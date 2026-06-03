# QueryEngine 系统深度技术文档

> 基于逐行代码分析的完整技术文档  
> **探索完成时间**: 2026 年 4 月 1 日  
> **核心文件**: QueryEngine.ts (1296 行), query.ts (1730 行), compact/, contextCollapse/

---

## 1. QueryEngine 系统概述

QueryEngine 系统是 Claude Code 的核心编排引擎，负责管理对话状态、API 查询循环、上下文管理和工具执行协调。

### 1.1 架构设计哲学

- **关注点分离**: `QueryEngine` 管理对话状态和 SDK 协议，`query()` 处理 API 交互循环
- **流式优先**: 所有响应通过 async generator 实时流式传输
- **特性门控模块化**: 高级功能使用运行时特性标志进行 tree-shaking
- **不可变配置，可变状态**: 构造函数配置不可变；消息数组和跟踪状态跨 turn 可变

### 1.2 组件层次

```
┌─────────────────────────────────────────────────────────┐
│                    Application Layer                     │
│  (ask() convenience wrapper / SDK entry points)          │
└─────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────┐
│                  QueryEngine Class                       │
│  - Conversation state management (messages, usage)       │
│  - SDK message normalization & yielding                  │
│  - Budget/turn limit enforcement                         │
│  - Transcript persistence                                │
└─────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────┐
│                    query() Generator                     │
│  - Query loop orchestration                              │
│  - Context management (snip/microcompact/autocompact)    │
│  - Tool execution coordination                           │
│  - Recovery mechanisms                                   │
└─────────────────────────────────────────────────────────┘
```

---

## 2. QueryEngine.ts 深度分析

### 2.1 类结构与状态管理

```typescript
export class QueryEngine {
  // 不可变配置
  private config: QueryEngineConfig
  
  // 核心对话状态（跨 turn 持久化）
  private mutableMessages: Message[]
  
  // 取消控制
  private abortController: AbortController
  
  // SDK 权限拒绝跟踪
  private permissionDenials: SDKPermissionDenial[]
  
  // 累积 token 使用量
  private totalUsage: NonNullableUsage
  
  // 文件读取缓存
  private readFileState: FileStateCache
  
  // Turn 作用域技能发现
  private discoveredSkillNames = new Set<string>()
  
  private hasHandledOrphanedPermission = false
  private loadedNestedMemoryPaths = new Set<string>()
}
```

**关键设计决策**:

1. **每个对话一个 QueryEngine 实例** (179-182 行): 状态在 `submitMessage()` 调用间持久化
2. **可变消息数组**: 原地修改以提升性能；仅在需要时克隆
3. **Turn 作用域技能发现**: 每个 `submitMessage()` 开始时清空，避免无限制增长

### 2.2 submitMessage() 完整生命周期

```typescript
async *submitMessage(
  prompt: string | ContentBlockParam[],
  options?: { uuid?: string; isMeta?: boolean },
): AsyncGenerator<SDKMessage, void, unknown>
```

#### 阶段 1: 初始化 (209-539 行)

1. **配置提取与重置** (213-238 行)
2. **权限包装器** (244-271 行)
3. **系统提示构建** (284-325 行)
4. **ProcessUserInputContext 设置** (335-395 行)
5. **孤立权限处理** (398-408 行)
6. **用户输入处理** (410-428 行)
7. **消息持久化** (430-463 行) - **关键**: 在查询循环之前写入 transcript

#### 阶段 2: 系统初始化消息 (540-554 行)

```typescript
yield buildSystemInitMessage({
  tools, mcpClients, model: mainLoopModel,
  permissionMode, commands, agents, skills, plugins, fastMode,
})
```

#### 阶段 3: 查询循环集成 (675-1049 行)

**消息处理 Switch** (757-969 行):

| 消息类型 | 处理方式 |
|---------|---------|
| `tombstone` | 跳过（消息移除控制信号）|
| `assistant` | 推入 mutableMessages，生成规范化消息 |
| `progress` | 推入并记录内联（去重要求）|
| `user` | 推入 mutableMessages，生成规范化消息 |
| `stream_event` | 跟踪使用量，从 message_delta 捕获 stop_reason |
| `attachment` | 处理 structured_output, max_turns_reached, queued_command |
| `system` | 处理 snip 回放，compact_boundary, api_retry |

