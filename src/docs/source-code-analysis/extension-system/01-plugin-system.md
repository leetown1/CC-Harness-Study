# Plugin System Architecture

## Overview

The plugin system is a multi-layer extension architecture that enables users to install, manage, and load plugins from various sources including marketplaces (git repos, URLs, npm, local files/directories), session-only paths (`--plugin-dir`), and built-in plugins. The system is built on a three-layer model: intent (settings), materialization (disk), and activation (runtime AppState).

A plugin is a directory containing optional `plugin.json` manifest, plus subdirectories for `commands/`, `agents/`, `skills/`, `output-styles/`, and `hooks/`. Plugins are identified by `name@marketplace` format (e.g., `code-formatter@claude-plugins-official`).

### Three-Layer Model

| Layer | Description | Location |
|-------|-------------|----------|
| **Layer 1: Intent** | Settings declare which plugins/marketplaces should exist | `settings.json` (`enabledPlugins`, `extraKnownMarketplaces`) |
| **Layer 2: Materialization** | Marketplaces are cloned/cached to disk; plugins are cached | `~/.claude/plugins/` (known_marketplaces.json, marketplaces/, cache/) |
| **Layer 3: Activation** | Loaded plugins populate AppState (commands, agents, hooks, MCP, LSP) | Runtime `AppState.plugins` |

---

## File Inventory

| File | Lines | Purpose |
|------|-------|---------|
| **Core Discovery & Loading** | | |
| `pluginLoader.ts` | 3302 | Core plugin discovery, loading, caching, manifest validation, git/npm/github/local source handling |
| `pluginIdentifier.ts` | 123 | Parse/build plugin IDs (`name@marketplace`), scope↔settings mapping |
| `pluginDirectories.ts` | 178 | Plugin directory paths, seed directories, data directories |
| **Schemas** | | |
| `schemas.ts` | 1681 | ALL Zod schemas: manifest, marketplace, plugin source, hooks, MCP/LSP config, user config, dependencies, installed plugins V1/V2, known marketplaces |
| **Marketplace System** | | |
| `marketplaceManager.ts` | 2643 | Marketplace lifecycle: known_marketplaces.json management, clone/cache from git/URL/file/directory/settings, SSH/HTTPS fallback, seed registration |
| `marketplaceHelpers.ts` | 592 | Enterprise policy enforcement: allowlist/blocklist, source extraction, host/pattern matching |
| `reconciler.ts` | 265 | Marketplace reconciler (Layer-2): diff declared vs materialized, install missing/changed |
| `parseMarketplaceInput.ts` | 162 | Parse marketplace source strings (git SSH, HTTPS, GitHub shorthand, local paths) |
| `officialMarketplace.ts` | 25 | Official marketplace constants (github:anthropics/claude-plugins-official) |
| `officialMarketplaceStartupCheck.ts` | 439 | Auto-install logic with retry backoff, GCS mirror fallback, git availability check |
| `officialMarketplaceGcs.ts` | 216 | GCS mirror fetch (downloads.claude.ai), SHA sentinel, atomic staging swap, ZIP extraction with exec-bit preservation |
| **Plugin Installation** | | |
| `pluginInstallationHelpers.ts` | 595 | Shared install core: cache+register, path validation, dependency closure, policy guards |
| `pluginStartupCheck.ts` | 341 | Startup: check enabled plugins across all scopes, scope tracking, install missing plugins |
| `headlessPluginInstall.ts` | 174 | CCR/headless install: seed registration, marketplace reconcile, ZIP cache sync, delisting enforcement |
| `performStartupChecks.tsx` | 70 | Background install after trust dialog (React component wrapper) |
| `installedPluginsManager.ts` | 1268 | installed_plugins.json management: V1→V2 migration, add/remove/update installations, scope tracking, pending updates |
| **Versioning & Updates** | | |
| `pluginVersioning.ts` | 157 | Version calculation: manifest > entry.version > git SHA > git-subdir path hash > unknown |
| `pluginAutoupdate.ts` | 284 | Background auto-updater: refresh marketplaces, update plugins from autoUpdate-enabled marketplaces |
| `pluginFlagging.ts` | 208 | Delisted plugin tracking: flagged-plugins.json, seen expiry (48h), atomic writes |
| `pluginBlocklist.ts` | 127 | Delisted plugin detection and auto-uninstall across marketplaces with `forceRemoveDeletedPlugins` |
| **Component Loaders** | | |
| `loadPluginCommands.ts` | 946 | Load slash commands from plugins. Handles markdown files + SKILL.md directory format, frontmatter parsing, variable substitution |
| `loadPluginAgents.ts` | 348 | Load agent definitions from plugins: namespace prefixing, memory scope, tools/skills config |
| `loadPluginHooks.ts` | 287 | Load and register hooks from all enabled plugins, hot-reload subscription |
| `loadPluginOutputStyles.ts` | 178 | Load output styles from plugin directories, frontmatter parsing, `forceForPlugin` flag |
| `walkPluginMarkdown.ts` | 69 | Recursive markdown walker with SKILL.md leaf detection, namespace tracking |
| **Integration** | | |
| `mcpPluginIntegration.ts` | 634 | MCP server config from plugins: MCPB files, inline config, `.mcp.json`, user config, env var substitution |
| `mcpbHandler.ts` | 968 | MCPB (.mcpb/.dxt) file handler: download/extract DXT manifests, caching, user config validation |
| `lspPluginIntegration.ts` | 387 | LSP server config from plugins: `.lsp.json`, inline config, extension mapping, platform-aware command resolution |
| `lspRecommendation.ts` | 374 | LSP plugin recommendations for known file extensions |
| **Enterprise & Policy** | | |
| `pluginPolicy.ts` | ~80 | Enterprise policy enforcement: check if plugin is blocked by managed settings |
| `managedPlugins.ts` | ~60 | Extract managed plugin names from policy settings |
| `dependencyResolver.ts` | 305 | Dependency resolution: DFS closure walk, cycle detection, cross-marketplace policy |
| **Storage** | | |
| `pluginOptionsStorage.ts` | 400 | Option storage: settings.json pluginConfigs + keychain for sensitive values, variable substitution |
| `addDirPluginSettings.ts` | 71 | --add-dir plugin/skills settings injection |
| **Caching** | | |
| `cacheUtils.ts` | 196 | Cache management: clear plugin/marketplace caches, orphaned version GC |
| `zipCache.ts` | 406 | ZIP cache for ephemeral containers: convert directories to ZIP, extract on load, session cleanup |
| `zipCacheAdapters.ts` | 164 | ZIP cache I/O: sync marketplaces to ZIP, read marketplace.json from ZIP |
| `orphanedPluginFilter.ts` | 114 | Ripgrep exclusion patterns for orphaned plugin versions |
| **Utilities** | | |
| `gitAvailability.ts` | 69 | Git availability check (memoized, with poison-on-failure) |
| `fetchTelemetry.ts` | 135 | Network fetch telemetry: log plugin/marketplace fetch outcomes |
| `installCounts.ts` | 292 | Install count fetching from backend API |
| `hintRecommendation.ts` | 164 | Plugin hint handling and recommendations |
| `validatePlugin.ts` | 903 | Manifest/component validation for plugin authors |
| **Service Layer** | | |
| `services/plugins/pluginOperations.ts` | 1088 | Core CRUD: install, uninstall, enable, disable, update operations |
| `services/plugins/PluginInstallationManager.ts` | 184 | Background reconciliation manager: startup checks + reactive re-check on settings changes |
| `services/plugins/pluginCliCommands.ts` | 344 | CLI wrappers: `claude plugin install/uninstall/enable/disable/update` |
| **Built-in** | | |
| `plugins/builtinPlugins.ts` | 141 | Built-in plugin registry, enabled/disabled state from user settings |
| `plugins/bundled/index.ts` | 22 | Bundled plugin index entry point |

