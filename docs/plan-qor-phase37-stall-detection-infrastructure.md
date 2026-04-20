# Plan: Phase 37 - stall-detection infrastructure (B20 + B21)

**change_class**: feature
**target_version**: v0.27.0
**doc_tier**: system
**pass**: 1

**Scope**: B20 + B20b + B21 only. Phase 36 shipped the B19 two-stage remediation flip as a narrow prerequisite. Phase 38 owns B22 (`ci_commands` schema slot). Context-discipline remains Phase 39.

**terms_introduced**:
- `audit_history` - append-only JSONL record at `.qor/gates/<session_id>/audit_history.jsonl` containing every emitted audit gate payload in session order. Home: `qor/scripts/audit_history.py` + doctrine §10.3.
- `findings_categories` - closed audit-finding category enum stored on VETO audit gate payloads and audit-history records. Home: `qor/gates/schema/audit.schema.json`.
- `findings signature` - 16-char SHA256 prefix of sorted unique `findings_categories`; `LEGACY` sentinel when categories are absent. Home: `qor/scripts/findings_signature.py`.
- `plan-replay` - remediate classifier output for repeated plan/audit cycles against a stable findings signature with no implement/debug break. Home: `qor/scripts/remediate_pattern_match.py` + `qor/gates/schema/shadow_event.schema.json`.
- `orchestration_override` - shadow event emitted when an operator declines a cycle-count escalation. Home: `qor/scripts/orchestration_override.py` + `qor/gates/schema/shadow_event.schema.json`.
- `infrastructure-mismatch` - audit finding category for plan claims that contradict current repository infrastructure. Home: `qor/gates/schema/audit.schema.json` + `/qor-audit` Infrastructure Alignment Pass.

**Source**:
- `docs/META_LEDGER.md` Entry #122 - accepted rescope: B20/B21 extracted from Phase 36 into Phase 37.
- `.agent/staging/AUDIT_REPORT.md` Phase 36 Pass 4 V10 - singleton `audit.json` overwrite made the prior stall-detection design dead code.
- `docs/BACKLOG.md` Phase 37 - B20, B20b, B21.

## Open Questions

None. V10 selected the append-only history route: write `.qor/gates/<sid>/audit_history.jsonl` alongside the existing singleton `.qor/gates/<sid>/audit.json`.

## Non-goals

- No change to the downstream singleton contract: `gate_chain.check_prior_artifact("implement")` still reads `.qor/gates/<sid>/audit.json`.
- No pass-suffixed gate artifacts (`audit.2.json`, `audit.3.json`). The audit history log is the only accumulation mechanism.
- No cross-session stall detection. Phase 37 is session-scoped; ledger-wide aggregation remains deferred.
- No `ci_commands` plan-schema slot. Phase 38 owns B22.
- No cryptographic attestation for audit-history records. Records are schema-validated append-only JSONL, not tamper-proof evidence.

## Phase 1 - B20: append-only audit history

### Affected Files

- `qor/scripts/audit_history.py` - NEW. Append/read audit history JSONL records. Public API: `append(payload, session_id)`, `read(session_id)`, `history_path(session_id)`.
- `qor/scripts/gate_chain.py` - call `audit_history.append` after successful `write_gate_artifact(phase="audit", ...)`; no behavior change for other phases.
- `qor/scripts/validate_gate_artifact.py` - no contract change; singleton write remains authoritative for chain gating.
- `qor/references/doctrine-governance-enforcement.md` - add §10.3 "Audit history" before findings-signature/cycle-count subsections.
- `tests/test_audit_history.py` - NEW.
- `tests/test_gate_chain_audit_history.py` - NEW.

### Changes

`audit_history.history_path(session_id: str) -> Path`
- Returns `workdir.gate_dir() / session_id / "audit_history.jsonl"`.

`audit_history.append(payload: dict, session_id: str) -> Path`
- Builds `record = {"phase": "audit", "session_id": session_id, **payload}`.
- Validates `record` against `audit.schema.json` via `validate_gate_artifact._validate_data("audit", record)`.
- Appends one compact JSON object plus newline to `.qor/gates/<sid>/audit_history.jsonl`.
- Creates parent directory if needed.
- Returns the history path.

`audit_history.read(session_id: str) -> list[dict]`
- Returns `[]` when the history file is absent.
- Parses JSONL in file order.
- Validates each record against `audit.schema.json`.
- Raises `ValueError` naming the line number on malformed JSON or schema failure.

`gate_chain.write_gate_artifact`
```python
path = vga.write_artifact(phase, payload, session_id=sid)
if phase == "audit":
    audit_history.append(payload, session_id=sid)
return path
```

