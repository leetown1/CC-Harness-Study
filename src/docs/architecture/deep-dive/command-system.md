# Command 系统深度技术文档

> 基于逐行代码分析的完整技术文档  
> **探索完成时间**: 2026 年 4 月 1 日  
> **核心文件**: commands.ts (717 行), 66+ 命令模块

---

## 1. Command 系统概述

Claude Code 的 Command 系统是一个高度模块化、可扩展的命令框架，支持三种命令类型：
- **Prompt Commands**: 将命令转换为系统提示词
- **Local Commands**: 本地执行的逻辑命令
- **Local JSX Commands**: 带有交互式 UI 界面的命令

### 1.1 命令目录结构

```
commands/
├── agents/           # 代理管理（6 个状态机模式）
├── mcp/             # MCP 服务器管理
├── memory/          # 内存文件编辑
├── skills/          # 技能管理
├── plugin/          # 插件市场与管理
├── config/          # 配置面板
├── plan/            # 计划模式
├── compact/         # 对话压缩
├── clear/           # 清除对话
├── model/           # 模型选择
├── permissions/     # 权限管理
├── session/         # 会话管理
└── ... (66+ 命令模块)
```

---

## 2. 命令类型层次结构

### 2.1 类型定义（来自 `types/command.ts`）

```typescript
// 命令基础类型
export type CommandBase = {
  availability?: CommandAvailability[]  // 可用的认证环境
  description: string                    // 命令描述
  name: string                          // 命令名称
  aliases?: string[]                    // 别名
  isEnabled?: () => boolean             // 动态启用检查
  isHidden?: boolean                    // 是否隐藏
  argumentHint?: string                 // 参数提示
  immediate?: boolean                   // 立即执行（绕过队列）
  isSensitive?: boolean                 // 参数脱敏
  // ... 更多元数据
}

// 命令联合类型
export type Command = CommandBase &
  (PromptCommand | LocalCommand | LocalJSXCommand)
```

### 2.2 三种命令类型详解

#### 1. PromptCommand

```typescript
type PromptCommand = {
  type: 'prompt'
  progressMessage: string
  contentLength: number
  argNames?: string[]
  allowedTools?: string[]
  model?: string
  source: SettingSource | 'builtin' | 'mcp' | 'plugin' | 'bundled'
  getPromptForCommand(
    args: string,
    context: ToolUseContext,
  ): Promise<ContentBlockParam[]>
}
```

**特点**：
- 将命令内容注入系统提示词
- 支持自定义模型和工具限制
- 支持 Hooks 系统
- 可配置执行上下文（inline/fork）

#### 2. LocalCommand

```typescript
type LocalCommand = {
  type: 'local'
  supportsNonInteractive: boolean
  load: () => Promise<LocalCommandModule>
}

type LocalCommandCall = (
  args: string,
  context: LocalJSXCommandContext,
) => Promise<LocalCommandResult>

type LocalCommandResult =
  | { type: 'text'; value: string }
  | { type: 'compact'; compactionResult: CompactionResult }
  | { type: 'skip' }
```

**特点**：
- 纯逻辑执行，无 UI
- 支持懒加载（load 函数）
- 返回结构化结果

#### 3. LocalJSXCommand

```typescript
type LocalJSXCommand = {
  type: 'local-jsx'
  load: () => Promise<LocalJSXCommandModule>
}

type LocalJSXCommandCall = (
  onDone: LocalJSXCommandOnDone,
  context: ToolUseContext & LocalJSXCommandContext,
  args: string,
) => Promise<React.ReactNode>
```

**特点**：
- 返回 React 组件进行 UI 渲染
- 支持复杂的交互状态管理
- 通过 `onDone` 回调完成命令

---

## 3. 命令注册与发现机制

### 3.1 命令注册模式

每个命令模块遵循统一的注册模式：

```typescript
// 示例：commands/agents/index.ts
import type { Command } from '../../commands.js'

const agents = {
  type: 'local-jsx',
  name: 'agents',
  description: 'Manage agent configurations',
  load: () => import('./agents.js'),
} satisfies Command

export default agents
```

### 3.2 元数据字段说明

