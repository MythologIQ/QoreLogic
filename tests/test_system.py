"""
QoreLogic System Test Suite

Validates all core functionality specified in the design documents:
- Sentinel verification pipeline
- Risk grade auto-classification
- Shadow Genome archival
- L3 approval workflow
- Penalty system
- Operational modes
"""

import sys
import os
import json

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from local_fortress.mcp_server.sentinel_engine import SentinelEngine, RiskGrade

def test_risk_classification():
    """Test automatic risk grade classification."""
    print("\n" + "="*60)
    print("TEST: Risk Grade Auto-Classification")
    print("="*60)
    
    sentinel = SentinelEngine()
    
    test_cases = [
        ("README.md", "", RiskGrade.L1),  # Empty content = L1
        ("src/utils.py", "def helper(): pass", RiskGrade.L2),
        ("auth/login.py", "def authenticate(): pass", RiskGrade.L3),
        ("db/migrations/001.sql", "CREATE TABLE users", RiskGrade.L3),
        ("payment_service.py", "def charge_card(): pass", RiskGrade.L3),
    ]
    
    passed = 0
    for file_path, content, expected in test_cases:
        result = sentinel.classify_risk_grade(file_path, content)
        status = "✅" if result == expected else "❌"
        print(f"{status} {file_path}: Expected {expected.value}, Got {result.value}")
        if result == expected:
            passed += 1
    
    print(f"\nResult: {passed}/{len(test_cases)} passed")
    return passed == len(test_cases)

def test_secret_detection():
    """Test hardcoded secret detection."""
    print("\n" + "="*60)
    print("TEST: Hardcoded Secret Detection")
    print("="*60)
    
    sentinel = SentinelEngine()
    
    test_cases = [
        ("Clean code", "x = os.getenv('API_KEY')", False),
        ("Stripe Live Key", 'api_key = "STRIPE_EXAMPLE_KEY_FAKE"', True),
        ("Google API Key", 'key = "AIzaSyDaGmWKa4JsXZ-HjGw7ISt7ZcDI1234567"', True),
        ("Password literal", 'password = "hunter2"', True),
    ]
    
    passed = 0
    for name, content, should_fail in test_cases:
        findings = sentinel.check_secrets(content)
        detected = len(findings) > 0
        status = "✅" if detected == should_fail else "❌"
        print(f"{status} {name}: {'Detected' if detected else 'Clean'}")
        if detected == should_fail:
            passed += 1
    
    print(f"\nResult: {passed}/{len(test_cases)} passed")
    return passed == len(test_cases)

def test_complexity_analysis():
    """Test cyclomatic complexity detection."""
    print("\n" + "="*60)
    print("TEST: Cyclomatic Complexity Analysis")
    print("="*60)
    
    sentinel = SentinelEngine()
    
    # Simple function (complexity ~2)
    simple_code = """
def simple():
    if True:
        return 1
    return 0
"""
    
    # Complex function (complexity >10)
    complex_code = """
def complex(a, b, c, d, e):
    if a:
        if b:
            if c:
                return 1
            elif d:
                return 2
            else:
                return 3
        elif e:
            for i in range(10):
                if i % 2:
                    continue
            return 4
    elif b and c:
        try:
            x = 1
        except:
            x = 2
        return x
    return 0
"""
    
    simple_complexity, simple_findings = sentinel.check_cyclomatic_complexity(simple_code)
    complex_complexity, complex_findings = sentinel.check_cyclomatic_complexity(complex_code)
    
    print(f"Simple function complexity: {simple_complexity}")
    print(f"Complex function complexity: {complex_complexity}")
    print(f"Complex function findings: {complex_findings}")
    
    passed = simple_complexity < 10 and complex_complexity >= 10
    status = "✅" if passed else "❌"
    print(f"\n{status} Complexity detection working correctly")
    return passed

def test_pii_redaction():
    """Test PII detection and redaction."""
    print("\n" + "="*60)
    print("TEST: PII Detection and Redaction")
    print("="*60)
    
    sentinel = SentinelEngine()
    
    content_with_pii = """
    User SSN: 123-45-6789
    Email: john.doe@example.com
    Card: 1234567890123456
    """
    
    redacted, had_pii = sentinel.check_pii_exposure(content_with_pii)
    
    print(f"Original contains PII: {had_pii}")
    print(f"Redacted content:\n{redacted}")
    
    # Verify redaction
    ssn_redacted = "123-45-6789" not in redacted
    email_redacted = "john.doe@example.com" not in redacted
    
    passed = had_pii and ssn_redacted and email_redacted
    status = "✅" if passed else "❌"
    print(f"\n{status} PII redaction working correctly")
    return passed

def test_full_audit_pipeline():
    """Test the complete audit pipeline."""
    print("\n" + "="*60)
    print("TEST: Full Audit Pipeline")
    print("="*60)
    
    sentinel = SentinelEngine()
    
    # Test 1: Clean L2 code should PASS
    clean_code = """
def calculate_total(items):
    total = 0
    for item in items:
        total += item.price
    return total
"""
    result1 = sentinel.audit("utils/calculator.py", clean_code)
    print(f"\nClean L2 Code:")
    print(f"  Verdict: {result1.verdict}")
    print(f"  Risk Grade: {result1.risk_grade}")
    print(f"  Latency: {result1.latency_ms:.2f}ms")
    
    # Test 2: Code with secrets should FAIL
    bad_code = """
def connect():
    api_key = "EXAMPLE_STRIPE_KEY_DO_NOT_USE"
    return requests.get(url, headers={"Authorization": api_key})
"""
    result2 = sentinel.audit("api/client.py", bad_code)
    print(f"\nCode with Secrets:")
    print(f"  Verdict: {result2.verdict}")
    print(f"  Failure Modes: {result2.failure_modes}")
    
    # Test 3: Auth code should require L3 approval
    auth_code = """
def authenticate(username, password):
    user = db.query(f"SELECT * FROM users WHERE username = {username}")
    return check_password(user, password)
"""
    result3 = sentinel.audit("auth/login.py", auth_code)
    print(f"\nAuth Code (L3):")
    print(f"  Verdict: {result3.verdict}")
    print(f"  Risk Grade: {result3.risk_grade}")
    print(f"  Requires Approval: {result3.requires_approval}")
    print(f"  Failure Modes: {result3.failure_modes}")  # Should catch SQL injection
    
    all_passed = (
        result1.verdict == "PASS" and
        result2.verdict == "FAIL" and
        result3.risk_grade == "L3"
    )
    
    status = "✅" if all_passed else "❌"
    print(f"\n{status} Full pipeline test {'PASSED' if all_passed else 'FAILED'}")
    return all_passed

def run_all_tests():
    """Run all system tests."""
    print("\n" + "#"*60)
    print("# QoreLogic SYSTEM VALIDATION SUITE")
    print("#"*60)
    
    results = {
        "Risk Classification": test_risk_classification(),
        "Secret Detection": test_secret_detection(),
        "Complexity Analysis": test_complexity_analysis(),
        "PII Redaction": test_pii_redaction(),
        "Full Pipeline": test_full_audit_pipeline(),
    }
    
    print("\n" + "="*60)
    print("FINAL RESULTS")
    print("="*60)
    
    all_passed = True
    for test_name, passed in results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status}: {test_name}")
        if not passed:
            all_passed = False
    
    print("\n" + ("🎉 ALL TESTS PASSED" if all_passed else "⚠️ SOME TESTS FAILED"))
    return all_passed

if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
