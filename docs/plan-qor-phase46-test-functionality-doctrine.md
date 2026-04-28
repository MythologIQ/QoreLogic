# Plan: Phase 46 — test-functionality doctrine

**change_class**: feature
**target_version**: v0.32.0
**doc_tier**: standard
**pass**: 1

**Scope**: Codify the "test functionality, not presence" principle as a first-class QorLogic doctrine (`qor/references/doctrine-test-functionality.md`), wire enforcement language into the four SDLC gate skills (`/qor-plan`, `/qor-audit`, `/qor-implement`, `/qor-substantiate`), update `CLAUDE.md` Authority, and lock the wiring with proximity-anchored doctrine tests.

**Rationale**: Phase 45 (attribution-trailer convention) shipped doc-consistency tests that asserted only string-membership (`assert <string> in <file_text>`). The user surfaced that the same anti-pattern is already documented as `SG-035` ("doctrine-content test unanchored"), yet QorLogic's own gate skills don't enforce it. Result: a presence-only test can clear `/qor-audit` PASS, satisfy `/qor-implement` TDD-Light (one assertion), and seal under `/qor-substantiate` while catching nothing. Memory file `feedback_test_functionality.md` captures the user framing.

**Why mechanical enforcement now**: SG-035 lives in the countermeasures catalog but the catalog only gets consulted if the audit pass already exists. The four skills currently have no pass / step / checklist that distinguishes "test invokes the unit" from "test asserts a string is present." Until each gate carries explicit language, manual vigilance is the only defense — exactly the pattern Phase 13's "Rule = Test" doctrine warns against.

**terms_introduced**:
- term: presence-only test
  home: qor/references/doctrine-test-functionality.md
- term: functionality test
  home: qor/references/doctrine-test-functionality.md

**boundaries**:
- limitations: doctrine and skill-prompt wiring only; no runtime AST-based presence-only detector ships this phase. Skill prompts and tests rely on operator vigilance plus proximity-anchored prompt language. A runtime detector is candidate work for a later phase if the prompt-level enforcement proves insufficient.
- non_goals: rewriting Phase 45 attribution-trailer tests; promoting SG-035 narrative entries into structured form beyond the new doctrine cross-reference; shipping a CLI tool that scans test files.
- exclusions: `/qor-audit` Step 3 schema-coverage gap (the Phase 45 audit ran six structural passes but missed `**change_class**` enum and `## CI Commands` capitalization, which are enforced by `tests/test_skill_doctrine.py` and `tests/test_plan_schema_ci_commands.py`). Out of scope for Phase 46; queued as Phase 47.

## Open Questions

None.

## Phase 1 — author doctrine + wire skills + lock with tests

### Affected Files

Tests authored first (TDD; verified RED before implementation):

- `tests/test_doctrine_test_functionality.py` — new. Eight proximity-anchored assertions (one per surface). Each test reads the target file, locates the named section header, and asserts the expected enforcement phrase appears within a bounded span of that header. Pattern follows SG-035 countermeasure: `re.search(r"<section>.{0,N}<phrase>", body, re.DOTALL)`. Negative-path test included (strip the section, prove the assertion fails) so the doctrine test cannot itself become presence-only.

Source surfaces:

- `qor/references/doctrine-test-functionality.md` — new. Sections: `## Principle`, `## Definitions` (presence-only test, functionality test), `## Rule`, `## Anti-patterns` (with verified Phase 45 instance + SG-035 cross-reference), `## Verification mechanisms`, `## Update protocol`. Mirrors the existing `doctrine-test-discipline.md` structure for consistency.
- `CLAUDE.md` — Authority line gains the new doctrine reference alongside `test-discipline`.
- `qor/skills/sdlc/qor-plan/SKILL.md` — Step 4 "Do NOT include" gets one bullet: "Tests that only assert presence (file existence, string-in-file, function-defined) without invoking the unit and verifying its output." Step 5 "Review Plan" gets one checklist item: "Each unit test description names the behavior it confirms (the unit's output for a given input), not the artifact it expects to find."
- `qor/skills/governance/qor-audit/SKILL.md` — new "#### Test Functionality Pass" inserted between "#### Section 4 Razor Pass" and "#### Dependency Audit". Veto criterion: "Any planned test that asserts only file existence, substring presence, or structural placement without invoking the unit and validating its output → VETO." Maps to existing `findings_categories` enum value `test-failure` (no schema migration needed). Required next action: Governor amend plan, re-run `/qor-audit`.
- `qor/skills/sdlc/qor-implement/SKILL.md` — Step 5 (TDD-Light) gains an explicit clause: "The failing test MUST invoke the unit under test and assert against its output. Tests that only check artifact existence (e.g., `assert path.exists()`, `assert <string> in <file_text>`) do not satisfy TDD-Light." Step 9 (Complexity Self-Check) gains a scan: "For every newly-added test, confirm the test body calls the unit under test (function/method/CLI) and the assertion compares against the call's return value or observable side-effect. Bare `assert <substring> in <file_text>` for the unit's behavior is a defect; flag and fix before declaring completion."
- `qor/skills/governance/qor-substantiate/SKILL.md` — Step 4 (Functional Verification) "#### Test Audit" subsection gains a presence-only review checklist: substantiation refuses to seal if any test added in the current phase is presence-only for the unit it claims to verify. References doctrine for the rule and SG-035 for the verified anti-pattern.

