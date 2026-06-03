# Tool 系统深度技术文档

> 基于逐行代码分析的完整技术文档  
> **探索完成时间**: 2026 年 4 月 1 日  
> **核心文件**: Tool.ts (793 行), tools.ts (389 行), services/tools/

---

## 1. Tool 系统概述

Tool 系统是 Claude Code 执行外部操作的核心机制，提供 153+ 个工具实现，涵盖文件操作、shell 执行、网络请求、任务管理等功能。

### 1.1 设计原则

- **类型安全**: 泛型接口 `Tool<Input, Output, Progress>`
- **Zod 验证**: 所有输入使用 Zod schema 运行时验证
- **进度跟踪**: 可选泛型进度类型用于流式更新
- **上下文注入**: 工具接收丰富的 `ToolUseContext`
- **工厂模式**: `buildTool()` 提供 sensible defaults

---

## 2. Tool 接口定义

### 2.1 完整接口

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
  
  // Schema & 验证
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

### 2.2 buildTool 工厂

```typescript
const TOOL_DEFAULTS = {
  isEnabled: () => true,
  isConcurrencySafe: (_input?: unknown) => false,
  isReadOnly: (_input?: unknown) => false,
  isDestructive: (_input?: unknown) => false,
  checkPermissions: (input) => Promise.resolve({ behavior: 'allow', updatedInput: input }),
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
- **类型安全**: `BuiltTool<D>` 确保所有可默认方法都存在
- **DRY 原则**: 60+ 工具共享通用默认值

---

## 3. 工具注册与发现

### 3.1 工具组装

```typescript
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
    // ... 40+ 更多条件工具
  ]
}
```

### 3.2 权限过滤

```typescript
export function filterToolsByDenyRules<T>(
  tools: readonly T[],
  permissionContext: ToolPermissionContext
): T[] {
  return tools.filter(tool => !getDenyRuleForTool(permissionContext, tool))
}
```

**过滤管道**：
1. 获取所有基础工具
2. 按拒绝规则过滤（工具级阻止）
3. 按 `isEnabled()` 检查过滤
4. 与 MCP 工具合并
5. 按工具名称去重（内置优先）

---

## 4. 工具执行流程

### 4.1 单工具执行管道

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

### 4.2 并行工具执行

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

---

## 5. 权限系统架构

### 5.1 权限模式层次

```typescript
export type PermissionMode =
  | 'acceptEdits'      // 自动批准安全工作区文件编辑
  | 'bypassPermissions' // 自动批准所有（安全检查除外）
  | 'default'          // 询问所有
  | 'dontAsk'          // 自动拒绝所有
  | 'plan'             // 只读模式
  | 'auto'             // AI 分类器决策
  | 'bubble'           // 将提示冒泡到父终端
```

### 5.2 权限决策管道

**逐步决策树**：

```
步骤 1a: 检查工具级拒绝规则 → 拒绝
步骤 1b: 检查工具级询问规则 → 询问
步骤 1c: 运行 tool.checkPermissions() → 工具特定逻辑
步骤 1d: 检查工具实现拒绝
步骤 1e: 检查 requiresUserInteraction() → 询问（bypass 免疫）
步骤 1f: 检查内容特定询问规则 → 询问（bypass 免疫）
步骤 1g: 检查安全检查 (.git/, .claude/, shell configs) → 询问（bypass 免疫）
步骤 2a: 检查 bypassPermissions 模式 → 允许
步骤 2b: 检查工具级允许规则 → 允许
步骤 3: 默认 → 询问

自动模式特殊路径：
  ↓ (如果 mode === 'auto' && behavior === 'ask')
  → 检查 acceptEdits 快速路径
  → 检查安全工具允许列表
  → 运行 YOLO 分类器
  → 返回分类器决策
