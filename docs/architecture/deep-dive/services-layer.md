# Services 层深度技术文档

> 基于逐行代码分析的完整技术文档  
> **探索完成时间**: 2026 年 4 月 1 日  
> **核心文件**: services/tools/, services/compact/, services/lsp/ 等 127+ 服务模块

---

## 1. Services 层架构概览

### 1.1 目录结构

```
services/
├── tools/                    # 工具服务层 (4 文件)
│   ├── toolOrchestration.ts  # 工具编排
│   ├── toolExecution.ts      # 工具执行 (1745 行)
│   ├── StreamingToolExecutor.ts # 流式执行器
│   └── toolHooks.ts          # 工具钩子
├── compact/                  # 紧凑服务层 (13 文件)
│   ├── compact.ts            # 对话压缩核心 (1706 行)
│   ├── autoCompact.ts        # 自动压缩
│   ├── microCompact.ts       # 微型压缩
│   ├── apiMicrocompact.ts    # API 微型压缩
│   ├── sessionMemoryCompact.ts # 会话内存压缩
│   ├── prompt.ts             # 压缩提示词
│   ├── grouping.ts           # 消息分组
│   └── postCompactCleanup.ts # 压缩后清理
├── lsp/                      # LSP 服务层 (7 文件)
│   ├── LSPClient.ts          # LSP 客户端 (447 行)
│   ├── manager.ts            # LSP 管理器 (289 行)
│   └── ...
├── analytics/                # 分析服务层
├── oauth/                    # OAuth 服务层
├── SessionMemory/            # 会话内存服务
├── autoDream/                # 自动整合服务
├── api/                      # API 服务层
├── mcp/                      # MCP 服务层
└── plugins/                  # 插件服务层
```

---

## 2. Tools 服务层 - 工具执行系统

### 2.1 工具编排 (toolOrchestration.ts)

**核心职责**: 工具调用的编排与并发控制

**关键函数**:

```typescript
// 主执行器 - 流式处理多个工具调用
async function* runTools(
  toolUseMessages: ToolUseBlock[],
  assistantMessages: AssistantMessage[],
  canUseTool: CanUseToolFn,
  toolUseContext: ToolUseContext,
): AsyncGenerator<MessageUpdate, void>
```

**并发策略**:
- **并发安全工具**: 可批量并行执行 (如 Read 操作)
- **非并发安全工具**: 串行执行 (如写操作)
- **最大并发数**: 通过 `CLAUDE_CODE_MAX_TOOL_USE_CONCURRENCY` 环境变量控制 (默认 10)

**分区算法**:

```typescript
function partitionToolCalls(
  toolUseMessages: ToolUseBlock[],
  toolUseContext: ToolUseContext,
): Batch[] {
  // 将连续的工具调用按并发性分组
  // 每个批次要么全是并发安全工具，要么只有一个非并发工具
}
```

### 2.2 工具执行核心 (toolExecution.ts - 1745 行)

**核心职责**: 单个工具的权限检查、执行、钩子处理

**执行流程**:

```
1. 工具查找与验证
   ↓
2. 输入验证 (Zod Schema)
   ↓
3. PreToolUse Hooks 执行
   ↓
4. 权限检查 (canUseTool)
   ↓
5. 工具实际执行 (tool.call)
   ↓
6. PostToolUse Hooks 执行
   ↓
7. 结果处理与返回
```

**关键机制**:

#### A. 错误分类系统

```typescript
function classifyToolError(error: unknown): string {
  // 遥测安全的错误分类
  // - TelemetrySafeError → telemetryMessage
  // - Node.js fs 错误 → 错误码 (ENOENT, EACCES)
  // - 已知错误类型 → 未混淆的名称
  // - 降级 → "Error"
}
```

#### B. 权限决策 OTel 映射

```typescript
function decisionReasonToOTelSource(
  reason: PermissionDecisionReason,
  behavior: 'allow' | 'deny',
): string {
  // 映射到标准词汇：
  // config, hook, user_permanent, user_temporary, user_reject
}
```

#### C. 钩子系统

**PreToolUse Hooks** (执行于工具调用前):
- 返回类型：`PermissionResult | updatedInput | preventContinuation`
- 可修改输入、阻止执行、提供额外上下文
- 性能监控：超过 2000ms 记录日志

**PostToolUse Hooks** (执行于工具成功后):
- 可修改 MCP 工具输出
- 提供额外上下文
- 性能监控

**PostToolUseFailure Hooks** (执行于工具失败后):
- 处理错误恢复
- 提供错误上下文

#### D. 遥测与日志

