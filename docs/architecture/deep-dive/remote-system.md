# Remote 系统深度技术文档

> 基于逐行代码分析的完整技术文档  
> **探索完成时间**: 2026 年 4 月 1 日  
> **核心文件**: remote/, server/ 目录下 9 个文件

---

## 1. Remote 系统架构概览

### 1.1 系统职责

Remote 系统负责**远程会话管理**和**服务器架构**，包括：
- 远程会话创建和管理
- 远程状态同步
- 远程权限处理
- 服务器架构和生命周期
- 服务器通信
- 与 Bridge 的集成

### 1.2 架构层次

```
┌─────────────────────────────────────────────────────────────┐
│                    Remote System Architecture                │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌──────────────────────────┐  ┌────────────────────────┐  │
│  │  RemoteSessionManager.ts │  │  SessionsWebSocket.ts  │  │
│  │  (CCR 会话管理核心)       │  │  (WebSocket 客户端)    │  │
│  │  344 行                  │  │  404 行                │  │
│  └──────────┬───────────────┘  └──────────┬─────────────┘  │
│             │                              │                │
│             └──────────────┬───────────────┘                │
│                            │                                │
│                   ┌────────▼────────┐                       │
│                   │ sdkMessageAdapter│                      │
│                   │ .ts (转换器)     │                      │
│                   │ 303 行           │                      │
│                   └────────┬────────┘                       │
│                            │                                │
│         ┌──────────────────┼──────────────────┐            │
│         │                  │                  │             │
│  ┌──────▼───────┐  ┌──────▼───────┐  ┌──────▼───────┐      │
│  │remotePermission│  │   server/    │  │  utils/      │      │
│  │  Bridge.ts    │  │   direct     │  │  background/ │      │
│  │  (权限桥接)    │  │   Connect    │  │  remote/     │      │
│  │  78 行         │  │   Manager    │  │  (后台会话)  │      │
│  │               │  │  (直连管理)   │  │  333 行       │      │
│  └───────────────┘  └───────────────┘  └──────────────┘      │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### 1.3 双模式架构

系统支持两种远程连接模式：

**CCR 模式**: 连接 Anthropic 云端容器 (OAuth 认证)
- 使用 CCR v2 worker 协议
- JWT 认证
- SSE 事件流

**Direct Connect 模式**: 连接自托管服务器 (Bearer Token)
- 简化的认证流程
- WebSocket 直连
- 适用于企业内部部署

---

## 2. 核心文件深度分析

### 2.1 RemoteSessionManager.ts (344 行) - CCR 会话管理核心

**职责**: 管理 CCR 远程会话的完整生命周期

#### 会话状态机

```typescript
type SessionState =
  | 'starting'      // 会话启动中
  | 'running'       // 会话运行中
  | 'detached'      // 会话分离（后台运行）
  | 'stopping'      // 会话停止中
  | 'stopped'       // 会话已停止
