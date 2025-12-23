from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import sqlite3
import os
import json
import logging
import time

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("DashboardAPI")

app = FastAPI()

# Enable CORS for local dev
# We use regex to allow any localhost port (Launcher might shift if 5500 is taken)
origin_regex = r"http://(localhost|127\.0\.0\.1)(:\d+)?"

app.add_middleware(
    CORSMiddleware,
    allow_origin_regex=origin_regex, 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Multi-Workspace Configuration
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
# We use the persistent QoreLogic home for the registry
QORELOGIC_HOME = os.environ.get("QORELOGIC_HOME", "/app/ledger") 
if not os.path.exists(QORELOGIC_HOME):
    try:
        os.makedirs(QORELOGIC_HOME, exist_ok=True)
    except:
        pass

WORKSPACE_REGISTRY_PATH = os.path.join(QORELOGIC_HOME, "workspaces.json")
STATIC_DIR = os.environ.get("QORELOGIC_STATIC_DIR", "/app/dashboard/dist")
DB_PATH = os.environ.get("QORELOGIC_DB_PATH", os.path.join(BASE_DIR, "default_ledger.db"))

class WorkspaceManager:
    def __init__(self):
        self._ensure_registry()
        
    def _ensure_registry(self):
        if not os.path.exists(WORKSPACE_REGISTRY_PATH):
            with open(WORKSPACE_REGISTRY_PATH, 'w') as f:
                json.dump({"active": None, "workspaces": {}}, f)
                
    def get_registry(self):
        with open(WORKSPACE_REGISTRY_PATH, 'r') as f:
            return json.load(f)
            
    def save_registry(self, data):
        with open(WORKSPACE_REGISTRY_PATH, 'w') as f:
            json.dump(data, f, indent=2)

    def register_workspace(self, name, path, env_type="standard"):
        data = self.get_registry()
        # Generate a simple ID
        ws_id = name.lower().replace(" ", "-")
        
        # In Docker, we might not have access to the actual 'path' unless mounted.
        # But we can store the metadata for reporting.
        # We assume each workspace has its own DB in QORELOGIC_HOME/dbs/<ws_id>.db
        # OR they share the main DB with a 'project_id' column. 
        # Let's go with separate DBs for isolation.
        
        data["workspaces"][ws_id] = {
            "id": ws_id,
            "name": name,
            "path": path, # Host path for reference
            "env_type": env_type,
            "id": ws_id,
            "name": name,
            "path": path, # Host path for reference
            "env_type": env_type,
            "created_at": str(time.time())
        }
        
        # If no active workspace, set this one
        if not data["active"]:
            data["active"] = ws_id
            
        self.save_registry(data)
        return data["workspaces"][ws_id]

    def get_active_workspace(self):
        data = self.get_registry()
        if not data["active"]: 
            return None
        return data["workspaces"].get(data["active"])

ws_manager = WorkspaceManager()

# Helper to get DB connection (Single DB Architecture)
def get_db_connection():
    # Use the global QORELOGIC_DB_PATH
    if not DB_PATH:
        raise ValueError("No global database path configured")
        
    # Auto-init DB directory if missing
    db_dir = os.path.dirname(DB_PATH)
    if not os.path.exists(db_dir):
        os.makedirs(db_dir, exist_ok=True)
        
# Connect to the SINGLE shared ledger
    return sqlite3.connect(DB_PATH)

def init_db_schema():
    """Initialize DB schema if tables are missing."""
    # Resolve path relative to this file (in /qorelogic_system/dashboard/backend)
    # Target: /qorelogic_system/local_fortress/ledger/schema.sql
    schema_path = os.path.join(BASE_DIR, "..", "..", "local_fortress", "ledger", "schema.sql")
    
    # If redundant check needed for different mount structure
    if not os.path.exists(schema_path):
        # Try local dev path
        schema_path = os.path.join(BASE_DIR, "..", "..", "local_fortress", "ledger", "schema.sql")
    
    if not os.path.exists(schema_path):
        logger.warning(f"Schema SQL not found at {schema_path}. DB Init skipped.")
        return

    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Check if master table exists
        cursor.execute("SELECT count(*) FROM sqlite_master WHERE type='table' AND name='soa_ledger'")
        if cursor.fetchone()[0] == 0:
            logger.info(f"Applying schema from {schema_path}...")
            with open(schema_path, 'r') as f:
                schema_sql = f.read()
                cursor.executescript(schema_sql)
            conn.commit()
            logger.info("✅ Database schema initialized successfully.")
        else:
            logger.info("Database schema already exists.")
            
    except Exception as e:
        logger.error(f"❌ Failed to initialize database: {e}")
    finally:
        if 'conn' in locals():
            conn.close()

@app.on_event("startup")
async def startup_event():
    init_db_schema()


@app.get("/api/health")
def health_check():
    return {"status": "ok", "db_path": DB_PATH, "db_exists": os.path.exists(DB_PATH)}

# ============================================================================
# AGENT CONFIGURATION API
# ============================================================================
AGENT_CONFIG_PATH = os.path.join(QORELOGIC_HOME, "config", "agents.json")

def ensure_agent_config_dir():
    """Ensure the agent config directory exists."""
    config_dir = os.path.dirname(AGENT_CONFIG_PATH)
    if not os.path.exists(config_dir):
        os.makedirs(config_dir, exist_ok=True)

@app.get("/api/agents/config")
def get_agent_config():
    """Load agent configuration from persistent storage."""
    ensure_agent_config_dir()
    if os.path.exists(AGENT_CONFIG_PATH):
        try:
            with open(AGENT_CONFIG_PATH, 'r', encoding='utf-8') as f:
                return {"status": "ok", "config": json.load(f)}
        except Exception as e:
            logger.warning(f"Failed to load agent config: {e}")
            return {"status": "error", "error": str(e)}
    # Return defaults if no config file exists
    return {
        "status": "ok",
        "config": {
            "provider": "ollama",
            "endpoint": "http://localhost:11434",
            "models": {
                "sentinel": "default",
                "judge": "default", 
                "overseer": "default",
                "scrivener": "default"
            },
            "prompts": {
                "sentinel": "You are SENTINEL, a security-focused code auditor.",
                "judge": "You are JUDGE, the final arbiter of code compliance.",
                "overseer": "You are OVERSEER, a project manager and strategist.",
                "scrivener": "You are SCRIVENER, the technical documentation engine."
            },
            "agents": {}
        }
    }

@app.post("/api/agents/config")
def save_agent_config(data: dict):
    """Save agent configuration to persistent storage."""
    ensure_agent_config_dir()
    try:
        with open(AGENT_CONFIG_PATH, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)
        logger.info(f"Agent config saved to {AGENT_CONFIG_PATH}")
        return {"status": "ok", "path": AGENT_CONFIG_PATH}
    except Exception as e:
        logger.error(f"Failed to save agent config: {e}")
        return {"status": "error", "error": str(e)}

@app.get("/api/workspaces")
def list_workspaces():
    return ws_manager.get_registry()

@app.post("/api/workspaces")
def create_workspace(data: dict):
    # Expects {name, path, env_type}
    return ws_manager.register_workspace(data["name"], data["path"], data.get("env_type", "standard"))

@app.post("/api/workspaces/activate")
def activate_workspace(data: dict):
    reg = ws_manager.get_registry()
    if data["id"] in reg["workspaces"]:
        reg["active"] = data["id"]
        ws_manager.save_registry(reg)
        return {"status": "ok", "active": data["id"]}
    return {"error": "Workspace not found"}

@app.post("/api/workspaces/deactivate")
def deactivate_workspace():
    """Clear the active workspace, returning user to selector."""
    reg = ws_manager.get_registry()
    reg["active"] = None
    ws_manager.save_registry(reg)
    return {"status": "ok", "active": None}

@app.delete("/api/workspaces/{ws_id}")
def delete_workspace(ws_id: str):
    """Remove a workspace from the registry (doesn't delete files on disk)."""
    reg = ws_manager.get_registry()
    if ws_id in reg.get("workspaces", {}):
        del reg["workspaces"][ws_id]
        # If this was the active workspace, clear it
        if reg.get("active") == ws_id:
            reg["active"] = None
        ws_manager.save_registry(reg)
        return {"status": "ok", "deleted": ws_id}
    return {"error": "Workspace not found"}

@app.get("/api/status")
def get_status(ws_id: str = None):
    try:
        conn = get_db_connection()
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # System State (GLOBAL)
        try:
            cursor.execute("SELECT * FROM system_state WHERE state_id = 1")
            row = cursor.fetchone()
            state = dict(row) if row else {"current_mode": "UNKNOWN"}
        except:
            state = {"current_mode": "Allocating..."}
        
        # Ledger Count (SCOPED to Workspace if provided)
        try:
            if ws_id:
                cursor.execute("SELECT COUNT(*) FROM soa_ledger WHERE workspace_id = ?", (ws_id,))
            else:
                cursor.execute("SELECT COUNT(*) FROM soa_ledger")
            state["total_ledger_entries"] = cursor.fetchone()[0]
        except:
            state["total_ledger_entries"] = 0
            
        return state
    except Exception as e:
        logger.error(f"Error fetching status: {e}")
        return {"error": str(e), "current_mode": "OFFLINE"}

@app.get("/api/ledger")
def get_ledger(limit: int = 50, ws_id: str = None):
    try:
        conn = get_db_connection()
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        query = "SELECT * FROM soa_ledger"
        params = []
        
        if ws_id:
            query += " WHERE workspace_id = ?"
            params.append(ws_id)
            
        query += " ORDER BY entry_id DESC LIMIT ?"
        params.append(limit)
        
        cursor.execute(query, tuple(params))
        rows = cursor.fetchall()
        return [dict(row) for row in rows]
    except Exception as e:
        logger.error(f"Error fetching ledger: {e}")
        return []

@app.get("/api/files")
def list_files(path: str = "", ws_id: str = None):
    """List files in the workspace (scoped to active workspace if ws_id provided)"""
    
    # Default workspace root
    default_root = os.environ.get("QORELOGIC_WORKSPACE_ROOT", "/src")
    workspace_root = default_root
    
    # Determine the workspace root based on ws_id
    if ws_id:
        reg = ws_manager.get_registry()
        ws = reg.get("workspaces", {}).get(ws_id)
        if ws and ws.get("path"):
            stored_path = ws["path"]
            
            # The stored_path is a host path (like G:\MythologIQ\Project)
            # Inside Docker, /src is mounted to the host project root
            # We need to find where this workspace actually lives
            
            # Check if it's a Windows-style path
            if "\\" in stored_path or (len(stored_path) > 1 and stored_path[1] == ":"):
                # Extract the directory name from the Windows path
                dir_name = os.path.basename(stored_path.rstrip("\\/"))
                potential_path = os.path.join("/src", dir_name)
                
                if os.path.exists(potential_path):
                    workspace_root = potential_path
                else:
                    # Maybe the workspace IS the /src mount itself
                    workspace_root = default_root
            elif stored_path.startswith("/"):
                # It's already a Unix path - use it if it exists
                if os.path.exists(stored_path):
                    workspace_root = stored_path
                else:
                    # Try it as relative to /src
                    potential_path = os.path.join("/src", stored_path.lstrip("/"))
                    if os.path.exists(potential_path):
                        workspace_root = potential_path
            else:
                # Relative path - join with /src
                workspace_root = os.path.join(default_root, stored_path)
    
    target_dir = os.path.join(workspace_root, path)
    
    # Normalize to prevent traversal  
    target_dir = os.path.abspath(target_dir)
    workspace_root = os.path.abspath(workspace_root)
    
    if not target_dir.startswith(workspace_root):
        return {"error": "Access denied - path traversal detected"}
        
    if not os.path.exists(target_dir):
         return {"error": f"Path not found", "workspace_root": workspace_root, "items": []}
         
    if os.path.isfile(target_dir):
        return {"type": "file", "name": os.path.basename(target_dir)}
        
    items = []
    try:
        for entry in os.scandir(target_dir):
            items.append({
                "name": entry.name,
                "is_dir": entry.is_dir(),
                "size": entry.stat().st_size if entry.is_file() else 0
            })
    except Exception as e:
        return {"error": str(e)}
        
    return {"path": path, "workspace_root": workspace_root, "items": sorted(items, key=lambda x: (not x['is_dir'], x['name'].lower()))}

# Serve Static Files (must be last to avoid catching API routes)
if os.path.exists(STATIC_DIR):
    app.mount("/", StaticFiles(directory=STATIC_DIR, html=True), name="static")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
