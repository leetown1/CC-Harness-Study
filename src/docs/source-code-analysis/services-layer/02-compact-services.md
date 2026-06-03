# Services Layer Analysis — File 2: Compact Services

> **Scope**: All files in `services/compact/` (11 files)
> **Purpose**: Context window management — compacts conversation history to stay within model token limits while preserving conversational state.

---

## 1. Core Compaction Engine

### 1.1 `services/compact/compact.ts` (1579 lines)

**The primary compaction engine.** Exports `compactConversation()` and `partialCompactConversation()` — there is no top-level `compact()` export.

#### Architecture

```
compactConversation()
├── Validation + hook custom instructions merge
├── groupMessagesByApiRound() (assistant message.id boundaries)
├── streamCompactSummary()
│   ├── Cache-sharing fork via runForkedAgent() (tengu_compact_cache_prefix)
│   └── Direct streaming fallback with retry (MAX_COMPACT_STREAMING_RETRIES = 2)
├── buildPostCompactMessages()
├── createPostCompactFileAttachments() / plan/skill/async-agent attachments
└── Returns CompactionResult (boundary, summaries, attachments, hookResults)

partialCompactConversation()
└── Compacts around a pivot index ('from' or 'up_to' direction)

truncateHeadForPTLRetry()
└── Reactive PTL: drops oldest API-round groups using getPromptTooLongTokenGap()
```

#### Key Exports

| Function | Purpose |
|---|---|
| `compactConversation()` | Main full-compact entry |
| `partialCompactConversation()` | Partial compact around a selected message index |
| `truncateHeadForPTLRetry()` | Reactive prompt-too-long head truncation |
| `buildPostCompactMessages()` | Assembles post-compact message array |
| `getCompactPrompt()` / `getPartialCompactPrompt()` | Prompt templates (in `prompt.ts`) |
| `groupMessagesByApiRound()` | Groups by assistant `message.id` (in `grouping.ts`) |

Summary output uses `<analysis>` / `<summary>` XML tags — not JSON. Parsing is inline via `formatCompactSummary()`.

---

### 1.2 `services/compact/autoCompact.ts` (351 lines)

**Automatic compaction trigger logic.** Monitors token usage and triggers compaction before hitting limits.

#### Trigger Algorithm

```
autoCompact()
├── 1. TOKEN ESTIMATION
│   ├── roughTokenCountEstimationForMessages()     [Fast char/4 estimate]
│   ├── countTokensViaHaikuFallback()               [Accurate API count]
│   └── Compare against model context window
├── 2. THRESHOLD CHECK
│   ├── Warning threshold (e.g., 80% of context window)
│   ├── Critical threshold (e.g., 95% of context window)
│   └── Input_pct + output budget > context window
├── 3. CIRCUIT BREAKER
│   ├── Minimum time between auto-compacts
│   ├── Maximum auto-compacts per session
│   └── Debounce: don't compact during active tool use
├── 4. DECISION
│   ├── Should compact? → start compaction
│   ├── Should warn? → show warning to user
│   └── Should block? → refuse new messages until compacted
└── 5. EXECUTION
    ├── Call compact() with auto-compact flags
    ├── Handle compact failure gracefully
    └── Update compaction state
```

#### Thresholds

Computed by `calculateTokenWarningState()` from effective context window minus buffer tokens:

| Constant | Value | Role |
|---|---|---|
| `AUTOCOMPACT_BUFFER_TOKENS` | 13,000 | Auto-compact fires at `effectiveWindow - 13K` |
| `WARNING_THRESHOLD_BUFFER_TOKENS` | 20,000 | Warning banner threshold |
| `ERROR_THRESHOLD_BUFFER_TOKENS` | 20,000 | Error-level threshold |
| `MANUAL_COMPACT_BUFFER_TOKENS` | 3,000 | Manual `/compact` buffer |

Effective window = model context window − min(max_output_tokens, 20K). Override via `CLAUDE_AUTOCOMPACT_PCT_OVERRIDE` or `CLAUDE_CODE_AUTO_COMPACT_WINDOW`.

#### Circuit Breaker

`MAX_CONSECUTIVE_AUTOCOMPACT_FAILURES = 3`. After three consecutive failures, `autoCompactIfNeeded()` stops retrying (prevents runaway API usage on irrecoverable PTL). Session-memory compact is attempted first when enabled, then legacy `compactConversation()`.

---

### 1.3 `services/compact/microCompact.ts` (530 lines)

**Client-side micro-compaction** — reduces token usage without API calls by manipulating message content directly.

#### Cached Microcompact

