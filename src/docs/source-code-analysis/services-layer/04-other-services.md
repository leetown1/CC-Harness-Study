# Services Layer Analysis — File 4: Other Services

> **Scope**: All remaining service directories — tools, analytics, plugins, LSP, SessionMemory, extractMemories, policyLimits, remoteManagedSettings, oauth, teamMemorySync, autoDream, tips, MagicDocs, PromptSuggestion, settingsSync, toolUseSummary, AgentSummary
> **Purpose**: Tool execution, analytics/telemetry, plugin management, LSP integration, session memory, enterprise policy enforcement, settings synchronization, and quality-of-life features.

---

## 1. Tools Services (`services/tools/` — 4 files)

### 1.1 `services/tools/toolExecution.ts` (1745 lines)

**Core tool execution engine.** Handles the complete lifecycle of a tool invocation from API response to user-facing result.

#### Architecture

```
executeToolUse()
├── 1. PRE-FLIGHT
│   ├── Find tool definition by name
│   ├── Validate tool is not deferred (ToolSearch deferred tools)
│   ├── Check permission (canUseTool)
│   │   ├── Permission denied → yield reject message
│   │   └── Permission granted → proceed
│   └── Build tool input (parse + validate against schema)
├── 2. PRE-HOOKS
│   ├── Execute pre-tool hooks (user scripts)
│   ├── Handle hook blocking (wait for user input)
│   └── Handle hook modifications (tool input override)
├── 3. EXECUTION
│   ├── Start OTel span + session tracing span
│   ├── Execute tool (await tool.call())
│   │   ├── Normal execution → progress + result
│   │   ├── Aborted → yield cancel message
│   │   ├── Errored → yield error message
│   │   └── Shell error (non-zero exit) → yield error
│   └── Track execution time + analytics
├── 4. POST-HOOKS
│   ├── Execute post-tool hooks
│   ├── Handle hook cancellations
│   ├── Handle hook modifications (output override, additional messages)
│   ├── Handle permission denied hooks
│   └── Handle stop hook (abort further tool execution)
├── 5. RESULT ASSEMBLY
│   ├── Build ToolResultBlockParam for API
│   ├── Handle large output truncation
│   ├── Handle binary output (persist to disk)
│   ├── Handle tool use summary generation
│   └── Build user-facing message (with diff, error formatting)
└── 6. ANALYTICS
    ├── Log tengu_tool_execution event
    ├── Log OTel tool_execution event
    ├── Track tool duration
    └── Diagnostic tracking (before/after IDE diagnostics)
```

#### Key Features

- **Async Generator Pattern**: `executeToolUse()` is an async generator that yields `Message` objects (progress, result, error, attachment)
- **Abort Handling**: Respects `AbortController` signals; yields CANCEL_MESSAGE on abort
- **Shell Error Integration**: Special handling for non-zero exit codes from Bash/PowerShell tools
- **Large Output Handling**: Truncates oversized tool results, persists binary content to disk
- **Git Operation Tracking**: Detects git operations (commit, push, pull) and emits tracking events
- **Permission Model**: Full permission system with deny/allow/ask modes, per-tool, per-directory granularity
- **Hook System**: Pre-hooks (modify input), post-hooks (modify output), permission-hooks (override permissions)
- **Stop Hooks**: Can abort remaining tool executions when a post-hook returns stop signal
- **Skill Integration**: Tracks skill executions (extract skill name, emit skill-specific attribution)
- **MCP Integration**: Special handling for MCP tools (server name, auth errors, elicitation)
- **Code Editing Attribution**: Tracks file edits per tool (which files were modified)

---

### 1.2 `services/tools/StreamingToolExecutor.ts` (530 lines)

**Concurrent tool execution manager.** Handles parallel tool execution from streaming API responses.

#### Architecture

