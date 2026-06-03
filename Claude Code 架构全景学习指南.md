## Claude Code (Harness) 架构全景学习指南

> 本文档结合腾讯技术工程文章《顶级开发团队设计的 Harness 工程项目源码什么样》与 CC学习 文件夹中的 37 篇架构文档、512K+ 行源码，系统性地拆解 Claude Code 这一工业级 AI Coding Agent 的完整架构。不同于纯技术罗列，本文以**产品哲学**为主线串联每个技术模块，试图回答一个更深层的问题：一个顶级团队是如何*思考* Agent 工程的。

---

## 前言：这不是一篇源码分析

腾讯技术工程的文章开篇就点明了一个关键判断："社区普遍认为，这份源码不仅仅展示了一个产品的实现细节，更像是一本关于如何构建工业级 AI Agent 的技术教科书。" 这个判断的分量在于——它说的不是"一个好产品"，而是"一本教科书"。区别在哪里？教科书意味着**方法论的可迁移性**。你不一定在做 CLI Agent，但这套工程思维可以指导任何 AI Agent 系统的构建。

文章提出了一个公式作为全文的理论基石：**Agent = Model + Harness**。模型是引擎，Harness 是缰绳、护栏和高速公路。在这个项目中，模型调用相关的代码不到 5%，剩下 95% 全部是 Harness。文章的核心论断是："AI Agent 的瓶颈从来不在模型智能，而在基础设施。"

这句话值得反复咀嚼。大多数团队在做 AI Agent 时，精力分配恰好反过来——90% 的时间在调 prompt、选模型、做 fine-tuning，只有 10% 在工程基础设施上。而这份 512K 行的源码告诉我们，真正决定 Agent 是否可靠、是否可控、是否好用的，是那 95% 的"非模型"代码。

---

## Part 1 · Harness Engineering：一种新的工程范式

### 什么是 Harness Engineering

腾讯文章给出了一个精炼的定义："Harness Engineering——2026 年让 Agent 可靠持续不失控的工程方法。核心哲学八个字：**人类掌舵，Agent 执行**。通过工程手段，让聪明但不可预测的模型在约束反馈中稳定工作。"

这里有几个关键词值得拆解。"可靠"意味着可预测——同一个任务跑两次应该得到质量相近的结果。"持续"意味着不崩溃——长对话、大文件、复杂工具链不会让系统失控。"不失控"意味着人类始终保有最终控制权——Agent 可以自主行动，但不能脱离人类的意图边界。

"聪明但不可预测"是对当前大模型最精准的定性。模型能力很强，但你无法保证它下一次输出和上一次一样。Harness Engineering 的全部意义，就是在这种不确定性之上构建确定性的工程系统。

### 六大支柱

文章将这套工程方法论提炼为六大支柱，每个支柱都对应着源码中一个庞大的子系统。

**支柱一：上下文架构（Context Architecture）**——"精准设计进入模型上下文的信息。永远不要让上下文窗口变成垃圾场。" 文章引用了一个研究结论：当上下文窗口利用率超过 40% 时，模型推理质量显著下滑。这解释了为什么 Claude Code 投入了不成比例的工程量在上下文压缩上——四级压缩管道（Snip → Micro → Collapse → Auto Compact）是整个系统最精密的管线之一。

**支柱二：架构约束（Architecture Constraints）**——"用代码和工具强制执行规则，而非依赖 prompt 软约束。" 这是与"prompt engineering"截然不同的哲学。Prompt 是建议，代码是法律。`buildTool()` 工厂的 Fail-Closed 默认值是这个支柱最精髓的体现：忘了设置安全属性？那就走最受限路径。遗漏不是漏洞。

**支柱三：自验证循环（Self-Verification Loops）**——"在执行流程中内置验证检查点，防止死循环与静默失败。" 文章揭示了一个惊人的数据：`query()` 循环的 16 个步骤中，仅有 1 步是调用模型，其余 15 步全部是验证、修复、状态管理逻辑。这是 Agent 工程最反直觉的真相——模型调用是整个系统中最简单的部分。

**支柱四：上下文隔离（Context Isolation）**——"多 Agent 协作时保持每个 Agent 上下文纯净，防止跨边界信息污染。" 实现方式是进程级隔离、通信接口化、控制面与数据面分离。

**支柱五：熵治理（Entropy Governance）**——"对抗系统状态自然熵增。" 这是最有诗意的设计：AutoDream 梦境系统模拟人类 REM 睡眠的记忆巩固机制，在后台自动进行上下文蒸馏、知识沉淀、状态清理和碎片整理。让 AI "做梦"来整理记忆——这不是技术炫技，而是严肃的工程选择。

