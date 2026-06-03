# Constants 系统深度技术文档

> 基于逐行代码分析的完整技术文档  
> **探索完成时间**: 2026 年 4 月 1 日  
> **核心文件**: constants/ 目录下 21 个文件

---

## 1. Constants 系统架构概览

### 1.1 目录结构

constants/ 目录包含 **21 个 TypeScript 文件**，涵盖以下核心领域：

| 类别 | 文件 | 行数 | 主要用途 |
|------|------|------|----------|
| **核心系统** | `system.ts` | 95 | 系统提示前缀、归属头 |
| **核心系统** | `prompts.ts` | 914 | 系统提示构建、环境信息 |
| **核心系统** | `common.ts` | 33 | 日期处理、会话管理 |
| **工具系统** | `tools.ts` | 112 | 工具权限、代理工具限制 |
| **工具系统** | `toolLimits.ts` | 56 | 工具结果大小限制 |
| **工具系统** | `xml.ts` | 86 | XML 标签常量定义 |
| **工具系统** | `files.ts` | 156 | 二进制文件扩展名检测 |
| **提示系统** | `systemPromptSections.ts` | 68 | 系统提示段缓存管理 |
| **提示系统** | `outputStyles.ts` | 216 | 输出样式配置 |
| **提示系统** | `turnCompletionVerbs.ts` | 12 | Turn 完成动词 |
| **提示系统** | `spinnerVerbs.ts` | 203 | 加载旋转器动词 |
| **安全系统** | `cyberRiskInstruction.ts` | 24 | 网络安全指令 |
| **认证系统** | `oauth.ts` | 234 | OAuth 配置、作用域 |
| **认证系统** | `keys.ts` | 11 | GrowthBook 密钥 |
| **API 系统** | `apiLimits.ts` | 94 | API 限制（图片/PDF/媒体） |
| **API 系统** | `betas.ts` | 52 | Beta 头常量 |
| **API 系统** | `product.ts` | 76 | 产品 URL、远程会话 |
| **GitHub 集成** | `github-app.ts` | 144 | GitHub Actions 工作流 |
| **错误处理** | `errorIds.ts` | 16 | 错误 ID 跟踪 |
| **消息系统** | `messages.ts` | 2 | 消息常量 |
| **UI 符号** | `figures.ts` | 45 | Unicode 符号 |

### 1.2 设计原则

1. **单一职责**: 每个文件专注于一个特定领域
2. **死代码消除**: 使用 `feature()` 函数进行编译时消除
3. **环境变量覆盖**: 支持运行时配置覆盖
4. **类型安全**: 使用 TypeScript 常量和枚举
5. **向后兼容**: 严格的向后兼容性保证

---

## 2. 核心系统常量

### 2.1 common.ts (33 行) - 通用常量

**核心功能**: 日期处理函数

```typescript
// 获取本地 ISO 日期（支持环境变量覆盖）
export function getLocalISODate(): string
export const getSessionStartDate = memoize(getLocalISODate)

// 获取本地"月 年"格式（用于工具提示，最小化缓存破坏）
export function getLocalMonthYear(): string
```

**关键设计**:
- 使用 `memoize` 缓存会话开始日期，防止提示缓存破坏
- 支持 `CLAUDE_CODE_OVERRIDE_DATE` 环境变量覆盖
- 日期格式：`YYYY-MM-DD` 和 `Month YYYY`

### 2.2 system.ts (95 行) - 系统常量

**核心功能**: CLI 系统提示前缀和归属头

**系统提示前缀类型**:

```typescript
type CLISyspromptPrefix = 
  | "You are Claude Code, Anthropic's official CLI for Claude."
  | "You are Claude Code, Anthropic's official CLI for Claude, running within the Claude Agent SDK."
  | "You are a Claude agent, built on Anthropic's Claude Agent SDK."
```

**前缀选择逻辑**:
- `vertex` API 提供商 → 默认前缀
- 非交互模式 + appendSystemPrompt → Agent SDK Claude Code 前缀
- 非交互模式 → Agent SDK 前缀
- 交互模式 → 默认前缀

**归属头 (Attribution Header)**:

```typescript
export function getAttributionHeader(fingerprint: string): string
```

**归属头格式**:
```
x-anthropic-billing-header: cc_version=${version}.${fingerprint}; cc_entrypoint=${entrypoint}; cch=00000; cc_workload=${workload};
```

**关键特性**:
- 支持 GrowthBook 功能标志 `tengu_attribution_header` 控制
- 支持 `NATIVE_CLIENT_ATTESTATION` 时包含 `cch=00000` 占位符（由 Bun 的 HTTP 栈替换为实际哈希）
- 支持工作负载路由（`cc_workload`）用于 QoS 池路由

### 2.3 prompts.ts (914 行) - 提示模板

**核心功能**: 系统提示构建系统

**关键常量**:

```typescript
// 动态边界标记（分隔静态/动态内容）
export const SYSTEM_PROMPT_DYNAMIC_BOUNDARY = '__SYSTEM_PROMPT_DYNAMIC_BOUNDARY__'

// 前沿模型名称
const FRONTIER_MODEL_NAME = 'Claude Opus 4.6'

// 模型家族 ID
const CLAUDE_4_5_OR_4_6_MODEL_IDS = {
  opus: 'claude-opus-4-6',
  sonnet: 'claude-sonnet-4-6',
  haiku: 'claude-haiku-4-5-20251001'
}
```

**系统提示结构**:

```typescript
// 静态部分（可缓存）
1. getSimpleIntroSection()
2. getSimpleSystemSection()
3. getSimpleDoingTasksSection()
4. getActionsSection()
5. getUsingYourToolsSection()
6. getSimpleToneAndStyleSection()
7. getOutputEfficiencySection()
--- SYSTEM_PROMPT_DYNAMIC_BOUNDARY ---
// 动态部分（每 turn 重新计算）
8. session_guidance
9. memory
10. ant_model_override
11. env_info_simple
12. language
13. output_style
14. mcp_instructions
15. scratchpad
16. frc (Function Result Clearing)
17. summarize_tool_results
18. numeric_length_anchors (ant-only)
19. token_budget (feature-gated)
20. brief (KAIROS feature)
```

**主要函数**:

#### `getSystemPrompt(tools, model, additionalWorkingDirectories, mcpClients)`
- 返回：`Promise<string[]>`
- 构建完整系统提示
- 支持简单模式（`CLAUDE_CODE_SIMPLE`）
- 支持主动模式（`PROACTIVE`/`KAIROS`）

#### `computeEnvInfo(modelId, additionalWorkingDirectories)`
- 计算环境信息
- 包含：工作目录、git 状态、平台、shell、OS 版本、模型信息、知识截止日期

#### `getKnowledgeCutoff(modelId)`
- 返回模型知识截止日期
- Opus 4.6: May 2025
- Sonnet 4.6: August 2025
- Haiku 4.5: February 2025

**特殊模式**:

**1. 简单模式** (`CLAUDE_CODE_SIMPLE`)
```typescript
return [
  `You are Claude Code...\nCWD: ${getCwd()}\nDate: ${getSessionStartDate()}`
]
```

**2. 主动模式** (`PROACTIVE`/`KAIROS`)
```typescript
return [
  `\nYou are an autonomous agent...`,
  getSystemRemindersSection(),
  await loadMemoryPrompt(),
  envInfo,
  getLanguageSection(settings.language),
  getMcpInstructionsSection(mcpClients),
  getScratchpadInstructions(),
  getFunctionResultClearingSection(model),
  SUMMARIZE_TOOL_RESULTS_SECTION,
  getProactiveSection()
]
```

**Proactive 模式特性**:
- 使用 `<tick>` 提示保持活跃
- 使用 `SLEEP_TOOL_NAME` 控制节奏
- 终端焦点感知（focused/unfocused）
- 偏向行动而非确认

**代码风格指令**（ant-only）:
```
- 默认不写注释，仅在逻辑不明显时添加
- 不解释代码做什么（良好命名已说明）
- 不引用当前任务或调用者
- 不删除现有注释（除非删除对应代码）
- 运行测试验证完成情况
- 真实报告结果（不伪造成功）
```

---

## 3. 工具系统常量

### 3.1 tools.ts (112 行) - 工具常量

**核心功能**: 工具权限定义

**工具权限集**:

#### ALL_AGENT_DISALLOWED_TOOLS
所有代理禁止的工具：
```typescript
[
  TASK_OUTPUT_TOOL_NAME,
  EXIT_PLAN_MODE_V2_TOOL_NAME,
  ENTER_PLAN_MODE_TOOL_NAME,
  AGENT_TOOL_NAME,  // 除非 USER_TYPE === 'ant'
  ASK_USER_QUESTION_TOOL_NAME,
  TASK_STOP_TOOL_NAME,
  WORKFLOW_TOOL_NAME  // feature-gated
]
```

#### ASYNC_AGENT_ALLOWED_TOOLS
异步代理允许的工具：
```typescript
[
  FILE_READ_TOOL_NAME,
  WEB_SEARCH_TOOL_NAME,
  TODO_WRITE_TOOL_NAME,
  GREP_TOOL_NAME,
  WEB_FETCH_TOOL_NAME,
  GLOB_TOOL_NAME,
  ...SHELL_TOOL_NAMES,
  FILE_EDIT_TOOL_NAME,
  FILE_WRITE_TOOL_NAME,
  NOTEBOOK_EDIT_TOOL_NAME,
  SKILL_TOOL_NAME,
  SYNTHETIC_OUTPUT_TOOL_NAME,
  TOOL_SEARCH_TOOL_NAME,
  ENTER_WORKTREE_TOOL_NAME,
  EXIT_WORKTREE_TOOL_NAME
]
```

