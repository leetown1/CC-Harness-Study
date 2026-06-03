# Services Layer Analysis — File 1: API Communication Services

> **Scope**: All files in `services/api/` (20 files) plus the 16 service root files (`services/*.ts`)
> **Purpose**: Handles all Anthropic API interaction, authentication, error handling, request lifecycle, rate limiting, voice/audio, sleep prevention, notifications, and internal tooling.

---

## 1. Core API Communication

### 1.1 `services/api/claude.ts` (3212 lines)

**The central API gateway** — orchestrates every Claude API call in the system. Contains the main `queryModel()` generator function plus a dozen supporting utilities.

#### Architecture Overview

The file is structured around a single async generator function `queryModel()` (lines 1017–2892) that builds and sends API requests, handling the full lifecycle:

```
verifyApiKey() ─────────────────────────────► One-shot auth verification
getExtraBodyParams() ──────────────────────► Extra JSON body from env + anti-distillation
getAPIMetadata() ─────────────────────────► Device/user/session metadata
getPromptCachingEnabled() ────────────────► Per-model caching toggle
getCacheControl() ────────────────────────► Cache control with TTL/scope
queryModelWithStreaming() / queryModelWithoutStreaming() ──► Public API surface
  └── queryModel() (internal async generator) ───────────► The main pipeline
       ├── GrowthBook off-switch check
       ├── Model resolution (Bedrock→inference profile→backing model)
       ├── Agentic query detection
       ├── Beta header assembly (merged betas + advisor + tool search + cached MC)
       ├── Advisor model configuration
       ├── Tool search / deferred tool detection
       ├── Tool schema building with defer_loading support
       ├── Message normalization pipeline
       ├── System prompt assembly with fingerprint
       ├── Cache break detection (PROMPT_CACHE_BREAK_DETECTION feature)
       ├── Streaming request dispatch
       │    ├── SSE stream iteration
       │    ├── First Token Date (TTFT) tracking
       │    └── Cache read/creation token tracking
       └── Non-streaming fallback (on stream errors)
```

#### Key Functions

| Function | Lines | Purpose |
|---|---|---|
| `queryModel()` | 1017-2892 | Core async generator: builds request, streams response, handles errors/fallback |
| `queryModelWithStreaming()` | 752-780 | Public streaming API wrapped with VCR |
| `queryModelWithoutStreaming()` | 709-750 | Public non-streaming API; iterates through streaming generator, extracts final message |
| `verifyApiKey()` | 530-586 | Validates API key using a minimal Haiku call with retry |
| `getExtraBodyParams()` | 272-331 | Assembles extra body params from env var + anti-distillation fake_tools opt-in |
| `getPromptCachingEnabled()` | 333-356 | Checks env vars for model-specific caching disable |
| `getCacheControl()` | 358-374 | Builds cache_control object with ephemeral type, optional 1h TTL, optional global scope |
| `getAPIMetadata()` | 503-528 | Builds user_id JSON with device_id, account_uuid, session_id |
| `userMessageToMessageParam()` | 588-631 | Converts UserMessage to API MessageParam with optional cache_control |
| `assistantMessageToMessageParam()` | 633-674 | Converts AssistantMessage, skipping cache_control on thinking/connector blocks |
| `configureEffortParams()` | 440-466 | Sets up effort budget for supported models |
| `configureTaskBudgetParams()` | 479-501 | Configures output_config.task_budget (beta: task-budgets-2026-03-13) |
| `stripExcessMediaItems()` | 956-1015 | Caps images+documents per request at API_MAX_MEDIA_PER_REQUEST |
| `executeNonStreamingRequest()` | 818-917 | Helper generator for non-streaming fallback with retry |

#### Streaming Architecture

The streaming path (line 1512+) operates as follows:

1. **SSE Stream Iteration**: Uses `anthropic.beta.messages.create({ stream: true }).withResponse()` — the fetch is dispatched and the SSE body is consumed from the response
2. **Event Processing**: Each SSE event is processed through a switch on `event.type`:
   - `message_start` → captures model, usage
   - `content_block_start/delta/stop` → text, thinking, tool_use blocks
   - `message_delta` → stop_reason, final usage delta
   - `message_stop` → finalizes the assistant message
3. **First Token Tracking**: Records TTFT (Time to First Token) via internal timing/profiling (no `tengu_first_token_date` event)
4. **Cache Tracking**: Monitors `cache_read_input_tokens` and `cache_creation_input_tokens` from usage deltas
5. **Non-Streaming Fallback**: If the stream errors with a retryable error, falls back to `executeNonStreamingRequest()`

