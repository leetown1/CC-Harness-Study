# Context 系统深度技术文档

> 基于逐行代码分析的完整技术文档  
> **探索完成时间**: 2026 年 4 月 1 日  
> **核心文件**: context/ 目录下 12 个 Context 文件

---

## 1. Context 系统架构概览

### 1.1 Context 层次结构图

```
App Root
├── AppStateProvider (核心状态管理)
│   ├── MailboxProvider (消息队列)
│   └── VoiceProvider (语音功能 - ANT only)
│
├── ThemeProvider (主题管理)
│
├── TerminalFocusProvider (终端焦点)
│
├── TerminalSizeContext (终端尺寸)
│
├── ClockProvider (时钟/动画)
│
├── KeybindingProvider (按键绑定)
│
├── StatsProvider (统计指标)
│
├── PromptOverlayProvider (提示覆盖层)
│
├── ModalContext (模态框)
│
├── ExpandShellOutputContext (Shell 输出扩展)
│
└── WizardProvider (向导流程)
```

### 1.2 核心设计模式

1. **基础 Context 模式**: createContext + Provider + Consumer Hook
2. **Store + useSyncExternalStore 模式**: 精确订阅状态切片
3. **Data/Setter 分离模式**: 写入者不会因自己的写入而重新渲染
4. **嵌套 Provider 模式**: 多层 Context 组合

---

## 2. 核心 Context 文件深度分析

### 2.1 AppStateProvider - 核心状态管理

**文件**: `state/AppState.tsx`

**职责**: 应用的全局状态管理中心，使用 Store 模式管理所有 AppState。

**核心类型**:
```typescript
type Props = {
  children: React.ReactNode;
  initialState?: AppState;
  onChangeAppState?: (args: {
    newState: AppState;
    oldState: AppState;
  }) => void;
};
```

**Provider 实现**:
```typescript
export const AppStoreContext = React.createContext<AppStateStore | null>(null);
const HasAppStateContext = React.createContext<boolean>(false);

export function AppStateProvider({
  children,
  initialState,
  onChangeAppState,
}: Props): React.ReactNode {
  // 防止嵌套
  const hasAppStateContext = useContext(HasAppStateContext);
  if (hasAppStateContext) {
    throw new Error("AppStateProvider can not be nested...");
  }
  
  // 创建 Store（只创建一次）
  const [store] = useState(() =>
    createStore<AppState>(
      initialState ?? getDefaultAppState(),
      onChangeAppState,
    )
  );
  
  // 初始化时检查 bypass permissions mode
  useEffect(() => {
    const { toolPermissionContext } = store.getState();
    if (toolPermissionContext.isBypassPermissionsModeAvailable && 
        isBypassPermissionsModeDisabled()) {
      store.setState(prev => ({
        ...prev,
        toolPermissionContext: createDisabledBypassPermissionsContext(
          prev.toolPermissionContext
        ),
      }));
    }
  }, []);
  
  // 监听设置变化
  const onSettingsChange = useEffectEvent((source: SettingSource) =>
    applySettingsChange(source, store.setState)
  );
  useSettingsChange(onSettingsChange);
  
  return (
    <HasAppStateContext.Provider value={true}>
      <AppStoreContext.Provider value={store}>
        <MailboxProvider>
          <VoiceProvider>{children}</VoiceProvider>
        </MailboxProvider>
      </AppStoreContext.Provider>
    </HasAppStateContext.Provider>
  );
}
```

**Consumer Hooks**:

#### useAppState - 订阅状态切片
```typescript
export function useAppState<T>(selector: (state: AppState) => T): T {
  const store = useAppStore();
  const get = () => {
    const state = store.getState();
    const selected = selector(state);
    // 性能检查：不允许返回原状态
    if ("external" === 'ant' && state === selected) {
      throw new Error(`Your selector returned the original state...`);
    }
    return selected;
  };
  return useSyncExternalStore(store.subscribe, get, get);
}
```

**使用示例**:
```typescript
const verbose = useAppState(s => s.verbose);
const model = useAppState(s => s.mainLoopModel);
// 好的：选择现有子对象引用
const { text, promptId } = useAppState(s => s.promptSuggestion);
```

#### useSetAppState - 获取更新器
```typescript
export function useSetAppState() {
  return useAppStore().setState;
}
```

#### useAppStateStore - 获取完整 Store
```typescript
export function useAppStateStore() {
  return useAppStore();
}
```

