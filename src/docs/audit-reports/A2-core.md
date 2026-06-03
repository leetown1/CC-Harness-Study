# Phase 1 Audit — A2 Core Engine

**Scope:** `QueryEngine.ts`, `query.ts`, `query/`, `Task.ts`, `tasks.ts`, `tasks/`, root core files (`Tool.ts`, `commands.ts`, `tools.ts`, `context.ts`, `cost-tracker.ts`, `history.ts`)

**Docs audited:** `docs/source-code-analysis/01-system-overview.md`, `docs/source-code-analysis/core-engine/01-query-engine.md`

**Method:** Line-by-line read of all scoped source files; cross-checked exports, registry behavior, line refs, and flows against documentation.

---

## Critical

| Issue | Fix applied |
|-------|-------------|
| **`tasks/`** subdirectory (12 files) lacked dedicated behavior entries | Added `### tasks/...` sections for all task implementation files plus `types.ts`, `stopTask.ts`, `pillLabel.ts` |
| **`Tool.ts`**, **`commands.ts`**, **`tools.ts`** — core registries with no behavior-template coverage in core doc | Added full behavior sections |
| **`getTaskByType()`** docs implied all `TaskType` variants are dispatchable | Documented that **`in_process_teammate`** is **not** in `getAllTasks()` registry; `stopTask()` returns `unsupported_type` for unregistered types |

---

## Moderate

| Issue | Fix applied |
|-------|-------------|
| **`getGitStatus`**, **`getSystemContext`**, **`getUserContext`** signatures showed invalid `=> void` return type in code blocks | Fixed to `Promise<...>` arrow function signatures |
| **`tasks.ts`** registry description incomplete | Clarified optional `LocalWorkflowTask` / `MonitorMcpTask` lazy requires and base four tasks always present |
| Overview aggregate counts for **`cli/`**, **`entrypoints/`**, **`upstreamproxy/`**, **`server/`**, **`coordinator/`**, root 18 files | Updated in `01-system-overview.md` (shared with A1) |

---

## Minor

| Issue | Fix applied |
|-------|-------------|
| `Task.ts` doc said 125 lines; file is 125 total lines — **accurate** (no change) |
| `query/config.ts`, `query/deps.ts`, `query/stopHooks.ts`, `query/tokenBudget.ts` line counts and exports — **verified accurate** against source |
| `QueryEngine.ts` phase line references and `submitMessage` flow — **spot-checked accurate** (no line ref changes needed) |
| `query.ts` `queryLoop` pipeline ordering and recovery branches — **verified accurate** |

---

## Verified accurate (no doc change)

- `QueryEngine.ts` (1295 lines): 5-phase `submitMessage`, orphaned permission one-shot, cowork eager flush, message switch types
- `query.ts` (1729 lines): context pipeline order (compact boundary → tool budget → snip → microcompact → collapse → autocompact), recovery paths, stop hooks integration
- `context.ts`: memoization + `BREAK_CACHE_COMMAND` / CCR git skip behavior
- `cost-tracker.ts`: session cost persistence and advisor recursion
- `history.ts`: JSONL persistence, paste refs, lock-based flush

---

## Files edited

- `docs/source-code-analysis/01-system-overview.md` (shared aggregate fixes)
- `docs/source-code-analysis/core-engine/01-query-engine.md`

## Source files verified (no code changes)

All 22 core-scope source files read systematically: 6 root core files, `QueryEngine.ts`, `query.ts`, 4 `query/` modules, `Task.ts`, `tasks.ts`, and 12 `tasks/` implementation files.
