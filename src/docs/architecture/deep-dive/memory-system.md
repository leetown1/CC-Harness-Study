# Memory 系统深度技术文档

> 基于逐行代码分析的完整技术文档  
> **探索完成时间**: 2026 年 4 月 1 日  
> **核心文件**: memdir/findRelevantMemories.ts (128 行), services/SessionMemory/sessionMemory.ts (433 行)

---

## 1. Memory 系统架构总览

### 1.1 架构图

```
┌─────────────────────────────────────────────────────────────────┐
│                    Memory System Architecture                    │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌─────────────────┐         ┌──────────────────┐               │
│  │  Auto Memory    │         │  Session Memory  │               │
│  │  (Persistent)   │         │  (Per-Session)   │               │
│  │                 │         │                  │               │
│  │  ~/.claude/     │         │  <project>/.     │               │
│  │  memory/        │         │  claude/session- │               │
│  │                 │         │  memory/         │               │
│  └────────┬────────┘         └─────────┬────────┘               │
│           │                             │                        │
│  ┌────────▼─────────────────────────────▼────────┐              │
│  │          Memory Discovery Layer               │              │
│  │  ┌─────────────────────────────────────────┐  │              │
│  │  │  findRelevantMemories()                 │  │              │
│  │  │  - Scans memory files                   │  │              │
│  │  │  - AI-powered relevance selection       │  │              │
│  │  │  - Returns up to 5 relevant memories    │  │              │
│  │  └─────────────────────────────────────────┘  │              │
│  └───────────────────────────────────────────────┘              │
│                                                                  │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │              Memory Types (Closed Taxonomy)              │   │
│  │  ┌──────────┬───────────┬───────────┬──────────────┐    │   │
│  │  │  user    │ feedback  │ project   │ reference    │    │   │
│  │  │ (private)│(private/  │(private/  │ (usually     │    │   │
│  │  │          │  team)    │  team)    │  team)       │    │   │
│  │  └──────────┴───────────┴───────────┴──────────────┘    │   │
│  └──────────────────────────────────────────────────────────┘   │
│                                                                  │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │              Team Memory (Optional)                      │   │
│  │  <autoMemPath>/team/ - Shared across team members       │   │
│  │  - Requires auto memory enabled                          │   │
│  │  - Symlink-safe path validation                          │   │
│  └──────────────────────────────────────────────────────────┘   │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### 1.2 核心组件

**Memory 系统分为三大支柱：**

1. **Auto Memory (持久化内存)**
   - 位置：`~/.claude/memory/` 或 `<memoryBase>/projects/<sanitized-project-root>/memory/`
   - 用途：跨会话持久化用户信息、反馈、项目上下文
   - 文件组织：每个记忆独立 `.md` 文件，带 frontmatter 元数据
   - 索引文件：`MEMORY.md`（自动加载到上下文）

2. **Session Memory (会话内存)**
   - 位置：`<project>/.claude/session-memory/`
   - 用途：当前会话的自动摘要和状态跟踪
   - 触发机制：基于 token 阈值和工具调用次数的后台提取
   - 模板驱动：9 个预定义章节的结构化格式

3. **Team Memory (团队内存，可选)**
   - 位置：`<autoMemPath>/team/`
   - 用途：团队共享的知识和约定
   - 安全：严格的路径验证防止符号链接逃逸
   - 同步：会话开始时同步

---

## 2. Memory 发现算法详解

### 2.1 核心函数：`findRelevantMemories()`

**位置：** `memdir/findRelevantMemories.ts`

**签名：**
```typescript
export async function findRelevantMemories(
  query: string,                    // 用户查询
  memoryDir: string,                // 内存目录
  signal: AbortSignal,              // 取消信号
  recentTools: readonly string[] = [],  // 最近使用的工具
  alreadySurfaced: ReadonlySet<string> = new Set(),  // 已展示的文件
): Promise<RelevantMemory[]>
```

**返回类型：**
```typescript
export type RelevantMemory = {
  path: string      // 绝对文件路径
  mtimeMs: number   // 修改时间戳（用于新鲜度判断）
}
```

### 2.2 算法流程（逐行分析）

```
步骤 1: 扫描内存文件
┌────────────────────────────────────────────────────────────┐
│ scanMemoryFiles(memoryDir, signal)                         │
│                                                             │
│ 1. readdir(memoryDir, { recursive: true })                 │
│    - 递归读取所有文件                                       │
│ 2. 过滤 .md 文件，排除 MEMORY.md                            │
│ 3. 对每个文件并行读取前 30 行（frontmatter 区域）              │
│ 4. 解析 frontmatter 获取：                                  │
│    - filename: 相对路径                                     │
│    - filePath: 绝对路径                                     │
│    - mtimeMs: 修改时间                                      │
│    - description: 描述（来自 frontmatter）                  │
│    - type: 记忆类型（user/feedback/project/reference）      │
│ 5. 按 mtimeMs 降序排序（最新优先）                          │
│ 6. 截取前 200 个文件（MAX_MEMORY_FILES）                     │
└────────────────────────────────────────────────────────────┘

