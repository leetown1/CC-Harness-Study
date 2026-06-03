# Service & Swarm Layer — Depth Fill Analysis

> Auto-generated comprehensive reference. Every file fully read.

---

## Section 1: `services/autoDream/` (4 files)

Background memory consolidation. Fires the `/dream` prompt as a forked subagent when time-gate passes AND enough sessions have accumulated.

### `autoDream.ts` (324 lines)

**Types and Interfaces:**

```typescript
type AutoDreamConfig = {
  minHours: number
  minSessions: number
}

type AppendSystemMessageFn = NonNullable<ToolUseContext['appendSystemMessage']>
```

**Constants:**

```typescript
const SESSION_SCAN_INTERVAL_MS = 10 * 60 * 1000  // 10 min scan throttle
const DEFAULTS: AutoDreamConfig = { minHours: 24, minSessions: 5 }
```

**Exported Functions:**

```typescript
export function initAutoDream(): void
export async function executeAutoDream(
  context: REPLHookContext,
  appendSystemMessage?: AppendSystemMessageFn,
): Promise<void>
```

**Internal Functions:**

```typescript
function getConfig(): AutoDreamConfig           // Reads GB feature flag tengu_onyx_plover with defensive validation
function isGateOpen(): boolean                  // KAIROS active? → false. Remote mode? → false. AutoMemory disabled? → false. Then isAutoDreamEnabled()
function isForced(): boolean                    // Ant-build-only test override — always false in production
function makeDreamProgressWatcher(taskId, setAppState): (msg: Message) => void  // Watches forked agent messages, extracts text & tool counts
```

**Gate order (cheapest first):**
1. **Time:** hours since `lastConsolidatedAt >= minHours` (one stat)
2. **Sessions:** transcript count with mtime > `lastConsolidatedAt >= minSessions`
3. **Lock:** no other process mid-consolidation

**Runner lifecycle:** Closure-scoped inside `initAutoDream()`. Tests call `initAutoDream()` in `beforeEach` for a fresh closure. Runner executes in order: gate check → scan throttle → time gate → session gate → lock acquire → register DreamTask → runForkedAgent → completeDreamTask → append inline completion message.

**Error handling:** On abort, returns early (DreamTask.kill already handled rollback). On fork failure, calls `rollbackConsolidationLock(priorMtime)` to rewind mtime so time-gate passes again.

---

### `consolidationLock.ts` (140 lines)

**PID-Based File Lock with Stale-Holder Reclaim.**

**Constants:**

```typescript
const LOCK_FILE = '.consolidate-lock'
const HOLDER_STALE_MS = 60 * 60 * 1000  // 1 hour stale threshold
```

**Exported Functions:**

```typescript
export async function readLastConsolidatedAt(): Promise<number>
  // mtime of lock file = lastConsolidatedAt. Returns 0 if file absent.

export async function tryAcquireConsolidationLock(): Promise<number | null>
  // Writes current PID to lock file. Returns pre-acquire mtime (for rollback)
  // or null if blocked/lost a race.
  // Acquire logic:
  //   1. Read lock file (PID + mtime)
  //   2. If mtime < HOLDER_STALE_MS and PID is live → blocked (return null)
  //   3. Dead PID or no file → reclaim: write our PID
  //   4. Re-read to verify we won the race → PID mismatch means lost

export async function rollbackConsolidationLock(priorMtime: number): Promise<void>
  // Clears PID body, rewinds mtime. priorMtime=0 → unlink (restore no-file).

export async function listSessionsTouchedSince(sinceMs: number): Promise<string[]>
  // Gets session IDs with mtime > sinceMs via listCandidates. Uses mtime (not birthtime).

export async function recordConsolidation(): Promise<void>
  // Stamp from manual /dream. Optimistic — fires at prompt-build time, no post-skill hook.
```

---

### `consolidationPrompt.ts` (65 lines)

**Phase 1-4 Dream Prompt Template.**

**Exported Functions:**

```typescript
export function buildConsolidationPrompt(
  memoryRoot: string,
  transcriptDir: string,
  extra: string,
): string
```

**Prompt Structure:**
- **Phase 1 — Orient:** `ls` memory directory, read `ENTRYPOINT_NAME`, skim existing topic files, review logs/sessions subdirs
- **Phase 2 — Gather Recent Signal:** Priority: daily logs → existing drifted memories → transcript grep (not exhaustive reads)
- **Phase 3 — Consolidate:** Write/update memory files using auto-memory format conventions. Merge into existing topics, convert relative dates to absolute, delete contradicted facts.
- **Phase 4 — Prune and Index:** Update entrypoint under `MAX_ENTRYPOINT_LINES` / ~25KB. Remove stale pointers, demote verbose index lines, resolve contradictions.
- **Tool constraints note:** Appended via `extra` parameter — Bash restricted to read-only commands.

Imports: `DIR_EXISTS_GUIDANCE`, `ENTRYPOINT_NAME`, `MAX_ENTRYPOINT_LINES` from `memdir/memdir.js`.

---

### `config.ts` (21 lines)

**Feature Gate.**

```typescript
export function isAutoDreamEnabled(): boolean
  // User setting (autoDreamEnabled in settings.json) overrides GrowthBook default.
  // Falls through to tengu_onyx_plover feature flag.
```

Minimal imports — intentionally a leaf so UI components can read the enabled state without dragging in the forked agent / task registry / message builder chain.

---

## Section 2: `services/remoteManagedSettings/` (5 files)

Manages fetching, caching, and validation of remote-managed settings for enterprise customers. Checksum-based validation, graceful degradation.

### `index.ts` (638 lines)

**Constants:**

```typescript
const SETTINGS_TIMEOUT_MS = 10000        // 10 seconds
const DEFAULT_MAX_RETRIES = 5
const POLLING_INTERVAL_MS = 60 * 60 * 1000  // 1 hour
const LOADING_PROMISE_TIMEOUT_MS = 30000 // 30 seconds
```

**Module-level state:**

```typescript
let pollingIntervalId: ReturnType<typeof setInterval> | null
let loadingCompletePromise: Promise<void> | null
let loadingCompleteResolve: (() => void) | null
```

**Exported Functions:**

```typescript
export function initializeRemoteManagedSettingsLoadingPromise(): void
  // Creates promise for other systems to await. Only if eligible. 30s timeout prevents deadlocks.

export function computeChecksumFromSettings(settings: SettingsJson): string
  // sha256:<hex> via sortKeysDeep + jsonStringify (matches Python's sort_keys=True, separators=(",", ":"))
  // Exported for testing

export function isEligibleForRemoteManagedSettings(): boolean
  // Public API delegating to syncCache.isRemoteManagedSettingsEligible()

export async function waitForRemoteManagedSettingsToLoad(): Promise<void>
  // Returns immediately if not eligible or loading already completed

export async function clearRemoteManagedSettingsCache(): Promise<void>
  // Stop polling, clear session cache, reset loading promise, unlink remote-settings.json

export async function loadRemoteManagedSettings(): Promise<void>
  // Cache-first: applies cached settings immediately, unblocks waiters.
  // Then runs fetchAndLoadRemoteManagedSettings() async.
  // Starts background polling if eligible.
  // Triggers settingsChangeDetector.notifyChange('policySettings') on success.

export async function refreshRemoteManagedSettings(): Promise<void>
  // Clear caches → fetch → notify (for auth state changes like login/logout)

export function startBackgroundPolling(): void
  // setInterval at POLLING_INTERVAL_MS, unref'd. Uses registerCleanup.

export function stopBackgroundPolling(): void
  // clearInterval + null state
```

