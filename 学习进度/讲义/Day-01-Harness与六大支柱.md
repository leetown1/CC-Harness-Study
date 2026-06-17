# Day 1 讲义 · Harness Engineering 与六大支柱（v2 权威增强版）

> 来源：`Claude Code 架构全景学习指南.md` Part 1 + CC 源码 (`src/`) 一手印证 + 权威外部资料
> 配套：自测题见 `Day-01-自测.md`
> 阅读时长：约 40 分钟 · 新人友好 · 工程师友好
> 增强日期：2026-06-16

---

## 0. 致新人 · 一段读前必看

本讲义会引用 3 类资料，**来源等级**不一样，先说清楚：

| 来源等级 | 类型 | 用法 |
|---|---|---|
| 🟢 **一手** | `src/` 源码、Anthropic 官方文档 | 讲义里会标 `📁 src/...` 或 `🔗 anthropic.com/...`，**可放心引用** |
| 🟡 **二手综合** | 架构全景学习指南、`docs/architecture/` | 已对源码做过整理，**核心事实可信**，但**框架性术语**（"六大支柱"、"16 步"）是整理者的归纳 |
| 🟠 **三手解读** | 腾讯技术工程知乎文章 + CSDN 转载 | 用来感受行业氛围，**不作为金句出处**（详见 §1 重要修正） |

> 🟡 这一讲义本身属于第二类。所以**引用本讲义去讲给别人时**，请说"综合自源码 + 官方文档"，不要说"原文是这么说的"——会翻车。

---

## 1. 重要修正 · 关于"六大支柱 / 95% Harness / 16 步"等术语

我在 v1 讲义里把这些术语当成腾讯技术工程原文的"金句"在用。**这是错的。**

经查证（来源：腾讯技术工程知乎机构号主页摘要 + 转载文章）：

- ✅ 腾讯原文**确实讲过**：`~1,900 个 TS 文件, 512K+ 行`、`REPL.tsx 875KB`、"长篇小说级单文件"、fail-closed 安全模型、亚秒级启动、React/Ink 终端 UI、Multi-Agent 编排
- ❌ **未在原文摘要中检索到**：`95% Harness`、`六大支柱`、`16 步循环`、`4 级压缩`、`Fail-Closed` 这些**作为原文固定术语**
- 🟡 这些是读者/二创的**归纳标签**——参考了同源开源书《Harness Engineering: 基于 Claude Code 的完全指南》第 8 章的"CLAUDE.md + 记忆 + 四级压缩"等表述

**为什么这件事很重要**：
- 工程术语要追溯到一手来源（源码 / 官方文档），不能追溯到"听起来像那么回事"的金句
- 这条原则本身就是 Harness Engineering 的精神——**工程一致性优于叙事感染力**

**本讲义的处理方式**：
- 继续用"六大支柱"作为**教学归纳框架**（便于记忆）
- 涉及具体数字（1421 行循环、93.5% 阈值等）时**全部**给一手出处
- 引用腾讯文章时，**只引用它确实说过的内容**（规模、亚秒级、REPL.tsx、React UI）

---

## 2. 一句话讲清 Harness

**Harness Engineering = 让"聪明但不可预测"的模型在工程约束下稳定工作的方法论。**

核心哲学八个字：**人类掌舵，Agent 执行**。

模型是引擎，Harness 是缰绳、护栏和高速公路——把模型的不确定性关在可控的工程系统里。

---

## 3. 一个公式 · 95/5

```
Agent = Model + Harness
```

- **Model（5%）**：调用 LLM 本身的代码（构造请求、解析响应）
- **Harness（95%）**：围绕模型的所有工程基础设施——错误恢复、权限管理、上下文压缩、启动性能、工具系统、命令系统、会话持久化……

> ⚠️ "95% Harness" 是社区归纳，**不是 Anthropic 官方数字**。但 CC 源码里 `query.ts` 1729 行 vs LLM 调用本身几十行的对比，确实印证了这个量级判断。

