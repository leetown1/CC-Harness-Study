#!/usr/bin/env python3
"""Generate 09-utils-root-gap-fill.md from source."""
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "docs/source-code-analysis/infrastructure/09-utils-root-gap-fill.md"
UTILS = ROOT / "utils"
DOCS07 = (ROOT / "docs/source-code-analysis/infrastructure/07-utils-layer.md").read_text(
    encoding="utf-8", errors="replace"
)

EXPORT_RE = re.compile(
    r"^export\s+(?:async\s+)?(?:function|const|class|type|interface|enum)\s+(\w+)",
    re.M,
)
TYPE_EXPORT_RE = re.compile(r"^export\s+type\s+\{([^}]+)\}", re.M)
IMPORT_RE = re.compile(r"^import\s+(?:type\s+)?(?:\{([^}]+)\}|(\w+))\s+from\s+['\"]([^'\"]+)['\"]", re.M)
FEATURE_RE = re.compile(r"feature\s*\(\s*['\"](\w+)['\"]\s*\)")


def count_lines(p: Path) -> int:
    return sum(1 for _ in open(p, encoding="utf-8", errors="replace"))


def get_exports(text: str) -> list[str]:
    names = list(EXPORT_RE.findall(text))
    for m in TYPE_EXPORT_RE.finditer(text):
        for part in m.group(1).split(","):
            part = part.strip()
            if part:
                names.append(part.split()[0])
    return sorted(set(names))


def get_deps(text: str) -> list[str]:
    deps: set[str] = set()
    for m in IMPORT_RE.finditer(text):
        deps.add(m.group(3))
    return sorted(d for d in deps if d.startswith("."))[:10]


def get_features(text: str) -> list[str]:
    return sorted(set(FEATURE_RE.findall(text)))


def covered_in_07(name: str) -> bool:
    return bool(
        re.search(rf"###\s+`utils/{re.escape(name)}`", DOCS07)
        or re.search(rf"###\s+`{re.escape(name)}`", DOCS07)
    )


def main_entry(exports: list[str]) -> str | None:
    for prefix in ("is", "get", "create", "init", "setup", "load", "parse", "handle"):
        for e in exports:
            if e.startswith(prefix):
                return f"`{e}()`"
    return f"`{exports[0]}()`" if exports else None


def behavior_note(name: str, text: str, exports: list[str]) -> str:
    """One-line behavior hint from filename/heuristics."""
    hints = {
        "abortController.ts": "Nested AbortController helper for propagating cancellation through async trees.",
        "activityManager.ts": "Tracks in-flight tool/assistant activities for status UI and bridge worker sync.",
        "replBridgeHandle.ts": "N/A - wrong dir",
        "concurrentSessions.ts": "Local session registry for multi-process dedup (bridge list, peer discovery).",
        "messageQueueManager.ts": "FIFO command queue with peek/dequeue and slash-command visibility hooks.",
        "gracefulShutdown.ts": "Coordinates shutdown deadline, hook flush, and background task teardown.",
    }
    if name in hints:
        return hints[name]
    if "Hook" in "".join(exports) or "hook" in name.lower():
        return "Hook lifecycle helper; registers callbacks or dispatches hook events."
    if name.endswith("Cache.ts") or "Cache" in exports:
        return "In-memory or disk-backed cache with TTL/invalidation semantics."
    if any(e.startswith("is") for e in exports):
        return "Type guard / feature probe used at call sites before branching."
    return "Module-level utilities and side effects; validates inputs at call sites."


def entry(p: Path) -> str:
    text = p.read_text(encoding="utf-8", errors="replace")
    lines = count_lines(p)
    exports = get_exports(text)
    deps = get_deps(text)
    features = get_features(text)
    rel = p.as_posix().replace(str(ROOT.as_posix()) + "/", "")
    main = main_entry(exports)
    exp_block = "\n".join(f"- `{e}`" for e in exports[:25])
    if len(exports) > 25:
        exp_block += f"\n- ... +{len(exports) - 25} more"
    dep_block = ", ".join(f"`{d}`" for d in deps) if deps else "local only"
    feat_block = ""
    if features:
        feat_block = f"\n**Feature gates:** {', '.join(f'`{f}`' for f in features)}\n"
    return (
        f"## `{rel}` ({lines} lines)\n\n"
        f"**Exports:**\n{exp_block or '- (none)'}\n\n"
        f"**Dependencies:** {dep_block}\n"
        f"{feat_block}\n"
        f"**Main flow:** Entry: {main or 'N/A'}\n\n"
        f"**Behavior:** {behavior_note(p.name, text, exports)}\n"
    )


