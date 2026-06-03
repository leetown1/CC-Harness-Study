## Agent Harness 基础学习计划

> 这份计划面向"从零理解 Agent Harness"的目标，按知识模块分层推进。不急着写代码——先建立完整的认知框架，后面动手时会事半功倍。建议用 3-4 周完成，按自己节奏调整。

---

## 总体结构

```
第一层：概念基础（理解 Agent 是什么）         ← 约 3 天
  ├── 学术根基：ReAct、CoT、Tool Use
  └── 核心公式：Agent = Model + Harness

第二层：产品图谱（理解行业在做什么）          ← 约 5 天
  ├── CLI 阵营：Claude Code、Codex CLI、Aider
  ├── IDE 阵营：Cursor、Copilot、Windsurf、Cline
  └── 云端阵营：Manus、Devin

第三层：核心机制（理解 Harness 的关键子系统）  ← 约 7 天
  ├── Agentic Loop（循环）
  ├── 工具系统（手和脚）
  ├── 上下文管理（记忆）
  ├── 权限与安全（缰绳）
  └── 多 Agent 编排（团队）

第四层：方法论（理解"为什么这样设计"）        ← 约 3 天
  ├── Anthropic "Building Effective Agents"
  ├── Manus 上下文工程六大实践
  └── Claude Code Harness 六大支柱

第五层：对照阅读（用 CC 源码验证理论）        ← 持续
  └── 带着问题去源码中找答案
```

---

## 第一层 · 概念基础：Agent 到底是什么（约 3 天）

### 第 1 天：理解 Agentic AI 的本质

**核心问题**：AI Agent 和普通的 LLM 对话有什么不同？

普通的 ChatGPT 对话是"一问一答"——你问，它答，结束。Agent 不同：它能**持续行动**，能**调用工具**，能**根据结果调整策略**，能**在多步任务中保持目标一致性**。

这个区别看似简单，但它引出了整个 Agent 工程的核心挑战：

- LLM 本身不会主动行动——需要一个循环（Loop）不断驱动它
- LLM 没有"手"——需要工具系统（Tools）让它与外部世界交互
- LLM 的记忆有限——需要上下文管理（Context Management）让它在长任务中不迷失
- LLM 不可预测——需要权限和安全系统（Guardrails）防止它做傻事

**这个"循环 + 工具 + 上下文 + 安全"的四件套，就是 Harness 的全部。**

推荐从 Anthropic 2024 年 12 月的官方博客 **"Building Effective Agents"** 开始读。这篇文章是整个 Agent 领域最有影响力的方法论之一，核心观点是：**简单优先，拒绝过度设计**。它提出了五种 Workflow 模式（Prompt Chaining、Routing、Parallelization、Orchestrator-Workers、Evaluator-Optimizer），几乎所有主流 Agent 产品都可以归类到其中一种或几种的组合。

**阅读清单**：
- Anthropic 博客 "Building Effective Agents"（约 30 分钟）— 搜索 `anthropic.com/research/building-effective-agents`
- 吴恩达（Andrew Ng）关于 Agentic AI 的演讲/博客 — 他对四种 Agentic 设计模式（Reflection、Tool Use、Planning、Multi-Agent）的总结非常清晰

### 第 2 天：学术根基——三篇必读论文

**论文 1：ReAct（Reasoning + Acting）**

ReAct 是几乎所有现代 Agent 的理论鼻祖。它的核心思想极其简洁：让 LLM 在"思考"和"行动"之间交替进行。

```
Thought: 我需要查找这个项目的测试配置
Action:  read_file("jest.config.js")
Observation: [文件内容]
Thought: 看到了，它用的是 Jest 28，配置了 ts-jest...
Action:  ...
```

这个 Thought-Action-Observation 循环就是 Claude Code 的 `query.ts` 中 while(true) 循环的学术原型。理解了 ReAct，你就理解了 Agentic Loop 的本质。

**论文 2：Toolformer**

Toolformer 回答了一个关键问题：LLM 怎么知道什么时候该调用工具、该调用哪个工具？论文提出了一种自监督的方法——让 LLM 自己学习在文本中插入工具调用标记。这奠定了后来 OpenAI function calling 和 Anthropic tool use 的理论基础。

**论文 3：Reflexion**

Reflexion 解决的是 Agent 如何从失败中学习。当 Agent 执行的工具返回错误，或者产出结果不符合预期时，它不应该简单地重试，而应该**用自然语言分析失败原因，生成"反思笔记"，在下一次尝试中避开同样的坑**。Claude Code 处理工具错误时的核心机制——保留错误日志、让模型分析原因、迭代修复——就是 Reflexion 思想的工程化。

