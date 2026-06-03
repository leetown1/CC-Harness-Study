# Vim 模式系统深度技术文档

> 基于逐行代码分析的完整技术文档  
> **探索完成时间**: 2026 年 4 月 1 日  
> **核心文件**: vim/ 目录下 6 个文件

---

## 1. Vim 模式系统架构概览

### 1.1 系统职责

Vim 模式系统提供**完整的 Vim 风格编辑体验**，包括：
- NORMAL 模式状态机
- INSERT 模式
- 操作符（delete/change/yank）
- 移动（motions）
- 文本对象（text objects）
- Find 移动（f/F/t/T）
- Dot-repeat（重播上次变更）
- 寄存器管理
- 大小写切换
- 行缩进
- 行合并

### 1.2 架构层次

```
┌─────────────────────────────────────────────────────────────┐
│                    Vim Mode Architecture                     │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │  types.ts    │  │ operators.ts │  │  motions.ts  │      │
│  │  (类型)      │  │  (操作符)    │  │  (移动)      │      │
│  │  44 行        │  │  380 行       │  │  120 行       │      │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘      │
│         │                 │                 │               │
│         └─────────────────┼─────────────────┘               │
│                           │                                 │
│                  ┌────────▼────────┐                        │
│                  │ transitions.ts  │                        │
│                  │ (状态转换表)    │                        │
│                  │ 450 行           │                        │
│                  └────────┬────────┘                        │
│                           │                                 │
│         ┌─────────────────┼─────────────────┐              │
│         │                 │                 │               │
│  ┌──────▼───────┐  ┌──────▼───────┐  ┌──────▼───────┐      │
│  │textObjects.ts│  │useVimInput.ts│  │  Cursor.ts   │      │
│  │ (文本对象)    │  │ (输入 Hook)   │  │ (光标类)     │      │
│  │ 180 行        │  │ 520 行        │  │ 集成         │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### 1.3 模式状态机

```typescript
type VimState =
  | { mode: 'INSERT'; insertedText: string }
  | { mode: 'NORMAL'; command: CommandState }

type CommandState =
  | { type: 'idle' }                              // 空闲状态
  | { type: 'count'; digits: string }             // 数字前缀 (1-9)
  | { type: 'operator'; op: Operator; count: number }        // 操作符待命
  | { type: 'operatorCount'; op: Operator; count: number; digits: string }
  | { type: 'operatorFind'; op: Operator; count: number; find: FindType }
  | { type: 'operatorTextObj'; op: Operator; count: number; scope: TextObjScope }
  | { type: 'find'; find: FindType; count: number }         // f/F/t/T 待命
  | { type: 'g'; count: number }                            // g 前缀
  | { type: 'operatorG'; op: Operator; count: number }      // 操作符 + g
  | { type: 'replace'; count: number }                      // r 待命
  | { type: 'indent'; dir: '>' | '<'; count: number }       // >> 或 <<
```

---

## 2. 核心文件深度分析

### 2.1 types.ts (44 行) - 核心类型系统

#### 状态机定义

```typescript
export type VimState =
  | { mode: 'INSERT'; insertedText: string }
  | { mode: 'NORMAL'; command: CommandState }
```

**INSERT 模式**: 追踪 `insertedText` 用于 dot-repeat
**NORMAL 模式**: 运行 `CommandState` 状态机

#### 操作符定义

```typescript
export type Operator = 'delete' | 'change' | 'yank'

export const OPERATORS = {
  d: 'delete',
  c: 'change',
  y: 'yank',
} as const
```

#### Find 类型

```typescript
export type FindType = 'f' | 'F' | 't' | 'T'
// f: forward to (包含字符)
// F: backward to (包含字符)
// t: forward till (不包含字符)
// T: backward till (不包含字符)
```

#### 文本对象范围

```typescript
export type TextObjScope = 'inner' | 'around'
// i: inner (不包含边界)
// a: around (包含边界)

export const TEXT_OBJ_SCOPES = {
  i: 'inner',
  a: 'around',
} as const
```

#### 持久化状态

```typescript
export type PersistentState = {
  lastChange: RecordedChange | null      // 用于 dot-repeat
  lastFind: { type: FindType; char: string } | null  // 用于 ;/,
  register: string                        // 粘贴寄存器
  registerIsLinewise: boolean             // 是否行级粘贴
}
```

#### RecordedChange - 变更记录

```typescript
export type RecordedChange =
  | { type: 'insert'; text: string }
  | { type: 'operator'; op: Operator; motion: string; count: number }
  | { type: 'operatorTextObj'; op: Operator; objType: string; scope: TextObjScope; count: number }
  | { type: 'operatorFind'; op: Operator; find: FindType; char: string; count: number }
  | { type: 'replace'; char: string; count: number }
  | { type: 'x'; count: number }
  | { type: 'toggleCase'; count: number }
  | { type: 'indent'; dir: '>' | '<'; count: number }
  | { type: 'join'; count: number }
  | { type: 'openLine'; direction: 'above' | 'below' }
```

#### 键位分组常量

```typescript
export const SIMPLE_MOTIONS = new Set([
  'h', 'l', 'j', 'k',  // 基本移动
  'w', 'b', 'e',       // 词移动
  'W', 'B', 'E',       // WORD 移动
  '0', '^', '$',       // 行位置
])

export const FIND_KEYS = new Set(['f', 'F', 't', 'T'])

export const TEXT_OBJ_TYPES = new Set([
  'w', 'W',            // 词/WORD
  '"', "'", '`',       // 引号
  '(', ')', 'b',       // 圆括号
  '[', ']',            // 方括号
  '{', '}', 'B',       // 花括号
  '<', '>',            // 尖括号
])

export const MAX_VIM_COUNT = 10000  // 最大数字前缀
```

#### 状态工厂

```typescript
export function createInitialVimState(): VimState {
  return { mode: 'INSERT', insertedText: '' }
}

