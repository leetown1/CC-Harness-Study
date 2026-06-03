# Components Supplement 2 — UI Layer Analysis

## Directory 1: `components/tasks/` (12 files)

### 1. AsyncAgentDetailDialog.tsx (229 lines)

**Exports**: `AsyncAgentDetailDialog` (React component, React Compiler-processed)

**Types**: `Props` — `DeepImmutable<LocalAgentTaskState>` agent, `() => void` onDone/onKillAgent/onBack callbacks.

**Functions/Components**:
- `AsyncAgentDetailDialog(props)` — Dialog showing detailed state of an async (non-teammate) local agent task. Displays title from agent `selectedAgent.agentType` and `description`, subtitle with status icon/color + elapsed time + token/tool counts. Renders running progress as `recentActivities` list via `renderToolActivity`, prompt text (with `plan` tag extraction for `UserPlanMessage`), and error display on failure. Key bindings: Space/Enter/Esc = close, Left = back, `x` = kill running agent.

### 2. BackgroundTask.tsx (345 lines)

**Exports**: `BackgroundTask` (React component)

**Types**: `Props` — `DeepImmutable<BackgroundTaskState>` task, optional `number` maxActivityWidth.

**Functions/Components**:
- `BackgroundTask(props)` — Single-line status renderer for a background task in the footer. Switches on `task.type` to render per-kind:
  - `local_bash`: Truncated command/description + `ShellProgress`
  - `remote_agent`: Diamond icon (filled/completed vs open/running) + truncated title + `RemoteSessionProgress`
  - `local_agent`: Truncated description + `TaskStatusText` with completion state
  - `in_process_teammate`: Agent color pill (@name) + truncated `describeTeammateActivity` output
  - `local_workflow`: Truncated workflow name/summary/description + agent count + `TaskStatusText`
  - `monitor_mcp`: Truncated description + `TaskStatusText`
  - `dream`: Description + phase count (files/files reviewed) + `TaskStatusText`

### 3. BackgroundTasksDialog.tsx (652 lines)

**Exports**: `BackgroundTasksDialog` (React component)

**Types**: `ViewState` — union of `{ mode: 'list' }` and `{ mode: 'detail'; itemId: string }`. `ListItem` — discriminated union on all 8 task types including `'leader'`. `Props` — onDone, toolUseContext, optional initialDetailTaskId.

**Functions/Components**:
- `getSelectableBackgroundTasks(tasks, foregroundedTaskId)` — Filters tasks record to `isBackgroundTask`, excludes foregrounded local_agent tasks.
- `toListItem(task)` — Converts a `BackgroundTaskState` into a `ListItem` for display; extracts label from command/description/title/agentName/summary per type.
- `Item({ item, isSelected })` — Renders a single task list row with pointer (if selected), truncation, and the `BackgroundTask` component.
- `TeammateTaskGroups({ teammateTasks, currentSelectionId })` — Groups teammates by `teamName`, renders leader + team members in sections.
- `BackgroundTasksDialog(props)` — Modal overlay dialog showing categorized lists of all background tasks. Supports: navigation with up/down/Enter, `x` to kill running tasks, `f` to foreground teammates, `left` to close. Detail views delegate to per-type dialogs (`ShellDetailDialog`, `AsyncAgentDetailDialog`, `RemoteSessionDetailDialog`, `InProcessTeammateDetailDialog`, `WorkflowDetailDialog` [feature-gated], `MonitorMcpDetailDialog` [feature-gated], `DreamDetailDialog`). Auto-enters detail if only one task or `initialDetailTaskId` provided. Workflow and MonitorMCP features are DCE-gated via `bun:bundle` feature flags.

### 4. BackgroundTaskStatus.tsx (429 lines)

**Exports**: `BackgroundTaskStatus` (React component)

**Types**: `Props` — tasksSelected, optional isViewingTeammate/teammateFooterIndex/isLeaderIdle/onOpenDialog. `AgentPillProps` — name, optional color, isSelected/isViewed/isIdle/onClick.

**Functions/Components**:
- `getAgentThemeColor(colorName)` — Maps agent color name to Ink theme color key via `AGENT_COLOR_TO_THEME_COLOR`.
- `AgentPill({ name, color, isSelected, isViewed, isIdle, onClick })` — Colored pill showing `@name` with hover/click support; uses theme background/inverse colors for selected state.
- `SummaryPill({ selected, onClick, children })` — Simple inverse/normal pill for the summary count.
- `BackgroundTaskStatus(props)` — Footer status bar component. When all tasks are in-process teammates, renders a horizontal scrollable list of agent pills with arrow indicators. Otherwise renders a summary pill with task count via `getPillLabel`, plus a view-hint text when `pillNeedsCta`. Uses `shouldHideTasksFooter` to suppress when spinner tree is active and all tasks are teammates.

### 5. DreamDetailDialog.tsx (251 lines)

**Exports**: `DreamDetailDialog` (React component)

**Types**: `Props` — `DeepImmutable<DreamTaskState>` task, `() => void` onDone/onBack/onKill.

**Constants**: `VISIBLE_TURNS = 6` — only the 6 most recent turns are rendered.

**Functions/Components**:
- `DreamDetailDialog(props)` — Dialog showing memory consolidation (dream) task details. Title: "Memory consolidation". Subtitle: elapsed time + "reviewing N sessions" + "M files touched". Body: status line (running/completed/failed), then last 6 visual turns with text + tool use counts. Earlier turns collapsed to "(N earlier turns)". Key bindings: Space/Enter/Esc = close, Left = back, `x` = kill running.

### 6. InProcessTeammateDetailDialog.tsx (266 lines)

**Exports**: `InProcessTeammateDetailDialog` (React component)

**Types**: `Props` — `DeepImmutable<InProcessTeammateTaskState>` teammate, `() => void` onDone/onKill/onBack/onForeground.

**Functions/Components**:
- `InProcessTeammateDetailDialog(props)` — Dialog for viewing an in-process teammate agent. Title: `@agentName` in agent color + activity description. Subtitle: status + elapsed time + token/tool counts. Body: progress list of recent activities via `renderToolActivity`, prompt text, error display. Key bindings: Space/Enter/Esc = close, Left = back, `x` = kill, `f` = foreground (switch to teammate view).

### 7. RemoteSessionDetailDialog.tsx (904 lines)

**Exports**: `RemoteSessionDetailDialog`, `formatToolUseSummary` (React component + utility)

**Types**: `Props` — `DeepImmutable<RemoteAgentTaskState>` session, `ToolUseContext`, onDone/onBack/onKill. `MenuAction` — 'open' | 'stop' | 'back' | 'dismiss'.

**Constants**: `PHASE_LABEL` — maps `needs_input`/'plan_ready' to 'input required'/'ready'. `AGENT_VERB` — maps to 'waiting'/'done'. `STAGES` — ['finding', 'verifying', 'synthesizing'] with `STAGE_LABELS` mapping to 'Find'/'Verify'/'Dedupe'.