#### Beta Header Management

Uses "sticky-on" latches for session stability:
- `AFK_MODE_BETA_HEADER` — locked on first auto-mode activation
- `FAST_MODE_BETA_HEADER` — locked on first fast-mode request
- `CACHE_EDITING_BETA_HEADER` — locked on first cached microcompact
All latches are cleared on `/clear` and `/compact`.

#### Off-Switch Pattern (line 1031-1049)

For non-subscriber Opus users, checks a GrowthBook dynamic config (`tengu-off-switch`) before sending the request. If activated, yields a friendly error suggesting `/model` to Sonnet, avoiding API calls during capacity crises.

---

### 1.2 `services/api/client.ts` (389 lines)

**Multi-provider Anthropic API client factory.**

#### Architecture

`getAnthropicClient()` is the single entry point that returns a configured `Anthropic` SDK instance based on environment variables:

```
getAnthropicClient()
├── CLAUDE_CODE_USE_BEDROCK → AnthropicBedrock
│   ├── AWS credential refresh
│   ├── Bearer token support
│   └── Region override for small/fast model
├── CLAUDE_CODE_USE_FOUNDRY → AnthropicFoundry
│   ├── DefaultAzureCredential for Azure AD
│   └── API key fallback
├── CLAUDE_CODE_USE_VERTEX → AnthropicVertex
│   ├── GoogleAuth with scoped credentials
│   ├── GCP credential refresh
│   └── Region resolution per model
└── Direct API → Anthropic
    ├── OAuth token (subscriber) or API key (3P)
    ├── Staging OAuth base URL override
    └── Custom headers from ANTHROPIC_CUSTOM_HEADERS env
```

#### Custom Headers

- `x-app: 'cli'` — identifies the client application
- `User-Agent` — built from `getUserAgent()`
- `X-Claude-Code-Session-Id` — session correlation
- `x-claude-remote-container-id` — CCR container tracking
- `x-client-request-id` — generated UUID per request for server log correlation
- `x-anthropic-additional-protection` — opt-in protection header

#### Client Request ID Injection

The `buildFetch()` function (line 358-389) wraps the native `fetch` to inject a `x-client-request-id` UUID header on first-party API calls. This survives timeouts (no server response → no server request-id) enabling server-side log lookup.

---

### 1.3 `services/api/withRetry.ts` (822 lines)

**Generic retry with exponential backoff for all API calls.**

#### Constants

| Constant | Value | Purpose |
|---|---|---|
| `DEFAULT_MAX_RETRIES` | 10 | Default retry attempts |
| `FLOOR_OUTPUT_TOKENS` | 3000 | Minimum output tokens on context overflow retry |
| `MAX_529_RETRIES` | 3 | Maximum consecutive 529s before fallback |
| `BASE_DELAY_MS` | 500 | Base delay for exponential backoff |
| `PERSISTENT_MAX_BACKOFF_MS` | 300000 | 5-min cap for unattended retry |
| `PERSISTENT_RESET_CAP_MS` | 21600000 | 6-hour cap for unattended retry |
| `HEARTBEAT_INTERVAL_MS` | 30000 | Keep-alive yield interval for persistent mode |

#### Retry Decision Logic (`shouldRetry()`)

1. **Mock rate limits**: Never retry (from `/mock-limits` command)
2. **Persistent unattended mode**: 429/529 always retried
3. **CCR mode**: 401/403 considered transient (JWT auth)
4. **Overloaded errors**: Retry if message contains `"type":"overloaded_error"`
5. **Max tokens overflow**: Retry with adjusted max_tokens
6. **`x-should-retry` header**: Obey server directive (except ants on 5xx)
7. **Status codes**: 408, 409, 429 (non-subscriber), 401, 5xx → retry

#### Persistent Unattended Mode (line 96-104)

Gated by `feature('UNATTENDED_RETRY')` and `CLAUDE_CODE_UNATTENDED_RETRY` env var. Retries 429/529 indefinitely, yielding `SystemAPIErrorMessage` keep-alives every 30s so the host doesn't mark the session idle.

#### Fast Mode Fallback (line 267-314)

On 429/529 with fast mode active:
1. **Overage disabled**: Permanently disable fast mode with user message
2. **Short retry-after (<20s)**: Wait and retry with fast mode (preserves cache)
3. **Long retry-after**: Enter cooldown, switch to standard speed
4. **API rejection**: If API returns "Fast mode is not enabled", permanently disable

