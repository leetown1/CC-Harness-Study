# Settings & Permissions & Plugins 系统深度技术文档

> 基于逐行代码分析的完整技术文档  
> **探索完成时间**: 2026 年 4 月 1 日  
> **核心文件**: utils/settings/ (19 文件), utils/permissions/ (24 文件), utils/plugins/ (44 文件)

---

## 1. Settings 系统 (设置管理)

### 1.1 架构概览

**职责**: 管理 Claude Code 的所有设置来源，包括用户设置、项目设置、本地设置、策略设置和标志设置。提供设置的加载、验证、缓存、合并和变更检测功能。

**文件数量**: 19 个文件

**核心架构**:
- 多来源设置系统（5 种来源）
- 优先级合并机制
- 严格的验证系统
- 三层缓存机制
- 文件变更检测
- MDM（移动设备管理）集成

### 1.2 文件清单与职责

#### settings.ts (1149 行) - 核心实现

**职责**: 设置系统的核心实现

**设置来源优先级**（从低到高）:
1. `userSettings` - 用户全局设置 (`~/.claude/settings.json`)
2. `projectSettings` - 项目共享设置 (`.claude/settings.json`)
3. `localSettings` - 本地设置 (`.claude/settings.local.json`, gitignored)
4. `flagSettings` - CLI 标志设置
5. `policySettings` - 策略设置（远程 > HKLM/plist > managed-settings.json > HKCU）

**合并策略**:
- 使用 `lodash.mergeWith` 进行深度合并
- 数组：连接并去重
- 对象：递归合并
- 高优先级覆盖低优先级

**缓存机制**:
- 会话级缓存 (`sessionSettingsCache`)
- 按来源缓存 (`perSourceCache`)
- 解析文件缓存 (`parseFileCache`)
- 插件设置基础缓存 (`pluginSettingsBase`)

**关键函数**:

```typescript
// 加载文件型托管设置（managed-settings.json + managed-settings.d/*.json）
function loadManagedFileSettings(): {
  settings: SettingsJson | null
  errors: ValidationError[]
}

// 解析设置文件
export function parseSettingsFile(path: string): {
  settings: SettingsJson | null
  errors: ValidationError[]
}

// 获取特定来源的设置
export function getSettingsForSource(source: SettingSource): SettingsJson | null

// 更新特定来源的设置
export function updateSettingsForSource(
  source: EditableSettingSource,
  settings: SettingsJson,
): { error: Error | null }

// 获取合并后的设置（带错误）
export function getSettingsWithErrors(): SettingsWithErrors

// 获取带来源的合并设置
export function getSettingsWithSources(): SettingsWithSources
```

#### types.ts (1149 行) - 类型定义

**职责**: 定义的设置的 Zod 架构和类型

**核心架构**:
```typescript
// 设置架构（部分）
export const SettingsSchema = lazySchema(() =>
  z.object({
    $schema: z.literal(CLAUDE_CODE_SETTINGS_SCHEMA_URL).optional(),
    apiKeyHelper: z.string().optional(),
    permissions: PermissionsSchema.optional(),
    hooks: HooksSchema.optional(),
    enabledPlugins: z.record(z.string(), z.union([z.array(z.string()), z.boolean(), z.undefined()])).optional(),
    // ... 100+ 字段
  }).passthrough()
)
```

**关键类型**:
- `SettingsJson` - 设置的 JSON 表示
- `SettingsWithErrors` - 带验证错误的设置
- `ValidationError` - 验证错误详情
- `PluginHookMatcher` - 插件钩子匹配器
- `SkillHookMatcher` - 技能钩子匹配器

**向后兼容性**:
- ✅ 允许添加新字段
- ✅ 允许添加新枚举值
- ❌ 禁止删除字段
- ❌ 禁止使可选字段变为必填
- ❌ 禁止使类型更严格

#### validation.ts (266 行) - 验证系统

**职责**: 设置验证和错误格式化

**关键函数**:

```typescript
// 格式化 Zod 错误
export function formatZodError(
  error: ZodError,
  filePath: string,
): ValidationError[]

// 验证设置文件内容
export function validateSettingsFileContent(content: string):
  | { isValid: true }
  | { isValid: false; error: string; fullSchema: string }

// 过滤无效的权限规则
export function filterInvalidPermissionRules(
  data: unknown,
  filePath: string,
): ValidationError[]
```

