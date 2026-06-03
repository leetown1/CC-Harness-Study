# Core Engine Source Code Analysis

## Table of Contents

1. [QueryEngine.ts — The Query Engine Class](#queryenginets--the-query-engine-class)
2. [query.ts — The Core Query Loop](#queryts--the-core-query-loop)
3. [query/config.ts — Query Configuration](#queryconfigts--query-configuration)
4. [query/deps.ts — Dependency Injection](#querydepsts--dependency-injection)
5. [query/stopHooks.ts — Stop Hook Execution](#querystophooksts--stop-hook-execution)
6. [query/tokenBudget.ts — Token Budget Tracker](#querytokenbudgetts--token-budget-tracker)
7. [context.ts — System & User Context](#contextts--system--user-context)
8. [cost-tracker.ts — Session Cost Tracking](#cost-trackerts--session-cost-tracking)
9. [history.ts — Command History Persistence](#historyts--command-history-persistence)
10. [tasks.ts — Task Implementation Registry](#tasksts--task-implementation-registry)
11. [Task.ts — Task Types & Interfaces](#taskts--task-types--interfaces)
12. [Tool.ts — Tool Interface & Context](#toolts--tool-interface--context)
13. [commands.ts — Command Registry](#commandsts--command-registry)
14. [tools.ts — Tool Registry](#toolsts--tool-registry)
15. [tasks/ — Task Implementations](#tasks--task-implementations)

---

## QueryEngine.ts — The Query Engine Class

**File location:** `src/QueryEngine.ts` (1295 lines)

### Overview

`QueryEngine` is the SDK/headless-facing orchestrator that owns the query lifecycle and session state for a conversation. It extracts the core logic previously embedded in `ask()` into a standalone class used by both the headless SDK path and (design anticipated for) the REPL.

The architecture follows a **one-QueryEngine-per-conversation** model. Each `submitMessage()` call starts a new turn within the same conversation. Mutable state (messages, file cache, usage, etc.) persists across turns.

### Class: `QueryEngine`

#### Private Fields

| Field | Type | Purpose |
|-------|------|---------|
| `config` | `QueryEngineConfig` | Immutable engine configuration (tools, commands, MCP, agents, system prompts, model) |
| `mutableMessages` | `Message[]` | Accumulated conversation messages across all turns |
| `abortController` | `AbortController` | Cancellation signal for the current turn |
| `permissionDenials` | `SDKPermissionDenial[]` | Accumulated denials for SDK result reporting |
| `totalUsage` | `NonNullableUsage` | Accumulated API token usage across all turns |
| `hasHandledOrphanedPermission` | `boolean` | One-shot guard for orphaned permission replay (fires once per engine lifetime) |
| `readFileState` | `FileStateCache` | Tracks files the model has read within this session |
| `discoveredSkillNames` | `Set<string>` | Turn-scoped skill discovery tracking for telemetry. Cleared at start of each `submitMessage()` |
| `loadedNestedMemoryPaths` | `Set<string>` | Persistable set of nested memory paths that have been loaded (survives across turns) |

#### Configuration: `QueryEngineConfig`

```typescript
type QueryEngineConfig = {
  cwd: string                           // Working directory
  tools: Tools                          // Available tools
  commands: Command[]                   // Slash commands
  mcpClients: MCPServerConnection[]     // MCP server connections
  agents: AgentDefinition[]             // Agent definitions
  canUseTool: CanUseToolFn              // Permission function
  getAppState: () => AppState           // App state accessor
  setAppState: (f: (prev: AppState) => AppState) => void  // App state mutator
  initialMessages?: Message[]           // Starting messages for resumption
  readFileCache: FileStateCache         // File state cache
  customSystemPrompt?: string           // Overrides default system prompt
  appendSystemPrompt?: string           // Appended after main system prompt
  userSpecifiedModel?: string           // User-chosen model
  fallbackModel?: string                // Fallback model
  thinkingConfig?: ThinkingConfig       // Extended thinking config
  maxTurns?: number                     // Max conversation turns
  maxBudgetUsd?: number                 // Max USD budget
  taskBudget?: { total: number }        // API task budget
  jsonSchema?: Record<string, unknown>  // Structured output schema
  verbose?: boolean                     // Verbose logging
  replayUserMessages?: boolean          // Replay user messages to SDK
  handleElicitation?: ToolUseContext['handleElicitation']  // MCP URL elicitation handler
  includePartialMessages?: boolean      // Include raw stream events
  setSDKStatus?: (status: SDKStatus) => void
  abortController?: AbortController
  orphanedPermission?: OrphanedPermission
  snipReplay?: (yieldedSystemMsg, store) => snip replay result | undefined  // SDK-only snip replay
}
```

#### Constructor

```typescript
constructor(config: QueryEngineConfig)
```

Initializes all private fields:
- `mutableMessages` from `initialMessages` (empty array default)
- `abortController` from config or `createAbortController()`
- `permissionDenials` as empty array
- `readFileState` from `readFileCache`
- `totalUsage` from `EMPTY_USAGE`
- `discoveredSkillNames` and `loadedNestedMemoryPaths` as empty Sets
- `hasHandledOrphanedPermission` = false

---

### Method: `submitMessage()` — The 5-Phase Lifecycle

```typescript
async *submitMessage(
  prompt: string | ContentBlockParam[],
  options?: { uuid?: string; isMeta?: boolean },
): AsyncGenerator<SDKMessage, void, unknown>
```

This is the heart of the engine. Each call represents a single user turn and traverses 5 distinct phases.

---

#### Phase 1: Initialization

**Steps:**

1. **Config extraction** (`:213-236`): Destructures all config fields, clears `discoveredSkillNames`, sets CWD, captures `startTime`.

2. **Permission wrapper** (`:244-271`): Wraps `canUseTool` to track denials. The wrapper calls the original function, then on non-`allow` results pushes to `permissionDenials[]` for SDK reporting (pairs tool name, tool_use_id, and input).

3. **System prompt construction** (`:273-325`):
   - Resolves model: `userSpecifiedModel` via `parseUserSpecifiedModel()` or `getMainLoopModel()`
   - Resolves thinking config: explicit `thinkingConfig` or `shouldEnableThinkingByDefault()` → adaptive/disabled
   - Calls `fetchSystemPromptParts()` with tools, model, additional working directories, MCP clients, custom prompt
   - Gets `defaultSystemPrompt`, `userContext`, `systemContext`
   - Merges coordinator user context if `COORDINATOR_MODE` feature gate
   - Injects memory mechanics prompt when SDK caller provides custom prompt AND `CLAUDE_COWORK_MEMORY_PATH_OVERRIDE` is set
   - Assembles final `systemPrompt` as `asSystemPrompt([customPrompt | default, memoryMechanics, appendSystemPrompt])`

4. **Structured output registration** (`:328-333`): If both `jsonSchema` and `SYNTHETIC_OUTPUT_TOOL_NAME` are present, registers structured output enforcement function hook.

5. **`ProcessUserInputContext` setup** (first instance, `:335-395`):
   Creates the context object passed to `processUserInput()`:
   - Writable `messages` and `setMessages` (writes back to `mutableMessages`)
   - Options: commands, tools, model, thinkingConfig, MCP, theme, agents, maxBudgetUsd
   - State accessors: `getAppState`, `setAppState`
   - `abortController`, `readFileState`, `nestedMemoryAttachmentTriggers` (empty), `loadedNestedMemoryPaths` (persistent), `dynamicSkillDirTriggers` (empty), `discoveredSkillNames` (turn-scoped)
   - File history and attribution updaters

6. **Orphaned permission handling** (`:397-408`): One-shot call to `handleOrphanedPermission()` if `orphanedPermission` is set and hasn't been handled. Replays restored tool permissions into the message stream. This is for SDK resume scenarios where an orphaned consent was persisted and needs re-injection.

7. **User input processing** (`:410-428`): Calls `processUserInput()` with:
   - Mode: `'prompt'`
   - The input prompt (string or ContentBlockParam[])
   - Messages context, custom UUID, isMeta flag
   - Returns: `messagesFromUserInput`, `shouldQuery`, `allowedTools`, `modelFromUserInput`, `resultText`

8. **Message persistence** (`:431-463`):
   - Pushes `messagesFromUserInput` into `this.mutableMessages`
   - Snapshots messages into local `messages` array
   - Persists transcript via `recordTranscript()` — **eager flush** in cowork mode: awaits the write, then flushes session storage to ensure transcript is resumable even if the process is killed before API responds

9. **Message replay/acknowledgement** (`:466-474`): Filters `messagesFromUserInput` for replayable messages (user messages that are non-meta, non-tool-result, selectable; plus compact boundaries). Stores in `messagesToAck` for later SDK acknowledgement.

10. **Permission context update** (`:477-486`): Updates `alwaysAllowRules.command` to `allowedTools` from user input processing.

11. **Model resolution** (`:488`): `modelFromUserInput ?? initialMainLoopModel`

12. **`ProcessUserInputContext` rebuild** (second instance, `:492-527`): Recreates after slash-command processing with updated `messages` and `model`. The `setMessages` is no-op this time (nothing else calls it past this point). Retains the same `updateFileHistoryState` and `updateAttributionState` references from the first instance.

13. **Skills and plugins loading** (`:529-538`): Cache-only load of slash command tool skills and enabled plugins. Must not block on network.

---

#### Phase 2: System Initialization Message

**`buildSystemInitMessage()`** (`:540-551`): Constructs and yields a system initialization message containing:
- Tools (with SDK-compatible names via `sdkCompatToolName`)
- MCP clients
- Model name
- Permission mode
- Commands
- Agent definitions
- Skills
- Enabled plugins
- Fast mode status

This message is the first message yielded to the SDK consumer, establishing the tool and capability surface.

---

#### Phase 3: Query Loop Integration

**for-await on `query()` generator** (`:675-1049`):

The `query()` function (from `src/query.ts`) is invoked with:
- `messages`, `systemPrompt`, `userContext`, `systemContext`
- `canUseTool: wrappedCanUseTool` (with denial tracking)
- `toolUseContext: processUserInputContext`
- `fallbackModel`, `querySource: 'sdk'`, `maxTurns`, `taskBudget`

This section is the message-processing switch that handles every message type yielded by the `query()` generator. See below for full switch documentation.

---

#### Message Processing Switch (within the for-await)

Each message from the `query()` generator is dispatched by `type`:

**`tombstone`** (`:758-760`):
- Control signal for removing orphaned messages from UI/transcript
- No-op in the switch — skip them
- Occurs during streaming fallback when partial messages with invalid thinking signatures must be removed

**`assistant`** (`:761-770`):
- Captures `stop_reason` from `message.message.stop_reason` (synthetic messages; streamed responses get it later via `message_delta`)
- Pushes to `this.mutableMessages` and local `messages` array
- Persists transcript via fire-and-forget `recordTranscript()` (not awaited — allows `message_delta` event to fire between content blocks)
- Yields normalized message via `normalizeMessage()`

**`progress`** (`:771-783`):
- Pushes to both `mutableMessages` and local `messages`
- Records transcript inline (fire-and-forget) — without this, deferred progress messages interleave with already-recorded tool_results and the dedup walk on resume freezes at the wrong parent UUID
- Yields normalized message

**`user`** (`:754, 784-787`):
- Increments `turnCount` first (turns are counted by user messages)
- Pushes to `mutableMessages`
- Yields normalized message

**`stream_event`** (`:788-828`):
Handles three sub-events:
- `message_start`: Resets `currentMessageUsage` to `EMPTY_USAGE`, then updates with the message's initial usage
- `message_delta`: Accumulates delta usage into `currentMessageUsage`, captures `stop_reason` from `delta.stop_reason` (this is where the real stop_reason arrives for streamed responses)
- `message_stop`: Accumulates `currentMessageUsage` into `this.totalUsage` via `accumulateUsage()`
- If `includePartialMessages` is true, yields the raw stream event to SDK

**`attachment`** (`:829-892`):
- Pushes to `mutableMessages` and local `messages`, records transcript inline
- Sub-type handlers:
  - `structured_output`: Captures `message.attachment.data` into `structuredOutputFromTool`
  - `max_turns_reached`: Flushes session storage (eager in cowork mode), yields `error_max_turns` result, returns
  - `queued_command` (when `replayUserMessages`): Yields as `SDKUserMessageReplay` with the command prompt

**`stream_request_start`** (`:894-896`):
- Suppressed — not yielded to SDK

**`system`** (`:897-957`):
- **Snip boundary replay**: If `config.snipReplay` is provided and the message is a snip boundary, replays snip compaction on `mutableMessages` and breaks
- **Compact boundary**: Yields `SDKCompactBoundaryMessage` with compact metadata. Releases pre-compaction messages from both `mutableMessages` and local `messages` for garbage collection (splices everything before the boundary)
- **API error**: Yields `api_retry` system message with attempt number, max retries, retry delay, error status, and categorized retryable error
- Other system messages: suppressed in headless mode

**`tool_use_summary`** (`:959-968`):
- Yields to SDK with summary text, preceding tool_use_ids, session_id, uuid

---

#### Phase 4: Termination Checks

Performed **inside** the for-await loop, checking on each yielded message:

**Budget exceeded** (`:972-1002`):
- If `maxBudgetUsd` is set and `getTotalCost() >= maxBudgetUsd`, flushes transcript (eager flush in cowork mode), yields `error_max_budget_usd` result, and returns early

**Structured output retries exceeded** (`:1004-1048`):
- If `jsonSchema` is set, counts `SYNTHETIC_OUTPUT_TOOL_NAME` tool calls in current query
- If `callsThisQuery >= MAX_STRUCTURED_OUTPUT_RETRIES` (env `MAX_STRUCTURED_OUTPUT_RETRIES` or default 5), yields `error_max_structured_output_retries` and returns

**Max turns** is handled inside `query.ts` itself and surfaced as `max_turns_reached` attachment.

---

#### Phase 5: Result Generation

After the for-await loop completes:

**Terminal state analysis** (`:1058-1068`):
- Finds the **last message** of type `assistant` or `user` in the messages array (not `mutableMessages`)
- `isResultSuccessful(result, lastStopReason)` (`utils/queryHelpers.ts:56-94`) checks:
  - Result is undefined → false
  - Assistant message whose **last content block** is `text`, `thinking`, or `redacted_thinking` → true (does **not** use `stop_reason` for assistant success)
  - User message where all content blocks are `tool_result` → true
  - `stopReason === 'end_turn'` carve-out when the API completed with zero assistant content blocks (e.g. task_notification drain turns) → true
  - Otherwise → false

**Error result** (`:1082-1118`):
If `isResultSuccessful` returns false, yields `error_during_execution` with diagnostic details: result_type, last_content_type, stop_reason, and error log entries scoped to current turn (using `errorLogWatermark`)

**Success result** (`:1120-1155`):
Extracts `textResult` from the last content block of the last assistant message (if it's a text block not in `SYNTHETIC_MESSAGES`). Sets `isApiError` from the assistant message's isApiErrorMessage flag. Yields `success` result with:
- `result`: extracted text
- `is_error`: true if API error message
- `stop_reason`, `structured_output` (from StructuredOutput tool), `usage`, `modelUsage`, `permission_denials`

---

### Other Methods

**`interrupt()`** `(:1158-1160)`:
Aborts the current abort controller, signaling cancellation to in-flight operations.

**`getMessages()`** `(:1162-1164)`:
Returns readonly snapshot of `mutableMessages`.

**`getReadFileState()`** `(:1166-1168)`:
Returns the file state cache (used by SDK to persist across engine reuse).

**`getSessionId()`** `(:1170-1172)`:
Returns the session ID from bootstrap state.

**`setModel(model: string)`** `(:1174-1176)`:
Sets `config.userSpecifiedModel`, affecting the next `submitMessage()` call.

---

### Function: `ask()` — Convenience Wrapper

```typescript
async function* ask({ commands, prompt, promptUuid, isMeta, cwd, tools,
  mcpClients, verbose, thinkingConfig, maxTurns, maxBudgetUsd, taskBudget,
  canUseTool, mutableMessages, getReadFileCache, setReadFileCache,
  customSystemPrompt, appendSystemPrompt, userSpecifiedModel, fallbackModel,
  jsonSchema, getAppState, setAppState, abortController, replayUserMessages,
  includePartialMessages, handleElicitation, agents, setSDKStatus,
  orphanedPermission }): AsyncGenerator<SDKMessage, void, unknown>
```

One-shot convenience wrapper. Creates a `QueryEngine`, calls `submitMessage(prompt)`, and in the `finally` block saves back `readFileState`. Used by `print.ts` for `-p` (non-interactive) mode.

Feature gate: If `HISTORY_SNIP` is enabled, injects `snipReplay` callback that checks if a system message is a snip boundary and, if so, force-applies snip compaction on the message store.

---

## query.ts — The Core Query Loop

**File location:** `src/query.ts` (1729 lines)

### Overview

`query()` is the **reactive query engine** — the actual conversation turn loop. It:
- Prefetches context (memory, skills)
- Manages context window via compaction pipeline
- Streams model responses
- Recovers from errors (max_output_tokens, prompt-too-long, media overflow)
- Executes tools and stop hooks
- Handles attachments and queued commands

### State Type Definition

```typescript
type State = {
  messages: Message[]                          // The conversation messages
  toolUseContext: ToolUseContext               // Tool execution context (mutable)
  autoCompactTracking: AutoCompactTrackingState | undefined  // Compaction tracker
  maxOutputTokensRecoveryCount: number         // Recovery attempts counter
  hasAttemptedReactiveCompact: boolean         // Whether reactive compact was tried
  maxOutputTokensOverride: number | undefined  // Override for max output tokens
  pendingToolUseSummary: Promise<ToolUseSummaryMessage | null> | undefined
  stopHookActive: boolean | undefined          // Whether stop hooks are active
  turnCount: number                            // Current turn count
  transition: Continue | undefined             // Why previous iteration continued
}
```

### `QueryParams`

```typescript
type QueryParams = {
  messages: Message[]
  systemPrompt: SystemPrompt
  userContext: { [k: string]: string }
  systemContext: { [k: string]: string }
  canUseTool: CanUseToolFn
  toolUseContext: ToolUseContext
  fallbackModel?: string
  querySource: QuerySource
  maxOutputTokensOverride?: number
  maxTurns?: number
  skipCacheWrite?: boolean
  taskBudget?: { total: number }
  deps?: QueryDeps
}
```

### Function: `query()`

```typescript
async function* query(params: QueryParams): AsyncGenerator<
  StreamEvent | RequestStartEvent | Message | TombstoneMessage | ToolUseSummaryMessage,
  Terminal
>
```

Outer wrapper that calls `queryLoop()`. When `queryLoop` returns normally (not via `.return()` or throw), notifies all consumed queued commands as `'completed'`. Returns the `Terminal` object.

### Function: `queryLoop()` — The Main Loop

#### Entry Setup

1. Destructures immutable params from `params`
2. Resolves `deps` from `params.deps ?? productionDeps()`
3. Initializes mutable `State` with `messages`, `toolUseContext`, `maxOutputTokensOverride`
4. Creates `budgetTracker` if `TOKEN_BUDGET` feature gate is enabled
5. Sets `taskBudgetRemaining` to undefined (tracked across compaction boundaries)
6. Snapshots `QueryConfig` via `buildQueryConfig()`
7. Fires `startRelevantMemoryPrefetch()` once per user turn (consumed later, per-iteration)
8. Enters `while (true)` loop

#### Per-Iteration Flow

**1. State Destructuring** (`:307-321`)
- Destructures `toolUseContext` (mutable within iteration) and all read-only fields: `messages`, `autoCompactTracking`, `maxOutputTokensRecoveryCount`, `hasAttemptedReactiveCompact`, `maxOutputTokensOverride`, `pendingToolUseSummary`, `stopHookActive`, `turnCount`

**2. Prefetch Initiation** (`:331-335`)
- Starts `skillPrefetch.startSkillDiscoveryPrefetch()` per-iteration (uses internal guard to skip non-write iterations)

**3. Query Chain Tracking** (`:347-363`)
- Initializes or increments `queryTracking` (chainId + depth)
- Only `queryTracking.chainId` is new for the first turn; subsequent turns increment depth

**4. Context Management Pipeline** (`:365-549`)

The pipeline processes `messagesForQuery` through these stages:

**a. Compact Boundary** (`:365`): `getMessagesAfterCompactBoundary(messages)` — discards pre-compaction messages, keeping only post-boundary history.

**b. Tool Result Budget** (`:369-394`): `applyToolResultBudget(messagesForQuery, ...)` — enforces per-message budget on aggregate tool result size. Runs BEFORE microcompact since cached MC operates by tool_use_id only. Persists replacements for `agent:` and `repl_main_thread` query sources.

**c. Snip Compact** (`:396-410`): If `HISTORY_SNIP` feature gate, `snipCompactIfNeeded(messagesForQuery)`. Records `snipTokensFreed` for autocompact threshold adjustment. Yields boundary message if created.

**d. Microcompact** (`:412-426`): `deps.microcompact(messagesForQuery, toolUseContext, querySource)` — removes tool result content referenced by tool_use_id, keeping only opaque tool_result blocks. Deferred boundary message with actual cache_deleted_input_tokens from API response.

**e. Context Collapse** (`:428-447`): If `CONTEXT_COLLAPSE` feature gate, `applyCollapsesIfNeeded(messagesForQuery, ...)` — projects collapsed context view. Runs BEFORE autocompact to allow collapse to bring context under autocompact threshold.

**f. System Prompt Assembly** (`:449-451`): `asSystemPrompt(appendSystemContext(systemPrompt, systemContext))` — merges system context (git status, cache breaker) into system prompt.

**g. Autocompact** (`:453-543`): `deps.autocompact(messagesForQuery, toolUseContext, cacheSafeParams, querySource, tracking, snipTokensFreed)`. Returns `{compactionResult, consecutiveFailures}`. If compaction succeeded:
- Logs telemetry with pre/post compact token counts
- Captures `preCompactContext` for task budget carryover
- Resets `tracking` with new turnId
- Builds post-compact messages, yields them, and replaces `messagesForQuery`

**Compaction triggers (summary):**

| Trigger | When | Where |
|---------|------|-------|
| **Proactive autocompact** | Estimated tokens ≥ autocompact threshold (`effectiveWindow - 13K`) | Start of each loop iteration, before API call |
| **Snip / microcompact / collapse** | Feature-gated thresholds; compose with autocompact | Same pre-API pipeline (snip → microcompact → collapse → autocompact) |
| **Blocking limit preempt** | At hard blocking limit when autocompact/reactive/collapse recovery is unavailable | Pre-API synthetic `prompt_too_long` error, returns `{reason: 'blocking_limit'}` |
| **Reactive compact** | Withheld 413 or media-size API error after a no-tool-call turn | Post-stream `!needsFollowUp` branch only |
| **Collapse drain** | Withheld 413, staged collapses pending | Post-stream, before reactive compact |
| **Proactive suppression** | `REACTIVE_COMPACT` (raccoon gate) or `CONTEXT_COLLAPSE` enabled | `shouldAutoCompact()` returns false; reactive compact remains 413 fallback |

Proactive autocompact is skipped for `querySource === 'compact'` or `'session_memory'` (fork deadlock guards). Reactive compact sets `hasAttemptedReactiveCompact` to prevent retry spirals.

**h. Model Selection** (`:570-579`): `getRuntimeMainLoopModel({permissionMode, mainLoopModel, exceeds200kTokens})` — in plan mode, if the most recent assistant message exceeds 200k tokens, selects the long-context model variant.

**i. Streaming Tool Executor** (`:561-568`): Creates `StreamingToolExecutor` if `config.gates.streamingToolExecution` is true.

**j. Dump Prompts Fetch** (`:588-590`): Creates `createDumpPromptsFetch()` for Ant debugging — once per query session to avoid memory retention.

**k. Blocking Limit Check** (`:593-648`): Skips if compaction just happened, snip was applied, reactive compact is enabled, or context collapse owns recovery. Otherwise calls `calculateTokenWarningState()` and if at blocking limit, yields API error and returns `{reason: 'blocking_limit'}`.

---

**5. API Streaming Loop** (`:650-954`)

The inner `while (attemptWithFallback)` loop:

**a. `deps.callModel()` call** (`:659-863`):
Streaming for-await on the model response. Key behaviors:
- **Backfill observable inputs** (`:748-787`): For tool_use blocks where the tool has `backfillObservableInput`, creates a cloned yield with the backfilled fields. Only yields a clone when fields were actually added (not just overwritten).
- **Error withholding** (`:799-822`): Withholds recoverable errors from yield:
  - Prompt-too-long (collapse withholder)
  - Prompt-too-long (reactive compact withholder)
  - Media size errors (reactive compact withholder)
  - Max output tokens error
- **Tool result streaming** (`:838-862`): If `streamingToolExecutor`, adds tool blocks to executor and yields completed results as they arrive.

**b. Deferred Microcompact Boundary** (`:866-892`):
If `CACHED_MICROCOMPACT`, computes the actual `cache_deleted_input_tokens` delta from the API response and yields the boundary message.

**c. Fallback Handling** (`:893-953`):
If `FallbackTriggeredError` is caught and `fallbackModel` is available:
- Switches model
- Yields missing tool result blocks for orphaned tool_use blocks
- Discards streaming tool executor and creates fresh one
- Strips signature blocks (Ant-only, for thinking compatibility)
- Logs event
- Sets `attemptWithFallback = true` to retry

**d. Error Catch** (`:955-997`):
Outer try/catch for non-recoverable errors:
- Image size errors: yields user-friendly message, returns `{reason: 'image_error'}`
- General errors: yields missing tool result blocks for all assistant messages, yields API error message, logs for Ant debugging, returns `{reason: 'model_error', error}`

---

**6. Post-Stream Pipeline** (`:999-1358`)

After streaming completes, three steps run **before** the `needsFollowUp` branch (they apply whether or not the model emitted tool calls):

**a. Post-Sampling Hooks** (`:999-1009`):
`executePostSamplingHooks([...messagesForQuery, ...assistantMessages], ...)` — fire-and-forget.

**b. Abort Check** (`:1015-1052`):
If `abortController.signal.aborted`, consumes remaining streamingToolExecutor results (generates synthetic tool_results for in-progress tools), runs chicago MCP cleanup, checks for interrupt vs aborted_streaming, returns `{reason: 'aborted_streaming'}`.

**c. Tool Use Summary** (`:1055-1060`):
Yields `pendingToolUseSummary` from the **previous** turn if available (Haiku summary generated during the prior model stream).

Then `query.ts` branches on `needsFollowUp` (set `true` during streaming whenever the assistant message contains `tool_use` blocks — **not** `stop_reason`):

When `needsFollowUp` is **false** (no tool calls — natural model completion):

**d. Collapse Drain Recovery** (`:1085-1117`):
For withheld 413 errors where previous transition was NOT `collapse_drain_retry`: drains all staged context-collapses. If any collapses were committed (`drained.committed > 0`), continues with `{reason: 'collapse_drain_retry'}`.

**e. Reactive Compact Recovery** (`:1119-1183`):
For withheld 413 or media errors: `reactiveCompact.tryReactiveCompact()`. If compacted:
- Captures pre-compact context for task budget
- Builds post-compact messages, yields them
- Resets state with `hasAttemptedReactiveCompact: true`
- Continues with `{reason: 'reactive_compact_retry'}`

If no recovery: surfaces the withheld error, calls `executeStopFailureHooks()`, returns.

**f. Max Output Tokens Recovery** (`:1188-1256`):
Two-phase recovery for max_output_tokens errors:

**Phase 1 — Escalation**: If the feature gate `tengu_otk_slot_v1` is enabled and no override was in effect and no `CLAUDE_CODE_MAX_OUTPUT_TOKENS` env var, retries the same request at `ESCALATED_MAX_TOKENS` (64k). Single-shot per turn.

**Phase 2 — Multi-turn**: If escalation already happened or is not available: injects a meta user message telling Claude to resume directly, increments `maxOutputTokensRecoveryCount`, continues. Limited to `MAX_OUTPUT_TOKENS_RECOVERY_LIMIT` (3) attempts.

If all recovery exhausted: yields the withheld error.

**g. API Error Bail** (`:1258-1265`):
If last message is an API error (rate limit, prompt-too-long, auth failure), calls `executeStopFailureHooks()` and returns `{reason: 'completed'}`. Skip stop hooks to prevent death spirals.

**h. Stop Hooks Execution** (`:1267-1306`):
Calls `handleStopHooks()` (see stopHooks section below). Runs only on the no-tool-call path — **not** after tool dispatch.

If `preventContinuation`: returns `{reason: 'stop_hook_prevented'}`

If `blockingErrors.length > 0`: resets state with errors appended, sets `stopHookActive: true`, continues with `{reason: 'stop_hook_blocking'}`. Preserves `hasAttemptedReactiveCompact` to prevent infinite loops.

**i. Token Budget Check** (`:1308-1355`):
If `TOKEN_BUDGET` feature gate: `checkTokenBudget(budgetTracker, agentId, getCurrentTurnTokenBudget(), getTurnOutputTokens())`.

If `action === 'continue'`: injects nudge message as meta user message, continues with `{reason: 'token_budget_continuation'}`.

If `action === 'stop'` with `completionEvent`: logs completion event, falls through to return `{reason: 'completed'}`.

**j. Natural End** (`:1357`):
Returns `{reason: 'completed'}` — the model chose not to use tools and all hooks/tracking passed.

---

**7. Tool Execution** (`:1360-1482`)

When `needsFollowUp` is **true** (assistant emitted tool_use blocks):

**a. Streaming Tool Executor** (`:1366-1408`):
If `streamingToolExecutor`: consumes remaining results via `getRemainingResults()`. Otherwise: calls `runTools(toolUseBlocks, assistantMessages, canUseTool, toolUseContext)`.

For each tool update:
- Yields the message
- Tracks `hook_stopped_continuation` attachments for `shouldPreventContinuation`
- Normalizes tool_results and pushes to `toolResults` array
- Updates `toolUseContext` if `update.newContext`

**b. Tool Use Summary Generation** (`:1411-1482`):
If `config.gates.emitToolUseSummaries` and tool_use blocks exist and not aborted and not a subagent:
- Extracts last assistant text for context
- Collects tool info (name, input, output) for each tool use block
- Fires `generateToolUseSummary()` as async promise (doesn't block next API call)
- Stores as `nextPendingToolUseSummary` for yield on next iteration

---

**8. Post-Tool Actions**

**a. Abort During Tools** (`:1484-1516`):
If aborted: chicago MCP cleanup, yields interruption message, checks maxTurns, returns.

**b. Hook Prevention** (`:1518-1521`):
If `shouldPreventContinuation`, returns `{reason: 'hook_stopped'}`.

**c. AutoCompact Turn Tracking** (`:1523-1533`):
If compaction happened, increments turn counter and logs.

**d. Attachment Processing** (`:1538-1590`):
Processes in order:
1. **Queued Commands**: `getCommandsByMaxPriority(sleepRan ? 'later' : 'next')`. Filters for non-slash commands, scoped to current agentId.
2. **Memory Attachments**: Via `getAttachmentMessages()` with full history.

**e. Memory Prefetch Consume** (`:1599-1614`):
If pending memory prefetch has settled: filters duplicates via `filterDuplicateMemoryAttachments()` using `readFileState`, yields memory attachments, marks consumed.

**f. Skill Prefetch Consume** (`:1617-1628`):
`skillPrefetch.collectSkillDiscoveryPrefetch()` — injects prefetched skill discovery attachments.

**g. Queued Command Cleanup** (`:1630-1643`):
Removes consumed queued commands, notifies lifecycle as `'started'`.

**h. Tool Refresh** (`:1660-1671`):
If `refreshTools` exists: refreshes tools between turns so newly-connected MCP servers become available.

**i. Task Summary** (`:1685-1702`):
If `BG_SESSIONS` feature gate and not subagent and time to generate: fires `maybeGenerateTaskSummary()` for `claude ps`.

**j. Max Turns Check** (`:1704-1712`):
If `nextTurnCount > maxTurns`: yields `max_turns_reached` attachment and returns.

**k. State Transition** (`:1714-1728`):
Constructs next `State` with `messages = [...messagesForQuery, ...assistantMessages, ...toolResults]`, updates `turnCount`, resets recovery counters, sets `pendingToolUseSummary`. Continues with `{reason: 'next_turn'}`.

---

### Error Classification & Recovery

| Error | Detection | Recovery Strategy |
|-------|-----------|-------------------|
| Prompt too long (413) | `isPromptTooLongMessage(message)` | Collapse drain → reactive compact → surface error |
| Media size error | `reactiveCompact.isWithheldMediaSizeError()` | Reactive compact strip-retry → surface error |
| Max output tokens | `message.apiError === 'max_output_tokens'` | Escalation (8k→64k) → multi-turn resume (3 attempts) |
| Streaming fallback | `FallbackTriggeredError` | Switch model, clear messages, retry |
| Image size | `ImageSizeError / ImageResizeError` | User-friendly error message |
| General error | Any other throw | Yield missing tool_result blocks, surface error |

---

## query/config.ts — Query Configuration

**File location:** `src/query/config.ts` (46 lines)

### Overview

Builds an immutable `QueryConfig` snapshot once at `query()` entry. Separating config from per-iteration state makes future `step()` extraction tractable.

### Type: `QueryConfig`

```typescript
type QueryConfig = {
  sessionId: SessionId
  gates: {
    streamingToolExecution: boolean  // Statsig gate: tengu_streaming_tool_execution2
    emitToolUseSummaries: boolean    // Env gate: CLAUDE_CODE_EMIT_TOOL_USE_SUMMARIES
    isAnt: boolean                   // Env gate: USER_TYPE === 'ant'
    fastModeEnabled: boolean         // Env gate: !CLAUDE_CODE_DISABLE_FAST_MODE
  }
}
```

### `buildQueryConfig()`

```typescript
function buildQueryConfig(): QueryConfig
```

Called once per `query()` invocation. Snapshots:
- `sessionId` from `getSessionId()`
- `streamingToolExecution` from Statsig `checkStatsigFeatureGate_CACHED_MAY_BE_STALE('tengu_streaming_tool_execution2')`
- `emitToolUseSummaries` from `isEnvTruthy(process.env.CLAUDE_CODE_EMIT_TOOL_USE_SUMMARIES)`
- `isAnt` from `process.env.USER_TYPE === 'ant'`
- `fastModeEnabled` from `!isEnvTruthy(process.env.CLAUDE_CODE_DISABLE_FAST_MODE)`

**Design note**: Intentionally excludes `feature()` gates — those are tree-shaking boundaries that must stay inline at the guarded blocks.

---

## query/deps.ts — Dependency Injection

**File location:** `src/query/deps.ts` (40 lines)

### Overview

Provides dependency injection for the `query()` function. Passing a `deps` override in `QueryParams` lets tests inject fakes directly instead of using per-module spying.

### Type: `QueryDeps`

```typescript
type QueryDeps = {
  callModel: typeof queryModelWithStreaming   // Model API call
  microcompact: typeof microcompactMessages    // Micro-compaction
  autocompact: typeof autoCompactIfNeeded      // Auto-compaction
  uuid: () => string                          // UUID generation
}
```

Using `typeof fn` keeps signatures automatically in sync with real implementations.

### `productionDeps()`

```typescript
function productionDeps(): QueryDeps
```

Returns production bindings: `queryModelWithStreaming`, `microcompactMessages`, `autoCompactIfNeeded`, and `crypto.randomUUID`.

---

## query/stopHooks.ts — Stop Hook Execution

**File location:** `src/query/stopHooks.ts` (473 lines)

### Overview

Executes post-turn hooks: Stop hooks, background housekeeping (prompt suggestion, memory extraction, auto-dream), and teammate lifecycle hooks (TeammateIdle, TaskCompleted). Called from `query.ts` at the end of each turn.

### Function: `handleStopHooks()`

```typescript
async function* handleStopHooks(
  messagesForQuery: Message[],
  assistantMessages: AssistantMessage[],
  systemPrompt: SystemPrompt,
  userContext: { [k: string]: string },
  systemContext: { [k: string]: string },
  toolUseContext: ToolUseContext,
  querySource: QuerySource,
  stopHookActive?: boolean,
): AsyncGenerator<StreamEvent | RequestStartEvent | Message | TombstoneMessage | ToolUseSummaryMessage, StopHookResult>
```

#### Execution Flow

**1. Hook Context Construction** (`:84-91`):
```typescript
const stopHookContext: REPLHookContext = {
  messages: [...messagesForQuery, ...assistantMessages],  // Full turn history
  systemPrompt, userContext, systemContext,
  toolUseContext, querySource,
}
```

**2. Cache-Safe Snapshot** (`:96-98`):
If `repl_main_thread` or `sdk` query source, saves cache-safe params for the REPL's `/btw` command and SDK's `side_question` control_request.

**3. Template Job Classifier** (`:100-132`):
If `TEMPLATES` feature gate and `CLAUDE_JOB_DIR` env is set and main thread:
- Classifies job state after each turn via `jobClassifier.classifyAndWriteState()`
- Filters full turn history for assistant messages
- Races against a 60s timeout to prevent hanging

**4. Background Housekeeping** (`:136-157`):
Skipped in `--bare` mode. Otherwise executes fire-and-forget:
- **Prompt Suggestion**: `executePromptSuggestion(stopHookContext)` (unless env-var disabled)
- **Memory Extraction**: `executeExtractMemories(stopHookContext, appendSystemMessage)` (if `EXTRACT_MEMORIES` gate, not subagent, extract mode active)
- **Auto-Dream**: `executeAutoDream(stopHookContext, appendSystemMessage)` (not subagent)

**5. Chicago MCP Cleanup** (`:164-173`):
Auto-unhide + lock release at turn end for computer use. Main thread only.

**6. Stop Hook Execution** (`:180-295`):

`executeStopHooks()` generator consumes:
- `permissionMode`, `abortController.signal`
- `stopHookActive` flag (carried over from previous iteration)
- `agentId`, `toolUseContext`, messages, `agentType`

For each result from the generator:
- **Progress messages**: Track `toolUseID`, count hooks, extract command/prompt text for `hookInfos`
- **Attachment messages**: Track by `hookEvent` type (`Stop`/`SubagentStop`):
  - `hook_non_blocking_error`: Records stderr/exit code
  - `hook_error_during_execution`: Records content
  - `hook_success`: Checks for non-empty stdout/stderr output
- **Blocking errors**: Creates user message with `getStopHookMessage()`, yields it, tracks in `blockingErrors`
- **Prevent continuation**: Sets `preventedContinuation = true`, yields `hook_stopped_continuation` attachment
- **Abort check**: On abort signal during hook execution, yields interruption message and returns `{preventContinuation: true}`

After generator exhausts:
- If `hookCount > 0`: yields `createStopHookSummaryMessage()` with counts, hook infos, errors, prevented state
- If `hookErrors.length > 0`: sends notification about hook errors
- If `preventedContinuation`: returns `{preventContinuation: true}`
- If `blockingErrors.length > 0`: returns `{blockingErrors, preventContinuation: false}`

**7. Teammate Hooks** (`:335-453`):
If `isTeammate()` returns true:

**a. TaskCompleted Hooks**:
- Lists tasks via `listTasks(taskListId)`
- Filters for `in_progress` tasks owned by this teammate
- For each: `executeTaskCompletedHooks(task.id, task.subject, task.description, teammateName, teamName, permissionMode, signal)`
- Same result processing as Stop hooks (blocking errors, preventContinuation)

**b. TeammateIdle Hooks**:
- `executeTeammateIdleHooks(teammateName, teamName, permissionMode, signal)`
- Same result processing

**8. Error Handling** (`:456-472`):
On exception: logs `tengu_stop_hook_error` with duration, yields warning system message, returns empty result.

---

## query/tokenBudget.ts — Token Budget Tracker

**File location:** `src/query/tokenBudget.ts` (93 lines)

### Overview

Tracks per-turn token budget consumption for the **`TOKEN_BUDGET`** feature — a **client-side** auto-continue nudge when the user specifies a token target in their prompt (e.g. `+500k`, `use 2M tokens`). Distinct from the API **`task_budget`** param (`QueryParams.taskBudget` → `configureTaskBudgetParams()` in `claude.ts`), which is server-side output budgeting.

Budget and baseline output tokens are set per user turn via `snapshotOutputTokensForTurn()` in the REPL (`bootstrap/state.ts`). `checkTokenBudget()` runs only on the **`!needsFollowUp`** path, **after** `handleStopHooks()` succeeds. Injects a nudge while turn output tokens are **under** 90% of budget and not diminishing. Detects diminishing returns after 3+ continuations.

### Constants

| Constant | Value | Purpose |
|----------|-------|---------|
| `COMPLETION_THRESHOLD` | `0.9` | Continue only while turn tokens are **below** 90% of budget |
| `DIMINISHING_THRESHOLD` | `500` | Tokens delta threshold for diminishing returns |

### Type: `BudgetTracker`

```typescript
type BudgetTracker = {
  continuationCount: number    // Number of continuation nudges sent
  lastDeltaTokens: number      // Token delta between last two checks
  lastGlobalTurnTokens: number // Tokens at last check
  startedAt: number            // Timestamp when tracker was created
}
```

### `createBudgetTracker()`

Initializes tracker with `continuationCount: 0`, `lastDeltaTokens: 0`, `lastGlobalTurnTokens: 0`, `startedAt: Date.now()`.

### `checkTokenBudget()`

```typescript
function checkTokenBudget(
  tracker: BudgetTracker,
  agentId: string | undefined,
  budget: number | null,
  globalTurnTokens: number,
): TokenBudgetDecision
```

**Decision logic**:

1. If `agentId` is set OR `budget` is null/zero: returns `{action: 'stop', completionEvent: null}` — subagents and no-budget sessions skip.

2. Computes `pct = turnTokens / budget * 100` and `deltaSinceLastCheck = globalTurnTokens - lastGlobalTurnTokens`.

3. **Diminishing returns detection**: True when `continuationCount >= 3` AND both last two deltas are below 500 tokens.

4. **Continue**: If NOT diminishing AND `turnTokens < budget * COMPLETION_THRESHOLD` (under 90%):
   - Increments `continuationCount`
   - Updates tracker state
   - Returns `{action: 'continue', nudgeMessage, continuationCount, pct, turnTokens, budget}`

5. **Stop with completion**: If diminishing OR has prior continuations:
   - Returns `{action: 'stop', completionEvent: {continuationCount, pct, turnTokens, budget, diminishingReturns, durationMs}}`

6. **Stop without completion**: Otherwise returns `{action: 'stop', completionEvent: null}`.

---

## context.ts — System & User Context

**File location:** `src/context.ts` (189 lines)

### Overview

Provides memoized system and user context that is prepended to each conversation. The system context includes git status; the user context includes CLAUDE.md files and the current date.

### System Prompt Injection

```typescript
let systemPromptInjection: string | null = null
export function getSystemPromptInjection(): string | null
export function setSystemPromptInjection(value: string | null): void
```

Ant-only, ephemeral debugging state for cache breaking. When injection is set, clears both `getUserContext` and `getSystemContext` memoization caches.

### `getGitStatus()`

```typescript
export const getGitStatus = memoize(async (): Promise<string | null> => { ... })
```

Memoized async function:
- Returns `null` in test mode (avoids cycles)
- Checks `getIsGit()` — if not a git repo, returns null
- If git repo, runs 5 git commands in parallel:
  - `getBranch()` — current branch name
  - `getDefaultBranch()` — main branch (for PR references)
  - `git status --short` — working tree status
  - `git log --oneline -n 5` — recent commits
  - `git config user.name` — git user name
- Truncates status at `MAX_STATUS_CHARS` (2000) with note about using BashTool
- Formats as multi-line string with section headers
- Logs detailed diagnostic timing for each step

### `getSystemContext()`

```typescript
export const getSystemContext = memoize(async (): Promise<{ [k: string]: string }> => { ... })
```

Returns context injected into the system prompt:
- **gitStatus**: From `getGitStatus()`, skipped in CCR (`CLAUDE_CODE_REMOTE`) or when git instructions are disabled
- **cacheBreaker**: If `BREAK_CACHE_COMMAND` feature gate and injection active, includes `[CACHE_BREAKER: <injection>]`

### `getUserContext()`

```typescript
export const getUserContext = memoize(async (): Promise<{ [k: string]: string }> => { ... })
```

Returns context prepended to user messages:
- **CLAUDE.md**: From `getClaudeMds(filterInjectedMemoryFiles(await getMemoryFiles()))`, unless disabled via `CLAUDE_CODE_DISABLE_CLAUDE_MDS` or `--bare` mode without explicit `--add-dir`
- **currentDate**: `Today's date is ${getLocalISODate()}.`

Caches CLAUDE.md content in bootstrap state for the auto-mode classifier (avoids circular import).

---

## cost-tracker.ts — Session Cost Tracking

**File location:** `src/cost-tracker.ts` (323 lines)

### Overview

Manages session-level cost tracking: total cost, token usage per model, API duration, code changes. Persists across session boundaries via project config.

### Core Functions

**`addToTotalSessionCost(cost, usage, model)`** `(:278-323)`:
- Calls `addToTotalModelUsage()` to accumulate per-model statistics
- Records to global cost state via `addToTotalCostState()`
- Increments cost and token counters (for metrics)
- Recursively processes advisor tool usage (if any), applying same cost accumulation

**`addToTotalModelUsage(cost, usage, model)`** `(:250-276)`:
- Gets or creates `ModelUsage` for model
- Accumulates: input_tokens, output_tokens, cache_read_input_tokens, cache_creation_input_tokens, web_search_requests, costUSD
- Sets contextWindow and maxOutputTokens

**`getStoredSessionCosts(sessionId)`** `(:87-123)`:
- Reads project config, returns cost state only if session ID matches
- Rebuilds model usage with context windows from stored data

**`restoreCostStateForSession(sessionId)`** `(:130-137)`:
- Calls `getStoredSessionCosts()`, if found restores to global state via `setCostStateForRestore()`
- Returns boolean indicating whether restore happened

**`saveCurrentSessionCosts(fpsMetrics?)`** `(:143-175)`:
- Saves accumulated costs to project config: totalCost, APIDuration, toolDuration, lines changed, token counts, model usage, session ID
- Called before switching sessions to avoid losing accumulated costs

**`formatTotalCost()`** `(:228-244)`:
- Returns chalk-dimmed string with total cost, API/wall duration, code changes, and per-model usage breakdown
- Handles unknown model costs with disclaimer

**`formatCost(cost, maxDecimalPlaces?)`** `(:177-179)`:
- Formats USD cost with >2 decimal places for sub-cent amounts

**Re-exports** (`:49-69`): Convenience re-exports from bootstrap state: `getTotalCost`, `getTotalDuration`, `getTotalAPIDuration`, etc.

---

## history.ts — Command History Persistence

**File location:** `src/history.ts` (464 lines)

### Overview

Persists and retrieves user command history for the interactive REPL. Supports up-arrow navigation, Ctrl+R search, and pasted content references. History is stored as JSONL in `~/.claude/history.jsonl`.

### Key Constants

| Constant | Value | Usage |
|----------|-------|-------|
| `MAX_HISTORY_ITEMS` | `100` | Max history entries to scan |
| `MAX_PASTED_CONTENT_LENGTH` | `1024` | Max chars to store inline (larger uses paste store) |

### Data Types

**`LogEntry`** — raw persisted form:
```typescript
type LogEntry = {
  display: string                                    // User-facing text
  pastedContents: Record<number, StoredPastedContent> // Paste refs
  timestamp: number                                   // Entry timestamp
  project: string                                     // Project root path
  sessionId?: string                                  // Current session ID
}
```

**`StoredPastedContent`** — paste storage variant:
```typescript
type StoredPastedContent = {
  id: number
  type: 'text' | 'image'
  content?: string        // Inline (small content)
  contentHash?: string    // Hash reference (large content → paste store)
  mediaType?: string
  filename?: string
}
```

### Paste Reference Functions

**`formatPastedTextRef(id, numLines)`** `(:51-56)`:
Formats `[Pasted text #N +M lines]`. If 0 lines, omits the line count.

**`formatImageRef(id)`** `(:58-60)`:
Formats `[Image #N]`.

**`parseReferences(input)`** `(:62-75)`:
Parses regex `/\[(Pasted text|Image|\.\.\.Truncated text) #(\d+)(?: \+\d+ lines)?(\.)*\]/g` for paste/image references.

**`expandPastedTextRefs(input, pastedContents)`** `(:81-100)`:
Replaces paste references in input with actual stored content. Processes in reverse order to maintain index validity.

### History Writing

**`addToHistory(command)`** `(:411-434)`:
Entry point. Skips if `CLAUDE_CODE_SKIP_PROMPT_HISTORY` is set (tmux sessions spawned by Tungsten tool). Registers cleanup handler on first call. Fires `addToPromptHistory()`.

**`addToPromptHistory(command)`** `(:355-409)`:
Converts pasted contents to `StoredPastedContent` (inline for <= 1024 chars, hash reference to paste store for larger). Pushes `LogEntry` to `pendingEntries`. Initiates `flushPromptHistory(0)`.

**`flushPromptHistory(retries)`** `(:329-353)`:
Guarded by `isWriting` flag. Calls `immediateFlushHistory()`. On failure, retries up to 5 times with 500ms backoff.

**`immediateFlushHistory()`** `(:292-327)`:
- If no pending entries, returns
- Ensures history file exists (append mode)
- Acquires file lock (`stale: 10000ms, retries: 3, minTimeout: 50ms`)
- Writes pending entries as JSONL
- Releases lock

### History Reading

**`makeLogEntryReader()`** `(:106-143)`:
Async generator yielding `LogEntry` from newest to oldest:
1. First yields pending (unflushed) entries
2. Then reads `history.jsonl` in reverse via `readLinesReverse()`
3. Filters out entries with `skippedTimestamps` (from `removeLastFromHistory`)
4. Skips malformed lines (non-critical)

**`getHistory()`** `(:190-217)`:
Async generator for interactive up-arrow. Yields current session entries first, then other sessions, deduped by project root. Limits to `MAX_HISTORY_ITEMS`.

**`getTimestampedHistory()`** `(:162-180)`:
For Ctrl+R picker. Yields `TimestampedHistoryEntry` with `display`, `timestamp`, and `resolve()` (lazy-loaded paste content). Deduped by display text within project scope.

**`makeHistoryReader()`** `(:145-149)`:
For backsearch, yields resolved `HistoryEntry` objects.

### History Management

**`clearPendingHistoryEntries()`** `(:436-440)`:
Resets `pendingEntries`, `lastAddedEntry`, and `skippedTimestamps`.

**`removeLastFromHistory()`** `(:453-464)`:
Undoes most recent `addToHistory`. Fast path: pops from pending buffer. Slow path: adds timestamp to skip-set for when entry was already flushed. One-shot; second call is no-op.

### Cleanup

On first `addToHistory()`, registers a cleanup function that:
1. Awaits any in-progress flush
2. If still pending entries, does one final `immediateFlushHistory()`

---

## tasks.ts — Task Implementation Registry

**File location:** `src/tasks.ts` (39 lines)

### Overview

Registry of task implementations. Tasks represent long-running background operations (shell commands, local agents, remote agents, workflows, MCP monitors, dreams).

### Task Implementations

```typescript
import { LocalShellTask } from './tasks/LocalShellTask/LocalShellTask.js'
import { LocalAgentTask } from './tasks/LocalAgentTask/LocalAgentTask.js'
import { RemoteAgentTask } from './tasks/RemoteAgentTask/RemoteAgentTask.js'
import { DreamTask } from './tasks/DreamTask/DreamTask.js'
```

Feature-gated (lazy-loaded):
- `LocalWorkflowTask` (gate: `WORKFLOW_SCRIPTS`)
- `MonitorMcpTask` (gate: `MONITOR_TOOL`)

### `getAllTasks()`

```typescript
function getAllTasks(): Task[]
```

Returns array of all available task implementations: `[LocalShellTask, LocalAgentTask, RemoteAgentTask, DreamTask]`, plus feature-gated `LocalWorkflowTask` and `MonitorMcpTask` if enabled.

### `getTaskByType(type)`

```typescript
function getTaskByType(type: TaskType): Task | undefined
```

Finds task by `TaskType`. Returns undefined if no match (including `in_process_teammate`, which has a `Task` implementation in `tasks/InProcessTeammateTask/` but is **not** registered here — teammate shutdown uses dedicated helpers).

---

## Tool.ts — Tool Interface & Context

**File location:** `src/Tool.ts` (792 lines)

### Exports (key types & functions)
- **`Tool`**, **`Tools`**, **`ToolDef`**, **`buildTool()`** — tool definition interface and builder
- **`ToolUseContext`**, **`ToolPermissionContext`**, **`getEmptyToolPermissionContext()`**
- **`ToolResult<T>`**, **`ValidationResult`**, **`ToolInputJSONSchema`**
- **`findToolByName(tools, name)`**, **`toolMatchesName()`**, **`filterToolProgressMessages()`**

### Main flow
Defines the contract every tool implements: `name`, Zod `inputSchema`, `prompt()`, `validateInput?()`, `call()`, optional streaming/progress hooks. `ToolUseContext` threads mutable session state (messages, MCP clients, abort signal, permission callbacks) into tool execution.

### Dependencies
- `types/permissions`, `types/tools`, `types/message`, `utils/fileStateCache`, Zod

### Feature gates / boundaries
- Type-only imports to break cycles; no runtime `feature()` gates in this file.

---

## commands.ts — Command Registry

**File location:** `src/commands.ts` (754 lines)

### Exports
- **`getCommands(cwd)`**: `Promise<Command[]>` — lazy-resolves all slash commands, filters by feature flags and availability
- **`findCommand()`**, **`hasCommand()`**, **`getCommand()`**, **`getCommandName()`**, **`isCommandEnabled()`**
- **`meetsAvailabilityRequirement()`**, **`filterCommandsForRemoteMode()`**, **`isBridgeSafeCommand()`**
- **`REMOTE_SAFE_COMMANDS`**, **`BRIDGE_SAFE_COMMANDS`**, **`INTERNAL_ONLY_COMMANDS`**
- Memoized helpers: **`getSkillToolCommands()`**, **`getSlashCommandToolSkills()`**, **`getMcpSkillCommands()`**
- Cache clears: **`clearCommandsCache()`**, **`clearCommandMemoizationCaches()`**

### Main flow
Hardcoded imports of 110+ command modules (many behind `feature()` require guards). `getCommands()` merges built-ins, plugins, skills, MCP skills; filters ant-only / remote / bridge contexts.

### Dependencies
- `commands/*`, `types/command`, `utils/plugins`, feature-gated command modules

### Feature gates / boundaries
- Per-command `feature()` requires for KAIROS, BRIDGE_MODE, ULTRAPLAN, etc.

---

## tools.ts — Tool Registry

**File location:** `src/tools.ts` (389 lines)

### Exports
- **`getTools(permissionContext)`**: Returns filtered `Tools` array for current session
- **`getAllBaseTools()`**, **`assembleToolPool()`**, **`getMergedTools()`**
- **`filterToolsByDenyRules()`**, **`parseToolPreset()`**, **`getToolsForDefaultPreset()`**
- **`TOOL_PRESETS`**, re-exports **`REPL_ONLY_TOOLS`**

### Main flow
Imports 40+ tool classes (feature-gated). `getTools()` applies permission context, ant-only filters, coordinator filter (via callers), and deny rules. Mirrors `commands.ts` registry pattern for DCE.

### Dependencies
- `tools/*`, `Tool.ts`, `services/mcp`, `utils/toolPool`

### Feature gates / boundaries
- `AGENT_TRIGGERS`, `KAIROS`, `MONITOR_TOOL`, `REPLTool` (ant-only), etc.

---

## tasks/ — Task Implementations

The registry in `tasks.ts` exposes kill dispatch for **`local_bash`**, **`local_agent`**, **`remote_agent`**, **`dream`**, plus optional **`local_workflow`** and **`monitor_mcp`**. Other task types below are managed via dedicated spawn helpers, not `getTaskByType()`.

### `tasks/types.ts` (42 lines)

#### Exports
- **`TaskState`**: Union of all concrete task state types
- **`BackgroundTaskState`**: Subset shown in background-task UI
- **`isBackgroundTask(task)`**: Running/pending && not foreground

### `tasks/stopTask.ts` (88 lines)

#### Exports
- **`StopTaskError`**: `{ code: 'not_found' | 'not_running' | 'unsupported_type' }`
- **`stopTask(taskId, context)`**: Lookup → validate running → `getTaskByType().kill()` → bash notification suppression

Used by `TaskStopTool` and SDK `stop_task` control request.

### `tasks/pillLabel.ts` (78 lines)

#### Exports
- **`getPillLabel(tasks)`**, **`pillNeedsCta(tasks)`**: Status-bar pill text for background tasks

### `tasks/LocalShellTask/LocalShellTask.tsx` (501 lines)

#### Exports
- **`LocalShellTask`**: `{ name, type: 'local_bash', kill }`
- **`spawnShellTask()`**, **`registerForeground()`**, **`backgroundAll()`**, **`unregisterForeground()`**
- **`looksLikePrompt()`**, **`hasForegroundTasks()`**

Shell execution with foreground/background lifecycle, output file streaming, monitor kind variant.

### `tasks/LocalShellTask/guards.ts` (37 lines)

#### Exports
- **`LocalShellTaskState`**, **`BashTaskKind`**, **`isLocalShellTask()`**

### `tasks/LocalShellTask/killShellTasks.ts` (69 lines)

#### Exports
- **`killTask()`**, **`killShellTasksForAgent()`**: Process termination for shell tasks

### `tasks/LocalAgentTask/LocalAgentTask.tsx` (654 lines)

#### Exports
- **`LocalAgentTask`**: `{ type: 'local_agent', kill: killAsyncAgent }`
- **`registerAsyncAgent()`**, **`registerAgentForeground()`**, **`backgroundAgentTask()`**
- **`completeAgentTask()`**, **`failAgentTask()`**, progress tracker helpers
- **`AgentProgress`**, **`createProgressTracker()`**, **`updateProgressFromMessage()`**

Local sub-agent execution with message queue, progress line, notification enqueue.

### `tasks/RemoteAgentTask/RemoteAgentTask.tsx` (815 lines)

#### Exports
- **`RemoteAgentTask`**: `{ type: 'remote_agent', kill }`
- **`registerRemoteAgentTask()`**, **`restoreRemoteAgentTasks()`**, **`checkRemoteAgentEligibility()`**
- **`getRemoteTaskSessionUrl()`**, completion checker registry, ultraplan failure notifications

Remote CCR/BYOC agent sessions with precondition checks and restore on startup.

### `tasks/LocalMainSessionTask.ts` (431 lines)

#### Exports
- **`LocalMainSessionTaskState`**, **`registerMainSessionTask()`**, **`completeMainSessionTask()`**
- **`foregroundMainSessionTask()`**, **`isMainSessionTask()`**, **`startBackgroundSession()`**

Main-thread agent packaged as a local agent task variant.

### `tasks/InProcessTeammateTask/InProcessTeammateTask.tsx` (118 lines)

#### Exports
- **`InProcessTeammateTask`**: `{ type: 'in_process_teammate', kill }` (not in `getAllTasks()` registry)
- **`requestTeammateShutdown()`**, **`injectUserMessageToTeammate()`**, **`appendTeammateMessage()`**
- **`findTeammateTaskByAgentId()`**, **`getRunningTeammatesSorted()`**

### `tasks/InProcessTeammateTask/types.ts` (104 lines)

#### Exports
- **`InProcessTeammateTaskState`**, **`TeammateIdentity`**, **`isInProcessTeammateTask()`**
- **`TEAMMATE_MESSAGES_UI_CAP`**, **`appendCappedMessage()`**

### `tasks/DreamTask/DreamTask.ts` (145 lines)

#### Exports
- **`DreamTask`**: `{ type: 'dream', kill }`
- **`DreamTaskState`**, **`registerDreamTask()`**, **`addDreamTurn()`**, **`completeDreamTask()`**, **`failDreamTask()`**

Auto-dream background summarization task (feature-gated usage from services layer).

---

## Task.ts — Task Types & Interfaces

**File location:** `src/Task.ts` (125 lines)

### Overview

Defines the task abstraction: types, statuses, lifecycle operations, and ID generation.

### `TaskType` Enum (Union)

```typescript
type TaskType =
  | 'local_bash'          // Shell command
  | 'local_agent'         // Local subagent
  | 'remote_agent'        // Remote subagent
  | 'in_process_teammate' // In-process teammate agent
  | 'local_workflow'      // Workflow script
  | 'monitor_mcp'         // MCP monitor
  | 'dream'               // Auto-dream background task
```

### `TaskStatus` Enum (Union)

```typescript
type TaskStatus = 'pending' | 'running' | 'completed' | 'failed' | 'killed'
```

### `isTerminalTaskStatus(status)`

```typescript
function isTerminalTaskStatus(status: TaskStatus): boolean
```

Returns true for `completed`, `failed`, or `killed`. Used to guard against injecting messages into dead teammates and for evicting finished tasks from AppState.

### Task Handle & Context

```typescript
type TaskHandle = { taskId: string; cleanup?: () => void }
type SetAppState = (f: (prev: AppState) => AppState) => void

type TaskContext = {
  abortController: AbortController
  getAppState: () => AppState
  setAppState: SetAppState
}
```

### `TaskStateBase`

```typescript
type TaskStateBase = {
  id: string              // Generated task ID
  type: TaskType          // Task variant
  status: TaskStatus      // Current lifecycle state
  description: string     // Human-readable description
  toolUseId?: string      // Associated tool_use block ID
  startTime: number       // Unix ms timestamp
  endTime?: number        // Set on terminal state
  totalPausedMs?: number  // Accumulated pause duration
  outputFile: string      // Path for output streaming
  outputOffset: number    // Byte offset in output file
  notified: boolean       // Whether user was notified of completion
}
```

### `LocalShellSpawnInput`

```typescript
type LocalShellSpawnInput = {
  command: string
  description: string
  timeout?: number
  toolUseId?: string
  agentId?: AgentId
  kind?: 'bash' | 'monitor'
}
```

### Task Interface

```typescript
type Task = {
  name: string
  type: TaskType
  kill(taskId: string, setAppState: SetAppState): Promise<void>
}
```

The `Task` interface is purposefully minimal — it only exposes `name`, `type`, and `kill`. Spawn and render were never called polymorphically.

### Task ID Generation

**ID Prefixes:**
| TaskType | Prefix |
|----------|--------|
| `local_bash` | `b` |
| `local_agent` | `a` |
| `remote_agent` | `r` |
| `in_process_teammate` | `t` |
| `local_workflow` | `w` |
| `monitor_mcp` | `m` |
| `dream` | `d` |

**Alphabet**: `0123456789abcdefghijklmnopqrstuvwxyz` (36 characters, ~2.8 trillion combinations with 8-char suffix)

**`generateTaskId(type)`** `(:98-106)`:
- Takes prefix + 8 random bytes modulo 36
- 36^8 ≈ 2.8 trillion combinations — sufficient to resist brute-force symlink attacks

**`createTaskStateBase(id, type, description, toolUseId?)`** `(:108-124)`:
Creates initial `TaskStateBase` with:
- `status: 'pending'`
- `startTime: Date.now()`
- `outputFile: getTaskOutputPath(id)`
- `outputOffset: 0`
- `notified: false`

---

## Cross-Cutting Architecture Notes

### Feature Gate Model

The codebase uses `feature()` from `bun:bundle` for tree-shaking. Feature-gated modules are imported via `require()` (not `import`) so that excluded strings are eliminated from external builds. Common gates:

| Gate | Files affected | Purpose |
|------|---------------|---------|
| `TOKEN_BUDGET` | query.ts, query/tokenBudget.ts, REPL | User-specified token-target auto-continue (e.g. `+500k`) |
| `HISTORY_SNIP` | query.ts, QueryEngine.ts | Snip-based history compaction |
| `CONTEXT_COLLAPSE` | query.ts | Context collapse projection |
| `REACTIVE_COMPACT` | query.ts | Reactive (413-triggered) compaction |
| `CACHED_MICROCOMPACT` | query.ts | Cache-editing microcompact |
| `EXTRACT_MEMORIES` | query/stopHooks.ts | Auto memory extraction |
| `TEMPLATES` | query/stopHooks.ts | Template job classification |
| `CHICAGO_MCP` | query.ts, stopHooks.ts | Computer use cleanup |
| `BG_SESSIONS` | query.ts | Background task summaries |
| `COORDINATOR_MODE` | QueryEngine.ts | Multi-agent coordination |
| `BREAK_CACHE_COMMAND` | context.ts | Cache-breaking injection |

### Message Flow

```
User Input → processUserInput() → QueryEngine.submitMessage()
  → query() → queryLoop() [while(true)]
    → Context Pipeline (compact boundary → tool budget → snip → microcompact → collapse → autocompact)
    → [optional] blocking-limit preempt (synthetic PTL, no API call)
    → deps.callModel() (= queryModelWithStreaming → queryModel) [streaming API]
    → Post-sampling hooks; abort check; yield prior-turn tool summary
    → if !needsFollowUp (no tool_use blocks):
        Recovery (collapse drain → reactive compact → max-output-tokens)
        → handleStopHooks() [Stop → TaskCompleted → TeammateIdle]
        → checkTokenBudget() [continue/stop]
        → return Terminal {reason: 'completed' | ...}
      else (needsFollowUp):
        Tool Execution [streaming/batch via runTools / StreamingToolExecutor]
        → Attachment Processing [queued commands, memory, skills]
        → max-turns check
        → State Transition → continue {reason: 'next_turn'}
  → QueryEngine result generation [isResultSuccessful → success | error_during_execution]
```

### Transcript Persistence

- **Eager flush in cowork mode**: When `CLAUDE_CODE_IS_COWORK` or `CLAUDE_CODE_EAGER_FLUSH` is set, `flushSessionStorage()` is called eagerly after each transcript write. In cowork/desktop, the process can be killed at any time; eager flush ensures the transcript is resumable.
- **Fire-and-forget for assistant messages**: In the for-await loop, assistant transcript writes are fire-and-forget to allow `message_delta` events to fire between content blocks.
- **Pre-query persistence**: The user's message is persisted to transcript BEFORE the API call so that transcripts remain resumable even if the process is killed before any response.
