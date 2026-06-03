# MCP 系统深度技术文档

> 基于逐行代码分析的完整技术文档  
> **探索完成时间**: 2026 年 4 月 1 日  
> **核心文件**: services/mcp/client.ts (119k+ 行), oauth.ts (2466 行), config.ts, elicitationHandler.ts

---

## 1. MCP 系统概述

MCP (Model Context Protocol) 系统实现了多传输、多范围的架构，支持 stdio、SSE、HTTP、WebSocket、SDK 等多种传输方式，具有完整的 OAuth 2.1 认证、Elicitation 协议和策略执行机制。

### 1.1 核心设计原则

- **传输无关**: 支持 stdio, SSE, HTTP, WebSocket, SDK 和 IDE 特定传输
- **基于范围的配置**: 企业 → 本地 → 项目 → 用户 → 动态 → Claude.ai 优先级
- **插件原生**: 插件可以提供带自动命名空间的 MCP 服务器
- **策略执行**: 企业允许列表/拒绝列表带命令和 URL 过滤
- **OAuth 2.1 兼容**: 完整的 PKCE 流程带动态客户端注册

### 1.2 架构层次

```
┌─────────────────────────────────────────────────────────────┐
│                    Claude Code Client                        │
├─────────────────────────────────────────────────────────────┤
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │ MCP Client   │  │ MCP Client   │  │ MCP Client   │      │
│  │ (stdio)      │  │ (SSE/HTTP)   │  │ (WebSocket)  │      │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘      │
│         │                 │                 │               │
│  ┌──────▼─────────────────▼─────────────────▼───────┐      │
│  │          MCP Connection Manager                   │      │
│  │  - Transport abstraction                          │      │
│  │  - OAuth token management                         │      │
│  │  - Elicitation handling                           │      │
│  │  - Resource & tool discovery                      │      │
│  └───────────────────┬───────────────────────────────┘      │
│                      │                                       │
│  ┌───────────────────▼───────────────────────────────┐      │
│  │          Configuration Manager                     │      │
│  │  - Multi-scope merge (enterprise→user→project)    │      │
│  │  - Policy enforcement (allowlist/denylist)        │      │
│  │  - Environment variable expansion                  │      │
│  │  - Plugin server deduplication                     │      │
│  └────────────────────────────────────────────────────┘      │
└─────────────────────────────────────────────────────────────┘
```

---

## 2. MCP 配置系统

### 2.1 配置范围（优先级顺序）

```typescript
type ConfigScope = 
  | 'enterprise'    // 最高：managed-mcp.json (IT 管理员)
  | 'local'         // .claude/settings.local.json (用户项目特定)
  | 'project'       // .mcp.json 在项目根目录 (共享团队)
  | 'user'          // ~/.claude/settings.json (全局用户)
  | 'dynamic'       // 运行时添加 (插件，SDK)
  | 'claudeai'      // Claude.ai 连接器 (最低)
```

**优先级规则**：
1. **企业独占控制**: 当 `managed-mcp.json` 存在时，所有其他范围被忽略
2. **仅限插件策略**: `allowManagedMcpServersOnly: true` 阻止用户/项目/本地范围
3. **项目继承**: 父目录中的 `.mcp.json` 文件向上合并（更接近 CWD 的获胜）

### 2.2 服务器配置 Schema

```typescript
// Stdio 服务器
export const McpStdioServerConfigSchema = z.object({
  type: z.literal('stdio').optional(),
  command: z.string().min(1),
  args: z.array(z.string()).default([]),
  env: z.record(z.string(), z.string()).optional(),
})

// 带 OAuth 的 SSE 服务器
export const McpSSEServerConfigSchema = z.object({
  type: z.literal('sse'),
  url: z.string(),
  headers: z.record(z.string(), z.string()).optional(),
  headersHelper: z.string().optional(),
  oauth: McpOAuthConfigSchema().optional(),
})

// SDK 管理的服务器
export const McpSdkServerConfigSchema = z.object({
  type: z.literal('sdk'),
  name: z.string(),
})

// Claude.ai 代理
export const McpClaudeAIProxyServerConfigSchema = z.object({
  type: z.literal('claudeai-proxy'),
  url: z.string(),
  id: z.string(),
})
```

### 2.3 环境变量扩展

```typescript
function expandEnvVars(config: McpServerConfig): {
  expanded: McpServerConfig
  missingVars: string[]
}
```

