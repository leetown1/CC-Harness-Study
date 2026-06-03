# Remaining UI Components — Part 2

> Gap-fill reference covering Agent Creation Wizard, HelpV2, StructuredDiff, Teams, Memory, Skills, and single-file components.

---

## Batch A: New Agent Creation Wizard

### A1. CreateAgentWizard.tsx (97 lines)

**Path:** `src/components/agents/new-agent-creation/CreateAgentWizard.tsx`

**Exports:** `CreateAgentWizard`

**Props:**
- `tools: Tools` — available tools registry
- `existingAgents: AgentDefinition[]` — list of already-defined agents for duplicate validation
- `onComplete: (message: string) => void` — called when wizard finishes successfully
- `onCancel: () => void` — called when wizard is dismissed

**Purpose:** Orchestrator that defines the step sequence and wraps everything in `WizardProvider<AgentWizardData>`.

**Step composition (in order):**
1. `LocationStep` — project vs. user scope
2. `MethodStep` — "generate with Claude" vs. "manual configuration"
3. `GenerateStep` — AI-powered agent description → generation (only if method === "generate")
4. `<TypeStep>` — name/identifier input (wrapped in closure passing `existingAgents`)
5. `PromptStep` — system prompt text entry
6. `DescriptionStep` — "when to use" description
7. `<ToolsStep>` — tool selection (wrapped in closure passing `tools`)
8. `ModelStep` — model picker
9. `ColorStep` — color assignment
10. `MemoryStep` — **only if `isAutoMemoryEnabled()`** (conditionally included)
11. `<ConfirmStepWrapper>` — final review + save (wrapped in closure passing all handlers)

**Key details:**
- Uses React compiler (`react/compiler-runtime`) with manual cache slots
- `WizardProvider` configured with `showStepCounter={false}` and empty initial data
- `_temp` is a no-op `onComplete` callback (actual completion handled inside ConfirmStepWrapper)
- Steps that need `tools` or `existingAgents` are created via inline closures to capture props

---

### A2. Wizard Step: TypeStep.tsx (103 lines)

**Path:** `src/components/agents/new-agent-creation/wizard-steps/TypeStep.tsx`

**Exports:** `TypeStep`

**Props:** `existingAgents: AgentDefinition[]`

**Purpose:** Collects the agent's unique identifier/name.

**Form Controls:**
- `TextInput` — single-line, 60 columns, placeholder `"e.g., test-runner, tech-lead, etc"`
- Keyboard shortcuts: ↑↓ navigate (if applicable), Enter to continue, Esc to go back

**State Management:**
- `agentType` (local state, initialized from `wizardData.agentType`)
- `error` (local state for validation messages)
- `cursorOffset` (local state for TextInput cursor tracking)
- `updateWizardData()` from `useWizard` to persist `agentType`

**Validation Logic:**
- `validateAgentType(trimmedValue)` validates the identifier (from `validateAgent.ts`)
- If invalid, sets `error` and blocks navigation
- If valid, clears error, updates wizard data, and calls `goNext()`

**Navigation/Transition:**
- `goBack()` bound to `confirm:no` keybinding with `Settings` context
- `handleSubmit` calls `goNext()` after validation passes

**Rendering:**
- `WizardDialogLayout` with subtitle "Agent type (identifier)"
- Footer: `Byline` with keyboard shortcut hints
- Error message shown in red `<Text>` below input

---

### A3. Wizard Step: MethodStep.tsx (80 lines)

**Path:** `src/components/agents/new-agent-creation/wizard-steps/MethodStep.tsx`

**Exports:** `MethodStep`

**Purpose:** Choose creation method — AI generation vs. manual config.

**Form Controls:**
- `Select` component with two options:
  - `"Generate with Claude (recommended)"` → value `"generate"`
  - `"Manual configuration"` → value `"manual"`

**State Management:**
- Updates `wizardData.method` and `wizardData.wasGenerated` via `updateWizardData()`

**Navigation/Transition:**
- "Generate" path: `goNext()` (advances to GenerateStep)
- "Manual" path: `goToStep(3)` (skips GenerateStep, lands on TypeStep)
- `goBack()` called on cancel

---

### A4. Wizard Step: GenerateStep.tsx (143 lines)

**Path:** `src/components/agents/new-agent-creation/wizard-steps/GenerateStep.tsx`

**Exports:** `GenerateStep`

**Purpose:** AI-powered agent generation from a natural language description.

**Form Controls:**
- `TextInput` — multi-line, 80 columns, placeholder `"e.g., Help me write unit tests for my code..."`
- External editor opening via `editPromptInEditor` (ctrl+g)

**State Management:**
- `prompt` (local, initialized from `wizardData.generationPrompt`)
- `isGenerating` (local boolean)
- `error` (local string | null)
- `cursorOffset` (local for cursor tracking)
- `abortControllerRef` — holds `AbortController` for cancellation
- `model` from `useMainLoopModel()`

**Validation Logic:**
- Empty prompt → `"Please describe what the agent should do"`

