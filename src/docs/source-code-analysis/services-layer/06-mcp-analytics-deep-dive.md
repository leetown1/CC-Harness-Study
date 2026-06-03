# Services Layer Analysis — File 6: MCP Remaining Files + Analytics Deep Dive

> **Scope**: All remaining mostly-undocumented files in `services/mcp/` (15 files) + all `services/analytics/` (9 files)
> **Purpose**: Complete coverage of the MCP and analytics subsystems left shallow or absent in previous analysis

---

## Part I: MCP Remaining Files Deep Dive

### Coverage Summary

| File | Lines | Previous Status | Coverage |
|------|-------|----------------|----------|
| `xaa.ts` | 511 | Merely mentioned | Full below |
| `xaaIdpLogin.ts` | 487 | Merely mentioned | Full below |
| `useManageMCPConnections.ts` | 1141 | Merely mentioned | Full below |
| `channelNotification.ts` | 316 | Merely mentioned | Full below |
| `channelPermissions.ts` | 240 | Merely mentioned | Full below |
| `channelAllowlist.ts` | 76 | Merely mentioned | Full below |
| `vscodeSdkMcp.ts` | 112 | Merely mentioned | Full below |
| `SdkControlTransport.ts` | 136 | Brief §1.6 | Full below |
| `claudeai.ts` | 164 | Brief §1.6 | Full below |
| `headersHelper.ts` | 138 | Brief §1.6 | Full below |
| `normalization.ts` | 23 | Brief §1.6 | Full below |
| `mcpStringUtils.ts` | 106 | Brief §1.6 | Full below |
| `officialRegistry.ts` | 72 | Brief §1.6 | Full below |
| `envExpansion.ts` | 38 | Brief §1.6 | Full below |
| `InProcessTransport.ts` | 63 | Brief §1.6 | Full below |

---

### 1.1 `services/mcp/xaa.ts` (511 lines)

**Cross-App Access (XAA) / SEP-990 — browserless MCP auth via IdP token exchange.**

Implements a four-step token chain:
1. **RFC 9728 PRM discovery** — discover protected resource metadata from MCP server
2. **RFC 8414 AS discovery** — discover authorization server metadata
3. **RFC 8693 Token Exchange at IdP** — `id_token` → ID-JAG (Identity Assertion Authorization Grant)
4. **RFC 7523 JWT Bearer Grant at AS** — ID-JAG → `access_token`

#### Exports

| Export | Kind | Description |
|--------|------|-------------|
| `XaaTokenExchangeError` | class | Custom Error subclass carrying `shouldClearIdToken` flag for cache management |
| `discoverProtectedResource()` | async fn | RFC 9728 PRM discovery with resource-mismatch validation |
| `discoverAuthorizationServer()` | async fn | RFC 8414 AS metadata discovery with issuer-mismatch + HTTPS enforcement |
| `requestJwtAuthorizationGrant()` | async fn | RFC 8693 token exchange: `id_token` → ID-JAG via `urn:ietf:params:oauth:grant-type:token-exchange` |
| `exchangeJwtAuthGrant()` | async fn | RFC 7523 JWT Bearer: ID-JAG → `access_token` via `urn:ietf:params:oauth:grant-type:jwt-bearer` |
| `performCrossAppAccess()` | async fn | Layer-3 orchestrator composing the four Layer-2 ops |

#### Types

| Type | Description |
|------|-------------|
| `ProtectedResourceMetadata` | `{ resource: string, authorization_servers: string[] }` |
| `AuthorizationServerMetadata` | `{ issuer, token_endpoint, grant_types_supported?, token_endpoint_auth_methods_supported? }` |
| `JwtAuthGrantResult` | `{ jwtAuthGrant: string, expiresIn?, scope? }` |
| `XaaTokenResult` | `{ access_token, token_type, expires_in?, scope?, refresh_token? }` |
| `XaaResult` | `XaaTokenResult & { authorizationServerUrl: string }` |
| `XaaConfig` | Full orchestrator input: `{ clientId, clientSecret, idpClientId, idpClientSecret?, idpIdToken, idpTokenEndpoint }` |

#### Private Functions

| Function | Description |
|----------|-------------|
| `makeXaaFetch(abortSignal?)` | Creates fetch wrapper with 30s timeout + caller abort signal via `AbortSignal.any` |
| `normalizeUrl(url)` | RFC 3986 §6.2.2 syntax-based normalization (lowercase scheme+host, strip trailing slash) |
| `redactTokens(raw)` | Redacts known token-bearing JSON keys (`access_token`, `refresh_token`, `id_token`, `assertion`, `subject_token`, `client_secret`) for safe logging |

#### Zod Schemas

| Schema | Purpose |
|--------|---------|
| `TokenExchangeResponseSchema` | Validates RFC 8693 response: `access_token?`, `issued_token_type?`, `expires_in?` (coerced), `scope?` |
| `JwtBearerResponseSchema` | Validates RFC 7523 response: `access_token` (min 1), `token_type` (default Bearer), `expires_in?`, `scope?`, `refresh_token?` |

#### Layer-2 Discovery Details

**`discoverProtectedResource(serverUrl, opts?)`:**
- Calls SDK's `discoverOAuthProtectedResourceMetadata`
- Validates `resource` + `authorization_servers[0]` are present
- RFC 9728 §3.3 mix-up protection: verifies `normalizeUrl(prm.resource) === normalizeUrl(serverUrl)`
- Throws descriptive `XAA: PRM discovery failed: ...` errors

**`discoverAuthorizationServer(asUrl, opts?)`:**
- Calls SDK's `discoverAuthorizationServerMetadata`
- Validates `issuer` + `token_endpoint` are present
- RFC 8414 §3.3 issuer-mismatch validation
- Refuses non-HTTPS token endpoints

#### Layer-2 Exchange Details

**`requestJwtAuthorizationGrant(opts)`:**
- POSTs to IdP token endpoint with `grant_type=token-exchange`, `requested_token_type=id-jag`, `subject_token_type=id_token`
- Sends `client_secret` via `client_secret_post` if available
- On `!res.ok`: parses `shouldClearIdToken = res.status < 500` (4xx = bad token → clear; 5xx = IdP outage → preserve)
- Validates response has `access_token` and `issued_token_type === id-jag`
- Non-JSON responses (captive portal) → `shouldClearIdToken = false`

**`exchangeJwtAuthGrant(opts)`:**
- POSTs to AS token endpoint with `grant_type=jwt-bearer`
- Supports `client_secret_basic` (Base64 header, default) and `client_secret_post` (body params)
- Validates response shape via `JwtBearerResponseSchema`

#### Layer-3 Orchestrator: `performCrossAppAccess(serverUrl, config, serverName?, abortSignal?)`

Full flow:
```
1. discoverProtectedResource(serverUrl)          → PRM
2. For each AS in PRM.authorization_servers:
   a. discoverAuthorizationServer(asUrl)         → AS metadata
   b. Skip if AS advertises grant_types without jwt-bearer
   c. Pick authMethod from token_endpoint_auth_methods_supported
3. requestJwtAuthorizationGrant(idpTokenEndpoint) → ID-JAG
4. exchangeJwtAuthGrant(AS tokenEndpoint)         → access_token
5. Return { ...tokens, authorizationServerUrl }
```

#### Integration Points

- Used by `auth.ts:performMCPXaaAuth()` and `auth.ts:ClaudeAuthProvider.xaaRefresh()`
- Consumed by `auth.ts` for interactive and silent XAA token acquisition
- Imported by conformance test scripts (`try-xaa*.ts`)

---

### 1.2 `services/mcp/xaaIdpLogin.ts` (487 lines)

**XAA IdP Login — acquires an OIDC `id_token` from an enterprise IdP via authorization_code + PKCE.**

Provides the "one browser pop" for XAA: one IdP login → N silent MCP server auths. The `id_token` is cached in keychain and reused until expiry.

#### Exports

| Export | Kind | Description |
|--------|------|-------------|
| `isXaaEnabled()` | fn | Checks `CLAUDE_CODE_ENABLE_XAA` env var |
| `getXaaIdpSettings()` | fn | Reads `settings.xaaIdp` from user settings |
| `issuerKey(issuer)` | fn | Normalizes issuer URL for cache key (strip trailing slash, lowercase host) |
| `getCachedIdpIdToken(idpIssuer)` | fn | Reads cached id_token from secure storage, checks expiry buffer |
| `clearIdpIdToken(idpIssuer)` | fn | Removes cached id_token for issuer |
| `saveIdpIdTokenFromJwt(idpIssuer, idToken)` | fn | Saves externally-obtained id_token (conformance testing) |
| `saveIdpClientSecret(idpIssuer, clientSecret)` | fn | Persists IdP client secret to secure storage (separate from AS secrets) |
| `getIdpClientSecret(idpIssuer)` | fn | Reads IdP client secret from secure storage |
| `clearIdpClientSecret(idpIssuer)` | fn | Removes IdP client secret |
| `discoverOidc(idpIssuer)` | async fn | OIDC discovery via `{issuer}/.well-known/openid-configuration` |
| `acquireIdpIdToken(opts)` | async fn | Full OIDC authorization_code + PKCE flow, caches result |

