# Plugin 系统深度技术文档

> 基于逐行代码分析的完整技术文档  
> **探索完成时间**: 2026 年 4 月 1 日  
> **核心文件**: utils/plugins/pluginLoader.ts, schemas.ts, loadPluginCommands.ts

---

## 1. Plugin 系统概述

Plugin 系统允许用户扩展 Claude Code 的功能，支持命令、技能、代理、Hook、MCP 服务器、LSP 服务器和输出样式等多种组件。

### 1.1 插件来源类型

**9 种 Marketplace 来源**:
- npm
- pip
- GitHub
- Git URL
- Git 子目录
- 本地路径
- HTTP URL
- 内置
- 管理式

**6 种 Plugin 来源**:
```typescript
export const PluginSourceSchema = lazySchema(() =>
  z.union([
    // 相对于 marketplace 的本地路径
    RelativePath(),
    
    // NPM 包
    z.object({
      source: z.literal('npm'),
      package: NpmPackageNameSchema(),
      version: z.string().optional(),
      registry: z.string().url().optional()
    }),
    
    // Python 包
    z.object({
      source: z.literal('pip'),
      package: z.string(),
      version: z.string().optional(),
      registry: z.string().url().optional()
    }),
    
    // Git URL
    z.object({
      source: z.literal('url'),
      url: z.string(),
      ref: z.string().optional(),
      sha: gitSha().optional()
    }),
    
    // GitHub 简写
    z.object({
      source: z.literal('github'),
      repo: z.string(),  // "owner/repo"
      ref: z.string().optional(),
      sha: gitSha().optional()
    }),
    
    // 单仓库子目录
    z.object({
      source: z.literal('git-subdir'),
      url: z.string(),
      path: z.string().min(1),  // 子目录路径
      ref: z.string().optional(),
      sha: gitSha().optional()
    })
  ])
)
```

---

## 2. Plugin Manifest 结构

### 2.1 完整 Manifest Schema

```typescript
export const PluginManifestSchema = lazySchema(() =>
  z.object({
    // 元数据
    name: z.string().min(1),
    version: z.string().optional(),
    description: z.string().optional(),
    author: PluginAuthorSchema().optional(),
    homepage: z.string().url().optional(),
    repository: z.string().optional(),
    license: z.string().optional(),
    keywords: z.array(z.string()).optional(),
    dependencies: z.array(DependencyRefSchema()).optional(),
    
    // Commands
    commands: z.union([
      RelativeCommandPath(),  // 单个路径
      z.array(RelativeCommandPath()),  // 多个路径
      z.record(z.string(), CommandMetadataSchema())  // 对象映射
    ]).optional(),
    
    // Skills
    skills: z.union([
      RelativePath(),
      z.array(RelativePath())
    ]).optional(),
    
    // Agents
    agents: z.union([
      RelativeMarkdownPath(),
      z.array(RelativeMarkdownPath())
    ]).optional(),
    
    // Hooks
    hooks: z.union([
      RelativeJSONPath(),
      HooksSchema(),
      z.array(z.union([RelativeJSONPath(), HooksSchema()]))
    ]).optional(),
    
    // Output Styles
    outputStyles: z.union([
      RelativePath(),
      z.array(RelativePath())
    ]).optional(),
    
    // MCP Servers
    mcpServers: z.union([
      RelativeJSONPath(),  // 路径到 .mcp.json
      McpbPath(),  // 路径到 .mcpb bundle
      z.record(z.string(), McpServerConfigSchema()),  // 内联
      z.array(z.union([
        RelativeJSONPath(),
        McpbPath(),
        z.record(z.string(), McpServerConfigSchema())
      ]))
    ]).optional(),
    
    // LSP Servers
    lspServers: z.union([
      RelativeJSONPath(),
      z.record(z.string(), LspServerConfigSchema()),
      z.array(z.union([
        RelativeJSONPath(),
        z.record(z.string(), LspServerConfigSchema())
      ]))
    ]).optional(),
    
    // 用户配置
    userConfig: z.record(
      z.string().regex(/^[A-Za-z_]\w*$/),
      PluginUserConfigOptionSchema()
    ).optional(),
    
    // Channels (助理模式)
    channels: z.array(
      z.object({
        server: z.string().min(1),
        displayName: z.string().optional(),
        userConfig: z.record(z.string(), PluginUserConfigOptionSchema()).optional()
      })
    ).optional(),
    
    // 设置合并
    settings: z.record(z.string(), z.unknown()).optional()
  })
)
```

### 2.2 用户配置 Schema

