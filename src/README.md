# QoreLogic Source Code Structure

This directory contains the reference implementation for the **QoreLogic Code DNA Engine**.

## Directory Layout

- **`agents/`**: Contains the logic/configuration for the three primary agent roles.
  - **`scrivener/`**: The Participant Agent (Code Generator).
    - Responsible for `Implementation Plans` and `Code Diffs`.
  - **`sentinel/`**: The Audit Agent (HRM Micro-Model).
    - Contains the `formal_verification` scripts and `citation_checker` logic.
  - **`judge/`**: The Enforcement Agent.
    - Manages the `SOA Ledger` and `MCP` server state.

## Getting Started

1.  Review the **QoreLogic Specification** in `../docs/QoreLogic_SPECIFICATION.md`.
2.  Configure your workspace rules in `../config/rules`.
3.  Deploy the Judge MCP server (Implementation TBD).
