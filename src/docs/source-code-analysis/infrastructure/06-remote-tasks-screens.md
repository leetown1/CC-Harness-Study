# 06 — Remote, Tasks, Screens, Server, Migrations & Supporting Modules

## Overview

This document covers the remote session subsystem, task management (background processes), the main REPL screen, diagnostic utilities, server infrastructure, data migrations, and several standalone support modules that complete the application infrastructure.

---

# Part A: Remote System (4 files)

## A.1 `remote/RemoteSessionManager.ts` (343 lines) — CCR Session Lifecycle

### Purpose
Orchestrates a remote CCR (Claude Code Remote) session. Coordinates WebSocket subscription for receiving messages from CCR, HTTP POST for sending user messages, and the permission request/response flow.

### Key Types

```typescript
type RemoteSessionConfig = {
  sessionId: string
  getAccessToken: () => string   // fresh token per call
  orgUuid: string
  hasInitialPrompt?: boolean
  viewerOnly?: boolean            // true = pure viewer, no Ctrl+C interrupt
}

type RemoteSessionCallbacks = {
  onMessage: (message: SDKMessage) => void
  onPermissionRequest: (request: SDKControlPermissionRequest, requestId: string) => void
  onPermissionCancelled?: (requestId: string, toolUseId?: string) => void
  onConnected?: () => void
  onDisconnected?: () => void
  onReconnecting?: () => void
  onError?: (error: Error) => void
}

type RemotePermissionResponse =
  | { behavior: 'allow'; updatedInput: Record<string, unknown> }
  | { behavior: 'deny'; message: string }
```

### Class: `RemoteSessionManager`

**Constructor** — takes `config` and `callbacks`, initializes empty `pendingPermissionRequests` Map.

**`connect(): void`** — Creates a `SessionsWebSocket` instance with callbacks wrapping `handleMessage`, then calls `ws.connect()`. Delegates all transport concerns to `SessionsWebSocket`.

**`handleMessage(message): void`** — Message dispatch:
1. `control_request` → `handleControlRequest()` (permission prompts from CCR)
2. `control_cancel_request` → removes from `pendingPermissionRequests`, calls `onPermissionCancelled`
3. `control_response` → debug-logged, ignored (acknowledgments)
4. SDK messages (type guard `isSDKMessage`) → forwarded to `callbacks.onMessage`

**`handleControlRequest(request): void`**
- `subtype === 'can_use_tool'` → stores in `pendingPermissionRequests`, calls `callbacks.onPermissionRequest`
- Other subtypes → sends error control_response so server doesn't hang

**`sendMessage(content, opts?): Promise<boolean>`** — Sends via `sendEventToRemoteSession()` HTTP POST.

**`respondToPermissionRequest(requestId, result): void`**
Looks up pending request, deletes it, sends `SDKControlResponse` via WebSocket. Response shape depends on `behavior`:
- `allow` → `{ behavior: 'allow', updatedInput }`
- `deny` → `{ behavior: 'deny', message }`

**`cancelSession(): void`** — Sends `{ subtype: 'interrupt' }` control request.

**`disconnect(): void`** — Closes WebSocket, clears pending permission requests.

**`reconnect(): void`** — Force reconnects WebSocket (useful after container shutdown).

**`isConnected(): boolean`**, **`getSessionId(): string`** — Simple accessors.

### Factory: `createRemoteSessionConfig()`
Creates config from OAuth tokens (`sessionId`, `getAccessToken`, `orgUuid`, `hasInitialPrompt`, `viewerOnly`).

---

## A.2 `remote/SessionsWebSocket.ts` (404 lines) — WebSocket Client

### Purpose
Low-level WebSocket client for connecting to CCR sessions via `/v1/sessions/ws/{sessionId}/subscribe`. Handles connection lifecycle, exponential reconnect, ping keepalive, and transient 4001 retries.

### Protocol
1. Connect to `wss://api.anthropic.com/v1/sessions/ws/{sessionId}/subscribe?organization_uuid=...`
2. Auth via Headers (`Authorization: Bearer {token}`) — no separate auth message needed
3. Receive SDKMessage stream from the session

### Constants
```typescript
RECONNECT_DELAY_MS = 2000
MAX_RECONNECT_ATTEMPTS = 5
PING_INTERVAL_MS = 30000
MAX_SESSION_NOT_FOUND_RETRIES = 3    // for transient 4001 during compaction
PERMANENT_CLOSE_CODES = new Set([4003])  // unauthorized
```

### State Machine
```
connecting ──→ connected ──→ (close) ──→ closed
    │              │                        │
    └── (retry) ───┘               (permanent: stop)
```

### Class: `SessionsWebSocket`

**Constructor** — takes `sessionId`, `orgUuid`, `getAccessToken`, `callbacks`.

**`connect(): Promise<void>`** — Dual-runtime support:
- **Bun**: Uses native `globalThis.WebSocket` with headers proxy, TLS options
- **Node**: Uses `ws` package with proxy agent, TLS options

Auth is handled via HTTP headers on the WebSocket upgrade request.

**`handleMessage(data): void`** — Parses JSON, validates with `isSessionsMessage` (accepts any object with string `type` field), forwards to `callbacks.onMessage`. Unknown types are debug-logged but not rejected.

**`handleClose(closeCode): void`** — Close handling logic:
1. Stop ping interval, null out ws reference
2. `PERMANENT_CLOSE_CODES.has(closeCode)` → `onClose`, no reconnect
3. `closeCode === 4001` → Increment `sessionNotFoundRetries`, retry with backoff up to `MAX_SESSION_NOT_FOUND_RETRIES` (3 attempts), then permanent close. Delay: `RECONNECT_DELAY_MS * retryCount`.
4. Standard close → If was connected AND reconnect attempts remain, retry at `RECONNECT_DELAY_MS`. Otherwise permanent close.

