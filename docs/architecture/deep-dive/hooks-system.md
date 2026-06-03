# Hook 系统深度技术文档

> 基于逐行代码分析的完整技术文档  
> **探索完成时间**: 2026 年 4 月 1 日  
> **核心文件**: toolHooks.ts (650 行), stopHooks.ts, types/hooks.ts

---

## 1. Hook 系统概述

Hook 系统是 Claude Code 的核心扩展机制，允许用户在特定事件点执行自定义命令、LLM prompt、HTTP 请求或 TypeScript 回调函数。系统支持**27 种不同的事件类型**，覆盖从工具执行、会话管理到权限控制的完整生命周期。

### 1.1 设计原则

- **非侵入式扩展**: 不修改核心逻辑，通过 Hook 注入自定义行为
- **并行执行**: 同一事件的所有 Hook 并行执行
- **独立超时**: 每个 Hook 独立的超时控制
- **类型安全**: 完整的 TypeScript 类型定义
- **错误隔离**: 单个 Hook 失败不影响其他 Hook 或核心流程

---

## 2. Hook 类型系统

### 2.1 Hook 事件类型 (HookEvent)

```typescript
type HookEvent =
  // 工具执行相关
  | 'PreToolUse'        // 工具执行前
  | 'PostToolUse'       // 工具执行后
  | 'PostToolUseFailure' // 工具执行失败后
  | 'PermissionRequest'  // 权限对话框显示时
  | 'PermissionDenied'   // 自动模式分类器拒绝后
  
  // 会话生命周期
  | 'SessionStart'       // 新会话启动
  | 'SessionEnd'         // 会话结束
  | 'Stop'               // Claude 回复结束前
  | 'StopFailure'        // 因 API 错误结束
  
  // 用户交互
  | 'UserPromptSubmit'   // 用户提交 prompt
  
  // 子代理
  | 'SubagentStart'
  | 'SubagentStop'
  
  // 对话管理
  | 'PreCompact'
  | 'PostCompact'
  
  // 团队/任务管理
  | 'TeammateIdle'
  | 'TaskCreated'
  | 'TaskCompleted'
  
  // MCP 集成
  | 'Elicitation'
  | 'ElicitationResult'
  
  // 配置/环境
  | 'ConfigChange'
  | 'InstructionsLoaded'
  | 'Setup'
  | 'WorktreeCreate'
  | 'WorktreeRemove'
  | 'CwdChanged'
  | 'FileChanged'
  
  // 通知
  | 'Notification'
```

### 2.2 Hook 命令类型

#### Bash 命令 Hook

```typescript
{
  type: 'command',
  command: string,          // shell 命令
  if?: string,              // 权限规则语法过滤
  shell?: 'bash' | 'powershell',
  timeout?: number,         // 超时（秒）
  statusMessage?: string,   // 自定义状态消息
  once?: boolean,           // 仅执行一次
  async?: boolean,          // 后台执行
  asyncRewake?: boolean     // 后台执行并在退出码 2 时唤醒
}
```

#### Prompt Hook

```typescript
{
  type: 'prompt',
  prompt: string,           // LLM prompt
  if?: string,
  timeout?: number,
  model?: string,           // 使用的模型
  statusMessage?: string,
  once?: boolean
}
```

#### Agent Hook

```typescript
{
  type: 'agent',
  prompt: string,           // 验证描述
  if?: string,
  timeout?: number,         // 默认 60 秒
  model?: string,           // 使用的模型
  statusMessage?: string,
  once?: boolean
}
```

#### HTTP Hook

```typescript
{
  type: 'http',
  url: string,              // POST 请求 URL
  if?: string,
  timeout?: number,
  headers?: Record<string, string>,
  allowedEnvVars?: string[],
  statusMessage?: string,
  once?: boolean
}
```

#### Callback Hook (内存回调)

```typescript
{
  type: 'callback',
  callback: (
    input: unknown,
    toolUseID: string,
    signal: AbortSignal,
    hookIndex: number,
    context: HookContext
  ) => Promise<HookJSONOutput>,
  timeout?: number,
  internal?: boolean
}
```

#### Function Hook (内存回调)

```typescript
{
  type: 'function',
  id?: string,
  timeout?: number,         // 默认 5000ms
  callback: (
    messages: Message[],
    signal: AbortSignal
  ) => boolean | Promise<boolean>,
  errorMessage: string,
  statusMessage?: string
}
```

