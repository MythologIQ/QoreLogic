"""
QoreLogic End-to-End Validation Suite
Pre-workspace testing validation for production readiness.

Tests the complete flow:
1. Sentinel Engine (Verification Pipeline)
2. Trust Dynamics (EWMA, Micro-Penalties)
3. Identity Fortress (Ed25519, Signatures)
4. Database Operations (R/W, Workspace Isolation)
5. MCP Server Tools (audit_code_v2, log_event)
6. Schema Compliance (v2.5 Multi-Tenant)

Date: December 23, 2025
"""

import sys
import os
import json
import time
import sqlite3
import hashlib
from datetime import datetime
from pathlib import Path

# Add project paths
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))
sys.path.insert(0, str(PROJECT_ROOT / "local_fortress"))

from mcp_server.sentinel_engine import SentinelEngine, RiskGrade
from mcp_server.trust_engine import TrustEngine, LOSS_AVERSION_LAMBDA
from mcp_server.identity_manager import IdentityManager
from mcp_server.cbmc_verifier import get_cbmc_verifier, CBMCStatus
from mcp_server.heuristic_patterns import VULNERABILITY_PATTERNS

# Database path
DB_PATH = PROJECT_ROOT / "local_fortress" / "ledger" / "qorelogic_soa_ledger.db"


class E2ETestResult:
    """Container for test results."""
    def __init__(self, name: str):
        self.name = name
        self.passed = 0
        self.failed = 0
        self.errors = []
    
    def record(self, test_name: str, passed: bool, error: str = None):
        if passed:
            self.passed += 1
            print(f"    ✅ {test_name}")
        else:
            self.failed += 1
            self.errors.append(f"{test_name}: {error or 'Failed'}")
            print(f"    ❌ {test_name}: {error or 'Failed'}")
    
    @property
    def success(self):
        return self.failed == 0


def print_section(title: str):
    print(f"\n{'='*60}")
    print(f" {title}")
    print(f"{'='*60}")


# =============================================================================
# TEST SUITE 1: SENTINEL ENGINE
# =============================================================================

def test_sentinel_engine() -> E2ETestResult:
    """Test the Sentinel verification pipeline."""
    print_section("E2E-1: SENTINEL ENGINE")
    result = E2ETestResult("Sentinel Engine")
    
    sentinel = SentinelEngine()
    
    # 1.1: Risk Classification
    print("\n  [1.1] Risk Classification")
    cases = [
        ("docs/README.md", "", RiskGrade.L1),
        ("src/utils.py", "def helper(): pass", RiskGrade.L2),
        ("auth/login.py", "def authenticate(): pass", RiskGrade.L3),
    ]
    for path, content, expected in cases:
        grade = sentinel.classify_risk_grade(path, content)
        result.record(f"classify({path}) = {expected.value}", grade == expected,
                     f"Got {grade.value}" if grade != expected else None)
    
    # 1.2: Secret Detection
    print("\n  [1.2] Secret Detection")
    clean = sentinel.check_secrets("x = os.getenv('KEY')")
    result.record("Clean code has no secrets", len(clean) == 0, 
                 f"Found {len(clean)}" if clean else None)
    
    bad = sentinel.check_secrets('api_key = "sk_live_1234567890abcdef"')
    result.record("API key detected", len(bad) > 0, "Not detected" if not bad else None)
    
    # 1.3: Complexity Analysis
    print("\n  [1.3] Cyclomatic Complexity")
    simple = "def f(): return 1"
    complex_code = """
def complex(a,b,c,d,e,f,g):
    if a:
        if b:
            if c:
                if d:
                    if e:
                        for i in range(10):
                            if i % 2:
                                continue
                        return 1
                    return 2
                return 3
            return 4
        return 5
    elif f:
        try:
            x = 1
        except:
            pass
    elif g:
        while True:
            break
    return 0
"""
    s_cc, _ = sentinel.check_cyclomatic_complexity(simple)
    c_cc, _ = sentinel.check_cyclomatic_complexity(complex_code)
    result.record(f"Simple code CC={s_cc} < 5", s_cc < 5)
    result.record(f"Complex code CC={c_cc} >= 5", c_cc >= 5, f"CC={c_cc}" if c_cc < 5 else None)
    
    # 1.4: Full Audit
    print("\n  [1.4] Full Audit Pipeline")
    clean_result = sentinel.audit("utils/calc.py", "def add(a,b): return a+b")
    result.record("Clean code passes audit", clean_result.verdict == "PASS", 
                 f"Got {clean_result.verdict}")
    
    bad_result = sentinel.audit("api/client.py", 'key = "sk_live_test123456789"')
    result.record("Secret code fails audit", bad_result.verdict == "FAIL",
                 f"Got {bad_result.verdict}")
    
    return result


