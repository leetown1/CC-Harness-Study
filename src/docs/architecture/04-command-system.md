# 命令系统深度解析

本文档详细分析 Claude Code 的斜杠命令系统，包括命令类型、注册机制、发现流程和执行模型。

## 一、Command 类型定义

**文件位置**: `src/types/command.ts` (216 行)

### 1.1 Command 联合类型

```typescript
export type Command = CommandBase &
  (PromptCommand | LocalCommand | LocalJSXCommand)
```

### 1.2 CommandBase 基础属性

```typescript
export type CommandBase = {
  // 可用性声明
  availability?: CommandAvailability[]
  
  // 基本属性
  description: string
  hasUserSpecifiedDescription?: boolean
  isEnabled?: () => boolean    // 默认 true
  isHidden?: boolean           // 默认 false
  name: string
  aliases?: string[]
  isMcp?: boolean
  argumentHint?: string        // 参数提示（灰色显示）
  whenToUse?: string          // 使用场景描述
  version?: string            // 版本号
  disableModelInvocation?: boolean  // 禁止模型调用
  userInvocable?: boolean     // 用户是否可调用
  
  // 加载来源
  loadedFrom?:
    | 'commands_DEPRECATED'
    | 'skills'
    | 'plugin'
    | 'managed'
    | 'bundled'
    | 'mcp'
  
  kind?: 'workflow'           // 工作流标记
  immediate?: boolean         // 立即执行，不等待停止点
  isSensitive?: boolean       // 参数在历史中脱敏
  userFacingName?: () => string  // 显示名称
}
```

### 1.3 PromptCommand 类型

```typescript
export type PromptCommand = {
  type: 'prompt'
  progressMessage: string
  contentLength: number       // 内容长度（用于 token 估算）
  argNames?: string[]
  allowedTools?: string[]
  model?: string
  source: SettingSource | 'builtin' | 'mcp' | 'plugin' | 'bundled'
  pluginInfo?: {
    pluginManifest: PluginManifest
    repository: string
  }
  disableNonInteractive?: boolean
  hooks?: HooksSettings
  skillRoot?: string          // 技能资源目录
  context?: 'inline' | 'fork' // 执行上下文
  agent?: string              // fork 时使用的代理类型
  effort?: EffortValue
  paths?: string[]            // 文件路径匹配模式
  getPromptForCommand(
    args: string,
    context: ToolUseContext,
  ): Promise<ContentBlockParam[]>
}
```

### 1.4 LocalCommand 类型

```typescript
type LocalCommand = {
  type: 'local'
  supportsNonInteractive: boolean
  load: () => Promise<LocalCommandModule>
}

export type LocalCommandModule = {
  call: LocalCommandCall
}

export type LocalCommandCall = (
  args: string,
  context: LocalJSXCommandContext,
) => Promise<LocalCommandResult>

export type LocalCommandResult =
  | { type: 'text'; value: string }
  | { type: 'compact'; compactionResult: CompactionResult; displayText?: string }
  | { type: 'skip' }
```

### 1.5 LocalJSXCommand 类型

```typescript
type LocalJSXCommand = {
  type: 'local-jsx'
  load: () => Promise<LocalJSXCommandModule>
}

export type LocalJSXCommandModule = {
  call: LocalJSXCommandCall
}

export type LocalJSXCommandCall = (
  onDone: LocalJSXCommandOnDone,
  context: ToolUseContext & LocalJSXCommandContext,
  args: string,
) => Promise<React.ReactNode>
```

### 1.6 CommandAvailability 类型

```typescript
/**
 * 声明命令在哪些认证/提供商环境下可用
 * 
 * availability 与 isEnabled 的区别：
 *   - availability = 谁可以使用（静态，认证要求）
 *   - isEnabled()  = 是否开启（动态，GrowthBook/平台/环境变量）
 */
export type CommandAvailability =
  | 'claude-ai'   // claude.ai OAuth 订阅者 (Pro/Max/Team/Enterprise)
  | 'console'     // Console API 密钥用户 (直接 api.anthropic.com)
```

