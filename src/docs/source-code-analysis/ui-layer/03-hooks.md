# 03 — Hooks System

> **104 files** | React hooks: text input, typeahead, voice, virtual scroll, sessions, permissions, notifications, IDE integration

## Overview

The Hooks layer encapsulates all reusable stateful logic — from text input cursors to voice streaming, from virtual scrolling to session teleportation. These hooks are the "brains" of the UI; components are thin wrappers that wire hooks to Ink's rendering primitives. Hooks are organized by domain: core input, session management, permissions, IDE integration, agent orchestration, plugin management, content suggestions, and notifications.

---

## 1. Core Input Hooks

### 1.1 `useTextInput.ts` (529 lines)
The foundational text input hook — manages everything from cursor position to paste handling, from kill ring to history navigation.

**Parameters** (`UseTextInputProps`):
- `value` / `onChange` / `onSubmit` — controlled input pattern
- `onExit` / `onExitMessage` — Escape behavior
- `onHistoryUp` / `onHistoryDown` / `onHistoryReset` — history navigation
- `focus` — whether the input is focused
- `mask` — password-style masking character
- `multiline` — enable multiline editing (Alt+Enter for newline)
- `cursorChar` — cursor character (e.g., `"█"`)
- `highlightPastedText` — flash pasted text
- `invert` / `themeText` — text transformation for theming
- `columns` — terminal width for wrapping
- `onImagePaste` — paste image handling (base64 + metadata)
- `disableCursorMovementForUpDownKeys` — reserve arrows for navigation
- `disableEscapeDoublePress` — disable double-Escape for exit
- `maxVisibleLines` — multiline viewport limit
- `externalOffset` / `onOffsetChange` — external cursor offset control
- `inputFilter` — post-parse input filter (for vim mode)
- `inlineGhostText` — ghost/suggestion text
- `dim` — dimming function for ghost text

**Internal State & Logic**:
- **Cursor Management** (`utils/Cursor.ts`): Uses `Cursor` class for position tracking. Handles `moveLeft`, `moveRight`, `moveWordLeft`, `moveWordRight`, `moveToStart`, `moveToEnd`, `backspace`, `delete`, `deleteWord`, `insert`.
- **Kill Ring** (`getLastKill`, `pushToKillRing`, `recordYank`, `resetKillAccumulation`, `resetYankState`, `updateYankLength`, `yankPop`): Emacs-style kill ring — `Ctrl+K` kills to end of line (consecutive kills accumulate), `Ctrl+W` kills word, `Ctrl+U` kills to start, `Ctrl+Y` yanks, `Alt+Y` cycles through kill ring.
- **History Navigation**: Up/Down arrows navigate command history. `onHistoryUp`/`onHistoryDown` callbacks. Reset on new input.
- **Paste Handling** (`usePasteHandler`): Detects bracketed paste (`\e[200~...\e[201~`), handles multiline paste, image paste detection (data URI, base64).
- **Modifier Detection** (`isModifierPressed`): Pre-warms modifier state on each keypress.
- **Double Press** (`useDoublePress`): Detects double-Escape for exit. Default timeout: 500ms.
- **Ghost Text**: InlineTab to accept, right-arrow at end to accept word, printing chars dismiss.
- **Input Filter**: Applied before any handler. Used by vim mode to intercept characters in NORMAL mode.
- **Image Paste**: Detects base64 images in pasted text, calls `onImagePaste` with decoded data, media type, dimensions.

### 1.2 `useTypeahead.tsx` (1384 lines)
Command/argument/file autocomplete engine — the system that powers the `/` command menu and `@` file suggestions.

