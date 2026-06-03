# Claude Code 架构深度解析

本文档基于对 Claude Code 源代码的逐行分析，提供比官方文档更深入的技术细节。

## 一、系统概述

Claude Code 是一个基于 TypeScript/Bun 构建的命令行 AI 编程助手，采用模块化架构设计，主要包含以下核心子系统：

```
┌─────────────────────────────────────────────────────────────────┐
│                        main.tsx (入口点)                         │
│  - CLI 参数解析                                                  │
│  - 启动流程编排                                                  │
│  - 热重载与迁移                                                  │
└───────────────────────────────┬─────────────────────────────────┘
                                │
        ┌───────────────────────┼───────────────────────┐
        ▼                       ▼                       ▼
┌───────────────┐     ┌───────────────┐     ┌───────────────┐
│  QueryEngine  │     │  Tool System  │     │ Command System│
│  (查询引擎)    │     │  (工具系统)    │     │  (命令系统)   │
└───────┬───────┘     └───────┬───────┘     └───────┬───────┘
        │                     │                     │
        └──────────────────────┼──────────────────────┘
                              ▼
                    ┌───────────────────┐
                    │   Plugin System   │
                    │   Skills System   │
                    │   MCP Services    │
                    └───────────────────┘
```

## 二、目录结构详解

### 顶层目录职责

| 目录 | 职责 | 核心文件 |
|------|------|----------|
| `assistant/` | KAIROS 助手模式实现 | - |
| `bootstrap/` | 启动状态管理、配置初始化 | `state.ts` |
| `bridge/` | 远程控制桥接模式 | - |
| `buddy/` | Buddy 功能模块 | - |
| `cli/` | 命令行接口实现 | - |
| `commands/` | 斜杠命令定义（110+ 文件） | `*.ts`, `*.tsx` |
| `components/` | React/Ink UI 组件 | - |
| `constants/` | 常量定义 | - |
| `context/` | 上下文管理 | - |
| `coordinator/` | 协调器模式（多代理） | `coordinatorMode.ts` |
| `entrypoints/` | 入口点定义 | `init.ts`, `agentSdkTypes.ts` |
| `hooks/` | React Hooks | `useCanUseTool.ts` |
| `ink/` | Ink 终端 UI 框架适配 | - |
| `keybindings/` | 快捷键管理 | - |
| `memdir/` | 内存目录管理 | - |
| `migrations/` | 配置迁移脚本 | - |
| `moreright/` | MoreRight 功能 | - |
| `native-ts/` | 原生 TypeScript 扩展 | - |
| `outputStyles/` | 输出样式定义 | - |
| `plugins/` | 内置插件注册 | `builtinPlugins.ts`, `bundled/index.ts` |
| `query/` | 查询循环辅助模块 | `config.ts`, `deps.ts`, `stopHooks.ts`, `tokenBudget.ts` |
| `remote/` | 远程会话管理 | `RemoteSessionManager.ts` |
| `schemas/` | Zod Schema 定义 | - |
| `screens/` | 全屏 UI 界面 | - |
| `server/` | 服务器模式 | `createDirectConnectSession.ts` |
| `services/` | 核心服务（127+ 文件） | `api/`, `mcp/`, `compact/`, `analytics/` |
| `skills/` | 内置技能定义 | `bundledSkills.ts`, `loadSkillsDir.ts` |
| `state/` | 应用状态管理 | `AppStateStore.ts`, `store.ts` |
| `tasks/` | 任务管理 | - |
| `tools/` | 工具实现（149+ 文件） | `BashTool/`, `FileReadTool/`, `AgentTool/` 等 |
| `types/` | TypeScript 类型定义 | `command.ts`, `message.ts`, `plugin.ts` |
| `utils/` | 工具函数库 | 大量辅助模块 |
| `vim/` | Vim 模式实现 | - |
| `voice/` | 语音模式实现 | - |

### 顶层核心文件

| 文件 | 大小 | 职责 |
|------|------|------|
| `main.tsx` | 803KB | 主入口点，CLI 解析，启动编排 |
| `QueryEngine.ts` | 46KB | 查询引擎类，会话状态管理 |
| `query.ts` | 68KB | 查询循环实现，核心状态机 |
| `Tool.ts` | 29KB | 工具接口定义，类型系统 |
| `tools.ts` | 17KB | 工具注册与获取 |
| `commands.ts` | 25KB | 命令聚合与发现 |
| `interactiveHelpers.tsx` | 57KB | 交互式 UI 辅助函数 |
| `dialogLaunchers.tsx` | 22KB | 对话框启动器 |
| `setup.ts` | 20KB | 初始化设置 |

## 三、核心依赖关系

```
main.tsx
    ├── commands.ts ──→ commands/
    ├── tools.ts ──→ tools/
    ├── QueryEngine.ts ──→ query.ts
    ├── services/
    │   ├── api/claude.ts (API 调用)
    │   ├── mcp/client.ts (MCP 协议)
    │   ├── compact/ (上下文压缩)
    │   └── analytics/ (分析)
    ├── skills/bundledSkills.ts ──→ skills/bundled/
    └── plugins/builtinPlugins.ts
```

## 四、启动流程分析

### main.tsx 启动序列

```typescript
// 1. 启动前置优化（并行执行）
profileCheckpoint('main_tsx_entry');
startMdmRawRead();      // MDM 配置预读
startKeychainPrefetch(); // 钥匙串预取

// 2. 特性门控条件导入
const coordinatorModeModule = feature('COORDINATOR_MODE') ? require('./coordinator/coordinatorMode.js') : null;
const assistantModule = feature('KAIROS') ? require('./assistant/index.js') : null;

// 3. 迁移执行
const CURRENT_MIGRATION_VERSION = 11;
function runMigrations(): void {
  // 执行配置迁移...
}

// 4. 延迟预取（渲染后执行）
export function startDeferredPrefetches(): void {
  void initUser();
  void getUserContext();
  prefetchSystemContextIfSafe();
  void getRelevantTips();
  // ... 更多预取
}

// 5. 主循环启动
// REPL 渲染或 headless 执行
```

### 关键启动优化点

1. **并行预取**：MDM 配置、钥匙串、OAuth 状态在模块加载时并行启动
2. **懒加载**：重型模块（如 insights.ts 113KB）使用动态导入
3. **特性门控**：通过 `feature()` 函数条件加载特性模块
4. **死代码消除**：Bun 打包时移除未启用特性的代码