# Utils Deep Dive - Part 1

Comprehensive analysis of six utility subsystems: Computer Use, Claude-in-Chrome, Deep Links, Native Installer, Telemetry, and Swarm Backends.

---

## Group 1: Computer Use System (`utils/computerUse/`)

**15 files | 1,560 total lines** — macOS remote desktop control via native modules.

### Architecture Overview

The computer use system allows Claude Code (a CLI) to control the user's macOS desktop: screenshots, mouse/keyboard input, clipboard, app management. It bridges two native modules (`@ant/computer-use-input` for enigo-based input, `@ant/computer-use-swift` for Swift-based screenshots/apps) through a CLI-specific executor, exposed as an MCP server.

**Key design decision — CLI deltas from the Electron desktop app (Cowork):**
- No `clickThrough` window exemption (no Electron window to exempt)
- Terminal as surrogate host for hide/activate logic
- Clipboard via `pbcopy`/`pbpaste` instead of Electron's clipboard module

---

### File-by-File Documentation

#### `common.ts` (61 lines)

**Exports:**
| Name | Kind | Signature |
|------|------|-----------|
| `COMPUTER_USE_MCP_SERVER_NAME` | const | `'computer-use'` (string) |
| `CLI_HOST_BUNDLE_ID` | const | `'com.anthropic.claude-code.cli-no-window'` — sentinel bundle ID that never matches a real frontmost app |
| `TERMINAL_BUNDLE_ID_FALLBACK` | const | `Readonly<Record<string, string>>` — maps terminal names to bundle IDs: `iTerm.app`, `Apple_Terminal`, `ghostty`, `kitty`, `WarpTerminal`, `vscode` |
| `getTerminalBundleId()` | function | `() => string \| null` — detects terminal emulator via `__CFBundleIdentifier` env var or fallback table |
| `CLI_CU_CAPABILITIES` | const | `{ screenshotFiltering: 'native', platform: 'darwin' }` |
| `isComputerUseMCPServer(name: string)` | function | `(name: string) => boolean` — checks if an MCP server name matches the CU server |

**Key logic:** `getTerminalBundleId` reads `process.env.__CFBundleIdentifier` first (exact bundle ID from LaunchServices), falls back to a static lookup table keyed by `env.terminal`.

---

#### `executor.ts` (658 lines)

The core factory that creates a `ComputerExecutor` instance implementing the `@ant/computer-use-mcp` interface.

**Exports:**
| Name | Kind | Signature |
|------|------|-----------|
| `createCliExecutor(opts)` | function | `(opts: { getMouseAnimationEnabled: () => boolean; getHideBeforeActionEnabled: () => boolean }) => ComputerExecutor` |
| `unhideComputerUseApps(bundleIds)` | function | `(bundleIds: readonly string[]) => Promise<void>` — fire-and-forget at turn end |

**Internal helpers (not exported):**

| Name | Signature | Description |
|------|-----------|-------------|
| `computeTargetDims(logicalW, logicalH, scaleFactor)` | `(number, number, number) => [number, number]` | Logical → physical → API target dims via `targetImageSize` |
| `readClipboardViaPbpaste()` | `() => Promise<string>` | Reads macOS clipboard via `pbpaste` subprocess |
| `writeClipboardViaPbcopy(text)` | `(string) => Promise<void>` | Writes macOS clipboard via `pbcopy` subprocess |
| `isBareEscape(parts)` | `(readonly string[]) => boolean` | Detects single-element escape/esc key press |
| `moveAndSettle(input, x, y)` | `(Input, number, number) => Promise<void>` | Instant move + 50ms HID round-trip settle |
| `releasePressed(input, pressed)` | `(Input, string[]) => Promise<void>` | Releases keys in reverse order, swallows errors |
| `withModifiers(input, mods, fn)` | `(Input, string[], () => Promise<T>) => Promise<T>` | Brackets `fn()` with modifier press/release |
| `typeViaClipboard(input, text)` | `(Input, string) => Promise<void>` | Save clipboard → write text → verify → Cmd+V → sleep 100ms → restore |
| `animatedMove(input, targetX, targetY, mouseAnimationEnabled)` | `(Input, number, number, boolean) => Promise<void>` | Ease-out-cubic at 60fps, 2000px/sec, capped 0.5s |

**Constants:**
- `SCREENSHOT_JPEG_QUALITY = 0.75`
- `MOVE_SETTLE_MS = 50`

**Type alias:**
- `Input = ReturnType<typeof requireComputerUseInput>`

**Executor methods returned by `createCliExecutor`:**

| Method | Parameters | Description |
|--------|-----------|-------------|
| `capabilities` | (getter) | Spreads `CLI_CU_CAPABILITIES` + `hostBundleId: CLI_HOST_BUNDLE_ID` |
| `prepareForAction(allowlistBundleIds, displayId?)` | `string[], number?` → `Promise<string[]>` | Hides non-allowlisted apps via Swift's `prepareDisplay`, wrapped in `drainRunLoop` |
| `previewHideSet(allowlistBundleIds, displayId?)` | `string[], number?` → `Promise<Array<{bundleId, displayName}>>` | Preview which apps would be hidden |
| `getDisplaySize(displayId?)` | `number?` → `Promise<DisplayGeometry>` | Gets display geometry from Swift |
| `listDisplays()` | `() => Promise<DisplayGeometry[]>` | Lists all displays |
| `findWindowDisplays(bundleIds)` | `string[]` → `Promise<Array<{bundleId, displayIds}>>` | Finds which displays have windows for given bundle IDs |
| `resolvePrepareCapture(opts)` | `{allowedBundleIds, preferredDisplayId?, autoResolve, doHide?}` → `Promise<ResolvePrepareCaptureResult>` | Pre-sizes screenshot, excludes terminal from allow list, wraps in `drainRunLoop` |
| `screenshot(opts)` | `{allowedBundleIds, displayId?}` → `Promise<ScreenshotResult>` | Captures display excluding terminal, pre-sized for API |
| `zoom(regionLogical, allowedBundleIds, displayId?)` | `{x,y,w,h}, string[], number?` → `Promise<{base64, width, height}>` | Region capture with output sizing |
| `key(keySequence, repeat?)` | `string, number?` → `Promise<void>` | xdotool-style key sequence, drainRunLoop wrapped, 8ms between repeats, Escape hole-punching |
| `holdKey(keyNames, durationMs)` | `string[], number` → `Promise<void>` | Press keys, sleep durationMs, release in finally, orphaned guard |
| `type(text, opts)` | `string, {viaClipboard: boolean}` → `Promise<void>` | Either clipboard paste or per-grapheme typeText |
| `readClipboard` | `() => Promise<string>` | Direct delegate to `readClipboardViaPbpaste` |
| `writeClipboard` | `(string) => Promise<void>` | Direct delegate to `writeClipboardViaPbcopy` |
| `moveMouse(x, y)` | `(number, number) => Promise<void>` | moveAndSettle |
| `click(x, y, button, count, modifiers?)` | `(number, number, 'left'\|'right'\|'middle', 1\|2\|3, string[]?)` → `Promise<void>` | Move + click with optional modifier bracket |
| `mouseDown()` | `() => Promise<void>` | Left button press |
| `mouseUp()` | `() => Promise<void>` | Left button release |
| `getCursorPosition()` | `() => Promise<{x, y}>` | Current mouse location |
| `drag(from?, to)` | `({x,y} \| undefined, {x,y})` → `Promise<void>` | Press → animatedMove/animatedMove → release (always releases in finally) |
| `scroll(x, y, dx, dy)` | `(number, number, number, number)` → `Promise<void>` | Move → vertical scroll → horizontal scroll |
| `getFrontmostApp()` | `() => Promise<FrontmostApp \| null>` | Via input module's `getFrontmostAppInfo` |
| `appUnderPoint(x, y)` | `(number, number)` → `Promise<{bundleId, displayName} \| null>` | Swift's `apps.appUnderPoint` |
| `listInstalledApps()` | `() => Promise<InstalledApp[]>` | Swift's `apps.listInstalled` in drainRunLoop |
| `getAppIcon(path)` | `(string) => Promise<string \| undefined>` | Swift's `apps.iconDataUrl` |
| `listRunningApps()` | `() => Promise<RunningApp[]>` | Swift's `apps.listRunning` |
| `openApp(bundleId)` | `(string) => Promise<void>` | Swift's `apps.open` |

**Surrogate host resolution:** Detects terminal bundle ID at factory time. If found, uses it as `surrogateHost` (exempt from hiding, skipped in activate z-order); otherwise falls back to sentinel `CLI_HOST_BUNDLE_ID`. The `withoutTerminal` filter strips terminal from screenshot allow-lists.

---

#### `mcpServer.ts` (106 lines)

Creates the in-process MCP server for the `computer-use` MCP server name.

**Exports:**
| Name | Kind | Signature |
|------|------|-----------|
| `createComputerUseMcpServerForCli()` | function | `() => Promise<ReturnType<typeof createComputerUseMcpServer>>` |
| `runComputerUseMcpServer()` | function | `() => Promise<void>` — subprocess entrypoint for `--computer-use-mcp` |

**Constants:**
- `APP_ENUM_TIMEOUT_MS = 1000`

**Internal helpers:**
- `tryGetInstalledAppNames()` — enumerates installed apps with a 1s timeout via `Promise.race`, filters through `filterAppsForDescription`

**Architecture:** The server:
1. Gets the host adapter (singleton executor factory)
2. Gets the coordinate mode from GrowthBook gates
3. Creates the base MCP server via `createComputerUseMcpServer(adapter, coordinateMode)`
4. Replaces `ListToolsRequestSchema` handler to include installed app names in `request_access` description
5. Returns server with patched handler

The subprocess runner (`runComputerUseMcpServer`) initializes analytics, creates the server, connects to `StdioServerTransport`, and sets up stdin-close → shutdown-and-exit.

---

#### `setup.ts` (53 lines)

Builds the dynamic MCP config for the `computer-use` server.

**Exports:**
| Name | Kind | Signature |
|------|------|-----------|
| `setupComputerUseMCP()` | function | `() => { mcpConfig: Record<string, ScopedMcpServerConfig>; allowedTools: string[] }` |

**Key logic:** Uses `buildComputerUseTools` from `@ant/computer-use-mcp` to generate allowed tool names (prefixed `mcp__computer-use__*`). The `command`/`args` are dummy values — `client.ts` intercepts by name and uses the in-process server. Bundled mode: `['--computer-use-mcp']`; dev mode: `['/path/to/cli.js', '--computer-use-mcp']`.

---

#### `hostAdapter.ts` (69 lines)

Process-lifetime singleton implementing `ComputerUseHostAdapter` from `@ant/computer-use-mcp/types`.

**Exports:**
| Name | Kind | Signature |
|------|------|-----------|
| `getComputerUseHostAdapter()` | function | `() => ComputerUseHostAdapter` |
| `DebugLogger` | class | Implements `Logger` interface, routes to `logForDebugging` |

**Adapter fields:**

| Field | Value |
|-------|-------|
| `serverName` | `COMPUTER_USE_MCP_SERVER_NAME` |
| `logger` | `new DebugLogger()` |
| `executor` | `createCliExecutor({ getMouseAnimationEnabled, getHideBeforeActionEnabled })` |
| `ensureOsPermissions` | Checks TCC accessibility + screen recording via Swift |
| `isDisabled` | `() => !getChicagoEnabled()` |
| `getSubGates` | `getChicagoSubGates` |
| `getAutoUnhideEnabled` | `() => true` (always unhide at turn end) |
| `cropRawPatch` | `() => null` — pixel validation skipped (async image processor incompatible with sync contract) |

---

#### `wrapper.tsx` (336 lines)

The `.call()` override — adapts between `ToolUseContext` and the `@ant/computer-use-mcp` `bindSessionContext`.

