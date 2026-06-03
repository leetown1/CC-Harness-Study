# Bridge System Analysis (31 files, 12,613 lines)

**Directory**: `F:\Claude\src\bridge\`  
**Purpose**: Implements the "Remote Control" (Claude Code Remote) bridge system — allowing the CLI to register as an execution environment, receive work/session dispatches from claude.ai, and relay bidirectional messages (inbound prompts from web/mobile, outbound tool results). Supports two transport architectures: **env-based** (Environments API + polling) and **env-less** (direct /bridge JWT exchange + SSE/CCR transport).

---

## Architecture Overview

```
┌──────────────────────────────────────────────────────────────────┐
│                         Entry Points                             │
│                                                                  │
│  initReplBridge.ts        bridgeMain.ts       remoteBridgeCore.ts│
│  (REPL auto-bridge)       (Standalone bridge) (Env-less bridge)  │
│        │                       │                     │           │
│        ▼                       ▼                     ▼           │
│  replBridge.ts            runBridgeLoop      remoteBridgeCore.ts │
│  (initBridgeCore)         (poll loop)        (initEnvLessBridgeCore)│
│        │                       │                     │           │
│        ▼                       ▼                     ▼           │
│  ┌─────────────────────────────────────────────────────────────┐ │
│  │              Transport Abstraction (replBridgeTransport.ts) │ │
│  │  v1: HybridTransport (WS reads + POST writes)               │ │
│  │  v2: SSETransport + CCRClient (SSE reads + /worker/* writes)│ │
│  └─────────────────────────────────────────────────────────────┘ │
│        │                       │                                 │
│        ▼                       ▼                                 │
│  ┌────────────────────────────────────────────────────────────┐  │
│  │             API Layer (bridgeApi.ts)                       │  │
│  │  register/poll/ack/heartbeat/stop/deregister              │  │
│  │  OAuth-authenticated, 401 retry, trusted device support   │  │
│  └────────────────────────────────────────────────────────────┘  │
│        │                                                        │
│        ▼                                                        │
│  ┌────────────────────────────────────────────────────────────┐  │
│  │               Infrastructure Utilities                     │  │
│  │  workSecret.ts (SDK URL builder, worker register)          │  │
│  │  sessionIdCompat.ts (cse_/session_ prefix translation)    │  │
│  │  jwtUtils.ts (token expiry decode, refresh scheduling)    │  │
│  │  trustedDevice.ts (elevated-auth device enrollment)        │  │
│  │  bridgePointer.ts (crash-recovery pointer persistence)     │  │
│  └────────────────────────────────────────────────────────────┘  │
└──────────────────────────────────────────────────────────────────┘
```

---

## Core Components

### 1. `bridgeMain.ts` (2,805 lines) — Main Bridge Orchestrator

The standalone bridge entry point (`claude remote-control`). Contains `runBridgeLoop()` which:

**State Machine & Session Tracking**:
- Maintains six Maps for tracking active sessions: `activeSessions` (SessionHandle), `sessionStartTimes`, `sessionWorkIds`, `sessionCompatIds` (cse_→session_), `sessionIngressTokens` (JWT for heartbeat), `sessionTimers` (timeout watchdog)
- `completedWorkIds` Set prevents re-processing stale server re-deliveries
- `sessionWorktrees` Map tracks git worktree isolation per session
- `v2Sessions` Set distinguishes CCR v2 sessions (JWT auth) from v1 (OAuth auth) for token refresh routing
- `titledSessions` Set prevents first-user-message from overwriting server-assigned titles

**Poll Loop Core** (`while (!loopSignal.aborted)`):
1. Fetches `getPollIntervalConfig()` per iteration (GrowthBook changes picked up within one sleep cycle)
2. Calls `api.pollForWork(environmentId, environmentSecret, signal, reclaim_older_than_ms)`
3. On no work: respects capacity throttling with varying sleep intervals (not_at_capacity / partial / at_capacity), including non-exclusive heartbeat mode
4. Work dispatch types handled:
   - `'healthcheck'`: acknowledged, logged
   - `'session'`: decoded work secret → CCR v2 path (`buildCCRv2SdkUrl` + `registerWorker`) or v1 path (`buildSdkUrl` for Session-Ingress WS) → optional worktree creation → `spawner.spawn()` → session lifecycle registration
   - Unknown types: acknowledged, gracefully skipped (forward compatibility)

**Heartbeat System** (at-capacity idle):
- `heartbeatActiveWorkItems()` — sends per-work-item heartbeats using session ingress tokens (not environment secret — JWT, no DB hit)
- Returns `'ok'` | `'auth_failed'` | `'fatal'` | `'failed'`
- On JWT expiry (401/403): calls `api.reconnectSession()` to trigger server-side re-dispatch (CC-1263: without this, ACK'd work stays out of Redis PEL and poll returns empty)
- On 404/410: marks as fatal (environment expired/deleted)

**Capacity Management**:
- `capacityWake` (from `capacityWake.ts`) — dual-signal AbortController merge that wakes at-capacity sleep when a session ends or transport is lost
- Three thresholds via `getPollIntervalConfig()`: not-at-capacity, partial-capacity, at-capacity
- Non-exclusive heartbeat mode: runs heartbeats AND periodically breaks out to poll (deadline-based)

**Session Lifecycle** (via `onSessionDone`):
- Comprehensive cleanup: removes from all Maps, clears timers (timeout + token refresh), wakes capacity
- `stopWorkWithRetry(force=false)` — notifies server work item is complete
- Worktree cleanup (`removeAgentWorktree`)
- Multi-session: archives session (`api.archiveSession(compatId)`) and returns to idle
- Single-session: aborts poll loop → teardown

**Token Refresh** (`createTokenRefreshScheduler`):
- Proactive JWT refresh scheduled 5min before expiry
- v1: delivers fresh OAuth token to child process via stdin
- v2: calls `api.reconnectSession()` to trigger server re-dispatch (JWT-only auth, epoch bump)

**Error Handling & Backoff**:
- `BridgeFatalError` (401/403): immediate teardown (except suppressible 403s)
- Connection errors: exponential backoff (2s→120s cap, 10min give-up), system sleep detection (resets budget when gap exceeds 2× connCapMs)
- `stopWorkWithRetry` — 1s/2s/4s backoff for cleanup calls
- `shutdownGraceMs` — SIGTERM→SIGKILL window (default 30s) with pending cleanup await

**Spawn Modes** (`BridgeConfig.spawnMode`):
- `'single-session'`: one session, bridge exits when complete
- `'worktree'`: each session gets isolated git worktree via `createAgentWorktree()`
- `'same-dir'`: all sessions share working directory
- GrowthBook-gated: `tengu_ccr_bridge_multi_session` → multi-session spawn (--spawn / --capacity)

---

### 2. `replBridge.ts` (2,255 lines) — REPL Bridge Integration

The REPL-mode bridge core (`initBridgeCore()`). Called by `initReplBridge.ts` after entitlement checks. Bootstrap-free — all context comes from `BridgeCoreParams`.

**Environment Registration → Session Creation → Poll Loop → Ingress Transport**:

1. Registers bridge environment via `api.registerBridgeEnvironment(config)`:
   - Includes `reuseEnvironmentId` for idempotent re-registration (perpetual mode / crash recovery)
   - `workerType` discriminates assistant-mode workers for web UI filtering

2. Crash-recovery pointer (`bridgePointer.ts`):
   - Written after session creation, refreshed on work dispatch
   - Perpetual mode (`perpetual=true`): reads prior pointer, attempts reconnect-in-place via `tryReconnectInPlace()`
   - Non-perpetual: cleared on teardown

3. Session creation via `createBridgeSession()` (injected):
   - REPL wrapper passes `createBridgeSession` from `createSession.ts` (OAuth, git context, org UUID)
   - Daemon/SDK callers pass leaner alternatives

4. Poll loop for work dispatch:
   - Single-session semantics: `isAtCapacity = () => transport !== null`
   - `onWorkReceived`: when new work arrives → close old transport (preserving SSE seq-num) → create new v1/v2 transport → wire callbacks → initial history flush → connect
   - Rejects foreign session IDs (cross-environment assignment)

5. Transport (v1/v2):
   - **v1**: `HybridTransport` — WS reads from Session-Ingress + POST writes (OAuth auth)
   - **v2**: `SSETransport` (reads) + `CCRClient` (writes to `/worker/*`) — JWT auth required (OAuth lacks `session_id` claim)
   - Server picks per-session via `secret.use_code_sessions`; `CLAUDE_BRIDGE_USE_CCR_V2` env var overrides

**Reconnection Strategies** (via `reconnectEnvironmentWithSession`):
- Triggered by: poll 404 (env lost), transport permanent close (non-1000), /bridge-kick
- **Strategy 1 (reconnect-in-place)**: idempotent re-register with `reuseEnvironmentId` → if same env returned → `api.reconnectSession()` → keeps same `currentSessionId`, URL, UUIDs
- **Strategy 2 (fresh session)**: if env expired → archive old session → create new session → reset per-session state (seq-num, UUID dedup, title derivation)
- Caps at `MAX_ENVIRONMENT_RECREATIONS = 3` consecutive failures
- Re-entrancy guard: concurrent callers share single `reconnectPromise`

**Message Handling**:
- `writeMessages(messages)`: filters by `isEligibleBridgeMessage` (user/assistant/system local_command, non-virtual) → dedup against `initialMessageUUIDs` + `recentPostedUUIDs` → enqueue via `FlushGate` if flush in-progress → else write to transport
- `writeSdkMessages(messages)`: for daemon callers (pre-formatted SDKMessages)
- `sendControlRequest/Response/CancelRequest`: forwarded to transport with session_id, `reportState()` calls for worker_status sync
- `sendResult()`: sends minimal `SDKResultSuccess` for session archival before transport close
- `onUserMessage` title derivation: called until callback returns `true` (count-1 placeholder + Haiku generate, count-3 full conversation regenerate)

**Teardown**:
- Registered with `registerCleanup()` (graceful shutdown integration)
- Sequence: `reconnectSession` attempts for perpetual → `api.stopWork(force=false)` → `api.deregisterEnvironment` → `archiveSession(currentSessionId)` → clear bridge pointer → transport close
- Ant-only: `/bridge-kick` fault injection via `registerBridgeDebugHandle()`

---

### 3. `remoteBridgeCore.ts` (1,008 lines) — Env-less Bridge Core

The v2 env-less bridge path (`initEnvLessBridgeCore()`). Activated when `tengu_bridge_repl_v2` GrowthBook gate is on AND not perpetual mode. **Skips the entire Environments API layer** — no register/poll/ack/heartbeat/deregister.

**Architecture** (env-less, no poll loop):
```
1. POST /v1/code/sessions (OAuth, no env_id) → session.id (cse_*)
2. POST /v1/code/sessions/{id}/bridge (OAuth) → {worker_jwt, expires_in, api_base_url, worker_epoch}
   Each /bridge call bumps epoch — it IS the register. No separate /worker/register.
3. createV2ReplTransport(worker_jwt, worker_epoch) → SSE + CCRClient
4. createTokenRefreshScheduler → proactive /bridge re-call (new JWT + new epoch)
5. 401 on SSE → rebuild transport with fresh /bridge credentials (same seq-num)
```

**Key Differences from v1**:
- No environment lifecycle — session created directly via `/v1/code/sessions`
- No poll loop — SSE pushes events continuously
- Transport rebuild on JWT expiry: fetches fresh `/bridge` credentials → creates new `SSETransport` + `CCRClient` preserving seq-num high-water mark
- `authRecoveryInFlight` flag prevents double `/bridge` fetch (laptop wake race)
- `FlushGate` gates writes during rebuild to prevent epoch-stale writes
- `connectDeadline` timer for silent-connect telemetry (~1% sessions get `started` but never `connected`)

**Transport Rebuild** (`rebuildTransport`):
- Started by proactive refresh scheduler OR 401 on SSE
- Captures old transport's seq-num → close → new transport at same `sessionUrl` with fresh JWT + epoch → wire callbacks → connect → drain queued writes
- `flushGate.start()` queues new writes during rebuild (old transport's epoch is stale after `/bridge`)
- On tornDown during async window: closes new transport, doesn't re-arm timers

**401 Recovery** (`recoverFromAuthFailure`):
- Unconditional OAuth refresh via `onAuth401(staleToken)` before `/bridge` call
- Resets `initialFlushDone = false` so next `onConnect` re-flushes history (old writeBatch may have silently no-op'd on closed uploader)

**Teardown**:
- Archive via compat layer (`/v1/sessions/{id}/archive`, not `/v1/code/sessions`) — retags `cse_*` to `session_*`
- 401 retry on archive (laptop wake past refresh window)
- 1.5s archive timeout (under graceful shutdown's 2s budget)
- Telemetry: `archive_ok`, `archive_http_status`, `archive_timeout`, `archive_no_token`

---

### 4. `bridgeApi.ts` (539 lines) — High-Level Bridge API

The HTTP client for the bridge system. Key design:

**`createBridgeApiClient(deps)`** returns `BridgeApiClient` with:
- `registerBridgeEnvironment(config)` — POST /v1/environments/bridge
- `pollForWork(envId, secret, signal, reclaimMs)` — GET /v1/environments/{id}/work/poll
- `acknowledgeWork(envId, workId, token)` — POST .../work/{id}/ack (JWT auth)
- `stopWork(envId, workId, force)` — POST .../work/{id}/stop (OAuth auth, auto-retry on 401)
- `heartbeatWork(envId, workId, token)` — POST .../work/{id}/heartbeat (JWT auth)
- `deregisterEnvironment(envId)` — DELETE /v1/environments/bridge/{id} (OAuth auth)
- `archiveSession(sessionId)` — POST /v1/sessions/{id}/archive (409=already archived, not error)
- `reconnectSession(envId, sessionId)` — POST .../bridge/reconnect (force-stops stale workers, re-queues session)
- `sendPermissionResponseEvent(sessionId, event, token)` — POST /v1/sessions/{id}/events

**Auth Flow**:
- Register/stop/deregister/reconnect/archive: OAuth-authenticated with 401 retry (`withOAuthRetry`)
- Poll/heartbeat/ack: authenticated with environment secret / session ingress JWT
- `X-Trusted-Device-Token` header injected when GrowthBook gate `tengu_sessions_elevated_auth_enforcement` is on
- Beta header: `environments-2025-11-01`

**Error Handling**:
- `handleErrorStatus(status, data, context)` — switches on HTTP status:
  - 401: `BridgeFatalError` — auth failure, suggests login
  - 403: `BridgeFatalError` — expired (session/env) or access denied
  - 404: `BridgeFatalError` — not found, may not be available
  - 410: `BridgeFatalError` — gone/session expired
  - 429: `Error` — rate limited
  - 200/204: passthrough
- `BridgeFatalError` class — carries `.status` and `.errorType` for discriminating recovery paths
- `isExpiredErrorType()` — checks for `expired` or `lifetime` in error type string
- `isSuppressible403()` — suppresses cosmetic 403s (external_poll_sessions scope, environments:manage permission)
- `validateBridgeId(id, label)` — `SAFE_ID_PATTERN = /^[a-zA-Z0-9_-]+$/`, prevents path traversal

**Empty Poll Throttling**: `consecutiveEmptyPolls` counter, logs every 1st and every 100th empty poll (avoids log spam while preserving visibility)

---

### 5. `bridgeMessaging.ts` (461 lines) — Inbound/Outbound Messaging

Shared transport-layer helpers used by both `replBridge.ts` (env-based) and `remoteBridgeCore.ts` (env-less).

**Type Guards**:
- `isSDKMessage(value)` — validates `{type: string}` discriminant
- `isSDKControlResponse(value)` — `{type: 'control_response', response: ...}`
- `isSDKControlRequest(value)` — `{type: 'control_request', request_id, request}`

**Message Filtering**:
- `isEligibleBridgeMessage(m)` — true for user, assistant, and system/local_command messages (non-virtual)
- `extractTitleText(m)` — extracts title-worthy text from a Message: user type, non-meta, non-tool-result, non-compact, human-origin, strips display tags

**Ingress Routing** (`handleIngressMessage`):
1. Parses data → `normalizeControlMessageKeys()` (camelCase compat)
2. Route: `control_response` → `onPermissionResponse` (skips SDKMessage type guard)
3. Route: `control_request` → `onControlRequest`
4. Route: `SDKMessage` → echo dedup (`recentPostedUUIDs`) → inbound dedup (`recentInboundUUIDs`) → `onInboundMessage?.(user-type only)`

**Server Control Requests** (`handleServerControlRequest`):
- Handles server-initiated `control_request` messages dispatched via SSE
- `initialize`: responds with minimal capabilities (empty commands/models/account, pid)
- `set_model`: delegates to `onSetModel` callback
- `set_max_thinking_tokens`: delegates to `onSetMaxThinkingTokens`
- `set_permission_mode`: delegates to `onSetPermissionMode` callback (returns {ok, error} verdict)
- `interrupt`: delegates to `onInterrupt` callback
- Outbound-only mode: all mutable requests reply with error (except initialize — server kills WS if it fails)
- Unknown subtypes: reply with error (prevents server hang)

**Result Message** (`makeResultMessage`):
- Builds minimal `SDKResultSuccess` for session archival — server needs this event before WS close

**`BoundedUUIDSet`** — FIFO-bounded set backed by a circular buffer:
- O(1) add/has, O(capacity) memory, ring buffer eviction (oldest first)
- Used for echo dedup (recentPostedUUIDs) and re-delivery dedup (recentInboundUUIDs)

---

### 6. `replBridgeTransport.ts` (370 lines) — Transport Layer

Abstraction over the two transport implementations:

**`ReplBridgeTransport` Interface** (15 methods/properties):
- `write(msg)` / `writeBatch(msgs)` — outbound message sending
- `close()` — resource cleanup
- `isConnectedStatus()` / `getStateLabel()` — health checks
- `setOnData/Close/Connect(cb)` — event callbacks
- `getLastSequenceNum()` — SSE high-water mark for transport swaps
- `droppedBatchCount` — batch drop detection
- `reportState(state)` — PUT /worker state (idle/running/requires_action)
- `reportMetadata(metadata)` — PUT /worker external_metadata
- `reportDelivery(eventId, status)` — POST delivery tracking
- `flush()` — drain write queue before close

**`createV1ReplTransport(hybrid)`** — wraps `HybridTransport` (WS reads + POST writes), getLastSequenceNum returns 0 (no SSE seq-num in v1)

**`createV2ReplTransport(opts)`** — async factory:
1. Sets up auth headers: per-instance closure (`getAuthToken`) or env-var (process-wide, single-session)
2. Registers worker OR accepts pre-bumped epoch (from /bridge response)
3. Constructs `SSETransport` (reads) + `CCRClient` (writes, heartbeat, worker-state)
4. Wires SSE close → notify CCR (close heartbeat timer) → delegate to replBridge
5. SSETransport.connect() is fire-and-forget (awaits read loop, never resolves)
6. CCRClient.initialize(epoch) is awaited → onConnect callback → mark write-ready
7. Epoch mismatch handler: closes SSE+CCR → calls onClose(4090) → replBridge poll loop picks up
8. Init failure handler: closes SSE+CCR → calls onClose(4091)
9. Auto-ACKs events as 'processed' immediately alongside 'received' (prevents phantom prompts on restart)

**Sequence Number Carryover**:
- v2: `getLastSequenceNum()` reads from `sse.getLastSequenceNum()` — carried across transport swaps
- Without carryover: each new SSETransport starts at 0 → server replays entire session event history
- Initial seed from `initialSSESequenceNum` (daemon persistState) or 0 (fresh session)

---

### 7. `initReplBridge.ts` (569 lines) — REPL Bridge Init

REPL-specific wrapper that owns bootstrap-state reads and delegates to `initBridgeCore`.

**Gate Checks (ordered)**:
1. `isBridgeEnabledBlocking()` — GrowthBook + auth + version + policy
2. OAuth token check — must be signed in with claude.ai
3. Cross-process backoff — if 3+ consecutive processes see same dead token (matched by expiresAt), skip silently
4. Proactive OAuth refresh — `checkAndRefreshOAuthTokenIfNeeded()` to avoid expected 401s
5. Skip if token expired AND unrefreshable (keychain dead, count-3 backoff)
6. Organization policy — `allow_remote_control` policy must be allowed
7. v1/v2 version floors — independent checks for each path

**v1/v2 Branch**:
- `isEnvLessBridgeEnabled()` AND `!perpetual` → `initEnvLessBridgeCore()` (env-less, no poll loop)
- Otherwise → env-based path via `initBridgeCore()`

**Title Derivation** (`onUserMessage` callback):
- Count-1: `deriveTitle()` placeholder (first sentence, 50 chars max, display tags stripped) → fire-and-forget `generateSessionTitle()` (Haiku LLM, sentence-case)
- Count-3: regenerate over full conversation via `extractConversationText(getMessagesAfterCompactBoundary(msgs))`
- Skips if title is explicit (initialName, /rename, sessionStorage)
- Resets on env-lost (session ID changes)

**Git Context Gathering**: `getBranch()`, `getRemoteUrl()`, `getOriginalCwd()`, `hostname()`

**Historical Message Cap**: `tengu_bridge_initial_history_cap` GrowthBook flag (default 200)

---

### 8. `bridgeConfig.ts` (48 lines) — Config Types

Three-layer auth/URL resolution:
- `getBridgeTokenOverride()` — ant-only dev override (`CLAUDE_BRIDGE_OAUTH_TOKEN`)
- `getBridgeBaseUrlOverride()` — ant-only dev override (`CLAUDE_BRIDGE_BASE_URL`)
- `getBridgeAccessToken()` — override → OAuth keychain token
- `getBridgeBaseUrl()` — override → `getOauthConfig().BASE_API_URL`

---

### 9. `bridgeDebug.ts` (135 lines) — Debug Utilities

Ant-only fault injection for manual testing of recovery paths:
- `registerBridgeDebugHandle(h)` — registers a debug handle with methods: `fireClose(code)`, `forceReconnect()`, `injectFault(fault)`, `wakePollLoop()`, `describe()`
- `wrapApiForFaultInjection(api)` — wraps `BridgeApiClient` to consume fault queue: matches on method name, decrements count, throws `BridgeFatalError` (fatal) or `Error` (transient)
- `injectBridgeFault(fault)` — `/bridge-kick` slash command entry point
- `clearBridgeDebugHandle()` — teardown cleanup

---

### 10. `bridgeEnabled.ts` (202 lines) — Enablement Checks

Multi-layered entitlement gates:
- `isBridgeEnabled()` — runtime check (non-blocking, cached): GrowthBook gate `tengu_ccr_bridge` + claude.ai subscriber
- `isBridgeEnabledBlocking()` — blocking check (awaits GrowthBook init on cache miss): same gate + same subscriber check
- `getBridgeDisabledReason()` — diagnostic: checks subscriber, profile scope, org UUID, GrowthBook gate, build feature; returns null if enabled, error string otherwise
- `isEnvLessBridgeEnabled()` — `tengu_bridge_repl_v2` gate (cached)
- `isCseShimEnabled()` — `tengu_bridge_repl_v2_cse_shim_enabled` gate, defaults to true
- `checkBridgeMinVersion()` — reads `tengu_bridge_min_version` config, compares with `MACRO.VERSION` via semver
- `getCcrAutoConnectDefault()` — `tengu_cobalt_harbor` gate (ant-only: `CCR_AUTO_CONNECT` build flag)
- `isCcrMirrorEnabled()` — env var `CLAUDE_CODE_CCR_MIRROR` or `tengu_ccr_mirror` gate

All auth module accesses wrapped in try/catch (handles pre-config access in main.tsx:5698).

---

### 11. Supporting Infrastructure

**`bridgePointer.ts`** (210 lines) — Crash-recovery pointer:
- Persists `{sessionId, environmentId, source}` as JSON alongside transcript files
- Staleness: file mtime > 4h TTL → cleared (matches BRIDGE_LAST_POLL_TTL)
- Worktree-aware read: fans out to git worktree siblings, picks freshest pointer
- Periodic refresh during session (same content, bumps mtime)
- Clear on clean shutdown, survives crash/kill -9

**`bridgeUI.ts`** (530 lines) — Terminal UI components via `createBridgeLogger`:
- State machine: idle → attached → titled → reconnecting → failed
- Renders: QR code (via `qrcode` library), status line with spinner frames, session count, per-session bullet list, tool activity trail
- OSC 8 terminal hyperlinks for session URLs
- Visual line counting for proper cursor positioning
- Connecting spinner (idle→attached transition)
- Multi-session support: bullet list with titles, URLs, current activity
- Keyboard hints: space for QR toggle, w for spawn mode toggle

**`bridgeStatusUtil.ts`** (163 lines) — Status formatting utilities:
- `StatusState` type (5 states)
- `formatDuration`, `truncatePrompt` re-exports from utils/format
- `buildBridgeConnectUrl/sessionUrl` — URL construction with proper base/prefix
- `computeShimmerSegments` — grapheme-aware text splitting for shimmer animation
- `getBridgeStatus()` — derives label + color from connection state
- `wrapWithOsc8Link()` — OSC 8 terminal hyperlink sequences

**`brush gate (poll config)`**:
- **`pollConfig.ts`** (110 lines) — GrowthBook-backed poll interval config with Zod schema validation (refines enforce floor/cap values, at-capacity liveness requirement)
- **`pollConfigDefaults.ts`** (82 lines) — Default intervals: 2s (not at capacity), 10min (at capacity), 60s heartbeat, 5s reclaim

**`capacityWake.ts`** (56 lines) — Shared wake-on-capacity-change primitive:
- Merges outer loop signal + wake controller into single AbortSignal
- `wake()` aborts current controller, creates fresh one for next sleep

**`codeSessionApi.ts`** (168 lines) — CCR v2 code-session HTTP wrappers:
- `createCodeSession(baseUrl, accessToken, title, timeout, tags)` — POST /v1/code/sessions
- `fetchRemoteCredentials(sessionId, baseUrl, accessToken, timeout, trustedDeviceToken)` — POST /v1/code/sessions/{id}/bridge → {worker_jwt, api_base_url, expires_in, worker_epoch}
- `RemoteCredentials` type
- SDK-exportable (no analytics, transport, auth dependencies)

**`createSession.ts`** (384 lines) — Session creation/fetch/archive:
- `createBridgeSession()` — POST /v1/sessions with git source/outcome context, org UUID, optional permission mode, model, session_context
- `getBridgeSession()` — GET /v1/sessions/{id} (for --session-id resume, returns environment_id + title)
- `archiveBridgeSession()` — POST /v1/sessions/{id}/archive (best-effort, throws on 5xx)
- `updateBridgeSessionTitle()` — PATCH /v1/sessions/{id} (best-effort title sync)
- All use dynamic imports (lazy-load auth/model/oauth modules)

**`debugUtils.ts`** (141 lines) — Debug/logging utilities:
- `redactSecrets(s)` — regex-based redaction of session_ingress_token, environment_secret, access_token fields
- `debugTruncate/body` — message truncation for debug logs (2000 char limit)
- `describeAxiosError(err)` — descriptive error message from axios responses
- `extractErrorDetail(data)` — human-readable message from API error body
- `logBridgeSkip(reason, debugMsg?, v2?)` — centralized skip logging + tengu_bridge_repl_skipped event

**`envLessBridgeConfig.ts`** (165 lines) — Env-less bridge config:
- 14 fields with Zod validation: retry params, timeouts, heartbeat, token refresh buffer, UUID dedup, connect timeout, version floor
- Fetched from `tengu_bridge_repl_v2_config` GrowthBook flag
- `checkEnvLessBridgeMinVersion()` — v2 version floor (independent of v1)

**`flushGate.ts`** (71 lines) — Message batching state machine:
- `start()` — activate queuing
- `end()` — return queued items (clears pending)
- `enqueue(...items)` — add to pending if active, return false if not
- `drop()` — discard pending (permanent close)
- `deactivate()` — clear active without dropping (transport replacement)

**`inboundAttachments.ts`** (175 lines) — Attachment processing:
- `extractInboundAttachments(msg)` — parse `file_attachments` array from inbound message
- `resolveInboundAttachments(attachments)` — fetch via OAuth GET /api/oauth/files/{uuid}/content → write to ~/.claude/uploads/{sessionId}/ → return @path refs
- `prependPathRefs(content, prefix)` — prepends to last text block (processUserInputBase reads from end)
- `resolveAndPrepend(msg, content)` — convenience: extract + resolve + prepend
- Zod schema for attachment validation

**`inboundMessages.ts`** (80 lines) — Message routing:
- `extractInboundMessageFields(msg)` — returns {content, uuid} or undefined for skip
- `normalizeImageBlocks(blocks)` — fix camelCase `mediaType` → snake_case `media_type` for iOS/web clients

**`jwtUtils.ts`** (256 lines) — JWT utilities:
- `decodeJwtPayload(token)` — base64url decode payload, strip `sk-ant-si-` prefix
- `decodeJwtExpiry(token)` — extract `exp` claim
- `createTokenRefreshScheduler({getAccessToken, onRefresh, label, refreshBufferMs})`:
  - `schedule(sessionId, token)` — decode JWT expiry, set timer
  - `scheduleFromExpiresIn(sessionId, expiresInSeconds)` — use explicit TTL (v2 /bridge response)
  - Generation counter per session — stale async doRefresh skips (prevents orphan timers)
  - Fallback follow-up refresh at 30min intervals (no expiry from token)
  - Max 3 consecutive failures, then gives up

**`sessionIdCompat.ts`** (57 lines) — ID compatibility:
- `toCompatSessionId(id)` — `cse_*` → `session_*` (for compat API calls that validate TagSession)
- `toInfraSessionId(id)` — `session_*` → `cse_*` (for infrastructure-layer calls below compat)
- `setCseShimGate(gate)` — GrowthBook-driven kill switch
- Separated from `workSecret.ts` to keep SDK bundle clean

**`sessionRunner.ts`** (550 lines) — Session spawner:
- `createSessionSpawner(deps)` → `SessionSpawner`
- Spawn child process: `execPath --print --sdk-url ... --session-id ... --input-format stream-json --output-format stream-json --replay-user-messages`
- Env vars: strips OAuth token, sets `CLAUDE_CODE_SESSION_ACCESS_TOKEN`, `CLAUDE_CODE_ENVIRONMENT_KIND=bridge`, optional CCR v2 vars
- NDJSON stdout parsing: extracts tool activities (tool_use → `tool_start` events), detects user messages for title derivation, detects permission requests
- Ring buffer: last 10 activities, last 10 stderr lines
- `updateAccessToken(token)` — sends token refresh via stdin (`update_environment_variables` message)
- Transcript logging: NDJSON write stream alongside debug file
- SIGTERM → SIGKILL grace period (platform-aware: Windows uses default signal)

**`trustedDevice.ts`** (210 lines) — Trusted device enrollment:
- GrowthBook gate: `tengu_sessions_elevated_auth_enforcement`
- `getTrustedDeviceToken()` — returns stored token if gate on (memoized keychain read)
- `enrollTrustedDevice()` — POST /api/auth/trusted_devices during /login (server gates on account_session.created_at < 10min)
- `clearTrustedDeviceToken/Cache()` — for logout/account switch
- Env var override: `CLAUDE_TRUSTED_DEVICE_TOKEN`

**`workSecret.ts`** (122 lines) — Work secret management:
- `decodeWorkSecret(secret)` — base64url decode → `WorkSecret` (Zod validated)
- `buildSdkUrl(ingressUrl, sessionId)` — v1 WS URL: `ws(s)://host/v1/code/sessions/{id}/connect`
- `buildCCRv2SdkUrl(apiBaseUrl, sessionId)` — v2 HTTP URL: `http(s)://host/v1/code/sessions/{id}`
- `registerWorker(sdkUrl, token)` — POST /v1/code/sessions/{id}/worker/register → epoch
- `sameSessionId(a, b)` — compare by underlying UUID (not tagged-ID prefix)

**`bridgePermissionCallbacks.ts`** (43 lines) — Web permission prompt wiring:
- `BridgePermissionCallbacks` — `{sendRequest, sendResponse, cancelRequest, onResponse}` for MCP-style `control_request`/`control_response` over the bridge transport
- `sendRequest(requestId, toolName, input, toolUseId, description, permissionSuggestions?, blockedPath?)` — emits permission prompt to claude.ai web UI
- `onResponse(requestId, handler)` — subscribe to user allow/deny; returns unsubscribe
- `cancelRequest(requestId)` — dismiss pending web prompt (e.g. on tool cancel)
- `BridgePermissionResponse` — `{behavior: 'allow'|'deny', updatedInput?, updatedPermissions?, message?}`
- `isBridgePermissionResponse(value)` — type guard on parsed `control_response` payload (checks `behavior` discriminant)

**`replBridgeHandle.ts`** (36 lines) — Global REPL bridge handle pointer:
- Module-level singleton set from `useReplBridge.tsx` on init, cleared on teardown
- `setReplBridgeHandle(h)` — stores handle; calls `updateSessionBridgeId(getSelfBridgeCompatId())` so local peers dedup this process from bridge session lists
- `getReplBridgeHandle()` — returns active `ReplBridgeHandle | null` for tools/slash commands outside React tree (e.g. BriefTool, upload)
- `getSelfBridgeCompatId()` — `session_*` compat ID from handle's `bridgeSessionId`, or undefined if disconnected
- Same one-bridge-per-process pattern as `bridgeDebug.ts` — handle closure owns sessionId + getAccessToken to avoid token divergence

**`types.ts`** (262 lines) — Type definitions:
- `WorkData`, `WorkResponse`, `WorkSecret` — environments API protocol types
- `BridgeConfig` — bridge configuration: dir, machineName, branch, gitRepoUrl, maxSessions, spawnMode, bridgeId, workerType, environmentId, reuseEnvironmentId, apiBaseUrl, sessionIngressUrl, debugFile, sessionTimeoutMs
- `SessionHandle`, `SessionSpawnOpts`, `SessionSpawner` — session lifecycle types
- `SessionActivity`, `SessionDoneStatus` — activity ring buffer types
- `BridgeLogger` — 27-method logging interface
- `BridgeApiClient` — 10-method API client interface
- `SpawnMode` — `'single-session' | 'worktree' | 'same-dir'`
- `BridgeWorkerType` — `'claude_code' | 'claude_code_assistant'`
- Constants: `DEFAULT_SESSION_TIMEOUT_MS` (24h), `BRIDGE_LOGIN_INSTRUCTION`, `BRIDGE_LOGIN_ERROR`, `REMOTE_CONTROL_DISCONNECTED_MSG`

---

## Data Flow

### Env-Based Path (v1)
```
claude.ai sends message
  → AcceptSession handles web-sent message (worker connects → sends message → action)
  → Backend dispatches work item to environment
  → bridgeMain.ts/replBridge.ts pollForWork picks it up
  → decodeWorkSecret extracts JWT + SDK URL
  → registerWorker (optional CCR v2) or buildSdkUrl (v1)
  → sessionRunner.ts spawns child claude process (--sdk-url, --session-id)
  → Child opens HybridTransport (v1) or SSETransport+CCRClient (v2)
  → Ingress: server forwards claude.ai messages via WS/SSE
  → bridgeMessaging.ts handleIngressMessage routes to onInboundMessage
  → Egress: writeMessages/writeBatch sends assistant/tool outputs back
```

### Env-less Path (v2)
```
/claude enables Remote Control
  → initReplBridge → isEnvLessBridgeEnabled() → initEnvLessBridgeCore
  → POST /v1/code/sessions → session.id (cse_*)
  → POST /v1/code/sessions/{id}/bridge → worker_jwt + epoch
  → createV2ReplTransport → SSETransport + CCRClient
  → Connect SSE → receive events continuously (no poll loop)
  → claude.ai sends message → server delivers via SSE
  → handleIngressMessage routes to onInboundMessage
  → Assistant responds → writeMessages sends via CCRClient → /worker/events
  → JWT expires → 401 on SSE → recoverFromAuthFailure → fresh /bridge → rebuild transport
  → On clean exit → archive session via compat layer
```

### Standalone Bridge (bridgeMain.ts)
```
claude remote-control [--spawn worktree] [--capacity 4]
  → registerBridgeEnvironment
  → createBridgeSession (empty, so user has somewhere to type)
  → runBridgeLoop (infinite poll loop)
  → Accepts multiple concurrent sessions (capped by maxSessions)
  → Per-session: spawn child, track lifecycle, heartbeat, timeout watchdog
  → Shutdown: SIGTERM→SIGKILL, stopWork, archive, deregister, worktree removal
```

---

## Key Design Decisions

1. **Dual transport abstraction** (v1 HybridTransport vs v2 SSETransport+CCRClient) confined to `replBridgeTransport.ts` — `ReplBridgeTransport` interface is the single integration surface for `replBridge.ts` and `remoteBridgeCore.ts`

2. **Env-less path skips entire Environments API** — reduces two RTTs (register + poll) to zero, replaces long-poll with SSE push for near-instant dispatch

3. **Crash-recovery pointers** (`bridgePointer.ts`) — survives SIGKILL, worktree-aware, 4h TTL matches server's environment expiry

4. **Generation counters everywhere** — `jwtUtils.ts` (token refresh), `replBridge.ts` (v2 transport creation) — prevent stale async operations from corrupting state

5. **Two-stage title derivation** — count-1 quick placeholder (first sentence, 50 chars) → count-3 full Haiku regeneration over conversation context

6. **Re-entrancy guards** — `reconnectPromise` in `replBridge.ts`, `authRecoveryInFlight` in `remoteBridgeCore.ts` — prevent duplicate concurrent recovery attempts

7. **Token refresh strategy asymmetry** — v1: OAuth token delivered to child via stdin (reuses OAuth refresh flow); v2: server re-dispatch via `reconnectSession()` (JWT can't be refreshed client-side)

8. **Bounded dedup sets** — `BoundedUUIDSet` at 2000 capacity prevents unbounded memory growth from echo/replay cycles

9. **Per-session vs process-wide auth** — `getAuthToken` closure (v2) vs `updateSessionIngressAuthToken()` env var (v1 legacy) — v2 closure prevents multi-session stomping

10. **Policy-driven lifecycle** — `allow_remote_control` policy rejects before any network calls; cross-process backoff prevents 401 storms from dead tokens