**阅读方式**：不需要通读全文。每篇论文读 Abstract + Introduction + Method 部分即可（约 30-45 分钟/篇）。重点是理解核心思想，不需要理解数学推导。

### 第 3 天：补充概念——CoT、ToT 与 LATS

**Chain-of-Thought（CoT）**：让 LLM "逐步思考"而非直接给答案。这是 Agent 推理能力的基础。你在 Claude Code 中看到的 `<thinking>` block 就是 CoT 的体现。

**Tree-of-Thought（ToT）**：把 CoT 从线性推理扩展为树状搜索——同时探索多条推理路径，评估每条路径的前景，选择最有希望的继续。理论上很美，但计算成本太高（每条路径都需要一次 LLM 调用），目前主流 Agent 产品都**没有**完整实现 ToT。

**LATS（Language Agent Tree Search）**：把蒙特卡洛树搜索（MCTS）引入 Agent 决策。在 HumanEval 上达到 92.7% 的成功率，代表了 Agent 决策的理论上限。但同样因为计算成本，目前更多是学术参考而非工程实践。

**为什么了解这些但不深入？** 因为当前工业级 Agent 的核心范式仍然是 ReAct + CoT + Reflexion 的组合。ToT 和 LATS 代表了"未来可能的方向"，但理解现状比追逐前沿更重要。

**第一天结束时的自测题**：
- 用一句话说清 ReAct 和 CoT 的区别
- 解释为什么 Agent 需要一个"循环"，而不能靠单次 API 调用完成复杂任务
- 举一个 Reflexion 思想在日常 Agent 使用中的例子

---

## 第二层 · 产品图谱：行业在做什么（约 5 天）

这一层的目的是建立对主流 Agent 产品的**横向认知**。你不需要每个产品都用一遍，但需要理解它们的设计选择和背后的理由。

### 第 4-5 天：三大阵营概览

当前 AI Coding Agent 产品可以分为三大阵营，每个阵营代表了一种对"Agent 应该怎么和人协作"的不同回答：

#### CLI 阵营："把 Agent 放到终端里"

| 产品 | 核心特点 | 设计理念 |
|------|---------|---------|
| **Claude Code** | Anthropic 官方，512K 行 TS，React+Ink TUI | 深度终端集成 + Fail-Closed 安全 + MCP 开放生态 |
| **Codex CLI** | OpenAI 官方，开源，Rust 实现 | 高性能终端 + 沙箱隔离 + 类似 CC 的形态 |
| **Aider** | 开源社区，Python | Git-first 工作流，每次修改自动 commit，轻量级 |

CLI 阵营的共同信念：**终端是程序员最高效的交互界面**，Agent 应该融入终端而非取代终端。

**重点研究**：Claude Code（你已经有完整源码）。Codex CLI 和 Aider 可以读官方文档和 README 了解设计理念即可。

#### IDE 阵营："把 Agent 嵌入编辑器"

| 产品 | 核心特点 | 设计理念 |
|------|---------|---------|
| **Cursor** | VS Code fork，自研代码索引，三层 Agent 模式 | AI-native IDE，上下文管理是最深的护城河 |
| **GitHub Copilot** | GitHub 官方，最大用户基数，Workspace 功能 | 平台生态优势，从补全到 Agent 的渐进演进 |
| **Windsurf** | Codeium 出品，Cascade 工作流 | 强调"flow state"，减少用户干预 |
| **Cline / Roo Code** | VS Code 插件，开源 | 社区驱动，快速迭代，MCP 生态的积极推动者 |

IDE 阵营的共同信念：**代码编辑是可视化的活动**，Agent 应该在编辑器中展示 diff、高亮变更、提供内联建议，而不是在终端里输出文本。

**重点研究**：Cursor。它的三层模式设计（Tab 补全 → Composer 编辑 → Agent 自主执行）是"自主性光谱"上最优雅的产品化实践。

#### 云端阵营："让 Agent 自己干活"

| 产品 | 核心特点 | 设计理念 |
|------|---------|---------|
| **Manus** | 通用 AI Agent，云端沙箱，200+ 工具 | "Less Structure, More Intelligence"，异步自主执行 |
| **Devin** | Cognition 出品，AI 软件工程师 | 完整开发环境，端到端自主完成软件工程任务 |

