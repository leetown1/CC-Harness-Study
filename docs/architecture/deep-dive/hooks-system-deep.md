# Hooks 系统深度技术文档

> 基于逐行代码分析的完整技术文档  
> **探索完成时间**: 2026 年 4 月 1 日  
> **核心文件**: hooks/ 目录下 141 个 Hook 文件

---

## 1. Hooks 系统架构概览

### 1.1 Hook 分类索引

| 分类 | Hook 数量 | 核心职责 |
|------|----------|---------|
| **状态管理** | 15+ | useSettings, useDynamicConfig, useMemoryUsage |
| **工具执行** | 10+ | useCanUseTool, useMergedTools, useCancelRequest |
| **权限** | 8+ | usePermission, usePermissionContext |
| **通知** | 5+ | useNotifications, useNotification |
| **输入** | 12+ | useTextInput, useVimInput, useSearchInput |
| **UI** | 20+ | useTerminalSize, useBlink, useDoublePress |
| **历史** | 8+ | useHistorySearch, useHistoryNavigation |
| **虚拟滚动** | 5+ | useVirtualScroll, useMeasureItem |
| **消息日志** | 3+ | useLogMessages, useRecordTranscript |
| **退出处理** | 4+ | useExitOnCtrlCD, useExitOnCtrlCDWithKeybindings |
| **命令队列** | 3+ | useCommandQueue, useQueuedCommand |
| **其他** | 50+ | 各种专用 Hook |

### 1.2 核心设计模式

1. **useSyncExternalStore**: 高效外部状态订阅
2. **useCallback + useEffectEvent**: 事件处理器优化
3. **useMemo**: 计算结果缓存
4. **useRef**: 可变状态追踪
5. **useState**: 本地状态管理
6. **useEffect**: 副作用处理
7. **useLayoutEffect**: 同步布局更新

---

## 2. 状态管理 Hooks

### 2.1 useSettings

**文件**: `hooks/useSettings.ts`

**职责**: 从 AppState 中读取当前设置的 React Hook

**接口**:
```typescript
export function useSettings(): ReadonlySettings
```

**返回值类型**:
```typescript
export type ReadonlySettings = AppState['settings']
```

**实现机制**:
- 使用 `useAppState` 选择器模式访问 `s.settings`
- 设置通过 `settingsChangeDetector` 监听磁盘文件变化自动更新
- 返回 DeepImmutable 包装的设置对象

**使用示例**:
```typescript
const settings = useSettings()
// settings.theme, settings.model, etc.
```

### 2.2 useSettingsChange

**文件**: `hooks/useSettingsChange.ts`

**职责**: 监听设置变化并触发回调

**接口**:
```typescript
export function useSettingsChange(
  onChange: (source: SettingSource, settings: SettingsJson) => void,
): void
```

**参数**:
- `onChange`: 回调函数，接收变化来源和新的设置对象

**内部机制**:
1. 使用 `useCallback` 包装 `handleChange` 避免重复订阅
2. 通过 `settingsChangeDetector.subscribe()` 注册监听器
3. 变化发生时调用 `getSettings_DEPRECATED()` 读取新设置
4. **重要**: 缓存已由 notifier 重置，此处不再重置以避免 N 路抖动

**副作用处理**:
```typescript
useEffect(() => {
  const unsubscribe = settingsChangeDetector.subscribe(handleChange)
  return unsubscribe
}, [handleChange])
```

### 2.3 useDynamicConfig

**文件**: `hooks/useDynamicConfig.ts`

**职责**: 动态配置值的 React Hook，支持异步加载

**接口**:
```typescript
export function useDynamicConfig<T>(
  configName: string, 
  defaultValue: T
): T
```

**参数**:
- `configName`: 配置项名称
- `defaultValue`: 默认值（初始返回，配置加载后更新）

**实现机制**:
```typescript
export function useDynamicConfig<T>(configName: string, defaultValue: T): T {
  const [configValue, setConfigValue] = React.useState<T>(defaultValue)

  React.useEffect(() => {
    if (process.env.NODE_ENV === 'test') {
      return  // 防止测试挂起
    }
    void getDynamicConfig_BLOCKS_ON_INIT<T>(configName, defaultValue).then(
      setConfigValue,
    )
  }, [configName, defaultValue])

  return configValue
}
```

### 2.4 useMemoryUsage

**文件**: `hooks/useMemoryUsage.ts`

**职责**: 监控 Node.js 进程内存使用情况

**接口**:
```typescript
export function useMemoryUsage(): MemoryUsageInfo | null
```

**返回类型**:
```typescript
export type MemoryUsageInfo = {
  heapUsed: number
  status: MemoryUsageStatus  // 'normal' | 'high' | 'critical'
}
```

**阈值常量**:
```typescript
const HIGH_MEMORY_THRESHOLD = 1.5 * 1024 * 1024 * 1024  // 1.5GB
const CRITICAL_MEMORY_THRESHOLD = 2.5 * 1024 * 1024 * 1024  // 2.5GB
```

**实现机制**:
1. 使用 `useState` 存储内存使用信息
2. 通过 `useInterval` 每 10 秒轮询一次
3. 状态为 'normal' 时返回 `null`（避免不必要的重渲染）
4. 仅当状态变化时才更新（避免 99% 用户的无效渲染）

**关键优化**:
```typescript
setMemoryUsage(prev => {
  // 状态为'normal'时不更新，避免整个 Notifications 子树每 10 秒重渲染
  if (status === 'normal') return prev === null ? prev : null
  return { heapUsed, status }
})
```