**Exports:**
| Name | Kind | Signature |
|------|------|-----------|
| `getComputerUseMCPToolOverrides(toolName)` | function | `(string) => ComputerUseMCPToolOverrides` — returns `.call()` + rendering overrides |
| `buildSessionContext()` | function | `() => ComputerUseSessionContext` |

**Internal types:**
- `CallOverride = Pick<Tool, 'call'>['call']`
- `Binding = { ctx: ComputerUseSessionContext; dispatch: (name, args) => Promise<CuCallToolResult> }`

**Module-level state:**
- `binding: Binding | undefined` — cached dispatcher, persists across calls (screenshot blob survives)
- `currentToolUseContext: ToolUseContext | undefined` — per-call ref, updated on every `.call()`

**Session context getters (read from AppState via per-call ref):**
- `getAllowedApps()`, `getGrantFlags()`, `getUserDeniedBundleIds()`, `getSelectedDisplayId()`, `getDisplayPinnedByModel()`, `getDisplayResolvedForApps()`, `getLastScreenshotDims()`

**Session context write-backs:**
- `onPermissionRequest(req, _dialogSignal) → runPermissionDialog(req)` — renders `ComputerUseApproval` via `setToolJSX`
- `onAllowedAppsChanged(apps, flags)` — merges into AppState
- `onAppsHidden(ids)` — adds to `hiddenDuringTurn` Set
- `onResolvedDisplayUpdated(id)` — updates display resolution state
- `onDisplayPinned(id)` — handles `switch_display` pin/unpin
- `onDisplayResolvedForApps(key)` — stores resolution key
- `onScreenshotCaptured(dims)` — stores last screenshot dimensions

**Session context lock methods:**
- `checkCuLock()` — delegates to `checkComputerUseLock()`, maps result kinds
- `acquireCuLock()` — delegates to `tryAcquireComputerUseLock()`, registers Escape hotkey on fresh acquire, sends OS notification

**The `.call()` override:**
1. Sets `currentToolUseContext = context`
2. Dispatches through cached binding
3. Maps MCP content blocks to Anthropic API blocks (image → base64-source, text → text, fallthrough → empty text)

**`runPermissionDialog(req)`:**
- Renders `React.createElement(ComputerUseApproval, { request: req, onDone })` via `setToolJSX`
- Wraps in `Promise<CuPermissionResponse>` with AbortController signal handling
- Clears JSX in finally block

---

#### `toolRendering.tsx` (125 lines)

UI rendering overrides for `mcp__computer-use__*` tools.

**Exports:**
| Name | Kind | Signature |
|------|------|-----------|
| `getComputerUseMCPRenderingOverrides(toolName)` | function | `(string) => { userFacingName, renderToolUseMessage, renderToolResultMessage }` |

**Internal types:**
- `CuToolInput` — `Record<string, unknown> & { coordinate?, start_coordinate?, text?, apps?, region?, direction?, amount?, duration? }`

**Constants:**
- `RESULT_SUMMARY` — maps tool names to brief result strings: `screenshot → 'Captured'`, `left_click → 'Clicked'`, `type → 'Typed'`, `scroll → 'Scrolled'`, etc.

**Rendering logic — `renderToolUseMessage`:**
Returns input-dependent strings:
- `screenshot`, `left_mouse_down`, `left_mouse_up`, `cursor_position`, `list_granted_applications`, `read_clipboard` → `''` (no detail)
- `left_click`, `right_click`, `middle_click`, `double_click`, `triple_click`, `mouse_move` → coordinate format `(x, y)`
- `left_click_drag` → `"(from) → (to)"` or `"to (x, y)"`
- `type`, `write_clipboard` → truncated quoted text (40 chars)
- `key`, `hold_key` → raw text
- `scroll` → direction × amount at coordinate
- `zoom` → region `[x, y, w, h]`
- `wait` → `"Ns"`
- `open_application` → bundle_id
- `request_access` → comma-joined app display names
- `computer_batch` → `"N actions"`

**Rendering logic — `renderToolResultMessage`:**
Non-verbose: one-line dim summary text from `RESULT_SUMMARY`. Verbose: `null` (let default renderer handle it).

---

#### `gates.ts` (72 lines)

GrowthBook-driven feature gates for the Computer Use MCP.

**Exports:**
| Name | Kind | Signature |
|------|------|-----------|
| `getChicagoEnabled()` | function | `() => boolean` |
| `getChicagoSubGates()` | function | `() => CuSubGates` |
| `getChicagoCoordinateMode()` | function | `() => CoordinateMode` — frozen at first read |

**Types:**
- `ChicagoConfig = CuSubGates & { enabled: boolean; coordinateMode: CoordinateMode }`

**GrowthBook gate:** `tengu_malort_pedway`

**Sub-gates (from `CuSubGates`):**
- `pixelValidation` (default `false`)
- `clipboardPasteMultiline` (default `true`)
- `mouseAnimation` (default `true`)
- `hideBeforeAction` (default `true`)
- `autoTargetDisplay` (default `true`)
- `clipboardGuard` (default `true`)

**Access control:** Requires Max/Pro subscription OR `USER_TYPE === 'ant'` (internal dogfooding). Ants with `MONOREPO_ROOT_DIR` set are blocked unless `ALLOW_ANT_COMPUTER_USE_MCP=1` is set.

---

#### `inputLoader.ts` (30 lines)

Lazy loader for `@ant/computer-use-input` (Rust/enigo native module).

**Exports:**
| Name | Kind | Signature |
|------|------|-----------|
| `requireComputerUseInput()` | function | `() => ComputerUseInputAPI` — throws if not supported on platform |

**Caching:** Module-level `cached` variable — loaded once, reused for process lifetime.

**Context:** The package reads `COMPUTER_USE_INPUT_NODE_PATH` (baked by `build-with-plugins.ts` on darwin targets). `key()`/`keys()` dispatch to `DispatchQueue.main` via `dispatch2::run_on_main` — need `drainRunLoop` to pump under libuv.

---

#### `swiftLoader.ts` (23 lines)

Lazy loader for `@ant/computer-use-swift` (Swift native module for screenshots, apps, TCC).

**Exports:**
| Name | Kind | Signature |
|------|------|-----------|
| `requireComputerUseSwift()` | function | `() => ComputerUseAPI` — throws if not darwin |
| `ComputerUseAPI` | type re-export | From `@ant/computer-use-swift` |

**Caching:** Module-level `cached` variable. Four `@MainActor` methods (`captureExcluding`, `captureRegion`, `apps.listInstalled`, `resolvePrepareCapture`) require `drainRunLoop` under libuv.

---

#### `drainRunLoop.ts` (79 lines)

Shared CFRunLoop pump for native module calls.

**Exports:**
| Name | Kind | Signature |
|------|------|-----------|
| `drainRunLoop(fn)` | function | `async <T>(fn: () => Promise<T>) => Promise<T>` |
| `retainPump` | const | `= retain` |
| `releasePump` | const | `= release` |

**Constants:**
- `TIMEOUT_MS = 30_000`

**Mechanism:** A refcounted `setInterval` (every 1ms) calls `requireComputerUseSwift()._drainMainRunLoop()`. Multiple concurrent `drainRunLoop()` calls share a single pump via `retain`/`release`. The timeout uses `Promise.race` — if the 30s timeout wins, the work promise is orphaned (its catch swallows late rejections).

---

#### `escHotkey.ts` (54 lines)

Global Escape → abort via `@ant/computer-use-swift` CGEventTap.

**Exports:**
| Name | Kind | Signature |
|------|------|-----------|
| `registerEscHotkey(onEscape)` | function | `(onEscape: () => void) => boolean` |
| `unregisterEscHotkey()` | function | `() => void` |
| `notifyExpectedEscape()` | function | `() => void` |

**Lifecycle:** `registerEscHotkey` on fresh lock acquire → `retainPump` for CFRunLoopSource lifetime → `unregisterEscHotkey` on lock release → `releasePump`. `notifyExpectedEscape` punches a hole for model-synthesized Escapes (100ms decay).

---

#### `computerUseLock.ts` (215 lines)

File-based exclusive lock for Computer Use sessions.

**Exports:**
| Name | Kind | Signature |
|------|------|-----------|
| `checkComputerUseLock()` | function | `() => Promise<CheckResult>` |
| `tryAcquireComputerUseLock()` | function | `() => Promise<AcquireResult>` |
| `releaseComputerUseLock()` | function | `() => Promise<boolean>` |
| `isLockHeldLocally()` | function | `() => boolean` |

**Types:**
- `ComputerUseLock = { sessionId: string; pid: number; acquiredAt: number }`
- `AcquireResult = { kind: 'acquired'; fresh: boolean } | { kind: 'blocked'; by: string }`
- `CheckResult = { kind: 'free' } | { kind: 'held_by_self' } | { kind: 'blocked'; by: string }`

**Constants:**
- `LOCK_FILENAME = 'computer-use.lock'`
- `FRESH = { kind: 'acquired', fresh: true }`
- `REENTRANT = { kind: 'acquired', fresh: false }`

**Lock location:** `~/.claude/computer-use.lock`

**Acquire algorithm:**
1. Create directory `mkdir(recursive: true)`
2. Try `writeFile(flag: 'wx')` — atomic O_EXCL test-and-set
3. If EEXIST: read lock, check ownership (same sessionId → re-entrant)
4. Check PID liveness via `process.kill(pid, 0)`
5. If stale: unlink + retry exclusive create once
6. On fresh acquire: register cleanup handler via `registerCleanup`

**Release algorithm:**
1. Unregister cleanup handler
2. Read lock, verify owner is self
3. Unlink lock file, return true if successful

**Stale recovery:** `checkComputerUseLock` does stale-PID recovery (unlinks) so dead sessions don't block `request_access` calls.

---

#### `cleanup.ts` (86 lines)

Turn-end cleanup: auto-unhide apps, release lock, unregister Escape hotkey.

**Exports:**
| Name | Kind | Signature |
|------|------|-----------|
| `cleanupComputerUseAfterTurn(ctx)` | function | `(ctx: Pick<ToolUseContext, 'getAppState' \| 'setAppState' \| 'sendOSNotification'>) => Promise<void>` |

**Constants:**
- `UNHIDE_TIMEOUT_MS = 5000`

**Cleanup sequence:**
1. If `hiddenDuringTurn` has entries: dynamic import `executor.js` → `unhideComputerUseApps` with 5s timeout
2. Clear `hiddenDuringTurn` from AppState
3. If `isLockHeldLocally()`: unregister Escape hotkey, release file lock
4. If lock released (we held it): send OS notification "Claude is done using your computer"

---

#### `appNames.ts` (196 lines)

Filter and sanitize installed-app data for `request_access` tool description.

**Exports:**
| Name | Kind | Signature |
|------|------|-----------|
| `filterAppsForDescription(installed, homeDir)` | function | `(readonly InstalledAppLike[], string \| undefined) => string[]` |

**Constants:**
- `PATH_ALLOWLIST: ['/Applications/', '/System/Applications/']` — only apps under these roots
- `NAME_PATTERN_BLOCKLIST` — filter out Helper, Agent, Service, Uninstaller, Updater, dot-names
- `ALWAYS_KEEP_BUNDLE_IDS` — 33 bundle IDs always included (Safari, Chrome, Slack, VS Code, Finder, etc.)
- `APP_NAME_ALLOWED = /^[\p{L}\p{M}\p{N}_ .&'()+-]+$/u` — Unicode-safe, bars quotes/angle brackets/backticks
- `APP_NAME_MAX_LEN = 40`
- `APP_NAME_MAX_COUNT = 50`

