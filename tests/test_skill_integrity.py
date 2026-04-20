"""Skill-integrity grep-lints for Phase 37 B21 wiring."""
from __future__ import annotations

import pathlib


_QOR_PLAN = pathlib.Path("qor/skills/sdlc/qor-plan/SKILL.md")
_QOR_AUDIT = pathlib.Path("qor/skills/governance/qor-audit/SKILL.md")
_DELEGATION = pathlib.Path("qor/gates/delegation-table.md")


def test_qor_plan_skill_calls_cycle_count_check():
    prose = _QOR_PLAN.read_text(encoding="utf-8")
    assert "cycle_count_escalator" in prose
    assert "cce.check" in prose or "cycle_count_escalator.check" in prose


def test_qor_audit_skill_calls_cycle_count_check():
    prose = _QOR_AUDIT.read_text(encoding="utf-8")
    assert "cycle_count_escalator" in prose


def test_qor_audit_has_infrastructure_alignment_pass():
    prose = _QOR_AUDIT.read_text(encoding="utf-8")
    assert "Infrastructure Alignment Pass" in prose
    assert "infrastructure-mismatch" in prose


def test_delegation_table_lists_cycle_count_escalation():
    prose = _DELEGATION.read_text(encoding="utf-8")
    assert "cycle-count escalation" in prose
    assert "orchestration_override" in prose
