# File Operation Tools

Four tools for file reading, editing, writing, and notebook manipulation. Together they form the primary filesystem surface of the tool system.

---

## FileReadTool (`src/tools/FileReadTool/FileReadTool.ts`, 1183 lines)

**Name**: `FILE_READ_TOOL_NAME`
**Search Hint**: `"read files, images, PDFs, notebooks"`
**Concurrency Safe**: Yes
**Read Only**: Yes
**Max Result Size**: `Infinity` (never persisted to disk — circular Read→file→Read loop)
**Strict Mode**: Yes

### Input Schema
```typescript
z.strictObject({
  file_path: z.string(),          // Absolute path
  offset: z.number().int().nonnegative().optional(),  // Starting line (1-indexed)
  limit: z.number().int().positive().optional(),     // Lines to read
  pages: z.string().optional(),   // PDF page range (e.g., "1-5", "3", "10-20")
})
```

### Output Schema
Discriminated union on `type` with 6 variants:

| `type` | Shape | When |
|--------|-------|------|
| `text` | `{ file: { filePath, content, numLines, startLine, totalLines } }` | Regular text files |
| `image` | `{ file: { base64, type (MIME), originalSize, dimensions? } }` | Image files (png/jpg/gif/webp) |
| `notebook` | `{ file: { filePath, cells[] } }` | Jupyter .ipynb files |
| `pdf` | `{ file: { filePath, base64, originalSize } }` | PDF files (inline, small) |
| `parts` | `{ file: { filePath, originalSize, count, outputDir } }` | PDF files (page extraction, large) |
| `file_unchanged` | `{ file: { filePath } }` | Dedup stub when file hasn't changed |

### Core Execution Flow (`call()`)

**1. Path Expansion**: `expandPath(file_path)` normalizes the path (handles `~`, relative paths, Windows separators, whitespace trimming).

**2. Dedup Check** (GrowthBook killswitch `tengu_read_dedup_killswitch`):
- Checks `readFileState` LRU cache for a prior read at the same range
- Compares file mtime — if unchanged, returns `type: 'file_unchanged'` stub
- Saves ~2.64% of fleet cache_creation tokens (BQ proxy data)
- Only dedup text/notebook reads; images/PDFs aren't cached in readFileState

**3. Skill Discovery**: Fire-and-forget skill directory discovery and conditional skill activation from the read path (skipped in simple mode).

**4. Content-Type Dispatch**:

| Extension | Handler | Details |
|-----------|---------|---------|
| `.ipynb` | `readNotebook()` → JSON parse → validate size → validate tokens → return `notebook` | Max size enforced against `maxSizeBytes` |
| `.png/.jpg/.jpeg/.gif/.webp` | `readImageWithTokenBudget()` → single-read → resize → compress | Token budget from `maxTokens`; aggressive sharp fallback |
| `.pdf` | `getPDFPageCount()` → `readPDF()` or `extractPDFPages()` | Threshold-based: inline if small + supported, else page extraction (requires poppler) |
| All others | `readFileInRange()` → `validateContentTokens()` → return `text` | Line-numbered text output |

**5. Post-Read**:
- Updates `readFileState` with content, timestamp, offset, limit
- Fires `fileReadListeners` (snapshot before iteration)
- Logs analytics (`tengu_session_file_read`, file operation, session detection)
- Auto-memory files get a freshness prefix via `memoryFileMtimes` WeakMap

### Validation (`validateInput()`)

Executed **before** `checkPermissions` (pre-I/O phase):

1. **PDF page range**: Parse with `parsePDFPageRange()`, validate count ≤ `PDF_MAX_PAGES_PER_READ` (error code 7-8)
2. **Path expansion & deny rules**: `expandPath(file_path)` + check deny rules on expanded path (error code 1)
3. **UNC path guard**: Skip filesystem operations for `\\` or `//` paths (NTLM credential leak prevention)
4. **Binary extension check**: String-only extension check — reject known binary types unless PDF/image (error code 4)
5. **Blocked device paths**: Reject `/dev/zero`, `/dev/random`, `/dev/urandom`, `/dev/stdin/tty/console`, `/dev/fd/0-2`, `/proc/.../fd/0-2` (error code 9)

### macOS Screenshot Handling

`getAlternateScreenshotPath()` detects macOS screenshot filenames with AM/PM markers and tries the alternate space character (regular space vs. U+202F thin space) if the file isn't found. macOS versions differ in which space character they use.

