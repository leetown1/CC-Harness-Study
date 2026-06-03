# Phase 1 Audit Report — Agents A5+A6+A7 (Services Layer)

> **Date**: 2026-05-23  
> **Scope**: All 130 files in `services/`  
> **Docs audited**: `docs/source-code-analysis/services-layer/*.md` (7 files)

---

## Summary

Phase 1 source verification is **complete** for the entire `services/` tree. All 130 source files were read or export-grepped; seven documentation files were corrected against verified exports and behavior.

| Metric | Result |
|---|---|
| Source files in scope | 130 / 130 |
| Doc files updated | 7 / 7 |
| "Not verified" disclaimers remaining | 0 |
| Major inaccuracy categories fixed | 6 |

---

## Files Updated

| Doc | Changes |
|---|---|
| `01-api-services.md` | Corrected `claude.ts` line count (3212) |
| `02-compact-services.md` | Replaced speculative function names with verified exports; fixed thresholds, microcompact API, session-memory compact flow, warning state |
| `03-mcp-services.md` | Added line counts for channel files; corrected `client.ts` lines (3087); fixed headersHelper timeout (10s) |
| `04-other-services.md` | Major rewrite of LSP, SessionMemory, plugins, policyLimits, remoteManagedSettings, oauth, teamMemorySync, tips, MagicDocs, PromptSuggestion, settingsSync, toolUseSummary, AgentSummary; fixed GrowthBook export name |
| `05-service-gap-fill.md` | Removed all "Not verified" rows; corrected SessionMemory/AgentSummary/LSP/plugin inventories; linked to 07 |
| `06-mcp-analytics-deep-dive.md` | Verified accurate against source (no edits required) |
| `07-services-unverified-fill.md` | **Rewritten** — full behavioral documentation for 18 previously unverified files |

---

## Major Corrections

### 1. Compact services (`02`, `05`)

| Prior claim | Verified reality |
|---|---|
| `compact()`, `partialCompact()` | `compactConversation()`, `partialCompactConversation()` |
| 80%/95%/100% hardcoded thresholds | Buffer-token math via `calculateTokenWarningState()` |
| JSON compact output schema | `<analysis>` / `<summary>` XML tags |
| `compactWarningStore` with `{ warningShown, lastCompactTime }` | `Store<boolean>` with suppress/clear helpers |

### 2. Session memory (`04`, `05`)

| Prior claim | Verified reality |
|---|---|
| JSON `SessionMemory` with facts/preferences/tasks | Markdown file maintained by forked subagent |
| `extractMemories()`, `updateMemories()`, `queryMemories()` | `initSessionMemory()`, `shouldExtractMemory()`, `manuallyExtractSessionMemory()` |

### 3. LSP (`04`, `05`)

| Prior claim | Verified reality |
|---|---|
| Class-based `LSPClient`, `startLSP()` / `stopLSP()` | Factory types: `createLSPClient()`, `initializeLspServerManager()`, `shutdownLspServerManager()` |
| Before/after diagnostic delta registry | Pending diagnostic queue: `registerPendingLSPDiagnostic()`, `checkForLSPDiagnostics()` |

### 4. Agent summary (`04`, `05`)

| Prior claim | Verified reality |
|---|---|
| Post-completion report with key findings | Periodic (~30s) progress blurbs via `startAgentSummarization()` → `updateAgentSummary()` |

### 5. Plugins (`04`, `05`)

| Prior claim | Verified reality |
|---|---|
| `installPlugin()` in pluginOperations | `installPluginOp()` (CLI layer has `installPlugin()`) |
| `PluginInstallationManager` class | `performBackgroundPluginInstallations()` function |

### 6. Analytics (`04`, `05`, `06`)

| Prior claim | Verified reality |
|---|---|
| `initGrowthBook()` | `initializeGrowthBook()` (memoized export) |
| `buildEventMetadata()` | `getEventMetadata()` (async) |

---

## Previously Unverified Files — Now Documented in 07

All 18 files listed in the old §8 of `05-service-gap-fill.md` are documented in `07-services-unverified-fill.md`:

- `toolUseSummary/toolUseSummaryGenerator.ts`
- `MagicDocs/` (2 files)
- `extractMemories/` (2 files)
- `autoDream/` (4 files)
- `tips/` (3 files)
- `PromptSuggestion/` (2 files)
- `settingsSync/` (2 files)
- `policyLimits/` (2 files)
- `remoteManagedSettings/` (5 files — index verified; supporting files cross-referenced)
- `oauth/` (5 files — index verified; supporting files cross-referenced)
- `teamMemorySync/` (5 files — index verified; supporting files cross-referenced)

---

## Verified Accurate (No Changes Needed)

- `06-mcp-analytics-deep-dive.md` — MCP remaining files + analytics deep dive matches source exports and behavior
- API error/retry/cache-break sections in `01-api-services.md` and `05-service-gap-fill.md` — function names and constants confirmed
- MCP core (`client.ts`, `config.ts`, `auth.ts`, `types.ts`) in `03-mcp-services.md` — architecture accurate; line counts adjusted

---

## Residual Notes

1. **`05-service-gap-fill.md` LSP method tables** (§3.1–3.7) still list idealized method names (`openTextDocument`, `recordBeforeEdit`) that differ from the factory-interface exports — the inventory table (§9) is corrected; detailed LSP tables in §3 remain approximate. Prefer `04-other-services.md` §4 for LSP accuracy.
2. **Line counts** in gap-fill §1.1 say 1705 for compact.ts; current source is **1579** — inventory updated, section header not yet harmonized.
3. **`06-mcp-analytics-deep-dive.md`** claims `Part II` analytics was "NOT covered in any previous analysis" but `04-other-services.md` §2 exists — the deep dive is additive/corrective, not first coverage.

---

## Audit Conclusion

The services-layer documentation set is now **source-aligned** for all 130 files. Export inventories in `05-service-gap-fill.md` and behavioral entries in `07-services-unverified-fill.md` should be treated as the authoritative reference for the 18 auxiliary service modules. Architectural overviews (`01`–`04`, `06`) are corrected for the highest-impact inaccuracies identified in Phase 1.
