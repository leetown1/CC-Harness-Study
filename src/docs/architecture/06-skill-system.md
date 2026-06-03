# 技能系统深度解析

本文档详细分析 Claude Code 的技能系统实现，包括技能定义格式、加载机制和执行流程。

## 一、技能系统概述

### 1.1 什么是技能 (Skills)?

技能是可被模型调用的 prompt 扩展，用于提供专业化能力。与命令不同：
- **技能**被设计为由模型自动调用（基于 `whenToUse` 描述）
- **命令**主要面向用户手动调用（通过斜杠命令）

### 1.2 技能来源

| 来源 | 目录/机制 | loadedFrom |
|------|-----------|------------|
| Bundled Skills | `skills/bundled/` | `'bundled'` |
| Builtin Plugin Skills | 内置插件定义 | `'bundled'` |
| User Skills | `~/.claude/skills/` | `'skills'` |
| Project Skills | `.claude/skills/` | `'skills'` |
| Managed Skills | 托管配置路径 | `'skills'` |
| Plugin Skills | 插件 `skills/` 目录 | `'plugin'` |
| MCP Skills | MCP 服务器提供 | `'mcp'` |

### 1.3 核心文件

| 文件 | 职责 |
|------|------|
| `skills/bundledSkills.ts` | 内置技能注册与管理 |
| `skills/loadSkillsDir.ts` | 磁盘技能目录加载 |
| `skills/mcpSkillBuilders.ts` | MCP 技能构建器 |
| `skills/bundled/` | 内置技能定义目录 |

## 二、BundledSkillDefinition 类型

**文件位置**: `src/skills/bundledSkills.ts`

```typescript
export type BundledSkillDefinition = {
  name: string
  description: string
  aliases?: string[]
  whenToUse?: string
  argumentHint?: string
  allowedTools?: string[]
  model?: string
  disableModelInvocation?: boolean
  userInvocable?: boolean
  isEnabled?: () => boolean
  hooks?: HooksSettings
  context?: 'inline' | 'fork'
  agent?: string
  
  /**
   * 首次调用时提取到磁盘的附加参考文件。
   * 键为相对路径，值为内容。
   * 技能提示会添加 "Base directory for this skill: <dir>" 前缀
   */
  files?: Record<string, string>
  
  getPromptForCommand: (
    args: string,
    context: ToolUseContext,
  ) => Promise<ContentBlockParam[]>
}
```

## 三、内置技能注册

### 3.1 注册机制

```typescript
// 内部注册表
const bundledSkills: Command[] = []

/**
 * 注册内置技能。在模块初始化或 init 函数中调用。
 */
export function registerBundledSkill(definition: BundledSkillDefinition): void {
  const { files } = definition

  let skillRoot: string | undefined
  let getPromptForCommand = definition.getPromptForCommand

  // 如果有参考文件，设置延迟提取
  if (files && Object.keys(files).length > 0) {
    skillRoot = getBundledSkillExtractDir(definition.name)
    
    let extractionPromise: Promise<string | null> | undefined
    const inner = definition.getPromptForCommand
    getPromptForCommand = async (args, ctx) => {
      extractionPromise ??= extractBundledSkillFiles(definition.name, files)
      const extractedDir = await extractionPromise
      const blocks = await inner(args, ctx)
      if (extractedDir === null) return blocks
      return prependBaseDir(blocks, extractedDir)
    }
  }

  const command: Command = {
    type: 'prompt',
    name: definition.name,
    description: definition.description,
    aliases: definition.aliases,
    hasUserSpecifiedDescription: true,
    allowedTools: definition.allowedTools ?? [],
    argumentHint: definition.argumentHint,
    whenToUse: definition.whenToUse,
    model: definition.model,
    disableModelInvocation: definition.disableModelInvocation ?? false,
    userInvocable: definition.userInvocable ?? true,
    contentLength: 0,
    source: 'bundled',
    loadedFrom: 'bundled',
    hooks: definition.hooks,
    skillRoot,
    context: definition.context,
    agent: definition.agent,
    isEnabled: definition.isEnabled,
    isHidden: !(definition.userInvocable ?? true),
    progressMessage: 'running',
    getPromptForCommand,
  }
  bundledSkills.push(command)
}
```