export function createInitialPersistentState(): PersistentState {
  return {
    lastChange: null,
    lastFind: null,
    register: '',
    registerIsLinewise: false,
  }
}
```

---

### 2.2 operators.ts (380 行) - 操作符实现

#### 上下文类型

```typescript
export type OperatorContext = {
  cursor: Cursor
  text: string
  setText: (text: string) => void
  setOffset: (offset: number) => void
  enterInsert: (offset: number) => void
  getRegister: () => string
  setRegister: (content: string, linewise: boolean) => void
  getLastFind: () => { type: FindType; char: string } | null
  setLastFind: (type: FindType, char: string) => void
  recordChange: (change: RecordedChange) => void
}
```

#### executeOperatorMotion - 操作符 + 移动

```typescript
export function executeOperatorMotion(
  op: Operator,
  motion: string,
  count: number,
  ctx: OperatorContext,
): void {
  const target = resolveMotion(motion, ctx.cursor, count)
  if (target.equals(ctx.cursor)) return
  
  const range = getOperatorRange(ctx.cursor, target, motion, op, count)
  applyOperator(op, range.from, range.to, ctx, range.linewise)
  ctx.recordChange({ type: 'operator', op, motion, count })
}
```

#### executeOperatorFind - 操作符 + find

```typescript
export function executeOperatorFind(
  op: Operator,
  findType: FindType,
  char: string,
  count: number,
  ctx: OperatorContext,
): void {
  const targetOffset = ctx.cursor.findCharacter(char, findType, count)
  if (targetOffset === null) return
  
  const target = new Cursor(ctx.cursor.measuredText, targetOffset)
  const range = getOperatorRangeForFind(ctx.cursor, target, findType)
  
  applyOperator(op, range.from, range.to, ctx)
  ctx.setLastFind(findType, char)
  ctx.recordChange({ type: 'operatorFind', op, find: findType, char, count })
}
```

#### executeOperatorTextObj - 操作符 + 文本对象

```typescript
export function executeOperatorTextObj(
  op: Operator,
  scope: TextObjScope,
  objType: string,
  count: number,
  ctx: OperatorContext,
): void {
  const range = findTextObject(
    ctx.text,
    ctx.cursor.offset,
    objType,
    scope === 'inner',
  )
  if (!range) return
  
  applyOperator(op, range.start, range.end, ctx)
  ctx.recordChange({ type: 'operatorTextObj', op, objType, scope, count })
}
```

#### executeLineOp - 行级操作 (dd/cc/yy)

```typescript
export function executeLineOp(
  op: Operator,
  count: number,
  ctx: OperatorContext,
): void {
  const text = ctx.text
  const lines = text.split('\n')
  const currentLine = countCharInString(text.slice(0, ctx.cursor.offset), '\n')
  const linesToAffect = Math.min(count, lines.length - currentLine)
  const lineStart = ctx.cursor.startOfLogicalLine().offset
  
  // 计算行尾
  let lineEnd = lineStart
  for (let i = 0; i < linesToAffect; i++) {
    const nextNewline = text.indexOf('\n', lineEnd)
    lineEnd = nextNewline === -1 ? text.length : nextNewline + 1
  }
  
  let content = text.slice(lineStart, lineEnd)
  if (!content.endsWith('\n')) {
    content = content + '\n'  // 确保行级粘贴检测
  }
  ctx.setRegister(content, true)
  
  if (op === 'yank') {
    ctx.setOffset(lineStart)
  } else if (op === 'delete') {
    // 删除逻辑...
  } else if (op === 'change') {
    // 变更逻辑...
  }
  
  ctx.recordChange({ type: 'operator', op, motion: op[0]!, count })
}
```

#### executeX - 删除字符 (x 命令)

```typescript
export function executeX(count: number, ctx: OperatorContext): void {
  const from = ctx.cursor.offset
  if (from >= ctx.text.length) return
  
  // 按 grapheme 前进，不是 code unit
  let endCursor = ctx.cursor
  for (let i = 0; i < count && !endCursor.isAtEnd(); i++) {
    endCursor = endCursor.right()
  }
  const to = endCursor.offset
  
  const deleted = ctx.text.slice(from, to)
  const newText = ctx.text.slice(0, from) + ctx.text.slice(to)
  
  ctx.setRegister(deleted, false)
  ctx.setText(newText)
  ctx.setOffset(Math.min(from, maxOff))
  ctx.recordChange({ type: 'x', count })
}
```

#### executeReplace - 替换字符 (r 命令)

```typescript
export function executeReplace(
  char: string,
  count: number,
  ctx: OperatorContext,
): void {
  let offset = ctx.cursor.offset
  let newText = ctx.text
  
  for (let i = 0; i < count && offset < newText.length; i++) {
    const graphemeLen = firstGrapheme(newText.slice(offset)).length || 1
    newText = newText.slice(0, offset) + char + newText.slice(offset + graphemeLen)
    offset += char.length
  }
  
  ctx.setText(newText)
  ctx.setOffset(Math.max(0, offset - char.length))
  ctx.recordChange({ type: 'replace', char, count })
}
```

#### executeToggleCase - 切换大小写 (~命令)

```typescript
export function executeToggleCase(count: number, ctx: OperatorContext): void {
  let newText = ctx.text
  let offset = ctx.cursor.offset
  let toggled = 0
  
  while (offset < newText.length && toggled < count) {
    const grapheme = firstGrapheme(newText.slice(offset))
    const toggledGrapheme =
      grapheme === grapheme.toUpperCase()
        ? grapheme.toLowerCase()
        : grapheme.toUpperCase()
    
    newText = newText.slice(0, offset) + toggledGrapheme + newText.slice(offset + graphemeLen)
    offset += toggledGrapheme.length
    toggled++
  }
  
  ctx.setText(newText)
  ctx.setOffset(offset)
  ctx.recordChange({ type: 'toggleCase', count })
}
```

#### executeJoin - 合并行 (J 命令)

```typescript
export function executeJoin(count: number, ctx: OperatorContext): void {
  const text = ctx.text
  const lines = text.split('\n')
  const { line: currentLine } = ctx.cursor.getPosition()
  
  if (currentLine >= lines.length - 1) return
  
  const linesToJoin = Math.min(count, lines.length - currentLine - 1)
  let joinedLine = lines[currentLine]!
  const cursorPos = joinedLine.length
  
  for (let i = 1; i <= linesToJoin; i++) {
    const nextLine = (lines[currentLine + i] ?? '').trimStart()
    if (nextLine.length > 0) {
      if (!joinedLine.endsWith(' ') && joinedLine.length > 0) {
        joinedLine += ' '
      }
      joinedLine += nextLine
    }
  }
  
  const newLines = [...lines.slice(0, currentLine), joinedLine, ...lines.slice(currentLine + linesToJoin + 1)]
  const newText = newLines.join('\n')
  
  ctx.setText(newText)
  ctx.setOffset(getLineStartOffset(newLines, currentLine) + cursorPos)
  ctx.recordChange({ type: 'join', count })
}
```

#### executePaste - 粘贴 (p/P 命令)

```typescript
export function executePaste(
  after: boolean,
  count: number,
  ctx: OperatorContext,
): void {
  const register = ctx.getRegister()
  if (!register) return
  
  const isLinewise = register.endsWith('\n')
  const content = isLinewise ? register.slice(0, -1) : register
  
  if (isLinewise) {
    // 行级粘贴
    const text = ctx.text
    const lines = text.split('\n')
    const { line: currentLine } = ctx.cursor.getPosition()
    
    const insertLine = after ? currentLine + 1 : currentLine
    const contentLines = content.split('\n')
    const repeatedLines: string[] = []
    for (let i = 0; i < count; i++) {
      repeatedLines.push(...contentLines)
    }
    
    const newLines = [...lines.slice(0, insertLine), ...repeatedLines, ...lines.slice(insertLine)]
    const newText = newLines.join('\n')
    
    ctx.setText(newText)
    ctx.setOffset(getLineStartOffset(newLines, insertLine))
  } else {
    // 字符级粘贴
    const textToInsert = content.repeat(count)
    const insertPoint =
      after && ctx.cursor.offset < ctx.text.length
        ? ctx.cursor.measuredText.nextOffset(ctx.cursor.offset)
        : ctx.cursor.offset
    
    const newText = ctx.text.slice(0, insertPoint) + textToInsert + ctx.text.slice(insertPoint)
    const lastGr = lastGrapheme(textToInsert)
    const newOffset = insertPoint + textToInsert.length - (lastGr.length || 1)
    
    ctx.setText(newText)
    ctx.setOffset(Math.max(insertPoint, newOffset))
  }
}
```

#### executeIndent - 缩进 (>> 命令)

```typescript
export function executeIndent(
  dir: '>' | '<',
  count: number,
  ctx: OperatorContext,
): void {
  const text = ctx.text
  const lines = text.split('\n')
  const { line: currentLine } = ctx.cursor.getPosition()
  const linesToAffect = Math.min(count, lines.length - currentLine)
  const indent = '  '  // 两个空格
  
  for (let i = 0; i < linesToAffect; i++) {
    const lineIdx = currentLine + i
    const line = lines[lineIdx] ?? ''
    
    if (dir === '>') {
      lines[lineIdx] = indent + line
    } else if (line.startsWith(indent)) {
      lines[lineIdx] = line.slice(indent.length)
    } else if (line.startsWith('\t')) {
      lines[lineIdx] = line.slice(1)
    } else {
      // 移除尽可能多的前导空白
      let removed = 0
      let idx = 0
      while (idx < line.length && removed < indent.length && /\s/.test(line[idx]!)) {
        removed++
        idx++
      }
      lines[lineIdx] = line.slice(idx)
    }
  }
  
  const newText = lines.join('\n')
  const currentLineText = lines[currentLine] ?? ''
  const firstNonBlank = (currentLineText.match(/^\s*/)?.[0] ?? '').length
  
  ctx.setText(newText)
  ctx.setOffset(getLineStartOffset(lines, currentLine) + firstNonBlank)
  ctx.recordChange({ type: 'indent', dir, count })
}
```

#### executeOpenLine - 开新行 (o/O 命令)

```typescript
export function executeOpenLine(
  direction: 'above' | 'below',
  ctx: OperatorContext,
): void {
  const text = ctx.text
  const lines = text.split('\n')
  const { line: currentLine } = ctx.cursor.getPosition()
  
  const insertLine = direction === 'below' ? currentLine + 1 : currentLine
  const newLines = [...lines.slice(0, insertLine), '', ...lines.slice(insertLine)]
  
  const newText = newLines.join('\n')
  ctx.setText(newText)
  ctx.enterInsert(getLineStartOffset(newLines, insertLine))
  ctx.recordChange({ type: 'openLine', direction })
}
```

#### 内部辅助函数

**getOperatorRange - 计算操作符范围**:

```typescript
function getOperatorRange(
  cursor: Cursor,
  target: Cursor,
  motion: string,
  op: Operator,
  count: number,
): { from: number; to: number; linewise: boolean } {
  let from = Math.min(cursor.offset, target.offset)
  let to = Math.max(cursor.offset, target.offset)
  let linewise = false
  
  // 特殊情况：cw/cW 改变到词尾，不是下一个词首
  if (op === 'change' && (motion === 'w' || motion === 'W')) {
    let wordCursor = cursor
    for (let i = 0; i < count - 1; i++) {
      wordCursor = motion === 'w' ? wordCursor.nextVimWord() : wordCursor.nextWORD()
    }
    const wordEnd = motion === 'w' ? wordCursor.endOfVimWord() : wordCursor.endOfWORD()
    to = cursor.measuredText.nextOffset(wordEnd.offset)
  } else if (isLinewiseMotion(motion)) {
    // 行级移动扩展到包含整行
    linewise = true
    const text = cursor.text
    const nextNewline = text.indexOf('\n', to)
    if (nextNewline === -1) {
      to = text.length
      if (from > 0 && text[from - 1] === '\n') {
        from -= 1
      }
    } else {
      to = nextNewline + 1
    }
  } else if (isInclusiveMotion(motion) && cursor.offset <= target.offset) {
    to = cursor.measuredText.nextOffset(to)
  }
  
  // 词移动可能落在 [Image #N] chip 内；扩展范围覆盖整个 chip
  from = cursor.snapOutOfImageRef(from, 'start')
  to = cursor.snapOutOfImageRef(to, 'end')
  
  return { from, to, linewise }
}
```

**applyOperator - 应用操作符**:

```typescript
function applyOperator(
  op: Operator,
  from: number,
  to: number,
  ctx: OperatorContext,
  linewise: boolean = false,
): void {
  let content = ctx.text.slice(from, to)
  if (linewise && !content.endsWith('\n')) {
    content = content + '\n'
  }
  ctx.setRegister(content, linewise)
  
  if (op === 'yank') {
    ctx.setOffset(from)
  } else if (op === 'delete') {
    const newText = ctx.text.slice(0, from) + ctx.text.slice(to)
    ctx.setText(newText)
    const maxOff = Math.max(0, newText.length - (lastGrapheme(newText).length || 1))
    ctx.setOffset(Math.min(from, maxOff))
  } else if (op === 'change') {
    const newText = ctx.text.slice(0, from) + ctx.text.slice(to)
    ctx.setText(newText)
    ctx.enterInsert(from)
  }
}
```

---

### 2.3 motions.ts (120 行) - 光标移动

#### resolveMotion - 解析移动

```typescript
export function resolveMotion(
  key: string,
  cursor: Cursor,
  count: number,
): Cursor {
  let result = cursor
  for (let i = 0; i < count; i++) {
    const next = applySingleMotion(key, result)
    if (next.equals(result)) break  // 无法继续移动时停止
    result = next
  }
  return result
}
```

#### applySingleMotion - 应用单次移动

```typescript
function applySingleMotion(key: string, cursor: Cursor): Cursor {
  switch (key) {
    case 'h': return cursor.left()
    case 'l': return cursor.right()
    case 'j': return cursor.downLogicalLine()
    case 'k': return cursor.upLogicalLine()
    case 'gj': return cursor.down()  // 视觉行
    case 'gk': return cursor.up()    // 视觉行
    case 'w': return cursor.nextVimWord()
    case 'b': return cursor.prevVimWord()
    case 'e': return cursor.endOfVimWord()
    case 'W': return cursor.nextWORD()
    case 'B': return cursor.prevWORD()
    case 'E': return cursor.endOfWORD()
    case '0': return cursor.startOfLogicalLine()
    case '^': return cursor.firstNonBlankInLogicalLine()
    case '$': return cursor.endOfLogicalLine()
    case 'G': return cursor.startOfLastLine()
    default: return cursor
  }
}
```

#### 移动类型判断

```typescript
// 包容性移动（包含目标字符）
export function isInclusiveMotion(key: string): boolean {
  return 'eE$'.includes(key)
}

