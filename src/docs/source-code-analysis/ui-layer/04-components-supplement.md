# UI Layer: Components Supplement

> Comprehensive analysis of every function, component, type, and export in the PromptInput, Settings, Spinner, sandbox, and shell component directories.

---

## Directory 1: `components/PromptInput/` (21 files)

### 1.1 `PromptInput.tsx` (2339 lines)

The core prompt input component — the most important UI component in the application. It manages text input, keyboard shortcuts, mode switching, history, suggestions, image pasting, and footer navigation.

#### Types

- **`Props`** (lines 124-189): The main component props interface with 36+ properties including debug flags, IDE selection, tool permission context, API key status, commands, agents, loading state, messages, auto-updater callbacks, input state, mode state, stashed prompt state, submission handlers, history search state, help menu state, voice interim range, and more.

#### Exported Components

- **`PromptInput(props: Props): ReactNode`** (lines 194-2297): The main prompt input component. This is a massive 2100+ line component that manages:
  - Modal overlay detection
  - Auto-update state tracking
  - Exit message state
  - Cursor offset tracking and external input detection
  - `insertTextRef` exposure for speech-to-text insertion
  - Footer item visibility logic (tasks, teams, bridge, companion, tmux)
  - Brief mode gap ownership
  - Teammate/agent context derivation
  - Permission mode for viewed teammates
  - History search integration
  - Paste ID tracking
  - Footer selection and navigation (selectFooterItem, navigateFooter)
  - Prompt suggestion integration
  - Text highlight computation (btw triggers, slash commands, token budgets, Slack channels, @mentions, image references, voice interim, ultrathink/ultraplan rainbow, buddy)
  - Stash hint detection
  - Input buffer (undo) initialization
  - History navigation handlers with queued command pop
  - Suggestion state management
  - onSubmit handler with speculation, prompt suggestions, direct messages, agent routing
  - Image paste handling (onImagePaste)
  - Text paste handling (onTextPaste)
  - Keybinding registrations (undo, newline, external editor, stash, model picker, cycle mode, image paste, etc.)
  - Auto mode opt-in dialog flow
  - Quick open / global search
  - Footer navigation keybindings
  - Swarm banner rendering
  - Border color computation (mode-specific, teammate color)
  - Full text input rendering with Vim support

- **`React.memo(PromptInput)`** (line 2338): Memoized default export.

#### Internal Functions

- **`getInitialPasteId(messages: Message[]): number`** (lines 2303-2327): Scans existing messages to find the maximum paste ID used, returning maxId+1 to avoid collisions on --continue/--resume.
- **`buildBorderText(showFastIcon, showFastIconHint, fastModeCooldown): BorderTextOptions | undefined`** (lines 2328-2337): Builds the border text configuration for the fast mode icon display in the prompt border's top-right corner. Returns undefined when fast icon is hidden.

#### Constants

- **`PROMPT_FOOTER_LINES`** = 5 (line 194): Lines reserved for footer, border, and status.
- **`MIN_INPUT_VIEWPORT_LINES`** = 3 (line 195): Minimum visible input lines.

---

### 1.2 `PromptInputFooter.tsx` (191 lines)

The footer bar rendered below the prompt input. Shows suggestions, help menu, or status/footer info.

#### Types

- **`Props`** (lines 26-62): 32 properties including API key status, debug mode, exit message, vim mode, input mode, auto-updater state, suggestions, tool permission context, help menu state, loading state, footer selection states (tasks, teams, bridge, tmux), IDE selection, MCP clients, paste/wrap states, messages, search state.
- **`BridgeStatusProps`** (lines 154-156): Contains `bridgeSelected` boolean.

#### Exported Components

- **`PromptInputFooter(props: Props): ReactNode`** (lines 63-152): Main footer component.
  - Reads terminal size to detect narrow/short displays
  - Computes pill selection state for coordinator task panel
  - In fullscreen, portals suggestion data to overlay context
  - Renders `PromptInputFooterSuggestions` when suggestions exist (inline in non-fullscreen)
  - Renders `PromptInputHelpMenu` when help is open
  - Otherwise renders a row with `PromptInputFooterLeftSide` on the left and `Notifications` on the right
  - Tracks the last assistant message ID for `StatusLine`
  - Conditionally renders `CoordinatorTaskPanel` (ant-only)
- **`memo(PromptInputFooter)`** (line 153): Memoized default export.

#### Internal Components

- **`BridgeStatusIndicator({ bridgeSelected }: BridgeStatusProps): ReactNode`** (lines 157-190): Shows bridge/remote-control connection status as a footer pill. Only renders when BRIDGE_MODE feature is enabled. Shows reconnecting state for implicit configurations, full status for explicit ones.

---

### 1.3 `PromptInputFooterLeftSide.tsx` (517 lines)

The left side of the prompt footer showing mode indicators, keyboard hints, and contextual information.

#### Types

- **`Props`** (lines 52-73): Properties for exit message, vim mode, prompt input mode, tool permission context, hint suppression, loading state, memory type selector, footer selection states, paste/search/history states.
- **`ModeIndicatorProps`** (lines 226-236): Properties for the ModeIndicator inner component.

#### Exported Functions

- **`PromptInputFooterLeftSide(props): ReactNode`** (lines 127-225): Main footer left side component.
  - Shows exit message ("Press X again to exit") when active
  - Shows "Pasting text..." message when pasting
  - Shows Vim INSERT indicator when in Vim insert mode
  - Renders `HistorySearchInput` when searching
  - Delegates to `ModeIndicator` for normal display

#### Internal Components

- **`ProactiveCountdown()`** (lines 74-126): Renders a countdown timer for the next proactive tick. Uses `useSyncExternalStore` to subscribe to proactive module changes. Formats remaining time with `formatDuration` and displays "waiting X" text.
- **`ModeIndicator({ mode, toolPermissionContext, ... }): ReactNode`** (lines 237-483): The main mode display component showing:
  - Bash mode indicator ("! for bash mode")
  - Current permission mode with cycle shortcut hint
  - Remote session link
  - Background tasks status
  - Team status (when agent swarms enabled)
  - PR status badge
  - Teammate pills (in-process teammates with their own row)
  - Spinner hints (esc to interrupt, stop agents, toggle tasks)
  - Voice hints (hold key to speak, warmup)
  - Selection copy hints (ctrl+c, native select)
  - Task management hints
  - Fullscreen stability: always returns at least a space in fullscreen to preserve layout height

#### Internal Functions

- **`getSpinnerHintParts(...): ReactElement[]`** (lines 484-513): Generates spinner hint parts based on loading state, task items, and teammate presence. Returns arrays of KeyboardShortcutHint elements for interrupt, stop agents, and toggle tasks.
- **`isPrStatusEnabled(): boolean`** (lines 514-516): Returns whether PR status footer is enabled in global config (defaults to true).