#### 阶段 4: 终止条件 (971-1049 行)

1. **预算超出检查**
2. **结构化输出重试限制**
3. **最大 Turn 数检查**

#### 阶段 5: 结果生成 (1058-1156 行)

---

## 3. query.ts 深度分析

### 3.1 状态类型定义

```typescript
type State = {
  messages: Message[]
  toolUseContext: ToolUseContext
  autoCompactTracking: AutoCompactTrackingState | undefined
  maxOutputTokensRecoveryCount: number
  hasAttemptedReactiveCompact: boolean
  maxOutputTokensOverride: number | undefined
  pendingToolUseSummary: Promise<ToolUseSummaryMessage | null> | undefined
  stopHookActive: boolean | undefined
  turnCount: number
  transition: Continue | undefined
}
```

### 3.2 查询循环生命周期

```
┌──────────────────────────────────────────────────────────┐
│              查询循环迭代 (while true)                     │
│                                                           │
│  1. 状态解构                                              │
│  2. 开始预取 (内存，技能)                                 │
│  3. 上下文管理管道：                                      │
│     a. getMessagesAfterCompactBoundary()                 │
│     b. snipCompactIfNeeded()  ← 移除消息                  │
│     c. microcompact()         ← 压缩工具结果              │
│     d. applyCollapsesIfNeeded() ← 读取时投影              │
│     e. autoCompactIfNeeded()  ← 完整摘要紧凑              │
│  4. API 流式循环：                                         │
│     - deps.callModel() 流式调用                           │
│     - 扣留可恢复错误                                     │
│     - 跟踪 tool_use 块                                    │
│     - 流式工具执行（如果启用）                           │
│  5. 流式后恢复：                                          │
│     - Collapse drain (如果 prompt_too_long)              │
│     - Reactive compact (如果仍然太长)                    │
│     - Max output tokens 升级                              │
│     - Max output tokens 多 turn 恢复                       │
│  6. Stop Hooks:                                          │
│     - executeStopHooks()                                 │
│  7. 工具执行：                                            │
│     - streamingToolExecutor.getRemainingResults()        │
│     - 或 runTools()                                      │
│  8. Attachment 处理：                                      │
│     - Queued commands drain                              │
│     - Memory prefetch consume                            │
│  9. 检查 maxTurns                                         │
│  10. 更新状态并继续                                       │
└──────────────────────────────────────────────────────────┘
```

### 3.3 上下文管理管道

**上下文管理顺序**：

```
messages → Snip → Microcompact → Context Collapse → Autocompact → messagesForQuery
```

**为什么这个顺序至关重要**：

- **Snip 第一**: 完全移除消息，释放 token
- **Microcompact 第二**: 压缩工具结果（缓存编辑）
- **Collapse 第三**: 投影折叠视图而不修改 REPL 历史
- **Autocompact 最后**: 当其他方法不足时进行完整摘要紧凑

---

## 4. 错误处理与恢复

### 4.1 错误分类

| 错误类型 | 恢复策略 | 位置 |
|---------|---------|------|
| `prompt_too_long` | Collapse drain → Reactive compact | query.ts:1085-1183 |
| `max_output_tokens` | 升级到 64k → 多 turn 恢复 | query.ts:1188-1256 |
| `media_size_error` | Reactive compact strip-retry | query.ts:1119-1176 |
| `model_fallback` | 使用 fallback 模型重试 | query.ts:894-950 |
| `streaming_fallback` | Tombstone 孤儿，重试 | query.ts:712-741 |

### 4.2 Max Output Tokens 恢复

**两阶段恢复**：

**阶段 1: 升级** (1195-1221 行):
```typescript
if (capEnabled && maxOutputTokensOverride === undefined) {
  state = {
    messages: messagesForQuery,
    maxOutputTokensOverride: ESCALATED_MAX_TOKENS,  // 64k
    transition: { reason: 'max_output_tokens_escalate' },
  }
  continue
}
```

**阶段 2: 多 Turn 恢复** (1223-1252 行):
```typescript
if (maxOutputTokensRecoveryCount < MAX_OUTPUT_TOKENS_RECOVERY_LIMIT) {  // 3
  const recoveryMessage = createUserMessage({
    content: `Output token limit hit. Resume directly...`,
    isMeta: true,
  })
  state = {
    messages: [...messagesForQuery, ...assistantMessages, recoveryMessage],
    maxOutputTokensRecoveryCount: maxOutputTokensRecoveryCount + 1,
    transition: { reason: 'max_output_tokens_recovery' },
  }
  continue
}
```