## 二、命令注册与发现

**文件位置**: `src/commands.ts` (717 行)

### 2.1 COMMANDS 静态注册表

```typescript
// 使用 memoize 延迟初始化，避免模块加载时读取配置
const COMMANDS = memoize((): Command[] => [
  addDir,
  advisor,
  agents,
  branch,
  btw,
  chrome,
  clear,
  color,
  compact,
  config,
  copy,
  desktop,
  context,
  contextNonInteractive,
  cost,
  diff,
  doctor,
  effort,
  exit,
  fast,
  files,
  heapDump,
  help,
  ide,
  init,
  keybindings,
  installGitHubApp,
  installSlackApp,
  mcp,
  memory,
  mobile,
  model,
  outputStyle,
  remoteEnv,
  plugin,
  pr_comments,
  releaseNotes,
  reloadPlugins,
  rename,
  resume,
  session,
  skills,
  stats,
  status,
  statusline,
  stickers,
  tag,
  theme,
  feedback,
  review,
  ultrareview,
  rewind,
  securityReview,
  terminalSetup,
  upgrade,
  extraUsage,
  extraUsageNonInteractive,
  rateLimitOptions,
  usage,
  usageReport,
  vim,
  // 条件加载的命令
  ...(webCmd ? [webCmd] : []),
  ...(forkCmd ? [forkCmd] : []),
  ...(buddy ? [buddy] : []),
  ...(proactive ? [proactive] : []),
  ...(briefCommand ? [briefCommand] : []),
  ...(assistantCommand ? [assistantCommand] : []),
  ...(bridge ? [bridge] : []),
  ...(remoteControlServerCommand ? [remoteControlServerCommand] : []),
  ...(voiceCommand ? [voiceCommand] : []),
  thinkback,
  thinkbackPlay,
  permissions,
  plan,
  privacySettings,
  hooks,
  exportCommand,
  sandboxToggle,
  ...(!isUsing3PServices() ? [logout, login()] : []),
  passes,
  ...(peersCmd ? [peersCmd] : []),
  tasks,
  ...(workflowsCmd ? [workflowsCmd] : []),
  ...(torch ? [torch] : []),
  ...(process.env.USER_TYPE === 'ant' && !process.env.IS_DEMO
    ? INTERNAL_ONLY_COMMANDS
    : []),
])
```

### 2.2 命令来源分类

```
命令来源层次结构
┌─────────────────────────────────────────────────────────────┐
│ 1. bundledSkills        - 内置技能（最高优先级）             │
│    通过 registerBundledSkill() 注册                         │
└─────────────────────────┬───────────────────────────────────┘
                          ▼
┌─────────────────────────────────────────────────────────────┐
│ 2. builtinPluginSkills  - 内置插件技能                       │
│    用户可通过 /plugin UI 启用/禁用                          │
└─────────────────────────┬───────────────────────────────────┘
                          ▼
┌─────────────────────────────────────────────────────────────┐
│ 3. skillDirCommands     - 磁盘技能目录                       │
│    ~/.claude/skills/, .claude/skills/, 托管路径             │
└─────────────────────────┬───────────────────────────────────┘
                          ▼
┌─────────────────────────────────────────────────────────────┐
│ 4. workflowCommands     - 工作流命令                         │
│    .claude/workflows/ 目录                                  │
└─────────────────────────┬───────────────────────────────────┘
                          ▼
┌─────────────────────────────────────────────────────────────┐
│ 5. pluginCommands       - 插件命令                           │
│    已安装插件的 commands/ 目录                              │
└─────────────────────────┬───────────────────────────────────┘
                          ▼
┌─────────────────────────────────────────────────────────────┐
│ 6. pluginSkills         - 插件技能                           │
│    已安装插件的 skills/ 目录                                │
└─────────────────────────┬───────────────────────────────────┘
                          ▼
┌─────────────────────────────────────────────────────────────┐
│ 7. COMMANDS()           - 内置命令（最低优先级）             │
│    硬编码的斜杠命令                                         │
└─────────────────────────────────────────────────────────────┘
```