#### Constants

- **`NO_OP_SUBSCRIBE`**: No-op subscriber for proactive module when not available.
- **`NULL`**: Returns null.
- **`MAX_VOICE_HINT_SHOWS`** = 3: Maximum times the voice hint is shown.

---

### 1.4 `PromptInputFooterSuggestions.tsx` (293 lines)

Renders the autocomplete suggestion dropdown in the prompt footer.

#### Exported Types

- **`SuggestionItem`** (lines 9-16): A suggestion with id, displayText, optional tag, description, metadata, and color theme key.
- **`SuggestionType`** (line 17): Union type of suggestion categories ('command', 'file', 'directory', 'agent', 'shell', 'custom-title', 'slack-channel', 'none').

#### Exported Constants

- **`OVERLAY_MAX_ITEMS`** = 5 (line 18): Maximum items shown in the overlay variant.

#### Internal Functions

- **`getIcon(itemId: string): string`** (lines 24-29): Returns icon character for suggestion type: '+' for files, '◇' for MCP resources, '*' for agents.
- **`isUnifiedSuggestion(itemId: string): boolean`** (lines 34-36): Checks if item is a file, MCP resource, or agent suggestion.

#### Exported Components

- **`SuggestionItemRow`** (lines 37-201): Memoized row renderer for a single suggestion.
  - For unified suggestions (file/MCP/agent): shows icon, displayText with path truncation, and description
  - For other suggestions: shows displayText, tag, and description in a tabular format
  - Computes layout widths based on terminal columns and maxColumnWidth
- **`PromptInputFooterSuggestions`** (lines 213-288): Main suggestions list component.
  - Computes maxVisibleItems based on terminal rows or overlay cap
  - Calculates scrolling window (startIndex, endIndex) centered on selectedSuggestion
  - Uses `justifyContent: 'flex-end'` to align suggestions at bottom of footer
- **`memo(PromptInputFooterSuggestions)`** (line 292): Memoized default export.

---

### 1.5 `PromptInputHelpMenu.tsx` (358 lines)

Displays a keyboard shortcut help overlay when the user types '?' or presses the help keybinding.

#### Types

- **`Props`** (lines 16-21): Optional dimColor, fixedWidth, gap, and paddingX properties.

#### Exported Components

- **`PromptInputHelpMenu(props): ReactNode`** (lines 22-357): Renders three-column help menu:
  - **Left column** (width 24): Input mode hints — '!' for bash, '/' for commands, '@' for file paths, '&' for background, '/btw' for side questions
  - **Middle column** (width 35): Editing shortcuts — double-tap esc to clear, shift+tab to cycle modes, ctrl+o for verbose output, ctrl+t for tasks, newline instructions, terminal toggle
  - **Right column**: Utility shortcuts — ctrl+_ to undo, ctrl+z to suspend (non-Windows), ctrl+v for images, alt+p for model picker, alt+o for fast mode, ctrl+s to stash, ctrl+g for external editor, /keybindings to customize
  - Each shortcut is resolved via `useShortcutDisplay` and formatted with `formatShortcut`

#### Internal Functions

- **`formatShortcut(shortcut: string): string`** (lines 13-15): Replaces '+' with ' + ' for display consistency.

---

### 1.6 `PromptInputModeIndicator.tsx` (93 lines)

Renders the prompt character ('>' or '!' for bash) with appropriate coloring.

#### Types

- **`Props`** (lines 10-15): mode (PromptInputMode), isLoading, optional viewing agent name/color.
- **`PromptCharProps`** (lines 34-38): isLoading and optional themeColor.

#### Internal Functions

- **`getTeammateThemeColor(): keyof Theme | undefined`** (lines 21-33): Returns the theme color for the current teammate's assigned color. Checks agent swarms enabled, gets teammate color, validates against known agent colors.

#### Internal Components

- **`PromptChar({ isLoading, themeColor }): ReactNode`** (lines 44-62): Renders the prompt character ('>' pointer figure) with optional teammate color override.

#### Exported Components

- **`PromptInputModeIndicator({ mode, isLoading, viewingAgentName, viewingAgentColor }): ReactNode`** (lines 63-92): Main mode indicator.
  - Shows teammate-colored prompt char when viewing a teammate
  - Shows '!' in bashBorder color for bash mode
  - Otherwise shows normal prompt char with optional teammate color

---

### 1.7 `PromptInputQueuedCommands.tsx` (117 lines)

Renders queued commands (from the command queue) above the prompt input.

#### Internal Functions

- **`isIdleNotification(value: string): boolean`** (lines 20-27): Checks if a command value is an idle notification (JSON with type 'idle_notification') that should be hidden.
- **`createOverflowNotificationMessage(count: number): string`** (lines 35-40): Creates a synthetic XML message for capped task notifications, showing "+N more tasks completed".
- **`processQueuedCommands(queuedCommands): QueuedCommand[]`** (lines 47-70): Processes queued commands by:
  - Filtering out idle notifications
  - Separating task notifications from other commands
  - Capping task notifications at MAX_VISIBLE_NOTIFICATIONS (3)
  - Creating overflow summary for excess notifications

#### Internal Component

- **`PromptInputQueuedCommandsImpl(): ReactNode`** (lines 71-115): Renders queued messages.
  - Subscribes to command queue and viewing agent state
  - Memoizes message creation (createUserMessage per command)
  - Filters to only visible commands
  - Hides when viewing an agent's transcript
  - Each message wrapped in `QueuedMessageProvider` with brief layout support

#### Exported

- **`PromptInputQueuedCommands`** = `React.memo(PromptInputQueuedCommandsImpl)` (line 116)

#### Constant

- **`EMPTY_SET`** = new Set<string>() (line 14)

---

### 1.8 `PromptInputStashNotice.tsx` (25 lines)

Shows a notice when a prompt is stashed.

#### Types

- **`Props`** (lines 5-7): hasStash boolean.

#### Exported Components

- **`PromptInputStashNotice({ hasStash }): ReactNode`** (lines 8-24): Renders "' Stashed (auto-restores after submit)" when hasStash is true. Returns null otherwise.

---

### 1.9 `Notifications.tsx` (240 lines)

Renders notification indicators in the prompt footer: IDE status, token warnings, auto-updater, API key status, voice errors, and more.

#### Types

- **`Props`** (lines 41-54): API key status, auto-updater result, debug/verbose flags, messages, update callbacks, IDE selection, MCP clients, wrap/narrow flags.

#### Exported Constant

- **`FOOTER_TEMPORARY_STATUS_TIMEOUT`** = 5000 (line 40): Default timeout for temporary footer notifications.

#### Exported Components

- **`Notifications(props): ReactNode`** (lines 55-209): Main notifications component.
  - Computes token usage from messages
  - Calculates token warning state via `calculateTokenWarningState`
  - Sets up env hook notifier for environment change notifications
  - Shows external editor hint when input is wrapped
  - Delegates rendering to `NotificationContent`