#### Types

| Type | Description |
|------|-------------|
| `XaaIdpSettings` | `{ issuer: string, clientId: string, callbackPort?: number }` |
| `IdpLoginOptions` | `{ idpIssuer, idpClientId, idpClientSecret?, callbackPort?, onAuthorizationUrl?, skipBrowserOpen?, abortSignal? }` |

#### Private Functions

| Function | Description |
|----------|-------------|
| `saveIdpIdToken(idpIssuer, idToken, expiresAt)` | Writes to `mcpXaaIdp` storage slot |
| `jwtExp(jwt)` | Decodes JWT `exp` claim without signature verification (for cache TTL only) |
| `waitForCallback(port, expectedState, abortSignal, onListening)` | HTTP server on localhost waiting for `/callback` with state validation |

#### OIDC Discovery: `discoverOidc(idpIssuer)`

Properly handles path-aware IdPs (Azure AD, Okta custom auth servers, Keycloak realms):
- Appends `/.well-known/openid-configuration` as relative path (NOT absolute-path replacement)
- Uses `trailing-slash base + relative path` construction
- Validates HTTPS on `token_endpoint`
- Detects captive portal non-JSON responses

#### IdP Login: `acquireIdpIdToken(opts)`

Flow:
```
1. Check cache via getCachedIdpIdToken() → return if valid
2. discoverOidc(idpIssuer) → OIDC metadata
3. findAvailablePort() or use configured callbackPort
4. startAuthorization() → PKCE authorization URL (SDK call)
5. waitForCallback() → HTTP server on localhost
6. On listening: call onAuthorizationUrl(), optionally open browser
7. exchangeAuthorization() → tokens (SDK call)
8. Extract exp from JWT, save to keychain
9. Return id_token
```

#### Security: `waitForCallback(port, expectedState, abortSignal, onListening)`

- Creates HTTP server bound to `127.0.0.1` (localhost only)
- Validates `state` parameter against expected value (CSRF protection)
- Sanitizes error messages with `xss()` before rendering HTML
- Handles `EADDRINUSE` with diagnostic command hint
- 5-minute timeout with `.unref()` to not pin event loop
- `onListening` fires before browser open (prevents spurious tabs on port conflict)

#### Integration Points

- Used by `auth.ts:performMCPXaaAuth()` for IdP auth
- Used by `auth.ts:ClaudeAuthProvider.xaaRefresh()` for silent token refresh
- Configured via `claude mcp xaa setup` CLI command
- Separate keychain domain from MCP server secrets (`mcpXaaIdp` vs `mcpOAuth`)

---

### 1.3 `services/mcp/useManageMCPConnections.ts` (1141 lines)

**React hook for MCP server lifecycle management — the central orchestrator of all MCP connection state in the UI.**

Handles initialization, connection, reconnection, notification routing, and channel integration.

#### Exports

| Export | Kind | Description |
|--------|------|-------------|
| `useManageMCPConnections()` | React hook | Main hook — returns `{ reconnectMcpServer, toggleMcpServer }` |

#### Hook Arguments

```typescript
function useManageMCPConnections(
  dynamicMcpConfig: Record<string, ScopedMcpServerConfig> | undefined,
  isStrictMcpConfig?: boolean,
): { reconnectMcpServer: (name: string) => Promise<...>, toggleMcpServer: (name: string) => Promise<void> }
```

#### Internal State

| Ref | Purpose |
|-----|---------|
| `reconnectTimersRef` | Maps server name → pending reconnect setTimeout handles (for cancellation) |
| `channelWarnedKindsRef` | Dedup set for channel-blocked notifications shown to user |
| `channelPermCallbacksRef` | Stable ref to `ChannelPermissionCallbacks` for channel permission relay |
| `pendingUpdatesRef` | Batched queue of `PendingUpdate` objects |
| `flushTimerRef` | Single setTimeout handle for batched flush |

#### Constants

| Constant | Value |
|----------|-------|
| `MAX_RECONNECT_ATTEMPTS` | 5 |
| `INITIAL_BACKOFF_MS` | 1000 |
| `MAX_BACKOFF_MS` | 30000 |
| `MCP_BATCH_FLUSH_MS` | 16 |

#### Architecture: Three Effects

**Effect 1: Initialize servers as pending (`sessionId` + `_pluginReconnectKey` deps)**
1. Reads all MCP configs via `getClaudeCodeMcpConfigs()`
2. Identifies stale plugin servers (removed from config) and disconnects them
3. Cancels pending reconnect timers for stale servers
4. Adds new servers as `'pending'` or `'disabled'` state to AppState
5. Runs on plugin reload (`_pluginReconnectKey`) to pick up new plugin MCP servers

**Effect 2: Load and connect MCP servers (`_authVersion` + `sessionId` + `_pluginReconnectKey` deps)**

Two-phase loading architecture:
```
Phase 1 (immediate): Claude Code local configs
├── Clear claude.ai cache
├── Start claude.ai fetch (promise kicked, not awaited)
├── getClaudeCodeMcpConfigs() → local configs
├── getMcpToolsCommandsAndResources() → connect all local servers
└── Does NOT await — connections run in parallel

Phase 2 (after claude.ai resolves):
├── await claudeaiPromise
├── filterMcpServersByPolicy()
├── dedupClaudeAiMcpServers() — remove servers already configured manually
├── Add claude.ai servers as 'pending' to AppState
└── getMcpToolsCommandsAndResources() → connect claude.ai servers
```

**Effect 3: Cleanup on unmount**
- Cancels all reconnect timers
- Flushes pending batched updates

#### `onConnectionAttempt` Callback

Called per-server as each connection attempt resolves. Handles three major responsibilities:

**1. State update**: Batched via `updateServer()` → batched into 16ms window → single `setAppState()`

**2. Elicitation handler**: Registers real elicitation handler on connected clients

**3. Per-type side effects**:

For `'connected'`:
- **Reconnection** (`client.onclose`):
  - Exponential backoff: 1s, 2s, 4s, 8s, 16s (capped at 30s)
  - Only for remote transports (not stdio/sdk)
  - Cancels if server was disabled during retry
  - Calls `reconnectMcpServerImpl()` for actual reconnection
  - 5 max attempts
- **Channel notification handler** (gated on `feature('KAIROS')`):
  - Runs `gateChannelServer()` to decide register/skip
  - On register: subscribes to `notifications/claude/channel` → wraps content → `enqueue()`
  - On register: subscribes to `notifications/claude/channel/permission` → resolves via `channelPermCallbacksRef`
  - On skip: removes any existing handler; surfaces toast for marketplace/allowlist/auth/policy
  - Logs `tengu_mcp_channel_gate` and `tengu_mcp_channel_message` events
- **`tools/list_changed` handler**: Clears cache, re-fetches tools, logs `tengu_mcp_list_changed`
- **`prompts/list_changed` handler**: Clears commands cache, re-fetches prompts + skills, logs event
- **`resources/list_changed` handler**: Clears resources + skills cache, re-fetches, logs event

#### Returned Functions

| Function | Description |
|----------|-------------|
| `reconnectMcpServer(serverName)` | Cancels auto-reconnect, calls `reconnectMcpServerImpl()`, calls `onConnectionAttempt` |
| `toggleMcpServer(serverName)` | Disable: persists to disk, disconnects, updates state to 'disabled'. Enable: persists, updates to 'pending', reconnects |

#### Analytics Events Emitted

| Event | When |
|-------|------|
| `tengu_mcp_servers` | After both phases complete — counts per scope + stdio commands (ant-only) |
| `tengu_mcp_channel_gate` | Per connected server with channel capability |
| `tengu_mcp_channel_message` | Per inbound channel notification |
| `tengu_mcp_list_changed` | Per tools/prompts/resources list change |

---

### 1.4 `services/mcp/channelNotification.ts` (316 lines)

**Channel notifications — MCP servers pushing user messages into the conversation.**

A "channel" (Discord, Slack, SMS, etc.) is an MCP server that:
- Exposes tools for outbound messages (standard MCP)
- Sends `notifications/claude/channel` for inbound (this file)

#### Exports

| Export | Kind | Description |
|--------|------|-------------|
| `ChannelMessageNotificationSchema` | Zod schema | Validates `notifications/claude/channel` notification |
| `CHANNEL_PERMISSION_METHOD` | const | `'notifications/claude/channel/permission'` |
| `ChannelPermissionNotificationSchema` | Zod schema | Validates structured permission reply |
| `CHANNEL_PERMISSION_REQUEST_METHOD` | const | `'notifications/claude/channel/permission_request'` |
| `ChannelPermissionRequestParams` | type | `{ request_id, tool_name, description, input_preview }` |
| `wrapChannelMessage()` | fn | Wraps content in `<channel>` XML tag |
| `getEffectiveChannelAllowlist()` | fn | Resolves org policy vs GrowthBook ledger |
| `gateChannelServer()` | fn | Full gate pipeline for channel registration |
| `findChannelEntry()` | fn | Matches server name against `--channels` entries |