**关键事件**:
- `tengu_tool_use_success` - 工具成功执行
- `tengu_tool_use_error` - 工具执行错误
- `tengu_tool_use_cancelled` - 工具被取消
- `tengu_tool_use_progress` - 工具执行进度

**OTel 事件**:
- `tool_decision` - 权限决策
- `tool_result` - 工具结果

#### E. MCP 工具特殊处理

```typescript
// MCP 服务器类型识别
function getMcpServerType(
  toolName: string,
  mcpClients: MCPServerConnection[],
): McpServerType

// MCP 服务器 Base URL 提取
function getMcpServerBaseUrlFromToolName(
  toolName: string,
  mcpClients: MCPServerConnection[],
): string | undefined
```

### 2.3 流式工具执行器 (StreamingToolExecutor.ts - 531 行)

**核心职责**: 流式工具执行器，支持并发控制

**设计模式**: 生产者 - 消费者模式

**关键类**:

```typescript
class StreamingToolExecutor {
  // 工具跟踪
  private tools: TrackedTool[]
  
  // 添加工具到执行队列
  addTool(block: ToolUseBlock, assistantMessage: AssistantMessage): void
  
  // 获取已完成的结果 (非阻塞)
  *getCompletedResults(): Generator<MessageUpdate, void>
  
  // 等待剩余工具完成
  async *getRemainingResults(): AsyncGenerator<MessageUpdate, void>
}
```

**并发控制策略**:

```typescript
private canExecuteTool(isConcurrencySafe: boolean): boolean {
  const executingTools = this.tools.filter(t => t.status === 'executing')
  return (
    executingTools.length === 0 ||
    (isConcurrencySafe && executingTools.every(t => t.isConcurrencySafe))
  )
}
```

**错误传播机制**:
- Bash 工具错误 → 取消所有兄弟工具
- 用户中断 (ESC) → 显示拒绝消息
- 流式回退 → 合成错误消息

**中断行为**:

```typescript
private getToolInterruptBehavior(tool: TrackedTool): 'cancel' | 'block' {
  // 'cancel': 可中断的工具 (如 Bash)
  // 'block': 不可中断的工具 (如文件编辑)
}
```

### 2.4 工具钩子 (toolHooks.ts - 651 行)

**核心职责**: 工具钩子执行系统

**钩子类型**:

#### A. PreToolUse Hooks

```typescript
async function* runPreToolUseHooks(...)
```

**返回值类型**:
- `message` - 显示消息
- `hookPermissionResult` - 权限决策
- `hookUpdatedInput` - 修改输入
- `preventContinuation` - 阻止继续
- `stopReason` - 停止原因
- `additionalContext` - 额外上下文
- `stop` - 停止执行

#### B. PostToolUse Hooks

```typescript
async function* runPostToolUseHooks(...)
```

**特殊功能**:
- 可修改 MCP 工具输出 (`updatedMCPToolOutput`)
- 提供额外上下文
- 阻止后续执行

#### C. PostToolUseFailure Hooks

```typescript
async function* runPostToolUseFailureHooks(...)
```

**权限决策解析**:

```typescript
async function resolveHookPermissionDecision(
  hookPermissionResult: PermissionResult | undefined,
  tool: Tool,
  input: Record<string, unknown>,
  toolUseContext: ToolUseContext,
  canUseTool: CanUseToolFn,
  assistantMessage: AssistantMessage,
  toolUseID: string,
): Promise<{
  decision: PermissionDecision
  input: Record<string, unknown>
}>
```

**关键逻辑**:
1. Hook `allow` 不绕过 settings.json 的 `deny/ask` 规则
2. 需要用户交互的工具 → 调用 `canUseTool`
3. `requireCanUseTool` 标志 → 强制调用 `canUseTool`

---

## 3. Compact 服务层 - 上下文压缩系统

### 3.1 对话压缩核心 (compact.ts - 1706 行)

**核心职责**: 对话上下文压缩与摘要生成

**压缩类型**:

#### A. 完整压缩 (`compactConversation`)
- 摘要化旧消息
- 保留最近对话历史
- 重新注入关键上下文

#### B. 部分压缩 (`partialCompactConversation`)
- `from` 方向：摘要化索引之后的消息，保留之前的
- `up_to` 方向：摘要化索引之前的消息，保留之后的

**关键常量**:

```typescript
export const POST_COMPACT_MAX_FILES_TO_RESTORE = 5      // 最多恢复 5 个文件
export const POST_COMPACT_TOKEN_BUDGET = 50_000         // 压缩后 token 预算
export const POST_COMPACT_MAX_TOKENS_PER_FILE = 5_000   // 每文件最大 token
export const POST_COMPACT_MAX_TOKENS_PER_SKILL = 5_000  // 每技能最大 token
export const POST_COMPACT_SKILLS_TOKEN_BUDGET = 25_000  // 技能总预算
```

