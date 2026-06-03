# Services Layer Analysis — File 3: MCP Services

> **Scope**: All files in `services/mcp/` (23 files)
> **Purpose**: Model Context Protocol integration — server connection management, OAuth authentication, configuration CRUD, tool execution, elicitation handling, and cross-app access.

---

## 1. MCP Client Connection & Tool Execution

### 1.1 `services/mcp/client.ts` (3087 lines)

**The central MCP client —** manages server connections and tool execution across all transport types.

#### Key exports (`client.ts` — no `MCPClient` class)

| Export | Purpose |
|---|---|
| `connectToServer` | Memoized server connection (stdio/SSE/HTTP/WS/sdk/claudeai-proxy) |
| `ensureConnectedClient` | Lazy connect/reconnect for a named server |
| `clearServerCache` | Evict cached connection(s) |
| `callMCPToolWithUrlElicitationRetry` | Tool execution with URL-elicitation retry |
| `processMCPResult` / `transformMCPResult` | Result normalization and truncation |
| `fetchToolsForClient` / `fetchResourcesForClient` / `fetchCommandsForClient` | Memoized discovery |
| `getMcpToolsCommandsAndResources` | Bulk tools/resources/prompts fetch |
| `reconnectMcpServerImpl` | Targeted reconnect |
| `setupSdkMcpClients` | In-process SDK MCP server wiring |
| `createClaudeAiProxyFetch` / `wrapFetchWithTimeout` | Fetch wrappers for remote servers |
| `McpAuthError` / `McpToolCallError_*` / `isMcpSessionExpiredError` | Error types |

Transports are created inside `connectToServer` (StdioClientTransport, SSEClientTransport, StreamableHTTPClientTransport, WebSocketTransport, SdkControlClientTransport, InProcessTransport).

#### Server Connection States

```typescript
type MCPServerConnection =
  | ConnectedMCPServer  // { type: 'connected', client: Client, capabilities, serverInfo, instructions, config, cleanup }
  | FailedMCPServer     // { type: 'failed', error, config }
  | NeedsAuthMCPServer  // { type: 'needs-auth', config }
  | PendingMCPServer    // { type: 'pending', reconnectAttempt, maxReconnectAttempts, config }
  | DisabledMCPServer   // { type: 'disabled', config }
```

#### Transport Types Supported

| Transport | Use Case | How Connected |
|---|---|---|
| `stdio` | Local MCP servers (npx, uvx, etc.) | Spawns subprocess, communicates via stdin/stdout JSON-RPC |
| `sse` | Remote MCP via Server-Sent Events | HTTP with SSE for server→client, POST for client→server |
| `sse-ide` | IDE-embedded MCP servers | Same as SSE with IDE-specific headers and platform info |
| `ws-ide` | IDE WebSocket MCP servers | WebSocket connection with auth token |
| `http` | Streamable HTTP MCP (MCP spec 2024+) | Bidirectional HTTP streaming |
| `ws` | WebSocket MCP servers | WebSocket with proxy/TLS support |
| `sdk` | In-process SDK MCP servers | Direct function calls via SdkControlClientTransport |
| `claudeai-proxy` | Claude.ai organization MCP | Proxy through claude.ai API |

#### Tool Execution Flow (`callMCPToolWithUrlElicitationRetry()`)

```
callMCPToolWithUrlElicitationRetry({ serverName, toolName, args, ... })
├── 1. Get connected client via ensureConnectedClient()
├── 2. Validate tool name (strip mcp__ prefix)
├── 3. Marshal arguments (handle binary content, file references)
├── 4. Call client.callTool() via MCP SDK
├── 5. Handle response:
│   ├── Success: transform result content blocks
│   │   ├── text → text blocks
│   │   ├── image → base64 image blocks (with resize/downsample)
│   │   ├── resource → resource link blocks
│   │   └── blob → persist to disk, return path reference
│   ├── isError: true → McpToolCallError
│   └── Error codes:
│       ├── -32001 (Session not found) → session expired, reconnect
│       ├── -32042 (Elicitation required) → trigger elicitation flow
│       └── Auth errors (401) → McpAuthError (status → 'needs-auth')
├── 6. Post-processing:
│   ├── Truncate oversized results via truncateMcpContentIfNeeded() (token limit, default 25k tokens)
│   ├── Recursively sanitize Unicode
│   ├── Persist tool results for scrollback
│   └── Emit tengu_mcp_tool_call analytics
└── 7. Progress reporting via progressCallback
```

