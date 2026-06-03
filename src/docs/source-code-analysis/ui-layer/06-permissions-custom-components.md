# 06 - Permissions System & Custom UI Components

## Overview

This document provides a complete analysis of the permissions system and custom UI components. The permissions system is the backbone of the interactive experience -- it handles every tool-use approval, denial, and classification check that happens during a conversation. The custom UI components (Select, diff viewer, permission dialog) are the rendering layer that powers all terminal interactions.

---

## Part 1: Permission Hook System (`hooks/toolPermission/`)

### 1.1 PermissionContext.ts (379 lines)

**File**: `hooks/toolPermission/PermissionContext.ts`

**Primary function**: `createPermissionContext()`  
**Secondary function**: `createPermissionQueueOps()`, `createResolveOnce()`

#### Core Abstractions

| Type | Purpose |
|------|---------|
| `PermissionApprovalSource` | Discriminated union: `{type:'hook', permanent?}` `\|` `{type:'user', permanent}` `\|` `{type:'classifier'}` |
| `PermissionRejectionSource` | Discriminated union: `{type:'hook'}` `\|` `{type:'user_abort'}` `\|` `{type:'user_reject', hasFeedback}` |
| `PermissionQueueOps` | Generic interface for queue management: `push()`, `remove()`, `update()` -- decoupled from React |
| `ResolveOnce<T>` | Guards against multiple resolutions with atomic `claim()` |

#### `createResolveOnce()` State Machine
- **States**: `unresolved` → `claimed` → `delivered`
- `claim()` atomically transitions `unresolved` → `claimed` (returns true if winner)
- `resolve()` transitions to `delivered` (idempotent)
- Used to prevent race conditions in async permission flows

#### `createPermissionContext()` - Returned Methods

| Method | Description |
|--------|-------------|
| `logDecision(args, opts)` | Fans out to analytics/OTel/permission logging |
| `logCancelled()` | Logs `tengu_tool_use_cancelled` event |
| `persistPermissions(updates)` | Persists + applies permission updates to app state |
| `resolveIfAborted(resolve)` | Checks abort signal; if aborted, logs + resolves cancel |
| `cancelAndAbort(feedback, isAbort, contentBlocks)` | Builds cancel/deny decision; aborts controller |
| `tryClassifier(pendingCheck, updatedInput)` | Bash classifier auto-approval (feature-flagged) |
| `runHooks(mode, suggestions, updatedInput)` | Iterates PermissionRequest hooks; resolves on first decision |
| `buildAllow(input, opts)` | Constructs `PermissionAllowDecision` |
| `buildDeny(message, reason)` | Constructs `PermissionDenyDecision` |
| `handleUserAllow(input, updates, feedback)` | Persists permissions, logs, detects user-modified input |
| `handleHookAllow(input, updates)` | Persists permissions, logs hook-sourced allow |
| `pushToQueue(item)` | Pushes ToolUseConfirm to React confirm queue |
| `removeFromQueue()` | Removes current item from queue |
| `updateQueueItem(patch)` | Patches queue item fields |

#### `createPermissionQueueOps()` Bridge
Translates React's `setToolUseConfirmQueue` (setState dispatch) into the generic `PermissionQueueOps` interface:
- `push` → `setToolUseConfirmQueue(prev => [...prev, item])`
- `remove` → `filter by toolUseID`
- `update` → `map + spread patch`

---

### 1.2 permissionLogging.ts (220 lines)

**File**: `hooks/toolPermission/permissionLogging.ts`

#### Primary Function: `logPermissionDecision()`

Centralized analytics/telemetry for all tool permission decisions. Called after every approve/reject.

**Flow**:
1. Computes `waiting_for_user_permission_ms` from start time
2. Calls `logApprovalEvent()` or `logRejectionEvent()` based on decision
3. For code-editing tools (Edit, Write, NotebookEdit), enriches with language + updates OTel counter
4. Persists decision to `toolUseContext.toolDecisions` map
5. Logs to OTel event pipeline

#### Analytics Event Names

| Source | Accept Event | Reject Event |
|--------|-------------|-------------|
| `config` | `tengu_tool_use_granted_in_config` | `tengu_tool_use_denied_in_config` |
| `user` (permanent) | `tengu_tool_use_granted_in_prompt_permanent` | -- |
| `user` (temporary) | `tengu_tool_use_granted_in_prompt_temporary` | -- |
| `user_abort` | -- | `tengu_tool_use_rejected_in_prompt` |
| `user_reject` | -- | `tengu_tool_use_rejected_in_prompt` |
| `hook` | `tengu_tool_use_granted_by_permission_hook` | `tengu_tool_use_rejected_in_prompt` |
| `classifier` | `tengu_tool_use_granted_by_classifier` | -- |

#### Helper Functions
- `sourceToString()`: Flattens structured source to string label
- `baseMetadata()`: Common metadata (messageId, toolName, sandboxEnabled, waitMs)
- `isCodeEditingTool()`: Checks against `['Edit', 'Write', 'NotebookEdit']`
- `buildCodeEditToolAttributes()`: Derives language from file path for OTel

---

### 1.3 Handlers: coordinatorHandler.ts (59 lines)

**File**: `hooks/toolPermission/handlers/coordinatorHandler.ts`

#### Function: `handleCoordinatorPermission()`

Handles the coordinator worker permission flow. For coordinator workers, automated checks are awaited **sequentially** before falling through to interactive dialog:

1. **Try permission hooks** (fast, local)
2. **Try classifier** (slow, inference -- bash only)
3. **Return null** → caller falls through to interactive dialog

Error handling: catches exceptions from automated checks, logs them, and falls through to dialog so the user can decide manually.

---

### 1.4 Handlers: interactiveHandler.ts (506 lines)

**File**: `hooks/toolPermission/handlers/interactiveHandler.ts`

#### Function: `handleInteractivePermission()`

This is the **main permission handler** for interactive (non-swarm) sessions. It pushes a `ToolUseConfirm` entry to the confirm queue and sets up multiple racers that compete to resolve the permission.

