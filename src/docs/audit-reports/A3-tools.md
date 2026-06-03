# Phase 1 Audit — A3 Tools

**Scope:** `Tool.ts`, `tools.ts`, `tools/` (187 files), `services/tools/` (4 files)  
**Audit date:** 2026-05-23  
**Docs:** `docs/source-code-analysis/tool-system/*.md` (6 files)

## Summary

| Metric | Before | After |
|--------|-------:|------:|
| Source `.ts`/`.tsx` files audited | 190 | 190 |
| Files with behavior-level coverage | ~138 | **190** (all mentioned; 7 previously missing now documented) |
| Missing from docs entirely | 7 | **0** |
| Known line-count collisions (`UI.tsx` basename) | 27 false positives | Documented per-tool paths; MCPTool `UI.tsx` = 403 lines |

## Core Files Verified

| File | Lines | Status |
|------|------:|--------|
| `Tool.ts` | 792 | Interface, `buildTool`, types — `01-overview.md` |
| `tools.ts` | 389 | Registry, conditional imports, presets — `01-overview.md` |
| `services/tools/toolExecution.ts` | 1745 | `06-other-tools.md` |
| `services/tools/toolHooks.ts` | 650 | `06-other-tools.md` |
| `services/tools/toolOrchestration.ts` | 188 | `06-other-tools.md` |
| `services/tools/StreamingToolExecutor.ts` | 530 | `06-other-tools.md` |

## Edits Applied

1. **`05-agent-tools.md`** — Expanded `TaskOutputTool` section; corrected path to `TaskOutputTool.tsx` (584 lines) with input/output schemas and execution flow
2. **`06-other-tools.md`** — Added full `AskUserQuestionTool` section (266 lines); added `TestingPermissionTool` section; expanded `ScheduleCronTool` with per-file `CronCreateTool.ts` / `CronDeleteTool.ts` / `CronListTool.ts` entries; documented `REPLTool/primitiveTools.ts`
3. Verified `tools.ts` conditional import gates match `01-overview.md` (`getAllBaseTools`, feature flags, ant-only tools)

## Previously Missing (now covered)

| File | Lines | Doc section |
|------|------:|-------------|
| `tools/AskUserQuestionTool/AskUserQuestionTool.tsx` | 266 | `06-other-tools.md` § AskUserQuestionTool |
| `tools/TaskOutputTool/TaskOutputTool.tsx` | 584 | `05-agent-tools.md` § TaskOutputTool |
| `tools/ScheduleCronTool/CronCreateTool.ts` | 157 | `06-other-tools.md` § ScheduleCronTool |
| `tools/ScheduleCronTool/CronDeleteTool.ts` | 95 | `06-other-tools.md` § ScheduleCronTool |
| `tools/ScheduleCronTool/CronListTool.ts` | 97 | `06-other-tools.md` § ScheduleCronTool |
| `tools/REPLTool/primitiveTools.ts` | 39 | `06-other-tools.md` § REPLTool |
| `tools/testing/TestingPermissionTool.tsx` | 74 | `06-other-tools.md` § TestingPermissionTool |

## Residual Notes

- Per-tool `prompt.ts`, `constants.ts`, and `UI.tsx` helper files are covered at tool-directory level (not individual `###` headings) — acceptable for Phase 1
- Basename-only line-count scans falsely match MCPTool's `UI.tsx (403 lines)` against other tools' `UI.tsx` files; docs use full paths where line counts matter