### Image Processing (`readImageWithTokenBudget()`)

Single-read pipeline:
1. `getFsImplementation().readFileBytes(filePath, maxBytes)` — capped read
2. `detectImageFormatFromBuffer()` — detect MIME type
3. `maybeResizeAndDownsampleImageBuffer()` — standard resize
4. Token estimation: `Math.ceil(base64.length * 0.125)`
5. If over budget: `compressImageBufferWithTokenLimit()` from SAME buffer
6. Fallback: sharp resize to 400x400 JPEG quality 20 (from SAME buffer)

### Cyber Risk Mitigation

`CYBER_RISK_MITIGATION_REMINDER` is appended to text file results for all models except `claude-opus-4-6`:
```
<system-reminder>
Whenever you read a file, you should consider whether it would be considered malware...
</system-reminder>
```

### Token Validation

`validateContentTokens()`:
1. Quick estimate via `roughTokenCountEstimationForFileType()`
2. If estimate > `maxTokens / 4`: full count via `countTokensWithAPI()`
3. Throws `MaxFileReadTokenExceededError` if over limit

### Map to API Blocks (`mapToolResultToToolResultBlockParam`)

| Type | Result Block |
|------|-------------|
| `image` | `{ type: 'tool_result', content: [{ type: 'image', source: { type: 'base64', data, media_type } }] }` |
| `notebook` | Via `mapNotebookCellsToToolResult()` |
| `pdf` | Text note: `"PDF file read: {path} ({size})"` — actual content sent as supplemental DocumentBlockParam |
| `parts` | Text note: `"PDF pages extracted: {count} page(s) from {path}"` |
| `file_unchanged` | `FILE_UNCHANGED_STUB` constant |
| `text` | Content + optional memory freshness prefix + optional cyber mitigation reminder + line-number formatting |

### Sub-files

- **`prompt.ts`**: Tool description, line format instructions, offset instructions (targeted vs. default)
- **`limits.ts`**: `getDefaultFileReadingLimits()` returns `{ maxTokens, maxSizeBytes, targetedRangeNudge, includeMaxSizeInPrompt }`
- **`imageProcessor.ts`**: Image reading/buffer handling utilities
- **`UI.tsx`**: `userFacingName` ("Read"), `getToolUseSummary`, `renderToolUseMessage`, `renderToolResultMessage`, `renderToolUseErrorMessage`, `renderToolUseTag`

### Helper Types

- `MaxFileReadTokenExceededError` — thrown when content exceeds token budget
- `BLOCKED_DEVICE_PATHS` — Set of device paths that would hang (infinite output / blocking input)
- `IMAGE_EXTENSIONS` — `Set(['png', 'jpg', 'jpeg', 'gif', 'webp'])`
- `fileReadListeners` — Array of `FileReadListener` callbacks for cross-cutting read notifications

---

## FileEditTool (`src/tools/FileEditTool/FileEditTool.ts`, 625 lines)

**Name**: `FILE_EDIT_TOOL_NAME`
**Search Hint**: `"modify file contents in place"`
**Concurrency Safe**: No (default)
**Read Only**: No (default — writes)
**Max Result Size**: `100_000` chars
**Strict Mode**: Yes

### Input Schema (from `types.ts`)
```typescript
z.strictObject({
  file_path: z.string(),        // Absolute path
  old_string: z.string(),       // Text to replace
  new_string: z.string(),       // Replacement text
  replace_all: z.boolean().optional(),  // Replace all occurrences
})
```

### Output Schema (from `types.ts`)
```typescript
z.object({
  filePath: z.string(),
  oldString: z.string(),        // Actual string found (after quote normalization)
  newString: z.string(),
  originalFile: z.string(),     // Pre-edit content
  structuredPatch: patchSchema(), // Diff hunks
  userModified: z.boolean(),    // Whether user modified before accepting
  replaceAll: z.boolean(),
  gitDiff: gitDiffSchema().optional(),
})
```

### Validation (`validateInput()`)

A multi-stage validation pipeline (error codes 0-10):

