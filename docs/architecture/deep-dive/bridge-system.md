# Bridge 系统深度技术文档

> 基于逐行代码分析的完整技术文档  
> **探索完成时间**: 2026 年 4 月 1 日  
> **核心文件**: bridge/ 目录下 20+ 文件

---

## 1. Bridge 系统架构概览

### 1.1 系统职责

Bridge 系统是 Claude Code 的**远程桥接核心**，负责：
- 远程会话的创建和管理
- JWT 认证和授权
- 消息传递机制
- 轮询配置和长轮询
- 入站消息和附件处理
- 权限回调
- 容量唤醒机制
- 与 CCR (Claude Code Remote) 的集成

### 1.2 架构层次

```
┌─────────────────────────────────────────────────────────────┐
│                    Application Layer                         │
│  (UI components, REPL bridge)                                │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                  Bridge Core Layer                           │
│  - bridgeMain.ts (主逻辑)                                    │
│  - bridgeApi.ts (API 封装)                                   │
│  - bridgeMessaging.ts (消息传递)                             │
│  - bridgePermissionCallbacks.ts (权限回调)                   │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                  Transport Layer                             │
│  - replBridgeTransport.ts (REPL 传输)                        │
│  - remoteBridgeCore.ts (远程桥接核心)                        │
│  - WebSocket/SSE/HTTP                                        │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                  CCR Integration                             │
│  - CCR v2 worker protocol                                    │
│  - JWT authentication                                        │
│  - Event streaming                                           │
└─────────────────────────────────────────────────────────────┘
```

### 1.3 核心设计模式

#### 依赖注入模式

Bridge 系统大量使用依赖注入来避免循环依赖和减少 bundle 大小：

```typescript
// bridgeApi.ts - 注入认证处理
type BridgeApiDeps = {
  getAccessToken: () => string | undefined
  onAuth401?: (staleAccessToken: string) => Promise<boolean>
  getTrustedDeviceToken?: () => string | undefined
}

// replBridge.ts - 注入消息映射
toSDKMessages?: (messages: Message[]) => SDKMessage[]

// remoteBridgeCore.ts - 注入标题派生
onUserMessage?: (text: string, sessionId: string) => boolean
```

#### 状态机模式

```typescript
type StatusState = 'idle' | 'attached' | 'titled' | 'reconnecting' | 'failed'

// bridgeUI.ts 中的状态转换
updateIdleStatus()      // → 'idle'
setAttached()           // → 'attached'
setSessionTitle()       // → 'titled'
updateReconnectingStatus() // → 'reconnecting'
updateFailedStatus()    // → 'failed'
```

#### 生成器模式（令牌刷新）

```typescript
// jwtUtils.ts - 使用 generation counter 防止过时定时器
const generations = new Map<string, number>()

function nextGeneration(sessionId: string): number {
  const gen = (generations.get(sessionId) ?? 0) + 1
  generations.set(sessionId, gen)
  return gen
}

async function doRefresh(sessionId: string, gen: number) {
  // 检查 generation 是否过时
  if (generations.get(sessionId) !== gen) {
    return // 被取消或重新调度
  }
}
```

---

## 2. 核心文件深度分析

### 2.1 bridgeApi.ts - 桥接 API

**职责**: 封装与远程 API 的通信

**核心函数**:

```typescript
async function createBridgeSession(
  options: CreateBridgeSessionOptions
): Promise<BridgeSession> {
  // 1. 获取认证令牌
  const accessToken = deps.getAccessToken()
  if (!accessToken) {
    throw new BridgeAuthError('No access token available')
  }
  
  // 2. 创建会话
  const response = await fetch('/v1/code/sessions', {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${accessToken}`,
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      machine_name: options.machineName,
      directory: options.dir,
      // ...
    }),
  })
  
  // 3. 处理认证错误
  if (response.status === 401) {
    if (deps.onAuth401) {
      const refreshed = await deps.onAuth401(accessToken)
      if (refreshed) {
        // 重试
        return createBridgeSession(options)
      }
    }
    throw new BridgeAuthError('Authentication failed')
  }
  
  return parseBridgeSession(response)
}
```

**错误处理**:

```typescript
class BridgeError extends Error {
  constructor(
    message: string,
    public readonly status?: number,
    public readonly recoverable: boolean = false
  ) {
    super(message)
  }
}