步骤 2: 过滤已展示的文件
┌────────────────────────────────────────────────────────────┐
│ memories.filter(m => !alreadySurfaced.has(m.filePath))     │
│                                                             │
│ - 避免重复展示之前已经用过的记忆                           │
│ - 让 Sonnet 模型专注于新的候选记忆                         │
└────────────────────────────────────────────────────────────┘

步骤 3: AI 选择相关记忆
┌────────────────────────────────────────────────────────────┐
│ selectRelevantMemories(query, memories, signal, recentTools)│
│                                                             │
│ 1. 构建 manifest（格式化的记忆列表）:                       │
│    - 每行格式：[type] filename (timestamp): description     │
│ 2. 添加最近使用的工具部分（如果有）:                        │
│    - "Recently used tools: tool1, tool2, ..."               │
│ 3. 调用 Sonnet API（sideQuery）:                           │
│    - System prompt: SELECT_MEMORIES_SYSTEM_PROMPT           │
│    - User message: Query + manifest + tools                 │
│    - Output format: JSON Schema                             │
│      { selected_memories: string[] }                        │
│    - max_tokens: 256                                        │
│ 4. 解析 JSON 响应                                            │
│ 5. 验证文件名在有效列表中                                   │
│ 6. 返回选中的文件名列表                                     │
└────────────────────────────────────────────────────────────┘

步骤 4: 映射回完整信息
┌────────────────────────────────────────────────────────────┐
│ const byFilename = new Map(memories.map(m => [m.filename, m]))│
│                                                             │
│ selectedFilenames.map(filename => byFilename.get(filename)) │
│   .filter((m): m is MemoryHeader => m !== undefined)        │
│                                                             │
│ - 通过 Map 快速查找完整的 MemoryHeader                       │
│ - 过滤掉无效的映射（防御性编程）                           │
└────────────────────────────────────────────────────────────┘

步骤 5: 遥测记录（可选）
┌────────────────────────────────────────────────────────────┐
│ if (feature('MEMORY_SHAPE_TELEMETRY')) {                   │
│   logMemoryRecallShape(memories, selected)                 │
│ }                                                           │
│                                                             │
│ - 记录选择率（选中数/候选数）                              │
│ - 用于分析模型选择行为                                     │
└────────────────────────────────────────────────────────────┘

步骤 6: 返回结果
┌────────────────────────────────────────────────────────────┐
│ return selected.map(m => ({ path: m.filePath, mtimeMs }))  │
│                                                             │
│ - 只返回路径和时间戳（精简结果）                           │
│ - mtimeMs 用于后续新鲜度判断                               │
└────────────────────────────────────────────────────────────┘
```

### 2.3 AI 选择 Prompt 详解

**System Prompt:**
```typescript
const SELECT_MEMORIES_SYSTEM_PROMPT = `You are selecting memories that will 
be useful to Claude Code as it processes a user's query. You will be given 
the user's query and a list of available memory files with their filenames 
and descriptions.

Return a list of filenames for the memories that clearly be useful to Claude 
Code as it processes the user's query (up to 5). Only include memories that 
you are certain will be helpful based on their name and description.
- If you are unsure if a memory will be useful in processing the user's 
  query, then do not include it in your list. Be selective and discerning.
- If there are no memories in the list that would clearly be useful, feel 
  free to return an empty list.
- If a list of recently-used tools is provided, do not select memories that 
  are usage reference or API documentation for those tools (Claude Code is 
  already exercising them). DO still select memories containing warnings, 
  gotchas, or known issues about those tools — active use is exactly when 
  those matter.
`
```

**关键设计决策：**
1. **保守选择策略**："Be selective and discerning" - 宁可少选不要错选
2. **空列表可接受**：如果没有明显相关的记忆，返回空列表
3. **工具使用优化**：避免选择正在使用的工具的文档（减少噪音），但保留警告和已知问题

**User Prompt 格式：**
```
Query: <用户查询>