**Internal Functions:**

```typescript
function sortKeysDeep(obj: unknown): unknown
  // Recursively sorts keys (matches Python json.dumps sort_keys=True)
  // Arrays sorted element-by-element, objects sorted by key.

function getRemoteManagedSettingsEndpoint(): string
  // Returns BASE_API_URL/api/claude_code/settings

function getRemoteSettingsAuthHeaders(): { headers: Record<string,string>, error?: string }
  // API key first (skipRetrievingKeyFromApiKeyHelper:true to avoid circular dep with getSettings)
  // Then OAuth tokens

async function fetchWithRetry(cachedChecksum?: string): Promise<RemoteManagedSettingsFetchResult>
  // Up to DEFAULT_MAX_RETRIES + 1 attempts with exponential backoff

async function fetchRemoteManagedSettings(cachedChecksum?: string): Promise<RemoteManagedSettingsFetchResult>
  // Single HTTP GET with If-None-Match, validates 200/204/304/404
  // 304 → cache valid (settings: null sentinel)
  // 204/404 → no settings (settings: {})
  // Multi-layer validation: RemoteManagedSettingsResponseSchema + SettingsSchema

async function saveSettings(settings: SettingsJson): Promise<void>
  // Write to remote-settings.json with mode 0o600 + datasync

async function fetchAndLoadRemoteManagedSettings(): Promise<SettingsJson | null>
  // Core fetch + load + security check + save pipeline
  // Graceful degradation: on failure, uses stale file cache if available

async function pollRemoteSettings(): Promise<void>
  // Background poll — fetches and triggers hot-reload on change
```

---

### `syncCache.ts` (112 lines)

**`isRemoteManagedSettingsEligible()` — Auth/provider eligibility cascade.**

```typescript
export function resetSyncCache(): void
  // Reset cache and delegate to leaf's resetSyncCache

export function isRemoteManagedSettingsEligible(): boolean
  // Cached (one-shot computation):
  // 1. 3p provider → false (returns (cached = setEligibility(false)))
  // 2. Custom base URL → false
  // 3. CLAUDE_CODE_ENTRYPOINT === 'local-agent' → false (Cowork VM)
  // 4. Check OAuth first (common case, avoids keychain subprocess):
  //    a. tokens with subscriptionType === null (externally-injected) → true
  //    b. tokens with CLAUDE_AI_INFERENCE_SCOPE + subscriptionType enterprise/team → true
  // 5. Console users (API key via getAnthropicApiKeyWithSource) → true
  // 6. Default → false
```

**Design rationale:** Split from `syncCacheState.ts` to break the `settings.ts → auth.ts → settings.ts` circular dependency cycle. `auth.ts` sits inside the large settings SCC; this file keeps the auth-touching part separate.

---

### `syncCacheState.ts` (96 lines)

**Leaf state module for the remote-managed-settings sync cache.**

```typescript
export function setSessionCache(value: SettingsJson | null): void
export function resetSyncCache(): void
  // sessionCache = null; eligible = undefined
export function setEligibility(v: boolean): boolean
  // Sets eligible bool, returns v
export function getSettingsPath(): string
  // Returns join(getClaudeConfigHomeDir(), 'remote-settings.json')
export function getRemoteManagedSettingsSyncFromCache(): SettingsJson | null
  // eligible !== true → return null
  // Has sessionCache → return it
  // Load from disk → if found, cache + flush stale merged settings (resetSettingsCache) → return
  // Empty → null
```

**Internal Functions:**

```typescript
function loadSettings(): SettingsJson | null
  // Sync read + json parse + BOM strip + type guard (must be object, not array)
```

**Session/file cache layering:**
1. `sessionCache` (in-memory, set after fetch) — fastest path
2. `loadSettings()` (file-based, `~/.claude/remote-settings.json`) — sync read on first call
3. On first disk hit, calls `resetSettingsCache()` to flush merged `getSettings_DEPRECATED()` cache (previously computed without policySettings layer visible)

Eligibility is tri-state: `undefined` → not yet determined (return null), `false` → ineligible (return null), `true` → proceed.

---

### `securityCheck.tsx` (74 lines)

**React blocking dialog for dangerous setting changes.**

```typescript
export type SecurityCheckResult = 'approved' | 'rejected' | 'no_check_needed'

export async function checkManagedSettingsSecurity(
  cachedSettings: SettingsJson | null,
  newSettings: SettingsJson | null,
): Promise<SecurityCheckResult>
  // Flow:
  //   1. No dangerous settings in new? → 'no_check_needed'
  //   2. Dangerous settings unchanged from cache? → 'no_check_needed'
  //   3. Non-interactive session? → 'no_check_needed'
  //   4. Show ManagedSettingsSecurityDialog (Ink/React blocking dialog) →
  //      user accepts → 'approved', user rejects → 'rejected'
  //      Fires tengu_managed_settings_security_dialog_shown/accepted/rejected analytics

export function handleSecurityCheckResult(result: SecurityCheckResult): boolean
  // result === 'rejected' → gracefulShutdownSync(1), return false
  // Otherwise return true
```

**Render context:** `AppStateProvider > KeybindingSetup > ManagedSettingsSecurityDialog`

---

### `types.ts` (31 lines)

```typescript
export const RemoteManagedSettingsResponseSchema = lazySchema(() =>
  z.object({
    uuid: z.string(),        // Settings UUID
    checksum: z.string(),    // sha256:<hex>
    settings: z.record(z.string(), z.unknown()) as z.ZodType<SettingsJson>,
    // Permissive z.record() to avoid circular dep; full validation via SettingsSchema.safeParse() in index.ts
  }),
)

export type RemoteManagedSettingsResponse = z.infer<ReturnType<typeof RemoteManagedSettingsResponseSchema>>

export type RemoteManagedSettingsFetchResult = {
  success: boolean
  settings?: SettingsJson | null  // null = 304 (cache valid)
  checksum?: string
  error?: string
  skipRetry?: boolean             // true for auth errors
}
```

---

## Section 3: `services/teamMemorySync/` (5 files)

Repo-scoped team memory sync between local filesystem and server API. Pull-first semantics (server wins), push-only-delta uploads, secret scanning.

### `index.ts` (1256 lines)

**Constants:**

```typescript
const TEAM_MEMORY_SYNC_TIMEOUT_MS = 30_000
const MAX_FILE_SIZE_BYTES = 250_000
const MAX_PUT_BODY_BYTES = 200_000
const MAX_RETRIES = 3
const MAX_CONFLICT_RETRIES = 2
```

**Types:**

```typescript
export type SyncState = {
  lastKnownChecksum: string | null        // ETag for conditional requests
  serverChecksums: Map<string, string>    // Per-key sha256:<hex> server state (for delta computation)
  serverMaxEntries: number | null         // Learned from structured 413 (GB-tunable per-org)
}
```

**Exported Functions:**

