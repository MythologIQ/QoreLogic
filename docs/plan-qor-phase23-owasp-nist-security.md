# Phase 23: OWASP Governance Integration + Security Remediation + NIST Evidence Framework

**change_class**: feature
**version_bump**: 0.13.0 -> 0.14.0
**branch**: phase/23-owasp-nist-security
**author**: Governor

## Summary

Three tracks closing all 9 security findings from docs/security-audit-2026-04-16.md, wiring OWASP Top 10 checks into governance lifecycle, and upgrading NIST SSDF from mapping to automated evidence generation.

## Track A: Security Remediation (9 findings, 0 tolerance)

### Files modified: 7

1. `qor/scripts/collect_shadow_genomes.py` -- MEDIUM-1: repo path validation
2. `qor/scripts/shadow_process.py` -- MEDIUM-2: warn on malformed JSONL; MEDIUM-3: file locking
3. `qor/scripts/ledger_hash.py` -- LOW-1: chain_hash separator; LOW-6: skip count reporting; LOW-9: SSDF practice tags
4. `qor/scripts/remediate_emit_gate.py` -- LOW-2: session_id validation
5. `qor/scripts/check_shadow_threshold.py` -- LOW-2: session_id validation
6. `qor/scripts/create_shadow_issue.py` -- LOW-3: event ID validation
7. `qor/reliability/intent-lock.py` -- LOW-4: PASS verdict regex; LOW-5: utcnow deprecation

### Tests: 15 in `tests/test_security_fixes.py`

1. MEDIUM-1: valid repo path accepted
2. MEDIUM-1: invalid repo path rejected
3. MEDIUM-2: malformed JSONL emits warning to stderr
4. MEDIUM-2: valid JSONL parses without warning
5. MEDIUM-3: atomic_append uses file locking
6. LOW-1: chain_hash uses separator
7. LOW-1: legacy_chain_hash without separator
8. LOW-1: verify handles both old and new format
9. LOW-2: valid session_id accepted
10. LOW-2: invalid session_id raises ValueError
11. LOW-3: valid event ID accepted
12. LOW-3: invalid event ID raises ValueError
13. LOW-4: verdict regex matches VERDICT...PASS
14. LOW-5: uses timezone-aware datetime
15. LOW-6: verify reports skipped entry count

## Track B: OWASP Governance Integration

### Files created: 3

1. `qor/policies/owasp_enforcement.cedar` -- Cedar forbid rules for shell=True, unsafe deserialization
2. `qor/references/doctrine-owasp-governance.md` -- OWASP mapping doctrine (~60 lines)

### Files modified: 1

3. `qor/skills/governance/qor-audit/SKILL.md` -- OWASP Top 10 Pass section

### Tests: 8 in `tests/test_owasp_governance.py`

1. doctrine exists
2. doctrine has OWASP categories
3. SKILL.md has OWASP pass
4. Cedar policies file exists
5. Cedar forbid shell_true
6. Cedar forbid unsafe_deserialization
7. No shell=True in production code (static grep)
8. No unsafe deserialization in production code (static grep)

## Track C: NIST SSDF Evidence Framework

### Files modified: 3

1. `qor/scripts/ledger_hash.py` -- ssdf_practices parameter in entry writer
2. `qor/cli.py` -- compliance report subcommand
3. `qor/references/doctrine-nist-ssdf-alignment.md` -- Evidence Collection section

### Tests: 6 in `tests/test_nist_compliance.py`

1. compliance CLI imports
2. compliance report format
3. practice tag parsing from ledger
4. coverage calculation
5. empty ledger handling
6. NIST doctrine evidence section exists

## Totals

- Files modified: 10
- Files created: 4
- Tests added: 29 (15 + 8 + 6)
- Security findings closed: 9/9
