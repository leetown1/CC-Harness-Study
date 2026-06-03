# 04 — Memory System

## Overview

The memory system provides persistent, file-based memory across conversations using a four-type taxonomy (user/feedback/project/reference). Memories are stored as `.md` files with YAML frontmatter under `~/.claude/projects/<slug>/memory/`. The system supports three modes: individual (auto-only), combined (auto+team), and assistant daily-log (KAIROS feature gate).

---

## 1. `memdir/memdir.ts` (507 lines) — Central Memory Module

### Purpose

Core orchestrator for all memory prompt construction. Dispatches between auto-only, auto+team, and assistant daily-log modes. Manages MEMORY.md truncation, directory creation, and memory prompt caching.

### Key Exports

| Export | Type | Description |
|--------|------|-------------|
| `ENTRYPOINT_NAME` | `'MEMORY.md'` | Index filename constant |
| `MAX_ENTRYPOINT_LINES` | `200` | Line cap for MEMORY.md |
| `MAX_ENTRYPOINT_BYTES` | `25000` | Byte cap for MEMORY.md (~125 chars/line) |
| `EntrypointTruncation` | `type` | `{ content, lineCount, byteCount, wasLineTruncated, wasByteTruncated }` |
| `DIR_EXISTS_GUIDANCE` | `string` | "This directory already exists — write to it directly..." |
| `DIRS_EXIST_GUIDANCE` | `string` | Plural variant for combined mode |

### Key Functions

#### `truncateEntrypointContent(raw: string): EntrypointTruncation`
Truncates MEMORY.md content to both line AND byte caps. Line-truncates first (natural boundary), then byte-truncates at the last newline before the cap so mid-line cuts are avoided. Appends a truncation warning naming which cap fired. The warning includes explicit guidance: "Keep index entries to one line under ~200 chars; move detail into topic files."

#### `ensureMemoryDirExists(memoryDir: string): Promise<void>`
Idempotent directory creation. Called once per session via `loadMemoryPrompt`. Uses `FsOperations.mkdir` which is recursive and swallows EEXIST internally. Failures (EACCES/EPERM/EROFS) are debug-logged but never block prompt construction — the model's Write tool will surface the real permission error.

#### `buildMemoryLines(displayName, memoryDir, extraGuidelines?, skipIndex?): string[]`
Builds the typed-memory behavioral instructions WITHOUT MEMORY.md content. Used by both `buildMemoryPrompt` (agent memory) and `loadMemoryPrompt` (system prompt). Returns an array of lines including:
- `## How to save memories` (two-step: write file + add pointer to MEMORY.md, or skipIndex variant)
- `## Types of memory` (from `TYPES_SECTION_INDIVIDUAL`)
- `## What NOT to save in memory`
- `## When to access memories`
- `## Before recommending from memory` (TRUSTING_RECALL_SECTION)
- `## Memory and other forms of persistence` (plan vs task vs memory distinction)
- `## Searching past context` (gated on `tengu_coral_fern` feature flag)

#### `buildMemoryPrompt(params): string`
Full memory prompt INCLUDING MEMORY.md content. Reads the entrypoint file synchronously (prompt building is synchronous), truncates it, logs telemetry (`tengu_memdir_loaded`), and appends it to the instruction lines. Used by agent memory.

#### `buildAssistantDailyLogPrompt(skipIndex): string`
Assistant-mode daily-log prompt (KAIROS feature gate). In assistant sessions, the agent writes append-only to a date-named log file (`{memoryDir}/logs/YYYY/MM/YYYY-MM-DD.md`) rather than maintaining MEMORY.md as a live index. A separate nightly `/dream` skill distills logs into topic files + MEMORY.md. The prompt describes the log path as a pattern so it remains cacheable across date changes.

#### `loadMemoryPrompt(): Promise<string | null>`
Top-level dispatcher for the unified memory prompt. Resolution order:
1. KAIROS daily-log mode (assistant sessions) — if `feature('KAIROS')` AND `autoEnabled` AND `kairosActive`
2. Team memory mode (combined auto+team) — if `feature('TEAMMEM')` AND `isTeamMemoryEnabled()`
3. Auto-only mode — if `isAutoMemoryEnabled()`
4. Disabled — returns null, logs `tengu_memdir_disabled` telemetry

