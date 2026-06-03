# Tool System Overview

## `Tool.ts` — Core Tool Interface & Building Blocks

**File**: `src/Tool.ts` (792 lines)

The Tool system defines the abstract contract that every tool in Claude Code must implement. It provides type definitions, interfaces, context types, and a factory function (`buildTool`) that fills in safe defaults. This file is the central hub from which all ~60+ tools derive their shape.

---

### `Tool<Input, Output, P>` Interface

The complete tool contract. Generic over `Input` (Zod schema), `Output` (result data), and `P` (progress type).

#### Identity

| Field | Type | Description |
|-------|------|-------------|
| `name` | `string` | Primary tool name (must be unique across the pool) |
| `aliases` | `string[]` (optional) | Backward-compatible alternative names. `toolMatchesName()` checks both name and aliases. |
| `searchHint` | `string` (optional) | 3–10 word capability phrase for ToolSearch keyword matching. Helps the model discover deferred tools. E.g., `'jupyter'` for NotebookEdit, `'read files, images, PDFs, notebooks'` for FileRead. |

#### Execution

| Field | Type | Description |
|-------|------|-------------|
| `call(args, context, canUseTool, parentMessage, onProgress)` | `Promise<ToolResult<Output>>` | **The core execution method.** Receives parsed input, the full tool-use context, a permission callback, the parent assistant message, and an optional progress emitter. Returns result data plus optional new messages. |
| `description(input, options)` | `Promise<string>` | Returns the full model-facing tool description. Called at prompt assembly time with the parsed input. `options` includes `isNonInteractiveSession`, `toolPermissionContext`, and `tools` (complete tool pool). |
| `inputSchema` | `Input extends AnyObject` | Zod schema for the tool's input parameters. Used for parsing and validation. Can be a getter-backed lazy schema (via `lazySchema()`) to survive circular dependency resolution at module load. |
| `inputJSONSchema` | `ToolInputJSONSchema` (optional) | Raw JSON Schema representation for MCP tools that don't use Zod. |
| `outputSchema` | `z.ZodType<unknown>` (optional) | Optional Zod schema for structured output typing (not yet required on all tools — TungstenTool omits it). |

#### Validation

| Field | Type | Description |
|-------|------|-------------|
| `validateInput(input, context)` | `Promise<ValidationResult>` (optional) | Pre-execution validation. Runs **before** `checkPermissions`. Returns `{ result: true }` or `{ result: false, message, errorCode }`. Used for early rejection (file not found, invalid parameters, deny rules). |
| `inputsEquivalent(a, b)` | `boolean` (optional) | Compares two inputs for deduplication. Used by `areFileEditsInputsEquivalent()` to detect repeated edit attempts. |

#### Permissions

| Field | Type | Description |
|-------|------|-------------|
| `checkPermissions(input, context)` | `Promise<PermissionResult>` | Runtime permission gate. Called **after** `validateInput`. Returns `{ behavior: 'allow' | 'deny' | 'ask' | 'passthrough', ... }`. Each tool implements its own permission logic (filesystem checks, domain lists, etc.). |
| `preparePermissionMatcher(input)` | `Promise<(pattern: string) => boolean>` (optional) | Pre-compiles an expensive permission pattern matcher once per hook-input pair. Returns a closure called per hook pattern. If unimplemented, only tool-name-level matching works. |
| `backfillObservableInput(input)` | `void` | Mutates observable input copies before hooks/observers see them. Idempotent — the original API-bound input is never mutated (preserves prompt cache). Used to expand `~` and relative paths to absolute. |

#### Safety

