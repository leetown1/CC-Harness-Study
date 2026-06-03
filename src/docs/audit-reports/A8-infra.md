# Phase 1 Audit — A8 Infrastructure

**Agent scope:** A8 — `bridge/`, `state/`, `types/`, `constants/`, `migrations/`, `schemas/`, `memdir/`, `remote/`, `tasks/`, `screens/`, `buddy/`, `keybindings/`, `vim/`, `voice/`, `native-ts/`, `assistant/`, `moreright/`, `outputStyles/` (691 source files)

**Docs audited:** `docs/source-code-analysis/infrastructure/01-bridge-system.md` through `06-remote-tasks-screens.md`, `02-state-types-constants.md`, `03-keybindings-vim-voice.md`, `04-memory-system.md`, `05-context-context.md`

**Method:** File inventory vs documentation cross-reference; line counts verified programmatically; targeted source reads for reported gaps.

---

## Summary

| Area | Source files | Doc coverage | Status |
|------|-------------:|:-------------|:-------|
| `bridge/` | 31 | 31/31 in `01-bridge-system.md` | Fixed (2 missing modules added) |
| `state/` | 6 | 6/6 in `02-state-types-constants.md` | OK |
| `types/` | 11 | 11/11 in `02-state-types-constants.md` | Fixed (`permissions.ts` unions) |
| `constants/` | 21 | 21/21 in `02-state-types-constants.md` | OK |
| `migrations/` | 11 | Table in `06-remote-tasks-screens.md` §E | Partial (no per-file `###` sections) |
| `schemas/` | 1 | `06-remote-tasks-screens.md` §H.3 | OK |
| `memdir/` | 8 | `04-memory-system.md` | OK |
| `remote/` | 4 | `06-remote-tasks-screens.md` | OK |
| `tasks/` | 12 | `06-remote-tasks-screens.md` | OK |
| `screens/` | 3 | `06-remote-tasks-screens.md` | OK |
| `keybindings/` | 14 | `03-keybindings-vim-voice.md` | OK |
| `vim/` | 5 | `03-keybindings-vim-voice.md` | OK |
| `voice/` | 1 | `03-keybindings-vim-voice.md` | OK |
| `assistant/` | 1 | `06-remote-tasks-screens.md` §H.1 | OK |
| `moreright/` | 1 | `06-remote-tasks-screens.md` §H.2 | OK |
| `buddy/` | 6 | Overview + `10-full-file-catalog.md` only | Gap (not in infrastructure docs) |
| `native-ts/` | 4 | `ui-layer/01-ink-engine.md` §7 only | Gap (not in infrastructure docs) |
| `outputStyles/` | 1 | Overview + catalog only | Gap (not in infrastructure docs) |

---

## Critical

| Issue | Fix applied |
|-------|-------------|
| **`bridge/bridgePermissionCallbacks.ts`** and **`bridge/replBridgeHandle.ts`** absent from `01-bridge-system.md` Supporting Infrastructure (31 source files, 29 documented) | Added behavior entries under §11 Supporting Infrastructure |
| **`types/permissions.ts`** union docs wrong: `PermissionDenyDecision` field named `reason` (source uses `message`); `PermissionAskDecision` used `permissionSuggestions` (source uses `suggestions`); `PermissionResult` described as allow/deny only (source is 4-variant union including `passthrough`); `bubble` mode conflated with runtime `INTERNAL_PERMISSION_MODES`; missing classifier/explainer/working-dir types | Rewrote permissions section in `02-state-types-constants.md` |

---

## Moderate

| Issue | Fix applied |
|-------|-------------|
| `InternalPermissionMode` `'bubble'` documented as user-addressable alongside `'auto'` | Clarified: `'bubble'` is type-only; runtime array is `EXTERNAL_PERMISSION_MODES` + conditional `'auto'` |
| Missing types in permissions docs: `ToolPermissionRulesBySource`, `AdditionalWorkingDirectory`, `WorkingDirectorySource`, `PermissionCommandMetadata`, `ClassifierResult`, `YoloClassifierResult`, `PermissionExplanation`, `RiskLevel` | Added to `02-state-types-constants.md` |
| `PermissionDecisionReason` variants truncated with `...` | Expanded full discriminated union including `sandboxOverride`, `classifier`, `workingDir`, `safetyCheck.classifierApprovable`, `other` |

---

## Minor / Remaining Gaps

| Issue | Notes |
|-------|-------|
| **`migrations/`** (11 files) | Covered as migration table + pattern in `06-remote-tasks-screens.md`; no individual `### migrations/...` behavior sections |
| **`buddy/`**, **`native-ts/`**, **`outputStyles/`** | Documented in `01-system-overview.md`, `10-full-file-catalog.md`, and (for `native-ts`) `ui-layer/01-ink-engine.md` — outside infrastructure doc set |
| **`workSecret.ts`** line count in `01-bridge-system.md` | Doc says 122 lines; source is **127** (pre-existing; not changed this audit) |
| **`05-context-context.md`** | Empty of buddy/native-ts/outputStyles references; scope overlap with UI layer docs |

---

## Files edited

- `docs/source-code-analysis/infrastructure/01-bridge-system.md` — added `bridgePermissionCallbacks.ts`, `replBridgeHandle.ts`
- `docs/source-code-analysis/infrastructure/02-state-types-constants.md` — corrected `types/permissions.ts` documentation

## Source verification

- All **31** `bridge/*.ts` files inventoried; both audit targets read in full
- All **11** `types/*.ts` files cross-checked against Part 2 of `02-state-types-constants.md`
- Infrastructure directories counted: **691** scoped `.ts`/`.tsx` files (564 in `utils/` delegated to Agent A9)