Cowork mode injects extra guidelines via `CLAUDE_COWORK_MEMORY_EXTRA_GUIDELINES` env var.

#### `buildSearchingPastContextSection(autoMemDir): string[]`
Builds grep/search instructions for the memory directory. Adapts to whether embedded search tools are available (Ant-native builds alias grep to embedded ugrep, REPL mode hides both Grep and Bash from direct use). Includes instructions for both memory directory search and transcript log search.

#### `logMemoryDirCounts(memoryDir, baseMetadata): void`
Fire-and-forget async telemetry. Reads the memory directory, counts files and subdirectories, logs `tengu_memdir_loaded` event. Falls back to logging without counts on read failure.

### Feature Gates
- `TEAMMEM` — team memory (imports `teamMemPaths` and `teamMemPrompts` lazily via `bun:bundle` feature)
- `KAIROS` — assistant daily-log mode
- `tengu_coral_fern` — "Searching past context" section
- `tengu_moth_copse` — skip MEMORY.md index instructions

---

## 2. `memdir/findRelevantMemories.ts` (141 lines) — Relevance Selector

### Purpose

At query time, scans available memory files and uses a Sonnet side-query to select the top 5 most relevant ones. This is a semantic pre-filter — the main model's context budget is limited, so we inject only memories that Sonnet deems clearly useful.

### Key Types

```typescript
type RelevantMemory = { path: string; mtimeMs: number }
```

### Key Functions

#### `findRelevantMemories(query, memoryDir, signal, recentTools?, alreadySurfaced?): Promise<RelevantMemory[]>`
Main entry point. Pipeline:
1. `scanMemoryFiles(memoryDir, signal)` — get all .md file headers (excluding MEMORY.md)
2. Filter out `alreadySurfaced` paths (shown in prior turns)
3. If no candidates remain, return `[]`
4. `selectRelevantMemories(query, memories, signal, recentTools)` — Sonnet side-query
5. Map selected filenames back to full `RelevantMemory` objects (path + mtimeMs)
6. Log telemetry via `logMemoryRecallShape` if `MEMORY_SHAPE_TELEMETRY` feature is enabled

#### `selectRelevantMemories(query, memories, signal, recentTools): Promise<string[]>`
Sonnet side-query implementation:
- System prompt: `SELECT_MEMORIES_SYSTEM_PROMPT` — instructs Sonnet to be selective, ignore tool reference docs, but keep warnings/gotchas about recently-used tools
- User message: `Query: {query}\n\nAvailable memories:\n{manifest}{toolsSection}`
- Output format: `json_schema` with `{ selected_memories: string[] }`
- `max_tokens: 256`
- Validates results: filters out filenames not in the original scan (hallucination guard)
- Returns `[]` on any failure (aborted, parse error, API error)

### Design Decisions
- Excludes `MEMORY.md` from the scan (already loaded in system prompt)
- `alreadySurfaced` set prevents re-picking files the caller already showed and will discard, maximizing the 5-slot budget on fresh candidates
- `recentTools` list suppresses tool reference docs for tools the model is already exercising (keyword overlap false positives), but preserves warnings/gotchas about those tools
- mtime is threaded through so callers can surface freshness to the main model without a second `stat()` call

---

## 3. `memdir/memoryScan.ts` (94 lines) — File Scanning

### Purpose

Scans the memory directory for `.md` files, reads frontmatter (description + type), and returns a sorted `MemoryHeader` list. Split from `findRelevantMemories.ts` to avoid pulling `sideQuery` and API-client chain into `extractMemories.ts`.

### Key Types

```typescript
type MemoryHeader = {
  filename: string      // relative path from memoryDir
  filePath: string       // absolute path
  mtimeMs: number        // modification timestamp
  description: string | null  // from frontmatter
  type: MemoryType | undefined // from frontmatter
}
```

### Key Functions

#### `scanMemoryFiles(memoryDir, signal): Promise<MemoryHeader[]>`
Single-pass scan-with-read:
1. `readdir(memoryDir, { recursive: true })` — get all entries
2. Filter to `.md` files excluding `MEMORY.md`
3. `Promise.allSettled` over `readFileInRange(filePath, 0, FRONTMATTER_MAX_LINES=30, ...)` — reads only the first 30 lines to get frontmatter
4. `parseFrontmatter(content)` — extracts description and type
5. Filter fulfilled promises, sort by `mtimeMs` descending (newest first)
6. Cap at `MAX_MEMORY_FILES=200`

