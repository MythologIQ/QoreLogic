# Plan: Phase 49 — attribution tiering + README badge currency enforcement

**change_class**: feature
**target_version**: v0.36.0
**doc_tier**: standard
**pass**: 1

**Scope**: Two coupled docs-currency enforcement gaps from `docs/compliance-re-evaluation-2026-04-29.md`. Both share a root cause — release-doc-currency contracts that aren't mechanically enforced — so they're remediated together with one consistent test surface.

(A) **G-3: tiered attribution policy** — define which attribution-trailer form is required at which surface; lock with an enforcement test. The full canonical 3-line trailer (emoji + Qor-logic SDLC line + `Co-Authored-By:`) becomes mandatory only on seal commits and PR descriptions; plan/audit/implement commits get the single-line `Co-Authored-By:` form; CHANGELOG attribution lives once per `## [X.Y.Z]` header. This stops further compaction drift (already happening in Phase 48) and prevents per-commit boilerplate noise.

(B) **G-4: README badge currency enforcement** — parse README.md badges at substantiate time and assert the literal counts match current truth (`Tests: <pytest collect count> passing`, `Ledger: <grep -c '^### Entry #' docs/META_LEDGER.md> entries sealed`, etc.). Currently WARN-only; promote to a `/qor-substantiate` step that aborts seal on mismatch when `change_class ∈ {feature, breaking}`. Hotfix exempt (matches the existing `_RELEASE_CLASSES` semantics).

**Rationale**:
- (A) without enforcement → silent compaction (Phase 48 dropped the canonical line; nobody noticed). Without tiering → 12 lines of boilerplate per phase across 4 commits, training operators to ignore attribution as noise.
- (B) WARN-only currency checks are dismissable. Phases 45/46/48 each shipped with stale README badges. The Phase 33 doctrine is in place; operator vigilance has not been a sufficient enforcement mechanism.

**terms_introduced**:
- term: tiered attribution policy
  home: qor/references/doctrine-attribution.md
- term: badge currency enforcement
  home: qor/references/doctrine-governance-enforcement.md

**boundaries**:
- limitations: badge currency enforcement targets only literal-count badges (Tests, Ledger, Skills, Agents, Doctrines). Dynamic badges (PyPI, Python version, License, NIST, OWASP, Doc Tier) are not parsed — they auto-refresh from shields.io or are framework-named and don't drift with project state. Attribution test walks last N commits + the `[Unreleased]` and current-version CHANGELOG sections; older entries grandfathered.
- non_goals: rewriting historical commits to backfill attribution form; renaming the `qorlogic` alias entry point (kept per Phase 48); changing the canonical attribution string content (only the per-surface usage policy changes); modifying the branch-protection ruleset (separate authorization).
- exclusions: G-1 (SSDF tag backfill), G-2 (skill-prose filesystem validation), and the ruleset `code_quality` rule are queued as Phase 50/51 separately.

## Open Questions

None.

## Phase 1 — tiered attribution + badge currency

### Affected Files

Tests authored first (TDD; verified RED before implementation):

- `tests/test_attribution_tiered_usage.py` — new. Six tests:
  - `test_seal_commits_have_full_canonical_trailer` — walks `git log` for commits matching `^seal:` on the last 10 sealed phases (or since Phase 45 origin); asserts each has the emoji + Qor-logic SDLC line AND the `Co-Authored-By:` line. Strip-and-fail negative-path: synthetic commit message missing the Qor-logic line MUST fail the assertion.
  - `test_plan_audit_implement_commits_have_coauthor_line` — walks commits matching `^(plan|audit|implement):` since Phase 45; asserts each has at least the `Co-Authored-By:` line. (Full canonical is permitted but not required.)
  - `test_changelog_has_attribution_under_each_version_header` — parses `CHANGELOG.md` for each `## [X.Y.Z]` header; asserts the canonical attribution line `_Built via [Qor-logic SDLC](url)._` appears within 5 lines below the header AND only once per version section. Strip-and-fail.
  - `test_attribution_helper_returns_canonical_strings_for_each_tier` — invokes `qor.scripts.attribution.commit_trailer_compact()` and `qor.scripts.attribution.commit_trailer()` (full); asserts return values match documented canonical strings. New helper function shipped this phase.
  - `test_pr_body_canonical_footer_documented_in_attribution_md` — proximity-anchored regex on `ATTRIBUTION.md`: `## PR-body footer` section followed within 1500 chars by both `Authored using` and `Qor-logic` and `audit gate caught`. Strip-and-fail.
  - `test_doctrine_attribution_documents_tier_table` — proximity-anchored regex on `qor/references/doctrine-attribution.md`: `## Tiered usage` section followed within 2000 chars by mentions of `seal commit`, `plan/audit/implement`, `CHANGELOG`, `PR description`. Strip-and-fail.

