# 插件系统深度解析

本文档详细分析 Claude Code 的插件系统实现，包括插件架构、生命周期、内置插件和市场集成。

## 一、插件系统概述

### 1.1 设计理念

插件系统允许用户通过安装插件来扩展 Claude Code 的功能。插件可以提供：
- **技能 (Skills)**: 可被模型调用的 prompt 扩展
- **命令 (Commands)**: 斜杠命令
- **钩子 (Hooks)**: 生命周期事件处理器
- **MCP 服务器**: Model Context Protocol 服务

### 1.2 核心文件

| 文件 | 职责 |
|------|------|
| `plugins/builtinPlugins.ts` | 内置插件注册与管理 |
| `plugins/bundled/index.ts` | 内置插件初始化入口 |
| `utils/plugins/loadPluginCommands.ts` | 插件命令/技能加载 |
| `utils/plugins/pluginLoader.ts` | 插件加载器 |
| `utils/plugins/pluginOptionsStorage.ts` | 插件选项存储 |
| `utils/plugins/schemas.ts` | 插件 manifest schema |
| `services/plugins/pluginOperations.ts` | 插件操作 API |
| `services/plugins/pluginCliCommands.ts` | 插件 CLI 命令 |

## 二、内置插件系统

**文件位置**: `src/plugins/builtinPlugins.ts` (159 行)

### 2.1 BuiltinPluginDefinition 类型

```typescript
import type { BundledSkillDefinition } from '../skills/bundledSkills.js'
import type { BuiltinPluginDefinition } from '../types/plugin.js'
// BuiltinPluginDefinition is defined in src/types/plugin.ts:

export type BuiltinPluginDefinition = {
  name: string
  description: string
  version?: string
  skills?: BundledSkillDefinition[]
  hooks?: HooksSettings
  mcpServers?: Record<string, McpServerConfig>
  isAvailable?: () => boolean
  defaultEnabled?: boolean
}
```

### 2.2 插件注册

```typescript
const BUILTIN_PLUGINS: Map<string, BuiltinPluginDefinition> = new Map()

export const BUILTIN_MARKETPLACE_NAME = 'builtin'

/**
 * 注册内置插件。在 startup 时的 initBuiltinPlugins() 中调用。
 */
export function registerBuiltinPlugin(
  definition: BuiltinPluginDefinition,
): void {
  BUILTIN_PLUGINS.set(definition.name, definition)
}

/**
 * 检查插件 ID 是否为内置插件（以 @builtin 结尾）。
 */
export function isBuiltinPluginId(pluginId: string): boolean {
  return pluginId.endsWith(`@${BUILTIN_MARKETPLACE_NAME}`)
}
```

### 2.3 获取内置插件

```typescript
/**
 * 获取特定内置插件定义。
 */
export function getBuiltinPluginDefinition(
  name: string,
): BuiltinPluginDefinition | undefined {
  return BUILTIN_PLUGINS.get(name)
}

/**
 * 获取所有注册的内置插件，根据用户设置分为启用/禁用。
 * isAvailable() 返回 false 的插件被完全省略。
 */
export function getBuiltinPlugins(): {
  enabled: LoadedPlugin[]
  disabled: LoadedPlugin[]
} {
  const settings = getSettings_DEPRECATED()
  const enabled: LoadedPlugin[] = []
  const disabled: LoadedPlugin[] = []

  for (const [name, definition] of BUILTIN_PLUGINS) {
    if (definition.isAvailable && !definition.isAvailable()) {
      continue
    }

    const pluginId = `${name}@${BUILTIN_MARKETPLACE_NAME}`
    const userSetting = settings?.enabledPlugins?.[pluginId]
    // 启用状态：用户偏好 > 插件默认 > true
    const isEnabled =
      userSetting !== undefined
        ? userSetting === true
        : (definition.defaultEnabled ?? true)

    const plugin: LoadedPlugin = {
      name,
      manifest: {
        name,
        description: definition.description,
        version: definition.version,
      },
      path: BUILTIN_MARKETPLACE_NAME,  // 哨兵值 — 无文件系统路径
      source: pluginId,
      repository: pluginId,
      enabled: isEnabled,
      isBuiltin: true,
      hooksConfig: definition.hooks,
      mcpServers: definition.mcpServers,
    }

    if (isEnabled) {
      enabled.push(plugin)
    } else {
      disabled.push(plugin)
    }
  }

  return { enabled, disabled }
}
```

### 2.4 获取内置插件技能