#### Context Overflow Adjustment (line 388-427)

Parses the `"input length and max_tokens exceed context limit: X + Y > Z"` error pattern, computes available context, adjusts max_tokens for the retry.

#### Custom Error Types

- `CannotRetryError` — wraps the original error when retries are exhausted
- `FallbackTriggeredError` — signals model fallback (e.g., Opus→Sonnet on repeated 529)

---

### 1.4 `services/api/errors.ts` (1207 lines)

**Error classification, user-facing error messages, and API error handling.**

#### Error Message Constants (lines 54-199)

| Constant | Message |
|---|---|
| `API_ERROR_MESSAGE_PREFIX` | `"API Error"` |
| `PROMPT_TOO_LONG_ERROR_MESSAGE` | `"Prompt is too long"` |
| `CREDIT_BALANCE_TOO_LOW_ERROR_MESSAGE` | `"Credit balance is too low"` |
| `INVALID_API_KEY_ERROR_MESSAGE` | `"Not logged in · Please run /login"` |
| `ORG_DISABLED_ERROR_MESSAGE_ENV_KEY` | `"Your ANTHROPIC_API_KEY belongs to a disabled organization..."` |
| `TOKEN_REVOKED_ERROR_MESSAGE` | `"OAuth token revoked · Please run /login"` |
| `CCR_AUTH_ERROR_MESSAGE` | `"Authentication error · This may be a temporary network issue..."` |
| `REPEATED_529_ERROR_MESSAGE` | `"Repeated 529 Overloaded errors"` |
| `CUSTOM_OFF_SWITCH_MESSAGE` | `"Opus is experiencing high load, please use /model..."` |

#### `getAssistantMessageFromError()` (line 425-934)

**The master error-to-user-message mapper.** Handles every known error type in precedence order:

1. Timeout errors → `"Request timed out"`
2. Image size/resize errors → `"Image was too large..."`
3. Off-switch → Opus capacity message
4. 429 rate limits:
   - New unified headers → `getRateLimitErrorMessage()`
   - Long context entitlement → `/extra-usage` suggestion
   - Other 429s → server message extraction
5. Prompt too long → `"Prompt is too long"` with errorDetails
6. PDF page limit / password / invalid errors
7. Image size (API 400)
8. Many-image dimension errors (2000px limit)
9. AFK-mode plan restriction
10. 413 request too large
11. Tool_use/tool_result mismatch (400) → `/rewind` suggestion
12. Duplicate tool_use IDs (400)
13. Invalid model name (subscriber)
14. Invalid model name (ant — org gating)
15. Credit balance low
16. Org disabled (env key override)
17. Invalid API key (401/403)
18. OAuth token revoked (403)
19. OAuth org not allowed (401/403)
20. Generic 401/403 → `/login` suggestion
21. Bedrock model access errors
22. 404 model not found
23. Connection errors → `formatAPIError()`
24. Generic errors

#### `classifyAPIError()` (line 965-1161)

Returns standardized error type string for analytics/Datadog tagging:
`aborted`, `api_timeout`, `repeated_529`, `capacity_off_switch`, `rate_limit`, `server_overload`, `prompt_too_long`, `pdf_too_large`, `pdf_password_protected`, `image_too_large`, `tool_use_mismatch`, `unexpected_tool_result`, `duplicate_tool_use_id`, `invalid_model`, `credit_balance_low`, `invalid_api_key`, `token_revoked`, `oauth_org_not_allowed`, `auth_error`, `bedrock_model_access`, `ssl_cert_error`, `connection_error`, `server_error`, `client_error`, `unknown`

#### Utility Functions

- `isPromptTooLongMessage()` — checks if assistant message contains PTL error
- `parsePromptTooLongTokenCounts()` — extracts actual/limit token counts from error
- `getPromptTooLongTokenGap()` — returns tokens-over-limit for reactive compact
- `isMediaSizeError()` / `isMediaSizeErrorMessage()` — media rejection detection
- `isValidAPIMessage()` — type guard for `BetaMessage`
- `getErrorMessageIfRefusal()` — refusal stop_reason handler with /model suggestion

---

### 1.5 `services/api/promptCacheBreakDetection.ts` (727 lines)

**Two-phase cache break detection system** — identifies and explains server-side prompt cache invalidations.

#### Architecture

**Phase 1: `recordPromptState()` (pre-call)**
- Captures everything affecting the server-side cache key:
  - System prompt hash (stripped of cache_control)
  - Full cache_control hash (catches scope/TTL flips)
  - Tool schemas hash + per-tool hashes
  - Beta headers (sorted)
  - Model, fastMode, globalCacheStrategy
  - AutoMode, overage, cachedMC state
  - Effort value, extra body params hash
  - System character count, tool names