#### useAppStateMaybeOutsideOfProvider - 安全版本
```typescript
export function useAppStateMaybeOutsideOfProvider<T>(
  selector: (state: AppState) => T,
): T | undefined {
  const store = useContext(AppStoreContext);
  return useSyncExternalStore(
    store ? store.subscribe : NOOP_SUBSCRIBE,
    () => store ? selector(store.getState()) : undefined
  );
}
```

### 2.2 MailboxProvider - 消息队列

**文件**: `context/mailbox.tsx`

**职责**: 提供 Mailbox 实例，用于组件间消息传递。

**实现**:
```typescript
const MailboxContext = createContext<Mailbox | undefined>(undefined);

export function MailboxProvider({ children }: Props): React.ReactNode {
  const mailbox = useMemo(() => new Mailbox(), []);
  return (
    <MailboxContext.Provider value={mailbox}>
      {children}
    </MailboxContext.Provider>
  );
}

export function useMailbox(): Mailbox {
  const mailbox = useContext(MailboxContext);
  if (!mailbox) {
    throw new Error("useMailbox must be used within a MailboxProvider");
  }
  return mailbox;
}
```

### 2.3 VoiceProvider - 语音状态管理

**文件**: `context/voice.tsx`

**职责**: 管理语音模式状态（ANT only，外部构建会被 DCE）。

**核心类型**:
```typescript
export type VoiceState = {
  voiceState: 'idle' | 'recording' | 'processing';
  voiceError: string | null;
  voiceInterimTranscript: string;
  voiceAudioLevels: number[];
  voiceWarmingUp: boolean;
};
```

**Provider 实现**:
```typescript
const VoiceContext = createContext<VoiceStore | null>(null);

export function VoiceProvider({ children }: Props): React.ReactNode {
  const [store] = useState(() => createStore<VoiceState>(DEFAULT_STATE));
  return (
    <VoiceContext.Provider value={store}>
      {children}
    </VoiceContext.Provider>
  );
}
```

**Consumer Hooks**:

#### useVoiceState - 订阅语音状态切片
```typescript
export function useVoiceState<T>(selector: (state: VoiceState) => T): T {
  const store = useVoiceStore();
  const get = () => selector(store.getState());
  return useSyncExternalStore(store.subscribe, get, get);
}
```

#### useSetVoiceState - 获取 setter
```typescript
export function useSetVoiceState() {
  return useVoiceStore().setState;
}
```

#### useGetVoiceState - 同步读取器
```typescript
export function useGetVoiceState(): () => VoiceState {
  return useVoiceStore().getState;
}
```

### 2.4 ThemeProvider - 主题管理

**文件**: `components/design-system/ThemeProvider.tsx`

**职责**: 管理应用主题（dark/light/auto），支持自动检测系统主题。

**核心类型**:
```typescript
type ThemeContextValue = {
  themeSetting: ThemeSetting;  // 用户偏好（可能是 'auto'）
  setThemeSetting: (setting: ThemeSetting) => void;
  setPreviewTheme: (setting: ThemeSetting) => void;
  savePreview: () => void;
  cancelPreview: () => void;
  currentTheme: ThemeName;  // 解析后的主题（永不为 'auto'）
};
```