```
StreamingToolExecutor
├── Queue Management
│   ├── addTool() → Add tool to queue, start if conditions allow
│   ├── TrackedTool state: queued | executing | completed | yielded
│   └── Results buffered in order (FIFO)
├── Concurrency Model
│   ├── Concurrent-safe tools → execute in parallel
│   │   └── Examples: Read, Grep, Glob, LS, ListMcpResources, Skill
│   ├── Non-concurrent tools → execute exclusively (one at a time)
│   │   └── Examples: Bash, Write, Edit, NotebookEdit, Agent, Task
│   └── Blocking: non-concurrent tool blocks all subsequent tools
├── Progress Streaming
│   ├── Progress messages yielded immediately (not buffered)
│   └── progressAvailable signal for async wake-up
├── Abort/Cancel
│   ├── Sibling abort: Bash error → cancel all in-progress tools
│   ├── discard(): streaming fallback → abandon all pending tools
│   └── Parent abort via AbortController hierarchy
└── Result Collection
    ├── getRemainingResults() → await all queued tools
    ├── Results emitted in submission order
    └── Context modifiers applied per-tool
```

#### Concurrency Rules

| Tool Category | Concurrent? | Examples |
|---|---|---|
| Read-only filesystem | Yes | Read, Grep, Glob, LS |
| File modification | No (exclusive) | Write, Edit, NotebookEdit |
| Shell execution | No (exclusive) | Bash, PowerShell |
| Agent/Subagent | No (exclusive) | Task, Agent |
| MCP tools | Configurable | Depends on tool type |
| Skills | Yes | Skill commands |

---

### 1.3 `services/tools/toolHooks.ts` (650 lines)

**Hook orchestration for tools.** Manages the pre/post hook lifecycle.

#### Hook Pipeline

```
Tool execution
├── PreToolUse hooks
│   ├── executePreToolHooks() → async generator
│   ├── Yields: additional messages, input modifications
│   ├── Blocks tool execution pending user input (blocking hooks)
│   └── getPreToolHookBlockingMessage() → wait for user
├── PostToolUse hooks
│   ├── executePostToolHooks() → async generator
│   ├── Output modification → updated tool output
│   ├── Additional messages (attachment, progress)
│   ├── Permission denied handling
│   └── Stop hook → abort remaining tools
├── PostToolUseFailure hooks
│   └── executePostToolUseFailureHooks() → on tool error
└── Rule-based permissions
    ├── checkRuleBasedPermissions() → per-file/directory rules
    └── getRuleBehaviorDescription() → explain permission decision
```

#### Hook Events (Analytics)

- `tengu_pre_tool_hooks_executed` — pre-hook completion
- `tengu_post_tool_hooks_executed` — post-hook completion
- `tengu_post_tool_hooks_cancelled` — hook cancelled
- `tengu_post_tool_hooks_failure` — hook execution failed
- `tengu_post_tool_hooks_permission_denied` — hook returned permission denied

---

### 1.4 `services/tools/toolOrchestration.ts` (188 lines)

**Read/write tool batching.** Optimizes tool execution by batching compatible operations:

- **Read Batching**: Multiple Read/Grep/Glob tools can execute in parallel
- **Write Batching**: Multiple file modifications can be grouped (when safe)
- **Conflict Detection**: Prevents read-after-write conflicts
- **Batch Progress**: Aggregated progress reporting for batched tools

---

## 2. Analytics Services (`services/analytics/` — 9 files)

### 2.1 `services/analytics/growthbook.ts` (1155 lines)

**GrowthBook feature flag client.** Central feature flag and A/B testing system.

#### Architecture

```
GrowthBook Client
├── Initialization
│   ├── initializeGrowthBook() → Create/configure GrowthBook instance
│   │   ├── API streaming connection (SSE)
│   │   ├── Fallback: CDN download with polling
│   │   └── Disk cache (features.json in config dir)
│   ├── Periodic refresh (60s default)
│   └── Re-init on auth changes (different user attributes)
├── User Attributes
│   ├── id, sessionId, deviceID
│   ├── platform, apiBaseUrlHost
│   ├── organizationUUID, accountUUID
│   ├── userType (ant/external), subscriptionType
│   ├── rateLimitTier, firstTokenTime
│   └── email, appVersion, github metadata
├── Feature Resolution
│   ├── getFeatureValue_CACHED_MAY_BE_STALE() → sync, no await
│   │   └── Returns cached value; used in hot paths
│   ├── getDynamicConfig_BLOCKS_ON_INIT() → async, waits for init
│   │   └── Used for security-critical gates (off-switch)
│   └── getFeatureValue() → standard async resolution
├── Remote Evaluation
│   ├── Support for server-side eval (remoteEval)
│   ├── Feature values cached from API response
│   └── Stale-while-revalidate pattern
├── Experiment Tracking
│   ├── Automatic exposure logging (dedup per session)
│   ├── Pending exposures queued before init
│   ├── Stored experiment data (experimentId, variationId)
│   └── 1P event logging integration
└── Event System
    ├── onFeatureRefresh() → notify listeners of new values
    └── signal-based change detection (createSignal)
```

