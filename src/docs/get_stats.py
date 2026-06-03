#!/usr/bin/env python3
from pathlib import Path
from collections import defaultdict
import re

SRC = Path(__file__).resolve().parent.parent

def count_lines(p):
    with open(p, encoding="utf-8", errors="replace") as f:
        return sum(1 for _ in f)

src_files = {}
for p in SRC.rglob("*"):
    if p.suffix not in (".ts", ".tsx"):
        continue
    if "docs" in p.parts or "概述" in str(p):
        continue
    rel = p.relative_to(SRC).as_posix()
    src_files[rel] = count_lines(p)

dir_files = defaultdict(int)
dir_lines = defaultdict(int)
root_files = {}
for rel, lines in src_files.items():
    parts = rel.split("/")
    top = parts[0] if len(parts) > 1 else "(root)"
    dir_files[top] += 1
    dir_lines[top] += lines
    if len(parts) == 1:
        root_files[rel] = lines

utils_root = sum(1 for k in src_files if k.startswith("utils/") and k.count("/") == 1)
utils_sub = sum(1 for k in src_files if k.startswith("utils/") and k.count("/") > 1)
utils_plugins = sum(1 for k in src_files if k.startswith("utils/plugins/"))
utils_plugins_lines = sum(v for k, v in src_files.items() if k.startswith("utils/plugins/"))

print("TOTAL files", len(src_files), "lines", sum(src_files.values()))
print(".ts", sum(1 for k in src_files if k.endswith(".ts")))
print(".tsx", sum(1 for k in src_files if k.endswith(".tsx")))
print("root", len(root_files), "lines", sum(root_files.values()))
print("utils total", dir_files["utils"], "root", utils_root, "subdir", utils_sub, "plugins", utils_plugins, "plugins_lines", utils_plugins_lines)
print("commands ts/tsx", sum(1 for k in src_files if k.startswith("commands/") and k.endswith(".ts")), sum(1 for k in src_files if k.startswith("commands/") and k.endswith(".tsx")))
print("tools ts/tsx", sum(1 for k in src_files if k.startswith("tools/") and k.endswith(".ts")), sum(1 for k in src_files if k.startswith("tools/") and k.endswith(".tsx")))
print("keybindings", dir_files["keybindings"], "lines", dir_lines["keybindings"])
print("migrations", dir_files["migrations"], "lines", dir_lines["migrations"])
print("cli", dir_files["cli"], "lines", dir_lines["cli"])
print("services", dir_files["services"], "lines", dir_lines["services"])
print("bootstrap/state.ts", src_files.get("bootstrap/state.ts"))
print("main.tsx", src_files.get("main.tsx"))
print("bridge lines", dir_lines["bridge"])

ff = set()
for rel in src_files:
    try:
        c = (SRC / rel).read_text(encoding="utf-8", errors="replace")
        for m in re.finditer(r"feature\s*\(\s*['\"]([^'\"]+)['\"]", c):
            ff.add(m.group(1))
    except OSError:
        pass
print("feature flags", len(ff))

for d in sorted(dir_files.keys()):
    print(f"{d:25} {dir_files[d]:4} {dir_lines[d]:8}")
