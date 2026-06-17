# Workflow vs Agent（工作流 vs 智能体）

## 一句话定义
Anthropic 把 Agentic Systems 分为两类：Workflow 按预定义路径执行，Agent 动态自主决策。大多数成功应用其实是 Workflow。

## 详细说明

**Workflow（工作流）**：LLM 和工具按照预定义的代码路径被编排。流程是人写好的，LLM 在每个节点做擅长的事（分类、生成、判断）。人是设计师，LLM 是工人。

**Agent（智能体）**：LLM 自主决定自己的流程走向和工具使用。没有预定义的固定路径，LLM 根据当前状态动态决策。LLM 既是工人也是现场指挥官。

**判断标准**：任务步骤能不能提前预知？
- 能预知 → Workflow（更稳定、更可控、更便宜）
- 不能预知 → Agent（更灵活、但更不可预测）

**核心原则**："简单优先，拒绝过度设计"——先用 Workflow 覆盖 80% 的确定场景，只在 Workflow 搞不定的地方加 Agent 能力。

## 我的理解
（用户原话）"有固定流程的时候就用 Workflow"；数据分析如果有确定方法，Workflow 就够了。

## 相关概念
- [[models/anthropic-5-workflow-patterns]]
- [[concepts/agent]]