云端阵营的共同信念：**人类不应该盯着 Agent 干活**，应该下达任务后去做别的事，等结果好了再看。

**重点研究**：Manus。它的上下文工程六大实践是目前公开资料中对 Context Engineering 最详尽的工业级分享。

### 第 6 天：深入 Cursor——三层模式与上下文工程

Cursor 的产品形态演进本身就是一部"Agent 设计思想进化史"：

**Tab 模式**（最早）：纯代码补全，光标后面的灰色建议文字。这是最轻量的 AI 辅助——延迟必须在 200ms 以内，不能打断编码节奏。Cursor 自训小模型专门优化这个场景。

**Composer 模式**（中期）：多文件编辑，用户描述需求，AI 生成跨文件的代码变更，用户审查后应用。这个模式的关键设计是**"人在回路中"**——AI 提出方案，人类审批。

**Agent 模式**（最新）：全自主执行。Agent 可以读写文件、执行终端命令、搜索代码、安装依赖——和 Claude Code 类似，但在 IDE 内完成。Cursor 3.0 的 Agents Window 取代文件树成为核心界面，标志着从"编辑器"向"Agent 指挥控制台"的转型。

**Cursor 上下文管理的深度**是它最核心的竞争力。它的 RAG 流水线包括：Merkle Tree 变更检测（感知哪些文件变了）→ Tree-sitter AST 分块（按语法结构切分代码）→ 768 维 Embedding → Turbopuffer 向量存储。这让它能从数十万文件中毫秒级检索出最相关的代码片段注入上下文。

**思考题**：为什么 Cursor 选择"三层模式"而不是直接给一个全自主 Agent？这背后是关于**信任级别和自主性之间的平衡**——用户对 Tab 补全的信任阈值低（错了按一下退格就行），对 Agent 模式的信任阈值高（它可能改错多个文件）。三层模式让用户可以根据任务风险和自身信任度选择合适的自主性级别。

### 第 7 天：深入 Manus——"Less Structure, More Intelligence"

Manus 的设计理念与 Claude Code/Cursor 形成了有趣的对比。

Manus 的核心信条是**"更少结构，更多智能"**。团队认为，不应过度预设 Agent 的角色和流程结构，而应该给 LLM 足够的上下文和工具，让智能自然涌现。他们的框架被重写了 5 次，最终选择了最简洁的设计。

这与 Claude Code 的"六大支柱"式工程化形成了鲜明对比：
- Claude Code 是**重装甲**——512K 行代码，95% 是 Harness，用严格的工程约束保证可靠性
- Manus 是**轻装骑兵**——依赖上下文工程和模型能力本身，减少框架层的干预

两种方式各有道理，适用于不同场景。Claude Code 面向专业开发者，需要对每一步操作有精确控制；Manus 面向通用任务，需要灵活适应各种意想不到的场景。

**Manus 上下文工程六大实践**（2025 年 7 月团队技术博客）：

1. **KV-Cache 命中率是最关键的优化指标**——保持上下文前缀稳定性，只追加不修改。这一项优化就能带来 10 倍成本降低。
2. **文件系统作为无限上下文**——原始数据和中间结果"卸载"到文件，LLM 只保留摘要和指针。
3. **工具遮蔽法优于移除工具**——不再需要的工具不删除（会破坏 KV-Cache），而是标记为不可用。
4. **重写 ToDo 清单操控注意力**——定期让 Agent "复述"任务清单，利用 LLM 对最近内容的注意力偏好。
5. **保留错误日志而非删除**——让模型从过去的错误中学习，删除反而会让模型重复犯错。
6. **压缩必须可逆**——上下文压缩必须能通过文件系统恢复原始信息。摘要会引入损失，宁可多保留。

**对比思考**：这六条和 Claude Code 的四层压缩管线（Snip → Micro → Collapse → Auto）有什么异同？Manus 更强调"不要过度压缩"，Claude Code 更强调"按顺序渐进压缩"。背后的原因是产品形态不同——Manus 的任务更长更不可预测（可能需要 50+ 次工具调用），Claude Code 的任务更聚焦（通常是一个编程问题的解决）。

### 第 8 天：横向对比——建立自己的判断框架

用这张表来做横向对比，每个维度都问自己"为什么这个产品做了不同的选择"：