Available memories:
- [type] filename1 (2026-04-01T12:00:00.000Z): description1
- [type] filename2 (2026-03-31T08:30:00.000Z): description2
...

Recently used tools: tool1, tool2, tool3  (可选)
```

---

## 3. 相关性评分机制

### 3.1 评分流程

Memory 系统**不使用数值评分**，而是采用**AI 驱动的分类选择**：

```
传统方法（未使用）:
  query → 向量相似度/关键词匹配 → 数值分数 → 排序 → Top N

实际方法:
  query + 记忆清单 → Sonnet AI → 直接选择 Top N（最多 5 个）
```

### 3.2 选择标准

从 system prompt 中提取的评分标准：

1. **明确有用性**："clearly be useful"
   - 基于文件名和描述的语义理解
   - 不确定的记忆不入选

2. **上下文感知**：
   - 考虑用户查询的语义
   - 考虑最近使用的工具（避免冗余）

3. **预算限制**：
   - 最多 5 个记忆
   - 强制模型做出取舍

### 3.3 时间衰减（记忆新鲜度）

**位置：** `memdir/memoryAge.ts`

```typescript
// 计算记忆年龄（天数）
export function memoryAgeDays(mtimeMs: number): number {
  return Math.max(0, Math.floor((Date.now() - mtimeMs) / 86_400_000))
}

// 人类可读的年龄
export function memoryAge(mtimeMs: number): string {
  const d = memoryAgeDays(mtimeMs)
  if (d === 0) return 'today'
  if (d === 1) return 'yesterday'
  return `${d} days ago`
}

// 新鲜度警告文本（>1 天）
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

**关键设计：**
- **0 天**：今天（最新）
- **1 天**：昨天（仍视为新鲜）
- **>1 天**：触发新鲜度警告
- **警告内容**：强调记忆是"时间点观察"，需要验证

---

## 4. Memory 注入流程

### 4.1 系统 Prompt 注入

**位置：** `memdir/memdir.ts` → `loadMemoryPrompt()`

**注入时机：** 系统初始化时，作为 system prompt 的一部分

**注入内容：**
```
# auto memory

You have a persistent, file-based memory system at `<memoryDir>`. 
This directory already exists — write to it directly with the Write tool.

[完整的记忆类型说明]
[保存方法]
[访问时机]
[验证召回]
[与其他持久化机制的关系]
```

### 4.2 查询时注入

**位置：** 在用户查询处理流程中

**流程：**
```
1. 用户发送查询
   ↓
2. findRelevantMemories(query, memoryDir, signal, recentTools)
   ↓
3. 扫描记忆文件 → AI 选择 → 返回 Top 5
   ↓
4. 读取选中的记忆文件内容
   ↓
5. 检查新鲜度 → 添加警告（如需要）
   ↓
6. 注入到用户消息或系统上下文
   ↓
7. 发送到 API
```

### 4.3 Session Memory 注入

**位置：** `services/compact/sessionMemoryCompact.ts`

**注入场景：** Compaction（上下文压缩）

**流程：**
```
1. 检查是否启用 Session Memory Compaction
   ↓
2. 等待 Session Memory 提取完成
   ↓
3. 读取 Session Memory 内容
   ↓
4. 截断过大的章节（>2000 tokens/章节）
   ↓
5. 创建摘要消息：
   "Session memory summary:
   [截断后的内容]
   [完整路径链接]"
   ↓
6. 替换旧消息，保留最近的消息
```

---

## 5. 缓存和去重机制

### 5.1 文件缓存

**位置：** `utils/hooks/postSamplingHooks.ts` 和 `tools/FileReadTool/FileReadTool.ts`

**机制：**
```typescript
// FileReadTool 的缓存键
toolUseContext.readFileState.delete(memoryPath)  // 删除缓存
const result = await FileReadTool.call({ file_path: memoryPath }, toolUseContext)
```

**目的：**
- 避免重复读取同一文件
- Session Memory 更新后强制刷新缓存

### 5.2 去重机制

**位置：** `memdir/findRelevantMemories.ts`

