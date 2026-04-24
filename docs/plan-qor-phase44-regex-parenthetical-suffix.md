# Plan: Phase 44 — accept parenthetical suffix on hash field labels

**change_class**: hotfix
**target_version**: v0.31.1
**doc_tier**: minimal
**pass**: 1

**Scope**: Single-line refinement to the three hash-field regex constants in `qor/scripts/ledger_hash.py` to optionally accept a parenthetical suffix inside the bold field-label markers (e.g., `**Chain Hash (Merkle seal)**:`, `**Content Hash (session seal)**:`). Restores chain-verification coverage for SESSION SEAL entries.

**Rationale**: Phase 41's regex tightening (anchor on `\*\*Field\*\*` exact label) introduced a regression: the pre-Phase-41 regex matched seal-entry markup via no-anchor sweep; the new strict regex does not. The standard SESSION SEAL convention writes `**Chain Hash (Merkle seal)**: \`hex\`` — the parenthetical "(Merkle seal)" sits inside the bold markers, so `\*\*Chain Hash\*\*` does not match. Same pattern for `**Content Hash (session seal)**:`.

**Affected entries** in current `docs/META_LEDGER.md`: #122, #126, #129, #132, #133, #137, #140, #143 — eight entries (mostly SESSION SEAL plus one REMEDIATE PROPOSAL with the same field-label convention). All silently skipped by the Phase 41 verifier rather than verified. The chain math is correct; only the parser's field-name match fails.

**Why the regression went undetected**: Phase 41's `test_verify_real_ledger_still_passes` asserted only `rc == 0`. With these entries silently skipped (no FAIL produced), `rc == 0` is satisfied vacuously — the very pattern Phase 42's capsys-style verification was designed to prevent, but the protection was applied only to synthetic-ledger tests. The real-ledger probe never counted verified vs skipped entries.

This is a one-instance recurrence of SG-AdjacentState-A: the Phase 41 plan focused on the defects in issue #13's reported markup forms (inline-backtick, fenced) and did not examine all field-label conventions present in the real ledger before tightening the anchor.

## Open Questions

None.

## Phase 1 — accept parenthetical suffix in hash field labels

### Affected Files

- `tests/test_ledger_hash.py` — new TDD tests added first; verified RED before patching.
- `qor/scripts/ledger_hash.py` — relax the three regexes to accept an optional parenthetical suffix inside the bold markers.

### Unit Tests

TDD order — new tests added and confirmed RED against the current Phase 41 regex, then GREEN after the patch.

- `test_verify_accepts_chain_hash_with_merkle_seal_suffix` — synthetic ledger with `**Chain Hash (Merkle seal)**: \`{hash}\`` form. Pre-fix: regex misses; entry skipped; `assert "OK   Entry #1:" in capsys.readouterr().out` fails. Post-fix: passes.
- `test_verify_accepts_content_hash_with_session_seal_suffix` — same pattern for `**Content Hash (session seal)**:`.
- `test_verify_accepts_previous_hash_with_arbitrary_suffix` — defensively cover `**Previous Hash (anything)**:` — even though the real ledger doesn't use this convention for Previous Hash, the regex change applies symmetrically and this guards against future drift.
- `test_verify_real_ledger_seal_entries_verify_clean` — anti-vacuous-green guard: parse `docs/META_LEDGER.md`, run `verify`, capture stdout, and assert that **every** SESSION SEAL entry numbered ≥ 116 (i.e. post-Phase-23 modern format) appears in the `OK` output. Replaces the rc-only check with a count-based assertion that would have caught the original Phase 41 regression. Reads ledger entry numbers from `ENTRY_RE.split` and filters by `SESSION SEAL` substring in the entry body.
- `test_verify_real_ledger_remediate_proposal_entries_verify_clean` — companion test for REMEDIATE PROPOSAL entries (same field-label convention). Asserts each such entry numbered ≥ 116 appears in `OK` output.
- `test_verify_real_ledger_no_silent_skips_for_modern_entries` — generalization: any entry numbered ≥ 116 (post-Phase-23 boundary) must verify. Skipping any such entry now FAILs the test rather than silently coexisting with a `rc == 0` from elsewhere. Whitelist documented for any expected exceptions (genesis-style or narrative entries that legitimately lack the three hash fields).

### Changes

In `qor/scripts/ledger_hash.py`, replace the three regex constants. The bold-anchor field-name segment changes from `\*\*<Name>\*\*` to `\*\*<Name>(?:\s*\([^)]+\))?\*\*` — the optional non-greedy parenthetical suffix sits inside the bold markers, before the closing `\*\*`:

```python
# Phase 44: hash field labels MAY carry a parenthetical suffix inside the bold
# markers (e.g., `**Chain Hash (Merkle seal)**:`, `**Content Hash (session seal)**:`).
# This is the standard SESSION SEAL convention since Phase 23. The Phase 41 strict
# anchor `\*\*Field\*\*` did not match these and silently skipped seal entries; the
# optional `(?:\s*\([^)]+\))?` segment restores coverage without weakening the
# bold-anchor protection against prose mentions.
_HASH_SPAN = r"(?:(?!\n\s*\*\*[A-Z])[\s\S])*?"
_HASH_VALUE = r"(?:`([0-9a-f]{64})`|=\s*([0-9a-f]{64})\b)"

CONTENT_HASH_RE = re.compile(rf"\*\*Content Hash(?:\s*\([^)]+\))?\*\*{_HASH_SPAN}{_HASH_VALUE}")
PREV_HASH_RE = re.compile(rf"\*\*Previous Hash(?:\s*\([^)]+\))?\*\*{_HASH_SPAN}{_HASH_VALUE}")
CHAIN_HASH_RE = re.compile(rf"\*\*Chain Hash(?:\s*\([^)]+\))?\*\*{_HASH_SPAN}{_HASH_VALUE}")
```

The bold-anchor protection (introduced in Phase 41) remains: prose mentions of "Chain Hash" without the surrounding `**...**` still don't match. The bounded-span discipline (also Phase 41) remains. The two-form value acceptance (also Phase 41) remains. Only the field-name segment widens to accept the parenthetical convention real ledgers use.

The `[A-Z]` character class in `_HASH_SPAN`'s negative lookahead still bounds the span at the next `**FieldName**` marker; parenthetical suffixes after a field name are inside the same `**...**` segment and don't introduce a stop point for the previous field's span.

`verify()` itself is unchanged. The match-group extraction already handles two alternation groups uniformly per Phase 41.

## CI Commands

Operator must run locally before substantiate:

- `python -m pytest tests/test_ledger_hash.py -v`
- `python qor/scripts/ledger_hash.py verify docs/META_LEDGER.md` — should now show OK for all SESSION SEAL entries (#126, #129, #132, #133, #137, #140, #143) and the REMEDIATE PROPOSAL entry #122. Previously these were silently in the "Skipped 39 entries" count.
- `python -m pytest tests/ -v` (full suite — catch any adjacent doctrine-test coupling)

Determinism check: each new test runs twice in a row locally. Deterministic by construction (regex match against fixed text).
