# Harness（线束/装甲）

## 一句话定义
Harness 是让 LLM 变成 Agent 的外部系统，由循环、工具、上下文管理、安全权限四个子系统构成。

## 核心公式
> **Agent = Model + Harness**

## 详细说明
Harness 这个概念来自工程领域——汽车的"线束"（wiring harness）是把发动机、电池、各种传感器连接在一起的神经系统。在 Agent 语境中，Harness 的角色一样：它不是智能本身（那是 LLM 的事），它是让智能能够**行动**的基础设施。

四个子系统各自解决一个核心问题：
1. **Loop（循环）**→ LLM 不会主动行动，循环驱动它持续工作
2. **Tools（工具）**→ LLM 没有"手"，工具让它与外部世界交互
3. **Context Management（上下文管理）**→ LLM 记忆有限，上下文管理让它在长任务中不迷失
4. **Guardrails（安全权限）**→ LLM 不可预测，安全系统防止它做有害的事

## 关键洞察
- 你要开发的"自己的 Agent"，本质上就是在设计 Harness
- Harness 的复杂度应该匹配任务的复杂度——简单任务不需要复杂 Harness
- Claude Code 512K 行代码中 95% 都是 Harness，只有 5% 是模型调用相关

## 我的理解
（待用户补充）

## 相关概念
- [[concepts/agent]]
- [[concepts/agentic-loop]]
- [[concepts/context-management]]
- [[concepts/guardrails]]