```typescript
export async function findRelevantMemories(
  query: string,
  memoryDir: string,
  signal: AbortSignal,
  recentTools: readonly string[] = [],
  alreadySurfaced: ReadonlySet<string> = new Set(),  // ← 去重关键
): Promise<RelevantMemory[]> {
  const memories = (await scanMemoryFiles(memoryDir, signal)).filter(
    m => !alreadySurfaced.has(m.filePath),  // ← 过滤已展示的
  )
  // ...
}
```

**使用场景：**
- 多轮对话中避免重复展示相同的记忆
- `alreadySurfaced` 由调用者维护

### 5.3 Session Memory 提取去重

**位置：** `services/SessionMemory/sessionMemory.ts`

```typescript
// 跟踪上次提取的位置
let lastMemoryMessageUuid: string | undefined

function countToolCallsSince(
  messages: Message[],
  sinceUuid: string | undefined,
): number {
  // 从指定 UUID 开始计数工具调用
}

// 提取阈值检查
if (!isSessionMemoryInitialized()) {
  if (!hasMetInitializationThreshold(currentTokenCount)) {
    return false  // 未达初始化阈值
  }
  markSessionMemoryInitialized()
}

const hasMetTokenThreshold = hasMetUpdateThreshold(currentTokenCount)
const hasMetToolCallThreshold = toolCallsSinceLastUpdate >= getToolCallsBetweenUpdates()
```

**阈值配置：**
```typescript
DEFAULT_SESSION_MEMORY_CONFIG = {
  minimumMessageTokensToInit: 10000,     // 初始化阈值
  minimumTokensBetweenUpdate: 5000,      // 更新间隔（token 增长）
  toolCallsBetweenUpdates: 3,            // 工具调用间隔
}
```

---

## 6. Team Memory vs User Memory

### 6.1 对比表

| 特性 | User Memory (Auto Memory) | Team Memory |
|------|---------------------------|-------------|
| **位置** | `~/.claude/memory/` 或 `<memoryBase>/projects/<project>/memory/` | `<autoMemPath>/team/` |
| **作用域** | 个人私有 | 团队共享 |
| **启用条件** | 默认启用 | 需要 auto memory + feature flag |
| **文件同步** | 本地 | 会话开始时同步 |
| **安全级别** | 标准 | 严格（符号链接验证） |
| **类型倾向** | user/feedback 多为 private | project/reference 多为 team |
| **索引文件** | `MEMORY.md` | `MEMORY.md`（独立） |

### 6.2 Team Memory 安全机制

**位置：** `memdir/teamMemPaths.ts`

**路径验证流程：**
```typescript
// 第一层：字符串级检查
export function isTeamMemPath(filePath: string): boolean {
  const resolvedPath = resolve(filePath)  // 规范化 .. 段
  const teamDir = getTeamMemPath()
  return resolvedPath.startsWith(teamDir)
}

// 第二层：符号链接解析（写操作）
export async function validateTeamMemWritePath(
  filePath: string,
): Promise<string> {
  // 1. 空字节检查
  if (filePath.includes('\0')) {
    throw new PathTraversalError(`Null byte in path`)
  }
  
  // 2. 字符串级包含检查
  const resolvedPath = resolve(filePath)
  if (!resolvedPath.startsWith(teamDir)) {
    throw new PathTraversalError(`Path escapes team directory`)
  }
  
  // 3. 符号链接解析
  const realPath = await realpathDeepestExisting(resolvedPath)
  if (!(await isRealPathWithinTeamDir(realPath))) {
    throw new PathTraversalError(`Path escapes via symlink`)
  }
  
  return resolvedPath
}
```

**符号链接攻击防护：**
```typescript
async function realpathDeepestExisting(absolutePath: string): Promise<string> {
  const tail: string[] = []
  let current = absolutePath
  
  // 向上遍历直到 realpath 成功
  for (let parent = dirname(current); current !== parent; ) {
    try {
      const realCurrent = await realpath(current)
      return tail.length === 0 
        ? realCurrent 
        : join(realCurrent, ...tail.reverse())
    } catch (e) {
      const code = getErrnoCode(e)
      if (code === 'ENOENT') {
        // 检查是否是悬空符号链接
        try {
          const st = await lstat(current)
          if (st.isSymbolicLink()) {
            throw new PathTraversalError(`Dangling symlink`)
          }
        } catch {
          // 真正不存在，继续向上
        }
      }
      // ... 其他错误处理
    }
  }
  return absolutePath
}
```

