# 08 Large Hooks — Deep Analysis

This document provides a complete analysis of 15 large React hooks used in the application's UI layer. Each analysis covers state management patterns, every function, effects, callbacks, dependencies, cleanup logic, and return values.

---

## 1. `useTypeahead.tsx` (1384 lines)

**File:** `F:\Claude\src\hooks\useTypeahead.tsx`

### Purpose
Command/skill typeahead autocomplete engine. Handles all suggestion types (commands, files, paths, agents, Slack channels, shell completions, custom titles) and keyboard navigation.

### State Variables
| Variable | Type | Purpose |
|----------|------|---------|
| `suggestionType` | `useState<SuggestionType>` | Current type of visible suggestions (`'none'`, `'command'`, `'file'`, `'directory'`, `'shell'`, `'agent'`, `'slack-channel'`, `'custom-title'`) |
| `maxColumnWidth` | `useState<number\|undefined>` | Fixed column width for command suggestions (computed from all commands to prevent layout shift) |
| `inlineGhostText` | `useState<InlineGhostText\|undefined>` | Async ghost text for bash history completion |
| `synchPromptGhostText` | `useMemo` | Synchronous ghost text for prompt-mode mid-input slash commands (avoids one-frame flicker) |

### Refs (11 total)
| Ref | Purpose |
|-----|---------|
| `cursorOffsetRef` | Current cursor offset, avoids re-triggering suggestions on cursor movement alone |
| `latestSearchTokenRef` | Latest file search token; discards stale async results |
| `prevInputRef` | Previous input value; detects actual text changes vs callback recreations |
| `latestPathTokenRef` | Latest path token; discards stale path completion results |
| `latestBashInputRef` | Latest bash input; discards stale history completion |
| `latestSlackTokenRef` | Latest Slack channel token; discards stale MCP results |
| `suggestionsRef` | Current suggestions; avoids recreating `updateSuggestions` on selection changes |
| `dismissedForInputRef` | Input value when suggestions were manually dismissed; prevents immediate re-trigger |

### Functions

#### Exported Helpers
- **`extractSearchToken(completionToken)`** — Strips `@` prefix and quotes from a completion token to get the raw search string. Handles quoted (`@"path"`) vs unquoted (`@path`) tokens.
- **`extractCompletionToken(text, cursorPos, includeAtSymbol)`** — Extracts the completable token at the cursor position. Handles quoted `@"...` tokens, `@path` tokens, and bare word tokens. Returns `{ token, startPos, isQuoted? }` or `null`.
- **`formatReplacementValue(options)`** — Formats a replacement value with proper `@` prefix and quotes based on mode (bash/prompt), existing prefix state, and whether quotes are needed (contains spaces).
- **`applyShellSuggestion(suggestion, input, cursorOffset, onInputChange, setCursorOffset, completionType)`** — Replaces the current word with a shell completion. Handles variable (`$`), command, and path completion types.
- **`applyDirectorySuggestion(input, suggestionId, tokenStartPos, tokenLength, isDirectory)`** — Replaces a path token with `@suggestionId/` (directory) or `@suggestionId ` (file). Returns new input text and cursor position.
- **`isPathMetadata(metadata)`** — Type guard checking if metadata has a `type` field (`'directory'` or `'file'`).

#### Internal Helpers
- **`getPreservedSelection(prev, prevIdx, newSugs)`** — When suggestions change, preserves the selected item by ID. Falls back to index 0 if item not found.
- **`buildResumeInputFromSuggestion(suggestion)`** — Builds `/resume <sessionId>` or `/resume <title>` from a suggestion's metadata.
- **`extractCommandNameAndArgs(value)`** — Parses a `/command args...` string into `{commandName, args}`.
- **`hasCommandWithArguments(isAtEnd, value)`** — Checks if a command has arguments without trailing whitespace (user is editing).

#### Core Callbacks
- **`clearSuggestions()`** — Resets `suggestions`, `selectedSuggestion`, `commandArgumentHint`, `suggestionType`, `maxColumnWidth`, and `inlineGhostText`.
- **`fetchFileSuggestions(searchToken, isAtSymbol)`** — Async: calls `generateUnifiedSuggestions` for file/MCP resource/agent suggestions. Discards stale results by comparing `latestSearchTokenRef`.
- **`fetchSlackChannels(partial)`** — Async: calls `getSlackChannelSuggestions` for Slack channel completions.
- **`updateSuggestions(value, cursorOffset?)`** — **The central suggestion controller (533-884 lines)**. Sequential priority logic:
  1. If suppressed, cancel everything and clear
  2. Check mid-input slash commands in prompt mode → ghost text
  3. Bash mode: check shell history for ghost text
  4. Check `@` for team member/subagent suggestions
  5. Check `#` for Slack channel suggestions
  6. Check `/` for command suggestions with argument hints
  7. Handle `/add-dir` directory completion
  8. Handle `/resume` custom title completion
  9. Check `@` for file/MCP path suggestions
  10. Maintain active `file`/`shell`/`agent`/`custom-title` suggestions
- **`handleTab()`** — Tab key handler (911-1134 lines). Applies ghost text or completes current selection. Complex branching by `suggestionType`:
  - Ghost text: replaces with full command
  - `command`: applies via `applyCommandSuggestion`
  - `custom-title`: builds resume input
  - `directory`: applies directory suggestion with recursive re-fetch for directories
  - `shell`: applies shell completion
  - `agent`: applies trigger suggestion with `DM_MEMBER_RE`
  - `slack-channel`: applies trigger suggestion with `HASH_CHANNEL_RE`
  - `file`: common prefix completion or full suggestion, with `formatReplacementValue`
  - No suggestions: generates bash suggestions or file suggestions
- **`handleEnter()`** — Enter key handler (1137-1225 lines). Applies and executes the selected suggestion. Same type-based branching as `handleTab` but also submits commands via `onSubmit`.
- **`handleAutocompleteAccept/Dismiss/Previous/Next`** — Keybinding action handlers for the autocomplete overlay.

#### Keyboard Handlers
- **`handleKeyDown(e)`** — KeyboardEvent handler (1294-1362 lines):
  - Right arrow: accepts prompt suggestion ghost text
  - Tab (no shift): thinking toggle reminder on empty input
  - Ctrl+N/P: navigate suggestions (guards against chord sequences)
  - Enter (no shift/meta): selects and executes suggestion
- **`acceptSuggestionText(text)`** — Detects input mode and applies suggestion text.

### Effects
1. **Pre-warm file index** (`useEffect`, lines 494-505): On mount, starts background cache refresh. Subscribes to `onIndexBuildComplete` to re-fire file search when index is ready. Skipped in test environment.
2. **Update suggestions on input change** (`useEffect`, lines 893-908): Fires `updateSuggestions` when input text changes. Resets `latestSearchTokenRef` and `dismissedForInputRef` on actual text changes.

### Keybindings Registration
- Registers `Autocomplete` keybinding context when suggestions are active
- Registers `autocomplete` overlay for ESC deferral
- Binds `autocomplete:accept/dismiss/previous/next` with `isAutocompleteActive && !isModalOverlayActive` guard

### Return Value
```typescript
{
  suggestions: SuggestionItem[],
  selectedSuggestion: number,
  suggestionType: SuggestionType,
  maxColumnWidth?: number,
  commandArgumentHint?: string,
  inlineGhostText?: InlineGhostText,
  handleKeyDown: (e: KeyboardEvent) => void
}
```

### Regex Patterns (module-level constants)
- `AT_TOKEN_HEAD_RE`: Matches `@` followed by Unicode letters/numbers/marks and path characters
- `PATH_CHAR_HEAD_RE`: Matches path characters at word start
- `TOKEN_WITH_AT_RE`: Matches tokens that may include `@`
- `TOKEN_WITHOUT_AT_RE`: Matches bare word tokens
- `HAS_AT_SYMBOL_RE`: Detects `@` symbol with following path chars
- `HASH_CHANNEL_RE`: Matches `#channel-name` for Slack
- `DM_MEMBER_RE`: Matches `@member-name` for DM

### Module-Level State
- `currentShellCompletionAbortController`: Global AbortController for shell completion cancellations

### Performance Patterns
- `useDebounceCallback` on file suggestions (50ms) and Slack channels (150ms)
- `useMemo` for `allCommandsMaxWidth` and `synchPromptGhostText`
- Ref-based cursor offset to avoid re-renders on cursor movement
- Stale-request detection via token refs before showing results
- `getPreservedSelection` for smooth selection transitions

---

## 2. `useVoice.ts` (1144 lines)

**File:** `F:\Claude\src\hooks\useVoice.ts`

### Purpose
Hold-to-talk voice input using Anthropic's `voice_stream` STT endpoint. Manages recording lifecycle, WebSocket audio streaming, transcription accumulation, and audio level computation.

### State Variables
| Variable | Type | Purpose |
|----------|------|---------|
| `state` | `useState<VoiceState>` | Current voice state: `'idle'`, `'recording'`, or `'processing'` |

