# Ink Hooks, Migrations, Protobuf Types & Plugin System (Chapters 1-4)

> **Source**: `F:\Claude\src`  
> **Generated**: 2026-05-23  
> **Coverage**: 4 Sections, ~70 files analyzed

---

## Section 1: ink/hooks/ (12 hooks)

Location: `F:\Claude\src\ink\hooks\`

### 1.1 use-input.ts (92 lines)

**File**: `ink/hooks/use-input.ts`

```typescript
type Handler = (input: string, key: Key, event: InputEvent) => void

type Options = {
  isActive?: boolean  // default: true
}

const useInput = (inputHandler: Handler, options: Options = {}) => void
```

**Logic flow**:
1. **`useLayoutEffect`** (synchronous during commit): Enables raw mode via `setRawMode(true)` when `isActive` is not `false`. Cleans up by calling `setRawMode(false)`. Uses `useLayoutEffect` instead of `useEffect` to enable raw mode *before* render returns — preventing terminal echo/cursor visibility during the first frame.
2. **`useEffect`** (listener registration): Registers `handleData` on the internal stdin EventEmitter's `'input'` event. Cleanup removes the listener. Stable reference via `useEventCallback` — `isActive`/`inputHandler` are read from closure but the listener slot stays fixed (preserving `stopImmediatePropagation()` ordering).
3. **Ctrl+C handling**: If `internal_exitOnCtrlC` is false or the input isn't Ctrl+C, passes to `inputHandler`. Otherwise lets the app-level handler process it.

**Integration**: Uses `useStdin()` → `StdinContext` → `AppContext`. Connects to Ink's event emitter for keyboard input.

---

### 1.2 use-app.ts (8 lines)

**File**: `ink/hooks/use-app.ts`

```typescript
const useApp = () => useContext(AppContext)
```

Returns the `AppContext` value which provides:
- `exit()`: manually unmount the Ink app
- Other app-level utilities

**Integration**: Direct context consumer. No effects or refs. Minimal wrapper around React context.

---

### 1.3 use-stdin.ts (8 lines)

**File**: `ink/hooks/use-stdin.ts`

```typescript
const useStdin = () => useContext(StdinContext)
```

Returns the `StdinContext` value providing:
- `stdin`: raw Node.js ReadStream
- `setRawMode(boolean)`: toggle raw mode
- `internal_exitOnCtrlC`: boolean flag
- `internal_eventEmitter`: EventEmitter for input events
- `isRawModeSupported`: boolean

**Integration**: Foundation hook consumed by `useInput`. The `StdinContext` is provided at the `App` level.

---

### 1.4 use-animation-frame.ts (57 lines)

**File**: `ink/hooks/use-animation-frame.ts`

```typescript
export function useAnimationFrame(
  intervalMs: number | null = 16,
): [ref: (element: DOMElement | null) => void, time: number]
```

**Logic flow**:
1. Reads `ClockContext` for the shared clock + `useTerminalViewport()` for visibility detection
2. `active` = `isVisible && intervalMs !== null`
3. **`useEffect`**: When `clock` and `active`, subscribes to clock with `keepAlive: true` (visible animations drive the clock). On each clock tick, only updates state if enough time has elapsed (`now - lastUpdate >= intervalMs`)
4. Returns `[viewportRef, time]` — ref for the animated element, current time in ms

**Integration**: Shares the same `ClockContext` clock — all animation consumers (spinners, etc.) synchronize to one timer. The clock only runs with at least one `keepAlive` subscriber. Auto-pauses when terminal blurs.

---

### 1.5 use-declared-cursor.ts (73 lines)

**File**: `ink/hooks/use-declared-cursor.ts`

```typescript
export function useDeclaredCursor({
  line,     // number
  column,   // number
  active,   // boolean
}: {
  line: number
  column: number
  active: boolean
}): (element: DOMElement | null) => void
```

**Logic flow**:
1. `useContext(CursorDeclarationContext)` — gets the setter
2. `useRef<DOMElement | null>(null)` — stores attached DOM element
3. `useCallback` — stable set-node callback for ref attachment
4. **`useLayoutEffect`** (no deps): Runs every commit:
   - Active + node: `setCursorDeclaration({ relativeX: column, relativeY: line, node })`
   - Inactive: `setCursorDeclaration(null, node)` — clears only if *our* node matches (prevents clobbering from memoized active instances or sibling handoff)
5. **`useLayoutEffect`** (empty deps): Unmount cleanup — clears cursor declaration

**Purpose**: Parks the terminal cursor at the input caret position. Enables CJK IME preedit text to appear inline and accessibility tools to track input position.

---

### 1.6 use-interval.ts (67 lines)

**File**: `ink/hooks/use-interval.ts`

```typescript
// Exported function 1
export function useAnimationTimer(intervalMs: number): number

// Exported function 2
export function useInterval(
  callback: () => void,
  intervalMs: number | null,
): void
```

**Logic flow** (both functions):
1. Read `ClockContext` for shared clock
2. `useEffect`: Subscribe to clock with `keepAlive: false` — won't keep the clock alive alone, gets ticks when spinners/animations drive it
3. On each tick, check elapsed time; if `>= intervalMs`, update state (`useAnimationTimer`) or invoke callback (`useInterval`)

**Difference from stock `useInterval`**: Piggybacks on the shared Clock instead of creating independent `setInterval`. All timers consolidate into one wake-up.

---

### 1.7 use-search-highlight.ts (53 lines)

**File**: `ink/hooks/use-search-highlight.ts`

```typescript
export function useSearchHighlight(): {
  setQuery: (query: string) => void
  scanElement: (el: DOMElement) => MatchPosition[]
  setPositions: (
    state: {
      positions: MatchPosition[]
      rowOffset: number
      currentIdx: number
    } | null,
  ) => void
}
```

**Logic flow**:
1. `useContext(StdinContext)` — anchor to App subtree
2. Gets Ink instance from `instances.get(process.stdout)`
3. Returns memoized object with delegated functions to the Ink instance
4. Returns no-ops if Ink instance is null (outside fullscreen mode)

**Purpose**: Screen-space search highlight (SGR 7 inverse, same damage machinery as selection). Matches RENDERED text (post-truncation/ellipsis), not source text. Works for any visible content (bash output, file paths, errors).

---

### 1.8 use-selection.ts (104 lines)

**File**: `ink/hooks/use-selection.ts`

```typescript
// Export 1
export function useSelection(): {
  copySelection: () => string
  copySelectionNoClear: () => string
  clearSelection: () => void
  hasSelection: () => boolean
  getState: () => SelectionState | null
  subscribe: (cb: () => void) => () => void
  shiftAnchor: (dRow: number, minRow: number, maxRow: number) => void
  shiftSelection: (dRow: number, minRow: number, maxRow: number) => void
  moveFocus: (move: FocusMove) => void
  captureScrolledRows: (firstRow: number, lastRow: number, side: 'above' | 'below') => void
  setSelectionBgColor: (color: string) => void
}

// Export 2
export function useHasSelection(): boolean
```

**Logic flow**:
- `useSelection()`: Gets Ink instance, returns memoized object delegating to instance methods. No-ops when Ink is null.
- `useHasSelection()`: Uses `useSyncExternalStore` to subscribe to selection changes. Re-renders when selection is created/cleared.

**Integration**: Fullscreen-only (alt-screen). Pipes selection color theme to support syntax highlighting under selection (replaces old SGR-7 inverse).

---

### 1.9 use-tab-status.ts (72 lines)

**File**: `ink/hooks/use-tab-status.ts`

```typescript
export type TabStatusKind = 'idle' | 'busy' | 'waiting'

export function useTabStatus(kind: TabStatusKind | null): void
```

**Logic flow**:
1. `useContext(TerminalWriteContext)` — gets raw terminal write function
2. `useRef<TabStatusKind | null>` — tracks previous kind
3. `useEffect`: On kind change:
   - **null → null**: Doesn't re-clear (prevents double-emit)
   - **non-null → null**: Writes `CLEAR_TAB_STATUS` (OSC 21337)
   - **non-null → non-null**: Writes tab status with preset colors (green/orange/blue dots)

**Presets**:
| Kind | Color (rgb) | Status Text |
|------|-------------|-------------|
| idle | (0, 215, 95) | "Idle" |
| busy | (255, 149, 0) | "Working…" |
| waiting | (95, 135, 255) | "Waiting" |

**Integration**: Wraps OSC sequences for tmux/screen passthrough. No-ops silently on terminals that don't support OSC 21337.

---

### 1.10 use-terminal-focus.ts (16 lines)

**File**: `ink/hooks/use-terminal-focus.ts`

```typescript
export function useTerminalFocus(): boolean
```

Returns `isTerminalFocused` from `TerminalFocusContext`. Uses DECSET 1004 focus reporting — the terminal sends escape sequences for focus/blur. Returns `true` if focused *or* focus state is unknown.

---

### 1.11 use-terminal-title.ts (31 lines)

**File**: `ink/hooks/use-terminal-title.ts`

```typescript
export function useTerminalTitle(title: string | null): void
```

**Logic flow**:
1. `useContext(TerminalWriteContext)` — raw write function
2. `useEffect`: On title change:
   - **Windows**: Sets `process.title`
   - **Others**: Writes `OSC 0` (set title+icon) via Ink's stdout
   - ANSI escapes are stripped before writing

---

### 1.12 use-terminal-viewport.ts (96 lines)

**File**: `ink/hooks/use-terminal-viewport.ts`

```typescript
type ViewportEntry = {
  isVisible: boolean
}