**Functions/Components**:
- `formatToolUseSummary(name, input)` — One-line tool call summary. Special-cases `ExitPlanModeV2Tool` as "Review the plan in Claude Code on the web", `AskUserQuestionTool` as "Answer in browser: {question text}". Otherwise extracts first string arg from input.
- `StagePipeline({ stage, completed, hasProgress })` — Renders Setup → Find → Verify → Dedupe pipeline with current stage highlighted, completed stages dimmed, and green checkmark on completion.
- `reviewCountsLine(session)` — Builds count string for review progress (bugs found/verified/refuted).
- `UltraplanSessionDetail({ session, onDone, onBack, onKill })` — Sub-dialog for ultraplan remote sessions. Counts agent spawns and tool calls from session log. Shows agent count + tool call count + last tool call summary + session URL link. Provides Select menu: "Review in Claude Code on the web", "Stop ultraplan" (with confirmation), "Back".
- `ReviewSessionDetail({ session, onDone, onBack, onKill })` — Sub-dialog for ultrareview sessions. Shows `StagePipeline`, review counts, session URL link. Provides Select menu: "Open in Claude Code on the web", "Stop ultrareview" (with confirmation), "Back"/"Dismiss".
- `RemoteSessionDetailDialog(props)` — Main dialog for remote agent sessions. If ultrapan, delegates to `UltraplanSessionDetail`. If review, delegates to `ReviewSessionDetail`. Otherwise shows generic details: status, runtime, title, progress (via `RemoteSessionProgress`), session URL link, recent messages (last 3 normalized, non-progress messages via `Message` component), and teleport functionality (key `t` to teleport to session via `teleportResumeCodeSession`).

### 8. RemoteSessionProgress.tsx (243 lines)

**Exports**: `RemoteSessionProgress`, `formatReviewStageCounts` (React component + utility)

**Types**: `ReviewStage` — NonNullable of reviewProgress stage.

**Constants**: `TICK_MS = 80` — animation tick interval.

**Functions/Components**:
- `formatReviewStageCounts(stage, found, verified, refuted)` — Canonical counts line for running reviews. Shared between pill and detail dialog. Handles finding/verifying/synthesizing stages with appropriate labels.
- `RainbowText({ text, phase })` — Renders text with per-character rainbow gradient colors, phase-offset for animation sweep effect.
- `useSmoothCount(target, time, snap)` — Animated count that ticks toward target 1 per frame. Snaps when reduced motion or frozen clock.
- `ReviewRainbowLine({ session })` — Ultrareview progress line with animated rainbow "ultrareview" text + smooth-count bug stats. Shows "setting up" before progress data, completed state with filled diamond, failed state with error.
- `RemoteSessionProgress({ session })` — Main progress component. Routes to `ReviewRainbowLine` for review sessions, or shows "done"/"error" for terminal states, or todoList `completed/total` count for running generic sessions.

### 9. renderToolActivity.tsx (33 lines)

**Exports**: `renderToolActivity` (pure function)

**Functions/Components**:
- `renderToolActivity(activity, tools, theme)` — Renders a `ToolActivity` into a React node. Finds the tool by name, safe-parses its input, gets the `userFacingName`, and renders `tool.renderToolUseMessage(parsedInput)`. Falls back to plain tool name if parsing fails or no user-facing name.

### 10. ShellDetailDialog.tsx (404 lines)

**Exports**: `ShellDetailDialog` (React component)

**Types**: `Props` — `DeepImmutable<LocalShellTaskState>` shell, onDone/onKillShell/onBack. `TaskOutputResult` — content string + bytesTotal. `ShellOutputContentProps` — outputPromise + columns.

**Constants**: `SHELL_DETAIL_TAIL_BYTES = 8192`.

**Functions/Components**:
- `getTaskOutput(shell)` — Async: reads tail of task output file via `getTaskOutputPath(shell.id)` + `tailFile(path, 8192)`. Returns content + bytesTotal.
- `ShellOutputContent({ outputPromise, columns })` — Uses React `use()` to unwrap promise. Renders last ~10 lines of output in a bordered box (12 rows height, max column width - 6), with truncation and "Showing N lines of X bytes" footer.
- `ShellDetailDialog(props)` — Dialog showing shell/monitor details. Title: "Shell details" or "Monitor details" based on `shell.kind`. Shows status (with exit code), runtime, command (truncated to 280 chars), and output section using Suspense + deferred output promise. Polls output every 1s while running. Key bindings: Space/Enter/Esc = close, Left = back, `x` = kill running.

### 11. ShellProgress.tsx (87 lines)

**Exports**: `ShellProgress`, `TaskStatusText` (React components)

**Types**: `TaskStatusTextProps` — status (TaskStatus), optional label/suffix.

**Functions/Components**:
- `TaskStatusText({ status, label, suffix })` — Renders status text with semantic color: success for completed, error for failed, warning for killed. Shows as `(label suffix)`.
- `ShellProgress({ shell })` — Switches on shell status to render appropriate `TaskStatusText`: "done" for completed, "error" for failed, "stopped" for killed, plain running status for running/pending.

### 12. taskStatusUtils.tsx (107 lines)

**Exports**: `isTerminalStatus`, `getTaskStatusIcon`, `getTaskStatusColor`, `describeTeammateActivity`, `shouldHideTasksFooter`

**Functions/Components**:
- `isTerminalStatus(status)` — Returns true if completed/failed/killed.
- `getTaskStatusIcon(status, options?)` — Returns figure icon: cross for errors, question-mark for awaiting approval, warning for shutdown requested, ellipsis for idle running, play for active running, tick for completed, cross for failed/killed, bullet for other.
- `getTaskStatusColor(status, options?)` — Returns semantic color: error/warning/background/success based on status and flags.
- `describeTeammateActivity(t)` — Derives human-readable activity string from teammate state, falling through shutdown → awaiting approval → idle → recent activities summary → last activity description → 'working'.
- `shouldHideTasksFooter(tasks, showSpinnerTree)` — True when spinner tree is active and all visible background tasks are in-process teammates (shown in tree instead).

---

## Directory 2: `components/teams/` (2 files)

### 1. TeamsDialog.tsx (715 lines)

**Exports**: `TeamsDialog` (React component)

**Types**: `Props` — optional `TeamSummary[]` initialTeams, `() => void` onDone. `DialogLevel` — union of `{ type: 'teammateList'; teamName }` and `{ type: 'teammateDetail'; teamName; memberName }`. `TeamDetailViewProps`, `TeammateListItemProps`, `TeammateDetailViewProps`.

**Functions/Components**:
- `killTeammate(paneId, backendType, teamName, teammateId, teammateName, setAppState)` — Kills a teammate's pane using the backend. Removes from team config, unassigns tasks, updates AppState, sends `teammate_terminated` inbox message.
- `viewTeammateOutput(paneId, backendType)` — Focuses teammate pane via iTerm2 or tmux commands.
- `toggleTeammateVisibility(teammate, teamName)` — Toggles hide/show of a teammate pane.
- `hideTeammate(teammate, teamName)` / `showTeammate(teammate, teamName)` — Ant-only placeholder functions.
- `sendModeChangeToTeammate(teammateName, teamName, targetMode)` — Updates config.json and sends mode set message to teammate.
- `cycleTeammateMode(teammate, teamName, isBypassAvailable)` — Cycles single teammate's permission mode.
- `cycleAllTeammateModes(teammates, teamName, isBypassAvailable)` — Cycles all teammates in tandem; if modes differ, resets all to default first.
- `TeamsDialog({ initialTeams, onDone })` — Main dialog with two-level navigation (list → detail). Supports raw keybindings: up/down arrows, Enter, `k` (kill), `s` (shutdown), `h`/`H` (hide/show), `p` (prune idle), shift+tab (cycle mode). Uses `useRegisterOverlay` for modal behavior, `useInterval` for 1s refresh of teammate statuses.
- `TeamDetailView({ teamName, teammates, selectedIndex, onCancel })` — List view with teammate count, pointer selection, and keyboard hints.
- `TeammateListItem({ teammate, isSelected })` — Single teammate row showing hidden/idle tags, permission mode symbol with color, model info, and `@name`.
- `TeammateDetailView({ teammate, teamName, onCancel })` — Detail view showing prompt (expandable with `p`), tasks list, model, working path, and mode symbol.

