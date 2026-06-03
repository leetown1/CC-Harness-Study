# Claude Code 深度技术文档 - 探索进度

> **最后更新**: 2026 年 4 月 1 日  
> **探索状态**: 持续进行中  
> **已保存文档**: 10 份  
> **已探索代码**: 219,000+ 行 (1672+ 文件)

---

## 📊 当前进度总览

### ✅ 已完成探索并保存到本地的文档 (10 份)

| # | 文档 | 文件大小 | 状态 | 核心内容 |
|---|------|---------|------|---------|
| 1 | [README.md](./README.md) | 导航索引 | ✅ 已保存 | 文档集合导航 |
| 2 | [PROGRESS.md](./PROGRESS.md) | 进度跟踪 | ✅ 已保存 | 探索进度跟踪 |
| 3 | [query-engine.md](./query-engine.md) | QueryEngine 完整分析 | ✅ 已保存 | 3026+ 行代码分析 |
| 4 | [tool-system.md](./tool-system.md) | Tool 系统完整分析 | ✅ 已保存 | 20000+ 行代码分析 |
| 5 | [mcp-system.md](./mcp-system.md) | MCP 系统完整分析 | ✅ 已保存 | 15000+ 行代码分析 |
| 6 | [plugin-system.md](./plugin-system.md) | Plugin 系统完整分析 | ✅ 已保存 | 10000+ 行代码分析 |
| 7 | [api-and-permissions.md](./api-and-permissions.md) | API 与权限系统 | ✅ 已保存 | 10000+ 行代码分析 |
| 8 | [hooks-system.md](./hooks-system.md) | Hook 系统完整分析 | ✅ 已保存 | 2000+ 行代码分析 |
| 9 | [command-system.md](./command-system.md) | Command 系统完整分析 | ✅ 已保存 | 10000+ 行代码分析 |
| 10 | [memory-system.md](./memory-system.md) | Memory 系统完整分析 | ✅ 已保存 | 3000+ 行代码分析 |

### 🔄 正在探索中的模块

| 模块 | 子代理状态 | 预计完成时间 |
|------|-----------|-------------|
| Services 层 | 🔄 子代理探索完成，待保存 | - |
| UI Components | 🔄 子代理探索完成，待保存 | - |
| CLI & Infrastructure | 🔄 子代理探索完成，待保存 | - |
| Types 系统 | 🔄 子代理探索完成，待保存 | - |
| Bridge 系统 | ⏳ 待启动子代理 | - |
| Remote 系统 | ⏳ 待启动子代理 | - |
| Buddy 系统 | ⏳ 待启动子代理 | - |
| Vim 模式 | ⏳ 待启动子代理 | - |
| Constants 系统 | ⏳ 待启动子代理 | - |

---

## 📚 已保存文档内容概览

### 1. QueryEngine 深度文档 (query-engine.md)

**核心内容**:
- QueryEngine.ts (1296 行) 完整分析
- query.ts (1730 行) 完整分析
- submitMessage 完整生命周期 (5 个阶段)
- queryLoop 16 个子系统
- Compact 多层策略 (Snip → Micro → Collapse → Auto)
- 错误恢复链 (Prompt Too Long → Max Output Tokens)
- Transcript 持久化策略

**关键发现**:
- 状态机模式管理跨迭代状态
- continue 站点实现复杂控制流
- 分层 Compact 策略
- 特性标志三层门控

### 2. Tool 系统深度文档 (tool-system.md)

**核心内容**:
- Tool 接口完整定义 (50+ 字段和方法)
- buildTool 工厂模式
- 153+ 工具逐一分析
- 工具执行完整管道 (6 个阶段)
- 权限决策树 (8 步流程)
- 并发控制算法
- Hook 系统集成

**关键工具**:
- FileReadTool: 去重/Token 预算/PDF 提取
- FileEditTool: 原子编辑/LSP 通知
- AgentTool: 子代理生命周期
- BashTool: 安全机制
- PowerShellTool: Windows 特定实现

### 3. MCP 系统深度文档 (mcp-system.md)

**核心内容**:
- OAuth 2.1 完整流程 (PKCE/DCR/Refresh/XAA)
- Elicitation 协议 (Form/URL 模式)
- 多范围配置合并 (6 个范围)
- 传输抽象 (Stdio/SSE/HTTP/WebSocket/SDK)
- 策略执行 (Allowlist/Denylist)
- 插件 MCP 集成

**关键发现**:
- 基于签名的去重算法
- 跨进程 Token 刷新锁
- XAA 企业 SSO (一次登录，多次使用)
- 环境变量三阶段扩展

### 4. Plugin 系统深度文档 (plugin-system.md)

**核心内容**:
- 9 种 Marketplace 来源
- 6 种 Plugin 来源
- Manifest Schema 完整定义
- 版本化缓存系统 (目录/ZIP 模式)
- 种子缓存系统 (企业部署)
- 安全验证 (同形异义字攻击防护)

**关键机制**:
- 插件命名空间 (`plugin:{name}:{server}`)
- 插件去重 (签名匹配)
- 官方名称保护
- 设置白名单合并

### 5. API & Permissions 深度文档 (api-and-permissions.md)

**核心内容**:
- 重试完整算法 (指数退避/529 处理/Persistent Retry)
- Fast Mode 回退逻辑
- 多 Provider 支持 (First-party/Bedrock/Vertex/Azure)
- 权限决策 10 步管道
- 自动模式分类器 (两阶段 XML)
- 拒绝追踪与熔断
- 安全规则系统

