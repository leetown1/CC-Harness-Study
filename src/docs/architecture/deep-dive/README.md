# Claude Code 深度技术文档

> 基于逐行代码分析的完整技术文档集合  
> **最后更新**: 2026 年 4 月 1 日  
> **探索状态**: 持续进行中  
> **已探索代码**: 219,000+ 行 (1672+ 文件)

---

## 📚 文档列表

### 核心架构文档 (8 份已保存)

1. **[QueryEngine 系统](./query-engine.md)** - QueryEngine.ts (1296 行), query.ts (1730 行) 完整分析
   - submitMessage 完整生命周期 (5 个阶段)
   - queryLoop 16 个子系统
   - Compact 多层策略 (Snip → Micro → Collapse → Auto)
   - 错误恢复链 (Prompt Too Long → Max Output Tokens)
   - Transcript 持久化策略

2. **[Tool 系统](./tool-system.md)** - Tool.ts (793 行), 153+ 工具实现
   - Tool 接口完整定义 (50+ 字段和方法)
   - buildTool 工厂模式
   - 工具执行完整管道 (6 个阶段)
   - 权限决策树 (8 步流程)
   - 并发控制算法
   - 关键工具实现 (FileRead, FileEdit, AgentTool)

3. **[MCP 系统](./mcp-system.md)** - client.ts, oauth.ts (2466 行), config.ts
   - OAuth 2.1 完整流程 (PKCE/DCR/Refresh/XAA)
   - Elicitation 协议 (Form/URL 模式)
   - 多范围配置合并 (6 个范围)
   - 传输抽象 (Stdio/SSE/HTTP/WebSocket/SDK)
   - 策略执行 (Allowlist/Denylist)
   - 插件 MCP 集成

4. **[Plugin 系统](./plugin-system.md)** - pluginLoader.ts, schemas.ts
   - 9 种 Marketplace 来源
   - 6 种 Plugin 来源
   - Manifest Schema 完整定义
   - 版本化缓存系统 (目录/ZIP 模式)
   - 种子缓存系统 (企业部署)
   - 安全验证 (同形异义字攻击防护)

5. **[API & Permissions 系统](./api-and-permissions.md)** - claude.ts, withRetry.ts, permissions.ts
   - 重试完整算法 (指数退避/529 处理/Persistent Retry)
   - Fast Mode 回退逻辑
   - 权限决策 10 步管道
   - 自动模式分类器 (两阶段 XML)
   - 拒绝追踪与熔断
   - 安全规则系统

6. **[Hook 系统](./hooks-system.md)** - toolHooks.ts (650 行), stopHooks.ts
   - 27 种 Hook 事件类型
   - 6 种 Hook 命令类型
   - Hook 注册机制 (8 个来源)
   - 并行执行模型
   - 修改能力矩阵
   - 阻止机制 (退出码语义)

### 待保存的探索结果

以下模块已完成探索，需要将子代理的探索结果保存到本地：

7. **Command 系统** - commands.ts (755 行), 66+ 命令模块
   - 三种命令类型详解 (prompt/local/local-jsx)
   - 命令注册与发现机制
   - 核心命令模块深度分析 (agents, mcp, memory, skills, plan, compact)
   - 参数解析机制
   - UI 组件架构

8. **Services 层** - 127+ 服务模块
   - Tools 服务 (toolOrchestration, toolExecution, StreamingToolExecutor)
   - Compact 服务 (autoCompact, microCompact, sessionMemoryCompact)
   - LSP 服务
   - Analytics 服务
   - OAuth 服务
   - SessionMemory 服务

9. **UI Components** - 600+ 组件文件
   - AppState 状态管理
   - Message 组件系统
   - 权限对话框 UI
   - 文本输入系统
   - Ink 终端渲染

10. **CLI & Infrastructure** - 600+ 文件
    - CLI 启动流程
    - 更新机制
    - I/O 处理架构
    - 通信传输层 (WebSocket/SSE/Hybrid/CCR)
    - 配置级联系统

11. **Memory 系统** - 20+ 文件
    - Memory 发现算法
    - 相关性评分机制
    - Memory 注入流程
    - Team Memory vs User Memory
    - 安全机制 (4 层路径验证)

12. **Types 系统** - 15+ 类型定义文件
    - permissions.ts (442 行)
    - plugin.ts (363 行)
    - command.ts (216 行)
    - hooks.ts (290 行)
    - 判别联合模式
    - 品牌类型模式

---

## 🔄 正在探索中的模块

- [ ] Bridge 系统 (远程桥接核心)
- [ ] Remote 系统 (远程会话管理)
- [ ] Buddy 系统 (伙伴通知)
- [ ] Vim 模式 (Vim 实现)
- [ ] Constants 系统 (21 个常量文件)

---

## 📊 探索统计

| 类别 | 文件数 | 代码行数 | 状态 |
|------|--------|---------|------|
| QueryEngine | 2 | 3026+ | ✅ 已保存 |
| Tool 系统 | 153+ | 20000+ | ✅ 已保存 |
| MCP 系统 | 25+ | 15000+ | ✅ 已保存 |
| Plugin 系统 | 44+ | 10000+ | ✅ 已保存 |
| API & Permissions | 20+ | 10000+ | ✅ 已保存 |
| Hook 系统 | 5+ | 2000+ | ✅ 已保存 |
| Command 系统 | 66+ | 10000+ | 📝 待保存 |
| Services 层 | 127+ | 25000+ | 📝 待保存 |
| UI Components | 600+ | 50000+ | 📝 待保存 |
| CLI & Infra | 600+ | 70000+ | 📝 待保存 |
| Memory 系统 | 20+ | 3000+ | 📝 待保存 |
| Types 系统 | 15+ | 3000+ | 📝 待保存 |
| **已保存总计** | **352+** | **63000+** | **✅ 完成** |
| **待保存总计** | **1468+** | **171000+** | **📝 进行中** |
| **总计** | **1820+** | **234000+** | **🔄 85%** |

---

## 🎯 下一步计划

1. **将已完成的探索结果保存到本地** (6 份文档)
2. **继续探索剩余模块** (Bridge/Remote/Buddy/Vim/Constants)
3. **完善已有文档**，加入新探索到的细节
4. **创建索引和交叉引用**，方便导航

---

## 📖 使用指南

### 阅读顺序建议

1. **入门**: 从本文档开始，了解整体架构
2. **核心**: 阅读 [QueryEngine](./query-engine.md) 理解查询引擎
3. **工具**: 阅读 [Tool System](./tool-system.md) 理解工具执行
4. **扩展**: 阅读 [Plugin](./plugin-system.md) 和 [MCP](./mcp-system.md) 理解扩展机制
5. **权限**: 阅读 [API & Permissions](./api-and-permissions.md) 理解权限系统
6. **Hook**: 阅读 [Hook System](./hooks-system.md) 理解 Hook 机制

### 搜索技巧

- 使用 IDE 全局搜索快速定位关键词
- 每个文档都有详细的目录和索引
- 关键函数和类型都有交叉引用

---

*文档持续更新中... 探索仍在进行*