| 字段 | 类型 | 说明 | 示例 |
|------|------|------|------|
| `type` | `'prompt' \| 'local' \| 'local-jsx'` | 命令类型 | `'local-jsx'` |
| `name` | `string` | 命令名称 | `'agents'` |
| `description` | `string` | 描述信息 | `'Manage agent configurations'` |
| `aliases` | `string[]` | 别名列表 | `['plugins', 'marketplace']` |
| `argumentHint` | `string` | 参数提示 | `'[enable\|disable [server-name]]'` |
| `immediate` | `boolean` | 立即执行 | `true` (绕过队列) |
| `isEnabled` | `() => boolean` | 启用检查 | `() => !DISABLE_COMPACT` |
| `load` | `() => Promise<Module>` | 懒加载函数 | `() => import('./agents.js')` |

---

## 4. 命令执行流程

### 4.1 通用执行流程

```
用户输入 /command [args]
    ↓
命令解析器识别命令
    ↓
检查命令可用性 (availability)
    ↓
检查命令启用状态 (isEnabled)
    ↓
懒加载命令模块 (load())
    ↓
根据类型执行:
  ├─ prompt: getPromptForCommand() → 注入提示词
  ├─ local: call(args, context) → 返回 LocalCommandResult
  └─ local-jsx: call(onDone, context, args) → 渲染 React 组件
    ↓
执行完成回调 (onDone)
    ↓
显示结果/插入消息
```

### 4.2 LocalJSX 命令执行示例（agents 命令）

```typescript
// commands/agents/agents.tsx
export async function call(
  onDone: LocalJSXCommandOnDone,
  context: ToolUseContext
): Promise<React.ReactNode> {
  const appState = context.getAppState()
  const permissionContext = appState.toolPermissionContext
  const tools = getTools(permissionContext)
  
  // 返回 UI 组件
  return <AgentsMenu tools={tools} onExit={onDone} />
}
```

### 4.3 状态机管理（AgentsMenu 示例）

```typescript
type ModeState =
  | { mode: 'list-agents'; source: SettingSource | 'all' }
  | { mode: 'create-agent' }
  | { mode: 'agent-menu'; agent: AgentDefinition; previousMode: ModeState }
  | { mode: 'view-agent'; agent: AgentDefinition; previousMode: ModeState }
  | { mode: 'edit-agent'; agent: AgentDefinition; previousMode: ModeState }
  | { mode: 'delete-confirm'; agent: AgentDefinition; previousMode: ModeState }

// 状态转换
switch (modeState.mode) {
  case 'list-agents':
    return <AgentsList ... />
  case 'create-agent':
    return <CreateAgentWizard ... />
  case 'agent-menu':
    return <Dialog><Select ... /></Dialog>
  // ...
}
```

---

## 5. 参数解析机制

### 5.1 参数解析模式

#### 1. 简单空格分割

```typescript
// compact 命令示例
const customInstructions = args.trim()

// plan 命令示例
const argList = args.trim().split(/\s+/)
if (argList[0] === 'open') {
  // 打开编辑器
}
```

#### 2. 结构化参数解析

```typescript
// mcp 命令示例
if (args) {
  const parts = args.trim().split(/\s+/)
  
  if (parts[0] === 'no-redirect') {
    return <MCPSettings onComplete={onDone} />
  }
  
  if (parts[0] === 'reconnect' && parts[1]) {
    return <MCPReconnect 
      serverName={parts.slice(1).join(' ')}
      onComplete={onDone} 
    />
  }
  
  if (parts[0] === 'enable' || parts[0] === 'disable') {
    return <MCPToggle
      action={parts[0]}
      target={parts.length > 1 ? parts.slice(1).join(' ') : 'all'}
      onComplete={onDone}
    />
  }
}
```

### 5.2 参数传递链

```
用户输入 → processSlashCommand() → 命令 call() → 组件 props
    ↓
args: string
    ↓
解析为结构化参数
    ↓
传递给 React 组件或逻辑函数
```

---

## 6. UI 组件架构（JSX 命令）

### 6.1 核心 UI 组件

#### 1. Dialog（对话框）

```typescript
<Dialog 
  title="Memory" 
  onCancel={handleCancel} 
  color="remember"
>
  <Box flexDirection="column">
    {/* 内容 */}
  </Box>
</Dialog>
```

#### 2. Select（选择器）

```typescript
<Select 
  options={menuItems}
  onChange={handleMenuSelect}
  onCancel={handleCancel}
/>
```

#### 3. Box & Text（布局组件）

```typescript
<Box flexDirection="column">
  <Text bold>Current Plan</Text>
  <Text dimColor>{planPath}</Text>
  <Box marginTop={1}>
    <Text>{planContent}</Text>
  </Box>
</Box>
```

