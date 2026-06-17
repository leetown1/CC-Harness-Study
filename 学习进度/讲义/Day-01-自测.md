# Day 1 自测题（v2 增强版）

> 配套讲义：`Day-01-Harness与六大支柱.md`（v2 权威增强版）
> 做完发给 Claude（我），我来对答案 + 批改
> v2 新增第 4 题"动手读源码"

---

## 第 1 题 · 概念题（热身）

**问题**：
在 `Agent = Model + Harness` 这个公式中，CC 的源码告诉我们，调用 LLM 本身的代码不到 5%，剩下 95% 全是 Harness。

**问**：为什么一个顶级 AI Agent 团队会把 95% 的精力放在 Harness（基础设施）上，而不是放在"调 prompt / 选模型 / 训练"上？请用 1-2 句话讲清你的理解。

**参考答案**（批改时看）：
> 模型能力很强但**不可预测**——同样的任务跑两次可能质量差距很大。Harness 的全部意义就是**在这种不确定性之上构建确定性的工程系统**。真正决定 Agent 可靠、可用、好用的是错误恢复、权限管理、上下文压缩、启动性能这些"非模型"工程。

**批改要点**：
- ✅ 提到"模型的不可预测性"——核心
- ✅ 提到"确定性 / 可靠性 / 体验"中任意一个词
- ❌ 只回答"基础设施很重要"这种空话——需要落到具体例子

---

## 第 2 题 · 设计哲学题（理解 Fail-Closed）

**问题**：
CC 的 `buildTool()` 工厂有这样一组默认值：

```typescript
const TOOL_DEFAULTS = {
  isConcurrencySafe: () => false,
  isReadOnly: () => false,
  isDestructive: () => false,
  toAutoClassifierInput: () => '',
}
```

**问**：
1. 这些默认值的设计哲学叫什么？（1 个词）
2. 为什么要把"安全分类器默认输入"设成空串 `''`？如果忘了给某个工具覆写，会发生什么？
3. 假设你新加了一个"删除文件"工具，忘了设置 `isDestructive` 字段，会发生什么？这是 bug 还是 feature？
4. 🆕 **v2 追加**：这个设计哲学**不是 Anthropic 一家之见**——请列出 2 个**外部权威源**（OWASP / NIST / 学术任选）支持"AI Agent 应该 fail-closed"的依据。

**参考答案**：
1. **Fail-Closed**（失败时关闭，走最受限路径）。
2. 安全分类器拿到空串就等于"我不知道这个工具干什么"——**不参与决策**，让请求走完整的人工确认流程。如果忘了覆写 `toAutoClassifierInput`，**分类器不参与，工具调用强制弹给用户**。
3. 这是 **Feature，不是 Bug**。`isDestructive: false` 表示"声明自己非破坏性"，但权限系统**不会因此放行**——它仍然走完整的 5 层纵深防御（静态规则 → 路径保护 → 语义分析 → 分类器 → 人工确认）。**声明 ≠ 授权**。
4. 外部权威（任选 2）：
   - **OWASP Agentic AI Threats and Mitigations Guide (2025-01-20)**：明确推荐 "default-deny" 工具调用策略
   - **NIST AI RMF 1.0 + NIST AI 600-1 (GenAI Profile, 2024-07)**：MEASURE/MANAGE 函数下 "fail-safe and fail-secure behavior"
   - **Saltzer & Schroeder (1975) ACM 论文**："fail-safe defaults" 是经典 8 条安全设计原则之一
   - **OWASP LLM Top 10 (2025)**：LLM03 (Training Data Poisoning) + LLM07 (Insecure Plugin Design) 都涉及工具调用安全

**批改要点**：
- ✅ 答出 Fail-Closed
- ✅ 解释空串的含义（分类器不参与）
- ✅ 第 3 问：必须明确"声明不等于授权"
- ✅ **第 4 问（v2 重点）**：能说出 2 个具体的权威源名字 + 关键术语（"default-deny" / "fail-safe" / "fail-safe defaults"）
- ⚠️ 进阶（加分）：能提到 5 层纵深防御的具体来源（NIST SP 800-53 / CWE-22）

---

## 第 3 题 · 反直觉题（看是不是真懂了）

**问题**：
CC 的 `query()` while(true) 循环被拆解为 16 个步骤，其中**只有 1 步**在调用 LLM API。

**问**：
1. 剩下 15 步大致在做什么？（列出 3-4 类）
2. 这件事揭示了 Agent 工程的什么**反直觉真相**？
3. 如果你是 CC 的 PM，要招一个"提升 Agent 质量"的人，**你会优先招什么样的工程师**？（给画像，不需要名字）
4. 🆕 **v2 追加**：CC 有一个**真实生产数据金句**说明为什么 auto-compact 熔断要做成 3 次——这个金句的数字是什么？

