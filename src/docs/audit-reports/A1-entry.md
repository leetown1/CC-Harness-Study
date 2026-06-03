# Phase 1 Audit — A1 Entry Layer

**Scope:** `main.tsx`, `setup.ts`, root helpers, `entrypoints/`, `cli/`, `bootstrap/state.ts`, `server/`, `coordinator/`, `upstreamproxy/`

**Docs audited:** `docs/source-code-analysis/01-system-overview.md`, `docs/source-code-analysis/02-entry-layer.md`

**Method:** Line-by-line read of all scoped source files; cross-checked exports, flows, line counts (total physical lines), and dependency references against documentation.

---

## Critical

| Issue | Fix applied |
|-------|-------------|
| **`server/`**, **`coordinator/`**, **`upstreamproxy/`**, **`cli/transports/transportUtils.ts`**, and **`setup.ts`** had no dedicated `### path (N lines)` behavior entries in `02-entry-layer.md` | Added full behavior sections with exports, flows, dependencies, and feature gates |
| **`applyCoordinatorToolFilter`** listed under coordinator dynamic imports without module path — implies it lives in `coordinatorMode.ts` | Corrected to `utils/toolPool.js`; coordinator section now states tool filtering is in `toolPool.ts` |
| **`server/`** described as server-side lifecycle in overview; source is **client-side** WebSocket manager for cc:// sessions | Rewrote overview + added accurate `DirectConnectSessionManager` / `createDirectConnectSession` docs |

---

## Moderate

| Issue | Fix applied |
|-------|-------------|
| **`cli/`** directory count wrong (18 vs **19** files); missing **`transportUtils.ts`** | Updated `01-system-overview.md` table; added `transportUtils.ts` to transports list |
| Aggregate line totals stale in overview: **`cli/`** (~11,431 → **~12,355**), **`entrypoints/`** (~3,742 → **~4,052**), **`src/` root** (~11,321 → **~11,972**), **`server/`** (321 → **358**), **`coordinator/`** (276 → **369**), **`upstreamproxy/`** (692 → **740**) | Updated `01-system-overview.md` |
| **`upstreamproxy`** overview listed vague "relay" purpose; missed fail-open design and `CCR_UPSTREAM_PROXY_ENABLED` server injection | Expanded overview bullets; added init/relay behavior entries |
| **`coordinatorMode.ts`** overview omitted exported API surface | Documented four exports and env activation (`CLAUDE_CODE_COORDINATOR_MODE`) |

---

## Minor

| Issue | Fix applied |
|-------|-------------|
| Typo **`suniquekeepaliveinterval()`** in WebSocket transport docs | Fixed to **`startKeepaliveInterval()`** |
| Root entry-adjacent files (`ink.ts`, `interactiveHelpers.tsx`, `dialogLaunchers.tsx`, `replLauncher.tsx`, `projectOnboardingState.ts`, `costHook.ts`) only in overview table | Added concise behavior entries under "ROOT HELPERS" in `02-entry-layer.md` |
| **`transportUtils.ts`** was incorrectly described as "shared transport utilities" in overview | Updated to transport factory description |

---

## Files edited

- `docs/source-code-analysis/01-system-overview.md`
- `docs/source-code-analysis/02-entry-layer.md`

## Source files verified (no code changes)

All 48 entry-scope source files read systematically, including all 19 `cli/` files, 8 `entrypoints/` files, `bootstrap/state.ts`, 3 `server/` files, `coordinator/coordinatorMode.ts`, 2 `upstreamproxy/` files, and 8 root entry-adjacent files.
