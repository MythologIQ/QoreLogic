# Plan: Phase 48 — script discoverability + qor-logic rename + /qor-help conversational mode

**change_class**: feature
**target_version**: v0.35.0
**doc_tier**: standard
**pass**: 1

**Scope**: Three coupled UX/install/discovery improvements.

(A) **Script discoverability post-install**: convert the three remaining path-form `python qor/scripts/<name>.py` invocations in skill prompts to `python -m qor.scripts.<name>` so they resolve against the installed package from any CWD. Strengthen `tests/test_installed_import_paths.py` with a new lint catching the path-form for both `qor/scripts/` and `qor/reliability/`. Update `doctrine-governance-enforcement.md` §138 to make the `python -m` rule cover both directories (currently only `reliability/`).

(B) **Rename `qorlogic` CLI → `qor-logic`**: introduce `qor-logic` as the canonical entry point. Retain `qorlogic` as a backwards-compat alias entry point (operator's existing scripts/muscle memory keep working). Update every operator-facing doc/skill/help-string/print statement to invoke `qor-logic`. Source-code prose comments updated to "qor-logic CLI". Filesystem state paths (`.qorlogic/config.json`, `.qorlogic-installed.json`) remain unchanged — those are operator data state, not naming.

(C) **`/qor-help` conversational evolution**: keep the bare `/qor-help` static catalog (intro + commands tables + ASCII SDLC flow chart + "Using /qor-help" subsection). Add two new invocation modes:

- `/qor-help --stuck`: state-aware. Skill reads `.qor/session/current` and the current session's gate artifacts under `.qor/gates/<sid>/*.json` to infer SDLC position (which artifacts exist, which is most recent, what the latest verdict was). Recommends the next skill with one-sentence rationale. No file writes.
- `/qor-help -- "<free-form question>"`: question-routing. Skill takes the operator's question, considers the current session state (mirror of `--stuck`'s state-read), then answers with the most relevant skill(s) and the rationale linking the question to the catalog. The LLM running the skill performs the routing — the skill prompt provides the protocol, the catalog, and the state-read recipe.

Both modes are markdown-only — execution is by the LLM following the skill protocol. No new Python helpers required. The catalog already lives in the bare `/qor-help` body and is reused.

**Rationale**:
- (A): Operator install via `pip install qor-logic` puts the package on `sys.path` but does NOT put `qor/scripts/<name>.py` filesystem paths in the operator's CWD. Skills calling `python qor/scripts/check_shadow_threshold.py` fail with "No such file" against any CWD that isn't the dev repo root. Phase 35 already shipped this fix for `qor/reliability/`; Phase 48 closes the same gap for `qor/scripts/`.
- (B): "qorlogic" (no dash) is inconsistent with the package name `qor-logic`, the PyPI project name, and the GitHub repo `MythologIQ-Labs-LLC/Qor-logic`. The mismatch confuses LLMs (skill prompts written by one phase reference one form; LLM output in another phase emits the other) and human users. Per user direction: alias is acceptable, primary command is `qor-logic`.
- (C): The current `/qor-help` is a static catalog. Operators new to QorLogic — or returning after time away — frequently know "I'm somewhere in the middle of work" but don't know which skill comes next, or have a specific question without a clear command match. The catalog answers "what skills exist"; it does not answer "which one applies to me right now". Adding `--stuck` (state-aware) and `-- "<question>"` (free-form routing) closes that gap without expanding the surface area beyond a single skill — both modes reuse the existing catalog and read existing gate artifacts.

**terms_introduced**:
- term: canonical CLI invocation
  home: README.md
- term: stuck mode
  home: qor/skills/meta/qor-help/SKILL.md
- term: question mode
  home: qor/skills/meta/qor-help/SKILL.md