| 维度 | Claude Code | Cursor | Manus |
|------|-------------|--------|-------|
| **产品形态** | CLI 终端 | IDE 编辑器 | 云端 Web |
| **执行环境** | 用户本地 | 用户本地 | 云端沙箱 |
| **交互模式** | 对话式，人确认关键步骤 | 三层自主性（Tab/Composer/Agent） | 异步提交，等结果 |
| **模型策略** | Claude 自有的模型 | 多模型 + 自训小模型 | 混合模型栈 |
| **上下文策略** | 四层压缩管线 | RAG + 代码索引 | 文件系统卸载 + 注意力操控 |
| **安全模型** | Fail-Closed + 五层纵深 | Auto-Run 开关 | 沙箱隔离 |
| **可扩展性** | MCP + Skills(Markdown) | 插件 + MCP | 200+ 内置工具 |
| **多 Agent** | AgentTool 子 Agent | Background Agent | Planner-Executor-Verifier |
| **开源程度** | 闭源（源码可分析） | 闭源 | 闭源（OpenManus 开源版） |

**第二层结束时的自测题**：
- 解释三大阵营各自适合什么样的用户和场景
- 为什么 Cursor 要做三层模式而不是直接做 Agent？
- Manus 的 "Less Structure" 和 Claude Code 的 "六大支柱" 分别适合什么场景？
- 如果你要做一个面向数据分析的 Agent，你会偏向哪种设计？为什么？

---

## 第三层 · 核心机制：Harness 的五个关键子系统（约 7 天）

这一层从"产品"下沉到"机制"。不管哪个阵营的产品，都绕不开这五个核心子系统。

### 第 9-10 天：Agentic Loop——Agent 的心脏

这是 Harness 最核心的机制，没有之一。所有 Agent 产品，无论形态多不同，底层都有一个类似的循环：

```
while (任务未完成) {
    1. 准备上下文（消息历史 + 系统提示 + 工具定义）
    2. 调用 LLM API
    3. 解析响应（文本 or 工具调用？）
    4. 如果是工具调用 → 执行工具 → 把结果注入消息历史
    5. 如果是文本 → 输出给用户 → 结束循环
    6. 检查终止条件（预算、轮次、错误）
}
```

这个循环在不同产品中的实现方式不同，但核心结构一致：
- Claude Code：`query.ts` 的 `queryLoop()`，AsyncGenerator 模式
- Cursor Agent 模式：类似的循环，但在 IDE 的后台线程中运行
- Manus：CodeAct 范式，Agent 生成代码并在沙箱中执行
- Aider：更简单的循环，每次修改都自动 git commit

**阅读材料**：
- 学习指南 Part 3（查询引擎），重点理解 16 步循环和四层压缩管线
- `src/query.ts` 第 300-500 行，对照代码理解循环结构
- Anthropic "Building Effective Agents" 中的五种 Workflow 模式，理解 Loop 是其中"Routing"和"Orchestrator-Workers"的基础

**关键问题**：
- 循环的终止条件有哪些？（end_turn、预算超限、轮次超限、错误熔断）
- 工具并行执行时如何处理错误？（Claude Code 的策略：取消兄弟工具，不终止父级循环）
- 上下文在每次迭代中如何变化？（只追加，不修改已有内容——保护 KV-Cache）

### 第 11-12 天：工具系统——Agent 的手和脚

工具系统决定了 Agent 能做什么、不能做什么。核心设计决策包括：

**工具的定义方式**：Claude Code 用 TypeScript 接口（50+ 字段），Manus 用 200+ 内置工具，Aider 只用了几个核心工具（读写文件、运行测试）。工具越多不等于越好——每个工具都在消耗上下文窗口（工具定义本身也是 token），工具过多反而会让模型选择困难。

**权限模型**：这是产品之间差异最大的地方。
- Claude Code：Fail-Closed，默认走最受限路径，五层纵深防御
- Cursor：Auto-Run 开关，用户决定信任级别
- Manus：沙箱隔离——不需要精细权限控制，因为 Agent 在隔离环境中运行，搞坏了也没关系
- Devin：同样是沙箱隔离，但提供了更细粒度的审批流程

**关键洞察**：沙箱隔离 vs 精细权限 是两种根本不同的安全哲学。沙箱隔离说"随便你做什么，但只能在这个房间里"；精细权限说"我可以让你在整个系统里活动，但某些动作需要你确认"。Claude Code 选了后者因为用户在自己的机器上运行，不能把用户锁在沙箱里；Manus/Devin 选了前者因为 Agent 在云端运行，沙箱是天然的选择。

**阅读材料**：
- 学习指南 Part 4（工具系统），重点理解 Fail-Closed 设计和缓存稳定性
- `src/Tool.ts` 全文（792 行），理解 50+ 字段的工具接口
- `src/tools/BashTool/` 目录，理解最复杂工具的权限+安全设计