#### Key Functions

| Function | Purpose |
|---|---|
| `initializeGrowthBook()` | Initialize with user attributes, remote eval + disk cache |
| `getFeatureValue_CACHED_MAY_BE_STALE()` | Sync cached read for hot paths |
| `getDynamicConfig_BLOCKS_ON_INIT()` | Async read, blocks until init complete |
| `getOnlineEvalValue()` | Remote evaluation value |
| `logGrowthBookExperimentTo1P()` | 1P event exposure logging |
| `refreshFeatures()` | Force refresh from server |
| `resetGrowthBook()` | Teardown and reinitialize |

#### Features Controlled via GrowthBook

GrowthBook gates hundreds of features including:
- Model betas (thinking, extended context, structured outputs)
- Cache strategies (1h TTL, global scope)
- Micro-compaction (cached MC, time-based MC)
- Auto-compact thresholds
- Rate limit configurations
- Tool search / deferred tools
- Voice mode (Nova 3 STT)
- Off-switch (Opus capacity management)
- Security classifiers (bash, yolo)
- UI experiments (various)
- Enterprise feature gates

---

### 2.2 `services/analytics/metadata.ts` (973 lines)

**Shared event metadata enrichment.** Single source of truth for analytics event metadata across all systems (Datadog, 1P, OTel).

#### Metadata Categories

| Category | Fields |
|---|---|
| **Environment** | OS type/version, shell, terminal, WSL version, Linux distro, VCS (git/svn/mercurial) |
| **Session** | sessionId, parentSessionId, agentId, isInteractive, isTeammate, teamName |
| **User** | userType, subscriptionType, organizationUUID, accountUUID, rateLimitTier |
| **Platform** | nodeVersion, bunVersion, platform, arch, clientType, electronVersion, kairosActive |
| **Repo** | gitRemoteHash (hashed, not plaintext), repo root detection |
| **Build** | appVersion, buildTime, commit SHA |
| **Model** | mainLoopModel, model betas, provider |
| **Auth** | isOAuth, isClaudeAISubscriber, authMethod |

#### Tool Name Sanitization

```typescript
sanitizeToolNameForAnalytics(toolName)
├── mcp__* → 'mcp_tool' (PII protection)
├── skill:*/skill_* → 'skill_tool'
└── Built-in tools → passed through as-is
```

`isToolDetailsLoggingEnabled()` — opt-in detailed logging for MCP server/tool names via `OTEL_LOG_TOOL_DETAILS=1`.

#### PII Protection

The `AnalyticsMetadata_I_VERIFIED_THIS_IS_NOT_CODE_OR_FILEPATHS` marker type (`never`) is used throughout to force explicit verification that logged string values contain no code snippets, file paths, or PII.

---

### 2.3 `services/analytics/datadog.ts`

**Datadog integration.** Sends analytics events to Datadog:
- Custom metrics (tool executions, API calls, token usage)
- Log-based metrics for Datadog dashboards
- DD-API-KEY authentication
- Batch sending with retry

### 2.4 `services/analytics/firstPartyEventLogger.ts`

**First-party event logger.** Internal Anthropic event pipeline:
- Batches events in memory
- Periodic flush (configurable interval)
- Internal API endpoint (`events.anthropic.com`)
- Zstd compression for large payloads
- GrowthBook config for batch size/flush interval

### 2.5 `services/analytics/firstPartyEventLoggingExporter.ts`

**OTel exporter for 1P events.** Bridges OTel spans/logs to the first-party event pipeline:
- Converts OTel format to 1P protobuf
- Maintains trace context across events
- Rate-limited per event type

