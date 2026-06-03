# State Management, Type Definitions & Constants Analysis (38 files, ~7,000 lines)

**Directories**: `F:\Claude\src\state\`, `F:\Claude\src\types\`, `F:\Claude\src\constants\`  
**Purpose**: Centralized application state management with React integration, comprehensive type system for all domain concepts, and immutable configuration constants.

---

## PART 1: State Management (6 files, ~1,144 lines)

### Architecture

```
┌──────────────────────────────────────────────┐
│                store.ts                       │
│           (Minimal reactive store)            │
│  createStore<T>(initialState, onChange?) →    │
│    { getState, setState, subscribe }         │
└──────────────┬───────────────────────────────┘
               │
               ▼
┌──────────────────────────────────────────────┐
│             AppStateStore.ts                  │
│           (Type + getDefaultAppState())       │
│  AppState type (~400 fields)                 │
│  getDefaultAppState()                        │
└──────────────┬───────────────────────────────┘
               │
               ▼
┌──────────────────────────────────────────────┐
│               AppState.tsx                    │
│         (React provider + hooks)              │
│  AppStateProvider (React context)            │
│  useAppState(selector) — useSyncExternalStore│
│  useSetAppState() — setter, no re-render     │
│  useAppStateStore() — raw store access       │
│  useAppStateMaybeOutsideOfProvider()         │
└──────────────┬───────────────────────────────┘
               │
       ┌───────┴───────┐
       ▼               ▼
┌──────────────┐ ┌──────────────┐
│onChangeAppState│selectors.ts   │
│(side-effects) │(pure derivations)│
└──────────────┘ └──────────────┘
       │               │
       ▼               ▼
