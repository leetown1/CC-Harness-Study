# 03 - Bundled Skills Deep Dive

> Comprehensive analysis of all 17 bundled skill files in `F:\Claude\src\skills\bundled\`

---

## Architecture Overview

### Registration Pattern

Every bundled skill follows a uniform pattern:

1. A module exports a `register<Name>Skill()` function (e.g. `registerDebugSkill()`)
2. That function calls `registerBundledSkill(definition)` from `../bundledSkills.js`
3. The `initBundledSkills()` function in `index.ts` calls each register function at startup
4. Some skills are gated behind feature flags (`AI_TRIGGERS`, `KAIROS`, etc.) or `USER_TYPE === 'ant'` checks

### `BundledSkillDefinition` Type (from `bundledSkills.ts`)

```typescript
export type BundledSkillDefinition = {
  name: string
  description: string
  aliases?: string[]
  whenToUse?: string
  argumentHint?: string
  allowedTools?: string[]
  model?: string
  disableModelInvocation?: boolean
  userInvocable?: boolean
  isEnabled?: () => boolean
  hooks?: HooksSettings
  context?: 'inline' | 'fork'
  agent?: string
  files?: Record<string, string>
  getPromptForCommand: (args: string, context: ToolUseContext) => Promise<ContentBlockParam[]>
}
```

### `registerBundledSkill` (from `bundledSkills.ts`)

```typescript
export function registerBundledSkill(definition: BundledSkillDefinition): void
```

Creates a `Command` object of type `'prompt'` with `source: 'bundled'` and pushes it into the internal `bundledSkills` array. If `files` are provided, wraps `getPromptForCommand` to lazily extract files to disk on first invocation.

**Key functions in `bundledSkills.ts`:**
| Function | Signature | Description |
|---|---|---|
| `registerBundledSkill` | `(definition: BundledSkillDefinition) => void` | Registers a bundled skill into the global command registry |
| `getBundledSkills` | `() => Command[]` | Returns a copy of all registered bundled skills |
| `clearBundledSkills` | `() => void` | Clears the registry (used in tests) |
| `getBundledSkillExtractDir` | `(skillName: string) => string` | Returns deterministic extraction directory for a bundled skill's reference files |
| `extractBundledSkillFiles` | `(skillName: string, files: Record<string, string>) => Promise<string \| null>` | Lazily extracts reference files to disk (internal) |
| `writeSkillFiles` | `(dir: string, files: Record<string, string>) => Promise<void>` | Writes skill files grouped by parent dir (internal) |
| `safeWriteFile` | `(p: string, content: string) => Promise<void>` | Writes with O_EXCL/O_NOFOLLOW for security (internal) |
| `resolveSkillFilePath` | `(baseDir: string, relPath: string) => string` | Validates path doesn't escape skill dir (internal) |
| `prependBaseDir` | `(blocks: ContentBlockParam[], baseDir: string) => ContentBlockParam[]` | Prepends base directory info to content blocks (internal) |

---

## 1. `index.ts` — Initialization Hub

**File:** `F:\Claude\src\skills\bundled\index.ts` (79 lines)

### Export

```typescript
export function initBundledSkills(): void
```

### Description

Called at startup to register all skills that ship with the CLI. Each call to a `register*Skill()` function creates a `Command` object and pushes it into the global bundled skills registry.

### Registration Order

| # | Call | Feature Gate | Notes |
|---|---|---|---|
| 1 | `registerUpdateConfigSkill()` | None | Settings/hooks configuration |
| 2 | `registerKeybindingsSkill()` | None | Keybinding customization help |
| 3 | `registerVerifySkill()` | None | Verify code changes (ant-only internally) |
| 4 | `registerDebugSkill()` | None | Debug logging |
| 5 | `registerLoremIpsumSkill()` | None | Placeholder text (ant-only internally) |
| 6 | `registerSkillifySkill()` | None | Skill creation (ant-only internally) |
| 7 | `registerRememberSkill()` | None | Memory review (ant-only internally) |
| 8 | `registerSimplifySkill()` | None | Code review/cleanup |
| 9 | `registerBatchSkill()` | None | Parallel batch orchestration |
| 10 | `registerStuckSkill()` | None | Diagnose stuck sessions (ant-only internally) |
| 11 | `registerDreamSkill()` | `KAIROS \|\| KAIROS_DREAM` | Dream/reflection feature |
| 12 | `registerHunterSkill()` | `REVIEW_ARTIFACT` | Review artifact feature |
| 13 | `registerLoopSkill()` | `AGENT_TRIGGERS` | Recurring prompts |
| 14 | `registerScheduleRemoteAgentsSkill()` | `AGENT_TRIGGERS_REMOTE` | Remote agent scheduling |
| 15 | `registerClaudeApiSkill()` | `BUILDING_CLAUDE_APPS` | Claude API development guide |
| 16 | `registerClaudeInChromeSkill()` | `shouldAutoEnableClaudeInChrome()` | Browser automation |
| 17 | `registerRunSkillGeneratorSkill()` | `RUN_SKILL_GENERATOR` | Run external skill generator |

### Imports

```typescript
import { feature } from 'bun:bundle'
import { shouldAutoEnableClaudeInChrome } from 'src/utils/claudeInChrome/setup.js'
import { registerBatchSkill } from './batch.js'
import { registerClaudeInChromeSkill } from './claudeInChrome.js'
import { registerDebugSkill } from './debug.js'
import { registerKeybindingsSkill } from './keybindings.js'
import { registerLoremIpsumSkill } from './loremIpsum.js'
import { registerRememberSkill } from './remember.js'
import { registerSimplifySkill } from './simplify.js'
import { registerSkillifySkill } from './skillify.js'
import { registerStuckSkill } from './stuck.js'
import { registerUpdateConfigSkill } from './updateConfig.js'
import { registerVerifySkill } from './verify.js'
```

---

## 2. `batch.ts` — Parallel Work Orchestration

**File:** `F:\Claude\src\skills\bundled\batch.ts` (124 lines)

### Export

```typescript
export function registerBatchSkill(): void
```

### Constants

```typescript
const MIN_AGENTS = 5
const MAX_AGENTS = 30
```

| Constant | Value | Description |
|---|---|---|
| `MIN_AGENTS` | `5` | Minimum number of parallel workers |
| `MAX_AGENTS` | `30` | Maximum number of parallel workers |
| `WORKER_INSTRUCTIONS` | (long string) | Instructions template for each worker agent (simplify, test, e2e, commit, push, report) |
| `NOT_A_GIT_REPO_MESSAGE` | (string) | Error message when not in a git repo |
| `MISSING_INSTRUCTION_MESSAGE` | (string) | Error message when no instruction provided |

### Internal Functions

```typescript
function buildPrompt(instruction: string): string
```

Builds a comprehensive orchestration prompt with three phases:
1. **Phase 1: Research and Plan** — Enter plan mode, research scope, decompose into 5-30 independent work units
2. **Phase 2: Spawn Workers** — Launch one background agent per work unit with `isolation: "worktree"` and `run_in_background: true`
3. **Phase 3: Track Progress** — Render status table, update from agent completion notifications

### Registration Details

```typescript
registerBundledSkill({
  name: 'batch',
  description: 'Research and plan a large-scale change, then execute it in parallel across 5-30 isolated worktree agents that each open a PR.',
  whenToUse: 'Use when the user wants to make a sweeping, mechanical change across many files...',
  argumentHint: '<instruction>',
  userInvocable: true,
  disableModelInvocation: true,
  async getPromptForCommand(args) { /* validates args, checks git repo, returns prompt */ },
})
```

**Key behaviors:**
- Validates input is non-empty (shows usage examples otherwise)
- Validates current directory is a git repo (required for worktree isolation)
- Each worker is instructed to: simplify changes, run tests, verify e2e, commit, push, create PR, report result
- Workers use `subagent_type: "general-purpose"` unless a more specific type fits
- Coordinator tracks results via PR URLs parsed from agent output

### Imports

```typescript
import { AGENT_TOOL_NAME } from '../../tools/AgentTool/constants.js'
import { ASK_USER_QUESTION_TOOL_NAME } from '../../tools/AskUserQuestionTool/prompt.js'
import { ENTER_PLAN_MODE_TOOL_NAME } from '../../tools/EnterPlanModeTool/constants.js'
import { EXIT_PLAN_MODE_TOOL_NAME } from '../../tools/ExitPlanModeTool/constants.js'
import { SKILL_TOOL_NAME } from '../../tools/SkillTool/constants.js'
import { getIsGit } from '../../utils/git.js'
import { registerBundledSkill } from '../bundledSkills.js'
```

---

## 3. `claudeApi.ts` — Claude API Development Guide

**File:** `F:\Claude\src\skills\bundled\claudeApi.ts` (196 lines)

### Export

```typescript
export function registerClaudeApiSkill(): void
```

### Types

```typescript
type SkillContent = typeof import('./claudeApiContent.js')