**压缩流程**:

```
1. PreCompact Hooks 执行
   ↓
2. 流式压缩摘要 (streamCompactSummary)
   ├─ 2a. Forked Agent 路径 (缓存共享)
   └─ 2b. 流式回退路径
   ↓
3. 存储文件状态
   ↓
4. 清除缓存
   ↓
5. 并行生成附件
   ├─ 文件附件
   ├─ 异步代理附件
   ├─ 计划文件附件
   ├─ 技能附件
   └─ Delta 附件 (工具/MCP/代理)
   ↓
6. SessionStart Hooks 执行
   ↓
7. 创建压缩边界标记
   ↓
8. PostCompact Hooks 执行
   ↓
9. 返回压缩结果
```

**Prompt Too Long 重试机制**:

```typescript
const MAX_PTL_RETRIES = 3
const PTL_RETRY_MARKER = '[earlier conversation truncated for compaction retry]'

function truncateHeadForPTLRetry(
  messages: Message[],
  ptlResponse: AssistantMessage,
): Message[] | null
```

- 丢弃最旧的 API 轮次组
- 每次尝试丢弃 20% 或覆盖 token 差距
- 最多重试 3 次

**缓存共享优化**:

```typescript
const promptCacheSharingEnabled = getFeatureValue_CACHED_MAY_BE_STALE(
  'tengu_compact_cache_prefix',
  true  // 3P 默认启用
)
```

- 使用 Forked Agent 复用主对话的缓存前缀
- 失败时回退到常规流式路径

**流式重试机制**:

```typescript
const MAX_COMPACT_STREAMING_RETRIES = 2

for (let attempt = 1; attempt <= maxAttempts; attempt++) {
  // 重置状态
  // 执行流式请求
  // 失败时等待重试
}
```

**后压缩附件生成**:

```typescript
async function createPostCompactFileAttachments(
  readFileState: Record<string, { content: string; timestamp: number }>,
  toolUseContext: ToolUseContext,
  maxFiles: number,
  preservedMessages: Message[] = [],
): Promise<AttachmentMessage[]>
```

**关键特性**:
- 基于时间选择最近访问的文件
- 跳过已存在于 preservedMessages 中的 Read 结果
- Token 预算约束 (50K 总预算，5K 每文件)

**技能附件**:

```typescript
function createSkillAttachmentIfNeeded(
  agentId?: string,
): AttachmentMessage | null
```

- 仅包含在当前会话中调用的技能
- 按调用时间排序 (最近优先)
- 每技能截断 (5K token)
- 总预算 25K token

### 3.2 自动压缩 (autoCompact.ts - 352 行)

**核心职责**: 自动压缩触发与管理

**关键阈值**:

```typescript
export const AUTOCOMPACT_BUFFER_TOKENS = 13_000
export const WARNING_THRESHOLD_BUFFER_TOKENS = 20_000
export const ERROR_THRESHOLD_BUFFER_TOKENS = 20_000
export const MANUAL_COMPACT_BUFFER_TOKENS = 3_000

const MAX_CONSECUTIVE_AUTOCOMPACT_FAILURES = 3  // 电路断路器
```

**有效上下文窗口**:

```typescript
export function getEffectiveContextWindowSize(model: string): number {
  const reservedTokensForSummary = Math.min(
    getMaxOutputTokensForModel(model),
    MAX_OUTPUT_TOKENS_FOR_SUMMARY,  // 20K
  )
  let contextWindow = getContextWindowForModel(model, getSdkBetas())
  
  // 支持环境变量覆盖
  const autoCompactWindow = process.env.CLAUDE_CODE_AUTO_COMPACT_WINDOW
  if (autoCompactWindow) {
    contextWindow = Math.min(contextWindow, parseInt(autoCompactWindow))
  }
  
  return contextWindow - reservedTokensForSummary
}
```

**自动压缩阈值**:

```typescript
export function getAutoCompactThreshold(model: string): number {
  const effectiveContextWindow = getEffectiveContextWindowSize(model)
  const autocompactThreshold = effectiveContextWindow - AUTOCOMPACT_BUFFER_TOKENS
  
  // 支持环境变量覆盖
  const envPercent = process.env.CLAUDE_AUTOCOMPACT_PCT_OVERRIDE
  if (envPercent) {
    const percentageThreshold = Math.floor(
      effectiveContextWindow * (parseFloat(envPercent) / 100),
    )
    return Math.min(percentageThreshold, autocompactThreshold)
  }
  
  return autocompactThreshold
}
```

