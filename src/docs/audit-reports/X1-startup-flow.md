# Phase 2 Cross-Cutting Audit — X1 Startup Flow

**Chain verified:** `entrypoints/cli.tsx` → `main()` in `main.tsx` → `run()` → `preAction` → `setup.ts` → REPL / headless / daemon paths

**Docs audited:** `docs/source-code-analysis/01-system-overview.md`, `docs/source-code-analysis/02-entry-layer.md`

**Method:** Step-by-step trace of source call order, line ranges, and feature gates; compared against documented startup flows and diagrams.

---

## Verified call order (source of truth)

| Step | Location | Lines | Notes |
|------|----------|-------|-------|
| 1 | `entrypoints/cli.tsx` top-level | 1–26 | Corepack fix, CCR heap, `ABLATION_BASELINE` env (before any dynamic import) |
| 2 | `cli.tsx` `main()` fast paths | 33–274 | Version, MCP helpers, daemon-worker, bridge, daemon, bg, templates, runners, tmux/worktree |
| 3 | `cli.tsx` fallback | 288–298 | `startCapturingEarlyInput()` → `import('../main.js')` → `await cliMain()` |
| 4 | `main.tsx` module eval | 1–209 | MDM + keychain prefetch side effects, imports, `main_tsx_imports_loaded` |
| 5 | `main.tsx` `main()` | 585–856 | Security, argv rewrite (cc://, LODESTONE, KAIROS, SSH), client type, `eagerLoadSettings()`, `await run()` @854 |
| 6 | `run()` Commander build | 884–906 | Program + `preAction` registration |
| 7 | `preAction` | 907–967 | MDM/keychain → `init()` → title → `initSinks()` → plugin-dir → **`runMigrations()`** → remote settings |
| 8 | Print fast path | 3883–3889 | Skip subcommands; `parseAsync` @3887 |
| 9 | Full parse | 4504 | Subcommands registered; `parseAsync` |
| 10 | Default `.action()` | 1007+ | Tools/MCP prep → **`setup()`** @1908–1934 → mode dispatch |
| 11a | Headless | 2584–2860 | `--init-only` exits earlier @2572; `runHeadless()` @2829 |
| 11b | REPL | 3134+ | `launchRepl()` → `App` → `REPL` |
| — | Daemon (bypasses main) | `cli.tsx` 165–179 | `daemonMain()` after `enableConfigs` + `initSinks` |
| — | Bridge RC (bypasses main) | `cli.tsx` 112–161 | Auth → GB gate → policy → `bridgeMain()` |

**Feature gates on fast paths:** `DUMP_SYSTEM_PROMPT`, `CHICAGO_MCP`, `DAEMON`, `BRIDGE_MODE`, `BG_SESSIONS`, `TEMPLATES`, `BYOC_ENVIRONMENT_RUNNER`, `SELF_HOSTED_RUNNER`, `DIRECT_CONNECT`, `LODESTONE`, `KAIROS`, `SSH_REMOTE`, `UDS_INBOX` (messaging socket in `setup()`).

---

## Critical

| Issue | Fix applied |
|-------|-------------|
| **Startup flow started at `main.tsx`**, omitting `entrypoints/cli.tsx` as the first executable and missing daemon/bridge fast paths that never load `main.tsx` | Rewrote §4 Startup Flow in `01-system-overview.md`; added phase 0 for `cli.tsx`; added mermaid diagram |
| **`cli.tsx` described as "structured I/O mode"** — actual role is process bootstrap with fast-path dispatch | Corrected entry-layer descriptions in `01-system-overview.md` (layer summary + entrypoints table) |
| **`runMigrations()` documented as running "before main logic" / at import time** — actually invoked from `preAction` after `init()` (line 950) | Fixed migration timing in both docs; restructured `02-entry-layer.md` startup §2 |
| **`setup.ts` claimed to call `processSessionStartHooks()`** — session-start hooks run from `main.tsx` action / `print.ts`, not `setup.ts` | Corrected `setup.ts` flow list in `02-entry-layer.md` |

---

## Moderate

| Issue | Fix applied |
|-------|-------------|
| **`preAction` vs `parseAsync` order wrong** — docs listed "parse argv" before `preAction`; `preAction` runs during `parseAsync` before the action | Fixed in `02-entry-layer.md` §3 and §6 |
| **Single `parseAsync` at line 4504** — print mode uses early parse at **3887** (skips subcommand registration) | Documented both paths in both docs |
| **`cc://` / `assistant` / `ssh` argv rewriting listed under action handler** — rewriting is in `main()` (609–795); action handler consumes `_pendingConnect` / `_pendingSSH` / `_pendingAssistantChat` | Moved/clarified in `02-entry-layer.md` action handler section |
| **§4 startup listed bridge/daemon under `main.tsx` subcommands** — `remote-control` and `daemon` are handled in `cli.tsx` before `main.tsx` loads | Documented in overview startup phases and audit table |
| **Dependency map started at `main.tsx`** | Prefixed with `entrypoints/cli.tsx` → `main.tsx` in `01-system-overview.md` |

---

## Minor

| Issue | Fix applied |
|-------|-------------|
| **`initSinks()` called in both `preAction` and `setup.ts`** — docs implied single location | `preAction` init for subcommands; `setup.ts` re-attaches for default command path (noted in overview preAction steps) |
| **`run()` line range "884–1934+"** understated file extent | Updated to 884–4513 in `02-entry-layer.md` |
| **No visual flow diagram** | Added mermaid flowchart to `01-system-overview.md` §4 |

---

## Files edited

- `docs/source-code-analysis/01-system-overview.md` — entry layer summary, cli.tsx description, migrations note, dependency map, full §4 startup rewrite + mermaid
- `docs/source-code-analysis/02-entry-layer.md` — startup sequence restructure, `setup.ts` flow correction, `run()`/action handler ordering fixes

## Source files traced (no code changes)

- `entrypoints/cli.tsx` (303 lines)
- `main.tsx` — `main()` 585–856, `run()` 884–4513, `preAction` 907–967, `.action()` 1007+, print fast path 3883–3889
- `entrypoints/init.ts` — called from `preAction` line 916
- `setup.ts` — `setup()` export, invoked from action handler ~1908–1934
- `replLauncher.tsx`, `cli/print.js` (`runHeadless`) — terminal dispatch paths
- `daemon/main.js`, `bridge/bridgeMain.js` — cli.tsx fast-path exits