**Navigation/Transition:**
- "Generate" mode: Calls `generateAgent(trimmedPrompt, model, [], controller.signal)`
- On success: Updates wizard data with `agentType`, `whenToUse`, `systemPrompt`, `generatedAgent`, sets `wasGenerated: true`, then calls `goToStep(6)` (skips to ToolsStep)
- Cancel during generation: aborts controller, sets `isGenerating = false`, error `"Generation cancelled"`
- Escape when NOT generating: Resets all generated data, calls `goBack()`
- `confirm:no` keybinding context switches between `Settings` (to allow typing 'n') and active-only

**UI Dual State:**
- Loading: Shows `Spinner` + "Generating agent from description..."
- Idle: Shows text input + footer with submit/external editor/go-back hints

**Error Handling:**
- `APIUserAbortError` silently ignored (already handled by escape handler)
- Other errors shown inline

---

### A5. Wizard Step: PromptStep.tsx (128 lines)

**Path:** `src/components/agents/new-agent-creation/wizard-steps/PromptStep.tsx`

**Exports:** `PromptStep`

**Purpose:** Collect the system prompt for the agent.

**Form Controls:**
- `TextInput` — 80 columns, placeholder `"You are a helpful code reviewer who..."`
- External editor via `editPromptInEditor`

**State Management:**
- `systemPrompt` (local, initialized from `wizardData.systemPrompt`)
- `error` (local)
- `cursorOffset` (local)
- `updateWizardData()` persists `systemPrompt`

**Validation Logic:**
- Empty prompt → `"System prompt is required"`

**Navigation/Transition:**
- `confirm:no` keybinding with `Settings` context → `goBack()`
- `chat:externalEditor` → opens in editor
- Submit calls `goNext()`

**Rendering:**
- `WizardDialogLayout` subtitle: "System prompt"
- Shows "Be comprehensive for best results" hint above input

---

### A6. Wizard Step: DescriptionStep.tsx (123 lines)

**Path:** `src/components/agents/new-agent-creation/wizard-steps/DescriptionStep.tsx`

**Exports:** `DescriptionStep`

**Purpose:** Collect "when to use this agent" description.

**Form Controls:**
- `TextInput` — 80 columns, placeholder `"e.g., use this agent after you're done writing code..."`
- External editor via `editPromptInEditor`

**State Management:**
- `whenToUse` (local, initialized from `wizardData.whenToUse`)
- `error` (local)
- `cursorOffset` (local)

**Validation Logic:**
- Empty → `"Description is required"`

**Navigation/Transition:**
- `confirm:no` → `goBack()`
- `chat:externalEditor` → opens in editor
- Submit → `updateWizardData({ whenToUse })` → `goNext()`

---

### A7. Wizard Step: ToolsStep.tsx (61 lines)

**Path:** `src/components/agents/new-agent-creation/wizard-steps/ToolsStep.tsx`

**Exports:** `ToolsStep`

**Props:** `tools: Tools`

**Purpose:** Select which tools the agent can use.

**Form Controls:**
- `ToolSelector` component — multi-select tool picker
- Keyboard: Enter to toggle, ↑↓ to navigate, Esc to go back

**State Management:**
- `initialTools` derived from `wizardData.selectedTools` (preserves "all tools" semantics by passing undefined)
- `handleComplete` updates `wizardData.selectedTools`

**Navigation/Transition:**
- On complete → `goNext()`
- On cancel → `goBack()`

---

### A8. Wizard Step: ModelStep.tsx (52 lines)

**Path:** `src/components/agents/new-agent-creation/wizard-steps/ModelStep.tsx`

**Exports:** `ModelStep`

**Purpose:** Select the AI model for the agent.

**Form Controls:**
- `ModelSelector` component — model picker with `initialModel` and `onComplete`/`onCancel` callbacks

**State Management:**
- `handleComplete` updates `wizardData.selectedModel`

**Navigation/Transition:**
- Model selected → `goNext()`
- Cancel → `goBack()`

---

### A9. Wizard Step: ColorStep.tsx (84 lines)

**Path:** `src/components/agents/new-agent-creation/wizard-steps/ColorStep.tsx`

**Exports:** `ColorStep`

**Purpose:** Choose agent background color.

**Form Controls:**
- `ColorPicker` component — color selection grid
- ↑↓ navigate, Enter to select, Esc to go back

**State Management:**
- `handleConfirm` builds `finalAgent` object on the wizard data:
  ```ts
  {
    agentType, whenToUse, getSystemPrompt: () => systemPrompt,
    tools: selectedTools,
    ...(model ? { model } : {}),
    ...(color ? { color: color as AgentColorName } : {}),
    source: location
  }
  ```

**Navigation/Transition:**
- Color picked → `updateWizardData({ selectedColor, finalAgent })` → `goNext()`
- `confirm:no` → `goBack()`

---

### A10. Wizard Step: MemoryStep.tsx (113 lines)

**Path:** `src/components/agents/new-agent-creation/wizard-steps/MemoryStep.tsx`

**Exports:** `MemoryStep`