### 6.2 状态管理模式

#### UseState + Switch 模式

```typescript
const [modeState, setModeState] = useState<ModeState>({
  mode: 'list-agents',
  source: 'all',
})

switch (modeState.mode) {
  case 'list-agents':
    // 渲染列表
  case 'create-agent':
    // 渲染创建向导
  // ...
}
```

#### UseAppState 模式

```typescript
const agentDefinitions = useAppState(s => s.agentDefinitions)
const mcpTools = useAppState(s => s.mcp.tools)
const toolPermissionContext = useAppState(s => s.toolPermissionContext)
const setAppState = useSetAppState()
```

---

## 7. 核心命令模块深度分析

### 7.1 Agents 命令（代理管理）

**文件结构**：
```
commands/agents/
├── index.ts              # 命令注册
├── agents.tsx            # 主入口组件
components/agents/
├── AgentsMenu.tsx        # 主菜单（状态机）
├── AgentsList.tsx        # 代理列表
├── AgentDetail.tsx       # 代理详情
├── AgentEditor.tsx       # 代理编辑器
├── CreateAgentWizard.tsx # 创建向导
└── ... (15+ 组件)
```

**状态机设计**：
```typescript
type ModeState =
  | { mode: 'list-agents' }
  | { mode: 'create-agent' }
  | { mode: 'agent-menu'; agent: AgentDefinition; previousMode: ModeState }
  | { mode: 'view-agent'; agent: AgentDefinition; previousMode: ModeState }
  | { mode: 'edit-agent'; agent: AgentDefinition; previousMode: ModeState }
  | { mode: 'delete-confirm'; agent: AgentDefinition; previousMode: ModeState }
```

**关键函数**：
```typescript
// 代理创建回调
const handleAgentCreated = useCallback((message: string) => {
  setChanges(prev => [...prev, message])
  setModeState({ mode: 'list-agents', source: 'all' })
}, [])

// 代理删除回调
const handleAgentDeleted = useCallback(async (agent: AgentDefinition) => {
  await deleteAgentFromFile(agent)
  setAppState(state => {
    const allAgents = state.agentDefinitions.allAgents.filter(
      a => !(a.agentType === agent.agentType && a.source === agent.source)
    )
    return {
      ...state,
      agentDefinitions: {
        ...state.agentDefinitions,
        allAgents,
        activeAgents: getActiveAgentsFromList(allAgents),
      },
    }
  })
}, [setAppState])
```

### 7.2 MCP 命令（服务器管理）

**功能特性**：
- MCP 服务器启用/禁用
- 服务器重连
- 设置面板

**参数解析**：
```typescript
/mcp enable [server-name]   # 启用服务器
/mcp disable [server-name]  # 禁用服务器
/mcp reconnect <name>       # 重连服务器
/mcp no-redirect            # 绕过重定向
```

**MCPToggle 组件**：
```typescript
function MCPToggle({
  action: 'enable' | 'disable',
  target: string,
  onComplete: (result: string) => void,
}): null {
  const mcpClients = useAppState(s => s.mcp.clients)
  const toggleMcpServer = useMcpToggleEnabled()
  
  useEffect(() => {
    const isEnabling = action === 'enable'
    const clients = mcpClients.filter(c => c.name !== 'ide')
    const toToggle = target === 'all'
      ? clients.filter(c => isEnabling ? c.type === 'disabled' : c.type !== 'disabled')
      : clients.filter(c => c.name === target)
    
    if (toToggle.length === 0) {
      onComplete(target === 'all' 
        ? `All MCP servers are already ${isEnabling ? 'enabled' : 'disabled'}`
        : `MCP server "${target}" not found`)
      return
    }
    
    for (const s of toToggle) {
      toggleMcpServer(s.name)
    }
    
    onComplete(target === 'all'
      ? `${isEnabling ? 'Enabled' : 'Disabled'} ${toToggle.length} MCP server(s)`
      : `MCP server "${target}" ${isEnabling ? 'enabled' : 'disabled'}`)
  }, [action, target, mcpClients, toggleMcpServer, onComplete])
  
  return null
}
```

### 7.3 Memory 命令（内存编辑）