- Computed per tracked source (querySource+agentId key)
- Detects what changed vs. previous state → stores as `PendingChanges`
- Capped at `MAX_TRACKED_SOURCES = 10` (prevents unbounded growth from subagents)
- Excludes Haiku models from tracking

**Phase 2: `checkResponseForCacheBreak()` (post-call)**
- Compares cache_read_input_tokens vs. previous call
- Break detected when: `cacheReadTokens < prevCacheRead * 0.95` AND `tokenDrop >= 2000`
- Builds human-readable reason from pending changes (e.g., "model changed", "+3/-1 tools")
- Falls back to TTL expiry detection (5min/1h thresholds)
- Writes `.diff` files for ant debugging in `claude-tmp/`
- Fires `tengu_prompt_cache_break` analytics event with full diagnostic data

#### Tracking Keys

```typescript
TRACKED_SOURCE_PREFIXES = ['repl_main_thread', 'sdk', 'agent:custom', 'agent:default', 'agent:builtin']
```
- `compact` maps to `repl_main_thread` (shared cache)
- Subagents use unique agentId as key
- Untracked sources (speculation, session_memory, etc.) are excluded

#### Ancillary Functions

- `notifyCacheDeletion()` — called when cached microcompact sends deletions (expected cache drop, not a break)
- `notifyCompaction()` — resets baseline after compaction
- `cleanupAgentTracking()` — removes subagent state on teardown
- `resetPromptCacheBreakDetection()` — clears all state (on /clear)

---

### 1.6 Other API Service Files

#### `services/api/bootstrap.ts` (141 lines)
**Session bootstrap API.** Fetches client_data and additional model options from the server.

- Uses OAuth or API key auth
- `fetchBootstrapData()` → calls `fetchBootstrapAPI()` → validates with Zod schema → persists to disk cache
- Avoids redundant writes via `isEqual()` comparison
- Gates: only first-party provider, requires OAuth profile scope or API key
- 5-second timeout

#### `services/api/filesApi.ts` (748 lines)
**Anthropic Files API client** for upload/download/list operations.

- **Download**: `downloadFile()`, `downloadAndSaveFile()`, `downloadSessionFiles()` — parallel with concurrency limit (default 5)
- **Upload**: `uploadFile()` (multipart form-data, 500MB max), `uploadSessionFiles()` — with retry
- **List**: `listFilesCreatedAfter()` — cursor-based pagination, for teleport file reconstruction
- **Parsing**: `parseFileSpecs()` — parses `<file_id>:<relative_path>` CLI arg format
- Uses beta headers: `files-api-2025-04-14,oauth-2025-04-20`
- Retry with exponential backoff (3 attempts, 500ms base)
- Path traversal protection in `buildDownloadPath()`

#### `services/api/grove.ts` (357 lines)
**Grove privacy/terms dialog proxy API.**

- `getGroveSettings()` — memoized fetch of account settings (grove_enabled, notice_viewed_at)
- `getGroveNoticeConfig()` — memoized Statsig config (domain_excluded, grace period, reminder frequency)
- `markGroveNoticeViewed()` — posts viewed timestamp, invalidates cache
- `updateGroveSettings()` — PATCH to toggle grove_enabled
- `isQualifiedForGrove()` — cache-first eligibility check (never blocks on network)
- `calculateShouldShowGrove()` — decision logic combining settings + config
- `checkGroveForNonInteractive()` — CLI print mode: shows terms notice or blocks if grace period ended
- 24-hour disk cache for Grove config

#### `services/api/logging.ts` (788 lines)
**Request/response logging and analytics emission.**

- `logAPIQuery()` — fires `tengu_api_query` event before API call (model, messages, betas, source, thinking, effort)
- `logAPISuccessAndDuration()` — fires `tengu_api_success` after successful call (full usage breakdown, TTFT, gateway detection, content analysis, cost)
- `logAPIError()` — fires `tengu_api_error` on failure (error type classification, gateway, teleport tracking)
- **Gateway Detection**: Identifies LiteLLM, Helicone, Portkey, Cloudflare AI Gateway, Kong, Braintrust from response headers; Databricks from host suffix
- **Content Analysis**: Tracks text/thinking/tool_use content lengths per response
- **OTel Integration**: Emits `api_request` and `api_error` events for OTLP
- **Teleport Support**: Tracks first message in teleported sessions