**支柱六：可拆解性（Disassemblability）**——"模块化设计使 Harness 能随模型迭代优雅适配。" 依赖注入让每个组件可替换，Skills 用纯 Markdown 定义让非程序员也能扩展，MCP 标准协议让工具生态独立于产品迭代，模型降级容错确保任何供应商切换都不会导致系统崩溃。

---

## Part 2 · 启动性能：200ms 的工程信仰

### 为什么启动速度是"生死线"

腾讯文章引用了团队内部的一句话："对 CLI 工具来说，启动速度是生死线。" 这背后有一个产品心理学判断：用户对 CLI 工具的耐心阈值大约是 200ms。超过这个阈值，用户会从"工具"的心理分类转向"应用"，期望和容忍度都会改变。

Bun 运行时的选择不仅仅是"快 4-6 倍"这么简单。更深层的原因是 Bun 内置了编译时特性开关（`feature()` 函数），这让死代码消除从运行时的 Tree-shaking 升级为编译时的条件分支消除。对于外部构建，未启用的特性对应的整段代码从二进制中消失——不是"不被调用"，而是"从未存在"。

### 四层启动链路与并行预取

启动流程分为四层：`cli.tsx`（快速路径预判）→ `main.tsx`（并行预取）→ `init.ts`（延迟加载）→ `setup.ts`（完整初始化）。

第一层的快速路径是关键：对于 `--version`、`--help`、`mcp` 等子命令，系统在前 13 行代码内直接返回，不加载任何多余模块。这意味着用户输入 `claude --version` 时，512K 行代码中的绝大部分根本没有被解析。

第二层的并行预取体现了"不等就跑"的工程哲学。代码中大量使用 `void` 前缀启动异步操作但不等待：`void lockCurrentVersion()`、`void getCommands()`、`void import(...)` 。注释中明确记录了策略的核心理由：**用户看到第一个 prompt 的时间比后台初始化完成的时间更重要**。这是以用户体验为锚点的优先级排序，而非以系统完整性为锚点。

第三层有一个经典的 Lazy Loading 案例：`/insights` 命令对应一个 113KB/3200 行的模块，使用动态 `import()` 延迟加载。这个模块只有在用户实际输入 `/insights` 时才会被加载——99% 的会话永远不会触发它。

### Preconnect：提前握手

另一个精妙的优化是 TCP Preconnect：在用户还在看终端初始化的时候，系统已经预先建立了与 API 服务器的 TCP 连接，完成了 TLS 握手。当用户输入第一条消息时，网络请求可以零延迟发出。这种"时间折叠"式的优化在 512K 行代码中随处可见——每一毫秒都被认真对待。

---

## Part 3 · 查询引擎：16 步循环中只有 1 步在调用模型

### Agentic Loop 的本质

查询引擎是整个系统的"心脏"，由 `QueryEngine.ts`（1295 行）和 `query.ts`（1729 行）协作实现。腾讯文章揭示了一个反直觉的事实：`query()` 的 while(true) 循环从第 307 行延伸到第 1728 行，跨越 1421 行代码。文章将其概念性拆解为"16 个步骤"（这是文章的分析视角，而非代码中的显式标注），其中只有 1 步是调用 LLM API。其余步骤是：消息准备、上下文压缩（四层管线）、权限验证、工具执行、结果处理、错误恢复、状态持久化、Token 预算检查……

这解释了为什么 `query.ts` 有 1729 行——真正的"智能"只占几十行（构造 API 请求、解析响应），剩余 95% 的代码都在管理这个智能的边界条件。

### AsyncGenerator：流式事件流的优雅

整个循环使用 AsyncGenerator 模式，这是架构中最核心的设计决策。`submitMessage()` 返回 `AsyncGenerator<SDKMessage>`，将复杂的多轮异步对话表达为可消费的事件流。调用方通过 `for await` 逐步接收 assistant 消息、stream 事件、工具使用摘要、压缩边界、最终结果。

为什么选择 AsyncGenerator 而非 Observable 或 EventEmitter？文章没有直接说，但从代码可以推断：AsyncGenerator 天然支持背压（backpressure）、可中断（通过 `.return()`）和有序消费，这三点对 Agent 循环至关重要。Observable 的多播能力在这里是多余的——每个对话只有一个消费者。

### State 对象：跨迭代替换的工程洁癖

