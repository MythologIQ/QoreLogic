# Plan: Phase 36 — two-stage addressed flip in /qor-remediate (B19 only)

**change_class**: feature
**target_version**: v0.26.0
**doc_tier**: system
**pass**: 2 (amended from Pass 1 VETO per `.agent/staging/AUDIT_REPORT.md` Entry #123 — V1 review-pass detection disambiguation)

**Scope**: B19 only. B20 (plan-replay classifier), B21 (cycle-count escalation), B22 (ci_commands schema slot) moved to Phase 37, Phase 37, Phase 38 respectively — see `docs/BACKLOG.md`. Context-discipline moves to Phase 39.

**Rationale for rescope**: 4 audit passes on the prior Phase 36 plan surfaced 10 findings (V1-V10) across 4 defect classes, each pass revealing deeper infrastructure-alignment mismatches. V10 (Pass 4) exposed the root cause: the stall-detection mechanism depends on multi-pass gate-artifact accumulation, but `gate_chain.write_gate_artifact` is singleton-overwrite. The prior plan's B20/B21 cannot land cleanly until gate artifact accumulation is designed as explicit infrastructure. B19 has zero infrastructure dependency — schema field + refactor + doctrine — and ships now. Prior Phase 36 commits preserved as investigation record on this branch.

**terms_introduced**:
- `addressed_pending` (event field) — optional boolean, default `false`; schema invariant: `addressed == true AND addressed_reason == "remediated"` implies `addressed_pending == true`. Home: `qor/gates/schema/shadow_event.schema.json` + doctrine §10.1.
- `review-pass artifact` — audit gate artifact with `verdict == "PASS"` whose `target` (or `reviews_remediate_gate` field) references the remediate gate being closed. Home: `qor/scripts/remediate_mark_addressed.py` docstring + doctrine §10.1.
- Two-stage remediation flip — `mark_addressed_pending` → `mark_addressed`, where the second stage requires a review-pass artifact. Home: doctrine §10.1.

**Source**:
- `docs/SHADOW_GENOME.md` Entry #26 (`SG-PlanAuditLoop-A` — addressed:false; B19 is partial countermeasure)
- `docs/META_LEDGER.md` Entry #117 (original failure documentation) + Entry #122 (rescope remediation proposal, accepted by operator)
- `docs/BACKLOG.md` B19

## Open Questions

None. Scope is minimal and all prior dialogue resolutions carry forward.

## Non-goals

- No plan-replay classifier (deferred to Phase 37)
- No cycle-count escalation (deferred to Phase 37)
- No `ci_commands` schema slot (deferred to Phase 38)
- No infrastructure work for multi-pass gate artifact accumulation (deferred to Phase 37 as explicit infrastructure design)

## Phase 1 — B19: two-stage `addressed` flip in `/qor-remediate`

### Affected Files

- `qor/gates/schema/shadow_event.schema.json` — add optional `addressed_pending: boolean` property; add `allOf` invariant at top level.
- `qor/gates/schema/audit.schema.json` — add optional `reviews_remediate_gate: string | null` property (V1 resolution — explicit disambiguation signal for review-pass flip).
- `qor/scripts/remediate_mark_addressed.py` — refactor (LOC ~60 → ~90). Split into `mark_addressed_pending(ids, session_id)` and `mark_addressed(ids, session_id, review_pass_artifact_path)`. Each function ≤40 LOC; shared helper `_flip_event_fields` factors the common write path.
- `qor/scripts/shadow_process.py` — `append_event` and `write_events_per_source` preserve `addressed_pending` on roundtrip. No new signature.
- `qor/skills/sdlc/qor-remediate/SKILL.md` Step 4 — rewrite to call `mark_addressed_pending`. New Step 6 "Review-pass flip" documents the final flip (invoked by `/qor-audit`, not by `/qor-remediate`).
- `qor/skills/governance/qor-audit/SKILL.md` Step 4 — when verdict is PASS and the audit's subject is a remediate proposal (detected via presence of `.qor/gates/<sid>/remediate.json` referenced by the audit's target), invoke `remediate_mark_addressed.mark_addressed` with the current audit gate artifact path.
- `qor/references/doctrine-governance-enforcement.md` §10.1 "Two-stage remediation flip" — codify. §10.2 "SG narrative entry closure" — narrative SG entries in `SHADOW_GENOME.md` get a manual `## Closure` block citing seal commit + ledger entry (distinct from structured-event two-stage flip).
- `tests/test_remediate.py` — new + refactored tests.
- `tests/test_shadow_event_schema.py` — schema roundtrip + invariant tests.