#### Types

| Type | Description |
|------|-------------|
| `ChannelGateResult` | `{ action: 'register' } \| { action: 'skip', kind, reason }` |
| `ChannelGateResult['kind']` | `'capability' \| 'disabled' \| 'auth' \| 'policy' \| 'session' \| 'marketplace' \| 'allowlist'` |

#### Schema: `ChannelMessageNotificationSchema`
```typescript
{
  method: 'notifications/claude/channel',
  params: {
    content: string,
    meta?: Record<string, string>  // Opaque passthrough
  }
}
```

#### Schema: `ChannelPermissionNotificationSchema`
```typescript
{
  method: 'notifications/claude/channel/permission',
  params: {
    request_id: string,
    behavior: 'allow' | 'deny'
  }
}
```

#### `wrapChannelMessage(serverName, content, meta?)`

- Builds `<channel source="serverName" key="value">\ncontent\n</channel>`
- Sanitizes meta keys with `SAFE_META_KEY` regex (`/^[a-zA-Z_][a-zA-Z0-9_]*$/`)
- Escapes XML attribute values

#### `getEffectiveChannelAllowlist(sub, orgList)`

Resolution order:
1. Team/Enterprise orgs with `allowedChannelPlugins` in managed settings → org list
2. Everyone else → GrowthBook ledger (`tengu_harbor_ledger`)

#### Gate Pipeline: `gateChannelServer(serverName, capabilities, pluginSource)`

Ordered checks — first failure short-circuits:
```
1. capability    → Server must declare experimental['claude/channel']
2. disabled      → isChannelsEnabled() (GrowthBook tengu_harbor)
3. auth          → Must have claude.ai OAuth tokens
4. policy        → Team/Enterprise must have channelsEnabled: true
5. session       → Must be in --channels list
6. marketplace   → Plugin tag must match installed source
7. allowlist     → Must be in GrowthBook ledger or org list
8. register      → All checks pass
```

#### `findChannelEntry(serverName, channels)`

Matches server name against parsed `--channels` entries:
- `server:name` → exact match on name
- `plugin:name@marketplace` → matches second segment of `plugin:X:Y` runtime name

#### Integration Points

- Consumed by `useManageMCPConnections.ts` for handler registration
- Channel message wrapping feeds into `messageQueueManager.ts:enqueue()` for model consumption
- Permission events integrate with `channelPermissions.ts:createChannelPermissionCallbacks()`

---

### 1.5 `services/mcp/channelPermissions.ts` (240 lines)

**Permission prompts over channels (Telegram, iMessage, Discord).**

Mirrors `BridgePermissionCallbacks` — when Claude Code hits a permission dialog, it also sends the prompt via active channels and races the reply against local UI / bridge / hooks / classifier.

#### Exports

| Export | Kind | Description |
|--------|------|-------------|
| `isChannelPermissionRelayEnabled()` | fn | GrowthBook gate `tengu_harbor_permissions` |
| `PERMISSION_REPLY_RE` | RegExp | `/^\s*(y\|yes\|n\|no)\s+([a-km-z]{5})\s*$/i` |
| `shortRequestId()` | fn | Generates 5-letter ID from toolUseID |
| `truncateForPreview()` | fn | Truncates tool input to 200 chars for phone preview |
| `filterPermissionRelayClients()` | fn | Filters connected clients that support permission relay |
| `createChannelPermissionCallbacks()` | fn | Factory for `ChannelPermissionCallbacks` |

#### Types

| Type | Description |
|------|-------------|
| `ChannelPermissionResponse` | `{ behavior: 'allow' \| 'deny', fromServer: string }` |
| `ChannelPermissionCallbacks` | `{ onResponse(id, handler): unsub, resolve(id, behavior, fromServer): boolean }` |

#### Permission ID Generation: `shortRequestId(toolUseID)`

- FNV-1a hash → uint32 → base-25 encode → 5 letters
- Alphabet: `a-z` minus `'l'` (avoids `1/I` confusion)
- Blocklist check for offensive substrings; re-hashes with salt if found
- Cap at 10 retries (~1/700 hit rate, (1/700)^10 negligible)

Blocklist: 25 offensive terms checked as substrings in generated IDs.

#### `truncateForPreview(input)`
- JSON-stringifies input
- Truncates at 200 chars with `…` ellipsis
- `'(unserializable)'` on error

#### `filterPermissionRelayClients(clients, isInAllowlist)`

Three conditions, ALL required:
1. `type === 'connected'`
2. `isInAllowlist(name)` — in session's `--channels`
3. Declares BOTH `claude/channel` AND `claude/channel/permission` capabilities

#### `createChannelPermissionCallbacks()`

Factory that returns `ChannelPermissionCallbacks` with a closed-over `pending` Map:

- **`onResponse(requestId, handler)`**: Registers handler, lowercases key, returns unsubscribe
- **`resolve(requestId, behavior, fromServer)`**: Deletes BEFORE calling handler (reentrancy-safe, handles duplicates)
- NOT module-level, NOT in AppState — follows `CLAUDE.md` pattern

#### Integration Points

- Used by `useManageMCPConnections.ts` to create per-session callbacks
- Stored in AppState as `channelPermissionCallbacks` for `interactiveHandler.ts`
- Permission gate `tengu_harbor_permissions` is separate from channel gate `tengu_harbor`

---

### 1.6 `services/mcp/channelAllowlist.ts` (76 lines)

**Approved channel plugins allowlist — controls which plugins can register channel handlers.**

#### Exports

| Export | Kind | Description |
|--------|------|-------------|
| `ChannelAllowlistEntry` | type | `{ marketplace: string, plugin: string }` |
| `ChannelAllowlistSchema` | Zod schema | Array of `{ marketplace: string, plugin: string }` |
| `getChannelAllowlist()` | fn | Reads from GrowthBook feature `tengu_harbor_ledger` |
| `isChannelsEnabled()` | fn | Reads GrowthBook feature `tengu_harbor` (overall on/off) |
| `isChannelAllowlisted()` | fn | Pure check against allowlist by plugin source |

#### `isChannelAllowlisted(pluginSource)`

- Returns `false` for undefined pluginSource (non-plugin servers)
- Returns `false` for `@`-less sources (builtin/inline)
- Parses `pluginSource` via `parsePluginIdentifier()` to extract `{name, marketplace}`
- Checks against `getChannelAllowlist()` entries

#### Design Principles

- Plugin-level granularity: if a plugin is approved, all its channel servers are
- `--dangerously-load-development-channels` bypasses both allowlist kinds
- Lives in GrowthBook so it can be updated without a release
- Default false for `isChannelsEnabled()` — opt-in per session

---

### 1.7 `services/mcp/vscodeSdkMcp.ts` (112 lines)

**VS Code MCP SDK integration — bidirectional communication with VS Code via the internal `claude-vscode` MCP server.**

#### Exports

| Export | Kind | Description |
|--------|------|-------------|
| `LogEventNotificationSchema` | Zod schema | Validates `{ method: 'log_event', params: { eventName, eventData } }` |
| `notifyVscodeFileUpdated()` | fn | Sends `file_updated` notification to VS Code |
| `setupVscodeSdkMcp()` | fn | Sets up bidirectional MCP communication with VS Code |

#### `notifyVscodeFileUpdated(filePath, oldContent, newContent)`

- Only sends if `USER_TYPE === 'ant'` AND `vscodeMcpClient` is set
- Sends notification with `method: 'file_updated'`
- Silently ignores failures (`.catch`)

#### `setupVscodeSdkMcp(sdkClients)`

1. Finds the `claude-vscode` client from `sdkClients`
2. Stores reference in module-level `vscodeMcpClient`
3. Registers handler for `LogEventNotificationSchema` → prefixes event names with `tengu_vscode_` and re-logs
4. Sends `experiment_gates` notification with current Gate values:
   - `tengu_vscode_review_upsell` — Statsig gate
   - `tengu_vscode_onboarding` — Statsig gate
   - `tengu_quiet_fern` — GrowthBook feature (browser support)
   - `tengu_vscode_cc_auth` — GrowthBook feature (in-band OAuth)
   - `tengu_auto_mode_state` — tri-state: enabled/disabled/opt-in

#### Integration Points

- Called from initialization code (likely `main.tsx`)
- Uses module-level mutable state for client reference (single client lifetime)
- Re-logs prefixed events through the analytics system

---

### 1.8 `services/mcp/SdkControlTransport.ts` (136 lines)

**SDK MCP transport bridge — enables in-process MCP servers running in the SDK to communicate with the CLI.**

