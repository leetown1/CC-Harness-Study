# Shell Execution Tools

Two shell execution tools for running commands: BashTool (Unix/macOS/Linux) and PowerShellTool (Windows). Together they provide the primary command execution surface.

---

## BashTool (`src/tools/BashTool/BashTool.tsx`, 1144 lines)

**Name**: `BASH_TOOL_NAME`
**Search Hint**: Not set (always loaded, not deferred)
**Concurrency Safe**: No
**Read Only**: No (default)
**Max Result Size**: Implicitly capped by output truncation
**Strict Mode**: Not set

The most complex tool in the system. Handles shell command execution with backgrounding, sandbox, progress tracking, sed-edit integration, and multiple safety layers.

### Input Schema

The model-facing schema omits `_simulatedSedEdit` (internal-only field set by SedEditPermissionRequest after user approval). When background tasks are disabled, `run_in_background` is also omitted. The full internal schema:

```typescript
z.strictObject({
  command: z.string(),                           // The shell command
  timeout: z.number().optional(),                // Max timeout ms (up to getMaxTimeoutMs())
  description: z.string().optional(),            // Human-readable description
  run_in_background: z.boolean().optional(),     // Background execution
  dangerouslyDisableSandbox: z.boolean().optional(), // Override sandbox
  _simulatedSedEdit: z.object({                  // INTERNAL ONLY
    filePath: z.string(),
    newContent: z.string()
  }).optional()
})
```

### Output Schema

Wraps `ShellResult` from the exec system with structured fields for display and model consumption.

### Core Execution Flow

**1. Permission Check** (`checkPermissions`):
- Delegates to `bashToolHasPermission()` in `bashPermissions.ts`
- Path-based: extracts working directory prefixes, supports chained callbacks
- Supports `commandHasAnyCd()` detection for directory-changing commands

**2. Input Validation**:
- `parseForSecurity(command)` — AST-based command parsing for security analysis
- Read-only validation via `checkReadOnlyConstraints()`
- Permission mode validation via `modeValidation.ts`
- Descriptions are checked to be user-provided (not model-generated) for certain commands

**3. Execution** (complex multi-path):

```
call()
  ├── _simulatedSedEdit handling (sed edit preview path)
  │   └── Direct file write via writeTextContent + readFileState update
  ├── Sandbox check: shouldUseSandbox()
  │   └── If sandboxed: runs via SandboxManager
  ├── Background check:
  │   ├── Explicit run_in_background → spawnShellTask()
  │   ├── Auto-background (assistant mode, >15s) → spawnShellTask()
  │   └── Not allowed (disallowed commands like `sleep`) → foreground
  ├── Foreground execution: registerForeground() → exec() → unregisterForeground()
  └── Progress tracking: PROGRESS_THRESHOLD_MS (2s) before showing spinner
```

**4. Post-Execution**:
- `interpretCommandResult()` — interprets exit codes, stderr patterns
- Image output detection via `isImageOutput()` + `resizeShellImageOutput()`
- `stripEmptyLines()` + `stdErrAppendShellResetMessage()` for stderr
- `resetCwdIfOutsideProject()` — detects and resets `cd` outside project
- `backgroundExistingForegroundTask()` — coordinator task backgrounding
- `trackGitOperations()` — git safety/danger tracking
- `extractClaudeCodeHints()` — parses Claude Code directive hints in output
- `maybeRecordPluginHint()` — suggests plugin installation from command usage
- `detectCodeIndexingFromCommand()` — detects code indexing operations

### Command Classification

Three classification functions analyze command strings for UI display:

#### `isSearchOrReadBashCommand(command)`
Returns `{ isSearch, isRead, isList }`. Parses command pipelines with operators (`&&`, `||`, `|`, `;`), skips semantic-neutral commands (`echo`, `printf`, `true`, `false`, `:`), and classifies the remaining parts:

- **Search commands**: `find`, `grep`, `rg`, `ag`, `ack`, `locate`, `which`, `whereis`
- **Read commands**: `cat`, `head`, `tail`, `less`, `more`, `wc`, `stat`, `file`, `strings`, `jq`, `awk`, `cut`, `sort`, `uniq`, `tr`
- **List commands**: `ls`, `tree`, `du`

