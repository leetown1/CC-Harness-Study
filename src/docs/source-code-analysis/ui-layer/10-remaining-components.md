# Remaining UI Components — Complete Reference

Covers all files in `AskUserQuestionPermissionRequest`, `FilePermissionDialog`, `BashPermissionRequest`, `FileWritePermissionRequest`, `NotebookEditPermissionRequest`, `PowerShellPermissionRequest`, `ComputerUseApproval`, `FeedbackSurvey`, and `hooks`.

---

## Batch A: Permission Subcomponents

### 1. AskUserQuestionPermissionRequest (7 files)

This subsystem renders the multi-step permission dialog when Claude uses the `AskUserQuestion` tool. It supports single-select, multi-select, text input ("Other"), image pasting, and a side-by-side preview mode for questions with preview content.

#### 1.1 `AskUserQuestionPermissionRequest.tsx` (645 lines)

**Entry component** for the ask-user-question permission flow.

**Exports:**
- `AskUserQuestionPermissionRequest(props: PermissionRequestProps)` — default export. Wraps `AskUserQuestionPermissionRequestBody` in either direct render (syntax highlighting disabled) or `<Suspense>` with async `CliHighlight`.

**Internal components:**
- `AskUserQuestionWithHighlight` — resolves the `getCliHighlightPromise()` via `use()`, then renders `AskUserQuestionPermissionRequestBody` with highlight context.

**`AskUserQuestionPermissionRequestBody`** — core ~600-line body component:
  - **Parsing:** Calls `AskUserQuestionTool.inputSchema.safeParse(toolUseConfirm.input)` to extract `questions[]`.
  - **Layout computation:** Iterates all questions/options to compute `globalContentHeight` and `globalContentWidth` for terminal. For options with `preview`, measures rendered markdown lines via `applyMarkdown` + `stringWidth` to calculate side-by-side panel heights. Caps at `terminalRows - CONTENT_CHROME_OVERHEAD(15)`.
  - **Image pasting:** Manages `pastedContentsByQuestion` state (record keyed by question text → `Record<id, PastedContent>`). `onImagePaste` stores images via `cacheImagePath` + `storeImage`. `onRemoveImage` deletes from state. Converts to `ImageBlockParam[]` on submit via `convertImagesToBlocks`.
  - **Plan mode:** Reads `toolPermissionContext.mode` from app state; if `"plan"`, provides `handleFinishPlanInterview` and `planFilePath`.
  - **Navigation:** Uses `useMultipleChoiceState()` for `currentQuestionIndex`, `answers`, `questionStates`, `isInTextInput`, and navigation actions. Creates `handleTabPrev`/`handleTabNext` wrappers. Registers `'tabs:previous'`/`'tabs:next'` keybindings.
  - **Answer handlers:**
    - `handleQuestionAnswer` — routes through single/multi-select, `__other__` text input, image attachments on input; auto-submits for single-question non-multi-select.
    - `handleFinalResponse` — "submit" or "cancel" from the submit view.
    - `handleRespondToClaude` — passes feedback to `toolUseConfirm.onReject` with unanswered questions.
    - `handleFinishPlanInterview` — signals enough answers for planning.
    - `submitAnswers` — maps answers + annotations + images, calls `toolUseConfirm.onAllow` with `updatedInput`.
  - **Rendering switch:** If `currentQuestion` (question view), renders `<QuestionView>`. If `isInSubmitView`, renders `<SubmitQuestionsView>`.
  - **Analytics:** Logs `tengu_ask_user_question_rejected`, `tengu_ask_user_question_respond_to_claude`, `tengu_ask_user_question_finish_plan_interview`, `tengu_ask_user_question_accepted` with metadata.

**Helper:**
- `convertImagesToBlocks(images)` — async, calls `maybeResizeAndDownsampleImageBlock` on each.

**Constants:** `MIN_CONTENT_HEIGHT = 12`, `MIN_CONTENT_WIDTH = 40`, `CONTENT_CHROME_OVERHEAD = 15`.

---

#### 1.2 `PreviewBox.tsx` (229 lines)

A bordered monospace box for rendering preview content with syntax-highlighted markdown.

**Exports:**
- `PreviewBox(props: PreviewBoxProps)` — entry component. Wraps in `<Suspense>` for async `CliHighlight`.

**`PreviewBoxProps` type:**
- `content: string` — markdown content to display.
- `maxLines?: number` (default 20) — max visible lines.
- `minHeight?: number` — minimum line count (padding applied).
- `minWidth?: number` (default 40).
- `maxWidth?: number` — terminal width cap.

**Constants:** `BOX_CHARS` — Unicode box-drawing characters (`┌┐└┘─│├┤`).

**`PreviewBoxBody` rendering logic:**
1. Applies `applyMarkdown(content, theme, highlight)`.
2. Splits into lines, truncates to `effectiveMaxLines`.
3. Computes `paddingNeeded` for min-height.
4. Computes `contentWidth` from max `stringWidth` + `minWidth`.
5. Clamps `boxWidth` to `effectiveMaxWidth`.
6. Renders: top border, content lines (vertical bar + ANSI text + padding + vertical bar), truncation bar (if truncated: `├── ✂ ── N lines hidden┤`), bottom border.
7. Lines exceeding `innerWidth` are sliced via `sliceAnsi`.

---

#### 1.3 `PreviewQuestionView.tsx` (328 lines)

Side-by-side question view for questions with preview content. Left: option list. Right: preview panel + notes input.

**Exports:**
- `PreviewQuestionView(props: Props): React.ReactNode`

**Props:** Extends question/questionStates/answers with `onUpdateQuestionState`, `onAnswer`, `onTextInputFocus`, `onCancel`, `onTabPrev`/`onTabNext`, `onRespondToClaude`, `onFinishPlanInterview`.

**State:**
- `isFooterFocused`, `footerIndex` — footer navigation (Chat / Skip interview).
- `isInNotesInput` — toggles notes `TextInput`.
- `focusedIndex` — which option is highlighted; resets on question change via `useRef(prevQuestionText)`.
- `cursorOffset` for the notes TextInput.

