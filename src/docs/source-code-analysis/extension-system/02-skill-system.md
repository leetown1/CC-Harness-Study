# Skill System Architecture

## Overview

The skill system provides instruction-based prompts (slash commands) that can be invoked by users (`/command`) or by the AI model. Skills are similar to custom GPTs: they contain markdown instructions, an optional SKILL.md file, and metadata defined via frontmatter. Skills can be loaded from multiple sources: user home directory, project directories, managed (policy) directories, additional directories (`--add-dir`), dynamic discovery, MCP servers, bundled (built into the CLI), and plugins.

Each skill is represented as a `Command` object (with `type: 'prompt'`) that contains:
- **Frontmatter metadata**: name, description, allowed-tools, when-to-use, model, etc.
- **Markdown content**: The actual prompt/instructions sent to the model
- **Base directory**: For file-based skills, the directory containing the skill files
- **Lazy evaluation**: Full content loaded only on invocation (via `getPromptForCommand`)

### Skill vs Command vs Agent

| Concept | Type | Invocation | Example |
|---------|------|------------|---------|
| **Skill** | `prompt` command | `/name` or model chooses | `/review-pr` |
| **Agent** | Agent tool | Model dispatches to sub-agent | Code review agent |
| **Output Style** | Output formatter | Model applies formatting | Formal report style |
| **Built-in Command** | `builtin` command | `/name` | `/help`, `/clear` |

---

## File Inventory

| File | Lines | Purpose |
|------|-------|---------|
| **Core Loading** | | |
| `skills/bundledSkills.ts` | 204 | BundledSkillDefinition type, registerBundledSkill(), getBundledSkills(), file extraction system |
| `skills/loadSkillsDir.ts` | 1086 | Full skill directory loading from 5 sources, dedup via realpath, frontmatter parsing, dynamic discovery, conditional activation, legacy commands compat |
| `skills/mcpSkillBuilders.ts` | 38 | MCP skill builder registry (dependency-graph leaf to break cycles) |
| **Bundled Skills** | | |
| `skills/bundled/index.ts` | 79 | Initializer: registers all bundled skills at startup |
| `skills/bundled/updateConfig.ts` | 383 | `/config-update`: View/update settings.json and CLAUDE.md files |
| `skills/bundled/keybindings.ts` | 313 | `/keybindings`: View, update, and manage keyboard shortcuts |
| `skills/bundled/verify.ts` | ~80 | `/verify`: Run verification checks on codebase |
| `skills/bundled/debug.ts` | ~60 | `/debug`: Debug session diagnostic information |
| `skills/bundled/loremIpsum.ts` | 267 | `/lorem-ipsum`: Generate token-characteristic placeholder text |
| `skills/bundled/skillify.ts` | 156 | `/skillify`: Capture session workflow as reusable skill |
| `skills/bundled/remember.ts` | ~60 | `/remember`: Save and retrieve session memory |
| `skills/bundled/simplify.ts` | ~60 | `/simplify`: Simplify complex outputs |
| `skills/bundled/batch.ts` | ~100 | `/batch`: Batch process multiple files/operations |
| `skills/bundled/stuck.ts` | ~50 | `/stuck`: Report when model appears stuck/looping |
| `skills/bundled/claudeApi.ts` | ~80 | `/claude-api`: Claude API integration (feature-flagged: BUILDING_CLAUDE_APPS) |
| `skills/bundled/claudeInChrome.ts` | ~50 | `/claude-in-chrome`: Claude in Chrome integration |
| `skills/bundled/loop.ts` | ~80 | `/loop`: Recurring task runner (feature-flagged: AGENT_TRIGGERS) |
| `skills/bundled/scheduleRemoteAgents.ts` | 387 | `/schedule-remote-agents`: Remote agent scheduling (feature-flagged: AGENT_TRIGGERS_REMOTE) |
| `skills/bundled/hunter.ts` | ~50 | Artifact review skill (feature-flagged: REVIEW_ARTIFACT) |
| `skills/bundled/dream.ts` | ~50 | Kairos dream skill (feature-flagged: KAIROS) |
| `skills/bundled/runSkillGenerator.ts` | ~50 | Skill generator (feature-flagged: RUN_SKILL_GENERATOR) |
| `skills/bundled/verifyContent.ts` | ~40 | Verification content helper |
| `skills/bundled/claudeApiContent.ts` | ~40 | Claude API content helper |