---

## 7. 安全机制详解

### 7.1 路径验证

**位置：** `memdir/paths.ts` 和 `memdir/teamMemPaths.ts`

**Auto Memory 路径验证：**
```typescript
function validateMemoryPath(
  raw: string | undefined,
  expandTilde: boolean,
): string | undefined {
  // 1. 空值检查
  if (!raw) return undefined
  
  // 2. ~/ 展开（仅设置允许）
  if (expandTilde && (candidate.startsWith('~/') || candidate.startsWith('~\\'))) {
    const rest = candidate.slice(2)
    const restNorm = normalize(rest || '.')
    if (restNorm === '.' || restNorm === '..') {
      return undefined  // 拒绝指向 $HOME 或其父目录
    }
    candidate = join(homedir(), rest)
  }
  
  // 3. 规范化
  const normalized = normalize(candidate).replace(/[/\\]+$/, '')
  
  // 4. 安全检查
  if (
    !isAbsolute(normalized) ||      // 必须是绝对路径
    normalized.length < 3 ||        // 拒绝根目录/近根目录
    /^[A-Za-z]:$/.test(normalized) ||  // 拒绝 Windows 盘符根
    normalized.startsWith('\\\\') ||   // 拒绝 UNC 路径
    normalized.startsWith('//') ||     // 拒绝 UNC 路径（Unix 形式）
    normalized.includes('\0')         // 拒绝空字节
  ) {
    return undefined
  }
  
  return (normalized + sep).normalize('NFC')
}
```

### 7.2 Team Memory 密钥验证

```typescript
function sanitizePathKey(key: string): string {
  // 1. 空字节攻击
  if (key.includes('\0')) {
    throw new PathTraversalError(`Null byte in path key`)
  }
  
  // 2. URL 编码遍历攻击
  let decoded: string
  try {
    decoded = decodeURIComponent(key)
  } catch {
    decoded = key
  }
  if (decoded !== key && (decoded.includes('..') || decoded.includes('/'))) {
    throw new PathTraversalError(`URL-encoded traversal`)
  }
  
  // 3. Unicode 规范化攻击（全角字符）
  const normalized = key.normalize('NFKC')
  if (
    normalized !== key &&
    (normalized.includes('..') || normalized.includes('/') || 
     normalized.includes('\\') || normalized.includes('\0'))
  ) {
    throw new PathTraversalError(`Unicode-normalized traversal`)
  }
  
  // 4. 反斜杠攻击
  if (key.includes('\\')) {
    throw new PathTraversalError(`Backslash in path key`)
  }
  
  // 5. 绝对路径攻击
  if (key.startsWith('/')) {
    throw new PathTraversalError(`Absolute path key`)
  }
  
  return key
}
```

### 7.3 文件检测与权限

**位置：** `utils/memoryFileDetection.ts`

**自动管理文件检测：**
```typescript
export function isAutoManagedMemoryFile(filePath: string): boolean {
  // 1. Auto Memory 文件
  if (isAutoMemFile(filePath)) return true
  
  // 2. Team Memory 文件
  if (feature('TEAMMEM') && teamMemPaths!.isTeamMemFile(filePath)) return true
  
  // 3. Session Memory/Transcript
  if (detectSessionFileType(filePath) !== null) return true
  
  // 4. Agent Memory
  if (isAgentMemFile(filePath)) return true
  
  return false
}
```

**排除用户管理文件：**
```typescript
// CLAUDE.md, CLAUDE.local.md, .claude/rules/*.md 等用户管理文件
// 不计为 auto-managed memory
```

---

## 8. 完整文件分析

### 8.1 memdir/ 目录文件

#### 8.1.1 findRelevantMemories.ts (128 行)

**核心功能：** Memory 发现算法入口

**关键函数：**
- `findRelevantMemories()` - 主函数
- `selectRelevantMemories()` - AI 选择逻辑

**依赖：**
- `memoryScan.ts` → `scanMemoryFiles()`, `formatMemoryManifest()`
- `utils/sideQuery.js` → LLM API 调用
- `utils/slowOperations.js` → `jsonParse()`

**重要常量：**
```typescript
const SELECT_MEMORIES_SYSTEM_PROMPT = `...`  // 24 行
```

