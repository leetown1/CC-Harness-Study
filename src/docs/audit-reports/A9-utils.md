# Phase 1 Audit — A9 Utils Layer

**Agent scope:** A9 — `utils/` (564 `.ts`/`.tsx` files)

**Docs audited:** `07-utils-layer.md`, `08-utils-hooks-task-subprocesses.md`, `09-utils-root-gap-fill.md`

**Method:** Regenerated gap-fill from source via `_gen_utils_gap_fill.py`; verified all 267 Part 1 line counts programmatically; spot-read high-traffic modules; cross-checked Part 2 subdir table against actual filenames.

---

## Summary

| Metric | Count |
|--------|------:|
| Total `utils/` source files | 564 |
| Root-level `utils/*.ts` | 290 |
| Root-level `utils/*.tsx` | 8 |
| Root files with dedicated §15 sections in `07` | 23 |
| Root files in regenerated `09` Part 1 | 267 |
| Utils subdirs with deep coverage in `07`/`08` | ~20 major dirs |
| Part 2 behavior tables added in `09` | 12 subdirs (25 files) |

**Coverage model:** `07` documents major subsystems (bash, shell, permissions, settings, hooks, plugins, swarm, etc.) plus §14 brief mentions and §15 for 23 high-traffic root modules. `08` deep-dives hooks/task/teleport batch-4. `09` fills the remaining **267** root `.ts` files and expands thin §14 subdir mentions with verified behavior tables.

---

## Critical

| Issue | Fix applied |
|-------|-------------|
| **`09-utils-root-gap-fill.md` corrupted** — prior auto-generation produced garbled encoding and wrong filenames in Part 2 (e.g. `toolResultStorage.ts`, `actions.ts`, `ultraplanMode.ts` — none exist in source) | Full regeneration from source; Part 2 filenames verified against filesystem |

---

## Moderate

| Issue | Fix applied |
|-------|-------------|
| Part 2 subdir behavior used invented module names | Replaced with verified files: `preconditions.ts`/`remoteSession.ts`, `ghAuthStatus.ts`, `elicitationValidation.ts`/`dateTimeParser.ts`, `keyword.ts`/`ccrSession.ts`, `parser.ts`/`dangerousCmdlets.ts`/`staticPrefix.ts`, etc. |
| Root gap-fill had no verified export/dependency blocks | Each of 267 entries now includes exports (from regex parse), dependency paths, line count, main-flow hint |

---

## Minor / Remaining Gaps

| Issue | Notes |
|-------|-------|
| **8 root `utils/*.tsx` files** not in `09` Part 1 | `autoRunIssue.tsx`, `exportRenderer.tsx`, `highlightMatch.tsx`, `preflightChecks.tsx`, `staticRender.tsx`, `status.tsx`, `statusNoticeDefinitions.tsx`, `teleport.tsx` — partially listed in `07` §15 table only |
| **Behavior notes are heuristic** for most Part 1 entries | Filename/export heuristics; high-traffic modules (auth, config, messages) remain in `07` §15 with manual docs |
| **`07` file counts slightly stale** | e.g. §1 says bash 16 files (source: 23), §10 swarm 14 (source: 22), §4 settings 17 (source: 19) — directory growth since doc write |
| **`utils/skills/`** (1 file) | Brief §14 mention only; no dedicated behavior section |
| Subdirs fully covered in `07`/`08` | No duplicate Part 2 entries (by design): `hooks/`, `task/`, `teleport/`, `plugins/`, `bash/`, `permissions/`, etc. |

---

## Verification results

| Check | Result |
|-------|--------|
| Part 1 line counts (267 entries) | **0 mismatches** (`_verify_09.py`) |
| Part 2 file existence | **25/25** paths exist on disk |
| Export samples spot-checked | `abortController.ts`, `activityManager.ts`, `mappers.ts` — match source |
| Generator output size | 116,658 bytes, 267 entries |

---

## Files edited

- `docs/source-code-analysis/infrastructure/09-utils-root-gap-fill.md` — regenerated (Part 1 + Part 2)

## Helper scripts (audit artifacts)

- `docs/audit-reports/_gen_utils_gap_fill.py` — generator
- `docs/audit-reports/_verify_09.py` — line-count verifier

## Source verification

All 564 utils files inventoried by subdirectory. Regeneration reads every uncovered root `.ts` file for exports, imports, and line count.
