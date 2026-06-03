# Types 完整类型系统技术文档

> 基于逐行代码分析的完整技术文档  
> **探索完成时间**: 2026 年 4 月 1 日  
> **核心文件**: permissions.ts (442 行), plugin.ts (363 行), command.ts (216 行), hooks.ts (290 行)

---

## 1. permissions.ts - 权限类型系统 (442 行)

### 1.1 权限模式 (Permission Modes)

#### 外部权限模式

```typescript
export const EXTERNAL_PERMISSION_MODES = [
  'acceptEdits',
  'bypassPermissions', 
  'default',
  'dontAsk',
  'plan',
] as const

export type ExternalPermissionMode = (typeof EXTERNAL_PERMISSION_MODES)[number]
```

**目的**: 定义用户可配置的外部权限模式，这些模式在 settings.json 和 CLI 标志中可见。

#### 内部权限模式

```typescript
export type InternalPermissionMode = ExternalPermissionMode | 'auto' | 'bubble'
export type PermissionMode = InternalPermissionMode
```

**目的**: 包含系统内部使用的额外模式，如 'auto'（自动模式）和 'bubble'（气泡模式）。

### 1.2 权限行为 (Permission Behaviors)

```typescript
export type PermissionBehavior = 'allow' | 'deny' | 'ask'
```

**目的**: 定义权限决策的三种基本行为：允许、拒绝、询问。

### 1.3 权限规则 (Permission Rules)

#### 规则来源

```typescript
export type PermissionRuleSource =
  | 'userSettings'
  | 'projectSettings'
  | 'localSettings'
  | 'flagSettings'
  | 'policySettings'
  | 'cliArg'
  | 'command'
  | 'session'
```

#### 规则值

```typescript
export type PermissionRuleValue = {
  toolName: string
  ruleContent?: string
}
```

#### 完整规则

```typescript
export type PermissionRule = {
  source: PermissionRuleSource
  ruleBehavior: PermissionBehavior
  ruleValue: PermissionRuleValue
}
```

### 1.4 权限更新 (Permission Updates)

#### 更新操作判别联合

```typescript
export type PermissionUpdate =
  | {
      type: 'addRules'
      destination: PermissionUpdateDestination
      rules: PermissionRuleValue[]
      behavior: PermissionBehavior
    }
  | {
      type: 'replaceRules'
      destination: PermissionUpdateDestination
      rules: PermissionRuleValue[]
      behavior: PermissionBehavior
    }
  | {
      type: 'removeRules'
      destination: PermissionUpdateDestination
      rules: PermissionRuleValue[]
      behavior: PermissionBehavior
    }
  | {
      type: 'setMode'
      destination: PermissionUpdateDestination
      mode: ExternalPermissionMode
    }
  | {
      type: 'addDirectories'
      destination: PermissionUpdateDestination
      directories: string[]
    }
  | {
      type: 'removeDirectories'
      destination: PermissionUpdateDestination
      directories: string[]
    }
```

**类型设计模式**: 
- 使用 `type` 字段作为判别式 (discriminator)
- TypeScript 可以基于 `type` 自动推断其他字段的类型
- 类型安全的更新操作，防止无效的组合

### 1.5 权限决策系统

#### 允许决策 (泛型类型)

```typescript
export type PermissionAllowDecision<
  Input extends { [key: string]: unknown } = { [key: string]: unknown },
> = {
  behavior: 'allow'
  updatedInput?: Input
  userModified?: boolean
  decisionReason?: PermissionDecisionReason
  toolUseID?: string
  acceptFeedback?: string
  contentBlocks?: ContentBlockParam[]
}
```

#### 询问决策 (泛型类型)

```typescript
export type PermissionAskDecision<
  Input extends { [key: string]: unknown } = { [key: string]: unknown },
> = {
  behavior: 'ask'
  message: string
  updatedInput?: Input
  decisionReason?: PermissionDecisionReason
  suggestions?: PermissionUpdate[]
  blockedPath?: string
  metadata?: PermissionMetadata
  isBashSecurityCheckForMisparsing?: boolean
  pendingClassifierCheck?: PendingClassifierCheck
  contentBlocks?: ContentBlockParam[]
}
```