**Sanitization flow:**
1. Partition into `alwaysKept` (matching bundle IDs) and `rest` (user-facing path, non-noisy name)
2. Always-kept names: sanitize via `sanitizeCore(raw, false)` — no char filter (trusted vendors)
3. Rest names: sanitize via `sanitizeCore(raw, true)` — apply char filter against `APP_NAME_ALLOWED`
4. Merge: alwaysKept first, then rest (deduplicated against alwaysKept)
5. If > 50: truncate to 50 + `"... and N more"`

---

## Group 2: Claude-in-Chrome System (`utils/claudeInChrome/`)

**7 files | 1,844 total lines** — Browser automation via Chrome extension with MCP.

### Architecture Overview

Claude-in-Chrome allows Claude Code to control a user's Chrome browser through a browser extension. Two connection paths exist:
1. **Native messaging**: Direct stdin/stdout pipe via Chrome Native Host
2. **Bridge**: WebSocket bridge for remote/dev environments

The system manages native host manifest installation across 7 Chromium browsers (Chrome, Brave, Arc, Chromium, Edge, Vivaldi, Opera) on macOS, Linux, and Windows.

---

### File-by-File Documentation

#### `common.ts` (540 lines)

Browser configuration, detection, and utility functions.

**Exports:**
| Name | Kind | Signature/Value |
|------|------|-----------------|
| `CLAUDE_IN_CHROME_MCP_SERVER_NAME` | const | `'claude-in-chrome'` |
| `CHROMIUM_BROWSERS` | const | `Record<ChromiumBrowser, BrowserConfig>` — configuration for all 7 browsers |
| `BROWSER_DETECTION_ORDER` | const | `ChromiumBrowser[]` — `['chrome', 'brave', 'arc', 'edge', 'chromium', 'vivaldi', 'opera']` |
| `getAllBrowserDataPaths()` | function | `() => { browser: ChromiumBrowser; path: string }[]` |
| `getAllNativeMessagingHostsDirs()` | function | `() => { browser: ChromiumBrowser; path: string }[]` |
| `getAllWindowsRegistryKeys()` | function | `() => { browser: ChromiumBrowser; key: string }[]` |
| `detectAvailableBrowser()` | function | `() => Promise<ChromiumBrowser \| null>` |
| `isClaudeInChromeMCPServer(name)` | function | `(string) => boolean` |
| `trackClaudeInChromeTabId(tabId)` | function | `(number) => void` |
| `isTrackedClaudeInChromeTabId(tabId)` | function | `(number) => boolean` |
| `openInChrome(url)` | function | `(string) => Promise<boolean>` |
| `getSocketDir()` | function | `() => string` — `/tmp/claude-mcp-browser-bridge-{username}` |
| `getSecureSocketPath()` | function | `() => string` — PID-based socket or Windows named pipe |
| `getAllSocketPaths()` | function | `() => string[]` — all PID sockets + legacy fallbacks |

**`BrowserConfig` type:**
```typescript
type BrowserConfig = {
  name: string
  macos: { appName: string; dataPath: string[]; nativeMessagingPath: string[] }
  linux: { binaries: string[]; dataPath: string[]; nativeMessagingPath: string[] }
  windows: { dataPath: string[]; registryKey: string; useRoaming?: boolean }
}
```

**Constants:**
- `MAX_TRACKED_TABS = 200` — circular tracking of tab IDs

**Socket naming:** Unix: `/tmp/claude-mcp-browser-bridge-{username}/{pid}.sock`. Windows: `\\.\pipe\claude-mcp-browser-bridge-{username}`.

---

#### `chromeNativeHost.ts` (527 lines)

Pure TypeScript Chrome native messaging host implementation (previously Rust NAPI).

**Exports:**
| Name | Kind | Signature |
|------|------|-----------|
| `sendChromeMessage(message)` | function | `(string) => void` — writes length-prefixed JSON to stdout (Chrome native protocol) |
| `runChromeNativeHost()` | function | `() => Promise<void>` — main entry point |

**Internal classes:**

**`ChromeNativeHost`:**
- Manages Unix socket server (or Windows named pipe) for MCP client connections
- `start()` — creates socket directory with 0700 perms, cleans stale sockets, listens on secure socket path, sets 0600 perms
- `stop()` — destroys all MCP client sockets, closes server, unlinks socket file
- `handleMessage(messageJson)` — dispatches Chrome messages: `ping→pong`, `get_status→status_response`, `tool_response`/`notification` → forward to MCP clients, unknown → error
- `handleMcpClient(socket)` — registers MCP client, relays tool requests to Chrome via stdout

**`ChromeMessageReader`:**
- Async stdin reader for Chrome native messaging protocol (4-byte length prefix + JSON payload)
- Uses `Buffer.concat` buffer, `process.stdin.on('data')` events
- `read()` — returns Promise<string | null>, null on stdin close

**Constants:**
- `VERSION = '1.0.0'`
- `MAX_MESSAGE_SIZE = 1024 * 1024` (1MB)

**Types:**
- `ToolRequest = { method: string; params?: unknown }`
- `McpClient = { id: number; socket: Socket; buffer: Buffer }`

---

#### `mcpServer.ts` (293 lines)

Creates the Claude-in-Chrome MCP server context and subprocess runner.

**Exports:**
| Name | Kind | Signature |
|------|------|-----------|
| `createChromeContext(env?)` | function | `(env?: Record<string, string>) => ClaudeForChromeContext` |
| `runClaudeInChromeMcpServer()` | function | `() => Promise<void>` |

**Constants:**
- `EXTENSION_DOWNLOAD_URL = 'https://claude.ai/chrome'`
- `BUG_REPORT_URL` — GitHub issue link
- `PERMISSION_MODES = ['ask', 'skip_all_permission_checks', 'follow_a_plan']`
- `SAFE_BRIDGE_STRING_KEYS` — allowlisted metadata keys for analytics (bridge_status, error_type, tool_name)

**Bridge URL resolution:**
- Ant users OR GrowthBook gate `tengu_copper_bridge` → bridge enabled
- Local: `ws://localhost:8765`
- Staging: `wss://bridge-staging.claudeusercontent.com`
- Production: `wss://bridge.claudeusercontent.com`

**`createChromeContext` fields:**

| Field | Value |
|-------|-------|
| `serverName` | `'Claude in Chrome'` |
| `socketPath` | `getSecureSocketPath()` |
| `getSocketPaths` | `getAllSocketPaths` |
| `clientTypeId` | `'claude-code'` |
| `onAuthenticationError` | Logs auth error instructions |
| `onToolCallDisconnected` | Returns extension connection instructions |
| `onExtensionPaired(deviceId, name)` | Saves to global config |
| `getPersistedDeviceId` | Reads from config |
| `bridgeConfig` | Conditional: `{ url, getUserId, getOAuthToken }` |
| `initialPermissionMode` | From `CLAUDE_CHROME_PERMISSION_MODE` env/override |
| `callAnthropicMessages` | Ant-only: delegates to `sideQuery` for lightning-mode agent loop |
| `trackEvent(eventName, metadata)` | Sanitized analytics forwarding |

**`DebugLogger`** (internal class): Implements `Logger` interface, routes through `logForDebugging`.

---

#### `prompt.ts` (83 lines)

System prompt templates for the Claude-in-Chrome skill.

**Exports:**
| Name | Kind | Value |
|------|------|-------|
| `BASE_CHROME_PROMPT` | const | Full browser automation guidelines: GIF recording, console log debugging, alerts/dialogs, rabbit-hole avoidance, tab context |
| `CHROME_TOOL_SEARCH_INSTRUCTIONS` | const | Instructions for loading chrome tools via ToolSearch |
| `getChromeSystemPrompt()` | function | `() => string` — returns `BASE_CHROME_PROMPT` |
| `CLAUDE_IN_CHROME_SKILL_HINT` | const | Startup hint to invoke the claude-in-chrome skill |
| `CLAUDE_IN_CHROME_SKILL_HINT_WITH_WEBBROWSER` | const | Variant when WebBrowser tool is also available — steers dev tasks to WebBrowser, authenticated tasks to extension |

---

#### `setup.ts` (400 lines)

Setup and installation of Chrome native host for the Claude-in-Chrome extension.

**Exports:**
| Name | Kind | Signature |
|------|------|-----------|
| `shouldEnableClaudeInChrome(chromeFlag?)` | function | `(boolean?) => boolean` |
| `shouldAutoEnableClaudeInChrome()` | function | `() => boolean` |
| `setupClaudeInChrome()` | function | `() => { mcpConfig, allowedTools, systemPrompt }` |
| `installChromeNativeHostManifest(manifestBinaryPath)` | function | `(string) => Promise<void>` |
| `isChromeExtensionInstalled()` | function | `() => Promise<boolean>` |

**Constants:**
- `NATIVE_HOST_IDENTIFIER = 'com.anthropic.claude_code_browser_extension'`
- `NATIVE_HOST_MANIFEST_NAME = '{identifier}.json'`
- `CHROME_EXTENSION_RECONNECT_URL = 'https://clau.de/chrome/reconnect'`

**Extension IDs in manifest:**
- Production: `fcoeoabgfenejglbffodgkkbkcdhcgfn`
- Dev (ant only): `dihbgbndebgnbjfmelmegjepbnkhlgni`
- Ant (ant only): `dngcpimnedloihjnnfngkgjoidhnaolf`

**`shouldEnableClaudeInChrome` precedence:**
1. CLI flag (true/false)
2. `CLAUDE_CODE_ENABLE_CFC` env var
3. Config `claudeInChromeDefaultEnabled`

**`setupClaudeInChrome` flow:**
1. Build allowedTools from `BROWSER_TOOLS` (prefixed `mcp__claude-in-chrome__*`)
2. If bypass mode: set `CLAUDE_CHROME_PERMISSION_MODE = 'skip_all_permission_checks'`
3. Create wrapper script in `~/.claude/chrome/`
4. Install manifest to all browser native messaging directories
5. Return MCP config (stdio, dynamic scope) with system prompt

**Wrapper script:** Required because Chrome native host manifest `path` cannot contain arguments. Unix: `#!/bin/sh` + `exec`; Windows: `@echo off`.

**Extension installation detection:** Scanning `Extensions/{extensionId}` across all Chromium browser profile directories. Only positive detections are cached to `~/.claude.json`.

---

#### `setupPortable.ts` (233 lines)

Portable browser extension detection (shared between TUI and VS Code extension).

**Exports:**
| Name | Kind | Signature |
|------|------|-----------|
| `CHROME_EXTENSION_URL` | const | `'https://claude.ai/chrome'` |
| `ChromiumBrowser` | type | `'chrome' \| 'brave' \| 'arc' \| 'chromium' \| 'edge' \| 'vivaldi' \| 'opera'` |
| `BrowserPath` | type | `{ browser: ChromiumBrowser; path: string }` |
| `getAllBrowserDataPathsPortable()` | function | `() => BrowserPath[]` |
| `detectExtensionInstallationPortable(browserPaths, log?)` | function | `(BrowserPath[], Logger?) => Promise<{ isInstalled: boolean; browser: ChromiumBrowser \| null }>` |
| `isChromeExtensionInstalledPortable(browserPaths, log?)` | function | `(BrowserPath[], Logger?) => Promise<boolean>` |
| `isChromeExtensionInstalled(log?)` | function | `(Logger?) => Promise<boolean>` — convenience, auto-detects paths |

**Extension IDs:**
- `PROD_EXTENSION_ID = 'fcoeoabgfenejglbffodgkkbkcdhcgfn'`
- `DEV_EXTENSION_ID = 'dihbgbndebgnbjfmelmegjepbnkhlgni'`
- `ANT_EXTENSION_ID = 'dngcpimnedloihjnnfngkgjoidhnaolf'`

**Browser data paths:** Same structure as `CHROMIUM_BROWSERS` in `common.ts` but duplicated for portability (uses `process.platform` directly instead of `getPlatform()`).