**Key logic:**
- `handleSelectOption(index)` — sets `focusedIndex`, updates `questionState.selectedValue`, calls `onAnswer`.
- `handleNavigate(direction)` — up/down/numeric key navigation.
- `handleKeyDown` — comprehensive keyboard handler:
  - Footer mode: up/down/enter (respond/claude vs finish plan), escape (cancel).
  - Notes mode: escape exits notes.
  - Option navigation: up/down, enter (select), `n` (focus notes), `1-9` (direct index), escape (cancel).
- `useKeybinding('chat:externalEditor')` — ctrl+g opens external editor for notes.
- `useKeybindings` for `tabs:previous`/`tabs:next` (active when not in notes/footer).
- `handleNotesExit` — re-submits answer with selected value on exiting notes.

**Layout:**
- `LEFT_PANEL_WIDTH = 30`, `GAP = 4`, `columns` from terminal.
- `previewMaxWidth = columns - LEFT_PANEL_WIDTH - GAP`.
- `previewMaxLines` computed from `minContentHeight - PREVIEW_OVERHEAD(11)`.
- Renders: `Divider` → `QuestionNavigationBar` → `PermissionRequestTitle` → side-by-side Box (left: option list with `figures.pointer`/tick indicators; right: `PreviewBox` + notes section) → footer section (Chat about this / Skip interview).

---

#### 1.4 `QuestionNavigationBar.tsx` (178 lines)

Tab-like bar showing question numbers/names, answer status, and submit tab.

**Exports:**
- `QuestionNavigationBar(props: Props)`

**Props:** `questions`, `currentQuestionIndex`, `answers`, `hideSubmitTab?`.

**Logic:**
- If `hideSubmitTab && questions.length === 1`, hides arrows entirely.
- Computes `submitText = " ✓ Submit "` (if not hidden).
- Fixed width = left arrow + right arrow + submit text.
- Computes tab header widths: each `q.header || "Q{N}"`. If total fits, uses full names. If not, allocates half width for current tab, remaining for others with min 6 per tab. Truncates via `truncateToWidth`.
- Renders: `< Prev` / tabs (checkbox icon + display text, highlighted for current with `backgroundColor="permission"`) / submit tab / `Next >`.

---

#### 1.5 `QuestionView.tsx` (465 lines)

Main question view rendering either `PreviewQuestionView` (when preview content exists) or an inline `Select`/`SelectMulti`.

**Exports:**
- `QuestionView(props: Props)`

**Props:** Full set including `onImagePaste`, `pastedContents`, `onRemoveImage`, `planFilePath`.

**State:**
- `isFooterFocused`, `footerIndex` — same footer pattern as PreviewQuestionView.
- `isOtherFocused` — tracks when "Other" input is active.
- `editorName` — derived from `getExternalEditor()`.

**Logic:**
- `hasAnyPreview` = `!question.multiSelect && question.options.some(opt => opt.preview)`. If true, delegates entirely to `<PreviewQuestionView>`.
- Otherwise builds options array: maps question.options to `{type:"text", value, label, description}`, then appends an "Other" `{type:"input"}` option.
- Renders `Select` (single) or `SelectMulti` based on `question.multiSelect`. Both wired to `onUpdateQuestionState`, `onAnswer`, `handleFocus`, `handleOpenEditor`, `onImagePaste`, etc.
- `handleFocus` — sets `isOtherFocused` if the focused value is `"__other__"`.
- `handleOpenEditor` — async, calls `editPromptInEditor` for ctrl+g.
- `handleKeyDown` — routes footer keyboard events (up/down/enter/escape).
- Plan mode banner with `<FilePathLink>` when `isInPlanMode && planFilePath`.
- Help text adapts to single vs multi-question mode.
- `handleDownFromLastItem` — focuses footer when navigating past last option.

---

#### 1.6 `SubmitQuestionsView.tsx` (144 lines)

Final review/submit screen after answering all questions.

**Exports:**
- `SubmitQuestionsView(props: Props)`

**Props:** `questions`, `currentQuestionIndex`, `answers`, `allQuestionsAnswered`, `permissionResult`, `minContentHeight`, `onFinalResponse`.

**Layout:**
- `QuestionNavigationBar` (on submit tab).
- `PermissionRequestTitle` = "Review your answers".
- Warning if not all answered: `<Text color="warning">`.
- Lists all answered questions with `figures.bullet` and `figures.arrowRight`.
- Shows `PermissionRuleExplanation`.
- "Ready to submit your answers?" prompt.
- `<Select>` with two options: "Submit answers" (value `"submit"`) and "Cancel" (value `"cancel"`).

---

#### 1.7 `use-multiple-choice-state.ts` (179 lines)

State management hook for the multiple-choice question flow.

**Exports:**
- `useMultipleChoiceState(): MultipleChoiceState`

**Types:**
- `AnswerValue = string`
- `QuestionState = { selectedValue?: string | string[]; textInputValue: string }`
- `State = { currentQuestionIndex: number; answers: Record<string, AnswerValue>; questionStates: Record<string, QuestionState>; isInTextInput: boolean }`
- `MultipleChoiceState` — extends state with dispatch actions: `nextQuestion`, `prevQuestion`, `updateQuestionState`, `setAnswer`, `setTextInputMode`.

**Reducer actions:**
- `'next-question'` — increments index, clears text input mode.
- `'prev-question'` — decrements (min 0), clears text input mode.
- `'update-question-state'` — merges `Partial<QuestionState>` for a specific question text. Respects `isMultiSelect` for default `selectedValue` (empty array vs undefined).
- `'set-answer'` — stores answer. If `shouldAdvance` (default true), auto-advances to next question.
- `'set-text-input-mode'` — toggles `isInTextInput`.

**Initial state:** `currentQuestionIndex: 0`, empty answers/questionStates, `isInTextInput: false`.

---

### 2. FilePermissionDialog (5 files)

Generic permission dialog framework for file operations (read/write/create). Used by FileWrite, NotebookEdit, and other file-manipulating tools.

#### 2.1 `FilePermissionDialog.tsx` (204 lines)

Generic dialog component for file operation permissions.

**Exports:**
- `FilePermissionDialog<T extends ToolInput>(props: FilePermissionDialogProps<T>): React.ReactNode`

