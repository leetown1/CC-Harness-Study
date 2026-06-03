# Other Tools

All remaining tools covering MCP integration, LSP operations, skill execution, configuration, plan/worktree management, cron scheduling, team management, and more.

---

## MCPTool (`src/tools/MCPTool/`)

**Location**: `src/tools/MCPTool/MCPTool.ts`

A generic wrapper that adapts MCP server tools into the Claude Code Tool interface. Every MCP tool exposed by a connected MCP server gets wrapped in an MCPTool instance.

### Key Characteristics
- `isMcp: true` — Identifies this as an MCP-sourced tool
- `mcpInfo: { serverName, toolName }` — Original MCP identity (unnormalized)
- `inputJSONSchema` — Uses raw JSON Schema from the MCP server (not Zod)
- `name` format: `mcp__<server>__<tool>` by default, can be unprefixed in SDK mode
- Dynamically generated `call()` that invokes the MCP server via `callTool()`
- Progress support: Emits `MCPProgress` events for long-running MCP operations
- Permission checks delegate to the general permission system with MCP-aware prefix matching

### Sub-files

#### `classifyForCollapse.ts`
Tool result classification for UI collapsing:
- Contains a 600+ tool allowlist mapping MCP tool names to display categories
- Determines whether MCP tool results should be collapsed into compact summaries
- Categories: search results, file listings, database queries, API responses, etc.
- Unknown tools default to non-collapsed rendering

#### `UI.tsx` (403 lines)
JSON-aware rendering:
- `renderToolUseMessage` — MCP tool invocation with server name badge
- `renderToolResultMessage` — JSON flattening and structured result display
- `renderToolUseProgressMessage` — MCP progress display
- `renderToolUseErrorMessage` — MCP error with server context
- JSON structure detection and nested object flattener for readable display

#### `prompt.ts`
MCP tool prompt generation with server-specific instructions.

---

## McpAuthTool (`src/tools/McpAuthTool/McpAuthTool.ts`, 215 lines)

OAuth authentication for MCP servers supporting the MCP auth flow.

### Input Schema
```typescript
z.object({})  // No user-facing parameters
```

### Output Type
```typescript
type McpAuthOutput = {
  status: 'auth_url' | 'unsupported' | 'error'
  message: string
  authUrl?: string
}
```

### Core Execution
1. Checks if the MCP server supports OAuth
2. Initiates `performMCPOAuthFlow()` for auth-capable servers
3. Opens the authorization URL for user interaction
4. Clears MCP auth cache on auth completion
5. Triggers `reconnectMcpServerImpl()` to reconnect with new credentials
6. Returns auth URL for display, or error/unsupported status

---

## LSPTool (`src/tools/LSPTool/`, 6 files)

**Name**: `LSP_TOOL_NAME`
**Enabled**: When `process.env.ENABLE_LSP_TOOL` is truthy

Provides 9 LSP operations as tool calls, each activating a specific language server capability.

### 9 Operations

| Operation | LSP Capability | Description |
|-----------|---------------|-------------|
| `definitions` | `textDocument/definition` | Go to definition |
| `references` | `textDocument/references` | Find all references |
| `implementations` | `textDocument/implementation` | Go to implementation |
| `hover` | `textDocument/hover` | Hover information |
| `type_definition` | `textDocument/typeDefinition` | Go to type definition |
| `document_symbols` | `textDocument/documentSymbol` | Document symbol outline |
| `workspace_symbols` | `workspace/symbol` | Workspace-wide symbol search |
| `call_hierarchy_incoming` | `callHierarchy/incomingCalls` | Incoming call hierarchy |
| `call_hierarchy_outgoing` | `callHierarchy/outgoingCalls` | Outgoing call hierarchy |

### Input Schema (from `schemas.ts`)

Discriminated union on `operation` with 9 operation-specific subtypes:
```typescript
z.discriminatedUnion('operation', [
  z.object({ operation: z.literal('definitions'), uri: z.string(), line: z.number(), character: z.number() }),
  z.object({ operation: z.literal('references'), uri: z.string(), line: z.number(), character: z.number() }),
  z.object({ operation: z.literal('hover'), uri: z.string(), line: z.number(), character: z.number() }),
  // ... etc.
])
```

Includes `contextLines` for adding surrounding source context to results.

### Sub-files

#### `LSPTool.ts`
Main tool implementation:
- Routes `operation` to corresponding LSP manager methods
- Handles URI resolution (file paths → `file://` URIs)
- Processes and formats LSP responses
- Filters results by language/relevance
- Error handling for LSP server unavailability