### 第 13-14 天：上下文管理——Agent 的记忆

上下文管理是长任务可靠性的关键。三个核心问题：

**问题一：上下文窗口装不下怎么办？**

所有产品都面临这个问题，但解决策略不同：
- Claude Code：四层压缩管线（Snip → Micro → Collapse → Auto），从轻到重渐进处理
- Manus：文件系统卸载 + KV-Cache 稳定性优先 + 压缩必须可逆
- Cursor：RAG 按需检索，只在需要时拉取相关代码
- Aider：更暴力——用 `--map-tokens` 控制仓库地图大小，超出的部分用 `/tokens` 命令查看

**问题二：怎么决定什么该放入上下文？**

这是"上下文架构"支柱的核心。Claude Code 的策略是：系统提示（静态）+ Git 状态（项目快照）+ CLAUDE.md（记忆）+ 工具结果（动态）。Cursor 的策略更复杂：代码索引 + 语义搜索 + 当前编辑的文件 + 最近的操作历史。

**问题三：怎么保护 KV-Cache 命中率？**

这是 Manus 团队着重强调的优化点。核心原则是**上下文前缀稳定性**——只追加，不修改。任何对已有内容的修改都会使后续所有 KV-Cache 失效，导致推理速度下降和成本上升。这解释了 Claude Code 为什么工具列表不能全局排序（会交错 MCP 工具，破坏缓存断点）。

**阅读材料**：
- Manus 技术博客 "Context Engineering for AI Agents"（搜索 `manus.im/blog`）
- 学习指南 Part 3（四层压缩管线）和 Part 5（AutoDream 记忆整合）
- `src/services/compact/` 目录的 autoCompact.ts 和 microCompact.ts

### 第 15 天：权限与安全——Agent 的缰绳

安全模型的选择直接受产品形态影响：

| 形态 | 安全策略 | 理由 |
|------|---------|------|
| 本地 CLI（CC） | 精细权限 + Fail-Closed | 用户在自己的机器上，Agent 有完整系统访问权限 |
| IDE 插件（Cursor） | Auto-Run 开关 | 用户在熟悉的编辑器中，通过开关控制自主性 |
| 云端沙箱（Manus） | 进程隔离 | Agent 在虚拟环境中运行，搞坏了可以重建 |
| 开源工具（Aider） | 最小权限 | 只做 Git 操作，不执行任意命令 |

Claude Code 的五层纵深防御是目前公开资料中最精细的安全设计。但 Manus 的沙箱隔离更简洁——如果 Agent 不可能伤害你的系统，就不需要复杂的权限决策树。

**思考题**：如果你的 Agent 运行在用户的 Docker 容器中（半隔离），你会选择哪种安全策略？

**阅读材料**：
- 学习指南 Part 7（安全与权限）
- `docs/architecture/deep-dive/api-and-permissions.md`

### 第 16 天：多 Agent 编排——从单兵到团队

当单个 Agent 无法胜任复杂任务时，就需要多个 Agent 协作。三种主流编排模式：

**模式一：Fork 子 Agent（Claude Code）**

AgentTool 生成一个子 Agent，子 Agent 拥有独立的上下文和工具白名单。父 Agent 和子 Agent 通过结构化消息通信，共享文件系统但隔离上下文。这是"进程隔离"的思路。

**模式二：Planner-Executor-Verifier（Manus）**

三个专职 Agent 分工协作：Planner 拆解任务，Executor 执行具体操作，Verifier 验证结果质量。通过共享看板（Shared Kanban）协同。这是"组织分工"的思路。

**模式三：Background Agent（Cursor/Devin）**

Agent 在后台独立运行，完成后通知用户。用户不需要实时监控，只在结果出来时审查。这是"异步委托"的思路。

**阅读材料**：
- 学习指南 Part 5（多 Agent 编排）
- `src/tools/AgentTool/` 目录
- Manus 公开的架构分享资料

---

## 第四层 · 方法论：为什么这样设计（约 3 天）

这一层是前面所有知识的提炼和升华。

### 第 17 天：Anthropic "Building Effective Agents" 精读

这篇博客的核心观点：

