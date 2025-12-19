---
description: Verify QoreLogic Compliance via MCP
---

# QoreLogic Verification Workflow (MCP)

This workflow triggers the **Sovereign Gatekeeper** via the Model Context Protocol.

## 1. Tool Call

The Agent invokes the `audit_code_artifact` tool provided by the QoreLogic MCP Server.

## 2. Process

1.  **Context**: The Agent reads the active file.
2.  **Request**: `audit_code_artifact(path, content)`
3.  **Process**:
    - Sentinel checks static safety.
    - Sentinel checks logic (BMC).
    - Judge signs and logs verdict.
4.  **Response**: Returns `{verdict, rationale, ledger_hash}`.

## 3. Action

- **PASS:** Proceed.
- **FAIL:** Reject change.
- **L3:** Halt and ask user for `request_overseer_approval`.
