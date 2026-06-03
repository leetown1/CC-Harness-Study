# Search Tools

Four tools for searching codebases, file systems, and the web: GrepTool, GlobTool, WebSearchTool, and WebFetchTool.

---

## GrepTool (`src/tools/GrepTool/GrepTool.ts`, 577 lines)

**Name**: `GREP_TOOL_NAME`
**Search Hint**: `"search file contents with regex (ripgrep)"`
**Concurrency Safe**: Yes
**Read Only**: Yes
**Max Result Size**: `20_000` chars
**Strict Mode**: Yes

Content search via the system ripgrep binary. Supports multiple output modes, context lines, pagination, and comprehensive file filtering.

### Input Schema
```typescript
z.strictObject({
  pattern: z.string(),                                     // Regex pattern
  path: z.string().optional(),                             // File or directory (default: cwd)
  glob: z.string().optional(),                             // Glob filter (e.g., "*.js", "*.{ts,tsx}")
  output_mode: z.enum(['content', 'files_with_matches', 'count']).optional(),
  '-B': z.number().optional(),                             // Lines before match (context)
  '-A': z.number().optional(),                             // Lines after match (context)
  '-C': z.number().optional(),                             // Lines before & after (alias: context)
  context: z.number().optional(),                          // Same as -C
  '-n': z.boolean().optional(),                            // Show line numbers (default: true)
  '-i': z.boolean().optional(),                            // Case insensitive
  type: z.string().optional(),                             // File type filter (rg --type)
  head_limit: z.number().optional(),                       // Max results (default: 250, 0 = unlimited)
  offset: z.number().optional(),                           // Skip first N results (default: 0)
  multiline: z.boolean().optional(),                       // Multiline mode (rg -U --multiline-dotall)
})
```

### Output Schema
```typescript
z.object({
  mode: z.enum(['content', 'files_with_matches', 'count']).optional(),
  numFiles: z.number(),
  filenames: z.array(z.string()),
  content: z.string().optional(),          // Content mode output
  numLines: z.number().optional(),          // Lines in content mode
  numMatches: z.number().optional(),        // Total matches in count mode
  appliedLimit: z.number().optional(),      // Actual limit applied (only when truncated)
  appliedOffset: z.number().optional(),     // Actual offset applied
})
```

### Output Modes

| Mode | ripgrep Flag | Description | Key Fields |
|------|-------------|-------------|------------|
| `content` | (default) | Matching lines with context | `content`, `numLines` |
| `files_with_matches` | `-l` | File paths sorted by mtime | `filenames`, `numFiles` |
| `count` | `-c` | Match counts per file | `content` (filename:count), `numMatches`, `numFiles` |

### Pagination (`applyHeadLimit()`)

Smart truncation with overflow awareness:
- `head_limit` default: `250` rows (DEFAULT_HEAD_LIMIT)
- `head_limit: 0` = unlimited escape hatch
- `offset` skips first N results before applying limit
- `appliedLimit` only set in output when truncation **actually occurred**, signaling the model to paginate
- Applied BEFORE path relativization (avoids processing discarded lines)

### Core Execution Flow

1. **Ripgrep arguments construction**:
   - `--hidden` (search hidden files)
   - `--glob !<vcs_dir>` for each of `.git`, `.svn`, `.hg`, `.bzr`, `.jj`, `.sl`
   - `--max-columns 500` (prevents base64/minified content clutter)
   - Multiline: `-U --multiline-dotall` if requested
   - Case insensitive: `-i` if requested
   - Output mode flags: `-l`, `-c`
   - Line numbers: `-n` (content mode only)
   - Context lines: `-C`, `-B`, `-A` precedence ordering
   - Pattern with `-` prefix: use `-e` flag

2. **Type filtering**: Direct `--type` flag for standard ripgrep file types

3. **Glob filtering**: Splits multiple glob patterns on commas/spaces, preserves brace patterns, feeds each as separate `--glob` argument

4. **Ignore patterns**: Loaded from `getFileReadIgnorePatterns(appState.toolPermissionContext)`, converted to ripgrep `--glob !pattern` format

5. **Plugin orphan exclusions**: `getGlobExclusionsForPluginCache()` adds exclusions for outdated plugin version directories

6. **Execution**: `ripGrep(args, absolutePath, abortController.signal)` — handles WSL2 performance penalty (3-5x slower) with built-in timeout

7. **Path relativization**: Absolute paths → relative (saves tokens) via `toRelativePath()`