---

## Core Architecture

### 1. `bundledSkills.ts` — Bundled Skill Infrastructure

The foundational module for all skills that ship compiled into the CLI binary.

#### `BundledSkillDefinition` Type

```typescript
type BundledSkillDefinition = {
  name: string                    // e.g., "config-update"
  description: string             // User-visible description
  aliases?: string[]              // Alternative invocation names
  whenToUse?: string              // Guidance for model on when to invoke
  argumentHint?: string           // e.g., "[setting-path]"
  allowedTools?: string[]         // Tool allowlist for this skill
  model?: string                  // Override default model
  disableModelInvocation?: boolean // If true, only user-invocable
  userInvocable?: boolean         // Default: true
  isEnabled?: () => boolean       // Dynamic enablement check
  hooks?: HooksSettings           // Skill-specific hooks
  context?: 'inline' | 'fork'     // Execution context
  agent?: string                  // Agent to dispatch to
  files?: Record<string, string>  // Reference files extracted on first invocation
  getPromptForCommand: (         // The actual prompt content
    args: string,
    context: ToolUseContext,
  ) => Promise<ContentBlockParam[]>
}
```

#### `registerBundledSkill(definition)`

Registration flow:
1. **File extraction setup** (if `files` provided):
   - Compute deterministic extraction dir: `{bundledSkillsRoot}/{skillName}/`
   - Wrap `getPromptForCommand` with lazy extraction and base-dir prefix
   - Uses **promise-based memoization**: first invocation extracts; concurrent callers await same promise
2. **Create `Command` object**: Populate all fields, set `source: 'bundled'`, `loadedFrom: 'bundled'`
3. **Push to internal registry**: `bundledSkills[]` array

#### File Extraction System

Bundled skills can ship reference files that are extracted to disk on first invocation so the model can `Read`/`Grep` them:

1. **Group by parent dir**: Batch `mkdir` calls per directory subtree
2. **Safe writes**: `open(p, O_WRONLY|O_CREAT|O_EXCL|O_NOFOLLOW, 0o600)` on Unix, `'wx'` flag on Windows
   - `O_EXCL`: Fail if file already exists (atomic creation)
   - `O_NOFOLLOW`: Fail if final path component is a symlink
   - `0o600`: Owner-only permissions
   - **No unlink+retry on EEXIST**: `unlink()` follows intermediate symlinks, opening a TOCTOU window
3. **Path traversal guard**: `normalize()`, reject absolute paths and paths containing `..`
4. **Base directory prefix**: Prepended to prompt: `Base directory for this skill: {dir}\n\n`

#### File Safety (detailed)

```
resolveSkillFilePath(baseDir, relPath):
  1. normalize(relPath) — resolve ./ and multiple /
  2. Check: isAbsolute || contains ".." (Unix sep) || contains ".." (generic) → throw
  3. join(baseDir, normalized)
```

#### Public API

| Function | Description |
|----------|-------------|
| `registerBundledSkill(def)` | Register a compiled-in skill |
| `getBundledSkills()` | Returns copy of all registered skills |
| `clearBundledSkills()` | Clear registry (testing only) |
| `getBundledSkillExtractDir(name)` | Deterministic extraction directory path |

---

### 2. `loadSkillsDir.ts` — Full Skill Directory Loading

The central loader that discovers skills from 5 static sources plus dynamic discovery and conditional activation.

#### Loading Sources (Static)

| Source | Directory | SettingSource | Guard |
|--------|-----------|---------------|-------|
| **Managed** | `{managedPath}/.claude/skills/` | `policySettings` | `CLAUDE_CODE_DISABLE_POLICY_SKILLS` env var |
| **User** | `~/.claude/skills/` | `userSettings` | `isSettingSourceEnabled('userSettings') && !skillsLocked` |
| **Project** | `.claude/skills/` (walked up to home) | `projectSettings` | `isSettingSourceEnabled('projectSettings') && !skillsLocked` |
| **Additional** | `--add-dir/.claude/skills/` per path | `projectSettings` | `projectSettingsEnabled && !skillsLocked` |
| **Legacy Commands** | `.claude/commands/` (traversed up) | project/local/user | SKILL.md handling, NOT skillsLocked (these ARE skills) |