The helper intentionally writes singleton first, then history. If singleton validation fails, no history record is appended. If history append fails after singleton write, the error is raised; the operator fixes the invalid audit emission before proceeding.

### Unit Tests

- `tests/test_audit_history.py::test_history_path_uses_gate_session_dir` - path is `.qor/gates/<sid>/audit_history.jsonl`.
- `tests/test_audit_history.py::test_append_creates_jsonl_record` - one append creates one valid JSONL line.
- `tests/test_audit_history.py::test_append_preserves_multiple_audit_passes` - three appends produce three records in order.
- `tests/test_audit_history.py::test_read_absent_history_returns_empty` - no file returns `[]`.
- `tests/test_audit_history.py::test_read_rejects_malformed_line_with_line_number` - malformed JSON raises with line number.
- `tests/test_gate_chain_audit_history.py::test_audit_write_updates_singleton_and_history` - `gate_chain.write_gate_artifact("audit", ...)` writes both `audit.json` and history.
- `tests/test_gate_chain_audit_history.py::test_non_audit_write_does_not_create_history` - plan/implement writes do not create `audit_history.jsonl`.
- `tests/test_gate_chain_audit_history.py::test_invalid_audit_payload_writes_neither_singleton_nor_history` - schema failure leaves no files.

## Phase 2 - B20b: findings categories + signature

### Affected Files

- `qor/gates/schema/audit.schema.json` - add `findings_categories` property and `allOf` rule requiring categories on VETO. (`reviews_remediate_gate` already shipped in Phase 36; no re-add.)
- `qor/scripts/findings_signature.py` - NEW. Compute stable signature from an audit record or audit-history record.
- `qor/skills/governance/qor-audit/SKILL.md` - Step 3 maps each VETO finding to a category; Step Z writes `findings_categories`.
- `qor/skills/governance/qor-audit/references/qor-audit-templates.md` - add a "Findings Categories" slot.
- `qor/references/doctrine-governance-enforcement.md` - extend §10.3 with findings-signature contract.
- `tests/test_findings_signature.py` - NEW.
- `tests/test_audit_gate_emits_findings_categories.py` - NEW structural + schema tests.

### Changes