#### Special Error Types

- **`McpAuthError`**: Thrown when tool call fails due to expired OAuth token → client status updated to `'needs-auth'`
- **`McpSessionExpiredError`**: Session not found (404 + JSON-RPC -32001) → connection cache cleared, retry with fresh client
- **`McpToolCallError`**: Tool returned `isError: true` → carries `_meta` for SDK consumers

#### Binary Content Handling

MCP tools can return binary content (images, files). The client:
1. Detects binary content by MIME type
2. Resizes/downsamples images to fit API limits
3. Persists blobs to disk in session temp directory
4. Returns path references + size descriptions instead of raw data
5. Supports `blob:` and `data:` URI schemes

---

### 1.2 `services/mcp/config.ts` (1578 lines)

**MCP configuration CRUD —** manages `.mcp.json`, `settings.json`, and enterprise managed config files.

#### Configuration Sources (in priority order, lowest wins in merge)

1. **Enterprise Managed** (`managed-mcp.json`) — IT-managed, read-only
2. **Claude.ai** (org MCP servers from claude.ai) — fetched via API
3. **User settings** (`settings.json` `mcpServers` key) — cross-project
4. **Project** (`.mcp.json` in workspace root) — per-project
5. **Local** (`.mcp.json` with `scope: 'local'`) — per-machine overrides
6. **Plugin** (plugin-provided MCP servers) — from enabled plugins
7. **Dynamic** (runtime-added, not persisted) — `/mcp add` without `--scope`

#### Key Functions

| Function | Purpose |
|---|---|
| `getAllMcpConfigs()` | Full merge of all config sources with dedup |
| `getMcpConfigsFromSettings()` | Reads from VS Code settings.json |
| `getMcpConfigsFromProject()` | Reads .mcp.json with atomic write support |
| `getMcpConfigsFromEnterprise()` | Reads managed-mcp.json |
| `addMcpConfig()` | Adds server to project/user config |
| `removeMcpConfig()` | Removes server from config |
| `parseMcpConfig()` / `parseMcpConfigFromFilePath()` | Parse and validate MCP config entries |
| `isMcpServerDisabled()` | Checks if server is disabled in settings |
| `filterMcpServersByPolicy()` | Applies allowlist/blocklist policies |
| `expandEnvVarsInConfig()` | Resolves ${VAR} references in config |
| `computeDedupSignature()` | Generates hash for plugin deduplication |
| `unwrapCcrProxyUrl()` | Extracts original URL from CCR proxy URLs |

#### Atomic File Writes

`writeMcpjsonFile()` uses temp file + `fsync` + rename:
1. Write to `.mcp.json.tmp.<pid>.<timestamp>`
2. `datasync()` to flush to disk
3. Restore original file permissions via `chmod`
4. Atomic `rename()` to target
5. Cleanup temp file on failure

#### Plugin Deduplication

When plugins provide MCP servers that users also manually configure:
- `computeDedupSignature()` generates a hash from command array or URL
- `getDuplicatedPluginServers()` identifies duplicates across sources
- Plugin-scoped servers take precedence; user config entries are silently dropped

#### CCR Proxy URL Handling

In remote (CCR) sessions, MCP URLs are rewritten to route through the session ingress proxy:
```
Original:  https://mcp.example.com/sse
Proxy:     https://ccr.anthropic.com/v2/session_ingress/shttp/mcp/...?mcp_url=https://mcp.example.com/sse
```
`unwrapCcrProxyUrl()` extracts the original `mcp_url` query param for dedup matching.

#### Policy Filtering

Settings can restrict which MCP servers are allowed:
- **Allowlist** (`mcp__<name>` settings): Only listed servers can connect
- **Blocklist**: Listed servers cannot connect
- **Plugin-only policy** (`mcp.pluginOnly`): Only plugin-provided servers allowed
- **Marketplace tier gates**: Free tier limited to N servers