- `tests/test_readme_badge_currency.py` — new. Five tests:
  - `test_readme_tests_badge_matches_pytest_collected_count` — invokes `pytest --collect-only -q` via subprocess (functionality test: invokes the unit, parses the `XXX/YYY tests collected` summary line), parses README's `Tests: NNN passing` badge, asserts the README count is within ±5 of the pytest-collected count (allowing for skipped/deselected slack). Mismatch beyond tolerance fails.
  - `test_readme_ledger_badge_matches_entry_count` — counts `^### Entry #` lines in `docs/META_LEDGER.md`, parses README's `Ledger: NNN entries sealed` badge, asserts equality. Strict.
  - `test_readme_skills_badge_matches_skill_count` — counts `qor/skills/**/SKILL.md` files, parses README badge `Skills: NN`, asserts equality.
  - `test_readme_agents_badge_matches_agent_count` — counts `qor/agents/**/*.md` files, parses badge, asserts equality.
  - `test_readme_doctrines_badge_matches_doctrine_count` — counts `qor/references/doctrine-*.md` files, parses badge, asserts equality.

  Each test invokes the corresponding counting helper (a new `qor/scripts/badge_currency.py` module) and asserts on the returned tuple `(declared, actual)`. Pure-function, no I/O in the assertion path; the helper does the reads.

- `tests/test_substantiate_badge_currency_wiring.py` — new. Three defensive tests with proximity-anchor + strip-and-fail (Phase 46 doctrine):
  - `test_substantiate_step_6_5_invokes_badge_currency_check` — proximity-anchored on `### Step 6.5: Documentation Currency Check` header in `qor/skills/governance/qor-substantiate/SKILL.md`: phrase `badge_currency` AND `feature, breaking` appear within 2000 chars.
  - `test_substantiate_aborts_seal_on_badge_mismatch_for_release_changes` — proximity-anchored on the same step: phrase `ABORT` (or `aborts seal`) within 2000 chars.
  - `test_substantiate_badge_check_exempts_hotfix` — proximity-anchored on the same step: phrase `hotfix` AND `exempt` (or `skip`) within 2000 chars.

Source surfaces:

- `qor/scripts/badge_currency.py` — new module, ~80 lines. Pure functions:
  - `count_tests(repo_root)` — invokes `pytest --collect-only -q` in subprocess, parses the summary line, returns int.
  - `count_ledger_entries(ledger_path)` — `re.findall(r'^### Entry #', ...)`, returns int.
  - `count_skills(repo_root)`, `count_agents(repo_root)`, `count_doctrines(repo_root)` — Path.rglob counts.
  - `parse_readme_badges(readme_path)` — regex over README badge HTML, returns dict `{tests, ledger, skills, agents, doctrines}` of declared ints.
  - `check_currency(repo_root, ledger_path)` — combines all of the above, returns list of mismatch strings (empty = clean). Tolerance ±5 for tests; strict for the others.
  - `main()` — CLI entrypoint for `python -m qor.scripts.badge_currency`. argv: `--repo-root`, `--ledger`. Exits 0 on clean, 1 on mismatch with diagnostic stdout.
- `qor/scripts/attribution.py` — extend with `commit_trailer_compact(model)` returning just the `Co-Authored-By:` line. Existing `commit_trailer()` (full canonical) unchanged.
- `qor/references/doctrine-attribution.md` — add `## Tiered usage` section after the existing canonical-strings section. Six rows mapping surface → required form (seal commit / plan-audit-implement commits / merge commit / PR description / CHANGELOG / GitHub release).
- `ATTRIBUTION.md` — add a brief `## Tiered usage` section pointing at the doctrine for full table; show a 4-row quickref (seal vs plan/audit/implement vs PR vs CHANGELOG).
- `qor/skills/governance/qor-substantiate/SKILL.md` — Step 6.5 (Documentation Currency Check) extends the warnings logic to ABORT seal when `change_class ∈ {feature, breaking}` AND `badge_currency.check_currency()` returns mismatches. Hotfix exempt (matches existing `_RELEASE_CLASSES`). Bash one-liner: `python -m qor.scripts.badge_currency --repo-root . --ledger docs/META_LEDGER.md`. ABORT message names which badge mismatches.
- `qor/references/doctrine-governance-enforcement.md` — add `## Badge currency` subsection under §"release-doc currency" (or extend §8 Install Currency) with the contract: feature/breaking phases must update README badges; the substantiate step verifies; the lint test prevents regression.
- `CHANGELOG.md` — `[Unreleased]` populated with Phase 49 narrative under `### Added` (tiered policy + badge enforcement) and `### Changed` (substantiate step 6.5 hardening).
- README.md — once-per-version attribution line `_Built via [Qor-logic SDLC](https://github.com/MythologIQ-Labs-LLC/qor-logic)._` added immediately under each version header in `CHANGELOG.md` for the post-cutoff versions. Cutoff: 0.36.0 forward. Older entries grandfathered (no rewrite).

