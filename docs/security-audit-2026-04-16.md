# Security + Stability Audit — 2026-04-16

**Scope**: QorLogic governance infrastructure (Phases 17 + 18 additions + legacy core)
**Standard**: OWASP Top 10 (2021) + stability checklist
**Auditor**: security-auditor subagent, dispatched by main session
**Repo state at audit**: main @ 9406864, v0.9.0, 263 tests passing

## Executive Summary

**Total findings: 9** (0 HIGH, 3 MEDIUM, 6 LOW). Overall posture: **MINOR FINDINGS**. No injection, deserialization, or credential vulnerabilities. Ledger/intent-lock crypto is appropriate (SHA-256 for integrity). All subprocess invocations use list-form commands with no shell interpretation. Primary concerns are (1) non-concurrency-safe file writes lacking OS-level locking, (2) `_atomic_append` that degrades to read-modify-write (TOCTOU window), and (3) silent skip of malformed JSONL lines in shadow logs. All findings are integrity-hardening items, not active vulnerabilities.

## OWASP Category Findings

### A01 Broken Access Control — N/A
Local tooling with no multi-tenant access surface. Subprocess invocations (`git`, `gh`) inherit caller identity, which is the intended design.

### A02 Cryptographic Failures — PASS
- SHA-256 used throughout for integrity only (`ledger_hash.py:25`, `shadow_process.py:35-46`, `intent-lock.py:25-30`). No authentication/authorization crypto, no KDF required.
- No MD5/SHA1 usage.
- No hardcoded secrets. `gh` auth delegated to the CLI (`create_shadow_issue.py:31-42`).
- **LOW-1**: `chain_hash = SHA256(content || prev)` in `ledger_hash.py:33-34` uses plain concatenation. Inputs are fixed-length 64-char hex so length-extension is not exploitable, but a separator (`"|"`) or HMAC would be defensive.

### A03 Injection — PASS
- No `shell=True` in repo.
- All `subprocess.run` calls pass argv list-form with static command heads.
- **MEDIUM-1**: `collect_shadow_genomes.py:76-82, 184-192` passes `cwd=str(repo_path)` where `repo_path` comes from user-controlled `~/.qor/repos.json`. Schema (`repos_config.schema.json:22`) only requires `minLength: 1`. A malicious config could point `cwd` at an arbitrary directory. Mitigation: validate path points to a directory containing a `qor/` marker, or confine to allowlisted roots.
- **LOW-2**: `remediate_emit_gate.py:31` uses `session_id` directly in path construction. Internal input, but no sanitization prevents `"../"` or separators. Add regex validation.
- **LOW-3**: `create_shadow_issue.py:193-198` splits `args.events` and passes to `gh` argv without format validation. Low risk; IDs originate from hashed logs.

### A04 Insecure Design — PASS with notes
- **MEDIUM-2**: `shadow_process.py:105-112` silently skips malformed JSONL lines (`except json.JSONDecodeError: continue`). Fail-open for the security-relevant log. If partial-write crash corrupts one line, it vanishes without surfacing. Recommend: stderr warning per-skipped line, track `corruption_count`.
- **LOW-4**: `intent-lock.py:47-50` uses substring match `"PASS" in body`. A file containing "PASS" anywhere admits capture even on VETO audit. Tighten to anchored regex.

### A05 Security Misconfiguration — PASS with notes
- `DEFAULT_REPO` hardcoded in `create_shadow_issue.py:28`; overridable via `--repo`.
- Temp files via `tempfile.NamedTemporaryFile` + `os.replace` across all writers; POSIX 0o600 inherited appropriately.
- **LOW-5**: `intent-lock.py:79` uses deprecated `datetime.utcnow()`. Should be `datetime.now(timezone.utc)` matching `shadow_process.now_iso`.

### A06 Vulnerable Components — PASS
- `pyproject.toml:11` declares `jsonschema>=4` — minimum-bound only. Standard for a library.
- No known CVEs in `jsonschema>=4`.
- No lockfile — acceptable for library posture.

### A07 Identification/Authentication Failures — N/A
No auth surface in scope.