**核心流程**：
```typescript
export const call: LocalJSXCommandCall = async onDone => {
  // 清除缓存并预加载
  clearMemoryFileCaches()
  await getMemoryFiles()
  
  return <MemoryCommand onDone={onDone} />
}

function MemoryCommand({ onDone }) {
  const handleSelectMemoryFile = async (memoryPath: string) => {
    try {
      // 创建目录（如果不存在）
      if (memoryPath.includes(getClaudeConfigHomeDir())) {
        await mkdir(getClaudeConfigHomeDir(), { recursive: true })
      }
      
      // 创建文件（如果不存在）
      try {
        await writeFile(memoryPath, '', { encoding: 'utf8', flag: 'wx' })
      } catch (e) {
        if (getErrnoCode(e) !== 'EEXIST') throw e
      }
      
      // 在编辑器中打开
      await editFileInEditor(memoryPath)
      
      // 编辑器信息
      let editorSource = 'default'
      let editorValue = ''
      if (process.env.VISUAL) {
        editorSource = '$VISUAL'
        editorValue = process.env.VISUAL
      } else if (process.env.EDITOR) {
        editorSource = '$EDITOR'
        editorValue = process.env.EDITOR
      }
      
      onDone(`Opened memory file at ${getRelativeMemoryPath(memoryPath)}\n\n
        ${editorSource !== 'default' 
          ? `Using ${editorSource}="${editorValue}".` 
          : 'To use a different editor, set $EDITOR or $VISUAL'}`, {
        display: 'system',
      })
    } catch (error) {
      logError(error)
      onDone(`Error opening memory file: ${error}`)
    }
  }
  
  return (
    <Dialog title="Memory" onCancel={() => onDone('Cancelled', { display: 'system' })}>
      <Box flexDirection="column">
        <React.Suspense fallback={null}>
          <MemoryFileSelector 
            onSelect={handleSelectMemoryFile}
            onCancel={handleCancel}
          />
        </React.Suspense>
      </Box>
    </Dialog>
  )
}
```

### 7.4 Plan 命令（计划模式）

**模式切换逻辑**：
```typescript
export async function call(
  onDone: LocalJSXCommandOnDone,
  context: LocalJSXCommandContext,
  args: string,
): Promise<React.ReactNode> {
  const { getAppState, setAppState } = context
  const appState = getAppState()
  const currentMode = appState.toolPermissionContext.mode
  
  // 如果不在 plan 模式，启用它
  if (currentMode !== 'plan') {
    handlePlanModeTransition(currentMode, 'plan')
    setAppState(prev => ({
      ...prev,
      toolPermissionContext: applyPermissionUpdate(
        prepareContextForPlanMode(prev.toolPermissionContext),
        { type: 'setMode', mode: 'plan', destination: 'session' }
      ),
    }))
    
    const description = args.trim()
    if (description && description !== 'open') {
      onDone('Enabled plan mode', { shouldQuery: true })
    } else {
      onDone('Enabled plan mode')
    }
    return null
  }
  
  // 已在 plan 模式 - 显示当前计划
  const planContent = getPlan()
  const planPath = getPlanFilePath()
  
  if (!planContent) {
    onDone('Already in plan mode. No plan written yet.')
    return null
  }
  
  // 如果用户输入 "/plan open"，在编辑器中打开
  const argList = args.trim().split(/\s+/)
  if (argList[0] === 'open') {
    const result = await editFileInEditor(planPath)
    if (result.error) {
      onDone(`Failed to open plan in editor: ${result.error}`)
    } else {
      onDone(`Opened plan in editor: ${planPath}`)
    }
    return null
  }
  
  // 显示计划内容
  const editor = getExternalEditor()
  const editorName = editor ? toIDEDisplayName(editor) : undefined
  const display = <PlanDisplay 
    planContent={planContent}
    planPath={planPath}
    editorName={editorName}
  />
  
  const output = await renderToString(display)
  onDone(output)
  return null
}
```

### 7.5 Compact 命令（对话压缩）

**压缩策略**：
1. 尝试 Session Memory 压缩（无自定义指令时）
2. 检查 Reactive 模式
3. 执行 Microcompact（减少 token）
4. 执行完整对话压缩