`audit.schema.json` adds:
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
      "coverage-gap",
      "infrastructure-mismatch"
    ]
  }
}
```

Plus top-level `allOf` with `if-then` enforcing: `verdict == "VETO"` requires `findings_categories`. PASS artifacts may omit the field or pass `[]`. (`reviews_remediate_gate` stays as shipped in Phase 36: `{"type": ["string", "null"]}`.)

`findings_signature.compute_record(record: dict) -> str`
- If `findings_categories` is absent, returns literal `"LEGACY"`.
- Validates every category against the schema enum.
- Dedupe + sort categories.
- Hashes the `|`-joined string with SHA256.
- Returns the first 16 lowercase hex characters.

`findings_signature.compute_path(path: str | Path) -> str`
- Loads one JSON object and delegates to `compute_record`.

`/qor-audit` category mapping:
- Section 4 Razor -> `razor-overage`
- Ghost UI -> `ghost-ui`
- Security L3 -> `security-l3`
- OWASP -> `owasp-violation`
- Orphan -> `orphan-file`
- Macro-Level -> `macro-architecture`
- Dependency -> `dependency-unjustified`
- Schema/narrative mismatch -> `schema-migration-missing`
- Plan-internal contradiction -> `specification-drift`
- Failing or missing required tests -> `test-failure` or `coverage-gap`
- Infrastructure Alignment Pass -> `infrastructure-mismatch`

Unmapped VETO finding raises `UnmappedCategoryError` before Step Z writes the gate artifact. No `other` category exists.

### Unit Tests

- `tests/test_findings_signature.py::test_signature_is_order_independent` - category order does not affect signature.
- `tests/test_findings_signature.py::test_signature_is_dedupe_stable` - duplicate categories do not affect signature.
- `tests/test_findings_signature.py::test_signature_differs_on_category_change` - category changes alter signature.
- `tests/test_findings_signature.py::test_signature_empty_is_stable` - present empty list hashes to a stable 16-char value.
- `tests/test_findings_signature.py::test_signature_returns_legacy_sentinel_when_field_absent` - absent field returns `"LEGACY"`.
- `tests/test_findings_signature.py::test_legacy_sentinel_is_not_hex_shaped` - sentinel cannot collide with real hash output.
- `tests/test_findings_signature.py::test_signature_rejects_unknown_category` - non-enum category raises.
- `tests/test_audit_gate_emits_findings_categories.py::test_veto_audit_schema_requires_categories` - VETO without field fails schema validation.
- `tests/test_audit_gate_emits_findings_categories.py::test_pass_audit_schema_allows_missing_categories` - PASS without field validates.
- `tests/test_audit_gate_emits_findings_categories.py::test_qor_audit_skill_writes_findings_categories` - Step Z payload references `findings_categories`.
- `tests/test_audit_gate_emits_findings_categories.py::test_qor_audit_template_has_categories_slot` - template has a categories slot.
- `tests/test_audit_gate_emits_findings_categories.py::test_qor_audit_skill_names_unmapped_category_error` - skill names `UnmappedCategoryError`.

## Phase 3 - B21: stall walk + plan-replay classifier

### Affected Files

- `qor/scripts/stall_walk.py` - NEW. Read audit history + phase singleton artifacts to count same-signature VETO streaks.
- `qor/scripts/remediate_pattern_match.py` - add `plan-replay` classifier, below `gate-loop` and above `capability-shortfall aggregation`.
- `qor/gates/schema/shadow_event.schema.json` - add `plan-replay` to `event_type` enum.
- `qor/skills/sdlc/qor-remediate/SKILL.md` - Step 2 documents plan-replay classifier and priority.
- `tests/test_stall_walk.py` - NEW.
- `tests/test_remediate.py` - extend classifier tests.

### Changes

`stall_walk.run(session_id: str) -> tuple[int, str | None, str | None]`
- Reads `.qor/gates/<sid>/audit_history.jsonl` via `audit_history.read`.
- Reads optional singleton break artifacts from `.qor/gates/<sid>/implement.json` and `.qor/gates/<sid>/debug.json` when present. `debug.json` may not exist today; absence is fine.
- Sorts records by `ts`.
- Walks backward.
- Counts consecutive audit records where `verdict == "VETO"` and `findings_signature != "LEGACY"` and signature matches the current run.
- Resets on PASS, signature change, LEGACY, or any implement/debug artifact whose `ts` is newer than an older audit under consideration.
- Returns `(count, signature, first_match_ts)` where `first_match_ts` is the oldest audit timestamp in the current run.

`remediate_pattern_match.classify(groups, session_id=None)`
- Existing `groups` behavior remains for shadow-event classifiers.
- When `session_id` is provided, calls `stall_walk.run(session_id)`.
- If count >= 3, appends one `plan-replay` classification with `event_ids=[]`, `skill="qor-plan"`, `session_id=session_id`, and details containing `signature`, `cycle_count`, `first_match_ts`.
- If a `gate-loop` classification exists for the same session, drops `plan-replay` for that run.

Priority order becomes:
`aged-high-severity > hallucination > regression > gate-loop > plan-replay > capability-shortfall aggregation`.

### Unit Tests

- `tests/test_stall_walk.py::test_run_empty_session_returns_zero_tuple` - no history returns `(0, None, None)`.
- `tests/test_stall_walk.py::test_run_counts_three_vetos_same_signature` - three VETOs with same categories returns count 3.
- `tests/test_stall_walk.py::test_run_resets_on_signature_change` - changed categories reset the run.
- `tests/test_stall_walk.py::test_run_resets_on_pass` - PASS breaks the run.
- `tests/test_stall_walk.py::test_run_resets_on_legacy_record` - absent categories return LEGACY and break the run.
- `tests/test_stall_walk.py::test_run_resets_on_implement_artifact_newer_than_prior_veto` - implement artifact splits the audit run.
- `tests/test_stall_walk.py::test_run_returns_oldest_matching_timestamp` - first-match timestamp is the oldest audit in the current run.
- `tests/test_remediate.py::test_plan_replay_classifier_fires_at_k3` - `classify(groups, session_id=sid)` emits plan-replay at count 3.
- `tests/test_remediate.py::test_plan_replay_classifier_does_not_fire_at_k2` - count 2 does not classify.
- `tests/test_remediate.py::test_plan_replay_dedup_when_gate_loop_matches_same_session` - gate-loop dominates plan-replay.
- `tests/test_remediate.py::test_plan_replay_priority_above_capability_shortfall` - plan-replay is evaluated before capability shortfall for session-level output.

## Phase 4 - B21: cycle-count escalation + infrastructure alignment pass

### Affected Files

- `qor/scripts/cycle_count_escalator.py` - NEW. Thin orchestrator over `stall_walk.run`.
- `qor/scripts/orchestration_override.py` - NEW. Emit override event and session suppression marker.
- `qor/gates/schema/shadow_event.schema.json` - add `orchestration_override` to `event_type` enum.
- `qor/scripts/remediate_pattern_match.py` - gate-loop counts `gate_override` OR `orchestration_override`.
- `qor/skills/sdlc/qor-plan/SKILL.md` - Step 2c cycle-count check before writing a new plan.
- `qor/skills/governance/qor-audit/SKILL.md` - Step 0 cycle-count check; Step 3 adds Infrastructure Alignment Pass.
- `qor/gates/delegation-table.md` - add cycle-count escalation rows.
- `qor/references/doctrine-shadow-genome-countermeasures.md` - add SG-InfrastructureMismatch countermeasure.
- `qor/references/doctrine-governance-enforcement.md` - add §10.4 cycle-count escalation and §10.5 override suppression.
- `tests/test_cycle_count_escalator.py` - NEW.
- `tests/test_orchestration_override.py` - NEW.
- `tests/test_skill_integrity.py` - extend.

### Changes

`cycle_count_escalator.check(session_id: str) -> EscalationRecommendation | None`
- Delegates to `stall_walk.run(session_id)`.
- Returns `None` when count < 3.
- Returns `None` when suppression marker `.qor/session/<sid>/escalation_suppressed` exists and is newer than `first_match_ts`.
- Otherwise returns frozen dataclass:
```python
EscalationRecommendation(
    suggested_skill="/qor-remediate",
    escalation_reason="cycle-count",
    signature=sig,
    cycle_count=count,
)
```

`orchestration_override.record(session_id, skill, recommended_skill, reason) -> str`
- Appends a severity-2 `orchestration_override` event.
- Writes `.qor/session/<sid>/escalation_suppressed` with current timestamp.
- Returns the event id.

`/qor-plan` Step 2c:
- Calls `cycle_count_escalator.check(sid)`.
- If recommendation exists, surfaces `/qor-remediate`.
- If operator declines, calls `orchestration_override.record(...)` and proceeds.

`/qor-audit` Step 0:
- Same check as `/qor-plan`, before issuing the current verdict.

`/qor-audit` Infrastructure Alignment Pass:
- New mandatory pass after Macro-Level Architecture.
- Grep-verifies plan claims about filesystem paths, gate artifact globbing, event types, and cross-module interfaces against current repository code.
- Any contradiction maps to findings category `infrastructure-mismatch`.
- This pass exists to catch the V10 class before implementation.

### Unit Tests

- `tests/test_cycle_count_escalator.py::test_two_consecutive_veto_does_not_escalate` - no recommendation at K=2.
- `tests/test_cycle_count_escalator.py::test_three_consecutive_veto_same_signature_escalates` - recommendation at K=3.
- `tests/test_cycle_count_escalator.py::test_signature_change_resets_counter` - no recommendation across changed signature.
- `tests/test_cycle_count_escalator.py::test_pass_between_resets_counter` - PASS breaks streak.
- `tests/test_cycle_count_escalator.py::test_implement_between_resets_counter` - implementation breaks streak.
- `tests/test_cycle_count_escalator.py::test_legacy_records_do_not_escalate` - LEGACY records are excluded.
- `tests/test_cycle_count_escalator.py::test_suppression_marker_skips_escalation` - marker newer than first-match timestamp suppresses.
- `tests/test_orchestration_override.py::test_override_appends_severity2_event` - event shape validates.
- `tests/test_orchestration_override.py::test_override_writes_suppression_marker` - marker file is written.
- `tests/test_orchestration_override.py::test_gate_loop_counts_orchestration_override` - two orchestration overrides classify as gate-loop.
- `tests/test_orchestration_override.py::test_mixed_gate_and_orchestration_override_count` - one of each classifies as gate-loop.
- `tests/test_skill_integrity.py::test_qor_plan_skill_calls_cycle_count_check` - plan skill references `cycle_count_escalator.check`.
- `tests/test_skill_integrity.py::test_qor_audit_skill_calls_cycle_count_check` - audit skill references `cycle_count_escalator.check`.
- `tests/test_skill_integrity.py::test_qor_audit_has_infrastructure_alignment_pass` - audit skill contains "Infrastructure Alignment Pass" and `infrastructure-mismatch`.
- `tests/test_skill_integrity.py::test_delegation_table_lists_cycle_count_escalation` - delegation table includes plan/audit rows.

## CI Commands

- `pytest tests/test_audit_history.py tests/test_gate_chain_audit_history.py` - Phase 1 targeted tests.
- `pytest tests/test_findings_signature.py tests/test_audit_gate_emits_findings_categories.py` - Phase 2 targeted tests.
- `pytest tests/test_stall_walk.py tests/test_remediate.py` - Phase 3 targeted tests.
- `pytest tests/test_cycle_count_escalator.py tests/test_orchestration_override.py tests/test_skill_integrity.py` - Phase 4 targeted tests.
- `pytest` - full suite at seal.
- `python -m qor.reliability.skill_admission qor-plan qor-audit qor-remediate` - admission on edited skills.
- `python -m qor.reliability.gate_skill_matrix` - handoff integrity.
- `python qor/scripts/doc_integrity_strict.py` - term homes and doctrine references.