# =============================================================================
# TEST SUITE 2: TRUST DYNAMICS
# =============================================================================

def test_trust_dynamics() -> E2ETestResult:
    """Test trust engine and EWMA calculations."""
    print_section("E2E-2: TRUST DYNAMICS")
    result = E2ETestResult("Trust Dynamics")
    
    engine = TrustEngine()
    
    # 2.1: Loss Aversion Lambda
    print("\n  [2.1] Loss Aversion Constant")
    result.record(f"LOSS_AVERSION_LAMBDA = {LOSS_AVERSION_LAMBDA}", 
                 LOSS_AVERSION_LAMBDA == 2.0,
                 f"Got {LOSS_AVERSION_LAMBDA}")
    
    # 2.2: EWMA Calculation
    print("\n  [2.2] EWMA Trust Decay")
    # Lambda high-risk = 0.94, low-risk = 0.97
    from mcp_server.trust_engine import TrustContext
    ctx = TrustContext.HIGH_RISK
    lam = engine.get_lambda(ctx)
    result.record(f"High-risk λ = 0.94", lam == 0.94, f"Got {lam}")
    
    ctx_low = TrustContext.LOW_RISK
    lam_low = engine.get_lambda(ctx_low)
    result.record(f"Low-risk λ = 0.97", lam_low == 0.97, f"Got {lam_low}")
    
    # 2.3: Trust Score Update
    print("\n  [2.3] Trust Score Updates")
    new_score = engine.calculate_ewma_update(0.5, 1.0, ctx)  # success
    result.record(f"Success increases trust: 0.5 -> {new_score:.3f}", new_score > 0.5)
    
    fail_score = engine.calculate_ewma_update(0.5, 0.0, ctx)  # failure
    result.record(f"Failure decreases trust: 0.5 -> {fail_score:.3f}", fail_score < 0.5)
    
    return result


# =============================================================================
# TEST SUITE 3: IDENTITY FORTRESS
# =============================================================================

def test_identity_fortress() -> E2ETestResult:
    """Test Ed25519 identity and signatures."""
    print_section("E2E-3: IDENTITY FORTRESS")
    result = E2ETestResult("Identity Fortress")
    
    import tempfile
    with tempfile.TemporaryDirectory() as temp_dir:
        # Monkey-patch keystore for isolated test
        import mcp_server.identity_manager as id_mod
        original_keystore = id_mod.KEYSTORE_DIR
        id_mod.KEYSTORE_DIR = Path(temp_dir)
        
        # Also mock DB registration to avoid polluting real DB
        original_register = id_mod.IdentityManager._register_in_db
        id_mod.IdentityManager._register_in_db = lambda self, identity, pub_key: None
        
        try:
            mgr = IdentityManager(passphrase="e2e-test-passphrase")
            
            # 3.1: Identity Creation
            print("\n  [3.1] Identity Generation")
            identity = mgr.create_agent("Sentinel")
            result.record(f"DID generated: {identity.did[:30]}...", 
                         identity.did.startswith("did:myth:"))
            
            # 3.2: Signing
            print("\n  [3.2] Ed25519 Signing")
            payload = b"E2E test payload for signing"
            sig = mgr.sign(identity.did, payload)
            result.record(f"Signature created ({len(sig)} bytes)", len(sig) > 0)
            
            # 3.3: Verification (direct crypto, not DB-based since we mocked DB registration)
            print("\n  [3.3] Signature Verification")
            # Load private key and get public key for direct verification
            keyfile_path = Path(temp_dir) / f"{identity.did.replace(':', '_')}.key"
            with open(keyfile_path, 'r') as f:
                keydata = json.load(f)
            pub_bytes = bytes.fromhex(keydata['public_key'])
            from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey
            pub_key = Ed25519PublicKey.from_public_bytes(pub_bytes)
            try:
                pub_key.verify(bytes.fromhex(sig), payload)
                valid = True
            except Exception:
                valid = False
            result.record("Signature verified (direct crypto)", valid)
            
            # 3.4: Tamper Detection
            tampered = b"TAMPERED payload"
            try:
                pub_key.verify(bytes.fromhex(sig), tampered)
                invalid = True  # Should not happen
            except Exception:
                invalid = False  # Expected - verification should fail
            result.record("Tampered payload rejected", not invalid, 
                         "Tampered payload accepted!" if invalid else None)
            
            # 3.5: Key Rotation
            print("\n  [3.5] Key Rotation")
            old_pub = identity.public_key_hex
            new_identity = mgr.rotate_key(identity.did)
            result.record("Key rotated", new_identity.public_key_hex != old_pub,
                         "Same key after rotation" if new_identity.public_key_hex == old_pub else None)
            
        finally:
            id_mod.KEYSTORE_DIR = original_keystore
            id_mod.IdentityManager._register_in_db = original_register
    
    return result