**支持的变量**：
- `${VAR}` - 标准环境变量
- `${CLAUDE_PLUGIN_ROOT}` - 插件安装目录
- `${CLAUDE_PLUGIN_DATA}` - 插件数据目录 (~/.claude/plugins/data/{pluginId})
- `${user_config.KEY}` - 插件用户配置值

**扩展顺序**：
1. 插件特定变量 (`${CLAUDE_PLUGIN_ROOT}`)
2. 用户配置变量 (`${user_config.KEY}`)
3. 通用环境变量 (`${PATH}`)

### 2.4 服务器去重

**基于签名的去重**：

```typescript
// 计算服务器签名（忽略 env 和 headers）
export function getMcpServerSignature(
  config: McpServerConfig
): string | null {
  const cmd = getServerCommandArray(config)
  if (cmd) {
    return `stdio:${jsonStringify(cmd)}`
  }
  const url = getServerUrl(config)
  if (url) {
    return `url:${unwrapCcrProxyUrl(url)}`  // 解包 CCR 代理 URL
  }
  return null  // SDK 类型没有签名
}

// 去重插件服务器对手动配置
export function dedupPluginMcpServers(
  pluginServers: Record<string, ScopedMcpServerConfig>,
  manualServers: Record<string, ScopedMcpServerConfig>
): {
  servers: Record<string, ScopedMcpServerConfig>
  suppressed: Array<{ name: string; duplicateOf: string }>
} {
  // 为手动服务器计算签名
  const manualSigs = new Map<string, string>()
  for (const [name, config] of Object.entries(manualServers)) {
    const sig = getMcpServerSignature(config)
    if (sig && !manualSigs.has(sig)) {
      manualSigs.set(sig, name)
    }
  }
  
  const servers: Record<string, ScopedMcpServerConfig> = {}
  const suppressed: Array<{ name: string; duplicateOf: string }> = []
  const seenPluginSigs = new Map<string, string>()
  
  for (const [name, config] of Object.entries(pluginServers)) {
    const sig = getMcpServerSignature(config)
    if (sig === null) {
      servers[name] = config
      continue
    }
    
    // 检查手动重复
    const manualDup = manualSigs.get(sig)
    if (manualDup !== undefined) {
      suppressed.push({ name, duplicateOf: manualDup })
      continue
    }
    
    // 检查插件重复（先加载的获胜）
    const pluginDup = seenPluginSigs.get(sig)
    if (pluginDup !== undefined) {
      suppressed.push({ name, duplicateOf: pluginDup })
      continue
    }
    
    seenPluginSigs.set(sig, name)
    servers[name] = config
  }
  
  return { servers, suppressed }
}
```

---

## 3. OAuth 认证系统

### 3.1 OAuth 流程架构

实现 **RFC 8414** (OAuth 2.0 Discovery) + **RFC 9728** (Protected Resource Metadata)：

- **动态客户端注册 (DCR)**: 自动客户端注册
- **PKCE (RFC 7636)**: 公共客户端的代码挑战
- **Token 刷新**: 主动刷新带 5 分钟缓冲
- **升级认证**: 通过 403 insufficient_scope 的范围提升
- **XAA (跨应用访问)**: SEP-990/991 企业 SSO

### 3.2 完整 OAuth 流程

```typescript
export async function performMCPOAuthFlow(
  serverName: string,
  serverConfig: McpSSEServerConfig | McpHTTPServerConfig,
  onAuthorizationUrl: (url: string) => void,
  abortSignal?: AbortSignal,
  options?: {
    skipBrowserOpen?: boolean
    onWaitingForCallback?: (submit: (callbackUrl: string) => void) => void
  }
): Promise<void>
```

**逐步流程**：

