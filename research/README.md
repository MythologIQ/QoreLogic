# QoreLogic Research Laboratory

This directory contains the active research artifacts, data tables, and study protocols for the QoreLogic project.

## Directory Structure

### 1. `studies/` (Active Protocols)

Formal definitions of the ongoing research investigations.

- `STUDY_001_SENTINEL.md`: Formal Verification viability.
- `STUDY_002_JUDGE_MCP.md`: MCP Enforcement architecture.
- `STUDY_003_EFFICIENCY.md`: HRM vs. CoT cost analysis.

### 2. `data/` (The Atlas)

Raw data, benchmarks, and reference tables.

## Research Philosophy

QoreLogic is not an AI assistant, nor a CI tool. It is a **Governance Substrate** for autonomous software creation.

### From Safety to Certainty

1.  **Architecture vs Policy:** Policies constrain intent ("Don't be bad"). Architecture constrains possibility ("You cannot commit unproven code").
2.  **Epistemic Escalation:** We do not "catch bugs" (defensive). We escalate artifacts from **Level 0 (Unverified)** to **Level 5 (Attested)** through rigorous proof.
3.  **Fail Forward:** We deliberately construct future impossibilities by converting observed failures into permanent structural constraints (The Shadow Genome).

## Launch Instructions (E2E Testing)

### Option 1: Automated Launch (Recommended)

Run the batch launcher from the root directory. This handles dependencies, builds the frontend, and boots the environment.

```powershell
.\Launch_QoreLogic.bat
```

Once running, the launcher will map the host and container ports automatically.

### Option 2: Manual Development Launch

**Prerequisite:** Ensure Docker is running.

1.  **Start the Local Fortress (Backend):**

    ```powershell
    # Terminal 1
    cd local_fortress
    python mcp_server/server.py
    ```

2.  **Start the Dashboard (Frontend):**

    ```powershell
    # Terminal 2
    cd dashboard/frontend
    npm run dev
    ```

3.  **Access the Governance Console:**
    Open [http://localhost:5173](http://localhost:5173) in your browser.

4.  **Verify the Pipeline:**
    - Navigate to **Identity Fortress** to see Agent Trust Scores.
    - Check **Sovereign Ledger** to view real-time verification events (Level 0-5).
