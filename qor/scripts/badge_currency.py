"""Badge currency check for README.md.

Pure functions for counting current-truth values (tests, ledger entries,
skills, agents, doctrines) and parsing the declared values in README badges.
Used by tests and by `/qor-substantiate` Step 6.5 to ABORT seal on mismatch
for feature/breaking phases.
"""
from __future__ import annotations

import argparse
import re
import subprocess
import sys
from pathlib import Path

_BADGE_RE = re.compile(
    r"badge/(Tests|Ledger|Skills|Agents|Doctrines)-(\d+)",
    re.IGNORECASE,
)


def count_tests(repo_root: Path) -> int:
    """Run pytest --collect-only and parse the collected count.

    Explicitly targets the `tests/` directory and uses the repo's pyproject
    config to avoid stray collection from ad-hoc paths. Picks the FIRST
    matching summary line going backwards through stdout (some pytest runs
    print multiple summary-shaped lines; the last clean count is what we want).
    """
    result = subprocess.run(
        [sys.executable, "-m", "pytest", "tests/", "--collect-only", "-q"],
        cwd=str(repo_root), capture_output=True, text=True, check=False,
    )
    # Prefer the line WITHOUT "errors" (a clean summary). Fall back to any.
    summary_re = re.compile(r"(\d+)(?:/\d+)?\s+tests?\s+collected")
    clean = None
    fallback = None
    for line in reversed(result.stdout.splitlines()):
        m = summary_re.search(line)
        if not m:
            continue
        if "error" not in line.lower():
            clean = int(m.group(1))
            break
        if fallback is None:
            fallback = int(m.group(1))
    if clean is not None:
        return clean
    if fallback is not None:
        return fallback
    raise RuntimeError(
        f"could not parse pytest collected-count: {result.stdout[-500:]!r}"
    )


def count_ledger_entries(ledger_path: Path) -> int:
    """Count `### Entry #` headers in META_LEDGER.md."""
    text = ledger_path.read_text(encoding="utf-8")
    return len(re.findall(r"^### Entry #", text, re.MULTILINE))


def count_skills(repo_root: Path) -> int:
    """Count SKILL.md files under qor/skills/."""
    skills_dir = repo_root / "qor" / "skills"
    if not skills_dir.exists():
        return 0
    return sum(1 for _ in skills_dir.rglob("SKILL.md"))


def count_agents(repo_root: Path) -> int:
    """Count agent .md files under qor/agents/."""
    agents_dir = repo_root / "qor" / "agents"
    if not agents_dir.exists():
        return 0
    return sum(1 for _ in agents_dir.rglob("*.md"))


def count_doctrines(repo_root: Path) -> int:
    """Count doctrine-*.md files under qor/references/."""
    refs_dir = repo_root / "qor" / "references"
    if not refs_dir.exists():
        return 0
    return sum(1 for _ in refs_dir.glob("doctrine-*.md"))


def parse_readme_badges(readme_path: Path) -> dict[str, int]:
    """Parse README.md badge HTML; return {tests, ledger, skills, agents, doctrines}."""
    text = readme_path.read_text(encoding="utf-8")
    out: dict[str, int] = {}
    for m in _BADGE_RE.finditer(text):
        out[m.group(1).lower()] = int(m.group(2))
    return out


def check_currency(
    repo_root: Path,
    ledger_path: Path,
    tests_tolerance: int = 5,
    skip_tests: bool = False,
) -> list[str]:
    """Return list of mismatch strings; empty list = clean.

    `tests_tolerance` allows for skipped/deselected slack on the Tests badge.
    `skip_tests=True` bypasses the pytest --collect-only invocation (useful
    for unit tests of this helper that don't want to recursively invoke pytest).
    """
    declared = parse_readme_badges(repo_root / "README.md")
    truth = {
        "ledger": count_ledger_entries(ledger_path),
        "skills": count_skills(repo_root),
        "agents": count_agents(repo_root),
        "doctrines": count_doctrines(repo_root),
    }
    if not skip_tests:
        truth["tests"] = count_tests(repo_root)

    mismatches: list[str] = []
    for key, actual in truth.items():
        d = declared.get(key)
        if d is None:
            mismatches.append(f"{key}: README has no badge")
            continue
        if key == "tests":
            if abs(d - actual) > tests_tolerance:
                mismatches.append(
                    f"tests: README declares {d}, truth {actual} "
                    f"(tolerance ±{tests_tolerance})"
                )
        else:
            if d != actual:
                mismatches.append(f"{key}: README declares {d}, truth {actual}")
    return mismatches


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--repo-root", type=Path, default=Path.cwd())
    ap.add_argument("--ledger", type=Path, default=Path("docs/META_LEDGER.md"))
    args = ap.parse_args(argv)
    mismatches = check_currency(args.repo_root, args.ledger)
    if mismatches:
        print("FAIL: README badge currency mismatch:")
        for m in mismatches:
            print(f"  {m}")
        return 1
    print("OK: README badges current")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
