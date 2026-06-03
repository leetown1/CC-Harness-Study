# Services Layer — Unverified Fill (Now Source-Verified)

> **Scope**: 18 service files previously marked unverified in `05-service-gap-fill.md`
> **Purpose**: Behavior-level documentation with accurate exports, triggers, and integration points verified against source (May 2026 audit).

---

## 1. `services/toolUseSummary/toolUseSummaryGenerator.ts` (~112 lines)

Generates a **one-line Haiku label** for a completed tool batch (SDK/mobile progress rows).

| Export | Purpose |
|---|---|
| `generateToolUseSummary(params)` | Returns summary string or `null` on failure |

**Behavior:**
- Skips when `tools.length === 0`
- Builds truncated JSON summaries (300 chars per input/output) for each tool
- Calls `queryHaiku()` with `querySource: 'tool_use_summary_generation'`, prompt caching enabled
- System prompt asks for git-commit-subject style (~30 char) past-tense labels
- Failures are logged with `E_TOOL_USE_SUMMARY_GENERATION_FAILED` but never throw

---

## 2. `services/MagicDocs/` (2 files)

Auto-maintains markdown files tagged with `# MAGIC DOC: [title]` on the first line.

### 2.1 `magicDocs.ts` (~254 lines)

| Export | Purpose |
|---|---|
| `initMagicDocs()` | Register post-sampling hook + `FileReadTool` listener |
| `detectMagicDocHeader(content)` | Parse header + optional italic instruction line |
| `registerMagicDoc(filePath)` | Track path (once per file) |
| `clearTrackedMagicDocs()` | Reset tracked map |

**Behavior:**
- On Read of a magic-doc file, registers path and runs updates via built-in agent (`runAgent`)
- Agent has `FileReadTool` + `FileEditTool`; updates run sequentially (`sequential()` queue)
- Post-sampling hook skips when last assistant turn has tool calls in flight
- Header pattern: `/^#\s*MAGIC\s+DOC:\s*(.+)$/im`; optional `_italic_` instructions on next line

### 2.2 `prompts.ts` (~127 lines)

| Export | Purpose |
|---|---|
| `buildMagicDocsUpdatePrompt(...)` | Async prompt for update agent |

---

## 3. `services/extractMemories/` (2 files)

Extracts durable memories to **auto-memory directory** (`~/.claude/projects/<path>/memory/`), not session-memory markdown.

### 3.1 `extractMemories.ts` (~615 lines)

| Export | Purpose |
|---|---|
| `initExtractMemories()` | Closure-scoped state; registers stop-hook handler |
| `executeExtractMemories(ctx)` | Run extraction fork |
| `drainPendingExtraction()` | Flush on shutdown |
| `createAutoMemCanUseTool(memoryDir)` | Deny writes outside auto-mem paths |

**Behavior:**
- Triggered at end of complete query loop (no pending tool calls) via `handleStopHooks`
- Uses `runForkedAgent()` for cache sharing with main thread
- Tools allowed: Read, Write, Edit, Glob, Grep, Bash (scoped), REPL (ant)
- Scans existing memory via `scanMemoryFiles()` + manifest formatting
- GrowthBook gate: `tengu_auto_memory` (cached, non-blocking)
- Team memory paths included when `TEAMMEM` bundle feature enabled

### 3.2 `prompts.ts` (~154 lines)

| Export | Purpose |
|---|---|
| `buildExtractAutoOnlyPrompt(...)` | Auto-memory extraction prompt |
| `buildExtractCombinedPrompt(...)` | Auto + team memory combined prompt |

---

## 4. `services/autoDream/` (4 files)

Background cross-session memory consolidation ("dreaming").

### 4.1 `autoDream.ts` (~324 lines)

| Export | Purpose |
|---|---|
| `initAutoDream()` | Closure-scoped; registers post-sampling hook |
| `executeAutoDream(ctx)` | Run consolidation when gates pass |

**Gate order (cheapest first):**
1. `isAutoDreamEnabled()` — separate GB gate in `config.ts`
2. Time: hours since `lastConsolidatedAt >= minHours` (default 24, from `tengu_onyx_plover`)
3. Sessions: count transcripts with mtime > lastConsolidatedAt >= minSessions (default 5)
4. Lock: `tryAcquireConsolidationLock()` prevents concurrent runs

Uses `runForkedAgent()` with `/dream`-style consolidation prompt; registers `DreamTask` for UI progress.

### 4.2 `consolidationLock.ts` (~140 lines)

File-based lock in project dir: `readLastConsolidatedAt()`, `tryAcquireConsolidationLock()`, `rollbackConsolidationLock()`, `listSessionsTouchedSince()`, `recordConsolidation()`.

### 4.3 `consolidationPrompt.ts` (~65 lines)

`buildConsolidationPrompt()` — prompt for consolidation fork.

### 4.4 `config.ts` (~21 lines)

