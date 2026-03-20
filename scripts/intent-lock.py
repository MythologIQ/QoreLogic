#!/usr/bin/env python3
"""Validate intent lock declarations in INTENT_LOCK.json."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
LOCK_FILE = REPO_ROOT / "INTENT_LOCK.json"


def find_lock(skill: str, locks: list[dict[str, str]]) -> dict[str, str] | None:
    """Return the lock entry for the given skill, or None."""
    return next((lk for lk in locks if lk.get("skill") == skill), None)


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate intent locks.")
    parser.add_argument("--skill", required=True, help="Skill name to check.")
    args = parser.parse_args()

    if not LOCK_FILE.exists():
        print(f"UNLOCKED: {args.skill} -- INTENT_LOCK.json not found")
        return 1

    data = json.loads(LOCK_FILE.read_text(encoding="utf-8"))
    locks = data.get("locks", [])
    entry = find_lock(args.skill, locks)

    if entry is None:
        print(f"UNLOCKED: {args.skill} -- no intent declaration found")
        return 1

    intent = entry.get("intent", "(no intent)")
    locked_by = entry.get("locked_by", "unknown")
    print(f"LOCKED: {args.skill} -- {intent} (by {locked_by})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
