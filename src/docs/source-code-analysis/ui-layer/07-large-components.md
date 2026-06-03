# Large Component Analysis (16 Files, ~8,200 Lines)

This document provides a function-by-function, type-by-type, and code-path-by-code-path analysis of every large standalone component in the UI layer.

---

## File 1: `LogSelector.tsx` (1,575 lines)

The session-resume picker: lets users browse, search, filter, rename, and resume past Claude Code sessions. Uses `TreeSelect` for session-fork grouping, `Fuse.js` for deep transcript search, and a multi-mode UI (list/search/rename/preview).

### Types

| Type | Description |
|---|---|
| `AgenticSearchState` | Union: `{status:'idle'}` \| `{status:'searching'}` \| `{status:'results', results:LogOption[], query:string}` \| `{status:'error', message:string}`. Tracks the AI-powered deep-search lifecycle. |
| `LogSelectorProps` | Props: `logs:LogOption[]`, `maxHeight?`, `forceWidth?`, `onCancel?`, `onSelect`, `onLogsChanged?`, `onLoadMore?`, `initialSearchQuery?`, `showAllProjects?`, `onToggleAllProjects?`, `onAgenticSearch?` (async AI search callback). |
| `Snippet` | `{before:string, match:string, after:string}` — extracted fragment around a deep-search match. |
| `LogTreeNode` | `TreeNode<{log:LogOption, indexInFiltered:number}>` — tree node for TreeSelect. |

### Helper Functions

- **`normalizeAndTruncateToWidth(text, maxWidth)`** — Collapses whitespace, truncates to terminal width.
- **`formatSnippet({before,match,after}, highlightColor)`** — Renders a snippet with `chalk.dim` for context and `highlightColor` for the match.
- **`extractSnippet(text, query, contextChars)`** — Case-insensitive exact-match snippet extraction. Returns `null` for fuzzy-only matches.
- **`buildLogLabel(log, maxLabelWidth, options?)`** — Constructs the display label for a log entry, accounting for `TreeSelect` prefix width (parent `▼ ` = 2 chars, child `  ▸ ` = 4 chars), sidechain markers, and fork counts (`(+N other sessions)`).
- **`buildLogMetadata(log, options?)`** — Builds metadata string with project-path suffix for cross-project view.
- **`extractSearchableText(message)`** — From `SerializedMessage`, extracts text from user/assistant `content` blocks (strings or structured arrays).
- **`buildSearchableText(log)`** — Aggregates metadata (title, summary, branch, tag, PR info) + cropped message text (first/last 1,000 messages from max 2,000) into a searchable string capped at 50,000 chars.
- **`groupLogsBySessionId(filteredLogs)`** — Groups logs by session ID (from `getSessionIdFromLog`), sorts each group by date descending.
- **`getUniqueTags(logs)`** — Extracts unique, alphabetically-sorted tags from all logs.

### Constants

| Constant | Value | Purpose |
|---|---|---|
| `PARENT_PREFIX_WIDTH` | 2 | `▼ ` or `▶ ` prefix width |
| `CHILD_PREFIX_WIDTH` | 4 | `  ▸ ` prefix width |
| `DEEP_SEARCH_MAX_MESSAGES` | 2000 | Max messages to index |
| `DEEP_SEARCH_CROP_SIZE` | 1000 | First/last N for long transcripts |
| `DEEP_SEARCH_MAX_TEXT_LENGTH` | 50000 | Cap searchable text per session |
| `FUSE_THRESHOLD` | 0.3 | Fuse.js fuzzy match threshold |
| `DATE_TIE_THRESHOLD_MS` | 60000 | 1-min window for relevance tiebreaker |
| `SNIPPET_CONTEXT_CHARS` | 50 | Context chars before/after match |

### Component: `LogSelector` (exported)

The main component. State variables:

| State | Type | Purpose |
|---|---|---|
| `currentBranch` | `string\|null` | Git branch, loaded on mount |
| `branchFilterEnabled` | `boolean` | Ctrl+B toggle to filter by current branch |
| `showAllWorktrees` | `boolean` | Ctrl+W toggle to show/hide other worktrees |
| `hasMultipleWorktrees` | `boolean` | Whether multiple git worktrees exist |
| `renameValue` | `string` | Inline rename text |
| `renameCursorOffset` | `number` | Cursor position in rename input |
| `expandedGroupSessionIds` | `Set<string>` | Which session groups are expanded in TreeSelect |
| `focusedNode` | `TreeNode\|null` | Currently focused tree/select node |
| `focusedIndex` | `number` | 1-based index for "X of N" display |
| `viewMode` | `"list"\|"search"\|"preview"\|"rename"` | Current UI mode |
| `previewLog` | `LogOption\|null` | Log being previewed (Ctrl+V) |
| `selectedTagIndex` | `number` | Active tag filter tab index |
| `agenticSearchState` | `AgenticSearchState` | AI search lifecycle |
| `isAgenticSearchOptionFocused` | `boolean` | Whether the "Search deeply" option is focused |

**Filtering pipeline** (applied in order):
1. **Rename-mode filter**: Exclude sessions without meaningful user content (`_temp2`).
2. **Tag filter**: `log.tag === selectedTag` (Tab-cycled).
3. **Branch filter**: `log.gitBranch === currentBranch` (Ctrl+B).
4. **Worktree filter**: `log.projectPath === currentCwd` when multiple worktrees exist (Ctrl+W).
5. **Title search**: Case-insensitive match against title, branch, tag, PR info.
6. **Deep search** (disabled `isDeepSearchEnabled=false`): Fuse.js fuzzy matching on transcript text with deduplication against title-match UUIDs.

**Key renders**:
- `viewMode === "preview"` → `<SessionPreview>` component
- `viewMode === "rename"` → `<TextInput>` overlay
- `viewMode === "list"` with rename enabled → `<TreeSelect>` with expand/collapse, group nodes
- `viewMode === "list"` without rename → `<Select>` flat list
- `viewMode === "search"` → `<SearchBox>` + select overlay
- Agentic search states → Spinner, "Claude found these results", "No matching sessions"

**Keybindings** (via `useInput`):
- `Tab` → Cycle tag filters
- `/` → Enter search mode
- `Ctrl+A` → Toggle all projects
- `Ctrl+B` → Toggle branch filter
- `Ctrl+W` → Toggle worktree filter
- `Ctrl+R` → Enter rename mode
- `Ctrl+V` → Open session preview
- Any alphanumeric key → Enter search with typed char
- `Enter` in agentic focus → Trigger AI search
- `Esc` → Cancel (via `useExitOnCtrlCDWithKeybindings`)

---

## File 2: `Stats.tsx` (1,228 lines)

A massive stats/metrics panel accessible via `/stats`. Shows session activity heatmaps, token usage breakdowns, model usage charts (ASCII), fun factoids comparing usage to books/movies, and ANSI clipboard copy support.