#### 拒绝决策

```typescript
export type PermissionDenyDecision = {
  behavior: 'deny'
  message: string
  decisionReason: PermissionDecisionReason
  toolUseID?: string
}
```

#### 决策联合类型

```typescript
export type PermissionDecision<
  Input extends { [key: string]: unknown } = { [key: string]: unknown },
> =
  | PermissionAllowDecision<Input>
  | PermissionAskDecision<Input>
  | PermissionDenyDecision
```

### 1.6 权限决策原因 (判别联合)

```typescript
export type PermissionDecisionReason =
  | {
      type: 'rule'
      rule: PermissionRule
    }
  | {
      type: 'mode'
      mode: PermissionMode
    }
  | {
      type: 'subcommandResults'
      reasons: Map<string, PermissionResult>
    }
  | {
      type: 'permissionPromptTool'
      permissionPromptToolName: string
      toolResult: unknown
    }
  | {
      type: 'hook'
      hookName: string
      hookSource?: string
      reason?: string
    }
  | {
      type: 'asyncAgent'
      reason: string
    }
  | {
      type: 'sandboxOverride'
      reason: 'excludedCommand' | 'dangerouslyDisableSandbox'
    }
  | {
      type: 'classifier'
      classifier: string
      reason: string
    }
  | {
      type: 'workingDir'
      reason: string
    }
  | {
      type: 'safetyCheck'
      reason: string
      classifierApprovable: boolean
    }
  | {
      type: 'other'
      reason: string
    }
```

**设计分析**:
- 11 种不同的决策原因类型
- 每种类型有特定的上下文数据
- 支持规则、模式、钩子、分类器等多种决策来源

---

## 2. plugin.ts - 插件类型系统 (363 行)

### 2.1 内置插件定义

```typescript
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

### 2.2 加载的插件

```typescript
export type LoadedPlugin = {
  name: string
  manifest: PluginManifest
  path: string
  source: string
  repository: string
  enabled?: boolean
  isBuiltin?: boolean
  sha?: string
  commandsPath?: string
  commandsPaths?: string[]
  commandsMetadata?: Record<string, CommandMetadata>
  agentsPath?: string
  agentsPaths?: string[]
  skillsPath?: string
  skillsPaths?: string[]
  outputStylesPath?: string
  outputStylesPaths?: string[]
  hooksConfig?: HooksSettings
  mcpServers?: Record<string, McpServerConfig>
  lspServers?: Record<string, LspServerConfig>
  settings?: Record<string, unknown>
}
```

### 2.3 插件错误系统 (判别联合)

```typescript
export type PluginError =
  | {
      type: 'path-not-found'
      source: string
      plugin?: string
      path: string
      component: PluginComponent
    }
  | {
      type: 'git-auth-failed'
      source: string
      plugin?: string
      gitUrl: string
      authType: 'ssh' | 'https'
    }
  | {
      type: 'git-timeout'
      source: string
      plugin?: string
      gitUrl: string
      operation: 'clone' | 'pull'
    }
  | {
      type: 'network-error'
      source: string
      plugin?: string
      gitUrl?: string
      error: string
    }
  | {
      type: 'manifest-parse-error'
      source: string
      plugin?: string
      parseError: string
    }
  | {
      type: 'manifest-validation-error'
      source: string
      plugin?: string
      validationError: string
    }
  // ... 共 24 种错误类型
  | {
      type: 'generic-error'
      source: string
      plugin?: string
      error: string
    }