**Purpose:** Configure agent memory scope.

**Form Controls:**
- `Select` component with 4 options (order depends on `location`):
  - User scope: `{ label: "User scope (~/.claude/agent-memory/) (Recommended)", value: "user" }` (first if `location === "userSettings"`)
  - Project scope: `{ label: "Project scope (.claude/agent-memory/) (Recommended)", value: "project" }` (first if location !== userSettings)
  - Local scope: `{ label: "Local scope (.claude/agent-memory-local/)", value: "local" }`
  - None: `{ label: "None (no persistent memory)", value: "none" }`

**State Management:**
- `handleSelect` updates `selectedMemory` and `finalAgent.memory` on wizard data
- If `isAutoMemoryEnabled()` and memory is set, `getSystemPrompt` is augmented by appending `loadAgentMemoryPrompt(agentType, memory)`

**Navigation/Transition:**
- Selection made → `goNext()`
- `confirm:no` → `goBack()`

---

### A11. Wizard Step: ConfirmStep.tsx (378 lines)

**Path:** `src/components/agents/new-agent-creation/wizard-steps/ConfirmStep.tsx`

**Exports:** `ConfirmStep`

**Props:**
- `tools: Tools`
- `existingAgents: AgentDefinition[]`
- `onSave: () => void`
- `onSaveAndEdit: () => void`
- `error?: string | null`

**Purpose:** Final review with validation warnings/errors before saving.

**Displayed Fields:**
- Name (agent type)
- Location (computed file path via `getNewRelativeAgentFilePath`)
- Tools (formatted: "All tools", "None", "tool1 and tool2", "tool1, tool2, and tool3")
- Model (via `getAgentModelDisplay`)
- Memory (via `getMemoryScopeDisplay`, only if `isAutoMemoryEnabled()`)
- Description (whenToUse, truncated to 240 chars)
- System prompt (truncated to 240 chars)

**Validation:**
- `validateAgent(agent, tools, existingAgents)` returns `{ warnings: string[], errors: string[] }`
- Warnings shown dimmed with `•` prefix
- Errors shown in red with `•` prefix

**Input Handling:**
- `handleKeyDown` on the outer `Box`:
  - `s` or `return` → `onSave()`
  - `e` → `onSaveAndEdit()`
- `confirm:no` keybinding → `goBack()`

**Rendering:**
- `WizardDialogLayout` with subtitle "Confirm and save"
- Footer: "s/Enter to save · e to edit in your editor · Esc to cancel"
- Bottom hint: "Press **s** or **Enter** to save, **e** to save and edit"

**Helper functions:**
- `_temp(toolNames)` — formats tool list with natural language conjunctions
- `_temp2/warning, i)` — renders warning bullet
- `_temp3(err, i)` — renders error bullet

---

### A12. Wizard Step: ConfirmStepWrapper.tsx (74 lines)

**Path:** `src/components/agents/new-agent-creation/wizard-steps/ConfirmStepWrapper.tsx`

**Exports:** `ConfirmStepWrapper`

**Props:**
- `tools: Tools`
- `existingAgents: AgentDefinition[]`
- `onComplete: (message: string) => void`

**Purpose:** Orchestrates the save operation wrapping `ConfirmStep`.

**State Management:**
- `saveError` (local, `useState<string | null>`)
- `setAppState` from `useSetAppState()`

**Save Flow (`saveAgent`):**
1. Calls `saveAgentToFile(location!, agentType, whenToUse, tools, getSystemPrompt(), true, color, model, memory)` from `agentFileUtils.ts`
2. Updates AppState: appends new agent to `agentDefinitions.allAgents`, recalculates `activeAgents`
3. If `openInEditor`: calls `editFileInEditor(filePath)`
4. Logs analytics event `tengu_agent_created` with detailed metadata
5. Calls `onComplete(message)` with chalk-highlighted agent name
6. On error: sets `saveError`

**Event Metadata (analytics):**
- `agent_type`, `generation_method` (generated | manual), `source`
- `tool_count`, `has_custom_model`, `has_custom_color`, `has_memory`, `memory_scope`
- `opened_in_editor`

**Navigation/Transition:**
- `handleSave` → `saveAgent(false)` → `onComplete`
- `handleSaveAndEdit` → `saveAgent(true)` → `onComplete`

---

### A13. Wizard Step: ConfirmStep.tsx — Source map remains private (no additional exports)

Already covered in A11 above.

---

## Batch B: HelpV2 System

### B1. HelpV2.tsx (184 lines)

**Path:** `src/components/HelpV2/HelpV2.tsx`

**Exports:** `HelpV2`

**Props:**
- `onClose: (result?: string, options?: { display?: CommandResultDisplay }) => void`
- `commands: Command[]`

**Purpose:** Main help dialog with tabbed interface (General, Commands, Custom Commands).

**Layout:**
- Uses `useTerminalSize()` to calculate `maxHeight = Math.floor(rows / 2)`
- `Pane` with `color="professionalBlue"` containing a `Tabs` component