```typescript
export function createSyncState(): SyncState

export function hashContent(content: string): string
  // 'sha256:' + SHA256(UTF-8 bytes)

export function isTeamMemorySyncAvailable(): boolean
  // Requires first-party OAuth with inference + profile scopes

export async function pullTeamMemory(state: SyncState, options?: { skipEtagCache?: boolean }): Promise<{
  success: boolean; filesWritten: number; entryCount: number; notModified?: boolean; error?: string
}>
  // Fetches from server → writes entries to local dir → refreshes serverChecksums

export async function pushTeamMemory(state: SyncState): Promise<TeamMemorySyncPushResult>
  // Delta upload: only keys whose local hash differs from serverChecksums
  // Conflict resolution: on 412, GET ?view=hashes to refresh serverChecksums, retry up to MAX_CONFLICT_RETRIES
  // Secret scanning: files with detected secrets excluded from upload set
  // Batches: splits delta into ≤200KB PUT bodies to stay under gateway limit

export async function syncTeamMemory(state: SyncState): Promise<{
  success: boolean; filesPulled: number; filesPushed: number; error?: string
}>
  // Bidirectional: pull → push with conflict resolution

export function batchDeltaByBytes(delta: Record<string, string>): Array<Record<string, string>>
  // Greedy bin-packing with sorted keys for deterministic batching
```

**Internal Functions:**

```typescript
function isUsingOAuth(): boolean              // Auth check with provider + scopes
function getTeamMemorySyncEndpoint(repoSlug): string
function getAuthHeaders(): { headers?, error? }

async function fetchTeamMemoryOnce(state, repoSlug, etag?): Promise<TeamMemorySyncFetchResult>
  // Single HTTP GET with If-None-Match, validates 200/304/404

async function fetchTeamMemoryHashes(state, repoSlug): Promise<TeamMemoryHashesResult>
  // GET ?view=hashes — cheap probe for conflict resolution (no entry bodies)

async function fetchTeamMemory(state, repoSlug, etag?): Promise<TeamMemorySyncFetchResult>
  // Retry wrapper up to MAX_RETRIES

async function uploadTeamMemory(state, repoSlug, entries, ifMatchChecksum?): Promise<TeamMemorySyncUploadResult>
  // Single PUT with If-Match (optimistic locking). Parses structured 413 for max_entries.

async function readLocalTeamMemory(maxEntries): Promise<{ entries, skippedSecrets }>
  // Walks team mem dir, scans each file for secrets (PSR M22174), skips secrets,
  // truncates to maxEntries if learned cap

async function writeRemoteEntriesToLocal(entries): Promise<number>
  // Parallel writes with path validation, content comparison (skip unchanged files)

function logPull(startTime, outcome): void   // Telemetry
function logPush(startTime, outcome): void   // Telemetry
```

**API contract:**
- `GET /api/claude_code/team_memory?repo={owner/repo}` → TeamMemoryData
- `GET ...&view=hashes` → metadata + entryChecksums only
- `PUT /api/claude_code/team_memory?repo={owner/repo}` → upsert entries
- 404 = no data exists; 304 = not modified; 412 = precondition failed; 413 = too many entries

---

### `types.ts` (156 lines)

**Zod Schemas:**

```typescript
export const TeamMemoryContentSchema = lazySchema(() =>
  z.object({
    entries: z.record(z.string(), z.string()),
    entryChecksums: z.record(z.string(), z.string()).optional(),
  })
)

export const TeamMemoryDataSchema = lazySchema(() =>
  z.object({
    organizationId: z.string(),
    repo: z.string(),
    version: z.number(),
    lastModified: z.string(),
    checksum: z.string(),
    content: TeamMemoryContentSchema(),
  })
)

export const TeamMemoryTooManyEntriesSchema = lazySchema(() =>
  z.object({
    error: z.object({
      details: z.object({
        error_code: z.literal('team_memory_too_many_entries'),
        max_entries: z.number().int().positive(),
        received_entries: z.number().int().positive(),
      }),
    }),
  })
)
```

**6 Result Types:**

```typescript
export type TeamMemoryData                     // Full GET response
export type SkippedSecretFile                  // { path, ruleId, label }
export type TeamMemorySyncFetchResult          // { success, data?, isEmpty?, notModified?, checksum?, error?, skipRetry?, errorType?, httpStatus? }
export type TeamMemoryHashesResult             // { success, version?, checksum?, entryChecksums?, error?, errorType?, httpStatus? }
export type TeamMemorySyncPushResult           // { success, filesUploaded, checksum?, conflict?, error?, skippedSecrets?, errorType?, httpStatus? }
export type TeamMemorySyncUploadResult         // { success, checksum?, lastModified?, conflict?, error?, errorType?, httpStatus?, serverErrorCode?, serverMaxEntries?, serverReceivedEntries? }
```

---

### `secretScanner.ts` (324 lines)

**Client-side secret scanner for team memory. Uses curated gitleaks rules.**

**Types:**

```typescript
type SecretRule = { id: string; source: string; flags?: string }
export type SecretMatch = { ruleId: string; label: string }
```

**Exported Functions:**

```typescript
export function scanForSecrets(content: string): SecretMatch[]
  // Scans content against all compiled rules. One match per rule ID (deduplicated).
  // Actual matched text is intentionally NOT returned.

export function getSecretLabel(ruleId: string): string
  // Converts kebab-case rule ID to human-readable label (e.g., "github-pat" → "GitHub PAT")

export function redactSecrets(content: string): string
  // Replaces captured groups with [REDACTED] in-place. Preserves boundary characters.
```

**32 Curated Rules (high-confidence only):**
- Cloud providers: AWS access token, GCP API key, Azure AD client secret, DigitalOcean PAT/token
- AI APIs: Anthropic API/admin key, OpenAI API key, HuggingFace token
- Version control: GitHub PAT (classic, fine-grained, app token, OAuth, refresh), GitLab PAT/deploy token
- Communication: Slack bot/user/app token, Twilio API key, SendGrid token
- Dev tooling: npm access token, PyPI upload token, Databricks token, HashiCorp TF token, Pulumi token, Postman token
- Observability: Grafana API/cloud/service account token, Sentry user/org token
- Payment: Stripe access token, Shopify access/shared secret
- Crypto: Private key (BEGIN/END blocks)

**Anthropic API key prefix** assembled at runtime via `['sk', 'ant', 'api'].join('-')` so the literal byte sequence isn't in the external bundle (excluded-strings check). `join()` is not constant-folded by the minifier.

**Lazy compilation:** Rules compiled once on first scan. Redaction patterns compiled separately (adds `g` flag).

**JS regex portability:** Go `(?i)` flag groups rewritten to explicit character classes `[a-zA-Z]`. Trailing boundary alternations `(?:[\x60'"\s;]|\\[nr]|$)` preserved.

---

### `teamMemSecretGuard.ts` (44 lines)

**Feature-gated secret scan guard for FileWriteTool/FileEditTool.**

```typescript
export function checkTeamMemSecrets(filePath: string, content: string): string | null
  // Gated by feature('TEAMMEM')
  // Uses require() to lazy-load isTeamMemPath + scanForSecrets (bundle splitting)
  // If filePath is NOT a team memory path → return null
  // If secrets detected → returns error message listing matched labels
  // Otherwise → null (safe to write)
```

**Error message format:** `"Content contains potential secrets ({labels}) and cannot be written to team memory. Team memory is shared with all repository collaborators. Remove the sensitive content and try again."`

---

### `watcher.ts` (387 lines)