| Field | Type | Description |
|-------|------|-------------|
| `isEnabled()` | `boolean` | Runtime enablement gate. Default: `true`. Tools can self-disable based on model provider, environment, or feature flags. |
| `isReadOnly(input)` | `boolean` | Whether the tool only reads. Default: `false` (assume writes). Read-only tools skip certain permission checks. |
| `isConcurrencySafe(input)` | `boolean` | Whether multiple instances can run concurrently. Default: `false`. Concurrency-safe tools bypass serialized execution queues. |
| `isDestructive(input)` | `boolean` (optional) | Whether the tool performs irreversible operations (delete, overwrite, send). Default: `false`. |
| `interruptBehavior()` | `'cancel' \| 'block'` (optional) | What happens when the user sends a new message while this tool runs: `'cancel'` stops it, `'block'` lets it finish. Default: `'block'`. |
| `isMcp` | `boolean` (optional) | `true` for MCP-provided tools. |
| `isLsp` | `boolean` (optional) | `true` for LSP operation tools. |
| `isOpenWorld(input)` | `boolean` (optional) | Whether the tool accesses external/arbitrary resources. Used in security classification. |
| `requiresUserInteraction()` | `boolean` (optional) | Whether the tool inherently needs user input (e.g., AskUserQuestion). |

#### Deferred Loading

| Field | Type | Description |
|-------|------|-------------|
| `shouldDefer` | `boolean` (optional, readonly) | When `true`, the tool is sent with `defer_loading: true` and requires ToolSearch to be used first. |
| `alwaysLoad` | `boolean` (optional, readonly) | When `true`, the tool is never deferred — its full schema always appears in the initial prompt. For MCP tools, set via `_meta['anthropic/alwaysLoad']`. |

#### MCP

| Field | Type | Description |
|-------|------|-------------|
| `mcpInfo` | `{ serverName, toolName }` (optional) | For MCP tools: original server/tool names as received from the MCP server. Present regardless of whether `name` is prefixed (`mcp__server__tool`) or unprefixed. |
| `strict` | `boolean` (optional, readonly) | When `true` and `tengu_tool_pear` feature is enabled, causes the API to more strictly adhere to tool instructions and parameter schemas. |

#### Rendering

| Field | Type | Description |
|-------|------|-------------|
| `renderToolUseMessage(input, options)` | `React.ReactNode` | Renders the tool invocation as inline UI. Called with partial input (streaming). |
| `renderToolResultMessage(content, progress, options)` | `React.ReactNode` (optional) | Renders the tool result. Omit to suppress UI (e.g., TodoWrite updates the sidebar, not the transcript). Options include `style: 'condensed'`, `theme`, `verbose`, `isTranscriptMode`, `isBriefOnly`, and the original `input`. |
| `renderToolUseProgressMessage(progress, options)` | `React.ReactNode` (optional) | Renders live progress while the tool runs. Options include `terminalSize`, `inProgressToolCallCount`, `isTranscriptMode`. |
| `renderToolUseTag(input)` | `React.ReactNode` (optional) | Renders an optional tag after the tool use message (e.g., timeout, model, resume ID). Returns `null` to suppress. |
| `renderToolUseQueuedMessage()` | `React.ReactNode` (optional) | Renders a queued-state indicator. |
| `renderToolUseRejectedMessage(input, options)` | `React.ReactNode` (optional) | Renders a rejection UI (e.g., file edits show the rejected diff). Falls back to `<FallbackToolUseRejectedMessage />`. |
| `renderToolUseErrorMessage(result, options)` | `React.ReactNode` (optional) | Renders an error UI (e.g., search tools show "File not found"). Falls back to `<FallbackToolUseErrorMessage />`. |
| `renderGroupedToolUse(toolUses, options)` | `React.ReactNode \| null` (optional) | Renders multiple parallel tool instances as a group (non-verbose mode only). Returns `null` to fall back to individual rendering. |
| `isTransparentWrapper()` | `boolean` (optional) | Transparent wrappers (e.g., REPL) delegate all rendering to progress handlers. The wrapper itself shows nothing. |

#### Metadata