**boundaries**:
- limitations: filesystem state paths (`.qorlogic/config.json`, `.qorlogic-installed.json`) and the persisted-record marker do not rename — operator data integrity. The setuptools entry-point alias gives operators both commands; existing automation continues to work. `/qor-help` conversational modes are markdown-only — no Python parser, no LLM API call, no new dependency. State-read uses existing `.qor/gates/<sid>/*.json` artifacts.
- non_goals: rewriting historical references in `docs/META_LEDGER.md`, `docs/plan-qor-phase*.md`, `CHANGELOG.md` past entries, or archived audit reports. These are immutable history. `/qor-help --stuck` does not auto-invoke other skills (constraint inherited from existing `/qor-help` "NEVER execute other skills" rule); it recommends only.
- exclusions: Gemini variant `commands/*.toml` files mentioning `qorlogic` regenerate from source skills via `dist_compile`; they are not edited directly. `/qor-help` mode-routing logic is prose-only; a future phase may promote routing to a Python helper if the prose-only path proves unreliable.

## Open Questions

None.

## Phase 1 — script discoverability and CLI rename

### Affected Files

Tests authored first (TDD; verified RED before source edits):

- `tests/test_installed_import_paths.py` — add `test_no_path_form_qor_scripts_invocations` and `test_no_path_form_qor_reliability_invocations` (the second formalizes what the existing hyphen-only check missed). The patterns scan skill prose for `python qor/scripts/<name>.py` and `python qor/reliability/<name>.py` of any name; offenders fail with the canonical fix string.
- `tests/test_cli_rename.py` — new. Asserts `[project.scripts]` in `pyproject.toml` declares both `qor-logic` and `qorlogic` mapping to `qor.cli:main`. Asserts `qor.cli` exposes a `main` callable. Subprocess-level smoke test: invoke the entry point's `main([" --version"])` directly with `argv = ["--version"]` and assert exit code 0 and stdout matches `qor-logic <semver>` (note: program name updates).
- `tests/test_cli_help_uses_qor_logic.py` — new. Invokes `qor.cli.main(["--help"])` and asserts the help text emits `prog="qor-logic"` not `qorlogic`. Negative-path: a mutated CLI module that emits `qorlogic` is caught.
- `tests/test_doctrine_governance_section_138_covers_both_dirs.py` — new. Proximity-anchored regex on §138 of `doctrine-governance-enforcement.md`: phrase `qor/reliability/` AND `qor/scripts/` AND `python -m` all appear within span of the §138 header. Strip-and-fail negative-path test paired (per Phase 46 doctrine).
- `tests/test_qor_help_conversational.py` — new. Locks the `/qor-help` skill body's three modes with proximity-anchored assertions (intro section, ASCII flow chart, "Using /qor-help" subsection, `--stuck` protocol, `-- "<question>"` protocol). Functionality: invokes the skill body's mode-router prose by reading the file, parsing the protocol structure (header positions and content regex), and asserting against the parse output. Each positive assertion paired with a strip-and-fail negative-path test per Phase 46 doctrine. Specific assertions include: ASCII chart contains the canonical SDLC chain `research`, `plan`, `audit`, `implement`, `substantiate` in order; `--stuck` protocol mentions reading `.qor/gates/<sid>/*.json`; `-- "<question>"` protocol mentions free-form routing using the catalog. The chart is verified by extracting the fenced code block under the SDLC Flow header and asserting the substring order — not just presence.

Source surfaces:

- `pyproject.toml`: `[project.scripts]` adds the new line `qor-logic = "qor.cli:main"`; existing `qorlogic = "qor.cli:main"` retained as alias.
- `qor/cli.py`: `prog="qorlogic"` → `prog="qor-logic"`. `--version` action's version string `f"qorlogic {__version__}"` → `f"qor-logic {__version__}"`. The init subparser help string `initialize .qorlogic/config.json` is documenting filesystem state (unchanged); leave the path literal but rephrase to `initialize the qor-logic config (.qorlogic/config.json)`.
- `qor/install.py`: docstring + 4 print/error strings mentioning `qorlogic compile`/`qorlogic install` → `qor-logic compile`/`qor-logic install`. The `.qorlogic-installed.json` filename stays (filesystem state).
- `qor/cli_policy.py`: docstrings/comments mentioning `qorlogic` updated to `qor-logic`. The `.qorlogic/config.json` filesystem path stays.
- `qor/seed.py`: docstring "Callable from the `qorlogic seed` CLI subcommand" → "qor-logic seed".
- `qor/hosts.py`: docstring "Host-to-install-path resolver for qorlogic CLI" → "qor-logic CLI".
- `qor/tone.py`: docstring reference `.qorlogic/config.json` is filesystem path — unchanged. Verify no command-form `qorlogic ...` mentioned.
- `qor/scripts/install_drift_check.py:72`: print `f"Fix: qorlogic install ..."` → `f"Fix: qor-logic install ..."`.
- `qor/skills/governance/qor-shadow-process/SKILL.md` lines 89, 101: replace `python qor/scripts/check_shadow_threshold.py` → `python -m qor.scripts.check_shadow_threshold`; same for `create_shadow_issue.py`.
- `qor/skills/governance/qor-process-review-cycle/SKILL.md` line 57: replace `python qor/scripts/check_shadow_threshold.py` → `python -m qor.scripts.check_shadow_threshold`.
- `qor/skills/meta/qor-help/SKILL.md`: rewrite for conversational mode. New top section: "Intro — How to use /qor-help" (3-4 sentences explaining the three modes). Insert new "## SDLC Flow" section above the existing "## SDLC Chain" table containing the ASCII flow chart (plain ASCII, no Unicode box-drawing). Existing tables (SDLC Chain, Memory & Meta, Governance, Migrated qore-*, Workflow Bundles) retained. New "## Modes" section after the catalog with three subsections: bare invocation (catalog dump), `## Mode: --stuck` (state-aware protocol), `## Mode: -- "question"` (free-form routing protocol). Replace the existing "## Quick Decision Tree" with a one-line pointer at the new ASCII flow chart and the `--stuck` mode. Constraint "NEVER execute other skills from within qor-help" preserved (recommend, never invoke).
- `qor/skills/**/*.md` — every `qorlogic <subcommand>` operator-facing invocation → `qor-logic <subcommand>`. Concrete files (per grep): qor-audit, qor-substantiate, qor-validate, qor-status, qor-tone, qor-plan SKILL.md.
- `qor/references/doctrine-governance-enforcement.md` §138: extend rule to cover BOTH `qor/scripts/` and `qor/reliability/`. Line 92 prose example `python qor/scripts/session.py new` → `python -m qor.scripts.session new`.
- `qor/references/doctrine-communication-tiers.md`, `doctrine-nist-ssdf-alignment.md`, `doctrine-prompt-resilience.md`, `glossary.md`, `skill-recovery-pattern.md`: update operator-facing invocations from `qorlogic ...` to `qor-logic ...`.
- `README.md`: update every operator-facing CLI invocation `qorlogic ...` → `qor-logic ...`. Quickstart, Usage, Examples, Troubleshooting all bear scrutiny.
- `tests/fixtures/skill_autonomous_good.md`, `tests/fixtures/skill_interactive_good.md`: update `qorlogic` → `qor-logic` in fixture text (these fixtures are exercise-of-skill-doctrine; their content represents canonical example of a "good" skill so should match new naming).
- Live test files (`tests/test_cli.py`, `test_cli_init_scope.py`, `test_cli_install_gemini.py`, `test_cli_seed.py`, `test_hosts_scope.py`, `test_packaging.py`, `test_phase21_harness.py`, `test_phase22_hosts.py`, `test_qor_validate_skill_references.py`, `test_skill_prerequisite_coverage.py`, `test_tone_config_persistence.py`): update assertion strings and subprocess argv from `qorlogic` to `qor-logic` where the test is checking operator-facing output. Subprocess invocations that exec the entry point: switch to `qor-logic`. Any test asserting `prog="qorlogic"` updated to `prog="qor-logic"`.

CHANGELOG:

- `CHANGELOG.md` `[Unreleased]` populated under `### Added` (the alias) and `### Changed` (the doctrine + invocations).

Variant regeneration:

- `qor/dist/variants/{claude,codex,gemini,kilo-code}/skills/**/SKILL.md` and `commands/*.toml` — auto-regenerated via `BUILD_REGEN=1 python -m qor.scripts.dist_compile`. Locked by `tests/test_compile.py`.