循环不使用 9 个独立变量赋值来传递状态，而是将所有可变状态集中在 `State` 对象中。每个 continue 站点写入 `state = { ... }`，每次迭代顶部解构为局部变量。文章评价这种做法："一个小小的设计选择，体现了对状态管理的洁癖——在 512K 行代码中，状态污染是最致命的技术债。"

### 四层上下文压缩：与遗忘的精确博弈

这是整个系统最精密的管线之一，也是"上下文架构"支柱的核心实现。四层压缩按严格顺序执行：

**Snip Compact**（最轻量）移除历史中的僵尸消息——那些被后续消息覆盖且不再相关的内容。成本几乎为零。

**Micro Compact**（细粒度）在缓存编辑模式下进行局部压缩，保留 prompt cache 的连续性。

**Context Collapse**（读时投影）将已归档消息替换为摘要视图，类似数据库的物化视图。

**Auto Compact**（最重量级）当 token 数超过阈值时，调用 LLM 做全量压缩摘要。

顺序至关重要。文章特别强调：collapse 在 autocompact 之前运行——如果 collapse 能将 token 数降到阈值以下，autocompact 就是 no-op，从而保留了更细粒度的上下文。这是一个**贪心但有序**的策略：先用最便宜的方法尝试，只在必要时才付出最高成本。

另一个精妙的设计是 `taskBudgetRemaining` 变量。它追踪 compact 后被"摘要掉"的 token 支出。原因是：uncompacted 时服务端能看到完整历史自行计算倒计时；compact 后服务端只看到摘要会少算，需要客户端告知实际消耗。这是分布式系统中"真相分裂"问题的一个优雅解法。

### `using` 关键字：TC39 提案的工业实践

代码中使用了 TC39 Explicit Resource Management 提案的 `using` 语法来做 Memory Prefetch：

```typescript
using pendingMemoryPrefetch = startRelevantMemoryPrefetch(...)
```

这确保 generator 在所有退出路径上都能正确清理预取资源。在一个 512K 行的项目中采用尚未正式定稿的语言特性，体现了团队对工程前沿的自信和对"正确性"的执着——他们宁愿用 polyfill 也不用 try/finally 的丑陋替代。

### 错误恢复：三层熔断与 max_output_tokens 恢复

系统实现了三层熔断机制：`maxBudgetUsd`（美元预算）、`maxTurns`（对话轮次）、`maxStructuredOutputRetries`（结构化输出重试次数）。任何一项超限立即终止循环。

但更精巧的是 `max_output_tokens` 的恢复策略。当模型输出被截断时，系统不会直接报错，而是：第一步，尝试升级 token 限制并重试；第二步，注入 resume 消息引导模型继续；第三步，才向用户暴露错误。整个恢复流程对用户透明。最多重试 3 次（`MAX_OUTPUT_TOKENS_RECOVERY_LIMIT = 3`），中间错误消息被"扣留"（`isWithheldMaxOutputTokens`），防止 SDK 消费方过早终止会话。

---

## Part 4 · 工具系统：Fail-Closed 是一种信仰

### 为什么不是 Fail-Open

腾讯文章在工具系统上着墨最多，因为这是整个 Harness 哲学最集中的体现。文章写道："Fail-Closed 不是一个理念，是一种信仰。"

传统的 API 设计中，一个工具如果忘了声明权限限制，默认行为是"允许"（Fail-Open）。这在大多数场景下是合理的——开发者体验好，不需要写太多声明。但在 AI Agent 场景下，这种默认行为是灾难性的。因为 Agent 会探索人类开发者不会触及的边界——它会尝试读取 `/etc/shadow`，会尝试执行 `rm -rf /`，会尝试在 `curl` 输出中注入 prompt injection。

`buildTool()` 工厂的默认值是这个信仰的代码化：

```typescript
const TOOL_DEFAULTS = {
  isEnabled: () => true,
  isConcurrencySafe: (_input?) => false,    // 默认不可并发——最保守
  isReadOnly: (_input?) => false,           // 默认非只读——需要显式声明才能被优化
  isDestructive: (_input?) => false,        // 默认非破坏性——权限检查仍走完整流程
  checkPermissions: (input, _ctx?) =>
    Promise.resolve({ behavior: 'allow', updatedInput: input }),
  toAutoClassifierInput: (_input?) => '',   // 安全敏感工具必须显式覆写
  userFacingName: (_input?) => '',
}
```

注意这里的精妙之处：`checkPermissions` 默认返回 `allow`，这看似 Fail-Open，实际上是将决策**委托**给外层的五层纵深防御系统——工具自身的权限检查只是第一层，后面还有路径保护、语义分析、分类器和人工确认。`toAutoClassifierInput` 默认返回空字符串，意味着安全分类器默认忽略此工具；安全敏感的工具（如 BashTool）必须显式覆写，向分类器提供有意义的输入。忘了覆写？分类器不参与决策，走完整的人工确认流程。