export function useTerminalViewport(): [
  ref: (element: DOMElement | null) => void,
  entry: ViewportEntry,
]
```

**Logic flow**:
1. `useContext(TerminalSizeContext)` — terminal dimensions
2. `useRef<DOMElement | null>` — attached element
3. `useRef<ViewportEntry>` — visibility state (mutable ref, no setState to avoid cascading re-renders)
4. `useCallback` — stable ref setter
5. **`useLayoutEffect`** (no deps, runs every render):
   - Walks DOM parent chain to compute absolute position (accounts for scroll container `scrollTop`)
   - Computes `cursorRestoreScroll` offset when content overflows
   - Updates `entryRef.current.isVisible` — visible if element overlaps viewport
6. Visibility changes DO NOT trigger re-renders (only update ref). Callers pick up fresh values on their own re-render cycles.

**Integration**: Used by `useAnimationFrame` to pause animations when offscreen. Walks the DOM ancestor chain (not yoga tree) to incorporate scroll offsets.

---

## Section 2: migrations/ (11 files)

Location: `F:\Claude\src\migrations\`

### 2.1 migrateAutoUpdatesToSettings.ts (61 lines)

```typescript
export function migrateAutoUpdatesToSettings(): void
```

**Version transition**: Global config → settings.json env var  
**Changes**: Moves `autoUpdates: false` from global config to `userSettings.env.DISABLE_AUTOUPDATER = '1'`  
**Preconditions**:
- `globalConfig.autoUpdates === false`
- `globalConfig.autoUpdatesProtectedForNative !== true` (not forced for native installation)  
**Strategy**: Sets env var in process AND settings.json, then strips `autoUpdates` from global config via `saveGlobalConfig` destructuring. Logs `tengu_migrate_autoupdates_to_settings`.

---

### 2.2 migrateBypassPermissionsAcceptedToSettings.ts (40 lines)

```typescript
export function migrateBypassPermissionsAcceptedToSettings(): void
```

**Version transition**: Global config → settings.json  
**Changes**: Moves `bypassPermissionsModeAccepted` → `skipDangerousModePermissionPrompt` in `userSettings`  
**Preconditions**: `globalConfig.bypassPermissionsModeAccepted === true` AND `hasSkipDangerousModePermissionPrompt()` returns false  
**Strategy**: Conditionally sets in settings, then removes from global config. Idempotent.

---

### 2.3 migrateEnableAllProjectMcpServersToSettings.ts (118 lines)

```typescript
export function migrateEnableAllProjectMcpServersToSettings(): void
```

**Version transition**: Project config → local settings  
**Changes**: Migrates three fields: `enableAllProjectMcpServers`, `enabledMcpjsonServers`, `disabledMcpjsonServers` from project config to `localSettings`  
**Preconditions**: Any of the three fields exist in project config  
**Strategy**:
- Reads existing `localSettings` to avoid overwriting already-migrated values
- Merges server lists with deduplication (`Set`)
- Strips migrated fields from project config via `saveCurrentProjectConfig`
- Logs `tengu_migrate_mcp_approval_fields_success` with count

---

### 2.4 migrateFennecToOpus.ts (45 lines)

```typescript
export function migrateFennecToOpus(): void
```

**Version transition**: Fennec model alias → Opus 4.6 alias (ants only)  
**Changes**:
| Old | New |
|-----|-----|
| `fennec-latest` | `opus` |
| `fennec-latest[1m]` | `opus[1m]` |
| `fennec-fast-latest` | `opus[1m]` + `fastMode: true` |
| `opus-4-5-fast` | `opus[1m]` + `fastMode: true` |
**Preconditions**: `USER_TYPE === 'ant'`, model in userSettings matches a fennec prefix  
**Strategy**: Reads and writes `userSettings` only. Project/local/policy settings left alone. Idempotent without completion flag.

---

### 2.5 migrateLegacyOpusToCurrent.ts (57 lines)

```typescript
export function migrateLegacyOpusToCurrent(): void
```

**Version transition**: Explicit Opus 4.0/4.1 → `opus` alias (1P users)  
**Changes**: Maps `claude-opus-4-20250514`, `claude-opus-4-1-20250805`, `claude-opus-4-0`, `claude-opus-4-1` → `opus`  
**Preconditions**: `getAPIProvider() === 'firstParty'` AND `isLegacyModelRemapEnabled()` AND model matches legacy string  
**Strategy**: Updates `userSettings`, sets `legacyOpusMigrationTimestamp` in global config for one-time REPL notification. Logs `tengu_legacy_opus_migration`.

---

### 2.6 migrateOpusToOpus1m.ts (43 lines)

```typescript
export function migrateOpusToOpus1m(): void
```

**Version transition**: `opus` → `opus[1m]` (Max/Team Premium 1P users)  
**Changes**: Replaces `opus` with `opus[1m]` in userSettings if eligible  
**Preconditions**: `isOpus1mMergeEnabled()` AND `model === 'opus'`  
**Strategy**: Only writes if the new alias resolves differently from default. Pro subscribers skipped (they keep separate Opus + Opus 1M). Logs `tengu_opus_to_opus1m_migration`.

---

### 2.7 migrateReplBridgeEnabledToRemoteControlAtStartup.ts (22 lines)

```typescript
export function migrateReplBridgeEnabledToRemoteControlAtStartup(): void
```

**Version transition**: Config key rename  
**Changes**: `replBridgeEnabled` → `remoteControlAtStartup`  
**Preconditions**: Old key exists AND new key is `undefined`  
**Strategy**: Reads raw config via untyped cast, copies boolean value, deletes old key. Idempotent.

---

### 2.8 migrateSonnet1mToSonnet45.ts (48 lines)

```typescript
export function migrateSonnet1mToSonnet45(): void
```

**Version transition**: `sonnet[1m]` → `sonnet-4-5-20250929[1m]`  
**Changes**: Pins Sonnet 1M users to explicit Sonnet 4.5 version (Sonnet alias now resolves to 4.6)  
**Preconditions**: `config.sonnet1m45MigrationComplete` is falsy AND `model === 'sonnet[1m]'`  
**Strategy**: Updates userSettings AND in-memory override. Sets completion flag. Runs once.

---

### 2.9 migrateSonnet45ToSonnet46.ts (67 lines)

```typescript
export function migrateSonnet45ToSonnet46(): void
```

**Version transition**: Explicit Sonnet 4.5 → `sonnet`/`sonnet[1m]` alias (Pro/Max/Team Premium 1P)  
**Changes**: Maps `claude-sonnet-4-5-20250929[1m]`, `sonnet-4-5-20250929[1m]` → `sonnet[1m]`, non-1M → `sonnet`  
**Preconditions**: `getAPIProvider() === 'firstParty'` AND is Pro/Max/Team Premium  
**Strategy**: Preserves `[1m]` suffix. Sets `sonnet45To46MigrationTimestamp` for notification (only for existing users with `numStartups > 1`). Logs `tengu_sonnet45_to_46_migration`.

---

### 2.10 resetAutoModeOptInForDefaultOffer.ts (51 lines)

```typescript
export function resetAutoModeOptInForDefaultOffer(): void
```

**Version transition**: Re-surface auto-mode dialog for new "make default" option  
**Changes**: Clears `skipAutoPermissionPrompt` in userSettings if user has auto mode but not as default  
**Preconditions**: `TRANSCRIPT_CLASSIFIER` feature flag, `hasResetAutoModeOptInForDefaultOffer` is falsy, `getAutoModeEnabledState() === 'enabled'`, `skipAutoPermissionPrompt` is true, `defaultMode !== 'auto'`  
**Strategy**: Sets skip to `undefined`. Guard in GlobalConfig (not settings.json) survives settings resets. Logs `tengu_migrate_reset_auto_opt_in_for_default_offer`.

---

### 2.11 resetProToOpusDefault.ts (51 lines)

```typescript
export function resetProToOpusDefault(): void
```

**Version transition**: Default model for Pro users  
**Changes**: Sets `opusProMigrationTimestamp` for Pro 1P users on default model  
**Preconditions**: `opusProMigrationComplete` is falsy  
**Strategy**: If Pro 1P user on default (no custom model), sets timestamp for notification. Logs `tengu_reset_pro_to_opus_default`.

---

## Section 3: types/generated/ (4 protobuf files)

Location: `F:\Claude\src\types\generated\`

### 3.1 claude_code_internal_event.ts (865 lines)

**Source**: `events_mono/claude_code/v1/claude_code_internal_event.proto`  
**Generated by**: protoc-gen-ts_proto v2.6.1

#### Interfaces

| Interface | Description | Key Fields |
|-----------|-------------|------------|
| `GitHubActionsMetadata` | GitHub Actions environment info | `actor_id`, `repository_id`, `repository_owner_id` (all optional string) |
| `EnvironmentMetadata` | Environment/runtime info | `platform`, `node_version`, `terminal`, `package_managers`, `runtimes`, `is_running_with_bun`, `is_ci`, `is_claubbit`, `is_github_action`, `is_claude_code_action`, `is_claude_ai_auth`, `version`, `github_*` fields, `wsl_version`, `arch`, `is_claude_code_remote`, `remote_environment_type`, `claude_code_container_id`, `claude_code_remote_session_id`, `tags[]`, `deployment_environment`, `is_conductor`, `version_base`, `coworker_type`, `build_time`, `is_local_agent_mode`, `linux_distro_*`, `vcs`, `platform_raw` (most optional) |
| `SlackContext` | Claude-in-Slack event context | `slack_team_id`, `is_enterprise_install`, `trigger`, `creation_method` |
| `ClaudeCodeInternalEvent` | Main event schema (Statsig) | `event_name`, `client_timestamp`, `model`, `session_id`, `user_type`, `betas`, `env` (EnvironmentMetadata), `entrypoint`, `agent_sdk_version`, `is_interactive`, `client_type`, `process` (JSON), `additional_metadata` (JSON), `auth` (PublicApiAuth), `server_timestamp`, `event_id`, `device_id`, `swe_bench_*`, `email`, `agent_id`, `parent_session_id`, `agent_type`, `slack` (SlackContext), `team_name`, `skill_name`, `plugin_name`, `marketplace_name` |

#### MessageFns Pattern
Each interface has an exported `MessageFns<T>` object with:
- `fromJSON(object: any): T`
- `toJSON(message: T): unknown`
- `create<I>(base?: I): T`
- `fromPartial<I>(object: I): T`

#### Internal Helpers
- `fromTimestamp(t: Timestamp): Date` — converts protobuf Timestamp to JS Date
- `fromJsonTimestamp(o: any): Date` — handles string/Date/Timestamp input
- `isSet(value: any): boolean` — null/undefined check
- `DeepPartial<T>`, `Exact<P, I>`, `KeysOfUnion<T>` — type utilities

---

### 3.2 auth.ts (100 lines)

**Source**: `events_mono/common/v1/auth.proto`

#### Interface

| Interface | Description | Fields |
|-----------|-------------|--------|
| `PublicApiAuth` | Auth context auto-injected by API | `account_id?: number`, `organization_uuid?: string`, `account_uuid?: string` |

**Used by**: `ClaudeCodeInternalEvent.auth`, `GrowthbookExperimentEvent.auth`

---

### 3.3 growthbook_experiment_event.ts (223 lines)

**Source**: `events_mono/growthbook/v1/growthbook_experiment_event.proto`

#### Interface

| Interface | Description | Key Fields |
|-----------|-------------|------------|
| `GrowthbookExperimentEvent` | Experiment exposure tracking | `event_id`, `timestamp`, `experiment_id`, `variation_id` (0=control, 1+=variants), `environment`, `user_attributes`, `experiment_metadata`, `device_id`, `auth` (PublicApiAuth), `session_id`, `anonymous_id`, `event_metadata_vars` |

**Connection**: Separate event type from `ClaudeCodeInternalEvent`. Tracks GrowthBook A/B experiment assignments following GrowthBook's BigQuery schema.

---

### 3.4 timestamp.ts (187 lines)

**Source**: `google/protobuf/timestamp.proto`

#### Interface

| Interface | Description | Fields |
|-----------|-------------|--------|
| `Timestamp` | Point in time (nanosecond resolution) | `seconds?: number` (Unix epoch seconds), `nanos?: number` (0-999,999,999) |

**Used by**: `ClaudeCodeInternalEvent` (cast to Date via `fromTimestamp`), `GrowthbookExperimentEvent` (same pattern). Range: 0001-01-01 to 9999-12-31.

---

## Section 4: utils/plugins/ (44 files) — Chapter 1

Location: `F:\Claude\src\utils\plugins\`

### 4.1 schemas.ts (1681 lines) — Core Zod Schemas

This is the single largest file, defining ALL Zod validation for the plugin ecosystem.

#### Constants

```typescript
export const ALLOWED_OFFICIAL_MARKETPLACE_NAMES = new Set([
  'claude-code-marketplace', 'claude-code-plugins',
  'claude-plugins-official', 'anthropic-marketplace',
  'anthropic-plugins', 'agent-skills', 'life-sciences',
  'knowledge-work-plugins',
])
export const BLOCKED_OFFICIAL_NAME_PATTERN = /.../
export const OFFICIAL_GITHUB_ORG = 'anthropics'
```

#### Exported Functions

```typescript
export function isMarketplaceAutoUpdate(marketplaceName: string, entry: { autoUpdate?: boolean }): boolean
export function isBlockedOfficialName(name: string): boolean
export function validateOfficialNameSource(name: string, source: {...}): string | null
export function isLocalPluginSource(source: PluginSource): source is string
export function isLocalMarketplaceSource(source: MarketplaceSource): source is Extract<...>
```

#### Exported Zod Schemas (all lazy-loaded via `z.lazy()` for circular dep safety)

| Schema Name | Purpose | Key Fields/Unions |
|-------------|---------|-------------------|
| `PluginAuthorSchema` | Plugin author info | `name`, `email?`, `url?` |
| `PluginHooksSchema` | hooks.json validation | `description?`, `hooks` (HooksSchema) |
| `CommandMetadataSchema` | Command metadata (source OR content) | `source?` \| `content?`, `description?`, `argumentHint?`, `model?`, `allowedTools?` |
| `LspServerConfigSchema` | LSP server config (.strictObject) | `command`, `args?`, `extensionToLanguage`, `transport` (stdio/socket), `env?`, `initializationOptions?`, `settings?`, `workspaceFolder?`, `startupTimeout?`, `shutdownTimeout?`, `restartOnCrash?`, `maxRestarts?` |
| `PluginManifestSchema` | plugin.json validation | Spreads: metadata + hooks + commands + agents + skills + outputStyles + channels + mcpServers + lspServers + settings + userConfig (all `.partial()`) |
| `MarketplaceSourceSchema` | Marketplace source locations (discriminated union) | `url`, `github`, `git`, `npm`, `file`, `directory`, `hostPattern`, `pathPattern`, `settings` |
| `PluginSourceSchema` | Plugin fetch sources (union) | `string` (rel path), `{source:'npm'}`, `{source:'pip'}`, `{source:'url'}`, `{source:'github'}`, `{source:'git-subdir'}` |
| `PluginMarketplaceEntrySchema` | Individual marketplace plugin entry | Extends `PluginManifestSchema().partial()` with `name`, `source`, `category?`, `tags?`, `strict?` (default true) |
| `PluginMarketplaceSchema` | Top-level marketplace.json | `name` (MarketplaceNameSchema), `owner`, `plugins[]`, `forceRemoveDeletedPlugins?`, `metadata?`, `allowCrossMarketplaceDependenciesOn?` |
| `PluginIdSchema` | Plugin@marketplace ID format | `/^[a-z0-9][-a-z0-9._]*@[a-z0-9][-a-z0-9._]*$/i` |
| `DependencyRefSchema` | Plugin dependency references | String `"name"` or `"name@mkt"` or `"name@mkt@^version"`, or object `{name, marketplace?}` — transforms strip version |
| `SettingsPluginEntrySchema` | Settings plugin reference | `PluginIdSchema` \| `{id, version?, required?, config?}` |
| `InstalledPluginSchema` | V1 installed plugin metadata | `version`, `installedAt`, `lastUpdated?`, `installPath`, `gitCommitSha?` |
| `InstalledPluginsFileSchemaV1` | V1 file format | `version: 1`, `plugins: Record<PluginId, InstalledPlugin>` |
| `PluginScopeSchema` | `z.enum(['managed', 'user', 'project', 'local'])` | |
| `PluginInstallationEntrySchema` | V2 installation entry | `scope`, `projectPath?`, `installPath`, `version?`, `installedAt?`, `lastUpdated?`, `gitCommitSha?` |
| `InstalledPluginsFileSchemaV2` | V2 file format | `version: 2`, `plugins: Record<PluginId, PluginInstallationEntry[]>` |
| `InstalledPluginsFileSchema` | Combined V1\|V2 | `z.union([V1, V2])` |
| `KnownMarketplaceSchema` | Marketplace cache metadata | `source`, `installLocation`, `lastUpdated`, `autoUpdate?` |
| `KnownMarketplacesFileSchema` | `Record<string, KnownMarketplace>` | |

#### Exported Inferred Types

```typescript
export type CommandMetadata, MarketplaceSource, PluginAuthor, PluginSource,
  PluginManifest, PluginManifestChannel, PluginMarketplace, PluginMarketplaceEntry,
  PluginId, InstalledPlugin, InstalledPluginsFileV1, InstalledPluginsFileV2,
  PluginScope, PluginInstallationEntry, KnownMarketplace, KnownMarketplacesFile