### Changes

Schema — append to existing `properties`:
```json
"addressed_pending": { "type": "boolean" }
```

Add top-level `allOf` to schema:
```json
"allOf": [
  {
    "if": {
      "properties": {
        "addressed": { "const": true },
        "addressed_reason": { "const": "remediated" }
      },
      "required": ["addressed", "addressed_reason"]
    },
    "then": {
      "properties": { "addressed_pending": { "const": true } },
      "required": ["addressed_pending"]
    }
  }
]
```

Legacy events with `addressed: true, addressed_reason: "issue_created" | "stale"` are unaffected — the conditional only fires on `addressed_reason == "remediated"`.

`mark_addressed_pending(ids: list[str], session_id: str) -> tuple[int, list[str]]` — ~30 LOC.
- Delegates field-write to `_flip_event_fields(ids, session_id, fields={"addressed_pending": True})`.
- Returns `(flipped_count, missing_ids)`.

`mark_addressed(ids: list[str], session_id: str, review_pass_artifact_path: str) -> tuple[int, list[str]]` — ~35 LOC.
- Reads the artifact at `review_pass_artifact_path`, parses JSON.
- Verifies: (1) file exists, (2) `phase == "audit"`, (3) `verdict == "PASS"`, (4) `target` references the remediate gate artifact path (startswith or equals `.qor/gates/<sid>/remediate.json`) OR `reviews_remediate_gate` field is set to that path.
- On verify: delegates field-write to `_flip_event_fields(ids, session_id, fields={"addressed": True, "addressed_ts": now_iso(), "addressed_reason": "remediated"})`. `addressed_pending` is assumed true per schema invariant (test verifies).
- On verify failure: raises `ReviewAttestationError`; no mutation.

`_flip_event_fields(ids: list[str], session_id: str, fields: dict) -> tuple[int, list[str]]` — ~25 LOC. Internal helper. Routes write-back to each event's origin file via `shadow_process.id_source_map()` + `write_events_per_source`. Returns `(flipped, missing)`.

File total: ~90 LOC across 3 functions (2 public + 1 private). Each ≤40; file <250.

`/qor-audit` Step 4 integration — skill prose addition (V1 resolution: explicit operator signal):

When operator intends to review a remediation, they invoke `/qor-audit` with the skill arg `reviews-remediate:<path>` (e.g., `/qor-audit reviews-remediate:.qor/gates/<sid>/remediate.json`). The skill captures this and writes `reviews_remediate_gate: "<path>"` into the audit gate artifact. Absence of the arg → field is null → no flip. This is the ONLY path that triggers the review-pass flip.

```
# /qor-audit Step 4 flip block (executes after verdict emission, before ledger update)
reviews_gate = audit_gate_payload.get("reviews_remediate_gate")
if verdict == "PASS" and reviews_gate:
    import json
    with open(reviews_gate) as f:
        remediate_proposal = json.load(f)
    from qor.scripts import remediate_mark_addressed as rma
    rma.mark_addressed(
        remediate_proposal["addressed_event_ids"],
        session_id=sid,
        review_pass_artifact_path=f".qor/gates/{sid}/audit.json",
    )
```

`mark_addressed`'s verification (in `remediate_mark_addressed.py`) confirms the audit artifact's `reviews_remediate_gate` field equals the remediate gate path being closed. Double-binding: operator signal sets the field at audit-write time; `mark_addressed` re-verifies at flip time. Both must agree; either mismatch raises `ReviewAttestationError`.