忘了设置？走最受限路径。遗漏不是漏洞，而是额外的安全层。

### Tool 接口：50+ 个字段的"过度设计"

`Tool<Input, Output, Progress>` 接口有 50+ 个字段，这看起来是过度设计。但每个字段都有明确的工程理由：

`interruptBehavior()` 返回 `'cancel'` 或 `'block'`——用户按 Ctrl+C 时，BashTool 应该取消（cancel），但 FileEditTool 应该阻塞等待（block）以避免写出半成品文件。

`toAutoClassifierInput()` 为自动模式分类器提供标准化输入——不是每个工具都需要用户确认，分类器可以根据工具的"危险程度"自动决策。

`backfillObservableInput()` 在不修改原始 API 输入的情况下回填可观测字段——这是为了保护 prompt cache：如果修改了发送给模型的 tool input，cache 就失效了。

`isMcp` 和 `inputJSONSchema` 让 MCP 工具成为一等公民——MCP 工具可以直接指定 JSON Schema 而非从 Zod 转换，避免了 schema 丢失。

### StreamingToolExecutor：并发的精确控制

工具并发执行不是简单的"全部并行"。`StreamingToolExecutor` 实现了一套精密的并发控制算法：并发安全工具（Glob、Grep、FileRead）可以彼此并行执行；非并发安全工具（Bash、FileEdit）必须独占执行；当 Bash 出错时，取消同批次的兄弟工具，但不终止父级 query 循环。

这种"错误隔离但不传播"的策略是一种工程权衡：一个工具失败不应该杀死整个对话，但应该阻止后续依赖该结果的步骤。

### 缓存稳定性：一个容易被忽视的细节

`assembleToolPool()` 在合并内置工具和 MCP 工具时，**不能**全局排序——必须分别排序后拼接（内置作为前缀），再用 `uniqBy('name')` 去重。原因极其微妙：全局排序会交错 MCP 工具到内置工具之间，导致服务端 `claude_code_system_cache_policy` 的缓存断点位置变化，所有下游缓存 key 失效。这种对缓存稳定性的关注，是工业级工程与 Demo 级工程的分水岭。

---

## Part 5 · 多 Agent 编排：控制面与数据面的分离

### 七种任务类型

系统定义了 7 种任务类型，每种有独特的 ID 前缀（`b`=bash, `a`=agent, `r`=remote, `t`=teammate, `w`=workflow, `m`=monitor, `d`=dream）。ID 使用 `randomBytes(8)` + 36 字符表生成，产生 `36^8 = 2.8 万亿`组合。注释明确说明这是为了"抵抗暴力符号链接攻击"。

### AgentTool：进程级隔离

AgentTool 生成子 Agent 时，每个子 Agent 拥有独立的上下文和工具白名单。这是"上下文隔离"支柱的核心实现。文章用了一个精妙的类比："就像 Unix 进程隔离——每个 Agent 有自己的地址空间，通信必须通过结构化消息接口。"

在 Coordinator 模式下，这种隔离更进一步：控制面（Coordinator）负责决策和任务分配，数据面（Worker Agent）负责具体执行。控制面看到的上下文是全局的，数据面看到的上下文是被裁剪的。

### DreamTask：让 AI 做梦

这是整个项目中最具想象力的设计之一。DreamTask 在后台自主运行，不需要用户触发，目的是整合和沉淀跨会话的知识。腾讯文章将其与人类 REM 睡眠的记忆巩固机制类比，而 AutoDream 的四阶段实现确实呼应了这种认知科学启发：

**Phase 1 · Orient（定位）** 读取记忆索引，了解当前知识结构的全貌。

**Phase 2 · Gather（收集）** 收集近期会话中的新知识和新经验。

**Phase 3 · Consolidate（整合）** 将新旧知识融合，更新记忆文件。

**Phase 4 · Prune & Index（修剪与重建索引）** 删除冗余内容，重建索引。

为什么要在一个严肃的工程工具中实现"做梦"？因为这解决了一个真实的工程问题：随着使用时间增长，Agent 的记忆会碎片化、重复化、过时化。手动整理不可行（用户不会做），自动整理需要认知能力（只有 LLM 能做）。让 Agent 在空闲时"做梦"整理记忆，是把问题从用户转移到系统的最优解。

---

## Part 6 · 终端 UI：用 React 写 CLI 的反直觉选择

### 为什么是 React + Ink

