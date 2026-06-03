# 05 — Context System

## Overview

The context system provides React Context providers and hooks for cross-cutting concerns in the CLI application. It covers UI state management (FPS metrics, notifications, overlays, modals, voice), inter-component messaging (mailbox), and in-memory metrics (stats).

---

## 1. `context/fpsMetrics.tsx` (30 lines) — FPS Metrics Context

### Purpose
Provides a React Context for accessing FPS (frames per second) metrics tracked by the `FpsTracker` utility. Instead of storing the metrics object directly (which would cause re-renders on every frame), it stores a getter function that consumers call imperatively to read the latest value.

### Architecture
- `FpsMetricsContext` — `createContext<FpsMetricsGetter | undefined>(undefined)` where `FpsMetricsGetter = () => FpsMetrics | undefined`
- `FpsMetricsProvider` — wraps children with the context, passing the getter as value
- `useFpsMetrics()` — returns the getter function or undefined

### Usage Pattern
```typescript
const getFps = useFpsMetrics()
// Imperative read — no subscription, no re-render on frame
const current = getFps?.()
```

---

## 2. `context/mailbox.tsx` (38 lines) — Mailbox Context

### Purpose
Provides a singleton `Mailbox` instance for inter-component messaging across the Ink render tree. The Mailbox is an event-emitter-like pattern used for communication between components that don't share a direct parent-child relationship (e.g., toolbar buttons to the main transcript).

### Architecture
- `MailboxContext` — `createContext<Mailbox | undefined>(undefined)`
- `MailboxProvider` — creates a `Mailbox` instance via `useMemo(() => new Mailbox(), [])` and provides it to children
- `useMailbox()` — returns the Mailbox instance, throws if used outside provider

### Design Notes
- The Mailbox singleton is stable (created once via useMemo with empty deps)
- Strict error boundary: throws `"useMailbox must be used within a MailboxProvider"` if context is missing — no optional chaining, no graceful degradation

---

## 3. `context/modalContext.tsx` (58 lines) — Modal Dialog Sizing

### Purpose
Provides context-aware terminal dimensions for components rendered inside the modal slot of `FullscreenLayout`. The modal slot is an absolute-positioned bottom-anchored pane for slash-command dialogs. Its inner area is smaller than the full terminal (rows minus transcript peek minus divider), so components that cap their visible option count need adjusted dimensions.

### Key Types
```typescript
type ModalCtx = {
  rows: number
  columns: number
  scrollRef: RefObject<ScrollBoxHandle | null> | null
}
```

### Exports
- `ModalContext` — `createContext<ModalCtx | null>(null)` (null = not inside modal slot)
- `useIsInsideModal()` — returns true if context is non-null
- `useModalOrTerminalSize(fallback)` — returns `{ rows, columns }` from context if available, else the fallback terminal size
- `useModalScrollRef()` — returns the scroll ref from context or null

### Use Cases
- Suppress top-level framing: `Pane` skips its full-terminal-width Divider (FullscreenLayout already draws the ▔ divider)
- Size Select pagination: components use modal rows instead of `useTerminalSize().rows` to avoid overflow
- Reset scroll on tab switch: Tabs keys its ScrollBox by `selectedTabIndex`, remounting on tab switch

---

## 4. `context/notifications.tsx` (240 lines) — Notification Queue System

### Purpose
Manages a priority-based notification queue with folding, timeout, and invalidation. Used for status bar notifications (tool completions, errors, warnings) displayed in the REPL footer.

### Key Types

```typescript
type Priority = 'low' | 'medium' | 'high' | 'immediate'

type BaseNotification = {
  key: string
  invalidates?: string[]          // keys to remove when this fires
  priority: Priority
  timeoutMs?: number               // default: DEFAULT_TIMEOUT_MS=8000
  fold?: (accumulator, incoming) => Notification  // combine same-key notifications
}

type TextNotification = BaseNotification & { text: string; color?: keyof Theme }
type JSXNotification = BaseNotification & { jsx: React.ReactNode }
type Notification = TextNotification | JSXNotification
```

### Hook: `useNotifications()`
Returns `{ addNotification, removeNotification }`.

#### `addNotification(notif: Notification)`
Three branches based on priority:

**Immediate priority:**
1. Clears any existing timeout
2. Sets up a new timeout that clears the notification after `timeoutMs`
3. Immediately sets the notification as `current` in app state
4. Re-queues the previous current notification (if any) unless it's also immediate
5. Filters out invalidated notifications from the queue

**Non-immediate priority (with fold):**
1. If current notification has matching key: folds them together, resets timeout
2. If queued notification has matching key: folds in-place
3. Otherwise: prevents duplicates (checks both current and queue by key)

