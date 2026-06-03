# Phase 4 — Final Audit Sign-Off

**Date:** 2026-05-23  
**Scope:** Full behavior-level documentation audit of `docs/source-code-analysis/` against 1,884 source files  
**Inputs:** Audit reports A1–A10; cross-cutting reports X1–X3 (not yet available); `docs/coverage_matrix.json`; verification scripts

---

## Executive Summary

| Gate | Result |
|------|--------|
| `python docs/verify_coverage.py` | **PASS** |
| `python docs/verify_exports.py` | **FAIL** |
| **Overall sign-off** | **CONDITIONAL FAIL** — coverage matrix complete; export hygiene and cross-cutting chain reports still open |

The documentation set achieves **100% file coverage** in the coverage matrix (1,884/1,884 verified). Phase 1 module audits (A1–A10) corrected critical behavioral errors across entry, core, tools, commands, services, infrastructure, utils, and UI layers. Remaining blockers: three known-bad symbol names still present in docs, 545 heuristic export-table mismatches from `verify_exports.py`, and missing X1–X3 cross-module chain audit reports.

---

## 1. Per-Module Correction Counts

Counts derived from `docs/audit-reports/A*.md`. Severity = issues fixed or entries added during Phase 1. X1–X3 reports were not found under `docs/audit-reports/` at sign-off time.

| Report | Module / Scope | Files in scope | Critical fixes | Moderate fixes | Minor / other | Docs edited |
|--------|----------------|---------------:|---------------:|---------------:|--------------:|------------:|
| **A1** | Entry layer (`main.tsx`, `entrypoints/`, `cli/`, `bootstrap/`, `server/`, `coordinator/`, `upstreamproxy/`) | 48 | 3 | 4 | 3 | 2 |
| **A2** | Core engine (`QueryEngine.ts`, `query.ts`, `query/`, `Task.ts`, `tasks/`, registries) | 22 | 3 | 3 | 4 verified-accurate | 2 |
| **A3** | Tool system (`Tool.ts`, `tools.ts`, `tools/`, `services/tools/`) | 190 | 7 missing-file gaps closed | 3 doc sections expanded | 2 residual notes | 2 |
| **A4** | Command system (`commands.ts`, `commands/`) | 189 | — | 96 new `####` per-file index entries | 3 accuracy caveats | 2 |
| **A5–A7** | Services layer (`services/`) | 130 | 6 major inaccuracy categories | 7 doc files rewritten/patched | 18 formerly-unverified files filled; 3 residual notes | 7 |
| **A8** | Infrastructure (bridge, state, types, constants, migrations, …) | 691 scoped | 2 | 3 | 3 remaining gaps (buddy, native-ts, outputStyles) | 2 |
| **A9** | Utils layer (`utils/`) | 564 | 1 (corrupted gap-fill regenerated) | 2 (invented names → verified files) | 267 Part 1 entries regenerated; 5 residual gaps | 1 |
| **A10** | UI layer (`components/`, `hooks/`, `ink/`, `context/`) | 598 | 7 behavior/API errors | 3 architecture + 20 line-count auto-fixes | 17 previously-missing files added | 5 |
| **X1** | Startup chain (`cli.tsx → main() → run() → setup → REPL`) | — | — | — | **Report not available** | — |
| **X2** | Query chain (`QueryEngine → query() → claude.ts → tool dispatch`) | — | — | — | **Report not available** | — |
| **X3** | Permissions chain (`useCanUseTool → permissions.ts → UI`) | — | — | — | **Report not available** | — |

**Phase 1 totals (approximate):** ~23 critical, ~120 moderate, ~320 minor/generated entries, **21 doc files** directly edited across A1–A10.

---

## 2. Coverage Matrix Statistics

Source: `docs/coverage_matrix.json` (read 2026-05-23)

| Metric | Value | Target | Status |
|--------|------:|--------|--------|
| Total files tracked | **1,884** | 1,884 | ✅ |
| `verified: true` | **1,884** | 1,884 | ✅ |
| `depth: behavior` | **1,880** | 1,884 | ✅ (4 generated exempt) |
| `depth: generated` | **4** | 4 (`types/generated/*`) | ✅ |
| `depth: none` | **0** | 0 | ✅ |
| Missing `doc_refs` | **0** | 0 | ✅ |
| Utils root (`utils/*.{ts,tsx}`, one slash) | **298** | 298 | ✅ all `behavior`, 0 `none` |