Uses the API's cache_edits feature to remove old content from the server-side cache:
- Identifies stale cache blocks (old message content already summarized)
- Sends `cache_edits` deletions to remove them from the prompt cache
- Coordinates with `promptCacheBreakDetection.ts` via `notifyCacheDeletion()`
- Preserves tool_use/tool_result pairing integrity

#### Time-Based Microcompact

Removes/reduces content based on message age:
- Messages older than threshold get summarized locally
- Tool results older than threshold get truncated
- Recent messages (last N turns) always preserved
- File attachments get special treatment (keep reference, reduce content)

#### Key Operations

| Function | Purpose |
|---|---|
| `microcompactMessages()` | Entry: time-based MC → cached MC → unchanged |
| `consumePendingCacheEdits()` | Returns pending `cache_edits` block for API layer |
| `pinCacheEdits()` | Pins cache edits to a user message index |
| `getPinnedCacheEdits()` | Re-sends pinned edits on cache hits |
| `markToolsSentToAPIState()` | Marks registered tools as sent to API |
| `resetMicrocompactState()` | Clears all cached MC state |
| `evaluateTimeBasedTrigger()` | Time-gap check for time-based microcompact |

---

### 1.4 `services/compact/apiMicrocompact.ts` (153 lines)

**API-native context management (apiMicrocompact).** Uses the context_management beta header to let the server manage context window overflow.

#### When Activated

- Ant-only feature (gated by `feature('CACHED_MICROCOMPACT')`)
- Uses `context_management` beta with `clear_tool_uses_20250919` / `clear_thinking_20251015` strategies
- Configured via `getAPIContextManagement()` in `apiMicrocompact.ts`

#### How It Works

Instead of client-side compaction, sends `context_management` instructions to the API:
- The API server handles token budget internally
- Can automatically drop/compress old context
- Client provides preferences (keep recent N messages, preserve tool results, etc.)

#### Functions

- `getAPIContextManagement()` — builds context_management config for API request
- `isApiMicrocompactEnabled()` — checks if feature is active for current user/model
- `getApiMicrocompactConfig()` — reads GrowthBook configuration

---

### 1.5 `services/compact/sessionMemoryCompact.ts` (630 lines)

**Session-memory-based compaction.** Uses Claude's memory of the conversation (extracted as structured notes) to perform smarter, context-aware compaction.

#### Architecture

Uses the session-memory markdown file and `lastSummarizedMessageId` to choose a split point, then runs the standard compact pipeline on the prefix:

1. `shouldUseSessionMemoryCompaction()` — gates on `tengu_session_memory` + `tengu_sm_compact`
2. `calculateMessagesToKeepIndex()` — expands kept tail to meet min token/text-block counts
3. `adjustIndexToPreserveAPIInvariants()` — keeps tool_use/tool_result and thinking pairs intact
4. `trySessionMemoryCompaction()` — main entry; returns `CompactionResult | null`

#### Functions

- `trySessionMemoryCompaction()` — orchestrates memory-guided compaction
- `calculateMessagesToKeepIndex()` — computes keep/start index from memory state
- `adjustIndexToPreserveAPIInvariants()` — preserves API invariants at split boundary
- `setSessionMemoryCompactConfig()` / `getSessionMemoryCompactConfig()` — test/config overrides

---

### 1.6 `services/compact/prompt.ts` (374 lines)

**Compact prompt templates.** Contains the system and user prompts sent to the API for summarization.

#### Prompt Structure

- **System instructions**: Detailed instructions for how to summarize, what to keep, output format
- **Output schema**: JSON-structured output with sections (summary, key decisions, files modified, pending tasks, etc.)
- **Context markers**: Special tokens to delineate parts of the conversation
- **Model-specific variants**: Different prompts for different model capabilities (thinking, long context)

#### Prompt Sections

1. **Role assignment**: "You are a conversation summarizer..."
2. **Format specification**: Required JSON fields and their semantics
3. **Content guidelines**: What to preserve (decisions, errors, file paths, tool outputs)
4. **Length constraints**: Token budgets for the summary
5. **Tool result handling**: How to summarize bash output, file edits, etc.

---

### 1.7 `services/compact/grouping.ts` (63 lines)

**Message grouping by API round.** Groups the flat message array into logical "rounds" where each round is a user message + the assistant's response(s).

#### Algorithm

- Iterates through messages in order
- Starts a new group when encountering a user message
- Includes all subsequent assistant and tool messages until the next user message
- Handles edge cases: consecutive user messages, system messages interspersed

---

### 1.8 `services/compact/postCompactCleanup.ts` (77 lines)