| Field | Type | Description |
|-------|------|-------------|
| `prompt({ getToolPermissionContext, tools, agents, allowedAgentTypes })` | `Promise<string>` | Returns the model-facing prompt text for this tool (constraints, instructions, warnings). |
| `userFacingName(input)` | `string` | Human-readable name for UI display (e.g., "Read", "Edit", "Bash"). Default: `name`. |
| `userFacingNameBackgroundColor(input)` | `keyof Theme \| undefined` (optional) | Theme color for the user-facing name badge. |
| `getToolUseSummary(input)` | `string \| null` (optional) | Short string summary for compact views (e.g., truncated file paths, command snippets). |
| `getActivityDescription(input)` | `string \| null` (optional) | Present-tense activity string for spinner display (e.g., "Reading src/foo.ts", "Running bun test"). |

#### Output

| Field | Type | Description |
|-------|------|-------------|
| `mapToolResultToToolResultBlockParam(content, toolUseID)` | `ToolResultBlockParam` | Converts the tool's output data into an API-compatible `tool_result` content block. This is what the model receives. |
| `maxResultSizeChars` | `number` | Maximum characters before the result is persisted to disk and replaced with a preview + file path. `Infinity` for tools that must never persist (e.g., Read — circular loop). |
| `extractSearchText(output)` | `string` (optional) | Flattened text of what `renderToolResultMessage` shows **in transcript mode**. Used for transcript search indexing. Must match what actually renders to avoid phantom/under-count bugs. |
| `isResultTruncated(output)` | `boolean` (optional) | Whether the non-verbose rendering is truncated. Gates the click-to-expand affordance in fullscreen. |

#### Advanced

| Field | Type | Description |
|-------|------|-------------|
| `isSearchOrReadCommand(input)` | `{ isSearch, isRead, isList? }` (optional) | Classifies a tool use for UI collapsing. Used by Grep, Glob, FileRead, and Bash. |
| `toAutoClassifierInput(input)` | `unknown` | Returns a compact representation for the auto-mode security classifier. E.g., `ls -la` for Bash, `/tmp/x: new content` for Edit. Return `''` to skip classification. |
| `getPath(input)` | `string` (optional) | Returns the primary file/directory path the tool operates on. Used for permission routing and context awareness. |

---

### Supporting Types

#### `ToolInputJSONSchema`
```typescript
type ToolInputJSONSchema = {
  [x: string]: unknown
  type: 'object'
  properties?: { [x: string]: unknown }
}
```
Raw JSON Schema for MCP tool inputs (no Zod intermediate).

#### `ValidationResult`
```typescript
type ValidationResult =
  | { result: true }
  | { result: false; message: string; errorCode: number }
```
Binary validation result. Error codes are tool-specific.

#### `ToolResult<T>`
```typescript
type ToolResult<T> = {
  data: T
  newMessages?: (UserMessage | AssistantMessage | AttachmentMessage | SystemMessage)[]
  contextModifier?: (context: ToolUseContext) => ToolUseContext
  mcpMeta?: {
    _meta?: Record<string, unknown>
    structuredContent?: Record<string, unknown>
  }
}
```
The return type from `call()`. `data` is mandatory. `newMessages` allows tools to inject supplementary messages (image metadata for FileRead, PDF document blocks, etc.). `contextModifier` is only honored for non-concurrency-safe tools and allows mutation of the tool context for subsequent calls. `mcpMeta` passes through MCP protocol metadata to SDK consumers.

#### `ToolProgress<P>`
```typescript
type ToolProgress<P extends ToolProgressData> = {
  toolUseID: string
  data: P
}
```

#### `ToolCallProgress<P>`
```typescript
type ToolCallProgress<P extends ToolProgressData = ToolProgressData> = (
  progress: ToolProgress<P>,
) => void
```
Callback type passed to `call()` for emitting progress updates.

#### `ToolUseContext`

The full execution context available to every tool call (300 lines). Key fields:

**`options`** (nested object):
- `commands`: `Command[]` — Registered slash commands
- `debug`: `boolean` — Debug mode flag
- `mainLoopModel`: `string` — Active model identifier
- `tools`: `Tools` — Complete tool pool (built-in + MCP)
- `verbose`: `boolean` — Verbose output mode
- `thinkingConfig`: `ThinkingConfig` — Model thinking configuration
- `mcpClients`: `MCPServerConnection[]` — Active MCP server connections
- `mcpResources`: `Record<string, ServerResource[]>` — MCP resources by server
- `isNonInteractiveSession`: `boolean` — SDK/print mode vs. REPL
- `agentDefinitions`: `AgentDefinitionsResult` — Available sub-agent definitions
- `maxBudgetUsd`: `number` (optional) — Cost ceiling
- `customSystemPrompt`: `string` (optional) — Replaces default system prompt
- `appendSystemPrompt`: `string` (optional) — Appended after main system prompt
- `querySource`: `QuerySource` (optional) — Analytics tracking override
- `refreshTools`: `() => Tools` (optional) — Callback for dynamic tool pools (MCP server reconnection)

**Core infrastructure**:
- `abortController`: `AbortController` — Cancellation signal
- `readFileState`: `FileStateCache` — LRU cache of read file contents + mtimes
- `getAppState()`: `() => AppState` — Root application state accessor
- `setAppState(f)`: `(f: (prev) => AppState) => void` — State updater (no-op for async agents)
- `setAppStateForTasks`: Same as above but always reaches the root store (session-scoped infrastructure)
- `messages`: `Message[]` — Full conversation transcript
- `toolUseId`: `string` (optional) — Current tool use ID

**UI & notifications**:
- `setToolJSX`: `SetToolJSXFn` (optional) — Renders JSX inline in the REPL
- `addNotification`: `(notif) => void` (optional) — Adds a UI notification
- `appendSystemMessage`: `(msg) => void` (optional) — Appends UI-only system message (stripped at API boundary)
- `sendOSNotification`: `(opts) => void` (optional) — OS-level notification (iTerm2, Kitty, etc.)
- `setInProgressToolUseIDs`: State updater for tracking running tools
- `setHasInterruptibleToolInProgress`: Tracks whether an interruptible tool is active
- `setResponseLength`: Tracks response token length
- `setStreamMode`: Controls spinner display mode
- `onCompactProgress`: Handler for context compaction progress events
- `openMessageSelector`: Opens message selector UI

**Agent & task infrastructure**:
- `agentId`: `AgentId` (optional) — Only set for subagents
- `agentType`: `string` (optional) — Subagent type name
- `requireCanUseTool`: `boolean` (optional) — Forces `canUseTool` call even when hooks auto-approve (used by speculation)
- `pushApiMetricsEntry`: `(ttftMs) => void` (optional) — Ant-only OTPS tracking
- `setSDKStatus`: `(status) => void` (optional) — SDK status reporting

**File & search limits**:
- `fileReadingLimits`: `{ maxTokens?, maxSizeBytes? }` (optional) — Override for FileReadTool defaults
- `globLimits`: `{ maxResults? }` (optional) — Override for GlobTool result limits

**Permission & denial tracking**:
- `toolDecisions`: `Map<string, { source, decision, timestamp }>` (optional) — Recorded permission decisions
- `localDenialTracking`: `DenialTrackingState` (optional) — Denial counter for async subagents (whose `setAppState` is a no-op)

**Session & history**:
- `updateFileHistoryState`: `(updater) => void` — File history mutation
- `updateAttributionState`: `(updater) => void` — Commit attribution tracking
- `setConversationId`: `(id: UUID) => void` (optional) — Conversation ID setter
- `queryTracking`: `QueryChainTracking` (optional) — Chain ID and depth tracking
- `requestPrompt`: Callback factory for interactive user prompts
- `criticalSystemReminder_EXPERIMENTAL`: Experimental system reminder text