```typescript
const PluginUserConfigOptionSchema = lazySchema(() =>
  z.object({
    type: z.enum(['string', 'number', 'boolean', 'directory', 'file']),
    title: z.string(),  // 配置对话框标签
    description: z.string(),  // 帮助文本
    required: z.boolean().optional(),
    default: z.union([
      z.string(),
      z.number(),
      z.boolean(),
      z.array(z.string())
    ]).optional(),
    multiple: z.boolean().optional(),  // 对于 string 类型：允许数组
    sensitive: z.boolean().optional(),  // 存储在安全存储中
    min: z.number().optional(),  // 对于 number 类型
    max: z.number().optional()  // 对于 number 类型
  }).strict()
)
```

**在 MCP 配置中使用**：

```json
{
  "mcpServers": {
    "telegram": {
      "type": "stdio",
      "command": "node",
      "args": ["server.js"],
      "env": {
        "BOT_TOKEN": "${user_config.botToken}",
        "OWNER_ID": "${user_config.ownerId}"
      }
    }
  },
  "channels": [
    {
      "server": "telegram",
      "displayName": "Telegram",
      "userConfig": {
        "botToken": {
          "type": "string",
          "title": "Bot Token",
          "description": "来自@BotFather 的 Telegram bot token",
          "required": true,
          "sensitive": true
        },
        "ownerId": {
          "type": "string",
          "title": "Owner ID",
          "description": "你的 Telegram 用户 ID",
          "required": true
        }
      }
    }
  ]
}
```

---

## 3. Plugin 加载流程

### 3.1 完整加载流程

```typescript
export const loadAllPluginsCacheOnly = memoize(async (): Promise<PluginLoadResult> => {
  // 1. 加载内置插件
  const { enabled: enabledBuiltins, disabled: disabledBuiltins } = 
    getBuiltinPlugins()
  
  // 2. 加载 marketplace 配置
  const marketplaces = await loadKnownMarketplacesConfigSafe()
  
  // 3. 从设置获取启用的插件 ID
  const settings = getSettings_DEPRECATED()
  const enabledPluginIds = settings?.enabledPlugins ?? {}
  
  // 4. 加载每个启用的插件
  const enabled: LoadedPlugin[] = []
  const errors: PluginError[] = []
  
  for (const [pluginId, isEnabled] of Object.entries(enabledPluginIds)) {
    if (!isEnabled) continue
    
    // 获取 marketplace 条目
    const entry = await getPluginByIdCacheOnly(pluginId, marketplaces)
    if (!entry) {
      errors.push({
        type: 'plugin-not-found',
        source: pluginId,
        pluginId,
        marketplace: extractMarketplace(pluginId)
      })
      continue
    }
    
    // 检查缓存或安装
    const pluginPath = await resolvePluginPath(pluginId, entry.source)
    
    // 加载插件 manifest
    const manifest = await loadPluginManifest(pluginPath)
    
    // 创建已加载插件对象
    const plugin: LoadedPlugin = {
      name: entry.name,
      manifest,
      path: pluginPath,
      source: pluginId,
      repository: pluginId,
      enabled: true,
      commandsPath: join(pluginPath, 'commands'),
      skillsPath: join(pluginPath, 'skills'),
      // ... 加载其他组件
    }
    
    enabled.push(plugin)
  }
  
  return { enabled, disabled: disabledBuiltins, errors }
})
```

### 3.2 版本化缓存系统

```typescript
// 缓存路径格式:
// ~/.claude/plugins/cache/{marketplace}/{plugin}/{version}/

export function getVersionedCachePath(
  pluginId: string,
  version: string
): string {
  const { name: pluginName, marketplace } = parsePluginIdentifier(pluginId)
  const sanitizedMarketplace = marketplace.replace(/[^a-zA-Z0-9\-_]/g, '-')
  const sanitizedPlugin = pluginName.replace(/[^a-zA-Z0-9\-_]/g, '-')
  const sanitizedVersion = version.replace(/[^a-zA-Z0-9\-_.]/g, '-')
  
  return join(
    getPluginsDirectory(),
    'cache',
    sanitizedMarketplace,
    sanitizedPlugin,
    sanitizedVersion
  )
}

// ZIP 缓存模式 (可选压缩)
export function getVersionedZipCachePath(
  pluginId: string,
  version: string
): string {
  return `${getVersionedCachePath(pluginId, version)}.zip`
}
```

### 3.3 种子缓存系统

```typescript
// 探测种子目录获取预填充缓存
async function probeSeedCache(
  pluginId: string,
  version: string
): Promise<string | null> {
  for (const seedDir of getPluginSeedDirs()) {
    const seedPath = getVersionedCachePathIn(seedDir, pluginId, version)
    try {
      const entries = await readdir(seedPath)
      if (entries.length > 0) return seedPath  // 缓存命中
    } catch {
      // 尝试下一个种子
    }
  }
  return null
}
```

**企业/团队种子目录**：

