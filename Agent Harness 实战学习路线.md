## Agent Harness 实战学习路线

> 目标：从 0 到 1 构建一个 TypeScript CLI Agent Harness，以 Claude Code 源码为参考蓝本。每个阶段都有"读什么"和"做什么"两部分。

---

### 第一阶段：最小 Agentic Loop（建议 1 周）

**目标**：跑通一个能对话、能执行工具的 while(true) 循环。这是整个 Harness 的心脏，其他一切都是围绕这个循环的装甲。

#### 读什么

| 优先级 | 文件 | 关注点 |
|--------|------|--------|
| ★★★ | `src/query.ts` 第 300-500 行 | `queryLoop()` 的 while(true) 结构，重点看每次迭代的流程：准备消息 → 调用 API → 处理响应 → 执行工具 → 注入结果 → 继续循环 |
| ★★★ | `src/QueryEngine.ts` 第 1-100 行 | QueryEngineConfig 类型和 submitMessage() 的入口，理解"一个对话一个实例"的设计 |
| ★★ | `docs/architecture/02-query-engine.md` | 文档对 query loop 的 6 阶段拆解 |
| ★ | `src/context.ts` 全文（189 行） | 如何采集 Git 状态和 CLAUDE.md 作为上下文 |

#### 做什么

搭建你的最小项目骨架：

```
my-agent/
├── package.json        # Bun 项目
├── src/
│   ├── index.ts        # CLI 入口
│   ├── loop.ts         # 核心 while(true) 循环
│   ├── tools/
│   │   ├── types.ts    # Tool 接口（极简版）
│   │   ├── bash.ts     # Bash 执行工具
│   │   └── file-read.ts
│   └── context.ts      # 简单上下文采集
```

**里程碑 1**：实现一个能执行以下对话的 CLI：
```
You: 帮我看看当前目录有什么文件
Agent: [调用 BashTool: ls]
Agent: 当前目录有 3 个文件：...
You: 读取一下 package.json 的内容
Agent: [调用 FileReadTool: package.json]
Agent: package.json 的内容是...
```

关键技术点：
- 用 `@anthropic-ai/sdk` 的 `messages.stream()` 做流式调用
- 处理 `tool_use` 类型的 content block，执行对应工具，把结果作为 `tool_result` 注入消息列表
- 循环条件：模型返回 `stop_reason === 'end_turn'` 时停止，否则继续
- 上下文就是一个 `Message[]` 数组，每次 API 调用都传完整历史

**核心代码骨架**（这是 query.ts 第 300-500 行的极简翻译）：

```typescript
// loop.ts - 你的第一个 agentic loop
async function agentLoop(messages: Message[], tools: Tool[]) {
  while (true) {
    // 1. 调用 API
    const response = await client.messages.create({
      model: 'claude-sonnet-4-20250514',
      max_tokens: 4096,
      system: 'You are a helpful coding assistant.',
      messages,
      tools: tools.map(t => ({ name: t.name, description: t.description, input_schema: t.schema })),
    });

    // 2. 检查是否有工具调用
    const toolUses = response.content.filter(b => b.type === 'tool_use');
    if (toolUses.length === 0) {
      // 没有工具调用 = 对话结束
      const text = response.content.find(b => b.type === 'text')?.text;
      console.log(text);
      messages.push({ role: 'assistant', content: response.content });
      break;
    }

    // 3. 执行工具，注入结果
    messages.push({ role: 'assistant', content: response.content });
    const toolResults = [];
    for (const use of toolUses) {
      const tool = tools.find(t => t.name === use.name)!;
      const result = await tool.call(use.input);
      toolResults.push({ type: 'tool_result', tool_use_id: use.id, content: result });
    }
    messages.push({ role: 'user', content: toolResults });
    // 4. 继续循环
  }
}
```

这不到 30 行代码就是 Claude Code `query.ts` 1729 行的核心抽象。区别只在于边界条件处理——而边界条件处理正是 Harness Engineering 的全部。

---

### 第二阶段：工具系统与安全模型（建议 1-2 周）

**目标**：建立可扩展的工具注册机制，加入 Fail-Closed 权限模型。

#### 读什么