```

#### 核心方法

**创建会话**:

```typescript
async function createSession(
  options: CreateSessionOptions
): Promise<RemoteSession> {
  // 1. 获取认证令牌
  const accessToken = await getAccessToken()
  if (!accessToken) {
    throw new Error('Authentication required')
  }
  
  // 2. 创建 CCR 会话
  const response = await fetch('/v1/code/sessions', {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${accessToken}`,
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      machine_name: options.machineName,
      directory: options.dir,
      entrypoint: options.entrypoint,
      // ...
    }),
  })
  
  // 3. 解析会话信息
  const session = await parseSessionResponse(response)
  
  // 4. 注册 WebSocket 订阅
  await subscribeToSession(session.id)
  
  return session
}
```

**会话心跳**:

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

**权限请求处理**:

```typescript
async function handlePermissionRequest(
  request: PermissionRequest,
  context: SessionContext
): Promise<PermissionDecision> {
  // 1. 注册回调
  const promise = registerPermissionCallback(request.toolUseId)
  
  // 2. 转发到本地 UI
  forwardToLocalUI(request)
  
  // 3. 等待用户决策
  try {
    const decision = await promise
    return decision
  } catch (error) {
    if (error instanceof TimeoutError) {
      return { behavior: 'deny', message: 'Permission request timeout' }
    }
    throw error
  }
}
```

**会话状态同步**:

```typescript
function syncSessionState(
  sessionId: string,
  state: SessionState,
  details?: SessionStateDetails
): void {
  // 1. 更新本地状态
  sessionStates.set(sessionId, { state, details, timestamp: Date.now() })
  
  // 2. 通知订阅者
  sessionStateListeners.forEach(listener => {
    listener(sessionId, state, details)
  })
  
  // 3. 持久化状态（用于恢复）
  persistSessionState(sessionId, state, details)
}
```

#### 错误处理

```typescript
class SessionError extends Error {
  constructor(
    message: string,
    public readonly sessionId?: string,
    public readonly recoverable: boolean = false
  ) {
    super(message)
  }
}

class SessionAuthError extends SessionError {
  constructor(message: string) {
    super(message, undefined, false)
  }
}

class SessionNotFoundError extends SessionError {
  constructor(sessionId: string) {
    super(`Session ${sessionId} not found`, sessionId, false)
  }
}

class SessionTimeoutError extends SessionError {
  constructor(message: string) {
    super(message, undefined, true)
  }
}
```

### 2.2 SessionsWebSocket.ts (404 行) - WebSocket 客户端实现

**职责**: 管理与远程会话的 WebSocket 连接

#### 连接状态

```typescript
type WSState =
  | 'connecting'    // 连接中
  | 'connected'     // 已连接
  | 'reconnecting'  // 重连中
  | 'disconnected'  // 已断开
```

#### 核心机制

**连接建立**:

```typescript
async function connect(
  sessionId: string,
  jwt: string
): Promise<void> {
  state = 'connecting'
  
  const wsUrl = buildWebSocketUrl(sessionId)
  ws = new WebSocket(wsUrl, {
    headers: {
      'Authorization': `Bearer ${jwt}`,
      'User-Agent': getClaudeCodeUserAgent(),
    },
  })
  
  ws.on('open', handleOpen)
  ws.on('message', handleMessage)
  ws.on('close', handleClose)
  ws.on('error', handleError)
}
```

**消息处理**:

```typescript
async function handleMessage(data: WebSocket.Data): Promise<void> {
  try {
    const message = JSON.parse(data.toString())
    
    switch (message.type) {
      case 'assistant':
        await handleAssistantMessage(message)
        break
      
      case 'user':
        await handleUserMessage(message)
        break
      
      case 'attachment':
        await handleAttachment(message)
        break
      
      case 'control_request':
        await handleControlRequest(message)
        break
      
      case 'control_response':
        handleControlResponse(message)
        break
      
      default:
        logWarning('Unknown message type', message.type)
    }
  } catch (error) {
    logError('Failed to handle message', error)
  }
}
```

**重连机制**:

```typescript
const RECONNECT_CONFIG = {
  baseDelayMs: 1000,
  maxDelayMs: 30000,
  maxAttempts: 5,
  jitterFraction: 0.25,
}

async function scheduleReconnect(attempt: number): Promise<void> {
  if (attempt >= RECONNECT_CONFIG.maxAttempts) {
    state = 'disconnected'
    emit('disconnected', { reason: 'max_attempts' })
    return
  }
  
  state = 'reconnecting'
  
  // 指数退避 + 抖动
  const baseDelay = RECONNECT_CONFIG.baseDelayMs * Math.pow(2, attempt - 1)
  const jitter = Math.random() * RECONNECT_CONFIG.jitterFraction * baseDelay
  const delay = Math.min(baseDelay + jitter, RECONNECT_CONFIG.maxDelayMs)
  
  await sleep(delay)
  
  if (state === 'reconnecting') {
    await connect(sessionId, jwt)
  }
}
```

**特殊关闭代码处理**:

```typescript
const SPECIAL_CLOSE_CODES = {
  4001: 'session_expired',    // 会话过期
  4003: 'unauthorized',       // 未授权
}

function handleClose(code: number, reason: string): void {
  const specialReason = SPECIAL_CLOSE_CODES[code as keyof typeof SPECIAL_CLOSE_CODES]
  
  if (specialReason) {
    // 特殊关闭代码不重连
    state = 'disconnected'
    emit('disconnected', { reason: specialReason, code })
  } else {
    // 普通关闭，尝试重连
    scheduleReconnect(reconnectAttempts++)
  }
}
```

### 2.3 sdkMessageAdapter.ts (303 行) - SDK 消息转换器

**职责**: 在 SDK 消息格式和 REPL 消息格式之间转换

#### 消息类型映射

```typescript
type SDKMessage =
  | { type: 'assistant'; message: AssistantMessage }
  | { type: 'user'; message: UserMessage }
  | { type: 'system'; message: SystemMessage }
  | { type: 'attachment'; attachment: Attachment }
  | { type: 'stream_event'; event: StreamEvent }

type REPLMessage =
  | { type: 'assistant'; message: AssistantMessage }
  | { type: 'user'; message: UserMessage }
  | { type: 'system'; message: SystemMessage }
  | { type: 'attachment'; attachment: Attachment }
```

#### 转换函数

**SDK → REPL**:

```typescript
function sdkToREPL(message: SDKMessage): REPLMessage | null {
  // 忽略 SDK 专用消息
  if (SDK_ONLY_MESSAGES.has(message.type)) {
    return null
  }
  
  switch (message.type) {
    case 'stream_event':
      // 流式事件转换为普通消息
      return convertStreamEvent(message.event)
    
    default:
      return message as REPLMessage
  }
}

const SDK_ONLY_MESSAGES = new Set([
  'auth_status',
  'tool_use_summary',
  'session_metadata',
])
```

**REPL → SDK**:

```typescript
function replToSDK(message: REPLMessage): SDKMessage {
  // SDK 需要额外的元数据
  return {
    ...message,
    metadata: {
      timestamp: Date.now(),
      sessionId: currentSessionId,
      // ...
    },
  }
}
```

#### 消息过滤

```typescript
function shouldForwardMessage(
  message: SDKMessage,
  context: ForwardContext
): boolean {
  // 1. 检查消息类型
  if (BLOCKED_MESSAGE_TYPES.has(message.type)) {
    return false
  }
  
  // 2. 检查工具结果大小
  if (message.type === 'attachment' && 
      message.attachment.type === 'tool_result') {
    const size = estimateAttachmentSize(message.attachment)
    if (size > MAX_ATTACHMENT_SIZE) {
      return false
    }
  }
  
  // 3. 检查权限
  if (!hasPermissionToForward(message, context)) {
    return false
  }
  
  return true
}
```

### 2.4 remotePermissionBridge.ts (78 行) - 权限请求桥接

**职责**: 桥接远程和本地权限请求

#### 核心机制

```typescript
class PermissionBridge {
  private pendingRequests = new Map<string, {
    resolve: (decision: PermissionDecision) => void
    reject: (error: Error) => void
    timeout: NodeJS.Timeout
  }>()
  
  async requestPermission(
    request: PermissionRequest,
    timeoutMs: number = 60000
  ): Promise<PermissionDecision> {
    return new Promise((resolve, reject) => {
      // 注册回调
      this.pendingRequests.set(request.toolUseId, {
        resolve,
        reject,
        timeout: setTimeout(() => {
          this.pendingRequests.delete(request.toolUseId)
          reject(new Error('Permission request timeout'))
        }, timeoutMs),
      })
      
      // 转发到本地 UI
      forwardToLocalUI(request)
    })
  }
  
  respond(toolUseId: string, decision: PermissionDecision): void {
    const pending = this.pendingRequests.get(toolUseId)
    if (pending) {
      clearTimeout(pending.timeout)
      this.pendingRequests.delete(toolUseId)
      pending.resolve(decision)
    }
  }
}
```

#### 合成消息创建

```typescript
function createSyntheticAssistantMessage(
  toolUse: ToolUseBlock,
  context: BridgeContext
): AssistantMessage {
  return {
    role: 'assistant',
    content: [toolUse],
    id: generateMessageId(),
    // 合成消息的特殊标记
    metadata: {
      synthetic: true,
      originalToolUseId: toolUse.id,
    },
  }
}
```

### 2.5 server/directConnectManager.ts (213 行) - 直连会话管理

**职责**: 管理直连会话（非 CCR 模式）

#### 会话持久化

```typescript
interface PersistedSession {
  id: string
  name: string
  serverUrl: string
  bearerToken: string
  createdAt: number
  lastConnectedAt?: number
  state: SessionState
}

const SESSIONS_FILE = path.join(
  getClaudeConfigHomeDir(),
  'server-sessions.json'
)

async function loadPersistedSessions(): Promise<PersistedSession[]> {
  try {
    const content = await readFile(SESSIONS_FILE, 'utf-8')
    return JSON.parse(content)
  } catch (error) {
    if ((error as NodeJS.ErrnoException).code === 'ENOENT') {
      return []
    }
    throw error
  }
}

async function savePersistedSessions(sessions: PersistedSession[]): Promise<void> {
  await writeFile(
    SESSIONS_FILE,
    JSON.stringify(sessions, null, 2),
    'utf-8'
  )
}
```

#### 会话管理

```typescript
class DirectConnectManager {
  private sessions = new Map<string, PersistedSession>()
  private connections = new Map<string, WebSocket>()
  
  async addSession(options: AddSessionOptions): Promise<string> {
    const session: PersistedSession = {
      id: randomUUID(),
      name: options.name,
      serverUrl: options.serverUrl,
      bearerToken: options.bearerToken,
      createdAt: Date.now(),
      state: 'stopped',
    }
    
    this.sessions.set(session.id, session)
    await savePersistedSessions(Array.from(this.sessions.values()))
    
    return session.id
  }
  
  async connect(sessionId: string): Promise<void> {
    const session = this.sessions.get(sessionId)
    if (!session) {
      throw new Error(`Session ${sessionId} not found`)
    }
    
    const ws = await createWebSocketConnection(
      session.serverUrl,
      session.bearerToken
    )
    
    this.connections.set(sessionId, ws)
    session.state = 'running'
    session.lastConnectedAt = Date.now()
    
    await savePersistedSessions(Array.from(this.sessions.values()))
  }
  
  async disconnect(sessionId: string): Promise<void> {
    const ws = this.connections.get(sessionId)
    if (ws) {
      ws.close()
      this.connections.delete(sessionId)
    }
    
    const session = this.sessions.get(sessionId)
    if (session) {
      session.state = 'detached'
      await savePersistedSessions(Array.from(this.sessions.values()))
    }
  }
}
```

### 2.6 server/createDirectConnectSession.ts (88 行) - 会话创建函数

**职责**: 创建直连会话的辅助函数

```typescript
async function createDirectConnectSession(
  options: CreateDirectConnectOptions
): Promise<DirectConnectSession> {
  // 1. 验证服务器 URL
  const url = new URL(options.serverUrl)
  if (!['ws:', 'wss:'].includes(url.protocol)) {
    throw new Error('Server URL must be ws:// or wss://')
  }
  
  // 2. 测试连接
  try {
    await testConnection(url, options.bearerToken)
  } catch (error) {
    throw new Error(
      `Failed to connect to server: ${(error as Error).message}`
    )
  }
  
  // 3. 创建会话
  const session = await manager.addSession({
    name: options.name,
    serverUrl: options.serverUrl,
    bearerToken: options.bearerToken,
  })
  
  // 4. 建立连接
  await manager.connect(session)
  
  return {
    id: session,
    name: options.name,
    serverUrl: options.serverUrl,
  }
}
```

### 2.7 server/types.ts (57 行) - 服务器类型定义

```typescript
export type ServerConfig = {
  serverUrl: string
  bearerToken: string
  name?: string
  autoConnect?: boolean
  reconnect?: boolean
}

export type ServerSession = {
  id: string
  config: ServerConfig
  state: SessionState
  lastError?: Error
  metrics: SessionMetrics
}

export type SessionMetrics = {
  connectedAt?: number
  disconnectedAt?: number
  messagesSent: number
  messagesReceived: number
  errors: number
}

export type SessionState =
  | 'starting'
  | 'running'
  | 'detached'
  | 'stopping'
  | 'stopped'
```

### 2.8 utils/background/remote/remoteSession.ts (98 行) - 后台会话类型

**职责**: 定义后台远程会话的类型和接口

```typescript
export type BackgroundRemoteSession = {
  sessionId: string
  state: 'background' | 'foreground'
  lastActivity: number
  keepAlive: boolean
}

export type RemoteSessionManager = {
  getBackgroundSession(sessionId: string): BackgroundRemoteSession | undefined
  createBackgroundSession(sessionId: string): BackgroundRemoteSession
  releaseBackgroundSession(sessionId: string): void
}
```

### 2.9 utils/background/remote/preconditions.ts (235 行) - 前置条件检查

**职责**: 检查远程会话的前置条件

#### 认证检查

```typescript
async function checkAuthPrecondition(): Promise<AuthPrecondition> {
  // 1. 检查 OAuth 令牌
  const oauthTokens = getClaudeAIOAuthTokens()
  if (!oauthTokens?.accessToken) {
    return {
      ok: false,
      reason: 'oauth_required',
      message: 'OAuth authentication required',
    }
  }
  
  // 2. 检查令牌过期
  if (isOAuthTokenExpired(oauthTokens)) {
    try {
      await refreshOAuthToken(oauthTokens.refreshToken)
    } catch (error) {
      return {
        ok: false,
        reason: 'token_expired',
        message: 'OAuth token expired and refresh failed',
      }
    }
  }
  
  return { ok: true }
}
```

#### 网络检查

```typescript
async function checkNetworkPrecondition(): Promise<NetworkPrecondition> {
  // 1. 检查网络连接
  if (!isOnline()) {
    return {
      ok: false,
      reason: 'offline',
      message: 'No network connection',
    }
  }
  
  // 2. 测试 API 可达性
  try {
    await fetch('/v1/health', { method: 'HEAD' })
  } catch (error) {
    return {
      ok: false,
      reason: 'api_unreachable',
      message: 'API server unreachable',
    }
  }
  
  return { ok: true }
}
```

#### 会话检查

```typescript
async function checkSessionPrecondition(
  sessionId: string
): Promise<SessionPrecondition> {
  // 1. 检查会话存在
  const session = await getSession(sessionId)
  if (!session) {
    return {
      ok: false,
      reason: 'session_not_found',
      message: `Session ${sessionId} not found`,
    }
  }
  
  // 2. 检查会话状态
  if (session.state === 'stopped') {
    return {
      ok: false,
      reason: 'session_stopped',
      message: 'Session has been stopped',
    }
  }
  
  // 3. 检查会话健康
  const health = await checkSessionHealth(sessionId)
  if (!health.healthy) {
    return {
      ok: false,
      reason: 'session_unhealthy',
      message: health.reason || 'Session is unhealthy',
    }
  }
  
  return { ok: true }
}
```

---

## 3. 远程会话管理流程

### 3.1 会话创建流程

```
1. 用户请求远程会话
   ↓
2. 检查前置条件（认证、网络、会话）
   ↓
3. 获取 JWT（CCR 模式）或 Bearer Token（直连模式）
   ↓
4. 创建 WebSocket 连接
   ↓
5. 注册会话管理器
   ↓
6. 启动心跳循环
   ↓
7. 订阅消息流
   ↓
8. 会话就绪
```

### 3.2 消息流处理

```
远程会话
   ↓
WebSocket 消息
   ↓
SessionsWebSocket.handleMessage()
   ↓
sdkMessageAdapter.sdkToREPL()
   ↓
消息过滤（shouldForwardMessage）
   ↓
转发到本地 UI
   ↓
用户看到消息
```

### 3.3 权限请求流程

```
远程工具调用
   ↓
remotePermissionBridge.requestPermission()
   ↓
创建合成 AssistantMessage
   ↓
转发到本地 UI
   ↓
用户看到权限对话框
   ↓
用户决策（Allow/Deny）
   ↓
bridge.respond(toolUseId, decision)
   ↓
发送决策到远程会话
   ↓
远程工具执行或取消
```

---

## 4. 状态同步机制

### 4.1 会话状态同步

```typescript
function syncSessionState(
  sessionId: string,
  state: SessionState,
  details?: SessionStateDetails
): void {
  // 1. 更新本地状态
  sessionStates.set(sessionId, { state, details, timestamp: Date.now() })
  
  // 2. 通知订阅者
  sessionStateListeners.forEach(listener => {
    listener(sessionId, state, details)
  })
  
  // 3. 持久化状态
  persistSessionState(sessionId, state, details)
}
```

### 4.2 心跳机制

```typescript
// CCR 模式
PUT /v1/code/sessions/{sessionId}/worker/heartbeat
{
  worker_epoch: number,
  timestamp: number
}
→ { lease_extended: boolean }

// 直连模式
ws.send(JSON.stringify({
  type: 'heartbeat',
  timestamp: Date.now()
}))
```

### 4.3 重连策略

```typescript
const RECONNECT_CONFIG = {
  baseDelayMs: 1000,      // 基础延迟
  maxDelayMs: 30000,      // 最大延迟
  maxAttempts: 5,         // 最大尝试次数
  jitterFraction: 0.25,   // 抖动比例
}

// 指数退避公式
delay = min(baseDelay * 2^(attempt-1) + jitter, maxDelay)
```

---

## 5. 错误处理策略

### 5.1 错误分类

```typescript
type RemoteErrorKind =
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
async function handleRemoteError(
  error: RemoteError,
  context: RemoteContext
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

### 5.3 特殊关闭代码

| 代码 | 含义 | 处理 |
|------|------|------|
| 4001 | 会话过期/未找到 | 不重连，清除本地状态 |
| 4003 | 未授权 | 不重连，提示重新认证 |
| 其他 | 普通关闭 | 尝试重连（最多 5 次） |

---

## 6. 性能优化

### 6.1 消息批处理

```typescript
class MessageBatcher {
  private batch: SDKMessage[] = []
  private timer: NodeJS.Timeout | null = null
  
  add(message: SDKMessage): void {
    this.batch.push(message)
    
    if (!this.timer) {
      this.timer = setTimeout(() => {
        this.flush()
      }, 100) // 100ms 批处理窗口
    }
    
    if (this.batch.length >= MAX_BATCH_SIZE) {
      this.flush()
    }
  }
  
  flush(): void {
    if (this.batch.length > 0) {
      this.transport.send(this.batch)
      this.batch = []
    }
    if (this.timer) {
      clearTimeout(this.timer)
      this.timer = null
    }
  }
}
```

### 6.2 连接池

```typescript
class ConnectionPool {
  private connections = new Map<string, WebSocket>()
  private maxPoolSize = 10
  
  acquire(sessionId: string): WebSocket | undefined {
    return this.connections.get(sessionId)
  }
  
  release(sessionId: string): void {
    if (this.connections.size > this.maxPoolSize) {
      // LRU 驱逐
      const oldest = this.connections.keys().next().value
      this.connections.delete(oldest)
    }
  }
}
```

### 6.3 内存管理

```typescript
// 限制待处理消息数量
const MAX_PENDING_MESSAGES = 1000

function enqueueMessage(message: SDKMessage): void {
  if (pendingMessages.length >= MAX_PENDING_MESSAGES) {
    // 丢弃最旧的消息
    pendingMessages.shift()
  }
  pendingMessages.push(message)
}
```

---

## 7. 安全机制

### 7.1 认证管理

```typescript
// CCR 模式：JWT 认证
async function getJWTForSession(sessionId: string): Promise<string> {
  const accessToken = await getAccessToken()
  
  const response = await fetch(`/v1/code/sessions/${sessionId}/bridge`, {
    method: 'POST',
    headers: { 'Authorization': `Bearer ${accessToken}` },
  })
  
  const { worker_jwt } = await response.json()
  return worker_jwt
}

// 直连模式：Bearer Token
function getBearerToken(serverConfig: ServerConfig): string {
  return serverConfig.bearerToken
}
```

### 7.2 令牌存储

```typescript
// macOS: Keychain
async function storeBearerToken(serverId: string, token: string): Promise<void> {
  await keychain.setPassword({
    account: `claude-code-server-${serverId}`,
    service: 'claude-code',
    password: token,
  })
}

// Windows: Credential Manager
async function storeBearerToken(serverId: string, token: string): Promise<void> {
  await wincred.setPassword({
    target: `claude-code-server-${serverId}`,
    password: token,
  })
}

// Linux: libsecret
async function storeBearerToken(serverId: string, token: string): Promise<void> {
  await libsecret.setPassword({
    service: 'claude-code',
    account: `claude-code-server-${serverId}`,
    password: token,
  })
}
```

### 7.3 会话隔离

```typescript
// 每个会话独立的 JWT
const jwt = await getJWTForSession(sessionId)
// JWT 包含 session_id claim，防止跨会话访问

// 工作树隔离
if (spawnMode === 'worktree') {
  const wt = await createAgentWorktree(`remote-${sessionId}`)
  sessionDir = wt.worktreePath  // 每个会话独立工作树
}
```

---

## 8. 与 Bridge 的集成

### 8.1 消息流集成

```
Remote Session
      ↓
SessionsWebSocket
      ↓
sdkMessageAdapter
      ↓
Bridge Messaging
      ↓
Local UI
```

### 8.2 权限集成

```
Remote Tool Use
      ↓
remotePermissionBridge
      ↓
Bridge Permission Callbacks
      ↓
Local Permission Dialog
      ↓
User Decision
      ↓
Remote Session (执行或取消)
```

### 8.3 状态同步集成

```
Remote Session State
      ↓
RemoteSessionManager
      ↓
Bridge Status
      ↓
UI Status Indicator
```

---

## 9. 总结

Remote 系统是一个**高度工程化**的远程会话管理系统，结合了：

1. **双模式架构**: CCR 云端模式 + 直连自托管模式
2. **健壮的错误处理**: 分类恢复、指数退避、特殊关闭代码处理
3. **性能优化**: 消息批处理、连接池、内存管理
4. **安全性**: JWT 认证、Bearer Token、会话隔离
5. **可维护性**: 类型安全、清晰的接口、状态机设计

**关键设计决策**:

| 决策 | 原因 |
|------|------|
| 双模式架构 | 支持云端和本地部署两种场景 |
| WebSocket + SSE | 实时双向通信 + 服务器推送 |
| 指数退避重连 | 避免服务器过载，提高成功率 |
| 特殊关闭代码 | 快速识别不可恢复错误 |
| 消息批处理 | 减少网络请求，提高效率 |

---

*文档持续更新中...*
