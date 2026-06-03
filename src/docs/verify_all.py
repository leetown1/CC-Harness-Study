#!/usr/bin/env python3
"""Run all documentation verification scripts."""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

DOCS = Path(__file__).resolve().parent


def run(script: str) -> int:
    path = DOCS / script
    print("\n" + "=" * 70)
    print(f"RUNNING {script}")
    print("=" * 70)
    result = subprocess.run([sys.executable, str(path)], cwd=DOCS.parent)
    return result.returncode


def main() -> int:
    steps = [
        ("get_stats.py", False),
        ("mark_coverage_verified.py", False),
        ("verify_docs.py", True),
        ("verify_exports.py", True),
        ("verify_coverage.py", True),
    ]
    failed = []
    for script, required in steps:
        code = run(script)
        if code != 0:
            if required:
                failed.append(script)
            else:
                print(f"  (non-fatal) {script} exited {code}")

    if failed:
        print("\nFAILED scripts:", ", ".join(failed))
        return 1
    print("\nALL REQUIRED CHECKS PASSED")
    return 0


if __name__ == "__main__":
    sys.exit(main())