class BridgeFatalError extends BridgeError {
  constructor(message: string, status?: number) {
    super(message, status, false)
  }
}

class BridgeAuthError extends BridgeFatalError {
  constructor(message: string) {
    super(message, 401)
  }
}
```

### 2.2 bridgeMessaging.ts - 消息传递

**职责**: 处理双向消息流

**核心机制**:

```typescript
class BridgeMessageQueue {
  private pendingMessages: Array<{
    message: StdoutMessage
    resolve: () => void
    reject: (error: Error) => void
  }> = []
  
  private flushGate: Promise<void> | null = null
  
  // 添加消息到队列
  enqueue(message: StdoutMessage): Promise<void> {
    return new Promise((resolve, reject) => {
      this.pendingMessages.push({ message, resolve, reject })
      this.tryFlush()
    })
  }
  
  // 尝试刷新队列
  private async tryFlush(): Promise<void> {
    if (this.flushGate) return // 等待门打开
    if (this.pendingMessages.length === 0) return
    
    const batch = this.pendingMessages.splice(0, MAX_BATCH_SIZE)
    
    try {
      await this.transport.send(batch)
      batch.forEach(({ resolve }) => resolve())
    } catch (error) {
      batch.forEach(({ reject }) => reject(error))
      // 重新加入队列
      this.pendingMessages.unshift(...batch)
    }
  }
  
  // 打开刷新门
  openFlushGate(): void {
    const gate = this.flushGate
    this.flushGate = null
    gate?.resolve()
    this.tryFlush()
  }
  
  // 等待刷新门
  async waitForFlushGate(): Promise<void> {
    if (!this.flushGate) return
    await this.flushGate
  }
}
```

**FlushGate 设计目的**:
- 确保历史消息在实时消息之前到达服务器
- 防止消息交错
- 即使刷新失败，队列消息也会丢失而不是乱序

### 2.3 bridgePermissionCallbacks.ts - 权限回调

**职责**: 处理远程权限请求

**核心机制**:

```typescript
type PermissionCallback = {
  toolUseId: string
  resolve: (decision: PermissionDecision) => void
  reject: (error: Error) => void
  timeoutMs: number
  timer: NodeJS.Timeout
}

class PermissionCallbackRegistry {
  private callbacks = new Map<string, PermissionCallback>()
  
  register(
    toolUseId: string,
    resolve: (decision: PermissionDecision) => void,
    reject: (error: Error) => void,
    timeoutMs: number
  ): void {
    const timer = setTimeout(() => {
      this.unregister(toolUseId)
      reject(new Error('Permission request timeout'))
    }, timeoutMs)
    
    this.callbacks.set(toolUseId, {
      toolUseId,
      resolve,
      reject,
      timeoutMs,
      timer,
    })
  }
  
  resolve(toolUseId: string, decision: PermissionDecision): void {
    const callback = this.callbacks.get(toolUseId)
    if (callback) {
      clearTimeout(callback.timer)
      this.callbacks.delete(toolUseId)
      callback.resolve(decision)
    }
  }
  
  reject(toolUseId: string, error: Error): void {
    const callback = this.callbacks.get(toolUseId)
    if (callback) {
      clearTimeout(callback.timer)
      this.callbacks.delete(toolUseId)
      callback.reject(error)
    }
  }
}
```

### 2.4 jwtUtils.ts - JWT 工具

**职责**: JWT 令牌管理和刷新

**核心机制**:

```typescript
interface JWTPayload {
  session_id: string
  worker_epoch: number
  exp: number // 过期时间戳
}

function decodeJWT(token: string): JWTPayload {
  const [, payloadBase64] = token.split('.')
  const payload = JSON.parse(
    Buffer.from(payloadBase64, 'base64').toString('utf-8')
  )
  return payload
}

function isJWTExpired(token: string, bufferMs: number = 300000): boolean {
  const payload = decodeJWT(token)
  const now = Date.now()
  const expiresWithBuffer = now + bufferMs
  return expiresWithBuffer >= payload.exp * 1000
}

