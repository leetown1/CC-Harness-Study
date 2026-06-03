# CLI Handlers & Transports 系统深度技术文档

> 基于逐行代码分析的完整技术文档  
> **探索完成时间**: 2026 年 4 月 1 日  
> **核心文件**: cli/handlers/ (6 文件), cli/transports/ (7 文件), 4,389 行代码

---

## 一、CLI Handlers 系统架构

### 1.1 目录结构

```
cli/handlers/
├── auth.ts (330 行)              # 认证命令处理器
├── agents.ts (71 行)             # Agent 列表命令
├── plugins.ts (879 行)           # 插件管理命令
├── autoMode.ts (171 行)          # 自动模式配置
├── mcp.tsx (495+ 行)             # MCP 服务器管理
└── util.tsx (110 行)             # 杂项命令处理器
```

### 1.2 Handler 职责分类

| Handler | 行数 | 核心职责 |
|---------|------|---------|
| auth.ts | 330 | OAuth 登录/登出/状态 |
| plugins.ts | 879 | 插件安装/卸载/启用/禁用/更新/验证 |
| autoMode.ts | 171 | 自动模式规则配置和批评 |
| mcp.tsx | 495+ | MCP 服务器管理和工具查看 |
| agents.ts | 71 | Agent 列表和选择 |
| util.tsx | 110 | 杂项命令处理 |

---

## 二、Auth Handler 详解 (auth.ts)

### 2.1 核心职责

**文件**: `cli/handlers/auth.ts` (330 行)

**主要功能**:
1. OAuth 登录流程
2. 认证状态显示
3. 登出处理
4. OAuth Token 安装

### 2.2 OAuth 登录流程