**错误类型**:
```typescript
export type ValidationError = {
  file?: string           // 相对文件路径
  path: FieldPath         // 点分字段路径
  message: string         // 人类可读的错误消息
  expected?: string       // 期望的值或类型
  invalidValue?: unknown  // 实际的无效值
  suggestion?: string     // 修复建议
  docLink?: string        // 文档链接
  mcpErrorMetadata?: {    // MCP 配置错误元数据
    scope: ConfigScope
    serverName?: string
    severity?: 'fatal' | 'warning'
  }
}
```

#### settingsCache.ts (81 行) - 缓存管理

**职责**: 管理设置的三层缓存

**缓存结构**:
```typescript
// 会话级缓存
let sessionSettingsCache: SettingsWithErrors | null = null

// 按来源缓存
const perSourceCache = new Map<SettingSource, SettingsJson | null>()

// 解析文件缓存
const parseFileCache = new Map<string, ParsedSettings>()

// 插件设置基础
let pluginSettingsBase: Record<string, unknown> | undefined
```

**关键函数**:
- `getSessionSettingsCache()` / `setSessionSettingsCache()`
- `getCachedSettingsForSource()` / `setCachedSettingsForSource()`
- `getCachedParsedFile()` / `setCachedParsedFile()`
- `resetSettingsCache()` - 清除所有缓存

#### changeDetector.ts (489 行) - 变更检测

**职责**: 监听设置文件变更并通知系统

**核心机制**:
```typescript
// 使用 chokidar 监听文件变更
watcher = chokidar.watch(dirs, {
  persistent: true,
  ignoreInitial: true,
  depth: 0,
  awaitWriteFinish: {
    stabilityThreshold: 1000ms,
    pollInterval: 500ms,
  },
})

// MDM 轮询（30 分钟）
const MDM_POLL_INTERVAL_MS = 30 * 60 * 1000
```

**关键函数**:
- `initialize()` - 初始化文件监听
- `dispose()` - 清理监听器
- `subscribe()` - 订阅变更事件
- `notifyChange(source)` - 手动触发变更通知

**内部写入检测**:
```typescript
// 防止循环触发
const INTERNAL_WRITE_WINDOW_MS = 5000

// 标记内部写入
markInternalWrite(filePath)

// 消费标记
consumeInternalWrite(path, windowMs)
```

**删除宽限期**:
```typescript
const DELETION_GRACE_MS = 2200ms  // 处理删除 - 重建模式
```

#### applySettingsChange.ts (93 行) - 变更应用

**职责**: 应用设置变更到应用状态

**关键流程**:
```typescript
export function applySettingsChange(
  source: SettingSource,
  setAppState: (f: (prev: AppState) => AppState) => void,
): void {
  const newSettings = getInitialSettings()
  
  // 重新加载权限规则
  const updatedRules = loadAllPermissionRulesFromDisk()
  
  // 更新钩子配置快照
  updateHooksConfigSnapshot()
  
  // 更新应用状态
  setAppState(prev => ({
    ...prev,
    settings: newSettings,
    toolPermissionContext: newContext,
  }))
}
```

### 1.3 MDM 集成

#### mdm/settings.ts (317 行) - MDM 设置读取

**职责**: MDM（移动设备管理）设置读取和解析

**平台支持**:
- **macOS**: `/Library/Managed Preferences/com.anthropic.claudecode.plist`
- **Windows**: `HKLM\SOFTWARE\Policies\ClaudeCode` (管理员) 和 `HKCU\SOFTWARE\Policies\ClaudeCode` (用户)
- **Linux**: 无 MDM（使用 `/etc/claude-code/managed-settings.json`）

**优先级**（第一个获胜）:
1. 远程设置（最高）
2. HKLM/plist（管理员 MDM）
3. managed-settings.json（基于文件）
4. HKCU（用户可写，最低）

**启动加载**:
```typescript
// 早期并行启动
export function startMdmSettingsLoad(): void {
  mdmLoadPromise = (async () => {
    const rawPromise = getMdmRawReadPromise() ?? fireRawRead()
    const { mdm, hkcu } = consumeRawReadResult(await rawPromise)
    mdmCache = mdm
    hkcuCache = hkcu
  })()
}
```