### 2.6 `services/analytics/index.ts`

**Main analytics entry point.** `logEvent()` function and event type definitions:
- Sends to all configured sinks (Datadog, 1P, OTel)
- Event deduplication (per-event-type rate limiting)
- Essential-traffic-only kill switch
- Build-time event exclusion (excluded-strings.txt)

### 2.7 `services/analytics/sink.ts`

**Analytics sink abstraction.** Pluggable sink architecture:
- Multiple sinks can be active simultaneously
- Each sink has its own flush/error handling
- Health monitoring per sink

### 2.8 `services/analytics/sinkKillswitch.ts`

**Sink killswitch management.** Runtime enable/disable per sink:
- Incident response: disable specific analytics without restart
- GrowthBook-controlled kill switches
- `isEssentialTrafficOnly()` global override

### 2.9 `services/analytics/config.ts`

**Analytics configuration.** 
- Endpoint URLs per environment
- Batch sizes per sink
- Flush intervals
- Retry policies
- Rate limits per event type

---

## 3. Plugin Services (`services/plugins/` — 3 files)

### 3.1 `services/plugins/pluginOperations.ts` (~1088 lines)

**Plugin lifecycle operations** — lower-level ops used by CLI wrappers:

| Function | Purpose |
|---|---|
| `installPluginOp()` | Downloads, validates, extracts plugin |
| `uninstallPluginOp()` | Removes plugin and cleans up |
| `enablePluginOp()` / `disablePluginOp()` | Toggle enabled state |
| `disableAllPluginsOp()` | Disable all installed plugins |
| `updatePluginOp()` | Update one or all plugins |
| `getPluginInstallationFromV2()` | Read v2 installation record |

Exports scope constants: `VALID_INSTALLABLE_SCOPES`, `VALID_UPDATE_SCOPES`.

### 3.2 `services/plugins/PluginInstallationManager.ts` (~184 lines)

**Background plugin installation.** Exports `performBackgroundPluginInstallations()` — runs queued installs at startup with progress reporting.

### 3.3 `services/plugins/pluginCliCommands.ts` (~344 lines)

**CLI commands for plugin management.** `/plugin` command handlers:

- `installPlugin()` / `uninstallPlugin()` / `enablePlugin()` / `disablePlugin()`
- `disableAllPlugins()` / `updatePluginCli()`

---

## 4. LSP Services (`services/lsp/` — 7 files)

Uses **factory types**, not classes — `createLSPClient()`, `createLSPServerInstance()`, `createLSPServerManager()`.

### 4.1 `services/lsp/LSPClient.ts` (~447 lines)

**LSP client wrapper** over `vscode-jsonrpc` stdio transport.

| Export | Purpose |
|---|---|
| `createLSPClient(onCrash?)` | Returns `LSPClient` with `start`, `initialize`, `sendRequest`, `sendNotification`, `stop` |
| `LSPClient` type | Readonly capabilities + JSON-RPC methods |

### 4.2 `services/lsp/LSPServerInstance.ts` (~511 lines)

**Single language-server lifecycle** — spawns process, owns one `LSPClient`.

| Export | Purpose |
|---|---|
| `createLSPServerInstance(...)` | Factory for per-server instance |
| `LSPServerInstance` type | `start`, `ensureStarted`, `getClient`, crash/restart state |

### 4.3 `services/lsp/LSPServerManager.ts` (~420 lines)

**Multi-server manager** — language → server mapping, lazy start per file type.

| Export | Purpose |
|---|---|
| `createLSPServerManager()` | Returns manager with `getServerForUri`, `shutdown` |
| `LSPServerManager` type | Per-language server instances |

### 4.4 `services/lsp/manager.ts` (~289 lines)

**Global singleton orchestrator:**

| Function | Purpose |
|---|---|
| `initializeLspServerManager()` | Async startup during Claude Code boot |
| `reinitializeLspServerManager()` | Restart after config change |
| `shutdownLspServerManager()` | Graceful shutdown |
| `getLspServerManager()` | Returns manager or `undefined` if pending/failed |
| `getInitializationStatus()` | `'not-started' \| 'pending' \| 'success' \| 'failed'` |
| `isLspConnected()` | At least one healthy server connected |
| `waitForInitialization()` | Await init promise |

