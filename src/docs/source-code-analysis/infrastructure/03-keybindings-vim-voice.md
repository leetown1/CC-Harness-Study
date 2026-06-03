# Keybindings, Vim Mode & Voice Input Analysis (25+ files, ~5,400 lines)

**Directories**: `F:\Claude\src\keybindings\`, `F:\Claude\src\vim\`, `F:\Claude\src\voice\`, `F:\Claude\src\hooks\useVoice*.ts`, `F:\Claude\src\services\voice*.ts`  
**Purpose**: Customizable keyboard shortcut system, vim-style modal text editing, and voice input (dictation/command) integration.

---

## PART 1: Keybindings System (14 files, ~2,550 lines)

### Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    Keybinding Configuration                     │
│                                                                 │
│  ~/.claude/keybindings.json  ──► loadUserBindings.ts           │
│  defaultBindings.ts           ──► merge with defaults           │
│         │                         │                             │
│         ▼                         ▼                             │
│  validate.ts               schema.ts (Zod validation)           │
│  (checks duplicates,         (19 valid contexts,                │
│   reserved keys,              ~60 valid actions)                 │
│   context-action pairs)                                         │
│         │                                                       │
│         ▼                                                       │
│  parser.ts → ParsedBinding[] (keystroke parsing)               │
│         │                                                       │
│         ▼                                                       │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │           KeybindingProviderSetup.tsx                     │  │
│  │  Loads & validates bindings, creates parsing infrastructure│  │
│  │  Manages: activeContexts Set, handlerRegistry Map,        │  │
│  │           pendingChord state                              │  │
│  └──────────────┬───────────────────────────────────────────┘  │
│                 │                                               │
│                 ▼                                               │
│  ┌──────────────────────────────────────┐                      │
│  │   KeybindingProvider (context.tsx)   │                      │
│  │  React context providing:            │                      │
│  │  - resolve(input, key, contexts)     │                      │
│  │  - getDisplayText(action, context)   │                      │
│  │  - setPendingChord / pendingChord    │                      │
│  │  - bindings (ParsedBinding[])        │                      │
│  │  - activeContexts (Set)              │                      │
│  │  - registerActiveContext / unregister│                      │
│  │  - registerHandler / invokeAction    │                      │
│  └──────────────┬───────────────────────┘                      │
│                 │                                               │
│     ┌───────────┼───────────┐                                  │
│     ▼           ▼           ▼                                  │
│  resolver.ts  match.ts   useKeybinding.ts                      │
│  (resolve     (Ink Key  (hook: registers handler               │
│   logic,      matching, for action → callback)                 │
│   chord       modifier                                         │
│   support)    comparison)                                       │
└─────────────────────────────────────────────────────────────────┘
```

### 1. `defaultBindings.ts` (334 lines) — Default Keybindings

Platform-aware default bindings organized by context blocks:

**Global Context** (controller-aware, feature-gated):
- `ctrl+c` → `app:interrupt` (time-based double-press for exit)
- `ctrl+d` → `app:exit` (time-based double-press)
- `ctrl+l` → `app:redraw`
- `ctrl+t` → `app:toggleTodos`
- `ctrl+o` → `app:toggleTranscript`
- `ctrl+shift+b` → `app:toggleBrief` (KAIROS-only)
- `ctrl+shift+o` → `app:toggleTeammatePreview`
- `ctrl+r` → `history:search`
- `ctrl+shift+f` / `cmd+shift+f` → `app:globalSearch` (QUICK_SEARCH feature)
- `ctrl+shift+p` / `cmd+shift+p` → `app:quickOpen` (QUICK_SEARCH feature)
- `meta+j` → `app:toggleTerminal` (TERMINAL_PANEL feature)