### 2. TeamStatus.tsx (80 lines)

**Exports**: `TeamStatus` (React component)

**Types**: `Props` — teamsSelected, showHint (booleans).

**Functions/Components**:
- `TeamStatus({ teamsSelected, showHint })` — Footer status indicator showing teammate count from `teamContext.teammates` (excluding team-lead). When selected + showHint, shows "Enter to view" hint. Uses inverse text styling for selected state.

---

## Directory 3: `components/TrustDialog/` (2 files)

### 1. TrustDialog.tsx (290 lines)

**Exports**: `TrustDialog` (React component)

**Types**: `Props` — `() => void` onDone, optional `Command[]` commands.

**Functions/Components**:
- `TrustDialog({ onDone, commands })` — Safety dialog shown at startup to confirm user trusts the current workspace directory. Checks for: MCP servers, hooks, bash permissions (from settings + slash commands + skills), API key helpers, AWS/GCP commands, OTel headers helpers, dangerous env vars. Tracks analytics events for shown/accepted. Offers "Yes, I trust this folder" (saves to project config or sets session flag) and "No, exit" (graceful shutdown). Uses `PermissionDialog` with warning color. CWD is displayed + security guide link.

### 2. utils.ts (245 lines)

**Exports**: `getHooksSources`, `getBashPermissionSources`, `formatListWithAnd`, `getOtelHeadersHelperSources`, `getApiKeyHelperSources`, `getAwsCommandsSources`, `getGcpCommandsSources`, `getDangerousEnvVarsSources`

**Functions/Components**:
- `hasHooks(settings)` — Checks if settings have hooks configured.
- `getHooksSources()` — Returns array of setting file paths that have hooks.
- `hasBashPermission(rules)` — Checks if any permission rule allows Bash tool.
- `getBashPermissionSources()` — Returns setting file paths that have bash allow rules.
- `formatListWithAnd(items, limit?)` — Formats a list with proper "and" conjunction; supports limiting with "...and N more".
- `hasOtelHeadersHelper(settings)` — Checks `otelHeadersHelper` setting.
- `getOtelHeadersHelperSources()` — Returns files with OTel headers configured.
- `hasApiKeyHelper(settings)` — Checks `apiKeyHelper` setting.
- `getApiKeyHelperSources()` — Returns files with API key helper configured.
- `hasAwsCommands(settings)` — Checks `awsAuthRefresh` or `awsCredentialExport`.
- `getAwsCommandsSources()` — Returns files with AWS commands configured.
- `hasGcpCommands(settings)` — Checks `gcpAuthRefresh`.
- `getGcpCommandsSources()` — Returns files with GCP commands configured.
- `hasDangerousEnvVars(settings)` — Checks for env vars NOT in SAFE_ENV_VARS.
- `getDangerousEnvVarsSources()` — Returns files with dangerous env vars.

---

## Directory 4: `components/wizard/` (5 files)

### 1. index.ts (9 lines)

**Exports**: Type exports for `WizardContextValue`, `WizardProviderProps`, `WizardStepComponent` from `./types.js`. Re-exports: `useWizard`, `WizardDialogLayout`, `WizardNavigationFooter`, `WizardProvider`.

### 2. useWizard.ts (13 lines)

**Exports**: `useWizard`

**Functions/Components**:
- `useWizard<T>()` — Context consumer hook for the Wizard context. Returns `WizardContextValue<T>`. Throws if not used within `WizardProvider`.

### 3. WizardDialogLayout.tsx (65 lines)

**Exports**: `WizardDialogLayout` (React component)

**Types**: `Props` — optional title/color/subtitle/footerText, required children.

**Functions/Components**:
- `WizardDialogLayout(props)` — Layout wrapper for wizard steps. Reads `currentStepIndex`, `totalSteps`, `providerTitle`, `showStepCounter`, `goBack` from wizard context. Combines title + step counter suffix. Renders `Dialog` with `WizardNavigationFooter`.

### 4. WizardNavigationFooter.tsx (24 lines)

**Exports**: `WizardNavigationFooter` (React component)

**Types**: `Props` — optional `ReactNode` instructions.

**Functions/Components**:
- `WizardNavigationFooter({ instructions })` — Footer with exit state display (Ctrl+C handling). Default instructions show arrow navigation, Enter select, and configurable back shortcut.

### 5. WizardProvider.tsx (213 lines)

**Exports**: `WizardContext` (React context), `WizardProvider` (React component)

**Functions/Components**:
- `WizardProvider<T>({ steps, initialData, onComplete, onCancel, children, title, showStepCounter })` — Context provider managing multi-step wizard state. Tracks `currentStepIndex`, `wizardData`, `navigationHistory` for breadcrumb-style back navigation, `isCompleted`. Provides: `goNext` (advances step or triggers onComplete), `goBack` (pops from navigation history or calls onCancel), `goToStep(index)`, `cancel`, `updateWizardData(updates)`, `currentStepIndex`, `totalSteps`, `wizardData`, `title`, `showStepCounter`. Uses `useExitOnCtrlCDWithKeybindings`. Renders current step component or children override.

---

## Directory 5: `components/FeedbackSurvey/` (9 files)

### 1. FeedbackSurvey.tsx (174 lines)

**Exports**: `FeedbackSurvey` (React component)

**Types**: `Props` — state (6-state union: closed/open/thanks/transcript_prompt/submitting/submitted), lastResponse, handleSelect, optional handleTranscriptSelect/onRequestFeedback/message, inputValue, setInputValue. `ThanksProps`.

**Constants**: `isFollowUpDigit` — type guard for '1'.

**Functions/Components**:
- `FeedbackSurvey(props)` — Top-level survey component. Renders nothing when closed. Routes to: `FeedbackSurveyThanks` (thanks state), transcript submitted view (submitted state), submitting spinner (submitting state), `TranscriptSharePrompt` (transcript_prompt state), or `FeedbackSurveyView` (open state with valid input).
- `FeedbackSurveyThanks({ lastResponse, inputValue, setInputValue, onRequestFeedback })` — Shows "Thanks for the feedback!" with optional follow-up prompt: "Press [1] to tell us what went well" (only for "good" responses). Uses `useDebouncedDigitInput` with `isFollowUpDigit` guard. Logs `tengu_feedback_survey_event` for followup_accepted.

### 2. FeedbackSurveyView.tsx (108 lines)

**Exports**: `FeedbackSurveyView`, `isValidResponseInput` (React component + validator)

**Types**: `Props` — onSelect, inputValue, setInputValue, optional message. `ResponseInput` — '0'|'1'|'2'|'3'.

**Constants**: `RESPONSE_INPUTS`, `inputToResponse` — maps digits to 'dismissed'/'bad'/'fine'/'good'. `DEFAULT_MESSAGE`.

**Functions/Components**:
- `isValidResponseInput(input)` — Type guard checking if input is a valid response digit.
- `FeedbackSurveyView(props)` — Renders question "How is Claude doing this session? (optional)" with digit options: 1:Bad, 2:Fine, 3:Good, 0:Dismiss. Uses `useDebouncedDigitInput` for debounced digit detection.