#### Loading Flow (`getSkillDirCommands()`)

```
getSkillDirCommands(cwd):
  ├─ Bare mode check: if --bare, only load --add-dir skills
  ├─ Parallel load from all sources:
  │   ├─ loadSkillsFromSkillsDir(managedSkillsDir, 'policySettings')
  │   ├─ loadSkillsFromSkillsDir(userSkillsDir, 'userSettings')
  │   ├─ [projectSkillsDirs].map(loadSkillsFromSkillsDir(*, 'projectSettings'))
  │   ├─ [additionalDirs].map(loadSkillsFromSkillsDir(    .claude/skills'))
  │   └─ loadSkillsFromCommandsDir(cwd) — legacy
  ├─ Flatten all results
  ├─ Deduplicate by realpath:
  │   ├─ Parallel getFileIdentity() (realpath) for all skills
  │   ├─ First-wins dedup: later duplicates logged and skipped
  ├─ Separate conditional from unconditional:
  │   ├─ Skills with `paths` frontmatter → conditionalSkills map
  │   ├─ Skills without paths → returned immediately
  └─ Return unconditional skills
```

#### Skills from `/skills/` Directory (Directory Format Only)

`loadSkillsFromSkillsDir(basePath, source)`:
1. `readdir(basePath)`
2. For each entry (directory or symlink to directory):
   - Look for `{dir}/SKILL.md`
   - Parse frontmatter + markdown content
   - Extract `paths` frontmatter for conditional skills
   - Create `SkillWithPath { skill, filePath }` via `createSkillCommand()`
3. **SKILL.md required**: Directories without SKILL.md are silently skipped

#### Skills from Legacy `/commands/` Directory

`loadSkillsFromCommandsDir(cwd)`:
1. `loadMarkdownFilesForSubdir('commands', cwd)` — traverses up to home
2. **SKILL.md transform**: If a directory contains any `SKILL.md` file, ONLY that file loads for that directory; other `.md` files in the same directory are discarded
3. **Namespacing**: `buildNamespace(targetDir, baseDir)` builds `:`-separated namespace from relative path
4. **Command names**:
   - Regular file: `namespace:filename` (without `.md`)
   - SKILL.md file: `namespace:parentDirName`

#### Namespacing Logic

```
buildNamespace("/project/.claude/commands/foo/bar", "/project/.claude/commands")
→ "foo:bar"

getCommandName for file /project/.claude/commands/deploy.md
→ "deploy"

getCommandName for file /project/.claude/commands/deploy/SKILL.md
→ "deploy"
```

#### `parseSkillFrontmatterFields(frontmatter, markdownContent, resolvedName)`

Extracts all shared frontmatter fields. Returns:

| Field | Source | Default |
|-------|--------|---------|
| `displayName` | `frontmatter.name` | `undefined` |
| `description` | `frontmatter.description` → markdown excerpter | Fallback label |
| `hasUserSpecifiedDescription` | Whether description was explicit | `false` |
| `allowedTools` | `frontmatter.allowed-tools` (parsed: `parseSlashCommandToolsFromFrontmatter`) | `[]` |
| `argumentHint` | `frontmatter.argument-hint` | `undefined` |
| `argumentNames` | `frontmatter.arguments` (string or array) | `[]` |
| `whenToUse` | `frontmatter.when_to_use` | `undefined` |
| `version` | `frontmatter.version` | `undefined` |
| `model` | `frontmatter.model` (`'inherit'` → undefined) | `undefined` |
| `disableModelInvocation` | `frontmatter.disable-model-invocation` | `false` |
| `userInvocable` | `frontmatter.user-invocable` | `true` |
| `hooks` | `frontmatter.hooks` (validated against HooksSchema) | `undefined` |
| `executionContext` | `frontmatter.context === 'fork'` | `undefined` |
| `agent` | `frontmatter.agent` | `undefined` |
| `effort` | `frontmatter.effort` (parsed: `parseEffortValue`) | `undefined` |
| `shell` | `frontmatter.shell` (parsed: `parseShellFrontmatter`) | `undefined` |