---

## 5. Transcript 持久化策略

**关键洞察** (QueryEngine.ts 436-463 行):

> "在**进入查询循环之前**将用户消息持久化到 transcript。下面的 for-await 只在 ask() 生成 assistant/user/compact_boundary 消息时调用 recordTranscript——这要等到 API 响应后才会发生。如果进程在此前被杀死（例如用户在 cowork 中点击发送后几秒点击停止），transcript 将只包含队列操作条目；getLastSessionLog 过滤掉这些，返回 null，--resume 失败并显示 'No conversation found'。"

**实现**：

```typescript
if (persistSession && messagesFromUserInput.length > 0) {
  const transcriptPromise = recordTranscript(messages)
  if (isBareMode()) {
    void transcriptPromise  // 发后不管
  } else {
    await transcriptPromise  // 阻塞以保证可恢复性
    if (isEnvTruthy(process.env.CLAUDE_CODE_EAGER_FLUSH) || 
        isEnvTruthy(process.env.CLAUDE_CODE_IS_COWORK)) {
      await flushSessionStorage()
    }
  }
}
```

**内联记录** (用于 progress/attachment 消息):

```typescript
if (message.type === 'progress') {
  this.mutableMessages.push(message)
  if (persistSession) {
    messages.push(message)
    void recordTranscript(messages)  // 内联，防止去重问题
  }
  yield* normalizeMessage(message)
}
```

**为什么内联**: "延迟的 progress 会与已记录的 tool_results 在 mutableMessages 中交错，去重遍历将 startingParentUuid 冻结在错误的消息处——使链分叉并使会话在恢复时孤立。"

---

## 6. 性能优化

### 6.1 预取模式

**内存预取**：
```typescript
using pendingMemoryPrefetch = startRelevantMemoryPrefetch(
  state.messages, state.toolUseContext,
)
```

**技能预取**：
```typescript
const pendingSkillPrefetch = skillPrefetch?.startSkillDiscoveryPrefetch(
  null, messages, toolUseContext,
)
```

**稍后消费**：
```typescript
if (pendingMemoryPrefetch && pendingMemoryPrefetch.settledAt !== null) {
  const memoryAttachments = filterDuplicateMemoryAttachments(
    await pendingMemoryPrefetch.promise,
    toolUseContext.readFileState,
  )
  // ... 生成 attachments
  pendingMemoryPrefetch.consumedOnIteration = turnCount - 1
}
```

### 6.2 克隆 - 写入 SDK

**回填可观察输入**：保持原始消息不变以维护 prompt 缓存

---

## 7. 特性标志

### 7.1 三层门控

1. **Bun feature()** (编译时): Tree-shaking
2. **Statsig** (运行时): A/B 测试
3. **环境变量**: 调试和覆盖

### 7.2 关键特性标志

- `HISTORY_SNIP`: 激进消息移除
- `CACHED_MICROCOMPACT`: 缓存编辑 API
- `CONTEXT_COLLAPSE`: 读取时投影
- `REACTIVE_COMPACT`: 错误后恢复
- `TOKEN_BUDGET`: 每 turn token 限制

---

## 8. 总结

QueryEngine 系统是一个复杂的编排引擎，管理：

1. **对话状态**: 可变消息数组、文件缓存、使用量跟踪跨 turn
2. **上下文管理**: 四层管道（snip → microcompact → collapse → autocompact）带反应式恢复
3. **工具执行**: 流式和批量模式带权限跟踪
4. **错误恢复**: 多策略恢复 prompt-too-long、max-output-tokens、媒体错误
5. **Token 预算**: 每 turn 延续和 API 端任务预算跟踪
6. **流式**: 实时消息生成带适当的 transcript 持久化
7. **特性门控**: 运行时标志用于外部构建中的 tree-shaking

架构优先考虑：
- **可恢复性**: 查询循环前 transcript 写入，progress 消息内联记录
- **性能**: 预取模式、SDK 克隆 - 写入、单次闭包创建
- **恢复**: 扣留可恢复错误、多阶段重试机制
- **可观察性**: 分析器检查点、分析事件、调试日志

---

*文档持续更新中...*