#### `formatters.ts` (592 lines)
Result formatters for each operation type:
- Symbol formatting with kind icons
- Location formatting with file path + line + context
- Call hierarchy tree formatting
- Hover content markdown rendering
- Context line extraction and annotation

#### `schemas.ts` (215 lines)
Zod schema definitions:
- Discriminated union for all 9 operations
- URI, position, and context line parameter schemas
- Output schemas for each operation result type

#### `symbolContext.ts`
Symbol context extraction and enrichment:
- Surrounding code context for symbol results
- Type-aware symbol categorization
- Relevance scoring for search results

#### `prompt.ts`
LSP tool usage prompt with operation descriptions and URI format documentation.

#### `UI.tsx`
- `userFacingName` — "LSP"
- `renderToolUseMessage` — Operation display with file position
- `renderToolResultMessage` — Formatted results (definitions, references, symbols)
- `renderToolUseErrorMessage` — LSP error display

---

## SkillTool (`src/tools/SkillTool/SkillTool.ts`, 1108 lines)

**Name**: `SKILL_TOOL_NAME`
**Concurrency Safe**: No (default)
**Read Only**: No (default)
**Max Result Size**: Not explicitly set

Executes slash-command skills (both built-in and custom). Supports three execution modes: inline, forked, and remote.

### Input Schema
```typescript
z.object({
  command: z.string(),  // Skill name (slash command)
  // ... command-specific parameters
})
```

### Execution Modes

1. **Inline Execution**: Runs the skill's commands directly in the current agent context. Lightweight, shares context with parent. Used for simple, fast skills.

2. **Forked Execution**: Runs the skill as a subagent via `runAgent()`. Gets its own tool set, system prompt, and context budget. Used for complex skills that need independent reasoning. Uses `prepareForkedCommandContext()` for context isolation.

3. **Remote Execution**: Runs the skill via the remote agent infrastructure. Used for skills that need additional resources or isolation.

### Core Execution Flow

1. **Command lookup**: `findCommand(name)` searches built-in commands and custom commands
2. **MCP skill integration**: `getAllCommands()` includes MCP-loaded skills/prompts from `appState.mcp.commands` (filtered to MCP-loaded prompts only)
3. **Skill resolution**: Parses the skill definition (frontmatter parsing for custom skills)
4. **Model resolution**: `resolveSkillModelOverride()` applies skill-specific model preferences
5. **Plugin identification**: `parsePluginIdentifier()` for plugin-sourced skills
6. **Execution dispatch**: Inline/forked/remote based on skill configuration and context
7. **Result extraction**: `extractResultText()` for forked skill output
8. **Telemetry**: `recordSkillUsage()` + `buildPluginCommandTelemetryFields()` for analytics
9. **Invocation tracking**: `addInvokedSkill()` for session-scoped skill usage tracking

### MCP Skill Integration

MCP servers can expose `prompts` which are loaded as skills:
- Loaded from `appState.mcp.commands` with `loadedFrom === 'mcp'`
- Appended to local commands via `uniqBy(name)`
- Before filtering: model could invoke MCP prompts via guessed `mcp__server__prompt` names; now only discoverable through the commands list

### Sub-files

- **`constants.ts`**: `SKILL_TOOL_NAME`
- **`prompt.ts`** (241 lines): Budget-aware skill prompt truncation — dynamically adjusts prompt length based on available context budget
- **`UI.tsx`**: `userFacingName`, `renderToolUseMessage`, `renderToolUseResultMessage`, `renderToolUseProgressMessage`, `renderToolUseRejectedMessage`, `renderToolUseErrorMessage`

---

## ToolSearchTool (`src/tools/ToolSearchTool/ToolSearchTool.ts`, 471 lines)

**Name**: `TOOL_SEARCH_TOOL_NAME`
**Deferred**: Not deferred (must always be available for tool discovery)
**Concurrency Safe**: Yes
**Read Only**: Yes

Enables the model to discover tools by keyword search. This tool is the gateway to the deferred loading system — when ToolSearch is active, tools with `shouldDefer: true` don't appear in the initial prompt.

### Input Schema
```typescript
{
  query: z.string(),  // Search keywords (matches against tool name, searchHint, description)
}
```

### Output Schema
```typescript
{
  results: z.array(z.object({
    name: z.string(),
    description: z.string(),
    searchHint: z.string().optional(),
    inputSchema: z.record(z.unknown()),
    // ... abbreviated tool info
  })),
}
```