用 React 写终端 UI，这本身就是一个反直觉的选择。React 是为浏览器设计的，Ink 是 React 的终端渲染器。团队为什么不直接用 Blessed 或 Terminal Kit 这些原生终端库？

腾讯文章引用了团队的设计考量："React 的组件化和声明式 UI 确实适合构建复杂的交互界面……团队需要对渲染层有完全的控制权。" "完全的控制权"是关键——他们不仅使用 Ink，还 fork 了一个 246KB 的自定义渲染引擎，而不是直接使用 npm 包。这意味着他们对渲染性能的每一个环节都有精细的控制。

这种选择的代价是 `REPL.tsx` 单文件达到了惊人的 875KB。Hacker News 上一位评论者的名言被腾讯文章引用："这不是代码，这是一部长篇小说。" 但在工业级工程中，一个文件的大小不是衡量代码质量的标准——**它解决的问题的复杂度才是**。

### 34 行 Store：你可能不需要 Redux

整个应用的状态管理核心是一个 34 行的极简 Store，基于 `useSyncExternalStore` 实现 Observer 模式。腾讯文章对此评价："该项目用 34 行代码证明了：你可能不需要 Redux。"

这不是炫技。Redux 的启动开销对于一个追求 200ms 冷启动的 CLI 应用是不可接受的。34 行 Store 配合不可变约束（`DeepImmutable<>` 泛型）确保了类型安全，同时避免了 Redux 的中间件链、action creator、reducer 组合等仪式性代码。

AppState 结构包含 100+ 个状态字段，全部由这个极简 Store 管理。这证明了状态管理的复杂度不在框架，而在状态本身的设计。

### Vim 模式：对程序员的尊重

Claude Code 内置了完整的 Vim 模式实现（7 个文件，50.2KB 的 deep-dive 分析），包含 NORMAL/INSERT 模式切换、操作符（delete/change/yank）、运动命令、文本对象、查找运动（f/F/t/T）、点重复、寄存器管理。

这不是一个"nice to have"。对于 Vim 用户来说，失去 Vim 键绑定等于生产力减半。在一个以程序员为目标用户的 CLI 工具中，Vim 支持不是锦上添花，而是基础设施。

---

## Part 7 · 安全与权限：五层纵深防御

### 权限决策的 10 步管线

从工具调用到最终执行，权限决策经过 10 个步骤。腾讯文章将其描述为"五层纵深防御体系"：

**第一层：静态规则**。检查 blanket allow/deny 规则和 per-tool 规则。这些规则在配置文件中预定义，不需要运行时计算。

**第二层：路径保护**。检查敏感路径（`.env`、`credentials.json`、`~/.ssh/`），对这些路径的读写操作强制额外确认。

**第三层：命令语义分析**。BashTool 分析命令中的管道、重定向、危险模式（`curl | bash`、`wget | sh`、`rm -rf`），结合 deny 规则做精细判断。

**第四层：Auto-Mode 分类器**。两阶段 XML 分类器——第一阶段 Fast（64 tokens 限制）做快速判断，如果不确定则进入第二阶段 Thinking（4096 tokens）深度推理。分类器输入包括工具名、参数、当前上下文快照。

**第五层：人工确认**。弹出交互式权限请求让用户决定。

### Denial Tracking 与熔断

权限拒绝追踪使用装饰器模式：`wrappedCanUseTool` 包裹原始 `canUseTool`，透明地记录所有被拒绝的工具调用。连续 3 次拒绝或累计 20 次拒绝触发熔断机制。

为什么需要熔断？因为 Agent 在权限被拒后可能陷入"死磕"模式——不断变换参数重试同一个操作。熔断不是惩罚 Agent，而是保护用户体验：如果模型连续 3 次被拒绝，说明它对当前任务的意图和用户的期望不匹配，应该停下来重新理解。

---

## Part 8 · Hooks 系统：开放内核的拦截架构

### 27 种事件类型，6 种 Hook 命令

如果说工具系统是 Agent 的"手"，那 Hooks 系统就是 Agent 的"神经系统"——它允许在工具执行的每个关键节点注入自定义逻辑，而不修改核心循环。

Claude Code 定义了 27 种 Hook 事件类型，覆盖 Agent 的完整生命周期：PreToolUse（工具执行前）、PostToolUse（工具执行后）、PrePermission（权限请求前）、Notification（通知时）、UserPrompt（用户输入时）等。每个事件都可以被用户通过配置文件拦截。

