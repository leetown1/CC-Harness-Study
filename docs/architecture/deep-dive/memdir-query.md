# Memdir & Query 系统深度技术文档

> 基于逐行代码分析的完整技术文档  
> **探索完成时间**: 2026 年 4 月 1 日  
> **核心文件**: memdir/ (8 文件，1,744 行), query/ (4 文件，656 行)

---

## 一、系统架构总览

### 1.1 Memory 系统架构

```
┌─────────────────────────────────────────────────────────────┐
│                    Memory System Architecture                │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐  │
│  │  memdir.ts   │    │  memoryTypes │    │ memoryScan.ts│  │
│  │  (核心入口)  │    │  (类型定义)  │    │ (文件扫描)   │  │
│  │  (508 行)     │    │  (272 行)     │    │  (95 行)      │  │
│  └──────┬───────┘    └──────┬───────┘    └──────┬───────┘  │
│         │                   │                    │          │
│         └───────────────────┼────────────────────┘          │
│                             │                               │
│                    ┌────────▼────────┐                      │
│                    │findRelevant    │                      │
│                    │Memories.ts      │                      │
│                    │(相关性发现)     │                      │
│                    │(142 行)          │                      │
│                    └────────┬────────┘                      │
│                             │                               │
│         ┌───────────────────┼───────────────────┐          │
│         │                   │                   │          │
│  ┌──────▼───────┐   ┌──────▼───────┐   ┌──────▼───────┐  │
│  │  paths.ts    │   │teamMemPaths  │   │teamMemPrompts│  │
│  │ (路径管理)   │   │  (团队路径)  │   │ (团队提示)   │  │
│  │ (279 行)      │   │  (293 行)     │   │  (101 行)     │  │
│  └──────────────┘   └──────────────┘   └──────────────┘  │
│                                                              │
│  ┌──────────────┐    ┌──────────────┐                       │
│  │ memoryAge.ts │    │memoryShape   │                       │
│  │ (新鲜度)     │    │Telemetry.ts  │                       │
│  │ (54 行)       │    │ (遥测)       │                       │
│  └──────────────┘    └──────────────┘                       │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

### 1.2 Query 系统架构

```
┌─────────────────────────────────────────────────────────────┐
│                    Query System Architecture                 │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐  │
│  │  config.ts   │    │   deps.ts    │    │tokenBudget.ts│  │
│  │ (查询配置)   │    │ (依赖注入)   │    │ (Token 预算)  │  │
│  │  (47 行)      │    │  (41 行)      │    │  (94 行)      │  │
│  └──────────────┘    └──────────────┘    └──────┬───────┘  │
│                                                  │          │
│                                         ┌────────▼────────┐│
│                                         │  stopHooks.ts   ││
│                                         │  (停止钩子)     ││
│                                         │  (474 行)        ││
│                                         └─────────────────┘│
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

---

## 二、Memory 系统详解

### 2.1 memdir.ts - Memory 核心入口文件

**文件位置**: `f:\Claude\src\memdir\memdir.ts` (508 行)

**核心常量**:

```typescript
export const ENTRYPOINT_NAME = 'MEMORY.md'
export const MAX_ENTRYPOINT_LINES = 200
export const MAX_ENTRYPOINT_BYTES = 25_000
const AUTO_MEM_DISPLAY_NAME = 'auto memory'
```

**关键类型**:

```typescript
export type EntrypointTruncation = {
  content: string
  lineCount: number
  byteCount: number
  wasLineTruncated: boolean
  wasByteTruncated: boolean
}
```

#### 2.1.1 truncateEntrypointContent (57-103 行)

**功能**: 对 MEMORY.md 内容进行双重截断（行数 + 字节数）

**算法逻辑**:
1. 首先按行数截断（200 行限制）
2. 然后按字节数截断（25KB 限制），在最后一个换行符处切断
3. 返回截断信息和警告标记

**设计意图**: 
- 行数限制防止长文件拖慢加载
- 字节限制防止长行索引（观察到的 p100: 200 行下 197KB）
- 双重保障确保 prompt 大小可控

#### 2.1.2 buildMemoryLines (199-266 行)

**功能**: 构建 Memory 行为指令（不包含 MEMORY.md 内容）

**四种 Memory 类型**:
- **user**: 用户角色、偏好、知识
- **feedback**: 用户反馈（纠正和确认）
- **project**: 项目上下文（截止日期、事件、决策）
- **reference**: 外部系统引用（Linear、Grafana 等）

**保存流程**（skipIndex = false 时）:
```
Step 1: 将 Memory 写入独立文件（带 frontmatter）
Step 2: 在 MEMORY.md 中添加索引条目
```

**索引格式**:
```markdown
- [Title](file.md) — one-line hook
```

#### 2.1.3 buildMemoryPrompt (272-316 行)

**功能**: 构建包含 MEMORY.md 内容的完整 Memory prompt

**流程**:
1. 读取 MEMORY.md 入口文件
2. 调用 truncateEntrypointContent 进行截断
3. 记录遥测数据（行数、字节数、截断状态）
4. 追加截断后的内容到 prompt

#### 2.1.4 loadMemoryPrompt (419-507 行)

