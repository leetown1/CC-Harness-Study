# 09 - Messages & MCP Components

## Overview

This document provides a deep analysis of the Claude Code terminal UI layer, covering four major component groups: **Message Rendering** (33 files), **Tool Result Messages** (8 files), **MCP Configuration UI** (13 files), and **Logo/Welcome Screens** (15 files). All components are Ink (React for terminals) based, compiled with the React Compiler (`react/compiler-runtime`), and rely on a primitive set of UI components: `Box`, `Text`, `Ansi`, `Markdown`, `MessageResponse`, `Dialog`, `Select`, and others.

---

## Directory 1: Core Message Components (`components/messages/` - 33 files)

This is the rendering engine for the chat interface. Each message type in the Claude Code conversation model maps to a dedicated React component.

---

### 1.1 Assistant Messages

#### `AssistantTextMessage.tsx` (270 lines)
- **Primary function:** Renders assistant text blocks with markdown formatting.
- **Props:** `param: TextBlockParam`, `addMargin`, `shouldShowDot`, `verbose`, `width`, `onOpenRateLimitOptions`.
- **Key rendering paths (all gated by text content):**
  - **Empty text** `isEmptyMessageText()`: Returns `null` (early exit).
  - **Rate limit error** `isRateLimitErrorMessage()`: Delegates to `<RateLimitMessage>`.
  - **No response requested** `NO_RESPONSE_REQUESTED`: Returns `null`.
  - **Prompt too long** `PROMPT_TOO_LONG_ERROR_MESSAGE`: Shows error with upgrade hint from `getUpgradeMessage()`.
  - **Credit balance low** `CREDIT_BALANCE_TOO_LOW_ERROR_MESSAGE`: Shows error with billing link.
  - **Invalid API key** `INVALID_API_KEY_ERROR_MESSAGE`: Renders `<InvalidApiKeyMessage>` sub-component that checks macOS keychain locked state and appends `security unlock-keychain` hint if applicable.
  - **External invalid key** `INVALID_API_KEY_ERROR_MESSAGE_EXTERNAL`: Simple error message.
  - **Org disabled** (`ORG_DISABLED_ERROR_MESSAGE_ENV_KEY` / `ORG_DISABLED_ERROR_MESSAGE_ENV_KEY_WITH_OAUTH`): Typed error display.
  - **Token revoked** `TOKEN_REVOKED_ERROR_MESSAGE`: Typed error.
  - **API timeout** `API_TIMEOUT_ERROR_MESSAGE`: Shows timeout with optional `API_TIMEOUT_MS` env var hint.
  - **Custom off-switch** `CUSTOM_OFF_SWITCH_MESSAGE`: Opus 4 demand message; directs to `/model` to switch to default Sonnet.
  - **User abort** `ERROR_MESSAGE_USER_ABORT`: Shows `<InterruptedByUser>`.
  - **API error prefix** `startsWithApiErrorPrefix()`: Truncates at 1000 chars if not verbose; shows `<CtrlOToExpand>` for truncated content.
  - **Default (text):** Renders with `<Markdown>`, optional black circle dot, selected-message background via `MessageActionsSelectedContext`.