```

#### Key Internal Helpers
- `SettingsMarketplacePluginSchema` — narrow schema for settings-sourced marketplace plugin entries (no inline manifest, only name/source/description/version/strict)
- `MarketplaceNameSchema` — shared name validation (no spaces, no path separators, no impersonation, reserved names blocked)
- `gitSha` — 40-char lowercase hex
- `NpmPackageNameSchema` — validates npm package names including @scoped
- `PluginUserConfigOptionSchema` — matches `McpbUserConfigurationOption` shape
- `PluginManifestUserConfigSchema` — validated identifier keys (`/^[A-Za-z_]\w*$/`)
- `PluginManifestChannelsSchema` — array of `{server, displayName?, userConfig?}`

---

### 4.2 marketplaceManager.ts (2643 lines) — Marketplace Operations

#### Types

```typescript
type LoadedPluginMarketplace = { marketplace: PluginMarketplace; cachePath: string }
export type KnownMarketplacesConfig = KnownMarketplacesFile
export type MarketplaceProgressCallback = (message: string) => void
export type DeclaredMarketplace = {
  source: MarketplaceSource
  installLocation?: string
  autoUpdate?: boolean
  sourceIsFallback?: boolean  // NOT from JSON, only set in code
}
```

#### Exported Functions — Directory/Config

```typescript
export function getMarketplacesCacheDir(): string
export function clearMarketplacesCache(): void
export function getDeclaredMarketplaces(): Record<string, DeclaredMarketplace>
export function getMarketplaceDeclaringSource(name: string): 'userSettings' | 'projectSettings' | 'localSettings' | null
export function saveMarketplaceToSettings(name: string, entry: DeclaredMarketplace, settingSource?): void
```

#### Exported Functions — Config I/O

```typescript
export async function loadKnownMarketplacesConfig(): Promise<KnownMarketplacesConfig>
export async function loadKnownMarketplacesConfigSafe(): Promise<KnownMarketplacesConfig>
export async function saveKnownMarketplacesConfig(config: KnownMarketplacesConfig): Promise<void>
```

#### Exported Functions — Seed Marketplaces

```typescript
export async function registerSeedMarketplaces(): Promise<boolean>
```
- Registers admin-baked marketplaces from `CLAUDE_CODE_PLUGIN_SEED_DIR`
- Multiple seed dirs supported (path-delimiter-separated, first-seed-wins)
- Idempotent — skips if primary JSON already matches
- Forces `autoUpdate: false`

#### Exported Functions — Git Operations

```typescript
export async function gitPull(cwd: string, ref?: string, options?: {...}): Promise<{ code: number; stderr: string }>
export async function gitClone(gitUrl: string, targetPath: string, ref?: string, sparsePaths?: string[]): Promise<{ code: number; stderr: string }>
export async function reconcileSparseCheckout(cwd: string, sparsePaths: string[] | undefined): Promise<{ code: number; stderr: string }>
```

#### Exported Functions — Marketplace Lifecycle

```typescript
export async function addMarketplaceSource(source: MarketplaceSource, onProgress?: MarketplaceProgressCallback): Promise<{name, alreadyMaterialized, resolvedSource}>
export async function removeMarketplaceSource(name: string): Promise<void>
export async function getMarketplaceCacheOnly(name: string): Promise<PluginMarketplace | null>
export const getMarketplace = memoize(async (name: string): Promise<PluginMarketplace>)
export async function getPluginByIdCacheOnly(pluginId: string): Promise<{entry, marketplaceInstallLocation} | null>
export async function getPluginById(pluginId: string): Promise<{entry, marketplaceInstallLocation} | null>
export async function refreshAllMarketplaces(): Promise<void>
export async function refreshMarketplace(name: string, onProgress?, options?): Promise<void>
export async function setMarketplaceAutoUpdate(name: string, autoUpdate: boolean): Promise<void>
```

#### Internal Functions (key)

- `loadAndCacheMarketplace()` — handles ALL source types: url (download), github (SSH/HTTPS fallback), git, npm (TODO), file, directory, settings (synthetic JSON)
- `cacheMarketplaceFromGit()` — tries pull first, fails → rm+reclone
- `cacheMarketplaceFromUrl()` — downloads + validates
- `readCachedMarketplace()` — tries `.claude-plugin/marketplace.json`, then direct file
- `isGitHubSshLikelyConfigured()` — quick SSH connection test (3s timeout)
- `gitSubmoduleUpdate()` — syncs submodules after pull (skips sparse clones)
- `seedDirFor()` — checks if installLocation is seed-managed
- `enhanceGitPullErrorMessages()` — user-friendly git error messages (SSH host key, auth, network)
- `redactUrlCredentials()` — redacts HTTP auth from URLs in logs

#### Key Design Choices
- **SSH/HTTPS fallback**: GitHub sources automatically try SSH first (if configured), fall back to HTTPS
- **Source-idempotency**: `addMarketplaceSource` skips clone if exact source already exists
- **Seed protection**: Seed-managed marketplaces can't be removed/modified by users
- **Settings sources**: Inline plugins from settings.json are materialized as synthetic marketplace.json

---

### 4.3 validatePlugin.ts (903 lines) — Plugin Validation Pipeline

#### Types

```typescript
export type ValidationResult = { success, errors: ValidationError[], warnings: ValidationWarning[], filePath, fileType }
export type ValidationError = { path, message, code? }
export type ValidationWarning = { path, message }
```

#### Exported Functions

```typescript
export async function validatePluginManifest(filePath: string): Promise<ValidationResult>
export async function validateMarketplaceManifest(filePath: string): Promise<ValidationResult>
export async function validatePluginContents(pluginDir: string): Promise<ValidationResult[]>
export async function validateManifest(filePath: string): Promise<ValidationResult>
```

#### Validation Pipeline for plugin.json

1. Read file (handle ENOENT/EISDIR/permission errors)
2. JSON parse (handle syntax errors)
3. Path traversal check: scan `commands[]`, `agents[]`, `skills[]` for `..`
4. Strip marketplace-only fields (`category`, `source`, `tags`, `strict`, `id`) — warn the author
5. `.strict()` Zod validation against `PluginManifestSchema`
6. Warnings: non-kebab name, missing version, missing description, missing author

#### Validation Pipeline for marketplace.json

1. Read + parse + path traversal check on `plugins[].source`
2. Path traversal on `plugins[].source.path` (git-subdir)
3. `.strict()` validation against `PluginMarketplaceSchema` + strict `PluginMarketplaceEntrySchema`
4. Warnings: no plugins, duplicate names, version mismatches (entry vs plugin.json)
5. Version-mismatch check for local-source entries (compares marketplace entry version with plugin's own plugin.json)

#### Component Validation

- `validateComponentFile()` — validates YAML frontmatter in skills/agents/commands markdown files
  - Checks: description (must be scalar), name (string), allowed-tools, shell (bash/powershell)
- `validateHooksJson()` — validates hooks/hooks.json with `PluginHooksSchema`
- `validatePluginContents()` — scans skills/, agents/, commands/, hooks/ directories

#### Key Helpers
- `detectManifestType()` — identifies plugin.json vs marketplace.json by filename
- `checkPathTraversal()` — detects `..` in paths with context-appropriate hints
- `marketplaceSourceHint()` — computes "use X instead of Y" for marketplace source paths
- `collectMarkdown()` — recursively collects .md files (SKILL.md for skills dirs)

---

### 4.4 pluginLoader.ts (~3095+ lines) — Plugin Loading Engine

#### Exported Functions — Cache Paths

```typescript
export function getPluginCachePath(): string
export function getVersionedCachePathIn(baseDir: string, pluginId: string, version: string): string
export function getVersionedCachePath(pluginId: string, version: string): string
export function getVersionedZipCachePath(pluginId: string, version: string): string
export function getLegacyCachePath(pluginName: string): string
export async function resolvePluginPath(pluginId: string, version?: string): Promise<string>
```

#### Exported Functions — Cache Operations

```typescript
export async function probeSeedCacheAnyVersion(pluginId: string): Promise<string | null>
export async function copyDir(src: string, dest: string): Promise<void>
export async function copyPluginToVersionedCache(sourcePath, pluginId, version, entry?, marketplaceDir?): Promise<string>
```

#### Exported Functions — Plugin Installation

```typescript
export async function installFromNpm(packageName: string, targetPath: string, options?): Promise<void>
export async function gitClone(gitUrl: string, targetPath: string, ref?: string, sha?: string): Promise<void>
export async function installFromGitSubdir(url: string, targetPath: string, subdirPath: string, ref?: string, sha?: string): Promise<string | undefined>
export function generateTemporaryCacheNameForPlugin(source: PluginSource): string
export async function cachePlugin(source: PluginSource, options?): Promise<{path, manifest, gitCommitSha?}>
```

#### Exported Functions — Manifest Loading

```typescript
export async function loadPluginManifest(manifestPath: string, pluginName: string, source: string): Promise<PluginManifest>
```

#### Exported Functions — Plugin Creation

```typescript
export async function createPluginFromPath(pluginPath, source, enabled, fallbackName, strict?): Promise<{plugin: LoadedPlugin, errors: PluginError[]}>
```

#### Exported Functions — Plugin Merging

```typescript
export function mergePluginSources(sources: {session, marketplace, builtin, managedNames?}): {plugins: LoadedPlugin[], errors: PluginError[]}
```

#### Internal Function — Main Loaders

```typescript
async function loadPluginsFromMarketplaces({cacheOnly}): Promise<{plugins, errors}>
```

**Flow**:
1. Merge `--add-dir` enabledPlugins with merged settings
2. Filter to `plugin@marketplace` format (skip builtin marketplace)
3. Pre-load marketplace catalogs once per marketplace (not per plugin)
4. Enterprise policy checks (allowlist/blocklist) — fail-closed guard
5. Load installed versions from `installed_plugins.json`
6. `Promise.allSettled` over all marketplace plugins:
   - `loadPluginFromMarketplaceEntry` (full) or `loadPluginFromMarketplaceEntryCacheOnly` (startup)
7. Collect plugins and errors

```typescript
async function loadPluginFromMarketplaceEntry(entry, marketplaceInstallLocation, pluginId, enabled, errorsOut, installedVersion?): Promise<LoadedPlugin | null>
async function loadPluginFromMarketplaceEntryCacheOnly(entry, marketplaceInstallLocation, pluginId, enabled, errorsOut, installPath?): Promise<LoadedPlugin | null>
async function finishLoadingPluginFromPath(entry, pluginId, enabled, errorsOut, pluginPath): Promise<LoadedPlugin | null>
```

**Load Plugin Flow** (simplified):
1. **Local plugins** (`typeof entry.source === 'string'`): Resolve relative path, calculate version, copy to versioned cache
2. **External plugins** (npm/github/url/git-subdir): Check versioned cache → seed cache → download + cache
3. **Zip cache mode**: Extract ZIP to session temp dir before loading
4. **finishLoadingPluginFromPath**: Load manifest, create LoadedPlugin, supplement with marketplace entry fields (commands, agents, skills, hooks, outputStyles)
5. **Strict mode** (default): marketplace supplements plugin.json; **non-strict**: marketplace provides full manifest

```typescript
async function loadSessionOnlyPlugins(sessionPluginPaths): Promise<{plugins, errors}>
```

Loads `--plugin-dir` plugins with `source='{name}@inline'`.

#### Internal Helper: `PluginSettingsSchema`

```typescript
// Allowlisted keys from SettingsSchema: only 'agent'
const PluginSettingsSchema = lazySchema(() => SettingsSchema().pick({agent: true}).strip())
```

#### Internal Helper: `loadPluginSettings()`

Loads from `settings.json` (priority) or `manifest.settings` (fallback). Filters through `PluginSettingsSchema`.

#### Internal Helper: `mergeHooksSettings()`

Merges two `HooksSettings` objects — per-event matcher arrays are concatenated.

---

### 4.5 dependencyResolver.ts (305 lines)

#### Types

```typescript
export type DependencyLookupResult = { dependencies?: string[] }
export type ResolutionResult =
  | { ok: true; closure: PluginId[] }
  | { ok: false; reason: 'cycle'; chain: PluginId[] }
  | { ok: false; reason: 'not-found'; missing: PluginId; requiredBy: PluginId }
  | { ok: false; reason: 'cross-marketplace'; dependency: PluginId; requiredBy: PluginId }