**警告状态计算**:

```typescript
export function calculateTokenWarningState(
  tokenUsage: number,
  model: string,
): {
  percentLeft: number
  isAboveWarningThreshold: boolean
  isAboveErrorThreshold: boolean
  isAboveAutoCompactThreshold: boolean
  isAtBlockingLimit: boolean
}
```

**自动压缩启用检查**:

```typescript
export function isAutoCompactEnabled(): boolean {
  if (isEnvTruthy(process.env.DISABLE_COMPACT)) return false
  if (isEnvTruthy(process.env.DISABLE_AUTO_COMPACT)) return false
  
  const userConfig = getGlobalConfig()
  return userConfig.autoCompactEnabled
}
```

**是否应该自动压缩**:

```typescript
export async function shouldAutoCompact(
  messages: Message[],
  model: string,
  querySource?: QuerySource,
  snipTokensFreed = 0,
): Promise<boolean>
```

**递归保护**:
- `session_memory` 或 `compact` 查询源 → 不触发
- `marble_origami` (ctx-agent) → 不触发
- `CONTEXT_COLLAPSE` 启用 → 不触发
- `REACTIVE_COMPACT` 启用 → 不触发

**自动压缩执行**:

```typescript
export async function autoCompactIfNeeded(
  messages: Message[],
  toolUseContext: ToolUseContext,
  cacheSafeParams: CacheSafeParams,
  querySource?: QuerySource,
  tracking?: AutoCompactTrackingState,
  snipTokensFreed?: number,
): Promise<{
  wasCompacted: boolean
  compactionResult?: CompactionResult
  consecutiveFailures?: number
}>
```

**电路断路器模式**:

```typescript
if (
  tracking?.consecutiveFailures !== undefined &&
  tracking.consecutiveFailures >= MAX_CONSECUTIVE_AUTOCOMPACT_FAILURES
) {
  return { wasCompacted: false }  // 跳过连续失败
}
```

**Session Memory 压缩优先**:

```typescript
// 先尝试 Session Memory 压缩
const sessionMemoryResult = await trySessionMemoryCompaction(...)
if (sessionMemoryResult) {
  return { wasCompacted: true, compactionResult: sessionMemoryResult }
}

// 回退到传统压缩
const compactionResult = await compactConversation(...)
```

### 3.3 微压缩 (microCompact.ts - 531 行)

**核心职责**: 微压缩 - 工具结果清理

**压缩策略**:

#### A. 基于时间的触发
- 当距离上次助手消息超过阈值时触发
- 清除除最近 N 个外的所有工具结果
- 直接修改消息内容

#### B. 缓存编辑触发 (Cached MC)
- 使用 cache editing API
- 不修改本地消息内容
- 通过 `cache_edits` 字段删除工具结果

**可压缩工具**:

```typescript
const COMPACTABLE_TOOLS = new Set<string>([
  FILE_READ_TOOL_NAME,
  ...SHELL_TOOL_NAMES,
  GREP_TOOL_NAME,
  GLOB_TOOL_NAME,
  WEB_SEARCH_TOOL_NAME,
  WEB_FETCH_TOOL_NAME,
  FILE_EDIT_TOOL_NAME,
  FILE_WRITE_TOOL_NAME,
])
```

**Token 估算**:

```typescript
function calculateToolResultTokens(block: ToolResultBlockParam): number {
  if (!block.content) return 0
  
  if (typeof block.content === 'string') {
    return roughTokenCountEstimation(block.content)
  }
  
  // 数组内容
  return block.content.reduce((sum, item) => {
    if (item.type === 'text') {
      return sum + roughTokenCountEstimation(item.text)
    } else if (item.type === 'image' || item.type === 'document') {
      return sum + IMAGE_MAX_TOKEN_SIZE  // ~2000 tokens
    }
    return sum
  }, 0)
}
```

**时间触发评估**:

```typescript
export function evaluateTimeBasedTrigger(
  messages: Message[],
  querySource: QuerySource | undefined,
): { gapMinutes: number; config: TimeBasedMCConfig } | null
```

**触发条件**:
1. 配置启用
2. 明确的 main-thread querySource
3. 存在助手消息
4. 间隔超过阈值

**微压缩执行**:

```typescript
export async function microcompactMessages(
  messages: Message[],
  toolUseContext?: ToolUseContext,
  querySource?: QuerySource,
): Promise<MicrocompactResult>
```

