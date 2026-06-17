# 吴恩达四种 Agentic 设计模式

## 一句话定义
吴恩达从"能力"角度总结 Agent 的四种核心设计模式：反思、工具使用、规划、多智能体协作。

## 四种模式

### 1. Reflection（反思）
LLM 审视自己的输出，发现不足，自我改进。
- 对应 Anthropic 的 Evaluator-Optimizer
- 例子：写完代码后让 LLM 自己 review 找 bug

### 2. Tool Use（工具使用）
给 LLM 配备搜索、代码执行、数据库查询等外部工具。
- 这是 Agent 从"只会说"变成"能动手"的关键
- 对应 Harness 四件套中的"工具"子系统

### 3. Planning（规划）
面对复杂任务，Agent 先制定多步计划，然后按计划执行。
- 对应 Anthropic 的 Orchestrator-Workers 的前半段
- 例子：重构模块 → 先分析依赖 → 确定修改顺序 → 逐步执行

### 4. Multi-Agent Collaboration（多智能体协作）
多个 Agent 分工合作，或互相辩论来得到更好方案。
- 对应 Anthropic 的 Parallelization + Orchestrator-Workers
- 例子：一个 Agent 写代码，另一个专门挑刺做 code review

## 关键洞察
吴恩达的四种模式和 Anthropic 的五种 Workflow 模式有大量重叠——这不是巧合，因为 Agent 设计的基本模式就那么几种，不同人从不同角度观察，看到的是同一头大象的不同部位。

吴恩达从"Agent 需要什么能力"的角度切入（能力视角），Anthropic 从"系统怎么编排"的角度切入（架构视角）。

## 我的理解
（待用户补充）

## 相关概念
- [[models/anthropic-5-workflow-patterns]]
- [[concepts/agent]]
- [[concepts/harness]]
