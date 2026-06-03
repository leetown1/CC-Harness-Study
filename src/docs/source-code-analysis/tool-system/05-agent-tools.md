# Agent & Task Tools

The agent subsystem enables subagent spawning, task management, inter-agent messaging, and coordination. This is the most architecturally complex subsystem, spanning 15+ files.

---

## AgentTool (`src/tools/AgentTool/AgentTool.tsx`, 1398 lines)

**Name**: `AGENT_TOOL_NAME` (+ `LEGACY_AGENT_TOOL_NAME` alias)
**Search Hint**: Not set (always loaded)
**Concurrency Safe**: No
**Read Only**: No (default)
**Max Result Size**: Implicitly bounded
**Strict Mode**: Not set

The primary mechanism for spawning subagents. Supports five distinct execution modes with varying isolation, tool sets, and lifecycle management.

### Input Schema (Full)

Base fields + multi-agent extensions + isolation options:

```typescript
// Base
{
  description: z.string(),              // 3-5 word task description
  prompt: z.string(),                   // Agent task prompt
  subagent_type: z.string().optional(), // Specialized agent type
  model: z.enum(['sonnet', 'opus', 'haiku']).optional(), // Model override
  run_in_background: z.boolean().optional(), // Background execution
}
// Multi-agent (gated by isAgentSwarmsEnabled)
{
  name: z.string().optional(),          // Addressable agent name
  team_name: z.string().optional(),     // Team context (default: current)
  mode: permissionModeSchema().optional(), // Permission mode for teammate
}
// Isolation
{
  isolation: z.enum(['worktree', 'remote']).optional(),  // Isolation mode
  cwd: z.string().optional(),           // Working directory override
}
```

### Execution Modes

#### 1. Async Background Subagent
- Triggered by `run_in_background: true`
- Launched via `registerAsyncAgent()`
- Returns immediately with a task ID
- Progress tracked via `createProgressTracker()`
- Completion notified via `enqueueAgentNotification()`

#### 2. Forked Subagent (FORK_AGENT)
- Gated by `isForkSubagentEnabled()`
- Creates a git worktree for isolation (`createAgentWorktree()`)
- Clones the parent's readFileState, contentReplacementState
- Builds forked messages from parent context
- Runs as async agent in the worktree
- Worktree cleaned up on completion via `removeAgentWorktree()`

#### 3. Inline Synchronous Agent
- Runs `runAgent()` directly in the current process
- Shared context with parent (readFileState, fileHistoryState, etc.)
- Tool filtering via `filterToolsForAgent()`

#### 4. Remote Agent (CCR)
- Gated by `checkRemoteAgentEligibility()`
- Launched via `registerRemoteAgentTask()`
- Returns session URL for monitoring
- Always runs in background

#### 5. Teammate (Multi-Agent)
- Gated by `isAgentSwarmsEnabled()`
- Launched via `spawnTeammate()` from `shared/spawnMultiAgent.ts`
- Creates an addressable agent with SendMessage support
- Team-based permission and context sharing

### Core Execution Flow (`call()`)

```
call()
  ├── subagent_type resolution (default: general-purpose → GENERAL_PURPOSE_AGENT)
  ├── Agent filtering: filterAgentsByMcpRequirements(), filterDeniedAgents()
  ├── Teammate path: spawnTeammate()
  ├── Fork path: buildForkedMessages() → registerAsyncAgent() with worktree
  ├── Remote path: checkRemoteAgentEligibility() → registerRemoteAgentTask()
  ├── Async path: registerAsyncAgent() with background lifecycle
  └── Inline path: runAgent() directly
```

### Auto-Backgrounding

When `CLAUDE_AUTO_BACKGROUND_TASKS` or `tengu_auto_background_agents` is active, background-capable agents auto-background after 120,000ms.

### Tool Filtering

Agents receive a filtered tool set based on:
- `ALL_AGENT_DISALLOWED_TOOLS` — Never available to any subagent
- `CUSTOM_AGENT_DISALLOWED_TOOLS` — Disallowed for custom user-defined agents
- `ASYNC_AGENT_ALLOWED_TOOLS` — Only these tools available to async agents
- Mode-specific filtering (coordinator vs. worker patterns)

### Sub-files (14 supplementary files)

