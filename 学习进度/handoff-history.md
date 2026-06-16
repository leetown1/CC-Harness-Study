# 学习进度 · 交接历史

> 每次会话结束追加一条；新会话读这份就知道上次学到哪。

---

## 会话 #1 · 2026-06-14

### 本次做了什么
- ✅ 状态机初版（6 个 Day 落地到 `.study-state.json`）
- ✅ 调研 Ultracode 真实机制：外部网络被策略挡，CC 源码无 ultracode 关键词
- ✅ 重读 system prompt + Workflow 工具描述，把 Ultracode 心智模型从"prompt 开关"升级到"行为准则 + 主动配 MCP"
- ✅ 装 MiniMax web_search MCP（`claude mcp add`），连接成功
- ✅ 读 4 处源码拿到 Day 1 事实（query.ts / Tool.ts / services/compact / QueryGuard.ts）
- ✅ 把 `.study-state.json` 复制到仓库 `学习进度/state.json`
- ✅ 把 `我的学习计划.md` 复制到仓库根
- ⚠️ **API Key 暴露在对话历史**（已 revoke 提示）

### 本次没做什么
- ❌ Day 1 讲义未出（讲义目录 `学习进度/讲义/` 已建但空）
- ❌ Ultracode 真实机制没真正验证（要等新会话用 web_search 搜）
- ❌ 状态机改进方案（备份+显式事件钩子）没落地
- ❌ 没给 Day 1 出自测题

### 下次第一动作（按顺序）
1. 读 `学习进度/state.json` 同步进度
2. 调 web_search 搜："ultracode minimax"、"ultracode anthropic"、"claude code workflow mode"
3. 把搜索证据给我看，更新 Ultracode 真实机制
4. 基于源码事实重写 Day 1 讲义（保存到 `学习进度/讲义/Day-01-...md`）
5. 出 2-3 道自测题

### 待办
- [ ] 验证 Ultracode 真实机制
- [ ] Day 1 讲义
- [ ] Day 1 自测题
- [ ] 状态机改进方案

### 文件位置速查
| 文件 | 仓库内路径 | 仓库外路径 |
|------|----------|----------|
| 状态机 | `学习进度/state.json` | `e:\学术\Agent学习\.study-state.json`（实时源） |
| 学习计划 | `我的学习计划.md` | （已搬进仓库，仓库外无） |
| 讲义目录 | `学习进度/讲义/` | （待写） |
| 交接历史 | `学习进度/handoff-history.md` | （本文） |
| 主指南 | `Claude Code 架构全景学习指南.md` | （仓库已有） |

### 关键警告
- API key `sk-cp-...JxkBsidET0MLOJCo5Z5AzQHOuPp1eJj8` 已暴露在对话历史——**必须 revoke + 重生**
- `.claude.json` 在 `~/.claude.json`（仓库**外**）——已含新 MCP 配置
- 任何 `.bak.*` 文件全在仓库**外**——不会被 push