#### `services/api/firstTokenDate.ts` (60 lines)
**First Claude Code token date tracking.** Fetches organization's first_token_date via OAuth, caches in GlobalConfig. Important for showing "You've been using Claude Code since..." messaging.

#### `services/api/metricsOptOut.ts` (159 lines)
**Organization-level metrics opt-out check.** Two-tier caching:
- Disk cache (24h TTL) — survives restarts
- In-memory cache (1h TTL) via `memoizeWithTTLAsync`
- Incident kill switch via `isEssentialTrafficOnly()`
- Service key OAuth sessions skip (no profile scope)

#### `services/api/overageCreditGrant.ts` (137 lines)
**Overage credit grant management.** Fetches org's overage credit grant eligibility and details:
- `getCachedOverageCreditGrant()` — 1h TTL disk cache
- `refreshOverageCreditGrantCache()` — fetch+persist with change detection
- `invalidateOverageCreditGrantCache()` — drops cache entry
- `formatGrantAmount()` — formats amount_minor_units to currency string

#### `services/api/usage.ts` (63 lines)
**Usage/utilization tracking API.** Fetches rate limit utilization from `/api/oauth/usage`:
- Supports five_hour, seven_day, seven_day_opus, seven_day_sonnet, extra_usage
- 5-second timeout, OAuth-only (requires profile scope)
- Skip on expired OAuth token

#### `services/api/sessionIngress.ts` (514 lines)
**Remote session log persistence.** Appends and retrieves transcript entries:

- **Append**: `appendSessionLog()` — sequential per-session, optimistic concurrency with Last-UUID header, exponential backoff (10 retries, 500ms base)
- **Retrieve**: `getSessionLogs()` (JWT), `getSessionLogsViaOAuth()` (OAuth), `getTeleportEvents()` (CCR v2)
- **409 Conflict Handling**: Adopts server's lastUUID from response header or re-fetches session to discover chain head
- **Teleport Events**: Paginated cursor-based fetch from CCR v2 Sessions API (1000/page, max 100 pages)
- `clearSession()` / `clearAllSessions()` for cleanup

#### `services/api/errorUtils.ts` (260 lines)
**Connection error detail extraction and formatting.**

- `extractConnectionErrorDetails()` — walks error cause chain (max depth 5) to find root error code; classifies SSL errors via 18 known OpenSSL/Node.js codes
- `formatAPIError()` — produces user-friendly messages per error code:
  - SSL certificate verification failures → proxy/corporate SSL instructions
  - ETIMEDOUT → internet connection check
  - HTML content detection (CloudFlare error pages) → extracts `<title>` text
- `getSSLErrorHint()` — actionable hint for TLS-intercepting proxies (Zscaler etc.)
- `sanitizeAPIError()` — strips HTML from error messages
- Handles post-JSONL deserialized errors with nested `.error.error.message` structure

#### `services/api/referral.ts` (281 lines)
**Referral/pass eligibility system (Claude Code guest passes).**
- `fetchReferralEligibility()` — checks if org is eligible for passes campaign
- `fetchReferralRedemptions()` — gets redemption history
- `checkCachedPassesEligibility()` — returns cached state with needsRefresh flag
- `fetchAndStorePassesEligibility()` — deduplicates concurrent fetches via in-flight promise
- `getCachedOrFetchPassesEligibility()` — main entry: stale-while-revalidate pattern with 24h disk cache
- Currency formatting for referrer rewards (8 currencies)
- Gates: Max subscribers only, OAuth authenticated

#### `services/api/ultrareviewQuota.ts` (38 lines)
**UltraReview quota peek.** Simple OAuth API call returning reviews_used/limit/remaining/is_overage. Subscribers only.

#### `services/api/adminRequests.ts` (119 lines)
**Admin request API (limit increase, seat upgrade).** For Team/Enterprise users:
- `createAdminRequest()` — creates request with duplicate detection
- `getMyAdminRequests()` — fetches user's requests by type + status filter
- `checkAdminRequestEligibility()` — checks if request type is allowed for org

#### `services/api/dumpPrompts.ts` (226 lines)
**Ant-only debug prompt dumper.** Writes API requests/responses to JSONL files for `/issue` debugging:
- `createDumpPromptsFetch()` — returns a fetch wrapper that intercepts POST requests and responses
- Dumps init data (system, tools, metadata) on first request, system_update on change
- Tracks message counts to only dump new user messages
- Uses SHA-256 fingerprint for change detection (avoid expensive stringify)
- Responses dumped with SSE stream parsing support
- All operations use `setImmediate` / fire-and-forget to avoid blocking API calls