### 3. submitTranscriptShare.ts (112 lines)

**Exports**: `submitTranscriptShare`, type `TranscriptShareTrigger`

**Types**: `TranscriptShareResult` — success boolean + optional transcriptId. `TranscriptShareTrigger` — 'bad_feedback_survey' | 'good_feedback_survey' | 'frustration' | 'memory_survey'.

**Functions/Components**:
- `submitTranscriptShare(messages, trigger, appearanceId)` — Posts transcript to Anthropic API. Collects normalized messages, subagent transcripts, raw JSONL transcript (with size guard via `MAX_TRANSCRIPT_READ_BYTES`), redacts sensitive info, authenticates via OAuth, and POSTs to `https://api.anthropic.com/api/claude_code_shared_session_transcripts`.

### 4. TranscriptSharePrompt.tsx (88 lines)

**Exports**: `TranscriptSharePrompt`, type `TranscriptShareResponse`

**Types**: `TranscriptShareResponse` — 'yes' | 'no' | 'dont_ask_again'. `Props` — onSelect, inputValue, setInputValue.

**Constants**: `RESPONSE_INPUTS`, `inputToResponse` — maps '1'/'2'/'3' to yes/no/dont_ask_again.

**Functions/Components**:
- `TranscriptSharePrompt({ onSelect, inputValue, setInputValue })` — Prompts "Can Anthropic look at your session transcript to help us improve Claude Code?" with options: 1:Yes, 2:No, 3:Don't ask again. Uses `useDebouncedDigitInput`.

### 5. useDebouncedDigitInput.ts (82 lines)

**Exports**: `useDebouncedDigitInput`

**Constants**: `DEFAULT_DEBOUNCE_MS = 400`.

**Functions/Components**:
- `useDebouncedDigitInput<T>({ inputValue, setInputValue, isValidDigit, onDigit, enabled, once, debounceMs })` — Hook that detects single-digit input from prompt text, debounces to prevent accidental submission (e.g., numbered list "1. First item"). On valid digit, clears the digit from input and fires `onDigit`. Uses refs to avoid re-running effect on callback changes. Returns cleanup function to clear timeout.

### 6. useFeedbackSurvey.tsx (296 lines)

**Exports**: `useFeedbackSurvey` (React hook)

**Types**: `FeedbackSurveyConfig` — minTimeBeforeFeedbackMs, minTimeBetweenFeedbackMs, minTimeBetweenGlobalFeedbackMs, minUserTurnsBeforeFeedback, minUserTurnsBetweenFeedback, hideThanksAfterMs, onForModels, probability. `TranscriptAskConfig` — probability.

**Constants**: `DEFAULT_FEEDBACK_SURVEY_CONFIG` — 600s initial, 3600s between, 100Ms global pacing, 5/10 turns, 3s thanks, all models, 0.5% probability. `DEFAULT_TRANSCRIPT_ASK_CONFIG` — 0 probability.

**Functions/Components**:
- `useFeedbackSurvey(messages, isLoading, submitCount, surveyType, hasActivePrompt)` — Master hook for session feedback surveys. Uses `useDynamicConfig` for GrowthBook config overrides. Manages pacing: session-local time/turn gates, probability gate (rolled once per eligibility window), global pacing across sessions. Computes `shouldOpen` with guard checks: not loading, hasActivePrompt suppression, model allowlist, env disable flags, org policy checks. Returns `{ state, lastResponse, handleSelect, handleTranscriptSelect }`. Delegates state management to `useSurveyState`. Handles transcript share flow with separate probability configs for bad vs good ratings.

### 7. useMemorySurvey.tsx (213 lines)

**Exports**: `useMemorySurvey` (React hook)

**Constants**: `HIDE_THANKS_AFTER_MS = 3000`, `MEMORY_SURVEY_GATE`, `MEMORY_SURVEY_EVENT`, `SURVEY_PROBABILITY = 0.2`, `TRANSCRIPT_SHARE_TRIGGER = 'memory_survey'`, `MEMORY_WORD_RE` — regex matching "memory" or "memories".

**Functions/Components**:
- `hasMemoryFileRead(messages)` — Scans messages for assistant tool_use blocks of type FILE_READ_TOOL_NAME where file_path refers to an auto-managed memory file.
- `useMemorySurvey(messages, isLoading, hasActivePrompt, { enabled })` — Hook that triggers a survey after an assistant message mentions "memory" AND a memory file was read. Uses GrowthBook gate `tengu_dunwich_bell`, checks auto-memory enabled, feedback survey disabled, policy allowed. Tracks seen assistant UUIDs to avoid re-evaluation. Marks memory as seen once detected (stays true for session). 20% probability roll. Returns `{ state, lastResponse, handleSelect, handleTranscriptSelect }`.

### 8. usePostCompactSurvey.tsx (206 lines)

**Exports**: `usePostCompactSurvey` (React hook)

**Constants**: `HIDE_THANKS_AFTER_MS = 3000`, `POST_COMPACT_SURVEY_GATE`, `SURVEY_PROBABILITY = 0.2`.

**Functions/Components**:
- `hasMessageAfterBoundary(messages, boundaryUuid)` — Checks if any user or assistant message exists after a compact boundary message.
- `usePostCompactSurvey(messages, isLoading, hasActivePrompt, { enabled })` — Survey triggered after session memory compaction. Uses GrowthBook/Statsig gate, checks feedback disabled, env disable flags. Tracks seen compact boundaries via UUID set. When a new compact boundary appears, waits for the next user/assistant message after it, then rolls 20% probability to open survey. Tracks `session_memory_compaction_enabled` in analytics.

### 9. useSurveyState.tsx (100 lines)

**Exports**: `useSurveyState` (React hook)

**Types**: `SurveyState` — 6-state union. `UseSurveyStateOptions` — hideThanksAfterMs, onOpen, onSelect, optional shouldShowTranscriptPrompt, onTranscriptPromptShown, onTranscriptSelect.

**Functions/Components**:
- `useSurveyState(options)` — State machine for survey lifecycle. Manages: `state` (closed → open → thanks/transcript_prompt → submitting → submitted → closed), `lastResponse`, `appearanceId` (random UUID per survey appearance). Exposes `open()` (triggers appearance, generates new ID, calls onOpen), `handleSelect(selected)` (records response, calls onSelect, optionally routes to transcript prompt or shows thanks with timeout), `handleTranscriptSelect(selected)` (handles yes/no/dont_ask_again, triggers submission flow or shows thanks). Thanks and submitted states auto-close after `hideThanksAfterMs`.

---

## Directory 6: `components/StructuredDiff/` (2 files)

### 1. colorDiff.ts (37 lines)

**Exports**: `getColorModuleUnavailableReason`, `expectColorDiff`, `expectColorFile`, `getSyntaxTheme`, type `ColorModuleUnavailableReason`

**Types**: `ColorModuleUnavailableReason` — 'env'.

**Functions/Components**:
- `getColorModuleUnavailableReason()` — Returns 'env' if `CLAUDE_CODE_SYNTAX_HIGHLIGHT` env var is falsy, otherwise null.
- `expectColorDiff()` — Returns `ColorDiff` class if available, else null.
- `expectColorFile()` — Returns `ColorFile` class if available, else null.
- `getSyntaxTheme(themeName)` — Returns SyntaxTheme or null based on availability.

### 2. Fallback.tsx (487 lines)