### Types

| Type | Description |
|---|---|
| `StatsResult` | `{type:'success', data:ClaudeCodeStats}` \| `{type:'error', message:string}` \| `{type:'empty'}` |
| `StatsContentProps` | `{allTimePromise:Promise<StatsResult>, onClose}` |
| `ModelEntryProps` | `{model:string, usage:{inputTokens,outputTokens,cacheReadInputTokens}, totalTokens:number}` |
| `ChartLegend` | `{model:string, coloredBullet:string}` |
| `ChartOutput` | `{chart:string, legend:ChartLegend[], xAxisLabels:string}` |

### Functions

- **`formatPeakDay(dateStr)`** — Formats a date string as `"Mon DD"`.
- **`getNextDateRange(current)`** — Cycles through `['all', '7d', '30d']`.
- **`createAllTimeStatsPromise()`** — Wraps `aggregateClaudeCodeStatsForRange('all')` in a never-rejecting promise.

### Component: `Stats` (exported)

Simple wrapper; creates the all-time promise at mount time, renders `<Suspense>` with `<StatsContent>`.

### Component: `StatsContent`

Core stats panel. Uses React 19's `use(allTimePromise)` to suspend. State:

| State | Type | Purpose |
|---|---|---|
| `dateRange` | `StatsDateRange` | Current date filter (`all`/`7d`/`30d`) |
| `statsCache` | `Record<StatsDateRange, ClaudeCodeStats>` | Lazy-load cache for non-"all" ranges |
| `isLoadingFiltered` | `boolean` | Loading indicator for date-range switch |
| `activeTab` | `"Overview"\|"Models"` | Tab selection |
| `copyStatus` | `string\|null` | "copying..." / "copied!" / "copy failed" |

**Keybindings**:
- `r` → Cycle date range
- `Ctrl+S` → Screenshot (copy ANSI to clipboard)
- `Tab` → Switch tab
- `Esc`/`Ctrl+C`/`Ctrl+D` → Close

**Renders two tabs** via `<Tabs>`: `<OverviewTab>` and `<ModelsTab>`.

### Component: `OverviewTab`

Displays in a 2-column grid:
- **Activity heatmap** (always all-time, via `generateHeatmap`)
- **Date range selector** (`<DateRangeSelector>`)
- **Favorite model** (most tokens used), **Total tokens**
- **Sessions** count
- **Longest session** (with `formatDuration`)
- **Active days** (X/total days)
- **Longest streak** / **Current streak**
- **Most active day** (`formatPeakDay`)
- **Speculation time saved** (ant-only, gated by `"external" === 'ant'`)
- **Shot distribution** (ant-only, gated by `feature('SHOT_STATS')`): 1-shot, 2-5 shot, 6-10 shot, 11+ shot buckets with counts and percentages, plus average shots/session
- **Fun factoid**: Randomly selected comparison to books (`BOOK_COMPARISONS`, 24 entries from The Little Prince at 22K tokens to War and Peace at 730K tokens) or time comparisons (`TIME_COMPARISONS`, 10 entries from a TED talk at 18 min to a full night of sleep at 480 min)

### Component: `ModelsTab`

- **Tokens per Day** ASCII chart (via `asciichart`) for top 3 models
- **Date range selector**
- **Model entries** in 2 columns (36 chars each), scrollable with ↑↓ (offsets by 2)
- **Scroll hint** showing "X-Y of N models (↑↓ to scroll)"

### Component: `DateRangeSelector`

Renders "All time · Last 7 days · Last 30 days" with the active one bolded in Claude color, plus a `<Spinner>` while loading.

### Component: `ModelEntry`

Renders a single model row: bullet icon, bolded model name (via `renderModelName`), percentage, and "In: N · Out: N" on a subtler line.

### Token Chart (`generateTokenChart`)

- Takes `DailyModelTokens[]`, model names, terminal width
- Distributes data across chart width (max 52 columns)
- Uses asciichart with 8-row height, theme-colored, with labels formatted as "k"/"M"
- X-axis date labels via `generateXAxisLabels`

### Book/Time Comparisons

- **`BOOK_COMPARISONS`**: 24 famous books with approximate token counts
- **`TIME_COMPARISONS`**: 10 time-based comparisons (TED talk, The Office episode, yoga class, World Cup match, Inception, Titanic, transatlantic flight, full night of sleep)
- **`generateFunFactoid(stats, totalTokens)`**: Builds factoid strings like "You've used ~3x more tokens than The Great Gatsby" or "Your longest session is ~2x longer than a yoga class", then picks one randomly.

### Screenshot System

- **`handleScreenshot(stats, activeTab, setStatus)`**: Renders stats to ANSI string, copies via `copyAnsiToClipboard`.
- **`renderStatsToAnsi(stats, activeTab)`**: Dispatches to `renderOverviewToAnsi` or `renderModelsToAnsi`, right-aligns "/stats" label.
- **`renderOverviewToAnsi(stats)`**: Two-column fixed-width layout (COL1=18, COL2_START=40, COL2_LABEL=18) with heatmap, model info, session info, streaks, active days, peak hour, shot stats, fun factoid.
- **`renderModelsToAnsi(stats)`**: ASCII chart + top-3 model breakdown.

---

## File 3: `ConsoleOAuthFlow.tsx` (631 lines)

Full OAuth login flow supporting three login methods: Claude subscription (claude.ai), Anthropic Console (API billing), and third-party platforms (Bedrock/Vertex/Foundry). Features browser-open + manual paste-code fallback.

### Types

| Type | Description |
|---|---|
| `Props` | `{onDone, startingMessage?, mode?:'login'\|'setup-token', forceLoginMethod?:'claudeai'\|'console'}` |
| `OAuthStatus` | Union of 8 states: `idle`, `platform_setup`, `ready_to_start`, `waiting_for_login` (with url), `creating_api_key`, `about_to_retry` (with nextState), `success` (with optional token), `error` (with message and optional toRetry) |
| `OAuthStatusMessageProps` | 15 props for the child status renderer |

### Component: `ConsoleOAuthFlow` (exported)

The main orchestrator. State:

| State | Type | Purpose |
|---|---|---|
| `oauthStatus` | `OAuthStatus` | Current state machine state |
| `pastedCode` | `string` | Manual paste-code input |
| `cursorOffset` | `number` | Cursor position in paste input |
| `oauthService` | `OAuthService` | OAuth service instance (created once) |
| `loginWithClaudeAi` | `boolean` | Whether using Claude AI auth (vs Console) |
| `showPastePrompt` | `boolean` | Show paste-code fallback after 3s timeout |
| `urlCopied` | `boolean` | Flash "Copied!" indicator |