**Debounced file watcher with push-triggered sync.**

**Constants:**

```typescript
const DEBOUNCE_MS = 2000
```

**Module-level state:**

```typescript
let watcher: FSWatcher | null
let debounceTimer: ReturnType<typeof setTimeout> | null
let pushInProgress: boolean
let hasPendingChanges: boolean
let currentPushPromise: Promise<void> | null
let watcherStarted: boolean
let pushSuppressedReason: string | null
let syncState: SyncState | null
```

**Exported Functions:**

```typescript
export function isPermanentFailure(r: TeamMemorySyncPushResult): boolean
  // no_oauth / no_repo → true. 4xx (except 409/429) → true. Otherwise false.

export async function startTeamMemoryWatcher(): Promise<void>
  // Gate chain: feature('TEAMMEM') → isTeamMemoryEnabled() → isTeamMemorySyncAvailable() → getGithubRepo()
  // Initial pull from server → always starts fs.watch(dir, {recursive:true})

export async function notifyTeamMemoryWrite(): Promise<void>
  // Explicit trigger from PostToolUse hooks. Schedules push (debounced).

export async function stopTeamMemoryWatcher(): Promise<void>
  // Clear debounce timer, close watcher, await in-flight push, flush pending.

export function _resetWatcherStateForTesting(opts?): void
  // Test-only: reset all module state

export function _startFileWatcherForTesting(dir: string): Promise<void>
  // Test-only: start real fs.watch on specified dir
```

**Push suppression:** After a permanent failure (e.g., `no_oauth`, `no_repo`, 4xx except 409/429), retries are suppressed until either file deletion clears suppression (stat shows ENOENT) or session restarts.

**Watcher uses `fs.watch({recursive: true})`** (not chokidar) because:
- chokidar 4+ dropped fsevents
- Bun's kqueue fallback requires one fd per watched file
- macOS uses FSEvents for recursive → O(1) fds
- `fs.watch` doesn't distinguish add/change/unlink → uses stat to detect unlink for suppression recovery

---

## Section 4: `utils/swarm/` (14 files)

> **Note:** Actual filenames differ from the expected list in the task description. The directory contains: `constants.ts`, `spawnUtils.ts`, `teammateInit.ts`, `inProcessRunner.ts`, `It2SetupPrompt.tsx`, `leaderPermissionBridge.ts`, `permissionSync.ts`, `reconnection.ts`, `spawnInProcess.ts`, `teamHelpers.ts`, `teammateLayoutManager.ts`, `teammateModel.ts`, `teammatePromptAddendum.ts`, plus `backends/` directory.

### `constants.ts` (33 lines)

```typescript
export const TEAM_LEAD_NAME = 'team-lead'
export const SWARM_SESSION_NAME = 'claude-swarm'
export const SWARM_VIEW_WINDOW_NAME = 'swarm-view'
export const TMUX_COMMAND = 'tmux'
export const HIDDEN_SESSION_NAME = 'claude-hidden'
export const TEAMMATE_COMMAND_ENV_VAR = 'CLAUDE_CODE_TEAMMATE_COMMAND'
export const TEAMMATE_COLOR_ENV_VAR = 'CLAUDE_CODE_AGENT_COLOR'
export const PLAN_MODE_REQUIRED_ENV_VAR = 'CLAUDE_CODE_PLAN_MODE_REQUIRED'

export function getSwarmSocketName(): string
  // Returns `claude-swarm-{process.pid}` — isolates swarm operations from user's tmux sessions
```

---

### `spawnUtils.ts` (146 lines)

**Shared utilities for spawning teammates across different backends.**

```typescript
export function getTeammateCommand(): string
  // TEAMMATE_COMMAND_ENV_VAR || (bundledMode ? execPath : argv[1])

export function buildInheritedCliFlags(options?: {
  planModeRequired?: boolean
  permissionMode?: PermissionMode
}): string
  // Builds: --dangerously-skip-permissions | --permission-mode acceptEdits |
  // --model X | --settings X | --plugin-dir X | --teammate-mode X | --chrome/--no-chrome

export function buildInheritedEnvVars(): string
  // CLAUDECODE=1, CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1
  // + TEAMMATE_ENV_VARS if set: CLAUDE_CODE_USE_BEDROCK/VERTEX/FOUNDRY,
  //   ANTHROPIC_BASE_URL, CLAUDE_CONFIG_DIR, CLAUDE_CODE_REMOTE,
  //   CLAUDE_CODE_REMOTE_MEMORY_DIR, HTTPS_PROXY, https_proxy, HTTP_PROXY,
  //   http_proxy, NO_PROXY, no_proxy, SSL_CERT_FILE, NODE_EXTRA_CA_CERTS,
  //   REQUESTS_CA_BUNDLE, CURL_CA_BUNDLE
```

---

### `teammateInit.ts` (129 lines)

**Teammate initialization — registers Stop hook for idle notification.**

```typescript
export function initializeTeammateHooks(
  setAppState: (updater: (prev: AppState) => AppState) => void,
  sessionId: string,
  teamInfo: { teamName: string; agentId: string; agentName: string },
): void
  // 1. Read team file → get leadAgentId
  // 2. Apply team-wide allowed paths as tool permissions
  // 3. If agent IS the leader → skip hook registration
  // 4. Register Stop hook: on Stop → setMemberActive(false) + send idle notification to leader's mailbox
```

---

### `inProcessRunner.ts` (1552 lines)

**In-process teammate runner. Wraps `runAgent()` for in-process teammates.**

**Types:**

```typescript
export type InProcessRunnerConfig = {
  identity: TeammateIdentity
  taskId: string
  prompt: string
  agentDefinition?: CustomAgentDefinition
  teammateContext: TeammateContext
  toolUseContext: ToolUseContext
  abortController: AbortController
  model?: string
  systemPrompt?: string
  systemPromptMode?: 'default' | 'replace' | 'append'
  allowedTools?: string[]
  allowPermissionPrompts?: boolean
  description?: string
  invokingRequestId?: string
}

export type InProcessRunnerResult = {
  success: boolean
  error?: string
  messages: Message[]
}
```

**Exported Functions:**

```typescript
export async function runInProcessTeammate(config: InProcessRunnerConfig): Promise<InProcessRunnerResult>
  // Main entry point. Continuous prompt loop:
  //   1. Build system prompt (default + addendum + custom agent prompt)
  //   2. Create resolved agent definition with team-essential tools injected
  //   3. Main loop: runAgent → mark idle → waitForNextPromptOrShutdown → loop
  //   4. On completion: mark task completed, emit SDK bookend, unregister Perfetto

export function startInProcessTeammate(config: InProcessRunnerConfig): void
  // Fire-and-forget wrapper: calls runInProcessTeammate().catch(log)
```

**Key internal functions:**

```typescript
function createInProcessCanUseTool(identity, abortController, onPermissionWaitMs?): CanUseToolFn
  // Permission resolution with two paths:
  //   1. Bridge path: uses leader's ToolUseConfirm dialog with worker badge
  //   2. Fallback: mailbox-based permission request → poll for response
  // Bash classifier auto-approval checked before showing UI

async function waitForNextPromptOrShutdown(identity, abortController, taskId, ...): Promise<WaitResult>
  // 500ms poll loop checking: pendingUserMessages → mailbox messages (shutdown requests priority over team-lead over peers) → task list

function findAvailableTask(tasks): Task | undefined
  // Pending, no owner, not blocked by unresolved tasks

function formatAsTeammateMessage(from, content, color?, summary?): string
  // Wraps in <teammate-message> XML with color attribute

async function sendMessageToLeader(from, text, color, teamName): Promise<void>
async function sendIdleNotification(agentName, agentColor, teamName, options?): Promise<void>
```

