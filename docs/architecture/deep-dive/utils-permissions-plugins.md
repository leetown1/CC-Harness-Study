# Utils Permissions & Plugins 系统深度技术文档

> 基于逐行代码分析的完整技术文档  
> **探索完成时间**: 2026 年 4 月 1 日  
> **核心文件**: utils/permissions/ (24 文件), utils/plugins/ (44 文件)

---

## 一、Permissions 权限系统详解

### 1.1 系统架构总览

```
┌─────────────────────────────────────────────────────────────┐
│              Permissions System Architecture                 │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐  │
│  │ permissions  │    │PermissionRule│    │ Permission   │  │
│  │ .ts          │    │ .ts          │    │ Mode.ts      │  │
│  │ (1486 行)     │    │ (40 行)       │    │ (141 行)      │  │
│  │ (核心检查)    │    │ (Schema)     │    │ (模式定义)    │  │
│  └──────┬───────┘    └──────┬───────┘    └──────┬───────┘  │
│         │                   │                    │          │
│         └───────────────────┼────────────────────┘          │
│                             │                               │
│                    ┌────────▼────────┐                      │
│                    │ Permission      │                      │
│                    │ Result.ts       │                      │
│                    │ (35 行)          │                      │
│                    │ (决策类型)       │                      │
│                    └────────┬────────┘                      │
│                             │                               │
│         ┌───────────────────┼───────────────────┐          │
│         │                   │                   │          │
│  ┌──────▼───────┐   ┌──────▼───────┐   ┌──────▼───────┐  │
│  │yoloClassifier│   │classifier    │   │autoModeState │  │
│  │.ts           │   │Decision.ts   │   │.ts           │  │
│  │(1495 行)      │   │(已探索)       │   │(39 行)        │  │
│  │(两阶段分类器) │   │               │   │(状态管理)    │  │
│  └──────────────┘   └───────────────┘   └──────────────┘  │
│                                                              │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐  │
│  │PermissionUpd │    │PermissionUpd │    │permissions   │  │
│  │ate.ts        │    │ateSchema.ts  │    │Loader.ts     │  │
│  │(389 行)       │    │(78 行)        │    │(296 行)       │  │
│  │(更新应用)     │    │(Schema)      │    │(加载持久化)  │  │
│  └──────────────┘    └──────────────┘    └──────────────┘  │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

### 1.2 权限检查核心流程 (permissions.ts)

**13 步权限决策管道**:

```typescript
async function hasPermissionsToUseToolInner(
  tool: Tool,
  input: { [key: string]: unknown },
  context: ToolPermissionContext,
): Promise<PermissionDecision> {
  // 1a. 检查 deny 规则
  const denyRule = getDenyRuleForTool(context, tool)
  if (denyRule) {
    return { behavior: 'deny', decisionReason: { type: 'rule', rule: denyRule } }
  }
  
  // 1b. 检查 ask 规则
  const askRule = getAskRuleForTool(context, tool)
  if (askRule) {
    const canSandboxAutoAllow = 
      tool.name === BASH_TOOL_NAME &&
      SandboxManager.isSandboxingEnabled() &&
      shouldUseSandbox(input)
    
    if (!canSandboxAutoAllow) {
      return { behavior: 'ask', decisionReason: { type: 'rule', rule: askRule } }
    }
  }
  
  // 1c. 工具特定权限检查
  const toolPermissionResult = await tool.checkPermissions(parsedInput, context)
  
  // 1d. 工具实现拒绝
  if (toolPermissionResult?.behavior === 'deny') {
    return toolPermissionResult
  }
  
  // 1e. 需要用户交互的工具（bypass 免疫）
  if (tool.requiresUserInteraction?.() && toolPermissionResult?.behavior === 'ask') {
    return toolPermissionResult
  }
  
  // 1f. 内容特定 ask 规则优先于 bypassPermissions 模式
  if (toolPermissionResult?.behavior === 'ask' &&
      toolPermissionResult.decisionReason?.type === 'rule' &&
      toolPermissionResult.decisionReason.rule.ruleBehavior === 'ask') {
    return toolPermissionResult
  }
  
  // 1g. 安全检查（.git/, .claude/, .vscode/）免疫绕过
  if (toolPermissionResult?.behavior === 'ask' &&
      toolPermissionResult.decisionReason?.type === 'safetyCheck') {
    return toolPermissionResult
  }
  
  // 2a. 检查模式是否允许
  const shouldBypassPermissions = 
    context.mode === 'bypassPermissions' ||
    (context.mode === 'plan' && context.isBypassPermissionsModeAvailable)
  
  if (shouldBypassPermissions) {
    return { behavior: 'allow', decisionReason: { type: 'mode', mode: context.mode } }
  }
  
  // 2b. 工具是否被 allow 规则允许
  const alwaysAllowedRule = toolAlwaysAllowedRule(context, tool)
  if (alwaysAllowedRule) {
    return { behavior: 'allow', decisionReason: { type: 'rule', rule: alwaysAllowedRule } }
  }
  
  // 3. 将 "passthrough" 转换为 "ask"
  return toolPermissionResult.behavior === 'passthrough'
    ? { ...toolPermissionResult, behavior: 'ask' }
    : toolPermissionResult
}
```

**关键设计**:
- **deny 优先**: deny 规则永远优先于 allow/bypass
- **安全检查免疫**: .git/, .claude/, .vscode/ 等敏感路径即使在 bypass 模式下也需要确认
- **沙箱自动允许**: Bash 命令在沙箱模式下可自动允许

### 1.3 自动模式分类器 (yoloClassifier.ts)

**两阶段 XML 分类器**:

```typescript
async function classifyYoloActionXml(
  prefixMessages: Anthropic.MessageParam[],
  systemPrompt: string,
  userPrompt: string,
  userContentBlocks: Array<Anthropic.TextBlockParam | Anthropic.ImageBlockParam>,
  model: string,
  promptLengths: { systemPrompt: number; toolCalls: number; userPrompts: number },
  signal: AbortSignal,
  dumpContextInfo: { ... },
  mode: TwoStageMode,  // 'both' | 'fast' | 'thinking'
): Promise<YoloClassifierResult> {
  // Stage 1: 快速决策（64 tokens，stop_sequences=['</block>']）
  if (mode !== 'thinking') {
    const stage1Opts = {
      model,
      max_tokens: (mode === 'fast' ? 256 : 64) + thinkingPadding,
      system: systemBlocks,
      messages: [...prefixMessages, { role: 'user', content: stage1Content }],
      ...(mode !== 'fast' && { stop_sequences: ['</block>'] }),
    }
    const stage1Raw = await sideQuery(stage1Opts)
    const stage1Block = parseXmlBlock(extractTextContent(stage1Raw.content))
    
    if (stage1Block === false) {
      // 快速允许
      return { shouldBlock: false, reason: 'Allowed by fast classifier', stage: 'fast', ... }
    }
    
    if (mode === 'fast') {
      // 快速模式最终决策
      if (stage1Block === null) {
        return { shouldBlock: true, reason: 'Classifier stage 1 unparseable', stage: 'fast', ... }
      }
      return { shouldBlock: true, reason: parseXmlReason(stage1Text), stage: 'fast', ... }
    }
  }
  
  // Stage 2: 思考模式（4096 tokens，chain-of-thought）
  const stage2Opts = {
    model,
    max_tokens: 4096 + thinkingPadding,
    system: systemBlocks,
    messages: [...prefixMessages, { role: 'user', content: stage2Content }],
  }
  const stage2Raw = await sideQuery(stage2Opts)
  const stage2Block = parseXmlBlock(extractTextContent(stage2Raw.content))
  
  if (stage2Block === null) {
    return { shouldBlock: true, reason: 'Classifier stage 2 unparseable', stage: 'thinking', ... }
  }
  
  return {
    thinking: parseXmlThinking(stage2Text),
    shouldBlock: stage2Block,
    reason: parseXmlReason(stage2Text),
    stage: 'thinking',
    stage1Usage, stage1DurationMs, stage1RequestId, stage1MsgId,
    stage2Usage, stage2DurationMs, stage2RequestId, stage2MsgId,
  }
}
```

**XML 解析器**:
```typescript
// 解析 <block>yes/no</block>
function parseXmlBlock(text: string): boolean | null {
  const matches = [...stripThinking(text).matchAll(/<block>(yes|no)\b(<\/block>)?/gi)]
  if (matches.length === 0) return null
  return matches[0]![1]!.toLowerCase() === 'yes'
}