### 2.5 useElapsedTime

**文件**: `hooks/useElapsedTime.ts`

**职责**: 返回格式化后的经过时间

**接口**:
```typescript
export function useElapsedTime(
  startTime: number,      // Unix 时间戳（毫秒）
  isRunning: boolean,     // 是否主动更新计时器
  ms: number = 1000,      // 更新间隔
  pausedMs: number = 0,   // 暂停的总时长
  endTime?: number,       // 结束时间（冻结时长）
): string
```

**实现机制**:
1. 使用 `useSyncExternalStore` 实现高效的外部状态订阅
2. `get` 函数计算格式化时长：`formatDuration(Math.max(0, (endTime ?? Date.now()) - startTime - pausedMs))`
3. `subscribe` 函数根据 `isRunning` 决定是否创建定时器
4. 支持通过 `endTime` 冻结时长（用于查看已完成任务）

**关键代码**:
```typescript
const subscribe = useCallback(
  (notify: () => void) => {
    if (!isRunning) return () => {}
    const interval = setInterval(notify, ms)
    return () => clearInterval(interval)
  },
  [isRunning, ms],
)

return useSyncExternalStore(subscribe, get, get)
```

---

## 3. 工具执行相关 Hooks

### 3.1 useCanUseTool

**文件**: `hooks/useCanUseTool.tsx`

**职责**: 核心工具权限检查 Hook，决定工具是否可以执行

**接口**:
```typescript
type CanUseToolFn<Input extends Record<string, unknown>> = (
  tool: ToolType,
  input: Input,
  toolUseContext: ToolUseContext,
  assistantMessage: AssistantMessage,
  toolUseID: string,
  forceDecision?: PermissionDecision<Input>,
) => Promise<PermissionDecision<Input>>
```

**实现机制**:

1. **创建 PermissionContext**:
   - 包含工具、输入、上下文、消息 ID 等信息
   - 提供 `resolveIfAborted` 原子检查
   - 提供 `logDecision`、`logCancelled` 等日志方法

2. **权限检查流程**:
   ```typescript
   const decisionPromise = forceDecision !== undefined 
     ? Promise.resolve(forceDecision)
     : hasPermissionsToUseTool(tool, input, toolUseContext, assistantMessage, toolUseID)
   ```

3. **行为处理**:
   - **allow**: 直接允许，记录分类器批准（如果适用）
   - **deny**: 记录拒绝，显示通知（如果是 auto-mode 拒绝）
   - **ask**: 进入交互式权限请求流程

4. **协调器处理** (Coordinator):
   - 对于 coordinator workers，在显示对话框前等待自动化检查
   - 调用 `handleCoordinatorPermission`

5. **Swarm 处理**:
   - 调用 `handleSwarmWorkerPermission` 尝试分类器自动批准
   - 通过 mailbox 将权限请求转发给 leader

6. **Bash 分类器优雅期**:
   - 等待最多 2 秒获取推测性分类器结果
   - 高置信度匹配时跳过对话框直接允许

7. **交互式权限**:
   - 调用 `handleInteractivePermission` 显示对话框
   - 支持 Bridge 模式和 Channels 模式回调

8. **错误处理**:
   - `AbortError` / `APIUserAbortError`: 记录取消，解析为中止决策
   - 其他错误：记录错误，解析为中止决策
   - `finally`: 清除分类器检查状态

**关键函数**:
- `createPermissionContext`: 创建权限上下文
- `createPermissionQueueOps`: 创建队列操作接口
- `logPermissionDecision`: 记录权限决策日志

### 3.2 useMergedTools

**文件**: `hooks/useMergedTools.ts`

**职责**: 合并内置工具和 MCP 工具

**接口**:
```typescript
export function useMergedTools(
  initialTools: Tools,
  mcpTools: Tools,
  toolPermissionContext: ToolPermissionContext,
): Tools
```

**实现机制**:
```typescript
export function useMergedTools(
  initialTools: Tools,
  mcpTools: Tools,
  toolPermissionContext: ToolPermissionContext,
): Tools {
  return useMemo(() => {
    const assembled = assembleToolPool(toolPermissionContext, mcpTools)
    return mergeAndFilterTools(
      initialTools,
      assembled,
      toolPermissionContext.mode,
    )
  }, [initialTools, mcpTools, toolPermissionContext])
}
```

### 3.3 useCancelRequest

**文件**: `hooks/useCancelRequest.ts`

**职责**: 处理取消/退出键绑定（CancelRequestHandler 组件）

**接口**:
```typescript
type CancelRequestHandlerProps = {
  setToolUseConfirmQueue: (f: (queue: ToolUseConfirm[]) => ToolUseConfirm[]) => void
  onCancel: () => void
  onAgentsKilled: () => void
  isMessageSelectorVisible: boolean
  screen: Screen
  abortSignal?: AbortSignal
  popCommandFromQueue?: () => void
  vimMode?: VimMode
  isLocalJSXCommand?: boolean
  isSearchingHistory?: boolean
  isHelpOpen?: boolean
  inputMode?: PromptInputMode
  inputValue?: string
  streamMode?: SpinnerMode
}
```

**关键功能**:

1. **优先级处理**:
   - 优先级 1: 如果有活动任务，优先取消
   - 优先级 2: Claude 空闲时弹出队列
   - 降级：无操作可取消