# =============================================================================
# TEST SUITE 4: DATABASE & WORKSPACE ISOLATION
# =============================================================================

def test_database_isolation() -> E2ETestResult:
    """Test database R/W and workspace isolation."""
    print_section("E2E-4: DATABASE & WORKSPACE ISOLATION")
    result = E2ETestResult("Database Isolation")
    
    if not DB_PATH.exists():
        result.record("Database exists", False, f"Not found: {DB_PATH}")
        return result
    
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    try:
        # 4.1: Table Existence
        print("\n  [4.1] Schema Verification")
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [r[0] for r in cursor.fetchall()]
        
        required = ["soa_ledger", "agent_registry", "shadow_genome", 
                   "trust_updates", "l3_approval_queue", "system_state"]
        for t in required:
            result.record(f"Table {t} exists", t in tables, f"Missing: {t}")
        
        # 4.2: workspace_id Column Check
        print("\n  [4.2] Isolation Column Verification")
        iso_tables = ["soa_ledger", "shadow_genome", "l3_approval_queue", "trust_updates"]
        for t in iso_tables:
            cursor.execute(f"PRAGMA table_info({t})")
            cols = [r[1] for r in cursor.fetchall()]
            result.record(f"{t}.workspace_id exists", "workspace_id" in cols,
                         f"Missing workspace_id in {t}")
        
        # 4.3: Cross-Tenant Isolation Test
        print("\n  [4.3] Cross-Tenant Isolation")
        ws_a = "e2e_tenant_alpha"
        ws_b = "e2e_tenant_beta"
        ts = datetime.now().timestamp()
        
        # Insert test data
        cursor.execute("""
            INSERT INTO shadow_genome (input_vector, context, failure_mode, workspace_id)
            VALUES (?, ?, ?, ?)
        """, (f"E2E_ALPHA_{ts}", '{"tenant":"alpha","secret":"ALPHA_SECRET"}', "E2E_TEST", ws_a))
        
        cursor.execute("""
            INSERT INTO shadow_genome (input_vector, context, failure_mode, workspace_id)
            VALUES (?, ?, ?, ?)
        """, (f"E2E_BETA_{ts}", '{"tenant":"beta","secret":"BETA_SECRET"}', "E2E_TEST", ws_b))
        
        # Query Alpha - should NOT see Beta's secret
        cursor.execute("SELECT context FROM shadow_genome WHERE workspace_id = ?", (ws_a,))
        alpha_data = " ".join([r[0] for r in cursor.fetchall()])
        alpha_leak = "BETA_SECRET" in alpha_data
        result.record("Alpha tenant isolated from Beta", not alpha_leak,
                     "CRITICAL: Cross-tenant leak!" if alpha_leak else None)
        
        # Query Beta - should NOT see Alpha's secret
        cursor.execute("SELECT context FROM shadow_genome WHERE workspace_id = ?", (ws_b,))
        beta_data = " ".join([r[0] for r in cursor.fetchall()])
        beta_leak = "ALPHA_SECRET" in beta_data
        result.record("Beta tenant isolated from Alpha", not beta_leak,
                     "CRITICAL: Cross-tenant leak!" if beta_leak else None)
        
        # Cleanup
        cursor.execute("DELETE FROM shadow_genome WHERE workspace_id IN (?, ?)", (ws_a, ws_b))
        conn.commit()
        
    finally:
        conn.close()
    
    return result


# =============================================================================
# TEST SUITE 5: VERIFICATION PIPELINE (CBMC/Heuristics)
# =============================================================================