**Tab Structure:**
1. **General** — static `General` component
2. **commands** — `Commands` component with `builtinCommands` (filtered from `commands`, excluding hidden and non-builtin)
3. **custom-commands** — `Commands` component with `customCommands` (non-builtin, non-hidden)
4. **[ant-only]** (dead code behind `false &&`) — filtered `antOnlyCommands`

**State Management:**
- `close` handler calls `onClose("Help dialog dismissed", { display: "system" })`
- `exitState` from `useExitOnCtrlCDWithKeybindings(close)` for Ctrl+C/Ctrl+D exit
- `dismissShortcut` from `useShortcutDisplay("help:dismiss", "Help", "esc")`

**Keybindings:**
- `help:dismiss` → `close` (context: "Help")
- Ctrl+C/D exit via `useExitOnCtrlCDWithKeybindings`

**Rendering Details:**
- Version display: `Claude Code v${MACRO.VERSION}`
- Footer: "Press {keyName} again to exit" (pending) or "{dismissShortcut} to cancel"
- Help link: `https://code.claude.com/docs/en/overview`
- Tabs `defaultTab="general"`

---

### B2. Commands.tsx (82 lines)

**Path:** `src/components/HelpV2/Commands.tsx`

**Exports:** `Commands`

**Props:**
- `commands: Command[]`
- `maxHeight: number`
- `columns: number`
- `title: string`
- `onCancel: () => void`
- `emptyMessage?: string`

**Purpose:** Renders a filtered, sorted, deduplicated list of commands with descriptions.

**Data Processing:**
- Deduplicates commands by name using a `Set`
- Sorts alphabetically by `name`
- Maps each to `{ label: "/{name}", value: name, description: truncate(formatDescriptionWithSource(cmd), maxWidth) }`
- `maxWidth = Math.max(1, columns - 10)`
- `visibleCount = Math.max(1, Math.floor((maxHeight - 10) / 2))`

**Rendering:**
- If empty and `emptyMessage` set: shows dimmed empty message
- Otherwise: renders title + `Select` with `layout="compact-vertical"`, `disableSelection={true}`, `hideIndexes={true}`
- Integrates with `useTabHeaderFocus()` for Tabs navigation (up arrow from first item moves to tab header)

---

### B3. General.tsx (23 lines)

**Path:** `src/components/HelpV2/General.tsx`

**Exports:** `General`

**Purpose:** Static "General" help tab content.

**Content:**
- Description text: "Claude understands your codebase, makes edits with your permission, and executes commands — right from your terminal."
- "Shortcuts" section heading
- `PromptInputHelpMenu` with `gap={2}` and `fixedWidth={true}`

---

## Batch C: StructuredDiff

### C1. StructuredDiff.tsx (190 lines)

**Path:** `src/components/StructuredDiff.tsx`

**Exports:** `StructuredDiff` (memoized)

**Props:**
- `patch: StructuredPatchHunk`
- `dim: boolean`
- `filePath: string` — for language detection
- `firstLine: string | null` — for shebang detection
- `fileContent?: string` — full file content for syntax context
- `width: number`
- `skipHighlighting?: boolean`

**Purpose:** Renders syntax-highlighted diffs using the native `color-diff-napi` module when available, falling back to `StructuredDiffFallback`.

**Architecture:**
- Uses module-level `RENDER_CACHE` (`WeakMap<StructuredPatchHunk, Map<string, CachedRender>>`) to survive React unmount/remount cycles (e.g., ctrl+o in REPL)
- `CachedRender` stores pre-split gutter/content columns (2 RawAnsi elements vs. N individual DiffLine nodes)

**Rendering Strategy:**
1. If `skipHighlighting` or `settings.syntaxHighlightingDisabled`: falls through to `StructuredDiffFallback`
2. Calls `renderColorDiff()` which uses `expectColorDiff()` to get the ColorDiff class
3. If `ColorDiff` unavailable: falls back
4. If fullscreen enabled (`isFullscreenEnvEnabled()`): splits into gutter (`NoSelect<RawAnsi>`) + content (`RawAnsi`) columns
5. Without split: single `RawAnsi` for entire width

**Module-level Caching (`RENDER_CACHE`):**
- Outer key: `WeakMap` keyed by `patch` (auto-GC when patch is no longer referenced)
- Inner key: `Map` keyed by `"${theme}|${width}|${dim}|${gutterWidth}|${firstLine}|${filePath}"`
- Inner map capped at 4 entries (2 widths × dim on/off)
- Stores pre-computed `gutterWidth`, `gutters[]`, `contents[]`

**Helper Functions:**
- `computeGutterWidth(patch)`: `max(oldStart + oldLines - 1, newStart + newLines - 1, 1).toString().length + 3`
- `renderColorDiff(...)`: Instantiates `new ColorDiff(patch, firstLine, filePath, fileContent).render(theme, width, dim)`, pre-splits gutters via `sliceAnsi`

---

### C2. Fallback.tsx (487 lines)

**Path:** `src/components/StructuredDiff/Fallback.tsx`