type DetectedLanguage =
  | 'python'
  | 'typescript'
  | 'java'
  | 'go'
  | 'ruby'
  | 'csharp'
  | 'php'
  | 'curl'
```

### Constants

| Constant | Value | Description |
|---|---|---|
| `LANGUAGE_INDICATORS` | `Record<DetectedLanguage, string[]>` | Maps each language to its indicator files/extensions for auto-detection |
| `INLINE_READING_GUIDE` | (long string) | Quick task reference mapping common tasks to specific doc files |

The `LANGUAGE_INDICATORS` map:

```typescript
const LANGUAGE_INDICATORS: Record<DetectedLanguage, string[]> = {
  python: ['.py', 'requirements.txt', 'pyproject.toml', 'setup.py', 'Pipfile'],
  typescript: ['.ts', '.tsx', 'tsconfig.json', 'package.json'],
  java: ['.java', 'pom.xml', 'build.gradle'],
  go: ['.go', 'go.mod'],
  ruby: ['.rb', 'Gemfile'],
  csharp: ['.cs', '.csproj'],
  php: ['.php', 'composer.json'],
  curl: [],
}
```

### Internal Functions

```typescript
async function detectLanguage(): Promise<DetectedLanguage | null>
```
Scans the CWD for language indicator files/extensions. Returns the first matched language or `null`.

```typescript
function getFilesForLanguage(lang: DetectedLanguage, content: SkillContent): string[]
```
Filters `SKILL_FILES` to get only documentation files relevant to the detected language (files starting with `{lang}/` or `shared/`).

```typescript
function processContent(md: string, content: SkillContent): string
```
Processes markdown content by:
1. Stripping HTML comments (recursively until no more matches)
2. Substituting `{{VAR}}` placeholders with values from `SKILL_MODEL_VARS`

```typescript
function buildInlineReference(filePaths: string[], content: SkillContent): string
```
Builds an inline reference document by concatenating processed skill files wrapped in `<doc path="...">` tags.

```typescript
function buildPrompt(lang: DetectedLanguage | null, args: string, content: SkillContent): string
```
Assembles the full prompt:
- Base prompt from `SKILL_PROMPT` up to "Reading Guide" section
- If language detected: reading guide with `{lang}` substituted + inline reference docs for that language
- If no language detected: all docs included, asks model to ask user which language
- "When to Use WebFetch" and "Common Pitfalls" sections appended at end
- User args appended as `## User Request`

### Registration Details

```typescript
registerBundledSkill({
  name: 'claude-api',
  description: 'Build apps with the Claude API or Anthropic SDK...',
  allowedTools: ['Read', 'Grep', 'Glob', 'WebFetch'],
  userInvocable: true,
  async getPromptForCommand(args) {
    const content = await import('./claudeApiContent.js')
    const lang = await detectLanguage()
    const prompt = buildPrompt(lang, args, content)
    return [{ type: 'text', text: prompt }]
  },
})
```

**Key behaviors:**
- Triggered when code imports `anthropic`/`@anthropic-ai/sdk`/`claude_agent_sdk`
- NOT triggered for other AI SDKs or general programming tasks
- Lazy-loads 247KB of `.md` content only on invocation
- Auto-detects project language and provides targeted documentation
- Model variable substitution for keeping model IDs current