```typescript
export async function authLogin({ email, sso, console, claudeai }) {
  // 1. 检查环境变量提供的 refresh token (快速路径)
  if (process.env.CLAUDE_CODE_OAUTH_REFRESH_TOKEN) {
    const tokens = await refreshOAuthToken(envRefreshToken, { scopes })
    await installOAuthTokens(tokens)
    process.exit(0)
  }
  
  // 2. 启动 OAuth 流程
  const oauthService = new OAuthService()
  const result = await oauthService.startOAuthFlow(
    url => {
      process.stdout.write(`Opening browser to sign in…\n`)
      process.stdout.write(`If browser didn't open, visit: ${url}\n`)
    },
    { 
      loginWithClaudeAi: claudeai,
      loginHint: email,
      loginMethod: sso ? 'sso' : undefined
    }
  )
  
  // 3. 安装 tokens
  await installOAuthTokens(result)
  
  // 4. 验证组织
  await validateForceLoginOrg()
  
  process.exit(0)
}
```

### 2.3 Token 安装流程

```typescript
export async function installOAuthTokens(tokens: OAuthTokens) {
  // 1. 清除旧状态
  await performLogout({ clearOnboarding: false })
  
  // 2. 获取用户信息
  const profile = await getOauthProfileFromOauthToken(tokens.accessToken)
  storeOAuthAccountInfo({
    accountUuid: profile.account.uuid,
    emailAddress: profile.account.email,
    organizationUuid: profile.organization.uuid,
    // ...
  })
  
  // 3. 保存 tokens
  saveOAuthTokensIfNeeded(tokens)
  clearOAuthTokenCache()
  
  // 4. 获取用户角色
  await fetchAndStoreUserRoles(tokens.accessToken)
  
  // 5. 创建 API key (Console 用户)
  if (!shouldUseClaudeAIAuth(tokens.scopes)) {
    const apiKey = await createAndStoreApiKey(tokens.accessToken)
  }
}
```

### 2.4 认证状态显示

```typescript
export async function authStatus() {
  const tokens = getClaudeAIOAuthTokens()
  
  if (!tokens) {
    cliOk('Not logged in')
    process.exit(0)
  }
  
  const profile = await getOauthProfileFromOauthToken(tokens.accessToken)
  
  cliOk(jsonStringify({
    email: profile.account.email,
    organization: profile.organization.name,
    subscriptionType: profile.organization.subscriptionType,
    expiresAt: new Date(tokens.expiresAt).toISOString(),
  }, null, 2))
}
```

---

## 三、Plugins Handler 详解 (plugins.ts)

### 3.1 核心职责

**文件**: `cli/handlers/plugins.ts` (879 行)

**主要功能**:
1. 插件列表显示
2. 插件安装
3. 插件卸载
4. 插件启用/禁用
5. 插件更新
6. 插件验证
7. 市场管理

### 3.2 插件列表处理

```typescript
export async function pluginListHandler({ json, available }) {
  // 1. 加载已安装插件
  const installedData = loadInstalledPluginsV2()
  const enabledPlugins = getPluginEditableScopes()
  
  // 2. 加载所有插件 (包括内联)
  const { enabled, disabled, errors } = await loadAllPlugins()
  const inlinePlugins = allLoadedPlugins.filter(p =>
    p.source.endsWith('@inline')
  )
  
  if (json) {
    // JSON 输出
    const plugins = pluginIds.map(pluginId => ({
      id: pluginId,
      version: installation.version,
      scope: installation.scope,
      enabled: enabledPlugins.has(pluginId),
      installPath: installation.installPath,
      mcpServers: loadedPlugin.mcpServers,
      errors: pluginErrors.map(getPluginErrorMessage)
    }))
    cliOk(jsonStringify({ installed: plugins, available }, null, 2))
  } else {
    // 人类可读输出
    console.log('Installed plugins:\n')
    for (const pluginId of pluginIds.sort()) {
      console.log(`  ${pointer} ${pluginId}`)
      console.log(`    Version: ${version}`)
      console.log(`    Scope: ${scope}`)
      console.log(`    Status: ${status}`)
    }
  }
}
```

### 3.3 插件验证流程

```typescript
export async function pluginValidateHandler(manifestPath, { cowork }) {
  // 1. 验证 manifest
  const result = await validateManifest(manifestPath)
  printValidationResult(result)
  
  // 2. 如果在 .claude-plugin 目录内，也验证内容文件
  if (result.fileType === 'plugin') {
    const manifestDir = dirname(result.filePath)
    if (basename(manifestDir) === '.claude-plugin') {
      const contentResults = await validatePluginContents(dirname(manifestDir))
      for (const r of contentResults) {
        printValidationResult(r)
      }
    }
  }
  
  // 3. 报告结果
  if (allSuccess) {
    cliOk(hasWarnings ? 'Validation passed with warnings' : 'Validation passed')
  } else {
    console.log('Validation failed')
    process.exit(1)
  }
}
```

### 3.4 插件安装处理

```typescript
export async function pluginInstallHandler(plugin, scope, { cowork }) {
  // 1. 解析插件标识符
  const { name, marketplace } = parsePluginIdentifier(plugin)
  
  // 2. 查找市场
  const marketplaces = await loadKnownMarketplacesConfig()
  const marketplaceConfig = marketplaces[marketplace]
  if (!marketplaceConfig) {
    cliError(`Marketplace "${marketplace}" not found`)
  }
  
  // 3. 安装插件
  const result = await installPluginOp(plugin, scope)
  if (!result.success) {
    cliError(result.message)
  }
  
  // 4. 清除缓存
  clearAllCaches()
  
  cliOk(result.message)
}
```

---

## 四、AutoMode Handler 详解 (autoMode.ts)

### 4.1 核心职责

**文件**: `cli/handlers/autoMode.ts` (171 行)

**主要功能**:
1. 显示默认分类规则
2. 显示有效配置（用户 + 默认）
3. 批评用户自定义规则

### 4.2 规则结构

```typescript
type AutoModeRules = {
  allow: string[]       // 自动批准的操作
  soft_deny: string[]   // 需要用户确认的操作
  environment: string[] // 上下文信息
}
```

### 4.3 批评系统提示

```typescript
const CRITIQUE_SYSTEM_PROMPT =
  'You are an expert reviewer of auto mode classifier rules...\n' +
  '\n' +
  'For each rule, evaluate:\n' +
  '1. Clarity: Is the rule unambiguous?\n' +
  '2. Completeness: Are there gaps or edge cases?\n' +
  '3. Conflicts: Do any rules conflict?\n' +
  '4. Actionability: Is the rule specific enough?\n'