**`scheduleReconnect(delay, label): void`** — Calls `onReconnecting`, sets timeout to call `connect()`.

**`startPingInterval() / stopPingInterval()`** — 30s ping keepalive using `ws.ping?.()`.

**`sendControlResponse(response): void`** — Sends `jsonStringify(response)` if connected.

**`sendControlRequest(request): void`** — Wraps in `SDKControlRequest` envelope with `randomUUID()`, sends.

**`reconnect(): void`** — Force reconnect: resets retry counters, closes, reconnects after 500ms delay.

---

## A.3 `remote/sdkMessageAdapter.ts` (302 lines) — SDK→REPL Message Conversion

### Purpose
Converts CCR SDK-format messages to internal REPL Message types. The CCR backend sends SDK-format messages via WebSocket; the REPL expects internal Message types for rendering.

### Conversion Table

| SDK Message Type | REPL Output | Notes |
|-----------------|-------------|-------|
| `assistant` | `AssistantMessage` | Direct mapping with `uuid`, `requestId: undefined`, current timestamp |
| `stream_event` | `StreamEvent` | For streaming partial responses |
| `result` (error) | `SystemMessage` (warning) | Errors joined, success results are noise → `ignored` |
| `result` (success) | `ignored` | `isLoading=false` is sufficient signal |
| `system/init` | `SystemMessage` | "Remote session initialized (model: {model})" |
| `system/status/compacting` | `SystemMessage` | "Compacting conversation…" |
| `system/status/other` | `SystemMessage` | "Status: {status}" |
| `system/compact_boundary` | `SystemMessage` (compact_boundary) | With `compactMetadata` from SDKBoundaryMetadata |
| `tool_progress` | `SystemMessage` | "Tool {name} running for {s}s…" with `toolUseID` |
| `user` with tool_result blocks | `UserMessage` | When `opts.convertToolResults` is true (direct connect mode) |
| `user` text | `UserMessage` | When `opts.convertUserTextMessages` is true (historical events) |
| `user` other | `ignored` | Already added locally by REPL in live WS mode |
| `auth_status` | `ignored` | Handled separately |
| `tool_use_summary` | `ignored` | SDK-only event |
| `rate_limit_event` | `ignored` | SDK-only event |

### Key Functions

**`convertSDKMessage(msg, opts?): ConvertedMessage`**
Main dispatch with exhaustive `switch` on `msg.type`. Returns `{ type: 'message', message }`, `{ type: 'stream_event', event }`, or `{ type: 'ignored' }`.

The `default` case gracefully ignores unknown types — the backend may send new types before the client is updated.

**`isSessionEndMessage(msg: SDKMessage): boolean`** — `msg.type === 'result'`

**`isSuccessResult(msg: SDKResultMessage): boolean`** — `msg.subtype === 'success'`

**`getResultText(msg: SDKResultMessage): string | null`** — Extracts `msg.result` from success results.

### ConvertOptions
- `convertToolResults: boolean` — Convert user messages with `tool_result` content blocks (direct connect mode)
- `convertUserTextMessages: boolean` — Convert user text messages for display (historical events)

### Design Decision: User Message Handling
In CCR mode, user-typed messages are already added locally by the REPL, so they're ignored by default. Tool result messages from the remote server need special handling to render and collapse like local tool results. Detection uses content shape (`tool_result` blocks) since `parent_tool_use_id` is not reliable.

---

## A.4 `remote/remotePermissionBridge.ts` (78 lines) — Permission Bridging

### Purpose
Creates synthetic data structures for remote permission requests. In remote mode, tool uses run on the CCR container — the local CLI doesn't have a real `AssistantMessage` or real `Tool` definition.

### Key Functions

**`createSyntheticAssistantMessage(request, requestId): AssistantMessage`**
Creates an `AssistantMessage` with:
- A single `tool_use` content block from the permission request
- Zero-value usage stats
- UUID: `remote-{requestId}`
- Empty model string

**`createToolStub(toolName): Tool`**
Creates a minimal `Tool` stub for tools not loaded locally (e.g., MCP tools on the remote). The stub:
- Has `isEnabled: () => true`, `needsPermissions: () => true`, `isReadOnly: () => false`
- `renderToolUseMessage()` renders up to 3 key-value pairs from the input
- `call()` returns `{ data: '' }` (never actually called)
- Routes to `FallbackPermissionRequest` in the permission flow

---

# Part B: Tasks System (12 files)

## B.1 `tasks/types.ts` (46 lines) — TaskState Union

### Purpose
Defines the `TaskState` discriminated union and a `BackgroundTaskState` subset for the footer pill indicator.

### TaskState Union
```typescript
type TaskState =
  | LocalShellTaskState       // Shell command execution
  | LocalAgentTaskState       // Local agent (sub-agent, main session background)
  | RemoteAgentTaskState      // CCR remote agent
  | InProcessTeammateTaskState // In-process teammate (swarm)
  | LocalWorkflowTaskState    // Background workflow
  | MonitorMcpTaskState       // MCP monitor
  | DreamTaskState            // Auto-dream memory consolidation
```

### BackgroundTaskState
Subset of `TaskState` that can appear in the background tasks indicator. All task types are eligible.

### `isBackgroundTask(task): boolean`
A task is considered a background task if:
1. `status === 'running' || status === 'pending'`
2. If `isBackgrounded` field exists, it's not `false` (foreground tasks not yet backgrounded)

---

## B.2 `tasks/stopTask.ts` (100 lines) — Shared Stop Logic

### Purpose
Shared logic for stopping a running task. Used by `TaskStopTool` (LLM-invoked) and SDK `stop_task` control request.

