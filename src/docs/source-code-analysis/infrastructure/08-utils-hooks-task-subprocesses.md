# 08 — Utils: Hooks, Task, Subprocesses, and Related Infrastructure

This document covers six subsystems that together form Claude Code's execution framework: the hook system (pre/post sampling lifecycle), the task output framework, the teleport cross-session communication system, background remote session preconditions, shared tool utilities, the tips system, and the prompt suggestion/speculation system.

---

## Batch 1 — `utils/hooks/` (17 files, ~3,600 lines)

The hooks subsystem is the event-driven lifecycle layer of Claude Code. Hooks allow external commands, LLM prompts, HTTP requests, or in-process callbacks to fire at specific lifecycle events (before/after tool use, on session start/stop, on file changes, etc.).

### 1.1 `AsyncHookRegistry.ts` (309 lines)

**Exports:**

| Export | Kind | Description |
|--------|------|-------------|
| `PendingAsyncHook` | Type | Shape of a registered async hook in the global pending map |
| `registerPendingAsyncHook(...)` | Function | Registers a new async hook with progress interval + timeout |
| `getPendingAsyncHooks()` | Function | Returns hooks where `responseAttachmentSent === false` |
| `checkForAsyncHookResponses()` | Async Function | Polls all pending hooks for completed JSON output |
| `removeDeliveredAsyncHooks(processIds)` | Function | Removes hooks whose response has already been sent |
| `finalizePendingAsyncHooks()` | Async Function | Finalizes/sends response for all remaining hooks, kills still-running processes |
| `clearAllAsyncHooks()` | Function | Test utility — stops progress intervals, clears all pending hooks |

**Types:**

```typescript
type PendingAsyncHook = {
  processId: string
  hookId: string
  hookName: string
  hookEvent: HookEvent | 'StatusLine' | 'FileSuggestion'
  toolName?: string
  pluginId?: string
  startTime: number
  timeout: number
  command: string
  responseAttachmentSent: boolean
  shellCommand?: ShellCommand
  stopProgressInterval: () => void
}
```

**Architecture:**
- Uses a module-level `Map<string, PendingAsyncHook>` (`pendingHooks`) as global state
- `registerPendingAsyncHook` creates a progress interval via `startHookProgressInterval` from `hookEvents.ts` and stores the hook
- `checkForAsyncHookResponses` is the main polling loop: iterates all pending hooks, checks if `shellCommand.status === 'completed'`, reads stdout line-by-line looking for JSON that doesn't contain `"async"`, and returns the first valid `SyncHookJSONOutput`
- Completed hooks are finalized via `finalizeHook()` which calls `stopProgressInterval()`, reads final output, cleans up the shell command, and emits the response via `emitHookResponse()`
- On `SessionStart` hook completion, invalidates the session env cache
- `finalizePendingAsyncHooks` handles cleanup on session end — completes running hooks, kills still-running ones with `'cancelled'` outcome

### 1.2 `execAgentHook.ts` (339 lines)

**Exports:**

| Export | Kind | Description |
|--------|------|-------------|
| `execAgentHook(...)` | Async Function | Executes an agent-based hook using a multi-turn LLM query |

**Signature:**

```typescript
async function execAgentHook(
  hook: AgentHook,
  hookName: string,
  hookEvent: HookEvent,
  jsonInput: string,
  signal: AbortSignal,
  toolUseContext: ToolUseContext,
  toolUseID: string | undefined,
  _messages: Message[], // kept for signature stability
  agentName?: string,
): Promise<HookResult>
```

**Behavior:**
1. Replaces `$ARGUMENTS` placeholders in `hook.prompt` with `jsonInput` via `addArgumentsToPrompt`
2. Creates a user message from the processed prompt (bypasses `processUserInput` to avoid recursion)
3. Sets up a timeout (default 60s) combined with the parent abort signal
4. Creates a `StructuredOutput` tool (via `createStructuredOutputTool` from `hookHelpers.ts`)
5. Filters out the `SyntheticOutputTool` from parent tools to avoid schema conflicts
6. Filters out `ALL_AGENT_DISALLOWED_TOOLS` to prevent recursive agent spawning
7. Creates a unique `hookAgentId` and a modified `toolUseContext` with `isNonInteractiveSession: true`, `thinkingConfig: 'disabled'`, and a permission context that auto-allows reading the transcript
8. Registers a session-level stop hook for structured output enforcement
9. Runs `query()` for multi-turn execution with max 50 turns
10. Listens for `structured_output` attachment messages — first valid response with `{ok: boolean, reason?: string}` is captured
11. Returns `'success'`, `'blocking'`, `'cancelled'`, or `'non_blocking_error'` outcomes
12. Cleans up the session hook after execution, logs analytics events (`tengu_agent_stop_hook_*`)

### 1.3 `execHttpHook.ts` (242 lines)

**Exports:**

| Export | Kind | Description |
|--------|------|-------------|
| `execHttpHook(...)` | Async Function | POSTs hook input to a configured URL and returns response |

**Signature:**

```typescript
async function execHttpHook(
  hook: HttpHook,
  _hookEvent: HookEvent,
  jsonInput: string,
  signal?: AbortSignal,
): Promise<{
  ok: boolean
  statusCode?: number
  body: string
  error?: string
  aborted?: boolean
}>
```

**Key internal functions:**

| Function | Description |
|----------|-------------|
| `getSandboxProxyConfig()` | Gets sandbox network proxy (host:port) for routing requests through the sandbox when sandboxing is enabled |
| `getHttpHookPolicy()` | Reads `allowedHttpHookUrls` and `httpHookAllowedEnvVars` from merged settings |
| `urlMatchesPattern(url, pattern)` | Glob-style URL matching with `*` wildcard (same semantics as MCP allowlists) |
| `sanitizeHeaderValue(value)` | Strips CR, LF, NUL bytes to prevent HTTP header injection |
| `interpolateEnvVars(value, allowedEnvVars)` | Replaces `$VAR_NAME` and `${VAR_NAME}` patterns in header values, but only for allowlisted env vars |

**Security/SSRF:**
1. URL allowlist check against `allowedHttpHookUrls` from settings (``undefined = no restriction, `[]` = block all)
2. Header env var interpolation restricted to `hook.allowedEnvVars` intersected with policy-level `httpHookAllowedEnvVars`
3. `sanitizeHeaderValue()` prevents CRLF injection
4. Routes through sandbox proxy when sandboxing is active (proxy enforces domain allowlist itself)
5. Uses `ssrfGuardedLookup` for DNS resolution when no proxy is active — validates resolved IPs are not in private/link-local ranges
6. Default timeout: 10 minutes

### 1.4 `execPromptHook.ts` (211 lines)

**Exports:**

| Export | Kind | Description |
|--------|------|-------------|
| `execPromptHook(...)` | Async Function | Executes a prompt-based hook using a single LLM query |

**Signature:**

```typescript
async function execPromptHook(
  hook: PromptHook,
  hookName: string,
  hookEvent: HookEvent,
  jsonInput: string,
  signal: AbortSignal,
  toolUseContext: ToolUseContext,
  messages?: Message[],
  toolUseID?: string,
): Promise<HookResult>
```

**Behavior:**
1. Replaces `$ARGUMENTS` in `hook.prompt` with `jsonInput`
2. Creates a user message (bypasses `processUserInput` to avoid recursion)
3. Optionally prepends conversation history (`messages`) to the query
4. Makes a single non-streaming LLM query via `queryModelWithoutStreaming` with Haiku (default model) and a system prompt instructing JSON output
5. Expects response matching `hookResponseSchema()` — `{ok: boolean, reason?: string}`
6. Default timeout: 30 seconds
7. Returns `'success'`, `'blocking'` (with `preventContinuation: true`), `'cancelled'`, or `'non_blocking_error'`

### 1.5 `fileChangedWatcher.ts` (191 lines)