**Provider 实现**:
```typescript
export function ThemeProvider({
  children,
  initialState,
  onThemeSave = defaultSaveTheme,
}: Props) {
  const [themeSetting, setThemeSetting] = useState(
    initialState ?? defaultInitialTheme
  );
  const [previewTheme, setPreviewTheme] = useState<ThemeSetting | null>(null);
  
  // 追踪系统主题（用于 'auto' 模式）
  const [systemTheme, setSystemTheme] = useState<SystemTheme>(() =>
    (initialState ?? themeSetting) === 'auto' 
      ? getSystemThemeName() 
      : 'dark'
  );
  
  const activeSetting = previewTheme ?? themeSetting;
  const { internal_querier } = useStdin();
  
  // 监听终端主题变化（'auto' 模式）
  useEffect(() => {
    if (feature('AUTO_THEME')) {
      if (activeSetting !== 'auto' || !internal_querier) return;
      let cleanup: (() => void) | undefined;
      let cancelled = false;
      void import('../../utils/systemThemeWatcher.js').then(({ watchSystemTheme }) => {
        if (cancelled) return;
        cleanup = watchSystemTheme(internal_querier, setSystemTheme);
      });
      return () => {
        cancelled = true;
        cleanup?.();
      };
    }
  }, [activeSetting, internal_querier]);
  
  const currentTheme: ThemeName = 
    activeSetting === 'auto' ? systemTheme : activeSetting;
  
  const value = useMemo<ThemeContextValue>(() => ({
    themeSetting,
    setThemeSetting: (newSetting) => {
      setThemeSetting(newSetting);
      setPreviewTheme(null);
      if (newSetting === 'auto') {
        setSystemTheme(getSystemThemeName());
      }
      onThemeSave?.(newSetting);
    },
    setPreviewTheme: (newSetting) => {
      setPreviewTheme(newSetting);
      if (newSetting === 'auto') {
        setSystemTheme(getSystemThemeName());
      }
    },
    savePreview: () => {
      if (previewTheme !== null) {
        setThemeSetting(previewTheme);
        setPreviewTheme(null);
        onThemeSave?.(previewTheme);
      }
    },
    cancelPreview: () => {
      if (previewTheme !== null) {
        setPreviewTheme(null);
      }
    },
    currentTheme,
  }), [themeSetting, previewTheme, currentTheme, onThemeSave]);
  
  return (
    <ThemeContext.Provider value={value}>
      {children}
    </ThemeContext.Provider>
  );
}
```

**Consumer Hooks**:

#### useTheme - 获取解析后的主题
```typescript
export function useTheme(): [ThemeName, (setting: ThemeSetting) => void] {
  const { currentTheme, setThemeSetting } = useContext(ThemeContext);
  return [currentTheme, setThemeSetting];
}
```

#### useThemeSetting - 获取原始设置
```typescript
export function useThemeSetting(): ThemeSetting {
  return useContext(ThemeContext).themeSetting;
}
```

#### usePreviewTheme - 预览主题控制
```typescript
export function usePreviewTheme() {
  const { setPreviewTheme, savePreview, cancelPreview } = useContext(ThemeContext);
  return { setPreviewTheme, savePreview, cancelPreview };
}
```

### 2.5 StatsProvider - 统计指标

**文件**: `context/stats.tsx`

**职责**: 提供性能指标收集和持久化功能。

**核心类型**:
```typescript
export type StatsStore = {
  increment(name: string, value?: number): void;
  set(name: string, value: number): void;
  observe(name: string, value: number): void;
  add(name: string, value: string): void;
  getAll(): Record<string, number>;
};
```

**Provider 实现**:
```typescript
export const StatsContext = createContext<StatsStore | null>(null);

export function StatsProvider({
  store: externalStore,
  children,
}: Props): React.ReactNode {
  const internalStore = useMemo(() => createStatsStore(), []);
  const store = externalStore ?? internalStore;
  
  // 退出时持久化指标
  useEffect(() => {
    const flush = () => {
      const metrics = store.getAll();
      if (Object.keys(metrics).length > 0) {
        saveCurrentProjectConfig(current => ({
          ...current,
          lastSessionMetrics: metrics,
        }));
      }
    };
    process.on('exit', flush);
    return () => {
      process.off('exit', flush);
    };
  }, [store]);
  
  return (
    <StatsContext.Provider value={store}>
      {children}
    </StatsContext.Provider>
  );
}
```

**Consumer Hooks**:

#### useStats - 获取 Store
```typescript
export function useStats(): StatsStore {
  const store = useContext(StatsContext);
  if (!store) {
    throw new Error("useStats must be used within a StatsProvider");
  }
  return store;
}
```

#### useCounter - 计数器
```typescript
export function useCounter(name: string): (value?: number) => void {
  const store = useStats();
  return useCallback(
    (value?: number) => store.increment(name, value),
    [store, name]
  );
}
```

#### useGauge - 仪表盘
```typescript
export function useGauge(name: string): (value: number) => void {
  const store = useStats();
  return useCallback(
    (value: number) => store.set(name, value),
    [store, name]
  );
}
```

#### useTimer - 计时器
```typescript
export function useTimer(name: string): (value: number) => void {
  const store = useStats();
  return useCallback(
    (value: number) => store.observe(name, value),
    [store, name]
  );
}
```

#### useSet - 集合计数器
```typescript
export function useSet(name: string): (value: string) => void {
  const store = useStats();
  return useCallback(
    (value: string) => store.add(name, value),
    [store, name]
  );
}
```

