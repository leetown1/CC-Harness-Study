# 02 — Components System

> **389 files** | React component hierarchy: messages, permissions, dialogs, agents, MCP, design system

## Overview

The Components layer is the UI surface of Claude Code. Everything the user sees — messages, dialogs, permission prompts, settings, file diffs — is built from these components. They are organized into logical groups: core layout components, message renderers, permission UI, feature-specific components (agents, MCP, plugins), and a reusable design system.

---

## 1. Core Components (Root)

### 1.1 Layout & Shell

#### `App.tsx` (56 lines)
Top-level wrapper for interactive sessions. Provides three context layers: `FpsMetricsProvider` (frame timing), `StatsProvider` (token/usage statistics), `AppStateProvider` (global application state with `onChangeAppState` subscription). All children render within these providers.

#### `FullscreenLayout.tsx` (637 lines)
The primary layout for fullscreen (alt-screen) mode. Divides the terminal into three zones:

- **Scrollable Area** (top, flexGrow): Contains the `ScrollBox` with messages, transcript content, and overlay content (like permission requests). Uses `ScrollChromeContext` to coordinate sticky headers and navigation pills.
- **Bottom Slot** (fixed height): Contains the spinner, prompt input, and permission prompts — always visible.
- **Bottom Float**: Absolute-positioned content anchored at the bottom-right (e.g., the companion speech bubble).
- **Modal Pane**: Absolute-positioned bottom-anchored pane with a `▔` divider, rendering over both scrollable and bottom areas (used by slash-command dialogs, MCP settings). Provides `ModalContext` for nested `Pane`/`Dialog` components.
- **Sticky Tracker**: Manages the "N new messages" pill and sticky user-prompt header. Uses `useSyncExternalStore` on `ScrollBox` for zero-re-render scroll detection.
- **Pill Visibility**: Computed from `dividerYRef` (scrollHeight at snapshot) — pill shows when viewport bottom hasn't reached the unseen-divider position. Supports "Jump to bottom" (count=0) and "N new messages" (count>0) states.

#### `VirtualMessageList.tsx` (1082 lines)
High-performance virtual scrolling for message history. Only renders messages within the visible viewport + overscan.

- **`useVirtualScroll` Integration**: Computes the range of visible message indices based on `scrollTop`, `viewportHeight`, and item heights (measured or estimated).
- **Height Cache**: Stores measured heights per message. Height changes (e.g., expanding a collapsed tool output) invalidate the cache entry, triggering a re-measure on the next render.
- **Search Integration**: Maintains `JumpHandle` interface for transcript search: `setSearchQuery(q)`, `nextMatch()`, `prevMatch()`, `warmSearchIndex()`, `disarmSearch()`. Uses `renderableSearchText()` for per-message text extraction, cached via `WeakMap<Message, string>`.
- **Sticky Prompt Header**: When the user scrolls up past their own prompt, a sticky header shows the prompt text (truncated to `STICKY_TEXT_CAP` = 500 chars). Clicking the header scrolls back to the position. Clicking dismisses the pill.
- **Navigation**: `n`/`p` keys cycle through navigable messages (Assistant + User). `j`/`k`/`PgUp`/`PgDn`/`gg`/`G` for modal scrolling. Integrates with `ScrollChromeContext.setStickyPrompt`.
- **Cold Start**: When `ScrollBox` hasn't laid out yet (`viewportHeight=0`), mounts `COLD_START_COUNT` (30) items.
- **Slide Step**: Mounts at most `SLIDE_STEP` (25) new items per React commit to bound sync render time (~1.5ms per MessageRow).
- **Overscan**: `OVERSCAN_ROWS = 80` rows above and below the viewport. Scroll quantum = `OVERSCAN_ROWS >> 1 = 40` — React only re-renders when the scrollTop crosses quantum boundaries.

#### `Messages.tsx` (834 lines)
Main message list container. Orchestrates the rendering pipeline from raw message arrays to UI.

- **Message Preprocessing**: Normalizes messages via `normalizeMessages()`, applies `reorderMessagesInUI()`, filters out empty/invisible messages, applies `applyGrouping()` (tool use grouping), collapses `readSearch` groups, collapses background bash notifications, collapses hook summaries, collapses teammate shutdowns.
- **Message Lookups**: Builds `messageLookups` (tool use IDs → messages, child → parent maps) for efficient cross-referencing during render.
- **Unseen Divider**: Manages the "N new messages" divider — computes which messages appeared after the user scrolled up.
- **Logo Header**: Memoized `<LogoV2>` + `<StatusNotices>` rendered at the top of the message list in main-screen mode.
- **Streaming State**: Tracks streaming thinking (`StreamingThinking`), streaming tool uses, in-progress tool use IDs, progress messages.
- **Verbose Toggle**: Per-message verbose mode (Alt-v) — shows expanded tool inputs/outputs.
- **Performance**: Memoizes individual message renders via `React.memo` and stable key derivation. The `OffscreenFreeze` component wraps off-screen messages to prevent Ink from painting their cells.

#### `Message.tsx` (627 lines)
The message dispatch point — routes each normalized message to the appropriate renderer component.

**Message type → Component mapping:**
| Message Type | Component |
|---|---|
| User text | `UserTextMessage` |
| User image | `UserImageMessage` |
| User bash input/output | `UserBashInputMessage` / `UserBashOutputMessage` |
| User command | `UserCommandMessage` |
| User prompt | `UserPromptMessage` |
| User memory input | `UserMemoryInputMessage` |
| User channel | `UserChannelMessage` |
| User teammate | `UserTeammateMessage` |
| User agent notification | `UserAgentNotificationMessage` |
| User resource update | `UserResourceUpdateMessage` |
| User plan | `UserPlanMessage` |
| Assistant text | `AssistantTextMessage` |
| Assistant thinking | `AssistantThinkingMessage` |
| Assistant redacted thinking | `AssistantRedactedThinkingMessage` |
| Assistant tool use | `AssistantToolUseMessage` |
| Attachment | `AttachmentMessage` |
| System text | `SystemTextMessage` |
| System API error | `SystemAPIErrorMessage` |
| Advisor | `AdvisorMessage` |
| Compact boundary | `CompactBoundaryMessage` |
| Collapsed read/search | `CollapsedReadSearchContent` |
| Grouped tool uses | `GroupedToolUseContent` |
| Shutdown | `ShutdownMessage` |
| Plan approval | `PlanApprovalMessage` |
| Rate limit | `RateLimitMessage` |
| Task assignment | `TaskAssignmentMessage` |
| Hook progress | `HookProgressMessage` |