---

#### `toolRendering.tsx` (262 lines)

UI rendering overrides for `mcp__claude-in-chrome__*` tools.

**Exports:**
| Name | Kind | Signature |
|------|------|-----------|
| `ChromeToolName` | type | Union of all 17 chrome tool names |
| `getClaudeInChromeMCPToolOverrides(toolName)` | function | `(string) => { userFacingName, renderToolUseMessage, renderToolUseTag, renderToolResultMessage }` |
| `renderChromeToolResultMessage(output, toolName, verbose)` | function | `(MCPToolResult, ChromeToolName, boolean) => React.ReactNode` |

**Tool names:** `javascript_tool`, `read_page`, `find`, `form_input`, `computer`, `navigate`, `resize_window`, `gif_creator`, `upload_image`, `get_page_text`, `tabs_context_mcp`, `tabs_create_mcp`, `update_plan`, `read_console_messages`, `read_network_requests`, `shortcuts_list`, `shortcuts_execute`

**Rendering features:**
- Tool use messages show secondary info (URL hostname, pattern, action details, coordinates)
- `javascript_tool` in verbose mode shows full code
- "View Tab" link via `renderChromeViewTabLink` — clickable hyperlink to `https://clau.de/chrome/tab/{tabId}`
- Result messages show brief one-line summaries (e.g., "Navigation completed", "Tab created")

---

## Group 3: Deep Link System (`utils/deepLink/`)

**6 files | 1,382 total lines** — `claude-cli://` URI protocol handling.

### Architecture Overview

Handles `claude-cli://open?q=...&cwd=...&repo=owner/repo` deep links across macOS, Linux, and Windows. When the OS opens such a link, Claude Code:
1. Parses the URI for query, cwd, and repo parameters
2. Registers as the OS-level handler for the `claude-cli://` scheme
3. Launches itself in the user's preferred terminal emulator

---

### File-by-File Documentation

#### `parseDeepLink.ts` (170 lines)

URI parser for `claude-cli://open` links.

**Exports:**
| Name | Kind | Signature/Value |
|------|------|-----------------|
| `DEEP_LINK_PROTOCOL` | const | `'claude-cli'` |
| `DeepLinkAction` | type | `{ query?: string; cwd?: string; repo?: string }` |
| `parseDeepLink(uri)` | function | `(string) => DeepLinkAction` |
| `buildDeepLink(action)` | function | `(DeepLinkAction) => string` — builds URL from action |

**Security validations:**
- ASCII control characters (0x00-0x1F, 0x7F) rejected in all fields
- cwd must start with `/` or `[A-Z]:[\/\\]` (absolute path)
- cwd max length: 4096 (PATH_MAX)
- repo must match `/^[\w.-]+\/[\w.-]+$/` (GitHub slug, single slash, no traversal)
- Query max length: 5000
- Unicode sanitized via `partiallySanitizeUnicode` (strips hidden characters)
- Query trimmed and rejected if empty

**Protocol normalization:** Accepts `claude-cli://...` or `claude-cli:...` (adds missing `//`).

---

#### `protocolHandler.ts` (136 lines)

Entry point for deep link handling when OS invokes claude.

**Exports:**
| Name | Kind | Signature |
|------|------|-----------|
| `handleDeepLinkUri(uri)` | function | `(string) => Promise<number>` — returns exit code (0=success) |
| `handleUrlSchemeLaunch()` | function | `() => Promise<number \| null>` — macOS URL scheme handling via `url-handler-napi` |

**`handleDeepLinkUri` flow:**
1. Parse URI → `DeepLinkAction`
2. Resolve CWD: explicit cwd > repo lookup (MRU clone) > home
3. Read `FETCH_HEAD` mtime for repo freshness
4. Launch in terminal via `launchInTerminal(process.execPath, { query, cwd, repo, lastFetchMs })`

**`resolveCwd`:**
- If `action.cwd` is set → use directly
- If `action.repo` is set → look up in `getKnownPathsForRepo(repo)`, filter existing via `filterExistingPaths`, use first match or fallback to home

---

#### `registerProtocol.ts` (348 lines)

OS-level protocol handler registration for `claude-cli://`.

**Exports:**
| Name | Kind | Signature/Value |
|------|------|-----------------|
| `MACOS_BUNDLE_ID` | const | `'com.anthropic.claude-code-url-handler'` |
| `registerProtocolHandler(claudePath?)` | function | `(string?) => Promise<void>` |
| `isProtocolHandlerCurrent(claudePath)` | function | `(string) => Promise<boolean>` |
| `ensureDeepLinkProtocolRegistered()` | function | `() => Promise<void>` — auto-register on session startup |

**Constants:**
- `APP_NAME = 'Claude Code URL Handler'`
- `DESKTOP_FILE_NAME = 'claude-code-url-handler.desktop'`
- `MACOS_APP_NAME = 'Claude Code URL Handler.app'`
- `FAILURE_BACKOFF_MS = 24 * 60 * 60 * 1000` (24 hours)

**Platform implementations:**

**macOS (`registerMacos`):**
- Creates `~/Applications/Claude Code URL Handler.app/`
- Writes `Info.plist` with `CFBundleURLTypes` registering `claude-cli` scheme
- `CFBundleExecutable` = symlink to actual claude binary (avoids separate signed executable)
- Runs `lsregister -R` to register with LaunchServices

**Linux (`registerLinux`):**
- Creates `.desktop` file in `$XDG_DATA_HOME/applications/`
- Registers via `xdg-mime default` as handler for `x-scheme-handler/claude-cli`
- Gracefully handles missing `xdg-mime` (headless systems)

**Windows (`registerWindows`):**
- Writes registry keys under `HKEY_CURRENT_USER\Software\Classes\claude-cli`
- Sets default value, `URL Protocol` flag, and `shell\open\command`

**`ensureDeepLinkProtocolRegistered`:**
- Gated on GrowthBook `tengu_lodestone_enabled`
- Skips if `disableDeepLinkRegistration === 'disable'` in settings
- Checks `isProtocolHandlerCurrent` before re-registering
- 24h failure backoff via `~/.claude/.deep-link-register-failed` marker
- Emits `tengu_deep_link_registered` analytics event

---

#### `terminalLauncher.ts` (557 lines)

Detects user's preferred terminal emulator and launches Claude Code inside it.

**Exports:**
| Name | Kind | Signature |
|------|------|-----------|
| `TerminalInfo` | type | `{ name: string; command: string }` |
| `detectTerminal()` | function | `() => Promise<TerminalInfo \| null>` |
| `launchInTerminal(claudePath, action)` | function | `(string, { query?, cwd?, repo?, lastFetchMs? }) => Promise<boolean>` |

**macOS terminals** (preference order): iTerm2, Ghostty, Kitty, Alacritty, WezTerm, Terminal.app
- iTerm2: Uses AppleScript `tell application "iTerm"` → `write text` (shell-string path)
- Terminal.app: Uses AppleScript `tell application "Terminal"` → `do script` (shell-string path)
- Ghostty, Alacritty, Kitty, WezTerm: Pure argv via `open -na <App> --args` (no shell interpretation)

**Linux terminals:** ghostty, kitty, alacritty, wezterm, gnome-terminal, konsole, xfce4-terminal, mate-terminal, tilix, xterm
- All use pure argv paths with terminal-specific `--working-directory`/`-e` flags

**Windows terminals:** Windows Terminal (wt.exe), PowerShell, cmd.exe
- Windows Terminal: Pure argv via `-d <cwd> -- <claude> <args>`
- PowerShell: Shell-string via `-NoExit -Command`
- cmd.exe: Shell-string via `/k`, with `windowsVerbatimArguments` to bypass MSVCRT double-escaping

**Quoting functions (internal):**
| Function | Purpose | Strategy |
|----------|---------|----------|
| `shellQuote(s)` | POSIX single-quote for AppleScript paths | `'...'` with `'\''` for embedded quotes |
| `appleScriptQuote(s)` | AppleScript string literal | Double-quote with backslash escapes |
| `psQuote(s)` | PowerShell single-quote | `'...'` with `''` for embedded quotes |
| `cmdQuote(arg)` | cmd.exe argument | Strip `"`, expand `%` → `%%`, double trailing backslashes |

**`spawnDetached`:** Spawns terminal with `detached: true, stdio: 'ignore'`, resolves on spawn, rejects on error.

---

#### `terminalPreference.ts` (54 lines)

Captures user's terminal preference from `TERM_PROGRAM` env var for deep link handler.

**Exports:**
| Name | Kind | Signature |
|------|------|-----------|
| `updateDeepLinkTerminalPreference()` | function | `() => void` |

**Constants:**
- `TERM_PROGRAM_TO_APP` — maps TERM_PROGRAM values (lowercased) to app names: `iterm→iTerm`, `ghostty→Ghostty`, `kitty→kitty`, `apple_terminal→Terminal`, etc.

**Logic:** macOS-only. Reads `TERM_PROGRAM`, maps to app name, stores in `globalConfig.deepLinkTerminal` if changed.

---

#### `banner.ts` (123 lines)

Builds warning banner for deep-link-originated sessions.

**Exports:**
| Name | Kind | Signature |
|------|------|-----------|
| `DeepLinkBannerInfo` | type | `{ cwd: string; prefillLength?: number; repo?: string; lastFetch?: Date }` |
| `buildDeepLinkBanner(info)` | function | `(DeepLinkBannerInfo) => string` |
| `readLastFetchTime(cwd)` | function | `(string) => Promise<Date \| undefined>` |

**Constants:**
- `STALE_FETCH_WARN_MS = 7 * 24 * 60 * 60 * 1000` (7 days)
- `LONG_PREFILL_THRESHOLD = 1000` — above this, shows "scroll to review" warning

**Banner content:**
1. Line 1: "This session was opened by an external deep link in {cwd}" (tildified)
2. If repo: "Resolved {repo} from local clones · last fetched {age}" (with stale warning if >7d)
3. If prefill: "The prompt below was supplied by the link — review carefully" (or scroll warning if >1000 chars)

**`readLastFetchTime`:** Reads `FETCH_HEAD` mtime from git dir, handles worktrees by checking both local and common dir.

---

## Group 4: Native Installer (`utils/nativeInstaller/`)

**5 files | 3,118 total lines** — File-based native binary installer with version management, locking, and package manager detection.

### Architecture Overview

Manages native binary installations of Claude Code (bypassing npm/npx). Key features:
- Downloads platform-specific binaries from GCS (external users) or Artifactory (ant users)
- Installs to `~/.local/share/claude/versions/{version}`
- Creates symlink at `~/.local/bin/claude` (Unix) or copies exe (Windows)
- Version cleanup retains 2 most recent
- Two locking strategies: PID-based (GrowthBook rollout) or mtime-based (fallback)

---

### File-by-File Documentation

#### `index.ts` (18 lines)

Barrel file exporting the public API.

**Exports:**
`checkInstall`, `cleanupNpmInstallations`, `cleanupOldVersions`, `cleanupShellAliases`, `installLatest`, `lockCurrentVersion`, `removeInstalledSymlink`, `SetupMessage` (type)

---

#### `installer.ts` (1,708 lines)

Core installer implementation — the largest file in this analysis.