**Exports:**
- `StructuredDiffFallback` (component)
- `LineObject` (interface / type)
- `transformLinesToObjects` (function)
- `processAdjacentLines` (function)
- `calculateWordDiffs` (function)
- `numberDiffLines` (function)

**Purpose:** Word-level diff highlighting fallback when color-diff-napi is unavailable.

**Processing Pipeline:**
1. `transformLinesToObjects(lines)` — converts +/- prefix lines to `{ code, type, i, originalCode }` objects
2. `processAdjacentLines(objects)` — groups adjacent remove/add pairs for word-level diffing; sets `wordDiff` and `matchedLine` on paired objects
3. `numberDiffLines(objects, startLine)` — assigns correct line numbers (removes re-use the removed line number)
4. `formatDiff(lines, startLine, width, dim, theme?)` — full pipeline orchestration:
   - For word-diff pairs: `generateWordDiffElements()` → word-level rendering or fallback to standard
   - Standard: wraps text, applies bg colors (`diffAdded`/`diffRemoved`/`diffAddedDimmed`/`diffRemovedDimmed`)

**Word-Level Diffing:**
- Uses `diffWordsWithSpace` from the `diff` library
- `generateWordDiffElements()` manually wraps content to available width
- `CHANGE_THRESHOLD = 0.4` — if change ratio exceeds 40%, falls back to standard line rendering
- Generator creates individual `<Text backgroundColor={bgColor}>` elements per word-diff part

**Color Scheme:**
- Add lines: `diffAdded` (green) bg
- Remove lines: `diffRemoved` (red) bg
- Dimmed variants: `diffAddedDimmed`, `diffRemovedDimmed`
- Gutter (line number + sigil) wrapped in `<NoSelect>` for clean text selection

---

### C3. colorDiff.ts (37 lines)

**Path:** `src/components/StructuredDiff/colorDiff.ts`

**Exports:**
- `ColorModuleUnavailableReason` (type: `'env'`)
- `getColorModuleUnavailableReason()` → `ColorModuleUnavailableReason | null`
- `expectColorDiff()` → `typeof ColorDiff | null`
- `expectColorFile()` → `typeof ColorFile | null`
- `getSyntaxTheme(themeName: string)` → `SyntaxTheme | null`

**Purpose:** Bridges the native `color-diff-napi` module, with env-var-based disable.

**Gating Logic:**
- `getColorModuleUnavailableReason()` checks `process.env.CLAUDE_CODE_SYNTAX_HIGHLIGHT`
- If env var is falsy (via `isEnvDefinedFalsy`), returns `'env'`
- All exports return `null` when unavailable

---

## Batch D: Teams + Memory + Skills

### D1. TeamsDialog.tsx (715 lines)

**Path:** `src/components/teams/TeamsDialog.tsx`

**Exports:** `TeamsDialog`

**Props:** `initialTeams?: TeamSummary[]`, `onDone: () => void`

**Purpose:** Full-featured teammate management dialog with list and detail views.

**Architecture:**
- Registers as overlay via `useRegisterOverlay('teams-dialog')`
- Two-level dialog state: `DialogLevel` union type of `teammateList` | `teammateDetail`
- Auto-refreshes every 1s via `useInterval`

**State Management:**
- `dialogLevel: DialogLevel` — current view (list vs. detail) and team/member names
- `selectedIndex: number` — current selection in list
- `refreshKey: number` — triggers re-fetch of teammate statuses
- `teammateStatuses` — `useMemo` calling `getTeammateStatuses(teamName)`, memoized on `[teamName, refreshKey]`
- `currentTeammate` — derived from `dialogLevel` and `teammateStatuses`
- `isBypassAvailable` from AppState for permission mode cycling

**Keybindings (raw `useInput`):**
- `leftArrow` — drill up from detail to list
- `upArrow/downArrow` — navigate selection (bounded by `getMaxIndex()`)
- `return` — drill into detail (list) or view output (detail)
- `k` — kill selected teammate (calls `killTeammate`)
- `s` — graceful shutdown via mailbox message
- `h` — toggle hide/show individual teammate (backend-gated)
- `H` — toggle hide/show all teammates (list view only)
- `p` — prune all idle teammates (list view only flow)

**Keybindings (`useKeybindings`):**
- `confirm:cycleMode` → `handleCycleMode()` (cycles permission modes)

**List View (`TeamDetailView`):**
- Shows `"Team {name}"` title with teammate count subtitle
- Empty state: "No teammates"
- Each `TeammateListItem`: mode symbol + color, `@name`, model info, hidden/idle indicators
- Selection pointer with `figures.pointer`
- Dims idle teammates when not selected
- Footer: full keyboard reference

**Detail View (`TeammateDetailView`):**
- Shows teammate name with agent color theme
- Subtitle: model + worktree path
- Mode cycling info
- Tasks section: fetched via `listTasks(teamName)`, filtered by `owner === agentId || owner === name`
- Prompt section: truncates to 80 chars, "p to expand" toggle
- Footer: back/kill/shutdown/hide/cycle-mode keyboard guide

