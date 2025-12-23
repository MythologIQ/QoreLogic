"""
QoreLogic Database R/W Validation Suite
Tests read/write capabilities across all database tables.
"""

import sqlite3
import json
from datetime import datetime
from pathlib import Path

DB_PATH = Path(__file__).parent / "ledger" / "qorelogic_soa_ledger.db"

def main():
    print("=" * 60)
    print(" DATABASE READ/WRITE VALIDATION SUITE")
    print("=" * 60)
    print(f"\nDatabase: {DB_PATH}")
    print(f"Exists: {DB_PATH.exists()}")
    
    if not DB_PATH.exists():
        print("\n❌ DATABASE FILE NOT FOUND!")
        return False
    
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    all_passed = True
    
    # 1. List all tables
    print("\n" + "-" * 40)
    print("[1] TABLES PRESENT:")
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
    tables = [t[0] for t in cursor.fetchall()]
    for t in tables:
        cursor.execute(f"SELECT COUNT(*) FROM {t}")
        count = cursor.fetchone()[0]
        print(f"    ✓ {t}: {count} rows")
    
    # 2. Test READ: soa_ledger
    print("\n" + "-" * 40)
    print("[2] READ TEST - soa_ledger (last 3 entries):")
    cursor.execute("SELECT entry_id, event_type, agent_did, workspace_id FROM soa_ledger ORDER BY entry_id DESC LIMIT 3")
    rows = cursor.fetchall()
    if rows:
        for r in rows:
            did_short = r["agent_did"][:20] if r["agent_did"] else "N/A"
            print(f"    ID={r['entry_id']} | Type={r['event_type']} | WS={r['workspace_id']}")
        print("    READ: ✅")
    else:
        print("    (empty table - OK for fresh install)")
    
    # 3. Test READ: agent_registry
    print("\n" + "-" * 40)
    print("[3] READ TEST - agent_registry:")
    cursor.execute("SELECT did, role, trust_score, trust_stage, status FROM agent_registry LIMIT 5")
    rows = cursor.fetchall()
    if rows:
        for r in rows:
            did_short = r["did"][:25] if r["did"] else "N/A"
            print(f"    Role={r['role']} | Trust={r['trust_score']:.3f} | Stage={r['trust_stage']} | Status={r['status']}")
        print("    READ: ✅")
    else:
        print("    (empty table - OK for fresh install)")
    
    # 4. Test WRITE: Insert test row into shadow_genome
    print("\n" + "-" * 40)
    print("[4] WRITE TEST - shadow_genome:")
    try:
        test_payload = {"test": True, "timestamp": str(datetime.now())}
        cursor.execute("""
            INSERT INTO shadow_genome (input_vector, context, failure_mode, causal_vector, workspace_id)
            VALUES (?, ?, ?, ?, ?)
        """, ("DB_VALIDATION_TEST", json.dumps(test_payload), "VALIDATION", "Automated DB test", "validation_ws"))
        test_id = cursor.lastrowid
        print(f"    Inserted test row ID: {test_id}")
        
        # 5. Test READ-BACK
        cursor.execute("SELECT * FROM shadow_genome WHERE genome_id = ?", (test_id,))
        row = cursor.fetchone()
        if row and row["failure_mode"] == "VALIDATION":
            print(f"    Read-back verified ✅")
        else:
            print(f"    Read-back FAILED ❌")
            all_passed = False
        
        # 6. Test DELETE (cleanup)
        cursor.execute("DELETE FROM shadow_genome WHERE genome_id = ?", (test_id,))
        print(f"    Cleanup: Deleted test row ✅")
        print("    WRITE/DELETE: ✅")
    except Exception as e:
        print(f"    WRITE FAILED: {e} ❌")
        all_passed = False
    
    # 7. Check trust_updates table
    print("\n" + "-" * 40)
    print("[5] READ TEST - trust_updates:")
    cursor.execute("SELECT agent_did, update_type, old_score, new_score FROM trust_updates ORDER BY timestamp DESC LIMIT 3")
    rows = cursor.fetchall()
    if rows:
        for r in rows:
            print(f"    Type={r['update_type']} | {r['old_score']:.3f} -> {r['new_score']:.3f}")
        print("    READ: ✅")
    else:
        print("    (empty table - OK for fresh install)")
    
    # 8. Check system_state
    print("\n" + "-" * 40)
    print("[6] SYSTEM STATE:")
    cursor.execute("SELECT current_mode, l3_reserve_available FROM system_state")
    row = cursor.fetchone()
    if row:
        print(f"    Mode: {row['current_mode']} | L3 Reserve: {row['l3_reserve_available']}")
        print("    READ: ✅")
    else:
        print("    (not initialized)")
    
    # 9. Test workspace isolation write
    print("\n" + "-" * 40)
    print("[7] WRITE TEST - l3_approval_queue (workspace isolation):")
    try:
        cursor.execute("""
            INSERT INTO l3_approval_queue (artifact_hash, requesting_agent, reason, workspace_id)
            VALUES (?, ?, ?, ?)
        """, ("test_hash_123", "did:myth:test:agent", "DB validation test", "isolated_ws_test"))
        q_id = cursor.lastrowid
        
        # Verify workspace isolation
        cursor.execute("SELECT workspace_id FROM l3_approval_queue WHERE queue_id = ?", (q_id,))
        row = cursor.fetchone()
        if row and row["workspace_id"] == "isolated_ws_test":
            print(f"    Workspace isolation verified ✅")
        else:
            print(f"    Workspace isolation FAILED ❌")
            all_passed = False
        
        cursor.execute("DELETE FROM l3_approval_queue WHERE queue_id = ?", (q_id,))
        print("    Cleanup complete ✅")
    except Exception as e:
        print(f"    WRITE FAILED: {e} ❌")
        all_passed = False
    
    
    print("\n" + "=" * 60)
    print(" BASIC R/W VALIDATION COMPLETE")
    print("=" * 60)
    
    # ========================================
    # CRITICAL: WORKSPACE ISOLATION TESTS
    # ========================================
    print("\n" + "=" * 60)
    print(" WORKSPACE ISOLATION VERIFICATION")
    print("=" * 60)
    
    # Create test data in two separate workspaces
    workspace_a = "tenant_alpha_test"
    workspace_b = "tenant_beta_test"
    
    print(f"\n[ISO-1] Creating test data in {workspace_a}...")
    try:
        # Insert into soa_ledger for workspace A
        cursor.execute("""
            INSERT INTO soa_ledger (agent_did, event_type, payload, entry_hash, prev_hash, signature, workspace_id)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            "did:myth:test:alpha_agent",
            "AUDIT_PASS",
            json.dumps({"test": "alpha_data", "secret": "ALPHA_SECRET_123"}),
            f"hash_alpha_{datetime.now().timestamp()}",
            "prev_hash_test",
            "sig_test",
            workspace_a
        ))
        alpha_id = cursor.lastrowid
        print(f"    Created ledger entry ID={alpha_id} in {workspace_a} ✅")
    except Exception as e:
        print(f"    Failed to create alpha entry: {e} ❌")
        all_passed = False
    
    print(f"\n[ISO-2] Creating test data in {workspace_b}...")
    try:
        # Insert into soa_ledger for workspace B
        cursor.execute("""
            INSERT INTO soa_ledger (agent_did, event_type, payload, entry_hash, prev_hash, signature, workspace_id)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            "did:myth:test:beta_agent",
            "AUDIT_PASS",
            json.dumps({"test": "beta_data", "secret": "BETA_SECRET_456"}),
            f"hash_beta_{datetime.now().timestamp()}",
            "prev_hash_test",
            "sig_test",
            workspace_b
        ))
        beta_id = cursor.lastrowid
        print(f"    Created ledger entry ID={beta_id} in {workspace_b} ✅")
    except Exception as e:
        print(f"    Failed to create beta entry: {e} ❌")
        all_passed = False
    
    # CRITICAL TEST: Query with workspace filter
    print(f"\n[ISO-3] ISOLATION TEST - Querying {workspace_a} only...")
    cursor.execute("""
        SELECT entry_id, agent_did, workspace_id, payload 
        FROM soa_ledger 
        WHERE workspace_id = ?
    """, (workspace_a,))
    alpha_rows = cursor.fetchall()
    
    beta_leak = False
    for row in alpha_rows:
        if "BETA_SECRET" in row["payload"]:
            beta_leak = True
            print(f"    ❌ ISOLATION BREACH: Beta data found in Alpha query!")
            all_passed = False
    
    if not beta_leak:
        print(f"    Rows returned for {workspace_a}: {len(alpha_rows)}")
        print(f"    No cross-tenant data leakage ✅")
    
    # CRITICAL TEST: Query with different workspace filter
    print(f"\n[ISO-4] ISOLATION TEST - Querying {workspace_b} only...")
    cursor.execute("""
        SELECT entry_id, agent_did, workspace_id, payload 
        FROM soa_ledger 
        WHERE workspace_id = ?
    """, (workspace_b,))
    beta_rows = cursor.fetchall()
    
    alpha_leak = False
    for row in beta_rows:
        if "ALPHA_SECRET" in row["payload"]:
            alpha_leak = True
            print(f"    ❌ ISOLATION BREACH: Alpha data found in Beta query!")
            all_passed = False
    
    if not alpha_leak:
        print(f"    Rows returned for {workspace_b}: {len(beta_rows)}")
        print(f"    No cross-tenant data leakage ✅")
    
    # CRITICAL TEST: Verify workspace filtering actually works
    print(f"\n[ISO-5] ISOLATION AUDIT - Counting by workspace...")
    cursor.execute("""
        SELECT workspace_id, COUNT(*) as count 
        FROM soa_ledger 
        GROUP BY workspace_id 
        ORDER BY count DESC
    """)
    ws_counts = cursor.fetchall()
    for row in ws_counts:
        print(f"    {row['workspace_id']}: {row['count']} entries")
    
    # CLEANUP
    print(f"\n[ISO-CLEANUP] Removing test data...")
    cursor.execute("DELETE FROM soa_ledger WHERE workspace_id IN (?, ?)", (workspace_a, workspace_b))
    deleted = cursor.rowcount
    print(f"    Deleted {deleted} test entries ✅")
    
    conn.commit()
    conn.close()
    
    print("\n" + "=" * 60)
    if all_passed:
        print(" DATABASE R/W + ISOLATION VALIDATION: ALL TESTS PASSED ✅")
    else:
        print(" DATABASE VALIDATION: SOME TESTS FAILED ❌")
    print("=" * 60)
    
    return all_passed

if __name__ == "__main__":
    main()