**System prompt building:**
1. `replace` mode: use provided systemPrompt directly
2. Default/append: full system prompt + `TEAMMATE_SYSTEM_PROMPT_ADDENDUM` + custom agent prompt + optional append prompt
3. Agent definition always injects team-essential tools: `SendMessage`, `TeamCreate`, `TeamDelete`, `TaskCreate`, `TaskGet`, `TaskList`, `TaskUpdate`

**Auto-compaction:** When token count exceeds auto-compact threshold, compacts conversation history before each iteration. Uses isolated ToolUseContext to prevent side effects on main session.

**Per-turn abort:** Uses `currentWorkAbortController` for Escape key handling (stops current work, teammate enters idle) vs lifecycle `abortController` (kills whole teammate).

**Task state transitions:** running → idle → (new prompt) → running → ... → completed/killed/failed

---

### `It2SetupPrompt.tsx` (380 lines)

**React component for iTerm2 it2 CLI setup wizard.**

```typescript
export function It2SetupPrompt(props: {
  onDone: (result: 'installed' | 'use-tmux' | 'cancelled') => void
  tmuxAvailable: boolean
}): JSX.Element
```

**Setup steps:** `initial` → `installing` → `install-failed` → `api-instructions` → `verifying` → `success` / `failed`

**Features:**
- Auto-detects Python package manager (`uvx` > `pipx` > `pip`)
- Installs it2 via detected package manager
- Verifies it2 can communicate with iTerm2 (session list)
- Offers tmux fallback if tmux available
- Cancellable via ESC or Ctrl+C
- Uses React Compiler (`_c` memoization)

---

### `leaderPermissionBridge.ts` (54 lines)

**Module-level bridge for REPL→in-process teammate permission queue sharing.**

```typescript
export type SetToolUseConfirmQueueFn = (updater: (prev: ToolUseConfirm[]) => ToolUseConfirm[]) => void
export type SetToolPermissionContextFn = (context: ToolPermissionContext, options?: { preserveMode?: boolean }) => void

export function registerLeaderToolUseConfirmQueue(setter: SetToolUseConfirmQueueFn): void
export function getLeaderToolUseConfirmQueue(): SetToolUseConfirmQueueFn | null
export function unregisterLeaderToolUseConfirmQueue(): void

export function registerLeaderSetToolPermissionContext(setter: SetToolPermissionContextFn): void
export function getLeaderSetToolPermissionContext(): SetToolPermissionContextFn | null
export function unregisterLeaderSetToolPermissionContext(): void
```

**Purpose:** When an in-process teammate requests permissions, it uses the standard ToolUseConfirm dialog. This bridge makes the REPL's queue setter accessible from non-React code in the in-process runner.

---

### `permissionSync.ts` (928 lines)

**Synchronized permission prompts for agent swarms via file-based queue + mailbox.**

**Types:**

```typescript
export type SwarmPermissionRequest (from Zod schema)
export type PermissionResolution = {
  decision: 'approved' | 'rejected'
  resolvedBy: 'worker' | 'leader'
  feedback?: string
  updatedInput?: Record<string, unknown>
  permissionUpdates?: PermissionUpdate[]
}
export type PermissionResponse = {
  requestId: string
  decision: 'approved' | 'denied'
  timestamp: string
  feedback?: string
  updatedInput?: Record<string, unknown>
  permissionUpdates?: unknown[]
}
```

**Exported Functions:**

```typescript
export const SwarmPermissionRequestSchema  // Zod: id, workerId, workerName, workerColor?, teamName, toolName, toolUseId, description, input, permissionSuggestions, status, resolvedBy?, resolvedAt?, feedback?, updatedInput?, permissionUpdates?, createdAt

export function getPermissionDir(teamName: string): string
export function generateRequestId(): string
export function createPermissionRequest(params): SwarmPermissionRequest

export async function writePermissionRequest(request): Promise<SwarmPermissionRequest>
  // Write to pending/ dir with file locking

export async function readPendingPermissions(teamName?): Promise<SwarmPermissionRequest[]>
  // Read all pending JSON files, sort by createdAt

export async function readResolvedPermission(requestId, teamName?): Promise<SwarmPermissionRequest | null>
export async function resolvePermission(requestId, resolution, teamName?): Promise<boolean>
  // Read pending → write resolved → unlink pending → file locking

export async function cleanupOldResolutions(teamName?, maxAgeMs = 3600000): Promise<number>

export async function pollForResponse(requestId, agentName?, teamName?): Promise<PermissionResponse | null>
export async function removeWorkerResponse(requestId, agentName?, teamName?): Promise<void>
export function isTeamLeader(teamName?): boolean
export function isSwarmWorker(): boolean
export async function deleteResolvedPermission(requestId, teamName?): Promise<boolean>
export const submitPermissionRequest = writePermissionRequest

// Mailbox-based permission system:
export async function getLeaderName(teamName?): Promise<string | null>
export async function sendPermissionRequestViaMailbox(request): Promise<boolean>
export async function sendPermissionResponseViaMailbox(workerName, resolution, requestId, teamName?): Promise<boolean>

// Sandbox permission system:
export function generateSandboxRequestId(): string
export async function sendSandboxPermissionRequestViaMailbox(host, requestId, teamName?): Promise<boolean>
export async function sendSandboxPermissionResponseViaMailbox(workerName, requestId, host, allow, teamName?): Promise<boolean>
```

**Directory structure:** `~/.claude/teams/{teamName}/permissions/pending/` and `resolved/`

**Flow:** Worker sends request to leader's mailbox → leader polls → user approves/denies → leader sends response to worker's mailbox → worker polls for response → continues execution.

---

### `reconnection.ts` (119 lines)

**Swarm context initialization for fresh spawns and resumed sessions.**

```typescript
export function computeInitialTeamContext(): AppState['teamContext'] | undefined
  // Synchronously computes teamContext from CLI args (via getDynamicTeamContext).
  // Reads team file for leadAgentId. Called in main.tsx before first render.

export function initializeTeammateContextFromSession(
  setAppState: (updater: (prev: AppState) => AppState) => void,
  teamName: string,
  agentName: string,
): void
  // For resumed sessions with teamName/agentName stored in transcript.
  // Finds member in team file, sets teamContext in AppState.
```

---

### `spawnInProcess.ts` (328 lines)

**In-process teammate spawning — creates task, registers in AppState.**