### Imports

```typescript
import { readdir } from 'fs/promises'
import { getCwd } from '../../utils/cwd.js'
import { registerBundledSkill } from '../bundledSkills.js'
```

---

## 4. `claudeApiContent.ts` — Claude API Reference Documentation Bundle

**File:** `F:\Claude\src\skills\bundled\claudeApiContent.ts` (75 lines)

### Exports

```typescript
export const SKILL_MODEL_VARS: Record<string, string>
export const SKILL_PROMPT: string
export const SKILL_FILES: Record<string, string>
```

### Constants

| Export | Type | Description |
|---|---|---|
| `SKILL_MODEL_VARS` | `Record<string, string>` | Model ID/name mappings for `{{VAR}}` substitution |
| `SKILL_PROMPT` | `string` | Raw content of `claude-api/SKILL.md` |
| `SKILL_FILES` | `Record<string, string>` | Map of 24 doc paths to their markdown content strings |

`SKILL_MODEL_VARS` values:

```typescript
export const SKILL_MODEL_VARS = {
  OPUS_ID: 'claude-opus-4-6',
  OPUS_NAME: 'Claude Opus 4.6',
  SONNET_ID: 'claude-sonnet-4-6',
  SONNET_NAME: 'Claude Sonnet 4.6',
  HAIKU_ID: 'claude-haiku-4-5',
  HAIKU_NAME: 'Claude Haiku 4.5',
  PREV_SONNET_ID: 'claude-sonnet-4-5',
} satisfies Record<string, string>
```

`SKILL_FILES` includes 24 keys covering:
- **Python**: agent-sdk (README, patterns), claude-api (README, batches, files-api, streaming, tool-use)
- **TypeScript**: agent-sdk (README, patterns), claude-api (README, batches, files-api, streaming, tool-use)
- **C#**: claude-api
- **Go**: claude-api
- **Java**: claude-api
- **PHP**: claude-api
- **Ruby**: claude-api
- **Curl**: examples
- **Shared**: error-codes, live-sources, models, prompt-caching, tool-use-concepts

### Imports

Uses Bun's text loader to import `.md` files as strings at build time (20 individual imports for each documentation file).

---

## 5. `claudeInChrome.ts` — Browser Automation Skill

**File:** `F:\Claude\src\skills\bundled\claudeInChrome.ts` (34 lines)

### Export

```typescript
export function registerClaudeInChromeSkill(): void
```

### Constants

| Constant | Type | Description |
|---|---|---|
| `CLAUDE_IN_CHROME_MCP_TOOLS` | `string[]` | Array of MCP tool names prefixed with `mcp__claude-in-chrome__` |
| `SKILL_ACTIVATION_MESSAGE` | `string` | Message injected when skill activates, instructing to call `tabs_context_mcp` |

### Registration Details