Variant regeneration (mechanical):

- `qor/dist/variants/{claude,codex,gemini,kilo-code}/skills/qor-plan/SKILL.md`
- `qor/dist/variants/{claude,codex,gemini,kilo-code}/skills/qor-audit/SKILL.md`
- `qor/dist/variants/{claude,codex,gemini,kilo-code}/skills/qor-implement/SKILL.md`
- `qor/dist/variants/{claude,codex,gemini,kilo-code}/skills/qor-substantiate/SKILL.md`
- `qor/dist/manifest.json` and per-variant `manifest.json` (auto-emitted by `dist_compile`)

Regenerated via `BUILD_REGEN=1 python qor/scripts/dist_compile.py`. The existing `tests/test_compile.py` and `qor/scripts/check_variant_drift.py` already lock the no-drift contract.

CHANGELOG:

- `CHANGELOG.md` — `[Unreleased]` populated with Phase 46 narrative entry under `### Added`. Stamped to `[0.32.0]` at `/qor-substantiate` Step 7.6.

### Unit Tests

TDD order — every test below is authored first, run RED against current source, then GREEN after the corresponding source edit. Each test invokes the file-read and the regex search, and the assertion compares the regex-match result against the expected behavior — no test in this file is itself presence-only on its own subject (anchor + section-strip negative-path proves it).

- `test_doctrine_file_exists_with_required_sections` — reads `qor/references/doctrine-test-functionality.md`. Asserts each of `## Principle`, `## Definitions`, `## Rule`, `## Anti-patterns`, `## Verification mechanisms`, `## Update protocol` appears as a heading. Then strips the body of one section (in-memory mutation) and asserts the same check fails — proves the section-presence assertion is anchored, not blind substring.
- `test_doctrine_anti_patterns_section_cites_sg_035_and_phase_45` — proximity-anchor: `re.search(r"## Anti-patterns.{0,2000}SG-035", body, re.DOTALL)` and the same for `Phase 45`. Negative-path: strip `## Anti-patterns` body and assert FAIL.
- `test_claude_md_authority_references_test_functionality_doctrine` — proximity-anchor on the `## Authority` section: must contain `doctrine-test-functionality.md`. Negative-path: strip Authority body and assert FAIL.
- `test_qor_plan_step4_forbids_presence_only_tests` — proximity-anchor: locate `### Step 4: Avoid Common Pitfalls` header in `qor/skills/sdlc/qor-plan/SKILL.md`, assert phrase `tests that only assert presence` (case-insensitive) appears within 1500 chars of header. Negative-path: strip Step 4 body and assert FAIL.
- `test_qor_plan_step5_review_lists_behavior_naming` — proximity-anchor: locate `### Step 5: Review Plan` header, assert phrase `names the behavior it confirms` (case-insensitive) appears within 1500 chars. Negative-path strip-and-fail.
- `test_qor_audit_has_test_functionality_pass_between_razor_and_dependency` — locate `#### Section 4 Razor Pass` and `#### Dependency Audit` headers in `qor/skills/governance/qor-audit/SKILL.md`. Assert: `#### Test Functionality Pass` appears between them (positional, not just present). Strip the Test Functionality Pass section and assert the positional check FAILs.
- `test_qor_audit_test_functionality_pass_states_veto_criterion` — proximity-anchor on `#### Test Functionality Pass` header: phrases `presence-only` AND `VETO` AND `invoking the unit` all appear within 1500 chars of that header. Negative-path strip-and-fail.
- `test_qor_implement_step5_requires_unit_invocation` — proximity-anchor on `### Step 5: TDD-Light` header in `qor/skills/sdlc/qor-implement/SKILL.md`: phrase `invoke the unit under test` AND `assert against its output` within 1500 chars. Strip-and-fail.
- `test_qor_implement_step9_scans_for_presence_only_tests` — proximity-anchor on `### Step 9: Complexity Self-Check` header: phrase `presence-only` OR `assert .* in .*file_text` (regex) within 1500 chars. Strip-and-fail.
- `test_qor_substantiate_seal_gate_blocks_presence_only_tests` — proximity-anchor on `#### Test Audit` subsection header in `qor/skills/governance/qor-substantiate/SKILL.md`: phrases `presence-only` AND `refuses to seal` (or `seal aborts` / `ABORT`) within 2000 chars. Strip-and-fail.