**功能**: 统一 Memory prompt 加载入口

**分发逻辑**:
```typescript
if (KAIROS 特性 && autoEnabled && getKairosActive()) {
  // 每日日志模式（append-only）
  return buildAssistantDailyLogPrompt()
}

if (TEAMMEM 特性 && teamMemPaths.isTeamMemoryEnabled()) {
  // 团队 + 个人组合模式
  return buildCombinedMemoryPrompt()
}

if (autoEnabled) {
  // 仅个人模式
  return buildMemoryLines()
}

return null // Memory 被禁用
```

**KAIROS 每日日志模式**:
- 日志路径：`<memoryDir>/logs/YYYY/MM/YYYY-MM-DD.md`
- Append-only 设计，不维护实时索引
- 夜间通过 `/dream` skill 提炼为 topic files + MEMORY.md

---

### 2.2 memoryTypes.ts - Memory 类型定义

**文件位置**: `f:\Claude\src\memdir\memoryTypes.ts` (272 行)

**类型系统**:

```typescript
export const MEMORY_TYPES = [
  'user',
  'feedback', 
  'project',
  'reference',
] as const

export type MemoryType = (typeof MEMORY_TYPES)[number]
```

**核心解析函数**:

```typescript
export function parseMemoryType(raw: unknown): MemoryType | undefined {
  if (typeof raw !== 'string') return undefined
  return MEMORY_TYPES.find(t => t === raw)
}
```

#### 2.2.1 两种模式的类型定义

**TYPES_SECTION_COMBINED** (37-106 行)

用于**团队 + 个人**组合模式，包含 `<scope>` 标签：

```xml
<type>
    <name>user</name>
    <scope>always private</scope>
    <description>...</description>
    <when_to_save>...</when_to_save>
    <how_to_use>...</how_to_use>
    <examples>...</examples>
</type>
```

**各类型 scope 规则**:
- **user**: always private
- **feedback**: default to private（项目级惯例用 team）
- **project**: private or team（强烈偏向 team）
- **reference**: usually team

**TYPES_SECTION_INDIVIDUAL** (113-178 行)

用于**仅个人**模式，无 `<scope>` 标签

#### 2.2.2 关键约束定义

**WHAT_NOT_TO_SAVE_SECTION** (183-195 行):
```typescript
export const WHAT_NOT_TO_SAVE_SECTION: readonly string[] = [
  '## What NOT to save in memory',
  '',
  '- Code patterns, conventions, architecture... (可从代码推导)',
  '- Git history, recent changes... (git log/blame 更权威)',
  '- Debugging solutions... (修复在代码中)',
  '- 已在 CLAUDE.md 中记录的内容',
  '- 临时任务详情',
]
```

**MEMORY_DRIFT_CAVEAT** (201-202 行):
```typescript
export const MEMORY_DRIFT_CAVEAT =
  '- Memory records can become stale over time. Use memory as context for what was true at a given point in time. Before answering the user or building assumptions based solely on information in memory records, verify that the memory is still correct and up-to-date by reading the current state of the files or resources. If a recalled memory conflicts with current information, trust what you observe now — and update or remove the stale memory rather than acting on it.'
```

**TRUSTING_RECALL_SECTION** (240-256 行):
```typescript
export const TRUSTING_RECALL_SECTION: readonly string[] = [
  '## Before recommending from memory',
  '',
  'A memory that names a specific function, file, or flag is a claim that it existed *when the memory was written*. It may have been renamed, removed, or never merged. Before recommending it:',
  '',
  '- If the memory names a file path: check the file exists.',
  '- If the memory names a function or flag: grep for it.',
  '- If the user is about to act on your recommendation (not just asking about history), verify first.',
  '',
  '"The memory says X exists" is not the same as "X exists now."',
]
```

#### 2.2.3 Frontmatter 格式