#### Architecture

Two transport classes form a bridge pair:

```
CLI Process                          SDK Process
┌──────────────────┐                ┌──────────────────┐
│ MCP Client        │               │ MCP Server        │
│   ↓               │               │   ↑               │
│ SdkControlClient  │───stdout──→   │ SdkControlServer  │
│ Transport         │←──stdin────   │ Transport         │
└──────────────────┘                └──────────────────┘
```

#### Exports

| Export | Kind | Description |
|--------|------|-------------|
| `SendMcpMessageCallback` | type | `(serverName: string, message: JSONRPCMessage) => Promise<JSONRPCMessage>` |
| `SdkControlClientTransport` | class | CLI-side transport — sends messages via callback, awaits response |
| `SdkControlServerTransport` | class | SDK-side transport — receives messages, sends responses via callback |

#### `SdkControlClientTransport`

Implements `Transport` interface:
- **`start()`**: No-op (connection is already established)
- **`send(message)`**: Calls `sendMcpMessage(serverName, message)` → waits for response → routes to `this.onmessage`
- **`close()`**: Sets `isClosed`, calls `onclose`
- Guards against double-close and send-after-close

#### `SdkControlServerTransport`

Implements `Transport` interface:
- **`start()`**: No-op
- **`send(message)`**: Forwards response through constructor-injected callback
- **`close()`**: Sets `isClosed`, calls `onclose`

#### Message Flow

```
CLI → SDK:
1. MCP Client calls tool → SdkControlClientTransport.send(jsonrpcRequest)
2. Wraps in control request with server_name + request_id
3. sendMcpMessage callback sends via stdout to SDK
4. SDK's StructuredIO receives → SdkControlServerTransport.onmessage
5. MCP Server processes → calls transport.send(response)
6. sendMcpMessage callback sends response back → resolves original promise

SDK → CLI:
1. StructuredIO receives control request → transport.onmessage
2. MCP Server processes → transport.send(response)
3. sendMcpMessage callback sends response back
4. Query resolves pending promise with response
```

#### Integration Points

- Created in `client.ts` for `type: 'sdk'` MCP servers
- Supports multiple SDK MCP servers running simultaneously (routed by `serverName`)
- Message IDs preserved through entire flow for correlation

---

### 1.9 `services/mcp/claudeai.ts` (164 lines)

**Claude.ai organization MCP servers — fetches and manages org-level MCP configurations.**

#### Exports

| Export | Kind | Description |
|--------|------|-------------|
| `fetchClaudeAIMcpConfigsIfEligible` | memoized async fn | Fetches MCP server configs from claude.ai API |
| `clearClaudeAIMcpConfigsCache()` | fn | Clears memoized cache + auth cache |
| `markClaudeAiMcpConnected(name)` | fn | Records that a server connected successfully |
| `hasClaudeAiMcpEverConnected(name)` | fn | Checks if a server was ever connected |

#### Types

| Type | Description |
|------|-------------|
| `ClaudeAIMcpServer` | `{ type: 'mcp_server', id, display_name, url, created_at }` |
| `ClaudeAIMcpServersResponse` | `{ data: ClaudeAIMcpServer[], has_more, next_page }` |

#### `fetchClaudeAIMcpConfigsIfEligible()`

Eligibility checks:
1. `ENABLE_CLAUDEAI_MCP_SERVERS` env var disabled? → `disabled_env_var`
2. No OAuth tokens? → `no_oauth_token`
3. No `user:mcp_servers` scope? → `missing_scope`
4. API fetch from `{BASE_API_URL}/v1/mcp_servers?limit=1000`
5. Normalizes names with dedup suffixes `(2)`, `(3)` for collisions
6. Returns `claudeai`-scoped configs with `type: 'claudeai-proxy'`

Emits `tengu_claudeai_mcp_eligibility` events for each state.

#### Config Format
```typescript
{
  [displayName]: {
    type: 'claudeai-proxy',
    url: server.url,
    id: server.id,
    scope: 'claudeai',
  }
}
```

#### `clearClaudeAIMcpConfigsCache()`

- Clears lodash memoize cache
- Calls `clearMcpAuthCache()` from `client.ts`

#### Integration Points

- Consumed by `config.ts` merge pipeline via `getAllMcpConfigs()`
- `markClaudeAiMcpConnected()` gates "N connectors unavailable" startup notification
- Used in `useManageMCPConnections.ts` Phase 2 loading

---

### 1.10 `services/mcp/headersHelper.ts` (138 lines)

**Dynamic auth headers for MCP connections — resolves headers from helper scripts.**

#### Exports

| Export | Kind | Description |
|--------|------|-------------|
| `getMcpHeadersFromHelper()` | async fn | Executes headersHelper script, returns parsed JSON headers |
| `getMcpServerHeaders()` | async fn | Combines static + dynamic headers |

#### `getMcpHeadersFromHelper(serverName, config)`

- Returns `null` if `config.headersHelper` is absent
- **Security check**: Blocks for project/local scope if workspace trust not confirmed
- Executes the helper script via `execFileNoThrowWithCwd()` with:
  - Shell: true, timeout: 10s
  - Env vars: `CLAUDE_CODE_MCP_SERVER_NAME`, `CLAUDE_CODE_MCP_SERVER_URL`
- Validates output is a JSON object with string key-value pairs
- Returns `null` on error (non-blocking)

#### `getMcpServerHeaders(serverName, config)`

Merges headers with priority:
```
staticHeaders (low) → dynamicHeaders (high, overrides static)
```

#### Security: Trust Check

```typescript
if (config.scope === 'project' || config.scope === 'local') {
  // Requires workspace trust confirmation before executing helper
  // Skips in non-interactive mode (CI/CD)
  checkHasTrustDialogAccepted() → else return null + log error
}
```

#### Integration Points

- Called from `client.ts` during transport creation for sse/http/ws servers
- Helper scripts follow git credential-helper pattern (one script serves multiple servers)
- Returns `null` on failure to avoid blocking connection

---

### 1.11 `services/mcp/normalization.ts` (23 lines)

**Pure server name normalization — zero dependencies.**

#### Exports

| Export | Kind | Description |
|--------|------|-------------|
| `normalizeNameForMCP(name)` | fn | Returns normalized name compatible with `^[a-zA-Z0-9_-]{1,64}$` |

#### `normalizeNameForMCP(name)`

- Replaces any character not in `[a-zA-Z0-9_-]` with `_`
- For claude.ai servers (prefix `claude.ai `): collapses consecutive underscores, strips leading/trailing underscores
- Used to build consistent `mcp__<server>__<tool>` tool names

#### Integration Points

- Used by `mcpStringUtils.ts`, `claudeai.ts`, `config.ts`, and across the MCP subsystem
- Must stay dependency-free to avoid circular imports

---

### 1.12 `services/mcp/mcpStringUtils.ts` (106 lines)

**MCP name parsing and building — lightweight string utilities.**

#### Exports

| Export | Kind | Description |
|--------|------|-------------|
| `mcpInfoFromString()` | fn | Parses `mcp__server__tool` → `{ serverName, toolName? }` |
| `getMcpPrefix()` | fn | Returns `mcp__<normalizedServer>__` |
| `buildMcpToolName()` | fn | Constructs `mcp__<server>__<tool>` |
| `getToolNameForPermissionCheck()` | fn | Returns qualified name for permission rule matching |
| `getMcpDisplayName()` | fn | Strips prefix from full MCP name |
| `extractMcpToolDisplayName()` | fn | Extracts display name from user-facing format `"server - tool (MCP)"` |

#### Known Limitation

Server names containing `__` cause incorrect parsing. Example: `mcp__my__server__tool` parses as server=`my`, tool=`server__tool`.

#### `mcpInfoFromString(toolString)`

```
Input:  "mcp__slack__send_message"
Output: { serverName: "slack", toolName: "send_message" }

Input:  "mcp__my__server__tool"
Output: { serverName: "my", toolName: "server__tool" } // WAIT, this is WRONG
```

#### `getToolNameForPermissionCheck(tool)`

- For MCP tools: returns fully qualified `mcp__server__tool` name
- For builtins: returns `tool.name` as-is
- Prevents deny rules targeting builtins from accidentally matching MCP replacements

#### `extractMcpToolDisplayName(userFacingName)`

```
Input:  "github - Add comment to issue (MCP)"
Output: "Add comment to issue"

Input:  "Write"
Output: "Write"
```

#### Integration Points

- Used by permission system, command filtering, UI display
- Inverse of `normalization.ts` `normalizeNameForMCP()`

---

### 1.13 `services/mcp/officialRegistry.ts` (72 lines)

**Official MCP registry integration — fetches and caches the known MCP server URL list.**

#### Exports

| Export | Kind | Description |
|--------|------|-------------|
| `prefetchOfficialMcpUrls()` | async fn | Fire-and-forget fetch of the MCP registry |
| `isOfficialMcpUrl()` | fn | Checks if a URL is in the official registry |
| `resetOfficialMcpUrlsForTesting()` | fn | Resets for test isolation |

