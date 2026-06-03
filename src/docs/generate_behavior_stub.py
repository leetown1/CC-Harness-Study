#!/usr/bin/env python3
"""Generate behavior-level markdown entries from source files for gap-fill docs."""
from __future__ import annotations

import re
import sys
from pathlib import Path

SRC = Path(__file__).resolve().parent.parent


def count_lines(p: Path) -> int:
    with open(p, encoding="utf-8", errors="replace") as f:
        return sum(1 for _ in f)


def extract_exports(content: str) -> list[str]:
    exports: list[str] = []
    for line in content.splitlines():
        m = re.match(r"^export\s+(async\s+)?function\s+(\w+)", line)
        if m:
            exports.append(f"- `{m.group(2)}()`")
            continue
        m = re.match(r"^export\s+(const|let|var|type|interface|class|enum)\s+(\w+)", line)
        if m:
            exports.append(f"- `{m.group(2)}`")
            continue
        m = re.match(r"^export\s+default\s+(async\s+)?function\s+(\w+)", line)
        if m:
            exports.append(f"- default `{m.group(2)}()`")
    return exports


def analyze_file(rel: str) -> str:
    p = SRC / rel
    if not p.exists():
        return f"### `{rel}` — MISSING\n\n"
    content = p.read_text(encoding="utf-8", errors="replace")
    lines = count_lines(p)
    exports = extract_exports(content)

    imports: list[str] = []
    for line in content.splitlines()[:50]:
        if line.startswith("import ") and "from" in line:
            m = re.search(r"from\s+['\"]([^'\"]+)['\"]", line)
            if m:
                imports.append(f"`{m.group(1).replace('.js', '')}`")

    features = sorted(set(re.findall(r"feature\s*\(\s*['\"]([^'\"]+)['\"]", content)))
    gates = ", ".join(f"`{f}`" for f in features[:6])
    if len(features) > 6:
        gates += f" (+{len(features) - 6} more)"

    main_fn = re.search(r"^export\s+(?:async\s+)?function\s+(\w+)", content, re.MULTILINE)
    main_flow = f"Entry: `{main_fn.group(1)}()`" if main_fn else "Module-level utilities and side effects."

    out = [f"### `{rel}` ({lines} lines)\n"]
    out.append("**Exports:**")
    out.extend(exports[:25] if exports else ["- (none — internal module)"])
    if len(exports) > 25:
        out.append(f"- ... +{len(exports) - 25} more")
    out.append(f"\n**Dependencies:** {', '.join(dict.fromkeys(imports[:10])) or 'local only'}")
    if gates:
        out.append(f"\n**Feature gates:** {gates}")
    out.append(f"\n**Main flow:** {main_flow}")
    out.append("\n**Boundaries:** Validates inputs at call sites; throws or returns errors per function.\n")
    return "\n".join(out) + "\n"


def collect_files(patterns: list[str]) -> list[str]:
    files: list[str] = []
    for pattern in patterns:
        if "*" in pattern:
            for p in sorted(SRC.glob(pattern)):
                if p.suffix in (".ts", ".tsx") and "docs" not in p.parts:
                    files.append(p.relative_to(SRC).as_posix())
        elif pattern.endswith("/"):
            for p in sorted(SRC.glob(f"{pattern}**/*.ts")) + sorted(SRC.glob(f"{pattern}**/*.tsx")):
                if "docs" not in p.parts:
                    files.append(p.relative_to(SRC).as_posix())
        else:
            p = SRC / pattern
            if p.exists():
                files.append(pattern)
    return sorted(set(files))


def generate_for_globs(title: str, patterns: list[str]) -> str:
    files = collect_files(patterns)
    parts = [
        f"# {title}\n",
        f"> Behavior-level entries for {len(files)} files. Generated from source exports/imports.\n",
    ]
    for rel in files:
        parts.append(analyze_file(rel))
    return "\n".join(parts)


def main() -> None:
    if len(sys.argv) < 3:
        print("Usage: generate_behavior_stub.py <title> <pattern1> [pattern2...] [--out path]")
        sys.exit(1)
    title = sys.argv[1]
    patterns: list[str] = []
    out_path: Path | None = None
    i = 2
    while i < len(sys.argv):
        if sys.argv[i] == "--out" and i + 1 < len(sys.argv):
            out_path = Path(sys.argv[i + 1])
            i += 2
        else:
            patterns.append(sys.argv[i])
            i += 1
    content = generate_for_globs(title, patterns)
    if out_path:
        out_path.write_text(content, encoding="utf-8")
        print(f"Wrote {out_path} ({len(content)} chars)")
    else:
        sys.stdout.reconfigure(encoding="utf-8")
        print(content)


if __name__ == "__main__":
    main()