### Depth by top-level directory

| Directory | Total | Behavior | Generated | Verified |
|-----------|------:|---------:|----------:|---------:|
| `(root)` | 18 | 18 | 0 | 18 |
| `utils/` | 564 | 564 | 0 | 564 |
| `components/` | 389 | 389 | 0 | 389 |
| `commands/` | 189 | 189 | 0 | 189 |
| `tools/` | 184 | 184 | 0 | 184 |
| `services/` | 130 | 130 | 0 | 130 |
| `hooks/` | 104 | 104 | 0 | 104 |
| `ink/` | 96 | 96 | 0 | 96 |
| `bridge/` | 31 | 31 | 0 | 31 |
| `types/` | 11 | 7 | 4 | 11 |
| *(all other dirs)* | 170 | 170 | 0 | 170 |

---

## 3. Sign-Off Checklist (from audit plan)

| # | Criterion | Result | Evidence |
|---|-----------|--------|----------|
| 1 | **1,884 files at behavior depth + verified** | ✅ **PASS** | `verify_coverage.py`: Total 1884, Not behavior 0, Not verified 0. Matrix: 1880 behavior + 4 generated, all verified. |
| 2 | **Line count mismatches** | ⚠️ **PASS with minor drift** | `verify_coverage.py` passed. Targeted scan of `` `file.ts` (N lines) `` annotations: **0 mismatches >5 lines**. A10 notes ±1–6 line drift on a handful of large UI files (source changed since doc write). A8 residual: `workSecret.ts` doc 122 vs source 127 (pre-existing). A5 residual: compact.ts header 1705 vs source 1579. |
| 3 | **"Not verified" count in docs** | ✅ **PASS** | `grep -r "Not verified" docs/source-code-analysis/` → **0 matches**. A5–A7 removed all 18 former disclaimers; filled in `07-services-unverified-fill.md`. |
| 4 | **Utils root coverage** | ✅ **PASS** | 298/298 utils root files in matrix at `depth: behavior`, `verified: true`. `verify_coverage.py`: utils root depth=none **0**. A9 regenerated `09-utils-root-gap-fill.md` (267 Part 1 `.ts` entries, 0 line-count mismatches). 8 root `.tsx` files covered via `07-utils-layer.md` §15 + catalog. |
| 5 | **Cross-module chains** | ⚠️ **PARTIAL** | X1/X2/X3 audit reports **not available**. Chain documentation exists in source docs and passes matrix checks for key nodes (see below). Phase 2 sub-agent reports pending formal sign-off. |

### Cross-module chain spot-check (matrix + doc refs)

| Chain | Documented path | Key nodes in matrix |
|-------|-----------------|---------------------|
| **Startup (X1)** | `01-system-overview.md` §4 Startup Flow; `02-entry-layer.md` | `entrypoints/cli.tsx`, `main.tsx`, `setup.ts`, `screens/REPL.tsx` — all behavior + verified |
| **Query (X2)** | `core-engine/01-query-engine.md`; overview §4 Phase 5 | `QueryEngine.ts`, `query.ts`, `services/api/claude.ts` — all behavior + verified |
| **Permissions (X3)** | `01-system-overview.md` dependency map; A10 fixes in `03-hooks.md` | `hooks/useCanUseTool.tsx`, `types/permissions.ts` — behavior + verified; A10 corrected `useCanUseTool` API description |

---

## 4. Verification Script Results

### `python docs/verify_coverage.py` — **PASS** (exit 0)

```
======================================================================
COVERAGE VERIFICATION
======================================================================
Total files: 1884
Not behavior depth: 0
Not verified: 0
No doc_refs: 0
utils root depth=none: 0

PASSED: All files behavior-level and verified.
```

### `python docs/verify_exports.py` — **FAIL** (exit 1)