// 解析 <reason>...</reason>
function parseXmlReason(text: string): string | null {
  const matches = [...stripThinking(text).matchAll(/<reason>([\s\S]*?)<\/reason>/g)]
  if (matches.length === 0) return null
  return matches[0]![1]!.trim()
}

// 解析 <thinking>...</thinking>
function parseXmlThinking(text: string): string | null {
  const match = /<thinking>([\s\S]*?)<\/thinking>/.exec(text)
  return match ? match[1]!.trim() : null
}

// 移除 thinking 内容，避免误解析
function stripThinking(text: string): string {
  return text
    .replace(/<thinking>[\s\S]*?<\/thinking>/g, '')
    .replace(/<thinking>[\s\S]*$/, '')
}
```

**白名单工具**:
```typescript
const SAFE_YOLO_ALLOWLISTED_TOOLS = new Set([
  // 只读文件操作
  FILE_READ_TOOL_NAME,
  // 搜索/只读
  GREP_TOOL_NAME, GLOB_TOOL_NAME, LSP_TOOL_NAME, TOOL_SEARCH_TOOL_NAME,
  LIST_MCP_RESOURCES_TOOL_NAME, 'ReadMcpResourceTool',
  // 任务管理（仅元数据）
  TODO_WRITE_TOOL_NAME, TASK_CREATE_TOOL_NAME, TASK_GET_TOOL_NAME,
  TASK_UPDATE_TOOL_NAME, TASK_LIST_TOOL_NAME, TASK_STOP_TOOL_NAME, TASK_OUTPUT_TOOL_NAME,
  // 计划模式/UI
  ASK_USER_QUESTION_TOOL_NAME, ENTER_PLAN_MODE_TOOL_NAME, EXIT_PLAN_MODE_TOOL_NAME,
  // Swarm 协调
  TEAM_CREATE_TOOL_NAME, TEAM_DELETE_TOOL_NAME, SEND_MESSAGE_TOOL_NAME,
  // 其他安全工具
  SLEEP_TOOL_NAME, YOLO_CLASSIFIER_TOOL_NAME,
  // Ant-only 安全工具
  ...(TERMINAL_CAPTURE_TOOL_NAME ? [TERMINAL_CAPTURE_TOOL_NAME] : []),
  ...(OVERFLOW_TEST_TOOL_NAME ? [OVERFLOW_TEST_TOOL_NAME] : []),
  ...(VERIFY_PLAN_EXECUTION_TOOL_NAME ? [VERIFY_PLAN_EXECUTION_TOOL_NAME] : []),
])