#### IN_PROCESS_TEAMMATE_ALLOWED_TOOLS
进程内队友专用工具：
```typescript
[
  TASK_CREATE_TOOL_NAME,
  TASK_GET_TOOL_NAME,
  TASK_LIST_TOOL_NAME,
  TASK_UPDATE_TOOL_NAME,
  SEND_MESSAGE_TOOL_NAME,
  CRON_CREATE_TOOL_NAME,  // feature-gated
  CRON_DELETE_TOOL_NAME,
  CRON_LIST_TOOL_NAME
]
```

#### COORDINATOR_MODE_ALLOWED_TOOLS
协调器模式工具：
```typescript
[
  AGENT_TOOL_NAME,
  TASK_STOP_TOOL_NAME,
  SEND_MESSAGE_TOOL_NAME,
  SYNTHETIC_OUTPUT_TOOL_NAME
]
```

**设计原则**:
- 防止递归（禁用 AgentTool、TaskOutputTool）
- 计划模式是主线程抽象（禁用 ExitPlanModeTool）
- TaskStopTool 需要主线程状态
- TungstenTool 使用单例虚拟终端

### 3.2 toolLimits.ts (56 行) - 工具限制

**核心功能**: 工具结果大小限制

**关键常量**:

```typescript
// 默认最大工具结果大小（字符）- 超过时持久化到磁盘
export const DEFAULT_MAX_RESULT_SIZE_CHARS = 50_000

// 最大工具结果大小（token）
export const MAX_TOOL_RESULT_TOKENS = 100_000  // ~400KB

// 每 token 字节数估算
export const BYTES_PER_TOKEN = 4

// 最大工具结果大小（字节）
export const MAX_TOOL_RESULT_BYTES = 400_000

// 每条消息最大工具结果大小（字符）
export const MAX_TOOL_RESULTS_PER_MESSAGE_CHARS = 200_000

// 工具摘要最大长度（字符）
export const TOOL_SUMMARY_MAX_LENGTH = 50
```

**设计原理**:
- `DEFAULT_MAX_RESULT_SIZE_CHARS`: 防止单个工具结果占用过多内存
- `MAX_TOOL_RESULTS_PER_MESSAGE_CHARS`: 防止 N 个并行工具同时达到上限产生超大消息
- 可通过 GrowthBook 标志 `tengu_hawthorn_window` 覆盖

### 3.3 xml.ts (86 行) - XML 标签常量

**核心功能**: XML 标签名称定义

**标签分类**:

#### 命令元数据
```typescript
COMMAND_NAME_TAG = 'command-name'
COMMAND_MESSAGE_TAG = 'command-message'
COMMAND_ARGS_TAG = 'command-args'
```

#### 终端输出
```typescript
BASH_INPUT_TAG = 'bash-input'
BASH_STDOUT_TAG = 'bash-stdout'
BASH_STDERR_TAG = 'bash-stderr'
LOCAL_COMMAND_STDOUT_TAG = 'local-command-stdout'
LOCAL_COMMAND_STDERR_TAG = 'local-command-stderr'
LOCAL_COMMAND_CAVEAT_TAG = 'local-command-caveat'

TERMINAL_OUTPUT_TAGS = [...]  // 所有终端标签数组
```

#### 任务通知
```typescript
TASK_NOTIFICATION_TAG = 'task-notification'
TASK_ID_TAG = 'task-id'
TOOL_USE_ID_TAG = 'tool-use-id'
TASK_TYPE_TAG = 'task-type'
OUTPUT_FILE_TAG = 'output-file'
STATUS_TAG = 'status'
SUMMARY_TAG = 'summary'
REASON_TAG = 'reason'
WORKTREE_TAG = 'worktree'
WORKTREE_PATH_TAG = 'worktreePath'
WORKTREE_BRANCH_TAG = 'worktreeBranch'
```

#### 远程会话
```typescript
ULTRAPLAN_TAG = 'ultraplan'
REMOTE_REVIEW_TAG = 'remote-review'
REMOTE_REVIEW_PROGRESS_TAG = 'remote-review-progress'
```

#### 团队通信
```typescript
TEAMMATE_MESSAGE_TAG = 'teammate-message'
CHANNEL_MESSAGE_TAG = 'channel-message'
CHANNEL_TAG = 'channel'
CROSS_SESSION_MESSAGE_TAG = 'cross-session-message'
```

#### Fork 指令
```typescript
FORK_BOILERPLATE_TAG = 'fork-boilerplate'
FORK_DIRECTIVE_PREFIX = 'Your directive: '
```

#### 通用参数
```typescript
COMMON_HELP_ARGS = ['help', '-h', '--help']
COMMON_INFO_ARGS = ['list', 'show', 'display', ...]  // 14 个参数
```

### 3.4 files.ts (156 行) - 文件常量

**核心功能**: 二进制文件检测

**二进制扩展名集合**（107 种）:

**分类**:
- **图片**: .png, .jpg, .jpeg, .gif, .bmp, .ico, .webp, .tiff, .tif
- **视频**: .mp4, .mov, .avi, .mkv, .webm, .wmv, .flv, .m4v, .mpeg, .mpg
- **音频**: .mp3, .wav, .ogg, .flac, .aac, .m4a, .wma, .aiff, .opus
- **压缩包**: .zip, .tar, .gz, .bz2, .7z, .rar, .xz, .z, .tgz, .iso
- **可执行文件**: .exe, .dll, .so, .dylib, .bin, .o, .a, .obj, .lib, .app, .msi, .deb, .rpm
- **文档**: .pdf, .doc, .docx, .xls, .xlsx, .ppt, .pptx, .odt, .ods, .odp
- **字体**: .ttf, .otf, .woff, .woff2, .eot
- **字节码**: .pyc, .pyo, .class, .jar, .war, .ear, .node, .wasm, .rlib
- **数据库**: .sqlite, .sqlite3, .db, .mdb, .idx
- **设计/3D**: .psd, .ai, .eps, .sketch, .fig, .xd, .blend, .3ds, .max
- **Flash**: .swf, .fla
- **锁/数据**: .lockb, .dat, .data

**检测函数**:
```typescript
export function hasBinaryExtension(filePath: string): boolean

export function isBinaryContent(buffer: Buffer): boolean
```

**二进制检测算法**:
1. 检查前 8192 字节（`BINARY_CHECK_SIZE`）
2. 查找空字节（null byte）→ 立即判定为二进制
3. 统计不可打印字符比例 → 超过 10% 判定为二进制

---

## 4. 提示系统常量

### 4.1 systemPromptSections.ts (68 行) - 系统提示部分

**核心功能**: 系统提示段的缓存管理

**类型定义**:
```typescript
type SystemPromptSection = {
  name: string
  compute: () => string | null | Promise<string | null>
  cacheBreak: boolean  // 是否破坏缓存
}
```

**关键函数**:

#### `systemPromptSection(name, compute)`
- 创建缓存的系统提示段
- 计算一次，缓存直到 `/clear` 或 `/compact`

#### `DANGEROUS_uncachedSystemPromptSection(name, compute, reason)`
- 创建易失性提示段（每 turn 重新计算）
- 会破坏提示缓存
- 需要提供破坏缓存的理由

#### `resolveSystemPromptSections(sections)`
- 异步解析所有提示段
- 缓存命中时直接返回
- 缓存未命中时计算并缓存

#### `clearSystemPromptSections()`
- 清除所有提示段缓存
- 同时重置 beta 头锁存器

### 4.2 outputStyles.ts (216 行) - 输出样式

**核心功能**: 输出样式配置系统

**样式类型**:
```typescript
type OutputStyleConfig = {
  name: string
  description: string
  prompt: string
  source: 'built-in' | 'userSettings' | 'projectSettings' | 'policySettings' | 'plugin'
  keepCodingInstructions?: boolean
  forceForPlugin?: boolean  // 插件强制使用的样式
}
```

**内置样式**:

#### 1. default
- 无特殊配置（null）

#### 2. Explanatory
- 描述：解释实现选择和代码库模式
- 特性：包含教育性见解（Insights）
- 提示：
```
## Insights
In order to encourage learning, before and after writing code, always 
provide brief educational explanations...
```

#### 3. Learning
- 描述：暂停并要求用户编写小程序进行实践
- 特性：
  - 请求用户贡献 2-10 行代码
  - 使用 `Learn by Doing` 格式
  - 集成 TodoList 跟踪
  - 包含贡献后的见解分享

**样式优先级**（从低到高）:
1. built-in
2. plugin
3. userSettings
4. projectSettings
5. managed (policySettings)

**关键函数**:
```typescript
export async function getAllOutputStyles(cwd: string): Promise<{...}>
export async function getOutputStyleConfig(): Promise<OutputStyleConfig | null>
export function hasCustomOutputStyle(): boolean
```

### 4.3 turnCompletionVerbs.ts (12 行) - Turn 完成动词

**核心功能**: Turn 完成消息的过去时动词

```typescript
export const TURN_COMPLETION_VERBS = [
  'Baked', 'Brewed', 'Churned', 'Cogitated',
  'Cooked', 'Crunched', 'Sautéed', 'Worked'
]
```

**用途**: 与持续时间连用，如 "Worked for 5s"

### 4.4 spinnerVerbs.ts (203 行) - 旋转器动词

**核心功能**: 加载消息的动词列表（204 个动词）

**配置系统**:
```typescript
export function getSpinnerVerbs(): string[]
```

**配置模式**:
- `mode: 'replace'` - 替换默认动词
- 默认 - 追加到默认动词列表

**默认动词列表**（部分示例）:
```typescript
export const SPINNER_VERBS = [
  'Accomplishing', 'Actioning', 'Actualizing', 'Architecting',
  'Baking', 'Beaming', "Beboppin'", 'Befuddling', 'Billowing',
  // ... 共 204 个动词
  'Working', 'Wrangling', 'Zesting', 'Zigzagging'
]
```