```typescript
// 1. 元数据发现 (RFC 8414 + RFC 9728)
const metadata = await fetchAuthServerMetadata(
  serverName,
  serverConfig.url,
  serverConfig.oauth?.authServerMetadataUrl
)
// 发现顺序:
// a) 配置的元数据 URL (如果提供)
// b) RFC 9728: /.well-known/oauth-protected-resource
// c) RFC 8414: /.well-known/oauth-authorization-server/{path}

// 2. 动态客户端注册 (如果没有预配置的 client_id)
if (!clientInfo) {
  const dcrResponse = await fetch(metadata.registration_endpoint, {
    method: 'POST',
    body: JSON.stringify({
      client_name: `Claude Code (${serverName})`,
      redirect_uris: [redirectUri],
      grant_types: ['authorization_code', 'refresh_token'],
      response_types: ['code'],
      token_endpoint_auth_method: 'none'  // 公共客户端
    })
  })
  clientInfo = await dcrResponse.json()
}

// 3. PKCE 设置
const codeVerifier = randomBytes(32).toString('base64url')
const codeChallenge = base64url(sha256(codeVerifier))

// 4. 授权请求
const authUrl = new URL(metadata.authorization_endpoint)
authUrl.searchParams.set('client_id', clientInfo.client_id)
authUrl.searchParams.set('redirect_uri', redirectUri)
authUrl.searchParams.set('response_type', 'code')
authUrl.searchParams.set('code_challenge', codeChallenge)
authUrl.searchParams.set('code_challenge_method', 'S256')
authUrl.searchParams.set('state', randomState())
authUrl.searchParams.set('scope', requestedScope)

// 5. 打开浏览器并等待回调
const authCode = await waitForCallback(port)

// 6. Token 交换
const tokenResponse = await fetch(metadata.token_endpoint, {
  method: 'POST',
  headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
  body: new URLSearchParams({
    grant_type: 'authorization_code',
    code: authCode,
    redirect_uri: redirectUri,
    code_verifier: codeVerifier,
    client_id: clientInfo.client_id
  })
})
const tokens = await tokenResponse.json()

// 7. 保存到安全存储
saveTokens(serverName, serverConfig, tokens)
```

### 3.3 Token 管理

**主动刷新**：

```typescript
// 当 token 在 5 分钟内过期时刷新
if (expiresIn <= 300 && tokenData.refreshToken && !needsStepUp) {
  const refreshed = await refreshAuthorization(refreshToken)
  if (refreshed) {
    return refreshed  // 新 tokens
  }
}
```

**跨进程锁**：

```typescript
// 防止跨进程并发刷新
const lockfilePath = join(claudeDir, `mcp-refresh-${sanitizedKey}.lock`)
const release = await lockfile.lock(lockfilePath)

try {
  // 重新读取 tokens - 另一个进程可能已刷新
  const freshTokens = await readFreshTokens()
  if (freshTokens.expiresIn > 300) {
    return freshTokens  // 使用现有有效 tokens
  }
  
  // 执行刷新
  return await _doRefresh(refreshToken)
} finally {
  await release()
}
```

### 3.4 XAA (跨应用访问) - SEP-990/991

**企业 SSO 流程**：

```typescript
async function performMCPXaaAuth(
  serverName: string,
  serverConfig: McpSSEServerConfig | McpHTTPServerConfig,
  onAuthorizationUrl: (url: string) => void,
  abortSignal?: AbortSignal
): Promise<void> {
  // 1. 获取 IdP 配置（通过 `claude mcp xaa setup` 配置一次）
  const idp = getXaaIdpSettings()
  
  // 2. 获取 id_token（缓存或通过 OIDC 浏览器登录）
  const idToken = await acquireIdpIdToken({
    idpIssuer: idp.issuer,
    idpClientId: idp.clientId,
    idpClientSecret,
    callbackPort: idp.callbackPort
  })
  
  // 3. RFC 8693 Token 交换（无浏览器 - 静默）
  const tokens = await performCrossAppAccess(
    serverConfig.url,
    {
      clientId: serverConfig.oauth.clientId,
      clientSecret: serverConfig.oauth.clientSecret,
      idpClientId: idp.clientId,
      idpClientSecret,
      idpIdToken: idToken,
      idpTokenEndpoint: oidc.token_endpoint
    }
  )
  
  // 4. 保存 tokens（与正常 OAuth 相同的存储）
  saveTokens(serverName, serverConfig, tokens)
}
```

**关键 XAA 特性**：
- **单次浏览器登录**: 一个 IdP 登录重用于所有 XAA 服务器
- **静默重新认证**: 缓存的 id_token 实现后台 token 更新
- **无回退**: 如果 `oauth.xaa: true`，XAA 是唯一路径（安全边界）

---

## 4. MCP Elicitation 处理

### 4.1 Elicitation 协议

Elicitation 允许 MCP 服务器在执行敏感操作前请求用户确认/同意。

**两种模式**：
1. **表单模式**: UI 内表单带 JSON schema 验证
2. **URL 模式**: 外部 URL 基础同意流程

### 4.2 Elicitation 处理器