2. **双重按下杀死 Agent**:
   - 3 秒时间窗口内第二次按下杀死所有后台 Agent
   - 第一次按下显示确认提示
   - 第二次按下执行杀死操作

3. **键绑定**:
   - `chat:cancel` (Escape): 取消当前请求
   - `app:interrupt` (Ctrl+C): 中断并可能杀死 Agent
   - `app:killAgents` (Ctrl+X Ctrl+K): 双重按下杀死所有 Agent

4. **上下文感知**:
   - 在 Transcript、HistorySearch、Help 等上下文中不活跃
   - Overlay 通过 `useRegisterOverlay` 注册自己的处理器
   - Local JSX 命令处理自己的输入

---

## 4. 输入相关 Hooks

### 4.1 useTextInput

**文件**: `hooks/useTextInput.ts`

**职责**: 核心文本输入 Hook，处理所有键盘输入和光标操作

**接口**:
```typescript
export type UseTextInputProps = {
  value: string
  onChange: (value: string) => void
  onSubmit?: (value: string) => void
  onExit?: () => void
  onExitMessage?: (show: boolean, key?: string) => void
  onHistoryUp?: () => void
  onHistoryDown?: () => void
  onHistoryReset?: () => void
  onClearInput?: () => void
  focus?: boolean
  mask?: string
  multiline?: boolean
  cursorChar: string
  highlightPastedText?: boolean
  invert: (text: string) => string
  themeText: (text: string) => string
  columns: number
  onImagePaste?: (base64Image: string, mediaType?, filename?, dimensions?, sourcePath?) => void
  disableCursorMovementForUpDownKeys?: boolean
  disableEscapeDoublePress?: boolean
  maxVisibleLines?: number
  externalOffset: number
  onOffsetChange: (offset: number) => void
  inputFilter?: (input: string, key: Key) => string
  inlineGhostText?: InlineGhostText
  dim?: (text: string) => string
}

export function useTextInput(props: UseTextInputProps): TextInputState
```

**返回类型**:
```typescript
export type TextInputState = {
  onInput: (input: string, key: Key) => void
  renderedValue: string
  offset: number
  setOffset: (offset: number) => void
  cursorLine: number
  cursorColumn: number
  viewportCharOffset: number
  viewportCharEnd: number
}
```

**核心功能**:

1. **双重按下处理**:
   - `handleCtrlC`: Ctrl+C 双重按下退出
   - `handleEscape`: Esc 双重按下清除输入
   - `handleEmptyCtrlD`: Ctrl+D 双重按下退出

2. **Kill Ring 操作**:
   ```typescript
   function killToLineEnd(): Cursor {
     const { cursor: newCursor, killed } = cursor.deleteToLineEnd()
     pushToKillRing(killed, 'append')
     return newCursor
   }
   
   function killToLineStart(): Cursor {
     const { cursor: newCursor, killed } = cursor.deleteToLineStart()
     pushToKillRing(killed, 'prepend')
     return newCursor
   }
   
   function killWordBefore(): Cursor {
     const { cursor: newCursor, killed } = cursor.deleteWordBefore()
     pushToKillRing(killed, 'prepend')
     return newCursor
   }
   ```

3. **Yank 操作**:
   ```typescript
   function yank(): Cursor {
     const text = getLastKill()
     if (text.length > 0) {
       const startOffset = cursor.offset
       const newCursor = cursor.insert(text)
       recordYank(startOffset, text.length)
       return newCursor
     }
     return cursor
   }
   
   function handleYankPop(): Cursor {
     const popResult = yankPop()
     if (!popResult) return cursor
     const { text, start, length } = popResult
     const before = cursor.text.slice(0, start)
     const after = cursor.text.slice(start + length)
     const newText = before + text + after
     const newOffset = start + text.length
     updateYankLength(text.length)
     return Cursor.fromText(newText, columns, newOffset)
   }
   ```

4. **Ctrl 键映射**:
   ```typescript
   const handleCtrl = mapInput([
     ['a', () => cursor.startOfLine()],
     ['b', () => cursor.left()],
     ['c', handleCtrlC],
     ['d', handleCtrlD],
     ['e', () => cursor.endOfLine()],
     ['f', () => cursor.right()],
     ['h', () => cursor.deleteTokenBefore() ?? cursor.backspace()],
     ['k', killToLineEnd],
     ['n', () => downOrHistoryDown()],
     ['p', () => upOrHistoryUp()],
     ['u', killToLineStart],
     ['w', killWordBefore],
     ['y', yank],
   ])
   ```

5. **Meta 键映射**:
   ```typescript
   const handleMeta = mapInput([
     ['b', () => cursor.prevWord()],
     ['f', () => cursor.nextWord()],
     ['d', () => cursor.deleteWordAfter()],
     ['y', handleYankPop],
   ])
   ```

6. **Enter 处理**:
   - 多行模式下反斜杠 + Enter 插入换行
   - Meta+Enter 或 Shift+Enter 插入换行
   - Apple Terminal 检测 Shift 修饰键

7. **上下箭头处理**:
   - 优先按包裹行移动
   - 多行模式下按逻辑行移动
   - 无法移动时触发历史导航