### 3.2 获取内置技能

```typescript
/**
 * 获取所有注册的内置技能。
 * 返回副本以防止外部修改。
 */
export function getBundledSkills(): Command[] {
  return [...bundledSkills]
}

/**
 * 清除内置技能注册表（用于测试）。
 */
export function clearBundledSkills(): void {
  bundledSkills.length = 0
}
```

## 四、磁盘技能加载

**文件位置**: `src/skills/loadSkillsDir.ts` (1086 行)

### 4.1 LoadedFrom 类型

```typescript
export type LoadedFrom =
  | 'commands_DEPRECATED'  // 旧 /commands/ 目录
  | 'skills'               // /skills/ 目录
  | 'plugin'               // 插件
  | 'managed'              // 托管配置
  | 'bundled'              // 内置
  | 'mcp'                  // MCP 服务器
```

### 4.2 getSkillDirCommands()

```typescript
/**
 * 从 /skills/ 和旧 /commands/ 目录加载所有技能。
 *
 * /skills/ 目录技能：
 * - 仅支持目录格式：skill-name/SKILL.md
 * - 默认 user-invocable: true
 *
 * 旧 /commands/ 目录技能：
 * - 支持目录格式 (SKILL.md) 和单 .md 文件格式
 * - 默认 user-invocable: true
 */
export const getSkillDirCommands = memoize(
  async (cwd: string): Promise<Command[]> => {
    const userSkillsDir = join(getClaudeConfigHomeDir(), 'skills')
    const managedSkillsDir = join(getManagedFilePath(), '.claude', 'skills')
    const projectSkillsDirs = getProjectDirsUpToHome('skills', cwd)

    // 从多个来源并行加载
    const [
      managedSkills,
      userSkills,
      projectSkillsNested,
      additionalSkillsNested,
      legacyCommands,
    ] = await Promise.all([
      isEnvTruthy(process.env.CLAUDE_CODE_DISABLE_POLICY_SKILLS)
        ? Promise.resolve([])
        : loadSkillsFromSkillsDir(managedSkillsDir, 'policySettings'),
      isSettingSourceEnabled('userSettings') && !skillsLocked
        ? loadSkillsFromSkillsDir(userSkillsDir, 'userSettings')
        : Promise.resolve([]),
      projectSettingsEnabled
        ? Promise.all(
            projectSkillsDirs.map(dir =>
              loadSkillsFromSkillsDir(dir, 'projectSettings'),
            ),
          )
        : Promise.resolve([]),
      projectSettingsEnabled
        ? Promise.all(
            additionalDirs.map(dir =>
              loadSkillsFromSkillsDir(join(dir, '.claude', 'skills'), 'projectSettings'),
            ),
          )
        : Promise.resolve([]),
      skillsLocked ? Promise.resolve([]) : loadSkillsFromCommandsDir(cwd),
    ])

    // 合并并去重
    const allSkillsWithPaths = [
      ...managedSkills,
      ...userSkills,
      ...projectSkillsNested.flat(),
      ...additionalSkillsNested.flat(),
      ...legacyCommands,
    ]

    // 使用 realpath 去重
    const fileIds = await Promise.all(
      allSkillsWithPaths.map(({ skill, filePath }) =>
        skill.type === 'prompt'
          ? getFileIdentity(filePath)
          : Promise.resolve(null),
      ),
    )

    const seenFileIds = new Map<string, SettingSource>()
    const deduplicatedSkills: Command[] = []

    for (let i = 0; i < allSkillsWithPaths.length; i++) {
      const entry = allSkillsWithPaths[i]
      if (entry === undefined || entry.skill.type !== 'prompt') continue
      
      const fileId = fileIds[i]
      if (fileId === null || fileId === undefined) {
        deduplicatedSkills.push(entry.skill)
        continue
      }

      const existingSource = seenFileIds.get(fileId)
      if (existingSource !== undefined) {
        logForDebugging(
          `Skipping duplicate skill '${skill.name}' from ${skill.source} (same file already loaded from ${existingSource})`,
        )
        continue
      }

      seenFileIds.set(fileId, skill.source)
      deduplicatedSkills.push(skill)
    }

    return deduplicatedSkills
  },
)
```

