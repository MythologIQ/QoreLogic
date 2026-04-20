# Plan: Phase 36 — plan/audit/replan loop countermeasures (SG-PlanAuditLoop-A)

**change_class**: feature
**target_version**: v0.26.0
**doc_tier**: system
**pass**: 4 (amended from Pass 3 VETO per `.agent/staging/AUDIT_REPORT.md` Entry #120)

**terms_introduced**:
- `plan-replay` (event_type) — recurring `/qor-plan` invocations within a session against a stable findings signature with no intervening `/qor-implement` / `/qor-debug`. Home: `qor/gates/schema/shadow_event.schema.json` enum + `qor/references/doctrine-governance-enforcement.md` §10.3.
- `findings signature` — normalized category-hash of audit findings read from the audit gate artifact. Home: `qor/scripts/findings_signature.py` + doctrine §10.3.
- `findings category` — closed enum of audit-finding classes. Home: `qor/gates/schema/audit.schema.json` `findings_categories.items.enum`.
- `orchestration_override` (event_type) — operator decline of a cycle-count escalation. Home: shadow_event schema enum + doctrine §10.4.
- `addressed_pending` (event field) — optional boolean, default false; invariant-coupled to `addressed == true AND addressed_reason == "remediated"`. Home: `qor/gates/schema/shadow_event.schema.json` + doctrine §10.1.

**Source**:
- `.agent/staging/AUDIT_REPORT.md` Pass 2 VETO — V6, V7 + F9, F10, F11 (Pass 1 V1-V5 + F1-F4, F6-F8 resolved at Pass 2; F5 disclosed)
- `docs/SHADOW_GENOME.md` Entry #26 (`SG-PlanAuditLoop-A`) + Entries #27, #28 (`SG-Phase36-A` pending across amendments)
- `docs/META_LEDGER.md` Entries #117-#119

## Open Questions

1. **K-threshold retune signal (F1 resolution).** Initial K=3 for `plan-replay` and cycle-count-escalation. First missed detection on a real stall with K=3 triggers an SG entry documenting the miss and a follow-up plan to reduce to K=2. No speculative retune.

2. **Canonical `findings_categories` list stability.** Eleven values in initial enum. New categories require deliberate schema amendment (no `other` escape hatch). If field work surfaces a category that clearly does not map, that is the signal to amend the enum, not to bypass it.

3. **Session-escalation-suppression scope (F3 resolution).** Suppression is per-session, cleared on session rotation. If an operator wants longer-term suppression (e.g., "known issue, do not nag for the week"), that is a separate feature — not in this phase.

## Non-goals (disclosed limitations)

- **Cross-session stall detection (F11 disclosure).** Cycle-count escalation is session-scoped by construction. A stall pattern that spans multiple operator sessions (legitimately common in long-running work) is not caught by this mechanism. The external postmortem that motivated SG-PlanAuditLoop-A plausibly involved cross-session stalls; those remain uncovered. Cross-session aggregation would require walking the ledger timeline rather than per-session gate artifacts, and is deliberately deferred to a follow-up phase. Disclosed here so the limitation is visible, not hidden.
- **Cryptographic attestation of review-pass artifacts (F5 carried forward).** Phase 1's `mark_addressed` verifies a review-pass artifact by reading its JSON fields; it does not cryptographically prove the artifact came from a genuine audit pass. An operator with filesystem write access can forge a review-pass artifact. Mitigation deferred; documented in `boundaries.limitations` of the plan gate artifact.
- **Retroactive signature-tagging of historical gate artifacts.** Pre-Phase-36 gate artifacts carry no `findings_categories` field; `findings_signature.compute` returns the `"LEGACY"` sentinel for them (V7 resolution). Historical artifacts are not rewritten.

## Phase 1 — B19 HIGH: two-stage `addressed` flip in `/qor-remediate`

### Affected Files

- `qor/gates/schema/shadow_event.schema.json` — add optional `addressed_pending: boolean` field (NOT in `required`, default `false`). Add `allOf` invariant: if `addressed == true AND addressed_reason == "remediated"`, then `addressed_pending == true`. Legacy events (with `addressed_reason == "issue_created" | "stale" | null`) are unaffected.
- `qor/scripts/remediate_mark_addressed.py` — refactor (LOC ~60 → ~100). Split into `mark_addressed_pending(ids, session_id)` and `mark_addressed(ids, session_id, review_pass_artifact_path)`.
- `qor/scripts/shadow_process.py` — `append_event` and `write_events_per_source` preserve `addressed_pending` on roundtrip. No new signature.
- `qor/skills/sdlc/qor-remediate/SKILL.md` Step 4 — rewrite to call `mark_addressed_pending`. New Step 6 "Review-pass flip" documents the final flip (invoked by `/qor-audit`, not by `/qor-remediate`).
- `qor/references/doctrine-governance-enforcement.md` §10.1 — author "Two-stage remediation flip" rule. §10.2 — "SG narrative entry closure" rule (F4 resolution): structured events use two-stage flip; narrative SG entries get a manual `## Closure` block citing the seal commit and ledger entry that shipped the countermeasure.

### Changes

Schema (append to existing `properties`, add to `allOf`):
```json
"addressed_pending": { "type": "boolean" }
```
```json
{
  "if": {
    "properties": {
      "addressed": { "const": true },
      "addressed_reason": { "const": "remediated" }
    },
    "required": ["addressed", "addressed_reason"]
  },
  "then": { "properties": { "addressed_pending": { "const": true } }, "required": ["addressed_pending"] }
}
```

`mark_addressed_pending(ids, session_id) -> (flipped, missing)`:
- Identical write-path to current `mark_addressed` except it writes `addressed_pending: true, addressed: false, addressed_reason: null, addressed_ts: null`.
- Contract: callable from `/qor-remediate` Step 4.

`mark_addressed(ids, session_id, review_pass_artifact_path) -> (flipped, missing)`:
- Reads the artifact at `review_pass_artifact_path`, parses JSON, verifies: (a) file exists, (b) `phase == "audit"`, (c) `verdict == "PASS"`, (d) the artifact references the remediate gate artifact path in its `target` field (or an explicit `reviews_remediate_gate` field — cleaner; declare the field).
- On verify: flips `addressed: true, addressed_ts: <now>, addressed_reason: "remediated"`. `addressed_pending` stays `true` (they compose).
- On verify failure: raises `ReviewAttestationError`; no mutation.
- Contract: callable from `/qor-audit` Step 4 when a subsequent audit PASSes on a remediation.

`remediate_emit_gate.emit(proposal, session_id)` — payload gains `addressed_pending_ids: [...]` alongside existing `addressed_event_ids`. Downstream review resolves which pending IDs to close.

`/qor-audit` Step 4 (modification): when verdict is PASS and the audit's subject is a `/qor-remediate` proposal (detected via presence of `.qor/gates/<sid>/remediate.json` referenced by the audit), invoke `remediate_mark_addressed.mark_addressed` with the current audit gate artifact path.

### Unit Tests (TDD — written first)

- `tests/test_remediate.py::test_mark_addressed_pending_flips_pending_only` — NEW. Flips one event; asserts `addressed_pending == True`, `addressed == False`, `addressed_ts is None`, `addressed_reason is None`.
- `tests/test_remediate.py::test_mark_addressed_requires_review_pass_artifact` — NEW. Calling without a paired artifact raises `ReviewAttestationError`; no mutation.
- `tests/test_remediate.py::test_mark_addressed_verifies_artifact_is_audit_pass` — NEW. Artifact exists but `verdict != "PASS"` → raises.
- `tests/test_remediate.py::test_mark_addressed_verifies_artifact_references_remediate_gate` — NEW. Artifact does not reference remediate gate → raises.
- `tests/test_remediate.py::test_mark_addressed_success_path_sets_addressed_ts` — NEW. Valid artifact → flip succeeds, `addressed_ts` stamped, `addressed_pending` retained.
- `tests/test_remediate.py::test_legacy_events_with_issue_created_reason_still_validate` — NEW. Events with `addressed: true, addressed_reason: "issue_created", addressed_pending: false (or missing)` pass schema validation.
- `tests/test_shadow_event_schema.py::test_schema_invariant_remediated_requires_pending` — NEW. Event with `addressed: true, addressed_reason: "remediated", addressed_pending: false` fails schema validation.
- `tests/test_shadow_event_schema.py::test_schema_invariant_issue_created_does_not_require_pending` — NEW. Event with `addressed: true, addressed_reason: "issue_created"` (no addressed_pending) passes schema.
- `tests/test_remediate.py::test_existing_18_tests_pass_unchanged` — regression assertion.

## Phase 2 — B20 MED: `plan-replay` classifier + `findings_signature`

### Affected Files

- `qor/gates/schema/audit.schema.json` — add required `findings_categories: string[]` field with closed enum (11 values, see Changes). Also add optional `reviews_remediate_gate: string` field referenced by Phase 1.
- `qor/scripts/findings_signature.py` — NEW (~40 LOC). Read audit gate artifact, extract `findings_categories`, normalize (sort lexicographic, dedupe), SHA256-hash, return 16-char prefix. LEGACY sentinel on absent field.
- `qor/scripts/stall_walk.py` — NEW (~50 LOC) (V9 resolution). Shared gate-artifact walker used by both Phase 2's classifier and Phase 3's escalator. Single source of truth for "walk session gate artifacts backward, count consecutive same-signature audit VETOs, reset on implement/debug/PASS/LEGACY, return (count, signature, first_match_ts)."
- `qor/scripts/remediate_pattern_match.py` — add `plan-replay` classifier as sixth pattern. Reads gate artifacts via `stall_walk`. Update priority table: `aged-high-severity > hallucination > regression > gate-loop > plan-replay > capability-shortfall`. Declared classifier de-dup rule (F6): gate-loop dominates plan-replay on overlapping group.
- `qor/gates/schema/shadow_event.schema.json` — add `plan-replay` to `event_type` enum.
- `qor/skills/sdlc/qor-remediate/SKILL.md` Step 2 — add `plan-replay` row with K=3 trigger; update priority ordering.
- `qor/skills/governance/qor-audit/SKILL.md` Step 4 — populate `findings_categories` from audit-pass results when emitting the gate artifact.
- `qor/references/doctrine-governance-enforcement.md` §10.3 — "Findings signature and category enum" rule.
- `tests/test_findings_signature.py` — NEW.
- `tests/test_remediate.py` — classifier tests extended.
- `tests/test_audit_gate_emits_findings_categories.py` — NEW.

### Changes

`audit.schema.json` addition — property + conditional-required (V6 resolution):
```json
"findings_categories": {
  "type": "array",
  "items": {
    "type": "string",
    "enum": [
      "razor-overage",
      "ghost-ui",
      "security-l3",
      "owasp-violation",
      "orphan-file",
      "macro-architecture",
      "dependency-unjustified",
      "schema-migration-missing",
      "specification-drift",
      "test-failure",
      "coverage-gap"
    ]
  }
}
```
```json
"allOf": [
  {
    "if": {
      "properties": { "verdict": { "const": "VETO" } },
      "required": ["verdict"]
    },
    "then": { "required": ["findings_categories"] }
  }
]
```
VETO artifacts must carry `findings_categories` (enforced by schema, not narrative). PASS artifacts may omit or pass an empty array. Any VETO emitted without the field fails validation at write time.

`findings_signature.compute(audit_gate_path: str) -> str` — V7 resolution via sentinel:
```
1. Load audit.json
2. If "findings_categories" key is ABSENT from the parsed object:
      return "LEGACY"       # reserved sentinel; 6-char literal, not a hash
3. Extract findings_categories (may be empty list if present)
4. Dedupe, sort lexicographic
5. Join with "|"
6. SHA256-hash the joined bytes
7. Return first 16 hex characters
```
Pure function; no side effects. Sentinel `"LEGACY"` is deliberately not hex-shaped so it can never collide with a real hash prefix.

F10 resolution — `/qor-audit` emission-time behavior on unmapped finding category:
Auditor raises `UnmappedCategoryError` at gate-artifact write time if any finding cannot be mapped to the 11-value enum. This makes drift impossible by deliberate friction — the auditor is forced to either amend the enum (deliberate schema evolution) or reclassify the finding. No silent-drop path; no `uncategorized` fallback. Test `test_audit_raises_on_unmapped_category`.

Classifier addition in `remediate_pattern_match.py` (V9 resolution — reads gate artifacts, not shadow events):
```
plan-replay:
  input_source: session gate artifacts at .qor/gates/<session_id>/
                (NOT shadow events — gate artifacts are the canonical
                record of phase completion)
  trigger: >= 3 consecutive audit*.json artifacts with verdict=="VETO"
           AND findings_signature stable across all 3,
           AND no intervening implement*.json / debug*.json artifact,
           within the same session directory
  severity: 3
  proposal_kind: gate
  proposal_text: "K=<N> plan/audit cycles against stable findings
                  signature <sig>. Escalate to /qor-remediate or
                  execute the standing plan directly."
  dedup_rule: if (artifact_paths of this match) overlap with any
              gate-loop match's contributing events in same run,
              drop this match (F6 — gate-loop dominates)
  implementation_note: detection shares logic with
              cycle_count_escalator.check (Phase 3). Factor common
              walk into qor/scripts/stall_walk.py; both call-sites
              consume it. The classifier produces a pattern proposal
              for remediate; the escalator produces a live escalation
              recommendation for plan/audit.
```
No new event types required. `shadow_event.schema.json` still gains `plan-replay` (classifier OUTPUT pattern name) + `orchestration_override` (override event). The `plan_complete` / `implement_complete` / `debug_complete` pseudo-events from the Pass 3 draft are removed — the presence of the corresponding gate artifact file IS the completion signal.

`/qor-audit` Step 4 (modification): after computing verdict, emit `findings_categories` populated from the audit passes that flagged findings. Mapping example:
```
Razor Pass VETO      -> "razor-overage"
Ghost UI Pass VETO   -> "ghost-ui"
Security L3 VETO     -> "security-l3"
OWASP VETO           -> "owasp-violation"
Orphan VETO          -> "orphan-file"
Macro-Arch VETO      -> "macro-architecture"
Dependency VETO      -> "dependency-unjustified"
(this plan's own V1) -> "schema-migration-missing"
(this plan's own V2/V3) -> "specification-drift"
```

### Unit Tests (TDD — written first)

- `tests/test_findings_signature.py::test_signature_is_order_independent` — NEW.
- `tests/test_findings_signature.py::test_signature_is_dedupe_stable` — NEW. `[a, b, a]` and `[a, b]` produce identical signature.
- `tests/test_findings_signature.py::test_signature_differs_on_category_change` — NEW.
- `tests/test_findings_signature.py::test_signature_empty_is_stable` — NEW. Empty categories (field PRESENT but empty list) produce a stable 16-char hash.
- `tests/test_findings_signature.py::test_signature_returns_legacy_sentinel_when_field_absent` — NEW (V7). Audit gate artifact with no `findings_categories` key → `compute` returns literal `"LEGACY"`.
- `tests/test_findings_signature.py::test_legacy_sentinel_is_not_hex_shaped` — NEW (V7). Sentinel cannot collide with a real signature prefix.
- `tests/test_findings_signature.py::test_signature_is_16_char_prefix` — NEW. Real signatures (non-sentinel) are 16 hex chars.
- `tests/test_findings_signature.py::test_signature_rejects_categories_outside_enum` — NEW. Non-enum category value raises (contract with schema).
- `tests/test_audit_gate_emits_findings_categories.py::test_audit_raises_on_unmapped_category` — NEW (F10). If `/qor-audit` encounters a finding that doesn't map to the 11-value enum, emission raises `UnmappedCategoryError`; no gate artifact written.
- `tests/test_audit_gate_emits_findings_categories.py::test_veto_audit_gate_carries_categories` — NEW. Synthetic audit → gate artifact emits `findings_categories`.
- `tests/test_audit_gate_emits_findings_categories.py::test_pass_audit_gate_may_omit_or_empty` — NEW.
- `tests/test_audit_gate_emits_findings_categories.py::test_schema_rejects_unknown_category` — NEW. Audit gate with `"findings_categories": ["fictional-category"]` fails validation.
- `tests/test_remediate.py::test_plan_replay_classifier_fires_at_k3` — NEW. Fixture: 3 audit gate artifacts in session with stable VETO signature, no intervening implement/debug artifact → classifier returns `plan-replay`.
- `tests/test_remediate.py::test_plan_replay_classifier_does_not_fire_at_k2` — NEW.
- `tests/test_remediate.py::test_plan_replay_classifier_resets_on_implement_artifact` — NEW. 2 VETOs + implement.json + 2 VETOs → no match.
- `tests/test_remediate.py::test_plan_replay_classifier_resets_on_signature_change` — NEW.
- `tests/test_remediate.py::test_plan_replay_dedup_when_gate_loop_matches_same_run` — NEW (F6).
- `tests/test_remediate.py::test_plan_replay_priority_below_gate_loop_when_both_match` — NEW.
- `tests/test_stall_walk.py::test_run_returns_three_tuple_with_timestamp` — NEW (V8). `stall_walk.run` returns `(count, signature, first_match_ts)`; timestamp is the `ts` of the oldest audit in the consecutive run.
- `tests/test_stall_walk.py::test_run_is_shared_by_escalator_and_classifier` — NEW (V9). Both call sites receive identical results for the same session fixture.
- `tests/test_stall_walk.py::test_run_resets_on_legacy_signed_artifact` — NEW (V7 integrated).
- `tests/test_stall_walk.py::test_run_empty_session_returns_zero_tuple` — NEW.

## Phase 3 — B21 MED: cycle-count escalation + event-type classifier union

### Affected Files

- `qor/scripts/cycle_count_escalator.py` — NEW (~30 LOC; thin orchestrator after stall_walk extraction).
- `qor/scripts/orchestration_override.py` — NEW (~30 LOC).
- `qor/gates/schema/shadow_event.schema.json` — add `orchestration_override` to `event_type` enum.
- `qor/scripts/remediate_pattern_match.py` — update gate-loop classifier to union event types: `>=2 events of type gate_override OR orchestration_override in same group` (V4 resolution).
- `qor/skills/sdlc/qor-plan/SKILL.md` Step 2c (new) — cycle-count check hook.
- `qor/skills/governance/qor-audit/SKILL.md` Step 0 preamble — symmetric cycle-count check.
- `qor/gates/delegation-table.md` — new rows for cycle-count escalation.
- `qor/references/doctrine-governance-enforcement.md` §10.4 "Cycle-count escalation" + §10.5 "Operator override and re-prompt suppression".
- `tests/test_cycle_count_escalator.py` — NEW. Tests the thin orchestrator; walk logic tested in `test_stall_walk.py` (Phase 2).
- `tests/test_orchestration_override.py` — NEW.
- `tests/test_skill_integrity.py` — NEW (F8 resolution: symmetric skill-integrity checks in one file).

### Changes

`cycle_count_escalator.py` — thin orchestrator over the shared `stall_walk` helper (V9 resolution integrates here):

`check(session_id: str) -> EscalationRecommendation | None` — ~20 LOC. Delegates the walk to `stall_walk`; handles suppression and builds the recommendation dataclass:
```
from qor.scripts import stall_walk
count, sig, first_match_ts = stall_walk.run(session_id)
if count < 3: return None
if _suppression_active(session_id, first_match_ts): return None
return EscalationRecommendation(
    suggested_skill="/qor-remediate",
    escalation_reason="cycle-count",
    signature=sig,
    cycle_count=count,
)
```

`_suppression_active(session_id: str, first_match_ts: str | None) -> bool` — ~10 LOC. Reads `.qor/session/<sid>/escalation_suppressed` marker; returns True iff marker exists and its timestamp is later than `first_match_ts`.

Total for `cycle_count_escalator.py`: ~30 LOC across 2 functions. Walk logic lives in `stall_walk.py` (shared with Phase 2 classifier). Pure filesystem reads; no mutation.

`stall_walk.py` contract (V8 + V9 resolution — 3-tuple return carries the timestamp the orchestrator needs):

`_list_session_artifacts(session_id: str) -> list[Path]` — ~15 LOC. Globs `.qor/gates/<sid>/{audit,plan,implement,debug}*.json`, returns chronologically sorted paths.

`_walk_backward(artifacts: list[Path]) -> tuple[int, str | None, str | None]` — ~30 LOC. Iterates in reverse; counts consecutive VETO audits with matching `findings_signature`; resets on implement/debug artifact, on signature change, on PASS audit, on LEGACY-signed artifact. Returns `(count, signature, first_match_ts)` where `first_match_ts` is the `ts` field of the OLDEST audit contributing to the current consecutive run (V8 resolution: timestamp is part of the return value, not a placeholder).

`run(session_id: str) -> tuple[int, str | None, str | None]` — ~5 LOC. Wraps `_list_session_artifacts` + `_walk_backward`; public entry point used by both `cycle_count_escalator.check` and `remediate_pattern_match`'s plan-replay classifier.

Total for `stall_walk.py`: ~50 LOC across 3 functions. Each ≤30 LOC; file under 250.

`EscalationRecommendation` is a `@dataclass(frozen=True)` with four fields (`suggested_skill`, `escalation_reason`, `signature`, `cycle_count`).

`orchestration_override.record(session_id, skill, recommended_skill, reason) -> event_id`:
```
1. Append orchestration_override shadow event (severity 2)
2. Write .qor/session/<sid>/escalation_suppressed marker with current timestamp
3. Return event id
```

Gate-loop classifier update (`remediate_pattern_match.py`):
```
# Before: gate_override events only
# After: gate_override | orchestration_override
gate_loop:
  trigger: >= 2 events where event_type in {"gate_override", "orchestration_override"} in same group
  severity: (unchanged)
  ...
```
Declared in Phase 3 because `orchestration_override` event_type is added here.

`/qor-plan` Step 2c (inserted after Step 2b grounding, before Step 3 plan write):
```python
from qor.scripts import cycle_count_escalator as cce
rec = cce.check(sid)
if rec:
    print(f"Cycle-count escalation: {rec.cycle_count} consecutive VETO on signature {rec.signature}.")
    print(f"Recommended: {rec.suggested_skill}")
    # Operator prompt: proceed with plan anyway, or escalate?
    # On decline of escalation:
    from qor.scripts import orchestration_override as oo
    oo.record(sid, "qor-plan", rec.suggested_skill, "operator elected to continue planning")
    # Proceed; next invocation will see escalation_suppressed marker and skip the check.
```

Symmetric insertion in `/qor-audit` Step 0 preamble. Audit's check fires before verdict emission, so a declined escalation still proceeds to normal audit.

`delegation-table.md` additions:
| `qor-plan` | 3rd consecutive VETO on stable findings signature | `/qor-remediate` | cycle-count escalation |
| `qor-audit` | 3rd consecutive VETO on stable findings signature | `/qor-remediate` | cycle-count escalation |
| any | operator declines cycle-count escalation | `orchestration_override.record` | logged; session-suppressed; feeds gate-loop classifier |

### Unit Tests (TDD — written first)

- `tests/test_cycle_count_escalator.py::test_two_consecutive_veto_does_not_escalate` — NEW.
- `tests/test_cycle_count_escalator.py::test_three_consecutive_veto_same_signature_escalates` — NEW.
- `tests/test_cycle_count_escalator.py::test_implement_between_resets_counter` — NEW.
- `tests/test_cycle_count_escalator.py::test_debug_between_resets_counter` — NEW.
- `tests/test_cycle_count_escalator.py::test_signature_change_resets_counter` — NEW.
- `tests/test_cycle_count_escalator.py::test_pass_between_resets_counter` — NEW.
- `tests/test_cycle_count_escalator.py::test_suppression_marker_skips_escalation` — NEW (F3).
- `tests/test_cycle_count_escalator.py::test_missing_gate_artifacts_does_not_raise` — NEW. Walking a session with gaps returns None; does not raise.
- `tests/test_cycle_count_escalator.py::test_three_legacy_signed_artifacts_do_not_escalate` — NEW (V7). Session with 3 consecutive LEGACY-signed audit artifacts → `check` returns None (false-positive blocked).
- `tests/test_cycle_count_escalator.py::test_legacy_between_real_signatures_resets_counter` — NEW (V7). Walking-backward order `[VETO-A, VETO-A, LEGACY, VETO-A, VETO-A]` → `check` returns None: LEGACY fragments the chain; neither the 2 newer nor the 2 older VETOs reach K=3.
- `tests/test_cycle_count_escalator.py::test_three_real_vetos_after_legacy_escalate` — NEW (V7). Walking-backward order `[VETO-A, VETO-A, VETO-A, LEGACY, ...]` → `check` returns escalation with `cycle_count == 3`: the three consecutive real VETOs satisfy threshold before the backward walk reaches LEGACY.
- `tests/test_orchestration_override.py::test_override_appends_severity2_event` — NEW.
- `tests/test_orchestration_override.py::test_override_writes_suppression_marker` — NEW.
- `tests/test_orchestration_override.py::test_override_feeds_gate_loop_via_union` — NEW. 2 `orchestration_override` events → gate-loop classifier fires.
- `tests/test_orchestration_override.py::test_mixed_gate_override_and_orchestration_override_count` — NEW. 1 `gate_override` + 1 `orchestration_override` → gate-loop fires.
- `tests/test_skill_integrity.py::test_qor_plan_skill_calls_cycle_count_check` — NEW. Grep-lint: `/qor-plan` SKILL.md references `cycle_count_escalator.check`.
- `tests/test_skill_integrity.py::test_qor_audit_skill_calls_cycle_count_check` — NEW. Grep-lint.
- `tests/test_skill_integrity.py::test_qor_audit_skill_calls_mark_addressed_on_pass_of_remediate` — NEW. Grep-lint.

## Phase 4 — B22 LOW: `ci_commands` schema slot in plan

### Affected Files

- `qor/gates/schema/plan.schema.json` — add `ci_commands: string[]` (required, minItems 1).
- `qor/skills/sdlc/qor-plan/SKILL.md` §Plan Structure — add `## CI Commands` section to the template.
- `qor/references/doctrine-governance-enforcement.md` §10.6 "CI command contract" — plans ship the commands that validate them locally.
- `tests/test_plan_schema.py` — schema tests for `ci_commands`; grandfathering per phase-number rule (F2).

### Changes

`plan.schema.json` addition:
```json
"ci_commands": {
  "type": "array",
  "items": { "type": "string", "minLength": 1 },
  "minItems": 1,
  "description": "Commands the operator runs to validate the plan locally before substantiate. Must match CI for deterministic parity."
}
```
`ci_commands` added to `required` for `phase == "plan"`.

Plan body template gains a section after Phases:
```markdown
## CI Commands

- `<command>` — <what it validates>
```

Grandfathering (F2 resolution): plans with filenames matching `docs/plan-qor-phase([0-9]+)-.*\.md` where the captured phase number is `< 36` are grandfathered. Phase 36 and all subsequent phases must validate against the new schema. Test enumerates via glob + regex.

### Unit Tests (TDD — written first)

- `tests/test_plan_schema.py::test_plan_schema_requires_ci_commands_for_phase_36_plus` — NEW.
- `tests/test_plan_schema.py::test_plan_schema_rejects_empty_ci_commands` — NEW.
- `tests/test_plan_schema.py::test_this_plan_passes_amended_schema` — NEW. Loads this plan file, parses, validates.
- `tests/test_plan_schema.py::test_pre_phase_36_plans_grandfathered` — NEW. Glob all `docs/plan-qor-phase[0-9]+-*.md`; phase < 36 is skipped (or flagged as grandfathered); phase >= 36 must pass.
- `tests/test_plan_schema.py::test_plan_schema_loads_successfully` — NEW. Schema file itself is valid JSON Schema.

## CI Commands

- `pytest tests/test_remediate.py tests/test_findings_signature.py tests/test_cycle_count_escalator.py tests/test_orchestration_override.py tests/test_shadow_event_schema.py tests/test_plan_schema.py tests/test_audit_gate_emits_findings_categories.py tests/test_skill_integrity.py` — targeted phase tests (fast loop during implement)
- `pytest` — full suite at seal
- `python -m qor.reliability.skill_admission qor-remediate qor-plan qor-audit` — admission on edited skills
- `python -m qor.reliability.gate_skill_matrix` — handoff integrity across skills
- `python qor/scripts/doc_integrity_strict.py` — `terms_introduced` have canonical homes

## Phase ordering rationale

Phases are ordered by blast-radius descending (HIGH → LOW) and by data-flow dependency:

- **Phase 1 must precede Phase 3**: cycle-count escalation (Phase 3) writes `orchestration_override` events; the event-state integrity fix (Phase 1) ensures those events cannot be prematurely marked addressed.
- **Phase 2 must precede Phase 3**: `findings_signature` (Phase 2) is the input to cycle-count escalation (Phase 3). Phase 2 also extends `audit.schema.json` (`findings_categories`), which Phase 3 depends on.
- **Phase 4 is independent of 1-3**: schema slot for `ci_commands`; lands anywhere but placed last because it is LOW severity.

Each phase is substantivally committable on its own; the implement step should land phases in discrete commits for reviewability.