8. **键映射**:
   ```typescript
   function mapKey(key: Key): InputMapper {
     switch (true) {
       case key.escape:
         return () => {
           if (disableEscapeDoublePress) return cursor
           handleEscape()
           return cursor
         }
       case key.leftArrow && (key.ctrl || key.meta || key.fn):
         return () => cursor.prevWord()
       case key.rightArrow && (key.ctrl || key.meta || key.fn):
         return () => cursor.nextWord()
       case key.backspace:
         return key.meta || key.ctrl
           ? killWordBefore
           : () => cursor.deleteTokenBefore() ?? cursor.backspace()
       case key.delete:
         return key.meta ? killToLineEnd : () => cursor.del()
       case key.ctrl:
         return handleCtrl
       // ... 更多键映射
     }
   }
   ```

9. **输入处理**:
   ```typescript
   function onInput(input: string, key: Key): void {
     // 应用过滤器
     const filteredInput = inputFilter ? inputFilter(input, key) : input
     
     // 过滤 DEL 字符（SSH/tmux 中的退格问题）
     if (!key.backspace && !key.delete && input.includes('\x7f')) {
       const delCount = (input.match(/\x7f/g) || []).length
       let currentCursor = cursor
       for (let i = 0; i < delCount; i++) {
         currentCursor = currentCursor.deleteTokenBefore() ?? currentCursor.backspace()
       }
       if (!cursor.equals(currentCursor)) {
         if (cursor.text !== currentCursor.text) {
           onChange(currentCursor.text)
         }
         setOffset(currentCursor.offset)
       }
       resetKillAccumulation()
       resetYankState()
       return
     }
     
     // 重置 kill 积累和 yank 状态
     if (!isKillKey(key, filteredInput)) {
       resetKillAccumulation()
     }
     if (!isYankKey(key, filteredInput)) {
       resetYankState()
     }
     
     const nextCursor = mapKey(key)(filteredInput)
     if (nextCursor) {
       if (!cursor.equals(nextCursor)) {
         if (cursor.text !== nextCursor.text) {
           onChange(nextCursor.text)
         }
         setOffset(nextCursor.offset)
       }
       // SSH 合并的 Enter 处理
       if (
         filteredInput.length > 1 &&
         filteredInput.endsWith('\r') &&
         !filteredInput.slice(0, -1).includes('\r') &&
         filteredInput[filteredInput.length - 2] !== '\\'
       ) {
         onSubmit?.(nextCursor.text)
       }
     }
   }
   ```

### 4.2 useVimInput

**文件**: `hooks/useVimInput.ts`

**职责**: Vim 模式输入处理

**接口**:
```typescript
export function useVimInput(props: UseVimInputProps): VimInputState
```

**核心功能**:

1. **状态管理**:
   ```typescript
   const vimStateRef = React.useRef<VimState>(createInitialVimState())
   const [mode, setMode] = useState<VimMode>('INSERT')
   const persistentRef = React.useRef<PersistentState>(
     createInitialPersistentState(),
   )
   ```

2. **模式切换**:
   ```typescript
   const switchToInsertMode = useCallback((offset?: number): void => {
     if (offset !== undefined) {
       textInput.setOffset(offset)
     }
     vimStateRef.current = { mode: 'INSERT', insertedText: '' }
     setMode('INSERT')
     onModeChange?.('INSERT')
   }, [textInput, onModeChange])
   
   const switchToNormalMode = useCallback((): void => {
     const current = vimStateRef.current
     if (current.mode === 'INSERT' && current.insertedText) {
       persistentRef.current.lastChange = {
         type: 'insert',
         text: current.insertedText,
       }
     }
     
     // Vim 行为：退出插入模式时左移光标
     const offset = textInput.offset
     if (offset > 0 && props.value[offset - 1] !== '\n') {
       textInput.setOffset(offset - 1)
     }
     
     vimStateRef.current = { mode: 'NORMAL', command: { type: 'idle' } }
     setMode('NORMAL')
     onModeChange?.('NORMAL')
   }, [onModeChange, textInput, props.value])
   ```

3. **Operator 上下文**:
   ```typescript
   function createOperatorContext(
     cursor: Cursor,
     isReplay: boolean = false,
   ): OperatorContext {
     return {
       cursor,
       text: props.value,
       setText: (newText: string) => props.onChange(newText),
       setOffset: (offset: number) => textInput.setOffset(offset),
       enterInsert: (offset: number) => switchToInsertMode(offset),
       getRegister: () => persistentRef.current.register,
       setRegister: (content: string, linewise: boolean) => {
         persistentRef.current.register = content
         persistentRef.current.registerIsLinewise = linewise
       },
       getLastFind: () => persistentRef.current.lastFind,
       setLastFind: (type, char) => {
         persistentRef.current.lastFind = { type, char }
       },
       recordChange: isReplay
         ? () => {}
         : (change: RecordedChange) => {
             persistentRef.current.lastChange = change
           },
     }
   }
   ```

4. **Dot-repeat 重放**:
   ```typescript
   function replayLastChange(): void {
     const change = persistentRef.current.lastChange
     if (!change) return
     
     const cursor = Cursor.fromText(props.value, props.columns, textInput.offset)
     const ctx = createOperatorContext(cursor, true)
     
     switch (change.type) {
       case 'insert':
         if (change.text) {
           const newCursor = cursor.insert(change.text)
           props.onChange(newCursor.text)
           textInput.setOffset(newCursor.offset)
         }
         break
       case 'x':
         executeX(change.count, ctx)
         break
       // ... 更多变更类型
     }
   }
   ```

