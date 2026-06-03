# Phase 2 Cross-Cutting Audit — X2 Query Loop

**Date:** 2026-05-23  
**Chain:** `QueryEngine.submitMessage` → `query()` / `queryLoop()` → `deps.callModel` (= `queryModelWithStreaming` → `queryModel`) → tool dispatch → compaction  
**Docs audited:** `docs/source-code-analysis/core-engine/01-query-engine.md`, `docs/source-code-analysis/services-layer/01-api-services.md`  
**Method:** Traced full call chain in source; cross-checked focus areas against documentation.

---

## Summary

| Focus area | Doc status before audit | Action |
|------------|-------------------------|--------|
| `needsFollowUp` vs stop hooks order | **Incorrect** — abort/summary nested under `!needsFollowUp`; message flow showed linear stop-hooks-before-tools | **Patched** |
| `isResultSuccessful` | **Accurate** | No change |
| Token budget (`TOKEN_BUDGET` vs `task_budget`) | **Partially wrong** — implied fixed 500k; omitted stop-hook ordering and REPL bootstrap | **Patched** |
| Compaction triggers | **Incomplete** — pipeline order correct but missing reactive/blocking/suppression matrix | **Patched** |
| API services ↔ query loop | **Missing** — no cross-cutting integration section | **Added** |

---

## Verified Call Chain

```
QueryEngine.submitMessage()          [QueryEngine.ts:209+]
  └─ for await (query(...))          [QueryEngine.ts:675+]
       └─ query()                    [query.ts:219]
            └─ queryLoop()           [query.ts:244, while(true)]
                 ├─ Context pipeline [query.ts:365-543]
                 ├─ deps.callModel() [query.ts:659]
                 │    └─ queryModelWithStreaming → queryModel [query/deps.ts:35, claude.ts:752+]
                 ├─ Post-stream      [query.ts:999+]
                 ├─ if !needsFollowUp [query.ts:1062]
                 │    ├─ recovery (413 / media / max_output_tokens)
                 │    ├─ handleStopHooks() [query.ts:1267]
                 │    └─ checkTokenBudget() [query.ts:1308]
                 └─ else (needsFollowUp)
                      └─ runTools / StreamingToolExecutor [query.ts:1380+]
QueryEngine result                   [QueryEngine.ts:1058+]
  └─ isResultSuccessful(result, lastStopReason) [utils/queryHelpers.ts:56]
```

---

## Focus Area Findings

### 1. `needsFollowUp` vs stop hooks order

**Source truth (`query.ts`):**

- `needsFollowUp` is set when streaming yields assistant content with `tool_use` blocks (`:834`), not from `stop_reason`.
- **Pre-branch steps** (lines 999–1060): post-sampling hooks, abort handling, prior-turn tool-use summary — run for **all** completions before the branch.
- **`!needsFollowUp` path only:** collapse drain → reactive compact → max-output-tokens recovery → API-error bail → **`handleStopHooks()`** → **`checkTokenBudget()`** → return `completed`.
- **`needsFollowUp` path:** tool dispatch → attachments → next turn; **stop hooks are skipped** until a later iteration completes without tool calls.

**Doc errors fixed:**

- Section 6 incorrectly listed abort check and tool-use summary under the `!needsFollowUp` branch.
- Message Flow diagram implied stop hooks and token budget always precede tool execution (linear flow). Actual behavior is a **branch**, not a sequence.

### 2. `isResultSuccessful`

**Verified accurate** in `01-query-engine.md` Phase 5 (`QueryEngine.ts:1058-1118` ↔ `utils/queryHelpers.ts:56-94`):

| Condition | Result |
|-----------|--------|
| `undefined` message | false |
| Assistant, last block `text` / `thinking` / `redacted_thinking` | true (ignores `stop_reason`) |
| User, all blocks `tool_result` | true |
| `stopReason === 'end_turn'` with no passing content (task_notification drain) | true |
| Otherwise | false |

`QueryEngine` uses `messages.findLast(m => m.type === 'assistant' \|\| m.type === 'user')` to skip stop-hook progress/attachment messages pushed inline (#23537).

### 3. Token budget

**Two distinct mechanisms (previously conflated in docs):**

| | `TOKEN_BUDGET` feature | API `task_budget` |
|--|------------------------|-------------------|
| **Config** | User prompt (`+500k`, `use 2M tokens`) via `parseTokenBudget()` | `QueryParams.taskBudget.total` |
| **Wire** | Client meta nudge message | `configureTaskBudgetParams()` → `output_config.task_budget` |
| **Baseline** | `snapshotOutputTokensForTurn()` in REPL (`bootstrap/state.ts:733`) | Server counts until compact; `remaining` updated in `queryLoop` on compact |
| **When checked** | After stop hooks, `!needsFollowUp` only | Passed on every `deps.callModel()` call |

**`checkTokenBudget()` logic** (`query/tokenBudget.ts`) — verified accurate:

- Skips subagents (`agentId` set) and null/zero budget.
- Continues while `turnTokens < budget × 0.9` and not diminishing.
- Diminishing: `continuationCount >= 3` and last two deltas `< 500` tokens.
- Uses `getTurnOutputTokens()` (= session output delta since turn snapshot), not input tokens.

### 4. Compaction triggers

**Pre-API (each loop iteration):**

1. Compact boundary strip  
2. Tool result budget  
3. Snip (`HISTORY_SNIP`)  
4. Microcompact (deferred boundary if `CACHED_MICROCOMPACT`)  
5. Context collapse projection (`CONTEXT_COLLAPSE`)  
6. Proactive autocompact (`autoCompactIfNeeded`) — unless suppressed by reactive-only raccoon gate or context-collapse ownership  
7. Blocking-limit preempt — synthetic PTL when at hard limit and recovery paths disabled  

**Post-stream (`!needsFollowUp` only):**

1. Collapse drain on withheld 413  
2. Reactive compact on withheld 413 / media errors  
3. `taskBudgetRemaining` decremented on both proactive and reactive compact  

**Circuit breaker:** `MAX_CONSECUTIVE_AUTOCOMPACT_FAILURES = 3` in `autoCompact.ts`.

---

## Files Edited

| File | Changes |
|------|---------|
| `docs/source-code-analysis/core-engine/01-query-engine.md` | Restructured §6 post-stream pipeline; added compaction trigger table; fixed Message Flow diagram; clarified token budget vs `task_budget`; fixed feature-gate description |
| `docs/source-code-analysis/services-layer/01-api-services.md` | Added "Query Loop Integration" cross-cutting section |

## Source Files Verified (no code changes)

- `QueryEngine.ts` — `submitMessage`, result generation, `isResultSuccessful` usage  
- `query.ts` — full `queryLoop`, `needsFollowUp`, compaction, stop hooks, token budget  
- `query/deps.ts`, `query/stopHooks.ts`, `query/tokenBudget.ts`  
- `utils/queryHelpers.ts` — `isResultSuccessful`  
- `services/api/claude.ts` — `queryModel`, `queryModelWithStreaming`, `configureTaskBudgetParams`  
- `services/compact/autoCompact.ts` — proactive triggers and suppression  
- `bootstrap/state.ts` — turn output token snapshot helpers  