**Skill & memory**:
- `nestedMemoryAttachmentTriggers`: `Set<string>` (optional) — Paths that triggered nested memory attachment
- `loadedNestedMemoryPaths`: `Set<string>` (optional) — Already-injected CLAUDE.md paths (dedup)
- `dynamicSkillDirTriggers`: `Set<string>` (optional) — Skill directories discovered via file reads
- `discoveredSkillNames`: `Set<string>` (optional) — Skill names surfaced via discovery (telemetry)

**Subagent-specific**:
- `preserveToolUseResults`: `boolean` (optional) — Keep tool results on messages even for subagents
- `contentReplacementState`: `ContentReplacementState` (optional) — Per-conversation-thread tool result budget
- `renderedSystemPrompt`: `SystemPrompt` (optional) — Parent's rendered prompt for fork cache sharing

**Elicitation**:
- `handleElicitation`: `(serverName, params, signal) => Promise<ElicitResult>` (optional) — MCP URL elicitation handler (print/SDK mode)

#### `ToolPermissionContext`

Immutable permission state snapshot:
```typescript
type ToolPermissionContext = DeepImmutable<{
  mode: PermissionMode
  additionalWorkingDirectories: Map<string, AdditionalWorkingDirectory>
  alwaysAllowRules: ToolPermissionRulesBySource
  alwaysDenyRules: ToolPermissionRulesBySource
  alwaysAskRules: ToolPermissionRulesBySource
  isBypassPermissionsModeAvailable: boolean
  isAutoModeAvailable?: boolean
  strippedDangerousRules?: ToolPermissionRulesBySource
  shouldAvoidPermissionPrompts?: boolean
  awaitAutomatedChecksBeforeDialog?: boolean
  prePlanMode?: PermissionMode
}>
```

#### `Tools`
```typescript
type Tools = readonly Tool[]
```
Tagged collection type for tracking where tool sets are assembled and passed across the codebase.

---

### `buildTool<D>(def: D): BuiltTool<D>`

The factory function that all ~60+ tool exports go through. Takes a `ToolDef` (same shape as `Tool` but with defaultable methods optional) and returns a complete `Tool`.

**Seven defaulted keys** (fail-closed where appropriate):

| Key | Default | Rationale |
|-----|---------|-----------|
| `isEnabled` | `() => true` | Most tools are always available |
| `isConcurrencySafe` | `(_input?: unknown) => false` | Assume not safe |
| `isReadOnly` | `(_input?: unknown) => false` | Assume writes |
| `isDestructive` | `(_input?: unknown) => false` | Most tools aren't destructive |
| `checkPermissions` | `(input, _ctx?) => Promise.resolve({ behavior: 'allow', updatedInput: input })` | Defer to general permission system |
| `toAutoClassifierInput` | `(_input?: unknown) => ''` | Skip classifier — security-relevant tools must override |
| `userFacingName` | `() => def.name` | Uses the tool's primary name |

**Type-level semantics**: `BuiltTool<D>` is a mapped type that spreads `TOOL_DEFAULTS` under `def`, with keys declared in `def` taking precedence. The `satisfies ToolDef` pattern at usage sites preserves literal types while providing contextual typing for method parameters.

**Constraint**: `D extends AnyToolDef` where `AnyToolDef = ToolDef<any, any, any>`. The `any` in constraint position is structural and never leaks into the return type.

#### `ToolDef<Input, Output, P>`
```typescript
type ToolDef<Input, Output, P> = Omit<Tool<Input, Output, P>, DefaultableToolKeys> &
  Partial<Pick<Tool<Input, Output, P>, DefaultableToolKeys>>
```
The partial form accepted by `buildTool`. All defaultable keys become optional.