Hook 命令支持 6 种类型：Command（执行命令）、Prompt（注入 prompt）、Agent（启动子 Agent）、HTTP（发送 HTTP 请求）、Callback（回调函数）、Function（执行函数）。注册来自 8 个来源，按优先级排列。

### 为什么这是"可拆解性"支柱的体现

这解决了可扩展性的核心矛盾：核心循环必须稳定不可修改，但用户又需要定制化能力。Hooks 的解法是"开放内核"——核心循环不可触碰，但 27 个拦截点允许注入逻辑。这类似于操作系统的系统调用表：你不能修改内核代码，但可以通过注册系统调用处理器来扩展功能。

PreToolUse Hook 尤其强大——它可以在工具执行前修改输入、拒绝执行、甚至替换为另一个工具。这意味着用户可以通过配置文件实现"禁止在周末执行 `git push`"这样的策略，而不需要修改 Claude Code 的任何代码。

每个 Hook 在独立的超时控制下并行执行，一个 Hook 失败不会影响其他 Hook 或核心循环。这是"错误隔离但不传播"原则在 Hook 层面的应用。

---

## Part 9 · 会话持久化与容错：永不丢失工作

### 崩溃恢复的产品哲学

`sessionRestore.ts` 和 `filePersistence.ts` 实现了跨进程崩溃的会话恢复。这背后的产品哲学是"永不丢失工作"——如果 Claude Code 因为网络断开、进程被杀、或系统崩溃而中断，用户下次启动时应该能从断点继续，而不是重新开始。

会话持久化的精细控制值得关注：assistant 消息使用 `void recordTranscript()`（fire-and-forget，不阻塞生成器），user/compact 消息使用 `await recordTranscript()`。注释详细解释了原因：阻塞会妨碍 message_delta 处理。这种"写入不等"的设计保证了流式输出的实时性，同时确保关键消息（用户输入、压缩边界）被可靠持久化。

### API 重试：渐进式降级的容错哲学

`withRetry.ts` 实现了 API 调用的重试策略，体现了一种"不轻易放弃，但也不无限重试"的工程平衡。指数退避从短间隔起步，对特定错误码（如 529 服务端过载）有专门的处理逻辑，持久重试但最终会超时。这种渐进式降级确保了在网络抖动时用户体验不中断，在服务端真正不可用时及时告知用户。

---

## Part 10 · 命令与技能：Markdown 是最佳扩展模式

### 三种命令类型与 7 级来源层次

命令系统支持三种类型：PromptCommand（转化为 prompt 发给模型）、LocalCommand（本地执行逻辑）、LocalJSXCommand（渲染交互式 UI）。命令来自 7 个层次：bundled → builtin plugin → skill directory → workflow → plugin → plugin skills → built-in。

### Skills = Markdown：非程序员也能扩展

腾讯文章将 "Skills = Markdown" 列为方法论的第 9 条："Markdown 是最佳扩展模式。" 技能文件使用 Markdown + frontmatter 格式，一个技能就是一个 `.md` 文件：

```yaml
---
name: my-skill
description: 做什么
when_to_use: 什么时候触发
allowed-tools: Bash, FileRead
model: claude-sonnet-4-20250514
effort: high
---
这里是发给模型的 prompt 内容...
```

为什么是 Markdown 而非 JSON/YAML/TOML？因为技能本质上是"有结构的自然语言"。Markdown 让人类可读可写，frontmatter 提供结构化元数据，正文是自由的自然语言。这是"可拆解性"支柱的体现——技能的定义不需要编译、不需要 SDK、不需要理解 TypeScript，只需要一个文本编辑器。

内置技能有 14 个，涵盖了日常开发的典型场景：`batch`（批量操作）、`debug`（调试）、`loop`（循环执行）、`remember`（记忆管理）、`simplify`（简化代码）、`verify`（验证结果）等。

---

## Part 11 · MCP 与 Bridge：开放性的工程化

### MCP：8 种传输方式的包容性

MCP（Model Context Protocol）支持与外部工具集成，提供 8 种传输方式：stdio、SSE、sse-ide、HTTP、WebSocket、ws-ide、SDK、claudeai-proxy。这种"传输无关"的设计让 MCP 可以适配从本地进程到 IDE 插件到云端服务的各种场景。

OAuth 2.1 完整流程包括 PKCE、DCR（Dynamic Client Registration）、Token Refresh、XAA（外部访问授权）。Elicitation 协议支持 Form 和 URL 两种模式，让 MCP 服务器能向用户请求额外信息。多作用域配置合并覆盖 6 个作用域，按优先级合并。

### Bridge：让手机也能操控本地 CLI