Props passed: `message`, `lookups`, `tools`, `commands`, `verbose`, `inProgressToolUseIDs`, `progressMessagesForMessage`, `shouldAnimate`, `shouldShowDot`, `style?`, `width`, `isTranscriptMode`, `isStatic`, `onOpenRateLimitOptions`, `isActiveCollapsedGroup`, `isUserContinuation`, `lastThinkingBlockId`, `latestBashOutputUUID`.

#### `MessageRow.tsx` (383 lines)
Message row wrapper — provides consistent spacing (margin), context-dependent dot indicator, and the "compact summary" rendering when `shouldShowDot` is true. Links messages to their tool results via `ExpandShellOutputContext`.

#### `MessageSelector.tsx` (831 lines)
Message restoration picker — allows the user to restore or summarize past messages. Uses `<Select>` for the message list. Features:
- **Restore Options**: `both` (conversation + code), `conversation` (just messages), `code` (just file changes), `summarize` (create compact summary), `summarize_up_to` (compact up to this point), `nevermind` (cancel).
- **File History Integration**: Shows file change counts and line diff stats per message when `fileHistory` is enabled.
- **Diff Stats**: `fileHistoryGetDiffStats()` returns `{ additions, deletions, files }` per restore target.
- **Pre-selection**: Supports `preselectedMessage` for skipping the pick list and going straight to confirm.

#### `MessageResponse.tsx` (78 lines)
Tree-indent wrapper for assistant/tool output lines — not copy-on-select (that lives in `useCopyOnSelect` / Ink selection).

**Props:** `children`, optional `height` (fixed row height skips `Ratchet` offscreen lock).

**Behavior:**
- Renders a row: dim `⎿` prefix (`NoSelect fromLeftEdge`) + flex-growing content box.
- **Nesting guard:** `MessageResponseContext` — nested instances return `children` only (avoids stacked `⎿` for multi-line tool output).
- **Offscreen lock:** When `height` is unset, wraps in `<Ratchet lock="offscreen">` so Ink skips painting off-screen continuation lines.

#### `MessageModel.tsx` (43 lines)
Displays the model name used for a message (e.g., "Claude 3.5 Sonnet"). Rendered inline with the message header.

#### `MessageTimestamp.tsx`
Renders a relative timestamp for messages (e.g., "2 min ago", "yesterday").

### 1.2 Input Components

#### `TextInput.tsx` (124 lines)
User-facing text input with voice-mode waveform cursor. Wraps `useTextInput` hook. Adds:
- **Voice Waveform Cursor**: When voice mode is active and the terminal is focused, replaces the standard cursor with an animated block-character waveform (`▁▂▃▄▅▆▇█`) driven by audio level data from `useVoiceState`.
- **Voice Recording Status**: Shows recording state, smoothed audio levels (EMA with `SMOOTH = 0.7`), and silence detection (grey cursor when below `SILENCE_THRESHOLD = 0.15`).
- **Text Highlights**: Renders `highlights` (search match positions, syntax coloring).

#### `BaseTextInput.tsx` (136 lines)
Core text input component — renders the input field with cursor, ghost text, highlighting, and paste indicator. Delegates input handling to `useTextInput`.

#### `VimTextInput.tsx` (140 lines)
Vim-enabled text input wrapper. Uses `useVimInput` hook. Renders the current vim mode indicator (INSERT/NORMAL/VISUAL) and passes filtered input through vim's state machine.

#### `ScrollKeybindingHandler.tsx` (1012 lines)
Keyboard and mouse wheel scrolling handler — the most complex scroll control in the system.

- **Mouse Wheel Acceleration**: Implements an exponential decay curve for smooth scrolling. Detects encoder bounce (spurious reverse ticks on worn mice) and engages a different decay profile for physical wheels vs trackpads. Respects `CLAUDE_CODE_SCROLL_SPEED` env var for baseline multiplier.
- **Native Terminal Path** (`WHEEL_ACCEL_WINDOW_MS = 40`, `WHEEL_ACCEL_STEP = 0.3`, `WHEEL_ACCEL_MAX = 6`): Linear ramp for events within the window, resets after idle.
- **xterm.js Path**: Separate exponential decay curve compensating for lower event rate (~30/sec vs ~3-5 events/notch in native terminals). Burst detection with gap-dependent caps tuned to VS Code event patterns.
- **Keyboard Scrolling**: j/k arrows, Ctrl+D/U (half-page), Ctrl+B/F (full-page), PgUp/PgDn, gg/G (top/bottom in modal mode), Home/End.
- **Selection Integration**: Uses `useSelection` hook for mouse selection — `startSelection` on mouse-down, `extendSelection` on drag, `getSelectedText` + `copyToClipboard` on release. Alt+drag for word selection. Supports drag-to-scroll (dragging past the viewport edge scrolls and extends the selection).
- **Search Integration**: `n`/`N` for navigating search matches (calls `JumpHandle.nextMatch()`/`prevMatch()`).
- **iTerm2 Progress Integration**: Sets OSC 9;4 progress while scrolling to show a scroll position indicator in supported terminals.

### 1.3 Navigation & Selection

#### `Stats.tsx` (1228 lines)
Usage statistics dashboard — the `/stats` command output. Features:
- **Tabs** (`Tabs` design system): Token usage, model usage, time, requests, thoughts, files, tools.
- **Date Range Toggle**: Switches between 7d, 30d, all-time. Uses `aggregateClaudeCodeStatsForRange()`.
- **ASCII Charts**: Token usage graph rendered as ASCII art via `asciichart` library. Model distribution as horizontal bar chart.
- **Heatmap**: Activity heatmap (GitHub-style) generated via `generateHeatmap()`.
- **Peak Day**: Shows the highest-usage day with model token breakdown.
- **Keybindings**: j/k for navigation, Tab/Shift+Tab for tab switching, r to toggle date range.
- **Copy**: Supports `C` / `y` to copy the entire stats display as ANSI to clipboard.