### Core Execution

1. Searches `getAllBaseTools()` + MCP tools for keyword matches
2. Matching strategy: token-level fuzzy matching against `name`, `searchHint`, `description`
3. Results include the tool's full input schema (so the model can make immediate use)
4. Excludes tools that are currently in the prompt (prevents redundant discovery)
5. Limits result count to prevent context bloat

### Sub-files

- **`constants.ts`**: `TOOL_SEARCH_TOOL_NAME`
- **`prompt.ts`**: Usage instructions for the tool search mechanism

---

## BriefTool (`src/tools/BriefTool/BriefTool.ts`, 204 lines)

**Name**: Variable (represents the `SendUserMessage` capability)

Sends messages to the user without using the normal assistant response channel. Used for direct user communication outside of turn boundaries.

### Sub-files

- **`attachments.ts`**: Attachment handling for brief messages (file sharing, image display)
- **`upload.ts`**: File upload integration for brief content
- **`UI.tsx`**: Message display with user-facing formatting

---

## SyntheticOutputTool (`src/tools/SyntheticOutputTool/SyntheticOutputTool.ts`, 163 lines)

**Name**: `SYNTHETIC_OUTPUT_TOOL_NAME`

Produces structured output for SDK/CLI consumers. Used when the model needs to return structured data (JSON) rather than conversational text.

### Validation
Uses Ajv (JSON Schema validator) to validate the structured output against the expected schema before returning.

---

## ConfigTool (`src/tools/ConfigTool/ConfigTool.ts`, 467 lines)

**Name**: `CONFIG_TOOL_NAME`
**Available**: Ant users only (`process.env.USER_TYPE === 'ant'`)

Get and set Claude Code configuration values. Reads from and writes to `.claude/settings.json` and related configuration files.

### Operations
- **Get**: Read current configuration value for a setting
- **Set**: Write a new value (with validation)
- **List**: Show all supported settings

### Sub-files

- **`supportedSettings.ts`** (211 lines): Complete registry of all supported settings with types, defaults, descriptions, and validation rules

---

## Plan Mode Tools

### EnterPlanModeTool (`src/tools/EnterPlanModeTool/EnterPlanModeTool.ts`, 126 lines)

**Name**: `ENTER_PLAN_MODE_TOOL_NAME`

Transitions the agent into plan mode. In plan mode:
- The agent proposes changes without executing them
- All write tools are gated behind plan approval
- The agent generates structured plans for user review
- Permission mode is saved to `prePlanMode` for restoration on exit

### ExitPlanModeV2Tool (`src/tools/ExitPlanModeTool/ExitPlanModeV2Tool.ts`, 493 lines)

**Name**: `EXIT_PLAN_MODE_V2_TOOL_NAME`

Exits plan mode and transitions to execution:
- Validates that the plan was approved
- Restores the pre-plan permission mode
- Begins executing the approved plan
- Handles plan rejection gracefully

---

## Worktree Management Tools

### EnterWorktreeTool (`src/tools/EnterWorktreeTool/EnterWorktreeTool.ts`, 127 lines)

**Name**: `ENTER_WORKTREE_TOOL_NAME`
**Available**: When `isWorktreeModeEnabled()`

Creates a git worktree for isolated operations:
- Creates temporary git worktree at a unique path
- Initializes the working directory for the worktree
- Sets up environment for worktree-isolated operations
- Returns worktree path for subsequent operations

### ExitWorktreeTool (`src/tools/ExitWorktreeTool/ExitWorktreeTool.ts`, 329 lines)

**Name**: `EXIT_WORKTREE_TOOL_NAME`

Cleans up a git worktree:
- Removes the worktree directory
- Runs `git worktree prune` to clean references
- Handles dirty worktree warnings (uncommitted changes)

---

## AskUserQuestionTool (`src/tools/AskUserQuestionTool/AskUserQuestionTool.tsx`, 266 lines)

**Name**: `ASK_USER_QUESTION_TOOL_NAME`  
**Deferred**: Yes (`shouldDefer: true`)  
**Requires User Interaction**: Yes  
**Read Only**: Yes (collects user input, no side effects)

Presents 1–4 multiple-choice questions to the user via the permission UI. Used by `/init`, plan flows, and any model path needing structured user decisions.