**Exports**: `StructuredDiffFallback`, `transformLinesToObjects`, `processAdjacentLines`, `calculateWordDiffs`, `numberDiffLines`, type `LineObject` (React component + utilities)

**Types**: `DiffLine` — code, type (add/remove/nochange), i (line number), originalCode, optional wordDiff/matchedLine. `LineObject` — same shape. `DiffPart` — optional added/removed, value. `Props` — `StructuredPatchHunk` patch, dim, width.

**Constants**: `CHANGE_THRESHOLD = 0.4` — ratio above which word-level diff falls back to full-line diff.

**Functions/Components**:
- `transformLinesToObjects(lines)` — Maps diff lines to `LineObject[]`, stripping `+`/`-` prefixes and setting type.
- `processAdjacentLines(lineObjects)` — Groups adjacent remove+add lines into word-diff pairs. Pairs up corresponding remove/add sequences and marks them with `wordDiff`/`matchedLine`.
- `calculateWordDiffs(oldText, newText)` — Uses `diffWordsWithSpace` for word-level comparison preserving whitespace.
- `generateWordDiffElements(item, width, maxWidth, dim, overrideTheme?)` — Renders word-level diff lines with background highlighting. Wraps text to terminal width, pads to fill remaining space. Uses `diffAddedWord`/`diffRemovedWord` colors for changed words within lines.
- `numberDiffLines(diff, startLine)` — Assigns line numbers to structured diff, handling remove lines that share the same number.
- `formatDiff(lines, startingLineNumber, width, dim, overrideTheme?)` — Full pipeline: transform lines → process adjacent → number → render. Falls back to standard line rendering when word-diff ratio exceeds threshold.
- `StructuredDiffFallback({ patch, dim, width })` — Main component calling `formatDiff` with patch data and rendering all lines in a flex-column box.

---

## Directory 7: `components/ui/` (3 files)

### 1. OrderedList.tsx (71 lines)

**Exports**: `OrderedList` (React component with `OrderedList.Item = OrderedListItem`)

**Types**: `OrderedListProps` — children.

**Functions/Components**:
- `OrderedListComponent({ children })` — Nested ordered list renderer. Counts `OrderedListItem` children, calculates max marker width for padding alignment. Wraps each list item in context providers with hierarchical markers (e.g., "1.2."). Supports nesting via `OrderedListContext`. Attaches `Item = OrderedListItem` as static property.

### 2. OrderedListItem.tsx (45 lines)

**Exports**: `OrderedListItem`, `OrderedListItemContext` (React component + context)

**Types**: `OrderedListItemProps` — children.

**Functions/Components**:
- `OrderedListItem({ children })` — Renders a single list item with dimmed marker text read from context, followed by the children in a flex column.

### 3. TreeSelect.tsx (397 lines)

**Exports**: `TreeSelect`, type `TreeNode<T>`, type `TreeSelectProps<T>`, type `FlattenedNode<T>` (React component + types)

**Types**: `TreeNode<T>` — id, value (T), label, optional description/dimDescription/children/metadata. `FlattenedNode<T>` — node, depth, isExpanded, hasChildren, optional parentId. `TreeSelectProps<T>` — nodes, onSelect, optional onCancel/onFocus/focusNodeId/visibleOptionCount/layout (compact|expanded|compact-vertical)/isDisabled/hideIndexes/isNodeExpanded/onExpand/onCollapse/getParentPrefix/getChildPrefix/onUpFromFirstItem.

**Functions/Components**:
- `TreeSelect(props)` — Generic hierarchical selection component. Internally flattens tree into a list using recursive `traverse()` respecting expand/collapse state. Manages `internalExpandedIds` via `Set<string>` state. Default prefixes: `▶ `/`▼ ` for parent nodes, `  ▸ ` for children. Supports keyboard navigation: right arrow to expand, left arrow to collapse or navigate to parent. Uses `Select` component for rendering. Provides `onFocus` callback with programmatic-focus detection. Supports `isNodeExpanded` for external expansion control.

---

## Directory 8: `components/ClaudeCodeHint/` (1 file)

### PluginHintMenu.tsx (78 lines)

**Exports**: `PluginHintMenu` (React component)

**Types**: `Props` — pluginName, optional pluginDescription, marketplaceName, sourceCommand, onResponse ('yes'|'no'|'disable').

**Constants**: `AUTO_DISMISS_MS = 30_000`.

**Functions/Components**:
- `PluginHintMenu(props)` — Modal dialog recommending a plugin installation. Shows plugin name, marketplace, source command, optional description. 3 options: "Yes, install", "No", "No, and don't show again". Auto-dismisses after 30s (counts as 'no'). Uses `PermissionDialog` wrapper.

---

## Directory 9: `components/DesktopUpsell/` (1 file)

### DesktopUpsellStartup.tsx (171 lines)

**Exports**: `DesktopUpsellStartup`, `getDesktopUpsellConfig`, `shouldShowDesktopUpsellStartup` (React component + utilities)

**Types**: `DesktopUpsellConfig` — enable_shortcut_tip, enable_startup_dialog. `DesktopUpsellSelection` — 'try'|'not-now'|'never'. `Props` — onDone.

**Constants**: `DESKTOP_UPSELL_DEFAULT` — both flags false.

**Functions/Components**:
- `getDesktopUpsellConfig()` — Returns GrowthBook dynamic config for desktop upsell.
- `isSupportedPlatform()` — True for macOS or Windows x64.
- `shouldShowDesktopUpsellStartup()` — Gate checker: supported platform + config enabled + not dismissed + seen < 3 times.
- `DesktopUpsellStartup({ onDone })` — Startup dialog promoting Claude Code Desktop. Tracks shown count and analytics. Options: "Open in Claude Code Desktop" (shows `DesktopHandoff` component), "Not now", "Don't ask again" (saves to global config).

---

## Directory 10: `components/grove/` (1 file)

### Grove.tsx (463 lines)

**Exports**: `GroveDialog`, `PrivacySettingsDialog`, type `GroveDecision` (React components + type)

**Types**: `GroveDecision` — 'accept_opt_in' | 'accept_opt_out' | 'defer' | 'escape' | 'skip_rendering'. `Props` — showIfAlreadyViewed, location, onDone. `PrivacySettingsDialogProps` — settings, optional domainExcluded, onDone.

**Constants**: `NEW_TERMS_ASCII` — ASCII art banner.

**Functions/Components**:
- `GracePeriodContentBody()` — Content for grace period notice: explains terms update effective October 8, 2025, what's changing (improve Claude training, data retention to 5 years), links to learn more and legal documents.
- `PostGracePeriodContentBody()` — Content for post-grace period: similar but different wording.
- `GroveDialog({ showIfAlreadyViewed, location, onDone })` — Terms/policy update dialog. Async loads grove settings + config, calculates whether to show via `calculateShouldShowGrove`. Supports two audience-specific option lists (domain_excluded gets only opt-out, others get both opt-in/opt-out). Grace period shows "Not now" defer option. Analytics events for viewed/submitted/dismissed/escaped. Calls `updateGroveSettings(bool)` for acceptance.
- `PrivacySettingsDialog({ settings, domainExcluded, onDone })` — Settings-level dialog showing current grove_enabled state. Allows toggling via Tab/Enter/Space (unless domain-excluded). Shows "true"/"false (for emails with your domain)". Links to privacy settings web UI.

---

## Directory 11: `components/HelpV2/` (3 files)

### 1. HelpV2.tsx (184 lines)

**Exports**: `HelpV2` (React component)

