# A10 UI Layer Audit Report

**Agent:** A10  
**Date:** 2026-05-23  
**Scope:** `components/` (389), `hooks/` (104), `ink/` (96), `context/` (9) — 598 files  
**Docs:** `docs/source-code-analysis/ui-layer/*.md` (11 files)

---

## Summary

Phase 2 deep verification prioritized the **top 50 most-imported** hooks/components (import-path grep, excluding `utils`/`types`/`index` barrel false positives). Enhanced behavior entries for catalog-stub modules that already had only auto-stubs in `10-full-file-catalog.md`. Corrected props/state-machine descriptions where source diverged from ui-layer docs.

| Metric | Phase 1 | Phase 2 |
|--------|---------|---------|
| Files with doc mention | 598 / 598 | 598 / 598 |
| Critical behavior errors (known list) | 0 | **0** |
| Top-50 import modules with behavior depth | ~12 rich / ~38 stub | **50 / 50** addressed |
| Props/state-machine corrections (this pass) | — | **14** |

---

## Import ranking method

Python import scan over all `.ts`/`.tsx` (excluding `node_modules`, `docs/`):

- Match normalized module paths (`hooks/useTerminalSize`, `components/design-system/Dialog`, `.js` suffix stripped).
- Exclude generic basenames (`utils`, `types`, `index`, `constants`, `helpers`) to avoid inflated counts.

**Top 10 by importer count:**

| Count | Module |
|------:|--------|
| 66 | `hooks/useTerminalSize.ts` |
| 66 | `components/design-system/Dialog.tsx` |
| 57 | `components/design-system/Byline.tsx` |
| 57 | `components/MessageResponse.tsx` |
| 56 | `components/design-system/KeyboardShortcutHint.tsx` |
| 56 | `components/CustomSelect/select.tsx` |
| 50 | `components/ConfigurableShortcutHint.tsx` |
| 29 | `components/permissions/PermissionRequest.tsx` |
| 28 | `hooks/useExitOnCtrlCDWithKeybindings.ts` |
| 26 | `hooks/useCanUseTool.tsx` |

Full top-50 list used for enhancement targeting; high fan-in design-system primitives dominate (not `PromptInput`/`useTypeahead`, which are wired centrally from `REPL.tsx`).

---

## Phase 2 fixes — behavior / props / state machines

| Doc | Module | Issue | Fix |
|-----|--------|-------|-----|
| `02-components.md` | `MessageResponse.tsx` | Described copy-on-select + expand/collapse | Documented `⎿` tree indent, nesting context, `Ratchet` offscreen lock; props `children`, `height?` |
| `02-components.md` | `PermissionRequest.tsx` | Called "state management" for allow/deny flow | Clarified tool→component dispatcher; persistence in `useCanUseTool` |
| `02-components.md` | `FallbackToolUseErrorMessage.tsx` | One-line stub | Error tag parsing, truncation, expand shortcut |
| `02-components.md` | `ConfigurableShortcutHint.tsx` | One-line stub | `useShortcutDisplay` → `KeyboardShortcutHint` pipeline |
| `02-components.md` | `inputModes.ts` | "chat, bash, multi-line" | `'bash' \| 'prompt'` + `!` prefix helpers |
| `02-components.md` | Design system §5.3 | Table-only stubs for top imports | Expanded `Dialog`, `Byline`, `KeyboardShortcutHint`, `Pane`, `Tabs`, `Divider` with props and keybindings |
| `03-hooks.md` | `useTerminalSize.ts` | "wraps `useStdout()`" | `TerminalSizeContext` + throws outside Ink App |
| `03-hooks.md` | `useExitOnCtrlCD*` | One-line stub | `ExitState` double-press FSM, `onInterrupt`, `isActive` |
| `03-hooks.md` | `useSwarmPermissionPoller.ts` | Polled "output directories" | `permissionSync.pollForResponse` @ 500ms; worker callback registry |
| `03-hooks.md` | `useVoice.ts` | Listed Chinese in STT allowlist | Removed — `zh` not in `SUPPORTED_LANGUAGE_CODES` |
| `03-hooks.md` | `useSettings.ts` | "zustand-like store" | `useAppState(s => s.settings)` + disk watcher |
| `03-hooks.md` | `useSearchInput.ts` | "debounced suggestions" | Vim/less key model, kill ring, Esc/cancel semantics |
| `03-hooks.md` | `useMainLoopModel.ts` | Generic one-liner | GrowthBook refresh re-render for alias resolution |
| `03-hooks.md` | `useElapsedTime.ts` | "HH:MM:SS status line" | `useSyncExternalStore`, `endTime` freeze, `formatDuration` |
| `03-hooks.md` | `useIdeSelection.ts` | Generic polling description | MCP `selection_changed` subscription + schema |
| `03-hooks.md` | `fileSuggestions.ts` | Vague cache invalidation | Git index mtime, signature skip, `onIndexBuildComplete` |

---

## Phase 1 recap (unchanged)

- All 598 scoped source files appear in at least one ui-layer doc.
- Prior critical fixes retained: `useCanUseTool` → `CanUseToolFn`, `useRemoteSession` scope, `useReplBridge`, `useInboxPoller` interval, voice FSM, `useHistorySearch` no Fuse.js, ink root file count, scroll drain constants.
- Line counts standardized to **physical total lines**.

---

## Catalog vs ui-layer priority

Of the import top 50, **38** had catalog auto-stubs (`10-full-file-catalog.md`) with thin "Main flow / Boundaries" text but insufficient behavior in ui-layer. Phase 2 patches targeted ui-layer docs directly; catalog stubs left as index entries (per gap-fill scope).

Modules already rich before this pass (no patch needed): `CustomSelect/select.tsx`, `PermissionRequest` detail in `06-permissions-custom-components.md`, `PromptInputFooterSuggestions` in `04-components-supplement.md`, `Spinner`, `TextInput`, `Markdown`, `CtrlOToExpand`, `PermissionDialog`.

---

## Files modified (Phase 2)

- `docs/source-code-analysis/ui-layer/02-components.md`
- `docs/source-code-analysis/ui-layer/03-hooks.md`
- `docs/audit-reports/A10-ui.md` (this report)

**Phase 1 files (prior pass):** `01-ink-engine.md`, `04-components-supplement.md`, `08-large-hooks.md`

---

## Status

**Phase 2 complete** for Agent A10 UI scope. Remaining optional work: line-count drift on fast-moving large files (`PromptInput.tsx`, `Messages.tsx`) — ±1–6 lines, no systematic error pattern.