#### mdm/constants.ts (82 行) - MDM 常量

**职责**: MDM 常量和路径构建器

**常量**:
```typescript
export const MACOS_PREFERENCE_DOMAIN = 'com.anthropic.claudecode'
export const WINDOWS_REGISTRY_KEY_PATH_HKLM = 'HKLM\\SOFTWARE\\Policies\\ClaudeCode'
export const WINDOWS_REGISTRY_KEY_PATH_HKCU = 'HKCU\\SOFTWARE\\Policies\\ClaudeCode'
export const WINDOWS_REGISTRY_VALUE_NAME = 'Settings'
export const PLUTIL_PATH = '/usr/bin/plutil'
export const MDM_SUBPROCESS_TIMEOUT_MS = 5000
```

#### mdm/rawRead.ts (131 行) - MDM 原始读取

**职责**: MDM 原始 subprocess 读取

**关键函数**:
- `startMdmRawRead()` - 启动启动时读取
- `getMdmRawReadPromise()` - 获取启动读取 promise
- `fireRawRead()` - 按需触发新鲜读取

**macOS 实现**:
```typescript
// 并行读取所有 plist 路径
const allResults = await Promise.all(
  plistPaths.map(async ({ path, label }) => {
    if (!existsSync(path)) return { stdout: '', label, ok: false }
    const { stdout, code } = await execFilePromise(PLUTIL_PATH, [
      ...PLUTIL_ARGS_PREFIX,
      path,
    ])
    return { stdout, label, ok: code === 0 && !!stdout }
  })
)

// 第一个获胜
const winner = allResults.find(r => r.ok)
```

### 1.4 权限验证

#### permissionValidation.ts (263 行) - 权限规则验证

**职责**: 权限规则验证

**关键函数**:
```typescript
export function validatePermissionRule(rule: string): {
  valid: boolean
  error?: string
  suggestion?: string
  examples?: string[]
}
```

**验证规则**:
1. 空规则检查
2. 括号匹配（转义感知）
3. 空括号检查
4. MCP 规则验证
5. 工具名验证（必须大写开头）
6. Bash 特定验证（`:*` 必须在末尾）
7. 文件模式验证（不支持 `:*`）

**MCP 规则格式**:
- `mcp__server` - 服务器级别（所有工具）
- `mcp__server__*` - 通配符（等价于服务器级别）
- `mcp__server__tool` - 特定工具

**权限规则架构**:
```typescript
export const PermissionRuleSchema = lazySchema(() =>
  z.string().superRefine((val, ctx) => {
    const result = validatePermissionRule(val)
    if (!result.valid) {
      ctx.addIssue({
        code: z.ZodIssueCode.custom,
        message: result.error!,
        params: { received: val },
      })
    }
  })
)
```

### 1.5 辅助模块

#### constants.ts (203 行) - 设置常量

**职责**: 设置常量定义

**关键常量**:
```typescript
export const SETTING_SOURCES = [
  'userSettings',
  'projectSettings',
  'localSettings',
  'flagSettings',
  'policySettings',
] as const

export const CLAUDE_CODE_SETTINGS_SCHEMA_URL = 
  'https://json.schemastore.org/claude-code-settings.json'

export const CUSTOMIZATION_SURFACES = ['skills', 'agents', 'hooks', 'mcp'] as const
```

**来源显示名**:
```typescript
export function getSettingSourceDisplayNameLowercase(
  source: SettingSource | 'cliArg' | 'command' | 'session',
): string {
  switch (source) {
    case 'userSettings': return 'user settings'
    case 'projectSettings': return 'shared project settings'
    case 'localSettings': return 'project local settings'
    case 'policySettings': return 'enterprise managed settings'
  }
}
```

#### managedPath.ts (35 行) - 托管路径

**职责**: 托管设置路径管理

**关键函数**:
```typescript
export const getManagedFilePath = memoize(function (): string {
  switch (getPlatform()) {
    case 'macos': return '/Library/Application Support/ClaudeCode'
    case 'windows': return 'C:\\Program Files\\ClaudeCode'
    default: return '/etc/claude-code'
  }
})

export const getManagedSettingsDropInDir = memoize(function (): string {
  return join(getManagedFilePath(), 'managed-settings.d')
})
```

