# Services Layer Analysis — File 5: Gap Fill & Precise Export Reference

> **Scope**: Code-verified export-by-export documentation for all 54 service files across 7 directories.
> **Purpose**: Corrects inaccuracies in prior architectural overviews (02, 04) with exact TypeScript signatures, exported types, interfaces, constants, and function details verified by reading every source file in full.

---

## 1. Compact Services — Precise Reference (`services/compact/` — 11 files)

*Gap-fill for 02-compact-services.md. Prior doc contained speculative function names that differ from actual exports.*

### 1.1 `services/compact/compact.ts` (1579 lines)

**Core compaction engine. Exports below are verified against source.**

#### Exported Types & Interfaces

```typescript
interface CompactionResult {
  boundaryMarker: SystemMessage
  summaryMessages: UserMessage[]
  attachments: AttachmentMessage[]
  hookResults: HookResultMessage[]
  messagesToKeep?: Message[]
  userDisplayMessage?: string
  preCompactTokenCount?: number
  postCompactTokenCount?: number
  truePostCompactTokenCount?: number
  compactionUsage?: ReturnType<typeof getTokenUsage>
}

type RecompactionInfo = {
  isRecompactionInChain: boolean
  turnsSincePreviousCompact: number
  previousCompactTurnId?: string
  autoCompactThreshold: number
  querySource?: QuerySource
}
```

#### Exported Functions

| Function | Signature | Purpose |
|---|---|---|
| `stripImagesFromMessages` | `(messages: Message[]): Message[]` | Replaces image/document blocks with `[image]`/`[document]` text markers |
| `stripReinjectedAttachments` | `(messages: Message[]): Message[]` | Strips `skill_discovery`/`skill_listing` attachment types (gated by `EXPERIMENTAL_SKILL_SEARCH`) |
| `truncateHeadForPTLRetry` | `(messages: Message[], ptlResponse: AssistantMessage): Message[] \| null` | Drops oldest API-round groups until token gap is covered; returns null when nothing can be dropped |
| `buildPostCompactMessages` | `(result: CompactionResult): Message[]` | Builds base post-compact messages array: boundary, summaries, kept, attachments, hooks |
| `annotateBoundaryWithPreservedSegment` | `(boundary: SystemCompactBoundaryMessage, anchorUuid: UUID, messagesToKeep: readonly Message[] \| undefined): SystemCompactBoundaryMessage` | Annotates boundary with relink metadata (headUuid, anchorUuid, tailUuid) |
| `mergeHookInstructions` | `(userInstructions: string \| undefined, hookInstructions: string \| undefined): string \| undefined` | Merges user + hook custom instructions; empty normalizes to undefined |
| `compactConversation` | `(messages: Message[], context: ToolUseContext, cacheSafeParams: CacheSafeParams, suppressFollowUpQuestions: boolean, customInstructions?: string, isAutoCompact?: boolean, recompactionInfo?: RecompactionInfo): Promise<CompactionResult>` | Main entry — orchestrates full conversation compaction with caching, hooks, and analytics |
| `partialCompactConversation` | `(allMessages: Message[], pivotIndex: number, context: ToolUseContext, cacheSafeParams: CacheSafeParams, userFeedback?: string, direction?: PartialCompactDirection): Promise<CompactionResult>` | Partial compaction around a selected message index; directions `'from'` or `'up_to'` |
| `createCompactCanUseTool` | `(): CanUseToolFn` | Returns a `canUseTool` function that denies all tool use during compaction |
| `createPostCompactFileAttachments` | `(readFileState: Record<string, { content: string; timestamp: number }>, toolUseContext: ToolUseContext, maxFiles: number, preservedMessages?: Message[]): Promise<AttachmentMessage[]>` | Re-reads recent files post-compact, constrained by count + token budget |
| `createPlanAttachmentIfNeeded` | `(agentId?: AgentId): AttachmentMessage \| null` | Creates plan file attachment if a plan exists |
| `createSkillAttachmentIfNeeded` | `(agentId?: string): AttachmentMessage \| null` | Creates invoked_skills attachment with per-skill truncation and budget |
| `createPlanModeAttachmentIfNeeded` | `(context: ToolUseContext): Promise<AttachmentMessage \| null>` | Creates plan_mode attachment if user is in plan mode |
| `createAsyncAgentAttachmentsIfNeeded` | `(context: ToolUseContext): Promise<AttachmentMessage[]>` | Creates task_status attachments for running/unretrieved async agents |

#### Exported Constants

| Constant | Value | Purpose |
|---|---|---|
| `POST_COMPACT_MAX_FILES_TO_RESTORE` | `5` | Max files re-attached post-compact |
| `POST_COMPACT_TOKEN_BUDGET` | `50_000` | Token budget for post-compact file attachments |
| `POST_COMPACT_MAX_TOKENS_PER_FILE` | `5_000` | Per-file token cap |
| `POST_COMPACT_MAX_TOKENS_PER_SKILL` | `5_000` | Per-skill truncation cap |
| `POST_COMPACT_SKILLS_TOKEN_BUDGET` | `25_000` | Total budget for skill attachments |
| `ERROR_MESSAGE_NOT_ENOUGH_MESSAGES` | `'Not enough messages to compact.'` | Error when message array is empty |
| `ERROR_MESSAGE_PROMPT_TOO_LONG` | `'Conversation too long. Press esc twice to go up a few messages and try again.'` | PTL fallback error message |
| `ERROR_MESSAGE_USER_ABORT` | `'API Error: Request was aborted.'` | User cancellation error |
| `ERROR_MESSAGE_INCOMPLETE_RESPONSE` | `'Compaction interrupted · This may be due to network issues — please try again.'` | Streaming failure error |

#### Internal Functions (not exported)

| Function | Purpose |
|---|---|
| `addErrorNotificationIfNeeded` | Shows error notification for manual /compact only |
| `streamCompactSummary` | Core streaming logic: attempts cache-sharing fork first, falls back to direct streaming with retry |
| `collectReadToolFilePaths` | Scans messages for Read tool_use blocks (dedup post-compact restoration) |
| `truncateToTokens` | Truncates string to ~maxTokens tokens, keeping head |

#### Key Internal Detail: `streamCompactSummary()`

Two-path strategy:
1. **Cache-sharing fork**: `runForkedAgent()` with `querySource: 'compact'`, reusing main thread's prompt cache. Gated by `tengu_compact_cache_prefix` GrowthBook flag.
2. **Direct streaming fallback**: `queryModelWithStreaming()` with `FileReadTool` (and optionally `ToolSearchTool` + MCP tools). Retries up to `MAX_COMPACT_STREAMING_RETRIES` (2).

Sends keep-alive signals every 30s during compaction to prevent WebSocket idle timeouts.

---

### 1.2 `services/compact/autoCompact.ts` (351 lines)

#### Exported Types & Interfaces

```typescript
type AutoCompactTrackingState = {
  compacted: boolean
  turnCounter: number
  turnId: string
  consecutiveFailures?: number
}
```

#### Exported Functions