```typescript
registerBundledSkill({
  name: 'claude-in-chrome',
  description: 'Automates your Chrome browser to interact with web pages...',
  whenToUse: 'When the user wants to interact with web pages, automate browser tasks...',
  allowedTools: CLAUDE_IN_CHROME_MCP_TOOLS,
  userInvocable: true,
  isEnabled: () => shouldAutoEnableClaudeInChrome(),
  async getPromptForCommand(args) {
    let prompt = `${BASE_CHROME_PROMPT}\n${SKILL_ACTIVATION_MESSAGE}`
    if (args) { prompt += `\n## Task\n\n${args}` }
    return [{ type: 'text', text: prompt }]
  },
})
```

**Key behaviors:**
- `allowedTools` is dynamically built from `BROWSER_TOOLS` exported by `@ant/claude-for-chrome-mcp`
- `isEnabled` delegates to `shouldAutoEnableClaudeInChrome()` utility
- Activation message instructs model to always invoke skill BEFORE attempting MCP tools
- Requires site-level permissions configured in the Chrome extension

### Imports

```typescript
import { BROWSER_TOOLS } from '@ant/claude-for-chrome-mcp'
import { BASE_CHROME_PROMPT } from '../../utils/claudeInChrome/prompt.js'
import { shouldAutoEnableClaudeInChrome } from '../../utils/claudeInChrome/setup.js'
import { registerBundledSkill } from '../bundledSkills.js'
```

---

## 6. `debug.ts` — Session Debugging Skill

**File:** `F:\Claude\src\skills\bundled\debug.ts` (103 lines)

### Export

```typescript
export function registerDebugSkill(): void
```

### Constants

| Constant | Value | Description |
|---|---|---|
| `DEFAULT_DEBUG_LINES_READ` | `20` | Number of last lines to show from debug log |
| `TAIL_READ_BYTES` | `64 * 1024` (64KB) | Max bytes to read from end of debug log |

### Registration Details

```typescript
registerBundledSkill({
  name: 'debug',
  description: process.env.USER_TYPE === 'ant'
    ? 'Debug your current Claude Code session by reading the session debug log...'
    : 'Enable debug logging for this session and help diagnose issues',
  allowedTools: ['Read', 'Grep', 'Glob'],
  argumentHint: '[issue description]',
  disableModelInvocation: true,
  userInvocable: true,
  async getPromptForCommand(args) { /* ... */ },
})
```

### `getPromptForCommand` Logic

1. Calls `enableDebugLogging()` to turn on logging (non-ants don't have it on by default)
2. Reads the last 64KB of the debug log via low-level `fs/promises` `open`/`read` calls
3. Takes the last 20 lines of that tail
4. Shows log size, format, settings file paths, and instructions
5. If debug logging was just enabled, adds a notice that nothing before this invocation was captured
6. Suggests launching `CLAUDE_CODE_GUIDE_AGENT_TYPE` subagent for understanding Claude Code features

**Key behaviors:**
- `disableModelInvocation: true` — must be explicitly requested, won't auto-trigger
- Ant users get richer description (includes "all event logging")
- Tail reads are bounded to 64KB to avoid RSS spikes in long sessions
- Handles ENOENT gracefully when debug log doesn't exist yet

### Imports

```typescript
import { open, stat } from 'fs/promises'
import { CLAUDE_CODE_GUIDE_AGENT_TYPE } from 'src/tools/AgentTool/built-in/claudeCodeGuideAgent.js'
import { getSettingsFilePathForSource } from 'src/utils/settings/settings.js'
import { enableDebugLogging, getDebugLogPath } from '../../utils/debug.js'
import { errorMessage, isENOENT } from '../../utils/errors.js'
import { formatFileSize } from '../../utils/format.js'
import { registerBundledSkill } from '../bundledSkills.js'
```

---

## 7. `keybindings.ts` — Keybinding Customization Help

**File:** `F:\Claude\src\skills\bundled\keybindings.ts` (339 lines)

### Export

```typescript
export function registerKeybindingsSkill(): void
```

### Internal Functions

```typescript
function generateContextsTable(): string
```
Builds a markdown table from `KEYBINDING_CONTEXTS` and `KEYBINDING_CONTEXT_DESCRIPTIONS`.

```typescript
function generateActionsTable(): string
```
Iterates `DEFAULT_BINDINGS` to build an action-to-binding lookup, then generates a markdown table of all `KEYBINDING_ACTIONS` with their default keys and context.

```typescript
function inferContextFromAction(action: string): string
```
Infers context from the action's colon-separated prefix (e.g., `chat:externalEditor` -> `Chat`). Uses a `prefixToContext` lookup table.

```typescript
function generateReservedShortcuts(): string
```
Generates a bulleted list of:
- **Non-rebindable** keys (`NON_REBINDABLE`) — will error
- **Terminal reserved** keys (`TERMINAL_RESERVED`) — errors or warnings
- **macOS reserved** keys (`MACOS_RESERVED`) — errors

```typescript
function markdownTable(headers: string[], rows: string[][]): string
```
Utility to generate GitHub-flavored markdown tables from headers and row data.

### Constants (Configuration Objects)

| Constant | Type | Description |
|---|---|---|
| `FILE_FORMAT_EXAMPLE` | `KeybindingsSchemaType` | Complete file format example with `$schema`, `$docs`, and sample binding |
| `UNBIND_EXAMPLE` | `KeybindingsSchemaType['bindings'][number]` | Example of unbinding `ctrl+s` by setting to `null` |
| `REBIND_EXAMPLE` | `KeybindingsSchemaType['bindings'][number]` | Example of rebinding external editor from `ctrl+g` to `ctrl+e` |
| `CHORD_EXAMPLE` | `KeybindingsSchemaType['bindings'][number]` | Example of chord binding `ctrl+k ctrl+t` |

### Prompt Sections (Constants)

| Constant | Content |
|---|---|
| `SECTION_INTRO` | Intro, critical read-before-write rule |
| `SECTION_FILE_FORMAT` | JSON schema for keybindings file |
| `SECTION_KEYSTROKE_SYNTAX` | Modifiers, special keys, chord syntax |
| `SECTION_UNBINDING` | How to unbind defaults |
| `SECTION_INTERACTION` | How user bindings interact with defaults |
| `SECTION_COMMON_PATTERNS` | Rebind and chord examples |
| `SECTION_BEHAVIORAL_RULES` | 5 rules for minimal overrides, validation, warnings |
| `SECTION_DOCTOR` | Validation with `/doctor` command, common issues table |

### Registration Details

```typescript
registerBundledSkill({
  name: 'keybindings-help',
  description: 'Use when the user wants to customize keyboard shortcuts...',
  allowedTools: ['Read'],
  userInvocable: false,
  isEnabled: isKeybindingCustomizationEnabled,
  async getPromptForCommand(args) {
    // Dynamically generates: contexts table, actions table, reserved shortcuts
    // Assembles all sections into a single prompt
  },
})
```

**Key behaviors:**
- `userInvocable: false` — only the model can invoke it
- `isEnabled` delegates to `isKeybindingCustomizationEnabled` from settings
- All reference tables (contexts, actions, reserved shortcuts) are generated dynamically from source-of-truth arrays
- Emphasizes reading before writing, merging with existing bindings
- Includes `/doctor` validation integration with common issues and fixes

### Imports

```typescript
import { DEFAULT_BINDINGS } from '../../keybindings/defaultBindings.js'
import { isKeybindingCustomizationEnabled } from '../../keybindings/loadUserBindings.js'
import { MACOS_RESERVED, NON_REBINDABLE, TERMINAL_RESERVED } from '../../keybindings/reservedShortcuts.js'
import type { KeybindingsSchemaType } from '../../keybindings/schema.js'
import { KEYBINDING_ACTIONS, KEYBINDING_CONTEXT_DESCRIPTIONS, KEYBINDING_CONTEXTS } from '../../keybindings/schema.js'
import { jsonStringify } from '../../utils/slowOperations.js'
import { registerBundledSkill } from '../bundledSkills.js'
```

---

## 8. `loop.ts` — Recurring Prompt Scheduling

**File:** `F:\Claude\src\skills\bundled\loop.ts` (92 lines)

### Export

```typescript
export function registerLoopSkill(): void
```

### Constants

| Constant | Value | Description |
|---|---|---|
| `DEFAULT_INTERVAL` | `'10m'` | Default interval when none specified |
| `USAGE_MESSAGE` | (string) | Help/usage text showing interval syntax and examples |

### Internal Functions

```typescript
function buildPrompt(args: string): string
```
Builds a prompt instructing the model to parse intervals with three priority rules:
1. **Leading token**: If the first token matches `^\d+[smhd]$`, it's the interval
2. **Trailing "every" clause**: `every 20m`, `every 5 minutes` patterns extracted
3. **Default**: interval is `10m`, entire input is the prompt

Includes interval-to-cron conversion table:
| Interval Pattern | Cron Expression | Note |
|---|---|---|
| `Nm` where N ≤ 59 | `*/N * * * *` | every N minutes |
| `Nm` where N ≥ 60 | `0 */H * * *` | round to hours |
| `Nh` where N ≤ 23 | `0 */N * * *` | every N hours |
| `Nd` | `0 0 */N * *` | every N days at midnight |
| `Ns` | `ceil(N/60)m` | cron minimum granularity is 1 minute |

### Registration Details

```typescript
registerBundledSkill({
  name: 'loop',
  description: 'Run a prompt or slash command on a recurring interval...',
  whenToUse: 'When the user wants to set up a recurring task, poll for status...',
  argumentHint: '[interval] <prompt>',
  userInvocable: true,
  isEnabled: isKairosCronEnabled,
  async getPromptForCommand(args) { /* validates, builds prompt */ },
})
```

**Key behaviors:**
- `isEnabled` delegates to `isKairosCronEnabled()` — lazy per-invocation check
- After creating the cron job, instructs the model to immediately execute the prompt (not wait for cron)
- Auto-expiry after `DEFAULT_MAX_AGE_DAYS` days
- Handles edge cases like `check every PR` where "every" is not a time expression

### Imports

```typescript
import { CRON_CREATE_TOOL_NAME, CRON_DELETE_TOOL_NAME, DEFAULT_MAX_AGE_DAYS, isKairosCronEnabled } from '../../tools/ScheduleCronTool/prompt.js'
import { registerBundledSkill } from '../bundledSkills.js'
```

---

## 9. `loremIpsum.ts` — Placeholder Text Generation

**File:** `F:\Claude\src\skills\bundled\loremIpsum.ts` (282 lines)

### Export

```typescript
export function registerLoremIpsumSkill(): void
```

### Constants

| Constant | Type | Description |
|---|---|---|
| `ONE_TOKEN_WORDS` | `string[]` | 201 common English words verified to tokenize as single tokens |

### Internal Functions

```typescript
function generateLoremIpsum(targetTokens: number): string
```
Generates approximately `targetTokens` tokens of pseudo-random English text by:
1. Building sentences of 10-20 random words from `ONE_TOKEN_WORDS`
2. Ending each sentence with `. ` 
3. Adding paragraph breaks (`\n\n`) with ~20% probability after sentences
4. Stopping when target token count is reached

### Registration Details

```typescript
registerBundledSkill({
  name: 'lorem-ipsum',
  description: 'Generate filler text for long context testing... Ant-only.',
  argumentHint: '[token_count]',
  userInvocable: true,
  async getPromptForCommand(args) { /* parses count, generates text */ },
})
```

**Key behaviors:**
- Only registers if `process.env.USER_TYPE === 'ant'` (returns early otherwise)
- Defaults to 10,000 tokens if no argument
- Capped at 500,000 tokens for safety
- Validates positive integer input
- Returns raw lorem ipsum text — the model just dumps it into the conversation

### Imports

```typescript
import { registerBundledSkill } from '../bundledSkills.js'
```

---

## 10. `remember.ts` — Memory Review/Organization

**File:** `F:\Claude\src\skills\bundled\remember.ts` (82 lines)

### Export

```typescript
export function registerRememberSkill(): void
```

### Registration Details

```typescript
registerBundledSkill({
  name: 'remember',
  description: 'Review auto-memory entries and propose promotions to CLAUDE.md, CLAUDE.local.md, or shared memory...',
  whenToUse: 'Use when the user wants to review, organize, or promote their auto-memory entries...',
  userInvocable: true,
  isEnabled: () => isAutoMemoryEnabled(),
  async getPromptForCommand(args) { /* appends user context to skill prompt */ },
})
```

### Skill Prompt Structure (`SKILL_PROMPT`)

The skill prompt is a local constant within `registerRememberSkill` that defines a 4-step process:

1. **Gather all memory layers** — Read CLAUDE.md, CLAUDE.local.md, and review auto-memory content from system prompt
2. **Classify each auto-memory entry** — Determine best destination:
   - **CLAUDE.md**: Project conventions all contributors should follow
   - **CLAUDE.local.md**: Personal instructions for this user
   - **Team memory**: Org-wide cross-repo knowledge
   - **Stay in auto-memory**: Working notes, temporary context
3. **Identify cleanup opportunities** — Duplicates, outdated entries, conflicts across layers
4. **Present the report** — Grouped by action type: Promotions, Cleanup, Ambiguous, No action needed

**Key behaviors:**
- Only registers if `process.env.USER_TYPE === 'ant'` (returns early otherwise)
- `isEnabled` delegates to `isAutoMemoryEnabled()`
- Emphasizes presenting ALL proposals before making any changes
- Explicitly forbids: modifying files without approval, creating files unnecessarily, guessing on ambiguous entries

### Imports

```typescript
import { isAutoMemoryEnabled } from '../../memdir/paths.js'
import { registerBundledSkill } from '../bundledSkills.js'
```

---

## 11. `scheduleRemoteAgents.ts` — Remote Agent Scheduling

**File:** `F:\Claude\src\skills\bundled\scheduleRemoteAgents.ts` (447 lines)

### Export

```typescript
export function registerScheduleRemoteAgentsSkill(): void
```

### Types

```typescript
type ConnectorInfo = {
  uuid: string
  name: string
  url: string
}
```

### Constants

| Constant | Value | Description |
|---|---|---|
| `BASE58` | `'123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz'` | Base58 alphabet for tagged ID decoding |
| `BASE_QUESTION` | `'What would you like to do with scheduled remote agents?'` | Default question for AskUserQuestion dialog |

### Internal Functions

```typescript
function taggedIdToUUID(taggedId: string): string | null
```
Decodes an `mcpsrv_` tagged ID to a standard UUID string using Base58 decoding. Format: `mcpsrv_01{base58(uuid.int)}`.

```typescript
function getConnectedClaudeAIConnectors(mcpClients: MCPServerConnection[]): ConnectorInfo[]
```
Filters MCP clients to find connected `claudeai-proxy` type connectors, decodes their tagged IDs, and returns `ConnectorInfo` objects.

```typescript
function sanitizeConnectorName(name: string): string
```
Sanitizes a connector name: strips "claude.ai" prefix, replaces non-alphanumeric chars with hyphens, collapses consecutive hyphens, trims leading/trailing hyphens.

```typescript
function formatConnectorsInfo(connectors: ConnectorInfo[]): string
```
Formats connector info as a bulleted list with `uuid`, sanitized `name`, and `url`.

```typescript
function formatSetupNotes(notes: string[]): string
```
Formats setup notes as a "Heads-up" bulleted block with a warning prefix.

```typescript
async function getCurrentRepoHttpsUrl(): Promise<string | null>
```
Gets the current repo's HTTPS URL by parsing the git remote URL.

```typescript
function buildPrompt(opts: { ... }): string
```
Assembles the full prompt with all runtime context (timezone, connectors, git repo, environments, setup notes, etc.).

### `buildPrompt` Options

```typescript
{
  userTimezone: string
  connectorsInfo: string
  gitRepoUrl: string | null
  environmentsInfo: string
  createdEnvironment: EnvironmentResource | null
  setupNotes: string[]
  needsGitHubAccessReminder: boolean
  userArgs: string
}
```

### Registration Details

```typescript
registerBundledSkill({
  name: 'schedule',
  description: 'Create, update, list, or run scheduled remote agents (triggers) that execute on a cron schedule.',
  whenToUse: 'When the user wants to schedule a recurring remote agent, set up automated tasks...',
  userInvocable: true,
  isEnabled: () =>
    getFeatureValue_CACHED_MAY_BE_STALE('tengu_surreal_dali', false) &&
    isPolicyAllowed('allow_remote_sessions'),
  allowedTools: [REMOTE_TRIGGER_TOOL_NAME, ASK_USER_QUESTION_TOOL_NAME],
  async getPromptForCommand(args, context) { /* comprehensive setup */ },
})
```

### `getPromptForCommand` Logic (Steps in order)

1. Validates claude.ai authentication (access token required; API accounts not supported)
2. Fetches remote environments, creates default environment if none exist
3. Runs soft setup checks (never blocking):
   - Git repo detection and GitHub access verification
   - MCP connector availability
4. Collects runtime context: timezone, connectors, git repo URL, environments
5. Builds and returns the comprehensive prompt

**Key behaviors:**
- `isEnabled` requires both feature flag `tengu_surreal_dali` AND policy `allow_remote_sessions`
- Creates default cloud environment automatically if user has none
- Minimum cron interval is 1 hour
- Always converts user's local timezone to UTC with confirmation
- Detects needed MCP connectors from user's described task
- GitHub access reminders vary based on feature flag `tengu_cobalt_lantern`

### Imports

```typescript
import { getFeatureValue_CACHED_MAY_BE_STALE } from '../../services/analytics/growthbook.js'
import type { MCPServerConnection } from '../../services/mcp/types.js'
import { isPolicyAllowed } from '../../services/policyLimits/index.js'
import type { ToolUseContext } from '../../Tool.js'
import { ASK_USER_QUESTION_TOOL_NAME } from '../../tools/AskUserQuestionTool/prompt.js'
import { REMOTE_TRIGGER_TOOL_NAME } from '../../tools/RemoteTriggerTool/prompt.js'
import { getClaudeAIOAuthTokens } from '../../utils/auth.js'
import { checkRepoForRemoteAccess } from '../../utils/background/remote/preconditions.js'
import { logForDebugging } from '../../utils/debug.js'
import { detectCurrentRepositoryWithHost, parseGitRemote } from '../../utils/detectRepository.js'
import { getRemoteUrl } from '../../utils/git.js'
import { jsonStringify } from '../../utils/slowOperations.js'
import { createDefaultCloudEnvironment, type EnvironmentResource, fetchEnvironments } from '../../utils/teleport/environments.js'
import { registerBundledSkill } from '../bundledSkills.js'
```

---

## 12. `simplify.ts` — Code Review and Cleanup

**File:** `F:\Claude\src\skills\bundled\simplify.ts` (69 lines)

### Export

```typescript
export function registerSimplifySkill(): void
```

### Constants

| Constant | Value | Description |
|---|---|---|
| `SIMPLIFY_PROMPT` | (long string) | 3-phase code review workflow |

### Skill Prompt Structure (`SIMPLIFY_PROMPT`)

**Phase 1: Identify Changes** — Run `git diff` (or `git diff HEAD` for staged) to find changed files.

**Phase 2: Launch Three Review Agents in Parallel** (via `AGENT_TOOL_NAME`):

| Agent | Focus Areas |
|---|---|
| Agent 1: Code Reuse | Duplicate functions, inline logic that could use existing utilities, hand-rolled patterns |
| Agent 2: Code Quality | Redundant state, parameter sprawl, copy-paste variations, leaky abstractions, stringly-typed code, unnecessary JSX nesting, unnecessary comments |
| Agent 3: Efficiency | Unnecessary work, missed concurrency, hot-path bloat, recurring no-op updates, TOCTOU patterns, memory leaks, overly broad operations |

**Phase 3: Fix Issues** — Aggregate findings, fix directly, skip false positives without arguing, summarize what was fixed.

### Registration Details

```typescript
registerBundledSkill({
  name: 'simplify',
  description: 'Review changed code for reuse, quality, and efficiency, then fix any issues found.',
  userInvocable: true,
  async getPromptForCommand(args) { /* appends additional focus to prompt */ },
})
```

### Imports

```typescript
import { AGENT_TOOL_NAME } from '../../tools/AgentTool/constants.js'
import { registerBundledSkill } from '../bundledSkills.js'
```

---

## 13. `skillify.ts` — Skill Creation Meta-Skill

**File:** `F:\Claude\src\skills\bundled\skillify.ts` (197 lines)

### Export

```typescript
export function registerSkillifySkill(): void
```

### Internal Functions

```typescript
function extractUserMessages(messages: Message[]): string[]
```
Filters messages to user type, extracts text content from string or structured content blocks, filters out empty messages.

### Constants

| Constant | Value | Description |
|---|---|---|
| `SKILLIFY_PROMPT` | (long string) | 4-step skill creation workflow with template placeholders |

### Skill Prompt Structure (`SKILLIFY_PROMPT`)

The prompt uses `{{sessionMemory}}`, `{{userMessages}}`, and `{{userDescriptionBlock}}` placeholders replaced at runtime.

**Step 1: Analyze the Session** — Identify repeatable process, inputs, steps, success criteria, corrections/steering, tools needed.

**Step 2: Interview the User** — Four rounds of `AskUserQuestion`:

| Round | Questions |
|---|---|
| Round 1 | Name, description, high-level goals, success criteria |
| Round 2 | Step list, arguments, inline vs fork execution, save location (repo vs personal) |
| Round 3 | Per-step breakdown: artifacts, success criteria, human checkpoints, parallel steps, execution mode, constraints |
| Round 4 | When to invoke, trigger phrases, gotchas |

**Step 3: Write the SKILL.md** — Template with frontmatter fields:
- `name`, `description`, `allowed-tools`, `when_to_use`, `argument-hint`, `arguments`, `context`
- Steps with per-step annotations: `Execution`, `Artifacts`, `Human checkpoint`, `Rules`
- Step structure tips: concurrent sub-numbering, human steps, simplicity

**Step 4: Confirm and Save** — Output SKILL.md for review, ask confirmation, then write and tell user how to invoke.

### Registration Details

```typescript
registerBundledSkill({
  name: 'skillify',
  description: "Capture this session's repeatable process into a skill...",
  allowedTools: ['Read', 'Write', 'Edit', 'Glob', 'Grep', 'AskUserQuestion', 'Bash(mkdir:*)'],
  userInvocable: true,
  disableModelInvocation: true,
  argumentHint: '[description of the process you want to capture]',
  async getPromptForCommand(args, context) { /* substitutes context into template */ },
})
```

**Key behaviors:**
- Only registers if `process.env.USER_TYPE === 'ant'` (returns early otherwise)
- `disableModelInvocation: true` — must be explicitly invoked
- Injects session memory AND user messages into the prompt for context
- Uses `getMessagesAfterCompactBoundary` to only consider messages from current compact window

### Imports

```typescript
import { getSessionMemoryContent } from '../../services/SessionMemory/sessionMemoryUtils.js'
import type { Message } from '../../types/message.js'
import { getMessagesAfterCompactBoundary } from '../../utils/messages.js'
import { registerBundledSkill } from '../bundledSkills.js'
```

---

## 14. `stuck.ts` — Diagnose Frozen Sessions

**File:** `F:\Claude\src\skills\bundled\stuck.ts` (79 lines)

### Export

```typescript
export function registerStuckSkill(): void
```

### Constants

| Constant | Value | Description |
|---|---|---|
| `STUCK_PROMPT` | (long string) | Diagnostic workflow for frozen Claude Code sessions |

### Skill Prompt Structure (`STUCK_PROMPT`)

**What to look for:**
| Symptom | Description |
|---|---|
| High CPU (>=90%) sustained | Likely infinite loop — sample twice 1-2s apart |
| Process state `D` | Uninterruptible sleep — often I/O hang |
| Process state `T` | Stopped — user probably hit Ctrl+Z |
| Process state `Z` | Zombie — parent isn't reaping |
| Very high RSS (>=4GB) | Possible memory leak |
| Stuck child process | Hung git/node/shell subprocess |

**Investigation steps:**
1. List all Claude Code processes via `ps` (filtered to `claude` or `cli` processes)
2. For suspicious processes: child processes, re-sample CPU, check debug log
3. Optional: stack dump via `sample <pid> 3` on macOS

**Report format:** Two-message Slack structure to `#claude-code-feedback`:
1. Top-level: one-line hostname, version, symptom
2. Thread reply: full diagnostic dump