```

---

## 五、CLI Transports 系统架构

### 5.1 目录结构

```
cli/transports/
├── transportUtils.ts (46 行)              # 传输层工厂
├── WebSocketTransport.ts (801 行)         # WebSocket 传输
├── SSETransport.ts (712 行)               # SSE 传输
├── HybridTransport.ts (283 行)            # 混合传输 (WS+POST)
├── ccrClient.ts (999 行)                  # CCR v2 客户端
├── SerialBatchEventUploader.ts (276 行)   # 串行批处理上传器
└── WorkerStateUploader.ts (132 行)        # Worker 状态上传器
```

### 5.2 传输层选择优先级

```typescript
function getTransportForUrl(url, headers, sessionId, refreshHeaders): Transport {
  // 1. CCR v2: SSE 读取 + HTTP POST 写入
  if (CLAUDE_CODE_USE_CCR_V2) {
    return new SSETransport(sseUrl, ...)
  }
  
  // 2. Hybrid: WS 读取 + HTTP POST 写入
  if (CLAUDE_CODE_POST_FOR_SESSION_INGRESS_V2) {
    return new HybridTransport(url, ...)
  }
  
  // 3. 默认：纯 WebSocket
  return new WebSocketTransport(url, ...)
}
```

---

## 六、SerialBatchEventUploader 详解

### 6.1 核心职责

**文件**: `cli/transports/SerialBatchEventUploader.ts` (276 行)

**主要功能**:
1. 串行化事件上传（防止并发 POST 冲突）
2. 批处理优化（减少请求次数）
3. 指数退避重试
4. 背压控制（防止内存爆炸）

### 6.2 配置类型

```typescript
type SerialBatchEventUploaderConfig<T> = {
  maxBatchSize: number        // 每批最大事件数
  maxBatchBytes?: number      // 每批最大字节数
  maxQueueSize: number        // 队列满时背压
  send: (batch: T[]) => Promise<void>  // 实际发送函数
  baseDelayMs: number         // 退避基数
  maxDelayMs: number          // 退避上限
  jitterMs: number            // 抖动范围
  maxConsecutiveFailures?: number  // 最大连续失败次数
  onBatchDropped?: (batchSize, failures) => void  // 丢弃回调
}
```

### 6.3 入队背压

```typescript
async enqueue(events: T | T[]): Promise<void> {
  // 背压：等待有空间
  while (this.pending.length + items.length > this.config.maxQueueSize) {
    await new Promise<void>(resolve => {
      this.backpressureResolvers.push(resolve)
    })
  }
  this.pending.push(...items)
  void this.drain()
}
```

### 6.4 批处理逻辑

```typescript
private takeBatch(): T[] {
  const { maxBatchSize, maxBatchBytes } = this.config
  
  if (maxBatchBytes === undefined) {
    return this.pending.splice(0, maxBatchSize)
  }
  
  let bytes = 0
  let count = 0
  while (count < maxBatchSize) {
    const itemBytes = Buffer.byteLength(jsonStringify(this.pending[count]))
    if (count > 0 && bytes + itemBytes > maxBatchBytes) break
    bytes += itemBytes
    count++
  }
  return this.pending.splice(0, count)
}
```

### 6.5 重试逻辑

```typescript
private async drain(): Promise<void> {
  let failures = 0
  
  while (this.pending.length > 0) {
    const batch = this.takeBatch()
    
    try {
      await this.config.send(batch)
      failures = 0  // 成功重置
    } catch (err) {
      failures++
      
      // 检查是否超过最大失败次数
      if (failures >= this.config.maxConsecutiveFailures) {
        this.droppedBatches++
        this.config.onBatchDropped?.(batch.length, failures)
        continue  // 丢弃，继续下一批
      }
      
      // 重新排队（使用 concat 而非 unshift 优化性能）
      this.pending = batch.concat(this.pending)
      
      // 指数退避 + 抖动
      const retryAfterMs = err instanceof RetryableError ? err.retryAfterMs : undefined
      await this.sleep(this.retryDelay(failures, retryAfterMs))
    }
    
    // 释放背压
    this.releaseBackpressure()
  }
}
```

---

## 七、WorkerStateUploader 详解

### 7.1 核心职责

**文件**: `cli/transports/WorkerStateUploader.ts` (132 行)

**主要功能**:
1. 合并 PUT /worker 请求（防止并发冲突）
2. RFC 7396 合并语义（metadata 深度合并）

### 7.2 合并规则

```typescript
function coalescePatches(base, overlay): Record<string, unknown> {
  const merged = { ...base }
  
  for (const [key, value] of Object.entries(overlay)) {
    if (
      (key === 'external_metadata' || key === 'internal_metadata') &&
      merged[key] && typeof merged[key] === 'object' &&
      typeof value === 'object' && value !== null
    ) {
      // RFC 7396 合并：overlay 键覆盖，null 保留用于删除
      merged[key] = {
        ...(merged[key] as Record<string, unknown>),
        ...(value as Record<string, unknown>),
      }
    } else {
      merged[key] = value  // 顶层键：后者胜
    }
  }
  
  return merged
}
```

### 7.3 入队逻辑

```typescript
enqueue(patch: Record<string, unknown>): void {
  if (this.closed) return
  // 合并到 pending patch
  this.pending = this.pending 
    ? coalescePatches(this.pending, patch) 
    : patch
  void this.drain()
}
```

---

## 八、CCRClient 详解

### 8.1 核心职责

**文件**: `cli/transports/ccrClient.ts` (999 行)

**主要功能**:
1. Epoch 管理（检测更新的 worker）
2. 心跳（保持 liveness）
3. 状态报告（idle, running, requires_action）
4. 事件写入（client events, internal events, delivery updates）
5. 内部事件读取（用于 session resume）

### 8.2 四个上传器

```typescript
export class CCRClient {
  private readonly workerState: WorkerStateUploader  // PUT /worker
  private readonly eventUploader: SerialBatchEventUploader<ClientEvent>  // POST /worker/events
  private readonly internalEventUploader: SerialBatchEventUploader<WorkerEvent>  // POST /worker/internal-events
  private readonly deliveryUploader: SerialBatchEventUploader<{eventId, status}>  // POST /worker/events/delivery
}
```

### 8.3 初始化流程

```typescript
async initialize(epoch?: number): Promise<Record<string, unknown> | null> {
  // 1. 获取 epoch
  if (epoch === undefined) {
    epoch = parseInt(process.env.CLAUDE_CODE_WORKER_EPOCH, 10)
  }
  this.workerEpoch = epoch
  
  // 2. 并发：注册 worker + 获取恢复状态
  const restoredPromise = this.getWorkerState()
  const result = await this.request('put', '/worker', {
    worker_status: 'idle',
    worker_epoch: this.workerEpoch,
    external_metadata: { pending_action: null, task_summary: null },
  })
  
  // 3. 启动心跳
  this.startHeartbeat()
  
  // 4. 注册 session activity 回调
  registerSessionActivityCallback(() => {
    void this.writeEvent({ type: 'keep_alive' })
  })
  
  // 5. 等待状态恢复
  const { metadata, durationMs } = await restoredPromise
  return metadata
}
```

### 8.4 心跳机制

```typescript
private startHeartbeat(): void {
  const schedule = () => {
    const jitter = this.heartbeatIntervalMs * this.heartbeatJitterFraction * (2 * Math.random() - 1)
    this.heartbeatTimer = setTimeout(tick, this.heartbeatIntervalMs + jitter)
  }
  
  const tick = () => {
    void this.sendHeartbeat()
    if (this.heartbeatTimer === null) return  // close() 期间
    schedule()
  }
  
  schedule()
}