#### Registry Source
```
GET https://api.anthropic.com/mcp-registry/v0/servers?version=latest&visibility=commercial
```

#### URL Normalization

```typescript
function normalizeUrl(url: string): string | undefined {
  // Strips query string and trailing slash
  // Matches getLoggingSafeMcpBaseUrl normalization
}
```

#### `isOfficialMcpUrl(normalizedUrl)`

- Returns `true` if URL is in the official registry Set
- Fail-closed: `undefined` registry → `false`
- Input MUST be pre-normalized via `getLoggingSafeMcpBaseUrl()`

#### Integration Points

- Used by `analytics/metadata.ts:isAnalyticsToolDetailsLoggingEnabled()` — official MCP servers get detailed tool name logging
- Called at startup to populate in-memory URL cache
- Respects `CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC` env var

---

### 1.14 `services/mcp/envExpansion.ts` (38 lines)

**Environment variable expansion in MCP config values.**

#### Exports

| Export | Kind | Description |
|--------|------|-------------|
| `expandEnvVarsInString(value)` | fn | Expands `${VAR}` and `${VAR:-default}` patterns |

#### `expandEnvVarsInString(value)`

```typescript
function expandEnvVarsInString(value: string): {
  expanded: string
  missingVars: string[]
}
```

- Supports `${VAR}` syntax (not `$VAR`)
- Supports `${VAR:-default}` for default values
- Splits on `:-` (limited to 2 parts to preserve `:-` in defaults)
- Tracks missing variables for error reporting
- Leaves unknown variables unexpanded in output

#### Integration Points

- Called by `config.ts:expandEnvVarsInConfig()` for MCP config values
- Applied to `command`, `args`, `env` values in server configurations

---

### 1.15 `services/mcp/InProcessTransport.ts` (63 lines)

**In-process linked transport pair for same-process MCP server/client communication.**

#### Exports

| Export | Kind | Description |
|--------|------|-------------|
| `createLinkedTransportPair()` | fn | Returns `[Transport, Transport]` — client and server transports |

#### Architecture

```typescript
class InProcessTransport implements Transport {
  private peer: InProcessTransport | undefined  // Linked to counterpart
  private closed = false

  async send(message): Promise<void> {
    // Uses queueMicrotask to deliver asynchronously
    // Prevents stack depth issues with sync request/response cycles
    queueMicrotask(() => this.peer?.onmessage?.(message))
  }

  async close(): Promise<void> {
    // Closes BOTH sides of the pair
    if (this.peer && !this.peer.closed) {
      this.peer.closed = true
      this.peer.onclose?.()
    }
  }
}
```

#### `createLinkedTransportPair()`

```
[a = new InProcessTransport(), b = new InProcessTransport()]
a._setPeer(b)
b._setPeer(a)
return [a, b]  // [clientTransport, serverTransport]
```

#### Integration Points

- Used for testing (no network/stdio overhead)
- Used for IDE-embedded MCP servers
- Bypasses all network/stdio overhead

---

## Part II: Analytics Services Deep Dive

### Coverage Summary

All 9 files in `services/analytics/` are NOT covered in any previous analysis document.

| File | Lines | Focus |
|------|-------|-------|
| `index.ts` | 173 | Public API — event queue, sink attachment |
| `sink.ts` | 114 | Routing logic — Datadog + 1P dispatch |
| `sinkKillswitch.ts` | 25 | Per-sink kill switch via GrowthBook |
| `config.ts` | 38 | Analytics enable/disable logic |
| `metadata.ts` | 973 | Event metadata enrichment |
| `datadog.ts` | 307 | Datadog HTTP logs intake |
| `firstPartyEventLogger.ts` | 449 | OpenTelemetry-based 1P event logging |
| `firstPartyEventLoggingExporter.ts` | 806 | Custom OTel exporter with retry + disk persistence |
| `growthbook.ts` | 1155 | GrowthBook feature flags + experiment system |

---

### 2.1 `services/analytics/index.ts` (173 lines)

**Public API for event logging — central entry point for all analytics.**

Architecture:
```
logEvent() → queued until attachAnalyticsSink() → sink routes to Datadog + 1P
```

#### Exports

| Export | Kind | Description |
|--------|------|-------------|
| `AnalyticsMetadata_I_VERIFIED_THIS_IS_NOT_CODE_OR_FILEPATHS` | type | `never` — marker type for PII safety |
| `AnalyticsMetadata_I_VERIFIED_THIS_IS_PII_TAGGED` | type | `never` — marker type for privileged proto columns |
| `stripProtoFields()` | fn | Strips `_PROTO_*` keys for general-access sinks |
| `AnalyticsSink` | type | `{ logEvent, logEventAsync }` |
| `attachAnalyticsSink()` | fn | Attaches sink, drains queued events |
| `logEvent()` | fn | Sync event logging (fire-and-forget) |
| `logEventAsync()` | async fn | Async event logging |
| `_resetForTesting()` | fn | Resets module state for tests |

#### Event Queue

Events logged before a sink is attached are queued in `eventQueue: QueuedEvent[]`. When `attachAnalyticsSink()` is called:
1. Copies queue
2. Clears original
3. Drains via `queueMicrotask()` (non-blocking after startup)

#### `stripProtoFields(metadata)`

- Returns a shallow copy with all `_PROTO_*` keys removed
- Returns original reference unchanged when no `_PROTO_*` keys present
- Guards all non-1P sinks (Datadog) from PII-tagged values

#### Integration Points

- Consumed by every file that logs events across the entire codebase
- `sink.ts` implements the `AnalyticsSink` interface
- Marker types are used extensively across MCP, OAuth, and all tengu events

---

### 2.2 `services/analytics/sink.ts` (114 lines)

**Analytics sink implementation — routes events to Datadog and 1P event logging.**

#### Exports

| Export | Kind | Description |
|--------|------|-------------|
| `initializeAnalyticsGates()` | fn | Reads gate values at startup |
| `initializeAnalyticsSink()` | fn | Attaches sink to `index.ts` |

#### Event Flow

```
logEventImpl(eventName, metadata)
├── shouldSampleEvent(eventName)
│   ├── 0 → drop (sampled out)
│   ├── null → passthrough (no sample rate)
│   └── number → add sample_rate to metadata
├── shouldTrackDatadog()
│   └── Gate: tengu_log_datadog_events (GrowthBook)
│   └── Killswitch: isSinkKilled('datadog')
├── trackDatadogEvent(eventName, stripProtoFields(metadata))
│   └── Only if Datadog gate enabled
└── logEventTo1P(eventName, metadata)
    └── Always (1P gets full payload including _PROTO_*)
```

#### Gate Initialization

`initializeAnalyticsGates()` reads `tengu_log_datadog_events` from GrowthBook disk cache once at startup. Early events use cached value from previous session.

#### Integration Points

- Called from `main.tsx` during `setupBackend()`
- `attachAnalyticsSink()` is idempotent (multiple calls = no-op)

---

### 2.3 `services/analytics/sinkKillswitch.ts` (25 lines)

**Per-sink analytics killswitch controlled by GrowthBook dynamic config.**

#### Exports

| Export | Kind | Description |
|--------|------|-------------|
| `SinkName` | type | `'datadog' \| 'firstParty'` |
| `isSinkKilled(sink)` | fn | Checks if sink is disabled via GrowthBook |

#### Config

GrowthBook dynamic config: `tengu_frond_boric`
```typescript
{ datadog?: boolean, firstParty?: boolean }
```

- `true` for a key stops all dispatch to that sink
- Default `{}` (nothing killed)
- Fail-open: missing/malformed config = sink stays on
- **Safety**: Must NOT be called from inside `is1PEventLoggingEnabled()` (circular dependency with GrowthBook)

#### Integration Points

- `isSinkKilled('datadog')` — checked in `sink.ts:shouldTrackDatadog()`
- `isSinkKilled('firstParty')` — checked in `firstPartyEventLogger.ts:logEventTo1P()`
- Also injected into `FirstPartyEventLoggingExporter` constructor for backoff retry gate

---

### 2.4 `services/analytics/config.ts` (38 lines)

**Analytics enable/disable logic — shared across all analytics systems.**

#### Exports

| Export | Kind | Description |
|--------|------|-------------|
| `isAnalyticsDisabled()` | fn | Checks all disable conditions |
| `isFeedbackSurveyDisabled()` | fn | Checks feedback survey conditions |

#### `isAnalyticsDisabled()`

Returns `true` when ANY is true:
- `NODE_ENV === 'test'`
- `CLAUDE_CODE_USE_BEDROCK` env var set
- `CLAUDE_CODE_USE_VERTEX` env var set
- `CLAUDE_CODE_USE_FOUNDRY` env var set
- `isTelemetryDisabled()` — privacy level `no-telemetry` or `essential-traffic`