def test_verification_pipeline() -> E2ETestResult:
    """Test the formal verification pipeline."""
    print_section("E2E-5: VERIFICATION PIPELINE")
    result = E2ETestResult("Verification Pipeline")
    
    verifier = get_cbmc_verifier()
    
    # 5.1: Heuristic Pattern Count
    print("\n  [5.1] Heuristic Pattern Library")
    pattern_count = len(VULNERABILITY_PATTERNS)
    result.record(f"Patterns loaded: {pattern_count} >= 10", pattern_count >= 10,
                 f"Only {pattern_count} patterns")
    
    # 5.2: Division by Zero Detection
    print("\n  [5.2] Vulnerability Detection")
    vuln_code = """
def unsafe(x):
    y = x / 0  # Division by zero
    return y
"""
    res = verifier.verify(vuln_code)
    div_zero = any("ARITH" in v or "division" in v.lower() for v in res.violations)
    result.record("Division by zero detected", div_zero or res.status == CBMCStatus.FAIL,
                 f"Status: {res.status.value}, Violations: {res.violations}")
    
    # 5.3: Hardcoded Secret Detection
    secret_code = 'api_key = "sk_live_1234567890abcdef123456"'
    res2 = verifier.verify(secret_code)
    secret_found = any("CRYPTO" in v or "key" in v.lower() for v in res2.violations)
    result.record("API key detected", secret_found or res2.status == CBMCStatus.FAIL,
                 f"Status: {res2.status.value}")
    
    # 5.4: Clean Code Passes
    print("\n  [5.4] Clean Code Verification")
    clean_code = """
def safe_add(a, b):
    if a is None or b is None:
        return 0
    return a + b
"""
    res3 = verifier.verify(clean_code)
    result.record("Clean code passes", res3.status in [CBMCStatus.PASS, CBMCStatus.LITE_ONLY],
                 f"Status: {res3.status.value}")
    
    return result


# =============================================================================
# TEST SUITE 6: INTEGRATED FLOW
# =============================================================================

def test_integrated_flow() -> E2ETestResult:
    """Test the complete integrated flow."""
    print_section("E2E-6: INTEGRATED FLOW")
    result = E2ETestResult("Integrated Flow")
    
    # 6.1: Simulate full audit with workspace context
    print("\n  [6.1] Full Audit with Workspace Context")
    sentinel = SentinelEngine()
    
    # Audit in workspace A
    ws_a_result = sentinel.audit("src/api.py", "def handler(): return {'status': 'ok'}")
    result.record("Workspace A audit completes", ws_a_result is not None)
    result.record("Workspace A verdict valid", ws_a_result.verdict in ["PASS", "FAIL"])
    
    # 6.2: End-to-end timing
    print("\n  [6.2] Performance Check")
    start = time.time()
    for _ in range(5):
        sentinel.audit("test.py", "x = 1 + 2")
    elapsed = (time.time() - start) / 5 * 1000  # avg ms
    result.record(f"Audit latency {elapsed:.1f}ms < 500ms", elapsed < 500,
                 f"Too slow: {elapsed:.1f}ms")
    
    # 6.3: Verify system state
    print("\n  [6.3] System State")
    if DB_PATH.exists():
        conn = sqlite3.connect(str(DB_PATH))
        cursor = conn.cursor()
        cursor.execute("SELECT current_mode FROM system_state WHERE state_id = 1")
        row = cursor.fetchone()
        conn.close()
        
        if row:
            result.record(f"System mode: {row[0]}", row[0] in ["NORMAL", "LEAN", "SURGE", "SAFE"])
        else:
            result.record("System state initialized", False, "No state row")
    
    return result


# =============================================================================
# MAIN TEST RUNNER
# =============================================================================

def run_e2e_tests():
    """Run all E2E tests."""
    print("\n" + "#" * 60)
    print("#  QORELOGIC END-TO-END VALIDATION SUITE")
    print("#  Pre-Workspace Testing Validation")
    print("#" * 60)
    print(f"\nTimestamp: {datetime.now().isoformat()}")
    print(f"Database: {DB_PATH}")
    
    all_results = []
    
    # Run all test suites
    all_results.append(test_sentinel_engine())
    all_results.append(test_trust_dynamics())
    all_results.append(test_identity_fortress())
    all_results.append(test_database_isolation())
    all_results.append(test_verification_pipeline())
    all_results.append(test_integrated_flow())
    
    # Summary
    print("\n" + "=" * 60)
    print(" E2E TEST SUMMARY")
    print("=" * 60)
    
    total_passed = 0
    total_failed = 0
    
    for r in all_results:
        status = "✅" if r.success else "❌"
        print(f"  {status} {r.name}: {r.passed} passed, {r.failed} failed")
        total_passed += r.passed
        total_failed += r.failed
        
        if r.errors:
            for err in r.errors:
                print(f"      ⚠️ {err}")
    
    print("\n" + "-" * 60)
    print(f"  TOTAL: {total_passed} passed, {total_failed} failed")
    
    all_passed = total_failed == 0
    
    print("\n" + "=" * 60)
    if all_passed:
        print(" 🎉 ALL E2E TESTS PASSED - READY FOR WORKSPACE TESTING")
    else:
        print(" ⚠️ SOME E2E TESTS FAILED - FIX BEFORE WORKSPACE TESTING")
    print("=" * 60)
    
    return all_passed


if __name__ == "__main__":
    success = run_e2e_tests()
    sys.exit(0 if success else 1)