#### Internal Component

- **`NotificationContent({ ... }): ReactNode`** (lines 216-331): The rendering component for all notification items:
  - Polls API key helper inflight state for slow-helper notice (10s threshold)
  - Shows voice indicator when recording/processing
  - Renders IDE status indicator
  - Shows current notification (with jsx or text)
  - Shows "Now using extra usage" when in overage mode
  - Shows apiKeyHelper warning when slow
  - Shows auth error when API key invalid/missing
  - Shows "Debug mode" when debug enabled
  - Shows token count when verbose
  - Shows token warning (if not brief mode)
  - Shows auto-updater wrapper
  - Shows voice errors
  - Shows memory usage indicator
  - Shows sandbox prompt footer hint

---

### 1.10 `ShimmeredInput.tsx` (143 lines)

Renders highlighted input text with shimmer animation for rainbow keywords (ultrathink, ultraplan, etc.).

#### Types

- **`Props`** (lines 6-9): text string and highlights array.
- **`LinePart`** (lines 10-14): A text part with its highlight info and starting position.

#### Exported Components

- **`HighlightedInput({ text, highlights }): ReactNode`** (lines 15-139): Main highlighted input component.
  - Segments text by highlights into lines using `segmentTextByHighlights`
  - Detects if any highlight has shimmerColor for shimmer animation
  - Uses `useAnimationFrame(50)` for shimmer animation timing
  - Computes glimmerIndex for the animated sweep
  - Renders each character with `ShimmerChar` for shimmer-highlighted text or plain Text with Ansi for regular text

---

### 1.11 `VoiceIndicator.tsx` (137 lines)

Shows voice recording/processing status indicator.

#### Types

- **`Props`** (lines 7-9): voiceState ('idle' | 'recording' | 'processing').

#### Constants

- **`PROCESSING_DIM`** = { r:153, g:153, b:153 }: Dim gray for processing shimmer.
- **`PROCESSING_BRIGHT`** = { r:185, g:185, b:185 }: Bright gray for processing shimmer.
- **`PULSE_PERIOD_S`** = 2: 2-second period for pulsing animations.

#### Exported Components

- **`VoiceIndicator(props): ReactNode`** (lines 24-38): Gate component — returns null if VOICE_MODE feature not enabled, otherwise renders `VoiceIndicatorImpl`.
- **`VoiceWarmupHint()`** (lines 78-91): Static "keep holding..." text shown during voice warmup. Returns null if VOICE_MODE not enabled.

#### Internal Components

- **`VoiceIndicatorImpl({ voiceState }): ReactNode`** (lines 39-72): Switches on voiceState:
  - 'recording': Shows "listening..." dimmed text
  - 'processing': Shows `ProcessingShimmer`
  - 'idle': Returns null
- **`ProcessingShimmer()`** (lines 92-136): Animated "Voice: processing..." text.
  - Checks reduced motion preference
  - Uses `useAnimationFrame(50)` for animation clock
  - Computes sine-wave opacity for smooth color interpolation between PROCESSING_DIM and PROCESSING_BRIGHT
  - For reduced motion: shows static "Voice: processing..." in warning color

---

### 1.12 `HistorySearchInput.tsx` (51 lines)

Inline search input for searching through prompt history (Ctrl+R).

#### Types

- **`Props`** (lines 6-10): value string, onChange callback, historyFailedMatch boolean.

#### Internal Component

- **`HistorySearchInput({ value, onChange, historyFailedMatch }): ReactNode`** (lines 11-48): Renders a search box with label "search prompts:" (or "no matching prompt:") and a TextInput with:
  - Cursor forced to end of input (no navigation)
  - Width computed from stringWidth
  - Focus, showCursor, dimColor enabled
  - Single-line mode

#### Exported

- **`default HistorySearchInput`** (line 50): Default export.

---

### 1.13 `IssueFlagBanner.tsx` (12 lines)

ANT-ONLY banner component for reporting issues.

#### Exported Components

- **`IssueFlagBanner()`** (lines 9-11): Returns null. The actual banner content is eliminated by build-time dead code when `"external" !== 'ant'`.

---

### 1.14 `SandboxPromptFooterHint.tsx` (64 lines)

Shows sandbox violation notifications in the prompt footer.

#### Exported Components

- **`SandboxPromptFooterHint(): ReactNode`** (lines 7-63):
  - Subscribes to `SandboxManager.getSandboxViolationStore()` for violation count changes
  - Shows recent violation count for 5 seconds after each new violation
  - Renders a dimmed message: "Sandbox blocked N operations · (shortcut) for details · /sandbox to disable"
  - Returns null when sandboxing is disabled or no recent violations

---

### 1.15 `inputModes.ts` (33 lines)

Utility functions for handling input mode characters (! for bash).

#### Exported Functions

- **`prependModeCharacterToInput(input: string, mode: PromptInputMode): string`** (lines 4-14): Prepends '!' for bash mode input (for history/serialization).
- **`getModeFromInput(input: string): HistoryMode`** (lines 16-21): Returns 'bash' if input starts with '!', otherwise 'prompt'.
- **`getValueFromInput(input: string): string`** (lines 23-29): Strips mode character from input — returns full string for prompt mode, slice(1) for bash mode.
- **`isInputModeCharacter(input: string): boolean`** (lines 31-33): Returns true if input is '!' (the bash mode character).

---

### 1.16 `inputPaste.ts` (90 lines)

Handles truncation of very long pasted text.

#### Types

- **`TruncatedMessage`** (lines 7-10): Contains truncatedText and placeholderContent strings.

#### Constants

- **`TRUNCATION_THRESHOLD`** = 10000 (line 4): Character threshold before truncation.
- **`PREVIEW_LENGTH`** = 1000 (line 5): Characters to show at start and end.

#### Exported Functions

- **`maybeTruncateMessageForInput(text: string, nextPasteId: number): TruncatedMessage`** (lines 20-55): If text exceeds TRUNCATION_THRESHOLD, shows first and last 500 chars with a placeholder reference in between. Returns truncated text and the hidden content.
- **`maybeTruncateInput(input, pastedContents): { newInput, newPastedContents }`** (lines 61-90): Wraps `maybeTruncateMessageForInput` for use in hooks. Computes next paste ID, applies truncation, returns new input and updated pastedContents.

#### Internal Functions

- **`formatTruncatedTextRef(id: number, numLines: number): string`** (lines 57-59): Formats truncated text reference as `[...Truncated text #N +N lines...]`.

---

### 1.17 `usePromptInputPlaceholder.ts` (76 lines)

Hook that determines the placeholder text for the prompt input.

#### Types

- **`Props`** (lines 16-20): input string, submitCount, optional viewingAgentName.