**Helper Functions:**
- `killTeammate(...)` — kills pane via backend (`ensureBackendsRegistered` + `getBackendByType`), removes from team config, unassigns tasks, updates AppState, sends notification
- `viewTeammateOutput(paneId, backendType)` — focuses pane (iterm2: `session focus -s`, tmux: `select-pane -t` with swarm socket)
- `toggleTeammateVisibility(teammate, teamName)` — delegates to `showTeammate`/`hideTeammate` (currently no-ops for external builds)
- `hideTeammate/showTeammate` — stubs for anti-feature gating
- `sendModeChangeToTeammate(name, teamName, targetMode)` — writes to `config.json` via `setMemberMode` + sends mailbox message
- `cycleTeammateMode(teammate, teamName, isBypassAvailable)` — cycles single teammate's permission mode
- `cycleAllTeammateModes(teammates, teamName, isBypassAvailable)` — batch mode cycle; if modes differ, resets all to `default`; uses `setMultipleMemberModes` for atomic batch update

**Sub-components:**
- `TeamDetailView` — stateless list renderer
- `TeammateListItem` — single teammate row with mode symbol, name, model, status
- `TeammateDetailView` — full teammate detail with tasks and prompt

---

### D2. TeamStatus.tsx (80 lines)

**Path:** `src/components/teams/TeamStatus.tsx`

**Exports:** `TeamStatus`

**Props:** `teamsSelected: boolean`, `showHint: boolean`

**Purpose:** Footer status indicator showing teammate count (similar to `BackgroundTaskStatus`).

**State Management:**
- `teamContext` from `useAppState(s => s.teamContext)`
- `totalTeammates` computed as: `Object.values(teamContext.teammates).filter(t => t.name !== "team-lead").length`

**Rendering:**
- Returns `null` if `totalTeammates === 0`
- Shows `"{N} teammate(s)"` with `color="background"` and optional `inverse` when selected
- When `showHint && teamsSelected`: appends "· Enter to view" hint

---

### D3. MemoryFileSelector.tsx (438 lines)

**Path:** `src/components/memory/MemoryFileSelector.tsx`

**Exports:** `MemoryFileSelector`

**Props:** `onSelect: (path: string) => void`, `onCancel: () => void`

**Purpose:** File selector for memory files (CLAUDE.md, auto-memory, agent memory folders).

**Data Sources:**
- `existingMemoryFiles` via `use(getMemoryFiles())` — async list of memory files
- `userMemoryPath` — `~/.claude/CLAUDE.md`
- `projectMemoryPath` — `./CLAUDE.md`
- Agent definitions from AppState for agent memory folders

**File List Construction:**
1. Filters out `AutoMem` and `TeamMem` types from existing files
2. Adds non-existing user memory path as `"(new)"`
3. Adds non-existing project memory path as `"(new)"`
4. Builds nested tree using `parent` field with indentation
5. Labels: "User memory" / "Project memory" for root entries, otherwise display path
6. Descriptions: "Saved in ~/.claude/CLAUDE.md" / "Checked in at ./CLAUDE.md" / "@-imported" / "dynamically loaded"

**Folder Options (appended when `isAutoMemoryEnabled()`):**
- "Open auto-memory folder" (via `getAutoMemPath()`)
- "Open team memory folder" (gated by `feature('TEAMMEM')`)
- One entry per agent with memory: `"Open {name} agent memory"` (via `getAgentMemoryDir`)

**Toggle Controls (above the select):**
- **Auto-memory toggle**: Toggles `autoMemoryEnabled` in user settings, logs `tengu_auto_memory_toggled`
- **Auto-dream toggle**: Toggles `autoDreamEnabled` in user settings, shows dream status ("running", "never", "last ran {time}"), logs `tengu_auto_dream_toggled`
- Navigation between toggles and select via arrow keys
- Toggles highlighted via focus tracking

**Keybindings:**
- `confirm:no` → `onCancel` (context: "Confirmation")
- `confirm:yes` → toggle focused setting (context: "Confirmation", active only when toggle focused)
- `select:next/select:previous` → move between toggles (context: "Select")
- `useExitOnCtrlCDWithKeybindings()`

**Select Behavior:**
- `Select` with `defaultFocusValue` = last selected path
- `disabled` when toggle is focused
- "Open folder" entries (prefixed `OPEN_FOLDER_PREFIX`) call `mkdir` + `openPath` instead of selecting
- Normal entries call `onSelect(path)` and store in `lastSelectedPath`

---

### D4. MemoryUpdateNotification.tsx (45 lines)

**Path:** `src/components/memory/MemoryUpdateNotification.tsx`

**Exports:**
- `MemoryUpdateNotification` (component)
- `getRelativeMemoryPath(path: string): string` (function)

**Purpose:** Notification banner when a memory file is updated.

**`getRelativeMemoryPath`:**
- Calculates shortest relative path: `~` for home, `./` for cwd, falls back to absolute

**Rendering:**
- `"Memory updated in {displayPath} · /memory to edit"`

---