### 2.6 KeybindingProvider - 按键绑定

**文件**: `keybindings/KeybindingContext.tsx`

**职责**: 管理全局按键绑定系统，支持和弦（chord）和上下文优先级。

**核心类型**:
```typescript
type KeybindingContextValue = {
  resolve: (input: string, key: Key, activeContexts: KeybindingContextName[]) 
    => ChordResolveResult;
  setPendingChord: (pending: ParsedKeystroke[] | null) => void;
  getDisplayText: (action: string, context: KeybindingContextName) 
    => string | undefined;
  bindings: ParsedBinding[];
  pendingChord: ParsedKeystroke[] | null;
  activeContexts: Set<KeybindingContextName>;
  registerActiveContext: (context: KeybindingContextName) => void;
  unregisterActiveContext: (context: KeybindingContextName) => void;
  registerHandler: (registration: HandlerRegistration) => () => void;
  invokeAction: (action: string) => boolean;
};
```

**Provider 实现**:
```typescript
const KeybindingContext = createContext<KeybindingContextValue | null>(null);

export function KeybindingProvider({
  bindings,
  pendingChordRef,
  pendingChord,
  setPendingChord,
  activeContexts,
  registerActiveContext,
  unregisterActiveContext,
  handlerRegistryRef,
  children,
}: ProviderProps): React.ReactNode {
  const value = useMemo<KeybindingContextValue>(() => {
    const getDisplay = (action: string, context: KeybindingContextName) =>
      getBindingDisplayText(action, context, bindings);
    
    const registerHandler = (registration: HandlerRegistration) => {
      const registry = handlerRegistryRef.current;
      if (!registry) return () => {};
      
      if (!registry.has(registration.action)) {
        registry.set(registration.action, new Set());
      }
      registry.get(registration.action)!.add(registration);
      
      return () => {
        const handlers = registry.get(registration.action);
        if (handlers) {
          handlers.delete(registration);
          if (handlers.size === 0) {
            registry.delete(registration.action);
          }
        }
      };
    };
    
    const invokeAction = (action: string): boolean => {
      const registry = handlerRegistryRef.current;
      if (!registry) return false;
      
      const handlers = registry.get(action);
      if (!handlers || handlers.size === 0) return false;
      
      for (const registration of handlers) {
        if (activeContexts.has(registration.context)) {
          registration.handler();
          return true;
        }
      }
      return false;
    };
    
    return {
      resolve: (input, key, contexts) =>
        resolveKeyWithChordState(
          input, key, contexts, bindings, pendingChordRef.current
        ),
      setPendingChord,
      getDisplayText: getDisplay,
      bindings,
      pendingChord,
      activeContexts,
      registerActiveContext,
      unregisterActiveContext,
      registerHandler,
      invokeAction,
    };
  }, [
    bindings,
    pendingChordRef,
    pendingChord,
    setPendingChord,
    activeContexts,
    registerActiveContext,
    unregisterActiveContext,
    handlerRegistryRef,
  ]);
  
  return (
    <KeybindingContext.Provider value={value}>
      {children}
    </KeybindingContext.Provider>
  );
}
```

**Consumer Hooks**:

#### useKeybindingContext - 获取完整上下文
```typescript
export function useKeybindingContext(): KeybindingContextValue {
  const ctx = useContext(KeybindingContext);
  if (!ctx) {
    throw new Error("useKeybindingContext must be used within KeybindingProvider");
  }
  return ctx;
}
```

#### useOptionalKeybindingContext - 可选版本
```typescript
export function useOptionalKeybindingContext(): KeybindingContextValue | null {
  return useContext(KeybindingContext);
}
```

#### useRegisterKeybindingContext - 注册活动上下文
```typescript
export function useRegisterKeybindingContext(
  context: KeybindingContextName,
  isActive: boolean = true,
): void {
  const keybindingContext = useOptionalKeybindingContext();
  
  useLayoutEffect(() => {
    if (!keybindingContext || !isActive) return;
    
    keybindingContext.registerActiveContext(context);
    return () => {
      keybindingContext.unregisterActiveContext(context);
    };
  }, [context, keybindingContext, isActive]);
}
```

### 2.7 PromptOverlayProvider - 提示覆盖层

**文件**: `context/promptOverlayContext.tsx`

**职责**: 管理浮动在输入提示上方的覆盖层内容（slash-command 建议、对话框）。