```typescript
export function registerElicitationHandler(
  client: Client,
  serverName: string,
  setAppState: (f: (prevState: AppState) => AppState) => void
): void {
  // 注册 elicitation 请求处理器
  client.setRequestHandler(ElicitRequestSchema, async (request, extra) => {
    // 1. 运行 elicitation hooks（编程响应）
    const hookResponse = await runElicitationHooks(
      serverName,
      request.params,
      extra.signal
    )
    if (hookResponse) {
      return hookResponse  // Hook 提供响应
    }
    
    // 2. 排队等待用户交互
    const response = new Promise<ElicitResult>(resolve => {
      setAppState(prev => ({
        ...prev,
        elicitation: {
          queue: [
            ...prev.elicitation.queue,
            {
              serverName,
              requestId: extra.requestId,
              params: request.params,
              signal: extra.signal,
              respond: (result: ElicitResult) => resolve(result)
            }
          ]
        }
      }))
    })
    
    // 3. 等待用户响应
    const rawResult = await response
    
    // 4. 运行结果 hooks（后处理）
    const result = await runElicitationResultHooks(
      serverName,
      rawResult,
      extra.signal,
      mode,
      elicitationId
    )
    
    return result
  })
  
  // 注册完成通知处理器
  client.setNotificationHandler(
    ElicitationCompleteNotificationSchema,
    notification => {
      const { elicitationId } = notification.params
      // 在 UI 中标记 elicitation 为已完成
      setAppState(prev => {
        const idx = findElicitationInQueue(
          prev.elicitation.queue,
          serverName,
          elicitationId
        )
        if (idx === -1) return prev
        const queue = [...prev.elicitation.queue]
        queue[idx] = { ...queue[idx]!, completed: true }
        return { ...prev, elicitation: { queue } }
      })
    }
  )
}
```

---

## 5. 安全策略执行

### 5.1 企业策略

**拒绝列表检查**：

```typescript
function isMcpServerDenied(
  serverName: string,
  config?: McpServerConfig
): boolean {
  const settings = getMcpDenylistSettings()
  if (!settings.deniedMcpServers) return false
  
  // 检查基于名称的拒绝
  for (const entry of settings.deniedMcpServers) {
    if (isMcpServerNameEntry(entry) && entry.serverName === serverName) {
      return true
    }
  }
  
  // 检查基于命令的拒绝（stdio 服务器）
  if (config) {
    const serverCommand = getServerCommandArray(config)
    if (serverCommand) {
      for (const entry of settings.deniedMcpServers) {
        if (
          isMcpServerCommandEntry(entry) &&
          commandArraysMatch(entry.serverCommand, serverCommand)
        ) {
          return true
        }
      }
    }
    
    // 检查基于 URL 的拒绝（远程服务器）
    const serverUrl = getServerUrl(config)
    if (serverUrl) {
      for (const entry of settings.deniedMcpServers) {
        if (
          isMcpServerUrlEntry(entry) &&
          urlMatchesPattern(serverUrl, entry.serverUrl)
        ) {
          return true
        }
      }
    }
  }
  
  return false
}
```

**允许列表检查**：

```typescript
function isMcpServerAllowedByPolicy(
  serverName: string,
  config?: McpServerConfig
): boolean {
  // 拒绝列表具有绝对优先级
  if (isMcpServerDenied(serverName, config)) {
    return false
  }
  
  const settings = getMcpAllowlistSettings()
  if (!settings.allowedMcpServers) {
    return true  // 没有允许列表限制
  }
  
  // 空允许列表意味着阻止所有
  if (settings.allowedMcpServers.length === 0) {
    return false
  }
  
  // 检查允许列表条目（基于名称、命令或 URL）
  // ... 实现细节
}
```

---

## 6. 传输抽象

### 6.1 支持的传输类型

1. **Stdio**: 本地进程执行
2. **SSE**: Server-Sent Events
3. **HTTP**: HTTP with OAuth
4. **WebSocket**: WebSocket 传输
5. **SDK**: SDK 管理的服务器
6. **Claude.ai Proxy**: Claude.ai 代理

### 6.2 连接状态机

```typescript
type MCPServerConnection =
  | ConnectedMCPServer    // 成功连接
  | FailedMCPServer       // 连接失败
  | NeedsAuthMCPServer    // 需要 OAuth
  | PendingMCPServer      // 重新连接/回退
  | DisabledMCPServer     // 用户禁用
```

---

## 7. 插件 MCP 集成

### 7.1 加载插件 MCP 服务器