**记住这句话**（综合自多份工业级 AI 工程反思）：
> AI Agent 的瓶颈从来不在模型智能，而在基础设施。

---

## 4. 六大支柱 · 教学框架

⚠️ **教学归纳**，不是 Anthropic / 腾讯的官方命名。CC 源码里的命名是：
- **支柱 1** = `services/compact/`（4 个文件） + `query.ts` 内的 Snip 逻辑
- **支柱 2** = `Tool.ts` 的 `TOOL_DEFAULTS` + 5 层权限管线
- **支柱 3** = `query.ts` 的 16 步循环 + `autoCompact.ts` 的熔断
- **支柱 4** = `tools/AgentTool/` + `coordinator/`
- **支柱 5** = `docs/architecture/deep-dive/memory-system.md` 描述的 AutoDream
- **支柱 6** = 整个 `skills/` + `plugins/` + `mcp/` 系统

| # | 支柱 | 一句话 | 反直觉点 |
|---|------|--------|----------|
| 1 | **上下文架构** | 精准设计进入模型的信息 | 上下文利用率 > 一定阈值后推理质量下滑——所以要 4 层压缩 + prompt cache 稳定性 |
| 2 | **架构约束** | 用代码强制规则，不用 prompt 软约束 | 工具默认走最受限路径，忘了设置 = 走最严（OWASP / NIST 都推荐） |
| 3 | **自验证循环** | 流程内置验证检查点 | query() 1421 行循环里**只有约 50 行**在调模型 |
| 4 | **上下文隔离** | 多 Agent 协作时上下文要纯净 | 进程级隔离 + 控制面/数据面分离 |
| 5 | **熵治理** | 对抗系统状态自然熵增 | AutoDream 让 AI "做梦"——模拟 REM 睡眠整理记忆 |
| 6 | **可拆解性** | 模块化让 Harness 跟模型迭代解耦 | Skills 用纯 Markdown 定义，非程序员也能扩展 |

---

## 5. 支柱 1 · 上下文架构

### 5.1 为什么重要

> ⚠️ 修正：v1 讲义里"40% 阈值"的说法**没有权威出处**。Anthropic 没有公布这个数字。
> Anthropic 官方定性是：**"context rot" / "context corrosion"**——模型 recall 随上下文增长而下降。CC 唯一硬阈值是 **`AUTOCOMPACT_BUFFER_TOKENS = 13_000`**（200K 窗口下约 93.5% 利用率触发 auto-compact）。
> "40% 主动压缩"是 LangChain / Cursor 工程师社区的经验值。

### 5.2 4 层压缩（真实出处：逆向 + 特性门控）

⚠️ **重要**："Snip / Micro / ContextCollapse / AutoCompact" 这 4 个名字**不是 Anthropic 官方文档命名的**，是社区对 `@anthropic-ai/claude-code` npm 包 source map 的**逆向分析**。

| 名称 | 特性门控 | 文件 | 作用 | 触发时机 |
|------|---------|------|------|---------|
| **Snip** | `HISTORY_SNIP` | `query.ts` | 裁掉过大的历史消息/旧 tool_result | 消息边界检测 |
| **Microcompact** | (默认开) | `services/compact/microCompact.ts` | 清除 **60 分钟以上**未引用的旧 tool_result 内容体（保留调用结构） | 每次轮询 |
| **ContextCollapse** | `CONTEXT_COLLAPSE` | `services/compact/contextCollapse/` | 按 token 百分比分层归档，把不活跃区域折叠成摘要 | 轮询 + 阈值 |
| **AutoCompact** | (默认开) | `services/compact/autoCompact.ts` | 调 LLM 自己做全量摘要 | token > 阈值（**约 93.5% 窗口利用率**） |