export function isAutoModeAllowlistedTool(toolName: string): boolean {
  return SAFE_YOLO_ALLOWLISTED_TOOLS.has(toolName)
}
```

### 1.4 拒绝跟踪机制

**DenialTrackingState**:
```typescript
export type DenialTrackingState = {
  consecutiveDenials: number  // 连续拒绝次数
  totalDenials: number        // 总拒绝次数
}

export const DENIAL_LIMITS = {
  maxConsecutive: 3,   // 连续 3 次拒绝 → 回退到提示
  maxTotal: 20,        // 总共 20 次拒绝 → 回退到提示
}

export function recordDenial(state: DenialTrackingState): DenialTrackingState {
  return {
    consecutiveDenials: state.consecutiveDenials + 1,
    totalDenials: state.totalDenials + 1,
  }
}

export function recordSuccess(state: DenialTrackingState): DenialTrackingState {
  if (state.consecutiveDenials === 0) return state
  return { ...state, consecutiveDenials: 0 }
}

export function shouldFallbackToPrompting(state: DenialTrackingState): boolean {
  return (
    state.consecutiveDenials >= DENIAL_LIMITS.maxConsecutive ||
    state.totalDenials >= DENIAL_LIMITS.maxTotal
  )
}
```

### 1.5 权限更新应用 (PermissionUpdate.ts)

**更新类型**:
```typescript
export type PermissionUpdate =
  | { type: 'addRules'; rules: PermissionRuleValue[]; behavior: PermissionBehavior; destination: PermissionUpdateDestination }
  | { type: 'replaceRules'; rules: PermissionRuleValue[]; behavior: PermissionBehavior; destination: PermissionUpdateDestination }
  | { type: 'removeRules'; rules: PermissionRuleValue[]; behavior: PermissionBehavior; destination: PermissionUpdateDestination }
  | { type: 'setMode'; mode: ExternalPermissionMode; destination: PermissionUpdateDestination }
  | { type: 'addDirectories'; directories: string[]; destination: PermissionUpdateDestination }
  | { type: 'removeDirectories'; directories: string[]; destination: PermissionUpdateDestination }

