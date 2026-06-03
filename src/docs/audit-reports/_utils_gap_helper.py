#!/usr/bin/env python3
"""Generate utils root gap-fill entries from source."""
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
UTILS = ROOT / "utils"
DOCS07 = (ROOT / "docs/source-code-analysis/infrastructure/07-utils-layer.md").read_text(
    encoding="utf-8", errors="replace"
)

EXPORT_RE = re.compile(
    r"^export\s+(?:async\s+)?(?:function|const|class|type|interface|enum)\s+(\w+)",
    re.M,
)
TYPE_EXPORT_RE = re.compile(r"^export\s+type\s+\{([^}]+)\}", re.M)
IMPORT_RE = re.compile(r"^import\s+(?:type\s+)?\{([^}]+)\}\s+from\s+['\"]([^'\"]+)['\"]", re.M)
IMPORT_DEFAULT_RE = re.compile(r"^import\s+(\w+)\s+from\s+['\"]([^'\"]+)['\"]", re.M)


def count_lines(p: Path) -> int:
    return sum(1 for _ in open(p, encoding="utf-8", errors="replace"))


def get_exports(text: str) -> list[str]:
    names = EXPORT_RE.findall(text)
    for m in TYPE_EXPORT_RE.finditer(text):
        names.extend(n.strip().split(",")[0].split()[0] for n in m.group(1).split(","))
    return sorted(set(names))


def get_imports(text: str) -> list[str]:
    deps: set[str] = set()
    for m in IMPORT_RE.finditer(text):
        deps.add(m.group(2))
    for m in IMPORT_DEFAULT_RE.finditer(text):
        deps.add(m.group(2))
    local = sorted(d for d in deps if d.startswith("."))
    return local[:12]


def main_entry(text: str, exports: list[str]) -> str | None:
    for name in exports:
        if name.startswith("is") or name.startswith("get") or name.startswith("create"):
            return f"`{name}()`"
    return f"`{exports[0]}()`" if exports else None


def covered_in_07(name: str) -> bool:
    patterns = [
        rf"###\s+`utils/{re.escape(name)}`",
        rf"###\s+`{re.escape(name)}`",
    ]
    return any(re.search(p, DOCS07) for p in patterns)


def entry_for(p: Path) -> str:
    text = p.read_text(encoding="utf-8", errors="replace")
    lines = count_lines(p)
    exports = get_exports(text)
    deps = get_imports(text)
    main = main_entry(text, exports)
    exp_lines = "\n".join(f"- `{e}`" for e in exports[:20])
    if len(exports) > 20:
        exp_lines += f"\n- ... +{len(exports) - 20} more"
    dep_line = ", ".join(f"`{d}`" for d in deps) if deps else "local only"
    main_line = f"**Main flow:** Entry: {main}\n\n" if main else ""
    return (
        f"## `{p.as_posix().replace(str(ROOT.as_posix()) + '/', '')}` ({lines} lines)\n\n"
        f"**Exports:**\n{exp_lines or '- (none)'}\n\n"
        f"**Dependencies:** {dep_line}\n\n"
        f"{main_line}"
        f"**Boundaries:** Validates inputs at call sites; throws or returns errors per function.\n"
    )


if __name__ == "__main__":
    root_files = sorted(UTILS.glob("*.ts"))
    uncovered = [p for p in root_files if not covered_in_07(p.name)]
    print(f"root={len(root_files)} uncovered={len(uncovered)}")
    for p in uncovered[:5]:
        print(entry_for(p)[:400])
        print("---")