### 4.3 loadSkillsFromSkillsDir()

```typescript
/**
 * 从 /skills/ 目录路径加载技能。
 * 仅支持目录格式：skill-name/SKILL.md
 */
async function loadSkillsFromSkillsDir(
  basePath: string,
  source: SettingSource,
): Promise<SkillWithPath[]> {
  const fs = getFsImplementation()

  let entries
  try {
    entries = await fs.readdir(basePath)
  } catch (e: unknown) {
    if (!isFsInaccessible(e)) logError(e)
    return []
  }

  const results = await Promise.all(
    entries.map(async (entry): Promise<SkillWithPath | null> => {
      try {
        // 仅支持目录格式
        if (!entry.isDirectory() && !entry.isSymbolicLink()) {
          return null
        }

        const skillDirPath = join(basePath, entry.name)
        const skillFilePath = join(skillDirPath, 'SKILL.md')

        let content: string
        try {
          content = await fs.readFile(skillFilePath, { encoding: 'utf-8' })
        } catch (e: unknown) {
          if (!isENOENT(e)) {
            logForDebugging(`[skills] failed to read ${skillFilePath}: ${e}`)
          }
          return null
        }

        const { frontmatter, content: markdownContent } = parseFrontmatter(
          content,
          skillFilePath,
        )

        const skillName = entry.name
        const parsed = parseSkillFrontmatterFields(
          frontmatter,
          markdownContent,
          skillName,
        )
        const paths = parseSkillPaths(frontmatter)

        return {
          skill: createSkillCommand({
            ...parsed,
            skillName,
            markdownContent,
            source,
            baseDir: skillDirPath,
            loadedFrom: 'skills',
            paths,
          }),
          filePath: skillFilePath,
        }
      } catch (error) {
        logError(error)
        return null
      }
    }),
  )

  return results.filter((r): r is SkillWithPath => r !== null)
}
```

## 五、技能 Frontmatter 解析

### 5.1 parseSkillFrontmatterFields()

```typescript
export function parseSkillFrontmatterFields(
  frontmatter: FrontmatterData,
  markdownContent: string,
  resolvedName: string,
  descriptionFallbackLabel: 'Skill' | 'Custom command' = 'Skill',
): {
  displayName: string | undefined
  description: string
  hasUserSpecifiedDescription: boolean
  allowedTools: string[]
  argumentHint: string | undefined
  argumentNames: string[]
  whenToUse: string | undefined
  version: string | undefined
  model: ReturnType<typeof parseUserSpecifiedModel> | undefined
  disableModelInvocation: boolean
  userInvocable: boolean
  hooks: HooksSettings | undefined
  executionContext: 'fork' | undefined
  agent: string | undefined
  effort: EffortValue | undefined
  shell: FrontmatterShell | undefined
} {
  const validatedDescription = coerceDescriptionToString(
    frontmatter.description,
    resolvedName,
  )
  const description =
    validatedDescription ??
    extractDescriptionFromMarkdown(markdownContent, descriptionFallbackLabel)

  const userInvocable =
    frontmatter['user-invocable'] === undefined
      ? true
      : parseBooleanFrontmatter(frontmatter['user-invocable'])

  const model =
    frontmatter.model === 'inherit'
      ? undefined
      : frontmatter.model
        ? parseUserSpecifiedModel(frontmatter.model as string)
        : undefined

  const effortRaw = frontmatter['effort']
  const effort =
    effortRaw !== undefined ? parseEffortValue(effortRaw) : undefined

  return {
    displayName: frontmatter.name != null ? String(frontmatter.name) : undefined,
    description,
    hasUserSpecifiedDescription: validatedDescription !== null,
    allowedTools: parseSlashCommandToolsFromFrontmatter(frontmatter['allowed-tools']),
    argumentHint: frontmatter['argument-hint'] != null ? String(frontmatter['argument-hint']) : undefined,
    argumentNames: parseArgumentNames(frontmatter.arguments as string | string[] | undefined),
    whenToUse: frontmatter.when_to_use as string | undefined,
    version: frontmatter.version as string | undefined,
    model,
    disableModelInvocation: parseBooleanFrontmatter(frontmatter['disable-model-invocation']),
    userInvocable,
    hooks: parseHooksFromFrontmatter(frontmatter, resolvedName),
    executionContext: frontmatter.context === 'fork' ? 'fork' : undefined,
    agent: frontmatter.agent as string | undefined,
    effort,
    shell: parseShellFrontmatter(frontmatter.shell, resolvedName),
  }
}
```