**Types**: `Props` — onClose, commands.

**Functions/Components**:
- `HelpV2({ onClose, commands })` — Tabbed help dialog. Splits commands into builtin (via `builtInCommandNames()`), custom (non-builtin, non-hidden), and ant-only. Renders 3 tabs: "general" (shortcuts + description), "commands" (browse builtin commands), "custom-commands" (browse custom commands). Uses `Pane` with `professionalBlue` color. Shows version in title. Height limited to `rows/2` when inside modal. Dismiss via `help:dismiss` keybinding.

### 2. Commands.tsx (82 lines)

**Exports**: `Commands` (React component)

**Types**: `Props` — commands array, maxHeight, columns, title, onCancel, optional emptyMessage.

**Functions/Components**:
- `Commands({ commands, maxHeight, columns, title, onCancel, emptyMessage })` — Browsable list of commands. Deduplicates by name, sorts alphabetically, truncates descriptions to `columns - 10`. Uses `Select` with `disableSelection` + `compact-vertical` layout for read-only browsing. Supports `useTabHeaderFocus` for keyboard navigation between tabs.

### 3. General.tsx (23 lines)

**Exports**: `General` (React component)

**Functions/Components**:
- `General()` — Static help content: description of Claude Code + `PromptInputHelpMenu` showing keyboard shortcuts.

---

## Directory 12: `components/HighlightedCode/` (1 file)

### Fallback.tsx (193 lines)

**Exports**: `HighlightedCodeFallback` (React component)

**Types**: `Props` — code, filePath, optional dim/skipColoring.

**Constants**: `HL_CACHE_MAX = 500` — LRU cache limit for highlighted code.

**Functions/Components**:
- `cachedHighlight(hl, code, language)` — Module-level LRU cache for CLI highlight results. Keyed by hash of code+language. Evicts oldest entry at capacity.
- `Highlighted({ codeWithSpaces, language })` — Inner component using React `use()` to unwrap highlight promise. Falls back to markdown if language unsupported. Catches "Unknown language" errors and retries with markdown.
- `HighlightedCodeFallback({ code, filePath, dim, skipColoring })` — Main fallback component. Converts leading tabs to spaces. If `skipColoring`, renders plain text via `Ansi`. Otherwise determines language from file extension, wraps in `Suspense` with `Ansi` fallback, and renders syntax-highlighted output.

---

## Directory 13: `components/LspRecommendation/` (1 file)

### LspRecommendationMenu.tsx (88 lines)

**Exports**: `LspRecommendationMenu` (React component)

**Types**: `Props` — pluginName, optional pluginDescription, fileExtension, onResponse ('yes'|'no'|'never'|'disable').

**Constants**: `AUTO_DISMISS_MS = 30_000`.

**Functions/Components**:
- `LspRecommendationMenu(props)` — Modal recommending LSP plugin installation. Shows plugin name, description, triggering file extension. 4 options: "Yes, install", "No, not now", "Never for {plugin}", "Disable all LSP recommendations". Auto-dismisses after 30s (counts as 'no'). Uses `PermissionDialog` wrapper.

---

## Directory 14: `components/ManagedSettingsSecurityDialog/` (2 files)

### 1. ManagedSettingsSecurityDialog.tsx (149 lines)

**Exports**: `ManagedSettingsSecurityDialog` (React component)

**Types**: `Props` — SettingsJson settings, `() => void` onAccept/onReject.

**Functions/Components**:
- `ManagedSettingsSecurityDialog({ settings, onAccept, onReject })` — Security confirmation dialog for managed (org-controlled) settings. Extracts dangerous settings via `extractDangerousSettings`, formats them as list via `formatDangerousSettingsList`. Shows warning text about arbitrary code execution/prompt interception, list of unsafe settings, and trust confirmation. Uses `PermissionDialog` with warning color.

### 2. utils.ts (144 lines)

**Exports**: `extractDangerousSettings`, `hasDangerousSettings`, `hasDangerousSettingsChanged`, `formatDangerousSettingsList`, type `DangerousSettings`

**Types**: `DangerousSettings` — shellSettings (Partial Record of DANGEROUS_SHELL_SETTINGS → string), envVars (Record string → string), hasHooks, optional hooks.

**Functions/Components**:
- `extractDangerousSettings(settings)` — Extracts dangerous shell settings, env vars (those NOT in SAFE_ENV_VARS), and hooks presence from settings.
- `hasDangerousSettings(dangerous)` — True if any shell settings, env vars, or hooks exist.
- `hasDangerousSettingsChanged(oldSettings, newSettings)` — Compares two settings snapshots by JSON stringifying dangerous fields.
- `formatDangerousSettingsList(dangerous)` — Returns array of setting key names (not values) for display.

---

## Directory 15: `components/Passes/` (1 file)

### Passes.tsx (184 lines)

**Exports**: `Passes` (React component)

**Types**: `PassStatus` — passNumber, isAvailable. `Props` — onDone.

**Functions/Components**:
- `Passes({ onDone })` — Guest passes dialog. Async loads passes eligibility and redemption data via `getCachedOrFetchPassesEligibility` and `fetchReferralRedemptions`. Renders ASCII-art tickets (available vs redeemed with slashes), referral link, description text with reward info. Enter copies link to clipboard via `setClipboard`. Shows loading/unavailable/available states. Uses `Pane` wrapper.

---

## Directory 16: `components/skills/` (1 file)

### SkillsMenu.tsx (237 lines)

**Exports**: `SkillsMenu` (React component)

**Types**: `SkillCommand` — intersection of CommandBase & PromptCommand. `SkillSource` — SettingSource | 'plugin' | 'mcp'. `Props` — onExit, commands.

**Functions/Components**:
- `getSourceTitle(source)` — Returns title like "Plugin skills", "MCP skills", or "{Cap source name} skills".
- `getSourceSubtitle(source, skills)` — For MCP, shows server names (extracted from `server:skill` format). For file-based, shows filesystem path with `getDisplayPath`. Adds commands source if any skills loaded via commands_DEPRECATED.
- `SkillsMenu({ onExit, commands })` — Lists all skills (prompt commands loaded from skills/commands_DEPRECATED/plugin/mcp). Groups by source: projectSettings, userSettings, policySettings, plugin, mcp. Each group shows title, subtitle (path or servers), and skills with estimated frontmatter tokens. Empty state shows "Create skills in .claude/skills/" message.

---

## Directory 17: `components/memory/` (2 files)

### 1. MemoryFileSelector.tsx (438 lines)

**Exports**: `MemoryFileSelector` (React component)

**Types**: `ExtendedMemoryFileInfo` — extends MemoryFileInfo with isNested?, exists. `Props` — onSelect(path), onCancel.

**Constants**: `OPEN_FOLDER_PREFIX = '__open_folder__'` — prefix for folder-open actions. Module-level `lastSelectedPath` variable remembers last selection.

**Functions/Components**:
- `MemoryFileSelector({ onSelect, onCancel })` — Multi-purpose dialog for viewing/opening memory files. Lists all CLAUDE.md files (user, project, nested/imported) with type labels (User memory, Project memory, "@-imported", "dynamically loaded"). Folders section: auto-memory folder, team memory folder (feature-gated), per-agent memory folders. Toggle section: Auto-memory on/off, Auto-dream on/off (with /dream ready status). Uses `Select` component for navigation. Enter selects a file; folders open in file manager via `openPath`. Remembers last selected path across invocations.