#### `formatMemoryManifest(memories): string`
Formats memory headers as a text manifest: `- [type] filename (timestamp): description`. Used by both the recall selector prompt and the extraction-agent prompt.

### Design Decisions
- Single-pass: `readFileInRange` stats internally and returns `mtimeMs`, so we read-then-sort rather than stat-sort-read. This halves syscalls vs a separate stat round for the common case (N ≤ 200).
- Uses `Promise.allSettled` so a single corrupt/broken file doesn't abort the entire scan.
- `MAX_MEMORY_FILES=200` cap prevents degenerate cases with thousands of files.

---

## 4. `memdir/memoryAge.ts` (53 lines) — Human-Readable Age

### Purpose

Converts mtime timestamps into human-readable age strings and staleness warnings. The model is poor at date arithmetic — "47 days ago" triggers staleness reasoning where a raw ISO timestamp does not.

### Key Functions

#### `memoryAgeDays(mtimeMs): number`
Days elapsed since mtime. Floor-rounded: 0 for today, 1 for yesterday, 2+ for older. Negative inputs (future mtime, clock skew) clamp to 0.

#### `memoryAge(mtimeMs): string`
Human-readable: `"today"`, `"yesterday"`, or `"47 days ago"`.

#### `memoryFreshnessText(mtimeMs): string`
Staleness caveat text for memories >1 day old. Returns empty string for fresh (today/yesterday) memories. Message: "This memory is N days old. Memories are point-in-time observations, not live state — claims about code behavior or file:line citations may be outdated. Verify against current code before asserting as fact."

#### `memoryFreshnessNote(mtimeMs): string`
Same as `memoryFreshnessText` but wrapped in `<system-reminder>` tags. Used by callers that don't add their own system-reminder wrapper (e.g., FileReadTool output).

---

## 5. `memdir/memoryTypes.ts` (271 lines) — Type Taxonomy

### Purpose

Defines the four memory types and provides prompt section text for combined vs individual modes. Sections are intentionally duplicated (not generated from a shared spec) to make per-mode edits trivial.

### Key Types

```typescript
type MemoryType = 'user' | 'feedback' | 'project' | 'reference'
```

### Key Exports

#### `MEMORY_TYPES` and `parseMemoryType(raw)`
The four-type constant array and a parse function. Invalid/missing values return `undefined` — legacy files without a `type:` field keep working.

#### `TYPES_SECTION_COMBINED: readonly string[]`
"## Types of memory" section for combined mode (private + team directories). Uses XML-style `<type>` blocks with `<scope>` tags (`always private`, `default to private`, `private or team but strongly bias toward team`, `usually team`). Each type has `<description>`, `<when_to_save>`, `<how_to_use>`, and `<examples>` sub-blocks. Feedback type additionally has `<body_structure>`. Examples use "saves private feedback memory" and "saves team project memory" qualifiers.

#### `TYPES_SECTION_INDIVIDUAL: readonly string[]`
Individual-only variant. No `<scope>` tags. Examples use plain "saves user memory" without private/team qualifiers. Prose that only makes sense with a private/team split is reworded.

#### `WHAT_NOT_TO_SAVE_SECTION: readonly string[]`
"## What NOT to save in memory" — five exclusion rules:
- Code patterns, conventions, architecture, file paths (derivable from current project state)
- Git history, recent changes (git log/blame are authoritative)
- Debugging solutions or fix recipes (the fix is in the code)
- Anything already in CLAUDE.md files
- Ephemeral task details

Includes an explicit-save gate: "These exclusions apply even when the user explicitly asks you to save."

#### `WHEN_TO_ACCESS_SECTION: readonly string[]`
Three access rules plus `MEMORY_DRIFT_CAVEAT`. Includes the "ignore" bullet (H6 eval-validated): "If the user says to ignore or not use memory: proceed as if MEMORY.md were empty."

#### `TRUSTING_RECALL_SECTION: readonly string[]`
"## Before recommending from memory" — heavier-weight guidance on verifying memory claims. Three verification rules:
- If memory names a file path: check the file exists
- If memory names a function or flag: grep for it
- If user is about to act on your recommendation: verify first

