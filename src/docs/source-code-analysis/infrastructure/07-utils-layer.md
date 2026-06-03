# 07 — Utils Layer

> **Size**: 564 files (~180,487 lines) — the largest module in the codebase.
> **Role**: Shared utility infrastructure consumed by all other layers (tools, services, UI, entrypoints).

---

## 1. Bash Utilities (`utils/bash/` — 16 files)

Pure-TypeScript bash parsing and AST analysis pipeline. Replaces shell-quote / regex-based approaches with a fail-closed tree-sitter-compatible AST.

### `bashParser.ts` (~4436 lines)
- **Pure-TypeScript tokenizer/parser** producing `TsNode` trees compatible with tree-sitter-bash's grammar.
- **`TsNode`**: `{ type, text, startIndex, endIndex, children }` — UTF-8 byte offsets, not JS string indices.
- **Token types**: `WORD`, `NUMBER`, `OP`, `NEWLINE`, `COMMENT`, `DQUOTE`, `SQUOTE`, `ANSI_C`, `DOLLAR`, `DOLLAR_PAREN`, `DOLLAR_BRACE`, `DOLLAR_DPAREN`, `BACKTICK`, `LT_PAREN`, `GT_PAREN`, `EOF`.
- **Safety caps**: 50ms wall-clock parse timeout, 50,000 node budget cap.
- **Key exports**: `ensureParserInitialized()`, `getParserModule()`, `parseSource()`.

### `ast.ts` (~2679 lines)
- **AST-based security analysis** for bash commands. Walks tree-sitter AST nodes with an explicit allowlist.
- **`SimpleCommand`**: `{ argv, envVars, redirects, text }`.
- **`Redirect`**: `{ op ('>'|'>>'|'<'|'<<'|...), target, fd? }`.
- **`ParseForSecurityResult`**: union of `{ kind: 'simple', commands }`, `{ kind: 'too-complex', reason, nodeType? }`, `{ kind: 'parse-unavailable' }`.
- **Structural types** recursed through: `program`, `list`, `pipeline`, `redirected_statement`.
- **Placeholder substitution**: `__CMDSUB_OUTPUT__` for `$()` command substitution in outer argv.
- **Design**: FAIL-CLOSED — any unrecognized node type causes `'too-complex'` classification.

### `parser.ts` (~230 lines)
- Thin wrapper over `bashParser.ts`'s `TsNode`, re-exported as `Node`.
- **`ParsedCommandData`**: `{ rootNode, envVars, commandNode, originalCommand }`.
- **`parseCommandRaw()`**: entry point for parsing with AST analysis.
- **`PARSE_ABORTED`**: sentinel for timed-out / over-budget parses.
- Handles declaration commands (`export`, `declare`, `typeset`, `readonly`, `local`, `unset`).

### `ParsedCommand.ts` (~318 lines)
- **`IParsedCommand`** interface: `{ originalCommand, toString(), getPipeSegments(), withoutOutputRedirections(), getOutputRedirections(), getTreeSitterAnalysis() }`.
- **`OutputRedirection`**: `{ target, operator: '>'|'>>' }`.
- Contains both tree-sitter and legacy shell-quote regex fallback implementations.

### `commands.ts` (~754 lines)
- Command splitting, heredoc extraction, and output redirection utilities.
- **`extractOutputRedirections()`**: parses `>`, `>>` redirects from shell commands.
- **`splitCommandWithOperators()`**: splits compound commands by `&&`, `||`, `|`, `;`.
- **Security**: uses `randomBytes()` to generate salted placeholder strings preventing injection via placeholder collision.
- **`extractHeredocs()` / `restoreHeredocs()`**: heredoc body extraction and restoration.

### `heredoc.ts`
- Heredoc delimiter detection and body extraction logic.

### `shellQuote.ts`, `shellQuoting.ts`
- Shell-safe quoting and unquoting utilities for constructing bash command strings.

### `shellPrefix.ts`, `shellCompletion.ts`, `prefix.ts`, `registry.ts`
- **`registry.ts`**: `CommandSpec` interface for registering known command behaviors.
- **`shellPrefix.ts`**: formats shell prefix commands (snapshot sourcing, environment setup).
- **`prefix.ts`**: command prefix extraction for permission matching.
- **`shellCompletion.ts`**: generates tab-completion candidates from command specs.

### `ShellSnapshot.ts`
- Captures and restores shell environment snapshots for consistent command execution context.

### `bashPipeCommand.ts`
- Pipe-aware command construction utilities.

### `treeSitterAnalysis.ts`
- **`TreeSitterAnalysis`** type and `analyzeCommand()` — bridges AST analysis with the rest of the command classification system.

### `specs/` (8 files)
Command specification files defining known-safe command behaviors for permission auto-classification:

| Spec | Purpose |
|------|---------|
| `pyright.ts` | Node-based Python type checker |
| `timeout.ts` | `timeout` wrapper — safe passthrough |
| `sleep.ts` | Safe no-op, no filesystem access |
| `alias.ts` | Shell alias resolution |
| `nohup.ts` | `nohup` wrapper — safe passthrough |
| `time.ts` | `/usr/bin/time` — safe measurement |
| `srun.ts` | SLURM `srun` — safe job submission |
| `index.ts` | Aggregates all specs into a `CommandSpec[]` |

---

## 2. Shell Utilities (`utils/shell/` — 10 files)

Platform-agnostic shell command execution abstraction.

### `shellProvider.ts`
- **`ShellProvider`** interface: `{ type, shellPath, detached, buildExecCommand(), getSpawnArgs(), getEnvironmentOverrides() }`.
- **`ShellType`**: `'bash' | 'powershell'`.
- **`DEFAULT_HOOK_SHELL`**: `'bash'`.
- **`buildExecCommand()`**: constructs full command string with snapshot sourcing, session env, extglob disable, pwd tracking.

### `bashProvider.ts`
- Bash-specific `ShellProvider` implementation. Handles tmux socket setup, shell snapshot, environment file sourcing.

### `powershellProvider.ts`, `powershellDetection.ts`
- PowerShell-specific `ShellProvider` implementation. **`getCachedPowerShellPath()`**: detects and caches the PowerShell executable path.
- **`buildPowerShellArgs()`**: constructs PowerShell spawn arguments.

### `outputLimits.ts`
- Shell output size limits and truncation policies.

### `readOnlyCommandValidation.ts`
- **`containsVulnerableUncPath()`**: detects vulnerable UNC paths in commands.
- Validates that read-only commands contain no malicious constructs.

### `prefix.ts`, `specPrefix.ts`
- Command prefix extraction for shell tool permission matching.

### `resolveDefaultShell.ts`
- Resolves the default shell for the current platform (bash on Linux/macOS, PowerShell on Windows).

### `shellToolUtils.ts`
- Shared utilities for BashTool and PowerShellTool implementations.

---

## 3. Permissions (`utils/permissions/` — 24 files)

The permission checking pipeline — rules, matching, classification, denial tracking, and mode management.

### `permissions.ts` (~1486 lines)
- **Central permission check orchestration**. Entry point: `checkPermissions()`.
- Features: auto-mode classifier integration (behind `TRANSCRIPT_CLASSIFIER` feature flag), rule matching, denial tracking fallback.
- Handles sandbox routing, permission mode titles, setting source display.
- **`getRuleByContentsForToolName()`**: finds matching permission rules for a tool.
- Integrates with GrowthBook feature gates, classifier decision pipeline, and analytics event logging.

### `classifierShared.ts`
- Shared infrastructure for classifier-based permission systems (bashClassifier, yoloClassifier).
- **`extractToolUseBlock()`**: extracts tool_use block by tool name from message content.
- **`parseClassifierResponse()`**: parses and validates classifier responses against Zod schemas.

### `classifierDecision.ts`
- **Safe YOLO allowlist** of tools that never need classifier checking:
  - Read-only: `FILE_READ_TOOL_NAME`, `GREP_TOOL_NAME`, `GLOB_TOOL_NAME`, `LSP_TOOL_NAME`
  - Task management: `TASK_CREATE/GET/LIST/UPDATE/STOP/OUTPUT_TOOL_NAME`
  - Infrastructure: `LIST_MCP_RESOURCES_TOOL_NAME`, `SLEEP_TOOL_NAME`, `TOOL_SEARCH_TOOL_NAME`
  - Communication: `SEND_MESSAGE_TOOL_NAME`, `ASK_USER_QUESTION_TOOL_NAME`
  - Team: `TEAM_CREATE/TOOL_NAME`, `TEAM_DELETE_TOOL_NAME`
  - Plan mode: `ENTER_PLAN_MODE_TOOL_NAME`, `EXIT_PLAN_MODE_TOOL_NAME`