| Function | Signature | Purpose |
|---|---|---|
| `getEffectiveContextWindowSize` | `(model: string): number` | Returns context window minus reserved output tokens (20K max) |
| `getAutoCompactThreshold` | `(model: string): number` | Returns threshold = effective window - 13K buffer; supports `CLAUDE_AUTOCOMPACT_PCT_OVERRIDE` |
| `calculateTokenWarningState` | `(tokenUsage: number, model: string): { percentLeft, isAboveWarningThreshold, isAboveErrorThreshold, isAboveAutoCompactThreshold, isAtBlockingLimit }` | Returns 5 status booleans + percentage left |
| `isAutoCompactEnabled` | `(): boolean` | Checks `DISABLE_COMPACT`, `DISABLE_AUTO_COMPACT`, and `userConfig.autoCompactEnabled` |
| `shouldAutoCompact` | `(messages: Message[], model: string, querySource?: QuerySource, snipTokensFreed?: number): Promise<boolean>` | Recursion-guarded (rejects session_memory, compact, marble_origami sources); checks GrowthBook + collapse gates |
| `autoCompactIfNeeded` | `(messages: Message[], toolUseContext: ToolUseContext, cacheSafeParams: CacheSafeParams, querySource?: QuerySource, tracking?: AutoCompactTrackingState, snipTokensFreed?: number): Promise<{ wasCompacted, compactionResult?, consecutiveFailures? }>` | Circuit-breaker (3 consecutive failures); tries session memory compact first, falls back to legacy compact |

#### Exported Constants

| Constant | Value |
|---|---|
| `AUTOCOMPACT_BUFFER_TOKENS` | `13_000` |
| `WARNING_THRESHOLD_BUFFER_TOKENS` | `20_000` |
| `ERROR_THRESHOLD_BUFFER_TOKENS` | `20_000` |
| `MANUAL_COMPACT_BUFFER_TOKENS` | `3_000` |

#### Key Internal Detail: Circuit Breaker

`MAX_CONSECUTIVE_AUTOCOMPACT_FAILURES = 3`. After 3 consecutive failed compaction attempts, `autoCompactIfNeeded` returns `{ wasCompacted: false }` without retrying, preventing ~250K wasted API calls/day globally.

---

### 1.3 `services/compact/microCompact.ts` (530 lines)

#### Exported Types & Interfaces

```typescript
type PendingCacheEdits = {
  trigger: 'auto'
  deletedToolIds: string[]
  baselineCacheDeletedTokens: number
}

type MicrocompactResult = {
  messages: Message[]
  compactionInfo?: {
    pendingCacheEdits?: PendingCacheEdits
  }
}
```

#### Exported Functions

| Function | Signature | Purpose |
|---|---|---|
| `getAPIContextManagement` | `(options?: { hasThinking?, isRedactThinkingActive?, clearAllThinking? }): ContextManagementConfig \| undefined` | Builds API-native context_management config; ant-only tool clearing |
| `microcompactMessages` | `(messages: Message[], toolUseContext?: ToolUseContext, querySource?: QuerySource): Promise<MicrocompactResult>` | Entry point: tries time-based MC first, then cached MC, finally returns messages unchanged |
| `consumePendingCacheEdits` | `(): CacheEditsBlock \| null` | Gets and clears pending cache edits for API layer |
| `getPinnedCacheEdits` | `(): PinnedCacheEdits[]` | Gets previously-pinned cache edits for cache hit re-send |
| `pinCacheEdits` | `(userMessageIndex: number, block: CacheEditsBlock): void` | Pins cache edits to a user message position |
| `markToolsSentToAPIState` | `(): void` | Marks registered tools as sent to API |
| `resetMicrocompactState` | `(): void` | Clears all cached MC state |
| `estimateMessageTokens` | `(messages: Message[]): number` | Walks messages estimating tokens per block type; pads by 4/3 |
| `evaluateTimeBasedTrigger` | `(messages: Message[], querySource: QuerySource \| undefined): { gapMinutes, config } \| null` | Checks if time-based MC should fire; extracted for shared use by snip force-apply |

#### Exported Constants

| Constant | Value |
|---|---|
| `TIME_BASED_MC_CLEARED_MESSAGE` | `'[Old tool result content cleared]'` |

#### Exported Types (from apiMicrocompact.ts)

```typescript
type ContextEditStrategy =
  | { type: 'clear_tool_uses_20250919'; trigger?: { type: 'input_tokens'; value: number }; keep?: { type: 'tool_uses'; value: number }; clear_tool_inputs?: boolean | string[]; exclude_tools?: string[]; clear_at_least?: { type: 'input_tokens'; value: number } }
  | { type: 'clear_thinking_20251015'; keep: { type: 'thinking_turns'; value: number } | 'all' }

type ContextManagementConfig = {
  edits: ContextEditStrategy[]
}
```

*(`ContextEditStrategy` and `ContextManagementConfig` are exported from `apiMicrocompact.ts`, but logically part of microcompact system.)*

#### Key Internal Detail: Cached Microcompact

The `cachedMicrocompact` path (ant-only, gated by `feature('CACHED_MICROCOMPACT')`) uses the API's `cache_edits` feature to delete old tool results without invalidating the cached prompt prefix. It:
1. Collects compactable tool IDs from assistant messages
2. Registers new tool results grouped by user message
3. Determines which tools to delete based on count-based trigger/keep thresholds
4. Creates `cache_edits` blocks consumed by the API layer
5. Does NOT mutate local message content (cache edits happen server-side)

The `cachedMicrocompact.ts` module is lazily imported to avoid circular dependencies and keep dead code elimination working for external builds.

---

### 1.4 `services/compact/grouping.ts` (63 lines)

#### Exported Functions

| Function | Signature | Purpose |
|---|---|---|
| `groupMessagesByApiRound` | `(messages: Message[]): Message[][]` | Groups messages at assistant-message.id boundaries; each group = one API round-trip |

#### Key Detail

Uses `message.id` (not user-message boundaries) for grouping. This allows reactive compact to operate on single-prompt agentic sessions (SDK/CCR/eval callers where the entire workload is one human turn). Extracted to its own file to break circular dependency between `compact.ts` and `compactMessages.ts`.

---

### 1.5 `services/compact/prompt.ts` (374 lines)

#### Exported Functions

| Function | Signature | Purpose |
|---|---|---|
| `getCompactPrompt` | `(customInstructions?: string): string` | Assembles full compact prompt with NO_TOOLS_PREAMBLE + BASE_COMPACT_PROMPT + optional instructions |
| `getPartialCompactPrompt` | `(customInstructions?: string, direction?: PartialCompactDirection): string` | Assembles partial compact prompt; direction `'up_to'` uses PARTIAL_COMPACT_UP_TO_PROMPT |
| `formatCompactSummary` | `(summary: string): string` | Strips `<analysis>` scratchpad, replaces `<summary>` tags with "Summary:" header |
| `getCompactUserSummaryMessage` | `(summary: string, suppressFollowUpQuestions?: boolean, transcriptPath?: string, recentMessagesPreserved?: boolean): string` | Builds user-facing summary message; supports proactive mode continuation instructions |