---

### 1.3 `services/mcp/auth.ts` (2465 lines)

**Full MCP OAuth implementation —** PKCE flow, token management, refresh, revocation, cross-app access.

#### Architecture

```
MCP OAuth Flow
├── Authorization (PKCE)
│   ├── generateCodeVerifier() (`services/oauth/crypto.ts`) → SHA-256 → code_challenge (S256)
│   ├── Discover OAuth metadata from server
│   ├── Open browser to authorization URL
│   ├── Listen on localhost callback port
│   ├── Exchange authorization code for tokens
│   └── Persist tokens to system keychain
├── Token Management
│   ├── getCachedToken() → read from keychain
│   ├── refreshToken() → refresh with refresh_token
│   ├── ClaudeAuthProvider → SDK-compatible auth provider
│   └── Token storage: keychain (macOS) / credential store (Win) / file (Linux)
├── Cross-App Access (XAA / SEP-990)
│   ├── Detect XAA server config
│   ├── Acquire IdP id_token via OIDC
│   ├── Exchange id_token for MCP JWT access token
│   └── Cache XAA tokens
├── Error Handling
│   ├── Invalid grant → clear stored tokens, re-auth
│   ├── Transient errors → retry with backoff (3 attempts)
│   ├── Step-up detection → notify user to re-authenticate
│   └── Non-standard error code normalization (Slack, etc.)
└── Security
    ├── PKCE (S256 challenge method)
    ├── State parameter (CSRF protection)
    ├── Port binding (localhost only)
    ├── Redirect URI validation
    └── Sensitive param redaction in logs
```

#### PKCE Flow

```
1. Client generates code_verifier (random 64 bytes → base64url)
2. Computes code_challenge = SHA256(code_verifier) → base64url
3. Opens browser: authorization_url?code_challenge=...&code_challenge_method=S256&state=...
4. Server redirects to: http://localhost:{port}/callback?code=...&state=...
5. Client validates state matches
6. POSTs token endpoint: code + code_verifier → access_token + refresh_token
7. Stores tokens in system keychain
```

#### Token Storage

Tokens are persisted to the system's secure credential store:
- **macOS**: Keychain (via `macOsKeychainHelpers.ts`)
- **Windows**: Windows Credential Manager
- **Linux**: Encrypted file (`~/.config/claude/credentials.json.enc`)
- Each server gets its own keychain entry keyed by server name + URL

#### Token Refresh

`refreshToken()` is called when:
1. Tool call returns 401 (expired token)
2. Proactive check before connection (token expiring within 5 minutes)
3. Manual `/mcp reauth` command

Refresh flow:
```
1. Read stored refresh_token from keychain
2. POST to token endpoint with grant_type=refresh_token
3. On success: store new access_token + refresh_token
4. On invalid_grant: clear stored tokens, set status to 'needs-auth'
5. On transient error: retry up to 3 times with backoff
```

#### Cross-App Access (XAA)

SEP-990 compliant cross-app identity assertion:
- Detected via `xaa: true` in server OAuth config
- Uses OIDC to acquire id_token from IdP
- Exchanges id_token for MCP access token
- Separate token cache from regular OAuth
- Supports xaaIdpLogin.ts for IdP configuration

#### Non-Standard Error Normalization

Some OAuth providers (notably Slack) return HTTP 200 with error in body instead of 400. `normalizeOAuthErrorBody()` rewrites:
- Slack's `invalid_refresh_token` → `invalid_grant`
- Slack's `expired_refresh_token` → `invalid_grant`
- Any 200 with OAuth error schema → 400 response

#### ClaudeAuthProvider

Implements the MCP SDK's `OAuthClientProvider` interface:
- `getClientMetadata()` → returns Claude CLI metadata URL
- `getTokens()` → reads from keychain
- `saveTokens()` → writes to keychain
- `redirectUrl()` → localhost callback port
- `saveCodeVerifier()` / `codeVerifier()` → in-memory PKCE state

---

### 1.4 `services/mcp/types.ts` (258 lines)

**Comprehensive MCP type definitions.**

#### Config Schemas (Zod v4)

