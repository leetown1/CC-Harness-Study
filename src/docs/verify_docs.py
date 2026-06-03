#!/usr/bin/env python3
"""Verify docs/source-code-analysis claims against actual source code."""
import os
import re
from pathlib import Path
from collections import defaultdict

SRC = Path(__file__).resolve().parent.parent
DOCS = SRC / "docs" / "source-code-analysis"

def count_lines(p: Path) -> int:
    try:
        with open(p, encoding="utf-8", errors="replace") as f:
            return sum(1 for _ in f)
    except OSError:
        return -1

# Index source files
src_files: dict[str, int] = {}
for p in SRC.rglob("*"):
    if p.suffix not in (".ts", ".tsx"):
        continue
    if "docs" in p.parts or "概述" in str(p):
        continue
    rel = p.relative_to(SRC).as_posix()
    src_files[rel] = count_lines(p)

# Directory stats
dir_files: dict[str, int] = defaultdict(int)
dir_lines: dict[str, int] = defaultdict(int)
root_files = {}
for rel, lines in src_files.items():
    parts = rel.split("/")
    top = parts[0] if len(parts) > 1 else "(root)"
    dir_files[top] += 1
    dir_lines[top] += lines
    if len(parts) == 1:
        root_files[rel] = lines

# README tree parsing
readme = (DOCS / "README.md").read_text(encoding="utf-8")
tree_pat = re.compile(
    r"[├└]──\s+([\w/-]+)\s+(\d+)\s+files?\s+~?([\d,]+|\d+)\s+lines?"
)
tree_claims = tree_pat.findall(readme)

print("=" * 70)
print("1. README DIRECTORY TREE: FILE COUNT ACCURACY")
print("=" * 70)
for d, claimed_files, claimed_lines in tree_claims:
    actual = dir_files.get(d.split("/")[0], dir_files.get(d, 0))
    status = "OK" if str(actual) == claimed_files else "WRONG"
    print(f"  [{status}] {d:25} claimed={claimed_files:>4} actual={actual:>4}")

print(f"\n  Root files: claimed=18 actual={len(root_files)} lines claimed~11321 actual={sum(root_files.values())}")

# Line count claims from all docs
line_pat = re.compile(
    r"(?:^|[\s`(])([\w./-]+\.(?:ts|tsx))(?:[`'\"]|\s|\)|\|).{0,30}?(\d{2,5})\s*(?:lines|行)",
    re.MULTILINE | re.IGNORECASE,
)
paren_pat = re.compile(
    r"`([\w./-]+\.(?:ts|tsx))`\s*\((\d{1,5})\s*lines?\)",
    re.IGNORECASE,
)
tilde_pat = re.compile(
    r"`([\w./-]+\.(?:ts|tsx))`\s*\(~(\d{1,5})\s*lines?\)",
    re.IGNORECASE,
)

def resolve_path(fpath: str) -> str | None:
    candidates = [fpath, fpath.replace("src/", "")]
    for c in candidates:
        if c in src_files:
            return c
    base = os.path.basename(fpath)
    matches = [k for k in src_files if k.endswith("/" + base) or k == base]
    if len(matches) == 1:
        return matches[0]
    return None

claims: list[tuple[str, str, int, str]] = []
for md in sorted(DOCS.rglob("*.md")):
    text = md.read_text(encoding="utf-8")
    for pat in (paren_pat, tilde_pat, line_pat):
        for m in pat.finditer(text):
            claims.append((md.name, m.group(1), int(m.group(2)), pat.pattern[:20]))

# Deduplicate keeping worst mismatch
seen: dict[tuple[str, str], tuple] = {}
for doc, fpath, claimed, _ in claims:
    resolved = resolve_path(fpath)
    if not resolved:
        continue
    key = (doc, resolved)
    actual = src_files[resolved]
    diff = actual - claimed
    if key not in seen or abs(diff) > abs(seen[key][3]):
        seen[key] = (doc, resolved, claimed, diff, actual)

mismatches = [(v[0], v[1], v[2], v[4], v[3]) for v in seen.values() if abs(v[3]) > max(10, v[4] * 0.03)]
mismatches.sort(key=lambda x: -abs(x[4]))