### Refs (17 total)
| Ref | Purpose |
|-----|---------|
| `stateRef` | Mirrors `state` for synchronous reads in callbacks |
| `connectionRef` | Active `VoiceStreamConnection` for WebSocket audio streaming |
| `accumulatedRef` | Accumulated final transcript text |
| `onTranscriptRef` | Current `onTranscript` callback (avoids stale closures) |
| `onErrorRef` | Current `onError` callback |
| `cleanupTimerRef` | Timer for cleanup operations |
| `releaseTimerRef` | Key release detection timer (200ms gap = release) |
| `seenRepeatRef` | Whether auto-repeat has been detected (gates release timer) |
| `repeatFallbackTimerRef` | Fallback timer if no auto-repeat arrives (600ms) |
| `focusTriggeredRef` | Whether current recording was started by terminal focus |
| `focusSilenceTimerRef` | Timer to tear down focus-mode session after 5s of silence |
| `silenceTimedOutRef` | Whether focus session was torn down due to silence |
| `recordingStartRef` | Timestamp of recording start |
| `sessionGenRef` | Monotonically increasing generation counter for session staleness detection |
| `retryUsedRef` | Whether early-error retry was used in this session |
| `fullAudioRef` | Buffer of all audio chunks for silent-drop replay |
| `silentDropRetriedRef` | Whether silent-drop replay was attempted |
| `attemptGenRef` | Generation counter for connection attempts (below session level) |
| `focusFlushedCharsRef` | Total chars flushed in focus mode (for analytics accuracy) |
| `hasAudioSignalRef` | Whether any chunk with non-trivial signal was received |
| `everConnectedRef` | Whether WebSocket onReady fired for this session |
| `audioLevelsRef` | Audio level histogram (last 16 bars for visualizer) |

### Functions

#### Exported
- **`computeLevel(chunk: Buffer)`** — Computes RMS amplitude from 16-bit signed PCM buffer. Returns normalized 0-1 value with sqrt curve for better visual distribution.
- **`normalizeLanguageForSTT(language)`** — Normalizes a language string to a BCP-47 code. Has a lookup table (`LANGUAGE_NAME_TO_CODE`) mapping 20 languages (including native names like `日本語`→`ja`). Falls back to `'en'` if unsupported. Returns `{code, fellBackFrom?}`.

#### Internal
- **`updateState(newState)`** — Synchronously updates `stateRef`, React state, and pushes to the voice context store.
- **`cleanup()`** — Full cleanup: increments `sessionGenRef` (stales all in-flight work), clears all timers, stops recording, closes WebSocket, resets accumulated text and audio levels.
- **`finishRecording()`** — Stops recording, transitions to `'processing'`, calls `voiceModule.stopRecording()`, captures metrics before async boundary, sends `finalize()` to WebSocket. In the `.then()`:
  - Detects silent-drop signature (no_data_timeout + hadAudioSignal + wsConnected)
  - Replays buffered audio on fresh WebSocket connection
  - Assembles final transcript and emits `tengu_voice_recording_completed` analytics
  - Shows appropriate error messages for: WS never connected, no audio signal, or no speech detected
- **`armFocusSilenceTimer()`** — Arms/resets a 5-second timer. When it fires and the session is focus-triggered, calls `finishRecording()`.
- **`startRecordingSession()`** — Main recording start function. Steps:
  1. Synchronously sets state to `'recording'` (prevents race conditions)
  2. Checks recording availability via `voiceModule.checkRecordingAvailability()`
  3. Starts audio capture with buffering (audio held until WebSocket opens)
  4. Normalizes language and emits `tengu_voice_recording_started` analytics
  5. Gets keyterms and attempts WebSocket connection with retry logic
  6. `attemptConnect(keyterms)`: connects voice stream with:
     - `onTranscript`: handles final transcripts (accumulate or flush in focus mode) and interim transcripts
     - `onError`: early-failure retry (once, after 250ms backoff), fatal error propagation
     - `onReady`: assigns `connectionRef`, flushes buffered audio in 32KB coalesced slices, arms release timer
  7. On connect failure (no OAuth): shows error, cleans up

### Effects
1. **Lazy-load voice module** (`useEffect`, lines 530-536): When `enabled` becomes true, dynamically imports `voice.ts`. Avoids triggering TCC microphone permission prompt on macOS until voice is actually activated.
2. **Focus-driven recording** (`useEffect`, lines 576-630): When in focus mode, starts recording on focus gain and stops on blur. Respects `silenceTimedOutRef` to prevent immediate restart after silence timeout. Cancellation handled via `cancelled` flag.
3. **Disable cleanup** (`useEffect`, lines 1130-1138): When `enabled` becomes false and state is not idle, calls `cleanup()`. Also cleans up on unmount.

### Cleanup
- `useEffect` return (line 1135-1137): Calls `cleanup()` on unmount
- Focus mode effect return (line 627-629): Sets `cancelled = true`
- Module lazy-load effect: no cleanup needed

### Return Value
```typescript
{
  state: VoiceState,          // 'idle' | 'recording' | 'processing'
  handleKeyEvent: (fallbackMs?: number) => void
}
```

### Constants
| Constant | Value | Purpose |
|----------|-------|---------|
| `RELEASE_TIMEOUT_MS` | 200 | Gap between key events signaling release |
| `REPEAT_FALLBACK_MS` | 600 | Default fallback for release timer arming |
| `FIRST_PRESS_FALLBACK_MS` | 2000 | Fallback for modifier-combo first press |
| `FOCUS_SILENCE_TIMEOUT_MS` | 5000 | Silence before tearing down focus session |
| `AUDIO_LEVEL_BARS` | 16 | Number of waveform visualization bars |
| `SUPPORTED_LANGUAGE_CODES` | Set(20) | BCP-47 codes accepted by the backend |
| `LANGUAGE_NAME_TO_CODE` | Record(34 entries) | Maps language names to codes |

### Key Design Patterns
- **Session generation counter**: `sessionGenRef++` before starting; all callbacks check `isStale()` before acting. Prevents zombie WebSockets from abandoned sessions from corrupting state.
- **Attempt generation counter**: Same pattern one level down for connection retry attempts.
- **Buffer-while-connecting**: Audio capture starts immediately, chunks are buffered. When WebSocket opens, buffer is flushed in 32KB coalesced slices.
- **Release detection via auto-repeat**: On first keypress, starts recording. Release is detected by a 200ms gap between auto-repeat events. A fallback timer (600ms) handles taps without auto-repeat.
- **Focus-mode continuous transcription**: Each final transcript is flushed immediately and `accumulatedRef` is reset. `focusFlushedCharsRef` tracks total for analytics.
- **Silent-drop replay**: When the server receives audio but returns no transcript (known ~1% bug), the full audio buffer is replayed on a fresh WebSocket after 250ms backoff.

---

## 3. `useInboxPoller.ts` (969 lines)

**File:** `F:\Claude\src\hooks\useInboxPoller.ts`

### Purpose
Polls the teammate inbox system for incoming messages from other sessions/agents. Routes permission requests, sandbox requests, shutdown requests, plan approvals, team permission updates, and regular messages. Works for both team leads and teammates.

### State
No local React state; uses `useAppState` for `inbox.messages.length` and reads imperatively from `useAppStateStore().getState()`.

### Props
| Prop | Type | Purpose |
|------|------|---------|
| `enabled` | `boolean` | Whether polling is active |
| `isLoading` | `boolean` | Whether session is busy (determines immediate vs queued delivery) |
| `focusedInputDialog` | `string\|undefined` | Whether a dialog has focus |
| `onSubmitMessage` | `(formatted: string) => boolean` | Submits formatted message as a new turn |

### Refs
| Ref | Purpose |
|-----|---------|
| `hasDoneInitialPollRef` | Guards initial poll to run only once |

### Functions

- **`getAgentNameToPoll(appState)`** — Determines which agent name to poll. Returns `undefined` for:
  - In-process teammates (they use `waitForNextPromptOrShutdown` instead)
  - Non-team standalone sessions
  Returns agent name for process-based teammates and team leads.

#### Core Poll Callback
- **`poll()`** (lines 139-873) — The main polling function. Steps:
  1. If not enabled or no agent name, return
  2. Call `readUnreadMessages(agentName, teamName)`
  3. **Plan approval response processing** (teammate side): Checks `isPlanApprovalResponse()` for each message from `'team-lead'`. If approved, applies `permissionMode` via `applyPermissionUpdate` (setMode). Ignores approvals from non-leaders.
  4. **Message classification**: Iterates unread messages and classifies each:
     - `permissionRequests` → `isPermissionRequest()`
     - `permissionResponses` → `isPermissionResponse()`
     - `sandboxPermissionRequests` → `isSandboxPermissionRequest()`
     - `sandboxPermissionResponses` → `isSandboxPermissionResponse()`
     - `shutdownRequests` → `isShutdownRequest()`
     - `shutdownApprovals` → `isShutdownApproved()`
     - `teamPermissionUpdates` → `isTeamPermissionUpdate()`
     - `modeSetRequests` → `isModeSetRequest()`
     - `planApprovalRequests` → `isPlanApprovalRequest()`
     - `regularMessages` → everything else
  5. **Permission requests (leader side)**: Routes to `ToolUseConfirmQueue` via `getLeaderToolUseConfirmQueue()`. Each request becomes a `ToolUseConfirm` entry with `onAbort`, `onAllow`, `onReject` handlers that send responses via `sendPermissionResponseViaMailbox`. Deduplicates by `tool_use_id`. Sends desktop notification.
  6. **Permission responses (worker side)**: Invokes registered callbacks via `processMailboxPermissionResponse()`.
  7. **Sandbox permission requests (leader side)**: Adds to `workerSandboxPermissions.queue` in AppState. Sends desktop notification.
  8. **Sandbox permission responses (worker side)**: Invokes callbacks via `processSandboxPermissionResponse()`, clears `pendingSandboxRequest`.
  9. **Team permission updates (worker side)**: Parses and applies via `applyPermissionUpdate({ type: 'addRules' })`.
  10. **Mode set requests (worker side)**: Only accepts from `'team-lead'`. Updates local permission context and calls `setMemberMode()`.
  11. **Plan approval requests (leader side)**: Auto-approves, writes approval response to teammate's mailbox with inherited permission mode, updates in-process teammate task state.
  12. **Shutdown requests (worker side)**: Passes through as regular messages.
  13. **Shutdown approvals (leader side)**: Kills the teammate's pane via backend, removes teammate from team file, unassigns tasks, marks tasks as completed, sends termination notification.
  14. **Regular message delivery**: If idle, submits immediately via `onSubmitTeammateMessage()`. If busy, queues in `AppState.inbox`.
  15. **Mark as read**: Called after successful delivery or reliable queuing.