### Types

```typescript
class StopTaskError extends Error {
  code: 'not_found' | 'not_running' | 'unsupported_type'
}
```

### `stopTask(taskId, context): Promise<StopTaskResult>`
1. Looks up task in `appState.tasks[taskId]`
2. Validates status is `'running'`
3. Looks up `Task` implementation via `getTaskByType(task.type)`
4. Calls `taskImpl.kill(taskId, setAppState)`
5. For shell tasks: suppresses the "exit code 137" notification by marking `notified: true`. Emits `emitTaskTerminatedSdk` directly so SDK consumers see the close.
6. Returns `{ taskId, taskType, command }`

---

## B.3 `tasks/pillLabel.ts` (82 lines) — Footer Pill Labels

### Purpose
Produces compact footer-pill labels for background tasks. Example outputs:

| Scenario | Label |
|----------|-------|
| 1 shell | `1 shell` |
| 3 shells, 2 monitors | `3 shells, 2 monitors` |
| 1 local agent | `1 local agent` |
| 1 cloud session | `◇ 1 cloud session` |
| Ultraplan phase | `◆ ultraplan ready` or `◇ ultraplan needs your input` |
| Dream task | `dreaming` |
| 1 team (teammates) | `1 team` |
| Mixed types | `3 background tasks` |

### `getPillLabel(tasks: BackgroundTaskState[]): string`
All-same-type optimization: produces type-specific labels. Shell tasks distinguish between `shells` and `monitors`. In-process teammates group by `teamName`. Remote agents show diamond symbols (◇ open for running, ◆ filled for ultraplan plan_ready).

### `pillNeedsCta(tasks): boolean`
True when the pill should show the dimmed "· ↓ to view" call-to-action. Only for single remote agent tasks with `isUltraplan && ultraplanPhase` in `needs_input` or `plan_ready`.

---

## B.4 `tasks/LocalMainSessionTask.ts` (479 lines) — Main Session Backgrounding

### Purpose
When the user presses Ctrl+B twice during a query, the main session query is "backgrounded": it continues running while the UI clears to a fresh prompt. This module reuses `LocalAgentTaskState` with `agentType: 'main-session'`.

### Key Functions

**`registerMainSessionTask(description, setAppState, mainThreadAgentDefinition?, existingAbortController?): { taskId, abortSignal }`**
- Generates task ID with 's' prefix (distinct from agent 'a' prefix)
- Links output to an isolated per-task transcript file (NOT the main session transcript — survives `/clear`)
- Reuses or creates abort controller
- Registers cleanup for process exit
- Creates task state with `isBackgrounded: true`, `agentType: 'main-session'`

**`completeMainSessionTask(taskId, success, setAppState): void`**
- Updates status to `completed` or `failed`
- Evicts task output
- Sends notification via `enqueueMainSessionNotification()` (only if still backgrounded — not if user foregrounded it)

**Task ID generation:** 9-character string with 's' prefix + 8 random alphanumeric characters from a custom alphabet.

---

## B.5 `tasks/LocalShellTask/` (3 files)

### B.5.1 `guards.ts` (41 lines) — Type Definitions

```typescript
type LocalShellTaskState = TaskStateBase & {
  type: 'local_bash'              // Backward compatible with persisted state
  command: string
  result?: { code: number; interrupted: boolean }
  completionStatusSentInAttachment: boolean
  shellCommand: ShellCommand | null  // Runtime — provides kill(), cleanup()
  unregisterCleanup?: () => void
  cleanupTimeoutId?: NodeJS.Timeout
  lastReportedTotalLines: number
  isBackgrounded: boolean
  agentId?: AgentId               // Spawning agent for orphan cleanup
  kind?: BashTaskKind             // 'bash' | 'monitor'
}
```

`isLocalShellTask(task)` — Type guard checking `task.type === 'local_bash'`.

### B.5.2 `killShellTasks.ts` (76 lines) — Kill Helpers

**`killTask(taskId, setAppState): void`**
1. Calls `shellCommand.kill()` and `shellCommand.cleanup()`
2. Clears cleanup timeout
3. Sets status to `'killed'`, `notified: true`, nulls shellCommand
4. Evicts task output

**`killShellTasksForAgent(agentId, getAppState, setAppState): void`**
Kills all running bash tasks spawned by a given agent. Called from `runAgent.ts` finally block so background processes don't outlive the agent. Also purges queued notifications for the dead agent via `dequeueAllMatching`.

### B.5.3 `LocalShellTask.tsx` (523 lines) — Shell Task Component

Full implementation of the `Task` interface for shell execution. Key features:
- `looksLikePrompt(tail)` — checks last line against 10 patterns (y/n prompts, "Do you want", "Press any key") to detect interactive prompt stalls
- **Stall watchdog** (`startStallWatchdog`) — monitors output file size every 5s, if output stops growing for 45s AND tail looks like a prompt, fires a notification so the model can intervene. Monitors are excluded from stall detection.
- **Output tailing** — reads output from `getTaskOutputPath()`, uses `tailFile()` for efficient reads
- **Background bash notification** — uses `BACKGROUND_BASH_SUMMARY_PREFIX = 'Background command '` for UI collapse transform
- **Agent-scoped cleanup** — stores `agentId` for orphan cleanup when agent exits

---

## B.6 `tasks/LocalAgentTask/LocalAgentTask.tsx` (683 lines) — Local Agent Task

### Purpose
Full `Task` interface implementation for local agent execution (sub-agents spawned by AgentTool, main session backgrounding, etc.).

### Key Types