**核心类型**:
```typescript
export type PromptOverlayData = {
  suggestions: SuggestionItem[];
  selectedSuggestion: number;
  maxColumnWidth?: number;
};
```

**Provider 实现**:
```typescript
const DataContext = createContext<PromptOverlayData | null>(null);
const SetContext = createContext<Setter<PromptOverlayData> | null>(null);
const DialogContext = createContext<ReactNode>(null);
const SetDialogContext = createContext<Setter<ReactNode> | null>(null);

export function PromptOverlayProvider({
  children,
}: { children: ReactNode }): ReactNode {
  const [data, setData] = useState<PromptOverlayData | null>(null);
  const [dialog, setDialog] = useState<ReactNode>(null);
  
  return (
    <SetContext.Provider value={setData}>
      <SetDialogContext.Provider value={setDialog}>
        <DataContext.Provider value={data}>
          <DialogContext.Provider value={dialog}>
            {children}
          </DialogContext.Provider>
        </DataContext.Provider>
      </SetDialogContext.Provider>
    </SetContext.Provider>
  );
}
```

**Consumer Hooks**:

#### usePromptOverlay - 获取建议数据
```typescript
export function usePromptOverlay(): PromptOverlayData | null {
  return useContext(DataContext);
}
```

#### usePromptOverlayDialog - 获取对话框
```typescript
export function usePromptOverlayDialog(): ReactNode {
  return useContext(DialogContext);
}
```

#### useSetPromptOverlay - 设置建议数据
```typescript
export function useSetPromptOverlay(data: PromptOverlayData | null): void {
  const set = useContext(SetContext);
  useEffect(() => {
    if (!set) return;
    set(data);
    return () => set(null);
  }, [set, data]);
}
```

#### useSetPromptOverlayDialog - 设置对话框
```typescript
export function useSetPromptOverlayDialog(node: ReactNode): void {
  const set = useContext(SetDialogContext);
  useEffect(() => {
    if (!set) return;
    set(node);
    return () => set(null);
  }, [set, node]);
}
```

### 2.8 ModalContext - 模态框

**文件**: `context/modalContext.tsx`

**职责**: 提供模态框内部的空间信息，用于正确计算可用行/列。

**核心类型**:
```typescript
type ModalCtx = {
  rows: number;
  columns: number;
  scrollRef: RefObject<ScrollBoxHandle | null> | null;
};
```

**Provider 实现**:
```typescript
export const ModalContext = createContext<ModalCtx | null>(null);
```

**Consumer Hooks**:

#### useIsInsideModal - 检查是否在模态框内
```typescript
export function useIsInsideModal(): boolean {
  return useContext(ModalContext) !== null;
}
```

#### useModalOrTerminalSize - 获取模态框或终端尺寸
```typescript
export function useModalOrTerminalSize(fallback: {
  rows: number;
  columns: number;
}): { rows: number; columns: number } {
  const ctx = useContext(ModalContext);
  return ctx 
    ? { rows: ctx.rows, columns: ctx.columns }
    : fallback;
}
```

#### useModalScrollRef - 获取滚动引用
```typescript
export function useModalScrollRef(): RefObject<ScrollBoxHandle | null> | null {
  return useContext(ModalContext)?.scrollRef ?? null;
}
```

### 2.9 ClockProvider - 时钟/动画

**文件**: `ink/components/ClockContext.tsx`

**职责**: 提供同步的时钟信号，用于动画和定时更新。

**核心类型**:
```typescript
export type Clock = {
  subscribe: (onChange: () => void, keepAlive: boolean) => () => void;
  now: () => number;
  setTickInterval: (ms: number) => void;
};
```