**State machine flow**:
1. `idle` → User selects login method (`claudeai`/`console`/`platform`)
2. `platform_setup` → Shows documentation links for Bedrock/Vertex/Foundry
3. `ready_to_start` → Automatically triggers `startOAuth()` on next tick
4. `waiting_for_login` → Browser opened; after 3s, shows URL + paste prompt
5. `creating_api_key` → Got access token, creating API key (semi-transient)
6. `success` → Login complete; auto-exits for `setup-token` mode
7. `error` → Shows error; offers retry or Enter to go back
8. `about_to_retry` → 1s delay before retrying

**Paste-code flow**: Pressing `c` in paste prompt copies URL to clipboard. Submitting code parses `authorizationCode#state` format, calls `oauthService.handleManualAuthCodeInput()`.

**`startOAuth()`**: Calls `oauthService.startOAuthFlow()` with a callback that transitions to `waiting_for_login`. Handles token exchange errors (with SSL error hints for enterprise TLS proxies). For `setup-token` mode, displays the raw access token for manual `CLAUDE_CODE_OAUTH_TOKEN` env var usage.

**Keybindings**:
- `Enter` on success → Done (fires `tengu_oauth_success` analytics)
- `Enter` on platform_setup → Back to idle
- `Enter` on error with retry → Retry after 1s delay

### Component: `OAuthStatusMessage`

Large switch-case renderer for each `oauthStatus.state`:

| State | Render |
|---|---|
| `idle` | Login method selector (`<Select>`) with 3 options: Claude subscription, Console, 3rd-party platform |
| `platform_setup` | Documentation links for Bedrock, Foundry, Vertex AI |
| `ready_to_start` | "Starting OAuth flow..." with spinner |
| `waiting_for_login` | Forced method message, spinner/"Opening browser", paste-code `<TextInput>` with masked display |
| `creating_api_key` | "Creating API key..." with spinner |
| `about_to_retry` | "Retrying..." in permission color |
| `success` | Email + "Login successful. Press Enter to continue" (or null for setup-token) |
| `error` | Error message + "Press Enter to retry" if retryable |

---

## File 4: `ContextVisualization.tsx` (489 lines)

Context usage visualization panel showing token breakdown by category, MCP tools, custom agents, memory files, skills, and a grid diagram. Called from `/context` or context status UI.

### Types

| Type | Description |
|---|---|
| `Props` | `{data: ContextData}` |

### Functions

- **`CollapseStatus()`** — Feature-gated (`CONTEXT_COLLAPSE`). Shows a one-liner summarizing context-collapse activity: collapsed spans, staged spans, total spawns, errors, empty-spawn warnings.
- **`groupBySource<T extends {source, tokens}>(items)`** — Groups items by source display name, sorts each group by tokens descending, returns in `SOURCE_DISPLAY_ORDER` (`['Project', 'User', 'Managed', 'Plugin', 'Built-in']`).

### Component: `ContextVisualization` (exported)

Extracts from `data`: `categories`, `totalTokens`, `rawMaxTokens`, `percentage`, `gridRows`, `model`, `memoryFiles`, `mcpTools`, `deferredBuiltinTools`, `systemTools`, `systemPromptSections`, `agents`, `skills`, `messageBreakdown`.

**Sections rendered** (top to bottom):

1. **Header**: `"Context Usage"` title
2. **Grid diagram**: Rows of colored squares representing category fill levels (`▱` = <70%, `▲` = >=70%, `⛝` = reserved, `⛶` = free space)
3. **Summary line**: `"Model · X/Y tokens (Z%)"` + `<CollapseStatus>` + `"Estimated usage by category"`
4. **Category breakdown**: Each category with its symbol, name, tokens, and percentage (N/A for deferred)
5. **Free space line** (if any)
6. **Autocompact buffer line** (if any)
7. **MCP tools section**: Loaded and available (on-demand) lists with per-tool token counts
8. **System tools** (ant-only, gated by `false`)
9. **System prompt sections** (ant-only, gated by `false`)
10. **Custom agents**: Grouped by source (Project/User/Managed/Plugin/Built-in), each showing agent type and tokens
11. **Memory files**: Per-file path and tokens
12. **Skills**: Grouped by source, each showing skill name and tokens
13. **Message breakdown** (ant-only, gated by `false`): Tool calls, tool results, attachments, assistant messages, user messages, top tools (top 5), top attachments (top 5)
14. **Context suggestions**: Via `generateContextSuggestions(data)` rendered in `<ContextSuggestions>`

---

## File 5: `TaskListV2.tsx` (378 lines)

Todo/task list panel showing running, queued, and completed tasks with progress indicators, owner attribution, agent team context, and truncation for space-constrained terminals.

### Types

| Type | Description |
|---|---|
| `Props` | `{tasks:Task[], isStandalone?:boolean}` |
| `TaskItemProps` | `{task, ownerColor?, openBlockers:string[], activity?:string, ownerActive:boolean, columns:number}` |

### Constants

| Constant | Value | Purpose |
|---|---|---|
| `RECENT_COMPLETED_TTL_MS` | 30000 | How long a completed task remains "recent" (30s) |

### Functions

- **`byIdAsc(a, b)`** — Numeric ID comparison for sorting (parses IDs as ints, falls back to localeCompare).
- **`getTaskIcon(status)`** — Returns icon (`✓`/`◼`/`□`) and theme color for each status.

### Component: `TaskListV2` (exported)

Checks `isTodoV2Enabled()` feature flag; returns null if disabled or empty.

**Data flow**:
1. Reads `teamContext` and `appStateTasks` from `useAppState`
2. Builds `teammateColors` map: agent color name → theme color (via `AGENT_COLOR_TO_THEME_COLOR`)
3. Builds `teammateActivity` map: agent name/ID → current activity description (from `progress.recentActivities` summarized via `summarizeRecentActivities`)
4. Tracks `activeTeammates` set for running agents
5. Computes `completedCount`, `pendingCount`, `inProgressCount`, `unresolvedTaskIds`

**Truncation logic** (when `tasks.length > maxDisplay`):
- Priority order: recently completed (<30s) → in-progress → pending → older completed
- Pending tasks sorted with blocked tasks at the end
- Hidden tasks summarized as "… +N in progress, M pending, K completed"

**Rendering**:
- `isStandalone` mode: Shows header line "N tasks (M done, K in progress, P open)" + content
- Inline mode: Just the content
- Each `<TaskItem>` with icon, subject (bold/italic depending on status), owner `@name` (in team color if available), blocked-by info, and activity description

### Component: `TaskItem`

Renders a single task row:
- Status icon (colored) + subject text (bold for in-progress, strikethrough for completed, dimmed for blocked)
- Owner tag `(@name)` shown when `columns >= 60` and owner is active
- Blocked-by: `→ blocked by #ID, #ID`
- Activity line: current teammate activity with ellipsis

---