```typescript
export function getPluginSeedDirs(): string[] {
  const seedDirs: string[] = []
  
  // 管理种子 (企业)
  const managedSeedDir = process.env.CLAUDE_PLUGIN_SEED_DIR
  if (managedSeedDir) {
    seedDirs.push(managedSeedDir)
  }
  
  // 系统范围种子
  if (getPlatform() === 'darwin') {
    seedDirs.push('/Library/Application Support/Claude/plugins/seed')
  }
  
  return seedDirs
}
```

---

## 4. Plugin 组件加载

### 4.1 插件命令加载

```typescript
export const getPluginCommands = memoize(async (): Promise<Command[]> => {
  if (isBareMode() && getInlinePlugins().length === 0) {
    return []
  }
  
  const { enabled, errors } = await loadAllPluginsCacheOnly()
  
  const perPluginCommands = await Promise.all(
    enabled.map(async (plugin): Promise<Command[]> => {
      const loadedPaths = new Set<string>()
      const pluginCommands: Command[] = []
      
      // 从默认命令目录加载
      if (plugin.commandsPath) {
        const commands = await loadCommandsFromDirectory(
          plugin.commandsPath,
          plugin.name,
          plugin.source,
          plugin.manifest,
          plugin.path,
          { isSkillMode: false },
          loadedPaths,
        )
        pluginCommands.push(...commands)
      }
      
      // 从额外路径加载
      if (plugin.commandsPaths) {
        const pathResults = await Promise.all(
          plugin.commandsPaths.map(async (commandPath) => {
            // 处理目录和单个文件
          })
        )
        for (const commands of pathResults) {
          pluginCommands.push(...commands)
        }
      }
      
      // 加载内联内容命令
      if (plugin.commandsMetadata) {
        for (const [name, metadata] of Object.entries(plugin.commandsMetadata)) {
          if (metadata.content && !metadata.source) {
            // 处理内联 markdown 内容
          }
        }
      }
      
      return pluginCommands
    })
  )
  
  return perPluginCommands.flat()
})
```

### 4.2 插件命令创建

```typescript
function createPluginCommand(
  commandName: string,
  file: PluginMarkdownFile,
  sourceName: string,
  pluginManifest: PluginManifest,
  pluginPath: string,
  isSkill: boolean,
  config: LoadConfig = { isSkillMode: false },
): Command | null {
  const { frontmatter, content } = file
  
  const validatedDescription = coerceDescriptionToString(
    frontmatter.description,
    commandName,
  )
  const description =
    validatedDescription ??
    extractDescriptionFromMarkdown(
      content,
      isSkill ? 'Plugin skill' : 'Plugin command',
    )
  
  // 在 allowed-tools 中替换变量
  const rawAllowedTools = frontmatter['allowed-tools']
  const substitutedAllowedTools =
    typeof rawAllowedTools === 'string'
      ? substitutePluginVariables(rawAllowedTools, {
          path: pluginPath,
          source: sourceName,
        })
      : Array.isArray(rawAllowedTools)
        ? rawAllowedTools.map(tool =>
            typeof tool === 'string'
              ? substitutePluginVariables(tool, {
                  path: pluginPath,
                  source: sourceName,
                })
              : tool,
          )
        : rawAllowedTools
  
  const allowedTools = parseSlashCommandToolsFromFrontmatter(
    substitutedAllowedTools,
  )
  
  return {
    type: 'prompt',
    name: commandName,
    description,
    hasUserSpecifiedDescription: validatedDescription !== null,
    allowedTools,
    argumentHint: frontmatter['argument-hint'] as string | undefined,
    argNames: parseArgumentNames(
      frontmatter.arguments as string | string[] | undefined,
    ),
    whenToUse: frontmatter.when_to_use as string | undefined,
    version: frontmatter.version as string | undefined,
    model: frontmatter.model === 'inherit'
      ? undefined
      : frontmatter.model
        ? parseUserSpecifiedModel(frontmatter.model as string)
        : undefined,
    effort: effortRaw !== undefined ? parseEffortValue(effortRaw) : undefined,
    disableModelInvocation: parseBooleanFrontmatter(
      frontmatter['disable-model-invocation'],
    ),
    userInvocable: userInvocableValue === undefined
      ? true
      : parseBooleanFrontmatter(userInvocableValue),
    contentLength: content.length,
    source: 'plugin',
    loadedFrom: isSkill || config.isSkillMode ? 'plugin' : undefined,
    pluginInfo: {
      pluginManifest,
      repository: sourceName,
    },
    isHidden: !userInvocable,
    progressMessage: isSkill || config.isSkillMode ? 'loading' : 'running',
    userFacingName(): string {
      return displayName || commandName
    },
    async getPromptForCommand(args, context) {
      // 内容处理和变量替换
      // ...
    },
  } satisfies Command
}
```

---

## 5. Plugin MCP 集成