- Excludes write/edit tools — those use the acceptEdits fast path.

### `yoloClassifier.ts` (~1495 lines)
- **AI-based YOLO mode security classifier**. Uses a separate model call to decide whether a tool use should be allowed without user confirmation.
- **`YoloClassifierResult`**: classification outcome with confidence, reason, permission decision.
- Behind `TRANSCRIPT_CLASSIFIER` feature flag. Ant-only feature with external stub.
- Loads prompt templates from text files: `auto_mode_system_prompt.txt`, `permissions_anthropic.txt`.
- Handles retries, timeouts, token tracking, and fallback logic.

### `bashClassifier.ts`
- **Semantic bash command matching** for prompt-based allow/deny rules.
- **`classifyBashCommand()`**: determines if a bash command matches natural language descriptions.
- **`ClassifierResult`**: `{ matches, matchedDescription?, confidence: 'high'|'medium'|'low', reason }`.
- External builds get stub implementations (all methods return "feature disabled").

### `denialTracking.ts`
- **`DenialTrackingState`**: `{ consecutiveDenials, totalDenials }`.
- **Limits**: 3 consecutive denials or 20 total denials trigger fallback to manual prompting.
- **`recordDenial()`**, **`recordSuccess()`**, **`shouldFallbackToPrompting()`**.
- Immutable updates (returns new state objects).

### `autoModeState.ts`
- Manages auto-mode permission state across turns, behind `TRANSCRIPT_CLASSIFIER` flag.

### `filesystem.ts` (~1777 lines)
- **Filesystem permission checking** for file read/edit tools.
- **`DANGEROUS_FILES`**: list of protected files (`.gitconfig`, `.gitmodules`, `.bashrc`, etc.).
- Path traversal detection, UNC path validation, sandbox boundary checks.
- Gitignore-based directory permission matching.
- Auto-memory directory (`MEMORY.md`, `CLAUDE.md`) path validation.
- **`getPathsForPermissionCheck()`**: resolves all paths in a tool call for checking.

### `PermissionMode.ts`
- **`PermissionMode`**: `'default' | 'plan' | 'acceptEdits' | 'bypass' | 'auto'` (with `TRANSCRIPT_CLASSIFIER`).
- **`ExternalPermissionMode`**: subset exposeInkRenderered externally (`'default' | 'plan' | 'acceptEdits' | 'bypass'`).
- **`PermissionModeConfig`**: `{ title, shortTitle, symbol, color, external }`.
- Mode UI rendering configuration (icon, color key).

### `PermissionRule.ts`
- **`PermissionBehavior`**: `'allow' | 'deny' | 'ask'`.
- **`PermissionRuleValue`**: `{ toolName, ruleContent? }`.
- **`PermissionRuleSource`**: where the rule comes from (settings file, managed policy, etc.).
- Types re-exported from `src/types/permissions.ts` to break import cycles.

### `PermissionResult.ts`
- **`PermissionResult`**: discriminated union with `killswitch` state, auto-detected permission filter, and decision.
- **`PermissionDecision`**: union of `PermissionAskDecision`, `PermissionDenyDecision`.
- **`PermissionDecisionReason`**: granular reason codes for decisions.

### `PermissionUpdate.ts`
- **`applyPermissionUpdate()`**, **`applyPermissionUpdates()`**, **`persistPermissionUpdates()`**: mutations for adding/removing permission rules.
- Creates `PermissionUpdate` records from user decisions.

### `PermissionUpdateSchema.ts`
- Zod schemas for permission updates with destination target (`userSettings`, `projectSettings`, `localSettings`).

### `permissionRuleParser.ts`
- **`permissionRuleValueFromString()`**, **`permissionRuleValueToString()`**: serialize/deserialize rule values between display strings and structured data.

### `permissionsLoader.ts`
- **`deletePermissionRuleFromSettings()`**: removes rules from settings files.
- **`shouldAllowManagedPermissionRulesOnly()`**: checks if managed policy restricts rules to admin-only.
- **`PermissionRuleFromEditableSettings`**: read-only snapshot type.

### `permissionSetup.ts`
- Permission system initialization and setup hooks.

### `permissionExplainer.ts`
- Human-readable explanations for permission decisions.

### `shadowedRuleDetection.ts`
- Detects when a permission rule is shadowed (overridden) by a higher-precedence rule.

### `getNextPermissionMode.ts`
- Computes the next permission mode after a tool use completes (e.g., auto→fallback transitions).

### `bypassPermissionsKillswitch.ts`
- Kill switch mechanism for globally disabling permission bypass mode.

### `dangerousPatterns.ts`
- Pattern definitions for detecting dangerous command constructs.

### `shellRuleMatching.ts`
- Shell-specific permission rule matching logic.

### `PermissionPromptToolResultSchema.ts`
- Zod schema for the permission prompt tool result structure.

### `pathValidation.ts`
- Path normalization and validation for permission rules targeting file paths.

---

## 4. Settings (`utils/settings/` — 17 files)

Multi-source configuration cascade with Zod validation, caching, and MDM support.