**`FilePermissionDialogProps<T>`:**
- `toolUseConfirm`, `toolUseContext`, `onDone`, `onReject` (standard permission props).
- `title: string`, `subtitle?: ReactNode`, `question?: string | ReactNode`, `content?: ReactNode`.
- `completionType?: CompletionType`, `languageName?: string`.
- `path: string | null`, `parseInput: (input: unknown) => T`, `operationType?: FileOperationType`.
- `ideDiffSupport?: IDEDiffSupport<T>`.
- `workerBadge: WorkerBadgeProps | undefined`.

**Logic:**
1. Derives `languageName` via `useMemo`: either override or `getLanguageName(path)`.
2. Sets up `unaryEvent` for logging; calls `usePermissionRequestLogging`.
3. Detects `symlinkTarget` via `expandPath` + `safeResolvePath`; shows warning if path is a symlink (outside cwd gets extra warning).
4. Calls `useFilePermissionDialog` hook to get `options`, feedback state, focus state, input mode toggles.
5. Calls `parseInput` to get typed input.
6. If `ideDiffSupport` provided, creates `ideDiffConfig` via `getConfig` and sets up `diffParams` for `useDiffInIDE`.
7. If `showingDiffInIDE`, renders `<ShowInIDEPrompt>`.
8. Otherwise renders `<PermissionDialog>` with:
   - Symlink warning.
   - `content` (diff component).
   - Question text and `<Select>` with permission options.
   - Help text: "Esc to cancel" + "Tab to amend" hint.

---

#### 2.2 `permissionOptions.tsx` (177 lines)

Builds the list of permission decision options for file operations.

**Exports:**
- `isInClaudeFolder(filePath: string): boolean` — checks if path is within project's `.claude/`.
- `isInGlobalClaudeFolder(filePath: string): boolean` — checks if path is within `~/.claude/`.
- `PermissionOption` type: `{ type: 'accept-once' } | { type: 'accept-session'; scope?: 'claude-folder' | 'global-claude-folder' } | { type: 'reject' }`.
- `PermissionOptionWithLabel` — extends `OptionWithDescription<string>` with `option: PermissionOption`.
- `FileOperationType = 'read' | 'write' | 'create'`.
- `getFilePermissionOptions({ filePath, toolPermissionContext, operationType, onRejectFeedbackChange, onAcceptFeedbackChange, yesInputMode, noInputMode }): PermissionOptionWithLabel[]`

**Option building:**
1. **"Yes" (accept-once):** Either input field (if `yesInputMode`) or simple label.
2. **".claude folder" option (accept-session with scope):** If path is within `.claude/` and operation is not `read`, shows special session option for Claude's own settings.
3. **"Yes, during this session" (accept-session):** Generic session-level allow. Label varies by:
   - Inside working directory: "Yes, during this session" or "Yes, allow all edits during this session".
   - Outside working directory: includes directory name `basename(dirPath)`.
   - Includes `modeCycleShortcut` (shift+tab) for keyboard hint.
4. **"No" (reject):** Either input field (if `noInputMode`) or simple label.

**Utility:** `normalizeCaseForComparison` for case-insensitive path comparison.

---

#### 2.3 `useFilePermissionDialog.ts` (212 lines)

Hook managing file permission dialog state.

**Exports:**
- `ToolInput` interface `{ [key: string]: unknown }`.
- `UseFilePermissionDialogProps<T>` interface.
- `UseFilePermissionDialogResult<T>` interface: `options`, `onChange`, `acceptFeedback`, `rejectFeedback`, `focusedOption`, `setFocusedOption`, `handleInputModeToggle`, `yesInputMode`, `noInputMode`.
- `useFilePermissionDialog<T>(props): UseFilePermissionDialogResult<T>`

**State:**
- `acceptFeedback`, `rejectFeedback` — free-text feedback strings.
- `focusedOption` — which option is selected (default `'yes'`).
- `yesInputMode`, `noInputMode` — toggles for feedback text input.
- `yesFeedbackModeEntered`, `noFeedbackModeEntered` — persists whether user ever entered feedback mode (remains true after collapse).

**Key logic:**
- Generates `options` via `getFilePermissionOptions` and `useMemo`.
- `onChange(option, input, feedback?)` — main handler: constructs `PermissionHandlerParams`, overrides `toolUseConfirm.onAllow` to pass parsed input, dispatches to `PERMISSION_HANDLERS[option.type]`.
- `handleCycleMode` — finds `accept-session` option and invokes onChange (bound to `confirm:cycleMode` keybinding).
- `handleFocusedOptionChange` — wraps `setFocusedOption` and resets input mode if navigating away with empty text.
- `handleInputModeToggle` — toggles input mode for Yes/No; logs analytics events (`tengu_accept_feedback_mode_entered/collapsed`, `tengu_reject_feedback_mode_entered/collapsed`).

---

#### 2.4 `usePermissionHandler.ts` (185 lines)

Permission decision handlers for accept-once, accept-session, and reject actions.

**Exports:**
- `PermissionHandlerParams` type.
- `PermissionHandlerOptions` type: `hasFeedback?`, `feedback?`, `enteredFeedbackMode?`, `scope?`.
- `PERMISSION_HANDLERS` — record of handler functions keyed by `PermissionOption['type']`.

**Handlers:**

1. **`handleAcceptOnce`**:
   - Calls `logPermissionEvent('accept')`.
   - Logs `tengu_accept_submitted` with feedback/enteredFeedbackMode metadata.
   - Calls `toolUseConfirm.onAllow(input, [], feedback?)`.

2. **`handleAcceptSession`**:
   - If `scope === 'claude-folder'` or `'global-claude-folder'`, creates `PermissionUpdate[]` with `addRules` using `CLAUDE_FOLDER_PERMISSION_PATTERN` or `GLOBAL_CLAUDE_FOLDER_PERMISSION_PATTERN`, `behavior: 'allow'`, `destination: 'session'`.
   - Otherwise calls `generateSuggestions(path, operationType, toolPermissionContext)`.
   - Calls `toolUseConfirm.onAllow(input, suggestions)`.