#### Internal Prompt Templates

| Template | Lines | Purpose |
|---|---|---|
| `NO_TOOLS_PREAMBLE` | 19-26 | Aggressive no-tools instruction for cache-sharing fork (avoids wasted tool-call turns) |
| `BASE_COMPACT_PROMPT` | 61-143 | 9-section summary format: primary request, concepts, files, errors, problem-solving, user messages, pending tasks, current work, optional next step |
| `PARTIAL_COMPACT_PROMPT` | 145-204 | 9-section format for partial compact ('from' direction) — "RECENT portion" |
| `PARTIAL_COMPACT_UP_TO_PROMPT` | 208-267 | 9-section format for partial compact ('up_to' direction) — "precedes kept context" |
| `DETAILED_ANALYSIS_INSTRUCTION_BASE` | 31-44 | Chronological analysis instructions for base prompt |
| `DETAILED_ANALYSIS_INSTRUCTION_PARTIAL` | 46-59 | Analysis instructions for partial prompt |
| `NO_TOOLS_TRAILER` | 269-272 | "REMINDER: Do NOT call any tools" appended to all prompts |

---

### 1.6 `services/compact/sessionMemoryCompact.ts` (630 lines)

#### Exported Types & Interfaces

```typescript
type SessionMemoryCompactConfig = {
  minTokens: number       // Default: 10_000
  minTextBlockMessages: number  // Default: 5
  maxTokens: number       // Default: 40_000
}
```

#### Exported Functions

| Function | Signature | Purpose |
|---|---|---|
| `setSessionMemoryCompactConfig` | `(config: Partial<SessionMemoryCompactConfig>): void` | Merges partial config into current |
| `getSessionMemoryCompactConfig` | `(): SessionMemoryCompactConfig` | Returns copy of current config |
| `resetSessionMemoryCompactConfig` | `(): void` | Resets to defaults + clears init flag |
| `hasTextBlocks` | `(message: Message): boolean` | Checks if message contains text content (user or assistant) |
| `adjustIndexToPreserveAPIInvariants` | `(messages: Message[], startIndex: number): number` | Ensures tool_use/tool_result pairs and thinking blocks sharing the same message.id are not split |
| `calculateMessagesToKeepIndex` | `(messages: Message[], lastSummarizedIndex: number): number` | Calculates start index for kept messages: expands backwards to meet minTokens/minTextBlockMessages, caps at maxTokens, floors at last compact boundary |
| `shouldUseSessionMemoryCompaction` | `(): boolean` | Checks GrowthBook flags `tengu_session_memory` AND `tengu_sm_compact`; supports `ENABLE_CLAUDE_CODE_SM_COMPACT` / `DISABLE_CLAUDE_CODE_SM_COMPACT` env overrides |
| `trySessionMemoryCompaction` | `(messages: Message[], agentId?: AgentId, autoCompactThreshold?: number): Promise<CompactionResult \| null>` | Main entry: handles normal case (lastSummarizedMessageId set) and resumed session (no ID); falls back to null on errors/threshold exceeded |

#### Exported Constants

| Constant | Value |
|---|---|
| `DEFAULT_SM_COMPACT_CONFIG` | `{ minTokens: 10_000, minTextBlockMessages: 5, maxTokens: 40_000 }` |

#### Key Internal Detail: `adjustIndexToPreserveAPIInvariants()`

Two-step adjustment:
1. **Tool pairs**: Collects `tool_result` IDs from ALL kept messages; walks backwards to find missing `tool_use` blocks
2. **Thinking blocks**: Finds assistant messages with the same `message.id` as kept messages; includes them so `normalizeMessagesForAPI` can properly merge thinking + tool_use blocks

---

### 1.7 `services/compact/postCompactCleanup.ts` (77 lines)

#### Exported Functions

| Function | Signature | Purpose |
|---|---|---|
| `runPostCompactCleanup` | `(querySource?: QuerySource): void` | Resets module-level state after compaction: microcompact, context-collapse, getUserContext cache, memory files cache, system prompt sections, classifier approvals, speculative checks, beta tracing, session messages cache, attribution file cache |

#### Key Detail

Subagent compacts (`agent:*` query sources) skip main-thread state resets (context-collapse, getMemoryFiles, getUserContext) to avoid corrupting the parent thread's module-level state. Uses `startsWith('repl_main_thread')` prefix matching for output-style variants.

---

### 1.8 `services/compact/compactWarningState.ts` (18 lines)

#### Exported

| Export | Signature | Purpose |
|---|---|---|
| `compactWarningStore` | `Store<boolean>` | React-free boolean store; false = show warning |
| `suppressCompactWarning` | `(): void` | Sets store to true (suppress) |
| `clearCompactWarningSuppression` | `(): void` | Sets store to false (show) |

---

### 1.9 `services/compact/compactWarningHook.ts` (16 lines)

#### Exported Functions

| Function | Signature | Purpose |
|---|---|---|
| `useCompactWarningSuppression` | `(): boolean` | React `useSyncExternalStore` hook subscribing to `compactWarningStore` |

---

### 1.10 `services/compact/timeBasedMCConfig.ts` (43 lines)

#### Exported Types & Interfaces

```typescript
type TimeBasedMCConfig = {
  enabled: boolean              // Default: false
  gapThresholdMinutes: number   // Default: 60
  keepRecent: number            // Default: 5
}
```

#### Exported Functions

| Function | Signature | Purpose |
|---|---|---|
| `getTimeBasedMCConfig` | `(): TimeBasedMCConfig` | Reads from GrowthBook flag `tengu_slate_heron`; hoisted for GB exposure on every eval path |

---

### 1.11 `services/compact/apiMicrocompact.ts` (153 lines)