Variant-drift coverage is already provided by `tests/test_compile.py`; no new test needed for the variant regeneration. Doctrine-skill cross-references are covered by existing `tests/test_skill_doctrine.py::test_skill_local_references_files_exist`; the new doctrine file is at the references root, not under a skill, so the new test in `test_doctrine_test_functionality.py` covers its existence and structure.

### Changes

#### 1. `qor/references/doctrine-test-functionality.md` (new)

Structure (terse, mirrors `doctrine-test-discipline.md`):

```markdown
# Doctrine: Test Functionality (not Presence)

**Source**: Phase 45 v1 lesson — attribution-trailer doc-consistency tests asserted only `<string> in <file_text>`. Cross-references SG-035 (doctrine-content test unanchored) in `qor/references/doctrine-shadow-genome-countermeasures.md`.

## Principle

A test must verify the unit under test does the right thing. Asserting only that a file exists, a string appears in a file, a function is defined, or a configuration key is set is insufficient — the test passes vacuously if the artifact survives but the behavior breaks.

## Definitions

- **Presence-only test**: assertion is solely about the existence or textual presence of an artifact (file, substring, attribute, declaration). The unit under test is not invoked; no output is compared.
- **Functionality test**: the test invokes the unit (function call, CLI subprocess, helper rendering, parser pass) and asserts the call's return value or observable side-effect against an expected value computed from the inputs.

## Rule

Every test of a unit's behavior MUST invoke that unit and assert against its output. Drift-guards (output-vs-documentation surface checks) are acceptable as auxiliary tests, but the primary test of the unit's behavior MUST be a functionality test, not a presence check.

Acceptance question: "If the unit's behavior were silently broken but the artifact still existed, would this test fail?" If no, the test is presence-only.

## Anti-patterns (verified instances)

| Anti-pattern | Where seen | Lesson |
|---|---|---|
| Substring-only doc-consistency check | Phase 45 attribution-trailer tests | A `Co-Authored-By:` substring presence check passes even if `git interpret-trailers --parse` would reject the rendered output. The behavioral test must run `git interpret-trailers --parse` (or the equivalent parser the runtime relies on) and assert the parsed output. |
| Doctrine-content test unanchored | SG-035 (Phase 15 v1 Entry #36 V-2) | Same family: substring presence with no anchor passes when the doctrine section is absent but the keyword co-occurs elsewhere. Anchor checks to the section header. |

## Verification mechanisms

- `tests/test_doctrine_test_functionality.py` locks each gate skill's enforcement language to its section header. Every assertion is paired with a strip-and-fail negative-path test, so the doctrine test cannot itself decay into a presence-only check.
- `/qor-plan` Step 4 forbids presence-only test descriptions in plan files; Step 5 reviews behavior-naming.
- `/qor-audit` Test Functionality Pass vetoes any plan whose described tests do not invoke the unit.
- `/qor-implement` Step 5 (TDD-Light) requires the failing test invoke the unit; Step 9 scans newly-added tests for the `assert <substring> in <file_text>` family.
- `/qor-substantiate` Step 4 Test Audit refuses to seal if a phase-added test is presence-only for the unit it claims to cover.

## Update protocol

When a new presence-only failure mode emerges, append to the Anti-patterns table with a where-seen citation. The doctrine grows with the project's failure history.
```

#### 2. `CLAUDE.md` Authority line

Append the new doctrine link immediately after `test-discipline`:

```diff
-User instructions override this file. Full doctrines: [token-efficiency](qor/references/doctrine-token-efficiency.md), [test-discipline](qor/references/doctrine-test-discipline.md), [governance-enforcement](qor/references/doctrine-governance-enforcement.md). Bundle protocol: [workflow-bundles](qor/gates/workflow-bundles.md). Skill handoff matrix: [delegation-table](qor/gates/delegation-table.md).
+User instructions override this file. Full doctrines: [token-efficiency](qor/references/doctrine-token-efficiency.md), [test-discipline](qor/references/doctrine-test-discipline.md), [test-functionality](qor/references/doctrine-test-functionality.md), [governance-enforcement](qor/references/doctrine-governance-enforcement.md). Bundle protocol: [workflow-bundles](qor/gates/workflow-bundles.md). Skill handoff matrix: [delegation-table](qor/gates/delegation-table.md).
```

#### 3. `qor/skills/sdlc/qor-plan/SKILL.md` — Step 4 + Step 5

Step 4 "Do NOT include" gains one bullet at the end of the existing list:

```markdown
- Tests that only assert presence (file existence, `<substring> in <file_text>`, function-defined) without invoking the unit and verifying its output (`qor/references/doctrine-test-functionality.md`)
```

Step 5 "Review Plan" gains one checklist item appended to the existing bullets:

```markdown
- [ ] Each unit test description names the behavior it confirms (the unit's output for a given input), not the artifact it expects to find. Per `qor/references/doctrine-test-functionality.md`.
```

#### 4. `qor/skills/governance/qor-audit/SKILL.md` — Test Functionality Pass

Insert a new pass between "#### Section 4 Razor Pass" (ends after the table + VETO line) and "#### Dependency Audit":

```markdown
#### Test Functionality Pass

For every unit test described in the plan, verify the description names the behavior the test confirms by invoking the unit, not just an artifact it expects to find.

Veto criterion: any planned test that asserts only file existence, substring presence, or structural placement without invoking the unit and validating its output → VETO. Per `qor/references/doctrine-test-functionality.md` and SG-035.

```markdown
### Test Functionality Audit

| Test description | Invokes unit? | Asserts on output? | Verdict |
| ---------------- | ------------- | ------------------ | ------- |
| [test name]      | [yes/no]      | [yes/no]           | [PASS/VETO] |
```

**Any presence-only test → VETO with `test-failure` category**.

**Required next action:** Governor: amend plan to replace presence-only tests with functionality tests (invoke the unit, assert against output), re-run `/qor-audit`. Per `qor/references/doctrine-audit-report-language.md`, this is a **Plan-text** ground.
```

#### 5. `qor/skills/sdlc/qor-implement/SKILL.md` — Step 5 + Step 9

Step 5 (TDD-Light) gains a new paragraph after the existing constraint:

```markdown
**Test functionality, not presence**: the failing test MUST invoke the unit under test (function call, CLI subprocess, helper render) and assert against its output. Tests that only check artifact existence (`assert path.exists()`, `assert <substring> in <file_text>`, `assert hasattr(...)`) do not satisfy TDD-Light. Per `qor/references/doctrine-test-functionality.md`.
```

Step 9 (Complexity Self-Check) gains a new bullet inside the for-each-file checklist:

```markdown
  - For every newly-added test in this file, confirm the test body invokes the unit under test and the assertion compares against the call's return value or observable side-effect. Bare `assert <substring> in <file_text>` for the unit's behavior is a presence-only test; flag and rewrite as a functionality test before declaring completion. Per `qor/references/doctrine-test-functionality.md`.
```

#### 6. `qor/skills/governance/qor-substantiate/SKILL.md` — Step 4 Test Audit

The "#### Test Audit" subsection (currently a Glob + Read pointer with template reference) gains an explicit gate clause:

```markdown
**Presence-only seal gate**: substantiation refuses to seal if any test added in the current phase is presence-only for the unit it claims to verify. Operator runs the acceptance question — "If the unit's behavior were silently broken but the artifact still existed, would this test fail?" — against each new test. Any "no" answer aborts seal. The operator amends the test to invoke the unit and assert against its output, then re-runs `/qor-substantiate`. Per `qor/references/doctrine-test-functionality.md` and SG-035.
```

#### 7. Variant regeneration

After source edits land:

```bash
BUILD_REGEN=1 python qor/scripts/dist_compile.py
```

Verify no drift remains:

```bash
python qor/scripts/check_variant_drift.py
```

#### 8. CHANGELOG entry

`[Unreleased]` populated under `### Added`:

```markdown
- **Test functionality doctrine** (Phase 46): new `qor/references/doctrine-test-functionality.md` codifying the "test functionality, not presence" principle and wiring enforcement language into the four SDLC gate skills (`/qor-plan` Steps 4 + 5, `/qor-audit` new Test Functionality Pass, `/qor-implement` Steps 5 + 9, `/qor-substantiate` Step 4 Test Audit). Cross-references SG-035 ("doctrine-content test unanchored"). Locked by `tests/test_doctrine_test_functionality.py` with proximity-anchored regex assertions and strip-and-fail negative-path tests.
```

## CI Commands

Operator must run locally before substantiate:

- `python -m pytest tests/test_doctrine_test_functionality.py -v` — phase-specific doctrine tests (run twice in a row for determinism per `qor/references/doctrine-test-discipline.md` Rule 2).
- `python -m pytest tests/test_skill_doctrine.py tests/test_plan_schema_ci_commands.py -v` — verifies the plan itself satisfies the existing skill-doctrine and plan-schema rules (the audit-blind-spot from Phase 45).
- `python -m pytest tests/test_compile.py -v` — variant compile contract.
- `python qor/scripts/check_variant_drift.py` — explicit no-drift check after `dist_compile`.
- `python -m pytest tests/ -v` — full suite (catch any adjacent doctrine-test coupling).