#### `isFeedbackSurveyDisabled()`

Only blocks on:
- `NODE_ENV === 'test'`
- `isTelemetryDisabled()`
Does NOT block on 3P providers (Bedrock/Vertex/Foundry) — survey is local UI with no transcript data.

#### Integration Points

- Used by `datadog.ts:initializeDatadog()`
- Used by `firstPartyEventLogger.ts:is1PEventLoggingEnabled()`
- Used by `growthbook.ts:isGrowthBookEnabled()` (indirectly via `is1PEventLoggingEnabled`)

---

### 2.5 `services/analytics/metadata.ts` (973 lines)

**Shared event metadata enrichment — single source of truth for collecting and formatting event metadata across all analytics systems.**

#### Exports

| Export | Kind | Description |
|--------|------|-------------|
| `AnalyticsMetadata_I_VERIFIED_THIS_IS_NOT_CODE_OR_FILEPATHS` | type | `never` marker type |
| `sanitizeToolNameForAnalytics()` | fn | Redacts MCP tool names to `'mcp_tool'` |
| `isToolDetailsLoggingEnabled()` | fn | Checks `OTEL_LOG_TOOL_DETAILS` env var |
| `isAnalyticsToolDetailsLoggingEnabled()` | fn | Checks if detailed MCP names can be logged |
| `mcpToolDetailsForAnalytics()` | fn | Returns `{mcpServerName, mcpToolName}` if gate passes |
| `extractMcpToolDetails()` | fn | Parses `mcp__server__tool` → `{serverName, mcpToolName}` |
| `extractSkillName()` | fn | Extracts skill name from Skill tool input |
| `extractToolInputForTelemetry()` | fn | Serializes + truncates tool input for OTel |
| `getFileExtensionForAnalytics()` | fn | Extracts sanitized file extension |
| `getFileExtensionsFromBashCommand()` | fn | Extracts file extensions from bash command |
| `getEventMetadata()` | async fn | Builds core event metadata |
| `to1PEventFormat()` | fn | Converts metadata to 1P event logging format |

#### Types

| Type | Description |
|------|-------------|
| `EnvContext` | Platform, runtime, CI flags, version info, VCS |
| `ProcessMetrics` | `{ uptime, rss, heapTotal, heapUsed, external, arrayBuffers, constrainedMemory, cpuUsage, cpuPercent }` |
| `EventMetadata` | Core metadata shared across all analytics: `{ model, sessionId, userType, betas?, envContext, entrypoint?, isInteractive, clientType, processMetrics?, agentId?, parentSessionId?, agentType?, teamName?, subscriptionType?, rh?, kairosActive?, skillMode?, observerMode? }` |
| `EnrichMetadataOptions` | `{ model?, betas?, additionalMetadata? }` |
| `FirstPartyEventLoggingCoreMetadata` | Snake_case version: `{ session_id, model, user_type, ... }` |
| `FirstPartyEventLoggingMetadata` | `{ env, process?, auth?, core, additional }` |

#### PII Sanitization

**`sanitizeToolNameForAnalytics(toolName)`:**
- MCP tools (starting `mcp__`) → `'mcp_tool'`
- Built-in tools (Bash, Read, Write) → pass through

**`isAnalyticsToolDetailsLoggingEnabled(mcpServerType, mcpServerBaseUrl)`:**

Detailed MCP names are logged only for:
1. Cowork agents (`CLAUDE_CODE_ENTRYPOINT === 'local-agent'`)
2. claude.ai-proxied connectors (type `claudeai-proxy`)
3. Servers matching the official MCP registry URL

**`mcpToolDetailsForAnalytics(toolName, mcpServerType, mcpServerBaseUrl)`:**
- Spreadable helper: returns `{mcpServerName, mcpToolName}` if gate passes, `{}` otherwise
- Also checks `BUILTIN_MCP_SERVER_NAMES` set (e.g., `computer-use`)

#### Tool Input Truncation (`extractToolInputForTelemetry`)

```typescript
const TOOL_INPUT_STRING_TRUNCATE_AT = 512   // Strings > 512 chars → truncated
const TOOL_INPUT_STRING_TRUNCATE_TO = 128    // Truncated to 128 chars + "[N chars]"
const TOOL_INPUT_MAX_JSON_CHARS = 4 * 1024   // Max serialized JSON length
const TOOL_INPUT_MAX_COLLECTION_ITEMS = 20   // Max array/object entries
const TOOL_INPUT_MAX_DEPTH = 2               // Max recursive depth
```

Filtered: internal marker keys starting with `_` (e.g., `_simulatedSedEdit`).

#### `buildEnvContext()` (memoized async)

Returns a complete `EnvContext` with:
- Platform detection (including WSL, Linux distro)
- Terminal type
- Package managers + runtimes
- CI/CD detection (GitHub Actions + event details)
- Claude Code remote/container identification
- Coworker type (feature-gated)
- Deploy environment detection
- VCS detection

#### `buildProcessMetrics()` (per-call)

Tracks CPU% delta between calls using `prevCpuUsage` + `prevWallTimeMs` module-level state.

#### `getEventMetadata(options)`

Enriches metadata with:
1. Model name + betas
2. Environment context
3. Process metrics
4. Agent identification (AsyncLocalStorage → env vars → bootstrap state)
5. Subscription type, kairos mode, repo hash
6. SWE-bench identifiers

#### `to1PEventFormat(metadata, userMetadata, additionalMetadata)`

Converts camelCase `EventMetadata` → snake_case `FirstPartyEventLoggingMetadata`:
- `env` is typed as proto-generated `EnvironmentMetadata` (compile-time validation)
- `core` fields get direct BQ columns
- `additional` fields go into `additional_metadata` JSON blob
- GitHub Actions metadata placed in `env.github_actions_metadata`
- Process metrics base64-encoded
- Auth fields from user metadata

#### Integration Points

- Used by `datadog.ts:trackDatadogEvent()` for Datadog metadata enrichment
- Used by `firstPartyEventLogger.ts:logEventTo1PAsync()` for 1P event enrichment
- Used by `firstPartyEventLoggingExporter.ts:transformLogsToEvents()` for final proto formatting
- `isOfficialMcpUrl()` imported from MCP officialRegistry

---

### 2.6 `services/analytics/datadog.ts` (307 lines)

**Datadog HTTP logs intake — batches and sends events to Datadog.**

#### Constants

| Constant | Value |
|----------|-------|
| `DATADOG_LOGS_ENDPOINT` | `https://http-intake.logs.us5.datadoghq.com/api/v2/logs` |
| `DATADOG_CLIENT_TOKEN` | `pubbbf48e6d78dae54bceaa4acf463299bf` |
| `DEFAULT_FLUSH_INTERVAL_MS` | 15000 |
| `MAX_BATCH_SIZE` | 100 |
| `NETWORK_TIMEOUT_MS` | 5000 |
| `NUM_USER_BUCKETS` | 30 |

#### Allowed Events (`DATADOG_ALLOWED_EVENTS`)

64 events in the allowlist set, including:
- `tengu_api_error`, `tengu_api_success`
- `tengu_init`, `tengu_started`, `tengu_exit`, `tengu_cancel`
- `tengu_tool_use_*` (success, error, granted, rejected)
- `tengu_oauth_*`, `tengu_model_fallback_triggered`
- `tengu_brief_*`, `tengu_compact_failed`, `tengu_flicker`
- `tengu_query_error`, `tengu_session_file_read`
- `tengu_uncaught_exception`, `tengu_unhandled_rejection`
- `tengu_voice_*`, `tengu_team_mem_*`
- `chrome_bridge_*` events

#### Exports

| Export | Kind | Description |
|--------|------|-------------|
| `initializeDatadog` | memoized async fn | Initializes Datadog (checks analytics disabled) |
| `shutdownDatadog()` | async fn | Flushes remaining logs on shutdown |
| `trackDatadogEvent()` | async fn | Batches and sends a single event |

#### Module State

| Variable | Purpose |
|----------|---------|
| `logBatch` | `DatadogLog[]` — accumulating batch |
| `flushTimer` | `setTimeout` handle for scheduled flush |
| `datadogInitialized` | `boolean \| null` — gate state (null = uninitialized) |

#### `trackDatadogEvent(eventName, properties)`

Flow:
1. **Skip if**: not production, not first-party provider, event not in allowlist
2. **Lazy init**: `datadogInitialized === null` → `await initializeDatadog()`
3. **Enrich**: call `getEventMetadata()` → merge with properties
4. **Cardinality reduction**:
   - MCP tool names → `'mcp'`
   - External user model names → canonical name or `'other'`
   - Dev versions → truncate to `base.date` format
5. **Field transform**: `status` → `http_status` + `http_status_range` (Datadog reserved field)
6. **Tags**: `event:<name>` + known tag fields in snake_case
7. **Batch**: push to `logBatch`, flush if `>= MAX_BATCH_SIZE` or schedule flush in 15s