**Exports:**
| Name | Kind | Signature |
|------|------|-----------|
| `VERSION_RETENTION_COUNT` | const | `2` |
| `SetupMessage` | type | `{ message: string; userActionRequired: boolean; type: 'path' \| 'alias' \| 'info' \| 'error' }` |
| `getPlatform()` | function | `() => string` — returns `${os}-${arch}` with optional `-musl` suffix |
| `getBinaryName(platform)` | function | `(string) => string` — `'claude.exe'` or `'claude'` |
| `checkInstall(force?)` | function | `(boolean?) => Promise<SetupMessage[]>` |
| `installLatest(channelOrVersion, forceReinstall?)` | function | `(string, boolean?) => Promise<InstallLatestResult>` |
| `lockCurrentVersion()` | function | `() => Promise<void>` |
| `cleanupOldVersions()` | function | `() => Promise<void>` |
| `removeInstalledSymlink()` | function | `() => Promise<void>` |
| `cleanupShellAliases()` | function | `() => Promise<SetupMessage[]>` |
| `cleanupNpmInstallations()` | function | `() => Promise<{ removed: number; errors: string[]; warnings: string[] }>` |
| `removeDirectoryIfEmpty(path)` | function | `(string) => Promise<void>` — exported for testing |

**Internal helpers:**

| Name | Signature | Description |
|------|-----------|-------------|
| `getBaseDirectories()` | `() => { versions, staging, locks, executable }` | XDG-based paths |
| `getVersionPaths(version)` | `(string) => { stagingPath, installPath }` | Paths for a specific version |
| `isPossibleClaudeBinary(filePath)` | `(string) => Promise<boolean>` | Checks file exists, non-zero size, executable |
| `versionIsAvailable(version)` | `(string) => Promise<boolean>` | Checks if version is already installed |
| `tryWithVersionLock(versionFilePath, callback, retries?)` | `(string, fn, number?) => Promise<boolean>` | Execute callback while holding lock |
| `atomicMoveToInstallPath(stagedBinaryPath, installPath)` | `(string, string) => Promise<void>` | Copy → chmod → rename atomic install |
| `installVersion(stagingPath, installPath, downloadType)` | `(string, string, 'npm' \| 'binary') => Promise<void>` | Routes to package or binary installer |
| `performVersionUpdate(version, forceReinstall)` | `(string, boolean) => Promise<boolean>` | Download → install → symlink |
| `updateSymlink(symlinkPath, targetPath)` | `(string, string) => Promise<boolean>` | Atomic symlink update with temp name |
| `updateLatest(channelOrVersion, forceReinstall?)` | `(string, boolean?) => Promise<{success, latestVersion, lockFailed?, lockHolderPid?}>` | Core update logic |
| `getVersionFromSymlink(symlinkPath)` | `(string) => Promise<string \| null>` | Resolves symlink target |
| `cleanupOldVersions()` | `() => Promise<void>` | Cleans old Windows exes, staging dirs, stale locks, temp files, old versions |
| `manualRemoveNpmPackage(packageName)` | `(string) => Promise<{success, error?, warning?}>` | Manual npm cleanup |
| `attemptNpmUninstall(packageName)` | `(string) => Promise<{success, error?, warning?}>` | npm uninstall with ENOTEMPTY fallback |

**Constants:**
- `LOCK_STALE_MS = 7 * 24 * 60 * 60 * 1000` (7 days)
- `VERSION_RETENTION_COUNT = 2`

**`installLatest` singleflight:** Module-level `inFlightInstall` promise prevents concurrent downloads when UI component remounts trigger multiple calls.

**`checkInstall` flow:**
1. Skip if `DISABLE_INSTALLATION_CHECKS` env var
2. Skip for development builds
3. Only check if `installMethod === 'native'` or force mode
4. Verify bin directory exists, executable exists/is valid, PATH contains bin dir
5. Platform-specific PATH instructions

**`lockCurrentVersion`:**
- Acquires lock on running version to prevent cleanup deletion
- PID-based locking (GrowthBook gate `tengu_pid_based_version_locking`) or mtime-based (7-day stale timeout)
- Registers cleanup handler to release on exit

**Version cleanup order:**
1. Old Windows renamed executables (`claude.exe.old.{ts}`)
2. Orphaned staging directories (>1 hour old)
3. Stale PID locks (crashed processes)
4. Orphaned temp install files (`{version}.tmp.{pid}.{timestamp}`, >1 hour old)
5. Old version bins (keep 2, protect locked/current versions)

---

#### `download.ts` (523 lines)

Binary download from GCS and Artifactory with checksum verification.

**Exports:**
| Name | Kind | Signature |
|------|------|-----------|
| `ARTIFACTORY_REGISTRY_URL` | const | `'https://artifactory.infra.ant.dev/artifactory/api/npm/npm-all/'` |
| `getLatestVersionFromArtifactory(tag?)` | function | `(string?) => Promise<string>` — ant users, npm view |
| `getLatestVersionFromBinaryRepo(channel, baseUrl, authConfig?)` | function | `(ReleaseChannel, string, {auth?}?) => Promise<string>` — external users, axios GET |
| `getLatestVersion(channelOrVersion)` | function | `(string) => Promise<string>` — routes to appropriate source |
| `downloadVersionFromArtifactory(version, stagingPath)` | function | `(string, string) => Promise<void>` — npm ci with integrity verification |
| `downloadVersionFromBinaryRepo(version, stagingPath, baseUrl, authConfig?)` | function | `(string, string, string, {auth?, headers?}?) => Promise<void>` — manifest-based download |
| `downloadVersion(version, stagingPath)` | function | `(string, string) => Promise<'npm' \| 'binary'>` — routes by user type |
| `StallTimeoutError` | class | Extends Error |
| `MAX_DOWNLOAD_RETRIES` | const | `3` |
| `STALL_TIMEOUT_MS` | const | `60000` |
| `_downloadAndVerifyBinaryForTesting` | const | `= downloadAndVerifyBinary` — exposed for tests |

**Constants:**
- `GCS_BUCKET_URL = 'https://storage.googleapis.com/claude-code-dist-86c565f3-f756-42ad-8dfa-d59b1c096819/claude-code-releases'`
- `MAX_DOWNLOAD_RETRIES = 3`
- `DEFAULT_STALL_TIMEOUT_MS = 60000`

**Download flow (`downloadAndVerifyBinary`):**
1. Up to 3 retries (only on stall timeouts)
2. `axios.get` with `responseType: 'arraybuffer'`, 5-min total timeout, stall detection via `onDownloadProgress` resetting a 60s timer
3. SHA-256 checksum verification
4. Write to disk + chmod 0755

**Artifactory download:** Creates npm project in staging, generates `package.json` + `package-lock.json` with integrity hash from `npm view ... dist.integrity`, runs `npm ci --prefer-online`.