### D5. SkillsMenu.tsx (237 lines)

**Path:** `src/components/skills/SkillsMenu.tsx`

**Exports:** `SkillsMenu`

**Exported types:** (none directly — `SkillCommand` and `SkillSource` are module-private)

**Props:** `onExit: (result?, options?) => void`, `commands: Command[]`

**Purpose:** Dialog displaying all registered skills grouped by source.

**Architecture:**
- Filters commands to only `type === "prompt"` with source `"skills"`, `"commands_DEPRECATED"`, `"plugin"`, or `"mcp"`
- Groups by `source` into: `policySettings`, `userSettings`, `projectSettings`, `localSettings`, `flagSettings`, `plugin`, `mcp`
- Sorts each group alphabetically by command name

**Helpers:**
- `getSourceTitle(source)`: Returns formatted title (e.g., "Project settings skills", "Plugin skills", "MCP skills")
- `getSourceSubtitle(source, skills)`: MCP → server names joined; file-based → filesystem paths
- `renderSkill(skill)`: Shows command name + optional plugin name + `~{N} description tokens`

**Empty State:**
- "Create skills in .claude/skills/ or ~/.claude/skills/"
- `Dialog` with subtitle "No skills found"

**Rendering:**
- `Dialog` with title "Skills" and subtitle `"{N} skill(s)"`
- Output order: project settings → user settings → policy settings → plugin → MCP
- Each group: bold title + optional subtitle (paths/servers) + list of skills

---

## Batch E: Single-file Component Directories

### E1. PluginHintMenu.tsx (78 lines)

**Path:** `src/components/ClaudeCodeHint/PluginHintMenu.tsx`

**Exports:** `PluginHintMenu`

**Props:** `pluginName`, `pluginDescription?`, `marketplaceName`, `sourceCommand`, `onResponse: (response: 'yes' | 'no' | 'disable') => void`

**Purpose:** Dialog suggesting plugin installation from a CLI command hint.

**Auto-dismiss:** 30-second timer (`AUTO_DISMISS_MS = 30_000`), auto-responds `'no'`

**Options:**
- "Yes, install **{name}**" → `'yes'`
- "No" → `'no'`
- "No, and don't show plugin installation hints again" → `'disable'`

**Rendering:**
- `PermissionDialog` wrapped around plugin info + `Select`

---

### E2. DesktopUpsellStartup.tsx (171 lines)

**Path:** `src/components/DesktopUpsell/DesktopUpsellStartup.tsx`

**Exports:**
- `DesktopUpsellStartup` (component)
- `getDesktopUpsellConfig()` → `DesktopUpsellConfig`
- `shouldShowDesktopUpsellStartup()` → `boolean`

**Props:** `onDone: () => void`

**Purpose:** Startup dialog promoting Claude Code Desktop.

**Gating Logic (`shouldShowDesktopUpsellStartup`):**
- Platform check: `darwin` or `win32/x64`
- Config flag `enable_startup_dialog` from GrowthBook (`tengu_desktop_upsell`)
- Not previously dismissed (`config.desktopUpsellDismissed`)
- Seen fewer than 3 times (`config.desktopUpsellSeenCount < 3`)

**Seen-count Tracking:**
- `useEffect` on mount: increments `desktopUpsellSeenCount` in global config, logs `tengu_desktop_upsell_shown`

**Options:**
- "Open in Claude Code Desktop" → `'try'` (shows `DesktopHandoff`)
- "Not now" → `'not-now'` (closes)
- "Don't ask again" → `'never'` (sets `desktopUpsellDismissed: true`, closes)

**Rendering:**
- `PermissionDialog` with upsell text about visual diffs, live preview, parallel sessions
- Transitions to `DesktopHandoff` component when "try" is selected

---

### E3. Grove.tsx (463 lines)

**Path:** `src/components/grove/Grove.tsx`

**Exports:**
- `GroveDecision` (type: `'accept_opt_in' | 'accept_opt_out' | 'defer' | 'escape' | 'skip_rendering'`)
- `GroveDialog` (component)
- `PrivacySettingsDialog` (component)
- `GracePeriodContentBody` (component)
- `PostGracePeriodContentBody` (component)

**Props (`GroveDialog`):**
- `showIfAlreadyViewed: boolean`
- `location: 'settings' | 'policy_update_modal' | 'onboarding'`
- `onDone(decision: GroveDecision): void`

**Purpose:** "Grove" terms-of-service/policy update dialog with grace period handling.

**Architecture:**
- On mount: fetches `getGroveSettings()` + `getGroveNoticeConfig()` in parallel
- `calculateShouldShowGrove()` determines visibility
- Calls `markGroveNoticeViewed()` and logs `tengu_grove_policy_viewed`

**Content Body (gated by `config.notice_is_grace_period`):**
- `GracePeriodContentBody`: "An update to our Consumer Terms and Privacy Policy will take effect on October 8, 2025."
  - "Help improve Claude" section (opt-in for training data)
  - "Updates to data retention" section (5 years vs. 30 days)