#### pluginOnlyPolicy.ts (61 行) - 插件独占策略

**职责**: 插件独占策略检查

**关键函数**:
```typescript
export function isRestrictedToPluginOnly(surface: CustomizationSurface): boolean {
  const policy = getSettingsForSource('policySettings')?.strictPluginOnlyCustomization
  if (policy === true) return true
  if (Array.isArray(policy)) return policy.includes(surface)
  return false
}

export function isSourceAdminTrusted(source: string | undefined): boolean {
  return source !== undefined && ADMIN_TRUSTED_SOURCES.has(source)
}
```

**管理员信任来源**:
- `plugin` - 通过 `strictKnownMarketplaces` 门控
- `policySettings` - 来自托管设置
- `built-in` / `builtin` / `bundled` - CLI 自带

---

## 2. Permissions 系统 (权限管理)

### 2.1 架构概览

**职责**: 管理工具使用的权限检查、规则验证、分类器决策。

**文件数量**: 24 个文件

### 2.2 核心文件

#### permissions.ts - 权限检查核心

**权限模式层次**:
```typescript
type PermissionMode =
  | 'acceptEdits'      // 自动批准安全工作区文件编辑
  | 'bypassPermissions' // 自动批准所有（安全检查除外）
  | 'default'          // 询问所有
  | 'dontAsk'          // 自动拒绝所有
  | 'plan'             // 只读模式
  | 'auto'             // AI 分类器决策
  | 'bubble'           // 将提示冒泡到父终端
```

**权限决策管道** (10+ 步骤):
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

#### yoloClassifier.ts - 自动模式分类器

**职责**: AI 驱动的权限决策分类器

**两阶段分类**:
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

**Stage 1 特征**:
- 64 tokens
- stop_sequences
- 立即决策

**Stage 2 特征**:
- 4096 tokens
- chain-of-thought
- 减少误报

#### classifierDecision.ts - 分类器决策

**职责**: 分类器决策处理和记录

**拒绝追踪**:
```typescript
const DENIAL_LIMITS = {
  maxConsecutive: 3,  // 连续拒绝限制
  maxTotal: 20,       // 总拒绝限制
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

### 2.3 工具验证配置

#### toolValidationConfig.ts (104 行) - 工具验证配置

**职责**: 工具验证配置

**配置**:
```typescript
export const TOOL_VALIDATION_CONFIG: ToolValidationConfig = {
  filePatternTools: ['Read', 'Write', 'Edit', 'Glob', 'NotebookRead', 'NotebookEdit'],
  bashPrefixTools: ['Bash'],
  customValidation: {
    WebSearch: content => {
      if (content.includes('*') || content.includes('?')) {
        return { valid: false, error: 'WebSearch does not support wildcards' }
      }
      return { valid: true }
    },
    WebFetch: content => {
      if (!content.startsWith('domain:')) {
        return { valid: false, error: 'WebFetch permissions must use "domain:" prefix' }
      }
      return { valid: true }
    },
  },
}
```

---

## 3. Plugins 系统 (插件管理)

### 3.1 架构概览

**职责**: 管理插件的加载、安装、启用、禁用、更新和卸载。

**文件数量**: 44 个文件

### 3.2 核心文件

#### pluginLoader.ts - 插件加载器

**职责**: 加载和解析插件

**加载流程**:
```
1. 解析插件标识符 (name@marketplace)
   ↓
2. 查找市场配置
   ↓
3. 下载/解析源
   ↓
4. 验证 manifest
   ↓
5. 复制到版本化缓存
   ↓
6. 更新安装信息
   ↓
7. 清除缓存
```

#### marketplaceManager.ts - 市场管理器

**职责**: 管理插件市场配置

**市场类型**:
- 官方市场 (Anthropic)
- 第三方市场
- 本地市场

**关键函数**:
```typescript
// 加载已知市场配置
export async function loadKnownMarketplacesConfig(): Promise<MarketplaceConfigs>

// 获取市场
export async function getMarketplace(name: string): Promise<Marketplace | null>

