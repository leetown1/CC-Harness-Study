# Command System Gap Fill Analysis

## Table of Contents
1. [commands/plugin/ — 17 files, ~6,400 lines](#1-commandsplugin--17-files-6400-lines)
2. [commands/review/ — 4 files, ~484 lines](#2-commandsreview--4-files-484-lines)
3. [commands/extra-usage/ — 4 files, ~182 lines](#3-commandsextra-usage--4-files-182-lines)
4. [commands/rename/ — 3 files, ~166 lines](#4-commandsrename--3-files-166-lines)
5. [Command File Index — Gap Fill](#5-command-file-index--gap-fill-phase-1-audit)

---

## 1. commands/plugin/ — 17 files, ~6,400 lines

### 1.1 `index.tsx` (11 lines)
**Command registration.** Exports a `Command` object with:
- `type: 'local-jsx'`, `name: 'plugin'`, aliases: `['plugins', 'marketplace']`
- `description: 'Manage Claude Code plugins'`
- `immediate: true` — renders directly in the terminal
- `load: () => import('./plugin.js')` — lazy-loads the entry point

### 1.2 `plugin.tsx` (7 lines)
**Entry point.** Exports `call(onDone, _context, args)` — an async function that renders `<PluginSettings onComplete={onDone} args={args} />`. Delegates everything to PluginSettings.

### 1.3 `PluginSettings.tsx` (1072 lines)
**Root orchestrator component.** Exports `PluginSettings(props: { onComplete, args?, showMcpRedirectMessage? })`.

**Internal components (not exported):**
- `MarketplaceList({ onComplete })` — utility component listing marketplace names
- `McpRedirectBanner()` — stub (returns null)
- `ErrorsTabContent({ setViewState, setActiveTab, markPluginsChanged })` — full errors tab with categorized error rows

**Helper functions (not exported):**
- `getExtraMarketplaceSourceInfo(name)` — checks userSettings/projectSettings/localSettings/policySettings for extraKnownMarketplaces entries
- `buildMarketplaceAction(name)` → `ErrorRowAction` — determines action kind for marketplace errors
- `buildPluginAction(pluginName)` → `ErrorRowAction` — navigate to installed tab for plugin errors
- `isTransientError(error)` — checks if error type is in `TRANSIENT_ERROR_TYPES` (git-auth-failed, git-timeout, network-error)
- `getPluginNameFromError(error)` — extracts plugin name from error's `pluginId`, `plugin`, or `source` field
- `buildErrorRows(...)` — aggregates all error categories into `ErrorRow[]`
- `removeExtraMarketplace(name, sources)` — removes marketplace from extraKnownMarketplaces + associated enabledPlugins from given settings sources
- `getInitialViewState(parsedCommand)` — maps `ParsedCommand` to `ViewState` (help/validate/install/manage/uninstall/enable/disable/marketplace/menu)
- `getInitialTab(viewState)` — maps ViewState to TabId (installed for manage-plugins, marketplaces for manage-marketplaces, else discover)

**Types (not exported):**
- `TabId = 'discover' | 'installed' | 'marketplaces' | 'errors'`
- `ErrorRowAction` — discriminated union: `navigate`, `remove-extra-marketplace`, `remove-installed-marketplace`, `managed-only`, `none`
- `ErrorRow` — `{ label, message, guidance?, action, scope? }`

**Tab structure:** Renders a `<Pane>` with `<Tabs>` containing 4 tabs:
1. **Discover** — either `<BrowseMarketplace>` (when viewState is `browse-marketplace`) or `<DiscoverPlugins>`
2. **Installed** — `<ManagePlugins>` with scoped `targetPlugin`, `targetMarketplace`, `action` from viewState
3. **Marketplaces** — `<ManageMarketplaces>` with scoped `targetMarketplace` and `action`
4. **Errors** — `<ErrorsTabContent>` with dynamic count badge

**View states handled at root level:** `help`, `validate`, `marketplace-menu`, `marketplace-list`, `add-marketplace`. Non-tab view states short-circuit and return their component directly (no tab chrome).

**State management:** Uses `useAppState` / `useSetAppState` for global plugin error/installation state. Local state for `inputValue`, `cursorOffset`, `error`, `result`, `childSearchActive`. Uses `useExitOnCtrlCDWithKeybindings()` for exit handling.

### 1.4 `parseArgs.ts` (103 lines)
**Argument parser.** Exports:
- **`ParsedCommand`** — discriminated union: `menu`, `help`, `install`, `manage`, `uninstall`, `enable`, `disable`, `validate`, `marketplace`
- **`parsePluginArgs(args?)`** — parses string arguments into structured `ParsedCommand`. Handles formats like `plugin@marketplace`, URL/path detection for marketplace targets, all marketplace sub-actions (add/remove/update/list).

### 1.5 `AddMarketplace.tsx` (162 lines)
**Marketplace addition UI.** Exports `AddMarketplace(props)`. States:
- Auto-adds on mount if `inputValue` is pre-filled (from CLI `marketplace add <target>`)
- Loading spinner with progress messages
- Error display
- Result display
- CLI mode: sets result (triggers completion) instead of switching to browse view

**Key flow:** `parseMarketplaceInput` → `addMarketplaceSource` → `saveMarketplaceToSettings` → `clearAllCaches` → analytics `tengu_marketplace_added`.

### 1.6 `BrowseMarketplace.tsx` (802 lines)
**Marketplace plugin browsing UI.** Exports `BrowseMarketplace(props)`. Three main view states:
1. **`marketplace-list`** — select from configured marketplaces (with plugin counts, install counts)
2. **`plugin-list`** — paginated plugin list with multi-select for installation (Space to toggle, i/Enter to install)
3. **`plugin-details`** — plugin metadata + scope-specific install options (user/project/local) + homepage/GitHub links

**Types (not exported):**
- `ViewState` — `marketplace-list | plugin-list | plugin-details | { type: 'plugin-options', plugin, pluginId }`
- `MarketplaceInfo` — `{ name, totalPlugins, installedCount, source? }`

**Key behaviors:**
- Loads marketplaces with graceful degradation (`loadMarketplacesWithGracefulDegradation`)
- Skips marketplace selection if only one marketplace
- Handles `targetMarketplace` and `targetPlugin` navigation from parent
- Sorts by install count (descending) with fetch failure degradation to alphabetical
- Filters out policy-blocked plugins
- Marks only globally installed plugins (user/managed scope) — project/local scope installs don't block
- Multi-select batch install with per-plugin error reporting
- Single install (from details) with automatic `PluginOptionsFlow` if plugin needs config
- `PluginSelectionKeyHint` from `pluginDetailsHelpers.tsx`

### 1.7 `DiscoverPlugins.tsx` (781 lines)
**Cross-marketplace plugin discovery UI.** Exports `DiscoverPlugins(props)`. View states:
1. **`plugin-list`** — searchable, paginated unified list of ALL plugins from ALL marketplaces
2. **`plugin-details`** — plugin metadata + install options

**Types (not exported):**
- `ViewState` — `plugin-list | plugin-details | { type: 'plugin-options', plugin, pluginId }`

**Key differences from BrowseMarketplace:**
- Aggregates plugins across ALL marketplaces, not just one
- Has inline search via `useSearchInput` + `useInput` for `'/'` and printable characters
- Shows marketplace name per plugin entry
- Install counts only for official marketplace
- `EmptyStateMessage` component with context-aware messages: `git-not-installed`, `all-blocked-by-policy`, `policy-restricts-sources`, `all-marketplaces-failed`, `all-plugins-installed`, `no-marketplaces-configured`
- `DiscoverPluginsKeyHint` — optimized with React compiler (`_c`)

### 1.8 `ManagePlugins.tsx` (2215 lines)
**Installed plugin management UI.** Exports:
- **`filterManagedDisabledPlugins(plugins)`** — filters out policy-blocked plugins
- **`ManagePlugins(props)`** — the main component

**Internal components (not exported):**
- `getBaseFileNames(dirPath)` — reads `.md` file names from a commands/agents directory
- `getSkillDirNames(dirPath)` — scans for `SKILL.md` directories
- `PluginComponentsDisplay({ plugin, marketplace })` — async component that reads filesystem to list commands/agents/skills/hooks/MCP servers for an installed plugin

**Helper functions (not exported):**
- `checkIfLocalPlugin(pluginName, marketplaceName)` — returns error if plugin source is local string
- `getMcpStatus(client)` — maps `MCPServerConnection.type` to status string

**Types (not exported):**
- `FlaggedPluginInfo` — `{ id, name, marketplace, reason, text, flaggedAt }`
- `FailedPluginInfo` — `{ id, name, marketplace, errors, scope }`
- `ViewState` — union of 12+ states: `plugin-list`, `plugin-details`, `configuring`, `plugin-options`, `configuring-options`, `confirm-project-uninstall`, `confirm-data-cleanup`, `flagged-detail`, `failed-plugin-details`, `mcp-detail`, `mcp-tools`, `mcp-tool-detail`
- `MarketplaceInfo` — `{ name, installedPlugins, enabledCount?, disabledCount? }`
- `PluginState` — `{ plugin, marketplace, scope?, pendingEnable?, pendingUpdate? }`

**View states managed:**
1. **`plugin-list`** — unified list of installed plugins, failed plugins, flagged plugins, MCP servers grouped by scope (flagged, project, local, user, enterprise, managed, builtin, dynamic); searchable, paginated
2. **`plugin-details`** — plugin metadata, version, scope, status, installed components (from filesystem), errors, operations menu (enable/disable/mark-for-update/configure/configure-options/update-now/uninstall/homepage/repository)
3. **`plugin-options`** — post-enable config via `<PluginOptionsFlow>`
4. **`configuring-options`** — independent config editing via `<PluginOptionsDialog>`
5. **`configuring`** — MCPB config via `<PluginOptionsDialog>`
6. **`confirm-project-uninstall`** — warns about shared `.claude/settings.json`, offers disable in `settings.local.json`
7. **`confirm-data-cleanup`** — prompts before deleting `${CLAUDE_PLUGIN_DATA}` on uninstall
8. **`flagged-detail`** — shows delisted plugin info, dismiss option
9. **`failed-plugin-details`** — shows plugin load error, remove option (with V2 uninstall fallback to settings cleanup)
10. **`mcp-detail`** — MCP server detail with transport-specific `<MCPStdioServerMenu>` or `<MCPRemoteServerMenu>`
11. **`mcp-tools`** — tool list via `<MCPToolListView>`
12. **`mcp-tool-detail`** — tool detail via `<MCPToolDetailView>`

**Key behaviors:**
- Merges plugin states, MCP clients, plugin errors, and flagged plugins into `unifiedItems` using `useMemo`
- Groups by scope with proper `scopeOrder`
- Child MCPs (prefixed `plugin:name:server`) indented under parent plugin
- Orphan errors (failed-to-load plugins) become `failed-plugin` items
- Pending toggle operations (enable/disable) execute immediately but track state for reload reminder
- `pendingAutoActionRef` enables auto-executing actions (`/plugin enable/disable/uninstall <name>`)
- `confirm-data-cleanup` uses raw `useInput` (not keybindings) to avoid accidental destructive Enter behavior
- Handles MCPB detection from both manifest and raw marketplace.json (backward compat)

### 1.9 `ManageMarketplaces.tsx` (838 lines)
**Marketplace management UI.** Exports `ManageMarketplaces(props)`. Internal view states:
1. **`list`** — shows all marketplaces with source, plugin count, install count, last-updated; supports u/r keyboard shortcuts for update/remove; batch operations with pending changes summary
2. **`details`** — marketplace details with menu: Browse plugins, Update, toggle auto-update, Remove
3. **`confirm-remove`** — warning dialog listing plugins to be uninstalled, y/n confirmation

**Types (not exported):**
- `MarketplaceState` — `{ name, source, lastUpdated?, pluginCount?, installedPlugins?, pendingUpdate?, pendingRemove?, autoUpdate? }`
- `InternalViewState = 'list' | 'details' | 'confirm-remove'`

**Helper functions (not exported):**
- `hasPendingChanges()` / `getPendingCounts()` — checks pending operations
- `applyChanges(states?)` — executes all pending updates/removes; handles plugin uninstall, marketplace removal, refresh, plugin version bumping via `updatePluginsForMarketplaces`
- `confirmRemove()` — marks selected marketplace for removal and applies
- `buildDetailsMenuOptions(marketplace)` — constructs details menu with conditional auto-update toggle
- `handleToggleAutoUpdate(marketplace)` — toggles marketplace auto-update setting

**Key behaviors:**
- `claude-plugin-directory` always sorted first
- Auto-executes actions when `targetMarketplace` + `action` provided (update/remove)
- Manages `known_marketplaces.json` via `marketplaceManager` utils
- After updates, bumps installed plugins to new version via `updatePluginsForMarketplaces`
- Props include `exitState` for Ctrl-C/D double-press back behavior

### 1.10 `PluginErrors.tsx` (124 lines)
**Error formatting utilities.** Exports:
- **`formatErrorMessage(error: PluginError)`** — converts every `PluginError` type discriminant to human-readable string. Covers: `path-not-found`, `git-auth-failed`, `git-timeout`, `network-error`, `manifest-parse-error`, `manifest-validation-error`, `plugin-not-found`, `marketplace-not-found`, `marketplace-load-failed`, `mcp-config-invalid`, `mcp-server-suppressed-duplicate`, `hook-load-failed`, `component-load-failed`, `mcpb-download-failed`, `mcpb-extract-failed`, `mcpb-invalid-manifest`, `marketplace-blocked-by-policy`, `dependency-unsatisfied`, `lsp-config-invalid`, `lsp-server-start-failed`, `lsp-server-crashed`, `lsp-request-timeout`, `lsp-request-failed`, `plugin-cache-miss`, `generic-error`. Has exhaustiveness check at end.
- **`getErrorGuidance(error: PluginError)`** — returns actionable guidance string or null for each error type. Handles `mcp-server-suppressed-duplicate` by analyzing `duplicateOf` prefix.

### 1.11 `PluginOptionsDialog.tsx` (357 lines)
**Interactive option configuration dialog.** Exports:
- **`buildFinalValues(fields, collected, configSchema, initialValues)`** — converts collected string inputs to typed `PluginOptionValues`. Handles: sensitive fields (omit blank if initial value exists), number type (skip blank, parse), boolean type (`isEnvTruthy`), string type.
- **`PluginOptionsDialog(props)`** — multi-field walk-through dialog using `<Dialog>`.

**Key behaviors:**
- Iterates through fields one at a time (Tab/Enter to advance)
- Sensitive fields are never prepopulated from initial values
- Backspace deletes characters, printable characters type
- Uses `stringWidth` for asterisk masking of sensitive input
- `initialFor` function builds per-field initial value ("" for sensitive, String(v) otherwise)
- Uses React compiler (`_c`) for memoization

### 1.12 `PluginOptionsFlow.tsx` (135 lines)
**Post-install/post-enable configuration flow.** Exports:
- **`findPluginOptionsTarget(pluginId)`** — async lookup: loads all plugins, finds one matching by `repository` or `source`. Returns `LoadedPlugin | undefined`.
- **`PluginOptionsFlow({ plugin, pluginId, onDone })`** — walks through config steps.

**Types (not exported):**
- `ConfigStep` — `{ key, title, subtitle, schema, load, save }`

**Key behaviors:**
- Builds step list at mount: top-level `manifest.userConfig` first, then per-channel `userConfig` (assistant modes)
- `getUnconfiguredOptions` + `getUnconfiguredChannels` determine what needs filling
- Calls `onDone('skipped')` immediately if nothing to configure
- Uses `key` prop to force remount `<PluginOptionsDialog>` on step advance (prevents stale internal state)
- `useRef` for latest `onDone` to avoid effect re-runs
- Outcome: `configured`, `skipped`, `error`

### 1.13 `PluginTrustWarning.tsx` (32 lines)
**Security notice component.** Exports `PluginTrustWarning()` — renders a static warning about trusting plugins before installing. Uses `getPluginTrustMessage()` for optional custom message. Memoized with React compiler.

### 1.14 `ValidatePlugin.tsx` (98 lines)
**Plugin manifest validation UI.** Exports `ValidatePlugin({ onComplete, path? })` — runs `validateManifest(path)` async, formats output with errors/warnings/success. Sets `process.exitCode` for CLI usage. Shows usage text if no path provided.

### 1.15 `UnifiedInstalledCell.tsx` (565 lines)
**Render cell for installed items.** Exports `UnifiedInstalledCell({ item, isSelected })` — renders a single row for any `UnifiedInstalledItem` type:
- **`plugin` type**: Shows icon (tick/disabled/error/pending-toggle) + name + marketplace + status text
- **`flagged-plugin` type**: Warning icon + name + marketplace + "removed" text
- **`failed-plugin` type**: Error icon + name + marketplace + "failed to load · N errors"
- **`mcp` type** (standalone or indented child): Status icon (connected/disabled/pending/needs-auth/failed) + name + status text
- Uses `useTheme()` and `color()` for theme-aware icons
- Uses React compiler (`_c`) extensively for memoization

### 1.16 `pluginDetailsHelpers.tsx` (117 lines)
**Shared plugin details utilities.** Exports:
- **`InstallablePlugin`** type — `{ entry: PluginMarketplaceEntry, marketplaceName, pluginId, isInstalled }`
- **`PluginDetailsMenuOption`** type — `{ label, action }`
- **`extractGitHubRepo(plugin)`** — extracts GitHub `repo` from plugin source object
- **`buildPluginDetailsMenuOptions(hasHomepage, githubRepo)`** — builds menu: install-user, install-project, install-local, homepage (conditional), github (conditional), back
- **`PluginSelectionKeyHint({ hasSelection })`** — keybinding hint component for browse/discover screens

### 1.17 `usePagination.ts` (171 lines)
**Pagination hook.** Exports `usePagination<T>({ totalItems, maxVisible?, selectedIndex? })`.

**Returns `UsePaginationResult<T>`:**
- `currentPage`, `totalPages`, `startIndex`, `endIndex`, `needsPagination`, `pageSize`
- `getVisibleItems(items)` — slices items for current scroll window
- `toActualIndex(visibleIndex)` — converts visible to absolute index
- `isOnCurrentPage(actualIndex)` — visibility check
- `goToPage(page)`, `nextPage()`, `prevPage()` — no-ops (continuous scrolling)
- `handleSelectionChange(newIndex, setSelectedIndex)` — clamps and updates index
- `handlePageNavigation(direction, setSelectedIndex)` — returns false (no page-based nav)
- `scrollPosition` — `{ current, total, canScrollUp, canScrollDown }`

**Algorithm:** Continuous scrolling via `scrollOffsetRef`. If selectedIndex moves above visible window → scroll up; below → scroll down; otherwise keep offset. Uses `useRef` for smooth transitions.

---

## 2. commands/review/ — 4 files, ~484 lines

### 2.1 `ultrareviewEnabled.ts` (14 lines)
**Feature gate.** Exports `isUltrareviewEnabled()` — reads `tengu_review_bughunter_config` from GrowthBook and returns `cfg?.enabled === true`. Controls command visibility.

### 2.2 `reviewRemote.ts` (316 lines)
**Remote review execution.** Exports:
- **`confirmOverage()`** — sets `sessionOverageConfirmed = true` (in-memory flag per session)
- **`OverageGate`** — discriminated union: `proceed`, `not-enabled`, `low-balance`, `needs-confirm`
- **`checkOverageGate()`** — async quota/usage check:
  - Team/Enterprise → proceed (no billing note)
  - Fetch quota + utilization in parallel
  - Has free reviews → proceed with count
  - No quota info → proceed (server-side billing)
  - Free exhausted, Extra Usage not enabled → `not-enabled`
  - Free exhausted, balance < $10 → `low-balance`
  - Free exhausted, not yet confirmed → `needs-confirm`
  - Free exhausted, confirmed → proceed with billing note
- **`launchRemoteReview(args, context, billingNote?)`** — creates CCR session for remote review:
  - PR mode (`args` is a number): Uses `teleportToRemote` with `refs/pull/N/head`, sets `BUGHUNTER_PR_NUMBER` and `BUGHUNTER_REPOSITORY`
  - Branch mode: Finds merge-base with default branch, checks for non-empty diff, uses `teleportToRemote` with `useBundle: true`, sets `BUGHUNTER_BASE_BRANCH`
  - Configures bug hunter env vars from GrowthBook (`tengu_review_bughunter_config`): `fleet_size`, `max_duration_minutes`, `agent_timeout_seconds`, `total_wallclock_minutes` with safe defaults and upper bounds (27min wallclock)
  - Uses `CODE_REVIEW_ENV_ID = 'env_011111111111111111111113'`
  - Returns `ContentBlockParam[]` for model narration or null on failure
  - Registers `RemoteAgentTask` for polling results

### 2.3 `ultrareviewCommand.tsx` (58 lines)
**Command implementation.** Exports `call(onDone, context, args)` — the `LocalJSXCommandCall` function.

**Internal functions:**
- `contentBlocksToString(blocks)` — extracts text from `ContentBlockParam[]`
- `launchAndDone(args, context, onDone, billingNote, signal?)` — calls `launchRemoteReview`, handles abort signal (Escape during launch), calls `onDone` with result or error message

**Flow:**
1. `checkOverageGate()` → gate decision
2. `not-enabled` → system message about enabling Extra Usage
3. `low-balance` → system message with available balance
4. `needs-confirm` → renders `<UltrareviewOverageDialog>`, on proceed calls `launchAndDone` then `confirmOverage()` (only on non-aborted launch)
5. `proceed` → `launchAndDone` directly

### 2.4 `UltrareviewOverageDialog.tsx` (96 lines)
**Billing confirmation dialog.** Exports `UltrareviewOverageDialog({ onProceed, onCancel })`:
- Shows billing info text + `<Select>` with "Proceed with Extra Usage billing" / "Cancel"
- Uses `<AbortController>` ref for cancellation during launch
- `handleSelect('proceed')` → sets launching state, calls `onProceed(signal)`, catches errors to restore select
- `handleCancel()` → aborts controller, calls `onCancel`

---

## 3. commands/extra-usage/ — 4 files, ~182 lines

### 3.1 `index.ts` (31 lines)
**Dual command registration.** Exports two `Command` objects:
- **`extraUsage`** — `local-jsx`, enabled when not in non-interactive session + overage provisioning allowed + not disabled by `DISABLE_EXTRA_USAGE_COMMAND` env var
- **`extraUsageNonInteractive`** — `local`, enabled only in non-interactive sessions, `isHidden` computed getter

Both check `isExtraUsageAllowed()` which verifies `isOverageProvisioningAllowed()` and `DISABLE_EXTRA_USAGE_COMMAND`.

### 3.2 `extra-usage-core.ts` (118 lines)
**Core logic.** Exports `runExtraUsage()` → `ExtraUsageResult` (`{ type: 'message', value }` or `{ type: 'browser-opened', url, opened }`).

**Flow:**
1. Marks `hasVisitedExtraUsage` in global config
2. Invalidates overage credit grant cache
3. For **Team/Enterprise** users without billing access:
   - Checks if unlimited overage already enabled → return message
   - Checks admin request eligibility
   - Checks for existing pending/dismissed requests
   - Creates admin request via `createAdminRequest`
   - Falls through to generic "contact admin" on errors
4. For all others (Pro/Max/have billing access):
   - Opens browser to `claude.ai/settings/usage` or `claude.ai/admin-settings/usage`
   - Returns `browser-opened` result

### 3.3 `extra-usage.tsx` (17 lines)
**Interactive JSX command.** Exports `call(onDone, context)` — calls `runExtraUsage()`, if result is `message` → calls `onDone` and returns null; if `browser-opened` → renders `<Login>` component with starting message about new login flow, calls `context.onChangeAPIKey()` on login success.

### 3.4 `extra-usage-noninteractive.ts` (16 lines)
**Non-interactive command.** Exports `call()` — calls `runExtraUsage()`, returns `{ type: 'text', value }` with appropriate browser URL message.

---

## 4. commands/rename/ — 3 files, ~166 lines

### 4.1 `index.ts` (12 lines)
**Command registration.** Exports `rename` Command object with `type: 'local-jsx'`, `name: 'rename'`, `argumentHint: '[name]'`, `immediate: true`.

### 4.2 `rename.ts` (87 lines)
**Command implementation.** Exports `call(onDone, context, args)`:
1. Prevents teammates from renaming (names set by team leader)
2. If no args → calls `generateSessionName()` using conversation context
3. If args → uses `args.trim()` as new name
4. Saves custom title via `saveCustomTitle()`
5. Syncs to bridge session via `updateBridgeSessionTitle()` (best-effort, non-blocking)
6. Saves agent name via `saveAgentName()`
7. Updates app state `standaloneAgentContext.name`

### 4.3 `generateSessionName.ts` (67 lines)
**AI name generation.** Exports `generateSessionName(messages, signal)`:
1. Extracts conversation text via `extractConversationText()`
2. Returns null if no conversation context
3. Calls `queryHaiku()` with JSON schema output format requesting kebab-case name (2-4 words)
4. Falls back to null on Haiku failure (uses `logForDebugging`, not `logError`)
5. Parses JSON response with `safeParseJSON()`

---

## 5. Command File Index — Gap Fill (Phase 1 Audit)

> Auto-generated behavior-level entries for command implementation files lacking dedicated `###` sections in prior docs. Line counts verified against source on 2026-05-23.
>
> **Type field convention:** Entries use `commandType` for the slash-command discriminant (`prompt` / `local` / `local-jsx` from `Command.type`). Implementation files that return synchronously use `returns` for `LocalCommandResult.type` (`text`, `compact`, `skip`) — not the command type. UI state machine types (e.g. `checking` in remote-setup) are noted separately.

### 5.1 `commands/add-dir/` — 2 files, 236 lines

#### 5.1.1 `commands/add-dir/add-dir.tsx` (126 lines)
- Internal UI state includes `addDirectories` picker flow
- Exports `call()` — command entry point (lazy-loaded by index)
- **Exports:** `call`

#### 5.1.2 `commands/add-dir/validation.ts` (110 lines)
- **Exports:** `AddDirectoryResult`, `validateDirectoryForWorkspace`, `addDirHelpMessage`

### 5.2 `commands/advisor.ts/` — 1 files, 109 lines

#### 5.2.1 `commands/advisor.ts` (109 lines)
- `name`: `advisor`
- `commandType`: `local`
- `returns`: `{ type: 'text' }`
- `description`: `Configure the advisor model`
- `argumentHint`: `[<model>|off]`
- `supportsNonInteractive`: `true`
- Gated by `canUserConfigureAdvisor()`

### 5.3 `commands/agents/` — 1 files, 12 lines

#### 5.3.1 `commands/agents/agents.tsx` (12 lines)
- Exports `call()` — command entry point (lazy-loaded by index)
- **Exports:** `call`

### 5.4 `commands/branch/` — 1 files, 296 lines

#### 5.4.1 `commands/branch/branch.ts` (296 lines)
- `commandType`: `local-jsx` (via `commands/branch/index.ts`)
- Exports `call()` — command entry point (lazy-loaded by index)
- **Exports:** `deriveFirstPrompt`, `call`

### 5.5 `commands/bridge/` — 1 files, 509 lines

#### 5.5.1 `commands/bridge/bridge.tsx` (509 lines)
- `commandType`: `local-jsx` (via `commands/bridge/index.ts`, name `remote-control`)
- Exports `call()` — command entry point (lazy-loaded by index)
- **Exports:** `call`

### 5.6 `commands/bridge-kick.ts/` — 1 files, 200 lines

#### 5.6.1 `commands/bridge-kick.ts` (200 lines)
- `name`: `bridge-kick`
- `commandType`: `local`
- `returns`: `{ type: 'text' }`
- `description`: `Inject bridge failure states for manual recovery testing`
- **ANT-only** (`INTERNAL_ONLY_COMMANDS`)

### 5.7 `commands/brief.ts/` — 1 files, 130 lines

#### 5.7.1 `commands/brief.ts` (130 lines)
- `name`: `brief`
- `commandType`: `local-jsx`
- `description`: `Toggle brief-only mode`
- **Feature:** `KAIROS` or `KAIROS_BRIEF`; gated by GrowthBook `tengu_kairos_brief_config.enable_slash_command`
- Defines Zod input/output schemas

### 5.8 `commands/btw/` — 1 files, 243 lines

#### 5.8.1 `commands/btw/btw.tsx` (243 lines)
- Exports `call()` — command entry point (lazy-loaded by index)
- **Exports:** `call`

### 5.9 `commands/chrome/` — 1 files, 285 lines

#### 5.9.1 `commands/chrome/chrome.tsx` (285 lines)
- **Exports:** `call`

### 5.10 `commands/clear/` — 3 files, 402 lines

#### 5.10.1 `commands/clear/caches.ts` (144 lines)
- **Exports:** `clearSessionCaches`

#### 5.10.2 `commands/clear/clear.ts` (7 lines)
- `commandType`: `local` (via `commands/clear/index.ts`)
- `returns`: `{ type: 'text' }` or triggers `clearConversation()`
- **Exports:** `call`

#### 5.10.3 `commands/clear/conversation.ts` (251 lines)
- **Exports:** `clearConversation`

### 5.11 `commands/color/` — 1 files, 93 lines

#### 5.11.1 `commands/color/color.ts` (93 lines)
- Exports `call()` — command entry point (lazy-loaded by index)
- **Exports:** `call`

### 5.12 `commands/commit-push-pr.ts/` — 1 files, 158 lines

#### 5.12.1 `commands/commit-push-pr.ts` (158 lines)
- `name`: `commit-push-pr`
- `commandType`: `prompt`
- `description`: `Commit, push, and open a PR`
- Generates prompt text for model invocation

### 5.13 `commands/commit.ts/` — 1 files, 92 lines

#### 5.13.1 `commands/commit.ts` (92 lines)
- `name`: `commit`
- `commandType`: `prompt`
- `description`: `Create a git commit`
- Generates prompt text for model invocation

### 5.14 `commands/compact/` — 1 files, 287 lines

#### 5.14.1 `commands/compact/compact.ts` (287 lines)
- `commandType`: `local` (via `commands/compact/index.ts`)
- `returns`: `{ type: 'compact' }` or `{ type: 'skip' }`
- **Exports:** `call`

### 5.15 `commands/config/` — 1 files, 7 lines

#### 5.15.1 `commands/config/config.tsx` (7 lines)
- **Exports:** `call`

### 5.16 `commands/context/` — 2 files, 389 lines

#### 5.16.1 `commands/context/context-noninteractive.ts` (325 lines)
- `commandType`: `local` (via `contextNonInteractive` in `commands/context/index.ts`)
- `returns`: `{ type: 'text' }`
- Exports `call()` — command entry point (lazy-loaded by index)
- **Exports:** `collectContextData`, `call`

#### 5.16.2 `commands/context/context.tsx` (64 lines)
- Exports `call()` — command entry point (lazy-loaded by index)
- **Exports:** `call`

### 5.17 `commands/copy/` — 1 files, 371 lines

#### 5.17.1 `commands/copy/copy.tsx` (371 lines)
- `name`: `copy${fileExtension(block_0.lang)}`
- `description`: `Skip this picker in the future (revert via /config)`
- **Exports:** `collectRecentAssistantTexts`, `fileExtension`, `call`

### 5.18 `commands/cost/` — 1 files, 24 lines

#### 5.18.1 `commands/cost/cost.ts` (24 lines)
- `commandType`: `local` (via `commands/cost/index.ts`)
- `returns`: `{ type: 'text' }`
- **Exports:** `call`

### 5.19 `commands/createMovedToPluginCommand.ts/` — 1 files, 65 lines

#### 5.19.1 `commands/createMovedToPluginCommand.ts` (65 lines)
- `commandType`: `prompt` (factory)
- Generates prompt text for model invocation
- **Exports:** `createMovedToPluginCommand`

### 5.20 `commands/desktop/` — 1 files, 9 lines

#### 5.20.1 `commands/desktop/desktop.tsx` (9 lines)
- Exports `call()` — command entry point (lazy-loaded by index)
- **Exports:** `call`

### 5.21 `commands/diff/` — 1 files, 9 lines

#### 5.21.1 `commands/diff/diff.tsx` (9 lines)
- **Exports:** `call`

### 5.22 `commands/doctor/` — 1 files, 7 lines

#### 5.22.1 `commands/doctor/doctor.tsx` (7 lines)
- **Exports:** `call`

### 5.23 `commands/effort/` — 1 files, 183 lines

#### 5.23.1 `commands/effort/effort.tsx` (183 lines)
- Exports `call()` — command entry point (lazy-loaded by index)
- **Exports:** `showCurrentEffort`, `executeEffort`, `call`

### 5.24 `commands/exit/` — 1 files, 33 lines

#### 5.24.1 `commands/exit/exit.tsx` (33 lines)
- Exports `call()` — command entry point (lazy-loaded by index)
- **Exports:** `call`

### 5.25 `commands/export/` — 1 files, 91 lines

#### 5.25.1 `commands/export/export.tsx` (91 lines)
- Exports `call()` — command entry point (lazy-loaded by index)
- **Exports:** `extractFirstPrompt`, `sanitizeFilename`, `call`

### 5.26 `commands/fast/` — 1 files, 269 lines

#### 5.26.1 `commands/fast/fast.tsx` (269 lines)
- Exports `call()` — command entry point (lazy-loaded by index)
- **Exports:** `FastModePicker`, `call`

### 5.27 `commands/feedback/` — 1 files, 25 lines

#### 5.27.1 `commands/feedback/feedback.tsx` (25 lines)
- Exports `call()` — command entry point (lazy-loaded by index)
- **Exports:** `renderFeedbackComponent`, `call`

### 5.28 `commands/files/` — 1 files, 19 lines

#### 5.28.1 `commands/files/files.ts` (19 lines)
- `commandType`: `local` (via `commands/files/index.ts`)
- `returns`: `{ type: 'text' }`
- Exports `call()` — command entry point (lazy-loaded by index)
- **Exports:** `call`

### 5.29 `commands/heapdump/` — 1 files, 17 lines

#### 5.29.1 `commands/heapdump/heapdump.ts` (17 lines)
- `commandType`: `local` (via `commands/heapdump/index.ts`)
- `returns`: `{ type: 'text' }`
- Exports `call()` — command entry point (lazy-loaded by index)
- **Exports:** `call`

### 5.30 `commands/help/` — 1 files, 11 lines

#### 5.30.1 `commands/help/help.tsx` (11 lines)
- **Exports:** `call`

### 5.31 `commands/hooks/` — 1 files, 13 lines

#### 5.31.1 `commands/hooks/hooks.tsx` (13 lines)
- **Exports:** `call`

### 5.32 `commands/ide/` — 1 files, 646 lines

#### 5.32.1 `commands/ide/ide.tsx` (646 lines)
- Exports `call()` — command entry point (lazy-loaded by index)
- **Exports:** `call`, `formatWorkspaceFolders`

### 5.33 `commands/init-verifiers.ts/` — 1 files, 262 lines

#### 5.33.1 `commands/init-verifiers.ts` (262 lines)
- `name`: `init-verifiers`
- `commandType`: `prompt`
- `description`: `Create verifier skill(s) for automated verification of code changes`
- Generates prompt text for model invocation

### 5.34 `commands/init.ts/` — 1 files, 256 lines

#### 5.34.1 `commands/init.ts` (256 lines)
- `name`: `init`
- `commandType`: `prompt`
- Generates prompt text for model invocation

### 5.35 `commands/insights.ts/` — 1 files, 3200 lines

#### 5.35.1 `commands/insights.ts` (3200 lines)
- `name`: `insights` (registered via lazy shim in `commands.ts`; also exports default `usageReport` Command)
- `commandType`: `prompt`
- `description`: `Generate a report analyzing your Claude Code sessions`
- Internal report section IDs include `project_areas`, `interaction_style`, `what_works`, etc.
- Generates prompt text for model invocation
- **Exports:** `deduplicateSessionBranches`, `detectMultiClauding`, `InsightsExport`, `buildExportData`, `generateUsageReport`

### 5.36 `commands/install-github-app/` — 13 files, 2351 lines

#### 5.36.1 `commands/install-github-app/ApiKeyStep.tsx` (231 lines)
- **Exports:** `ApiKeyStep`

#### 5.36.2 `commands/install-github-app/CheckExistingSecretStep.tsx` (190 lines)
- **Exports:** `CheckExistingSecretStep`

#### 5.36.3 `commands/install-github-app/CheckGitHubStep.tsx` (15 lines)
- **Exports:** `CheckGitHubStep`

#### 5.36.4 `commands/install-github-app/ChooseRepoStep.tsx` (211 lines)
- **Exports:** `ChooseRepoStep`

#### 5.36.5 `commands/install-github-app/CreatingStep.tsx` (65 lines)
- **Exports:** `CreatingStep`

#### 5.36.6 `commands/install-github-app/ErrorStep.tsx` (85 lines)
- **Exports:** `ErrorStep`

#### 5.36.7 `commands/install-github-app/ExistingWorkflowStep.tsx` (103 lines)
- **Exports:** `ExistingWorkflowStep`

#### 5.36.8 `commands/install-github-app/InstallAppStep.tsx` (94 lines)
- **Exports:** `InstallAppStep`

#### 5.36.9 `commands/install-github-app/OAuthFlowStep.tsx` (276 lines)
- **Exports:** `OAuthFlowStep`

#### 5.36.10 `commands/install-github-app/SuccessStep.tsx` (96 lines)
- **Exports:** `SuccessStep`

#### 5.36.11 `commands/install-github-app/WarningsStep.tsx` (73 lines)
- **Exports:** `WarningsStep`

#### 5.36.12 `commands/install-github-app/install-github-app.tsx` (587 lines)
- Exports `call()` — command entry point (lazy-loaded by index)
- **Exports:** `call`

#### 5.36.13 `commands/install-github-app/setupGitHubActions.ts` (325 lines)
- **Exports:** `setupGitHubActions`

### 5.37 `commands/install-slack-app/` — 1 files, 30 lines

#### 5.37.1 `commands/install-slack-app/install-slack-app.ts` (30 lines)
- `commandType`: `local` (via `commands/install-slack-app/index.ts`)
- `returns`: `{ type: 'text' }`
- Exports `call()` — command entry point (lazy-loaded by index)
- **Exports:** `call`

### 5.38 `commands/install.tsx/` — 1 files, 300 lines

#### 5.38.1 `commands/install.tsx` (300 lines)
- `name`: `install`
- `commandType`: `local-jsx` (export shape only — **not registered in `commands.ts` / `getCommands()`**)
- `description`: `Install Claude Code native build`
- `argumentHint`: `[options]`
- Used from `cli.tsx` only; UI state machine includes `checking`, `installing`, `success`, `error`
- **Exports:** `install`

### 5.39 `commands/keybindings/` — 1 files, 53 lines

#### 5.39.1 `commands/keybindings/keybindings.ts` (53 lines)
- `commandType`: `local` (via `commands/keybindings/index.ts`)
- `returns`: `{ type: 'text' }`
- Exports `call()` — command entry point (lazy-loaded by index)
- **Exports:** `call`

### 5.40 `commands/login/` — 1 files, 104 lines

#### 5.40.1 `commands/login/login.tsx` (104 lines)
- Exports `call()` — command entry point (lazy-loaded by index)
- **Exports:** `call`, `Login`

### 5.41 `commands/logout/` — 1 files, 82 lines

#### 5.41.1 `commands/logout/logout.tsx` (82 lines)
- Exports `call()` — command entry point (lazy-loaded by index)
- **Exports:** `performLogout`, `clearAuthRelatedCaches`, `call`

### 5.42 `commands/mcp/` — 3 files, 631 lines

#### 5.42.1 `commands/mcp/addCommand.ts` (280 lines)
- Registers MCP server add subcommand; transport types include `sse`, `stdio`, `http`
- **Exports:** `registerMcpAddCommand`

#### 5.42.2 `commands/mcp/mcp.tsx` (85 lines)
- Exports `call()` — command entry point (lazy-loaded by index)
- **Exports:** `call`

#### 5.42.3 `commands/mcp/xaaIdpCommand.ts` (266 lines)
- **Exports:** `registerMcpXaaIdpCommand`

### 5.43 `commands/memory/` — 1 files, 90 lines

#### 5.43.1 `commands/memory/memory.tsx` (90 lines)
- **Exports:** `call`

### 5.44 `commands/mobile/` — 1 files, 274 lines

#### 5.44.1 `commands/mobile/mobile.tsx` (274 lines)
- `commandType`: `local-jsx` (via `commands/mobile/index.ts`)
- QR payload encoding uses UTF-8
- Exports `call()` — command entry point (lazy-loaded by index)
- **Exports:** `call`

### 5.45 `commands/model/` — 1 files, 297 lines

#### 5.45.1 `commands/model/model.tsx` (297 lines)
- **Exports:** `call`

### 5.46 `commands/output-style/` — 1 files, 7 lines

#### 5.46.1 `commands/output-style/output-style.tsx` (7 lines)
- Exports `call()` — command entry point (lazy-loaded by index)
- **Exports:** `call`

### 5.47 `commands/passes/` — 1 files, 24 lines

#### 5.47.1 `commands/passes/passes.tsx` (24 lines)
- Exports `call()` — command entry point (lazy-loaded by index)
- **Exports:** `call`

### 5.48 `commands/permissions/` — 1 files, 10 lines

#### 5.48.1 `commands/permissions/permissions.tsx` (10 lines)
- **Exports:** `call`

### 5.49 `commands/plan/` — 1 files, 122 lines

#### 5.49.1 `commands/plan/plan.tsx` (122 lines)
- `commandType`: `local-jsx` (via `commands/plan/index.ts`)
- Internal handler uses `setMode` to toggle plan mode
- Exports `call()` — command entry point (lazy-loaded by index)
- **Exports:** `call`

### 5.50 `commands/privacy-settings/` — 1 files, 58 lines

#### 5.50.1 `commands/privacy-settings/privacy-settings.tsx` (58 lines)
- Exports `call()` — command entry point (lazy-loaded by index)
- **Exports:** `call`

### 5.51 `commands/rate-limit-options/` — 1 files, 210 lines

#### 5.51.1 `commands/rate-limit-options/rate-limit-options.tsx` (210 lines)
- Exports `call()` — command entry point (lazy-loaded by index)
- **Exports:** `call`

### 5.52 `commands/release-notes/` — 1 files, 50 lines

#### 5.52.1 `commands/release-notes/release-notes.ts` (50 lines)
- `commandType`: `local` (via `commands/release-notes/index.ts`)
- `returns`: `{ type: 'text' }`
- Exports `call()` — command entry point (lazy-loaded by index)
- **Exports:** `call`

### 5.53 `commands/reload-plugins/` — 1 files, 61 lines

#### 5.53.1 `commands/reload-plugins/reload-plugins.ts` (61 lines)
- `commandType`: `local` (via `commands/reload-plugins/index.ts`)
- `returns`: `{ type: 'text' }`
- **Exports:** `call`

### 5.54 `commands/remote-env/` — 1 files, 7 lines

#### 5.54.1 `commands/remote-env/remote-env.tsx` (7 lines)
- Exports `call()` — command entry point (lazy-loaded by index)
- **Exports:** `call`

### 5.55 `commands/remote-setup/` — 2 files, 369 lines

#### 5.55.1 `commands/remote-setup/api.ts` (182 lines)
- Remote environment preset named `Default` with trusted network access
- **Exports:** `RedactedGithubToken`, `ImportTokenResult`, `ImportTokenError`, `importGithubToken`, `createDefaultEnvironment`, `isSignedIn`

#### 5.55.2 `commands/remote-setup/remote-setup.tsx` (187 lines)
- `commandType`: `local-jsx` (via `commands/remote-setup/index.ts`, name `web-setup`)
- UI state machine includes `checking`, `confirm`, `uploading`
- Exports `call()` — command entry point (lazy-loaded by index)
- **Exports:** `call`

### 5.56 `commands/resume/` — 1 files, 275 lines

#### 5.56.1 `commands/resume/resume.tsx` (275 lines)
- **Exports:** `filterResumableSessions`, `call`

### 5.57 `commands/review.ts/` — 1 files, 57 lines

#### 5.57.1 `commands/review.ts` (57 lines)
- `name`: `review`
- `commandType`: `prompt`
- `description`: `Review a pull request`
- Also exports `ultrareview` (`local-jsx`, gated by `isUltrareviewEnabled()`)
- Generates prompt text for model invocation

### 5.58 `commands/rewind/` — 1 files, 13 lines

#### 5.58.1 `commands/rewind/rewind.ts` (13 lines)
- `commandType`: `local` (via `commands/rewind/index.ts`)
- `returns`: `{ type: 'skip' }` on success (checkpoint restore is side-effect only)
- Exports `call()` — command entry point (lazy-loaded by index)
- **Exports:** `call`

### 5.59 `commands/sandbox-toggle/` — 1 files, 83 lines

#### 5.59.1 `commands/sandbox-toggle/sandbox-toggle.tsx` (83 lines)
- Exports `call()` — command entry point (lazy-loaded by index)
- **Exports:** `call`

### 5.60 `commands/security-review.ts/` — 1 files, 243 lines

#### 5.60.1 `commands/security-review.ts` (243 lines)
- `name`: `security-review`
- `commandType`: `prompt` (via `createMovedToPluginCommand`)
- `description`: `Complete a security review of the pending changes on the current branch`
- **Exports:** default Command (plugin migration shim)

### 5.61 `commands/session/` — 1 files, 140 lines

#### 5.61.1 `commands/session/session.tsx` (140 lines)
- `commandType`: `local-jsx` (via `commands/session/index.ts`)
- Exports QR/URL for remote session control
- **Exports:** `call`

### 5.62 `commands/skills/` — 1 files, 8 lines

#### 5.62.1 `commands/skills/skills.tsx` (8 lines)
- Exports `call()` — command entry point (lazy-loaded by index)
- **Exports:** `call`

### 5.63 `commands/stats/` — 1 files, 7 lines

#### 5.63.1 `commands/stats/stats.tsx` (7 lines)
- **Exports:** `call`

### 5.64 `commands/status/` — 1 files, 8 lines

#### 5.64.1 `commands/status/status.tsx` (8 lines)
- Exports `call()` — command entry point (lazy-loaded by index)
- **Exports:** `call`

### 5.65 `commands/statusline.tsx/` — 1 files, 24 lines

#### 5.65.1 `commands/statusline.tsx` (24 lines)
- `name`: `statusline`
- `commandType`: `prompt`
- `description`: `Set up Claude Code's status line UI`
- Generates prompt text for model invocation

### 5.66 `commands/stickers/` — 1 files, 16 lines

#### 5.66.1 `commands/stickers/stickers.ts` (16 lines)
- `commandType`: `local` (via `commands/stickers/index.ts`)
- `returns`: `{ type: 'text' }`
- Exports `call()` — command entry point (lazy-loaded by index)
- **Exports:** `call`

### 5.67 `commands/tag/` — 1 files, 215 lines

#### 5.67.1 `commands/tag/tag.tsx` (215 lines)
- Exports `call()` — command entry point (lazy-loaded by index)
- **Exports:** `call`

### 5.68 `commands/tasks/` — 1 files, 8 lines

#### 5.68.1 `commands/tasks/tasks.tsx` (8 lines)
- Exports `call()` — command entry point (lazy-loaded by index)
- **Exports:** `call`

### 5.69 `commands/terminalSetup/` — 1 files, 531 lines

#### 5.69.1 `commands/terminalSetup/terminalSetup.tsx` (531 lines)
- Exports `call()` — command entry point (lazy-loaded by index)
- **Exports:** `getNativeCSIuTerminalDisplayName`, `shouldOfferTerminalSetup`, `setupTerminal`, `isShiftEnterKeyBindingInstalled`, `hasUsedBackslashReturn`, `markBackslashReturnUsed`

### 5.70 `commands/theme/` — 1 files, 57 lines

#### 5.70.1 `commands/theme/theme.tsx` (57 lines)
- **Exports:** `call`

### 5.71 `commands/thinkback/` — 1 files, 554 lines

#### 5.71.1 `commands/thinkback/thinkback.tsx` (554 lines)
- `description`: `Watch your year in review`
- Exports `call()` — command entry point (lazy-loaded by index)
- **Exports:** `playAnimation`, `call`

### 5.72 `commands/thinkback-play/` — 1 files, 43 lines

#### 5.72.1 `commands/thinkback-play/thinkback-play.ts` (43 lines)
- `commandType`: `local` (via `commands/thinkback-play/index.ts`)
- `returns`: `{ type: 'text' }`
- Exports `call()` — command entry point (lazy-loaded by index)
- **Exports:** `call`

### 5.73 `commands/ultraplan.tsx/` — 1 files, 471 lines

#### 5.73.1 `commands/ultraplan.tsx` (471 lines)
- `name`: `ultraplan`
- `commandType`: `local-jsx`
- `description`: `~10–30 min · Claude Code on the web drafts an advanced plan you can edit and approve. See ${CCR_TERMS_URL}`
- `argumentHint`: `<prompt>`
- **Feature:** `ULTRAPLAN` | **ANT-only** (`INTERNAL_ONLY_COMMANDS`)
- **Exports:** `CCR_TERMS_URL`, `buildUltraplanPrompt`, `stopUltraplan`, `launchUltraplan`

### 5.74 `commands/upgrade/` — 1 files, 38 lines

#### 5.74.1 `commands/upgrade/upgrade.tsx` (38 lines)
- Exports `call()` — command entry point (lazy-loaded by index)
- **Exports:** `call`

### 5.75 `commands/version.ts/` — 1 files, 22 lines

#### 5.75.1 `commands/version.ts` (22 lines)
- `name`: `version`
- `commandType`: `local`
- `returns`: `{ type: 'text' }`
- `description`: `Print the version this session is running (not what autoupdate downloaded)`
- **ANT-only** (`INTERNAL_ONLY_COMMANDS`)

### 5.76 `commands/vim/` — 1 files, 38 lines

#### 5.76.1 `commands/vim/vim.ts` (38 lines)
- `commandType`: `local` (via `commands/vim/index.ts`)
- `returns`: `{ type: 'text' }`
- **Exports:** `call`

### 5.77 `commands/voice/` — 1 files, 150 lines

#### 5.77.1 `commands/voice/voice.ts` (150 lines)
- `commandType`: `local` (via `commands/voice/index.ts`, feature `VOICE_MODE`)
- `returns`: `{ type: 'text' }`
- **Exports:** `call`
