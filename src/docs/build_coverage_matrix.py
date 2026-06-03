#!/usr/bin/env python3
"""Build docs/coverage_matrix.json from source files and doc cross-references."""
from __future__ import annotations

import json
import re
from datetime import date
from pathlib import Path

SRC = Path(__file__).resolve().parent.parent
DOCS = SRC / "docs" / "source-code-analysis"
OUT = Path(__file__).resolve().parent / "coverage_matrix.json"

UNVERIFIED_SERVICES = {
    "services/toolUseSummary/toolUseSummaryGenerator.ts",
    "services/magicDocs/magicDocs.ts",
    "services/magicDocs/prompts.ts",
    "services/extractMemories/extractMemories.ts",
    "services/extractMemories/prompts.ts",
    "services/autoDream/autoDream.ts",
    "services/tips/tipRegistry.ts",
    "services/tips/tipScheduler.ts",
    "services/tips/tipHistory.ts",
    "services/PromptSuggestion/speculation.ts",
    "services/PromptSuggestion/promptSuggestion.ts",
    "services/settingsSync/index.ts",
    "services/settingsSync/types.ts",
    "services/policyLimits/index.ts",
    "services/policyLimits/types.ts",
    "services/remoteManagedSettings/index.ts",
    "services/oauth/index.ts",
    "services/teamMemorySync/index.ts",
}

DOC_MODULE_MAP: list[tuple[str, str]] = [
    ("", "01-system-overview.md"),
    ("entrypoints/", "02-entry-layer.md"),
    ("cli/", "02-entry-layer.md"),
    ("bootstrap/", "02-entry-layer.md"),
    ("server/", "02-entry-layer.md"),
    ("coordinator/", "02-entry-layer.md"),
    ("upstreamproxy/", "02-entry-layer.md"),
    ("QueryEngine.ts", "core-engine/01-query-engine.md"),
    ("query.ts", "core-engine/01-query-engine.md"),
    ("query/", "core-engine/01-query-engine.md"),
    ("tools/", "tool-system/"),
    ("Tool.ts", "tool-system/01-overview.md"),
    ("tools.ts", "tool-system/01-overview.md"),
    ("commands/", "command-system/"),
    ("commands.ts", "command-system/01-commands.md"),
    ("services/api/", "services-layer/01-api-services.md"),
    ("services/compact/", "services-layer/02-compact-services.md"),
    ("services/mcp/", "services-layer/03-mcp-services.md"),
    ("services/analytics/", "services-layer/06-mcp-analytics-deep-dive.md"),
    ("services/oauth/", "services-layer/06-mcp-analytics-deep-dive.md"),
    ("services/", "services-layer/04-other-services.md"),
    ("plugins/", "extension-system/01-plugin-system.md"),
    ("skills/", "extension-system/02-skill-system.md"),
    ("bridge/", "infrastructure/01-bridge-system.md"),
    ("state/", "infrastructure/02-state-types-constants.md"),
    ("types/", "infrastructure/02-state-types-constants.md"),
    ("constants/", "infrastructure/02-state-types-constants.md"),
    ("migrations/", "infrastructure/02-state-types-constants.md"),
    ("schemas/", "infrastructure/02-state-types-constants.md"),
    ("keybindings/", "infrastructure/03-keybindings-vim-voice.md"),
    ("vim/", "infrastructure/03-keybindings-vim-voice.md"),
    ("voice/", "infrastructure/03-keybindings-vim-voice.md"),
    ("native-ts/", "infrastructure/03-keybindings-vim-voice.md"),
    ("memdir/", "infrastructure/04-memory-system.md"),
    ("context/", "infrastructure/05-context-context.md"),
    ("remote/", "infrastructure/06-remote-tasks-screens.md"),
    ("tasks/", "infrastructure/06-remote-tasks-screens.md"),
    ("screens/", "infrastructure/06-remote-tasks-screens.md"),
    ("buddy/", "infrastructure/06-remote-tasks-screens.md"),
    ("assistant/", "infrastructure/06-remote-tasks-screens.md"),
    ("moreright/", "infrastructure/06-remote-tasks-screens.md"),
    ("outputStyles/", "infrastructure/02-state-types-constants.md"),
    ("utils/", "infrastructure/07-utils-layer.md"),
    ("components/", "ui-layer/"),
    ("hooks/", "ui-layer/"),
    ("ink/", "ui-layer/01-ink-engine.md"),
]