```

**错误类型完整列表**:
1. `path-not-found`
2. `git-auth-failed`
3. `git-timeout`
4. `network-error`
5. `manifest-parse-error`
6. `manifest-validation-error`
7. `plugin-not-found`
8. `marketplace-not-found`
9. `marketplace-load-failed`
10. `mcp-config-invalid`
11. `mcp-server-suppressed-duplicate`
12. `lsp-config-invalid`
13. `hook-load-failed`
14. `component-load-failed`
15. `mcpb-download-failed`
16. `mcpb-extract-failed`
17. `mcpb-invalid-manifest`
18. `lsp-server-start-failed`
19. `lsp-server-crashed`
20. `lsp-request-timeout`
21. `lsp-request-failed`
22. `marketplace-blocked-by-policy`
23. `dependency-unsatisfied`
24. `plugin-cache-miss`
25. `generic-error`

---

## 3. command.ts - 命令类型系统 (216 行)

### 3.1 命令基础类型

```typescript
export type CommandBase = {
  availability?: CommandAvailability[]
  description: string
  hasUserSpecifiedDescription?: boolean
  isEnabled?: () => boolean
  isHidden?: boolean
  name: string
  aliases?: string[]
  isMcp?: boolean
  argumentHint?: string
  whenToUse?: string
  version?: string
  disableModelInvocation?: boolean
  userInvocable?: boolean
  loadedFrom?: 'commands_DEPRECATED' | 'skills' | 'plugin' | 'managed' | 'bundled' | 'mcp'
  kind?: 'workflow'
  immediate?: boolean
  isSensitive?: boolean
  userFacingName?: () => string
}
```

### 3.2 命令可用性

```typescript
export type CommandAvailability =
  | 'claude-ai'      // claude.ai OAuth 订阅用户
  | 'console'        // Console API 密钥用户
```

### 3.3 Prompt 命令

```typescript
export type PromptCommand = {
  type: 'prompt'
  progressMessage: string
  contentLength: number
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
  skillRoot?: string
  context?: 'inline' | 'fork'
  agent?: string
  effort?: EffortValue
  paths?: string[]
  getPromptForCommand(
    args: string,
    context: ToolUseContext,
  ): Promise<ContentBlockParam[]>
}
```

### 3.4 本地命令模块模式

```typescript
export type LocalCommandCall = (
  args: string,
  context: LocalJSXCommandContext,
) => Promise<LocalCommandResult>

export type LocalCommandModule = {
  call: LocalCommandCall
}

type LocalCommand = {
  type: 'local'
  supportsNonInteractive: boolean
  load: () => Promise<LocalCommandModule>
}
```

**设计亮点**:
- 延迟加载模式 (lazy loading)
- 模块形状抽象
- 支持 JSX 命令

### 3.5 命令联合类型

```typescript
export type Command = CommandBase &
  (PromptCommand | LocalCommand | LocalJSXCommand)
```

---

## 4. hooks.ts - Hook 类型系统 (290 行)

### 4.1 Hook 事件和输入

从 `agentSdkTypes.js` 导入：
- `HookEvent`
- `HOOK_EVENTS`
- `HookInput`
- `PermissionUpdate`

### 4.2 Prompt 请求协议

```typescript
export const promptRequestSchema = lazySchema(() =>
  z.object({
    prompt: z.string(),
    message: z.string(),
    options: z.array(
      z.object({
        key: z.string(),
        label: z.string(),
        description: z.string().optional(),
      }),
    ),
  }),
)

export type PromptRequest = z.infer<ReturnType<typeof promptRequestSchema>>