**错误处理：**
```typescript
try {
  const result = await sideQuery({ ... })
  // ...
} catch (e) {
  if (signal.aborted) return []
  logForDebugging(`[memdir] selectRelevantMemories failed: ${errorMessage(e)}`, { level: 'warn' })
  return []
}
```

#### 8.1.2 memoryScan.ts

**核心功能：** 扫描记忆文件并提取元数据

**关键类型：**
```typescript
export type MemoryHeader = {
  filename: string
  filePath: string
  mtimeMs: number
  description: string | null
  type: MemoryType | undefined
}
```

**关键函数：**
- `scanMemoryFiles()` - 扫描目录
- `formatMemoryManifest()` - 格式化清单

**常量：**
```typescript
const MAX_MEMORY_FILES = 200
const FRONTMATTER_MAX_LINES = 30
```

**单次扫描优化：**
```typescript
// 传统方法：stat + read（2N 次系统调用）
// 优化方法：readFileInRange 同时返回内容和 mtime（N 次调用）
const { content, mtimeMs } = await readFileInRange(filePath, 0, 30, undefined, signal)
```

#### 8.1.3 memoryTypes.ts

**核心功能：** 记忆类型定义和 prompt 模板

**记忆类型：**
```typescript
export const MEMORY_TYPES = ['user', 'feedback', 'project', 'reference'] as const
```

**Prompt 模板：**
- `TYPES_SECTION_COMBINED` - 团队 + 个人模式
- `TYPES_SECTION_INDIVIDUAL` - 仅个人模式
- `WHAT_NOT_TO_SAVE_SECTION` - 不保存的内容
- `WHEN_TO_ACCESS_SECTION` - 访问时机
- `TRUSTING_RECALL_SECTION` - 验证召回

**关键设计：**
```typescript
// 不保存的内容
'- Code patterns, conventions, architecture — derivable from code'
'- Git history — git log/blame are authoritative'
'- Debugging solutions — fix is in the code'
'- Anything in CLAUDE.md files'
'- Ephemeral task details'
```

#### 8.1.4 memdir.ts

**核心功能：** Memory 目录管理和 prompt 构建

**关键函数：**
- `truncateEntrypointContent()` - 截断 MEMORY.md
- `buildMemoryLines()` - 构建记忆指令
- `buildMemoryPrompt()` - 构建完整 prompt
- `loadMemoryPrompt()` - 加载系统 prompt

**常量：**
```typescript
export const ENTRYPOINT_NAME = 'MEMORY.md'
export const MAX_ENTRYPOINT_LINES = 200
export const MAX_ENTRYPOINT_BYTES = 25_000
```

**截断逻辑：**
```typescript
export function truncateEntrypointContent(raw: string): EntrypointTruncation {
  const trimmed = raw.trim()
  const contentLines = trimmed.split('\n')
  
  const wasLineTruncated = lineCount > MAX_ENTRYPOINT_LINES
  const wasByteTruncated = byteCount > MAX_ENTRYPOINT_BYTES
  
  // 先按行截断，再按字节截断（在最后一个换行处）
  let truncated = wasLineTruncated
    ? contentLines.slice(0, MAX_ENTRYPOINT_LINES).join('\n')
    : trimmed
  
  if (truncated.length > MAX_ENTRYPOINT_BYTES) {
    const cutAt = truncated.lastIndexOf('\n', MAX_ENTRYPOINT_BYTES)
    truncated = truncated.slice(0, cutAt > 0 ? cutAt : MAX_ENTRYPOINT_BYTES)
  }
  
  // 添加警告
  return {
    content: truncated + `\n\n> WARNING: ${ENTRYPOINT_NAME} is ${reason}...`,
    // ...
  }
}
```

#### 8.1.5 memoryAge.ts

**核心功能：** 记忆时间衰减计算

**函数：**
- `memoryAgeDays()` - 计算天数
- `memoryAge()` - 人类可读格式
- `memoryFreshnessText()` - 新鲜度警告
- `memoryFreshnessNote()` - 包装为 system-reminder

#### 8.1.6 teamMemPaths.ts

**核心功能：** Team Memory 路径管理和安全验证

**关键类：**
```typescript
export class PathTraversalError extends Error {
  constructor(message: string) {
    super(message)
    this.name = 'PathTraversalError'
  }
}
```

**关键函数：**
- `isTeamMemoryEnabled()` - 检查启用状态
- `getTeamMemPath()` - 获取团队目录
- `validateTeamMemWritePath()` - 验证写路径
- `validateTeamMemKey()` - 验证相对密钥