### Input Schema
```typescript
z.strictObject({
  questions: z.array(questionSchema).min(1).max(4),  // Each: question, header, options[2-4], multiSelect?
  answers: z.record(z.string(), z.string()).optional(),  // Filled by permission component
  annotations: z.record(...).optional(),  // Per-question preview/notes
  metadata: z.object({ source: z.string().optional() }).optional(),
})
```

### Core Execution
1. **`checkPermissions`**: Always returns `behavior: 'ask'` — opens multiple-choice dialog
2. **`call`**: Returns user answers collected by permission component (questions + answers + optional annotations)
3. **`mapToolResultToToolResultBlockParam`**: Formats answers as model-facing tool result text
4. **`validateInput`**: When preview format is HTML, validates option previews via `validateHtmlPreview()` (no full documents, no script/style tags)
5. **`isEnabled`**: Disabled when KAIROS channels active (Telegram/Discord) — no TUI user present

### Sub-files
- **`prompt.ts`**: `DESCRIPTION`, `ASK_USER_QUESTION_TOOL_PROMPT`, preview feature prompts
- **`UI.tsx`**: Result rendering via `AskUserQuestionResultMessage`

---

## REPLTool (`src/tools/REPLTool/`)

**Name**: `REPL_TOOL_NAME`
**Available**: Ant users only (`process.env.USER_TYPE === 'ant'`)

A virtualized REPL (Read-Eval-Print-Loop) tool that wraps the primitive tools (Bash, Read, Edit) in an isolated VM context. When active:
- `REPL_ONLY_TOOLS` are hidden from direct use (only accessible inside REPL)
- The REPL provides a sandboxed execution environment
- All tool operations within the REPL go through the VM bridge

### Sub-files

- **`constants.ts`**: `REPL_TOOL_NAME`, `REPL_ONLY_TOOLS`, `isReplModeEnabled()`
- **`REPLTool.tsx`**: Main tool implementation
- **`primitiveTools.ts`** (39 lines): Exports `getReplPrimitiveTools()` — lazy getter returning the 8 primitive tools (FileRead, FileWrite, FileEdit, Glob, Grep, Bash, NotebookEdit, AgentTool) accessible inside the REPL VM. Used by collapse/render code when REPL-only tools are filtered from the execution pool.

---

## ScheduleCronTool (`src/tools/ScheduleCronTool/`, 5 files)

**Available**: When `feature('AGENT_TRIGGERS')` is active

Cron-based agent scheduling with durable storage.

### `CronCreateTool.ts` (157 lines)
**Name**: `CRON_CREATE_TOOL_NAME` | **Deferred**: Yes

Creates a cron schedule for recurring or one-shot agent prompts:
- **Input**: `cron` (5-field expression), `prompt`, `recurring` (default true), `durable` (persist to `.claude/scheduled_tasks.json`)
- Validates cron via `parseCronExpression()`, enforces `MAX_JOBS` (50)
- Calls `addCronTask()`; enables scheduled tasks via `setScheduledTasksEnabled(true)`

### `CronDeleteTool.ts` (95 lines)
**Name**: `CRON_DELETE_TOOL_NAME` | **Deferred**: Yes

Deletes a scheduled cron by ID. Validates task exists before removal.

### `CronListTool.ts` (97 lines)
**Name**: `CRON_LIST_TOOL_NAME` | **Deferred**: Yes

Lists all cron tasks via `listAllCronTasks()` with human-readable schedules (`cronToHuman`) and next run times (`nextCronRunMs`).

### Sub-files

- **`prompt.ts`**: Cron usage instructions, tool names, `DEFAULT_MAX_AGE_DAYS`, feature gates (`isDurableCronEnabled`, `isKairosCronEnabled`)
- **`UI.tsx`**: Schedule display with cron expression formatting (`renderCreateToolUseMessage`, `renderCreateResultMessage`)

---

## RemoteTriggerTool (`src/tools/RemoteTriggerTool/RemoteTriggerTool.ts`, 161 lines)

**Available**: When `feature('AGENT_TRIGGERS_REMOTE')` is active

Manages remote agent triggers. Allows external systems to trigger agent runs via webhooks or API calls.

---

## ListMcpResourcesTool & ReadMcpResourceTool

### ListMcpResourcesTool (`src/tools/ListMcpResourcesTool/ListMcpResourcesTool.ts`, 123 lines)

Lists available MCP resources across all connected MCP servers. Resources are server-exposed data sources (files, databases, APIs).

### ReadMcpResourceTool (`src/tools/ReadMcpResourceTool/ReadMcpResourceTool.ts`, 158 lines)