### 4.5 `services/lsp/LSPDiagnosticRegistry.ts` (~386 lines)

**Pending diagnostic queue** for edit-attribution — not a before/after delta store:

| Function | Purpose |
|---|---|
| `registerPendingLSPDiagnostic()` | Queue diagnostics for later delivery |
| `checkForLSPDiagnostics()` | Flush pending diagnostics to conversation |
| `clearAllLSPDiagnostics()` / `resetAllLSPDiagnosticState()` | Cleanup |

### 4.6 `services/lsp/config.ts` (~79 lines)

| Function | Purpose |
|---|---|
| `getAllLspServers()` | Returns configured LSP server definitions |

### 4.7 `services/lsp/passiveFeedback.ts` (~328 lines)

| Function | Purpose |
|---|---|
| `registerLSPNotificationHandlers()` | Wire publishDiagnostic notifications into registry |
| `formatDiagnosticsForAttachment()` | Format diagnostics for user-visible attachment |

---

## 5. Session Memory Services (`services/SessionMemory/` — 3 files)

Maintains a **markdown session-memory file** via background forked subagents — not a structured JSON `facts/preferences/tasks` object.

### 5.1 `services/SessionMemory/sessionMemory.ts` (~495 lines)

| Function | Purpose |
|---|---|
| `initSessionMemory()` | Registers post-sampling hook for periodic extraction |
| `shouldExtractMemory()` | Token + tool-call thresholds for background update |
| `manuallyExtractSessionMemory()` | Manual `/memory` extraction |
| `createMemoryFileCanUseTool()` | Restricts forked agent to memory file edits |
| `resetLastMemoryMessageUuid()` | Test reset |

Uses `runForkedAgent()` with `FileReadTool` + `FileEditTool`, gated by `tengu_session_memory` and `tengu_sm_config`.

### 5.2 `services/SessionMemory/prompts.ts` (~324 lines)

| Function | Purpose |
|---|---|
| `loadSessionMemoryTemplate()` / `loadSessionMemoryPrompt()` | Load template + system prompt |
| `buildSessionMemoryUpdatePrompt()` | Incremental update prompt |
| `isSessionMemoryEmpty()` | Template-only detection |
| `truncateSessionMemoryForCompact()` | Size cap for compact injection |

### 5.3 `services/SessionMemory/sessionMemoryUtils.ts` (~207 lines)

| Function | Purpose |
|---|---|
| `setLastSummarizedMessageId()` / `getLastSummarizedMessageId()` | Compact split tracking |
| `getSessionMemoryContent()` | Read memory file from disk |
| `waitForSessionMemoryExtraction()` | Await in-progress extraction |
| `getSessionMemoryConfig()` / `setSessionMemoryConfig()` | Threshold config (init/update tokens, tool-call intervals) |

---

## 6. Extract Memories (`services/extractMemories/` — 2 files)

Writes durable memories to the **auto-memory directory** (`~/.claude/projects/<path>/memory/`), not session-memory markdown.

### 6.1 `services/extractMemories/extractMemories.ts` (~615 lines)

| Function | Purpose |
|---|---|
| `initExtractMemories()` | Closure-scoped state; registers stop-hook handler |
| `executeExtractMemories()` | Forked-agent extraction at end of query loop |
| `drainPendingExtraction()` | Flush pending extraction on shutdown |
| `createAutoMemCanUseTool()` | Restricts writes to auto-mem paths |

Triggered from `handleStopHooks` when the model finishes with no pending tool calls. Uses `runForkedAgent()` for cache sharing.

### 6.2 `services/extractMemories/prompts.ts`

| Function | Purpose |
|---|---|
| `buildExtractAutoOnlyPrompt()` | Auto-memory-only extraction prompt |
| `buildExtractCombinedPrompt()` | Combined auto + team memory prompt |

---

## 7. Policy Limits (`services/policyLimits/` — 2 files)

### 7.1 `services/policyLimits/index.ts` (~663 lines)