5. **Vim 输入处理**:
   ```typescript
   function handleVimInput(rawInput: string, key: Key): void {
     const state = vimStateRef.current
     const filtered = inputFilter ? inputFilter(rawInput, key) : rawInput
     const input = state.mode === 'INSERT' ? filtered : rawInput
     const cursor = Cursor.fromText(props.value, props.columns, textInput.offset)
     
     // Ctrl 键：传递给基础处理器
     if (key.ctrl) {
       textInput.onInput(input, key)
       return
     }
     
     // Escape: INSERT->NORMAL 模式切换
     if (key.escape && state.mode === 'INSERT') {
       switchToNormalMode()
       return
     }
     
     // Escape: NORMAL 模式取消待处理命令
     if (key.escape && state.mode === 'NORMAL') {
       vimStateRef.current = { mode: 'NORMAL', command: { type: 'idle' } }
       return
     }
     
     // Enter: 无论模式如何都传递给基础处理器
     if (key.return) {
       textInput.onInput(input, key)
       return
     }
     
     // INSERT 模式：跟踪插入的文本用于 dot-repeat
     if (state.mode === 'INSERT') {
       if (key.backspace || key.delete) {
         if (state.insertedText.length > 0) {
           vimStateRef.current = {
             mode: 'INSERT',
             insertedText: state.insertedText.slice(
               0,
               -(lastGrapheme(state.insertedText).length || 1),
             ),
           }
         }
       } else {
         vimStateRef.current = {
           mode: 'INSERT',
           insertedText: state.insertedText + input,
         }
       }
       textInput.onInput(input, key)
       return
     }
     
     // NORMAL 模式：Vim 命令处理
     if (state.mode !== 'NORMAL') {
       return
     }
     
     // 空闲状态：箭头键传递给基础处理器
     if (
       state.command.type === 'idle' &&
       (key.upArrow || key.downArrow || key.leftArrow || key.rightArrow)
     ) {
       textInput.onInput(input, key)
       return
     }
     
     const ctx: TransitionContext = {
       ...createOperatorContext(cursor, false),
       onUndo: props.onUndo,
       onDotRepeat: replayLastChange,
     }
     
     // 映射箭头键到 Vim 动作
     let vimInput = input
     if (key.leftArrow) vimInput = 'h'
     else if (key.rightArrow) vimInput = 'l'
     else if (key.upArrow) vimInput = 'k'
     else if (key.downArrow) vimInput = 'j'
     else if (expectsMotion && key.backspace) vimInput = 'h'
     else if (expectsMotion && state.command.type !== 'count' && key.delete)
       vimInput = 'x'
     
     const result = transition(state.command, vimInput, ctx)
     
     if (result.execute) {
       result.execute()
     }
     
     // 更新命令状态
     if (vimStateRef.current.mode === 'NORMAL') {
       if (result.next) {
         vimStateRef.current = { mode: 'NORMAL', command: result.next }
       } else if (result.execute) {
         vimStateRef.current = { mode: 'NORMAL', command: { type: 'idle' } }
       }
     }
   }
   ```

---

## 5. UI 相关 Hooks

### 5.1 useTerminalSize

**文件**: `hooks/useTerminalSize.ts`

**职责**: 获取终端尺寸

**接口**:
```typescript
export function useTerminalSize(): TerminalSize
```

**实现机制**:
```typescript
export function useTerminalSize(): TerminalSize {
  const size = useContext(TerminalSizeContext)
  
  if (!size) {
    throw new Error('useTerminalSize must be used within an Ink App component')
  }
  
  return size
}
```

### 5.2 useBlink

**文件**: `hooks/useBlink.ts`

**职责**: 同步闪烁动画

**接口**:
```typescript
export function useBlink(
  enabled: boolean,
  intervalMs: number = BLINK_INTERVAL_MS,
): [ref: (element: DOMElement | null) => void, isVisible: boolean]
```

**实现机制**:
```typescript
const BLINK_INTERVAL_MS = 600

export function useBlink(
  enabled: boolean,
  intervalMs: number = BLINK_INTERVAL_MS,
): [ref, isVisible] {
  const focused = useTerminalFocus()
  const [ref, time] = useAnimationFrame(enabled && focused ? intervalMs : null)
  
  if (!enabled || !focused) return [ref, true]
  
  // 所有实例从同一时间派生状态，实现同步
  const isVisible = Math.floor(time / intervalMs) % 2 === 0
  return [ref, isVisible]
}
```

**特性**:
- 所有实例同步闪烁（从同一动画时钟派生）
- 终端失焦时暂停
- 仅当至少一个订阅者可见时时钟才运行

### 5.3 useDoublePress

**文件**: `hooks/useDoublePress.ts`

**职责**: 处理双重按下手势

**接口**:
```typescript
export function useDoublePress(
  setPending: (pending: boolean) => void,
  onDoublePress: () => void,
  onFirstPress?: () => void,
): () => void
```

**常量**:
```typescript
export const DOUBLE_PRESS_TIMEOUT_MS = 800
```