#### Constants

- **`NUM_TIMES_QUEUE_HINT_SHOWN`** = 3: Max times queue hint is shown.
- **`MAX_TEAMMATE_NAME_LENGTH`** = 20: Truncation threshold for teammate names.

#### Exported Functions

- **`usePromptInputPlaceholder({ input, submitCount, viewingAgentName }): string | undefined`** (lines 25-76):
  - Returns undefined when input is non-empty
  - When viewing a teammate: shows "Message @displayName..." (truncated to 20 chars)
  - When queued commands are editable and hint count < 3: shows "Press up to edit queued messages"
  - When submitCount < 1 and prompt suggestions enabled and not proactive: returns example command from cache

---

### 1.18 `useShowFastIconHint.ts` (31 lines)

Hook managing the /fast hint display next to the fast icon.

#### Exported Functions

- **`useShowFastIconHint(showFastIcon: boolean): boolean`** (lines 11-31): Shows hint for 5 seconds once per session. Uses module-level `hasShownThisSession` flag and `useState`/`useEffect` with `setTimeout`.

#### Constants

- **`HINT_DISPLAY_DURATION_MS`** = 5000

---

### 1.19 `useSwarmBanner.ts` (155 lines)

Hook that returns banner information for swarm/standalone agent/CLI context.

#### Types

- **`SwarmBannerInfo`** (lines 29-32): text string and bgColor theme key, or null.

#### Exported Functions

- **`useSwarmBanner(): SwarmBannerInfo`** (lines 44-146): Returns banner info:
  - **Teammate process** (non-in-process): Shows "@agentName" with assigned color
  - **Leader with spawned teammates**: Shows tmux attach hint when not in tmux; shows viewed teammate name when inside tmux/native/in-process
  - **Viewing background agent** (CoordinatorTaskPanel): Reverse-looks up name from agentNameRegistry, shows "@name" with agent color
  - **Standalone agent** (/rename, /color): Shows name with custom color, no @team
  - **--agent CLI flag**: Shows agent type with cyan background
  - Returns null when no context matches

#### Internal Functions

- **`toThemeColor(colorName, fallback): keyof Theme`** (lines 148-155): Converts agent color name to theme color key. Validates against AGENT_COLORS array, falls back to provided fallback (default 'cyan_FOR_SUBAGENTS_ONLY').

---

### 1.20 `utils.ts` (60 lines)

General utility functions for the prompt input component.

#### Exported Functions

- **`isVimModeEnabled(): boolean`** (lines 12-15): Returns true if editorMode in global config is 'vim'.
- **`getNewlineInstructions(): string`** (lines 17-32): Returns platform-appropriate newline instructions:
  - Apple Terminal on macOS: "shift + enter for newline"
  - iTerm2/VSCode with shift+enter binding installed: "shift + enter for newline"
  - Otherwise: "backslash (\) + return (enter) for newline" or "enter for newline"
- **`isNonSpacePrintable(input: string, key: Key): boolean`** (lines 39-60): Returns true when the keystroke is a printable character that doesn't begin with whitespace. Used to gate the lazy space inserted after image pills.

---

### 1.21 `useMaybeTruncateInput.ts` (58 lines)

Hook to automatically truncate very long inputs (>10K chars).

#### Types

- **`Props`** (lines 5-11): input, pastedContents, and setter callbacks.

#### Exported Functions

- **`useMaybeTruncateInput({ input, pastedContents, onInputChange, setCursorOffset, setPastedContents })`** (lines 13-58):
  - Tracks whether truncation has been applied for the current input
  - When input exceeds 10K chars and hasn't been truncated: calls `maybeTruncateInput`, updates input/cursor/pastedContents
  - Resets when input is cleared (after submission)

---

## Directory 2: `components/Settings/` (4 files)

### 2.1 `Settings.tsx` (137 lines)

Top-level settings dialog component with tab navigation.

#### Types

- **`Props`** (lines 15-21): onClose callback, command context, default tab ('Status' | 'Config' | 'Usage' | 'Gates').

#### Exported Components

- **`Settings({ onClose, context, defaultTab }): ReactNode`** (lines 22-130):
  - Manages selected tab, tabsHidden, and configOwnsEsc/gatesOwnsEsc states
  - Computes content height based on modal context and terminal rows
  - Registers Escape handler that reverts and closes
  - Renders a Pane with Tabs containing:
    - **Status tab**: Shows `Status` component with diagnostics promise
    - **Config tab**: Shows `Config` wrapped in Suspense
    - **Usage tab**: Shows `Usage`
    - **Gates tab**: Ant-only, conditionally rendered

---

### 2.2 `Status.tsx` (241 lines)

Shows system status information: version, session, model, IDE, MCP, sandbox, and diagnostics.

#### Types

- **`Props`** (lines 15-18): command context and diagnostics Promise.

#### Exported Functions

- **`buildDiagnostics(): Promise<Diagnostic[]>`** (lines 54-56): Async function combining installation, health, and memory diagnostics into a single array.

#### Exported Components

- **`Status({ context, diagnosticsPromise }): ReactNode`** (lines 102-187):
  - Reads mainLoopModel and mcp from AppState
  - Reads theme from useTheme
  - Builds primary section (version, session name/ID, cwd, account, API provider)
  - Builds secondary section (model, IDE, MCP, sandbox, setting sources)
  - Renders property sections and diagnostics in a Suspense boundary

#### Internal Components

- **`PropertyValue({ value }): ReactNode`** (lines 57-101): Renders property values.
  - Arrays: renders as comma-separated wrapped Text components
  - Strings: renders as plain Text
  - JSX: renders directly
- **`Diagnostics({ promise }): ReactNode`** (lines 204-237): Suspense-compatible component that resolves the diagnostics promise and renders warnings/errors with icons.

#### Internal Functions

- **`buildPrimarySection(): Property[]`** (lines 19-36): Returns version, session name (with /rename hint if unnamed), session ID, cwd, account properties, and API provider properties.
- **`buildSecondarySection({ mainLoopModel, mcp, theme, context }): Property[]`** (lines 37-53): Returns model label, IDE properties, MCP properties, sandbox properties, and setting sources properties.

---

### 2.3 `Config.tsx` (1822 lines)

The most complex settings panel — renders an interactive, searchable, keyboard-navigable list of toggleable settings.

#### Types

- **`Props`** (lines 51-59): onClose, context, setTabsHidden, onIsSearchModeChange, optional contentHeight.
- **`SettingBase`** (lines 60-67): Union of { id, label } and { id, label: ReactNode, searchText }.
- **`Setting`** (lines 68-83): Discriminated union of boolean, enum, and managedEnum setting types, each with id, label, value, and onChange.
- **`SubMenu`** (line 84): 'Theme' | 'Model' | 'TeammateModel' | 'ExternalIncludes' | 'OutputStyle' | 'ChannelDowngrade' | 'Language' | 'EnableAutoUpdates'.