export type PromptResponse = {
  prompt_response: string
  selected: string
}
```

### 4.3 Sync Hook 响应 Schema

```typescript
export const syncHookResponseSchema = lazySchema(() =>
  z.object({
    continue: z.boolean().optional(),
    suppressOutput: z.boolean().optional(),
    stopReason: z.string().optional(),
    decision: z.enum(['approve', 'block']).optional(),
    reason: z.string().optional(),
    systemMessage: z.string().optional(),
    hookSpecificOutput: z.union([
      z.object({
        hookEventName: z.literal('PreToolUse'),
        permissionDecision: permissionBehaviorSchema().optional(),
        permissionDecisionReason: z.string().optional(),
        updatedInput: z.record(z.string(), z.unknown()).optional(),
        additionalContext: z.string().optional(),
      }),
      // ... 13 种不同的 hook 事件类型
    ]).optional(),
  }),
)
```

**支持的 Hook 事件类型**:
1. `PreToolUse`
2. `UserPromptSubmit`
3. `SessionStart`
4. `Setup`
5. `SubagentStart`
6. `PostToolUse`
7. `PostToolUseFailure`
8. `PermissionDenied`
9. `Notification`
10. `PermissionRequest`
11. `Elicitation`
12. `ElicitationResult`
13. `CwdChanged`
14. `FileChanged`
15. `WorktreeCreate`

### 4.4 Hook 回调类型

```typescript
export type HookCallback = {
  type: 'callback'
  callback: (
    input: HookInput,
    toolUseID: string | null,
    abort: AbortSignal | undefined,
    hookIndex?: number,
    context?: HookCallbackContext,
  ) => Promise<HookJSONOutput>
  timeout?: number
  internal?: boolean
}
```

### 4.5 Hook 结果类型

```typescript
export type HookResult = {
  message?: Message
  systemMessage?: Message
  blockingError?: HookBlockingError
  outcome: 'success' | 'blocking' | 'non_blocking_error' | 'cancelled'
  preventContinuation?: boolean
  stopReason?: string
  permissionBehavior?: 'ask' | 'deny' | 'allow' | 'passthrough'
  hookPermissionDecisionReason?: string
  additionalContext?: string
  initialUserMessage?: string
  updatedInput?: Record<string, unknown>
  updatedMCPToolOutput?: unknown
  permissionRequestResult?: PermissionRequestResult
  retry?: boolean
}
```

---

## 5. ids.ts - ID 类型系统 (45 行)

### 5.1 品牌类型 (Branded Types)

```typescript
/**
 * A session ID uniquely identifies a Claude Code session.
 * Returned by getSessionId().
 */
export type SessionId = string & { readonly __brand: 'SessionId' }

/**
 * An agent ID uniquely identifies a subagent within a session.
 * Returned by createAgentId().
 * When present, indicates the context is a subagent (not the main session).
 */
export type AgentId = string & { readonly __brand: 'AgentId' }
```

**设计模式**:
- 使用品牌类型防止类型混淆
- `__brand` 属性在运行时不存在 (zero-cost abstraction)
- TypeScript 在编译时进行类型检查

### 5.2 类型转换函数

```typescript
export function asSessionId(id: string): SessionId {
  return id as SessionId
}

export function asAgentId(id: string): AgentId {
  return id as AgentId
}
```

### 5.3 Agent ID 验证

```typescript
const AGENT_ID_PATTERN = /^a(?:.+-)?[0-9a-f]{16}$/

