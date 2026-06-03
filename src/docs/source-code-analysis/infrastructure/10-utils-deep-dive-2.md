# Utils Deep-Dive 2: Advanced Utilities & Tool Prompts

> Comprehensive reference for Group 1–6 utility modules and tool files.
> Covers input routing, suggestions, secure storage, PowerShell parsing, misc utilities, and tool prompts.

---

## Table of Contents

1. [Group 1: User Input Processing (`utils/processUserInput/`)](#group-1-user-input-processing)
2. [Group 2: Suggestions & Autocomplete (`utils/suggestions/`)](#group-2-suggestions--autocomplete)
3. [Group 3: Secure Storage (`utils/secureStorage/`)](#group-3-secure-storage)
4. [Group 4: PowerShell Parsing & Security (`utils/powershell/`)](#group-4-powershell-parsing--security)
5. [Group 5: Small Utilities](#group-5-small-utilities)
6. [Group 6: Tool Prompt & Output Files](#group-6-tool-prompt--output-files)

---

## Group 1: User Input Processing

**Directory**: `F:\Claude\src\utils\processUserInput\`
**Files**: 4 total (605 + 140 + 922 + 100 = 1,767 lines)

### `processUserInput.ts` (605 lines)

**Purpose**: Primary entry point for classifying and routing all user input. Orchestrates the decision tree: bash commands (`!` prefix), slash commands (`/` prefix), ultraplan keyword detection, and regular text prompts.

#### Types

| Type | Description |
|------|-------------|
| `ProcessUserInputContext` | `ToolUseContext & LocalJSXCommandContext` — union of two core context types |
| `ProcessUserInputBaseResult` | Return type containing `messages`, `shouldQuery`, optional `allowedTools`, `model`, `effort`, `resultText`, `nextInput`, `submitNextInput` |

#### Exported Functions

| Function | Signature | Description |
|----------|-----------|-------------|
| `processUserInput()` | `async (options: {...}) => Promise<ProcessUserInputBaseResult>` | Main entry point. Runs hooks, handles blocking errors, additional contexts, and truncation. Options include `input`, `preExpansionInput`, `mode`, `setToolJSX`, `context`, `pastedContents`, `ideSelection`, `messages`, `uuid`, `isAlreadyProcessing`, `querySource`, `canUseTool`, `skipSlashCommands`, `bridgeOrigin`, `isMeta`, `skipAttachments` |

#### Internal Functions

| Function | Description |
|----------|-------------|
| `processUserInputBase()` (281) | Core routing logic. Handles image processing, bridge-safe slash commands, ultraplan keyword detection, bash mode, slash commands, and regular prompts |
| `addImageMetadataMessage()` (592) | Appends isMeta user message with image metadata texts |
| `applyTruncation()` (274) | Truncates hook output at `MAX_HOOK_OUTPUT_LENGTH` (10,000 chars) |

#### Input Routing Decision Tree (in `processUserInputBase`)

1. **Image processing**: If input is `ContentBlockParam[]`, resize/downsample each image block, extract text from last block
2. **Pasted image processing**: Resize pasted images in parallel, store to disk, collect metadata
3. **Bridge-safe slash commands**: If `bridgeOrigin` + starts with `/`, check `isBridgeSafeCommand()`. Unsafe commands get an error message
4. **Ultraplan keyword detection**: If `ULTRAPLAN` feature enabled, non-slash-prefixed input containing "ultraplan" keyword routes to `/ultraplan`
5. **Attachment extraction**: Extract `@mentions`, MCP resources, agent mentions (unless `skipAttachments`)
6. **Bash mode** (`mode === 'bash'`): Routes to `processBashCommand()`
7. **Slash command** (starts with `/`): Routes to `processSlashCommand()`
8. **Regular prompt**: Falls through to `processTextPrompt()`

---

### `processBashCommand.tsx` (140 lines)

**Purpose**: Handles `mode === 'bash'` input — the `!` prefix mode where the user wants to run a shell command directly without the model.

#### Exported Function

| Function | Signature | Description |
|----------|-----------|-------------|
| `processBashCommand()` | `async (inputString, precedingInputBlocks, attachmentMessages, context, setToolJSX) => Promise<{messages, shouldQuery}>` | Executes a bash/PowerShell command directly, shows progress UI, returns output |

#### Logic Flow

1. **Shell routing**: Uses `isPowerShellToolEnabled()` + `resolveDefaultShell()` to determine bash vs PowerShell
2. **Progress UI**: Renders `<BashModeProgress>` component, updates on shell progress events
3. **Lazy PowerShell import**: Only `require()`s `PowerShellTool` when `usePowerShell` is true (~300KB chunk saving)
4. **Sandbox override**: Sets `dangerouslyDisableSandbox: true` for user-initiated `!` commands
5. **Output formatting**: Uses `processToolResultBlock()` for stdout, `escapeXml()` for stderr
6. **Error handling**: `ShellError` with `interrupted` flag, generic exceptions

#### Return Shape

```ts
{
  messages: [caveat, userMessage, ...attachmentMessages, resultMessage],
  shouldQuery: false  // Never queries the model
}
```

---

### `processSlashCommand.tsx` (922 lines)

**Purpose**: Handles `/` prefixed commands — the richest and most complex input handler. Supports three command types: `local-jsx` (interactive UI), `local` (sync execution), `prompt` (model-based with fork/inline modes).

#### Types

| Type | Description |
|------|-------------|
| `SlashCommandResult` | `ProcessUserInputBaseResult & { command: Command }` |

#### Exported Functions

| Function | Signature | Description |
|----------|-----------|-------------|
| `processSlashCommand()` | `async (inputString, precedingInputBlocks, imageContentBlocks, attachmentMessages, context, setToolJSX, uuid?, isAlreadyProcessing?, canUseTool?) => Promise<ProcessUserInputBaseResult>` | Main slash command router. Parses command, validates, dispatches to `getMessagesForSlashCommand()` |
| `processPromptSlashCommand()` | `async (commandName, args, commands, context, imageContentBlocks?) => Promise<SlashCommandResult>` | Programmatic prompt-command execution (used by SkillTool) |
| `formatSkillLoadingMetadata()` | `(skillName, progressMessage?) => string` | XML metadata for skill loading messages |
| `looksLikeCommand()` | `(commandName) => boolean` | Validates command name format `[a-zA-Z0-9:_-]` |

#### Command Type Handling (in `getMessagesForSlashCommand()`)

**`local-jsx` commands** (line 551):
- Calls `command.load().then(mod => mod.call(onDone, context, args))`
- Returns a `Promise` that resolves via the `onDone` callback
- Supports `display: 'skip'`, `display: 'system'`, and default display modes
- Handles `isFullscreenEnvEnabled()` for modal dismissals
- Detects `isLocalJSXCommand` for input focus management

**`local` commands** (line 657):
- Synchronous execution: `await command.load()` then `await mod.call(args, context)`
- Supports result types: `'skip'` (no messages), `'compact'` (compaction with preserved messages), `'text'` (display result)
- Handles `isSensitive` commands (args replaced with `***`)

**`prompt` commands** (line 723):
- **Fork mode** (`context === 'fork'`): Executes via `executeForkedSlashCommand()` using `runAgent()`
- **Inline mode**: Executes via `getMessagesForPromptSlashCommand()`
- **Coordinator mode**: Returns skill summary instead of full content (when `CLAUDE_CODE_COORDINATOR_MODE` is set)

#### Forked Command Execution (`executeForkedSlashCommand()` — line 62)

- **Synchronous path**: Runs `runAgent()` in-process, collects progress messages, renders via `renderToolUseProgressMessage()`
- **KAIROS async path**: Background execution with `MCP_SETTLE_TIMEOUT_MS` (10s) wait for MCP connections, then `runAgent({isAsync: true})`, results re-enqueued via `enqueuePendingNotification({isMeta: true})`

#### Constants

| Constant | Value | Description |
|----------|-------|-------------|
| `MCP_SETTLE_POLL_MS` | 200 | Poll interval for MCP server readiness |
| `MCP_SETTLE_TIMEOUT_MS` | 10,000 | Max wait for MCP servers to settle |
| `MAX_HOOK_OUTPUT_LENGTH` | 10,000 | Truncation limit (in `processUserInput.ts`) |

---

### `processTextPrompt.ts` (100 lines)

**Purpose**: Handles regular (non-slash, non-bash) user prompts. The simplest handler.

#### Exported Function

| Function | Signature | Description |
|----------|-----------|-------------|
| `processTextPrompt()` | `(input, imageContentBlocks, imagePasteIds, attachmentMessages, uuid?, permissionMode?, isMeta?) => {messages, shouldQuery}` | Creates user messages from text/images, logs telemetry, sets prompt ID |

#### Logic

1. Generates `promptId` via `randomUUID()`, sets via `setPromptId()`
2. Starts interaction span for telemetry
3. Emits `user_prompt` OTEL event (handles both string and array input shapes)
4. Checks `matchesNegativeKeyword()` and `matchesKeepGoingKeyword()` for analytics
5. If `imageContentBlocks` present: merges text + images into single user message
6. Returns `{ messages: [userMessage, ...attachments], shouldQuery: true }`

---

## Group 2: Suggestions & Autocomplete

**Directory**: `F:\Claude\src\utils\suggestions\`
**Files**: 5 total (567 + 263 + 119 + 55 + 209 = 1,213 lines)

### `commandSuggestions.ts` (567 lines)

**Purpose**: Slash command autocomplete. Uses `fuse.js` for fuzzy matching with weighted keys.

#### Types

| Type | Description |
|------|-------------|
| `CommandSearchItem` | Internal type: `{ descriptionKey, partKey, commandName, command, aliasKey }` |
| `MidInputSlashCommand` | `{ token, startPos, partialCommand }` — slash command found mid-input |

#### Exported Functions

| Function | Signature | Description |
|----------|-----------|-------------|
| `generateCommandSuggestions()` | `(input, commands) => SuggestionItem[]` | Main suggestion generator. On empty query (`/`), categorizes commands (recently used, built-in, user, project, policy, other). On partial query, uses Fuse fuzzy search with sorting |
| `getBestCommandMatch()` | `(partialCommand, commands) => {suffix, fullCommand} \| null` | Finds best prefix-match for inline ghost-text completion |
| `findMidInputSlashCommand()` | `(input, cursorOffset) => MidInputSlashCommand \| null` | Detects `/command` patterns not at position 0 |
| `applyCommandSuggestion()` | `(suggestion, shouldExecute, commands, onInputChange, setCursorOffset, onSubmit) => void` | Applies selected suggestion to input, optionally auto-submits |
| `isCommandInput()` | `(input) => boolean` | Returns `true` if input starts with `/` |
| `hasCommandArgs()` | `(input) => boolean` | Returns `true` if command input has arguments |
| `formatCommand()` | `(command) => string` | Formats `command` → `/command ` |
| `findSlashCommandPositions()` | `(text) => Array<{start, end}>` | Finds all `/command` patterns for syntax highlighting |

#### Fuse Configuration

```ts
{
  threshold: 0.3,     // Relatively strict
  location: 0,        // Prefer matches at string start
  distance: 100,      // Allow matching in descriptions
  keys: [
    { name: 'commandName', weight: 3 },    // Highest priority
    { name: 'partKey', weight: 2 },         // Command parts (e.g., ["git","push"])
    { name: 'aliasKey', weight: 2 },        // Aliases
    { name: 'descriptionKey', weight: 0.5 },// Lowest priority
  ]
}
```

#### Sorting Priority (line 424)

1. Exact name match (highest)
2. Exact alias match
3. Prefix name match (shorter preferred)
4. Prefix alias match (shorter preferred)
5. Fuse score (with usage frequency as tiebreaker)

#### Command Categorization

When typing just `/`:
1. **Recently used** (top 5, filtered by `getSkillUsageScore() > 0`)
2. **Built-in** (`local`/`local-jsx` type, alphabetically)
3. **User** (`userSettings`/`localSettings` source)
4. **Project** (`projectSettings` source)
5. **Policy** (`policySettings` source)
6. **Other** (plugins, MCP, etc.)

---

### `directoryCompletion.ts` (263 lines)

**Purpose**: Filesystem path autocomplete for `@` mentions and file argument completion.

#### Types

| Type | Description |
|------|-------------|
| `DirectoryEntry` | `{ name, path, type: 'directory' }` |
| `PathEntry` | `{ name, path, type: 'directory' \| 'file' }` |
| `CompletionOptions` | `{ basePath?, maxResults? }` |
| `PathCompletionOptions` | `CompletionOptions & { includeFiles?, includeHidden? }` |
| `ParsedPath` | `{ directory, prefix }` |

#### Caches

| Cache | Type | TTL | Max Size |
|-------|------|-----|----------|
| `directoryCache` | `LRUCache<string, DirectoryEntry[]>` | 5 min | 500 |
| `pathCache` | `LRUCache<string, PathEntry[]>` | 5 min | 500 |

#### Exported Functions

| Function | Signature | Description |
|----------|-----------|-------------|
| `parsePartialPath()` | `(partialPath, basePath?) => ParsedPath` | Splits partial path into directory + prefix |
| `scanDirectory()` | `async (dirPath) => Promise<DirectoryEntry[]>` | Scans directory with LRU caching. Filters out hidden dirs, limits to 100 results |
| `getDirectoryCompletions()` | `async (partialPath, options?) => Promise<SuggestionItem[]>` | Main directory completion function |
| `clearDirectoryCache()` | `() => void` | Clears directory cache |
| `isPathLikeToken()` | `(token) => boolean` | Checks if a token starts with `~/`, `/`, `./`, `../`, `~`, `.`, `..` |
| `scanDirectoryForPaths()` | `async (dirPath, includeHidden?) => Promise<PathEntry[]>` | Scans for both files and directories |
| `getPathCompletions()` | `async (partialPath, options?) => Promise<SuggestionItem[]>` | Full path completion (files + dirs) |
| `clearPathCache()` | `() => void` | Clears both caches |

---

### `shellHistoryCompletion.ts` (119 lines)

**Purpose**: Ghost-text completion for bash mode (`!` prefix), suggesting previously used shell commands.

#### Types

| Type | Description |
|------|-------------|
| `ShellHistoryMatch` | `{ fullCommand, suffix }` |

#### Exported Functions

| Function | Signature | Description |
|----------|-----------|-------------|
| `getShellHistoryCompletion()` | `async (input) => Promise<ShellHistoryMatch \| null>` | Finds first history command starting with exact input. Requires input length ≥ 2 |
| `clearShellHistoryCache()` | `() => void` | Clears the history cache |
| `prependToShellHistoryCache()` | `(command) => void` | Adds command to front of cache (used after submission) |

#### Internal Details

- Cache TTL: 60 seconds
- Max history entries: 50
- Only considers entries with `display` starting with `!`
- Exact prefix matching (preserves spaces): `"ls "` matches `"ls -lah"` but `"ls  "` does not

---

### `skillUsageTracking.ts` (55 lines)

**Purpose**: Tracks skill usage frequency and recency for ranking in suggestion lists.

#### Exported Functions

| Function | Signature | Description |
|----------|-----------|-------------|
| `recordSkillUsage()` | `(skillName) => void` | Records a skill usage with debouncing (60s). Updates `usageCount` and `lastUsedAt` in global config |
| `getSkillUsageScore()` | `(skillName) => number` | Calculates score: exponential decay with 7-day half-life, minimum recency factor of 0.1. Formula: `usageCount * max(0.5^(daysSinceUse/7), 0.1)` |

#### Debouncing

- `SKILL_USAGE_DEBOUNCE_MS = 60,000` (1 minute)
- Uses `lastWriteBySkill` Map for process-lifetime debounce cache
- Avoids lock + file I/O on rapid calls

---

### `slackChannelSuggestions.ts` (209 lines)

**Purpose**: Autocomplete for Slack `#channel` mentions when Slack MCP server is connected.

#### Exported Functions

| Function | Signature | Description |
|----------|-----------|-------------|
| `getSlackChannelSuggestions()` | `async (clients, searchToken) => Promise<SuggestionItem[]>` | Fetches Slack channel completions via MCP, with caching and prefix reuse |
| `hasSlackMcpServer()` | `(clients) => boolean` | Checks if a Slack MCP server is connected |
| `getKnownChannelsVersion()` | `() => number` | Returns version for change detection |
| `subscribeKnownChannels` | Signal | Subscribe to known channels updates |
| `findSlackChannelPositions()` | `(text) => Array<{start, end}>` | Finds `#channel` patterns for highlighting |
| `clearSlackChannelCache()` | `() => void` | Clears all caches |

#### Internal Details

- Uses `slack_search_channels` MCP tool with 5s timeout
- Cache: `Map<string, string[]>` (max 50 entries, FIFO eviction)
- Known channels: `Set<string>` for highlighting gate
- Query optimization: Strips trailing partial hyphen/underscore segment for MCP query, filters locally
- Prefix cache reuse: Typing `c` → `cl` → `cla` reuses `c` cache result

---

## Group 3: Secure Storage

**Directory**: `F:\Claude\src\utils\secureStorage\`
**Files**: 6 (but `./types.js` is referenced but not present in this directory — likely defined at a higher level or generated)
**Total lines**: 231 + 111 + 116 + 84 + 70 + 17 = 629

### Architecture Overview

The secure storage system uses a **fallback chain** pattern:
- **macOS**: Keychain (primary) → plaintext (fallback)
- **Other platforms**: plaintext only

The `SecureStorage` interface (imported from `./types.js`) provides:
- `name: string` — storage backend name
- `read(): SecureStorageData | null` — synchronous read
- `readAsync(): Promise<SecureStorageData | null>` — asynchronous read
- `update(data: SecureStorageData): { success: boolean; warning?: string }` — write
- `delete(): boolean` — remove stored data

`SecureStorageData` is the opaque data payload type.

---

### `macOsKeychainStorage.ts` (231 lines)

**Purpose**: macOS Keychain integration using the `security` CLI. Implements `SecureStorage` interface.

#### Exported Object

```ts
macOsKeychainStorage = { name: 'keychain', read, readAsync, update, delete }
// satisfies SecureStorage
```

#### Key Implementation Details

- **Service name**: `getMacOsKeychainStorageServiceName(CREDENTIALS_SERVICE_SUFFIX)` — e.g., `"Claude Code-credentials"`
- **Username**: `getUsername()` (from `$USER` or `os.userInfo().username`)
- **Stdin line limit**: `SECURITY_STDIN_LINE_LIMIT = 4096 - 64` — when payload exceeds this, falls back to argv (hex-encoded)
- **Payload encoding**: Hex-encoded JSON (`-X` flag) to avoid escaping issues
- **Cache**: `keychainCacheState` with `KEYCHAIN_CACHE_TTL_MS = 30,000`, `generation` counter, and `readInFlight` deduplication
- **Stale-while-error**: If read fails, serves stale data (if available) rather than caching `null`

#### Exported Functions

| Function | Signature | Description |
|----------|-----------|-------------|
| `isMacOsKeychainLocked()` | `() => boolean` | Checks if macOS keychain is locked (exit code 36). Cached for process lifetime. Only runs on `darwin` |

#### Async Reads

`readAsync()` uses `execFileNoThrow()` instead of sync `execSyncWithDefaults_DEPRECATED()`. Deduplicates concurrent calls via `keychainCacheState.readInFlight` promise.

#### Update Flow

1. Invalidate cache (`clearKeychainCache()`)
2. Serialize data as JSON hex string
3. If `command.length <= SECURITY_STDIN_LINE_LIMIT`: use `security -i` with stdin (hides payload from process monitors)
4. Else: use argv (with hex payload)
5. Update cache on success

---

### `macOsKeychainHelpers.ts` (111 lines)

**Purpose**: Lightweight helpers shared between `keychainPrefetch.ts` and `macOsKeychainStorage.ts`. Must NOT import heavy modules (`execa`, `execaFileNoThrow`) to avoid defeating the prefetch optimization (~58ms sync module init).

#### Constants

| Constant | Value | Description |
|----------|-------|-------------|
| `CREDENTIALS_SERVICE_SUFFIX` | `'-credentials'` | Suffix for OAuth keychain entry (never change — orphaning risk) |
| `KEYCHAIN_CACHE_TTL_MS` | `30,000` | Cross-process staleness tolerance |

#### Exported Functions

| Function | Signature | Description |
|----------|-----------|-------------|
| `getMacOsKeychainStorageServiceName()` | `(serviceSuffix?) => string` | Builds service name: `"Claude Code{OAUTH_FILE_SUFFIX}{serviceSuffix}{dirHash}"`. Hash uses SHA-256 first 8 chars of config dir (only for non-default dirs) |
| `getUsername()` | `() => string` | Returns `$USER` or `os.userInfo().username`, fallback `'claude-code-user'` |
| `clearKeychainCache()` | `() => void` | Invalidates cache, increments generation, clears in-flight promise |
| `primeKeychainCacheFromPrefetch()` | `(stdout: string \| null) => void` | Primes cache from prefetch result (only if untouched) |

#### Exported State

```ts
keychainCacheState: {
  cache: { data: SecureStorageData | null, cachedAt: number },
  generation: number,       // Incremented on invalidation
  readInFlight: Promise<...> | null  // Concurrent call dedup
}
```

---

### `keychainPrefetch.ts` (116 lines)

**Purpose**: Fires macOS keychain reads in parallel with `main.tsx` module evaluation (~65ms head start). Same pattern as MDM raw read.

#### Exported Functions

| Function | Signature | Description |
|----------|-----------|-------------|
| `startKeychainPrefetch()` | `() => void` | Fires both OAuth + legacy reads immediately (non-blocking). No-op on non-darwin / bare mode |
| `ensureKeychainPrefetchCompleted()` | `async () => Promise<void>` | Awaits prefetch completion (called in `main.tsx` preAction) |
| `getLegacyApiKeyPrefetchResult()` | `() => {stdout: string \| null} \| null` | Consumed by `getApiKeyFromConfigOrMacOSKeychain()` |
| `clearLegacyApiKeyPrefetch()` | `() => void` | Clears prefetch on cache invalidation |

#### Internal Details

- `KEYCHAIN_PREFETCH_TIMEOUT_MS = 10,000`
- Two parallel spawns: `spawnSecurity(credentials_service)` + `spawnSecurity(base_service)`
- Timed-out prefetches do NOT prime cache (sync path retries)
- Uses `execFile` from `child_process` (not execa) to avoid heavy import chain

---

### `plainTextStorage.ts` (84 lines)

**Purpose**: Plain text JSON file storage at `~/.claude/.credentials.json`. Used as fallback on macOS and primary on other platforms.

#### Exported Object

```ts
plainTextStorage = { name: 'plaintext', read, readAsync, update, delete }
// satisfies SecureStorage
```

#### Key Details

- **Path**: `join(getClaudeConfigHomeDir(), '.credentials.json')`
- **File permissions**: `chmodSync(0o600)` after write
- **Dir creation**: `mkdirSync()` with `EEXIST` tolerance
- **Delete**: Reports success if file doesn't exist (`ENOENT`)
- **Warning on update**: `"Warning: Storing credentials in plaintext."`

---

### `fallbackStorage.ts` (70 lines)

**Purpose**: Composite storage that chains primary + secondary backends.

#### Exported Function

| Function | Signature | Description |
|----------|-----------|-------------|
| `createFallbackStorage()` | `(primary: SecureStorage, secondary: SecureStorage) => SecureStorage` | Creates a fallback chain storage |

#### Read Logic

1. Try `primary.read()`
2. If null/undefined, try `secondary.read()` (falls back to `{}`)

#### Update Logic

1. Try `primary.update(data)`
2. If success AND primary had no prior data, delete secondary (migration)
3. If failure, try `secondary.update(data)`:
   - If success AND primary had stale data, delete primary

#### Delete Logic

Tries both `primary.delete()` and `secondary.delete()`, returns `true` if either succeeded.

---

### `index.ts` (17 lines)

**Purpose**: Platform-specific storage factory.

#### Exported Function

| Function | Signature | Description |
|----------|-----------|-------------|
| `getSecureStorage()` | `() => SecureStorage` | Returns `createFallbackStorage(macOsKeychainStorage, plainTextStorage)` on darwin, `plainTextStorage` otherwise. Note: libsecret support for Linux is TODO |

---

## Group 4: PowerShell Parsing & Security

**Directory**: `F:\Claude\src\utils\powershell\`
**Files**: 3 total (1,804 + 185 + 316 = 2,305 lines)

### `parser.ts` (1,804 lines)

**Purpose**: Core PowerShell command parser. Spawns `pwsh.exe` with an embedded PowerShell script that uses the native `System.Management.Automation.Language.Parser` to produce structured JSON AST output. The TypeScript side transforms raw output into typed security-relevant data.

#### Type Hierarchy

**AST Node Types**:

```ts
PipelineElementType: 'CommandAst' | 'CommandExpressionAst' | 'ParenExpressionAst'
CommandElementType: 'ScriptBlock' | 'SubExpression' | 'ExpandableString' | 'MemberInvocation' | 'Variable' | 'StringConstant' | 'Parameter' | 'Other'
StatementType: 'PipelineAst' | 'PipelineChainAst' | 'AssignmentStatementAst' | 'IfStatementAst' | 'ForStatementAst' | 'ForEachStatementAst' | 'WhileStatementAst' | 'DoWhileStatementAst' | 'DoUntilStatementAst' | 'SwitchStatementAst' | 'TryStatementAst' | 'TrapStatementAst' | 'FunctionDefinitionAst' | 'DataStatementAst' | 'UnknownStatementAst'
```

**Core Data Types**:

| Type | Key Fields | Description |
|------|------------|-------------|
| `ParsedCommandElement` | `name`, `nameType` ('cmdlet'\|'application'\|'unknown'), `elementType`, `args`, `text`, `elementTypes?`, `children?`, `redirections?` | A single command invocation |
| `ParsedStatement` | `statementType`, `commands`, `redirections`, `text`, `nestedCommands?`, `securityPatterns?` | A parsed statement (pipeline/if/for/etc.) |
| `ParsedVariable` | `path`, `isSplatted` | Variable reference with splatting flag |
| `ParsedRedirection` | `operator` ('>'\|'>>'\|'2>'\|'2>>'\|'*>'\|'*>>'\|'2>&1'), `target`, `isMerging` | I/O redirection |
| `ParsedPowerShellCommand` | `valid`, `errors`, `statements`, `variables`, `hasStopParsing`, `originalCommand`, `typeLiterals?`, `hasUsingStatements?`, `hasScriptRequirements?` | Complete parse result |
| `CommandElementChild` | `type: CommandElementType`, `text: string` | Child node for colon-bound parameters |

#### Constants

| Constant | Value | Description |
|----------|-------|-------------|
| `DEFAULT_PARSE_TIMEOUT_MS` | `5,000` | Default pwsh spawn timeout (overridable via `CLAUDE_CODE_PWSH_PARSE_TIMEOUT_MS`) |
| `MAX_COMMAND_LENGTH` | Platform-dependent | Windows: derived from `WINDOWS_MAX_COMMAND_LENGTH` (~1,092 UTF-8 bytes). Unix: `4,500` UTF-8 bytes |
| `WINDOWS_ARGV_CAP` | `32,767` | Windows CreateProcess command-line limit |
| `FIXED_ARGV_OVERHEAD` | `200` | pwsh path + flags overhead |

#### PS1 Parse Script (`PARSE_SCRIPT_BODY`, ~568 chars, lines 315-568)

The embedded PowerShell script:
1. Decodes `$EncodedCommand` (UTF-8 Base64)
2. Parses via `[Parser]::ParseInput()`
3. Walks AST for: variables, type literals, stop-parsing token (`--%`)
4. Processes named blocks: Begin, Process, End, Clean, DynamicParam
5. Processes `ParamBlock` (script-level params, separate find for security)
6. For each statement: extracts commands, nested commands (FindAll for control flow), redirections, security patterns
7. Outputs JSON via `ConvertTo-Json -Depth 10 -Compress`

#### Exported Functions — Core Parsing

| Function | Signature | Description |
|----------|-----------|-------------|
| `parsePowerShellCommand()` | `async (command: string) => Promise<ParsedPowerShellCommand>` | Main parse function. Uses `memoizeWithLRU` (256 entries). Transient errors auto-evict from cache. Checks command length, resolves pwsh path, builds script, spawns pwsh, retries on timeout (1 retry), parses JSON output |
| `buildParseScript()` | `(command) => string` | Wraps command in Base64 variable for injection protection |
| `toUtf16LeBase64()` | `(text) => string` | Encodes text as UTF-16LE Base64 (required by `-EncodedCommand`) |

#### Exported Functions — Raw-to-Typed Transformation

| Function | Signature | Description |
|----------|-----------|-------------|
| `mapStatementType()` | `(rawType: string) => StatementType` | Maps .NET `GetType().Name` to TS union |
| `mapElementType()` | `(rawType, expressionType?) => CommandElementType` | Maps AST node names. Handles `ArrayExpressionAst` → `SubExpression` (security), `ParenExpressionAst` → `SubExpression`, `ConstantExpressionAst` → `StringConstant` |
| `classifyCommandName()` | `(name: string) => 'cmdlet' \| 'application' \| 'unknown'` | Regex-based classification: `cmdlet` = `Verb-Noun` pattern, `application` = contains `./\` |
| `stripModulePrefix()` | `(name: string) => string` | Strips `Microsoft.PowerShell.Utility\Invoke-Expression` → `Invoke-Expression`. Guards against file paths |
| `transformCommandAst()` | `(raw: RawPipelineElement) => ParsedCommandElement` | Transforms raw CommandAst. Handles name type classification, quote stripping, unicode security gate, module prefix stripping |
| `transformExpressionElement()` | `(raw: RawPipelineElement) => ParsedCommandElement` | Transforms non-CommandAst elements |
| `transformRedirection()` | `(raw: RawRedirection) => ParsedRedirection` | Transforms raw redirections with operator derivation |
| `transformStatement()` | `(raw: RawStatement) => ParsedStatement` | Transforms statements. Handles dedup of FileRedirectionAst from FindAll vs element-level |

#### Exported Functions — Analysis Helpers

| Function | Signature | Description |
|----------|-----------|-------------|
| `getAllCommandNames()` | `(parsed) => string[]` | All command names across statements + nested commands (lowercased) |
| `getAllCommands()` | `(parsed) => ParsedCommandElement[]` | Flat list of all `ParsedCommandElement`s |
| `getAllRedirections()` | `(parsed) => ParsedRedirection[]` | All redirections including nested |
| `getVariablesByScope()` | `(parsed, scope) => ParsedVariable[]` | Filters variables by scope prefix (e.g., `'env'`) |
| `hasCommandNamed()` | `(parsed, name) => boolean` | Case-insensitive name match with alias resolution (bidirectional) |
| `hasDirectoryChange()` | `(parsed) => boolean` | Detects `cd`/`Set-Location`/`Push-Location`/`Pop-Location` |
| `isSingleCommand()` | `(parsed) => boolean` | True if exactly one command in one statement |
| `commandHasArg()` | `(command, arg) => boolean` | Case-insensitive arg match |
| `isPowerShellParameter()` | `(arg, elementType?) => boolean` | Determines if arg is a parameter flag (uses elementType when available, falls back to dash char check) |
| `commandHasArgAbbreviation()` | `(command, fullParam, minPrefix) => boolean` | Checks for PowerShell parameter abbreviation matching |
| `getPipelineSegments()` | `(parsed) => ParsedStatement[]` | Returns statements as pipeline segments |
| `isNullRedirectionTarget()` | `(target) => boolean` | Checks `$null`/`${null}` redirection |
| `getFileRedirections()` | `(parsed) => ParsedRedirection[]` | File redirections only (excludes merging and null targets) |
| `deriveSecurityFlags()` | `(parsed) => SecurityFlags` | Computes 7 security flags from AST: `hasSubExpressions`, `hasScriptBlocks`, `hasSplatting`, `hasExpandableStrings`, `hasMemberInvocations`, `hasAssignments`, `hasStopParsing` |

#### `COMMON_ALIASES` Map (line 1326)

Comprehensive PowerShell alias → canonical cmdlet mapping (~80+ entries), using `Object.create(null)` to prevent prototype pollution. Covers:
- Directory: `ls→Get-ChildItem`, `dir→Get-ChildItem`
- Content: `cat→Get-Content`, `type→Get-Content`
- Navigation: `cd→Set-Location`, `pushd→Push-Location`
- Items: `rm→Remove-Item`, `cp→Copy-Item`
- Process: `kill→Stop-Process`, `ps→Get-Process`
- Output: `echo→Write-Output`, `sleep→Start-Sleep`
- Invoke: `iex→Invoke-Expression`, `iwr→Invoke-WebRequest`
- Deliberately omitted: `sc`, `sort`, `curl`, `wget` (native .exe collisions on PS Core)

---

### `dangerousCmdlets.ts` (185 lines)

**Purpose**: Shared constants of dangerous PowerShell cmdlets consumed by permission-engine validators and UI suggestion gates.

#### Exported Sets

| Set | Members | Description |
|-----|---------|-------------|
| `FILEPATH_EXECUTION_CMDLETS` | `invoke-command`, `start-job`, `start-threadjob`, `register-scheduledjob` | Cmdlets that execute files as scripts via `-FilePath` |
| `DANGEROUS_SCRIPT_BLOCK_CMDLETS` | `invoke-command`, `invoke-expression`, `start-job`, `start-threadjob`, `register-scheduledjob`, `register-engineevent`, `register-objectevent`, `register-wmievent`, `new-pssession`, `enter-pssession` | Cmdlets where ScriptBlock args execute arbitrary code |
| `MODULE_LOADING_CMDLETS` | `import-module`, `ipmo`, `install-module`, `save-module`, `update-module`, `install-script`, `save-script` | Cmdlets that load/execute .psm1 code |
| `NETWORK_CMDLETS` | `invoke-webrequest`, `invoke-restmethod` | Network/exfil cmdlets |
| `ALIAS_HIJACK_CMDLETS` | `set-alias`, `sal`, `new-alias`, `nal`, `set-variable`, `sv`, `new-variable`, `nv` | Alias/variable mutation cmdlets |
| `WMI_CIM_CMDLETS` | `invoke-wmimethod`, `iwmi`, `invoke-cimmethod` | WMI/CIM process spawn |
| `ARG_GATED_CMDLETS` | `select-object`, `sort-object`, `group-object`, `where-object`, `measure-object`, `write-output`, `write-host`, `start-sleep`, `format-table`, `format-list`, `format-wide`, `format-custom`, `out-string`, `out-host`, `ipconfig`, `hostname`, `route` | Allowlist cmdlets with callback-gated args |
| `NEVER_SUGGEST` | Union of all above + `foreach-object` + cross-platform code exec + shells (`pwsh`, `powershell`, `cmd`, `bash`, `wsl`, `sh`, `start-process`, `start`, `add-type`, `new-object`) + all aliases | Commands never suggested as wildcard prefix in permission dialog |

---

### `staticPrefix.ts` (316 lines)

**Purpose**: PowerShell static command prefix extraction for the permission dialog's "don't ask again for ___" editable input. Mirrors bash's `getCommandPrefixStatic`.

#### Exported Functions

| Function | Signature | Description |
|----------|-----------|-------------|
| `getCommandPrefixStatic()` | `async (command) => Promise<{commandPrefix: string \| null} \| null>` | Parses command, takes first `CommandAst`, returns best-guess prefix |
| `getCompoundCommandPrefixesStatic()` | `async (command, excludeSubcommand?) => Promise<string[]>` | For compound commands (e.g., `Get-Process; git status && npm test`), returns per-subcommand prefixes with word-aligned LCP collapse |

#### Internal Functions

| Function | Signature | Description |
|----------|-----------|-------------|
| `extractPrefixFromElement()` | `async (cmd: ParsedCommandElement) => Promise<string \| null>` | Extracts prefix from a single parsed element. Returns `null` for: `application` nameType, items in `NEVER_SUGGEST`, dynamic args, and bare subcommand-aware roots |
| `wordAlignedLCP()` | `(strings: string[]) => string` | Case-insensitive word-aligned longest common prefix. `["npm run test", "npm run lint"]` → `"npm run"` |

#### Prefix Extraction Logic

1. Rejects `nameType === 'application'` (file paths)
2. Rejects names in `NEVER_SUGGEST`
3. For cmdlets: returns name directly (e.g., `Get-Process`)
4. For external commands: validates args are static (no variables/subexpressions), consults fig spec via `getCommandSpec(nameLower)` + `buildPrefix()`
5. Post-build integrity check: verifies prefix words match positional args in order
6. Bare-root guard: rejects single-word results for commands with subcommands (e.g., `git` without subcommand)

#### Compound Collapse

For `get-compoundCommandPrefixesStatic()`:
- Groups prefixes by root command (case-insensitive)
- Collapses each group via `wordAlignedLCP()`
- Rejects collapsed bare-root prefixes for subcommand-aware commands
- Excludes subcommands via optional filter callback

---

## Group 5: Small Utilities

### `utils/dxt/` (2 files)

#### `helpers.ts` (88 lines)

**Purpose**: DXT (Developer eXtension Toolkit) manifest parsing and validation.

| Function | Signature | Description |
|----------|-----------|-------------|
| `validateManifest()` | `async (manifestJson: unknown) => Promise<McpbManifest>` | Validates manifest JSON against `McpbManifestSchema` (lazy-loaded from `@anthropic-ai/mcpb` to defer ~700KB of closure allocations) |
| `parseAndValidateManifestFromText()` | `async (manifestText: string) => Promise<McpbManifest>` | Parses JSON string then validates |
| `parseAndValidateManifestFromBytes()` | `async (manifestData: Uint8Array) => Promise<McpbManifest>` | Decodes UTF-8 then validates |
| `generateExtensionId()` | `(manifest: McpbManifest, prefix?: 'local.unpacked' \| 'local.dxt') => string` | Generates extension ID: sanitizes author.name + name (lowercase, hyphen-replace, strip special chars). Format: `{author}.{name}` or `{prefix}.{author}.{name}` |

#### `zip.ts` (226 lines)

**Purpose**: Safe zip file extraction with zip bomb protection and path traversal prevention.

| Function | Signature | Description |
|----------|-----------|-------------|
| `isPathSafe()` | `(filePath: string) => boolean` | Validates against path traversal and absolute paths |
| `validateZipFile()` | `(file: ZipFileMetadata, state: ZipValidationState) => FileValidationResult` | Validates single file: path safety, file size (max 512MB), total size (max 1GB), file count (max 100K), compression ratio (max 50:1, min 0.5:1) |
| `unzipFile()` | `async (zipData: Buffer) => Promise<Record<string, Uint8Array>>` | Unzips using lazy-loaded `fflate.unzipSync` (avoids ~196KB startup allocation). Validates each file via filter callback |
| `parseZipModes()` | `(data: Uint8Array) => Record<string, number>` | Parses Unix file modes from zip central directory. Walks EOCD → central directory entries, extracts st_mode from external attributes |
| `readAndUnzipFile()` | `async (filePath: string) => Promise<Record<string, Uint8Array>>` | Reads zip from disk then unzips, with error wrapping |

**Limits**:
```ts
MAX_FILE_SIZE: 512 * 1024 * 1024        // 512MB per file
MAX_TOTAL_SIZE: 1024 * 1024 * 1024      // 1024MB total
MAX_FILE_COUNT: 100000                   // Max files
MAX_COMPRESSION_RATIO: 50               // Zip bomb detection
```

---

### `utils/filePersistence/` (2 files)

#### `filePersistence.ts` (287 lines)

**Purpose**: Orchestrator for persisting modified files at end of each turn. BYOC mode uploads to Files API; Cloud mode (1P) reads file IDs from xattr.

| Function | Signature | Description |
|----------|-----------|-------------|
| `runFilePersistence()` | `async (turnStartTime: TurnStartTime, signal?: AbortSignal) => Promise<FilesPersistedEventData \| null>` | Main orchestrator. Checks `CLAUDE_CODE_ENVIRONMENT_KIND === 'byoc'`, session access token, remote session ID. Dispatches to BYOC or Cloud mode |
| `executeFilePersistence()` | `async (turnStartTime, signal, onResult) => Promise<void>` | Wrapper that calls `runFilePersistence()` and emits result via callback |
| `isFilePersistenceEnabled()` | `() => boolean` | Gates on feature flag `FILE_PERSISTENCE` + BYOC env + session token + remote session ID |

**BYOC Flow** (`executeBYOCPersistence`):
1. `findModifiedFiles(turnStartTime, outputsDir)` — local filesystem scan
2. Enforces `FILE_COUNT_LIMIT`
3. Filters out paths resolving outside outputs dir
4. `uploadSessionFiles()` with `DEFAULT_UPLOAD_CONCURRENCY`
5. Returns `{ files: PersistedFile[], failed: FailedPersistence[] }`

#### `outputsScanner.ts` (126 lines)

**Purpose**: Scans `{cwd}/{sessionId}/outputs` directory for files modified since turn start.

| Function | Signature | Description |
|----------|-----------|-------------|
| `logDebug()` | `(message: string) => void` | Debug logger with `[file-persistence]` prefix |
| `getEnvironmentKind()` | `() => EnvironmentKind \| null` | Reads `CLAUDE_CODE_ENVIRONMENT_KIND`, returns `'byoc'` or `'anthropic_cloud'` |
| `findModifiedFiles()` | `async (turnStartTime: TurnStartTime, outputsDir: string) => Promise<string[]>` | Recursive `fs.readdir` with `withFileTypes: true`, parallel `lstat()` calls, filters by `mtimeMs >= turnStartTime`. Skips symlinks |

---

### `utils/mcp/` (2 files)

#### `dateTimeParser.ts` (121 lines)

**Purpose**: Natural language date/time parsing via Haiku model for MCP elicitation.

| Function | Signature | Description |
|----------|-----------|-------------|
| `parseNaturalLanguageDateTime()` | `async (input: string, format: 'date' \| 'date-time', signal: AbortSignal) => Promise<DateTimeParseResult>` | Sends ISO 8601 context to Haiku, extracts parsed date. Validates output starts with `\d{4}`. Returns `{success: true, value}` or error |
| `looksLikeISO8601()` | `(input: string) => boolean` | Checks for `YYYY-MM-DD` pattern |

**Context provided to Haiku**:
- Current UTC datetime
- Local timezone offset
- Day of week

---

#### `elicitationValidation.ts` (336 lines)

**Purpose**: MCP elicitation form input validation using Zod schemas derived from MCP JSON Schema definitions.

| Function | Signature | Description |
|----------|-----------|-------------|
| `isEnumSchema()` | `(schema) => schema is EnumSchema` | Checks for single-select enum (`enum` or `oneOf`) |
| `isMultiSelectEnumSchema()` | `(schema) => schema is MultiSelectEnumSchema` | Checks for multi-select enum (array with items enum/anyOf) |
| `getMultiSelectValues()` | `(schema) => string[]` | Extracts values from multi-select enum |
| `getMultiSelectLabels()` | `(schema) => string[]` | Extracts display labels |
| `getMultiSelectLabel()` | `(schema, value) => string` | Gets label for specific value |
| `getEnumValues()` | `(schema) => string[]` | Extracts enum values (handles both `enum` and `oneOf`) |
| `getEnumLabels()` | `(schema) => string[]` | Extracts labels (uses `enumNames` when available) |
| `getEnumLabel()` | `(schema, value) => string` | Gets label for specific enum value |
| `validateElicitationInput()` | `(stringValue, schema) => ValidationResult` | Synchronous validation via Zod |
| `validateElicitationInputAsync()` | `async (stringValue, schema, signal) => Promise<ValidationResult>` | Async validation. Falls back to Haiku NL parsing for date/datetime if sync validation fails and input doesn't look like ISO 8601 |
| `getFormatHint()` | `(schema) => string \| undefined` | Returns human-readable format hint |
| `isDateTimeSchema()` | `(schema) => schema is StringSchema & {format: 'date' \| 'date-time'}` | Type guard for date/time schemas |

**Zod Schema Building** (`getZodSchema`):
- `string`: applies `min`/`max` length, format validators (email, uri, date, date-time)
- `number`/`integer`: `z.coerce.number()`, range checks, descriptive error messages
- `boolean`: `z.coerce.boolean()`
- Enum: `z.enum([first, ...rest])`

---

### `utils/memory/` (2 files)

#### `types.ts` (12 lines)

```ts
MEMORY_TYPE_VALUES = ['User', 'Project', 'Local', 'Managed', 'AutoMem',
  ...(feature('TEAMMEM') ? ['TeamMem'] : [])] as const
MemoryType = (typeof MEMORY_TYPE_VALUES)[number]
```

#### `versions.ts` (8 lines)

| Function | Signature | Description |
|----------|-----------|-------------|
| `projectIsInGitRepo()` | `(cwd: string) => boolean` | Checks if cwd is in git repo via `findGitRoot()` (sync, no subprocess) |

---

### `utils/messages/` (2 files)

#### `mappers.ts` (290 lines)

**Purpose**: Bidirectional conversion between internal `Message[]` and SDK `SDKMessage[]` formats.

| Function | Signature | Description |
|----------|-----------|-------------|
| `toInternalMessages()` | `(messages: DeepImmutable<SDKMessage>[]) => Message[]` | SDK → Internal. Handles `assistant`, `user`, `system` (compact_boundary only) |
| `toSDKMessages()` | `(messages: Message[]) => SDKMessage[]` | Internal → SDK. Handles `assistant`, `user` (with `tool_use_result` passthrough), `system` (compact_boundary + local_command output) |
| `toSDKCompactMetadata()` | `(meta: CompactMetadata) => SDKCompactMetadata` | Compact metadata internal → SDK |
| `fromSDKCompactMetadata()` | `(meta: SDKCompactMetadata) => CompactMetadata` | Compact metadata SDK → internal |
| `toSDKRateLimitInfo()` | `(limits?: ClaudeAILimits) => SDKRateLimitInfo \| undefined` | Strips internal-only fields |
| `localCommandOutputToSDKAssistantMessage()` | `(rawContent: string, uuid: UUID) => SDKAssistantMessage` | Converts local command output to well-formed assistant message. Strips ANSI, unwraps XML tags |
| `sdkCompatToolName()` | `(name: string) => string` | Maps Agent → Task for SDK backward compat (defined in `systemInit.ts`) |

**Internal normalization** (`normalizeAssistantMessageForSDK`):
- Injects plan content into `ExitPlanModeV2` tool inputs for SDK consumers

---

#### `systemInit.ts` (96 lines)

**Purpose**: Builds the `system/init` SDKMessage — the first message on the SDK stream carrying session metadata.

| Function | Signature | Description |
|----------|-----------|-------------|
| `buildSystemInitMessage()` | `(inputs: SystemInitInputs) => SDKMessage` | Builds init message with: `cwd`, `session_id`, `tools`, `mcp_servers`, `model`, `permissionMode`, `slash_commands`, `apiKeySource`, `betas`, `claude_code_version`, `output_style`, `agents`, `skills`, `plugins`, `fast_mode_state`, optional `messaging_socket_path` |
| `sdkCompatToolName()` | `(name: string) => string` | `Agent` → `Task` mapping for SDK backward compat |

**`SystemInitInputs` type**:
```ts
{
  tools, mcpClients, model, permissionMode, commands, agents, skills,
  plugins, fastMode
}
```

---

### `utils/sandbox/` (2 files)

#### `sandbox-adapter.ts` (985 lines)

**Purpose**: Adapter layer wrapping `@anthropic-ai/sandbox-runtime` with Claude CLI integrations. The largest utility file outside powershell/parser.

**Exported Object**: `SandboxManager: ISandboxManager`

**`ISandboxManager` Interface** (39 methods):
- `initialize`, `isSupportedPlatform`, `isPlatformInEnabledList`, `getSandboxUnavailableReason`
- `isSandboxingEnabled`, `isSandboxEnabledInSettings`, `checkDependencies`
- `isAutoAllowBashIfSandboxedEnabled`, `areUnsandboxedCommandsAllowed`, `isSandboxRequired`
- `areSandboxSettingsLockedByPolicy`, `setSandboxSettings`
- `getFsReadConfig`, `getFsWriteConfig`, `getNetworkRestrictionConfig`, `getAllowUnixSockets`, `getAllowLocalBinding`
- `getIgnoreViolations`, `getEnableWeakerNestedSandbox`, `getExcludedCommands`
- `getProxyPort`, `getSocksProxyPort`, `getLinuxHttpSocketPath`, `getLinuxSocksSocketPath`
- `waitForNetworkInitialization`, `wrapWithSandbox`, `cleanupAfterCommand`
- `getSandboxViolationStore`, `annotateStderrWithSandboxFailures`, `getLinuxGlobPatternWarnings`
- `refreshConfig`, `reset`

**Key Functions**:

| Function | Description |
|----------|-------------|
| `convertToSandboxRuntimeConfig()` | Converts CC settings → sandbox-runtime config. Handles: network domains from WebFetch rules, filesystem paths from Edit/Read rules, default cwd/temp-dir, settings.json deny-write protection, `.claude/skills` protection, git bare-repo files protection, worktree support, ripgrep config |
| `resolvePathPatternForSandbox()` | Resolves CC path conventions: `//path` → `/path` (root-relative), `/path` → settings-dir-relative, `~/path`/`./path` pass through |
| `resolveSandboxFilesystemPath()` | Resolves `sandbox.filesystem.*` paths with standard semantics (`/path` = absolute, NOT settings-relative) |
| `initialize()` | Resolves worktree path, builds config, initializes base sandbox, subscribes to settings changes |
| `detectWorktreeMainRepoPath()` | Detects git worktree by reading `.git` file for `gitdir:` marker |

**Re-exported Types**: `SandboxAskCallback`, `SandboxDependencyCheck`, `FsReadRestrictionConfig`, `FsWriteRestrictionConfig`, `NetworkRestrictionConfig`, `NetworkHostPattern`, `SandboxViolationEvent`, `SandboxRuntimeConfig`, `IgnoreViolationsConfig`, `SandboxViolationStore`, `SandboxRuntimeConfigSchema`

---

#### `sandbox-ui-utils.ts` (12 lines)

| Function | Signature | Description |
|----------|-----------|-------------|
| `removeSandboxViolationTags()` | `(text: string) => string` | Regex removes `<sandbox_violations>...</sandbox_violations>` tags from text |

---

### `utils/ultraplan/` (2 files)

#### `ccrSession.ts` (349 lines)

**Purpose**: Polls CCR (Claude Code Remote) session for ExitPlanMode approval. Used by `/ultraplan` to wait for plan approval from the browser.

**Class: `ExitPlanModeScanner`**
- Tracks `exitPlanCalls` (tool_use IDs), `results` (tool_result blocks), `rejectedIds`
- `hasPendingPlan` getter: true when ExitPlanMode requested but not yet resolved
- `everSeenPending`: set to true on first pending detection
- `rejectCount`: number of unique rejections
- `ingest(newEvents: SDKMessage[]): ScanResult` — processes event batches, returns verdict

**`ScanResult` type**: `{ kind: 'approved' | 'teleport' | 'rejected' | 'pending' | 'terminated' | 'unchanged', ... }`

**`UltraplanPhase` type**: `'running' | 'needs_input' | 'plan_ready'`

| Function | Signature | Description |
|----------|-----------|-------------|
| `pollForApprovedExitPlanMode()` | `async (sessionId, timeoutMs, onPhaseChange?, shouldStop?) => Promise<PollResult>` | Main polling loop. Polls every 3s (`POLL_INTERVAL_MS`). Handles: transient network errors (max 5 consecutive failures), phase transitions, terminated sessions. Returns `{ plan, rejectCount, executionTarget: 'local' | 'remote' }` |
| `contentToText()` | `(content) => string` | Normalizes tool_result content (string or ContentBlockParam[]) |
| `extractApprovedPlan()` | `(content) => string` | Extracts plan from `## Approved Plan:\n` or `## Approved Plan (edited by user):\n` markers |
| `extractTeleportPlan()` | `(content) => string \| null` | Extracts plan from `ULTRAPLAN_TELEPORT_SENTINEL` marker |

**Constants**:
```ts
POLL_INTERVAL_MS = 3000
MAX_CONSECUTIVE_FAILURES = 5
ULTRAPLAN_TELEPORT_SENTINEL = '__ULTRAPLAN_TELEPORT_LOCAL__'
```

**Error**: `UltraplanPollError` class with `reason: PollFailReason` and `rejectCount`.

---

#### `keyword.ts` (127 lines)

**Purpose**: Ultraplan/ultrareview keyword detection with exclusion rules to prevent false triggers.

| Function | Signature | Description |
|----------|-----------|-------------|
| `findUltraplanTriggerPositions()` | `(text: string) => TriggerPosition[]` | Finds triggerable "ultraplan" occurrences |
| `findUltrareviewTriggerPositions()` | `(text: string) => TriggerPosition[]` | Finds triggerable "ultrareview" occurrences |
| `hasUltraplanKeyword()` | `(text: string) => boolean` | Returns true if keyword found |
| `hasUltrareviewKeyword()` | `(text: string) => boolean` | Returns true if keyword found |
| `replaceUltraplanKeyword()` | `(text: string) => string` | Replaces first "ultraplan" with "plan" for prompt forwarding |

**Exclusion rules** (in `findKeywordTriggerPositions`):
- Inside delimiters: backticks, double quotes, angle brackets (tag-like), curly braces, square brackets, parentheses, single quotes (apostrophe-safe)
- Path/identifier context: preceded/followed by `/`, `\`, `-`, or followed by `.ext`
- Followed by `?` (questions don't trigger)
- Slash command input (starts with `/`)
- No delimited ranges in text → no triggers

---

### `utils/git/gitConfigParser.ts` (277 lines)

**Purpose**: Lightweight `.git/config` parser verified against git's `config.c`.

| Function | Signature | Description |
|----------|-----------|-------------|
| `parseGitConfigValue()` | `async (gitDir, section, subsection, key) => Promise<string \| null>` | Reads `.git/config` from disk, finds first matching key |
| `parseConfigString()` | `(config, section, subsection, key) => string \| null` | Pure string parser. Section matching case-insensitive, subsection case-sensitive |

**Internal Parsing**:
- `parseKeyValue()`: Extracts key (alphanumeric + hyphen), skips `=`, delegates to `parseValue()`
- `parseValue()`: Handles quoted strings, escape sequences (`\n`, `\t`, `\b`, `\"`, `\\`), inline comments (`#`, `;` outside quotes), trailing whitespace trimming
- `matchesSectionHeader()`: Handles `[section]` and `[section "subsection"]`. Subsection parsing handles `\\` and `\"` escapes
- `isKeyChar()`: Validates key characters `[a-zA-Z0-9-]`

---

### `utils/todo/types.ts` (18 lines)

Zod schemas for todo items:

```ts
TodoStatusSchema → z.enum(['pending', 'in_progress', 'completed'])
TodoItemSchema → z.object({ content, status, activeForm })  // all string().min(1)
TodoListSchema → z.array(TodoItemSchema())
```

Exports both schemas (via `lazySchema`) and inferred types `TodoItem`, `TodoList`.

---

## Group 6: Tool Prompt & Output Files

### `tools/BashTool/prompt.ts` (369 lines)

**Tool Name**: `BASH_TOOL_NAME` (from `./toolName.js`)

#### Exports

| Export | Type | Description |
|--------|------|-------------|
| `getSimplePrompt()` | `() => string` | Full Bash tool prompt (~250 lines). Covers: tool preference (use FileRead/Glob/Grep over cat/find/grep), multiple command batching rules, git safety protocol (no --no-verify, no --amend, no force-push to main), sleep avoidance, sandbox section, commit/PR instructions |
| `getDefaultTimeoutMs()` | `() => number` | Default bash timeout |
| `getMaxTimeoutMs()` | `() => number` | Maximum bash timeout |

#### Prompt Structure

1. **Tool preference** (embedded vs non-embedded):
   - Non-embedded: `File search: Use Glob`, `Content search: Use Grep`
   - Embedded: skips Glob/Grep as find/grep are bfs/ugrep in Claude's shell
2. **Multiple commands**: independent → parallel tool calls; dependent → `&&` chain; `;` for fire-and-forget
3. **Git commands**: no destructive ops unless asked, no amend without request, specific file staging
4. **Sleep avoidance**: no sleep between commands, no polling, run_in_background for long-running
5. **Sandbox section**: `SandboxManager.isSandboxingEnabled()` check, shows filesystem/network restrictions, allowed/non-allowed unsandboxed command guidance. Dedups allowOnly/denyWithinAllow paths

#### Internal Functions

| Function | Description |
|----------|-------------|
| `getSimpleSandboxSection()` | Reads sandbox config from `SandboxManager`, normalizes temp dir to `$TMPDIR`, outputs JSON restrictions + override instructions |
| `getCommitAndPRInstructions()` | Git commit/PR workflow instructions. Two variants: ant users (short, references skills) vs external users (full inline instructions with heredoc examples) |
| `getBackgroundUsageNote()` | Returns `run_in_background` usage note (unless disabled) |
| `dedup()` | Array deduplication for sandbox paths |

---

### `tools/BriefTool/prompt.ts` (22 lines)

**Tool Name**: `BRIEF_TOOL_NAME = 'SendUserMessage'` (legacy: `'Brief'`)

#### Exports

| Export | Value |
|--------|-------|
| `BRIEF_TOOL_NAME` | `'SendUserMessage'` |
| `LEGACY_BRIEF_TOOL_NAME` | `'Brief'` |
| `DESCRIPTION` | `'Send a message to the user'` |
| `BRIEF_TOOL_PROMPT` | Tool prompt: message supports markdown, attachments take file paths, status labels intent ('normal'/'proactive') |
| `BRIEF_PROACTIVE_SECTION` | System prompt section: explains SendUserMessage is where answers go, acknowledgment pattern (ack → work → result), checkpoint guidance |

---

### `tools/ConfigTool/` (3 files)

#### `constants.ts` (1 line)
```ts
CONFIG_TOOL_NAME = 'Config'
```

#### `prompt.ts` (93 lines)

| Export | Type | Description |
|--------|------|-------------|
| `DESCRIPTION` | `string` | Tool description string |
| `generatePrompt()` | `() => string` | Dynamic prompt generation from `SUPPORTED_SETTINGS` registry. Separates global vs project settings. Voice settings gated by GrowthBook. Model gets separate section with dynamic options from `getModelOptions()` |

#### `UI.tsx` (38 lines)

| Export | Signature | Description |
|--------|-----------|-------------|
| `renderToolUseMessage()` | `(input: Partial<Input>) => ReactNode` | Shows "Getting {setting}" or "Setting {setting} to {value}" |
| `renderToolResultMessage()` | `(content: Output) => ReactNode` | Shows get result (`setting = value`) or set confirmation. Handles errors with red text |
| `renderToolUseRejectedMessage()` | `() => ReactNode` | "Config change rejected" warning |

---

### `tools/TodoWriteTool/` (2 files)

#### `constants.ts` (1 line)
```ts
TODO_WRITE_TOOL_NAME = 'TodoWrite'
```

#### `prompt.ts` (184 lines)

| Export | Value |
|--------|-------|
| `PROMPT` | Full prompt (~180 lines). Covers: when to use (6 scenarios), when NOT to use (4 scenarios), 4 positive examples with reasoning, 4 negative examples with reasoning, task states (pending/in_progress/completed), dual-form descriptions (content + activeForm), management rules, completion requirements |
| `DESCRIPTION` | `'Update the todo list for the current session...'` |

---

### `tools/TeamCreateTool/` (3 files)

#### `constants.ts` (1 line)
```ts
TEAM_CREATE_TOOL_NAME = 'TeamCreate'
```

#### `prompt.ts` (113 lines)

| Export | Type | Description |
|--------|------|-------------|
| `getPrompt()` | `() => string` | Full prompt (~110 lines). Covers: when to use, choosing agent types for teammates, team workflow (create → tasks → spawn → assign → work → shutdown), task ownership, automatic message delivery, teammate idle state handling, team member discovery, task list coordination |

**JSDoc shape**: `{ "team_name": "my-project", "description": "Working on feature X" }`
**Creates**: `~/.claude/teams/{team-name}/config.json` + `~/.claude/tasks/{team-name}/`

#### `UI.tsx` (6 lines)

```tsx
renderToolUseMessage(input) → `create team: ${input.team_name}`
```

---

### `tools/TeamDeleteTool/` (3 files)

#### `constants.ts` (1 line)
```ts
TEAM_DELETE_TOOL_NAME = 'TeamDelete'
```

#### `prompt.ts` (16 lines)

| Export | Type | Description |
|--------|------|-------------|
| `getPrompt()` | `() => string` | Removes team + task directories, clears context. Fails if team has active members |

#### `UI.tsx` (20 lines)

| Export | Signature | Description |
|--------|-----------|-------------|
| `renderToolUseMessage()` | `() => ReactNode` | Returns `"cleanup team: current"` |
| `renderToolResultMessage()` | `(content, _progressMessages, {verbose}) => ReactNode` | Suppresses cleanup result (batched shutdown message covers it), returns `null` |

---

## Summary Statistics

| Group | Files | Total Lines | Key Feature |
|-------|-------|-------------|-------------|
| 1. User Input Processing | 4 | 1,767 | Input classification & routing |
| 2. Suggestions | 5 | 1,213 | Fuse.js autocomplete + filesystem + shell history |
| 3. Secure Storage | 6 | ~650 | macOS Keychain + fallback chain |
| 4. PowerShell Parser | 3 | 2,305 | AST-based parser with 1,804-line core |
| 5. Small Utils | 17 | ~2,300 | DXT, file persistence, MCP validation, memory, messages, sandbox, ultraplan, git config, todos |
| 6. Tool Prompts | 13 | ~830 | Bash, Brief, Config, TodoWrite, Team Create/Delete |
| **Total** | **48** | **~9,065** | |