#### Exported Components

- **`Config({ onClose, context, setTabsHidden, onIsSearchModeChange, contentHeight }): ReactNode`** (lines 85-1737): Massive config component:
  - Manages tab header focus, search mode, selected index, scroll offset
  - Computes pane cap and max visible items
  - Reads extensive app state (model, verbose, thinking, fast mode, prompt suggestions, brief mode, bridge, settings)
  - Defines model change handler with analytics and fast mode implications
  - Defines verbose toggle with global config persistence
  - Defines 30+ `settingsItems` including:
    - autoCompactEnabled
    - spinnerTipsEnabled
    - prefersReducedMotion
    - thinkingEnabled
    - fastMode (conditional)
    - promptSuggestionEnabled (conditional)
    - speculationEnabled (ant-only)
    - fileCheckpointingEnabled (conditional)
    - verbose
    - terminalProgressBarEnabled
    - showStatusInTerminalTab (conditional)
    - showTurnDuration
    - defaultPermissionMode (with auto mode support)
    - useAutoModeDuringPlan (conditional)
    - respectGitignore
    - copyFullResponse
    - copyOnSelect (fullscreen only)
    - autoUpdatesChannel
    - theme
    - notifChannel (with push notification settings)
    - outputStyle
    - defaultView (kairos/brief only)
    - language
    - editorMode (normal/vim)
    - prStatusFooterEnabled
    - model
    - diffTool (IDE-connected)
    - autoConnectIde / autoInstallIdeExtension (terminal-dependent)
    - claudeInChromeDefaultEnabled
    - teammateMode (agent swarms)
    - teammateDefaultModel
    - remoteControlAtStartup (bridge mode)
    - externalClaudeMdIncludes
    - customApiKey
  - Implements search filtering via `filteredSettingsItems`
  - Scroll adjustment and keeping selection visible
  - `handleSaveAndClose`: collects all changed settings, formats them with chalk, and closes with summary
  - `revertChanges`: restores theme, global config, settings files, app state, and bootstrap state to mount-time snapshots
  - `toggleSetting`: handles boolean toggle, managedEnum submenu opening, enum cycling, and auto-update channel logic
  - Keyboard navigation (up/down, left/right/tab for cycling values)
  - Rendering logic for all submenus (ThemePicker, ModelPicker, OutputStylePicker, LanguagePicker, ChannelDowngradeDialog, EnableAutoUpdates dialog, ClaudeMdExternalIncludesDialog)
  - Main list rendering with scroll indicators, color-coded selected items, type-specific value display

#### Internal Functions

- **`teammateModelDisplayString(value): string`** (lines 1738-1744): Formats teammate model for display: undefined shows hardcoded fallback, null shows "Default (leader's model)", otherwise uses modelDisplayString.

#### Internal Components

- **`NotifChannelLabel({ value }): ReactNode`** (lines 1754-1821): Renders notification channel labels with protocol details (auto, iTerm2 OSC 9, Terminal Bell, Kitty OSC 99, Ghostty OSC 777, iTerm2 w/ Bell, Disabled).

#### Constants

- **`THEME_LABELS`** (lines 1745-1753): Human-readable labels for theme options.

---

### 2.4 `Usage.tsx` (377 lines)

Shows API usage/rate limit information with progress bars.

#### Types

- **`LimitBarProps`** (lines 18-24): title, limit (RateLimit), maxWidth, optional showTimeInReset and extraSubtext.
- **`ExtraUsageSectionProps`** (lines 266-269): extraUsage (ExtraUsage type) and maxWidth.

#### Exported Components

- **`Usage(): ReactNode`** (lines 174-265):
  - Fetches utilization data via `fetchUtilization()`
  - Shows loading/error states with retry keybinding
  - Renders `LimitBar` for 5-hour session limit and 7-day weekly limit
  - Conditionally shows Sonnet-only weekly limit (Max/Team plans)
  - Shows `ExtraUsageSection` when extra usage data is available
  - Shows `OverageCreditUpsell` when eligible

#### Internal Components

- **`LimitBar({ title, limit, maxWidth, showTimeInReset, extraSubtext }): ReactNode`** (lines 25-173): Renders a rate limit progress bar.
  - Null for null utilization
  - Wide mode (>= 62 cols): title on one line, ProgressBar + "N% used" on next, subtext with reset info below
  - Narrow mode: title and subtext inline, then ProgressBar, then "N% used"
- **`ExtraUsageSection({ extraUsage, maxWidth }): ReactNode`** (lines 271-376): Renders extra usage information for Pro/Max subscribers.
  - Shows enable prompt when not enabled
  - Shows "Unlimited" when no monthly limit
  - Shows formatted credit usage with LimitBar and "spent" subtext

#### Internal Constants

- **`EXTRA_USAGE_SECTION_TITLE`** = 'Extra usage' (line 270)

---

## Directory 3: `components/Spinner.tsx` + `components/Spinner/` (14 files)

### 3.1 `Spinner.tsx` (562 lines, at `components/Spinner.tsx`)

The main spinner component with verb animation, thinking status, and teammate integration.

#### Types

- **`Props`** (lines 42-57): mode, timer refs (loadingStartTimeRef, totalPausedMsRef, pauseStartTimeRef), optional spinnerTip, responseLengthRef, override color/message/suffix, verbose flag, hasActiveTools, leaderIsIdle.
- **`BriefSpinnerProps`** (lines 312-315): mode and optional overrideMessage.

#### Exported Types

- **`SpinnerMode`** (line 39): Re-exported from Spinner/index.js.

#### Exported Components

- **`SpinnerWithVerb(props: Props): ReactNode`** (lines 62-81): Thin wrapper that branches on isBriefOnly.
  - In brief mode (kairos/brief enabled, briefOnly active, not viewing teammate): renders `BriefSpinner`
  - Otherwise: renders `SpinnerWithVerbInner`
- **`BriefIdleStatus()`** (lines 451-500): Static idle placeholder for brief/assistant mode.
  - Same 2-row [blank, content] footprint as BriefSpinner
  - Shows connection warning (reconnecting/disconnected) in red or background task count in subtle
  - Returns a height=2 Box when no status to show
- **`Spinner()`** (lines 507-550): Simple standalone spinner (no verb text).
  - Uses `useAnimationFrame(120)` for 8.3fps animation
  - Cycles through SPINNER_FRAMES characters
  - For reduced motion: shows static '●' dot

#### Internal Components