1. **简单优先**：不要一开始就搭建复杂的多 Agent 系统。先用一个 Agent + 几个工具解决问题，只在确实需要时才增加复杂度。
2. **五种 Workflow 模式**：Prompt Chaining（链式调用）、Routing（路由）、Parallelization（并行化）、Orchestrator-Workers（编排者+工人）、Evaluator-Optimizer（评估+优化）。
3. **Workflow vs Agent**：Workflow 是预定义的流程（确定性的），Agent 是自主决策的（不确定的）。大多数场景用 Workflow 就够了，Agent 只在需要灵活性的场景使用。

**阅读方式**：逐段精读，每读完一种模式，想一想你之前研究的产品中哪个用了这种模式。

### 第 18 天：Claude Code Harness 六大支柱 + Manus 六大实践对照

| 维度 | Claude Code 六大支柱 | Manus 六大实践 |
|------|---------------------|---------------|
| 上下文 | 四层压缩管线 | 文件系统卸载 + 压缩必须可逆 |
| 安全 | Fail-Closed + 五层纵深 | 沙箱隔离（无需精细权限） |
| 验证 | 16 步循环，15 步做验证 | Verifier Agent 独立验证 |
| 隔离 | 进程级上下文隔离 | 每个任务独立沙箱 |
| 熵治理 | AutoDream 自动整合 | ToDo 重写操控注意力 |
| 可扩展 | Skills=Markdown + MCP | 200+ 内置工具 + CodeAct |

**关键洞察**：Claude Code 和 Manus 解决的是相同的问题（如何让 Agent 在长任务中保持可靠），但因为产品形态不同（本地 CLI vs 云端通用 Agent），选择了截然不同的工程路径。没有谁对谁错——**好的工程设计是对约束条件的最优响应**。

### 第 19 天：建立你自己的设计原则

综合前面所有学习内容，尝试提炼 5-10 条你自己的 Agent Harness 设计原则。这些原则应该能回答以下问题：

- 什么时候该让 Agent 自主行动，什么时候该让人类确认？
- 上下文应该包含什么、不包含什么？
- 工具应该多还是少？精细还是粗糙？
- 安全模型的粒度应该到什么程度？
- 什么时候该引入多 Agent，什么时候单 Agent 就够了？

**写下来，后面动手时这就是你的设计指南针。**

---

## 第五层 · 持续对照阅读

完成前四层后，你已经有了完整的认知框架。这时候最有价值的学习方式是：**带着具体问题去源码中找答案**。

| 你好奇的问题 | 去哪找答案 |
|-------------|-----------|
| Agentic Loop 的工业级实现长什么样？ | `src/query.ts` |
| 50+ 字段的工具接口是不是过度设计？ | `src/Tool.ts` |
| 长对话怎么不崩溃？ | `src/services/compact/` |
| AI 怎么"做梦"整理记忆？ | `docs/architecture/deep-dive/memory-system.md` |
| 为什么 CLI 要做虚拟宠物？ | `docs/architecture/deep-dive/buddy-system.md` |
| 权限系统为什么设计得如此"不信任"Agent？ | `docs/architecture/deep-dive/api-and-permissions.md` |
| MCP 协议怎么连接外部工具？ | `docs/architecture/deep-dive/mcp-system.md` |

---

## 推荐的外部阅读资源

### 必读（5 篇）

1. Anthropic "Building Effective Agents" — 搜索 `anthropic.com/research/building-effective-agents`
2. Manus "Context Engineering for AI Agents" — 搜索 `manus.im/blog`
3. ReAct 论文 — 搜索 `arxiv.org/abs/2210.03629`
4. Reflexion 论文 — 搜索 `arxiv.org/abs/2303.11366`
5. 腾讯技术工程 "顶级开发团队设计的 Harness 工程项目源码什么样" — 你已有的链接

### 选读（按兴趣）

6. Toolformer 论文 — 理解 tool use 的理论基础
7. LATS 论文 — 理解 Agent 决策的理论上限
8. Cursor 官方博客 — 搜索 `cursor.com/blog`
9. OpenAI Codex CLI README — 搜索 `github.com/openai/codex`
10. Aider 文档 — 搜索 `aider.chat/docs`

### 播客/视频

11. Cursor CEO 的访谈（搜索 YouTube/B站）— 了解产品决策背后的故事
12. Manus 团队的技术分享 — 搜索 B 站/YouTube
13. Anthropic 的 "How we build" 系列 — 官方视角

---

> 这份计划是一个框架，不是约束。如果你对某个模块特别感兴趣，可以多花时间深挖；如果某个模块已经了解，可以快速跳过。最重要的是：**每学完一层，都能用自己的话向别人解释清楚**。如果你能做到这一点，后面动手写代码时，设计决策会自然而然地浮现出来。