```typescript
/**
 * 获取已启用内置插件的技能作为 Command 对象。
 * 禁用插件的技能不返回。
 */
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

### 2.5 技能定义转换

```typescript
function skillDefinitionToCommand(definition: BundledSkillDefinition): Command {
  return {
    type: 'prompt',
    name: definition.name,
    description: definition.description,
    hasUserSpecifiedDescription: true,
    allowedTools: definition.allowedTools ?? [],
    argumentHint: definition.argumentHint,
    whenToUse: definition.whenToUse,
    model: definition.model,
    disableModelInvocation: definition.disableModelInvocation ?? false,
    userInvocable: definition.userInvocable ?? true,
    contentLength: 0,
    // 'bundled' 不是 'builtin' — Command.source 中的 'builtin' 表示硬编码斜杠命令
    source: 'bundled',
    loadedFrom: 'bundled',
    hooks: definition.hooks,
    context: definition.context,
    agent: definition.agent,
    isEnabled: definition.isEnabled ?? (() => true),
    isHidden: !(definition.userInvocable ?? true),
    progressMessage: 'running',
    getPromptForCommand: definition.getPromptForCommand,
  }
}
```

## 三、插件命令加载

**文件位置**: `src/utils/plugins/loadPluginCommands.ts` (647+ 行)

### 3.1 getPluginCommands()

```typescript
/**
 * 获取所有已安装插件的命令。
 */
export const getPluginCommands = memoize(async (): Promise<Command[]> => {
  const { enabled } = await loadAllPluginsCacheOnly()
  const commands: Command[] = []

  for (const plugin of enabled) {
    const pluginCommandsPath = join(plugin.path, 'commands')
    if (!existsSync(pluginCommandsPath)) continue

    const pluginCommands = await loadCommandsFromDirectory(
      pluginCommandsPath,
      plugin.name,
      plugin.source,
      plugin.manifest,
      plugin.path,
      { isSkillMode: false },
      new Set(),
    )

    commands.push(...pluginCommands)
  }

  return commands
})

export function clearPluginCommandCache(): void {
  getPluginCommands.cache?.clear?.()
}
```

### 3.2 getPluginSkills()

```typescript
/**
 * 获取所有已安装插件的技能。
 */
export const getPluginSkills = memoize(async (): Promise<Command[]> => {
  const { enabled } = await loadAllPluginsCacheOnly()
  const skills: Command[] = []

  for (const plugin of enabled) {
    const pluginSkillsPath = join(plugin.path, 'skills')
    if (!existsSync(pluginSkillsPath)) continue

    const pluginSkills = await loadCommandsFromDirectory(
      pluginSkillsPath,
      plugin.name,
      plugin.source,
      plugin.manifest,
      plugin.path,
      { isSkillMode: true },
      new Set(),
    )

    skills.push(...pluginSkills)
  }

  return skills
})

export function clearPluginSkillsCache(): void {
  getPluginSkills.cache?.clear?.()
}
```

### 3.3 命令加载配置

```typescript
type LoadConfig = {
  isSkillMode: boolean  // true 时从 skills/ 目录加载
}

