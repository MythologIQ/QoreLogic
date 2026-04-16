"""Phase 22 Track B: NIST SP 800-218A alignment doctrine tests."""
from __future__ import annotations

import re
from pathlib import Path

DOCTRINE_PATH = Path(__file__).resolve().parent.parent / "qor" / "references" / "doctrine-nist-ssdf-alignment.md"


def test_nist_ssdf_alignment_exists():
    assert DOCTRINE_PATH.exists(), f"Missing {DOCTRINE_PATH}"
    body = DOCTRINE_PATH.read_text(encoding="utf-8")
    assert len(body) > 200, "Doctrine too short"


def _read_body() -> str:
    return DOCTRINE_PATH.read_text(encoding="utf-8")


def test_po_section_present():
    """PO practice group anchored with proximity check."""
    body = _read_body()
    # Find PO header, then check PO.1.1 within 500 chars
    m = re.search(r"## PO.{0,500}PO\.1\.1", body, re.DOTALL)
    assert m is not None, "PO.1.1 not found near PO section header"


def test_ps_section_present():
    """PS practice group anchored with proximity check."""
    body = _read_body()
    m = re.search(r"## PS.{0,500}PS\.1\.1", body, re.DOTALL)
    assert m is not None, "PS.1.1 not found near PS section header"


def test_pw_section_present():
    """PW practice group anchored with proximity check."""
    body = _read_body()
    m = re.search(r"## PW.{0,500}PW\.1\.1", body, re.DOTALL)
    assert m is not None, "PW.1.1 not found near PW section header"


def test_rv_section_present():
    """RV practice group anchored with proximity check."""
    body = _read_body()
    m = re.search(r"## RV.{0,500}RV\.1\.1", body, re.DOTALL)
    assert m is not None, "RV.1.1 not found near RV section header"