3. **`handleReject`**:
   - Logs `logPermissionEvent('reject')` with `hasFeedback`.
   - Logs `tengu_reject_submitted`.
   - Calls `onDone()`, `onReject()`, `toolUseConfirm.onReject(feedback?)`.

**Logging helper:**
- `logPermissionEvent(event, completionType, languageName, messageId, hasFeedback?)` — calls `logUnaryEvent` with platform, language_name, message_id.

---

#### 2.5 `ideDiffConfig.ts` (42 lines)

Types and helpers for IDE diff integration in file permission dialogs.

**Exports:**
- `FileEdit` interface: `old_string: string; new_string: string; replace_all?: boolean`.
- `IDEDiffConfig` interface: `filePath: string; edits?: FileEdit[]; editMode?: 'single' | 'multiple'`.
- `IDEDiffChangeInput` interface: `file_path: string; edits: FileEdit[]`.
- `IDEDiffSupport<TInput>` interface: `getConfig(input: TInput): IDEDiffConfig; applyChanges(input: TInput, modifiedEdits: FileEdit[]): TInput`.
- `createSingleEditDiffConfig(filePath, oldString, newString, replaceAll?): IDEDiffConfig` — convenience factory.

---

### 3. BashPermissionRequest (2 files)

#### 3.1 `BashPermissionRequest.tsx` (482 lines)

Permission dialog for the Bash tool. Detects sed commands (routes to `SedEditPermissionRequest`) and includes bash classifier integration.

**Exports:**
- `BashPermissionRequest(props: PermissionRequestProps)`

**`ClassifierCheckingSubtitle`** — extracted shimmer animation component showing "Attempting to auto-approve…" with 20fps shimmer while classifier runs. Isolated to prevent re-rendering the full dialog.

**`BashPermissionRequestInner`** — core ~400-line implementation:

1. **Parsing:** Extracts `command`, `description` from `BashTool.inputSchema`. Checks for sed commands via `parseSedEditCommand`; if found, delegates to `<SedEditPermissionRequest>`.

2. **Shell Feedback:** Uses `useShellPermissionFeedback` for Yes/No input modes, feedback state, and reject handler.

3. **Classifier integration:**
   - `classifierDescription` — initially from prop, refined async via `generateGenericDescription` (if `isClassifierPermissionsEnabled()`).
   - `initialClassifierDescriptionEmpty` — tracks whether the first description was empty.
   - `classifierWasChecking` — captures mount-time `toolUseConfirm.classifierCheckInProgress`.
   - `classifierSubtitle` — shows shimmer (checking), success tick, "Requires manual approval", or nothing.