All non-neutral parts must be search/read/list for the pipeline to be collapsible.

#### `isSilentBashCommand(command)`
Returns `true` for commands that typically produce no stdout on success: `mv`, `cp`, `rm`, `mkdir`, `rmdir`, `chmod`, `chown`, `chgrp`, `touch`, `ln`, `cd`, `export`, `unset`, `wait`.

### Background Execution

Two thresholds control backgrounding:

- `PROGRESS_THRESHOLD_MS` = 2,000ms — Show progress spinner after this duration
- `ASSISTANT_BLOCKING_BUDGET_MS` = 15,000ms — Auto-background after this duration in assistant mode (not non-interactive)

**Disallowed auto-background commands**: `sleep` (should run foreground unless explicitly backgrounded).

`isBackgroundTasksDisabled` gates the entire background feature via `CLAUDE_CODE_DISABLE_BACKGROUND_TASKS` env var.

### Sed Edit Integration

The `_simulatedSedEdit` internal field allows the SedEditPermissionRequest flow to pre-compute the edit result during the sandbox preview. After user approval, `call()` detects the field and writes directly to disk without re-running sed in a sandbox.

### Sub-files (17 supplementary files)

#### `bashPermissions.ts`
Permission checking pipeline for Bash commands:
- `bashToolHasPermission()` — Entry point; extracts command prefix and delegates
- `commandHasAnyCd()` — Detects `cd` in command pipelines
- `matchWildcardPattern()` — Pattern matching for permission rules
- `permissionRuleExtractPrefix()` — Extracts command substring for permission rule matching

#### `bashSecurity.ts`
Command security validation:
- AST-based parsing via `parseForSecurity()`
- Detects dangerous patterns, privilege escalation, network operations
- Integrates with the permission system

#### `commandSemantics.ts`
Exit code interpretation:
- `interpretCommandResult()` — Maps exit codes + stderr patterns to semantic meanings
- Distinguishes between "command failed" and "command succeeded with warnings"

#### `readOnlyValidation.ts`
Read-only classification:
- `checkReadOnlyConstraints()` — Analyzes command for write operations
- Determines whether the command is read-only for permission bypass decisions

#### `modeValidation.ts`
Permission mode validation:
- Checks whether the command is allowed under the current permission mode
- Handles mode-specific restrictions (e.g., default vs. acceptEdits)

#### `pathValidation.ts`
Path constraint checking:
- Validates file paths accessed by the command against working directory boundaries
- Ensures commands don't escape the allowed filesystem scope

#### `destructiveCommandWarning.ts`
Git/branch danger detection:
- Identifies destructive git operations (force push, hard reset, branch deletion)
- Triggers explicit user warnings through the permission system

#### `shouldUseSandbox.ts`
Sandbox determination:
- Analyzes command risk level to decide whether sandboxing is appropriate
- Considers command type, filesystem access patterns, and environment configuration

#### `sedEditParser.ts` + `sedValidation.ts`
sed command handling:
- `parseSedEditCommand()` — Parses sed commands to extract file path + operation
- Validates sed edit patterns against actual file contents
- Powers the sed edit preview UI

#### `commentLabel.ts`
Generates rich comment labels for generated/modified files.

#### `bashCommandHelpers.ts`
Utility functions for command string manipulation, tokenization, and display.

#### `toolName.ts`
Exports `BASH_TOOL_NAME` constant.

#### `UI.tsx`
Rendering components:
- `userFacingName` — "Bash"
- `renderToolUseMessage` — Command display with syntax highlighting
- `renderToolResultMessage` — Result display with output, duration, exit code
- `renderToolUseProgressMessage` — Live progress with spinner
- `renderToolUseQueuedMessage` — Queued state indicator
- `renderToolUseErrorMessage` — Error display
- `BackgroundHint` — Background task notification component

#### `BashToolResultMessage.tsx`
Specialized result message component with:
- Output truncation for large results
- File persistence when output exceeds threshold
- Preview generation via `generatePreview()`
- Full-screen expand affordance