**Version format:** Accepts `v1.2.3` or `1.2.3-dev.shaf4937ce`, channels `stable`/`latest`. Test versions `99.99.x` are gated on `feature('ALLOW_TEST_VERSIONS')` (DCE'd from shipped builds).

---

#### `packageManagers.ts` (336 lines)

Detects which package manager installed Claude Code.

**Exports:**
| Name | Kind | Signature |
|------|------|-----------|
| `PackageManager` | type | `'homebrew' \| 'winget' \| 'pacman' \| 'deb' \| 'rpm' \| 'apk' \| 'mise' \| 'asdf' \| 'unknown'` |
| `getOsRelease` | function | memoized async: `() => Promise<{ id: string; idLike: string[] } \| null>` |
| `detectHomebrew()` | function | `() => boolean` — checks for `/Caskroom/` in exec path |
| `detectWinget()` | function | `() => boolean` — checks for `WinGet\Packages` or `WinGet\Links` |
| `detectMise()` | function | `() => boolean` — checks for `/mise/installs/` |
| `detectAsdf()` | function | `() => boolean` — checks for `/.asdf/installs/` |
| `detectPacman` | function | memoized async: `() => Promise<boolean>` — `pacman -Qo {execPath}`, gated on Arch family |
| `detectDeb` | function | memoized async: `() => Promise<boolean>` — `dpkg -S {execPath}`, gated on Debian family |
| `detectRpm` | function | memoized async: `() => Promise<boolean>` — `rpm -qf {execPath}`, gated on Fedora/RHEL/SUSE family |
| `detectApk` | function | memoized async: `() => Promise<boolean>` — `apk info --who-owns {execPath}`, gated on Alpine family |
| `getPackageManager()` | function | memoized async: `() => Promise<PackageManager>` |

**Detection priority (sync first, then async):**
1. `detectHomebrew()` — sync, path-based
2. `detectWinget()` — sync, path-based
3. `detectMise()` — sync, path-based
4. `detectAsdf()` — sync, path-based
5. `detectPacman()` — async, distro-gated
6. `detectApk()` — async, distro-gated
7. `detectDeb()` — async, distro-gated
8. `detectRpm()` — async, distro-gated
9. `'unknown'` — fallback

**Distro gating:** Before running package manager commands, reads `/etc/os-release` and checks distro family to avoid false positives (e.g., `pacman` game on Ubuntu).

---

#### `pidLock.ts` (433 lines)

PID-based version locking — detects crashed processes immediately.

**Exports:**
| Name | Kind | Signature |
|------|------|-----------|
| `VersionLockContent` | type | `{ pid: number; version: string; execPath: string; acquiredAt: number }` |
| `LockInfo` | type | `{ version: string; pid: number; isProcessRunning: boolean; execPath: string; acquiredAt: Date; lockFilePath: string }` |
| `isPidBasedLockingEnabled()` | function | `() => boolean` |
| `isProcessRunning(pid)` | function | `(number) => boolean` |
| `readLockContent(lockFilePath)` | function | `(string) => VersionLockContent \| null` |
| `isLockActive(lockFilePath)` | function | `(string) => boolean` |
| `tryAcquireLock(versionPath, lockFilePath)` | function | `(string, string) => Promise<(() => void) \| null>` |
| `acquireProcessLifetimeLock(versionPath, lockFilePath)` | function | `(string, string) => Promise<boolean>` |
| `withLock(versionPath, lockFilePath, callback)` | function | `(string, string, fn) => Promise<boolean>` |
| `getAllLockInfo(locksDir)` | function | `(string) => LockInfo[]` |
| `cleanupStaleLocks(locksDir)` | function | `(string) => number` |

**Constants:**
- `FALLBACK_STALE_MS = 2 * 60 * 60 * 1000` (2 hours)

**Lock format:** JSON file in locks directory containing `{ pid, version, execPath, acquiredAt }`.

**`isPidBasedLockingEnabled`:** GrowthBook gate `tengu_pid_based_version_locking`, overridable by `ENABLE_PID_BASED_VERSION_LOCKING` env var.

**`isLockActive` checks:**
1. Read lock content (valid JSON with required fields?)
2. Is process running? (`process.kill(pid, 0)`)
3. Is it actually a Claude process? (validates command contains 'claude' or exec path)
4. Fallback: if lock > 2 hours old and we can't validate, treat as potentially stale

**`tryAcquireLock`:**
1. Check `isLockActive` — if active, return null
2. Write lock file with current PID
3. Verify we won the race (re-read, check PID)
4. Return release function (unlinks if PID still matches)

**`cleanupStaleLocks`:** Handles both PID-based JSON files and legacy proper-lockfile directories.

---

## Group 5: Telemetry System (`utils/telemetry/`)

**9 files | 3,270 total lines** — Full telemetry pipeline: OTel events, logging, tracing, Perfetto, BigQuery, plugin telemetry.

### Architecture Overview

The telemetry system provides three independent data pipelines:
1. **OpenTelemetry Events/Logs** — Claude-code specific events via OTel log records
2. **OpenTelemetry Metrics** — Via MeterProvider, exported to OTLP/BigQuery/Prometheus
3. **Session Tracing** — Span-based tracing of interactions, LLM requests, and tool calls
4. **Perfetto Tracing** — Chrome Trace Event format for ui.perfetto.dev (ant-only)
5. **Plugin Telemetry** — Privacy-preserving plugin lifecycle events with PII redaction

---

### File-by-File Documentation

#### `events.ts` (75 lines)

OpenTelemetry event logging helper.

**Exports:**
| Name | Kind | Signature |
|------|------|-----------|
| `redactIfDisabled(content)` | function | `(string) => string` — returns `<REDACTED>` if user prompt logging disabled |
| `logOTelEvent(eventName, metadata?)` | function | `(string, { [key: string]: string \| undefined }?) => Promise<void>` |

**Event attributes:**
- `event.name`, `event.timestamp` (ISO), `event.sequence` (monotonic)
- `prompt.id` (from session state)
- `workspace.host_paths` (from `CLAUDE_CODE_WORKSPACE_HOST_PATHS`, split on `|`)
- Telemetry attributes from `getTelemetryAttributes()`
- Custom metadata (undefined values filtered)

**Gating:** Skips if no event logger initialized (warns once), skips in `NODE_ENV=test`.

---

#### `logger.ts` (26 lines)

OpenTelemetry diagnostic logger implementation.

**Exports:**
| Name | Kind | Description |
|------|------|-------------|
| `ClaudeCodeDiagLogger` | class | Implements `DiagLogger` from `@opentelemetry/api` |

**Behavior:** `error` and `warn` log to both `logError` and `logForDebugging`. `info`, `debug`, `verbose` are no-ops.

---

#### `sessionTracing.ts` (927 lines)

High-level span-based tracing API using OpenTelemetry.

**Exports:**
| Name | Kind | Signature |
|------|------|-----------|
| `Span` | type re-export | From `@opentelemetry/api` |
| `isBetaTracingEnabled` | re-export | From `./betaSessionTracing.js` |
| `LLMRequestNewContext` | type re-export | From `./betaSessionTracing.js` |
| `isEnhancedTelemetryEnabled()` | function | `() => boolean` |
| `startInteractionSpan(userPrompt)` | function | `(string) => Span` |
| `endInteractionSpan()` | function | `() => void` |
| `startLLMRequestSpan(model, newContext?, messagesForAPI?, fastMode?)` | function | `(string, LLMRequestNewContext?, APIMessage[]?, boolean?) => Span` |
| `endLLMRequestSpan(span?, metadata?)` | function | `(Span?, { inputTokens?, outputTokens?, cacheReadTokens?, cacheCreationTokens?, success?, statusCode?, error?, attempt?, modelResponse?, modelOutput?, thinkingOutput?, hasToolCall?, ttftMs?, requestSetupMs?, attemptStartTimes? }?) => void` |
| `startToolSpan(toolName, toolAttributes?, toolInput?)` | function | `(string, Record<string, string\|number\|boolean>?, string?) => Span` |
| `endToolSpan(toolResult?, resultTokens?)` | function | `(string?, number?) => void` |
| `startToolBlockedOnUserSpan()` | function | `() => Span` |
| `endToolBlockedOnUserSpan(decision?, source?)` | function | `(string?, string?) => void` |
| `startToolExecutionSpan()` | function | `() => Span` |
| `endToolExecutionSpan(metadata?)` | function | `({ success?, error? }?) => void` |
| `addToolContentEvent(eventName, attributes)` | function | `(string, Record<string, string\|number\|boolean>) => void` |
| `getCurrentSpan()` | function | `() => Span \| null` |
| `executeInSpan(spanName, fn, attributes?)` | function | `(string, (Span) => Promise<T>, Record?) => Promise<T>` |
| `startHookSpan(hookEvent, hookName, numHooks, hookDefinitions)` | function | `(string, string, number, string) => Span` |
| `endHookSpan(span, metadata?)` | function | `(Span, { numSuccess?, numBlocking?, numNonBlockingError?, numCancelled? }?) => void` |

**Span types:** `interaction`, `llm_request`, `tool`, `tool.blocked_on_user`, `tool.execution`, `hook`

**Internal architecture:**
- `AsyncLocalStorage` for interaction and tool context propagation
- `activeSpans: Map<string, WeakRef<SpanContext>>` — WeakRef-based span registry
- `strongSpans: Map<string, SpanContext>` — for spans not in ALS (LLM requests, blocked-on-user, tool execution, hooks)
- Lazy cleanup interval (60s) evicts orphaned spans older than 30 minutes
- Perfetto spans are started/ended in parallel with OTel spans

**`isEnhancedTelemetryEnabled`:** Feature gate `ENHANCED_TELEMETRY_BETA` + env var override + ant user OR GrowthBook gate `enhanced_telemetry_beta`.

---

#### `perfettoTracing.ts` (1,120 lines)

Chrome Trace Event format tracing for visualization in `ui.perfetto.dev` (ant-only).

**Exports:**
| Name | Kind | Signature |
|------|------|-----------|
| `TraceEventPhase` | type | `'B' \| 'E' \| 'X' \| 'i' \| 'C' \| 'b' \| 'n' \| 'e' \| 'M'` |
| `TraceEvent` | type | JSON structure with `name, cat, ph, ts, pid, tid, dur?, args?, id?, scope?` |
| `initializePerfettoTracing()` | function | `() => void` — enables via `CLAUDE_CODE_PERFETTO_TRACE=1` or path |
| `isPerfettoTracingEnabled()` | function | `() => boolean` |
| `registerAgent(agentId, agentName, parentAgentId?)` | function | `(string, string, string?) => void` |
| `unregisterAgent(agentId)` | function | `(string) => void` |
| `startLLMRequestPerfettoSpan(args)` | function | `({ model, promptTokens?, messageId?, isSpeculative?, querySource? }) => string` (returns spanId) |
| `endLLMRequestPerfettoSpan(spanId, metadata)` | function | `(string, { ttftMs?, ttltMs?, promptTokens?, outputTokens?, cacheReadTokens?, cacheCreationTokens?, messageId?, success?, error?, requestSetupMs?, attemptStartTimes? }) => void` |
| `startToolPerfettoSpan(toolName, args?)` | function | `(string, Record<string, unknown>?) => string` |
| `endToolPerfettoSpan(spanId, metadata?)` | function | `(string, { success?, error?, resultTokens? }?) => void` |
| `startUserInputPerfettoSpan(context?)` | function | `(string?) => string` |
| `endUserInputPerfettoSpan(spanId, metadata?)` | function | `(string, { decision?, source? }?) => void` |
| `emitPerfettoInstant(name, category, args?)` | function | `(string, string, Record<string, unknown>?) => void` |
| `emitPerfettoCounter(name, values)` | function | `(string, Record<string, number>) => void` |
| `startInteractionPerfettoSpan(userPrompt?)` | function | `(string?) => string` |
| `endInteractionPerfettoSpan(spanId)` | function | `(string) => void` |
| `getPerfettoEvents()` | function | `() => TraceEvent[]` — for testing |
| `resetPerfettoTracer()` | function | `() => void` — for testing |
| `triggerPeriodicWriteForTesting()` | function | `() => Promise<void>` |
| `evictStaleSpansForTesting()` | function | `() => void` |
| `MAX_EVENTS_FOR_TESTING` | const | `= MAX_EVENTS` |
| `evictOldestEventsForTesting()` | function | `() => void` |

**Constants:**
- `MAX_EVENTS = 100_000` — events ring buffer
- `STALE_SPAN_TTL_MS = 30 * 60 * 1000` (30 minutes)

**Architecture:**
- Events stored in `events[]` and `metadataEvents[]` arrays
- `pendingSpans: Map<string, PendingSpan>` for begin/end pairs
- `agentRegistry: Map<string, AgentInfo>` for swarm agent hierarchy tracking
- Numeric PID mapping via `agentIdToProcessId`
- Periodic full-trace writes if `CLAUDE_CODE_PERFETTO_WRITE_INTERVAL_S` set
- Stale span eviction every 60s
- Event eviction at MAX_EVENTS (drops oldest half, inserts marker)
- Three exit handlers: cleanup registry (async), beforeExit (async), exit (sync fallback)

**LLM request Perfetto spans include sub-spans:**
- Request Setup (with retry attempt sub-spans if multiple attempts)
- First Token (with ITPS and cache hit rate)
- Sampling (with OTPS)
- API Call (parent, with duration, token counts, error info)

**Trace output:** `~/.claude/traces/trace-{sessionId}.json` in Chrome Trace Event format.

---

#### `pluginTelemetry.ts` (289 lines)

Privacy-preserving plugin telemetry with PII redaction.

**Exports:**
| Name | Kind | Signature/Value |
|------|------|-----------------|
| `hashPluginId(name, marketplace?)` | function | `(string, string?) => string` — SHA-256(prefix:16) opaque hash |
| `TelemetryPluginScope` | type | `'official' \| 'org' \| 'user-local' \| 'default-bundle'` |
| `getTelemetryPluginScope(name, marketplace, managedNames)` | function | `(string, string \| undefined, Set<string> \| null) => TelemetryPluginScope` |
| `EnabledVia` | type | `'user-install' \| 'org-policy' \| 'default-enable' \| 'seed-mount'` |
| `InvocationTrigger` | type | `'user-slash' \| 'claude-proactive' \| 'nested-skill'` |
| `SkillExecutionContext` | type | `'fork' \| 'inline' \| 'remote'` |
| `InstallSource` | type | `'cli-explicit' \| 'ui-discover' \| 'ui-suggestion' \| 'deep-link'` |
| `getEnabledVia(plugin, managedNames, seedDirs)` | function | `(LoadedPlugin, Set<string>\|null, string[]) => EnabledVia` |
| `buildPluginTelemetryFields(name, marketplace, managedNames?)` | function | `(string, string\|undefined, Set<string>\|null?) => { plugin_id_hash, plugin_scope, plugin_name_redacted, marketplace_name_redacted, is_official_plugin }` |
| `buildPluginCommandTelemetryFields(pluginInfo, managedNames?)` | function | `({ pluginManifest, repository }, Set<string>\|null?) => ReturnType<typeof buildPluginTelemetryFields>` |
| `logPluginsEnabledForSession(plugins, managedNames, seedDirs)` | function | `(LoadedPlugin[], Set<string>\|null, string[]) => void` |
| `PluginCommandErrorCategory` | type | `'network' \| 'not-found' \| 'permission' \| 'validation' \| 'unknown'` |
| `classifyPluginCommandError(error)` | function | `(unknown) => PluginCommandErrorCategory` |
| `logPluginLoadErrors(errors, managedNames)` | function | `(PluginError[], Set<string>\|null) => void` |

**Twin-column privacy pattern:**
- `_PROTO_plugin_name` → routes to PII-tagged BQ column (raw value)
- `plugin_name_redacted` → `'third-party'` for non-Anthropic plugins, real name for official/builtin
- `plugin_id_hash` → opaque SHA-256 prefix for per-plugin aggregation without PII exposure

**Hash salt:** `'claude-plugin-telemetry-v1'` — fixed across all repos, enables cross-org distinct-count.

---

#### `bigqueryExporter.ts` (252 lines)

Custom OpenTelemetry metrics exporter that sends to Anthropic's internal BigQuery pipeline.

**Exports:**
| Name | Kind | Description |
|------|------|-------------|
| `BigQueryMetricsExporter` | class | Implements `PushMetricExporter` |

**Constructor:** `(options?: { timeout?: number })` — endpoint defaults to `https://api.anthropic.com/api/claude_code/metrics`, ant users can override via `ANT_CLAUDE_CODE_METRICS_ENDPOINT`.

**Methods:**
| Method | Signature | Description |
|--------|-----------|-------------|
| `export(metrics, resultCallback)` | `(ResourceMetrics, (ExportResult) => void) => Promise<void>` | Transforms metrics, sends POST to BigQuery API |
| `shutdown()` | `() => Promise<void>` | Sets shutdown flag, force flushes |
| `forceFlush()` | `() => Promise<void>` | Awaits all pending exports |
| `selectAggregationTemporality()` | `() => AggregationTemporality` | Always returns DELTA |

**Gating:** Skips if trust dialog not accepted (unless non-interactive), skips if organization-level metrics opt-out is enabled.

**Payload format:** `{ resource_attributes: { service.name, service.version, os.type, os.version, host.arch, aggregation.temporality, wsl.version?, user.customer_type, user.subscription_type? }, metrics: [...] }`

---

#### `skillLoadedEvent.ts` (39 lines)

Logs `tengu_skill_loaded` events for each skill at session startup.

**Exports:**
| Name | Kind | Signature |
|------|------|-----------|
| `logSkillsLoaded(cwd, contextWindowTokens)` | function | `(string, number) => Promise<void>` |

**Fields per skill:** `_PROTO_skill_name`, `skill_source`, `skill_loaded_from`, `skill_budget`, `skill_kind` (optional).

---

#### `betaSessionTracing.ts` (491 lines)

Beta tracing features for detailed debugging (Honeycomb-compatible).

**Exports:**
| Name | Kind | Signature |
|------|------|-----------|
| `isBetaTracingEnabled()` | function | `() => boolean` |
| `clearBetaTracingState()` | function | `() => void` |
| `truncateContent(content, maxSize?)` | function | `(string, number?) => { content: string; truncated: boolean }` |
| `LLMRequestNewContext` | type | `{ systemPrompt?: string; querySource?: string; tools?: string }` |
| `addBetaInteractionAttributes(span, userPrompt)` | function | `(Span, string) => void` |
| `addBetaLLMRequestAttributes(span, newContext?, messagesForAPI?)` | function | `(Span, LLMRequestNewContext?, APIMessage[]?) => void` |
| `addBetaLLMResponseAttributes(endAttributes, metadata?)` | function | `(Record<string, string\|number\|boolean>, { modelOutput?, thinkingOutput? }?) => void` |
| `addBetaToolInputAttributes(span, toolName, toolInput)` | function | `(Span, string, string) => void` |
| `addBetaToolResultAttributes(endAttributes, toolName, toolResult)` | function | `(Record<string, string\|number\|boolean>, string\|number\|boolean, string) => void` |

**Constants:**
- `MAX_CONTENT_SIZE = 60 * 1024` (60KB, Honeycomb limit is 64KB)
- `SYSTEM_REMINDER_REGEX` — detects `<system-reminder>...</system-reminder>` wrappers

**Enabling:** Requires `ENABLE_BETA_TRACING_DETAILED=1` AND `BETA_TRACING_ENDPOINT`. For external users: enabled in SDK/headless mode OR GrowthBook gate `tengu_trace_lantern`.

**Content visibility matrix:**

| Content | External | Ant |
|---------|----------|-----|
| System prompts | Yes | Yes |
| Model output | Yes | Yes |
| Thinking output | No | Yes |
| Tools | Yes | Yes |
| new_context | Yes | Yes |

**Hash-based deduplication:**
- `seenHashes: Set<string>` — system prompts and tool schemas logged once per unique hash
- `lastReportedMessageHash: Map<string, string>` — per-querySource tracking for incremental context delta

**new_context computation:**
1. Find last reported message hash for this querySource
2. Only send messages after the last-reported position
3. Filter to user messages only (not assistant)
4. Separate system reminders from regular content
5. Truncate at 60KB if needed

---

#### `instrumentation.ts` (825 lines)

Main telemetry initialization — sets up OpenTelemetry providers for metrics, logs, and traces.

**Exports:**
| Name | Kind | Signature |
|------|------|-----------|
| `bootstrapTelemetry()` | function | `() => void` — copies ANT_OTEL_* env vars to OTEL_* for ant users, sets default tempoality to delta |
| `parseExporterTypes(value)` | function | `(string \| undefined) => string[]` — splits comma-separated, filters 'none' |
| `isTelemetryEnabled()` | function | `() => boolean` — checks `CLAUDE_CODE_ENABLE_TELEMETRY` |
| `initializeTelemetry()` | function | `() => Promise<Meter>` — main entry point |
| `flushTelemetry()` | function | `() => Promise<void>` — force flushes all providers |

**Constants:**
- `DEFAULT_METRICS_EXPORT_INTERVAL_MS = 60000`
- `DEFAULT_LOGS_EXPORT_INTERVAL_MS = 5000`
- `DEFAULT_TRACES_EXPORT_INTERVAL_MS = 5000`
- `BIGQUERY_EXPORT_INTERVAL_MS = 5 * 60 * 1000`

**`TelemetryTimeoutError`** — internal class for timeout race conditions.

**`initializeTelemetry` flow:**
1. Bootstrap (ANT_OTEL_* → OTEL_*)
2. Strip console exporters in stream-json mode (would break SDK line reader)
3. Set OTEL diag logger to `ClaudeCodeDiagLogger` at ERROR level
4. Initialize Perfetto tracing
5. Build metric readers:
   - Customer exporters (if `isTelemetryEnabled()`)
   - BigQuery exporter (for API customers, C4E, Teams)
6. Build resource from detectors (env, OS, host.arch, WSL version)
7. **Branch A — Beta tracing enabled:**
   - Initialize beta tracing (separate HTTP exporter to `BETA_TRACING_ENDPOINT`)
   - Set up MeterProvider only (no regular logs/traces)
   - Register shutdown with timeout
8. **Branch B — Regular telemetry:**
   - Set up MeterProvider
   - If telemetry enabled: set up LoggerProvider with OTLP log exporters
   - If enhanced telemetry: set up TracerProvider with OTLP trace exporters
9. Register cleanup handler for graceful shutdown

**Exporter protocol support:**
- For each signal (metrics, logs, traces): dynamically imports the appropriate OTLP exporter based on `OTEL_EXPORTER_OTLP_PROTOCOL` (grpc, http/json, http/protobuf)
- Console exporters available as debug fallback
- Prometheus exporter available for metrics
- Dynamic imports keep unused SDK packages out of the bundle

**Proxy/mTLS support:** `getOTLPExporterConfig()` configures `HttpsProxyAgent` with optional mTLS certs and custom CA certificates. Supports dynamic OAuth headers via `otelHeadersHelper`.

**Shutdown:** All providers flushed in parallel with configurable timeout (`CLAUDE_CODE_OTEL_SHUTDOWN_TIMEOUT_MS`, default 2000ms). `endInteractionSpan()` called before shutdown.

---

## Group 6: Swarm Backends (`utils/swarm/backends/`)

**9 files | 2,849 total lines** — Multi-agent swarm execution backends (tmux panes, iTerm2 panes, in-process).

### Architecture Overview

The swarm system allows Claude Code to spawn teammate agents running in parallel. Three execution backends:
1. **InProcessBackend** — same Node.js process, isolated via AsyncLocalStorage, file-based mailbox communication
2. **TmuxBackend** — pane-based, uses tmux split-pane with leader layout (30%/70%) or standalone swarm session
3. **ITermBackend** — pane-based, uses iTerm2 native split panes via `it2` CLI tool

All backends implement `PaneBackend` (low-level pane ops). `PaneBackendExecutor` adapts `PaneBackend` → `TeammateExecutor` (high-level lifecycle). Backend selection is auto-detected via a priority chain.

---

### File-by-File Documentation

#### `types.ts` (311 lines)

Core type definitions for the swarm backend system.

**Types:**
| Name | Definition |
|------|-----------|
| `BackendType` | `'tmux' \| 'iterm2' \| 'in-process'` |
| `PaneBackendType` | `'tmux' \| 'iterm2'` |
| `PaneId` | `string` (opaque) |
| `CreatePaneResult` | `{ paneId: PaneId; isFirstTeammate: boolean }` |
| `PaneBackend` | Interface with `type`, `displayName`, `supportsHideShow`, `isAvailable()`, `isRunningInside()`, `createTeammatePaneInSwarmView()`, `sendCommandToPane()`, `setPaneBorderColor()`, `setPaneTitle()`, `enablePaneBorderStatus()`, `rebalancePanes()`, `killPane()`, `hidePane()`, `showPane()` |
| `BackendDetectionResult` | `{ backend: PaneBackend; isNative: boolean; needsIt2Setup?: boolean }` |
| `TeammateIdentity` | `{ name: string; teamName: string; color?: AgentColorName; planModeRequired?: boolean }` |
| `TeammateSpawnConfig` | `TeammateIdentity & { prompt: string; cwd: string; model?: string; systemPrompt?: string; systemPromptMode?: 'default'\|'replace'\|'append'; worktreePath?: string; parentSessionId: string; permissions?: string[]; allowPermissionPrompts?: boolean }` |
| `TeammateSpawnResult` | `{ success: boolean; agentId: string; error?: string; abortController?: AbortController; taskId?: string; paneId?: PaneId }` |
| `TeammateMessage` | `{ text: string; from: string; color?: string; timestamp?: string; summary?: string }` |
| `TeammateExecutor` | Interface with `type`, `isAvailable()`, `spawn()`, `sendMessage()`, `terminate()`, `kill()`, `isActive()` |

**Type guard:** `isPaneBackend(type: BackendType): type is 'tmux' | 'iterm2'`

---

#### `detection.ts` (128 lines)

Environment detection for swarm backends.

**Exports:**
| Name | Kind | Signature |
|------|------|-----------|
| `isInsideTmuxSync()` | function | `() => boolean` — reads `ORIGINAL_USER_TMUX` |
| `isInsideTmux()` | function | `() => Promise<boolean>` — cached async version |
| `getLeaderPaneId()` | function | `() => string \| null` — `ORIGINAL_TMUX_PANE` captured at module load |
| `isTmuxAvailable()` | function | `() => Promise<boolean>` — `tmux -V` exit code |
| `isInITerm2()` | function | `() => boolean` — cached, checks `TERM_PROGRAM`, `ITERM_SESSION_ID`, `env.terminal` |
| `IT2_COMMAND` | const | `'it2'` |
| `isIt2CliAvailable()` | function | `() => Promise<boolean>` — `it2 session list` (not `--version`) |
| `resetDetectionCache()` | function | `() => void` — for testing |

**Key design decisions:**
- `TMUX` env var captured at module load (before `Shell.ts` overrides it)
- `iTerm2` detection uses 3 indicators: TERM_PROGRAM, ITERM_SESSION_ID, env.terminal
- `it2` availability uses `session list` (not `--version`) because `--version` succeeds even when Python API is disabled

---

#### `InProcessBackend.ts` (339 lines)

In-process teammate execution backend.

**Exports:**
| Name | Kind | Signature |
|------|------|-----------|
| `InProcessBackend` | class | Implements `TeammateExecutor` |
| `createInProcessBackend()` | function | `() => InProcessBackend` |

**Class fields:**
- `type = 'in-process'`
- `context: ToolUseContext | null`

**Methods:**
| Method | Description |
|--------|-------------|
| `setContext(context)` | Sets ToolUseContext for AppState access |
| `isAvailable()` | Always returns true (no external deps) |
| `spawn(config)` | Calls `spawnInProcessTeammate()` then `startInProcessTeammate()`. Passes prompt through task state, strips messages from toolUseContext to avoid pinning parent conversation |
| `sendMessage(agentId, message)` | Writes to file-based mailbox via `writeToMailbox()` |
| `terminate(agentId, reason?)` | Sends shutdown request via mailbox, marks task as `shutdownRequested`. Skips if already requested |
| `kill(agentId)` | Calls `killInProcessTeammate()` which aborts the AbortController |
| `isActive(agentId)` | Checks task status is 'running' and AbortController not aborted |

---

#### `it2Setup.ts` (245 lines)

iTerm2 it2 CLI setup and verification.

**Exports:**
| Name | Kind | Signature/Value |
|------|------|-----------------|
| `PythonPackageManager` | type | `'uvx' \| 'pipx' \| 'pip'` |
| `It2InstallResult` | type | `{ success: boolean; error?: string; packageManager?: PythonPackageManager }` |
| `It2VerifyResult` | type | `{ success: boolean; error?: string; needsPythonApiEnabled?: boolean }` |
| `detectPythonPackageManager()` | function | `() => Promise<PythonPackageManager \| null>` |
| `isIt2CliAvailable()` | function | `() => Promise<boolean>` (independent copy from detection.ts) |
| `installIt2(packageManager)` | function | `(PythonPackageManager) => Promise<It2InstallResult>` |
| `verifyIt2Setup()` | function | `() => Promise<It2VerifyResult>` |
| `getPythonApiInstructions()` | function | `() => string[]` |
| `markIt2SetupComplete()` | function | `() => void` |
| `setPreferTmuxOverIterm2(prefer)` | function | `(boolean) => void` |
| `getPreferTmuxOverIterm2()` | function | `() => boolean` |

**Package manager detection order:** uv → pipx → pip → pip3

**Installation:** Runs from home directory to avoid project-level pip.conf/uv.toml which could redirect to malicious PyPI server.

---

#### `ITermBackend.ts` (370 lines)

iTerm2 native split pane backend via it2 CLI.

**Exports:**
| Name | Kind | Description |
|------|------|-------------|
| `ITermBackend` | class | Implements `PaneBackend` |

**Class fields:** `type = 'iterm2'`, `displayName = 'iTerm2'`, `supportsHideShow = false`

**Module-level state:**
- `teammateSessionIds: string[]` — tracked session IDs
- `firstPaneUsed: boolean` — layout state
- `paneCreationLock: Promise<void>` — sequential pane creation

**Methods:**

| Method | Description |
|--------|-------------|
| `isAvailable()` | Checks `isInITerm2()` AND `isIt2CliAvailable()` |
| `isRunningInside()` | Delegates to `isInITerm2()` |
| `createTeammatePaneInSwarmView(name, color)` | Acquires lock, splits vertically from leader session (first teammate) or horizontally from last teammate. At-fault recovery: if targeted session is dead, prunes and retries |
| `sendCommandToPane(paneId, command)` | `it2 session run -s {paneId} {command}` |
| `setPaneBorderColor(...)` | No-op (perf: each it2 call spawns Python process) |
| `setPaneTitle(...)` | No-op (perf) |
| `enablePaneBorderStatus(...)` | No-op (iTerm2 doesn't have pane border status concept) |
| `rebalancePanes(...)` | No-op (iTerm2 handles automatically) |
| `killPane(paneId)` | `it2 session close -f -s {paneId}`, cleans up module state |
| `hidePane(...)` | Not supported (returns false) |
| `showPane(...)` | Not supported (returns false) |

**Pane layout:** Leader on left, teammates stacked vertically on right. Session IDs tracked from `ITERM_SESSION_ID` env var (extracts UUID after colon).

**Self-registration:** `registerITermBackend(ITermBackend)` called at module top level.

---

#### `PaneBackendExecutor.ts` (354 lines)

Adapter converting `PaneBackend` → `TeammateExecutor`.

**Exports:**
| Name | Kind | Signature |
|------|------|-----------|
| `PaneBackendExecutor` | class | Implements `TeammateExecutor` |
| `createPaneBackendExecutor(backend)` | function | `(PaneBackend) => PaneBackendExecutor` |

**Constructor:** `(backend: PaneBackend)` — stores backend, initializes `spawnedTeammates` map.

**Methods:**

| Method | Description |
|--------|-------------|
| `setContext(context)` | Stores ToolUseContext for AppState access |
| `isAvailable()` | Delegates to backend |
| `spawn(config)` | 1) Assign color, 2) Create pane via backend, 3) Enable pane border status on first teammate (tmux), 4) Build CLI spawn command with identity flags (`--agent-id`, `--agent-name`, `--team-name`, `--agent-color`, `--parent-session-id`), 5) Merge inherited CLI flags + custom model, 6) Send command to pane, 7) Register cleanup to kill panes on leader exit, 8) Send initial prompt via mailbox |
| `sendMessage(agentId, message)` | Writes to file-based mailbox |
| `terminate(agentId, reason?)` | Sends shutdown request JSON via mailbox |
| `kill(agentId)` | Kills pane via backend, removes from spawned map |
| `isActive(agentId)` | Returns true if in spawned map (best-effort) |