#### `getUserBucket()` (memoized)

SHA-256 hash of user ID → modulus 30 buckets. Used for user-count estimation without high-cardinality user ID.

#### `shutdownDatadog()`

- Cancels pending flush timer
- Forces immediate flush
- Called from `gracefulShutdown()`

#### Integration Points

- Called from `sink.ts:logEventImpl()` when Datadog gate is enabled
- Uses `config.ts:isAnalyticsDisabled()` for gate
- Uses `metadata.ts:getEventMetadata()` for enrichment

---

### 2.7 `services/analytics/firstPartyEventLogger.ts` (449 lines)

**First-party event logging via OpenTelemetry — batches events and exports to `/api/event_logging/batch`.**

#### Exports

| Export | Kind | Description |
|--------|------|-------------|
| `EventSamplingConfig` | type | `{ [eventName]: { sample_rate: number } }` |
| `getEventSamplingConfig()` | fn | Reads sampling config from GrowthBook |
| `shouldSampleEvent()` | fn | Returns sample rate or null/0 based on config |
| `shutdown1PEventLogging()` | async fn | Graceful shutdown of OTel provider |
| `is1PEventLoggingEnabled()` | fn | Checks analytics disabled gate |
| `logEventTo1P()` | fn | Logs an event to 1P analytics |
| `GrowthBookExperimentData` | type | `{ experimentId, variationId, userAttributes?, experimentMetadata? }` |
| `logGrowthBookExperimentTo1P()` | fn | Logs experiment assignment to 1P |
| `initialize1PEventLogging()` | fn | Creates OTel LoggerProvider |
| `reinitialize1PEventLoggingIfConfigChanged()` | async fn | Rebuilds pipeline on config change |

#### Sampling (`shouldSampleEvent`)

- Reads `tengu_event_sampling_config` from GrowthBook dynamic config
- No config for event → 100% (returns `null`)
- `sample_rate >= 1` → 100% (returns `null`)
- `sample_rate <= 0` → 0% (returns `0`)
- Otherwise: `Math.random() < sampleRate ? sampleRate : 0`

#### 1P Event Logging Pipeline

```
initialize1PEventLogging()
├── is1PEventLoggingEnabled()? no → return
├── getBatchConfig() → scheduledDelayMillis, maxExportBatchSize, etc.
├── Create Resource with service name + version + WSL attributes
└── Create LoggerProvider:
    ├── Resource (minimal, separate from customer OTLP)
    ├── BatchLogRecordProcessor
    │   └── FirstPartyEventLoggingExporter
    └── Logger: 'com.anthropic.claude_code.events'
```

#### `logEventTo1P(eventName, metadata)`

1. Checks `is1PEventLoggingEnabled()`
2. Checks `firstPartyEventLogger` is initialized
3. Checks `isSinkKilled('firstParty')`
4. Fires `logEventTo1PAsync()` — fire-and-forget

#### `logEventTo1PAsync(firstPartyEventLogger, eventName, metadata)`

1. Enriches with `getEventMetadata()` (model, session, env context)
2. Builds OTel attributes with `event_name`, `event_id` (UUID), `core_metadata`, `user_metadata`, `event_metadata`
3. Emits OTel log record

#### `logGrowthBookExperimentTo1P(data)`

1. Enriches with device ID, account UUID, org UUID
2. Builds `GrowthbookExperimentEvent` attributes
3. Emits OTel log record with body `'growthbook_experiment'`

#### `reinitialize1PEventLoggingIfConfigChanged()`

Detects GrowthBook config changes and rebuilds pipeline:
1. Null the logger (new events bail during swap)
2. `forceFlush()` the old provider (failures go to disk)
3. `initialize1PEventLogging()` with new config
4. On failure: restore old provider/logger
5. Old provider shutdown runs in background

#### Integration Points

- `sink.ts:logEventImpl()` calls `logEventTo1P()` for every event
- `growthbook.ts` calls `logGrowthBookExperimentTo1P()` for experiment exposures
- Uses custom exporter `FirstPartyEventLoggingExporter`

---

### 2.8 `services/analytics/firstPartyEventLoggingExporter.ts` (806 lines)

**OpenTelemetry LogRecordExporter for 1P event logging — sends to `/api/event_logging/batch` with retry + disk persistence.**

Implements the OTel `LogRecordExporter` interface. Export cycles are controlled by `BatchLogRecordProcessor`.

#### Exports

| Export | Kind | Description |
|--------|------|-------------|
| `FirstPartyEventLoggingExporter` | class | Custom OTel exporter |

#### Class State

| Property | Description |
|----------|-------------|
| `endpoint` | API URL for batch event logging |
| `timeout` | HTTP timeout (default 10s) |
| `maxBatchSize` | Events per HTTP request (default 200) |
| `skipAuth` | Whether to skip auth headers |
| `baseBackoffDelayMs` | Base backoff delay (500ms) |
| `maxBackoffDelayMs` | Max backoff delay (30s) |
| `maxAttempts` | Max retry attempts (default 8) |
| `isKilled` | Injected killswitch probe |
| `pendingExports` | In-flight export promises |
| `isShutdown` | Shutdown flag |
| `attempts` | Current backoff retry count |
| `isRetrying` | Retry-in-progress flag |
| `cancelBackoff` | Cancel function for scheduled backoff |
| `lastExportErrorContext` | Last error context string |

#### Resilience Features

1. **Append-only log for failed events** — concurrency-safe JSONL file
2. **Quadratic backoff** — `base * attempts²`, capped at `maxBackoffDelayMs`
3. **Immediate retry** of queued events when any export succeeds
4. **Chunking** large event sets into `maxBatchSize` batches
5. **Auth fallback** — retries without auth on 401 errors
6. **Disk persistence** — failed events survive process restart

#### `export(logs, resultCallback)`

OTel callback interface. Filters for `com.anthropic.claude_code.events` scope, transforms to internal format, sends via `sendEventsInBatches()`.

#### `sendEventsInBatches(events)`

- Chunks events into batches of `maxBatchSize`
- Sends with `batchDelayMs` between batches
- Short-circuits on first failure (assumes endpoint down)
- Returns list of failed events

#### `sendBatchWithRetry(payload)`

1. Checks killswitch → throws if killed
2. Builds headers with User-Agent
3. Checks trust + auth availability
4. Tries with auth headers first
5. On 401 → retries without auth
6. Logs success with auth status

#### Disk Storage

- Directory: `{CLAUDE_CONFIG_DIR}/telemetry/`
- File pattern: `1p_failed_events.{sessionId}.{BATCH_UUID}.json`
- Format: JSONL (one event per line)
- `retryPreviousBatches()` on construction — loads + retries from previous runs

#### Backoff Strategy

```typescript
const delay = Math.min(
  baseBackoffDelayMs * attempts * attempts,  // Quadratic
  maxBackoffDelayMs,                           // Capped at 30s
)
```

- Resets on successful export
- Drops events after `maxAttempts` (default 8)

#### Transform: `transformLogsToEvents(logs)`

Converts OTel log records to `FirstPartyEventLoggingEvent[]`:
1. **GrowthBook experiments**: Extracts event fields, constructs `GrowthbookExperimentEvent.toJSON()`
2. **Regular events**: Extracts `coreMetadata`, `userMetadata`, `eventMetadata` → `to1PEventFormat()`
3. **Missing core metadata**: Creates partial event with error marker
4. **Proto fields**: Hoists known `_PROTO_*` keys to top-level fields, strips remaining `_PROTO_*`

#### Integration Points

- Constructed by `firstPartyEventLogger.ts:initialize1PEventLogging()`
- Sends to `https://api.anthropic.com/api/event_logging/batch`
- Uses proto-generated types: `ClaudeCodeInternalEvent`, `GrowthbookExperimentEvent`

---

### 2.9 `services/analytics/growthbook.ts` (1155 lines)

**GrowthBook feature flag client — manages remote eval, disk cache, experiment exposure logging, and periodic refresh.**

#### Exports