8. **File sorting** (files_with_matches mode only):
   - `Promise.allSettled(fs.stat())` for mtime sorting
   - ENOENT-tolerant (files deleted between ripgrep scan and stat don't crash the batch)
   - Sorted by mtime descending, filename ascending as tiebreaker
   - Test mode: sorts by filename only for deterministic output

### Validation (`validateInput()`)

Path existence check with UNC guard and ENOENT-friendly error with cwd-relative suggestions.

### Map to API Blocks

Produces formatted output with pagination info, match counts, and filing summaries. Content mode includes `[Showing results with pagination = ...]` banner.

### Sub-files

- **`prompt.ts`**: `GREP_TOOL_NAME`, `getDescription()`
- **`UI.tsx`**: `userFacingName` ("Search"), `getToolUseSummary` (pattern + path), `renderToolUseMessage`, `renderToolResultMessage` (SearchResultSummary with file list or content), `renderToolUseErrorMessage`

---

## GlobTool (`src/tools/GlobTool/GlobTool.ts`, 198 lines)

**Name**: `GLOB_TOOL_NAME`
**Search Hint**: `"find files by name pattern or wildcard"`
**Concurrency Safe**: Yes
**Read Only**: Yes
**Max Result Size**: `100_000` chars

File pattern matching via the internal glob utility. Lightweight file discovery with permission-aware filtering and result truncation.

### Input Schema
```typescript
z.strictObject({
  pattern: z.string(),        // Glob pattern
  path: z.string().optional(), // Directory to search (default: cwd)
})
```

### Output Schema
```typescript
z.object({
  durationMs: z.number(),
  numFiles: z.number(),
  filenames: z.array(z.string()),     // Relative paths
  truncated: z.boolean(),             // Limited to 100 files
})
```

### Core Execution

1. **Path resolution**: `expandPath(path)` or `getCwd()` as default
2. **Glob execution**: `glob(pattern, resolvedPath, { limit, offset: 0 }, signal, permissionContext)`
   - `maxResults` from `globLimits?.maxResults ?? 100`
3. **Path relativization**: `toRelativePath()` for token efficiency
4. **Truncation flag**: Set when results exceed the limit

### Validation

Same pattern as GrepTool: path existence check with UNC guard, directory-type validation.

### Map to API Blocks

Empty results: `"No files found"`. Non-empty: filenames joined by newlines + truncation note.

### Sub-files

- **`prompt.ts`**: `GLOB_TOOL_NAME`, `DESCRIPTION`
- **`UI.tsx`**: `userFacingName` ("Find"), `getToolUseSummary`, `renderToolUseMessage`, `renderToolResultMessage`, `renderToolUseErrorMessage`

---

## WebSearchTool (`src/tools/WebSearchTool/WebSearchTool.ts`, 435 lines)

**Name**: `WEB_SEARCH_TOOL_NAME`
**Search Hint**: `"search the web for current information"`
**Concurrency Safe**: Yes
**Read Only**: Yes
**Max Result Size**: `100_000` chars
**Deferred**: Yes (`shouldDefer: true`)

Web search via the Claude API's server-side search capability. Uses a dedicated API call with the web search tool schema, streaming progress, and multi-turn search orchestration.

### Input Schema
```typescript
z.strictObject({
  query: z.string().min(2),                              // Search query
  allowed_domains: z.array(z.string()).optional(),        // Domain allowlist
  blocked_domains: z.array(z.string()).optional(),        // Domain blocklist
})
```

### Output Schema
```typescript
z.object({
  query: z.string(),
  results: z.array(z.union([searchResultSchema, z.string()])),  // Search results + commentary
  durationSeconds: z.number(),
})

// searchResultSchema
z.object({
  tool_use_id: z.string(),
  content: z.array(z.object({
    title: z.string(),
    url: z.string(),
  })),
})
```

### Provider Enablement (`isEnabled()`)

| Provider | Condition |
|----------|-----------|
| `firstParty` | Always enabled |
| `vertex` | Model includes `claude-opus-4`, `claude-sonnet-4`, or `claude-haiku-4` |
| `foundry` | Always enabled (only ships Web Search-capable models) |
| Other (e.g., Bedrock) | Disabled |

### Core Execution

1. **Dedicated API call**: `queryModelWithStreaming()` with a single `web_search_20250305` server tool schema
2. **Model selection**: GrowthBook gate `tengu_plum_vx3` uses Haiku (`getSmallFastModel()`) with thinking disabled; otherwise uses `mainLoopModel`
3. **Tool schema**: `max_uses: 8` hardcoded (Anthropic API rate limit)
4. **Tool choice**: Haiku path sets `tool_choice: { type: 'tool', name: 'web_search' }`
5. **Streaming progress**: Parses streaming events to emit progress updates:
   - `query_update` progress: Extracts query from partial JSON deltas
   - `search_results_received` progress: Fires when web_search_tool_result blocks arrive
6. **Result assembly**: `makeOutputFromSearchResponse()` interleaves text commentary and search result objects, handling `server_tool_use`, `web_search_tool_result`, and `text` block sequences

### Permission Model

Returns `behavior: 'passthrough'` with suggestions to add allow rules (cannot auto-approve).

### Map to API Blocks

Formats results with query header, text summaries, and JSON link arrays. Appends:
```
REMINDER: You MUST include the sources above in your response to the user using markdown hyperlinks.
```

### Validation

- Missing query → error code 1
- Both `allowed_domains` and `blocked_domains` specified → error code 2 (mutually exclusive)

### Sub-files

- **`prompt.ts`**: `WEB_SEARCH_TOOL_NAME`, `getWebSearchPrompt()`
- **`UI.tsx`**: `userFacingName` ("Web Search"), `getToolUseSummary`, `renderToolUseMessage`, `renderToolResultMessage` (search results with links), `renderToolUseProgressMessage` (search progress with live query display)

---

## WebFetchTool (`src/tools/WebFetchTool/WebFetchTool.ts`, 318 lines)

**Name**: `WEB_FETCH_TOOL_NAME`
**Search Hint**: `"fetch and extract content from a URL"`
**Concurrency Safe**: Yes
**Read Only**: Yes
**Max Result Size**: `100_000` chars
**Deferred**: Yes (`shouldDefer: true`)

URL content fetching with HTML→markdown conversion, AI-powered content extraction, domain preapproval, redirect handling, and binary content detection.

### Input Schema
```typescript
z.strictObject({
  url: z.string().url(),    // Valid URL
  prompt: z.string(),       // Prompt to apply to fetched content
})
```

### Output Schema
```typescript
z.object({
  bytes: z.number(),          // Content size
  code: z.number(),           // HTTP status code
  codeText: z.string(),       // HTTP status text
  result: z.string(),         // Processed result (prompt applied to content)
  durationMs: z.number(),     // Fetch + processing time
  url: z.string(),            // Original URL
})
```

### Permission Model

Three-tier check:
1. **Preapproved hosts**: `isPreapprovedHost(hostname, pathname)` → auto-approve (130+ domains including major documentation sites, package registries, public APIs)
2. **Explicit rules**: Check `getRuleByContentsForTool()` for deny → ask → allow cascade, matching by `domain:<hostname>` rule content
3. **Default**: Ask with suggestions to add allow rules

Auth warning is always included in the prompt:
```
IMPORTANT: WebFetch WILL FAIL for authenticated or private URLs. Before using this tool,
check if the URL points to an authenticated service...
```

### Core Execution Flow

1. **Fetch**: `getURLMarkdownContent(url, abortController)`:
   - Validates URL (against domain blocklist)
   - Handles HTTP redirects (cross-host detection)
   - Converts HTML to markdown via turndown
   - Caches results
   - Detects binary content (PDFs saved to disk with mime-based extension)

2. **Redirect handling**: If the redirect target is a different host, returns a structured redirect message instructing the model to retry with the redirected URL

3. **Content processing**: `applyPromptToMarkdown()`:
   - Preapproved markdown content under `MAX_MARKDOWN_LENGTH`: used directly
   - All other content: processed through AI prompt for extraction/summarization

4. **Binary content note**: Appended when binary content was saved to disk

### Validation

URL parsing via `new URL(url)` — returns error code 1 for malformed URLs.

### Sub-files

- **`prompt.ts`**: `WEB_FETCH_TOOL_NAME`, `DESCRIPTION`
- **`utils.ts`**: Core fetch logic — `getURLMarkdownContent()`, `applyPromptToMarkdown()`, `isPreapprovedUrl()`, `MAX_MARKDOWN_LENGTH`, URL validation, domain blocklist, redirect handling, caching, turndown integration
- **`preapproved.ts`**: 130+ preapproved domains covering major documentation sites (MDN, docs.rs, pkg.go.dev, etc.), package registries (npm, PyPI, crates.io), public APIs (GitHub API, StackOverflow), and developer resources
- **`UI.tsx`**: `userFacingName` ("Fetch"), `getToolUseSummary`, `renderToolUseMessage` (URL display), `renderToolUseProgressMessage`, `renderToolResultMessage`

### Map to API Blocks

Returns the `result` string directly as the tool_result content.

---

## Cross-Cutting Search Patterns

### Concurrency Safety
All search tools are `isConcurrencySafe: true` — multiple searches can run in parallel without interference.

### Read-Only
All search tools are `isReadOnly: true` — they never modify filesystem state.

### Path Relativization
GrepTool and GlobTool relativize absolute paths to save tokens in the model context. They also sort results by modification time (files_with_matches mode) or by internal ordering (content/count modes).

### Permission Model
GrepTool and GlobTool use `checkReadPermissionForTool()` for standard filesystem permission checks. WebSearchTool uses a passthrough pattern. WebFetchTool uses domain-based permission checks with preapproved host optimization.

### Deferred Loading
WebSearchTool and WebFetchTool are deferred (`shouldDefer: true`) — their full schemas don't appear in the initial prompt unless ToolSearch is used first. This reduces prompt bloat for tools that are used less frequently.

### Truncation & Pagination
GrepTool has the most sophisticated pagination system with `head_limit`/`offset`/`appliedLimit` for model-aware result pagination. GlobTool has a simpler fixed limit (`maxResults: 100`) with a `truncated` boolean. Both include awareness signals so the model knows when to paginate.