### Effects
1. **Idle delivery** (`useEffect`, lines 876-950): When session becomes idle (`!isLoading && !focusedInputDialog`):
   - Cleans up processed messages (delivered mid-turn as attachments)
   - Formats and submits pending messages
   - Clears submitted messages from AppState

### Polling
- **Interval poll** (line 954): Uses `useInterval` at 1000ms when `shouldPoll` is true.
- **Initial poll** (lines 958-968): Runs once on mount if enabled and agent name is resolved.

### Dependencies
- `poll()`: `[enabled, isLoading, focusedInputDialog, onSubmitTeammateMessage, setAppState, terminal, store]`
- Idle effect: `[enabled, isLoading, focusedInputDialog, onSubmitTeammateMessage, setAppState, inboxMessageCount, store]`

### Return Value
Void — this hook operates via side effects (polling, AppState mutations).

### Key Design Patterns
- **Imperative store reads**: `store.getState()` avoids stale closures and infinite re-render loops
- **Message classification precedence**: Permission-related messages are extracted before regular messages, ensuring they're handled first
- **Defensive deduplication**: Permission requests are deduplicated by `tool_use_id` in case `markMessagesAsRead` failed on a prior poll
- **Reliable delivery guarantee**: Messages are only marked as read after successful delivery or reliable queuing, preventing permanent message loss

---

## 4. `useReplBridge.tsx` (723 lines)

**File:** `F:\Claude\src\hooks\useReplBridge.tsx`

### Purpose
Initializes an always-on bridge connection to `claude.ai` (Remote Control). Handles inbound/outbound message forwarding, permission bridging, model/mode sync, and crash recovery via perpetual session mode.

### Props
| Prop | Type | Purpose |
|------|------|---------|
| `messages` | `Message[]` | Full conversation history |
| `setMessages` | `React.Dispatch` | Message array setter |
| `abortControllerRef` | `RefObject<AbortController>` | For remote interrupt |
| `commands` | `readonly Command[]` | Available slash commands |
| `mainLoopModel` | `string` | Current model name |

### Refs (9 total)
| Ref | Purpose |
|-----|---------|
| `handleRef` | Current `ReplBridgeHandle` |
| `teardownPromiseRef` | In-flight teardown promise (awaited before re-init) |
| `lastWrittenIndexRef` | Index of last message written to bridge |
| `flushedUUIDsRef` | Set of UUIDs already flushed (prevents duplicate sends) |
| `failureTimeoutRef` | Timer to auto-disable bridge after failure |
| `consecutiveFailuresRef` | Count of consecutive init failures (max 3 before session fuse) |
| `commandsRef` | Current commands (avoids stale closures in callbacks) |
| `mainLoopModelRef` | Current model |
| `messagesRef` | Current messages |

### AppState Selectors
- `replBridgeEnabled` — Whether bridge mode is enabled
- `replBridgeConnected` — Whether bridge is currently connected
- `replBridgeOutboundOnly` — Mirror mode (no inbound)
- `replBridgeInitialName` — Optional initial session name

### Functions

#### handleInboundMessage(msg)
Async handler for inbound messages from `claude.ai`:
1. Extracts message fields via `extractInboundMessageFields()`
2. Sanitizes webhook content (if `KAIROS_GITHUB_WEBHOOKS` feature)
3. Resolves file attachments via `resolveAndPrepend()`
4. Enqueues via `enqueue()` with `bridgeOrigin: true`

#### handleStateChange(state, detail)
Maps bridge lifecycle events to AppState:
- `'ready'`: Sets `replBridgeConnected`, connect URL and session URL
- `'connected'`: Sets `replBridgeSessionActive`, sends system/init with tools/commands/agents/skills
- `'reconnecting'`: Sets `replBridgeReconnecting`
- `'failed'`: Shows notification, sets error, auto-disables after `BRIDGE_FAILURE_DISMISS_MS` (10s)

#### handlePermissionResponse(msg)
Dispatches incoming `control_response` messages to registered `pendingPermissionHandlers` by `request_id`.

#### onSetPermissionMode(mode)
Policy-guarded permission mode change:
1. `bypassPermissions`: checks if disabled or unavailable
2. `auto`: checks transcript classifier gate
3. Applies via `transitionPermissionMode()`
4. Rechecks queued permission prompts

#### sendBridgeResult()
Sends result signal to the bridge.

### Effects

#### Init/Teardown Effect (lines 95-680)
Dependencies: `[replBridgeEnabled, replBridgeOutboundOnly, setAppState, setMessages, addNotification]`

When `replBridgeEnabled` becomes true:
1. Checks consecutive failures fuse (max 3)
2. Waits for previous teardown to complete
3. Dynamically imports `initReplBridge` and `shouldShowAppUpgradeMessage`
4. Checks for perpetual mode (assistant mode for crash recovery)
5. Calls `initReplBridge()` with:
   - `onInboundMessage`: `handleInboundMessage`
   - `onPermissionResponse`: `handlePermissionResponse`
   - `onInterrupt`: aborts current controller
   - `onSetModel`: updates `mainLoopModelForSession`
   - `onSetMaxThinkingTokens`: toggles `thinkingEnabled`
   - `onSetPermissionMode`: policy-guarded mode change
   - `onStateChange`: `handleStateChange`
   - `initialMessages`: current messages (skip by `lastWrittenIndexRef` for reconnects)
   - `previouslyFlushedUUIDs`: dedup set
6. On success: stores handle, resets consecutive failures, builds permission callbacks, creates bridge status message
7. On failure: increments failures, shows error, auto-disables after 10s

Cleanup: tears down bridge, clears AppState bridge fields, resets `lastWrittenIndexRef`.

#### Forwarding Effect (lines 685-713)
Dependencies: `[messages, replBridgeConnected]`

When connected, forwards new user/assistant/system-local_command messages to the bridge from `lastWrittenIndexRef` onwards. Handles compaction clamping.

### Return Value
```typescript
{ sendBridgeResult: () => void }
```

### Constants
| Constant | Value | Purpose |
|----------|-------|---------|
| `BRIDGE_FAILURE_DISMISS_MS` | 10000 | Auto-disable timeout after failure |
| `MAX_CONSECUTIVE_INIT_FAILURES` | 3 | Session fuse for unrecoverable failures |

### Key Design Patterns
- **Perpetual session**: Assistant mode bridges clear the file pointer on teardown only for crash-recovery
- **UUID dedup**: `flushedUUIDsRef` persists across reconnections; same UUID sent twice kills the WebSocket
- **Consecutive failure fuse**: After 3 failures, bridge is permanently disabled for the session
- **Permission callbacks pattern**: `pendingPermissionHandlers` map for request-response matching with cleanup-on-return

---

## 5. `useVirtualScroll.ts` (721 lines)

**File:** `F:\Claude\src\hooks\useVirtualScroll.ts`

### Purpose
React-level virtualization for items inside a ScrollBox. Mounts only items in viewport + overscan, using spacer boxes for others at O(1) fiber cost each. Works with Ink's Yoga layout.

### State
No React state. Uses refs for all mutable data to avoid extra commits.

### Refs (10 total)
| Ref | Purpose |
|-----|---------|
| `heightCache` | `Map<string, number>` — measured Yoga heights for items |
| `offsetVersionRef` | Version counter bumped when heightCache mutates |
| `lastScrollTopRef` | scrollTop at last commit (for velocity detection) |
| `offsetsRef` | Cached `{arr: Float64Array, version, n}` — cumulative Y-offsets |
| `itemRefs` | `Map<string, DOMElement>` — mounted DOM elements by key |
| `refCache` | `Map<string, (el) => void>` — stable per-key callback refs |
| `prevColumns` | Previous column count (for resize scaling) |
| `skipMeasurementRef` | Whether to skip height measurement this frame |
| `prevRangeRef` | Previous mount range (for slide cap and unmount guard) |
| `freezeRendersRef` | Number of renders to freeze range (resize settling) |
| `listOriginRef` | Content-wrapper-relative Y origin of the virtualized list |
| `spacerRef` | DOM element ref for the top spacer |

### Constants
| Constant | Value | Purpose |
|----------|-------|---------|
| `DEFAULT_ESTIMATE` | 3 | Height (rows) for unmeasured items |
| `OVERSCAN_ROWS` | 80 | Extra rows above/below viewport |
| `COLD_START_COUNT` | 30 | Items rendered before first layout |
| `SCROLL_QUANTUM` | 40 | ScrollTop quantization bin size |
| `PESSIMISTIC_HEIGHT` | 1 | Worst-case height for unmeasured items (coverage guarantee) |
| `MAX_MOUNTED_ITEMS` | 300 | Cap on mounted fiber allocation |
| `SLIDE_STEP` | 25 | Max new items per commit in fast-scroll mode |