### 5.1 加载插件 MCP 服务器

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
      const results = await Promise.all(
        mcpServersSpec.map(async spec => {
          if (typeof spec === 'string') {
            if (isMcpbSource(spec)) {
              return await loadMcpServersFromMcpb(plugin, spec, errors)
            }
            return await loadMcpServersFromFile(plugin.path, spec)
          }
          return spec  // 内联配置
        })
      )
      for (const result of results) {
        if (result) {
          servers = { ...servers, ...result }
        }
      }
    } else {
      // 直接 MCP 服务器配置
      servers = { ...servers, ...mcpServersSpec }
    }
  }
  
  return Object.keys(servers).length > 0 ? servers : undefined
}
```

### 5.2 插件服务器命名空间

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

## 6. Plugin 安全机制

### 6.1 官方 Marketplace 保护

```typescript
export const ALLOWED_OFFICIAL_MARKETPLACE_NAMES = new Set([
  'claude-code-marketplace',
  'claude-code-plugins',
  'anthropic-marketplace',
  // ... 保留名称
])

export const BLOCKED_OFFICIAL_NAME_PATTERN = 
  /(?:official[^a-z0-9]*(anthropic|claude)|(?:anthropic|claude)[^a-z0-9]*official|^(?:anthropic|claude)[^a-z0-9]*(marketplace|plugins|official))/i

export function isBlockedOfficialName(name: string): boolean {
  if (ALLOWED_OFFICIAL_MARKETPLACE_NAMES.has(name.toLowerCase())) {
    return false  // 在允许列表中
  }
  
  // 阻止非 ASCII 字符（同形异义字攻击）
  if (NON_ASCII_PATTERN.test(name)) {
    return true
  }
  
  // 检查冒充模式
  return BLOCKED_OFFICIAL_NAME_PATTERN.test(name)
}
```

### 6.2 来源验证

```typescript
// 对保留名称的来源验证
export function validateOfficialNameSource(
  name: string,
  source: { source: string; repo?: string; url?: string }
): string | null {
  const normalizedName = name.toLowerCase()
  
  if (!ALLOWED_OFFICIAL_MARKETPLACE_NAMES.has(normalizedName)) {
    return null  // 不是保留名称
  }
  
  // 必须来自官方 GitHub 组织
  if (source.source === 'github') {
    const repo = source.repo || ''
    if (!repo.toLowerCase().startsWith('anthropics/')) {
      return `名称 '${name}' 保留给官方 Anthropic marketplaces`
    }
    return null
  }
  
  // ... 额外来源验证
}
```

### 6.3 插件设置限制

```typescript
// 只允许白名单设置键合并
const PluginManifestSettingsSchema = lazySchema(() =>
  z.object({
    settings: z
      .record(z.string(), z.unknown())
      .optional()
      .describe(
        '启用插件时要合并的设置。' +
        '只保留白名单键（当前：agent)'
      )
  })
)
```

**当前白名单键**：
- `agent` - 代理配置

---

## 7. Plugin 依赖和去重

### 7.1 依赖解析

```typescript
// apt 风格依赖解析
dependencies: z.array(DependencyRefSchema()).optional()
```

### 7.2 跨 Marketplace 控制

- 依赖可以引用其他 marketplace 的插件
- 版本范围支持
- 循环依赖检测

---

## 8. 内置插件机制

### 8.1 内置插件注册表

```typescript
// 内置插件定义
const BUILTIN_PLUGINS = new Map<string, BuiltinPluginDefinition>([
  // ...
])
```

### 8.2 内置插件技能

```typescript
export function getBuiltinPluginSkillCommands(): Command[] {
  const { enabled } = getBuiltinPlugins()
  const commands: Command[] = []
  
  for (const plugin of enabled) {
    const definition = BUILTIN_PLUGINS.get(plugin.name)
    if (!definition?.skills) continue
    for (const skill of definition.skills) {
      commands.push(skillDefinitionToCommand(skill))
    }
  }
  
  return commands
}
```

---

## 9. 企业策略和权限控制

### 9.1 安装范围控制

- 企业可以限制插件安装来源
- 白名单/黑名单机制
- 仅允许管理式 marketplace

### 9.2 插件启用控制

- 用户可以启用/禁用已安装插件
- 会话级临时启用
- 项目级自动启用

---

## 10. 性能优化

### 10.1 缓存策略

- **版本化缓存**: 每个版本独立缓存
- **ZIP 压缩**: 可选 ZIP 模式减少磁盘占用
- **种子缓存**: 企业预填充缓存

### 10.2 懒加载

- **按需加载**: 仅在启用时加载插件
- **组件懒加载**: 命令/技能/MCP 服务器按需加载
- **Memoization**: 使用 memoize 缓存昂贵操作

---

*文档持续更新中...*
