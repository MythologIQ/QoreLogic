#!/usr/bin/env python3
"""S.H.I.E.L.D. skill processor: validates ingest/ skills and copies compliant ones to processed/."""

from __future__ import annotations

import re
import shutil
from dataclasses import dataclass, field
from pathlib import Path
from typing import List

REPO_ROOT = Path(__file__).resolve().parent.parent
INGEST_DIR = REPO_ROOT / "ingest" / "internal"
PROCESSED_DIR = REPO_ROOT / "processed"

# Categories that are NOT skills (different document types)
PASSTHROUGH_CATEGORIES = {"references", "scripts"}

# Categories with different compliance rules (persona defs, not skills)
AGENT_CATEGORIES = {"agents"}

# S.H.I.E.L.D. required sections (from ARCHITECTURE_PLAN.md Processing Rules)
REQUIRED_SECTIONS = {
    "skill_block": re.compile(r"<skill>.*?</skill>", re.DOTALL),
    "execution_protocol": re.compile(r"##\s+Execution Protocol", re.IGNORECASE),
    "constraints": re.compile(r"##\s+Constraints", re.IGNORECASE),
    "success_criteria": re.compile(r"##\s+Success Criteria", re.IGNORECASE),
    "integration": re.compile(r"##\s+Integration", re.IGNORECASE),
}

CONSTRAINT_PATTERN = re.compile(r"\*\*(NEVER|ALWAYS)\*\*", re.IGNORECASE)
CHECKBOX_PATTERN = re.compile(r"- \[[ x]\]")
MAX_FILE_LINES = 250


@dataclass
class SkillReport:
    path: Path
    name: str
    category: str
    line_count: int
    sections_found: dict = field(default_factory=dict)
    has_constraint_rules: bool = False
    has_checkboxes: bool = False
    compliance: str = "UNKNOWN"
    issues: List[str] = field(default_factory=list)

    @property
    def sections_missing(self) -> List[str]:
        return [k for k, v in self.sections_found.items() if not v]


def analyze_skill(filepath: Path, category: str) -> SkillReport:
    """Analyze a single skill file for S.H.I.E.L.D. compliance."""
    content = filepath.read_text(encoding="utf-8", errors="replace")
    lines = content.splitlines()
    name = filepath.stem

    report = SkillReport(
        path=filepath,
        name=name,
        category=category,
        line_count=len(lines),
    )

    # Check each required section
    for section_name, pattern in REQUIRED_SECTIONS.items():
        report.sections_found[section_name] = bool(pattern.search(content))

    # Check for NEVER/ALWAYS constraint rules
    report.has_constraint_rules = bool(CONSTRAINT_PATTERN.search(content))

    # Check for success criteria checkboxes
    report.has_checkboxes = bool(CHECKBOX_PATTERN.search(content))

    # Validate line count
    if report.line_count > MAX_FILE_LINES:
        report.issues.append(f"Exceeds {MAX_FILE_LINES} line limit ({report.line_count} lines)")

    # Missing sections
    for section in report.sections_missing:
        report.issues.append(f"Missing: {section}")

    # Constraints section exists but no NEVER/ALWAYS rules
    if report.sections_found.get("constraints") and not report.has_constraint_rules:
        report.issues.append("Constraints section has no NEVER/ALWAYS rules")

    # Success criteria exists but no checkboxes
    if report.sections_found.get("success_criteria") and not report.has_checkboxes:
        report.issues.append("Success criteria has no checkboxes")

    # Determine compliance level
    missing_count = len(report.sections_missing)
    if missing_count == 0 and not report.issues:
        report.compliance = "COMPLIANT"
    elif missing_count <= 1 and report.line_count <= MAX_FILE_LINES:
        report.compliance = "PARTIAL"
    else:
        report.compliance = "NON_COMPLIANT"

    return report


def process_skills() -> tuple[List[SkillReport], List[Path], List[SkillReport]]:
    """Scan all ingest/internal skills. Returns (skills, passthrough, agents)."""
    reports: List[SkillReport] = []
    passthrough: List[Path] = []
    agents: List[SkillReport] = []

    for category_dir in sorted(INGEST_DIR.iterdir()):
        if not category_dir.is_dir():
            continue
        category = category_dir.name

        if category in PASSTHROUGH_CATEGORIES:
            for f in sorted(category_dir.glob("*.md")):
                passthrough.append(f)
            continue

        for skill_file in sorted(category_dir.glob("*.md")):
            report = analyze_skill(skill_file, category)
            if category in AGENT_CATEGORIES:
                agents.append(report)
            else:
                reports.append(report)

    return reports, passthrough, agents


def copy_compliant(reports: List[SkillReport], passthrough: List[Path]) -> int:
    """Copy COMPLIANT skills and passthrough files to processed/."""
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    copied = 0

    for report in reports:
        if report.compliance != "COMPLIANT":
            continue
        dest = PROCESSED_DIR / f"{report.name}.md"
        shutil.copy2(report.path, dest)
        copied += 1

    # Copy passthrough files (references, scripts) as-is
    for pt_file in passthrough:
        category = pt_file.parent.name
        dest_dir = PROCESSED_DIR / category
        dest_dir.mkdir(parents=True, exist_ok=True)
        shutil.copy2(pt_file, dest_dir / pt_file.name)
        copied += 1

    return copied


def print_report(
    reports: List[SkillReport],
    passthrough: List[Path],
    agents: List[SkillReport],
    copied: int,
) -> None:
    """Print a formatted compliance report."""
    compliant = [r for r in reports if r.compliance == "COMPLIANT"]
    partial = [r for r in reports if r.compliance == "PARTIAL"]
    non_compliant = [r for r in reports if r.compliance == "NON_COMPLIANT"]

    print("=" * 60)
    print("S.H.I.E.L.D. Skill Processing Report")
    print("=" * 60)
    print()
    print(f"Skills scanned:    {len(reports)}")
    print(f"  COMPLIANT:       {len(compliant)}")
    print(f"  PARTIAL:         {len(partial)}")
    print(f"  NON_COMPLIANT:   {len(non_compliant)}")
    print(f"Passthrough files: {len(passthrough)}")
    print(f"Agent personas:    {len(agents)}")
    print(f"Copied to processed/: {copied}")
    print()

    if compliant:
        print("--- COMPLIANT (copied to processed/) ---")
        for r in compliant:
            print(f"  [OK] {r.category}/{r.name} ({r.line_count} lines)")
        print()

    if partial:
        print("--- PARTIAL (needs minor fixes) ---")
        for r in partial:
            print(f"  [~] {r.category}/{r.name} ({r.line_count} lines)")
            for issue in r.issues:
                print(f"      - {issue}")
        print()

    if non_compliant:
        print("--- NON_COMPLIANT (needs normalization) ---")
        for r in non_compliant:
            print(f"  [X] {r.category}/{r.name} ({r.line_count} lines)")
            for issue in r.issues:
                print(f"      - {issue}")
        print()

    if passthrough:
        print(f"--- PASSTHROUGH ({len(passthrough)} files copied as-is) ---")
        for f in passthrough:
            print(f"  [>] {f.parent.name}/{f.name}")
        print()

    if agents:
        print("--- AGENT PERSONAS (separate format) ---")
        for a in agents:
            print(f"  [@] {a.name} ({a.line_count} lines)")
        print()


def main() -> int:
    reports, passthrough, agents = process_skills()
    copied = copy_compliant(reports, passthrough)
    print_report(reports, passthrough, agents, copied)
    skills_ok = all(r.compliance == "COMPLIANT" for r in reports)
    return 0 if skills_ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