// 清除市场缓存
export function clearMarketplacesCache(): void
```

#### pluginOperations.ts - 插件操作

**职责**: 实现插件的核心操作（安装/卸载/启用/禁用/更新）

**安装操作**:
```typescript
export async function installPluginOp(plugin, scope = 'user') {
  assertInstallableScope(scope)
  
  const { name: pluginName, marketplace } = parsePluginIdentifier(plugin)
  
  // 1. 搜索市场
  let foundPlugin: PluginMarketplaceEntry | undefined
  if (marketplace) {
    const pluginInfo = await getPluginById(plugin)
    foundPlugin = pluginInfo?.entry
  } else {
    const marketplaces = await loadKnownMarketplacesConfig()
    for (const [mktName, mktConfig] of Object.entries(marketplaces)) {
      const marketplace = await getMarketplace(mktName)
      const pluginEntry = marketplace.plugins.find(p => p.name === pluginName)
      if (pluginEntry) {
        foundPlugin = pluginEntry
        break
      }
    }
  }
  
  if (!foundPlugin) {
    return { success: false, message: `Plugin "${pluginName}" not found` }
  }
  
  const pluginId = `${foundPlugin.name}@${foundMarketplace}`
  
  // 2. 安装解析的插件
  const result = await installResolvedPlugin({
    pluginId,
    entry: foundPlugin,
    scope,
    marketplaceInstallLocation,
  })
  
  if (!result.ok) {
    switch (result.reason) {
      case 'blocked-by-policy':
        return { success: false, message: 'Blocked by policy' }
      case 'dependency-blocked-by-policy':
        return { success: false, message: `Dependency "${result.blockedDependency}" blocked` }
      // ...
    }
  }
  
  return {
    success: true,
    message: `Successfully installed: ${pluginId}`,
    pluginId,
    pluginName: foundPlugin.name,
    scope,
  }
}
```

**卸载操作**:
```typescript
export async function uninstallPluginOp(plugin, scope = 'user', deleteDataDir = true) {
  assertInstallableScope(scope)
  
  const { enabled, disabled } = await loadAllPlugins()
  const allPlugins = [...enabled, ...disabled]
  
  // 1. 查找插件
  const foundPlugin = findPluginByIdentifier(plugin, allPlugins)
  
  let pluginId: string
  let pluginName: string
  
  if (foundPlugin) {
    pluginId = findMatchingSettingsKey(foundPlugin)
    pluginName = foundPlugin.name
  } else {
    // 从市场中删除 → 回退到 installed_plugins.json
    const resolved = resolveDelistedPluginId(plugin)
    if (!resolved) {
      return { success: false, message: 'Plugin not found' }
    }
    pluginId = resolved.pluginId
    pluginName = resolved.pluginName
  }
  
  // 2. 检查作用域安装
  const scopeInstallation = findScopeInstallation(pluginId, scope)
  if (!scopeInstallation) {
    return { success: false, message: 'Not installed in this scope' }
  }
  
  // 3. 从设置中移除
  updateSettingsForSource(settingSource, {
    enabledPlugins: { ...settings?.enabledPlugins, [pluginId]: undefined },
  })
  
  // 4. 清除缓存
  clearAllCaches()
  
  // 5. 从 installed_plugins_v2.json 移除
  removePluginInstallation(pluginId, scope, projectPath)
  
  // 6. 清理数据和选项
  const isLastScope = !remainingInstallations || remainingInstallations.length === 0
  if (isLastScope) {
    await markPluginVersionOrphaned(installPath)
    deletePluginOptions(pluginId)
    if (deleteDataDir) {
      await deletePluginDataDir(pluginId)
    }
  }
  
  // 7. 警告依赖
  const reverseDependents = findReverseDependents(pluginId, allPlugins)
  const depWarn = formatReverseDependentsSuffix(reverseDependents)
  
  return {
    success: true,
    message: `Successfully uninstalled: ${pluginName}${depWarn}`,
    reverseDependents,
  }
}
```

### 3.3 插件 CLI 命令

#### pluginCliCommands.ts - CLI 命令包装

**职责**: 将插件操作包装为 CLI 命令

**错误处理**:
```typescript
function handlePluginCommandError(error, command, plugin?) {
  logError(error)
  
  const telemetryFields = plugin
    ? (() => {
        const { name, marketplace } = parsePluginIdentifier(plugin)
        return {
          _PROTO_plugin_name: name,
          ...(marketplace && { _PROTO_marketplace_name: marketplace }),
          ...buildPluginTelemetryFields(name, marketplace, getManagedPluginNames()),
        }
      })()
    : {}
  
  logEvent('tengu_plugin_command_failed', {
    command,
    error_category: classifyPluginCommandError(error),
    ...telemetryFields,
  })
  
  process.exit(1)
}
```

**安装命令**:
```typescript
export async function installPlugin(plugin, scope = 'user') {
  console.log(`Installing plugin "${plugin}"...`)
  
  const result = await installPluginOp(plugin, scope)
  if (!result.success) {
    throw new Error(result.message)
  }
  
  console.log(`✓ ${result.message}`)
  
  const { name, marketplace } = parsePluginIdentifier(result.pluginId || plugin)
  logEvent('tengu_plugin_installed_cli', {
    _PROTO_plugin_name: name,
    ...(marketplace && { _PROTO_marketplace_name: marketplace }),
    scope: result.scope || scope,
    install_source: 'cli-explicit',
    ...buildPluginTelemetryFields(name, marketplace, getManagedPluginNames()),
  })
  
  process.exit(0)
}
```

---

## 4. 依赖关系图

```
settings.ts
├── types.ts (SettingsSchema)
├── validation.ts (验证)
│   ├── permissionValidation.ts
│   │   └── toolValidationConfig.ts
│   ├── schemaOutput.ts
│   └── validationTips.ts
├── settingsCache.ts
├── constants.ts
├── managedPath.ts
├── changeDetector.ts
│   ├── internalWrites.ts
│   └── applySettingsChange.ts
├── mdm/
│   ├── constants.ts
│   ├── rawRead.ts
│   └── settings.ts
├── pluginOnlyPolicy.ts
├── validateEditTool.ts
└── allErrors.ts

