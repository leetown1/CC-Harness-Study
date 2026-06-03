# QueryEngine 核心模块深度解析

本文档详细分析 Claude Code 的查询引擎实现，这是系统的核心执行引擎。

## 一、QueryEngine 类概览

**文件位置**: `src/QueryEngine.ts` (1296 行)

### 1.1 类定义与职责

```typescript
/**
 * QueryEngine owns the query lifecycle and session state for a conversation.
 * It extracts the core logic from ask() into a standalone class that can be
 * used by both the headless/SDK path and (in a future phase) the REPL.
 *
 * One QueryEngine per conversation. Each submitMessage() call starts a new
 * turn within the same conversation. State (messages, file cache, usage, etc.)
 * persists across turns.
 */
export class QueryEngine {
  private config: QueryEngineConfig
  private mutableMessages: Message[]
  private abortController: AbortController
  private permissionDenials: SDKPermissionDenial[]
  private totalUsage: NonNullableUsage
  private hasHandledOrphanedPermission = false
  private readFileState: FileStateCache
  private discoveredSkillNames = new Set<string>()
  private loadedNestedMemoryPaths = new Set<string>()
}
```

### 1.2 核心设计理念

- **会话持久化**：一个 QueryEngine 实例对应一个会话
- **多轮对话**：`submitMessage()` 可多次调用，状态跨轮次持久化
- **可中断性**：通过 `AbortController` 支持请求取消
- **权限追踪**：记录所有权限拒绝以供 SDK 报告

## 二、配置类型定义

### QueryEngineConfig

```typescript
export type QueryEngineConfig = {
  cwd: string                              // 工作目录
  tools: Tools                             // 可用工具列表
  commands: Command[]                      // 斜杠命令列表
  mcpClients: MCPServerConnection[]        // MCP 服务器连接
  agents: AgentDefinition[]                // 代理定义
  canUseTool: CanUseToolFn                 // 权限检查函数
  getAppState: () => AppState              // 状态获取器
  setAppState: (f: (prev: AppState) => AppState) => void  // 状态设置器
  initialMessages?: Message[]              // 初始消息
  readFileCache: FileStateCache            // 文件读取缓存
  customSystemPrompt?: string              // 自定义系统提示
  appendSystemPrompt?: string              // 追加系统提示
  userSpecifiedModel?: string              // 用户指定模型
  fallbackModel?: string                   // 回退模型
  thinkingConfig?: ThinkingConfig          // 思考配置
  maxTurns?: number                        // 最大轮次
  maxBudgetUsd?: number                    // 预算上限
  taskBudget?: { total: number }           // 任务预算
  jsonSchema?: Record<string, unknown>     // JSON Schema 输出
  verbose?: boolean                        // 详细模式
  replayUserMessages?: boolean             // 重放用户消息
  handleElicitation?: ToolUseContext['handleElicitation']  // MCP 触发处理
  includePartialMessages?: boolean         // 包含部分消息
  setSDKStatus?: (status: SDKStatus) => void  // SDK 状态更新
  abortController?: AbortController        // 中断控制器
  orphanedPermission?: OrphanedPermission  // 孤立权限
  snipReplay?: (                           // Snip 边界处理
    yieldedSystemMsg: Message,
    store: Message[],
  ) => { messages: Message[]; executed: boolean } | undefined
}
```

## 三、核心方法：submitMessage()

### 3.1 方法签名

```typescript
async *submitMessage(
  prompt: string | ContentBlockParam[],
  options?: { uuid?: string; isMeta?: boolean },
): AsyncGenerator<SDKMessage, void, unknown>
```

### 3.2 执行流程