**Chat Context** (input-focused):
- `escape` → `chat:cancel`
- `ctrl+x ctrl+k` → `chat:killAgents`
- `shift+tab` / `meta+m` → `chat:cycleMode` (platform-dependent: Windows VT mode check)
- `meta+p` → `chat:modelPicker`
- `meta+o` → `chat:fastMode`
- `meta+t` → `chat:thinkingToggle`
- `enter` → `chat:submit`
- `up/down` → `history:previous/next`
- `ctrl+_` / `ctrl+shift+-` → `chat:undo` (two bindings for terminal compatibility)
- `ctrl+x ctrl+e` / `ctrl+g` → `chat:externalEditor`
- `ctrl+s` → `chat:stash`
- `alt+v` (Windows) / `ctrl+v` (others) → `chat:imagePaste`
- `shift+up` → `chat:messageActions` (MESSAGE_ACTIONS feature)
- `space` → `voice:pushToTalk` (VOICE_MODE feature)

**Autocomplete / Confirmation / Help / ThemePicker / Transcript / HistorySearch / Tabs / Select / MessageSelector / DiffDialog** — individual context blocks with specific bindings (tab navigation, accept/dismiss, etc.)

**Platform support**:
- `IMAGE_PASTE_KEY`: `alt+v` on Windows (ctrl+v is system paste), `ctrl+v` elsewhere
- `MODE_CYCLE_KEY`: checks VT mode support for shift+tab on Windows Terminal
- Kitty keyboard protocol: `cmd+` bindings (super modifier) only fire on supporting terminals

### 2. `schema.ts` (236 lines) — Zod Validation Schema

**`KEYBINDING_CONTEXTS`** (19 contexts):
- Global, Chat, Autocomplete, Confirmation, Help, Transcript, HistorySearch, Task, ThemePicker, Settings, Tabs
- Attachments, Footer, MessageSelector, DiffDialog, ModelPicker, Select, Plugin

**`KEYBINDING_ACTIONS`** (~65 actions across 8 categories):
- App-level: `app:interrupt`, `app:exit`, `app:toggleTodos`, `app:toggleTranscript`, `app:toggleBrief`, `app:toggleTeammatePreview`, `app:toggleTerminal`, `app:redraw`, `app:globalSearch`, `app:quickOpen`
- History: `history:search`, `history:previous`, `history:next`
- Chat: `chat:cancel`, `chat:killAgents`, `chat:cycleMode`, `chat:modelPicker`, `chat:fastMode`, `chat:thinkingToggle`, `chat:submit`, `chat:newline`, `chat:undo`, `chat:externalEditor`, `chat:stash`, `chat:imagePaste`, `chat:messageActions`
- Autocomplete: `autocomplete:accept`, `autocomplete:dismiss`, `autocomplete:previous`, `autocomplete:next`
- Confirmation: `confirm:yes`, `confirm:no`, `confirm:deny`, `confirm:always-allow`
- Vim: `vim:toggle`, `vim:enterInsert`, `vim:enterNormal`
- Voice: `voice:pushToTalk`, `voice:toggle`
- Navigation: `nav:back`, `nav:quit`

**Validation**:
- Zod schema validates keybinding JSON shape: array of `{context, bindings: Record<keystring, action>}`
- Keystring format: `[modifier+]key` (e.g. `ctrl+shift+k`)
- Supports chord bindings: `ctrl+x ctrl+k`
- `null` action = unbind (remove binding in that context)

**`KEYBINDING_CONTEXT_DESCRIPTIONS`** — human-readable descriptions for all 19 contexts

### 3. `parser.ts` (203 lines) — Keystroke Parsing

**`parseKeystroke(input)`**: Parses `"ctrl+shift+k"` → `{key:'k', ctrl:true, shift:true, alt:false, meta:false, super:false}`
- Alias handling: `ctrl/control`, `alt/opt/option/meta`, `cmd/command/super/win`
- Special key mapping: `esc`→`escape`, `return`→`enter`, `space`→`' '`
- Arrow display: `↑←↓→` → `up/left/down/right`
- All keys normalized to lowercase

**`parseChord(input)`**: Parses `"ctrl+k ctrl+s"` → `[{key:'k', ctrl:true}, {key:'s', ctrl:true}]`
- Space-as-separator vs space-as-key handled: lone `" "` = space key

**`keystrokeToString(ks)`**: Canonical → display: `{key:'k', ctrl:true, shift:true}` → `"ctrl+shift+k"`

