import sqlite3
from pathlib import Path

DB_PATH = Path("local_fortress/ledger/qorelogic_soa_ledger.db")
SCHEMA_PATH = Path("local_fortress/ledger/schema.sql")

def update_schema():
    print(f"Updating schema for {DB_PATH} using {SCHEMA_PATH}")
    
    with open(SCHEMA_PATH, 'r') as f:
        schema = f.read()
    
    conn = sqlite3.connect(DB_PATH)
    try:
        conn.executescript(schema)
        conn.commit()
        print("Schema updated successfully.")
    except Exception as e:
        print(f"Error updating schema: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    update_schema()