### 2. MemoryUpdateNotification.tsx (45 lines)

**Exports**: `MemoryUpdateNotification`, `getRelativeMemoryPath` (React component + utility)

**Functions/Components**:
- `getRelativeMemoryPath(path)` — Converts absolute path to shortest relative form: `~/.claude/...` or `./relative/path` or original.
- `MemoryUpdateNotification({ memoryPath })` — Simple notification: "Memory updated in {path} · /memory to edit".

---

## Directory 18: `components/mcp/utils/` (1 file)

### reconnectHelpers.tsx (49 lines)

**Exports**: `handleReconnectResult`, `handleReconnectError`, type `ReconnectResult`

**Types**: `ReconnectResult` — message, success.

**Functions/Components**:
- `handleReconnectResult(result, serverName)` — Switches on client connection type ('connected'/'needs-auth'/'failed') and returns appropriate ReconnectResult.
- `handleReconnectError(error, serverName)` — Formats error messages for reconnect failures.

---

## Directory 19: `components/agents/` (14 files + 12 wizard-step files)

### Core Files

### 1. agentFileUtils.ts (272 lines)

**Exports**: `formatAgentAsMarkdown`, `getNewAgentFilePath`, `getActualAgentFilePath`, `getNewRelativeAgentFilePath`, `getActualRelativeAgentFilePath`, `saveAgentToFile`, `updateAgentFile`, `deleteAgentFromFile`

**Functions/Components**:
- `formatAgentAsMarkdown(agentType, whenToUse, tools, systemPrompt, color?, model?, memory?, effort?)` — Formats agent data as YAML frontmatter + markdown. Escapes backslashes, double-quotes, newlines in YAML strings. Omits tools when undefined or ['*'].
- `getAgentDirectoryPath(location)` — Maps SettingSource to filesystem path: userSettings → ~/.claude/agents/, projectSettings/localSettings → ./.claude/agents/, policySettings → managed path, flagSettings throws.
- `getRelativeAgentDirectoryPath(location)` — Relative path for display purposes.
- `getNewAgentFilePath({ source, agentType })` — File path for a new agent (uses agentType as filename).
- `getActualAgentFilePath(agent)` — File path for an existing agent (uses `agent.filename` or `agent.agentType` as filename). Returns 'Built-in' for built-in, throws for plugin.
- `getNewRelativeAgentFilePath(agent)` — Relative display path for new agents.
- `getActualRelativeAgentFilePath(agent)` — Relative display path for existing agents.
- `ensureAgentDirectoryExists(source)` — Creates agent directory if needed.
- `saveAgentToFile(source, agentType, whenToUse, tools, systemPrompt, checkExists, color?, model?, memory?, effort?)` — Saves agent markdown to filesystem. Uses `'wx'` flag when checkExists to fail on collision, otherwise `'w'`.
- `updateAgentFile(agent, newWhenToUse, newTools, newSystemPrompt, newColor?, newModel?, newMemory?, newEffort?)` — Overwrites existing agent file.
- `deleteAgentFromFile(agent)` — Unlinks agent file (ignores ENOENT).
- `writeFileAndFlush(filePath, content, flag)` — Private: opens file, writes content, calls datasync() for durability, then closes.

### 2. validateAgent.ts (109 lines)

**Exports**: `validateAgent`, `validateAgentType`, type `AgentValidationResult`

**Types**: `AgentValidationResult` — isValid, errors[], warnings[].

**Functions/Components**:
- `validateAgentType(agentType)` — Validates agent type format: required, alphanumeric + hyphens, 3-50 chars, must start/end with alphanumeric.
- `validateAgent(agent, availableTools, existingAgents)` — Full validation: type + duplicate check, description (required, min 10 chars), tools (array validation, invalid tools via `resolveAgentTools`), system prompt (required, min 20 chars).

### 3. types.ts (27 lines)

**Exports**: `AGENT_PATHS` constant, type `ModeState`, type `AgentValidationResult`

**Types**: `AGENT_PATHS` — FOLDER_NAME: '.claude', AGENTS_DIR: 'agents'. `ModeState` — discriminated union: 'main-menu' | 'list-agents' (with source) | 'agent-menu' (with agent + previousMode) | 'view-agent' | 'create-agent' | 'edit-agent' | 'delete-confirm'.

### 4. utils.ts (18 lines)

**Exports**: `getAgentSourceDisplayName`

**Functions/Components**:
- `getAgentSourceDisplayName(source)` — Returns display name: 'Agents' for 'all', 'Built-in agents' for 'built-in', 'Plugin agents' for 'plugin', or capitalized setting source name.

### 5. generateAgent.ts (197 lines)

**Exports**: `generateAgent`

**Types**: `GeneratedAgent` — identifier, whenToUse, systemPrompt.

**Constants**: `AGENT_CREATION_SYSTEM_PROMPT` — Detailed system prompt instructing Claude to act as an agent architect: extract intent, design persona, create identifier, write system prompt, with 6 numbered directives. `AGENT_MEMORY_INSTRUCTIONS` — Memory-specific instructions appended when auto-memory is enabled.

**Functions/Components**:
- `generateAgent(userPrompt, model, existingIdentifiers, abortSignal)` — Calls Claude API with a system prompt to generate an agent configuration from a natural language description. Prepends user context (CLAUDE.md files, etc.) to messages. Returns `{ identifier, whenToUse, systemPrompt }`. Parses JSON from response, handles missing JSON with regex fallback. Emits `tengu_agent_definition_generated` analytics event.

### 6. AgentDetail.tsx (220 lines)

**Exports**: `AgentDetail` (React component)

**Types**: `Props` — agent, tools, optional allAgents, onBack.

**Functions/Components**:
- `AgentDetail({ agent, tools, onBack })` — Read-only agent view. Shows: file path, description (whenToUse) rendered as Markdown, tools list (resolved via `resolveAgentTools` with warning for unrecognized tools), model, color sample, memory scope, and system prompt (rendered as Markdown). Uses `getActualRelativeAgentFilePath`, `getAgentColor` for background, `getAgentModelDisplay`. Key bindings: Enter/Esc = back.

### 7. AgentEditor.tsx (178 lines)

**Exports**: `AgentEditor` (React component)

**Types**: `EditMode` — 'menu' | 'edit-tools' | 'edit-color' | 'edit-model'. `SaveChanges` — optional tools/color/model. `Props` — agent, tools, onSaved, onBack.

**Functions/Components**:
- `AgentEditor({ agent, tools, onSaved, onBack })` — Agent editing interface with menu-driven navigation. Menu items: "Open in editor" (opens file in external editor via `editFileInEditor`), "Edit tools" (opens `ToolSelector`), "Edit color" (opens `ColorPicker`), "Edit model" (opens `ModelSelector`). Save flow calls `updateAgentFile` and `setAgentColor`, then updates AppState's `agentDefinitions`. Only works for custom/plugin agents.

### 8. AgentNavigationFooter.tsx (26 lines)

**Exports**: `AgentNavigationFooter` (React component)

**Types**: `Props` — optional instructions string.

**Functions/Components**:
- `AgentNavigationFooter({ instructions })` — Footer with Ctrl+C exit handling; shows either exit confirmation or navigation instructions.

### 9. AgentsList.tsx (440 lines)

**Exports**: `AgentsList` (React component)

**Types**: `Props` — source, agents (ResolvedAgent[]), onBack, onSelect, optional onCreateNew/changes.

