# Claude Code 源码逐文件阅读进度

> **开始时间**: 2026-05-23
> **完成时间**: 2026-05-23
> **总文件数**: 1,985 个 .ts/.tsx 文件
> **总行数**: 506,456 行
> **完成状态**: ✅ 全部阅读完成

---

## 阅读覆盖清单

| 目录 | 文件数 | 状态 |
|------|--------|------|
| src/ (root) | 19 个核心文件 | ✅ 完成 |
| commands/ | 110 个文件 | ✅ 完成 |
| tools/ | 149 个文件 | ✅ 完成 |
| services/ | 132 个文件 | ✅ 完成 |
| utils/ | 254 个文件 | ✅ 完成 |
| utils/plugins/ | 44 个文件 | ✅ 完成 |
| components/ | 389 个文件 | ✅ 完成 |
| hooks/ | 104 个文件 | ✅ 完成 |
| ink/ | 96 个文件 | ✅ 完成 |
| state/ | 6 个文件 | ✅ 完成 |
| types/ | 11 个文件 | ✅ 完成 |
| constants/ | 21 个文件 | ✅ 完成 |
| context/ | 9 个文件 | ✅ 完成 |
| entrypoints/ | 8 个文件 | ✅ 完成 |
| cli/ | 18 个文件 | ✅ 完成 |
| bridge/ | 31 个文件 | ✅ 完成 |
| skills/ | 20 个文件 | ✅ 完成 |
| plugins/ | 2 个文件 | ✅ 完成 |
| buddy/ | 6 个文件 | ✅ 完成 |
| assistant/ | 1 个文件 | ✅ 完成 |
| bootstrap/ | 1 个文件 | ✅ 完成 |
| keybindings/ | 12 个文件 | ✅ 完成 |
| memdir/ | 8 个文件 | ✅ 完成 |
| migrations/ | 10 个文件 | ✅ 完成 |
| moreright/ | 1 个文件 | ✅ 完成 |
| native-ts/ | 4 个文件 | ✅ 完成 |
| outputStyles/ | 1 个文件 | ✅ 完成 |
| query/ | 4 个文件 | ✅ 完成 |
| remote/ | 4 个文件 | ✅ 完成 |
| schemas/ | 1 个文件 | ✅ 完成 |
| screens/ | 3 个文件 | ✅ 完成 |
| server/ | 3 个文件 | ✅ 完成 |
| vim/ | 5 个文件 | ✅ 完成 |
| voice/ | 1 个文件 | ✅ 完成 |
| coordinator/ | 1 个文件 | ✅ 完成 |
| upstreamproxy/ | 2 个文件 | ✅ 完成 |
| tasks/ | 12 个文件 | ✅ 完成 |
| types/generated/ | 4 个文件 | ✅ 完成 |

---

## 系统架构总览

Claude Code 是一个基于 TypeScript/Bun 的 CLI AI 编程助手，架构分为以下层次：

### 1. 入口层
- **main.tsx** (4441行): CLI入口，60+ 命令行选项，启动编排
- **entrypoints/**: SDK协议、MCP服务器入口、沙箱配置
- **cli/**: 打印输出(5256行)、更新机制、传输层(SSE/WebSocket/CCR)

### 2. 核心引擎层
- **QueryEngine.ts** (1231行): 对话状态管理、SDK协议
- **query.ts** (1608行): 查询循环、上下文管理管道、错误恢复
- **query/**: 配置、依赖注入、StopHooks、Token预算

### 3. 工具系统
- **Tool.ts** (754行): Tool接口定义，50+字段
- **tools.ts** (373行): 工具注册表，特性门控
- **tools/** (149文件): AgentTool、BashTool、FileRead/Edit/Write、Grep、Glob、WebFetch、MCPTool等

### 4. 命令系统
- **commands.ts** (717行): 100+斜杠命令注册
- **commands/** (110文件): /agents、/mcp、/plugin、/memory、/compact等

### 5. 服务层
- **services/api/**: Claude API调用、重试逻辑、流式处理
- **services/mcp/**: MCP客户端、OAuth认证、Elicitation协议
- **services/compact/**: Snip→Microcompact→Collapse→Autocompact多层压缩
- **services/analytics/**: GrowthBook特性标志、Datadog/1P事件日志
- **services/plugins/**: 插件CRUD、安装管理
- **services/lsp/**: LSP服务器管理、诊断

### 6. 扩展系统
- **utils/plugins/** (44文件): 插件加载器、市场管理、依赖解析、ZIP缓存
- **skills/** (20文件): 内置技能、技能目录加载、MCP技能构建

### 7. UI层
- **components/** (389文件): React/Ink终端UI组件
- **hooks/** (104文件): React Hooks(useTextInput、useVoice、useKeybinding等)
- **ink/** (96文件): 终端渲染引擎(Yoga布局、ANSI解析、事件系统)

### 8. 基础设施
- **utils/** (254文件): Bash解析器(4299行ast)、消息序列化(5068行)、Hook系统(4673行)、会话存储(4699行)
- **bridge/** (31文件): 远程控制桥接、REPL桥接
- **state/**: AppState管理
- **types/**: 权限、插件、命令、Hook类型定义
- **constants/**: 系统提示构建、OAuth配置、API限制