#### `DefaultableToolKeys`
```typescript
type DefaultableToolKeys =
  | 'isEnabled'
  | 'isConcurrencySafe'
  | 'isReadOnly'
  | 'isDestructive'
  | 'checkPermissions'
  | 'toAutoClassifierInput'
  | 'userFacingName'
```

---

### Utility Functions

#### `toolMatchesName(tool, name): boolean`
Checks primary `name` and `aliases[]`. Used by `findToolByName`, `filterToolsByDenyRules`, and REPL tool filtering.

#### `findToolByName(tools, name): Tool | undefined`
Linear scan using `toolMatchesName`.

#### `getEmptyToolPermissionContext(): ToolPermissionContext`
Returns a fresh default permission context (`mode: 'default'`, empty rule maps).

#### `filterToolProgressMessages(msgs): ProgressMessage<ToolProgressData>[]`
Filters out `hook_progress` entries from progress message arrays.

---

## `tools.ts` — Tool Pool Assembly & Filtering

**File**: `src/tools.ts` (389 lines)

The orchestration layer that assembles the complete tool pool from built-in tools, feature-flagged tools, and MCP tools. It handles mode filtering, permission-based filtering, and deduplication.

---

### `getAllBaseTools(): Tools`

The **single source of truth** for all available tools. Returns the complete list respecting `process.env` flags, feature gates, and conditional imports. The ordering matters — it must stay in sync with the `claude_code_global_system_caching` GrowthBook config to preserve prompt caching.

**Always-included tools** (unconditional):
```
AgentTool, TaskOutputTool, BashTool, ExitPlanModeV2Tool,
FileReadTool, FileEditTool, FileWriteTool, NotebookEditTool,
WebFetchTool, TodoWriteTool, WebSearchTool, TaskStopTool,
AskUserQuestionTool, SkillTool, EnterPlanModeTool,
SendMessageTool, ListMcpResourcesTool, ReadMcpResourceTool,
BriefTool
```

**Conditionally-included tools** (feature gated):
- `GlobTool` + `GrepTool` — Excluded when `hasEmbeddedSearchTools()` (ant-native builds with bfs/ugrep)
- `ConfigTool` — `process.env.USER_TYPE === 'ant'` only
- `TungstenTool` — `process.env.USER_TYPE === 'ant'` only
- `REPLTool` — `process.env.USER_TYPE === 'ant'` only
- `SuggestBackgroundPRTool` — `process.env.USER_TYPE === 'ant'` only
- `WebBrowserTool` — `feature('WEB_BROWSER_TOOL')`
- `TaskCreateTool, TaskGetTool, TaskUpdateTool, TaskListTool` — `isTodoV2Enabled()`
- `OverflowTestTool` — `feature('OVERFLOW_TEST_TOOL')`
- `CtxInspectTool` — `feature('CONTEXT_COLLAPSE')`
- `TerminalCaptureTool` — `feature('TERMINAL_PANEL')`
- `LSPTool` — `isEnvTruthy(process.env.ENABLE_LSP_TOOL)`
- `EnterWorktreeTool, ExitWorktreeTool` — `isWorktreeModeEnabled()`
- `ListPeersTool` — `feature('UDS_INBOX')`
- `TeamCreateTool, TeamDeleteTool` — `isAgentSwarmsEnabled()`
- `VerifyPlanExecutionTool` — `process.env.CLAUDE_CODE_VERIFY_PLAN === 'true'`
- `WorkflowTool` — `feature('WORKFLOW_SCRIPTS')`
- `SleepTool` — `feature('PROACTIVE') || feature('KAIROS')`
- `CronCreateTool, CronDeleteTool, CronListTool` — `feature('AGENT_TRIGGERS')`
- `RemoteTriggerTool` — `feature('AGENT_TRIGGERS_REMOTE')`
- `MonitorTool` — `feature('MONITOR_TOOL')`
- `SendUserFileTool` — `feature('KAIROS')`
- `PushNotificationTool` — `feature('KAIROS') || feature('KAIROS_PUSH_NOTIFICATION')`
- `SubscribePRTool` — `feature('KAIROS_GITHUB_WEBHOOKS')`
- `PowerShellTool` — `isPowerShellToolEnabled()` (Windows only)
- `SnipTool` — `feature('HISTORY_SNIP')`
- `ToolSearchTool` — `isToolSearchEnabledOptimistic()`
- `TestingPermissionTool` — `process.env.NODE_ENV === 'test'` only