### Unit Tests

TDD order — every test below authored first, RED, then GREEN after the source edit. Each invokes the unit and asserts on output (not just artifact presence), per `qor/references/doctrine-test-functionality.md`.

- `test_no_path_form_qor_scripts_invocations` — walks `qor/skills/**/*.md`, applies `re.compile(r"python\s+qor/scripts/[a-z_]+\.py")` per line, fails with the offender list and the canonical fix template (`python -m qor.scripts.<name>`). Verifies the lint by mutating a fixture string in-memory and asserting the regex matches. **Invocation**: the test calls the regex, asserts on match output, not "assert offenders is None" — it counts offenders and reports zero.
- `test_no_path_form_qor_reliability_invocations` — companion lint scanning `python\s+qor/reliability/[a-z_]+\.py`. Existing hyphen-only check (`test_no_hyphen_named_reliability_invocations`) stays for backwards compat with its narrower charter; this new test catches snake_case path-form too.
- `test_pyproject_declares_both_qor_logic_and_qorlogic_entry_points` — parses `pyproject.toml` with `tomllib`, asserts `project.scripts` dict contains both keys, both pointing at `qor.cli:main`. Functional, not just textual: importable and dict-membership-checked.
- `test_cli_main_version_string_uses_qor_logic` — invokes `qor.cli.main` with `argv=["--version"]` (capturing stdout via `capsys`), asserts the captured string matches `r"^qor-logic \d+\.\d+\.\d+"`. Functionality test: it invokes the unit and asserts the output's content.
- `test_cli_help_text_uses_qor_logic_program_name` — invokes `qor.cli.main` with `argv=["--help"]`, captures stdout, asserts `qor-logic` appears in usage line and `qorlogic` does NOT appear (modulo the `.qorlogic/config.json` filesystem path mention, which is acceptable). Asserts on rendered help text content.
- `test_doctrine_governance_section_138_covers_both_scripts_and_reliability` — proximity-anchored regex on `doctrine-governance-enforcement.md` §138. Asserts `qor/reliability/` AND `qor/scripts/` AND `python -m qor.scripts.` AND `python -m qor.reliability.` all appear within the §138 span. Strip-and-fail negative-path test paired.
- `test_install_drift_check_emits_qor_logic_fix_string` — mocks the args, invokes `install_drift_check.main()` with the failure path, captures stdout, asserts the printed fix string contains `qor-logic install` and not `qorlogic install`. Functionality test of the print branch.
- `test_skill_prose_uses_qor_logic_for_cli_invocations` — walks `qor/skills/**/*.md`, scans for token-boundary `\bqorlogic\b ` (with trailing space — i.e., the CLI invocation form `qorlogic <subcommand>`, not the package-data filename `.qorlogic/`). Fails the lint if any operator-facing invocation still uses the old name. Note: `.qorlogic/` (filesystem path with leading dot) is excluded from the match because the regex requires word boundary on the LEFT — `.qorlogic` has `.` as the left boundary character, but `\b` matches between word and non-word characters; verify: `\b` at start of `qorlogic` after `.` is a word boundary because `.` is non-word. Hmm: this would still match. Use a tighter pattern: `(?<![./.])qorlogic\s+\w` matches only when not preceded by `.` or `/`. **Implementation**: use `re.compile(r"(?<![./])\bqorlogic\b\s+[a-z]")` so `qorlogic init` is matched but `.qorlogic/config.json` is not. Test the regex itself with positive and negative example strings before applying to skill bodies.

`/qor-help` conversational evolution tests:

- `test_qor_help_has_intro_section` — proximity-anchored regex: `## Intro` (or `## How to use /qor-help`) header followed within bounded span by phrases like `bare`, `--stuck`, and `-- "`. Strip-and-fail negative-path paired.
- `test_qor_help_has_ascii_sdlc_flow_chart` — finds the `## SDLC Flow` header, extracts the next fenced code block, asserts it contains the substrings `research`, `plan`, `audit`, `implement`, `substantiate` in left-to-right order via positional check. Asserts the chart is plain ASCII (no Unicode box-drawing characters via `body.encode('ascii')` round-trip on the chart fence; failure raises `UnicodeEncodeError`). Strip-and-fail negative-path paired.
- `test_qor_help_has_stuck_mode_protocol` — proximity-anchored on `## Mode: --stuck` header: phrases `.qor/gates/`, `session_id`, and `recommend` appear within span. Strip-and-fail negative-path paired.
- `test_qor_help_has_question_mode_protocol` — proximity-anchored on `## Mode: -- "` header (or its variant): phrases `free-form`, `catalog`, and `routing` appear within span. Strip-and-fail negative-path paired.
- `test_qor_help_constraint_no_execute_preserved` — proximity-anchored on `## Constraints` header: phrase `NEVER` appears with `execute other skills`. Locks the existing constraint against the rewrite — even with conversational modes, `/qor-help` recommends but does not invoke. Strip-and-fail negative-path paired.

### Changes

#### 1. `pyproject.toml` — add canonical entry point alongside alias

```diff
 [project.scripts]
-qorlogic = "qor.cli:main"
+qor-logic = "qor.cli:main"
+qorlogic = "qor.cli:main"
```

Both names install to bin dirs as wrappers around `qor.cli:main`. `qor-logic` is canonical.

#### 2. `qor/cli.py` — program name in argparse

```diff
-        prog="qorlogic",
+        prog="qor-logic",
```

```diff
-    parser.add_argument("--version", action="version", version=f"qorlogic {__version__}")
+    parser.add_argument("--version", action="version", version=f"qor-logic {__version__}")
```

The `init` subparser help: `"initialize .qorlogic/config.json"` → `"initialize the qor-logic config (.qorlogic/config.json)"` — keeps the literal path so existing automation reading the config from that path is unaffected.

#### 3. `qor/install.py` — operator-facing print/error strings

Module docstring + four print/error strings: rename `qorlogic compile`/`qorlogic install` → `qor-logic compile`/`qor-logic install`. Filesystem state filename `.qorlogic-installed.json` unchanged.

#### 4. `qor/cli_policy.py`, `qor/seed.py`, `qor/hosts.py`, `qor/tone.py` — docstrings

Update prose mentions of `qorlogic CLI` / `qorlogic seed` / etc. to `qor-logic`. Filesystem state paths `.qorlogic/config.json` literally unchanged.

#### 5. `qor/scripts/install_drift_check.py:72`

```diff
-    print(f"Fix: qorlogic install --host {args.host} --scope {args.scope}")
+    print(f"Fix: qor-logic install --host {args.host} --scope {args.scope}")
```

#### 6. Skill prompts — path-form invocations

Three replacements in two files:

- `qor/skills/governance/qor-shadow-process/SKILL.md:89`: `python qor/scripts/check_shadow_threshold.py` → `python -m qor.scripts.check_shadow_threshold`
- `qor/skills/governance/qor-shadow-process/SKILL.md:101`: `python qor/scripts/create_shadow_issue.py` → `python -m qor.scripts.create_shadow_issue`
- `qor/skills/governance/qor-process-review-cycle/SKILL.md:57`: same as 89

#### 7. Skill prompts — `qorlogic` operator invocations

Across qor-audit, qor-substantiate, qor-validate, qor-status, qor-tone, qor-plan (and any others surfaced by grep): every CLI invocation form `qorlogic <subcommand>` becomes `qor-logic <subcommand>`. Filesystem path mentions `.qorlogic/...` unchanged.

#### 8. `qor/references/doctrine-governance-enforcement.md`

§138 rewrite to make the rule symmetric across both dirs:

```markdown
2. **Snake_case helper modules, `python -m` invocation**. Scripts under `qor/scripts/` and `qor/reliability/` must be snake_case (`intent_lock.py`, `check_shadow_threshold.py`) so they are valid Python module names. Skills invoke them via `python -m qor.scripts.<name>` or `python -m qor.reliability.<name>` — never via filesystem path (`python qor/scripts/<name>.py` / `python qor/reliability/<name>.py`). Each module exposes a `main()` entry point and an `if __name__ == "__main__":` guard. Locked by `tests/test_installed_import_paths.py::test_no_path_form_qor_scripts_invocations`, `::test_no_path_form_qor_reliability_invocations`, `::test_no_hyphen_named_reliability_invocations`, and `::test_qor_reliability_modules_importable`.
```