**`keystrokeToDisplayString(ks, platform)`**: Platform-appropriate display:
- macOS: `alt` → `opt`, `super` → `cmd`
- Other: `alt` → `alt`, `super` → `super`

**`parseBindings(blocks)`**: `KeybindingBlock[]` → `ParsedBinding[]` (flat list for matching)

### 4. `match.ts` (120 lines) — Ink Key Matching

Bridges Ink's Key object format with the parsed binding format:

**`getKeyName(input, key)`**: Maps Ink's boolean flags to string key names:
- `key.escape` → `'escape'`, `key.return` → `'enter'`, `key.tab` → `'tab'`
- `key.upArrow` → `'up'`, etc. (16 key flags mapped)
- Single-char input → lowercase

**`modifiersMatch(inkMods, target)`**: Compares modifier sets:
- Ctrl, shift: direct comparison
- Alt/meta: merged (terminal limitation — Ink sets `key.meta` for both)
- Super (cmd/win): distinct from alt/meta, only arrives via kitty protocol
- **Quirk**: escape key carries `meta=true` in Ink (legacy terminal behavior) — ignored for escape matching

**`matchesKeystroke(input, key, target)`**: Full keystroke match (key name + modifiers)

**`matchesBinding(input, key, binding)`**: Single-keystroke binding match (phase 1 only)

### 5. `resolver.ts` (244 lines) — Resolution Engine

**`resolveKey(input, key, activeContexts, bindings)` → `ResolveResult`**:
- Phase 1 (no chord state): filters bindings by active contexts + single-keystroke
- Last matching binding wins (user overrides come after defaults in the array)
- Returns `{type:'match', action}` | `{type:'none'}` | `{type:'unbound'}`
- Uses Set lookup for context filtering (O(n) instead of O(n*m))

**`resolveKeyWithChordState(input, key, activeContexts, bindings, pending)` → `ChordResolveResult`**:
Multi-keystroke chord state machine (5 result types):
- `'match'` — chord completed, action found
- `'none'` — no binding matches
- `'unbound'` — explicitly unbound (null action)
- `'chord_started'` — prefix matches longer chord, enter pending state
- `'chord_cancelled'` — chord broken (escape key or invalid continuation)

**Resolution algorithm**:
1. Escape cancels active chord
2. Build current keystroke (`buildKeystroke` from Ink)
3. If keystroke unparseable: cancel chord if pending, otherwise none
4. Build test chord: pending + current
5. Check for LONGER chord prefixes (prefer chord continuation over exact match)
6. `chordWinners` Map per chord string → if any non-null actions exist, prefer chord
7. Check exact matches (last wins)
8. If no match + pending chord: cancel

**`getBindingDisplayText(action, context, bindings)`**: Reverse lookup: find keystroke for action display (`ctrl+t` → `app:toggleTodos`). Uses `findLast` so user overrides take precedence.