**执行顺序**:
1. 时间触发 (优先，短路)
2. 缓存 MC 路径 (如果启用)
3. 无压缩 (回退)

**缓存 MC 状态管理**:

```typescript
// 模块级状态
let cachedMCModule: typeof import('./cachedMicrocompact.js') | null = null
let cachedMCState: import('./cachedMicrocompact.js').CachedMCState | null = null
let pendingCacheEdits: import('./cachedMicrocompact.js').CacheEditsBlock | null = null
```

**关键函数**:
- `consumePendingCacheEdits()` - 获取待处理的缓存编辑
- `getPinnedCacheEdits()` - 获取已固定的缓存编辑
- `pinCacheEdits()` - 固定缓存编辑到特定位置
- `markToolsSentToAPIState()` - 标记工具已发送到 API
- `resetMicrocompactState()` - 重置微压缩状态

### 3.4 API 微压缩 (apiMicrocompact.ts - 154 行)

**核心职责**: API 级上下文管理配置

**上下文编辑策略类型**:

```typescript
type ContextEditStrategy =
  | {
      type: 'clear_tool_uses_20250919'
      trigger?: { type: 'input_tokens'; value: number }
      keep?: { type: 'tool_uses'; value: number }
      clear_tool_inputs?: boolean | string[]
      exclude_tools?: string[]
      clear_at_least?: { type: 'input_tokens'; value: number }
    }
  | {
      type: 'clear_thinking_20251015'
      keep: { type: 'thinking_turns'; value: number } | 'all'
    }
```

**可清除结果的工具**:

```typescript
const TOOLS_CLEARABLE_RESULTS = [
  ...SHELL_TOOL_NAMES,
  GLOB_TOOL_NAME,
  GREP_TOOL_NAME,
  FILE_READ_TOOL_NAME,
  WEB_FETCH_TOOL_NAME,
  WEB_SEARCH_TOOL_NAME,
]
```

**可清除使用的工具**:

```typescript
const TOOLS_CLEARABLE_USES = [
  FILE_EDIT_TOOL_NAME,
  FILE_WRITE_TOOL_NAME,
  NOTEBOOK_EDIT_TOOL_NAME,
]
```

**API 上下文管理配置**:

```typescript
export function getAPIContextManagement(options?: {
  hasThinking?: boolean
  isRedactThinkingActive?: boolean
  clearAllThinking?: boolean
}): ContextManagementConfig | undefined
```

**策略生成**:
1. Thinking 块保留策略 (如果启用)
2. 工具结果清除策略 (如果启用)
3. 工具使用清除策略 (如果启用)

**默认阈值**:

```typescript
const DEFAULT_MAX_INPUT_TOKENS = 180_000  // 典型警告阈值
const DEFAULT_TARGET_INPUT_TOKENS = 40_000  // 保留最后 40K token
```

### 3.5 会话内存压缩 (sessionMemoryCompact.ts - 631 行)

**核心职责**: Session Memory 压缩实验

**配置管理**:

```typescript
export type SessionMemoryCompactConfig = {
  minTokens: number              // 压缩后最小 token 数
  minTextBlockMessages: number   // 最小文本块消息数
  maxTokens: number              // 压缩后最大 token 数 (硬上限)
}

export const DEFAULT_SM_COMPACT_CONFIG: SessionMemoryCompactConfig = {
  minTokens: 10_000,
  minTextBlockMessages: 5,
  maxTokens: 40_000,
}
```

**远程配置初始化**:

```typescript
async function initSessionMemoryCompactConfig(): Promise<void> {
  if (configInitialized) return
  configInitialized = true
  
  const remoteConfig = await getDynamicConfig_BLOCKS_ON_INIT<
    Partial<SessionMemoryCompactConfig>
  >('tengu_sm_compact_config', {})
  
  // 仅使用显式设置的值 (正数)
  // 确保默认值不会被零值覆盖
}
```

**文本块检测**:

```typescript
export function hasTextBlocks(message: Message): boolean {
  // 助手消息：检查 text 类型块
  // 用户消息：检查字符串内容或 text 类型块
}
```

**工具结果 ID 提取**:

```typescript
function getToolResultIds(message: Message): string[] {
  // 从用户消息中提取 tool_result 块的 tool_use_id
}
```

**工具使用检测**:

```typescript
function hasToolUseWithIds(message: Message, toolUseIds: Set<string>): boolean {
  // 检查助手消息是否包含指定 ID 的 tool_use 块
}
```

**API 不变性保护**:

```typescript
export function adjustIndexToPreserveAPIInvariants(
  messages: Message[],
  startIndex: number,
): number
```

**保护场景**:

**A. tool_use/tool_result 配对**:
- 收集保留范围内所有消息的 tool_result ID
- 向后查找匹配的 tool_use 块
- 调整 startIndex 包含所有配对

**B. Thinking 块合并**:
- 收集保留范围内助手消息的 message.id
- 向后查找相同 message.id 的消息
- 确保 thinking 块能正确合并

**消息保留索引计算**:

```typescript
export function calculateMessagesToKeepIndex(
  messages: Message[],
  lastSummarizedIndex: number,
): number
```

**算法**:
1. 从 `lastSummarizedIndex + 1` 开始
2. 计算当前 token 数和文本块消息数
3. 如果已达最大上限 → 返回
4. 如果满足最小要求 → 返回
5. 向后扩展直到满足要求或达到上限
6. 应用 API 不变性保护

**Session Memory 压缩尝试**:

```typescript
export async function trySessionMemoryCompaction(
  messages: Message[],
  agentId?: AgentId,
  autoCompactThreshold?: number,
): Promise<CompactionResult | null>
```

**场景处理**:

**正常情况**:
- `lastSummarizedMessageId` 已设置
- 仅保留该 ID 之后的消息

**恢复会话**:
- `lastSummarizedMessageId` 未设置
- Session Memory 有内容
- 保留所有消息，使用 Session Memory 作为摘要

**压缩结果创建**:

```typescript
function createCompactionResultFromSessionMemory(
  messages: Message[],
  sessionMemory: string,
  messagesToKeep: Message[],
  hookResults: HookResultMessage[],
  transcriptPath: string,
  agentId?: AgentId,
): CompactionResult
```

**特性**:
- Session Memory 截断 (防止占用全部预算)
- 计划文件附件
- 边界标记注释 (保留段信息)

---

## 4. LSP 服务层 - 语言服务器协议

### 4.1 LSP 客户端 (LSPClient.ts - 447 行)

**核心职责**: 与语言服务器的 JSON-RPC 通信

**关键接口**:

```typescript
type LSPClient = {
  readonly capabilities: ServerCapabilities | undefined
  readonly isInitialized: boolean
  start: (command: string, args: string[], options?: {...}) => Promise<void>
  initialize: (params: InitializeParams) => Promise<InitializeResult>
  sendRequest: <TResult>(method: string, params: unknown) => Promise<TResult>
  sendNotification: (method: string, params: unknown) => Promise<void>
  onNotification: (method: string, handler: (params: unknown) => void) => void
  onRequest: <TParams, TResult>(method: string, handler: ...) => void
  stop: () => Promise<void>
}
```

**传输层**: stdio (子进程)

**初始化流程**:
1. 启动子进程
2. 发送 initialize 请求
3. 等待初始化响应
4. 发送 initialized 通知
5. 标记为已初始化

**错误处理**:
- 启动失败：抛出错误
- 崩溃：触发 onCrash 回调
- 请求超时：抛出超时错误

### 4.2 LSP 管理器 (manager.ts - 289 行)

**核心职责**: 全局 LSP 服务器管理

**单例模式**:

```typescript
let lspManagerInstance: LSPServerManager | undefined
let initializationState: InitializationState = 'not-started'
let initializationError: Error | undefined
let initializationGeneration = 0  // 防止陈旧初始化
let initializationPromise: Promise<void> | undefined
```

**初始化状态机**:

```typescript
type InitializationState = 'not-started' | 'pending' | 'success' | 'failed'
```

**代际计数器模式**:

```typescript
const currentGeneration = ++initializationGeneration
initializationPromise = lspManagerInstance
  .initialize()
  .then(() => {
    if (currentGeneration === initializationGeneration) {
      initializationState = 'success'
      registerLSPNotificationHandlers(lspManagerInstance)
    }
  })
  .catch((error: unknown) => {
    if (currentGeneration === initializationGeneration) {
      initializationState = 'failed'
      initializationError = error as Error
      lspManagerInstance = undefined
    }
  })
```

**设计目的**: 防止插件刷新时的陈旧初始化覆盖新初始化

---

## 5. 服务架构图