**Setup at dialog push-time**:
- Creates `ResolveOnce` guard
- Sets `permissionPromptStartTimeMs` timestamp
- Pushes to confirm queue with callbacks: `onAbort`, `onAllow`, `onReject`, `recheckPermission`, `onUserInteraction`, `onDismissCheckmark`

**Callback: `onUserInteraction()`**
- 200ms grace period prevents accidental keypresses
- Sets `userInteracted = true` (prevents classifier from stealing focus)
- Clears classifier checking indicator

**Callback: `onAllow()`**
- Atomic `claim()` before await
- Sends bridge response to CCR if connected
- Calls `ctx.handleUserAllow()` for persistence + logging
- Resolves via `resolveOnce()`

**Callback: `onReject()`**
- Atomic `claim()`
- Sends bridge response
- Logs rejection event
- Resolves via `resolveOnce()`

**Callback: `recheckPermission()`**
- Re-runs `hasPermissionsToUseTool()` (e.g., after CCR-initiated mode switch)
- If now allowed, claims, cancels bridge, removes from queue, resolves

**After queue push, four automated racers are started:**

1. **Bridge** (lines 244-298): Sends permission request to CCR (claude.ai). All tools forwarded. Whichever side responds first wins via `claim()`.

2. **Channel** (lines 300-408): Sends permission prompt to every active MCP channel (Telegram, iMessage, etc.) via `CHANNEL_PERMISSION_REQUEST_METHOD` notification. Fire-and-forget; failure of any channel doesn't block other racers.

3. **PermissionRequest hooks** (lines 411-431): Executes async hooks. First hook decision that passes `claim()` wins.

4. **Bash classifier** (lines 433-530): Async classifier check for Bash commands. Features:
   - UI indicator for "classifier running"
   - On allow: shows checkmark transition (3s focused / 1s unfocused), updates queue item with `classifierAutoApproved`, sets classifier approval state
   - Classifier API errors logged but not propagated as interruptions

---

### 1.5 Handlers: swarmWorkerHandler.ts (142 lines)

**File**: `hooks/toolPermission/handlers/swarmWorkerHandler.ts`

#### Function: `handleSwarmWorkerPermission()`

Handles swarm worker permission flow. Returns `null` if swarms are not enabled or not a swarm worker.

**Flow for swarm workers**:
1. Try classifier auto-approval (agents await, not race)
2. Create permission request via `createPermissionRequest()`
3. Register callback via `registerPermissionCallback()` **before** sending (race condition prevention)
4. Send to leader via `sendPermissionRequestViaMailbox()`
5. Show visual indicator (`pendingWorkerRequest` in app state)
6. Return Promise that resolves when leader responds

**Callbacks**:
- `onAllow()`: atomic claim → clear pending → call `ctx.handleUserAllow()`
- `onReject()`: atomic claim → clear pending → log + cancel

**Abort handling**: If abort signal fires while waiting, claim resolves with cancel decision.

---

## Part 2: Permission UI Components (`components/permissions/`)

### 2.1 PermissionRequest.tsx (214 lines)

**File**: `components/permissions/PermissionRequest.tsx`

#### Function: `permissionComponentForTool()`
Routes tools to their specific permission component:

| Tool | Component |
|------|-----------|
| `FileEditTool` | `FileEditPermissionRequest` |
| `FileWriteTool` | `FileWritePermissionRequest` |
| `BashTool` | `BashPermissionRequest` |
| `PowerShellTool` | `PowerShellPermissionRequest` |
| `WebFetchTool` | `WebFetchPermissionRequest` |
| `NotebookEditTool` | `NotebookEditPermissionRequest` |
| `ExitPlanModeV2Tool` | `ExitPlanModePermissionRequest` |
| `EnterPlanModeTool` | `EnterPlanModePermissionRequest` |
| `SkillTool` | `SkillPermissionRequest` |
| `AskUserQuestionTool` | `AskUserQuestionPermissionRequest` |
| `GlobTool` / `GrepTool` / `FileReadTool` | `FilesystemPermissionRequest` |
| Feature-flagged (`ReviewArtifact`, `Workflow`, `Monitor`) | Respective component or `FallbackPermissionRequest` |
| Default | `FallbackPermissionRequest` |

#### Types

**`ToolUseConfirm<Input>`**: The queue entry object
```typescript
{
  assistantMessage, tool, description, input,
  toolUseContext, toolUseID, permissionResult,
  permissionPromptStartTimeMs,
  classifierCheckInProgress?, classifierAutoApproved?,
  classifierMatchedRule?, workerBadge?,
  onUserInteraction(), onAbort(), onDismissCheckmark?(),
  onAllow(updatedInput, permissionUpdates, feedback?, contentBlocks?),
  onReject(feedback?, contentBlocks?),
  recheckPermission()
}
```

**`PermissionRequestProps<Input>`**: Props for each specific permission component
```typescript
{
  toolUseConfirm, toolUseContext,
  onDone(), onReject(),
  verbose, workerBadge,
  setStickyFooter?(jsx | null)
}
```

#### Function: `getNotificationMessage()`
Returns OS notification message based on tool type.

#### Component: `PermissionRequest`
- Registers `app:interrupt` keybinding
- Uses `useNotifyAfterTimeout()` for OS notifications
- Selects the appropriate permission component via `permissionComponentForTool()`
- Renders it with all props forwarded

---

### 2.2 PermissionDialog.tsx (72 lines)

**File**: `components/permissions/PermissionDialog.tsx`

Standard dialog wrapper for permission requests.

**Props**:
- `title`: string
- `subtitle?`: ReactNode
- `color?`: Theme key (default: `"permission"`)
- `titleColor?`: Theme key
- `innerPaddingX?`: number (default: 1)
- `workerBadge?`: WorkerBadgeProps
- `titleRight?`: ReactNode
- `children`: ReactNode