async function refreshJWTIfNeeded(
  sessionId: string,
  currentJWT: string
): Promise<string> {
  if (!isJWTExpired(currentJWT)) {
    return currentJWT // 未过期，直接使用
  }
  
  // 获取新一代
  const gen = nextGeneration(sessionId)
  
  // 刷新令牌
  const newJWT = await doRefresh(sessionId, gen)
  
  return newJWT
}
```

### 2.5 capacityWake.ts - 容量唤醒

**职责**: 当远程容量可用时唤醒会话

**核心机制**:

```typescript
class CapacityWakeManager {
  private wakeCallbacks = new Map<string, Array<() => void>>()
  private capacityAvailable = new Set<string>()
  
  // 注册唤醒回调
  onWake(sessionId: string, callback: () => void): void {
    if (this.capacityAvailable.has(sessionId)) {
      // 容量已可用，立即回调
      callback()
    } else {
      // 注册回调
      const callbacks = this.wakeCallbacks.get(sessionId) || []
      callbacks.push(callback)
      this.wakeCallbacks.set(sessionId, callbacks)
    }
  }
  
  // 标记容量可用
  markCapacityAvailable(sessionId: string): void {
    this.capacityAvailable.add(sessionId)
    
    const callbacks = this.wakeCallbacks.get(sessionId)
    if (callbacks) {
      callbacks.forEach(cb => cb())
      this.wakeCallbacks.delete(sessionId)
    }
  }
  
  // 清除会话状态
  clear(sessionId: string): void {
    this.capacityAvailable.delete(sessionId)
    this.wakeCallbacks.delete(sessionId)
  }
}
```

### 2.6 pollConfig.ts - 轮询配置

**职责**: 管理轮询间隔和超时

**配置常量**:

```typescript
const DEFAULT_POLL_CONFIG = {
  baseIntervalMs: 1000,      // 基础轮询间隔
  maxIntervalMs: 30000,      // 最大轮询间隔
  timeoutMs: 60000,          // 超时
  backoffMultiplier: 1.5,    // 退避乘数
}

const POLL_CONFIG_SCHEMA = z.object({
  baseIntervalMs: z.number().min(100).max(10000),
  maxIntervalMs: z.number().min(1000).max(60000),
  timeoutMs: z.number().min(10000).max(300000),
  backoffMultiplier: z.number().min(1.0).max(3.0),
})
```

**轮询逻辑**:

```typescript
async function pollWithBackoff<T>(
  operation: () => Promise<T>,
  config: PollConfig = DEFAULT_POLL_CONFIG
): Promise<T> {
  let interval = config.baseIntervalMs
  let lastError: Error | null = null
  
  while (true) {
    try {
      const result = await operation()
      return result
    } catch (error) {
      lastError = error as Error
      
      // 检查超时
      if (Date.now() - startTime > config.timeoutMs) {
        throw new Error('Poll timeout')
      }
      
      // 指数退避
      await sleep(interval)
      interval = Math.min(
        interval * config.backoffMultiplier,
        config.maxIntervalMs
      )
    }
  }
}
```

### 2.7 inboundMessages.ts - 入站消息

**职责**: 处理从远程接收的消息

**消息类型**:

```typescript
type InboundMessage =
  | { type: 'assistant'; message: AssistantMessage }
  | { type: 'user'; message: UserMessage }
  | { type: 'system'; message: SystemMessage }
  | { type: 'attachment'; attachment: Attachment }
  | { type: 'control_request'; request: ControlRequest }
  | { type: 'control_response'; response: ControlResponse }
```

**处理逻辑**:

```typescript
async function handleInboundMessage(
  message: InboundMessage,
  context: BridgeContext
): Promise<void> {
  switch (message.type) {
    case 'assistant':
      await handleAssistantMessage(message.message, context)
      break
    
    case 'user':
      await handleUserMessage(message.message, context)
      break
    
    case 'attachment':
      await handleAttachment(message.attachment, context)
      break
    
    case 'control_request':
      await handleControlRequest(message.request, context)
      break
    
    case 'control_response':
      handleControlResponse(message.response, context)
      break
  }
}
```

### 2.8 inboundAttachments.ts - 入站附件

**职责**: 处理从远程接收的附件

**附件类型**:

```typescript
type InboundAttachment =
  | { type: 'queued_command'; command: QueuedCommand }
  | { type: 'memory_prefetch'; memories: MemoryAttachment[] }
  | { type: 'skill_prefetch'; skills: SkillAttachment[] }
  | { type: 'permission_request'; request: PermissionRequest }
  | { type: 'hook_result'; result: HookResult }