async function loadCommandsFromDirectory(
  commandsPath: string,
  pluginName: string,
  sourceName: string,
  pluginManifest: PluginManifest,
  pluginPath: string,
  config: LoadConfig = { isSkillMode: false },
  loadedPaths: Set<string> = new Set(),
): Promise<Command[]> {
  // 收集所有 markdown 文件
  const markdownFiles = await collectMarkdownFiles(
    commandsPath,
    commandsPath,
    loadedPaths,
  )

  // 应用技能转换
  const processedFiles = transformPluginSkillFiles(markdownFiles)

  // 转换为命令
  const commands: Command[] = []
  for (const file of processedFiles) {
    const commandName = getCommandNameFromFile(
      file.filePath,
      file.baseDir,
      pluginName,
    )

    const command = createPluginCommand(
      commandName,
      file,
      sourceName,
      pluginManifest,
      pluginPath,
      isSkillFile(file.filePath),
      config,
    )

    if (command) {
      commands.push(command)
    }
  }

  return commands
}
```

### 3.4 插件命令创建

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
  try {
    const { frontmatter, content } = file

    // 解析 frontmatter 字段
    const description = validatedDescription ??
      extractDescriptionFromMarkdown(content, isSkill ? 'Plugin skill' : 'Plugin command')

    // 替换 ${CLAUDE_PLUGIN_ROOT} 变量
    const substitutedAllowedTools = substitutePluginVariables(rawAllowedTools, {
      path: pluginPath,
      source: sourceName,
    })

    return {
      type: 'prompt',
      name: commandName,
      description,
      hasUserSpecifiedDescription: validatedDescription !== null,
      allowedTools,
      argumentHint,
      argNames: argumentNames.length > 0 ? argumentNames : undefined,
      whenToUse,
      version,
      model,
      disableModelInvocation,
      userInvocable,
      context: executionContext,
      agent,
      effort,
      contentLength: content.length,
      isHidden: !userInvocable,
      progressMessage: isSkill ? 'loading' : 'running',
      source: 'plugin',
      loadedFrom: 'plugin',
      pluginInfo: {
        pluginManifest,
        repository: sourceName,
      },
      skillRoot: pluginPath,
      hooks,
      async getPromptForCommand(args, toolUseContext) {
        // 处理参数替换和变量扩展
        let finalContent = substituteArguments(content, args, true, argumentNames)
        
        // 替换 ${CLAUDE_SKILL_DIR}
        if (pluginPath) {
          finalContent = finalContent.replace(/\$\{CLAUDE_SKILL_DIR\}/g, pluginPath)
        }
        
        // 替换 ${CLAUDE_PLUGIN_ROOT}
        finalContent = substitutePluginVariables(finalContent, {
          path: pluginPath,
          source: sourceName,
        })

        // 替换用户配置变量
        const options = await loadPluginOptions(sourceName)
        finalContent = substituteUserConfigInContent(finalContent, options)

        return [{ type: 'text', text: finalContent }]
      },
    }
  } catch (error) {
    logError(error)
    return null
  }
}
```

## 四、命令与技能的区别

### 4.1 loadedFrom 差异

| 来源 | loadedFrom | 说明 |
|------|------------|------|
| 插件命令 (commands/) | `undefined`（非技能命令） | 普通命令 loadedFrom 为 undefined |
| 插件技能 (skills/) | `'plugin'` | 技能获得特殊处理和提示前缀 |

### 4.2 特殊处理差异

```typescript
// 技能获得特殊前缀
if (isSkill) {
  // "Base directory for this skill: <dir>"
  // ${CLAUDE_SKILL_DIR} 变量替换
  // progressMessage: 'loading' vs 'running'
}
```

## 五、插件热重载

### 5.1 /reload-plugins 命令

**文件位置**: `src/commands/reload-plugins/reload-plugins.ts`

此命令触发 `refreshActivePlugins()`（位于 `src/utils/plugins/refresh.ts`），
执行完整的插件重新加载流程：清除所有缓存、重新加载插件、提取 MCP/LSP 服务器、
重建 hooks 注册表，然后更新 AppState。

```typescript
export async function refreshActivePlugins(
  setAppState: SetAppState,
): Promise<RefreshActivePluginsResult> {
  clearAllCaches()
  clearPluginCacheExclusions()

  const pluginResult = await loadAllPlugins()
  const [pluginCommands, agentDefinitions] = await Promise.all([
    getPluginCommands(),
    getAgentDefinitionsWithOverrides(getOriginalCwd()),
  ])

  // 加载 MCP/LSP 服务器配置
  // ...

  setAppState(prev => ({
    ...prev,
    plugins: {
      enabled, disabled, commands: pluginCommands,
      errors: mergePluginErrors(prev.plugins.errors, errors),
      needsRefresh: false,
    },
    agentDefinitions,
    mcp: {
      ...prev.mcp,
      pluginReconnectKey: prev.mcp.pluginReconnectKey + 1,
    },
  }))

  reinitializeLspServerManager()
  // 重建 hooks 注册表、恢复 OAuth token 等
}

// 返回结果包含：enabled_count, disabled_count, command_count,
// agent_count, hook_count, mcp_count, lsp_count, error_count
```

## 六、插件 Manifest Schema

**文件位置**: `src/utils/plugins/schemas.ts`

```typescript
export const PluginManifestSchema = lazySchema(() =>
  z.object({
    ...PluginManifestMetadataSchema().shape,
    ...PluginManifestHooksSchema().partial().shape,
    ...PluginManifestCommandsSchema().partial().shape,
    ...PluginManifestAgentsSchema().partial().shape,
    ...PluginManifestSkillsSchema().partial().shape,
    ...PluginManifestOutputStylesSchema().partial().shape,
    ...PluginManifestChannelsSchema().partial().shape,
    ...PluginManifestMcpServerSchema().partial().shape,
    ...PluginManifestLspServerSchema().partial().shape,
    ...PluginManifestSettingsSchema().partial().shape,
    ...PluginManifestUserConfigSchema().partial().shape,
  }),
)

export type PluginManifest = z.infer<typeof PluginManifestSchema>
```

