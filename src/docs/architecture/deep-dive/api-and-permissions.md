# API 与权限系统深度技术文档

> 基于逐行代码分析的完整技术文档  
> **探索完成时间**: 2026 年 4 月 1 日  
> **核心文件**: services/api/claude.ts, withRetry.ts, services/tools/permissions.ts

---

## 1. API 层概述

API 层提供与 Anthropic API、AWS Bedrock、GCP Vertex、Azure Foundry 的完整集成，支持流式处理、重试逻辑、Fast Mode 和持久重试模式。

### 1.1 多 Provider 支持

1. **First-party API**: 直接 Anthropic API
2. **AWS Bedrock**: 凭证刷新、区域选择
3. **GCP Vertex**: Google Auth、区域映射
4. **Azure Foundry**: Azure AD Token Provider

---

## 2. API 客户端实现

### 2.1 关键功能

- **流式支持**: 基于 async generator 的流式响应
- **Beta Headers**: 动态 beta 功能启用
- **Thinking 支持**: 扩展 thinking 带预算控制
- **Fast Mode**: 低延迟模式带回退逻辑
- **Prompt 缓存**: 1 小时缓存范围支持
- **上下文管理**: API 端上下文窗口管理
- **Advisor 模式**: 多模型顾问集成

### 2.2 Extra Body 参数

```typescript
export function getExtraBodyParams(betaHeaders?: string[]): JsonObject {
  const extraBodyStr = process.env.CLAUDE_CODE_EXTRA_BODY
  let result: JsonObject = {}

  if (extraBodyStr) {
    try {
      const parsed = safeParseJSON(extraBodyStr)
      if (parsed && typeof parsed === 'object' && !Array.isArray(parsed)) {
        result = { ...(parsed as JsonObject) }  // 浅克隆以避免缓存中毒
      }
    } catch (error) {
      logForDebugging(`Error parsing CLAUDE_CODE_EXTRA_BODY: ${errorMessage(error)}`)
    }
  }

  // 从 beta headers 添加 Bedrock 特定参数
  // ...
  return result
}
```

---

## 3. 重试逻辑

### 3.1 重试配置

```typescript
const DEFAULT_MAX_RETRIES = 10
const FLOOR_OUTPUT_TOKENS = 3000
const MAX_529_RETRIES = 3
export const BASE_DELAY_MS = 500
```

### 3.2 前台与后台重试

```typescript
const FOREGROUND_529_RETRY_SOURCES = new Set<QuerySource>([
  'repl_main_thread',
  'repl_main_thread:outputStyle:custom',
  'sdk',
  'agent:custom',
  'compact',
  'side_question',
  'auto_mode',  // 安全分类器
  // ...
])

function shouldRetry529(querySource: QuerySource | undefined): boolean {
  return (
    querySource === undefined || FOREGROUND_529_RETRY_SOURCES.has(querySource)
  )
}
```

### 3.3 持久重试模式 (无人值守会话)

```typescript
// CLAUDE_CODE_UNATTENDED_RETRY: 用于无人值守会话 (仅限 ant)
// 使用更高的回退和定期保活生成无限重试 429/529
const PERSISTENT_MAX_BACKOFF_MS = 5 * 60 * 1000
const PERSISTENT_RESET_CAP_MS = 6 * 60 * 60 * 1000
const HEARTBEAT_INTERVAL_MS = 30_000

function isPersistentRetryEnabled(): boolean {
  return feature('UNATTENDED_RETRY')
    ? isEnvTruthy(process.env.CLAUDE_CODE_UNATTENDED_RETRY)
    : false
}
```

### 3.4 Fast Mode 回退

```typescript
if (
  wasFastModeActive &&
  !isPersistentRetryEnabled() &&
  error instanceof APIError &&
  (error.status === 429 || is529Error(error))
) {
  const overageReason = error.headers?.get(
    'anthropic-ratelimit-unified-overage-disabled-reason',
  )
  if (overageReason !== null && overageReason !== undefined) {
    handleFastModeOverageRejection(overageReason)
    retryContext.fastMode = false
    continue
  }

  const retryAfterMs = getRetryAfterMs(error)
  if (retryAfterMs !== null && retryAfterMs < SHORT_RETRY_THRESHOLD_MS) {
    // 短 retry-after: 等待并用仍激活的 fast mode 重试
    await sleep(retryAfterMs, options.signal, { abortError })
    continue
  }
  // 长 retry-after: 进入冷却（切换到标准速度模型）
  const cooldownMs = Math.max(
    retryAfterMs ?? DEFAULT_FAST_MODE_FALLBACK_HOLD_MS,
    MIN_COOLDOWN_MS,
  )
  triggerFastModeCooldown(Date.now() + cooldownMs, cooldownReason)
  if (isFastModeEnabled()) {
    retryContext.fastMode = false
  }
  continue
}
```

### 3.5 重试延迟计算

