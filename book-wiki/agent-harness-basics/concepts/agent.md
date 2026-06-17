# Agent（智能体）

## 一句话定义
Agent 是在 LLM 基础上套上 Harness 的智能体系统，能通过循环驱动、工具调用、上下文管理和安全约束来自主完成多步复杂任务。

## 详细说明
Agent 和普通 LLM 对话的根本区别不在于模型本身，而在于模型外面的"装甲"——Harness。同一个 LLM，裸着跑就是一问一答的聊天机器人，套上 Harness 就变成了能持续行动、调用工具、根据结果调整策略的智能体。

Agent 的四大能力来源：
1. **循环（Loop）**：反复调用 LLM，执行 → 观测 → 决策 → 再执行，直到任务完成
2. **工具（Tools）**：让 LLM 从"只会生成文本"变成"能读写文件、执行代码、查询数据"
3. **上下文管理（Context Management）**：主动管理记忆，在长任务中不迷失方向
4. **安全与权限（Guardrails）**：防止 Agent 执行有害操作，控制自主性边界

## 我的理解
（用户原话）Agent 能在 LLM 基础上有更强的鲁棒性、工具使用能力、任务规划能力，能真正像人类一样去做真正的事情。

## 关键区分
- Agent vs 普通 LLM：区别不在模型，在 Harness
- Agent vs Workflow：Agent 是动态决策的，Workflow 是预定义路径的（见 [[models/workflow-vs-agent]]）
- 鲁棒性不是模型天生的，是 Harness 设计出来的

## 相关概念
- [[concepts/harness]]
- [[concepts/agentic-loop]]
- [[models/anthropic-5-workflow-patterns]]