private async sendHeartbeat(): Promise<void> {
  if (this.heartbeatInFlight) return
  this.heartbeatInFlight = true
  try {
    const result = await this.request('post', '/worker/heartbeat', {
      session_id: this.sessionId,
      worker_epoch: this.workerEpoch,
    }, 'Heartbeat', { timeout: 5_000 })
  } finally {
    this.heartbeatInFlight = false
  }
}
```

### 8.5 Stream Event 累积

```typescript
async writeEvent(message: StdoutMessage): Promise<void> {
  if (message.type === 'stream_event') {
    // 累积 100ms
    this.streamEventBuffer.push(message)
    if (!this.streamEventTimer) {
      this.streamEventTimer = setTimeout(
        () => void this.flushStreamEventBuffer(),
        STREAM_EVENT_FLUSH_INTERVAL_MS
      )
    }
    return
  }
  
  // 非 stream_event: 先 flush 缓冲区
  await this.flushStreamEventBuffer()
  
  // 清理 accumulator (assistant message 完成)
  if (message.type === 'assistant') {
    clearStreamAccumulatorForMessage(this.streamTextAccumulator, message)
  }
  
  await this.eventUploader.enqueue(this.toClientEvent(message))
}
```

### 8.6 文本 Delta 合并

```typescript
export function accumulateStreamEvents(buffer, state): EventPayload[] {
  const out: EventPayload[] = []
  const touched = new Map<string[], CoalescedStreamEvent>()
  
  for (const msg of buffer) {
    switch (msg.event.type) {
      case 'message_start':
        // 记录 active message
        state.scopeToMessage.set(scopeKey(msg), msg.event.message.id)
        break
        
      case 'content_block_delta':
        if (msg.event.delta.type !== 'text_delta') {
          out.push(msg)
          break
        }
        
        // 累积文本块
        const chunks = (blocks[msg.event.index] ??= [])
        chunks.push(msg.event.delta.text)
        
        // 更新 snapshot（重写同一 entry）
        const existing = touched.get(chunks)
        if (existing) {
          existing.event.delta.text = chunks.join('')
          break
        }
        
        // 创建 snapshot
        const snapshot = {
          type: 'stream_event',
          uuid: msg.uuid,
          event: {
            type: 'content_block_delta',
            index: msg.event.index,
            delta: { type: 'text_delta', text: chunks.join('') },
          },
        }
        touched.set(chunks, snapshot)
        out.push(snapshot)
        break
        
      default:
        out.push(msg)
    }
  }
  
  return out
}
```

---

## 九、SSETransport 详解

### 9.1 核心职责

**文件**: `cli/transports/SSETransport.ts` (712 行)

**主要功能**:
1. 通过 SSE 读取事件流
2. HTTP POST 写入事件
3. 自动重连（指数退避）
4. 活性检测（45 秒无帧则重连）

### 9.2 SSE 帧解析

```typescript
export function parseSSEFrames(buffer: string): { frames: SSEFrame[], remaining: string } {
  const frames: SSEFrame[] = []
  let pos = 0
  
  while ((idx = buffer.indexOf('\n\n', pos)) !== -1) {
    const rawFrame = buffer.slice(pos, idx)
    pos = idx + 2
    
    if (!rawFrame.trim()) continue
    
    const frame: SSEFrame = {}
    let isComment = false
    
    for (const line of rawFrame.split('\n')) {
      if (line.startsWith(':')) {
        isComment = true  // keepalive 注释
        continue
      }
      
      const colonIdx = line.indexOf(':')
      if (colonIdx === -1) continue
      
      const field = line.slice(0, colonIdx)
      const value = line[colonIdx + 1] === ' ' 
        ? line.slice(colonIdx + 2) 
        : line.slice(colonIdx + 1)
      
      switch (field) {
        case 'event': frame.event = value; break
        case 'id': frame.id = value; break
        case 'data': frame.data = frame.data ? frame.data + '\n' + value : value; break
      }
    }
    
    if (frame.data || isComment) {
      frames.push(frame)
    }
  }
  
  return { frames, remaining: buffer.slice(pos) }
}
```

### 9.3 流读取

```typescript
private async readStream(body: ReadableStream<Uint8Array>): Promise<void> {
  const reader = body.getReader()
  const decoder = new TextDecoder()
  let buffer = ''
  
  try {
    while (true) {
      const { done, value } = await reader.read()
      if (done) break
      
      buffer += decoder.decode(value, STREAM_DECODE_OPTS)
      const { frames, remaining } = parseSSEFrames(buffer)
      buffer = remaining
      
      for (const frame of frames) {
        // 任何帧都证明连接活跃
        this.resetLivenessTimer()
        
        // 跟踪序列号（去重）
        if (frame.id) {
          const seqNum = parseInt(frame.id, 10)
          if (!this.seenSequenceNums.has(seqNum)) {
            this.seenSequenceNums.add(seqNum)
            // 防止无限增长
            if (this.seenSequenceNums.size > 1000) {
              const threshold = this.lastSequenceNum - 200
              for (const s of this.seenSequenceNums) {
                if (s < threshold) this.seenSequenceNums.delete(s)
              }
            }
          }
          if (seqNum > this.lastSequenceNum) {
            this.lastSequenceNum = seqNum
          }
        }
        
        // 处理帧
        if (frame.event && frame.data) {
          this.handleSSEFrame(frame.event, frame.data)
        }
      }
    }
  } finally {
    reader.releaseLock()
  }
  
  // 流结束：重连
  if (this.state !== 'closing' && this.state !== 'closed') {
    this.handleConnectionError()
  }
}
```

### 9.4 活性检测

```typescript
private readonly onLivenessTimeout = (): void => {
  this.livenessTimer = null
  logForDebugging('SSETransport: Liveness timeout, reconnecting')
  this.abortController?.abort()
  this.handleConnectionError()
}