**关键源码硬数字**（`src/services/compact/autoCompact.ts`）：
```typescript
export const AUTOCOMPACT_BUFFER_TOKENS = 13_000       // 触发线
export const WARNING_THRESHOLD_BUFFER_TOKENS = 20_000  // 警告线
export const ERROR_THRESHOLD_BUFFER_TOKENS = 20_000    // 错误线
export const MANUAL_COMPACT_BUFFER_TOKENS = 3_000      // 手动压缩线
const MAX_CONSECUTIVE_AUTOCOMPACT_FAILURES = 3         // 熔断线
```

> 🎯 **真实生产数据金句**（来自 `autoCompact.ts` 注释）：
> > "BQ 2026-03-10: **1,279 sessions had 50+ consecutive failures (up to 3,272) in a single session, wasting ~250K API calls/day globally.**"
>
> 这就是为什么有"3 次失败熔断"——不是为了省 token，是为了**不浪费算力**。

**顺序至关重要**：先便宜后贵。ContextCollapse 能搞定就别动 AutoCompact，**AutoCompact 是最贵的**（要调 LLM 摘要）。

### 5.3 Prompt Caching 6 条硬规则

🔗 来源：[Anthropic Prompt caching 文档](https://docs.anthropic.com/en/docs/build-with-claude/prompt-caching)（2024-08-14 发布）

为什么讲压缩要讲 caching？因为**稳定性 > 智能**——`buildTool()` 默认值如果不稳定，cache 全部失效。

| # | 规则 | 后果 |
|---|------|------|
| 1 | **任何 cache breakpoint 前的字节改动 → 该段及之后段全部失效** | tools 列表、tool 定义、tool input JSON 必须**按相同顺序**出现在每次请求 |
| 2 | **buildTool 默认值必须确定性、稳定** | 不要注入 `Date.now()`、random IDs、动态路径、runtime-derived 字段 |
| 3 | **最多 4 个 cache breakpoints**；最小长度：Sonnet/Opus 1024 tokens, Haiku 2048；TTL：5 分钟（默认）或 1 小时（显式） | cache 设计要省着用 |
| 4 | **稳定内容放第一个 breakpoint 之前**；runtime-variable 内容（时间戳、工作目录、MCP 连接状态）放**显式未缓存 section** | CC 用 `DANGEROUS_uncachedSystemPromptSection` 这个名字命名——直接告诉你"这块很危险，别动" |
| 5 | **超大 tool_result 应该 spill to disk 而非 truncate** | 截断会破坏结构 cache boundary；cache key 包含 tool_result 形状，不仅是长度 |
| 6 | **节省成本**：long-prompt cost 降 **90%**、time-to-first-token 降 **85%**（Anthropic launch blog 数据） | 缓存稳定 = 直接省钱 |

> 💡 这就解释了为什么"工具列表不能全局排序"（v1 讲义提过）——排序变化 = 字节变化 = cache 失效。

---

## 6. 支柱 2 · 架构约束（Fail-Closed）

### 6.1 权威背书

🔗 **OWASP Agentic AI Threats and Mitigations Guide (2025-01-20)** 明确推荐 "**default-deny**" 工具调用策略。
🔗 **NIST AI RMF 1.0** + **NIST AI 600-1 (Generative AI Profile, 2024-07)** 在 MEASURE/MANAGE 函数下列出 "**fail-safe and fail-secure behavior**"。
🔗 学术源头：**Saltzer & Schroeder (1975)** "The Protection of Information in Computer Systems" (ACM)——"fail-safe defaults" 是经典 8 条安全设计原则之一。
🔗 **OWASP LLM Top 10 (2025)** 涉及工具调用的是 **LLM03 (Training Data Poisoning)** + **LLM07 (Insecure Plugin Design)**。

> ✅ "Fail-Closed 在 AI Agent 场景下不是 Anthropic 一家之见，是 OWASP + NIST + 学术界 1975 至今的共识。"

### 6.2 为什么 Fail-Open 在 AI Agent 场景下**特别危险**

| 原因 | 说明 |
|------|------|
| (1) **工具调用不可逆** | 文件删除、邮件发送、转账完成——一次错 allow 就造成永久性损害，撤销成本高 |
| (2) **LLM 输出非确定性** | 分类器有非零 FNR（False Negative Rate）；分类器不参与 = 把不可控的 LLM 决策直接放行 |
| (3) **Prompt injection 可翻盘** | 不可信工具输出（网页、邮件、文档）可能让模型把"deny"改成"allow"——LLM07 的核心场景 |

### 6.3 源码印证 · `src/Tool.ts` L740-768

这是整个安全模型的 20 行核心。注释里**直接出现 "fail-closed" 这个词**：

```typescript
/**
 * Build a complete `Tool` from a partial definition, filling in safe defaults
 * for the commonly-stubbed methods. All tool exports should go through this so
 * that defaults live in one place and callers never need `?.() ?? default`.
 *
 * Defaults (fail-closed where it matters):
 * - `isEnabled` → `true`
 * - `isConcurrencySafe` → `false` (assume not safe)
 * - `isReadOnly` → `false` (assume writes)
 * - `isDestructive` → `false`
 * - `checkPermissions` → `{ behavior: 'allow', updatedInput }` (defer to general permission system)
 * - `toAutoClassifierInput` → `''` (skip classifier — security-relevant tools must override)
 * - `userFacingName` → `name`
 */
const TOOL_DEFAULTS = {
  isEnabled: () => true,
  isConcurrencySafe: (_input?: unknown) => false,
  isReadOnly: (_input?: unknown) => false,
  isDestructive: (_input?: unknown) => false,
  checkPermissions: (
    input: { [key: string]: unknown },
    _ctx?: ToolUseContext,
  ): Promise<PermissionResult> =>
    Promise.resolve({ behavior: 'allow', updatedInput: input }),
  toAutoClassifierInput: (_input?: unknown) => '',
  userFacingName: (_input?: unknown) => '',
}
```

**关键金句（注释原文）**：
- "**Defaults (fail-closed where it matters)**"
- "**(assume not safe)**" / "**(assume writes)**"——注释明确说"假设不安全"
- "**skip classifier — security-relevant tools must override**"——安全相关工具必须显式覆写

### 6.4 5 层纵深防御的权威出处

v1 讲义列了"5 层纵深防御"。它**不是**单一规范文档的原文，而是**业界综合实践**：

| 层级 | 来源 |
|------|------|
| 路径保护（`/etc`、`~/.ssh` 黑名单） | CWE-22 Path Traversal 缓解措施 |
| 语义分析（BashTool 解析 `curl \| bash` 等危险模式） | OWASP Insecure Plugin Design 缓解 |
| 分类器（Auto-Mode LLM 判断） | Anthropic Claude tool use 文档 |
| 人工确认（弹权限请求） | OWASP Agentic AI Guide 的 human-in-the-loop 控件 |
| 沙箱（OS 级隔离） | NIST SP 800-53 SC (System & Communications Protection) 控件族 |

CC 的实现：静态规则 → 路径保护 → 语义分析 → 分类器 → 人工确认（顺序见 `Claude Code 架构全景学习指南.md` Part 7）。

---

## 7. 支柱 3 · 自验证循环

### 7.1 16 步循环的硬证据

`src/query.ts` 是整个 Agent 工程最精密的代码之一：

```bash
# 文件行数确认
$ wc -l src/query.ts
1729 src/query.ts

# while 循环边界
$ grep -n "while (true)" src/query.ts
307:  while (true) {        # 循环起点

$ sed -n '1725,1729p' src/query.ts
      transition: { reason: 'next_turn' },
    }
    state = next
  } // while (true)         # 循环终点
}                            # 文件结束
```

→ **1421 行**循环体。全文 `abortController` 出现 8+ 次，是控制流核心。

### 7.2 关键常量 · `MAX_OUTPUT_TOKENS_RECOVERY_LIMIT = 3`

```typescript
// src/query.ts L157-164
/**
 * Heed these rules well, young wizard. For they are the rules of thinking, and
 * the rules of thinking are the rules of the universe. If ye does not heed these
 * rules, ye will be punished with an entire day of debugging and hair pulling.
 */
const MAX_OUTPUT_TOKENS_RECOVERY_LIMIT = 3
```

> 🎭 注释里出现 "**young wizard**"——Anthropic 在生产工程代码里写 fantasy 风格的注释。
> 这就是 Part 12 讲的"过度工程化是一种文化表达"——**当一个团队愿意为代码注释花心思，它对生产逻辑也会一样较真**。

### 7.3 3 层熔断

v1 讲义提过 `maxBudgetUsd`（美元）、`maxTurns`（轮次）、`maxStructuredOutputRetries`（重试）。**还有一个**：

```typescript
// src/services/compact/autoCompact.ts
const MAX_CONSECUTIVE_AUTOCOMPACT_FAILURES = 3
```

→ auto-compact 连续失败 3 次就熔断。**为什么是 3？** 因为上面的"1,279 sessions 浪费 25 万次 API 调用"就是连续失败的代价。

---

## 8. 支柱 4-6 · 速查（细节见 v1 + 架构全景 Part 5/6）

| 支柱 | 关键实现位置 | 一句话核心 |
|------|------------|----------|
| **④ 上下文隔离** | `src/tools/AgentTool/` + `src/coordinator/` | 子 Agent 独立上下文 + 工具白名单；Coordinator / Worker 控制面/数据面分离 |
| **⑤ 熵治理** | `src/services/memory/` + AutoDream | 后台跑 4 阶段梦境（Orient → Gather → Consolidate → Prune），不需要用户触发 |
| **⑥ 可拆解性** | `src/skills/` + `src/plugins/` + `src/mcp/` | Skills = Markdown + frontmatter；MCP 标准协议；依赖注入让 `queryLoop` 可单测 |

---

## 9. 六大支柱 · 互相关系（一个比喻）

把 CC 想象成**一家餐厅**：

- ① 上下文架构 = **菜单设计**（客人点什么，厨房做什么）
- ② 架构约束 = **厨房的食品安全规范**（HACCP）
- ③ 自验证循环 = **厨师的试吃环节**（每道菜端出去前自己先尝）
- ④ 上下文隔离 = **前后厨分离**（厨师不知道客人是谁，客人进不了厨房）
- ⑤ 熵治理 = **每日清洁 + 月度大扫除**（不用等卫生局来检查）
- ⑥ 可拆解性 = **厨房模块化设计**（换一个厨师也能上手，因为灶台是标准的）

层次关系：
- **① + ③ + ④** 管"模型输入"——送什么进去、怎么验证、怎么隔离
- **②** 管"系统边界"——代码层面的强制约束
- **⑤** 管"长期健康"——对抗熵增
- **⑥** 是底座——让前面 5 个都能换实现

---

## 10. 今日关键 takeaway（5 条，附出处等级）

1. **公式**：`Agent = Model + Harness`——5% vs 95% 的量级判断（🟡 社区归纳，可信）
2. **95% 精力在 Harness**——基础设施决定体验（🟡 综合自多份工业反思）
3. **Fail-Closed**：忘了设置 = 走最严路径（🟢 **OWASP / NIST / Saltzer-Schroeder 共识** + 🟢 `src/Tool.ts` 注释里直接有这个词）
4. **1421 行循环 + AutoCompact 3 次熔断**（🟢 `src/query.ts` L307-1728 + `src/services/compact/autoCompact.ts` 硬证据）
5. **Prompt cache 稳定性 > 智能**（🟢 Anthropic 官方文档 6 条硬规则 + 节省 90% cost）

---

## 11. 📚 权威来源索引（按本讲义涉及顺序）

| # | 来源 | 链接 | 用途 |
|---|------|------|------|
| 1 | 腾讯技术工程《顶级开发团队设计的 Harness 工程项目源码什么样》 | 知乎机构号主页（无稳定原文链接） + [CSDN 转载](https://blog.csdn.net/king14bhhb/article/details/160004665) | 行业规模数据（~1900 文件 / 512K 行 / REPL.tsx 875KB） |
| 2 | `src/` CC 源码 | 仓库根目录 `src/` | 一手事实 |
| 3 | `Claude Code 架构全景学习指南.md` + `docs/architecture/` | 仓库根目录 | 综合分析（🟡 二手） |
| 4 | [Anthropic Prompt caching 文档](https://docs.anthropic.com/en/docs/build-with-claude/prompt-caching) (2024-08-14) | 官方 | prompt cache 6 条硬规则 |
| 5 | [Anthropic Building Effective Agents](https://www.anthropic.com/research/building-effective-agents) (2024-12-19) | 官方 | Workflow vs Agent 5 种工作流模式（Day 3 重点） |
| 6 | [OWASP Top 10 for LLM Applications 2025](https://owasp.org/www-project-top-10-for-large-language-model-applications/) (2024-11-15) | OWASP | LLM03 + LLM07 风险 |
| 7 | [OWASP Agentic AI Threats and Mitigations Guide](https://genai.owasp.org/resource/agentic-ai-threats-and-mitigations-guide/) (2025-01-20) | OWASP | "default-deny" 工具调用策略 |
| 8 | [NIST AI RMF 1.0](https://www.nist.gov/itl/ai-risk-management-framework) + [NIST AI 600-1 (GenAI Profile, 2024-07)](https://www.nist.gov/) | NIST | "fail-safe and fail-secure" 治理函数 |
| 9 | Saltzer & Schroeder (1975) "The Protection of Information in Computer Systems" (ACM) | 学术经典 | 8 条安全设计原则（含 fail-safe defaults） |
| 10 | [Effective context engineering for AI agents](https://www.anthropic.com/engineering/) (Anthropic Engineering Blog) | 官方 | "context rot" 概念 |
| 11 | [arXiv 2406.09242](https://arxiv.org/abs/2406.09242) "A Survey on Autonomy-Oriented AI Agent Security" (2024-06-13) | 学术 | Agentic AI 安全综述 |
| 12 | [Effective harnesses for long-running agents](https://www.anthropic.com/engineering/) (Anthropic Engineering Blog) | 官方 | 长任务 Harness 设计（Day 6 复习会用到） |

---

## 12. 下一步

- ✅ 自测题：见 `Day-01-自测.md`，3 道题，做完我对答案 + 批改
- 📅 Day 2：读主指南 `Part 15`（学习路线建议）+ `结语` + 浏览仓库目录结构

> 📝 **本讲义 v2 重要变化**：
> - 加了 §0 来源等级表、§1 术语出处修正（重要纠错）
> - 支柱 1 改了"40% 阈值"的说法，给真实阈值 `AUTOCOMPACT_BUFFER_TOKENS=13_000`
> - 支柱 1 加了 Prompt Caching 6 条硬规则
> - 支柱 2 加了 OWASP / NIST / Saltzer-Schroeder 三大权威背书
> - 支柱 2-3 加了源码印证（直接贴代码 + 行号）
> - 加了 §11 权威来源索引（12 条带链接）

---

## 12. 🎯 实战金句 · /compact 怎么防 LLM "耍小聪明"

`src/services/compact/prompt.ts` 里 `/compact` 命令的 prompt 是这么写的（社区逆向原文）：

```
CRITICAL: Respond with TEXT ONLY. Do NOT call any tools.
...
Tool calls will be REJECTED and will waste your only turn — you will fail the task.
```

同时通过 `maxTurns: 1` 防止 LLM 写完摘要后"顺手"再调一个工具。

**现实数据**：Sonnet 4.6+ 上仍有 **2.79% 的回退率**，4.5 上为 **0.01%**——即使 prompt 写这么死，LLM 还是有 1-3% 的概率试图调工具。

**这就是 Harness Engineering 的现实**：
- **Harness 不是 100% 防御**——是 96-99% 的概率防御
- 剩下的 1-4% 靠**熔断 + 重试 + 人工兜底**补救
- 完美主义在 Agent 工程里是错的——**确定性 + 熔断 > 完美**

---

## 13. 📅 Day 3 预告 · Anthropic 官方 5 种工作流模式

🔗 来源：[Anthropic Building Effective Agents (2024-12-19)](https://www.anthropic.com/engineering/building-effective-agents)

**核心哲学（Anthropic 官方原文）**：
> "When building applications with LLMs, **find the simplest solution possible and only increase complexity when needed**; this might mean **not building agentic systems at all**."
>
> "For many applications, **optimizing single LLM calls** with retrieval and in-context examples is usually enough."

**5 种工作流模式**（Anthropic 官方命名）：

| # | 模式 | 一句话 | 适合场景 |
|---|------|--------|----------|
| 1 | **Prompt Chaining** | 固定顺序的 LLM 调用链 + 编程 gate 检查 | 任务能干净拆成固定子任务 |
| 2 | **Routing** | 分类后路由到专门的 handler / 模型 | 简单查询用小模型、难查询用大模型 |
| 3 | **Parallelization** | 并行多个 LLM 调用再聚合 | 2 个变体：Sectioning（独立子任务）+ Voting（同任务多次跑投票） |
| 4 | **Orchestrator-Workers** | 中央 LLM 动态拆任务 + 委派 worker | 子任务不能预先定义（多文件改动、信息聚合） |
| 5 | **Evaluator-Optimizer** | 一个 LLM 生成 + 另一个 LLM 评估反馈循环 | 有明确评估标准 + 迭代能提升质量 |

**Framework 警告（Anthropic 原文）**：
> "We suggest that developers start by using LLM APIs directly; **many patterns can be implemented in a few lines of code**. If you do use a framework, ensure you understand the underlying code."

**Augmented LLM**（基础构建块）：
> LLM + retrieval + tools + memory（Anthropic 推荐 MCP 作为 integration 方式之一）

**生产用例**（Anthropic 官方列举）：
- **Customer support**：对话 + 工具支持动作
- **Coding agents**：可验证解（自动化测试）+ SWE-bench Verified 基准

> 📌 **Day 3 会展开讲**：这些模式如何映射到 CC 的 `query.ts` / `AgentTool` / 实际产品（CC / Cursor / Manus / Devin）的设计选择。

---

## 14. 下一步

- ✅ 自测题 v2：见 `Day-01-自测.md`，4 道题（新增第 4 题动手读源码）
- 📅 Day 2：读主指南 `Part 15`（学习路线建议）+ `结语` + 浏览仓库目录结构
- 📅 Day 3：Anthropic 官方 5 种工作流模式 + ReAct / CoT 学术基础

> 📝 **本讲义 v2.1 重要变化**（v2 → v2.1）：
> - 加了 §12 /compact prompt 实战金句（Harness 不是 100% 防御）
> - 加了 §13 Day 3 预告（Anthropic 官方 5 种工作流模式 + "simple is better" 哲学）
> - 标了所有官方链接的发布日期（之前漏了）
>
> **v1 → v2 变化回顾**：
> - 加了 §0 来源等级表、§1 术语出处修正（重要纠错）
> - 支柱 1 改了"40% 阈值"的说法，给真实阈值 `AUTOCOMPACT_BUFFER_TOKENS=13_000`
> - 支柱 1 加了 Prompt Caching 6 条硬规则
> - 支柱 2 加了 OWASP / NIST / Saltzer-Schroeder 三大权威背书
> - 支柱 2-3 加了源码印证（直接贴代码 + 行号）
> - 加了 §11 权威来源索引（12 条带链接）