#### `builtInAgents.ts`
Agent registry:
- `GENERAL_PURPOSE_AGENT` — Default fallback agent
- `STATUSLINE_SETUP_AGENT` — Statusline configuration assistant
- `EXPLORE_AGENT` — Repository exploration agent
- `PLAN_AGENT` — Planning agent
- `CLAUDE_CODE_GUIDE_AGENT` — Claude Code usage guide
- `ONE_SHOT_BUILTIN_AGENT_TYPES` — Single-use agent type identifiers

#### `built-in/` directory
Individual agent definitions as markdown/frontmatter:
- `generalPurposeAgent.ts` — Universal task agent
- `statuslineSetup.ts` — Statusline theme configuration
- `exploreAgent.ts` — Codebase navigation and discovery
- `planAgent.ts` — Strategic planning and architecture
- `verificationAgent.ts` — Code review and validation
- `claudeCodeGuideAgent.ts` — Self-referential usage guidance

#### `runAgent.ts` (973 lines)
**Core agent runner** — the execution engine for all subagents:

- **System prompt assembly**: `buildEffectiveSystemPrompt()` with agent-specific instructions, tool descriptions, permission context, and environment details
- **MCP initialization**: Sets up MCP server connections for the agent
- **Hook integration**: Registers pre/post tool use hooks for the agent session
- **Skill preloading**: Loads applicable skill definitions
- **Message loop**: Iterates conversation turns with the model, processing tool calls and responses
- **Tool execution**: Runs tools through the execution pipeline with permission checks
- **Context management**: Handles context budget, compaction, and content replacement
- **Agent termination**: Detects completion conditions (task done, max turns, error)

#### `forkSubagent.ts` (210 lines)
Fork subagent experiment:
- `isForkSubagentEnabled()` — Feature gate check
- `isInForkChild()` — Whether the current process is a fork child
- `buildForkedMessages()` — Assembles parent messages for fork context
- `buildWorktreeNotice()` — System message informing the agent about its worktree
- `FORK_AGENT` — Agent type constant

#### `resumeAgent.ts` (265 lines)
Resume stopped agents:
- `resumeAgent()` — Reconstructs agent state from saved records
- `resumeAgentBackground()` — Background-resume path for async agents
- Handles state reconstruction from sidechain records (for async subagents whose setAppState is a no-op)

#### `agentMemory.ts` (177 lines)
Persistent agent memory:
- Reads/writes agent memory from `~/.claude/agent-memory/`
- Memory key-value store with serialization
- Session-scoped memory persistence

#### `agentMemorySnapshot.ts` (197 lines)
Snapshot sync:
- Captures and restores agent memory snapshots
- Synchronizes memory state between parent and child agents
- Used for fork/teammate memory sharing

#### `agentToolUtils.ts` (686 lines)
Utility belt for agent tool operations:
- `finalizeAgentTool()` — Result finalization and output construction
- `runAsyncAgentLifecycle()` — Full async agent lifecycle management
- `filterToolsForAgent()` — Tool filtering based on agent type and context
- `classifyHandoffIfNeeded()` — Detects coordinator task handoff
- `emitTaskProgress()` — Progress event emission for task tracking
- `extractPartialResult()` — Partial result extraction from incomplete agents
- `getLastToolUseName()` — Gets the final tool invocation name
- `agentToolResultSchema()` — Zod schema for agent tool results
- `createProgressTracker()` — Creates per-agent progress trackers
- `createActivityDescriptionResolver()` — Resolves activity descriptions from agent state
- `getProgressUpdate()` / `updateProgressFromMessage()` — Progress state management
- `getTokenCountFromTracker()` — Token consumption tracking
- `isLocalAgentTask()` — Local vs. remote agent detection

#### `agentDisplay.ts` (104 lines)
Display formatting:
- `formatAgentSummary()` — Formats agent output for display
- `formatAgentResult()` — Rich result rendering

#### `agentColorManager.ts` (66 lines)
Color mapping:
- `setAgentColor()` — Assigns a consistent color to an agent ID
- `getAgentColor()` — Retrieves assigned color
- Color palette management for multi-agent displays

#### `loadAgentsDir.ts` (755 lines)
Load agent definitions from markdown/JSON/plugins:
- Parses frontmatter from markdown agent definitions
- Loads from `.claude/agents/` directory
- Loads from plugin agent directories
- `filterAgentsByMcpRequirements()` — Filters agents requiring unavailable MCP servers
- `hasRequiredMcpServers()` — Checks MCP server availability
- `isBuiltInAgent()` — Distinguishes built-in from user-defined agents
- `AgentDefinition`, `AgentDefinitionsResult` types