### 5.2 createSkillCommand()

```typescript
export function createSkillCommand({
  skillName,
  displayName,
  description,
  hasUserSpecifiedDescription,
  markdownContent,
  allowedTools,
  argumentHint,
  argumentNames,
  whenToUse,
  version,
  model,
  disableModelInvocation,
  userInvocable,
  source,
  baseDir,
  loadedFrom,
  hooks,
  executionContext,
  agent,
  paths,
  effort,
  shell,
}: {...}): Command {
  return {
    type: 'prompt',
    name: skillName,
    description,
    hasUserSpecifiedDescription,
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
    paths,
    contentLength: markdownContent.length,
    isHidden: !userInvocable,
    progressMessage: 'running',
    userFacingName(): string {
      return displayName || skillName
    },
    source,
    loadedFrom,
    hooks,
    skillRoot: baseDir,
    async getPromptForCommand(args, toolUseContext) {
      let finalContent = baseDir
        ? `Base directory for this skill: ${baseDir}\n\n${markdownContent}`
        : markdownContent

      // 参数替换
      finalContent = substituteArguments(finalContent, args, true, argumentNames)

      // ${CLAUDE_SKILL_DIR} 替换
      if (baseDir) {
        const skillDir = process.platform === 'win32' ? baseDir.replace(/\\/g, '/') : baseDir
        finalContent = finalContent.replace(/\$\{CLAUDE_SKILL_DIR\}/g, skillDir)
      }

      // ${CLAUDE_SESSION_ID} 替换
      finalContent = finalContent.replace(/\$\{CLAUDE_SESSION_ID\}/g, getSessionId())

      // 安全：MCP 技能不执行 shell 命令
      if (loadedFrom !== 'mcp') {
        finalContent = await executeShellCommandsInPrompt(
          finalContent,
          {
            ...toolUseContext,
            getAppState() {
              const appState = toolUseContext.getAppState()
              return {
                ...appState,
                toolPermissionContext: {
                  ...appState.toolPermissionContext,
                  alwaysAllowRules: {
                    ...appState.toolPermissionContext.alwaysAllowRules,
                    command: allowedTools,
                  },
                },
              }
            },
          },
          `/${skillName}`,
          shell,
        )
      }

      return [{ type: 'text', text: finalContent }]
    },
  } satisfies Command
}
```

## 六、动态技能发现

### 6.1 发现机制