permissions/
├── permissions.ts
├── yoloClassifier.ts
├── classifierDecision.ts
└── ...

plugins/
├── pluginLoader.ts
├── marketplaceManager.ts
├── pluginOperations.ts
└── pluginCliCommands.ts
```

---

## 5. 执行流程图

### 5.1 设置加载流程

```
启动
  ↓
startMdmRawRead() (并行启动 MDM subprocess)
  ↓
loadSettingsFromDisk()
  ↓
getPluginSettingsBase() (最低优先级基础)
  ↓
遍历 enabledSettingSources:
  ├─ policySettings (第一个获胜：远程 > HKLM/plist > 文件 > HKCU)
  ├─ userSettings
  ├─ projectSettings
  ├─ localSettings
  └─ flagSettings (+ inline settings)
  ↓
parseSettingsFile() (带缓存)
  ├─ 读取文件
  ├─ filterInvalidPermissionRules()
  └─ SettingsSchema.safeParse()
  ↓
mergeWith(settingsMergeCustomizer)
  ├─ 数组：连接并去重
  └─ 对象：递归合并
  ↓
缓存到 sessionSettingsCache
  ↓
返回 SettingsWithErrors
```

### 5.2 设置变更检测流程

```
文件变更
  ↓
chokidar.on('change'/'unlink'/'add')
  ↓
getSourceForPath(path)
  ↓
如果是删除：
  └─ 启动 DELETION_GRACE_MS (2200ms) 定时器
      ↓
      如果文件重建：取消删除，作为变更处理
      ↓
      如果定时器到期：触发 ConfigChange hook
  ↓
如果是变更/添加：
  ├─ 检查内部写入标记 (INTERNAL_WRITE_WINDOW_MS = 5000ms)
  │   └─ 如果是内部写入：忽略
  │
  └─ 如果是外部写入：
      ↓
      executeConfigChangeHooks()
      ├─ 如果 blocked：跳过
      └─ 如果 allowed：
          ↓
          fanOut(source)
          ├─ resetSettingsCache()
          └─ settingsChanged.emit(source)
              ↓
              applySettingsChange()
              ├─ getInitialSettings() (读取新缓存)
              ├─ loadAllPermissionRulesFromDisk()
              ├─ updateHooksConfigSnapshot()
              └─ setAppState()