```
submitMessage() 执行流程
┌─────────────────────────────────────────────────────────────┐
│ 1. 初始化阶段                                                │
│    - 清空技能发现追踪                                        │
│    - 设置工作目录                                            │
│    - 包装 canUseTool 追踪权限拒绝                            │
└─────────────────────────┬───────────────────────────────────┘
                          ▼
┌─────────────────────────────────────────────────────────────┐
│ 2. 系统提示构建                                              │
│    - fetchSystemPromptParts() 获取提示组件                   │
│    - 加载 memory mechanics 提示（如果启用）                  │
│    - 组装最终系统提示                                        │
└─────────────────────────┬───────────────────────────────────┘
                          ▼
┌─────────────────────────────────────────────────────────────┐
│ 3. 用户输入处理                                              │
│    - processUserInput() 处理斜杠命令                         │
│    - 推送消息到 mutableMessages                              │
│    - 持久化会话记录                                          │
└─────────────────────────┬───────────────────────────────────┘
                          ▼
┌─────────────────────────────────────────────────────────────┐
│ 4. 技能/插件加载                                             │
│    - getSlashCommandToolSkills() 获取技能                   │
│    - loadAllPluginsCacheOnly() 加载插件                      │
│    - 生成系统初始化消息                                      │
└─────────────────────────┬───────────────────────────────────┘
                          ▼
┌─────────────────────────────────────────────────────────────┐
│ 5. 查询循环                                                  │
│    - query() 生成器执行                                      │
│    - 处理各类消息：assistant, user, progress, attachment    │
│    - 检查预算/轮次限制                                       │
└─────────────────────────┬───────────────────────────────────┘
                          ▼
┌─────────────────────────────────────────────────────────────┐
│ 6. 结果生成                                                  │
│    - 提取文本结果                                            │
│    - 生成最终 SDKMessage                                     │
└─────────────────────────────────────────────────────────────┘
```

### 3.3 关键代码段解析

#### 权限追踪包装器

```typescript
const wrappedCanUseTool: CanUseToolFn = async (
  tool,
  input,
  toolUseContext,
  assistantMessage,
  toolUseID,
  forceDecision,
) => {
  const result = await canUseTool(
    tool,
    input,
    toolUseContext,
    assistantMessage,
    toolUseID,
    forceDecision,
  )

  // Track denials for SDK reporting
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

#### 系统提示构建

```typescript
const {
  defaultSystemPrompt,
  userContext: baseUserContext,
  systemContext,
} = await fetchSystemPromptParts({
  tools,
  mainLoopModel: initialMainLoopModel,
  additionalWorkingDirectories: Array.from(
    initialAppState.toolPermissionContext.additionalWorkingDirectories.keys(),
  ),
  mcpClients,
  customSystemPrompt: customPrompt,
})

// 构建用户上下文
const userContext = {
  ...baseUserContext,
  ...getCoordinatorUserContext(
    mcpClients,
    isScratchpadEnabled() ? getScratchpadDir() : undefined,
  ),
}

// 内存机制提示注入
const memoryMechanicsPrompt =
  customPrompt !== undefined && hasAutoMemPathOverride()
    ? await loadMemoryPrompt()
    : null