1. **Secret check** (code 0): `checkTeamMemSecrets()` rejects edits introducing secrets to team memory files
2. **No-op check** (code 1): `old_string === new_string` → reject with `behavior: 'ask'`
3. **Deny rule check** (code 2): Expanded path tested against deny rules for 'edit' permission
4. **UNC path guard**: Skip filesystem I/O for UNC paths (NTLM leak prevention)
5. **Size check** (code 10): Async `fs.stat()` — reject files > 1 GiB (V8/Bun string length limit)
6. **Encoding detection**: Read file bytes, detect UTF-16LE BOM (`0xFF 0xFE`) vs UTF-8
7. **File existence** (code 3-4):
   - Nonexistent + empty `old_string`: valid (new file creation)
   - Nonexistent + non-empty `old_string`: suggest similar filename via `findSimilarFile()` / `suggestPathUnderCwd()`
   - Exists + empty `old_string` + non-empty file: reject (file already exists)
8. **Notebook rejection** (code 5): `.ipynb` files require NotebookEditTool
9. **Read-before-edit** (code 6): `readFileState.get()` must have an entry — no blind edits
10. **Staleness check** (code 7): File mtime must not exceed read timestamp. On Windows, falls back to content comparison for full reads (avoids false positives from cloud sync/antivirus timestamp changes)
11. **String matching** (code 8): `findActualString()` handles curly-quote normalization. Returns `actualOldString` in meta
12. **Multiple matches** (code 9): If matches > 1 and `replace_all` is false, reject with count
13. **Settings validation**: `validateInputForSettingsFileEdit()` runs additional checks for Claude config files
14. **Success**: Returns `{ result: true, meta: { actualOldString } }`

### Core Execution Flow (`call()`)

**Atomic Read-Modify-Write Section** (no async between staleness check and write):

1. **Pre-section**: Skill discovery, diagnostic tracking, `mkdir(dirname(...))`, file history backup
2. **Read**: `readFileForEdit()` synchronously reads file with metadata (encoding, line endings)
3. **Staleness check**: Compares file mtime against `readFileState` entry; content-comparison fallback for Windows
4. **Quote normalization**: `findActualString()` matches the target string accounting for curly quotes
5. **Quote preservation**: `preserveQuoteStyle()` applies the same quote transformations to `new_string`
6. **Patch generation**: `getPatchForEdit()` computes a structured diff
7. **Write**: `writeTextContent()` with encoding and line endings preserved
8. **LSP notification**: `didChange` + `didSave` notifications to all LSP managers; clears delivered diagnostics
9. **VSCode notification**: `notifyVscodeFileUpdated()` for diff view
10. **State update**: `readFileState.set()` with post-write mtime (offset:undefined breaks Read dedup)
11. **Analytics**: CLAUDE.md detection (`tengu_write_claudemd`), line count tracking, file operation logging, string length event, optional git diff (remote + `tengu_quartz_lantern` gate)

### Input Equivalence (`inputsEquivalent()`)

Delegates to `areFileEditsInputsEquivalent()` in utils.ts. Converts individual `old_string/new_string/replace_all` fields to the multi-edit format used by the equivalence checker.

### Map to API Blocks

Returns success messages with optional user-modification notes. Replace-all mode gets a distinct message: `"The file {path} has been updated. All occurrences were successfully replaced."`

### Sub-files

- **`types.ts`**: `FileEditInput`, `FileEditOutput`, `inputSchema`, `outputSchema`, patch/hunk/gitDiff Zod schemas
- **`utils.ts`** (775 lines): Quote normalization (`findActualString`, `preserveQuoteStyle`), patch generation (`getPatchForEdit`), input equivalence (`areFileEditsInputsEquivalent`), CRLF normalization
- **`constants.ts`**: `FILE_EDIT_TOOL_NAME`, `FILE_UNEXPECTEDLY_MODIFIED_ERROR` ("File has been modified since read...")
- **`prompt.ts`**: `getEditToolDescription()` — model-facing usage guide
- **`UI.tsx`**: `userFacingName` ("Edit"), `getToolUseSummary`, `renderToolUseMessage`, `renderToolResultMessage`, `renderToolUseRejectedMessage` (shows rejected diff), `renderToolUseErrorMessage`

### Key Constants

- `MAX_EDIT_FILE_SIZE` = 1 GiB (stat bytes) — prevents OOM on multi-GB files

---

## FileWriteTool (`src/tools/FileWriteTool/FileWriteTool.ts`, 434 lines)

**Name**: `FILE_WRITE_TOOL_NAME`
**Search Hint**: `"create or overwrite files"`
**Concurrency Safe**: No (default)
**Read Only**: No (default — writes)
**Max Result Size**: `100_000` chars
**Strict Mode**: Yes