```

---

## 6. 关键工具实现

### 6.1 FileReadTool

**特殊功能**：
- **去重**: 检测未更改文件的重新读取
- **Token 预算**: 压缩图片以适应 token 限制
- **PDF 提取**: 将大 PDF 拆分为页面图片
- **技能发现**: 从文件路径激活技能

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
  
  // 文本文件读取
  const { content, lineCount, totalLines, mtimeMs } = await readFileInRange(
    resolvedFilePath, lineOffset, limit, maxSizeBytes
  )
  
  // 更新缓存
  readFileState.set(fullFilePath, { content, timestamp: mtimeMs, offset, limit })
  
  return { data: { type: 'text', file: { filePath, content, ... } } }
}
```

### 6.2 FileEditTool

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

### 6.3 AgentTool

**子代理生命周期**：

```typescript
async function* runAgent({ agentDefinition, promptMessages, toolUseContext }) {
  // 1. 初始化代理特定 MCP 服务器
  const { clients: mergedMcpClients, tools: agentMcpTools } = 
    await initializeAgentMcpServers(agentDefinition, parentClients)
  
  // 2. 解析代理工具
  const resolvedTools = resolveAgentTools(agentDefinition, availableTools, isAsync)
  
  // 3. 构建代理系统提示
  const agentSystemPrompt = await getAgentSystemPrompt(
    agentDefinition, resolvedAgentModel, resolvedTools
  )
  
  // 4. 创建隔离上下文
  const agentToolUseContext = createSubagentContext(toolUseContext, {
    options: { tools: allTools, isNonInteractiveSession: isAsync },
    agentId,
    agentType: agentDefinition.agentType,
    messages: initialMessages,
    readFileState: agentReadFileState, // 克隆或全新缓存
  })
  
  // 5. 运行查询循环
  for await (const message of query({
    messages: initialMessages,
    systemPrompt: agentSystemPrompt,
    toolUseContext: agentToolUseContext,
  })) {
    yield message
  }
  
  // 6. 清理
  await mcpCleanup()
  clearSessionHooks(rootSetAppState, agentId)
  killShellTasksForAgent(agentId, ...)
}
```

---

## 7. 错误处理

### 7.1 错误分类

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

### 7.2 合成错误生成

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

## 8. 上下文与状态管理

### 8.1 ToolUseContext 结构

```typescript
export type ToolUseContext = {
  options: {
    commands: Command[]
    tools: Tools
    mcpClients: MCPServerConnection[]
    mcpResources: Record<string, ServerResource[]>
    isNonInteractiveSession: boolean
    verbose: boolean
    thinkingConfig: ThinkingConfig
    // ...
  }
  abortController: AbortController
  readFileState: FileStateCache // LRU 文件读取缓存
  getAppState(): AppState
  setAppState(f: (prev: AppState) => AppState): void
  setAppStateForTasks?: (f: (prev: AppState) => AppState) => void // 根存储通道
  setInProgressToolUseIDs: (f: (prev: Set<string>) => Set<string>) => void
  updateFileHistoryState: (f: (prev: FileHistoryState) => FileHistoryState) => void
  agentId?: AgentId
  agentType?: string
  localDenialTracking?: DenialTrackingState // 用于异步子代理
  contentReplacementState?: ContentReplacementState
  renderedSystemPrompt?: SystemPrompt // 在 turn 开始时冻结（分叉子代理）
  // ... 30+ 更多属性
}
```

### 8.2 文件状态缓存

**LRU 缓存用于陈旧检测**：

```typescript
class FileStateCache {
  private cache = new Map<string, {
    content: string
    timestamp: number // mtimeMs
    offset?: number
    limit?: number
    isPartialView?: boolean
  }>()
  
  get(filePath: string): FileState | undefined {
    // LRU 访问模式
  }
  
  set(filePath: string, state: FileState): void {
    // 如果超过大小限制则驱逐最旧的
  }
  
  clear(): void {
    // 在代理清理时释放内存
  }
}
```

**使用模式**：

```typescript
// FileEditTool 针对缓存验证
const lastRead = readFileState.get(absoluteFilePath)
if (lastWriteTime > lastRead.timestamp && content !== lastRead.content) {
  throw new Error(FILE_UNEXPECTEDLY_MODIFIED_ERROR)
}

// FileReadTool 更新缓存
readFileState.set(fullFilePath, {
  content,
  timestamp: mtimeMs,
  offset,
  limit,
})
```

