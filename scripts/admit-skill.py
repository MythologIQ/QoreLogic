#!/usr/bin/env python3
"""Validate that a skill file meets minimum admission criteria."""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

MAX_LINES = 250
FRONTMATTER_RE = re.compile(r"^---\n.*?\n---\n", re.DOTALL)
SKILL_BLOCK_RE = re.compile(r"<skill>.*?</skill>", re.DOTALL)


def check_admission(filepath: Path) -> tuple[bool, list[str]]:
    """Run admission checks. Returns (admitted, reasons)."""
    reasons: list[str] = []

    if not filepath.exists():
        return False, ["file does not exist"]

    if not filepath.is_file():
        return False, ["path is not a file"]

    content = filepath.read_text(encoding="utf-8", errors="replace")
    lines = content.splitlines()

    if not FRONTMATTER_RE.match(content):
        reasons.append("missing YAML frontmatter (---)")

    if not SKILL_BLOCK_RE.search(content):
        reasons.append("missing <skill> block")

    if len(lines) > MAX_LINES:
        reasons.append(f"exceeds {MAX_LINES} line limit ({len(lines)} lines)")

    admitted = len(reasons) == 0
    return admitted, reasons


def main() -> int:
    parser = argparse.ArgumentParser(description="Skill admission gate.")
    parser.add_argument("file", type=Path, help="Path to skill file.")
    args = parser.parse_args()

    admitted, reasons = check_admission(args.file)

    if admitted:
        print(f"ADMIT: {args.file.name} -- all criteria met")
        return 0

    print(f"REJECT: {args.file.name}")
    for reason in reasons:
        print(f"  - {reason}")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