### 2.3 loadAllCommands()

```typescript
/**
 * 加载所有命令来源。按 cwd memoize 因为加载成本高（磁盘 I/O、动态导入）。
 */
const loadAllCommands = memoize(async (cwd: string): Promise<Command[]> => {
  const [
    { skillDirCommands, pluginSkills, bundledSkills, builtinPluginSkills },
    pluginCommands,
    workflowCommands,
  ] = await Promise.all([
    getSkills(cwd),
    getPluginCommands(),
    getWorkflowCommands ? getWorkflowCommands(cwd) : Promise.resolve([]),
  ])

  return [
    ...bundledSkills,
    ...builtinPluginSkills,
    ...skillDirCommands,
    ...workflowCommands,
    ...pluginCommands,
    ...pluginSkills,
    ...COMMANDS(),
  ]
})
```

### 2.4 getCommands()

```typescript
/**
 * 返回当前用户可用的命令。
 * 昂贵的加载被 memoize，但 availability 和 isEnabled 检查每次调用都重新执行，
 * 以便认证变更（如 /login）立即生效。
 */
export async function getCommands(cwd: string): Promise<Command[]> {
  const allCommands = await loadAllCommands(cwd)

  // 获取动态发现的技能
  const dynamicSkills = getDynamicSkills()

  // 构建基础命令
  const baseCommands = allCommands.filter(
    _ => meetsAvailabilityRequirement(_) && isCommandEnabled(_),
  )

  if (dynamicSkills.length === 0) {
    return baseCommands
  }

  // 去重动态技能
  const baseCommandNames = new Set(baseCommands.map(c => c.name))
  const uniqueDynamicSkills = dynamicSkills.filter(
    s =>
      !baseCommandNames.has(s.name) &&
      meetsAvailabilityRequirement(s) &&
      isCommandEnabled(s),
  )

  // 在插件技能后、内置命令前插入动态技能
  const builtInNames = new Set(COMMANDS().map(c => c.name))
  const insertIndex = baseCommands.findIndex(c => builtInNames.has(c.name))

  if (insertIndex === -1) {
    return [...baseCommands, ...uniqueDynamicSkills]
  }

  return [
    ...baseCommands.slice(0, insertIndex),
    ...uniqueDynamicSkills,
    ...baseCommands.slice(insertIndex),
  ]
}
```

### 2.5 meetsAvailabilityRequirement()

```typescript
/**
 * 按 availability 过滤命令。
 * 无 availability 的命令视为通用命令。
 * 在 isEnabled() 之前运行，确保提供商限制的命令被隐藏。
 */
export function meetsAvailabilityRequirement(cmd: Command): boolean {
  if (!cmd.availability) return true
  for (const a of cmd.availability) {
    switch (a) {
      case 'claude-ai':
        if (isClaudeAISubscriber()) return true
        break
      case 'console':
        if (
          !isClaudeAISubscriber() &&
          !isUsing3PServices() &&
          isFirstPartyAnthropicBaseUrl()
        )
          return true
        break
      default: {
        const _exhaustive: never = a
        void _exhaustive
        break
      }
    }
  }
  return false
}
```

## 三、技能过滤函数

### 3.1 getSkillToolCommands()

```typescript
/**
 * SkillTool 显示所有模型可调用的 prompt 类型命令
 * 包括 skills（/skills/）、commands（/commands/）
 */
export const getSkillToolCommands = memoize(
  async (cwd: string): Promise<Command[]> => {
    const allCommands = await getCommands(cwd)
    return allCommands.filter(
      cmd =>
        cmd.type === 'prompt' &&
        !cmd.disableModelInvocation &&
        cmd.source !== 'builtin' &&
        // 始终包含 skills/ 目录的技能、bundled skills 和 legacy commands
        // 插件/MCP 命令仍需显式描述才能出现在列表中
        (cmd.loadedFrom === 'bundled' ||
          cmd.loadedFrom === 'skills' ||
          cmd.loadedFrom === 'commands_DEPRECATED' ||
          cmd.hasUserSpecifiedDescription ||
          cmd.whenToUse),
    )
  },
)
```