```typescript
type ToolActivity = {
  toolName: string
  input: Record<string, unknown>
  activityDescription?: string  // Pre-computed from Tool.getActivityDescription()
  isSearch?: boolean             // Grep, Glob, etc.
  isRead?: boolean               // Read, cat, etc.
}

type AgentProgress = {
  toolUseCount: number
  tokenCount: number
  lastActivity?: ToolActivity
  recentActivities?: ToolActivity[]  // Capped at MAX_RECENT_ACTIVITIES=5
  summary?: string
}

type ProgressTracker = {
  toolUseCount: number
  latestInputTokens: number         // Cumulative per-turn from API
  cumulativeOutputTokens: number    // Per-turn output, summed
  recentActivities: ToolActivity[]
}
```

### Key Functions

**`createProgressTracker(): ProgressTracker`** — Factory for fresh tracker.

**`getTokenCountFromTracker(tracker): number`** — `latestInputTokens + cumulativeOutputTokens`

**`updateProgressFromMessage(tracker, message, resolveActivityDescription?, tools?): void`**
Processes each assistant message: updates token counts, increments tool counter, pre-computes activity descriptions. Excludes `SyntheticOutputTool` (internal tool) from activity display.

### Design Notes
- `latestInputTokens` is cumulative in the Claude API (includes all previous context), so we keep the latest value
- `cumulativeOutputTokens` is per-turn, so we sum those
- Token count includes `cache_creation_input_tokens` and `cache_read_input_tokens`
- Activity descriptions are pre-computed at recording time (when tool definitions are available) rather than at render time

---

## B.7 `tasks/InProcessTeammateTask/` (2 files)

### B.7.1 `types.ts` (121 lines) — Teammate Types

```typescript
type TeammateIdentity = {
  agentId: string             // e.g., "researcher@my-team"
  agentName: string           // e.g., "researcher"
  teamName: string
  color?: string
  planModeRequired: boolean
  parentSessionId: string     // Leader's session ID
}

type InProcessTeammateTaskState = TaskStateBase & {
  type: 'in_process_teammate'
  identity: TeammateIdentity
  prompt: string
  model?: string
  selectedAgent?: AgentDefinition
  abortController?: AbortController          // Kills WHOLE teammate
  currentWorkAbortController?: AbortController // Aborts current turn only
  awaitingPlanApproval: boolean
  permissionMode: PermissionMode              // Cycled independently via Shift+Tab
  error?: string
  result?: AgentToolResult
  progress?: AgentProgress
  messages?: Message[]                        // UI mirror, capped at 50
  inProgressToolUseIDs?: Set<string>
  pendingUserMessages: string[]               // Queue for zoomed view
  isIdle: boolean
  shutdownRequested: boolean
  onIdleCallbacks?: Array<() => void>         // Runtime only
  lastReportedToolCount: number
  lastReportedTokenCount: number
}
```

### Design: Message Cap

`TEAMMATE_MESSAGES_UI_CAP = 50` — The `task.messages` array exists purely for the zoomed transcript dialog. The full conversation lives in `inProcessRunner`'s local `allMessages` array and on disk. Without this cap, whale sessions launching 292 agents in 2 minutes reached 36.8GB RSS. The cap uses `appendCappedMessage(prev, item)` which slices to keep the most recent 50 entries.

### B.7.2 `InProcessTeammateTask.tsx` (126 lines) — Task Implementation

**`InProcessTeammateTask: Task`** — Minimal Task interface:
- `kill(taskId, setAppState)` → delegates to `killInProcessTeammate()`

**`requestTeammateShutdown(taskId, setAppState): void`** — Sets `shutdownRequested: true` on running task.

**`appendTeammateMessage(taskId, message, setAppState): void`** — Appends to messages array with cap, only for running tasks.

**`injectUserMessageToTeammate(taskId, userMessage, setAppState): void`** — For zoomed view: appends user message to both messages array and `pendingUserMessages` queue.

**`getAllInProcessTeammateTasks(state): InProcessTeammateTaskState[]`** — Filters all tasks by type guard.

---

## B.8 `tasks/RemoteAgentTask/RemoteAgentTask.tsx` (856 lines) — Remote CCR Agent Task

### Purpose
Task implementation for CCR remote agents. Spawned by `/remote-agent`, ultraplan, ultrareview, autofix-pr, and background-pr commands. Uses polling to track remote session state.

### Key Types

```typescript
const REMOTE_TASK_TYPES = ['remote-agent', 'ultraplan', 'ultrareview', 'autofix-pr', 'background-pr'] as const
type RemoteTaskType = typeof REMOTE_TASK_TYPES[number]

type RemoteAgentTaskState = TaskStateBase & {
  type: 'remote_agent'
  remoteTaskType: RemoteTaskType
  remoteTaskMetadata?: RemoteTaskMetadata  // PR number, repo, etc.
  sessionId: string                         // For API calls
  command: string
  title: string
  todoList: TodoList
  log: SDKMessage[]
  isLongRunning?: boolean                   // Don't auto-complete on first result
  pollStartedAt: number                     // Review timeout clocks from here
  isRemoteReview?: boolean                  // Created by /ultrareview
  reviewProgress?: { stage, bugsFound, bugsVerified, bugsRefuted }
  isUltraplan?: boolean
  ultraplanPhase?: Exclude<UltraplanPhase, 'running'>  // needs_input | plan_ready
}
```

### Remote Task Metadata
- `AutofixPrRemoteTaskMetadata` — `{ owner, repo, prNumber }`
- `RemoteTaskMetadata` is currently just `AutofixPrRemoteTaskMetadata`