Variant regeneration:

- `qor/dist/variants/{claude,codex,gemini,kilo-code}/skills/qor-substantiate/SKILL.md` — auto-regenerated via `python -m qor.scripts.dist_compile`.

### Unit Tests

TDD order — every test below authored first, run RED, then GREEN after the corresponding source edit. Each invokes the unit and asserts on output, per `qor/references/doctrine-test-functionality.md`.

- `test_seal_commits_have_full_canonical_trailer` — invokes `subprocess.run(['git', 'log', '--format=%H%x00%s%x00%b', ...])` to get commit messages; filters `seal:` subjects; asserts each body contains both `Authored via` AND `Co-Authored-By:` substrings AND the Qor-logic URL. Functional: invokes git, parses output, asserts on per-commit body content. Strip-and-fail covered by a fixture-based negative-path test.
- `test_plan_audit_implement_commits_have_coauthor_line` — same `git log` invocation, filters `^(plan|audit|implement):` subjects, asserts each has `Co-Authored-By:` line. Tolerant of either compact or full form.
- `test_changelog_has_attribution_under_each_version_header` — parses CHANGELOG.md, finds each `## [X.Y.Z]` header, asserts the next 5 lines contain `_Built via [Qor-logic SDLC](url)._` once. Cutoff: only checks versions ≥ `0.36.0` (the version this phase ships) so historical CHANGELOG isn't required to backfill.
- `test_attribution_helper_returns_canonical_strings_for_each_tier` — invokes `commit_trailer_compact("Claude Opus 4.7 (1M context)")` and `commit_trailer("Claude Opus 4.7 (1M context)")`; asserts compact form is exactly one `Co-Authored-By:` line and full form is the canonical 3-line block. Functional: invokes the helper, asserts on returned string content.
- `test_pr_body_canonical_footer_documented_in_attribution_md` / `test_doctrine_attribution_documents_tier_table` — proximity-anchored regex on doc files; strip-and-fail negative-paths paired.
- `test_readme_*_badge_matches_*` (5 tests) — each invokes `qor.scripts.badge_currency.count_X()` AND `parse_readme_badges()`, asserts equality (or tolerance for tests). Functional: invokes the helper, asserts on the (declared, actual) tuple.
- `test_substantiate_step_6_5_*` (3 tests) — proximity-anchored on `qor-substantiate/SKILL.md` Step 6.5 prose; strip-and-fail negative-paths paired.

### Changes

#### 1. `qor/scripts/badge_currency.py` — new helper module

Pure functions returning ints / dicts; no global state; CLI entrypoint via `python -m`. ~80 lines, all functions ≤30 lines, depth ≤2.

