#!/usr/bin/env python3
"""Generate behavior stubs for all source files missing ### headings."""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

SRC = Path(__file__).resolve().parent.parent
DOCS = Path(__file__).resolve().parent / "source-code-analysis"
MATRIX = Path(__file__).resolve().parent / "coverage_matrix.json"
OUT = DOCS / "10-full-file-catalog.md"

sys.path.insert(0, str(Path(__file__).resolve().parent))
from generate_behavior_stub import analyze_file  # noqa: E402

HEADING = re.compile(r"^###\s+`([\w./-]+\.(?:ts|tsx))`", re.MULTILINE)


def main() -> None:
    covered: set[str] = set()
    for md in DOCS.rglob("*.md"):
        if md.name == "10-full-file-catalog.md":
            continue
        for m in HEADING.finditer(md.read_text(encoding="utf-8")):
            covered.add(m.group(1))

    all_files = sorted(
        p.relative_to(SRC).as_posix()
        for p in SRC.rglob("*")
        if p.suffix in (".ts", ".tsx") and "docs" not in p.parts and "概述" not in str(p)
    )
    missing = [f for f in all_files if f not in covered and not f.startswith("types/generated/")]

    parts = [
        "# Full File Catalog (Gap Fill)\n",
        f"> Behavior-level stubs for {len(missing)} files not covered by `###` headings elsewhere.\n",
    ]
    for rel in missing:
        parts.append(analyze_file(rel))

    OUT.write_text("\n".join(parts), encoding="utf-8")
    print(f"Wrote {OUT} with {len(missing)} entries ({len(covered)} already covered)")


if __name__ == "__main__":
    main()