### Registration Details

```typescript
registerBundledSkill({
  name: 'stuck',
  description: '[ANT-ONLY] Investigate frozen/stuck/slow Claude Code sessions on this machine...',
  userInvocable: true,
  async getPromptForCommand(args) { /* appends user context to prompt */ },
})
```

**Key behaviors:**
- Only registers if `process.env.USER_TYPE === 'ant'` (returns early otherwise)
- Diagnostic-only — explicitly forbids killing processes
- Only posts to Slack if something is actually stuck (no "all-clear" messages)
- Falls back to copy-pasteable report format if Slack MCP unavailable

### Imports

```typescript
import { registerBundledSkill } from '../bundledSkills.js'
```

---

## 15. `updateConfig.ts` — Configuration Updates

**File:** `F:\Claude\src\skills\bundled\updateConfig.ts` (475 lines)

### Export

```typescript
export function registerUpdateConfigSkill(): void
```

### Internal Functions

```typescript
function generateSettingsSchema(): string
```
Generates JSON Schema from the Zod `SettingsSchema` using `toJSONSchema()`, serialized with `jsonStringify()`.

### Constants (Content Sections)

| Constant | Content |
|---|---|
| `SETTINGS_EXAMPLES_DOCS` | File locations table, permissions, env vars, model/agent, attribution, MCP servers, plugins, other settings |
| `HOOKS_DOCS` | Hook structure, event types, hook types (command/prompt/agent), input/output JSON schemas, common patterns |
| `HOOK_VERIFICATION_FLOW` | 7-step construction workflow: dedup, construct, pipe-test, write, validate, prove, handoff |
| `UPDATE_CONFIG_PROMPT` | Full skill prompt: when hooks vs memory, read-before-write, AskUserQuestion for ambiguity, Config tool vs direct edit, merging arrays, troubleshooting |
| `FILE_FORMAT_EXAMPLE` | (see keybindings) Example of complete file format |
| `UNBIND_EXAMPLE` | (see keybindings) Example of unbinding |
| `REBIND_EXAMPLE` | (see keybindings) Example of rebinding |
| `CHORD_EXAMPLE` | (see keybindings) Example of chord binding |