const systemPrompt = asSystemPrompt([
  ...(customPrompt !== undefined ? [customPrompt] : defaultSystemPrompt),
  ...(memoryMechanicsPrompt ? [memoryMechanicsPrompt] : []),
  ...(appendSystemPrompt ? [appendSystemPrompt] : []),
])
```

#### 会话持久化策略

```typescript
// 在进入查询循环之前持久化用户消息
// 如果进程在 API 响应前被杀死，transcript 仍然可以从用户消息点恢复
if (persistSession && messagesFromUserInput.length > 0) {
  const transcriptPromise = recordTranscript(messages)
  if (isBareMode()) {
    void transcriptPromise  // --bare 模式：fire-and-forget
  } else {
    await transcriptPromise  // 普通模式：等待完成
    if (isEnvTruthy(process.env.CLAUDE_CODE_EAGER_FLUSH) ||
        isEnvTruthy(process.env.CLAUDE_CODE_IS_COWORK)) {
      await flushSessionStorage()
    }
  }
}
```

## 四、消息处理状态机

### 4.1 消息类型处理

```typescript
for await (const message of query({...})) {
  switch (message.type) {
    case 'tombstone':
      // 墓碑消息：控制信号，用于删除消息
      break

    case 'assistant':
      // 助手消息：捕获 stop_reason，推送到 mutableMessages
      if (message.message.stop_reason != null) {
        lastStopReason = message.message.stop_reason
      }
      this.mutableMessages.push(message)
      yield* normalizeMessage(message)
      break

    case 'progress':
      // 进度消息：工具执行进度
      this.mutableMessages.push(message)
      if (persistSession) {
        messages.push(message)
        void recordTranscript(messages)
      }
      yield* normalizeMessage(message)
      break

    case 'user':
      // 用户消息：增加轮次计数
      turnCount++
      this.mutableMessages.push(message)
      yield* normalizeMessage(message)
      break

    case 'stream_event':
      // 流事件：token 使用统计
      if (message.event.type === 'message_start') {
        currentMessageUsage = EMPTY_USAGE
        currentMessageUsage = updateUsage(currentMessageUsage, message.event.message.usage)
      }
      if (message.event.type === 'message_delta') {
        currentMessageUsage = updateUsage(currentMessageUsage, message.event.usage)
        if (message.event.delta.stop_reason != null) {
          lastStopReason = message.event.delta.stop_reason
        }
      }
      if (message.event.type === 'message_stop') {
        this.totalUsage = accumulateUsage(this.totalUsage, currentMessageUsage)
      }
      break

    case 'attachment':
      // 附件消息：结构化输出、最大轮次信号等
      if (message.attachment.type === 'structured_output') {
        structuredOutputFromTool = message.attachment.data
      }
      else if (message.attachment.type === 'max_turns_reached') {
        // 生成最大轮次错误结果
        yield { type: 'result', subtype: 'error_max_turns', ... }
        return
      }
      break

    case 'system':
      // 系统消息：压缩边界、API 重试
      if (message.subtype === 'compact_boundary') {
        // 释放预压缩消息以进行 GC
        this.mutableMessages.splice(0, mutableBoundaryIdx)
        yield { type: 'system', subtype: 'compact_boundary', ... }
      }
      if (message.subtype === 'api_error') {
        yield { type: 'system', subtype: 'api_retry', ... }
      }
      break

    case 'tool_use_summary':
      // 工具使用摘要
      yield { type: 'tool_use_summary', ... }
      break
  }
}
```

## 五、ask() 便捷函数

```typescript
/**
 * Sends a single prompt to the Claude API and returns the response.
 * Assumes that claude is being used non-interactively -- will not
 * ask the user for permissions or further input.
 *
 * Convenience wrapper around QueryEngine for one-shot usage.
 */
export async function* ask({
  commands,
  prompt,
  promptUuid,
  isMeta,
  cwd,
  tools,
  mcpClients,
  verbose = false,
  thinkingConfig,
  maxTurns,
  maxBudgetUsd,
  taskBudget,
  canUseTool,
  mutableMessages = [],
  getReadFileCache,
  setReadFileCache,
  customSystemPrompt,
  appendSystemPrompt,
  userSpecifiedModel,
  fallbackModel,
  jsonSchema,
  getAppState,
  setAppState,
  abortController,
  replayUserMessages = false,
  includePartialMessages = false,
  handleElicitation,
  agents = [],
  setSDKStatus,
  orphanedPermission,
}): AsyncGenerator<SDKMessage, void, unknown> {
  const engine = new QueryEngine({...})

  try {
    yield* engine.submitMessage(prompt, { uuid: promptUuid, isMeta })
  } finally {
    setReadFileCache(engine.getReadFileState())
  }
}
```

## 六、query.ts 核心循环

**文件位置**: `src/query.ts` (1700+ 行)

### 6.1 状态定义

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

### 6.2 查询参数

```typescript
export type QueryParams = {
  messages: Message[]
  systemPrompt: SystemPrompt
  userContext: { [k: string]: string }
  systemContext: { [k: string]: string }
  canUseTool: CanUseToolFn
  toolUseContext: ToolUseContext
  fallbackModel?: string
  querySource: QuerySource
  maxOutputTokensOverride?: number
  maxTurns?: number
  skipCacheWrite?: boolean
  taskBudget?: { total: number }
  deps?: QueryDeps
}
```

### 6.3 查询循环核心

```typescript
export async function* query(
  params: QueryParams,
): AsyncGenerator<
  | StreamEvent
  | RequestStartEvent
  | Message
  | TombstoneMessage
  | ToolUseSummaryMessage,
  Terminal