```

#### Exported Functions

```typescript
export function qualifyDependency(dep: string, declaringPluginId: string): string
```
Normalizes bare names → `name@marketplace`. @inline plugins keep bare names.

```typescript
export async function resolveDependencyClosure(
  rootId: PluginId,
  lookup: (id: PluginId) => Promise<DependencyLookupResult | null>,
  alreadyEnabled: ReadonlySet<PluginId>,
  allowedCrossMarketplaces: ReadonlySet<string> = new Set(),
): Promise<ResolutionResult>
```
DFS walk of transitive dependency closure. Cross-marketplace dependencies blocked by default. Root marketplace's allowlist applies. Already-enabled deps are skipped (no surprise settings writes).

```typescript
export function verifyAndDemote(plugins: readonly LoadedPlugin[]): {demoted: Set<string>, errors: PluginError[]}
```
Fixed-point loop: demote plugins with unsatisfied deps. Demoting A may break B → iterate until stable. Returns set of plugin IDs to demote + errors.

```typescript
export function findReverseDependents(pluginId: PluginId, plugins: readonly LoadedPlugin[]): string[]
export function getEnabledPluginIdsForScope(settingSource: EditableSettingSource): Set<PluginId>
export function formatDependencyCountSuffix(installedDeps: string[]): string
export function formatReverseDependentsSuffix(rdeps: string[] | undefined): string
```

---

### 4.6 pluginDirectories.ts (178 lines)

#### Exported Functions

```typescript
export function getPluginsDirectory(): string
export function getPluginSeedDirs(): string[]
export function pluginDataDirPath(pluginId: string): string
export function getPluginDataDir(pluginId: string): string
export async function getPluginDataDirSize(pluginId: string): Promise<{bytes, human} | null>
export async function deletePluginDataDir(pluginId: string): Promise<void>
```

#### Logic
- `getPluginsDirectory()`: Priority: `CLAUDE_CODE_PLUGIN_CACHE_DIR` env → `~/.claude/plugins` (or `~/.claude/cowork_plugins` if `--cowork` flag or `CLAUDE_CODE_USE_COWORK_PLUGINS`)
- `getPluginSeedDirs()`: Splits `CLAUDE_CODE_PLUGIN_SEED_DIR` by path delimiter (multiple seeds supported)
- Uses tilde expansion (`expandTilde`) for env var paths

---

### 4.7 pluginIdentifier.ts (123 lines)

#### Types

```typescript
export type ExtendedPluginScope = PluginScope | 'flag'
export type PersistablePluginScope = Exclude<ExtendedPluginScope, 'flag'>
export type ParsedPluginIdentifier = { name: string; marketplace?: string }
```

#### Constants

```typescript
export const SETTING_SOURCE_TO_SCOPE = {
  policySettings: 'managed', userSettings: 'user',
  projectSettings: 'project', localSettings: 'local', flagSettings: 'flag',
} as const
```

#### Exported Functions

```typescript
export function parsePluginIdentifier(plugin: string): ParsedPluginIdentifier
export function buildPluginId(name: string, marketplace?: string): string
export function isOfficialMarketplaceName(marketplace: string | undefined): boolean
export function scopeToSettingSource(scope: PluginScope): EditableSettingSource
export function settingSourceToScope(source: EditableSettingSource): Exclude<PluginScope, 'managed'>
```

---

### 4.8 reconciler.ts (265 lines)

#### Types

```typescript
export type MarketplaceDiff = { missing: string[], sourceChanged: Array<{name, declaredSource, materializedSource}>, upToDate: string[] }
export type ReconcileOptions = { skip?, onProgress? }
export type ReconcileProgressEvent = {type: 'installing'|'installed'|'failed', ...}
export type ReconcileResult = { installed, updated, failed, upToDate, skipped }
```

#### Exported Functions

```typescript
export function diffMarketplaces(declared, materialized, opts?): MarketplaceDiff
export async function reconcileMarketplaces(opts?): Promise<ReconcileResult>
```

**Reconcile logic**:
1. Diff declared vs materialized → missing + sourceChanged + upToDate
2. For missing: install via `addMarketplaceSource`
3. For sourceChanged: update (re-install with new source)
4. Sparse-checkout reconciliation handled by marketplaceManager

**`normalizeSource()`**: Resolves relative paths for project-scoped settings. For git worktrees, resolves against canonical root (not worktree cwd).

---

### 4.9 marketplaceHelpers.ts (592 lines)

#### Exported Functions

```typescript
export function formatFailureDetails(failures, includeReasons): string
export function getMarketplaceSourceDisplay(source: MarketplaceSource): string
export function createPluginId(pluginName: string, marketplaceName: string): string
export async function loadMarketplacesWithGracefulDegradation(config): Promise<{marketplaces, failures}>
export function formatMarketplaceLoadingErrors(failures, successCount): {type, message} | null
export function getStrictKnownMarketplaces(): MarketplaceSource[] | null
export function getBlockedMarketplaces(): MarketplaceSource[] | null
export function getPluginTrustMessage(): string | undefined
export function extractHostFromSource(source: MarketplaceSource): string | null
export function getHostPatternsFromAllowlist(): string[]
export function isSourceInBlocklist(source: MarketplaceSource): boolean
export function isSourceAllowedByPolicy(source: MarketplaceSource): boolean
export function formatSourceForDisplay(source: MarketplaceSource): string
```

#### Types

```typescript
export type EmptyMarketplaceReason = 'git-not-installed' | 'all-blocked-by-policy' | 'policy-restricts-sources' | 'all-marketplaces-failed' | 'no-marketplaces-configured' | 'all-plugins-installed'
```

#### Exported Async Functions

```typescript
export async function detectEmptyMarketplaceReason({configuredMarketplaceCount, failedMarketplaceCount}): Promise<EmptyMarketplaceReason>
```

#### Policy System
- **Allowlist** (`strictKnownMarketplaces`): Empty array = deny all. Supports `hostPattern`, `pathPattern`, and exact source matching.
- **Blocklist** (`blockedMarketplaces`): Explicit denies. Empty = no-op. Supports asymmetric matching (git-url ↔ github shorthand).
- **Precedence**: Blocklist checked first, then allowlist.

---

### 4.10 installedPluginsManager.ts (1268 lines)

#### Exported Functions — File Paths

```typescript
export function getInstalledPluginsFilePath(): string
export function getInstalledPluginsV2FilePath(): string
export function clearInstalledPluginsCache(): void
export function migrateToSinglePluginFile(): void
export function resetMigrationState(): void
```

#### Exported Functions — Loading

```typescript
export function loadInstalledPluginsV2(): InstalledPluginsFileV2
export function addPluginInstallation(pluginId, scope, installPath, metadata, projectPath?): void
export function removePluginInstallation(pluginId, scope, projectPath?): void
export function getInMemoryInstalledPlugins(): InstalledPluginsFileV2
export function loadInstalledPluginsFromDisk(): InstalledPluginsFileV2
export function updateInstallationPathOnDisk(pluginId, scope, projectPath, newPath, newVersion, gitCommitSha?): void
export function hasPendingUpdates(): boolean
export function getPendingUpdateCount(): number
export function getPendingUpdatesDetails(): Array<{pluginId, scope, oldVersion, newVersion}>
export function resetInMemoryState(): void
export async function initializeVersionedPlugins(): Promise<void>
export function removeAllPluginsForMarketplace(marketplaceName: string): {orphanedPaths, removedPluginIds}
export function isInstallationRelevantToCurrentProject(inst: PluginInstallationEntry): boolean
export function isPluginInstalled(pluginId: string): boolean
export function isPluginGloballyInstalled(pluginId: string): boolean
export function addInstalledPlugin(pluginId, metadata, scope?, projectPath?): void
export function removeInstalledPlugin(pluginId: string): InstalledPlugin | undefined
export function deletePluginCache(installPath: string): void
export async function migrateFromEnabledPlugins(): Promise<void>
```

#### Migration System
- **V1→V2**: Single-file consolidation (`installed_plugins_v2.json` → `installed_plugins.json`)
- **V2 format**: Each plugin has array of installations (one per scope)
- **V1→V2 conversion**: All V1 plugins → `scope: 'user'`, recalculate versioned cache paths
- **Legacy cleanup**: Removes V1 flat cache directories not referenced by any installation

#### In-Memory vs Disk
- **Session state**: Frozen at startup (`inMemoryInstalledPlugins`)
- **Disk state**: Updated by background operations (`updateInstallationPathOnDisk`)
- **Pending updates**: Detected by comparing memory vs disk `installPath` differences

---

### 4.11 pluginVersioning.ts (157 lines)

```typescript
export async function calculatePluginVersion(
  pluginId, source, manifest?, installPath?, providedVersion?, gitCommitSha?
): Promise<string>

