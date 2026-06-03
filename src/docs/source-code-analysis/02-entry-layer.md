# 02 — Entry & Bootstrap Layer

This document provides an exhaustive analysis of the entry, bootstrap, and CLI layers of Claude Code — every file, every function, every significant code path. This layer governs how the process starts, how it is configured, and how it communicates with external consumers (SDKs, IDEs, MCP clients, remote bridges).

---

## ENTRYPOINTS (8 files)

### `entrypoints/cli.tsx` (303 lines)

**The very first file executed.** Its `main()` function is called immediately via a top-level `void main()` side-effect. All imports are dynamic to minimize module evaluation for fast-path commands that need zero or few modules loaded.

#### Top-Level Side Effects (before `main()`)
1. **Corepack fix** (line 5): Sets `process.env.COREPACK_ENABLE_AUTO_PIN = '0'` to prevent corepack from auto-pinning yarn to package.json.
2. **CCR heap sizing** (lines 9–14): When `CLAUDE_CODE_REMOTE=true`, sets `NODE_OPTIONS` to `--max-old-space-size=8192` (8 GB) for CCR container environments.
3. **Ablation baseline** (lines 21–26): Feature-gated (`ABLATION_BASELINE`) block that sets 7 environment variables (`CLAUDE_CODE_SIMPLE`, `CLAUDE_CODE_DISABLE_THINKING`, `DISABLE_INTERLEAVED_THINKING`, `DISABLE_COMPACT`, `DISABLE_AUTO_COMPACT`, `CLAUDE_CODE_DISABLE_AUTO_MEMORY`, `CLAUDE_CODE_DISABLE_BACKGROUND_TASKS`) to `'1'` for L0 ablation baselines. Uses the `feature('ABLATION_BASELINE')` guard so Bun's DCE eliminates the entire block from external builds.

#### `main()` Function — Fast-Path Dispatch

The function implements a prioritized fast-path dispatch chain. Each path early-returns, avoiding the full CLI load:

1. **`--version` / `-v` / `-V`** (line 37-42): Zero-import fast path. Prints `MACRO.VERSION (Claude Code)` and returns. MACRO.VERSION is inlined at build time.

2. **Startup profiler import** (line 45-48): All remaining paths load `profileCheckpoint` from `utils/startupProfiler.js` and call `profileCheckpoint('cli_entry')`.

3. **`--dump-system-prompt`** (lines 53-71): Feature-gated (`DUMP_SYSTEM_PROMPT`). Loads `enableConfigs`, `getMainLoopModel`, and `getSystemPrompt` to render and print the full system prompt. Optionally accepts `--model` to switch which model's prompt is rendered. Ant-only; eliminated from external builds via feature flag.

4. **`--claude-in-chrome-mcp`** (lines 72-78): Loads `runClaudeInChromeMcpServer` and starts it.

5. **`--chrome-native-host`** (lines 79-85): Loads `runChromeNativeHost` for Chrome Native Messaging integration.

6. **`--computer-use-mcp`** (lines 86-93): Feature-gated (`CHICAGO_MCP`). Loads and starts the Computer Use MCP server.

7. **`--daemon-worker=<kind>`** (lines 100-106): Feature-gated (`DAEMON`). Internal fast path for supervisor-spawned workers. Loads `runDaemonWorker` from `daemon/workerRegistry.js` and passes the worker kind. No `enableConfigs()` or analytics sinks — workers are lean. Must come before the daemon subcommand check.

8. **Bridge/remote-control** (lines 112-162): Feature-gated (`BRIDGE_MODE`). Handles `claude remote-control`, `remote`, `sync`, `bridge`, and `rc` subcommands. Performs auth check (`getClaudeAIOAuthTokens`), GrowthBook gate check (`getBridgeDisabledReason`), version check (`checkBridgeMinVersion`), and policy limits check (`isPolicyAllowed('allow_remote_control')`) before calling `bridgeMain(args.slice(1))`.

9. **Daemon subcommand** (lines 165-180): Feature-gated (`DAEMON`). Handles `claude daemon [subcommand]`. Loads `enableConfigs`, `initSinks`, and `daemonMain`.

10. **Background sessions** (lines 185-209): Feature-gated (`BG_SESSIONS`). Handles `claude ps`, `logs`, `attach`, `kill`, and `--bg`/`--background` flags. Loads `cli/bg.js` and dispatches to `psHandler`, `logsHandler`, `attachHandler`, `killHandler`, or `handleBgFlag`.

11. **Template job commands** (lines 212-222): Feature-gated (`TEMPLATES`). Handles `claude new`, `list`, `reply`. Calls `templatesMain(args)` then `process.exit(0)` (Ink TUI can leave event loop handles).

12. **Environment runner** (lines 226-233): Feature-gated (`BYOC_ENVIRONMENT_RUNNER`). Handles `claude environment-runner`. Calls `environmentRunnerMain`.

13. **Self-hosted runner** (lines 238-245): Feature-gated (`SELF_HOSTED_RUNNER`). Handles `claude self-hosted-runner`. Calls `selfHostedRunnerMain`.

14. **Tmux + worktree fast path** (lines 248-274): When `--tmux` and `--worktree`/`-w` flags are both present, attempts `execIntoTmuxWorktree`. If handled, returns. On error, calls `exitWithError`.

15. **Update flag redirect** (lines 277-279): Redirects `claude --update` or `claude --upgrade` to `claude update` by rewriting `process.argv`.

16. **`--bare` flag** (lines 283-285): Sets `CLAUDE_CODE_SIMPLE=1` early so gates fire during module evaluation and Commander option building.

17. **Full CLI fallback** (lines 288-298): No special flags detected. Starts capturing early input (`startCapturingEarlyInput`), loads `main.js` (`main: cliMain`), and calls `cliMain()`.

### `entrypoints/init.ts` (340 lines)

**Memoized initialization function.** Called at startup before any user-facing work. Uses `lodash-es/memoize` so calling `init()` multiple times returns the cached promise (re-entrant safe). Tracks `telemetryInitialized` flag to prevent double initialization of telemetry.

#### `init` (memoized, line 57-238)

Sequential initialization steps:

1. **Config validation** (line 65): Calls `enableConfigs()` to validate and load the configuration system. Catches `ConfigParseError` — in non-interactive sessions writes to stderr and graceful-shutdowns; in interactive sessions shows `InvalidConfigDialog`.

2. **Safe environment variables** (line 74): `applySafeConfigEnvironmentVariables()` — applies only safe env vars before trust dialog.

3. **Extra CA certs** (line 79): `applyExtraCACertsFromConfig()` — applies `NODE_EXTRA_CA_CERTS` from settings.json before any TLS connections (Bun caches the TLS cert store at boot via BoringSSL).

4. **Graceful shutdown setup** (line 87): `setupGracefulShutdown()` — registers process signal handlers for clean exit.

5. **1P event logging** (lines 94-106): Fires a `Promise.all` for `firstPartyEventLogger.js` and `growthbook.js`, then calls `fp.initialize1PEventLogging()` and wires `gb.onGrowthBookRefresh` to reinitialize logging if config changes.

6. **OAuth account info** (line 110): `populateOAuthAccountInfoIfNeeded()` — populates OAuth account info if not cached (needed after VSCode extension login).

7. **JetBrains detection** (line 114): `initJetBrainsDetection()` — async, populates cache for later sync access.

8. **Repository detection** (line 118): `detectCurrentRepository()` — async, populates cache for gitDiff PR linking.

9. **Remote settings/policy initialization** (lines 123-128): If eligible, initializes loading promises for `RemoteManagedSettings` and `PolicyLimits`.

10. **First start time** (line 132): `recordFirstStartTime()`.

11. **mTLS configuration** (lines 135-141): `configureGlobalMTLS()` — configures global mutual TLS settings.

12. **Proxy configuration** (lines 144-151): `configureGlobalAgents()` — configures global HTTP agents for proxy/mTLS.

13. **API preconnect** (line 159): `preconnectAnthropicApi()` — fire-and-forget TCP+TLS handshake warmup. Skipped for proxy/mTLS/unix/cloud-provider environments.

14. **CCR upstream proxy** (lines 167-183): If `CLAUDE_CODE_REMOTE` is truthy, loads `initUpstreamProxy` and `getUpstreamProxyEnv` from `upstreamproxy/upstreamproxy.js`, registers the proxy env function, and initializes the upstream proxy. Fail-open on error.

15. **Windows shell fix** (line 186): `setShellIfWindows()` — sets up git-bash if relevant.

16. **LSP cleanup registration** (line 189): `registerCleanup(shutdownLspServerManager)`.

17. **Team cleanup registration** (lines 195-200): Registers `cleanupSessionTeams()` for gh-32730 — teams created by subagents without explicit `TeamDelete` were left on disk forever.

18. **Scratchpad initialization** (lines 203-209): If scratchpad is enabled, calls `ensureScratchpadDir()`.

19. **Error handling** (lines 215-237): Config parse errors show `InvalidConfigDialog` in interactive mode or write to stderr in non-interactive mode. Other errors rethrow.

#### `initializeTelemetryAfterTrust()` (line 247-286)

Called after trust is granted. For remote-settings-eligible users, waits for settings to load (non-blocking) then re-applies env vars before initializing telemetry. For SDK/headless mode with beta tracing, eagerly initializes telemetry first to ensure the tracer is ready before the first query. `doInitializeTelemetry()` is a no-op if already initialized.

#### `doInitializeTelemetry()` (line 288-303)

Guards against double initialization via `telemetryInitialized` flag. Calls `setMeterState()`.

#### `setMeterState()` (line 305-339)

Lazy-loads `initializeTelemetry` from `utils/telemetry/instrumentation.js` (~400KB OpenTelemetry + protobuf modules). Creates a `createAttributedCounter` factory function that fetches fresh telemetry attributes per call. Calls `setMeter(meter, createAttributedCounter)`. Increments the session counter.

### `entrypoints/mcp.ts` (196 lines)

**MCP server that exposes Claude Code tools over stdio transport.** Enables IDE integration by making Claude Code tools available via the Model Context Protocol.

#### `startMCPServer(cwd, debug, verbose)` (line 35-196)

1. Creates a size-limited LRU cache for `readFileState` (100 files, 25 MB limit).
2. Sets the CWD via `setCwd(cwd)`.
3. Creates an MCP `Server` with name `claude/tengu` and capabilities `{ tools: {} }`.