### Registration Details

```typescript
registerBundledSkill({
  name: 'update-config',
  description: 'Use this skill to configure the Claude Code harness via settings.json...',
  allowedTools: ['Read'],
  userInvocable: true,
  async getPromptForCommand(args) {
    // Special [hooks-only] prefix for hook-specific prompts
    // Otherwise includes full settings JSON schema
  },
})
```

### `getPromptForCommand` Logic

1. If args start with `[hooks-only]`: returns only `HOOKS_DOCS` + `HOOK_VERIFICATION_FLOW` + optional task
2. Otherwise: returns `UPDATE_CONFIG_PROMPT` + dynamically generated full settings JSON schema + user args

**Key behaviors:**
- Emphasizes hooks vs memory distinction: "before/after X" requires hooks, NOT memory/preferences
- CRITICAL rule: always read before write, merge with existing settings
- Specific guidance for the `[hooks-only]` prefix for hook-specific prompts
- Dynamically generates JSON schema from actual Zod types to stay in sync
- Includes hook verification flow: pipe-test, validate with `jq -e`, prove the hook fires, handoff

### Imports

```typescript
import { toJSONSchema } from 'zod/v4'
import { SettingsSchema } from '../../utils/settings/types.js'
import { jsonStringify } from '../../utils/slowOperations.js'
import { registerBundledSkill } from '../bundledSkills.js'
```