```typescript
export function getRetryDelay(
  attempt: number,
  retryAfterHeader?: string | null,
  maxDelayMs = 32000,
): number {
  if (retryAfterHeader) {
    const seconds = parseInt(retryAfterHeader, 10)
    if (!isNaN(seconds)) {
      return seconds * 1000  // 遵守 Retry-After header
    }
  }

  // 带抖动的指数退避
  const baseDelay = Math.min(
    BASE_DELAY_MS * Math.pow(2, attempt - 1),
    maxDelayMs,
  )
  const jitter = Math.random() * 0.25 * baseDelay
  return baseDelay + jitter
}
```

### 3.6 529 错误检测

```typescript
export function is529Error(error: unknown): boolean {
  if (!(error instanceof APIError)) {
    return false
  }
  return (
    error.status === 529 ||
    // SDK 有时在流式传输期间无法传递 529 状态
    (error.message?.includes('"type":"overloaded_error"') ?? false)
  )
}
```

---

## 4. 错误处理

### 4.1 错误分类

20+ 种错误分类：
- `aborted`
- `api_timeout`
- `rate_limit`
- `server_overload`
- `authentication_error`
- `permission_error`
- `not_found_error`
- `invalid_request_error`
- ...

### 4.2 连接错误详情提取

```typescript
// 遍历 error.cause 链提取详细信息
function extractConnectionErrorDetails(error: unknown): string | null {
  // ...
}
```

### 4.3 SSL 错误代码识别

20+ 种 OpenSSL 错误码识别

### 4.4 HTML 错误页面清理

CloudFlare 错误页处理

---

## 5. 流式处理

### 5.1 流式事件解析

```typescript
// 完整的流式事件解析
type StreamEvent =
  | { type: 'text', text: string }
  | { type: 'thinking', thinking: string }
  | { type: 'tool_use', toolUse: ToolUseBlock }
  | { type: 'connector_text', text: string }
```

### 5.2 Thinking 内容支持

```typescript
// Thinking content 支持
type ThinkingConfig =
  | { type: 'adaptive' }
  | { type: 'enabled', budgetTokens: number }
  | { type: 'disabled' }
```

---

## 6. 权限系统架构

### 6.1 权限模式层次

```typescript
export type PermissionMode =
  | 'acceptEdits'      // 自动批准安全工作区文件编辑
  | 'bypassPermissions' // 自动批准所有（安全检查除外）
  | 'default'          // 询问所有
  | 'dontAsk'          // 自动拒绝所有
  | 'plan'             // 只读模式
  | 'auto'             // AI 分类器决策
  | 'bubble'           // 将提示冒泡到父终端
```

### 6.2 权限决策管道

**10+ 步骤决策流程**：

```
步骤 1a: Deny 规则检查 → 拒绝
步骤 1b: Ask 规则检查 → 询问
步骤 1c: 工具特定检查（checkPermissions）
步骤 1d: 用户交互需求检查
步骤 1e: 内容特定 Ask 规则
步骤 1f: 安全检查（.git/, .claude/, shell configs）
步骤 1g: 模式检查（bypassPermissions/plan）
步骤 1h: Allow 规则检查
步骤 2: 模式转换（dontAsk→deny, auto→classifier）
步骤 3: Headless 模式处理
```

### 6.3 自动模式分类器

**两阶段 XML 架构**（Fast + Thinking）：

```typescript
async function classifyYoloAction(messages, action, tools, permissionContext, signal) {
  // Stage 1: 快速分类（廉价模型）
  const stage1Result = await callClassifier(messages, action, 'fast-model')
  
  if (stage1Result.confidence === 'high') {
    return stage1Result
  }
  
  // Stage 2: 深度思考（昂贵模型）
  const stage2Result = await callClassifier(messages, action, 'thinking-model')
  
  return stage2Result
}
```

**Stage 1 特征**：
- 64 tokens
- stop_sequences
- 立即决策

**Stage 2 特征**：
- 4096 tokens
- chain-of-thought
- 减少误报

### 6.4 Transcript 序列化

```typescript
// 仅用户消息 + 助手工具调用
function serializeTranscript(messages: Message[]): string {
  // ...
}
```

### 6.5 CLAUDE.md 集成

```typescript
// 作为用户意图
const claudeMdContent = await loadClaudeMd()
```

### 6.6 acceptEdits 快速路径

```typescript
// 避免分类器 API 调用
if (mode === 'acceptEdits' && isSafeEdit(input)) {
  return { behavior: 'allow' }
}
```

### 6.7 安全工具 allowlist

```typescript
// 跳过分类器
const SAFE_TOOLS = new Set(['Read', 'Glob', 'Grep', ...])
if (SAFE_TOOLS.has(toolName)) {
  return { behavior: 'allow' }
}
```

---

## 7. 拒绝追踪与熔断

### 7.1 拒绝限制

```typescript
const DENIAL_LIMITS = {
  maxConsecutive: 3,  // 连续拒绝限制
  maxTotal: 20,       // 总拒绝限制
}
```