## File 6: `GlobalSearchDialog.tsx` (343 lines)

Ctrl+Shift+F global search dialog. Uses ripgrep streaming with debounced queries, file preview with syntax highlighting, and both "open in editor" and "mention" insert modes.

### Types

| Type | Description |
|---|---|
| `Props` | `{onDone, onInsert}` |
| `Match` | `{file:string, line:number, text:string}` |

### Constants

| Constant | Value | Purpose |
|---|---|---|
| `VISIBLE_RESULTS` | 12 | Max visible FuzzyPicker items |
| `DEBOUNCE_MS` | 100 | Ripgrep debounce |
| `PREVIEW_CONTEXT_LINES` | 4 | Lines before/after match in preview |
| `MAX_MATCHES_PER_FILE` | 10 | rg `-m` cap per file |
| `MAX_TOTAL_MATCHES` | 500 | Global result cap |

### Component: `GlobalSearchDialog` (exported)

State:

| State | Type | Purpose |
|---|---|---|
| `matches` | `Match[]` | Accumulated ripgrep results |
| `truncated` | `boolean` | Whether results hit `MAX_TOTAL_MATCHES` |
| `isSearching` | `boolean` | Search-in-progress indicator |
| `query` | `string` | Current search text |
| `focused` | `Match\|undefined` | Currently focused result |
| `preview` | `{file,line,content}\|null` | File preview content |

**Search flow** (`handleQueryChange`):
1. Sets query immediately, aborts previous search
2. If query is empty → clear results
3. Otherwise: filter existing results client-side, then schedule ripgrep stream after 100ms debounce
4. Ripgrep runs with `-n --no-heading -i -m 10 -F -e <query>`
5. Stream callback: parse each line via `parseRipgrepLine()`, deduplicate via `matchKey()`, accumulate (cap at 500), truncate if exceeded, clear on error/empty

**Preview**: When focus changes, reads file content via `readFileInRange()` with context lines, renders syntax-highlighted preview

**Renders `<FuzzyPicker>`** with:
- Two actions: Tab=mention (`@file#LN`), Shift+Tab=insert path (`file:line`)
- Empty message: "Type to search..." / "Searching..." / "No matches"
- Match label: "N+ matches…" (with truncation indicator)
- Preview positioned right (wide terminals >=140 cols) or bottom

### Function: `parseRipgrepLine(line)` (exported for testing)

Parses `"path:line:text"` format. Uses regex `/^(.*?):(\d+):(.*)$/` to handle Windows drive-letter paths (`C:\...`). Returns `{file, line, text}` or null.

---

## File 7: `RemoteEnvironmentDialog.tsx` (340 lines)

Remote environment selection/configuration dialog. Fetches available environments (teleport), shows current selection with source info, allows changing the default.

### Types

| Type | Description |
|---|---|
| `Props` | `{onDone}` |
| `LoadingState` | `'loading' \| 'updating' \| null` |

### Component: `RemoteEnvironmentDialog` (exported)

State:

| State | Type | Purpose |
|---|---|---|
| `loadingState` | `LoadingState` | Loading/updating indicator |
| `environments` | `EnvironmentResource[]` | Available environments |
| `selectedEnvironment` | `EnvironmentResource\|null` | Currently active |
| `selectedEnvironmentSource` | `SettingSource\|null` | Source of the setting |
| `error` | `string\|null` | Error message |

**Data flow**: On mount, calls `getEnvironmentSelectionInfo()` which returns available environments + selected + source. Writes selection to `updateSettingsForSource('localSettings', {remote: {defaultEnvironmentId}})`.

**Rendering branches**:
1. `loadingState === 'loading'` → `<LoadingState>` in `<Dialog>`
2. `error` → Error text in `<Dialog>`
3. `!selectedEnvironment` → "No remote environments available" in `<Dialog>` with setup hint URL
4. Single environment → `<SingleEnvironmentContent>`: just the name + Enter to confirm
5. Multiple → `<MultipleEnvironmentsContent>`: `<Select>` with all options, current selection shown as subtitle

### Helper Components

- **`EnvironmentLabel`**: `✓ Using <bold name> (environment_id)`
- **`SingleEnvironmentContent`**: Dialog wrapping `EnvironmentLabel`, Enter to confirm
- **`MultipleEnvironmentsContent`**: Dialog with current selection subtitle, `<Select>` options, `<Byline>` hint, setup hint URL

---

## File 8: `ResumeTask.tsx` (268 lines)

Resume-task picker for teleport sessions. Fetches code sessions from the Sessions API, filters by current repository, and presents a selectable list.

### Types

| Type | Description |
|---|---|
| `Props` | `{onSelect:(session:CodeSession)=>void, onCancel, isEmbedded?:boolean}` |
| `LoadErrorType` | `'network' \| 'auth' \| 'api' \| 'other'` |

### Component: `ResumeTask` (exported)

State:

| State | Type | Purpose |
|---|---|---|
| `sessions` | `CodeSession[]` | Loaded sessions |
| `currentRepo` | `string\|null` | Detected repository |
| `loading` | `boolean` | Loading indicator |
| `loadErrorType` | `LoadErrorType\|null` | Error category |
| `retrying` | `boolean` | Retry-in-progress |
| `hasCompletedTeleportErrorFlow` | `boolean` | Gate for `<TeleportError>` |
| `focusedIndex` | `number` | For "N of M" scroll indicator |

**Data flow** (`loadSessions`):
1. Detects current repository via `detectCurrentRepository()`
2. Fetches sessions via `fetchCodeSessionsFromSessionsAPI()`
3. Filters by repo (`session.repo.owner.login/session.repo.name === detectedRepo`)
4. Sorts by `updated_at` descending

**Rendering branches**:
1. `!hasCompletedTeleportErrorFlow` → `<TeleportError>` (first-run check)
2. `loading` → Spinner + "Loading Claude Code sessions..."
3. `loadErrorType` → Error message with type-specific guidance (network/auth/api/other)
4. `sessions.length === 0` → "No Claude Code sessions found"
5. Normal → Session list with `<Select>`, padded timestamps, scroll position indicator

### Helper Functions

- **`determineErrorType(errorMessage)`** — Classifies errors by keyword matching: `fetch/network/timeout` → network, `auth/token/permission/oauth/403` → auth, `api/rate limit/500/529` → api, else other.
- **`renderErrorSpecificGuidance(errorType)`** — Renders type-specific troubleshooting: network → "Check your internet connection", auth → "Run /login", api → "Sorry, Claude encountered an error", other → "Sorry, Claude Code encountered an error"

---

## File 9: `QuickOpenDialog.tsx` (244 lines)

Ctrl+Shift+P fuzzy file finder. Uses `generateFileSuggestions()` for file discovery, `readFileInRange()` for syntax-highlighted preview, and `FuzzyPicker` for the selection UI.