```
┌─────────────────────────────────────────────────────────────────┐
│                      Services Layer                              │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │
│  │   Tools      │  │   Compact    │  │  Context     │          │
│  │   Service    │  │   Service    │  │  Collapse    │          │
│  │              │  │              │  │              │          │
│  │ • Orchestration│ • Auto Compact│ • Index        │          │
│  │ • Execution  │  │ • Micro      │              │          │
│  │ • Streaming  │  │ • Session Mem│              │          │
│  │ • Hooks      │  │ • Reactive   │              │          │
│  └──────────────┘  └──────────────┘  └──────────────┘          │
│                                                                  │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │
│  │    LSP       │  │  Analytics   │  │    OAuth     │          │
│  │   Service    │  │   Service    │  │   Service    │          │
│  │              │  │              │  │              │          │
│  │ • Client     │  │ • Index      │  │ • Index      │          │
│  │ • Manager    │  │ • Sink       │  │ • Client     │          │
│  │ • Diagnostic │  │ • Datadog    │  │ • Crypto     │          │
│  └──────────────┘  └──────────────┘  └──────────────┘          │
│                                                                  │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │
│  │Session Memory│  │  Auto Dream  │  │    API       │          │
│  │   Service    │  │   Service    │  │   Service    │          │
│  │              │  │              │  │              │          │
│  │ • Session Mem│  │ • Auto Dream │  │ • Claude     │          │
│  │ • Prompts    │  │ • Config     │  │ • Errors     │          │
│  │ • Utils      │  │ • Consolidate│  │ • Retry      │          │
│  └──────────────┘  └──────────────┘  └──────────────┘          │
│                                                                  │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │
│  │    MCP       │  │   Plugins    │  │   Remote     │          │
│  │   Service    │  │   Service    │  │   Settings   │          │
│  │              │  │              │  │              │          │
│  │ • Client     │  │ • Plugin     │  │ • Index      │          │
│  │ • Config     │  │   Install    │  │ • Security   │          │
│  │ • OAuth      │  │ • Operations │  │ • SyncCache  │          │
│  │ • Elicitation│  │              │  │              │          │
│  └──────────────┘  └──────────────┘  └──────────────┘          │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## 6. 依赖关系图

```
Tools Service
├── Tool Execution
│   ├── Permission System
│   ├── Hooks System
│   ├── Analytics
│   ├── MCP Client
│   └── Telemetry
├── Tool Orchestration
│   └── Concurrency Control
└── Streaming Executor
    └── Queue Management

Compact Service
├── Auto Compact
│   ├── Session Memory
│   ├── Traditional Compact
│   └── Post Compact Cleanup
├── Micro Compact
│   ├── Time-based Trigger
│   ├── Cache Editing
│   └── Token Estimation
└── Compact Core
    ├── Streaming Summary
    ├── Attachment Generation
    └── Hook Integration
```

---

## 7. 性能优化机制

### 7.1 Token 管理

**压缩后文件恢复**:

```typescript
POST_COMPACT_MAX_FILES_TO_RESTORE = 5
POST_COMPACT_TOKEN_BUDGET = 50_000
POST_COMPACT_MAX_TOKENS_PER_FILE = 5_000
```

**技能内容保留**:

```typescript
POST_COMPACT_MAX_TOKENS_PER_SKILL = 5_000
POST_COMPACT_SKILLS_TOKEN_BUDGET = 25_000

// 按调用时间排序，保留最近的技能
const skills = Array.from(invokedSkills.values())
  .sort((a, b) => b.invokedAt - a.invokedAt)
```

### 7.2 缓存优化

**Prompt 缓存共享**:

```typescript
const promptCacheSharingEnabled = getFeatureValue_CACHED_MAY_BE_STALE(
  'tengu_compact_cache_prefix',
  true
)

if (promptCacheSharingEnabled) {
  // 使用 forked agent 复用主对话的缓存前缀
  const result = await runForkedAgent({...})
}
```

**微压缩缓存状态**:

```typescript
// 缓存 MC 状态（仅 ant）
let cachedMCState: CachedMCState | null = null
let pendingCacheEdits: CacheEditsBlock | null = null