4. **Compound command handling (GH#11380):**
   - Detects `decisionReason.type === 'subcommandResults'`.
   - Initializes `editablePrefix` from backend suggestion (single Bash rule) or sync prefix extraction (`getSimpleCommandPrefix`/`getFirstWordPrefix`).
   - Async refinement via `getCompoundCommandPrefixesStatic` (tree-sitter for ant builds).
   - `hasUserEditedPrefix` ref prevents overwriting user edits.

5. **Destructive command warning:** via `getDestructiveCommandWarning`, gated by `tengu_destructive_command_warning` feature flag.

6. **Sandboxing:** `SandboxManager.isSandboxingEnabled()` + `shouldUseSandbox(input)`.

7. **Options:** Built via `bashToolUseOptions` with `editablePrefix`, `suggestions`, `classifierDescription`, etc.

8. **onSelect handler:**
   - `'yes-prefix-edited'` — creates `addRules` permission update with trimmed prefix.
   - `'yes-classifier-reviewed'` — creates `addRules` with `createPromptRuleContent(description)` (session scope).
   - `'yes'` — simple accept with optional feedback.
   - `'yes-apply-suggestions'` — accepts backend suggestions.
   - `'no'` — reject with optional feedback.

9. **Rendering:** `<PermissionDialog>` with command display, explainer content, permission debug info (toggle with `permission:toggleDebug`), rule explanation, destructive warning, `Select` (auto-approved disables options), and help text footer.

---

#### 3.2 `bashToolUseOptions.tsx` (147 lines)

Builds the option list for the Bash permission dialog.

**Exports:**
- `BashToolUseOption = 'yes' | 'yes-apply-suggestions' | 'yes-prefix-edited' | 'yes-classifier-reviewed' | 'no'`
- `bashToolUseOptions({ suggestions, decisionReason, onRejectFeedbackChange, onAcceptFeedbackChange, onClassifierDescriptionChange, classifierDescription, initialClassifierDescriptionEmpty, existingAllowDescriptions, yesInputMode, noInputMode, editablePrefix, onEditablePrefixChange }): OptionWithDescription<BashToolUseOption>[]`

**Logic:**
1. "Yes" — simple or input (if `yesInputMode`).
2. Always-allow options (if `shouldShowAlwaysAllowOptions()`):
   - If `editablePrefix` is defined and no non-Bash suggestions exist → editable input option (`'yes-prefix-edited'`).
   - Else if suggestions exist → label generated by `generateShellSuggestionsLabel` (`'yes-apply-suggestions'`).
   - If ant build, classifier not shown as editable prefix, classifier enabled, description non-empty, not duplicate, and decision isn't `'classifier'` → editable classifier option (`'yes-classifier-reviewed'`).
3. "No" — simple or input (if `noInputMode`).

**Helpers:**
- `descriptionAlreadyExists(description, existingDescriptions)` — normalized comparison.
- `stripBashRedirections(command)` — removes output redirections for label clarity.

---

### 4. FileWritePermissionRequest (2 files)

#### 4.1 `FileWritePermissionRequest.tsx` (161 lines)

Permission dialog for the `FileWriteTool`. Delegates to `FilePermissionDialog`.

**Exports:**
- `FileWritePermissionRequest(props: PermissionRequestProps)`

**`ideDiffSupport` object:**
- `getConfig` — reads current file content via `readFileSync(input.file_path)`, returns `createSingleEditDiffConfig(file_path, oldContent, input.content, false)`.
- `applyChanges` — replaces `input.content` with first edit's `new_string`.

**Parsing:** `parseInput = (input) => FileWriteTool.inputSchema.parse(input)`.

**Logic:**
1. Parses input, extracts `file_path` and `content`.
2. Reads old file content (or empty string if ENOENT).
3. Determines `actionText = fileExists ? "overwrite" : "create"`.
4. Computes subtitle (relative path), title ("Overwrite file" / "Create file"), question text.
5. Renders `<FileWriteToolDiff>` and wraps in `<FilePermissionDialog>` with `completionType="write_file_single"` and `ideDiffSupport`.

---

#### 4.2 `FileWriteToolDiff.tsx` (89 lines)

Renders a unified diff or raw highlighted code for file write operations.

**Exports:**
- `FileWriteToolDiff(props: Props): React.ReactNode`

**Props:** `file_path`, `content`, `fileExists`, `oldContent`.

**Logic:**
- If `fileExists`, computes `hunks` via `getPatchForDisplay` (treating entire old content → new content as a single edit). Renders `<StructuredDiff>` for each hunk with `<NoSelect>` ellipsis separators.
- If new file, renders `<HighlightedCode code={content} filePath={file_path} />`.
- Encased in a dashed-border `<Box>`.

---

### 5. NotebookEditPermissionRequest (2 files)

#### 5.1 `NotebookEditPermissionRequest.tsx` (166 lines)

Permission dialog for `NotebookEditTool`.

**Exports:**
- `NotebookEditPermissionRequest(props: PermissionRequestProps)`

**Parsing:** Uses `safeParse` with error logging. Falls back to empty input on parse failure.

**Logic:**
1. Extracts `notebook_path`, `edit_mode`, `cell_type`.
2. Derives `language` from `cell_type` (`"markdown"` or `"python"`).
3. Builds `editTypeText` based on `edit_mode` ("insert this cell into" / "delete this cell from" / "make this edit to").
4. Renders `<NotebookEditToolDiff>` and wraps in `<FilePermissionDialog>` with custom title ("Edit notebook"), question, `languageName` override.

**Key:** `languageName` passed explicitly to `FilePermissionDialog` (unlike FileWrite which derives from path). `completionType="tool_use_single"`.

---

#### 5.2 `NotebookEditToolDiff.tsx` (235 lines)

Renders diff for notebook cell edits.

**Exports:**
- `NotebookEditToolDiff(props: Props)`

**Props:** `notebook_path`, `cell_id`, `new_source`, `cell_type?`, `edit_mode?`, `verbose`, `width`.

**Logic:**
1. Fetches notebook content via `getFsImplementation().readFile(path)` → `safeParseJSON` in a `use()` promise wrapped in `<Suspense>`.
2. **`NotebookEditToolDiffInner`:**
   - Locates the target cell: first tries `parseCellId(cell_id)` (numeric index), then falls back to `.find(cell => cell.id === cell_id)`.
   - Extracts `oldSource` (joins array source if needed).
   - For `"replace"` mode: computes `hunks` via `getPatchForDisplay`.
   - For `"insert"` mode: renders `<HighlightedCode>` of new source.
   - For `"delete"` mode: renders `<HighlightedCode>` of old source.
   - Shows cell metadata: bold file path, dim description ("Replace cell contents for cell {id} ({cell_type})").
   - Encased in a round-bordered `<Box>`.

---

### 6. PowerShellPermissionRequest (2 files)

#### 6.1 `PowerShellPermissionRequest.tsx` (235 lines)

Permission dialog for the `PowerShellTool`.

**Exports:**
- `PowerShellPermissionRequest(props: PermissionRequestProps): React.ReactNode`

**Similar structure to BashPermissionRequest** but simpler (no classifier, no sandbox toggle):

1. **Parsing:** `PowerShellTool.inputSchema.parse(toolUseConfirm.input)`.
2. **Shell feedback:** `useShellPermissionFeedback` hook.
3. **Editable prefix:**
   - Initialized from raw command (single-line) or `undefined` (multiline).
   - Async refinement via `getCompoundCommandPrefixesStatic(command, isAllowlistedCommand)`.
   - `hasUserEditedPrefix` ref.
4. **Destructive warning:** via `getDestructiveCommandWarning`, gated by feature flag.
5. **Options:** Built via `powershellToolUseOptions`.
6. **onSelect handler:** Similar to Bash: `'yes-prefix-edited'` → `addRules` with `PowerShellTool.name`; `'yes'` → accept with feedback; `'yes-apply-suggestions'` → backend suggestions; `'no'` → reject.
7. **Rendering:** `<PermissionDialog>` with command display, explainer, permission debug, rule explanation, destructive warning, `Select`, help text.

**Note:** Title is always "PowerShell command" (no sandbox indicator — sandbox not supported on Windows).

---

#### 6.2 `powershellToolUseOptions.tsx` (91 lines)

Builds option list for PowerShell permission dialog.

**Exports:**
- `PowerShellToolUseOption = 'yes' | 'yes-apply-suggestions' | 'yes-prefix-edited' | 'no'`
- `powershellToolUseOptions({ suggestions, onRejectFeedbackChange, onAcceptFeedbackChange, yesInputMode, noInputMode, editablePrefix, onEditablePrefixChange }): OptionWithDescription<PowerShellToolUseOption>[]`

**Logic:**
1. "Yes" — simple or input.
2. Always-allow options (if `shouldShowAlwaysAllowOptions() && suggestions.length > 0`):
   - If `editablePrefix` defined and no non-PowerShell suggestions → editable `'yes-prefix-edited'`.
   - Else → `generateShellSuggestionsLabel` for `'yes-apply-suggestions'`.
3. "No" — simple or input.

**Note:** No classifier option (ANT-only feature for Bash). No sandbox toggle.

---

### 7. ComputerUseApproval (1 file)

#### 7.1 `ComputerUseApproval.tsx` (441 lines)

Approval UI for Computer Use (CU) permissions. Handles macOS TCC permissions and app allowlisting.

**Exports:**
- `ComputerUseApproval({ request, onDone }: ComputerUseApprovalProps)`

**Types:**
- `CuPermissionRequest`, `CuPermissionResponse` from `@ant/computer-use-mcp/types`.
- `DEFAULT_GRANT_FLAGS` — default flags for granted permissions.

**Two-panel dispatcher:**
- If `request.tccState` present → `<ComputerUseTccPanel>` (macOS permissions).
- Else → `<ComputerUseAppListPanel>` (app allowlist).

**`DENY_ALL_RESPONSE`** — empty `granted[]`, empty `denied[]`, `DEFAULT_GRANT_FLAGS`.

---

**`ComputerUseTccPanel`** (TCC permissions):

**Options:** Dynamic based on missing permissions: "Open System Settings → Accessibility", "Open System Settings → Screen Recording", "Try again".

**Logic:**
- Shows checkmark/cross for each permission status.
- `onChange` handler opens System Settings panes via `execFileNoThrow("open", "x-apple.systempreferences:...")` or calls `onDone()` for retry.
- Uses `<Dialog>` with title "Computer Use needs macOS permissions".

---

**`ComputerUseAppListPanel`** (App allowlist):

**Options:** "Allow for this session (N apps)", "Deny, and tell Claude what to do differently".

**Constants:** `SENTINEL_WARNING` — maps `getSentinelCategory` results to warnings ("equivalent to shell access", "can read/write any file", "can change system settings").

**State:**
- `checked: Set<string>` — initialized from `request.apps.flatMap(a => a.resolved && !a.alreadyGranted ? [a.resolved.bundleId] : [])`.

**Logic:**
- `ALL_FLAG_KEYS = ["clipboardRead", "clipboardWrite", "systemKeyCombos"]`.
- `requestedFlagKeys` — subset where `request.requestedFlags[k]` is true.
- `respond(allow)` — constructs `CuPermissionResponse` with:
  - `granted` — resolved, checked apps with timestamps.
  - `denied` — unresolved or unchecked apps.
  - `flags` — `DEFAULT_GRANT_FLAGS` merged with requested flags.
- **App list display:**
  - Not installed: `○ name (not installed)` dim.
  - Already granted: `✓ name (already granted)` dim.
  - Installable: `●/○ name` with optional sentinel warning.
- Shows "Also requested:" flags section.
- Shows "N other apps will be hidden while Claude works."
- Uses `<Dialog>` title "Computer Use wants to control these apps".

---

## Batch B: FeedbackSurvey (9 files)

### 8. `FeedbackSurvey.tsx` (174 lines)

Top-level feedback survey component rendering different states.

**Exports:**
- `FeedbackSurvey(props: Props)`

**Props:** `state` (closed | open | thanks | transcript_prompt | submitting | submitted), `lastResponse`, `handleSelect`, `handleTranscriptSelect?`, `inputValue`, `setInputValue`, `onRequestFeedback?`, `message?`.

**State-based rendering:**
- `"closed"` → null.
- `"thanks"` → `<FeedbackSurveyThanks>`.
- `"submitted"` → "✓ Thanks for sharing your transcript!".
- `"submitting"` → "Sharing transcript…".
- `"transcript_prompt"` → `<TranscriptSharePrompt>` (if handleTranscriptSelect provided and input is valid).
- `"open"` (default) → `<FeedbackSurveyView>` (if input validated).

**`FeedbackSurveyThanks`** — internal component showing "Thanks for the feedback!" message:
- If `lastResponse === "good"` and `onRequestFeedback` exists, shows follow-up prompt "Press [1] to tell us what went well".
- Uses `useDebouncedDigitInput` with `isFollowUpDigit` (only '1') and `once: true`.
- Links to `/feedback` command.
- If `lastResponse === "bad"`, suggests `/issue`.

---

### 9. `FeedbackSurveyView.tsx` (108 lines)

The main survey view showing rating options.

**Exports:**
- `FeedbackSurveyView(props: Props)`
- `isValidResponseInput(input)` — validates input is in `['0','1','2','3']`.

**Constants:**
- `RESPONSE_INPUTS = ['0', '1', '2', '3']`.
- `inputToResponse`: `{'0': 'dismissed', '1': 'bad', '2': 'fine', '3': 'good'}`.
- `DEFAULT_MESSAGE = 'How is Claude doing this session? (optional)'`.

**Logic:**
- Wires `useDebouncedDigitInput` with `isValidResponseInput` and digit→response mapping.
- Renders: cyan dot + bold message, then option list: `1: Bad`, `2: Fine`, `3: Good`, `0: Dismiss`.

---

### 10. `TranscriptSharePrompt.tsx` (88 lines)

Prompt for sharing session transcript with Anthropic.

**Exports:**
- `TranscriptShareResponse = 'yes' | 'no' | 'dont_ask_again'`
- `TranscriptSharePrompt(props: Props)`

**Constants:**
- `RESPONSE_INPUTS = ['1', '2', '3']`.
- `inputToResponse`: `{'1': 'yes', '2': 'no', '3': 'dont_ask_again'}`.

**Logic:**
- Wires `useDebouncedDigitInput`.
- Renders prompt question + link to data usage docs + options.

---

### 11. `useFeedbackSurvey.tsx` (296 lines)

Main hook orchestrating session-based feedback survey logic.

**Exports:**
- `useFeedbackSurvey(messages, isLoading, submitCount, surveyType?, hasActivePrompt?)`

**Types:**
- `FeedbackSurveyConfig` — time/model/probability settings via GrowthBook.
- `TranscriptAskConfig` — probability for transcript ask.

**Default config:**
- `minTimeBeforeFeedbackMs: 600000` (10 min), `minTimeBetweenFeedbackMs: 3600000` (1 hr), `minTimeBetweenGlobalFeedbackMs: 100000000` (~3.17 yrs).
- `minUserTurnsBeforeFeedback: 5`, `minUserTurnsBetweenFeedback: 10`.
- `hideThanksAfterMs: 3000`, `onForModels: ['*']`, `probability: 0.005`.

**Key state:**
- `feedbackSurvey` — `{ timeLastShown, submitCountAtLastAppearance }`.
- Uses refs to prevent re-rolling probability on re-renders: `probabilityPassedRef`, `lastEligibleSubmitCountRef`.
- Tracks `lastAssistantMessageIdRef` for analytics.

**Callback factory pattern:**
- `onOpen` — logs `'appeared'` event, persists cross-session state.
- `onSelect` — logs `'responded'` event.
- `shouldShowTranscriptPrompt` — probability gate per rating (bad/good), checks `transcriptShareDismissed`, `isPolicyAllowed('allow_product_feedback')`.
- `onTranscriptPromptShown` — logs `'transcript_prompt_appeared'`.
- `onTranscriptSelect` — handles share/no/dont_ask_again; calls `submitTranscriptShare` for 'yes'.

**`shouldOpen` computation:**
Checks: not closed, not loading, no active prompt, not force-displayed, model allowed, not disabled by env/config/policy, session pacing (time since last, user turns), probability gate (one roll per eligibility window via refs), global pacing (filesystem read for cross-session).

**Delegates to:** `useSurveyState` for state machine.

---

### 12. `useMemorySurvey.tsx` (213 lines)

Hook for the memory-survey-specific trigger (shown after Claude reads a memory file).

**Exports:**
- `useMemorySurvey(messages, isLoading, hasActivePrompt?, { enabled? })`

**Constants:**
- `MEMORY_SURVEY_GATE = 'tengu_dunwich_bell'`, `SURVEY_PROBABILITY = 0.2`.
- `MEMORY_WORD_RE = /\bmemor(?:y|ies)\b/i`.

**`hasMemoryFileRead(messages)`** — scans assistant messages for `tool_use` blocks where `toolName === FILE_READ_TOOL_NAME` and `file_path` matches `isAutoManagedMemoryFile`.

**Logic:**
- Tracks `seenAssistantUuids` ref (Set) to avoid re-evaluation.
- Tracks `memoryReadSeen` ref (once true, skips O(n) scan).
- `useSurveyState` with `hideThanksAfterMs: 3000` and no transcript prompt probability gate.
- `useEffect` — checks when not closed, not loading, no active prompt:
  - Gate, auto-memory enabled, not disabled, policy allowed, env not disabled.
  - Last assistant's UUID not seen → extract text, test `MEMORY_WORD_RE`.
  - If match found, mark UUID as seen, scan for memory file read.
  - If memory read confirmed, roll `Math.random() < 0.2` → `open()`.

---

### 13. `usePostCompactSurvey.tsx` (206 lines)

Hook for post-compaction survey (shown after session memory compaction).

**Exports:**
- `usePostCompactSurvey(messages, isLoading, hasActivePrompt?, { enabled? })`

**Constants:**
- `POST_COMPACT_SURVEY_GATE = 'tengu_post_compact_survey'`, `SURVEY_PROBABILITY = 0.2`.

**`hasMessageAfterBoundary(messages, boundaryUuid)`** — checks for user/assistant messages after a compact boundary.

**Logic:**
1. Evaluates gate via `checkStatsigFeatureGate_CACHED_MAY_BE_STALE`.
2. Tracks `seenCompactBoundaries` ref (Set of UUIDs), `pendingCompactBoundaryUuid`.
3. `useSurveyState` with only `onOpen`/`onSelect` (no transcript prompt).
4. `useEffect` — checks conditions (not closed, not loading, no prompt, gate enabled, not disabled).
5. If `pendingCompactBoundaryUuid` is set, waits for a message after that boundary → rolls probability → `open()`.
6. Otherwise finds new compact boundaries (not in `seenCompactBoundaries`) → sets latest as pending.

---

### 14. `useSurveyState.tsx` (100 lines)

State machine hook shared across all survey types.

**Exports:**
- `useSurveyState(options: UseSurveyStateOptions)`

**`UseSurveyStateOptions`:**
- `hideThanksAfterMs`, `onOpen`, `onSelect`, `shouldShowTranscriptPrompt?`, `onTranscriptPromptShown?`, `onTranscriptSelect?`.

**State:** `state: SurveyState = 'closed' | 'open' | 'thanks' | 'transcript_prompt' | 'submitting' | 'submitted'`, `lastResponse`.

**Actions:**
- `open()` — sets 'open', generates new `appearanceId` (via `randomUUID`), calls `onOpen`.
- `handleSelect(selected)` — sets response, fires `onSelect`. If dismissed → closed. If transcript prompt should show → 'transcript_prompt' state. Else → 'thanks' (auto-closes after `hideThanksAfterMs`).
- `handleTranscriptSelect(selected)` — 'yes' → 'submitting' → 'submitted' or 'thanks'. 'no'/'dont_ask_again' → 'thanks'.

**`showThanksThenClose`** — sets 'thanks', schedules 'closed' + clear lastResponse via `setTimeout`.
**`showSubmittedThenClose`** — sets 'submitted', schedules 'closed'.

---

### 15. `submitTranscriptShare.ts` (112 lines)

Submits session transcript to Anthropic's API for quality improvement.

**Exports:**
- `TranscriptShareTrigger = 'bad_feedback_survey' | 'good_feedback_survey' | 'frustration' | 'memory_survey'`
- `submitTranscriptShare(messages, trigger, appearanceId): Promise<TranscriptShareResult>`

**Logic:**
1. Normalizes messages for API.
2. Collects subagent transcripts via `extractAgentIdsFromMessages` + `loadSubagentTranscripts`.
3. Reads raw JSONL transcript file (size-guarded by `MAX_TRANSCRIPT_READ_BYTES`).
4. Redacts sensitive info via `redactSensitiveInfo`.
5. Authenticates via `checkAndRefreshOAuthTokenIfNeeded` + `getAuthHeaders`.
6. POSTs to `https://api.anthropic.com/api/claude_code_shared_session_transcripts` with 30s timeout.
7. Returns `{ success, transcriptId }`.

---

### 16. `useDebouncedDigitInput.ts` (82 lines)

Shared hook for detecting single-digit typed input with debounce.

**Exports:**
- `useDebouncedDigitInput<T>({ inputValue, setInputValue, isValidDigit, onDigit, enabled?, once?, debounceMs? })`

**Logic:**
- Compares `inputValue` against `initialInputValue` (captured at mount).
- If last character passes `isValidDigit`, strips it from input and schedules `onDigit` callback after `debounceMs` (default 400ms).
- `once` flag prevents retriggering.
- Uses `callbacksRef` pattern to avoid effect re-runs when callbacks change.
- Handles full-width digit normalization via `normalizeFullWidthDigits`.
- Cleans up timeout on unmount/re-render.

---

## Batch C: Hooks Configuration Menu (6 files)

### 17. `HooksConfigMenu.tsx` (578 lines)

Read-only browser for configured hooks with drill-down navigation.

**Exports:**
- `HooksConfigMenu(props: Props)`

**Props:** `toolNames: string[]`, `onExit: (result?, options?) => void`.

**`ModeState` — 4-level navigation:**
- `'select-event'` — choose a hook event.
- `'select-matcher'` — choose a matcher for an event (if event has matcher metadata).
- `'select-hook'` — choose a hook for an event+matcher.
- `'view-hook'` — view read-only hook details.

**State:**
- `modeState` — current navigation level + context.
- `disabledByPolicy` — whether all hooks are disabled by managed settings.
- `restrictedByPolicy` — whether `allowManagedHooksOnly` policy is active.

**Keybindings:** `'confirm:no'` (escape) bound differently per mode:
- select-event → exit.
- select-matcher → back to select-event.
- select-hook → back to previous view.
- view-hook → back to select-hook.

**Data derivation:**
- `combinedToolNames = [...toolNames, ...mcp.tools.map(t => t.name)]`.
- `hooksByEventAndMatcher` from `groupHooksByEventAndMatcher(appStateStore.getState(), combinedToolNames)`.
- `sortedMatchersForSelectedEvent` from `getSortedMatchersForEvent`.
- `hooksForSelectedMatcher` from `getHooksForMatcher`.
- `hookEventMetadata` from `getHookEventMetadata`.
- `hooksByEvent` and `totalHooksCount` computed by iterating `hooksByEventAndMatcher`.

**Disabled state:** Shows full-screen message "All hooks are currently disabled" with list of consequences and instructions to re-enable.

**Mode rendering:**
- `'select-event'` → `<SelectEventMode>`.
- `'select-matcher'` → `<SelectMatcherMode>`.
- `'select-hook'` → `<SelectHookMode>`.
- `'view-hook'` → `<ViewHookMode>`.

---

### 18. `PromptDialog.tsx` (90 lines)

Dialog displayed when a hook sends a prompt request to the user.

**Exports:**
- `PromptDialog(props: Props)`

**Props:** `title`, `toolInputSummary?`, `request: PromptRequest`, `onRespond`, `onAbort`.

**Logic:**
- Registers `'app:interrupt'` keybinding for abort.
- Maps `request.options` to `Select` options (label/value/description).
- Shows optional `toolInputSummary` as dim text in titleRight.
- Uses `<PermissionDialog>` with request message as subtitle.

---

### 19. `SelectEventMode.tsx` (127 lines)

Event selection view for the hooks menu.

**Exports:**
- `SelectEventMode(props: Props)`

**Props:** `hookEventMetadata`, `hooksByEvent`, `totalHooksCount`, `restrictedByPolicy`, `onSelectEvent`, `onCancel`.

**Layout:**
- Dialog title "Hooks" with subtitle "{count} hook(s) configured".
- If `restrictedByPolicy`, shows policy restriction warning with info icon.
- Read-only notice with link to docs.
- `<Select>` listing events with hook counts in parentheses and summary descriptions.

---

### 20. `SelectMatcherMode.tsx` (144 lines)

Matcher selection view for a chosen hook event.

**Exports:**
- `SelectMatcherMode(props: Props)`

**Props:** `selectedEvent`, `matchersForSelectedEvent`, `hooksByEventAndMatcher`, `eventDescription`, `onSelect`, `onCancel`.

**Logic:**
- Builds `matchersWithSources` — array of `{ matcher, sources: HookSource[], hookCount }` for each matcher.
- If no matchers, shows empty state with help text.
- Dialog title: "{Event} - Matchers".
- Options: `[{source}] {matcher}` with hook count description.

---

### 21. `SelectHookMode.tsx` (112 lines)

Hook list view for a given event+matcher pair.

**Exports:**
- `SelectHookMode(props: Props)`

**Props:** `selectedEvent`, `selectedMatcher`, `hooksForSelectedMatcher`, `hookEventMetadata`, `onSelect`, `onCancel`.

**Logic:**
- Title: "{Event} - Matcher: {name}" (if matcher metadata exists) or just "{Event}".
- If no hooks, shows empty state.
- Options: `[{config.type}] {displayText}` with source description.

---

### 22. `ViewHookMode.tsx` (199 lines)

Read-only detail view for a single hook configuration.

**Exports:**
- `ViewHookMode(props: Props)`

**Props:** `selectedHook`, `eventSupportsMatcher`, `onCancel`.

**Fields displayed:**
- **Event:** bold name.
- **Matcher:** bold matcher value or "(all)" (only if event supports matchers).
- **Type:** bold hook type.
- **Source:** dim description.
- **Plugin:** dim name (if applicable).
- **Content field:** Labeled box with the command/prompt/URL (depends on type).
- **Status message:** if present on config.

**Footer hint:** "To modify or remove this hook, edit settings.json directly or ask Claude to help."

**Helper functions:**
- `getContentFieldLabel(config)` — returns 'Command' | 'Prompt' | 'URL' based on type.
- `getContentFieldValue(config)` — returns `config.command` | `config.prompt` | `config.url`.

---

## Summary Data

| Subsystem | Files | Total Lines |
|-----------|-------|-------------|
| AskUserQuestionPermissionRequest | 7 | 2,148 |
| FilePermissionDialog | 5 | 820 |
| BashPermissionRequest | 2 | 629 |
| FileWritePermissionRequest | 2 | 250 |
| NotebookEditPermissionRequest | 2 | 401 |
| PowerShellPermissionRequest | 2 | 326 |
| ComputerUseApproval | 1 | 441 |
| **Batch A total** | **21** | **5,015** |
| FeedbackSurvey | 9 | 1,379 |
| Hooks Config Menu | 6 | 1,250 |
| **Grand Total** | **36** | **7,644** |