Invalid `effort` values are logged and treated as `undefined`. Valid values: predefined levels (`low`, `medium`, `high`) or an integer.

#### `createSkillCommand({ ... })`

Assembles a `Command` object from parsed data:

```typescript
type Command = {
  type: 'prompt'
  name: string                    // skillName
  description: string
  hasUserSpecifiedDescription: boolean
  allowedTools: string[]
  argumentHint?: string
  argNames?: string[]             // For argument substitution
  whenToUse?: string
  version?: string
  model?: string
  disableModelInvocation: boolean
  userInvocable: boolean
  context?: 'inline' | 'fork'
  agent?: string
  effort?: EffortValue
  paths?: string[]                // Conditional activation patterns
  contentLength: number
  isHidden: boolean               // !userInvocable
  progressMessage: string         // 'running'
  userFacingName(): string        // displayName || skillName
  source: SettingSource           // 'userSettings', 'projectSettings', etc.
  loadedFrom: LoadedFrom          // 'skills', 'commands_DEPRECATED', 'plugin', etc.
  hooks?: HooksSettings
  skillRoot?: string              // Base directory for the skill
  getPromptForCommand: (args, ctx) => Promise<ContentBlockParam[]>
}
```

The `getPromptForCommand` closure handles:
1. **Base directory prefix**: If `baseDir` provided, prepends `Base directory for this skill: {baseDir}\n\n`
2. **Argument substitution**: `$ARGUMENTS`, `$1`, `$2`, named arguments via `substituteArguments()`
3. **Variable substitution**: `${CLAUDE_SKILL_DIR}` (normalizes backslashes on Windows), `${CLAUDE_SESSION_ID}`
4. **Shell execution** (non-MCP): `!` and ` ```! ` blocks expanded via `executeShellCommandsInPrompt()`
5. **Security**: MCP skills skip shell execution and CLAUDE_SKILL_DIR substitution

#### Deduplication

`getFileIdentity(filePath)`: Uses `realpath()` to resolve all symlinks to a canonical path. This catches:
- Symlinks pointing to the same file
- Nested `.claude/skills/` in parent directories (project walk produces overlapping scans)
- Filesystem-agnostic (avoids inode 0 issues on virtual/container/NFS filesystems)

First occurrence wins; subsequent duplicates are logged and skipped.

#### Dynamic Skill Discovery

**`discoverSkillDirsForPaths(filePaths, cwd)`**:
1. For each file path, walk parent directories up to (but not including) cwd
2. Check for `.claude/skills/` in each parent
3. Skip gitignored directories (`isPathGitignored`)
4. Return directories sorted deepest-first

**`addSkillDirectories(dirs)`**:
1. Load skills from each dir in parallel
2. Process in **reverse order** (shallow first) so deeper paths override
3. Merge into `dynamicSkills` map
4. Fire `skillsLoaded` signal (listeners clear caches)

**`activateConditionalSkillsForPaths(filePaths, cwd)`**:
1. For each conditional skill (with `paths` frontmatter):
2. Use `ignore` library (gitignore-style matching)
3. Match filenames relative to cwd against path patterns
4. On match: move from `conditionalSkills` → `dynamicSkills`, mark as `activatedConditionalSkillNames`
5. Skip: empty strings, `../` paths, absolute paths
6. Once activated, survives cache clears within session

**Signal system**: `onDynamicSkillsLoaded(callback)` subscribes to skill changes. Each listener is wrapped in try/catch (one throwing listener doesn't abort others).

#### Policy Guards

- `isBareMode()`: Skips managed/user/project dir walks + legacy commands. Only `--add-dir` paths load. `skillsLocked` still applies.
- `isRestrictedToPluginOnly('skills')`: Blocks file-based skills entirely (enterprise policy).
- `CLAUDE_CODE_DISABLE_POLICY_SKILLS`: Disables managed (policy) skills.
- `isSettingSourceEnabled()`: Guards userSettings and projectSettings individually.

#### Cache Control

`clearSkillCaches()`:
- Clears `getSkillDirCommands` memoize cache
- Clears `loadMarkdownFilesForSubdir` memoize cache
- Clears conditional skills and activated names
- Does NOT clear dynamic skills (session-persistent)

---

### 3. `mcpSkillBuilders.ts` — MCP Skill Builder Registry

A dependency-graph leaf module that breaks import cycles between MCP skill discovery and skill loading:

```
client.ts
  → mcpSkills.ts
    → loadSkillsDir.ts (needs createSkillCommand, parseSkillFrontmatterFields)
      → ... → client.ts (cycle!)