export function toAgentId(s: string): AgentId | null {
  return AGENT_ID_PATTERN.test(s) ? (s as AgentId) : null
}
```

**格式说明**:
- 以 `a` 开头
- 可选的 `<label>-` 前缀
- 16 个十六进制字符

---

## 6. logs.ts - 日志类型系统 (331 行)

### 6.1 序列化消息

```typescript
export type SerializedMessage = Message & {
  cwd: string
  userType: string
  entrypoint?: string
  sessionId: string
  timestamp: string
  version: string
  gitBranch?: string
  slug?: string
}
```

### 6.2 日志选项

```typescript
export type LogOption = {
  date: string
  messages: SerializedMessage[]
  fullPath?: string
  value: number
  created: Date
  modified: Date
  firstPrompt: string
  messageCount: number
  fileSize?: number
  isSidechain: boolean
  isLite?: boolean
  sessionId?: string
  teamName?: string
  agentName?: string
  agentColor?: string
  agentSetting?: string
  isTeammate?: boolean
  leafUuid?: string
  summary?: string
  customTitle?: string
  tag?: string
  fileHistorySnapshots?: FileHistorySnapshot[]
  attributionSnapshots?: AttributionSnapshotMessage[]
  contextCollapseCommits?: ContextCollapseCommitEntry[]
  contextCollapseSnapshot?: ContextCollapseSnapshotEntry
  gitBranch?: string
  projectPath?: string
  prNumber?: number
  prUrl?: string
  prRepository?: string
  mode?: 'coordinator' | 'normal'
  worktreeSession?: PersistedWorktreeSession | null
  contentReplacements?: ContentReplacementRecord[]
}
```

### 6.3 元数据消息类型

#### 摘要消息

```typescript
export type SummaryMessage = {
  type: 'summary'
  leafUuid: UUID
  summary: string
}
```

#### 自定义标题消息

```typescript
export type CustomTitleMessage = {
  type: 'custom-title'
  sessionId: UUID
  customTitle: string
}
```

#### AI 标题消息

```typescript
export type AiTitleMessage = {
  type: 'ai-title'
  sessionId: UUID
  aiTitle: string
}
```

#### 任务摘要消息

```typescript
export type TaskSummaryMessage = {
  type: 'task-summary'
  sessionId: UUID
  summary: string
  timestamp: string
}
```

### 6.4 工作树会话

```typescript
export type PersistedWorktreeSession = {
  originalCwd: string
  worktreePath: string
  worktreeName: string
  worktreeBranch?: string
  originalBranch?: string
  originalHeadCommit?: string
  sessionId: string
  tmuxSessionName?: string
  hookBased?: boolean
}
```

### 6.5 上下文折叠

#### 折叠提交条目

```typescript
export type ContextCollapseCommitEntry = {
  type: 'marble-origami-commit'
  sessionId: UUID
  collapseId: string
  summaryUuid: string
  summaryContent: string
  summary: string
  firstArchivedUuid: string
  lastArchivedUuid: string
}
```

#### 折叠快照条目

```typescript
export type ContextCollapseSnapshotEntry = {
  type: 'marble-origami-snapshot'
  sessionId: UUID
  staged: Array<{
    startUuid: string
    endUuid: string
    summary: string
    risk: number
    stagedAt: number
  }>
  armed: boolean
  lastSpawnTokens: number
}
```

### 6.6 条目联合类型

```typescript
export type Entry =
  | TranscriptMessage
  | SummaryMessage
  | CustomTitleMessage
  | AiTitleMessage
  | LastPromptMessage
  | TaskSummaryMessage
  | TagMessage
  | AgentNameMessage
  | AgentColorMessage
  | AgentSettingMessage
  | PRLinkMessage
  | FileHistorySnapshotMessage
  | AttributionSnapshotMessage
  | QueueOperationMessage
  | SpeculationAcceptMessage
  | ModeEntry
  | WorktreeStateEntry
  | ContentReplacementEntry
  | ContextCollapseCommitEntry
  | ContextCollapseSnapshotEntry
```

---

## 7. textInputTypes.ts - 文本输入类型系统 (388 行)

### 7.1 基础输入组件属性

```typescript
export type BaseTextInputProps = {
  readonly onHistoryUp?: () => void
  readonly onHistoryDown?: () => void
  readonly placeholder?: string
  readonly multiline?: boolean
  readonly focus?: boolean
  readonly mask?: string
  readonly showCursor?: boolean
  readonly highlightPastedText?: boolean
  readonly value: string
  readonly onChange: (value: string) => void
  readonly onSubmit?: (value: string) => void
  readonly onExit?: () => void
  readonly onExitMessage?: (show: boolean, key?: string) => void
  readonly onHistoryReset?: () => void
  readonly onClearInput?: () => void
  readonly columns: number
  readonly maxVisibleLines?: number
  readonly onImagePaste?: (
    base64Image: string,
    mediaType?: string,
    filename?: string,
    dimensions?: ImageDimensions,
    sourcePath?: string,
  ) => void
  readonly onPaste?: (text: string) => void
  readonly onIsPastingChange?: (isPasting: boolean) => void
  readonly disableCursorMovementForUpDownKeys?: boolean
  readonly disableEscapeDoublePress?: boolean
  readonly cursorOffset: number
  onChangeCursorOffset: (offset: number) => void
  readonly argumentHint?: string
  readonly onUndo?: () => void
  readonly dimColor?: boolean
  readonly highlights?: TextHighlight[]
  readonly placeholderElement?: React.ReactNode
  readonly inlineGhostText?: InlineGhostText
  readonly inputFilter?: (input: string, key: Key) => string
}
```

### 7.2 队列优先级

```typescript
export type QueuePriority = 'now' | 'next' | 'later'
```

**优先级语义**:
- `now`: 立即中断并发送
- `next`: 当前工具调用完成后发送
- `later`: 当前回合结束后处理

### 7.3 队列命令

```typescript
export type QueuedCommand = {
  value: string | Array<ContentBlockParam>
  mode: PromptInputMode
  priority?: QueuePriority
  uuid?: UUID
  orphanedPermission?: OrphanedPermission
  pastedContents?: Record<number, PastedContent>
  preExpansionValue?: string
  skipSlashCommands?: boolean
  bridgeOrigin?: boolean
  isMeta?: boolean
  origin?: MessageOrigin
  workload?: string
  agentId?: AgentId
}
```

---

## 8. 类型系统关键设计模式

### 8.1 判别联合 (Discriminated Unions)

**模式**: 使用 `type` 字段作为判别式

```typescript
export type PermissionUpdate =
  | { type: 'addRules'; /* ... */ }
  | { type: 'replaceRules'; /* ... */ }
  | { type: 'removeRules'; /* ... */ }
  | { type: 'setMode'; /* ... */ }