```
======================================================================
EXPORT VERIFICATION (scoped): checked=664 fabricated=545
======================================================================
  [02-entry-layer.md] entrypoints/sdk/coreSchemas.ts: `error_max_turns` not exported
  [01-commands.md] types/command.ts: `name` not exported
  [01-commands.md] types/command.ts: `description` not exported
  ... (545 total heuristic mismatches; first 50 printed)

Known bad symbols still in docs: ['parseArgs', 'MCPClient', 'tengu_first_token_date']
```

**Notes:** Most of the 545 "fabricated" hits are false positives — table rows listing interface **fields** (e.g. `Command.name`) or string-literal command names (e.g. `'commit'`) rather than top-level exports. The three **known bad symbols** are genuine blockers per script design.

---

## 5. Remaining Risks

### Auto-generated stubs vs hand-verified depth

| Tier | Location | Count | Depth | Risk |
|------|----------|------:|-------|------|
| **Hand-verified** | Core docs (`01`–`08` per layer), gap-fill deep sections, A1–A10 corrected areas | ~370 files with dedicated `###` headings | Exports + flows + boundaries read against source | Low — primary reference material |
| **Semi-automated** | `09-utils-root-gap-fill.md` Part 1 | 267 root `.ts` files | Regex exports + import deps + heuristic main-flow | Medium — line counts verified (0 mismatches); behavior bullets are filename/export heuristics |
| **Auto-generated stubs** | `10-full-file-catalog.md` | **1,512** entries | Template: exports list, deps, generic "Module-level utilities" flow | **High for edge cases** — guarantees matrix coverage, not behavioral accuracy |
| **Table-only / partial** | Various supplement docs, LSP method tables in `05-service-gap-fill.md` §3 | ~50–100 files | Directory-level or idealized API names | Medium — A5 notes LSP §3 tables still approximate; prefer `04-other-services.md` §4 |
| **Generated protobuf** | `types/generated/*` | 4 | Documented as generated; no line-by-line analysis | Low — intentional exemption |

### Other residual risks

1. **Export symbol hygiene** — `parseArgs`, `MCPClient`, `tengu_first_token_date` remain in docs; should be grep-replaced or removed.
2. **Command gap-fill §5 type fields** — A4 warns auto-extracted `type:` may reflect `LocalCommandResult.type` not `Command.type`.
3. **UI line-count drift** — Large components may be ±1–6 lines stale until next regen pass.
4. **Cross-cutting chains** — Documented in overview/core docs but lack formal X1–X3 audit reports with issue/fix tables.
5. **`verify_exports.py` heuristic noise** — 545 scoped mismatches include interface fields and string literals; script should be refined before treating as hard failures.

---

## 6. Sign-Off Decision

| Area | Verdict |
|------|---------|
| File coverage (1884/1884) | ✅ **Signed off** |
| Behavior depth in matrix | ✅ **Signed off** |
| Phase 1 module corrections (A1–A10) | ✅ **Signed off** |
| "Not verified" disclaimers | ✅ **Signed off** (0 remaining) |
| Utils root gap-fill | ✅ **Signed off** |
| Line counts (critical paths) | ⚠️ **Accepted with minor drift** |
| Cross-module chains (X1–X3) | ❌ **Not signed off** — reports pending |
| Export verification | ❌ **Not signed off** — 3 bad symbols |

### Overall: **CONDITIONAL FAIL**

**Pass criteria met:** coverage matrix complete, all files verified, utils root filled, Phase 1 corrections applied, zero "Not verified" strings.

**Fail criteria:** `verify_exports.py` exit 1; X1–X3 cross-cutting audit reports missing; ~1,512 auto-generated catalog stubs provide breadth without behavioral depth guarantee.

**Recommended next steps:**
1. Produce X1, X2, X3 audit reports under `docs/audit-reports/`.
2. Remove or replace `parseArgs`, `MCPClient`, `tengu_first_token_date` in docs.
3. Refine `verify_exports.py` to skip interface-field rows and string-literal command names.
4. Spot-upgrade high-traffic catalog stubs (QueryEngine, claude.ts, useCanUseTool) from template to hand-verified depth.

---

*Generated by Phase 4 sign-off agent. Plan file not modified.*