```typescript
// 动态发现的技能目录
const dynamicSkillDirs = new Set<string>()
const dynamicSkills = new Map<string, Command>()

// 条件技能（带 paths frontmatter）
const conditionalSkills = new Map<string, Command>()
const activatedConditionalSkillNames = new Set<string>()

/**
 * 通过从文件路径向上遍历到 cwd 来发现技能目录。
 */
export async function discoverSkillDirsForPaths(
  filePaths: string[],
  cwd: string,
): Promise<string[]> {
  const fs = getFsImplementation()
  const resolvedCwd = cwd.endsWith(pathSep) ? cwd.slice(0, -1) : cwd
  const newDirs: string[] = []

  for (const filePath of filePaths) {
    let currentDir = dirname(filePath)

    // 向上遍历到 cwd（不包括 cwd 本身）
    while (currentDir.startsWith(resolvedCwd + pathSep)) {
      const skillDir = join(currentDir, '.claude', 'skills')

      if (!dynamicSkillDirs.has(skillDir)) {
        dynamicSkillDirs.add(skillDir)
        try {
          await fs.stat(skillDir)
          // 检查是否 gitignored
          if (await isPathGitignored(currentDir, resolvedCwd)) {
            logForDebugging(`[skills] Skipped gitignored skills dir: ${skillDir}`)
            continue
          }
          newDirs.push(skillDir)
        } catch {
          // 目录不存在
        }
      }

      const parent = dirname(currentDir)
      if (parent === currentDir) break
      currentDir = parent
    }
  }

  // 按路径深度排序（最深的优先）
  return newDirs.sort((a, b) => b.split(pathSep).length - a.split(pathSep).length)
}
```

### 6.2 条件技能激活

```typescript
/**
 * 激活路径匹配的条件技能。
 */
export function activateConditionalSkillsForPaths(
  filePaths: string[],
  cwd: string,
): string[] {
  if (conditionalSkills.size === 0) {
    return []
  }

  const activated: string[] = []

  for (const [name, skill] of conditionalSkills) {
    if (skill.type !== 'prompt' || !skill.paths || skill.paths.length === 0) {
      continue
    }

    const skillIgnore = ignore().add(skill.paths)
    for (const filePath of filePaths) {
      const relativePath = isAbsolute(filePath)
        ? relative(cwd, filePath)
        : filePath

      if (skillIgnore.ignores(relativePath)) {
        // 激活技能
        dynamicSkills.set(name, skill)
        conditionalSkills.delete(name)
        activatedConditionalSkillNames.add(name)
        activated.push(name)
        logForDebugging(`[skills] Activated conditional skill '${name}' (matched path: ${relativePath})`)
        break
      }
    }
  }

  return activated
}
```

## 七、内置技能列表

`skills/bundled/` 目录包含以下内置技能：

| 文件 | 技能名 | 描述 |
|------|--------|------|
| `batch.ts` | batch | 批量操作 |
| `claudeApi.ts` | claude-api | Claude API 调用 |
| `claudeInChrome.ts` | claude-in-chrome | Chrome 集成 |
| `debug.ts` | debug | 调试辅助 |
| `keybindings.ts` | keybindings | 快捷键管理 |
| `loop.ts` | loop | 循环执行 |
| `loremIpsum.ts` | lorem-ipsum | 占位文本 |
| `remember.ts` | remember | 记忆管理 |
| `scheduleRemoteAgents.ts` | schedule-remote-agents | 远程代理调度 |
| `simplify.ts` | simplify | 简化输出 |
| `skillify.ts` | skillify | 技能创建 |
| `stuck.ts` | stuck | 卡住恢复 |
| `updateConfig.ts` | update-config | 配置更新 |
| `verify.ts` | verify | 验证执行 |

## 八、技能目录结构

```
~/.claude/skills/           # 用户技能
├── my-skill/
│   ├── SKILL.md            # 必需：技能定义
│   └── helpers/            # 可选：辅助文件
│       └── utils.js

.claude/skills/             # 项目技能
├── project-skill/
│   ├── SKILL.md
│   └── scripts/
│       └── build.sh

# SKILL.md 格式
---
name: my-skill
description: My custom skill
when_to_use: Use when you need to...
allowed-tools:
  - Read
  - Write
arguments:
  - inputFile
  - outputFile
argument-hint: <inputFile> <outputFile>
model: opus
context: fork
agent: general-purpose
user-invocable: true
disable-model-invocation: false
hooks:
  PreToolUse:
    - matcher: Read
      hooks:
        - type: prompt
          prompt: "Be careful with file reading"
paths:
  - "src/**/*.ts"
  - "lib/**/*.ts"
effort: high
---

Skill content here...

You can use ${CLAUDE_SKILL_DIR} to reference the skill directory.
Arguments: $1 = ${inputFile}, $2 = ${outputFile}
```