# Plan: Phase 50 — skill-prose filesystem validation

**change_class**: feature
**target_version**: v0.37.0
**doc_tier**: standard
**pass**: 1

**Scope**: Closes G-2 from `docs/compliance-re-evaluation-2026-04-29.md`. Skill prose that performs filesystem operations with operator-controlled identifiers (e.g., `/qor-help --stuck` reading `.qor/gates/<sid>/*.json`) must cite the canonical validator (`qor.scripts.session.SESSION_ID_PATTERN` / `qor.scripts.session.current()`) so the LLM running the skill follows the validated path. Phase 23 LOW-2/LOW-3 fixed the runtime; Phase 50 makes the skill-prose contract explicit and lint-locked.

**Rationale**:
- `/qor-help --stuck` currently reads `.qor/session/current` directly per its Mode protocol. `session.current()` exists and internally validates `SESSION_ID_PATTERN`. The skill prose tells the LLM to "read the file" without naming the helper, so a reasonable LLM following the protocol literally would NOT route through the validator. The validation is in the helper layer; the skill prose layer is silent.
- New attack surface (per the compliance report's G-2): if `.qor/session/current` is corrupted (operator error, malicious actor with write access to working directory, accidental edit), naive read + path concatenation passes unsanitized text to a glob. Phase 23 SESSION_ID_PATTERN catches malformed IDs, but only if the skill uses the helper. Doctrinal currency, not runtime gap.

**terms_introduced**:
- term: skill-prose filesystem validation
  home: qor/references/doctrine-owasp-governance.md

**boundaries**:
- limitations: lint test scans skill bodies for `.qor/gates/<` and `.qor/session/current` references; asserts the same body cites `qor.scripts.session`. False positives (e.g., a skill that legitimately mentions the path without operating on it) handled via narrow regex.
- non_goals: changing the runtime validator (Phase 23 already shipped); rewriting historical skills that don't touch `.qor/`; addressing the branch-protection ruleset `code_quality` rule (separate authorization needed).
- exclusions: G-1 (SSDF tag backfill) is queued as Phase 51 separately.

## Open Questions

None.

## Phase 1 — skill-prose validation contract

### Affected Files

Tests authored first (TDD; verified RED before source edits):

- `tests/test_skill_prose_filesystem_validation.py` — new. Three tests:
  - `test_skills_referencing_qor_gates_cite_session_validator` — walks `qor/skills/**/SKILL.md`; for any skill whose body contains `.qor/gates/<` or `.qor/session/current`, assert the same body also cites `qor.scripts.session` (helper module reference) OR `SESSION_ID_PATTERN` (validator constant). Functional: invokes regex-based scan, returns offender list, asserts empty.
  - `test_skill_prose_validation_doctrine_documented` — proximity-anchored regex on `qor/references/doctrine-owasp-governance.md` §A03: phrase `skill prose` AND `filesystem` AND `validate` (case-insensitive) appear within bounded span of the A03 header. Strip-and-fail negative-path paired.
  - `test_qor_help_stuck_mode_cites_session_helper` — proximity-anchored on `/qor-help` SKILL.md `## Mode: --stuck` header: phrase `qor.scripts.session` (or `session.current()`) within span. Strip-and-fail.

Source surfaces:

- `qor/skills/meta/qor-help/SKILL.md` Mode: --stuck protocol step 1 — replace "Resolve session_id from `.qor/session/current` (read the file)" with explicit invocation: "Resolve session_id via `qor.scripts.session.current()` (which reads `.qor/session/current` AND validates against `SESSION_ID_PATTERN`). If `current()` returns `None` (no marker, stale, or invalid format), recommend `/qor-status` and stop."
- `qor/references/doctrine-owasp-governance.md` §A03 — add a worked example after the existing LOW-2/LOW-3 paragraph: "Skill prose that performs filesystem operations with operator-controlled identifiers (e.g., session_id, event_id, plan paths) MUST cite the canonical validator helper (`qor.scripts.session.current()`, `qor.scripts.shadow_process.validate_event_id()`, `qor.scripts.governance_helpers.current_phase_plan_path()`). The runtime validator alone is insufficient — the skill prose must route the LLM through the helper. Locked by `tests/test_skill_prose_filesystem_validation.py`."

Variant regeneration:

- `qor/dist/variants/{claude,codex,gemini,kilo-code}/skills/qor-help/SKILL.md` — auto-regenerated.

### Unit Tests

TDD order — every test invokes the unit and asserts on output, per `qor/references/doctrine-test-functionality.md`.

- `test_skills_referencing_qor_gates_cite_session_validator` — invokes a regex scan, returns offender file list, asserts empty. Functional invocation; not presence-only.
- `test_skill_prose_validation_doctrine_documented` — proximity-anchor on doctrine; strip-and-fail negative-path paired (Phase 46 doctrine).
- `test_qor_help_stuck_mode_cites_session_helper` — proximity-anchor on Mode header; strip-and-fail paired.

### Changes

#### 1. `/qor-help` Mode: --stuck protocol step 1

```diff
-1. Resolve session_id from `.qor/session/current` (read the file). If absent, recommend `/qor-status` and stop.
+1. Resolve session_id via `qor.scripts.session.current()` (which reads `.qor/session/current` AND validates the content against `SESSION_ID_PATTERN`). If `current()` returns `None` (no marker, stale beyond TTL, or invalid format), recommend `/qor-status` and stop. Do not bypass the validator — naive `Path('.qor/session/current').read_text()` fails open on corrupted markers.
```

#### 2. `doctrine-owasp-governance.md` §A03 worked example

Append after the existing "Worked example" paragraph for A03:

```markdown
**Skill-prose worked example (Phase 50)**: `/qor-help --stuck` reads `.qor/gates/<session_id>/*.json` where `session_id` is the operator-controlled marker file `.qor/session/current`. The runtime validator `qor.scripts.session.SESSION_ID_PATTERN` exists (Phase 23 LOW-2 fix) but is enforced only when `session.current()` is invoked. Skill prose that bypasses the helper and reads the marker directly fails open on corrupted markers (operator-controlled paths reaching glob without sanitization). Mitigation: skill prose MUST cite `qor.scripts.session.current()` (or equivalent canonical helper) before any filesystem operation on operator-controlled identifiers. Locked by `tests/test_skill_prose_filesystem_validation.py::test_skills_referencing_qor_gates_cite_session_validator`.
```

#### 3. CHANGELOG

Under `[Unreleased]` (will be stamped to `[0.37.0]` at seal):

```markdown
### Added
- **Skill-prose filesystem validation contract** (Phase 50): closes G-2 from `docs/compliance-re-evaluation-2026-04-29.md`. Skill prose that performs filesystem operations on operator-controlled identifiers (e.g., `.qor/gates/<sid>/*.json`) MUST cite the canonical validator helper (`qor.scripts.session.current()`). `qor/references/doctrine-owasp-governance.md` §A03 gains a "Skill-prose worked example" paragraph; `/qor-help --stuck` Mode protocol step 1 routes through `session.current()` explicitly. Locked by `tests/test_skill_prose_filesystem_validation.py` (3 tests with proximity-anchor + strip-and-fail per Phase 46 doctrine).
```

#### 4. Variant regeneration

```bash
python -m qor.scripts.dist_compile && python -m qor.scripts.check_variant_drift
```

## CI Commands

- `python -m pytest tests/test_skill_prose_filesystem_validation.py -v` — phase-specific tests, twice for determinism.
- `python -m pytest tests/test_owasp_governance.py tests/test_skill_doctrine.py tests/test_compile.py -v` — schema/doctrine/compile guards.
- `python -m qor.scripts.badge_currency --repo-root . --ledger docs/META_LEDGER.md` — Phase 49 enforcement check.
- `python -m pytest tests/ -v` — full suite.
- `python -m qor.reliability.seal_entry_check --ledger docs/META_LEDGER.md --plan docs/plan-qor-phase50-skill-prose-filesystem-validation.md` — Phase 47 chain integrity check post-seal.