| Schema | Transport | Key Fields |
|---|---|---|
| `McpStdioServerConfigSchema` | stdio | command, args, env |
| `McpSSEServerConfigSchema` | sse | url, headers, headersHelper, oauth |
| `McpSSEIDEServerConfigSchema` | sse-ide | url, ideName, ideRunningInWindows |
| `McpWebSocketIDEServerConfigSchema` | ws-ide | url, ideName, authToken |
| `McpHTTPServerConfigSchema` | http | url, headers, headersHelper, oauth |
| `McpWebSocketServerConfigSchema` | ws | url, headers, headersHelper |
| `McpSdkServerConfigSchema` | sdk | name |
| `McpClaudeAIProxyServerConfigSchema` | claudeai-proxy | url, id |
| `McpOAuthConfigSchema` | (nested) | clientId, callbackPort, authServerMetadataUrl, xaa |

#### Config Scopes

```typescript
type ConfigScope = 'local' | 'user' | 'project' | 'dynamic' | 'enterprise' | 'claudeai' | 'managed'
```

#### Connection State Types

- `ConnectedMCPServer`: Active client + capabilities + server info + cleanup function
- `FailedMCPServer`: Failed connection with error message
- `NeedsAuthMCPServer`: Awaiting OAuth authentication
- `PendingMCPServer`: In progress (connecting/reconnecting, with attempt counter)
- `DisabledMCPServer`: Explicitly disabled in settings

#### MCP CLI State

`MCPCliState` is a serialization-friendly state snapshot used for CLI commands and status display:
- `clients[]`: Server connection states
- `configs{}`: Server configurations by name
- `tools[]`: Available tools with schemas
- `resources{}`: Available resources by server
- `normalizedNames{}`: Original → normalized name mappings

---

### 1.5 `services/mcp/utils.ts` (575 lines)

**Utility functions for MCP server management.**

| Function | Purpose |
|---|---|
| `filterToolsByServer()` | Filters tool array by MCP server prefix `mcp__<server>__` |
| `filterCommandsByServer()` | Filters commands (prompts + skills) by server |
| `filterMcpPromptsByServer()` | Filters MCP prompts only (excludes skills) |
| `filterResourcesByServer()` | Filters resource lists by server name |
| `commandBelongsToServer()` | Checks if command belongs to server (prompts: `mcp__<s>__`, skills: `<s>:`) |
| `isToolFromMcpServer()` | Checks if tool name belongs to a specific MCP server |
| `getLoggingSafeMcpBaseUrl()` | Strips auth params from URL for safe logging |
| `computeMcpConfigHash()` | Deterministic hash for config change detection |
| `getMcpScopeLabel()` | Human-readable scope names for UI display |
| `getProjectMcpServerStatus()` | Project-level server status tracking |
| `isMcpServerAllowed()` | Policy allowlist/blocklist check |
| `filterConfigsByPolicy()` | Bulk filter via settings policy |
| `getMcpServerCounts()` | Server count by status (connected, failed, pending, etc.) |

---

### 1.6 Remaining MCP Files

#### `services/mcp/elicitationHandler.ts` (313 lines)

**Elicitation request handling.** When MCP servers request user input:

- **Two modes**: `form` (structured input) and `url` (browser-based OAuth/authorization)
- **Request lifecycle**: 
  1. Server sends `elicitation/create` JSON-RPC request
  2. Client shows UI (form or "Open browser" prompt)
  3. User completes action → response sent back
  4. URL mode: server sends `elicitation/complete` notification → client dismisses waiting UI
- **Hook integration**: Runs `elicitationHooks` first for programmatic responses
- **Queue management**: Maintains per-server elicitation queue, re-processes on reconnect
- **Timeout**: 5-minute default, configurable
- **Error retry**: -32042 error code triggers retry flow with "Retry now" button

#### `services/mcp/oauthPort.ts` (78 lines)

**OAuth redirect port helpers.** Finds available localhost ports for OAuth callback listeners:
- `findAvailablePort()` — probes ports in range, returns first available
- `buildRedirectUri()` — constructs `http://localhost:{port}/callback`

#### `services/mcp/MCPConnectionManager.tsx` (73 lines)