#### `LogSelector.tsx` (1575 lines)
Session resume dialog — shown by `/resume`. Features:
- **Search**: Full-text search via Fuse.js across log metadata (titles, paths, branches).
- **Agentic Search** (`onAgenticSearch`): AI-powered session discovery — sends session metadata to a Haiku model for semantic matching (finds sessions by describing what you were doing).
- **Tree Structure**: Sessions organized in a tree by project → git branch → workspace → timestamp. Uses `TreeSelect` component.
- **Tag Tabs**: Filter by: All sessions, This project, This branch, Recent (within 24h), Starred.
- **Title Editing**: Rename sessions via TextInput + `saveCustomTitle()`. Custom titles persist in session storage.
- **Session Preview**: Shows session metadata (duration, message count, first user message, model) in a right pane.
- **Pagination**: `onLoadMore(count)` for lazy loading additional sessions.
- **Exit**: `onCancel()` / `onSelect()` callbacks.

#### `Feedback.tsx` (592 lines)
Bug report / feedback submission dialog. Multi-step flow:
1. **User Input**: Description text area.
2. **Consent Screen**: Shows what will be uploaded (messages, git state, errors, platform info). GitHub issue link generation with pre-filled body.
3. **Submitting**: Sends feedback via Haiku classification → GitHub issue creation or internal logging.
- Gathers: `latestAssistantMessageId`, `message_count`, `datetime`, `description`, `platform`, `gitState`, `errors`, `transcript` (latest messages, capped).
- **Privacy**: Respects `isEssentialTrafficOnly()` — skips feedback collection for privacy-sensitive deployments.