```typescript
export const MEMORY_FRONTMATTER_EXAMPLE: readonly string[] = [
  '```markdown',
  '---',
  'name: {{memory name}}',
  'description: {{one-line description — used to decide relevance in future conversations, so be specific}}',
  `type: {{${MEMORY_TYPES.join(', ')}}}`,
  '---',
  '',
  '{{memory content — for feedback/project types, structure as: rule/fact, then **Why:** and **How to apply:** lines}}',
  '```',
]
```

---

### 2.3 memoryScan.ts - Memory 文件扫描

**文件位置**: `f:\Claude\src\memdir\memoryScan.ts` (95 行)

**核心类型**:

```typescript
export type MemoryHeader = {
  filename: string
  filePath: string
  mtimeMs: number
  description: string | null
  type: MemoryType | undefined
}
```

**常量定义**:
```typescript
const MAX_MEMORY_FILES = 200
const FRONTMATTER_MAX_LINES = 30
```

#### 2.3.1 scanMemoryFiles (35-77 行)

**功能**: 扫描 Memory 目录，读取 frontmatter，返回按时间排序的头部列表

**单次遍历算法**（优化 I/O）:

```typescript
export async function scanMemoryFiles(
  memoryDir: string,
  signal: AbortSignal,
): Promise<MemoryHeader[]> {
  try {
    const entries = await readdir(memoryDir, { recursive: true })
    const mdFiles = entries.filter(
      f => f.endsWith('.md') && basename(f) !== 'MEMORY.md',
    )

    const headerResults = await Promise.allSettled(
      mdFiles.map(async (relativePath): Promise<MemoryHeader> => {
        const filePath = join(memoryDir, relativePath)
        const { content, mtimeMs } = await readFileInRange(
          filePath,
          0,
          FRONTMATTER_MAX_LINES,
          undefined,
          signal,
        )
        const { frontmatter } = parseFrontmatter(content, filePath)
        return {
          filename: relativePath,
          filePath,
          mtimeMs,
          description: frontmatter.description || null,
          type: parseMemoryType(frontmatter.type),
        }
      }),
    )

    return headerResults
      .filter(
        (r): r is PromiseFulfilledResult<MemoryHeader> =>
          r.status === 'fulfilled',
      )
      .map(r => r.value)
      .sort((a, b) => b.mtimeMs - a.mtimeMs)  // 最新优先
      .slice(0, MAX_MEMORY_FILES)  // 限制 200 个文件
  } catch {
    return []
  }
}
```

**性能优化**:
- 单次读取：`readFileInRange` 内部 stat 获取 mtime，避免二次 stat
- 并行处理：`Promise.allSettled` 处理所有文件
- 错误容忍：失败的读取被过滤，不影响其他文件
- 时间排序：最新修改的文件优先（capped at 200）

#### 2.3.2 formatMemoryManifest (84-94 行)

**功能**: 格式化 Memory 头部为文本清单

**输出格式**:
```
- [type] filename (timestamp): description
- [type] filename (timestamp)  // 无 description 时
```

```typescript
export function formatMemoryManifest(memories: MemoryHeader[]): string {
  return memories
    .map(m => {
      const tag = m.type ? `[${m.type}] ` : ''
      const ts = new Date(m.mtimeMs).toISOString()
      return m.description
        ? `- ${tag}${m.filename} (${ts}): ${m.description}`
        : `- ${tag}${m.filename} (${ts})`
    })
    .join('\n')
}
```

---

### 2.4 findRelevantMemories.ts - Memory 相关性发现

**文件位置**: `f:\Claude\src\memdir\findRelevantMemories.ts` (142 行)

**核心类型**:

```typescript
export type RelevantMemory = {
  path: string
  mtimeMs: number
}
```

**系统 Prompt**:

```typescript
const SELECT_MEMORIES_SYSTEM_PROMPT = `You are selecting memories that will be useful to Claude Code as it processes a user's query. You will be given the user's query and a list of available memory files with their filenames and descriptions.

Return a list of filenames for the memories that clearly be useful to Claude Code as it processes the user's query (up to 5). Only include memories that you are certain will be helpful based on their name and description.
- If you are unsure if a memory will be useful in processing the user's query, then do not include it in your list. Be selective and discerning.
- If there are no memories in the list that would clearly be useful, feel free to return an empty list.
- If a list of recently-used tools is provided, do not select memories that are usage reference or API documentation for those tools (Claude Code is already exercising them). DO still select memories containing warnings, gotchas, or known issues about those tools — active use is exactly when those matter.
`
```

#### 2.4.1 findRelevantMemories (39-75 行)

**功能**: 通过扫描 Memory 文件并调用 Sonnet 选择最相关的 Memory

**算法流程**:

```typescript
export async function findRelevantMemories(
  query: string,
  memoryDir: string,
  signal: AbortSignal,
  recentTools: readonly string[] = [],
  alreadySurfaced: ReadonlySet<string> = new Set(),
): Promise<RelevantMemory[]> {
  // Step 1: 扫描 Memory 文件，过滤已展示过的
  const memories = (await scanMemoryFiles(memoryDir, signal)).filter(
    m => !alreadySurfaced.has(m.filePath),
  )
  if (memories.length === 0) {
    return []
  }

  // Step 2: 调用 Sonnet 选择相关 Memory
  const selectedFilenames = await selectRelevantMemories(
    query,
    memories,
    signal,
    recentTools,
  )
  
  // Step 3: 构建结果
  const byFilename = new Map(memories.map(m => [m.filename, m]))
  const selected = selectedFilenames
    .map(filename => byFilename.get(filename))
    .filter((m): m is MemoryHeader => m !== undefined)

  // Step 4: 记录遥测（如果启用）
  if (feature('MEMORY_SHAPE_TELEMETRY')) {
    const { logMemoryRecallShape } =
      require('./memoryShapeTelemetry.js') as typeof import('./memoryShapeTelemetry.js')
    logMemoryRecallShape(memories, selected)
  }

  // Step 5: 返回路径 + mtime
  return selected.map(m => ({ path: m.filePath, mtimeMs: m.mtimeMs }))
}
```

**关键设计**:
- `alreadySurfaced` 过滤：避免重复展示同一 Memory
- 5 个名额预算：Sonnet 最多选 5 个
- 工具过滤：不选择正在使用工具的参考文档（但保留警告/问题）

#### 2.4.2 selectRelevantMemories (77-141 行)

**功能**: 调用 Sonnet 模型选择相关 Memory

**实现细节**:

```typescript
async function selectRelevantMemories(
  query: string,
  memories: MemoryHeader[],
  signal: AbortSignal,
  recentTools: readonly string[],
): Promise<string[]> {
  const validFilenames = new Set(memories.map(m => m.filename))
  const manifest = formatMemoryManifest(memories)

  // 添加最近使用的工具信息（用于过滤）
  const toolsSection =
    recentTools.length > 0
      ? `\n\nRecently used tools: ${recentTools.join(', ')}`
      : ''

  try {
    const result = await sideQuery({
      model: getDefaultSonnetModel(),
      system: SELECT_MEMORIES_SYSTEM_PROMPT,
      skipSystemPromptPrefix: true,
      messages: [
        {
          role: 'user',
          content: `Query: ${query}\n\nAvailable memories:\n${manifest}${toolsSection}`,
        },
      ],
      max_tokens: 256,
      output_format: {
        type: 'json_schema',
        schema: {
          type: 'object',
          properties: {
            selected_memories: { type: 'array', items: { type: 'string' } },
          },
          required: ['selected_memories'],
          additionalProperties: false,
        },
      },
      signal,
      querySource: 'memdir_relevance',
    })

    const textBlock = result.content.find(block => block.type === 'text')
    if (!textBlock || textBlock.type !== 'text') {
      return []
    }

    const parsed: { selected_memories: string[] } = jsonParse(textBlock.text)
    return parsed.selected_memories.filter(f => validFilenames.has(f))
  } catch (e) {
    if (signal.aborted) {
      return []
    }
    logForDebugging(
      `[memdir] selectRelevantMemories failed: ${errorMessage(e)}`,
      { level: 'warn' },
    )
    return []
  }
}
```

**错误处理**:
- 解析失败：返回空数组
- Signal 中止：立即返回空数组
- 其他错误：记录警告日志，返回空数组

---

### 2.5 paths.ts - Memory 路径管理

**文件位置**: `f:\Claude\src\memdir\paths.ts` (279 行)

**核心功能**:
1. Auto Memory 启用状态检测
2. Memory 路径解析和验证
3. 安全路径检查

#### 2.5.1 isAutoMemoryEnabled (30-55 行)

**启用优先级链**（首个定义获胜）:

```typescript
export function isAutoMemoryEnabled(): boolean {
  const envVal = process.env.CLAUDE_CODE_DISABLE_AUTO_MEMORY
  if (isEnvTruthy(envVal)) {
    return false
  }
  if (isEnvDefinedFalsy(envVal)) {
    return true
  }
  // --bare / SIMPLE 模式：禁用
  if (isEnvTruthy(process.env.CLAUDE_CODE_SIMPLE)) {
    return false
  }
  // CCR 无持久化存储：禁用
  if (
    isEnvTruthy(process.env.CLAUDE_CODE_REMOTE) &&
    !process.env.CLAUDE_CODE_REMOTE_MEMORY_DIR
  ) {
    return false
  }
  // settings.json 配置
  const settings = getInitialSettings()
  if (settings.autoMemoryEnabled !== undefined) {
    return settings.autoMemoryEnabled
  }
  // 默认：启用
  return true
}
```

#### 2.5.2 validateMemoryPath (109-150 行)

**安全路径验证**（防御路径遍历攻击）:

```typescript
function validateMemoryPath(
  raw: string | undefined,
  expandTilde: boolean,
): string | undefined {
  if (!raw) {
    return undefined
  }
  let candidate = raw
  
  // ~/ 展开（仅设置路径支持）
  if (
    expandTilde &&
    (candidate.startsWith('~/') || candidate.startsWith('~\\'))
  ) {
    const rest = candidate.slice(2)
    const restNorm = normalize(rest || '.')
    if (restNorm === '.' || restNorm === '..') {
      return undefined  // 拒绝 trivial 路径
    }
    candidate = join(homedir(), rest)
  }
  
  // 标准化并添加 trailing separator
  const normalized = normalize(candidate).replace(/[/\\]+$/, '')
  
  // 安全检查
  if (
    !isAbsolute(normalized) ||           // 必须是绝对路径
    normalized.length < 3 ||              // 根路径太短
    /^[A-Za-z]:$/.test(normalized) ||     // Windows 盘符根
    normalized.startsWith('\\\\') ||       // UNC 路径
    normalized.startsWith('//') ||         // 另一种 UNC
    normalized.includes('\0')             // null 字节
  ) {
    return undefined
  }
  
  return (normalized + sep).normalize('NFC')
}
```

**拒绝的攻击向量**:
- 相对路径（`../foo`）
- 根/近根路径（`/`, `/a`）
- Windows 盘符根（`C:\` → `C:`）
- UNC 路径（`\\server\share`）
- null 字节注入

#### 2.5.3 getAutoMemPath (223-235 行)

**Memory 目录解析**（带缓存）:

```typescript
export const getAutoMemPath = memoize(
  (): string => {
    const override = getAutoMemPathOverride() ?? getAutoMemPathSetting()
    if (override) {
      return override
    }
    const projectsDir = join(getMemoryBaseDir(), 'projects')
    return (
      join(projectsDir, sanitizePath(getAutoMemBase()), AUTO_MEM_DIRNAME) + sep
    ).normalize('NFC')
  },
  () => getProjectRoot(),
)
```

**解析顺序**:
1. `CLAUDE_COWORK_MEMORY_PATH_OVERRIDE` 环境变量
2. `settings.json` 中的 `autoMemoryDirectory`（仅信任源：policy/local/user）
3. 默认：`<memoryBase>/projects/<sanitized-git-root>/memory/`

**Memoization**: 基于 `getProjectRoot()` 缓存，避免重复读取 settings.json

#### 2.5.4 isAutoMemPath (274-278 行)

**安全检查**: 判断路径是否在 Auto Memory 目录内

```typescript
export function isAutoMemPath(absolutePath: string): boolean {
  const normalizedPath = normalize(absolutePath)
  return normalizedPath.startsWith(getAutoMemPath())
}
```

---

### 2.6 memoryAge.ts - Memory 新鲜度计算

**文件位置**: `f:\Claude\src\memdir\memoryAge.ts` (54 行)

**核心函数**:

#### 2.6.1 memoryAgeDays (6-8 行)

```typescript
export function memoryAgeDays(mtimeMs: number): number {
  return Math.max(0, Math.floor((Date.now() - mtimeMs) / 86_400_000))
}
```

**计算逻辑**:
- 向下取整：今天=0，昨天=1，前天=2
- 负数钳制到 0（未来时间/时钟偏移）

#### 2.6.2 memoryAge (15-20 行)

```typescript
export function memoryAge(mtimeMs: number): string {
  const d = memoryAgeDays(mtimeMs)
  if (d === 0) return 'today'
  if (d === 1) return 'yesterday'
  return `${d} days ago`
}
```

**设计意图**: 模型不擅长日期计算，"47 days ago" 比 ISO 时间戳更能触发陈旧性推理

#### 2.6.3 memoryFreshnessText (33-42 行)

**陈旧性警告**（>1 天的 Memory）:

```typescript
export function memoryFreshnessText(mtimeMs: number): string {
  const d = memoryAgeDays(mtimeMs)
  if (d <= 1) return ''
  return (
    `This memory is ${d} days old. ` +
    `Memories are point-in-time observations, not live state — ` +
    `claims about code behavior or file:line citations may be outdated. ` +
    `Verify against current code before asserting as fact.`
  )
}
```

**动机**: 用户报告过时代码状态 Memory（file:line 引用）被当作事实断言的问题

#### 2.6.4 memoryFreshnessNote (49-53 行)

```typescript
export function memoryFreshnessNote(mtimeMs: number): string {
  const text = memoryFreshnessText(mtimeMs)
  if (!text) return ''
  return `<system-reminder>${text}</system-reminder>\n`
}
```

---

## 三、Query 系统详解

### 3.1 config.ts - 查询配置

**文件位置**: `f:\Claude\src\query\config.ts` (47 行)

**配置类型**:

```typescript
export type QueryConfig = {
  sessionId: SessionId

  // 运行时 gates（env/statsig）
  gates: {
    streamingToolExecution: boolean
    emitToolUseSummaries: boolean
    isAnt: boolean
    fastModeEnabled: boolean
  }
}
```

**构建函数**:

```typescript
export function buildQueryConfig(): QueryConfig {
  return {
    sessionId: getSessionId(),
    gates: {
      streamingToolExecution: checkStatsigFeatureGate_CACHED_MAY_BE_STALE(
        'tengu_streaming_tool_execution2',
      ),
      emitToolUseSummaries: isEnvTruthy(
        process.env.CLAUDE_CODE_EMIT_TOOL_USE_SUMMARIES,
      ),
      isAnt: process.env.USER_TYPE === 'ant',
      fastModeEnabled: !isEnvTruthy(
        process.env.CLAUDE_CODE_DISABLE_FAST_MODE),
    },
  }
}
```

**设计原则**:
- 不可变配置：在 `query()` 入口快照一次
- 与 per-iteration State 分离：便于未来 `step()` 提取
- 排除 `feature()` gates：保持 tree-shaking 边界

---

### 3.2 deps.ts - 依赖注入

**文件位置**: `f:\Claude\src\query\deps.ts` (41 行)

**依赖类型**:

```typescript
export type QueryDeps = {
  // -- model
  callModel: typeof queryModelWithStreaming

  // -- compaction
  microcompact: typeof microcompactMessages
  autocompact: typeof autoCompactIfNeeded

  // -- platform
  uuid: () => string
}
```

**生产依赖工厂**:

```typescript
export function productionDeps(): QueryDeps {
  return {
    callModel: queryModelWithStreaming,
    microcompact: microcompactMessages,
    autocompact: autoCompactIfNeeded,
    uuid: randomUUID,
  }
}
```

**设计意图**:
- 测试可注入 fake：避免 spyOn-per-module 样板代码
- 窄范围（4 deps）：证明模式可行性
- `typeof fn` 保持签名自动同步

---

### 3.3 tokenBudget.ts - Token 预算机制

**文件位置**: `f:\Claude\src\query\tokenBudget.ts` (94 行)

**常量定义**:
```typescript
const COMPLETION_THRESHOLD = 0.9
const DIMINISHING_THRESHOLD = 500
```

**预算跟踪器类型**:

```typescript
export type BudgetTracker = {
  continuationCount: number
  lastDeltaTokens: number
  lastGlobalTurnTokens: number
  startedAt: number
}
```

**创建函数**:

```typescript
export function createBudgetTracker(): BudgetTracker {
  return {
    continuationCount: 0,
    lastDeltaTokens: 0,
    lastGlobalTurnTokens: 0,
    startedAt: Date.now(),
  }
}
```

#### 3.3.1 checkTokenBudget (45-93 行)

**功能**: 检查 Token 预算，决定是否继续

**决策逻辑**:

```typescript
export function checkTokenBudget(
  tracker: BudgetTracker,
  agentId: string | undefined,
  budget: number | null,
  globalTurnTokens: number,
): TokenBudgetDecision {
  // Agent 模式或无预算：立即停止
  if (agentId || budget === null || budget <= 0) {
    return { action: 'stop', completionEvent: null }
  }

  const turnTokens = globalTurnTokens
  const pct = Math.round((turnTokens / budget) * 100)
  const deltaSinceLastCheck = globalTurnTokens - tracker.lastGlobalTurnTokens

  // 收益递减检测
  const isDiminishing =
    tracker.continuationCount >= 3 &&
    deltaSinceLastCheck < DIMINISHING_THRESHOLD &&
    tracker.lastDeltaTokens < DIMINISHING_THRESHOLD

  // 未达阈值且非收益递减：继续
  if (!isDiminishing && turnTokens < budget * COMPLETION_THRESHOLD) {
    tracker.continuationCount++
    tracker.lastDeltaTokens = deltaSinceLastCheck
    tracker.lastGlobalTurnTokens = globalTurnTokens
    return {
      action: 'continue',
      nudgeMessage: getBudgetContinuationMessage(pct, turnTokens, budget),
      continuationCount: tracker.continuationCount,
      pct,
      turnTokens,
      budget,
    }
  }

  // 已继续过或收益递减：停止
  if (isDiminishing || tracker.continuationCount > 0) {
    return {
      action: 'stop',
      completionEvent: {
        continuationCount: tracker.continuationCount,
        pct,
        turnTokens,
        budget,
        diminishingReturns: isDiminishing,
        durationMs: Date.now() - tracker.startedAt,
      },
    }
  }

  return { action: 'stop', completionEvent: null }
}
```

**决策类型**:

```typescript
type ContinueDecision = {
  action: 'continue'
  nudgeMessage: string
  continuationCount: number
  pct: number
  turnTokens: number
  budget: number
}