def count_lines(p: Path) -> int:
    with open(p, encoding="utf-8", errors="replace") as f:
        return sum(1 for _ in f)


def extract_exports(content: str) -> list[str]:
    names: list[str] = []
    patterns = [
        r"^export\s+(?:async\s+)?function\s+(\w+)",
        r"^export\s+(?:const|let|var)\s+(\w+)",
        r"^export\s+(?:type|interface)\s+(\w+)",
        r"^export\s+class\s+(\w+)",
        r"^export\s+enum\s+(\w+)",
        r"^export\s+default\s+(?:async\s+)?function\s+(\w+)",
    ]
    for line in content.splitlines():
        for pat in patterns:
            m = re.match(pat, line)
            if m:
                names.append(m.group(1))
                break
    return sorted(set(names))


def default_doc_refs(rel: str) -> list[str]:
    refs: list[str] = []
    for prefix, doc in DOC_MODULE_MAP:
        if prefix and (rel.startswith(prefix) or rel == prefix.rstrip("/")):
            refs.append(doc if doc.endswith(".md") else doc)
        elif not prefix and "/" not in rel:
            refs.append("01-system-overview.md")
    if rel.startswith("utils/") and rel.count("/") == 1:
        refs.append("infrastructure/09-utils-root-gap-fill.md")
    if rel in UNVERIFIED_SERVICES:
        refs.append("services-layer/07-services-unverified-fill.md")
    # dedupe preserve order
    seen: set[str] = set()
    out: list[str] = []
    for r in refs:
        if r not in seen:
            seen.add(r)
            out.append(r)
    return out or ["01-system-overview.md"]


def classify_depth(rel: str, basename: str, doc_text: str) -> str:
    if rel.startswith("types/generated/"):
        return "generated"
    # behavior indicators
    behavior_markers = [
        f"`{rel}`",
        f"`{basename}`",
        "**主流程**",
        "**Main flow**",
        "**Behavior**",
        "**Exports",
    ]
    if any(m in doc_text for m in behavior_markers):
        # check for more than table mention
        if re.search(rf"###?\s+.*{re.escape(basename)}", doc_text):
            return "behavior"
        if doc_text.count(basename) >= 3:
            return "behavior"
        return "table"
    if basename in doc_text or rel in doc_text:
        return "table"
    # partial: directory segment
    parts = rel.replace(".tsx", "").replace(".ts", "").split("/")
    if any(len(p) > 4 and p in doc_text for p in parts[:-1]):
        return "partial"
    return "none"


def find_doc_refs(rel: str, all_docs: dict[str, str]) -> list[str]:
    basename = Path(rel).name
    refs: list[str] = []
    for doc_path, text in all_docs.items():
        if rel in text or basename in text:
            refs.append(doc_path.replace("\\", "/"))
    if not refs:
        refs = default_doc_refs(rel)
    return sorted(set(refs))


def main() -> None:
    all_docs = {
        md.relative_to(DOCS).as_posix(): md.read_text(encoding="utf-8")
        for md in DOCS.rglob("*.md")
    }
    combined_doc = "\n".join(all_docs.values())

    matrix: dict[str, dict] = {}
    for p in sorted(SRC.rglob("*")):
        if p.suffix not in (".ts", ".tsx"):
            continue
        if "docs" in p.parts or "概述" in str(p):
            continue
        rel = p.relative_to(SRC).as_posix()
        content = p.read_text(encoding="utf-8", errors="replace")
        basename = p.name
        depth = classify_depth(rel, basename, combined_doc)
        refs = find_doc_refs(rel, all_docs)
        verified = depth == "behavior" and rel not in UNVERIFIED_SERVICES

        matrix[rel] = {
            "lines": count_lines(p),
            "doc_refs": refs,
            "depth": depth,
            "verified": verified,
            "exports": extract_exports(content),
            "last_checked": None,
        }

    OUT.write_text(json.dumps(matrix, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    depths: dict[str, int] = {}
    for v in matrix.values():
        depths[v["depth"]] = depths.get(v["depth"], 0) + 1
    print(f"Wrote {OUT} ({len(matrix)} files)")
    print("Depth breakdown:", depths)
    print("Verified:", sum(1 for v in matrix.values() if v["verified"]))


if __name__ == "__main__":
    main()
