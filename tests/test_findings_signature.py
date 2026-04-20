"""Tests for qor/scripts/findings_signature.py (Phase 37 B20b)."""
from __future__ import annotations

import json
import re

import pytest

from qor.scripts import findings_signature as fs


def _rec(cats):
    return {"findings_categories": cats} if cats is not None else {}


def test_signature_is_order_independent():
    sig_a = fs.compute_record(_rec(["razor-overage", "macro-architecture", "specification-drift"]))
    sig_b = fs.compute_record(_rec(["macro-architecture", "specification-drift", "razor-overage"]))
    assert sig_a == sig_b


def test_signature_is_dedupe_stable():
    sig_a = fs.compute_record(_rec(["razor-overage", "razor-overage", "specification-drift"]))
    sig_b = fs.compute_record(_rec(["razor-overage", "specification-drift"]))
    assert sig_a == sig_b


def test_signature_differs_on_category_change():
    sig_a = fs.compute_record(_rec(["razor-overage"]))
    sig_b = fs.compute_record(_rec(["ghost-ui"]))
    assert sig_a != sig_b


def test_signature_empty_is_stable():
    sig_a = fs.compute_record(_rec([]))
    sig_b = fs.compute_record(_rec([]))
    assert sig_a == sig_b
    assert sig_a != fs.LEGACY_SENTINEL


def test_signature_returns_legacy_sentinel_when_field_absent():
    result = fs.compute_record({})
    assert result == fs.LEGACY_SENTINEL
    assert result == "LEGACY"


def test_legacy_sentinel_is_not_hex_shaped():
    # Real signatures are 16 lowercase hex chars. LEGACY contains L/G/Y (non-hex).
    assert not re.match(r"^[0-9a-f]{16}$", fs.LEGACY_SENTINEL)


def test_signature_rejects_unknown_category():
    with pytest.raises(fs.UnmappedCategoryError):
        fs.compute_record(_rec(["fictional-category"]))


def test_signature_is_16_char_prefix():
    sig = fs.compute_record(_rec(["razor-overage"]))
    assert len(sig) == 16
    assert re.match(r"^[0-9a-f]{16}$", sig)


def test_compute_path_loads_file(tmp_path):
    path = tmp_path / "audit.json"
    path.write_text(
        json.dumps({"findings_categories": ["macro-architecture", "specification-drift"]}),
        encoding="utf-8",
    )
    sig = fs.compute_path(path)
    expected = fs.compute_record({"findings_categories": ["macro-architecture", "specification-drift"]})
    assert sig == expected