#### `services/api/emptyUsage.ts` (22 lines)
**Zero-initialized usage object.** Extracted from logging.ts to avoid circular deps. Contains all usage fields initialized to zero.

---

## 2. Service Root Files

### 2.1 Token Counting

#### `services/tokenEstimation.ts` (495 lines)

**Dual-path token counting: API-based (authoritative) + rough estimation (fast fallback).**

| Function | Method | Use Case |
|---|---|---|
| `countTokensWithAPI()` | Anthropic countTokens endpoint | Single string token counting |
| `countMessagesTokensWithAPI()` | Anthropic countTokens endpoint | Full message array + tools |
| `countTokensViaHaikuFallback()` | Haiku messages.create (1 max_tokens) | Bedrock fallback (no countTokens), thinking blocks |
| `roughTokenCountEstimation()` | `Math.round(chars / 4)` | Fast estimate for content strings |
| `roughTokenCountEstimationForMessages()` | Aggregated char/4 | Full conversation estimate |
| `roughTokenCountEstimationForContent()` | Per-block estimation | Text=char/4, image=2000, tool_use=name+input |
| `bytesPerTokenForFileType()` | Type-aware ratio | JSON: 2 chars/token, default: 4 |

**Haiku fallback logic (line 251-325):**
- Defaults to Haiku (fastest, cheapest)
- Falls back to Sonnet when: Vertex global region (Haiku unavailable), Bedrock with thinking, Vertex with thinking
- Strips tool_search fields (caller, tool_reference) before counting
- Returns sum of input_tokens + cache_creation + cache_read

**Bedrock counting (line 437-495):**
- Uses AWS SDK `CountTokensCommand` (dynamically imported, ~279KB)
- Resolves ARN/inference profiles to foundation model IDs
- Converts to Bedrock request format

### 2.2 Voice Services

#### `services/voiceStreamSTT.ts` (544 lines)

**WebSocket speech-to-text client** for push-to-talk. Ant-only (gated by `feature('VOICE_MODE')`).

**Protocol:**
- JSON control messages: `KeepAlive` (every 8s), `CloseStream`
- Binary audio frames: 16kHz linear16, mono
- Server responses: `TranscriptText` (incremental+final), `TranscriptEndpoint`, `TranscriptError`

**Connection lifecycle:**
1. `connectVoiceStream()` — OAuth token refresh, WebSocket connection with TLS/mTLS support
2. `connection.send(audioChunk)` — sends raw audio buffers
3. `connection.finalize()` — sends CloseStream, waits for TranscriptEndpoint or timeout
4. `connection.close()` — tears down WebSocket

**Features:**
- Nova 3 STT support via GrowthBook gate `tengu_cobalt_frost`
- Proxy support (Node.js agent or Bun tls config)
- Domain-specific keyterms for boosting
- Language parameter support
- Availability check: OAuth authenticated users only
- Timeouts: safety=5s, noData=1.5s (exported for test overrides)

#### `services/voiceKeyterms.ts` (106 lines)

**Domain-specific keyterms for STT boosting.** Returns arrays of technical terms organized by context:
- Programming languages (TypeScript, Python, Rust, Go, etc.)
- Frameworks (React, Next.js, Express, Django, etc.)
- Claude Code commands (/compact, /model, /clear, etc.)
- Infrastructure terms (Docker, Kubernetes, AWS, etc.)

#### `services/voice.ts` (525 lines)

**Audio recording with native system capture.** Platform-specific capture via:
- **macOS**: Uses `rec` (SoX) or `ffmpeg` for audio capture from default input device
- **Linux**: Uses `arecord` (ALSA) for audio capture
- **Windows**: Uses `ffmpeg` with dshow

Provides `startRecording()` / `stopRecording()` with WAV output at 16kHz mono 16-bit linear PCM.

### 2.3 Testing / VCR

#### `services/vcr.ts` (406 lines)

**Test VCR (Video Cassette Recorder) for deterministic API replay.**

**Purpose:** Records real API responses to disk as JSON fixtures, then replays them in tests instead of making actual API calls.

**Activation:** `NODE_ENV === 'test'` or `FORCE_VCR=1` (ant only)

**Key Functions:**
- `withVCR(messages, f)` — for non-streaming calls: hashes normalized messages, caches response array
- `withStreamingVCR(messages, asyncGen)` — for streaming calls: caches all yielded events
- `withTokenCountVCR(messages, tools, f)` — for token counting calls
- `withFixture(input, name, f)` — generic fixture helper for any data type