**`ListToolsRequestSchema` handler** (lines 59-97):
- Gets tools from `getTools(toolPermissionContext)`.
- For each tool, converts `inputSchema` to JSON Schema via `zodToJsonSchema`.
- For `outputSchema`, validates the converted schema has `type: "object"` at root level (skips `anyOf`/`oneOf` unions — see issue #8014).
- Resolves tool descriptions via `tool.prompt()`.

**`CallToolRequestSchema` handler** (lines 99-188):
- Finds the tool by name via `findToolByName`.
- Checks `tool.isEnabled()`.
- Calls `tool.validateInput?.(args, toolUseContext)`.
- Calls `tool.call(args, toolUseContext, hasPermissionsToUseTool, createAssistantMessage)`.
- Returns text content (stringified via `jsonStringify` for non-string results).
- On error, returns `isError: true` with filtered error message via `getErrorParts`.

**`runServer()`** (lines 190-194): Creates `StdioServerTransport`, connects server to transport.

The `MCP_COMMANDS` array contains only the `review` command. The `ToolUseContext` created for tool calls uses:
- A fresh `AbortController`.
- Disabled thinking (`{ type: 'disabled' }`).
- Empty MCP clients and resources.
- `isNonInteractiveSession: true`.
- Empty agent definitions.
- No mutation side effects for `setInProgressToolUseIDs`, `setResponseLength`, `updateFileHistoryState`, `updateAttributionState`.

### `entrypoints/agentSdkTypes.ts` (443 lines)

**Public SDK API stubs.** This is the main entrypoint for SDK consumers (TypeScript/Python SDKs, IDE extensions). Functions throw `'not implemented'` — they exist as type stubs. The actual implementations live in the main CLI process.

#### Re-exports
- **Control protocol types**: `SDKControlRequest`, `SDKControlResponse` from `sdk/controlTypes.js` (marked `@alpha`).
- **Core types**: All from `sdk/coreTypes.js` and `sdk/runtimeTypes.js`.
- **Settings types**: `Settings` from `sdk/settingsTypes.generated.js` (generated from settings JSON schema).
- **Tool types**: All from `sdk/toolTypes.js` (marked `@internal`).

#### Exported Types
- `ListSessionsOptions`, `GetSessionInfoOptions`, `SessionMutationOptions`, `ForkSessionOptions`, `ForkSessionResult`, `SDKSessionInfo` — re-exported from runtime types.

#### Stub Functions

1. **`tool(_name, _description, _inputSchema, _handler, _extras?)`** (line 73-88): Stub for creating SDK MCP tool definitions. Accepts a Zod schema, handler function, and optional annotations/search hint/alwaysLoad. Returns `SdkMcpToolDefinition<Schema>`.

2. **`createSdkMcpServer(_options)`** (line 103-107): Stub for creating an MCP server instance for SDK transport. `CreateSdkMcpServerOptions` includes `name`, `version`, and optional `tools` array. Note: if calls will run longer than 60s, override `CLAUDE_CODE_STREAM_CLOSE_TIMEOUT`.

3. **`AbortError`** (line 109): Empty error class extending `Error`.

4. **`query(_params)`** (lines 112-122): Two overloads — one for `InternalOptions` (internal use), one for `Options` (public use). Returns `Query` or `InternalQuery`.

5. **`unstable_v2_createSession(_options)`** (lines 129-133): V2 API — creates a persistent session for multi-turn conversations. Returns `SDKSession`.

6. **`unstable_v2_resumeSession(_sessionId, _options)`** (lines 140-145): V2 API — resumes an existing session by ID.

7. **`unstable_v2_prompt(_message, _options)`** (lines 160-165): V2 API — one-shot convenience function for single prompts. Returns `Promise<SDKResultMessage>`.

8. **`getSessionMessages(_sessionId, _options?)`** (lines 178-183): Reads a session's conversation messages from its JSONL transcript file. Returns `Promise<SessionMessage[]>`.

9. **`listSessions(_options?)`** (lines 204-208): Lists sessions with metadata. Supports `dir`, `limit`, `offset` for pagination.

10. **`getSessionInfo(_sessionId, _options?)`** (lines 219-224): Reads metadata for a single session by ID. Returns `Promise<SDKSessionInfo | undefined>`.

11. **`renameSession(_sessionId, _title, _options?)`** (lines 232-238): Appends a custom-title entry to the session's JSONL file.

12. **`tagSession(_sessionId, _tag, _options?)`** (lines 246-252): Tags a session. Pass `null` to clear the tag.

13. **`forkSession(_sessionId, _options?)`** (lines 268-273): Forks a session into a new branch with fresh UUIDs. Copies transcript messages, remapping UUIDs and preserving `parentUuid` chain. Supports `upToMessageId` for branching.

#### Internal Daemon Primitives (lines 276-443)

14. **`CronTask`** type (lines 283-289): A scheduled task from `<dir>/.claude/scheduled_tasks.json` with `id`, `cron`, `prompt`, `createdAt`, `recurring?`.

15. **`CronJitterConfig`** type (lines 298-305): Tuning knobs for cron scheduler: `recurringFrac`, `recurringCapMs`, `oneShotMaxMs`, `oneShotFloorMs`, `oneShotMinuteMod`, `recurringMaxAgeMs`.

16. **`ScheduledTaskEvent`** type (lines 311-313): Discriminated union — `{ type: 'fire', task: CronTask }` or `{ type: 'missed', tasks: CronTask[] }`.

17. **`ScheduledTasksHandle`** type (lines 319-328): Handle with `events()` async generator and `getNextFireTime()`.

18. **`watchScheduledTasks(_opts)`** (lines 350-356): Watches `<dir>/.claude/scheduled_tasks.json` and yields events as tasks fire. Acquires per-directory scheduler lock (PID-based liveness). Intended for daemon architectures.

19. **`buildMissedTaskNotification(_missed)`** (lines 363-365): Formats missed one-shot tasks into a prompt for the model.

20. **`InboundPrompt`** type (lines 371-374): User message typed on claude.ai.

21. **`ConnectRemoteControlOptions`** type (lines 380-389): Options for `connectRemoteControl`: `dir`, `name?`, `workerType?`, `branch?`, `gitRepoUrl?`, `getAccessToken`, `baseUrl`, `orgUUID`, `model`.

22. **`RemoteControlHandle`** type (lines 398-417): Handle with `sessionUrl`, `environmentId`, `bridgeSessionId`, `write(msg)`, `sendResult()`, `sendControlRequest(req)`, `sendControlResponse(res)`, `sendControlCancelRequest(requestId)`, `inboundPrompts()` generator, `controlRequests()` generator, `permissionResponses()` generator, `onStateChange(cb)`, `teardown()`.

23. **`connectRemoteControl(_opts)`** (lines 439-442): Holds a claude.ai remote-control bridge connection from a daemon process. The daemon owns the WebSocket in the parent process. Returns `null` on no-OAuth or registration failure.

### `entrypoints/sandboxTypes.ts` (156 lines)

**Zod schemas and types for sandbox configuration.** Single source of truth for sandbox types used by both the SDK and settings validation.

#### `SandboxNetworkConfigSchema` (lines 14-42)
- `allowedDomains`: array of strings (optional).
- `allowManagedDomainsOnly`: boolean (optional) — when true, only managed settings domains and allow rules are respected.
- `allowUnixSockets`: array of strings (optional) — macOS only.
- `allowAllUnixSockets`: boolean (optional).
- `allowLocalBinding`: boolean (optional).
- `httpProxyPort`: number (optional).
- `socksProxyPort`: number (optional).

#### `SandboxFilesystemConfigSchema` (lines 47-86)
- `allowWrite`: array of strings (optional) — paths to allow writing within sandbox.
- `denyWrite`: array of strings (optional) — paths to deny writing.
- `denyRead`: array of strings (optional) — paths to deny reading.
- `allowRead`: array of strings (optional) — paths to re-allow reading within denyRead regions; takes precedence.
- `allowManagedReadPathsOnly`: boolean (optional) — when true, only managed settings paths are used.

#### `SandboxSettingsSchema` (lines 91-144)
- `enabled`: boolean (optional).
- `failIfUnavailable`: boolean (optional) — exit at startup if sandbox cannot start.
- `autoAllowBashIfSandboxed`: boolean (optional).
- `allowUnsandboxedCommands`: boolean (optional) — defaults to true.
- `network`: `SandboxNetworkConfigSchema()`.
- `filesystem`: `SandboxFilesystemConfigSchema()`.
- `ignoreViolations`: record of string to array of strings (optional).
- `enableWeakerNestedSandbox`: boolean (optional).
- `enableWeakerNetworkIsolation`: boolean (optional) — macOS only, allows `com.apple.trustd.agent` access for Go-based CLI tools.
- `excludedCommands`: array of strings (optional).
- `ripgrep`: object with `command` and `args` (optional) — custom ripgrep config.
- `.passthrough()` — allows undocumented settings like `enabledPlatforms`.

#### Inferred Types (lines 147-156)
- `SandboxSettings`
- `SandboxNetworkConfig`: NonNullable of the inferred network config.
- `SandboxFilesystemConfig`: NonNullable of the inferred filesystem config.
- `SandboxIgnoreViolations`: NonNullable of `ignoreViolations`.

### `entrypoints/sdk/coreSchemas.ts` (1889 lines)

**Complete SDK Zod schemas.** This is the SDK contract — the single source of truth for all SDK data types. TypeScript types are generated from these schemas via `scripts/generate-sdk-types.ts`. Uses `lazySchema()` wrapper for all schemas to avoid circular reference issues.

#### Usage & Model Types
- **`ModelUsageSchema`**: `inputTokens`, `outputTokens`, `cacheReadInputTokens`, `cacheCreationInputTokens`, `webSearchRequests`, `costUSD`, `contextWindow`, `maxOutputTokens` — all `z.number()`.

#### Output Format Types
- **`OutputFormatTypeSchema`**: `z.literal('json_schema')`.
- **`BaseOutputFormatSchema`**: `{ type: OutputFormatTypeSchema }`.
- **`JsonSchemaOutputFormatSchema`**: `{ type: z.literal('json_schema'), schema: z.record(z.string(), z.unknown()) }`.
- **`OutputFormatSchema`**: Aliases `JsonSchemaOutputFormatSchema`.

#### Config Types
- **`ApiKeySourceSchema`**: `z.enum(['user', 'project', 'org', 'temporary', 'oauth'])`.
- **`ConfigScopeSchema`**: `z.enum(['local', 'user', 'project'])`.
- **`SdkBetaSchema`**: `z.literal('context-1m-2025-08-07')`.
- **`ThinkingConfigSchema`**: Union of `ThinkingAdaptiveSchema` (Claude decides when to think), `ThinkingEnabledSchema` (fixed token budget), `ThinkingDisabledSchema`.

#### MCP Server Config Types
- **`McpStdioServerConfigSchema`**: `{ type, command, args?, env? }`.
- **`McpSSEServerConfigSchema`**: `{ type: 'sse', url, headers? }`.
- **`McpHttpServerConfigSchema`**: `{ type: 'http', url, headers? }`.
- **`McpSdkServerConfigSchema`**: `{ type: 'sdk', name }`.
- **`McpServerConfigForProcessTransportSchema`**: Union of stdio, SSE, HTTP, SDK.
- **`McpClaudeAIProxyServerConfigSchema`**: `{ type: 'claudeai-proxy', url, id }`.
- **`McpServerStatusConfigSchema`**: Union including claudeai-proxy (output-only).
- **`McpServerStatusSchema`**: `{ name, status, serverInfo?, error?, config?, scope?, tools?, capabilities? }`. Status is `'connected' | 'failed' | 'needs-auth' | 'pending' | 'disabled'`.
- **`McpSetServersResultSchema`**: `{ added, removed, errors }`.

#### Permission Types
- **`PermissionUpdateDestinationSchema`**: `z.enum(['userSettings', 'projectSettings', 'localSettings', 'session', 'cliArg'])`.
- **`PermissionBehaviorSchema`**: `z.enum(['allow', 'deny', 'ask'])`.
- **`PermissionRuleValueSchema`**: `{ toolName, ruleContent? }`.
- **`PermissionUpdateSchema`**: Discriminated union on `type` — `addRules`, `replaceRules`, `removeRules`, `setMode`, `addDirectories`, `removeDirectories`.
- **`PermissionDecisionClassificationSchema`**: `z.enum(['user_temporary', 'user_permanent', 'user_reject'])`.
- **`PermissionResultSchema`**: Union of `{ behavior: 'allow', updatedInput?, updatedPermissions?, toolUseID?, decisionClassification? }` and `{ behavior: 'deny', message, interrupt?, toolUseID?, decisionClassification? }`.
- **`PermissionModeSchema`**: `z.enum(['default', 'acceptEdits', 'bypassPermissions', 'plan', 'dontAsk'])`.

#### Hook Types (355-797)
- **`HOOK_EVENTS`** const array: 27 hook events including `PreToolUse`, `PostToolUse`, `PostToolUseFailure`, `Notification`, `UserPromptSubmit`, `SessionStart`, `SessionEnd`, `Stop`, `StopFailure`, `SubagentStart`, `SubagentStop`, `PreCompact`, `PostCompact`, `PermissionRequest`, `PermissionDenied`, `Setup`, `TeammateIdle`, `TaskCreated`, `TaskCompleted`, `Elicitation`, `ElicitationResult`, `ConfigChange`, `WorktreeCreate`, `WorktreeRemove`, `InstructionsLoaded`, `CwdChanged`, `FileChanged`.
- **`BaseHookInputSchema`**: `{ session_id, transcript_path, cwd, permission_mode?, agent_id?, agent_type? }`.
- Individual hook input schemas for each event (e.g., `PreToolUseHookInputSchema`, `PostToolUseHookInputSchema`, etc.), each using `BaseHookInputSchema().and(...)` pattern.
- **`HookInputSchema`**: Union of all 27 hook input schemas.
- **`AsyncHookJSONOutputSchema`**: `{ async: true, asyncTimeout? }`.
- Individual hook output schemas for specific events (`PreToolUseHookSpecificOutputSchema`, `UserPromptSubmitHookSpecificOutputSchema`, `SessionStartHookSpecificOutputSchema`, etc.).
- **`SyncHookJSONOutputSchema`**: `{ continue?, suppressOutput?, stopReason?, decision?, systemMessage?, reason?, hookSpecificOutput? }`.
- **`HookJSONOutputSchema`**: Union of `AsyncHookJSONOutputSchema` and `SyncHookJSONOutputSchema`.

#### Prompt Request Types
- **`PromptRequestOptionSchema`**: `{ key, label, description? }`.
- **`PromptRequestSchema`**: `{ prompt, message, options }`.
- **`PromptResponseSchema`**: `{ prompt_response, selected }`.

#### Skill/Command Types (1016-1079)
- **`SlashCommandSchema`**: `{ name, description, argumentHint }`.
- **`AgentInfoSchema`**: `{ name, description, model? }`.
- **`ModelInfoSchema`**: `{ value, displayName, description, supportsEffort?, supportedEffortLevels?, supportsAdaptiveThinking?, supportsFastMode?, supportsAutoMode? }`.
- **`AccountInfoSchema`**: `{ email?, organization?, subscriptionType?, tokenSource?, apiKeySource?, apiProvider? }`.

#### Agent Definition Types (1103-1183)
- **`AgentMcpServerSpecSchema`**: Union of string or record of MCP server configs.
- **`AgentDefinitionSchema`**: `{ description, tools?, disallowedTools?, prompt, model?, mcpServers?, criticalSystemReminder_EXPERIMENTAL?, skills?, initialPrompt?, maxTurns?, background?, memory?, effort?, permissionMode? }`.

#### Settings Types (1189-1211)
- **`SettingSourceSchema`**: `z.enum(['user', 'project', 'local'])`.
- **`SdkPluginConfigSchema`**: `{ type: 'local', path }`.

#### Rewind Types (1217-1227)
- **`RewindFilesResultSchema`**: `{ canRewind, error?, filesChanged?, insertions?, deletions? }`.

#### External Type Placeholders (1232-1251)
- `APIUserMessagePlaceholder`, `APIAssistantMessagePlaceholder`, `RawMessageStreamEventPlaceholder`, `UUIDPlaceholder` (`z.string()`), `NonNullableUsagePlaceholder` — placeholders for external types; generation script uses `TypeOverrideMap` for correct TS type references.

#### SDK Message Types (1256-1880)
- **`SDKAssistantMessageErrorSchema`**: `'authentication_failed' | 'billing_error' | 'rate_limit' | 'invalid_request' | 'server_error' | 'unknown' | 'max_output_tokens'`.
- **`SDKStatusSchema`**: `z.union([z.literal('compacting'), z.null()])`.
- **`SDKUserMessageContentSchema`**: `{ type: 'user', message, parent_tool_use_id, isSynthetic?, tool_use_result?, priority?, timestamp? }`.
- **`SDKUserMessageSchema`**: Content + `{ uuid?, session_id? }`.
- **`SDKUserMessageReplaySchema`**: Content + `{ uuid, session_id, isReplay: true }`.
- **`SDKRateLimitInfoSchema`**: Complex rate limit info with nested overage statuses and disabled reasons.
- **`SDKAssistantMessageSchema`**: `{ type: 'assistant', message, parent_tool_use_id, error?, uuid, session_id }`.
- **`SDKRateLimitEventSchema`**: `{ type: 'rate_limit_event', rate_limit_info, uuid, session_id }`.
- **`SDKStreamlinedTextMessageSchema`**: `@internal` — preserves text from assistant messages, removes thinking and tool_use blocks.
- **`SDKStreamlinedToolUseSummaryMessageSchema`**: `@internal` — cumulative summary string replacing tool_use blocks.
- **`SDKResultSuccessSchema`**: `{ type: 'result', subtype: 'success', duration_ms, duration_api_ms, is_error, num_turns, result, stop_reason, total_cost_usd, usage, modelUsage, permission_denials, structured_output?, fast_mode_state?, uuid, session_id }`.
- **`SDKResultErrorSchema`**: Like success but with `subtype` as error variant (`error_during_execution` | `error_max_turns` | `error_max_budget_usd` | `error_max_structured_output_retries`) and `errors` array.
- **`SDKResultMessageSchema`**: Union of success and error results.
- **`SDKSystemMessageSchema`**: `{ type: 'system', subtype: 'init', agents?, apiKeySource, betas?, claude_code_version, cwd, tools, mcp_servers, model, permissionMode, slash_commands, output_style, skills, plugins, fast_mode_state?, uuid, session_id }`.
- **`SDKPartialAssistantMessageSchema`**: `{ type: 'stream_event', event, parent_tool_use_id, uuid, session_id }`.
- **`SDKCompactBoundaryMessageSchema`**: `{ type: 'system', subtype: 'compact_boundary', compact_metadata, uuid, session_id }`.
- **`SDKStatusMessageSchema`**: `{ type: 'system', subtype: 'status', status, permissionMode?, uuid, session_id }`.
- **`SDKPostTurnSummaryMessageSchema`**: `@internal` — `{ type: 'system', subtype: 'post_turn_summary', summarizes_uuid, status_category, status_detail, is_noteworthy, title, description, recent_action, needs_action, artifact_urls, uuid, session_id }`.
- **`SDKAPIRetryMessageSchema`**: `{ type: 'system', subtype: 'api_retry', attempt, max_retries, retry_delay_ms, error_status, error, uuid, session_id }`.
- **`SDKLocalCommandOutputMessageSchema`**: `{ type: 'system', subtype: 'local_command_output', content, uuid, session_id }`.
- **`SDKHookStartedMessageSchema`**: `{ type: 'system', subtype: 'hook_started', hook_id, hook_name, hook_event, uuid, session_id }`.
- **`SDKHookProgressMessageSchema`**: `{ type: 'system', subtype: 'hook_progress', hook_id, hook_name, hook_event, stdout, stderr, output, uuid, session_id }`.
- **`SDKHookResponseMessageSchema`**: `{ type: 'system', subtype: 'hook_response', hook_id, hook_name, hook_event, output, stdout, stderr, exit_code?, outcome, uuid, session_id }`.
- **`SDKToolProgressMessageSchema`**: `{ type: 'tool_progress', tool_use_id, tool_name, parent_tool_use_id, elapsed_time_seconds, task_id?, uuid, session_id }`.
- **`SDKAuthStatusMessageSchema`**: `{ type: 'auth_status', isAuthenticating, output, error?, uuid, session_id }`.
- **`SDKFilesPersistedEventSchema`**: `{ type: 'system', subtype: 'files_persisted', files, failed, processed_at, uuid, session_id }`.
- **`SDKTaskNotificationMessageSchema`**: `{ type: 'system', subtype: 'task_notification', task_id, tool_use_id?, status, output_file, summary, usage?, uuid, session_id }`.
- **`SDKTaskStartedMessageSchema`**: `{ type: 'system', subtype: 'task_started', task_id, tool_use_id?, description, task_type?, workflow_name?, prompt?, uuid, session_id }`.
- **`SDKSessionStateChangedMessageSchema`**: `{ type: 'system', subtype: 'session_state_changed', state: 'idle' | 'running' | 'requires_action', uuid, session_id }`.
- **`SDKTaskProgressMessageSchema`**: `{ type: 'system', subtype: 'task_progress', task_id, tool_use_id?, description, usage, last_tool_name?, summary?, uuid, session_id }`.
- **`SDKToolUseSummaryMessageSchema`**: `{ type: 'tool_use_summary', summary, preceding_tool_use_ids, uuid, session_id }`.
- **`SDKElicitationCompleteMessageSchema`**: `{ type: 'system', subtype: 'elicitation_complete', mcp_server_name, elicitation_id, uuid, session_id }`.
- **`SDKPromptSuggestionMessageSchema`**: `@internal` — `{ type: 'prompt_suggestion', suggestion, uuid, session_id }`.

#### Session Listing Types (1808-1852)
- **`SDKSessionInfoSchema`**: `{ sessionId, summary, lastModified, fileSize?, customTitle?, firstPrompt?, gitBranch?, cwd?, tag?, createdAt? }`.

#### Aggregate Message Schema (1854-1881)
- **`SDKMessageSchema`**: Union of all 24 message schemas.
- **`FastModeStateSchema`**: `z.enum(['off', 'cooldown', 'on'])`.

### `entrypoints/sdk/coreTypes.ts` (62 lines)

**Re-exports generated SDK types and const arrays.**

- Re-exports sandbox types from `sandboxTypes.js`.
- Re-exports all generated types from `coreTypes.generated.js`.
- Re-exports `NonNullableUsage` from `sdkUtilityTypes.js`.
- **`HOOK_EVENTS`** const array: Same 27 events as `coreSchemas.ts` — `as const` for literal types.
- **`EXIT_REASONS`** const array: `'clear'`, `'resume'`, `'logout'`, `'prompt_input_exit'`, `'other'`, `'bypass_permissions_disabled'`.

### `entrypoints/sdk/controlSchemas.ts` (663 lines)

**Control protocol Zod schemas** for the SDK control channel. Used by SDK builders to communicate with the CLI process.

#### Hook Callback Types
- **`SDKHookCallbackMatcherSchema`**: `{ matcher?, hookCallbackIds, timeout? }`.

#### Control Request Types

1. **`SDKControlInitializeRequestSchema`** (lines 57-75): `{ subtype: 'initialize', hooks?, sdkMcpServers?, jsonSchema?, systemPrompt?, appendSystemPrompt?, agents?, promptSuggestions?, agentProgressSummaries? }`.

2. **`SDKControlInitializeResponseSchema`** (lines 77-95): `{ commands, agents, output_style, available_output_styles, models, account, pid? }`.

3. **`SDKControlInterruptRequestSchema`** (line 97-103): `{ subtype: 'interrupt' }`.

4. **`SDKControlPermissionRequestSchema`** (lines 106-122): `{ subtype: 'can_use_tool', tool_name, input, permission_suggestions?, blocked_path?, decision_reason?, title?, display_name?, tool_use_id, agent_id?, description? }`.

5. **`SDKControlSetPermissionModeRequestSchema`** (lines 124-135): `{ subtype: 'set_permission_mode', mode, ultraplan? }`.

6. **`SDKControlSetModelRequestSchema`** (lines 137-143): `{ subtype: 'set_model', model? }`.

7. **`SDKControlSetMaxThinkingTokensRequestSchema`** (lines 146-155): `{ subtype: 'set_max_thinking_tokens', max_thinking_tokens }`.

8. **`SDKControlMcpStatusRequestSchema`** (lines 157-163): `{ subtype: 'mcp_status' }`.

9. **`SDKControlMcpStatusResponseSchema`** (lines 165-173): `{ mcpServers }`.

10. **`SDKControlGetContextUsageRequestSchema`** (lines 175-183): `{ subtype: 'get_context_usage' }`.

11. **`SDKControlGetContextUsageResponseSchema`** (lines 205-306): Complex response with `categories` (ContextCategory with `name`, `tokens`, `color`, `isDeferred?`), `totalTokens`, `maxTokens`, `rawMaxTokens`, `percentage`, `gridRows` (ContextGridSquare with `color`, `isFilled`, `categoryName`, `tokens`, `percentage`, `squareFullness`), `model`, `memoryFiles`, `mcpTools`, `deferredBuiltinTools?`, `systemTools?`, `systemPromptSections?`, `agents`, `slashCommands?`, `skills?`, `autoCompactThreshold?`, `isAutoCompactEnabled`, `messageBreakdown?`, `apiUsage?`.

12. **`SDKControlRewindFilesRequestSchema`** (lines 308-316): `{ subtype: 'rewind_files', user_message_id, dry_run? }`.

13. **`SDKControlRewindFilesResponseSchema`** (lines 318-328): `{ canRewind, error?, filesChanged?, insertions?, deletions? }`.

14. **`SDKControlCancelAsyncMessageRequestSchema`** (lines 330-339): `{ subtype: 'cancel_async_message', message_uuid }`.

15. **`SDKControlCancelAsyncMessageResponseSchema`** (lines 341-349): `{ cancelled }`.

16. **`SDKControlSeedReadStateRequestSchema`** (lines 351-361): `{ subtype: 'seed_read_state', path, mtime }`.

17. **`SDKHookCallbackRequestSchema`** (lines 363-372): `{ subtype: 'hook_callback', callback_id, input, tool_use_id? }`.

18. **`SDKControlMcpMessageRequestSchema`** (lines 374-382): `{ subtype: 'mcp_message', server_name, message }`.

19. **`SDKControlMcpSetServersRequestSchema`** (lines 384-391): `{ subtype: 'mcp_set_servers', servers }`.

20. **`SDKControlMcpSetServersResponseSchema`** (lines 393-403): `{ added, removed, errors }`.

21. **`SDKControlReloadPluginsRequestSchema`** (lines 405-413): `{ subtype: 'reload_plugins' }`.

22. **`SDKControlReloadPluginsResponseSchema`** (lines 415-433): `{ commands, agents, plugins, mcpServers, error_count }`.

23. **`SDKControlMcpReconnectRequestSchema`** (lines 435-442): `{ subtype: 'mcp_reconnect', serverName }`.

24. **`SDKControlMcpToggleRequestSchema`** (lines 444-452): `{ subtype: 'mcp_toggle', serverName, enabled }`.

25. **`SDKControlStopTaskRequestSchema`** (lines 455-462): `{ subtype: 'stop_task', task_id }`.

26. **`SDKControlApplyFlagSettingsRequestSchema`** (lines 464-473): `{ subtype: 'apply_flag_settings', settings }`.

27. **`SDKControlGetSettingsRequestSchema`** (lines 475-483): `{ subtype: 'get_settings' }`.

28. **`SDKControlGetSettingsResponseSchema`** (lines 485-520): `{ effective, sources (ordered low-to-high), applied? (runtime-resolved values) }`.

29. **`SDKControlElicitationRequestSchema`** (lines 522-536): `{ subtype: 'elicitation', mcp_server_name, message, mode?, url?, elicitation_id?, requested_schema? }`.

30. **`SDKControlElicitationResponseSchema`** (lines 538-545): `{ action, content? }`.

#### Control Request/Response Wrappers (548-610)
- **`SDKControlRequestInnerSchema`**: Union of all 21 request schemas.
- **`SDKControlRequestSchema`**: `{ type: 'control_request', request_id, request }`.
- **`ControlResponseSchema`**: `{ subtype: 'success', request_id, response? }`.
- **`ControlErrorResponseSchema`**: `{ subtype: 'error', request_id, error, pending_permission_requests? }`.
- **`SDKControlResponseSchema`**: `{ type: 'control_response', response }`.
- **`SDKControlCancelRequestSchema`**: `{ type: 'control_cancel_request', request_id }`.
- **`SDKKeepAliveMessageSchema`**: `{ type: 'keep_alive' }`.
- **`SDKUpdateEnvironmentVariablesMessageSchema`**: `{ type: 'update_environment_variables', variables }`.

#### Aggregate Message Types (638-663)
- **`StdoutMessageSchema`**: Union of `SDKMessageSchema`, streamlined messages, post-turn summary, control responses/requests, cancel requests, keep-alive.
- **`StdinMessageSchema`**: Union of `SDKUserMessageSchema`, control requests/responses, keep-alive, environment variable updates.

---

## BOOTSTRAP

### `bootstrap/state.ts` (1758 lines)

**Global mutable STATE singleton.** Every field has explicit getter/setter accessor functions. This is the shared mutable state backbone — all modules read from and write to this module.

#### The `State` Type (lines 45-257)

Comprehensive state covering:

- **CWD & path**: `originalCwd`, `projectRoot`, `cwd`, `directConnectServerUrl`, `sessionProjectDir`.
- **Costs & durations**: `totalCostUSD`, `totalAPIDuration`, `totalAPIDurationWithoutRetries`, `totalToolDuration`, `startTime`, `totalLinesAdded`, `totalLinesRemoved`.
- **Turn-level trackers**: `turnHookDurationMs`, `turnToolDurationMs`, `turnClassifierDurationMs`, `turnToolCount`, `turnHookCount`, `turnClassifierCount`.
- **Model**: `modelUsage` (per-model map), `mainLoopModelOverride`, `initialMainLoopModel`, `modelStrings`, `lastAPIRequest`, `lastAPIRequestMessages`, `lastClassifierRequests`, `lastMainRequestId`, `lastApiCompletionTimestamp`, `pendingPostCompaction`.
- **Session identity**: `sessionId`, `parentSessionId`, `isInteractive`, `clientType`, `sessionSource`, `questionPreviewFormat`, `isRemoteMode`.
- **Auth & tokens**: `sessionIngressToken`, `oauthTokenFromFd`, `apiKeyFromFd`.
- **Telemetry**: `meter`, `sessionCounter`, `locCounter`, `prCounter`, `commitCounter`, `costCounter`, `tokenCounter`, `codeEditToolDecisionCounter`, `activeTimeCounter`, `statsStore`, `loggerProvider`, `eventLogger`, `meterProvider`, `tracerProvider`.
- **Agent colors**: `agentColorMap` (Map), `agentColorIndex`.
- **System prompt cache**: `systemPromptSectionCache` (Map), `lastEmittedDate`.
- **Beta header latches**: `afkModeHeaderLatched`, `fastModeHeaderLatched`, `cacheEditingHeaderLatched`, `thinkingClearLatched` — sticky-on latches for prompt cache optimization.
- **Session flags**: `sessionBypassPermissionsMode`, `scheduledTasksEnabled`, `sessionCronTasks`, `sessionCreatedTeams` (Set), `sessionTrustAccepted`, `sessionPersistenceDisabled`.
- **Plan mode**: `hasExitedPlanMode`, `needsPlanModeExitAttachment`, `needsAutoModeExitAttachment`.
- **LSP recommendation**: `lspRecommendationShownThisSession`.
- **SDK init**: `initJsonSchema`, `registeredHooks`, `sdkBetas`, `sdkAgentProgressSummariesEnabled`.
- **Plugins**: `inlinePlugins`, `useCoworkPlugins`.
- **Chrome**: `chromeFlagOverride`.
- **Settings**: `flagSettingsPath`, `flagSettingsInline`, `allowedSettingSources`.
- **Agent**: `mainThreadAgentType`, `kairosActive`, `strictToolResultPairing`, `userMsgOptIn`.
- **Worktrees**: `additionalDirectoriesForClaudeMd`.
- **Channels**: `allowedChannels` (ChannelEntry[]), `hasDevChannels`.
- **Prompt cache**: `promptCache1hAllowlist`, `promptCache1hEligible`.
- **Teleported session**: `teleportedSessionInfo`.
- **Invoked skills**: `invokedSkills` (Map) — keyed by `${agentId}:${skillName}`.
- **Slow operations**: `slowOperations` — dev bar display, ant-only, max 10 entries, 10s TTL.
- **Other**: `lastInteractionTime`, `hasUnknownModelCost`, `inMemoryErrorLog` (max 100), `planSlugCache`, `cachedClaudeMdContent`.

#### Key Functions

**Session management**: `getSessionId()`, `regenerateSessionId({ setCurrentAsParent? })`, `getParentSessionId()`, `switchSession(sessionId, projectDir?)`, `onSessionSwitch` (signal), `getSessionProjectDir()`.

**Path**: `getOriginalCwd()`, `getProjectRoot()`, `setOriginalCwd(cwd)`, `setProjectRoot(cwd)`, `getCwdState()`, `setCwdState(cwd)`.

**Duration/cost**: `addToTotalDurationState(duration, durationWithoutRetries)`, `resetTotalDurationStateAndCost_FOR_TESTS_ONLY()`, `addToTotalCostState(cost, modelUsage, model)`, `getTotalCostUSD()`, `getTotalAPIDuration()`, `getTotalDuration()`, `getTotalAPIDurationWithoutRetries()`, `getTotalToolDuration()`, `addToToolDuration(duration)`.

**Turn hooks/classifiers**: `getTurnHookDurationMs()`, `addToTurnHookDuration(duration)`, `resetTurnHookDuration()`, `getTurnHookCount()`, `getTurnToolDurationMs()`, `resetTurnToolDuration()`, `getTurnToolCount()`, `getTurnClassifierDurationMs()`, `addToTurnClassifierDuration(duration)`, `resetTurnClassifierDuration()`, `getTurnClassifierCount()`.

**Token tracking per-turn**: `getTurnOutputTokens()`, `getCurrentTurnTokenBudget()`, `snapshotOutputTokensForTurn(budget)`, `getBudgetContinuationCount()`, `incrementBudgetContinuationCount()`.

**Lines**: `addToTotalLinesChanged(added, removed)`, `getTotalLinesAdded()`, `getTotalLinesRemoved()`.

**Token aggregation** (all across all models): `getTotalInputTokens()`, `getTotalOutputTokens()`, `getTotalCacheReadInputTokens()`, `getTotalCacheCreationInputTokens()`, `getTotalWebSearchRequests()`.

**Interaction time**: `updateLastInteractionTime(immediate?)` — deferred by default (batched via `flushInteractionTime()` called by Ink before each render), immediate option for useEffect callbacks. Uses a `interactionTimeDirty` flag pattern.

**Scroll drain suspension**: `markScrollActivity()`, `getIsScrollDraining()`, `waitForScrollIdle()` — prevents background intervals from competing with scroll frames. Uses 150ms debounce timer.

**Model**: `getModelUsage()`, `getUsageForModel(model)`, `getMainLoopModelOverride()`, `setMainLoopModelOverride(model)`, `getInitialMainLoopModel()`, `setInitialMainLoopModel(model)`, `getSdkBetas()`, `setSdkBetas(betas)`.

**Cost reset**: `resetCostState()`, `setCostStateForRestore(...)` — restores per-model usage, adjusts startTime for wall duration accumulation.

**Model strings**: `getModelStrings()`, `setModelStrings(modelStrings)`, `resetModelStringsForTestingOnly()`.

**Telemetry**: `setMeter(meter, createCounter)` — initializes all 9 counters. Individual getters: `getMeter()`, `getSessionCounter()`, `getLocCounter()`, `getPrCounter()`, `getCommitCounter()`, `getCostCounter()`, `getTokenCounter()`, `getCodeEditToolDecisionCounter()`, `getActiveTimeCounter()`.

**Logger provider**: `getLoggerProvider()`, `setLoggerProvider(provider)`, `getEventLogger()`, `setEventLogger(logger)`, `getMeterProvider()`, `setMeterProvider(provider)`, `getTracerProvider()`, `setTracerProvider(provider)`.

**Interactive**: `getIsNonInteractiveSession()`, `getIsInteractive()`, `setIsInteractive(value)`.

**Client type**: `getClientType()`, `setClientType(type)`.

**SDK agent progress summaries**: `getSdkAgentProgressSummariesEnabled()`, `setSdkAgentProgressSummariesEnabled(value)`.

**Kairos/proactive**: `getKairosActive()`, `setKairosActive(value)`, `getStrictToolResultPairing()`, `setStrictToolResultPairing(value)`, `getUserMsgOptIn()`, `setUserMsgOptIn(value)`.

**Session source/format**: `getSessionSource()`, `setSessionSource(source)`, `getQuestionPreviewFormat()`, `setQuestionPreviewFormat(format)`.

**Agent colors**: `getAgentColorMap()`.

**Flag settings**: `getFlagSettingsPath()`, `setFlagSettingsPath(path)`, `getFlagSettingsInline()`, `setFlagSettingsInline(settings)`.

**Auth tokens**: `getSessionIngressToken()`, `setSessionIngressToken(token)`, `getOauthTokenFromFd()`, `setOauthTokenFromFd(token)`, `getApiKeyFromFd()`, `setApiKeyFromFd(key)`.

**API request tracking**: `setLastAPIRequest(params)`, `getLastAPIRequest()`, `setLastAPIRequestMessages(messages)`, `getLastAPIRequestMessages()`, `setLastClassifierRequests(requests)`, `getLastClassifierRequests()`.

**Claude.md cache**: `setCachedClaudeMdContent(content)`, `getCachedClaudeMdContent()`.

**Error log**: `addToInMemoryErrorLog(errorInfo)` — max 100, FIFO eviction.

**Settings sources**: `getAllowedSettingSources()`, `setAllowedSettingSources(sources)`.

**3P auth**: `preferThirdPartyAuthentication()` — returns true for non-interactive sessions unless clientType is `claude-vscode`.

**Plugins**: `setInlinePlugins(plugins)`, `getInlinePlugins()`, `setUseCoworkPlugins(value)`, `getUseCoworkPlugins()`.

**Chrome**: `setChromeFlagOverride(value)`, `getChromeFlagOverride()`.

**Permissions**: `setSessionBypassPermissionsMode(enabled)`, `getSessionBypassPermissionsMode()`.

**Scheduled tasks**: `setScheduledTasksEnabled(enabled)`, `getScheduledTasksEnabled()`, `getSessionCronTasks()`, `addSessionCronTask(task)`, `removeSessionCronTasks(ids)`. `SessionCronTask` type includes `agentId?` for routing to specific teammate queues.

**Trust**: `setSessionTrustAccepted(accepted)`, `getSessionTrustAccepted()`.

**Session persistence**: `setSessionPersistenceDisabled(disabled)`, `isSessionPersistenceDisabled()`.

**Plan mode**: `hasExitedPlanModeInSession()`, `setHasExitedPlanMode(value)`, `needsPlanModeExitAttachment()`, `setNeedsPlanModeExitAttachment(value)`, `handlePlanModeTransition(fromMode, toMode)`.

**Auto mode**: `needsAutoModeExitAttachment()`, `setNeedsAutoModeExitAttachment(value)`, `handleAutoModeTransition(fromMode, toMode)` — skips auto↔plan transitions.

**LSP**: `hasShownLspRecommendationThisSession()`, `setLspRecommendationThisSession(value)`.

**SDK init state**: `setInitJsonSchema(schema)`, `getInitJsonSchema()`, `registerHookCallbacks(hooks)`, `getRegisteredHooks()`, `clearRegisteredHooks()`, `clearRegisteredPluginHooks()`, `resetSdkInitState()`.

**Plan slugs**: `getPlanSlugCache()`.

**Session teams**: `getSessionCreatedTeams()`.

**Teleported session**: `setTeleportedSessionInfo(info)`, `getTeleportedSessionInfo()`, `markFirstTeleportMessageLogged()`.

**Invoked skills**: `addInvokedSkill(skillName, skillPath, content, agentId?)`, `getInvokedSkills()`, `getInvokedSkillsForAgent(agentId)`, `clearInvokedSkills(preservedAgentIds?)`, `clearInvokedSkillsForAgent(agentId)`.

**Slow operations**: `addSlowOperation(operation, durationMs)` — ant-only, skips editor sessions, max 10, 10s TTL. `getSlowOperations()` returns stable reference when empty.

**Agent thread type**: `getMainThreadAgentType()`, `setMainThreadAgentType(agentType)`.

**Remote mode**: `getIsRemoteMode()`, `setIsRemoteMode(value)`.

**System prompt cache**: `getSystemPromptSectionCache()`, `setSystemPromptSectionCacheEntry(name, value)`, `clearSystemPromptSectionState()`.

**Last emitted date**: `getLastEmittedDate()`, `setLastEmittedDate(date)`.

**Additional directories**: `getAdditionalDirectoriesForClaudeMd()`, `setAdditionalDirectoriesForClaudeMd(directories)`.

**Channels**: `getAllowedChannels()`, `setAllowedChannels(entries)`, `getHasDevChannels()`, `setHasDevChannels(value)`.

**Prompt cache**: `getPromptCache1hAllowlist()`, `setPromptCache1hAllowlist(allowlist)`, `getPromptCache1hEligible()`, `setPromptCache1hEligible(eligible)`.

**Beta header latches**: Individual getter/setter pairs for `afkModeHeaderLatched`, `fastModeHeaderLatched`, `cacheEditingHeaderLatched`, `thinkingClearLatched`. `clearBetaHeaderLatches()` resets all four to null.

**Prompt ID**: `getPromptId()`, `setPromptId(id)`.

**Test reset**: `resetStateForTests()` — only in `NODE_ENV === 'test'`, resets state via spreading `getInitialState()` values, resets turn-level globals, clears `sessionSwitched` signal.

---

## CLI LAYER (18 files)

### `cli/print.ts` (5594 lines)

**Core print/output handler for SDK/headless mode.** The largest CLI file. Formats messages, handles stream events, permission prompts. Contains the `runHeadless` and `runHeadlessStreaming` functions — the main execution loop for `-p`/`--print` mode.

#### Module-level state
- **Received message UUID tracking**: `receivedMessageUuids` (Set) and `receivedMessageUuidsOrder` (array), max 10,000 entries, used by `trackReceivedMessageUuid(uuid)` to detect duplicates (returns false for duplicates).

#### Utility Functions (417-453)
- **`toBlocks(v)`**: Converts `PromptValue` (string or ContentBlockParam[]) to `ContentBlockParam[]`.
- **`joinPromptValues(values)`**: Joins queued commands — strings join with `'\n'`, block arrays concatenate.
- **`canBatchWith(head, next)`**: Checks if `next` can batch into `head`'s `ask()` call. Only prompt-mode commands with matching workload tag and isMeta flag.

#### `runHeadless()` (lines 455-974)

The main entry for headless/print mode. Takes `inputPrompt`, `getAppState`, `setAppState`, commands, tools, SDK MCP configs, agents, and options.

**Initial setup**:
1. Handles `CLAUDE_CODE_EXIT_AFTER_FIRST_RENDER` (ant-only) — prints startup time and exits.
2. Downloads user settings (if `DOWNLOAD_USER_SETTINGS` feature gate and remote).
3. Subscribes to settings changes to apply managed settings and fast mode sync.
4. Activates proactive mode if `CLAUDE_CODE_PROACTIVE` env and not already active.
5. Starts periodic Bun.gc() (every 1s) if Bun runtime.
6. Starts headless profiler, checks Grove requirements, initializes GrowthBook.
7. Validates flag combinations (`--resume-session-at` requires `--resume`, `--rewind-files` requires `--resume`).
8. Creates `StructuredIO` via `getStructuredIO(inputPrompt, options)`.
9. Installs `stream-json` stdout guard if output format is `stream-json`.
10. Handles sandbox unavailability — logs reason, exits if `failIfUnavailable`, warns otherwise. Initializes sandbox with network permission callback.
11. Registers hook event handler for verbose stream-json mode (emits hook lifecycle events).
12. Runs setup hooks if `setupTrigger` is set.

**Message loading** (line 680-706):
- Calls `loadInitialMessages` with continue/teleport/resume/forkSession options.
- If SessionStart hooks emit an `initialUserMessage`, prepends it via `structuredIO.prependUserMessage`.
- Restores agent setting from resumed session if no `--agent` flag or settings override.

**`--rewind-files` handling** (lines 737-771): Validates target is a user message, calls `handleRewindFiles`, prints result, exits.

**Input validation** (lines 774-793): Requires input via stdin or prompt argument. Validates stream-json requires verbose.

**Tool setup** (lines 796-832):
- Filters MCP tools by deny rules.
- Constructs `canUseTool` function via `getCanUseToolFn()`.
- Removes permission prompt tool from available tools.
- Registers process output error handlers.

**Model strings** (line 841): Awaits `ensureModelStringsInitialized()` (waits for Bedrock profile fetch for correct region strings).

**Streamlined mode** (lines 856-861): Feature-gated transformer for `CLAUDE_CODE_STREAMLINED_OUTPUT`.

**Main streaming loop** (lines 863-915):
- Iterates over `runHeadlessStreaming()` async generator.
- Transforms messages if streamlined mode is active.
- Writes messages to structuredIO in stream-json verbose mode.
- Accumulates last message (excluding system events, control messages, stream events).
- Outputs final result based on format: json (verbose=full array, else last message), stream-json (already streamed), text (default).

**Cleanup** (lines 959-973):
- Logs headless profiler turn metrics.
- Drains pending memory extraction if `EXTRACT_MEMORIES` feature gate and extract mode active.
- Calls `gracefulShutdownSync(exitCode)`.

#### `runHeadlessStreaming()` (lines 976-2680+)

Returns `AsyncIterable<StdoutMessage>`. Manages the command queue and background agent lifecycle.

**State variables** (lines 1010-1022):
- `running`: mutex flag to prevent re-entrant execution.
- `runPhase`: tracks current phase for diagnostics.
- `inputClosed`: set when stdin stream ends.
- `shutdownPromptInjected`: prevents duplicate shutdown prompt.
- `heldBackResult`: holds results while background agents are active.
- `abortController`: current turn's abort controller.
- `output`: references `structuredIO.outbound` stream.

**SIGINT handler** (lines 1027-1034): Aborts in-flight query, calls gracefulShutdown.

**Cleanup registration** (lines 1038-1050): Logs run state at SIGTERM for healthsweep diagnostics.

**Permission mode listener** (lines 1060-1079): Emits status messages on mode changes (default/acceptEdits/bypassPermissions/plan/auto/dontAsk).

**Prompt suggestion tracking** (lines 1082-1108): Tracks inflight suggestion generation with abort controller and pending last-emitted entry.

**AWS auth status listener** (lines 1111-1124): Optionally subscribes to AWS auth status changes.

**Rate limit listener** (lines 1129-1140): Emits SDKRateLimitEvent for all status changes.

**Mutable messages** (line 1145): Shared mutable array used by `ask()`.

**Read file state cache** (lines 1151-1167): Seeded from transcript, merged with client-supplied seeds.

**Auto-resume interrupted turns** (lines 1171-1192): Re-enqueues interrupted messages if `CLAUDE_CODE_RESUME_INTERRUPTED_TURN` is set.

**Model options** (lines 1194-1219): Builds ModelInfo[] from model options, including effort/adaptiveThinking/fastMode/autoMode capabilities.

**Model switch breadcrumbs** (lines 1222-1247): Injects breadcrumb messages on model switches.

**SDK MCP management**: `updateSdkMcp()` (line 1389) manages SDK MCP clients — connects new, cleans up removed, retries failed.

**Elicitation handlers** (lines 1263-1387): Registers per-connection elicitation request/completion handlers.

**Dynamic MCP state** (lines 1463-1469): Separate from SDK MCP with full transport support.

**`buildAllTools()`** (lines 1474-1500): Assembles all tools (builtin, SDK, dynamic, MCP, synthetic output).

**Bridge handle** (lines 1505-1531): Optional remote-control bridge for forwarding messages to claude.ai.

**`applyMcpServerChanges()`** (lines 1548-1608): Serialized MCP server change application with closure state mutation.

**`buildMcpServerStatuses()`** (lines 1612-1701): Builds McpServerStatus array for control responses.

**`installPluginsAndApplyMcpInBackground()`** (lines 1704-1729): Downloads user/managed settings, installs plugins, applies MCP diff.

**`refreshPluginState()`** (lines 1760-1785): Clears plugin caches, reloads commands/agents/hooks, preserves SDK-injected agents.

**`applyPluginMcpDiff()`** (lines 1792-1821): Re-diffs MCP configs after plugin changes.

**Skill change hot-reload** (lines 1824-1829): Subscribes to skill change detector, reloads commands on change.

**Proactive tick** (lines 1835-1856): Feature-gated periodic tick injection for autonomous model looping.

**`run()` function** (lines 1865-2699): The main execution loop:
1. Acquires mutex, notifies 'running', stops idle timeout.
2. Updates SDK MCP servers.
3. Resolves deferred plugin installation (with optional timeout).
4. Refreshes plugin state if plugins were installed.
5. Sets up plugin hook hot-reload.
6. **Command drain loop** (`drainCommandQueue`):
   - Dequeues commands with `isMainThread` filter.
   - Validates command mode (only prompt/orphaned-permission/task-notification).
   - Batches consecutive prompt-mode commands with matching workload.
   - Emits replay messages for non-head batch commands.
   - Combines all MCP clients, registers elicitation + channel handlers.
   - Builds all tools.
   - Calls `ask()` with full context.
   - Holds back result while background agents are running.
   - Forwards messages to bridge.
   - Generates prompt suggestions for SDK consumers.
7. **do-while loop**: Re-drains if background agents produce new tasks.
8. **Shutdown sequence**: Flushes heldBackResult + pending suggestion, flushes internal events, notifies 'idle', drains SDK events.
9. **Teammate poll loop**: Polls for teammate messages when team lead has active teammates, processes shutdown approvals, injects shutdown prompt when input closes.
10. **Idle timeout** management to track idle session time.

### `cli/structuredIO.ts` (859 lines)

**Structured I/O protocol implementation** for the SDK control channel. Handles bidirectional NDJSON communication between the CLI process and SDK consumers.

#### `StructuredIO` Class

**Constructor** (lines 164-170):
- Takes `input` (AsyncIterable<string>) and `replayUserMessages` flag.
- Creates `outbound` Stream<StdoutMessage> for enqueuing.
- Initializes `structuredInput` via `this.read()` generator.

**State**:
- `pendingRequests`: Map of requestId to PendingRequest, used for correlating control requests with responses.
- `resolvedToolUseIds`: Set of resolved tool_use IDs, max 1000, evicts oldest.
- `prependedLines`: Queue for user turns to yield before real input.
- `onControlRequestSent`/`onControlRequestResolved`: Bridge callbacks.
- `restoredWorkerState`: Promise for worker state restore (assigned by RemoteIO).

**`prependUserMessage(content)`** (lines 204-213): Queues a user turn as an NDJSON-encoded `SDKUserMessage`.

**`read()` generator** (lines 215-261):
- Splits input by `'\n'` into lines.
- Processes each line via `processLine()`.
- On input closed, rejects all pending requests.

**`processLine(line)`** (lines 333-462):
- Skips empty lines and `keep_alive` messages.
- Applies `update_environment_variables` messages directly to `process.env`.
- For `control_response`: resolves matching pending request, tracks resolved tool_use ID, notifies `onControlRequestResolved`, rejects on error subtype. If no pending request, checks `resolvedToolUseIds` for duplicates, calls `unexpectedResponseCallback`.
- Validates message type is `user`/`control_request`/`assistant`/`system`.
- Validates user message role is `'user'`.

**`write(message)`** (lines 465-467): Writes message to stdout as NDJSON line.

**`sendRequest(request, schema, signal?, requestId?)`** (lines 469-531):
- Constructs `SDKControlRequest` with generated or provided requestId.
- Enqueues to `outbound` stream.
- On abort signal: sends `control_cancel_request`, tracks resolved tool_use ID, rejects with `AbortError`.
- Returns a Promise<Response> that resolves when matching `control_response` arrives.
- Cleans up in finally (removes abort listener, deletes pending request).

**`createCanUseTool(onPermissionPrompt?)`** (lines 533-659):
- Returns a `CanUseToolFn` that races `hasPermissionsToUseTool` against SDK permission prompt.
- Runs `PermissionRequest` hooks in parallel with SDK prompt.
- Whichever resolves first wins; the loser is cancelled.
- `executePermissionRequestHooksForSDK` (lines 787-858) iterates over hook generator, returns the first allow/deny decision. On allow, applies permission updates and persists them.

**`createHookCallback(callbackId, timeout?)`** (lines 661-688): Returns a HookCallback that sends `hook_callback` control request and awaits response.

**`handleElicitation(serverName, message, requestedSchema?, signal?, mode?, url?, elicitationId?)`** (lines 694-721): Sends elicitation request to SDK consumer and returns response.

**`createSandboxAskCallback()`** (lines 731-753): Creates callback that piggybacks on `can_use_tool` protocol with synthetic `SandboxNetworkAccess` tool name.

**`sendMcpMessage(serverName, message)`** (lines 758-773): Sends MCP message to SDK server and awaits response.

### `cli/update.ts` (422 lines)

**Auto-update mechanism.** Handles version check, download, extraction, and installation.

#### `update()` function (line 30-422)

1. Logs `tengu_update_check` event, prints current version.
2. Reads autoUpdatesChannel from settings (default 'latest').
3. Runs diagnostic via `getDoctorDiagnostic()` to detect installation type.
4. Warns on multiple installations.
5. Displays diagnostic warnings.
6. Updates config if `installMethod` is not set.
7. **Development builds**: Warns and exits — cannot update.
8. **Package-manager installs**: Shows platform-specific update instructions (brew, winget, apk, or generic).
9. **Config/reality mismatch**: Detects and corrects config/actual installation type.
10. **Native installation**: Calls `installLatestNative(channel, true)`, handles lock contention, prints success/failure.
11. **NPM-based update**: Fetches latest version from npm registry, handles failures with diagnostic messages, determines update method (local vs global), calls `installOrUpdateClaudePackage(channel)` or `installGlobalPackage()`, handles status results (success, no_permissions, install_failed, in_progress), regenerates completion cache on success.

### `cli/remoteIO.ts` (255 lines)

**Remote I/O transport for SDK control protocol over stdin/stdout.** Extends `StructuredIO`. Used for bridge/remote control sessions.

#### `RemoteIO` Class

**Constructor** (lines 44-215):
- Takes `streamUrl`, optional `initialPrompt`, and `replayUserMessages` flag.
- Creates `PassThrough` input stream.
- Parses URL, prepares auth headers from session ingress token.
- Gets appropriate transport via `getTransportForUrl(streamUrl, headers, sessionId, refreshHeaders)`.
- Sets transport data callback to write to input stream.
- Sets transport close callback to end input stream.
- **CCR v2 initialization** (lines 116-168): If `CLAUDE_CODE_USE_CCR_V2` is set, creates `CCRClient` with the SSE transport, calls `initialize()`, wires `restoredWorkerState`, registers cleanup, sets internal event writer/reader for transcript persistence, wires lifecycle listener for delivery reporting, state change, and metadata change.
- Calls `transport.connect()` (fire-and-forget).
- Sets up keep-alive timer for bridge sessions (interval from GrowthBook config).
- Registers cleanup for graceful shutdown.
- Forwards initial prompt through input stream.

**`write(message)`** (lines 231-242): Delegates to CCRClient if present, else direct transport write. In bridge mode, echoes control_request and debug messages to stdout.

**`close()`** (lines 247-254): Clears keep-alive timer, closes transport, ends input stream.

### `cli/exit.ts` (31 lines)

**Exit code constants and `exitProcess` function.** Consolidates the "print + lint-suppress + exit" block.

- **`cliError(msg?)`**: Writes error message to stderr (if given), exits with code 1. Returns `never`.
- **`cliOk(msg?)`**: Writes message to stdout (if given), exits with code 0. Returns `never`.

Both use `return undefined as never` for testability — tests spy on `process.exit` and let it return.

### `cli/ndjsonSafeStringify.ts` (32 lines)

**NDJSON-safe JSON stringify** handling JavaScript line terminators.

- **`escapeJsLineTerminators(json)`**: Replaces U+2028 (LINE SEPARATOR) and U+2029 (PARAGRAPH SEPARATOR) with `\u2028`/`\u2029` — prevents line-splitting receivers from breaking mid-string.
- **`ndjsonSafeStringify(value)`**: Calls `escapeJsLineTerminators(jsonStringify(value))`. The `\uXXXX` form is equivalent JSON that parses to the same value, matching ES2019 "Subsume JSON" semantics.

### `cli/handlers/agents.ts` (70 lines)

**Agent management handler.** Lists agents loaded from settings/plugins.

#### `agentsHandler()` (line 32-70)
- Gets all agent definitions with overrides from `getAgentDefinitionsWithOverrides(cwd)`.
- Filters active agents via `getActiveAgentsFromList`.
- Resolves overrides via `resolveAgentOverrides`.
- Groups agents by source (Built-in, Plugins, Settings, Inline) using `AGENT_SOURCE_GROUPS`.
- Prints each agent with model display and memory scope. Shadowed agents are marked `(shadowed by ...)`.

### `cli/handlers/auth.ts` (330 lines)

**Auth handlers:** login, logout, API key management, OAuth flow.

#### `installOAuthTokens(tokens)` (line 50-110)
- Performs logout first (clears old state).
- Fetches or reuses OAuth profile.
- Stores account info (UUID, email, organization, billing, subscription dates).
- Saves tokens, clears cache.
- Fetches user roles and first token date.
- For non-claude.ai auth, creates and stores API key.
- Clears auth-related caches.

#### `authLogin({ email, sso, console: useConsole, claudeai })` (line 112-230)
- Validates mutual exclusion of `--console` and `--claudeai`.
- Resolves login method: forceLoginMethod from settings, else `useConsole` flag.
- **Refresh token fast path**: If `CLAUDE_CODE_OAUTH_REFRESH_TOKEN` env var is set, exchanges it directly for tokens (requires `CLAUDE_CODE_OAUTH_SCOPES`).
- **Browser OAuth flow**: Creates `OAuthService`, calls `startOAuthFlow`, installs tokens, validates force login org.

#### `authStatus(opts)` (line 232-319)
- Determines auth state: checks auth token source, API key source, env vars, OAuth account info, subscription type, 3P services.
- Resolves auth method: `third_party`, `claude.ai`, `api_key_helper`, `oauth_token`, `api_key`, or `none`.
- **Text mode**: Prints account and API provider properties.
- **JSON mode**: Outputs JSON with `loggedIn`, `authMethod`, `apiProvider`, optional `apiKeySource`, `email`, `orgId`, `orgName`, `subscriptionType`.
- Exits with code 0 if logged in, 1 otherwise.

#### `authLogout()` (line 321-330)
- Calls `performLogout({ clearOnboarding: false })`.
- Prints success message.

### `cli/handlers/autoMode.ts` (170 lines)

**Auto mode handler:** enables/disables automatic permission approval.

#### `autoModeDefaultsHandler()` (line 24-26)
- Prints default external auto mode rules (allow, soft_deny, environment sections).

#### `autoModeConfigHandler()` (line 35-47)
- Prints effective auto mode config: user settings where provided, external defaults otherwise. Uses per-section REPLACE semantics.

#### `autoModeCritiqueHandler(options)` (lines 73-149)
- Checks if custom rules exist.
- Uses `sideQuery` with a specialized critique system prompt to analyze custom rules.
- Sends both the full classifier system prompt and the user's custom rules.
- Prints the critique text.
- `formatRulesForCritique(section, userRules, defaultRules)` (lines 151-170) formats rules with context about what defaults are being replaced.

### `cli/handlers/mcp.tsx` (362 lines)

**MCP server management handler:** list, add, remove, connect, disconnect.

#### `mcpServeHandler({ debug, verbose })` (lines 42-71)
- Logs `tengu_mcp_start` event.
- Validates CWD exists.
- Calls `setup()` then `startMCPServer(cwd, debug, verbose)`.

#### `mcpRemoveHandler(name, options)` (lines 74-141)
- Looks up config before removal for secure storage cleanup.
- If scope specified, removes from that scope directly.
- If no scope, checks project (`.mcp.json`), local, user scopes for the server.
- If server exists in one scope, removes it.
- If server exists in multiple scopes, lists them and suggests scope-specific removal.
- Cleans up secure storage tokens on removal.

#### `mcpListHandler()` (lines 144-190)
- Gets all MCP configs, checks health concurrently via `pMap` with configurable batch size.
- Prints server name, transport type (SSE URL, HTTP URL, stdio command+args), and health status.
- Uses `gracefulShutdown(0)` for proper cleanup.

#### `mcpGetHandler(name)` (lines 193-283)
- Gets config for specific server, shows scope, type-specific details (URL, headers, OAuth config, command, args, env).

#### `mcpAddJsonHandler(name, json, options)` (lines 286-314)
- Parses JSON, adds config to specified scope.
- Optionally reads and stores client secret for SSE/HTTP servers.

#### `mcpAddFromDesktopHandler(options)` (lines 317-349)
- Reads Claude Desktop MCP servers, renders `MCPServerDesktopImportDialog` for interactive import.

#### `mcpResetChoicesHandler()` (lines 352-361)
- Resets project-scoped `.mcp.json` server approvals and rejections.

### `cli/handlers/plugins.ts` (878 lines)

**Plugin management handler:** install, uninstall, list, enable, disable, validate, marketplace management.

#### `pluginValidateHandler(manifestPath, options)` (lines 101-154)
- Validates a plugin manifest file.
- If the file is a plugin manifest inside `.claude-plugin` directory, also validates content files.
- Prints validation results with errors/warnings.

#### `pluginListHandler(options)` (lines 157-444)
- Lists installed plugins with version, scope, enabled status, install path, MCP servers.
- **JSON mode**: Outputs structured data including optional `--available` marketplace plugins.
- **Human mode**: Formatted output with tick/cross status indicators, session-only plugins, path-level failures.

#### `marketplaceAddHandler(source, options)` (lines 447-524)
- Parses marketplace source (owner/repo, URL, path).
- Validates scope, supports `--sparse` for GitHub/Git sources.
- Adds marketplace source, saves to settings, clears caches.

#### `marketplaceListHandler(options)` (lines 527-592)
- Lists configured marketplaces with source type details.

#### `marketplaceRemoveHandler(name, options)` (lines 595-609)
- Removes marketplace source, clears caches.

#### `marketplaceUpdateHandler(name, options)` (lines 616-665)
- Updates specific marketplace or all marketplaces via refresh.

#### `pluginInstallHandler(plugin, options)` (lines 668-701)
- Installs a plugin from marketplace. Validates scope against `VALID_INSTALLABLE_SCOPES`.

#### `pluginUninstallHandler(plugin, options)` (lines 704-737)
- Uninstalls a plugin. Supports `--keepData` flag.

#### `pluginEnableHandler(plugin, options)` (lines 740-779)
- Enables a plugin. Supports `--cowork` for user scope only.

#### `pluginDisableHandler(plugin, options)` (lines 782-843)
- Disables a plugin or all plugins (`--all`). Cannot combine `--all` with `--scope`.

#### `pluginUpdateHandler(plugin, options)` (lines 846-878)
- Updates a plugin. Validates scope against `VALID_UPDATE_SCOPES`.

### `cli/handlers/util.tsx` (110 lines)

**CLI handler utilities:** setup-token, doctor, install.

#### `setupTokenHandler(root)` (lines 20-50)
- Checks if Anthropic auth is already configured.
- Renders `ConsoleOAuthFlow` with `WelcomeV2` header.
- Shows warning if existing auth is configured.
- Uses setup-token mode for long-lived (1-year) auth token creation.

#### `doctorHandler(root)` (lines 72-87)
- Renders `Doctor` screen (lazy-loaded) wrapped in `MCPConnectionManager` for diagnosing system state.

#### `installHandler(target, options)` (lines 90-109)
- Calls `setup()` then `install` command. Supports optional target and `--force` flag.

### `cli/transports/ccrClient.ts` (998 lines)

**CCR (Claude Code Remote) client:** WebSocket connection, event serialization. Manages the worker lifecycle protocol with CCR v2.

#### `CCRClient` Class

**Constructor** (lines 310-446):
- Takes `transport` (SSETransport), `sessionUrl`, and options.
- Configures epoch mismatch handler (default: process.exit(1)).
- Sets heartbeat interval (default 20s).
- Sets auth header source (default: process-wide session ingress auth headers).
- Parses session base URL and ID from the URL path.
- Creates four uploader instances:
  - `WorkerStateUploader`: PUT /worker (state + metadata).
  - `eventUploader` (SerialBatchEventUploader): POST /worker/events (client events).
  - `internalEventUploader` (SerialBatchEventUploader): POST /worker/internal-events (transcript entries).
  - `deliveryUploader` (SerialBatchEventUploader): POST /worker/events/delivery (delivery status reports).
- Wires transport's `setOnEvent` to report delivery status as 'received'.

**`initialize(epoch?)`** (lines 459-526):
- Validates auth headers, reads or accepts worker_epoch.
- Calls PUT /worker to register with status 'idle' and clear stale metadata.
- Reads back prior worker state via `getWorkerState()`.
- Starts heartbeat timer.
- Registers session activity callback for keep-alive writes.
- Returns restored metadata.

**`request(method, path, body, label, opts?)`** (lines 556-642):
- Sends authenticated HTTP request to CCR.
- Handles auth headers, 409 epoch mismatch, 401/403 with expired JWT detection.
- Counts consecutive auth failures (max 10 before exit).
- On 429, reads `Retry-After` header for server-specified backoff.

**`reportState(state, details?)`** (lines 645-658): Queues worker status change via `WorkerStateUploader`.

**`reportMetadata(metadata)`** (lines 661-663): Queues external metadata change.

**`writeEvent(message)`** (lines 735-751):
- For `stream_event` type: buffers for up to 100ms before flushing (text_delta coalescing).
- For other types: flushes buffered stream events first, then enqueues.
- On `assistant` type: clears stream accumulator for the message.

**`writeInternalEvent(eventType, payload, opts?)`** (lines 793-814): Writes internal worker events (transcript messages, compaction markers).

**Accumulator** (lines 86-223):
- `createStreamAccumulator()`: Creates accumulator state tracking per-message block text.
- `accumulateStreamEvents(buffer, state)`: Processes stream events, merging text_delta chunks into full-so-far snapshots by content block. Each flush emits one self-contained event per block.
- `clearStreamAccumulatorForMessage(state, assistant)`: Clears state when a complete assistant message arrives.

**`readInternalEvents()`** (lines 842-843): Reads foreground agent internal events via paginated GET.

**`readSubagentInternalEvents()`** (lines 852-858): Reads all subagent internal events via paginated GET.

**`paginatedGet(path, params, context)`** (lines 864-899): Fetches all pages from a list endpoint with retry.

**`getWithRetry(url, authHeaders, context)`** (lines 905-958): Single GET with up to 10 retries using exponential backoff + jitter.

**`close()`** (lines 982-997): Stops heartbeat, clears buffers/accumulators, closes all uploaders.

### `cli/transports/HybridTransport.ts` (282 lines)

**Hybrid transport combining SSE + WebSocket.** Extends `WebSocketTransport`.

#### `HybridTransport` Class

- **Write flow**: Writes use HTTP POST via `SerialBatchEventUploader`. stream_event messages buffer for 100ms before enqueuing.
- **Constructor** (lines 63-108): Creates uploader with configurable max batch sizes, max queue size, retry delays, and optional dropout on max consecutive failures.
- **`write(message)`** (lines 117-133): Delays stream_events; immediate messages flush buffered events first then enqueue.
- **`writeBatch(messages)`** (lines 135-138): Batch enqueue + flush.
- **`flush()`** (lines 149-152): Flushes buffered stream events + uploader.
- **`close()`** (lines 171-195): Grace period for queued writes (3s), then closes uploader. Keeps close() sync.
- **`postOnce(events)`** (lines 202-261): Single-attempt POST. Retryable on 429/5xx/network errors. Permanent on 4xx (non-429)/no-token.

**URL conversion** (`convertWsUrlToPostUrl`, lines 269-281): Converts wss://.../ws/... to https://.../session/.../events.

### `cli/transports/SerialBatchEventUploader.ts` (275 lines)

**Batched analytics event uploader.** Serial ordered uploader with batching, retry, and backpressure.

#### `RetryableError` Class (lines 26-33)
- Custom error with optional `retryAfterMs` for server-specified backoff.

#### `SerialBatchEventUploader<T>` Class

**Configuration**:
- `maxBatchSize`: Max items per POST.
- `maxBatchBytes?`: Max serialized bytes per POST (first item always goes regardless).
- `maxQueueSize`: Max pending items before `enqueue()` blocks.
- `send(batch)`: The actual HTTP call.
- `baseDelayMs`, `maxDelayMs`, `jitterMs`: Retry timing.
- `maxConsecutiveFailures?`: After this many failures, drop the batch and move on (optional; undefined = indefinite retry).
- `onBatchDropped?`: Callback when a batch is dropped.

**`enqueue(events)`** (lines 101-119): Adds events to pending buffer. Blocks if queue is full (backpressure).

**`flush()`** (lines 125-133): Blocks until all pending events are sent. Used at turn boundaries and shutdown.

**`close()`** (lines 139-150): Drops pending events, resolves blocked callers.

**`drain()`** (lines 156-202): Serial drain loop. Takes batches, sends, retries on failure with exponential backoff. Releases backpressure after each successful batch. Notifies flush waiters when queue empties.

**`takeBatch()`** (lines 213-233): Pulls next batch respecting maxBatchSize and maxBatchBytes. Drops un-serializable items (BigInt, circular refs, throwing toJSON).

**`retryDelay(failures, retryAfterMs?)`** (lines 235-253): Computes delay as `min(baseDelay * 2^(failures-1), maxDelay) + jitter`. If `retryAfterMs` is provided, clamps it to [baseDelay, maxDelay] before adding jitter.

### `cli/transports/SSETransport.ts` (711 lines)

**Server-Sent Events transport for streaming.** Reads events via SSE from the CCR v2 event stream endpoint, writes via HTTP POST with retry.

#### `SSETransport` Class (implements Transport)

**Configuration constants**:
- `RECONNECT_BASE_DELAY_MS`: 1000ms.
- `RECONNECT_MAX_DELAY_MS`: 30,000ms.
- `RECONNECT_GIVE_UP_MS`: 600,000ms (10 minutes).
- `LIVENESS_TIMEOUT_MS`: 45,000ms.
- `PERMANENT_HTTP_CODES`: Set of {401, 403, 404}.
- `POST_MAX_RETRIES`: 10.
- `POST_BASE_DELAY_MS`: 500ms.
- `POST_MAX_DELAY_MS`: 8000ms.

**Constructor** (lines 190-219):
- Takes URL, headers, sessionId, refreshHeaders, initialSequenceNum, getAuthHeaders.
- Converts SSE URL to POST URL.
- Seeds high-water mark sequence number for resumption.

**`connect()`** (lines 231-333):
- Builds SSE URL with `from_sequence_num` param for resumption.
- Sends fetch request with auth headers, Last-Event-ID, abort signal.
- On permanent status codes: transitions to 'closed', calls onCloseCallback.
- On success: reads the SSE stream body via `readStream()`.
- On error: calls `handleConnectionError()`.

**`readStream(body)`** (lines 339-415):
- Reads stream in chunks, decodes with TextDecoder, parses SSE frames via `parseSSEFrames()`.
- Tracks sequence numbers for dedup and high-water mark.
- Calls `handleSSEFrame(event, data)` for each frame.
- On stream end: reconnects unless closing.

**`parseSSEFrames(buffer)`** (lines 58-116): Incrementally parses SSE frames, returning parsed frames and remaining buffer. Handles `event:`, `id:`, `data:` fields, multi-line data concatenation, and comments.

**`handleSSEFrame(eventType, data)`** (lines 425-465):
- Expects `client_event` type (other types are logged as warnings).
- Parses JSON, extracts payload, passes to `onData` as newline-delimited JSON.
- Calls `onEventCallback` with the full StreamClientEvent.

**`handleConnectionError()`** (lines 470-535):
- Aborts in-flight fetch, clears liveness timer.
- Checks reconnection time budget (10 minutes).
- Applies exponential backoff with ±25% jitter.
- Refreshes headers before reconnecting.
- On budget exhaustion: transitions to 'closed', calls onCloseCallback.

**Liveness**:
- `resetLivenessTimer()`: Resets 45s timer. Any SSE frame (including comments) resets it.
- `onLivenessTimeout`: Aborts connection and reconnects.

**`write(message)`** (lines 572-653):
- Sends message via HTTP POST with up to 10 retries.
- Uses exponential backoff for 429/5xx errors.
- 4xx errors (non-429) are permanent — no retry.

**`close()`** (lines 679-689): Clears reconnect timer, liveness timer, aborts fetch.

### `cli/transports/WebSocketTransport.ts` (800 lines)

**WebSocket transport with reconnection, backoff, heartbeat.** Supports both Bun (native WebSocket) and Node.js (ws package).

#### `WebSocketTransport` Class (implements Transport)

**Configuration constants**:
- `DEFAULT_MAX_BUFFER_SIZE`: 1000.
- `DEFAULT_BASE_RECONNECT_DELAY`: 1000ms.
- `DEFAULT_MAX_RECONNECT_DELAY`: 30,000ms.
- `DEFAULT_RECONNECT_GIVE_UP_MS`: 600,000ms (10 minutes).
- `DEFAULT_PING_INTERVAL`: 10,000ms.
- `DEFAULT_KEEPALIVE_INTERVAL`: 300,000ms (5 minutes).
- `SLEEP_DETECTION_THRESHOLD_MS`: 60,000ms.
- `PERMANENT_CLOSE_CODES`: Set of {1002, 4001, 4003}.

**Constructor** (lines 119-133):
- Takes URL, headers, sessionId, refreshHeaders, options (autoReconnect, isBridge).
- Creates `CircularBuffer` for message buffering (replay on reconnect).

**`connect()`** (lines 135-193):
- Bun path: Creates native WebSocket with headers, proxy, TLS options.
- Node path: Dynamically imports `ws`, creates WS with agent and TLS options.
- Wires open/message/error/close/pong event handlers for each runtime.

**Event handlers** (Bun vs Node):
- **Open**: Calls `handleOpenEvent()`, replays buffered messages (Bun) or checks upgrade response headers for last-id (Node).
- **Message**: Passes data to `onData` callback.
- **Error**: Logged, `close` event fires after.
- **Close**: Calls `handleConnectionError(closeCode)`.
- **Pong**: Sets `pongReceived = true`.

**`handleOpenEvent()`** (lines 296-329):
- Logs connect duration, emits `tengu_ws_transport_reconnected` event (bridge only).
- Resets reconnection state, sets state to 'connected'.
- Starts ping interval (10s), keepalive interval (5min), session activity callback.

**`handleConnectionError(closeCode?)`** (lines 397-553):
- Disconnects WS, removes listeners.
- For permanent codes (1002/4001/4003): doesn't retry unless 4003 has refreshed headers.
- Sleep detection: if gap between reconnection attempts exceeds 60s, resets budget.
- 10-minute time budget from first failure.
- Exponential backoff with ±25% jitter.
- Emits telemetry events for bridge sessions.

**Ping/keepalive**:
- `startPingInterval()`: 10s ping with pong timeout. Detects process suspension via tick gap.
- `startKeepaliveInterval()`: 5min keep-alive data frame (skipped in CCR sessions).

**`replayBufferedMessages(lastId)`** (lines 574-634):
- Finds server's last confirmed message by UUID, evicts confirmed messages from buffer.
- Replays unconfirmed messages, retaining them in buffer until next reconnection.

**`write(message)`** (lines 660-681): Buffers message if it has UUID, sends line if connected.

**`close()`** (lines 556-572): Clears timers, stops intervals, disconnects.

### `cli/transports/WorkerStateUploader.ts` (131 lines)

**Coalescing uploader for PUT /worker.** Manages session state + metadata uploads with coalescing and retry.

#### `WorkerStateUploader` Class

- **Coalescing**: 1 in-flight PUT + 1 pending patch. New calls coalesce into pending (never grows beyond 1 slot).
- **Merge rules**: Top-level keys (worker_status, external_metadata) — last value wins. Inside metadata — RFC 7396 merge (keys added/overwritten, null values preserved for server-side delete).

**`enqueue(patch)`** (lines 43-47): Coalesces patch into pending, kicks drain.

**`close()`** (lines 49-52): Discards pending patch.

**`drain()`** (lines 54-67): Takes pending payload, sends with retry, on success drains again if new pending arrived.

**`sendWithRetry(payload)`** (lines 70-86): Retries indefinitely with exponential backoff. Absorbs any patches that arrived during retry into the current payload.

**`coalescePatches(base, overlay)`** (lines 106-131): Merges two patches. Top-level keys: overlay wins. Metadata keys: RFC 7396 merge one level deep.

### `cli/transports/transportUtils.ts` (45 lines)

**Transport selection helper** used by `remoteIO.ts` and other SDK ingress paths.

#### Exports
- **`getTransportForUrl(url, headers?, sessionId?, refreshHeaders?)`**: Returns the appropriate `Transport` implementation.

#### Main flow
1. If `CLAUDE_CODE_USE_CCR_V2`: derive SSE stream URL (`.../worker/events/stream`) and return `SSETransport`.
2. Else if `ws:`/`wss:` and `CLAUDE_CODE_POST_FOR_SESSION_INGRESS_V2`: return `HybridTransport` (WS reads + HTTP POST writes).
3. Else if `ws:`/`wss:`: return `WebSocketTransport` (default bidirectional WS).
4. Otherwise throw `Unsupported protocol`.

#### Dependencies
- `HybridTransport`, `SSETransport`, `WebSocketTransport`, `isEnvTruthy`

#### Feature gates / boundaries
- Env-var driven selection (`CLAUDE_CODE_USE_CCR_V2`, `CLAUDE_CODE_POST_FOR_SESSION_INGRESS_V2`); no `feature()` gates in this file.

---

## SETUP

### `setup.ts` (477 lines)

**Post-`init()` environment setup** called from `main.tsx` action handler before REPL or headless mode. Sets CWD/project root, worktrees, hooks, and prefetches.

#### Exports
- **`setup(cwd, permissionMode, allowDangerouslySkipPermissions, worktreeEnabled, worktreeName, tmuxEnabled, customSessionId?, worktreePRNumber?, messagingSocketPath?)`**: `Promise<void>`

#### Main flow / key branches
1. Node.js ≥18 check; exits on failure.
2. Custom session ID via `switchSession()` if provided.
3. UDS messaging server (`UDS_INBOX`) unless `--bare` without explicit socket path.
4. Teammate snapshot capture (swarms, not bare).
5. Terminal backup restore (iTerm2 if swarms; Apple Terminal) — interactive only.
6. `setCwd(cwd)` then `captureHooksConfigSnapshot()` + `initializeFileChangedWatcher()`.
7. Worktree path: create worktree, optional tmux, `chdir`, re-capture hooks.
8. Background init (skipped in `--bare`): `initSessionMemory()`, optional `initContextCollapse()`.
9. Prefetch: `getCommands()`, plugin hooks, API key helper; `initSinks()` + `tengu_started` beacon.
10. Bypass-permissions safety gate (root check, ant-only sandbox/internet validation).
11. Logs `tengu_exit` from prior session metrics if present in project config.

Note: `processSessionStartHooks()` is **not** called here — it runs later from `main.tsx` action handler / `cli/print.js`.

#### Dependencies
- `bootstrap/state.ts`, `commands.ts`, `utils/worktree`, `utils/hooks/*`, `utils/config`, `services/SessionMemory`, feature-gated `services/contextCollapse`

#### Feature gates / boundaries
- `CONTEXT_COLLAPSE`, `COMMIT_ATTRIBUTION`, `TEAMMEM` — lazy `require()` blocks
- `--bare` / `isBareMode()` skips hooks, memory init, release-notes prefetch, attribution hooks

---

## SERVER (Direct Connect Client)

### `server/types.ts` (57 lines)

#### Exports
- **`connectResponseSchema()`**: Zod schema `{ session_id, ws_url, work_dir? }`
- **`ServerConfig`**, **`SessionState`**, **`SessionInfo`**, **`SessionIndexEntry`**, **`SessionIndex`**

#### Dependencies
- `zod/v4`, `lazySchema`, `child_process` types

### `server/createDirectConnectSession.ts` (88 lines)

#### Exports
- **`DirectConnectError`**: Named error for connect failures
- **`createDirectConnectSession({ serverUrl, authToken?, cwd, dangerouslySkipPermissions? })`**: POST `/sessions`, validates response, returns `{ config, workDir? }`

#### Main flow
1. POST JSON body with `cwd` and optional `dangerously_skip_permissions`.
2. Parse/validate via `connectResponseSchema`.
3. Return `DirectConnectConfig` for `DirectConnectSessionManager`.

#### Dependencies
- `./types.js`, `utils/errors`, `utils/slowOperations`

### `server/directConnectManager.ts` (213 lines)

#### Exports
- **`DirectConnectConfig`**, **`DirectConnectCallbacks`**
- **`DirectConnectSessionManager`**: WebSocket client class

#### Main flow
- **`connect()`**: Opens WS with optional Bearer auth; parses NDJSON lines.
- Routes `control_request` subtype `can_use_tool` to `onPermissionRequest`; rejects unknown subtypes with error response.
- Forwards SDK messages (assistant, user, system, etc.) to `onMessage`; filters control/keep-alive/streamlined types.
- **`sendMessage(content)`**: Sends stream-json user message.
- **`respondToPermissionRequest(requestId, result)`**: Sends success control response.
- **`sendInterrupt()`**: Sends interrupt control request.
- **`disconnect()`** / **`isConnected()`**

#### Dependencies
- `entrypoints/agentSdkTypes`, `entrypoints/sdk/controlTypes`, `remote/RemoteSessionManager`, `utils/teleport/api`

#### Feature gates / boundaries
- Client-side only; server process that accepts `/sessions` is out of tree here.

---

## COORDINATOR MODE

### `coordinator/coordinatorMode.ts` (369 lines)

**Multi-agent coordinator mode** — prompt/context helpers when `COORDINATOR_MODE` is enabled and `CLAUDE_CODE_COORDINATOR_MODE=1`.

#### Exports
- **`isCoordinatorMode()`**: `feature('COORDINATOR_MODE')` && env var
- **`matchSessionMode(sessionMode?)`**: Flips env to match resumed session; returns warning string or undefined
- **`getCoordinatorUserContext(mcpClients, scratchpadDir?)`**: `{ workerToolsContext }` for user-context injection
- **`getCoordinatorSystemPrompt()`**: Full coordinator system prompt string

#### Main flow
- Worker tool list filtered from `ASYNC_AGENT_ALLOWED_TOOLS` minus internal worker tools; bare mode restricts to Bash/Read/Edit.
- Scratchpad path injected when Statsig gate `tengu_scratch` is on (duplicated gate check to avoid circular import with `filesystem.ts`).
- Tool surface filtering for REPL/headless is **`applyCoordinatorToolFilter()`** in `utils/toolPool.ts`, not this file.

#### Dependencies
- `constants/tools`, `services/analytics/growthbook`, tool name constants, `isEnvTruthy`

#### Feature gates / boundaries
- Entire module DCE'd when `COORDINATOR_MODE` is off
- Runtime activation requires `CLAUDE_CODE_COORDINATOR_MODE=1`

---

## UPSTREAM PROXY (CCR)

### `upstreamproxy/upstreamproxy.ts` (285 lines)

**Container-side upstreamproxy init** — called from `entrypoints/init.ts` when `CLAUDE_CODE_REMOTE` and `CCR_UPSTREAM_PROXY_ENABLED`.

#### Exports
- **`SESSION_TOKEN_PATH`**: `'/run/ccr/session_token'`
- **`initUpstreamProxy(opts?)`**: Reads token, builds CA bundle, starts relay, sets proxy env; fail-open
- **`getUpstreamProxyEnv()`**: `{ HTTPS_PROXY, SSL_CERT_FILE, NO_PROXY, ... }` for subprocesses
- **`resetUpstreamProxyForTests()`**

#### Main flow
1. Gate on `CLAUDE_CODE_REMOTE` + `CCR_UPSTREAM_PROXY_ENABLED` + session ID.
2. Read session token; download upstreamproxy CA; concatenate with system bundle.
3. Start `startUpstreamProxyRelay()` on ephemeral localhost port.
4. Unlink token file after relay confirmed; register cleanup.

#### Dependencies
- `./relay.js`, `utils/cleanupRegistry`, `utils/debug`

#### Feature gates / boundaries
- Server injects `CCR_UPSTREAM_PROXY_ENABLED` (no client-side GrowthBook check)
- All steps fail open — errors log warning and disable proxy

### `upstreamproxy/relay.ts` (455 lines)

**CONNECT-over-WebSocket relay** for agent subprocess HTTPS traffic.

#### Exports
- **`encodeChunk(data)`** / **`decodeChunk(buf)`**: Protobuf `UpstreamProxyChunk` wire encoding
- **`UpstreamProxyRelay`**: `{ port, close() }`
- **`startUpstreamProxyRelay(opts)`**: Bun-native or Node `ws` relay server
- **`startNodeRelay(...)`**: Node-specific WS tunnel

#### Main flow
1. TCP server accepts HTTP CONNECT from curl/gh/etc.
2. Opens WebSocket to CCR upstreamproxy endpoint with session auth.
3. Bidirectional byte tunnel wrapped in protobuf chunks; 30s WS ping.

#### Dependencies
- `node:net`, `utils/mtls`, `utils/proxy`, optional `ws` package

---

## ROOT HELPERS (entry-adjacent)

### `ink.ts` (85 lines)

**Ink re-export wrapper** with `ThemeProvider`. Exports `render`, `createRoot`, design-system `Box`/`Text`, and core Ink components/hooks from `./ink/`.

### `interactiveHelpers.tsx` (366 lines)

**Interactive TUI lifecycle**: `showDialog`, `renderAndRun`, `exitWithError`, `exitWithMessage`, `showSetupScreens`, `completeOnboarding`, `getRenderContext`.

### `dialogLaunchers.tsx` (133 lines)

**Dynamic-import dialog launchers**: snapshot update, invalid settings, assistant chooser/install, teleport resume/mismatch, resume chooser.

### `replLauncher.tsx` (23 lines)

**`launchRepl(root, appProps, replProps, renderAndRun)`**: Dynamic-imports `App` + `REPL`, mounts via `renderAndRun`.

### `projectOnboardingState.ts` (83 lines)

**Two-step onboarding state machine**: `getSteps()`, `shouldShowProjectOnboarding`, `incrementProjectOnboardingSeenCount`, completion markers in project config.

### `costHook.ts` (22 lines)

**`useCostSummary()`**: React hook writing total session cost to stdout on process exit (console billing users).

---

## `main.tsx` (4684 lines)

### Startup Sequence

Full chain: **`entrypoints/cli.tsx`** (fast paths or fallback) → **`main.tsx` `main()`** → **`run()`** → Commander **`preAction`** (`init()`) → default **`.action()`** → **`setup.ts`** → REPL or headless.

#### 0. `entrypoints/cli.tsx` (runs first)

See the `entrypoints/cli.tsx` section above. When no fast path matches, calls `startCapturingEarlyInput()` and dynamically imports `main.tsx`.

#### 1. Side-Effect Preloading (lines 1–20)

When `main.tsx` loads:
1. `profileCheckpoint('main_tsx_entry')` — marks entry point for startup profiler.
2. `startMdmRawRead()` — fires MDM subprocesses (plutil/reg query) in parallel with remaining imports.
3. `startKeychainPrefetch()` — fires both macOS keychain reads (OAuth + legacy API key) in parallel to avoid ~65ms of sequential reads in `applySafeConfigEnvironmentVariables`.

Module evaluation continues through line 209 (`profileCheckpoint('main_tsx_imports_loaded')`).

#### 2. `runMigrations()` — Migration Function (lines 326–352)

Defines sync migrations (`CURRENT_MIGRATION_VERSION = 11`) and async `migrateChangelogFromConfig()`. **Invoked from the `preAction` hook at line 950**, after `init()` and `initSinks()`, not at import time. Sequence when version is stale:

1. `migrateAutoUpdatesToSettings()`
2. `migrateBypassPermissionsAcceptedToSettings()`
3. `migrateEnableAllProjectMcpServersToSettings()`
4. `resetProToOpusDefault()`
5. `migrateSonnet1mToSonnet45()`
6. `migrateLegacyOpusToCurrent()`
7. `migrateSonnet45ToSonnet46()`
8. `migrateOpusToOpus1m()`
9. `migrateReplBridgeEnabledToRemoteControlAtStartup()`
10. `resetAutoModeOptInForDefaultOffer()` (feature-gated: `TRANSCRIPT_CLASSIFIER`)
11. `migrateFennecToOpus()` (ant-only)

#### 3. Commander Program Setup (lines 884–4504)

Creates a Commander program with:
- `configureHelp()` with sorted options and subcommands.
- **`preAction` hook** (line 907) registered before options/subcommands.
- Default `.action()` handler (line 1006) for the main command.
- Subcommands registered unless print-mode fast path skips them (lines 3883–3889).

**`preAction` execution order** (runs during `parseAsync`, before the matched action):
1. Await MDM settings + keychain prefetch (914–915)
2. `await init()` (916)
3. Set terminal title (922–924)
4. `initSinks()` (931–934)
5. Wire `--plugin-dir` (937–949)
6. `runMigrations()` (950)
7. `void loadRemoteManagedSettings()` + `void loadPolicyLimits()` (957–958)
8. Optional `uploadUserSettingsInBackground()` (`UPLOAD_USER_SETTINGS`, 963–965)

**CLI Options** (>60 options) organized by category:

**Pre-action options** (set before the action handler): `--plugin-dir`, `--settings`, `--setting-sources`.

**Debug/Verbosity**: `--debug`, `--debug-to-stderr`, `--debug-file`, `--verbose`.

**Execution modes**: `--print`/`-p`, `--bare`, `--init`, `--init-only`, `--maintenance`.

**Output**: `--output-format` (text/json/stream-json), `--json-schema`, `--include-hook-events`, `--include-partial-messages`, `--input-format` (text/stream-json), `--replay-user-messages`, `--enable-auth-status`.

**Tools**: `--allowedTools`, `--tools`, `--disallowedTools`.

**MCP**: `--mcp-config`, `--permission-prompt-tool`, `--strict-mcp-config`.

**Prompts**: `--system-prompt`, `--system-prompt-file`, `--append-system-prompt`, `--append-system-prompt-file`.

**Permissions**: `--permission-mode`, `--dangerously-skip-permissions`.

**Session**: `--continue`/`-c`, `--resume`/`-r`, `--fork-session`, `--from-pr`, `--no-session-persistence`, `--resume-session-at`, `--rewind-files`, `--session-id`, `--name`.

**Model**: `--model`, `--effort`, `--agent`, `--betas`, `--fallback-model`, `--workload`.

**Storage**: `--settings`, `--add-dir`.

**Integration**: `--ide`, `--chrome`, `--no-chrome`, `--file`, `--disable-slash-commands`.

**Feature-gated** (only available in specific builds): `--assistant`, `--channels`, `--dangerously-load-development-channels`, `--agent-id`, `--agent-name`, `--team-name`, `--teammate-mode`, `--agent-color`, `--plan-mode-required`, `--parent-session-id`, `--messaging-socket-path`, `--max-budget-usd`, `--task-budget`, `--enable-auto-mode`, `--remote`, `--remote-control`/`--rc`, `--teleport`, `--worktree`/`-w`, `--tmux`, `--sdk-url`, `--prefill`.

#### 4. Feature-Gated Conditional Imports

At module scope (before `main()`):
- `coordinatorModeModule`: `require('./coordinator/coordinatorMode.js')` if `COORDINATOR_MODE`.
- `assistantModule` and `kairosGate`: `require('./assistant/...')` if `KAIROS`.
- `autoModeStateModule`: `require('./utils/permissions/autoModeState.js')` if `TRANSCRIPT_CLASSIFIER`.

Inside the action handler, dynamic imports:
- `parseConnectUrl` (DIRECT_CONNECT feature).
- `handleDeepLinkUri` / `handleUrlSchemeLaunch` (LODESTONE feature).
- `buildBridgeConnectUrl`, `extractInboundMessageFields` (bridge mode).
- `isComputerUseMCPServer` / `getChicagoEnabled` / `setupComputerUseMCP` (CHICAGO_MCP).
- `applyCoordinatorToolFilter` from `utils/toolPool.js` (COORDINATOR_MODE).

#### 5. Main Dispatch Logic

The `main()` function (lines 585-856) orchestrates:
1. **Windows security**: Sets `NoDefaultCurrentDirectoryInExePath='1'`.
2. **Warning handler**: Initializes early.
3. **SIGINT handling**: In print mode, defers to print.ts's own handler; otherwise exits.
4. **cc:// URL handling**: Parses and rewrites argv for interactive or headless paths. For headless: rewrites to `open` subcommand. For interactive: stashes serverUrl/authToken, strips cc URL and flags.
5. **`--handle-uri` processing** (LODESTONE): Handles deep link URIs from OS protocol handler, exits after processing.
6. **macOS URL handler** (LODESTONE): Detects `__CFBundleIdentifier` for LaunchServices URL launches.
7. **`claude assistant` processing** (KAIROS): Stashes sessionId/discover flags, strips from argv for main command path.
8. **`claude ssh` processing** (SSH_REMOTE): Extracts host, cwd, permission mode, dangerous permissions, local flag, extra CLI args (--continue, --resume, --model). Strips from argv.
9. **Interactive/non-interactive determination**: Based on `--print`, `--init-only`, `--sdk-url`, TTY status. Stops early input capture for non-interactive.
10. **Client type determination**: Maps `CLAUDE_CODE_ENTRYPOINT` env var and session ingress token to client type (github-action, sdk-typescript, sdk-python, sdk-cli, claude-vscode, local-agent, claude-desktop, remote, cli).
11. **Eager settings loading**: Parses `--settings` and `--setting-sources` flags before `run()`.
12. **Calls `run()`** — the main command handler.

#### 6. `run()` — Commander Program Execution (lines 884–4513)

1. Creates Commander program with sorted help and positional options.
2. Registers `preAction` hook (see step 3 above).
3. Defines all >60 CLI options and default `.action()` handler.
4. **Print-mode fast path** (3883–3889): if `-p`/`--print` and no `cc://` URL in argv, skips subcommand registration and calls `parseAsync` immediately (line 3887).
5. Registers subcommands (full path only): `update`, `mcp`, `plugin`, `auth`, `doctor`, `install`, `auto-mode`, `agents`, `setup-token`, feature-gated `assistant`/`output-style`, etc.
6. **`await program.parseAsync(process.argv)`** — full path at line **4504**; triggers `preAction` then the matched action handler.

#### Action Handler (lines 1007–3860+)

Runs after `preAction` completes. The enormous default action covers:

**Early flags**: `--bare` sets `CLAUDE_CODE_SIMPLE=1`. Ignores "code" as a prompt (shows tip).

**Assistant/Kairos mode**: If `--assistant` or settings-based assistant mode, forces brief mode, initializes assistant team. Trust-gated: refuses to activate until directory is trusted.

**Option extraction**: Destructures 40+ options from Commander.

**Note**: `cc://`, `claude assistant`, and `claude ssh` argv rewriting happens in **`main()`** (lines 609–795), not here. The action handler consumes stashed state (`_pendingConnect`, `_pendingSSH`, `_pendingAssistantChat`) for Direct Connect / SSH / assistant launch branches (~3156+).

**Validation**: Validates mutual exclusion of flags (session-id with continue/resume, system-prompt with system-prompt-file, console with claudeai, model with fallback-model, tmux with worktree/Windows).

**File downloads** (`--file` flag): Downloads file resources using session ingress token before REPL renders.

**Format validation**: Validates input/output format combinations, SDK URL format requirements, replayUserMessages format requirements, includePartialMessages requirements, no-session-persistence requirements.

**Input prompt**: Calls `getInputPrompt()` — reads stdin if not TTY (with 3s timeout warning).

**Proactive activation**: Activates proactive mode before `getTools()` so SleepTool passes filtering.

**Tools**: Gets tools from `getTools(toolPermissionContext)`. Applies coordinator filter if enabled. Adds SyntheticOutputTool if jsonSchema provided.

**setup()**: Calls `setup()`, `getCommands()`, `getAgentDefinitionsWithOverrides()` — runs setup and command/agent loading in parallel (except when worktree is enabled, where setup must process.chdir() first).

**Worktree setup**: Creates worktree if enabled, optionally with PR reference or custom name. Validates tmux availability.

**Direct Connect**: Opens cc:// connection, launches REPL with remote session.

**Teleport**: If URL, fetches session from teleport API, validates repository, checks out branch, processes messages for resume, launches teleport resume wrapper.

**Remote mode**: Validates bridge enabled/gated, configures bridge settings, launches bridge session.

**SSH mode**: Launches SSH-based REPL with remote session.

**Permission & MCP setup**: Initializes tool permission context, determines permission mode, parses MCP configs, filters by policy, handles enterprise MCP config conflicts, sets up Claude in Chrome MCP (if subscriber), sets up Chicago MCP (feature-gated, macOS only), filters MCP tools by deny rules.

**Action handler dispatch** (interactive vs print):
- **Print mode app**: Gets `getAppState`/`setAppState` from store, loads session start hooks, handles message replay format, waits for MCP configs, prefetches MCP resources, merges dynamic/global/claudeai MCP configs, runs `runHeadless()`.
- **Interactive mode app**: Creates Ink render instance, renders REPL component with 67 props (all parsed options, MCP configs, tool context, commands, SDK configs, worktree paths, etc.), implements dynamic imports for heavy components (REPL itself is lazy-loaded).

**`prefetchSystemContextIfSafe()`** (lines 360-380): Prefetches git status safely — only after trust is established or in non-interactive mode (where trust is implicit).

**`startDeferredPrefetches()`** (lines 388-427): Called after first render to reduce event loop contention. Prefetches: initUser, getUserContext, system context, tips, AWS/GCP credentials, file count, analytics gates, official MCP URLs, model capabilities, settings change detector, skill change detector. All skipped in `--bare` mode or when `CLAUDE_CODE_EXIT_AFTER_FIRST_RENDER` is set.

**`logSessionTelemetry()`** (lines 279-290): Logs skills and plugin telemetry. Called from both interactive and headless paths.

**`logStartupTelemetry()`** (lines 307-321): Logs startup telemetry (is_git, worktree_count, gh_auth_status, sandbox settings, auto_updater, prefers_reduced_motion, cert env vars).