### 3.2 getSlashCommandToolSkills()

```typescript
/**
 * 过滤命令以仅包含技能。
 * 技能是提供模型专用能力的命令，通过 loadedFrom 或 disableModelInvocation 识别。
 */
export const getSlashCommandToolSkills = memoize(
  async (cwd: string): Promise<Command[]> => {
    try {
      const allCommands = await getCommands(cwd)
      return allCommands.filter(
        cmd =>
          cmd.type === 'prompt' &&
          cmd.source !== 'builtin' &&
          (cmd.hasUserSpecifiedDescription || cmd.whenToUse) &&
          (cmd.loadedFrom === 'skills' ||
            cmd.loadedFrom === 'plugin' ||
            cmd.loadedFrom === 'bundled' ||
            cmd.disableModelInvocation),
      )
    } catch (error) {
      logError(toError(error))
      logForDebugging('Returning empty skills array due to load failure')
      return []
    }
  },
)
```

### 3.3 getMcpSkillCommands()

```typescript
/**
 * 从 AppState.mcp.commands 过滤 MCP 提供的技能
 * (prompt 类型、模型可调用、从 MCP 加载)
 */
export function getMcpSkillCommands(
  mcpCommands: readonly Command[],
): readonly Command[] {
  if (feature('MCP_SKILLS')) {
    return mcpCommands.filter(
      cmd =>
        cmd.type === 'prompt' &&
        cmd.loadedFrom === 'mcp' &&
        !cmd.disableModelInvocation,
    )
  }
  return []
}
```

## 四、缓存管理

### 4.1 缓存清除函数

```typescript
/**
 * 仅清除命令的 memoize 缓存，不清除技能缓存。
 * 当动态技能添加时使用。
 */
export function clearCommandMemoizationCaches(): void {
  loadAllCommands.cache?.clear?.()
  getSkillToolCommands.cache?.clear?.()
  getSlashCommandToolSkills.cache?.clear?.()
  clearSkillIndexCache?.()
}

/**
 * 完全清除所有命令缓存。
 */
export function clearCommandsCache(): void {
  clearCommandMemoizationCaches()
  clearPluginCommandCache()
  clearPluginSkillsCache()
  clearSkillCaches()
}
```

## 五、远程模式命令过滤

### 5.1 REMOTE_SAFE_COMMANDS

```typescript
/**
 * 在远程模式 (--remote) 下安全的命令。
 * 这些仅影响本地 TUI 状态，不依赖本地文件系统、git、shell、IDE、MCP 等。
 */
export const REMOTE_SAFE_COMMANDS: Set<Command> = new Set([
  session,    // 显示远程会话 QR 码/URL
  exit,       // 退出 TUI
  clear,      // 清屏
  help,       // 显示帮助
  theme,      // 更改终端主题
  color,      // 更改代理颜色
  vim,        // 切换 vim 模式
  cost,       // 显示会话成本
  usage,      // 显示使用信息
  copy,       // 复制最后消息
  btw,        // 快速笔记
  feedback,   // 发送反馈
  plan,       // 计划模式切换
  keybindings, // 快捷键管理
  statusline, // 状态栏切换
  stickers,   // 贴纸
  mobile,     // 移动端 QR 码
])

export function filterCommandsForRemoteMode(commands: Command[]): Command[] {
  return commands.filter(cmd => REMOTE_SAFE_COMMANDS.has(cmd))
}
```

### 5.2 BRIDGE_SAFE_COMMANDS

