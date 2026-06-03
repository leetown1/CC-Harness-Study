# Claude Code Source Code Analysis Archive

## Project Overview

**Claude Code** is a TypeScript/Bun-based CLI AI coding assistant built by Anthropic. It runs in the terminal using React/Ink for its TUI (Terminal User Interface) and communicates with Anthropic's Claude API to provide agentic AI assistance for software engineering tasks. The tool supports interactive REPL mode, headless/batch mode, SDK SDH mode, direct-connect sessions, and remote bridge sessions (CCR). It features tools for file editing, bash execution, web fetching, search, agent task delegation, MCP integration, and more.

## Quick Stats

| Metric | Count |
|--------|-------|
| Total TypeScript/TSX files | 1,884 |
| Total lines of code | ~513,216 |
| `.ts` files | 1,332 |
| `.tsx` files | 552 |
| Root-level source files | 18 files, 11,972 lines |
| Directories (non-test) | 34 |
| Feature flags (`feature()`) | 90 unique flags |
| CLI options in `main.tsx` | 60+ |
| Source code analysis docs | **41 documents** (39 core + 2 gap-fill appendices) |
| Coverage of source files | **1,884 files** — tracked in [`coverage_matrix.json`](../../coverage_matrix.json) |

### Coverage Tiers

| Tier | Meaning | Verification |
|------|---------|--------------|
| **Verified behavior-level** | `### \`path\` (N lines)`` entry with exports, flow, boundaries | `verified: true` in coverage matrix |
| **Table-only** | Mentioned in directory tables or inline lists | Legacy; being upgraded to behavior |
| **Generated** | `types/generated/*` — protobuf output, no line-by-line analysis | Documented as generated |

Run regression: `python docs/verify_all.py` from repo root.

See [audit reports](../../audit-reports/) for module-by-module diff summaries.

## Complete Directory Tree

```
src/ (root)                   18 files   11,972 lines     CLI entry, setup, query engine, task/tool registries
├── assistant/                 1 file        87 lines     KAIROS assistant session history
├── bootstrap/                 1 file     1,758 lines     Global state singleton (AppState-like)
├── bridge/                   31 files  12,613 lines     Remote bridge (CCR) infrastructure
├── buddy/                     6 files    1,300 lines      Companion buddy/animated sprite system
├── cli/                      19 files  12,355 lines     CLI transport layer, structured I/O, CCR client
│   ├── handlers/              6 files                    CLI subcommand handlers (agents, auth, mcp, etc.)
│   └── transports/            7 files                    WebSocket, SSE, hybrid transports, event uploader
├── commands/                189 files  26,507 lines     Slash-command implementations (110 command implementations; 79 .tsx UI modules)
├── components/              389 files   81,892 lines     React/Ink UI components (TUI widgets)
├── constants/                21 files    2,648 lines      Magic strings, prompts, limits, product config
├── context/                   9 files    1,013 lines      React context providers (stats, modals, voice, etc.)
├── coordinator/               1 file       369 lines      Coordinator agent mode (multi-agent orchestration)
├── entrypoints/               8 files    4,052 lines      Program entry points (init, CLI, MCP, SDK types)
│   └── sdk/                   3 files                    SDK schemas and types for external API
├── hooks/                   104 files   19,232 lines     React hooks for UI behavior and state management
├── ink/                      96 files   19,859 lines      Custom fork of Ink (React-for-CLI rendering engine)
│   ├── components/                                       Core Ink components (Box, Text, Button, Link, Ansi)
│   ├── events/                                           Event system (input, click, focus, terminal focus)
│   ├── hooks/                                            Low-level Ink hooks (use-input, use-app, etc.)
│   ├── layout/                                           Yoga layout engine integration
│   └── termio/                                           Terminal I/O, OSC codes, raw mode handling
├── keybindings/              14 files   3,161 lines      Customizable keybinding system (parser, resolver, schema)
├── memdir/                    8 files    1,736 lines      Memory directory (CLAUDE.md scanning/loading)
├── migrations/               11 files      603 lines      Config migration scripts (model renames, settings)
├── moreright/                 1 file        26 lines     "MoreRight" feature hook
├── native-ts/                 4 files    4,081 lines      Native-compiled TypeScript (color-diff, file-index, yoga)
│   ├── color-diff/                                       Fast color-coded diff rendering
│   ├── file-index/                                       Native file indexing
│   └── yoga-layout/                                      Yoga layout engine bindings
├── outputStyles/              1 file        98 lines     Output style definitions loader
├── plugins/                   2 files       182 lines     Plugin system core (builtin plugins, registry)
├── query/                     4 files       652 lines     Query configuration, deps, stop hooks, token budget
├── remote/                    4 files     1,127 lines     Remote session management (WebSocket, permission bridge)
├── schemas/                   1 file       222 lines      Hook event schemas (JSON Schema definitions)
├── screens/                   3 files     5,980 lines      Top-level screens (REPL, Doctor, ResumeConversation)
├── server/                    3 files       358 lines      Direct-connect server mode (IDE integration)
├── services/                130 files  53,683 lines      Service layer — API, analytics, MCP, compaction, etc.
├── skills/                   20 files    4,066 lines      Skill system (bundled skills, skill loading, MCP skills)
├── state/                     6 files    1,191 lines      AppState store, selectors, change observers
├── tasks/                    12 files    3,290 lines      Asynchronous task execution system
├── tools/                   184 files  50,863 lines      Tool implementations (149 .ts + 35 .tsx; Bash, FileEdit, Agent, WebFetch, etc.)
├── types/                    11 files    3,446 lines      Shared TypeScript type definitions
│   └── generated/             4 files    1,375 lines      Generated protobuf/types from external sources
├── upstreamproxy/             2 files      740 lines      Upstream proxy relay for remote sessions
├── utils/                   564 files 180,487 lines     Utility functions — the largest single directory (298 root + 266 subdir)
│   └── plugins/              44 files  20,522 lines     Plugin management utilities (loader, cache, registry)
├── vim/                       5 files    1,513 lines      Vim-mode keybinding implementation
└── voice/                     1 file        54 lines    Voice mode feature gate
```

## Document Index (42 documents)

### Gap-Fill & Catalog (Audit 2026-05-23)

| # | Document | Description |
|---|----------|-------------|
| GF1 | [infrastructure/09-utils-root-gap-fill.md](./infrastructure/09-utils-root-gap-fill.md) | Behavior-level entries for 298 utils root `.ts` files |
| GF2 | [services-layer/07-services-unverified-fill.md](./services-layer/07-services-unverified-fill.md) | 18 formerly unverified services — verified behavior entries |
| GF3 | [10-full-file-catalog.md](./10-full-file-catalog.md) | Behavior stubs for remaining files without dedicated `###` headings |
| — | [`../../coverage_matrix.json`](../../coverage_matrix.json) | Per-file coverage tracking (1884 files) |
| — | [`../../audit-reports/`](../../audit-reports/) | Module audit diff reports + FINAL-SIGNOFF |

### System Overview & Entry Points
| # | Document | Description |
|---|----------|-------------|
| 01 | [01-system-overview.md](./01-system-overview.md) | Architecture layers, full directory walkthrough, dependency map, startup flow, design patterns, feature flags |
| 02 | [02-entry-layer.md](./02-entry-layer.md) | `main.tsx` (4684 lines), `entrypoints/`, `cli/`, `bootstrap/`, `server/`, `coordinator/`, `upstreamproxy/` |

### Core Engine
| # | Document | Description |
|---|----------|-------------|
| 03 | [core-engine/01-query-engine.md](./core-engine/01-query-engine.md) | `QueryEngine.ts` (1295 lines), `query.ts` (1729 lines), `query/` configuration, StopHooks, token budget |

### Tool System (6 docs)
| # | Document | Description |
|---|----------|-------------|
| 04 | [tool-system/01-overview.md](./tool-system/01-overview.md) | Tool interface (Tool.ts, 754 lines), registry (tools.ts, 373 lines), 184 tool files (149 .ts + 35 .tsx) |
| 05 | [tool-system/02-file-tools.md](./tool-system/02-file-tools.md) | FileRead, FileEdit, FileWrite, Glob, Grep, Rename, Delete, FileSearch, etc. |
| 06 | [tool-system/03-shell-tools.md](./tool-system/03-shell-tools.md) | BashTool, PowerShellTool, AgentTool (Docker), BashInteractiveTool |
| 07 | [tool-system/04-search-tools.md](./tool-system/04-search-tools.md) | WebFetch, WebSearch, Task, NotebookEdit, ComputerUse, TextEditor, etc. |
| 08 | [tool-system/05-agent-tools.md](./tool-system/05-agent-tools.md) | AgentTool (spawn multi-agent), DeferToAgentTool, DelegateToAgentTool |
| 09 | [tool-system/06-other-tools.md](./tool-system/06-other-tools.md) | ScheduleCronTool, McpTool, McpAuthTool, SyntheticOutputTool, TestingPermissionTool, tools/shared/ |

### Command System (2 docs)
| # | Document | Description |
|---|----------|-------------|
| 10 | [command-system/01-commands.md](./command-system/01-commands.md) | Slash-command registry (commands.ts), 110 command implementations (189 ts/tsx files), command loader |
| 11 | [command-system/02-command-gap-fill.md](./command-system/02-command-gap-fill.md) | `commands/plugin/` (17 files, plugin management UI), `commands/review/`, `commands/extra-usage/`, `commands/rename/` |

### Services Layer (6 docs)
| # | Document | Description |
|---|----------|-------------|
| 12 | [services-layer/01-api-services.md](./services-layer/01-api-services.md) | Claude API client (`claude.ts`), API service, streaming, sessions, files, usage, admin |
| 13 | [services-layer/02-compact-services.md](./services-layer/02-compact-services.md) | Context compaction: Snip→Microcompact→Collapse→Autocompact, cleanup, warnings |
| 14 | [services-layer/03-mcp-services.md](./services-layer/03-mcp-services.md) | MCP client (`connectToServer`, `callMCPToolWithUrlElicitationRetry`), MCP agents, config parsers, hubs, runners |
| 15 | [services-layer/04-other-services.md](./services-layer/04-other-services.md) | Auth, analytics (Statsig/GrowthBook), plugins, SessionMemory, LSP, Compactor, AgentSummary, tips, PromptSuggestion |
| 16 | [services-layer/05-service-gap-fill.md](./services-layer/05-service-gap-fill.md) | LSP (7 files), remaining API/analytics/compact files, plugins CRUD, SessionMemory, AgentSummary |
| 17 | [services-layer/06-mcp-analytics-deep-dive.md](./services-layer/06-mcp-analytics-deep-dive.md) | MCP remaining (15 files: auth, channels, XAA, transports), all analytics (9 files: sink, metadata, Datadog, 1P events, GrowthBook) |

### Extension System (2 docs)
| # | Document | Description |
|---|----------|-------------|
| 18 | [extension-system/01-plugin-system.md](./extension-system/01-plugin-system.md) | Plugin definitions (BuiltinPluginDefinition), registry, Marketplace, lifecycle |
| 19 | [extension-system/02-skill-system.md](./extension-system/02-skill-system.md) | Skill loading, bundled skills, MCP skills, skill directory scanning, hook integration |

### UI Layer (11 docs)
| # | Document | Description |
|---|----------|-------------|
| 20 | [ui-layer/01-ink-engine.md](./ui-layer/01-ink-engine.md) | Custom Ink fork (96 files): reconciler, Yoga layout, terminal I/O, events, components |
| 21 | [ui-layer/02-components.md](./ui-layer/02-components.md) | Core UI components: App, REPL, Messages, VirtualMessageList, FullscreenLayout, MessageInput, etc. |
| 22 | [ui-layer/03-hooks.md](./ui-layer/03-hooks.md) | All 104 React hooks: useTextInput, useVoice, useKeybinding, useTypeahead, etc. |
| 23 | [ui-layer/04-components-supplement.md](./ui-layer/04-components-supplement.md) | PromptInput (14 files), Settings (4), Spinner (7), sandbox (5), shell (4), tasks (12), FeedbackSurvey (9) |
| 24 | [ui-layer/05-components-supplement-2.md](./ui-layer/05-components-supplement-2.md) | Design system (16 files), permissions (40+), CustomSelect (10), wizard (5) |
| 25 | [ui-layer/06-permissions-custom-components.md](./ui-layer/06-permissions-custom-components.md) | Permissions UI system, tool approvals, rules, AskUserQuestion, FilePermissionDialog, Bash/FileWrite/NotebookEdit/PowerShell permission requests, ComputerUseApproval |
| 26 | [ui-layer/07-large-components.md](./ui-layer/07-large-components.md) | LogSelector (1565 lines), Stats (1183), ConsoleOAuthFlow (623), ContextVisualization (486), TaskListV2, GlobalSearchDialog, RemoteEnvironmentDialog, ResumeTask, QuickOpenDialog, Onboarding, MCPServerDesktopImportDialog, DesktopHandoff, messageActions, Messages, VirtualMessageList, FullscreenLayout |
| 27 | [ui-layer/08-large-hooks.md](./ui-layer/08-large-hooks.md) | useTypeahead (1304), useVoice (1086), useInboxPoller (883), useReplBridge (704), useVirtualScroll (697), useRemoteSession, useTextInput, useVoiceIntegration, useManagePlugins, useHistorySearch, useVimInput, usePasteHandler, useCancelRequest, useCanUseTool, useSwarmPermissionPoller |
| 28 | [ui-layer/09-messages-mcp-components.md](./ui-layer/09-messages-mcp-components.md) | Messages (33 files), UserToolResultMessage (8), MCP components (13 + 1 util), LogoV2 (15 files) |
| 29 | [ui-layer/10-remaining-components.md](./ui-layer/10-remaining-components.md) | Permission subcomponents (21 files: AskUserQuestion, FilePermissionDialog, Bash, FileWrite, NotebookEdit, PowerShell, ComputerUseApproval), FeedbackSurvey (9), Hooks config menu (6) |
| 30 | [ui-layer/11-remaining-components-2.md](./ui-layer/11-remaining-components-2.md) | New agent creation wizard (13 files), HelpV2 (3), StructuredDiff (3), Teams (2), Memory (2), Skills (1), single-file components (7) |

### Infrastructure (8 docs)
| # | Document | Description |
|---|----------|-------------|
| 31 | [infrastructure/01-bridge-system.md](./infrastructure/01-bridge-system.md) | Bridge mode (31 files): REPL bridge, session runner, remote file system, AgentBridge |
| 32 | [infrastructure/02-state-types-constants.md](./infrastructure/02-state-types-constants.md) | AppState store (6 files), types (11), constants (21), migrations (11), schemas (1) |
| 33 | [infrastructure/03-keybindings-vim-voice.md](./infrastructure/03-keybindings-vim-voice.md) | Keybindings (14 files), Vim mode (5), Voice mode, native-ts (4 files) |
| 34 | [infrastructure/04-memory-system.md](./infrastructure/04-memory-system.md) | memdir (8 files), CLAUDE.md scanning/parsing/loading, memory read/write |
| 35 | [infrastructure/05-context-context.md](./infrastructure/05-context-context.md) | React context providers (9): stats, modals, voice, theme, focus, tool use history |
| 36 | [infrastructure/06-remote-tasks-screens.md](./infrastructure/06-remote-tasks-screens.md) | Remote (4), Tasks (12: LocalShell/LocalAgent/RemoteAgent/DreamTask), Screens (3), Buddy (6) |
| 37 | [infrastructure/07-utils-layer.md](./infrastructure/07-utils-layer.md) | Utils overview (564 files): bash parser, serialization, permissions, telemetry, swarm, settings, etc. |
| 38 | [infrastructure/08-utils-hooks-task-subprocesses.md](./infrastructure/08-utils-hooks-task-subprocesses.md) | utils/hooks/ (17: hook execution, SSRF guard, skill hooks), utils/task/ (5: output, framework, SDK progress), utils/teleport/ (4), utils/background/remote/ (2), tools/shared/ (2), services/tips/ (3), services/PromptSuggestion/ (2), single-file gap fills |

## Reading Order Recommendations

### For New Contributors

1. Start with **[01-system-overview.md](./01-system-overview.md)** for the big picture
2. Read `main.tsx` (4,684 lines) — the CLI entry point that ties everything together
3. Study `QueryEngine.ts` and `query.ts` — the core conversation loop
4. Understand `Tool.ts` and `tools.ts` — the tool interface and registry
5. Examine `commands.ts` — the slash-command system
6. Read `setup.ts` and `entrypoints/init.ts` — startup and initialization

### For Feature Developers

1. **[01-system-overview.md](./01-system-overview.md)** — architecture and dependency map
2. `main.tsx` lines 585–856 (`main()`) and 884–4513 (`run()` / Commander setup) — the CLI entry point that ties everything together
3. The relevant tool/command/hook directory for your feature
4. `constants/prompts.ts` — system prompt assembly with feature-gated sections
5. `services/analytics/growthbook.ts` — GrowthBook integration for feature flagging

### For Architecture Study

1. **[01-system-overview.md](./01-system-overview.md)** — layer diagram and module descriptions
2. Trace startup: `main.tsx` → `entrypoints/init.ts` → `setup.ts` → `bridge/bridgeMain.ts` or `replLauncher.tsx`
3. Follow query path: `QueryEngine.ts` → `query.ts` → `services/api/claude.ts` → response → tool dispatch → `tools/`
4. Understand state: `state/AppStateStore.ts` → `state/selectors.ts` → `state/onChangeAppState.ts`
5. Examine rendering: `ink/root.ts` → `ink/reconciler.ts` → `ink/renderer.ts` → `screens/REPL.tsx`

## Technology Stack

| Layer | Technology |
|-------|------------|
| Language | TypeScript 5.x |
| Runtime | Bun (primary), Node.js 18+ (compatible) |
| CLI Framework | Commander.js (@commander-js/extra-typings) |
| TUI Framework | Custom fork of Ink (React-for-terminal) |
| Layout Engine | Yoga Layout (native bindings via `native-ts/yoga-layout/`) |
| UI Framework | React 18 (with hooks and context) |
| API Client | @anthropic-ai/sdk |
| Schema Validation | Zod v4 |
| Serialization | Protocol Buffers (protobuf) |
| Analytics | Statsig + GrowthBook |
| Feature Flags | GrowthBook + bun:bundle dead-code elimination |
| Terminal Rendering | ANSI escape codes, raw terminal mode |
| MCP Protocol | @modelcontextprotocol/sdk |
| Concurrent Build | ESLint (via biome-ignore markers), custom bundler |
| Package Manager | Bun (with npm compatibility) |
| Testing | Vitest |
| CI | GitHub Actions |