**关键算法**:
- 重试延迟计算 (500ms 基础，32s 上限，25% jitter)
- 权限决策树 (deny → ask → allow)
- 自动模式分类 (Fast 64 tokens → Thinking 4096 tokens)
- 拒绝限制 (连续 3 次 / 总计 20 次 → 回退到询问)

### 6. Hook 系统深度文档 (hooks-system.md)

**核心内容**:
- 27 种 Hook 事件类型
- 6 种 Hook 命令类型 (Command/Prompt/Agent/HTTP/Callback/Function)
- Hook 注册机制 (8 个来源)
- 并行执行模型
- 独立超时控制
- 修改能力矩阵
- 阻止机制 (退出码语义)

**关键特性**:
- PreToolUse: 修改输入/阻止执行
- PostToolUse: 修改 MCP 输出
- PermissionRequest: 权限决策覆盖
- Async Hook: 后台执行/唤醒机制

### 7. Command 系统深度文档 (command-system.md)

**核心内容**:
- 三种命令类型详解 (prompt/local/local-jsx)
- 命令注册与发现机制
- 66+ 命令模块分析
- 核心命令模块深度分析 (agents, mcp, memory, skills, plan, compact)
- 参数解析机制
- UI 组件架构
- 与核心系统的交互

**关键命令**:
- /agents: 代理管理 (6 个状态机模式)
- /mcp: MCP 服务器管理
- /memory: 内存文件编辑
- /plan: 计划模式切换
- /compact: 对话压缩

### 8. Memory 系统深度文档 (memory-system.md)

**核心内容**:
- Memory 发现算法详解 (6 步流程)
- AI 相关性评分机制
- Memory 注入流程
- 缓存和去重机制
- Team Memory vs User Memory
- 安全机制 (4 层路径验证)

**关键发现**:
- 封闭类型分类 (user/feedback/project/reference)
- AI 驱动选择 (Sonnet 语义选择)
- 时间衰减感知 (>1 天触发警告)
- 符号链接攻击防护

---

## 📈 代码覆盖统计

### 已保存文档覆盖

| 类别 | 文件数 | 代码行数 | 状态 |
|------|--------|---------|------|
| QueryEngine | 2 | 3026+ | ✅ 已保存 |
| Tool 系统 | 153+ | 20000+ | ✅ 已保存 |
| MCP 系统 | 25+ | 15000+ | ✅ 已保存 |
| Plugin 系统 | 44+ | 10000+ | ✅ 已保存 |
| API & Permissions | 20+ | 10000+ | ✅ 已保存 |
| Hook 系统 | 5+ | 2000+ | ✅ 已保存 |
| Command 系统 | 66+ | 10000+ | ✅ 已保存 |
| Memory 系统 | 20+ | 3000+ | ✅ 已保存 |
| **已保存总计** | **336+** | **73000+** | **✅ 完成** |

### 待保存到本地的文档

| 类别 | 文件数 | 代码行数 | 状态 |
|------|--------|---------|------|
| Services 层 | 127+ | 25000+ | 📝 子代理完成，待保存 |
| UI Components | 600+ | 50000+ | 📝 子代理完成，待保存 |
| CLI & Infra | 600+ | 70000+ | 📝 子代理完成，待保存 |
| Types 系统 | 15+ | 3000+ | 📝 子代理完成，待保存 |
| **待保存总计** | **1342+** | **148000+** | **📝 进行中** |

### 待探索模块

| 类别 | 文件数 | 代码行数 | 状态 |
|------|--------|---------|------|
| Bridge 系统 | 20+ | 5000+ | ⏳ 待启动 |
| Remote 系统 | 30+ | 8000+ | ⏳ 待启动 |
| Buddy 系统 | 5+ | 500+ | ⏳ 待启动 |
| Vim 模式 | 10+ | 2000+ | ⏳ 待启动 |
| Constants 系统 | 21 | 3000+ | ⏳ 待启动 |
| **待探索总计** | **86+** | **18500+** | **⏳ 待启动** |

### 总计

| 指标 | 数值 |
|------|------|
| 总探索文件数 | 1758+ |
| 总代码行数 | 239500+ |
| 已保存文档 | 10 份 |
| 待保存文档 | 4 份 |
| 待探索模块 | 5 个 |
| 整体覆盖率 | 🔄 90% |

---

## 🎯 下一步工作

### 立即需要

1. ✅ 完成：QueryEngine, Tool, MCP, Plugin, API/Permissions, Hook, Command, Memory 文档保存
2. 🔄 进行中：将子代理已完成的文档保存到本地
   - services-layer.md
   - ui-components.md
   - cli-and-infrastructure.md
   - types-system.md
3. ⏳ 继续：启动子代理探索 Bridge/Remote/Buddy/Vim/Constants

### 持续进行

- 多子代理并行深度探索
- 逐行代码分析
- 文档持续更新

---

## 📖 文档阅读顺序建议

1. **入门**: 从 [README.md](./README.md) 开始，了解整体架构
2. **核心**: 阅读 [QueryEngine](./query-engine.md) 理解查询引擎
3. **工具**: 阅读 [Tool System](./tool-system.md) 理解工具执行
4. **扩展**: 阅读 [Plugin](./plugin-system.md) 和 [MCP](./mcp-system.md) 理解扩展机制
5. **权限**: 阅读 [API & Permissions](./api-and-permissions.md) 理解权限系统
6. **Hook**: 阅读 [Hook System](./hooks-system.md) 理解 Hook 机制
7. **命令**: 阅读 [Command System](./command-system.md) 理解命令系统
8. **内存**: 阅读 [Memory System](./memory-system.md) 理解记忆系统

---

*文档持续更新中... 探索仍在进行*
