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

---

## 会话 #2 · 2026-06-16

### 本次做了什么
- ✅ `git pull` 拉下远端新提交（`51a71d5..6f4f831`）—— 状态机 + 学习计划 + .gitignore 首次同步到本地
- ✅ web_search 搜了 3 个 Ultracode 查询，拿到充分证据（CSDN 逐梦苍穹三篇深度文）
- ✅ **写 Day 1 讲义**：`学习进度/讲义/Day-01-Harness与六大支柱.md`（新人友好版，比主指南 Part 1 更精炼）
- ✅ **出 Day 1 自测题 3 道**：`学习进度/讲义/Day-01-自测.md`（概念题 + Fail-Closed 设计题 + 反直觉应用题）
- ✅ 更新 state.json：
  - `current_day: null → 1`
  - `day_1.stage: not_started → lecture_ready`
  - `lecture_artifact` / `quiz_artifact` 指向新文件
  - `review_queue` 加入 day_1（2026-06-23 复习）
  - `stats.days_lecture_ready: 0 → 1`，`current_streak_days: 0 → 1`
  - `transitions_log` 追加 `day_1_lecture_ready` 事件
  - `session_handoff` 字段重写为会话 #2 视角

### 本次没做什么
- ❌ Day 1 批改未做（等用户答完 3 道题）
- ❌ Ultracode 没讲（用户明确说"我现在没要你讲 ultracode"——已封存到 memory，不进 Day 1 讲义）
- ❌ 状态机方案改进（备份+显式事件钩子）—— 仍未做
- ❌ API Key revoke —— 用户仍未处理

### 关键纠正（重要，下次别再犯）
- ⚠️ **第一次**：用 `git status` + `git log @{u}..HEAD` 就下结论"完全对齐"——但没先 `git fetch`，本地跟踪引用是陈的。**正确顺序**：先 `fetch` 再 `log @{u}..HEAD`。
- ⚠️ **第二次**：搜完 Ultracode 之后想顺便讲清楚——但用户明确说不要。**教训**：carryover 里的待办如果用户已经明确放弃，立即从 carryover 移除，别再拉回主线。

### 下次第一动作（按顺序）
1. 读 state.json 同步进度（current_day=1, day_1.stage=lecture_ready）
2. 等用户发 Day 1 自测题答案
3. 逐题批改 + 追问，**不要直接给标准答案**——先看用户怎么想的
4. 批改后推进 day_1：lecture_ready → mastered（满分）/ needs_re_read（部分对）
5. 启动 Day 2：读主指南 Part 15 + 结语 + 浏览仓库目录结构

### 文件位置速查（会话 #2 新增）
| 文件 | 路径 | 状态 |
|------|------|------|
| Day 1 讲义 | `学习进度/讲义/Day-01-Harness与六大支柱.md` | ✅ 已写 |
| Day 1 自测题 | `学习进度/讲义/Day-01-自测.md` | ✅ 已出 |
| 状态机 | `学习进度/state.json` | ✅ day_1 → lecture_ready |

### 待办（下个会话继续）
- [ ] 批改 Day 1 自测题
- [ ] Day 2 讲义（Part 15 + 结语 + 仓库地图）
- [ ] Day 2 自测题
- [ ] 状态机方案改进（备份+显式事件钩子）
- [ ] 【长期】API Key revoke + 重生