### Functions

#### Resize Handling (inline in render, lines 193-202)
When `columns` changes:
1. Scales all cached heights by `oldCols / newCols`
2. Bumps `offsetVersionRef`
3. Sets `skipMeasurementRef = true` (skip pre-resize Yoga)
4. Freezes range for 2 renders (pre- and post-resize Yoga settle)

#### Offset Computation (lines 296-310)
Rebuilds cumulative offsets when `offsetVersionRef` or `n` changes. Reuses `Float64Array` buffer. Uses `DEFAULT_ESTIMATE` (3) for unmeasured items.

#### Range Computation (lines 314-479)
Complex range calculation:

1. **Frozen range** (resize settling): keeps pre-resize range, clamped to `n`
2. **Cold start** (viewportH === 0): renders last `COLD_START_COUNT` (30) items
3. **Sticky (pinned to bottom)**: walks back from tail covering `viewportH + OVERSCAN_ROWS`
4. **Scrolled up**: 
   - Computes `effLo`/`effHi` spanning `[committed, target]` scroll positions
   - Caps span to `viewportH * 3` to prevent death spiral
   - Subtracts `listOrigin` for content-wrapper offset
   - Binary search for `start` in O(log n)
   - Guards against unmounting mounted-but-unmeasured items
   - Walks `end` forward using `PESSIMISTIC_HEIGHT` (1) for unmeasured items
   - Coverage back-check for at-bottom path
   - **Slide cap**: When scroll velocity > 2×viewportH, limits range growth to `SLIDE_STEP` (25) items
5. **Deferred range** (useDeferredValue): Time-slices fresh mounts
   - Only defers range GROWTH (shrinking is cheap)
   - Bypasses deferral when sticky or scrolling down
   - Final O(viewport) enforcement via `MAX_MOUNTED_ITEMS`

#### Clamp Bounds (useLayoutEffect, lines 591-597)
Sets `scrollRef.current.setClampBounds(clampMin, clampMax)` on each commit:
- `clampMin`: allows scrolling past listOrigin when no unmounted items above
- `clampMax`: Infinity when tail is mounted (avoids clamping streaming items)
- Skipped when sticky (render-node-to-output handles pinning)

#### Height Measurement (useLayoutEffect, lines 619-645)
Reads Yoga heights from previous Ink render:
1. Reads `listOrigin` from spacer's Yoga `computedTop`
2. Skips if `skipMeasurementRef` is set (resize settling)
3. Iterates `itemRefs`, reads `yogaNode.getComputedHeight()`
4. Writes to `heightCache` if changed
5. Handles `h=0` special case: distinguished "Yoga hasn't run" (transient) from "MessageRow rendered null" (permanent) by checking `getComputedWidth() > 0`
6. Bumps `offsetVersionRef` if any changes (no setState — propagates on next render)

#### Imperative Helpers
- **`measureRef(key)`**: Returns stable callback ref. On mount: stores element in `itemRefs`. On unmount: captures final height, cleans up.
- **`getItemTop(index)`**: Returns Yoga `computedTop` for item, or -1 if not measured.
- **`getItemElement(index)`**: Returns DOM element for item, or null.
- **`getItemHeight(index)`**: Returns cached height or undefined.
- **`scrollToIndex(i)`**: Scrolls to `offsets[i] + listOrigin`.

#### Scroll Subscription (useSyncExternalStore, lines 233-244)
Subscribes to ScrollBox imperative scroll. Snapshot is **quantized** `scrollTop / SCROLL_QUANTUM` so most wheel ticks (3-5 per notch) don't trigger React commits. Uses `target` (scrollTop + pendingDelta) for forward-looking range computation. Sticky state encoded in sign bit.

### Return Value
```typescript
{
  range: readonly [number, number],   // [effStart, effEnd) half-open
  topSpacer: number,                  // Height of top spacer in rows
  bottomSpacer: number,               // Height of bottom spacer in rows
  measureRef: (key: string) => (el: DOMElement | null) => void,
  spacerRef: RefObject<DOMElement | null>,
  offsets: ArrayLike<number>,         // Cumulative offsets per item
  getItemTop: (index: number) => number,
  getItemElement: (index: number) => DOMElement | null,
  getItemHeight: (index: number) => number | undefined,
  scrollToIndex: (i: number) => void
}
```

### Key Design Patterns
- **Offset version system**: Ref-based version counter avoids setState for cache invalidation
- **Pessimistic coverage**: Assumes unmeasured items are 1 row tall to guarantee viewport is never blank
- **Fast-scroll death spiral prevention**: Caps span to 3×viewportH, limits growth to SLIDE_STEP per commit
- **useDeferredValue for time-slicing**: Background renders for expensive fresh mounts
- **useSyncExternalStore for quantization**: Reduces React commits by quantizing scroll position

---

## 6. `useRemoteSession.ts` (605 lines)

**File:** `F:\Claude\src\hooks\useRemoteSession.ts`

### Purpose
Manages a remote CCR session connection in the REPL. Handles WebSocket connection, SDK message conversion, user input sending, permission request flow, and reconnection.

### Props
| Prop | Type | Purpose |
|------|------|---------|
| `config` | `RemoteSessionConfig\|undefined` | Session configuration (sessionId, viewerOnly, etc.) |
| `setMessages` | `React.Dispatch` | Message array setter |
| `setIsLoading` | `(loading: boolean) => void` | Loading state setter |
| `onInit` | `(slashCommands: string[]) => void` | Init callback with available commands |
| `setToolUseConfirmQueue` | `React.Dispatch` | Tool permission queue setter |
| `tools` | `Tool[]` | Available tools |
| `setStreamingToolUses` | `React.Dispatch?` | Streaming tool uses state |
| `setStreamMode` | `React.Dispatch?` | Spinner mode state |
| `setInProgressToolUseIDs` | `(f: (prev: Set<string>) => Set<string>) => void?` | In-progress tool IDs |

### Refs
| Ref | Purpose |
|-----|---------|
| `runningTaskIdsRef` | Set of running remote subagent task IDs |
| `responseTimeoutRef` | Timer for detecting stuck sessions (60s / 180s during compaction) |
| `isCompactingRef` | Whether remote session is compacting |
| `managerRef` | Current `RemoteSessionManager` instance |
| `hasUpdatedTitleRef` | Whether session title has been auto-updated |
| `sentUUIDsRef` | `BoundedUUIDSet(50)` of locally-sent message UUIDs (echo filter) |
| `toolsRef` | Current tools (avoids stale closures) |

### Functions

- **`setConnStatus(s)`** — `useCallback`: Updates `remoteConnectionStatus` in AppState.
- **`writeTaskCount()`** — `useCallback`: Writes `runningTaskIdsRef.size` to `remoteBackgroundTaskCount`.

#### sendMessage(content, opts?)
Async: Sends user message to remote session:
1. Validates manager exists
2. Clears existing timeout
3. Sets loading true
4. Records UUID in `sentUUIDsRef` (for echo filtering)
5. Calls `manager.sendMessage()`
6. Updates session title after first message (if `!hasInitialPrompt && !viewerOnly`)
7. Arms response timeout (60s normal, 180s during compaction)

#### cancelRequest()
Clears timeout, sends interrupt to CCR (unless viewerOnly), sets loading false.

#### disconnect()
Clears timeout, disconnects manager, nulls ref.

### Effects

#### Init Effect (lines 146-469)
Dependencies: `[config, setMessages, setIsLoading, onInit, setToolUseConfirmQueue, setStreamingToolUses, setStreamMode, setInProgressToolUseIDs, setConnStatus, writeTaskCount]`

When `config` is provided:
1. Creates `RemoteSessionManager` with callbacks:
   - **`onMessage(sdkMessage)`**:
     - Logs message type/subtype
     - Clears response timeout on any message (heartbeat)
     - **Echo filter**: Drops user messages with known UUIDs
     - **Init handler**: Extracts slash commands for `onInit`
     - **Task lifecycle**: Tracks `task_started`/`task_notification`/`task_progress`
     - **Compaction tracking**: Monitors `status='compacting'` and `compact_boundary`
     - **Session end**: Sets loading false
     - **Tool result cleanup**: Removes tool_use IDs from in-progress set
     - **Message conversion**: `convertSDKMessage()` with viewerOnly options
     - **Tool use tracking**: Marks tool_use IDs as in-progress
     - **Stream events**: Handles via `handleMessageFromStream`
   - **`onPermissionRequest(request, requestId)`**:
     - Creates `ToolUseConfirm` with onAbort/onAllow/onReject handlers
     - Handlers call `manager.respondToPermissionRequest()`
     - Pauses loading indicator
   - **`onPermissionCancelled(requestId, toolUseId)`**:
     - Removes from queue
     - Resumes loading
   - **`onConnected`**: Sets status to `'connected'`
   - **`onReconnecting`**: Sets status to `'reconnecting'`, clears task/TOOL_USE sets
   - **`onDisconnected`**: Sets status to `'disconnected'`, clears loading and sets
   - **`onError`**: Logs error
2. Calls `manager.connect()`
3. Cleanup: clears timeout, disconnects manager