> {
  const consumedCommandUuids: string[] = []
  const terminal = yield* queryLoop(params, consumedCommandUuids)
  // 完成后通知命令生命周期
  for (const uuid of consumedCommandUuids) {
    notifyCommandLifecycle(uuid, 'completed')
  }
  return terminal
}
```

## 七、关键辅助模块

### 7.1 query/config.ts - 查询配置

```typescript
// 快照不可变的环境/Statsig/会话状态
export function buildQueryConfig(): QueryConfig {
  return {
    isAutoCompactEnabled: isAutoCompactEnabled(),
    isReactivelyCompactEnabled: feature('REACTIVE_COMPACT'),
    // ... 更多配置
  }
}
```

### 7.2 query/deps.ts - 依赖注入

```typescript
export type QueryDeps = {
  callClaudeAPI: typeof callClaudeAPI
  runTools: typeof runTools
  // ... 更多依赖
}

export function productionDeps(): QueryDeps {
  return {
    callClaudeAPI,
    runTools,
    // ...
  }
}
```

### 7.3 query/stopHooks.ts - 停止钩子

```typescript
export async function* handleStopHooks(
  toolUseContext: ToolUseContext,
  messages: Message[],
  lastAssistantMessage: AssistantMessage,
): AsyncGenerator<Message, void, unknown> {
  // 执行 PostToolUse 钩子
  // 处理停止条件
}
```

### 7.4 query/tokenBudget.ts - Token 预算

```typescript
export function createBudgetTracker(): BudgetTracker {
  // 追踪 token 使用
  // 检查预算限制
}

export function checkTokenBudget(
  budgetTracker: BudgetTracker | null,
  messages: Message[],
): { shouldContinue: boolean; tokensUsed: number } {
  // 检查是否超出 token 预算
}
```

## 八、错误处理与恢复机制

### 8.1 最大输出 Token 恢复

```typescript
const MAX_OUTPUT_TOKENS_RECOVERY_LIMIT = 3

// 检测 max_output_tokens 错误
function isWithheldMaxOutputTokens(
  msg: Message | StreamEvent | undefined,
): msg is AssistantMessage {
  return msg?.type === 'assistant' && msg.apiError === 'max_output_tokens'
}
```

### 8.2 结构化输出重试

```typescript
// 检查结构化输出重试限制
if (message.type === 'user' && jsonSchema) {
  const currentCalls = countToolCalls(
    this.mutableMessages,
    SYNTHETIC_OUTPUT_TOOL_NAME,
  )
  const callsThisQuery = currentCalls - initialStructuredOutputCalls
  const maxRetries = parseInt(process.env.MAX_STRUCTURED_OUTPUT_RETRIES || '5', 10)
  if (callsThisQuery >= maxRetries) {
    yield { type: 'result', subtype: 'error_max_structured_output_retries', ... }
    return
  }
}
```

### 8.3 预算检查

```typescript
// 检查 USD 预算是否超出
if (maxBudgetUsd !== undefined && getTotalCost() >= maxBudgetUsd) {
  yield {
    type: 'result',
    subtype: 'error_max_budget_usd',
    errors: [`Reached maximum budget ($${maxBudgetUsd})`],
    ...
  }
  return
}
```