private resetLivenessTimer(): void {
  this.clearLivenessTimer()
  this.livenessTimer = setTimeout(this.onLivenessTimeout, LIVENESS_TIMEOUT_MS)
}
```

### 9.5 重连逻辑

```typescript
private handleConnectionError(): void {
  this.clearLivenessTimer()
  this.abortController?.abort()
  
  const now = Date.now()
  if (!this.reconnectStartTime) {
    this.reconnectStartTime = now
  }
  
  const elapsed = now - this.reconnectStartTime
  if (elapsed < RECONNECT_GIVE_UP_MS) {
    // 刷新 headers
    if (this.refreshHeaders) {
      const freshHeaders = this.refreshHeaders()
      Object.assign(this.headers, freshHeaders)
    }
    
    // 指数退避 + 抖动
    this.reconnectAttempts++
    const baseDelay = Math.min(
      RECONNECT_BASE_DELAY_MS * Math.pow(2, this.reconnectAttempts - 1),
      RECONNECT_MAX_DELAY_MS
    )
    const delay = Math.max(
      0,
      baseDelay + baseDelay * 0.25 * (2 * Math.random() - 1)
    )
    
    this.reconnectTimer = setTimeout(() => {
      this.reconnectTimer = null
      void this.connect()
    }, delay)
  } else {
    // 放弃
    this.state = 'closed'
    this.onCloseCallback?.()
  }
}
```

---

## 十、WebSocketTransport 详解

### 10.1 核心职责

**文件**: `cli/transports/WebSocketTransport.ts` (801 行)

**主要功能**:
1. WebSocket 连接管理
2. 消息缓冲和重放
3. Ping/Pong 健康检查
4. Keep_alive 数据帧

### 10.2 Bun vs Node 支持

```typescript
async connect(): Promise<void> {
  if (typeof Bun !== 'undefined') {
    // Bun WebSocket（支持 headers）
    const ws = new globalThis.WebSocket(this.url.href, {
      headers,
      proxy: getWebSocketProxyUrl(this.url.href),
      tls: getWebSocketTLSOptions(),
    })
    this.ws = ws
    this.isBunWs = true
    
    ws.addEventListener('open', this.onBunOpen)
    ws.addEventListener('message', this.onBunMessage)
    ws.addEventListener('error', this.onBunError)
    ws.addEventListener('close', this.onBunClose)
    ws.addEventListener('pong', this.onPong)
  } else {
    // Node ws 包
    const { default: WS } = await import('ws')
    const ws = new WS(this.url.href, {
      headers,
      agent: getWebSocketProxyAgent(this.url.href),
    })
    this.ws = ws
    this.isBunWs = false
    
    ws.on('open', this.onNodeOpen)
    ws.on('message', this.onNodeMessage)
    ws.on('error', this.onNodeError)
    ws.on('close', this.onNodeClose)
    ws.on('pong', this.onPong)
  }
}
```

### 10.3 消息缓冲

```typescript
async write(message: StdoutMessage): Promise<void> {
  // 缓冲有 UUID 的消息
  if ('uuid' in message && typeof message.uuid === 'string') {
    this.messageBuffer.add(message)
    this.lastSentId = message.uuid
  }
  
  const line = jsonStringify(message) + '\n'
  
  if (this.state !== 'connected') {
    return  // 缓冲，等待重连后重放
  }
  
  this.sendLine(line)
}
```

### 10.4 重放逻辑

```typescript
private replayBufferedMessages(lastId: string): void {
  const messages = this.messageBuffer.toArray()
  if (messages.length === 0) return
  
  // 找到服务器确认的位置
  let startIndex = 0
  if (lastId) {
    const lastConfirmedIndex = messages.findIndex(
      message => 'uuid' in message && message.uuid === lastId
    )
    if (lastConfirmedIndex >= 0) {
      startIndex = lastConfirmedIndex + 1
      // 重建缓冲区
      const remaining = messages.slice(startIndex)
      this.messageBuffer.clear()
      this.messageBuffer.addAll(remaining)
    }
  }
  
  // 重放未确认消息
  const messagesToReplay = messages.slice(startIndex)
  for (const message of messagesToReplay) {
    const line = jsonStringify(message) + '\n'
    const success = this.sendLine(line)
    if (!success) break
  }
}
```

### 10.5 Ping/Pong 检测

```typescript
private startPingInterval(): void {
  this.pongReceived = true
  let lastTickTime = Date.now()
  
  this.pingInterval = setInterval(() => {
    if (this.state === 'connected' && this.ws) {
      const now = Date.now()
      const gap = now - lastTickTime
      lastTickTime = now
      
      // 检测进程暂停（笔记本合盖等）
      if (gap > SLEEP_DETECTION_THRESHOLD_MS) {
        logForDebugging(`${Math.round(gap / 1000)}s tick gap detected — forcing reconnect`)
        this.handleConnectionError()
        return
      }
      
      // 检查上次 ping 的 pong
      if (!this.pongReceived) {
        logForDebugging('No pong received, connection appears dead')
        this.handleConnectionError()
        return
      }
      
      this.pongReceived = false
      this.ws.ping?.()
    }
  }, DEFAULT_PING_INTERVAL)
}
```

### 10.6 Keep_alive 数据帧

```typescript
private startKeepaliveInterval(): void {
  if (CLAUDE_CODE_REMOTE) return  // CCR 使用心跳
  
  this.keepAliveInterval = setInterval(() => {
    if (this.state === 'connected' && this.ws) {
      this.ws.send(KEEP_ALIVE_FRAME)
      this.lastActivityTime = Date.now()
    }
  }, DEFAULT_KEEPALIVE_INTERVAL)  // 5 分钟
}
```

---

## 十一、总结

### 11.1 CLI Handlers 系统设计哲学

1. **快速路径优先**: 13 条快速路径避免不必要的初始化
2. **人类可读输出**: JSON 和文本两种输出格式
3. **错误处理**: 统一的错误报告和退出码
4. **验证优先**: 插件验证、Manifest 验证

### 11.2 Transports 系统设计哲学

1. **传输抽象**: 统一的 Transport 接口
2. **容错性**: 自动重连、指数退避
3. **性能优化**: 批处理、背压控制
4. **可靠性**: 消息缓冲、重放、去重

### 11.3 关键创新

1. **串行批处理上传器**: 防止并发 POST 冲突，优化网络请求
2. **Worker 状态合并**: RFC 7396 合并语义，防止状态覆盖
3. **文本 Delta 累积**: 100ms 窗口累积，重写同一 entry
4. **活性检测**: 45 秒无帧自动重连
5. **Ping/Pong 健康检查**: 检测进程暂停

### 11.4 性能指标

| 指标 | 数值 |
|------|------|
| 批处理大小 | 100 条或 15 秒 |
| 背压阈值 | 8192 条 |
| 重连预算 | 10 分钟 |
| 活性超时 | 45 秒 |
| Ping 间隔 | 10 秒 |
| Stream Event 累积 | 100ms |

---

*文档持续更新中...*