### Return Value (useMemo stable reference)
```typescript
{
  isRemoteMode: boolean,
  sendMessage: (content, opts?) => Promise<boolean>,
  cancelRequest: () => void,
  disconnect: () => void
}
```

### Constants
| Constant | Value | Purpose |
|----------|-------|---------|
| `RESPONSE_TIMEOUT_MS` | 60000 | Normal stuck session timeout |
| `COMPACTION_TIMEOUT_MS` | 180000 | Extended timeout during compaction |

### Key Design Patterns
- **BoundedUUIDSet echo filter**: User messages echoed over WebSocket are filtered by UUID with a ring buffer (cap 50)
- **Tool lifecycle tracking**: `runningTaskIdsRef` mirrors local task tracking for the "N in background" counter
- **Compaction-aware timeout**: Uses 3× longer timeout during compaction
- **Memoized return value**: Prevents churn in REPL's `onSubmit` useCallback deps

---

## 7. `useTextInput.ts` (529 lines)

**File:** `F:\Claude\src\hooks\useTextInput.ts`

### Purpose
Core text input handling for the REPL prompt. Manages cursor position, text history, keybindings (Emacs-style), multiline input, kill ring, and yank-pop.

### Props (20 total)
| Prop | Type | Purpose |
|------|------|---------|
| `value` | `string` | Current input text |
| `onChange` | `(value: string) => void` | Text change callback |
| `onSubmit` | `(value: string) => void` | Submit callback |
| `onExit` | `() => void` | Exit callback |
| `onExitMessage` | `(show: boolean, key?: string) => void` | Exit warning display |
| `onHistoryUp/Down/Reset` | `() => void` | History navigation |
| `onClearInput` | `() => void` | Clear input callback |
| `focus` | `boolean` | Focus state |
| `mask` | `string` | Password/input mask |
| `multiline` | `boolean` | Multiline mode |
| `cursorChar` | `string` | Cursor character for rendering |
| `highlightPastedText` | `boolean` | Paste highlighting |
| `invert` | `(text: string) => string` | Text inversion function |
| `themeText` | `(text: string) => string` | Text theming function |
| `columns` | `number` | Terminal width |
| `onImagePaste` | `(base64, mediaType?, filename?, dimensions?, sourcePath?) => void` | Image paste handler |
| `disableCursorMovementForUpDownKeys` | `boolean` | Disable cursor on up/down |
| `disableEscapeDoublePress` | `boolean` | Disable Esc double-press |
| `maxVisibleLines` | `number` | Max visible lines for viewport |
| `externalOffset` | `number` | External cursor offset |
| `onOffsetChange` | `(offset: number) => void` | Cursor offset change callback |
| `inputFilter` | `(input: string, key: Key) => string` | Input transformation filter |
| `inlineGhostText` | `InlineGhostText` | Ghost text for rendering |
| `dim` | `(text: string) => string` | Dim function for ghost text |

### State (none directly — uses Cursor utility and props)

### Functions

#### Double-Press Handlers
- **`handleCtrlC`** — Three-stage: show exit message → (double press) exit → (if has text) clear input
- **`handleEscape`** — Show "Esc again to clear" notification → (double press) save to history and clear
- **`handleEmptyCtrlD`** — Only when input is empty: show exit message → (double press) exit

#### Emacs Key Bindings
- **`handleCtrl(map)`**: Ctrl+A (start of line), Ctrl+B (left), Ctrl+C (exit), Ctrl+D (delete forward), Ctrl+E (end of line), Ctrl+F (right), Ctrl+H (delete token/backspace), Ctrl+K (kill to end), Ctrl+N (down/history), Ctrl+P (up/history), Ctrl+U (kill to start), Ctrl+W (kill word before), Ctrl+Y (yank)
- **`handleMeta(map)`**: Meta+B (prev word), Meta+F (next word), Meta+D (delete word after), Meta+Y (yank pop)

#### Kill Ring Operations
- **`killToLineEnd()`** — Deletes to line end and pushes to kill ring with 'append'
- **`killToLineStart()`** — Deletes to line start, pushes with 'prepend'
- **`killWordBefore()`** — Deletes word before cursor, pushes with 'prepend'
- **`yank()`** — Inserts last kill, records yank position
- **`handleYankPop()`** — Replaces yanked text with next kill ring entry

#### Line Navigation
- **`upOrHistoryUp()`** — Try wrapped line up → logical line up → history navigation
- **`downOrHistoryDown()`** — Try wrapped line down → logical line down → history navigation

#### Key Mapping
- **`handleEnter(key)`** — Backslash+Enter = literal newline; Shift/Meta+Enter = newline; plain Enter = submit
- **`mapKey(key)`** — Main switch dispatcher:
  - Escape → double-press handler
  - Arrow keys with modifiers → word navigation
  - Backspace/Delete with modifiers → kill operations
  - Ctrl → Emacs handler
  - Home/End → line navigation
  - PageUp/PageDown → fullscreen (no-op) or line nav
  - Wheel → no-op (fullscreen only)
  - Default → Unicode character insertion with ANSI stripping

#### Kill/Yank State Reset
- **`isKillKey(key, input)`** — Detects Ctrl+K/U/W and Meta+Backspace/Delete
- **`isYankKey(key, input)`** — Detects Ctrl+Y and Alt+Y

#### Main Handler
- **`onInput(input, key)`** — The main input handler:
  1. Applies `inputFilter` if provided
  2. Filters DEL characters (`\x7f`) — handles SSH/tmux backspace artifacts
  3. Resets kill accumulation or yank state based on key type
  4. Dispatches via `mapKey(key)` to get transformed cursor
  5. Handles SSH-coalesced Enter detection (`"o\r"` → submit)
  6. Validates ghost text insert position against current offset

### Return Value
```typescript
{
  onInput: (input: string, key: Key) => void,
  renderedValue: string,        // Cursor-rendered text
  offset: number,
  setOffset: (offset: number) => void,
  cursorLine: number,           // Viewport-relative line
  cursorColumn: number,         // Column position
  viewportCharOffset: number,   // Viewport character offset
  viewportCharEnd: number       // Viewport character end
}
```

### Key Design Patterns
- **Cursor utility class**: All text mutations go through `Cursor` methods (immutable)
- **Kill ring**: Tracks kill operations with accumulation for consecutive kills
- **Yank state**: Tracks yank position for yank-pop cycling
- **SSH/tmux artifact handling**: Filters DEL characters; detects coalesced Enter
- **Ghost text validation**: Only renders ghost text when `insertPosition` matches current offset

---

## 8. `useVoiceIntegration.tsx` (677 lines)

**File:** `F:\Claude\src\hooks\useVoiceIntegration.tsx`

### Purpose
Voice input UI integration layer. Handles hold-to-talk key detection (space or configurable key), voice anchor management (preserving typed text around cursor), interim transcript display, and warmup feedback UI.

### Exports two hooks:
1. `useVoiceIntegration` — Core voice integration (main hook)
2. `useVoiceKeybindingHandler` — Keybinding integration that consumes voice events

### State (from voice context)
| Selector | Purpose |
|----------|---------|
| `voiceState` | Current voice state from context |
| `voiceInterimTranscript` | Live interim transcript |

### Refs (from `useVoiceIntegration`)
| Ref | Purpose |
|-----|---------|
| `voicePrefixRef` | Text before cursor when voice starts |
| `voiceSuffixRef` | Text after cursor when voice starts |
| `lastSetInputRef` | Last input value this hook wrote (submit race guard) |

### Refs (from `useVoiceKeybindingHandler`)
| Ref | Purpose |
|-----|---------|
| `rapidCountRef` | Count of rapid consecutive key events |
| `charsInInputRef` | How many warmup chars flowed into input |
| `recordingFloorRef` | Trailing chars preserved after activation strip |
| `isHoldActiveRef` | Whether current recording was key-held (not focus) |
| `resetTimerRef` | Timer to reset hold detection state |

### Functions (useVoiceIntegration)

- **`stripTrailing(maxStrip, opts?)`** — Strips trailing hold-key chars from input. With `anchor=true`: captures prefix/suffix refs around cursor for interim transcript placement. Inserts gap space if suffix doesn't start with whitespace. Returns remaining trailing count.
- **`resetAnchor()`** — Undoes the gap space and resets prefix/suffix refs. Called when voice activation fails.
- **`handleVoiceTranscript(text)`** — Called when voice produces final transcript. Constructs `prefix + leadingSpace + text + trailingSpace + suffix` input. Updates `voicePrefixRef` for focus mode continuation. Guards against submit race via `lastSetInputRef`.

### Effects (useVoiceIntegration)
1. **Focus-mode anchor** (`useEffect`, lines 234-248): When `voiceState` becomes `'recording'` and no anchor exists, captures prefix/suffix at current cursor. Clears on `'idle'`.
2. **Interim transcript display** (`useEffect`, lines 253-280): Live-updates input with interim transcript between prefix and suffix. Handles spacing intelligently. Guards against submit race.

### Functions (useVoiceKeybindingHandler)