---

## Core Architecture

### 1. `pluginLoader.ts` — Core Discovery & Loading

The heart of the plugin system. Handles all plugin source types and provides both full loading (with network/caching) and cache-only loading (for fast startup).

#### Key Exports

| Export | Description |
|--------|-------------|
| `loadAllPlugins()` | Primary entry: discovers plugins from marketplaces, session paths, and builtins. Memoized. |
| `loadAllPluginsCacheOnly()` | Cache-only variant (no network). Used by downstream loaders (commands, agents, hooks). |
| `cachePlugin(source)` | Downloads/clones a plugin from any source to temp cache. |
| `copyPluginToVersionedCache()` | Copies plugin to versioned cache directory: `cache/{mkt}/{plugin}/{version}/` |
| `copyDir(src, dest)` | Recursive directory copy with symlink/looping prevention. |
| `createPluginFromPath()` | Assembles a `LoadedPlugin` from a directory: loads manifest, detects directories, loads hooks/settings. |
| `loadPluginManifest()` | Loads and validates `plugin.json` from `.claude-plugin/plugin.json` or legacy `plugin.json`. |
| `mergePluginSources()` | Merges session, marketplace, and builtin plugins with priority logic. |
| `getPluginCachePath()` | Returns `~/.claude/plugins/cache/` |
| `getVersionedCachePath(pluginId, version)` | Returns `cache/{marketplace}/{plugin}/{version}/` |
| `getLegacyCachePath(pluginName)` | Returns non-versioned `cache/{plugin-name}/` |
| `resolvePluginPath()` | Resolves with fallback: versioned → legacy → versioned (new installs). |

#### Plugin Source Types

```typescript
type PluginSource =
  | string                  // "./path" — relative to marketplace root
  | { source: 'npm', package, version?, registry? }
  | { source: 'pip', package, version?, registry? }
  | { source: 'url', url, ref?, sha? }         // git URL
  | { source: 'github', repo, ref?, sha? }     // owner/repo
  | { source: 'git-subdir', url, path, ref?, sha? }  // monorepo subdirectory
```

#### Source Installation

- **Local path**: `copyDir(source, target)`, remove `.git`
- **NPM**: `npm install` into npm-cache, then `copyDir`
- **GitHub**: Clone via SSH (CLI) or HTTPS (CCR), with `--depth 1`
- **Git URL**: `git clone` with `--depth 1 --recurse-submodules --shallow-submodules`
- **Git subdir**: **Partial clone** (`--filter=tree:0`) + **sparse-checkout** (`--cone`) for monorepo efficiency. Only tree objects for the target path and blobs under it are downloaded.
- **Pip**: Not yet supported (throws error)

#### Plugin Loading Pipeline

```
loadAllPlugins()
  ├─ loadPlaygouinsFromMarketplaces()
  │   ├─ Collect enabled plugins (settings + --add-dir)
  │   ├─ Filter to plugin@marketplace format (skip builtins)
  │   ├─ Load known marketplaces config (policy check)
  │   ├─ Pre-load marketplace catalogs (M reads instead of N*M)
  │   ├─ For each plugin entry (parallel via Promise.allSettled):
  │   │   ├─ Enterprise policy check (allowlist/blocklist)
  │   │   ├─ Marketplace entry lookup (pre-loaded catalog)
  │   │   ├─ installed_plugins.json lookup (version for cache hit)
  │   │   ├─ cacheOnly → loadPluginFromMarketplaceEntryCacheOnly()
  │   │   │   ├─ Local: read directly from marketplace source dir
  │   │   │   ├─ Remote: read from recorded installPath
  │   │   │   └─ ZIP cache: extract to session temp dir
  │   │   └─ !cacheOnly → loadPluginFromMarketplaceEntry()
  │   │       ├─ Local: calculate version → copy to versioned cache
  │   │       ├─ Remote: check versioned cache → seed probe → clone + cache
  │   │       └─ ZIP cache: extract
  │   │   └─ finishLoadingPluginFromPath() — shared tail
  │   └─ Collect results, errors
  ├─ loadSessionOnlyPlugins() — --plugin-dir
  ├─ getBuiltinPlugins()
  └─ mergePluginSources()
```

#### Merge Precedence
1. **Session plugins** (`--plugin-dir`) — override installed with same name
2. **Marketplace plugins** (installed) — non-overridden entries
3. **Built-in plugins** — shipped with CLI, user-toggleable

Managed (policy) plugins cannot be overridden by session plugins.