### `settings.ts` (~1015 lines)
- **Settings read/write cascade**: loads and merges settings from 10+ sources with defined precedence.
- **`getSettings_DEPRECATED()`**: merged view of all setting sources.
- **`getSettingsForSource(source)`**: reads settings from a single source.
- **`loadManagedFileSettings()`**: loads managed-settings.json + managed-settings.d/*.json with systemd-style drop-in precedence.
- **`loadSettingsFromDisk()`**: full cascade load (user, project, local, managed, plugin, etc.).
- **`getSettingsFilePathForSource()`**: resolves filesystem path for each source.
- Writes settings with file flushing, gitignore updates, and internal write marking.
- **Setting source precedence** (highest to lowest): flag overrides → session → local → project → user → managed drop-ins → managed base → plugin → MDM → built-in defaults.

### `types.ts` (~1148 lines)
- **`SettingsJson`**, **`SettingsSchema`**: Zod schemas for all settings sections.
- **`PermissionsSchema`**: `{ allow, deny, ask, defaultMode, disableBypassPermissionsMode, disableAutoMode?, additionalDirectories }`.
- **`EnvironmentVariablesSchema`**: `Record<string, string>`.
- **`HooksSchema`** re-export: `{ hookMatchers, hookCommands }` for each hook event.
- Re-exports hook schemas from `src/schemas/hooks.ts` for backward compatibility.

### `settingsCache.ts`
- **`getSessionSettingsCache()` / `setSessionSettingsCache()`**: session-scoped merged settings cache.
- **`getCachedSettingsForSource()` / `setCachedSettingsForSource()`**: per-source cache to avoid redundant disk reads + Zod parses.
- **`getCachedParsedFile()` / `setCachedParsedFile()`**: path-keyed cache for `parseSettingsFile()`.
- **`resetSettingsCache()`**: invalidates all caches (triggered by writes, --add-dir, plugin init, hooks refresh).

### `validation.ts`, `validationTips.ts`, `allErrors.ts`
- **`SettingsWithErrors`**: merged settings with validation error collection.
- **`filterInvalidPermissionRules()`**: strips malformed rules and reports errors.
- **`formatZodError()`**: human-readable Zod error formatting.
- **`validationTips.ts`**: user-facing validation tips for common misconfigurations.
- **`allErrors.ts`**: aggregates all validation errors across all sources into one list.

### `constants.ts`
- **`SettingSource`**: union of all setting source identifiers.
- **`EditableSettingSource`**: subset of sources users can write to.
- **`SETTING_SOURCES`**: enum-like const object.
- **`getEnabledSettingSources()`**: returns currently active sources.
- **`getSettingSourceDisplayNameLowercase()`**: display names for UI.
- **`CLAUDE_CODE_SETTINGS_SCHEMA_URL`**: schema reference URL for `$schema` field.

### `managedPath.ts`
- **`getManagedFilePath()`**: resolves the managed settings directory path.
- **`getManagedSettingsDropInDir()`**: resolves the drop-in directory for managed settings.

### `internalWrites.ts`
- **`markInternalWrite()`**: marks a settings write as internal (not user-initiated) to prevent feedback loops.

### `changeDetector.ts`
- Detects settings changes between writes for caching decisions.

### `applySettingsChange.ts`
- Applies a single setting key/value change to the appropriate source file.

### `permissionValidation.ts`
- **`PermissionRuleSchema()`**: Zod schema for individual permission rules.
- Validates tool names, rule content, and rule structure.

### `pluginOnlyPolicy.ts`
- Policy enforcement for managed settings that restrict to plugin-only configuration.

### `schemaOutput.ts`
- Generates JSON Schema output for settings documentation.

### `toolValidationConfig.ts`
- Configuration for validating tool-specific settings.

### `validateEditTool.ts`
- Validates the Edit tool's permission configuration.

### `mdm/` (3 files)
- **`constants.ts`**: MDM key paths and platform-specific registry/plist constants.
- **`rawRead.ts`**: reads raw MDM settings from OS-specific stores (Windows registry, macOS plist).
- **`settings.ts`**: **`getMdmSettings()`**, **`getHkcuSettings()`** — reads MDM and local-machine policy settings.

---

## 5. Hooks (`utils/hooks.ts` + `utils/hooks/` — 17+1 files)

User-extensible lifecycle hook system (shell commands, HTTP callbacks, prompt injection, function callbacks).

### `hooks.ts` (~5022 lines)
- **Global hook orchestration** — registration, match-filtering, execution, and result processing.
- **Hook types**: `command` (shell), `prompt` (inject system message), `http` (REST callback), `function` (in-process JS callback), `callback` (SDK-registered).
- **Hook events** (lifecycle points):
  - `PreToolUse` / `PostToolUse` — before/after tool execution, can block or modify.
  - `PostToolUseFailure` — error recovery hooks.
  - `UserPromptSubmit` — can modify user input, inject context.
  - `SessionStart` — startup initialization hooks.
  - `Stop` — agent stop hooks.
  - `PreCompact` / `PreCompactInstructions` — compaction pipeline hooks.
  - `Notification` — event notification hooks.
  - `StatusLine` — status bar content hooks.
  - `FileSuggestion` — typeahead file suggestion hooks.
  - `WorktreeCreate` / `WorktreeRemove` — worktree lifecycle hooks.
  - `SubagentStop` / `SubagentStart` — teammate lifecycle hooks.
- **`HookCallback`**: `{ matcher?, hooks: HookCommand[] }` — registered via SDK.
- **`HookCallbackMatcher`**: optional filter: `{ toolName?, timeout?, command? }`.
- **`MatchedHook`**: `{ hook: HookCommand | HookCallback, ... }`.
- **`HookResult`**: `{ outcome: 'success'|'blocking'|'non_blocking_error'|'cancelled', message?, hook, ... }`.
- **`executeUserPromptSubmitHooks()`**: runs UserPromptSubmit hooks, returns blocking messages.
- **`getUserPromptSubmitHookBlockingMessage()`**: synchronous check for blocking results.
- **`executeHooksOutsideREPL()`**: runs hooks outside the main REPL loop (for worktree ops, etc.).
- **`hasWorktreeCreateHook()`**: checks if worktree hooks are configured.
- **`executeWorktreeCreateHook()`**: returns worktree path from hook stdout.
- **`executeWorktreeRemoveHook()`**: notifies worktree removal.
- **Workspace trust gating**: all hooks require `checkHasTrustDialogAccepted()` in interactive mode.
- **Managed settings gating**: `shouldAllowManagedHooksOnly()`, `shouldDisableAllHooksIncludingManaged()`.
- Integrates with OTel tracing (`startHookSpan`/`endHookSpan`), analytics, and session stats.

### `hooks/hookEvents.ts`
- **`HookExecutionEvent`**: union of `HookStartedEvent | HookProgressEvent | HookResponseEvent`.
- **`HookEventHandler`**: callback type `(event: HookExecutionEvent) => void`.
- Always-emitted events: `SessionStart`, `Setup` (backward compatible).
- **`MAX_PENDING_EVENTS` = 100**: buffers events before handlers are registered.
- **`setHookEventHandler()`, `clearHookEventHandler()`, `disableAllHookEvents()`**.

### `hooks/hooksConfigSnapshot.ts`
- **`getHooksConfigFromSnapshot()`**: returns frozen snapshot of all hook configurations.
- **`shouldAllowManagedHooksOnly()`**: managed policy restricting to admin hooks.
- **`shouldDisableAllHooksIncludingManaged()`**: global hooks kill switch.

### `hooks/hooksConfigManager.ts`
- Manages hook configuration lifecycle (load, watch, invalidate).

### `hooks/execCommandHook.ts`, `hooks/execHttpHook.ts`, `hooks/execPromptHook.ts`, `hooks/execAgentHook.ts`
- Per-hook-type execution implementations.
- `execCommandHook`: spawns shell command via `child_process.spawn`, handles timeouts, environment variables.
- `execHttpHook`: sends JSON payload to configured URL, receives response or 2xx error.
- `execPromptHook`: injects prompt text into system message stream.

### `hooks/AsyncHookRegistry.ts`
- Registry for async hook execution and result tracking.

### `hooks/registerFrontmatterHooks.ts`
- Registers hooks from frontmatter in instruction files (MEMORY.md, CLAUDE.md).

### `hooks/registerSkillHooks.ts`
- Registers hooks from loaded skills.

### `hooks/sessionHooks.ts`
- Session-level hook lifecycle management.

### `hooks/postSamplingHooks.ts`
- Post-sampling hook processing (after model response).

### `hooks/fileChangedWatcher.ts`
- Watches for hook configuration file changes.

### `hooks/hookHelpers.ts`
- Shared helpers for hook execution.

### `hooks/hooksSettings.ts`
- Hook settings resolution from the settings cascade.

### `hooks/skillImprovement.ts`
- Hook-driven skill improvement prompts.

### `hooks/ssrfGuard.ts`
- SSRF guard for HTTP hook URLs (prevents internal network access).

### `hooks/apiQueryHookHelper.ts`
- Helper for API query hooks.

---

## 6. Messages (`utils/messages.ts` — ~5512 lines + `utils/messages/`)

Message normalization, serialization, deserialization, and content block manipulation.

### `messages.ts` (~5512 lines)
- **Message type system**: `Message` = `UserMessage | AssistantMessage | SystemMessage | AttachmentMessage | ProgressMessage | ToolUseSummaryMessage | TombstoneMessage | ...`.
- **`NormalizedMessage`**, **`NormalizedAssistantMessage`**, **`NormalizedUserMessage`**: flattened message representations.
- **Normalization pipeline**: `normalizeMessages()`, `normalizeContentBlocks()`.
- **Serialization/Deserialization**: `serializeMessages()`, `deserializeMessages()`.
- **Content block parameter handling**: converts between SDK `ContentBlockParam` and internal `ContentBlock` types.
- **`createUserMessage()`**, **`createSystemMessage()`**, **`createCommandInputMessage()`**, **`createAttachmentMessage()`**: message factory functions.
- **`extractTextContent()`**: extracts text from content blocks.
- **`createAssistantMessage()`**: builds assistant messages with tool use blocks.
- **System message types** (comprehensive list):
  - `SystemBridgeStatusMessage`, `SystemInformationalMessage`, `SystemAPIErrorMessage`
  - `SystemApiMetricsMessage`, `SystemTurnDurationMessage`, `SystemCompactBoundaryMessage`
  - `SystemMicrocompactBoundaryMessage`, `SystemStopHookSummaryMessage`, `SystemAwaySummaryMessage`
  - `SystemPermissionRetryMessage`, `SystemScheduledTaskFireMessage`, `SystemMemorySavedMessage`
  - `SystemAgentsKilledMessage`, `SystemLocalCommandMessage`
- **`NO_CONTENT_MESSAGE`**: empty content sentinel.
- **`StopHookInfo`**, **`StreamEvent`**, **`RequestStartEvent`**, **`ProgressMessage`**: streaming infrastructure types.
- Integration with analytics for tool name sanitization, image error messages, PDF error messages.

### `messages/mappers.ts`
- Message type mapping utilities for protocol conversion.

### `messages/systemInit.ts`
- System initialization message generation for session setup.

---

## 7. Session Storage (`utils/sessionStorage.ts` — ~5105 lines)

Session persistence engine with transcript recording and replay.

### `sessionStorage.ts` (~5105 lines)
- **Transcript persistence**: appends messages to JSONL transcript files.
- **`appendMessage()`**: writes a single message to the session transcript.
- **`getTranscriptPathForSession()`**, **`getAgentTranscriptPath()`**: resolves transcript file paths for sessions and agents.
- **`readTranscript()`**: reads and parses session transcripts.
- **`getProjectDir()`**: resolves project directory for session storage.
- **`listSessions()`**, **`convertEntryToLogOption()`**: session listing and display.
- **Entry types**: `TranscriptMessage`, `ContextCollapseCommitEntry`, `ContextCollapseSnapshotEntry`, `ContentReplacementEntry`, `FileHistorySnapshotMessage`, `AttributionSnapshotMessage`.
- **`SerializedMessage`**, **`LogOption`**, **`PersistedWorktreeSession`**: serialization/display types.
- **`sortLogs()`**: chronological sort with tiebreaking.
- **`isTranscriptMessage()`**: type guard for transcript entries.
- **`sessionStoragePortable.ts`**: portable variant for non-Node environments.

---

## 8. Attachments (`utils/attachments.ts` — ~3997 lines)

File attachment handling, image processing, and context injection.

### `attachments.ts` (~3997 lines)
- **`createAttachmentMessage()`**: creates structured attachment messages for the model context.
- **`getAttachmentMessages()`**: resolves all attachment types for a prompt:
  - IDE selections / open files
  - Memory files (MEMORY.md, CLAUDE.md, conditional rules)
  - Image pastes (with resizing/downsampling)
  - PDF files (with validation)
  - Clipboard content
  - Diagnostic files
  - Plan files
  - Task context (viewed teammate tasks, todo lists)
  - Tool result files
- **Attachment types**: `AgentMentionAttachment`, `HookAttachment`, `HookPermissionDecisionAttachment`, `HookErrorDuringExecutionAttachment`.
- **Image handling**: `maybeResizeAndDownsampleImageBlock()` for budget-aware image sizing.
- **Memory file integration**: `getMemoryFiles()`, `filterInjectedMemoryFiles()`, `getManagedAndUserConditionalRules()`, `getConditionalRulesForCwdLevelDirectory()`.
- **Todo/Task attachments**: integrates with `tasks.ts` and `todo/types.ts` for task state injection.

---

## 9. Computer Use (`utils/computerUse/` — 15 files)

Browser automation via Chrome DevTools Protocol (CDP) for Mac-only CLI.

### `executor.ts` (~658 lines)
- **`ComputerExecutor`** implementation wrapping two native modules:
  - `@ant/computer-use-input` (Rust/enigo): mouse, keyboard, frontmost app
  - `@ant/computer-use-swift`: SCContentFilter screenshots, NSWorkspace apps, TCC permissions
- **CLI deltas from Cowork** (Electron desktop app):
  - No click-through overlay bracket (no window)
  - Terminal as surrogate host (detected via `getTerminalBundleId()`)
  - Clipboard via `pbcopy`/`pbpaste` (no Electron clipboard module)
- **`computeTargetDims()`**: logical → physical → API target dimension computation.
- **Screenshot**: 0.75 JPEG quality, drain run loop before capture.

### `common.ts`
- **`CLI_CU_CAPABILITIES`**: capability declarations for the CLI host.
- **`CLI_HOST_BUNDLE_ID`**: sentinel bundle ID (never matches frontmost).
- **`getTerminalBundleId()`**: detects the terminal emulator bundle ID.

### `mcpServer.ts`
- MCP (Model Context Protocol) server for computer use tool exposure.

### `setup.ts`
- One-time setup and permission grants for computer use.

### `hostAdapter.ts`
- Adapts the CLI host for the computer-use-mcp package contract.

### `wrapper.tsx`
- React/Ink rendering wrapper for computer use UI elements.

### `toolRendering.tsx`
- Tool-specific rendering components for computer use operations.

### `gates.ts`
- Feature gates and capability checks for computer use.

### `inputLoader.ts`
- **`requireComputerUseInput()`**: dynamic import of the native input module.

### `swiftLoader.ts`
- **`requireComputerUseSwift()`**: dynamic import of the native Swift module.

### `drainRunLoop.ts`
- Run loop draining before screenshots (ensures window state is current).

### `escHotkey.ts`
- **`notifyExpectedEscape()`**: escape key handling for computer use sessions.

### `computerUseLock.ts`
- Mutual exclusion lock preventing concurrent computer use sessions.

### `cleanup.ts`
- Resource cleanup for computer use sessions.

### `appNames.ts`
- Application name resolution for NSWorkspace.

---

## 10. Swarm (`utils/swarm/` — 14 files)

Multi-agent swarm coordination with pluggable communication backends.

### Backend Types (`backends/types.ts`)
- **`BackendType`**: `'tmux' | 'iterm2' | 'in-process'`.
- **`PaneBackendType`**: `'tmux' | 'iterm2'` (pane-based only).
- **`PaneId`**: opaque pane identifier string.
- **`PaneBackend`** interface: `{ type, createPane(), sendKeys(), resizePane(), killPane(), isAvailable(), supportsColors() }`.
- **`CreatePaneResult`**: `{ paneId, isFirstTeammate }`.

### `backends/` (9 files)
- **`TmuxBackend.ts`**: tmux pane management via tmux CLI.
- **`ITermBackend.ts`**: iTerm2 native split panes via it2 CLI.
- **`InProcessBackend.ts`**: same-process execution with isolated context.
- **`PaneBackendExecutor.ts`**: unified executor dispatching to the appropriate backend.
- **`detection.ts`**: auto-detects available backends at runtime.
- **`registry.ts`**: backend registry for registration and lookup.
- **`it2Setup.ts`**: iTerm2 setup and configuration.
- **`teammateModeSnapshot.ts`**: captures/restores swarm layout state.
- **`types.ts`**: backend-specific type definitions.

### Core Swarm Files
- **`constants.ts`**: swarm configuration constants.
- **`inProcessRunner.ts`**: runner for in-process agents.
- **`spawnUtils.ts` / `spawnInProcess.ts`**: agent spawn utilities.
- **`teammateInit.ts`**: teammate initialization (layout, model, prompt).
- **`teammateModel.ts`**: model selection for teammates.
- **`teammatePromptAddendum.ts`**: teammate-specific prompt additions.
- **`teamHelpers.ts`**: shared team coordination utilities.
- **`teammateLayoutManager.ts`**: pane layout strategy.
- **`leaderPermissionBridge.ts`**: bridges leader permissions to teammates.
- **`permissionSync.ts`**: synchronizes permissions across swarm members.
- **`reconnection.ts`**: handles reconnection after backend changes.
- **`It2SetupPrompt.tsx`**: iTerm2 setup prompt UI component.

---

## 11. Telemetry (`utils/telemetry/` — 9 files)

OpenTelemetry integration for metrics, tracing, and logging.

### `instrumentation.ts` (~825 lines)
- **OTel SDK setup**: configures `TracerProvider`, `MeterProvider`, `LoggerProvider`.
- **Dynamic exporter loading**: OTLP (HTTP/gRPC), Prometheus exporters are lazy-loaded per signal type (~1.2MB savings at startup).
- **Resource detection**: `envDetector`, `hostDetector`, `osDetector`, manual attributes (`ATTR_SERVICE_NAME`, `ATTR_SERVICE_VERSION`, `SEMRESATTRS_HOST_ARCH`).
- **Exporters**: `ConsoleSpanExporter`, `ConsoleMetricExporter`, `ConsoleLogRecordExporter` + OTLP variants.
- **Processors**: `BatchSpanProcessor`, `PeriodicExportingMetricReader`, `BatchLogRecordProcessor`.
- **Proxy support**: `HttpsProxyAgent` for OTLP exporters behind corporate proxies.
- **mTLS**: supports mutual TLS via `getMTLSConfig()`.
- **CACertificates**: custom CA bundle support via `getCACertificates()`.
- **Provider setter/getter integration** with `bootstrap/state.ts`.

### `events.ts`
- **`logOTelEvent()`**: emits OTel events with typed attributes.
- Event type definitions for common telemetry events.

### `logger.ts`
- OTel log bridge — routes application logs through OTel SDK logger provider.

### `sessionTracing.ts`
- **`startHookSpan()` / `endHookSpan()`**: OpenTelemetry span management for hook execution.
- Session-scoped tracing with span hierarchy.

### `perfettoTracing.ts`
- Perfetto trace event format generation for Chrome trace viewer integration.

### `pluginTelemetry.ts`
- Plugin-specific telemetry event definitions and logging.

### `bigqueryExporter.ts`
- Custom BigQuery log exporter for analytics pipeline.

### `skillLoadedEvent.ts`
- Telemetry event for skill loading tracking.

### `betaSessionTracing.ts`
- Beta/experimental session tracing feature gate and implementation.

---

## 12. Model (`utils/model/` — 16 files)

Model resolution, aliases, capability detection, provider routing, and deprecation.

### `model.ts` (~618 lines)
- **`ModelName`** (= `string`), **`ModelShortName`**, **`ModelSetting`** (= `ModelName | ModelAlias | null`).
- **`getUserSpecifiedModelSetting()`**: resolves user model preference cascade:
  1. `/model` command override (highest)
  2. `--model` CLI flag override
  3. `ANTHROPIC_MODEL` env var
  4. Settings file `model` field
- **Model allowlist filtering**: ignores user preference if not in `availableModels`.
- **`getDefaultSonnetModel()`**, **`getDefaultHaikuModel()`**, **`getDefaultOpusModel()`**: default model resolution.
- **`getSmallFastModel()`**: returns the configured small/fast model (env fallback to haiku).
- **`isNonCustomOpusModel()`**: checks if a model is a non-custom Opus variant.
- **`getMainLoopModel()`**: resolves the active main loop model.
- **Subscription-aware model access**: `isMaxSubscriber()`, `isProSubscriber()`, `isTeamPremiumSubscriber()`.

### `aliases.ts`
- **`ModelAlias`**: `'sonnet' | 'opus' | 'haiku' | 'best' | 'sonnet[1m]' | 'opus[1m]' | 'opusplan'`.
- **`isModelAlias()`**: type guard for model aliases.
- **`ModelFamilyAlias`**: `'sonnet' | 'opus' | 'haiku'` — wildcard aliases for the `availableModels` allowlist.
- **`isModelFamilyAlias()`**: checks if a string is a family-level wildcard.

### `configs.ts`
- **`ModelConfig`**: `Record<APIProvider, ModelName>` — per-provider model name mapping.
- **Model configs** for every released Claude model:
  - `CLAUDE_3_5_HAIKU_CONFIG`, `CLAUDE_HAIKU_4_5_CONFIG`
  - `CLAUDE_3_5_V2_SONNET_CONFIG`, `CLAUDE_3_7_SONNET_CONFIG`, `CLAUDE_SONNET_4_CONFIG`, `CLAUDE_SONNET_4_5_CONFIG`
  - `CLAUDE_OPUS_4_CONFIG`, `CLAUDE_OPUS_4_1_CONFIG`
- Each maps `firstParty`, `bedrock`, `vertex`, `foundry` provider-specific model IDs.

### `providers.ts`
- **`APIProvider`**: `'firstParty' | 'bedrock' | 'vertex' | 'foundry'`.
- **`getAPIProvider()`**: detects active provider from environment variables:
  - `CLAUDE_CODE_USE_BEDROCK` → bedrock
  - `CLAUDE_CODE_USE_VERTEX` → vertex
  - `CLAUDE_CODE_USE_FOUNDRY` → foundry
  - default → firstParty
- **`isFirstPartyAnthropicBaseUrl()`**: validates base URL points to `api.anthropic.com`.

### `modelCapabilities.ts`
- **`ModelCapability`**: `{ id, max_input_tokens?, max_tokens? }` — fetched from API, cached to disk.
- **`getModelCapabilities()`**: returns cached model capability data.
- **`isModelCapabilitiesEligible()`**: ant-only, firstParty-only guard.
- Disk cache at `~/.claude/cache/model-capabilities.json`.

### `modelStrings.ts`
- **`getModelStrings()`**: returns current model codename strings for feature-detection comparisons.
- **`resolveOverriddenModel()`**: handles model string overrides.

### `modelAllowlist.ts`
- **`isModelAllowed()`**: checks if a model (or its family alias) is in the user's allowlist.

### `modelOptions.ts`
- **`ModelOption`**: type for model selection UI options with display name, description, pricing.

### `antModels.ts`
- **`resolveAntModel()`**: resolves ant-only model references. Dead-code-eliminated in external builds.

### `modelSupportOverrides.ts`
- Manual model capability overrides for testing/edge cases.

### `contextWindowUpgradeCheck.ts`
- Checks if the user is eligible for a 1M context window upgrade.

### `check1mAccess.ts`
- **`has1mContext()`**: checks if 1M context window is available.
- **`modelSupports1M()`**: checks if a model supports 1M context.

### `deprecation.ts`
- Model deprecation date tracking and upgrade nudge logic.

### `validateModel.ts`
- Validates model names against known valid model IDs.

---

## 13. ClaudeInChrome (`utils/claudeInChrome/` — 7 files)

Chrome extension integration for browser-hosted Claude Code.

### `common.ts`
- Shared types and constants for Chrome native messaging protocol.

### `chromeNativeHost.ts`
- Chrome Native Messaging host implementation using stdio JSON protocol.

### `mcpServer.ts`
- MCP server adapter for Chrome extension transport.

### `prompt.ts`
- Browser-specific prompt injection and context assembly.

### `setup.ts`, `setupPortable.ts`
- One-time setup for Chrome native host registration.
- Portable variant for non-standard installations.

### `toolRendering.tsx`
- Tool-specific rendering for Chrome-based tool execution.

---

## 14. Additional Directory Modules

### `utils/cli/` — CLI Helper Utilities
> Note: The user mentions `utils/cli/` but the directory listing shows these as root-level utils files: `cliArgs.ts`, `cliHighlight.ts`, `slashCommandParsing.ts`, `exampleCommands.ts`.

- **`cliArgs.ts`**: **`eagerParseCliFlag()`** — parses CLI flags before Commander.js init (e.g., `--settings`). **`extractArgsAfterDoubleDash()`** — handles `--` separator convention.
- **`cliHighlight.ts`**: syntax highlighting for CLI output.
- **`slashCommandParsing.ts`**: parses slash commands (`/model`, `/compact`, etc.) from user input.
- **`exampleCommands.ts`**: built-in example command definitions.

### `utils/git/` (3 files)
- **`gitFilesystem.ts`**: reads `.git` directory structure directly (HEAD ref, branch, remote URL, worktree count, shallow clone detection). Faster than spawning `git` process.
- **`gitignore.ts`**: `.gitignore` parsing and pattern matching (`addFileGlobRuleToGitignore()`).
- **`gitConfigParser.ts`**: parses `.git/config` INI-style format.

### `utils/git.ts` (~926 lines)
- **`findGitRoot()`**: walks directory tree upward to find `.git` directory or file.
- **`getDefaultBranch()`**: resolves default branch (main/master).
- **`getBranch()`**: resolves current branch.
- **`getIsClean()`**: checks for uncommitted changes.
- **`getRemoteUrl()`**: resolves git remote URL.
- **`gitExe()`**: returns the git executable path.
- **`findCanonicalGitRoot()`**: resolves through symlinks to find real repository root.
- **`getCachedBranch()`, `getCachedDefaultBranch()`, etc.**: memoized git metadata accessors.

### `utils/sandbox/` (2 files)
- **`sandbox-adapter.ts`**: **`SandboxManager`** interface — abstracts sandbox container operations (create, exec, cleanup, mount).
- **`sandbox-ui-utils.ts`**: UI helpers for sandbox status display.

### `utils/suggestions/` (5 files)
- **`commandSuggestions.ts`**: generates slash command suggestions.
- **`directoryCompletion.ts`**: filesystem-based directory path completion.
- **`shellHistoryCompletion.ts`**: shell history-based suggestion engine.
- **`skillUsageTracking.ts`**: tracks skill usage for suggestion ranking.
- **`slackChannelSuggestions.ts`**: Slack channel name completions.

### `utils/secureStorage/` (6 files)
- **`index.ts`**: **`getSecureStorage()`** — platform dispatch (macOS → Keychain+Plaintext fallback, others → Plaintext).
- **`macOsKeychainStorage.ts`**: macOS Keychain integration via `security` CLI.
- **`macOsKeychainHelpers.ts`**: Keychain service name resolution, username detection.
- **`keychainPrefetch.ts`**: background keychain prefetch for API keys.
- **`plainTextStorage.ts`**: plaintext fallback storage for non-macOS platforms.
- **`fallbackStorage.ts`**: **`createFallbackStorage()`** — tries primary storage, falls back to secondary.
- **`SecureStorage`** interface: `{ getPassword(), setPassword(), deletePassword() }`.

### `utils/deepLink/` (6 files)
- **`parseDeepLink.ts`**: parses `claude://` protocol URLs into structured data.
- **`protocolHandler.ts`**: registers the `claude://` protocol handler with the OS.
- **`registerProtocol.ts`**: OS-specific protocol registration (Windows registry, macOS plist).
- **`terminalLauncher.ts`**: launches the terminal with the correct command for deep link handling.
- **`terminalPreference.ts`**: user terminal emulator preference detection.
- **`banner.ts`**: deep link setup completion banner.

### `utils/teleport/` (4 files + root `teleport.tsx`)
- **Root `teleport.tsx`** (~1226 lines): session teleport main orchestration — resume sessions from another machine via Anthropic API. Fetches session logs via OAuth, parses git remote, checks out branch, deserializes messages. **`TeleportResult`**: `{ messages, branchName }`.
- **`teleport/api.ts`**: Anthropic API client for session/teleport endpoints.
- **`teleport/gitBundle.ts`**: creates and uploads git bundles for session state transfer.
- **`teleport/environments.ts`**: machine/device environment listing.
- **`teleport/environmentSelection.ts`**: UI for selecting teleport target environment.

### `utils/processUserInput/` (4 files)
- **`processUserInput.ts`**: main user input processing pipeline — stitches together command parsing, attachment resolution, hook execution, message creation.
- **`processBashCommand.tsx`**: processes !bang/bash-prefixed commands.
- **`processSlashCommand.tsx`**: processes /slash commands.
- **`processTextPrompt.ts`**: processes plain text prompts.

### `utils/nativeInstaller/` (5 files)
- **`installer.ts`**: native binary download and installation orchestration.
- **`download.ts`**: binary download with progress tracking.
- **`packageManagers.ts`**: system package manager detection (npm, yarn, pnpm, pip, etc.).
- **`pidLock.ts`**: PID-based file lock for installer singleton.
- **`index.ts`**: re-exports public API.

### `utils/dxt/` (2 files)
- **`helpers.ts`**: DXT (DirectX Texture) format detection and metadata extraction.
- **`zip.ts`**: DXT file decompression utilities.

### `utils/background/remote/` (2 files)
- Remote agent background communication utilities and preconditions checks.

### `utils/powershell/` (3 files)
- **`parser.ts`**: PowerShell command parsing for permission classification.
- **`dangerousCmdlets.ts`**: list of dangerous PowerShell cmdlets for security checks.
- **`staticPrefix.ts`**: static prefix extraction for PowerShell command matching.

### `utils/mcp/` (2 files)
- **`dateTimeParser.ts`**: MCP response date/time parsing.
- **`elicitationValidation.ts`**: validates MCP elicitation request/response schemas.

### `utils/messages/` (2 files)
- **`mappers.ts`**: message type mapping for protocol conversion.
- **`systemInit.ts`**: system initialization message generation.

### `utils/filePersistence/` (2 files)
- **`filePersistence.ts`**: persists generated/modified file state across sessions.
- **`outputsScanner.ts`**: scans tool outputs for file paths to track.

### `utils/ultraplan/` (2 files)
- **`keyword.ts`**: **`hasUltraplanKeyword()`**, **`replaceUltraplanKeyword()`** — detects and transforms UltraPlan trigger words in user input.
- **`ccrSession.ts`**: CCR (Cross-Computer Resume) session management for UltraPlan.

### `utils/memory/` (2 files)
- **`types.ts`**: **`MemoryType`** — memory file type definitions.
- **`versions.ts`**: memory file versioning support.

### `utils/todo/` (1 file)
- **`types.ts`**: **`TodoList`** type — todo item structure with status, content, priority.

### `utils/github/` (1 files)
- **`githubRepoPathMapping.ts`**: maps GitHub repository names to local paths.

### `utils/skills/` (1 file)
- Skill utility functions (likely skill loading/registration helpers).

### `utils/plugins/` (44 files)
- **Plugin loader**: `pluginLoader.ts` — discovers and loads plugins from disk.
- **Marketplace**: `marketplaceManager.ts`, `officialMarketplace.ts`, `officialMarketplaceGcs.ts`, `parseMarketplaceInput.ts` — plugin marketplace discovery and installation.
- **Installation**: `pluginInstallationHelpers.ts`, `headlessPluginInstall.ts`, `installCounts.ts` — plugin install/uninstall lifecycle.
- **Validation**: `validatePlugin.ts`, `pluginBlocklist.ts`, `pluginFlagging.ts`, `orphanedPluginFilter.ts` — security and quality validation.
- **Dependency management**: `dependencyResolver.ts`, `pluginVersioning.ts`, `pluginAutoupdate.ts` — semver resolution and updates.
- **Startup**: `performStartupChecks.tsx`, `pluginStartupCheck.ts`, `officialMarketplaceStartupCheck.ts` — startup validation.
- **Plugin features**: `loadPluginAgents.ts`, `loadPluginCommands.ts`, `loadPluginHooks.ts`, `loadPluginOutputStyles.ts` — loads feature bundles from plugins.
- **Settings**: `pluginOptionsStorage.ts`, `addDirPluginSettings.ts` — per-plugin settings persistence.
- **Schemas**: `schemas.ts` — plugin manifest Zod schemas, marketplace metadata schemas.
- **Other**: `cacheUtils.ts`, `zipCache.ts`, `zipCacheAdapters.ts`, `managedPlugins.ts`, `pluginPolicy.ts`, `lspPluginIntegration.ts`, `lspRecommendation.ts`, `mcpbHandler.ts`, `mcpPluginIntegration.ts`, `walkPluginMarkdown.ts`, `pluginIdentifier.ts`, `reconciler.ts`, `refresh.ts`, `fetchTelemetry.ts`, `gitAvailability.ts`, `hintRecommendation.ts`.

---

## 15. Root-Level Utility Files

### `utils/auth.ts` (~2002 lines)
- **Authentication orchestration** — API key, OAuth, AWS credentials, SSO.
- **`getAPIKey()`**: resolves API key with caching (5-min TTL).
- **`getSubscriptionType()`**: returns user subscription tier (Free, Pro, Max, Team, Enterprise).
- **`isClaudeAISubscriber()`, `isMaxSubscriber()`, `isProSubscriber()`, `isTeamPremiumSubscriber()`**: tier checks.
- **`getClaudeAIOAuthTokens()`**: OAuth token resolution with refresh.
- **`checkAndRefreshOAuthTokenIfNeeded()`**: proactive token refresh.
- **OAuth flow**: `login()`, `logout()`, `checkHasTrustDialogAccepted()`, `getOauthProfileFromOauthToken()`.
- **AWS auth**: `checkStsCallerIdentity()`, `clearAwsIniCache()`, `AwsAuthStatusManager`.
- **API key sources**: environment variable, file descriptor, macOS Keychain, plaintext config, MDM.
- **`preferThirdPartyAuthentication()`**: checks if third-party API key mode is forced.

### `utils/config.ts` (~1817 lines)
- **Global config file management** (`~/.claude.json`).
- **`getGlobalConfig()`**: reads global config with caching and file watching.
- **`saveGlobalConfig()`**: persists config with lockfile-based concurrency.
- **Config sections**: `accounts`, `projects`, `settings`, `theme`, `releaseChannel`, `pastedContents`, `history`, `autoMemApprovals`.
- **`ProjectConfig`**: per-project settings (allowed tools, MCP servers, API preferences, permissions).
- **`HistoryEntry`**, **`PastedContent`**: clipboard history and image paste tracking.
- **`AccountInfo`**: user account metadata (ID, email, org, subscription).
- **`ReleaseChannel`**: `'stable' | 'latest'`.
- **`ThemeSetting`**: light/dark/detected theme.
- File watching for real-time config reload (re-entrancy guard with `insideGetConfig`).

### `utils/startupProfiler.ts` (~194 lines)
- **Startup phase profiling** using `perf_hooks` performance API.
- Two modes:
  1. **Sampled logging**: 100% ant, 0.5% external — logs phase durations to analytics.
  2. **Detailed profiling**: `CLAUDE_CODE_PROFILE_STARTUP=1` — full report with memory snapshots.
- **Phase definitions**: `import_time`, `init_time`, `settings_time`, `total_time`.
- **`profileCheckpoint()`**: records timing checkpoints with optional metadata.
- **`formatTimelineLine()`**: renders profiling timeline to terminal.

### `utils/log.ts` (~362 lines)
- **`getLogDisplayTitle()`**: resolves display title for sessions with fallback logic.
- **`dateToFilename()`**: converts dates to session filename format.
- **`logAPIRequest()`**: logs API request/response for debugging and session replay.
- `CACHE_PATHS` integration for log file location resolution.
- `setLastAPIRequest()`, `setLastAPIRequestMessages()` for request inspection.

### `utils/debug.ts` (~268 lines)
- **`isDebugMode()`**: checks `DEBUG`, `DEBUG_SDK`, `--debug`, `--debug-file` flags.
- **`logForDebugging()`**: conditional logging to debug file with level filtering.
- **`getMinDebugLogLevel()`**: configurable minimum level (`verbose`|`debug`|`info`|`warn`|`error`).
- **`getDebugFilePath()`**: resolves `--debug-file` path or default `~/.claude/debug/` location.
- **`writeToDebugFile()`**: writes buffered debug output with session-scoped log files.
- **`enableDebugMode()`**: runtime debug toggling via `/debug` command.
- **`logAntError()`**: ant-only error logging (DCE'd for external builds).
- **`debugFilter.ts`**: pattern-based debug message filtering.

### `utils/errors.ts` (~238 lines)
- **Error class hierarchy**:
  - `ClaudeError` — base error class (sets `this.name = this.constructor.name`).
  - `MalformedCommandError` — invalid user command syntax.
  - `AbortError` — operation cancelled.
  - `ConfigParseError` — JSON config parse failure (carries filePath + defaultConfig).
  - `ShellError` — shell command failure (carries stdout, stderr, code, interrupted).
  - `TeleportOperationError` — session teleport failure (carries formattedMessage).
  - `TelemetrySafeError` — error with safe/unsafe message separation. Single-arg: same message for user and telemetry. Two-arg: full message (user) + sanitized message (telemetry).
- **`isAbortError()`**: robust abort detection (`AbortError`, `DOMException`, `APIUserAbortError`).
- **`toError()`**: coerces unknown to `Error` (wraps non-Error values).
- **`errorMessage()`**: extracts safe message from any error type.
- **`isENOENT()`**, **`isFsInaccessible()`**: filesystem error classification.
- **`getErrnoCode()`**: extracts POSIX errno from Node.js errors.

### `utils/file.ts` (~584 lines)
- **`File`**: `{ filename, content }`.
- **`pathExists()`**: async path existence check.
- **`readFileSafe()`**: read with error tolerant fallback.
- **`MAX_OUTPUT_SIZE`**: 0.25MB file output cap.
- File write operations with encoding detection, line ending normalization, and atomic writes.

### `utils/path.ts` (~155 lines)
- **`expandPath()`**: resolves `~`, relative, and absolute paths with null-byte security checks. On Windows, converts POSIX paths to Windows format.
- **`sanitizePath()`**: path sanitization for permission checks.
- **`containsPathTraversal()`**: detects `..` traversal attacks.
- **`getDirectoryForPath()`**: resolves the directory containing a path.
- **`normalizePathForConfigKey()`**: normalizes paths for use as config keys.

### `utils/array.ts`
- **`count()`**: counts array elements matching a predicate.
- **`uniq()`**: deduplication via Set.
- **`intersperse()`**: inserts separators between array elements.

### `utils/objectGroupBy.ts`
- **`objectGroupBy()`**: polyfill for `Object.groupBy()` (TC39 proposal).

### `utils/stringUtils.ts` (~235 lines)
- **`capitalize()`**: uppercase first character only (unlike lodash).
- **`plural()`**: singular/plural word selection.
- **`escapeRegExp()`**: escapes regex special characters.
- **`firstLineOf()`**: extracts first line without array allocation.
- **`countCharInString()`**: character counting via indexOf jumps (works with Buffer).

### `utils/format.ts` (~308 lines)
- **`formatFileSize()`**: bytes → human readable (`"1.5KB"`, `"2.3MB"`).
- **`formatDuration()`**: ms → human readable (`"5m 30s"`, `"1h 2m"`).
- **`formatSecondsShort()`**: ms → decimal seconds (`"1.2s"`).
- **`truncateToWidth()`**: width-aware string truncation.
- **`formatMs()`**: brief millisecond formatter for profiling.

### `utils/crypto.ts`
- **`randomUUID`**: re-exports `crypto.randomUUID` with a `browser` field indirection for bun builds (avoids ~500KB `crypto-browserify` polyfill).

### `utils/env.ts` (~347 lines)
- **`getGlobalClaudeFile()`**: resolves `~/.claude.json` with legacy fallback.
- **`hasInternetAccess()`**: connectivity check via `http://1.1.1.1` HEAD request.
- **`detectPackageManagers()`**: discovers npm/yarn/pnpm availability.
- **`detectRuntimes()`**: discovers Node/Python/Ruby/etc. availability.
- **`getEnvironmentInfo()`**: comprehensive environment fingerprint gathering.

### `utils/process.ts`
- **`registerProcessOutputErrorHandlers()`**: handles EPIPE on SIGPIPE (prevents memory leak from broken pipes, e.g., `claude -p | head -1`).
- **`writeToStdout()`**, **`writeToStderr()`**: safe stream writes checking `.destroyed`.
- **`exitWithError()`**: `console.error` + `process.exit(1)` fast-path.
- **`peekForStdinData()`**: waits for stdin data with timeout (used by -p mode to distinguish pipe from idle stdin).

### `utils/envUtils.ts`
- **`getClaudeConfigHomeDir()`**: resolves `~/.claude` with XDG fallback.
- **`isEnvTruthy()`**: checks if env var is `'1'`, `'true'`, `'yes'`.
- **`isEnvDefinedFalsy()`**: checks if env var is `'0'`, `'false'`, `'no'`.
- **`isBareMode()`, `isRunningOnHomespace()`**: environment detection helpers.

### `utils/platform.ts`
- **`getPlatform()`**: returns `'win32' | 'darwin' | 'linux'`.
- **`getWslVersion()`**: detects WSL 1 vs WSL 2.

### `utils/feature.ts` / GrowthBook Integration
- `getFeatureValue_CACHED_MAY_BE_STALE()` — cached feature flag lookup.
- `getFeatureValue_CACHED_WITH_REFRESH()` — cached with background refresh.
- `checkStatsigFeatureGate_CACHED_MAY_BE_STALE()` — boolean gate check.
- Located in `services/analytics/growthbook.ts`, imported throughout utils.

### More Root Utilities (Single-File)

| File | Purpose |
|------|---------|
| `utils/envDynamic.ts` | Dynamic environment resolution (runtime-only env vars). |
| `utils/envValidation.ts` | Validates required environment variables. |
| `utils/abortController.ts` | AbortController helpers for cancellable operations. |
| `utils/cleanupRegistry.ts` | Global cleanup function registry for graceful shutdown. |
| `utils/gracefulShutdown.ts` | SIGINT/SIGTERM handler with shutdown state tracking. |
| `utils/lockfile.ts` | PID-based file locking for concurrent access prevention. |
| `utils/memoize.ts` | Memoization utilities: `memoizeWithLRU()`, `memoizeWithTTLAsync()`. |
| `utils/json.ts` | `safeParseJSON()`, `parseJSONL()` — error-tolerant JSON parsing. |
| `utils/slowOperations.ts` | `jsonParse()`, `jsonStringify()` — with performance profiling. |
| `utils/execFileNoThrow.ts` | `execFileNoThrow()` — spawns processes without throwing. |
| `utils/which.ts` | `which()` / `whichSync()` — finds executables in PATH. |
| `utils/sleep.ts` | `sleep(ms)` — promise-based delay. |
| `utils/sequential.ts` | Sequential async execution helpers. |
| `utils/queueProcessor.ts` | Background queue processing with retry. |
| `utils/uuid.ts` | UUID v4 generation. |
| `utils/userAgent.ts` | HTTP user-agent string construction. |
| `utils/user.ts` | Current user info (username, home dir). |
| `utils/xml.ts` | XML parsing/serialization utilities. |
| `utils/yaml.ts` | YAML parsing/serialization utilities. |
| `utils/jsonRead.ts` | JSON file reading with BOM stripping. |
| `utils/diff.ts` | Diff/patch utilities for file edits. |
| `utils/tokens.ts` | Token counting and estimation. |
| `utils/tokenBudget.ts` | Token budget tracking and enforcement. |
| `utils/context.ts` | Context window size detection. |
| `utils/thinking.ts` | Thinking/extended thinking configuration. |
| `utils/effort.ts` | Effort level (`EffortValue`) for budget reasons. |
| `utils/truncate.ts` | Width-aware ANSI-safe string truncation. |
| `utils/sliceAnsi.ts` | ANSI-escape-aware string slicing. |
| `utils/markdown.ts` | Markdown rendering and parsing. |
| `utils/promptCategory.ts` | Prompt category classification. |
| `utils/sanitization.ts` | Content sanitization (PII, paths, credentials). |
| `utils/tempfile.ts` | Temporary file creation and cleanup. |
| `utils/stream.ts` | Stream processing utilities. |
| `utils/signal.ts` | AbortSignal helpers and `createCombinedAbortSignal()`. |
| `utils/timeouts.ts` | Timeout constants and helpers. |
| `utils/cachePaths.ts` | `CACHE_PATHS` — centralized cache directory resolution. |
| `utils/fingerprint.ts` | Device/installation fingerprint generation. |
| `utils/proxy.ts` | HTTP/HTTPS proxy detection and configuration. |
| `utils/mtls.ts` | Mutual TLS certificate configuration. |
| `utils/caCerts.ts` | Custom CA certificate bundle loading. |
| `utils/semver.ts` | Semver parsing and comparison. |
| `utils/semanticBoolean.ts`, `utils/semanticNumber.ts` | Config value coercion helpers. |
| `utils/lazySchema.ts` | `lazySchema()` — Zod lazy schema wrapper with type safety. |
| `utils/zodToJsonSchema.ts` | Zod schema → JSON Schema conversion. |
| `utils/xdg.ts` | XDG Base Directory specification compliance. |
| `utils/windowsPaths.ts` | Windows path utilities (`posixPathToWindowsPath()`, `findGitBashPath()`). |
| `utils/worktree.ts` | Git worktree management. |
| `utils/worktreeModeEnabled.ts` | Worktree mode feature gate. |
| `utils/fsOperations.ts` | Filesystem operation abstraction with platform-specific implementations. |
| `utils/fileRead.ts` | File reading with encoding detection (`detectEncodingForResolvedPath()`, `detectLineEndingsForString()`). |
| `utils/fileReadCache.ts` | File read result caching. |
| `utils/fileStateCache.ts` | File state/metadata caching. |
| `utils/ripgrep.ts` | ripgrep integration for fast file search. |
| `utils/browser.ts` | Browser launch utilities. |
| `utils/editor.ts` | External editor integration. |
| `utils/terminal.ts` | Terminal interaction utilities. |
| `utils/api.ts` | API client configuration. |
| `utils/apiPreconnect.ts` | Pre-connection warming for API endpoints. |
| `utils/ansiToPng.ts`, `utils/ansiToSvg.ts` | ANSI terminal output to image conversion. |
| `utils/asciicast.ts` | Asciicast recording and playback. |
| `utils/binaryCheck.ts` | Binary file detection. |
| `utils/conversationRecovery.ts` | Session conversation recovery from interrupted states. |
| `utils/crossProjectResume.ts` | Cross-project session resume support. |
| `utils/cwd.ts` | Current working directory tracking. |
| `utils/detectRepository.ts` | Git repository detection from cwd. |
| `utils/ide.ts` | IDE integration (VS Code, JetBrains). |
| `utils/idePathConversion.ts` | IDE-to-filesystem path conversion. |
| `utils/ink.ts` | Ink (React for CLI) rendering utilities. |
| `utils/intl.ts` | Internationalization helpers (timezone, relative time formatting). |
| `utils/notebook.ts` | Jupyter notebook integration. |
| `utils/pdf.ts`, `utils/pdfUtils.ts` | PDF handling and validation. |
| `utils/plans.ts` | Plan mode persistence. |
| `utils/preflightChecks.tsx` | Pre-startup environment validation checks. |
| `utils/privacyLevel.ts` | Privacy/telemetry preference detection. |
| `utils/releaseNotes.ts` | Release notes display. |
| `utils/systemPrompt.ts` | System prompt assembly. |
| `utils/systemPromptType.ts` | System prompt type classification. |
| `utils/theme.ts` | Terminal theme detection. |
| `utils/toolPool.ts` | Tool execution pooling. |
| `utils/toolErrors.ts` | Tool error classification. |
| `utils/toolSchemaCache.ts` | Cached tool schema resolution. |
| `utils/toolSearch.ts` | Tool search/filter utilities. |
| `utils/toolResultStorage.ts` | Tool result file persistence. |
| `utils/transcriptSearch.ts` | Transcript content search. |
| `utils/treeify.ts` | Tree structure rendering. |
| `utils/warningHandler.ts` | Warning message handling. |
| `utils/words.ts` | Word list utilities. |

---

## Architecture Patterns

### Import Convention
- Named imports from file paths (not barrel re-exports).
- `import { logForDebugging } from './debug.js'` (`.js` extension in source, bundled as ESM).
- Selective `lodash-es` imports: `import memoize from 'lodash-es/memoize.js'`.
- `bun:bundle` feature flags for dead-code elimination: `import { feature } from 'bun:bundle'`.

### Caching Strategy
- **Memoization**: `lodash memoize`, custom `memoizeWithLRU()`, `memoizeWithTTLAsync()`.
- **Session-scoped caches**: `settingsCache.ts`, `sessionEnvironment.ts`.
- **Per-source caches**: deduplicate settings reads across the cascade.
- **Path-keyed caches**: avoid redundant Zod parse of the same file.

### Error Patterns
- **`ClaudeError`** base class with dynamic `this.name`.
- **`TelemetrySafeError`**: dual-message design for safe telemetry reporting.
- **`toError()`**: universal unknown→Error coercion.
- **Error classification**: `isENOENT()`, `isAbortError()`, `getErrnoCode()`.

### Security Patterns
- **Fail-closed**: AST analysis refuses to interpret unrecognized node types.
- **Salted placeholders**: random bytes in placeholder strings prevent injection.
- **Workspace trust gating**: all hooks and file operations require trust dialog acceptance.
- **Managed policy override**: MDM/local policies supersede user settings.
- **Null-byte checks**: path utilities reject `\0` bytes.
- **SSRF guard**: HTTP hook URLs validated against internal network access.

### Feature Flags
- **Build-time**: `bun:bundle` `feature()` calls, dead-code eliminated for external builds.
- **Runtime**: GrowthBook Statsig feature gates with cached and blocking variants.
- **Environment**: `isEnvTruthy()` checks for opt-in features.

### Module Dependencies
```
utils/ (shared infrastructure)
  ↑ consumed by:
  tools/ (tool implementations)
  services/ (API, analytics, MCP, OAuth)
  hooks/ (React Ink components)
  state/ (AppState selectors/actions)
  entrypoints/ (CLI, SDK)
```

Utils are leaf-free: they may import from `types/`, `constants/`, `schemas/`, and `bootstrap/state.js` but never from `tools/`, `services/`, `hooks/`, or `components/`.
