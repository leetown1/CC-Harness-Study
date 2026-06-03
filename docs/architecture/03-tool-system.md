# Tool 系统深度解析

本文档详细分析 Claude Code 的工具系统实现，这是 AI 与外部世界交互的核心接口。

## 一、Tool 接口定义

**文件位置**: `src/Tool.ts` (793 行)

### 1.1 核心 Tool 类型

```typescript
export type Tool<
  Input extends AnyObject = AnyObject,
  Output = unknown,
  P extends ToolProgressData = ToolProgressData,
> = {
  // 别名支持（向后兼容）
  aliases?: string[]
  
  // 关键字搜索提示
  searchHint?: string
  
  // 核心方法
  call(
    args: z.infer<Input>,
    context: ToolUseContext,
    canUseTool: CanUseToolFn,
    parentMessage: AssistantMessage,
    onProgress?: ToolCallProgress<P>,
  ): Promise<ToolResult<Output>>
  
  description(
    input: z.infer<Input>,
    options: {
      isNonInteractiveSession: boolean
      toolPermissionContext: ToolPermissionContext
      tools: Tools
    },
  ): Promise<string>
  
  // Schema 定义
  readonly inputSchema: Input
  readonly inputJSONSchema?: ToolInputJSONSchema  // MCP 工具直接使用 JSON Schema
  outputSchema?: z.ZodType<unknown>
  
  // 工具方法
  inputsEquivalent?(a: z.infer<Input>, b: z.infer<Input>): boolean
  isConcurrencySafe(input: z.infer<Input>): boolean
  isEnabled(): boolean
  isReadOnly(input: z.infer<Input>): boolean
  isDestructive?(input: z.infer<Input>): boolean
  
  // 中断行为
  interruptBehavior?(): 'cancel' | 'block'
  
  // 搜索/读取命令检测
  isSearchOrReadCommand?(input: z.infer<Input>): {
    isSearch: boolean
    isRead: boolean
    isList?: boolean
  }
  
  isOpenWorld?(input: z.infer<Input>): boolean
  requiresUserInteraction?(): boolean
  isMcp?: boolean
  isLsp?: boolean
  
  // 延迟加载标记
  readonly shouldDefer?: boolean
  readonly alwaysLoad?: boolean
  
  // MCP 信息
  mcpInfo?: { serverName: string; toolName: string }
  
  // 工具名称和结果限制
  readonly name: string
  maxResultSizeChars: number
  
  // 严格模式
  readonly strict?: boolean
  
  // 输入验证和权限检查
  backfillObservableInput?(input: Record<string, unknown>): void
  validateInput?(
    input: z.infer<Input>,
    context: ToolUseContext,
  ): Promise<ValidationResult>
  checkPermissions(
    input: z.infer<Input>,
    context: ToolUseContext,
  ): Promise<PermissionResult>
  
  // 路径获取
  getPath?(input: z.infer<Input>): string
  
  // 权限匹配器
  preparePermissionMatcher?(
    input: z.infer<Input>,
  ): Promise<(pattern: string) => boolean>
  
  // 提示生成
  prompt(options: {
    getToolPermissionContext: () => Promise<ToolPermissionContext>
    tools: Tools
    agents: AgentDefinition[]
    allowedAgentTypes?: string[]
  }): Promise<string>
  
  // UI 显示
  userFacingName(input: Partial<z.infer<Input>> | undefined): string
  userFacingNameBackgroundColor?(input: Partial<z.infer<Input>> | undefined): keyof Theme | undefined
  isTransparentWrapper?(): boolean
  getToolUseSummary?(input: Partial<z.infer<Input>> | undefined): string | null
  getActivityDescription?(input: Partial<z.infer<Input>> | undefined): string | null
  toAutoClassifierInput(input: z.infer<Input>): unknown
  
  // 结果映射
  mapToolResultToToolResultBlockParam(
    content: Output,
    toolUseID: string,
  ): ToolResultBlockParam
  
  // 渲染方法
  renderToolResultMessage?(...): React.ReactNode
  extractSearchText?(out: Output): string
  renderToolUseMessage(...): React.ReactNode
  isResultTruncated?(output: Output): boolean
  renderToolUseTag?(input: Partial<z.infer<Input>>): React.ReactNode
  renderToolUseProgressMessage?(...): React.ReactNode
  renderToolUseQueuedMessage?(): React.ReactNode
  renderToolUseRejectedMessage?(...): React.ReactNode
  renderToolUseErrorMessage?(...): React.ReactNode
  renderGroupedToolUse?(...): React.ReactNode | null
}
```