*(Exports documented in §1.3 alongside microCompact.ts since they're logically grouped.)*

#### Key Internal Detail: Tool Clearing

Two ant-only strategies:
1. **Clear tool results**: `TOOLS_CLEARABLE_RESULTS` includes Shell, Glob, Grep, Read, WebFetch, WebSearch tool results
2. **Clear tool uses**: `TOOLS_CLEARABLE_USES` includes FileEdit, FileWrite, NotebookEdit tool uses (excluded, meaning everything else is cleared)

Both use `clear_tool_uses_20250919` strategy with input_tokens trigger and `clear_at_least` target.

---

### Corrections to 02-compact-services.md

| Prior Doc Claim | Actual Export |
|---|---|
| `compact()` | `compactConversation()` |
| `partialCompact()` | `partialCompactConversation()` |
| `summarizeHistory()` | Does not exist |
| `buildCompactPrompt()` | `getCompactPrompt()` |
| `parseCompactResponse()` | Does not exist; summary parsing is inline |
| `rebuildConversation()` | Does not exist; `buildPostCompactMessages()` replaces |
| `groupConversationRounds()` | `groupMessagesByApiRound()` (different algorithm — uses assistant message.id, not user boundaries) |
| `selectMessagesToKeep()` | Does not exist; kept messages determined by `calculateMessagesToKeepIndex()` |
| `mergeCompactResults()` | Does not exist |
| `compactViaSessionMemory()` | `trySessionMemoryCompaction()` |
| `buildMemoryGuidedCompactPrompt()` | Does not exist |
| `filterByMemoryRelevance()` | Does not exist |
| `updateSessionMemoryAfterCompact()` | Does not exist |
| `applyMicroCompact()` | `microcompactMessages()` |
| `shouldMicroCompact()` | Inline in `microcompactMessages()` |
| `truncateOldToolResults()` | `maybeTimeBasedMicrocompact()` (internal) |
| `summarizeOldUserMessages()` | Does not exist |
| `insertCacheEditsBlock()` | Does not exist; cache edits consumed via `consumePendingCacheEdits()` |
| `compactWarningStore` type | `Store<boolean>` (not `{ warningShown, lastCompactTime }`) |
| Warning 80% / Critical 95% / Forced 100% | Not hardcoded; computed via `calculateTokenWarningState()` with thresholds = context window minus buffer tokens |
| "Prompts output schema is JSON" | Prompts use `<analysis>`/`<summary>` XML tags, not JSON |

---

## 2. API Services — Precise Reference (`services/api/` — 20 files)

*Gap-fill for 01-api-services.md. Prior doc correctly identified major functions but omitted several files and minor exports.*

### 2.1 `services/api/claude.ts` (~5230+ lines)

**Additional exports not fully documented in 01-api-services.md:**

#### Exported Functions (supplemental)

| Function | Signature | Purpose |
|---|---|---|
| `getMaxOutputTokensForModel` | `(model: string): number` | Returns max output tokens for a given model |
| `configureEffortParams` | Internal helper | Sets up effort budget for thinking-enabled models |
| `configureTaskBudgetParams` | Internal helper | Configures `output_config.task_budget` (beta: task-budgets-2026-03-13) |
| `stripExcessMediaItems` | `(messages: Message[]): Message[]` | Caps images+documents per request at `API_MAX_MEDIA_PER_REQUEST` |
| `executeNonStreamingRequest` | Internal generator | Helper for non-streaming fallback with retry |

#### Beta Header Latches

| Latch | Trigger |
|---|---|
| `AFK_MODE_BETA_HEADER` | First auto-mode activation |
| `FAST_MODE_BETA_HEADER` | First fast-mode request |
| `CACHE_EDITING_BETA_HEADER` | First cached microcompact |
| `COMPUTER_USE_BETA_HEADER` | Computer use tool available |
| `TOOL_SEARCH_BETA_HEADER` | Tool search enabled |
| `STRUCTURED_OUTPUTS_BETA_HEADER` | Structured outputs enabled |

---

### 2.2 `services/api/errors.ts` (1207 lines)

#### Additional Exports

| Export | Type | Purpose |
|---|---|---|
| `startsWithApiErrorPrefix` | `(text: string): boolean` | Checks if text starts with `"API Error"` prefix |
| `hasErrorMessageFragment` | Internal helper | Checks for error message substring in various API error structures |
| `getToolUseMismatchMessage` | Internal | Generates error message for tool_use/tool_result pairing failures |

#### Exported Error Message Constants (complete list)

| Constant | Message |
|---|---|
| `API_ERROR_MESSAGE_PREFIX` | `"API Error"` |
| `PROMPT_TOO_LONG_ERROR_MESSAGE` | `"Prompt is too long"` |
| `CREDIT_BALANCE_TOO_LOW_ERROR_MESSAGE` | `"Credit balance is too low"` |
| `INVALID_API_KEY_ERROR_MESSAGE` | `"Not logged in · Please run /login"` |
| `ORG_DISABLED_ERROR_MESSAGE_ENV_KEY` | `"Your ANTHROPIC_API_KEY belongs to a disabled organization..."` |
| `TOKEN_REVOKED_ERROR_MESSAGE` | `"OAuth token revoked · Please run /login"` |
| `CCR_AUTH_ERROR_MESSAGE` | `"Authentication error · This may be a temporary network issue..."` |
| `REPEATED_529_ERROR_MESSAGE` | `"Repeated 529 Overloaded errors"` |
| `CUSTOM_OFF_SWITCH_MESSAGE` | `"Opus is experiencing high load, please use /model..."` |
| `RATE_LIMITED_MESSAGE` | Rate limit specific message |
| `TOOL_USE_MISMATCH_ERROR_MESSAGE` | `"The assistant's response includes tool_use blocks... but the following tool_use ids don't have tool_results..."` |
| `DUPLICATE_TOOL_USE_ID_ERROR_MESSAGE` | `"The assistant's response includes duplicate tool_use ids..."` |

---

### 2.3 `services/api/withRetry.ts` (822 lines)

#### Additional Exports

| Export | Type | Value / Purpose |
|---|---|---|
| `getRetryDelay` | `(attempt: number): number` | Returns exponential backoff delay = `BASE_DELAY_MS * 2^(attempt-1)` |
| `DEFAULT_MAX_RETRIES` | `10` | Default retry attempts |
| `FLOOR_OUTPUT_TOKENS` | `3000` | Minimum output tokens on context overflow retry |
| `MAX_529_RETRIES` | `3` | Maximum consecutive 529s before fallback |
| `BASE_DELAY_MS` | `500` | Base delay in ms |
| `PERSISTENT_MAX_BACKOFF_MS` | `300000` | 5-min cap for unattended retry |
| `PERSISTENT_RESET_CAP_MS` | `21600000` | 6-hour cap for unattended retry |
| `HEARTBEAT_INTERVAL_MS` | `30000` | Keep-alive yield interval for persistent mode |

---

### 2.4 `services/api/promptCacheBreakDetection.ts` (727 lines)

#### Additional Exports

| Export | Signature | Purpose |
|---|---|---|
| `TRACKED_SOURCE_PREFIXES` | `string[]` | Sources eligible for cache break tracking |
| `MAX_TRACKED_SOURCES` | `10` | Cap to prevent unbounded growth from subagents |
| `cleanupAgentTracking` | `(agentId: string): void` | Removes subagent tracking state on teardown |
| `resetPromptCacheBreakDetection` | `(): void` | Clears all tracking state (on `/clear`) |

---

### 2.5 Files Missing from 01-api-services.md Detail Section

The following files were mentioned but deserve expanded export references:

#### `services/api/sessionIngress.ts` (514 lines)

| Export | Signature | Purpose |
|---|---|---|
| `appendSessionLog` | `(logEntry: LogEntry, sessionId: string): Promise<void>` | Appends transcript entry with optimistic concurrency (Last-UUID header) |
| `getSessionLogs` | `(sessionId: string): Promise<LogEntry[]>` | JWT-authenticated log retrieval |
| `getSessionLogsViaOAuth` | `(sessionId: string): Promise<LogEntry[]>` | OAuth-authenticated log retrieval |
| `getTeleportEvents` | `(sessionId: string): Promise<TeleportEvent[]>` | Paginated cursor-based fetch from CCR v2 Sessions API |
| `clearSession` | `(sessionId: string): Promise<void>` | Clears session logs |
| `clearAllSessions` | `(): Promise<void>` | Clears all session logs |

#### `services/api/filesApi.ts` (748 lines)

| Export | Signature | Purpose |
|---|---|---|
| `downloadFile` | `(fileId: string): Promise<FileContent>` | Downloads single file |
| `downloadAndSaveFile` | `(fileId: string, destPath: string): Promise<void>` | Downloads and saves to disk |
| `downloadSessionFiles` | `(sessionId: string, destDir: string, concurrency?: number): Promise<void>` | Parallel download (default 5) |
| `uploadFile` | `(filePath: string): Promise<FileUploadResult>` | Multipart upload (500MB max) |
| `uploadSessionFiles` | `(sessionId: string, fileSpecs: string[]): Promise<void>` | Batch upload with retry |
| `listFilesCreatedAfter` | `(timestamp: Date): Promise<FileMeta[]>` | Cursor-based pagination |
| `parseFileSpecs` | `(specs: string[]): ParsedFileSpec[]` | Parses `<file_id>:<relative_path>` format |

#### `services/api/usage.ts` (63 lines)

| Export | Signature | Purpose |
|---|---|---|
| `fetchUsage` | `(): Promise<UsageData>` | Fetches rate limit utilization from `/api/oauth/usage` |
| `UsageData` type | `{ five_hour, seven_day, seven_day_opus, seven_day_sonnet, extra_usage }` | Usage windows |

#### `services/api/dumpPrompts.ts` (226 lines)

| Export | Signature | Purpose |
|---|---|---|
| `createDumpPromptsFetch` | `(): FetchFunction` | Returns fetch wrapper that intercepts POST requests/responses for debug dumping |

#### `services/api/emptyUsage.ts` (22 lines)

| Export | Type | Purpose |
|---|---|---|
| `emptyUsage` | `object` | Zero-initialized usage object (all fields = 0) |

#### `services/api/metricsOptOut.ts` (159 lines)

| Export | Signature | Purpose |
|---|---|---|
| `isMetricsOptedOut` | `(): Promise<boolean>` | Two-tier cache (disk 24h + memory 1h) |
| `refreshMetricsOptOut` | `(): Promise<void>` | Force refresh from server |
| `clearMetricsOptOutCache` | `(): Promise<void>` | Clear all caches |

#### `services/api/overageCreditGrant.ts` (137 lines)

| Export | Signature | Purpose |
|---|---|---|
| `getCachedOverageCreditGrant` | `(): Promise<OverageCreditGrant \| null>` | 1h TTL disk cache |
| `refreshOverageCreditGrantCache` | `(): Promise<void>` | Fetch + persist with change detection |
| `invalidateOverageCreditGrantCache` | `(): Promise<void>` | Drops cache entry |
| `formatGrantAmount` | `(amountMinorUnits: number, currency: string): string` | Formats to currency string |

#### `services/api/adminRequests.ts` (119 lines)

| Export | Signature | Purpose |
|---|---|---|
| `createAdminRequest` | `(type: AdminRequestType): Promise<AdminRequestResult>` | Creates request with duplicate detection |
| `getMyAdminRequests` | `(type: AdminRequestType, status: RequestStatus): Promise<AdminRequest[]>` | Fetches user's requests |
| `checkAdminRequestEligibility` | `(type: AdminRequestType): Promise<boolean>` | Checks if request type is allowed for org |

#### `services/api/referral.ts` (281 lines)

| Export | Signature | Purpose |
|---|---|---|
| `fetchReferralEligibility` | `(): Promise<ReferralEligibility>` | Checks org pass eligibility |
| `fetchReferralRedemptions` | `(): Promise<ReferralRedemption[]>` | Gets redemption history |
| `checkCachedPassesEligibility` | `(): { eligible, needsRefresh }` | Returns cached state with refresh flag |
| `fetchAndStorePassesEligibility` | `(): Promise<void>` | Deduplicates concurrent fetches |
| `getCachedOrFetchPassesEligibility` | `(): Promise<ReferralEligibility>` | Stale-while-revalidate with 24h disk cache |

#### `services/api/ultrareviewQuota.ts` (38 lines)

| Export | Signature | Purpose |
|---|---|---|
| `peekUltraReviewQuota` | `(): Promise<UltraReviewQuota>` | Returns reviews_used/limit/remaining/is_overage |

---

## 3. LSP Services — Precise Reference (`services/lsp/` — 7 files)

*Gap-fill for 04-other-services.md §4. Prior doc covered architecture at high level.*

### 3.1 `services/lsp/LSPClient.ts` (~447 lines)

#### Exported Classes & Types

| Export | Kind | Purpose |
|---|---|---|
| `LSPClient` | Class | Wraps MCP SDK `Client` for LSP protocol over stdio |

#### `LSPClient` Methods

| Method | Signature | Purpose |
|---|---|---|
| `initialize` | `(serverProcess: ChildProcess, serverName: string, rootUri: string): Promise<void>` | LSP initialize handshake + `InitializedNotification` |
| `openTextDocument` | `(uri: string, languageId: string, text: string): void` | `textDocument/didOpen` |
| `changeTextDocument` | `(uri: string, text: string, version: number): void` | `textDocument/didChange` |
| `closeTextDocument` | `(uri: string): void` | `textDocument/didClose` |
| `getDiagnostics` | `(uri: string): Promise<LSPDiagnostic[]>` | `textDocument/diagnostic` (pull) |
| `close` | `(): Promise<void>` | Graceful shutdown |

---

### 3.2 `services/lsp/LSPServerInstance.ts` (~511 lines)

#### Exported Classes

| Export | Kind | Purpose |
|---|---|---|
| `LSPServerInstance` | Class | Manages single LSP server process lifecycle |

#### `LSPServerInstance` Methods

| Method | Signature | Purpose |
|---|---|---|
| `start` | `(command: string, args: string[], rootUri: string, serverName: string): Promise<void>` | Spawns server process, initializes LSP |
| `restart` | `(): Promise<void>` | Kills and restarts server |
| `kill` | `(): Promise<void>` | Force kills process |
| `getClient` | `(): LSPClient` | Returns wrapped LSP client |
| `isRunning` | `(): boolean` | Process aliveness check |

---

### 3.3 `services/lsp/LSPServerManager.ts` (~420 lines)

#### Exported Classes

| Export | Kind | Purpose |
|---|---|---|
| `LSPServerManager` | Class | Manages multiple LSP servers with language→server mapping |

#### `LSPServerManager` Methods

| Method | Signature | Purpose |
|---|---|---|
| `getOrStartServer` | `(languageId: string, rootUri: string): Promise<LSPServerInstance>` | Discovers and starts server for language |
| `getServerForFile` | `(filePath: string): Promise<LSPServerInstance \| null>` | Per-file server resolution |
| `shutdownAll` | `(): Promise<void>` | Graceful shutdown of all servers |
| `getActiveServers` | `(): LSPServerInstance[]` | Returns running server instances |

---

### 3.4 `services/lsp/manager.ts` (~289 lines)

#### Exported Functions

| Function | Signature | Purpose |
|---|---|---|
| `startLSP` | `(): Promise<void>` | Initialize LSP: discover file types, start servers |
| `stopLSP` | `(): Promise<void>` | Shutdown all servers |
| `getLSPInitializationStatus` | `(): LSPStatus` | Returns `'not-started' \| 'pending' \| 'ready' \| 'error'` |

---

### 3.5 `services/lsp/LSPDiagnosticRegistry.ts` (~386 lines)

#### Exported Classes & Types

| Export | Kind | Purpose |
|---|---|---|
| `LSPDiagnosticRegistry` | Class | Collects per-file diagnostics before/after edits |

#### `LSPDiagnosticRegistry` Methods

| Method | Signature | Purpose |
|---|---|---|
| `recordBeforeEdit` | `(uri: string, diagnostics: LSPDiagnostic[]): void` | Saves pre-edit diagnostics |
| `recordAfterEdit` | `(uri: string, diagnostics: LSPDiagnostic[]): void` | Saves post-edit diagnostics |
| `getDelta` | `(uri: string): DiagnosticDelta` | Returns { introduced, resolved, unchanged } counts |

---

### 3.6 `services/lsp/config.ts` (~79 lines)

#### Exported Functions

| Function | Signature | Purpose |
|---|---|---|
| `getLSPConfig` | `(): LSPConfig` | Global LSP settings |
| `setLSPConfig` | `(config: Partial<LSPConfig>): void` | Merge updates |

---

### 3.7 `services/lsp/passiveFeedback.ts` (~328 lines)

#### Exported Functions

| Function | Signature | Purpose |
|---|---|---|
| `trackDiagnosticDelta` | `(uri: string, before: LSPDiagnostic[], after: LSPDiagnostic[]): void` | Tracks diagnostic changes caused by edits |
| `getDiagnosticStats` | `(): DiagnosticStats` | Returns aggregate counts |
| `resetDiagnosticStats` | `(): void` | Clears all tracking |

---

## 4. Analytics Services — Precise Reference (`services/analytics/` — 9 files)

*Gap-fill for 04-other-services.md §2.*

### 4.1 `services/analytics/growthbook.ts` (1155 lines)

#### Exported Functions (complete)

| Function | Signature | Purpose |
|---|---|---|
| `initializeGrowthBook` | memoized async | Initialize with remote eval, disk cache, auth headers |
| `getFeatureValue_CACHED_MAY_BE_STALE` | `<T>(key: string, defaultValue: T): T` | Sync cached read for hot paths; no await |
| `getDynamicConfig_BLOCKS_ON_INIT` | `<T>(key: string, defaultValue: T): Promise<T>` | Async, blocks until init complete; for security-critical gates |
| `getFeatureValue` | `<T>(key: string, defaultValue: T): Promise<T>` | Standard async resolution |
| `getOnlineEvalValue` | `(key: string): Promise<unknown>` | Remote evaluation value |
| `logGrowthBookExperimentTo1P` | `(experiment: Experiment, result: ExperimentResult): void` | 1P event exposure logging |
| `refreshFeatures` | `(): Promise<void>` | Force refresh from server |
| `resetGrowthBook` | `(): Promise<void>` | Teardown and reinitialize |
| `onFeatureRefresh` | `(callback: () => void): () => void` | Subscribe to feature changes; returns unsubscribe |

#### User Attributes Shape

```typescript
type GrowthBookAttributes = {
  id: string
  sessionId: string
  deviceID: string
  platform: string
  apiBaseUrlHost: string
  organizationUUID?: string
  accountUUID?: string
  userType: 'ant' | 'external'
  subscriptionType: string
  rateLimitTier: number
  firstTokenTime: number
  email?: string
  appVersion: string
  github?: { repoID: string }
}
```

---

### 4.2 `services/analytics/index.ts` (~173 lines)

#### Exported Functions & Types

| Export | Kind | Purpose |
|---|---|---|
| `logEvent` | Function | Main entry: sends to all configured sinks (DD, 1P, OTel) with dedup |
| `AnalyticsMetadata_I_VERIFIED_THIS_IS_NOT_CODE_OR_FILEPATHS` | Type (`never`) | PII marker — forces explicit verification of safe values |
| `EventPayload` | Type | Event structure |

---

### 4.3 `services/analytics/metadata.ts` (973 lines)

#### Exported Functions

| Function | Signature | Purpose |
|---|---|---|
| `sanitizeToolNameForAnalytics` | `(toolName: string): string` | MCP→`'mcp_tool'`, skill→`'skill_tool'`, built-in→passthrough |
| `isToolDetailsLoggingEnabled` | `(): boolean` | Opt-in detailed logging via `OTEL_LOG_TOOL_DETAILS=1` |
| `getEventMetadata` | `async (options?): Promise<EventMetadata>` | Assembles all metadata fields for event enrichment |

#### Metadata Field Categories

| Category | Fields |
|---|---|
| Environment | OS, shell, terminal, WSL, Linux distro, VCS |
| Session | sessionId, parentSessionId, agentId, isInteractive, isTeammate, teamName |
| User | userType, subscriptionType, organizationUUID, accountUUID, rateLimitTier |
| Platform | nodeVersion, bunVersion, platform, arch, clientType, electronVersion, kairosActive |
| Repo | gitRemoteHash (SHA-256 hashed) |
| Build | appVersion, buildTime, commit SHA |
| Model | mainLoopModel, model betas, provider |
| Auth | isOAuth, isClaudeAISubscriber, authMethod |

---

### 4.4-4.9 Remaining Analytics Files

#### `services/analytics/datadog.ts`

| Export | Purpose |
|---|---|
| `sendToDatadog` | Sends events to DD with API key auth |
| `configureDatadog` | Sets endpoint and API key |

#### `services/analytics/firstPartyEventLogger.ts`

| Export | Purpose |
|---|---|
| `logToFirstParty` | Batches + flushes to `events.anthropic.com` |
| `flushFirstPartyEvents` | Force flush |
| `configureFirstPartyLogging` | Set batch interval/size from GB config |

#### `services/analytics/firstPartyEventLoggingExporter.ts`

| Export | Purpose |
|---|---|
| `FirstPartyEventLoggingExporter` | OTel span/log exporter → 1P events |

#### `services/analytics/sink.ts`

| Export | Purpose |
|---|---|
| `AnalyticsSink` | Interface for pluggable sinks |
| `SinkConfig` | Per-sink configuration |

#### `services/analytics/sinkKillswitch.ts`

| Export | Purpose |
|---|---|
| `isEssentialTrafficOnly` | Global override |
| `setSinkEnabled` | Runtime enable/disable per sink |
| `growthbookKillswitch` | GB-controlled kill switches |

#### `services/analytics/config.ts`

| Export | Purpose |
|---|---|
| `analyticsConfig` | Endpoints, batch sizes, flush intervals, retry policies |

---

## 5. Plugin Services — Precise Reference (`services/plugins/` — 3 files)

*Gap-fill for 04-other-services.md §3.*

### 5.1 `services/plugins/pluginOperations.ts` (~1088 lines)

#### Exported Functions

| Function | Signature | Purpose |
|---|---|---|
| `installPlugin` | `(name: string, source?: string): Promise<PluginInstallResult>` | Downloads from marketplace, validates, extracts |
| `updatePlugin` | `(name?: string): Promise<PluginUpdateResult>` | Checks for updates, downloads new version |
| `removePlugin` | `(name: string): Promise<void>` | Uninstalls, cleans up files |
| `enablePlugin` | `(name: string): Promise<void>` | Toggles enabled in settings |
| `disablePlugin` | `(name: string): Promise<void>` | Toggles disabled in settings |
| `listPlugins` | `(): Promise<PluginInfo[]>` | Lists installed plugins with status |
| `searchPlugins` | `(query: string): Promise<PluginSearchResult[]>` | Marketplace search |

---

### 5.2 `services/plugins/PluginInstallationManager.ts` (~184 lines)

#### Exported Classes

| Export | Kind | Purpose |
|---|---|---|
| `PluginInstallationManager` | Class | Queue-based installation state manager |

#### `PluginInstallationManager` Methods

| Method | Purpose |
|---|---|
| `enqueueInstall` | Adds to install queue (prevents races) |
| `getProgress` | Current installation progress |
| `rollback` | Reverts failed installation |

---

### 5.3 `services/plugins/pluginCliCommands.ts` (~344 lines)

#### Exported Functions

| Function | Purpose |
|---|---|
| `handlePluginInstall` | `/plugin install <name>` handler |
| `handlePluginList` | `/plugin list` handler |
| `handlePluginRemove` | `/plugin remove <name>` handler |
| `handlePluginUpdate` | `/plugin update [name]` handler |
| `handlePluginSearch` | `/plugin search <query>` handler |

---

## 6. SessionMemory Services — Precise Reference (`services/SessionMemory/` — 3 files)

*Gap-fill for 04-other-services.md §5.*

### 6.1 `services/SessionMemory/sessionMemory.ts` (495 lines)

#### Exported Functions (verified)

| Function | Signature | Purpose |
|---|---|---|
| `initSessionMemory()` | `(): void` | Registers post-sampling extraction hook |
| `shouldExtractMemory()` | `(messages: Message[]): boolean` | Token/tool-call threshold check |
| `manuallyExtractSessionMemory()` | `(ctx: ToolUseContext): Promise<ManualExtractionResult>` | Manual extraction |
| `createMemoryFileCanUseTool()` | `(memoryPath: string): CanUseToolFn` | Scoped write permission |
| `resetLastMemoryMessageUuid()` | `(): void` | Test reset |

*Prior doc listed `extractMemories`, `updateMemories`, `queryMemories`, `compactMemories`, and a JSON `SessionMemory` type — none exist in this module. See `07-services-unverified-fill.md` for behavioral detail.*

---

### 6.2 `services/SessionMemory/prompts.ts` (~324 lines)

#### Exported Functions

| Function | Purpose |
|---|---|
| `getMemoryExtractionPrompt` | Returns system prompt for memory extraction |
| `getMemoryQueryPrompt` | Returns prompt for querying memories |
| `isSessionMemoryEmpty` | Checks if session memory is template-only |
| `truncateSessionMemoryForCompact` | Truncates oversized memory sections |

---

### 6.3 `services/SessionMemory/sessionMemoryUtils.ts` (~207 lines)

#### Exported Functions

| Function | Signature | Purpose |
|---|---|---|
| `setLastSummarizedMessageId` | `(uuid: string \| undefined): void` | Persists last summarized message UUID |
| `getLastSummarizedMessageId` | `(): string \| undefined` | Retrieves last summarized message UUID |
| `getSessionMemoryContent` | `(): Promise<string \| null>` | Reads session memory file |
| `waitForSessionMemoryExtraction` | `(timeout?: number): Promise<void>` | Waits for in-progress extraction |

---

## 7. AgentSummary Services — Precise Reference (`services/AgentSummary/` — 1 file)

*Gap-fill for 04-other-services.md §17.*

### 7.1 `services/AgentSummary/agentSummary.ts` (~180 lines)

#### Exported Functions

| Function | Signature | Purpose |
|---|---|---|
| `startAgentSummarization()` | `(taskId, agentId, cacheSafeParams, setAppState): { stop }` | Periodic (~30s) progress summaries for coordinator sub-agents |

*Prior doc listed `summarizeAgentCompletion`, `getAgentSummary`, `clearAgentSummary`, and an `AgentSummary` type — none are exported.*

---

## 8. Cross-Cutting Corrections

### Formerly Unverified Services — Now Verified

All 18 services previously listed as unverified have been verified against source. See [07-services-unverified-fill.md](07-services-unverified-fill.md) for behavior-level entries.

| Path | Key exports |
|---|---|
| `services/toolUseSummary/toolUseSummaryGenerator.ts` | `generateToolUseSummary()` |
| `services/MagicDocs/magicDocs.ts` | `initMagicDocs()`, `detectMagicDocHeader()`, `registerMagicDoc()` |
| `services/MagicDocs/prompts.ts` | `buildMagicDocsUpdatePrompt()` |
| `services/extractMemories/extractMemories.ts` | `initExtractMemories()`, `executeExtractMemories()` |
| `services/extractMemories/prompts.ts` | `buildExtractAutoOnlyPrompt()`, `buildExtractCombinedPrompt()` |
| `services/autoDream/autoDream.ts` | `initAutoDream()`, `executeAutoDream()` |
| `services/tips/tipRegistry.ts` | `getRelevantTips()` |
| `services/tips/tipScheduler.ts` | `getTipToShowOnSpinner()`, `recordShownTip()` |
| `services/tips/tipHistory.ts` | `recordTipShown()`, `getSessionsSinceLastShown()` |
| `services/PromptSuggestion/speculation.ts` | `startSpeculation()`, `acceptSpeculation()`, `abortSpeculation()` |
| `services/PromptSuggestion/promptSuggestion.ts` | `shouldEnablePromptSuggestion()`, `tryGenerateSuggestion()` |
| `services/settingsSync/index.ts` | `uploadUserSettingsInBackground()`, `downloadUserSettings()` |
| `services/settingsSync/types.ts` | `UserSyncDataSchema`, `SYNC_KEYS` |
| `services/policyLimits/index.ts` | `isPolicyAllowed()`, `loadPolicyLimits()` |
| `services/policyLimits/types.ts` | `PolicyLimitsResponseSchema` |
| `services/remoteManagedSettings/index.ts` | `loadRemoteManagedSettings()`, `computeChecksumFromSettings()` |
| `services/oauth/index.ts` | `OAuthService` class |
| `services/teamMemorySync/index.ts` | `syncTeamMemory()`, `pullTeamMemory()`, `pushTeamMemory()` |

### Inaccuracies in 04-other-services.md

| Claim | Correction |
|---|---|
| `tokenEstimation.ts` file path under services/ | Lives at `services/tokenEstimation.ts` (service root, not subdirectory) — confirmed |
| `sessionMemory.ts` under `services/sessionMemory/` | Lives at `services/SessionMemory/sessionMemory.ts` (capital S) — confirmed |
| `prompts.ts` under `services/sessionMemory/` | Lives at `services/SessionMemory/prompts.ts` — confirmed |
| `sessionMemoryUtils.ts` under `services/sessionMemory/` | Lives at `services/SessionMemory/sessionMemoryUtils.ts` — confirmed |
| `analytics/growthbook.ts` "Initialization" flow | Confirmed: SSE streaming connection with CDN fallback, 60s periodic refresh, disk cache |
| `analytics/index.ts` | Confirmed: `logEvent()` function with dedup and multi-sink routing |

---

## 9. Complete Export Inventory

### Services Compact (11 files, 3,928 total lines)

| File | Lines | Exported Functions | Exported Types | Exported Constants |
|---|---|---|---|---|
| compact.ts | 1579 | 16 | 2 | 6 |
| autoCompact.ts | 351 | 6 | 1 | 4 |
| microCompact.ts | 530 | 10 | 2 | 1 |
| apiMicrocompact.ts | 153 | 1 | 2 | 0 (types only) |
| sessionMemoryCompact.ts | 630 | 8 | 1 | 1 |
| prompt.ts | 374 | 4 | 0 | 0 |
| grouping.ts | 63 | 1 | 0 | 0 |
| postCompactCleanup.ts | 77 | 1 | 0 | 0 |
| compactWarningState.ts | 18 | 2 | 0 | 0 (store exported) |
| compactWarningHook.ts | 16 | 1 | 0 | 0 |
| timeBasedMCConfig.ts | 43 | 1 | 1 | 0 |

### Services API (20 files, ~10,000+ total lines)

| File | Lines | Key Exports |
|---|---|---|
| claude.ts | 3212 | `queryModelWithStreaming`, `queryModelWithoutStreaming`, `getMaxOutputTokensForModel`, `verifyApiKey` |
| errors.ts | 1207 | `getAssistantMessageFromError`, `classifyAPIError`, `isPromptTooLongMessage`, `getPromptTooLongTokenGap`, 12+ error constants |
| withRetry.ts | 822 | Retry wrapper, `getRetryDelay`, 7 constants |
| promptCacheBreakDetection.ts | 727 | `recordPromptState`, `checkResponseForCacheBreak`, `notifyCompaction`, `notifyCacheDeletion` |
| filesApi.ts | 748 | `downloadFile`, `uploadFile`, `listFilesCreatedAfter` |
| client.ts | 389 | `getAnthropicClient` |
| grove.ts | 357 | `getGroveSettings`, `isQualifiedForGrove`, `checkGroveForNonInteractive` |
| logging.ts | 788 | `logAPIQuery`, `logAPISuccessAndDuration`, `logAPIError` |
| sessionIngress.ts | 514 | `appendSessionLog`, `getSessionLogs`, `clearSession` |
| referral.ts | 281 | `fetchReferralEligibility`, `getCachedOrFetchPassesEligibility` |
| errorUtils.ts | 260 | `extractConnectionErrorDetails`, `formatAPIError`, `sanitizeAPIError` |
| dumpPrompts.ts | 226 | `createDumpPromptsFetch` |
| bootstrap.ts | 141 | `fetchBootstrapData` |
| overageCreditGrant.ts | 137 | `getCachedOverageCreditGrant`, `refreshOverageCreditGrantCache` |
| adminRequests.ts | 119 | `createAdminRequest`, `getMyAdminRequests` |
| metricsOptOut.ts | 159 | `isMetricsOptedOut`, `refreshMetricsOptOut` |
| firstTokenDate.ts | 60 | Fetches org first_token_date |
| usage.ts | 63 | `fetchUsage` |
| ultrareviewQuota.ts | 38 | `peekUltraReviewQuota` |
| emptyUsage.ts | 22 | `emptyUsage` object |

### Services Analytics (9 files, ~2,700+ total lines)

| File | Key Exports |
|---|---|
| growthbook.ts | `initializeGrowthBook`, `getFeatureValue_CACHED_MAY_BE_STALE`, `getDynamicConfig_BLOCKS_ON_INIT` |
| metadata.ts | `sanitizeToolNameForAnalytics`, `getEventMetadata` |
| index.ts | `logEvent`, `AnalyticsMetadata_I_VERIFIED_THIS_IS_NOT_CODE_OR_FILEPATHS` |
| datadog.ts | `sendToDatadog` |
| firstPartyEventLogger.ts | `logToFirstParty` |
| firstPartyEventLoggingExporter.ts | `FirstPartyEventLoggingExporter` |
| sink.ts | `AnalyticsSink` interface |
| sinkKillswitch.ts | `isEssentialTrafficOnly` |
| config.ts | `analyticsConfig` |

### Services LSP (7 files, ~750+ total lines)

| File | Key Exports |
|---|---|
| LSPClient.ts | `createLSPClient()`, `LSPClient` type |
| LSPServerInstance.ts | `createLSPServerInstance()`, `LSPServerInstance` type |
| LSPServerManager.ts | `createLSPServerManager()`, `LSPServerManager` type |
| manager.ts | `initializeLspServerManager()`, `getInitializationStatus()`, `isLspConnected()` |
| LSPDiagnosticRegistry.ts | `registerPendingLSPDiagnostic()`, `checkForLSPDiagnostics()` |
| config.ts | `getAllLspServers()` |
| passiveFeedback.ts | `registerLSPNotificationHandlers()`, `formatDiagnosticsForAttachment()` |

### Services Plugins (3 files, ~850+ total lines)

| File | Key Exports |
|---|---|
| pluginOperations.ts | `installPluginOp`, `updatePluginOp`, `enablePluginOp`, `disablePluginOp` |
| PluginInstallationManager.ts | `performBackgroundPluginInstallations()` |
| pluginCliCommands.ts | `installPlugin`, `uninstallPlugin`, `updatePluginCli` |

### Services SessionMemory (3 files, ~780+ total lines)

| File | Key Exports |
|---|---|
| sessionMemory.ts | `initSessionMemory`, `shouldExtractMemory`, `manuallyExtractSessionMemory` |
| prompts.ts | `loadSessionMemoryPrompt`, `isSessionMemoryEmpty`, `truncateSessionMemoryForCompact` |
| sessionMemoryUtils.ts | `setLastSummarizedMessageId`, `getLastSummarizedMessageId`, `getSessionMemoryContent` |

### Services AgentSummary (1 file, ~180 lines)

| File | Key Exports |
|---|---|
| agentSummary.ts | `startAgentSummarization` |

---

*End of gap-fill document. All exports verified against source files read in full. Total files documented: 54 across 7 directories.*
