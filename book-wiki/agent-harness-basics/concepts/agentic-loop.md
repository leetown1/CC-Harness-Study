# Agentic Loop（智能体循环）

## 一句话定义
Agentic Loop 是 Agent 的心脏——一个反复调用 LLM、执行工具、观测结果、注入上下文的 while 循环，直到任务完成。

## 详细说明
伪代码表示：

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

这个循环在不同产品中的实现：
- Claude Code：`query.ts` 的 `queryLoop()`，AsyncGenerator 模式
- Cursor Agent 模式：类似的循环，在 IDE 后台线程中运行
- Manus：CodeAct 范式，Agent 生成代码并在沙箱中执行
- Aider：更简单的循环，每次修改自动 git commit

循环终止条件：
- end_turn（模型认为任务完成）
- 预算超限（token 消耗超出限制）
- 轮次超限（循环次数超出上限）
- 错误熔断（连续错误触发安全退出）

## 学术根源
ReAct 论文的 Thought-Action-Observation 循环是 Agentic Loop 的理论原型（第 2 天会深入学习）。

## 我的理解
（用户原话）"少了循环就不叫 Agent 了"——循环是 Agent 最不可或缺的组件。

## 相关概念
- [[concepts/harness]]
- [[concepts/agent]]
- [[models/anthropic-5-workflow-patterns]] 中的 Evaluator-Optimizer 也包含循环