### 1.2 Tools 集合类型

```typescript
/**
 * A collection of tools. Use this type instead of `Tool[]` to make it easier
 * to track where tool sets are assembled, passed, and filtered across the codebase.
 */
export type Tools = readonly Tool[]
```

### 1.3 buildTool 工厂函数

```typescript
/**
 * Build a complete `Tool` from a partial definition, filling in safe defaults
 * for the commonly-stubbed methods.
 */
const TOOL_DEFAULTS = {
  isEnabled: () => true,
  isConcurrencySafe: (_input?: unknown) => false,  // 默认不安全
  isReadOnly: (_input?: unknown) => false,          // 默认写入
  isDestructive: (_input?: unknown) => false,
  checkPermissions: (input, _ctx) =>
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

## 二、ToolUseContext 上下文

```typescript
export type ToolUseContext = {
  options: {
    commands: Command[]
    debug: boolean
    mainLoopModel: string
    tools: Tools
    verbose: boolean
    thinkingConfig: ThinkingConfig
    mcpClients: MCPServerConnection[]
    mcpResources: Record<string, ServerResource[]>
    isNonInteractiveSession: boolean
    agentDefinitions: AgentDefinitionsResult
    maxBudgetUsd?: number
    customSystemPrompt?: string
    appendSystemPrompt?: string
    querySource?: QuerySource
    refreshTools?: () => Tools
  }
  abortController: AbortController
  readFileState: FileStateCache
  getAppState(): AppState
  setAppState(f: (prev: AppState) => AppState): void
  setAppStateForTasks?: (f: (prev: AppState) => AppState) => void
  handleElicitation?: (serverName, params, signal) => Promise<ElicitResult>
  setToolJSX?: SetToolJSXFn
  addNotification?: (notif: Notification) => void
  appendSystemMessage?: (msg) => void
  sendOSNotification?: (opts) => void
  nestedMemoryAttachmentTriggers?: Set<string>
  loadedNestedMemoryPaths?: Set<string>
  dynamicSkillDirTriggers?: Set<string>
  discoveredSkillNames?: Set<string>
  userModified?: boolean
  setInProgressToolUseIDs: (f: (prev: Set<string>) => Set<string>) => void
  setHasInterruptibleToolInProgress?: (v: boolean) => void
  setResponseLength: (f: (prev: number) => number) => void
  pushApiMetricsEntry?: (ttftMs: number) => void
  setStreamMode?: (mode: SpinnerMode) => void
  onCompactProgress?: (event: CompactProgressEvent) => void
  setSDKStatus?: (status: SDKStatus) => void
  openMessageSelector?: () => void
  updateFileHistoryState: (updater) => void
  updateAttributionState: (updater) => void
  setConversationId?: (id: UUID) => void
  agentId?: AgentId
  agent_type?: string
  requireCanUseTool?: boolean
  messages: Message[]
  fileReadingLimits?: { maxTokens?: number; maxSizeBytes?: number }
  globLimits?: { maxResults?: number }
  toolDecisions?: Map<string, { source: string; decision: 'accept' | 'reject'; timestamp: number }>
  queryTracking?: QueryChainTracking
  requestPrompt?: (sourceName, toolInputSummary) => (request) => Promise<PromptResponse>
  toolUseId?: string
  criticalSystemReminder_EXPERIMENTAL?: string
  preserveToolUseResults?: boolean
  localDenialTracking?: DenialTrackingState
  contentReplacementState?: ContentReplacementState
  renderedSystemPrompt?: SystemPrompt
}
```

## 三、工具注册与获取

**文件位置**: `src/tools.ts`

### 3.1 getAllBaseTools()

```typescript
/**
 * Get the complete exhaustive list of all tools that could be available
 * in the current environment (respecting process.env flags).
 * This is the source of truth for ALL tools.
 */
