import sqlite3
import shutil
import os
import time
from pathlib import Path

ORIG = Path("local_fortress/ledger/qorelogic_soa_ledger.db")
TEMP = Path("local_fortress/ledger/qorelogic_soa_ledger_temp.db")

def fix():
    print(f"Copying {ORIG} to {TEMP}...")
    try:
        shutil.copy2(ORIG, TEMP)
    except Exception as e:
        print(f"Copy failed: {e}")
        return

    print("Altering temp DB...")
    conn = sqlite3.connect(TEMP)
    try:
        # Check if exists first to avoid error
        cursor = conn.execute("PRAGMA table_info(agent_registry)")
        cols = [row[1] for row in cursor.fetchall()]
        if "trust_stage" in cols:
             print("trust_stage already exists in copy.")
        else:
             conn.execute("ALTER TABLE agent_registry ADD COLUMN trust_stage TEXT DEFAULT 'CBT' CHECK(trust_stage IN ('CBT', 'KBT', 'IBT'))")
             conn.commit()
             print("Column added to temp.")
    except Exception as e:
        print(f"Error altering: {e}")
        conn.close()
        return
    finally:
        conn.close()
        
    print("Swapping DBs...")
    try:
        os.replace(TEMP, ORIG)
        print("Swap success!")
    except OSError as e:
        print(f"Swap failed (File Locked?): {e}")
        
if __name__ == "__main__":
    fix()