PASS audits without the `reviews-remediate` arg never touch event state. Unrelated audits in the same session remain inert.

`/qor-remediate` Step 4 (modification): call `mark_addressed_pending` instead of `mark_addressed`. Skill prose updates inline. New Step 6 "Review-pass flip" references the `/qor-audit` integration above.

Doctrine §10.1 authors ~400 words codifying the two-stage flip rule: pending = "proposal filed, awaiting review," addressed = "review passed and closure certified." Explicitly names the review-pass artifact verification contract (fields + error class). §10.2 authors ~200 words on narrative SG closure via `## Closure` block with seal commit + ledger entry citation (not applicable to this plan's scope except as a doctrine addition — no narrative SG entry is being closed here).

### Unit Tests (TDD — written first)

- `tests/test_shadow_event_schema.py::test_schema_allows_addressed_pending_optional` — NEW. Event without `addressed_pending` field passes validation.
- `tests/test_shadow_event_schema.py::test_schema_invariant_remediated_requires_pending` — NEW. Event with `addressed: true, addressed_reason: "remediated", addressed_pending: false` fails validation.
- `tests/test_shadow_event_schema.py::test_schema_invariant_issue_created_does_not_require_pending` — NEW. Event with `addressed: true, addressed_reason: "issue_created"` (no `addressed_pending`) passes.
- `tests/test_shadow_event_schema.py::test_schema_invariant_stale_does_not_require_pending` — NEW.
- `tests/test_remediate.py::test_mark_addressed_pending_flips_pending_only` — NEW. Flips one event; asserts `addressed_pending == True`, `addressed == False`, `addressed_ts is None`, `addressed_reason is None`.
- `tests/test_remediate.py::test_mark_addressed_requires_review_pass_artifact` — NEW. Calling without a paired artifact raises `ReviewAttestationError`; no mutation.
- `tests/test_remediate.py::test_mark_addressed_verifies_artifact_is_audit_pass` — NEW. Artifact exists but `verdict != "PASS"` → raises.
- `tests/test_remediate.py::test_mark_addressed_verifies_artifact_references_remediate_gate` — NEW. Artifact does not reference remediate gate → raises.
- `tests/test_remediate.py::test_mark_addressed_success_path_sets_addressed_ts` — NEW. Valid artifact → flip succeeds, `addressed_ts` stamped.
- `tests/test_remediate.py::test_mark_addressed_preserves_addressed_pending_true` — NEW. After flip, `addressed_pending` retains `true` value.
- `tests/test_remediate.py::test_mark_addressed_rejects_audit_without_reviews_remediate_gate_field` — NEW (V1). Audit artifact with `verdict: "PASS"` but no `reviews_remediate_gate` field → `ReviewAttestationError`; events not flipped.
- `tests/test_remediate.py::test_mark_addressed_rejects_reviews_remediate_gate_mismatch` — NEW (V1). Audit artifact's `reviews_remediate_gate` field value does not match the remediate gate path argument → raises; events not flipped.
- `tests/test_remediate.py::test_pass_audit_without_arg_does_not_flip_events` — NEW (V1). Integration scenario: session has remediate.json from prior invocation; later PASS audit without `reviews-remediate` arg → `reviews_remediate_gate` field is null → flip logic short-circuits; events remain `addressed: false`.
- `tests/test_remediate.py::test_legacy_events_with_issue_created_reason_still_read` — NEW. `remediate_read_context.load_unaddressed_groups` correctly reads events missing `addressed_pending` field.
- `tests/test_remediate.py::test_existing_18_tests_pass_unchanged` — regression assertion.

## CI Commands

- `pytest tests/test_remediate.py tests/test_shadow_event_schema.py` — targeted phase tests (fast loop during implement)
- `pytest` — full suite at seal
- `python -m qor.reliability.skill_admission qor-remediate qor-audit` — admission on edited skills
- `python -m qor.reliability.gate_skill_matrix` — handoff integrity
- `python qor/scripts/doc_integrity_strict.py` — terms_introduced have canonical homes