**Exports:**

| Export | Kind | Description |
|--------|------|-------------|
| `setEnvHookNotifier(cb)` | Function | Sets a callback for displaying hook output to user |
| `initializeFileChangedWatcher(cwd)` | Function | Initializes chokidar watcher for FileChanged/CwdChanged hooks |
| `updateWatchPaths(paths)` | Function | Dynamically updates watch paths based on hook output |
| `onCwdChangedForHooks(oldCwd, newCwd)` | Async Function | Handles CWD change: re-evaluates hooks, executes CwdChanged hooks, restarts watcher |
| `resetFileChangedWatcherForTesting()` | Function | Resets all state for testing |

**Architecture:**
- Uses chokidar `FSWatcher` to monitor files for `FileChanged` events
- `resolveWatchPaths()` combines static matcher paths (from hook config's `matcher` field, pipe-separated filenames) with dynamic paths returned by hook output
- Starts watching with `awaitWriteFinish` stability threshold (500ms) and `ignorePermissionErrors`
- On file change/add/unlink, calls `executeFileChangedHooks()` from `../hooks.js`
- Dynamic paths from hook output are merged and watcher is restarted
- `onCwdChangedForHooks` handles directory changes: clears env files, executes `CwdChanged` hooks, updates dynamic paths, re-resolves matcher paths against new CWD
- All hook output/errors are routed through `notifyCallback` for user-facing display

### 1.6 `hookEvents.ts` (192 lines)

**Exports:**

| Export | Kind | Description |
|--------|------|-------------|
| `HookStartedEvent` | Type | `{type: 'started', hookId, hookName, hookEvent}` |
| `HookProgressEvent` | Type | `{type: 'progress', hookId, hookName, hookEvent, stdout, stderr, output}` |
| `HookResponseEvent` | Type | `{type: 'response', hookId, hookName, hookEvent, output, stdout, stderr, exitCode?, outcome}` |
| `HookExecutionEvent` | Type | Union of started/progress/response events |
| `HookEventHandler` | Type | `(event: HookExecutionEvent) => void` |
| `registerHookEventHandler(handler)` | Function | Registers the singleton event handler; drains pending queue on registration |
| `emitHookStarted(hookId, hookName, hookEvent)` | Function | Emits a started event (if emission is enabled) |
| `emitHookProgress({...})` | Function | Emits a progress event (if emission is enabled) |
| `startHookProgressInterval({...})` | Function | Starts a polling interval that emits progress events; returns stop function |
| `emitHookResponse({...})` | Function | Emits a response event with outcome |
| `setAllHookEventsEnabled(enabled)` | Function | Enables/disables emission of all hook events (beyond `SessionStart` and `Setup`) |
| `clearHookEventState()` | Function | Resets all event state for testing |

**Architecture:**
- Singleton event handler + pending event queue (max 100 events)
- `ALWAYS_EMITTED_HOOK_EVENTS = ['SessionStart', 'Setup']` — always emitted regardless of setting
- `shouldEmit()` checks if the event is always-emitted OR if `allHookEventsEnabled` is true AND event is in `HOOK_EVENTS`
- Progress interval defaults to 1 second polling, uses `interval.unref()` to not block process exit

### 1.7 `hookHelpers.ts` (83 lines)

**Exports:**

| Export | Kind | Description |
|--------|------|-------------|
| `hookResponseSchema` | Zod schema (lazy) | `{ok: boolean, reason?: string}` |
| `addArgumentsToPrompt(prompt, jsonInput)` | Function | Substitutes `$ARGUMENTS` / `$0`, `$1`, etc. with JSON input |
| `createStructuredOutputTool()` | Function | Creates a `Tool` object configured with hook response schema and prompt |
| `registerStructuredOutputEnforcement(...)` | Function | Registers a session-level stop function hook enforcing structured output via `SyntheticOutputTool` |

**Key details:**
- `hookResponseSchema` wraps `z.object(...)` inside `lazySchema()` for deferred evaluation
- `addArgumentsToPrompt` delegates to `substituteArguments` from `argumentSubstitution.ts`
- `createStructuredOutputTool` has a custom `prompt()` that instructs "call exactly once at end"

### 1.8 `hooksConfigManager.ts` (400 lines)

**Exports:**

| Export | Kind | Description |
|--------|------|-------------|
| `MatcherMetadata` | Type | `{fieldToMatch: string, values: string[]}` |
| `HookEventMetadata` | Type | `{summary, description, matcherMetadata?}` |
| `getHookEventMetadata(toolNames)` | Function | Memoized function returning metadata for all 26 HookEvents |
| `groupHooksByEventAndMatcher(appState, toolNames)` | Function | Groups all hooks (settings + registered/plugin) by event + matcher key |
| `getSortedMatchersForEvent(hooksByEventAndMatcher, event)` | Function | Returns sorted matcher keys for a given event |
| `getHooksForMatcher(hooksByEventAndMatcher, event, matcher)` | Function | Returns hooks for a specific event + matcher |
| `getMatcherMetadata(event, toolNames)` | Function | Gets matcher metadata for a specific event |

**HookEvent catalog (26 events):**

| Event | Description |
|-------|-------------|
| `PreToolUse` | Before tool execution, matched by `tool_name` |
| `PostToolUse` | After tool execution, matched by `tool_name` |
| `PostToolUseFailure` | After tool execution fails |
| `PermissionDenied` | After auto mode classifier denies a tool |
| `Notification` | When notifications are sent |
| `UserPromptSubmit` | When user submits a prompt |
| `SessionStart` | New session started (startup/resume/clear/compact) |
| `Stop` | Right before Claude concludes its response |
| `StopFailure` | When turn ends due to API error |
| `SubagentStart` | When a subagent is started |
| `SubagentStop` | Before a subagent concludes its response |
| `PreCompact` | Before conversation compaction |
| `PostCompact` | After conversation compaction |
| `SessionEnd` | When session is ending |
| `PermissionRequest` | When a permission dialog is displayed |
| `Setup` | Repo setup hooks (init/maintenance) |
| `TeammateIdle` | When a teammate is about to go idle |
| `TaskCreated` | When a task is created |
| `TaskCompleted` | When a task is completed |
| `Elicitation` | When MCP server requests user input |
| `ElicitationResult` | After user responds to MCP elicitation |
| `ConfigChange` | When configuration files change |
| `InstructionsLoaded` | When CLAUDE.md or rule is loaded |
| `WorktreeCreate` | Create isolated worktree |
| `WorktreeRemove` | Remove previously created worktree |
| `CwdChanged` | After working directory changes |
| `FileChanged` | When a watched file changes |

**Grouping logic:**
- Calls `getAllHooks(appState)` from `hooksSettings.ts` for file-based hooks
- Includes `getRegisteredHooks()` from `bootstrap/state.ts` for plugin hooks and built-in hooks (the latter only when `USER_TYPE === 'ant'`)
- Per-plugin hooks (detected by `'pluginRoot' in matcher`) are included; `HookCallbackMatcher` hooks (internal callbacks) are only included for Anthropic internal builds
- Matchers are sorted by source priority using `sortMatchersByPriority` (user > project > local > plugin/builtin)

### 1.9 `hooksConfigSnapshot.ts` (133 lines)

**Exports:**

| Export | Kind | Description |
|--------|------|-------------|
| `captureHooksConfigSnapshot()` | Function | Captures current hooks config at startup respecting `allowManagedHooksOnly` |
| `updateHooksConfigSnapshot()` | Function | Updates snapshot when hooks are modified at runtime; resets settings cache |
| `getHooksConfigFromSnapshot()` | Function | Returns cached snapshot (lazy-captures if null) |
| `resetHooksConfigSnapshot()` | Function | Resets snapshot + SDK init state for testing |
| `shouldAllowManagedHooksOnly()` | Function | Checks if only managed hooks should run |
| `shouldDisableAllHooksIncludingManaged()` | Function | Checks if ALL hooks (including managed) are disabled |

**Policy resolution chain (`getHooksFromAllowedSources`):**
1. If `policySettings.disableAllHooks === true` → return `{}`
2. If `policySettings.allowManagedHooksOnly === true` → return `policySettings.hooks`
3. If `isRestrictedToPluginOnly('hooks')` → return `policySettings.hooks` (blocks user/project/local)
4. Get merged settings; if `disableAllHooks === true` → return managed hooks only
5. Otherwise return merged hooks from all sources (backward compat)

### 1.10 `hooksSettings.ts` (271 lines)

**Exports:**

| Export | Kind | Description |
|--------|------|-------------|
| `HookSource` | Type | `'userSettings' | 'projectSettings' | 'localSettings' | 'policySettings' | 'pluginHook' | 'sessionHook' | 'builtinHook'` |
| `IndividualHookConfig` | Type | `{event, config, matcher?, source, pluginName?}` |
| `isHookEqual(a, b)` | Function | Deep comparison of two hooks (ignores timeout) |
| `getHookDisplayText(hook)` | Function | Returns human-readable display text for a hook |
| `getAllHooks(appState)` | Function | Collects all hooks from settings files + session hooks |
| `getHooksForEvent(appState, event)` | Function | Filters all hooks by event type |
| `hookSourceDescriptionDisplayString(source)` | Function | Returns human-readable source description |
| `hookSourceHeaderDisplayString(source)` | Function | Returns short header name for source |
| `hookSourceInlineDisplayString(source)` | Function | Returns inline label for source |
| `sortMatchersByPriority(matchers, hooksByEventAndMatcher, event)` | Function | Sorts matchers by source priority |

**Hook equality rules:**
- `command`: compares `command` string, `shell` (defaults to `DEFAULT_HOOK_SHELL`), and `if` condition
- `prompt`: compares `prompt` content and `if` condition
- `agent`: compares `prompt` content and `if` condition
- `http`: compares `url` and `if` condition
- `function`: always returns `false` (no stable identifier)

**Source file deduplication:**
- When collecting hooks from `userSettings`, `projectSettings`, `localSettings`, tracks resolved file paths to avoid duplicates (e.g., when CWD is home dir, userSettings and projectSettings both resolve to `~/.claude/settings.json`)

### 1.11 `postSamplingHooks.ts` (70 lines)

**Exports:**

| Export | Kind | Description |
|--------|------|-------------|
| `REPLHookContext` | Type | Context object passed to post-sampling hooks |
| `PostSamplingHook` | Type | `(context: REPLHookContext) => Promise<void> | void` |
| `registerPostSamplingHook(hook)` | Function | Registers a hook called after model sampling completes |
| `clearPostSamplingHooks()` | Function | Clears all registered hooks (testing) |
| `executePostSamplingHooks(...)` | Async Function | Executes all registered hooks in sequence |

**`REPLHookContext` type:**
```typescript
type REPLHookContext = {
  messages: Message[]
  systemPrompt: SystemPrompt
  userContext: { [k: string]: string }
  systemContext: { [k: string]: string }
  toolUseContext: ToolUseContext
  querySource?: QuerySource
}
```

Post-sampling hooks are **not** exposed via settings.json — they are programmatically registered hooks (used by skill improvement, prompt suggestion, etc.). Errors are caught and logged individually.

### 1.12 `registerFrontmatterHooks.ts` (67 lines)

**Exports:**

| Export | Kind | Description |
|--------|------|-------------|
| `registerFrontmatterHooks(...)` | Function | Registers hooks from agent/skill frontmatter as session-scoped hooks |

**Signature:**
```typescript
function registerFrontmatterHooks(
  setAppState: (updater: (prev: AppState) => AppState) => void,
  sessionId: string,
  hooks: HooksSettings,
  sourceName: string,
  isAgent: boolean = false,
): void
```

**Behavior:**
- Iterates all `HOOK_EVENTS` and registers each hook via `addSessionHook`
- For agents (`isAgent: true`), converts `Stop` events to `SubagentStop` (since subagents trigger `SubagentStop`, not `Stop`)
- Logs the count of registered hooks for debugging

### 1.13 `registerSkillHooks.ts` (64 lines)

**Exports:**

| Export | Kind | Description |
|--------|------|-------------|
| `registerSkillHooks(...)` | Function | Registers hooks from a skill's frontmatter as session hooks |

**Behavior:**
- Iterates all `HOOK_EVENTS`
- For `once: true` hooks, registers an `onHookSuccess` callback that automatically removes the hook after first successful execution via `removeSessionHook`
- Passes `skillRoot` for `CLAUDE_PLUGIN_ROOT` env var support

### 1.14 `sessionHooks.ts` (447 lines)

**Exports:**

| Export | Kind | Description |
|--------|------|-------------|
| `FunctionHookCallback` | Type | `(messages: Message[], signal?: AbortSignal) => boolean | Promise<boolean>` |
| `FunctionHook` | Type | `{type: 'function', id?, timeout?, callback, errorMessage, statusMessage?}` |
| `SessionStore` | Type | `{hooks: {[event in HookEvent]?: SessionHookMatcher[]}}` |
| `SessionHooksState` | Type | `Map<string, SessionStore>` — global hooks state in AppState |
| `addSessionHook(...)` | Function | Adds a command/prompt hook to session state |
| `addFunctionHook(...)` | Function | Adds a function hook (TS callback) to session state; returns hook ID |
| `removeFunctionHook(...)` | Function | Removes a function hook by ID |
| `removeSessionHook(...)` | Function | Removes a command/prompt hook by equality |
| `getSessionHooks(appState, sessionId, event?)` | Function | Gets session hooks (excluding function hooks) |
| `SessionDerivedHookMatcher` | Type | `{matcher, hooks, skillRoot?}` |
| `getSessionFunctionHooks(...)` | Function | Gets only function-type session hooks |
| `getSessionHookCallback(...)` | Function | Gets full hook entry (including callbacks) for a specific hook |
| `clearSessionHooks(...)` | Function | Clears all session hooks for a session |

**Why Map instead of Record for `SessionHooksState`:**
- Map's `.set()` and `.delete()` don't change the container's reference
- This means React's `Object.is(next, prev)` check short-circuits, preventing listener notification
- Critical under high concurrency: `parallel()` with N schema-mode agents fires N `addFunctionHook` calls synchronously; with Record + spread, each call is O(N) copy → O(N²) total; with Map, each is O(1)

**Function hooks:**
- Execute TypeScript callbacks in-memory for validation
- Cannot be persisted to settings.json (session-scoped only)
- Have optional `id` for targeted removal
- Default timeout: 5000ms

### 1.15 `skillImprovement.ts` (267 lines)

**Exports:**

| Export | Kind | Description |
|--------|------|-------------|
| `SkillUpdate` | Type | `{section, change, reason}` |
| `initSkillImprovement()` | Function | Entry point — registers post-sampling hook if feature flag + GrowthBook gate are enabled |
| `applySkillImprovement(skillName, updates)` | Async Function | Fire-and-forget: calls LLM to rewrite skill file with improvements |

**Architecture:**
- `createSkillImprovementHook()` builds an `ApiQueryHookConfig<SkillUpdate[]>` and creates a post-sampling hook via `createApiQueryHook`
- `shouldRun` checks: only on `repl_main_thread`, only if a project skill exists, only every `TURN_BATCH_SIZE` (5) user messages
- `buildMessages` crafts a prompt asking the LLM to detect user preferences and corrections from recent conversation that should be permanently added to the skill
- `parseResponse` extracts `<updates>` tags and parses JSON array
- `logResult` logs analytics and stores suggestions in `appState.skillImprovement`
- `applySkillImprovement` reads the skill file from `.claude/skills/<name>/SKILL.md`, sends to LLM with instructions to integrate improvements, writes back
- Guarded by `feature('SKILL_IMPROVEMENT')` and GrowthBook flag `tengu_copper_panda`

### 1.16 `ssrfGuard.ts` (294 lines)

**Exports:**

| Export | Kind | Description |
|--------|------|-------------|
| `isBlockedAddress(address)` | Function | Returns true if IP is in a blocked private/link-local range |
| `ssrfGuardedLookup(hostname, options, callback)` | Function | DNS lookup wrapper that validates resolved IPs, used as axios `lookup` option |

**Blocked IPv4 ranges:**
- `0.0.0.0/8` — "this" network
- `10.0.0.0/8` — private
- `100.64.0.0/10` — CGNAT (Alibaba cloud metadata at `100.100.100.200`)
- `169.254.0.0/16` — link-local (cloud metadata)
- `172.16.0.0/12` — private
- `192.168.0.0/16` — private

**Allowed:**
- `127.0.0.0/8` — loopback (local dev hooks)
- `::1` — loopback

**Blocked IPv6:**
- `::` — unspecified
- `fc00::/7` — unique local
- `fe80::/10` — link-local
- `::ffff:<v4>` — mapped IPv4 in a blocked range

**Key details:**
- `isBlockedV6` handles IPv4-mapped IPv6 addresses by extracting the embedded IPv4 and delegating to `isBlockedV4`
- `expandIPv6Groups` handles trailing dotted-decimal notation and `::` compression
- `ssrfError` returns an `ErrnoException` with `code: 'ERR_HTTP_HOOK_BLOCKED_ADDRESS'`
- Used as axios `lookup` option in `execHttpHook.ts` so the validated IP is the one the socket connects to (no TOCTOU / DNS rebinding window)
- Bypassed when sandbox proxy or env-var proxy is active (the proxy performs DNS)

### 1.17 `apiQueryHookHelper.ts` (141 lines)

**Exports:**

| Export | Kind | Description |
|--------|------|-------------|
| `ApiQueryHookContext` | Type | `REPLHookContext & { queryMessageCount?: number }` |
| `ApiQueryHookConfig<TResult>` | Type | Configuration object for creating an API query hook |
| `ApiQueryResult<TResult>` | Type | `{type: 'success', result, ...} | {type: 'error', error, ...}` |
| `createApiQueryHook<TResult>(config)` | Function | Factory function that creates a post-sampling hook |

**`ApiQueryHookConfig<TResult>` fields:**
```typescript
type ApiQueryHookConfig<TResult> = {
  name: QuerySource
  shouldRun: (context: ApiQueryHookContext) => Promise<boolean>
  buildMessages: (context: ApiQueryHookContext) => Message[]
  systemPrompt?: string
  useTools?: boolean          // defaults to true
  parseResponse: (content: string, context: ApiQueryHookContext) => TResult
  logResult: (result: ApiQueryResult<TResult>, context: ApiQueryHookContext) => void
  getModel: (context: ApiQueryHookContext) => string
}
```

**Behavior:**
1. Calls `config.shouldRun(context)` — if false, returns early
2. Builds messages via `config.buildMessages(context)`
3. Makes a non-streaming LLM query with `temperatureOverride: 0`
4. Calls `config.parseResponse(content, context)` on the response text
5. Calls `config.logResult(result, context)` — errors in parseResponse are caught and logged as error results
6. Outer errors are logged via `logError`

---

## Batch 2 — `utils/task/` (5 files, ~1,223 lines)

### 2.1 `TaskOutput.ts` (390 lines)

**Class: `TaskOutput`**

Single source of truth for a shell command's output, supporting two modes:

**File mode (bash):** stdout goes directly to a file via stdio fds — never enters JS. Progress is extracted by polling the file tail. `getStderr()` returns empty string (stderr is interleaved in output file).

**Pipe mode (hooks):** data flows through `writeStdout()`/`writeStderr()` and is buffered in memory, spilling to disk if exceeding 8MB limit.

**Key fields:**
- `#stdoutBuffer`, `#stderrBuffer`: in-memory buffers (pipe mode)
- `#disk: DiskTaskOutput | null`: disk spill target
- `#recentLines: CircularBuffer<string>`: last 1000 lines for progress
- `#totalLines`, `#totalBytes`: counters
- `#maxMemory`: default 8MB
- `#outputFileRedundant`: set after `getStdout()` when file was fully read and can be deleted

**Static poller:**
- `TaskOutput.#registry`: all file-mode instances with `onProgress` callbacks
- `TaskOutput.#activePolling`: currently being polled (React visibility-driven)
- `TaskOutput.#tick()`: shared interval (1s) that reads file tail (4KB) for every actively-polled task
- `startPolling(taskId)` / `stopPolling(taskId)`: managed by React useEffect

**Methods:**
| Method | Description |
|--------|-------------|
| `writeStdout(data)` | Write stdout (pipe mode only) |
| `writeStderr(data)` | Write stderr (always piped) |
| `getStdout()` | Async: reads from file (file mode) or returns in-memory/disk buffer (pipe mode) |
| `getStderr()` | Sync: returns stderr buffer (empty if on disk) |
| `spillToDisk()` | Force all buffered content to disk (called when backgrounding) |
| `flush()` | Flush disk writes |
| `deleteOutputFile()` | Unlink the output file |
| `clear()` | Clear all buffers, cancel progress, unregister |

### 2.2 `diskOutput.ts` (451 lines)

**Disk-backed task output storage with file-level and module-level APIs.**

**Constants:**
- `MAX_TASK_OUTPUT_BYTES = 5GB` — disk cap for output files
- `DEFAULT_MAX_READ_BYTES = 8MB`

**Class: `DiskTaskOutput`**

Encapsulates async disk writes for a single task using a flat write queue processed by a single drain loop. Uses `O_NOFOLLOW` to prevent symlink-following attacks (sandbox → host file write).

**Module-level exports:**

| Export | Kind | Description |
|--------|------|-------------|
| `getTaskOutputDir()` | Function | Returns session-scoped temp directory for task outputs |
| `getTaskOutputPath(taskId)` | Function | Returns full path: `<dir>/<taskId>.output` |
| `getTaskOutputDelta(taskId, fromOffset, maxBytes?)` | Async Function | Reads new content since last offset (incremental) |
| `getTaskOutput(taskId, maxBytes?)` | Async Function | Reads tail of output file |
| `getTaskOutputSize(taskId)` | Async Function | Returns file size via `stat` |
| `initTaskOutput(taskId)` | Async Function | Creates empty output file with `O_EXCL | O_NOFOLLOW` |
| `initTaskOutputAsSymlink(taskId, targetPath)` | Async Function | Creates symlink output file (for agent transcripts) |
| `appendTaskOutput(taskId, content)` | Async Function | Appends content to task's disk file |
| `flushTaskOutput(taskId)` | Async Function | Waits for pending writes to complete |
| `evictTaskOutput(taskId)` | Async Function | Flushes and removes from in-memory map (without deleting file) |
| `cleanupTaskOutput(taskId)` | Async Function | Cancels writes + deletes output file |
| `_resetTaskOutputDirForTest()` | Function | Clears memoized dir for testing |
| `_clearOutputsForTest()` | Async Function | Cancels all, drains pending ops, clears map |

**Session-scoped directory:**
- Path: `<projectTempDir>/<sessionId>/tasks/`
- Session ID captured at first call, cached — survives `/clear` (which regenerates session ID) so background tasks' output files stay reachable
- This prevents cross-session clobbering and ENOENT errors from startup cleanup

### 2.3 `framework.ts` (308 lines)

**Task lifecycle management in AppState.**

**Constants:**
- `POLL_INTERVAL_MS = 1000`
- `STOPPED_DISPLAY_MS = 3000`
- `PANEL_GRACE_MS = 30000`

**Exports:**

| Export | Kind | Description |
|--------|------|-------------|
| `TaskAttachment` | Type | `{type: 'task_status', taskId, toolUseId?, taskType, status, description, deltaSummary}` |
| `updateTaskState(taskId, setAppState, updater)` | Function | Type-safe state updater for a specific task |
| `registerTask(task, setAppState)` | Function | Registers new task in AppState; emits SDK `task_started` event |
| `evictTerminalTask(taskId, setAppState)` | Function | Eagerly evicts terminal (completed/failed/killed) tasks |
| `getRunningTasks(state)` | Function | Returns all tasks with `status === 'running'` |
| `generateTaskAttachments(state)` | Async Function | Polls running tasks for new output + evicts terminal tasks |
| `applyTaskOffsetsAndEvictions(setAppState, offsets, evictions)` | Function | Applies offset patches and task evictions (TOCTOU-safe) |
| `pollTasks(getAppState, setAppState)` | Async Function | Main polling loop: generate + apply + notify |

**Key patterns:**
- `registerTask` carries forward UI-held state (`retain`, `messages`, `diskLoaded`) on re-registration (resume)
- `evictTerminalTask` respects panel grace period (`evictAfter`) for `LocalAgentTaskState`
- `generateTaskAttachments` only reads delta for running tasks; completed tasks get evicted, not double-notified
- `applyTaskOffsetsAndEvictions` merges patches against **fresh** `prev.tasks` to avoid TOCTOU (stale snapshots from async disk reads)
- `enqueueTaskNotification` formats XML with `<task_notification>`, `<task_id>`, `<tool_use_id>`, `<task_type>`, `<output_file>`, `<status>`, `<summary>` tags

### 2.4 `outputFormatting.ts` (38 lines)

**Exports:**

| Export | Kind | Description |
|--------|------|-------------|
| `TASK_MAX_OUTPUT_UPPER_LIMIT` | Constant | 160,000 characters |
| `TASK_MAX_OUTPUT_DEFAULT` | Constant | 32,000 characters |
| `getMaxTaskOutputLength()` | Function | Reads `TASK_MAX_OUTPUT_LENGTH` env var, bounded by upper limit |
| `formatTaskOutput(output, taskId)` | Function | Truncates output with header indicating file path if too large |

### 2.5 `sdkProgress.ts` (36 lines)

**Exports:**

| Export | Kind | Description |
|--------|------|-------------|
| `emitTaskProgress(params)` | Function | Emits a `task_progress` SDK event via `enqueueSdkEvent` |

**Parameters:**
```typescript
{
  taskId: string
  toolUseId: string | undefined
  description: string
  startTime: number
  totalTokens: number
  toolUses: number
  lastToolName?: string
  summary?: string
  workflowProgress?: SdkWorkflowProgress[]
}
```

Emits `{type: 'system', subtype: 'task_progress', ...}` with `usage.calc` (total_tokens, tool_uses, duration_ms).

---

## Batch 3 — `utils/teleport/` (4 files, ~955 lines)

The teleport system enables cross-session file transfer and remote session management for Claude Code web sessions (CCR).

### 3.1 `api.ts` (466 lines)

**Exports:**

| Export | Kind | Description |
|--------|------|-------------|
| `CCR_BYOC_BETA` | Constant | `'ccr-byoc-2025-07-29'` beta header value |
| `isTransientNetworkError(error)` | Function | Checks if axios error is a 5xx or network error (eligible for retry) |
| `axiosGetWithRetry<T>(url, config?)` | Async Function | GET with exponential backoff retry (2s, 4s, 8s, 16s — 4 retries) |
| `SessionStatus` | Type | `'requires_action' | 'running' | 'idle' | 'archived'` |
| `GitSource` | Type | `{type: 'git_repository', url, revision?, allow_unrestricted_git_push?}` |
| `KnowledgeBaseSource` | Type | `{type: 'knowledge_base', knowledge_base_id}` |
| `SessionContextSource` | Type | `GitSource | KnowledgeBaseSource` |
| `OutcomeGitInfo` | Type | `{type: 'github', repo, branches}` |
| `GitRepositoryOutcome` | Type | `{type: 'git_repository', git_info}` |
| `SessionContext` | Type | Full session context with sources, cwd, outcomes, prompts, model, bundle, PR info |
| `SessionResource` | Type | API session resource with id, title, status, environment_id, timestamps, context |
| `ListSessionsResponse` | Type | `{data: SessionResource[], has_more, first_id, last_id}` |
| `CodeSessionSchema` | Zod schema (lazy) | Schema for code sessions returned to UI |
| `CodeSession` | Type | Inferred from schema |
| `prepareApiRequest()` | Async Function | Validates auth and returns `{accessToken, orgUUID}` |
| `fetchCodeSessionsFromSessionsAPI()` | Async Function | Fetches sessions from `/v1/sessions`, transforms to `CodeSession[]` |
| `getOAuthHeaders(accessToken)` | Function | Returns OAuth headers (Authorization, Content-Type, anthropic-version) |
| `fetchSession(sessionId)` | Async Function | Fetches single session by ID (handles 404, 401, other errors) |
| `getBranchFromSession(session)` | Function | Extracts first branch name from session's git outcomes |
| `RemoteMessageContent` | Type | `string | Array<{type, ...}>` — content for remote messages |
| `sendEventToRemoteSession(sessionId, content, opts?)` | Async Function | Sends user message event to remote session via `/v1/sessions/<id>/events` |
| `updateSessionTitle(sessionId, title)` | Async Function | Updates session title via PATCH `/v1/sessions/<id>` |

**Error handling:** All API calls use `anthropic-beta: ccr-byoc-2025-07-29` header and `x-organization-uuid`. The `sendEventToRemoteSession` and `updateSessionTitle` functions return `boolean` (never throw).

### 3.2 `environments.ts` (120 lines)

**Exports:**

| Export | Kind | Description |
|--------|------|-------------|
| `EnvironmentKind` | Type | `'anthropic_cloud' | 'byoc' | 'bridge'` |
| `EnvironmentState` | Type | `'active'` |
| `EnvironmentResource` | Type | `{kind, environment_id, name, created_at, state}` |
| `EnvironmentListResponse` | Type | `{environments[], has_more, first_id, last_id}` |
| `fetchEnvironments()` | Async Function | Fetches available environments from `/v1/environment_providers` |
| `createDefaultCloudEnvironment(name)` | Async Function | Creates a default `anthropic_cloud` environment via `/v1/environment_providers/cloud/create` |

### 3.3 `environmentSelection.ts` (77 lines)

**Exports:**

| Export | Kind | Description |
|--------|------|-------------|
| `EnvironmentSelectionInfo` | Type | `{availableEnvironments, selectedEnvironment, selectedEnvironmentSource}` |
| `getEnvironmentSelectionInfo()` | Async Function | Returns available environments and which one is currently selected |

**Selection logic:**
1. Fetches all environments from API
2. Checks merged settings for `remote.defaultEnvironmentId`
3. If set, finds matching environment and identifies which `SettingSource` defines it (iterates from highest to lowest priority)
4. Falls back to first non-bridge environment (or first available) if no setting
5. Returns the selection info for SettingsUI display

### 3.4 `gitBundle.ts` (292 lines)

**Git bundle creation + upload for CCR seed-bundle seeding.**

**Flow:** `git stash create` → `update-ref refs/seed/stash` → `git bundle create --all` (with `HEAD` and `squashed-root` fallbacks) → upload to `/v1/files` → cleanup refs.

**Exports:**

| Export | Kind | Description |
|--------|------|-------------|
| `BundleUploadResult` | Type | `{success: true, fileId, bundleSizeBytes, scope, hasWip} | {success: false, error, failReason?}` |
| `BundleScope` | Type | `'all' | 'head' | 'squashed'` |
| `BundleFailReason` | Type | `'git_error' | 'too_large' | 'empty_repo'` |
| `createAndUploadGitBundle(config, opts?)` | Async Function | Main entry point: creates bundle, uploads, returns result |

**Bundle fallback chain (`_bundleWithFallback`):**
1. `git bundle create --all` — full repo, all refs
2. If > 100MB: `git bundle create HEAD` — current branch only
3. If still > 100MB: `git commit-tree HEAD^{tree}` → squashed single-parentless commit → `git bundle create refs/seed/root`
4. If still > 100MB: fail with `'too_large'`

**Stash handling:**
- `git stash create` creates a dangling commit (doesn't touch `refs/stash` or working tree)
- Made reachable via `refs/seed/stash` so bundle includes it
- Squashed root uses `refs/seed/stash^{tree}` when WIP exists (bakes uncommitted changes in)
- Cleanup: `update-ref -d refs/seed/stash` and `refs/seed/root` in `finally` block

**Empty repo check:** Uses `git for-each-ref --count=1 refs/` before attempting bundle creation.

---

## Batch 4 — Background, Skills, GitHub, Shared Tools

### 4.1 `utils/background/remote/remoteSession.ts` (98 lines)

**Exports:**

| Export | Kind | Description |
|--------|------|-------------|
| `BackgroundRemoteSession` | Type | `{id, command, startTime, status, todoList, title, type: 'remote_session', log}` |
| `BackgroundRemoteSessionPrecondition` | Type | Union of precondition failure types |
| `checkBackgroundRemoteSessionEligibility({skipBundle?})` | Async Function | Checks all preconditions for creating a background remote session |

**Precondition checks (in order):**
1. Policy: `isPolicyAllowed('allow_remote_sessions')`
2. Auth: `checkNeedsClaudeAiLogin()`
3. Environment: `checkHasRemoteEnvironment()`
4. Repository: `checkIsInGitRepo()` then:
   - If bundle seed gate on (env var `CCR_FORCE_BUNDLE`/`CCR_ENABLE_BUNDLE` or GrowthBook `tengu_ccr_bundle_seed_enabled`): skip remote checks
   - If no git remote: `'no_git_remote'`
   - If GitHub: `checkGithubAppInstalled(owner, name)`

### 4.2 `utils/background/remote/preconditions.ts` (235 lines)

**Exports:**

| Export | Kind | Description |
|--------|------|-------------|
| `checkNeedsClaudeAiLogin()` | Async Function | Returns true if OAuth token needs refresh |
| `checkIsGitClean()` | Async Function | Returns true if working tree is clean (ignores untracked) |
| `checkHasRemoteEnvironment()` | Async Function | Returns true if user has ≥1 remote environment |
| `checkIsInGitRepo()` | Function | Returns true if CWD has `.git/` directory |
| `checkHasGitRemote()` | Async Function | Returns true if repo has a remote configured |
| `checkGithubAppInstalled(owner, repo, signal?)` | Async Function | Checks GitHub app installation via `/api/oauth/organizations/.../code/repos/...` |
| `checkGithubTokenSynced()` | Async Function | Checks if user has synced GitHub credentials via `/web-setup` |
| `checkRepoForRemoteAccess(owner, repo)` | Async Function | Tiered check: GitHub app → token sync → `'none'` |
| `RepoAccessMethod` | Type | `'github-app' | 'token-sync' | 'none'` |

### 4.3 `utils/skills/skillChangeDetector.ts` (311 lines)

**File watcher for skill/command directories.** Uses chokidar to monitor `.claude/skills/` and `.claude/commands/` directories at user and project levels.

**Exports:**

| Export | Kind | Description |
|--------|------|-------------|
| `skillChangeDetector` | Object | `{initialize, dispose, subscribe: skillsChanged.subscribe, resetForTesting}` |
| `initialize()` | Async Function | Sets up watchers for skill/command directories |
| `dispose()` | Async Function | Cleanup watcher, timers, signal |
| `subscribe` | Function | Subscribe to `skillsChanged` signal |
| `resetForTesting(overrides?)` | Async Function | Clean + reset state with optional timing overrides |

**Architecture:**
- Watches up to 4 base directories + additional `--add-dir` skills paths
- Depth: 2 (matches `skill-name/SKILL.md` format)
- `awaitWriteFinish` stability: 1s threshold, 500ms poll
- Uses stat() polling under Bun (workaround for `oven-sh/bun#27469` deadlock)
- Ignores `.git` directories and non-regular/non-directory file types
- **Debounces** rapid changes into single reload (300ms) to prevent cascading reload cycles
- On debounce fire: executes `ConfigChange` hooks (blocking check), then `clearSkillCaches()`, `clearCommandsCache()`, `resetSentSkillNames()`, `skillsChanged.emit()`
- Registers cleanup for graceful shutdown

### 4.4 `utils/github/ghAuthStatus.ts` (29 lines)

**Exports:**

| Export | Kind | Description |
|--------|------|-------------|
| `GhAuthStatus` | Type | `'authenticated' | 'not_authenticated' | 'not_installed'` |
| `getGhAuthStatus()` | Async Function | Returns gh CLI install + auth status |

**Implementation:**
- Uses `which('gh')` (Bun.which) first — no subprocess
- Then runs `gh auth token` with `stdout: 'ignore'` (token never enters process)
- Exit code 0 = authenticated, non-zero = not authenticated

### 4.5 `tools/shared/spawnMultiAgent.ts` (1,093 lines)

**Shared spawn module for teammate creation** — used by both `TeammateTool` and `AgentTool`.

**Exports:**

| Export | Kind | Description |
|--------|------|-------------|
| `SpawnOutput` | Type | Full spawn result with teammate_id, agent_id, model, name, color, tmux info, team info |
| `SpawnTeammateConfig` | Type | Input config: name, prompt, team_name, cwd, model, agent_type, etc. |
| `resolveTeammateModel(inputModel, leaderModel)` | Function | Resolves model with 'inherit' → leader model fallback |
| `generateUniqueTeammateName(baseName, teamName)` | Async Function | Appends numeric suffix if name exists in team |
| `spawnTeammate(config, context)` | Async Function | Main entry point — delegates to `handleSpawn` |

**Three spawn strategies (attempted in order):**
1. **In-process** (`handleSpawnInProcess`): Runs teammate in same Node.js process using AsyncLocalStorage (when `isInProcessEnabled()`)
2. **Split-pane** (`handleSpawnSplitPane`): Default — creates teammate in shared tmux window or iTerm2 split pane
3. **Separate window** (`handleSpawnSeparateWindow`): Legacy — each teammate in its own tmux window

**Common spawn flow:**
1. Resolve model (`'inherit'` → leader's model)
2. Get/create team context
3. Generate unique name + sanitize agent name (prevent `@` in IDs)
4. Format deterministic agent ID: `{name}@{teamName}`
5. Assign teammate color
6. Build CLI args with identity flags (`--agent-id`, `--agent-name`, `--team-name`, etc.)
7. Build inherited CLI flags (permission mode, model, settings, plugins, chrome)
8. Register background task (`InProcessTeammateTaskState`)
9. Register in team file
10. Send initial prompt via mailbox (tmux) or directly (in-process)

**iTerm2 setup:**
- When detecting iTerm2 without it2 CLI, shows `It2SetupPrompt` JSX to user
- Can install it2 or fall back to tmux; caches decision

### 4.6 `tools/shared/gitOperationTracking.ts` (277 lines)

**Shell-agnostic git operation detection for usage metrics.**

**Exports:**

| Export | Kind | Description |
|--------|------|-------------|
| `CommitKind` | Type | `'committed' | 'amended' | 'cherry-picked'` |
| `BranchAction` | Type | `'merged' | 'rebased'` |
| `PrAction` | Type | `'created' | 'edited' | 'merged' | 'commented' | 'closed' | 'ready'` |
| `parseGitCommitId(stdout)` | Function | Extracts SHA from git commit output |
| `detectGitOperation(command, output)` | Function | Scans command + output for git/gh operations |
| `trackGitOperations(command, exitCode, stdout?)` | Function | Logs analytics events + increments OTLP counters |

**Detected operations:**
- `git commit` (including `--amend`) — extracts SHA
- `git push` — extracts branch name from ref update line
- `git cherry-pick` — extracts SHA
- `git merge` — extracts target ref, checks for "Fast-forward" or "Merge made by"
- `git rebase` — extracts target ref, checks for "Successfully rebased"
- `gh pr create/edit/merge/comment/close/ready` — extracts PR URL or number
- `glab mr create` — GitLab MR creation
- `curl` POST to PR endpoints — detects REST API PR creation

### 4.7 `tools/testing/TestingPermissionTool.tsx` (74 lines)

**Testing-only tool** that always pops a permission dialog. Enabled only when `"production" === 'test'`. Always returns `{behavior: 'ask', message: 'Run test?'}` from `checkPermissions`. Returns `"TestingPermission executed successfully"` on call. All render methods return `null`.

### 4.8 `tools/McpAuthTool/McpAuthTool.ts` (215 lines)

**Creates a pseudo-tool for MCP servers needing OAuth authentication.**

**Exports:**

| Export | Kind | Description |
|--------|------|-------------|
| `McpAuthOutput` | Type | `{status: 'auth_url' | 'unsupported' | 'error', message, authUrl?}` |
| `createMcpAuthTool(serverName, config)` | Function | Creates a Tool for OAuth initiation |

**Behavior:**
1. Surfaced in place of a server's real tools when the server is installed but not authenticated
2. Named `mcp__<serverName>__authenticate`
3. On call:
   - `claudeai-proxy` transport → returns unsupported (user should run `/mcp`)
   - Non-SSE/HTTP transports → returns unsupported
   - SSE/HTTP → starts `performMCPOAuthFlow` with `skipBrowserOpen: true`
   - Captures auth URL via callback; races it with the flow promise (silent auth possible)
   - Background: on OAuth completion, clears auth cache, reconnects MCP, swaps real tools into `appState.mcp.tools` (prefix-based removal of this pseudo-tool)

### 4.9 `tools/SyntheticOutputTool/SyntheticOutputTool.ts` (163 lines)

**Structured output enforcement tool for non-interactive sessions.**

**Exports:**

| Export | Kind | Description |
|--------|------|-------------|
| `SYNTHETIC_OUTPUT_TOOL_NAME` | Constant | `'StructuredOutput'` |
| `Output` | Type | Inferred string output schema |
| `isSyntheticOutputToolEnabled(opts)` | Function | Returns true if `isNonInteractiveSession` |
| `SyntheticOutputTool` | Tool | Base tool (open schema, `{}.passthrough()`) |
| `createSyntheticOutputTool(jsonSchema)` | Function | Creates a tool with custom JSON schema validation (uses Ajv) |

**Key details:**
- `inputSchema`: `z.object({}).passthrough()` — accepts any object
- Always enabled once created, always read-only, not open-world
- `call()` returns `{data, structured_output}` — validates against schema when created via `createSyntheticOutputTool`
- `createSyntheticOutputTool` uses WeakMap cache on schema object identity to avoid recompilation (~1.4ms Ajv overhead each, 80-call workflows: 110ms → 4ms)
- Error messages are `TelemetrySafeError` instances

---

## Batch 5 — `services/tips/` (3 files, ~761 lines)

Contextual tip display system shown during idle time (spinner/loading).

### 5.1 `tipHistory.ts` (17 lines)

**Exports:**

| Export | Kind | Description |
|--------|------|-------------|
| `recordTipShown(tipId)` | Function | Records that a tip was shown in the current startup session |
| `getSessionsSinceLastShown(tipId)` | Function | Returns number of sessions since tip was last shown; `Infinity` if never shown |

**Storage:** Uses `getGlobalConfig().tipsHistory` — persists across sessions.

### 5.2 `tipRegistry.ts` (686 lines)

**Exports:**

| Export | Kind | Description |
|--------|------|-------------|
| `getRelevantTips(context?)` | Async Function | Returns all relevant tips after filtering |

**Tip structure:**
```typescript
type Tip = {
  id: string
  content: (context?: TipContext) => Promise<string>
  cooldownSessions: number   // minimum sessions between shows
  isRelevant: (context?: TipContext) => Promise<boolean>
}
```

**Tip categories (43 built-in tips):**

| Category | Tips |
|----------|------|
| **New user** | `new-user-warmup`, `plan-mode-for-complex-tasks`, `default-permission-mode-config` |
| **Session management** | `git-worktrees`, `color-when-multi-clauding`, `rename-conversation`, `continue`, `double-esc`, `double-esc-code-restore` |
| **Terminal/IDE** | `terminal-setup`, `shift-enter`, `shift-enter-setup`, `vscode-command-install`, `ide-upsell-external-terminal` |
| **Commands** | `memory-command`, `theme-command`, `status-line`, `todo-list`, `custom-commands`, `custom-agents`, `agent-flag`, `feedback-command` |
| **Permissions** | `permissions` |
| **Input** | `prompt-queue`, `enter-to-steer-in-relatime`, `drag-and-drop-images`, `paste-images-mac`, `image-paste`, `shift-tab` |
| **App integration** | `desktop-app`, `desktop-shortcut`, `web-app`, `mobile-app` |
| **GitHub/Slack** | `install-github-app`, `install-slack-app` |
| **Plugins** | `frontend-design-plugin`, `vercel-plugin` |
| **Features** | `effort-high-nudge`, `subagent-fanout-nudge`, `loop-command-nudge`, `opusplan-mode-reminder` |
| **Social** | `guest-passes`, `overage-credit` |
| **Admin-only** | `important-claudemd`, `skillify` |
| **Platform** | `powershell-tool-env`, `colorterm-truecolor` |

**Custom tips:** Can be configured via `settings.spinnerTipsOverride.tips`. `excludeDefault: true` skips all built-in tips. Custom tips have `cooldownSessions: 0` and are always relevant.

**Filtering pipeline:**
1. If custom tips exist and `excludeDefault` → return only custom tips
2. Otherwise: filter built-in tips by `isRelevant()`, then by `cooldownSessions` (via `getSessionsSinceLastShown`)

### 5.3 `tipScheduler.ts` (58 lines)

**Exports:**

| Export | Kind | Description |
|--------|------|-------------|
| `selectTipWithLongestTimeSinceShown(tips)` | Function | Selects the tip that hasn't been shown for the most sessions |
| `getTipToShowOnSpinner(context?)` | Async Function | Main entry point: returns a tip to show, or undefined if disabled |
| `recordShownTip(tip)` | Function | Records tip shown in history + logs analytics event |

**Selection algorithm:** Picks the tip with the longest time since last shown (max of `getSessionsSinceLastShown`).

---

## Batch 6 — `services/PromptSuggestion/` (2 files, ~1,514 lines)

Prompt suggestion and speculation system — predicts what the user might type next and speculatively executes it.

### 6.1 `promptSuggestion.ts` (523 lines)

**Exports:**

| Export | Kind | Description |
|--------|------|-------------|
| `PromptVariant` | Type | `'user_intent' | 'stated_intent'` |
| `getPromptVariant()` | Function | Returns `'user_intent'` |
| `shouldEnablePromptSuggestion()` | Function | Checks env var, GrowthBook gate, non-interactive mode, swarm teammate, settings |
| `abortPromptSuggestion()` | Function | Aborts any in-flight suggestion generation |
| `getSuggestionSuppressReason(appState)` | Function | Returns suppression reason string or null if generation allowed |
| `tryGenerateSuggestion(abortController, messages, getAppState, cacheSafeParams, source?)` | Async Function | Shared guard + generation logic |
| `executePromptSuggestion(context)` | Async Function | Post-sampling hook entry point for CLI TUI |
| `getParentCacheSuppressReason(lastAssistantMessage)` | Function | Checks if parent response exceeds 10K uncached tokens (cache cold) |
| `generateSuggestion(abortController, promptId, cacheSafeParams)` | Async Function | Forks the conversation with the suggestion prompt |
| `shouldFilterSuggestion(suggestion, promptId, source?)` | Function | Applies 10+ filters to reject bad suggestions |
| `logSuggestionOutcome(suggestion, userInput, emittedAt, promptId, generationRequestId)` | Function | Logs acceptance/ignoring |
| `logSuggestionSuppressed(reason, suggestion?, promptId?, source?)` | Function | Logs suppression events |

**Gate chain (`shouldEnablePromptSuggestion`):**
1. Env var `CLAUDE_CODE_ENABLE_PROMPT_SUGGESTION` — override everything
2. GrowthBook flag `tengu_chomp_inflection` — feature gate
3. Non-interactive session → disable
4. Swarm teammate → disable (only leader shows suggestions)
5. Settings `promptSuggestionEnabled` — default true

**Suppression reasons (`getSuggestionSuppressReason`):**
- `'disabled'` — promptSuggestionEnabled turned off
- `'pending_permission'` — worker/sandbox request pending
- `'elicitation_active'` — MCP elicitation dialog open
- `'plan_mode'` — in plan mode
- `'rate_limit'` — external user over limit

**Generation pipeline (`tryGenerateSuggestion`):**
1. Check abort, assistant turn count ≥ 2, no API error in last message
2. Check parent cache suppression (output + cache writes > 10K tokens)
3. Check app state suppress reason
4. Call `generateSuggestion()` via `runForkedAgent` with `skipCacheWrite: true`
5. Filter result through `shouldFilterSuggestion`
6. Return `{suggestion, promptId, generationRequestId}`

**Cache preservation:**
- Fork piggybacks on main thread's prompt cache by sending identical cache-key params
- Only safe overrides: `abortController`, `skipTranscript`, `skipCacheWrite`, `canUseTool`
- Setting `effort:'low'` or `maxOutputTokens` on the fork was shown to cause a 45× spike in cache writes (92.7% → 61% hit rate)

**Suggestion filters (in `shouldFilterSuggestion`):**
| Filter | Description |
|--------|-------------|
| `empty` | Null/undefined suggestion |
| `done` | Exactly "done" |
| `meta_text` | "nothing found", "no suggestion", "silence" etc. |
| `meta_wrapped` | Meta-reasoning in parens/brackets |
| `error_message` | API error strings |
| `prefixed_label` | Starts with `word:` |
| `too_few_words` | Single word not in allowlist |
| `too_many_words` | > 12 words |
| `too_long` | ≥ 100 characters |
| `multiple_sentences` | Multiple sentences |
| `has_formatting` | Contains `\n`, `*`, or `**` |
| `evaluative` | "thanks", "looks good", etc. |
| `claude_voice` | "let me", "i'll", "here's", etc. |

### 6.2 `speculation.ts` (991 lines)

**Speculative execution system** — after generating a suggestion, Claude Code speculatively executes it in an isolated fork. If the user types exactly the suggested text, the speculated work is committed instantly.

**Exports:**

| Export | Kind | Description |
|--------|------|-------------|
| `ActiveSpeculationState` | Type | Extract of `SpeculationState` with `status: 'active'` |
| `isSpeculationEnabled()` | Function | Returns true for `USER_TYPE === 'ant'` with `speculationEnabled` default true |
| `startSpeculation(suggestionText, context, setAppState, isPipelined?, cacheSafeParams?)` | Async Function | Starts speculative execution in an isolated fork |
| `acceptSpeculation(state, setAppState, cleanMessageCount)` | Async Function | Accepts speculation: copies overlay, returns result |
| `abortSpeculation(setAppState)` | Function | Aborts current speculation |
| `handleSpeculationAccept(speculationState, sessionTimeSaved, setAppState, input, deps)` | Async Function | Full accept flow: inject messages, apply overlay, promote pipelined suggestion |
| `prepareMessagesForInjection(messages)` | Function | Strips failed/incomplete tool uses, thinking blocks, interrupt messages |

**Isolation mechanism:**
1. Creates overlay directory at `<claudeTempDir>/speculation/<pid>/<id>`
2. Files written during speculation are redirected to overlay (copy-on-write)
3. Reads check overlay first, then main filesystem
4. On accept: `copyOverlayToMain` copies all written files back

**Tool permission boundaries:**
| Tool | Allowed? | Notes |
|------|----------|-------|
| Read/Glob/Grep/ToolSearch/LSP/TaskGet/TaskList | Yes | Read-only tools, redirect to overlay if needed |
| Edit/Write/NotebookEdit | Conditional | Allowed only in `acceptEdits`, `bypassPermissions`, or plan-with-bypass modes; stops at edit boundary otherwise |
| Bash (read-only) | Yes | Uses `checkReadOnlyConstraints` |
| Bash (non-read-only) | No | Stops at bash boundary |
| All other tools | No | Stops at denied tool boundary |
| Write outside CWD | No | Denied |

**Speculation lifecycle:**
1. `startSpeculation`: creates overlay, forks agent with `runForkedAgent`
2. Tracks tool results via `onMessage` callback, updates `activeSpeculationState`
3. When complete: sets `boundary: {type: 'complete', ...}`
4. On complete: fires pipelined suggestion generation (`generatePipelinedSuggestion`)
5. `acceptSpeculation`: aborts fork, copies overlay, returns `{messages, boundary, timeSavedMs}`
6. `handleSpeculationAccept`: full flow — clears prompt suggestion, injects user message + speculated messages, merges file state cache, promotes pipelined suggestion

**Speculation analytics:**
- Logs `tengu_speculation` events with outcome (`accepted`/`aborted`/`error`), duration, tool count, boundary type, pipelining status
- Log `tengu_skill_improvement_detected` for skill improvement outcomes
- Writes `speculation-accept` entries to transcript when time was saved

**ANT-only features:**
- Speculation feedback message: `"[ANT-ONLY] Speculated N tool uses +M tokens saved"`
- Content logging in suppression/outcome events
- Pipelined suggestion generation

---

## Cross-system Relationships

```
Hooks System ──────────────────────────────────────────────────
  hooksConfigManager.ts ← hooksSettings.ts ← sessionHooks.ts
       ↓                    ↓                        ↓
  hooksConfigSnapshot.ts    ↑                addSessionHook()
       ↓                    |                addFunctionHook()
  executeHooks() (core)     |                getSessionHooks()
       ↓                    |
  execAgentHook / execHttpHook / execPromptHook
       ↓
  AsyncHookRegistry.ts ←── shellCommand execution
       ↓
  hookEvents.ts ─────── emits → SDK event queue

Post-Sampling System:
  executePostSamplingHooks() ← postSamplingHooks.ts
       ↓
  registerPostSamplingHook ← skillImprovement.ts (via apiQueryHookHelper.ts)
                            ← executePromptSuggestion() → speculation.ts

Task System:
  TaskOutput (memory+disk) → diskOutput.ts (file-level API)
       ↓
  framework.ts → registerTask / pollTasks / generateTaskAttachments

Teleport:
  api.ts ← environments.ts ← environmentSelection.ts
  api.ts ← gitBundle.ts → uploadFile()

Background Remote:
  remoteSession.ts ← preconditions.ts → environments.ts, api.ts

Tips:
  tipScheduler.ts ← tipRegistry.ts ← tipHistory.ts (config persistence)

Prompt Suggestion:
  promptSuggestion.ts → speculation.ts
       ↓                    ↓
  runForkedAgent()    runForkedAgent() + overlay isolation
```