#### `utils.ts`
Shared utilities:
- `buildImageToolResult()` — Image output construction
- `isImageOutput()` — Image output detection
- `resizeShellImageOutput()` — Image resize for display
- `resetCwdIfOutsideProject()` — CWD reset logic
- `stdErrAppendShellResetMessage()` — Stderr message formatting
- `stripEmptyLines()` — Output cleanup

---

## PowerShellTool (`src/tools/PowerShellTool/`, 14 files)

**Name**: `POWERSHELL_TOOL_NAME`
**Concurrency Safe**: No
**Read Only**: No
**Available**: Windows only (`isPowerShellToolEnabled()`)

A Windows-specific shell execution tool that mirrors BashTool's architecture but adapts to PowerShell's execution model, security constraints, and canonical cmdlet resolution.

### Sub-files

#### `PowerShellTool.tsx`
Main tool implementation. Core execution flow:
1. **Canonical cmdlet resolution**: Maps aliases and shorthand to full PowerShell cmdlet names for security analysis
2. **Constrained Language Mode**: Runs PowerShell in CLM for security hardening
3. **Command parsing**: PowerShell-aware AST parsing for security and classification
4. **Execution**: Uses PowerShell's `-Command` invocation with proper escaping
5. **Progress tracking**: Mirrors BashTool's 2s threshold
6. **Background support**: Same `run_in_background` pattern as BashTool

#### `clmTypes.ts`
Constrained Language Mode type definitions:
- Defines the types allowed in CLM (signed scripts, approved modules, specific cmdlets)
- Used for runtime validation of PowerShell execution policy

#### `commonParameters.ts`
PowerShell common parameter handling:
- Maps standard PowerShell common parameters (`-Verbose`, `-Debug`, `-ErrorAction`, etc.)
- Validates parameter combinations against PowerShell specification

#### `powershellPermissions.ts`
Permission checking pipeline:
- Canonical name resolution for permission matching
- Cmdlet prefix extraction for rule-based permission checks
- Integration with the general permission system

#### `powershellSecurity.ts`
Command security validation:
- PowerShell-specific dangerous operation detection
- Module loading analysis
- Script block validation

#### `readOnlyValidation.ts`
Read-only classification for PowerShell:
- Analyzes cmdlets for read vs. write operations
- Considers piped output, redirection, and file operations

#### `modeValidation.ts`
Permission mode validation for PowerShell-specific scenarios:
- Handles PowerShell-specific permission constraints
- Mode-specific restrictions

#### `pathValidation.ts`
Path constraint checking for PowerShell commands:
- Validates paths accessed by PowerShell cmdlets
- Handles PowerShell-specific path formats (PSDrives, provider paths)

#### `gitSafety.ts`
Git safety analysis for PowerShell:
- Detects dangerous git operations executed through PowerShell
- Matches BashTool's git safety patterns

#### `commandSemantics.ts`
Exit code interpretation for PowerShell:
- Maps PowerShell exit codes to semantic meanings
- Handles `$LASTEXITCODE` and `$?` patterns

#### `destructiveCommandWarning.ts`
Destructive command detection for PowerShell:
- Identifies irreversible PowerShell operations
- Triggers user warnings through the permission system

#### `prompt.ts`
Tool description and prompt generation:
- PowerShell-specific usage instructions
- Canonical cmdlet naming guidelines
- Security constraint documentation

#### `toolName.ts`
Exports `POWERSHELL_TOOL_NAME` constant.

#### `UI.tsx`
Rendering components:
- `userFacingName` — "PowerShell"
- `renderToolUseMessage` — Cmdlet display with PowerShell-aware syntax highlighting
- `renderToolResultMessage` — Result display with output, duration, exit code
- `renderToolUseProgressMessage` — Live progress
- `renderToolUseErrorMessage` — Error display

### Key Differences from BashTool

| Aspect | BashTool | PowerShellTool |
|--------|----------|----------------|
| Execution Model | Shell process with command string | PowerShell process with `-Command` |
| Sandbox | Optional via SandboxManager | Via Constrained Language Mode |
| Aliases | Direct shell aliases | Canonical cmdlet resolution required |
| Security | AST-based parse | CLM + AST + cmdlet allowlisting |
| Path Model | POSIX paths | PSDrive + provider paths |
| Platform | Unix/macOS/Linux | Windows only |
| Deferred Loading | No | Conditional (Windows only) |