**设计理念**: 使用幽默、创意的动词提升用户体验

---

## 5. 安全系统常量

### 5.1 cyberRiskInstruction.ts (24 行) - 网络安全风险指令

**核心功能**: 安全相关请求的处理指令

**关键常量**:
```typescript
export const CYBER_RISK_INSTRUCTION = `
IMPORTANT: Assist with authorized security testing, defensive security, 
CTF challenges, and educational contexts. Refuse requests for destructive 
techniques, DoS attacks, mass targeting, supply chain compromise, or 
detection evasion for malicious purposes. Dual-use security tools (C2 
frameworks, credential testing, exploit development) require clear 
authorization context: pentesting engagements, CTF competitions, security 
research, or defensive use cases.
`
```

**所有权**: Safeguards 团队（David Forsythe, Kyla Guru）

**修改要求**:
1. 联系 Safeguards 团队
2. 确保经过评估
3. 获得明确批准

**安全边界**:
- ✅ 允许：授权安全测试、防御安全、CTF 挑战、教育场景
- ❌ 拒绝：破坏性技术、DoS 攻击、大规模定向、供应链攻击、恶意检测规避

---

## 6. 认证系统常量

### 6.1 oauth.ts (234 行) - OAuth 常量

**核心功能**: OAuth 配置管理

**配置类型**:
```typescript
type OauthConfigType = 'prod' | 'staging' | 'local'
```

**OAuth 作用域**:
```typescript
// Console OAuth（用于 API 密钥创建）
export const CONSOLE_OAUTH_SCOPES = [
  'org:create_api_key',
  'user:profile'
]

// Claude.ai OAuth（用于订阅用户）
export const CLAUDE_AI_OAUTH_SCOPES = [
  'user:profile',
  'user:inference',
  'user:sessions:claude_code',
  'user:mcp_servers',
  'user:file_upload'
]

// 所有作用域并集
export const ALL_OAUTH_SCOPES = [...]
```

**Beta 头**:
```typescript
export const OAUTH_BETA_HEADER = 'oauth-2025-04-20'
```

**配置结构**:
```typescript
type OauthConfig = {
  BASE_API_URL: string
  CONSOLE_AUTHORIZE_URL: string
  CLAUDE_AI_AUTHORIZE_URL: string
  CLAUDE_AI_ORIGIN: string
  TOKEN_URL: string
  API_KEY_URL: string
  ROLES_URL: string
  CONSOLE_SUCCESS_URL: string
  CLAUDEAI_SUCCESS_URL: string
  MANUAL_REDIRECT_URL: string
  CLIENT_ID: string
  OAUTH_FILE_SUFFIX: string
  MCP_PROXY_URL: string
  MCP_PROXY_PATH: string
}
```

**环境配置**:

#### 生产环境
```typescript
BASE_API_URL: 'https://api.anthropic.com'
CONSOLE_AUTHORIZE_URL: 'https://platform.claude.com/oauth/authorize'
CLAUDE_AI_AUTHORIZE_URL: 'https://claude.com/cai/oauth/authorize'
CLAUDE_AI_ORIGIN: 'https://claude.ai'
CLIENT_ID: '9d1c250a-e61b-44d9-88ed-5944d1962f5e'
```

#### 预发布环境（仅 ant 构建）
```typescript
BASE_API_URL: 'https://api-staging.anthropic.com'
CLIENT_ID: '22422756-60c9-4084-8eb7-27705fd5cf9a'
```

#### 本地开发
```typescript
BASE_API_URL: 'http://localhost:8000'
CLAUDE_AI_ORIGIN: 'http://localhost:4000'
```

**自定义 OAuth URL**:
- 环境变量：`CLAUDE_CODE_CUSTOM_OAUTH_URL`
- 允许的主机：
  - `https://beacon.claude-ai.staging.ant.dev`
  - `https://claude.fedstart.com`
  - `https://claude-staging.fedstart.com`

**MCP 客户端元数据 URL**:
```typescript
export const MCP_CLIENT_METADATA_URL = 
  'https://claude.ai/oauth/claude-code-client-metadata'
```

### 6.2 keys.ts (11 行) - GrowthBook 密钥

**核心功能**: GrowthBook 客户端密钥

**密钥逻辑**:
```typescript
export function getGrowthBookClientKey(): string
```

**密钥值**:

| 环境 | 条件 | 密钥 |
|------|------|------|
| ant | ENABLE_GROWTHBOOK_DEV | `sdk-yZQvlplybuXjYh6L` |
| ant | 默认 | `sdk-xRVcrliHIlrg4og4` |
| 外部 | - | `sdk-zAZezfDKGoZuXXKe` |

**设计**: 懒加载，确保 `ENABLE_GROWTHBOOK_DEV` 在模块加载后设置也能生效

---

## 7. API 系统常量

### 7.1 apiLimits.ts (94 行) - API 限制

**核心功能**: Anthropic API 限制定义

