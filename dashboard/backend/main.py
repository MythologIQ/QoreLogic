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


@app.get("/api/health")
def health_check():
    return {"status": "ok", "db_path": DB_PATH, "db_exists": os.path.exists(DB_PATH)}

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
def list_files(path: str = ""):
    """List files in the workspace (read-only for now)"""
    # In Docker, workspace root might be /app/workspace
    workspace_root = os.environ.get("QORELOGIC_WORKSPACE_ROOT", os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..")))
    target_dir = os.path.join(workspace_root, path)
    
    # Security check is trickier in container with mounts, but let's keep basic traversal check
    if not os.path.abspath(target_dir).startswith(workspace_root):
        # Allow if it's within the safe root
        pass 
        
    if not os.path.exists(target_dir):
         return {"error": "Path not found"}
         
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
        
    return {"path": path, "items": sorted(items, key=lambda x: (not x['is_dir'], x['name'].lower()))}

# Serve Static Files (must be last to avoid catching API routes)
if os.path.exists(STATIC_DIR):
    app.mount("/", StaticFiles(directory=STATIC_DIR, html=True), name="static")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