Reads content from a specific MCP resource by URI. Handles MCP resource protocol negotiation and content type detection.

---

## Team Management Tools

### TeamCreateTool (`src/tools/TeamCreateTool/TeamCreateTool.ts`, 240 lines)

**Available**: When `isAgentSwarmsEnabled()`

Creates a multi-agent team with:
- Team name and composition
- Permission mode for the team
- Agent role assignments
- Team configuration persistence

### TeamDeleteTool (`src/tools/TeamDeleteTool/TeamDeleteTool.ts`, 139 lines)

Deletes a team and cleans up associated resources.

---

## SleepTool (`src/tools/SleepTool/SleepTool.ts`, 17 lines)

**Available**: When `feature('PROACTIVE') || feature('KAIROS')`

A minimal tool that sleeps for a specified duration. Used by proactive/kairos agents for timed waiting between operations.

### Input Schema
```typescript
{
  seconds: z.number(),  // Duration to sleep
}
```

---

## TestingPermissionTool (`src/tools/testing/TestingPermissionTool.tsx`, 74 lines)

**Name**: `TestingPermission`  
**Available**: `process.env.NODE_ENV === 'test'` only (compiled as `"production" === 'test'`)

Test-only tool that always triggers the permission dialog (`checkPermissions` → `behavior: 'ask'`). Empty input schema. Used for end-to-end permission flow testing — never included in production bundles.

---

## Feature-Gated Tools (Ant + Feature Flag)

These tools are only available under specific conditions and are tree-shaken at bundle time when the feature is off:

| Tool | Gate | Description |
|------|------|-------------|
| `SuggestBackgroundPRTool` | `USER_TYPE === 'ant'` | Suggests creating PRs for background work |
| `WebBrowserTool` | `feature('WEB_BROWSER_TOOL')` | Opens URLs in a web browser |
| `OverflowTestTool` | `feature('OVERFLOW_TEST_TOOL')` | Tests context overflow handling |
| `CtxInspectTool` | `feature('CONTEXT_COLLAPSE')` | Inspects context compression state |
| `TerminalCaptureTool` | `feature('TERMINAL_PANEL')` | Captures terminal output |
| `TungstenTool` | `USER_TYPE === 'ant'` | Ant-specific internal tool |
| `VerifyPlanExecutionTool` | `CLAUDE_CODE_VERIFY_PLAN === 'true'` | Verifies plan execution fidelity |
| `ListPeersTool` | `feature('UDS_INBOX')` | Lists UDS peer agents |
| `SnipTool` | `feature('HISTORY_SNIP')` | Snips conversation history |
| `WorkflowTool` | `feature('WORKFLOW_SCRIPTS')` | Workflow script execution |
| `SendUserFileTool` | `feature('KAIROS')` | Sends files to users |
| `PushNotificationTool` | `feature('KAIROS') \|\| feature('KAIROS_PUSH_NOTIFICATION')` | Sends push notifications |
| `SubscribePRTool` | `feature('KAIROS_GITHUB_WEBHOOKS')` | Subscribes to GitHub PR webhooks |
| `MonitorTool` | `feature('MONITOR_TOOL')` | System monitoring |

See dedicated sections above for `AskUserQuestionTool`, `TestingPermissionTool`, and `ScheduleCronTool` (not repeated in this table).

---

## Tool Utilities (`src/tools/utils.ts`)

Shared utility belt for the tool system:
- `getToolUseIDFromParentMessage()` — Extracts tool use ID from parent assistant message
- `tagMessagesWithToolUseID()` — Tags message objects with their originating tool use ID

---

## Tool Service Layer (`src/services/tools/`)

Five service files supporting tool execution infrastructure:

### `toolExecution.ts`
Core execution pipeline:
- Schedules tool calls with concurrency control
- Handles tool result serialization/deserialization
- Integrates with the permission system

### `toolHooks.ts`
Hook system for tool execution lifecycle:
- Pre-tool-use hooks (modify input, approve/reject)
- Post-tool-use hooks (modify output, trigger side effects)
- Hook condition matching (tool name patterns, input matching)

### `toolOrchestration.ts`
Coordinates parallel tool execution:
- Groups independent tool calls
- Manages execution ordering constraints
- Handles tool result merging

### `StreamingToolExecutor.ts`
Streaming-aware tool execution:
- Handles tools that produce incremental output
- Progress event streaming
- Partial result delivery

### `toolUseSummaryGenerator.ts`
Generates compact summaries of tool use sequences for display in the UI header and for analytics tracking.