**React context for MCP state.** Provides an `MCPConnectionManager` React context that wraps:
- Server connection state (connected, failed, pending, etc.)
- Connection lifecycle methods (connect, disconnect, reconnect)
- Available tools, prompts, and resources
- OAuth authorization triggers

#### `services/mcp/InProcessTransport.ts` (63 lines)

**In-process MCP transport.** Allows MCP server logic to run in the same process:
- Adapts a Transport interface for in-process communication
- Used primarily for testing and IDE-embedded MCP servers
- Bypasses network/stdio overhead

#### `services/mcp/SdkControlTransport.ts` (136 lines)

**SDK transport bridge.** Bridges the MCP SDK's transport interface:
- Implements `Transport` for `McpSdkServerConfig` (type: 'sdk')
- Adapts custom in-process transport to standard MCP SDK interface
- Handles message routing and JSON-RPC framing
- Handles `RootsListChangedNotification` for workspace root tracking
- Sends `sampling/createMessage` requests for SDK-side model calls

#### `services/mcp/officialRegistry.ts` (72 lines)

**Official MCP server registry.** Static list of known MCP servers with metadata:
- Server name, description, install command, category
- Used for `/mcp discover` and marketplace suggestions

#### `services/mcp/normalization.ts` (23 lines)

**Server name normalization.** `normalizeNameForMCP()` converts server names to a canonical form:
- Lowercase
- Replace spaces/hyphens with underscores
- Remove special characters
- Used to build consistent `mcp__<server>__<tool>` tool names

#### `services/mcp/mcpStringUtils.ts` (106 lines)

**MCP name parsing and building.** 
- `mcpInfoFromString()` — parses `mcp__server__tool` back into {server, tool}
- `buildMcpToolName()` — constructs `mcp__<server>__<tool>` from components
- `buildMcpPromptName()` — constructs `mcp__<server>__<prompt>` for prompt commands
- `parseMcpServerName()` — extracts server name from tool/prompt name

#### `services/mcp/headersHelper.ts` (138 lines)

**Dynamic auth headers for MCP connections.** 
- `getMcpServerHeaders()` — resolves dynamic headers for remote MCP servers
- Supports `headersHelper` config: runs a command to get auth headers
- Supports static headers from config
- Merges OAuth Bearer tokens when authenticated
- Caches helper command output with TTL to avoid per-request overhead
- Executes the helper script via `execFileNoThrowWithCwd()` with shell, **10s timeout**

#### `services/mcp/envExpansion.ts` (38 lines)

**Environment variable expansion.** `expandEnvVarsInString()` resolves `${VAR}` and `$VAR` patterns in MCP config values:
- Replaces environment variable references at config load time
- Supports both `${VAR}` and `$VAR` syntax
- Leaves unknown variables unexpanded (no error)

#### `services/mcp/claudeai.ts` (164 lines)

**Claude.ai organization MCP servers.** Fetches and manages organization-level MCP configurations:
- `fetchClaudeAIMcpConfigsIfEligible()` — checks eligibility, fetches from API
- `markClaudeAiMcpConnected()` — notifies server of successful connection
- Uses OAuth token for authentication
- Configs cached with TTL in GlobalConfig
- Servers appear with `claudeai` scope

#### `services/mcp/channelAllowlist.ts` (69 lines)

**MCP channel allowlists.** Controls which MCP channels (tool categories) are available to which server scopes. Used for marketplace/server tier restrictions.

#### `services/mcp/channelNotification.ts` (297 lines)

**MCP notification routing.** Routes MCP notifications (resource updates, tool changes, prompt updates) to the appropriate handlers (UI updates, tool cache invalidation).

#### `services/mcp/channelPermissions.ts` (226 lines)

**MCP channel permissions.** Permission model for MCP channels:
- User consent for tool categories
- Scope-based restrictions (enterprise vs user-installed servers)
- Persistent permission grants with revocation

#### `services/mcp/useManageMCPConnections.ts` (1057 lines)

**React hook for MCP lifecycle.** `useManageMCPConnections()`:
- Manages connect/disconnect/reconnect lifecycle
- Handles parallel connection with concurrency limits
- Provides status updates for UI rendering
- Integrates with MCPConnectionManager context