```

**处理逻辑**:

```typescript
async function handleInboundAttachment(
  attachment: InboundAttachment,
  context: BridgeContext
): Promise<void> {
  switch (attachment.type) {
    case 'queued_command':
      await handleQueuedCommand(attachment.command, context)
      break
    
    case 'memory_prefetch':
      await handleMemoryPrefetch(attachment.memories, context)
      break
    
    case 'skill_prefetch':
      await handleSkillPrefetch(attachment.skills, context)
      break
    
    case 'permission_request':
      await handlePermissionRequest(attachment.request, context)
      break
    
    case 'hook_result':
      await handleHookResult(attachment.result, context)
      break
  }
}
```

### 2.9 bridgeUI.ts - 桥接 UI

**职责**: 渲染桥接状态 UI

**状态显示**:

```typescript
function renderBridgeStatus(state: StatusState): React.ReactNode {
  switch (state) {
    case 'idle':
      return <Text dimColor>Bridge idle</Text>
    
    case 'attached':
      return (
        <Box>
          <Text color="success">✓</Text>
          <Text> Bridge attached</Text>
        </Box>
      )
    
    case 'titled':
      return (
        <Box>
          <Text color="success">✓</Text>
          <Text> Session titled</Text>
        </Box>
      )
    
    case 'reconnecting':
      return (
        <Box>
          <Spinner frames={BRIDGE_SPINNER_FRAMES} />
          <Text> Reconnecting...</Text>
        </Box>
      )
    
    case 'failed':
      return (
        <Box>
          <Text color="error">✗</Text>
          <Text> Bridge failed</Text>
        </Box>
      )
  }
}
```

### 2.10 remoteBridgeCore.ts - 远程桥接核心

**职责**: 核心桥接逻辑

**连接流程**:

```typescript
async function connectRemoteBridge(
  options: RemoteBridgeOptions
): Promise<BridgeConnection> {
  // 1. 创建会话
  const session = await createBridgeSession({
    machineName: options.machineName,
    dir: options.dir,
    ...
  })
  
  // 2. 获取 JWT
  const jwt = await getJWTForSession(session.id)
  
  // 3. 建立传输
  const transport = await createTransport({
    sessionId: session.id,
    jwt,
    ...
  })
  
  // 4. 启动消息循环
  startMessageLoop(transport, options)
  
  // 5. 返回连接
  return {
    session,
    transport,
    send: (message) => transport.send(message),
    close: () => transport.close(),
  }
}
```

---

## 3. 远程会话生命周期

### 3.1 会话创建

```
1. 用户启动远程会话
   ↓
2. 调用 /v1/code/sessions (POST)
   ↓
3. 获取 session_id 和 worker_epoch
   ↓
4. 创建 JWT (包含 session_id 和 worker_epoch)
   ↓
5. 建立 WebSocket/SSE 连接
   ↓
6. 注册 /v1/code/sessions/{id}/worker/events/stream
   ↓
7. 启动心跳循环
   ↓