### Key Features
- **Poll-based monitoring** — `pollRemoteSessionEvents` checks for new messages and state changes
- **Completion checkers** — `Map<RemoteTaskType, RemoteTaskCompletionChecker>` for type-specific completion detection
- **Ultraplan phases** — Distinct pill states: `needs_input` (remote asked a clarifying question), `plan_ready` (ExitPlanMode awaiting browser approval)
- **Review progress** — Parsed from orchestrator's `<remote-review-progress>` heartbeat echoes with stages (finding/verifying/synthesizing) and bug counts
- **Metadata persistence** — Remote agent metadata persisted via `writeRemoteAgentMetadata` / `listRemoteAgentMetadata` for resume
- **Notification formatting** — XML notifications with `<task-notification>`, `<status>`, `<summary>`, `<remote-review>`, `<ultraplan>` tags

---

## B.9 `tasks/DreamTask/DreamTask.ts` (157 lines) — Auto-Dream Task

### Purpose
UI surfacing for auto-dream (memory consolidation subagent). Makes the otherwise-invisible forked agent visible in the footer pill and Shift+Down dialog.

### Key Types

```typescript
type DreamTurn = { text: string; toolUseCount: number }
type DreamPhase = 'starting' | 'updating'

type DreamTaskState = TaskStateBase & {
  type: 'dream'
  phase: DreamPhase
  sessionsReviewing: number
  filesTouched: string[]      // INCOMPLETE — only captures Edit/Write tool calls
  turns: DreamTurn[]          // Capped at MAX_TURNS=30
  abortController?: AbortController
  priorMtime: number          // For rewinding consolidation lock on kill
}
```

### Key Functions

**`registerDreamTask(setAppState, opts): string`** — Registers with `phase: 'starting'`, `sessionsReviewing`, `priorMtime`, `abortController`.

**`addDreamTurn(taskId, turn, touchedPaths, setAppState): void`** — Appends turn to capped array, deduplicates touched paths, flips phase to `'updating'` on first write.

**`completeDreamTask(taskId, setAppState): void`** — Sets `status: 'completed'`, `notified: true` immediately (dream has no model-facing notification path).

**`failDreamTask(taskId, setAppState): void`** — Sets `status: 'failed'`, `notified: true`.

**`DreamTask: Task`** — Kill implementation: aborts controller, rewinds consolidation lock mtime via `rollbackConsolidationLock(priorMtime)` so next session can retry.

---

# Part C: Screens (3 files)

## C.1 `screens/REPL.tsx` (5,006 lines) — THE Main REPL Screen

### Purpose
The largest single file in the codebase. The main REPL (Read-Eval-Print Loop) screen that orchestrates the entire interactive CLI experience.

### Component Scope
This is the central UI component that integrates:
- **Message rendering** — Virtual scroll, message grouping, turn boundaries
- **Prompt input** — Text input, history, slash commands, tab completion
- **Tool permission dialogs** — `PermissionRequest` for tool use confirmation
- **Task management** — Background task indicators, detail dialogs, kill/stop
- **Keybindings** — Full keyboard shortcut system
- **Voice input** — Recording and processing state
- **Swarm (teammates)** — Worker pending permissions, sandbox permission sync
- **Cost tracking** — Token usage display, cost threshold warnings
- **Idle detection** — Auto-return after inactivity
- **Notifications** — Priority queue display in footer
- **Remote sessions** — Orchestrates `RemoteSessionManager` for CCR connections
- **Direct Connect** — Local server connections
- **SSH sessions** — Remote SSH REPL
- **Assistant history** — Paginated event history
- **Skill improvement survey** — Post-turn survey prompts
- **MoreRight integration** — Internal-only hook via external stub
- **FPS metrics** — Performance monitoring display
- **Search** — Transcript search (`useSearchInput`, `useSearchHighlight`)
- **Export** — Message export to plain text / external editor
- **Clipboard** — OSC 52 clipboard for copy operations

### Key Hooks Used
- `useTerminalSize`, `useTerminalFocus`, `useTerminalTitle`, `useTabStatus`
- `useNotifications` — footer notification queue
- `useRemoteSession` / `useDirectConnect` / `useSSHSession` — session management
- `useAssistantHistory` — paginated event history loading
- `useReplBridge` — SDK REPL bridge
- `useLogMessages` — message logging/history
- `useIdeLogging` — IDE integration
- `useSwarmPermissionPoller` — swarm permission sync
- `useSkillImprovementSurvey` — post-turn survey
- `useMoreRight` — external stub (no-op)
- `useFpsMetrics` — performance metrics
- `useSearchInput` / `useSearchHighlight` — transcript search
- `useDeferredHookMessages` — deferred hook message handling

### Key Components Rendered
- `PromptInput` — main input area with mode indicators
- `PromptInputQueuedCommands` — queued command display
- `PermissionRequest` — tool use confirmation dialogs
- `ElicitationDialog` — MCP elicitation
- `PromptDialog` — hook prompt dialogs
- `CostThresholdDialog` — cost warning
- `IdleReturnDialog` — idle return prompt
- `SkillImprovementSurvey` — post-turn survey
- `WorkerPendingPermission` — swarm permission display
- `MessageSelector` — message selection (for editing/retrying)

### Key Functions
- `handleSubmit` — processes user input through the query pipeline
- Message rendering with virtual scroll via `VirtualMessageList`
- Scroll-to-bottom behavior with "jump to bottom" UI
- Tool permission flow: intercept, display dialog, respond with allow/deny
- Task lifecycle: create, poll, complete, kill
- Ctrl+B backgrounding flow
- Voice recording → processing → transcript injection
- OCR paste image detection

---

## C.2 `screens/Doctor.tsx` (575 lines) — Diagnostic Screen

### Purpose
`/doctor` slash command. Displays comprehensive diagnostic information about the CLI environment.

### Sections Displayed