### Types

| Type | Description |
|---|---|
| `Props` | `{onDone, onInsert}` |

### Constants

| Constant | Value | Purpose |
|---|---|---|
| `VISIBLE_RESULTS` | 8 | Max visible files |
| `PREVIEW_LINES` | 20 | Lines in file preview |

### Component: `QuickOpenDialog` (exported)

State:

| State | Type | Purpose |
|---|---|---|
| `results` | `string[]` | Filtered file paths |
| `query` | `string` | Current search text |
| `focusedPath` | `string\|undefined` | Currently focused file |
| `preview` | `{path,content}\|null` | File content preview |

**Query flow** (`handleQueryChange`):
1. Sets query, increments generation counter
2. If empty → clear results
3. Calls `generateFileSuggestions(q, true)`, filters to file-only results, converts path separators to `/`
4. Stale-generation guard: drops results if a newer query started

**Preview**: On focus change, reads file via `readFileInRange` with `PREVIEW_LINES` lines, renders with syntax highlighting. If the preview doesn't match the focused path, shows "· loading..."

**Renders `<FuzzyPicker>`** with:
- Tab=mention (`@file`), Shift+Tab=insert path
- Preview: Right (wide terminals >=120 cols) or bottom
- Empty message: "No matching files" / "Start typing to search..."

---

## File 10: `Onboarding.tsx` (244 lines)

Multi-step onboarding wizard shown on first run. Guides users through preflight checks, theme selection, OAuth login, API key approval, security notes, and terminal setup.

### Types

| Type | Description |
|---|---|
| `StepId` | `'preflight' \| 'theme' \| 'oauth' \| 'api-key' \| 'security' \| 'terminal-setup'` |
| `OnboardingStep` | `{id:StepId, component:ReactNode}` |
| `Props` | `{onDone}` |

### Component: `Onboarding` (exported)

State:

| State | Type | Purpose |
|---|---|---|
| `currentStepIndex` | `number` | Current wizard step |
| `skipOAuth` | `boolean` | Skip OAuth (if custom API key approved) |
| `oauthEnabled` | `boolean` | Whether Anthropic auth is available |

**Step construction** (conditional assembly):
1. `preflight` — Only if `oauthEnabled` (gated behind auth)
2. `theme` — Always present (`<ThemePicker>`)
3. `api-key` — Only if `ANTHROPIC_API_KEY` is set and has `'new'` custom status
4. `oauth` — Only if `oauthEnabled` and not skipped; wrapped in `<SkippableStep>`
5. `security` — Always present (security notes with `OrderedList`)
6. `terminal-setup` — Only if `shouldOfferTerminalSetup()` returns true

**Navigation**: `goToNextStep()` increments index or calls `onDone()` at the end. Each step fires `tengu_onboarding_step` analytics.

**Keybindings**:
- Enter on security step → continue
- Esc on terminal-setup step → skip

### Component: `SkippableStep`

If `skip` prop is true, calls `onSkip()` on mount and renders null, otherwise renders children. Used to auto-skip OAuth when a custom API key was approved.

### Terminal Setup Step

Offers two options: "Yes, use recommended settings" or "No, maybe later". On yes, calls `setupTerminal(theme)` (with OS-specific instructions: Option+Enter for Apple Terminal, Shift+Enter for others). Shows `exitState` info (press Ctrl+C again to exit if pending).

---

## File 11: `MCPServerDesktopImportDialog.tsx` (203 lines)

Imports MCP server configurations from the Claude Desktop app. Features multi-select, collision detection, and automatic numbered-suffix fallback for conflicts.

### Types

| Type | Description |
|---|---|
| `Props` | `{servers:Record<string,McpServerConfig>, scope:ConfigScope, onDone}` |

### Component: `MCPServerDesktopImportDialog` (exported)

State:

| State | Type | Purpose |
|---|---|---|
| `existingServers` | `Record<string,ScopedMcpServerConfig>` | Already-configured servers (to detect collisions) |

**Data flow**:
1. On mount, loads existing MCP configs via `getAllMcpConfigs()`
2. Computes `collisions`: server names that already exist in config
3. Builds `<SelectMulti>` options with "(already exists)" suffixes for collisions
4. Default selection: all non-colliding servers pre-selected

**Submission** (`onSubmit`):
1. Iterates selected servers
2. For each collision, finds the next available numbered suffix (`serverName_N`)
3. Calls `addMcpConfig(finalName, serverConfig, scope)`
4. On completion, writes success/failure message to stdout via `writeToStdout()` and calls `gracefulShutdown()`

**Renders `<Dialog>`** with:
- Title: "Import MCP Servers from Claude Desktop"
- Subtitle: "Found N MCP servers in Claude Desktop"
- Warning: if collisions exist, "Some servers already exist... imported with numbered suffix"
- `<SelectMulti>` for selection
- `<Byline>` with Space/Enter/Esc hints

---

## File 12: `DesktopHandoff.tsx` (193 lines)

Session transfer to the Claude Desktop app. Detects installation status, prompts download when missing, flushes session storage, and opens the current session in Desktop via deep link.

### Types

| Type | Description |
|---|---|
| `DesktopHandoffState` | `'checking' \| 'prompt-download' \| 'flushing' \| 'opening' \| 'success' \| 'error'` |
| `Props` | `{onDone}` |

### Component: `DesktopHandoff` (exported)

State:

| State | Type | Purpose |
|---|---|---|
| `state` | `DesktopHandoffState` | Current handoff state |
| `error` | `string\|null` | Error message (for error state) |
| `downloadMessage` | `string` | Download prompt message (for prompt-download state) |

**State machine** (`performHandoff`):
1. `checking` → Calls `getDesktopInstallStatus()`
2. `not-installed` → `prompt-download` with "Claude Desktop is not installed"
3. `version-too-old` → `prompt-download` with version info
4. Installed → `flushing` → `flushSessionStorage()` → `opening` → `openCurrentSessionInDesktop()`
5. Success → `success` → Delayed `onDone()` after 500ms
6. Failure → `error`

**Input handling** (via `useInput`):
- `prompt-download` state: `y`/`Y` → opens browser to download URL, `n`/`N` → cancels with docs link
- `error` state: any key → dismisses

**Rendering**:
- `error` → Error message + "Press any key to continue..."
- `prompt-download` → Download message + "Download now? (y/n)"
- Other states → `<LoadingState>` with contextual message from `messages` map

### Function: `getDownloadUrl()`

Returns platform-specific download URL: `win32` → Windows x64 exe, default → macOS universal dmg.

---

## File 13: `messageActions.tsx` (450 lines)

Message selection/action system. Defines navigable message types, action definitions (copy, edit, expand, copy-tool-input), keybinding dispatch, and the action bar renderer.

### Types