```typescript
/**
 * 类型为 'local' 且可通过 Remote Control 桥接安全执行的内置命令。
 * 这些产生文本输出流回移动/Web 客户端，无终端专用副作用。
 */
export const BRIDGE_SAFE_COMMANDS: Set<Command> = new Set(
  [
    compact,       // 压缩上下文
    clear,         // 清除转录
    cost,          // 显示会话成本
    summary,       // 总结对话
    releaseNotes,  // 显示更新日志
    files,         // 列出跟踪文件
  ].filter((c): c is Command => c !== null),
)

export function isBridgeSafeCommand(cmd: Command): boolean {
  if (cmd.type === 'local-jsx') return false
  if (cmd.type === 'prompt') return true
  return BRIDGE_SAFE_COMMANDS.has(cmd)
}
```

## 六、命令目录结构

`commands/` 目录包含 110+ 个文件：

```
commands/
├── skills/              # /skills - 技能浏览器
│   ├── index.ts
│   └── skills.tsx
├── plugin/              # /plugin - 插件管理
│   ├── index.tsx
│   ├── plugin.tsx
│   ├── parseArgs.ts
│   └── usePagination.ts
├── mcp/                 # MCP 相关命令
│   ├── index.ts
│   ├── addCommand.ts
│   └── xaaIdpCommand.ts
├── config/              # /config - 配置管理
├── compact/             # /compact - 上下文压缩
├── doctor/              # /doctor - 诊断工具
├── login/               # /login - 登录
├── logout/              # /logout - 登出
├── model/               # /model - 模型选择
├── permissions/         # /permissions - 权限管理
├── resume/              # /resume - 恢复会话
├── session/             # /session - 会话管理
├── tasks/               # /tasks - 任务管理
├── agents/              # /agents - 代理管理
├── branch/              # /branch - 分支操作
├── commit.ts             # /commit - 提交代码
├── review.ts             # /review - 代码审查
├── init.ts               # /init - 项目初始化
├── help/                # /help - 帮助信息
├── clear/               # /clear - 清屏
├── cost/                # /cost - 成本显示
├── ...                  # 更多命令
└── createMovedToPluginCommand.ts  # 迁移桥接工厂
```

## 七、命令迁移机制

### createMovedToPluginCommand()

```typescript
/**
 * 当内置命令迁移到插件时，创建存根命令拦截调用并重定向到插件安装流程。
 */
export function createMovedToPluginCommand({
  name,
  description,
  progressMessage,
  pluginName,
  pluginCommand,
  getPromptWhileMarketplaceIsPrivate,
}: {
  name: string
  description: string
  progressMessage: string
  pluginName: string
  pluginCommand: string
  getPromptWhileMarketplaceIsPrivate: (
    args: string,
    context: ToolUseContext,
  ) => Promise<ContentBlockParam[]>
}): Command {
  return {
    type: 'prompt',
    name,
    description,
    progressMessage,
    source: 'builtin',
    contentLength: 0,
    async getPromptForCommand(args, context) {
      if (process.env.USER_TYPE === 'ant') {
        return [{
          type: 'text',
          text: `This command has been moved to a plugin. Tell the user:

1. To install the plugin, run:
   claude plugin install ${pluginName}@claude-code-marketplace

2. After installation, use /${pluginName}:${pluginCommand} to run this command

3. For more information, see: https://github.com/anthropics/claude-code-marketplace/blob/main/${pluginName}/README.md

Do not attempt to run the command. Simply inform the user about the plugin installation.`,
        }]
      }
      return getPromptWhileMarketplaceIsPrivate(args, context)
    },
  }
}
```

## 八、内置命令名称获取

```typescript
export const builtInCommandNames = memoize(
  (): Set<string> =>
    new Set(COMMANDS().flatMap(_ => [_.name, ...(_.aliases ?? [])])),
)

export function findCommand(
  commandName: string,
  commands: Command[],
): Command | undefined {
  return commands.find(
    _ =>
      _.name === commandName ||
      getCommandName(_) === commandName ||
      _.aliases?.includes(commandName),
  )
}
```