#### `constants.ts`
- `AGENT_TOOL_NAME`, `LEGACY_AGENT_TOOL_NAME`
- `ONE_SHOT_BUILTIN_AGENT_TYPES`

#### `prompt.ts`
- `getPrompt()` — Agent tool prompt with usage instructions, model guidance, and subagent type catalog

#### `UI.tsx`
- `userFacingName` — Agent type name or "Agent"
- `userFacingNameBackgroundColor` — Agent-specific color
- `renderToolUseMessage` — Agent launch display with description, model, mode
- `renderToolUseTag` — Timeout/model/resume ID tag
- `renderToolUseProgressMessage` — Live agent progress with status
- `renderToolUseRejectedMessage` — Agent rejection display
- `renderToolUseErrorMessage` — Agent error display
- `renderToolResultMessage` — Agent completion with summary
- `renderGroupedAgentToolUse` — Groups multiple parallel agent launches

---

## Task Management Tools

Six tools for creating, listing, getting, updating, stopping, and reading task output.

### TaskCreateTool (`src/tools/TaskCreateTool/TaskCreateTool.ts`)

Creates a new task with description, subagent type, and optional background execution. V2 todo system compatible. Sets up task metadata and registers with the task tracking infrastructure.

### TaskGetTool (`src/tools/TaskGetTool/TaskGetTool.ts`)

Retrieves the current state, progress, and output of a specific task by ID.

### TaskListTool (`src/tools/TaskListTool/TaskListTool.ts`)

Lists all active and completed tasks with status summaries.

### TaskUpdateTool (`src/tools/TaskUpdateTool/TaskUpdateTool.ts`)

Updates task metadata (status, description, priority).

### TaskStopTool (`src/tools/TaskStopTool/TaskStopTool.ts`)

Stops a running task by ID. Sends abort signal to the task's abort controller. Handles cleanup of background agent resources.

### TaskOutputTool (`src/tools/TaskOutputTool/TaskOutputTool.tsx`, 584 lines)

**Name**: `TASK_OUTPUT_TOOL_NAME`  
**Concurrency Safe**: Yes  
**Read Only**: Yes (reads task output only)

Reads accumulated output from background tasks (local bash, local agent, remote agent). Supports blocking wait with timeout and non-blocking peek.

#### Input Schema
```typescript
z.strictObject({
  task_id: z.string(),
  block: semanticBoolean(z.boolean().default(true)),  // Wait for completion
  timeout: z.number().min(0).max(600000).default(30000),
})
```

#### Output Schema
```typescript
{
  retrieval_status: 'success' | 'timeout' | 'not_ready',
  task: {
    task_id, task_type, status, description, output,
    exitCode?, error?, prompt?, result?
  } | null
}
```

#### Core Execution
1. Resolves task by `task_id` from task framework
2. If `block: true`, polls until task completes or `timeout` elapses
3. For `local_bash` tasks, merges stdout/stderr from shell command or disk output path
4. For agent tasks, includes prompt/result fields when available
5. Formats output via `formatTaskOutput()` with type-specific rendering in `UI.tsx`

#### Sub-files
- **`constants.ts`**: `TASK_OUTPUT_TOOL_NAME`
- **`prompt.ts`**: Usage instructions for blocking vs non-blocking reads
- **`UI.tsx`**: Renders bash output (`BashToolResultMessage`) and agent output (`AgentPromptDisplay` / `AgentResponseDisplay`)

### TodoWriteTool (`src/tools/TodoWriteTool/TodoWriteTool.ts`)

Writes/updates the structured todo list for the current session. Integrates with the sidebar todo panel. Results are surfaced in the todo UI panel (not the transcript), so `renderToolResultMessage` is intentionally omitted from the tool — the UI updates via the todo panel instead.

---

## SendMessageTool (`src/tools/SendMessageTool/SendMessageTool.ts`, 917 lines)

**Name**: `SEND_MESSAGE_TOOL_NAME`
**Concurrency Safe**: No (default)
**Read Only**: No (default)
**Max Result Size**: Not explicitly set
**Deferred**: Not deferred

Inter-agent messaging, broadcast, shutdown coordination, and plan approval. The communication backbone for multi-agent teams.