export function getGitCommitSha(dirPath: string): Promise<string | null>
export function getVersionFromPath(installPath: string): string | null
export function isVersionedPath(path: string): boolean
```

**Version priority**: 1. plugin.json `version` → 2. Provided version → 3. Pre-resolved git SHA → 4. Git SHA from install path → 5. `'unknown'`

**Git-subdir special case**: Encodes subdir path into version key (`{sha12}-{pathHash8}`) so cache keys differ when paths change but SHA doesn't.

---

### 4.12 addDirPluginSettings.ts (71 lines)

```typescript
export function getAddDirEnabledPlugins(): NonNullable<SettingsJson['enabledPlugins']>
export function getAddDirExtraMarketplaces(): Record<string, ExtraKnownMarketplace>
```

Reads from `--add-dir` directories' `.claude/settings.json` and `.claude/settings.local.json`. Lowest priority — callers spread standard settings on top.

---

### 4.13 cacheUtils.ts (196 lines)

```typescript
export function clearAllPluginCaches(): void
export function clearAllCaches(): void
export async function markPluginVersionOrphaned(versionPath: string): Promise<void>
export async function cleanupOrphanedPluginVersionsInBackground(): Promise<void>
```

**Orphan cleanup**: Versions not in `installed_plugins.json` get `.orphaned_at` marker. After 7 days, directory is deleted. ZIP cache mode skips cleanup entirely.

---

### 4.14 fetchTelemetry.ts (135 lines)

```typescript
export type PluginFetchSource = 'install_counts' | 'marketplace_clone' | 'marketplace_pull' | 'marketplace_url' | 'plugin_clone' | 'mcpb'
export type PluginFetchOutcome = 'success' | 'failure' | 'cache_hit'