**Fixture format:** JSON files in `fixtures/` directory, named by SHA1 hash of dehydrated input. Includes both input and output for debugging. In CI, missing fixtures throw with instructions to re-record.

**Security:** Sensitive data (file contents, tool results) is dehydrated/hydrated to/from hash references to avoid committing real data.

### 2.4 Rate Limiting

#### `services/claudeAiLimits.ts` (515 lines)

**Claude.ai subscription rate limit management.**

**Core State:**
- `currentLimits: ClaudeAILimits` — global limits state (status, resetsAt, rateLimitType, utilization, overageStatus, etc.)
- `rawUtilization: RawUtilization` — per-window utilization from response headers (exposed to statusline scripts)
- `statusListeners: Set<StatusChangeListener>` — reactive listeners for UI updates

**Header Processing:**
- `extractQuotaStatusFromHeaders()` — parses API response headers for rate limit information
- `extractQuotaStatusFromError()` — parses 429 error headers for quota details
- `extractRawUtilization()` — reads `anthropic-ratelimit-unified-{5h,7d}-utilization/reset` headers

**Early Warning System (lines 38-77):**
- Two tiers: 5-hour (90% at 72% time elapsed) and 7-day (75%/50%/25% thresholds)
- Surpasses regular warnings by detecting over-consumption BEFORE hitting the limit
- Falls back to client-side `computeTimeProgress()` calculation when server doesn't send surpassed-threshold header

**Change Detection:**
- `emitStatusChange()` — updates currentLimits, fires all listeners, logs event
- `hasLimitsChanged()` — deep-equality comparison to avoid redundant updates

#### `services/claudeAiLimitsHook.ts` (23 lines)

**React hook wrapper.** `useClaudeAiLimits()` — subscribes to statusListeners, returns current limits state. Thin adapter for React components.

#### `services/rateLimitMessages.ts` (344 lines)

**Rate limit message generation.** Produces localized, context-aware messages:
- `getRateLimitErrorMessage()` — error messages per rate limit type + overage status
- `getRateLimitWarning()` — warning messages (early warning, near-limit)
- `getUsingOverageText()` — text for overage pricing increase notification
- Message variants: interactive (CLI) vs. non-interactive (SDK/headless)
- Formatting: UTC-formatted reset times, time-until-reset calculations

#### `services/rateLimitMocking.ts` (144 lines)

**Mock rate limit infrastructure.** Intercepts API rate limit headers:
- `processRateLimitHeaders()` — applies mock overrides to real headers
- `checkMockRateLimitError()` — returns a mock 429 error for testing
- `isMockRateLimitError()` — identifies mock errors
- `shouldProcessRateLimits()` — gate (ant + `/mock-limits` active)
- Mock configurations set via the `/mock-limits` command

#### `services/mockRateLimits.ts` (882 lines)

**Comprehensive mock rate limit system with 19 scenarios.**

Supports full simulation of rate limit states for testing:
- **Rate Limit Types**: five_hour, seven_day, seven_day_opus, seven_day_sonnet, overage
- **Statuses**: allowed, allowed_warning, rejected
- **Overage States**: allowed, allowed_warning, rejected, disabled with 13 reasons
- **Scenarios**: normal, warning, limit_reached, overage_allowed, overage_warning, overage_rejected, unified_fallback, overage_disabled_reasons, fast_mode, early_warning, seat_upgrade, limit_increase, combined, clear, default_haiku, etc.
- Parses `/mock-limits` command arguments for interactive testing
- Persists mock config to GlobalConfig

### 2.5 System Services

#### `services/preventSleep.ts` (165 lines)

**macOS sleep prevention via caffeinate.**

- Uses `caffeinate -i -t 300` (5-min idle sleep assertion, self-healing timeout)
- Reference-counted: `startPreventSleep()` increments, `stopPreventSleep()` decrements
- Auto-restarts every 4 minutes (buffer before 5-min expiry)
- `unref()` on both process and interval to not keep Node alive
- macOS-only (silently no-ops on other platforms)
- Register cleanup on process exit via `registerCleanup()`

#### `services/notifier.ts` (156 lines)

**Terminal notification system.** Routes completion notifications to:
- **iTerm2**: OSC escape sequence (`notifyITerm2`)
- **Kitty**: OSC escape sequence (`notifyKitty`) with random ID
- **Ghostty**: OSC escape sequence (`notifyGhostty`)
- **Terminal Bell**: ASCII bell character
- **Auto mode**: Detects terminal type and chooses best method
  - Apple Terminal: Checks if bell is disabled in current profile (parses plist)
  - iTerm.app → iTerm2 notification
  - kitty → Kitty notification
  - ghostty → Ghostty notification