**createClock 实现**:
```typescript
export function createClock(tickIntervalMs: number): Clock {
  const subscribers = new Map<() => void, boolean>();
  let interval: ReturnType<typeof setInterval> | null = null;
  let currentTickIntervalMs = tickIntervalMs;
  let startTime = 0;
  let tickTime = 0;
  
  function tick(): void {
    tickTime = Date.now() - startTime;
    for (const onChange of subscribers.keys()) {
      onChange();
    }
  }
  
  function updateInterval(): void {
    const anyKeepAlive = [...subscribers.values()].some(Boolean);
    
    if (anyKeepAlive) {
      if (interval) {
        clearInterval(interval);
        interval = null;
      }
      if (startTime === 0) {
        startTime = Date.now();
      }
      interval = setInterval(tick, currentTickIntervalMs);
    } else if (interval) {
      clearInterval(interval);
      interval = null;
    }
  }
  
  return {
    subscribe(onChange, keepAlive) {
      subscribers.set(onChange, keepAlive);
      updateInterval();
      return () => {
        subscribers.delete(onChange);
        updateInterval();
      };
    },
    now() {
      if (startTime === 0) {
        startTime = Date.now();
      }
      if (interval && tickTime) {
        return tickTime;
      }
      return Date.now() - startTime;
    },
    setTickInterval(ms) {
      if (ms === currentTickIntervalMs) return;
      currentTickIntervalMs = ms;
      updateInterval();
    },
  };
}
```

**Provider 实现**:
```typescript
export const ClockContext = createContext<Clock | null>(null);
const BLURRED_TICK_INTERVAL_MS = FRAME_INTERVAL_MS * 2;

export function ClockProvider({ children }: { children: ReactNode }): ReactNode {
  const [clock] = useState(() => createClock(FRAME_INTERVAL_MS));
  const focused = useTerminalFocus();
  
  useEffect(() => {
    clock.setTickInterval(
      focused ? FRAME_INTERVAL_MS : BLURRED_TICK_INTERVAL_MS
    );
  }, [clock, focused]);
  
  return (
    <ClockContext.Provider value={clock}>
      {children}
    </ClockContext.Provider>
  );
}
```

### 2.10 TerminalSizeContext - 终端尺寸

**文件**: `ink/components/TerminalSizeContext.tsx`

**职责**: 提供终端的行列数信息。

**实现**:
```typescript
export type TerminalSize = {
  columns: number;
  rows: number;
};

export const TerminalSizeContext = createContext<TerminalSize | null>(null);
```

### 2.11 TerminalFocusProvider - 终端焦点

**文件**: `ink/components/TerminalFocusContext.tsx`

**职责**: 追踪终端焦点状态。

**实现**:
```typescript
export type TerminalFocusContextProps = {
  readonly isTerminalFocused: boolean;
  readonly terminalFocusState: TerminalFocusState;
};

const TerminalFocusContext = createContext<TerminalFocusContextProps>({
  isTerminalFocused: true,
  terminalFocusState: 'unknown',
});

export function TerminalFocusProvider({
  children,
}: { children: ReactNode }): ReactNode {
  const isTerminalFocused = useSyncExternalStore(
    subscribeTerminalFocus,
    getTerminalFocused
  );
  const terminalFocusState = useSyncExternalStore(
    subscribeTerminalFocus,
    getTerminalFocusState
  );
  
  const value = useMemo(
    () => ({ isTerminalFocused, terminalFocusState }),
    [isTerminalFocused, terminalFocusState]
  );
  
  return (
    <TerminalFocusContext.Provider value={value}>
      {children}
    </TerminalFocusContext.Provider>
  );
}
```

### 2.12 ExpandShellOutputContext - Shell 输出扩展

**文件**: `components/shell/ExpandShellOutputContext.tsx`

**职责**: 指示 shell 输出应完整显示（不截断）。

**实现**:
```typescript
const ExpandShellOutputContext = React.createContext(false);

export function ExpandShellOutputProvider({
  children,
}: { children: ReactNode }): ReactNode {
  return (
    <ExpandShellOutputContext.Provider value={true}>
      {children}
    </ExpandShellOutputContext.Provider>
  );
}

export function useExpandShellOutput(): boolean {
  return useContext(ExpandShellOutputContext);
}
```

### 2.13 WizardProvider - 向导流程

**文件**: `components/wizard/WizardProvider.tsx`

**职责**: 管理多步骤向导流程的状态和导航。

**核心类型**:
```typescript
type WizardContextValue<T> = {
  currentStepIndex: number;
  totalSteps: number;
  wizardData: T;
  setWizardData: React.Dispatch<React.SetStateAction<T>>;
  updateWizardData: (updates: Partial<T>) => void;
  goNext: () => void;
  goBack: () => void;
  goToStep: (index: number) => void;
  cancel: () => void;
  title: string;
  showStepCounter: boolean;
};
```