**Trigger Detection**:
- **Slash Commands** (`/`): Detected by `isCommandInput()`. Prefix `/` triggers command suggestions.
- **File/Skill References** (`@`): Detected by `AT_TOKEN_HEAD_RE`. Prefix `@` triggers file/skill/agent suggestions.
- **Hash Channels** (`#`): Detected by `HASH_CHANNEL_RE` for Slack channel mentions.
- **Plain Paths** (`PATH_CHAR_HEAD_RE`): Triggered for paths containing `/` or `.\`.

**Suggestion Sources**:
1. **Commands** (`getCommandName`, `generateCommandSuggestions`, `getBestCommandMatch`): All registered slash commands, ranked by usage frequency and prefix match. Handles subcommands and argument suggestions.
2. **File Suggestions** (`applyFileSuggestion`, `startBackgroundCacheRefresh`): Uses the `FileIndex` (nucleo-style fuzzy search) from `fileSuggestions.ts`. Background cache refresh keeps the index current. Handles: directories, file paths, relative/absolute paths.
3. **Shell History** (`getShellHistoryCompletion`): Recent shell commands from bash/zsh/fish history files.
4. **Shell Completions** (`getShellCompletions`): Dynamic completions via shell's native tab-completion. Types: `file`, `directory`, `command`, `process`, `variable`, `user`, `host`. Uses `getShellCompletions()` with caching.
5. **Path Completions** (`getPathCompletions`, `getDirectoryCompletions`): Filesystem-based path completion with `stat` for type detection (file vs directory).
6. **Slack Channels** (`getSlackChannelSuggestions`): When MCP Slack server is connected, suggests channel names.
7. **Unified Suggestions** (`generateUnifiedSuggestions`): Merges all sources into a single ranked list.

**State Management**:
- `suggestions: SuggestionItem[]` — current suggestion list
- `selectedSuggestion: number` — highlighted index (-1 = none)
- `isAutocompleteActive` — derived (`suggestions.length > 0 || !!effectiveGhostText`), not stored in `useState`; drives overlay/keybinding context registration
- `context: { promptInputMode, terminalWidth, cursorOffset, cursorLine }` — rendering context

**Keybindings**:
- `Tab`: Insert selected suggestion or cycle
- `Shift+Tab`: Cycle backward
- `Enter`: Insert selected suggestion and submit
- `Escape`: Dismiss suggestions
- Arrow keys: Navigate suggestions (when menu is open)

**Debouncing**: Suggestion refreshes are debounced with `useDebounceCallback`. File completions have progressive timeouts (fast for short queries, slower for long ones).

**Argument Hints** (`generateProgressiveArgumentHint`): Shows command argument names and descriptions as the user types arguments (e.g., `/resume [sessionId]`).

**Resume Input** (`buildResumeInputFromSuggestion`): Special handling for session resume — inserts `/resume <sessionId>` for session suggestions.

### 1.3 `useVimInput.ts` (316 lines)
Vim modal editing for text input — brings vim's NORMAL/VISUAL/INSERT modes to the CLI prompt.

**Architecture**:
- Uses `useTextInput` internally for all character-level editing in INSERT mode.
- Wraps input with a Vim state machine (`vim/transitions.ts` → `transition()`) that intercepts keypresses before they reach `useTextInput`.
- Maintains `VimState` (mode, operator pending, count prefix, register) and `PersistentState` (last search, recorded changes for dot-repeat).

**Modes**:
- **INSERT**: Default mode. Text is typed normally. Escape returns to NORMAL.
- **NORMAL**: Navigation and editing commands: `h`/`j`/`k`/`l` movement, `w`/`b`/`e` word movement, `0`/`$`/`^` line boundaries, `i`/`a`/`I`/`A`/`o`/`O` for entering INSERT, `x`/`dd`/`D`/`cc`/`C`/`s`/`S` for deletion/change, `p`/`P` for paste, `u`/`Ctrl+R` undo/redo, `/`/`?` search, `~` toggle case, `J` join lines, `>>`/`<<` indent.
- **VISUAL**: Character/line/block selection for operations. `v`/`V`/`Ctrl+V` to enter.
- **OPERATOR-PENDING**: After `d`/`c`/`y`/`>`/`<`, waiting for motion or text object.

**Operators** (`vim/operators.ts`):
- `executeOperatorMotion(ctx, motion)`: Apply operator (d/c/y) to a motion (j/gg/iw/etc.)
- `executeOperatorFind(ctx, char)`: Apply operator to find (f/F/t/T)
- `executeOperatorTextObj(ctx, obj)`: Apply operator to text object (iw/iW/aw/i"/i)/etc.)
- `executeX(ctx)`: Delete character under cursor (x)
- `executeReplace(ctx, char)`: Replace character (r)
- `executeToggleCase(ctx)`: Toggle case (~)
- `executeIndent(ctx)`: Indent (>>)
- `executeJoin(ctx)`: Join lines (J)
- `executeOpenLine(ctx)`: Open line below/above (o/O)

**Integration**: Exposes `VimInputState` with `mode`, `textInput` (the underlying `useTextInput` result), and `handleVimInput` function. `VimTextInput` component renders the mode indicator.

### 1.4 Other Core Input Hooks

#### `useCommandQueue.ts`
Command queuing — serializes slash commands into a FIFO queue. Ensures commands from different sources (keybindings, typeahead, programmatic) don't interleave.

#### `useCommandKeybindings.tsx`
Maps keyboard shortcuts to command execution. Handles: global keybindings from `useGlobalKeybindings`, context-sensitive keybindings from `useOptionalKeybindingContext`, and keybinding conflict resolution.

#### `useQueueProcessor.ts`
Processes the command queue sequentially — respects modal overlays, handles command lifecycle (start, running, done, error).

#### `useInputBuffer.ts` (132 lines)
Raw stdin buffering — separates stdin into keypress tokens using `parse-keypress.ts`. Feeds tokens to both the main input handler and any active overlays. Handles paste bracketing detection and buffered input flushing.

#### `useArrowKeyHistory.tsx` (229 lines)
Arrow-key-driven command history navigation with fuzzy search — like `Ctrl+R` but with visual feedback. Up/Down arrows filtered by a search query. Shows matching history entries in a floating panel.

#### `useHistorySearch.ts` (303 lines)
Interactive command history search (Ctrl+R style). Substring matching via `lastIndexOf` over history entries (no Fuse.js). Scrolls through results. Features: case-sensitive substring search, timestamp display, oldest-to-newest ordering.

#### `usePasteHandler.ts` (285 lines)
Paste detection and processing — handles bracketed paste mode detection, multiline paste normalization (strip trailing newline, preserve indentation), image paste detection (base64 data URIs, binary image data from clipboard), and paste highlighting (temporary background color flash).

---

## 2. Session/Remote Hooks

### 2.1 `useRemoteSession.ts` (604 lines)
Remote CCR session hook for the REPL — manages a `RemoteSessionManager` WebSocket connection. Scope is limited to CCR remote sessions (not SSH tunnels; see `useSSHSession.ts`). Handles:
- **Connection Lifecycle**: Connect, disconnect, reconnect callbacks (`onConnected`, `onReconnecting`, `onDisconnected`).
- **SDK Message Stream**: Adapts remote SDK messages via `convertSDKMessage` / `handleMessageFromStream`.
- **Permission Bridge**: Surfaces remote permission prompts as `ToolUseConfirm` queue entries with `respondToPermissionRequest`.
- **User Input**: `sendMessage()` via HTTP POST; UUID echo filter via `BoundedUUIDSet`.
- **State**: Returns `{ isRemoteMode, sendMessage, cancelRequest, disconnect }`; tracks streaming tool uses, response timeouts (60s default, 180s during compaction).
- **Session Title**: Fire-and-forget `generateSessionTitle()` / `updateSessionTitle()` after first user message.

### 2.2 `useSSHSession.ts` (241 lines)
SSH tunnel management — establishes and maintains the SSH connection for remote REPL.

- **Tunnel Setup**: `ssh -L localPort:localhost:remotePort user@host -N` style forwarding.
- **Authentication**: Handles key-based, agent-forwarding, and password (via askpass) auth.
- **Connection Health**: Periodic keepalive pings. Detects broken pipes and triggers reconnect.
- **Port Management**: Auto-selects a free local port for forwarding.

### 2.3 `useSessionBackgrounding.ts` (158 lines)
Session backgrounding — saves session state, disconnects from remote, runs in background. Handles:
- **Background Transition**: Save transcript, disconnect bridge, continue workers.
- **Foreground Restore**: Reconnect bridge, restore UI state, sync file changes.
- **Task Continuation**: Background tasks keep running; their output is captured and replayed on restore.

### 2.4 `useReplBridge.tsx` (719 lines)
Remote Control bridge to claude.ai — connects the local REPL to a browser session via `ReplBridge`. Handles:
- **Bridge Lifecycle**: Init, reconnect, disconnect; tracks `replBridgeConnectionStatus` in AppState.
- **Permission Sync**: Forwards tool permission requests/responses between local REPL and Remote Control.
- **Message Relay**: Bidirectional message flow between local session and browser bridge.
- **Failure Handling**: Consecutive init failure fuse (max 3) permanently disables bridge for the session.

See `08-large-hooks.md` §4 for full callback and ref inventory.

### 2.5 `useDirectConnect.ts` (229 lines)
Direct connection management (without SSH bridge) — used for local sessions or when the remote is directly reachable.

### 2.6 `useTeleportResume.tsx`
Teleport session resume — recreates the exact state of a previous session. Handles:
- **State Restoration**: Messages, tool calls, agent state, file history.
- **File State Sync**: Restore file states to their session-end values.
- **Agent Resume**: Restart background agents that were running.
- **Progress Display**: Shows resume progress steps.

### 2.7 `useCancelRequest.ts` (276 lines)
Escape/Ctrl+C handling for canceling the current operation. Priority system:
1. Active text selection → clear selection
2. Open permission prompt → deny request
3. Streaming response → abort API request
4. Idle state → exit (Ctrl+C twice or Esc twice)

### 2.8 `useExitOnCtrlCD.ts` (96 lines) & `useExitOnCtrlCDWithKeybindings.ts` (25 lines)

Double-press exit for Ctrl+C / Ctrl+D — hardcoded (not rebindable via `keybindings.json`).

**`useExitOnCtrlCD(useKeybindingsHook, onInterrupt?, onExit?, isActive?)` → `ExitState`:**
- Registers `app:interrupt` (Ctrl+C) and `app:exit` (Ctrl+D) via injected `useKeybindings` hook (avoids import cycle with keybindings module).
- **`ExitState`:** `{ pending: boolean, keyName: 'Ctrl-C' | 'Ctrl-D' | null }` — first press sets `pending`; second press within `useDoublePress` timeout calls `onExit ?? useApp().exit`.
- **`onInterrupt`:** If returns `true`, first Ctrl+C is consumed (e.g. cancel streaming) and double-press exit is skipped.
- **`isActive`:** When `false`, handlers are not registered — used by `Dialog` while embedded `TextInput` is focused.

**`useExitOnCtrlCDWithKeybindings`:** Standard wrapper passing `useKeybindings` — the import path used by `Dialog`, wizards, and permission flows.

---

## 3. Permission/Security Hooks

### 3.1 `useCanUseTool.tsx` (204 lines)
Permission resolution hook — returns a stable `CanUseToolFn` used by the tool executor. The returned async function runs the full pipeline: config check via `hasPermissionsToUseTool()`, then on `'ask'` routes through coordinator auto-checks, swarm worker forwarding, bash classifier grace period, and interactive permission via `setToolUseConfirmQueue`.

**Return type**: `CanUseToolFn` — `(tool, input, toolUseContext, assistantMessage, toolUseID, forceDecision?) => Promise<PermissionDecision>`. Not a boolean `{ canUse, reason }` wrapper.

### 3.2 `toolPermission/` (5 files)

Supporting modules for `useCanUseTool` — not a React context provider. See `06-permissions-custom-components.md` Part 1 for full detail.

#### `PermissionContext.ts` (379 lines)
Factory `createPermissionContext()` — per-invocation helper bound to one tool call. Provides abort handling (`resolveIfAborted`, `cancelAndAbort`), decision builders (`buildAllow`, `buildDeny`), persistence (`persistPermissions`, `handleUserAllow`, `handleHookAllow`), analytics (`logDecision`, `logCancelled`), classifier/hook runners (`tryClassifier`, `runHooks`), and confirm-queue ops (`pushToQueue`, `removeFromQueue`, `updateQueueItem`). `createPermissionQueueOps()` bridges React `setToolUseConfirmQueue` to generic queue interface.

#### `permissionLogging.ts` (220 lines)
`logPermissionDecision()` — centralized analytics/OTel after every approve/reject (wait time, code-edit enrichment, `toolDecisions` map).

#### `handlers/` (3 files)
Resolution stages invoked from `useCanUseTool` on `'ask'` behavior — not per-tool category checkers:
- **`coordinatorHandler.ts` (59 lines)**: `handleCoordinatorPermission()` — coordinator workers await hooks + classifier sequentially before dialog.
- **`interactiveHandler.ts` (506 lines)**: `handleInteractivePermission()` — pushes `ToolUseConfirm` to queue; races bridge, channel, hooks, and bash classifier against user input.
- **`swarmWorkerHandler.ts` (142 lines)**: `handleSwarmWorkerPermission()` — forwards permission to swarm leader via mailbox; returns `null` for non-workers.

### 3.3 Security Hooks

#### `useApiKeyVerification.ts` (84 lines)
API key validation — verifies the API key is valid before making requests. Shows error if key is invalid, expired, or has insufficient credits. Handles OAuth token refresh.

#### `useAfterFirstRender.ts`
Utility hook — runs a callback only after the first render completes, not during SSR/mount. Used for deferred initialization that shouldn't block the initial paint.

---

## 4. IDE Integration Hooks

### 4.1 `useIDEIntegration.tsx`
IDE integration master hook — manages the IDE connection lifecycle. Handles:
- **Connection**: WebSocket/stdio connection to the IDE extension.
- **Capability Negotiation**: Discovers IDE features (file opening, selection, diagnostics, terminal).
- **Workspace Sync**: Sends workspace root, open files, cursor position.
- **Command Dispatch**: Forwards IDE commands (go to definition, find references, format).

### 4.2 `useIdeSelection.ts` (151 lines)
Subscribes to IDE MCP `selection_changed` notifications from the connected IDE client.

**Returns:** `IDESelection | null` — `{ lineCount, lineStart?, text?, filePath? }` derived from LSP-style `{ start, end }` points and optional selected text.

**Flow:** Registers listener on `getConnectedIdeClient()`; validates payloads with `SelectionChangedSchema`; clears selection when IDE disconnects. Used by prompt context (@-mention IDE options) and status indicators — not a polling hook.

### 4.3 `useIdeConnectionStatus.ts`
IDE connection status monitoring — shows connection state in the status line. States: `disconnected`, `connecting`, `connected`, `error`.

### 4.4 `useIdeAtMentioned.ts`
IDE @-mention integration — when the user types `@` in the prompt, includes IDE context options (open file, selection, visible range, function under cursor).

### 4.5 `useIdeLogging.ts`
IDE diagnostic logging — streams LSP diagnostics (errors, warnings, hints) from the IDE. Used for context-aware error suggestions.

### 4.6 `useDiffInIDE.ts` (379 lines)
IDE diff integration — sends file diffs to the IDE for side-by-side review. Handles:
- **Diff Format**: Converts Claude's unified diff to IDE's expected format.
- **Apply/Reject**: Sends apply/reject commands to the IDE for individual hunks or whole files.
- **Progress**: Reports diff application progress and errors.
- **Multi-File**: Coordinates diffs across multiple files.

### 4.7 IDE Onboarding Components
- `IdeOnboardingDialog.tsx` — IDE setup wizard: install extension, configure, connect.
- `IdeAutoConnectDialog.tsx` — Auto-connect prompt when IDE is detected.

---

## 5. Agent/Team/Swarm Hooks

### 5.1 `useInboxPoller.ts` (969 lines)
Teammate mailbox poller — reads `teammateMailbox` for swarm team leads and process-based teammates. Features:
- **Polling Interval**: `INBOX_POLL_INTERVAL_MS = 1000` (1 second) via `useInterval` when `shouldPoll` is true.
- **Message Classification**: Permission requests/responses, plan approvals, sandbox permissions, shutdown requests, mode-set requests, then regular teammate messages.
- **Delivery**: Submits immediately when session idle; queues in `AppState.inbox` when busy; idle-delivery effect flushes on turn completion.
- **Permission Integration**: Routes permission prompts to `ToolUseConfirm` queue; syncs responses via mailbox and `useSwarmPermissionPoller` helpers.
- **Reliable Read**: Marks messages read only after successful delivery or reliable queuing.

### 5.2 `useSwarmInitialization.ts`
Swarm startup — initializes the agent swarm on session start. Handles:
- **Agent Discovery**: Loads agent definitions from `.claude/agents/` directory.
- **Dependency Resolution**: Sorts agents by dependency order (some agents depend on others).
- **Resource Allocation**: Assigns initial tasks, starts polling.
- **Health Check**: Verifies agent connectivity and responsiveness.

### 5.3 `useSwarmPermissionPoller.ts` (331 lines)
Worker-side permission response poller — pairs with `handleSwarmWorkerPermission()` in `useCanUseTool`.

- **Scope:** Only active when `isSwarmWorker()` is true.
- **Polling:** `useInterval` every `POLL_INTERVAL_MS = 500` calls `pollForResponse()` from `utils/swarm/permissionSync` (mailbox/disk sync — not agent output directories).
- **Callback registry:** Module-level `pendingCallbacks` map; `registerSwarmPermissionCallback()` / `unregisterSwarmPermissionCallback()` called from worker permission flow when a request is outstanding.
- **Response handling:** Validates `permissionUpdates` with `permissionUpdateSchema`; invokes `onAllow(updatedInput, permissionUpdates, feedback?)` or `onReject(feedback?)`; cleans up via `removeWorkerResponse`.
- **Not** the team-lead inbox poller — that is `useInboxPoller.ts`.

### 5.4 Other Agent/Team Hooks

#### `useBackgroundTaskNavigation.ts`
Navigates between background tasks — keyboard shortcuts (Ctrl+B then N for next task, Ctrl+B then P for previous, Ctrl+B then K for kill). Shows task list overlay.

#### `useTaskListWatcher.ts`
Watches the task list directory for changes — new tasks, completed tasks, failed tasks. Updates AppState with task counts and statuses for the status line indicator.

#### `useTasksV2.ts` (250 lines)
Task management for the v2 task system — creates, monitors, and controls tasks. Handles: task creation with structured inputs, task status polling, task cancellation, task result extraction.

#### `useTeammateViewAutoExit.ts`
Auto-exits the teammate view when the sub-agent completes its task. Uses `useEffect` with dependency on task completion state.

---

## 6. Plugin Hooks

### 6.1 `useManagePlugins.ts` (304 lines)
Plugin lifecycle management — install, enable, disable, remove, update plugins. Handles:
- **Plugin Discovery**: Scans configured plugin sources (marketplace, local dirs, git repos).
- **Installation**: Downloads and installs plugins with dependency resolution.
- **Status**: Tracks plugin state: `not_installed`, `installing`, `installed`, `enabled`, `disabled`, `error`, `updating`.
- **Permissions**: Manages plugin permissions (filesystem access, network, shell, MCP tools).
- **Updates**: Checks for updates, downloads, and installs with restart prompt.

### 6.2 `usePluginRecommendationBase.tsx`
Base hook for plugin recommendations — determines when to suggest plugins to the user. Features:
- **Context Analysis**: Analyzes the user's workflow (languages used, tools referenced) to recommend relevant plugins.
- **Dismissal Tracking**: Tracks which recommendations have been dismissed (permanently or temporarily).
- **Frequency Control**: Limits recommendation frequency to avoid annoyance.

### 6.3 `useLspPluginRecommendation.tsx`
LSP-specific plugin recommendation — suggests LSP plugins when the user works with languages that benefit from IDE-like features (auto-complete, diagnostics, go-to-definition).

### 6.4 `useClaudeCodeHintRecommendation.tsx`
Claude Code hint recommendation — suggests the Claude Code IDE extension when relevant.

---

## 7. Content Hooks

### 7.1 `fileSuggestions.ts` (812 lines)
File/folder suggestion engine — backend for `@` mention completions in `useTypeahead`.

- **FileIndex:** Lazy singleton `getFileIndex()` → Rust `native-ts/file-index` (nucleo-style fuzzy scoring).
- **Background refresh:** `startBackgroundCacheRefresh()` — git `ls-files` + untracked merge; `.git/index` mtime triggers immediate rebuild; 5s time floor for untracked pickup. Signatures skip redundant `nucleo.restart()` when list unchanged.
- **Completion signal:** `onIndexBuildComplete` re-runs last typeahead query when a partial index finishes.
- **Ignore:** `.gitignore`, `.ignore`/`.rgignore` (cached per repoRoot:cwd), user exclusion patterns.
- **Exports used by typeahead:** `applyFileSuggestion`, `findLongestCommonPrefix`, hook-driven `executeFileSuggestionCommand` via `utils/hooks`.

### 7.2 `unifiedSuggestions.ts` (202 lines)
Merges suggestions from all sources into a single ranked list. Deduplicates by ID. Weighted ranking: commands > files > shell history > shell completions > Slack channels. Applies `fuse.js` fuzzy matching for the final sort.

### 7.3 `renderPlaceholder.ts`
Placeholder rendering utilities — renders dimmed placeholder text in inputs. Handles multi-line placeholders, wrapping, and cursor-aware positioning.

### 7.4 Content Utility Hooks

#### `useClipboardImageHint.ts`
Shows a hint when a clipboard image is available for pasting. Detects clipboard changes via polling. Renders a "Paste image" hint next to the input.

#### `useCopyOnSelect.ts`
Copies selected text to clipboard on mouse release. Uses OSC 52 for terminal-native clipboard (when supported) with fallback to system clipboard via `clipboardy`. Enforces a 5-minute clipboard permission prompt for security.

#### `usePromptSuggestion.ts`
Generates prompt suggestions based on context. Analyzes: open files, recent errors, git status, past commands. Shows suggestions as ghost text or in a suggestion bar.

#### `useSkillImprovementSurvey.ts`
Post-skill-use survey — prompts for feedback after a skill/tool is used. Tracks: which skills were used, user satisfaction, improvement suggestions.

#### `usePrStatus.ts`
Pull request status checker — polls for PR creation/merge status. Shows PR creation progress, review status, and merge result.

---

## 8. Notification Hooks (`notifs/` — 16 files)

### 8.1 `useAutoModeUnavailableNotification.ts`
Notifies when auto-mode cannot be activated (e.g., due to managed settings, sandbox restrictions).

### 8.2 `useCanSwitchToExistingSubscription.tsx`
Checks if the user can switch to an existing subscription — shows notification if eligible.

### 8.3 `useDeprecationWarningNotification.tsx`
Shows deprecation warnings for deprecated features, APIs, or configuration options. Checks against a deprecation schedule and shows warnings with migration guidance.

### 8.4 `useFastModeNotification.tsx` (162 lines)
Fast mode notification — shown when fast/normal mode is toggled. Explains behavior differences: tool approval requirements, model selection, thinking visibility.

### 8.5 `useIDEStatusIndicator.tsx` (186 lines)
IDE connection status in the UI — shows an icon in the status bar. States: disconnected (grey dot), connecting (yellow spinner), connected (green dot), error (red dot). Handles reconnection prompts.

### 8.6 `useInstallMessages.tsx`
Installation-related messages — first-run welcome, version update changelog, migration notices.

### 8.7 `useLspInitializationNotification.tsx`
LSP initialization progress — shows "Indexing..." or "LSP Ready" notifications. Tracks: language server download, project indexing, diagnostics population.

### 8.8 `useMcpConnectivityStatus.tsx`
MCP server connectivity monitoring — shows server status notifications. Tracks: `connected`, `connecting`, `disconnected`, `error`, `reconnecting`. Shows reconnect button.

### 8.9 `useModelMigrationNotifications.tsx`
Model migration notices — when a model is deprecated or a new default is set, shows migration guidance. Tracks: model deprecation dates, migration deadlines, auto-migration status.

### 8.10 `useNpmDeprecationNotification.tsx`
Shows deprecation notice when the installed npm package is deprecated in favor of a new package name or native distribution.

### 8.11 `usePluginAutoupdateNotification.tsx`
Plugin auto-update notifications — shows when plugins auto-updated, what changed, and restart prompts if needed.

### 8.12 `usePluginInstallationStatus.tsx` (128 lines)
Plugin installation progress — shows "Installing [plugin]..." with progress bar. Tracks: download progress, extraction, dependency installation, activation.

### 8.13 `useRateLimitWarningNotification.tsx` (114 lines)
Rate limit warning — shows remaining requests count, reset time countdown, and tier upgrade suggestions. Progressive: warning at 20% remaining, urgent at 5%.

### 8.14 `useSettingsErrors.tsx`
Settings validation errors — shows invalid settings with file path and line number. Offers quick-fix options. Integrates with `InvalidSettingsDialog`.

### 8.15 `useStartupNotification.ts`
Startup sequence — shows: version number, check for updates, new features banner, community announcements.

### 8.16 `useTeammateShutdownNotification.ts`
Notifies when a teammate/sub-agent shuts down. Shows: agent name, completion status, result summary.

### 8.17 `useOfficialMarketplaceNotification.tsx`
Official marketplace availability notification — shows when the official Claude Code plugin marketplace is available.

---

## 9. Virtual Scrolling & Layout Hooks

### 9.1 `useVirtualScroll.ts` (721 lines)
The virtual scrolling engine — the brains behind `VirtualMessageList`. Core algorithm:

**Height Tracking**:
- `heightCache: Map<key, number>` — measured heights for each rendered item.
- `DEFAULT_ESTIMATE = 3` rows for unmeasured items (intentionally low — overestimating causes blank space).
- `PESSIMISTIC_HEIGHT = 1` — worst-case height for coverage computation (guarantees mounted span reaches viewport bottom).

**Range Calculation**:
- `computeRange(scrollTop, viewportHeight)`: Find the first visible item by accumulating heights from `heightCache` (measured) + `DEFAULT_ESTIMATE` (unmeasured).
- `scrollClampMin` / `scrollClampMax`: Clamp scrollTop to the mounted range so burst scrolls show content edges instead of blank spacer.
- `overscanStart` / `overscanEnd`: `OVERSCAN_ROWS = 80` above and below viewport.

**Scroll Quantization**:
- `SCROLL_QUANTUM = OVERSCAN_ROWS >> 1 = 40` — React only re-renders when `scrollTop` crosses quantum boundaries.
- Uses `useSyncExternalStore` subscribing to `ScrollBoxHandle.subscribe()`, with `Math.trunc(scrollTop / SCROLL_QUANTUM) * SCROLL_QUANTUM` as the snapshot value.

**Sliding Window**:
- `SLIDE_STEP = 25` — max new items per commit for smooth progressive loading.
- `COLD_START_COUNT = 30` — items to mount before `ScrollBox` has laid out.
- `MAX_MOUNTED_ITEMS = 300` — cap to bound fiber allocation.

**Height Measurement**:
- Uses `useLayoutEffect` after each render to read `getComputedHeight()` from Yoga for newly mounted items.
- Invalidated when `columns` changes (text rewrap on resize).

### 9.2 `useScrollKeybindingHandler`
See `ScrollKeybindingHandler.tsx` in components — delegates scroll control to the component. This hook is the programmatic interface for scroll-related keyboard events.

### 9.3 `useTerminalSize.ts` (16 lines)
Reads `{ columns, rows }` from Ink's `TerminalSizeContext` (`src/ink/components/TerminalSizeContext.js`). Throws if used outside an Ink `<App>`. Re-exported widely by dialogs, suggestion overlays, and layout components (66+ importers) — not a stdout poll hook.

---

## 10. Voice Hooks

### 10.1 `useVoice.ts` (1144 lines)
Hold-to-talk voice input — the complete voice recording and transcription pipeline.

**Recording Flow**:
1. User holds the voice keybinding (configurable, default: V or F2).
2. Recording starts via the native audio module (macOS: `avfaudio`; Linux: SoX `rec`).
3. Audio is streamed to Anthropic's `voice_stream` STT endpoint via WebSocket.
4. Intermediate transcripts appear as ghost text.
5. On release: recording stops, final transcript is committed to the input field.
6. Auto-repeat detection: if no keypress arrives within `RELEASE_TIMEOUT_MS` (configurable), recording auto-stops.

**State Machine** (`VoiceState` in `useVoice.ts` — only three states):
- `idle` → `recording` (keybinding held, audio capture active) → `processing` (transcription in flight) → `idle`

**Context store** (`context/voice.tsx`): Separate `voiceWarmingUp` boolean and `voiceInterimTranscript`/`voiceAudioLevels`/`voiceError` fields shared via `VoiceProvider`; UI warmup hints use `voiceWarmingUp`, not an extra hook state.

**Language Support:** Maps language names → BCP-47 codes against `SUPPORTED_LANGUAGE_CODES` (GrowthBook `speech_to_text_voice_stream_config` subset: en, es, fr, ja, de, pt, it, ko, hi, id, ru, pl, tr, nl, uk, el, cs, da, sv, no). Unsupported inputs fall back to `en` with optional `fellBackFrom` warning — Chinese (`zh`) is **not** in the allowlist.

**Keyterms**: `getVoiceKeyterms()` — custom vocabulary boost for accurate transcription of code terms (function names, variable names, CLI commands).

**Audio Buffering**: Accumulates audio chunks in a buffer during WebSocket setup, sends them as the first message on connect. Prevents losing the first ~500ms of speech.

**Error Recovery**: WebSocket reconnection with exponential backoff. Graceful degradation: falls back to platform speech-to-text if the API is unavailable.

### 10.2 `useVoiceIntegration.tsx` (677 lines)
Voice integration with the prompt input — renders the voice button, recording indicator, level meter, and waveform cursor. Subscribes to `useVoiceState` from context. Handles: activation, recording feedback, transcription display, error messages.

### 10.3 `useVoiceEnabled.ts`
Checks if voice input is available — platform support, microphone permission, API availability. Returns `{ enabled, reason? }`.

---

## 11. State & Settings Hooks

### 11.1 `useSettings.ts` (18 lines)
Reactive settings accessor: `useAppState(s => s.settings)` returning `ReadonlySettings` (`AppState['settings']`). Updates when `settingsChangeDetector` detects on-disk changes — prefer over `getSettings_DEPRECATED()` in React components.

### 11.2 `useSettingsChange.ts`
Watches for settings changes — registers a callback that fires when a specific setting changes. Used for side-effects like: re-theming on theme change, reconnecting on API key change.

### 11.3 `useSkillsChange.ts`
Watches the skills directory for changes — new skills, modified skills, removed skills. Updates the skill registry. Uses file system polling with a debounce.

### 11.4 `useDynamicConfig.ts`
Dynamic configuration (GrowthBook/remote config) — checks feature flags, experiments, and remote settings. Handles: A/B test assignment, gradual rollouts, kill switches.

---

## 12. File & Diff Hooks

### 12.1 `useFileHistorySnapshotInit.ts`
Initializes file history tracking — takes a snapshot of file states before the session starts. Used for file restoration on session resume. Handles: git-aware snapshotting (reads from git when available), large-file batching, incremental snapshots.

### 12.2 `useDiffData.ts`
Computes diff statistics for display — reads git diff for the current session, counts additions/deletions/files. Caches results per message.

### 12.3 `useTurnDiffs.ts` (213 lines)
Tracks per-turn file changes — shows what files changed in each message turn. Computes cumulative and per-message diffs. Integrates with `MessageSelector` for restore preview.

---

## 13. Timing & Animation Hooks

| Hook | Description |
|------|-------------|
| `useMemoryUsage.ts` | Monitors process memory usage (RSS, heap) — shows in dev bar when enabled. |
| `useElapsedTime.ts` (38 lines) | Formatted elapsed duration via `useSyncExternalStore` + interval. Args: `startTime`, `isRunning`, `ms` (default 1000), `pausedMs`, optional `endTime` (freeze display for completed tasks). Returns strings like `"1m 23s"` from `formatDuration`. |
| `useMinDisplayTime.ts` | Enforces a minimum display time for transient UI (loading spinners, progress bars) to prevent flicker. |
| `useTimeout.ts` | `setTimeout` with automatic cleanup on unmount. Refs-based to avoid stale closure issues. |
| `useBlink.ts` | Blinking cursor/text — toggles boolean at configurable interval. Used for cursor blink and warning indicators. |
| `useDoublePress.ts` | Double-press detection — fires callback when the same key is pressed twice within a timeout. Used for double-Escape exit. |
| `useNotifyAfterTimeout.ts` | Shows a notification after a configurable timeout — used for "taking a while..." messages. |

---

## 14. Other Hooks

| Hook | Description |
|------|-------------|
| `useBookmarks.ts` | Bookmark management — save/restore cursor positions in message history. |
| `useScheduledTasks.ts` (139 lines) | Scheduled task runner — runs periodic maintenance tasks (cache cleanup, index refresh, update check). |
| `useLogMessages.ts` | Log message reader — reads and displays session transcript files. |
| `useAssistantHistory.ts` | Assistant message history — provides previous assistant messages for context. |
| `useAwaySummary.ts` (125 lines) | "While you were away" summary — shows what happened while the user was away (tool calls, errors, completions). |
| `useMergedClients.ts` | Merges API client configurations from multiple sources (user settings, managed settings, environment). |
| `useMergedCommands.ts` | Merges command registrations from plugins, built-in commands, and user-defined commands. |
| `useMergedTools.ts` | Merges tool registrations from MCP servers, plugins, and built-in tools. |
| `useSearchInput.ts` (364 lines) | Vim/less-style search field: `query`, `setQuery`, `cursorOffset`, `handleKeyDown`. Enter/down → `onExit`; up → `onExitUp`; Esc clears query or exits; optional `onCancel` for abandon. Kill ring (Ctrl+K/U/W/Y). Bridges legacy `useInput` pending `onKeyDown` migration. Used by LogSelector, QuickOpen, FuzzyPicker. |
| `useMainLoopModel.ts` (34 lines) | Resolved `ModelName` for next API call via `parseUserSpecifiedModel(session ?? global ?? default)`. Re-renders on `onGrowthBookRefresh` so alias overrides apply after GrowthBook init. |
| `useIssueFlagBanner.ts` | Shows issue/incident banner — fetches status page data and displays active incidents. |
| `useChromeExtensionNotification.tsx` | Prompts installation of the Claude in Chrome extension when relevant. |
| `useGlobalKeybindings.tsx` | Global keyboard shortcut registry — all keybindings that work regardless of focus. |
| `useMailboxBridge.ts` | Mailbox bridge connection — for agents receiving external messages. |
| `useUpdateNotification.ts` | Checks for app updates and shows notification. |
| `usePromptsFromClaudeInChrome.tsx` | Receives prompts sent from the Chrome extension. |
| `useDeferredHookMessages.ts` | Deferred hook message display — shows hook output with a delay for better UX. |

---

## 15. Hook Architecture Patterns

### State Management
- **Zustand-like slices**: Hooks use `useAppState(selector)` for global state; stable selectors prevent unnecessary re-renders.
- **Ref-based mutable state**: Performance-critical inner-loop state (cursor position, vim mode, scroll position) uses `useRef` to avoid triggering re-renders.
- **Context + Subscription**: Font-end design pattern where a context provider broadcasts via `useSyncExternalStore` for zero-re-render subscriptions (used by virtual scroll, scroll chrome).

### Input Processing
- **Keybinding context**: Hooks declare desired keybindings; the keybinding context resolves actual keys based on user customization.
- **Input filter pipeline**: `inputFilter → (input mapper → handler map) → Cursor operations` — composable input processing.
- **Modifier pre-warming**: `prewarmModifiers()` called on each keypress for the terminal modifier detection system.

### Side Effects
- **Cleanup on unmount**: All interval/timeout/animation-frame hooks return cleanup functions.
- **AbortSignal propagation**: Long-running operations respect `AbortSignal` for cancellation.
- **Error boundaries**: Errors in hooks are caught by Sentry error boundaries and displayed inline.

### Performance
- **Debouncing**: Network-dependent hooks (typeahead, search, file suggestions) use `useDebounceCallback`.
- **Lazy initialization**: Expensive resources (highlight.js, voice module, file index) are lazy-loaded on first use.
- **WeakMap caches**: Message text extraction, search results, and height measurements use `WeakMap` for automatic garbage collection.
- **Batched updates**: Multiple rapid state changes are batched (via `unstable_batchedUpdates` or React 18's automatic batching).