---

### `getTools(permissionContext): Tools`

Filters `getAllBaseTools()` through mode-specific logic:

1. **Simple mode** (`CLAUDE_CODE_SIMPLE`):
   - If REPL mode is also enabled: returns `[REPLTool]` (plus TaskStop + SendMessage in coordinator mode)
   - Otherwise: returns `[BashTool, FileReadTool, FileEditTool]` (plus Agent + TaskStop + SendMessage in coordinator mode)

2. **Normal mode**:
   - Removes special tools (`ListMcpResourcesTool`, `ReadMcpResourceTool`, `SyntheticOutputTool`) from the base list
   - Applies `filterToolsByDenyRules()` to strip blanket-denied tools
   - If REPL mode is enabled: hides `REPL_ONLY_TOOLS` from direct access (they run inside the REPL VM)
   - Applies per-tool `isEnabled()` filter

---

### `assembleToolPool(permissionContext, mcpTools): Tools`

The **single source of truth** for combining built-in + MCP tools. Used by both `useMergedTools` (REPL) and `runAgent.ts` (coordinator workers).

1. Gets built-in tools via `getTools()` (mode filtering)
2. Filters MCP tools by deny rules via `filterToolsByDenyRules()`
3. **Sorts each partition for prompt-cache stability**: built-ins first (contiguous prefix), then MCP tools — each sorted by `name.localeCompare()`. Prevents MCP tools from interleaving into built-ins and invalidating cache keys.
4. Deduplicates by `name` via `uniqBy` — built-in tools take precedence (insertion order preservation).

---

### `filterToolsByDenyRules(tools, permissionContext): T[]`

Strips tools blanket-denied by permission rules. A tool is removed if there's a deny rule matching its name with no `ruleContent` (blanket deny). Uses the same matcher as the runtime permission check (step 1a), so MCP server-prefix rules like `mcp__server` strip all tools from that server before the model sees them.

Works on any object with `{ name, mcpInfo? }`.

---

### `getMergedTools(permissionContext, mcpTools): Tools`

Simple concatenation of built-in + MCP tools (no dedup, no sorting). Used for token counting and context where both categories matter.

---

### `TOOL_PRESETS` & `parseToolPreset()`

```typescript
export const TOOL_PRESETS = ['default'] as const
export type ToolPreset = (typeof TOOL_PRESETS)[number]

export function parseToolPreset(preset: string): ToolPreset | null
```

`getToolsForDefaultPreset()` returns names of all enabled base tools. CLI `--tools` flag uses this preset system.

---

### Exported Constants

```typescript
export {
  ALL_AGENT_DISALLOWED_TOOLS,
  CUSTOM_AGENT_DISALLOWED_TOOLS,
  ASYNC_AGENT_ALLOWED_TOOLS,
  COORDINATOR_MODE_ALLOWED_TOOLS,
} from './constants/tools.js'
```

These lists control which tools are available in different agent execution contexts (subagents, async agents, coordinator workers).

---

### Conditional Import Pattern

Many tools use the `feature()` and `process.env` pattern for dead code elimination:
```typescript
const SleepTool = feature('PROACTIVE') || feature('KAIROS')
  ? require('./tools/SleepTool/SleepTool.js').SleepTool
  : null
```
The `bun:bundle` `feature()` function is resolved at build time and eliminated from the bundle when the feature is off. Tools gated by `process.env` similarly tree-shake.