**最后验证**: 2025-12-22

#### 图片限制

```typescript
// 最大 base64 编码图片大小
export const API_IMAGE_MAX_BASE64_SIZE = 5 * 1024 * 1024  // 5 MB

// 目标原始图片大小（base64 编码前）
export const IMAGE_TARGET_RAW_SIZE = 3.75 MB  // 5MB * 3/4

// 客户端最大尺寸
export const IMAGE_MAX_WIDTH = 2000
export const IMAGE_MAX_HEIGHT = 2000
```

**计算原理**:
- Base64 编码增加 ~33% 大小
- 公式：`raw_size * 4/3 = base64_size`

#### PDF 限制

```typescript
// 目标原始 PDF 大小
export const PDF_TARGET_RAW_SIZE = 20 MB  // base64 后 ~27MB

// API 最大页数
export const API_PDF_MAX_PAGES = 100

// 提取阈值（超过此值提取为页面图片）
export const PDF_EXTRACT_SIZE_THRESHOLD = 3 MB

// 最大提取大小
export const PDF_MAX_EXTRACT_SIZE = 100 MB

// 单次读取最大页数
export const PDF_MAX_PAGES_PER_READ = 20

// @提及内联阈值
export const PDF_AT_MENTION_INLINE_THRESHOLD = 10
```

#### 媒体限制

```typescript
// 每个请求最大媒体项数
export const API_MAX_MEDIA_PER_REQUEST = 100
```

### 7.2 betas.ts (52 行) - Beta 头常量

**核心功能**: API Beta 头定义

**Beta 头列表**:

| 常量 | 值 | 用途 |
|------|-----|------|
| `CLAUDE_CODE_20250219_BETA_HEADER` | `claude-code-20250219` | Claude Code |
| `INTERLEAVED_THINKING_BETA_HEADER` | `interleaved-thinking-2025-05-14` | 交错思考 |
| `CONTEXT_1M_BETA_HEADER` | `context-1m-2025-08-07` | 1M 上下文 |
| `CONTEXT_MANAGEMENT_BETA_HEADER` | `context-management-2025-06-27` | 上下文管理 |
| `STRUCTURED_OUTPUTS_BETA_HEADER` | `structured-outputs-2025-12-15` | 结构化输出 |
| `WEB_SEARCH_BETA_HEADER` | `web-search-2025-03-05` | 网络搜索 |
| `TOOL_SEARCH_BETA_HEADER_1P` | `advanced-tool-use-2025-11-20` | 工具搜索（1P） |
| `TOOL_SEARCH_BETA_HEADER_3P` | `tool-search-tool-2025-10-19` | 工具搜索（3P） |
| `EFFORT_BETA_HEADER` | `effort-2025-11-24` | 努力级别 |
| `TASK_BUDGETS_BETA_HEADER` | `task-budgets-2026-03-13` | 任务预算 |
| `PROMPT_CACHING_SCOPE_BETA_HEADER` | `prompt-caching-scope-2026-01-05` | 提示缓存范围 |
| `FAST_MODE_BETA_HEADER` | `fast-mode-2026-02-01` | 快速模式 |
| `REDACT_THINKING_BETA_HEADER` | `redact-thinking-2026-02-12` | 编辑思考 |
| `TOKEN_EFFICIENT_TOOLS_BETA_HEADER` | `token-efficient-tools-2026-03-28` | Token 高效工具 |
| `SUMMARIZE_CONNECTOR_TEXT_BETA_HEADER` | `summarize-connector-text-2026-03-13` | 连接器文本摘要 |
| `AFK_MODE_BETA_HEADER` | `afk-mode-2026-01-31` | AFK 模式 |
| `CLI_INTERNAL_BETA_HEADER` | `cli-internal-2026-02-09` | CLI 内部（仅 ant） |
| `ADVISOR_BETA_HEADER` | `advisor-tool-2026-03-01` | 顾问工具 |

**特殊集合**:

#### Bedrock 额外参数
```typescript
export const BEDROCK_EXTRA_PARAMS_HEADERS = new Set([
  INTERLEAVED_THINKING_BETA_HEADER,
  CONTEXT_1M_BETA_HEADER,
  TOOL_SEARCH_BETA_HEADER_3P
])
```

#### Vertex countTokens 允许
```typescript
export const VERTEX_COUNT_TOKENS_ALLOWED_BETAS = new Set([
  CLAUDE_CODE_20250219_BETA_HEADER,
  INTERLEAVED_THINKING_BETA_HEADER,
  CONTEXT_MANAGEMENT_BETA_HEADER
])
```

### 7.3 product.ts (76 行) - 产品常量

**核心功能**: 产品 URL 和远程会话管理

**基础 URL**:
```typescript
export const PRODUCT_URL = 'https://claude.com/claude-code'
export const CLAUDE_AI_BASE_URL = 'https://claude.ai'
export const CLAUDE_AI_STAGING_BASE_URL = 'https://claude-ai.staging.ant.dev'
export const CLAUDE_AI_LOCAL_BASE_URL = 'http://localhost:4000'
```