**Cache clearing after compaction.** Post-compaction cleanup ensures the prompt cache state is consistent:

- Resets cache read baseline (compaction legitimately changes the prompt)
- Calls `notifyCompaction()` on cache break detection
- Clears cached microcompact state
- Updates compaction counter
- Resets auto-compact circuit breaker timers

---

### 1.9 `services/compact/timeBasedMCConfig.ts` (43 lines)

**GrowthBook configuration for time-based microcompact.** Defines the config schema:

```typescript
type TimeBasedMCConfig = {
  enabled: boolean              // Default: false
  gapThresholdMinutes: number   // Default: 60
  keepRecent: number            // Default: 5
}
```

Reads from GrowthBook `tengu_slate_heron` via `getTimeBasedMCConfig()`.

---

### 1.10 `services/compact/compactWarningHook.ts` (16 lines)

**Warning suppression hook.** React hook that exposes `suppressCompactWarnings: boolean` state. When true, the UI hides auto-compact warning messages (set after user acknowledges a warning, reset on next warning condition).

---

### 1.11 `services/compact/compactWarningState.ts` (18 lines)

**React-free boolean store for compact warning visibility:**
- `compactWarningStore: Store<boolean>` — `false` = show warning
- `suppressCompactWarning()` / `clearCompactWarningSuppression()` — toggle suppression
- `useCompactWarningSuppression()` hook in `compactWarningHook.ts` subscribes via `useSyncExternalStore`

---

## 2. Compaction Lifecycle

### Full Compaction Flow

```
Trigger: /compact command OR auto-compact threshold
    │
    ▼
[Validate prerequisites]
    ├── Conversation has enough messages?
    ├── Not already compacting?
    └── Token budget allows?
    │
    ▼
[Group messages into rounds]
    └── grouping.ts: groupByAPIRound()
    │
    ▼
[Select messages to preserve]
    ├── Last 2-3 rounds (recent context)
    ├── Pinned user messages
    └── Critical system messages
    │
    ▼
[Select messages to summarize]
    └── Everything older than preservation window
    │
    ▼
[Build compact prompt]
    └── prompt.ts templates + selected messages
    │
    ▼
[Send compact API call]
    ├── Non-streaming (queryModelWithoutStreaming)
    ├── Dedicated compact querySource
    └── Lower temperature for structured output
    │
    ▼
[Parse compact response]
    ├── Extract summary JSON
    ├── Extract file references
    ├── Extract pending TODOs
    └── Extract key decisions
    │
    ▼
[Rebuild conversation]
    ├── Insert compact summary as system message
    ├── Reattach preserved messages after summary
    ├── Restore file attachment references
    └── Rebuild tool_use/tool_result pairs
    │
    ▼
[Post-compact cleanup]
    ├── Clear cache break detection baseline
    ├── Clear microcompact cached state
    ├── Update compaction metadata
    └── Emit analyticEvent
```

### Reactive Compaction (Prompt-Too-Long)

```
API returns 400/413 "Prompt is too long"
    │
    ▼
[parsePromptTooLongTokenCounts()]
    ├── Extract actual tokens vs. limit
    └── Compute gap (how many tokens over)
    │
    ▼
[partialCompact() with token gap]
    ├── Jump past N oldest groups
    ├── Rebuild messages without them
    └── Retry API call with smaller context
    │
    ▼
[If still too long]
    └── Another partial compaction → retry
```

### Micro-Compaction (Per-Request)

```
Before each API call:
    │
    ▼
[Cached microcompact]
    ├── consumePendingCacheEdits()  → apply deletions
    ├── pinCacheEdits()             → mark stale blocks
    └── insertCacheEditsBlock()     → send cache_edits to API
    
[Time-based microcompact]
    ├── Truncate old tool results
    └── Summarize old user messages
```

---

## 3. Token Budget Management

The compact system manages token budgets at multiple levels:

| Level | Mechanism | When |
|---|---|---|
| API call budget | max_tokens | Every API call |
| Context window budget | autoCompact.ts thresholds | Before API calls |
| Prompt cache budget | microCompact.ts cache_edits | Before API calls |
| Summary budget | prompt.ts length constraints | During compaction |
| Session budget | sessionMemoryCompact.ts | Persisted across compact |

### Budget Priority

When token budget is tight:
1. **First**: Time-based microcompact (old tool results + messages)
2. **Second**: Cached microcompact (cache_edits deletions)
3. **Third**: API-native context management (server-side)
4. **Fourth**: Auto-compact warning
5. **Fifth**: Auto-compact
6. **Last resort**: Prompt-too-long → reactive partial compact