`isAutoDreamEnabled()` — feature gate (separate from scheduling config).

---

## 5. `services/tips/` (3 files)

Contextual tips shown on loading spinner.

### 5.1 `tipRegistry.ts` (~686 lines)

| Export | Purpose |
|---|---|
| `getRelevantTips(context?)` | Returns tips whose predicates match current session |

~50 tips defined inline with async predicates (IDE installed, model, referral eligibility, file history, marketplace, etc.). No public `registerTip()` API.

### 5.2 `tipScheduler.ts` (~58 lines)

| Export | Purpose |
|---|---|
| `selectTipWithLongestTimeSinceShown(tips)` | Pick least-recently-shown eligible tip |
| `getTipToShowOnSpinner()` | Async selection for spinner |
| `recordShownTip(tip)` | Mark shown this session |

### 5.3 `tipHistory.ts` (~17 lines)

| Export | Purpose |
|---|---|
| `recordTipShown(tipId)` | Persist to global config |
| `getSessionsSinceLastShown(tipId)` | Cooldown counter |

---

## 6. `services/PromptSuggestion/` (2 files)

Ghost-text prompt suggestions + speculative pre-computation.

### 6.1 `promptSuggestion.ts` (~523 lines)

| Export | Purpose |
|---|---|
| `shouldEnablePromptSuggestion()` | Env → `tengu_chomp_inflection` → non-interactive/teammate checks |
| `tryGenerateSuggestion()` / `generateSuggestion()` | Haiku fork for suggestion text |
| `executePromptSuggestion()` | Inject accepted suggestion into input |
| `abortPromptSuggestion()` | Cancel in-flight generation |
| `shouldFilterSuggestion()` | Dedup/low-quality filter |
| `logSuggestionOutcome()` / `logSuggestionSuppressed()` | Analytics |

**Behavior:**
- Disabled for non-interactive sessions, swarm teammates, and when rate limits are active
- Uses `runForkedAgent()` with cache-safe params from main thread
- Integrates with speculation: may accept pre-computed response on Tab

### 6.2 `speculation.ts` (~991 lines)

| Export | Purpose |
|---|---|
| `isSpeculationEnabled()` | Settings + GB gate |
| `startSpeculation()` | Begin parallel cache-shared API call |
| `acceptSpeculation()` / `abortSpeculation()` | User accept/cancel |
| `prepareMessagesForInjection()` | Strip/inject messages for fork |
| `handleSpeculationAccept()` | Accept flow coordinator |

**Behavior:**
- Pre-computes likely next assistant response while user reads current output
- Stores state in `AppState.speculation`; aborted on new user input or model change
- Cache sharing requires identical tool list + system prompt fingerprint

---

## 7. `services/settingsSync/` (2 files)

OAuth settings + memory file sync across Claude Code environments.

### 7.1 `index.ts` (~581 lines)

| Export | Purpose |
|---|---|
| `uploadUserSettingsInBackground()` | Interactive CLI push (changed keys only) |
| `downloadUserSettings()` | CCR download (memoized promise) |
| `redownloadUserSettings()` | Force re-download |

**Behavior:**
- Push gated: `UPLOAD_USER_SETTINGS` bundle + `tengu_enable_settings_sync_push` + interactive + OAuth
- Upload is incremental via `pickBy` diff against last-known remote state
- Download runs before plugin installation in CCR mode
- 500KB per-file cap; 10s timeout; 3 retries with exponential backoff
- Sync keys defined in `SYNC_KEYS` allowlist (types.ts)

### 7.2 `types.ts` (~67 lines)

Zod schemas: `UserSyncContentSchema`, `UserSyncDataSchema`, result types, `SYNC_KEYS`.

---

## 8. `services/policyLimits/` (2 files)

Org-level CLI feature restrictions from API.

### 8.1 `index.ts` (~663 lines)

| Export | Purpose |
|---|---|
| `initializePolicyLimitsLoadingPromise()` | Early awaitable promise (30s timeout) |
| `isPolicyLimitsEligible()` | API-key users + Team/Enterprise OAuth |
| `loadPolicyLimits()` / `refreshPolicyLimits()` | Fetch with ETag disk cache |
| `waitForPolicyLimitsToLoad()` | Block until initial load |
| `isPolicyAllowed(policy)` | Check named restriction string |
| `startBackgroundPolling()` / `stopBackgroundPolling()` | 1-hour poll |

**Behavior:**
- **Fails open** — fetch errors leave restrictions empty
- Cache: `policy-limits.json` in config dir
- 10s fetch timeout, 5 retries, exponential backoff via `getRetryDelay()`

### 8.2 `types.ts` (~27 lines)

`PolicyLimitsResponseSchema`, `PolicyLimitsFetchResult`.

---

## 9. `services/remoteManagedSettings/` (5 files)

Enterprise managed settings with checksum validation.