**Non-immediate priority (no fold):**
1. Prevents duplicates (checks both current and queue by key)
2. If invalidates current: clears its timeout, sets current to null
3. Filters out invalidated notifications from the queue
4. Adds notification to queue, then calls `processQueue()`

#### `removeNotification(key: string)`
If key matches current or is in queue: removes it. If current, also clears timeout.

#### `processQueue()`
Called after every add/remove. Uses `getNext()` to find the highest-priority notification in the queue, moves it to current, starts its timeout.

### Free Function: `getNext(queue: Notification[]): Notification | undefined`
Finds the highest-priority notification using `PRIORITIES` mapping:
```typescript
const PRIORITIES = { immediate: 0, high: 1, medium: 2, low: 3 }
```

### Design Notes
- `currentTimeoutId` is a module-level `let` — deliberately outside React state so it's imperatively controlled
- Timeouts carry closure arguments via `setTimeout(callback, delay, arg1, arg2, ...)` to avoid stale closures
- Fold pattern: `fold(accumulator, incoming) => Notification` — like Array.reduce(), enables progressive text accumulation ("N tools running" → "N+1 tools running")

---

## 5. `context/overlayContext.tsx` (151 lines) — Escape Key Coordination

### Purpose
Tracks active overlay IDs to coordinate Escape key handling. When overlays (like Select with onCancel) are open, the CancelRequestHandler needs to know so it doesn't cancel the running request when the user just wants to dismiss the overlay.

### Architecture
- Overlay IDs are stored in `AppState.activeOverlays: Set<string>`
- `useRegisterOverlay(id, enabled?)` — registers on mount, unregisters on unmount
- `useIsOverlayActive()` — returns `activeOverlays.size > 0`
- `useIsModalOverlayActive()` — returns true if any overlay NOT in `NON_MODAL_OVERLAYS` set is active

### Non-Modal Overlays
```typescript
const NON_MODAL_OVERLAYS = new Set(['autocomplete'])
```
Autocomplete is non-modal — it shouldn't disable TextInput focus. Modal overlays (like Select dialogs) capture all input.

### Hook Details

#### `useRegisterOverlay(id, enabled = true)`
- `useEffect` for mount/unmount registration (async-safe)
- `useLayoutEffect` for frame invalidation on overlay close (synchronous, prevents render flash on Escape)
- When enabled is false: no registration (for conditional overlays, e.g., only register Select when `onCancel` is provided)

#### `useIsOverlayActive()`
Selects `s.activeOverlays.size > 0` from AppState. Reactive — re-renders when overlay state changes.

#### `useIsModalOverlayActive()`
Iterates active overlays, returns true if any is NOT in `NON_MODAL_OVERLAYS`. Used for TextInput focus decisions.

---

## 6. `context/promptOverlayContext.tsx` (125 lines) — Prompt Floating Overlay

### Purpose
Portal for content that floats above the prompt, escaping FullscreenLayout's `overflowY:hidden` clip. The clip is load-bearing (tall pastes would squash the ScrollBox without it), but floating overlays use `position:absolute; bottom:100%` — and Ink's clip stack intersects ALL descendants, clipping them to ~1 row.

### Two Channels
- **Data channel** (`PromptOverlayData`): Slash-command suggestion data (structured — `{ suggestions, selectedSuggestion, maxColumnWidth }`), written by `PromptInputFooter`
- **Dialog channel** (`ReactNode`): Arbitrary dialog node (e.g., `AutoModeOptInDialog`), written by `PromptInput`

### Context Split Pattern
Split into data/setter context pairs so writers never re-render on their own writes:
- `DataContext` / `SetContext` — suggestion data
- `DialogContext` / `SetDialogContext` — dialog node

### Exports
- `PromptOverlayProvider` — wraps children with all four contexts
- `usePromptOverlay()` — reads suggestion data
- `usePromptOverlayDialog()` — reads dialog node
- `useSetPromptOverlay(data)` — writes suggestion data, clears on unmount (no-op outside provider)
- `useSetPromptOverlayDialog(node)` — writes dialog node, clears on unmount (no-op outside provider)

### Design Notes
- `FullscreenLayout` reads both contexts and renders them outside the clipped bottom slot
- Setter contexts are stable (the setter function reference never changes), so writers don't re-render on their own writes

---

## 7. `context/QueuedMessageContext.tsx` (63 lines) — Queued Message Context

### Purpose
Provides context to message renderers indicating whether a message is queued (waiting to be rendered) and whether it's the first in the queue. This controls indentation/padding so queued messages visually group together.

### Key Types
```typescript
type QueuedMessageContextValue = {
  isQueued: boolean
  isFirst: boolean
  paddingWidth: number  // e.g., 4 for paddingX={2}
}
```

### Exports
- `QueuedMessageProvider` — wraps children with `Box paddingX={padding}` and the context value. Brief layout mode (for HighlightedThinkingText/BriefTool UI) uses `paddingX=0` to avoid double-indenting.
- `useQueuedMessage()` — returns the context value or undefined