export type PermissionUpdateDestination =
  | 'userSettings' | 'projectSettings' | 'localSettings' | 'session' | 'cliArg'
```

**应用逻辑**:
```typescript
export function applyPermissionUpdate(
  context: ToolPermissionContext,
  update: PermissionUpdate,
): ToolPermissionContext {
  switch (update.type) {
    case 'setMode':
      return { ...context, mode: update.mode }
    
    case 'addRules': {
      const ruleKind = update.behavior === 'allow' ? 'alwaysAllowRules'
                       : update.behavior === 'deny' ? 'alwaysDenyRules'
                       : 'alwaysAskRules'
      return {
        ...context,
        [ruleKind]: {
          ...context[ruleKind],
          [update.destination]: [
            ...(context[ruleKind][update.destination] || []),
            ...update.rules.map(permissionRuleValueToString),
          ],
        },
      }
    }
    
    case 'replaceRules': {
      const ruleKind = update.behavior === 'allow' ? 'alwaysAllowRules'
                       : update.behavior === 'deny' ? 'alwaysDenyRules'
                       : 'alwaysAskRules'
      return {
        ...context,
        [ruleKind]: {
          ...context[ruleKind],
          [update.destination]: update.rules.map(permissionRuleValueToString),
        },
      }
    }
    
    case 'removeRules': {
      const ruleKind = update.behavior === 'allow' ? 'alwaysAllowRules'
                       : update.behavior === 'deny' ? 'alwaysDenyRules'
                       : 'alwaysAskRules'
      const existingRules = context[ruleKind][update.destination] || []
      const rulesToRemove = new Set(update.rules.map(permissionRuleValueToString))
      const filteredRules = existingRules.filter(rule => !rulesToRemove.has(rule))
      return {
        ...context,
        [ruleKind]: {
          ...context[ruleKind],
          [update.destination]: filteredRules,
        },
      }
    }
    
    case 'addDirectories': {
      const newAdditionalDirs = new Map(context.additionalWorkingDirectories)
      for (const directory of update.directories) {
        newAdditionalDirs.set(directory, { path: directory, source: update.destination })
      }
      return { ...context, additionalWorkingDirectories: newAdditionalDirs }
    }
    
    case 'removeDirectories': {
      const newAdditionalDirs = new Map(context.additionalWorkingDirectories)
      for (const directory of update.directories) {
        newAdditionalDirs.delete(directory)
      }
      return { ...context, additionalWorkingDirectories: newAdditionalDirs }
    }
  }
}
```

---

## 二、Plugins 插件系统详解

### 2.1 系统架构总览

```
┌─────────────────────────────────────────────────────────────┐
│               Plugins System Architecture                    │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐  │
│  │pluginLoader  │    │marketplace   │    │mcpPlugin     │  │
│  │.ts           │    │Manager.ts    │    │Integration.ts│  │
│  │(加载器)       │    │(市场管理)     │    │(MCP 集成)     │  │
│  └──────┬───────┘    └──────┬───────┘    └──────┬───────┘  │
│         │                   │                    │          │
│         └───────────────────┼────────────────────┘          │
│                             │                               │
│                    ┌────────▼────────┐                      │
│                    │pluginOperations │                      │
│                    │.ts              │                      │
│                    │(安装/卸载/更新)  │                      │
│                    └────────┬────────┘                      │
│                             │                               │
│         ┌───────────────────┼───────────────────┐          │
│         │                   │                   │          │
│  ┌──────▼───────┐   ┌──────▼───────┐   ┌──────▼───────┐  │
│  │pluginCli     │   │PluginInstall │   │builtinPlugins│  │
│  │Commands.ts   │   │ationManager  │   │.ts           │  │
│  │(CLI 命令)     │   │.ts           │   │(内置插件)    │  │
│  │              │   │(安装管理)     │   │              │  │
│  └──────────────┘   └──────────────┘   └──────────────┘  │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