---

## 3. Hook 注册机制

### 3.1 Hook 来源（按优先级）

```
优先级 0: User Settings (~/.claude/settings.json)
优先级 1: Project Settings (.claude/settings.json)
优先级 2: Local Settings (.claude/settings.local.json)
特殊：Policy Settings (远程管理)
优先级 999: Plugin Hooks
优先级 999: Skill Hooks
特殊：Session Hooks (运行时动态)
优先级 999: Built-in Hooks (内部)
```

### 3.2 Hook 配置结构

```json
{
  "PreToolUse": [
    {
      "matcher": "Write",
      "hooks": [
        {
          "type": "command",
          "command": "echo 'About to write'",
          "timeout": 30
        }
      ]
    }
  ],
  "Stop": [
    {
      "matcher": "",
      "hooks": [
        {
          "type": "http",
          "url": "https://example.com/hook",
          "headers": {
            "Authorization": "Bearer $MY_TOKEN"
          },
          "allowedEnvVars": ["MY_TOKEN"]
        }
      ]
    }
  ]
}
```

### 3.3 去重机制

```typescript
function hookDedupKey(m: MatchedHook, payload: string): string {
  return `${m.pluginRoot ?? m.skillRoot ?? ''}\0${payload}`
}

// Command hook payload
const payload = `${hook.shell ?? 'bash'}\0${hook.command}\0${hook.if ?? ''}`

// Prompt/Agent hook payload
const payload = `${hook.prompt}\0${hook.model ?? ''}\0${hook.if ?? ''}`

// HTTP hook payload
const payload = `${hook.url}\0${JSON.stringify(hook.headers)}\0${hook.if ?? ''}`
```

---

## 4. Hook 执行模型

### 4.1 完整执行时序

```
用户输入
  ↓
[UserPromptSubmit Hooks]
  ↓
[SessionStart Hooks] (首次)
  ↓
[Setup Hooks] (首次)
  ↓
┌──────────────────────────────┐
│ Query Loop                   │
│                              │
│ [PreToolUse Hooks] → 权限检查  │
│     ↓                        │
│   工具执行                   │
│     ↓                        │
│ [PostToolUse / Failure Hooks]│
│     ↓                        │
│ [Stop Hooks]                 │
│     ↓                        │
│ [TeammateIdle Hooks]         │
│     ↓                        │
│ [TaskCompleted Hooks]        │
└──────────────────────────────┘
  ↓
[SessionEnd Hooks]
```

### 4.2 并行执行架构

```typescript
// 所有匹配的 hooks 并行执行
const hookPromises = matchingHooks.map(async function* (
  { hook, pluginRoot, pluginId, skillRoot },
  hookIndex,
): AsyncGenerator<HookResult> {
  // 每个 hook 独立执行
  if (hook.type === 'command') {
    yield execCommandHook({...})
  } else if (hook.type === 'prompt') {
    yield execPromptHook({...})
  }
  // ...
})

// 并发执行所有 generators
const allResults = all(hookPromises)
```

### 4.3 独立超时控制

```typescript
// 每个 hook 独立的超时
const hookTimeoutMs = hook.timeout ? hook.timeout * 1000 : timeoutMs
const { signal: abortSignal, cleanup } = createCombinedAbortSignal(
  parentSignal,
  { timeoutMs: hookTimeoutMs }
)

try {
  yield executeHook(abortSignal)
} finally {
  cleanup()
}
```

**默认超时：**
- Command/Prompt: 10 分钟
- Agent: 60 秒
- HTTP: 10 分钟
- Function: 5 秒
- SessionEnd: 1.5 秒

---

## 5. Hook 修改能力

### 5.1 修改输入 (PreToolUse)

```typescript
{
  hookSpecificOutput: {
    hookEventName: 'PreToolUse',
    updatedInput: {
      filePath: '/new/path.txt',
      content: 'modified'
    }
  }
}
```

### 5.2 修改输出 (PostToolUse)

```typescript
{
  hookSpecificOutput: {
    hookEventName: 'PostToolUse',
    updatedMCPToolOutput: {...}
  }
}
```

### 5.3 修改能力矩阵