8. 会话就绪
```

### 3.2 会话维护

**心跳机制**:

```typescript
async function startHeartbeatLoop(
  sessionId: string,
  intervalMs: number = 30000
): Promise<void> {
  while (true) {
    await sleep(intervalMs)
    
    try {
      await fetch(`/v1/code/sessions/${sessionId}/worker/heartbeat`, {
        method: 'PUT',
        headers: { 'Authorization': `Bearer ${jwt}` },
        body: JSON.stringify({
          worker_epoch,
          timestamp: Date.now(),
        }),
      })
    } catch (error) {
      logError('Heartbeat failed', error)
      // 不中断循环，继续尝试
    }
  }
}
```

**JWT 刷新**:

```typescript
async function startJWTRefreshLoop(
  sessionId: string,
  bufferMs: number = 300000 // 5 分钟缓冲
): Promise<void> {
  while (true) {
    const currentJWT = getCurrentJWT(sessionId)
    
    if (isJWTExpired(currentJWT, bufferMs)) {
      const newJWT = await refreshJWT(sessionId)
      setJWT(sessionId, newJWT)
      
      // 重新建立传输（epoch 增加）
      await reconnectTransport(sessionId, newJWT)
    }
    
    // 每分钟检查一次
    await sleep(60000)
  }
}
```

### 3.3 会话结束

```typescript
async function closeBridgeSession(
  sessionId: string,
  reason: 'normal' | 'error' | 'timeout'
): Promise<void> {
  // 1. 停止心跳
  stopHeartbeatLoop(sessionId)
  
  // 2. 停止 JWT 刷新
  stopJWTRefreshLoop(sessionId)
  
  // 3. 关闭传输
  await transport.close()
  
  // 4. 清理回调
  permissionCallbacks.clear(sessionId)
  capacityWake.clear(sessionId)
  
  // 5. 通知服务器
  if (reason === 'normal') {
    await fetch(`/v1/code/sessions/${sessionId}`, {
      method: 'DELETE',
    })
  }
}
```

---

## 4. 认证和授权流程

### 4.1 OAuth 集成

```typescript
async function getAccessToken(): Promise<string> {
  // 1. 检查缓存
  const cached = getCachedAccessToken()
  if (cached && !isTokenExpired(cached)) {
    return cached
  }
  
  // 2. 刷新令牌
  const tokens = getClaudeAIOAuthTokens()
  if (tokens && isTokenExpired(tokens)) {
    await refreshOAuthToken(tokens.refreshToken)
  }
  
  // 3. 返回新令牌
  return getCachedAccessToken()
}
```

### 4.2 Trusted Device 认证

```typescript
async function getTrustedDeviceToken(): Promise<string> {
  // 1. 检查缓存
  const cached = readStoredTrustedDeviceToken()
  if (cached) {
    return cached
  }
  
  // 2. 请求新令牌
  const response = await fetch('/v1/trusted-device/request', {
    method: 'POST',
    headers: { 'Authorization': `Bearer ${accessToken}` },
  })
  
  // 3. 存储令牌
  const token = await response.text()
  storeTrustedDeviceToken(token)
  
  return token
}
```

---

## 5. 错误处理策略

### 5.1 错误分类

```typescript
type BridgeErrorKind =
  | 'network'          // 网络连接错误
  | 'timeout'          // 超时
  | 'auth'             // 认证错误 (401/403)
  | 'not_found'        // 资源不存在 (404)
  | 'gone'             // 资源已过期 (410)
  | 'overloaded'       // 服务器过载 (529)
  | 'unknown'          // 未知错误
```

### 5.2 错误恢复

```typescript
async function handleBridgeError(
  error: BridgeError,
  context: BridgeContext
): Promise<RecoveryAction> {
  switch (error.kind) {
    case 'network':
    case 'timeout':
      // 指数退避重试
      return { action: 'retry', delayMs: calculateBackoff(attempt) }
    
    case 'auth':
      // 刷新认证
      await refreshAuth()
      return { action: 'retry', delayMs: 0 }
    
    case 'not_found':
    case 'gone':
      // 资源不存在，停止重连
      return { action: 'stop', reason: 'environment_expired' }
    
    case 'overloaded':
      // 服务器过载，长退避
      return { action: 'retry', delayMs: 60000 }
    
    default:
      return { action: 'stop', reason: 'unknown_error' }
  }
}
```

### 5.3 错误预算

```typescript
// 独立跟踪连接错误和一般错误
let connErrorStart: number | null = null
let generalErrorStart: number | null = null

function trackError(error: BridgeError): void {
  const now = Date.now()
  
  if (isConnectionError(error)) {
    if (generalErrorStart !== null) {
      generalErrorStart = null // 重置一般错误跟踪
    }
    if (connErrorStart === null) {
      connErrorStart = now
    }
  } else {
    if (connErrorStart !== null) {
      connErrorStart = null // 重置连接错误跟踪
    }
    if (generalErrorStart === null) {
      generalErrorStart = now
    }
  }
}

