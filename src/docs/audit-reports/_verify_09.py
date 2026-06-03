#!/usr/bin/env python3
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
text = (ROOT / "docs/source-code-analysis/infrastructure/09-utils-root-gap-fill.md").read_text(
    encoding="utf-8"
)
entries = re.findall(r"^## `(utils/[^`]+)` \((\d+) lines\)", text, re.M)
errors = []
for path, doc_lines in entries:
    p = ROOT / path
    actual = sum(1 for _ in open(p, encoding="utf-8", errors="replace"))
    if int(doc_lines) != actual:
        errors.append((path, doc_lines, actual))
print(f"Total entries: {len(entries)}")
print(f"Line count errors: {len(errors)}")
for e in errors[:10]:
    print(e)