#### finishLoadingPluginFromPath()

The shared tail function (~500 lines) handles:
- **No plugin.json**: Marketplace entry becomes the manifest; commands/agents/skills/output-styles/hooks read from entry
- **Non-strict + both**: Conflict error if both plugin.json and marketplace entry specify components
- **Has plugin.json**: Marketplace entry **supplements** (not replaces) manifest components
- **Commands**: Supports path/array format AND object mapping format with `CommandMetadata` (source|content, description, argumentHint, model, allowedTools)
- SHA from source pinning if available

### 2. `schemas.ts` — All Zod Schemas

#### Export Summary

| Schema | Purpose |
|--------|---------|
| `PluginManifestSchema` | Full `plugin.json` validation (11 sub-schemas merged via spread) |
| `PluginAuthorSchema` | `{ name, email?, url? }` |
| `PluginHooksSchema` | `{ description?, hooks: HooksSchema }` |
| `PluginMarketplaceSchema` | Marketplace manifest: `{ name, owner, plugins[], forceRemoveDeletedPlugins?, metadata?, allowCrossMarketplaceDependenciesOn? }` |
| `PluginMarketplaceEntrySchema` | Individual plugin entry within marketplace (extends manifest partial + source + category + tags + strict) |
| `PluginSourceSchema` | Union: string (relative path) | discriminated by source field |
| `MarketplaceSourceSchema` | Discriminated union: url, github, git, npm, file, directory, hostPattern, pathPattern, settings |
| `SettingsPluginEntrySchema` | Union: `"plugin@marketplace"` string | `{ id, version?, required?, config? }` |
| `InstalledPluginSchema` (V1) | `{ version, installedAt, lastUpdated, installPath, gitCommitSha?, marketplace? }` |
| `PluginInstallationEntrySchema` (V2) | `{ version, installedAt, lastUpdated, installPath, gitCommitSha?, scope, projectPath? }` |
| `InstalledPluginsFileSchemaV1` | `{ version: 1, plugins: Record<string, InstalledPlugin> }` |
| `InstalledPluginsFileSchemaV2` | `{ version: 2, plugins: Record<string, PluginInstallationEntry[]> }` |
| `KnownMarketplacesFileSchema` | `Record<string, { source: MarketplaceSource, installLocation, lastUpdated?, autoUpdate? }>` |
| `PluginIdSchema` | Regex: `/^[a-z0-9][-a-z0-9._]*@[a-z0-9][-a-z0-9._]*$/i` |
| `DependencyRefSchema` | Union: string (regex with optional @^version stripping) | object `{ name, marketplace? }` |
| `LspServerConfigSchema` | `{ command, args?, extensionToLanguage, transport?, env?, ... }` |
| `CommandMetadataSchema` | `{ source?: path, content?: string, description?, argumentHint?, model?, allowedTools? }` (source XOR content) |
| `PluginUserConfigOptionSchema` | `{ type, title, description, required?, default?, multiple?, sensitive?, min?, max? }` |

#### Marketplace Name Validation