#### `services/mcp/vscodeSdkMcp.ts`

**VS Code SDK MCP integration.** Bridges VS Code's MCP extension system:
- Discovers VS Code-installed MCP servers
- Maps VS Code MCP config format to Claude Code's format
- Handles VS Code-specific auth and transport settings

#### `services/mcp/xaa.ts`

**XAA/SEP-990 JWT exchange.** Implements the Cross-App Access token exchange:
- `performCrossAppAccess()` — acquires IdP id_token, exchanges for JWT access token
- `XaaTokenExchangeError` — custom error for exchange failures
- Handles token endpoint communication
- Validates JWT response format

#### `services/mcp/xaaIdpLogin.ts`

**XAA IdP OIDC login.** Manages IdP discovery and login for cross-app access:
- `discoverOidc()` — OIDC discovery endpoint (`.well-known/openid-configuration`)
- `acquireIdpIdToken()` — full OIDC authorization code flow
- `getCachedIdpIdToken()` — reads cached XAA id_token from secure storage
- `clearIdpIdToken()` — clears cached token on logout
- `getXaaIdpSettings()` — reads IdP configuration from settings
- `isXaaEnabled()` — checks if XAA is configured for any server
- `getIdpClientSecret()` — reads client secret from secure storage

---

## 2. MCP Lifecycle Diagram

```
Startup
  │
  ├── getAllMcpConfigs() ─────► Merge all config sources
  │   ├── Enterprise (managed-mcp.json)
  │   ├── Claude.ai (API fetch)
  │   ├── User settings (settings.json)
  │   ├── Project (.mcp.json)
  │   ├── Plugin (enabled plugins)
  │   └── Dynamic (runtime --mcp-config)
  │
  ├── filterMcpServersByPolicy() ─────► Apply allowlist/blocklist
  │
  └── connectToServer() (per server, batched) ─────► Connect each allowed server
      │
      ├── [stdio] → spawn process → StdioClientTransport
      ├── [sse/http] → ClaudeAuthProvider (if OAuth)
      │   ├── hasMcpDiscoveryButNoToken() → discover first
      │   └── Needs auth → set status 'needs-auth'
      ├── [sdk] → SdkControlClientTransport
      └── [claudeai-proxy] → proxy through claude.ai
      │
      ├── On connect: list tools, resources, prompts
      ├── On fail: exponential reconnect (max 5, 1s-32s)
      └── On auth error: status → 'needs-auth'
```

### Tool Call Flow

```
User types message → LLM decides to call MCP tool
  │
  ├── callMCPToolWithUrlElicitationRetry(...)
  │   ├── ensureConnectedClient() → get live client
  │   ├── client.callTool({ name, arguments })
  │   └── Process response
  │
  ├── [401] → refreshToken() → retry
  │   └── [invalid_grant] → status → 'needs-auth'
  │
  ├── [-32001] → session expired → reconnect → retry
  │
  ├── [-32042] → elicitation required
  │   └── Show user prompt → collect response → retry
  │
  └── [Success] → transform content
      ├── text → TextBlockParam
      ├── image → BetaImageBlockParam (resized)
      ├── resource → ResourceLink
      └── blob → file path reference
```

### OAuth Flow

```
Server config has oauth config
  │
  ├── hasMcpToken() → read from keychain
  ├── [No] → start OAuth flow
  │   ├── discoverAuthorizationServerMetadata()
  │   ├── generate PKCE (code_verifier + code_challenge)
  │   ├── Open browser with authorization URL
  │   ├── Listen on localhost callback
  │   ├── Receive authorization code
  │   ├── Exchange code for tokens
  │   └── Save tokens to keychain
  │
  ├── [Yes, expiring] → refreshToken()
  │   ├── POST token endpoint (refresh_token grant)
  │   ├── [Success] → store new tokens
  │   └── [invalid_grant] → clear tokens, restart OAuth
  │
  └── [XAA configured] → performCrossAppAccess()
      ├── discoverOidc() → IdP configuration
      ├── acquireIdpIdToken() → OIDC flow
      └── Exchange id_token for MCP JWT token
```