```

### 5.3 MDM 轮询流程

```
startMdmPoll()
  ↓
捕获初始快照 (mdm + hkcu)
  ↓
setInterval(30 分钟)
  ↓
refreshMdmSettings()
  ├─ fireRawRead() (新鲜 subprocess 读取)
  └─ consumeRawReadResult() (解析)
  ↓
比较快照
  ├─ 如果相同：无操作
  └─ 如果不同：
      ├─ setMdmSettingsCache() (更新缓存)
      └─ fanOut('policySettings')
```

---

## 6. 性能优化机制

### 6.1 三层缓存

```typescript
// 1. 会话级缓存 (整个设置对象)
let sessionSettingsCache: SettingsWithErrors | null = null

// 2. 按来源缓存 (每个来源单独缓存)
const perSourceCache = new Map<SettingSource, SettingsJson | null>()

// 3. 解析文件缓存 (每个文件路径缓存解析结果)
const parseFileCache = new Map<string, ParsedSettings>()
```

**优势**:
- 避免重复文件 I/O
- 避免重复 Zod 解析
- 避免重复合并计算

### 6.2 并行启动

```typescript
// MDM 读取在模块评估时启动
startMdmRawRead()  // main.tsx 模块评估时触发

// 并行读取所有 plist 路径
const allResults = await Promise.all(
  plistPaths.map(async ({ path, label }) => {
    // ...
  })
)
```

### 6.3 快速路径优化

```typescript
// MDM plist 文件不存在时快速跳过
if (!existsSync(path)) {
  return { stdout: '', label, ok: false }
}
// 节省 ~5ms plutil subprocess 启动时间
```

### 6.4 缓存重置优化

```typescript
// 之前：每个监听器都重置缓存 → N 次磁盘重载
// 现在：fanOut 中统一重置 → 1 次磁盘重载
function fanOut(source: SettingSource): void {
  resetSettingsCache()  // 单一生产者
  settingsChanged.emit(source)
}
```

---

## 7. 错误处理策略

### 7.1 文件读取错误

```typescript
function handleFileSystemError(error: unknown, path: string): void {
  if (error.code === 'ENOENT') {
    logForDebugging(`Broken symlink or missing file: ${path}`)
  } else {
    logError(error)
  }
}
```

### 7.2 JSON 解析错误

```typescript
const data = safeParseJSON(content, false)
if (data === null) {
  return {
    isValid: false,
    error: `Invalid JSON: ${parseError.message}`,
    fullSchema: generateSettingsJSONSchema(),
  }
}
```

### 7.3 验证错误处理

```typescript
// 过滤无效权限规则（防止一个坏规则污染整个文件）
const ruleWarnings = filterInvalidPermissionRules(data, path)

const result = SettingsSchema().safeParse(data)
if (!result.success) {
  const errors = formatZodError(result.error, path)
  return { settings: null, errors: [...ruleWarnings, ...errors] }
}
```

### 7.4 MCP 错误聚合

```typescript
export function getSettingsWithAllErrors(): SettingsWithErrors {
  const result = getSettingsWithErrors()
  const mcpErrors = scopes.flatMap(scope => 
    getMcpConfigsByScope(scope).errors
  )
  return {
    settings: result.settings,
    errors: [...result.errors, ...mcpErrors],
  }
}
```

---

## 8. 总结

**utils/settings/**, **utils/permissions/**, **utils/plugins/** 模块是一个高度复杂、性能优化的设置管理系统，具有以下特点：

✅ **多来源支持**: 5 种设置来源，灵活的优先级系统
✅ **严格验证**: Zod 架构验证，详细的错误报告和修复建议
✅ **高性能**: 三层缓存，并行启动，快速路径优化
✅ **变更检测**: 文件监听 + MDM 轮询，内部写入检测
✅ **MDM 集成**: 跨平台企业策略支持
✅ **向后兼容**: 严格的向后兼容性保证
✅ **错误处理**: 优雅的错误恢复和报告机制

**总代码行数**: 约 3500+ 行 (settings) + 2000+ 行 (permissions) + 4000+ 行 (plugins) = **9500+ 行**

**核心设计模式**: 策略模式、缓存模式、观察者模式、责任链模式

---

*文档持续更新中...*