```python
"""Badge currency check for README.md.

Pure functions for counting current-truth values (tests, ledger entries,
skills, agents, doctrines) and parsing the declared values in README badges.
Used by tests and by `/qor-substantiate` Step 6.5 to ABORT seal on mismatch
for feature/breaking phases.
"""
from __future__ import annotations

import re
import subprocess
from pathlib import Path

_BADGE_RE = re.compile(
    r'badge/(Tests|Ledger|Skills|Agents|Doctrines)-(\d+)',
    re.IGNORECASE,
)


def count_tests(repo_root: Path) -> int:
    """Run pytest --collect-only and parse the collected count."""
    result = subprocess.run(
        ["python", "-m", "pytest", "--collect-only", "-q"],
        cwd=str(repo_root), capture_output=True, text=True, check=False,
    )
    # Last meaningful line: 'NNN/MMM tests collected (...)' or 'NNN tests collected'
    for line in reversed(result.stdout.splitlines()):
        m = re.search(r"(\d+)(?:/\d+)?\s+tests?\s+collected", line)
        if m:
            return int(m.group(1))
    raise RuntimeError(f"could not parse pytest collected-count: {result.stdout[-500:]!r}")


def count_ledger_entries(ledger_path: Path) -> int:
    text = ledger_path.read_text(encoding="utf-8")
    return len(re.findall(r"^### Entry #", text, re.MULTILINE))


def count_skills(repo_root: Path) -> int:
    return sum(1 for _ in (repo_root / "qor" / "skills").rglob("SKILL.md"))


def count_agents(repo_root: Path) -> int:
    return sum(1 for _ in (repo_root / "qor" / "agents").rglob("*.md"))


def count_doctrines(repo_root: Path) -> int:
    return sum(1 for _ in (repo_root / "qor" / "references").glob("doctrine-*.md"))


def parse_readme_badges(readme_path: Path) -> dict[str, int]:
    text = readme_path.read_text(encoding="utf-8")
    out: dict[str, int] = {}
    for m in _BADGE_RE.finditer(text):
        key, val = m.group(1).lower(), int(m.group(2))
        out[key] = val
    return out


def check_currency(repo_root: Path, ledger_path: Path, tests_tolerance: int = 5) -> list[str]:
    """Return list of mismatch strings; empty list = clean."""
    declared = parse_readme_badges(repo_root / "README.md")
    truth = {
        "tests": count_tests(repo_root),
        "ledger": count_ledger_entries(ledger_path),
        "skills": count_skills(repo_root),
        "agents": count_agents(repo_root),
        "doctrines": count_doctrines(repo_root),
    }
    mismatches: list[str] = []
    for key, actual in truth.items():
        d = declared.get(key)
        if d is None:
            mismatches.append(f"{key}: README has no badge")
            continue
        if key == "tests":
            if abs(d - actual) > tests_tolerance:
                mismatches.append(f"tests: README declares {d}, truth {actual} (tolerance ±{tests_tolerance})")
        else:
            if d != actual:
                mismatches.append(f"{key}: README declares {d}, truth {actual}")
    return mismatches


def main() -> int:
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo-root", type=Path, default=Path.cwd())
    ap.add_argument("--ledger", type=Path, default=Path("docs/META_LEDGER.md"))
    args = ap.parse_args()
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
```

#### 2. `qor/scripts/attribution.py` — add `commit_trailer_compact`

```python
def commit_trailer_compact(model: str, *, model_email: str | None = None) -> str:
    """Return just the Co-Authored-By: line for low-signal commits.

    Used on plan/audit/implement commits per the tiered usage policy. Seal
    commits use the full `commit_trailer()` instead.
    """
    email = _MODEL_EMAIL if model_email is None else model_email
    return f"Co-Authored-By: {model} <{email}>"
```

#### 3. `qor/references/doctrine-attribution.md` — `## Tiered usage` section

Insert after the existing canonical-strings section:

```markdown
## Tiered usage

The canonical strings above define the *content* of attribution. This section defines *which form is required at which surface*, so the full canonical form is reserved for high-signal places (seal commits, PR descriptions) and low-signal commits get a compact form. Avoids 12-line boilerplate per phase across 4 commits while preserving attribution where reviewers actually read it.

| Surface | Required form | Rationale |
|---|---|---|
| Seal commit (`seal: phase NN ...`) | Full canonical (emoji + Qor-logic line + `Co-Authored-By:`) | One per phase. Marks the substantiated artifact. |
| Plan/audit/implement commits | `Co-Authored-By:` only (from `commit_trailer_compact`) | Bilineage established by the seal commit they chain into. Low signal-per-commit. |
| Merge commit | Untouched | GitHub auto-generates; outside operator authoring surface. |
| PR description | Full canonical PR-body footer | Reviewer-facing. Highest-context surface. |
| CHANGELOG entry | `_Built via [Qor-logic SDLC](url)._` once per `## [X.Y.Z]` header | Per-version, not per-entry. Reader scans CHANGELOG version-by-version. |
| GitHub release notes | Once per release | Same rationale as CHANGELOG. |

Locked by `tests/test_attribution_tiered_usage.py`. Cutoff for CHANGELOG: versions ≥ 0.36.0; older sections grandfathered.
```

#### 4. `ATTRIBUTION.md` — quickref `## Tiered usage` block

Add a small section after the existing canonical-strings blocks:

```markdown
## Tiered usage (quickref)

| Surface | Form |
|---|---|
| Seal commit | Full canonical (3 lines) |
| Plan/audit/implement | `Co-Authored-By:` only |
| PR description | Full PR-body footer |
| CHANGELOG version section | `_Built via [Qor-logic SDLC](url)._` |

Full table and rationale: [doctrine-attribution.md §"Tiered usage"](qor/references/doctrine-attribution.md).
```