```typescript
export type SpawnContext = {
  setAppState: SetAppStateFn
  toolUseId?: string
}

export type InProcessSpawnConfig = {
  name: string
  teamName: string
  prompt: string
  color?: string
  planModeRequired: boolean
  model?: string
}

export type InProcessSpawnOutput = {
  success: boolean
  agentId: string
  taskId?: string
  abortController?: AbortController
  teammateContext?: ReturnType<typeof createTeammateContext>
  error?: string
}

export async function spawnInProcessTeammate(
  config: InProcessSpawnConfig,
  context: SpawnContext,
): Promise<InProcessSpawnOutput>
  // 1. Format agentId (name@team)
  // 2. Create AbortController (independent, not linked to parent)
  // 3. Create TeammateContext for AsyncLocalStorage
  // 4. Register Perfetto agent
  // 5. Create InProcessTeammateTaskState in AppState via registerTask
  // 6. Register cleanup handler

export function killInProcessTeammate(taskId: string, setAppState: SetAppStateFn): boolean
  // Aborts controller, calls cleanup, updates status to 'killed',
  // removes from teamContext.teammates, removes member from team file,
  // emits SDK bookend, schedules eviction
```

---

### `teamHelpers.ts` (683 lines)

**Team file management (config.json), worktree operations, cleanup.**

**Types:**

```typescript
export type TeamAllowedPath = {
  path: string
  toolName: string
  addedBy: string
  addedAt: number
}

export type TeamFile = {
  name: string
  description?: string
  createdAt: number
  leadAgentId: string
  leadSessionId?: string
  hiddenPaneIds?: string[]
  teamAllowedPaths?: TeamAllowedPath[]
  members: Array<{
    agentId: string
    name: string
    agentType?: string
    model?: string
    prompt?: string
    color?: string
    planModeRequired?: boolean
    joinedAt: number
    tmuxPaneId: string
    cwd: string
    worktreePath?: string
    sessionId?: string
    subscriptions: string[]
    backendType?: BackendType
    isActive?: boolean
    mode?: PermissionMode
  }>
}

export type SpawnTeamOutput = { team_name: string; team_file_path: string; lead_agent_id: string }
export type CleanupOutput = { success: boolean; message: string; team_name?: string }
export type Input = z.infer<...> // spawnTeam | cleanup operations
export type Output = SpawnTeamOutput
```

**Exported Functions:**

```typescript
export const inputSchema = lazySchema(() => z.strictObject({ operation: z.enum(...), agent_type?, team_name?, description? }))

export function sanitizeName(name: string): string                // [^a-zA-Z0-9] → -, lowercase
export function sanitizeAgentName(name: string): string           // @ → -
export function getTeamDir(teamName: string): string              // ~/.claude/teams/{sanitized}
export function getTeamFilePath(teamName: string): string         // teamDir/config.json

export function readTeamFile(teamName: string): TeamFile | null   // sync
export async function readTeamFileAsync(teamName: string): Promise<TeamFile | null>
export async function writeTeamFileAsync(teamName, teamFile): Promise<void>

export function removeTeammateFromTeamFile(teamName, identifier): boolean
export function addHiddenPaneId(teamName, paneId): boolean
export function removeHiddenPaneId(teamName, paneId): boolean
export function removeMemberFromTeam(teamName, tmuxPaneId): boolean
export function removeMemberByAgentId(teamName, agentId): boolean

export function setMemberMode(teamName, memberName, mode: PermissionMode): boolean
export function syncTeammateMode(mode: PermissionMode, teamNameOverride?): void
export function setMultipleMemberModes(teamName, modeUpdates: Array<{memberName, mode}>): boolean
export async function setMemberActive(teamName, memberName, isActive): Promise<void>

export function registerTeamForSessionCleanup(teamName: string): void
export function unregisterTeamForSessionCleanup(teamName: string): void
export async function cleanupSessionTeams(): Promise<void>        // Kill orphaned panes → cleanup dirs
export async function cleanupTeamDirectories(teamName: string): Promise<void>  // Destroy worktrees → rm team dir → rm tasks dir
```

---

### `teammateLayoutManager.ts` (107 lines)

**Teammate color assignment and pane management delegation.**

```typescript
export function assignTeammateColor(teammateId: string): AgentColorName
  // Round-robin from AGENT_COLORS palette. Idempotent (returns existing if set).

export function getTeammateColor(teammateId: string): AgentColorName | undefined
export function clearTeammateColors(): void

export async function isInsideTmux(): Promise<boolean>

export async function createTeammatePaneInSwarmView(
  teammateName: string, teammateColor: AgentColorName
): Promise<{ paneId: string; isFirstTeammate: boolean }>
  // Delegates to detected PaneBackend

export async function enablePaneBorderStatus(windowTarget?, useSwarmSocket?): Promise<void>
export async function sendCommandToPane(paneId, command, useSwarmSocket?): Promise<void>
```

---

### `teammateModel.ts` (10 lines)

```typescript
export function getHardcodedTeammateModelFallback(): string
  // Returns CLAUDE_OPUS_4_6_CONFIG[getAPIProvider()] — provider-aware fallback model
```

---

### `teammatePromptAddendum.ts` (18 lines)

```typescript
export const TEAMMATE_SYSTEM_PROMPT_ADDENDUM: string
  // Instructions about SendMessage tool, team lead coordination, task system.
  // "Just writing a response in text is not visible to others on your team - you MUST use the SendMessage tool."
```

---

## Section 5: `utils/swarm/backends/` (9 files)

Swarm communication backends — tmux, iTerm2, and in-process execution.

### `types.ts` (311 lines)

**All backend type definitions.**

```typescript
export type BackendType = 'tmux' | 'iterm2' | 'in-process'
export type PaneBackendType = 'tmux' | 'iterm2'
export type PaneId = string

export type CreatePaneResult = {
  paneId: PaneId
  isFirstTeammate: boolean
}

export type PaneBackend = {
  readonly type: BackendType
  readonly displayName: string
  readonly supportsHideShow: boolean
  isAvailable(): Promise<boolean>
  isRunningInside(): Promise<boolean>
  createTeammatePaneInSwarmView(name: string, color: AgentColorName): Promise<CreatePaneResult>
  sendCommandToPane(paneId: PaneId, command: string, useExternalSession?: boolean): Promise<void>
  setPaneBorderColor(paneId: PaneId, color: AgentColorName, useExternalSession?: boolean): Promise<void>
  setPaneTitle(paneId: PaneId, name: string, color: AgentColorName, useExternalSession?: boolean): Promise<void>
  enablePaneBorderStatus(windowTarget?: string, useExternalSession?: boolean): Promise<void>
  rebalancePanes(windowTarget: string, hasLeader: boolean): Promise<void>
  killPane(paneId: PaneId, useExternalSession?: boolean): Promise<boolean>
  hidePane(paneId: PaneId, useExternalSession?: boolean): Promise<boolean>
  showPane(paneId: PaneId, targetWindowOrPane: string, useExternalSession?: boolean): Promise<boolean>
}

export type BackendDetectionResult = {
  backend: PaneBackend
  isNative: boolean
  needsIt2Setup?: boolean
}

export type TeammateIdentity = {
  name: string
  teamName: string
  color?: AgentColorName
  planModeRequired?: boolean
}

export type TeammateSpawnConfig = TeammateIdentity & {
  prompt: string
  cwd: string
  model?: string
  systemPrompt?: string
  systemPromptMode?: 'default' | 'replace' | 'append'
  worktreePath?: string
  parentSessionId: string
  permissions?: string[]
  allowPermissionPrompts?: boolean
}

export type TeammateSpawnResult = {
  success: boolean
  agentId: string
  error?: string
  abortController?: AbortController
  taskId?: string
  paneId?: PaneId
}

export type TeammateMessage = {
  text: string
  from: string
  color?: string
  timestamp?: string
  summary?: string
}

export type TeammateExecutor = {
  readonly type: BackendType
  isAvailable(): Promise<boolean>
  spawn(config: TeammateSpawnConfig): Promise<TeammateSpawnResult>
  sendMessage(agentId: string, message: TeammateMessage): Promise<void>
  terminate(agentId: string, reason?: string): Promise<boolean>
  kill(agentId: string): Promise<boolean>
  isActive(agentId: string): Promise<boolean>
}

export function isPaneBackend(type: BackendType): type is 'tmux' | 'iterm2'
```