## 七、插件选项存储

**文件位置**: `src/utils/plugins/pluginOptionsStorage.ts`

```typescript
/**
 * 加载插件选项，合并非敏感（settings.json pluginConfigs[pluginId].options）
 * 和敏感（secureStorage pluginSecrets[pluginId]）值。
 * SecureStorage 在键冲突时优先。按 pluginId memoize。
 */
export const loadPluginOptions = memoize(
  (pluginId: string): PluginOptionValues => {
    const settings = getSettings_DEPRECATED()
    const nonSensitive =
      settings.pluginConfigs?.[pluginId]?.options ?? ({} as PluginOptionValues)
    const storage = getSecureStorage()
    const sensitive =
      storage.read()?.pluginSecrets?.[pluginId] ?? ({} as Record<string, string>)
    return { ...nonSensitive, ...sensitive }
  },
)

/**
 * 保存插件选项，按 schema[key].sensitive 拆分存储目标：
 *   - sensitive: true  → secureStorage
 *   - 其他             → settings.json pluginConfigs[pluginId].options
 */
export function savePluginOptions(
  pluginId: string,
  values: PluginOptionValues,
  schema: PluginOptionSchema,
): void {
  // 拆分敏感/非敏感值
  // 先写 secureStorage，再写 settings.json
  // 交叉擦除：将本次写入的敏感键从 settings 中清除，反之亦然
}

/**
 * 替换插件变量
 *   ${CLAUDE_PLUGIN_ROOT} — 插件安装目录
 *   ${CLAUDE_PLUGIN_DATA} — 持久化数据目录（跨更新保留）
 */
export function substitutePluginVariables(
  value: string,
  plugin: { path: string; source?: string },
): string {
  const normalize = (p: string) =>
    process.platform === 'win32' ? p.replace(/\\/g, '/') : p
  let out = value.replace(/\$\{CLAUDE_PLUGIN_ROOT\}/g, () =>
    normalize(plugin.path),
  )
  if (plugin.source) {
    out = out.replace(/\$\{CLAUDE_PLUGIN_DATA\}/g, () =>
      normalize(getPluginDataDir(plugin.source!)),
    )
  }
  return out
}

/**
 * 替换用户配置内容（用于技能/代理提示文本）
 *   ${user_config.KEY} → 已保存的值
 *   敏感键替换为占位符: [sensitive option 'KEY' not available in skill content]
 *   未知键保留原样（不抛出）
 */
export function substituteUserConfigInContent(
  content: string,
  options: PluginOptionValues,
  schema: PluginOptionSchema,
): string {
  return content.replace(/\$\{user_config\.([^}]+)\}/g, (match, key) => {
    if (schema[key]?.sensitive === true) {
      return `[sensitive option '${key}' not available in skill content]`
    }
    const value = options[key]
    if (value === undefined) return match
    return String(value)
  })
}
```

## 八、插件生命周期

```
插件生命周期
┌─────────────────────────────────────────────────────────────┐
│ 安装阶段                                                     │
│   /plugin install <plugin-id>                               │
│   - 下载插件包                                              │
│   - 验证 manifest                                           │
│   - 存储到插件目录                                          │
└─────────────────────────┬───────────────────────────────────┘
                          ▼
┌─────────────────────────────────────────────────────────────┐
│ 启用阶段                                                     │
│   /plugin enable <plugin-id>                                │
│   - 更新用户设置                                            │
│   - 加载命令/技能/钩子                                      │
│   - 启动 MCP 服务器                                         │
└─────────────────────────┬───────────────────────────────────┘
                          ▼
┌─────────────────────────────────────────────────────────────┐
│ 运行阶段                                                     │
│   - 技能可通过 SkillTool 调用                               │
│   - 命令可通过斜杠命令调用                                  │
│   - 钩子响应生命周期事件                                    │
└─────────────────────────┬───────────────────────────────────┘
                          ▼
┌─────────────────────────────────────────────────────────────┐
│ 禁用/卸载阶段                                                │
│   /plugin disable <plugin-id>                               │
│   /plugin uninstall <plugin-id>                             │
│   - 清除缓存                                                │
│   - 停止 MCP 服务器                                         │
│   - 移除文件（卸载时）                                      │
└─────────────────────────────────────────────────────────────┘
```