| Hook 类型 | updatedInput | updatedMCPOutput | additionalContext | watchPaths |
|-----------|--------------|------------------|-------------------|------------|
| PreToolUse | ✅ | ❌ | ✅ | ❌ |
| PostToolUse | ❌ | ✅ | ✅ | ❌ |
| SessionStart | ❌ | ❌ | ✅ | ✅ |
| CwdChanged | ❌ | ❌ | ❌ | ✅ |
| PermissionRequest | ✅ (via updatedPermissions) | ❌ | ✅ | ❌ |

---

## 6. Hook 阻止机制

### 6.1 退出码语义

| 退出码 | 含义 | 行为 |
|--------|------|------|
| 0 | 成功 | 继续执行 |
| 2 | 阻塞错误 | 阻止执行，显示 stderr |
| 其他 | 非阻塞错误 | 继续，显示错误 |

### 6.2 阻止决策聚合

```typescript
const aggregated: AggregatedHookResult = {
  blockingErrors: [],
  preventContinuation: false,
}

for await (const result of all(hookGenerators)) {
  if (result.blockingError) {
    aggregated.blockingErrors.push(result.blockingError)
  }
  if (result.preventContinuation) {
    aggregated.preventContinuation = true
  }
}

// blocking error 优先
if (aggregated.blockingErrors.length > 0) {
  return { blockingErrors: aggregated.blockingErrors }
}
```

---

## 7. Hook 与权限系统集成

### 7.1 权限决策类型

```typescript
type PermissionBehavior = 'allow' | 'deny' | 'ask'
```

### 7.2 优先级规则

```typescript
// Hook 'allow' 不绕过 settings.json deny/ask 规则
if (hookPermissionResult?.behavior === 'allow') {
  const ruleCheck = await checkRuleBasedPermissions(...)
  
  if (ruleCheck?.behavior === 'deny') {
    // settings.json deny 覆盖 hook allow
    return { decision: ruleCheck }
  }
  
  return { decision: hookPermissionResult }
}

// Hook 'deny' → 直接拒绝
if (hookPermissionResult?.behavior === 'deny') {
  return { decision: hookPermissionResult }
}
```

### 7.3 PermissionRequest Hook

```typescript
{
  hookSpecificOutput: {
    hookEventName: 'PermissionRequest',
    decision: {
      behavior: 'allow',
      updatedInput?: {...},
      updatedPermissions?: [...]
    }
  }
}
```

---

## 8. Hook 错误处理

### 8.1 错误类型

```typescript
type HookOutcome = 
  | 'success'
  | 'blocking'
  | 'non_blocking_error'
  | 'cancelled'
```

### 8.2 错误处理流程

```typescript
try {
  const result = await executeHook(signal)
  
  if (result.code === 2) {
    return {
      blockingError: { blockingError: stderr },
      outcome: 'blocking'
    }
  }
  
  if (result.code !== 0) {
    return {
      message: createAttachmentMessage({
        type: 'hook_non_blocking_error',
        stderr,
        exitCode: result.code
      }),
      outcome: 'non_blocking_error'
    }
  }
  
  return { outcome: 'success' }
} catch (error) {
  if (signal.aborted) {
    return { outcome: 'cancelled' }
  }
  
  return {
    message: createAttachmentMessage({
      type: 'hook_error_during_execution',
      content: formatError(error)
    }),
    outcome: 'non_blocking_error'
  }
}
```

### 8.3 超时处理

```typescript
function createCombinedAbortSignal(
  parentSignal?: AbortSignal,
  options?: { timeoutMs?: number }
) {
  const controller = new AbortController()
  
  parentSignal?.addEventListener('abort', () => {
    controller.abort(parentSignal.reason)
  })
  
  if (options?.timeoutMs) {
    setTimeout(() => {
      controller.abort(new AbortError('Timeout'))
    }, options.timeoutMs)
  }
  
  return { signal: controller.signal, cleanup }
}
```

---

## 9. Hook 进度报告

### 9.1 进度事件

```typescript
type HookProgressEvent = {
  type: 'hook_progress',
  hookEvent: HookEvent,
  hookName: string,
  command: string,
  promptText?: string,
  statusMessage?: string
}
```

### 9.2 进度轮询

```typescript
function startHookProgressInterval(params) {
  let lastEmittedOutput = ''
  
  const interval = setInterval(() => {
    void params.getOutput().then(({ stdout, stderr, output }) => {
      if (output === lastEmittedOutput) return
      lastEmittedOutput = output
      
      emitHookProgress({
        hookId: params.hookId,
        hookName: params.hookName,
        stdout,
        stderr,
        output,
      })
    })
  }, 1000)
  
  return () => clearInterval(interval)
}
```