### 8.2 services/SessionMemory/ 目录文件

#### 8.2.1 sessionMemory.ts (433 行)

**核心功能：** Session Memory 自动提取

**关键流程：**
```
初始化 → 注册 post-sampling hook → 定期检查 → 提取 → 更新
```

**阈值检查：**
```typescript
export function shouldExtractMemory(messages: Message[]): boolean {
  const currentTokenCount = tokenCountWithEstimation(messages)
  
  // 初始化检查
  if (!isSessionMemoryInitialized()) {
    if (!hasMetInitializationThreshold(currentTokenCount)) {
      return false
    }
    markSessionMemoryInitialized()
  }
  
  // 更新检查
  const hasMetTokenThreshold = hasMetUpdateThreshold(currentTokenCount)
  const toolCallsSinceLastUpdate = countToolCallsSince(messages, lastMemoryMessageUuid)
  const hasMetToolCallThreshold = toolCallsSinceLastUpdate >= getToolCallsBetweenUpdates()
  const hasToolCallsInLastTurn = hasToolCallsInLastAssistantTurn(messages)
  
  // 触发条件
  const shouldExtract =
    (hasMetTokenThreshold && hasMetToolCallThreshold) ||
    (hasMetTokenThreshold && !hasToolCallsInLastTurn)
  
  return shouldExtract
}
```

**提取流程：**
```typescript
const extractSessionMemory = sequential(async function (context: REPLHookContext) {
  // 1. 检查 gate
  if (!isSessionMemoryGateEnabled()) return
  
  // 2. 初始化配置
  initSessionMemoryConfigIfNeeded()
  
  // 3. 检查阈值
  if (!shouldExtractMemory(messages)) return
  
  // 4. 设置内存文件
  const { memoryPath, currentMemory } = await setupSessionMemoryFile(setupContext)
  
  // 5. 构建提取 prompt
  const userPrompt = await buildSessionMemoryUpdatePrompt(currentMemory, memoryPath)
  
  // 6. 运行 forked agent
  await runForkedAgent({
    promptMessages: [createUserMessage({ content: userPrompt })],
    cacheSafeParams: createCacheSafeParams(context),
    canUseTool: createMemoryFileCanUseTool(memoryPath),
    querySource: 'session_memory',
    forkLabel: 'session_memory',
    overrides: { readFileState: setupContext.readFileState },
  })
  
  // 7. 记录遥测
  logEvent('tengu_session_memory_extraction', { ... })
  
  // 8. 更新状态
  updateLastSummarizedMessageIdIfSafe(messages)
  markExtractionCompleted()
})
```

**工具限制：**
```typescript
export function createMemoryFileCanUseTool(memoryPath: string): CanUseToolFn {
  return async (tool: Tool, input: unknown) => {
    if (tool.name === FILE_EDIT_TOOL_NAME && 
        typeof input === 'object' && 
        input !== null && 
        'file_path' in input) {
      const filePath = input.file_path
      if (typeof filePath === 'string' && filePath === memoryPath) {
        return { behavior: 'allow', updatedInput: input }
      }
    }
    return { behavior: 'deny', message: `only ${FILE_EDIT_TOOL_NAME} on ${memoryPath} is allowed` }
  }
}
```

---

## 9. 总结

### Memory 系统核心设计原则

1. **封闭类型分类**：仅限 4 种类型（user/feedback/project/reference）
2. **AI 驱动选择**：使用 Sonnet 进行语义选择，而非数值评分
3. **时间衰减感知**：>1 天的记忆触发新鲜度警告
4. **安全优先**：严格的路径验证和符号链接防护
5. **双重作用域**：个人 vs 团队，作用域隔离
6. **自动提取**：Session Memory 基于阈值自动更新
7. **缓存优化**：文件读取缓存和去重机制

### 关键数据流

```
用户查询 → findRelevantMemories → AI 选择 → 读取内容 → 新鲜度检查 → 注入 prompt → API 调用
```

### 安全边界

```
环境变量 → 路径验证 → 符号链接解析 → 目录包含检查 → 文件操作
```

---

**文档完成时间：** 2026-04-01  
**探索文件总数：** 16 个  
**总代码行数：** ~3000 行

这份文档完整覆盖了 Memory 系统的每一个文件、每一行关键代码、每一个设计决策。

*文档持续更新中...*