type StopDecision = {
  action: 'stop'
  completionEvent: {
    continuationCount: number
    pct: number
    turnTokens: number
    budget: number
    diminishingReturns: boolean
    durationMs: number
  } | null
}
```

**关键机制**:
1. **90% 阈值**: 达到预算 90% 前可继续
2. **收益递减检测**: 连续 3 次继续且增量 < 500 tokens 时停止
3. **Agent 模式**: 子 Agent 不使用 Token 预算

---

### 3.4 stopHooks.ts - 停止钩子机制

**文件位置**: `f:\Claude\src\query\stopHooks.ts` (474 行)

**核心类型**:

```typescript
type StopHookResult = {
  blockingErrors: Message[]
  preventContinuation: boolean
}
```

#### 3.4.1 handleStopHooks (65-473 行)

**功能**: 在查询结束时执行停止钩子

**钩子执行流程**:

```typescript
export async function* handleStopHooks(
  messagesForQuery: Message[],
  assistantMessages: AssistantMessage[],
  systemPrompt: SystemPrompt,
  userContext: { [k: string]: string },
  systemContext: { [k: string]: string },
  toolUseContext: ToolUseContext,
  querySource: QuerySource,
  stopHookActive?: boolean,
): AsyncGenerator<...> {
  const hookStartTime = Date.now()

  // Step 1: 构建钩子上下文
  const stopHookContext: REPLHookContext = {
    messages: [...messagesForQuery, ...assistantMessages],
    systemPrompt,
    userContext,
    systemContext,
    toolUseContext,
    querySource,
  }
  
  // Step 2: 保存缓存安全参数（仅主会话）
  if (querySource === 'repl_main_thread' || querySource === 'sdk') {
    saveCacheSafeParams(createCacheSafeParams(stopHookContext))
  }

  // Step 3: 模板作业分类（TEMPLATES 特性）
  if (
    feature('TEMPLATES') &&
    process.env.CLAUDE_JOB_DIR &&
    querySource.startsWith('repl_main_thread') &&
    !toolUseContext.agentId
  ) {
    const turnAssistantMessages = stopHookContext.messages.filter(
      (m): m is AssistantMessage => m.type === 'assistant',
    )
    await jobClassifierModule!.classifyAndWriteState(
      process.env.CLAUDE_JOB_DIR,
      turnAssistantMessages,
    )
  }

  // Step 4: 后台任务（非 bare 模式）
  if (!isBareMode()) {
    // 4.1 提示建议
    if (!isEnvDefinedFalsy(process.env.CLAUDE_CODE_ENABLE_PROMPT_SUGGESTION)) {
      void executePromptSuggestion(stopHookContext)
    }
    // 4.2 Memory 提取
    if (
      feature('EXTRACT_MEMORIES') &&
      !toolUseContext.agentId &&
      isExtractModeActive()
    ) {
      void extractMemoriesModule!.executeExtractMemories(
        stopHookContext,
        toolUseContext.appendSystemMessage,
      )
    }
    // 4.3 Auto Dream
    if (!toolUseContext.agentId) {
      void executeAutoDream(stopHookContext, toolUseContext.appendSystemMessage)
    }
  }

  // Step 5: Computer Use 清理（CHICAGO_MCP 特性）
  if (feature('CHICAGO_MCP') && !toolUseContext.agentId) {
    await cleanupComputerUseAfterTurn(toolUseContext)
  }

  // Step 6: 执行 Stop 钩子
  try {
    const blockingErrors = []
    const appState = toolUseContext.getAppState()
    const permissionMode = appState.toolPermissionContext.mode

    const generator = executeStopHooks(
      permissionMode,
      toolUseContext.abortController.signal,
      undefined,
      stopHookActive ?? false,
      toolUseContext.agentId,
      toolUseContext,
      [...messagesForQuery, ...assistantMessages],
      toolUseContext.agentType,
    )

    // 消费所有进度消息
    let stopHookToolUseID = ''
    let hookCount = 0
    let preventedContinuation = false
    let stopReason = ''
    let hasOutput = false
    const hookErrors: string[] = []
    const hookInfos: StopHookInfo[] = []

    for await (const result of generator) {
      if (result.message) {
        yield result.message
        // 跟踪钩子信息
        if (result.message.type === 'progress' && result.message.toolUseID) {
          stopHookToolUseID = result.message.toolUseID
          hookCount++
          const progressData = result.message.data as HookProgress
          if (progressData.command) {
            hookInfos.push({
              command: progressData.command,
              promptText: progressData.promptText,
            })
          }
        }
        // 跟踪错误和输出
        if (result.message.type === 'attachment') {
          const attachment = result.message.attachment
          if (
            'hookEvent' in attachment &&
            (attachment.hookEvent === 'Stop' ||
              attachment.hookEvent === 'SubagentStop')
          ) {
            if (attachment.type === 'hook_non_blocking_error') {
              hookErrors.push(
                attachment.stderr || `Exit code ${attachment.exitCode}`,
              )
              hasOutput = true
            } else if (attachment.type === 'hook_error_during_execution') {
              hookErrors.push(attachment.content)
              hasOutput = true
            } else if (attachment.type === 'hook_success') {
              if (
                (attachment.stdout && attachment.stdout.trim()) ||
                (attachment.stderr && attachment.stderr.trim())
              ) {
                hasOutput = true
              }
            }
            // 提取每钩子持续时间
            if ('durationMs' in attachment && 'command' in attachment) {
              const info = hookInfos.find(
                i =>
                  i.command === attachment.command &&
                  i.durationMs === undefined,
              )
              if (info) {
                info.durationMs = attachment.durationMs
              }
            }
          }
        }
      }
      if (result.blockingError) {
        const userMessage = createUserMessage({
          content: getStopHookMessage(result.blockingError),
          isMeta: true,
        })
        blockingErrors.push(userMessage)
        yield userMessage
        hasOutput = true
        hookErrors.push(result.blockingError.blockingError)
      }
      if (result.preventContinuation) {
        preventedContinuation = true
        stopReason = result.stopReason || 'Stop hook prevented continuation'
        yield createAttachmentMessage({
          type: 'hook_stopped_continuation',
          message: stopReason,
          hookName: 'Stop',
          toolUseID: stopHookToolUseID,
          hookEvent: 'Stop',
        })
      }
      if (toolUseContext.abortController.signal.aborted) {
        return { blockingErrors: [], preventContinuation: true }
      }
    }

    // 创建钩子摘要消息
    if (hookCount > 0) {
      yield createStopHookSummaryMessage(
        hookCount,
        hookInfos,
        hookErrors,
        preventedContinuation,
        stopReason,
        hasOutput,
        'suggestion',
        stopHookToolUseID,
      )

      // 错误通知
      if (hookErrors.length > 0) {
        toolUseContext.addNotification?.({
          key: 'stop-hook-error',
          text: `Stop hook error occurred · ${expandShortcut} to see`,
          priority: 'immediate',
        })
      }
    }

    if (preventedContinuation) {
      return { blockingErrors: [], preventContinuation: true }
    }

    if (blockingErrors.length > 0) {
      return { blockingErrors, preventContinuation: false }
    }

    // Step 7: Teammate 钩子（如果是 teammate）
    if (isTeammate()) {
      // 7.1 TaskCompleted 钩子
      const tasks = await listTasks(getTaskListId())
      const inProgressTasks = tasks.filter(
        t => t.status === 'in_progress' && t.owner === teammateName,
      )

      for (const task of inProgressTasks) {
        // 执行 TaskCompleted 钩子...
      }

      // 7.2 TeammateIdle 钩子
      // 执行 TeammateIdle 钩子...
    }

    return { blockingErrors: [], preventContinuation: false }
  } catch (error) {
    logEvent('tengu_stop_hook_error', {
      duration: Date.now() - hookStartTime,
      queryChainId: toolUseContext.queryTracking?.chainId,
      queryDepth: toolUseContext.queryTracking?.depth,
    })
    yield createSystemMessage(
      `Stop hook failed: ${errorMessage(error)}`,
      'warning',
    )
    return { blockingErrors: [], preventContinuation: false }
  }
}
```

**钩子类型**:
1. **Stop Hooks**: 每次查询结束时执行
2. **TaskCompleted Hooks**: teammate 完成任务时执行
3. **TeammateIdle Hooks**: teammate 空闲时执行

**后台任务**（非 bare 模式）:
- Prompt Suggestion
- Memory Extraction
- Auto Dream
- Computer Use Cleanup

**错误处理**:
- Blocking errors: 阻止继续执行
- Non-blocking errors: 记录但不阻止
- 超时保护：60 秒超时（job classifier）

---

## 四、Memory 发现算法详解

### 4.1 完整流程

```
┌─────────────────────────────────────────────────────────────┐
│              Memory Discovery Algorithm Flow                 │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  1. User Query Input                                         │
│         │                                                    │
│         ▼                                                    │
│  2. scanMemoryFiles(memoryDir)                              │
│     - readdir(recursive)                                     │
│     - filter *.md (exclude MEMORY.md)                        │
│     - Promise.allSettled:                                    │
│       - readFileInRange(0-30 lines)                          │
│       - parseFrontmatter                                     │
│       - extract {filename, description, type, mtime}         │
│     - sort by mtimeMs DESC                                   │
│     - slice(0, 200)                                          │
│         │                                                    │
│         ▼                                                    │
│  3. filter alreadySurfaced paths                            │
│         │                                                    │
│         ▼                                                    │
│  4. formatMemoryManifest()                                  │
│     - "- [type] filename (timestamp): description"           │
│         │                                                    │
│         ▼                                                    │
│  5. selectRelevantMemories()                                │
│     - sideQuery(Sonnet):                                     │
│       - system: SELECT_MEMORIES_SYSTEM_PROMPT                │
│       - user: "Query: {query}\n\nAvailable memories: {manifest}" │
│       - output: JSON schema {selected_memories: string[]}    │
│       - max_tokens: 256                                      │
│     - parse JSON response                                    │
│     - filter valid filenames                                 │
│         │                                                    │
│         ▼                                                    │
│  6. Map filenames → MemoryHeader                            │
│         │                                                    │
│         ▼                                                    │
│  7. logMemoryRecallShape() (telemetry)                      │
│         │                                                    │
│         ▼                                                    │
│  8. Return RelevantMemory[]                                 │
│     [{path, mtimeMs}, ...]                                   │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