Bridge 系统（`bridgeMain.ts` 单文件 113KB）实现本地 CLI 与 claude.ai 网页端的双向通信。这意味着你可以在手机上通过 claude.ai 向本地的 Claude Code 发送任务，等回家后在终端里看到结果。

Worker 生命周期包含完整的指数退避重试（2 秒起步，120 秒上限，10 分钟放弃）、JWT token 刷新调度（使用 generation counter 防止 stale timer）、容量唤醒机制。传输层支持三种模式：CCR v2 SSE（优先）、Hybrid WS+POST、纯 WebSocket。

---

## Part 12 · 彩蛋：过度工程化是一种文化表达

### Buddy 虚拟宠物

藏在严肃工程代码中的，是一个 45KB 的完整虚拟宠物系统。18 个物种、5 个稀有度等级（普通 60% 到传说 1%）、抽卡式概率系统。每个物种有 3 帧 ASCII 动画，idle 序列共 15 帧：73% 概率休息、13% 小动作（两种变体各约 7%）、7% 眨眼。宠物分为 CompanionBones（确定性，可重新生成）和 CompanionSoul（唯一性，持久化存储），使用 Mulberry32 PRNG 和 FNV-1a 哈希。

腾讯文章对此评价："过度工程化是一种文化表达。为年度回顾动画写 554 行代码，为贴纸链接写完整命令——传递信号：我们在乎细节，我们有幽默感。彩蛋分层访问确保不同层次发现惊喜。"

这不是无关紧要的花絮。在 512K 行代码中放入这些彩蛋，传递了一个重要信号：**工程团队对"过度工程化"有自觉意识，并且以此为荣**。这种文化特质直接影响产品质量——当你愿意为动画的 73%/7%/7% 概率分配较真时，你对生产代码中的边界条件也会同样较真。

### /thinkback：个性化年度回顾

`/thinkback` 命令生成个性化的 ASCII 艺术年度回顾，基于用户的实际使用数据。`preventSleep` 使用 macOS `caffeinate` 防止长任务期间系统休眠，采用引用计数 + 定时重启（4 分钟一次，5 分钟超时自毁）的设计。这些"小功能"每个都有完整的工程实现，没有一个是 hack 出来的。

---

## Part 13 · 方法论总结：构建 Harness 的十条原则

腾讯文章在 Part 7 提炼了构建顶级 Harness 的方法论。这里结合源码分析，给出每条原则的工程解释：

**1. 把 95% 的精力放在 Harness 上。** 模型调用只是冰山一角。真正决定用户体验的是错误恢复、权限管理、上下文压缩、启动性能这些"非模型"工程。

**2. Agent Loop 用 AsyncGenerator。** 天然支持流式输出、背压控制和中断。Observable/EventEmitter 的多播能力在 Agent 场景下是多余的复杂度。

**3. 工具系统 Fail-Closed。** 默认走最受限路径。遗漏不是漏洞。这是"悲观默认"原则在 AI Agent 场景下的极致应用。

**4. 权限模型分层纵深。** 静态规则 → 路径保护 → 语义分析 → 分类器 → 人工确认。任何单层失效不会导致系统沦陷。

**5. 上下文压缩用渐进管道。** 从轻到重：Snip → Micro → Collapse → Auto。先用最便宜的方法尝试，只在必要时付出最高成本。

**6. 配置快照 > 实时读取。** `QueryConfig` 在查询入口做不可变快照，确保整个迭代过程中的配置一致性。实时读取会引入竞态条件。

**7. 上下文隔离用结构化消息。** 多 Agent 通信必须通过结构化接口，禁止共享内存。这是分布式系统的基本功，在 Agent 场景下同样适用。

**8. 熵治理要自动化。** 不要期望用户手动整理记忆。AutoDream 的四阶段整合是"系统自维护"理念的体现。

**9. Skills = Markdown 是最佳扩展模式。** 让人类可读可写，让非程序员也能扩展。这是"可拆解性"支柱的实用化落地。

**10. 测试用依赖注入而非 mock patch。** `QueryDeps` 通过构造函数注入所有外部依赖，让核心循环可以在不启动网络、不读取文件系统的情况下被测试。

---

## Part 14 · 反直觉设计决策清单

这份源码中有大量反直觉的设计选择，每一个都经过了深思熟虑：

**用 React 写终端 UI**——代价是 875KB 的单文件，收益是组件化和声明式开发的开发体验。

**34 行 Store 替代 Redux**——在 512K 行代码中，状态管理的核心只有 34 行。Redux 的启动开销对 200ms 冷启动目标不可接受。