**环境检测函数**:
```typescript
export function isRemoteSessionStaging(sessionId?: string, ingressUrl?: string): boolean
// 检测条件：sessionId 包含 '_staging_' 或 ingressUrl 包含 'staging'

export function isRemoteSessionLocal(sessionId?: string, ingressUrl?: string): boolean
// 检测条件：sessionId 包含 '_local_' 或 ingressUrl 包含 'localhost'

export function getClaudeAiBaseUrl(sessionId?: string, ingressUrl?: string): string
// 根据环境返回基础 URL

export function getRemoteSessionUrl(sessionId: string, ingressUrl?: string): string
// 获取远程会话完整 URL
// 支持 cse_→session_ 转换（临时兼容层）
```

**会话 ID 转换**:
- Worker 端点需要 `cse_*` 格式
- Claude.ai 前端需要 `session_*` 格式
- 使用 `toCompatSessionId()` 进行转换
- 由 `tengu_bridge_repl_v2_cse_shim_enabled` 功能标志控制

---

## 8. GitHub 集成常量

### 8.1 github-app.ts (144 行) - GitHub App 常量

**核心功能**: GitHub Actions 工作流模板

**导出的常量**:

| 常量 | 用途 |
|------|------|
| `PR_TITLE` | PR 标题 |
| `GITHUB_ACTION_SETUP_DOCS_URL` | 设置文档 URL |
| `WORKFLOW_CONTENT` | Claude Code 工作流 YAML |
| `PR_BODY` | PR 描述模板 |
| `CODE_REVIEW_PLUGIN_WORKFLOW_CONTENT` | 代码审查工作流 YAML |

**工作流触发条件**:
```yaml
on:
  issue_comment:
    types: [created]
  pull_request_review_comment:
    types: [created]
  issues:
    types: [opened, assigned]
  pull_request_review:
    types: [submitted]
```

**触发条件**: 包含 `@claude` 提及

**权限要求**:
```yaml
permissions:
  contents: read
  pull-requests: read
  issues: read
  id-token: write
  actions: read  # 读取 CI 结果
```

---

## 9. 错误处理常量

### 9.1 errorIds.ts (16 行) - 错误 ID

**核心功能**: 错误源跟踪 ID

**当前错误 ID**:
```typescript
export const E_TOOL_USE_SUMMARY_GENERATION_FAILED = 344
```

**设计原则**:
- 混淆标识符，用于生产环境错误跟踪
- 独立的 const 导出，优化死代码消除
- 下一个可用 ID：346

### 9.2 messages.ts (2 行) - 消息常量

**核心功能**: 消息模板

```typescript
export const NO_CONTENT_MESSAGE = '(no content)'
```

---

## 10. UI 符号常量

### 10.1 figures.ts (45 行) - Unicode 符号

**核心功能**: Unicode 符号定义

**状态指示器**:
```typescript
BLACK_CIRCLE = '⏺' / '●'  // 平台相关
BULLET_OPERATOR = '∙'
TEARDROP_ASTERISK = '✻'
UP_ARROW = '↑'  // opus 1m 合并通知
DOWN_ARROW = '↓'  // 滚动提示
LIGHTNING_BOLT = '↯'  // 快速模式指示器
```

**努力级别**:
```typescript
EFFORT_LOW = '○'      // \u25cb
EFFORT_MEDIUM = '◐'   // \u25d0
EFFORT_HIGH = '●'     // \u25cf
EFFORT_MAX = '◉'      // \u25c9 (Opus 4.6 only)
```

**媒体/触发器状态**:
```typescript
PLAY_ICON = '▶'
PAUSE_ICON = '⏸'
```

**MCP 订阅指示器**:
```typescript
REFRESH_ARROW = '↻'  // 资源更新
CHANNEL_ARROW = '←'  // 入站频道消息
INJECTED_ARROW = '→' // 跨会话注入消息
FORK_GLYPH = '⑂'     // fork 指令
```

**审查状态**:
```typescript
DIAMOND_OPEN = '◇'     // 运行中
DIAMOND_FILLED = '◆'   // 完成/失败
REFERENCE_MARK = '※'   // 离开摘要标记
```

**其他符号**:
```typescript
FLAG_ICON = '⚑'         // issue 标记
BLOCKQUOTE_BAR = '▎'    // 引用块前缀
HEAVY_HORIZONTAL = '━'  // 粗横线
```

**Bridge 状态**:
```typescript
BRIDGE_SPINNER_FRAMES = ['·|·', '·/·', '·—·', '·\·']
BRIDGE_READY_INDICATOR = '·✔︎·'
BRIDGE_FAILED_INDICATOR = '×'
```

---

## 11. 重要设计模式

### 11.1 缓存策略

**系统提示段缓存**:
```typescript
// 缓存直到 /clear 或 /compact
systemPromptSection('name', computeFn)

// 每 turn 重新计算（破坏缓存）
DANGEROUS_uncachedSystemPromptSection('name', computeFn, reason)
```

