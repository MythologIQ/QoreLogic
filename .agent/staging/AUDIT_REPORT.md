# AUDIT REPORT

**Tribunal Date**: 2026-04-29T00:00:00Z
**Target**: `docs/plan-qor-phase48-script-discoverability-and-rename.md` (Pass 1)
**Risk Grade**: L1
**Auditor**: The QorLogic Judge
**Mode**: solo

---

## VERDICT: PASS

---

### Executive Summary

Phase 48 ships three coupled UX/install/discovery improvements: (A) convert 3 path-form `python qor/scripts/<name>.py` skill invocations to `python -m qor.scripts.<name>` and lock the rule for both `qor/scripts/` and `qor/reliability/`; (B) introduce `qor-logic` as the canonical CLI entry point alongside `qorlogic` (alias retained) and update every operator-facing surface; (C) evolve `/qor-help` from static catalog into a three-mode skill (bare / `--stuck` / `-- "<question>"`) with an ASCII SDLC flow chart. All eight audit passes clear.

### Audit Results

#### Security Pass
**Result**: PASS
No auth, secrets, or credential surfaces touched. CLI rename is naming only; alias keeps prior behavior. `/qor-help --stuck` reads existing gate artifacts (already on disk under `.qor/gates/<sid>/`) read-only. No new subprocess shell-form invocations.

#### OWASP Top 10 Pass
**Result**: PASS
- A03 Injection: `/qor-help -- "<question>"` does not eval the question string; the LLM running the skill consumes it as routing input. No subprocess interpolation.
- A04 Insecure Design: alias does not fail-open; both entry points dispatch to the same `qor.cli:main`.
- A05 Security Misconfiguration: no secrets, no temp files.
- A08 Software/Data Integrity: no deserialization changes.

#### Ghost UI Pass
**Result**: PASS
N/A.

#### Section 4 Razor Pass
**Result**: PASS

| Check              | Limit | Plan Proposes                                                       | Status |
| ------------------ | ----- | ------------------------------------------------------------------- | ------ |
| Max function lines | 40    | n/a (markdown + small CLI prose edits)                              | OK     |
| Max file lines     | 250   | `/qor-help` SKILL.md grows from ~125 to ~210 (under limit)          | OK     |
| Max nesting depth  | 3     | n/a                                                                 | OK     |
| Nested ternaries   | 0     | n/a                                                                 | OK     |

Specific check on `/qor-help` rewrite size: existing skill is 125 lines; adding Intro (~10 lines), SDLC Flow ASCII chart fence (~25 lines), Mode: --stuck protocol (~25 lines), Mode: -- "question" protocol (~15 lines), removing Quick Decision Tree (~13 lines saved) → projected ~187 lines. Under the 250-line cap.

#### Test Functionality Pass (Phase 46 doctrine)

For every described test in Phase 48's plan:

| Test description | Invokes unit? | Asserts on output? | Verdict |
| ---------------- | ------------- | ------------------ | ------- |
| `test_no_path_form_qor_scripts_invocations` | Yes — applies regex over skill bodies | Yes — counts/reports offenders | PASS |
| `test_no_path_form_qor_reliability_invocations` | Yes — same shape | Yes | PASS |
| `test_pyproject_declares_both_qor_logic_and_qorlogic_entry_points` | Yes — `tomllib.load`, dict membership check | Yes | PASS |
| `test_cli_main_version_string_uses_qor_logic` | Yes — `qor.cli.main(["--version"])` invocation, capsys capture | Yes — regex on stdout | PASS |
| `test_cli_help_text_uses_qor_logic_program_name` | Yes — `qor.cli.main(["--help"])` invocation, capsys capture | Yes — substring on captured help | PASS |
| `test_doctrine_governance_section_138_covers_both_scripts_and_reliability` | Yes — proximity-anchor regex on §138 | Yes — strip-and-fail negative-path paired | PASS |
| `test_install_drift_check_emits_qor_logic_fix_string` | Yes — invokes `install_drift_check.main()`, capsys | Yes — substring on captured fix line | PASS |
| `test_skill_prose_uses_qor_logic_for_cli_invocations` | Yes — regex with negative lookbehind on skill bodies | Yes — counts/reports offenders | PASS |
| `test_qor_help_has_intro_section` | Yes — proximity-anchor; strip-and-fail | Yes | PASS |
| `test_qor_help_has_ascii_sdlc_flow_chart` | Yes — fenced-block extraction + `body.encode('ascii')` round-trip + positional substring order | Yes — strip-and-fail | PASS |
| `test_qor_help_has_stuck_mode_protocol` | Yes — proximity-anchor; strip-and-fail | Yes | PASS |
| `test_qor_help_has_question_mode_protocol` | Yes — proximity-anchor; strip-and-fail | Yes | PASS |
| `test_qor_help_constraint_no_execute_preserved` | Yes — proximity-anchor on Constraints; strip-and-fail | Yes | PASS |