### Input Schema
```typescript
z.strictObject({
  file_path: z.string(),    // Absolute path
  content: z.string(),      // Full file content
})
```

### Output Schema
```typescript
z.object({
  type: z.enum(['create', 'update']),
  filePath: z.string(),
  content: z.string(),
  structuredPatch: z.array(hunkSchema()),  // Empty for create
  originalFile: z.string().nullable(),     // null for create
  gitDiff: gitDiffSchema().optional(),
})
```

### Validation (`validateInput()`)

1. **Secret check** (code 0): `checkTeamMemSecrets(fullFilePath, content)`
2. **Deny rule check** (code 1): Expanded path against 'edit' deny rules
3. **UNC path guard**: Skip I/O for UNC paths
4. **File existence**: Async `fs.stat()` — if ENOENT, passes validation (new file creation)
5. **Read-before-write** (code 2): `readFileState.get()` must have an entry; no blind overwrites
6. **Staleness check** (code 3): File mtime must not exceed read timestamp

### Core Execution (`call()`)

Similar to FileEditTool's atomic section:

1. **Pre-section**: Skill discovery, diagnostic tracking, `mkdir(dirname(...))`, file history backup
2. **Read**: `readFileSyncWithMetadata()` for existing files; null for new
3. **Staleness check**: For existing files, compare mtime (with Windows content-comparison fallback for full reads)
4. **Write**: `writeTextContent()` with preserved encoding, explicit LF endings (does NOT preserve original line endings — the model sent explicit endings in `content`)
5. **LSP notification**: `didChange` + `didSave`
6. **VSCode notification**: `notifyVscodeFileUpdated(fullFilePath, oldContent, content)`
7. **State update**: `readFileState.set()` with post-write content + mtime
8. **Analytics**: CLAUDE.md detection, line counting, file operation logging, optional git diff

**Key difference from FileEditTool**: Full content replacement (not string-based). For new files (`type: 'create'`), `structuredPatch` is empty and `originalFile` is null.

### Map to API Blocks

| Type | Result |
|------|--------|
| `create` | `"File created successfully at: {filePath}"` |
| `update` | `"The file {filePath} has been updated successfully."` |

### Sub-files

- **`prompt.ts`**: `FILE_WRITE_TOOL_NAME`, `getWriteToolDescription()`
- **`UI.tsx`**: `userFacingName` ("Write"), `getToolUseSummary`, `isResultTruncated`, `renderToolUseMessage`, `renderToolResultMessage`, `renderToolUseRejectedMessage`, `renderToolUseErrorMessage`

---

## NotebookEditTool (`src/tools/NotebookEditTool/NotebookEditTool.ts`, 490 lines)

**Name**: `NOTEBOOK_EDIT_TOOL_NAME`
**Search Hint**: `"edit Jupyter notebook cells (.ipynb)"`
**Concurrency Safe**: No (default)
**Read Only**: No (default — writes)
**Max Result Size**: `100_000` chars
**Deferred**: Yes (`shouldDefer: true`)

### Input Schema
```typescript
z.strictObject({
  notebook_path: z.string(),              // Absolute path
  cell_id: z.string().optional(),         // Cell ID (or cell-N index)
  new_source: z.string(),                 // New cell source content
  cell_type: z.enum(['code', 'markdown']).optional(),  // Required for insert
  edit_mode: z.enum(['replace', 'insert', 'delete']).optional(),  // Default: replace
})
```

### Output Schema
```typescript
z.object({
  new_source: z.string(),
  cell_id: z.string().optional(),
  cell_type: z.enum(['code', 'markdown']),
  language: z.string(),                   // From notebook metadata
  edit_mode: z.string(),
  error: z.string().optional(),
  notebook_path: z.string(),
  original_file: z.string(),             // Pre-edit notebook JSON
  updated_file: z.string(),              // Post-edit notebook JSON
})
```

### Validation (`validateInput()`)

1. **UNC path guard**
2. **Extension check** (code 2): Must be `.ipynb` — redirects to FileEditTool for other types
3. **Edit mode validation** (code 4): Must be `replace`, `insert`, or `delete`
4. **Insert requires type** (code 5): `edit_mode=insert` must specify `cell_type`
5. **Read-before-edit** (code 9): `readFileState.get()` must exist
6. **Staleness check** (code 10): File mtime vs. read timestamp
7. **Notebook JSON validation** (code 6): Must parse as valid JSON
8. **Cell ID validation** (code 7-8): Empty cell_id only valid for insert; numeric index fallback via `parseCellId()`