**实现机制**:
```typescript
export function useDoublePress(
  setPending,
  onDoublePress,
  onFirstPress,
): () => void {
  const lastPressRef = useRef<number>(0)
  const timeoutRef = useRef<NodeJS.Timeout | undefined>(undefined)
  
  const clearTimeoutSafe = useCallback(() => {
    if (timeoutRef.current) {
      clearTimeout(timeoutRef.current)
      timeoutRef.current = undefined
    }
  }, [])
  
  useEffect(() => {
    return () => {
      clearTimeoutSafe()
    }
  }, [clearTimeoutSafe])
  
  return useCallback(() => {
    const now = Date.now()
    const timeSinceLastPress = now - lastPressRef.current
    const isDoublePress =
      timeSinceLastPress <= DOUBLE_PRESS_TIMEOUT_MS &&
      timeoutRef.current !== undefined
    
    if (isDoublePress) {
      // 检测到双重按下
      clearTimeoutSafe()
      setPending(false)
      onDoublePress()
    } else {
      // 第一次按下
      onFirstPress?.()
      setPending(true)
      
      clearTimeoutSafe()
      timeoutRef.current = setTimeout(
        (setPending, timeoutRef) => {
          setPending(false)
          timeoutRef.current = undefined
        },
        DOUBLE_PRESS_TIMEOUT_MS,
        setPending,
        timeoutRef,
      )
    }
    
    lastPressRef.current = now
  }, [setPending, onDoublePress, onFirstPress, clearTimeoutSafe])
}
```

---

## 6. 历史搜索相关 Hooks

### 6.1 useHistorySearch

**文件**: `hooks/useHistorySearch.ts`

**职责**: 历史搜索功能

**接口**:
```typescript
export function useHistorySearch(
  onAcceptHistory: (entry: HistoryEntry) => void,
  currentInput: string,
  onInputChange: (input: string) => void,
  onCursorChange: (cursorOffset: number) => void,
  currentCursorOffset: number,
  onModeChange: (mode: PromptInputMode) => void,
  currentMode: PromptInputMode,
  isSearching: boolean,
  setIsSearching: (isSearching: boolean) => void,
  setPastedContents: (pastedContents: HistoryEntry['pastedContents']) => void,
  currentPastedContents: HistoryEntry['pastedContents'],
): {
  historyQuery: string
  setHistoryQuery: (query: string) => void
  historyMatch: HistoryEntry | undefined
  historyFailedMatch: boolean
  handleKeyDown: (e: KeyboardEvent) => void
}
```

**核心功能**:

1. **状态管理**:
   ```typescript
   const [historyQuery, setHistoryQuery] = useState('')
   const [historyFailedMatch, setHistoryFailedMatch] = useState(false)
   const [originalInput, setOriginalInput] = useState('')
   const [originalCursorOffset, setOriginalCursorOffset] = useState(0)
   const [originalMode, setOriginalMode] = useState<PromptInputMode>('prompt')
   const [originalPastedContents, setOriginalPastedContents] = useState({})
   const [historyMatch, setHistoryMatch] = useState<HistoryEntry | undefined>(undefined)
   const historyReader = useRef<AsyncGenerator<HistoryEntry> | undefined>(undefined)
   const seenPrompts = useRef<Set<string>>(new Set())
   const searchAbortController = useRef<AbortController | null>(null)
   ```

2. **历史搜索**:
   ```typescript
   const searchHistory = useCallback(async (resume: boolean, signal?: AbortSignal): Promise<void> => {
     if (!isSearching) return
     
     if (historyQuery.length === 0) {
       closeHistoryReader()
       seenPrompts.current.clear()
       setHistoryMatch(undefined)
       setHistoryFailedMatch(false)
       onInputChange(originalInput)
       onCursorChange(originalCursorOffset)
       onModeChange(originalMode)
       setPastedContents(originalPastedContents)
       return
     }
     
     if (!resume) {
       closeHistoryReader()
       historyReader.current = makeHistoryReader()
       seenPrompts.current.clear()
     }
     
     if (!historyReader.current) return
     
     while (true) {
       if (signal?.aborted) return
       
       const item = await historyReader.current.next()
       if (item.done) {
         setHistoryFailedMatch(true)
         return
       }
       
       const display = item.value.display
       const matchPosition = display.lastIndexOf(historyQuery)
       
       if (matchPosition !== -1 && !seenPrompts.current.has(display)) {
         seenPrompts.current.add(display)
         setHistoryMatch(item.value)
         setHistoryFailedMatch(false)
         
         const mode = getModeFromInput(display)
         onModeChange(mode)
         onInputChange(display)
         setPastedContents(item.value.pastedContents)
         
         const value = getValueFromInput(display)
         const cleanMatchPosition = value.lastIndexOf(historyQuery)
         onCursorChange(
           cleanMatchPosition !== -1 ? cleanMatchPosition : matchPosition,
         )
         return
       }
     }
   }, [/* 依赖项 */])
   ```

3. **键绑定**:
   - `history:search` (Ctrl+R): 开始搜索
   - `historySearch:next`: 查找下一个匹配
   - `historySearch:accept`: 接受当前匹配
   - `historySearch:cancel`: 取消搜索
   - `historySearch:execute`: 执行（接受并提交）

4. **资源清理**:
   ```typescript
   const closeHistoryReader = useCallback((): void => {
     if (historyReader.current) {
       // 必须显式调用 .return() 触发 finally 块，关闭文件句柄
       void historyReader.current.return(undefined)
       historyReader.current = undefined
     }
   }, [])
   ```

---

## 7. 虚拟滚动相关 Hooks

### 7.1 useVirtualScroll

**文件**: `hooks/useVirtualScroll.ts`

**职责**: 虚拟滚动，仅渲染视口内的项目

**接口**:
```typescript
export function useVirtualScroll(
  scrollRef: RefObject<ScrollBoxHandle | null>,
  itemKeys: readonly string[],
  columns: number,
): VirtualScrollResult
```