**Spawn command format:** `cd {cwd} && env {envStr} {binaryPath} --agent-id {id} --agent-name {name} ... {flags}`

**Cleanup:** On first spawn, registers cleanup handler that kills all spawned panes on leader exit (SIGHUP, etc.).

---

#### `registry.ts` (464 lines)

Backend detection, selection, and caching registry.

**Exports:**
| Name | Kind | Signature |
|------|------|-----------|
| `ensureBackendsRegistered()` | function | `() => Promise<void>` — dynamic imports TmuxBackend + ITermBackend |
| `registerTmuxBackend(backendClass)` | function | `(new () => PaneBackend) => void` |
| `registerITermBackend(backendClass)` | function | `(new () => PaneBackend) => void` |
| `detectAndGetBackend()` | function | `() => Promise<BackendDetectionResult>` |
| `getBackendByType(type)` | function | `(PaneBackendType) => PaneBackend` |
| `getCachedBackend()` | function | `() => PaneBackend \| null` |
| `getCachedDetectionResult()` | function | `() => BackendDetectionResult \| null` |
| `markInProcessFallback()` | function | `() => void` |
| `isInProcessEnabled()` | function | `() => boolean` |
| `getResolvedTeammateMode()` | function | `() => 'in-process' \| 'tmux'` |
| `getInProcessBackend()` | function | `() => TeammateExecutor` |
| `getTeammateExecutor(preferInProcess?)` | function | `(boolean?) => Promise<TeammateExecutor>` |
| `resetBackendDetection()` | function | `() => void` — for testing |