```

**Solution**: `mcpSkillBuilders.ts` is a leaf module importing only types:
1. `loadSkillsDir.ts` calls `registerMCPSkillBuilders({ createSkillCommand, parseSkillFrontmatterFields })` at module init
2. `mcpSkills.ts` calls `getMCPSkillBuilders()` at runtime to get the functions
3. No circular dependency because the leaf has no imports

```typescript
type MCPSkillBuilders = {
  createSkillCommand: typeof createSkillCommand
  parseSkillFrontmatterFields: typeof parseSkillFrontmatterFields
}
```

Registration is write-once at `loadSkillsDir.ts` module init (eagerly evaluated at startup via static import from `commands.ts`), well before any MCP server connects.

---

## Bundled Skills — Detailed

All bundled skills are registered via `registerBundledSkill()` and initialized by `initBundledSkills()` in `skills/bundled/index.ts`.

### Always Registered

| Skill | File | Description |
|-------|------|-------------|
| **`/config-update`** | `updateConfig.ts` (475 lines) | View/update settings.json and CLAUDE.md. Generates JSON Schema from Zod types at registration time. Provides extensive examples for permissions, env, hooks, agents, plugins, status line, MCP servers, model, and more. Includes settings file location guide (global/project/local). |
| **`/keybindings`** | `keybindings.ts` (313 lines) | View, update, and manage keyboard shortcuts. Generates action table from `DEFAULT_BINDINGS` and `KEYBINDING_ACTIONS`. Lists reserved shortcuts (terminal-bound, macOS-bound, non-rebindable). Reads current user bindings. |
| **`/verify`** | `verify.ts` | Run verification checks on the codebase. Configurable via `verifyContent.ts`. |
| **`/debug`** | `debug.ts` | Output diagnostic information about the current session: state, config, active plugins, etc. |
| **`/lorem-ipsum`** | `loremIpsum.ts` (282 lines) | Generate token-characteristic placeholder text. Uses verified 1-token English words (articles, verbs, prepositions, nouns, adjectives). Supports `--tokens=N` flag. Counts tokens via `roughTokenCountEstimation`. Reference: token count validation table. |
| **`/skillify`** | `skillify.ts` (197 lines) | Capture the current session's repeatable workflow as a reusable skill. Extracts user messages, session memory, analyzes process steps, then generates SKILL.md with proper frontmatter. Uses template with `{{sessionMemory}}` and `{{userMessages}}` substitution. |
| **`/remember`** | `remember.ts` | Save information to session memory. Retrievable in subsequent turns. |
| **`/simplify`** | `simplify.ts` | Simplify complex outputs. Prompts model to reduce verbosity while preserving key information. |
| **`/batch`** | `batch.ts` | Batch process multiple files or operations in a single invocation. |
| **`/stuck`** | `stuck.ts` | Report and diagnose when the model appears stuck or looping. |

### Feature-Flagged (require feature flags enabled)

| Skill | Features Flag | Description |
|-------|---------------|-------------|
| **`/claude-api`** | `BUILDING_CLAUDE_APPS` | Claude API integration for building Claude-based applications |
| **`/loop`** | `AGENT_TRIGGERS` | Recurring task/agent runner. `isEnabled` delegates to `isKairosCronEnabled()`. |
| **`/schedule-remote-agents`** | `AGENT_TRIGGERS_REMOTE` | Remote agent scheduling: fetch MCP server environments, schedule agents to run remotely. Handles `mcpsrv_` tagged ID decoding, environment management. |
| **hunter** | `REVIEW_ARTIFACT` | Review and analyze build artifacts |
| **dream** | `KAIROS` or `KAIROS_DREAM` | Kairos dream integration |
| **run skill generator** | `RUN_SKILL_GENERATOR` | Generate new skills from usage patterns |
| **`/claude-in-chrome`** | `shouldAutoEnableClaudeInChrome()` | Claude in Chrome integration — registered when the Chrome extension is detected |

### Feature Flag Registration Pattern

```typescript
if (feature('FEATURE_FLAG_NAME')) {
  const { registerXSkill } = require('./x.js')  // Dynamic require
  registerXSkill()
}
```

Uses `require()` (not `import`) for feature-flagged skills to avoid bundling unless the feature flag is active. Each skill file exports a `register*Skill()` function that calls `registerBundledSkill()`.

---

## Loading Flow — Complete Picture

Skills are discovered and loaded in this order:

```
App Start
  ├─ initBundledSkills()                    # Synchronous, module init
  │   └─ registerBundledSkill() for each    # Populates bundledSkills[]
  │
  ├─ getSkillDirCommands(cwd) [memoized]    # Asynchronous
  │   ├─ [managed] loadSkillsFromSkillsDir()
  │   ├─ [user] loadSkillsFromSkillsDir()
  │   ├─ [project*] loadSkillsFromSkillsDir()   # Walk tree up to home
  │   ├─ [--add-dir*] loadSkillsFromSkillsDir()
  │   ├─ [legacy] loadSkillsFromCommandsDir()  # /commands/ dir
  │   ├─ Deduplicate by realpath
  │   └─ Separate conditional skills
  │
  ├─ getBundledSkills()                     # Synchronous copy
  ├─ getBuiltinPluginSkillCommands()        # From enabled builtin plugins
  ├─ getPluginCommands() [memoized]         # From enabled marketplace plugins
  │
  ├─ getDynamicSkills()                     # Session-discovered skills
  │
  └─ Runtime: activateConditionalSkillsForPaths()  # On file touch
      └─ Moves matching skills to dynamicSkills
