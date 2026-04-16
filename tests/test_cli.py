"""Phase 19: qorlogic CLI stub dispatcher tests."""
from __future__ import annotations

import pytest


def test_qor_cli_main_importable():
    from qor.cli import main
    assert callable(main)


def test_qor_cli_help_returns_zero(capsys):
    from qor.cli import main
    with pytest.raises(SystemExit) as exc_info:
        main(["--help"])
    assert exc_info.value.code == 0


def test_qor_cli_version_prints_version(capsys):
    from qor.cli import main
    with pytest.raises(SystemExit):
        main(["--version"])
    captured = capsys.readouterr()
    assert "qorlogic" in captured.out
    assert "qorlogic" in captured.out


def test_qor_cli_compile_callable():
    """Phase 21: compile subcommand is wired (not stub)."""
    from qor.cli import main
    # compile should succeed (exit 0) when called with real source
    exit_code = main(["compile"])
    assert exit_code == 0