**Provider 实现（关键部分）**:
```typescript
export const WizardContext = createContext<WizardContextValue<any> | null>(null);

export function WizardProvider<T extends Record<string, unknown>>({
  steps,
  initialData = {} as T,
  onComplete,
  onCancel,
  children,
  title,
  showStepCounter = true,
}: WizardProviderProps<T>): ReactNode {
  const [currentStepIndex, setCurrentStepIndex] = useState(0);
  const [wizardData, setWizardData] = useState<T>(initialData);
  const [isCompleted, setIsCompleted] = useState(false);
  const [navigationHistory, setNavigationHistory] = useState<number[]>([]);
  
  // 完成时回调
  useEffect(() => {
    if (isCompleted) {
      setNavigationHistory([]);
      onComplete(wizardData);
    }
  }, [isCompleted, wizardData, onComplete]);
  
  // 前进
  const goNext = useCallback(() => {
    if (currentStepIndex < steps.length - 1) {
      if (navigationHistory.length > 0) {
        setNavigationHistory(prev => [...prev, currentStepIndex]);
      }
      setCurrentStepIndex(prev => prev + 1);
    } else {
      setIsCompleted(true);
    }
  }, [currentStepIndex, steps.length, navigationHistory]);
  
  // 后退
  const goBack = useCallback(() => {
    if (navigationHistory.length > 0) {
      const previousStep = navigationHistory[navigationHistory.length - 1];
      if (previousStep !== undefined) {
        setNavigationHistory(prev => prev.slice(0, -1));
        setCurrentStepIndex(previousStep);
      }
    } else if (currentStepIndex > 0) {
      setCurrentStepIndex(prev => prev - 1);
    } else if (onCancel) {
      onCancel();
    }
  }, [currentStepIndex, navigationHistory, onCancel]);
  
  // 跳转到指定步骤
  const goToStep = useCallback(
    (index: number) => {
      if (index >= 0 && index < steps.length) {
        setNavigationHistory(prev => [...prev, currentStepIndex]);
        setCurrentStepIndex(index);
      }
    },
    [currentStepIndex, steps.length]
  );
  
  // 取消
  const cancel = useCallback(() => {
    setNavigationHistory([]);
    if (onCancel) {
      onCancel();
    }
  }, [onCancel]);
  
  // 更新向导数据
  const updateWizardData = useCallback((updates: Partial<T>) => {
    setWizardData(prev => ({ ...prev, ...updates }));
  }, []);
  
  const contextValue = useMemo<WizardContextValue<T>>(() => ({
    currentStepIndex,
    totalSteps: steps.length,
    wizardData,
    setWizardData,
    updateWizardData,
    goNext,
    goBack,
    goToStep,
    cancel,
    title,
    showStepCounter,
  }), [
    currentStepIndex,
    steps.length,
    wizardData,
    updateWizardData,
    goNext,
    goBack,
    goToStep,
    cancel,
    title,
    showStepCounter,
  ]);
  
  const CurrentStepComponent = steps[currentStepIndex];
  
  if (!CurrentStepComponent || isCompleted) {
    return null;
  }
  
  return (
    <WizardContext.Provider value={contextValue}>
      {children || <CurrentStepComponent />}
    </WizardContext.Provider>
  );
}
```

### 2.14 OverlayContext - 覆盖层跟踪

**文件**: `context/overlayContext.tsx`

**职责**: 跟踪活动覆盖层，用于 Escape 键协调。

**Consumer Hooks**:

#### useRegisterOverlay - 注册覆盖层
```typescript
export function useRegisterOverlay(id: string, enabled = true): void {
  const store = useContext(AppStoreContext);
  const setAppState = store?.setState;
  
  useEffect(() => {
    if (!enabled || !setAppState) return;
    
    setAppState(prev => {
      if (prev.activeOverlays.has(id)) return prev;
      const next = new Set(prev.activeOverlays);
      next.add(id);
      return { ...prev, activeOverlays: next };
    });
    
    return () => {
      setAppState(prev => {
        if (!prev.activeOverlays.has(id)) return prev;
        const next = new Set(prev.activeOverlays);
        next.delete(id);
        return { ...prev, activeOverlays: next };
      });
    };
  }, [id, enabled, setAppState]);
  
  // 强制下一帧完全 diff
  useLayoutEffect(() => {
    if (!enabled) return;
    return () => instances.get(process.stdout)?.invalidatePrevFrame();
  }, [enabled]);
}
```

#### useIsOverlayActive - 检查是否有覆盖层活动
```typescript
export function useIsOverlayActive(): boolean {
  return useAppState(s => s.activeOverlays.size > 0);
}
```