```

### Skill Name Collision Resolution

When multiple sources provide skills with the same name:
1. **Static loading**: First-wins deduplication via `realpath` identity
2. **Dynamic discovery**: Deeper paths override shallower (processed reverse order)
3. **Bundled vs file-based**: File-based skills can override bundled skills (depends on merge order in the consumer)
4. **Plugin skills**: Prefixed with `pluginName:` to avoid collisions

---

## Key Design Decisions

1. **Lazy content loading**: Full markdown content read only on invocation via `getPromptForCommand`. This keeps startup fast — only frontmatter is parsed eagerly.

2. **Promise-memoized file extraction**: Bundled skill reference files extracted once per process. Concurrent callers await the same extraction promise.

3. **realpath-based deduplication**: More robust than inode-based dedup (avoids virtual filesystem issues). Parallel pre-computation, serial dedup (order-dependent).

4. **gitignore-aware dynamic discovery**: `isPathGitignored` prevents loading skills from `node_modules/`, `dist/`, etc. The invocation-time trust dialog remains the actual security boundary.

5. **Conditional skill activation**: Skills with `paths` frontmatter are stored inactive until a matching file is touched. Uses `ignore` library (same as CLAUDE.md conditional rules). Once activated, survives cache clears within a session.

6. **`mcpSkillBuilders.ts` dependency-graph leaf**: Breaks the `client → mcpSkills → loadSkillsDir → … → client` import cycle without runtime dynamic imports (which fail in Bun-bundled binaries).

7. **Shell command execution safety**: MCP skills (remote, untrusted) skip inline shell execution. File-based skills execute shell blocks with context-specific `alwaysAllowRules`.

8. **Bare mode awareness**: `--bare` skips managed/user/project dir walks and legacy commands. Only `--add-dir` explicit paths load. Skills-lock policy still applies.

9. **Skill file safety on extraction**: `O_EXCL | O_NOFOLLOW` on Unix, `'wx'` on Windows. No unlink+retry pattern. Per-process nonce in extraction root is primary defense against pre-created symlinks/dirs.
