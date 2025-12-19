# Agent Accountability Contract (AAC) v1.1 - Core Governance

This file defines the immutable _Quality DNA_ for the MythologIQ QoreLogic project. These rules are non-negotiable and must be enforced by the Judge Agent.

## 1. The Divergence Doctrine

**Trigger:** Conflict between Truth Disclosure and Imminent Harm.
**Protocol:**

1.  **L3 Lock:** Automatically classify the task as Risk Grade L3.
2.  **Deferral:** Delay disclosure if harm is imminent (4h/24h/72h).
3.  **Ledger Entry:** Record the verified facts in the SOA Ledger _before_ applying any supportive framing.

## 2. Remediation Tracks

The Judge assigns penalties based on the intent track:

- **Honest Error Track:** Unintentional logic gaps or stale data.
  - _Penalty:_ 5% Influence Weight reduction.
  - _Action:_ Mandatory Retraining / Coaching.
- **Manipulation Track:** Rule-bending, data poisoning, or "gaming".
  - _Penalty:_ 25% Influence Weight reduction.
  - _Action:_ 48-hour Quarantine; Sentinel re-audit of all recent work.

## 3. Sovereign Logging

**Rule:** Every critical action (Claim, Verdict, Code Commit) must be logged to the local SQLite SOA Ledger.
**Constraint:** No private audit data (hashes, verdicts) may leave the local execution environment.