| Section | Content |
|---------|---------|
| **System Info** | Platform, Node version, Bun version, process uptime, PID |
| **Version & Updates** | Current version, latest npm/GCS dist tags, auto-update status |
| **Settings** | All settings sources (user/policy/local/project/flag) with values |
| **Context Warnings** | Token usage, conversation length, context size advisories |
| **Keybinding Errors** | `KeybindingWarnings` — conflicting or invalid keybindings |
| **MCP Parsing** | `McpParsingWarnings` — MCP server config parsing issues |
| **Agent Config** | Active agents list (source: settings/plugin/built-in), user/project agent dirs |
| **Auto-Updater** | Version lock info, stale locks cleaned, lock file paths |
| **Lock Files** | `getAllLockInfo()` — pid-based locking for auto-updates |
| **Sandbox** | `SandboxDoctorSection` — sandbox-specific diagnostics |
| **Validation Errors** | `ValidationErrorsList` — settings validation errors from `useSettingsErrors` |

### Key Hooks
- `useSettingsErrors` — settings validation state
- `useKeybindings` — for checking keybinding errors
- `useAppState` — for settings state
- `checkContextWarnings` — token/context analysis
- `getDoctorDiagnostic` — system info collection
- `getGcsDistTags` / `getNpmDistTags` — version comparison

---

## C.3 `screens/ResumeConversation.tsx` (399 lines) — Session Resume

### Purpose
Interactive session resume screen. Supports `--resume`, `--resume-last`, `--resume SESSION_ID`, and `--resume PR#`.

### Key Features

**Log Selection** — Uses `LogSelector` component for browsing conversation logs across projects.

**Cross-Project Resume** — `checkCrossProjectResume()` detects if the selected session is from a different project and handles directory changes.

**Worktree Restoration** — `restoreWorktreeForResume()` for worktree-based agents.

**PR Parsing** — `parsePrIdentifier(value)` extracts PR numbers from URLs or direct numbers.

**Session Resumption** — `loadConversationForResume()` loads full conversation state from session storage.

**Agent Restore** — `restoreAgentFromSession()` / `computeStandaloneAgentContext()` for restoring agent-specific context.

**Progressive Log Loading** — `loadAllProjectsMessageLogsProgressive()` and `loadSameRepoMessageLogsProgressive()` with incremental rendering.

**Session Metadata** — `restoreSessionMetadata()` for cost state, tool results, content replacements.

**Asciicast Rename** — `renameRecordingForSession()` for terminal recording alignment.

### Session Search
When `initialSearchQuery` is provided, uses `agenticSessionSearch()` for AI-powered session discovery.

---

# Part D: Server (3 files) — Direct Connect Mode

## D.1 `server/types.ts` (57 lines) — Server Types

### Key Types

```typescript
type ServerConfig = {
  port: number
  host: string
  authToken: string
  unix?: string
  idleTimeoutMs?: number       // 0 = never expire
  maxSessions?: number
  workspace?: string
}

type SessionState = 'starting' | 'running' | 'detached' | 'stopping' | 'stopped'

type SessionInfo = {
  id: string
  status: SessionState
  createdAt: number
  workDir: string
  process: ChildProcess | null
  sessionKey?: string
}

type SessionIndexEntry = {
  sessionId: string
  transcriptSessionId: string
  cwd: string
  permissionMode?: string
  createdAt: number
  lastActiveAt: number
}

type SessionIndex = Record<string, SessionIndexEntry>
```

### Zod Schema
`connectResponseSchema` — validates `POST /sessions` response: `{ session_id: string, ws_url: string, work_dir?: string }`.

---

## D.2 `server/createDirectConnectSession.ts` (88 lines) — Session Creation

### `createDirectConnectSession({ serverUrl, authToken, cwd, dangerouslySkipPermissions }): Promise<{ config, workDir? }>`
1. POSTs to `${serverUrl}/sessions` with JSON body `{ cwd, dangerously_skip_permissions }`
2. Validates response with `connectResponseSchema` (Zod)
3. Returns `DirectConnectConfig` and optional `workDir`

### `DirectConnectError` — Named error class for connection failures.

---

## D.3 `server/directConnectManager.ts` (213 lines) — Direct Connect WebSocket

### Purpose
Manages a direct-connect WebSocket session. Unlike CCR sessions (which use OAuth + message queue), direct connect talks directly to a local server process via its stdout WebSocket.

### `DirectConnectSessionManager`

**`connect(): void`** — Opens WebSocket to `wsUrl` with optional `authToken` as Bearer header. Parse messages line-by-line from stdout.

**Message types handled:**
- `control_request` (`can_use_tool`) → `callbacks.onPermissionRequest`
- SDK messages (assistant, result, system, etc.) → `callbacks.onMessage`
- Ignored: `control_response`, `keep_alive`, `control_cancel_request`, `streamlined_text`, `streamlined_tool_use_summary`, `system/post_turn_summary`

**`sendMessage(content): boolean`** — Sends `{ type: 'user', message: { role: 'user', content }, parent_tool_use_id: null, session_id: '' }`.

**`respondToPermissionRequest(requestId, result): void`** — Sends `{ type: 'control_response', response: { subtype: 'success', request_id, response: { behavior, updatedInput/message } } }`.

**`sendInterrupt(): void`** — Sends `{ type: 'control_request', request_id: randomUUID(), request: { subtype: 'interrupt' } }`.

**`sendErrorResponse(requestId, error): void`** — For unrecognized control request subtypes.

---

# Part E: Migrations (10 files)

All migration files follow a consistent pattern: read settings/config, transform values, write back (idempotent). Each targets a specific model name or settings key migration.