| Export | Kind | Description |
|--------|------|-------------|
| `GrowthBookUserAttributes` | type | User attributes for targeting |
| `onGrowthBookRefresh()` | fn | Register callback fired on feature refresh |
| `hasGrowthBookEnvOverride()` | fn | Checks `CLAUDE_INTERNAL_FC_OVERRIDES` env var |
| `getAllGrowthBookFeatures()` | fn | Enumerates all known features |
| `getGrowthBookConfigOverrides()` | fn | Returns local config overrides |
| `setGrowthBookConfigOverride()` | fn | Set/clear a single override |
| `clearGrowthBookConfigOverrides()` | fn | Clear all overrides |
| `initializeGrowthBook()` | memoized async fn | Init client, blocks until ready |
| `getFeatureValue_DEPRECATED()` | async fn | Blocks on init |
| `getFeatureValue_CACHED_MAY_BE_STALE()` | fn | Non-blocking, reads memory then disk |
| `getFeatureValue_CACHED_WITH_REFRESH()` | fn | (deprecated) Delegates to `_CACHED_MAY_BE_STALE` |
| `checkStatsigFeatureGate_CACHED_MAY_BE_STALE()` | fn | Migration helper: checks GB then Statsig |
| `checkSecurityRestrictionGate()` | async fn | Waits for re-init if in progress |
| `checkGate_CACHED_OR_BLOCKING()` | async fn | Fast `true` from cache, blocks for `false` |
| `refreshGrowthBookAfterAuthChange()` | fn | Destroys + recreates client with new auth |
| `resetGrowthBook()` | fn | Full reset for testing |
| `refreshGrowthBookFeatures()` | async fn | Light refresh without client recreation |
| `setupPeriodicGrowthBookRefresh()` | fn | Sets up 20min/6hr refresh interval |
| `stopPeriodicGrowthBookRefresh()` | fn | Stops refresh interval |
| `getDynamicConfig_BLOCKS_ON_INIT()` | async fn | Dynamic config that blocks on init |
| `getDynamicConfig_CACHED_MAY_BE_STALE()` | fn | Non-blocking dynamic config |

#### Architecture

```
GrowthBook Client
├── API: https://api.anthropic.com/ (with auth headers)
├── remoteEval: true (server-side evaluation)
├── Cache key: [id, organizationUUID]
├── In-memory: remoteEvalFeatureValues Map
├── Disk cache: GlobalConfig.cachedGrowthBookFeatures
└── Periodic refresh: 20min (ant) / 6hr (external)
```

#### Feature Value Resolution Order

For all getter functions:
```
1. Env var override (CLAUDE_INTERNAL_FC_OVERRIDES — ant only)
2. Config override (/config Gates tab — ant only)
3. In-memory remoteEval cache (processRemoteEvalPayload)
4. Disk cache (cachedGrowthBookFeatures)
5. Default value
```

#### Module State

| Variable | Purpose |
|----------|---------|
| `client` | GrowthBook client instance |
| `remoteEvalFeatureValues` | `Map<string, unknown>` — in-memory payload cache |
| `experimentDataByFeature` | `Map<string, StoredExperimentData>` — for exposure logging |
| `loggedExposures` | `Set<string>` — dedup exposure events per session |
| `pendingExposures` | `Set<string>` — deferred until init completes |
| `reinitializingPromise` | `Promise \| null` — tracks re-init for security gates |
| `refreshed` | Signal (pub/sub) for refresh listeners |

#### Initialization: `getGrowthBookClient()` (memoized)

1. Checks `isGrowthBookEnabled()` → `is1PEventLoggingEnabled()`
2. Builds user attributes from CoreUserData
3. Checks workspace trust → gets auth headers
4. Creates GrowthBook client with remoteEval, cache key attributes, auth headers
5. No auth → returns client with resolved promise (skips HTTP init)
6. With auth → `client.init({ timeout: 5000 })`
7. On init success: `processRemoteEvalPayload()`, `logExposureForFeature()` for pending, `syncRemoteEvalToDisk()`, emits `refreshed`

#### `processRemoteEvalPayload(gbClient)`

Workaround for API returning `{ value: ... }` instead of `{ defaultValue: ... }`:
1. Transforms features: `value` → `defaultValue`
2. Extracts experiment data for exposure logging
3. Re-sets the payload via `setPayload()`
4. Populates `remoteEvalFeatureValues` Map

#### `syncRemoteEvalToDisk()`

Wholesale replace (not merge) of `cachedGrowthBookFeatures` in `GlobalConfig`. Only called on successful payload (not on failure — prevents init-timeout poisoning).

#### Feature Getters

| Function | Blocking | Source | Use Case |
|----------|----------|--------|----------|
| `_CACHED_MAY_BE_STALE` | No | Memory → Disk | Preferred for all paths |
| `_DEPRECATED` | Yes | Network wait | Legacy, prefer cached |
| `checkStatsigFeatureGate` | No | GB → Statsig cache | Migration only |
| `checkSecurityRestrictionGate` | Maybe | Waits re-init | Security gates |
| `checkGate_CACHED_OR_BLOCKING` | Conditional | Cache true fast, block false | Entitlement gates |

#### Experiment Exposure Logging

```typescript
function logExposureForFeature(feature: string): void {
  // Dedup: each feature logged at most once per session
  if (loggedExposures.has(feature)) return

  const expData = experimentDataByFeature.get(feature)
  if (expData) {
    loggedExposures.add(feature)
    logGrowthBookExperimentTo1P({
      experimentId: expData.experimentId,
      variationId: expData.variationId,
      userAttributes: getUserAttributes(),
      experimentMetadata: { feature_id: feature },
    })
  }
}
```

#### Auth Change: `refreshGrowthBookAfterAuthChange()`

1. `resetGrowthBook()` — destroys client, clears all caches
2. Emits `refreshed` so subscribers read disk cache (fresh)
3. `initializeGrowthBook()` — creates new client with fresh auth
4. Sets `reinitializingPromise` for security gate coordination

#### Refresh Architecture

Two refresh mechanisms:
1. **Auth change** (`refreshGrowthBookAfterAuthChange`): Destroys + recreates client (needed because `apiHostRequestHeaders` is immutable)
2. **Light refresh** (`refreshGrowthBookFeatures`): Re-fetches features without recreating client (periodic)

#### Periodic Refresh

- Ant users: 20 minutes
- External users: 6 hours
- Timer `.unref()` so it doesn't pin the event loop
- Cleanup registered on `beforeExit`

#### Integration Points

- Used across the entire codebase for feature gating
- `initializeGrowthBook()` called during startup in `main.tsx`
- `refreshGrowthBookAfterAuthChange()` called on login/logout
- `firstPartyEventLogger.ts` reads dynamic configs for batch config + sampling
- `sink.ts` reads `tengu_log_datadog_events` gate
- `sinkKillswitch.ts` reads `tengu_frond_boric` config
- `channelAllowlist.ts` reads `tengu_harbor_ledger` + `tengu_harbor`
- `channelPermissions.ts` reads `tengu_harbor_permissions`
- `vscodeSdkMcp.ts` reads multiple gates for VS Code integration

---

## Part III: Data Flow Diagrams

### Analytics Event Flow

```
logEvent("tengu_xxx", { ... })
  │
  ├── index.ts: queue until sink attached
  │
  └── sink.ts: logEventImpl()
      │
      ├── shouldSampleEvent() → sample_rate or drop
      │
      ├── shouldTrackDatadog()
      │   └── isSinkKilled('datadog')? → skip
      │   └── checkStatsigFeatureGate('tengu_log_datadog_events')
      │       └── trackDatadogEvent()
      │           └── datadog.ts
      │               ├── Lazy init
      │               ├── getEventMetadata() → enrich
      │               ├── Cardinality reduction
      │               ├── Batch + flush (15s / 100 events)
      │               └── POST to Datadog HTTP API
      │
      └── logEventTo1P()
          └── firstPartyEventLogger.ts
              ├── isSinkKilled('firstParty')? → skip
              └── fire-and-forget
                  └── firstPartyEventLoggingExporter.ts
                      ├── Buffer via BatchLogRecordProcessor
                      ├── Export cycle (5s / 200 events)
                      ├── sendBatchWithRetry()
                      │   ├── Auth headers → 401→retry without
                      │   └── Disc failure queue → quadratic backoff
                      └── POST to /api/event_logging/batch
```

### MCP Channel Notification Flow

```
MCP Server sends notifications/claude/channel
  │
  ├── gateChannelServer() gate pipeline
  │   ├── capability → must declare claude/channel
  │   ├── disabled → tengu_harbor gate
  │   ├── auth → OAuth required
  │   ├── policy → org opt-in
  │   ├── session → --channels list
  │   ├── marketplace → plugin tag matches
  │   ├── allowlist → GrowthBook ledger
  │   └── register → all pass
  │
  ├── [register]
  │   ├── wrapChannelMessage() → <channel> tag
  │   └── enqueue({ mode: 'prompt', ... }) → model sees it
  │
  └── [skip] → log + optional toast
```

### XAA Auth Flow (Browserless)

```
performMCPXaaAuth()
  │
  ├── [No cached id_token]
  │   └── acquireIdpIdToken()
  │       ├── discoverOidc(issuer) → OIDC metadata
  │       ├── startAuthorization() → PKCE auth URL
  │       ├── Browser pop at IdP
  │       ├── exchangeAuthorization() → id_token
  │       └── Cache id_token in keychain
  │
  ├── [Cached id_token] → skip browser
  │
  └── performCrossAppAccess()
      ├── discoverProtectedResource() → PRM
      ├── discoverAuthorizationServer() → AS metadata
      ├── requestJwtAuthorizationGrant() → id_token → ID-JAG
      ├── exchangeJwtAuthGrant() → ID-JAG → access_token
      └── Save tokens to keychain
```