**Renders**: `Box` with `borderStyle="round"`, `borderColor={color}`, top border only, marginTop 1. Header row with `PermissionRequestTitle` and optional `titleRight`. Children below.

---

### 2.3 PermissionPrompt.tsx (336 lines)

**File**: `components/permissions/PermissionPrompt.tsx`

Shared component for permission prompts with optional feedback input.

**Props**: `options[]`, `onSelect(value, feedback?)`, `onCancel?`, `question?`, `toolAnalyticsContext?`

**State machine** (8 state variables):
- `acceptFeedback` / `rejectFeedback`: Feedback text for accept/reject
- `acceptInputMode` / `rejectInputMode`: Whether input field is expanded
- `focusedValue`: Currently focused option value
- `acceptFeedbackModeEntered` / `rejectFeedbackModeEntered`: Track if user ever entered feedback mode (persists after collapse, used for analytics)

**Option types**: Each option has `value`, `label`, optional `feedbackConfig` (type: 'accept'|'reject', placeholder?), optional `keybinding`.

**Key behavior**:
- Tab toggles input mode for Yes/No options
- Input options auto-expand when focused and `feedbackConfig` is set
- Esc cancels with `logEvent('tengu_permission_request_escape')`
- Empty input submission cancels (unless `allowEmptySubmitToCancel`)
- Keybinding handlers registered for each option's keybinding

---

### 2.4 PermissionRequestTitle.tsx (66 lines)

**File**: `components/permissions/PermissionRequestTitle.tsx`

**Props**: `title`, `subtitle?`, `color?`, `workerBadge?`

Renders:
- Bold title with `permission` color
- Worker badge: `· @{name}` in dimmed text (if provided)
- Subtitle in dimmed text, `wrap="truncate-start"`

---

### 2.5 PermissionExplanation.tsx (272 lines)

**File**: `components/permissions/PermissionExplanation.tsx`

AI-generated explanation of why a tool needs permission. Uses React 19 `use()` to read promises with Suspense.

**Components**:
- `ShimmerLoadingText()`: Animated shimmer text "Loading explanation..."
- `usePermissionExplainerUI(props)`: Hook -- manages explainer state
  - Enabled via `isPermissionExplainerEnabled()`
  - Toggle with `Ctrl+E` (keybinding: `confirm:toggleExplanation`)
  - Lazily creates explanation promise (avoids token cost if never viewed)
- `ExplanationResult()`: Inner component using `use(promise)` -- suspends while loading
- `PermissionExplainerContent()`: Content component with Suspense + fallback

**Risk levels**: `LOW` → `success` green, `MEDIUM` → `warning` yellow, `HIGH` → `error` red.

---

### 2.6 PermissionRuleExplanation.tsx (121 lines)

**File**: `components/permissions/PermissionRuleExplanation.tsx`

Explains WHY a permission is being asked (the decision reason).

**Function**: `stringsForDecisionReason(reason, toolType)`

| Reason Type | Output Format |
|-------------|---------------|
| `classifier` | "Classifier **{name}** requires confirmation for this {toolType}." |
| `rule` | "Permission rule **{ruleValue}** requires confirmation for this {toolType}." + "/permissions to update rules" |
| `hook` | "Hook **{hookName}** requires confirmation for this {toolType}: {reason} [{source}]" + "/hooks to update" |
| `workingDir` | reason string + "/permissions to update rules" |
| `safetyCheck` / `other` | raw reason string |
| Auto-mode classifier | "Auto mode classifier requires confirmation..." with `error` color |

---

### 2.7 FallbackPermissionRequest.tsx (333 lines)

**File**: `components/permissions/FallbackPermissionRequest.tsx`

Fallback for tools without a specific permission component.

**Options**: `'yes'`, `'yes-dont-ask-again'` (conditional on `shouldShowAlwaysAllowOptions()`), `'no'`

**Key behavior**:
- Shows tool's `userFacingName`, rendered tool use message, and truncated description (3 lines)
- "Yes, don't ask again" persists to `localSettings`
- All selections logged via `logUnaryEvent()`

**State**: `userFacingName` (with/without MCP suffix), `originalCwd`, `showAlwaysAllowOptions`, `theme`

---

### 2.8 PermissionDecisionDebugInfo.tsx (460 lines)

**File**: `components/permissions/PermissionDecisionDebugInfo.tsx`

Debug overlay showing detailed permission decision information. Toggled via `permission:toggleDebug` keybinding.

**Components**:
- `PermissionDecisionInfoItem()`: Renders a single decision reason
  - `subcommandResults` type: renders per-subcommand results with icons (tick/cross)
  - Other types: renders via `decisionReasonDisplayString()`
- `SuggestedRules()`: Shows suggested permission rules
- `SuggestionDisplay()`: Shows suggestions, directories, and mode as labeled columns
- `PermissionDecisionDebugInfo()`: Main component
  - Shows Behavior, Message, Reason, Suggestions
  - Detects unreachable rules via `detectUnreachableRules()`
  - Warns about unreachable rules with fix suggestions

---

### 2.9 utils.ts (25 lines)

**File**: `components/permissions/utils.ts`

#### Function: `logUnaryPermissionEvent()`
Logs accept/reject events using `logUnaryEvent` with `completion_type`, `message_id`, `platform`, and `hasFeedback`.

---

### 2.10 hooks.ts (209 lines)

**File**: `components/permissions/hooks.ts`

#### Function: `usePermissionRequestLogging(toolUseConfirm, unaryEvent)`

**Key behaviors**:
1. Increments `permissionPromptCount` for attribution
2. Logs `tengu_tool_use_show_permission_request` analytics event
3. **ANT-ONLY**: If Bash tool with no "always allow" suggestions → logs internal event
4. **ANT-ONLY**: Parses Bash command input for internal logging
5. Logs unary completion event

**Dedup guard**: Uses `loggedToolUseID` ref to prevent re-firing on object reference changes (prevents infinite microtask loop).

**Helper**: `permissionResultToLog()` -- converts `PermissionResult` to human-readable string for logging.