### 9.3 持续时间跟踪

```typescript
const hookStartMs = Date.now()
const result = await executeHook(...)
const durationMs = Date.now() - hookStartMs

// 注入到 attachment
if (result.message?.type === 'attachment') {
  result.message.attachment.durationMs = durationMs
}
```

---

## 10. 环境变量插值

### 10.1 HTTP Hook Headers

```json
{
  "Authorization": "Bearer $API_TOKEN",
  "X-Custom-Header": "${CUSTOM_VAR}"
}
```

### 10.2 插值实现

```typescript
function interpolateEnvVars(value, allowedEnvVars) {
  return value.replace(
    /\$\{?([A-Z_][A-Z0-9_]*)\}?/g,
    (_, varName) => {
      if (!allowedEnvVars.has(varName)) return ''
      return process.env[varName] ?? ''
    }
  )
}
```

### 10.3 安全限制

- 只允许白名单环境变量
- HTTP Hook 需要显式声明 `allowedEnvVars`
- Plugin Hook 自动允许 `CLAUDE_PLUGIN_ROOT`

---

## 11. If 条件语法

### 11.1 权限规则语法

- `Bash(git *)`: 仅 git 命令
- `Read(*.ts)`: 仅 .ts 文件
- `Write(src/**)`: 仅 src/ 目录
- `Glob(**/*.md)`: 仅 markdown 文件

### 11.2 匹配实现

```typescript
function matchesHookIfCondition(
  hookIf: string | undefined,
  toolName: string,
  toolInput: unknown,
  permissionContext: ToolPermissionContext
): boolean {
  if (!hookIf) return true
  
  // 解析权限规则语法
  const rule = parsePermissionRule(hookIf)
  if (!rule) return false
  
  // 检查工具匹配
  return checkRuleMatch(rule, toolName, toolInput, permissionContext)
}
```

---

## 12. Plugin Hooks vs User Hooks

### 12.1 区别对比

| 特性 | User Hooks | Plugin Hooks |
|------|-----------|--------------|
| 来源 | `~/.claude/settings.json` | `~/.claude/plugins/*/hooks.json` |
| 优先级 | 高 (0-2) | 低 (999) |
| 环境变量 | 普通 | `CLAUDE_PLUGIN_ROOT` |
| 去重命名空间 | `''` | `pluginRoot` |

### 12.2 Plugin Hook 特殊能力

```json
{
  "PreToolUse": [
    {
      "matcher": "Write",
      "hooks": [
        {
          "type": "command",
          "command": "${CLAUDE_PLUGIN_ROOT}/scripts/hook.sh"
        }
      ]
    }
  ]
}
```

---

## 13. 异步 Hook 模型

### 13.1 异步配置

```json
{
  "Stop": [
    {
      "matcher": "",
      "hooks": [
        {
          "type": "command",
          "command": "npm run build:watch",
          "async": true,
          "asyncTimeout": 30000,
          "asyncRewake": true
        }
      ]
    }
  ]
}
```

### 13.2 异步执行

```typescript
// 注册到异步注册表
registerPendingAsyncHook({
  processId,
  hookId,
  asyncResponse,
  shellCommand,
})

// 后台执行，不阻塞
if (asyncRewake) {
  void shellCommand.result.then(result => {
    if (result.code === 2) {
      // 唤醒模型
      enqueuePendingNotification({...})
    }
  })
}
```

### 13.3 唤醒机制

- 退出码 2 触发唤醒
- 通过 `pendingAsyncHookNotifications` 队列
- 下次查询时注入为 attachment

---

## 14. 实际使用示例

### 14.1 PreToolUse - 安全审计

```json
{
  "PreToolUse": [
    {
      "matcher": "Write",
      "hooks": [
        {
          "type": "command",
          "command": "node audit.js '$ARGUMENTS'",
          "timeout": 30,
          "statusMessage": "Running security audit..."
        }
      ]
    }
  ]
}
```

### 14.2 Stop - 验证测试

```json
{
  "Stop": [
    {
      "matcher": "",
      "hooks": [
        {
          "type": "agent",
          "prompt": "Verify all tests passed and lint is clean",
          "timeout": 120,
          "model": "claude-sonnet-4-6",
          "statusMessage": "Verifying tests..."
        }
      ]
    }
  ]
}
```

### 14.3 PostToolUse - MCP 输出转换