- **`handleKeyDown(e)`** — The central key handler:
  1. Guards: voice enabled, isActive, no modal overlay, valid binding
  2. **If already recording** (hold-active): swallows keypress, forwards to voice, strips leaked chars
  3. **If non-idle** (focus-mode recording): swallows modifier combos, passes bare chars through
  4. **Activation check**: Modifier combos activate on first press. Bare chars need `HOLD_THRESHOLD` (5) rapid events.
  5. **On activation**: Stops propagation, strips warmup chars, anchors prefix/suffix, calls `voiceHandleKeyEvent()`. If voice fails to transition, resets anchor.
  6. **Warmup** (bare-char only): First `WARMUP_THRESHOLD` (2) chars flow through. Subsequent chars swallowed with defensive strip.
  7. **Reset timer**: If gap between key events exceeds `RAPID_KEY_GAP_MS` (120ms), resets hold state.

### Backward-Compat Bridge
- `useInput` subscription converts InputEvent to KeyboardEvent (lines 653-664)
- `VoiceKeybindingHandler` shim component for existing JSX callers

### Return Value (useVoiceIntegration)
```typescript
{
  stripTrailing: (maxStrip: number, opts?: StripOpts) => number,
  resetAnchor: () => void,
  handleKeyEvent: (fallbackMs?: number) => void,
  interimRange: InterimRange | null
}
```

### Return Value (useVoiceKeybindingHandler)
```typescript
{ handleKeyDown: (e: KeyboardEvent) => void }
```

### Constants
| Constant | Value | Purpose |
|----------|-------|---------|
| `RAPID_KEY_GAP_MS` | 120 | Max gap between key events to count as held |
| `MODIFIER_FIRST_PRESS_FALLBACK_MS` | 2000 | Fallback for modifier-combo first press |
| `HOLD_THRESHOLD` | 5 | Rapid events required to activate |
| `WARMUP_THRESHOLD` | 2 | Events before showing warmup feedback |

### Key Design Patterns
- **Anchor system**: Captures text before/after cursor so interim transcript inserts at exact position
- **Submit race guard**: `lastSetInputRef` comparison prevents re-filling cleared input
- **Warmup flow-through**: First 2 chars flow to input for normal typing; rapid chars beyond that are swallowed
- **Modifier vs bare char**: Different activation thresholds (first press vs 5 rapid events)
- **Defensive strip**: `stripTrailing` called even when listener order isn't guaranteed (text input may fire first)

---

## 9. `useManagePlugins.ts` (304 lines)

**File:** `F:\Claude\src\hooks\useManagePlugins.ts`

### Purpose
Plugin lifecycle management. Handles initial plugin load on mount, delisting enforcement, flagged plugin notifications, and surface-level refresh notifications.

### Props
| Prop | Type | Default | Purpose |
|------|------|---------|---------|
| `enabled` | `boolean` | `true` | Whether plugin loading is active |

### State Selectors
- `needsRefresh` — `useAppState(s => s.plugins.needsRefresh)`

### Functions

- **`initialPluginLoad()`** — Async callback. Executes the full plugin loading pipeline:
  1. `loadAllPlugins()` → `{ enabled, disabled, errors }`
  2. `detectAndUninstallDelistedPlugins()` — blocklist enforcement
  3. `getFlaggedPlugins()` — notification for pending dismissals
  4. **Individually try/caught**: `getPluginCommands()`, `loadPluginAgents()`, `loadPluginHooks()`
  5. `Promise.all` for MCP server configs per plugin
  6. `Promise.all` for LSP server configs per plugin
  7. `reinitializeLspServerManager()` — defensive LSP restart
  8. **AppState update**: Merges errors, preserving existing LSP errors and deduplicating
  9. **Metrics computation**: counts for enabled, disabled, inline, marketplace, skills, agents, hooks, MCP, LSP, errors
  10. **Analytics**: `tengu_plugins_loaded` event with all metrics
  Error path: sets empty plugin state, logs error, emits zero metrics.

### Effects
1. **Initial load** (`useEffect`, lines 269-285): On mount (if enabled), calls `initialPluginLoad()`. Emits telemetry on completion.
2. **Refresh notification** (`useEffect`, lines 293-303): When `needsRefresh` is true, shows notification directing user to `/reload-plugins`. Does NOT auto-refresh.

### Return Value
Void — operates via side effects (AppState mutations, notifications).

### Key Design Patterns
- **Single-load-then-notify**: Initial load happens on mount. Subsequent changes show a notification; all refresh goes through `/reload-plugins` → `refreshActivePlugins()` for consistent Layer-3 swap.
- **Error accumulation**: Each loading step has its own try/catch, pushing errors to a shared array visible in Doctor UI.
- **LSP error preservation**: When merging plugin errors into AppState, existing LSP-manager and plugin-origin errors are preserved and deduplicated.
- **Delisting enforcement**: Detects and auto-uninstalls plugins that were delisted, recorded as flagged for user review.

---

## 10. `useHistorySearch.ts` (303 lines)

**File:** `F:\Claude\src\hooks\useHistorySearch.ts`

### Purpose
Reverse-chronological prompt history search (Ctrl+R). Matches via `display.lastIndexOf(historyQuery)` over an async generator — no Fuse.js.

### Props (11 total)
| Prop | Type | Purpose |
|------|------|---------|
| `onAcceptHistory` | `(entry: HistoryEntry) => void` | Submit handler for accepted entry |
| `currentInput` | `string` | Current prompt input |
| `onInputChange` | `(input: string) => void` | Input change callback |
| `onCursorChange` | `(cursorOffset: number) => void` | Cursor change callback |
| `currentCursorOffset` | `number` | Current cursor position |
| `onModeChange` | `(mode: PromptInputMode) => void` | Mode change callback |
| `currentMode` | `PromptInputMode` | Current input mode |
| `isSearching` | `boolean` | Whether search mode is active |
| `setIsSearching` | `(isSearching: boolean) => void` | Search mode setter |
| `setPastedContents` | `(pastedContents: object) => void` | Pasted contents setter |
| `currentPastedContents` | `object` | Current pasted contents |

### State Variables (5)
| Variable | Type | Default | Purpose |
|----------|------|---------|---------|
| `historyQuery` | `useState<string>` | `''` | Current search query |
| `historyFailedMatch` | `useState<boolean>` | `false` | No more matches flag |
| `originalInput` | `useState<string>` | `''` | Input preserved at search start |
| `originalCursorOffset` | `useState<number>` | `0` | Cursor preserved at search start |
| `originalMode` | `useState<PromptInputMode>` | `'prompt'` | Mode preserved at search start |
| `originalPastedContents` | `useState<object>` | `{}` | Pasted contents preserved |
| `historyMatch` | `useState<HistoryEntry\|undefined>` | `undefined` | Current matching entry |

### Refs
| Ref | Purpose |
|-----|---------|
| `historyReader` | Async generator reading history file in reverse |
| `seenPrompts` | Set of already-seen display strings (prevents cycling) |
| `searchAbortController` | AbortController for current search |
| `searchHistoryRef` | Keeps searchHistory ref current for useEffect |

### Functions

- **`closeHistoryReader()`** — Calls `.return(undefined)` on the async generator to trigger finally block (closes file handle).
- **`reset()`** — Clears all state, closes reader, clears seen prompts.
- **`searchHistory(resume, signal?)`** — Async search function:
  1. If query is empty, restores original input and clears
  2. If not resume, creates new reader and clears seen set
  3. Iterates history entries; matches via `display.lastIndexOf(historyQuery)`
  4. Skips already-seen entries
  5. On match: sets input, mode, cursor (relative to clean value), pasted contents
  6. On exhaustion: sets `historyFailedMatch = true`
- **`handleStartSearch()`** — Initiates search: saves original state, creates reader
- **`handleNextMatch()`** — Resumes search for next match
- **`handleAccept()`** — Accepts current match and exits search
- **`handleCancel()`** — Restores original input and exits search
- **`handleExecute()`** — Accepts and submits current match

### Keybindings
- `history:search` (Ctrl+R, Global context): Starts search (gated off when `HISTORY_PICKER` feature is active)
- `historySearch:next/accept/cancel/execute` (HistorySearch context): Active when searching

### Effects
- **Query change** (`useEffect`, lines 286-294): Aborts previous search, creates new AbortController, starts fresh search with signal. Cleanup aborts controller.

### Return Value
```typescript
{
  historyQuery: string,
  setHistoryQuery: (query: string) => void,
  historyMatch: HistoryEntry | undefined,
  historyFailedMatch: boolean,
  handleKeyDown: (e: KeyboardEvent) => void
}
```

### Key Design Patterns
- **Async generator reader**: History file is read in reverse using an async generator. `.return()` is explicitly called to close the file handle.
- **Seen set dedup**: Entries with the same display text are skipped to prevent cycling.
- **AbortController per query**: Each query change aborts the previous search, ensuring only the latest query's results are shown.

---

## 11. `useVimInput.ts` (316 lines)

**File:** `F:\Claude\src\hooks\useVimInput.ts`

### Purpose
Vim-style modal text editing with INSERT and NORMAL mode support. Extends `useTextInput` with vim command state machine (counts, operators, motions, text objects).

### State Variables
| Variable | Type | Default | Purpose |
|----------|------|---------|---------|
| `mode` | `useState<VimMode>` | `'INSERT'` | Current vim mode |

### Refs
| Ref | Purpose |
|-----|---------|
| `vimStateRef` | Current `VimState` ({ mode, command, insertedText }) |
| `persistentRef` | Persistent state across mode switches (register, lastFind, lastChange) |

### Functions

