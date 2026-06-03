# 01 — Ink Engine: Custom React-for-Terminal Renderer

> **96 files** | Core subsystem: custom reconciler, virtual DOM, flexbox layout, terminal I/O, ANSI parsing

## Overview

The Ink Engine is the rendering heart of Claude Code. It is a heavily customized fork of [Ink](https://github.com/vadimdemedes/ink) — React's `<Box>`/`<Text>` primitives adapted for terminal rendering. The engine takes React component trees, runs them through a custom reconciler (`ink/reconciler.ts`), performs flexbox layout via a pure-TypeScript Yoga port (`native-ts/yoga-layout/`), paints the result into a double-buffered screen buffer (`ink/screen.ts`), diffs against the previous frame (`ink/log-update.ts`), and emits minimal ANSI escape sequences to `stdout` (`ink/terminal.ts`). The result: a 60fps terminal UI that feels like a GUI.

---

## 1. Ink Root (`ink/`) — 43 Files

### 1.1 Core Lifecycle & Orchestration

#### `ink/ink.tsx` (1723 lines)
The central `Ink` class that owns the entire rendering lifecycle. Key responsibilities:

- **Constructor**: Takes `stdout`, `stdin`, `stderr` streams plus `exitOnCtrlC`, `patchConsole`, `waitUntilExit`, `onFrame` options. Creates a React reconciler container (`ConcurrentRoot`), initializes double-buffered frames (`frontFrame`/`backFrame`), sets up a `LogUpdate` instance for terminal output, configures the terminal (mouse tracking, kitty keyboard protocol, alt-screen), and starts the render loop.
- **render()**: Accepts a React element, schedules a React update via the reconciler. Manages alternate screen enter/exit, SIGCONT handling (full redraw on resume), and terminal resize detection via `SIGWINCH` → full invalidate.
- **Frame Loop**: After each React commit, runs Yoga `calculateLayout()` on the root node, calls the `renderer()` factory (which produces a screen buffer via `renderNodeToOutput`), applies search highlights and selection overlays, diffs the screen against the previous frame via `LogUpdate.render()`, optimizes the diff, and writes patches to `stdout`. Uses `scheduleRender` throttled at `FRAME_INTERVAL_MS` (16ms).
- **Selection Management**: Owns `SelectionState` (alt-screen only) — dispatches `startSelection`/`extendSelection`/`clearSelection` on mouse events. Applies inversion overlay post-render.
- **Click/Hover Dispatch**: Routes SGR mouse tracking events through `hitTest` → `dispatchClick`/`dispatchHover`, which walks the DOM tree to find the deepest containing element and bubbles events.
- **Scroll Drain**: Accumulates scroll wheel events in `pendingScrollDelta`; `render-node-to-output.ts` drains adaptively per frame (`SCROLL_MIN_PER_FRAME = 4`, proportional step up to innerHeight−1; xterm path uses `SCROLL_INSTANT_THRESHOLD = 5`, `SCROLL_STEP_MED/HIGH = 2/3`).
- **Pool Reset**: Every 5 minutes, resets `stylePool`, `charPool`, `hyperlinkPool` to prevent unbounded growth from long sessions.
- **Yoga Stats Collection**: Tracks `yogaVisited`, `yogaMeasured`, `yogaCacheHits`, `yogaLive` counters for performance monitoring (`onFrame` callback).

#### `ink/reconciler.ts` (512 lines)
The React reconciler — maps React's internal host component API to Ink's virtual DOM. This is what makes `<Box>`, `<Text>`, `<ScrollBox>` work as React components in a terminal.

- **Host Config**: Implements `createInstance`, `createTextInstance`, `appendChild`, `removeChild`, `insertBefore`, `commitUpdate`, `commitTextUpdate`, `prepareForCommit`, `resetAfterCommit`, `clearContainer`, `detachDeletedInstance`, `scheduleTimeout`, `cancelTimeout`, `noTimeout`, `getPublicInstance`, `supportsMutation`.
- **createInstance(type, props)**: Maps React element type strings (`'ink-box'`, `'ink-text'`, `'ink-scrollbox'`, `'ink-link'`, `'ink-progress'`, `'ink-raw-ansi'`) to `dom.createNode()` calls. Applies styles via `applyStyles()`. Wires event handlers to the `Dispatcher`.
- **commitUpdate**: Handles prop diffs — updates styles, event handlers, attributes. Also handles visibility toggling (`hideInstance`/`unhideInstance`), used by `<OffscreenFreeze>` for virtual scrolling.
- **resetAfterCommit**: The critical bridge between React and Yoga. After React commits mutations, this runs `calculateLayout()` on the root, collects timings, marks the last-commit timestamp. Calls `nodeCache.clear()` and `pendingClears` processing.
- **Commit Timing**: Exports `getLastCommitMs()` and `getLastYogaMs()` for performance monitoring. `recordYogaMs()` stores the last Yoga pass duration.
- **DevTools**: Conditionally imports `react-devtools-core` when `NODE_ENV === 'development'`.

#### `ink/renderer.ts` (178 lines)
The renderer factory — bridges the reconciler's DOM tree to screen buffer output.

- **createRenderer(node, stylePool)**: Returns a function that takes `{frontFrame, backFrame, isTTY, terminalWidth, terminalRows, altScreen, prevFrameContaminated}` and produces a new `Frame`.
- **Layout Validation**: Checks that `node.yogaNode?.getComputedHeight()` and `getComputedWidth()` return valid finite values before proceeding.
- **Screen Management**: Reads `charPool`/`hyperlinkPool` from the back buffer's screen. Creates or resizes the output `Screen` buffer. Handles the target-height computation for alt-screen vs main-screen mode.
- **Render Tree Walk**: Calls `renderNodeToOutput()` to walk the DOM tree and paint into the screen buffer. Applies `stickyScroll` auto-pin logic.
- **Scroll Optimization**: Reads `scrollHint` from `renderNodeToOutput` — when a single `ScrollBox`'s `scrollTop` changed and nothing else shifted, the hint enables hardware scroll (`DECSTBM + SU/SD`) instead of rewriting the entire viewport.
- **Layout Shift Detection**: Reads `didLayoutShift()` — when any node's position changed, forces full-damage diff instead of cell-level blit.

### 1.2 Virtual DOM

#### `ink/dom.ts` (484 lines)
The lightweight virtual DOM for terminal rendering — not a browser DOM. Defines the node types and the imperative API the reconciler calls.

- **Node Types**: `'ink-root'`, `'ink-box'`, `'ink-text'`, `'ink-virtual-text'`, `'ink-link'`, `'ink-progress'`, `'ink-raw-ansi'`, and `'#text'` (text nodes).
- **DOMElement Interface**: `{ nodeName, attributes, childNodes, textStyles?, yogaNode?, parentNode, style, dirty, isHidden?, _eventHandlers?, scrollTop?, pendingScrollDelta?, onComputeLayout?, onRender?, onImmediateRender?, hasRenderedContent? }`.
- **createNode(elementName)**: Creates a DOM element with the specified `nodeName`, initializes a Yoga layout node via `createLayoutNode()`, sets `dirty: true`.
- **createTextNode(text)**: Creates a `#text` text node with `nodeValue` set.
- **setTextNodeValue(node, text)**: Updates a text node's value and marks the parent dirty.
- **appendChildNode/removeChildNode/insertBeforeNode**: Mutate the child list, set parent references, mark parents dirty. `removeChildNode` adds the removed child's rect to `pendingClears`.
- **setAttribute/setStyle/setTextStyles**: Update node properties and mark dirty.
- **markDirty(node)**: Sets `dirty: true` on the node and recursively on all ancestors. Used as the damage-tracking mechanism — the render tree walk in `render-node-to-output` only re-renders dirty subtrees.
- **clearYogaNodeReferences(node)**: Resets yoga child references after removal, preventing stale pointer use.
- **scheduleRenderFrom(node)**: Walks up to the root and triggers a re-render on the parent Ink instance.

#### `ink/root.ts` (184 lines)
The public entry point for creating an Ink render instance.

- **render(element, options?)**: Creates an `Ink` instance, calls `ink.render(element)`. Returns `{ rerender, unmount, waitUntilExit, cleanup }`.
- **Options**: `{ stdout?, stdin?, stderr?, exitOnCtrlC?, patchConsole?, onFrame? }`.
- **Instance Registry**: Instances are tracked in `ink/instances.ts` (a simple `Set` of Ink instances). The root render function adds/removes instances.

#### `ink/instances.ts` (10 lines)
Tiny registry — a `Set<Ink>` of active Ink instances. Used for cleanup on exit.

### 1.3 Screen Buffer & Rendering

#### `ink/screen.ts` (1486 lines)
The terminal screen buffer — the heart of the rendering pipeline. A columnar grid of cells, plus shared pools for style/character/hyperlink interning.

- **Cell Structure**: `{ char: number (pool index), styleId: number, width: CellWidth, hyperlink: number (pool index), noWrap?: boolean }`. Each cell is a single grapheme cluster with its full rendering context.
- **CellWidth Enum**: `{ Single: 1, Double: 2, SpacerTail: -1, SpacerHead: -2 }`. Double-width characters (CJK, emoji) occupy two cells — the first holds the char, the second is a `SpacerTail` marker.
- **StylePool**: Interns ANSI style combinations via `@alcalzone/ansi-tokenize`. Each unique combination of (foreground, background, bold, dim, italic, underline, strikethrough, inverse) gets a numeric ID. The pool is session-lived (never reset). Exposes `transition(fromId, toId)` → cached transition escape sequence, avoiding `diffAnsiCodes` per cell in the hot path.
- **CharPool**: Interns character strings. ASCII characters use a direct `Int32Array` lookup for fast paths. Shared across screens so `blitRegion` can copy IDs directly.
- **HyperlinkPool**: Interns OSC 8 hyperlink URIs. Index 0 = no hyperlink. Resets every 5 minutes (generational) to prevent unbounded growth.
- **Screen Structure**: `{ width, height, cells: CellBuffer[], stylePool, charPool, hyperlinkPool, noSelect: Uint8Array, softWrap: Uint8Array }`. `cells` is indexed as `row * width + col`. `noSelect` marks gutters (⎿, line numbers) as unselectable. `softWrap` marks line-continuations from word wrap.
- **blitRegion(src, srcScreen, dstScreen, dstX, dstY, srcX, srcY, w, h)**: Copy a rectangular region between screens, preserving pool IDs. Core optimization — unchanged parts of the tree get blitted instead of repainted.
- **shiftRows(screen, count, top, bottom)**: Shift rows within a scroll region. Used for the DECSTBM hardware-scroll optimization.
- **setCellAt/createScreen/resetScreen**: Primitive cell manipulation and screen lifecycle.
- **diffEach(prev, next, fn)**: Cell-by-cell diff iterator. Calls `fn(col, row, prevCell, nextCell)` for every cell that changed. Used by `LogUpdate` to produce minimal ANSI patches.

#### `ink/render-node-to-output.ts` (1462 lines)
The DOM→screen-buffer renderer — walks the reconciled DOM tree and paints each node's output into a `Screen` buffer via an `Output` instance.

- **renderNodeToOutput(node, output, options)**: The main recursive function. For each node:
  1. Checks `node.dirty` — if clean, blits from cache (`nodeCache.get(node)` rect) and skips subtree.
  2. Reads Yoga-computed position/size from the layout node.
  3. Applies border rendering (`render-border.ts`) if the node has border styles.
  4. For text-like nodes (`ink-text`, `ink-virtual-text`, `ink-link`): squashes text nodes via `squashTextNodesToSegments()`, wraps text if needed, applies ANSI colors via `applyTextStyles()`, writes to output.
  5. For raw ANSI nodes (`ink-raw-ansi`): writes ANSI content directly.
  6. Recursively renders children, applying viewport culling for `overflow: hidden`/`scroll` containers.
  7. For `overflow: scroll` ScrollBox containers: applies `scrollTop` offset to child painting, records `scrollHint` for hardware scroll optimization.
  8. Posts render to `nodeCache` for next-frame blit.
- **ScrollBox Viewport Culling**: Only renders children whose Yoga-rect intersects the viewport. Uses `getComputedTop()` cached from layout for O(dirty) culling.
- **Border Rendering**: Renders `borderStyle` using `cli-boxes` box-drawing characters. Supports custom dashed borders and embedded border text (top/bottom labels).
- **Absolute Positioning**: Handles `position: absolute` nodes — paints them in a second pass with `left`/`top`/`right`/`bottom` offsets relative to the nearest positioned ancestor.
- **Layout Shift Detection**: Sets `layoutShifted = true` when any node's rendered rect differs from its cached rect (from `nodeCache`). This gates whether the diff engine uses blit (cheap) or full-damage (expensive).
- **Scroll Drain**: Processes `pendingScrollDelta` from mouse wheel events via adaptive drain in `render-node-to-output.ts` (see §1.1).
- **Pending Clears**: Clears rects from removed children (`pendingClears`) to prevent ghosting.

#### `ink/render-to-screen.ts` (231 lines)
Utility for rendering React elements to an isolated `Screen` buffer — used for search highlighting.

- **renderToScreen(el, width)**: Creates a temporary React root, mounts the element, runs Yoga layout, paints to a screen buffer, then unmounts. Returns `{ screen, height }`.
- **applyPositionedHighlight(screen, positions, stylePool)**: Applies yellow current-match highlighting to specific (row, col) positions. Different from `applySelectionOverlay` (inverse) and `applySearchHighlight` (inverse for all matches).
- **scanPositions(screen, query)**: Scans a screen buffer for a case-insensitive query, returning `MatchPosition[]` — each with `{ row, col, len }`. Positions are relative to the message's own bounding box; caller adds the message's screen-row offset.

#### `ink/output.ts` (797 lines)
Collects write/blit/clear/clip operations from the render tree and applies them to a Screen buffer. Acts as the paint context.

- **Output Class**: Manages the `Screen` being painted into, with methods: `write(x, y, text, styleId, hyperlink?)` — writes text at a position; `moveCursor(x, y)` — sets the cursor; `clip(rect)` / `clipOff()` — restricts writes to a region.
- **ClusteredChar**: Precomputed rendering unit — `{ value: string, width: number, styleId: number, hyperlink: string | undefined }`. Built once per unique line and cached via `charCache` so the per-char hot loop is just property reads + `setCellAt`.
- **charCache**: LRU map of `"styleId|hyperlink|text"` → `ClusteredChar[]`. Colons that would collide are escaped first. Since `StylePool` is session-lived and `HyperlinkPool` resets every 5 min, cache keys remain valid across resets.
- **Bidi Support**: Calls `reorderBidi()` on every write — handles RTL (right-to-left) text like Arabic/Hebrew by reversing the visual order while keeping logical segments intact.
- **blit(rect, srcScreen)**: Blits a region from the source screen (prev frame) into the output screen.
- **clear(rect)**: Fills a region with spaces (styleId 0, hyperlink 0).
- **get()**: Finalizes the output — applies all queued operations, returns the populated `Screen`.

### 1.4 Style & Layout

#### `ink/styles.ts` (771 lines)
Flexbox layout engine integration + terminal styling types.

- **Styles Type**: Defines the inline style API. Includes:
  - **Flexbox**: `flexGrow`, `flexShrink`, `flexBasis`, `flexDirection`, `justifyContent`, `alignItems`, `alignSelf`, `gap`, `columnGap`, `rowGap`
  - **Box Model**: `width`, `height`, `minWidth`, `minHeight`, `maxWidth`, `maxHeight`, `margin`, `marginTop`/`Left`/`Bottom`/`Right`, `padding`, `paddingTop`/etc.
  - **Position**: `position` ('absolute' | 'relative'), `top`, `bottom`, `left`, `right`
  - **Display**: `display` ('flex' | 'none'), `overflow` ('visible' | 'hidden' | 'scroll')
  - **Borders**: `borderStyle`, `borderColor`, `borderWidth` (uniform or per-edge), `borderTop`/`Left`/etc.
  - **Text**: `textWrap` ('wrap' | 'wrap-trim' | 'end' | 'middle' | 'truncate-end' | 'truncate' | 'truncate-middle' | 'truncate-start')
- **TextStyles Type**: `{ color?, backgroundColor?, bold?, dim?, italic?, underline?, strikethrough?, inverse? }`
- **Color Type**: `RGBColor | HexColor | Ansi256Color | AnsiColor` — raw color values, not theme keys. Theme resolution happens at the component layer.
- **applyStyles(node, styles)**: Maps the declarative `Styles` object to Yoga layout node properties: `setFlexGrow`, `setFlexShrink`, `setFlexBasis`, `setFlexDirection`, `setJustifyContent`, `setAlignItems`, `setAlignSelf`, `setPositionType`, `setWidth`, `setHeight`, `setMinWidth`, `setMaxWidth`, `setMargin`, `setPadding`, `setGap`, `setBorder`, `setOverflow`, `setDisplay`, `setPosition`. Also sets `textStyles` on the DOM element for rendering.

#### `ink/frame.ts` (124 lines)
Frame structure and lifecycle.

- **Frame Type**: `{ readonly screen: Screen, readonly viewport: Size, readonly cursor: Cursor, readonly scrollHint?: ScrollHint | null, readonly scrollDrainPending?: boolean }`
- **emptyFrame(rows, columns, stylePool, charPool, hyperlinkPool)**: Creates a zeroed frame.
- **shouldClearScreen(prevFrame, frame)**: Determines if a full terminal clear is needed. Triggers on: resize (viewport dimensions changed), offscreen (content overflows terminal height), or explicit clear request.
- **Patch Type**: The diff opcodes emitted by `LogUpdate`: `stdout` (raw string), `clear` (clear N lines), `clearTerminal` (full reset with reason), `cursorHide`, `cursorShow`, `cursorMove`, `cursorTo`, `carriageReturn`, `hyperlink` (OSC 8 link), `styleStr` (pre-serialized SGR transition).
- **FlickerReason**: `'resize' | 'offscreen' | 'clear'` — used in `FrameEvent.flickers` for diagnostics.

#### `ink/optimizer.ts` (93 lines)
Patch-level diff optimizer — runs after `LogUpdate.render()` produces the raw diff.

- **optimize(diff)**: Applies rules in a single pass: removes empty `stdout` patches, merges consecutive `cursorMove` patches (adds x/y), removes no-op `(0,0)` moves, concatenates adjacent `styleStr` patches, deduplicates consecutive hyperlinks with the same URI, cancels `cursorHide`/`cursorShow` pairs, removes zero-count `clear` patches.
- Produces a minimal set of ANSI operations to write to the terminal.

#### `ink/colorize.ts` (231 lines)
ANSI text formatting via `chalk` — with environment-aware color level handling.

- **Chalk Level Boosting**: Detects `TERM_PROGRAM=vscode` and boosts `chalk.level` from 2 (256-color) to 3 (truecolor) — `chalk` doesn't recognize VS Code's terminal as truecolor-capable, causing washed-out colors.
- **Tmux Clamping**: When `$TMUX` is set, clamps `chalk.level` to 2 (256-color) because tmux's default config doesn't pass through truecolor. Respects `CLAUDE_CODE_TMUX_TRUECOLOR` escape hatch.
- **applyColor(color)**: Converts `Color` (RGB, hex, ANSI) to a chalk function. Handles `ansi256(n)` via `chalk.ansi256()`.
- **applyTextStyles(text, styles)**: Applies `TextStyles` (bold, dim, italic, underline, strikethrough, inverse, color, backgroundColor) via chalk method chaining.

#### `ink/Ansi.tsx` (292 lines)
React component that parses ANSI escape sequences in strings and renders them as styled `<Text>` components. Uses the termio parser internally. Memoized for performance.

### 1.5 Terminal I/O

#### `ink/terminal.ts` (248 lines)
Terminal abstraction — manages stdin/stdout and converts Ink's internal `Diff` (patches) to raw terminal output.

- **Terminal Type**: Wraps the `Writable` stream for stdout.
- **writeDiffToTerminal(terminal, diff)**: Serializes the optimized diff into ANSI escape sequences and writes to `stdout`. Handles: `stdout` patches (raw string), `clear` (eraseLines + CR), `clearTerminal` (full clear sequence), `cursorHide`/`cursorShow` (DECTCEM), `cursorMove` (CUP), `cursorTo` (CHA), `carriageReturn`, `hyperlink` (OSC 8), `styleStr` (pre-built SGR string).
- **SYNC_OUTPUT_SUPPORTED**: Boolean indicating whether the terminal supports synchronous writes (used for performance).
- **isProgressReportingAvailable()**: Checks if the terminal supports OSC 9;4 progress reporting (supported: ConEmu, Ghostty 1.2.0+, iTerm2 3.6.6+; excluded: Windows Terminal).
- **isXtermJs()**: Detects xterm.js-based terminals (VS Code, Cursor) via XTVERSION probe. Important for mouse wheel behavior differences.

#### `ink/log-update.ts` (773 lines)
Log-based terminal updater — diffs two screen buffers and produces a minimal `Diff` (patch sequence). The key optimization layer between the screen buffer and terminal output.

- **LogUpdate Class**: Holds `previousOutput` state for the previous frame's serialized screen string.
- **render(prevFrame, frame)**: The main diff method. Compares two `Frame` objects and produces a `Diff`. Three strategies:
  1. **DECSTBM Hardware Scroll**: When `scrollHint` is available and no other changes exist, emits `DECSTBM` + `SU`/`SD` sequences for zero-rewrite scrolling (10x faster than rewrite).
  2. **Cell-by-Cell Diff**: Uses `diffEach()` to find changed cells, then emits minimal ANSI sequences — cursor movements + style transitions + character writes. Only rewrites changed cells.
  3. **Full Render** (fallback): When a full clear is needed (resize, overscan, SIGCONT), serializes the entire screen buffer.
- **State Tracking**: Maintains `previousOutput` (the complete ANSI serialization of the last frame) and `prevScreen` for cursor position tracking during cell-level diffs.
- **renderPreviousOutput_DEPRECATED(prevFrame)**: Final render on exit — replays the last frame's output with trailing newline.

#### `ink/parse-keypress.ts` (801 lines)
Keyboard input parser — converts raw terminal input bytes to structured key events using the termio tokenizer.

- **Key Press Detection**: Matches raw input against regex patterns:
  - `META_KEY_CODE_RE`: ESC + single character (Meta/Alt+char)
  - `FN_KEY_RE`: ESC + `O`/`N`/`[` sequences (function keys, arrows, home/end, etc.)
  - `CSI_U_RE`: Kitty keyboard protocol (`ESC [ codepoint [; modifier] u`)
  - `MODIFY_OTHER_KEYS_RE`: xterm modifyOtherKeys (`ESC [ 27 ; modifier ; keycode ~`)
- **Terminal Response Patterns**: Also parses terminal query responses:
  - `DECRPM_RE`: DEC mode responses (e.g., cursor visibility confirmation)
  - `DA1_RE`/`DA2_RE`: Device attribute responses
  - `KITTY_FLAGS_RE`: Kitty keyboard protocol capability flags
  - `CURSOR_POSITION_RE`: DECXCPR cursor position report
  - `OSC_RESPONSE_RE`: OSC response (tab status, clipboard)
  - `XTVERSION_RE`: Terminal name/version string
- **Mouse Events**: Parses SGR mouse tracking events (mode 1006) and X10 mouse events (mode 9). Handles button press/release, drag, scroll wheel, and modifier keys (shift, alt, ctrl).
- **Paste Bracketing**: Detects `PASTE_START` (`\e[200~`) and `PASTE_END` (`\e[201~`) sequences.

### 1.6 Text Processing

#### `ink/stringWidth.ts` (222 lines)
ANSI-aware string width calculation with CJK/emoji awareness.

- **stringWidth(str)**: Returns the visual column width of a string. Handles: ANSI stripping, ASCII fast path, CJK wide characters (calculated via `eastAsianWidth`), emoji (via `emoji-regex`), grapheme clusters (multi-codepoint emoji like family emoji), zero-width characters (ZWJ, variation selectors).
- **Fallback**: Uses a JavaScript implementation when `Bun.stringWidth` is not available (the Bun runtime provides a native implementation).

#### `ink/wrap-text.ts` (74 lines)
Text wrapping utility that respects terminal column width.

- **wrapText(text, maxWidth, options)**: Wraps text at word boundaries. Returns `string[]` (lines). Handles: ANSI codes (wraps around them), word boundaries (spaces), forced breaks when a single word exceeds `maxWidth`, blank-line preservation.

#### `ink/bidi.ts` (139 lines)
Bidirectional text (RTL/LTR) handling.

- **reorderBidi(text)**: Reorders text segments for correct display of RTL languages (Arabic, Hebrew). Uses Unicode Bidi Algorithm (UBA) Level 2. Segments text at direction boundaries, reverses RTL runs for visual order.

#### `ink/squash-text-nodes.ts` (92 lines)
Text node optimization — collapses chains of nested `<Text>` components into flat `StyledSegment[]` arrays.

- **squashTextNodesToSegments(node, inheritedStyles, inheritedHyperlink)**: Recursively walks `ink-text`/`ink-virtual-text`/`ink-link` children, merging text styles (closer child styles override parent). Produces `StyledSegment[]` with cumulative styles per segment.
- **squashTextNodes(node)**: Plain-text version — returns a concatenated string of all text content, used for text measurement in layout.

#### `ink/widest-line.ts` (19 lines)
Returns the widest line width from a multi-line string. Used for block-level width calculation.

#### `ink/get-max-width.ts` (27 lines)
Computes the maximum width available for a node, accounting for parent constraints.

#### `ink/tabstops.ts` (46 lines)
Tab stop calculation — expands tabs to spaces based on standard 8-column tab stop positions.

#### `ink/wrapAnsi.ts` (20 lines)
Wraps ANSI text while preserving escape sequence boundaries. Thin wrapper around `wrapAnsi` package.

#### `ink/measure-element.ts` (23 lines)
Element dimension measurement hook for Yoga's measure function integration.

#### `ink/measure-text.ts` (47 lines)
Text measurement — returns `{ width: number }` for a string, accounting for text wrapping and truncation modes. Used by Yoga's measure function for intrinsic text sizing.

#### `ink/line-width-cache.ts` (24 lines)
Simple LRU cache mapping `(text, maxWidth)` → `number` (line count). Prevents re-measuring frequently rendered text lines.

### 1.7 Interaction

#### `ink/selection.ts` (917 lines)
Text selection state and operations (alt-screen only, where the terminal supports mouse tracking).

- **SelectionState**: Tracks `anchor` (mouse-down position), `focus` (drag position), `isDragging`, `anchorSpan` (word/line mode bounds), `scrolledOffAbove`/`scrolledOffBelow` (rows that scrolled past the viewport), `softWrap` tracking for accurate copy-paste of wrapped lines.
- **startSelection(col, row, screen)**: Initiates selection at a cell position. Supports modifiers: alt (force rectangle selection), double-click (select word), triple-click (select line).
- **extendSelection(col, row, screen)**: Extends the selection as the mouse moves.
- **clearSelection()**: Clears all selection state.
- **getSelectedText(screen, state)**: Extracts the selected text from the screen buffer, joining wrapped lines and respecting `noSelect` regions (gutters, line numbers). Returns clean plain text for clipboard copy.
- **applySelectionOverlay(screen, state, stylePool)**: Applies inverse (SGR 7) styling to selected cells. Called post-render, so the diff engine picks up the overlay as changes.
- **captureScrolledRows(screen, state)**: When the viewport scrolls during a drag, captures the rows leaving the viewport for later text extraction.
- **findPlainTextUrlAt(col, row, screen)**: Finds the URL (OSC 8 hyperlink) at a clicked position for Ctrl+Click opening.

#### `ink/searchHighlight.ts` (93 lines)
Search result highlighting — inverts all occurrences of a query string in the screen buffer.

- **applySearchHighlight(screen, query, stylePool)**: Scans the screen row by row, building a lowercase text representation (excluding `SpacerTail`, `SpacerHead`, and `noSelect` cells). Finds all non-overlapping matches of `query` and inverts their styles via `stylePool.withInverse()`. Returns `true` if any match was highlighted (for damage gating).

#### `ink/hit-test.ts` (130 lines)
Spatial click detection and event dispatch.

- **hitTest(node, col, row)**: Recursively searches the DOM tree (in reverse child order — later siblings on top) for the deepest element whose rendered rect contains `(col, row)`. Uses `nodeCache` rects (screen coordinates, scroll-adjusted).
- **dispatchClick(root, col, row, cellIsBlank)**: Hit-tests, then bubbles a `ClickEvent` from the deepest node up to the root. Fires `onClick` handlers. Also handles click-to-focus via `FocusManager`.
- **dispatchHover(root, col, row)**: Similar to `dispatchClick` but for mouse-move events. Calls `onMouseEnter`/`onMouseLeave` handlers. Uses a `hoveredNode` cache to track enter/leave across frames.

#### `ink/focus.ts` (181 lines)
DOM-like focus management for terminal UI.

- **FocusManager Class**: Tracks `activeElement`, a focus stack (depth-limited to 32), and enabled state. Methods:
  - `focus(node)`: Blurs current, pushes to stack, focuses new node. Dispatches `blur` and `focus` events.
  - `blur()`: Clears active element. Dispatches `blur` event.
  - `handleNodeRemoved(node, root)`: When a node is removed from the tree — purges it and descendants from the focus stack, blurs if active, restores focus from stack.
  - `handleAutoFocus(node)`: Auto-focuses a node on mount.
  - `handleClickFocus(node)`: Focuses a node on click (if `tabIndex >= 0`).
  - `focusNext(root)` / `focusPrevious(root)`: Tab/Shift+Tab cycling through all tabbable nodes in the tree.
  - `enable()` / `disable()`: Toggle focus system.
- **getRootNode(node)**: Walks up to find the root node (which owns the `FocusManager`).
- **getFocusManager(node)**: Returns the `FocusManager` from the root.

### 1.8 Optimization & Performance

#### `ink/node-cache.ts` (54 lines)
Rendered node position cache — stores each node's layout rect after rendering for next-frame blit.

- **nodeCache**: `WeakMap<DOMElement, CachedLayout>` — maps DOM elements to their last rendered rect `{x, y, width, height, top?}`. Top is the yoga-local top for ScrollBox viewport culling.
- **pendingClears**: `WeakMap<DOMElement, Rectangle[]>` — rects of removed children that need clearing on the next frame.
- **addPendingClear(parent, rect, isAbsolute)**: Registers a region to clear, with special handling for absolute-positioned removals (they may paint cross-subtree).
- **consumeAbsoluteRemovedFlag()**: Returns and resets the flag that disables blit for the next frame when absolute-positioned content was removed.

#### `ink/optimizer.ts` (81 lines — see section 1.4)

### 1.9 Miscellaneous

#### `ink/supports-hyperlinks.ts` (57 lines)
Detects terminal hyperlink (OSC 8) support via environment inspection (`TERM_PROGRAM`, `TERM`, `WT_SESSION`, `FORCE_HYPERLINK`).

#### `ink/useTerminalNotification.ts` (126 lines)
React hook enabling components to send OSC sequences (terminal notifications, progress, tab status) via a `TerminalWriteProvider` context.

#### `ink/clearTerminal.ts` (74 lines)
Cross-platform terminal clear with scrollback support. Detects Windows Terminal, mintty, and modern terminals supporting `ESC[3J` (erase scrollback). Exports `clearTerminal(reason?)` used by `LogUpdate` full-reset patches.

#### `ink/constants.ts` (2 lines)
Shared `FRAME_INTERVAL_MS = 16` (~60fps render throttle).

#### `ink/terminal-focus-state.ts` (47 lines)
Module-level terminal focus tracking — updated by focus events from stdin. Used by voice and other hooks via `useTerminalFocus`.

#### `ink/terminal-querier.ts` (210 lines)
Async terminal capability queries (size, color, kitty keyboard, mouse mode) via CSI/DA responses. Caches results per session.

#### `ink/termio.ts` (42 lines)
Re-exports the termio parser stack (`ansi`, `csi`, `sgr`, `osc`, etc.) for consumers outside the parser modules.

#### `ink/warn.ts` (9 lines)
Dev-only integer validation helper — `ifNotInteger(value, name)` logs a warning when layout props receive non-integer values.

---

## 2. Ink Components (`ink/components/`) — 18 Files

### 2.1 `ink/components/App.tsx` (657 lines)
Root app component — provides context providers (`StdinContext`, `AppContext`, `TerminalFocusContext`, `TerminalSizeContext`, `ClockContext`, `CursorDeclarationContext`) for all descendants. Wraps the entire Ink component tree.

### 2.2 `Box.tsx` (214 lines)
The fundamental flexbox container — equivalent to `<div style="display: flex">`. Props include all flexbox styles (`flexDirection`, `flexGrow`, `justifyContent`, etc.) plus interactive props (`onClick`, `onFocus`, `onBlur`, `onKeyDown`, `onMouseEnter`, `onMouseLeave`, `tabIndex`, `autoFocus`). Renders as `ink-box` DOM node.

### 2.3 `Text.tsx` (254 lines)
Text rendering component with rich styling. Props: `color`, `backgroundColor`, `italic`, `underline`, `strikethrough`, `inverse`, `wrap`, `bold`/`dim` (mutually exclusive — bold and dim cannot coexist in terminals). Children can be strings, numbers, or nested Text components (styles cascade/override). Renders as `ink-text` DOM node.

### 2.4 `ScrollBox.tsx` (237 lines)
Scrollable container — the core scrolling mechanism for message history and other overflow content.

- **State**: Maintains `scrollTop` and `pendingScrollDelta` on the DOM element.
- **stickyScroll**: Auto-pins to the bottom when content grows (like a chat app auto-scrolling to new messages).
- **Imperative Handle** (`ScrollBoxHandle`): Exposes `scrollTo(y)`, `scrollBy(dy)`, `scrollToElement(el, offset)`, `scrollToBottom()`, `getScrollTop()`, `getPendingDelta()`, `getScrollHeight()`, `getFreshScrollHeight()`, `getViewportHeight()`, `getViewportTop()`, `isSticky()`, `subscribe(listener)` for external control.
- **forceRender flag**: When `true`, forces a full re-render on every frame regardless of `dirty` state. Used during active scrolling for smooth updates.
- **Scroll Drain**: Accumulates mouse wheel `deltaY` into `pendingScrollDelta`; the renderer drains it gradually across frames.

### 2.5 `Button.tsx` (192 lines)
Interactive button component — renders as a focusable `Box` with `onAction` callback. Supports `autoFocus`, `tabIndex`, and a render-prop pattern `children: ((state: { focused, hovered, active }) => ReactNode) | ReactNode`. Responds to Enter/Space/click to fire `onAction`.

### 2.6 `Link.tsx` (42 lines)
Clickable hyperlink component — wraps children in an `ink-link` DOM node with `href` attribute. Renders with OSC 8 hyperlink for terminal-native link support (Cmd+Click opens browser).

### 2.7 `Newline.tsx` (39 lines)
Explicit newline component — renders `\n` for layout purposes.

### 2.8 `Spacer.tsx` (20 lines)
Spacing component — renders a single blank space character with flexible dimensions.

### 2.9 `NoSelect.tsx` (68 lines)
Prevents text selection within its children by wrapping them in a region marked as `noSelect` in the screen buffer.

### 2.10 `RawAnsi.tsx` (57 lines)
Raw ANSI escape code passthrough — writes raw ANSI content directly to the screen buffer without Ink processing. Useful for embedding external tool output with pre-existing ANSI formatting.

### 2.11 `AlternateScreen.tsx` (80 lines)
Alternate screen buffer component — enters/exits the terminal's alternate screen buffer (like vim/less). Enables mouse tracking (SGR mode 1006), kitty keyboard protocol, and modifyOtherKeys. Manages terminal mode cleanup on unmount.

### 2.12 `ErrorOverview.tsx` (109 lines)
Error display overlay — shows a summary of errors within a bordered panel. Used for diagnostic display.

### 2.13 Context Providers (5 files)
- **`AppContext.ts`** (17 lines): Provides the Ink `Ink` instance reference.
- **`ClockContext.tsx`** (111 lines): Provides a clock/timing service for animation frames and intervals.
- **`CursorDeclarationContext.ts`** (28 lines): Allows components to declare cursor visibility/shape.
- **`StdinContext.ts`** (37 lines): Provides stdin stream and raw mode control.
- **`TerminalFocusContext.tsx`** (49 lines): Provides terminal focus state (detected via `CSI I`/`CSI O` focus tracking sequences).
- **`TerminalSizeContext.tsx`** (7 lines): Provides `columns` and `rows` context from terminal dimensions.

---

## 3. Ink Events (`ink/events/`) — 10 Files

| File | Purpose |
|------|---------|
| `event.ts` | Base `Event` class with `type`, `target`, `currentTarget`, `stopImmediatePropagation()`, `_propagationStopped` |
| `click-event.ts` | `ClickEvent` — extends `Event`, adds `col`, `row`, `cellIsBlank`. Fired for mouse left-click |
| `focus-event.ts` | `FocusEvent` — extends `Event`, adds `relatedTarget`. Fired for focus/blur |
| `keyboard-event.ts` | `KeyboardEvent` — extends `Event`, adds `key`, `shiftKey`, `ctrlKey`, `metaKey`, `altKey`, `input`. Fired for keyboard input |
| `terminal-event.ts` | `TerminalEvent` — base for terminal-specific events |
| `terminal-focus-event.ts` | `TerminalFocusEvent` — fired when the terminal window gains/loses focus (tracked via DECSET 1004) |
| `input-event.ts` | Raw input event for text input |
| `dispatcher.ts` | `Dispatcher` class — manages event handler registration and dispatch with capture + bubble phases |
| `emitter.ts` | Event emitter utilities |
| `event-handlers.ts` | `EVENT_HANDLER_PROPS` constant — maps event handler prop names to their event types |

---

## 4. Ink Hooks (`ink/hooks/`) — 12 Files

| Hook | Purpose |
|------|---------|
| `use-input.ts` | Subscribe to keyboard input. Calls callback with `(input: string, key: Key)` on each keypress |
| `use-app.ts` | Access the Ink `Ink` instance from context |
| `use-stdin.ts` | Access raw stdin stream |
| `use-terminal-focus.ts` | Subscribe to terminal window focus/blur events |
| `use-terminal-title.ts` | Set the terminal window title via OSC 2 |
| `use-terminal-viewport.ts` | Get/set terminal viewport properties |
| `use-animation-frame.ts` | Request animation frame callback (requestAnimationFrame for terminal) |
| `use-interval.ts` | `setInterval` with cleanup — fires at the configured `FRAME_INTERVAL_MS` |
| `use-declared-cursor.ts` | Declare cursor visibility/shape for the current render tree |
| `use-selection.ts` | Access text selection state and operations from the Ink instance |
| `use-search-highlight.ts` | Control search highlight state (query string + current match index) |
| `use-tab-status.ts` | Set terminal tab status via OSC 9;0 (iTerm2/Ghostty tab badge) |

---

## 5. Ink Layout (`ink/layout/`) — 4 Files

### `node.ts` (152 lines)
Adapter interface for the layout engine. Defines enums: `LayoutDisplay`, `LayoutFlexDirection`, `LayoutAlign`, `LayoutJustify`, `LayoutWrap`, `LayoutPositionType`, `LayoutOverflow`, `LayoutMeasureMode`, `LayoutEdge`, `LayoutGutter`. The `LayoutNode` interface abstracts the underlying Yoga node.

### `geometry.ts` (97 lines)
Pure geometry types: `Point`, `Size`, `Rectangle`, `Edges`. Includes helpers: `edges()` (factory for uniform/single-axis/full edge values), `addEdges()`, `subtractEdges()`, `clamp()`, `unionRect()`.

### `engine.ts` (6 lines)
Trivial factory — `createLayoutNode()` → delegates to `createYogaLayoutNode()`.

### `yoga.ts` (308 lines)
Yoga layout adapter. The `YogaLayoutNode` class wraps a native-TS `Yoga.Node` and implements the `LayoutNode` interface. Maps edge/gutter enums between Ink's namespace and Yoga's built-in enums. Provides the bridge between `applyStyles()` (which sets Yoga properties) and `calculateLayout()` (which reads computed positions).

---

## 6. Ink Termio (`ink/termio/`) — 9 Files

A streaming ANSI escape sequence parser and tokenizer. Handles the full grammar of terminal escape sequences.

### `types.ts` (236 lines)
Semantic types for the ANSI parser output:
- **Color**: `{ type: 'named' | 'indexed' | 'rgb' | 'default', ... }`
- **TextStyle**: `{ bold, dim, italic, underline: UnderlineStyle, blink, inverse, hidden, strikethrough, ... }`
- **Grapheme**: `{ text: string, codePoint: number, width: number }`
- **Action**: Union of all possible semantic actions — `Print`, `SGR`, `CursorMove`, `CursorTo`, `EraseDisplay`, `EraseLine`, `Scroll`, `SetMode`, `ResetMode`, `RingBell`, `OscAction`, etc.

### `tokenize.ts` (319 lines)
Escape sequence boundary detection. Splits raw terminal input into `{ type: 'text' | 'sequence', value: string }` tokens. Implements a state machine with states: `ground`, `escape`, `escapeIntermediate`, `csi`, `ss3`, `osc`, `dcs`. Used by `parse-keypress.ts` for keyboard input parsing.

### `parser.ts` (394 lines)
Semantic action generator. A streaming parser that produces structured `Action[]` from raw ANSI text. Uses the tokenizer for sequence detection, then interprets each escape sequence. Tracks current `TextStyle` state across SGR sequences. Handles: SGR (color/style), CUP (cursor positioning), ED (erase display), EL (erase line), SU/SD (scroll), DEC modes, OSC sequences (hyperlink, title, clipboard).

### Support Files
- **`ansi.ts`**: C0 control codes (`BEL`, `BS`, `HT`, `LF`, `CR`, `ESC`, `ST`, etc.) and escape sequence type classifiers (`isEscFinal`, escape type enum).
- **`csi.ts`**: CSI (Control Sequence Introducer) sequences — cursor movement (`CURSOR_HOME`, CUP, CHA), erase operations (ED, EL with subparameters), scroll region (`DECSTBM`, `SU`, `SD`), keyboard protocol (`ENABLE_KITTY_KEYBOARD`, `DISABLE_KITTY_KEYBOARD`, `ENABLE_MODIFY_OTHER_KEYS`, `DISABLE_MODIFY_OTHER_KEYS`), paste bracketing (`PASTE_START`, `PASTE_END`).
- **`dec.ts`**: DEC private sequences — alternate screen (`ENTER_ALT_SCREEN`, `EXIT_ALT_SCREEN`), cursor visibility (`SHOW_CURSOR`, `HIDE_CURSOR`, `DBP`, `DFE`), mouse tracking (`ENABLE_MOUSE_TRACKING`, `DISABLE_MOUSE_TRACKING`).
- **`esc.ts`**: ESC sequence parser — handles ESC + intermediate + final byte parsing.
- **`osc.ts`**: OSC (Operating System Command) sequences — window title (OSC 2), hyperlinks (OSC 8), tab status (OSC 9;0), clipboard (OSC 52), progress (OSC 9;4), iTerm2 marks.
- **`sgr.ts`**: SGR (Select Graphic Rendition) parser — maps SGR parameter sequences to `TextStyle` mutations. Handles all standard SGR codes (0-107) for colors, bold, dim, italic, underline, blink, inverse, strikethrough, fonts.
- **`types.ts`**: Type definitions for the parser.

---

## 7. Native-TypeScript Modules (`native-ts/`)

### 7.1 Yoga Layout (`native-ts/yoga-layout/`) — 2 files

#### `index.ts` (2578 lines)
A pure-TypeScript port of Meta's Yoga flexbox engine. This is a **complete reimplementation** of the Yoga layout algorithm — the same engine that powers React Native and many other frameworks. Key features:

- **Class `Node`**: Core layout node with properties for flex, dimensions, margins, padding, borders, position, alignment, etc.
- **`calculateLayout(width, height, direction)`**: The main layout pass — runs the full recursive flexbox algorithm:
  1. Resolves all child dimensions (specified, percentage, auto)
  2. Computes main-axis size based on `flexGrow` and `flexShrink`
  3. Distributes remaining space according to `justifyContent`
  4. Computes cross-axis size and alignment (`alignItems`, `alignSelf`)
  5. Handles `margin: auto` on both axes
  6. Positions children
  7. Recurses into child nodes
- **Measure Functions**: Support for `measureFunc` callbacks — when Ink's text components need intrinsic sizing, Yoga calls the measure function to determine the text width/height.
- **Implemented Features**: flex-direction (row/column + reverse), flex-grow/shrink/basis, align-items/self (stretch, flex-start, center, flex-end, baseline), justify-content (all 6), margin/padding/border/gap, width/height/min/max (point, percent, auto), position relative/absolute, display flex/none/contents, flex-wrap (wrap/wrap-reverse + align-content).
- **Not Implemented**: aspect-ratio, box-sizing: content-box, RTL direction (always LTR for terminal).
- **Performance Counters**: Exports `getYogaCounters()` returning `{ ms, visited, measured, cacheHits, live }` for diagnostics.

#### `enums.ts` (134 lines)
Layout enums matching the Yoga API: `Align`, `BoxSizing`, `Dimension`, `Direction`, `Display`, `Edge`, `Errata`, `ExperimentalFeature`, `FlexDirection`, `Gutter`, `Justify`, `MeasureMode`, `Overflow`, `PositionType`, `Unit`, `Wrap`.

### 7.2 Color Diff (`native-ts/color-diff/index.ts`) — 1 file (999 lines)

A pure-TypeScript port of the native Rust color-diff module (originally wrapping `syntect` + `similar`). Used for syntax-highlighted file diffs.

- **`colorDiff(oldStr, newStr, options)`**: Computes a unified diff with syntax highlighting. Uses `highlight.js` for syntax coloring (lazy-loaded to avoid ~50MB heap on import) and the `diff` npm package's `diffArrays` for word-level diffing.
- **Diff Structure**: Returns `Hunk[]` with `{ oldStart, oldLines, newStart, newLines, lines: string[] }` — each line is an ANSI-formatted string with line numbers, gutter markers (+/-), syntax colors, and word-level diff highlighting.
- **`SyntaxTheme`**: Maps highlight.js scope tokens to ANSI colors. Defaults for light/dark themes.
- **`calculateSyntaxHighlightedHtml(source, filePath)`**: HTML output path (used for HTML diff exports).
- **Language Detection**: Auto-detects file language from extension via highlight.js's `highlightAuto()`.

### 7.3 File Index (`native-ts/file-index/index.ts`) — 1 file (370 lines)

A pure-TypeScript port of the native Rust `file-index` module (which wraps nucleo for fuzzy search).

- **Class `FileIndex`**: High-performance fuzzy file search with nucleo-style scoring.
  - `loadFromFileList(fileList: string[])`: Deduplicates and indexes file paths. Builds character bitmap arrays for fast multi-character matching. Runs asynchronously in chunks (yields every ~4ms of work to keep the UI responsive).
  - `search(query: string, limit: number): SearchResult[]`: Fuzzy-searches the indexed paths. Scoring approximates fzf-v2/nucleo scoring: bonuses for boundary characters, camelCase, consecutive matches, and first character matches; penalties for gap starts and extensions.
  - **Scoring**: `SCORE_MATCH = 16`, `BONUS_BOUNDARY = 8`, `BONUS_CAMEL = 6`, `BONUS_CONSECUTIVE = 4`, `BONUS_FIRST_CHAR = 8`, `PENALTY_GAP_START = 3`, `PENALTY_GAP_EXTENSION = 1`. Test-file penalty: 1.05x score boost (capped at 1.0) for non-test files.
  - **Top-Level Cache**: Caches the first `TOP_LEVEL_CACHE_LIMIT` (100) search results for repeated queries.

---

## Architecture Flow Summary

```
User Input (stdin)
    │
    ▼
parse-keypress.ts  ──►  FocusManager / Dispatcher  ──►  React Event Handlers
                                                          │
                                                          ▼
                                                    React Reconciler
                                                   (reconciler.ts)
                                                          │
                                              ┌───────────┴───────────┐
                                              │  createInstance()      │
                                              │  commitUpdate()        │
                                              │  prepareForCommit()    │
                                              │  resetAfterCommit()    │
                                              └───────────┬───────────┘
                                                          │
                                              Yoga calculateLayout()
                                              (yoga-layout/index.ts)
                                                          │
                                                          ▼
                                              renderer.ts → renderNodeToOutput.ts
                                                          │
                                              ┌───────────┴───────────┐
                                              │  DOM tree walk          │
                                              │  squashTextNodes()      │
                                              │  renderBorder()         │
                                              │  applyTextStyles()      │
                                              │  Output.write()         │
                                              │  nodeCache.set()        │
                                              └───────────┬───────────┘
                                                          │
                                                          ▼
                                                   Screen Buffer
                                                   (screen.ts)
                                                          │
                                              applySelectionOverlay()
                                              applySearchHighlight()
                                                          │
                                                          ▼
                                              log-update.ts  ──►  Diff
                                                          │
                                                          ▼
                                              optimizer.ts  ──►  Diff (optimized)
                                                          │
                                                          ▼
                                              writeDiffToTerminal()
                                              (terminal.ts)
                                                          │
                                                          ▼
                                                    stdout (ANSI)
```

---

## Key Performance Optimizations

1. **Double Buffering**: `frontFrame` and `backFrame` screens — one being rendered into, one being diffed against.
2. **Dirty Tracking**: `markDirty()` propagates up the tree. Only dirty subtrees re-render; clean subtrees blit from `nodeCache`.
3. **Style/Char/Hyperlink Interning**: Pools convert strings to integers — cell arrays are `Int32Array`, enabling fast integer comparison in `diffEach()`.
4. **DECSTBM Hardware Scroll**: When only scrollTop changes, emits `DECSTBM` + `SCROLL_UP`/`SCROLL_DOWN` ANSI sequences instead of rewriting the viewport.
5. **Patch Optimization**: `optimizer.ts` deduplicates and merges adjacent patches before emitting to stdout.
6. **ClusteredChar Cache**: Per-line cache of `(styleId, hyperlink, text)` → precomputed `ClusteredChar[]`. Most lines don't change between frames.
7. **Generational Pool Reset**: `CharPool` and `HyperlinkPool` reset every 5 minutes — bounded growth, hot caches in steady state.
8. **Yoga Caching**: `_hasL` single-slot cache in the Yoga port avoids recomputing layout for unchanged subtrees.