### 7.2 拒绝追踪状态

```typescript
type DenialTrackingState = {
  consecutiveDenials: number
  totalDenials: number
}

function recordDenial(state: DenialTrackingState): DenialTrackingState {
  return {
    consecutiveDenials: state.consecutiveDenials + 1,
    totalDenials: state.totalDenials + 1,
  }
}

function shouldFallbackToPrompting(state: DenialTrackingState): boolean {
  return (
    state.consecutiveDenials >= DENIAL_LIMITS.maxConsecutive ||
    state.totalDenials >= DENIAL_LIMITS.maxTotal
  )
}
```

### 7.3 Iron Gate 机制

```typescript
// 分类器不可用时 Fail Closed/Fail Open 切换
if (classifierUnavailable) {
  if (feature('IRON_GATE')) {
    return { behavior: 'ask' }  // Fail Closed
  } else {
    return { behavior: 'allow' }  // Fail Open
  }
}
```

### 7.4 成功重置

```typescript
// 成功重置连续计数
if (decision.behavior === 'allow') {
  state.consecutiveDenials = 0
}
```

---

## 8. 安全规则系统

### 8.1 敏感路径保护

```typescript
const SENSITIVE_PATHS = [
  '.git/',
  '.claude/',
  '.vscode/',
  // shell configs
]

function isSensitivePath(filePath: string): boolean {
  return SENSITIVE_PATHS.some(path => filePath.includes(path))
}
```

### 8.2 危险 Bash 模式匹配

**4 类危险命令**：

1. **破坏性**: `rm -rf`, `drop table`, `delete from`
2. **外部代码**: `curl | bash`, `wget | sh`
3. **持久化**: `systemctl enable`, `crontab`
4. **安全削弱**: `setenforce 0`, `ufw disable`

### 8.3 PowerShell 特定保护

```typescript
const POWERSHELL_PROTECTED = [
  'iex', 'iwr',  // 代码执行
  'Remove-Item',  // 删除
  '$PROFILE',     // 配置文件
  // ...
]
```

### 8.4 内容特定规则

```typescript
// Bash(npm publish:*), Write(/src/*.ts)
function matchesContentRule(rule: string, toolName: string, input: unknown): boolean {
  // ...
}
```

---

## 9. Hook 集成

### 9.1 PermissionRequest Hooks

```typescript
// 为 Headless Agent 提供允许/拒绝机会
type PermissionRequestHook = {
  type: 'callback'
  callback: (input, toolUseID, signal) => Promise<{
    behavior: 'allow' | 'deny' | 'ask'
    updatedInput?: unknown
  }>
}
```

### 9.2 Hook 持久化

```typescript
// Hook 可持久化权限更新
if (hookResult.updatedPermissions) {
  await updatePermissions(hookResult.updatedPermissions)
}
```

### 9.3 Hook 中断执行

```typescript
// Hook 可中断执行
if (hookResult.preventContinuation) {
  return { behavior: 'deny', reason: 'hook_blocked' }
}
```

---

## 10. 环境变量参考

### 10.1 API 相关

- `CLAUDE_CODE_EXTRA_BODY`: Extra body params
- `CLAUDE_CODE_MAX_OUTPUT_TOKENS`: 覆盖最大输出 tokens
- `CLAUDE_CODE_UNATTENDED_RETRY`: 启用持久重试

### 10.2 权限相关

- `CLAUDE_CODE_PERMISSION_MODE`: 覆盖权限模式
- `CLAUDE_CODE_AUTO_MODE_ENABLED`: 启用自动模式

### 10.3 重试相关

- `CLAUDE_CODE_MAX_RETRIES`: 最大重试次数
- `CLAUDE_CODE_RETRY_AFTER`: 覆盖 Retry-After

---

## 11. 关键指标事件

### 11.1 API 指标

- `tengu_api_call`: API 调用
- `tengu_api_error`: API 错误
- `tengu_api_retry`: API 重试
- `tengu_api_success`: API 成功

### 11.2 权限指标

- `tengu_permission_check`: 权限检查
- `tengu_permission_allow`: 权限允许
- `tengu_permission_deny`: 权限拒绝
- `tengu_auto_mode_classify`: 自动模式分类

### 11.3 重试指标

- `tengu_retry_start`: 重试开始
- `tengu_retry_success`: 重试成功
- `tengu_retry_exhausted`: 重试用尽

---

## 12. 性能优化

### 12.1 连接池

- **Keep-Alive**: 持久连接
- **连接复用**: 避免重复建立连接
- **超时控制**: 合理的超时设置

### 12.2 缓存策略

- **Prompt 缓存**: 1 小时缓存范围
- **Token 缓存**: 避免重复计算
- **响应缓存**: 可缓存响应

### 12.3 流式优化

- **渐进式处理**: 边接收边处理
- **背压控制**: 避免内存爆炸
- **取消支持**: 及时中止不需要的请求

---

*文档持续更新中...*