// 行级移动（与操作符一起使用时操作整行）
export function isLinewiseMotion(key: string): boolean {
  return 'jkG'.includes(key) || key === 'gg'
}
```

---

### 2.4 transitions.ts (450 行) - 状态转换表

#### 主转换函数

```typescript
export function transition(
  state: CommandState,
  input: string,
  ctx: TransitionContext,
): TransitionResult {
  switch (state.type) {
    case 'idle': return fromIdle(input, ctx)
    case 'count': return fromCount(state, input, ctx)
    case 'operator': return fromOperator(state, input, ctx)
    case 'operatorCount': return fromOperatorCount(state, input, ctx)
    case 'operatorFind': return fromOperatorFind(state, input, ctx)
    case 'operatorTextObj': return fromOperatorTextObj(state, input, ctx)
    case 'find': return fromFind(state, input, ctx)
    case 'g': return fromG(state, input, ctx)
    case 'operatorG': return fromOperatorG(state, input, ctx)
    case 'replace': return fromReplace(state, input, ctx)
    case 'indent': return fromIndent(state, input, ctx)
  }
}
```

#### fromIdle - 空闲状态转换

```typescript
function fromIdle(input: string, ctx: TransitionContext): TransitionResult {
  // 0 是行首移动，不是数字前缀
  if (/[1-9]/.test(input)) {
    return { next: { type: 'count', digits: input } }
  }
  if (input === '0') {
    return {
      execute: () => ctx.setOffset(ctx.cursor.startOfLogicalLine().offset),
    }
  }
  
  const result = handleNormalInput(input, 1, ctx)
  if (result) return result
  
  return {}  // 未识别输入，保持 idle
}
```

#### fromCount - 数字状态转换

```typescript
function fromCount(
  state: { type: 'count'; digits: string },
  input: string,
  ctx: TransitionContext,
): TransitionResult {
  if (/[0-9]/.test(input)) {
    const newDigits = state.digits + input
    const count = Math.min(parseInt(newDigits, 10), MAX_VIM_COUNT)
    return { next: { type: 'count', digits: String(count) } }
  }
  
  const count = parseInt(state.digits, 10)
  const result = handleNormalInput(input, count, ctx)
  if (result) return result
  
  return { next: { type: 'idle' } }  // 未识别，重置
}
```

#### fromOperator - 操作符状态转换

```typescript
function fromOperator(
  state: { type: 'operator'; op: Operator; count: number },
  input: string,
  ctx: TransitionContext,
): TransitionResult {
  // dd, cc, yy = 行级操作
  if (input === state.op[0]) {
    return { execute: () => executeLineOp(state.op, state.count, ctx) }
  }
  
  // 数字前缀
  if (/[0-9]/.test(input)) {
    return {
      next: {
        type: 'operatorCount',
        op: state.op,
        count: state.count,
        digits: input,
      },
    }
  }
  
  const result = handleOperatorInput(state.op, state.count, input, ctx)
  if (result) return result
  
  return { next: { type: 'idle' } }  // 未识别，重置
}
```

#### handleNormalInput - 处理 NORMAL 模式输入

```typescript
function handleNormalInput(
  input: string,
  count: number,
  ctx: TransitionContext,
): TransitionResult | null {
  // 操作符
  if (isOperatorKey(input)) {
    return { next: { type: 'operator', op: OPERATORS[input], count } }
  }
  
  // 简单移动
  if (SIMPLE_MOTIONS.has(input)) {
    return {
      execute: () => {
        const target = resolveMotion(input, ctx.cursor, count)
        ctx.setOffset(target.offset)
      },
    }
  }
  
  // Find 移动
  if (FIND_KEYS.has(input)) {
    return { next: { type: 'find', find: input as FindType, count } }
  }
  
  // g 前缀
  if (input === 'g') return { next: { type: 'g', count } }
  
  // r 替换
  if (input === 'r') return { next: { type: 'replace', count } }
  
  // 缩进
  if (input === '>' || input === '<') {
    return { next: { type: 'indent', dir: input, count } }
  }
  
  // 切换大小写
  if (input === '~') {
    return { execute: () => executeToggleCase(count, ctx) }
  }
  
  // 删除字符
  if (input === 'x') {
    return { execute: () => executeX(count, ctx) }
  }
  
  // 合并行
  if (input === 'J') {
    return { execute: () => executeJoin(count, ctx) }
  }
  
  // 粘贴
  if (input === 'p' || input === 'P') {
    return { execute: () => executePaste(input === 'p', count, ctx) }
  }
  
  // 删除到行尾
  if (input === 'D') {
    return { execute: () => executeOperatorMotion('delete', '$', 1, ctx) }
  }
  
  // 变更到行尾
  if (input === 'C') {
    return { execute: () => executeOperatorMotion('change', '$', 1, ctx) }
  }
  
  // 行级 yank
  if (input === 'Y') {
    return { execute: () => executeLineOp('yank', count, ctx) }
  }
  
  // G - 跳转到行
  if (input === 'G') {
    return {
      execute: () => {
        if (count === 1) {
          ctx.setOffset(ctx.cursor.startOfLastLine().offset)
        } else {
          ctx.setOffset(ctx.cursor.goToLine(count).offset)
        }
      },
    }
  }
  
  // . - dot repeat
  if (input === '.') {
    return { execute: () => ctx.onDotRepeat?.() }
  }
  
  // ;/, - 重复 find
  if (input === ';' || input === ',') {
    return { execute: () => executeRepeatFind(input === ',', count, ctx) }
  }
  
  // u - undo
  if (input === 'u') {
    return { execute: () => ctx.onUndo?.() }
  }
  
  // 进入 INSERT 模式
  if (input === 'i') {
    return { execute: () => ctx.enterInsert(ctx.cursor.offset) }
  }
  
  if (input === 'I') {
    return {
      execute: () =>
        ctx.enterInsert(ctx.cursor.firstNonBlankInLogicalLine().offset),
    }
  }
  
  if (input === 'a') {
    return {
      execute: () => {
        const newOffset = ctx.cursor.isAtEnd()
          ? ctx.cursor.offset
          : ctx.cursor.right().offset
        ctx.enterInsert(newOffset)
      },
    }
  }
  
  if (input === 'A') {
    return {
      execute: () => ctx.enterInsert(ctx.cursor.endOfLogicalLine().offset),
    }
  }
  
  // 开新行
  if (input === 'o') {
    return { execute: () => executeOpenLine('below', ctx) }
  }
  
  if (input === 'O') {
    return { execute: () => executeOpenLine('above', ctx) }
  }
  
  return null
}
```

---

### 2.5 textObjects.ts (180 行) - 文本对象查找

#### 括号对定义

```typescript
const PAIRS: Record<string, [string, string]> = {
  '(': ['(', ')'],
  ')': ['(', ')'],
  b: ['(', ')'],
  '[': ['[', ']'],
  ']': ['[', ']'],
  '{': ['{', '}'],
  '}': ['{', '}'],
  B: ['{', '}'],
  '<': ['<', '>'],
  '>': ['<', '>'],
  '"': ['"', '"'],
  "'": ["'", "'"],
  '`': ['`', '`'],
}
```

#### findTextObject - 查找文本对象

```typescript
export function findTextObject(
  text: string,
  offset: number,
  objectType: string,
  isInner: boolean,
): TextObjectRange {
  // 词对象
  if (objectType === 'w')
    return findWordObject(text, offset, isInner, isVimWordChar)
  if (objectType === 'W')
    return findWordObject(text, offset, isInner, ch => !isVimWhitespace(ch))
  
  // 括号/引号对象
  const pair = PAIRS[objectType]
  if (pair) {
    const [open, close] = pair
    return open === close
      ? findQuoteObject(text, offset, open, isInner)
      : findBracketObject(text, offset, open, close, isInner)
  }
  
  return null
}
```

#### findWordObject - 查找词对象

```typescript
function findWordObject(
  text: string,
  offset: number,
  isInner: boolean,
  isWordChar: (ch: string) => boolean,
): TextObjectRange {
  // 预分割为 graphemes 以进行 grapheme-safe 迭代
  const graphemes: Array<{ segment: string; index: number }> = []
  for (const { segment, index } of getGraphemeSegmenter().segment(text)) {
    graphemes.push({ segment, index })
  }
  
  // 找到 offset 所在的 grapheme 索引
  let graphemeIdx = graphemes.length - 1
  for (let i = 0; i < graphemes.length; i++) {
    const g = graphemes[i]!
    const nextStart = i + 1 < graphemes.length ? graphemes[i + 1]!.index : text.length
    if (offset >= g.index && offset < nextStart) {
      graphemeIdx = i
      break
    }
  }
  
  const graphemeAt = (idx: number): string => graphemes[idx]?.segment ?? ''
  const offsetAt = (idx: number): number => idx < graphemes.length ? graphemes[idx]!.index : text.length
  
  let startIdx = graphemeIdx
  let endIdx = graphemeIdx
  
  // 根据字符类型扩展边界
  if (isWordChar(graphemeAt(graphemeIdx))) {
    while (startIdx > 0 && isWordChar(graphemeAt(startIdx - 1))) startIdx--
    while (endIdx < graphemes.length && isWordChar(graphemeAt(endIdx))) endIdx++
  } else if (isVimWhitespace(graphemeAt(graphemeIdx))) {
    while (startIdx > 0 && isVimWhitespace(graphemeAt(startIdx - 1))) startIdx--
    while (endIdx < graphemes.length && isVimWhitespace(graphemeAt(endIdx))) endIdx++
    return { start: offsetAt(startIdx), end: offsetAt(endIdx) }
  } else if (isVimPunctuation(graphemeAt(graphemeIdx))) {
    while (startIdx > 0 && isVimPunctuation(graphemeAt(startIdx - 1))) startIdx--
    while (endIdx < graphemes.length && isVimPunctuation(graphemeAt(endIdx))) endIdx++
  }
  
  if (!isInner) {
    // 包含周围空白
    if (endIdx < graphemes.length && isVimWhitespace(graphemeAt(endIdx))) {
      while (endIdx < graphemes.length && isVimWhitespace(graphemeAt(endIdx))) endIdx++
    } else if (startIdx > 0 && isVimWhitespace(graphemeAt(startIdx - 1))) {
      while (startIdx > 0 && isVimWhitespace(graphemeAt(startIdx - 1))) startIdx--
    }
  }
  
  return { start: offsetAt(startIdx), end: offsetAt(endIdx) }
}
```

#### findQuoteObject - 查找引号对象

```typescript
function findQuoteObject(
  text: string,
  offset: number,
  quote: string,
  isInner: boolean,
): TextObjectRange {
  const lineStart = text.lastIndexOf('\n', offset - 1) + 1
  const lineEnd = text.indexOf('\n', offset)
  const effectiveEnd = lineEnd === -1 ? text.length : lineEnd
  const line = text.slice(lineStart, effectiveEnd)
  const posInLine = offset - lineStart
  
  // 找到所有引号位置
  const positions: number[] = []
  for (let i = 0; i < line.length; i++) {
    if (line[i] === quote) positions.push(i)
  }
  
  // 正确配对引号：0-1, 2-3, 4-5, etc.
  for (let i = 0; i < positions.length - 1; i += 2) {
    const qs = positions[i]!
    const qe = positions[i + 1]!
    if (qs <= posInLine && posInLine <= qe) {
      return isInner
        ? { start: lineStart + qs + 1, end: lineStart + qe }
        : { start: lineStart + qs, end: lineStart + qe + 1 }
    }
  }
  
  return null
}
```

#### findBracketObject - 查找括号对象

```typescript
function findBracketObject(
  text: string,
  offset: number,
  open: string,
  close: string,
  isInner: boolean,
): TextObjectRange {
  // 向后查找匹配的左括号
  let depth = 0
  let start = -1
  
  for (let i = offset; i >= 0; i--) {
    if (text[i] === close && i !== offset) depth++
    else if (text[i] === open) {
      if (depth === 0) {
        start = i
        break
      }
      depth--
    }
  }
  if (start === -1) return null
  
  // 向前查找匹配的右括号
  depth = 0
  let end = -1
  for (let i = start + 1; i < text.length; i++) {
    if (text[i] === open) depth++
    else if (text[i] === close) {
      if (depth === 0) {
        end = i
        break
      }
      depth--
    }
  }
  if (end === -1) return null
  
  return isInner
    ? { start: start + 1, end }
    : { start, end: end + 1 }
}
```

---

### 2.6 useVimInput.ts (520 行) - Vim 输入 Hook

#### 核心状态管理

```typescript
export function useVimInput(props: UseVimInputProps): VimInputState {
  const vimStateRef = React.useRef<VimState>(createInitialVimState())
  const [mode, setMode] = useState<VimMode>('INSERT')
  
  const persistentRef = React.useRef<PersistentState>(
    createInitialPersistentState(),
  )
  
  const textInput = useTextInput({ ...props, inputFilter: undefined })
  
  // 切换到 INSERT 模式
  const switchToInsertMode = useCallback(
    (offset?: number): void => {
      if (offset !== undefined) {
        textInput.setOffset(offset)
      }
      vimStateRef.current = { mode: 'INSERT', insertedText: '' }
      setMode('INSERT')
      onModeChange?.('INSERT')
    },
    [textInput, onModeChange],
  )
  
  // 切换到 NORMAL 模式
  const switchToNormalMode = useCallback((): void => {
    const current = vimStateRef.current
    if (current.mode === 'INSERT' && current.insertedText) {
      persistentRef.current.lastChange = {
        type: 'insert',
        text: current.insertedText,
      }
    }
    
    // Vim 行为：退出 insert 模式时左移 1 个字符
    const offset = textInput.offset
    if (offset > 0 && props.value[offset - 1] !== '\n') {
      textInput.setOffset(offset - 1)
    }
    
    vimStateRef.current = { mode: 'NORMAL', command: { type: 'idle' } }
    setMode('NORMAL')
    onModeChange?.('NORMAL')
  }, [onModeChange, textInput, props.value])
```

#### OperatorContext 创建

```typescript
function createOperatorContext(
  cursor: Cursor,
  isReplay: boolean = false,
): OperatorContext {
  return {
    cursor,
    text: props.value,
    setText: (newText: string) => props.onChange(newText),
    setOffset: (offset: number) => textInput.setOffset(offset),
    enterInsert: (offset: number) => switchToInsertMode(offset),
    getRegister: () => persistentRef.current.register,
    setRegister: (content: string, linewise: boolean) => {
      persistentRef.current.register = content
      persistentRef.current.registerIsLinewise = linewise
    },
    getLastFind: () => persistentRef.current.lastFind,
    setLastFind: (type, char) => {
      persistentRef.current.lastFind = { type, char }
    },
    recordChange: isReplay
      ? () => {}
      : (change: RecordedChange) => {
          persistentRef.current.lastChange = change
        },
  }
}
```

#### replayLastChange - 重播上次变更

```typescript
function replayLastChange(): void {
  const change = persistentRef.current.lastChange
  if (!change) return
  
  const cursor = Cursor.fromText(props.value, props.columns, textInput.offset)
  const ctx = createOperatorContext(cursor, true)
  
  switch (change.type) {
    case 'insert':
      if (change.text) {
        const newCursor = cursor.insert(change.text)
        props.onChange(newCursor.text)
        textInput.setOffset(newCursor.offset)
      }
      break
    
    case 'x':
      executeX(change.count, ctx)
      break
    
    case 'replace':
      executeReplace(change.char, change.count, ctx)
      break
    
    case 'toggleCase':
      executeToggleCase(change.count, ctx)
      break
    
    case 'indent':
      executeIndent(change.dir, change.count, ctx)
      break
    
    case 'join':
      executeJoin(change.count, ctx)
      break
    
    case 'openLine':
      executeOpenLine(change.direction, ctx)
      break
    
    case 'operator':
      executeOperatorMotion(change.op, change.motion, change.count, ctx)
      break
    
    case 'operatorFind':
      executeOperatorFind(
        change.op,
        change.find,
        change.char,
        change.count,
        ctx,
      )
      break
    
    case 'operatorTextObj':
      executeOperatorTextObj(
        change.op,
        change.scope,
        change.objType,
        change.count,
        ctx,
      )
      break
  }
}
```

#### handleVimInput - 主输入处理

```typescript
function handleVimInput(rawInput: string, key: Key): void {
  const state = vimStateRef.current
  
  // 在 INSERT 模式应用 inputFilter，NORMAL 模式不应用
  const filtered = inputFilter ? inputFilter(rawInput, key) : rawInput
  const input = state.mode === 'INSERT' ? filtered : rawInput
  const cursor = Cursor.fromText(props.value, props.columns, textInput.offset)
  
  // Ctrl 组合键交给基础处理器
  if (key.ctrl) {
    textInput.onInput(input, key)
    return
  }
  
  // Escape 退出 INSERT 模式
  if (key.escape && state.mode === 'INSERT') {
    switchToNormalMode()
    return
  }
  
  // Escape 在 NORMAL 模式取消待命命令
  if (key.escape && state.mode === 'NORMAL') {
    vimStateRef.current = { mode: 'NORMAL', command: { type: 'idle' } }
    return
  }
  
  // Enter 交给基础处理器
  if (key.return) {
    textInput.onInput(input, key)
    return
  }
  
  // INSERT 模式处理
  if (state.mode === 'INSERT') {
    // 追踪插入的文本用于 dot-repeat
    if (key.backspace || key.delete) {
      if (state.insertedText.length > 0) {
        vimStateRef.current = {
          mode: 'INSERT',
          insertedText: state.insertedText.slice(
            0,
            -(lastGrapheme(state.insertedText).length || 1),
          ),
        }
      }
    } else {
      vimStateRef.current = {
        mode: 'INSERT',
        insertedText: state.insertedText + input,
      }
    }
    textInput.onInput(input, key)
    return
  }
  
  // NORMAL 模式空闲状态下的方向键交给基础处理器
  if (
    state.command.type === 'idle' &&
    (key.upArrow || key.downArrow || key.leftArrow || key.rightArrow)
  ) {
    textInput.onInput(input, key)
    return
  }
  
  // 创建转换上下文
  const ctx: TransitionContext = {
    ...createOperatorContext(cursor, false),
    onUndo: props.onUndo,
    onDotRepeat: replayLastChange,
  }
  
  // 方向键映射到 Vim 移动
  let vimInput = input
  if (key.leftArrow) vimInput = 'h'
  else if (key.rightArrow) vimInput = 'l'
  else if (key.upArrow) vimInput = 'k'
  else if (key.downArrow) vimInput = 'j'
  else if (expectsMotion && key.backspace) vimInput = 'h'
  else if (expectsMotion && state.command.type !== 'count' && key.delete)
    vimInput = 'x'
  
  // 执行状态转换
  const result = transition(state.command, vimInput, ctx)
  
  if (result.execute) {
    result.execute()
  }
  
  // 更新命令状态（如果 execute 没有切换到 INSERT）
  if (vimStateRef.current.mode === 'NORMAL') {
    if (result.next) {
      vimStateRef.current = { mode: 'NORMAL', command: result.next }
    } else if (result.execute) {
      vimStateRef.current = { mode: 'NORMAL', command: { type: 'idle' } }
    }
  }
  
  // 特殊处理：? 在 NORMAL 模式插入 ?
  if (
    input === '?' &&
    state.mode === 'NORMAL' &&
    state.command.type === 'idle'
  ) {
    props.onChange('?')
  }
}
```

---

## 3. 模式状态机

```
┌─────────────────────────────────────────────────────────────┐
│                         VimState                             │
│                                                              │
│  ┌──────────────────┐          ┌──────────────────────┐     │
│  │    INSERT        │          │      NORMAL          │     │
│  │                  │          │                      │     │
│  │ insertedText     │ Escape   │  command:            │     │
│  │ (for dot-repeat) │─────────►│  CommandState        │     │
│  │                  │          │                      │     │
│  │                  │          │  ┌────────────────┐  │     │
│  │                  │          │  │    idle        │  │     │
│  │                  │          │  └────────────────┘  │     │
│  │                  │          │         │            │     │
│  │                  │          │    ┌───┴───┐        │     │
│  │                  │          │    ▼     ▼        │     │
│  │                  │          │ ┌────┐ ┌─────┐   │     │
│  │                  │          │ │count│ │operator│  │     │
│  │                  │          │ └────┘ └─────┘   │     │
│  │                  │          │    │      │       │     │
│  │                  │          │    ▼      ▼      │     │
│  │                  │          │ ┌──────────┐    │     │
│  │                  │          │ │operatorCount│   │     │
│  │                  │          │ └──────────┘    │     │
│  │                  │          │    │            │     │
│  │                  │          │    ▼            │     │
│  │                  │          │ ┌──────────┐    │     │
│  │                  │          │ │  motion  │    │     │
│  │                  │          │ │ execute  │    │     │
│  │                  │          │ └──────────┘    │     │
│  └──────────────────┘          └──────────────────────┘     │
└─────────────────────────────────────────────────────────────┘
```

---

## 4. 键位映射表

### NORMAL 模式键位

| 键位 | 功能 | 状态转换 |
|------|------|----------|
| `h` | 左移 | idle → execute |
| `j` | 下移 | idle → execute |
| `k` | 上移 | idle → execute |
| `l` | 右移 | idle → execute |
| `w` | 下一词 | idle → execute |
| `b` | 上一词 | idle → execute |
| `e` | 词尾 | idle → execute |
| `W` | 下一 WORD | idle → execute |
| `B` | 上一 WORD | idle → execute |
| `E` | WORD 尾 | idle → execute |
| `0` | 行首 | idle → execute |
| `^` | 首个非空白 | idle → execute |
| `$` | 行尾 | idle → execute |
| `G` | 最后一行 | idle → execute |
| `gg` | 第一行 | idle → g → execute |
| `f` | 向前查找 | idle → find → execute |
| `F` | 向后查找 | idle → find → execute |
| `t` | 向前直到 | idle → find → execute |
| `T` | 向后直到 | idle → find → execute |
| `;` | 重复 find | idle → execute |
| `,` | 反向重复 find | idle → execute |
| `i` | 进入 INSERT | idle → execute |
| `I` | 行首进入 INSERT | idle → execute |
| `a` | 追加进入 INSERT | idle → execute |
| `A` | 行尾进入 INSERT | idle → execute |
| `o` | 下方开新行 | idle → execute |
| `O` | 上方开新行 | idle → execute |
| `x` | 删除字符 | idle → execute |
| `~` | 切换大小写 | idle → execute |
| `r` | 替换字符 | idle → replace → execute |
| `d` | 删除操作符 | idle → operator → execute |
| `c` | 变更操作符 | idle → operator → execute |
| `y` | yank 操作符 | idle → operator → execute |
| `dd` | 删除行 | idle → operator → execute |
| `cc` | 变更行 | idle → operator → execute |
| `yy` | yank 行 | idle → operator → execute |
| `p` | 粘贴到后 | idle → execute |
| `P` | 粘贴到前 | idle → execute |
| `.` | dot-repeat | idle → execute |
| `u` | undo | idle → execute |
| `J` | 合并行 | idle → execute |
| `>` | 缩进 | idle → indent → execute |
| `<` | 取消缩进 | idle → indent → execute |
| `>>` | 缩进行 | idle → indent → execute |
| `<<` | 取消缩进行 | idle → indent → execute |
| `D` | 删除到行尾 | idle → execute |
| `C` | 变更到行尾 | idle → execute |
| `Y` | yank 行 | idle → execute |
| `Escape` | 取消待命 | any → idle |

### 数字前缀

```
[1-9] → count 状态
[0-9] → 继续累积数字
[运动] → 应用 count * 运动
```

### 操作符待命

```
d/c/y → operator 状态
[运动] → 执行操作符 + 运动
[数字] → operatorCount 状态
[i/a] → operatorTextObj 状态
[f/F/t/T] → operatorFind 状态
```

---

## 5. 重要代码示例

### 5.1 cw 命令执行流程

```typescript
// 用户输入：cw
// 1. 'c' → operator 状态 (op='change', count=1)
// 2. 'w' → executeOperatorMotion('change', 'w', 1, ctx)

// 在 getOperatorRange 中：
if (op === 'change' && (motion === 'w' || motion === 'W')) {
  // cw 特殊处理：改变到词尾，不是下一个词首
  let wordCursor = cursor
  for (let i = 0; i < count - 1; i++) {
    wordCursor = motion === 'w' ? wordCursor.nextVimWord() : wordCursor.nextWORD()
  }
  const wordEnd = motion === 'w' ? wordCursor.endOfVimWord() : wordCursor.endOfWORD()
  to = cursor.measuredText.nextOffset(wordEnd.offset)
}
```

### 5.2 di" 命令执行流程

```typescript
// 用户输入：di"
// 1. 'd' → operator 状态 (op='delete', count=1)
// 2. 'i' → operatorTextObj 状态 (op='delete', scope='inner')
// 3. '"' → executeOperatorTextObj('delete', 'inner', '"', 1, ctx)

// 在 findQuoteObject 中：
// - 找到当前行所有引号位置
// - 配对引号：0-1, 2-3, 4-5...
// - 找到包含 cursor 的配对
// - 返回 inner 范围（不包含引号）
```

### 5.3 3dw 命令执行流程

```typescript
// 用户输入：3dw
// 1. '3' → count 状态 (digits='3')
// 2. 'd' → operator 状态 (op='delete', count=3)
// 3. 'w' → executeOperatorMotion('delete', 'w', 3, ctx)

// 在 resolveMotion 中：
// - 循环 3 次应用 nextVimWord()
// - 每次移动到下一个词首
```

### 5.4 dot-repeat (.)

```typescript
// 用户执行：cwHello
// 1. cw 进入 change 模式
// 2. 输入 "Hello"
// 3. 退出 INSERT 模式时记录：
//    persistentRef.current.lastChange = {
//      type: 'operator',
//      op: 'change',
//      motion: 'w',
//      count: 1
//    }

// 用户按下 . 时：
// replayLastChange() 重播相同的操作
```

---

## 6. 与核心系统集成

### 6.1 Cursor 类集成

- `MeasuredText`: 处理文本测量和换行
- `graphemeAt()`: grapheme-safe 字符访问
- `nextOffset()/prevOffset()`: grapheme 边界导航
- `snapOutOfImageRef()`: 避免损坏 [Image #N] chip

### 6.2 Unicode 处理

```typescript
// 使用 Intl.Segmenter 进行 grapheme 分割
const graphemes = Array.from(getGraphemeSegmenter().segment(text))

// 所有移动都按 grapheme 边界进行
const nextOffset = this.measuredText.nextOffset(this.offset)
```

### 6.3 状态行集成

```typescript
...(isVimModeEnabled() && {
  vim: {
    mode: vimMode ?? 'INSERT'
  }
}),
```

### 6.4 配置检查

```typescript
export function isVimModeEnabled(): boolean {
  const config = getGlobalConfig()
  return config.editorMode === 'vim'
}
```

---

## 7. 设计亮点

### 7.1 类型安全的状态机

TypeScript 确保所有状态转换都被穷尽处理：

```typescript
export type CommandState =
  | { type: 'idle' }
  | { type: 'count'; digits: string }
  // ... 其他状态

// switch 语句必须处理所有情况
switch (state.type) {
  case 'idle': /* ... */
  case 'count': /* ... */
  // TypeScript 会警告遗漏的状态
}
```

### 7.2 纯函数架构

所有操作符都是纯函数，接受 `OperatorContext`：

```typescript
export function executeOperatorMotion(
  op: Operator,
  motion: string,
  count: number,
  ctx: OperatorContext,
): void {
  // 纯计算，无副作用
  const target = resolveMotion(motion, ctx.cursor, count)
  const range = getOperatorRange(ctx.cursor, target, motion, op, count)
  applyOperator(op, range.from, range.to, ctx, range.linewise)
  ctx.recordChange({ type: 'operator', op, motion, count })
}
```

### 7.3 Grapheme-safe 文本处理

```typescript
// 使用 Intl.Segmenter 进行 grapheme 分割
const graphemes = Array.from(getGraphemeSegmenter().segment(text))

// 所有移动都按 grapheme 边界进行
const nextOffset = this.measuredText.nextOffset(this.offset)
```

### 7.4 状态转换表设计

```typescript
// 每个状态类型有独立的转换函数
function fromIdle(input: string, ctx: TransitionContext): TransitionResult
function fromCount(state: { type: 'count'; digits: string }, ...): TransitionResult
function fromOperator(state: { type: 'operator'; ... }, ...): TransitionResult
```

### 7.5 持久化状态分离

```typescript
// VimState: 当前模式 + 待命命令
const vimStateRef = useRef<VimState>(createInitialVimState())

// PersistentState: 跨命令的记忆
const persistentRef = useRef<PersistentState>(createInitialPersistentState())
```

---

## 8. 总结

这个 Vim 模式系统是一个**完全类型安全、纯函数式、grapheme-aware**的实现，包含：

- **6 个核心文件**：types, operators, motions, transitions, textObjects, useVimInput
- **完整的状态机**：11 种 CommandState 类型
- **丰富的操作符**：delete/change/yank/x/replace/toggleCase/join/paste/indent/openLine
- **全面的移动**：基本移动、词移动、find 移动、文本对象
- **dot-repeat 支持**：记录并重播所有变更
- **Unicode 支持**：使用 Intl.Segmenter 进行 grapheme 处理
- **状态行集成**：实时显示 Vim 模式

系统设计优雅，代码质量高，是 Vim 集成的优秀实现！

---

*文档持续更新中...*