- **`SpinnerWithVerbInner(props: Props): ReactNode`** (lines 82-301): The full spinner implementation.
  - Checks reduced motion preference
  - Computes verbose verb from tasks/override/random
  - Tracks thinking status with minimum 2s display per state
  - Computes teammate token aggregation (sum of all running teammates)
  - Handles leader-is-idle display (static dim text + spinner tree)
  - Handles foregrounded idle teammate display
  - Shows tips based on elapsed time thresholds (clear tip at 30min, btw tip at 30s)
  - Shows token budget text (ant-only)
  - Delegates animation to `SpinnerAnimationRow`
  - Conditionally renders `TeammateSpinnerTree` or `TaskListV2` or tip/budget text
- **`BriefSpinner({ mode, overrideMessage }): ReactNode`** (lines 316-436): Simplified brief-mode spinner.
  - 2-row footprint: blank row + spinner row (marginTop=1, paddingLeft=2)
  - Shows verb with shimmer animation using `computeGlimmerIndex` and `computeShimmerSegments`
  - Shows connection warnings in red
  - Shows background task count on the right

#### Internal Functions

- **`findNextPendingTask(tasks): Task | undefined`** (lines 551-561): Finds the first unblocked pending task. Checks blockedBy dependencies, falls back to first pending task.

#### Constants

- **`DEFAULT_CHARACTERS`**: Default spinner characters from `getDefaultCharacters()`.
- **`SPINNER_FRAMES`**: Default characters + reversed, for animation sequence.

---

### 3.2 `SpinnerAnimationRow.tsx` (265 lines)

The 50ms-animated portion of the spinner. Owns the animation frame subscription and all derived values.

#### Types

- **`SpinnerAnimationRowProps`** (lines 36-69): 20 properties including mode, reducedMotion, timer refs, message, colors, display flags, teammate data, thinking status, effort suffix.

#### Exported Components

- **`SpinnerAnimationRow(props: SpinnerAnimationRowProps): ReactNode`** (lines 81-231): The hot animation path component.
  - Uses `useAnimationFrame(50)` for 20fps animation
  - Computes elapsed time from timer refs
  - Tracks turn start time for teammate context
  - Uses `useStalledAnimation` for stall detection and red fade
  - Computes frame (for spinner glyph) and glimmer index
  - Implements token counter smooth animation (increment by 3, 8, or 50 tokens per frame)
  - Computes leader/total token counts
  - Implements thinking text with progressive width gating
  - Computes thinking shimmer color (sine-wave opacity interpolation)
  - Progressive responsive layout: thinking > timer > tokens
  - Builds status parts array and renders with Byline or parentheses

#### Internal Components

- **`SpinnerModeGlyph({ mode }): ReactNode`** (lines 232-264): Renders arrow direction glyph based on mode: arrowDown for tool-input/tool-use/responding/thinking, arrowUp for requesting.

#### Constants

- **`SEP_WIDTH`**: Width of ' · ' separator.
- **`THINKING_BARE_WIDTH`**: Width of 'thinking' text.
- **`SHOW_TOKENS_AFTER_MS`** = 30,000: Show token count after 30 seconds.
- **`THINKING_INACTIVE`** = { r:153, g:153, b:153 }: Dim gray for thinking shimmer.
- **`THINKING_INACTIVE_SHIMMER`** = { r:185, g:185, b:185 }: Bright gray for thinking shimmer.
- **`THINKING_DELAY_MS`** = 3000: Delay before thinking shimmer starts.
- **`THINKING_GLOW_PERIOD_S`** = 2: Sine wave period for thinking glow.

---

### 3.3 `SpinnerGlyph.tsx` (80 lines)

Renders the spinning character glyph with color and stall effects.

#### Types

- **`Props`** (lines 15-21): frame number, messageColor theme key, optional stalledIntensity, reducedMotion, time.

#### Exported Components

- **`SpinnerGlyph({ frame, messageColor, stalledIntensity, reducedMotion, time }): ReactNode`** (lines 22-79):
  - For reduced motion: shows pulsing dot (1s visible, 1s dim, 2s cycle) colored by messageColor
  - For stalled state: interpolates between messageColor and ERROR_RED based on stalledIntensity
  - Normal: cycles through SPINNER_FRAMES at the given frame index

#### Constants

- **`SPINNER_FRAMES`**: Default characters + reversed array.
- **`REDUCED_MOTION_DOT`** = '●': Static dot for reduced motion.
- **`REDUCED_MOTION_CYCLE_MS`** = 2000: 2-second pulse cycle.
- **`ERROR_RED`** = { r:171, g:43, b:63 }: Red color for stalled state.

---

### 3.4 `ShimmerChar.tsx` (36 lines)

Renders a single character with shimmer highlight effect.

#### Types

- **`Props`** (lines 5-11): char string, index, glimmerIndex, messageColor, shimmerColor.

#### Exported Components

- **`ShimmerChar({ char, index, glimmerIndex, messageColor, shimmerColor }): ReactNode`** (lines 12-35):
  - Highlights the character at glimmerIndex with shimmerColor
  - Also highlights adjacent characters (index +/- 1) for a 3-char shimmer glow
  - Non-highlighted characters use messageColor

---

### 3.5 `GlimmerMessage.tsx` (328 lines)

Renders the spinner message text with shimmer animation and stall/flash effects.

#### Types

- **`Props`** (lines 9-17): message string, mode, messageColor, glimmerIndex, flashOpacity, shimmerColor, optional stalledIntensity.

#### Exported Components

- **`GlimmerMessage({ message, mode, messageColor, glimmerIndex, flashOpacity, shimmerColor, stalledIntensity }): ReactNode`** (lines 23-327):
  - Returns null for empty message
  - **Stalled state**: Interpolates between messageColor and ERROR_RED
  - **Tool-use mode**: Flashes between messageColor and shimmerColor using flashOpacity
  - **Normal shimmer**: Segments message into grapheme clusters, splits into before/shimmer/after segments around glimmerIndex (3-char shimmer window), renders each segment with appropriate color

#### Constants

- **`ERROR_RED`** = { r:171, g:43, b:63 }: Red for stalled state.

---

### 3.6 `FlashingChar.tsx` (61 lines)

Renders a single character with color interpolation between two colors.

#### Types

- **`Props`** (lines 6-11): char string, flashOpacity (0-1), messageColor, shimmerColor.

#### Exported Components

- **`FlashingChar({ char, flashOpacity, messageColor, shimmerColor }): ReactNode`** (lines 12-60):
  - Attempts smooth RGB interpolation between base and shimmer colors
  - Fallback for ANSI themes: binary switch at flashOpacity > 0.5

---

### 3.7 `TeammateSpinnerLine.tsx` (233 lines)

Renders a single teammate row in the spinner tree.

#### Types

- **`Props`** (lines 16-23): teammate (InProcessTeammateTaskState), isLast, isSelected, isForegrounded, allIdle, showPreview.

#### Exported Components

