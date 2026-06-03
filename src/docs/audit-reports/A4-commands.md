# Phase 1 Audit — A4 Commands

**Scope:** `commands.ts`, `commands/` (189 `.ts`/`.tsx` files)  
**Audit date:** 2026-05-23 (deep verification pass)  
**Docs:** `docs/source-code-analysis/command-system/*.md` (2 files)

## Summary

| Metric | Before | After |
|--------|-------:|------:|
| Command implementation files | 189 | 189 (110 `.ts` + 79 `.tsx`) |
| Files with dedicated `###`/`####` sections | 189 | 189 |
| `commands.ts` line count in docs | 754 | **754** (verified) |
| `types/command.ts` line count | 216 | **216** (verified) |
| Doc corrections this pass | — | **47** |

## Deep Verification Findings (2026-05-23)

### Registry (`commands.ts`)

- **71 base** built-in commands in `COMMANDS()` (was documented as ~65); up to **~82** with feature flags + OAuth pair
- **`INTERNAL_ONLY_COMMANDS`:** 25 fixed entries + up to 3 conditional (`forceSnip`, `ultraplan`, `subscribePr`) = **28 max** — confirmed against source
- **`usageReport` / `/insights`:** lazy shim in `commands.ts:190-202`; full impl in `commands/insights.ts` (`name: 'insights'`, not `project_areas`)
- **`commands/install.tsx`:** CLI-only native installer — **not** in `COMMANDS` or `getCommands()`

### Type / Section Misplacements Fixed

| Issue | Source truth | Doc fix |
|-------|-------------|---------|
| `/btw`, `/add-dir` under §3 Prompt Commands | Both are `local-jsx` | Moved to §5.49–5.50 |
| Appendix listed `compact (interactive)` as `local-jsx` | `/compact` is `local` | Removed from JSX table |
| §5 gap-fill `type: text/compact/skip/utf8/...` on impl files | `LocalCommandResult` or UI state, not `Command.type` | Replaced with `commandType` + `returns` convention |
| `insights.ts` indexed as `name: project_areas` | Command is `insights`; `project_areas` is internal report section ID | Corrected in §5.35.1 |
| `security-review.ts` listed as `type: text` | `prompt` via `createMovedToPluginCommand` | Corrected |
| `install.tsx` listed as `type: checking` | UI state; export is `local-jsx`-shaped, CLI-only | Corrected |
| `statusline.tsx` description truncated | Full: "Set up Claude Code's status line UI" | Corrected |

### Feature Gates Verified

| Flag | Command | Type | Notes |
|------|---------|------|-------|
| `KAIROS` / `KAIROS_BRIEF` | `/brief` | `local-jsx` | GB `tengu_kairos_brief_config.enable_slash_command` |
| `ULTRAPLAN` | `/ultraplan` | `local-jsx` | ANT-only internal |
| `BRIDGE_MODE` | `/remote-control` | `local-jsx` | aliases `rc` |
| `FORK_SUBAGENT` | `/fork` | — | `/branch` loses `fork` alias when enabled |
| `VOICE_MODE` | `/voice` | `local` | `claude-ai` availability |
| `CCR_REMOTE_SETUP` | `/web-setup` | `local-jsx` | |
| `MCP_SKILLS` | MCP skill filter | — | `getMcpSkillCommands()` |

### Implementation Inventory (confirmed)

- **110** `.ts` implementation/registration modules
- **79** `.tsx` UI modules
- **18** `.js` ANT-only stubs (not in 189 external count)
- **82** distinct slash-command names in registry (including duplicates like `context`/`extra-usage` interactive + non-interactive variants)

## Doc Edits Applied (This Pass)

1. **`01-commands.md`** — 12 fixes: COMMANDS count, moved `/btw`/`/add-dir` to §5, added `/brief`/`/ultrareview`/`/ultraplan`/`install.tsx` sections, fixed appendix JSX table, renumbered §3
2. **`02-command-gap-fill.md`** — 35 fixes: §5 type-field convention note, corrected 33 file entries (`commandType`/`returns`/exports/feature gates/ANT-only)

## Coverage Map

| Doc section | Files | Coverage type |
|-------------|------:|----------------|
| `01-commands.md` §1–2 | types + registry | Type system, exports, discovery flow |
| `01-commands.md` §3–6 | ~74 commands | Command-level behavior (prompt/local/local-jsx) |
| `02-command-gap-fill.md` §1–4 | 28 files | Deep file-level analysis |
| `02-command-gap-fill.md` §5 | 96 impl files | Per-file `####` index with corrected metadata |

## Residual Notes

- §5 index entries for thin `index.ts` wrappers defer to parent `###` sections in `01-commands.md` — by design
- Feature-gated commands whose source lives outside `commands/` tree (e.g. `proactive.js`, `fork/index.js`) are documented in §10.2 only; no `.ts`/`.tsx` file in the 189 count
- Plugin subsystem line total in `01-commands.md` (7259 lines) vs gap-fill §1 (~6400) — gap-fill counts TS/TSX only

## Files Not in External Build

§7 internal ANT-only stubs (`index.js` in gated directories) documented in `01-commands.md`; not counted in the 189 external `commands/` file inventory.