#### 5. `qor/skills/governance/qor-substantiate/SKILL.md` — Step 6.5 hardening

Existing Step 6.5 prose extended with:

```markdown
**Phase 49 addition: README badge currency check (release-class only)**. When `plan_artifact.change_class ∈ {feature, breaking}`, run `python -m qor.scripts.badge_currency --repo-root . --ledger docs/META_LEDGER.md`. Non-zero exit ABORTs seal — the operator must update the literal-count badges (Tests, Ledger, Skills, Agents, Doctrines) to match current truth before re-running `/qor-substantiate`. Hotfix is exempt (matches `_RELEASE_CLASSES` semantics).

Bash one-liner:

\`\`\`bash
if [[ "${CHANGE_CLASS}" == "feature" || "${CHANGE_CLASS}" == "breaking" ]]; then
  python -m qor.scripts.badge_currency --repo-root . --ledger docs/META_LEDGER.md || { echo "ABORT: README badge currency mismatch"; exit 1; }
fi
\`\`\`
```

#### 6. `qor/references/doctrine-governance-enforcement.md` — `## Badge currency` subsection

Add under §"release-doc currency" (Phase 33's section) or as a new subsection:

```markdown
### Badge currency (Phase 49 wiring)

Feature and breaking phases MUST update README literal-count badges (Tests, Ledger, Skills, Agents, Doctrines) to match current truth. Verified by `qor/scripts/badge_currency.py` invoked at `/qor-substantiate` Step 6.5; ABORTs seal on mismatch. Hotfix exempt. Locked at the test layer by `tests/test_readme_badge_currency.py`. Dynamic badges (PyPI, Python version, License, NIST, OWASP, Doc Tier) are not parsed.
```

#### 7. `CHANGELOG.md` — `[Unreleased]` entry + retroactive attribution lines

Under `[Unreleased]`:

```markdown
### Added
- **Tiered attribution-trailer policy** (Phase 49): defines required form per surface — seal commits and PR descriptions use full canonical; plan/audit/implement commits use compact `Co-Authored-By:` only; CHANGELOG and release notes once per version. New `qor.scripts.attribution.commit_trailer_compact()` helper. Locked by `tests/test_attribution_tiered_usage.py` walking last 10 commits + CHANGELOG versions, with strip-and-fail negative-paths per Phase 46 doctrine. Closes G-3 from `docs/compliance-re-evaluation-2026-04-29.md`.
- **README badge currency enforcement** (Phase 49): new `qor/scripts/badge_currency.py` parses README literal-count badges (Tests, Ledger, Skills, Agents, Doctrines) and asserts them against current truth. Wired into `/qor-substantiate` Step 6.5: ABORTs seal on mismatch when `change_class ∈ {feature, breaking}`. Hotfix exempt. Locked by `tests/test_readme_badge_currency.py` (5 tests) + `tests/test_substantiate_badge_currency_wiring.py` (3 defensive proximity-anchor tests). Closes G-4.
```

The post-cutoff once-per-version attribution line is added under the new `## [0.36.0]` header on seal.

#### 8. Variant regeneration

```bash
python -m qor.scripts.dist_compile
python -m qor.scripts.check_variant_drift
```

## CI Commands

Operator must run locally before substantiate:

- `python -m pytest tests/test_attribution_tiered_usage.py tests/test_readme_badge_currency.py tests/test_substantiate_badge_currency_wiring.py -v` — phase-specific tests, run twice for determinism.
- `python -m qor.scripts.badge_currency --repo-root . --ledger docs/META_LEDGER.md` — manually invoke the new currency check; verify it reports current state correctly.
- `python -m pytest tests/test_skill_doctrine.py tests/test_plan_schema_ci_commands.py tests/test_doctrine_test_functionality.py tests/test_compile.py tests/test_release_doc_currency.py -v` — schema/doctrine/compile guards.
- `python -m qor.scripts.check_variant_drift` — explicit no-drift after dist_compile.
- `python -m pytest tests/ -v` — full suite (catch any adjacent doctrine-test coupling).
- `python -m qor.reliability.seal_entry_check --ledger docs/META_LEDGER.md --plan docs/plan-qor-phase49-attribution-tiering-and-badge-enforcement.md` — Phase 47 seal-entry-check verifies the new ledger entry on substantiate.
