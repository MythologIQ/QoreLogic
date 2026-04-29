"""Phase 48: /qor-help conversational evolution.

Five mode/structure assertions on qor/skills/meta/qor-help/SKILL.md, each
paired with a strip-and-fail negative-path test per Phase 46 doctrine
(qor/references/doctrine-test-functionality.md).

Functionality: every test reads the file, locates a section header, extracts
content within a bounded span (or extracts a fenced code block), and asserts
on the parsed result. No bare-substring presence checks.
"""
from __future__ import annotations

import re
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
SKILL = REPO_ROOT / "qor" / "skills" / "meta" / "qor-help" / "SKILL.md"


def _read() -> str:
    return SKILL.read_text(encoding="utf-8")


def _proximity(body: str, header_pattern: str, phrase_pattern: str, span: int = 2000) -> bool:
    m = re.search(header_pattern, body, re.MULTILINE)
    if not m:
        return False
    window = body[m.end(): m.end() + span]
    return re.search(phrase_pattern, window, re.IGNORECASE | re.DOTALL) is not None


def _strip_section(body: str, header_pattern: str, span: int = 4000) -> str:
    """Replace `span` characters after the named header with neutral filler.

    Preserves overall body length so content past the strip does not slide
    into the proximity window. Same shape as Phase 46's helper.
    """
    m = re.search(header_pattern, body, re.MULTILINE)
    if not m:
        return body
    start = m.end()
    end = min(len(body), start + span)
    filler = "\n# stripped\n" * ((end - start) // 12 + 1)
    filler = filler[: end - start]
    return body[:start] + filler + body[end:]


def _fenced_block_after(body: str, header_pattern: str) -> str | None:
    """Extract the first ``` fenced code block following the named header."""
    m = re.search(header_pattern, body, re.MULTILINE)
    if not m:
        return None
    rest = body[m.end():]
    fence = re.search(r"```[a-z]*\n(.*?)\n```", rest, re.DOTALL)
    return fence.group(1) if fence else None


# -------- Intro section --------

INTRO_HEADER = r"^## Intro\b|^## How to use /qor-help\b"


def test_qor_help_has_intro_section():
    body = _read()
    assert _proximity(body, INTRO_HEADER, r"--stuck", span=2000), (
        "Intro section must mention --stuck mode"
    )
    assert _proximity(body, INTRO_HEADER, r'-- "', span=2000), (
        'Intro section must mention -- "<question>" mode'
    )
    assert _proximity(body, INTRO_HEADER, r"bare", span=2000), (
        "Intro section must describe bare invocation"
    )


def test_qor_help_intro_negative_path():
    body = _read()
    mutated = _strip_section(body, INTRO_HEADER)
    assert not _proximity(mutated, INTRO_HEADER, r"--stuck", span=2000)


# -------- ASCII SDLC flow chart --------

FLOW_HEADER = r"^## SDLC Flow\b"


def test_qor_help_has_ascii_sdlc_flow_chart():
    body = _read()
    chart = _fenced_block_after(body, FLOW_HEADER)
    assert chart is not None, "SDLC Flow section must contain a fenced code block"

    # Plain ASCII only (no Unicode box-drawing chars).
    try:
        chart.encode("ascii")
    except UnicodeEncodeError as exc:
        pytest.fail(f"SDLC Flow chart must be plain ASCII; non-ASCII char at {exc}")

    # Positional substring order: research before plan before audit before
    # implement before substantiate. Not just presence — order.
    expected_order = ["research", "plan", "audit", "implement", "substantiate"]
    positions = [chart.lower().find(name) for name in expected_order]
    assert all(p >= 0 for p in positions), (
        f"chart must mention all SDLC phases; positions: {dict(zip(expected_order, positions))}"
    )
    assert positions == sorted(positions), (
        f"chart must list phases in left-to-right SDLC order; got positions {dict(zip(expected_order, positions))}"
    )


def test_qor_help_ascii_chart_negative_path():
    body = _read()
    mutated = _strip_section(body, FLOW_HEADER)
    chart = _fenced_block_after(mutated, FLOW_HEADER)
    # After strip, no fenced code block remains in the bounded region; chart is None
    # OR it lacks the expected phases. Either way the positive-path assertion fails.
    if chart is not None:
        positions = [chart.lower().find(n) for n in ["research", "plan", "audit"]]
        assert not all(p >= 0 for p in positions), (
            "After strip, chart should not contain all SDLC phases"
        )


# -------- --stuck mode --------

STUCK_HEADER = r"^## Mode: --stuck\b"


def test_qor_help_has_stuck_mode_protocol():
    body = _read()
    assert _proximity(body, STUCK_HEADER, r"\.qor/gates/", span=2500), (
        "--stuck protocol must mention reading .qor/gates/<sid>/*.json"
    )
    assert _proximity(body, STUCK_HEADER, r"session_id|session/current", span=2500), (
        "--stuck protocol must mention session id resolution"
    )
    assert _proximity(body, STUCK_HEADER, r"recommend", span=2500), (
        "--stuck protocol must specify recommendation as the output"
    )


def test_qor_help_stuck_mode_negative_path():
    body = _read()
    mutated = _strip_section(body, STUCK_HEADER)
    assert not _proximity(mutated, STUCK_HEADER, r"\.qor/gates/", span=2500)


# -------- -- "question" mode --------

QUESTION_HEADER = r'^## Mode: -- "question"|^## Mode: -- "<question>"'


def test_qor_help_has_question_mode_protocol():
    body = _read()
    assert _proximity(body, QUESTION_HEADER, r"free.form|free-form", span=2000), (
        'question-mode protocol must describe free-form question handling'
    )
    assert _proximity(body, QUESTION_HEADER, r"catalog", span=2000), (
        'question-mode protocol must reference the catalog as routing source'
    )


def test_qor_help_question_mode_negative_path():
    body = _read()
    mutated = _strip_section(body, QUESTION_HEADER)
    assert not _proximity(mutated, QUESTION_HEADER, r"free.form", span=2000)


# -------- No-execute constraint preserved --------

CONSTRAINTS_HEADER = r"^## Constraints\b"


def test_qor_help_constraint_no_execute_preserved():
    body = _read()
    # Markdown bolds may wrap NEVER as **NEVER**; allow any non-letter delimiter
    # between tokens so the assertion isn't tied to formatting.
    assert _proximity(body, CONSTRAINTS_HEADER, r"NEVER[^a-zA-Z]+execute[^a-zA-Z]+other[^a-zA-Z]+skills", span=1500), (
        "Constraints must preserve 'NEVER execute other skills' rule"
    )


def test_qor_help_no_execute_constraint_negative_path():
    body = _read()
    mutated = _strip_section(body, CONSTRAINTS_HEADER)
    assert not _proximity(mutated, CONSTRAINTS_HEADER, r"NEVER[^a-zA-Z]+execute[^a-zA-Z]+other[^a-zA-Z]+skills", span=1500)