**核心流程**：
```typescript
export const call: LocalCommandCall = async (args, context) => {
  const { abortController } = context
  let { messages } = context
  
  // 过滤边界后的消息
  messages = getMessagesAfterCompactBoundary(messages)
  
  if (messages.length === 0) {
    throw new Error('No messages to compact')
  }
  
  const customInstructions = args.trim()
  
  try {
    // 1. 尝试 Session Memory 压缩
    if (!customInstructions) {
      const sessionMemoryResult = await trySessionMemoryCompaction(
        messages,
        context.agentId,
      )
      if (sessionMemoryResult) {
        getUserContext.cache.clear?.()
        runPostCompactCleanup()
        markPostCompaction()
        suppressCompactWarning()
        
        return {
          type: 'compact',
          compactionResult: sessionMemoryResult,
          displayText: buildDisplayText(context),
        }
      }
    }
    
    // 2. Reactive 模式检查
    if (reactiveCompact?.isReactiveOnlyMode()) {
      return await compactViaReactive(
        messages,
        context,
        customInstructions,
        reactiveCompact,
      )
    }
    
    // 3. 传统压缩流程
    const microcompactResult = await microcompactMessages(messages, context)
    const messagesForCompact = microcompactResult.messages
    
    const result = await compactConversation(
      messagesForCompact,
      context,
      await getCacheSharingParams(context, messagesForCompact),
      false,
      customInstructions,
      false,
    )
    
    setLastSummarizedMessageId(undefined)
    suppressCompactWarning()
    getUserContext.cache.clear?.()
    runPostCompactCleanup()
    
    return {
      type: 'compact',
      compactionResult: result,
      displayText: buildDisplayText(context, result.userDisplayMessage),
    }
  } catch (error) {
    if (abortController.signal.aborted) {
      throw new Error('Compaction canceled.')
    } else if (hasExactErrorMessage(error, ERROR_MESSAGE_NOT_ENOUGH_MESSAGES)) {
      throw new Error(ERROR_MESSAGE_NOT_ENOUGH_MESSAGES)
    } else if (hasExactErrorMessage(error, ERROR_MESSAGE_INCOMPLETE_RESPONSE)) {
      throw new Error(ERROR_MESSAGE_INCOMPLETE_RESPONSE)
    } else {
      logError(error)
      throw new Error(`Error during compaction: ${error}`)
    }
  }
}
```

---

## 8. 与核心系统的交互

### 8.1 AppState 交互

```typescript
// 读取状态
const appState = context.getAppState()
const agentDefinitions = useAppState(s => s.agentDefinitions)
const mcpTools = useAppState(s => s.mcp.tools)

// 写入状态
const setAppState = useSetAppState()
setAppState(prev => ({
  ...prev,
  toolPermissionContext: applyPermissionUpdate(...),
}))
```

### 8.2 Tool 系统集成

```typescript
const permissionContext = appState.toolPermissionContext
const tools = getTools(permissionContext)
const mergedTools = useMergedTools(tools, mcpTools, toolPermissionContext)
```

### 8.3 权限系统

```typescript
// Plan 模式权限设置
import { prepareContextForPlanMode } from '../../utils/permissions/permissionSetup.js'
import { applyPermissionUpdate } from '../../utils/permissions/PermissionUpdate.js'

setAppState(prev => ({
  ...prev,
  toolPermissionContext: applyPermissionUpdate(
    prepareContextForPlanMode(prev.toolPermissionContext),
    { type: 'setMode', mode: 'plan', destination: 'session' }
  ),
}))
```

### 8.4 Hooks 系统

```typescript
// Pre-compact hooks
const hookResult = await executePreCompactHooks(
  { trigger: 'manual', customInstructions },
  context.abortController.signal,
)

// 合并钩子指令
const mergedInstructions = mergeHookInstructions(
  customInstructions,
  hookResult.newCustomInstructions,
)
```

---

## 9. 权限处理机制

### 9.1 权限上下文

```typescript
type ToolPermissionContext = {
  mode: PermissionMode  // 'plan' | 'default' | ...
  additionalWorkingDirectories: Map<string, ...>
  // ... 其他权限配置
}
```

### 9.2 权限更新流程

```typescript
// 应用权限更新
applyPermissionUpdate(
  baseContext: ToolPermissionContext,
  update: PermissionUpdate,
): ToolPermissionContext

// 示例：Plan 模式切换
const newContext = applyPermissionUpdate(
  prepareContextForPlanMode(prev.toolPermissionContext),
  { type: 'setMode', mode: 'plan', destination: 'session' }
)
```

---

## 10. 设计模式与最佳实践

### 10.1 懒加载模式

```typescript
const command = {
  type: 'local-jsx',
  name: 'example',
  load: () => import('./example.js'),  // 动态导入
}
```

**优势**：
- 减少启动时间
- 按需加载代码
- 降低内存占用

### 10.2 状态机模式