---

## 8. `context/stats.tsx` (220 lines) — In-Memory Metrics Store

### Purpose
In-memory metrics store for session-level statistics. Supports counters, gauges, histograms, and sets. Metrics are flushed to project config (`lastSessionMetrics`) on process exit.

### Key Types

```typescript
type StatsStore = {
  increment(name: string, value?: number): void
  set(name: string, value: number): void
  observe(name: string, value: number): void
  add(name: string, value: string): void
  getAll(): Record<string, number>
}
```

### `createStatsStore(): StatsStore`
Creates a store with four metric types backed by Maps:

**`increment(name, value=1)`**
Simple counter. `metrics.set(name, (get(name) ?? 0) + value)`

**`set(name, value)`**
Gauge — overwrites previous value.

**`observe(name, value)`**
Histogram with reservoir sampling (Algorithm R, `RESERVOIR_SIZE=1024`). Tracks count, sum, min, max plus a uniform random sample reservoir. On `getAll()`, computes `_count`, `_min`, `_max`, `_avg`, `_p50`, `_p95`, `_p99`.

**`add(name, value)`**
Set cardinality. Stores unique string values, reports set size on `getAll()`.

### React Integration
- `StatsContext` — `createContext<StatsStore | null>(null)`
- `StatsProvider` — creates internal store (or uses external), registers `process.on('exit')` flush to `saveCurrentProjectConfig({ lastSessionMetrics })`
- `useStats()` — returns store, throws if outside provider

### Convenience Hooks
- `useCounter(name)` — returns `(value?) => store.increment(name, value)`
- `useGauge(name)` — returns `(value) => store.set(name, value)`
- `useTimer(name)` — returns `(value) => store.observe(name, value)`
- `useSet(name)` — returns `(value) => store.add(name, value)`

Each hook is a stable function reference memoized by `[name, store]`.

---

## 9. `context/voice.tsx` (88 lines) — Voice State Store

### Purpose
Manages voice input state: idle, recording, processing. Uses a simple store pattern (not full zustand) with `useSyncExternalStore` for React integration.

### Key Types

```typescript
type VoiceState = {
  voiceState: 'idle' | 'recording' | 'processing'
  voiceError: string | null
  voiceInterimTranscript: string
  voiceAudioLevels: number[]
  voiceWarmingUp: boolean
}
```

Default: `{ voiceState: 'idle', voiceError: null, voiceInterimTranscript: '', voiceAudioLevels: [], voiceWarmingUp: false }`

### Exports
- `VoiceProvider` — creates store once (stable context value, never triggers provider re-renders)
- `useVoiceState(selector)` — subscribes to a slice via `useSyncExternalStore`, only re-renders when the selected value changes (Object.is comparison)
- `useSetVoiceState()` — returns `store.setState` (stable reference, synchronous)
- `useGetVoiceState()` — returns `store.getState` (stable reference, for imperative reads in callbacks)

### Design Notes
- `store.setState` is synchronous: callers can read `getVoiceState()` immediately after to observe the new value (VoiceKeybindingHandler relies on this)
- `useGetVoiceState()` doesn't cause re-renders — intended for event handlers that need to read state set earlier in the same tick

---

## Architecture Summary

```
App Root
├── FpsMetricsProvider      → useFpsMetrics()        (imperative getter)
├── MailboxProvider          → useMailbox()            (event bus)
├── StatsProvider            → useStats()              (metrics store)
│   ├── useCounter(name)     → increment(value?)
│   ├── useGauge(name)       → set(value)
│   ├── useTimer(name)       → observe(value)          (histogram)
│   └── useSet(name)         → add(value)              (cardinality)
├── VoiceProvider            → useVoiceState(selector) (subscription)
│   ├── useSetVoiceState()   → setState(partial)
│   └── useGetVoiceState()   → getState()              (imperative)
├── QueuedMessageProvider    → useQueuedMessage()      (render hint)
├── ModalContext             → useModalOrTerminalSize()(sizing)
│                           → useModalScrollRef()
├── PromptOverlayProvider    → usePromptOverlay()      (data)
│                           → usePromptOverlayDialog() (dialog)
│                           → useSetPromptOverlay()    (write data)
│                           → useSetPromptOverlayDialog()(write dialog)
└── Overlay System (AppState)
    ├── useRegisterOverlay(id)→ activeOverlays.add(id)
    ├── useIsOverlayActive() → activeOverlays.size > 0
    └── useIsModalOverlayActive() → non-autocomplete active

Notification System (not context, but hooks-based)
    useNotifications() → { addNotification, removeNotification }
    Priority: immediate > high > medium > low
    Features: fold, invalidate, timeout, processQueue
```