export function getAllBaseTools(): Tools {
  return [
    AgentTool,
    TaskOutputTool,
    BashTool,
    ...(hasEmbeddedSearchTools() ? [] : [GlobTool, GrepTool]),
    ExitPlanModeV2Tool,
    FileReadTool,
    FileEditTool,
    FileWriteTool,
    NotebookEditTool,
    WebFetchTool,
    TodoWriteTool,
    WebSearchTool,
    TaskStopTool,
    AskUserQuestionTool,
    SkillTool,
    EnterPlanModeTool,
    ...(process.env.USER_TYPE === 'ant' ? [ConfigTool, TungstenTool] : []),
    ...(SuggestBackgroundPRTool ? [SuggestBackgroundPRTool] : []),
    ...(WebBrowserTool ? [WebBrowserTool] : []),
    ...(isTodoV2Enabled() ? [TaskCreateTool, TaskGetTool, TaskUpdateTool, TaskListTool] : []),
    ...(OverflowTestTool ? [OverflowTestTool] : []),
    ...(CtxInspectTool ? [CtxInspectTool] : []),
    ...(TerminalCaptureTool ? [TerminalCaptureTool] : []),
    ...(isEnvTruthy(process.env.ENABLE_LSP_TOOL) ? [LSPTool] : []),
    ...(isWorktreeModeEnabled() ? [EnterWorktreeTool, ExitWorktreeTool] : []),
    getSendMessageTool(),
    ...(ListPeersTool ? [ListPeersTool] : []),
    ...(isAgentSwarmsEnabled() ? [getTeamCreateTool(), getTeamDeleteTool()] : []),
    ...(VerifyPlanExecutionTool ? [VerifyPlanExecutionTool] : []),
    ...(process.env.USER_TYPE === 'ant' && REPLTool ? [REPLTool] : []),
    ...(WorkflowTool ? [WorkflowTool] : []),
    ...(SleepTool ? [SleepTool] : []),
    ...cronTools,
    ...(RemoteTriggerTool ? [RemoteTriggerTool] : []),
    ...(MonitorTool ? [MonitorTool] : []),
    BriefTool,
    ...(SendUserFileTool ? [SendUserFileTool] : []),
    ...(PushNotificationTool ? [PushNotificationTool] : []),
    ...(SubscribePRTool ? [SubscribePRTool] : []),
    ...(getPowerShellTool() ? [getPowerShellTool()] : []),
    ...(SnipTool ? [SnipTool] : []),
    ...(process.env.NODE_ENV === 'test' ? [TestingPermissionTool] : []),
    ListMcpResourcesTool,
    ReadMcpResourceTool,
    ...(isToolSearchEnabledOptimistic() ? [ToolSearchTool] : []),
  ]
}
```

### 3.2 getTools()

```typescript
export const getTools = (permissionContext: ToolPermissionContext): Tools => {
  // Simple 模式：仅 Bash, Read, Edit
  if (isEnvTruthy(process.env.CLAUDE_CODE_SIMPLE)) {
    if (isReplModeEnabled() && REPLTool) {
      const replSimple: Tool[] = [REPLTool]
      if (feature('COORDINATOR_MODE') && coordinatorModeModule?.isCoordinatorMode()) {
        replSimple.push(TaskStopTool, getSendMessageTool())
      }
      return filterToolsByDenyRules(replSimple, permissionContext)
    }
    const simpleTools: Tool[] = [BashTool, FileReadTool, FileEditTool]
    if (feature('COORDINATOR_MODE') && coordinatorModeModule?.isCoordinatorMode()) {
      simpleTools.push(AgentTool, TaskStopTool, getSendMessageTool())
    }
    return filterToolsByDenyRules(simpleTools, permissionContext)
  }

  // 获取所有基础工具并过滤
  const allTools = getAllBaseTools()
  const enabledTools = allTools.filter(tool => tool.isEnabled())
  
  return filterToolsByDenyRules(enabledTools, permissionContext)
}
```

### 3.3 filterToolsByDenyRules()

```typescript
/**
 * Filters out tools that are blanket-denied by the permission context.
 */
export function filterToolsByDenyRules<
  T extends {
    name: string
    mcpInfo?: { serverName: string; toolName: string }
  },