**Detection priority (`detectAndGetBackend`):**
1. Inside tmux → use tmux (always, even in iTerm2)
2. In iTerm2 + it2 available → use ITermBackend
3. In iTerm2 + it2 not available + tmux available → use tmux (fallback), signal it2 setup needed
4. In iTerm2 + no it2 + no tmux → throw error with install instructions
5. tmux available (external) → use tmux (external swarm session mode)
6. Nothing available → throw error with platform-specific tmux install instructions

**`isInProcessEnabled` logic:**
1. Non-interactive session → always true
2. `teammateMode === 'in-process'` → true
3. `teammateMode === 'tmux'` → false
4. `'auto'` mode:
   - If fallback active (prior spawn fell back) → true
   - Inside tmux → false (use pane backend)
   - In iTerm2 → false (use pane backend)
   - Otherwise → true (use in-process)

**Caching:** Once detected, backend selection and executor instances are frozen for process lifetime.

---

#### `teammateModeSnapshot.ts` (87 lines)

Captures teammate mode at session startup (immutable for session lifetime).

**Exports:**
| Name | Kind | Signature |
|------|------|-----------|
| `TeammateMode` | type | `'auto' \| 'tmux' \| 'in-process'` |
| `setCliTeammateModeOverride(mode)` | function | `(TeammateMode) => void` |
| `getCliTeammateModeOverride()` | function | `() => TeammateMode \| null` |
| `clearCliTeammateModeOverride(newMode)` | function | `(TeammateMode) => void` |
| `captureTeammateModeSnapshot()` | function | `() => void` |
| `getTeammateModeFromSnapshot()` | function | `() => TeammateMode` |

**Snapshot precedence:** CLI override (`--teammate-mode`) > config (`globalConfig.teammateMode`) > `'auto'` default.

---

#### `TmuxBackend.ts` (764 lines)

Tmux pane management backend.

**Exports:**
| Name | Kind | Description |
|------|------|-------------|
| `TmuxBackend` | class | Implements `PaneBackend` |

**Class fields:** `type = 'tmux'`, `displayName = 'tmux'`, `supportsHideShow = true`

**Module-level state:**
- `firstPaneUsedForExternal: boolean` — tracks external swarm session initialization
- `cachedLeaderWindowTarget: string | null` — session:window format
- `paneCreationLock: Promise<void>` — sequential pane creation

**Constants:**
- `PANE_SHELL_INIT_DELAY_MS = 200`

**Methods:**

| Method | Description |
|--------|-------------|
| `isAvailable()` | Checks tmux binary exists |
| `isRunningInside()` | Checks if in tmux session |
| `createTeammatePaneInSwarmView(name, color)` | Acquires lock, routes to `createTeammatePaneWithLeader` (inside tmux) or `createTeammatePaneExternal` (outside) |
| `sendCommandToPane(paneId, command, useExternalSession)` | `tmux send-keys -t {paneId} {command} Enter` |
| `setPaneBorderColor(paneId, color, useExternalSession)` | `select-pane -P bg=default,fg={color}` + `set-option -p pane-border-style fg={color}` + `pane-active-border-style` |
| `setPaneTitle(paneId, name, color, useExternalSession)` | `select-pane -T {name}` + `pane-border-format` with color |
| `enablePaneBorderStatus(windowTarget?, useExternalSession?)` | `set-option -w pane-border-status top` |
| `rebalancePanes(windowTarget, hasLeader)` | Leader: main-vertical + 30% resize. Tiled: tiled layout |
| `killPane(paneId, useExternalSession)` | `tmux kill-pane -t {paneId}` |
| `hidePane(paneId, useExternalSession)` | Creates hidden session if needed, `break-pane -d -s {paneId} -t {HIDDEN_SESSION_NAME}:` |
| `showPane(paneId, targetWindowOrPane, useExternalSession)` | `join-pane -h -s {paneId} -t {target}`, reapplies main-vertical + 30% leader |

**Private methods:**

| Method | Description |
|--------|-------------|
| `getCurrentPaneId()` | Uses `TMUX_PANE` env var captured at startup or `display-message -p '#{pane_id}'` |
| `getCurrentWindowTarget()` | Cached `#{session_name}:#{window_index}` via leader's pane |
| `getCurrentWindowPaneCount(windowTarget?, useSwarmSocket?)` | `list-panes` count |
| `hasSessionInSwarm(sessionName)` | `has-session -t {name}` in swarm socket |
| `createExternalSwarmSession()` | Creates `claude-swarm` session with `swarm-view` window |
| `createTeammatePaneWithLeader(name, color)` | In-tmux layout: leader (30%), first teammate splits right (70%), subsequent split from existing teammates in semi-binary tree |
| `createTeammatePaneExternal(name, color)` | External swarm: first teammate uses existing pane, subsequent split horizontally/vertically in semi-binary tree |
| `rebalancePanesWithLeader(windowTarget)` | `select-layout main-vertical` + `resize-pane -x 30%` for leader |
| `rebalancePanesTiled(windowTarget)` | `select-layout tiled` |

**Semi-binary tree layout:** Teammates are split alternating horizontal/vertical from progressively selected target panes, creating an even distribution.

**Self-registration:** `registerTmuxBackend(TmuxBackend)` called at module top level.

---

## Summary Statistics

| Group | Files | Total Lines | Primary Responsibility |
|-------|-------|-------------|----------------------|
| Computer Use | 15 | ~1,560 | macOS remote desktop control via native Swift/Rust modules |
| Claude-in-Chrome | 7 | ~1,844 | Browser automation via Chrome extension + native messaging |
| Deep Links | 6 | ~1,382 | `claude-cli://` URI protocol handling + terminal launching |
| Native Installer | 5 | ~3,118 | Binary download, version management, locking, package manager detection |
| Telemetry | 9 | ~3,270 | OTel events/logs/metrics/traces, Perfetto, BigQuery export, plugin analytics |
| Swarm Backends | 9 | ~2,849 | Multi-agent execution via tmux panes, iTerm2 panes, or in-process |

**Grand total:** 51 files, ~14,023 lines