Eval-validated (memory-prompt-iteration.eval.ts): position matters. When buried as a bullet under "When to access", dropped to 0/3 on H1 evals. Needs its own section.

#### `MEMORY_DRIFT_CAVEAT: string`
"Memory records can become stale over time. Use memory as context for what was true at a given point in time. Before answering the user or building assumptions based solely on information in memory records, verify that the memory is still correct..."

#### `MEMORY_FRONTMATTER_EXAMPLE: readonly string[]`
YAML frontmatter template with `name`, `description`, and `type` fields.

---

## 6. `memdir/paths.ts` (278 lines) — Path Resolution

### Purpose

Resolves the auto-memory directory path with a multi-layer priority chain. Provides path validation with security hardening against traversal attacks.

### Key Functions

#### `isAutoMemoryEnabled(): boolean`
Priority chain (first defined wins):
1. `CLAUDE_CODE_DISABLE_AUTO_MEMORY` env var (1/true → OFF, 0/false → ON)
2. `CLAUDE_CODE_SIMPLE` (--bare) → OFF
3. CCR without persistent storage (`CLAUDE_CODE_REMOTE` set, `CLAUDE_CODE_REMOTE_MEMORY_DIR` unset) → OFF
4. `autoMemoryEnabled` in settings.json (supports project-level opt-out)
5. Default: enabled

#### `isExtractModeActive(): boolean`
Whether the extract-memories background agent will run this session. Gated on `tengu_passport_quail` feature flag. Non-interactive sessions excluded unless `tengu_slate_thimble` is also enabled.

#### `getMemoryBaseDir(): string`
Resolution:
1. `CLAUDE_CODE_REMOTE_MEMORY_DIR` env var (explicit override, set in CCR)
2. `~/.claude` (default config home via `getClaudeConfigHomeDir()`)

#### `getAutoMemPath(): string` (memoized)
Resolution order:
1. `CLAUDE_COWORK_MEMORY_PATH_OVERRIDE` env var (full-path override, used by Cowork to redirect to space-scoped mount)
2. `autoMemoryDirectory` in settings.json (trusted sources only: policySettings, flagSettings, localSettings, userSettings — projectSettings excluded for security)
3. `<memoryBase>/projects/<sanitized-git-root>/memory/`

Memoized keyed on `getProjectRoot()`. Uses `findCanonicalGitRoot` so all worktrees of the same repo share one auto-memory directory.

#### `validateMemoryPath(raw, expandTilde): string | undefined`
Security validation rejects:
- Relative paths (`!isAbsolute`)
- Root/near-root (`length < 3`)
- Windows drive-root (`C:` regex)
- UNC paths (`\\\\server\\share`)
- Null bytes (survives normalize(), can truncate in syscalls)
- `~/` expansion to `$HOME` or an ancestor

#### `isAutoMemPath(absolutePath): boolean`
Containment check: normalizes path, checks `startsWith(getAutoMemPath())`. Used by filesystem.ts write carve-out for DANGEROUS_DIRECTORIES bypass.

#### `getAutoMemEntrypoint(): string`
Returns `join(getAutoMemPath(), 'MEMORY.md')`.

#### `getAutoMemDailyLogPath(date?): string`
Returns `{autoMemPath}/logs/YYYY/MM/YYYY-MM-DD.md`. Used by assistant mode (KAIROS).

---

## 7. `memdir/teamMemPaths.ts` (292 lines) — Team Memory Paths

### Purpose

Team memory path resolution and security validation. Team memory lives as a subdirectory (`memory/team/`) of the auto-memory directory.

### Key Types

```typescript
class PathTraversalError extends Error
```

### Key Functions

#### `isTeamMemoryEnabled(): boolean`
Requires `isAutoMemoryEnabled()` AND `tengu_herring_clock` feature flag.

#### `getTeamMemPath(): string`
Returns `join(getAutoMemPath(), 'team')` with trailing separator, NFC-normalized.

#### `getTeamMemEntrypoint(): string`
Returns `join(getAutoMemPath(), 'team', 'MEMORY.md')`.