Line 92 prose example: `python qor/scripts/session.py new` → `python -m qor.scripts.session new`.

#### 9. `qor/references/doctrine-communication-tiers.md`, `doctrine-nist-ssdf-alignment.md`, `doctrine-prompt-resilience.md`, `glossary.md`, `skill-recovery-pattern.md`

Operator-facing CLI invocations renamed `qorlogic` → `qor-logic`.

#### 10. README.md

Every operator-facing invocation `qorlogic <subcommand>` → `qor-logic <subcommand>`. Add a one-line "Note: `qorlogic` (no dash) is retained as a backwards-compat alias for existing automation; new docs all use `qor-logic`." in the Installation or Usage section.

#### 11. Live tests

Update assertion strings + subprocess argv from `qorlogic` → `qor-logic`. Tests asserting `prog="qorlogic"` updated to `prog="qor-logic"`. Subprocess invocations of the entry point switch to `qor-logic`. Tests covering operator-data filesystem state (`.qorlogic/...`) keep that literal.

#### 11.5 `/qor-help` conversational rewrite

Skill body restructured. Concrete shape:

```markdown
# /qor-help — Conversational catalog and SDLC navigator

## Intro — How to use /qor-help

Three modes:

- `/qor-help` — show the full command catalog and SDLC flow chart below.
- `/qor-help --stuck` — diagnose where the current session is in the SDLC and recommend the next skill, with rationale.
- `/qor-help -- "<your question>"` — answer a free-form question by routing to the most relevant skill(s), citing the catalog and (when relevant) current session state.

All three modes are read-only. /qor-help never invokes another skill — it recommends; you invoke.

## SDLC Flow

\`\`\`
                       [ /qor-status ]   <- diagnose at any time
                              |
              +---------------+---------------+
              |                               |
              v                               v
         (new work)                      (--stuck?)
              |                               |
              v                               v
   /qor-research                   read .qor/gates/<sid>/*.json
              |                       infer phase, recommend
              v
   /qor-plan ----> /qor-audit ----> /qor-implement ----> /qor-substantiate
                    |  ^                  |
                    |  | VETO             v
                    v  |               /qor-debug   (regression / hallucination)
                   amend                    |
                    |                       v
                    +--> /qor-refactor    /qor-organize
                    +--> /qor-remediate (after 3+ same-signature VETOs)

   Bundles: /qor-deep-audit, /qor-onboard-codebase, /qor-process-review-cycle
\`\`\`

## Catalog

[existing tables: SDLC Chain, Memory & Meta, Governance, Migrated qore-*, Workflow Bundles — unchanged]

## Mode: --stuck

Protocol:
1. Read `.qor/session/current` to obtain session_id.
2. Glob `.qor/gates/<session_id>/*.json` and read each.
3. Determine highest-rank artifact present (research < plan < audit < implement < substantiate).
4. If audit present, read its verdict (PASS/VETO) and findings_categories.
5. Map state to recommendation:
   - No artifacts -> /qor-research (or /qor-plan if research has been done out-of-gate).
   - plan.json only -> /qor-audit.
   - audit.json verdict=PASS -> /qor-implement.
   - audit.json verdict=VETO -> Governor amends plan per findings_categories; cite the required next action from doctrine-audit-report-language.md.
   - implement.json present -> /qor-substantiate.
   - substantiate.json present -> session sealed; recommend new /qor-plan or /qor-research.
6. Print one-paragraph recommendation: state observed, recommended skill, rationale, exact command.

No file writes. Routing is read-only inference.

## Mode: -- "question"

Protocol:
1. Capture the operator's question text (everything after `-- `).
2. Optionally perform the --stuck state-read for context.
3. Use the catalog above + state to identify the 1-3 most relevant skills.
4. Answer with: which skill(s) apply, why, exact command(s) to invoke, what the operator should expect to see.
5. If the question maps to no skill (e.g., asking about external tooling), say so plainly and suggest the closest fit.

The LLM running this skill is the routing engine. The catalog is the table above. Free-form question handling reuses the catalog as the source of truth — never invent skills.

## Constraints

- NEVER execute other skills from within qor-help (recommend, never invoke)
- NEVER write files
- ALWAYS recommend /qor-status when the operator's state is unclear and --stuck cannot resolve it (e.g., no .qor/ directory)
```

The existing `Quick Decision Tree` is removed; the `SDLC Flow` chart subsumes it. The `Constraints` section retains "NEVER execute other skills". The `Integration with S.H.I.E.L.D.` and `Success Criteria` sections retained, lightly updated to mention conversational modes.

#### 12. /qor-document run (doc consistency)

After all source edits and variant regen, invoke `/qor-document` to refresh public-facing docs (README, lifecycle, operations, architecture) for the rename. The skill produces a single edit pass over `docs/architecture.md`, `docs/lifecycle.md`, `docs/operations.md`, `docs/policies.md` aligning prose with the new canonical CLI name.

#### 13. Variant regeneration

```bash
BUILD_REGEN=1 python -m qor.scripts.dist_compile
python -m qor.scripts.check_variant_drift
```

#### 14. CHANGELOG entry

Under `[Unreleased]`:

```markdown
### Added
- **`qor-logic` canonical CLI** (Phase 48): new entry point alongside `qorlogic` (retained as alias). All operator-facing docs/help/skills updated to invoke `qor-logic`. Existing automation referencing `qorlogic` continues to work.
- **Conversational `/qor-help`** (Phase 48): `/qor-help` evolves from static catalog into a three-mode skill. Bare invocation shows the existing catalog plus a new ASCII SDLC flow chart and a "How to use /qor-help" intro. `/qor-help --stuck` reads `.qor/gates/<sid>/*.json` to infer the operator's SDLC position and recommend the next skill with rationale. `/qor-help -- "<free-form question>"` routes the question against the catalog and current state. All modes are read-only; recommendation only.

### Changed
- **Script discoverability** (Phase 48): the three remaining path-form `python qor/scripts/<name>.py` invocations in skill prose are now `python -m qor.scripts.<name>`, resolving against the installed package from any CWD. `doctrine-governance-enforcement.md` §138 updated to cover both `qor/scripts/` and `qor/reliability/`. New lint `tests/test_installed_import_paths.py::test_no_path_form_qor_scripts_invocations` prevents regression. Closes the gap left by Phase 35 (which fixed only `qor/reliability/`).
```

## CI Commands

Operator must run locally before substantiate:

- `python -m pytest tests/test_installed_import_paths.py tests/test_cli_rename.py tests/test_cli_help_uses_qor_logic.py tests/test_doctrine_governance_section_138_covers_both_dirs.py tests/test_qor_help_conversational.py -v` — phase-specific tests; run twice for determinism per `qor/references/doctrine-test-discipline.md`.
- `python -m pytest tests/test_cli.py tests/test_cli_init_scope.py tests/test_cli_install_gemini.py tests/test_cli_seed.py tests/test_packaging.py tests/test_phase21_harness.py tests/test_phase22_hosts.py tests/test_qor_validate_skill_references.py tests/test_skill_prerequisite_coverage.py tests/test_tone_config_persistence.py -v` — CLI/install-touching test suite with rename applied.
- `python -m pytest tests/test_skill_doctrine.py tests/test_plan_schema_ci_commands.py tests/test_doctrine_test_functionality.py tests/test_compile.py -v` — schema/doctrine/compile guards (validate plan + doctrine wiring + variant compile).
- `python -m qor.scripts.check_variant_drift` — explicit no-drift after dist_compile.
- `python -m pytest tests/ -v` — full suite (catch any adjacent doctrine-test coupling).
- `pip install -e . && qor-logic --version && qorlogic --version` — runtime smoke verifying both entry points exist and emit `qor-logic <semver>`.