### Core Execution (`call()`)

1. **Read**: `readFileSyncWithMetadata()` for encoding/line endings; `jsonParse()` for notebook object (use non-memoized parser — mutations below would poison the cache)
2. **Cell lookup**: Find by actual ID first, then try `parseCellId()` for numeric indices
3. **Insert position**: Cell inserted *after* the identified cell (+1 index)
4. **Edge case**: `replace` at index === cells.length → converted to `insert`
5. **Notebook format detection**: nbformat ≥ 4.5 requires `id` field on cells; generate random ID for inserts
6. **Operation dispatch**:
   - `delete`: `cells.splice(cellIndex, 1)`
   - `insert`: Create new `NotebookCell` object (code or markdown), `cells.splice(cellIndex, 0, new_cell)`
   - `replace`: Update `targetCell.source`, reset `execution_count` + `outputs` for code cells, optionally change `cell_type`
7. **Write**: `jsonStringify(notebook, null, 1)` + `writeTextContent()` with preserved encoding/line endings
8. **State update**: `readFileState.set()` with `offset: undefined` (breaks FileReadTool dedup to prevent stale read caching)

### Map to API Blocks

| Edit Mode | Result |
|-----------|--------|
| `replace` | `"Updated cell {cell_id} with {new_source}"` |
| `insert` | `"Inserted cell {cell_id} with {new_source}"` |
| `delete` | `"Deleted cell {cell_id}"` |
| Error | Uses `is_error: true` with error message |

### Conditional Classifier Input

When `feature('TRANSCRIPT_CLASSIFIER')` is enabled: `"{notebook_path} {mode}: {new_source}"`. Otherwise returns `''`.

### Sub-files

- **`constants.ts`**: `NOTEBOOK_EDIT_TOOL_NAME`
- **`prompt.ts`**: `DESCRIPTION`, `PROMPT`
- **`UI.tsx`**: `userFacingName` ("Edit Notebook"), `getToolUseSummary`, `renderToolUseMessage`, `renderToolResultMessage`, `renderToolUseRejectedMessage`, `renderToolUseErrorMessage`

---

## Cross-Cutting Patterns

### Read-Before-Write Guard
FileEditTool and FileWriteTool refuse to modify files that haven't been read first. The `readFileState` LRU cache tracks reads, and both tools validate the cache entry exists and the file mtime hasn't advanced (with Windows content-comparison fallback). NotebookEditTool enforces the same pattern.

### UNC Path Protection
All file tools skip filesystem I/O for UNC paths (`\\` or `//` prefix) to prevent NTLM credential leaks on Windows. This check happens early in validation, before any `stat()` or `readFile()` calls.

### Path Expansion & Backfill
All tools call `expandPath()` to normalize `~`, relative paths, and Windows separators. The `backfillObservableInput()` method also applies this normalization to observable copies (for hooks/observers) while preserving the original API-bound input for prompt cache stability.

### Atomic Read-Modify-Write
FileEditTool and FileWriteTool maintain a critical section between their staleness check and disk write where no async operations occur, preserving atomicity. The `mkdir()` for parent directories happens before this section.

### Skill Discovery
All file-mutating tools fire `discoverSkillDirsForPaths()` and `activateConditionalSkillsForPaths()` as side effects (fire-and-forget, non-blocking).

### LSP Integration
FileEditTool and FileWriteTool notify LSP servers via `didChange` (content modified) and `didSave` (file saved — triggers diagnostics). They clear previously delivered diagnostics before applying. Failures are logged but don't block the operation.

### VSCode Integration
`notifyVscodeFileUpdated()` sends the pre/post content for VSCode's diff view, enabled via the VSCode SDK MCP channel.

### Team Memory Secret Guard
`checkTeamMemSecrets()` runs on all writes/edits to team memory files, rejecting content that introduces secrets.

### File History Tracking
When `fileHistoryEnabled()`, all write/edit operations are backed up via `fileHistoryTrackEdit()` before the critical section. Backups are idempotent (keyed on content hash), so unused backups from failed staleness checks are harmless.

### Git Diff Capture
FileEditTool and FileWriteTool optionally compute a single-file git diff (gated by `CLAUDE_CODE_REMOTE` and `tengu_quartz_lantern` GrowthBook flag). The diff is included in the output for remote session context enrichment.