---

## 16. `verify.ts` — Code Change Verification

**File:** `F:\Claude\src\skills\bundled\verify.ts` (30 lines)

### Export

```typescript
export function registerVerifySkill(): void
```

### Constants

| Constant | Type | Description |
|---|---|---|
| `SKILL_BODY` | `string` | Body of SKILL.md after frontmatter parsing |
| `DESCRIPTION` | `string` | Frontmatter `description` field or fallback |

### Registration Details

```typescript
registerBundledSkill({
  name: 'verify',
  description: DESCRIPTION,
  userInvocable: true,
  files: SKILL_FILES,
  async getPromptForCommand(args) {
    // Returns skill body + optional user request
  },
})
```

**Key behaviors:**
- Only registers if `process.env.USER_TYPE === 'ant'` (returns early otherwise)
- Uses the `files` mechanism to include reference files (`examples/cli.md`, `examples/server.md`) extracted to disk
- Description is parsed from SKILL.md frontmatter directly (dynamic)
- Minimal prompt generation — skill body drives the behavior

### Imports

```typescript
import { parseFrontmatter } from '../../utils/frontmatterParser.js'
import { registerBundledSkill } from '../bundledSkills.js'
import { SKILL_FILES, SKILL_MD } from './verifyContent.js'
```

---