export function logPluginFetch(source, urlOrSpec, outcome, durationMs, errorKind?): void
export function classifyFetchError(error: unknown): string
```

**Privacy**: Only known public hosts reported by name (github.com, gitlab.com, bitbucket.org, etc.). Private hostnames bucketed as `'other'`. Error classification: `dns_or_refused`, `timeout`, `conn_reset`, `auth`, `not_found`, `tls`, `invalid_schema`, `other`.

---

### 4.15 gitAvailability.ts (69 lines)

```typescript
export const checkGitAvailable = memoize(async (): Promise<boolean>)
export function markGitUnavailable(): void
export function clearGitAvailabilityCache(): void
```

Uses `which` (not exec) for security. macOS xcrun shim passes PATH check; callers that get `xcrun: error:` should call `markGitUnavailable()`.

---

### 4.16 headlessPluginInstall.ts (174 lines)

```typescript
export async function installPluginsForHeadless(): Promise<boolean>
```

**Flow**: Register seed marketplaces → reconcile marketplaces (zip-cache: skip unsupported types) → sync to zip cache → detect/uninstall delisted plugins → return `true` if anything changed.

---

### 4.17 hintRecommendation.ts (164 lines)

```typescript
export type PluginHintRecommendation = { pluginId, pluginName, marketplaceName, pluginDescription?, sourceCommand }
export function maybeRecordPluginHint(hint: ClaudeCodeHint): void
export async function resolvePluginHint(hint: ClaudeCodeHint): Promise<PluginHintRecommendation | null>
export function markHintPluginShown(pluginId: string): void
export function disableHintRecommendations(): void
export function _resetHintRecommendationForTesting(): void
```

Triggered by `type="plugin"` hints from CLIs. Gates: growthbook flag, already shown this session, hints disabled, cap (100 shown), not official marketplace, already installed, already shown, policy-blocked.

---

### 4.18 installCounts.ts (292 lines)

```typescript
export async function getInstallCounts(): Promise<Map<string, number> | null>
export function formatInstallCount(count: number): string
```

Fetches from GitHub stats repo. 24h TTL cache. Returns null on error (UI hides counts). Formats: <1000 raw, >=1000 "1.2K", >=1M "1.2M".

---

### 4.19 loadPluginAgents.ts (348 lines)

```typescript
export const loadPluginAgents = memoize(async (): Promise<AgentDefinition[]>)
export function clearPluginAgentCache(): void
```

**Flow**: Loads enabled plugins → for each: scans `agentsPath` + `agentsPaths` → loads .md files with frontmatter → namespaces as `plugin:agentName`. Parses: whenToUse, tools, skills, color, model, background, memory, isolation, effort, maxTurns, disallowedTools. Substitutes `${CLAUDE_PLUGIN_ROOT}` and `${user_config.X}`. Auto-injects Write/Edit/Read tools when memory enabled. `permissionMode`, `hooks`, `mcpServers` intentionally NOT parsed for plugin agents (security boundary).

---

### 4.20 loadPluginCommands.ts (946 lines)

```typescript
export const getPluginCommands = memoize(async (): Promise<Command[]>)
export function clearPluginCommandCache(): void
export const getPluginSkills = memoize(async (): Promise<Command[]>)
export function clearPluginSkillsCache(): void
```

**Command flow**: Scans `commandsPath` + `commandsPaths` → collects .md files → applies skill transformation (SKILL.md in directory = leaf container) → creates `Command` objects with plugin-prefixed names (`plugin:command`).

**Skill flow**: Scans `skillsPath` + `skillsPaths` → looks for `<dir>/SKILL.md` patterns → creates skill commands with `${CLAUDE_PLUGIN_ROOT}`, `${user_config.X}`, `${CLAUDE_SKILL_DIR}`, `${CLAUDE_SESSION_ID}` substitution.

Both support: inline content commands (no source file), metadata overrides from marketplace entry, frontmatter parsing (description, tools, argument-hint, model, effort, shell, etc.).

---

### 4.21 loadPluginHooks.ts (287 lines)

```typescript
export const loadPluginHooks = memoize(async (): Promise<void>)
export function clearPluginHookCache(): void
export async function pruneRemovedPluginHooks(): Promise<void>
export function resetHotReloadState(): void
export function getPluginAffectingSettingsSnapshot(): string
export function setupPluginHookHotReload(): void
```

**Hook events supported**: PreToolUse, PostToolUse, PostToolUseFailure, PermissionDenied, Notification, UserPromptSubmit, SessionStart, SessionEnd, Stop, StopFailure, SubagentStart, SubagentStop, PreCompact, PostCompact, PermissionRequest, Setup, TeammateIdle, TaskCreated, TaskCompleted, Elicitation, ElicitationResult, ConfigChange, WorktreeCreate, WorktreeRemove, InstructionsLoaded, CwdChanged, FileChanged (26 events).

**Hot reload**: Subscribes to `settingsChangeDetector` for `policySettings` changes. Compares snapshot of enabledPlugins + extraKnownMarketplaces + strictKnownMarketplaces + blockedMarketplaces. Only reloads if actually changed.

---

### 4.22 loadPluginOutputStyles.ts (178 lines)

```typescript
export const loadPluginOutputStyles = memoize(async (): Promise<OutputStyleConfig[]>)
export function clearPluginOutputStyleCache(): void
```

Scans `outputStylesPath` + `outputStylesPaths` → loads .md files → namespaces as `plugin:styleName`. Supports `force-for-plugin` frontmatter flag.

---

### 4.23 managedPlugins.ts (27 lines)

```typescript
export function getManagedPluginNames(): Set<string> | null
```

Returns plugin names locked by `policySettings.enabledPlugins` (boolean entries only). Returns null if no managed plugins.

---

### 4.24 mcpbHandler.ts (968 lines)

#### Types

```typescript
export type UserConfigValues = Record<string, string | number | boolean | string[]>
export type UserConfigSchema = Record<string, McpbUserConfigurationOption>
export type McpbLoadResult = { manifest, mcpConfig, extractedPath, contentHash }
export type McpbNeedsConfigResult = { status: 'needs-config', manifest, extractedPath, contentHash, configSchema, existingConfig, validationErrors }
export type McpbCacheMetadata = { source, contentHash, extractedPath, cachedAt, lastChecked }
export type ProgressCallback = (status: string) => void
```

#### Exported Functions

```typescript
export function isMcpbSource(source: string): boolean  // .mcpb or .dxt
export function loadMcpServerUserConfig(pluginId, serverName): UserConfigValues | null
export function saveMcpServerUserConfig(pluginId, serverName, config, schema): void
export function validateUserConfig(values, schema): {valid, errors}
export async function checkMcpbChanged(source, pluginPath): Promise<boolean>
export async function loadMcpbFile(source, pluginPath, pluginId, onProgress?, providedUserConfig?, forceConfigDialog?): Promise<McpbLoadResult | McpbNeedsConfigResult>
```

**MCPB loading flow**: Check cache → if valid use cached → else download/read → unzip → parse manifest → check user_config → if needed return `needs-config` → generate MCP config via `@anthropic-ai/mcpb`.

**Config storage**: Sensitive values → secureStorage (keychain), non-sensitive → settings.json `pluginConfigs[pluginId].mcpServers[serverName]`. Composite key: `${pluginId}/${serverName}`.

---

### 4.25 mcpPluginIntegration.ts (634 lines)

#### Types

```typescript
export type UnconfiguredChannel = { server, displayName, configSchema }
```

#### Exported Functions

```typescript
export async function loadPluginMcpServers(plugin: LoadedPlugin, errors?): Promise<Record<string, McpServerConfig> | undefined>
export function getUnconfiguredChannels(plugin: LoadedPlugin): UnconfiguredChannel[]
export function addPluginScopeToServers(servers, pluginName, pluginSource): Record<string, ScopedMcpServerConfig>
export async function extractMcpServersFromPlugins(plugins, errors?): Promise<Record<string, ScopedMcpServerConfig>>
export function resolvePluginMcpEnvironment(config, plugin, userConfig?, errors?, pluginName?, serverName?): McpServerConfig
export async function getPluginMcpServers(plugin, errors?): Promise<Record<string, ScopedMcpServerConfig> | undefined>
```

**MCP loading sources** (priority, last wins):
1. `.mcp.json` in plugin directory
2. `manifest.mcpServers` — handles string (path/MCPB), array, or inline object
3. MCPB files: downloaded, extracted, validated, config-generated

**Environment resolution**: `${CLAUDE_PLUGIN_ROOT}` → plugin path, `${CLAUDE_PLUGIN_DATA}` → data dir, `${user_config.X}` → saved config, general `${VAR}` → process env. Adds `CLAUDE_PLUGIN_ROOT` and `CLAUDE_PLUGIN_DATA` to server env.

**Server naming**: `plugin:{pluginName}:{serverName}`. Uses `scope: 'dynamic'`.

---

### 4.26 lspPluginIntegration.ts (387 lines)

#### Exported Functions

```typescript
export async function loadPluginLspServers(plugin, errors?): Promise<Record<string, LspServerConfig> | undefined>
export function resolvePluginLspEnvironment(config, plugin, userConfig?, _errors?): LspServerConfig
export function addPluginScopeToLspServers(servers, pluginName): Record<string, ScopedLspServerConfig>
export async function getPluginLspServers(plugin, errors?): Promise<Record<string, ScopedLspServerConfig> | undefined>
export async function extractLspServersFromPlugins(plugins, errors?): Promise<Record<string, ScopedLspServerConfig>>
```

**LSP loading sources**:
1. `.lsp.json` in plugin directory
2. `manifest.lspServers` — handles string (path), inline object, or array of both

**Path validation**: Uses `validatePathWithinPlugin()` to prevent traversal attacks. `resolvePluginLspEnvironment()` mirrors MCP environment resolution. Server naming: `plugin:{pluginName}:{name}`.

---

### 4.27 lspRecommendation.ts (374 lines)

#### Types

```typescript
export type LspPluginRecommendation = { pluginId, pluginName, marketplaceName, description?, isOfficial, extensions, command }
```

#### Exported Functions

```typescript
export async function getMatchingLspPlugins(filePath: string): Promise<LspPluginRecommendation[]>
export function addToNeverSuggest(pluginId: string): void
export function incrementIgnoredCount(): void
export function isLspRecommendationsDisabled(): boolean
export function resetIgnoredCount(): void
```

**Recommendation flow**: Scans ALL marketplaces for LSP plugins → filters by file extension → checks binary is installed (`isBinaryInstalled`) → excludes already installed / never-suggested → sorts official first. Disabled after 5 ignores or explicit disable.

---

### 4.28 officialMarketplace.ts (25 lines)

```typescript
export const OFFICIAL_MARKETPLACE_SOURCE = {
  source: 'github',
  repo: 'anthropics/claude-plugins-official',
} as const satisfies MarketplaceSource
export const OFFICIAL_MARKETPLACE_NAME = 'claude-plugins-official'
```

---

### 4.29 officialMarketplaceGcs.ts (216 lines)

```typescript
export async function fetchOfficialMarketplaceFromGcs(installLocation, marketplacesCacheDir): Promise<string | null>
export function classifyGcsError(e: unknown): string
```

**GCS fetch flow** (inc-5046):
1. GET `{GCS_BASE}/latest` → SHA pointer
2. Check `.gcs-sha` sentinel — skip if matches
3. GET `{GCS_BASE}/{sha}.zip` → download + extract to staging
4. Atomic swap: rm old → rename staging
5. Telemetry: `tengu_plugin_remote_fetch` with `source: 'marketplace_gcs'`

**Path guard**: Refuses paths outside marketplaces cache dir (prevents corrupted `known_marketplaces.json` from causing data loss).

---

### 4.30 officialMarketplaceStartupCheck.ts (439 lines)

#### Types

```typescript
export type OfficialMarketplaceSkipReason = 'already_attempted' | 'already_installed' | 'policy_blocked' | 'git_unavailable' | 'gcs_unavailable' | 'unknown'
export type OfficialMarketplaceCheckResult = { installed, skipped, reason?, configSaveFailed? }
```

#### Exported Functions

```typescript
export function isOfficialMarketplaceAutoInstallDisabled(): boolean
export const RETRY_CONFIG = { MAX_ATTEMPTS: 10, INITIAL_DELAY_MS: 3600000, BACKOFF_MULTIPLIER: 2, MAX_DELAY_MS: 604800000 }
export async function checkAndInstallOfficialMarketplace(): Promise<OfficialMarketplaceCheckResult>
```

**Auto-install flow**: Check retry eligibility → check env disable → check already installed → check policy → try GCS → fall back to git → exponential backoff on failure. macOS xcrun shim treated as `git_unavailable` (poisons memoized check). Telemetry: `tengu_official_marketplace_auto_install`.

---

### 4.31 orphanedPluginFilter.ts (114 lines)

```typescript
export async function getGlobExclusionsForPluginCache(searchPath?: string): Promise<string[]>
export function clearPluginCacheExclusions(): void
```

Finds `.orphaned_at` markers via ripgrep, generates `--glob '!**/<dir>/**'` exclusion patterns for Grep/Glob tools. Session-scoped cache, frozen once computed.

---

### 4.32 parseMarketplaceInput.ts (162 lines)

```typescript
export async function parseMarketplaceInput(input: string): Promise<MarketplaceSource | { error: string } | null>
```

**Input formats supported**:
- Git SSH: `user@host:path[#ref]`
- HTTP/HTTPS URLs: detects GitHub repos, Azure DevOps (`/_git/`)
- Local paths: `./`, `../`, `/`, `~`, Windows drive letters
- GitHub shorthand: `owner/repo[#ref]` or `owner/repo[@ref]`

---

### 4.33 performStartupChecks.tsx (70 lines)

```typescript
export async function performStartupChecks(setAppState: SetAppState): Promise<void>
```

**Flow**: Check trust dialog accepted → register seed marketplaces → if seed changed: clear caches + set `needsRefresh` → `performBackgroundPluginInstallations`. Called from REPL after trust dialog.

---

### 4.34 pluginAutoupdate.ts (284 lines)

#### Types

```typescript
export type PluginAutoUpdateCallback = (updatedPlugins: string[]) => void
```

#### Exported Functions

```typescript
export function onPluginsAutoUpdated(callback: PluginAutoUpdateCallback): () => void
export function getAutoUpdatedPluginNames(): string[]
export async function updatePluginsForMarketplaces(marketplaceNames: Set<string>): Promise<string[]>
export function autoUpdateMarketplacesAndPluginsInBackground(): void
```

**Auto-update flow**: Get autoUpdate-enabled marketplaces → refresh each → update plugins for those marketplaces → notify callback. Uses `Promise.allSettled`. Non-blocking (void IIFE). Pending notifications stored until callback registered.

---

### 4.35 pluginBlocklist.ts (127 lines)

```typescript
export function detectDelistedPlugins(installedPlugins, marketplace, marketplaceName): string[]
export async function detectAndUninstallDelistedPlugins(): Promise<string[]>
```

**Delisting flow**: Compare installed plugins against marketplace manifests → find plugins not listed → auto-uninstall from user/project/local scopes → add to flagged list. Only applies when `forceRemoveDeletedPlugins: true` in marketplace.json.

---

### 4.36 pluginFlagging.ts (208 lines)

#### Types

```typescript
export type FlaggedPlugin = { flaggedAt: string, seenAt?: string }
```

#### Exported Functions

```typescript
export async function loadFlaggedPlugins(): Promise<void>
export function getFlaggedPlugins(): Record<string, FlaggedPlugin>
export async function addFlaggedPlugin(pluginId: string): Promise<void>
export async function markFlaggedPluginsSeen(pluginIds: string[]): Promise<void>
export async function removeFlaggedPlugin(pluginId: string): Promise<void>
```

**Storage**: `~/.claude/plugins/flagged-plugins.json`. Atomic writes (temp + rename). Auto-expires seen entries after 48h.

---

### 4.37 pluginInstallationHelpers.ts (595 lines)

#### Types

```typescript
export type PluginInstallationInfo = { pluginId, installPath, version? }
export type InstallCoreResult = { ok: true, closure, depNote } | { ok: false, reason, ... }
export type InstallPluginResult = { success: true, message } | { success: false, error }
export type InstallPluginParams = { pluginId, entry, marketplaceName, scope?, trigger? }
```

#### Exported Functions

```typescript
export function getCurrentTimestamp(): string
export function validatePathWithinBase(basePath, relativePath): string
export async function cacheAndRegisterPlugin(pluginId, entry, scope?, projectPath?, localSourcePath?): Promise<string>
export function registerPluginInstallation(info, scope?, projectPath?): void
export function parsePluginId(pluginId: string): {name, marketplace} | null
export function formatResolutionError(r: ResolutionResult & {ok: false}): string
export async function installResolvedPlugin({pluginId, entry, scope, marketplaceInstallLocation}): Promise<InstallCoreResult>
export async function installPluginFromMarketplace({pluginId, entry, marketplaceName, scope?, trigger?}): Promise<InstallPluginResult>
```

**Install core flow**:
1. Policy guard (check `isPluginBlockedByPolicy`)
2. Resolve dependency closure via `resolveDependencyClosure`
3. Policy guard for transitive deps
4. Write entire closure to `enabledPlugins` (one settings update)
5. Materialize: cache each closure member via `cacheAndRegisterPlugin`
6. Clear caches

---

### 4.38 pluginOptionsStorage.ts (400 lines)

#### Types

```typescript
export type PluginOptionValues = UserConfigValues
export type PluginOptionSchema = UserConfigSchema
```

#### Exported Functions

```typescript
export function getPluginStorageId(plugin: LoadedPlugin): string
export const loadPluginOptions = memoize((pluginId: string): PluginOptionValues)
export function clearPluginOptionsCache(): void
export function savePluginOptions(pluginId, values, schema): void
export function deletePluginOptions(pluginId: string): void
export function getUnconfiguredOptions(plugin: LoadedPlugin): PluginOptionSchema
export function substitutePluginVariables(value, plugin): string
export function substituteUserConfigVariables(value, userConfig): string
export function substituteUserConfigInContent(content, options, schema): string
```

**Storage split**: `sensitive: true` → secureStorage (keychain), everything else → `settings.json pluginConfigs[pluginId].options`.

**Variable substitution**:
- `substitutePluginVariables()`: `${CLAUDE_PLUGIN_ROOT}`, `${CLAUDE_PLUGIN_DATA}` → paths (forward-slash normalize on Windows)
- `substituteUserConfigVariables()`: `${user_config.KEY}` → saved values (throws on missing)
- `substituteUserConfigInContent()`: Safe variant for skill/agent content — sensitive keys → placeholder, unknown keys → literal

---

### 4.39 pluginPolicy.ts (20 lines)

```typescript
export function isPluginBlockedByPolicy(pluginId: string): boolean
```

Single source of truth: checks `policySettings.enabledPlugins[pluginId] === false`.

---

### 4.40 pluginStartupCheck.ts (341 lines)

#### Types

```typescript
export type PluginInstallResult = { installed: string[], failed: Array<{name, error}> }
```

#### Exported Functions

```typescript
export async function checkEnabledPlugins(): Promise<string[]>
export function getPluginEditableScopes(): Map<string, ExtendedPluginScope>
export function isPersistableScope(scope): scope is PersistablePluginScope
export function settingSourceToScope(source): ExtendedPluginScope
export async function getInstalledPlugins(): Promise<string[]>
export async function findMissingPlugins(enabledPlugins): Promise<string[]>
export async function installSelectedPlugins(pluginsToInstall, onProgress?, scope?): Promise<PluginInstallResult>
```

**Scope precedence** (lowest → highest): addDir → managed → user → project → local → flag. Managed settings can block user-enabled plugins.

---

### 4.41 refresh.ts (215 lines)

#### Types

```typescript
export type RefreshActivePluginsResult = { enabled_count, disabled_count, command_count, agent_count, hook_count, mcp_count, lsp_count, error_count, agentDefinitions, pluginCommands }
```

#### Exported Function

```typescript
export async function refreshActivePlugins(setAppState): Promise<RefreshActivePluginsResult>
```

**Layer-3 refresh flow**:
1. Clear all caches + orphan exclusions
2. `loadAllPlugins()` (full, warms cache-only memoize)
3. `getPluginCommands()` + `getAgentDefinitionsWithOverrides()` (parallel)
4. Pre-load MCP + LSP servers for each enabled plugin
5. Update AppState (enabled, disabled, commands, errors, needsRefresh: false)
6. Bump `pluginReconnectKey` (triggers MCP connection manager re-read)
7. `reinitializeLspServerManager()` (unconditional, handles removal)
8. `loadPluginHooks()` — full hook swap

---

### 4.42 walkPluginMarkdown.ts (69 lines)

```typescript
export async function walkPluginMarkdown(
  rootDir: string,
  onFile: (fullPath: string, namespace: string[]) => Promise<void>,
  opts: { stopAtSkillDir?: boolean; logLabel?: string } = {},
): Promise<void>
```

Recursive directory walker. When `stopAtSkillDir` is true and directory contains `SKILL.md`, collects .md files at that level but doesn't recurse into subdirectories. Namespace array tracks subdirectory path relative to root.

---

### 4.43 zipCache.ts (406 lines)

#### Exported Functions

```typescript
export function isPluginZipCacheEnabled(): boolean
export function getPluginZipCachePath(): string | undefined
export function getZipCacheKnownMarketplacesPath(): string
export function getZipCacheInstalledPluginsPath(): string
export function getZipCacheMarketplacesDir(): string
export function getZipCachePluginsDir(): string
export async function getSessionPluginCachePath(): Promise<string>
export async function cleanupSessionPluginCache(): Promise<void>
export function resetSessionPluginCache(): void
export async function atomicWriteToZipCache(targetPath, data): Promise<void>
export async function createZipFromDirectory(sourceDir: string): Promise<Uint8Array>
export async function extractZipToDirectory(zipPath, targetDir): Promise<void>
export async function convertDirectoryToZipInPlace(dirPath, zipPath): Promise<void>
export function getMarketplaceJsonRelativePath(marketplaceName: string): string
export function isMarketplaceSourceSupportedByZipCache(source: MarketplaceSource): boolean
```

**Zip cache structure**: Mounter volume (`CLAUDE_CODE_PLUGIN_CACHE_DIR`) with `known_marketplaces.json`, `installed_plugins.json`, `marketplaces/`, `plugins/`. Only `github`, `git`, `url`, `settings` sources supported. Preserves Unix exec bits via `external_attr` in ZIP entries.

---

### 4.44 zipCacheAdapters.ts (164 lines)

```typescript
export async function readZipCacheKnownMarketplaces(): Promise<KnownMarketplacesFile>
export async function writeZipCacheKnownMarketplaces(data: KnownMarketplacesFile): Promise<void>
export async function readMarketplaceJson(marketplaceName: string): Promise<PluginMarketplace | null>
export async function saveMarketplaceJsonToZipCache(marketplaceName, installLocation): Promise<void>
export async function syncMarketplacesToZipCache(): Promise<void>
```

**Sync flow**: Reads `known_marketplaces.json` → saves each marketplace JSON to zip cache → merges with previously cached data → writes back. Enables ephemeral containers to access marketplaces without re-cloning.

---

## Index of All Files Read

| # | File | Lines | Key Exports |
|---|------|-------|-------------|
| 1 | ink/hooks/use-input.ts | 92 | `useInput` (default) |
| 2 | ink/hooks/use-app.ts | 8 | `useApp` (default) |
| 3 | ink/hooks/use-stdin.ts | 8 | `useStdin` (default) |
| 4 | ink/hooks/use-animation-frame.ts | 57 | `useAnimationFrame` |
| 5 | ink/hooks/use-declared-cursor.ts | 73 | `useDeclaredCursor` |
| 6 | ink/hooks/use-interval.ts | 67 | `useAnimationTimer`, `useInterval` |
| 7 | ink/hooks/use-search-highlight.ts | 53 | `useSearchHighlight` |
| 8 | ink/hooks/use-selection.ts | 104 | `useSelection`, `useHasSelection` |
| 9 | ink/hooks/use-tab-status.ts | 72 | `useTabStatus`, `TabStatusKind` |
| 10 | ink/hooks/use-terminal-focus.ts | 16 | `useTerminalFocus` |
| 11 | ink/hooks/use-terminal-title.ts | 31 | `useTerminalTitle` |
| 12 | ink/hooks/use-terminal-viewport.ts | 96 | `useTerminalViewport` |
| 13 | migrations/migrateAutoUpdatesToSettings.ts | 61 | `migrateAutoUpdatesToSettings` |
| 14 | migrations/migrateBypassPermissionsAcceptedToSettings.ts | 40 | `migrateBypassPermissionsAcceptedToSettings` |
| 15 | migrations/migrateEnableAllProjectMcpServersToSettings.ts | 118 | `migrateEnableAllProjectMcpServersToSettings` |
| 16 | migrations/migrateFennecToOpus.ts | 45 | `migrateFennecToOpus` |
| 17 | migrations/migrateLegacyOpusToCurrent.ts | 57 | `migrateLegacyOpusToCurrent` |
| 18 | migrations/migrateOpusToOpus1m.ts | 43 | `migrateOpusToOpus1m` |
| 19 | migrations/migrateReplBridgeEnabledToRemoteControlAtStartup.ts | 22 | `migrateReplBridgeEnabledToRemoteControlAtStartup` |
| 20 | migrations/migrateSonnet1mToSonnet45.ts | 48 | `migrateSonnet1mToSonnet45` |
| 21 | migrations/migrateSonnet45ToSonnet46.ts | 67 | `migrateSonnet45ToSonnet46` |
| 22 | migrations/resetAutoModeOptInForDefaultOffer.ts | 51 | `resetAutoModeOptInForDefaultOffer` |
| 23 | migrations/resetProToOpusDefault.ts | 51 | `resetProToOpusDefault` |
| 24 | types/generated/.../claude_code_internal_event.ts | 865 | `ClaudeCodeInternalEvent`, `EnvironmentMetadata`, `GitHubActionsMetadata`, `SlackContext` |
| 25 | types/generated/.../auth.ts | 100 | `PublicApiAuth` |
| 26 | types/generated/.../growthbook_experiment_event.ts | 223 | `GrowthbookExperimentEvent` |
| 27 | types/generated/google/protobuf/timestamp.ts | 187 | `Timestamp` |
| 28 | utils/plugins/schemas.ts | 1681 | ~25 Zod schemas, 15+ inferred types, 5 functions |
| 29 | utils/plugins/marketplaceManager.ts | 2643 | 20+ exported functions for marketplace CRUD |
| 30 | utils/plugins/validatePlugin.ts | 903 | `validatePluginManifest`, `validateMarketplaceManifest`, `validatePluginContents`, `validateManifest` |
| 31 | utils/plugins/pluginLoader.ts | 3095+ | `createPluginFromPath`, `loadAllPlugins`, `cachePlugin`, `mergePluginSources`, etc. |
| 32 | utils/plugins/dependencyResolver.ts | 305 | `resolveDependencyClosure`, `verifyAndDemote`, `findReverseDependents` |
| 33 | utils/plugins/pluginDirectories.ts | 178 | `getPluginsDirectory`, `getPluginSeedDirs`, `getPluginDataDir` |
| 34 | utils/plugins/pluginIdentifier.ts | 123 | `parsePluginIdentifier`, `buildPluginId`, scope mapping |
| 35 | utils/plugins/reconciler.ts | 265 | `diffMarketplaces`, `reconcileMarketplaces` |
| 36 | utils/plugins/marketplaceHelpers.ts | 592 | Policy checks, `isSourceAllowedByPolicy`, `isSourceInBlocklist` |
| 37 | utils/plugins/installedPluginsManager.ts | 1268 | V1/V2 migration, `addInstalledPlugin`, `removeInstalledPlugin` |
| 38 | utils/plugins/pluginVersioning.ts | 157 | `calculatePluginVersion`, `getGitCommitSha` |
| 39 | utils/plugins/addDirPluginSettings.ts | 71 | `getAddDirEnabledPlugins`, `getAddDirExtraMarketplaces` |
| 40 | utils/plugins/cacheUtils.ts | 196 | `clearAllPluginCaches`, `cleanupOrphanedPluginVersionsInBackground` |
| 41 | utils/plugins/fetchTelemetry.ts | 135 | `logPluginFetch`, `classifyFetchError` |
| 42 | utils/plugins/gitAvailability.ts | 69 | `checkGitAvailable`, `markGitUnavailable` |
| 43 | utils/plugins/headlessPluginInstall.ts | 174 | `installPluginsForHeadless` |
| 44 | utils/plugins/hintRecommendation.ts | 164 | `maybeRecordPluginHint`, `resolvePluginHint` |
| 45 | utils/plugins/installCounts.ts | 292 | `getInstallCounts`, `formatInstallCount` |
| 46 | utils/plugins/loadPluginAgents.ts | 348 | `loadPluginAgents`, `clearPluginAgentCache` |
| 47 | utils/plugins/loadPluginCommands.ts | 946 | `getPluginCommands`, `getPluginSkills` |
| 48 | utils/plugins/loadPluginHooks.ts | 287 | `loadPluginHooks`, `setupPluginHookHotReload` |
| 49 | utils/plugins/loadPluginOutputStyles.ts | 178 | `loadPluginOutputStyles` |
| 50 | utils/plugins/managedPlugins.ts | 27 | `getManagedPluginNames` |
| 51 | utils/plugins/mcpbHandler.ts | 968 | `loadMcpbFile`, `validateUserConfig`, `isMcpbSource` |
| 52 | utils/plugins/mcpPluginIntegration.ts | 634 | `extractMcpServersFromPlugins`, `resolvePluginMcpEnvironment` |
| 53 | utils/plugins/lspPluginIntegration.ts | 387 | `extractLspServersFromPlugins`, `resolvePluginLspEnvironment` |
| 54 | utils/plugins/lspRecommendation.ts | 374 | `getMatchingLspPlugins`, `addToNeverSuggest` |
| 55 | utils/plugins/officialMarketplace.ts | 25 | `OFFICIAL_MARKETPLACE_SOURCE`, `OFFICIAL_MARKETPLACE_NAME` |
| 56 | utils/plugins/officialMarketplaceGcs.ts | 216 | `fetchOfficialMarketplaceFromGcs`, `classifyGcsError` |
| 57 | utils/plugins/officialMarketplaceStartupCheck.ts | 439 | `checkAndInstallOfficialMarketplace`, `RETRY_CONFIG` |
| 58 | utils/plugins/orphanedPluginFilter.ts | 114 | `getGlobExclusionsForPluginCache` |
| 59 | utils/plugins/parseMarketplaceInput.ts | 162 | `parseMarketplaceInput` |
| 60 | utils/plugins/performStartupChecks.tsx | 70 | `performStartupChecks` |
| 61 | utils/plugins/pluginAutoupdate.ts | 284 | `autoUpdateMarketplacesAndPluginsInBackground`, `onPluginsAutoUpdated` |
| 62 | utils/plugins/pluginBlocklist.ts | 127 | `detectAndUninstallDelistedPlugins` |
| 63 | utils/plugins/pluginFlagging.ts | 208 | `loadFlaggedPlugins`, `addFlaggedPlugin`, `removeFlaggedPlugin` |
| 64 | utils/plugins/pluginInstallationHelpers.ts | 595 | `installResolvedPlugin`, `cacheAndRegisterPlugin`, `validatePathWithinBase` |
| 65 | utils/plugins/pluginOptionsStorage.ts | 400 | `loadPluginOptions`, `savePluginOptions`, `substitutePluginVariables` |
| 66 | utils/plugins/pluginPolicy.ts | 20 | `isPluginBlockedByPolicy` |
| 67 | utils/plugins/pluginStartupCheck.ts | 341 | `checkEnabledPlugins`, `installSelectedPlugins` |
| 68 | utils/plugins/refresh.ts | 215 | `refreshActivePlugins` |
| 69 | utils/plugins/walkPluginMarkdown.ts | 69 | `walkPluginMarkdown` |
| 70 | utils/plugins/zipCache.ts | 406 | `isPluginZipCacheEnabled`, `createZipFromDirectory`, `extractZipToDirectory` |
| 71 | utils/plugins/zipCacheAdapters.ts | 164 | `syncMarketplacesToZipCache`, `readZipCacheKnownMarketplaces` |