| Migration | Purpose | Strategy |
|-----------|---------|----------|
| `migrateAutoUpdatesToSettings` | Move auto-updates flag to settings | Read global config → write to settings |
| `migrateBypassPermissionsAcceptedToSettings` | Move bypass permissions flag to settings | Settings key migration |
| `migrateEnableAllProjectMcpServersToSettings` | Move MCP servers setting to settings | Permission migration |
| `migrateFennecToOpus` | Rename Fennec model to Opus | Model name string replace in userSettings |
| `migrateLegacyOpusToCurrent` | Map legacy Opus model names to current | Model name mapping |
| `migrateOpusToOpus1m` | Map Opus to Opus 1M | Model name upgrade |
| `migrateReplBridgeEnabledToRemoteControlAtStartup` | Rename REPL bridge setting | Settings key rename |
| `migrateSonnet1mToSonnet45` | Map Sonnet 1M to Sonnet 4.5 | Model name upgrade (1M → 4.5) |
| `migrateSonnet45ToSonnet46` | Map Sonnet 4.5 to 'sonnet' alias (points to 4.6) | Pro/Max/Team Premium users only, first-party API only. Idempotent: only writes if userSettings.model matches a 4.5 string. Does not touch project/local pins. |
| `resetAutoModeOptInForDefaultOffer` | Reset auto-mode opt-in for default offer | Feature flag reset |
| `resetProToOpusDefault` | Reset Pro users to Opus default | Tier-based reset |