>(tools: readonly T[], permissionContext: ToolPermissionContext): T[] {
  return tools.filter(tool => !getDenyRuleForTool(permissionContext, tool))
}
```

## 四、工具目录结构

`tools/` 目录包含 149+ 个文件，按工具类型组织：

```
tools/
├── AgentTool/              # 子代理工具
│   ├── AgentTool.ts
│   ├── agentMemory.ts
│   ├── agentDisplay.ts
│   ├── builtInAgents.ts
│   ├── loadAgentsDir.ts
│   ├── runAgent.ts
│   ├── forkSubagent.ts
│   └── built-in/           # 内置代理定义
│       ├── exploreAgent.ts
│       ├── planAgent.ts
│       ├── generalPurposeAgent.ts
│       └── ...
├── BashTool/               # Shell 命令工具
│   ├── BashTool.ts
│   ├── bashPermissions.ts
│   ├── bashSecurity.ts
│   ├── bashCommandHelpers.ts
│   ├── commandSemantics.ts
│   └── ...
├── FileReadTool/           # 文件读取工具
│   ├── FileReadTool.ts
│   ├── imageProcessor.ts
│   └── limits.ts
├── FileEditTool/           # 文件编辑工具
│   ├── FileEditTool.ts
│   ├── utils.ts
│   └── ...
├── FileWriteTool/          # 文件写入工具
├── GlobTool/               # 文件模式匹配工具
├── GrepTool/               # 内容搜索工具
├── WebFetchTool/           # 网页获取工具
├── WebSearchTool/          # 网页搜索工具
├── SkillTool/              # 技能调用工具
├── MCPTool/                # MCP 工具包装器
├── LSPTool/                # LSP 工具
├── TodoWriteTool/          # Todo 写入工具
├── TaskCreateTool/         # 任务创建工具
├── TaskUpdateTool/         # 任务更新工具
├── AskUserQuestionTool/    # 用户提问工具
├── EnterPlanModeTool/      # 进入计划模式
├── ExitPlanModeTool/       # 退出计划模式
├── ToolSearchTool/         # 工具搜索（延迟加载）
├── SyntheticOutputTool/    # 结构化输出工具
├── PowerShellTool/         # PowerShell 工具
└── ...                     # 更多工具
```

## 五、核心工具详解

### 5.1 BashTool

**位置**: `tools/BashTool/BashTool.ts`

Shell 命令执行工具，支持：
- 沙箱模式
- 权限控制
- 破坏性命令警告
- 命令语义分析

```typescript
// BashTool 核心功能
- 沙箱执行（shouldUseSandbox）
- 只读命令验证（readOnlyValidation）
- 破坏性命令检测（destructiveCommandWarning）
- 命令标签解析（commentLabel）
- 路径验证（pathValidation）
```

### 5.2 FileReadTool

**位置**: `tools/FileReadTool/FileReadTool.ts`

文件读取工具，支持：
- 文本文件读取
- 图片处理（imageProcessor）
- 读取限制（limits）

### 5.3 FileEditTool

**位置**: `tools/FileEditTool/FileEditTool.ts`

文件编辑工具，支持：
- 字符串替换（StrReplace）
- 多行编辑
- 差异显示

### 5.4 AgentTool

**位置**: `tools/AgentTool/AgentTool.ts`

子代理工具，支持：
- 内置代理（explore, plan, general-purpose 等）
- 自定义代理加载（loadAgentsDir）
- 代理内存（agentMemory）
- 分离子代理（forkSubagent）

## 六、ToolResult 类型

```typescript
export type ToolResult<T> = {
  data: T
  newMessages?: (
    | UserMessage
    | AssistantMessage
    | AttachmentMessage
    | SystemMessage
  )[]
  // 上下文修改器（仅非并发安全工具）
  contextModifier?: (context: ToolUseContext) => ToolUseContext
  // MCP 协议元数据透传
  mcpMeta?: {
    _meta?: Record<string, unknown>
    structuredContent?: Record<string, unknown>
  }
}
```

## 七、权限检查流程

```
工具调用权限检查流程
┌─────────────────────────────────────────┐
│ 1. validateInput() - 输入验证            │
│    检查参数有效性，不涉及权限             │
└─────────────────────┬───────────────────┘
                      ▼
┌─────────────────────────────────────────┐
│ 2. checkPermissions() - 工具特定权限     │
│    工具自定义的权限逻辑                  │
└─────────────────────┬───────────────────┘
                      ▼
┌─────────────────────────────────────────┐
│ 3. canUseTool() - 通用权限检查           │
│    - AlwaysAllow 规则检查                │
│    - AlwaysDeny 规则检查                 │
│    - 用户交互确认                        │
└─────────────────────┬───────────────────┘
                      ▼
┌─────────────────────────────────────────┐
│ 4. call() - 执行工具                     │
└─────────────────────────────────────────┘
```

## 八、工具预设

```typescript
export const TOOL_PRESETS = ['default'] as const

export function getToolsForDefaultPreset(): string[] {
  const tools = getAllBaseTools()
  const isEnabled = tools.map(tool => tool.isEnabled())
  return tools.filter((_, i) => isEnabled[i]).map(tool => tool.name)
}
```

## 九、工具导出常量

```typescript
// 代理禁用工具列表
export {
  ALL_AGENT_DISALLOWED_TOOLS,
  CUSTOM_AGENT_DISALLOWED_TOOLS,
  ASYNC_AGENT_ALLOWED_TOOLS,
  COORDINATOR_MODE_ALLOWED_TOOLS,
} from './constants/tools.js'

// REPL 专用工具
export { REPL_ONLY_TOOLS } from './tools/REPLTool/constants.js'
```