#### `sanitizePathKey(key: string): string`
Rejects dangerous patterns:
- Null bytes (can truncate paths in C-based syscalls)
- URL-encoded traversals (`%2e%2e%2f` = `../`) — decodes and checks
- Unicode normalization attacks (fullwidth `．．／` normalizes to `../` under NFKC) — checks both raw and NFKC-normalized forms
- Backslashes (Windows path separator as traversal vector)
- Absolute paths (starting with `/`)

#### `isTeamMemPath(filePath): boolean`
String-level containment check using `path.resolve()` to eliminate `..` segments. Does NOT resolve symlinks.

#### `validateTeamMemWritePath(filePath): Promise<string>`
Two-pass validation for write operations:
1. **String-level**: `resolve()` normalizes `..` segments, checks `startsWith(teamDir)`.
2. **Symlink-level**: `realpathDeepestExisting()` resolves symlinks on the deepest existing ancestor, then `isRealPathWithinTeamDir()` verifies the real path is within the real team dir.

Throws `PathTraversalError` on any violation.

#### `realpathDeepestExisting(absolutePath): Promise<string>`
Walks up the directory tree until `realpath()` succeeds, then rejoins the non-existing tail onto the resolved ancestor. Handles:
- `ENOENT` — may be dangling symlink (attacks via writeFile following the link), checks with `lstat()` to distinguish
- `ELOOP` — symlink loop, throws PathTraversalError
- `EACCES`, `EIO` — cannot verify containment, fails closed

#### `validateTeamMemKey(relativeKey): Promise<string>`
Validation for server-supplied relative path keys. Sanitizes the key, joins with team dir, then runs the same two-pass validation as `validateTeamMemWritePath`.

#### `isTeamMemFile(filePath): boolean`
Convenience: `isTeamMemoryEnabled() && isTeamMemPath(filePath)`.

---

## 8. `memdir/teamMemPrompts.ts` (100 lines) — Combined Prompt

### Purpose

Builds the combined memory prompt when both auto and team memory are enabled.

### Key Functions

#### `buildCombinedMemoryPrompt(extraGuidelines?, skipIndex?): string`
Builds a prompt with:
- `# Memory` header
- Two-directory layout: private at `{autoDir}`, team at `{teamDir}`
- `## Memory scope` section explaining private vs team
- `## Types of memory` (from `TYPES_SECTION_COMBINED` with `<scope>` tags)
- `## What NOT to save in memory` (same as individual mode)
- `## How to save memories` (two-step: write file in chosen directory + add pointer to that directory's MEMORY.md)
- `## When to access memories` (with MEMORY_DRIFT_CAVEAT)
- `## Before recommending from memory` (TRUSTING_RECALL_SECTION)
- `## Memory and other forms of persistence`
- `## Searching past context` (if feature-gated)

The `skipIndex` parameter controls whether Step 2 (MEMORY.md pointer) is included. When true, the prompt omits Step 2 and related text about MEMORY.md as an index.

Includes an additional rule for team mode: "You MUST avoid saving sensitive data within shared team memories. For example, never save API keys or user credentials."

---

## Architecture Summary

```
loadMemoryPrompt() ──┬── KAIROS? → buildAssistantDailyLogPrompt()
                     │              └── uses getAutoMemPath(), logPathPattern
                     │
                     ├── TEAMMEM? → teamMemPrompts.buildCombinedMemoryPrompt()
                     │              ├── TYPES_SECTION_COMBINED (<scope> tags)
                     │              ├── DIRS_EXIST_GUIDANCE
                     │              └── ensureMemoryDirExists(teamDir)
                     │
                     ├── autoEnabled? → buildMemoryLines() → buildMemoryPrompt()
                     │                  ├── TYPES_SECTION_INDIVIDUAL
                     │                  ├── truncateEntrypointContent(MEMORY.md)
                     │                  └── ensureMemoryDirExists(autoDir)
                     │
                     └── disabled → null (log tengu_memdir_disabled)

findRelevantMemories() ── scanMemoryFiles() → formatMemoryManifest()
                          → sideQuery(Sonnet, json_schema) → select up to 5
                          → logMemoryRecallShape()

Paths resolution chain:
  CLAUDE_COWORK_MEMORY_PATH_OVERRIDE
  → autoMemoryDirectory in settings (user/policy/local, NOT projectSettings)
  → ~/.claude/projects/<sanitized-git-root>/memory/
```