---

## 9. 高级功能

### 9.1 工具结果持久化

**20KB 阈值**：

```typescript
export async function processToolResultBlock(
  tool: Tool,
  result: unknown,
  toolUseID: string,
): Promise<ToolResultBlockParam> {
  const mappedBlock = tool.mapToolResultToToolResultBlockParam(result, toolUseID)
  const content = mappedBlock.content
  
  const resultSizeBytes = typeof content === 'string'
    ? content.length
    : jsonStringify(content).length
  
  if (resultSizeBytes > tool.maxResultSizeChars) {
    // 持久化到磁盘，返回预览
    const filePath = await persistToolResultToDisk(toolUseID, content)
    return {
      tool_use_id: toolUseID,
      type: 'tool_result',
      content: `Tool result persisted to ${filePath} (${formatFileSize(resultSizeBytes)})`,
    }
  }
  
  return mappedBlock
}
```

### 9.2 自动模式分类器

**两阶段分类**：

```typescript
async function classifyYoloAction(messages, action, tools, permissionContext, signal) {
  // 阶段 1: 快速分类（廉价模型）
  const stage1Result = await callClassifier(messages, action, 'fast-model')
  
  if (stage1Result.confidence === 'high') {
    return stage1Result
  }
  
  // 阶段 2: 深度思考（昂贵模型）
  const stage2Result = await callClassifier(messages, action, 'thinking-model')
  
  return stage2Result
}
```

**拒绝追踪**：

```typescript
const DENIAL_LIMITS = {
  maxConsecutive: 5,
  maxTotal: 20,
}

function recordDenial(state: DenialTrackingState): DenialTrackingState {
  return {
    consecutiveDenials: state.consecutiveDenials + 1,
    totalDenials: state.totalDenials + 1,
  }
}

function shouldFallbackToPrompting(state: DenialTrackingState): boolean {
  return (
    state.consecutiveDenials >= DENIAL_LIMITS.maxConsecutive ||
    state.totalDenials >= DENIAL_LIMITS.maxTotal
  )
}
```

---

## 10. 性能优化

### 10.1 Prompt 缓存优化

**分叉子代理策略**：
- 字节相同的 API 请求前缀
- 只有最终指令文本块不同
- 共享 `renderedSystemPrompt`（在 turn 开始时冻结）
- 相同的工具定义（父级的确切池）

**读取去重**：
- 检测未更改文件的重新读取
- 返回存根而不是完整内容
- 节省约 2.64% 的舰队 cache_creation tokens

### 10.2 并发工具执行

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

---

## 11. 安全功能

### 11.1 UNC 路径保护

```typescript
// FileReadTool.ts
if (fullFilePath.startsWith('\\\\') || fullFilePath.startsWith('//')) {
  return { result: true } // 跳过 stat() 以防止 NTLM 凭据泄漏
}
```

### 11.2 设备文件阻止

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

### 11.3 团队内存秘密保护

```typescript
// FileEditTool.ts
const secretError = checkTeamMemSecrets(fullFilePath, new_string)
if (secretError) {
  return { result: false, message: secretError, errorCode: 0 }
}
```

---

## 12. 遥测与分析

### 12.1 工具执行指标

```typescript
logEvent('tengu_tool_use_success', {
  toolName: sanitizeToolNameForAnalytics(tool.name),
  durationMs,
  preToolHookDurationMs,
  toolResultSizeBytes,
  fileExtension,
  mcpServerType,
  mcpServerBaseUrl,
  queryChainId,
  queryDepth,
})
```

### 12.2 OTel 事件

```typescript
void logOTelEvent('tool_result', {
  tool_name: sanitizeToolNameForAnalytics(tool.name),
  success: 'true' | 'false',
  duration_ms: String(durationMs),
  tool_parameters: jsonStringify(toolParameters),
  tool_input: telemetryToolInput,
  decision_source: decisionInfo.source,
  decision_type: decisionInfo.decision,
  mcp_server_scope: mcpServerScope,
})
```

---

*文档持续更新中...*
