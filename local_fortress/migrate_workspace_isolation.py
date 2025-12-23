"""
QoreLogic Database Migration: Add Workspace Isolation Columns
Version: 2.5 Multi-Tenant Isolation
Date: December 23, 2025

This migration adds workspace_id columns to enable multi-tenant isolation.
"""

import sqlite3
from pathlib import Path
from datetime import datetime

DB_PATH = Path(__file__).parent / "ledger" / "qorelogic_soa_ledger.db"

MIGRATIONS = [
    {
        "table": "soa_ledger",
        "column": "workspace_id",
        "sql": "ALTER TABLE soa_ledger ADD COLUMN workspace_id TEXT DEFAULT 'default'",
        "index": "CREATE INDEX IF NOT EXISTS idx_ledger_workspace ON soa_ledger(workspace_id)"
    },
    {
        "table": "shadow_genome",
        "column": "workspace_id",
        "sql": "ALTER TABLE shadow_genome ADD COLUMN workspace_id TEXT DEFAULT 'default'",
        "index": None
    },
    {
        "table": "l3_approval_queue",
        "column": "workspace_id",
        "sql": "ALTER TABLE l3_approval_queue ADD COLUMN workspace_id TEXT DEFAULT 'default'",
        "index": None
    },
    {
        "table": "trust_updates",
        "column": "workspace_id",
        "sql": "ALTER TABLE trust_updates ADD COLUMN workspace_id TEXT DEFAULT 'default'",
        "index": None
    }
]

def column_exists(cursor, table, column):
    """Check if a column exists in a table."""
    cursor.execute(f"PRAGMA table_info({table})")
    columns = [row[1] for row in cursor.fetchall()]
    return column in columns

def run_migrations():
    print("=" * 60)
    print(" QORELOGIC DATABASE MIGRATION")
    print(" Adding Multi-Tenant Isolation (workspace_id)")
    print("=" * 60)
    print(f"\nDatabase: {DB_PATH}")
    print(f"Timestamp: {datetime.now().isoformat()}")
    
    if not DB_PATH.exists():
        print("\n❌ DATABASE NOT FOUND!")
        return False
    
    conn = sqlite3.connect(str(DB_PATH))
    cursor = conn.cursor()
    
    # Backup check
    print("\n[PRE-FLIGHT] Checking current state...")
    
    migrations_applied = 0
    migrations_skipped = 0
    
    for migration in MIGRATIONS:
        table = migration["table"]
        column = migration["column"]
        
        if column_exists(cursor, table, column):
            print(f"  ⏭️  {table}.{column} already exists - SKIP")
            migrations_skipped += 1
        else:
            print(f"  🔧 {table}.{column} missing - APPLYING...")
            try:
                cursor.execute(migration["sql"])
                print(f"      Column added ✅")
                
                if migration.get("index"):
                    cursor.execute(migration["index"])
                    print(f"      Index created ✅")
                
                migrations_applied += 1
            except Exception as e:
                print(f"      FAILED: {e} ❌")
                conn.rollback()
                conn.close()
                return False
    
    conn.commit()
    
    print("\n" + "-" * 40)
    print("[POST-MIGRATION] Verifying columns...")
    
    all_good = True
    for migration in MIGRATIONS:
        table = migration["table"]
        column = migration["column"]
        exists = column_exists(cursor, table, column)
        status = "✅" if exists else "❌"
        print(f"  {table}.{column}: {status}")
        if not exists:
            all_good = False
    
    conn.close()
    
    print("\n" + "=" * 60)
    print(f" MIGRATION COMPLETE")
    print(f" Applied: {migrations_applied} | Skipped: {migrations_skipped}")
    if all_good:
        print(" STATUS: ALL ISOLATION COLUMNS PRESENT ✅")
    else:
        print(" STATUS: SOME COLUMNS MISSING ❌")
    print("=" * 60)
    
    return all_good

if __name__ == "__main__":
    success = run_migrations()
    exit(0 if success else 1)
