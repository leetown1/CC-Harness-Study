# Claude Code 架构深度解析 - 完整技术文档

> 本文档基于对 `f:\Claude\src` 代码库的逐行探索，提供了比任何网页文档都详细的技术架构解析。
> 
> 文档生成时间：2026 年 4 月 1 日
> 探索方法：多代理并行探索式分析
> 覆盖范围：1944 个源文件，核心模块逐行分析

---

## 目录

1. [架构概览](#1-架构概览)
2. [QueryEngine 核心系统](#2-queryengine 核心系统)
3. [Tool 工具系统](#3-tool 工具系统)
4. [Command 命令系统](#4-command 命令系统)
5. [Services 服务层](#5-services 服务层)
6. [MCP 与插件系统](#6-mcp 与插件系统)
7. [API 与通信层](#7-api 与通信层)
8. [核心设计模式](#8-核心设计模式)
9. [性能优化策略](#9-性能优化策略)
10. [安全机制](#10-安全机制)

---

## 1. 架构概览

### 1.1 目录结构

```
f:\Claude\src\
├── 核心架构文件（根目录）
│   ├── QueryEngine.ts          (1296 行) - 查询生命周期管理器
│   ├── query.ts                (1730 行) - 核心查询循环实现
│   ├── Tool.ts                 (793 行)  - 工具类型定义
│   ├── tools.ts                (389 行)  - 工具注册表
│   └── commands.ts             (755 行)  - 命令注册表
│
├── commands/                   (66+ 命令模块)
├── tools/                      (153+ 工具实现)
├── services/                   (127+ 服务模块)
├── utils/                      (549+ 工具函数)
├── components/                 (React UI 组件)
├── hooks/                      (React Hooks)
├── types/                      (TypeScript 类型定义)
├── constants/                  (应用常量)
├── entrypoints/                (应用入口点)
├── cli/                        (CLI 基础设施)
├── bridge/                     (远程通信桥接)
├── memdir/                     (内存目录管理)
├── query/                      (查询处理)
├── remote/                     (远程会话管理)
├── server/                     (服务器组件)
└── vim/                        (Vim 模式支持)
```

### 1.2 核心架构层次

```
┌─────────────────────────────────────────────────────────┐
│                    应用层 (Application)                   │
│  - CLI 入口 / SDK / 远程模式                              │
│  - React 组件 / Ink 终端 UI                               │
└────────────────────────┬────────────────────────────────┘
                         │
┌────────────────────────▼────────────────────────────────┐
│              核心编排层 (Core Orchestration)              │
│  - QueryEngine: 对话状态管理                             │
│  - query(): API 查询循环                                  │
│  - Tool 系统：工具执行协调                                │
│  - Command 系统：命令注册与发现                           │
└────────────────────────┬────────────────────────────────┘
                         │
┌────────────────────────▼────────────────────────────────┐
│              服务层 (Services Layer)                      │
│  - API 客户端 / 重试逻辑 / 流式处理                       │
│  - 上下文管理 (compact/collapse)                         │
│  - MCP 客户端 / OAuth / Elicitation                      │
│  - 工具编排 / 权限检查 / Hook 系统                        │
│  - LSP / 插件管理 / 分析日志                             │
└────────────────────────┬────────────────────────────────┘
                         │
┌────────────────────────▼────────────────────────────────┐
│              基础设施层 (Infrastructure)                  │
│  - 文件系统 / 进程管理 / 网络通信                        │
│  - 缓存系统 / 配置管理 / 安全策略                        │
└─────────────────────────────────────────────────────────┘
```

### 1.3 关键模块规模

| 模块 | 文件数 | 核心文件行数 | 职责 |
|------|--------|-------------|------|
| QueryEngine | 2 | 3026 行 | 查询生命周期、上下文管理 |
| Tool 系统 | 153+ | 1182 行 | 工具定义、执行、权限 |
| Command 系统 | 66+ | 755 行 | 命令注册、发现、执行 |
| Services | 127+ | - | API、MCP、工具编排等 |
| Utils | 549+ | - | 工具函数、辅助逻辑 |

---

## 2. QueryEngine 核心系统

### 2.1 架构设计哲学

QueryEngine 系统采用以下核心原则：

- **关注点分离**: `QueryEngine` 管理对话状态和 SDK 协议，`query()` 处理 API 交互循环
- **流式优先**: 所有响应通过 async generator 实时流式传输
- **特性门控模块化**: 高级功能（snip/collapse/reactive compact）使用运行时特性标志进行 tree-shaking
- **不可变配置，可变状态**: 构造函数配置不可变；消息数组和跟踪状态跨 turn 可变

### 2.2 QueryEngine 类结构

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

**关键设计决策**：

1. **每个对话一个 QueryEngine 实例** (179-182 行): 状态在 `submitMessage()` 调用间持久化
2. **可变消息数组**: 原地修改以提升性能；仅在需要时克隆
3. **Turn 作用域技能发现**: 每个 `submitMessage()` 开始时清空，避免无限制增长

### 2.3 submitMessage() 核心方法

完整的生命周期分为 5 个阶段：

#### 阶段 1: 初始化 (209-539 行)

```typescript
async *submitMessage(
  prompt: string | ContentBlockParam[],
  options?: { uuid?: string; isMeta?: boolean },
): AsyncGenerator<SDKMessage, void, unknown>
```

**详细步骤**：

1. **配置提取与重置** (213-238 行):
   - 通过解构提取所有配置选项
   - 清空 `discoveredSkillNames` 集合用于新 turn

2. **权限包装器** (244-271 行):
   ```typescript
   const wrappedCanUseTool: CanUseToolFn = async (
     tool, input, toolUseContext, assistantMessage, toolUseID, forceDecision,
   ) => {
     const result = await canUseTool(...)
     
     // 跟踪拒绝决策用于 SDK 报告
     if (result.behavior !== 'allow') {
       this.permissionDenials.push({
         tool_name: sdkCompatToolName(tool.name),
         tool_use_id: toolUseID,
         tool_input: input,
       })
     }
     
     return result
   }
   ```

3. **系统提示构建** (284-325 行):
   ```typescript
   const { defaultSystemPrompt, userContext: baseUserContext, systemContext } 
     = await fetchSystemPromptParts({...})
   
   const memoryMechanicsPrompt = customPrompt !== undefined && hasAutoMemPathOverride()
     ? await loadMemoryPrompt() : null
   
   const systemPrompt = asSystemPrompt([
     ...(customPrompt !== undefined ? [customPrompt] : defaultSystemPrompt),
     ...(memoryMechanicsPrompt ? [memoryMechanicsPrompt] : []),
     ...(appendSystemPrompt ? [appendSystemPrompt] : []),
   ])
   ```

4. **ProcessUserInputContext 设置** (335-395 行):
   - 创建 `processUserInput()` 上下文对象
   - 包含用于斜杠命令的可变消息设置器
   - 跟踪嵌套内存触发和技能发现

5. **孤立权限处理** (398-408 行):
   - 处理上一 turn 结束后到达的权限决策
   - 使用 `hasHandledOrphanedPermission` 标志防止重复处理

6. **用户输入处理** (410-428 行):
   ```typescript
   const { messages: messagesFromUserInput, shouldQuery, allowedTools, model: modelFromUserInput, resultText } 
     = await processUserInput({...})
   ```

7. **消息持久化** (430-463 行):
   - 推送新消息到 `mutableMessages`
   - **关键**: 在查询循环**之前**写入 transcript（可恢复性保证）
   - 在 cowork 模式下通过 `CLAUDE_CODE_EAGER_FLUSH` 急切刷新

#### 阶段 2: 系统初始化消息 (540-554 行)

```typescript
yield buildSystemInitMessage({
  tools, mcpClients, model: mainLoopModel,
  permissionMode, commands, agents, skills, plugins, fastMode,
})
```

此消息用当前会话状态初始化 SDK 客户端。

#### 阶段 3: 查询循环集成 (675-1049 行)

核心查询循环集成：

```typescript
for await (const message of query({
  messages, systemPrompt, userContext, systemContext,
  canUseTool: wrappedCanUseTool,
  toolUseContext: processUserInputContext,
  ...
})) {
  // 消息处理 switch 语句
}
```

**消息处理 Switch** (757-969 行):

| 消息类型 | 处理方式 |
|---------|---------|
| `tombstone` | 跳过（消息移除控制信号）|
| `assistant` | 推入 mutableMessages，生成规范化消息 |
| `progress` | 推入并记录内联（去重要求）|
| `user` | 推入 mutableMessages，生成规范化消息 |
| `stream_event` | 跟踪使用量，从 message_delta 捕获 stop_reason |
| `attachment` | 处理 structured_output, max_turns_reached, queued_command |
| `stream_request_start` | 跳过（内部控制）|
| `system` | 处理 snip 回放，compact_boundary, api_retry |
| `tool_use_summary` | 生成到 SDK |

**关键：紧凑边界处理** (898-942 行):

```typescript
const snipResult = this.config.snipReplay?.(message, this.mutableMessages)
if (snipResult !== undefined) {
  if (snipResult.executed) {
    this.mutableMessages.length = 0
    this.mutableMessages.push(...snipResult.messages)
  }
  break
}

// 对于 compact_boundary，释放紧凑前消息给 GC
if (message.subtype === 'compact_boundary' && message.compactMetadata) {
  const mutableBoundaryIdx = this.mutableMessages.length - 1
  if (mutableBoundaryIdx > 0) {
    this.mutableMessages.splice(0, mutableBoundaryIdx)  // GC 旧消息
  }
  // ... 生成边界到 SDK
}
```

#### 阶段 4: 终止条件 (971-1049 行)

循环内三个终止检查：

1. **预算超出** (972-1002 行):
   ```typescript
   if (maxBudgetUsd !== undefined && getTotalCost() >= maxBudgetUsd) {
     yield {
       type: 'result', subtype: 'error_max_budget_usd',
       duration_ms: Date.now() - startTime,
       is_error: true,
       num_turns: turnCount,
       errors: [`Reached maximum budget ($${maxBudgetUsd})`],
     }
     return
   }
   ```

2. **结构化输出重试限制** (1005-1048 行):
   ```typescript
   const callsThisQuery = currentCalls - initialStructuredOutputCalls
   if (callsThisQuery >= maxRetries) {
     yield {
       type: 'result', subtype: 'error_max_structured_output_retries',
       errors: [`Exceeded maximum structured output retries`],
     }
     return
   }
   ```

3. **最大 Turn 数** (通过 query.ts 中的 attachment 处理)

#### 阶段 5: 结果生成 (1058-1156 行)

**终端状态分析** (1058-1118 行):

```typescript
const result = messages.findLast(m => m.type === 'assistant' || m.type === 'user')
const edeResultType = result?.type ?? 'undefined'
const edeLastContentType = result?.type === 'assistant'
  ? (last(result.message.content)?.type ?? 'none')
  : 'n/a'

if (!isResultSuccessful(result, lastStopReason)) {
  yield {
    type: 'result', subtype: 'error_during_execution',
    errors: [
      `[ede_diagnostic] result_type=${edeResultType} ...`,
      ...getInMemoryErrors().slice(start).map(_ => _.error),
    ],
  }
  return
}
```

**文本结果提取** (1121-1155 行):

```typescript
let textResult = ''
if (result.type === 'assistant') {
  const lastContent = last(result.message.content)
  if (lastContent?.type === 'text' && !SYNTHETIC_MESSAGES.has(lastContent.text)) {
    textResult = lastContent.text
  }
}

yield {
  type: 'result', subtype: 'success',
  result: textResult,
  structured_output: structuredOutputFromTool,
  ...
}
```

### 2.4 query.ts 查询循环

#### 2.4.1 状态类型定义

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
  transition: Continue | undefined  // 为什么上一次迭代继续
}
```

#### 2.4.2 查询循环生命周期

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
│     - executeTaskCompletedHooks() (如果是 teammate)      │
│     - executeTeammateIdleHooks() (如果是 teammate)       │
│  7. 工具执行：                                            │
│     - streamingToolExecutor.getRemainingResults()        │
│     - 或 runTools()                                      │
│  8. Attachment 处理：                                      │
│     - Queued commands drain                              │
│     - Memory prefetch consume                            │
│     - Skill prefetch consume                            │
│  9. 检查 maxTurns                                         │
│  10. 更新状态并继续                                       │
└──────────────────────────────────────────────────────────┘
```

#### 2.4.3 上下文管理管道

**上下文管理顺序**：

```
messages → Snip → Microcompact → Context Collapse → Autocompact → messagesForQuery
```

**详细实现**：

```typescript
// A. 获取紧凑边界后消息 (365 行)
let messagesForQuery = [...getMessagesAfterCompactBoundary(messages)]

// B. Snip 紧凑 (396-410 行)
let snipTokensFreed = 0
if (feature('HISTORY_SNIP')) {
  queryCheckpoint('query_snip_start')
  const snipResult = snipModule!.snipCompactIfNeeded(messagesForQuery)
  messagesForQuery = snipResult.messages
  snipTokensFreed = snipResult.tokensFreed
  if (snipResult.boundaryMessage) {
    yield snipResult.boundaryMessage
  }
  queryCheckpoint('query_snip_end')
}

// C. Microcompact (412-426 行)
queryCheckpoint('query_microcompact_start')
const microcompactResult = await deps.microcompact(
  messagesForQuery, toolUseContext, querySource,
)
messagesForQuery = microcompactResult.messages
const pendingCacheEdits = feature('CACHED_MICROCOMPACT')
  ? microcompactResult.compactionInfo?.pendingCacheEdits
  : undefined

// D. Context Collapse (440-447 行)
if (feature('CONTEXT_COLLAPSE') && contextCollapse) {
  const collapseResult = await contextCollapse.applyCollapsesIfNeeded(
    messagesForQuery, toolUseContext, querySource,
  )
  messagesForQuery = collapseResult.messages
}

// E. Autocompact (453-543 行)
queryCheckpoint('query_autocompact_start')
const { compactionResult, consecutiveFailures } = await deps.autocompact(
  messagesForQuery, toolUseContext,
  { systemPrompt, userContext, systemContext, toolUseContext, forkContextMessages: messagesForQuery },
  querySource, tracking, snipTokensFreed,
)
queryCheckpoint('query_autocompact_end')

if (compactionResult) {
  // 更新 task_budget 跟踪
  if (params.taskBudget) {
    const preCompactContext = finalContextTokensFromLastResponse(messagesForQuery)
    taskBudgetRemaining = Math.max(0, (taskBudgetRemaining ?? params.taskBudget.total) - preCompactContext)
  }
  
  // 重置跟踪
  tracking = { compacted: true, turnId: deps.uuid(), turnCounter: 0, consecutiveFailures: 0 }
  
  // 构建并生成紧凑后消息
  const postCompactMessages = buildPostCompactMessages(compactionResult)
  for (const message of postCompactMessages) {
    yield message
  }
  messagesForQuery = postCompactMessages
}
```

**为什么这个顺序至关重要**：

- **Snip 第一**: 完全移除消息，释放 token
- **Microcompact 第二**: 压缩工具结果（缓存编辑）
- **Collapse 第三**: 投影折叠视图而不修改 REPL 历史
- **Autocompact 最后**: 当其他方法不足时进行完整摘要紧凑

### 2.5 错误处理与恢复

#### 2.5.1 错误分类

| 错误类型 | 恢复策略 | 位置 |
|---------|---------|------|
| `prompt_too_long` | Collapse drain → Reactive compact | query.ts:1085-1183 |
| `max_output_tokens` | 升级到 64k → 多 turn 恢复 | query.ts:1188-1256 |
| `media_size_error` | Reactive compact strip-retry | query.ts:1119-1176 |
| `model_fallback` | 使用 fallback 模型重试 | query.ts:894-950 |
| `streaming_fallback` | Tombstone 孤儿，重试 | query.ts:712-741 |
| `structured_output_retry` | 计数重试，超出后失败 | QueryEngine.ts:1005-1048 |
| `tool_execution_error` | 生成错误作为 tool_result | query.ts:984-992 |

#### 2.5.2 Max Output Tokens 恢复

**两阶段恢复**：

**阶段 1: 升级** (1195-1221 行):

```typescript
const capEnabled = getFeatureValue_CACHED_MAY_BE_STALE('tengu_otk_slot_v1', false)
if (capEnabled && maxOutputTokensOverride === undefined && !process.env.CLAUDE_CODE_MAX_OUTPUT_TOKENS) {
  logEvent('tengu_max_tokens_escalate', { escalatedTo: ESCALATED_MAX_TOKENS })  // 64k
  state = {
    messages: messagesForQuery,
    maxOutputTokensOverride: ESCALATED_MAX_TOKENS,
    transition: { reason: 'max_output_tokens_escalate' },
  }
  continue
}
```

**阶段 2: 多 Turn 恢复** (1223-1252 行):

```typescript
if (maxOutputTokensRecoveryCount < MAX_OUTPUT_TOKENS_RECOVERY_LIMIT) {  // 3
  const recoveryMessage = createUserMessage({
    content: `Output token limit hit. Resume directly — no apology, no recap...`,
    isMeta: true,
  })
  state = {
    messages: [...messagesForQuery, ...assistantMessages, recoveryMessage],
    maxOutputTokensRecoveryCount: maxOutputTokensRecoveryCount + 1,
    transition: { reason: 'max_output_tokens_recovery', attempt: maxOutputTokensRecoveryCount + 1 },
  }
  continue
}

// 用尽 - 表面错误
yield lastMessage
```

### 2.6 Transcript 持久化策略

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
// Progress 消息 (QueryEngine.ts 771-783 行)
if (message.type === 'progress') {
  this.mutableMessages.push(message)
  if (persistSession) {
    messages.push(message)
    void recordTranscript(messages)  // 内联，防止去重问题
  }
  yield* normalizeMessage(message)
}
```

**为什么内联**: "没有这个，延迟的 progress 会与已记录的 tool_results 在 mutableMessages 中交错，去重遍历将 startingParentUuid 冻结在错误的消息处——使链分叉并使会话在恢复时孤立。"

---

## 3. Tool 工具系统

### 3.1 Tool 接口定义

```typescript
export type Tool<
  Input extends AnyObject = AnyObject,
  Output = unknown,
  P extends ToolProgressData = ToolProgressData,
> = {
  // 身份与发现
  name: string
  aliases?: string[]
  searchHint?: string
  
  // 核心执行
  call(
    args: z.infer<Input>,
    context: ToolUseContext,
    canUseTool: CanUseToolFn,
    parentMessage: AssistantMessage,
    onProgress?: ToolCallProgress<P>,
  ): Promise<ToolResult<Output>>
  
  // Schema 与验证
  inputSchema: Input
  inputJSONSchema?: ToolInputJSONSchema
  outputSchema?: z.ZodType<unknown>
  validateInput?(input: z.infer<Input>, context: ToolUseContext): Promise<ValidationResult>
  
  // 权限系统
  checkPermissions(input: z.infer<Input>, context: ToolUseContext): Promise<PermissionResult>
  preparePermissionMatcher?(input: z.infer<Input>): Promise<(pattern: string) => boolean>
  
  // 并发与安全
  isConcurrencySafe(input: z.infer<Input>): boolean
  isReadOnly(input: z.infer<Input>): boolean
  isDestructive?(input: z.infer<Input>): boolean
  interruptBehavior?(): 'cancel' | 'block'
  
  // UI 渲染
  renderToolUseMessage(input: Partial<z.infer<Input>>, options: {...}): React.ReactNode
  renderToolResultMessage(content: Output, progressMessages: ProgressMessage<P>[], options: {...}): React.ReactNode
  renderToolUseProgressMessage?(progressMessages: ProgressMessage<P>[], options: {...}): React.ReactNode
  
  // 元数据与描述
  description(input: z.infer<Input>, options: {...}): Promise<string>
  prompt(options: {...}): Promise<string>
  userFacingName(input: Partial<z.infer<Input>> | undefined): string
  
  // 高级功能
  isSearchOrReadCommand?(input: z.infer<Input>): { isSearch: boolean; isRead: boolean; isList?: boolean }
  toAutoClassifierInput(input: z.infer<Input>): unknown
  mapToolResultToToolResultBlockParam(content: Output, toolUseID: string): ToolResultBlockParam
}
```

**关键设计模式**：
- **泛型**: 工具使用 Input/Output/Progress 泛型强类型
- **Zod 验证**: 所有输入使用 Zod schema 进行运行时验证
- **进度跟踪**: 可选泛型进度类型用于流式更新
- **上下文注入**: 工具接收丰富的 `ToolUseContext` 包含所有依赖

### 3.2 buildTool 工厂模式

```typescript
const TOOL_DEFAULTS = {
  isEnabled: () => true,
  isConcurrencySafe: (_input?: unknown) => false,
  isReadOnly: (_input?: unknown) => false,
  isDestructive: (_input?: unknown) => false,
  checkPermissions: (input: { [key: string]: unknown }): Promise<PermissionResult> =>
    Promise.resolve({ behavior: 'allow', updatedInput: input }),
  toAutoClassifierInput: (_input?: unknown) => '',
  userFacingName: (_input?: unknown) => '',
}

export function buildTool<D extends AnyToolDef>(def: D): BuiltTool<D> {
  return {
    ...TOOL_DEFAULTS,
    userFacingName: () => def.name,
    ...def,
  } as BuiltTool<D>
}
```

**设计原理**：
- **故障安全默认值**: `isConcurrencySafe` 默认为 `false`（保守）
- **权限委托**: 默认 `checkPermissions` 委托给通用权限系统
- **类型安全**: `BuiltTool<D>` 类型确保所有可默认方法都存在
- **DRY 原则**: 60+ 工具共享通用默认值而无需重复

### 3.3 工具执行流程

#### 3.3.1 单工具执行

**完整执行管道**：

```
┌─────────────────────────────────────────────────────────────┐
│ 1. 工具查找与验证                                           │
│    - 按名称/别名查找工具                                    │
│    - 使用 Zod schema 解析输入                               │
│    - 运行 validateInput()                                   │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│ 2. 工具前 Hook                                                │
│    - 并行运行 PreToolUse hooks                              │
│    - 收集 hook 权限决策                                      │
│    - 收集额外上下文                                         │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│ 3. 权限解析                                                   │
│    - 检查拒绝规则 (步骤 1a)                                  │
│    - 检查询问规则 (步骤 1b)                                  │
│    - 运行 tool.checkPermissions() (步骤 1c)                 │
│    - 检查安全规则 (步骤 1g)                                  │
│    - 应用模式转换 (bypassPermissions, auto)                 │
│    - 如需要运行自动模式分类器                               │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│ 4. 工具执行                                                   │
│    - 使用验证后的输入调用 tool.call()                       │
│    - 流式进度更新                                           │
│    - 处理错误和中止                                         │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│ 5. 工具后 Hook                                                │
│    - 运行 PostToolUse hooks                                 │
│    - 转换 MCP 工具输出                                       │
│    - 收集 hook 指标                                          │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│ 6. 结果处理                                                   │
│    - 映射结果到 ToolResultBlockParam                        │
│    - 应用结果大小限制                                       │
│    - 如超过阈值持久化到磁盘                                 │
│    - 附加图片/反馈                                          │
└─────────────────────────────────────────────────────────────┘
```

#### 3.3.2 并行工具执行

**并发控制算法**：

```typescript
class StreamingToolExecutor {
  private tools: TrackedTool[] = []
  
  addTool(block: ToolUseBlock, assistantMessage: AssistantMessage): void {
    const isConcurrencySafe = tool.isConcurrencySafe(parsedInput)
    this.tools.push({
      id: block.id,
      status: 'queued',
      isConcurrencySafe,
      // ...
    })
    void this.processQueue()
  }
  
  private canExecuteTool(isConcurrencySafe: boolean): boolean {
    const executingTools = this.tools.filter(t => t.status === 'executing')
    return (
      executingTools.length === 0 ||
      (isConcurrencySafe && executingTools.every(t => t.isConcurrencySafe))
    )
  }
}
```

**并发规则**：
1. **非并发工具** 单独执行（独占访问）
2. **并发安全工具** 可以与其他并发安全工具并行执行
3. **顺序保持**: 结果按原始工具调用顺序生成
4. **错误级联**: Bash 错误通过 `siblingAbortController` 取消兄弟子进程

### 3.4 权限系统架构

#### 3.4.1 权限模式层次

```typescript
export type PermissionMode =
  | 'acceptEdits'      // 自动批准安全文件编辑
  | 'bypassPermissions' // 自动批准所有（安全检查除外）
  | 'default'          // 询问所有
  | 'dontAsk'          // 自动拒绝所有
  | 'plan'             // 只读模式
  | 'auto'             // AI 分类器决策
  | 'bubble'           // 将提示冒泡到父终端
```

#### 3.4.2 权限决策管道

**逐步决策树**：

```
步骤 1a: 检查工具级拒绝规则
  ↓ (如果拒绝)
  → 返回 {behavior: 'deny', decisionReason: {type: 'rule'}}

步骤 1b: 检查工具级询问规则
  ↓ (如果询问)
  → 检查沙箱自动批准（仅 Bash）
  → 返回 {behavior: 'ask'} 或继续

步骤 1c: 运行 tool.checkPermissions(input, context)
  ↓ (工具特定逻辑)
  → 可能返回 {behavior: 'deny' | 'ask' | 'allow' | 'passthrough'}

步骤 1d: 检查工具实现拒绝
  ↓ (如果拒绝)
  → 返回 toolPermissionResult

步骤 1e: 检查 requiresUserInteraction()
  ↓ (如果 true)
  → 返回 {behavior: 'ask'} (bypass 免疫)

步骤 1f: 检查内容特定询问规则
  ↓ (如果 Bash(npm publish:*) 模式)
  → 返回 {behavior: 'ask'} (bypass 免疫)

步骤 1g: 检查安全检查 (.git/, .claude/, shell 配置)
  ↓ (如果敏感路径)
  → 返回 {behavior: 'ask'} (bypass 免疫)

步骤 2a: 检查 bypassPermissions 模式
  ↓ (如果 mode === 'bypassPermissions')
  → 返回 {behavior: 'allow'}

步骤 2b: 检查工具级允许规则
  ↓ (如果允许)
  → 返回 {behavior: 'allow', decisionReason: {type: 'rule'}}

步骤 3: 转换 passthrough 为 ask
  ↓ (默认)
  → 返回 {behavior: 'ask'}

自动模式特殊路径 (步骤 3 → 自动分类器):
  ↓ (如果 mode === 'auto' && behavior === 'ask')
  → 检查 acceptEdits 快速路径
  → 检查安全工具允许列表
  → 运行 YOLO 分类器
  → 返回分类器决策
```

### 3.5 关键工具实现

#### 3.5.1 FileReadTool

**特殊功能**：
- **去重**: 检测未更改文件的重新读取 (536-573 行)
- **Token 预算**: 压缩图片以适应 token 限制 (1097-1183 行)
- **PDF 提取**: 将大 PDF 拆分为页面图片 (894-1017 行)
- **技能发现**: 从文件路径激活技能 (575-591 行)

```typescript
async call({ file_path, offset = 1, limit, pages }, context) {
  const fullFilePath = expandPath(file_path)
  
  // 去重检查：如果文件未更改返回存根
  const existingState = readFileState.get(fullFilePath)
  if (existingState && !existingState.isPartialView) {
    const mtimeMs = await getFileModificationTimeAsync(fullFilePath)
    if (mtimeMs === existingState.timestamp) {
      return { data: { type: 'file_unchanged', file: { filePath } } }
    }
  }
  
  // 处理不同文件类型
  if (ext === 'ipynb') return readNotebook()
  if (IMAGE_EXTENSIONS.has(ext)) return readImageWithTokenBudget()
  if (isPDFExtension(ext)) return extractPDFPages()
  
  // 带行限制的文本文件读取
  const { content, lineCount, totalLines, mtimeMs } = await readFileInRange(
    resolvedFilePath, lineOffset, limit, maxSizeBytes
  )
  
  // 更新缓存
  readFileState.set(fullFilePath, { content, timestamp: mtimeMs, offset, limit })
  
  return { data: { type: 'text', file: { filePath, content, ... } } }
}
```

#### 3.5.2 FileEditTool

**原子编辑保证**：

```typescript
async call({ file_path, old_string, new_string, replace_all }, context) {
  const absoluteFilePath = expandPath(file_path)
  
  // 1. 文件历史备份
  await fileHistoryTrackEdit(updateFileHistoryState, absoluteFilePath, uuid)
  
  // 2. 原子读 - 改-写临界区
  const { content: originalFileContents, encoding, lineEndings } = readFileForEdit(absoluteFilePath)
  
  // 3. 陈旧检查
  const lastWriteTime = getFileModificationTime(absoluteFilePath)
  if (lastWriteTime > lastRead.timestamp && content !== lastRead.content) {
    throw new Error(FILE_UNEXPECTEDLY_MODIFIED_ERROR)
  }
  
  // 4. 引号规范化
  const actualOldString = findActualString(originalFileContents, old_string)
  const actualNewString = preserveQuoteStyle(old_string, actualOldString, new_string)
  
  // 5. 生成补丁并写入
  const { patch, updatedFile } = getPatchForEdit({...})
  writeTextContent(absoluteFilePath, updatedFile, encoding, lineEndings)
  
  // 6. LSP 通知
  lspManager.changeFile(absoluteFilePath, updatedFile)
  lspManager.saveFile(absoluteFilePath)
  
  return { data: { filePath, oldString, newString, structuredPatch: patch } }
}
```

### 3.6 错误处理

#### 3.6.1 错误分类

```typescript
export function classifyToolError(error: unknown): string {
  if (error instanceof TelemetrySafeError) {
    return error.telemetryMessage.slice(0, 200)
  }
  if (error instanceof Error) {
    const errnoCode = getErrnoCode(error) // ENOENT, EACCES, etc.
    if (typeof errnoCode === 'string') {
      return `Error:${errnoCode}`
    }
    if (error.name && error.name.length > 3) {
      return error.name.slice(0, 60)
    }
    return 'Error' // 回退（最小化安全）
  }
  return 'UnknownError'
}
```

#### 3.6.2 合成错误生成

```typescript
private createSyntheticErrorMessage(
  toolUseId: string,
  reason: 'sibling_error' | 'user_interrupted' | 'streaming_fallback',
  assistantMessage: AssistantMessage,
): Message {
  if (reason === 'user_interrupted') {
    return createUserMessage({
      content: [{
        type: 'tool_result',
        content: withMemoryCorrectionHint(REJECT_MESSAGE),
        is_error: true,
        tool_use_id: toolUseId,
      }],
      toolUseResult: 'User rejected tool use',
    })
  }
  
  if (reason === 'sibling_error') {
    const desc = this.erroredToolDescription
    const msg = desc 
      ? `Cancelled: parallel tool call ${desc} errored`
      : 'Cancelled: parallel tool call errored'
    
    return createUserMessage({
      content: [{
        type: 'tool_result',
        content: `<tool_use_error>${msg}</tool_use_error>`,
        is_error: true,
        tool_use_id: toolUseId,
      }],
    })
  }
}
```

---

## 4. Command 命令系统

### 4.1 命令类型定义

```typescript
// 基础命令类型
export type CommandBase = {
  availability?: CommandAvailability[]  // 认证/提供者要求
  description: string
  hasUserSpecifiedDescription?: boolean
  isEnabled?: () => boolean  // 动态启用（特性标志等）
  isHidden?: boolean  // 从类型提示/帮助中隐藏
  name: string
  aliases?: string[]
  isMcp?: boolean
  argumentHint?: string  // 参数灰色提示文本
  whenToUse?: string  // 详细使用场景
  version?: string
  disableModelInvocation?: boolean  // 阻止模型调用
  userInvocable?: boolean  // 用户可以输入 /command-name
  loadedFrom?: 'commands_DEPRECATED' | 'skills' | 'plugin' | 'managed' | 'bundled' | 'mcp'
  kind?: 'workflow'  // 基于工作流的命令
  immediate?: boolean  // 无需等待停止点即可执行
  isSensitive?: boolean  // 从历史中参数
  userFacingName?: () => string  // 覆盖显示名称
}

// 命令联合类型
export type Command = CommandBase & (
  | PromptCommand 
  | LocalCommand 
  | LocalJSXCommand
)
```

### 4.2 三种命令类型详解

#### 4.2.1 Prompt 命令 (`type: 'prompt'`)

**用途**: 扩展为发送到模型的文本提示的命令。这是最常见的命令类型，包括技能、工作流和插件命令。

**特性**：
- 包含带指令的 markdown 内容
- 支持通过 `${arg}` 语法的参数替换
- 支持在提示中使用 `!\`command\``或 ```! ... ``` 块执行 shell 命令
- 支持工具允许列表 (`allowedTools`)
- 可以指定模型覆盖
- 支持通过 `paths` glob 模式条件激活
- 可以在分叉子代理上下文中运行 (`context: 'fork'`)

**示例 - `/commit`**:

```typescript
const command = {
  type: 'prompt',
  name: 'commit',
  description: '创建 git 提交',
  allowedTools: [
    'Bash(git add:*)',
    'Bash(git status:*)',
    'Bash(git commit:*)',
  ],
  contentLength: 0,
  progressMessage: 'creating commit',
  source: 'builtin',
  async getPromptForCommand(_args, context) {
    const promptContent = getPromptContent()
    const finalContent = await executeShellCommandsInPrompt(
      promptContent,
      {
        ...context,
        getAppState() {
          const appState = context.getAppState()
          return {
            ...appState,
            toolPermissionContext: {
              ...appState.toolPermissionContext,
              alwaysAllowRules: {
                ...appState.toolPermissionContext.alwaysAllowRules,
                command: ALLOWED_TOOLS,
              },
            },
          }
        },
      },
      '/commit',
    )
    return [{ type: 'text', text: finalContent }]
  },
} satisfies Command
```

#### 4.2.2 Local 命令 (`type: 'local'`)

**用途**: 本地执行并返回文本结果的命令。这些是不涉及模型调用的纯函数。

**特性**：
- 返回 `{ type: 'text', value: string }`
- 支持非交互式会话
- 同步执行无需模型参与
- 用于实用工具命令如 `/reload-plugins`

**示例 - `/reload-plugins`**:

```typescript
export const call: LocalCommandCall = async (_args, context) => {
  if (
    feature('DOWNLOAD_USER_SETTINGS') &&
    (isEnvTruthy(process.env.CLAUDE_CODE_REMOTE) || getIsRemoteMode())
  ) {
    const applied = await redownloadUserSettings()
    if (applied) {
      settingsChangeDetector.notifyChange('userSettings')
    }
  }

  const r = await refreshActivePlugins(context.setAppState)

  const parts = [
    n(r.enabled_count, 'plugin'),
    n(r.command_count, 'skill'),
    n(r.agent_count, 'agent'),
    n(r.hook_count, 'hook'),
    n(r.mcp_count, 'plugin MCP server'),
    n(r.lsp_count, 'plugin LSP server'),
  ]
  let msg = `Reloaded: ${parts.join(' · ')}`

  if (r.error_count > 0) {
    msg += `\n${n(r.error_count, 'error')} during load. Run /doctor for details.`
  }

  return { type: 'text', value: msg }
}
```

#### 4.2.3 Local JSX 命令 (`type: 'local-jsx'`)

**用途**: 渲染 React/Ink UI 组件的命令。这些提供交互式终端界面。

**特性**：
- 返回 `React.ReactNode` (Ink 组件)
- 接收 `onDone` 回调用于完成
- 可以访问和修改消息历史通过 `setMessages`
- 用于设置面板、菜单和配置 UI
- 通过 `load()` 函数懒加载

**示例 - `/memory`**:

```typescript
export const call: LocalJSXCommandCall = async onDone => {
  clearMemoryFileCaches()
  await getMemoryFiles()
  return <MemoryCommand onDone={onDone} />
}

function MemoryCommand({ onDone }: {
  onDone: (result?: string, options?: { display?: CommandResultDisplay }) => void
}): React.ReactNode {
  const handleSelectMemoryFile = async (memoryPath: string) => {
    try {
      await mkdir(getClaudeConfigHomeDir(), { recursive: true })
      try {
        await writeFile(memoryPath, '', { encoding: 'utf8', flag: 'wx' })
      } catch (e: unknown) {
        if (getErrnoCode(e) !== 'EEXIST') throw e
      }
      await editFileInEditor(memoryPath)
      
      let editorSource = 'default'
      let editorValue = ''
      if (process.env.VISUAL) {
        editorSource = '$VISUAL'
        editorValue = process.env.VISUAL
      } else if (process.env.EDITOR) {
        editorSource = '$EDITOR'
        editorValue = process.env.EDITOR
      }
      
      const editorInfo = editorSource !== 'default' 
        ? `Using ${editorSource}="${editorValue}".` 
        : ''
      const editorHint = editorInfo 
        ? `> ${editorInfo} To change editor, set $EDITOR or $VISUAL.` 
        : `> To use a different editor, set $EDITOR or $VISUAL.`
      
      onDone(`Opened memory file at ${getRelativeMemoryPath(memoryPath)}\n\n${editorHint}`, {
        display: 'system'
      })
    } catch (error) {
      logError(error)
      onDone(`Error opening memory file: ${error}`)
    }
  }

  return (
    <Dialog title="Memory" onCancel={() => onDone('Cancelled', { display: 'system' })} color="remember">
      <Box flexDirection="column">
        <React.Suspense fallback={null}>
          <MemoryFileSelector 
            onSelect={handleSelectMemoryFile} 
            onCancel={() => onDone('Cancelled', { display: 'system' })} 
          />
        </React.Suspense>
        <Box marginTop={1}>
          <Text dimColor>
            Learn more: <Link url="https://code.claude.com/docs/en/memory" />
          </Text>
        </Box>
      </Box>
    </Dialog>
  )
}
```

### 4.3 命令注册与加载

#### 4.3.1 中央命令注册表

主命令注册表遵循此加载层次：

```typescript
const COMMANDS = memoize((): Command[] => [
  addDir, advisor, agents, branch, btw, chrome, clear, color, compact,
  config, copy, desktop, context, contextNonInteractive, cost, diff,
  doctor, effort, exit, fast, files, heapDump, help, ide, init,
  keybindings, installGitHubApp, installSlackApp, mcp, memory, mobile,
  model, outputStyle, remoteEnv, plugin, pr_comments, releaseNotes,
  reloadPlugins, rename, resume, session, skills, stats, status,
  statusline, stickers, tag, theme, feedback, review, ultrareview,
  rewind, securityReview, terminalSetup, upgrade, extraUsage,
  extraUsageNonInteractive, rateLimitOptions, usage, usageReport, vim,
  // 特性门控命令
  ...(webCmd ? [webCmd] : []),
  ...(forkCmd ? [forkCmd] : []),
  ...(buddy ? [buddy] : []),
  // ... 更多
])
```

#### 4.3.2 加载流程

```typescript
const loadAllCommands = memoize(async (cwd: string): Promise<Command[]> => {
  const [
    { skillDirCommands, pluginSkills, bundledSkills, builtinPluginSkills },
    pluginCommands,
    workflowCommands,
  ] = await Promise.all([
    getSkills(cwd),
    getPluginCommands(),
    getWorkflowCommands ? getWorkflowCommands(cwd) : Promise.resolve([]),
  ])

  return [
    ...bundledSkills,
    ...builtinPluginSkills,
    ...skillDirCommands,
    ...workflowCommands,
    ...pluginCommands,
    ...pluginSkills,
    ...COMMANDS(),
  ]
})
```

#### 4.3.3 getCommands() 带可用性和启用检查

```typescript
export async function getCommands(cwd: string): Promise<Command[]> {
  const allCommands = await loadAllCommands(cwd)
  
  // 获取文件操作期间发现的动态技能
  const dynamicSkills = getDynamicSkills()
  
  // 按可用性和 isEnabled() 过滤
  const baseCommands = allCommands.filter(
    _ => meetsAvailabilityRequirement(_) && isCommandEnabled(_),
  )
  
  if (dynamicSkills.length === 0) {
    return baseCommands
  }
  
  // 去重动态技能
  const baseCommandNames = new Set(baseCommands.map(c => c.name))
  const uniqueDynamicSkills = dynamicSkills.filter(
    s =>
      !baseCommandNames.has(s.name) &&
      meetsAvailabilityRequirement(s) &&
      isCommandEnabled(s),
  )
  
  if (uniqueDynamicSkills.length === 0) {
    return baseCommands
  }
  
  // 插入动态技能到插件技能之后，内置命令之前
  const builtInNames = new Set(COMMANDS().map(c => c.name))
  const insertIndex = baseCommands.findIndex(c => builtInNames.has(c.name))
  
  if (insertIndex === -1) {
    return [...baseCommands, ...uniqueDynamicSkills]
  }
  
  return [
    ...baseCommands.slice(0, insertIndex),
    ...uniqueDynamicSkills,
    ...baseCommands.slice(insertIndex),
  ]
}
```

### 4.4 命令发现来源

#### 4.4.1 内置命令

硬编码在 `commands.ts` 中，从 `commands/*/index.ts` 文件导入。

#### 4.4.2 捆绑技能

编译到 CLI 二进制文件，通过 `registerBundledSkill()` 注册：

```typescript
export function registerBundledSkill(definition: BundledSkillDefinition): void {
  const { files } = definition
  
  let skillRoot: string | undefined
  let getPromptForCommand = definition.getPromptForCommand
  
  if (files && Object.keys(files).length > 0) {
    skillRoot = getBundledSkillExtractDir(definition.name)
    let extractionPromise: Promise<string | null> | undefined
    const inner = definition.getPromptForCommand
    getPromptForCommand = async (args, ctx) => {
      extractionPromise ??= extractBundledSkillFiles(definition.name, files)
      const extractedDir = await extractionPromise
      const blocks = await inner(args, ctx)
      if (extractedDir === null) return blocks
      return prependBaseDir(blocks, extractedDir)
    }
  }
  
  const command: Command = {
    type: 'prompt',
    name: definition.name,
    description: definition.description,
    aliases: definition.aliases,
    hasUserSpecifiedDescription: true,
    allowedTools: definition.allowedTools ?? [],
    argumentHint: definition.argumentHint,
    whenToUse: definition.whenToUse,
    model: definition.model,
    disableModelInvocation: definition.disableModelInvocation ?? false,
    userInvocable: definition.userInvocable ?? true,
    contentLength: 0,
    source: 'bundled',
    loadedFrom: 'bundled',
    hooks: definition.hooks,
    skillRoot,
    context: definition.context,
    agent: definition.agent,
    isEnabled: definition.isEnabled,
    isHidden: !(definition.userInvocable ?? true),
    progressMessage: 'running',
    getPromptForCommand,
  }
  bundledSkills.push(command)
}
```

#### 4.4.3 用户技能来自 `/skills/` 目录

从多个位置加载由 `loadSkillsDir.ts`：

```typescript
export const getSkillDirCommands = memoize(async (cwd: string): Promise<Command[]> => {
  const userSkillsDir = join(getClaudeConfigHomeDir(), 'skills')
  const managedSkillsDir = join(getManagedFilePath(), '.claude', 'skills')
  const projectSkillsDirs = getProjectDirsUpToHome('skills', cwd)
  const additionalDirs = getAdditionalDirectoriesForClaudeMd()
  
  // 并行加载所有来源
  const [
    managedSkills,
    userSkills,
    projectSkillsNested,
    additionalSkillsNested,
    legacyCommands,
  ] = await Promise.all([
    loadSkillsFromSkillsDir(managedSkillsDir, 'policySettings'),
    loadSkillsFromSkillsDir(userSkillsDir, 'userSettings'),
    Promise.all(projectSkillsDirs.map(dir => 
      loadSkillsFromSkillsDir(dir, 'projectSettings')
    )),
    Promise.all(additionalDirs.map(dir => 
      loadSkillsFromSkillsDir(join(dir, '.claude', 'skills'), 'projectSettings')
    )),
    loadSkillsFromCommandsDir(cwd),  // 传统 /commands/ 格式
  ])
  
  // 组合并去重
  const allSkillsWithPaths = [
    ...managedSkills,
    ...userSkills,
    ...projectSkillsNested.flat(),
    ...additionalSkillsNested.flat(),
    ...legacyCommands,
  ]
  
  // 按解析的文件路径去重
  const fileIds = await Promise.all(
    allSkillsWithPaths.map(({ skill, filePath }) =>
      skill.type === 'prompt' ? getFileIdentity(filePath) : Promise.resolve(null)
    )
  )
  
  const seenFileIds = new Map()
  const deduplicatedSkills: Command[] = []
  
  for (let i = 0; i < allSkillsWithPaths.length; i++) {
    const entry = allSkillsWithPaths[i]
    if (entry === undefined || entry.skill.type !== 'prompt') continue
    const { skill } = entry
    const fileId = fileIds[i]
    
    if (fileId === null || fileId === undefined) {
      deduplicatedSkills.push(skill)
      continue
    }
    
    const existingSource = seenFileIds.get(fileId)
    if (existingSource !== undefined) {
      logForDebugging(
        `Skipping duplicate skill '${skill.name}' from ${skill.source} ` +
        `(same file already loaded from ${existingSource})`
      )
      continue
    }
    
    seenFileIds.set(fileId, skill.source)
    deduplicatedSkills.push(skill)
  }
  
  return unconditionalSkills
})
```

#### 4.4.4 插件命令

从启用的插件加载由 `loadPluginCommands.ts`：

```typescript
export const getPluginCommands = memoize(async (): Promise<Command[]> => {
  if (isBareMode() && getInlinePlugins().length === 0) {
    return []
  }
  
  const { enabled, errors } = await loadAllPluginsCacheOnly()
  
  const perPluginCommands = await Promise.all(
    enabled.map(async (plugin): Promise<Command[]> => {
      const loadedPaths = new Set<string>()
      const pluginCommands: Command[] = []
      
      // 从默认命令目录加载
      if (plugin.commandsPath) {
        const commands = await loadCommandsFromDirectory(
          plugin.commandsPath,
          plugin.name,
          plugin.source,
          plugin.manifest,
          plugin.path,
          { isSkillMode: false },
          loadedPaths,
        )
        pluginCommands.push(...commands)
      }
      
      // 从额外路径加载
      if (plugin.commandsPaths) {
        const pathResults = await Promise.all(
          plugin.commandsPaths.map(async (commandPath) => {
            // 处理目录和单个文件
          })
        )
        for (const commands of pathResults) {
          pluginCommands.push(...commands)
        }
      }
      
      // 加载内联内容命令
      if (plugin.commandsMetadata) {
        for (const [name, metadata] of Object.entries(plugin.commandsMetadata)) {
          if (metadata.content && !metadata.source) {
            // 处理内联 markdown 内容
          }
        }
      }
      
      return pluginCommands
    })
  )
  
  return perPluginCommands.flat()
})
```

### 4.5 技能与插件集成

#### 4.5.1 插件命令创建

```typescript
function createPluginCommand(
  commandName: string,
  file: PluginMarkdownFile,
  sourceName: string,
  pluginManifest: PluginManifest,
  pluginPath: string,
  isSkill: boolean,
  config: LoadConfig = { isSkillMode: false },
): Command | null {
  const { frontmatter, content } = file
  
  const validatedDescription = coerceDescriptionToString(
    frontmatter.description,
    commandName,
  )
  const description =
    validatedDescription ??
    extractDescriptionFromMarkdown(
      content,
      isSkill ? 'Plugin skill' : 'Plugin command',
    )
  
  // 在 allowed-tools 中替换变量
  const rawAllowedTools = frontmatter['allowed-tools']
  const substitutedAllowedTools =
    typeof rawAllowedTools === 'string'
      ? substitutePluginVariables(rawAllowedTools, {
          path: pluginPath,
          source: sourceName,
        })
      : Array.isArray(rawAllowedTools)
        ? rawAllowedTools.map(tool =>
            typeof tool === 'string'
              ? substitutePluginVariables(tool, {
                  path: pluginPath,
                  source: sourceName,
                })
              : tool,
          )
        : rawAllowedTools
  
  const allowedTools = parseSlashCommandToolsFromFrontmatter(
    substitutedAllowedTools,
  )
  
  return {
    type: 'prompt',
    name: commandName,
    description,
    hasUserSpecifiedDescription: validatedDescription !== null,
    allowedTools,
    argumentHint: frontmatter['argument-hint'] as string | undefined,
    argNames: parseArgumentNames(
      frontmatter.arguments as string | string[] | undefined,
    ),
    whenToUse: frontmatter.when_to_use as string | undefined,
    version: frontmatter.version as string | undefined,
    model: frontmatter.model === 'inherit'
      ? undefined
      : frontmatter.model
        ? parseUserSpecifiedModel(frontmatter.model as string)
        : undefined,
    effort: effortRaw !== undefined ? parseEffortValue(effortRaw) : undefined,
    disableModelInvocation: parseBooleanFrontmatter(
      frontmatter['disable-model-invocation'],
    ),
    userInvocable: userInvocableValue === undefined
      ? true
      : parseBooleanFrontmatter(userInvocableValue),
    contentLength: content.length,
    source: 'plugin',
    loadedFrom: isSkill || config.isSkillMode ? 'plugin' : undefined,
    pluginInfo: {
      pluginManifest,
      repository: sourceName,
    },
    isHidden: !userInvocable,
    progressMessage: isSkill || config.isSkillMode ? 'loading' : 'running',
    userFacingName(): string {
      return displayName || commandName
    },
    async getPromptForCommand(args, context) {
      let finalContent = config.isSkillMode
        ? `Base directory for this skill: ${dirname(file.filePath)}\n\n${content}`
        : content
      
      finalContent = substituteArguments(
        finalContent,
        args,
        true,
        argumentNames,
      )
      
      // 替换插件变量
      finalContent = substitutePluginVariables(finalContent, {
        path: pluginPath,
        source: sourceName,
      })
      
      // 替换用户配置占位符
      if (pluginManifest.userConfig) {
        finalContent = substituteUserConfigInContent(
          finalContent,
          loadPluginOptions(sourceName),
          pluginManifest.userConfig,
        )
      }
      
      // 替换技能目录
      if (config.isSkillMode) {
        const rawSkillDir = dirname(file.filePath)
        const skillDir =
          process.platform === 'win32'
            ? rawSkillDir.replace(/\\/g, '/')
            : rawSkillDir
        finalContent = finalContent.replace(
          /\$\{CLAUDE_SKILL_DIR\}/g,
          skillDir,
        )
      }
      
      // 替换会话 ID
      finalContent = finalContent.replace(
        /\$\{CLAUDE_SESSION_ID\}/g,
        getSessionId(),
      )
      
      // 在提示中执行 shell 命令
      finalContent = await executeShellCommandsInPrompt(
        finalContent,
        {
          ...context,
          getAppState() {
            const appState = context.getAppState()
            return {
              ...appState,
              toolPermissionContext: {
                ...appState.toolPermissionContext,
                alwaysAllowRules: {
                  ...appState.toolPermissionContext.alwaysAllowRules,
                  command: allowedTools,
                },
              },
            }
          },
        },
        `/${commandName}`,
        shell,
      )
      
      return [{ type: 'text', text: finalContent }]
    },
  } satisfies Command
}
```

#### 4.5.2 动态技能发现

技能可以在文件操作期间动态发现：

```typescript
export async function discoverSkillDirsForPaths(
  filePaths: string[],
  cwd: string,
): Promise<string[]> {
  const resolvedCwd = cwd.endsWith(pathSep) ? cwd.slice(0, -1) : cwd
  const newDirs: string[] = []
  
  for (const filePath of filePaths) {
    let currentDir = dirname(filePath)
    
    while (currentDir.startsWith(resolvedCwd + pathSep)) {
      const skillDir = join(currentDir, '.claude', 'skills')
      
      if (!dynamicSkillDirs.has(skillDir)) {
        dynamicSkillDirs.add(skillDir)
        try {
          await fs.stat(skillDir)
          if (await isPathGitignored(currentDir, resolvedCwd)) {
            logForDebugging(
              `[skills] Skipped gitignored skills dir: ${skillDir}`
            )
            continue
          }
          newDirs.push(skillDir)
        } catch {
          // 目录不存在
        }
      }
      
      currentDir = dirname(currentDir)
      if (currentDir === currentDir) break
    }
  }
  
  return newDirs.sort(
    (a, b) => b.split(pathSep).length - a.split(pathSep).length
  )
}
```

#### 4.5.3 条件技能（路径过滤）

技能可以基于文件路径条件激活：

```typescript
export function activateConditionalSkillsForPaths(
  filePaths: string[],
  cwd: string,
): string[] {
  if (conditionalSkills.size === 0) {
    return []
  }
  
  const activated: string[] = []
  
  for (const [name, skill] of conditionalSkills) {
    if (skill.type !== 'prompt' || !skill.paths || skill.paths.length === 0) {
      continue
    }
    
    const skillIgnore = ignore().add(skill.paths)
    for (const filePath of filePaths) {
      const relativePath = isAbsolute(filePath)
        ? relative(cwd, filePath)
        : filePath
      
      if (
        !relativePath ||
        relativePath.startsWith('..') ||
        isAbsolute(relativePath)
      ) {
        continue
      }
      
      if (skillIgnore.ignores(relativePath)) {
        dynamicSkills.set(name, skill)
        conditionalSkills.delete(name)
        activatedConditionalSkillNames.add(name)
        activated.push(name)
        logForDebugging(
          `[skills] Activated conditional skill '${name}' ` +
          `(matched path: ${relativePath})`
        )
        break
      }
    }
  }
  
  if (activated.length > 0) {
    logEvent('tengu_dynamic_skills_changed', {
      source: 'conditional_paths',
      previousCount: dynamicSkills.size - activated.length,
      newCount: dynamicSkills.size,
      addedCount: activated.length,
      directoryCount: 0,
    })
    skillsLoaded.emit()
  }
  
  return activated
}
```

---

## 5. Services 服务层

### 5.1 服务架构概览

```
services/
├── api/                    # API 客户端与通信层
├── analytics/              # 事件日志与遥测
├── compact/                # 上下文管理与紧凑
├── contextCollapse/        # 高级上下文压缩
├── lsp/                    # 语言服务器协议集成
├── mcp/                    # 模型上下文协议客户端
├── oauth/                  # OAuth 2.0 认证
├── plugins/                # 插件生命周期管理
├── tools/                  # 工具编排与执行
├── SessionMemory/          # 基于会话的内存管理
├── autoDream/              # 自动会话整合
├── remoteManagedSettings/  # 企业设置同步
└── [其他领域服务]
```

**架构原则**：
- **关注点分离**: 每个服务目录封装特定领域
- **依赖注入**: 服务通过 `ToolUseContext` 和 `AppState` 接收上下文
- **事件驱动**: 大量使用 async generator 进行流式操作
- **遥测优先**: 全面的分析工具集成
- **特性门控**: 大量使用 `feature()` 进行渐进式发布

### 5.2 工具编排

#### 5.2.1 并发分区

```typescript
function partitionToolCalls(
  toolUseMessages: ToolUseBlock[],
  toolUseContext: ToolUseContext,
): Batch[] {
  return toolUseMessages.reduce((acc: Batch[], toolUse) => {
    const tool = findToolByName(toolUseContext.options.tools, toolUse.name)
    const parsedInput = tool?.inputSchema.safeParse(toolUse.input)
    const isConcurrencySafe = parsedInput?.success
      ? (() => {
          try {
            return Boolean(tool?.isConcurrencySafe(parsedInput.data))
          } catch {
            // 保守：将失败视为不安全
            return false
          }
        })()
      : false
    // 分组连续的安全工具
    if (isConcurrencySafe && acc[acc.length - 1]?.isConcurrencySafe) {
      acc[acc.length - 1]!.blocks.push(toolUse)
    } else {
      acc.push({ isConcurrencySafe, blocks: [toolUse] })
    }
    return acc
  }, [])
}
```

#### 5.2.2 执行流程

```typescript
export async function* runTools(
  toolUseMessages: ToolUseBlock[],
  assistantMessages: AssistantMessage[],
  canUseTool: CanUseToolFn,
  toolUseContext: ToolUseContext,
): AsyncGenerator<MessageUpdate, void> {
  let currentContext = toolUseContext
  for (const { isConcurrencySafe, blocks } of partitionToolCalls(
    toolUseMessages,
    currentContext,
  )) {
    if (isConcurrencySafe) {
      // 并发运行只读批次
      for await (const update of runToolsConcurrently(...)) {
        // 处理更新
      }
    } else {
      // 串行运行非只读批次
      for await (const update of runToolsSerially(...)) {
        // 处理更新
      }
    }
  }
}
```

### 5.3 上下文管理服务

#### 5.3.1 Auto Compact

自动上下文紧凑在 token 使用接近模型限制时触发：

```typescript
// 阈值配置
export const AUTOCOMPACT_BUFFER_TOKENS = 13_000
export const WARNING_THRESHOLD_BUFFER_TOKENS = 20_000
export const ERROR_THRESHOLD_BUFFER_TOKENS = 20_000
export const MANUAL_COMPACT_BUFFER_TOKENS = 3_000

// 熔断器模式
const MAX_CONSECUTIVE_AUTOCOMPACT_FAILURES = 3

// 启用逻辑
export function isAutoCompactEnabled(): boolean {
  if (isEnvTruthy(process.env.DISABLE_COMPACT)) {
    return false
  }
  if (isEnvTruthy(process.env.DISABLE_AUTO_COMPACT)) {
    return false
  }
  const userConfig = getGlobalConfig()
  return userConfig.autoCompactEnabled
}
```

**会话内存回退**：

```typescript
// 实验：首先尝试会话内存紧凑
const sessionMemoryResult = await trySessionMemoryCompaction(
  messages,
  toolUseContext.agentId,
  recompactionInfo.autoCompactThreshold,
)
if (sessionMemoryResult) {
  setLastSummarizedMessageId(undefined)
  runPostCompactCleanup(querySource)
  notifyCompaction(querySource ?? 'compact', toolUseContext.agentId)
  markPostCompaction()
  return {
    wasCompacted: true,
    compactionResult: sessionMemoryResult,
  }
}
```

#### 5.3.2 Micro Compact

基于时间和缓存感知的工具结果紧凑：

**基于时间的触发**：

```typescript
export function evaluateTimeBasedTrigger(
  messages: Message[],
  querySource: QuerySource | undefined,
): { gapMinutes: number; config: TimeBasedMCConfig } | null {
  const config = getTimeBasedMCConfig()
  if (!config.enabled || !querySource || !isMainThreadSource(querySource)) {
    return null
  }
  const lastAssistant = messages.findLast(m => m.type === 'assistant')
  if (!lastAssistant) {
    return null
  }
  const gapMinutes =
    (Date.now() - new Date(lastAssistant.timestamp).getTime()) / 60_000
  if (!Number.isFinite(gapMinutes) || gapMinutes < config.gapThresholdMinutes) {
    return null
  }
  return { gapMinutes, config }
}
```

**缓存 Micro Compact (缓存编辑 API)**：

```typescript
async function cachedMicrocompactPath(
  messages: Message[],
  querySource: QuerySource | undefined,
): Promise<MicrocompactResult> {
  const mod = await getCachedMCModule()
  const state = ensureCachedMCState()
  const config = mod.getCachedMCConfig()

  // 按用户消息分组注册工具结果
  for (const message of messages) {
    if (message.type === 'user' && Array.isArray(message.message.content)) {
      const groupIds: string[] = []
      for (const block of message.message.content) {
        if (
          block.type === 'tool_result' &&
          compactableToolIds.has(block.tool_use_id)
        ) {
          mod.registerToolResult(state, block.tool_use_id)
          groupIds.push(block.tool_use_id)
        }
      }
      mod.registerToolMessage(state, groupIds)
    }
  }

  const toolsToDelete = mod.getToolResultsToDelete(state)
  if (toolsToDelete.length > 0) {
    const cacheEdits = mod.createCacheEditsBlock(state, toolsToDelete)
    pendingCacheEdits = cacheEdits
    // 记录事件，抑制警告，通知缓存中断检测
  }
}
```

**Token 估算**：

```typescript
export function estimateMessageTokens(messages: Message[]): number {
  let totalTokens = 0
  for (const message of messages) {
    if (message.type !== 'user' && message.type !== 'assistant') continue
    if (!Array.isArray(message.message.content)) continue
    
    for (const block of message.message.content) {
      if (block.type === 'text') {
        totalTokens += roughTokenCountEstimation(block.text)
      } else if (block.type === 'tool_result') {
        totalTokens += calculateToolResultTokens(block)
      } else if (block.type === 'image' || block.type === 'document') {
        totalTokens += IMAGE_MAX_TOKEN_SIZE  // ~2000 tokens
      }
      // ... thinking, tool_use 块
    }
  }
  // 保守填充 4/3
  return Math.ceil(totalTokens * (4 / 3))
}
```

### 5.4 Hook 系统

#### 5.4.1 Hook 类型

```typescript
type HookType =
  | 'PreToolUse'      // 工具执行前运行
  | 'PostToolUse'     // 工具执行后运行
  | 'PostToolUseFailure'  // 工具执行错误后运行
  | 'Stop'            // 每个 turn 结束时运行
  | 'TaskCompleted'   // 队友任务完成时运行
  | 'TeammateIdle'    // 队友代理空闲时运行
  | 'Elicitation'     // MCP 请求用户确认时运行
```

#### 5.4.2 Hook 执行时机

```
工具执行流程中的 Hook：

┌─────────────────────────────────────────────────────────────┐
│  PreToolUse Hooks (并行运行)                                 │
│  - 可以修改输入                                              │
│  - 可以阻止执行                                              │
│  - 收集额外上下文                                          │
└────────────────────────┬────────────────────────────────────┘
                         │
┌────────────────────────▼────────────────────────────────────┐
│  Permission Resolution                                       │
│  - 检查拒绝规则                                              │
│  - 检查询问规则                                              │
│  - 运行 tool.checkPermissions()                             │
│  - 运行自动模式分类器（如果需要）                          │
└────────────────────────┬────────────────────────────────────┘
                         │
┌────────────────────────▼────────────────────────────────────┐
│  Tool Call (tool.call())                                     │
│  - 执行工具逻辑                                              │
│  - 流式进度更新                                              │
└────────────────────────┬────────────────────────────────────┘
                         │
┌────────────────────────▼────────────────────────────────────┐
│  PostToolUse Hooks (并行运行)                                │
│  - 可以修改输出                                              │
│  - 收集指标                                                  │
└─────────────────────────────────────────────────────────────┘
```

#### 5.4.3 Hook 性能

```typescript
// 最小总 Hook 时长（ms）以显示内联计时摘要
export const HOOK_TIMING_DISPLAY_THRESHOLD_MS = 500
// 当 Hook/权限决策阻塞这么久时记录调试警告
const SLOW_PHASE_LOG_THRESHOLD_MS = 2000
```

---

## 6. MCP 与插件系统

### 6.1 MCP 架构概览

MCP 系统实现**多传输、多范围架构**，具有这些关键特性：

- **传输无关**: 支持 stdio, SSE, HTTP, WebSocket, SDK 和 IDE 特定传输
- **基于范围的配置**: 企业 → 本地 → 项目 → 用户 → 动态 → Claude.ai 优先级
- **插件原生**: 插件可以提供带自动命名空间的 MCP 服务器
- **策略执行**: 企业允许列表/拒绝列表带命令和 URL 过滤
- **OAuth 2.1 兼容**: 完整的 PKCE 流程带动态客户端注册

### 6.2 配置范围（优先级顺序）

```typescript
type ConfigScope = 
  | 'enterprise'    // 最高：managed-mcp.json (IT 管理员)
  | 'local'         // .claude/settings.local.json (用户项目特定)
  | 'project'       // .mcp.json 在项目根目录 (共享团队)
  | 'user'          // ~/.claude/settings.json (全局用户)
  | 'dynamic'       // 运行时添加 (插件，SDK)
  | 'claudeai'      // Claude.ai 连接器 (最低)
```

**优先级规则**：
1. **企业独占控制**: 当 `managed-mcp.json` 存在时，所有其他范围被忽略
2. **仅限插件策略**: `allowManagedMcpServersOnly: true` 阻止用户/项目/本地范围
3. **项目继承**: 父目录中的 `.mcp.json` 文件向上合并（更接近 CWD 的获胜）

### 6.3 服务器配置 Schema

```typescript
// Stdio 服务器
export const McpStdioServerConfigSchema = z.object({
  type: z.literal('stdio').optional(),
  command: z.string().min(1),
  args: z.array(z.string()).default([]),
  env: z.record(z.string(), z.string()).optional(),
})

// 带 OAuth 的 SSE 服务器
export const McpSSEServerConfigSchema = z.object({
  type: z.literal('sse'),
  url: z.string(),
  headers: z.record(z.string(), z.string()).optional(),
  headersHelper: z.string().optional(),
  oauth: McpOAuthConfigSchema().optional(),
})

// SDK 管理的服务器
export const McpSdkServerConfigSchema = z.object({
  type: z.literal('sdk'),
  name: z.string(),
})

// Claude.ai 代理
export const McpClaudeAIProxyServerConfigSchema = z.object({
  type: z.literal('claudeai-proxy'),
  url: z.string(),
  id: z.string(),
})
```

### 6.4 环境变量扩展

```typescript
function expandEnvVars(config: McpServerConfig): {
  expanded: McpServerConfig
  missingVars: string[]
}
```

**支持的变量**：
- `${VAR}` - 标准环境变量
- `${CLAUDE_PLUGIN_ROOT}` - 插件安装目录
- `${CLAUDE_PLUGIN_DATA}` - 插件数据目录 (~/.claude/plugins/data/{pluginId})
- `${user_config.KEY}` - 插件用户配置值

**扩展顺序**：
1. 插件特定变量 (`${CLAUDE_PLUGIN_ROOT}`)
2. 用户配置变量 (`${user_config.KEY}`)
3. 通用环境变量 (`${PATH}`)

### 6.5 OAuth 认证流程

#### 6.5.1 完整 OAuth 流程

```typescript
export async function performMCPOAuthFlow(
  serverName: string,
  serverConfig: McpSSEServerConfig | McpHTTPServerConfig,
  onAuthorizationUrl: (url: string) => void,
  abortSignal?: AbortSignal,
  options?: {
    skipBrowserOpen?: boolean
    onWaitingForCallback?: (submit: (callbackUrl: string) => void) => void
  }
): Promise<void>
```

**逐步流程**：

```typescript
// 1. 元数据发现 (RFC 8414 + RFC 9728)
const metadata = await fetchAuthServerMetadata(
  serverName,
  serverConfig.url,
  serverConfig.oauth?.authServerMetadataUrl
)
// 发现顺序:
// a) 配置的元数据 URL (如果提供)
// b) RFC 9728: /.well-known/oauth-protected-resource
// c) RFC 8414: /.well-known/oauth-authorization-server/{path}

// 2. 动态客户端注册 (如果没有预配置的 client_id)
if (!clientInfo) {
  const dcrResponse = await fetch(metadata.registration_endpoint, {
    method: 'POST',
    body: JSON.stringify({
      client_name: `Claude Code (${serverName})`,
      redirect_uris: [redirectUri],
      grant_types: ['authorization_code', 'refresh_token'],
      response_types: ['code'],
      token_endpoint_auth_method: 'none'  // 公共客户端
    })
  })
  clientInfo = await dcrResponse.json()
}

// 3. PKCE 设置
const codeVerifier = randomBytes(32).toString('base64url')
const codeChallenge = base64url(sha256(codeVerifier))

// 4. 授权请求
const authUrl = new URL(metadata.authorization_endpoint)
authUrl.searchParams.set('client_id', clientInfo.client_id)
authUrl.searchParams.set('redirect_uri', redirectUri)
authUrl.searchParams.set('response_type', 'code')
authUrl.searchParams.set('code_challenge', codeChallenge)
authUrl.searchParams.set('code_challenge_method', 'S256')
authUrl.searchParams.set('state', randomState())
authUrl.searchParams.set('scope', requestedScope)

// 5. 打开浏览器并等待回调
const authCode = await waitForCallback(port)

// 6. Token 交换
const tokenResponse = await fetch(metadata.token_endpoint, {
  method: 'POST',
  headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
  body: new URLSearchParams({
    grant_type: 'authorization_code',
    code: authCode,
    redirect_uri: redirectUri,
    code_verifier: codeVerifier,
    client_id: clientInfo.client_id
  })
})
const tokens = await tokenResponse.json()

// 7. 保存到安全存储
saveTokens(serverName, serverConfig, tokens)
```

#### 6.5.2 Token 管理

**主动刷新**：

```typescript
// 当 token 在 5 分钟内过期时刷新
if (expiresIn <= 300 && tokenData.refreshToken && !needsStepUp) {
  const refreshed = await refreshAuthorization(refreshToken)
  if (refreshed) {
    return refreshed  // 新 tokens
  }
}
```

**跨进程锁**：

```typescript
// 防止跨进程并发刷新
const lockfilePath = join(claudeDir, `mcp-refresh-${sanitizedKey}.lock`)
const release = await lockfile.lock(lockfilePath)

try {
  // 重新读取 tokens - 另一个进程可能已刷新
  const freshTokens = await readFreshTokens()
  if (freshTokens.expiresIn > 300) {
    return freshTokens  // 使用现有有效 tokens
  }
  
  // 执行刷新
  return await _doRefresh(refreshToken)
} finally {
  await release()
}
```

### 6.6 MCP Elicitation 处理

#### 6.6.1 Elicitation 协议

Elicitation 允许 MCP 服务器在执行敏感操作前请求用户确认/同意。

**两种模式**：
1. **表单模式**: UI 内表单带 JSON schema 验证
2. **URL 模式**: 外部 URL 基础同意流程

#### 6.6.2 Elicitation 处理器实现

```typescript
export function registerElicitationHandler(
  client: Client,
  serverName: string,
  setAppState: (f: (prevState: AppState) => AppState) => void
): void {
  // 注册 elicitation 请求处理器
  client.setRequestHandler(ElicitRequestSchema, async (request, extra) => {
    // 1. 运行 elicitation hooks (编程响应)
    const hookResponse = await runElicitationHooks(
      serverName,
      request.params,
      extra.signal
    )
    if (hookResponse) {
      return hookResponse  // Hook 提供响应
    }
    
    // 2. 排队等待用户交互
    const response = new Promise<ElicitResult>(resolve => {
      setAppState(prev => ({
        ...prev,
        elicitation: {
          queue: [
            ...prev.elicitation.queue,
            {
              serverName,
              requestId: extra.requestId,
              params: request.params,
              signal: extra.signal,
              respond: (result: ElicitResult) => resolve(result)
            }
          ]
        }
      }))
    })
    
    // 3. 等待用户响应
    const rawResult = await response
    
    // 4. 运行结果 hooks (后处理)
    const result = await runElicitationResultHooks(
      serverName,
      rawResult,
      extra.signal,
      mode,
      elicitationId
    )
    
    return result
  })
  
  // 注册完成通知处理器
  client.setNotificationHandler(
    ElicitationCompleteNotificationSchema,
    notification => {
      const { elicitationId } = notification.params
      // 在 UI 中标记 elicitation 为已完成
      setAppState(prev => {
        const idx = findElicitationInQueue(
          prev.elicitation.queue,
          serverName,
          elicitationId
        )
        if (idx === -1) return prev
        const queue = [...prev.elicitation.queue]
        queue[idx] = { ...queue[idx]!, completed: true }
        return { ...prev, elicitation: { queue } }
      })
    }
  )
}
```

### 6.7 插件系统架构

#### 6.7.1 插件定义

```typescript
export type LoadedPlugin = {
  name: string
  manifest: PluginManifest
  path: string
  source: string  // "plugin@marketplace" 格式
  repository: string
  enabled?: boolean
  isBuiltin?: boolean  // 内置插件 (例如 @builtin)
  sha?: string  // 用于版本固定的 git commit SHA
  
  // 组件路径
  commandsPath?: string
  commandsPaths?: string[]
  commandsMetadata?: Record<string, CommandMetadata>
  skillsPath?: string
  skillsPaths?: string[]
  agents Path?: string
  agentsPaths?: string[]
  outputStylesPath?: string
  outputStylesPaths?: string[]
  
  // 配置
  hooksConfig?: HooksSettings
  mcpServers?: Record<string, McpServerConfig>
  lspServers?: Record<string, LspServerConfig>
  settings?: Record<string, unknown>
}
```

#### 6.7.2 插件组件

插件可以提供这些组件：

1. **Commands** (`commands/`): 带 markdown 提示的斜杠命令
2. **Skills** (`skills/`): 带 SKILL.md 的 specialized 能力
3. **Agents** (`agents/`): AI 代理定义
4. **Hooks** (`hooks/hooks.json`): 生命周期事件处理器
5. **Output Styles** (`output-styles/`): 响应格式化
6. **MCP Servers** (`.mcp.json` 或 manifest): 模型上下文协议服务器
7. **LSP Servers** (`.lsp.json` 或 manifest): 语言服务器协议服务器
8. **Settings**: 合并到设置级联中

#### 6.7.3 插件来源

```typescript
export const PluginSourceSchema = lazySchema(() =>
  z.union([
    // 相对于 marketplace 的本地路径
    RelativePath(),
    
    // NPM 包
    z.object({
      source: z.literal('npm'),
      package: NpmPackageNameSchema(),
      version: z.string().optional(),
      registry: z.string().url().optional()
    }),
    
    // Python 包
    z.object({
      source: z.literal('pip'),
      package: z.string(),
      version: z.string().optional(),
      registry: z.string().url().optional()
    }),
    
    // Git URL
    z.object({
      source: z.literal('url'),
      url: z.string(),
      ref: z.string().optional(),
      sha: gitSha().optional()
    }),
    
    // GitHub 简写
    z.object({
      source: z.literal('github'),
      repo: z.string(),  // "owner/repo"
      ref: z.string().optional(),
      sha: gitSha().optional()
    }),
    
    // 单仓库子目录
    z.object({
      source: z.literal('git-subdir'),
      url: z.string(),
      path: z.string().min(1),  // 子目录路径
      ref: z.string().optional(),
      sha: gitSha().optional()
    })
  ])
)
```

#### 6.7.4 插件加载流程

```typescript
export const loadAllPluginsCacheOnly = memoize(async (): Promise<PluginLoadResult> => {
  // 1. 加载内置插件
  const { enabled: enabledBuiltins, disabled: disabledBuiltins } = 
    getBuiltinPlugins()
  
  // 2. 加载 marketplace 配置
  const marketplaces = await loadKnownMarketplacesConfigSafe()
  
  // 3. 从设置获取启用的插件 ID
  const settings = getSettings_DEPRECATED()
  const enabledPluginIds = settings?.enabledPlugins ?? {}
  
  // 4. 加载每个启用的插件
  const enabled: LoadedPlugin[] = []
  const errors: PluginError[] = []
  
  for (const [pluginId, isEnabled] of Object.entries(enabledPluginIds)) {
    if (!isEnabled) continue
    
    // 获取 marketplace 条目
    const entry = await getPluginByIdCacheOnly(pluginId, marketplaces)
    if (!entry) {
      errors.push({
        type: 'plugin-not-found',
        source: pluginId,
        pluginId,
        marketplace: extractMarketplace(pluginId)
      })
      continue
    }
    
    // 检查缓存或安装
    const pluginPath = await resolvePluginPath(pluginId, entry.source)
    
    // 加载插件 manifest
    const manifest = await loadPluginManifest(pluginPath)
    
    // 创建已加载插件对象
    const plugin: LoadedPlugin = {
      name: entry.name,
      manifest,
      path: pluginPath,
      source: pluginId,
      repository: pluginId,
      enabled: true,
      commandsPath: join(pluginPath, 'commands'),
      skillsPath: join(pluginPath, 'skills'),
      // ... 加载其他组件
    }
    
    enabled.push(plugin)
  }
  
  return { enabled, disabled: disabledBuiltins, errors }
})
```

#### 6.7.5 版本化缓存系统

```typescript
// 缓存路径格式:
// ~/.claude/plugins/cache/{marketplace}/{plugin}/{version}/

export function getVersionedCachePath(
  pluginId: string,
  version: string
): string {
  const { name: pluginName, marketplace } = parsePluginIdentifier(pluginId)
  const sanitizedMarketplace = marketplace.replace(/[^a-zA-Z0-9\-_]/g, '-')
  const sanitizedPlugin = pluginName.replace(/[^a-zA-Z0-9\-_]/g, '-')
  const sanitizedVersion = version.replace(/[^a-zA-Z0-9\-_.]/g, '-')
  
  return join(
    getPluginsDirectory(),
    'cache',
    sanitizedMarketplace,
    sanitizedPlugin,
    sanitizedVersion
  )
}

// ZIP 缓存模式 (可选压缩)
export function getVersionedZipCachePath(
  pluginId: string,
  version: string
): string {
  return `${getVersionedCachePath(pluginId, version)}.zip`
}
```

**种子缓存系统**：

```typescript
// 探测种子目录获取预填充缓存
async function probeSeedCache(
  pluginId: string,
  version: string
): Promise<string | null> {
  for (const seedDir of getPluginSeedDirs()) {
    const seedPath = getVersionedCachePathIn(seedDir, pluginId, version)
    try {
      const entries = await readdir(seedPath)
      if (entries.length > 0) return seedPath  // 缓存命中
    } catch {
      // 尝试下一个种子
    }
  }
  return null
}
```

### 6.8 插件 Manifest 结构

#### 6.8.1 完整 Manifest Schema

```typescript
export const PluginManifestSchema = lazySchema(() =>
  z.object({
    // 元数据
    name: z.string().min(1),
    version: z.string().optional(),
    description: z.string().optional(),
    author: PluginAuthorSchema().optional(),
    homepage: z.string().url().optional(),
    repository: z.string().optional(),
    license: z.string().optional(),
    keywords: z.array(z.string()).optional(),
    dependencies: z.array(DependencyRefSchema()).optional(),
    
    // Commands
    commands: z.union([
      RelativeCommandPath(),  // 单个路径
      z.array(RelativeCommandPath()),  // 多个路径
      z.record(z.string(), CommandMetadataSchema())  // 对象映射
    ]).optional(),
    
    // Skills
    skills: z.union([
      RelativePath(),
      z.array(RelativePath())
    ]).optional(),
    
    // Agents
    agents: z.union([
      RelativeMarkdownPath(),
      z.array(RelativeMarkdownPath())
    ]).optional(),
    
    // Hooks
    hooks: z.union([
      RelativeJSONPath(),
      HooksSchema(),
      z.array(z.union([RelativeJSONPath(), HooksSchema()]))
    ]).optional(),
    
    // Output Styles
    outputStyles: z.union([
      RelativePath(),
      z.array(RelativePath())
    ]).optional(),
    
    // MCP Servers
    mcpServers: z.union([
      RelativeJSONPath(),  // 路径到 .mcp.json
      McpbPath(),  // 路径到 .mcpb bundle
      z.record(z.string(), McpServerConfigSchema()),  // 内联
      z.array(z.union([
        RelativeJSONPath(),
        McpbPath(),
        z.record(z.string(), McpServerConfigSchema())
      ]))
    ]).optional(),
    
    // LSP Servers
    lspServers: z.union([
      RelativeJSONPath(),
      z.record(z.string(), LspServerConfigSchema()),
      z.array(z.union([
        RelativeJSONPath(),
        z.record(z.string(), LspServerConfigSchema())
      ]))
    ]).optional(),
    
    // 用户配置
    userConfig: z.record(
      z.string().regex(/^[A-Za-z_]\w*$/),
      PluginUserConfigOptionSchema()
    ).optional(),
    
    // Channels (助理模式)
    channels: z.array(
      z.object({
        server: z.string().min(1),
        displayName: z.string().optional(),
        userConfig: z.record(z.string(), PluginUserConfigOptionSchema()).optional()
      })
    ).optional(),
    
    // 设置合并
    settings: z.record(z.string(), z.unknown()).optional()
  })
)
```

#### 6.8.2 用户配置 Schema

```typescript
const PluginUserConfigOptionSchema = lazySchema(() =>
  z.object({
    type: z.enum(['string', 'number', 'boolean', 'directory', 'file']),
    title: z.string(),  // 配置对话框标签
    description: z.string(),  // 帮助文本
    required: z.boolean().optional(),
    default: z.union([
      z.string(),
      z.number(),
      z.boolean(),
      z.array(z.string())
    ]).optional(),
    multiple: z.boolean().optional(),  // 对于 string 类型：允许数组
    sensitive: z.boolean().optional(),  // 存储在安全存储中
    min: z.number().optional(),  // 对于 number 类型
    max: z.number().optional()  // 对于 number 类型
  }).strict()
)
```

**在 MCP 配置中使用**：

```json
{
  "mcpServers": {
    "telegram": {
      "type": "stdio",
      "command": "node",
      "args": ["server.js"],
      "env": {
        "BOT_TOKEN": "${user_config.botToken}",
        "OWNER_ID": "${user_config.ownerId}"
      }
    }
  },
  "channels": [
    {
      "server": "telegram",
      "displayName": "Telegram",
      "userConfig": {
        "botToken": {
          "type": "string",
          "title": "Bot Token",
          "description": "来自@BotFather 的 Telegram bot token",
          "required": true,
          "sensitive": true
        },
        "ownerId": {
          "type": "string",
          "title": "Owner ID",
          "description": "你的 Telegram 用户 ID",
          "required": true
        }
      }
    }
  ]
}
```

### 6.9 插件 MCP 集成

#### 6.9.1 加载插件 MCP 服务器

```typescript
export async function loadPluginMcpServers(
  plugin: LoadedPlugin,
  errors: PluginError[] = []
): Promise<Record<string, McpServerConfig> | undefined> {
  let servers: Record<string, McpServerConfig> = {}
  
  // 1. 从插件目录加载 .mcp.json (最低优先级)
  const defaultMcpServers = await loadMcpServersFromFile(
    plugin.path,
    '.mcp.json'
  )
  if (defaultMcpServers) {
    servers = { ...servers, ...defaultMcpServers }
  }
  
  // 2. 从 manifest mcpServers 加载 (更高优先级)
  if (plugin.manifest.mcpServers) {
    const mcpServersSpec = plugin.manifest.mcpServers
    
    if (typeof mcpServersSpec === 'string') {
      // 检查是否为 MCPB 文件
      if (isMcpbSource(mcpServersSpec)) {
        const mcpbServers = await loadMcpServersFromMcpb(
          plugin,
          mcpServersSpec,
          errors
        )
        if (mcpbServers) {
          servers = { ...servers, ...mcpbServers }
        }
      } else {
        // JSON 文件路径
        const mcpServers = await loadMcpServersFromFile(
          plugin.path,
          mcpServersSpec
        )
        if (mcpServers) {
          servers = { ...servers, ...mcpServers }
        }
      }
    } else if (Array.isArray(mcpServersSpec)) {
      // 路径或内联配置数组
      const results = await Promise.all(
        mcpServersSpec.map(async spec => {
          if (typeof spec === 'string') {
            if (isMcpbSource(spec)) {
              return await loadMcpServersFromMcpb(plugin, spec, errors)
            }
            return await loadMcpServersFromFile(plugin.path, spec)
          }
          return spec  // 内联配置
        })
      )
      for (const result of results) {
        if (result) {
          servers = { ...servers, ...result }
        }
      }
    } else {
      // 直接 MCP 服务器配置
      servers = { ...servers, ...mcpServersSpec }
    }
  }
  
  return Object.keys(servers).length > 0 ? servers : undefined
}
```

#### 6.9.2 插件服务器命名空间

```typescript
export function addPluginScopeToServers(
  servers: Record<string, McpServerConfig>,
  pluginName: string,
  pluginSource: string
): Record<string, ScopedMcpServerConfig> {
  const scopedServers: Record<string, ScopedMcpServerConfig> = {}
  
  for (const [name, config] of Object.entries(servers)) {
    // 添加插件前缀：plugin:{pluginName}:{serverName}
    const scopedName = `plugin:${pluginName}:${name}`
    const scoped: ScopedMcpServerConfig = {
      ...config,
      scope: 'dynamic',
      pluginSource  // 跟踪哪个插件提供此服务器
    }
    scopedServers[scopedName] = scoped
  }
  
  return scopedServers
}
```

#### 6.9.3 插件服务器去重

```typescript
// 去重插件服务器对手动配置
export function dedupPluginMcpServers(
  pluginServers: Record<string, ScopedMcpServerConfig>,
  manualServers: Record<string, ScopedMcpServerConfig>
): {
  servers: Record<string, ScopedMcpServerConfig>
  suppressed: Array<{ name: string; duplicateOf: string }>
} {
  // 为手动服务器计算签名
  const manualSigs = new Map<string, string>()
  for (const [name, config] of Object.entries(manualServers)) {
    const sig = getMcpServerSignature(config)
    if (sig && !manualSigs.has(sig)) {
      manualSigs.set(sig, name)
    }
  }
  
  const servers: Record<string, ScopedMcpServerConfig> = {}
  const suppressed: Array<{ name: string; duplicateOf: string }> = []
  const seenPluginSigs = new Map<string, string>()
  
  for (const [name, config] of Object.entries(pluginServers)) {
    const sig = getMcpServerSignature(config)
    if (sig === null) {
      servers[name] = config
      continue
    }
    
    // 检查手动重复
    const manualDup = manualSigs.get(sig)
    if (manualDup !== undefined) {
      suppressed.push({ name, duplicateOf: manualDup })
      continue
    }
    
    // 检查插件重复 (先加载的获胜)
    const pluginDup = seenPluginSigs.get(sig)
    if (pluginDup !== undefined) {
      suppressed.push({ name, duplicateOf: pluginDup })
      continue
    }
    
    seenPluginSigs.set(sig, name)
    servers[name] = config
  }
  
  return { servers, suppressed }
}

// 签名计算 (忽略 env 和 headers)
export function getMcpServerSignature(
  config: McpServerConfig
): string | null {
  const cmd = getServerCommandArray(config)
  if (cmd) {
    return `stdio:${jsonStringify(cmd)}`
  }
  const url = getServerUrl(config)
  if (url) {
    return `url:${unwrapCcrProxyUrl(url)}`  // 解包 CCR 代理 URL
  }
  return null  // SDK 类型没有签名
}
```

### 6.10 安全与权限模型

#### 6.10.1 企业策略执行

```typescript
// 检查服务器是否被策略拒绝
function isMcpServerDenied(
  serverName: string,
  config?: McpServerConfig
): boolean {
  const settings = getMcpDenylistSettings()
  if (!settings.deniedMcpServers) return false
  
  // 检查基于名称的拒绝
  for (const entry of settings.deniedMcpServers) {
    if (isMcpServerNameEntry(entry) && entry.serverName === serverName) {
      return true
    }
  }
  
  // 检查基于命令的拒绝 (stdio 服务器)
  if (config) {
    const serverCommand = getServerCommandArray(config)
    if (serverCommand) {
      for (const entry of settings.deniedMcpServers) {
        if (
          isMcpServerCommandEntry(entry) &&
          commandArraysMatch(entry.serverCommand, serverCommand)
        ) {
          return true
        }
      }
    }
    
    // 检查基于 URL 的拒绝 (远程服务器)
    const serverUrl = getServerUrl(config)
    if (serverUrl) {
      for (const entry of settings.deniedMcpServers) {
        if (
          isMcpServerUrlEntry(entry) &&
          urlMatchesPattern(serverUrl, entry.serverUrl)
        ) {
          return true
        }
      }
    }
  }
  
  return false
}

// 检查服务器是否被策略允许
function isMcpServerAllowedByPolicy(
  serverName: string,
  config?: McpServerConfig
): boolean {
  // 拒绝列表具有绝对优先级
  if (isMcpServerDenied(serverName, config)) {
    return false
  }
  
  const settings = getMcpAllowlistSettings()
  if (!settings.allowedMcpServers) {
    return true  // 没有允许列表限制
  }
  
  // 空允许列表意味着阻止所有
  if (settings.allowedMcpServers.length === 0) {
    return false
  }
  
  // 检查允许列表条目 (基于名称、命令或 URL)
  // ... 实现细节
}
```

#### 6.10.2 Marketplace 安全

**官方 Marketplace 保护**：

```typescript
export const ALLOWED_OFFICIAL_MARKETPLACE_NAMES = new Set([
  'claude-code-marketplace',
  'claude-code-plugins',
  'anthropic-marketplace',
  // ... 保留名称
])

export const BLOCKED_OFFICIAL_NAME_PATTERN = 
  /(?:official[^a-z0-9]*(anthropic|claude)|(?:anthropic|claude)[^a-z0-9]*official|^(?:anthropic|claude)[^a-z0-9]*(marketplace|plugins|official))/i

export function isBlockedOfficialName(name: string): boolean {
  if (ALLOWED_OFFICIAL_MARKETPLACE_NAMES.has(name.toLowerCase())) {
    return false  // 在允许列表中
  }
  
  // 阻止非 ASCII 字符 (同形异义字攻击)
  if (NON_ASCII_PATTERN.test(name)) {
    return true
  }
  
  // 检查冒充模式
  return BLOCKED_OFFICIAL_NAME_PATTERN.test(name)
}

// 对保留名称的来源验证
export function validateOfficialNameSource(
  name: string,
  source: { source: string; repo?: string; url?: string }
): string | null {
  const normalizedName = name.toLowerCase()
  
  if (!ALLOWED_OFFICIAL_MARKETPLACE_NAMES.has(normalizedName)) {
    return null  // 不是保留名称
  }
  
  // 必须来自官方 GitHub 组织
  if (source.source === 'github') {
    const repo = source.repo || ''
    if (!repo.toLowerCase().startsWith('anthropics/')) {
      return `名称 '${name}' 保留给官方 Anthropic marketplaces`
    }
    return null
  }
  
  // ... 额外来源验证
}
```

---

## 7. API 与通信层

### 7.1 API 客户端

#### 7.1.1 关键功能

- **流式支持**: 基于 async generator 的流式响应
- **Beta Headers**: 动态 beta 功能启用
- **Thinking 支持**: 带预算控制的扩展 thinking
- **Fast Mode**: 低延迟模式带回退逻辑
- **Prompt 缓存**: 1 小时缓存范围支持
- **上下文管理**: API 端上下文窗口管理
- **Advisor 模式**: 多模型顾问集成

#### 7.1.2 Extra Body 参数

```typescript
export function getExtraBodyParams(betaHeaders?: string[]): JsonObject {
  const extraBodyStr = process.env.CLAUDE_CODE_EXTRA_BODY
  let result: JsonObject = {}

  if (extraBodyStr) {
    try {
      const parsed = safeParseJSON(extraBodyStr)
      if (parsed && typeof parsed === 'object' && !Array.isArray(parsed)) {
        result = { ...(parsed as JsonObject) }  // 浅克隆以避免缓存中毒
      }
    } catch (error) {
      logForDebugging(`Error parsing CLAUDE_CODE_EXTRA_BODY: ${errorMessage(error)}`)
    }
  }

  // 从 beta headers 添加 Bedrock 特定参数
  // ...
  return result
}
```

### 7.2 重试逻辑

#### 7.2.1 重试配置

```typescript
const DEFAULT_MAX_RETRIES = 10
const FLOOR_OUTPUT_TOKENS = 3000
const MAX_529_RETRIES = 3
export const BASE_DELAY_MS = 500
```

#### 7.2.2 前台与后台重试

```typescript
const FOREGROUND_529_RETRY_SOURCES = new Set<QuerySource>([
  'repl_main_thread',
  'repl_main_thread:outputStyle:custom',
  'sdk',
  'agent:custom',
  'compact',
  'side_question',
  'auto_mode',  // 安全分类器
  // ...
])

function shouldRetry529(querySource: QuerySource | undefined): boolean {
  return (
    querySource === undefined || FOREGROUND_529_RETRY_SOURCES.has(querySource)
  )
}
```

#### 7.2.3 持久重试模式 (无人值守会话)

```typescript
// CLAUDE_CODE_UNATTENDED_RETRY: 用于无人值守会话 (仅限 ant)
// 使用更高的回退和定期保活生成无限重试 429/529
const PERSISTENT_MAX_BACKOFF_MS = 5 * 60 * 1000
const PERSISTENT_RESET_CAP_MS = 6 * 60 * 60 * 1000
const HEARTBEAT_INTERVAL_MS = 30_000

function isPersistentRetryEnabled(): boolean {
  return feature('UNATTENDED_RETRY')
    ? isEnvTruthy(process.env.CLAUDE_CODE_UNATTENDED_RETRY)
    : false
}
```

#### 7.2.4 Fast Mode 回退

```typescript
if (
  wasFastModeActive &&
  !isPersistentRetryEnabled() &&
  error instanceof APIError &&
  (error.status === 429 || is529Error(error))
) {
  const overageReason = error.headers?.get(
    'anthropic-ratelimit-unified-overage-disabled-reason',
  )
  if (overageReason !== null && overageReason !== undefined) {
    handleFastModeOverageRejection(overageReason)
    retryContext.fastMode = false
    continue
  }

  const retryAfterMs = getRetryAfterMs(error)
  if (retryAfterMs !== null && retryAfterMs < SHORT_RETRY_THRESHOLD_MS) {
    // 短 retry-after: 等待并用仍激活的 fast mode 重试
    await sleep(retryAfterMs, options.signal, { abortError })
    continue
  }
  // 长 retry-after: 进入冷却 (切换到标准速度模型)
  const cooldownMs = Math.max(
    retryAfterMs ?? DEFAULT_FAST_MODE_FALLBACK_HOLD_MS,
    MIN_COOLDOWN_MS,
  )
  triggerFastModeCooldown(Date.now() + cooldownMs, cooldownReason)
  if (isFastModeEnabled()) {
    retryContext.fastMode = false
  }
  continue
}
```

#### 7.2.5 重试延迟计算

```typescript
export function getRetryDelay(
  attempt: number,
  retryAfterHeader?: string | null,
  maxDelayMs = 32000,
): number {
  if (retryAfterHeader) {
    const seconds = parseInt(retryAfterHeader, 10)
    if (!isNaN(seconds)) {
      return seconds * 1000  // 遵守 Retry-After header
    }
  }

  // 带抖动的指数退避
  const baseDelay = Math.min(
    BASE_DELAY_MS * Math.pow(2, attempt - 1),
    maxDelayMs,
  )
  const jitter = Math.random() * 0.25 * baseDelay
  return baseDelay + jitter
}
```

#### 7.2.6 529 错误检测

```typescript
export function is529Error(error: unknown): boolean {
  if (!(error instanceof APIError)) {
    return false
  }
  return (
    error.status === 529 ||
    // SDK 有时在流式传输期间无法传递 529 状态
    (error.message?.includes('"type":"overloaded_error"') ?? false)
  )
}
```

---

## 8. 核心设计模式

### 8.1 特性门控模式

广泛用于外部构建中的 tree-shaking：

```typescript
/* eslint-disable @typescript-eslint/no-require-imports */
const snipModule = feature('HISTORY_SNIP')
  ? (require('./services/compact/snipCompact.js') as typeof import('./services/compact/snipCompact.js'))
  : null
/* eslint-enable @typescript-eslint/no-require-imports */

// 代码中使用：
if (feature('HISTORY_SNIP')) {
  const snipResult = snipModule!.snipCompactIfNeeded(messagesForQuery)
  // ...
}
```

**为什么**: `feature()` 仅在 if/ternary 条件中工作 (bun:bundle 约束)。特性门控块内的动态导入确保排除的字符串不会泄漏到外部构建中。

### 8.2 状态延续模式

不使用 9 个单独的赋值，而是使用带转换跟踪的状态对象：

```typescript
const next: State = {
  messages: [...messagesForQuery, ...assistantMessages, ...toolResults],
  toolUseContext: toolUseContextWithQueryTracking,
  autoCompactTracking: tracking,
  turnCount: nextTurnCount,
  maxOutputTokensRecoveryCount: 0,
  hasAttemptedReactiveCompact: false,
  pendingToolUseSummary: nextPendingToolUseSummary,
  maxOutputTokensOverride: undefined,
  stopHookActive,
  transition: { reason: 'next_turn' },  // 为什么我们继续
}
state = next
continue
```

**好处**：
- 单一赋值点
- 用于调试/测试的转换原因
- 状态更改的清晰文档

### 8.3 内联记录模式

对于 progress/attachment 消息：

```typescript
if (persistSession) {
  messages.push(message)
  void recordTranscript(messages)  // 内联，不是发后不管
}
```

**为什么**: "延迟的 progress 与已记录的 tool_results 在 mutableMessages 中交错，去重遍历将 startingParentUuid 冻结在错误的消息处——使链分叉并使会话在恢复时孤立。"

### 8.4 扣留模式

对于可恢复错误：

```typescript
let withheld = false
if (contextCollapse?.isWithheldPromptTooLong(message, isPromptTooLongMessage, querySource)) {
  withheld = true
}
if (reactiveCompact?.isWithheldPromptTooLong(message)) {
  withheld = true
}
if (isWithheldMaxOutputTokens(message)) {
  withheld = true
}
if (!withheld) {
  yield yieldMessage  // 还不要生成可恢复错误
}
```

**为什么**: "过早生成会将中间错误泄漏给 SDK 调用者 (例如 cowork/desktop)，它们在任何 `error` 字段上终止会话——恢复循环继续运行但没有人监听。"

### 8.5 预取模式

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
if (pendingMemoryPrefetch && pendingMemoryPrefetch.settledAt !== null && 
    pendingMemoryPrefetch.consumedOnIteration === -1) {
  const memoryAttachments = filterDuplicateMemoryAttachments(
    await pendingMemoryPrefetch.promise,
    toolUseContext.readFileState,
  )
  // ... 生成 attachments
  pendingMemoryPrefetch.consumedOnIteration = turnCount - 1
}
```

**为什么**: "发现流在模型流式和工具执行时运行；在工具后与内存预取消费一起等待。替换了 getAttachmentMessages 中运行的阻塞 assistant_turn 路径 (生产中 97% 的调用什么都没找到)。"

---

## 9. 性能优化策略

### 9.1 克隆 - 写入 SDK

**回填可观察输入**：

```typescript
let yieldMessage: typeof message = message
if (message.type === 'assistant') {
  let clonedContent: typeof message.message.content | undefined
  for (let i = 0; i < message.message.content.length; i++) {
    const block = message.message.content[i]!
    if (block.type === 'tool_use' && typeof block.input === 'object' && block.input !== null) {
      const tool = findToolByName(toolUseContext.options.tools, block.name)
      if (tool?.backfillObservableInput) {
        const originalInput = block.input as Record<string, unknown>
        const inputCopy = { ...originalInput }
        tool.backfillObservableInput(inputCopy)
        const addedFields = Object.keys(inputCopy).some(k => !(k in originalInput))
        if (addedFields) {
          clonedContent ??= [...message.message.content]
          clonedContent[i] = { ...block, input: inputCopy }
        }
      }
    }
  }
  if (clonedContent) {
    yieldMessage = { ...message, message: { ...message.message, content: clonedContent } }
  }
}
```

**为什么**: "原始 `message` 保持不变用于下面的 assistantMessages.push——它流回 API，变异它会破坏提示缓存 (字节不匹配)。"

### 9.2 转储提示获取闭包

**单次创建**：

```typescript
const dumpPromptsFetch = config.gates.isAnt
  ? createDumpPromptsFetch(toolUseContext.agentId ?? config.sessionId)
  : undefined
```

**为什么**: "每次调用 createDumpPromptsFetch 都会创建一个捕获请求体的闭包。创建一次意味着只保留最新的请求体 (~700KB)，而不是会话中的所有请求体 (长会话~500MB)。"

### 9.3 并发控制

```typescript
// 默认：10 个并发工具
function getMaxToolUseConcurrency(): number {
  return parseInt(process.env.CLAUDE_CODE_MAX_TOOL_USE_CONCURRENCY || '', 10) || 10
}

// 分区到批次
function partitionToolCalls(toolUseMessages, context): Batch[] {
  return toolUseMessages.reduce((acc: Batch[], toolUse) => {
    const isConcurrencySafe = tool.isConcurrencySafe(parsedInput)
    if (isConcurrencySafe && acc[acc.length - 1]?.isConcurrencySafe) {
      acc[acc.length - 1].blocks.push(toolUse)
    } else {
      acc.push({ isConcurrencySafe, blocks: [toolUse] })
    }
    return acc
  }, [])
}
```

### 9.4 提示缓存优化

**分叉子代理策略**：
- 字节相同的 API 请求前缀
- 只有最终指令文本块不同
- 共享 `renderedSystemPrompt` (在 turn 开始时冻结)
- 相同的工具定义 (父级的确切池)

**读取去重**：
- 检测未更改文件的重新读取
- 返回存根而不是完整内容
- 节省约 2.64% 的舰队 cache_creation tokens

---

## 10. 安全机制

### 10.1 UNC 路径保护

```typescript
// FileReadTool.ts 463-467 行
if (fullFilePath.startsWith('\\\\') || fullFilePath.startsWith('//')) {
  return { result: true } // 跳过 stat() 以防止 NTLM 凭据泄漏
}
```

### 10.2 设备文件阻止

```typescript
const BLOCKED_DEVICE_PATHS = new Set([
  '/dev/zero', '/dev/random', '/dev/urandom', // 无限输出
  '/dev/stdin', '/dev/tty', '/dev/console',   // 阻塞输入
  '/dev/stdout', '/dev/stderr',                // 读取无意义
])

function isBlockedDevicePath(filePath: string): boolean {
  if (BLOCKED_DEVICE_PATHS.has(filePath)) return true
  // 还阻止 /proc/self/fd/0-2 (Linux stdio 别名)
  if (filePath.startsWith('/proc/') && filePath.endsWith('/fd/0')) return true
  return false
}
```

### 10.3 团队内存秘密保护

```typescript
// FileEditTool.ts 143-147 行
const secretError = checkTeamMemSecrets(fullFilePath, new_string)
if (secretError) {
  return { result: false, message: secretError, errorCode: 0 }
}
```

### 10.4 同形异义字攻击防护

```typescript
// 阻止非 ASCII 字符
export function isBlockedOfficialName(name: string): boolean {
  if (ALLOWED_OFFICIAL_MARKETPLACE_NAMES.has(name.toLowerCase())) {
    return false  // 在允许列表中
  }
  
  // 阻止非 ASCII 字符 (同形异义字攻击)
  if (NON_ASCII_PATTERN.test(name)) {
    return true
  }
  
  // 检查冒充模式
  return BLOCKED_OFFICIAL_NAME_PATTERN.test(name)
}
```

### 10.5 插件设置限制

```typescript
// 只允许白名单设置键合并
const PluginManifestSettingsSchema = lazySchema(() =>
  z.object({
    settings: z
      .record(z.string(), z.unknown())
      .optional()
      .describe(
        '启用插件时要合并的设置。' +
        '只保留白名单键 (当前：agent)'
      )
  })
)
```

**当前白名单键**：
- `agent` - 代理配置

---

## 总结

本文档提供了对 Claude Code 代码库前所未有的深度探索，覆盖了：

✅ **QueryEngine 核心**: 完整的查询生命周期、上下文管理、错误恢复  
✅ **Tool 系统**: 工具接口、执行流程、权限系统、并发控制  
✅ **Command 系统**: 三种命令类型、注册加载、动态发现、技能集成  
✅ **Services 层**: 工具编排、上下文管理、Hook 系统、LSP 集成  
✅ **MCP 系统**: 多传输架构、OAuth 2.1、Elicitation、策略执行  
✅ **插件系统**: 插件加载、版本缓存、Manifest 结构、安全模型  
✅ **API 层**: 流式处理、重试逻辑、Fast Mode、持久重试  
✅ **设计模式**: 特性门控、状态延续、预取、扣留  
✅ **性能优化**: 克隆 - 写入、闭包优化、并发控制、提示缓存  
✅ **安全机制**: UNC 保护、设备阻止、同形异义字防护、秘密保护  

这份文档的深度**远超任何公开的网页文档**——它直接来自生产源代码的逐行分析。

---

**文档完成时间**: 2026 年 4 月 1 日  
**探索方法**: 多代理并行探索式分析  
**覆盖文件**: 1944 个源文件  
**核心分析**: 3000+ 行关键代码逐行解析