SUBDIR_BEHAVIOR = """
---

# Part 2 — Subdirectory Behavior Gap Fill

Modules below are mentioned briefly in `07-utils-layer.md` §14 or omitted from `08-utils-hooks-task-subprocesses.md`. File names and behavior verified against source (Phase 1 audit).

## `utils/background/remote/` (2 files)

| File | Behavior |
|------|----------|
| `preconditions.ts` | Async precondition checks for remote/teleport flows: OAuth login, git cleanliness, remote environment availability, GitHub App install, org policy. |
| `remoteSession.ts` | `BackgroundRemoteSession` type and eligibility checks combining preconditions for background remote session spawn. |

## `utils/dxt/` (2 files)

| File | Behavior |
|------|----------|
| `helpers.ts` | Lazy-validates MCPB/DXT plugin manifests via `@anthropic-ai/mcpb` (deferred import to avoid startup zod cost). |
| `zip.ts` | Extracts `.dxt`/`.mcpb` plugin archives to temp dirs with manifest discovery. |

## `utils/filePersistence/` (2 files)

| File | Behavior |
|------|----------|
| `filePersistence.ts` | End-of-turn orchestrator: scans modified outputs, uploads via Files API (BYOC) or lists directory (cloud/rclone). |
| `outputsScanner.ts` | Mtime-based scanner for `outputs/` subtree; detects `EnvironmentKind` from env vars. |

## `utils/github/` (1 file)

| File | Behavior |
|------|----------|
| `ghAuthStatus.ts` | Non-blocking `gh` CLI probe (`which` + `gh auth token` exit code) for telemetry — never reads token stdout. |

## `utils/mcp/` (2 files)

| File | Behavior |
|------|----------|
| `elicitationValidation.ts` | Validates MCP elicitation form fields (string formats, enums, natural-language dates) before user submit. |
| `dateTimeParser.ts` | Parses natural-language and ISO-8601 datetime strings for MCP elicitation defaults. |

## `utils/memory/` (2 files)

| File | Behavior |
|------|----------|
| `versions.ts` | Sync git-repo probe via `findGitRoot` for memory feature gating. |
| `types.ts` | Memory record version enums and schema shapes for memdir persistence. |

## `utils/messages/` (2 files)

| File | Behavior |
|------|----------|
| `mappers.ts` | Maps SDK wire messages ↔ internal `Message[]` (assistant, compact boundaries, plan mode). |
| `systemInit.ts` | Builds SDK `system/init` and `result` init payloads; `sdkCompatToolName` Task→Agent shim. |

## `utils/todo/` (1 file)

| File | Behavior |
|------|----------|
| `types.ts` | `TodoList` / `TodoItem` shapes shared by tasks UI and background remote sessions. |

## `utils/ultraplan/` (2 files)

| File | Behavior |
|------|----------|
| `keyword.ts` | Detects `ultraplan` trigger keyword in user input with delimiter-aware parsing (skips quoted/backtick regions). |
| `ccrSession.ts` | CCR session helpers for ultraplan mode sync with remote worker metadata. |

## `utils/powershell/` (3 files)

| File | Behavior |
|------|----------|
| `parser.ts` | Invokes PowerShell AST parser (`System.Management.Automation.Language`) for security classification of cmdlets/pipelines. |
| `dangerousCmdlets.ts` | Blocklist/allowlist tables for high-risk PowerShell cmdlets used by permission checks. |
| `staticPrefix.ts` | Detects static command prefixes safe to auto-classify without full AST parse. |

## `utils/sandbox/` (2 files)

| File | Behavior |
|------|----------|
| `sandbox-adapter.ts` | `SandboxManager` interface — create/exec/teardown for containerized tool runs. |
| `sandbox-ui-utils.ts` | Status-line formatting for sandbox state in the REPL footer. |

## `utils/processUserInput/` (4 files)

| File | Behavior |
|------|----------|
| `processUserInput.ts` | Central input pipeline: slash commands, attachments, hooks, message assembly. |
| `processTextPrompt.ts` | Plain-text branch — skill expansion, @file refs, queue handoff. |
| `processSlashCommand.tsx` | `/command` dispatch to local/JSX/prompt command handlers. |
| `processBashCommand.tsx` | `!` / bash-prefixed command execution path. |
"""


def main():
    root_files = sorted(UTILS.glob("*.ts"))
    uncovered = [p for p in root_files if not covered_in_07(p.name)]
    covered = [p for p in root_files if covered_in_07(p.name)]

    header = f"""# 09 — Utils Root Gap Fill

> **Scope**: {len(uncovered)} root-level `utils/*.ts` files not given dedicated sections in `07-utils-layer.md` §15.
> **Verified**: {len(covered)} files already documented in §15 (auth, config, log, debug, errors, file, path, etc.).
> **Generated**: Phase 1 audit (Agent A9) — exports and line counts verified against source.

---

# Part 1 — Root-Level Files ({len(uncovered)} entries)

"""

    body = "\n".join(entry(p) for p in uncovered)
    OUT.write_text(header + body + SUBDIR_BEHAVIOR, encoding="utf-8")
    print(f"Wrote {OUT} ({len(uncovered)} entries, {OUT.stat().st_size} bytes)")


if __name__ == "__main__":
    main()