```typescript
export async function loadPluginMcpServers(
  plugin: LoadedPlugin,
  errors: PluginError[] = []
): Promise<Record<string, McpServerConfig> | undefined> {
  let servers: Record<string, McpServerConfig> = {}
  
  // 1. 从插件目录加载 .mcp.json (最低优先级)
  const defaultMcpServers = await loadMcpServersFromFile(
    plugin.path,
    '.mcp.json'
  )
  if (defaultMcpServers) {
    servers = { ...servers, ...defaultMcpServers }
  }
  
  // 2. 从 manifest mcpServers 加载 (更高优先级)
  if (plugin.manifest.mcpServers) {
    const mcpServersSpec = plugin.manifest.mcpServers
    
    if (typeof mcpServersSpec === 'string') {
      // 检查是否为 MCPB 文件
      if (isMcpbSource(mcpServersSpec)) {
        const mcpbServers = await loadMcpServersFromMcpb(
          plugin,
          mcpServersSpec,
          errors
        )
        if (mcpbServers) {
          servers = { ...servers, ...mcpbServers }
        }
      } else {
        // JSON 文件路径
        const mcpServers = await loadMcpServersFromFile(
          plugin.path,
          mcpServersSpec
        )
        if (mcpServers) {
          servers = { ...servers, ...mcpServers }
        }
      }
    } else if (Array.isArray(mcpServersSpec)) {
      // 路径或内联配置数组
      // ...
    } else {
      // 直接 MCP 服务器配置
      servers = { ...servers, ...mcpServersSpec }
    }
  }
  
  return Object.keys(servers).length > 0 ? servers : undefined
}
```

### 7.2 插件服务器命名空间

```typescript
export function addPluginScopeToServers(
  servers: Record<string, McpServerConfig>,
  pluginName: string,
  pluginSource: string
): Record<string, ScopedMcpServerConfig> {
  const scopedServers: Record<string, ScopedMcpServerConfig> = {}
  
  for (const [name, config] of Object.entries(servers)) {
    // 添加插件前缀：plugin:{pluginName}:{serverName}
    const scopedName = `plugin:${pluginName}:${name}`
    const scoped: ScopedMcpServerConfig = {
      ...config,
      scope: 'dynamic',
      pluginSource  // 跟踪哪个插件提供此服务器
    }
    scopedServers[scopedName] = scoped
  }
  
  return scopedServers
}
```

---

## 8. MCPB (MCP Bundle) 处理

### 8.1 MCPB 文件结构

MCPB 文件是 `.mcpb` 或 `.dxt` 包，包含：
- DXT manifest（服务器元数据）
- 服务器代码/资源
- 用户配置 schema

### 8.2 MCPB 加载

```typescript
export async function loadMcpbFile(
  mcpbPath: string,
  pluginPath: string,
  pluginId: string,
  onProgress?: (status: string) => void
): Promise<McpbLoadResult> {
  // 1. 提取 ZIP 存档
  const extractedPath = await extractMcpb(mcpbPath, pluginPath)
  
  // 2. 加载 DXT manifest
  const manifest = await loadDxtManifest(extractedPath)
  
  // 3. 检查用户配置
  const userConfigSchema = manifest.userConfig
  if (userConfigSchema) {
    // 加载保存的配置
    const savedConfig = loadMcpServerUserConfig(pluginId, manifest.name)
    
    // 针对 schema 验证
    const validation = validateUserConfig(savedConfig, userConfigSchema)
    if (!validation.valid) {
      return {
        status: 'needs-config',
        manifest,
        extractedPath,
        configSchema: userConfigSchema
      }
    }
  }
  
  // 4. 转换为 MCP 配置
  const mcpConfig = convertDxtToMcpConfig(manifest, extractedPath)
  
  return {
    status: 'success',
    manifest,
    mcpConfig,
    extractedPath
  }
}
```

---

## 9. 性能考虑

### 9.1 连接管理

- **延迟初始化**: 仅在首次使用时连接
- **连接池**: 重用现有连接
- **优雅降级**: 失败时回退到简化模式

### 9.2 缓存策略

- **工具发现缓存**: 避免重复枚举
- **资源列表缓存**: 定期刷新
- **OAuth token 缓存**: 安全存储带主动刷新

---

## 10. 安全考虑

### 10.1 认证安全

- **PKCE**: 防止授权代码拦截攻击
- **动态客户端注册**: 每个服务器唯一的客户端 ID
- **Token 存储**: 敏感数据在安全存储中
- **范围最小化**: 仅请求必要的范围

### 10.2 策略执行

- **拒绝列表优先**: 绝对阻止列出的服务器
- **命令模式匹配**: 阻止特定命令模式
- **URL 模式匹配**: 阻止特定 URL 模式
- **企业独占控制**: IT 管理员可以锁定配置

---

*文档持续更新中...*