print("\n" + "=" * 70)
print(f"2. LINE COUNT MISMATCHES (>10 lines or >3%): {len(mismatches)}")
print("=" * 70)
for doc, f, claimed, actual, diff in mismatches[:60]:
    print(f"  [{doc:35}] {f:45} doc={claimed:5} actual={actual:5} diff={diff:+5}")

# Export name verification - use pre-built index (O(exports) not O(exports × files))
export_index: set[str] = set()
ff_actual: set[str] = set()
for rel in src_files:
    try:
        content = (SRC / rel).read_text(encoding="utf-8", errors="replace")
    except OSError:
        continue
    for em in re.finditer(
        r"^export\s+(?:async\s+)?(?:function|const|let|var|type|interface|class|enum)\s+(\w+)",
        content,
        re.MULTILINE,
    ):
        export_index.add(em.group(1))
    for m in re.finditer(r"feature\s*\(\s*['\"]([^'\"]+)['\"]", content):
        ff_actual.add(m.group(1))

missing_exports = []
checked_exports = 0
for md in sorted(DOCS.rglob("*.md")):
    if md.name in ("README.md", "10-full-file-catalog.md"):
        continue  # skip auto-generated catalog
    text = md.read_text(encoding="utf-8")
    table_pat = re.compile(r"\|\s*`([a-zA-Z_]\w*)`\s*\|")
    for m in table_pat.finditer(text):
        name = m.group(1)
        if name[0].isupper() and not name.endswith("Tool"):
            continue
        if len(name) < 4:
            continue
        checked_exports += 1
        if name not in export_index:
            missing_exports.append((md.name, name))

print("\n" + "=" * 70)
print(f"3. EXPORT NAME CHECK (table backtick names): checked={checked_exports} not_found={len(missing_exports)}")
print("=" * 70)
for doc, name in missing_exports[:40]:
    print(f"  [{doc}] `{name}`")

# Feature flag count (computed during export index pass above)
print("\n" + "=" * 70)
print(f"4. FEATURE FLAGS: README claims 90, actual unique feature() strings: {len(ff_actual)}")
print("=" * 70)

# Tool count
tools_ts = sum(1 for k in src_files if k.startswith("tools/") and k.endswith(".ts"))
tools_tsx = sum(1 for k in src_files if k.startswith("tools/") and k.endswith(".tsx"))
print(f"\n5. TOOLS DIR: .ts={tools_ts} .tsx={tools_tsx} total={tools_ts+tools_tsx} (README: 184 files)")

# Commands count
cmd_ts = sum(1 for k in src_files if k.startswith("commands/") and k.endswith(".ts"))
cmd_tsx = sum(1 for k in src_files if k.startswith("commands/") and k.endswith(".tsx"))
print(f"6. COMMANDS DIR: .ts={cmd_ts} .tsx={cmd_tsx} total={cmd_ts+cmd_tsx} (README: 189 files, 110 .ts implementations)")

# Total stats
total_lines = sum(src_files.values())
ts_count = sum(1 for k in src_files if k.endswith(".ts"))
tsx_count = sum(1 for k in src_files if k.endswith(".tsx"))
print(f"\n7. TOTALS: files={len(src_files)} .ts={ts_count} .tsx={tsx_count} lines={total_lines}")
print(f"   README baseline: files=1884 .ts=1332 .tsx=552 lines~513216")

# Verify key file paths mentioned in README index exist
key_files = [
    "main.tsx", "QueryEngine.ts", "query.ts", "Tool.ts", "tools.ts", "commands.ts",
    "state/AppStateStore.ts", "state/selectors.ts", "state/onChangeAppState.ts",
    "ink/root.ts", "ink/reconciler.ts", "ink/renderer.ts", "screens/REPL.tsx",
    "services/api/claude.ts", "services/analytics/growthbook.ts", "constants/prompts.ts",
    "entrypoints/init.ts", "setup.ts", "bridge/bridgeMain.ts", "replLauncher.tsx",
]
print("\n8. KEY FILE PATH CHECK:")
for f in key_files:
    exists = f in src_files
    print(f"  {'OK' if exists else 'MISSING':7} {f}" + (f" ({src_files[f]} lines)" if exists else ""))