```json
{
  "PostToolUse": [
    {
      "matcher": "mcp:*",
      "hooks": [
        {
          "type": "callback",
          "callback": (input, toolUseID, signal, hookIndex, context) => {
            const output = context.mcpToolOutput
            return {
              updatedMCPToolOutput: transformOutput(output)
            }
          }
        }
      ]
    }
  ]
}
```

### 14.4 SessionStart - 加载上下文

```json
{
  "SessionStart": [
    {
      "matcher": "",
      "hooks": [
        {
          "type": "command",
          "command": "cat .claude/context.md",
          "statusMessage": "Loading context..."
        }
      ]
    }
  ]
}
```

### 14.5 Async Hook - 后台监控

```json
{
  "Stop": [
    {
      "matcher": "",
      "hooks": [
        {
          "type": "command",
          "command": "npm run build:watch",
          "async": true,
          "asyncRewake": true
        }
      ]
    }
  ]
}
```

### 14.6 Function Hook - 强制结构化输出

```typescript
addFunctionHook(
  setAppState,
  agentId,
  'Stop',
  '',
  messages => hasSuccessfulToolCall(messages, 'StructuredOutput'),
  'Must call StructuredOutput before finishing',
  { timeout: 5000 }
)
```

---

## 附录 A: Hook 事件完整能力矩阵

| 事件 | 阻塞 | 修改输入 | 修改输出 | 异步 | 默认超时 |
|------|------|----------|----------|------|----------|
| PreToolUse | ✅ | ✅ | ❌ | ✅ | 10m |
| PostToolUse | ❌ | ❌ | ✅ | ✅ | 10m |
| PostToolUseFailure | ❌ | ❌ | ❌ | ✅ | 10m |
| Stop | ✅ | ❌ | ❌ | ✅ | 10m |
| SessionStart | ❌ | ❌ | ❌ | ✅ | 10m |
| SessionEnd | ❌ | ❌ | ❌ | ❌ | 1.5s |
| UserPromptSubmit | ✅ | ❌ | ❌ | ✅ | 10m |
| PermissionRequest | ✅ | ✅ | ❌ | ✅ | 10m |
| PreCompact | ✅ | ❌ | ❌ | ✅ | 10m |
| PostCompact | ❌ | ❌ | ❌ | ✅ | 10m |
| FileChanged | ❌ | ❌ | ❌ | ✅ | 10m |
| CwdChanged | ❌ | ❌ | ❌ | ✅ | 10m |

---

## 附录 B: 最佳实践

1. **使用 If 条件**: 避免不必要执行，提高性能
2. **设置合理超时**: 防止阻塞，建议 30-120 秒
3. **使用异步 Hook**: 处理长时间任务（watch、server）
4. **最小权限原则**: 只请求必要环境变量
5. **输入验证**: 始终验证 `$ARGUMENTS`，防止注入
6. **错误处理**: 使用退出码 2 表示阻塞错误
7. **状态消息**: 提供清晰的 `statusMessage` 改善 UX

---

## 附录 C: 故障排除

### Hook 未执行

**检查清单：**
1. 工作区信任检查
2. 检查 `allowManagedHooksOnly` 策略
3. 检查 If 条件匹配
4. 启用详细日志：`CLAUDE_CODE_VERBOSE=true`
5. 检查 Hook 语法（JSON 格式）

### Hook 超时

**解决方案：**
1. 增加 `timeout` 值
2. 检查是否死锁
3. 使用异步执行
4. 优化命令性能

### Hook 修改未生效

**检查：**
1. 确认 Hook 类型支持修改（PreToolUse 改输入，PostToolUse 改输出）
2. 检查返回格式（`hookSpecificOutput`）
3. 验证字段名称（`updatedInput` / `updatedMCPToolOutput`）

---

## 附录 D: 性能考虑

### Hook 执行时间

```
典型执行时间：
- Command Hook: 100ms - 5s
- Prompt Hook: 1s - 10s
- Agent Hook: 5s - 60s
- HTTP Hook: 50ms - 2s
- Callback Hook: 1ms - 100ms
```

### 并行优化

- 同一事件的所有 Hook 并行执行
- 总执行时间 = max(单个 Hook 时间)
- 建议：避免过多 Hook（>10 个）

### 内存考虑

- Function Hook 常驻内存
- Callback Hook 会话期间有效
- 异步 Hook 后台进程

---

*文档持续更新中...*