┌──────────────┐
│teammateView- │
│Helpers.ts    │
└──────────────┘
```

### 1. `store.ts` (34 lines) — Minimal Reactive Store

A lightweight observable state container implementing the pub/sub pattern:

```typescript
export function createStore<T>(initialState: T, onChange?: OnChange<T>): Store<T>
```

**Design**:
- `getState()` — returns current state reference (no defensive copy — callers must not mutate)
- `setState(updater)` — functional updater pattern: `(prev: T) => T`; uses `Object.is` for change detection (identity comparison, not deep equality); calls `onChange?.({newState, oldState})` then notifies all listeners
- `subscribe(listener)` — Set-based listener collection, returns unsubscribe function
- **Zero dependencies** — no React, no external state library

### 2. `AppStateStore.ts` (560 lines) — AppState Type & Defaults

Defines the monolithic `AppState` type (~400 fields) and `getDefaultAppState()`. This is the single source of truth for ALL application state. Key sections:

**Core Settings**:
- `settings: SettingsJson` — user/project/local settings (model, permissions, etc.)
- `verbose: boolean` — debug mode
- `mainLoopModel: ModelSetting` — current model selection (null = not overridden)
- `mainLoopModelForSession: ModelSetting` — session-level model override

**UI State**:
- `statusLineText: string | undefined` — live status bar message
- `expandedView: 'none' | 'tasks' | 'teammates'` — panel visibility
- `isBriefOnly: boolean` — command line --brief flag
- `selectedIPAgentIndex: number` — agent sidebar selection
- `coordinatorTaskIndex: number` — CoordinatorTaskPanel selection (-1=pills, 0=main, 1+=agent rows)
- `viewSelectionMode: 'none' | 'selecting-agent' | 'viewing-agent'`
- `footerSelection: FooterItem | null` — focused footer pill
- `spinnerTip?: string` — loading tip display
- `agent: string | undefined` — --agent CLI flag

**Remote Control (REPL Bridge) State** — 12 fields:
- `replBridgeEnabled: boolean` — desired state (config/footer toggle)
- `replBridgeExplicit: boolean` — activated via /remote-control vs config-driven
- `replBridgeOutboundOnly: boolean` — mirror mode (forward events only)
- `replBridgeConnected: boolean` — env registered + session created (Ready)
- `replBridgeSessionActive: boolean` — ingress WebSocket open (Connected)
- `replBridgeReconnecting: boolean` — poll loop in error backoff
- `replBridgeConnectUrl/SessionUrl: string | undefined`
- `replBridgeEnvironmentId/SessionId: string | undefined`
- `replBridgeError: string | undefined`
- `replBridgeInitialName: string | undefined` — custom session name
- `showRemoteCallout: boolean` — first-time remote dialog

**Permissions**:
- `toolPermissionContext: ToolPermissionContext` — nested permission snapshot (mode, rule maps, working directories, bypass/auto-mode flags; see `Tool.ts`, not the simplified `types/permissions.ts` mirror)

**Tasks & Agents** (MCP models excluded from DeepImmutable due to function types):
- `tasks: {[taskId: string]: TaskState}` — all active tasks including agents
- `agentNameRegistry: Map<string, AgentId>` — name→ID routing
- `foregroundedTaskId?: string` — currently displayed task
- `viewingAgentTaskId?: string` — in-process teammate transcript view

**MCP Integration**:
- `mcp.clients: MCPServerConnection[]` — connected MCP servers
- `mcp.tools: Tool[]` / `mcp.commands: Command[]` — discovered tools/commands
- `mcp.resources: Record<string, ServerResource[]>` — resource listings
- `mcp.pluginReconnectKey: number` — incremented by /reload-plugins

**Plugin System**:
- `plugins.enabled: LoadedPlugin[]` / `plugins.disabled: LoadedPlugin[]`
- `plugins.errors: PluginError[]` — loading errors (29 variants)
- `plugins.installationStatus` — marketplace/plugin install tracking
- `plugins.needsRefresh: boolean` — stale flag

**Notifications & Elicitation**:
- `notifications: {current: Notification | null, queue: Notification[]}`
- `elicitation: {queue: ElicitationRequestEvent[]}` — MCP elicitation requests

**Other State Groups**:
- `kairosEnabled: boolean` — assistant mode (computed once in main.tsx)
- `remoteSessionUrl | remoteConnectionStatus | remoteBackgroundTaskCount` — assistant viewer mode
- `tungsten*` fields — tmux integration (ant-only)
- `bagel*` fields — WebBrowser tool
- `computerUseMcpState` — Chicago MCP session state (ant-only, 15 fields)
- `todos: {[agentId: string]: TodoList}` — todo tracking
- `fileHistory: FileHistoryState` — file change tracking
- `attribution: AttributionState` — commit attribution tracking
- `thinkingEnabled: boolean | undefined` — thinking toggle
- `promptSuggestionEnabled: boolean` — suggestion toggle
- `sessionHooks: SessionHooksState` — hook state
- `speculation: SpeculationState` — Speculative Edit state (idle/active with 12 sub-fields)

**Supporting Types**:
- `CompletionBoundary` — discriminated union: complete/bash/edit/denied_tool
- `SpeculationState` — discriminated union: idle ({status:'idle'}) vs active (id, abort(), startTime, messagesRef, boundary, etc.)
- `FooterItem` — `'tasks' | 'tmux' | 'bagel' | 'teams' | 'bridge' | 'companion'`
- `IDLE_SPECULATION_STATE: SpeculationState = {status: 'idle'}`

### 3. `AppState.tsx` (200 lines) — React Provider & Hooks

React integration layer using `useSyncExternalStore` for optimal rendering:

**`AppStateProvider({children, initialState?, onChangeAppState?})`**:
- Creates store via `createStore` (stored in useState for stable ref)
- Guards against nesting (throws if already inside another AppStateProvider)
- On mount: checks if bypass-permissions-mode became disabled while app wasn't mounted (remote settings)
- `useEffectEvent` wraps `applySettingsChange(store.setState, source)` for settings change handler
- Renders: `HasAppStateContext → AppStoreContext → MailboxProvider → VoiceProvider → children`
- Uses React Compiler (`_c()`) for memoization optimization

**`useAppState(selector: (state: AppState) => T): T`**:
- Subscribes to store using `useSyncExternalStore` — only re-renders when selected value changes (Object.is comparison)
- Throws if selector returns the entire state object (must return a property)
- Stable selector reference avoids re-subscription

**`useSetAppState(): (updater: (prev: AppState) => AppState) => void`**:
- Returns stable setState reference (never triggers re-render from state changes)
- Components using only this hook never re-render

**`useAppStateStore(): AppStateStore`** — raw store access for non-React code

**`useAppStateMaybeOutsideOfProvider(selector): T | undefined`**:
- Safe version that returns undefined outside AppStateProvider
- For components that may render in contexts without AppStateProvider

**Voice Integration** — feature-gated VoiceProvider (lazy-loaded only when `VOICE_MODE` build flag is on)

### 4. `onChangeAppState.ts` (171 lines) — Side-Effect Handler

Called by the store's `onChange` callback on every state mutation. Acts as a single choke point for cross-cutting side effects:

**Permission Mode Sync**:
- Detects `toolPermissionContext.mode` changes (any of 8+ mutation paths)
- Externalizes internal modes (bubble, ungated auto → their external equivalents)
- Notifies CCR via `notifySessionMetadataChanged({permission_mode, is_ultraplan_mode})`
- Notifies SDK status stream via `notifyPermissionModeChanged(newMode)`
- Ultraplan flag: gated (`plan` mode + newState true + oldState false), null for RFC 7396 key removal

**Model Change Persistence**:
- Model set to null → remove from userSettings
- Model set to value → save to userSettings + set `mainLoopModelOverride`

**Expanded View Persistence**:
- `expandedView` change → map to `showExpandedTodos`/`showSpinnerTree` legacy booleans → save to globalConfig

**Verbose Mode Persistence**:
- `verbose` change → save to globalConfig

**Tungsten Panel (ant-only) Persistence**:
- `tungstenPanelVisible` change → save to globalConfig

**Settings Change Side-Effects**:
- On `settings` change: clears API key helper cache, AWS credentials cache, GCP credentials cache
- On `settings.env` change: re-applies config environment variables (`applyConfigEnvironmentVariables()`)

**`externalMetadataToAppState(metadata)`** — inverse: restores AppState from CCR external_metadata (worker restart recovery)

### 5. `selectors.ts` (76 lines) — Pure Selectors

**`getViewedTeammateTask(appState)`**:
- Returns `InProcessTeammateTaskState | undefined`
- Checks: viewingAgentTaskId exists → task exists → is in-process teammate task

**`getActiveAgentForInput(appState)`**:
- Returns discriminated union: `{type:'leader'} | {type:'viewed', task} | {type:'named_agent', task}`
- Routing priority: viewed in-process teammate → viewed local agent → leader

### 6. `teammateViewHelpers.ts` (141 lines) — Teammate View Functions

**`enterTeammateView(taskId, setAppState)`**:
- If switching from another agent: releases previous (retain=false, messages cleared, evictAfter set if terminal)
- Sets retain=true on target (blocks eviction, enables stream-append)
- Clears evictAfter
- Sets viewingAgentTaskId + viewSelectionMode='viewing-agent'

**`exitTeammateView(setAppState)`**:
- Releases viewed agent: retain=false, messages cleared, evictAfter set for terminal
- Clears viewingAgentTaskId + viewSelectionMode='none'

**`stopOrDismissAgent(taskId, setAppState)`**:
- Running → abort (via abortController.abort())
- Terminal → dismiss (evictAfter=0, hides from filter)
- If viewing dismissed agent, also exits to leader view
- Uses `PANEL_GRACE_MS = 30_000` for eviction delay

---

## PART 2: Type Definitions (11 files, ~3,100 lines)

### 1. `types/permissions.ts` (402 lines) — Permission Types

The canonical permission type system, extracted to its own module to break import cycles:

**Permission Modes**:
- `ExternalPermissionMode` — user-facing modes: `'acceptEdits' | 'bypassPermissions' | 'default' | 'dontAsk' | 'plan'`
- `InternalPermissionMode = ExternalPermissionMode | 'auto' | 'bubble'` — exhaustive type union for typechecking
- `PermissionMode = InternalPermissionMode`
- `EXTERNAL_PERMISSION_MODES` — const array (5 modes)
- `INTERNAL_PERMISSION_MODES` — runtime validation set: spreads `EXTERNAL_PERMISSION_MODES` plus `'auto'` when `TRANSCRIPT_CLASSIFIER` feature is on. **`bubble` is internal-only** (not in this array; used by implementation, not settings/CLI recovery)
- `PERMISSION_MODES` — alias for `INTERNAL_PERMISSION_MODES`

**Permission Rules**:
- `PermissionRuleSource` — 8 sources: `userSettings | projectSettings | localSettings | flagSettings | policySettings | cliArg | command | session`
- `PermissionRuleValue` — `{toolName: string, ruleContent?: string}`
- `PermissionRule` — `{source: PermissionRuleSource, ruleBehavior: PermissionBehavior, ruleValue: PermissionRuleValue}`
- `ToolPermissionRulesBySource` — `{[T in PermissionRuleSource]?: string[]}` — allow/deny/ask rule lists keyed by source

**Working Directories**:
- `WorkingDirectorySource` — alias of `PermissionRuleSource` (semantic separation for future divergence)
- `AdditionalWorkingDirectory` — `{path: string, source: WorkingDirectorySource}`

**Permission Updates**:
- `PermissionUpdateDestination` — where to persist: `userSettings | projectSettings | localSettings | session | cliArg`
- `PermissionUpdate` — discriminated union (6 variants): `addRules | replaceRules | removeRules | setMode | addDirectories | removeDirectories`

**Permission Decisions**:
- `PermissionBehavior` — `'allow' | 'deny' | 'ask'`
- `PermissionCommandMetadata` — minimal `{name, description?, ...}` command shape for permission metadata (avoids importing full `Command` type)
- `PermissionMetadata` — `{command: PermissionCommandMetadata} | undefined`
- `PermissionAllowDecision<Input>` — granted: `behavior: 'allow'`, optional `updatedInput`, `userModified`, `decisionReason`, `toolUseID`, `acceptFeedback`, `contentBlocks`
- `PendingClassifierCheck` — async classifier metadata: `{command, cwd, descriptions}`
- `PermissionAskDecision<Input>` — pending: `behavior: 'ask'`, `message`, optional `updatedInput`, `decisionReason`, `suggestions` (PermissionUpdate[]), `blockedPath`, `metadata`, `isBashSecurityCheckForMisparsing`, `pendingClassifierCheck`, `contentBlocks`
- `PermissionDenyDecision` — denied: `behavior: 'deny'`, **`message`** (not `reason`), `decisionReason`, optional `toolUseID`
- `PermissionDecision = Allow | Ask | Deny`

**Permission Result (4-variant union)**:
- `PermissionResult<Input> = PermissionDecision<Input> | { behavior: 'passthrough', message, decisionReason?, suggestions?, blockedPath?, pendingClassifierCheck? }`
- Passthrough variant lets permission checkers defer to downstream handlers without allow/deny/ask

**Decision Reasons** (`PermissionDecisionReason` discriminated union):
- `rule` — matched `PermissionRule`
- `mode` — resolved from `PermissionMode`
- `subcommandResults` — composite bash: `reasons: Map<string, PermissionResult>`
- `permissionPromptTool` — tool-mediated prompt result
- `hook` — `{hookName, hookSource?, reason?}`
- `asyncAgent` — `{reason}`
- `sandboxOverride` — `'excludedCommand' | 'dangerouslyDisableSandbox'`
- `classifier` — `{classifier, reason}`
- `workingDir` — `{reason}`
- `safetyCheck` — `{reason, classifierApprovable}` — when true, auto mode lets classifier evaluate instead of forcing prompt
- `other` — `{reason}`

**Bash Classifier Types**:
- `ClassifierResult` — `{matches, matchedDescription?, confidence: 'high'|'medium'|'low', reason}`
- `ClassifierBehavior` — `'deny' | 'ask' | 'allow'`
- `ClassifierUsage` — token usage counters for classifier API calls
- `YoloClassifierResult` — auto-mode 2-stage classifier output: `shouldBlock`, `reason`, `model`, optional `thinking`, `unavailable`, `transcriptTooLong`, stage1/2 usage/duration/request IDs

**Permission Explainer**:
- `RiskLevel` — `'LOW' | 'MEDIUM' | 'HIGH'`
- `PermissionExplanation` — `{riskLevel, explanation, reasoning, risk}`

**Permissions Configuration**:
- `ToolPermissionContext` — **two definitions**:
  - `types/permissions.ts:427-441` — cycle-breaking subset for pure type modules (`ReadonlyMap` for directories; 10 fields)
  - `Tool.ts:123-138` — **runtime** app-state type (`DeepImmutable<…>`, `Map` for directories) adds optional **`isAutoModeAvailable`** (auto-mode gate; set by `permissionSetup.ts`)
- Shared fields: `mode`, `additionalWorkingDirectories`, `alwaysAllowRules`, `alwaysDenyRules`, `alwaysAskRules`, `isBypassPermissionsModeAvailable`, optional `strippedDangerousRules`, `shouldAvoidPermissionPrompts`, `awaitAutomatedChecksBeforeDialog`, `prePlanMode`

**Bridge / Hook Integration** (implementation in `bridge/bridgePermissionCallbacks.ts`, `utils/permissions/`):
- `PermissionRequestEvent` — hook-level permission request (see `types/hooks.ts`)
- Bridge wire types: `BridgePermissionResponse` (`allow|deny`, optional `updatedInput`, `updatedPermissions`, `message`); `isBridgePermissionResponse()` type guard

### 2. `types/plugin.ts` (363 lines) — Plugin System Types

**`BuiltinPluginDefinition`** — built-in plugins that ship with CLI:
- `name, description, version?, skills?, hooks?, mcpServers?, isAvailable?(), defaultEnabled?`

**`LoadedPlugin`** — loaded plugin instance:
- `name, manifest, path, source, repository, enabled?, isBuiltin?, sha?, commandsPath(s), agentsPath(s), skillsPath(s), outputStylesPath(s), hooksConfig?, mcpServers?, lspServers?, settings?`

**`PluginError`** — 29-variant discriminated union:
- Installation: `path-not-found, git-auth-failed, git-timeout, network-error`
- Parsing: `manifest-parse-error, manifest-validation-error`
- Resolution: `plugin-not-found, marketplace-not-found, marketplace-load-failed`
- Configuration: `mcp-config-invalid, mcp-server-suppressed-duplicate, lsp-config-invalid`
- Loading: `hook-load-failed, component-load-failed`
- Runtime: `mcpb-download-failed, ...` (additional variants)
- Rich context per variant (paths, URLs, error details, component names)
- Used as a structured type (not string-based) for reliable error handling

**`PluginRepository`** — `{url, branch, lastUpdated?, commitSha?}`
**`PluginConfig`** — `{repositories: Record<string, PluginRepository>}`
**`PluginComponent`** — `'commands' | 'agents' | 'skills' | 'hooks' | 'output-styles'`

### 3. `types/command.ts` (216 lines) — Command System Types

**`PromptCommand`** — model-prompting commands (skills):
- `type: 'prompt'`, `progressMessage`, `contentLength`, `argNames?`, `allowedTools?`, `model?`
- `source: SettingSource | 'builtin' | 'mcp' | 'plugin' | 'bundled'`
- `pluginInfo?: {pluginManifest, repository}` — for plugin-sourced skills
- `disableNonInteractive?, hooks?, skillRoot?`
- `context?: 'inline' | 'fork'` — inline (expands in conversation) vs fork (sub-agent)
- `agent?, effort?, paths?` — fork-specific
- `getPromptForCommand(args, context): Promise<ContentBlockParam[]>` — generates skill content

**`LocalCommand`** — local JS commands:
- `type: 'local'`, `supportsNonInteractive`, `load(): Promise<LocalCommandModule>`
- `LocalCommandCall = (args, context) => Promise<LocalCommandResult>`
- `LocalCommandResult` — discriminated union: text | compact | skip
- `LocalCommandModule = {call: LocalCommandCall}`

**`LocalJSXCommand`** — React/JSX commands:
- `type: 'local-jsx'`, `load(): Promise<LocalJSXCommandModule>`
- `LocalJSXCommandCall = (onDone, context, args) => Promise<ReactNode>`
- `LocalJSXCommandModule = {call: LocalJSXCommandCall}`
- `LocalJSXCommandOnDone` — callback: `(result?, {display?, shouldQuery?, metaMessages?, nextInput?, submitNextInput?}) => void`
- `LocalJSXCommandContext` — extends `ToolUseContext` with canUseTool, setMessages, IDE status, theme, API key changes, resume function

**`CommandBase`** — common command metadata:
- `availability?: CommandAvailability[]` — auth/provider gating: `'claude-ai' | 'console'`
- `name, description, aliases?, argumentHint?, whenToUse?, version?`
- `isEnabled?(), isHidden?` — conditional visibility
- `isMcp?, loadedFrom?, kind?: 'workflow', immediate?, isSensitive?`
- `disableModelInvocation?, userInvocable?`

**`CommandResultDisplay`** — `'skip' | 'system' | 'user'`
**`ResumeEntrypoint`** — `'cli_flag' | 'slash_command_picker' | 'slash_command_session_id' | 'slash_command_title' | 'fork'`
**`CommandAvailability`** — `'claude-ai' | 'console'`

### 4. `types/hooks.ts` (290 lines) — Hook System Types & Schemas

**Hook JSON Output (Zod Schemas)**:
- `syncHookResponseSchema` — comprehensive sync hook response:
  - Common: `continue?, suppressOutput?, stopReason?, decision?, reason?, systemMessage?`
  - `hookSpecificOutput` — per-event-type union (15 variants):
    - PreToolUse: `permissionDecision?, permissionDecisionReason?, updatedInput?, additionalContext?`
    - UserPromptSubmit: `additionalContext?`
    - SessionStart: `additionalContext?, initialUserMessage?, watchPaths?`
    - Setup: `additionalContext?`
    - SubagentStart: `additionalContext?`
    - PostToolUse: `additionalContext?, updatedMCPToolOutput?`
    - PostToolUseFailure: `additionalContext?`
    - PermissionDenied: `retry?`
    - Notification: `additionalContext?`
    - PermissionRequest: `decision: allow({updatedInput?, updatedPermissions?}) | deny({message?, interrupt?})`
    - Elicitation/ElicitationResult: `action?('accept'|'decline'|'cancel'), content?`
    - CwdChanged: `watchPaths?`
    - FileChanged: `watchPaths?`
    - WorktreeCreate: `worktreePath`

- `asyncHookResponseSchema` — `{async: true, asyncTimeout?}`
- `hookJSONOutputSchema` — union of async + sync
- Compile-time assertion: `IsEqual<SchemaHookJSONOutput, HookJSONOutput>`

**Prompt Elicitation**:
- `promptRequestSchema` — `{prompt: string (request id), message: string, options: {key, label, description?}[]}`
- `PromptRequest` / `PromptResponse` types

**Utilities**:
- `isHookEvent(value)` — type guard using `HOOK_EVENTS` array
- `isSyncHookJSONOutput(json)` / `isAsyncHookJSONOutput(json)` — type guards
- `HookCallback` — `(hookEvent, hookInput, appState, attributionState) => Promise<HookResult>`

### 5. `types/ids.ts` (44 lines) — Branded IDs

- `SessionId` — branded string: `string & {__brand_session_id: true}`
- `AgentId` — branded string: `string & {__brand_agent_id: true}`
- Used with branded type pattern for compile-time type safety without runtime overhead

### 6. `types/logs.ts` (330 lines) — Log & Message Types

- `SerializedMessage` — full serialized message representation
- `LogOption` — discriminated union: `'full' | 'sparse' | 'resume'`
- Various metadata message types (system notifications, task tracking, etc.)
- Message metadata interfaces for IDE events, task events, hook events, MCP status

### 7. `types/textInputTypes.ts` (387 lines) — Input Types

- `QueuedCommand` — command queue items
- `PromptInputMode` — input mode variants
- Input-related type definitions for the prompt/REPL interaction system
- Hook integration types for input lifecycle

### 8. `types/generated/` (4 files, ~1,200 lines) — Protobuf Types

Generated from Protocol Buffer definitions:

- **`claude_code_internal_event.ts`** (837 lines) — Claude Code internal analytics event schema:
  - Events: bridge lifecycle (started, connected, work_received, session_done, heartbeat_error), permission decisions, tool usage, hook events
  - Rich field definitions with validation rules

- **`auth.ts`** — Auth event schema (login, token refresh, etc.)

- **`growthbook_experiment_event.ts`** — GrowthBook experiment tracking schema

- **`timestamp.ts`** — Google protobuf Timestamp wrapper

---

## PART 3: Constants (21 files, ~2,600 lines)

### System & Product Constants

**`constants/product.ts`** (71 lines):
- `getClaudeAiBaseUrl()` — resolves claude.ai base URL by org UUID / tenant
- `getRemoteSessionUrl(sessionId, ingressUrl?)` — session URL with `cse_→session_` prefix translation
- Product URL constants (login, signup, docs, billing, etc.)

**`constants/oauth.ts`** (217 lines):
- `getOauthConfig()` — OAuth endpoints: `BASE_API_URL`, Auth + Token URLs, Client ID, scopes, redirect URIs
- OAuth flow configuration for claude.ai integration
- `CLAUDE_CODE_OAUTH_TOKEN` env var support for federated auth

**`constants/system.ts`** (83 lines):
- `getCliSystemPrompt()` — default CLI system prompt builder
- Model instructions for the coding assistant persona

**`constants/systemPromptSections.ts`** (61 lines):
- Memoized vs volatile sections of the system prompt
- Controls which sections are cached between turns and which are re-evaluated

**`constants/prompts.ts`** (799 lines) — **System Prompt Builder**:
- Comprehensive prompt template system:
  - Core identity and capabilities description
  - Tool usage instructions (Read, Write, Edit, Bash, Glob, Grep, WebFetch, WebSearch, Task, etc.)
  - Code style guidelines (no comments, follow conventions, etc.)
  - Permission model instructions (when to ask, how to present info)
  - Context management (compaction, continuation)
  - Error handling philosophy
  - Markdown formatting rules for CLI output
  - Platform-specific notes (Windows PowerShell, git, etc.)
- `SYSTEM_PROMPT_SECTIONS` object with categorized sections
- Dynamic injection points for: custom skill prompts, plugin hooks, tool definitions, file context

**`constants/common.ts`** (29 lines):
- `formatDate(ms)` — date formatting utilities
- Common helper functions used across constants

**`constants/errorIds.ts`** (14 lines):
- Error ID constants for structured error reporting and telemetry

### Tool & API Constants

**`constants/tools.ts`** (107 lines):
- Tool allowlists for various permission modes
- Default tool configurations
- Tool name constants and categorization

**`constants/toolLimits.ts`** (50 lines):
- Tool result size limits: `MAX_TOOL_RESULT_BYTES`, `MAX_TOOL_RESULT_LINES`
- Bash output limits
- Read tool limits (bytes, lines)
- Truncation thresholds

**`constants/apiLimits.ts`** (81 lines):
- API rate limits and timeout configurations
- `DEFAULT_TIMEOUT_MS`, `MAX_RETRIES`
- Token budget limits per model
- Max input tokens, max output tokens
- Budget enforcement rules

**`constants/betas.ts`** (49 lines):
- API beta header constants: `PromptCachingBeta`, `ComputerUseBeta`, etc.
- GrowthBook feature flag keys
- Beta feature toggles

### UI & Formatting Constants

**`constants/outputStyles.ts`** (174 lines):
- Output style definitions: `'normal' | 'explanatory' | 'learning'`
- Each style has: name, description, system prompt modifiers
- `OutputStyle` type and available styles list
- Style-specific instructions for model behavior

**`constants/spinnerVerbs.ts`** (202 lines):
- Spinner verb alternatives for various actions: "Reading", "Writing", "Searching", "Processing", "Analyzing", "Computing", "Generating", etc.
- Themed verb arrays for different tool categories
- Randomized selection for liveliness

**`constants/turnCompletionVerbs.ts`** (12 lines):
- Turn completion verb list: "Done", "Complete", "Ready", etc.

**`constants/figures.ts`** (37 lines):
- Unicode glyph constants: `BRIDGE_READY_INDICATOR`, `BRIDGE_FAILED_INDICATOR`, `BRIDGE_SPINNER_FRAMES`
- Decorative symbols for CLI output

**`constants/files.ts`** (151 lines):
- Binary file detection constants: magic bytes patterns, file extension blocklists
- `BINARY_FILE_EXTENSIONS`, `BINARY_MAGIC_BYTES`
- File truncation and handling rules

### Feature & GrowthBook Keys

**`constants/keys.ts`** (10 lines):
- GrowthBook feature key constants: `TENGU_CCR_BRIDGE`, `TENGU_BRIDGE_REPL_V2`, etc.
- Centralized key management for feature flags

**`constants/cyberRiskInstruction.ts`** (24 lines):
- Security boundary instructions for the model
- Policy enforcement language

### Other Constants

**`constants/messages.ts`** (1 line):
- `NO_CONTENT_MESSAGE = '(No content)'` — fallback display text

**`constants/xml.ts`** (73 lines):
- XML tag constants for structured output: `<thinking>`, `<tool_call>`, `<result>`, etc.
- Tag definitions and attributes
- Parsing boundaries

### GitHub Actions Integration

**`constants/github-app.ts`** (115 lines):
- GitHub Actions workflow templates
- GitHub App client ID / installation URL
- CI/CD integration constants
- Workflow YAML templates for Claude Code automation

---

## Key Design Decisions

1. **Monolithic AppState with slice selectors** — Single source of truth avoids state synchronization bugs; `useSyncExternalStore` with selector pattern ensures minimal re-renders

2. **Functional updater pattern** — `setState(prev => ({...prev, field: value}))` ensures stale closures can't cause lost updates

3. **`Object.is` comparison** — Identity check (not deep equality) for change detection; callers must return new object references for mutations

4. **Single change handler (`onChangeAppState`)** consolidates all cross-cutting side effects (permission mode sync, settings persistence) into one place — eliminates scattered mutation-path logic

5. **Branded types for IDs** — Compile-time distinction between SessionId, AgentId without runtime overhead

6. **Discriminated union errors** — `PluginError` (29 variants) replaces string-based error matching with type-safe, IDE-autocompletable error handling

7. **Zod schemas for hooks** — Runtime validation of hook JSON output via Zod schemas, with compile-time type assertion matching SDK types

8. **Generated protobuf types** — Analytics events use protobuf-generated TypeScript types for consistent schema across client/server

9. **Extracted permission types** — Breaking the import cycle by isolating pure type definitions from implementation modules in `utils/permissions/`

10. **Feature-gated voice** — `VoiceProvider` is ant-only via `require()` with `feature('VOICE_MODE')` guard — zero import in external bundles