- **`switchToInsertMode(offset?)`** — Sets vim state to INSERT, optionally moves cursor. Calls `onModeChange`.
- **`switchToNormalMode()`** — Records last insert change for dot-repeat. Moves cursor left by 1 (vim behavior). Sets state to NORMAL with idle command.
- **`createOperatorContext(cursor, isReplay)`** — Creates fresh `OperatorContext` for vim operators. Bridges between Cursor/AppState and vim operator internals.
- **`replayLastChange()`** — Dot-repeat implementation. Replays the last change from `persistentRef.lastChange`, dispatching to `executeX`, `executeReplace`, `executeToggleCase`, `executeIndent`, `executeJoin`, `executeOpenLine`, `executeOperatorMotion`, `executeOperatorFind`, `executeOperatorTextObj`.
- **`handleVimInput(rawInput, key)`** — Main input handler:
  1. Runs `inputFilter` (only applies in INSERT mode)
  2. Creates current cursor
  3. **Ctrl combos**: pass through to base text input (handles interrupts, etc.)
  4. **Escape in INSERT**: switch to NORMAL mode (NOT using keybindings system — deliberately hardcoded)
  5. **Escape in NORMAL**: cancel pending command
  6. **Enter**: pass through (allows submission from NORMAL mode)
  7. **INSERT mode**: Tracks inserted text for dot-repeat (handles backspace/delete by truncating last grapheme)
  8. **NORMAL mode**: Arrow keys in idle state pass through. Other keys route through vim `transition()` state machine with `TransitionContext`
  9. Arrow key to vim motion mapping: left→h, right→l, up→k, down→j
  10. Backspace/Delete in motion-expecting states mapped to h/x
- **`setModeExternal(newMode)`** — External mode setter (e.g., from UI). Resets vim state.

### Return Value
```typescript
{
  ...textInput,           // All useTextInput fields (onInput, renderedValue, offset, etc.)
  onInput: handleVimInput, // Overrides base onInput
  mode: VimMode,
  setMode: (mode: VimMode) => void
}
```

### Key Design Patterns
- **Composition over inheritance**: Extends `useTextInput` internally, spreads its return but overrides `onInput`
- **State machine**: NORMAL mode commands follow `transition()` state machine (idle → count → operator → operatorCount → motion/find/textObj)
- **Dot-repeat**: All changes recorded in `persistentRef.lastChange`. Replay dispatches to respective operator functions.
- **Grapheme-aware backspace**: Uses `lastGrapheme()` for Unicode-safe backspace in INSERT tracking
- **Deliberately non-keybinding escape**: Escape in INSERT mode always switches to NORMAL — not configurable

---

## 12. `usePasteHandler.ts` (285 lines)

**File:** `F:\Claude\src\hooks\usePasteHandler.ts`

### Purpose
Paste event handling for text, images, and large content detection. Handles bracketed paste mode, clipboard image detection (macOS), image file path resolution, and paste chunking.

### Props
| Prop | Type | Purpose |
|------|------|---------|
| `onPaste` | `(text: string) => void` | Paste text handler |
| `onInput` | `(input: string, key: Key) => void` | Normal input handler |
| `onImagePaste` | `(base64, mediaType?, filename?, dimensions?, sourcePath?) => void` | Image paste handler |

### State Variables
| Variable | Type | Default | Purpose |
|----------|------|---------|---------|
| `pasteState` | `useState<{chunks, timeoutId}>` | `{chunks: [], timeoutId: null}` | Accumulated paste chunks |
| `isPasting` | `useState<boolean>` | `false` | Whether currently pasting |

### Refs
| Ref | Purpose |
|-----|---------|
| `isMountedRef` | Mount flag for async clipboard operations |
| `pastePendingRef` | Synchronous paste-pending flag (avoids stale state in same batch) |

### Functions

- **`checkClipboardForImageImpl()`** — Async: calls `getImageFromClipboard()`, passes results to `onImagePaste`. Debounced at 50ms.
- **`resetPasteTimeout(currentTimeoutId)`** — Schedules paste completion after `PASTE_COMPLETION_TIMEOUT_MS` (100ms):
  1. Joins accumulated chunks
  2. Filters orphaned focus sequences (`[I$`, `[O$`)
  3. **Image path detection**: Splits pasted text on spaces before absolute paths, then newlines. Detects image file paths.
  4. Multiple images: reads all via `tryReadImageFromPath()`, passes valid images to `onImagePaste`, non-image lines to `onPaste`
  5. **Temporary screenshot**: On macOS, if paths are in TemporaryItems, tries clipboard instead
  6. **Empty paste on macOS**: Checks clipboard for images (Cmd+V pasting images)
  7. Regular paste: calls `onPaste(pastedText)`

- **`wrappedOnInput(input, key, event)`** — The wrapped input handler:
  1. Detects paste from `event.keypress.isPasted` (bracketed paste mode)
  2. Sets `isPasting` state for UI feedback
  3. **Empty paste on macOS**: checks clipboard for images
  4. **Paste detection conditions**: `onPaste` exists AND (input > `PASTE_THRESHOLD` OR pending OR has image paths OR bracketed paste)
  5. If pasting: accumulates chunks, resets timeout
  6. Otherwise: passes to normal `onInput`

### Return Value
```typescript
{
  wrappedOnInput: (input: string, key: Key, event: InputEvent) => void,
  pasteState: { chunks: string[], timeoutId },
  isPasting: boolean
}
```

### Constants
| Constant | Value | Purpose |
|----------|-------|---------|
| `CLIPBOARD_CHECK_DEBOUNCE_MS` | 50 | Debounce for clipboard image check |
| `PASTE_COMPLETION_TIMEOUT_MS` | 100 | Timeout for paste chunk accumulation |

### Key Design Patterns
- **Bracketed paste detection**: Uses `keypress.isPasted` from the keypress parser (no stdin race condition)
- **pastePendingRef for synchronous reads**: When paste + keystroke arrive in same batch, React state is stale; the ref provides the ground truth
- **Timeout-based chunk accumulation**: Large pastes are batched by stdin; 100ms timeout waits for all chunks
- **Image path fallback chain**: Pasted paths → file read → clipboard (for temp screenshots on macOS)

---

## 13. `useCancelRequest.ts` (276 lines)

**File:** `F:\Claude\src\hooks\useCancelRequest.ts`

### Purpose
Request cancellation via Escape key with overlay conflict resolution. Also handles Ctrl+C interrupt, background agent killing, and teammate view exit.

### Props (14 total)
| Prop | Type | Purpose |
|------|------|---------|
| `setToolUseConfirmQueue` | `function` | Permission queue setter |
| `onCancel` | `() => void` | Cancel callback |
| `onAgentsKilled` | `() => void` | Agents killed callback |
| `isMessageSelectorVisible` | `boolean` | Message selector state |
| `screen` | `Screen` | Current screen |
| `abortSignal` | `AbortSignal?` | Active abort signal |
| `popCommandFromQueue` | `() => void?` | Queue pop function |
| `vimMode` | `VimMode?` | Current vim mode |
| `isLocalJSXCommand` | `boolean?` | Local JSX command active |
| `isSearchingHistory` | `boolean?` | History search active |
| `isHelpOpen` | `boolean?` | Help screen open |
| `inputMode` | `PromptInputMode?` | Current input mode |
| `inputValue` | `string?` | Current input value |
| `streamMode` | `SpinnerMode?` | Current spinner mode |

### Refs
| Ref | Purpose |
|-----|---------|
| `lastKillAgentsPressRef` | Timestamp of last kill-agents press (for double-press detection) |

### Functions

- **`handleCancel()`** — Priority-ordered cancel:
  1. If task running (`abortSignal` not aborted): logs analytics, clears permission queue, calls `onCancel()`
  2. If commands in queue: pops command from queue
  3. Fallback: clears queue, calls `onCancel()`

- **`killAllAgentsAndNotify()`** — Kills all running background agents:
  1. Reads running `local_agent` tasks from store
  2. Calls `killAllRunningAgentTasks()`
  3. Marks each as notified
  4. Emits `taskTerminated` SDK events
  5. Enqueues aggregate notification message
  6. Returns true if anything was killed

- **`handleInterrupt()`** — Ctrl+C handler:
  1. If viewing teammate: kills agents, exits teammate view
  2. If task running or commands queued: calls `handleCancel()`

- **`handleKillAgents()`** — Two-press pattern:
  1. Checks for running agents; if none, shows notification
  2. First press: shows confirmation hint with shortcut display
  3. Second press within `KILL_AGENTS_CONFIRM_WINDOW_MS` (3s): kills all agents

### Activity Guards
- **`isEscapeActive`**: Context active AND (canCancel OR hasQueuedCommands) AND NOT special mode with empty input AND NOT viewing teammate
- **`isCtrlCActive`**: Context active AND (canCancel OR hasQueuedCommands OR viewingTeammate)
- Context guards: screen !== 'transcript', not searching history, not message selector, not local JSX, not help open, not overlay active, not in vim INSERT mode

### Keybindings
| Action | Key | Context | Active Condition |
|--------|-----|---------|------------------|
| `chat:cancel` | Escape | Chat | `isEscapeActive` |
| `app:interrupt` | Ctrl+C | Global | `isCtrlCActive` |
| `chat:killAgents` | Ctrl+X Ctrl+K | Chat | Always (handler gates internally) |

### Return Value
`null` — renders nothing, operates via keybinding side effects.

### Constants
| Constant | Value | Purpose |
|----------|-------|---------|
| `KILL_AGENTS_CONFIRM_WINDOW_MS` | 3000 | Confirmation window for kill agents |