| Type | Description |
|---|---|
| `NavigableType` | `'user' \| 'assistant' \| 'grouped_tool_use' \| 'collapsed_read_search' \| 'system' \| 'attachment'` |
| `NavigableOf<T>` | Extract from `RenderableMessage` by type |
| `NavigableMessage` | Alias for `RenderableMessage` |
| `PrimaryInput` | `{label:string, extract:(input)=>string\|undefined}` |
| `MessageActionCaps` | `{copy:(text)=>void, edit:(msg)=>Promise<void>}` |
| `MessageActionsState` | `{uuid, msgType, expanded, toolName?}` |
| `MessageActionsNav` | `{enterCursor, navigatePrev, navigateNext, navigatePrevUser, navigateNextUser, navigateTop, navigateBottom, getSelected}` |

### Functions

- **`isNavigableMessage(msg)`** — Tier-2 blocklist for actionable messages:
  - `assistant`: Text responses (non-empty, non-synthetic) or tool calls with extractable `PRIMARY_INPUT`
  - `user`: Non-meta, non-compact-summary, non-synthetic, non-XML-wrapped
  - `system`: Blocks `api_metrics`, `stop_hook_summary`, `turn_duration`, `memory_saved`, `agents_killed`, `away_summary`, `thinking` subtypes; others are navigable
  - `grouped_tool_use` / `collapsed_read_search`: Always navigable
  - `attachment`: Only navigable for `queued_command`, `diagnostics`, `hook_blocking_error`, `hook_error_during_execution`

- **`toolCallOf(msg)`** — Extracts tool call `{name, input}` from assistant or grouped_tool_use messages.

- **`stripSystemReminders(text)`** — Removes leading `<system-reminder>...</system-reminder>` blocks.

- **`copyTextOf(msg)`** — Extracts copyable text from any navigable message type:
  - `user`: Strips system reminders
  - `assistant`: Text content or tool primary input
  - `grouped_tool_use`: Joined tool results
  - `collapsed_read_search`: Joined tool results from all sub-messages
  - `system`: Content, error string, or subtype
  - `attachment`: Queued command prompt text or `[type]` fallback

- **`toolResultText(r)`** — Extracts text from a tool_result content block.

- **`action()`** — Identity builder that preserves tuple types for action definitions.

### Constants

- **`NAVIGABLE_TYPES`**: `['user', 'assistant', 'grouped_tool_use', 'collapsed_read_search', 'system', 'attachment']`
- **`PRIMARY_INPUT`**: Maps tool names to their primary input extractors:
  - `Read/Edit/Write`: `file_path`
  - `NotebookEdit`: `notebook_path`
  - `Bash`: `command`
  - `Grep/Glob`: `pattern`
  - `WebFetch`: `url`
  - `WebSearch`: `query`
  - `Task/Agent`: `prompt`
  - `Tmux`: `"tmux " + args.join(' ')`

- **`MESSAGE_ACTIONS`**: Array of 4 action definitions:
  1. `enter` → expand/collapse (grouped_tool_use, collapsed_read_search, attachment, system), `stays:true`
  2. `enter` → edit (user)
  3. `c` → copy (all types)
  4. `p` → copy primary input (grouped_tool_use, assistant), conditional on `toolName in PRIMARY_INPUT`

### Hooks

- **`useSelectedMessageBg()`** — Returns `"messageActionsBackground"` if inside `MessageActionsSelectedContext`, else `undefined`.

- **`useMessageActions(cursor, setCursor, navRef, caps)`** — Returns `{enter, handlers}`:
  - `enter`: Calls `navRef.current.enterCursor()`, logs analytics
  - `handlers`: Generated per-action keybinding handlers (`messageActions:prev`, `messageActions:next`, `messageActions:prevUser`, `messageActions:nextUser`, `messageActions:top`, `messageActions:bottom`, `messageActions:escape`, `messageActions:ctrlc`, plus one per distinct action key)

### Components

- **`MessageActionsKeybindings`** — Mounts `useKeybindings(handlers, {context:'MessageActions', isActive})`. Must be inside `<KeybindingSetup>`.