**返回类型**:
```typescript
export type VirtualScrollResult = {
  range: readonly [number, number]  // [startIndex, endIndex)
  topSpacer: number
  bottomSpacer: number
  measureRef: (key: string) => (el: DOMElement | null) => void
  spacerRef: RefObject<DOMElement | null>
  offsets: ArrayLike<number>
  getItemTop: (index: number) => number
  getItemElement: (index: number) => DOMElement | null
  getItemHeight: (index: number) => number | undefined
  scrollToIndex: (i: number) => void
}
```

**常量**:
```typescript
const DEFAULT_ESTIMATE = 3  // 未测量项目的估计高度
const OVERSCAN_ROWS = 80    // 视口上下额外渲染的行数
const COLD_START_COUNT = 30 // 冷启动时渲染的项目数
const SCROLL_QUANTUM = OVERSCAN_ROWS >> 1  // scrollTop 量化单位
const PESSIMISTIC_HEIGHT = 1  // 最坏情况高度假设
const MAX_MOUNTED_ITEMS = 300  // 挂载项目上限
const SLIDE_STEP = 25  // 每次提交挂载的最大新项目数
```

**核心优化**:

1. **使用 useSyncExternalStore**:
   - 将 scrollTop 量化到 SCROLL_QUANTUM 区间
   - 小幅度滚动不触发 React 提交
   - 粘性滚动状态折叠到快照中

2. **高度缓存**:
   ```typescript
   const heightCache = useRef(new Map<string, number>())
   const offsetVersionRef = useRef(0)
   const offsetsRef = useRef({ arr: new Float64Array(0), version: -1, n: -1 })
   ```

3. **偏移量计算**:
   ```typescript
   if (
     offsetsRef.current.version !== offsetVersionRef.current ||
     offsetsRef.current.n !== n
   ) {
     const arr = offsetsRef.current.arr.length >= n + 1
       ? offsetsRef.current.arr
       : new Float64Array(n + 1)
     arr[0] = 0
     for (let i = 0; i < n; i++) {
       arr[i + 1] = arr[i]! + (heightCache.current.get(itemKeys[i]!) ?? DEFAULT_ESTIMATE)
     }
     offsetsRef.current = { arr, version: offsetVersionRef.current, n }
   }
   ```

4. **范围计算**:
   - 粘性滚动：从尾部向后遍历
   - 用户滚动：二分查找起始位置，累积覆盖范围
   - 冻结渲染：列变化时保持原范围 2 次渲染

5. **列变化处理**:
   ```typescript
   if (prevColumns.current !== columns) {
     const ratio = prevColumns.current / columns
     prevColumns.current = columns
     for (const [k, h] of heightCache.current) {
       heightCache.current.set(k, Math.max(1, Math.round(h * ratio)))
     }
     offsetVersionRef.current++
     skipMeasurementRef.current = true
     freezeRendersRef.current = 2
   }
   ```

6. **测量 Ref**:
   ```typescript
   const measureRef = useCallback((key: string) => {
     let fn = refCache.current.get(key)
     if (!fn) {
       fn = (el: DOMElement | null) => {
         if (el) {
           itemRefs.current.set(key, el)
         } else {
           const yoga = itemRefs.current.get(key)?.yogaNode
           if (yoga && !skipMeasurementRef.current) {
             const h = yoga.getComputedHeight()
             if (
               (h > 0 || yoga.getComputedWidth() > 0) &&
               heightCache.current.get(key) !== h
             ) {
               heightCache.current.set(key, h)
               offsetVersionRef.current++
             }
           }
           itemRefs.current.delete(key)
         }
       }
       refCache.current.set(key, fn)
     }
     return fn
   }, [])
   ```

---

## 8. 退出处理相关 Hooks

### 8.1 useExitOnCtrlCD

**文件**: `hooks/useExitOnCtrlCD.ts`

**职责**: 处理 Ctrl+C 和 Ctrl+D 退出应用

**接口**:
```typescript
export function useExitOnCtrlCD(
  useKeybindingsHook: UseKeybindingsHook,
  onInterrupt?: () => boolean,
  onExit?: () => void,
  isActive = true,
): ExitState
```

**返回类型**:
```typescript
export type ExitState = {
  pending: boolean
  keyName: 'Ctrl-C' | 'Ctrl-D' | null
}
```

**实现机制**:
```typescript
export function useExitOnCtrlCD(
  useKeybindingsHook,
  onInterrupt,
  onExit,
  isActive = true,
): ExitState {
  const { exit } = useApp()
  const [exitState, setExitState] = useState<ExitState>({
    pending: false,
    keyName: null,
  })
  
  const exitFn = useMemo(() => onExit ?? exit, [onExit, exit])
  
  // Ctrl+C 双重按下处理器
  const handleCtrlCDoublePress = useDoublePress(
    pending => setExitState({ pending, keyName: 'Ctrl-C' }),
    exitFn,
  )
  
  // Ctrl+D 双重按下处理器
  const handleCtrlDDoublePress = useDoublePress(
    pending => setExitState({ pending, keyName: 'Ctrl-D' }),
    exitFn,
  )
  
  // app:interrupt 处理器
  const handleInterrupt = useCallback(() => {
    if (onInterrupt?.()) return  // Feature 处理了
    handleCtrlCDoublePress()
  }, [handleCtrlCDoublePress, onInterrupt])
  
  // app:exit 处理器
  const handleExit = useCallback(() => {
    handleCtrlDDoublePress()
  }, [handleCtrlDDoublePress])
  
  const handlers = useMemo(
    () => ({
      'app:interrupt': handleInterrupt,
      'app:exit': handleExit,
    }),
    [handleInterrupt, handleExit],
  )
  
  useKeybindingsHook(handlers, { context: 'Global', isActive })
  
  return exitState
}
```