#### `Markdown.tsx` (236 lines)
Streaming Markdown renderer for assistant text responses. Converts Markdown to Ink components:
- **Code Blocks**: Fenced code blocks (` ``` `) render as `HighlightedCode` with syntax highlighting.
- **Tables**: GFM tables render as `MarkdownTable`.
- **Inline Code**: Backtick-quoted text.
- **Headings**: Rendered with bold/underline styling.
- **Lists**: Ordered and unordered lists.
- **Links**: Rendered as clickable `Link` elements with OSC 8 hyperlinks.
- **Bold/Italic**: Rendered via Ink `Text` styling.

#### `MarkdownTable.tsx` (322 lines)
GitHub-Flavored Markdown table renderer for terminal. Renders bordered tables with proper column alignment, row separators, and text wrapping.

#### `HighlightedCode.tsx` (190 lines)
Syntax-highlighted code block renderer. Uses `highlight.js` for language detection and token coloring. Renders as a bordered box with line numbers and theme-appropriate colors.

#### `ConsoleOAuthFlow.tsx` (631 lines)
OAuth 2.0 authentication flow in the terminal. Renders the login URL with instructions, polls for token callback, shows progress spinner. Uses `checkAndRefreshOAuthTokenIfNeeded()`.

#### `Onboarding.tsx` (244 lines)
First-run onboarding/questionnaire dialog. Gathers user preferences (language, editor, theme). Uses multi-step wizard pattern.

#### `ThemePicker.tsx` (333 lines)
Theme selection dialog. Shows theme previews with sample code blocks, color swatches, and background/font options. Uses `<Select>` with visual preview items. Supports: built-in themes, custom themes, system-follow (`followSystem: true`).

#### `ModelPicker.tsx` (448 lines)
Model/API picker dialog. Lists available Claude models with descriptions, context windows, capabilities, and pricing. Shows current model with checkmark. Supports: Claude 3.5 Sonnet, Claude 3 Opus, Claude 3 Haiku, and future models.

#### `OutputStylePicker.tsx` (112 lines)
Output style selection — switches between default, compact, and other output styles.

#### `LanguagePicker.tsx` (86 lines)
Language/thinking output preference picker.

#### `EffortIndicator.ts` (42 lines) & `EffortCallout.tsx` (265 lines)
Effort estimation components — shows Claude's confidence/effort level for a given task. Visualized as a progress bar with color coding.

### 1.4 Auto-Update

#### `AutoUpdater.tsx` + `AutoUpdaterWrapper.tsx` (91 lines)
Auto-update notification system. Checks for new versions, shows update available notification (non-blocking), handles download progress in `NativeAutoUpdater.tsx`.

#### `NativeAutoUpdater.tsx` (193 lines)
Native platform auto-updater integration (macOS Sparkle, Windows squirrel, Linux AppImage).

#### `PackageManagerAutoUpdater.tsx` (104 lines)
Package-manager-based update path (npm, brew, etc.).

### 1.5 Status & Misc

#### `StatusLine.tsx` (324 lines)
Bottom status bar — shows: model name, session duration, token count, cost estimate, connection status, background task count, keyboard shortcut hints. Highly optimized for minimal re-renders (subscribes to specific state slices).

#### `AgentProgressLine.tsx`
Shows progress of running agent/background tasks — formatted as a compact one-line indicator.

#### `AutoModeOptInDialog.tsx`
Auto-mode opt-in prompt — shown when the user first triggers a tool that would benefit from auto-approve.

#### `CompactSummary.tsx`
Compact transcript summary renderer — shows a condensed view of a session (message count, key actions, duration).

#### `ContextSuggestions.tsx`
Context-aware suggestion chips — shows relevant commands/shortcuts based on current state.

#### `ContextVisualization.tsx`
Visual tree of the current context window composition (system prompt, messages, tools, files, memory).

#### `CtrlOToExpand.tsx`
Hint to press Ctrl+O to expand truncated content.

---

## 2. Dialog Components

| File | Description |
|------|-------------|
| `BridgeDialog.tsx` (401 lines) | Bridge/remote connection dialog — setup for remote sessions. Handles WebSocket URL configuration, authentication, connection status. |
| `BypassPermissionsModeDialog.tsx` | Bypass permissions mode toggle — confirms intention to temporarily bypass all permission checks. |
| `ChannelDowngradeDialog.tsx` | Channel downgrade warning — shown when downgrading from Team to Pro. |
| `ClaudeMdExternalIncludesDialog.tsx` | External CLAUDE.md includes review — shows external markdown files being included and asks for confirmation. |
| `CostThresholdDialog.tsx` | Cost threshold warning — shown when estimated session cost exceeds a configured limit. |
| `IdleReturnDialog.tsx` (118 lines) | Idle session return prompt — shown when returning to a session that has been idle for a while. |
| `InvalidConfigDialog.tsx` | Invalid configuration error display. |
| `InvalidSettingsDialog.tsx` | Invalid settings error display with remediation suggestions. |
| `ManagedSettingsSecurityDialog/` | Managed (team/organization) settings security review. |
| `TeleportError.tsx` (189 lines) | Teleport session resume error — shows error details and recovery options. |
| `TeleportProgress.tsx` (140 lines) | Teleport session resume progress — progress bar with step indicators. |
| `TeleportRepoMismatchDialog.tsx` (104 lines) | Repository mismatch warning during teleport resume (session was in a different repo). |
| `WorktreeExitDialog.tsx` (231 lines) | Git worktree exit confirmation — prompts before removing a temporary worktree. |

### Additional Dialogs
- `AwsAuthStatusBox.tsx` — AWS authentication status display
- `ApproveApiKey.tsx` — API key approval prompt
- `DevChannelsDialog.tsx` — Development channel switcher
- `ExportDialog.tsx` — Transcript export dialog (Markdown, HTML, JSON)
- `GlobalSearchDialog.tsx` — Global fuzzy search (files, sessions, commands)
- `HistorySearchDialog.tsx` — Command history search with fuzzy matching
- `KeybindingWarnings.tsx` — Keybinding conflict warnings
- `MCPServerApprovalDialog.tsx` — MCP server trust approval
- `MCPServerDesktopImportDialog.tsx` — Desktop app MCP server import
- `MCPServerDialogCopy.tsx` — MCP server configuration copy/share
- `MCPServerMultiselectDialog.tsx` — Multi-select for enabling/disabling MCP servers
- `PrBadge.tsx` — Pull request status badge
- `PressEnterToContinue.tsx` — Pause/prompt for Enter
- `QuickOpenDialog.tsx` — Quick file/command opener (Ctrl+P style)
- `RemoteCallout.tsx` — Remote session connection callout
- `RemoteEnvironmentDialog.tsx` — Remote environment settings
- `ResumeTask.tsx` — Task resume confirmation
- `SessionPreview.tsx` — Session metadata preview
- `ShowInIDEPrompt.tsx` — Prompt to open file in IDE
- `TeleportResumeWrapper.tsx` — Teleport resume orchestration wrapper
- `TeleportStash.tsx` — Stash management during teleport
- `TokenWarning.tsx` — Token limit warning
- `ValidationErrorsList.tsx` — Form validation error list
- `WorkflowMultiselectDialog.tsx` — Workflow/task multi-select dialog
- `DesktopHandoff.tsx` — Desktop app handoff prompt
- `FastIcon.tsx` — Fast mode indicator icon
- `ThinkingToggle.tsx` — Thinking visibility toggle
- `SandboxViolationExpandedView.tsx` — Expanded sandbox violation details
- `OffscreenFreeze.tsx` — Offscreen rendering freeze (prevents Ink from painting)
- `SessionBackgroundHint.tsx` — Background session hint
- `SentryErrorBoundary.ts` — Sentry error boundary wrapper
- `DevBar.tsx` — Developer debug bar
- `ExitFlow.tsx` — Exit/quit flow dialog

---

## 3. Message Components (`messages/`) — 34 Files

### 3.1 Assistant Message Types

| Component | Description |
|---|---|
| `AssistantTextMessage.tsx` | Main assistant text response — renders markdown, manages thinking toggle. Handles: streaming content, truncation for long responses, code block expansion. |
| `AssistantThinkingMessage.tsx` | Claude's internal thinking/reasoning display. Shows thinking text with different styling (dimmed, italic). Controls visibility via global/claude.md thinking settings. |
| `AssistantRedactedThinkingMessage.tsx` | Redacted thinking display — shown when thinking was flagged for safety and redacted. |
| `AssistantToolUseMessage.tsx` | Tool call display — shows tool name, input summary, and result. Expands to show full JSON input/output. Integrates with `ToolUseLoader` for streaming tool results. Handles: FileEdit, FileWrite, Bash, Grep, Glob, WebFetch, NotebookEdit, AskUserQuestion, Task, EnterPlanMode, ExitPlanMode, Sandbox. |
| `AdvisorMessage.tsx` | Claude's internal advisor/reflection — shown as a dimmed, collapsible block. Handles: structured advisor output with sections. |

### 3.2 User Message Types

| Component | Description |
|---|---|
| `UserTextMessage.tsx` | Plain text user message. |
| `UserImageMessage.tsx` | User image attachment — shows thumbnail/placeholder with image dimensions. Renders via `ClickableImageRef`. |
| `UserBashInputMessage.tsx` | User shell command input display. |
| `UserBashOutputMessage.tsx` | User shell command output — renders stdout/stderr with optional ANSI formatting. Auto-expands the latest output. |
| `UserCommandMessage.tsx` | User slash-command display. |
| `UserPromptMessage.tsx` | User prompt — the main input message. |
| `UserMemoryInputMessage.tsx` | Memory/context injection message — shows what was added to memory. |
| `UserChannelMessage.tsx` | Channel/user notification display. |
| `UserLocalCommandOutputMessage.tsx` | Local command execution output. |
| `UserTeammateMessage.tsx` | Teammate/sub-agent message — shows agent identity and status. |
| `UserAgentNotificationMessage.tsx` | Agent lifecycle notification (spawned, completed, failed). |
| `UserResourceUpdateMessage.tsx` | Resource/file change notification. |
| `UserPlanMessage.tsx` | Plan mode message — shows the task plan outline. |
| `TaskAssignmentMessage.tsx` | Task delegation display — which agent is working on what. |

### 3.3 System Message Types

| Component | Description |
|---|---|
| `SystemTextMessage.tsx` (827 lines) | System text/meta messages — the most complex system message renderer. Handles: tool approval states, compact mode, session boundaries, model switches, context window warnings, hook execution results. |
| `SystemAPIErrorMessage.tsx` | API error display with retry options and error code explanation. |
| `RateLimitMessage.tsx` | Rate limit notification with retry-after countdown. |
| `ShutdownMessage.tsx` | Session shutdown/exit message. |
| `HookProgressMessage.tsx` | Hook execution progress — shows running hooks with spinner and status. |
| `PlanApprovalMessage.tsx` | Plan approval request — shows the plan and asks for confirmation. |

### 3.4 Content Components

| Component | Description |
|---|---|
| `AttachmentMessage.tsx` (531 lines) | File attachment display — renders file icon, name, size, and preview. Supports image previews, text file snippets. |
| `CollapsedReadSearchContent.tsx` (484 lines) | Collapsed group of read/search operations — summarizes multiple file reads or searches into a compact view with file count and match count. |
| `CompactBoundaryMessage.tsx` | Compact session boundary — divider between compacted/summarized and current conversation. |
| `GroupedToolUseContent.tsx` | Groups of related tool uses (e.g., sequential file reads) with expand/collapse toggle. Shows tool count and aggregate timing. |
| `HighlightedThinkingText.tsx` | Thinking text with search match highlighting (yellow current match, inverse all matches). |
| `teamMemCollapsed.tsx` | Collapsed teammate memory display. |
| `teamMemSaved.ts` | Teammate memory save utility — types and formatting for saved memories. |
| `nullRenderingAttachments.ts` | Null-rendering attachment detection — identifies attachments that should not produce visible UI (e.g., empty images, zero-length text). |

### 3.5 `UserToolResultMessage/` (8 files)

Directory with specialized renderers for different tool result types. Each tool's output has unique display needs — file diffs, terminal output, search results, structured data.

| File | Tool Result Type |
|---|---|
| `UserToolResultMessage.tsx` | Main dispatcher — routes to specific renderers |
| `FileEditResultMessage.tsx` | File edit diff display |
| `FileWriteResultMessage.tsx` | File write/create display |
| `BashResultMessage.tsx` | Shell command output (with ANSI support) |
| `GrepResultMessage.tsx` | Search result listing |
| `GlobResultMessage.tsx` | File pattern match listing |
| `WebFetchResultMessage.tsx` | Web content display |
| `NotebookEditResultMessage.tsx` | Jupyter notebook cell display |

### 3.6 Shell & Tool Display

- `FileEditToolDiff.tsx` — Inline file edit diff display with +/- markers
- `FileEditToolUpdatedMessage.tsx` — "File updated" confirmation
- `FileEditToolUseRejectedMessage.tsx` — "Edit rejected" message
- `FallbackToolUseErrorMessage.tsx` (116 lines) — Default tool error renderer when a tool has no custom `renderToolUseErrorMessage`. Parses `<tool_use_error>` tags, strips sandbox violation tags, maps `InputValidationError` to "Invalid tool parameters" when not verbose. Truncates to `MAX_RENDERED_LINES = 10` with "+N lines" hint and configurable `ctrl+o` expand shortcut via `useShortcutDisplay`.
- `FallbackToolUseRejectedMessage.tsx` — Generic tool rejection display
- `ToolUseLoader.tsx` — Animated tool call progress indicator
- `NotebookEditToolUseRejectedMessage.tsx` — Notebook edit rejection
- `InterruptedByUser.tsx` — "Interrupted by user" indicator
- `BashModeProgress.tsx` — Bash mode execution progress
- `CoordinatorAgentStatus.tsx` — Coordinator agent status display
- `DiagnosticsDisplay.tsx` — LSP diagnostic display (errors, warnings, hints)
- `MemoryUsageIndicator.tsx` — RAM/CPU usage gauge
- `SearchBox.tsx` — Search input with clear button
- `ConfigurableShortcutHint.tsx` (57 lines) — Resolves user keybindings via `useShortcutDisplay(action, context, fallback)` then renders `KeyboardShortcutHint`. Used wherever hints must reflect `/keybindings` overrides (Dialog footers, expand hints).
- `FilePathLink.tsx` — Clickable file path (opens in IDE or $EDITOR)
- `ClickableImageRef.tsx` — Clickable image reference (opens in browser/OS viewer)
- `Spinner.tsx` + `Spinner/` — Animated terminal spinner (dots, lines, custom frames)
- `TagTabs.tsx` — Tab-style filter UI
- `TeammateViewHeader.tsx` — Teammate view header with agent identity

---

## 4. Permission Components (`permissions/`) — 30+ Files

### 4.1 Core Permission UI

| Component | Description |
|---|---|
| `PermissionDialog.tsx` | Main permission dialog orchestrator — routes to specific permission request components based on the tool being invoked. |
| `PermissionPrompt.tsx` (335 lines) | Permission prompt presentation — shows the tool name, arguments, and action buttons (Allow/Deny/Always). |
| `PermissionRequest.tsx` (217 lines) | Tool → component dispatcher (`permissionComponentForTool` switch). Renders the matching `*PermissionRequest` UI; decision persistence lives in `useCanUseTool` / handlers, not here. Registers `confirm:no` timeout via `useNotifyAfterTimeout`. |
| `PermissionExplanation.tsx` | Explanation of what the tool will do — security implications, data access, scope. |
| `PermissionRequestTitle.tsx` | Title bar for permission prompt — shows tool icon, name, security level badge. |
| `PermissionRuleExplanation.tsx` | Explanation of existing permission rules that match this request. |
| `FallbackPermissionRequest.tsx` (333 lines) | Generic/unknown tool permission prompt — used when no specialized component exists for a tool. |
| `PermissionDecisionDebugInfo.tsx` (458 lines) | Debug overlay showing why a permission decision was made (matching rules, scopes, conditions). |

### 4.2 Tool-Specific Permission Requests

| Component | Tool |
|---|---|
| `BashPermissionRequest/` (2 files) | Shell command permission — shows the command, working directory, and security warnings. |
| `FileEditPermissionRequest.tsx` | File edit permission — shows diff preview of changes. |
| `FileWritePermissionRequest/` (2 files) | File write permission — shows file path and content preview. |
| `FilePermissionDialog/` (5 files) | File permission dialog — full dialog with file list, diff preview, and bulk approve/deny. |
| `FilesystemPermissionRequest.tsx` | Filesystem operation permission (read, write, list). |
| `NotebookEditPermissionRequest/` (2 files) | Jupyter notebook edit permission. |
| `PowerShellPermissionRequest/` (2 files) | PowerShell command permission. |
| `SedEditPermissionRequest.tsx` | Sed edit permission. |
| `SkillPermissionRequest.tsx` | Skill invocation permission. |
| `WebFetchPermissionRequest.tsx` | Web fetch permission — shows URL and purpose. |
| `ComputerUseApproval/` (1 file) | Computer use/vision permission. |
| `AskUserQuestionPermissionRequest/` (7 files) | Ask-user-question tool permission — specialized because it involves Claude asking the user. |
| `EnterPlanModePermissionRequest.tsx` | Enter plan mode permission. |
| `ExitPlanModePermissionRequest.tsx` (768 lines) | Exit plan mode permission — the most complex, coordinating the plan→execution transition. |
| `SandboxPermissionRequest.tsx` | Sandbox execution permission. |

### 4.3 Permission Rules (`rules/` — 8 files)

| Component | Description |
|---|---|
| `PermissionRuleList.tsx` (1175 lines) | Master permission rules editor — list all rules, add/edit/remove rules, reorder rules. The most complex permission UI component. |
| `AddPermissionRules.tsx` | Add new permission rule dialog. |
| `PermissionRuleInput.tsx` | Permission rule input form — tool selector, scope editor, action picker. |
| `PermissionRuleDescription.tsx` | Human-readable permission rule description. |
| `AddWorkspaceDirectory.tsx` | Add workspace directory to permission scope. |
| `RemoveWorkspaceDirectory.tsx` | Remove workspace directory from scope. |
| `WorkspaceTab.tsx` | Workspace tab in permission rules — grouped by workspace. |
| `RecentDenialsTab.tsx` | Recent denials tab — shows recently denied requests with option to create rules. |

### 4.4 Permission Utilities

- `shellPermissionHelpers.tsx` — Shell command safety analysis (dangerous commands, scope analysis)
- `useShellPermissionFeedback.ts` — Hook for shell permission feedback animations
- `WorkerBadge.tsx` — Worker/sandbox permission badge
- `WorkerPendingPermission.tsx` — Pending permission indicator for background workers

---

## 5. Feature Components

### 5.1 Agents (`agents/` — 14 files)

| Component | Description |
|---|---|
| `AgentsMenu.tsx` (800 lines) | Main agents management interface — list, create, edit, delete, start agents. Tabs: My Agents, Team Agents, Templates. |
| `AgentsList.tsx` | Agent list with status indicators (idle, running, error). |
| `AgentDetail.tsx` | Agent detail view — configuration, permissions, recent activity. |
| `AgentEditor.tsx` | Agent configuration editor — system prompt, model, tools, permissions, schedule. |
| `agentFileUtils.ts` | Agent file management — read/write agent definitions, validation. |
| `AgentNavigationFooter.tsx` | Navigation footer with keyboard shortcuts. |
| `ColorPicker.tsx` | Agent color picker (for visual identification). |
| `generateAgent.ts` | Agent generation/creation logic. |
| `ModelSelector.tsx` | Model picker for agent configuration. |
| `new-agent-creation/` | New agent creation flow (multi-step wizard). |
| `ToolSelector.tsx` | Tool picker — select which tools an agent can access. |
| `types.ts` | Agent type definitions (`AgentDefinition`, `AgentState`). |
| `utils.ts` | Agent utility functions. |
| `validateAgent.ts` | Agent configuration validation. |

### 5.2 MCP (`mcp/` — 13 files)

| Component | Description |
|---|---|
| `ElicitationDialog.tsx` (1169 lines) | MCP server discovery and setup dialog — the largest MCP component. Handles: server URL input, capability inspection, trust configuration, tool listing, testing. |
| `MCPListPanel.tsx` | MCP server list — running servers with status, tools count, resource count. |
| `MCPSettings.tsx` | MCP settings editor — JSON config with validation, add/remove servers. |
| `MCPAgentServerMenu.tsx` | Agent-specific MCP server management. |
| `MCPRemoteServerMenu.tsx` | Remote MCP server configuration (SSE/WebSocket transport). |
| `MCPStdioServerMenu.tsx` | Local MCP server configuration (stdio transport — command + args). |
| `MCPToolDetailView.tsx` | Individual MCP tool detail — input schema, description, examples. |
| `MCPToolListView.tsx` | List of MCP tools with enable/disable toggles. |
| `CapabilitiesSection.tsx` | Server capabilities display — resources, tools, prompts, logging. |
| `MCPReconnect.tsx` | Server reconnection UI. |
| `McpParsingWarnings.tsx` | MCP configuration parsing warnings. |
| `index.ts` | MCP module exports. |
| `utils/` | MCP utility functions. |

### 5.3 Design System (`design-system/` — 16 files)

High-import primitives (66+ importers each for `Dialog`, `Byline`, `KeyboardShortcutHint`):

#### `Dialog.tsx` (138 lines)
Modal shell built on `Pane` + `useExitOnCtrlCDWithKeybindings`.

**Props:** `title`, optional `subtitle`, `children`, `onCancel`, `color` (default `"permission"`), `hideInputGuide`, `hideBorder`, `inputGuide(exitState)`, `isCancelActive` (default `true` — set `false` while embedded `TextInput` is focused so Esc/Ctrl+C reach the field).

**Keybindings:** `confirm:no` → `onCancel` (context `"Confirmation"`, gated by `isCancelActive`). Built-in footer shows Enter confirm + `ConfigurableShortcutHint` for Esc cancel; pending double Ctrl+C/D shows "Press X again to exit".

#### `Byline.tsx` (77 lines)
Joins child hint nodes with middot separators (` · `). Filters null/false children; renders nothing when empty. Typical pattern: wrap multiple `KeyboardShortcutHint` / `ConfigurableShortcutHint` in dim `Text`.

#### `KeyboardShortcutHint.tsx` (81 lines)
**Props:** `shortcut`, `action` (description text), optional `parens`, `bold`. Renders `"shortcut to action"`, `"shortcut action"` (bold shortcut), or `"(shortcut to action)"`.

#### `ConfigurableShortcutHint.tsx` (57 lines)
See §3.6 — wraps `KeyboardShortcutHint` with `useShortcutDisplay`.

#### `Pane.tsx` (89 lines)
Bordered flex-column panel used by `Dialog` and settings screens. Optional `title` header row, scrollable body, `color` theme key for border.

#### `Tabs.tsx` (154 lines)
Horizontal tab headers with `selectedIndex` / `onSelect`. Arrow keys and Tab cycle tabs; content area renders active tab child only.

#### `Divider.tsx` (48 lines)
Full-width `─` rule with optional centered `label`.

#### Other design-system files

| Component | Description |
|---|---|
| `FuzzyPicker.tsx` | Fuzzy search picker — `useSearchInput` + Fuse.js filtered list. |
| `ListItem.tsx` | Selectable list row — selected/hover styles, keyboard focus. |
| `LoadingState.tsx` | Spinner + optional message. |
| `ProgressBar.tsx` | `████░░░░` bar with percentage label. |
| `StatusIcon.tsx` | Colored status dot (ok/warning/error). |
| `Ratchet.tsx` | Offscreen render lock / incremental height control (used by `MessageResponse`). |
| `color.ts` | Resolve theme semantic keys → ANSI color strings. |
| `ThemedBox.tsx` | Box with theme background/border from semantic `color` prop. |
| `ThemedText.tsx` | Text with theme foreground; optional hover color. |
| `ThemeProvider.tsx` | Provides `Theme` context to descendants. |

### 5.4 Custom Select (`CustomSelect/` — 10 files)

A complete select/dropdown framework for terminal UIs:

| File | Description |
|---|---|
| `select.tsx` | Main select component — renders list of options with keyboard navigation (j/k arrows, Enter to select, Esc to cancel, / to search). Supports: single-select, headers, separators, custom renderers, disabled items. |
| `SelectMulti.tsx` | Multi-select variant — Space to toggle, Enter to confirm. Shows selected count. |
| `select-option.tsx` | Individual select option — renders label, metadata, icon, keyboard shortcut hint. |
| `select-input-option.tsx` | Option with embedded text input (for editing values inline). |
| `option-map.ts` | Option registration and ID management. |
| `use-select-state.ts` | Single-select state management — tracks selected index, search query, filtered options. |
| `use-multi-select-state.ts` | Multi-select state management — tracks selected set, toggle logic. |
| `use-select-input.ts` | Select input handling — keyboard events, search, navigation. |
| `use-select-navigation.ts` | Select navigation — j/k, PgUp/PgDn, gg/G, mouse click selection. |
| `index.ts` | Module exports. |

### 5.5 LogoV2 (`LogoV2/` — 15 files)

| Component | Description |
|---|---|
| `LogoV2.tsx` (542 lines) | Main logo display — the Claude character and branding. Shows different states: idle, active, thinking, errors. |
| `WelcomeV2.tsx` (433 lines) | Welcome screen — shown at session start with tips, version info, recent sessions. |
| `Clawd.tsx` | Clawd (Claude mascot) character renderer. |
| `AnimatedClawd.tsx` | Animated Clawd with thinking/eating animations. |
| `AnimatedAsterisk.tsx` | Animated asterisk (the Claude reaction indicator). |
| `CondensedLogo.tsx` | Compact logo for narrow displays. |
| `ChannelsNotice.tsx` | Channels/managed accounts notice. |
| `EmergencyTip.tsx` | Emergency/security tip display. |
| `Feed.tsx` | Activity feed — latest updates, tips, announcements. |
| `FeedColumn.tsx` | Feed column layout. |
| `feedConfigs.tsx` | Feed configuration — what to show and when. |
| `GuestPassesUpsell.tsx` | Guest pass promotion. |
| `Opus1mMergeNotice.tsx` | Model migration notice. |
| `OverageCreditUpsell.tsx` | Credit overage promotion. |
| `VoiceModeNotice.tsx` | Voice mode notification. |

### 5.6 Tasks (`tasks/` — 12 files)

| Component | Description |
|---|---|
| `BackgroundTask.tsx` | Background task indicator — shows task type, progress, duration. |
| `BackgroundTasksDialog.tsx` | Full background tasks list — view all running/completed background tasks. |
| `BackgroundTaskStatus.tsx` | Compact task status pill. |
| `AsyncAgentDetailDialog.tsx` | Agent detail dialog — for viewing agent tasks. |
| `DreamDetailDialog.tsx` | Dream mode detail — background Claude thinking sessions. |
| `InProcessTeammateDetailDialog.tsx` | Teammate task detail — view a sub-agent's conversation and progress. |
| `RemoteSessionDetailDialog.tsx` | Remote session detail — connection status, latency, activity. |
| `RemoteSessionProgress.tsx` | Remote session progress bar. |
| `renderToolActivity.tsx` | Tool activity renderer — shows which tools are currently in use. |
| `ShellDetailDialog.tsx` | Shell session detail — running commands, output, history. |
| `ShellProgress.tsx` | Shell command progress. |
| `taskStatusUtils.tsx` | Task status formatting utilities. |

### 5.7 Diff Viewer (`diff/` — 3 files)

| Component | Description |
|---|---|
| `DiffDialog.tsx` | Full diff dialog — side-by-side or unified view of file changes. |
| `DiffDetailView.tsx` | Detailed diff view — individual hunk display with syntax highlighting. |
| `DiffFileList.tsx` | File list in a diff — shows changed files with +/- counts. |

### 5.8 Additional Components

#### Prompt Input (`PromptInput/`)
- `inputModes.ts` (34 lines) — Bash-mode prefix helpers: `!` prefix/suffix for history serialization (`prependModeCharacterToInput`, `getModeFromInput` → `'bash' | 'prompt'`, `getValueFromInput`, `isInputModeCharacter`)
- `PromptInputFooterSuggestions.tsx` — Suggestion bar below the prompt input

#### Settings (`Settings/`)
Settings-related components

#### Shell (`shell/`)
- `ExpandShellOutputContext.ts` — Context for expanding/collapsing shell output

#### Teams (`teams/`)
Teammate/swarm-related components

#### Memory (`memory/`)
Memory management components

#### Sandbox (`sandbox/`)
Sandbox execution components

#### HelpV2 (`HelpV2/`)
Help system components

#### ClaudeCodeHint (`ClaudeCodeHint/`)
Claude Code contextual hints

#### LspRecommendation (`LspRecommendation/`)
LSP plugin recommendation UI

#### FeedbackSurvey (`FeedbackSurvey/`)
Post-session feedback survey

#### DesktopUpsell (`DesktopUpsell/`)
Desktop app promotion

#### Passes (`Passes/`)
Guest pass management

#### UI (`ui/`)
- `TreeSelect.tsx` — Tree-structured select component (used by LogSelector)

#### grove/ — Grove visualization components

#### wizard/ — Multi-step wizard framework

---

## 6. Context Providers (`context/`) — 9 Files

React context modules wired by `components/App.tsx` and feature components.

#### `context/stats.tsx` (220 lines)
`StatsProvider` / `createStatsStore()` — session metrics (counters, histograms with reservoir sampling, string sets). Persists project stats via `saveCurrentProjectConfig`.

#### `context/notifications.tsx` (240 lines)
`useNotifications()` — adds/removes toast notifications in AppState. Priority queue (`low`/`medium`/`high`/`immediate`), fold merge, invalidation keys, default 8s timeout.

#### `context/voice.tsx` (88 lines)
`VoiceProvider`, `useVoiceState(selector)`, `useSetVoiceState()`, `useGetVoiceState()`. Zustand-style store for `voiceState` (`idle`|`recording`|`processing`), interim transcript, audio levels, errors, and `voiceWarmingUp`.

#### `context/fpsMetrics.tsx` (30 lines)
`FpsMetricsProvider` / `useFpsMetrics()` — exposes Ink frame timing getter to `DevBar`.

#### `context/mailbox.tsx` (38 lines)
`MailboxProvider` / `useMailbox()` — single shared `Mailbox` instance for agent message routing.

#### `context/modalContext.tsx` (57 lines)
`ModalContext`, `useIsInsideModal()`, `useModalOrTerminalSize()`, `useModalScrollRef()` — set by `FullscreenLayout` modal slot for slash-command dialogs.

#### `context/overlayContext.tsx` (151 lines)
`useRegisterOverlay()`, `useIsOverlayActive()`, `useIsModalOverlayActive()` — tracks active overlays in AppState for Escape/cancel coordination; invalidates prev frame on overlay unmount.

#### `context/promptOverlayContext.tsx` (125 lines)
`PromptOverlayProvider`, `useSetPromptOverlay()`, `useSetPromptOverlayDialog()` — portal channel for suggestion menus and floating dialogs above the clipped prompt slot.

#### `context/QueuedMessageContext.tsx` (63 lines)
`QueuedMessageProvider` / `useQueuedMessage()` — marks queued teammate messages with padding width for brief layout.

---

## 7. Supplemental Root Components

#### `StatusNotices.tsx` (55 lines)
Startup notice strip below the logo. Renders active entries from `getActiveNotices()` (config, agent definitions, memory files). Neutral/positive status moved to `/status` (`Status.tsx`).

#### `ClaudeInChromeOnboarding.tsx` (121 lines)
First-run Chrome extension onboarding dialog. Checks `isChromeExtensionInstalled()`, logs analytics, saves global config flag on dismiss.

#### `SkillImprovementSurvey.tsx` (152 lines)
In-session survey when skill-improvement hooks propose updates. Renders skill name, pending updates, numeric response input via `FeedbackSurveyView` patterns.

#### `StructuredDiffList.tsx` (30 lines)
Renders multiple `StructuredPatchHunk` entries via `StructuredDiff`, interspersed with dim `...` ellipsis separators.

---

## 8. Component Architecture Patterns

### Event Handling
- **Capture/Bubble**: Components use a DOM-like event model — `onKeyDownCapture` (capture phase) + `onKeyDown` (bubble phase). The `Dispatcher` walks the DOM tree from root to target (capture) then target to root (bubble).
- **Keybindings System**: `useKeybinding` / `useKeybindings` hooks use a `KeybindingContext` that respects user-customizable keymaps. Components declare keybindings with `key` and `action`; the context resolves the actual keys.
- **Ctrl+CD Exit**: Components that consume Escape use `useExitOnCtrlCD` / `useExitOnCtrlCDWithKeybindings` to ensure Ctrl+C still exits.

### State Management
- **AppState**: Global state via `useAppState(selector)` — a zustand-like immutable state store. Components subscribe to specific slices, avoiding full-tree re-renders on unrelated changes.
- **Context**: Feature-specific context providers (modal, overlay, scroll chrome, prompt overlay) for tight coupling without prop threading.
- **Imperative Handles**: Complex interactive components (ScrollBox, VirtualMessageList, Select) expose `useImperativeHandle` refs for parent control (scroll, search, focus).

### Performance
- **React Compiler**: Most components use the `react/compiler-runtime` (`_c` cache slots) for automatic memoization.
- **OffscreenFreeze**: Components outside the virtual viewport are wrapped in `<OffscreenFreeze>` which marks their DOM nodes as hidden, preventing Ink from rendering their cells.
- **Memo**: Heavy components (LogoV2, StatusNotices, MessageRows) use `React.memo` with stable props to avoid re-renders.
- **StreamingContent**: The `Markdown` component handles streaming content — partial markdown is rendered incrementally and corrected as more text arrives.