**`keystrokesEqual(a, b)`**: Equality with alt/meta collapse (terminals can't distinguish them)

### 6. `validate.ts` (498 lines) — Binding Validation

Validates user keybindings.json for errors:

**Duplicate detection**:
- Same keystroke mapped to multiple actions in the same context → error
- Chord prefix collision: `ctrl+x` mapped AND `ctrl+x ctrl+k` also mapped → warning

**Reserved shortcuts** (from `reservedShortcuts.ts`):
- `ctrl+c` → `app:interrupt`: cannot be unbound or rebound
- `ctrl+d` → `app:exit`: cannot be unbound or rebound
- Overriding reserved shortcuts → error

**Context-action validity**:
- Action not valid in given context → warning (e.g., `confirm:yes` in Global context)

**Schema validation**:
- JSON shape validation via Zod
- Valid context check (19 allowed)
- Valid action check (~65 allowed)
- Null action = unbind (valid syntax)

**Error reporting**:
- Structured error types with: key, action, context, message
- User-friendly messages with suggestions for fixes

### 7. `reservedShortcuts.ts` (127 lines) — Reserved Keys

Defines keys that CANNOT be rebound by users:
- `ctrl+c` → `app:interrupt` (required for process control)
- `ctrl+d` → `app:exit` (required for graceful exit)
- These use special time-based double-press handling but MUST be defined in default bindings so the resolver finds them
- Validation rejects user overrides for these keys

### 8. `shortcutFormat.ts` (60 lines) — Shortcut Display Formatting

Platform-appropriate shortcut display:
- macOS: `⌘F` (symbol) vs Windows/Linux: `Ctrl+F` (text)
- Key symbol mapping: `cmd→⌘`, `shift→⇧`, `ctrl→⌃`, `alt/opt→⌥`, `enter→↵`, `space→␣`, `tab→⇥`, `escape→⎋`, `backspace→⌫`, `delete→⌦`

### 9. `template.ts` (52 lines) — Keybinding Template

Generates a template keybindings.json file for new users:
- Commented-out example bindings with documentation
- Context headers with short descriptions
- Escape hatch: `"{context}:{action}": null` syntax for unbinding

### 10. `useKeybinding.ts` (196 lines) — React Hook

**`useKeybinding(action, handler, context?)`**:
- Registers a callback for a keybinding action using the KeybindingContext
- Returns nothing — handler is registered/unregistered automatically
- Uses `registerHandler` from context, which stores `{action, context, handler}` in the `handlerRegistryRef` Map
- Auto-cleanup on unmount (returns `unregister` function from `registerHandler`)

### 11. `useShortcutDisplay.ts` (59 lines) — Display Hook

**`useShortcutDisplay(action, context?)`**:
- Returns the display text for a keybinding: `"ctrl+t"`, `"⌘T"` (platform-aware)
- Uses `getDisplayText` from KeybindingContext
- Falls back to no display if action is unbound

### 12. `loadUserBindings.ts` (472 lines) — User Config Loader

Loads and validates `~/.claude/keybindings.json`:
- Reads from config directory
- Parses JSON, validates schema
- Merges with defaults: user bindings appended after defaults (last-wins for overrides)
- Handles migration from old config format
- Error reporting: invalid bindings shown with line references
- Caching: parsed bindings cached until file changes

### 13. `KeybindingProviderSetup.tsx` (308 lines) — Provider Setup

Wires react-ink integration:
- Creates `pendingChordRef` (ref for immediate access, avoids React state lag)
- Creates `handlerRegistryRef` (Map<string, Set<HandlerRegistration>>)
- Manages `activeContexts` Set: components mount/unmount register their contexts
- `ChordInterceptor` component: reads Ink input, resolves via `resolveKeyWithChordState`, invokes handlers via `invokeAction`
- Bypasses React state loop by using ref for pending chord (immediate, not next-frame)

### 14. `KeybindingContext.tsx` (243 lines) — React Context

React context providing the full keybinding API to the component tree:

**Context Value** (`KeybindingContextValue`):
- `resolve(input, key, activeContexts)` — resolve to action (supports chord)
- `setPendingChord(pending)` / `pendingChord` — chord state
- `getDisplayText(action, context)` — display text for action
- `bindings` — all ParsedBinding[]
- `activeContexts` — Set of current context names
- `registerActiveContext(ctx)` / `unregisterActiveContext(ctx)` — mount/unmount lifecycle
- `registerHandler(registration)` — returns unsubscribe function
- `invokeAction(action)` — calls all registered handlers, returns true if any handled

Used by `useKeybinding` hook and `ChordInterceptor` for dispatching.

---

## PART 2: Vim Mode (5 files, ~1,400 lines)

### Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Vim State Machine                         │
│                                                             │
│  VimState = INSERT | NORMAL                                 │
│  NORMAL.command = CommandState (12-variant discriminated     │
│                   union state machine)                       │
│                                                             │
│  ┌──────┐    [d/c/y]    ┌──────────┐   [motion]   ┌──────┐ │
│  │ idle │──────────────►│ operator │─────────────►│ exec │ │
│  └──┬───┘               └────┬─────┘              └──────┘ │
│     │                        │                              │
│     │  [1-9]          [0-9]  │  [ia]                       │
│     ▼                        ▼             ▼                │
│  ┌───────┐          ┌──────────────┐  ┌──────────────┐     │
│  │ count │          │ operatorCount│  │opTextObj     │     │
│  └───────┘          └──────────────┘  └──────────────┘     │
│     │                        │             │                │
│     │  [f/F/t/T]      [f/F/t/T]    [text obj char]         │
│     ▼                        ▼             ▼                │
│  ┌──────┐          ┌───────────┐   ┌───────────┐           │
│  │ find │          │ opFind    │   │ [execute] │           │
│  └──────┘          └───────────┘   └───────────┘           │
│                                                             │
│  Other idle→... paths:                                      │
│    idle─[g]─►g─[g]─►gg   idle─[r]─►replace─[char]─►exec   │
│    idle─[><]─►indent     idle─[~/J/p/.]─►immediate exec     │
└─────────────────────────────────────────────────────────────┘
```

### 1. `vim/types.ts` (199 lines) — Complete Type System

**`VimState`** — top-level mode:
- `{mode:'INSERT', insertedText: string}` — tracks text for dot-repeat
- `{mode:'NORMAL', command: CommandState}` — state machine

**`CommandState`** (12-variant discriminated union):
- `{type:'idle'}` — waiting for command
- `{type:'count', digits: string}` — parsing count (e.g., `5dd`)
- `{type:'operator', op, count}` — waiting for motion (e.g., `d5` → waiting for `w`)
- `{type:'operatorCount', op, count, digits}` — operator + count (e.g., `d5` → still parsing digits)
- `{type:'operatorFind', op, count, find}` — operator + find mode waiting for char (e.g., `df` → waiting for `x`)
- `{type:'operatorTextObj', op, count, scope}` — operator + text object scope (e.g., `di` → waiting for `w`)
- `{type:'find', find, count}` — find motion parsing (e.g., `f` → waiting for char)
- `{type:'g', count}` — g-prefix waiting (e.g., `g` → waiting for `g`)
- `{type:'operatorG', op, count}` — operator + g-prefix waiting
- `{type:'replace', count}` — replace mode pending
- `{type:'indent', dir, count}` — indent operator pending

**`PersistentState`** — survives across commands:
- `lastChange: RecordedChange | null` — for dot-repeat (`.`)
- `lastFind: {type: FindType, char: string} | null` — for `;` / `,`
- `register: string` / `registerIsLinewise: boolean` — current yank register

**`RecordedChange`** (10-variant discriminated union):
- `{type:'insert', text}` — dot-repeat for insert mode
- `{type:'operator', op, motion, count}` — operator + motion
- `{type:'operatorTextObj', op, objType, scope, count}` — operator + text object
- `{type:'operatorFind', op, find, char, count}` — operator + find char
- `{type:'replace', char, count}` — replace command
- `{type:'x', count}` — x delete
- `{type:'toggleCase', count}` — ~ toggle case
- `{type:'indent', dir, count}` — > / < indent
- `{type:'openLine', direction}` — o / O open line
- `{type:'join', count}` — J join lines

**Key Groups** (immutable constants):
- `OPERATORS: {d:'delete', c:'change', y:'yank'}`
- `SIMPLE_MOTIONS` Set: h/l/j/k, w/b/e/W/B/E, 0/^/$ (13 motions)
- `FIND_KEYS` Set: f/F/t/T
- `TEXT_OBJ_SCOPES: {i:'inner', a:'around'}`
- `TEXT_OBJ_TYPES` Set: w/W/" /' /` /(/)/b/[/]/{/}/B/</> (15 types)
- `MAX_VIM_COUNT = 10000`

**State Factories**: `createInitialVimState()`, `createInitialPersistentState()`

### 2. `vim/transitions.ts` (490 lines) — State Machine Transition Table

Central dispatcher `transition(state, input, ctx)` → `TransitionResult` (`{next?: CommandState, execute?: () => void}`):

**Idle state transitions** (`fromIdle`):
- `ESC` / `ctrl+[` → enter insert mode (exit normal)
- `i` / `a` → enter insert at cursor/after
- `I` / `A` → enter insert at line start/end
- `o` / `O` → open line below/above + enter insert
- `d/c/y` + motion → operator pending
- `dd/cc/yy` → line operation
- `1-9` → count pending (shift: `digit → count`)
- `0` → motion to line start
- `f/F/t/T` → find pending
- `~` → toggle case (count)
- `x` → delete char
- `p/P` → paste
- `J` → join lines
- `>` / `<` → indent
- `g` → g-prefix pending
- `r` → replace pending
- `.` → dot-repeat (replay `lastChange`)

**Count state** (`fromCount`): accumulates digits, dispatches to operator/idle transitions with parsed count

**Operator state** (`fromOperator`):
- Simple motions (h/l/j/k/w/b/e/W/B/E/0/$/gj/gk) → execute
- `d/c/y` again → operator change (e.g., `d` → `c` switches to change)
- `0-9` → operatorCount
- `f/F/t/T` → operatorFind
- `i/a` → operatorTextObj
- `g` → operatorG

**Operator+Find** (`fromOperatorFind`): char input → `executeOperatorFind(op, findType, char, count, ctx)`

**Operator+TextObj** (`fromOperatorTextObj`): text object character → `executeOperatorTextObj(op, scope, objType, count, ctx)`

**Find pending** (`fromFind`): char input → resolve find motion (cursor movement)

### 3. `vim/motions.ts` (82 lines) — Motion Resolution

**`resolveMotion(key, cursor, count)`**: Applies motion `count` times, stops when position doesn't change (boundary detection)

**`applySingleMotion(key, cursor)` → `Cursor`**: 16 motions mapped to Cursor methods:
- `h/l` → `left()/right()`
- `j/k` → `downLogicalLine()/upLogicalLine()` (preserves visual column)
- `gj/gk` → `down()/up()` (wrapped line-aware)
- `w/b/e` → `nextVimWord()/prevVimWord()/endOfVimWord()` (word object)
- `W/B/E` → `nextWORD()/prevWORD()/endOfWORD()` (WORD object, whitespace-delimited)
- `0/^/$` → `startOfLogicalLine()/firstNonBlankInLogicalLine()/endOfLogicalLine()`
- `G` → `startOfLastLine()`

**`isInclusiveMotion(key)`**: `e/E/$` → destination character included in range

**`isLinewiseMotion(key)`**: `j/k/G/gg` → operates on full lines when combined with operators

### 4. `vim/operators.ts` (550 lines) — Operator Engine

All operators share a common context interface `OperatorContext`:
```typescript
{
  cursor: Cursor, text: string,
  setText(text), setOffset(offset), enterInsert(offset),
  getRegister()/setRegister(content, linewise),
  getLastFind()/setLastFind(type, char),
  recordChange(change)
}
```

**`executeOperatorMotion(op, motion, count, ctx)`**:
1. Resolve motion target via `resolveMotion(motion, cursor, count)`
2. Compute range: `getOperatorRange(from, to, motion, op, count)` — handles inclusive/exclusive/linewise boundary
3. `applyOperator(op, from, to, ctx, range.linewise)` → delegates to delete/change/yank
4. Record change for dot-repeat

**`executeOperatorFind(op, findType, char, count, ctx)`**:
- Uses `cursor.findCharacter(char, findType, count)` for find-based ranges
- Handles `f`/`F`/`t`/`T` semantics (inclusive vs exclusive)

**`executeOperatorTextObj(op, scope, objType, count, ctx)`**:
- Calls `findTextObject(text, offset, objType, isInner)` from `textObjects.ts`
- Applies operator to text object boundary range

**`executeLineOp(op, count, ctx)`**: `dd`/`cc`/`yy` — operates on `count` logical lines:
- Computes line boundaries by newline counting
- Sets register with linewise flag (for correct `p`/`P` paste behavior)
- Delete: removes line(s) including trailing newline
- Change: removes line(s) → enters insert mode
- Yank: copies to register, cursor unchanged

**`executeOperatorG/executeOperatorGg`**: `dG`/`cG`/`yG` and `dgg`/`cgg`/`ygg`

**`executeReplace(char, count, ctx)`**: `r{char}` replaces `count` characters at cursor

**`executeToggleCase(count, ctx)`**: `~` toggles case of `count` characters

**`executeIndent(dir, count, ctx)`**: `>` / `<` indents `count` lines

**`executeJoin(count, ctx)`**: `J` joins `count` lines

**`executePaste(before, ctx)`**: `p`/`P` pastes register content

**`executeX(count, ctx)`**: `x` deletes `count` characters

**`executeOpenLine(direction, ctx)`**: `o`/`O` opens line above/below

**`applyOperator(op, from, to, ctx, linewise?)`**: Core operator application:
- `delete`: removes range, sets register, adjusts cursor
- `change`: removes range, sets register, enters insert mode at range start
- `yank`: copies range to register, cursor at range start

**Range computation** (`getOperatorRange`): Handles:
- Characterwise: exclusive end for normal motions, inclusive for `e`/`E`/`$`
- Linewise: full lines from start to end

### 5. `vim/textObjects.ts` (186 lines) — Text Object Boundaries

**`findTextObject(text, offset, type, inner)` → `{start, end} | null`**:

**Word objects**:
- `iw` / `aw` — inner/around word (alphanumeric + underscore)
- `iW` / `aW` — inner/around WORD (non-whitespace)

**Quote objects** (with nesting support):
- `i"` / `a"` / `i'` / `a'` / `` i` `` / `` a` `` — quoted strings
- Scans backwards from cursor for opening quote, forwards for matching closing quote

**Bracket objects** (with nesting support):
- `i(` / `a(` / `ib` / `ab` — parentheses (pair)
- `i[` / `a[` — brackets (pair)
- `i{` / `a{` / `iB` / `aB` — braces (pair)
- `i<` / `a<` — angle brackets (pair)
- Nesting: counts depth of opening brackets to find matching close

**Inner vs Around**:
- Inner: excludes delimiters (e.g., `di(` → delete inside parens, keep parens)
- Around: includes delimiters (e.g., `da(` → delete including parens)

---

## PART 3: Voice Input (7 files, ~3,000 lines)

### 1. `voice/voiceModeEnabled.ts` (54 lines) — Voice Gate

- Checks `VOICE_MODE` build feature flag
- Checks GrowthBook gate for voice mode enablement
- Platform capability check (microphone access)
- Returns boolean for whether voice mode is available

### 2. `hooks/useVoice.ts` (1,086 lines) — Full Voice Integration Hook

The core voice recording/streaming/transcription hook:

**Voice State** (`VoiceState`):
- Mode: `idle` | `recording` | `transcribing` | `error`
- Audio buffer management: `audioBuffer` (accumulated PCM data)
- Audio levels: `currentLevel` (0-1 amplitude), `silenceDuration` for auto-stop
- VAD (Voice Activity Detection): determines when user stops speaking
- Error state: microphone permission denied, not supported, network error

**Lifecycle**:
1. **Start recording**: `startListening()` — requests mic, creates MediaStream, connects AudioContext
2. **Capture**: uses `AnalyserNode` for VAD, accumulates audio into buffer
3. **VAD**: monitors audio levels, detects silence threshold + duration for auto-stop
4. **Transcription**: sends audio to STT service via `voiceStreamSTT`
5. **Result**: processes transcription result, injects into input

**Audio Levels**: Uses `getByteFrequencyData` from AnalyserNode for real-time level visualization

**Key Features**:
- Push-to-talk: `holdSpace → record, release → transcribe`
- Toggle mode: `press → start recording, press again → stop + transcribe`
- Auto-stop: silence detection after configurable timeout
- Cancellation: escape key during recording → discard
- Error handling: permission denied, browser not supported, network errors
- Integration: results injected as user input

### 3. `hooks/useVoiceEnabled.ts` (24 lines) — Voice Availability Hook

- Returns whether voice input is currently available
- Combines feature gate, browser support, and permissions

### 4. `hooks/useVoiceIntegration.tsx` (677 lines) — Voice UI Integration

React component integration for voice mode:
- Renders voice indicator in the UI (microphone icon, audio level visualization)
- Manages recording state transitions
- Keyboard shortcut integration (space for push-to-talk)
- Message routing: transcribed text inserted into chat input
- Visual feedback: recording indicator, transcription progress, error states
- Accessibility: keyboard-accessible voice controls

### 5. `services/voice.ts` (525 lines) — Voice Service Backend

Lower-level voice processing service:
- Audio format handling (sample rate conversion, channel mixing)
- Buffer management and streaming
- Integration with speech-to-text API
- Error handling and retry logic
- Telemetry events for voice usage

### 6. `services/voiceStreamSTT.ts` (544 lines) — Speech-to-Text Streaming

Real-time streaming speech-to-text integration:
- WebSocket connection to STT service
- Chunked audio streaming with backpressure handling
- Interim results (shown while speaking) + final results (after stopping)
- Language detection/specification
- Connection management: reconnect on drop, timeout handling
- Configurable parameters: language, model, sampling rate

### 7. `services/voiceKeyterms.ts` (106 lines) — Voice Command Keyterms

Keyword/phrase definitions for voice commands:
- Command vocabulary: specific phrases mapped to actions
- Pattern matching: regex-based keyword detection
- Local processing: client-side keyterm detection (no server round-trip)
- Configurable keyterms list (per language/locale)

---

## Key Design Decisions

### Keybindings

1. **Last-wins override model** — User bindings appended after defaults, creating a flat array where later entries override earlier ones (simple, predictable)

2. **Context-based scoping** — 19 contexts allow the same keystroke to mean different things depending on which UI component has focus (e.g., `enter` submits in Chat but confirms in Confirmation)

3. **Chord support without readline interference** — All chords prefixed with `ctrl+x` to avoid conflicting with readline's reserved `ctrl+a/b/e/f/n/p` editing keys

4. **Platform-aware key display** — macOS users see `⌘T` and `opt`; Linux/Windows users see `Ctrl+T` and `alt`; fallback bindings when terminal VT mode is unavailable

5. **Ref-based pending chord** — Chord state stored in ref (not React state) for zero-latency resolution, avoiding the "one frame behind" problem that would cause chord delay

6. **Reserved shortcuts** — `ctrl+c` and `ctrl+d` use special time-based double-press handling but CANNOT be unbound; user attempts produce validation errors

7. **Null-unbinding semantics** — `{action: null}` explicitly removes a default binding (not "do nothing" which would eat the key event)

### Vim Mode

1. **Discriminated union state machine** — 12-state CommandState ensures TypeScript exhaustiveness checking; impossible to forget handling a transition

2. **Pure cursor operations** — `motions.ts` and `operators.ts` are pure functions operating on immutable `Cursor` objects; side effects (setText, setOffset, enterInsert) injected via `OperatorContext`

3. **Dot-repeat via recorded changes** — `RecordedChange` captures exact semantics (operator + motion + count, not byte offsets) so `.` replays correctly regardless of cursor position

4. **Text object nesting** — Parentheses/bracket matching counts nesting depth, correctly handling `di(` when cursor is inside nested parens

5. **Linewise vs characterwise registers** — Deleted content tagged as linewise (`registerIsLinewise`) so `p`/`P` paste inserts on new line vs inline

6. **Logical vs wrapped lines** — `j/k` use logical lines (preserving visual column); `gj/gk` use wrapped display lines

### Voice

1. **Streaming STT** — Audio sent in chunks as soon as recorded (not batch after recording stops) for lower latency

2. **VAD auto-stop** — Client-side voice activity detection eliminates the need for manual stop; user just pauses

3. **Feature-gated entirely** — `VOICE_MODE` build flag + GrowthBook gate ensures zero runtime cost in external builds; `require()` used for lazy loading to avoid bundling voice modules

4. **Dual recording mode** — Push-to-talk (hold space) and toggle (press to start, press to stop) support different user preferences

5. **Audio level visualization** — Real-time level meter using Web Audio API AnalyzerNode for user feedback