### A08 Software/Data Integrity Failures — PASS with notes
- Ledger chain (`ledger_hash.py:85-114`): `verify()` correctly detects tampering via cascade. Solid.
- No `pickle.load`, unsafe `yaml.load`, `eval`, or `exec` anywhere.
- Intent-lock rehashes plan + audit + git HEAD. Verification detects drift on any axis.
- **MEDIUM-3 (stability)**: `shadow_process._atomic_append` (`shadow_process.py:84-94`) is **not atomic against concurrent writers**. Read → compose → write-temp → `os.replace` allows last-write-wins. Use `fcntl.flock` / `msvcrt.locking`, or true `O_APPEND` with bounded line size.
- **LOW-6**: `ledger_hash.verify()` silently skips entries with non-matching markup (backward compat). Report skip count for auditor visibility.

### A09 Security Logging/Monitoring Failures — PASS with notes
- Every security-relevant operation emits a shadow event. Log-first design.
- `shadow_process.append_event` validates against schema before write. Malformed events rejected loud.
- Silent-skip of corrupted READ lines covered in MEDIUM-2.

### A10 SSRF — N/A
No HTTP/URL fetching. `gh` calls target `--repo <name>` from `DEFAULT_REPO` constant or self-owned config.

## Stability Findings

- **Atomic writes**: All writes use tempfile + `os.replace`. Concurrent-append gap covered in MEDIUM-3.
- **Race conditions**: No file locking. Read-modify-write windows in `append_event`, `write_events_per_source`, `mark_addressed`, `flip_events_only`. Single-operator tooling masks this.
- **Error swallowing**: No bare `except:` or `except: pass`. Specific-type catches throughout.
- **Input validation**: JSON schema consistently applied for gate artifacts and shadow events. `repos_config` schema gap covered in MEDIUM-1.
- **Test coverage of failure paths**: Adequate for admission failures and missing IDs. Missing: corrupted JSONL read, concurrent append.

## Prioritized Remediation

| Severity | Finding | File:Line | Recommendation |
|---|---|---|---|
| MEDIUM | User-controlled `cwd` from config with only minLength validation | `qor/scripts/collect_shadow_genomes.py:76-82, 184-192`; `qor/gates/schema/repos_config.schema.json:22` | Validate path contains `qor/` marker; or confine to allowlist. |
| MEDIUM | Silent skip of corrupted JSONL in shadow log reads | `qor/scripts/shadow_process.py:105-112` | Emit stderr warning per skip; expose corruption count. |
| MEDIUM | `_atomic_append` not concurrency-safe (read-modify-write race) | `qor/scripts/shadow_process.py:84-94` | Add `fcntl.flock` / `msvcrt.locking`, or rewrite to true `O_APPEND` with bounded line size. |
| LOW | Chain hash concat without separator (hygiene) | `qor/scripts/ledger_hash.py:33-34` | Use `SHA256(content + "|" + prev)` or HMAC. |
| LOW | `session_id` unsanitized in path construction | `qor/scripts/remediate_emit_gate.py:31`; `check_shadow_threshold.py:58` | Regex-validate session_id before joining to paths. |
| LOW | Event IDs not format-checked before `gh` argv | `qor/scripts/create_shadow_issue.py:193-198` | Validate IDs as 64-hex before use. |
| LOW | Substring-only PASS check in intent-lock | `tools/reliability/intent-lock.py:47-50` | Anchored regex: `^(Verdict:\|Status:)\s*PASS\s*$` multiline. |
| LOW | `datetime.utcnow()` deprecated | `tools/reliability/intent-lock.py:79` | Replace with `datetime.now(timezone.utc)`. |
| LOW | `ledger_hash.verify()` silently skips non-matching entries | `qor/scripts/ledger_hash.py:102-104` | Report skip count and entry numbers. |

## Posture Summary

**MINOR FINDINGS**. QorLogic demonstrates disciplined defensive programming: no shell injection surface, no unsafe deserialization, consistent schema validation, atomic single-writer file writes, consistent SHA-256 integrity. No exploitable vulnerability. MEDIUM findings are integrity-hardening items relevant to the threat model; LOW findings are hygiene and forward-compatibility. No blocking action required. MEDIUM-1 and MEDIUM-3 worth scheduling in a near-term reliability phase.