**内置而非依赖 Ink 渲染引擎**——fork 了 246KB 的自定义渲染引擎，因为需要对渲染层有完全控制权。

**让 AI "做梦"**——投入大量工程资源实现后台记忆整合，灵感来自人类 REM 睡眠。这不是技术炫技，而是解决记忆碎片化的最优解。

**为彩蛋"过度工程化"**——554 行代码做年度回顾动画、45KB 实现虚拟宠物。传递"我们在乎细节"的文化信号。

**编译时特性开关消除死代码**——89 个 Feature Flag，未启用的特性从二进制中完全消失。比 Tree-shaking 更彻底的消除。

**query() 循环 16 步只有 1 步调用模型**——Agent 工程最反直觉的真相：模型调用是最简单的部分。

**不能全局排序工具列表**——为了维护 prompt cache 稳定性，内置工具和 MCP 工具必须分区排序。

---

## Part 15 · 学习路线建议

### 哲学优先的阅读顺序

建议按照"为什么 → 是什么 → 怎么做"的顺序阅读，而非反过来。

**入门阶段**：先读腾讯文章原文建立整体认知，然后阅读 `docs/architecture/01-overview.md` 建立全局视图。重点理解"Agent = Model + Harness"这个公式，以及为什么 95% 的代码不是模型逻辑。

**核心理解阶段**：阅读 `02-query-engine.md`，对照源码 `QueryEngine.ts` 和 `query.ts`。重点关注 `queryLoop()` 的 16 步循环——数一下哪 1 步在调用模型，哪 15 步在做基础设施工作。然后阅读 `03-tool-system.md`，理解 Fail-Closed 安全模型的每一个默认值。

**深度阶段**：阅读 `deep-dive/memory-system.md` 理解 AutoDream 的四阶段设计，思考"熵治理"在 Agent 系统中的必要性。阅读 `deep-dive/bridge-system.md` 理解分布式通信的工程化。阅读 `deep-dive/buddy-system.md` 思考为什么严肃工程中需要"有温度"的设计。

**方法论阶段**：重读腾讯文章的方法论部分，对照本文的 Part 13 逐条验证。然后选择你自己正在构建的 Agent 项目，用这 10 条原则做一次 audit。

### 关键文件速查

| 文件 | 行数 | 为什么重要 |
|------|------|-----------|
| `query.ts` | 1,729 | 16 步 Agentic Loop 的核心实现，理解 Agent 工程的必读 |
| `QueryEngine.ts` | 1,295 | 对话生命周期管理，理解 AsyncGenerator 事件流模式 |
| `Tool.ts` | 792 | Fail-Closed 安全模型的类型基础，50+ 字段的工具接口 |
| `commands.ts` | 754 | 7 级命令源层次和 Memoization 缓存策略 |
| `tools.ts` | 389 | 工具组装工厂，缓存稳定性设计的典范 |
| `setup.ts` | 477 | 启动管线的操作顺序和并行预取策略 |
| `query.ts` 中的 queryLoop | ~800 | 16 步循环的核心，只有 ~50 行在调用模型 |
| `Tool.ts` 中的 TOOL_DEFAULTS | ~20 | Fail-Closed 哲学的代码化，20 行代码定义了整个安全基线 |
| `services/compact/` | 11 文件 | 四层上下文压缩的完整实现 |
| `bridge/bridgeMain.ts` | ~3,000 | 分布式通信的指数退避和 JWT 刷新调度 |

---

## 结语：这不只是一个产品

回到腾讯文章的结论："这不是一个'应用了 Harness Engineering 理念的项目'，而是这个理念最完整的工业级实现。"

当你读完这份源码，你会发现它最打动人的不是任何一个技术模块的精巧——虽然每个模块都很精巧——而是贯穿始终的**工程一致性**。从 34 行 Store 到 89 个 Feature Flag，从 Fail-Closed 默认值到 AutoDream 梦境系统，从 Buddy 宠物的 73%/7%/7% 概率分配到工具列表的缓存稳定性，每一个决策都指向同一套价值观：**确定性优于灵活性，安全优于便利，正确性优于速度，对细节的执着优于"够用了"的妥协**。

这是学习这份源码最大的收获——不是学到了某个具体的技术方案，而是看到了一种工程品味是如何在 512K 行代码中保持一致的。

---

> 本文档基于 CC学习 文件夹中 37 篇架构文档（约 1.01MB 文本）和完整源码分析生成，深度结合腾讯技术工程文章《顶级开发团队设计的 Harness 工程项目源码什么样》的产品哲学分析。所有源码引用均指向实际文件，所有行数数据经过 `wc -l` 验证。