- **`TeammateSpinnerLine({ teammate, isLast, isSelected, isForegrounded, allIdle, showPreview }): ReactNode`** (lines 72-232):
  - Picks random verb on mount (or uses teammate's spinnerVerb)
  - Picks past-tense verb (or uses teammate's pastTenseVerb)
  - Renders tree characters (╘═/╞═ or └─/├─) based on position and highlight state
  - Tracks idle start time for "Idle for X..." display
  - Freezes duration display when all teammates idle
  - **Progressive responsive layout**:
    - Wide (80+): full name + activity + stats + hint
    - Medium (60-80): full name + activity
    - Narrow (<60): activity only
  - Activity text from recentActivities summary or lastActivity description or random verb
  - Status rendering: stopping, awaiting approval, idle (with duration), active (with verb)
  - Preview lines from teammate messages (when showPreview enabled)

#### Internal Functions

- **`getMessagePreview(messages): string[]`** (lines 29-71): Extracts last 3 lines of content from teammate's messages. Handles text blocks and tool_use blocks, trims lines to 80 chars.

---

### 3.8 `TeammateSpinnerTree.tsx` (272 lines)

Renders the tree of teammates with leader and hide row.

#### Types

- **`Props`** (lines 10-20): selectedIndex, isInSelectionMode, allIdle, leaderVerb, leaderTokenCount, leaderIdleText.

#### Exported Components

- **`TeammateSpinnerTree({ selectedIndex, isInSelectionMode, allIdle, leaderVerb, leaderTokenCount, leaderIdleText }): ReactNode`** (lines 21-202):
  - Reads tasks and viewing agent state from AppState
  - Gets running teammates sorted from `getRunningTeammatesSorted`
  - Returns null when no teammates
  - Renders leader row with tree char (╒═/┌─), name ("team-lead"), verb, token count, select/view hints
  - Maps teammate tasks to `TeammateSpinnerLine` components
  - Renders `HideRow` at the end when in selection mode

#### Internal Components

- **`HideRow({ isSelected }): ReactNode`** (lines 212-271): Renders a "hide" row with tree character (╘═/└─), selectable with pointer and "enter to collapse" hint.

---

### 3.9 `index.ts` (10 lines)

Barrel export file for the Spinner directory.

#### Exported Items

- `FlashingChar`, `GlimmerMessage`, `ShimmerChar`, `SpinnerGlyph` (components)
- `SpinnerMode` (type)
- `useShimmerAnimation`, `useStalledAnimation` (hooks)
- `getDefaultCharacters`, `interpolateColor` (utilities)

Note: Teammate components are NOT exported — they use dynamic require() for dead code elimination.

---

### 3.10 `teammateSelectHint.ts` (1 line)

#### Exported Constant

- **`TEAMMATE_SELECT_HINT`** = 'shift + ↑/↓ to select' (line 1)

---

### 3.11 `useShimmerAnimation.ts` (31 lines)

Hook to compute shimmer animation position.

#### Exported Functions

- **`useShimmerAnimation(mode, message, isStalled): [ref, glimmerIndex]`** (lines 6-31):
  - Uses `useAnimationFrame` with speed based on mode (50ms for requesting, 200ms otherwise)
  - When stalled: passes null to unsubscribe from animation, returns glimmerIndex -100
  - Computes cyclePosition and cycleLength from message width
  - For requesting mode: returns glimmer sweeping left-to-right (cyclePosition % cycleLength - 10)
  - For other modes: returns glimmer sweeping right-to-left (messageWidth + 10 - cyclePosition % cycleLength)

---

### 3.12 `useStalledAnimation.ts` (75 lines)

Hook to detect and animate the spinner's stalled (red) state.

#### Exported Functions

- **`useStalledAnimation(time, currentResponseLength, hasActiveTools, reducedMotion): { isStalled, stalledIntensity }`** (lines 6-75):
  - Tracks last token time and last response length via refs
  - Resets stall timer when new tokens arrive
  - Time since last token computed from animation clock or mount time
  - Stall triggers after 3 seconds of no tokens (when no active tools)
  - Stall intensity fades in over 2 seconds (0 to 1)
  - Smooth intensity transition at 50ms intervals (0.1 lerp per step)
  - For reduced motion: instant intensity changes

---

### 3.13 `utils.ts` (84 lines)

Color and character utilities for the spinner.

#### Exported Functions

- **`getDefaultCharacters(): string[]`** (lines 4-11): Returns platform-specific spinner characters. Ghostty terminal uses '*' instead of '✽' due to rendering offset. macOS uses a different character set than other platforms.
- **`interpolateColor(color1, color2, t): RGBColorType`** (lines 14-24): Linear interpolation between two RGB colors by factor t (0-1).
- **`toRGBColor(color): RGBColorString`** (lines 27-29): Converts RGB object to `rgb(r,g,b)` string.
- **`hueToRgb(hue): RGBColorType`** (lines 32-66): Converts HSL hue to RGB using voice-mode waveform parameters (saturation=0.7, lightness=0.6). Implements full HSL-to-RGB conversion.
- **`parseRGB(colorStr): RGBColorType | null`** (lines 70-84): Parses `rgb(r,g,b)` string to RGB object with caching via `RGB_CACHE` Map.

---

## Directory 4: `components/sandbox/` (5 files)

### 4.1 `SandboxSettings.tsx` (296 lines)

Main sandbox configuration dialog with tab navigation.

#### Types

- **`Props`** (lines 15-20): onComplete callback and depCheck (SandboxDependencyCheck).
- **`SandboxMode`** = 'auto-allow' | 'regular' | 'disabled' (line 21).

#### Exported Components

- **`SandboxSettings({ onComplete, depCheck }): ReactNode`** (lines 22-221):
  - Checks current sandbox state (enabled, auto-allow)
  - Computes sandbox mode options with "(current)" indicators
  - Handles mode selection: auto-allow (enabled + autoAllowBashIfSandboxed), regular (enabled only), disabled
  - Displays socket warning when warnings exist and Unix sockets not allowed
  - Tabs: Mode, Overrides, Config, and conditionally Dependencies (when errors/warnings)
  - Registers Escape keybinding for cancel

#### Internal Components

- **`SandboxModeTab({ showSocketWarning, options, onSelect, onComplete }): ReactNode`** (lines 222-295):
  - Shows socket warning when relevant
  - Renders sandbox mode selector with `Select` component
  - Shows auto-allow mode description and documentation link

---

### 4.2 `SandboxConfigTab.tsx` (45 lines)

Read-only tab showing current sandbox configuration details.

#### Exported Components

- **`SandboxConfigTab(): ReactNode`** (lines 5-41):
  - Checks if sandbox is enabled
  - Shows warning notes from dependency check
  - When disabled: shows "Sandbox is not enabled"
  - When enabled: displays excluded commands, filesystem read restrictions (denied paths, allowed within denied), filesystem write restrictions (allowed paths, denied within allowed), network restrictions (allowed/denied hosts with managed indicator), allowed Unix sockets, and glob pattern warnings

---

### 4.3 `SandboxDependenciesTab.tsx` (120 lines)

Shows sandbox dependency check results with platform-specific install instructions.

#### Types

- **`Props`** (lines 6-8): depCheck (SandboxDependencyCheck).

#### Exported Components

- **`SandboxDependenciesTab({ depCheck }): ReactNode`** (lines 9-104):
  - Detects platform (macOS vs other)
  - On macOS: shows seatbelt status (built-in), ripgrep status with brew install hint
  - On Linux/WSL: shows bubblewrap, socat, and seccomp filter status with install instructions
  - Shows other errors in red

---

### 4.4 `SandboxDoctorSection.tsx` (46 lines)

Renders sandbox status in the /doctor output.

#### Exported Components

- **`SandboxDoctorSection(): ReactNode`** (lines 5-39):
  - Early returns null if platform not supported or sandbox not enabled in settings
  - Checks dependencies for errors/warnings
  - Returns null if no errors or warnings
  - Shows "Sandbox" section with status (Missing dependencies / Available with warnings), error/warning messages, and "/sandbox for install instructions" hint

---

### 4.5 `SandboxOverridesTab.tsx` (193 lines)

Tab for configuring sandbox override settings (allow unsandboxed fallback vs strict mode).

#### Types

- **`Props`** (lines 8-12): onComplete callback.
- **`OverrideMode`** = 'open' | 'closed' (line 13).

#### Exported Components

- **`SandboxOverridesTab({ onComplete }): ReactNode`** (lines 14-58):
  - Checks if sandbox is enabled and settings are locked by policy
  - When disabled: shows explanation
  - When locked: shows lock notice with current setting
  - Otherwise: renders `OverridesSelect`

#### Internal Components

- **`OverridesSelect({ onComplete, currentMode }): ReactNode`** (lines 63-192):
  - Builds options with "(current)" indicators for open/closed modes
  - Handles selection: sets allowUnsandboxedCommands based on choice
  - Shows descriptions for both modes (allow unsandboxed fallback, strict sandbox mode)
  - Provides documentation link

---

## Directory 5: `components/shell/` (4 files)

### 5.1 `ExpandShellOutputContext.tsx` (36 lines)

React context for controlling shell output expansion.

#### Internal Context

- **`ExpandShellOutputContext`** (line 12): Created with `React.createContext(false)`. Boolean context indicating shell output should be shown in full.

#### Exported Components

- **`ExpandShellOutputProvider({ children }): ReactNode`** (lines 13-27): Wraps children in context provider with value=true.

#### Exported Hooks

- **`useExpandShellOutput(): boolean`** (lines 33-35): Returns true if rendered inside an ExpandShellOutputProvider, indicating shell output should be shown in full rather than truncated.

---

### 5.2 `OutputLine.tsx` (118 lines)

Renders a single line of shell output with JSON formatting and URL linking support.

#### Exported Functions

- **`tryFormatJson(line: string): string`** (lines 12-31): Attempts to parse and re-stringify a line as JSON for pretty-printing.
  - Performs JSON round-trip parse → stringify
  - Detects precision loss (large integers exceeding Number.MAX_SAFE_INTEGER) by comparing normalized original to normalized stringified
  - If precision loss detected: returns original unformatted line
  - Otherwise: returns pretty-printed JSON (2-space indent)
- **`tryJsonFormatContent(content: string): string`** (lines 33-39): Formats multi-line content. Skips content longer than 10K chars. Splits by newline, formats each line, rejoins.
- **`linkifyUrlsInText(content: string): string`** (lines 44-46): Replaces http/https URLs in JSON string values with hyperlinks via `createHyperlink`.
- **`OutputLine({ content, verbose, isError, isWarning, linkifyUrls }): ReactNode`** (lines 47-104): Main output line component.
  - Formats content with JSON formatting and optional URL linking
  - In verbose mode or when expandShellOutput is true: shows full content
  - Otherwise: truncates content via `renderTruncatedContent`
  - Strips underline ANSI codes to prevent leakage
  - Renders with Ansi wrapper and MessageResponse, colored by error/warning state
- **`stripUnderlineAnsi(content: string): string`** (lines 113-117): Strips underline ANSI escape sequences specifically (preserving other formatting). Uses regex matching SGR sequences containing code 4 (underline).

#### Constants

- **`MAX_JSON_FORMAT_LENGTH`** = 10,000 (line 32): Skip JSON formatting for content longer than this.
- **`URL_IN_JSON`** regex (line 43): Matches http/https URLs in JSON strings.

---

### 5.3 `ShellProgressMessage.tsx` (150 lines)

Shows real-time progress of a running shell command.

#### Types

- **`Props`** (lines 9-18): output string, fullOutput string, optional elapsedTimeSeconds, totalLines, totalBytes, timeoutMs, taskId, verbose flag.

#### Exported Components

- **`ShellProgressMessage({ output, fullOutput, elapsedTimeSeconds, totalLines, totalBytes, timeoutMs, verbose }): ReactNode`** (lines 19-146):
  - Strips ANSI from output and fullOutput
  - In verbose mode: shows full output
  - In non-verbose mode: shows last 5 lines
  - When no output: shows "Running..." with time display
  - Shows line count (totalLines or "+N lines" for extra)
  - Renders truncated output in a box with height capped at 5
  - Shows status line with line count, time display, and file size
  - Wrapped in MessageResponse and OffscreenFreeze for performance

---

### 5.4 `ShellTimeDisplay.tsx` (74 lines)

Displays elapsed time and/or timeout for a running shell command.

#### Types

- **`Props`** (lines 5-8): optional elapsedTimeSeconds and timeoutMs.

#### Exported Components

- **`ShellTimeDisplay({ elapsedTimeSeconds, timeoutMs }): ReactNode`** (lines 9-73):
  - Returns null when neither elapsedTimeSeconds nor timeoutMs provided
  - Formats timeout with `hideTrailingZeros: true`
  - When only timeout: shows "(timeout X)"
  - When only elapsed: shows "(X)"
  - When both: shows "(X · timeout Y)"

---

## Summary of Export/Import Patterns

- **PromptInput** components use feature flags (`bun:bundle` `feature()`) for build-time dead code elimination (ANT-ONLY, VOICE_MODE, BRIDGE_MODE, KAIROS, etc.)
- **Spinner** components separate animation from layout: `SpinnerAnimationRow` owns the 50ms clock, `SpinnerWithVerb` is off the animation path
- **Settings** uses a searchable, keyboard-navigable list pattern with submenus for complex pickers
- **Sandbox** uses a tabs-based dialog with Select components for mode/override configuration
- **Shell** components handle ANSI stripping, JSON formatting, progressive truncation, and responsive layout
- All components use React Compiler memo caching (the `_c` pattern) for automatic memoization