**Functions/Components**:
- `AgentsList({ source, agents, onBack, onSelect, onCreateNew, changes })` — Scrollable list of agents for a given source. Shows "Create new agent" option at top (when onCreateNew provided). Each agent row shows: agentType, resolved model display, memory scope, override/shadow warnings. Non-built-in agents are selectable (built-in always dimmed). Supports keyboard navigation: up/down to select, Enter to select agent or create new, Esc to go back. Uses `AGENT_SOURCE_GROUPS` for source ordering.

### 10. AgentsMenu.tsx (800 lines)

**Exports**: `AgentsMenu` (React component)

**Types**: `Props` — tools, onExit.

**Functions/Components**:
- `AgentsMenu({ tools, onExit })` — Top-level agent management component implementing a state machine via `ModeState`. Modes:
  - `main-menu`: 6 options — "Browse agents", "Manage active agents", "Create new agent", "View agent detail", "List agents by source", "Exit".
  - `list-agents`: Delegates to `AgentsList` with source filter.
  - `agent-menu`: Per-agent menu with "View details", "Edit", "Delete" (drilldown to confirmation), and "Back".
  - `view-agent`: Delegates to `AgentDetail`.
  - `edit-agent`: Delegates to `AgentEditor`.
  - `create-agent`: Delegates to `CreateAgentWizard`.
  - `delete-confirm`: Confirmation dialog with "Yes, delete" and "No, go back".
  Manages `changes` array tracking unsaved changes across edits. Fetches `allAgents` and `activeAgents` from AppState. MCP tools included via `useMergedTools`. Uses `Dialog` for consistent modal presentation.

### 11. ColorPicker.tsx (112 lines)

**Exports**: `ColorPicker` (React component)

**Types**: `ColorOption` — AgentColorName | 'automatic'. `Props` — agentName, optional currentColor, onConfirm.

**Constants**: `COLOR_OPTIONS` — ['automatic', ...AGENT_COLORS].

**Functions/Components**:
- `ColorPicker({ agentName, currentColor, onConfirm })` — Up/down navigable color picker. Shows all agent colors with swatch backgrounds + "Automatic color" first option. Live preview of `@agentName` in selected color. Enter confirms selection (undefined for automatic). Wraps around at top/bottom.

### 12. ModelSelector.tsx (68 lines)

**Exports**: `ModelSelector` (React component)

**Types**: `ModelSelectorProps` — optional initialModel, onComplete, optional onCancel.

**Functions/Components**:
- `ModelSelector({ initialModel, onComplete, onCancel })` — Model selection dropdown. Gets options via `getAgentModelOptions()`. If agent's current model is a custom ID not in the alias list, injects it as first option to preserve round-trip. Defaults to 'sonnet'. On cancel, calls onComplete(undefined).

### 13. ToolSelector.tsx (562 lines)

**Exports**: `ToolSelector` (React component)

**Types**: `ToolBucket` — name, toolNames (Set), isMcp?. `ToolBuckets` — READ_ONLY, EDIT, EXECUTION, MCP, OTHER. `Props` — tools, initialTools (string[] | undefined), onComplete, optional onCancel.

**Functions/Components**:
- `getToolBuckets()` — Returns predefined tool bucket definitions: READ_ONLY (Glob, Grep, ExitPlanMode, FileRead, WebFetch, TodoWrite, WebSearch, TaskStop, TaskOutput, ListMcpResources, ReadMcpResource), EDIT (FileEdit, FileWrite, NotebookEdit), EXECUTION (Bash, Tungsten [ant-only]), MCP (dynamic), OTHER (catch-all).
- `getMcpServerBuckets(tools)` — Groups MCP tools by server name, sorted alphabetically.
- `ToolSelector({ tools, initialTools, onComplete, onCancel })` — Checkbox-style tool selector. Bucket-level toggles: "All tools", "Read-only tools", "Edit tools", "Execution tools", "MCP tools" (per server), "Other tools". "Continue" button at top. "Show advanced options" toggle reveals individual tool checkboxes. MCP tools displayed with server groupings. Keyboard: up/down/Enter to toggle, handles checkbox figures for selected/unselected. Initial tools expanded from '*' wildcard or passed directly.

### 14. CreateAgentWizard.tsx (97 lines)

**Exports**: `CreateAgentWizard` (React component)

**Types**: `Props` — tools, existingAgents, onComplete(message), onCancel.

**Functions/Components**:
- `CreateAgentWizard({ tools, existingAgents, onComplete, onCancel })` — Wizard-based agent creation. Steps (in order): LocationStep, MethodStep, GenerateStep (if generate method), TypeStep, PromptStep, DescriptionStep, ToolsStep, ModelStep, ColorStep, MemoryStep (if auto-memory enabled), ConfirmStepWrapper. Wraps everything in `WizardProvider` with empty initial data and `showStepCounter: false`. The `onComplete` callback is a no-op at the WizardProvider level because the ConfirmStepWrapper handles the actual save directly.

### Wizard Steps (new-agent-creation/wizard-steps/)

### 15. LocationStep.tsx (80 lines)
- Chooses agent location: "Project (.claude/agents/)" or "Personal (~/.claude/agents/)". Sets `location` in wizard data and advances.

### 16. MethodStep.tsx (80 lines)
- Chooses creation method: "Generate with Claude (recommended)" advances normally; "Manual configuration" jumps to TypeStep (step 3).

### 17. GenerateStep.tsx (143 lines)
- Natural language agent generation step. Text input for describing what the agent should do. On submit, calls `generateAgent` API with abort controller support. During generation, shows spinner + cancel option. On success, populates agentType, whenToUse, systemPrompt and jumps to ToolsStep (step 6). Supports external editor via `chat:externalEditor` keybinding.

### 18. TypeStep.tsx (103 lines)
- Manual agent identifier entry. Validates via `validateAgentType` (alphanumeric + hyphens, 3-50 chars). Sets `agentType` in wizard data.

### 19. PromptStep.tsx (128 lines)
- System prompt text input. Validates non-empty. Supports external editor. Sets `systemPrompt` in wizard data.

### 20. DescriptionStep.tsx (123 lines)
- When-to-use description text input. Validates non-empty (trimmed). Supports external editor. Sets `whenToUse` in wizard data.

### 21. ToolsStep.tsx (61 lines)
- Delegates to `ToolSelector` with agent-specific tools. Sets `selectedTools` in wizard data.

### 22. ModelStep.tsx (52 lines)
- Delegates to `ModelSelector`. Sets `selectedModel` in wizard data.

### 23. ColorStep.tsx (84 lines)
- Delegates to `ColorPicker`. Constructs `finalAgent` object in wizard data with all accumulated fields.

### 24. MemoryStep.tsx (113 lines)
- Memory scope selection (only if auto-memory enabled). Options ordered by recommendation based on agent location (user scope preferred for userSettings agents, project scope for projectSettings). When memory selected, appends memory prompt to system prompt via `loadAgentMemoryPrompt`. Sets `selectedMemory` and updates `finalAgent`.

### 25. ConfirmStep.tsx (378 lines)
- Final review step. Shows validation results (warnings/errors), name, location, tools list, model, memory scope, description preview, system prompt preview. Key bindings: `s`/Enter = save, `e` = save and open in editor. Errors block saving.

### 26. ConfirmStepWrapper.tsx (74 lines)
- Wrapper providing save logic: calls `saveAgentToFile`, updates AppState, optionally opens in editor, logs `tengu_agent_created` analytics. Dispatches error state to ConfirmStep.