| 优先级 | 文件 | 关注点 |
|--------|------|--------|
| ★★★ | `src/Tool.ts` 全文（792 行） | Tool 接口的完整定义，特别是 `buildTool()` 工厂和 `TOOL_DEFAULTS`。理解 Fail-Closed 默认值 |
| ★★★ | `src/tools.ts` 全文（389 行） | `getAllBaseTools()` 和 `assembleToolPool()` 的组装逻辑 |
| ★★ | `src/tools/BashTool/` 目录 | BashTool 的权限检查（bashPermissions.ts）和安全检查（bashSecurity.ts）|
| ★★ | `src/tools/FileEditTool/` 目录 | old_string/new_string 替换模式的实现 |
| ★ | `docs/architecture/03-tool-system.md` | 6 阶段执行管线和 8 步权限决策树 |

#### 做什么

**里程碑 2**：实现一个有 5 个工具、带权限确认的 Agent：
- BashTool（带危险命令检测：rm -rf、curl | bash 等）
- FileReadTool
- FileEditTool（基于 old_string/new_string 替换）
- FileWriteTool
- GlobTool（文件搜索）

关键设计：
- 定义一个 `Tool` 接口，用 `buildTool()` 工厂填充默认值
- 工具执行前做权限检查：dangerous commands 需要用户确认，safe commands 自动通过
- 用 `isConcurrencySafe` 标记哪些工具可以并行执行（FileRead/Glob 可以，Bash/FileEdit 不行）

**核心设计模式**（来自 Tool.ts 的精华）：

```typescript
// types.ts - 极简版 Tool 接口
interface Tool {
  name: string;
  description: string;
  schema: JsonSchema;
  isConcurrencySafe: boolean;     // 默认 false
  isReadOnly: boolean;            // 默认 false
  isDestructive: boolean;         // 默认 false
  checkPermissions(input: any): 'allow' | 'deny' | 'ask';
  call(input: any): Promise<string>;
}

// 默认走最受限路径
function buildTool(def: Partial<Tool> & { name: string; call: Function }): Tool {
  return {
    isConcurrencySafe: false,
    isReadOnly: false,
    isDestructive: false,
    checkPermissions: () => 'ask',  // 默认需要确认
    ...def,
  };
}
```

---

### 第三阶段：上下文管理与压缩（建议 1-2 周）

**目标**：解决长对话的上下文溢出问题，实现至少两层压缩。

#### 读什么

| 优先级 | 文件 | 关注点 |
|--------|------|--------|
| ★★★ | `src/query.ts` 第 280-320 行 | 四层压缩管线的调用顺序和条件判断 |
| ★★★ | `src/services/compact/` 目录 | autoCompact.ts（全量压缩）和 microCompact.ts（细粒度压缩）的实现 |
| ★★ | `src/cost-tracker.ts` 全文（323 行） | Token 用量追踪和费用计算 |
| ★★ | `docs/architecture/deep-dive/memory-system.md` | AutoDream 四阶段的设计理念 |
| ★ | `src/context.ts` 全文（189 行） | Git 状态采集和 CLAUDE.md 自动发现 |

#### 做什么

**里程碑 3**：实现一个能在 50+ 轮对话中保持稳定的 Agent：
- Token 计数器（用 Anthropic 的 `countTokens` API 或简单估算）
- 自动压缩：当消息 token 数超过阈值（如上下文窗口的 70%），调用 LLM 生成摘要替换旧消息
- max_output_tokens 恢复：当模型输出被截断时，自动注入"请继续"消息
- 费用追踪：显示当前会话的 token 用量和美元费用

**关键洞察**（来自 query.ts 的设计）：
压缩顺序很重要——先做便宜的（移除僵尸消息），再做中等的（局部压缩），最后才做昂贵的（LLM 全量摘要）。能省则省。

---

### 第四阶段：CLI 体验与流式输出（建议 1 周）

**目标**：从"能跑"变成"好用"。

#### 读什么

| 优先级 | 文件 | 关注点 |
|--------|------|--------|
| ★★★ | `src/setup.ts` 全文（477 行） | 启动管线的操作顺序、并行预取策略 |
| ★★ | `src/services/api/` 目录 | API 流式调用和重试逻辑（withRetry.ts） |
| ★★ | `docs/architecture/deep-dive/cli-and-infrastructure.md` | 18 步启动流程和性能优化 |
| ★ | `src/services/notifier.ts` | 多渠道终端通知的设计 |

#### 做什么

**里程碑 4**：
- 流式输出（逐字显示 Agent 的回复，而非等完整回复才输出）
- 彩色输出（工具调用用不同颜色标记）
- Ctrl+C 中断（中断当前 API 调用，但不退出程序）
- 启动优化（快速路径：`--version` 和 `--help` 立即返回）
- 会话历史持久化（保存到本地文件，支持 `--resume` 恢复）