Defenses against impersonation:
- **Non-ASCII check**: Blocks homograph attacks (Cyrillic 'а' vs Latin 'a')
- **Name pattern matching**: Blocks names matching `anthropic/claude` + `official/marketplace/plugins` patterns
- **Exact allowlist**: `ALLOWED_OFFICIAL_MARKETPLACE_NAMES` (9 names) — only allowed from `anthropics/` GitHub org
- **Reserved names**: `inline` (session-only), `builtin` (built-in)
- **Path safety**: No spaces, `/`, `\`, `..`, or `.`

#### `validateOfficialNameSource()`

Reserved marketplace names (e.g., `claude-plugins-official`) MUST come from:
- GitHub source with `anthropics/*` repo
- Git source with URL matching `github.com/anthropics/`

#### `isMarketplaceAutoUpdate()`

Official marketplaces auto-update by default (except `knowledge-work-plugins`). Third-party default to off. Per-entry `autoUpdate` setting overrides.

### 3. `pluginIdentifier.ts` — Plugin ID Parsing & Scope Mapping

```typescript
type ParsedPluginIdentifier = { name: string; marketplace?: string }
```

- `parsePluginIdentifier(plugin)`: Splits `"name@marketplace"` on first `@`
- `buildPluginId(name, marketplace?)`: Joins with `@`
- `isOfficialMarketplaceName(marketplace)`: Checks against `ALLOWED_OFFICIAL_MARKETPLACE_NAMES` (for telemetry redaction)

#### Scope ↔ SettingSource Mapping

```
policySettings → managed    (not user-editable)
userSettings   → user       (global, ~/.claude/settings.json)
projectSettings → project   (per-repo, .claude/settings.json)
localSettings  → local      (per-repo local override)
flagSettings   → flag       (session-only, NOT persisted)
```

`flag` scope is session-only — used for `--plugin-dir` and `--add-dir` plugins.

---

## Marketplace System

### 4. `marketplaceManager.ts` — Marketplace Lifecycle

Manages `~/.claude/plugins/known_marketplaces.json` and the `marketplaces/` cache directory.

#### Key Operations

| Operation | Description |
|-----------|-------------|
| `loadKnownMarketplacesConfig()` | Read JSON, validate schema, return. Throws on corruption (mutate paths). |
| `loadKnownMarketplacesConfigSafe()` | Same but returns `{}` on error (read-only paths). |
| `saveKnownMarketplacesConfig(config)` | Validate then write atomically via temp file + rename. |
| `getDeclaredMarketplaces()` | Intent layer: merge implicit official + `--add-dir` + settings. |
| `addMarketplaceSource(source, opts)` | Materialize a marketplace: clone/fetch, validate, register in JSON. |
| `getMarketplace(name)` | Memoized: load cached marketplace manifest. |
| `getMarketplaceCacheOnly(name)` | Cache-only variant (blocks on in-flight load, returns stale). |
| `getPluginById(pluginId)` | Full lookup: validates marketplace first. |
| `getPluginByIdCacheOnly(pluginId)` | Cache-only: reads known_marketplaces.json directly. |
| `refreshMarketplace(name)` | Git pull / re-fetch for a marketplace. |
| `removeMarketplace(name)` | Remove from JSON + delete cache. |
| `registerSeedMarketplaces()` | Sync read-only seed directories into primary JSON. |

#### Source Cache Strategies

| Source Type | Caching Strategy |
|-------------|-----------------|
| `url` | `axios.get()` → validate → write JSON to `marketplaces/{name}.json` |
| `github` | `git clone --depth 1 [--branch ref] [--filter=blob:none --no-checkout for sparse]` → read `.claude-plugin/marketplace.json` |
| `git` | Same as github but with explicit URL |
| `npm` | (Not yet implemented) |
| `file` | Read and validate local `.json` file |
| `directory` | Read `.claude-plugin/marketplace.json` from local directory |
| `settings` | Write synthetic `marketplace.json` from inline settings declaration |

#### Git Operations

**`gitClone()`** (marketplaceManager version):
- Configurable timeout: `CLAUDE_CODE_PLUGIN_GIT_TIMEOUT_MS` (default 120s)
- SSH: `StrictHostKeyChecking=yes`, `BatchMode=yes` (fail-closed)
- HTTPS: Credential helper enabled (respects `gh auth`, git-credential-store)
- Interactive prompts blocked: `GIT_TERMINAL_PROMPT=0`, `GIT_ASKPASS=''`, `stdin: 'ignore'`
- Sparse checkout: `--filter=blob:none --no-checkout` → `sparse-checkout set --cone` → `checkout HEAD`
- Enhanced error messages for: timeout, SSH host key, authentication, network
- Credential redaction in logs and error messages

**`gitPull()`**:
- If ref: `fetch origin ref` → `checkout ref` → `pull origin ref`
- No ref: `pull origin HEAD`
- Submodule update after successful pull (for non-sparse repos)
- Same timeout/error handling as clone

**`reconcileSparseCheckout()`**:
- Sparse→Full transition: return non-zero → caller falls back to `rm` + `re-clone`
- Full→Sparse or SparseA→SparseB: run `sparse-checkout set --cone` (idempotent)
- Full→Full: single `git config --get core.sparseCheckout` check, no-op

#### SSH/HTTPS Fallback

`isGitHubSshLikelyConfigured()`:
- Quick SSH test: `ssh -T -o BatchMode=yes -o ConnectTimeout=2 -o StrictHostKeyChecking=yes git@github.com`
- Exit code 1 + "successfully authenticated" → SSH works
- Else → HTTPS fallback for CCR mode

`addMarketplaceRegisterOnly()` uses this to route to SSH or HTTPS automatically.

#### Seed Directories

`CLAUDE_CODE_PLUGIN_SEED_DIR` environment variable:
- Pre-baked marketplace/plugin cache in container images
- PATH-like delimiter (`:` or `;`)
- Read-only — entries marked `autoUpdate: false`
- registerSeedMarketplaces() runs at startup:
  1. Read seed `known_marketplaces.json`
  2. Compute `installLocation` relative to runtime seed dir
  3. Register into primary JSON (seed wins over existing)
  4. First-seed-wins across multiple seeds

#### After loadAndCacheMarketplace

- Validation via `PluginMarketplaceSchema`
- Rename cache from temp name to marketplace's actual name
- Update `known_marketplaces.json`

### 5. `marketplaceHelpers.ts` — Policy Enforcement

#### Blocklist/Allowlist System

**`getStrictKnownMarketplaces()`**: Returns allowlist from `policySettings.strictKnownMarketplaces` or `null` (no restriction).

**`getBlockedMarketplaces()`**: Returns blocklist from `policySettings.blockedMarketplaces` or `null`.

**`isSourceAllowedByPolicy(source)`**:
1. Check blocklist first (takes precedence)
2. If allowlist exists, source must match at least one entry
3. If no allowlist, allowed by default

**`isSourceInBlocklist(source)`**: Cross-source-type matching:
- `github` ↔ `git` URL equivalence (e.g., GitHub shorthand matches git@github.com URLs)
- Blocklist without ref/path = wildcard (blocks all)
- Blocklist with specific ref/path = exact match only

**Source matching types**:
- `hostPattern`: Extract hostname from source, test against regex
- `pathPattern`: Match file/directory `.path` against regex
- Regular entries: Exact field comparison (`areSourcesEqual`)

#### Other Utilities
- `formatFailureDetails()`: Format error lists for user display
- `loadMarketplacesWithGracefulDegradation()`: Load all marketplaces, skip blocked, collect errors
- `detectEmptyMarketplaceReason()`: Diagnose why Discover screen is empty
- `extractHostFromSource()`: Extract hostname for hostPattern matching
- `formatSourceForDisplay()`: Human-readable source formatting

### 6. `reconciler.ts` — Marketplace Reconciliation (Layer-2)

Compares **declared intent** (settings) against **materialized state** (known_marketplaces.json).

#### `diffMarketplaces(declared, materialized)`

| Result | Condition |
|--------|-----------|
| `missing` | Declared in settings, absent from JSON |
| `sourceChanged` | Present in both, settings source ≠ JSON source |
| `upToDate` | Present in both, sources match |

Special case: `sourceIsFallback=true` → presence suffices, never reports sourceChanged (used for implicit official marketplace declaration with seed dirs).

Path normalization: Resolves relative `directory`/`file` paths against the canonical git root (not worktree cwd) for stable comparison across worktrees.

#### `reconcileMarketplaces(opts?)`

1. Get declared marketplaces
2. Load materialized state
3. Diff
4. For each missing/changed:
   - Skip if `opts.skip()` returns true
   - For sourceChanged local-path entries: skip if declared path doesn't exist
5. Process remaining work items sequentially via `addMarketplaceSource()`
6. Report progress via `opts.onProgress()`
7. Return results: `{ installed[], updated[], failed[{name,error}], upToDate[], skipped[] }`

### 7. `officialMarketplace.ts` + Startup Check + GCS

#### Constants
- `OFFICIAL_MARKETPLACE_NAME`: `claude-plugins-official`
- `OFFICIAL_MARKETPLACE_SOURCE`: `{ source: 'github', repo: 'anthropics/claude-plugins-official' }`

#### `checkAndInstallOfficialMarketplace()`

Retry logic with exponential backoff:

| Config | Value |
|--------|-------|
| `MAX_ATTEMPTS` | 10 |
| `INITIAL_DELAY_MS` | 1 hour |
| `BACKOFF_MULTIPLIER` | 2 |
| `MAX_DELAY_MS` | 1 week |

**Flow**:
1. **Check `shouldRetryInstallation()`**: Honor backoff, skip permanent failures (policy_blocked), enforce max attempts
2. **Skip reasons**: `already_attempted`, `already_installed`, `policy_blocked`, `git_unavailable` (with xcrun shim detection on macOS), `gcs_unavailable`
3. **Installation**:
   - Try **GCS mirror** first (`downloads.claude.ai`): fetch latest SHA pointer → compare `.gcs-sha` sentinel → download ZIP if new → atomic staging swap → register in known_marketplaces.json. Falls through to git if GCS fails AND kill-switch allows.
   - Git fallback: `addMarketplaceSource(OFFICIAL_MARKETPLACE_SOURCE)`
4. **On failure**: Record `failReason`, `retryCount`, `nextRetryTime` in GlobalConfig; log telemetry
5. **On success**: Clear retry metadata, record `installed: true`

#### `fetchOfficialMarketplaceFromGcs(installLocation, marketplacesCacheDir)`

1. **Path safety guard**: Refuse extraction if resolved path is outside marketplaces cache dir
2. **Wait for scroll idle** (network competes with scroll frames)
3. **Latest pointer**: `GET /latest` (Cache-Control: max-age=300)
4. **Sentinel check**: Compare `.gcs-sha` at install root → no-op if matches
5. **Download ZIP**: `GET /{sha}.zip` (content-addressed, CDN-cachable)
6. **Extract to staging**: `{installLocation}.staging/`, strip `marketplaces/claude-plugins-official/` prefix
7. **Preserve exec bits**: Parse ZIP central directory for external_attr → `chmod` +x where applicable
8. **Atomic swap**: `rm(installLocation)` → `rename(staging, installLocation)`
9. **Write sentinel**: `.gcs-sha` with new SHA
10. **Telemetry**: `tengu_plugin_remote_fetch` with outcome, duration, SHA, bytes, error classification

#### Error Classification (`classifyGcsError`)

| Error | Bucket |
|-------|--------|
| Axios timeout | `timeout` |
| HTTP status | `http_{status}` |
| Network error | `network` |
| Known FS codes (ENOSPC, EACCES, EPERM, EXDEV, EBUSY, ENOENT, ENOTDIR, EROFS, EMFILE, ENAMETOOLONG) | `fs_{code}` |
| Other FS errno codes | `fs_other` |
| fflate numeric code | `zip_parse` |
| Zip/central directory message | `zip_parse` |
| Empty latest body | `empty_latest` |
| Everything else | `other` |

### 8. `parseMarketplaceInput.ts` — Input Parsing

Parses raw user input strings into `MarketplaceSource`:

| Input Pattern | Result |
|--------------|--------|
| `user@host:path.git#ref` | `{ source: 'git', url, ref }` |
| `https://github.com/owner/repo` | `{ source: 'git', url: with .git suffix }` |
| `https://example.com/file.json` | `{ source: 'url', url }` |
| `https://*.azure.com/*/_git/*` | `{ source: 'git', url }` (ADO detection) |
| `owner/repo` or `owner/repo#ref` or `owner/repo@ref` | `{ source: 'github', repo, ref? }` |
| `./path`, `../path`, `/path`, `~/path` | `{ source: 'file' }` or `{ source: 'directory' }` |
| Windows: `.\path`, `C:\path` | Same resolution |

---

## Plugin Installation System

### 9. `pluginInstallationHelpers.ts` — Shared Installation Core

#### `installResolvedPlugin({ pluginId, entry, scope, marketplaceInstallLocation })`

Complete installation pipeline:

1. **Policy guard**: `isPluginBlockedByPolicy(pluginId)` → block
2. **Local-source guard**: Must have `marketplaceInstallLocation` for local plugins
3. **Resolve dependency closure**: DFS traversal via `resolveDependencyClosure()`
   - Fetch each dependency from marketplaces
   - Validate cross-marketplace policy (`allowCrossMarketplaceDependenciesOn`)
   - Detect cycles
4. **Policy guard for dependencies**: Check each transitive dependency against policy
5. **Write to settings**: Update `enabledPlugins` with closure in one atomic write
6. **Materialize**: Cache each closure member via `cacheAndRegisterPlugin()`
7. **Clear caches**: Invalidate memoized state

Result: `{ ok: true, closure[], depNote }` or structured error.

#### `cacheAndRegisterPlugin(pluginId, entry, scope, projectPath?, localSourcePath?)`

1. **Cache**: `cachePlugin(source)` → temp directory
2. **Version**: Calculate version from manifest, marketplace entry, git SHA, etc.
3. **Move to versioned path**: `cache/{mkt}/{plugin}/{version}/`
   - Handles marketplace-name-equals-plugin-name edge case (temp intermediate rename)
4. **ZIP cache**: If enabled, convert directory to ZIP
5. **Register**: `addInstalledPlugin()` with version, timestamps, installPath, scope

#### `validatePathWithinBase(basePath, relativePath)`

Path traversal guard: `resolve(basePath, relativePath)` must start with `resolve(basePath) + sep`.

#### `installPluginFromMarketplace()` — Interactive UI Wrapper

-Wraps `installResolvedPlugin` with try/catch, analytics (`tengu_plugin_installed`), and user-friendly messages.

### 10. `pluginStartupCheck.ts` — Startup Checks

#### `checkEnabledPlugins()`

Aggregates enabled plugins from all sources with correct precedence:
1. `--add-dir` (lowest priority)
2. Policy settings (highest priority)

Returns `string[]` of `plugin@marketplace` IDs.

#### `getPluginEditableScopes()`

Maps each plugin to the **user-editable** scope that "owns" it:
1. `managed` (lowest precedence — not editable but tracked for fallback)
2. `user` → `project` → `local` → `flag` (highest)

Used to determine which settings file to write back to when enabling/disabling.

#### `getInstalledPlugins()`

1. Triggers `migrateFromEnabledPlugins()` (background sync settings → installed_plugins)
2. Reads V2 format from in-memory session state
3. Returns array of installed plugin IDs

#### `findMissingPlugins(enabledPlugins)`

Filters enabled plugins not in installed list, checks marketplace existence in parallel.

#### `installSelectedPlugins(pluginIds, onProgress, scope)`

Batch install: for each plugin, lookup marketplace entry → cache external or register local → mark enabled in settings.

### 11. `headlessPluginInstall.ts` — CCR/Headless Install

Non-interactive plugin installation without AppState:

1. **Register seed marketplaces**: `registerSeedMarketplaces()` → clear caches if changed
2. **ZIP cache setup**: Create directory structure
3. **Reconcile marketplaces**: `reconcileMarketplaces()` with ZIP cache skip for unsupported types
4. **Sync marketplaces to ZIP cache**: `syncMarketplacesToZipCache()` (steady-state containers still need this)
5. **Delisting enforcement**: `detectAndUninstallDelistedPlugins()`
6. **Session cleanup registration**: `registerCleanup(cleanupSessionPluginCache)` for ZIP cache temp dirs
7. **Return**: `true` if plugins changed (caller refreshes, clears caches)

### 12. `installedPluginsManager.ts` — Installation State Management

Manages `~/.claude/plugins/installed_plugins.json`:

#### V1 → V2 Migration

**V1 format**: `{ version: 1, plugins: { "name@mkt": { version, installedAt, lastUpdated, installPath, gitCommitSha? } } }`

**V2 format**: `{ version: 2, plugins: { "name@mkt": [{ version, installedAt, lastUpdated, installPath, gitCommitSha?, scope, projectPath? }] } }`

Migration process:
1. If `installed_plugins_v2.json` exists: rename to `installed_plugins.json`, clean legacy cache
2. If V1 in main file: convert in-place, clean legacy cache
3. If V2 or no file: no-op

#### Session State

- `inMemoryInstalledPlugins`: Session snapshot at startup — not updated by background operations
- `installedPluginsCacheV2`: Memoized cache read from disk
- Background operations (auto-update) write to disk only; session reads from in-memory snapshot

#### Operations

- `addInstalledPlugin()`: Add new installation (V2 format with scope)
- `removePluginInstallation()`: Remove specific installation (multi-scope support)
- `updateInstallationPathOnDisk()`: Background update path without invalidating session state
- `loadInstalledPluginsFromDisk()`: Force re-read from disk (bypasses in-memory cache)
- `getInMemoryInstalledPlugins()`: Session snapshot
- `loadInstalledPluginsV2()`: Load V2 format (migrates V1 if needed)
- `hasPendingUpdates()` / `getPendingUpdatesDetails()`: Track updated-but-not-reloaded plugins
- `migrateFromEnabledPlugins()`: Sync settings.json enabledPlugins → installed_plugins.json (catch-up for plugins enabled via settings before install)
- `isInstallationRelevantToCurrentProject()`: Filter installations by current cwd

### 13. `pluginVersioning.ts` — Version Calculation

Priority order:
1. **Manifest version**: `plugin.json` → `version` field
2. **Provided version**: From marketplace entry or caller
3. **Pre-resolved git SHA**: Caller-captured (e.g., git-subdir before clone discard)
4. **Git SHA from install path**: `getHeadForDir(installPath)`
5. **`unknown`**: Last resort

**git-subdir path hashing**: SHA(40 chars) → short(12) + `-{path_hash}` (8 hex from SHA-256 of normalized path). Normalization matches squashfs cron byte-for-byte: backslash→/, strip leading `./`, strip trailing `/`, UTF-8 SHA-256 first 8 hex. Prevents cache key collision for different subdirs at same commit.

**Path helpers**: `getVersionFromPath(installPath)`, `isVersionedPath(path)`

---

## Auto-Update & Maintenance

### 14. `pluginAutoupdate.ts` — Background Auto-Updater

Runs as fire-and-forget background job:

1. `getAutoUpdateEnabledMarketplaces()`: Check declared + JSON state for `autoUpdate`
   - Settings-declared autoUpdate takes precedence
   - Official marketplaces default to true (except `knowledge-work-plugins`)
   - Third-party default to false
2. `refreshMarketplace()` for each enabled marketplace (parallel via `Promise.allSettled`)
3. `updatePlugins(autoUpdateEnabledMarketplaces)`: For each plugin, filter to project-relevant installations, call `updatePluginOp()`
4. **Notification**: If plugin callback registered → call immediately; else store pending notification for delivery when REPL mounts
5. **Skip conditions**: `shouldSkipPluginAutoupdate()` (config), no autoUpdate marketplaces

### 15. `pluginFlagging.ts` — Delisted Plugin Tracking

Manages `~/.claude/plugins/flagged-plugins.json`:

- **Write**: Atomic via temp file + rename (safe against crashes)
- **Module-level cache**: `getFlaggedPlugins()` is synchronous (for React render)
- **Seen expiry**: 48 hours after `seenAt` → auto-clear on next `loadFlaggedPlugins()`
- **Operations**: `addFlaggedPlugin()`, `markFlaggedPluginsSeen()`, `removeFlaggedPlugin()`, `getFlaggedPlugins()`

### 16. `pluginBlocklist.ts` — Delisted Plugin Removal

`detectAndUninstallDelistedPlugins()`:
1. Load flagged plugins
2. For each marketplace with `forceRemoveDeletedPlugins: true`:
   - Compare installed plugins against marketplace manifest
   - Delisted = installed but absent from marketplace entries list
3. Auto-uninstall delisted plugins from user-controllable scopes (skip managed-only)
4. Flag for UI notification
5. Graceful degradation: per-marketplace failure doesn't abort

---

## Component Loaders

### 17. `loadPluginCommands.ts` — Command Loading

Loads slash commands (`/plugin:command`) from plugin directories. Handles:

- **Directory scanning**: Walk plugin `commands/` dir, `commandsPaths[]` from manifest, `commandsMetadata[]` with object mapping
- **File formats**: Regular `.md` files (filename becomes command name) and `SKILL.md` directory format (parent dir becomes command name)
- **Namespace prefixing**: `pluginName:subdir:commandName`
- **Frontmatter parsing**: description, allowed-tools, argument-hint, when-to-use, model, disable-model-invocation, user-invocable, context, agent, effort, shell
- **Variable substitution**: `$ARGUMENTS`, `${CLAUDE_PLUGIN_DATA}`, `${CLAUDE_PLUGIN_ROOT}`, user config values
- **Shell execution**: `!` and ` ```! ` block expansion
- **Content blocks**: Object mapping with `source` (file path) or `content` (inline markdown)
- **Plugin options integration**: Load and substitute plugin options from settings.json + keychain

### 18. `loadPluginAgents.ts` — Agent Loading

Creates `AgentDefinition` objects from plugin markdown files:

| Frontmatter Field | Purpose |
|-------------------|---------|
| `name` | Agent name (fallback: filename) |
| `description` | Agent description |
| `tools` | Tool allowlist |
| `skills` | Skill allowlist |
| `color` | Agent color name |
| `model` | Default model |
| `when-to-use` | When the agent should be used |
| `memory` | Memory scope (user/project/local) |
| `max-turns` | Maximum conversation turns |
| `effort` | Effort level |
| `user-invocable` | Whether user can invoke directly |
| `hidden` | Hide from UI |
| `context` | Execution context (fork) |

### 19. `loadPluginHooks.ts` — Hook Registration

1. Load enabled plugins via cache-only path
2. Convert each plugin's `hooksConfig` to `PluginHookMatcher[]` arrays per event type
3. Register via `registerHookCallbacks()` (injected into runtime hook system)
4. **Hot-reload**: Subscribe to settings change detector; on `enabledPlugins` change → re-register
5. 24 hook event types supported (PreToolUse, PostToolUse, SessionStart, etc.)

### 20. `loadPluginOutputStyles.ts` — Output Style Loading

1. Walk plugin `output-styles/` dir and `outputStylesPaths[]` from manifest
2. Parse frontmatter: `name` (prefix with `pluginName:`), `description`, `force-for-plugin`
3. Return `OutputStyleConfig[]` with `{ name, description, prompt, source: 'plugin', forceForPlugin? }`

### 21. `walkPluginMarkdown.ts` — Recursive Walker

Walking strategy:
- Scan directory entries in parallel
- **`stopAtSkillDir` mode**: When a directory contains `SKILL.md`, collect `.md` files in that dir but don't recurse into subdirs (skill dirs are leaf containers)
- **Default mode**: Recurse into all subdirs, namespace accumulating as `["subdir1", "subdir2"]`
- Errors swallowed with debug log (one bad dir doesn't abort plugin load)

---

## Integration Points

### 22. `mcpPluginIntegration.ts` — MCP from Plugins

Loads MCP server configs from plugins via multiple sources:

1. **MCPB files** (`.mcpb` / `.dxt`): Download, extract DXT manifests, convert to MCP config
2. **Inline JSON config**: Direct `Record<string, McpServerConfig>` in manifest
3. **`.mcp.json`**: Standard location in plugin root
4. **Server conflict detection**: Warn when plugin MCP servers conflict

**Variable substitution**: `${CLAUDE_PLUGIN_ROOT}`, `${CLAUDE_PLUGIN_DATA}`, `${CLAUDE_PLUGIN_MCP_DIR}`, user config values.

**Channel validation**: Each `channels[].server` must match a key in the plugin's mcpServers.

### 23. `mcpbHandler.ts` — MCPB File Handler

Handles `.mcpb` and `.dxt` files:
- **Local files**: Validate path within plugin root, read and parse
- **Remote URLs**: Download with axios, cache by SHA256, validate
- **DXT manifest**: Parse and convert to `McpServerConfig`
- **User config**: Parse `UserConfigSchema` from manifest, prompt for values via `validateUserConfig`
- **Caching**: SHA256-based cache for downloaded MCPB files

### 24. `lspPluginIntegration.ts` — LSP from Plugins

Loads LSP server configs:
1. **`.lsp.json`**: Standard location in plugin root
2. **Inline config**: `Record<string, LspServerConfig>` in manifest
3. **Platform-aware command**: `command.win32` / `command.linux` / `command.darwin` overrides
4. **Extension mapping**: `extensionToLanguage` → file extension → language ID
5. **Auto-detected extensions**: When `extensionToLanguage` is empty, derive from server name convention

### 25. `lspRecommendation.ts` — LSP Recommendations

Matches file extensions to recommended LSP plugins from installed marketplaces. Useful for suggesting plugins when user opens certain file types.

---

## Enterprise & Policy

### `pluginPolicy.ts`
Checks `managed-settings.json` for `enabledPlugins: { "id": false }` — org-blocked plugins.

### `managedPlugins.ts`
Extracts managed plugin names from `policySettings.enabledPlugins`.

### `dependencyResolver.ts`

| Function | Description |
|----------|-------------|
| `resolveDependencyClosure()` | DFS closure walk starting from root plugin. Reads `dependencies` from manifest/marketplace entry. |
| `qualifyDependency()` | Resolve bare names against declaring plugin's marketplace |
| `verifyAndDemote()` | Demote circular dependencies from explicit installs to implicit dependencies |
| `findReverseDependents()` | Find plugins that depend on a given plugin |
| `formatDependencyCountSuffix()` | Format " (+ N dependency)" suffix for user messages |
| `getEnabledPluginIdsForScope()` | Get enabled plugin IDs for dependency resolution |

**Cross-marketplace policy**: Only the root plugin's marketplace `allowCrossMarketplaceDependenciesOn` matters — no transitive trust.

---

## Caching & Storage

### `pluginOptionsStorage.ts`
- **settings.json**: `pluginConfigs[pluginId].options` for non-sensitive values
- **Keychain / .credentials.json**: For `sensitive: true` options
- **Variable substitution**: `${user_config.KEY}` in MCP/LSP config, hook commands, skill/agent content
- **Plugin variables**: `${CLAUDE_PLUGIN_ROOT}`, `${CLAUDE_PLUGIN_DATA}`, `${CLAUDE_PLUGIN_MCP_DIR}`
- **Config dialog flow**: `loadPluginOptions()` → `getPluginStorageId()` → prompt if missing required fields

### `cacheUtils.ts`
- `clearAllCaches()`: Clear all plugin-related memoized caches (commands, agents, hooks, output styles, LSP recommendations, MCP, marketplace, plugin cache)
- `markPluginVersionOrphaned()`: Write `.orphaned_at` sentinel file for GC
- Orphan GC cleanup on load: remove version cache directories with expired sentinel

### `zipCache.ts`
For ephemeral/container environments:
- `isPluginZipCacheEnabled()`: `CLAUDE_CODE_PLUGIN_USE_ZIP_CACHE` env var
- `convertDirectoryToZipInPlace()`: ZIP a plugin directory in-place (replaces with `.zip`)
- `extractZipToDirectory()`: Extract ZIP to session temp dir for loading
- `getSessionPluginCachePath()`: Session temp dir for extracted ZIPs
- `cleanupSessionPluginCache()`: Clean up extracted temp dirs on session end
- `isMarketplaceSourceSupportedByZipCache()`: Only github and git sources supported for ZIP cache marketplaces

### `zipCacheAdapters.ts`
- `syncMarketplacesToZipCache()`: Write marketplace JSONs to ZIP cache volumes
- `readMarketplaceFromZipCache(name)`: Read cached marketplace JSON

### `orphanedPluginFilter.ts`
Generates ripgrep `--glob '!...' ` exclusion patterns for orphaned plugin version directories (prevents ripgrep from searching deleted plugin content).

---

## Service Layer

### `services/plugins/pluginOperations.ts` — Core CRUD

| Operation | Behavior |
|-----------|----------|
| `installPluginOp(pluginId, scope)` | Full install: dependency resolution, cache, register, settings write |
| `uninstallPluginOp(pluginId, scope)` | Remove from scope: update settings, remove installation, clean options/data dirs, warn about reverse dependents |
| `enablePluginOp(pluginId)` | Enable in appropriate scope; if not installed, trigger install |
| `disablePluginOp(pluginId, scope)` | Disable in scope; warn about reverse dependents |
| `updatePluginOp(pluginId, scope)` | Update to latest: re-cache, update installed_plugins, GC old version, handle managed scope |
| `getInstalledPluginDetails(pluginId)` | Enriched info: version, marketplace, scopes, update availability |
| `listPluginsOp()` | List all installed plugins |
| `searchPluginsOp(query)` | Search across marketplaces |
| `getPluginUpdateInfo(pluginId)` | Check if update available, return old/new versions |

### `services/plugins/PluginInstallationManager.ts`
Background reconciliation manager:
- **startup**: Calls `performBackgroundPluginInstallations()` after trust dialog
- **settings changes**: Reactively re-checks when `extraKnownMarketplaces` changes
- **progress tracking**: Per-marketplace progress notifications

### `services/plugins/pluginCliCommands.ts`
CLI command implementations:
- `claude plugin install <id> [--scope]`
- `claude plugin uninstall <id> [--scope]`
- `claude plugin enable <id>`
- `claude plugin disable <id> [--scope]`
- `claude plugin update <id> [--scope]`
- `claude plugin list [--installed]`
- `claude plugin search <query>`

---

## Built-in Plugins

### `plugins/builtinPlugins.ts`

Built-in plugins are shipped with the CLI and user-toggleable in `/plugin` UI:

- `registerBuiltinPlugin(definition)`: Register a `BuiltinPluginDefinition` (name, description, version, skills[], hooks?, mcpServers?, defaultEnabled?, isAvailable?)
- `getBuiltinPlugins()`: Returns `{ enabled: LoadedPlugin[], disabled: LoadedPlugin[] }` split by user settings
- `BUILTIN_MARKETPLACE_NAME`: `"builtin"` (used as marketplace suffix in IDs)
- `getBuiltinPluginSkillCommands()`: Convert enabled builtin skills to `Command[]` for the skill tool
- Source is `"bundled"` not `"builtin"` (keeps skills in skill tool listing, analytics, and prompt-truncation exemption)

### `plugins/bundled/index.ts`
Entry point for bundled plugin initialization (loads bundled plugin definitions).

---

## Plugin Directory Structure

```
~/.claude/plugins/
├── known_marketplaces.json      # Marketplace registry
├── installed_plugins.json       # V2 format: plugin installation history
├── flagged-plugins.json         # Delisted plugin tracking
├── marketplaces/                # Cached marketplace data
│   ├── claude-plugins-official/ # Git clone (URL/ge/directory sources)
│   │   ├── .claude-plugin/
│   │   │   └── marketplace.json
│   │   ├── .gcs-sha             # GCS sentinel
│   │   └── plugins/             # Plugin implementations
│   └── custom-marketplace.json  # Direct marketplace JSON (URL source)
├── cache/                       # Versioned plugin cache
│   └── {marketplace}/
│       └── {plugin}/
│           └── {version}/       # Plugin directory or .zip
└── data/                        # Persistent plugin data (survives updates)
    └── {plugin-id}/
```

---

## Key Design Decisions

1. **Pre-load marketplace catalogs**: For N plugins across M marketplaces, the old approach did 2N config reads + N catalog reads. Current approach does M pre-loads, reducing I/O.

2. **Seed cache priority**: Read-only pre-baked caches in container images bypass git clone entirely. Version `unknown` handled via `probeSeedCacheAnyVersion()` (first-boot chicken-and-egg).

3. **Parallel path validation**: `validatePluginPaths()` parallelizes `pathExists` checks while preserving deterministic error ordering.

4. **Atomic writes**: All JSON writes use temp-file + rename pattern (safe against crashes).

5. **ZIP cache for ephemeral containers**: Mount volume stores ZIPs instead of directories. Extracted to session temp on load.

6. **Git partial clone for monorepos**: `--filter=tree:0` + sparse-checkout avoids downloading entire monorepo blobs.

7. **Fail-closed policy**: Unknown marketplace source + active enterprise policy = blocked. Prevents silent fail-open of corrupted config.

8. **Versioned cache with deterministic keys**: git-subdir sources hash the path into the cache key to prevent collisions from same-monorepo-SHA, different-subdirs.