**参考答案**：
1. 剩下 15 步主要在干：
   - 上下文管理（4 级压缩：Snip / Micro / ContextCollapse / AutoCompact）
   - 权限检查（5 层纵深防御）
   - 工具执行协调（并发控制、错误隔离）
   - 状态持久化（消息记录、断点恢复）
   - 错误恢复（重试、熔断、max_output_tokens 恢复）
   - Token 预算检查

2. **反直觉真相**：**模型调用是整个系统中最简单的部分**。真正决定 Agent 质量的不是"模型多聪明"，而是"这 15 步工程做得多扎实"。大多数人以为做 AI Agent 是调 prompt，**实际上是在做分布式系统**——错误恢复、状态管理、并发控制才是主战场。

3. **优先招的画像**：
   - ✅ 分布式系统工程师 / 后端工程师（懂得状态机、错误恢复、熔断）
   - ✅ DevOps / SRE 背景（懂得可观测性、限流、降级）
   - ⚠️ 不优先：纯算法 / 调 prompt / 训练微调背景

4. **生产数据金句**（来自 `src/services/compact/autoCompact.ts` 注释）：
   > "BQ 2026-03-10: **1,279 sessions had 50+ consecutive failures (up to 3,272) in a single session, wasting ~250K API calls/day globally.**"
   
   → 数字：**1,279 sessions** 连续失败 50+ 次（最多 **3,272 次**），每天浪费约 **25 万次** API 调用。这就是 `MAX_CONSECUTIVE_AUTOCOMPACT_FAILURES = 3` 的来源。

**批改要点**：
- ✅ 15 步列对 3-4 类即可
- ✅ 必须明确"模型调用不是难点"这个反直觉点
- ✅ 第 3 问：能跳"调 prompt / 选模型"的圈
- ✅ **第 4 问（v2 重点）**：能说出 1279 / 3272 / 25 万 这三个数字中至少 2 个
- 🎁 加分：能提到"做 Agent 实际上是做分布式系统"

---

## 🆕 第 4 题 · 动手读源码题（v2 独家）

**目的**：验证你是不是真的去 `src/` 里看了，而不是只看讲义。Harness Engineering 的核心是**用代码强制规则**——所以你得亲眼看到代码。

**任务**：

请打开 `src/Tool.ts`，定位到 `TOOL_DEFAULTS` 这个常量（提示：在文件**约 700-800 行**之间），把这段代码 + 它**正上方**的注释（应该是一段说明 fail-closed 的注释）原样贴出来。

**如果你确实读了源码**，会注意到几个细节：

1. 注释里**直接出现 "fail-closed" 这个词**——这证明"Fail-Closed"不是后人归纳的，是 Anthropic 自己的命名
2. 注释里有 "**(assume not safe)**" / "**(assume writes)**" 这样的元注释
3. `checkPermissions` 默认是 `{ behavior: 'allow', ... }`——**这看起来像 Fail-Open 啊**？你想想为什么这不是 Fail-Open？

**第 3 问的参考答案**：
`checkPermissions` 默认返回 `allow` 看似 Fail-Open，但**决策被委托给外层 5 层纵深防御**——工具自身的权限检查只是第一层，后面还有路径保护、语义分析、分类器、人工确认。**单层 Fail-Open 不等于系统 Fail-Open**——这是"defense in depth"哲学的体现。

**批改要点**：
- ✅ 贴出的代码片段**真实存在**（能复现 grep 结果）
- ✅ 看到注释里 "fail-closed" 这个词
- ✅ 第 3 问：能解释"单层 allow" + "外层纵深"的关系
- 🎁 加分：能引用 `DANGEROUS_uncachedSystemPromptSection` 这种 Anthropic 命名风格

---

## 自评指南

| 分数 | 含义 |
|------|------|
| 4 题全对 | 掌握扎实，可以推 Day 2 |
| 3 题对 | 基础有了，再读一遍讲义红字部分 + 把缺的源码看一遍 |
| < 3 题对 | 建议重读 `Claude Code 架构全景学习指南.md` Part 1 + 精读 `src/Tool.ts` 700-800 行 |

---

> 📝 **请把你的答案发给我**，我对每题给你具体的批改 + 追问。
> 📅 答完后 Day 1 推进到 `mastered`（如果全对）或 `needs_re_read`（如果有疑点）。
> 📂 v2 升级点：第 2 题加了外部权威源问；第 3 题加了生产数据金句问；新增第 4 题动手读源码。