```typescript
type ModeState = 
  | { mode: 'list' }
  | { mode: 'detail'; item: Item }
  | { mode: 'edit'; item: Item; previousMode: ModeState }

switch (modeState.mode) {
  case 'list': ...
  case 'detail': ...
  case 'edit': ...
}
```

**优势**：
- 清晰的状态转换
- 类型安全
- 易于维护

### 10.3 回调完成模式

```typescript
export async function call(
  onDone: LocalJSXCommandOnDone,
  context: ToolUseContext,
): Promise<React.ReactNode> {
  // 执行操作
  await doSomething()
  
  // 完成回调
  onDone('Operation completed', {
    display: 'system',
    shouldQuery: true,
  })
  
  return <Component />
}
```

### 10.4 错误处理模式

```typescript
try {
  await operation()
} catch (error) {
  if (abortController.signal.aborted) {
    throw new Error('Operation canceled.')
  } else if (hasExactErrorMessage(error, KNOWN_ERROR)) {
    throw new Error(KNOWN_ERROR)
  } else {
    logError(error)
    throw new Error(`Operation failed: ${error}`)
  }
}
```

### 10.5 缓存清理模式

```typescript
// 操作后清理
getUserContext.cache.clear?.()
runPostCompactCleanup()
suppressCompactWarning()
```

---

## 11. 命令类型对比表

| 特性 | Prompt | Local | Local-JSX |
|------|--------|-------|-----------|
| UI 界面 | 无 | 无 | React 组件 |
| 返回值 | ContentBlockParam[] | LocalCommandResult | ReactNode |
| 执行上下文 | 系统提示词 | 本地逻辑 | 交互式 UI |
| 懒加载 | ✓ | ✓ | ✓ |
| 参数支持 | ✓ | ✓ | ✓ |
| Hooks 支持 | ✓ | ✓ | ✓ |
| 权限控制 | ✓ | ✓ | ✓ |
| 立即执行 | ✓ | ✓ | ✓ |
| 典型用例 | 技能/工作流 | compact/clear | agents/mcp/config |

---

## 12. 关键 API 总结

### 12.1 命令上下文 API

```typescript
type LocalJSXCommandContext = ToolUseContext & {
  canUseTool?: CanUseToolFn
  setMessages: (updater: (prev: Message[]) => Message[]) => void
  options: {
    dynamicMcpConfig?: Record<string, ScopedMcpServerConfig>
    ideInstallationStatus: IDEExtensionInstallationStatus | null
    theme: ThemeName
  }
  onChangeAPIKey: () => void
  resume?: (sessionId: UUID, log: LogOption, entrypoint: ResumeEntrypoint) => Promise<void>
  // ...
}
```

### 12.2 完成回调 API

```typescript
type LocalJSXCommandOnDone = (
  result?: string,
  options?: {
    display?: CommandResultDisplay  // 'skip' | 'system' | 'user'
    shouldQuery?: boolean           // 是否发送给模型
    metaMessages?: string[]         // 元消息
    nextInput?: string              // 下一个输入
    submitNextInput?: boolean       // 是否提交下一个输入
  },
) => void
```

---

## 13. 性能优化策略

### 13.1 懒加载
- 命令实现延迟加载
- 减少初始启动时间

### 13.2 缓存管理
```typescript
clearMemoryFileCaches()
getUserContext.cache.clear?.()
```

### 13.3 React Compiler
```typescript
import { c as _c } from "react/compiler-runtime"
// 自动 memoization
```

### 13.4 Suspense 边界
```typescript
<React.Suspense fallback={null}>
  <MemoryFileSelector ... />
</React.Suspense>
```

---

## 14. 扩展新命令的最佳实践

### 步骤 1：创建命令模块

```typescript
// commands/my-command/index.ts
import type { Command } from '../../commands.js'

const myCommand = {
  type: 'local-jsx',
  name: 'my-command',
  description: 'Description of what my command does',
  aliases: ['mc'],
  argumentHint: '[options]',
  load: () => import('./my-command.js'),
} satisfies Command

export default myCommand
```

### 步骤 2：实现命令逻辑

```typescript
// commands/my-command/my-command.tsx
export async function call(
  onDone: LocalJSXCommandOnDone,
  context: ToolUseContext,
  args?: string,
): Promise<React.ReactNode> {
  // 解析参数
  const options = args?.trim()
  
  // 执行操作
  await doSomething()
  
  // 完成回调
  onDone('Operation completed', {
    display: 'system',
  })
  
  return <MyComponent />
}
```

---

*文档持续更新中...*