Fetches org policy restrictions from API; **fails open** on errors.

| Function | Purpose |
|---|---|
| `initializePolicyLimitsLoadingPromise()` | Early init promise (30s timeout) |
| `isPolicyLimitsEligible()` | API-key users + Team/Enterprise OAuth |
| `loadPolicyLimits()` / `refreshPolicyLimits()` | Fetch with ETag disk cache |
| `waitForPolicyLimitsToLoad()` | Await initial load |
| `isPolicyAllowed(policy)` | Check named restriction |
| `startBackgroundPolling()` / `stopBackgroundPolling()` | 1-hour poll interval |

Cache file: `policy-limits.json` in config dir.

### 7.2 `services/policyLimits/types.ts`

Zod schemas: `PolicyLimitsResponseSchema`, `PolicyLimitsFetchResult`.

---

## 8. Remote Managed Settings (`services/remoteManagedSettings/` — 5 files)

### 8.1 `services/remoteManagedSettings/index.ts` (~638 lines)

Enterprise remote settings with checksum validation; **fails open**.

| Function | Purpose |
|---|---|
| `initializeRemoteManagedSettingsLoadingPromise()` | Early awaitable promise |
| `loadRemoteManagedSettings()` / `refreshRemoteManagedSettings()` | Fetch from `/api/claude_code/settings` |
| `computeChecksumFromSettings()` | Sorted-keys SHA checksum |
| `isEligibleForRemoteManagedSettings()` | Enterprise/Team OAuth + API key users |
| `waitForRemoteManagedSettingsToLoad()` | Block until first load |
| `startBackgroundPolling()` / `stopBackgroundPolling()` | 1-hour poll |

### 8.2 `services/remoteManagedSettings/syncCache.ts`

Eligibility checks and cache reset for remote managed settings sync.

### 8.3 `services/remoteManagedSettings/syncCacheState.ts`

Session cache; exports `getRemoteManagedSettingsSyncFromCache()`.

### 8.4 `services/remoteManagedSettings/securityCheck.tsx`

React UI gate: `checkManagedSettingsSecurity()` compares checksums before applying remote setting changes.

### 8.5 `services/remoteManagedSettings/types.ts`

Zod schema: `RemoteManagedSettingsResponseSchema`.

---

## 9. OAuth Services (`services/oauth/` — 5 files)

### 9.1 `services/oauth/index.ts` (~198 lines)

**`OAuthService` class** — PKCE authorization-code flow orchestrator:
- `startOAuthFlow()` — spawns `AuthCodeListener`, opens browser, exchanges code
- Supports automatic localhost callback and manual code paste
- Formats tokens with subscription/rate-limit tier from profile

### 9.2 `services/oauth/client.ts` (~566 lines)

| Function | Purpose |
|---|---|
| `buildAuthUrl()` | Construct authorization URL (manual + automatic variants) |
| `exchangeCodeForTokens()` / `refreshOAuthToken()` | Token endpoint calls |
| `fetchProfileInfo()` | User profile + subscription tier |
| `isOAuthTokenExpired()` | Expiry check with buffer |
| `populateOAuthAccountInfoIfNeeded()` | Persist account metadata |
| `getOrganizationUUID()` | Org UUID from stored profile |

### 9.3 `services/oauth/auth-code-listener.ts` (~211 lines)

**`AuthCodeListener` class** — localhost HTTP server for OAuth redirect, state validation, success/failure HTML pages.

### 9.4 `services/oauth/crypto.ts`

`generateCodeVerifier()`, `generateCodeChallenge()`, `generateState()` — PKCE + CSRF.

### 9.5 `services/oauth/getOauthProfile.ts`

`getOauthProfileFromApiKey()`, `getOauthProfileFromOauthToken()` — profile fetch helpers.

---

## 10. Team Memory Sync (`services/teamMemorySync/` — 5 files)

Per-repo team memory sync via `/api/claude_code/team_memory`. **Server wins on pull**; push is delta-by-hash; local deletes do not propagate.

### 10.1 `services/teamMemorySync/index.ts` (~1256 lines)