### Input Schema
```typescript
z.object({
  to: z.string(),            // Recipient: teammate name, "*" (broadcast), "uds:<path>", "bridge:<id>"
  summary: z.string().optional(), // 5-10 word preview for UI
  message: z.union([
    z.string(),               // Plain text
    StructuredMessage(),      // Typed structured messages
  ]),
})
```

### Structured Message Types

```typescript
z.discriminatedUnion('type', [
  // Shutdown protocol
  z.object({
    type: z.literal('shutdown_request'),
    reason: z.string().optional(),
  }),
  z.object({
    type: z.literal('shutdown_response'),
    request_id: z.string(),
    approve: semanticBoolean(),
    reason: z.string().optional(),
  }),
  // Plan approval protocol
  z.object({
    type: z.literal('plan_approval_response'),
    request_id: z.string(),
    approve: semanticBoolean(),
    feedback: z.string().optional(),
  }),
])
```

### Routing Mechanisms

| Prefix | Target | Mechanism |
|--------|--------|-----------|
| `*` | Broadcast | All teammates via `writeToMailbox()` to each |
| `uds:<path>` | UDS peer | Unix Domain Socket bridge |
| `bridge:<id>` | Remote peer | Remote Control bridge session |
| `<name>` | Named teammate | Direct mailbox via `writeToMailbox()` |

### Core Execution Flow

1. **Address parsing**: `parseAddress(to)` resolves the routing mechanism
2. **Sender identity**: `getAgentName()` + `getTeammateColor()`
3. **Target resolution**: For named teammates, finds via `findTeammateTaskByAgentId()`
4. **Local agent check**: `isLocalAgentTask()` for direct delivery; `queuePendingMessage()` for poll-based agents
5. **Mailbox delivery**: `writeToMailbox()` writes to the agent's mailbox file
6. **UDS delivery**: Uses `replBridgeHandle` for UDS peer communication
7. **Bridge delivery**: Uses bridge transport for remote peers
8. **Shutdown protocol**: `gracefulShutdown()` integration — sends shutdown requests to all teammates, collects responses
9. **Plan approval**: Routes plan approval responses to the requesting agent

### Broadcast Semantics

When `to: "*"`, the message is delivered to all teammates except the sender. Each teammate receives the message in their mailbox with sender identity preserved.

### Shutdown Protocol

A two-phase protocol:
1. Agent sends `shutdown_request` to another agent or broadcasts
2. Recipients respond with `shutdown_response` (`approve: true/false`)
3. Requester collects responses; if all approve, proceeds with shutdown

### Plan Approval Protocol

Agents in plan mode send plan proposals; the approver responds with `plan_approval_response` (`approve: true/false` + optional `feedback`).

### Sub-files

- **`constants.ts`**: `SEND_MESSAGE_TOOL_NAME`
- **`prompt.ts`**: `DESCRIPTION`, `getPrompt()` — messaging usage guide, protocol documentation
- **`UI.tsx`**: `userFacingName`, `renderToolUseMessage` (message envelope display), `renderToolResultMessage` (delivery confirmation)

---

## Supporting Infrastructure

### `shared/spawnMultiAgent.ts`
Multi-agent spawning orchestration. Creates teammates with team context, permission inheritance, and tool pool assembly.

### `shared/gitOperationTracking.ts`
Git operation tracking hook shared across BashTool, PowerShellTool, and agent operations. Tracks git commands for safety and analytics.

### `utils/agentContext.ts`
Agent context propagation utilities:
- `runWithAgentContext()` — Executes code within a specific agent's context
- `getAgentContext()` — Retrieves current agent context for the active thread

### `tasks/LocalAgentTask/`
Local agent task lifecycle management:
- `registerAsyncAgent()` — Registers and launches background agent
- `completeAgentTask()` — Marks agent as complete
- `failAgentTask()` — Marks agent as failed
- `killAsyncAgent()` — Force-terminates background agent
- `isLocalAgentTask()` — Type guard for local agent tasks
- `enqueueAgentNotification()` — Sends completion notification
- `queuePendingMessage()` — Queues message for poll-based delivery

### `tasks/RemoteAgentTask/`
Remote agent task management:
- `registerRemoteAgentTask()` — Registers remote CCR agent
- `checkRemoteAgentEligibility()` — Validates remote execution prerequisites
- `formatPreconditionError()` — Formats eligibility failure message
- `getRemoteTaskSessionUrl()` — Returns monitoring URL