function pinCacheEdits(userMessageIndex: number, block: CacheEditsBlock) {
  cachedMCState.pinnedEdits.push({ userMessageIndex, block })
}
```

### 7.3 并发控制

**工具并发**:

```typescript
function getMaxToolUseConcurrency(): number {
  return parseInt(process.env.CLAUDE_CODE_MAX_TOOL_USE_CONCURRENCY || '', 10) || 10
}
```

**LSP 服务器并发启动**:

```typescript
// 并行加载所有插件的 LSP 服务器
const results = await Promise.all(
  plugins.map(async plugin => {
    const scopedServers = await getPluginLspServers(plugin, errors)
    return { plugin, scopedServers, errors }
  })
)
```

---

## 8. 错误处理策略

### 8.1 分层错误处理

**工具执行错误**:
1. **输入验证错误**: Zod schema 验证失败
2. **权限错误**: canUseTool 拒绝
3. **执行错误**: tool.call() 抛出
4. **Hook 错误**: Pre/PostToolUse hooks 失败

**LSP 错误**:
1. **启动错误**: spawn 失败、初始化超时
2. **运行时错误**: 请求失败、连接关闭
3. **崩溃错误**: 进程非零退出

### 8.2 错误传播机制

**工具错误传播**:

```typescript
// Bash 工具错误会取消兄弟工具
if (tool.block.name === BASH_TOOL_NAME) {
  this.hasErrored = true
  this.erroredToolDescription = this.getToolDescription(tool)
  this.siblingAbortController.abort('sibling_error')
}
```

**LSP 崩溃传播**:

```typescript
const client = createLSPClient(name, error => {
  state = 'error'
  lastError = error
  crashRecoveryCount++
  // onCrash 回调传播到管理器
})
```

---

## 9. 监控和遥测

### 9.1 事件日志

**工具执行事件**:
- `tengu_tool_use_success` - 成功执行
- `tengu_tool_use_error` - 执行错误
- `tengu_tool_use_cancelled` - 取消
- `tengu_post_tool_hook_error` - Hook 错误

**压缩事件**:
- `tengu_compact` - 压缩完成
- `tengu_cached_microcompact` - 缓存微压缩
- `tengu_time_based_microcompact` - 时间微压缩
- `tengu_sm_compact` - 会话内存压缩

**LSP 事件**:
- 诊断失败跟踪
- 注册错误聚合
- 崩溃恢复计数

### 9.2 性能指标

**工具性能**:

```typescript
// Hook 执行时间
const preToolHookDurationMs = Date.now() - preToolHookStart
getStatsStore()?.observe('pre_tool_hook_duration_ms', preToolHookDurationMs)

// 慢 Hook 警告
if (preToolHookDurationMs >= SLOW_PHASE_LOG_THRESHOLD_MS) {
  logForDebugging(`Slow PreToolUse hooks: ${duration}ms`)
}
```

**压缩性能**:

```typescript
logEvent('tengu_compact', {
  preCompactTokenCount,
  postCompactTokenCount,
  truePostCompactTokenCount,
  compactionInputTokens,
  compactionOutputTokens,
  compactionCacheReadTokens,
  compactionCacheCreationTokens,
})
```

---

## 10. 配置系统

### 10.1 环境变量配置

```typescript
// 工具并发
CLAUDE_CODE_MAX_TOOL_USE_CONCURRENCY

// 自动压缩
CLAUDE_CODE_AUTO_COMPACT_WINDOW
CLAUDE_AUTOCOMPACT_PCT_OVERRIDE
CLAUDE_CODE_BLOCKING_LIMIT_OVERRIDE

// 微压缩
USE_API_CLEAR_TOOL_RESULTS
USE_API_CLEAR_TOOL_USES
API_MAX_INPUT_TOKENS
API_TARGET_INPUT_TOKENS

// 功能开关
DISABLE_COMPACT
DISABLE_AUTO_COMPACT
ENABLE_CLAUDE_CODE_SM_COMPACT
```

### 10.2 GrowthBook 配置

```typescript
// 时间微压缩配置
TimeBasedMCConfig = {
  enabled: boolean
  gapThresholdMinutes: number  // 60 分钟
  keepRecent: number  // 保留最近 N 个
}

// 会话内存压缩配置
SessionMemoryCompactConfig = {
  minTokens: number
  minTextBlockMessages: number
  maxTokens: number
}

// 缓存微压缩配置
CachedMCConfig = {
  triggerThreshold: number
  keepRecent: number
}
```

---

## 11. 总结

### 核心服务模块

- **Tools 服务**: 工具编排、执行、钩子、流式处理
- **Compact 服务**: 自动压缩、微压缩、会话内存压缩
- **LSP 服务**: 语言服务器客户端、管理器、诊断
- **Analytics 服务**: 事件日志、Datadog 集成
- **OAuth 服务**: OAuth 认证、Token 管理
- **SessionMemory 服务**: 会话内存自动提取
- **API 服务**: API 客户端、重试逻辑
- **MCP 服务**: MCP 客户端、配置、OAuth
- **Plugins 服务**: 插件安装、管理

### 关键设计模式

1. **工厂函数模式**: LSP 客户端使用工厂函数而非类
2. **生成器模式**: 工具执行使用生成器进行流式处理
3. **策略模式**: 压缩策略可插拔
4. **状态机模式**: LSP 服务器状态管理
5. **电路断路器模式**: 自动压缩连续失败保护

### 性能优化

- Token 预算管理
- Prompt 缓存共享
- 并发控制
- 懒加载
- 批处理

---

*文档持续更新中...*
