import sqlite3
import json
import hashlib
import time
from local_fortress.mcp_server.sentinel_engine import SentinelEngine

# Configuration
DB_PATH = "local_fortress/ledger/qorelogic_soa_ledger.db"

def get_keys(role):
    """Load keys from local JSON (Prototype only)."""
    try:
        with open(f"{role.lower()}_creds.json", "r") as f:
            creds = json.load(f)
            return creds["did"], creds["private_key"]
    except FileNotFoundError:
        print(f"❌ No credentials found for {role}. Run identity_gen.py first.")
        return None, None

def sign_payload(private_key, data):
    """Mock Signing Function (Ed25519 placeholder)."""
    return f"sig_{role}_{hashlib.sha256(data.encode()).hexdigest()[:8]}"

def log_event(role, event_type, payload, verdict_data=None):
    """Write to the SOA Ledger with Merkle Chaining."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Get last hash
    cursor.execute("SELECT entry_hash FROM soa_ledger ORDER BY entry_id DESC LIMIT 1")
    row = cursor.fetchone()
    prev_hash = row[0] if row else "0"*64
    
    did, priv_key = get_keys(role)
    if not did: return

    # Combine payload with verdict if exists
    final_payload = payload
    if verdict_data:
        final_payload = {**payload, **verdict_data}
    
    payload_str = json.dumps(final_payload, sort_keys=True)
    timestamp = str(time.time())
    
    # Hash Chain
    entry_data = f"{timestamp}{did}{payload_str}{prev_hash}"
    entry_hash = hashlib.sha256(entry_data.encode()).hexdigest()
    
    # Sign
    signature = f"sig_{did[:8]}_{entry_hash[:6]}" # Mock signature
    
    cursor.execute("""
        INSERT INTO soa_ledger (agent_did, event_type, payload, entry_hash, prev_hash, signature)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (did, event_type, payload_str, entry_hash, prev_hash, signature))
    
    conn.commit()
    conn.close()
    print(f"📝 Agent {role} logged {event_type}. Hash: {entry_hash[:12]}...")

def run_audit_simulation():
    print("🚀 Starting Phase 2: Sentinel Audit Simulation\n")
    
    sentinel = SentinelEngine()
    sentinel.check_connection()
    
    # 1. Scrivener Proposes Unsafe Code
    unsafe_code = """
    def payment_process():
        api_key = "EXAMPLE_FAKE_KEY_DO_NOT_USE" # Oops
        os.system("rm -rf /")
    """
    proposal_payload = {"file": "payment.py", "diff": unsafe_code}
    
    print("\n--- Step 1: Scrivener Proposal ---")
    log_event("Scrivener", "PROPOSAL", proposal_payload)
    
    # 2. Sentinel Audits (Fail Case)
    print("\n--- Step 2: Sentinel Audit (L2 Check) ---")
    verdict_fail = sentinel.audit("CODE_DIFF", unsafe_code)
    print(f"Verdict: {verdict_fail['verdict']}")
    print(f"Rationale: {verdict_fail['rationale']}")
    
    log_event("Sentinel", "AUDIT_FAIL", proposal_payload, verdict_fail)
    
    # 3. Judge Penalizes
    print("\n--- Step 3: Judge Enforcement ---")
    if verdict_fail['verdict'] == "FAIL":
        penalty = {"action": "SLASH_WEIGHT", "amount": 0.25, "reason": "Hardcoded Secret"}
        log_event("Judge", "PENALTY", penalty)

    # 4. Scrivener Retry (Clean Code)
    safe_code = """
    def payment_process():
        api_key = os.getenv("API_KEY") 
        process_payment(api_key)
    """
    retry_payload = {"file": "payment.py", "diff": safe_code}
    
    print("\n--- Step 4: Scrivener Retry ---")
    log_event("Scrivener", "PROPOSAL_RETRY", retry_payload)
    
    # 5. Sentinel Re-Audit (Pass Case)
    print("\n--- Step 5: Sentinel Re-Audit (L3 BMC Check) ---")
    verdict_pass = sentinel.audit("CODE_DIFF", safe_code)
    print(f"Verdict: {verdict_pass['verdict']}")
    print(f"Rationale: {verdict_pass['rationale']}")
    print(f"Latency: {verdict_pass.get('latency', 'N/A')}")
    
    log_event("Sentinel", "AUDIT_PASS", retry_payload, verdict_pass)
    
    # 6. Judge Commit
    print("\n--- Step 6: Judge Verification & Commit ---")
    if verdict_pass['verdict'] == "PASS":
        commit_payload = {"status": "MERGED", "ticket": "TICKET-123"}
        log_event("Judge", "COMMIT", commit_payload)

if __name__ == "__main__":
    run_audit_simulation()