---

### 2.11 WorkerBadge.tsx (49 lines)

**File**: `components/permissions/WorkerBadge.tsx`

**Props**: `name: string`, `color: string`

Renders a colored badge: `◉ @{name}` for swarm worker permission prompts. Uses `toInkColor()` for color conversion.

---

### 2.12 WorkerPendingPermission.tsx (105 lines)

**File**: `components/permissions/WorkerPendingPermission.tsx`

Visual indicator on workers while waiting for leader approval.

**Props**: `toolName: string`, `description: string`

**Renders**:
- Spinner with "Waiting for team lead approval" warning text
- Worker badge (agent name + color)
- Tool name and action description
- Team name notification

---

## Part 3: Tool-Specific Permission Request Components

### 3.1 BashPermissionRequest (471 lines + 143 lines)

**Files**:
- `BashPermissionRequest/BashPermissionRequest.tsx` (482 lines)
- `BashPermissionRequest/bashToolUseOptions.tsx` (147 lines)

#### BashPermissionRequest.tsx

**Subcomponents**:
- `ClassifierCheckingSubtitle()`: Isolated shimmer animation (separated from Inner to avoid re-rendering entire dialog at 20fps)

**Outer component**: `BashPermissionRequest`
- Parses Bash input from toolUseConfirm
- Detects sed edits → delegates to `SedEditPermissionRequest`
- Otherwise renders `BashPermissionRequestInner`

**Inner component**: `BashPermissionRequestInner`
- Uses `useShellPermissionFeedback()` for accept/reject feedback state
- Uses `usePermissionExplainerUI()` for Ctrl+E explainer
- Shows permission debug on Ctrl+D

**Editable prefix** (for "don't ask again" rule):
- Sync initializer: `getSimpleCommandPrefix()` or `getFirstWordPrefix()`
- Async refinement: `getCompoundCommandPrefixesStatic()` for compound commands
- For compound commands (`decisionReason.type === 'subcommandResults'`): uses backend suggestion as source of truth
- `hasUserEditedPrefix` ref prevents async result from overriding manual edits

**Classifier features** (ANT-ONLY):
- `classifierWasChecking`: Set from `toolUseConfirm.classifierCheckInProgress` at mount
- Classifier subtitle: auto-approved checkmark, loading shimmer, or "Requires manual approval"
- When auto-approved: options dimmed, Esc dismisses checkmark

**Options handling**: `onSelect(value)` dispatches to:
- `'yes'`: With optional feedback
- `'yes-apply-suggestions'`: Applies suggestions from permission result
- `'yes-prefix-edited'`: Editable prefix rule added to localSettings
- `'yes-classifier-reviewed'`: Classifier description rule added to session
- `'no'`: With optional feedback

#### bashToolUseOptions.tsx

**Function**: `bashToolUseOptions()` -- builds option array

**Options built**:
1. Yes (with input mode for feedback)
2. "Yes, and don't ask again for" (editable prefix or Haiku-generated suggestions)
3. "Yes, and don't ask again for" (classifier-reviewed, ANT-ONLY)
4. No (with input mode for feedback)

**Edge cases**: Skips classifier-reviewed option when initial description is empty, already exists in allow list, or decision reason is already a classifier block.

---

### 3.2 PowerShellPermissionRequest (231 lines + 91 lines)

**Files**:
- `PowerShellPermissionRequest/PowerShellPermissionRequest.tsx` (235 lines)
- `PowerShellPermissionRequest/powershellToolUseOptions.tsx` (91 lines)

Similar to BashPermissionRequest but simpler (no classifier, no shimmer):
- Editable prefix via `getCompoundCommandPrefixesStatic()`
- Multiline commands hide "don't ask again" option
- No sandbox toggle (not supported on Windows)
- Options: yes, yes-prefix-edited, yes-apply-suggestions, no

---

### 3.3 FileEditPermissionRequest (182 lines)

**File**: `FileEditPermissionRequest/FileEditPermissionRequest.tsx`

Wraps `FilePermissionDialog` with edit-specific configuration.

**IDE diff support**: `ideDiffSupport` with `createSingleEditDiffConfig()`:
- `getConfig`: Maps input to `{filePath, edits: [{old_string, new_string, replace_all}]}`
- `applyChanges`: Applies modified edits back to input

**Renders**: FilePermissionDialog with:
- Title: "Edit file"
- Subtitle: relative path
- Question: "Do you want to make this edit to `{basename}`?"
- Content: `FileEditToolDiff` component
- `completionType: "str_replace_single"`

---

### 3.4 FileWritePermissionRequest (161 lines + 89 lines)

**Files**:
- `FileWritePermissionRequest/FileWritePermissionRequest.tsx` (161 lines)
- `FileWritePermissionRequest/FileWriteToolDiff.tsx` (89 lines)

#### FileWritePermissionRequest
- Detects if file exists (reads old content) or is new file
- Title: "Overwrite file" or "Create file"
- `ideDiffSupport` reads file content from disk for diff config
- Renders `FileWriteToolDiff` as content

#### FileWriteToolDiff
- For existing files: Shows structured diff via `getPatchForDisplay()` + `StructuredDiff`
- For new files: Shows `HighlightedCode`
- Interspersed ellipsis between hunk groups

---

### 3.5 FilesystemPermissionRequest (115 lines)

**File**: `FilesystemPermissionRequest/FilesystemPermissionRequest.tsx`

Handles Glob, Grep, and FileRead tools.

**Path extraction**: `pathFromToolUse()` -- calls `tool.getPath()` if available
- Falls back to `FallbackPermissionRequest` if path is null
- Shows tool's `renderToolUseMessage()` as content
- Uses `FilePermissionDialog` with `operationType: "read"|"write"`

---

### 3.6 WebFetchPermissionRequest (258 lines)

**File**: `WebFetchPermissionRequest/WebFetchPermissionRequest.tsx`

