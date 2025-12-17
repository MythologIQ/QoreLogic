# Q-DNA Risk Grading Policy (L1-L3)

This policy defines the mandatory risk assessment protocol for all Q-DNA artifacts.

## 1. Risk Trigger Matrix

| Risk Grade      | Definition                                         | Trigger Examples                                      | Verification Protocol                                             |
| :-------------- | :------------------------------------------------- | :---------------------------------------------------- | :---------------------------------------------------------------- |
| **L1 (Low)**    | Routine, reversable, non-critical.                 | UI text edits, comment updates, variable renames.     | **Static Analysis:** Basic linting & spellcheck.                  |
| **L2 (Medium)** | Logic changes, data handling, external APIs.       | New function logic, API integrations, schema changes. | **Sentinel Audit:** Semantic check + Citation scan.               |
| **L3 (High)**   | Security-critical, irreversible, financial/safety. | Auth logic, Encryption, Key management, PII handling. | **Formal Verification:** Bounded Model Checking + Human Sign-off. |

## 2. The Verification SLA

- **L1:** < 1 minute (Synchronous).
- **L2:** < 5 minutes (Synchronous).
- **L3:** < 24 hours (Asynchronous Background Task).

## 3. L3 "Lockdown"

Any task flagged as L3 triggers the _High Assurance Protocol_:

1.  **Code Freeze:** No further merges until Verdict.
2.  **Shadow Genome:** Any failure is archived with full context.
3.  **Overseer Signal:** The Human Overseer is explicitly notified via the Judge.