function shouldStopRetrying(): boolean {
  const now = Date.now()
  const maxDuration = 10 * 60 * 1000 // 10 分钟
  
  if (connErrorStart && now - connErrorStart > maxDuration) {
    return true
  }
  if (generalErrorStart && now - generalErrorStart > maxDuration) {
    return true
  }
  
  return false
}
```

---

## 6. 性能优化

### 6.1 懒加载

```typescript
// bridgeMain.ts - 延迟加载 createSession
void import('./createSession.js')
  .then(({ updateBridgeSessionTitle }) => ...)
```

### 6.2 记忆化

```typescript
// trustedDevice.ts - 记忆化 keychain 读取
const readStoredToken = memoize((): string | undefined => {
  return getSecureStorage().read()?.trustedDeviceToken
})
```

### 6.3 防御性默认值

```typescript
// pollConfig.ts - Zod schema 验证 + 默认值
const parsed = pollIntervalConfigSchema().safeParse(raw)
return parsed.success ? parsed.data : DEFAULT_POLL_CONFIG
```

---

## 7. 调试工具

### 7.1 故障注入

```typescript
// bridgeDebug.ts - 注入故障进行测试
injectBridgeFault({
  method: 'pollForWork',
  kind: 'fatal',
  status: 404,
  errorType: 'environment_expired',
  count: 1
})
```

### 7.2 调试日志

```typescript
// debugUtils.ts - 脱敏日志
debugBody({
  machine_name: config.machineName,
  directory: config.dir,
  // session_ingress_token 会自动脱敏
})
// → {"machine_name":"...", "session_ingress_token":"sk-ant...1234"}
```

---

## 8. 与 CCR 的集成

### 8.1 CCR v2 协议

```
POST /v1/code/sessions/{id}/bridge
→ worker_jwt (JWT with session_id claim)

PUT /v1/code/sessions/{id}/worker/register
→ worker_epoch

POST /v1/code/sessions/{id}/worker/events
→ 发送事件

GET /v1/code/sessions/{id}/worker/events/stream
→ SSE 事件流
```

### 8.2 心跳协议

```typescript
PUT /v1/code/sessions/{id}/worker/heartbeat
{
  worker_epoch: number,
  timestamp: number
}
→ { lease_extended: boolean }
```

---

## 9. 安全考虑

### 9.1 密钥管理

- **session_ingress_token**: 从不记录完整值，只记录前缀
- **environment_secret**: 仅用于环境 API 调用
- **OAuth 令牌**: 存储在 macOS keychain

### 9.2 ID 验证

```typescript
// bridgeApi.ts - 防止路径遍历
const SAFE_ID_PATTERN = /^[a-zA-Z0-9_-]+$/

function validateBridgeId(id: string, label: string): string {
  if (!id || !SAFE_ID_PATTERN.test(id)) {
    throw new Error(`Invalid ${label}: contains unsafe characters`)
  }
  return id
}
```

### 9.3 工作树隔离

```typescript
// bridgeMain.ts - 多会话工作树隔离
if (spawnMode === 'worktree') {
  const wt = await createAgentWorktree(`bridge-${safeFilenameId(sessionId)}`)
  sessionDir = wt.worktreePath  // 每个会话独立工作树
}
```

---

## 10. 总结

Bridge 系统展现了以下工程卓越性：

1. **清晰的架构分层**: UI → 核心 → 传输 → API → 云端
2. **精心设计的抽象**: Transport 接口、FlushGate、CapacityWake
3. **健壮的错误处理**: 分类恢复、指数退避、睡眠检测
4. **性能优化**: 懒加载、记忆化、环形缓冲区
5. **安全性**: 密钥脱敏、ID 验证、工作树隔离
6. **可维护性**: 依赖注入、类型安全、防御性编程

**关键设计决策**:

| 决策 | 原因 |
|------|------|
| 使用环形缓冲区而不是普通 Set | 内存效率 O(1)，自动淘汰 |
| v2 使用 CCRClient + SSETransport | 协议差异，读写分离 |
| 需要 FlushGate | 保证消息顺序，防止交错 |
| JWT 刷新重建整个传输 | epoch 绑定，原子性更新 |

---

*文档持续更新中...*