---

### `detection.ts` (128 lines)

**Environment detection for tmux/iTerm2.**

```typescript
const ORIGINAL_USER_TMUX = process.env.TMUX           // Captured at module load (Shell.ts may override)
const ORIGINAL_TMUX_PANE = process.env.TMUX_PANE       // Captured at module load

export function isInsideTmuxSync(): boolean
  // !!ORIGINAL_USER_TMUX — synchronous, no caching needed

export async function isInsideTmux(): Promise<boolean>
  // Cached version — captures at module load, not dynamic env

export function getLeaderPaneId(): string | null
  // ORIGINAL_TMUX_PANE (e.g., %0) or null

export async function isTmuxAvailable(): Promise<boolean>
  // tmux -V → code === 0

export function isInITerm2(): boolean
  // TERM_PROGRAM === 'iTerm.app' || !!ITERM_SESSION_ID || env.terminal === 'iTerm.app'
  // Cached result

export async function isIt2CliAvailable(): Promise<boolean>
  // it2 session list → code === 0 (uses session list, not --version, because
  // --version succeeds even when Python API is disabled)

export function resetDetectionCache(): void
  // Test-only: clears isInsideTmuxCached, isInITerm2Cached
```

---

### `TmuxBackend.ts` (764 lines)

**Tmux pane management backend. Implements `PaneBackend`.**

```typescript
export class TmuxBackend implements PaneBackend {
  readonly type = 'tmux' as const
  readonly displayName = 'tmux'
  readonly supportsHideShow = true

  async isAvailable(): Promise<boolean>
  async isRunningInside(): Promise<boolean>

  async createTeammatePaneInSwarmView(name, color): Promise<CreatePaneResult>
    // Lock-protected. Two modes:
    //   Inside tmux: createTeammatePaneWithLeader — split-window -h, leader at 30%
    //   Outside: createTeammatePaneExternal — external claude-swarm session, tiled layout

  async sendCommandToPane(paneId, command, useExternalSession?): Promise<void>
    // send-keys to target pane with Enter

  async setPaneBorderColor(paneId, color, useExternalSession?): Promise<void>
    // select-pane -P bg=default,fg={color} + pane options

  async setPaneTitle(paneId, name, color, useExternalSession?): Promise<void>
    // select-pane -T {name} + pane-border-format with colored title

  async enablePaneBorderStatus(windowTarget?, useExternalSession?): Promise<void>
    // set-option -w pane-border-status top

  async rebalancePanes(windowTarget, hasLeader): Promise<void>
    // With leader: main-vertical layout, leader at 30%
    // Without: tiled layout

  async killPane(paneId, useExternalSession?): Promise<boolean>
    // kill-pane -t {paneId}

  async hidePane(paneId, useExternalSession?): Promise<boolean>
    // break-pane -d to HIDDEN_SESSION_NAME

  async showPane(paneId, targetWindowOrPane, useExternalSession?): Promise<boolean>
    // join-pane -h back, then main-vertical layout, resize leader to 30%
}
```

**Internal helpers:**
```typescript
function acquirePaneCreationLock(): Promise<() => void>
function getTmuxColorName(color: AgentColorName): string      // Maps to tmux colors (e.g., orange→colour208)
function runTmuxInUserSession(args): Promise<...>              // tmux with default socket
function runTmuxInSwarm(args): Promise<...>                    // tmux -L claude-swarm-{pid}

private async getCurrentPaneId(): Promise<string | null>
private async getCurrentWindowTarget(): Promise<string | null>
private async getCurrentWindowPaneCount(windowTarget?, useSwarmSocket?): Promise<number | null>
private async hasSessionInSwarm(sessionName): Promise<boolean>
private async createExternalSwarmSession(): Promise<{windowTarget, paneId}>
private async createTeammatePaneWithLeader(name, color): Promise<CreatePaneResult>
private async createTeammatePaneExternal(name, color): Promise<CreatePaneResult>
private async rebalancePanesWithLeader(windowTarget): Promise<void>
private async rebalancePanesTiled(windowTarget): Promise<void>
```

**PANE_SHELL_INIT_DELAY_MS = 200** — wait after pane creation for shell initialization (rc files, prompts like starship/oh-my-zsh).

**Self-registers at module load:** `registerTmuxBackend(TmuxBackend)` at bottom of file — side effect for registry pattern (avoids circular deps).

---

### `ITermBackend.ts` (370 lines)

**iTerm2 native split pane backend via it2 CLI. Implements `PaneBackend`.**

```typescript
export class ITermBackend implements PaneBackend {
  readonly type = 'iterm2' as const
  readonly displayName = 'iTerm2'
  readonly supportsHideShow = false

  async isAvailable(): Promise<boolean>
    // isInITerm2() && isIt2CliAvailable()

  async isRunningInside(): Promise<boolean>
    // isInITerm2()

  async createTeammatePaneInSwarmView(name, color): Promise<CreatePaneResult>
    // Lock-protected. Layout: leader on left, teammates stacked vertically on right.
    // First: session split -v -s {leaderSessionId}
    // Subsequent: session split -s {lastTeammateId}
    // Dead-session recovery: prune dead ID + retry (confirmed via session list before pruning)

  async sendCommandToPane(paneId, command, useExternalSession?): Promise<void>
    // session run -s {paneId} {command}

  async setPaneBorderColor(paneId, color): Promise<void>       // No-op (performance)
  async setPaneTitle(paneId, name, color): Promise<void>        // No-op (performance)
  async enablePaneBorderStatus(): Promise<void>                 // No-op (iTerm2 doesn't have this concept)
  async rebalancePanes(): Promise<void>                         // No-op (auto-balanced)

  async killPane(paneId, useExternalSession?): Promise<boolean>
    // session close -f -s {paneId} (-f required to bypass confirm preference)
    // Also cleans up tracked session IDs

  async hidePane(): Promise<boolean>                            // Unsupported → returns false
  async showPane(): Promise<boolean>                            // Unsupported → returns false
}
```

**At-fault recovery:** If a targeted teammate session is dead (user closed via Cmd+W or process crash), prune it from tracked IDs and retry with next-to-last. `session list` confirms dead-target vs systemic failure to avoid corrupting state.

**Session tracking:** `teammateSessionIds[]` + `firstPaneUsed` flag. Cleaned on kill.

**Self-registers at module load:** `registerITermBackend(ITermBackend)`.

---

### `InProcessBackend.ts` (339 lines)

**In-process teammate execution backend. Implements `TeammateExecutor`.**

