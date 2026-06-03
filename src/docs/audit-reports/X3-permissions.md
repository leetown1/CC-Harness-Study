# Phase 2 Cross-Cutting Audit — Permissions Chain

**Agent:** X3  
**Date:** 2026-05-23  
**Trace:** `useCanUseTool` → `types/permissions.ts` → `hooks/toolPermission/` → `components/permissions/` UI dialogs  
**Docs audited:** `01-system-overview.md`, `ui-layer/06-permissions-custom-components.md`, `infrastructure/02-state-types-constants.md`, plus cross-refs in `ui-layer/03-hooks.md`, `ui-layer/08-large-hooks.md`, `tool-system/01-overview.md`

---

## Summary

Phase 2 verified the end-to-end permissions chain against source. Core type unions (`PermissionDecisionReason`, `CanUseToolFn` return type) match source after A8 fixes. **`ToolPermissionContext` exists in two shapes** — a cycle-breaking subset in `types/permissions.ts` and the runtime `DeepImmutable` type in `Tool.ts` (adds `isAutoModeAvailable`). One **critical behavioral error** remained in `03-hooks.md` §3.2 (stale placeholder handler descriptions). Line counts in `06-permissions-custom-components.md` drifted ±9–30 lines.

| Check | Status |
|-------|--------|
| `CanUseToolFn` → `Promise<PermissionDecision>` | **Verified** |
| `PermissionDecisionReason` (10 variants) | **Verified** |
| `ToolPermissionContext` field set | **Fixed** — dual-type + missing `isAutoModeAvailable` in infra doc |
| Hook → handler → dialog chain | **Verified** — `03-hooks.md` §3.2 corrected |
| UI dialog routing (`permissionComponentForTool`) | **Verified** in `06-permissions-custom-components.md` |

---

## Chain Trace (Source-Verified)

```
REPL.tsx
  useCanUseTool(setToolUseConfirmQueue, setToolPermissionContext)
    → hasPermissionsToUseTool()          [utils/permissions/permissions.ts]
         reads appState.toolPermissionContext (Tool.ts type)
         converts PermissionResult passthrough → ask before return
    → on 'ask':
         handleCoordinatorPermission       [coordinator workers, awaitAutomatedChecksBeforeDialog]
         handleSwarmWorkerPermission       [swarm workers → leader mailbox]
         speculative bash classifier race  [2s timeout, main agent only]
         handleInteractivePermission       [push ToolUseConfirm → queue]
    → PermissionRequest.tsx               [REPL overlay, permissionComponentForTool()]
         → tool-specific *PermissionRequest components
         → PermissionDialog.tsx            [shared bordered shell]
```

**Wiring:** `screens/REPL.tsx` holds `toolUseConfirmQueue` state, calls `useCanUseTool` at ~L2382, renders `PermissionRequest` when `focusedInputDialog === 'tool-permission'`.

---

## Type Verification

### `CanUseToolFn` (`hooks/useCanUseTool.tsx:27`)

```typescript
export type CanUseToolFn<Input extends Record<string, unknown> = Record<string, unknown>> = (
  tool: ToolType,
  input: Input,
  toolUseContext: ToolUseContext,
  assistantMessage: AssistantMessage,
  toolUseID: string,
  forceDecision?: PermissionDecision<Input>,
) => Promise<PermissionDecision<Input>>
```

- Returns **`PermissionDecision`** (allow | ask | deny), not `PermissionResult`.
- `hasPermissionsToUseTool()` also returns `Promise<PermissionDecision>` after converting internal `passthrough` results to `ask` (`permissions.ts:1299–1310`).
- `forceDecision` bypasses config check when provided (used by tests and forced resolutions).

### `PermissionDecisionReason` (`types/permissions.ts:271–324`)

All 10 discriminated variants confirmed:

| `type` | Payload |
|--------|---------|
| `rule` | `{ rule: PermissionRule }` |
| `mode` | `{ mode: PermissionMode }` |
| `subcommandResults` | `{ reasons: Map<string, PermissionResult> }` |
| `permissionPromptTool` | `{ permissionPromptToolName, toolResult }` |
| `hook` | `{ hookName, hookSource?, reason? }` |
| `asyncAgent` | `{ reason }` |
| `sandboxOverride` | `{ reason: 'excludedCommand' \| 'dangerouslyDisableSandbox' }` |
| `classifier` | `{ classifier, reason }` |
| `workingDir` | `{ reason }` |
| `safetyCheck` | `{ reason, classifierApprovable }` |
| `other` | `{ reason }` |

Note: `PermissionDenyDecision.decisionReason` is **required**; `PermissionAllowDecision.decisionReason` is optional.

### `ToolPermissionContext` — Dual Definition

| Location | Purpose | Fields |
|----------|---------|--------|
| `types/permissions.ts:427–441` | Cycle-breaking type-only module | 10 fields; `ReadonlyMap` for directories; **no** `isAutoModeAvailable` |
| `Tool.ts:123–138` | Runtime app-state type (`DeepImmutable<…>`) | Same 10 + optional **`isAutoModeAvailable`**; `Map` (deep-frozen) for directories |

Runtime code (`PermissionContext.ts`, `permissionSetup.ts`, `PromptInput.tsx`) imports from **`Tool.ts`**. The `types/permissions.ts` shape is a simplified mirror for pure type modules.

**AppState field:** `toolPermissionContext` is a **single nested object** (~11 fields), not "22+ fields" as previously documented.

---

## Issues Found & Fixes Applied

### Critical

| Doc | Issue | Fix |
|-----|-------|-----|
| `ui-layer/03-hooks.md` §3.2 | Described `PermissionContext` as a React rule-engine provider (`checkPermission`, `getRules`, `FileHandler`/`BashHandler`/`WebHandler`) — **does not exist in source** | Replaced with accurate `createPermissionContext` / handler pipeline; points to `06-permissions-custom-components.md` Part 1 |

### Moderate

| Doc | Issue | Fix |
|-----|-------|-----|
| `infrastructure/02-state-types-constants.md` | `ToolPermissionContext` documented only from `types/permissions.ts`; missing `isAutoModeAvailable`; AppState described as "22+ fields" | Dual-type note + runtime field list; corrected AppState description |
| `infrastructure/02-state-types-constants.md` | `types/permissions.ts` line count 441 | Updated to **402** (physical lines) |
| `01-system-overview.md` | Permissions chain not cross-linked | Added one-line chain summary under hooks |

### Minor — Line Count Drift (`06-permissions-custom-components.md`)

| File | Doc (before) | Source |
|------|-------------:|-------:|
| `PermissionContext.ts` | 388 | **379** |
| `permissionLogging.ts` | 238 | **220** |
| `coordinatorHandler.ts` | 65 | **59** |
| `interactiveHandler.ts` | 536 | **506** |
| `swarmWorkerHandler.ts` | 159 | **142** |
| `PermissionRequest.tsx` | 217 | **214** |

---

## Already Correct (No Change)

- `ui-layer/03-hooks.md` §3.1 — `CanUseToolFn` / pipeline (fixed in A10)
- `ui-layer/08-large-hooks.md` §14 — full pipeline diagram
- `ui-layer/06-permissions-custom-components.md` — handler behavior, `ToolUseConfirm`, `permissionComponentForTool` routing
- `tool-system/01-overview.md` — `ToolPermissionContext` includes `isAutoModeAvailable`
- `infrastructure/02-state-types-constants.md` — `PermissionDecisionReason`, `PermissionResult` passthrough variant (fixed in A8)

---

## Files Modified

- `docs/audit-reports/X3-permissions.md` (this report)
- `docs/source-code-analysis/ui-layer/03-hooks.md`
- `docs/source-code-analysis/infrastructure/02-state-types-constants.md`
- `docs/source-code-analysis/ui-layer/06-permissions-custom-components.md`
- `docs/source-code-analysis/01-system-overview.md`

---

## Status

**Phase 2 complete** for permissions cross-cutting chain X3.
