# API Contract Verification: Q-DNA MCP Tools

**Auditor:** ChatGPT  
**Date:** December 18, 2025  
**Scope:** `server.py` MCP tools vs Q-DNA Specification

---

## Executive Summary

| Finding             | Result                                 |
| ------------------- | -------------------------------------- |
| Tools Implemented   | **46** @mcp.tool() + 2 @mcp.resource() |
| Claimed in Dev Plan | 36                                     |
| Spec Compliance     | **PARTIAL** — 2 critical failures      |

---

## Critical Compliance Failures

| Requirement                      | Evidence                                                              | Status     | Confidence |
| -------------------------------- | --------------------------------------------------------------------- | ---------- | ---------- |
| **Ed25519 signing**              | `log_event()` uses `f"sig_{sha256(...)[:16]}"`                        | 🔴 FAIL    | 97%        |
| **PII redaction before logging** | No redaction layer before `log_event(payload=...)`                    | 🔴 FAIL    | 90%        |
| **Data minimization**            | `log_event()` stores full payload; `archive_failure()` stores vectors | 🟡 PARTIAL | 85%        |

---

## Compliance Matrix

| Spec Requirement             | Implementation                                 | Status     |
| ---------------------------- | ---------------------------------------------- | ---------- |
| Ed25519 ledger signing       | Mock signature only                            | 🔴 FAIL    |
| PII redaction mandatory      | Not enforced                                   | 🔴 FAIL    |
| Data minimization            | Full payloads stored                           | 🟡 PARTIAL |
| Semantic drift < 0.85        | `check_semantic_drift()` ✓                     | ✅ PASS    |
| Deferral windows             | `request_deferral()` exists                    | 🟡 PARTIAL |
| Diversity quorum ≥2 families | `check_diversity_quorum()` ✓                   | 🟡 PARTIAL |
| Backpressure/reject          | `get_traffic_monitor().request_access()` + 503 | ✅ PASS    |
| Volatility TTL               | `register_claim_with_ttl()` etc.               | ✅ PASS    |

---

## Error Handling Issues

### 1. Non-JSON Error Returns

Tools return raw strings like `"Error: ..."` instead of JSON:

- `log_event()` → `"Error: Ledger not initialized..."`
- `archive_failure()`, `request_l3_approval()` → `"Error: {e}"`

**Fix:** Standardize on `{"status": "ERROR", "error_code": "...", "message": "..."}`

### 2. Missing DB Error Handling

- `get_system_status()` assumes `fetchone()` returns data
- No `sqlite3.Error` catches

### 3. Duplicate Variable Assignment

`_quarantine_manager` assigned twice at top of file.

### 4. Signing Mismatch

- `verify_signature()` validates Ed25519
- `log_event()` generates mock signatures
- **"Cryptography theater"** — verification exists but signing doesn't

---

## Implemented Tools (46)

| #   | Tool                          | Signature                                                                         |
| --- | ----------------------------- | --------------------------------------------------------------------------------- |
| 1   | `audit_code`                  | `(file_path, content) -> str`                                                     |
| 2   | `audit_claim`                 | `(text) -> str`                                                                   |
| 3   | `log_event`                   | `(agent_role, event_type, risk_grade, payload) -> str`                            |
| 4   | `archive_failure`             | `(input_vector, failure_mode, context, causal_vector, decision_rationale) -> str` |
| 5   | `request_l3_approval`         | `(artifact_hash, reason) -> str`                                                  |
| 6   | `approve_l3`                  | `(queue_id, approved, overseer_notes) -> str`                                     |
| 7   | `get_pending_approvals`       | `() -> str`                                                                       |
| 8   | `apply_penalty`               | `(agent_did, amount, reason) -> str`                                              |
| 9   | `set_operational_mode`        | `(mode, reason) -> str`                                                           |
| 10  | `get_system_status`           | `() -> str`                                                                       |
| 11  | `register_claim_with_ttl`     | `(content, volatility_class, source_url) -> str`                                  |
| 12  | `check_claim_validity`        | `(claim_id) -> str`                                                               |
| 13  | `get_expired_claims`          | `() -> str`                                                                       |
| 14  | `get_sla_status`              | `() -> str`                                                                       |
| 15  | `verify_signature`            | `(did, data, signature_hex) -> str`                                               |
| 16  | `system_health_check`         | `() -> str`                                                                       |
| 17  | `register_source`             | `(url, tier_override) -> str`                                                     |
| 18  | `check_source_credibility`    | `(url, current_grade) -> str`                                                     |
| 19  | `update_source_verification`  | `(url, success) -> str`                                                           |
| 20  | `get_agent_trust`             | `(agent_did) -> str`                                                              |
| 21  | `update_agent_trust`          | `(agent_did, outcome_score, context, ledger_ref_id) -> str`                       |
| 22  | `apply_trust_penalty`         | `(agent_did, penalty_type, reason) -> str`                                        |
| 23  | `apply_trust_decay`           | `(agent_did) -> str`                                                              |
| 24  | `check_semantic_drift`        | `(agent_did, content) -> str`                                                     |
| 25  | `request_diversity_vote`      | `(artifact_hash, content, family, verdict, reason, confidence) -> str`            |
| 26  | `check_diversity_quorum`      | `(artifact_hash) -> str`                                                          |
| 27  | `get_adversarial_prompt`      | `(content, perspective) -> str`                                                   |
| 28  | `submit_adversarial_critique` | `(agent_did, critique_json) -> str`                                               |
| 29  | `get_low_credibility_sources` | `(threshold) -> str`                                                              |
| 30  | `quarantine_agent`            | `(agent_did, reason, track) -> str`                                               |
| 31  | `check_agent_quarantine`      | `(agent_did) -> str`                                                              |
| 32  | `get_active_quarantines`      | `() -> str`                                                                       |
| 33  | `release_expired_quarantines` | `() -> str`                                                                       |
| 34  | `check_sentinel_fallback`     | `(current_grade) -> str`                                                          |
| 35  | `request_deferral`            | `(artifact_hash, category, reason) -> str`                                        |
| 36  | `complete_deferral`           | `(deferral_id) -> str`                                                            |
| 37  | `get_active_deferrals`        | `() -> str`                                                                       |
| 38  | `check_expired_deferrals`     | `() -> str`                                                                       |
| 39  | `check_verification_mode`     | `(risk_grade) -> str`                                                             |
| 40  | `get_mode_behavior`           | `() -> str`                                                                       |
| 41  | `record_prediction`           | `(agent_did, confidence, correct) -> str`                                         |
| 42  | `get_calibration_report`      | `(agent_did) -> str`                                                              |
| 43  | `check_honest_error`          | `(agent_did) -> str`                                                              |
| 44  | `record_clean_audit`          | `(agent_did) -> str`                                                              |
| 45  | `get_all_agent_weights`       | `() -> str`                                                                       |
| 46  | `get_monitor_status`          | `() -> str`                                                                       |

**Resources:** `ledger://recent`, `genome://unresolved`

---

## Priority Fixes

1. **Make `log_event()` use real Ed25519 via `IdentityManager.sign()`**
2. **Add PII redaction gate before any DB write**
3. **Standardize all error returns to JSON**
4. **Harden DB reads with `fetchone() is None` checks**
5. **Update DEVELOPMENT_PLAN.md: 46 tools, not 36**