| Function | Purpose |
|---|---|
| `createSyncState()` | Per-session mutable sync state (ETag, checksums, max_entries) |
| `pullTeamMemory()` / `pushTeamMemory()` | Download / delta upload |
| `syncTeamMemory()` | Full sync orchestrator |
| `isTeamMemorySyncAvailable()` | Feature + auth eligibility |
| `batchDeltaByBytes()` | Split large PUT bodies (200KB cap) |

### 10.2 `services/teamMemorySync/secretScanner.ts` (~324 lines)

| Function | Purpose |
|---|---|
| `scanForSecrets()` | Regex scan before upload |
| `redactSecrets()` | Redact matched content |
| `getSecretLabel()` | Human label for rule ID |

### 10.3 `services/teamMemorySync/watcher.ts` (~387 lines)

| Function | Purpose |
|---|---|
| `startTeamMemoryWatcher()` / `stopTeamMemoryWatcher()` | File watcher lifecycle |
| `notifyTeamMemoryWrite()` | Debounced push trigger |

### 10.4-10.5 Supporting Files

- `types.ts` — Zod schemas for team memory API payloads
- `teamMemSecretGuard.ts` — `checkTeamMemSecrets()` pre-upload guard

---

## 11. Auto Dream (`services/autoDream/` — 4 files)

Background memory consolidation ("dreaming") — fires `/dream` prompt as forked subagent when time + session gates pass.

### 11.1 `services/autoDream/autoDream.ts` (~324 lines)

| Function | Purpose |
|---|---|
| `initAutoDream()` | Closure-scoped state; registers hook |
| `executeAutoDream()` | Run consolidation fork when gates pass |

Gate order: hours since `lastConsolidatedAt` → session count → file lock. Config from `tengu_onyx_plover` GB flag.

### 11.2-11.4 Supporting Files

- `consolidationPrompt.ts` — `buildConsolidationPrompt()`
- `consolidationLock.ts` — file lock + `readLastConsolidatedAt()`, `tryAcquireConsolidationLock()`
- `config.ts` — `isAutoDreamEnabled()` (separate from scheduling config)

---

## 12. Tips Service (`services/tips/` — 3 files)

### 12.1 `services/tips/tipRegistry.ts` (~686 lines)

| Function | Purpose |
|---|---|
| `getRelevantTips(context?)` | Returns tips matching current session context (~50 registered tips) |

Tips are predicate-driven (IDE installed, model, settings, referral eligibility, etc.) — not a simple register/get API.

### 12.2 `services/tips/tipScheduler.ts` (~58 lines)

| Function | Purpose |
|---|---|
| `selectTipWithLongestTimeSinceShown()` | Pick tip for spinner display |
| `getTipToShowOnSpinner()` | Async tip selection |
| `recordShownTip()` | Mark tip shown this session |

### 12.3 `services/tips/tipHistory.ts` (~17 lines)

| Function | Purpose |
|---|---|
| `recordTipShown()` / `getSessionsSinceLastShown()` | Persist tip cooldown across sessions |

---

## 13. Magic Docs (`services/MagicDocs/` — 2 files)

Auto-updates markdown files marked `# MAGIC DOC: [title]` when read during conversation.

### 13.1 `services/MagicDocs/magicDocs.ts` (~254 lines)

| Function | Purpose |
|---|---|
| `initMagicDocs()` | Register post-sampling hook + file-read listener |
| `detectMagicDocHeader()` | Parse `# MAGIC DOC:` header + optional italic instructions |
| `registerMagicDoc()` | Track file path on Read |
| `clearTrackedMagicDocs()` | Reset tracked set |

Uses built-in agent via `runAgent()` (not raw fork) with `FileReadTool` + `FileEditTool`.

### 13.2 `services/MagicDocs/prompts.ts`

`buildMagicDocsUpdatePrompt()` — update prompt for forked agent.

---

## 14. Prompt Suggestion (`services/PromptSuggestion/` — 2 files)

### 14.1 `services/PromptSuggestion/speculation.ts` (~991 lines)

Parallel speculative API call that pre-computes a likely next response:

| Function | Purpose |
|---|---|
| `isSpeculationEnabled()` | GB + settings gate |
| `startSpeculation()` / `acceptSpeculation()` / `abortSpeculation()` | Lifecycle |
| `prepareMessagesForInjection()` | Message prep for cache-shared fork |
| `handleSpeculationAccept()` | Accept flow on Tab |

### 14.2 `services/PromptSuggestion/promptSuggestion.ts` (~523 lines)

| Function | Purpose |
|---|---|
| `shouldEnablePromptSuggestion()` | Env override → `tengu_chomp_inflection` → non-interactive/teammate checks |
| `tryGenerateSuggestion()` / `generateSuggestion()` | Haiku fork for ghost-text suggestion |
| `executePromptSuggestion()` | Inject accepted suggestion |
| `shouldFilterSuggestion()` / `logSuggestionOutcome()` | Quality + analytics |

---

## 15. Settings Sync (`services/settingsSync/` — 2 files)

Syncs user settings + memory files across environments (OAuth, first-party API).

### 15.1 `services/settingsSync/index.ts` (~581 lines)

| Function | Purpose |
|---|---|
| `uploadUserSettingsInBackground()` | Interactive CLI push (incremental, changed keys only) |
| `downloadUserSettings()` / `redownloadUserSettings()` | CCR pull before plugin install |
| `_resetDownloadPromiseForTesting()` | Test helper |

Gated by `UPLOAD_USER_SETTINGS` bundle feature + `tengu_enable_settings_sync_push`.

### 15.2 `services/settingsSync/types.ts`

Zod schemas: `UserSyncDataSchema`, `SYNC_KEYS` allowlist of syncable setting keys.

---

## 16. Tool Use Summary (`services/toolUseSummary/` — 1 file)

### 16.1 `services/toolUseSummary/toolUseSummaryGenerator.ts` (~112 lines)

| Function | Purpose |
|---|---|
| `generateToolUseSummary()` | Haiku one-line label for completed tool batch (SDK/mobile progress) |

Uses `queryHaiku()` with `querySource: 'tool_use_summary_generation'`. Returns `null` on failure (non-critical).

---

## 17. Agent Summary (`services/AgentSummary/` — 1 file)

### 17.1 `services/AgentSummary/agentSummary.ts` (~180 lines)

| Function | Purpose |
|---|---|
| `startAgentSummarization()` | Returns `{ stop }` — periodic (~30s) forked progress summaries for coordinator sub-agents |

Uses `runForkedAgent()` with cache-shared params; updates `AgentProgress` via `updateAgentSummary()`. Not a post-completion report generator.

---

## Cross-Cutting Architecture Patterns

### Token Budget Awareness

Many services are token-budget-aware:
- `tokenEstimation.ts` → rough count (char/4) and API-based counting
- `compact/compact.ts` → reduces context when budget nears limits
- `compact/autoCompact.ts` → proactive compaction trigger
- `compact/microCompact.ts` → per-request token optimization
- `extractMemories/extractMemories.ts` → uses Haiku for cost efficiency

### GrowthBook Feature Gating

Nearly every experimental feature is gated through GrowthBook:
- Model betas (thinking, extended context, structured outputs, effort, task budgets)
- Cache strategies (1h TTL, global scope, cache editing)
- Compaction (auto, micro, cached, session memory)
- Voice mode (Nova 3 STT)
- Tool search / deferred tools
- MCP features (skills, elicitation)
- UI experiments (tips, suggestions, grove)
- Classifiers (bash, yolo, auto-mode)

### Cache-Aware Architecture

The system is deeply cache-aware:
- Prompt caching with deterministic cache_control markers
- Beta header "sticky-on" latches to avoid cache key changes
- Cache break detection with root-cause analysis
- Cache edit support for incremental cache modifications
- Compaction-aware cache baseline resetting

### PII Protection

The analytics system has strict PII protection:
- `AnalyticsMetadata_I_VERIFIED_THIS_IS_NOT_CODE_OR_FILEPATHS` marker type
- Tool name sanitization (MCP tools → 'mcp_tool')
- Server URL sanitization
- File path hashing (SHA-256 or djb2)
- Build-time string exclusion (excluded-strings.txt)
- `isToolDetailsLoggingEnabled()` opt-in for detailed logging