#### useIsModalOverlayActive - 检查是否有模态覆盖层活动
```typescript
export function useIsModalOverlayActive(): boolean {
  return useAppState(s => {
    for (const id of s.activeOverlays) {
      if (!NON_MODAL_OVERLAYS.has(id)) return true;
    }
    return false;
  });
}
```

### 2.15 QueuedMessageContext - 队列消息

**文件**: `context/QueuedMessageContext.tsx`

**职责**: 为队列消息提供上下文信息（是否是第一个、padding 等）。

**实现**:
```typescript
type QueuedMessageContextValue = {
  isQueued: boolean;
  isFirst: boolean;
  paddingWidth: number;
};

const QueuedMessageContext = React.createContext<
  QueuedMessageContextValue | undefined
>(undefined);

const PADDING_X = 2;

export function QueuedMessageProvider({
  isFirst,
  useBriefLayout,
  children,
}: Props): ReactNode {
  const padding = useBriefLayout ? 0 : PADDING_X;
  const value = React.useMemo(
    () => ({ isQueued: true, isFirst, paddingWidth: padding * 2 }),
    [isFirst, padding]
  );
  
  return (
    <QueuedMessageContext.Provider value={value}>
      <Box paddingX={padding}>{children}</Box>
    </QueuedMessageContext.Provider>
  );
}

export function useQueuedMessage(): QueuedMessageContextValue | undefined {
  return React.useContext(QueuedMessageContext);
}
```

### 2.16 FpsMetricsProvider - FPS 指标

**文件**: `context/fpsMetrics.tsx`

**职责**: 提供 FPS 性能指标的 getter。

**实现**:
```typescript
type FpsMetricsGetter = () => FpsMetrics | undefined;

const FpsMetricsContext = createContext<FpsMetricsGetter | undefined>(undefined);

export function FpsMetricsProvider({
  getFpsMetrics,
  children,
}: Props): ReactNode {
  return (
    <FpsMetricsContext.Provider value={getFpsMetrics}>
      {children}
    </FpsMetricsContext.Provider>
  );
}

export function useFpsMetrics(): FpsMetricsGetter | undefined {
  return useContext(FpsMetricsContext);
}
```

---

## 3. Context 使用模式总结

### 3.1 基础 Context 模式
```typescript
const MyContext = createContext<T | null>(null);

export function MyProvider({ children }: Props) {
  const value = useMemo(() => createValue(), []);
  return (
    <MyContext.Provider value={value}>
      {children}
    </MyContext.Provider>
  );
}

export function useMyContext(): T {
  const ctx = useContext(MyContext);
  if (!ctx) {
    throw new Error("useMyContext must be used within MyProvider");
  }
  return ctx;
}
```

### 3.2 Store + useSyncExternalStore 模式
```typescript
const StoreContext = createContext<Store<T> | null>(null);

export function useStoreState<T, R>(
  selector: (state: T) => R
): R {
  const store = useStore();
  const get = () => selector(store.getState());
  return useSyncExternalStore(store.subscribe, get, get);
}
```

### 3.3 Data/Setter 分离模式
```typescript
const DataContext = createContext<Data | null>(null);
const SetContext = createContext<Setter<Data> | null>(null);

// 写入者不会因自己的写入而重新渲染
```

### 3.4 嵌套 Provider 模式
```typescript
function AppStateProvider({ children }) {
  return (
    <HasAppStateContext.Provider value={true}>
      <AppStoreContext.Provider value={store}>
        <MailboxProvider>
          <VoiceProvider>{children}</VoiceProvider>
        </MailboxProvider>
      </AppStoreContext.Provider>
    </HasAppStateContext.Provider>
  );
}
```

---

## 4. 关键设计原则

1. **稳定性**: Provider 值使用 `useMemo` 缓存，避免不必要的重新渲染
2. **性能**: 使用 `useSyncExternalStore` 订阅状态切片，只在选择值变化时重新渲染
3. **类型安全**: 所有 Context 都有明确的类型定义
4. **错误处理**: Consumer hooks 检查 Context 是否存在并抛出有意义的错误
5. **分离关注点**: Data/Setter 分离，写入者不会因自己的写入而重新渲染
6. **嵌套保护**: AppStateProvider 检查是否被嵌套并抛出错误

---

*文档持续更新中...*