### 4.2 相关性评分机制

**Sonnet 选择标准**:
1. **查询关键词匹配**: 基于 query 与 Memory 描述的相关性
2. **确定性阈值**: 仅选择"明确有用"的 Memory
3. **工具使用过滤**: 排除正在使用工具的参考文档
4. **例外**: 保留工具的警告/陷阱/已知问题

**保守策略**:
```typescript
// SELECT_MEMORIES_SYSTEM_PROMPT
"- If you are unsure if a memory will be useful in processing the user's query, 
   then do not include it in your list. Be selective and discerning."
"- If there are no memories in the list that would clearly be useful, 
   feel free to return an empty list."
```

### 4.3 去重机制

**alreadySurfaced 过滤**:
```typescript
const memories = (await scanMemoryFiles(memoryDir, signal)).filter(
  m => !alreadySurfaced.has(m.filePath),
)
```

**使用场景**:
- 多轮对话中避免重复展示同一 Memory
- 调用方维护已展示路径集合
- 让 Sonnet 的 5 个名额用于新 Memory

---

## 五、总结

### 5.1 Memory 系统设计哲学

1. **文件优先**: 所有 Memory 存储在独立 .md 文件中
2. **索引分离**: MEMORY.md 仅作为索引，不存储内容
3. **类型约束**: 封闭的 4 类型分类法防止滥用
4. **新鲜度感知**: 陈旧 Memory 自动添加警告
5. **安全验证**: 多层路径验证防止注入攻击

### 5.2 Query 系统设计哲学

1. **配置不可变**: 在入口快照，避免迭代中变化
2. **依赖注入**: 测试可注入 fake，减少 mock 样板
3. **预算保护**: Token 预算 + 收益递减防止浪费
4. **钩子扩展**: Stop Hooks 提供灵活的扩展点

### 5.3 关键创新

1. **单次遍历扫描**: `readFileInRange` 同时获取 content + mtime，减少 I/O
2. **Sonnet 选择**: 使用 AI 模型而非关键词匹配选择相关 Memory
3. **符号链接解析**: `realpathDeepestExisting` 防御 symlink 逃逸
4. **收益递减检测**: 基于增量 token 使用识别低效对话

---

*文档持续更新中...*
