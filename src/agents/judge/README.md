# Judge Agent (The Enforcement)

**Role:** Policy Enforcer & Ledger Keeper
**Architecture:** Model Context Protocol (MCP) Server
**Persistence:** SQLite / Firestore (SOA Ledger)

## Responsibilities

1.  **Manage Identity:** Issue and verify Agent Keys.
2.  **Maintain SOA Ledger:** Append-only log of all `PASS/FAIL` decisions.
3.  **Enforce Penalties:** Apply Influence Weight reductions via MCP context updates.
4.  **Divergence Doctrine:** Handle L3 escalations to the Overseer.

## Sub-Components

- `ledger.db`: The immutable history.
- `policy_engine/`: Logic for resolving grade disputes.