**边界标记**:
```typescript
SYSTEM_PROMPT_DYNAMIC_BOUNDARY = '__SYSTEM_PROMPT_DYNAMIC_BOUNDARY__'
```
- 之前：静态内容（可全局缓存）
- 之后：动态内容（每 turn 重新计算）

### 11.2 Feature Flags

**GrowthBook 集成**:
```typescript
import { feature } from 'bun:bundle'
import { getFeatureValue_CACHED_MAY_BE_STALE } from '../services/analytics/growthbook.js'
```

**常见模式**:
```typescript
// 构建时消除
feature('WORKFLOW_SCRIPTS') ? [WORKFLOW_TOOL_NAME] : []

// 运行时检查
getFeatureValue_CACHED_MAY_BE_STALE('tengu_attribution_header', true)
```

### 11.3 环境变量覆盖

**常见环境变量**:
- `CLAUDE_CODE_OVERRIDE_DATE` - 日期覆盖
- `CLAUDE_CODE_SIMPLE` - 简单模式
- `CLAUDE_CODE_ENTRYPOINT` - 入口点
- `USER_TYPE` - 用户类型（'ant' vs 外部）
- `CLAUDE_CODE_CUSTOM_OAUTH_URL` - 自定义 OAuth
- `ENABLE_GROWTHBOOK_DEV` - GrowthBook 开发模式

### 11.4 死代码消除 (DCE)

**模式**:
```typescript
// 内联检查，允许 bundler 消除
if (process.env.USER_TYPE === 'ant' && isUndercover()) {
  // suppress
}
```

**条件导入**:
```typescript
const module = feature('FEATURE_X')
  ? require('../module.js')
  : null
```

---

## 12. 使用场景索引

### 系统提示构建
- `prompts.ts` - 主系统提示
- `systemPromptSections.ts` - 段管理
- `outputStyles.ts` - 样式配置
- `common.ts` - 日期处理

### 工具系统
- `tools.ts` - 权限定义
- `toolLimits.ts` - 大小限制
- `files.ts` - 文件检测
- `xml.ts` - XML 标签

### 认证授权
- `oauth.ts` - OAuth 配置
- `keys.ts` - GrowthBook 密钥

### API 交互
- `apiLimits.ts` - API 限制
- `betas.ts` - Beta 头
- `product.ts` - 产品 URL

### 安全合规
- `cyberRiskInstruction.ts` - 安全指令
- `errorIds.ts` - 错误跟踪

### UI/UX
- `figures.ts` - Unicode 符号
- `spinnerVerbs.ts` - 加载动词
- `turnCompletionVerbs.ts` - 完成动词

### GitHub 集成
- `github-app.ts` - Actions 工作流

---

## 13. 关键常量快速查找

### 模型相关
```typescript
FRONTIER_MODEL_NAME = 'Claude Opus 4.6'
CLAUDE_4_5_OR_4_6_MODEL_IDS = {
  opus: 'claude-opus-4-6',
  sonnet: 'claude-sonnet-4-6',
  haiku: 'claude-haiku-4-5-20251001'
}
```

### 限制相关
```typescript
DEFAULT_MAX_RESULT_SIZE_CHARS = 50_000
MAX_TOOL_RESULT_TOKENS = 100_000
MAX_TOOL_RESULTS_PER_MESSAGE_CHARS = 200_000
API_IMAGE_MAX_BASE64_SIZE = 5 MB
API_PDF_MAX_PAGES = 100
API_MAX_MEDIA_PER_REQUEST = 100
```

### 系统边界
```typescript
SYSTEM_PROMPT_DYNAMIC_BOUNDARY = '__SYSTEM_PROMPT_DYNAMIC_BOUNDARY__'
```

### OAuth 作用域
```typescript
CLAUDE_AI_INFERENCE_SCOPE = 'user:inference'
CLAUDE_AI_PROFILE_SCOPE = 'user:profile'
CONSOLE_SCOPE = 'org:create_api_key'
```

---

## 14. 总结

constants/ 目录是 Claude Code 系统的配置中枢，包含：

- **21 个文件**，覆盖所有核心系统配置
- **914 行**的 prompts.ts 是最大文件，包含完整的系统提示构建逻辑
- **204 个** spinner verbs 提供幽默的加载体验
- **107 种**二进制扩展名检测
- **18 个** Beta 头定义
- **完整的** OAuth 配置系统（生产/预发布/本地）
- **精细的**工具权限管理系统
- **多层**缓存策略（静态/动态分离）

这个系统的设计核心是：
1. **性能优化**: 通过缓存、memoization、DCE
2. **可配置性**: 通过环境变量、GrowthBook、设置文件
3. **安全性**: 通过权限控制、安全指令、OAuth 作用域
4. **可维护性**: 通过模块化、类型安全、清晰的命名

---

*文档持续更新中...*