#### `AssistantThinkingMessage.tsx` (86 lines)
- **Primary function:** Renders thinking blocks (Claude's chain-of-thought).
- **Props:** `param: ThinkingBlock | ThinkingBlockParam`, `addMargin`, `isTranscriptMode`, `verbose`, `hideInTranscript`.
- **Key paths:**
  - **Empty thinking / hideInTranscript:** Returns `null`.
  - **Collapsed mode** (not transcript, not verbose): Shows `"∴ Thinking"` with `<CtrlOToExpand>` hint.
  - **Expanded mode** (transcript or verbose): Shows `"∴ Thinking…"` label + `<Markdown dimColor>` with full thinking text indented at padding left 2.

#### `AssistantToolUseMessage.tsx` (368 lines)
- **Primary function:** Renders tool use blocks (bash, read, write, search, etc.).
- **Props:** `param: ToolUseBlockParam`, `addMargin`, `tools`, `commands`, `verbose`, `inProgressToolUseIDs`, `progressMessagesForMessage`, `shouldAnimate`, `shouldShowDot`, `inProgressToolCallCount`, `lookups`, `isTranscriptMode`.
- **Architecture:** Code-compiled with React Compiler. Uses memo caches (81 slots).
- **Key functions:**
  - `renderToolUseMessage(tool, input, {theme, verbose, commands})` (line 304): Parses input via `tool.inputSchema.safeParse()`, calls `tool.renderToolUseMessage()`.
  - `renderToolUseProgressMessage(tool, tools, lookups, toolUseID, ...)` (line 328): Filters hook progress from `progressMessagesForMessage`, calls `tool.renderToolUseProgressMessage()` if available, wraps `<HookProgressMessage>` for PreToolUse hooks.
  - `renderToolUseQueuedMessage(tool)` (line 360): Calls `tool.renderToolUseQueuedMessage()`.
- **Rendering flow:**
  1. Looks up tool definition via `findToolByName(tools, param.name)`.
  2. Parses input through `tool.inputSchema.safeParse(param.input)`.
  3. Derives `userFacingToolName`, `userFacingToolNameBackgroundColor`, `isTransparentWrapper` from tool instance.
  4. Computes: `isResolved` (in resolved IDs), `isQueued` (in progress + not resolved), `isWaitingForPermission` (pending worker request matches).
  5. **Transparent wrapper path:** Returns only progress message, no tool chrome.
  6. **Empty name path:** If `userFacingToolName === ""`, returns null.
  7. **Normal path:** Renders dot/loader, tool name (with optional bg color), tool use message in parentheses, progress section (classifier check / waiting for permission / progress message), and queued message. Uses `ToolUseLoader` for animated spinners.

#### `AssistantRedactedThinkingMessage.tsx` (31 lines)
- **Primary function:** Placeholder for redacted thinking content.
- **Renders:** `"✻ Thinking…"` in dim italic at optional margin top. No expandability.

---

### 1.2 Advisor Messages

#### `AdvisorMessage.tsx` (158 lines)
- **Primary function:** Renders advisor model output (a second model that reviews and provides feedback).
- **Props:** `block: AdvisorBlock`, `addMargin`, `resolvedToolUseIDs`, `erroredToolUseIDs`, `shouldAnimate`, `verbose`, `advisorModel`.
- **Block type dispatch:**
  - **`server_tool_use`:** Shows `"Advising"` with optional model name and tool input params. Uses `<ToolUseLoader>` for animated status indicator. Input is serialized via `jsonStringify()` if keys > 0.
  - **`advisor_tool_result_error`:** Shows `"Advisor unavailable"` with error code in error color.
  - **`advisor_result`:** Verbose mode shows full text; non-verbose shows `"✓ Advisor has reviewed the conversation and will apply the feedback"` with `<CtrlOToExpand>`.
  - **`advisor_redacted_result`:** Shows checkmark message without expand option. Wrapped in `<MessageResponse>` with right padding.

---

### 1.3 Attachment Messages (System Events)

#### `AttachmentMessage.tsx` (531 lines)
- **Primary function:** The universal attachment renderer — file reads, memory, diagnostics, hooks, skills, tasks, teammate mailboxes, MCP events, plans, and more.
- **Props:** `attachment: Attachment`, `addMargin`, `verbose`, `isTranscriptMode`.
- **Uses `useSelectedMessageBg()`** for message action selection highlighting.
- **Pre-switch handling:**
  - **`teammate_mailbox`** (gated by `isAgentSwarmsEnabled()`): Filters idle notifications + terminated messages. Renders each visible message: task assignments, plan approvals, teammate messages (with color from `toInkColor()`), and shutdown-approved filtering.
  - **`skill_discovery`** (gated by `feature('EXPERIMENTAL_SKILL_SEARCH')`): Shows skill count with optional `/skill-feedback` hint for ant users.
- **`switch` on `attachment.type`:**
  - **`directory`:** "Listed directory <path>/".
  - **`file` / `already_read_file`:** "Read <path> (<lines> lines)" or "(<size>)" with truncation sentinel. Notebook variant shows cell count.
  - **`compact_file_reference`:** "Referenced file <path>".
  - **`pdf_reference`:** "Referenced PDF <path> (<pages> pages)".
  - **`selected_lines_in_ide`:** "Selected <N> lines from <path> in <IDE>".
  - **`nested_memory`:** "Loaded <path>".
  - **`relevant_memories`:** Shows count with `<CtrlOToExpand>`; verbose/transcript mode shows each memory file path + content via `<Ansi>`.
  - **`dynamic_skill`:** "Loaded <N> skill(s) from <path>".
  - **`skill_listing`:** "N skills available" (skips initial).
  - **`agent_listing_delta`:** "N agent type(s) available" (skips initial/empty).
  - **`queued_command`:** Re-renders as `<UserTextMessage>` + optional images.
  - **`plan_file_reference`:** "Plan file referenced (<path>)".
  - **`invoked_skills`:** "Skills restored (<names>)".
  - **`diagnostics`:** Delegates to `<DiagnosticsDisplay>`.
  - **`mcp_resource`:** "Read MCP resource <name> from <server>".
  - **`command_permissions`:** Returns `null` (rendered by SkillTool).
  - **`async_hook_response`:** Shows when verbose/transcript (SessionStart only in verbose).
  - **`hook_blocking_error`:** Shows error + stderr (except Stop/SubagentStop).
  - **`hook_non_blocking_error`:** "hook name hook error" (except Stop hooks).
  - **`hook_error_during_execution`:** "hook name hook warning" (except Stop hooks).
  - **`hook_success`:** Returns `null` (logged to debug).
  - **`hook_stopped_continuation`:** Warning with hook name + message.
  - **`hook_system_message`:** "hook name says: <content>".
  - **`hook_permission_decision`:** "Allowed/Denied by <hookEvent> hook".
  - **`task_status`:** Delegates to `<TaskStatusMessage>` sub-component. Dispatches to `<TeammateTaskStatus>` for agent swarm tasks or `<GenericTaskStatus>` for regular tasks. Shows status: completed/killed/running with description.
  - **`teammate_shutdown_batch`:** "N teammate(s) shut down gracefully".
  - **Default:** TypeScript exhaustiveness check via `satisfies NullRenderingAttachmentType`.
- **Helper components** (within file):
  - `TaskStatusMessage`: Dispatches by `isAgentSwarmsEnabled()` and `taskType`.
  - `GenericTaskStatus`: Shows "(BLACK_CIRCLE) Task 'description' status" with dim color.
  - `TeammateTaskStatus`: Uses `useAppState` to get task from store, shows `@agentName` in agent color.
  - `Line`: Utility wrapper combining `<MessageResponse>` + `<Text>` with dim color, optional error color, and selected-message background.

#### `nullRenderingAttachments.ts` (70 lines)
- **Primary function:** Identifies attachment types that render as `null` (no visible output).
- **`NULL_RENDERING_TYPES` array** (34 types): `hook_success`, `hook_additional_context`, `hook_cancelled`, `command_permissions`, `agent_mention`, `budget_usd`, `critical_system_reminder`, `edited_image_file`, `edited_text_file`, `opened_file_in_ide`, `output_style`, `plan_mode`, `plan_mode_exit`, `plan_mode_reentry`, `structured_output`, `team_context`, `todo_reminder`, `context_efficiency`, `deferred_tools_delta`, `mcp_instructions_delta`, `companion_intro`, `token_usage`, `ultrathink_effort`, `max_turns_reached`, `task_reminder`, `auto_mode`, `auto_mode_exit`, `output_token_usage`, `pen_mode_enter`, `pen_mode_exit`, `verify_plan_reminder`, `current_session_memory`, `compaction_reminder`, `date_change`.
- **`isNullRenderingAttachment(msg)`:** Returns `true` if `msg.type === 'attachment'` and type is in the set.
- **Purpose:** Enables `Messages.tsx` to pre-filter these before render cap counting, preventing invisible entries from consuming the 200-message render budget.

---

### 1.4 Collapsed/Grouped Content

#### `CollapsedReadSearchContent.tsx` (484 lines)
- **Primary function:** Collapses repeated read/search/list/REPL/MCP/bash operations into a single progressive summary line.
- **Props:** `message: CollapsedReadSearchGroup`, `inProgressToolUseIDs`, `shouldAnimate`, `verbose`, `tools`, `lookups`, `isActiveGroup`.
- **Max-ref tracker:** Uses `useRef` to track maximum seen counts for read, search, list, MCP, bash — prevents jitter from debounce-induced dips during streaming.
- **`VerboseToolUse` sub-component** (line 42): Renders individual tool uses with tool name, loader/spinner, progress, and result summaries when resolved.
- **Non-verbose mode rendering:**
  - Builds natural language summary with progressive tense (active) vs. past tense (finalized).
  - **Git operations:** Commits, pushes, branches (merge/rebase), PRs — each with specific verbs and bold text.
  - **Search count:** "Searching for N patterns" / "Searched for N patterns".
  - **Read count:** "Reading N files" / "Read N files".
  - **List count:** "Listing N directories" / "Listed N directories".
  - **REPL count:** "REPL'ing N times" / "REPL'd N times".
  - **MCP count:** "Querying <server>" / "Queried <server>" with optional N times.
  - **Bash count:** "Running N bash commands" / "Ran N bash commands" (fullscreen only, minus git ops to avoid double-counting).
  - **Memory operations:** "Recalling", "Searching memories", "Writing".
  - **Team memory** (gated by `feature('TEAMMEM')`): Uses `teamMemCollapsed.CheckHasTeamMemOps` and `TeamMemCountParts` from conditionally-required module.
  - **Active hint:** Shows displayed hint (last search pattern, file path, or REPL tool) with `⎿` gutter. Uses `useMinDisplayTime(700ms)` to prevent flicker. For active REPL, reads current tool name/input from progress messages.
  - **Shell progress:** For fullscreen: after 2s elapsed, shows `(time · N lines)` suffix for in-progress bash.
  - **Hook info:** Shows PreToolUse hook count and timing when present.
  - **Spinner:** Uses `<ToolUseLoader>` when active; static dot when finalized.

#### `GroupedToolUseContent.tsx` (58 lines)
- **Primary function:** Renders grouped concurrent tool uses via `tool.renderGroupedToolUse()`.
- **Builds** a `resultsByToolUseId` map from grouped message results.
- **Builds** `toolUsesData` array with `param`, `isResolved`, `isError`, `isInProgress`, `progressMessages`, `result` for each tool use.
- Delegates all rendering to the tool's `renderGroupedToolUse` method.

---

### 1.5 Thinking & Syntax Highlighting

#### `HighlightedThinkingText.tsx` (162 lines)
- **Primary function:** Renders thinking text with optional rainbow-color highlighting for Ultrathink trigger positions.
- **Props:** `text`, `useBriefLayout?`, `timestamp?`.
- **Brief layout mode:** Chat-style "You" label with optional timestamp (`formatBriefTimestamp`), queued-message aware (color changes to "subtle").
- **Full layout mode:**
  - Reads `isUltrathinkEnabled()`; if enabled, finds trigger positions via `findThinkingTriggerPositions()`.
  - **No triggers:** Simple pointer figure + plain text.
  - **Has triggers:** Rainbow coloring per character using `getRainbowColor(i - t.start)`.
  - Uses `MessageActionsSelectedContext` for selection-aware pointer color.

---

### 1.6 Hook & Progress Messages

#### `HookProgressMessage.tsx` (116 lines)
- **Props:** `hookEvent`, `lookups`, `toolUseID`, `verbose`, `isTranscriptMode`.
- **Data sources:** `lookups.inProgressHookCounts.get(toolUseID)?.get(hookEvent)` and `lookups.resolvedHookCounts`.
- **Rendering:**
  - Returns `null` if `inProgressHookCount === 0`.
  - **PreToolUse/PostToolUse with transcript:** Shows static summary ("N <hookEvent> hook(s) ran").
  - **PreToolUse/PostToolUse non-transcript:** Returns `null` (transient, handled by other components).
  - **Other hooks:** If all resolved (`resolved === inProgress`), returns `null`. Otherwise shows "Running <hookEvent> hooks…" with spinner.
  - Wraps everything in `<MessageResponse>`.

---

### 1.7 System Messages

#### `PlanApprovalMessage.tsx` (222 lines)
- **Primary function:** Plan approval request/response display for teammate workflows.
- **Components:**
  - `PlanApprovalRequestDisplay`: Shows bordered box with planMode color, "Plan Approval Request from <name>", plan content as Markdown, plan file path. Uses dashed inner border.
  - `PlanApprovalResponseDisplay`: Two paths:
    - **Approved:** Green "✓ Plan Approved by <name>" with next-steps text. Success-colored round border.
    - **Rejected:** Red "✗ Plan Rejected by <name>" with optional feedback, "Please revise your plan" hint. Error-colored round border.
  - `tryRenderPlanApprovalMessage(content, senderName)`: Parses and dispatches to request or response display.
  - `formatTeammateMessageContent(content)`: Formats various teammate message types (plan approval, shutdown, idle notification, task assignment, teammate_terminated) into summary strings.
  - `getIdleNotificationSummary(msg)`: Builds "Agent idle · Task X completed · Last DM: <summary>".

#### `RateLimitMessage.tsx` (161 lines)
- **Primary function:** Rate limit warning with usage breakdown and upgrade messaging.
- **Components:**
  - `getUpsellMessage(params)`: Returns contextual upsell string based on subscriber tier, max20x status, team/enterprise, billing access.
  - `RateLimitMessage`: Checks `subscriptionType`, `rateLimitTier`. Uses `useClaudeAiLimits()`. Auto-opens rate limit options menu when currently rate limited. Shows upsell text when applicable. Once interactive menu opened, upsell disappears.

#### `ShutdownMessage.tsx` (132 lines)
- **Primary function:** Shutdown request/rejected display for teammate system.
- **Components:**
  - `ShutdownRequestDisplay`: Warning-colored round border, "Shutdown request from <name>", optional reason.
  - `ShutdownRejectedDisplay`: Subtle-colored round border, "Shutdown rejected by <name>", reason + continuation hint.
  - `tryRenderShutdownMessage(content)`: Dispatches to request/rejected display; approved shutdown returns null (handled inline).
  - `getShutdownMessageSummary(content)`: Summary strings for request/approved/rejected.

#### `SystemAPIErrorMessage.tsx` (141 lines)
- **Primary function:** System API error with retry countdown.
- **Components:**
  - Hidden for attempts < 4. Uses `useInterval` for 1-second countdown ticks.
  - Shows `formatAPIError(error)` truncated at 1000 chars if not verbose.
  - Shows "Retrying in N seconds… (attempt X/Y)" with optional `API_TIMEOUT_MS` hint.
  - Shows `<CtrlOToExpand>` when truncated.

#### `SystemTextMessage.tsx` (827 lines)
- **Primary function:** THE central system message renderer. Dispatches by `message.subtype`.
- **Main `SystemTextMessage` dispatch (by subtype):**
  - **`turn_duration`:** → `<TurnDurationMessage>` — Shows random verb ("Worked", etc.) + duration, budget usage with nudges, background task summary.
  - **`memory_saved`:** → `<MemorySavedMessage>` — Shows saved count with file paths (hover + click to open), team memory segment (gated by `feature('TEAMMEM')` via `teamMemSaved`).
  - **`away_summary`:** Shows reference mark + dim content.
  - **`agents_killed`:** Error-colored circle + "All background agents stopped".
  - **`thinking`:** Returns `null`.
  - **`bridge_status`:** → `<BridgeStatusMessage>` — Shows `/remote-control` active status, URL as `<Link>`, upgrade nudge.
  - **`scheduled_task_fire`:** Teardrop asterisk + content.
  - **`permission_retry`:** "Allowed <command>".
  - **`api_error`:** → `<SystemAPIErrorMessage>`.
  - **`stop_hook_summary`:** → `<StopHookSummaryMessage>`.
  - **Default:** Info-level messages hidden in non-verbose. Warning/error levels always shown via `<SystemTextMessageInner>`.
- **Sub-components:**
  - `StopHookSummaryMessage`: Conditional display (hidden if no errors, no prevented continuation, no hook label). Shows `"Ran N hook(s)"` with bold count, optional ctrl+o for verbose details, stopped-continuation reason, error list.
  - `SystemTextMessageInner`: Generic text with dot, color-coded by level, terminal-width-aware layout.
  - `TurnDurationMessage`: Uses sample from `TURN_COMPLETION_VERBS`, shows budget tracking with nudge count.
  - `MemorySavedMessage`: Shows written paths with hover/click to open via `MemoryFileRow`.
  - `MemoryFileRow`: Hover state management, click to `openPath`, file path link.
  - `BridgeStatusMessage`: Remote control banner with link and upgrade nudge.

#### `TaskAssignmentMessage.tsx` (76 lines)
- **Primary function:** Task assignment display with cyan border.
- **Components:**
  - `TaskAssignmentDisplay`: Round cyan border, "Task #<id> assigned by <name>", bold subject, optional description.
  - `tryRenderTaskAssignmentMessage(content)`: Attempts to parse and render.
  - `getTaskAssignmentSummary(content)`: Returns "[Task Assigned] #<id> - <subject>".

#### `teamMemCollapsed.tsx` (138 lines)
- **Primary function:** Team memory counters for collapsed read/search UI (ant-only).
- **Gated by `feature('TEAMMEM')`** — dead-code eliminated from external builds.
- **`checkHasTeamMemOps(message)`:** True if any team memory count > 0.
- **`TeamMemCountParts`:** Renders team memory operations (read/write/search) with progressive/past tense, comma separators, bold counts, "team" prefix.

#### `teamMemSaved.ts` (19 lines)
- **Primary function:** Formats team memory saved segment (ant-only).
- **`teamMemSavedPart(message)`:** Returns `{segment, count}` e.g. "2 team memories" if `teamCount > 0`, else `null`.

#### `CompactBoundaryMessage.tsx` (18 lines)
- Renders `"✻ Conversation compacted (ctrl+o for history)"` between compacted sections.

---

### 1.8 User Input Messages

#### `UserAgentNotificationMessage.tsx` (83 lines)
- Extracts `summary` and `status` tags from text.
- `getStatusColor(status)`: Maps 'completed'→'success', 'failed'→'error', 'killed'→'warning'.
- Renders colored black circle + summary text.

#### `UserBashInputMessage.tsx` (58 lines)
- Extracts `<bash-input>` tag.
- Renders `"! <command>"` with bash border color and bash message background.

#### `UserBashOutputMessage.tsx` (54 lines)
- Extracts `<bash-stdout>` and `<bash-stderr>` tags.
- Unwraps `<persisted-output>` inner tag from stdout.
- Delegates to `<BashToolResultMessage>`.

#### `UserChannelMessage.tsx` (137 lines)
- Parses `<channel>` XML: `source`, optional `user`, and content.
- `displayServerName(name)`: Strips `plugin:scope:` prefix to just leaf name.
- Truncates content to 60 chars via `truncateToWidth`.
- Shows channel arrow + server:user + ":" + truncated content.

#### `UserCommandMessage.tsx` (108 lines)
- Extracts `<command-message>` and `<command-args>` tags.
- Two modes:
  - **Skill format** (when `skill-format="true"`): Shows `"Skill(name)"`.
  - **Default:** Shows `"/name args"`.
- Both use pointer figure + user message background.

#### `UserImageMessage.tsx` (59 lines)
- Renders `[Image #N]` as clickable `<Link>` if stored and terminal supports hyperlinks.
- Uses `MessageResponse` when addMargin is false (connected to previous message).

#### `UserLocalCommandOutputMessage.tsx` (167 lines)
- Extracts stdout/stderr from local-command tags.
- `IndentedContent`: Two rendering paths:
  - **Cloud launch** (starts with diamond characters): Shows bold label + optional suffix + rest as nested indent.
  - **Default:** Shows `"⎿ "` gutter + markdown content.
- `CloudLaunchContent`: Parses header line for label (before `·`) and suffix, bold label with background-colored diamond.

#### `UserMemoryInputMessage.tsx` (75 lines)
- Extracts `<user-memory-input>` tag.
- Shows `# <input>` with memory background color.
- Random saving confirmation from `['Got it.', 'Good to know.', 'Noted.']` via `lodash-es/sample`.

#### `UserPlanMessage.tsx` (42 lines)
- Shows planMode-colored round border.
- Title: "Plan to implement".
- Content rendered as Markdown.

#### `UserPromptMessage.tsx` (80 lines)
- **Primary function:** User prompt display with truncation and brief mode support.
- **Truncation:** Hard cap at 10,000 chars. For long text, shows head (2,500 chars), middle line count, tail (2,500 chars).
- **Brief mode** (gated by `feature('KAIROS')` / `feature('KAIROS_BRIEF')`): Uses `useBriefLayout` which changes background, padding, and delegates to `<HighlightedThinkingText>` with brief layout.
- Selection-aware background via `MessageActionsSelectedContext`.

#### `UserResourceUpdateMessage.tsx` (121 lines)
- **Primary function:** MCP resource and polling update notifications.
- **`parseUpdates(text)`:** Parses `<mcp-resource-update>` and `<mcp-polling-update>` XML tags into `ParsedUpdate[]` using regex.
- **`formatUri(uri)`:** Shows filename for file:// URIs; truncates others at 40 chars.
- Renders each update: success-colored refresh arrow + server name + target + optional reason.

#### `UserTeammateMessage.tsx` (206 lines)
- **Primary function:** Teammate (agent swarm) message rendering.
- **`parseTeammateMessages(text)`:** Parses `<teammate-message>` XML with `teammate_id`, optional `color` and `summary`.
- **Filters out** shutdown-approved and `teammate_terminated` messages.
- **Per-message dispatch:**
  - Plan approval → `tryRenderPlanApprovalMessage`
  - Shutdown → `tryRenderShutdownMessage`
  - Task assignment → `tryRenderTaskAssignmentMessage`
  - Idle notification → hidden
  - Task completed → shows `@name` + "✓ Completed task #id (subject)"
  - Default → `<TeammateMessageContent>` with display name, ink color, truncated content.
- **`TeammateMessageContent`:** Shows `@name→` with color, optional summary, and in transcript mode: full `<Ansi>` content.

---

### 1.9 User Messages (Plain Text)

#### `UserTextMessage.tsx` (275 lines)
- **Primary function:** Serves as a universal dispatcher for user text blocks with tag-based parsing.
- **Tag-based dispatch (via `extractTag`):**
  - `<bash-input>` → `<UserBashInputMessage>`
  - `<bash-stdout>` / `<bash-stderr>` → `<UserBashOutputMessage>`
  - `<command-message>` → `<UserCommandMessage>`
  - `<agent-notification>` → `<UserAgentNotificationMessage>`
  - `<user-memory-input>` → `<UserMemoryInputMessage>`
  - `<local-command-stdout>` → `<UserLocalCommandOutputMessage>`
  - `<resource-update>` → `<UserResourceUpdateMessage>`
  - `<teammate-message>` → `<UserTeammateMessage>`
  - `<channel>` → `<UserChannelMessage>`
- Also checks for plan content via `looksLikePlanContent()` → `<UserPlanMessage>`.

---

## Directory 2: Tool Result Messages (`components/messages/UserToolResultMessage/` - 8 files)

This directory handles rendering of tool results returned from the model.

---

### 2.1 `UserToolResultMessage.tsx` (106 lines)
- **Primary function:** Main dispatcher for tool result blocks.
- **Props:** `param: ToolResultBlockParam`, `message`, `lookups`, `progressMessagesForMessage`, `style`, `tools`, `verbose`, `width`, `isTranscriptMode`.
- **Uses `useGetToolFromMessages(toolUseID, tools, lookups)`** to resolve the tool definition from the tool use ID.
- **Dispatch paths:**
  - **Canceled** (`content.startsWith(CANCEL_MESSAGE)`): → `<UserToolCanceledMessage>`
  - **Rejected** (`content.startsWith(REJECT_MESSAGE)` or `=== INTERRUPT_MESSAGE_FOR_TOOL_USE`): → `<UserToolRejectMessage>`
  - **Error** (`is_error === true`): → `<UserToolErrorMessage>`
  - **Success (default):** → `<UserToolSuccessMessage>`

---

### 2.2 `UserToolSuccessMessage.tsx` (104 lines)
- **Primary function:** Renders successful tool results.
- **Gated features:** `BASH_CLASSIFIER`, `TRANSCRIPT_CLASSIFIER`, `KAIROS`/`KAIROS_BRIEF`.
- **Classifier approval:** Captures classifier rule and YOLO reason once on mount via `React.useState` lazy initializer, then deletes from approval map to prevent memory leak.
- **Output validation:** Validates `toolUseResult` against `tool.outputSchema` before rendering.
- **Rendering:** Calls `tool.renderToolResultMessage(toolResult, progressMsgs, {style, theme, tools, verbose, ...})`.
- **Post-render:** Shows classifier auto-approval lines (checkmark + matched rule for BASH_CLASSIFIER; "Allowed by auto mode classifier" for TRANSCRIPT_CLASSIFIER). Also wraps `<HookProgressMessage>` for PostToolUse hooks.

---

### 2.3 `UserToolErrorMessage.tsx` (103 lines)
- **Primary function:** Error result rendering.
- **Dispatch by content prefix:**
  - Contains `INTERRUPT_MESSAGE_FOR_TOOL_USE` → `<InterruptedByUser>`
  - Starts with `PLAN_REJECTION_PREFIX` → `<RejectedPlanMessage>`
  - Starts with `REJECT_MESSAGE_WITH_REASON_PREFIX` → `<RejectedToolUseMessage>`
  - `isClassifierDenial()` (gated by `TRANSCRIPT_CLASSIFIER`) → "Denied by auto mode classifier · /feedback if incorrect"
  - **Default:** `tool.renderToolUseErrorMessage()` with fallback to `<FallbackToolUseErrorMessage>`

---

### 2.4 `UserToolRejectMessage.tsx` (95 lines)
- **Primary function:** Rejected tool use rendering.
- If tool is missing or has no `renderToolUseRejectedMessage`, shows `<FallbackToolUseRejectedMessage>`.
- Otherwise parses input and calls `tool.renderToolUseRejectedMessage(parsedInput, {...})`.

---

### 2.5 `UserToolCanceledMessage.tsx` (16 lines)
- Static component rendering `<MessageResponse>` with `<InterruptedByUser>`.

### 2.6 `RejectedToolUseMessage.tsx` (16 lines)
- Static component rendering "Tool use rejected" in dim text.

### 2.7 `RejectedPlanMessage.tsx` (31 lines)
- Shows "User rejected Claude's plan:" + plan content in planMode-colored border box.

### 2.8 `utils.tsx` (44 lines)
- **`useGetToolFromMessages(toolUseID, tools, lookups)`:** React Compiler-memoized hook that looks up tool use from `lookups.toolUseByToolUseID` and resolves tool via `findToolByName`. Returns `{tool, toolUse}` or `null`.

---

## Directory 3: MCP Configuration UI (`components/mcp/` - 13 files)

This directory implements the MCP server management interface accessible via `/mcp`.

---

### 3.1 `MCPSettings.tsx` (398 lines) - MAIN ENTRY POINT
- **Primary function:** State machine for MCP settings navigation.
- **State:** `MCPViewState` with types: `'list'`, `'server-menu'`, `'server-tools'`, `'server-tool-detail'`, `'agent-server-menu'`.
- **Data loading:**
  - Reads `mcp.clients` from AppState.
  - Filters out "ide" client.
  - Sets up server info list via async `prepareServers()` which maps each client to typed `ServerInfo`.
  - Resolves authentication status for remote (SSE/HTTP) servers via `ClaudeAuthProvider` + session ingress tokens.
  - Extracts agent MCP servers from `agentDefinitions.allAgents`.
- **View dispatch:**
  - `'list'` → `<MCPListPanel>` with servers, agent servers, select handlers.
  - `'server-menu'` → Routes by transport: `stdio` → `<MCPStdioServerMenu>`, otherwise → `<MCPRemoteServerMenu>`.
  - `'server-tools'` → `<MCPToolListView>` with select/back handlers.
  - `'server-tool-detail'` → `<MCPToolDetailView>` with tool details.
  - `'agent-server-menu'` → `<MCPAgentServerMenu>`.
- Edge case: If 0 servers and 0 agent servers, shows "No MCP servers configured" message.

---

### 3.2 `MCPListPanel.tsx` (504 lines)
- **Primary function:** Server list with status icons, navigation, and scope grouping.
- **Grouping:** `groupServersByScope()` partitions servers by `scope` (`project`, `local`, `user`, `enterprise`, `dynamic`).
- **Scope order:** `['project', 'local', 'user', 'enterprise']` + dynamic at end.
- **Scope headings:** Each scope has a label (e.g., "Project MCPs") and optional file path via `describeMcpConfigFilePath()`.
- **Special sections:**
  - `claudeAiServers` (proxy type): Listed under "claude.ai" section.
  - `agentServers`: Listed under "Agent MCPs" section, grouped by source agent name (`@agentName`).
- **Selectable items:** Built as flat array of `SelectableItem` (server or agent-server).
- **Server item rendering** (`renderServerItem`): Each server shows:
  - Pointer arrow for selected; spaces otherwise.
  - Server name (colored by selection).
  - Status icon + text: `disabled` (radiooff), `connected` (tick/green), `pending` (radiooff + "connecting…" or reconnect attempt), `needs-auth` (triangleUpOutline/yellow), `failed` (cross/red).
- **Agent server item rendering:** Shows "may need auth" or "agent-only" status.
- **Keyboard navigation:** Up/Down to navigate, Enter to select, Esc to cancel. Uses `useKeybindings` with `confirm:previous`, `confirm:next`, `confirm:yes`, `confirm:no`.
- **Footer:** Shows keyboard shortcut hints + MCP docs link. If any failed clients, shows debug hint.

---

### 3.3 `MCPRemoteServerMenu.tsx` (649 lines) - LARGEST MCP COMPONENT
- **Primary function:** Configuration menu for remote (SSE, HTTP, claude.ai proxy) MCP servers.
- **Props:** `server: SSEServerInfo | HTTPServerInfo | ClaudeAIServerInfo`, `serverToolsCount`, `onViewTools`, `onCancel`, `onComplete`, `borderless`.
- **Server info display:**
  - Status: disabled/connected/pending/needs-auth/failed with color-coded icons.
  - Auth status (non-proxy): authenticated/not authenticated.
  - URL, Config location.
  - Capabilities (tools/prompts/resources via `<CapabilitiesSection>`).
  - Tools count.
- **Authentication flows:**
  - **Standard OAuth:** `handleAuthenticate()` — revokes existing tokens (preserving step-up auth), calls `performMCPOAuthFlow()` with abort controller, shows authorization URL with copy-to-clipboard support (key 'c'), manual callback URL input for connection errors.
  - **Claude.ai proxy auth:** `handleClaudeAIAuth()` — builds auth URL with org UUID and server ID, opens browser, shows "Press Enter after authenticating" prompt.
  - **Claude.ai clear auth:** `handleClaudeAIClearAuth()` — opens browser to connectors page, clears cache and app state on completion.
- **Auth UI states:**
  - `isAuthenticating`: Spinner + "A browser window will open" message. XAA (silent exchange) detected via config check.
  - `isClaudeAIAuthenticating`: Spinner + browser URL copy + Enter-to-continue prompt.
  - `isClaudeAIClearingAuth`: Two sub-states — initial (Enter to open browser) and browser-opened (Enter when done).
  - `isReconnecting`: Spinner + "Connecting to server…" message.
- **Menu options** (context-sensitive):
  - Disabled server → "Enable".
  - Connected + has tools → "View tools".
  - Claude.ai proxy: connected → "Clear authentication"; not disabled → "Authenticate".
  - Non-proxy: authenticated → "Re-authenticate" + "Clear authentication"; not authenticated → "Authenticate".
  - Not disabled, not needs-auth → "Reconnect".
  - Not disabled → "Disable".
- **Reconnect:** Uses `useMcpReconnect()`, logs events for claude.ai proxy.

---

### 3.4 `MCPStdioServerMenu.tsx` (177 lines)
- **Primary function:** Simpler menu for stdio MCP servers (no OAuth).
- **Information displayed:** Status, Command, Args, Config location, Capabilities, Tools count.
- **Menu options:** "View tools" (if has tools), "Reconnect" (if not disabled), "Disable/Enable".
- **Reconnect state:** Shows spinner + "Restarting MCP server process" text.
- Follows same footer pattern with keyboard shortcut hints.

---

### 3.5 `MCPToolListView.tsx` (141 lines)
- **Primary function:** List of tools for a server, with search/selection.
- **Data:** Filters `mcp.tools` by server name via `filterToolsByServer()`.
- **Tool option rendering:** Each tool shows:
  - Display name via `extractMcpToolDisplayName()`
  - Annotations: read-only (success color), destructive (error color), open-world (dim color)
  - Description color-coded: error for destructive, success for read-only.
- **Empty state:** "No tools available".
- **Selection:** `Select` component with keyboard navigation and cancel.

---

### 3.6 `MCPToolDetailView.tsx` (212 lines)
- **Primary function:** Detailed view of a single MCP tool.
- **Display:**
  - Display name with annotations: [read-only], [destructive], [open-world].
  - Tool name (full MCP-qualified name).
  - Full name.
  - Description (loaded asynchronously via `tool.description()` with a mock `toolPermissionContext`).
  - Parameters: Lists each parameter with required indicator, type, and description from `tool.inputJSONSchema.properties`.
- **Dialog:** Uses `<Dialog>` with server name subtitle, customizable input guide for exit/cancel.

---

### 3.7 `MCPReconnect.tsx` (167 lines)
- **Primary function:** Standalone reconnection dialog for MCP servers.
- **Props:** `serverName`, `onComplete`.
- **Auto-starts reconnection** on mount via `useEffect`.
- **States:**
  - `isReconnecting`: Spinner + "Reconnecting to <server>" + "Establishing connection to MCP server".
  - Error: Cross icon + error message + "Error: <detail>".
- Handles result types: connected, needs-auth, failed, disabled.

---

### 3.8 `MCPAgentServerMenu.tsx` (183 lines)
- **Primary function:** Menu for agent-specific MCP servers (defined in agent frontmatter).
- **Shows:** Type, URL (if HTTP/SSE), Command (if stdio), Used by (source agents), Status (always "not connected (agent-only)"), Auth status with warning icon.
- **Auth flow:** Uses `performMCPOAuthFlow()` with temporary config built from agent server's transport and URL. Shows spinner + browser instructions.
- **Menu options:** Authenticate/Re-authenticate + Back.
- **Note:** These servers only connect when the agent runs; this menu allows pre-authentication.

---

### 3.9 `ElicitationDialog.tsx` (1169 lines) - LARGEST COMPONENT IN THIS DIRECTORY
- **Primary function:** Handles MCP elicitation (form/URL) requests from servers.
- **Two modes** dispatched by `ElicitationDialog`:
  - **`mode === "url"`** → `<ElicitationURLDialog>`
  - **`mode === "form"` (default)** → `<ElicitationFormDialog>`
- **`ElicitationFormDialog`:**
  - **Form field types supported:**
    - **Text fields** (string/number/integer): Inline `<TextInput>` with real-time validation.
    - **Date/datetime fields:** ISO value parsing with `formatDateDisplay()`, debounced async NL parsing via `validateElicitationInputAsync()` (2s timeout). Uses `resolveFieldAsync()` which manages AbortController per field for cancellation.
    - **Boolean fields:** Space to toggle, y/n typeahead with `runTypeahead()`.
    - **Single-select enum fields:** Expandable accordion (`→` to expand, `Space` to select, `Enter` to select+advance). Supports typeahead.
    - **Multi-select enum fields:** Expandable accordion with checkboxes (`Space` to toggle, `Enter` to check+advance). Validates minItems/maxItems. Supports typeahead.
  - **Navigation:** Up/Down to cycle through fields + Accept/Decline buttons.
  - **Validation:** Required fields checked on Accept. Each field valid on change via `validateElicitationInput()`. Errors shown below each field.
  - **Scroll windowing:** Calculates visible field range based on terminal rows (14 lines overhead, 3 lines per field). Shows "N more above/below" indicators.
  - **Checkbox column** (left gutter):
    - `isResolving` → `<ResolvingSpinner>` (own 80ms animation timer, isolated from parent re-renders).
    - Has error → warning icon.
    - Has value → green checkmark.
    - Required + unset → red asterisk.
    - Otherwise → space.
  - **Footer buttons:** "Accept" (success color) and "Decline" (error color) with pointer indicators.
  - **Signal handling:** Respects `signal.aborted` from MCP server; auto-cancels on abort.
  - **Overlay registration:** Uses `useRegisterOverlay('elicitation')` and `useNotifyAfterTimeout()` for desktop notification.
- **`ElicitationURLDialog`:**
  - **Prompt phase:** Shows URL with domain highlighted, "Accept" to open browser + enter waiting, "Decline" to cancel.
  - **Waiting phase:** Shows "Reopen URL", action (continue without waiting), optional Cancel button. Auto-dismisses when server sends completion notification.
  - **Cancel support:** `showCancel` from `waitingState` enables a third button.

---

### 3.10 Supporting MCP Files

#### `McpParsingWarnings.tsx` (213 lines)
- **Primary function:** Displays MCP config parsing errors/warnings at the top of the MCP list.
- **Data:** `getMcpConfigsByScope()` for user, project, local, enterprise scopes.
- **`McpConfigErrorSection`:** Per-scope section showing:
  - Header: `[Failed to parse]` (error color) or `[Contains warnings]` (warning color) + scope label.
  - Location: file path.
  - Errors: `└ [Error] [serverName] path: message`.
  - Warnings: `└ [Warning] [serverName] path: message`.
- **`filterErrors()`:** Separates fatal errors from warnings by `mcpErrorMetadata.severity`.
- Returns null if no parsing errors/warnings.

#### `CapabilitiesSection.tsx` (61 lines)
- **Primary function:** Displays server capabilities (tools, resources, prompts).
- Collects non-zero capabilities into a `<Byline>` component.

#### `index.ts` (9 lines)
- Re-exports all public MCP components: `MCPAgentServerMenu`, `MCPListPanel`, `MCPReconnect`, `MCPRemoteServerMenu`, `MCPSettings`, `MCPStdioServerMenu`, `MCPToolDetailView`, `MCPToolListView`. Also exports types.

#### `utils/reconnectHelpers.tsx` (49 lines)
- **`handleReconnectResult(result, serverName)`:** Maps client type to user-facing messages (connected/success, needs-auth/requires auth, failed/error).
- **`handleReconnectError(error, serverName)`:** Formats error into user-facing string.

---

## Directory 4: Logo & Welcome Components (`components/LogoV2/` - 15 files)

This directory implements the welcome screen, condensed logo, animated Clawd mascot, notice banners, and promotional feeds.

---

### 4.1 `LogoV2.tsx` (543 lines) - MAIN LOGO COMPONENT
- **Primary function:** The welcome/startup screen with layout modes (full, compact, condensed).
- **Data sources:**
  - `getLogoDisplayData()`: version, cwd, billingType, agentName.
  - `getRecentActivitySync()`: Recent conversation logs.
  - `getRecentReleaseNotesSync(3)`: Latest 3 release notes.
  - `getGlobalConfig()`: User config (display name, org, theme, etc.).
  - `getInitialSettings().companyAnnouncements`: Org announcements.
  - `checkForReleaseNotesSync()`: Whether new release notes available.
  - `shouldShowProjectOnboarding()`: Project tips for new users.
  - `useShowGuestPassesUpsell()`, `useShowOverageCreditUpsell()`: Upsell banners.
  - `SandboxManager.isSandboxingEnabled()`: Sandbox warning.
- **Three layout modes:**
  - **Condensed** (no release notes, no onboarding, not forced full): Shows `<CondensedLogo>` + notices (VoiceMode, Opus1mMerge, Channels, Debug, EmergencyTip, tmux) + org announcement.
  - **Compact** (narrow terminal): Border with `"Claude Code" v<version>`, welcome message (with username), `<Clawd>` ASCII art, model display name, billing type, agent name + cwd. Wrapped in `<OffscreenFreeze>`.
  - **Full** (default): Two-panel layout with vertical/horizontal split (layout mode by terminal width). Left panel: welcome message, Clawd, model + billing, cwd. Right panel: feed column with rotating content (project onboarding / guest passes / overage credit / recent activity + what's new).
- **Feed selection priority:** `showOnboarding` > `showGuestPassesUpsell` > `showOverageCreditUpsell` > `[recentActivity, whatsNew]`.
- **Notices** (rendered after the main box): `VoiceModeNotice`, `Opus1mMergeNotice`, `ChannelsNotice` (gated by `feature('KAIROS')||feature('KAIROS_CHANNELS')`), Debug mode, EmergencyTip, tmux session info, org announcements, sandbox warning, ant-only log paths.
- **On first render:** Updates `lastReleaseNotesSeen` to current version. Increments project onboarding/project upsell seen counts.

---

### 4.2 `WelcomeV2.tsx` (433 lines)
- **Primary function:** Welcome Clawd ASCII art with "Welcome to Claude Code" header.
- **Theme-aware rendering:**
  - **Apple Terminal:** Uses `AppleTerminalClawd` with background-color fill trick (no `clawd_body`/`clawd_background` colors — sweeps them with bg fill patterns). Separate light/dark paths.
  - **Light themes** (light, light-daltonized, light-ansi): ASCII art with `clawd_body`, `clawd_background` colors.
  - **Dark themes** (default): Similar ASCII with dark-mode optimized characters.
  - All at fixed width: 58 columns.
- **Sub-component: `AppleTerminalWelcomeV2`**: Renders the same ASCII art but optimized for Apple Terminal's rendering quirks, using `bgClawdBody` fill trick.

---

### 4.3 `Clawd.tsx` (240 lines) - STATIC CLAWD ASCII ART
- **Primary function:** Clawd mascot rendering with 4 poses.
- **Poses:**
  - `'default'`: Normal, eyes centered (`▛███▜`).
  - `'look-left'`: Both pupils shifted left (`▟███▟`).
  - `'look-right'`: Both pupils shifted right (`▙███▙`).
  - `'arms-up'`: Arms raised (`▗▟`/`▙▖` on row 1; body simplified on row 2).
- **Segments system:** Each pose defined as 5 segments (`r1L`, `r1E`, `r1R`, `r2L`, `r2R`) for row decomposition. Allows varying only eyes/arms while keeping body spans stable.
- **Total height:** 3 rows, 9 columns wide.
- **Apple Terminal variant:** Uses bg-fill trick instead of `clawd_body`/`clawd_background` colors. Only eye poses apply (arm poses fall back to default). `APPLE_EYES` record maps poses to inner eye patterns.

---

### 4.4 `AnimatedClawd.tsx` (124 lines)
- **Primary function:** Click-triggered Clawd animations in fullscreen mode.
- **`useClawdAnimation()` hook:**
  - Respects `prefersReducedMotion` setting (falls back to static).
  - **Animations:** Randomly picks from `JUMP_WAVE` (crouch→spring with arms up ×2) or `LOOK_AROUND` (look right→left→center).
  - Uses `setTimeout` at 60ms per frame for animation stepping.
  - Frame index → -1 when idle (no animation playing).
  - `onClick`: Triggers a new animation if idle and motion not reduced.
- **Container:** Fixed height 3, flex column, onClick handler.
- **Bounce offset:** During crouch frames, `marginTop=1` causes Clawd's feet to clip below the container (reads as "ducking").

---

### 4.5 `AnimatedAsterisk.tsx` (50 lines)
- **Primary function:** Animated asterisk with rainbow hue sweep for notice banners.
- **Animation:** 1500ms per sweep, 2 sweeps total. Uses `useAnimationFrame(50ms)`.
- **Color:** Cycles through hues mapped to RGB via `hueToRgb()` / `toRGBColor()`.
- **Settled state:** Settles to grey RGB(153, 153, 153). Uses `setTimeout` for completion.
- Respects `prefersReducedMotion`.

---

### 4.6 `CondensedLogo.tsx` (161 lines)
- **Primary function:** Compact welcome logo with Clawd + text + upsells.
- **Layout:** Horizontal row: `<AnimatedClawd>` (fullscreen) or `<Clawd>` (non-fullscreen) + vertical column of text.
- **Text column:** "Claude Code v<version>" → model + billing (split to two lines if needed) → `@agentName · cwd` or just cwd.
- **Upsells:** Guest passes upsell (`<GuestPassesUpsell>`) or overage credit upsell (`<OverageCreditUpsell twoLine>`) when applicable.
- **Wraps in** `<OffscreenFreeze>` for performance.

---

### 4.7 `Feed.tsx` (112 lines)
- **Primary function:** Feed column item rendering.
- **`FeedConfig` type:** `{title, lines: FeedLine[], footer?, emptyMessage?, customContent?}`.
- **`calculateFeedWidth(config)`:** Computes optimal width from title, lines (including timestamps), footer, custom content.
- **`Feed` component:**
  - Title in claude color + bold.
  - **Custom content:** Shows content directly.
  - **Empty:** Shows empty message.
  - **Lines:** Shows each line with optional timestamp (right-aligned, padded) + text (truncated to fit).
  - **Footer:** Dim italic, truncated.
- All text widths are computed using `stringWidth` for correct CJK/emoji handling.

---

### 4.8 `FeedColumn.tsx` (59 lines)
- **Primary function:** Multiple feeds stacked vertically with dividers.
- Computes `actualWidth` as `min(maxOfAllFeeds, maxWidth)`.
- Maps feeds → `<Feed>` + `<Divider color="claude">` between items.
- Wraps in `<Box flexDirection="column">`.

---

### 4.9 `feedConfigs.tsx` (92 lines)
- **Primary function:** Feed item configurations for the welcome screen.
- **`createRecentActivityFeed(activities)`:**
  - Maps each log entry to `{text: description, timestamp: formatRelativeTimeAgo(time)}`.
  - Title: "Recent activity".
  - Footer: "/resume for more".
  - Empty: "No recent activity".
- **`createWhatsNewFeed(releaseNotes)`:**
  - For ant builds: Parses `"N <unit>s ago <message>"` format into timestamp + text.
  - For external: Shows raw notes.
  - Title: "What's new [ANT-ONLY: Latest CC commits]" or "What's new".
  - Footer: "/release-notes for more".
- **`createProjectOnboardingFeed(steps)`:**
  - Filters enabled steps, sorts by completion (incomplete first).
  - Shows checkmarks (`✓`) for completed steps.
  - Home directory warning appended if applicable.
  - Title: "Tips for getting started".
- **`createGuestPassesFeed()`:**
  - Custom content with `[✻] [✻] [✻]` in claude color.
  - Shows referral reward amount if available.
  - Footer: "/passes".

---

### 4.10 Notice Components

#### `ChannelsNotice.tsx` (262 lines)
- **Primary function:** Channel (Slack/Discord/etc.) integration status notice.
- **Gated by `feature('KAIROS')||feature('KAIROS_CHANNELS')`**; tree-shaken via `require()` pattern.
- **States:**
  - **No channels:** Returns null.
  - **Disabled:** "Channels not currently available".
  - **No auth:** "Channels require claude.ai authentication · run /login".
  - **Policy blocked:** "Channels blocked by org policy · Inbound messages will be silently dropped" + admin instructions.
  - **Normal:** "Listening for channel messages from: <list>" + experimental warning.
- **`findUnmatched(entries, allowlist)`:** Validates each channel entry against configured servers (for server-kind) or installed plugins + allowlist (for plugin-kind). Reports why entries are unmatched.
- **`formatEntry(c)`:** Formats channel entry as `"plugin:name@marketplace"` or `"server:name"`.

#### `EmergencyTip.tsx` (58 lines)
- **Primary function:** Emergency/operational tip from dynamic config (GrowthBook).
- Loads tip from `getDynamicConfig_CACHED_MAY_BE_STALE('tengu-top-of-feed-tip')`.
- Shows only if new/different from `lastShownEmergencyTip` in global config.
- Auto-saves shown tip to config to prevent repeat display.
- Supports colors: dim (default), warning, error.

#### `GuestPassesUpsell.tsx` (70 lines)
- **Primary function:** Guest passes promotional upsell.
- **Eligibility:** Checks cached passes eligibility, resets impression count if passes refreshed.
- **Impression cap:** 3 impressions before dismissed.
- **Dismissed if** user has visited passes page.
- **Condensed display:** `[✻] [✻] [✻] · Share Claude Code and earn <amount> · /passes`.

#### `OverageCreditUpsell.tsx` (166 lines)
- **Primary function:** Overage credit promotional upsell.
- **Eligibility:** Backend-determined via `getCachedOverageCreditGrant()`. Checks available + not granted + formatable amount.
- **Impression cap:** 3 impressions. Dismissed if `hasVisitedExtraUsage`.
- **`maybeRefreshOverageCreditCache()`:** Background cache refresh if empty.
- **Two rendering modes:**
  - `twoLine`: Title (claude color) + subtitle (dim). For condensed logo.
  - Single line: `<amount> in extra usage for third-party apps · /extra-usage` with claude-highlighted amount portion.
- **`createOverageCreditFeed()`:** Returns `FeedConfig` for welcome screen feed.

#### `Opus1mMergeNotice.tsx` (55 lines)
- **Primary function:** "Opus now defaults to 1M context" notice.
- Shows animated asterisk (up arrow) + "Opus now defaults to 1M context · 5x more room, same pricing".
- Max show count: 6. Auto-saves seen count to global config.

#### `VoiceModeNotice.tsx` (68 lines)
- **Primary function:** Voice mode availability notice.
- **Gated by `feature('VOICE_MODE')`.** Returns null for non-enabled builds.
- **Inner component** eligibility: `isVoiceModeEnabled() && !voiceEnabled && seenCount < 3 && !shouldShowOpus1mMergeNotice()`.
- Shows animated asterisk + "Voice mode is now available · /voice to enable".

---

## Cross-Cutting Patterns

### React Compiler Usage
All components use `react/compiler-runtime` (`import { c as _c }`). The compiler generates memoization caches with numbered slots (`$[0]`, `$[1]`, etc.), using `Symbol.for("react.memo_cache_sentinel")` as cache-miss sentinel. `Symbol.for("react.early_return_sentinel")` is used for early returns within memoized blocks.

### Feature Gating
Two mechanisms:
1. `feature()` from `bun:bundle`: Compile-time gating. e.g., `feature('KAIROS')`, `feature('TEAMMEM')`, `feature('VOICE_MODE')`.
2. Conditional `require()`: Runtime tree-shaking via module-level require guards. Used for `ChannelsNotice`, `teamMemCollapsed`, `teamMemSaved` — entire files eliminated when both flags are false.

### Ink UI Primitives
All UI is built on Ink (React for CLI): `Box`, `Text`, `Ansi`, `Link`, `useTheme`, `useInput`, `useTerminalSize`, `color()`, `stringWidth()`. Custom components include `Markdown`, `MessageResponse`, `Dialog`, `Select`, `Spinner`, `ToolUseLoader`, `CtrlOToExpand`, `ConfigurableShortcutHint`, `KeyboardShortcutHint`, `Byline`, `Divider`, `FilePathLink`, `OffscreenFreeze`, `SentryErrorBoundary`.

### State Management
- `useAppState(selector)` / `useAppStateMaybeOutsideOfProvider(selector)` for Zustand store access.
- `useAppStateStore()` for direct store access.
- `getGlobalConfig()` / `saveGlobalConfig()` for persistent config.
- `getInitialSettings()` for one-time setting reads.
- `React.useState` for component-local state (animations, form values, UI state).

### Selection & Message Actions
`useSelectedMessageBg()` and `MessageActionsSelectedContext` provide selection-aware coloring for messages.

### Progress & Animation
- `useAnimationFrame(interval)` / `useMinDisplayTime(value, min)` for timed transitions.
- `useRef` for tracking max counts (jitter prevention), animation frame indices, and abort controllers.
- `setTimeout` / `setInterval` for animation stepping and debounce.

### Tool System Integration
Tools are resolved via `findToolByName(tools, name)` and provide render callbacks: `renderToolUseMessage`, `renderToolUseProgressMessage`, `renderToolUseQueuedMessage`, `renderToolUseRejectedMessage`, `renderToolResultMessage`, `renderToolUseErrorMessage`, `renderGroupedToolUse`. The `Tool` type includes `userFacingName`, `userFacingNameBackgroundColor`, `isTransparentWrapper`, `inputSchema`, `outputSchema`, `isReadOnly`, `isDestructive`, `isOpenWorld`, and `inputJSONSchema`.

### Message Lookups
`buildMessageLookups` creates a comprehensive lookup structure: `resolvedToolUseIDs`, `erroredToolUseIDs`, `toolUseByToolUseID`, `toolResultByToolUseID`, `progressMessagesByToolUseID`, `inProgressHookCounts`, `resolvedHookCounts`. This is threaded through most message components.
