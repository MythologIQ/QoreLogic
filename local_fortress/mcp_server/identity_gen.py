import os
import json
import secrets
import sqlite3

# Configuration
DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'ledger', 'qdna_soa_ledger.db')

def generate_did(role):
    """Generate a Decentralized Identifier based on role and randomness."""
    random_suffix = secrets.token_hex(4)
    return f"did:myth:{role.lower()}:{random_suffix}"

def generate_keypair():
    """
    Simulate Keypair Generation.
    In a full production implementation, use 'cryptography' or 'nacl' libs.
    For this 'Lean Mode' prototype, we generate hex tokens to represent keys.
    """
    private_key = secrets.token_hex(32)
    public_key = secrets.token_hex(32) # In reality, derived from private
    return public_key, private_key

def register_agent(role, weight=1.0):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    did = generate_did(role)
    pub, priv = generate_keypair()

    print(f"Registering Agent: {role}...")
    
    try:
        cursor.execute("""
            INSERT INTO agent_registry (did, public_key, role, influence_weight)
            VALUES (?, ?, ?, ?)
        """, (did, pub, role, weight))
        conn.commit()
        
        # Save credentials locally (Securely in production, JSON here for prototype)
        creds = {
            "did": did,
            "role": role,
            "public_key": pub,
            "private_key": priv # NEVER SHARE THIS
        }
        
        filename = f"{role.lower()}_creds.json"
        with open(filename, 'w') as f:
            json.dump(creds, f, indent=4)
            
        print(f"✅ Registered {did}. Credentials saved to {filename}")
        
    except sqlite3.Error as e:
        print(f"❌ Database error: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    # Create the Trinity
    if not os.path.exists(DB_PATH):
        print("❌ Ledger DB not found. Run myth_soa_init.py first.")
    else:
        register_agent("Scrivener", weight=1.0)
        register_agent("Sentinel", weight=1.2) # Higher weight for Audit
        register_agent("Judge", weight=1.5)    # Highest weight for Enforcement
