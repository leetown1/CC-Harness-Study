# Command System Analysis — Slash Commands

> **File:** `src/commands.ts`, `src/types/command.ts`, `src/commands/`  
> **Scope:** All slash commands in Claude Code — type system, registry, 110 command implementations (189 ts/tsx files in `commands/`)  
> **Lines:** ~25,000 across `commands/` directory; 754 lines in `commands.ts`; 216 lines in `types/command.ts`

---

## Table of Contents

1. [Type System](#1-type-system)
2. [Command Registry](#2-command-registry)
3. [Prompt Commands](#3-prompt-commands)
4. [Local Commands](#4-local-commands)
5. [Local JSX Commands](#5-local-jsx-commands)
6. [Bridge/Migration Commands](#6-bridgemigration-commands)
7. [Internal & ANT-Only Stubs](#7-internal--ant-only-stubs)
8. [Remote Safety & Bridge Safety](#8-remote-safety--bridge-safety)
9. [Skill/Plugin Loading Pipeline](#9-skillplugin-loading-pipeline)
10. [Command Discovery Flow](#10-command-discovery-flow)

---

## 1. Type System

**File:** `src/types/command.ts` (216 lines)

### 1.1 Core Types

The type system defines three mutually exclusive command categories via a discriminated union on `type`:

| Type | Description | Injected As |
|------|-------------|-------------|
| `'prompt'` | Model-invocable — expands to text fed to the LLM | `PromptCommand` |
| `'local'` | Synchronous/local — returns `LocalCommandResult` immediately | `LocalCommand` |
| `'local-jsx'` | Interactive TUI — renders React/Ink components | `LocalJSXCommand` |

The top-level `Command` type is formed by intersecting `CommandBase` with the discriminated union:

```typescript
export type Command = CommandBase & (PromptCommand | LocalCommand | LocalJSXCommand)
```

### 1.2 CommandBase (Shared Properties)

All commands inherit `CommandBase` (`command.ts:175-203`):

| Property | Type | Default | Description |
|----------|------|---------|-------------|
| `name` | `string` | required | Unique command identifier (e.g. `'init'`, `'clear'`) |
| `description` | `string` | required | User-facing description shown in help/autocomplete |
| `aliases` | `string[]?` | — | Alternative names (e.g. `/reset` → `/clear`) |
| `argumentHint` | `string?` | — | Gray hint text displayed after command in UI |
| `availability` | `CommandAvailability[]?` | — | Auth/provider gate — who can use this command |
| `isEnabled()` | `() => boolean` | `true` | Dynamic enable/disable (GrowthBook flags, env vars) |
| `isHidden` | `boolean` | `false` | Hides from `/help` listing and typeahead |
| `isMcp` | `boolean?` | — | Marks MCP-provided commands |
| `disableModelInvocation` | `boolean?` | — | Prevents model from auto-invoking as skill |
| `userInvocable` | `boolean?` | — | Users can type `/skill-name` to invoke |
| `loadedFrom` | `string?` | — | Origin: `'skills'`, `'plugin'`, `'bundled'`, `'managed'`, `'mcp'`, `'commands_DEPRECATED'` |
| `kind` | `'workflow'?` | — | Distinguishes workflow-backed commands (badged in autocomplete) |
| `immediate` | `boolean?` | — | Executes immediately, bypassing the message queue |
| `isSensitive` | `boolean?` | — | Redacts args from conversation history |
| `whenToUse` | `string?` | — | From the "Skill" spec — detailed usage scenarios |
| `version` | `string?` | — | Version of the command/skill |
| `hasUserSpecifiedDescription` | `boolean?` | — | Whether user provided a description override |
| `userFacingName()` | `() => string` | `cmd.name` | Override for displayed name (e.g. plugin prefix stripping) |
| `source` | (PromptCommand only) | `'builtin'` | Source: `'builtin'`, `'plugin'`, `'bundled'`, `'mcp'`, or `SettingSource` |

**Utility functions** (`command.ts:208-216`):
- `getCommandName(cmd)` — resolves user-visible name: `cmd.userFacingName?.() ?? cmd.name`
- `isCommandEnabled(cmd)` — resolves: `cmd.isEnabled?.() ?? true`

### 1.3 CommandAvailability

Two auth/provider scopes (`command.ts:169-173`):

| Value | Meaning |
|-------|---------|
| `'claude-ai'` | claude.ai OAuth subscriber (Pro/Max/Team/Enterprise) |
| `'console'` | Direct API key user (api.anthropic.com, not via claude.ai OAuth) |

Commands without `availability` are universal (available everywhere). Commands with `availability` require the user to match at least one of the listed types.

### 1.4 PromptCommand

**`PromptCommand`** (`command.ts:25-57`) — Model-invocable commands that expand to text content blocks:

```typescript
export type PromptCommand = {
  type: 'prompt'
  progressMessage: string         // Displayed while command runs
  contentLength: number           // Char length for token estimation (0 = dynamic)
  argNames?: string[]             // Named arguments
  allowedTools?: string[]         // Array of tool restriction patterns
  model?: string                  // Specific model override
  source: SettingSource | 'builtin' | 'mcp' | 'plugin' | 'bundled'
  pluginInfo?: { pluginManifest, repository } // Plugin metadata
  disableNonInteractive?: boolean // Block in non-interactive mode
  hooks?: HooksSettings           // Hooks to register when this skill is invoked
  skillRoot?: string              // Base directory for CLAUDE_PLUGIN_ROOT env var
  context?: 'inline' | 'fork'     // Execution context: inline (default) or fork (sub-agent)
  agent?: string                  // Agent type when forked
  effort?: EffortValue            // Effort level override
  paths?: string[]                // Glob patterns — only visible after model touches matching files
  getPromptForCommand(args, context): Promise<ContentBlockParam[]> // Core — returns prompt content
}
```

**Execution contexts:**
- `context: 'inline'` (default) — Skill content expands into the current conversation
- `context: 'fork'` — Skill runs in a sub-agent with separate context and token budget

### 1.5 LocalCommand

**`LocalCommand`** (`command.ts:74-78`) — Invoked locally, returns text/compact/skip results:

```typescript
type LocalCommand = {
  type: 'local'
  supportsNonInteractive: boolean
  load: () => Promise<LocalCommandModule> // Lazy-loads implementation
}

type LocalCommandModule = {
  call: LocalCommandCall
}

type LocalCommandCall = (
  args: string,
  context: LocalJSXCommandContext,
) => Promise<LocalCommandResult>
```

**`LocalCommandResult`** (`command.ts:16-23`):

```typescript
export type LocalCommandResult =
  | { type: 'text'; value: string }           // Display text in UI
  | { type: 'compact'; compactionResult; displayText? } // Trigger compaction
  | { type: 'skip' }                          // Skip messages
```

### 1.6 LocalJSXCommand

**`LocalJSXCommand`** (`command.ts:144-152`) — Interactive TUI commands that render React/Ink:

```typescript
type LocalJSXCommand = {
  type: 'local-jsx'
  load: () => Promise<LocalJSXCommandModule>
}

type LocalJSXCommandModule = {
  call: LocalJSXCommandCall
}

type LocalJSXCommandCall = (
  onDone: LocalJSXCommandOnDone,
  context: ToolUseContext & LocalJSXCommandContext,
  args: string,
) => Promise<React.ReactNode>
```

**`LocalJSXCommandOnDone`** (`command.ts:117-126`):

```typescript
export type LocalJSXCommandOnDone = (
  result?: string,
  options?: {
    display?: CommandResultDisplay  // 'skip' | 'system' | 'user'
    shouldQuery?: boolean           // Send messages to model after completion
    metaMessages?: string[]         // Additional model-visible messages (hidden from user)
    nextInput?: string              // Pre-fill next input
    submitNextInput?: boolean       // Auto-submit next input
  },
) => void
```

### 1.7 LocalJSXCommandContext

**Extended context** (`command.ts:80-98`) provided to local and local-jsx commands:

```typescript
export type LocalJSXCommandContext = ToolUseContext & {
  canUseTool?: CanUseToolFn
  setMessages: (updater: (prev: Message[]) => Message[]) => void
  options: {
    dynamicMcpConfig?: Record<string, ScopedMcpServerConfig>
    ideInstallationStatus: IDEExtensionInstallationStatus | null
    theme: ThemeName
  }
  onChangeAPIKey: () => void
  onChangeDynamicMcpConfig?: (config) => void
  onInstallIDEExtension?: (ide: IdeType) => void
  resume?: (sessionId, log, entrypoint) => Promise<void>
}
```

### 1.8 ResumeEntrypoint

```typescript
export type ResumeEntrypoint =
  | 'cli_flag'                  // --resume <id>
  | 'slash_command_picker'      // /resume interactive picker
  | 'slash_command_session_id'  // /resume <session-id>
  | 'slash_command_title'       // /resume <title-search>
  | 'fork'                      // Fork from a conversation branch
```

---

## 2. Command Registry

**File:** `src/commands.ts` (754 lines)

### 2.1 COMMANDS Memoized Array

`COMMANDS` (`commands.ts:258-346`) is a `lodash-es/memoize` wrapper returning a flat array of built-in command definitions. It is memoized because underlying functions read from config, which cannot be read at module initialization time.

The array contains **71 base built-in command definitions** (up to ~82 with feature flags and OAuth commands) arranged in this order:

```
addDir, advisor, agents, branch, btw, chrome, clear, color, compact, config,
copy, desktop, context, contextNonInteractive, cost, diff, doctor, effort, exit,
fast, files, heapDump, help, ide, init, keybindings, installGitHubApp,
installSlackApp, mcp, memory, mobile, model, outputStyle, remoteEnv, plugin,
pr_comments, releaseNotes, reloadPlugins, rename, resume, session, skills,
stats, status, statusline, stickers, tag, theme, feedback, review, ultrareview,
rewind, securityReview, terminalSetup, upgrade, extraUsage, extraUsageNonInteractive,
rateLimitOptions, usage, usageReport, vim
```

Plus **conditionally included** feature-flagged commands:
- `webCmd` (CCR_REMOTE_SETUP) — /web-setup
- `forkCmd` (FORK_SUBAGENT) — /fork
- `buddy` (BUDDY) — /buddy
- `proactive` (PROACTIVE or KAIROS) — proactive mode command
- `briefCommand` (KAIROS or KAIROS_BRIEF) — /brief
- `assistantCommand` (KAIROS) — assistant session
- `bridge` (BRIDGE_MODE) — remote control bridge
- `remoteControlServerCommand` (DAEMON + BRIDGE_MODE)
- `voiceCommand` (VOICE_MODE) — voice toggle
- `forceSnip` (HISTORY_SNIP)
- `workflowsCmd` (WORKFLOW_SCRIPTS) — workflow commands
- `peersCmd` (UDS_INBOX) — /peers
- `torch` (TORCH) — /torch
- `thinkback`, `thinkbackPlay` — Year in Review
- `permissions`, `plan`, `privacySettings`, `hooks`, `sandboxToggle`
- `exportCommand` — /export
- `logout`, `login()` — OAuth (excluded if `isUsing3PServices()`)
- `passes` — guest passes
- `tasks` — /tasks

**ANT-only internal commands** (`process.env.USER_TYPE === 'ant' && !IS_DEMO`): 25 commands (up to 28 with conditional entries) via `INTERNAL_ONLY_COMMANDS` array (`commands.ts:225-254`).

### 2.2 getCommands()

`getCommands(cwd)` (`commands.ts:476-517`) — the main entry point for obtaining all available commands:

1. Calls `loadAllCommands(cwd)` (memoized by cwd) which loads from **5 sources** in parallel:
   - `getSkills(cwd)` → `{ skillDirCommands, pluginSkills, bundledSkills, builtinPluginSkills }`
   - `getPluginCommands()` → plugin-provided commands
   - `getWorkflowCommands(cwd)` → workflow script commands
   - All merged with `COMMANDS()` (built-in commands)
   - Order: `bundledSkills → builtinPluginSkills → skillDirCommands → workflowCommands → pluginCommands → pluginSkills → COMMANDS()`

2. Filters by `meetsAvailabilityRequirement(cmd)` and `isCommandEnabled(cmd)`

3. Merges `getDynamicSkills()` — skills discovered during file operations, inserted after plugin skills but before built-in commands (deduplicated by name)

### 2.3 meetsAvailabilityRequirement()

`meetsAvailabilityRequirement(cmd)` (`commands.ts:417-443`) — checks if the current user's auth/provider matches the command's `availability`:
- No availability → universal (always true)
- `'claude-ai'` → checks `isClaudeAISubscriber()`
- `'console'` → checks `!isClaudeAISubscriber() && !isUsing3PServices() && isFirstPartyAnthropicBaseUrl()`

### 2.4 getSkillToolCommands()

`getSkillToolCommands(cwd)` (`commands.ts:563-581`) — filters to ALL prompt-based commands the model can invoke:

Filter criteria:
- `type === 'prompt'`
- `!disableModelInvocation` (model can invoke)
- `source !== 'builtin'` (exclude builtin slash commands like /init, /commit)
- Description gate: `loadedFrom === 'bundled'` or `'skills'` or `'commands_DEPRECATED'` OR has explicit `hasUserSpecifiedDescription` / `whenToUse`

### 2.5 getSlashCommandToolSkills()

`getSlashCommandToolSkills(cwd)` (`commands.ts:586-608`) — filters to only skills (not all prompt commands):

Filter criteria:
- `type === 'prompt'`
- `source !== 'builtin'`
- Has `hasUserSpecifiedDescription` or `whenToUse`
- `loadedFrom === 'skills'` or `'plugin'` or `'bundled'` OR `disableModelInvocation` is set

### 2.6 getMcpSkillCommands()

`getMcpSkillCommands(mcpCommands)` (`commands.ts:547-559`) — extracts MCP-provided prompt commands from app state, gated behind the `MCP_SKILLS` feature flag.

### 2.7 Cache Management

| Function | Scope |
|----------|-------|
| `clearCommandMemoizationCaches()` | Clears `loadAllCommands`, `getSkillToolCommands`, `getSlashCommandToolSkills`, and `clearSkillIndexCache` memoization |
| `clearCommandsCache()` | Full reset — clears memoization + `clearPluginCommandCache()` + `clearPluginSkillsCache()` + `clearSkillCaches()` |

### 2.8 Command Lookup

| Function | Purpose |
|----------|---------|
| `findCommand(name, commands)` | Searches by `name`, `userFacingName()`, or `aliases` |
| `hasCommand(name, commands)` | Boolean existence check |
| `getCommand(name, commands)` | Returns command or throws `ReferenceError` with all available names |

### 2.9 formatDescriptionWithSource()

`formatDescriptionWithSource(cmd)` (`commands.ts:728-753`) — formats command descriptions for user-facing UI with source annotations:
- `'workflow'` kind → appends `(workflow)`
- `'plugin'` source → prepends `(pluginName)` or appends `(plugin)`
- `'bundled'` source → appends `(bundled)`
- Other non-builtin/mcp → appends `(sourceDisplayName)`
- `'builtin'` / `'mcp'` → no annotation

---

## 3. Prompt Commands

Prompt commands are **model-invocable** — they expand to LLM prompts that instruct Claude how to perform a task.

### 3.1 /commit — Git Commit

**File:** `src/commands/commit.ts` (92 lines)  
**Type:** `prompt` | **Source:** `builtin` | **Progress:** "creating commit"

**Allowed Tools:** `Bash(git add:*)`, `Bash(git status:*)`, `Bash(git commit:*)`

**Behavior:**
1. Generates a prompt that instructs the model to analyze staged/unstaged changes (`git diff HEAD`, `git status`, recent commits)
2. Provides a **Git Safety Protocol** — forbid config updates, skip hooks (unless user requests), amend, empty commits, interactive flags
3. Instructs model to draft a 1-2 sentence commit message focusing on "why" not "what"
4. Uses HEREDOC syntax for commit messages with optional attribution
5. `executeShellCommandsInPrompt()` processes `!` shell commands (e.g., `!`git status``) embedded in the prompt, injecting their output
6. Tool permissions are set to `alwaysAllowRules.command = ALLOWED_TOOLS`

**ANT-only:** Undercover mode injects additional prefix instructions.

### 3.2 /commit-push-pr — Branch, Commit, Push, Open PR

**File:** `src/commands/commit-push-pr.ts` (158 lines)  
**Type:** `prompt` | **Source:** `builtin` | **Progress:** "creating commit and PR"

**Allowed Tools:** `Bash(git checkout:*:*)`, `Bash(git add:*)`, `Bash(git status:*)`, `Bash(git push:*)`, `Bash(git commit:*)`, `Bash(gh pr create:*)`, `Bash(gh pr edit:*)`, `Bash(gh pr view:*)`, `Bash(gh pr merge:*)`, `ToolSearch`, `mcp__slack__send_message`, `mcp__claude_ai_Slack__slack_send_message`

**Behavior:**
1. Captures: `git status`, `git diff HEAD`, branch name, branch-vs-default diff, existing PR info
2. Git Safety Protocol (extended with force-push prohibitions)
3. Multi-step workflow:
   - Create a new branch if on default branch (prefix: `$SAFEUSER/feature-name`)
   - Stage and commit with HEREDOC syntax + attribution
   - Push to origin
   - Create PR (`gh pr create`) or update existing (`gh pr edit`) with: short title (<70 chars), summary bullets, test plan checklist, optional changelog section
   - Optional: Post PR URL to Slack (checks CLAUDE.md, uses ToolSearch for Slack tools)
4. `getEnhancedPRAttribution()` enriches PR description with contributing docs if available
5. User args appended as "Additional instructions from user"

### 3.3 /init — Analyze Codebase, Create CLAUDE.md

**File:** `src/commands/init.ts` (256 lines)  
**Type:** `prompt` | **Source:** `builtin` | **Progress:** "analyzing your codebase"

**Dual-mode prompt:** The command has two prompt variants gated by `feature('NEW_INIT')` and `CLAUDE_CODE_NEW_INIT`:

**OLD_INIT_PROMPT** (simple):
- Analyze codebase, create a CLAUDE.md
- Include: build/lint/test commands, high-level architecture
- Exclude: obvious instructions, generic advice, easily discoverable file structures
- Check Cursor rules, Copilot instructions, README
- Prefix with standard CLAUDE.md header

**NEW_INIT_PROMPT** (8-phase):
1. **Phase 1: Ask** — Uses `AskUserQuestion` to determine: project CLAUDE.md, personal CLAUDE.local.md, or both; whether to also set up skills and hooks
2. **Phase 2: Explore** — Subagent surveys codebase: manifest files, existing configs, build/test commands, formatter config, git worktrees
3. **Phase 3: Fill gaps** — `AskUserQuestion` for what code can't answer; proposes hooks (deterministic), skills (on-demand), CLAUDE.md notes (loose guidelines)
4. **Phase 4: Write CLAUDE.md** — Minimal project file at root; every line must pass "Would removing this cause Claude to make mistakes?"
5. **Phase 5: Write CLAUDE.local.md** — Personal preferences, gitignored; handles git worktree scenarios
6. **Phase 6: Skills** — Creates skills from proposal queue, suggests additional ones for repeatable workflows
7. **Phase 7: Optimizations** — Checks GitHub CLI, linting setup, proposal-sourced hooks
8. **Phase 8: Summary** — Recap what was created, suggests next steps (frontend plugins, test framework, skill-creator plugin)

Calls `maybeMarkProjectOnboardingComplete()` on invocation.

### 3.4 /init-verifiers — Create Verifier Skills

**File:** `src/commands/init-verifiers.ts` (262 lines)  
**Type:** `prompt` | **Source:** `builtin` | **Progress:** "analyzing your project and creating verifier skills"

**5-phase verifier skill creation:**

1. **Phase 1: Auto-Detection** — Scans project structure for distinct areas, detects app type (web/CLI/API), finds testing tools, dev server configs, installed verification packages (Playwright, Chrome DevTools MCP, Chrome Extension MCP)

2. **Phase 2: Tool Setup** — Helps install appropriate tools:
   - Web apps: Playwright (`npm install -D @playwright/test`), Chrome DevTools MCP, Claude Chrome Extension
   - CLI tools: checks asciinema availability
   - API services: curl/httpie

3. **Phase 3: Q&A** — Confirms verifier name conventions:
   - Single area: `verifier-playwright`, `verifier-cli`, `verifier-api`
   - Multiple areas: `verifier-<project>-<type>` (e.g., `verifier-frontend-playwright`)
   - Asks about authentication: login method, test credentials, post-login indicators

4. **Phase 4: Generate** — Creates `SKILL.md` in `.claude/skills/<verifier-name>/` with:
   - Project context, setup instructions, authentication steps
   - Allowed tools by type (Playwright: `mcp__playwright__*`, CLI: `Tmux`, API: `Bash(curl:*)`)
   - Self-update capability for outdated instructions

5. **Phase 5: Confirm** — Reports created files, explains Verify agent discovery ("verifier" in folder name)

### 3.5 /review — Pull Request Review

**File:** `src/commands/review.ts` (57 lines)  
**Type:** `prompt` | **Source:** `builtin` | **Progress:** "reviewing pull request"

**Behavior:**
- If no PR number in args: instructs model to run `gh pr list`
- If PR number provided: runs `gh pr view`, `gh pr diff`, then analyzes
- Review focuses on: code correctness, conventions, performance, test coverage, security
- Output formatted with clear sections and bullet points

**Also exports `/ultrareview`** — a `local-jsx` command that launches the remote bughunter path (~10-20 min deep review in CCR). Gated by `isUltrareviewEnabled()` (GrowthBook `tengu_review_bughunter_config.enabled`).

### 3.6 /security-review — Security Audit

**File:** `src/commands/security-review.ts` (243 lines)  
**Type:** `prompt` (via `createMovedToPluginCommand`) | **Source:** `builtin` | **Progress:** "analyzing code changes for security risks"

**Plugin migration shim:** Currently uses `createMovedToPluginCommand` with `getPromptWhileMarketplaceIsPrivate` — ANTs get a "moved to plugin" message; external users get the full prompt.

**Full security review prompt (~190 lines of instruction):**
1. **Input:** `git status`, changed files, commits, full `git diff origin/HEAD...`
2. **Categories:** Input validation (SQL injection, command injection, XSS, path traversal), auth/authz (bypass, privilege escalation, JWT), crypto/secrets (hardcoded keys, weak crypto), injection/RCE (deserialization, eval, XSS), data exposure (PII, logging, debug info)
3. **Methodology:**
   - Phase 1: Research existing security patterns in codebase
   - Phase 2: Compare new code against established patterns
   - Phase 3: Assess each modified file
4. **Output format:** Markdown with file:line, severity (HIGH/MEDIUM/LOW), category, description, exploit scenario, fix recommendation, confidence scoring (1-10)
5. **False Positive Filtering:** 19 hard exclusions (DOS, secrets-on-disk, rate limiting, race conditions, outdated libraries, regex injection, documentation files, audit logs), 12 precedents (UUIDs are unguessable, env vars are trusted, React/Angular XSS-safe, etc.)
6. **Signal quality criteria:** Requires concrete exploitability, clear attack path, specific code locations, confidence ≥ 8

**ANT-only plugin path:** Returns "This command has been moved to a plugin. Install: `claude plugin install security-review@claude-code-marketplace`. Use: `/security-review:security-review`."

### 3.7 /statusline — Configure Terminal Status Line

**File:** `src/commands/statusline.tsx` (24 lines)  
**Type:** `prompt` | **Source:** `builtin` | **Progress:** "setting up statusLine"

**Allowed Tools:** `Agent`, `Read(~/**)`, `Edit(~/.claude/settings.json)`  
**`disableNonInteractive: true`** — blocked in SDK/batch mode

**Behavior:** Creates an `Agent` tool call with `subagent_type: "statusline-setup"` and a prompt derived from args (or defaults to "Configure my statusLine from my shell PS1 configuration"). The agent handles reading PS1 config, generating status line settings, and writing to `~/.claude/settings.json`.

### 3.8 /pr-comments — Fetch GitHub PR Comments

**File:** `src/commands/pr_comments/index.ts` (50 lines)  
**Type:** `prompt` (via `createMovedToPluginCommand`) | **Source:** `builtin` | **Progress:** "fetching PR comments"

**Plugin migration shim** for `pr-comments@claude-code-marketplace`.

**Fallback prompt:**
1. Uses `gh pr view --json number,headRepository`
2. Fetches PR-level comments: `gh api /repos/{owner}/{repo}/issues/{number}/comments`
3. Fetches review comments: `gh api /repos/{owner}/{repo}/pulls/{number}/comments`
4. Formats as threaded markdown with diff hunk context

### 3.9 /insights — Session Analysis Report

**File:** Inline in `commands.ts:190-202` (lazy dynamic import of `commands/insights.js`)  
**Type:** `prompt` | **Source:** `builtin` | **Progress:** "analyzing your sessions"

Lazy shim — the real implementation is 113KB (3200 lines) and is only loaded when `/insights` is invoked, avoiding startup cost.

### 3.10 /security-review (Plugin Migration)

Implemented via `createMovedToPluginCommand()` with `pluginName: 'security-review'`. Creates a prompt command that:
- For ANTs: instructs to install `security-review@claude-code-marketplace` and use `/security-review:security-review`
- For external users: uses the full inline security review prompt (see 3.6 above)

---

## 4. Local Commands

Local commands are invoked synchronously and return `LocalCommandResult` (text, compact, or skip).

### 4.1 /clear — Clear Conversation

**File:** `src/commands/clear/index.ts` (19 lines), `clear.ts` (7 lines), `conversation.ts` (251 lines), `caches.ts` (144 lines)  
**Type:** `local` | **Aliases:** `reset`, `new` | **`supportsNonInteractive: false`**

**Architecture:** 3-layer split for lazy-loading:
- `index.ts` — command metadata only
- `clear.ts` — thin call wrapper (7 lines)
- `conversation.ts` — heavy implementation (251 lines)
- `caches.ts` — cache clearing utilities (144 lines, also imported at startup)

**`clearConversation()` full flow** (`conversation.ts:49-251`):

1. **SessionEnd hooks** — executes end-of-session hooks with configurable timeout (`CLAUDE_CODE_SESSIONEND_HOOKS_TIMEOUT_MS`, default 1.5s)
2. **Cache eviction hint** — signals inference tier to evict conversation cache
3. **Preserved tasks** — computes which background tasks survive (tasks with `isBackgrounded !== false`):
   - `LocalAgentTask`s → preserved by `agentId`
   - `InProcessTeammateTask`s → preserved by `identity.agentId`
4. **Clear messages** — `setMessages(() => [])`
5. **Unblock proactive** — clears context-blocked flag so proactive ticks resume
6. **Reset conversationId** — forces logo re-render via `randomUUID()`
7. **Clear session caches** — calls `clearSessionCaches(preservedAgentIds)` which clears 37+ individual caches (see 4.1a)
8. **Reset CWD** — `setCwd(getOriginalCwd())`
9. **Clear readFileState** — file state cache
10. **Clear discoveredSkillNames, loadedNestedMemoryPaths** — `Set.clear()`
11. **Clean app state** — kills foreground tasks, clears `attribution`, `standaloneAgentContext`, `fileHistory`, resets MCP state (preserves `pluginReconnectKey`)
12. **Clear plan slugs** — `clearAllPlanSlugs()`
13. **Clear session metadata** — title, tag, agent name/color
14. **Regenerate session ID** — sets current as parent for analytics lineage
15. **Reset session file pointer** — new session file
16. **Re-point task symlinks** — preserved running agents get new `TaskOutput` symlinks
17. **Re-persist mode/worktree** — session metadata re-saved for future `--resume`
18. **SessionStart hooks** — executes start-of-session hooks, may produce hook messages

#### 4.1a clearSessionCaches() — Cache Clearing

**File:** `src/commands/clear/caches.ts` (144 lines)

Comprehensive cache invalidation touching 37+ subsystems:

| Cache | Function |
|-------|----------|
| Context caches | `getUserContext`, `getSystemContext`, `getGitStatus`, `getSessionStartDate` |
| File suggestion caches | `clearFileSuggestionCaches()` |
| Commands/skills cache | `clearCommandsCache()` |
| Prompt cache break detection | `resetPromptCacheBreakDetection()` (if no preserved agents) |
| System prompt injection | `setSystemPromptInjection(null)` |
| Last emitted date | `setLastEmittedDate(null)` |
| Post-compaction cleanup | `runPostCompactCleanup()` |
| Sent skill names | `resetSentSkillNames()` |
| Memory files cache | `resetGetMemoryFilesCache('session_start')` |
| Stored image paths | `clearStoredImagePaths()` |
| Session ingress caches | `clearAllSessions()` |
| Swarm permission callbacks | `clearAllPendingCallbacks()` (if no preserved agents) |
| Tungsten session tracking | `clearSessionsWithTungstenUsage()` (ANT-only, dynamic import) |
| Attribution caches | `clearAttributionCaches()` (COMMIT_ATTRIBUTION feature) |
| Repository detection caches | `clearRepositoryCaches()` |
| Bash command prefix caches | `clearCommandPrefixCaches()` |
| Dump prompts state | `clearAllDumpState()` (if no preserved agents) |
| Invoked skills cache | `clearInvokedSkills(preservedAgentIds)` |
| Git dir resolution cache | `clearResolveGitDirCache()` |
| Dynamic skills | `clearDynamicSkills()` |
| LSP diagnostic state | `resetAllLSPDiagnosticState()` |
| Tracked magic docs | `clearTrackedMagicDocs()` |
| Session environment variables | `clearSessionEnvVars()` |
| WebFetch URL cache | `clearWebFetchCache()` (dynamic import) |
| ToolSearch description cache | `clearToolSearchDescriptionCache()` (dynamic import) |
| Agent definitions cache | `clearAgentDefinitionsCache()` (dynamic import) |
| SkillTool prompt cache | `clearPromptCache()` (dynamic import) |

### 4.2 /compact — Context Compaction

**File:** `src/commands/compact/index.ts` (15 lines), `compact.ts` (287 lines)  
**Type:** `local` | **`supportsNonInteractive: true`** | **Argument hint:** `<optional custom summarization instructions>`

Gated by `DISABLE_COMPACT` env var.

**Full compaction flow** (`compact.ts:40-287`):
1. Projects messages: `getMessagesAfterCompactBoundary()`
2. Pre-compaction hooks: `executePreCompactHooks()`
3. Tries **session memory compaction** if no custom instructions
4. Falls through to **standard compaction**: `compactConversation()` with `abortController`
5. Handles abort signals (SIGINT/Ctrl-C)
6. Handles error types: incomplete response, not enough messages, user abort
7. Post-compaction: `markPostCompaction()`, `notifyCompaction()`, `runPostCompactCleanup()`, `suppressCompactWarning()`
8. Returns `{ type: 'compact', compactionResult }` or `{ type: 'skip' }`

Reactive compaction support via `REACTIVE_COMPACT` feature flag.

### 4.3 /cost — Session Cost

**File:** `src/commands/cost/index.ts` (23 lines), `cost.ts` (24 lines)  
**Type:** `local` | **`supportsNonInteractive: true`** | **Hidden for claude.ai subscribers**

**Behavior:**
- claude.ai subscribers: shows overage/subscription status; ANTs additionally see raw cost breakdown
- Non-subscribers: shows `formatTotalCost()` from cost tracker
- Hidden for subscribers (except ANTs) because cost is included in subscription

### 4.4 /advisor — Configure Advisor Model

**File:** `src/commands/advisor.ts` (109 lines)  
**Type:** `local` | **`supportsNonInteractive: true`** | **Argument hint:** `[<model>|off]`

**Behavior:**
- No args: displays current advisor model status
- `unset` / `off`: clears advisor model from state and settings
- `<model>`: validates model, checks `isValidAdvisorModel()`, sets in app state and persists via `updateSettingsForSource('userSettings', ...)`
- Validates model with server via `validateModel()`
- Warns if base model doesn't support advisors
- Gated by `canUserConfigureAdvisor()`

### 4.5 /version — Version Info

**File:** `src/commands/version.ts` (22 lines)  
**Type:** `local` | **ANT-only** | **`supportsNonInteractive: true`**

Returns `MACRO.VERSION` and optionally `MACRO.BUILD_TIME`. Only available to ANTs.

### 4.6 /bridge-kick — Bridge Failure Injection

**File:** `src/commands/bridge-kick.ts` (200 lines)  
**Type:** `local` | **ANT-only** | **`supportsNonInteractive: false`**

Debug tool for injecting bridge failure states to manually test recovery paths:

| Subcommand | Effect |
|------------|--------|
| `close <code>` | Fire `ws_closed` with given code |
| `poll <status> [type]` | Next poll throws `BridgeFatalError(status, type)` |
| `poll transient` | Next poll throws axios-style rejection |
| `register fail [N]` | Next N registers transient-fail |
| `register fatal` | Next register 403s (terminal) |
| `reconnect-session fail` | Next POST /bridge/reconnect fails |
| `heartbeat <status>` | Next heartbeat throws BridgeFatalError |
| `reconnect` | Force `doReconnect` directly |
| `status` | Print current bridge state |

### 4.7 /voice — Voice Mode Toggle

**File:** `src/commands/voice/index.ts` (20 lines)  
**Type:** `local` | **Availability:** `claude-ai` | **Feature:** `VOICE_MODE`

Gated by GrowthBook via `isVoiceGrowthBookEnabled()`. Lazy-loads `voice.js`. Hidden when voice mode is not available. (No `/vv` alias.)

### 4.8 /keybindings — Keybinding Config

**File:** `src/commands/keybindings/index.ts` (13 lines)  
**Type:** `local` | **`supportsNonInteractive: false`**

Opens or creates keybindings config file. Gated by `isKeybindingCustomizationEnabled()`.

### 4.9 /install-slack-app — Install Slack App

**File:** `src/commands/install-slack-app/index.ts` (12 lines)  
**Type:** `local` | **Availability:** `claude-ai` | **`supportsNonInteractive: false`**

Installs the Claude Slack app for slash command integration.

### 4.10 /stickers — Order Stickers

**File:** `src/commands/stickers/index.ts` (11 lines)  
**Type:** `local` | **`supportsNonInteractive: false`**

Orders Claude Code merchandise stickers.

### 4.11 /files — List Files in Context

**File:** `src/commands/files/index.ts` (12 lines)  
**Type:** `local` | **ANT-only** | **`supportsNonInteractive: true`**

Lists all files currently in context.

### 4.12 /heapdump — JS Heap Dump

**File:** `src/commands/heapdump/index.ts` (12 lines)  
**Type:** `local` | **`isHidden: true`** | **`supportsNonInteractive: true`**

Dumps the JS heap to `~/Desktop` for debugging memory issues.

### 4.13 /release-notes — View Release Notes

**File:** `src/commands/release-notes/index.ts` (11 lines)  
**Type:** `local` | **`supportsNonInteractive: true`**

Displays the current version's release notes/changelog.

### 4.14 /reload-plugins — Refresh Plugins

**File:** `src/commands/reload-plugins/index.ts` (18 lines)  
**Type:** `local` | **`supportsNonInteractive: false`**

Layer-3 refresh: applies pending plugin changes (install/uninstall/update) to the running session. SDK callers use `query.reloadPlugins()` control request instead.

### 4.15 /rewind — Restore Checkpoint

**File:** `src/commands/rewind/index.ts` (13 lines)  
**Type:** `local` | **Aliases:** `checkpoint` | **`supportsNonInteractive: false`**

Restores code and/or conversation to a previous checkpoint point.

### 4.16 /vim — Toggle Vim Mode

**File:** `src/commands/vim/index.ts` (11 lines)  
**Type:** `local` | **`supportsNonInteractive: false`**

Toggles between Vim and Normal editing modes for the input prompt.

### 4.17 /extra-usage (Non-Interactive)

**File:** `src/commands/extra-usage/index.ts` (31 lines) — exports both `extraUsage` and `extraUsageNonInteractive`  
**Type:** Two variants — `local-jsx` (interactive) and `local` (non-interactive)

The non-interactive variant (`extraUsageNonInteractive`) provides extra usage configuration in headless/SDK mode. Gated by `isOverageProvisioningAllowed()`.

### 4.18 /context (Non-Interactive)

**File:** `src/commands/context/index.ts` (24 lines) — exports both `context` (local-jsx) and `contextNonInteractive` (local)

The non-interactive variant renders context usage as a Markdown table rather than an Ink visualization. See section 5.3 for details.

### 4.19 /thinkback-play — Animation Playback

**File:** `src/commands/thinkback-play/index.ts` (17 lines)  
**Type:** `local` | **`isHidden: true`** | **`supportsNonInteractive: false`**

Hidden command that plays the Year in Review animation. Called by the thinkback skill after generation is complete. Gated by GrowthBook `tengu_thinkback`.

---

## 5. Local JSX Commands

Local JSX commands render interactive React/Ink TUI components.

### 5.1 /agents — Agent Configuration Manager

**File:** `src/commands/agents/index.ts` (10 lines)  
**Type:** `local-jsx`

Launches an interactive agent configuration manager for managing custom agent definitions.

### 5.2 /chrome — Claude in Chrome Settings

**File:** `src/commands/chrome/index.ts` (13 lines)  
**Type:** `local-jsx` | **Availability:** `claude-ai` | **285 lines** implementation

Manages "Claude in Chrome (Beta)" settings. Gated by `!getIsNonInteractiveSession()`.

### 5.3 /config — Config Panel

**File:** `src/commands/config/index.ts` (11 lines)  
**Type:** `local-jsx` | **Aliases:** `settings`

Opens an interactive configuration panel for managing Claude Code settings.

### 5.4 /context — Context Visualization

**File:** `src/commands/context/index.ts` (24 lines), `context.tsx` (64 lines), `context-noninteractive.ts` (325 lines)  
**Type:** `local-jsx` (interactive) + `local` (non-interactive)

**Interactive variant** (`context.tsx`):
1. Applies API-view transforms: `getMessagesAfterCompactBoundary()` + `projectView()` (CONTEXT_COLLAPSE feature)
2. Runs `microcompactMessages()` for accurate token representation
3. Calls `analyzeContextUsage()` with terminal width, model, tools, agent definitions
4. Renders to ANSI string via `<ContextVisualization>` component

**Non-interactive variant** (`context-noninteractive.ts:79-325`):
1. Shared `collectContextData()` function — mirrors query.ts transforms
2. Formats as Markdown table with sections:
   - Context usage (model, tokens, percentage)
   - Context collapse strategy status
   - Estimated usage by category table
   - MCP tools with server/token breakdowns
   - System tools (ANT-only)
   - System prompt sections (ANT-only)
   - Custom agents (type, source, tokens)
   - Memory files (type, path, tokens)
   - Skills (name, source, tokens)
   - Message breakdown (ANT-only): tool calls, results, attachments by type

### 5.5 /copy — Copy to Clipboard

**File:** `src/commands/copy/index.ts` (15 lines) | **371 lines** implementation  
**Type:** `local-jsx`

Copies Claude's last response to clipboard. Supports `/copy N` for the Nth-latest message.

### 5.6 /diff — View Diffs

**File:** `src/commands/diff/index.ts` (8 lines)  
**Type:** `local-jsx`

Shows uncommitted changes and per-turn diffs rendered in the TUI.

### 5.7 /doctor — Diagnostic Screen

**File:** `src/commands/doctor/index.ts` (12 lines)  
**Type:** `local-jsx`

Diagnoses and verifies Claude Code installation: checks version, connectivity, settings, tools. Gated by `DISABLE_DOCTOR_COMMAND`.

### 5.8 /effort — Set Effort Level

**File:** `src/commands/effort/index.ts` (13 lines) | **183 lines** implementation  
**Type:** `local-jsx` | **Argument hint:** `[low|medium|high|max|auto]`

Controls model effort level. Uses `shouldInferenceConfigCommandBeImmediate()` for immediate execution gating.

### 5.9 /extra-usage — Request Extra Usage

**File:** `src/commands/extra-usage/index.ts` (31 lines) — exports `extraUsage` and `extraUsageNonInteractive`  
**Type:** `local-jsx` | **Availability:** (gated by `isOverageProvisioningAllowed`)

Configures extra usage to keep working when rate limits are hit. The non-interactive variant handles headless/SDK mode.

### 5.10 /fast — Toggle Fast Mode

**File:** `src/commands/fast/index.ts` (26 lines) | **269 lines** implementation  
**Type:** `local-jsx` | **Availability:** `claude-ai`, `console` | **Argument hint:** `[on|off]`

Toggles fast mode (uses `FAST_MODE_MODEL_DISPLAY` model only). Gated by `isFastModeEnabled()`. Uses `shouldInferenceConfigCommandBeImmediate()`.

### 5.11 /feedback — Submit Feedback

**File:** `src/commands/feedback/index.ts` (26 lines) | **560 lines** implementation  
**Type:** `local-jsx` | **Aliases:** `bug` | **Argument hint:** `[report]`

Submits feedback about Claude Code. Disabled for: Bedrock, Vertex, Foundry, essential-traffic-only, ANTs, or when `allow_product_feedback` policy is denied.

### 5.12 /help — Show Help

**File:** `src/commands/help/index.ts` (10 lines)  
**Type:** `local-jsx`

Displays the interactive help screen with all available commands.

### 5.13 /hooks — Hook Configuration

**File:** `src/commands/hooks/index.ts` (11 lines)  
**Type:** `local-jsx` | **`immediate: true`**

Views hook configurations for tool events (PreToolUse, PostToolUse, Stop, etc.).

### 5.14 /ide — IDE Integration

**File:** `src/commands/ide/index.ts` (11 lines) | **646 lines** implementation  
**Type:** `local-jsx` | **Argument hint:** `[open]`

Manages IDE integrations (VS Code, JetBrains, etc.), shows installation status, opens project in IDE.

### 5.15 /install-github-app — Multi-Step Wizard

**File:** `src/commands/install-github-app/index.ts` (13 lines) | **14 files, 2322 lines total**  
**Type:** `local-jsx` | **Availability:** `claude-ai`, `console`

Multi-step wizard for setting up Claude GitHub Actions:

| Step File | Purpose |
|-----------|---------|
| `CheckGitHubStep.tsx` | Verify GitHub CLI is installed and authenticated |
| `ChooseRepoStep.tsx` | Select GitHub repository |
| `CheckExistingSecretStep.tsx` | Check for existing API key secrets |
| `ApiKeyStep.tsx` | Configure API key as GitHub Actions secret |
| `OAuthFlowStep.tsx` | Handle OAuth authorization flow |
| `InstallAppStep.tsx` | Install Claude GitHub App on repository |
| `setupGitHubActions.ts` | Create workflow YAML files |
| `CreatingStep.tsx` | Progress indicator during creation |
| `SuccessStep.tsx` | Completion confirmation |
| `ErrorStep.tsx` | Error handling and recovery |
| `WarningsStep.tsx` | Display configuration warnings |
| `ExistingWorkflowStep.tsx` | Handle pre-existing workflow files |
| `install-github-app.tsx` | Main orchestration component |

### 5.16 /login — OAuth Login

**File:** `src/commands/login/index.ts` (14 lines) | **104 lines** implementation  
**Type:** `local-jsx`

Signs in with Anthropic account. Description changes dynamically:
- Has API key: "Switch Anthropic accounts"
- No API key: "Sign in with your Anthropic account"

Gated by `DISABLE_LOGIN_COMMAND`. Excluded from 3P services (Bedrock/Vertex/Foundry).

### 5.17 /logout — Sign Out

**File:** `src/commands/logout/index.ts` (10 lines) | **82 lines** implementation  
**Type:** `local-jsx`

Signs out from Anthropic account. Gated by `DISABLE_LOGOUT_COMMAND`. Excluded from 3P services.

### 5.18 /mcp — MCP Server Management

**File:** `src/commands/mcp/index.ts` (12 lines)  
**Type:** `local-jsx` | **`immediate: true`** | **Argument hint:** `[enable|disable [server-name]]`

Manages MCP (Model Context Protocol) servers. Lazy-loads `mcp.js` (4 files in directory).

### 5.19 /memory — Memory File Editor

**File:** `src/commands/memory/index.ts` (10 lines)  
**Type:** `local-jsx`

Opens an editor for Claude memory files (CLAUDE.md, CLAUDE.local.md, project rules).

### 5.20 /mobile — QR Codes for Mobile App

**File:** `src/commands/mobile/index.ts` (11 lines)  
**Type:** `local-jsx` | **Aliases:** `ios`, `android`

Shows QR codes to download the Claude mobile app for iOS and Android.

### 5.21 /model — Model Selection

**File:** `src/commands/model/index.ts` (16 lines) | **297 lines** implementation  
**Type:** `local-jsx` | **Argument hint:** `[model]`

Sets the AI model. Description dynamically shows current model name via `renderModelName(getMainLoopModel())`. Uses `shouldInferenceConfigCommandBeImmediate()`.

### 5.22 /output-style — Deprecation Notice

**File:** `src/commands/output-style/index.ts` (11 lines)  
**Type:** `local-jsx` | **`isHidden: true`**

Deprecated — redirects users to `/config` for output style changes. Hidden from help.

### 5.23 /passes — Guest Passes

**File:** `src/commands/passes/index.ts` (22 lines)  
**Type:** `local-jsx`

Shares free Claude Code guest passes with friends. Description dynamically shows referrer reward status. Hidden when not eligible.

### 5.24 /permissions — Permission Rules

**File:** `src/commands/permissions/index.ts` (11 lines)  
**Type:** `local-jsx` | **Aliases:** `allowed-tools`

Manages allow & deny tool permission rules with an interactive list.

### 5.25 /plan — Plan Mode

**File:** `src/commands/plan/index.ts` (11 lines) | **122 lines** implementation  
**Type:** `local-jsx` | **Argument hint:** `[open|<description>]`

Enables plan mode or views the current session plan. Plan mode shows a structured plan before execution.

### 5.26 /plugin — Plugin Marketplace UI

**File:** `src/commands/plugin/index.tsx` (11 lines) | **17 files, 7259 lines total**  
**Type:** `local-jsx` | **Aliases:** `plugins`, `marketplace` | **`immediate: true`**

Full plugin marketplace interface for browsing, installing, updating, and managing plugins. The largest command subsystem by line count.

### 5.27 /privacy-settings — Privacy Settings

**File:** `src/commands/privacy-settings/index.ts` (14 lines)  
**Type:** `local-jsx` | **Availability:** (gated by `isConsumerSubscriber`)

Views and updates privacy settings. Only available to consumer subscribers.

### 5.28 /rate-limit-options — Rate Limit Dialog

**File:** `src/commands/rate-limit-options/index.ts` (19 lines) | **210 lines** implementation  
**Type:** `local-jsx` | **`isHidden: true`** | **Availability:** (gated by `isClaudeAISubscriber`)

Internal-only dialog showing options when rate limit is reached. Hidden from help.

### 5.29 /remote-env — Remote Environment Config

**File:** `src/commands/remote-env/index.ts` (15 lines)  
**Type:** `local-jsx` | **Availability:** (gated by `isClaudeAISubscriber` + `allow_remote_sessions` policy)

Configures the default remote environment for teleport sessions.

### 5.30 /web-setup — Remote Setup (Web)

**File:** `src/commands/remote-setup/index.ts` (20 lines) | **369 lines** implementation  
**Type:** `local-jsx` | **Availability:** `claude-ai` | **Feature:** `CCR_REMOTE_SETUP`

Sets up Claude Code on the web (requires GitHub account connection). Gated by GrowthBook `tengu_cobalt_lantern` and `allow_remote_sessions` policy.

### 5.31 /resume — Session Resume

**File:** `src/commands/resume/index.ts` (12 lines) | **275 lines** implementation  
**Type:** `local-jsx` | **Aliases:** `continue` | **Argument hint:** `[conversation id or search term]`

Interactive session picker for resuming previous conversations by ID or title search.

### 5.32 /sandbox — Sandbox Settings

**File:** `src/commands/sandbox-toggle/index.ts` (50 lines) | **83 lines** implementation  
**Type:** `local-jsx` | **`immediate: true`** | **Argument hint:** `exclude "command pattern"`

Configures sandbox execution settings. Description dynamically shows:
- Current status (enabled/disabled)
- Auto-allow mode
- Unandboxed fallback status
- Managed/policy-locked status
- Dependency warning icon

Hidden when platform doesn't support sandboxing.

### 5.33 /session — Remote Session QR

**File:** `src/commands/session/index.ts` (16 lines) | **140 lines** implementation  
**Type:** `local-jsx` | **Aliases:** `remote`

Shows remote session URL and QR code. Only available in remote mode (`getIsRemoteMode()`).

### 5.34 /skills — Skill Browser

**File:** `src/commands/skills/index.ts` (10 lines)  
**Type:** `local-jsx`

Lists available skills from all sources (project, user, bundled, plugin, MCP).

### 5.35 /status — Status Display

**File:** `src/commands/status/index.ts` (12 lines)  
**Type:** `local-jsx` | **`immediate: true`**

Shows comprehensive status: version, model, account, API connectivity, tool statuses.

### 5.36 /tag — Session Tagging

**File:** `src/commands/tag/index.ts` (12 lines) | **215 lines** implementation  
**Type:** `local-jsx` | **ANT-only** | **Argument hint:** `<tag-name>`

Toggles searchable tags on the current session for session organization and filtering.

### 5.37 /tasks — Task List

**File:** `src/commands/tasks/index.ts` (11 lines)  
**Type:** `local-jsx` | **Aliases:** `bashes`

Lists and manages background tasks (backgrounded shell commands and agent tasks).

### 5.38 /terminal-setup — Terminal Keybinding Install

**File:** `src/commands/terminalSetup/index.ts` (23 lines) | **531 lines** implementation  
**Type:** `local-jsx`

Installs key bindings for the terminal:
- Apple Terminal: enables Option+Enter for newlines and visual bell
- Other terminals: installs Shift+Enter for newlines

Hidden when terminal natively supports CSI u / Kitty keyboard protocol (Ghostty, Kitty, iTerm2, WezTerm). Description dynamically adapts based on detected terminal.

### 5.39 /think-back — Year in Review

**File:** `src/commands/thinkback/index.ts` (13 lines) | **554 lines** implementation  
**Type:** `local-jsx`

"Your 2025 Claude Code Year in Review" — interactive retrospective with animation. Gated by GrowthBook `tengu_thinkback`.

### 5.40 /usage — Usage Limits

**File:** `src/commands/usage/index.ts` (9 lines)  
**Type:** `local-jsx` | **Availability:** `claude-ai`

Shows plan usage limits and current consumption.

### 5.41 /exit — Exit REPL

**File:** `src/commands/exit/index.ts` (12 lines)  
**Type:** `local-jsx` | **Aliases:** `quit` | **`immediate: true`**

Exits the REPL. Immediate execution (bypasses message queue).

### 5.42 /export — Export Conversation

**File:** `src/commands/export/index.ts` (11 lines)  
**Type:** `local-jsx` | **Argument hint:** `[filename]`

Exports the current conversation to a file or clipboard.

### 5.43 /rename — Rename Conversation

**File:** `src/commands/rename/index.ts` (12 lines)  
**Type:** `local-jsx` | **`immediate: true`** | **Argument hint:** `[name]`

Renames the current conversation session. Immediate execution.

### 5.44 /color — Set Prompt Bar Color

**File:** `src/commands/color/index.ts` (16 lines)  
**Type:** `local-jsx` | **`immediate: true`** | **Argument hint:** `<color|default>`

Sets the prompt bar color for the session. Immediate execution.

### 5.45 /theme — Change Theme

**File:** `src/commands/theme/index.ts` (10 lines)  
**Type:** `local-jsx`

Opens an interactive theme selector for the TUI.

### 5.46 /stats — Usage Statistics

**File:** `src/commands/stats/index.ts` (10 lines)  
**Type:** `local-jsx`

Shows Claude Code usage statistics and activity dashboard.

### 5.47 /upgrade — Upgrade Plan

**File:** `src/commands/upgrade/index.ts` (16 lines)  
**Type:** `local-jsx` | **Availability:** `claude-ai`

Upgrade to Max for higher rate limits and more Opus usage. Gated by `DISABLE_UPGRADE_COMMAND`.

### 5.48 /desktop — Continue in Desktop App

**File:** `src/commands/desktop/index.ts` (26 lines)  
**Type:** `local-jsx` | **Aliases:** `app` | **Availability:** `claude-ai`

Continues the current session in Claude Desktop. Only supported on macOS (`darwin`) and Windows x64 (`win32` with `arch === 'x64'`).

### 5.49 /btw — Side Question (Quick Note)

**File:** `src/commands/btw/index.ts` (13 lines) | **243 lines** implementation  
**Type:** `local-jsx` | **`immediate: true`** | **Argument hint:** `<question>`

"Ask a quick side question without interrupting the main conversation." Lazy-loads `btw.tsx`. Listed in `REMOTE_SAFE_COMMANDS`.

### 5.50 /add-dir — Add Working Directory

**File:** `src/commands/add-dir/index.ts` (11 lines) | **126 lines** implementation  
**Type:** `local-jsx` | **Argument hint:** `<path>`

"Add a new working directory." Validates path via `validateDirectoryForWorkspace()` (`validation.ts`), then renders `<AddWorkspaceDirectory>` or applies permission updates. Lazy-loads `add-dir.tsx`.

### 5.51 /brief — Brief-Only Mode Toggle

**File:** `src/commands/brief.ts` (130 lines)  
**Type:** `local-jsx` | **Feature:** `KAIROS` or `KAIROS_BRIEF` | **`immediate: true`**

"Toggle brief-only mode." Gated by GrowthBook `tengu_kairos_brief_config.enable_slash_command` (Zod-validated). Uses `BRIEF_TOOL_NAME` and toggles `setUserMsgOptIn()`. Not in external builds unless the feature flag is enabled.

### 5.52 /ultrareview — Remote Deep PR Review

**File:** `src/commands/review.ts` (57 lines) + `src/commands/review/ultrareviewCommand.tsx`  
**Type:** `local-jsx` | **Separate from `/review`** (which stays `prompt`)

"~10–20 min · Finds and verifies bugs in your branch. Runs in Claude Code on the web." Gated by `isUltrareviewEnabled()` (GrowthBook `tengu_review_bughunter_config.enabled`). Renders overage permission dialog via `UltrareviewOverageDialog.tsx` when free reviews are exhausted.

---

## 6. Bridge/Migration Commands

### 6.1 /remote-control /rc — Remote Control Bridge

**File:** `src/commands/bridge/index.ts` (26 lines)  
**Type:** `local-jsx` | **Feature:** `BRIDGE_MODE` | **`immediate: true`** | **Argument hint:** `[name]`

Connects the terminal for remote-control sessions (CCR — Claude Code Remote). Gated by `BRIDGE_MODE` feature flag and `isBridgeEnabled()`.

### 6.2 /branch — Conversation Forking

**File:** `src/commands/branch/index.ts` (14 lines) | **296 lines** implementation  
**Type:** `local-jsx` | **Aliases:** `fork` (only when `FORK_SUBAGENT` is disabled) | **Argument hint:** `[name]`

Creates a branch (fork) of the current conversation at the current point, enabling parallel exploration paths.

### 6.3 createMovedToPluginCommand — Plugin Migration Factory

**File:** `src/commands/createMovedToPluginCommand.ts` (65 lines)

Factory function that creates a `prompt` command acting as a migration shim for functionality moved from built-in to plugin:

```typescript
createMovedToPluginCommand({ name, description, progressMessage, pluginName, pluginCommand, getPromptWhileMarketplaceIsPrivate })
```

**Behavior:**
- **ANTs** (`USER_TYPE === 'ant'`): Returns instructions: "This command has been moved to a plugin. Install: `claude plugin install <pluginName>@claude-code-marketplace`. Use: `/<pluginName>:<pluginCommand>`."
- **External users**: Uses `getPromptWhileMarketplaceIsPrivate` to render the actual prompt inline (while marketplace is private)

**Used by:** `/security-review`, `/pr-comments`

### 6.4 /ultraplan — Remote Advanced Planning

**File:** `src/commands/ultraplan.tsx` (471 lines)  
**Type:** `local-jsx` | **Feature:** `ULTRAPLAN` | **ANT-only** (in `INTERNAL_ONLY_COMMANDS`) | **Argument hint:** `<prompt>`

"~10–30 min · Claude Code on the web drafts an advanced plan you can edit and approve." Exports `launchUltraplan`, `stopUltraplan`, `buildUltraplanPrompt`. Only registered when `feature('ULTRAPLAN')` and `USER_TYPE === 'ant' && !IS_DEMO`.

### 6.5 `commands/install.tsx` — CLI Native Installer (Not a Slash Command)

**File:** `src/commands/install.tsx` (300 lines)  
**Type:** `local-jsx`-shaped export | **Not in `COMMANDS` or `getCommands()`**

Used only from `cli.tsx` for native build installation (`install` export with `call(onDone, context, args)`). Supports `--force` and target version (`latest`, `stable`, or semver). Not available as `/install` in the REPL.

---

## 7. Internal & ANT-Only Stubs

All the following are 1-line stub files that mark commands as disabled (`isEnabled: () => false`) and hidden. These are internal/ANT-only commands stripped from the external build:

| Directory | File | Purpose |
|-----------|------|---------|
| `backfill-sessions/` | `index.js` | Session backfill utility |
| `break-cache/` | `index.js` | Cache break injection |
| `bughunter/` | `index.js` | Bug hunter tool |
| `ctx_viz/` | `index.js` | Context visualization debug |
| `good-claude/` | `index.js` | Internal quality assessment |
| `issue/` | `index.js` | Issue reporting |
| `mock-limits/` | `index.js` | Mock rate limit injection |
| `onboarding/` | `index.js` | Onboarding flow |
| `share/` | `index.js` | Session sharing |
| `teleport/` | `index.js` | Remote teleport |
| `ant-trace/` | `index.js` | ANT trace tool |
| `perf-issue/` | `index.js` | Performance issue reporting |
| `env/` | `index.js` | Environment info |
| `oauth-refresh/` | `index.js` | OAuth token refresh |
| `debug-tool-call/` | `index.js` | Debug tool call injection |
| `autofix-pr/` | `index.js` | Auto-fix PR |
| `summary/` | `index.js` | Session summarization |
| `reset-limits/` | `index.js` | Limits reset (ANT-only) |
| `agents-platform/` | (conditional import) | ANT agents platform |

These are collected in `INTERNAL_ONLY_COMMANDS` array (`commands.ts:225-254`) and only included when `USER_TYPE === 'ant' && !IS_DEMO`.

---

## 8. Remote Safety & Bridge Safety

### 8.1 REMOTE_SAFE_COMMANDS

**`commands.ts:619-637`** — Commands safe for `--remote` mode. These only affect local TUI state and have no local filesystem/git/shell/IDE/MCP dependencies:

```
session, exit, clear, help, theme, color, vim, cost, usage, copy, btw,
feedback, plan, keybindings, statusline, stickers, mobile
```

Used in:
1. Pre-filtering commands in `main.tsx` before REPL renders (prevents race with CCR init)
2. Preserving local-only commands in REPL's `handleRemoteInit` after CCR filters

### 8.2 BRIDGE_SAFE_COMMANDS

**`commands.ts:651-660`** — Built-in `local` commands safe for execution over the Remote Control bridge:

```
compact, clear, cost, summary, releaseNotes, files
```

These produce text output that streams back to mobile/web clients without terminal-only side effects.

### 8.3 isBridgeSafeCommand()

**`commands.ts:672-676`** — Determines if a command can execute over the bridge:
- `'local-jsx'` → **false** (they render Ink UI)
- `'prompt'` → **true** (expand to text sent to model)
- `'local'` → **only if in `BRIDGE_SAFE_COMMANDS`**

### 8.4 filterCommandsForRemoteMode()

**`commands.ts:684-686`** — Pre-filters commands for `--remote` mode to only include `REMOTE_SAFE_COMMANDS`.

### 8.5 builtInCommandNames

**`commands.ts:348-351`** — Memoized `Set<string>` of all built-in command names + aliases. Used for distinguishing built-in from dynamic commands.

---

## 9. Skill/Plugin Loading Pipeline

### 9.1 loadAllCommands() Flow

```
loadAllCommands(cwd) [memoized]
  ├── getSkills(cwd) [parallel]
  │   ├── getSkillDirCommands(cwd) — from /.claude/skills/ and project .claude/skills/
  │   ├── getPluginSkills() — from installed plugins
  │   ├── getBundledSkills() — bundled skills registered at startup
  │   └── getBuiltinPluginSkillCommands() — from enabled built-in plugins
  │
  ├── getPluginCommands() [parallel]
  │   └── clearPluginCommandCache() — for invalidation
  │
  ├── getWorkflowCommands(cwd) [parallel, gated by WORKFLOW_SCRIPTS]
  │   └── WorkflowTool/createWorkflowCommand → getWorkflowCommands
  │
  └── Merge order:
      1. bundledSkills
      2. builtinPluginSkills
      3. skillDirCommands
      4. workflowCommands
      5. pluginCommands
      6. pluginSkills
      7. COMMANDS() (built-in commands)
```

### 9.2 getCommands() Post-Processing

```
getCommands(cwd)
  ├── loadAllCommands(cwd) [memoized]
  ├── getDynamicSkills() — skills discovered during file operations
  ├── Filter: meetsAvailabilityRequirement + isCommandEnabled
  ├── Dedupe dynamic skills by name
  └── Insert dynamic skills after plugin skills, before built-in commands
```

### 9.3 Skill Loading Sources

| Source | Loader Function | Description |
|--------|----------------|-------------|
| Skill directories | `getSkillDirCommands(cwd)` | `.claude/skills/` (project) and user skill dir |
| Plugin skills | `getPluginSkills()` | Skills from installed plugins |
| Bundled skills | `getBundledSkills()` | Built-in skills registered at startup |
| Built-in plugin skills | `getBuiltinPluginSkillCommands()` | Skills from enabled built-in plugins |
| MCP skills | `getMcpSkillCommands()` | MCP-provided prompt commands (gated by `MCP_SKILLS`) |
| Dynamic skills | `getDynamicSkills()` | Skills discovered during file operations |
| Workflow commands | `getWorkflowCommands(cwd)` | Workflow script commands (`WORKFLOW_SCRIPTS`) |

---

## 10. Command Discovery Flow

### 10.1 Complete Command Lifecycle

```
1. Module initialization
   └── COMMANDS memoized array created (reads from config lazily)

2. First getCommands(cwd) call
   ├── loadAllCommands(cwd) — parallel load from all sources
   ├── Build merged list
   ├── Filter by availability + isEnabled
   └── Return

3. Command invocation (user types /command-name)
   ├── findCommand() — locate by name/alias/userFacingName
   ├── For 'prompt' type:
   │   ├── call getPromptForCommand(args, context)
   │   ├── executeShellCommandsInPrompt() if needed
   │   └── Expand content blocks into conversation
   │
   ├── For 'local' type:
   │   ├── call cmd.load() → get { call }
   │   ├── call(args, context) → LocalCommandResult
   │   └── Handle result (text display, compaction, skip)
   │
   └── For 'local-jsx' type:
       ├── call cmd.load() → get { call }
       ├── call(onDone, context, args) → React.ReactNode
       └── Render Ink component tree

4. Cache invalidation
   ├── /clear → clearSessionCaches()
   ├── /reload-plugins → clearPluginCommandCache() + clearPluginSkillsCache()
   └── Dynamic skill added → clearCommandMemoizationCaches()
```

### 10.2 Conditionally Loaded (Feature-Flagged) Commands

These commands are only loaded when their corresponding feature flag is enabled:

| Flag | Command(s) | Description |
|------|-----------|-------------|
| `CCR_REMOTE_SETUP` | `/web-setup` | Remote web setup |
| `FORK_SUBAGENT` | `/fork` | Conversation forking |
| `BUDDY` | `/buddy` | Buddy companion |
| `PROACTIVE` / `KAIROS` | proactive | Proactive assistance |
| `KAIROS` / `KAIROS_BRIEF` | `/brief` | Brief mode |
| `KAIROS` | `/assistant` | KAIROS assistant session |
| `BRIDGE_MODE` | `/remote-control`, `/rc` | Remote control bridge |
| `DAEMON` + `BRIDGE_MODE` | remote control server | Daemon-mode bridge |
| `VOICE_MODE` | `/voice` | Voice mode toggle |
| `HISTORY_SNIP` | force-snip | History snipping |
| `WORKFLOW_SCRIPTS` | workflows | Workflow commands |
| `UDS_INBOX` | `/peers` | Peer inbox |
| `TORCH` | `/torch` | Torch feature |
| `ULTRAPLAN` | `/ultraplan` | Ultra plan mode |
| `KAIROS_GITHUB_WEBHOOKS` | subscribe-pr | GitHub webhook PR subscription |
| `NEW_INIT` | `/init` (new 8-phase variant) | Init mode switching |
| `REACTIVE_COMPACT` | `/compact` (reactive path) | Reactive compaction |
| `CONTEXT_COLLAPSE` | `/context` (projectView) | Context collapse visualization |
| `MCP_SKILLS` | MCP skills in SkillTool | MCP-provided skills |
| `COMMIT_ATTRIBUTION` | attribution caches clear | Commit attribution cleanup |
| `COORDINATOR_MODE` | `/clear` mode re-persist | Coordinator mode persistence |
| `EXPERIMENTAL_SKILL_SEARCH` | `clearSkillIndexCache` | Skill search index |

### 10.3 Ant-Only Command Separation

ANT-only commands are excluded from the external build entirely via dead code elimination (Bun's `feature()` gating on the `import` statements). The `INTERNAL_ONLY_COMMANDS` array (`commands.ts:225-254`) lists 25 commands (up to 28 with `forceSnip`/`ultraplan`/`subscribePr`) that only load when `USER_TYPE === 'ant' && !IS_DEMO`.

---

## Appendix: Command Quick Reference

### All Prompt Commands

| Name | Progress Message | Key Feature |
|------|-----------------|-------------|
| `commit` | "creating commit" | Git Safety Protocol, HEREDOC commits |
| `commit-push-pr` | "creating commit and PR" | Branch, commit, push, PR + Slack notification |
| `init` | "analyzing your codebase" | 8-phase CLAUDE.md/skills/hooks creation |
| `init-verifiers` | "analyzing your project..." | Auto-detect + create Playwright/Tmux/HTTP verifiers |
| `review` | "reviewing pull request" | `gh pr`-based code review |
| `security-review` | "analyzing code changes for security risks" | Confidence-scored vulnerability scanning |
| `statusline` | "setting up statusLine" | Agent-based PS1 config → status line |
| `pr-comments` | "fetching PR comments" | GitHub PR comment extraction |
| `insights` | "analyzing your sessions" | 113KB lazy-loaded session analytics |

### All Local Commands

| Name | Aliases | Supports Non-Interactive |
|------|---------|------------------------|
| `clear` | `reset`, `new` | No |
| `compact` | — | Yes |
| `cost` | — | Yes |
| `advisor` | — | Yes |
| `version` | — | Yes |
| `bridge-kick` | — | No |
| `voice` | — | No |
| `keybindings` | — | No |
| `install-slack-app` | — | No |
| `stickers` | — | No |
| `files` | — | Yes |
| `heapdump` | — | Yes |
| `release-notes` | — | Yes |
| `reload-plugins` | — | No |
| `rewind` | `checkpoint` | No |
| `vim` | — | No |
| `thinkback-play` | — | No |
| `extra-usage` (non-interactive) | — | Yes |
| `context` (non-interactive) | — | Yes |

### All Local JSX Commands

| Name | Aliases | Immediate | Argument Hint |
|------|---------|-----------|---------------|
| `agents` | — | — | — |
| `chrome` | — | — | — |
| `config` | `settings` | — | — |
| `context` (interactive) | — | — | — |
| `copy` | — | — | (N for Nth-latest) |
| `diff` | — | — | — |
| `doctor` | — | — | — |
| `effort` | — | dynamic | `[low\|medium\|high\|max\|auto]` |
| `exit` | `quit` | Yes | — |
| `export` | — | — | `[filename]` |
| `extra-usage` | — | — | — |
| `fast` | — | dynamic | `[on\|off]` |
| `feedback` | `bug` | — | `[report]` |
| `help` | — | — | — |
| `hooks` | — | Yes | — |
| `ide` | — | — | `[open]` |
| `install-github-app` | — | — | — |
| `login` | — | — | — |
| `logout` | — | — | — |
| `mcp` | — | Yes | `[enable\|disable [server-name]]` |
| `memory` | — | — | — |
| `mobile` | `ios`, `android` | — | — |
| `model` | — | dynamic | `[model]` |
| `output-style` | — | — | (hidden) |
| `passes` | — | — | — |
| `permissions` | `allowed-tools` | — | — |
| `plan` | — | — | `[open\|<description>]` |
| `plugin` | `plugins`, `marketplace` | Yes | — |
| `privacy-settings` | — | — | — |
| `rate-limit-options` | — | — | (hidden) |
| `remote-env` | — | — | — |
| `web-setup` | — | — | — |
| `resume` | `continue` | — | `[id or search term]` |
| `sandbox` | — | Yes | `exclude "command pattern"` |
| `session` | `remote` | — | — |
| `skills` | — | — | — |
| `status` | — | Yes | — |
| `tag` | — | — | `<tag-name>` |
| `tasks` | `bashes` | — | — |
| `terminal-setup` | — | — | — |
| `think-back` | — | — | — |
| `usage` | — | — | — |
| `rename` | — | Yes | `[name]` |
| `color` | — | Yes | `<color\|default>` |
| `theme` | — | — | — |
| `stats` | — | — | — |
| `upgrade` | — | — | — |
| `desktop` | `app` | — | — |
| `ultrareview` | — | — | — |
| `btw` | — | Yes | `<question>` |
| `add-dir` | — | — | `<path>` |
| `add-dir` | — | — | `<path>` |
| `branch` | `fork` (conditional) | — | `[name]` |
| `brief` | — | Yes | — |
| `remote-control` | `rc` | Yes | `[name]` |