### 8.2 useExitOnCtrlCDWithKeybindings

**文件**: `hooks/useExitOnCtrlCDWithKeybindings.ts`

**职责**: useExitOnCtrlCD 的便捷包装

**接口**:
```typescript
export function useExitOnCtrlCDWithKeybindings(
  onExit?: () => void,
  onInterrupt?: () => boolean,
  isActive?: boolean,
): ExitState
```

**实现机制**:
```typescript
export function useExitOnCtrlCDWithKeybindings(
  onExit,
  onInterrupt,
  isActive,
): ExitState {
  return useExitOnCtrlCD(useKeybindings, onInterrupt, onExit, isActive)
}
```

---

## 9. Hooks 配置管理

### 9.1 hooksConfigManager

**文件**: `utils/hooks/hooksConfigManager.ts`

**职责**: Hooks 配置管理，支持 managed hooks only 模式

**核心函数**:

1. **`getHooksFromAllowedSources`**: 从允许的来源获取 hooks
   ```typescript
   function getHooksFromAllowedSources(): HooksSettings {
     const policySettings = settingsModule.getSettingsForSource('policySettings')
     
     // Managed settings 禁用所有 hooks
     if (policySettings?.disableAllHooks === true) {
       return {}
     }
     
     // allowManagedHooksOnly: 仅使用 managed hooks
     if (policySettings?.allowManagedHooksOnly === true) {
       return policySettings.hooks ?? {}
     }
     
     // strictPluginOnlyCustomization: 阻止 user/project/local settings hooks
     if (isRestrictedToPluginOnly('hooks')) {
       return policySettings?.hooks ?? {}
     }
     
     const mergedSettings = settingsModule.getSettings_DEPRECATED()
     
     // disableAllHooks 在非 managed settings 中：仅 managed hooks 运行
     if (mergedSettings.disableAllHooks === true) {
       return policySettings?.hooks ?? {}
     }
     
     // 否则使用所有 hooks（向后兼容）
     return mergedSettings.hooks ?? {}
   }
   ```

2. **`shouldAllowManagedHooksOnly`**: 检查是否仅允许 managed hooks
   ```typescript
   export function shouldAllowManagedHooksOnly(): boolean {
     const policySettings = settingsModule.getSettingsForSource('policySettings')
     if (policySettings?.allowManagedHooksOnly === true) {
       return true
     }
     // disableAllHooks 在非 managed settings 中：视为 managed-only
     if (
       settingsModule.getSettings_DEPRECATED().disableAllHooks === true &&
       policySettings?.disableAllHooks !== true
     ) {
       return true
     }
     return false
   }
   ```

3. **`shouldDisableAllHooksIncludingManaged`**: 检查是否禁用所有 hooks（包括 managed）
   ```typescript
   export function shouldDisableAllHooksIncludingManaged(): boolean {
     return (
       settingsModule.getSettingsForSource('policySettings')?.disableAllHooks ===
       true
     )
   }
   ```

4. **快照管理**:
   ```typescript
   export function captureHooksConfigSnapshot(): void {
     initialHooksConfig = getHooksFromAllowedSources()
   }
   
   export function updateHooksConfigSnapshot(): void {
     resetSettingsCache()  // 重置缓存以读取最新设置
     initialHooksConfig = getHooksFromAllowedSources()
   }
   
   export function getHooksConfigFromSnapshot(): HooksSettings | null {
     if (initialHooksConfig === null) {
       captureHooksConfigSnapshot()
     }
     return initialHooksConfig
   }
   
   export function resetHooksConfigSnapshot(): void {
     initialHooksConfig = null
     resetSdkInitState()
   }
   ```

---

## 10. 总结

这个 Hooks 系统是一个极其复杂和完善的架构，包含以下关键特性：

1. **分层架构**:
   - 基础输入处理（useTextInput, useVimInput）
   - 状态管理（useSettings, useDynamicConfig）
   - 工具执行和权限（useCanUseTool, PermissionContext）
   - UI 和渲染（useTerminalSize, useBlink, useVirtualScroll）
   - 命令和历史（useCommandQueue, useHistorySearch）

2. **性能优化**:
   - useSyncExternalStore 用于高效外部状态订阅
   - useDeferredValue 用于时间切片
   - 防抖和节流
   - 缓存和记忆化
   - 虚拟滚动

3. **权限系统**:
   - 多层权限检查（配置、分类器、用户、Hook）
   - 权限持久化
   - 详细的分析和遥测

4. **输入处理**:
   - 完整的 readline 功能（kill ring, yank）
   - Vim 模式支持
   - 多模式输入（prompt, bash 等）

5. **Hooks 系统**:
   - 27 种不同的 Hook 事件
   - 多来源支持（user/project/local/policy/session/plugin/builtin）
   - 复杂的优先级和过滤逻辑

这是一个企业级的、生产就绪的 Hooks 架构，展示了 React Hooks 在复杂 CLI 应用中的最佳实践。

---

*文档持续更新中...*