**Options**: Yes, Yes (don't ask again for domain), No (with feedback).

**Domain extraction**: `inputToPermissionRuleContent()` extracts hostname from URL → `domain:{hostname}` rule content.

**No feedback input mode** (unlike other permission requests -- feedback is pre-composed in the "No" label: "No, and tell Claude what to do differently").

---

### 3.7 SkillPermissionRequest (369 lines)

**File**: `SkillPermissionRequest/SkillPermissionRequest.tsx`

**Options**:
- Yes (with feedback input)
- Yes, don't ask again for this exact skill (`yes-exact`)
- Yes, don't ask again for skill prefix (`yes-prefix`) -- shown when skill name contains space (e.g., "git commit")
- No (with feedback input)

**Always-don't-ask handling**: Persists rules to `localSettings` with `SKILL_TOOL_NAME`.

---

### 3.8 SedEditPermissionRequest (230 lines)

**File**: `SedEditPermissionRequest/SedEditPermissionRequest.tsx`

Handles Bash sed edit commands detected by `parseSedEditCommand()`.

**Flow**:
1. Reads file asynchronously → `contentPromise` (via `Suspense`)
2. `SedEditPermissionRequestInner` uses `use(contentPromise)` for file content
3. Applies sed substitution via `applySedSubstitution()`
4. Shows diff via `FileEditToolDiff` or "Pattern did not match" / "File does not exist"

**parseInput**: Wraps Bash input with `_simulatedSedEdit` metadata for IDE diff integration.

---

### 3.9 EnterPlanModePermissionRequest (122 lines)

**File**: `EnterPlanModePermissionRequest/EnterPlanModePermissionRequest.tsx`

**Options**: "Yes, enter plan mode" or "No, start implementing now"

**On accept**: Calls `handlePlanModeTransition()` + `setMode` to `"plan"`. Logs `tengu_plan_enter`.

**Display**: Shows plan mode description with dimmed text explaining the benefits.

---

### 3.10 ExitPlanModePermissionRequest (739 lines)

**File**: `ExitPlanModePermissionRequest/ExitPlanModePermissionRequest.tsx`

The most complex permission request component. Handles exiting plan mode with multiple permission modes.

**Options** (built by `buildPlanApprovalOptions()`):
1. Yes, clear context + elevated mode (auto/bp/edits) -- with context usage %
2. Yes, keep context + elevated mode
3. Yes, manually approve edits
4. Ultraplan (feature-flagged)
5. No, keep planning (input mode for feedback)

**Key features**:
- **Sticky footer**: When `setStickyFooter` is provided, options render in bottom slot for fullscreen mode
- **Ctrl+G**: Edit plan in external editor (in-place for V2 with plan file, prompt editor for V1)
- **Shift+Tab**: Quick "auto-accept edits" shortcut
- **Image paste**: Supports pasting images as feedback
- **Auto-name**: Names the session from plan content on accept (fire-and-forget)
- **Auto-mode integration**: Restores dangerous permissions, handles auto mode exit attachment
- **V1/V2 detection**: Uses tool name (`EXIT_PLAN_MODE_V2_TOOL_NAME`) to detect version

**`handleResponse(value)` state machine**:
- `ultraplan`: Reject locally, teleport plan to CCR as seed draft
- Clear-context options: Set `initialMessage`, call `setHasExitedPlanMode(true)`, reject dialog
- Keep-context options: Set mode, call `onAllow` with permission updates + `buildPermissionUpdates()`
- Auto keep-context: Set mode directly via `setAppState`, strip dangerous permissions
- `no`: Reject with feedback and optional image attachments

**`autoNameSessionFromPlan()`**: Generates session name from plan content (first 1000 chars), saves to disk with `saveCustomTitle()` + `saveAgentName()`.

---

### 3.11 SandboxPermissionRequest.tsx (163 lines)

**File**: `components/permissions/SandboxPermissionRequest.tsx`

Network request outside sandbox permission dialog.

**Props**: `hostPattern`, `onUserResponse({allow, persistToSettings})`

**Options**: Yes, Yes (don't ask again -- hidden when `shouldAllowManagedSandboxDomainsOnly`), No

---

### 3.12 ComputerUseApproval.tsx (441 lines)

**File**: `components/permissions/ComputerUseApproval/ComputerUseApproval.tsx`

Two-panel dispatcher for macOS Computer Use permissions.

**Panel 1 - TCC Panel** (`ComputerUseTccPanel`):
- Shown when `request.tccState` is present
- Checks Accessibility and Screen Recording permissions
- Options: Open System Settings → Accessibility, Open System Settings → Screen Recording, Try again
- Uses `execFileNoThrow('open', [...])` to open System Settings

**Panel 2 - App Allowlist Panel** (`ComputerUseAppListPanel`):
- Shows list of apps Claude wants to control
- Sentinel warnings: shell apps = "equivalent to shell access", filesystem = "can read/write any file", system_settings = "can change system settings"
- Options: Allow for session (N apps), Deny with feedback
- Handles clipboard read/write and system key combo flags
- Shows hidden app count

**Explanatory callout**: `DENY_ALL_RESPONSE` constant used when denying all.

---

## Part 4: FilePermissionDialog System

**Directory**: `components/permissions/FilePermissionDialog/` (5 files)

### 4.1 FilePermissionDialog.tsx (204 lines)

**File**: `FilePermissionDialog/FilePermissionDialog.tsx`

Generic dialog for file operations (used by FileEdit, FileWrite, SedEdit, Filesystem).

**Props**: `toolUseConfirm`, `toolUseContext`, `onDone`, `onReject`, `title`, `subtitle?`, `question?`, `content?`, `completionType?`, `languageName?`, `path`, `parseInput`, `operationType?`, `ideDiffSupport?`, `workerBadge`

**Features**:
- Language detection from path (for analytics)
- Symlink detection (warns if target is outside working directory)
- IDE diff integration: Opens diff in external IDE, shows `ShowInIDEPrompt` while open
- `onChange()` handles option selection, closes IDE tab first

### 4.2 ideDiffConfig.ts (42 lines)

**File**: `FilePermissionDialog/ideDiffConfig.ts`

Types and factory for IDE diff integration:

- `FileEdit {old_string, new_string, replace_all?}`
- `IDEDiffConfig {filePath, edits?, editMode?}`
- `IDEDiffSupport<TInput> {getConfig, applyChanges}`
- `createSingleEditDiffConfig(filePath, oldString, newString, replaceAll?)`

### 4.3 permissionOptions.tsx (177 lines)

**File**: `FilePermissionDialog/permissionOptions.tsx`

**Function**: `getFilePermissionOptions()`

Builds option list for file permission dialogs based on context:

| Option Type | Description |
|-------------|-------------|
| `'accept-once'` | Yes (with optional feedback input) |
| `'accept-session'` | Yes, allow all edits/reads during this session |
| `'reject'` | No (with optional feedback input) |

**Special cases**:
- `.claude/` folder paths: Show "allow Claude to edit its own settings" instead of generic session option
- AllowManagedPermissionRulesOnly: Session options always shown (memory-only, no persistence)
- Path inside/outside working directory: Different labels with directory name
- Read operations: Simplified labels without mode cycle shortcut

### 4.4 useFilePermissionDialog.ts (212 lines)

**File**: `FilePermissionDialog/useFilePermissionDialog.ts`

React hook managing file permission dialog state.

**State**: `acceptFeedback`, `rejectFeedback`, `focusedOption`, `yesInputMode`, `noInputMode`, `yesFeedbackModeEntered`, `noFeedbackModeEntered`

**Key behavior**:
- `onChange()`: Dispatches to `PERMISSION_HANDLERS` based on option type, overriding `toolUseConfirm.onAllow` to pass parsed input
- `handleCycleMode`: Keybinding handler for `confirm:cycleMode` (selects accept-session option)
- `handleInputModeToggle`: Tab key toggling with analytics events
- `handleFocusedOptionChange`: Resets input mode when navigating away (if no text typed)

### 4.5 usePermissionHandler.ts (185 lines)

**File**: `FilePermissionDialog/usePermissionHandler.ts`

Three permission handler functions:

1. **`handleAcceptOnce()`**: Logs accept event, calls `onAllow` with empty permission updates + optional feedback
2. **`handleAcceptSession()`**:
   - For `.claude-folder` scope: Creates session-level rule with `CLAUDE_FOLDER_PERMISSION_PATTERN` or `GLOBAL_CLAUDE_FOLDER_PERMISSION_PATTERN`
   - Otherwise: Generates suggestions from path via `generateSuggestions()`
3. **`handleReject()`**: Logs reject event, calls `onReject` with optional feedback

**Exported**: `PERMISSION_HANDLERS` record mapping option types to handlers.

---

## Part 5: Permission Rules UI (`components/permissions/rules/`)

### 5.1 PermissionRuleList.tsx (1175 lines)

**File**: `components/permissions/rules/PermissionRuleList.tsx`

Main permission rules management page accessible via `/permissions` command.

**Tabs**: `'recent'`, `'allow'`, `'ask'`, `'deny'`, `'workspace'`

**Subcomponents**:
- `RuleSourceText()`: Shows "From {source}" for rules
- `RuleDetails()`: Shows rule details, handles interactive deletion workflow
- `getRuleBehaviorLabel()`: Maps behavior to display label

**Key features**:
- SearchBox for filtering rules
- Tabs component with `useTabHeaderFocus()`
- Delete confirmation workflow with `useExitOnCtrlCDWithKeybindings()`
- Sort, filter, and display of allow/ask/deny rules
- Unreachable rule detection and warnings

### 5.2 AddPermissionRules.tsx (180 lines)

**File**: `components/permissions/rules/AddPermissionRules.tsx`

Save destination selection dialog for adding permission rules.

**Destinations**: `localSettings` (project local), `projectSettings` (checked in), `userSettings` (global)

**Function**: `optionForPermissionSaveDestination()` -- maps destination to display label with file path.

**On select**: Applies + persists permission update, detects unreachable rules, calls `onAddRules` with `UnreachableRule[]`.

### 5.3 PermissionRuleInput.tsx (138 lines)

**File**: `components/permissions/rules/PermissionRuleInput.tsx`

Text input for entering a permission rule manually.

**Props**: `onCancel`, `onSubmit(ruleValue, ruleBehavior)`, `ruleBehavior`

**Function**: Parses input via `permissionRuleValueFromString()` and validates.

**Help text**: Shows examples like `WebFetch`, `Bash(ls:*)`.

### 5.4 PermissionRuleDescription.tsx (76 lines)

**File**: `components/permissions/rules/PermissionRuleDescription.tsx`

Describes what a permission rule covers in human-readable text.

**Bash rules**: 
- `{prefix}:*` → "Any Bash command starting with **{prefix}**"
- `{exact}` → "The Bash command **{exact}**"
- No content → "Any Bash command"

**Other tools**: "Any use of the **{toolName}** tool"

### 5.5 AddWorkspaceDirectory.tsx (340 lines)

**File**: `components/permissions/rules/AddWorkspaceDirectory.tsx`

Dialog for adding a directory to the workspace.

**Two modes**:
1. **Directory input mode**: Text input with autocomplete suggestions (debounced 100ms fetch from `getDirectoryCompletions()`)
2. **Confirmation mode**: When `directoryPath` is provided (from prompt-based suggestion)

**Keyboard handling**: Tab to apply suggestion, Enter to submit, Up/Down to navigate suggestions.

**Remember options**: `yes-session` (session only), `yes-remember` (persist), `no`

### 5.6 RemoveWorkspaceDirectory.tsx (110 lines)

**File**: `components/permissions/rules/RemoveWorkspaceDirectory.tsx`

Confirmation dialog for removing a workspace directory.

**Action**: `applyPermissionUpdate` with `type: 'removeDirectories'` to session context.

### 5.7 WorkspaceTab.tsx (150 lines)

**File**: `components/permissions/rules/WorkspaceTab.tsx`

Shows list of additional working directories with add/remove options.

**Features**:
- Lists original working directory (dimmed, non-deletable)
- Lists additional directories (deletable)
- "Add directory..." option
- Up navigation to tab header via `focusHeader`
- Max 10 visible options

### 5.8 RecentDenialsTab.tsx (207 lines)

**File**: `components/permissions/rules/RecentDenialsTab.tsx`

Shows recent auto-mode classifier denials with approval/retry capability.

**State**: 
- `denials`: From `getAutoModeDenials()`
- `approved`: Set of approved indices
- `retry`: Set of retry indices
- `focusedIdx`: Currently focused denial

**Key 'r'** toggles retry mode for focused item (auto-approves it).

---

## Part 6: Diff Viewer Components (`components/diff/`)

### 6.1 DiffDialog.tsx (383 lines)

**File**: `components/diff/DiffDialog.tsx`

Full diff viewer dialog with source selection, file list, and detail navigation.

**View modes**: `'list'` (file selector) → `'detail'` (diff per file)

**Sources**: Current working tree changes + per-turn diffs from conversation.

**State**: `viewMode`, `selectedIndex`, `sourceIndex`

**Keybindings**:
- `diff:previousSource` / `diff:nextSource`: Cycle between sources
- `diff:back`: Return to list view
- `diff:viewDetails`: Enter detail view
- `diff:previousFile` / `diff:nextFile`: Navigate files
- Escape: dismiss

**Pagination**: Source selector shows dots between turn numbers, arrow indicators for prev/next.

**Empty states**: "Loading diff...", "No file changes in this turn", "Working tree is clean", "Too many files to display details"

### 6.2 DiffDetailView.tsx (280 lines)

**File**: `components/diff/DiffDetailView.tsx`

Displays diff content for a single file using `StructuredDiff` for word-level diffing.

**Special file states**:
- **Untracked**: Shows "New file not yet staged. Run `git add {path}`"
- **Binary**: "Binary file - cannot display diff"
- **Large file**: "Large file - diff exceeds 1 MB limit"
- **Truncated**: "diff truncated (exceeded 400 line limit)"

**Normal display**: File path header, `StructuredDiff` per hunk, truncation footer.

### 6.3 DiffFileList.tsx (292 lines)

**File**: `components/diff/DiffFileList.tsx`

Scrollable file list with pagination (max 5 visible files).

**Subcomponents**:
- `FileItem()`: Shows truncated path + stats (`+N -M`)
- `FileStats()`: Shows file status (untracked, binary, large file, or line counts)

**Pagination**: "↑ N more files" / "↓ N more files" indicators. Selected file highlighted with inverse color.

---

## Part 7: CustomSelect Components (`components/CustomSelect/`)

### 7.1 select.tsx (690 lines)

**File**: `components/CustomSelect/select.tsx`

The primary Select component used throughout the permission system.

**`OptionWithDescription<T>` type** (discriminated union):
- `{type?: 'text', label, value, description?, dimDescription?, disabled?}`
- `{type: 'input', label, value, onChange, placeholder?, initialValue?, allowEmptySubmitToCancel?, showLabelWithValue?, labelValueSeparator?, resetCursorOnUpdate?}`

**`SelectProps<T>`**: ~25 configurable props including `isDisabled`, `disableSelection`, `hideIndexes`, `visibleOptionCount`, `highlightText`, `layout` ('compact'|'expanded'|'compact-vertical'), `inlineDescriptions`, `onUpFromFirstItem`, `onDownFromLastItem`, `onInputModeToggle`, `onOpenEditor`, `onImagePaste`, `pastedContents`, `onRemoveImage`.

**Three layout modes**:
1. **`compact`** (default): Single line per option, index + label + description
2. **`expanded`**: Multiple lines per option, empty line separator
3. **`compact-vertical`**: Compact indexes with descriptions below

**Input options**: Rendered via `SelectInputOption`, support:
- External editor (Ctrl+G)
- Image paste
- Label display modes (showLabel)
- Cursor position management

**Non-input options**: Rendered via `SelectOption`, support:
- Text highlighting
- Description display (inline or separate column)
- Disabled state (dimmed)

**State management**: Uses `useSelectState` + `useSelectInput` hooks. Input values tracked in `Map<value, string>`. Initial values auto-sync when options change.

### 7.2 SelectMulti.tsx (213 lines)

**File**: `components/CustomSelect/SelectMulti.tsx`

Multi-select variant with checkbox-style selection.

**Props**: Additional `submitButtonText`, `onSubmit`, `initialFocusLast`

**Selection**: Space toggles selection. Each option shows `[✓]` or `[ ]` prefix.

**Submit button**: When `submitButtonText` is set, navigation includes a submit button at the end.

**State**: Uses `useMultiSelectState` which manages `selectedValues[]`, `isSubmitFocused`, and `inputValues` map.

### 7.3 select-option.tsx (68 lines)

**File**: `components/CustomSelect/select-option.tsx`

Thin wrapper around `ListItem` for rendering a select option.

**Props**: `isFocused`, `isSelected`, `children`, `description?`, `shouldShowDownArrow?`, `shouldShowUpArrow?`, `declareCursor?`

### 7.4 select-input-option.tsx (488 lines)

**File**: `components/CustomSelect/select-input-option.tsx`

Input-type option with built-in `TextInput`, image attachment support, and external editor integration.

**Keybindings**:
- `chat:externalEditor` (Ctrl+G): Opens value in external editor
- `chat:imagePaste` (Ctrl+V with image): Pastes clipboard image
- `attachments:remove`: Removes last pasted image
- `attachments:next` / `attachments:previous`: Navigate images (when `imagesSelected`)
- `attachments:exit`: Exit image selection mode

**Image selection mode**: When images exist and user presses down arrow on empty input, enters image selection. Images show as clickable refs. Navigation via arrow keys; remove via backspace; exit via esc.

**Cursor management**: `resetCursorOnUpdate` option auto-resets cursor to end of line when value changes or option becomes focused.

**Two display modes**:
- `showLabel = true`: Shows label before input field (with customizable separator)
- `showLabel = false`: Uses label as placeholder when input is empty

### 7.5 use-select-state.ts (157 lines)

**File**: `components/CustomSelect/use-select-state.ts`

Lightweight hook wrapping `useSelectNavigation` with value selection.

**State**: `value` (selected), `selectFocusedOption()` callback

### 7.6 use-multi-select-state.ts (414 lines)

**File**: `components/CustomSelect/use-multi-select-state.ts`

Full multi-select state management with keyboard input handling.

**State**: `selectedValues`, `isSubmitFocused`, `inputValues` (Map).

**Keyboard input** (via `useInput()`):
- Tab / Shift+Tab: Navigate between options and submit button
- Arrow keys / Ctrl+N/P / j/k: Navigate options
- PageUp/PageDown: Page navigation
- Enter: Submit (or toggle if no submit button)
- Space: Toggle selection
- Number keys (1-9): Direct selection by index (when `hideIndexes` is false)
- Escape: Cancel

**Input option handling**: In input mode, only navigation keys are intercepted; all others pass through to `TextInput`.

**Options reset**: When options change (deep comparison via `isDeepStrictEqual`), selected values reset to `defaultValue`.

### 7.7 use-select-input.ts (287 lines)

**File**: `components/CustomSelect/use-select-input.ts`

Keyboard input handling for single-select components.

**Hybrid approach**: Uses both `useKeybindings` (for select:next/previous/accept/cancel) and `useInput` (for remaining keys).

**Keybindings** (when not in input mode):
- `select:next` / `select:previous`: Navigation
- `select:accept`: Enter to select
- `select:cancel`: Escape to cancel

**useInput handlers**:
- Tab: Toggle input mode
- Arrow keys in input mode: Navigate options (and potentially enter image selection)
- PageUp/PageDown: Page navigation
- Number keys: Direct selection (suppressed in input mode by `disableSelection`)
- Space: Multi-select toggle

**Overlay registration**: Registers as 'select' overlay to prevent CancelRequestHandler from intercepting Escape.

### 7.8 use-select-navigation.ts (653 lines)

**File**: `components/CustomSelect/use-select-navigation.ts`

Core navigation state machine using `useReducer`.

**Reducer actions**: `focus-next-option`, `focus-previous-option`, `focus-next-page`, `focus-previous-page`, `set-focus`, `reset`

**Navigation algorithms**:
- **Next option**: Uses `optionMap` linked list. If at end, wraps to first (resetting viewport). Otherwise scrolls viewport by 1 if needed.
- **Previous option**: Mirrors next but in reverse.
- **Next/Previous page**: Moves by `visibleOptionCount` items, updates viewport.
- **Set focus**: Scrolls viewport to include target item (minimal scrolling -- puts item at edge).

**Viewport management**: `visibleFromIndex` / `visibleToIndex` define the visible range. Viewport auto-scrolls when focused item moves outside.

**Options reset**: When options change (deep comparison), state is reset via `createDefaultState()` preserving current viewport position when possible.

**Focus validation**: `validatedFocusedValue` computed to handle stale focused values when options list changes.

### 7.9 option-map.ts (50 lines)

**File**: `components/CustomSelect/option-map.ts`

`OptionMap<T>` class extending `Map<T, OptionMapItem<T>>`.

**Properties**: `first`, `last` -- reference to first and last items.

**Items**: Doubly-linked list with `previous`, `next`, `index` properties. Built during construction from options array.

### 7.10 index.ts (3 lines)

**File**: `components/CustomSelect/index.ts`

Re-exports: `SelectMulti`, `OptionWithDescription` type, and everything from `select.tsx`.

---

## Architecture Summary

### Permission Flow

```
User asks Claude → Tool wants to execute
  → hasPermissionsToUseTool() → PermissionResult
    → behavior: 'allow' → execute directly
    → behavior: 'deny' → reject with message
    → behavior: 'ask' → show permission dialog
      → createPermissionContext()
      → handleInteractivePermission() / handleCoordinatorPermission() / handleSwarmWorkerPermission()
        → Push to confirm queue
        → Race: [hooks, classifier, bridge, channel, user interaction]
          → First resolution wins (via ResolveOnce claim())
          → persistPermissions() if permanent
          → logDecision()
```

### Component Hierarchy

```
PermissionRequest (dispatcher)
  ├── BashPermissionRequest → BashPermissionRequestInner
  │     ├── PermissionDialog
  │     ├── PermissionRuleExplanation
  │     ├── PermissionExplainerContent
  │     ├── PermissionDecisionDebugInfo (debug only)
  │     └── Select (options from bashToolUseOptions)
  ├── FileEditPermissionRequest
  ├── FileWritePermissionRequest
  ├── FilesystemPermissionRequest
  ├── PowerShellPermissionRequest
  ├── WebFetchPermissionRequest
  ├── SkillPermissionRequest
  ├── SedEditPermissionRequest
  ├── EnterPlanModePermissionRequest
  ├── ExitPlanModePermissionRequest
  ├── NotebookEditPermissionRequest
  ├── AskUserQuestionPermissionRequest
  └── FallbackPermissionRequest
  │
  ├── FilePermissionDialog (shared by FileEdit/FileWrite/SedEdit/Filesystem)
  │     ├── useFilePermissionDialog hook
  │     ├── usePermissionHandler (PERMISSION_HANDLERS)
  │     ├── getFilePermissionOptions
  │     ├── ShowInIDEPrompt (IDE diff mode)
  │     └── Select
  │
  └── Select (CustomSelect system)
        ├── useSelectState → useSelectNavigation
        ├── useSelectInput
        ├── SelectOption (→ ListItem)
        └── SelectInputOption (→ TextInput + keybindings)
```