- Runs notification hooks via `executeNotificationHooks()`
- Logs `tengu_notification_method_used` analytics

#### `services/awaySummary.ts` (74 lines)

**Away-time conversation recap.** When user returns after inactivity:
- Identifies messages exchanged during away period
- Generates a summary of what happened while away
- Uses compact/summarization prompts to recap

#### `services/mcpServerApproval.tsx` (41 lines)

**MCP server approval dialog component.** React component showing:
- Server name, description, required scopes
- Approve/deny buttons
- Used when MCP servers request elevated permissions

#### `services/internalLogging.ts` (90 lines)

**Ant-only internal logging.** Sends structured diagnostic logs to internal endpoints:
- Gated by `USER_TYPE === 'ant'`
- Batches log entries for efficiency
- Uses internal API endpoints separate from public telemetry

---

## 3. Cross-Cutting Concerns

### Query Loop Integration

The main conversation loop in `query.ts` calls the API via dependency injection — not by importing `queryModel()` directly:

```
QueryEngine.submitMessage()
  → query() → queryLoop()
       → deps.callModel()  (= queryModelWithStreaming in production)
            → withStreamingVCR()
                 → queryModel()  [services/api/claude.ts]
```

**Two different “budget” concepts:**

| Mechanism | Layer | Purpose |
|-----------|-------|---------|
| **`task_budget`** (`configureTaskBudgetParams()`) | API `output_config` (beta `task-budgets-2026-03-13`) | Server-side token budget for an agentic turn; `remaining` decremented across compactions in `queryLoop` |
| **`TOKEN_BUDGET`** feature (`checkTokenBudget()` in `query/tokenBudget.ts`) | Client-side nudge after stop hooks | User prompt token target (e.g. `+500k`); injects meta user message to continue |

Compaction side effects on the API layer: proactive/reactive compact calls `notifyCompaction()` in `promptCacheBreakDetection.ts` to reset cache-break baselines. Cached microcompact calls `notifyCacheDeletion()` instead.

Stop hooks and token-budget checks run only when the model **did not** emit `tool_use` blocks (`needsFollowUp === false`). Tool dispatch (`runTools` / `StreamingToolExecutor`) runs on the `needsFollowUp === true` branch and skips stop hooks until the next natural completion.

### API Request Lifecycle

Every API call goes through this pipeline:

```
[Caller] → queryModelWithStreaming() / queryModelWithoutStreaming()
         → withStreamingVCR() / withVCR()          [Test fixture interceptor]
         → queryModel()                             [Main pipeline]
            ├── recordPromptState()                [Cache break detection: Phase 1]
            ├── logAPIQuery()                       [Pre-request analytics]
            ├── startLLMRequestSpan()               [Beta tracing span]
            ├── anthropic.beta.messages.create({ stream: true }).withResponse()    [Actual API call]
            │   ├── SSE event processing
            │   ├── TTFT tracking
            │   └── Usage delta capture
            ├── logAPISuccessAndDuration()          [Post-success analytics]
            │   ├── endLLMRequestSpan()
            │   └── OTel events
            ├── checkResponseForCacheBreak()         [Cache break detection: Phase 2]
            └── [On error] logAPIError()             [Error analytics]
```

### Error Handling Chain

```
API throws → withRetry() catches
           ├── Classifies error (shouldRetry)
           ├── Adjusts context (max_tokens overflow)
           ├── Handles auth (401/403 → refresh tokens)
           ├── Handles fast mode (429/529 → cooldown/fallback)
           ├── Exponential backoff + yield SystemAPIErrorMessage
           └── Exhausted → CannotRetryError
              └── getAssistantMessageFromError()
                  └── User-facing error message
```

### Authentication Flow

```
getAnthropicClient()
├── 1st Party w/ OAuth
│   ├── checkAndRefreshOAuthTokenIfNeeded()
│   └── Bearer token → Anthropic(authToken)
├── 1st Party w/ API Key
│   └── x-api-key → Anthropic(apiKey)
├── Bedrock → AnthropicBedrock
│   ├── AWS credential refresh
│   └── Skip auth option
├── Foundry → AnthropicFoundry
│   └── Azure AD or API key
└── Vertex → AnthropicVertex
    └── GoogleAuth
```
