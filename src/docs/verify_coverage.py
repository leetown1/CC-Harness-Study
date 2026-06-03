#!/usr/bin/env python3
"""Verify coverage_matrix.json meets audit targets."""
from __future__ import annotations

import json
import sys
from pathlib import Path

MATRIX = Path(__file__).resolve().parent / "coverage_matrix.json"


def main() -> int:
    if not MATRIX.exists():
        print(f"ERROR: {MATRIX} not found. Run build_coverage_matrix.py first.")
        return 1

    matrix: dict = json.loads(MATRIX.read_text(encoding="utf-8"))
    total = len(matrix)
    errors: list[str] = []

    not_behavior = [p for p, v in matrix.items() if v.get("depth") != "behavior" and v.get("depth") != "generated"]
    not_verified = [p for p, v in matrix.items() if not v.get("verified")]
    no_refs = [p for p, v in matrix.items() if not v.get("doc_refs")]

    utils_root_missing = [
        p
        for p, v in matrix.items()
        if p.startswith("utils/") and p.count("/") == 1 and v.get("depth") == "none"
    ]

    print("=" * 70)
    print("COVERAGE VERIFICATION")
    print("=" * 70)
    print(f"Total files: {total}")
    print(f"Not behavior depth: {len(not_behavior)}")
    print(f"Not verified: {len(not_verified)}")
    print(f"No doc_refs: {len(no_refs)}")
    print(f"utils root depth=none: {len(utils_root_missing)}")

    if not_behavior:
        errors.append(f"{len(not_behavior)} files not at behavior depth")
        for p in not_behavior[:20]:
            print(f"  [depth={matrix[p]['depth']}] {p}")
        if len(not_behavior) > 20:
            print(f"  ... and {len(not_behavior) - 20} more")

    if not_verified:
        errors.append(f"{len(not_verified)} files not verified")
        for p in not_verified[:20]:
            print(f"  [unverified] {p}")

    if no_refs:
        errors.append(f"{len(no_refs)} files without doc_refs")

    # Check for Not verified in docs
    docs_dir = Path(__file__).resolve().parent / "source-code-analysis"
    not_verified_docs = 0
    for md in docs_dir.rglob("*.md"):
        text = md.read_text(encoding="utf-8")
        not_verified_docs += text.count("Not verified")
    if not_verified_docs:
        errors.append(f"{not_verified_docs} 'Not verified' strings remain in docs")
        print(f"\n'Not verified' in docs: {not_verified_docs}")

    if errors:
        print("\nFAILED:")
        for e in errors:
            print(f"  - {e}")
        return 1

    print("\nPASSED: All files behavior-level and verified.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