### Migration Pattern
All migrations:
1. Check preconditions (API provider, subscription tier, etc.)
2. Read current state from `userSettings` specifically (not merged settings)
3. Transform only if value matches the old pattern
4. Write back via `updateSettingsForSource`
5. Log telemetry events for analytics
6. Are idempotent (won't overwrite user changes)

---

# Part F: Coordinator Mode

## `coordinator/coordinatorMode.ts` (369 lines) — Coordinator Orchestration

### Purpose
Implements the "coordinator mode" where Claude Code acts as an orchestrator spawning workers. Gated on `feature('COORDINATOR_MODE')` and `CLAUDE_CODE_COORDINATOR_MODE` env var.

### Key Functions

**`isCoordinatorMode(): boolean`** — Checks feature gate AND env var.

**`matchSessionMode(sessionMode): string | undefined`** — On resume, matches coordinator mode to the session's stored mode. Flips the env var if mismatched, returns a warning message about the switch.

**`getCoordinatorUserContext(mcpClients, scratchpadDir?): { workerToolsContext }`** — Builds user context text injected into the system prompt:
- Lists worker tool names (from `ASYNC_AGENT_ALLOWED_TOOLS`, minus internal tools: TeamCreate, TeamDelete, SendMessage, SyntheticOutput)
- In SIMPLE mode: Bash + Read + Edit only
- Includes MCP server names if connected
- Includes scratchpad directory info if gate enabled

**`getCoordinatorSystemPrompt(): string`** — 369-line system prompt with:
- Role definition: "You are a coordinator. Help the user achieve their goal, direct workers, synthesize results."
- Tool descriptions: AgentTool (spawn), SendMessage (continue), TaskStopTool (stop), PR subscription tools
- Worker result format: `<task-notification>` XML with task-id, status, summary, result, usage
- Example interaction flow (coordinator launches 2 workers → receives notification → responds)
- Task workflow phases (research, implementation, verification)
- Worker capabilities text (varies by SIMPLE mode)
- Rules: don't fabricate worker results, don't use workers for trivial file reads, don't set model parameter on workers

### Key Tools Enabled
- `AGENT_TOOL_NAME` — spawn workers
- `SEND_MESSAGE_TOOL_NAME` — continue existing workers
- `TASK_STOP_TOOL_NAME` — stop running workers
- `subscribe_pr_activity` / `unsubscribe_pr_activity` — GitHub PR event subscriptions

---

# Part G: Upstream Proxy (2 files)

## G.1 `upstreamproxy/relay.ts` (455 lines) — CONNECT-over-WebSocket Relay

### Purpose
Implements a CONNECT-over-WebSocket relay for CCR's upstream proxy. Listens on localhost TCP, accepts HTTP CONNECT from curl/gh/kubectl/etc., and tunnels bytes over WebSocket to the CCR upstreamproxy endpoint.

### Protocol
```
Client (curl) → localhost TCP → HTTP CONNECT → WebSocket → CCR server
                                    ↑                           ↓
                              (encode/decode            UpstreamProxyChunk
                               protobuf chunks)          protobuf wrappers)
```

### Protobuf Encoding (Manual)
For `message UpstreamProxyChunk { bytes data = 1; }`:
- Tag: `0x0a` (field 1, wire type 2)
- Varint-encoded length
- Raw bytes

`encodeChunk(data: Uint8Array): Uint8Array` and `decodeChunk(buf: Uint8Array): Uint8Array | null` implement this manually to avoid a protobuf runtime dependency in the hot path.

### Key Features
- **Dual runtime**: Bun (`Bun.listen`) and Node (`net.createServer`) — the CCR container runs CLI under Node
- **Buffered pending bytes**: TCP can coalesce CONNECT + ClientHello into one packet; data that arrives before WebSocket `onopen` fires is buffered in `pending` array
- **Ping keepalive**: 30s interval (sidecar idle timeout is 50s)
- **Max chunk**: 512KB (`MAX_CHUNK_BYTES`) — Envoy per-request buffer cap
- **Write backpressure**: Bun's `sock.write()` does partial writes and needs explicit tail-queueing; Node's `net.Socket` buffers unconditionally
- **Established flag**: Once the tunnel is carrying TLS, writing plaintext errors would corrupt the client's TLS stream — just close instead

## G.2 `upstreamproxy/upstreamproxy.ts` (285 lines) — CCR Container-Side Wiring

### Purpose
Initializes the upstream proxy when running inside a CCR session container.

### Initialization Steps (`initUpstreamProxy()`)
1. Reads session token from `/run/ccr/session_token`
2. Calls `setNonDumpable()` — `prctl(PR_SET_DUMPABLE, 0)` via `bun:ffi` to block same-UID ptrace of the heap (Linux-only)
3. Downloads upstreamproxy CA cert (`/v1/code/upstreamproxy/ca-cert`) and concatenates with system CA bundle
4. Starts CONNECT→WebSocket relay (`startUpstreamProxyRelay()`)
5. Unlinks token file (token stays heap-only; file is gone before the agent loop can see it)
6. Exposes `HTTPS_PROXY=localhost:{port}` and `SSL_CERT_FILE={caBundlePath}` env vars

### NO_PROXY List
Prevents MITM for internal services: localhost, RFC1918 ranges (10.0.0.0/8, 172.16.0.0/12, 192.168.0.0/16), Anthropic API (`.anthropic.com`, `*.anthropic.com`, `anthropic.com`), GitHub, npm, PyPI, crates.io, Go proxy.

### Failure Mode
Every step fails open — any error logs a warning and disables the proxy. A broken proxy setup must never break an otherwise-working session.

---

# Part H: Other Supporting Modules

## H.1 `assistant/sessionHistory.ts` (87 lines) — Paginated Session Events

### Purpose
Fetches paginated event history for the assistant viewer mode. Uses the CCR sessions API (`/v1/sessions/{sessionId}/events`).

### Key Types
```typescript
type HistoryPage = {
  events: SDKMessage[]    // Chronological within page
  firstId: string | null  // Cursor for older pages
  hasMore: boolean
}
```

### Key Functions
- `createHistoryAuthCtx(sessionId): Promise<HistoryAuthCtx>` — Prepares auth headers once, reuse across pages
- `fetchLatestEvents(ctx, limit): Promise<HistoryPage | null>` — Newest page via `anchor_to_latest`
- `fetchOlderEvents(ctx, beforeId, limit): Promise<HistoryPage | null>` — Older page via `before_id` cursor

---

## H.2 `moreright/useMoreRight.tsx` (26 lines) — External Stub

### Purpose
Stub for external builds — the real `useMoreRight` hook is internal only. Provides no-op implementations:
- `onBeforeQuery`: async () => true
- `onTurnComplete`: async () => {}
- `render`: () => null

Self-contained with no relative imports (typecheck sees this file before the internal overlay).

---

## H.3 `schemas/hooks.ts` (222 lines) — Hook Config Zod Schemas

### Purpose
Zod schema definitions for hook configurations (extracted from `utils/settings/types.ts` to break import cycles with `plugins/schemas.ts`).

### Hook Types
Three discriminated union members:

**`BashCommandHookSchema`**
- `type: 'command'`, `command: string`, optional: `if` (permission rule syntax filter), `shell`, `timeout`, `statusMessage`, `once`, `async`, `asyncRewake` (async + wakes model on exit code 2)

**`PromptHookSchema`**
- `type: 'prompt'`, `prompt: string` (with `$ARGUMENTS` placeholder), optional: `if`, `timeout`, `model`, `statusMessage`, `once`

**`HttpHookSchema`**
- `type: 'http'`, `url: string` (validated URL), optional: `if`, `timeout`, `statusMessage`, `once`

### Advanced Hook Features
- `async` — runs in background without blocking
- `asyncRewake` — runs in background, wakes the model on exit code 2 (blocking error). Implies `async`.
- `once` — runs once and is removed after execution
- `if` — permission rule syntax filter (e.g., `"Bash(git *)"`) to avoid spawning hooks for non-matching commands

---

# Architecture Summary

```
┌─────────────────────────────────────────────────────────┐
│                      REPL.tsx                            │
│  ┌─────────────┐ ┌──────────┐ ┌──────────────────────┐ │
│  │ PromptInput  │ │ Messages │ │ Permission Dialogs   │ │
│  └──────┬───────┘ └──────────┘ └──────────────────────┘ │
│         │                                                 │
│  ┌──────┴──────────────────────────────────────────────┐ │
│  │              Session Management                      │ │
│  │  RemoteSessionManager  ◄── SessionsWebSocket        │ │
│  │  DirectConnectSessionManager ◄── ws://localhost     │ │
│  │  SSH Session                                         │ │
│  └─────────────────────────────────────────────────────┘ │
│                                                           │
│  ┌─────────────────────────────────────────────────────┐ │
│  │              Task Management                         │ │
│  │  LocalShellTask ── background bash commands         │ │
│  │  LocalAgentTask ── sub-agents, main session         │ │
│  │  RemoteAgentTask ── CCR remote agents               │ │
│  │  InProcessTeammateTask ── swarm teammates           │ │
│  │  DreamTask ── auto-dream consolidation              │ │
│  └─────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────┘

┌──────────────┐    ┌─────────────┐    ┌──────────────────┐
│  Server       │    │ Coordinator │    │ Upstream Proxy   │
│  ──────────── │    │ ─────────── │    │ ──────────────── │
│  DirectConnect│    │ Coordinator │    │ relay.ts:        │
│  POST/sessions│    │  System      │    │  CONNECT→WS     │
│  WS stdout    │    │  Prompt      │    │  relay for CCR  │
│  SessionIndex │    │  Worker tools│    │ upstreamproxy   │
└──────────────┘    └─────────────┘    └──────────────────┘

┌──────────────────────────────────────────────────────────┐
│                   Migrations (10 files)                   │
│  migrateSonnet45ToSonnet46, migrateSonnet1mToSonnet45,  │
│  migrateOpusToOpus1m, migrateFennecToOpus, etc.         │
└──────────────────────────────────────────────────────────┘
```