---

### 第五阶段：多工具编排与高级特性（建议 2 周）

**目标**：从"单轮对话"进化到"真正的编码助手"。

#### 读什么

| 优先级 | 文件 | 关注点 |
|--------|------|--------|
| ★★★ | `src/tools/AgentTool/` 目录 | 子 Agent 的 fork 机制和上下文隔离 |
| ★★ | `src/commands/init.ts`（20KB） | /init 命令如何引导创建 CLAUDE.md |
| ★★ | `src/skills/loadSkillsDir.ts`（34KB） | Markdown 技能文件的加载和解析 |
| ★ | `src/services/mcp/` 目录 | MCP 协议的核心实现 |
| ★ | `docs/architecture/06-skill-system.md` | Skills = Markdown 的扩展模式 |

#### 做什么

**里程碑 5**：
- GrepTool（用 ripgrep 做内容搜索）
- 子 Agent（AgentTool：fork 一个隔离上下文的子 Agent 处理子任务）
- CLAUDE.md 支持（自动发现项目根目录的 CLAUDE.md 并注入上下文）
- 简单的 Skill 系统（读取 .md 文件作为预定义 prompt）
- 错误恢复的三层熔断（预算上限、轮次上限、重试上限）

---

### 第六阶段：对照 CC 源码做架构审计（持续）

当你走完前五个阶段，你的 Agent 已经有了可用的骨架。这时候最有价值的学习方式是：**带着你自己项目中遇到的具体问题，去 CC 源码中找答案**。

常见的问题和对应的源码参考：

| 你遇到的问题 | CC 源码中的参考 | 文件位置 |
|-------------|----------------|---------|
| 长对话越来越慢 | 四层上下文压缩管线 | `services/compact/` |
| 工具执行顺序不确定 | StreamingToolExecutor 并发控制 | `services/tools/` |
| 权限请求太频繁 | Auto-Mode 两阶段分类器 | `deep-dive/api-and-permissions.md` |
| 模型输出被截断 | max_output_tokens 三层恢复 | `query.ts` 第 160-200 行 |
| 想支持第三方工具 | MCP 协议实现 | `services/mcp/` |
| 想做记忆持久化 | Memory 系统 + AutoDream | `deep-dive/memory-system.md` |
| 想支持多 Agent 协作 | AgentTool + Coordinator 模式 | `tools/AgentTool/` |
| 想做 CLI 远程操控 | Bridge 系统 | `bridge/` |

---

### 推荐的学习节奏

```
第 1 周：跑通最小 Loop（第一阶段）
         ↓  此时你能做一个能对话、能执行 Bash 的 Agent
第 2-3 周：工具系统 + 安全模型（第二阶段）
         ↓  此时你的 Agent 有 5 个工具，知道什么该问你什么该自己做
第 4-5 周：上下文管理（第三阶段）
         ↓  此时你的 Agent 能跑 50+ 轮长对话不崩溃
第 6 周：CLI 体验打磨（第四阶段）
         ↓  此时你的 Agent 用起来像一个真正的 CLI 产品
第 7-8 周：高级特性（第五阶段）
         ↓  此时你的 Agent 有子 Agent、技能系统、MCP 支持
第 9 周+：带着具体问题研读 CC 源码（第六阶段）
         ↓  持续迭代，逐步接近工业级水平
```

### 必读的 5 个文件（按顺序）

如果时间只够读 5 个文件，按这个顺序读：

1. **`src/query.ts`**（第 300-500 行）— Agentic Loop 的核心，理解 while(true) 的结构
2. **`src/Tool.ts`**（全文 792 行）— 工具系统的类型基础，理解 Fail-Closed 设计
3. **`src/tools/BashTool/BashTool.tsx`** — 最复杂工具的实现，理解权限+安全+执行
4. **`src/services/compact/autoCompact.ts`** — 上下文压缩，理解长对话如何不崩溃
5. **`src/QueryEngine.ts`**（第 1-200 行）— 对话生命周期管理，理解 AsyncGenerator 事件流

### 必读的 3 篇文档

1. **`docs/architecture/02-query-engine.md`** — 查询引擎的系统性文档
2. **`docs/architecture/03-tool-system.md`** — 工具系统的系统性文档
3. **学习指南的 Part 1 + Part 13** — Harness Engineering 六大支柱 + 方法论十条