```

**优势**:
- TypeScript 自动类型收窄
- 编译器检查 exhaustiveness
- 运行时类型安全

### 8.2 品牌类型 (Branded Types)

**模式**: 使用交叉类型添加品牌标记

```typescript
export type SessionId = string & { readonly __brand: 'SessionId' }
export type AgentId = string & { readonly __brand: 'AgentId' }
```

**优势**:
- 编译时类型安全
- 零运行时开销
- 防止类型混淆

### 8.3 条件类型和映射类型

**模式**: 使用 `Pick`, `Omit`, `Partial` 等工具类型

```typescript
type DefaultableToolKeys =
  | 'isEnabled'
  | 'isConcurrencySafe'
  // ...

export type ToolDef<...> = Omit<Tool<...>, DefaultableToolKeys> &
  Partial<Pick<Tool<...>, DefaultableToolKeys>>
```

### 8.4 Zod Schema 集成

**模式**: 使用 `lazySchema` 和 `z.infer`

```typescript
export const permissionBehaviorSchema = lazySchema(() =>
  z.enum(['allow', 'deny', 'ask']),
)

export type PermissionBehavior = z.infer<ReturnType<typeof permissionBehaviorSchema>>
```

**优势**:
- 运行时验证
- 类型推断
- 单一真实来源

### 8.5 泛型约束

**模式**: 使用 `extends` 约束泛型

```typescript
export type PermissionAllowDecision<
  Input extends { [key: string]: unknown } = { [key: string]: unknown },
