import argparse
import sys
import os
import sqlite3
import json
import hashlib
import time

# Ensure we can import from local_fortress
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from local_fortress.mcp_server.sentinel_engine import SentinelEngine
except ImportError:
    # Fallback if running from root
    from local_fortress.mcp_server.sentinel_engine import SentinelEngine

DB_PATH = os.path.join("local_fortress", "ledger", "qdna_soa_ledger.db")


# Load Workflow Configuration
CONFIG_PATH = os.path.join(os.path.dirname(__file__), "config", "workflow_map.json")
WORKFLOW_MAP = {}
if os.path.exists(CONFIG_PATH):
    with open(CONFIG_PATH, "r") as f:
        data = json.load(f)
        WORKFLOW_MAP = data.get("workflow_roles", {})

def get_keys(role):
    """
    Dynamic Credential Loading.
    Looks for {role}_creds.json in the local_fortress/mcp_server directory.
    """
    # Try various paths to find the creds
    potential_paths = [
        f"{role.lower()}_creds.json",
        os.path.join("local_fortress", "mcp_server", f"{role.lower()}_creds.json")
    ]
    
    for p in potential_paths:
        if os.path.exists(p):
            with open(p, "r") as f:
                creds = json.load(f)
                return creds["did"]
    
    print(f"⚠️ Warning: No credentials found for role '{role}'. Using Mock DID.")
    return f"did:myth:{role.lower()}:mock"

def log_event(role, event_type, payload, verdict_data=None):
    """Write verdict to the Sovereign Ledger."""
    if not os.path.exists(DB_PATH):
        print(f"❌ Error: Ledger not found at {DB_PATH}")
        return

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Merkle Chain: Get previous hash
    cursor.execute("SELECT entry_hash FROM soa_ledger ORDER BY entry_id DESC LIMIT 1")
    row = cursor.fetchone()
    prev_hash = row[0] if row else "0"*64
    
    did = get_keys(role)
    
    # Construct Payload
    final_payload = payload
    if verdict_data:
        final_payload = {**payload, **verdict_data}
    
    payload_str = json.dumps(final_payload, sort_keys=True)
    timestamp = str(time.time())
    
    # Hash
    entry_data = f"{timestamp}{did}{payload_str}{prev_hash}"
    entry_hash = hashlib.sha256(entry_data.encode()).hexdigest()
    signature = f"sig_{did[:8]}_{entry_hash[:6]}" 
    
    cursor.execute("""
        INSERT INTO soa_ledger (agent_did, event_type, payload, entry_hash, prev_hash, signature)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (did, event_type, payload_str, entry_hash, prev_hash, signature))
    
    conn.commit()
    conn.close()
    return entry_hash

def audit_file(file_path):
    """Run the Sentinel against a real file on disk."""
    if not os.path.exists(file_path):
        print(f"❌ File not found: {file_path}")
        sys.exit(1)

    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    print(f"🛡️ Sentinel Auditing: {file_path} ({len(content)} bytes)...")
    
    # 1. Initialize Engine
    sentinel = SentinelEngine()
    

    # 2. Assign Roles from Config
    task_config = WORKFLOW_MAP.get("audit_file", {"executor_role": "Sentinel", "approver_role": "Judge"})
    executor = task_config["executor_role"]
    approver = task_config["approver_role"]
    
    # 3. Run Audit (The Executor)
    verdict = sentinel.audit("CODE_DIFF", content)
    
    # 4. Output Result
    print("\n--- 🏁 Verification Verdict ---")
    print(f"Status: {verdict['verdict']}")
    print(f"Rationale: {verdict['rationale']}")
    if "latency" in verdict:
        print(f"Latency: {verdict['latency']}")
    
    # 5. Log to Ledger (The Approver/Witness)
    # Log Proposal (Implicitly the User/Scrivener)
    log_event("Scrivener", "FILE_AUDIT_REQUEST", {"file": file_path})
    
    # Log Verdict
    h = log_event(executor, "AUDIT_VERDICT", {"file": file_path}, verdict)
    print(f"\n✅ Recorded in Sovereign Ledger by {executor}. Hash: {h[:12]}...")

    if verdict['verdict'] == "FAIL":
        sys.exit(1) # Return error code for CI/CD blocking

def main():
    parser = argparse.ArgumentParser(description="Q-DNA Soverign Gatekeeper")
    subparsers = parser.add_subparsers(dest="command")
    
    # Audit Command
    audit_parser = subparsers.add_parser("audit", help="Audit a specific file")
    audit_parser.add_argument("file", help="Path to the file to verify")
    
    args = parser.parse_args()
    
    if args.command == "audit":
        audit_file(args.file)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