## 17. `verifyContent.ts` — Verify Skill Content Bundle

**File:** `F:\Claude\src\skills\bundled\verifyContent.ts` (13 lines)

### Exports

```typescript
export const SKILL_MD: string
export const SKILL_FILES: Record<string, string>
```

### Constants

| Export | Type | Description |
|---|---|---|
| `SKILL_MD` | `string` | Raw content of `verify/SKILL.md` |
| `SKILL_FILES` | `Record<string, string>` | Maps 2 doc paths to markdown: `examples/cli.md`, `examples/server.md` |

### Imports

Uses Bun's text loader to import `.md` files as strings at build time (3 imports).

---

## Cross-Cutting Patterns

### Ant-Only Skills

The following skills only register when `process.env.USER_TYPE === 'ant'`:
- `loremIpsum.ts` — Placeholder text generation
- `remember.ts` — Memory review
- `skillify.ts` — Skill creation meta-skill
- `stuck.ts` — Diagnose stuck sessions
- `verify.ts` — Code change verification

These return early from their `register*Skill()` functions if the condition is not met.

### Feature-Gated Skills

Skills gated behind `feature()` flags from `bun:bundle`:

| Skill | Feature Flag(s) | Registration Condition |
|---|---|---|
| `dream.js` | `KAIROS \|\| KAIROS_DREAM` | Dream/reflection feature |
| `hunter.js` | `REVIEW_ARTIFACT` | Review artifact feature |
| `loop.ts` | `AGENT_TRIGGERS` | Recurring prompts |
| `scheduleRemoteAgents.ts` | `AGENT_TRIGGERS_REMOTE` + `isPolicyAllowed('allow_remote_sessions')` | Remote agent scheduling |
| `claudeApi.ts` | `BUILDING_CLAUDE_APPS` | Claude API development guide |
| `runSkillGenerator.js` | `RUN_SKILL_GENERATOR` | Run external skill generator |

### Files Mechanism

Two skills use the `files` property to include reference documentation:
- `claudeApi.ts`: includes 24 markdown files bundled in `claudeApiContent.ts` (not passed via `files` — content is inlined in the prompt)
- `verify.ts`: includes `examples/cli.md` and `examples/server.md` via `verifyContent.ts`

When `files` is set, `registerBundledSkill` lazily extracts them to disk on first invocation and prepends a `Base directory for this skill: <dir>` line to the prompt.

### Lazy Loading

Several skills use lazy loading to minimize startup cost:
- `claudeApi.ts`: Lazily imports `claudeApiContent.js` (247KB) inside `getPromptForCommand`
- Feature-gated skills: Imported via `require()` inside `if (feature(...))` blocks to avoid loading unused modules

### `disableModelInvocation`

Skills with `disableModelInvocation: true`:
- `batch.ts` — Must be explicitly invoked by the user
- `debug.ts` — Must be explicitly invoked (keeps description out of context)
- `skillify.ts` — Must be explicitly invoked

### `allowedTools` Patterns

| Tools Pattern | Skills Using It |
|---|---|
| `['Read', 'Grep', 'Glob']` | `claudeApi.ts`, `debug.ts` |
| `['Read']` | `keybindings.ts`, `updateConfig.ts` |
| `['Read', 'Write', 'Edit', 'Glob', 'Grep', 'AskUserQuestion', 'Bash(mkdir:*)']` | `skillify.ts` |
| `[REMOTE_TRIGGER_TOOL_NAME, ASK_USER_QUESTION_TOOL_NAME]` | `scheduleRemoteAgents.ts` |
| MCP tool names (dynamic) | `claudeInChrome.ts` |

### `isEnabled` Delegation

| Skill | `isEnabled` Delegate |
|---|---|
| `claudeInChrome.ts` | `shouldAutoEnableClaudeInChrome()` |
| `keybindings.ts` | `isKeybindingCustomizationEnabled` |
| `loop.ts` | `isKairosCronEnabled` |
| `remember.ts` | `isAutoMemoryEnabled()` |
| `scheduleRemoteAgents.ts` | `getFeatureValue_CACHED_MAY_BE_STALE('tengu_surreal_dali', false) && isPolicyAllowed('allow_remote_sessions')` |