> = {
  behavior: 'allow'
  updatedInput?: Input
  // ...
}
```

---

## 9. 类型关系图

```
┌─────────────────────────────────────────────────────────────┐
│                    Permission System                         │
├─────────────────────────────────────────────────────────────┤
│  PermissionMode                                             │
│    ├─ ExternalPermissionMode                                │
│    │   ├─ 'acceptEdits'                                     │
│    │   ├─ 'bypassPermissions'                               │
│    │   ├─ 'default'                                         │
│    │   ├─ 'dontAsk'                                         │
│    │   └─ 'plan'                                            │
│    └─ Internal (auto, bubble)                               │
│                                                             │
│  PermissionBehavior: 'allow' | 'deny' | 'ask'               │
│                                                             │
│  PermissionRule                                             │
│    ├─ source: PermissionRuleSource                          │
│    ├─ ruleBehavior: PermissionBehavior                      │
│    └─ ruleValue: PermissionRuleValue                        │
│                                                             │
│  PermissionUpdate (Discriminated Union)                     │
│    ├─ type: 'addRules'                                      │
│    ├─ type: 'replaceRules'                                  │
│    ├─ type: 'removeRules'                                   │
│    ├─ type: 'setMode'                                       │
│    ├─ type: 'addDirectories'                                │
│    └─ type: 'removeDirectories'                             │
│                                                             │
│  PermissionDecision                                         │
│    ├─ PermissionAllowDecision                               │
│    ├─ PermissionAskDecision                                 │
│    └─ PermissionDenyDecision                                │
│                                                             │
│  PermissionDecisionReason (11 types)                        │
│    ├─ rule, mode, subcommandResults                         │
│    ├─ permissionPromptTool, hook, asyncAgent                │
│    ├─ sandboxOverride, classifier, workingDir               │
│    ├─ safetyCheck, other                                    │
│    └─ ...                                                   │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│                      Plugin System                           │
├─────────────────────────────────────────────────────────────┤
│  BuiltinPluginDefinition                                    │
│    ├─ name, description, version                            │
│    ├─ skills, hooks, mcpServers                             │
│    └─ isAvailable(), defaultEnabled                         │
│                                                             │
│  LoadedPlugin                                               │
│    ├─ manifest: PluginManifest                              │
│    ├─ paths (commands, agents, skills, outputStyles)        │
│    ├─ configs (hooks, mcp, lsp, settings)                   │
│    └─ metadata (source, repository, sha)                    │
│                                                             │
│  PluginError (25 types)                                     │
│    ├─ path-not-found, git-auth-failed, git-timeout          │
│    ├─ network-error, manifest-*, plugin-not-found           │
│    ├─ marketplace-*, mcp-*, lsp-*                           │
│    ├─ hook-load-failed, component-load-failed               │
│    └─ dependency-unsatisfied, generic-error                 │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│                      Command System                          │
├─────────────────────────────────────────────────────────────┤
│  CommandBase                                                │
│    ├─ availability: CommandAvailability[]                   │
│    ├─ name, description, aliases                            │
│    ├─ isEnabled(), isHidden()                               │
│    └─ metadata (version, kind, immediate, etc.)             │
│                                                             │
│  Command = CommandBase & (                                   │
│    ├─ PromptCommand                                         │
│    ├─ LocalCommand                                          │
│    └─ LocalJSXCommand                                       │
│  )                                                          │
│                                                             │
│  LocalCommandModule                                         │
│    └─ call: (args, context) => Promise<LocalCommandResult>  │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│                       Hook System                            │
├─────────────────────────────────────────────────────────────┤
│  HookCallback                                               │
│    ├─ type: 'callback'                                      │
│    ├─ callback: (HookInput, ...) => Promise<HookJSONOutput> │
│    └─ timeout, internal                                     │
│                                                             │
│  HookJSONOutput                                             │
│    ├─ SyncHookJSONOutput                                    │
│    │   └─ continue, suppressOutput, decision, etc.          │
│    └─ AsyncHookJSONOutput                                   │
│        └─ async: true, asyncTimeout                         │
│                                                             │
│  HookResult                                                 │
│    ├─ outcome: 'success' | 'blocking' | ...                 │
│    ├─ message, systemMessage, blockingError                 │
│    └─ permissionBehavior, additionalContext, etc.           │
└─────────────────────────────────────────────────────────────┘
```

---

## 10. 总结

### 类型系统规模

- **核心类型文件**: 7 个
- **生成类型文件**: 4 个
- **总行数**: ~2000+ 行类型定义
- **判别联合**: 10+ 个大型联合类型
- **泛型类型**: 20+ 个
- **类型守卫**: 15+ 个

### 设计亮点

1. **判别联合的广泛应用**：权限更新、插件错误、决策原因等
2. **品牌类型**：SessionId 和 AgentId 的类型安全
3. **Zod Schema 集成**：运行时验证 + 类型推断
4. **泛型约束**：灵活的决策类型
5. **条件类型**：ToolDef → BuiltTool 的类型级计算
6. **延迟加载**：LocalCommandModule 模式
7. **只读性**：大量使用 `readonly` 和 `DeepImmutable`

### 类型系统完整性

✅ 权限类型系统 (permissions.ts)
✅ 插件类型系统 (plugin.ts)
✅ 命令类型系统 (command.ts)
✅ Hook 类型系统 (hooks.ts)
✅ ID 类型系统 (ids.ts)
✅ 日志类型系统 (logs.ts)
✅ 文本输入类型系统 (textInputTypes.ts)

---

*文档持续更新中...*