### Key Design Patterns
- **Priority-based cancel**: Task running → queue pop → fallback
- **Overlay conflict resolution**: Declines to handle cancel when other overlays are active (via `useIsOverlayActive`)
- **Two-press safety pattern**: Kill agents requires confirmation within 3s window
- **Vim INSERT mode exclusion**: Escape in INSERT mode belongs to vim, not cancel

---

## 14. `useCanUseTool.tsx` (204 lines)

**File:** `F:\Claude\src\hooks\useCanUseTool.tsx`

### Purpose
Permission checking hook for determining if a tool can be used. Implements the full permission resolution pipeline: config-based allow/deny, coordinator permission, swarm worker permission, classifier check, and interactive permission.

This hook uses React Compiler (`useMemoCache` via `_c(3)`).

### Props
| Prop | Type | Purpose |
|------|------|---------|
| `setToolUseConfirmQueue` | `function` | Permission queue setter |
| `setToolPermissionContext` | `function` | Permission context setter |

### Return Value
A `CanUseToolFn` — async function `(tool, input, toolUseContext, assistantMessage, toolUseID, forceDecision?) => Promise<PermissionDecision>`.

### Permission Resolution Pipeline

The returned function creates a Promise that executes the following pipeline:

1. **Create PermissionContext** — via `createPermissionContext()` with `createPermissionQueueOps()`
2. **Early abort check** — `ctx.resolveIfAborted(resolve)`
3. **Config-based check** — `hasPermissionsToUseTool()` returns the initial permission decision
4. **Resolve behaviors**:
   - **`'allow'`**: Logs decision, handles classifier-based auto-mode approval, calls `ctx.buildAllow()`
   - **`'deny'`**: Logs decision, records auto-mode denial if applicable, returns result
   - **`'ask'`**: Enters the interactive resolution sub-pipeline:
     a. **Coordinator check** (`handleCoordinatorPermission`): If `awaitAutomatedChecksBeforeDialog` is set, checks if coordinator can auto-approve (with optional bash classifier pending check)
     b. **Swarm worker check** (`handleSwarmWorkerPermission`): If running as a swarm worker, forwards permission request to leader
     c. **Bash classifier speculative check**: If no automated checks before dialog, tries speculative classifier check with 2s timeout. On high-confidence match, auto-approves with classifier reason.
     d. **Interactive permission** (`handleInteractivePermission`): Falls through to bridge/channel permission callbacks for user interaction
5. **Error handling**: `AbortError` or `APIUserAbortError` → logs and aborts. Other errors → logs and aborts.
6. **Finally**: `clearClassifierChecking(toolUseID)`

### Key Design Patterns
- **Promise-based pipeline**: Permission resolution is a linear Promise chain with early-return points
- **React Compiler integration**: Uses `useMemoCache` (`_c(3)`) for the callback memoization
- **Multi-layer resolution**: Config → coordinator → swarm → classifier → interactive, each layer can resolve or pass through
- **Speculative classifier race**: Bash classifier check runs with 2s timeout; high-confidence match auto-approves, low-confidence falls through to interactive
- **Permission context abstraction**: `createPermissionContext()` encapsulates abort handling, logging, and decision building

---

## 15. `useSwarmPermissionPoller.ts` (330 lines)

**File:** `F:\Claude\src\hooks\useSwarmPermissionPoller.ts`

### Purpose
Polls for permission responses from the team leader when running as a swarm worker. Maintains module-level callback registries for permission and sandbox permission forwarding.

### Module-Level State
| Variable | Type | Purpose |
|----------|------|---------|
| `pendingCallbacks` | `Map<string, PermissionResponseCallback>` | Permission request callbacks |
| `pendingSandboxCallbacks` | `Map<string, SandboxPermissionResponseCallback>` | Sandbox permission callbacks |

### Types
- **`PermissionResponseCallback`**: `{ requestId, toolUseId, onAllow(updatedInput, permissionUpdates, feedback?), onReject(feedback?) }`
- **`SandboxPermissionResponseCallback`**: `{ requestId, host, resolve(allow: boolean) }`

### Exported Functions

#### Registry Management
- **`registerPermissionCallback(callback)`** — Adds to `pendingCallbacks` map
- **`unregisterPermissionCallback(requestId)`** — Removes from map
- **`hasPermissionCallback(requestId)`** — Checks existence
- **`clearAllPendingCallbacks()`** — Clears both registries (called on `/clear`)
- **`registerSandboxPermissionCallback(callback)`** — Adds to sandbox map
- **`hasSandboxPermissionCallback(requestId)`** — Checks sandbox existence

#### Response Processing
- **`processMailboxPermissionResponse(params)`** — Called by inbox poller. Validates `permissionUpdates` via Zod schema (`parsePermissionUpdates`). Invokes `onAllow` or `onReject`. Removes from registry.
- **`processSandboxPermissionResponse(params)`** — Called by inbox poller. Resolves the sandbox promise with allow/deny. Removes from registry.
- **`processResponse(response)`** — Internal: processes a file-based permission response (poll-based path).
- **`parsePermissionUpdates(raw)`** — Validates `permissionUpdates` array using Zod schema. Filters out malformed entries (from buggy/old teammate processes).

### Hook Implementation
- **`useSwarmPermissionPoller()`** — Void hook:
  1. Only polls when `isSwarmWorker()` returns true
  2. Uses `isProcessingRef` to prevent concurrent polling
  3. Skips if no callbacks registered
  4. For each pending request: calls `pollForResponse()`, processes if found, removes response file
  5. Polls every `POLL_INTERVAL_MS` (500ms) via `useInterval`
  6. Initial poll on mount

### Refs
| Ref | Purpose |
|-----|---------|
| `isProcessingRef` | Concurrent poll guard (boolean) |

### Constants
| Constant | Value | Purpose |
|----------|-------|---------|
| `POLL_INTERVAL_MS` | 500 | Poll interval |

### Key Design Patterns
- **Module-level registries**: `pendingCallbacks` and `pendingSandboxCallbacks` persist across React renders. Registered when a worker submits a permission request; resolved when leader responds.
- **Dual resolution paths**: File-based polling (`pollForResponse`) for local swarm; mailbox-based (`processMailboxPermissionResponse`) for inbox integration.
- **Zod validation**: Permission updates from external sources are validated; malformed entries filtered rather than propagated.
- **Concurrent poll guard**: `isProcessingRef` prevents overlapping poll cycles.

---

## Cross-Cutting Patterns

### Ref-Based State Patterns
Many hooks use refs instead of state for values that:
- Need synchronous reads in async callbacks (`sessionGenRef`, `lastSetInputRef`)
- Should not trigger re-renders (`cursorOffsetRef`, `suggestionsRef`)
- Track staleness for async operations (`latestSearchTokenRef`, `latestPathTokenRef`)

### Staleness Detection
Multiple hooks use generation counters or token comparison to discard stale async results:
- `useVoice.ts`: `sessionGenRef`, `attemptGenRef` — prevents zombie WebSockets
- `useTypeahead.tsx`: `latestSearchTokenRef`, `latestPathTokenRef`, `latestSlackTokenRef`
- `useHistorySearch.ts`: `AbortController` per query

### Module-Level State
Some hooks use module-level variables for cross-render or cross-hook state:
- `useSwarmPermissionPoller.ts`: `pendingCallbacks` Map, `pendingSandboxCallbacks` Map
- `useTypeahead.tsx`: `currentShellCompletionAbortController`
- `useVoice.ts`: `voiceModule` (lazy-loaded)

### Backward-Compat Bridges
Several hooks use `useInput` as a bridge from the old event system to `KeyboardEvent`:
- `useTypeahead.tsx`: lines 1368-1374
- `useVoiceIntegration.tsx`: lines 653-664
- `useHistorySearch.ts`: lines 274-279

### Keybinding Registration
Hooks that register keybindings:
- `useTypeahead.tsx`: Autocomplete context (accept/dismiss/previous/next)
- `useHistorySearch.ts`: HistorySearch context (next/accept/cancel/execute) + Global (search)
- `useCancelRequest.ts`: Chat context (cancel, killAgents) + Global (interrupt)

### Overlay Registration
`useTypeahead.tsx` registers `autocomplete` as an overlay to defer ESC handling from `useCancelRequest.ts`.

### Store Imperative Reads
Several hooks use `store.getState()` for synchronous reads without subscribing:
- `useInboxPoller.ts`: Reads `appState.teamContext`, `appState.toolPermissionContext`
- `useCancelRequest.ts`: Reads `tasks` for kill-all-agents
- `useTypeahead.tsx`: Reads teammate registry, MCP clients

### Debounce Patterns
- `useTypeahead.tsx`: File suggestions (50ms), Slack channels (150ms)
- `usePasteHandler.ts`: Clipboard image check (50ms)
- `useVoiceIntegration.tsx`: Built-in via rapid key gap detection (120ms)

### Race Condition Prevention
- **Submit race guard** (`useVoiceIntegration.tsx`): `lastSetInputRef` comparison
- **Batched state reads** (`usePasteHandler.ts`): `pastePendingRef` for synchronous reads
- **Effect cancellation** (`useVoice.ts`): `cancelled` flag in cleanup
- **Concurrent poll guard** (`useSwarmPermissionPoller.ts`): `isProcessingRef`
- **Previous teardown await** (`useReplBridge.tsx`): `teardownPromiseRef` before re-init