```typescript
export class InProcessBackend implements TeammateExecutor {
  readonly type = 'in-process' as const

  private context: ToolUseContext | null = null

  setContext(context: ToolUseContext): void
  async isAvailable(): Promise<boolean>           // Always true

  async spawn(config: TeammateSpawnConfig): Promise<TeammateSpawnResult>
    // Delegates to spawnInProcessTeammate → startInProcessTeammate
    // Strips parent's messages to avoid pinning conversation

  async sendMessage(agentId: string, message: TeammateMessage): Promise<void>
    // Writes to file-based mailbox via writeToMailbox

  async terminate(agentId: string, reason?: string): Promise<boolean>
    // Creates shutdown request → writes to mailbox → sets shutdownRequested flag
    // Don't re-send if already pending

  async kill(agentId: string): Promise<boolean>
    // Delegates to killInProcessTeammate(taskId, setAppState)

  async isActive(agentId: string): Promise<boolean>
    // Checks task status === 'running' and abortController.signal not aborted
}

export function createInProcessBackend(): InProcessBackend
```

---

### `PaneBackendExecutor.ts` (354 lines)

**Adapter: `PaneBackend` → `TeammateExecutor` interface.**

```typescript
export class PaneBackendExecutor implements TeammateExecutor {
  readonly type: BackendType

  private backend: PaneBackend
  private context: ToolUseContext | null = null
  private spawnedTeammates: Map<string, { paneId: string; insideTmux: boolean }>
  private cleanupRegistered = false

  constructor(backend: PaneBackend)

  setContext(context: ToolUseContext): void
  async isAvailable(): Promise<boolean>

  async spawn(config: TeammateSpawnConfig): Promise<TeammateSpawnResult>
    // 1. Assign color, create pane via backend
    // 2. Build CLI command: cd {cwd} && env {envVars} {binary} --agent-id {id} --agent-name {name} ...
    //    with inherited CLI flags and env vars from spawnUtils
    // 3. Send command to pane
    // 4. Register cleanup to kill all spawned panes on leader exit
    // 5. Write initial prompt to teammate's mailbox

  async sendMessage(agentId: string, message: TeammateMessage): Promise<void>
  async terminate(agentId: string, reason?: string): Promise<boolean>
  async kill(agentId: string): Promise<boolean>
  async isActive(agentId: string): Promise<boolean>
}

export function createPaneBackendExecutor(backend: PaneBackend): PaneBackendExecutor
```

---

### `registry.ts` (464 lines)

**Backend registry: detection, caching, executor creation.**

```typescript
export async function ensureBackendsRegistered(): Promise<void>
  // Dynamically imports TmuxBackend.js and ITermBackend.js (module-level side effects register them)

export function registerTmuxBackend(backendClass: new () => PaneBackend): void
export function registerITermBackend(backendClass: new () => PaneBackend): void

export async function detectAndGetBackend(): Promise<BackendDetectionResult>
  // Cached result. Priority:
  //   1. Inside tmux → tmux (always)
  //   2. In iTerm2 with it2 → iTerm2
  //   3. In iTerm2 without it2: fallback to tmux if available; if no tmux → throw
  //   4. Not in tmux/iTerm2: tmux external session if available; otherwise throw

export function getBackendByType(type: PaneBackendType): PaneBackend
export function getCachedBackend(): PaneBackend | null
export function getCachedDetectionResult(): BackendDetectionResult | null

export function markInProcessFallback(): void
  // Records that spawn fell back to in-process. Subsequent spawns short-circuit.

export function isInProcessEnabled(): boolean
  // Logic:
  //   Non-interactive session → true
  //   teammateMode === 'in-process' → true
  //   teammateMode === 'tmux' → false
  //   teammateMode === 'auto': fallback active → true; inside tmux/iTerm2 → false; else → true

export function getResolvedTeammateMode(): 'in-process' | 'tmux'

export function getInProcessBackend(): TeammateExecutor

export async function getTeammateExecutor(preferInProcess: boolean = false): Promise<TeammateExecutor>
  // preferInProcess && isInProcessEnabled() → InProcessBackend
  // Otherwise → PaneBackendExecutor (lazy-created via detectAndGetBackend)

export function resetBackendDetection(): void
  // Test-only: clears all caches
```

**Cached state:**
- `cachedBackend`: PaneBackend | null
- `cachedDetectionResult`: BackendDetectionResult | null
- `cachedInProcessBackend`: TeammateExecutor | null
- `cachedPaneBackendExecutor`: TeammateExecutor | null
- `inProcessFallbackActive`: boolean
- `backendsRegistered`: boolean

**Platform-specific tmux install instructions** for macOS (`brew`), Linux/WSL (`apt`/`dnf`), Windows (WSL).

---

### `it2Setup.ts` (245 lines)

**iTerm2 it2 CLI setup utilities (installation, verification, preferences).**

```typescript
export type PythonPackageManager = 'uvx' | 'pipx' | 'pip'

export type It2InstallResult = { success: boolean; error?: string; packageManager?: PythonPackageManager }
export type It2VerifyResult = { success: boolean; error?: string; needsPythonApiEnabled?: boolean }

export async function detectPythonPackageManager(): Promise<PythonPackageManager | null>
  // Checks: which uv → uvx; which pipx → pipx; which pip/pip3 → pip; none → null

export async function isIt2CliAvailable(): Promise<boolean>
  // which it2 → code === 0 (note: different from detection.ts's it2 session list check)

export async function installIt2(packageManager: PythonPackageManager): Promise<It2InstallResult>
  // Runs from homedir() to avoid project-level pip.conf/uv.toml (malicious redirect attack surface)
  // uvx: uv tool install it2
  // pipx: pipx install it2
  // pip: pip install --user it2 (fallback: pip3)

export async function verifyIt2Setup(): Promise<It2VerifyResult>
  // 1. Check it2 installed (which it2)
  // 2. Run it2 session list to test Python API connection
  // 3. Parse stderr for common Python API errors

export function getPythonApiInstructions(): string[]
  // Instructions for enabling Python API in iTerm2 preferences

export function markIt2SetupComplete(): void
  // Sets globalConfig.iterm2It2SetupComplete = true

export function setPreferTmuxOverIterm2(prefer: boolean): void
  // Sets globalConfig.preferTmuxOverIterm2

export function getPreferTmuxOverIterm2(): boolean
  // Reads globalConfig.preferTmuxOverIterm2
```

---

### `teammateModeSnapshot.ts` (87 lines)

**Captures teammate mode at startup (prevents runtime changes from affecting current session).**

```typescript
export type TeammateMode = 'auto' | 'tmux' | 'in-process'

export function setCliTeammateModeOverride(mode: TeammateMode): void
  // Set from --teammate-mode CLI flag before capture

export function getCliTeammateModeOverride(): TeammateMode | null

export function clearCliTeammateModeOverride(newMode: TeammateMode): void
  // User changed setting in UI → null override + update snapshot

export function captureTeammateModeSnapshot(): void
  // CLI override > config.teammateMode > 'auto' default

export function getTeammateModeFromSnapshot(): TeammateMode
  // Returns captured mode. If capture never called → auto-captures + logs warning.
  // Fallback to 'auto' if somehow null.
```

---

## File Count Summary

| Directory | File Count | Total Lines |
|-----------|-----------|-------------|
| `services/autoDream/` | 4 | ~550 |
| `services/remoteManagedSettings/` | 5 | ~951 |
| `services/teamMemorySync/` | 5 | ~2,167 |
| `utils/swarm/` | 14 | ~4,805 |
| `utils/swarm/backends/` | 9 | ~3,106 |
| **Total** | **37** | **~11,579** |