### 9.1 `index.ts` (~638 lines)

| Export | Purpose |
|---|---|
| `initializeRemoteManagedSettingsLoadingPromise()` | Early awaitable promise |
| `loadRemoteManagedSettings()` / `refreshRemoteManagedSettings()` | Fetch from `/api/claude_code/settings` |
| `computeChecksumFromSettings()` | Sorted-keys SHA-256 checksum |
| `isEligibleForRemoteManagedSettings()` | Enterprise/Team OAuth + API key |
| `waitForRemoteManagedSettingsToLoad()` | Block until load |
| `clearRemoteManagedSettingsCache()` | Drop cache |
| `startBackgroundPolling()` / `stopBackgroundPolling()` | 1-hour poll |

**Behavior:**
- **Fails open** on network errors
- Security UI gate: `checkManagedSettingsSecurity()` in `securityCheck.tsx` compares checksums before applying changes
- Session cache via `syncCacheState.ts`

Supporting: `syncCache.ts` (eligibility), `syncCacheState.ts` (session cache), `types.ts` (Zod schema).

---

## 10. `services/oauth/` (5 files)

First-party OAuth login flow (distinct from MCP OAuth in `services/mcp/auth.ts`).

### 10.1 `index.ts` (~198 lines)

**`OAuthService` class:**
- `startOAuthFlow(authURLHandler, options?)` — full PKCE flow
- Supports automatic localhost callback + manual code paste
- `skipBrowserOpen` for SDK control protocol

### 10.2 `client.ts` (~566 lines)

| Export | Purpose |
|---|---|
| `buildAuthUrl()` | Manual + automatic auth URLs |
| `exchangeCodeForTokens()` / `refreshOAuthToken()` | Token endpoint |
| `fetchProfileInfo()` | Subscription tier + rate limit tier |
| `isOAuthTokenExpired()` | Expiry with buffer |
| `populateOAuthAccountInfoIfNeeded()` | Persist account metadata |
| `getOrganizationUUID()` | Org UUID lookup |
| `shouldUseClaudeAIAuth()` | Scope check |

### 10.3 `auth-code-listener.ts` (~211 lines)

**`AuthCodeListener` class** — localhost HTTP server, state validation, success/failure HTML.

### 10.4 `crypto.ts` (~23 lines)

PKCE: `generateCodeVerifier()`, `generateCodeChallenge()`, `generateState()`.

### 10.5 `getOauthProfile.ts` (~35 lines)

`getOauthProfileFromApiKey()`, `getOauthProfileFromOauthToken()`.

---

## 11. `services/teamMemorySync/` (5 files)

Per-repo team memory sync via `/api/claude_code/team_memory`.

### 11.1 `index.ts` (~1256 lines)

| Export | Purpose |
|---|---|
| `createSyncState()` | Per-session sync state object |
| `pullTeamMemory(state)` | Download; server wins per-key |
| `pushTeamMemory(state)` | Delta upload by content hash |
| `syncTeamMemory(state)` | Full sync orchestrator |
| `isTeamMemorySyncAvailable()` | Feature + auth gate |
| `batchDeltaByBytes(entries)` | Split PUT bodies (200KB cap) |
| `hashContent(content)` | SHA-256 content hash |

**Sync semantics:**
- Pull overwrites local files with server content
- Push uploads only keys whose hash differs from `serverChecksums`
- **Local deletes do not propagate** — next pull restores deleted files
- Secret scan before push via `scanForSecrets()`
- Per-entry cap: 250KB; gateway PUT body cap: 200KB

### 11.2 `secretScanner.ts` (~324 lines)

Regex-based secret detection: `scanForSecrets()`, `redactSecrets()`, `getSecretLabel()`.

### 11.3 `watcher.ts` (~387 lines)

File watcher: `startTeamMemoryWatcher()`, `stopTeamMemoryWatcher()`, `notifyTeamMemoryWrite()` (debounced push).

### 11.4 `teamMemSecretGuard.ts` (~44 lines)

`checkTeamMemSecrets()` — pre-upload guard with user notification.

### 11.5 `types.ts` (~155 lines)

Zod schemas for API payloads and result types.

---

## Cross-Cutting Patterns

| Pattern | Used by |
|---|---|
| `runForkedAgent()` + cache sharing | SessionMemory, extractMemories, autoDream, AgentSummary, compact, PromptSuggestion |
| Closure-scoped init (`initX()` in beforeEach) | extractMemories, autoDream |
| Post-sampling hooks | SessionMemory, MagicDocs, autoDream |
| Stop hooks | extractMemories |
| Fail-open API fetch | policyLimits, remoteManagedSettings |
| OAuth + first-party API gate | settingsSync, teamMemorySync, policyLimits, remoteManagedSettings |
| GrowthBook cached reads | Most feature gates (`getFeatureValue_CACHED_MAY_BE_STALE`) |