Self-application of Phase 46's Test Functionality Pass clears. Every test invokes the unit (the regex helper, the parsed config, the imported CLI's `main()`, the file-content extraction) and compares the result against an expected value. No presence-only tests in the plan.

#### Dependency Pass
**Result**: PASS
No new dependencies. `tomllib` is stdlib (Python 3.11+, already required).

#### Macro-Level Architecture Pass
**Result**: PASS
- Alias entry point is one line in `[project.scripts]`; no module restructure.
- `/qor-help` rewrite stays inside one SKILL.md; no new module boundaries.
- Path-form fixes are single-line edits in three skills.

#### Infrastructure Alignment Pass

| Cited path / symbol | Verification |
|---|---|
| `pyproject.toml` `[project.scripts] qorlogic = "qor.cli:main"` | exists (line ~32) |
| `qor/cli.py` `prog="qorlogic"` | exists (line 165) |
| `qor/cli.py` `--version` action with `f"qorlogic {__version__}"` | exists (line 168) |
| `qor/install.py` `qorlogic compile` / `qorlogic install` print strings | exists (lines 86, 147) |
| `qor/skills/meta/qor-help/SKILL.md` | exists; current 125 lines, contains tables + Quick Decision Tree |
| `qor/skills/governance/qor-shadow-process/SKILL.md:89,101` | exist; path-form invocations present |
| `qor/skills/governance/qor-process-review-cycle/SKILL.md:57` | exists; path-form invocation present |
| `qor/references/doctrine-governance-enforcement.md:138` | exists; rule currently mentions only `qor/reliability/` |
| `qor/references/doctrine-governance-enforcement.md:92` | exists; prose example uses path-form `python qor/scripts/session.py new` |
| `tests/test_installed_import_paths.py` | exists; `test_no_hyphen_named_reliability_invocations` and `test_qor_scripts_modules_importable` already present |
| `qor/scripts/check_shadow_threshold.py`, `create_shadow_issue.py` | exist; both have `if __name__ == "__main__"` guards (verified via grep earlier) |
| `qor/scripts/install_drift_check.py:72` | exists; print contains `qorlogic install` |
| `.qor/gates/<sid>/*.json` artifacts referenced by `--stuck` mode | shipped per Phase 11D wiring; `gate_chain.write_gate_artifact` is canonical writer |
| `qor.cli:main` callable | exists; argparse-based dispatcher |
| `tomllib` stdlib import | available in Python 3.11+ (project requires-python = ">=3.11") |

PASS.

#### Orphan Detection
**Result**: PASS
- New tests live under `tests/`; auto-collected by pytest.
- Doctrine edits modify existing referenced files.
- `/qor-help` rewrite stays in place; no new file.

### Backwards-Compat Risk

The `qorlogic` alias is retained. Operators with shell history, scripts, CI configs, or muscle memory referencing `qorlogic` continue to work. Filesystem state paths `.qorlogic/config.json` and `.qorlogic-installed.json` unchanged — no on-disk migration required. Risk: minimal.

### `/qor-help` mode-routing reliability

The plan correctly notes that mode routing is prose-only (LLM follows the protocol; no Python parser). Boundary clause acknowledges a future phase may promote routing to a helper if prose-only proves unreliable. The locked tests cover what the skill body MUST contain (intro, ASCII chart with positional substring order check, stuck-mode protocol, question-mode protocol, no-execute constraint preserved). They do not assert against runtime routing accuracy — that's an evaluation concern outside the gate's scope.

### Sequencing

Branch `phase/48-script-discoverability-and-rename` cut from `origin/main` at v0.34.0 (post Phase 46 + 47 merges). `bump_version('feature')` → v0.35.0; downgrade guard clears.

### Violations Found

None.

## Process Pattern Advisory

<!-- qor:veto-pattern-advisory -->

No repeated-VETO pattern detected.

## Documentation Drift

<!-- qor:drift-section -->
(clean — `terms_introduced` for canonical CLI, stuck mode, question mode each map to a home file. Boundaries enumerate filesystem-state preservation, prose-only mode routing, and the Gemini variant exclusion.)

---
_This verdict is binding._
