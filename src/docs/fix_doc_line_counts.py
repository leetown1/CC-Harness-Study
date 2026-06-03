#!/usr/bin/env python3
"""Update line count claims in docs/source-code-analysis to match actual source."""
import re
from pathlib import Path

SRC = Path(__file__).resolve().parent.parent
DOCS = SRC / "docs" / "source-code-analysis"

src_files: dict[str, int] = {}
for p in SRC.rglob("*"):
    if p.suffix not in (".ts", ".tsx"):
        continue
    if "docs" in p.parts or "概述" in str(p):
        continue
    rel = p.relative_to(SRC).as_posix()
    src_files[rel] = sum(1 for _ in open(p, encoding="utf-8", errors="replace"))


def resolve_path(fpath: str) -> str | None:
    candidates = [fpath, fpath.replace("src/", "")]
    for c in candidates:
        if c in src_files:
            return c
    base = Path(fpath).name
    matches = [k for k in src_files if k.endswith("/" + base) or k == base]
    if len(matches) == 1:
        return matches[0]
    return None


PATTERNS = [
    # `file.ts` (123 lines) or (~123 lines)
    re.compile(
        r"(`(?:[\w./-]+\.(?:ts|tsx))`)\s*\((~?)(\d{1,5})\s*lines?\)",
        re.IGNORECASE,
    ),
    # file.ts (123 lines) without backticks at start of heading
    re.compile(
        r"(?<![`\w])([\w./-]+\.(?:ts|tsx))\s*\((~?)(\d{1,5})\s*lines?\)",
        re.IGNORECASE,
    ),
    # **File location:** `src/file.ts` (123 lines)
    re.compile(
        r"(\*\*File location:\*\*\s*`(?:src/)?([\w./-]+\.(?:ts|tsx))`)\s*\((~?)(\d{1,5})\s*lines?\)",
        re.IGNORECASE,
    ),
]


def replace_line_count(match: re.Match, group_file_idx: int, group_tilde_idx: int, group_num_idx: int) -> str:
    fpath = match.group(group_file_idx).strip("`")
    if fpath.startswith("**File location:**"):
        inner = re.search(r"`(?:src/)?([\w./-]+\.(?:ts|tsx))`", fpath)
        fpath = inner.group(1) if inner else fpath
    resolved = resolve_path(fpath)
    if not resolved:
        return match.group(0)
    actual = src_files[resolved]
    claimed = int(match.group(group_num_idx))
    if abs(actual - claimed) <= max(3, claimed * 0.02):
        return match.group(0)
    tilde = match.group(group_tilde_idx) if group_tilde_idx else ""
    prefix = match.group(0).split("(")[0]
    return f"{prefix}({tilde}{actual} lines)"


def fix_file(path: Path) -> int:
    text = path.read_text(encoding="utf-8")
    original = text
    changes = 0

    def sub_pattern(pat, file_idx, tilde_idx, num_idx):
        nonlocal text, changes

        def repl(m):
            nonlocal changes
            new = replace_line_count(m, file_idx, tilde_idx, num_idx)
            if new != m.group(0):
                changes += 1
            return new

        text = pat.sub(repl, text)

    sub_pattern(PATTERNS[0], 1, 2, 3)
    sub_pattern(PATTERNS[1], 1, 2, 3)

    # File location pattern - special handling
    def repl_loc(m):
        nonlocal changes
        fpath = m.group(2)
        resolved = resolve_path(fpath)
        if not resolved:
            return m.group(0)
        actual = src_files[resolved]
        claimed = int(m.group(4))
        if abs(actual - claimed) <= max(3, claimed * 0.02):
            return m.group(0)
        changes += 1
        tilde = m.group(3)
        return f"**File location:** `src/{resolved}` ({tilde}{actual} lines)"

    text = PATTERNS[2].sub(repl_loc, text)

    if text != original:
        path.write_text(text, encoding="utf-8")
    return changes


total = 0
for md in sorted(DOCS.rglob("*.md")):
    n = fix_file(md)
    if n:
        print(f"  {md.name}: {n} updates")
        total += n
print(f"Total updates: {total}")