### 2.2 插件加载流程 (pluginLoader.ts)

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

**版本化缓存**:
```typescript
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
```

### 2.3 插件操作 (pluginOperations.ts)

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

### 2.4 CLI 插件命令 (pluginCliCommands.ts)

**插件列表处理**:
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

**插件验证流程**:
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

---

## 三、关键安全机制

### 3.1 权限安全检查

**安全检查免疫**:
```typescript
// 1g. 安全检查（.git/, .claude/, .vscode/ 等）免疫绕过
if (toolPermissionResult?.behavior === 'ask' &&
    toolPermissionResult.decisionReason?.type === 'safetyCheck') {
  return toolPermissionResult
}
```

**敏感路径保护**:
- `.git/` - Git 仓库
- `.claude/` - Claude 配置
- `.vscode/` - VSCode 配置
- Shell 配置文件

### 3.2 插件安全验证

**Manifest 验证**:
```typescript
export async function validateManifest(manifestPath: string) {
  const content = await readFile(manifestPath, 'utf-8')
  const manifest = jsonParse(content)
  
  // 1. Schema 验证
  const result = PluginManifestSchema.safeParse(manifest)
  if (!result.success) {
    return {
      valid: false,
      error: `Invalid manifest schema: ${result.error.message}`,
      fullSchema: generateSettingsJSONSchema(),
    }
  }
  
  // 2. 官方名称保护
  if (isBlockedOfficialName(manifest.name)) {
    return {
      valid: false,
      error: `Name "${manifest.name}" is blocked (impersonation risk)`,
    }
  }
  
  return { valid: true }
}
```

**官方名称保护**:
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

---

## 四、总结

### 4.1 权限系统设计哲学

1. **多层检查**: deny → ask → allow → working directory → safety checks
2. **安全优先**: deny 规则和安全检查永远优先
3. **自动模式**: AI 分类器决策，带拒绝跟踪
4. **收益递减**: 连续/总拒绝次数限制，回退到用户提示

### 4.2 插件系统设计哲学

1. **版本化缓存**: 每个版本独立缓存，支持回滚
2. **作用域隔离**: user/project/local/managed 作用域分离
3. **依赖追踪**: 反向依赖检测，卸载时警告
4. **安全验证**: Manifest schema 验证 + 官方名称保护

### 4.3 关键创新

1. **两阶段 XML 分类器**: 快速路径 (64 tokens) + 思考路径 (4096 tokens)
2. **拒绝跟踪**: 连续 3 次或总共 20 次拒绝后回退到提示
3. **安全检查免疫**: 敏感路径即使在 bypass 模式下也需要确认
4. **版本化缓存**: 支持多版本并存，平滑升级/回滚

---

*文档持续更新中...*
