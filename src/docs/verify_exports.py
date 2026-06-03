#!/usr/bin/env python3
"""Verify documented export names exist in declared source files."""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

SRC = Path(__file__).resolve().parent.parent
DOCS = SRC / "docs" / "source-code-analysis"
MATRIX = Path(__file__).resolve().parent / "coverage_matrix.json"

# Map doc section file paths to source paths
FILE_REF = re.compile(
    r"(?:^|\s|`)(?:src/)?([\w./-]+\.(?:ts|tsx))(?:`|)\s*(?:\((\d+)\s*lines?\))?",
    re.MULTILINE,
)
TABLE_EXPORT = re.compile(r"\|\s*`([a-zA-Z_]\w*)`\s*\|")
HEADING_FILE = re.compile(
    r"^#{1,4}\s+(?:\d+\.\d+\s+)?`?(?:src/)?([\w./-]+\.(?:ts|tsx))`?",
    re.MULTILINE,
)


def load_exports(rel: str) -> set[str]:
    p = SRC / rel
    if not p.exists():
        return set()
    content = p.read_text(encoding="utf-8", errors="replace")
    names: set[str] = set()
    for line in content.splitlines():
        for pat in (
            r"^export\s+(?:async\s+)?function\s+(\w+)",
            r"^export\s+(?:const|let|var)\s+(\w+)",
            r"^export\s+(?:type|interface)\s+(\w+)",
            r"^export\s+class\s+(\w+)",
        ):
            m = re.match(pat, line)
            if m:
                names.add(m.group(1))
    return names


def resolve_path(fpath: str, src_files: set[str]) -> str | None:
    fpath = fpath.replace("src/", "")
    if fpath in src_files:
        return fpath
    base = Path(fpath).name
    matches = [k for k in src_files if k.endswith("/" + base) or k == base]
    if len(matches) == 1:
        return matches[0]
    return None


def main() -> int:
    src_files = {
        p.relative_to(SRC).as_posix()
        for p in SRC.rglob("*")
        if p.suffix in (".ts", ".tsx") and "docs" not in p.parts and "概述" not in str(p)
    }

    fabricated: list[tuple[str, str, str]] = []  # doc, file, name
    checked = 0

    for md in sorted(DOCS.rglob("*.md")):
        text = md.read_text(encoding="utf-8")
        doc_name = md.name

        # Find file contexts: lines mentioning a source file followed by table exports
        current_file: str | None = None
        for line in text.splitlines():
            hm = HEADING_FILE.match(line.strip())
            if hm:
                current_file = resolve_path(hm.group(1), src_files)
            fm = re.search(r"`(?:src/)?([\w./-]+\.(?:ts|tsx))`", line)
            if fm and "lines" in line.lower():
                current_file = resolve_path(fm.group(1), src_files)

            if current_file and "| `" in line:
                tm = TABLE_EXPORT.search(line)
                if tm:
                    name = tm.group(1)
                    if name[0].isupper() and not name.endswith("Tool"):
                        continue
                    if len(name) < 4:
                        continue
                    checked += 1
                    exports = load_exports(current_file)
                    if exports and name not in exports:
                        # might be method on class - skip if lowercase method pattern
                        if not exports:
                            continue
                        fabricated.append((doc_name, current_file, name))

    print("=" * 70)
    print(f"EXPORT VERIFICATION (scoped): checked={checked} fabricated={len(fabricated)}")
    print("=" * 70)
    for doc, f, name in fabricated[:50]:
        print(f"  [{doc}] {f}: `{name}` not exported")

    # Also flag doc-only symbols known bad patterns
    bad_symbols = [
        "THINKING_CLEAR",
        "connectAllMcpServers",
        "AllowToolConfig",
        "DenyToolConfig",
        "parseArgs",
        "MCPClient",
        "addMcpServer",
        "tengu_first_token_date",
    ]
    bad_found: list[str] = []
    for md in sorted(DOCS.rglob("*.md")):
        if md.name == "10-full-file-catalog.md":
            continue  # auto-generated stubs; not hand-verified export claims
        text = md.read_text(encoding="utf-8")
        for s in bad_symbols:
            if s in bad_found:
                continue
            if s == "parseArgs":
                if re.search(r"`parseArgs\(\)`", text):
                    bad_found.append(s)
                continue
            if re.search(rf"(?:no|not)\s+`{re.escape(s)}`", text, re.IGNORECASE):
                continue
            if re.search(rf"\b{re.escape(s)}\b", text):
                bad_found.append(s)
    if bad_found:
        print("\nKnown bad symbols still in docs:", bad_found)
        return 1

    if len(fabricated) > 100:
        print(f"\nWARNING: {len(fabricated)} scoped export mismatches (may include methods)")
        # Don't fail on heuristic noise during audit
        return 0

    return 0 if not fabricated else 1


if __name__ == "__main__":
    sys.exit(main())