- `PostGracePeriodContentBody`: "We've updated our Consumer Terms and Privacy Policy."
  - Same two topics with post-effective wording

**Options:**
- `"Accept terms · Help improve Claude: ON"` → `accept_opt_in` (calls `updateGroveSettings(true)`)
- `"Accept terms · Help improve Claude: OFF"` → `accept_opt_out` (calls `updateGroveSettings(false)`)
- If `domain_excluded`: only opt-out option shown
- Grace period: adds "Not now" → `defer`
- Escape: `escape` via `handleCancel`

**Rendering:**
- ASCII art box (`NEW_TERMS_ASCII`) of a filing cabinet labeled "NEW TERMS"
- `Dialog` with title "Updates to Consumer Terms and Policies"

---

**`PrivacySettingsDialog`** (inner component):
- Props: `settings: AccountSettings`, `domainExcluded?: boolean`, `onDone(): void`
- Shows "Help improve Claude" toggle (true/false display)
- Domain-excluded users see locked-false with note
- Logs `tengu_grove_privacy_settings_viewed`

---

### E4. HighlightedCode Fallback.tsx (193 lines)

**Path:** `src/components/HighlightedCode/Fallback.tsx`

**Exports:** `HighlightedCodeFallback` (component)

**Props:** `code: string`, `filePath: string`, `dim?: boolean`, `skipColoring?: boolean`

**Purpose:** Syntax-highlights code using CLI highlight utility, with Suspense fallback and module-level caching.

**Architecture:**
- Converts leading tabs to spaces
- If `skipColoring`: returns plain `<Ansi>` text
- Extracts language from `extname(filePath)`
- Falls back to `<Ansi>` text during loading (Suspense boundary)
- Uses `React.use()` with `getCliHighlightPromise()` promise

**Module-level Cache (`hlCache`):**
- `Map<string, string>` keyed by `hashPair(language, code)`
- Max 500 entries, LRU-eviction via `delete`+`set` on hit
- Survives unmount/remount cycles (unlike `useMemo`)

**`Highlighted` subcomponent:**
- Uses `use(promise)` for the highlight module
- Checks `hl.supportsLanguage(language)`
- On failure: falls back to "markdown" language
- Wraps result in `<Ansi>` for terminal rendering

---

### E5. LspRecommendationMenu.tsx (88 lines)

**Path:** `src/components/LspRecommendation/LspRecommendationMenu.tsx`

**Exports:** `LspRecommendationMenu`

**Props:** `pluginName`, `pluginDescription?`, `fileExtension`, `onResponse: (response: 'yes' | 'no' | 'never' | 'disable') => void`

**Purpose:** Dialog recommending LSP plugin installation.

**Auto-dismiss:** 30-second timer, auto-responds `'no'`

**Options:**
- "Yes, install **{name}**" → `'yes'`
- "No, not now" → `'no'`
- "Never for **{name}**" → `'never'`
- "Disable all LSP recommendations" → `'disable'`

**Rendering:**
- `PermissionDialog` with LSP explanation, plugin info, file extension trigger, and `Select`

---

### E6. reconnectHelpers.tsx (49 lines)

**Path:** `src/components/mcp/utils/reconnectHelpers.tsx`

**Exports:**
- `ReconnectResult` (interface: `{ message: string; success: boolean }`)
- `handleReconnectResult(result, serverName)` → `ReconnectResult`
- `handleReconnectError(error, serverName)` → `string`

**Purpose:** Utility functions for MCP server reconnection messaging.

**`handleReconnectResult`:**
- `connected` → `"Reconnected to {name}."` (success: true)
- `needs-auth` → `"{name} requires authentication. Use the 'Authenticate' option."` (success: false)
- `failed` → `"Failed to reconnect to {name}."` (success: false)
- default → `"Unknown result when reconnecting to {name}."` (success: false)

**`handleReconnectError`:**
- `"Error reconnecting to {name}: {errorMessage}"`

---

### E7. Passes.tsx (184 lines)

**Path:** `src/components/Passes/Passes.tsx`

**Exports:** `Passes`

**Props:** `onDone: (result?, options?) => void`

**Purpose:** Guest pass (referral) management dialog.

**Data Flow:**
1. On mount: `getCachedOrFetchPassesEligibility()` → checks eligibility
2. If eligible: `fetchReferralRedemptions(campaign)` → gets redemption data
3. Builds `PassStatus[]` — one entry per available pass (up to `maxRedemptions`, default 3)
4. Loading state: shaded spinner
5. Unavailable state: "Guest passes are not currently available."

**Display:**
- Header: "Guest passes · {N} left"
- ASCII art tickets: redeemed (dimmed with slashes) vs. available (highlighted with teardrop asterisk)
- Referral link: copied to clipboard on Enter
- Optional referrer reward info with dynamic support link
- Terms link based on reward presence

**Keybindings:**
- `Enter` → copies referral link to clipboard (if available)
- `confirm:no` → dismisses
- `useExitOnCtrlCDWithKeybindings()`
- Logs `tengu_guest_passes_link_copied` on copy