- **`MessageActionsBar`** — Renders the cursor action bar:
  - Filters `MESSAGE_ACTIONS` to applicable actions for current cursor state
  - Renders each as `<key> <label>` with dot separators
  - Appends `↑↓ navigate · esc back`
  - Top border only (matches PromptInput's ─── line)

### Contexts

- **`MessageActionsSelectedContext`** — `React.createContext(false)`. Indicates a message is the currently selected one.
- **`InVirtualListContext`** — `React.createContext(false)`. Indicates rendering inside `VirtualMessageList`.

---

## File 14: `Messages.tsx` (834 lines)

The main messages list component. Normalizes, filters, groups, and collapses messages; handles streaming thinking/tool use, unseen dividers, sticky prompts, and virtual list integration.

### Types

| Type | Description |
|---|---|
| `Props` | 25+ props including messages, tools, commands, verbose, streaming state, fullscreen config, search config, cursor state, renderRange |
| `SliceAnchor` | `{uuid:string, idx:number} \| null` |

### Constants

| Constant | Value | Purpose |
|---|---|---|
| `MAX_MESSAGES_TO_SHOW_IN_TRANSCRIPT_MODE` | 30 | Truncation cap for ctrl+o |
| `MAX_MESSAGES_WITHOUT_VIRTUALIZATION` | 200 | Safety cap for non-virtualized rendering |
| `MESSAGE_CAP_STEP` | 50 | How far past cap before advancing the slice window |

### Component: `LogoHeader`

Memoed (`React.memo`) component that renders `<LogoV2>` + `<StatusNotices>` wrapped in `<OffscreenFreeze>`. Memoed on `agentDefinitions` so new messages arrays don't invalidate the logo subtree.

### Functions

- **`filterForBriefTool(messages, briefToolNames)`** — Filters to Brief tool_use blocks, their tool_results, real user input, and queued_command attachments with `commandMode==='prompt'`. Drops assistant text.
- **`dropTextInBriefTurns(messages, briefToolNames)`** — Two-pass filter: finds turns containing Brief tool_use, then drops assistant text blocks from those turns only.
- **`computeSliceStart(collapsed, anchorRef, cap?, step?)`** — UUID-anchored slicing for non-virtualized cap. Uses stored `{uuid, idx}` anchor; falls back to idx if uuid vanished (collapse regrouping changes uuids). Advances the window when `collapsed.length - start > cap + step`.
- **`shouldRenderStatically(message, streamingToolUseIDs, ...)`** — Determines if a message is "final" (can render statically). Returns false for streaming tool uses, unresolved hooks, in-progress tool uses. Returns true for transcript mode, static text messages, fully resolved tool uses.
- **`expandKey(msg)`** — Returns `tool_use_id` for expandable messages (so tool_use + tool_result expand together), else `uuid`.

### Component: `MessagesImpl` (wrapped as `Messages` export)

**Memoized computations**:
1. `normalizedMessages`: `normalizeMessages(messages).filter(isNotEmptyMessage)`
2. `isStreamingThinkingVisible`: Streaming or within 30s timeout
3. `lastThinkingBlockId`: Last thinking block UUID:index for hiding past thinking in transcript mode. Returns `'streaming'` if streaming thinking visible, `'no-thinking'` if reached previous user turn.
4. `latestBashOutputUUID`: Last message with `<bash-stdout` or `<bash-stderr` content
5. `streamingToolUsesWithoutInProgress`: Streaming tool uses not yet in normalized messages or in-progress set
6. `syntheticStreamingToolUseMessages`: Streaming tool uses converted to normalized messages with deterministic UUIDs
7. `collapsed/lookups/hasTruncatedMessages/hiddenMessageCount`: The big O(n) transform:
   - Filter compact boundary (or include all for fullscreen/verbose)
   - Reorder, drop progress, filter null-rendering attachments
   - Apply brief-mode filtering (`filterForBriefTool` or `dropTextInBriefTurns`)
   - Truncate for transcript mode (last 30)
   - Apply grouping (tool use merging), then collapse passes (read/search, hook summaries, teammate shutdowns, background bash)
8. `renderableMessages`: Slice for render cap (non-virtualized path)
9. `dividerBeforeIndex`: First renderable message matching `unseenDivider.firstUnseenUuid`
10. `selectedIdx`: Index of cursor-selected message

**State**:
- `expandedKeys`: Set of expanded message keys (click-to-toggle verbose)
- `onItemClick`: Toggles expanded key
- `isItemExpanded`: Checks if key is in expanded set
- `isItemClickable`: True for collapsed_read_search, advisor tool results, or tool results with `isResultTruncated`

**`renderMessageRow`**: Creates `<MessageRow>` with full props including: isUserContinuation, hasContentAfter, verbose/expanded override, streaming IDs, lookups. Wraps in `<MessageActionsSelectedContext.Provider>`. Inserts unseen divider as a sibling `<Divider>` at `dividerBeforeIndex`.

**Terminal progress**: Reports 'indeterminate' when tools are in progress, 'completed' when done, via OSC 9;4.

**Rendering**:
- Logo (unless hidden or mid-export chunk)
- Truncation indicator (`"Ctrl+E to show N previous messages"`)
- Show-all indicator (in transcript mode)
- Messages: `<VirtualMessageList>` (fullscreen+virtual) or `flatMap(renderMessageRow)` (non-virtualized)
- Streaming text preview (green circle + `<StreamingMarkdown>`)
- Streaming thinking block

### React.memo Comparator

Custom comparator skips re-render when:
- `onOpenRateLimitOptions`, `scrollRef`, `trackStickyPrompt`, `setCursor`, `cursorNavRef`, `jumpRef`, `onSearchMatchesChange`, `scanElement`, `setPositions` changed (don't affect output)
- `streamingToolUses`: Only re-renders if contentBlock references changed
- `inProgressToolUseIDs`: Uses `setsEqual` comparison
- `unseenDivider`: Compares firstUnseenUuid and count
- `tools`: Compares tool names

---

## File 15: `VirtualMessageList.tsx` (1,082 lines)

Virtual-scrolling message list using Ink's `ScrollBox`. Implements sticky headers (pinned-prompt breadcrumb), pill messages, efficient rendering for large histories, full transcript search, cursor navigation, and per-message hover/click.

### Types

| Type | Description |
|---|---|
| `StickyPrompt` | `{text:string, scrollTo:()=>void} \| 'clicked'` |
| `JumpHandle` | Imperative handle: `jumpToIndex`, `setSearchQuery`, `nextMatch`, `prevMatch`, `setAnchor`, `warmSearchIndex`, `disarmSearch` |
| `Props` | 15+ props: messages, scrollRef, columns, itemKey, renderItem, onItemClick?, isItemClickable?, isItemExpanded?, extractSearchText?, trackStickyPrompt?, selectedIndex?, cursorNavRef?, setCursor?, jumpRef?, onSearchMatchesChange?, scanElement?, setPositions? |

### Constants

| Constant | Value | Purpose |
|---|---|---|
| `HEADROOM` | 3 | Rows above target when scrolling to |
| `STICKY_TEXT_CAP` | 500 | Max sticky header text length |

### Functions

- **`defaultExtractSearchText(msg)`** — Falls back to `renderableSearchText()` with a WeakMap cache.
- **`stickyPromptText(msg)`** — Returns the text of a real user prompt (via WeakMap cache), or null. Strips system reminders, excludes XML-wrapped payloads (`<bash-stdout>`, `<command-message>`), meta messages, and task-notification attachment prompts.
- **`computeStickyPromptText(msg)`** — Inner extraction: handles `user` (non-meta, text content) and `attachment` (queued_command, non-task-notification).

### Component: `VirtualItem`

Individual virtual-scroll item wrapper. Props: `itemKey, msg, idx, measureRef, expanded, hovered, clickable, onClickK, onEnterK, onLeaveK, renderItem`.

- Wraps `renderItem` in a `<Box>` with measurement ref, background color (grey when expanded or hovered), padding, and mouse event handlers
- NOT React.memo'd — renderItem captures changing state (cursor, selectedIdx, verbose); memoring would use stale closures

### Component: `VirtualMessageList` (exported)

**Incremental key array**: Appends new keys one-at-a-time during streaming; full rebuild on compaction, `/clear`, or itemKey change.

**Virtual scroll hook**: `useVirtualScroll(scrollRef, keys, columns)` returns `{range, topSpacer, bottomSpacer, measureRef, spacerRef, offsets, getItemTop, getItemElement, getItemHeight, scrollToIndex}`.

**Cursor navigation** (`useImperativeHandle(cursorNavRef)`):
- `enterCursor`: Scans backward from end for first user-typed message
- `navigatePrev/navigateNext`: Scans from `selectedIdx` in direction
- `navigatePrevUser/navigateNextUser`: User-type only
- `navigateTop/navigateBottom`: Scans from edges
- `getSelected`: Returns message at `selectedIdx`
- `isVisible` filter: height > 0 AND `isNavigableMessage`

**Search engine** (`useImperativeHandle(jumpRef)`):
- `setSearchQuery(q)`: Lowercases query, builds matches array (one per message) with prefix sums for global occurrence count, finds nearest message to scroll anchor, jumps to it
- `nextMatch/prevMatch`: Calls `step(1)` / `step(-1)`
- `setAnchor`: Captures current scrollTop
- `disarmSearch`: Clears positions (manual scroll invalidates)
- `warmSearchIndex`: Pre-computes `extractSearchText` for all messages in 500-message chunks with yield between chunks

**Two-phase jump + seek**:
1. `jump(i, wantLast)`: Clears positions, sets `scanRequestRef`, scrolls to target, bumps `seekGen`
2. Seek effect: Reads mounted element, `scanElement` → positions, `highlight(ord)`

**Highlight**: Computes screen-absolute position from message-relative + scrollViewport, highlights via `setPositions`, computes badge via prefix sum.

**Step**: Advances `screenOrd` within current message's positions. Exhausted → advances `ptr` to next matched message → jump → re-scan. Wraparound guard stops if all messages are phantoms (engine matched, render didn't).

**Phantom handling**: Up to 20 consecutive phantoms auto-advanced; resets on scan success.

**One-deep pending step queue**: n/N arriving mid-seek gets stored and fired after seek completes.

**Sorted by relevance**: `setSearchQuery` computes origin from `getItemTop(start) - offsets[start]`, then finds nearest match by `abs(origin + offset - scrollTop)`.

### Component: `StickyTracker`

Effect-only child (renders null) that tracks the last user prompt scrolled above the viewport. Uses fine-grained scroll subscription (unquantized) so it updates every wheel tick.

- Walks the mounted range backward to find `firstVisible` item below viewport top
- Walks further backward from `firstVisible` to find the first user prompt whose ❯ character is above the viewport
- Debounces via `lastIdx` ref and suppression state machine (`'none' → 'armed' → 'force'`)
- Click handler: Sets `'clicked'` sentinel → scrolls to prompt element (or estimate if unmounted)
- Correction effect: Re-anchors after click-jump to unmounted items (up to 5 retries)
- Text collapsed to first paragraph only, capped at `STICKY_TEXT_CAP`, whitespace normalized

---

## File 16: `FullscreenLayout.tsx` (637 lines)

Core fullscreen layout engine. Wraps the REPL with a sticky ScrollBox, floating "N new" pill, modal pane overlay (for slash-command dialogs), sticky prompt header, suggestion/dialog overlays, and scroll-freeze optimization.

### Types

| Type | Description |
|---|---|
| `Props` | `{scrollable, bottom, overlay?, bottomFloat?, modal?, modalScrollRef?, scrollRef?, dividerYRef?, hidePill?, hideSticky?, newMessageCount?, onPillClick?}` |
| `UnseenDivider` | `{firstUnseenUuid, count}` |

### Constants

| Constant | Value | Purpose |
|---|---|---|
| `MODAL_TRANSCRIPT_PEEK` | 2 | Rows of transcript visible above modal |

### Context

- **`ScrollChromeContext`**: `createContext<{setStickyPrompt}>({setStickyPrompt:()=>{}})`. Used by `StickyTracker` in `VirtualMessageList` to communicate upward without threading callbacks through REPL.

### Hook: `useUnseenDivider(messageCount)`

Tracks in-transcript "N new messages" divider position:

- **State**: `dividerIndex` (message count at first scroll-away snapshot)
- **Refs**: `countRef` (live message count, written in render body), `dividerYRef` (scrollHeight snapshot, ref-only for synchronous read in `onScrollAway`)
- **`onScrollAway(handle)`**: Fires on every scroll action. Only snapshots on the FIRST break from sticky-bottom. Uses `pendingDelta` to account for accumulated scrollBy.
- **`onRepin()`**: Clears divider index. The useEffect defers clearing `dividerYRef` so racing wheel events don't see null.
- **`jumpToNew(handle)`**: scrollToBottom (not scrollTo) to preserve stickyScroll.
- **`shiftDivider(indexDelta, heightDelta)`**: Adjusts divider when messages are prepended (infinite scroll-back).
- Returns `{dividerIndex, dividerYRef, onScrollAway, onRepin, jumpToNew, shiftDivider}`.

### Functions

- **`countUnseenAssistantTurns(messages, dividerIndex)`** — Counts assistant turns below divider, skipping progress and tool-use-only assistant entries.
- **`assistantHasVisibleText(m)`** — Checks if assistant message has non-empty text blocks.
- **`computeUnseenDivider(messages, dividerIndex)`** — Builds `{firstUnseenUuid, count}`. Skips progress and null-rendering attachments. Count floors at 1.

### Layout Effect

On mount (fullscreen only), wires Ink's `onHyperlinkClick` to handle `file://` and `https://` URLs:
- `file://` → `openPath(fileURLToPath(url))`
- Other → `openBrowser(url)`

### Component: `FullscreenLayout` (exported)

**Fullscreen mode** (when `isFullscreenEnvEnabled()`):
1. **Sticky prompt header**: Renders `<StickyPromptHeader>` when sticky != null and != 'clicked' and no overlay. Padding collapsed to 0 when sticky is active.
2. **ScrollBox**: `flexGrow={1}`, `stickyScroll={true}`, contains scrollable content + overlay
3. **"N new" pill** (`<NewMessagesPill>`): Visible when not hidden, pillVisible (viewport bottom < dividerY), and no overlay. Shows count or "Jump to bottom".
4. **Bottom float**: Absolute-positioned `bottomFloat` at bottom-right
5. **Bottom section**: `<SuggestionsOverlay>` + `<DialogOverlay>` portaled from PromptInput + actual bottom content (prompt input, spinner) with `maxHeight="50%"` and `overflowY="hidden"`
6. **Modal pane**: Absolute-positioned overlay with ▔ divider, paddingX=2, wrapping modal content in `<ModalContext>` with computed rows/columns
7. Everything wrapped in `<PromptOverlayProvider>`

**Main-screen mode** (fallback): Sequential rendering of `{scrollable}{bottom}{overlay}{modal}`.

**pillVisible**: Computed via `useSyncExternalStore` subscribing to ScrollBox changes, comparing `scrollTop + pendingDelta + viewportHeight < dividerY`.

### Component: `NewMessagesPill`

Slack-style pill at bottom of scroll area:
- Hoverable (background changes to `userMessageBackgroundHover`)
- Shows "Jump to bottom" (count=0) or "N new messages" with ↓ arrow
- Centered horizontally, absolute at bottom

### Component: `StickyPromptHeader`

Breadcrumb header for pinned prompt:
- Fixed height at 1 row (prevents ScrollBox shifting)
- `❯ prompt text` truncated-end
- Hoverable (background color change)
- Clickable → scrolls to prompt via `StickyPrompt.scrollTo`

### Component: `SuggestionsOverlay`

Portaled slash-command suggestions from PromptInput:
- Absolute position `bottom="100%"` (floats above prompt)
- Uses `<PromptInputFooterSuggestions>` with overlay=true
- Handles scroll-smear repair at Ink layer

### Component: `DialogOverlay`

Portaled dialog from PromptInput (e.g., AutoModeOptInDialog):
- Same absolute positioning as suggestions
- Renders after suggestions in tree order (paints over)
