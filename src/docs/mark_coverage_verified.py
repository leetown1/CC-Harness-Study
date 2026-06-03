#!/usr/bin/env python3
"""Rebuild coverage matrix and mark files verified when they have behavior entries in docs."""
from __future__ import annotations

import json
import re
import subprocess
import sys
from datetime import date
from pathlib import Path

DOCS_DIR = Path(__file__).resolve().parent
SRC = DOCS_DIR.parent
MATRIX = DOCS_DIR / "coverage_matrix.json"
SCA = DOCS_DIR / "source-code-analysis"

BEHAVIOR_HEADING = re.compile(
    r"^###\s+(?:[\d.]+\s+)?`?(?:src/)?([\w./-]+\.(?:ts|tsx))`?",
    re.MULTILINE,
)


def resolve_path(fpath: str, src_files: set[str]) -> str | None:
    fpath = fpath.replace("src/", "")
    if fpath in src_files:
        return fpath
    base = fpath.rsplit("/", 1)[-1]
    matches = [k for k in src_files if k.endswith("/" + base) or k == base]
    if len(matches) == 1:
        return matches[0]
    return None


def main() -> None:
    subprocess.run([sys.executable, str(DOCS_DIR / "build_coverage_matrix.py")], check=True)
    matrix: dict = json.loads(MATRIX.read_text(encoding="utf-8"))
    today = date.today().isoformat()

    behavior_files: set[str] = set()
    src_files = set(matrix.keys())
    for md in SCA.rglob("*.md"):
        text = md.read_text(encoding="utf-8")
        for m in BEHAVIOR_HEADING.finditer(text):
            rel = resolve_path(m.group(1), src_files)
            if rel and rel in matrix:
                behavior_files.add(rel)

    for rel, entry in matrix.items():
        if rel in behavior_files or entry.get("depth") == "generated":
            entry["depth"] = "generated" if rel.startswith("types/generated/") else "behavior"
            entry["verified"] = True
            entry["last_checked"] = today

    MATRIX.write_text(json.dumps(matrix, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    verified = sum(1 for v in matrix.values() if v.get("verified"))
    behavior = sum(1 for v in matrix.values() if v.get("depth") == "behavior")
    print(f"Updated matrix: {verified}/{len(matrix)} verified, {behavior} behavior depth")


if __name__ == "__main__":
    main()
