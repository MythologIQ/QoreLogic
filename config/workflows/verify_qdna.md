---
description: Run the Q-DNA Sentinel Audit Workflow
---

# Q-DNA Verification Workflow

This workflow triggers the Sentinel Engine to audit a specific artifact (Code or Text) against the AAC v1.1 standards.

## 1. Preparation

1.  **Identify Artifact:** Determine if the input is `CODE_DIFF` or `CLAIM`.
2.  **Assess Risk:** Assign provisional Risk Grade (L1/L2/L3).

## 2. Sentinel Execution (The "Consensus Loop")

Execute the following step to run the audit simulation:

```bash
python g:/MythologIQ/Q-DNA/Q-DNA/audit_runner.py
```

_Note: In production, this would accept arguments like `--file path/to/code.py`._

## 3. Verdict Interpretation

- **PASS:** Proceed with commit/merge.
- **FAIL:**
  - **Honest Error:** Retry with provided rationale coaching.
  - **Manipulation:** Halt execution. Quaratine agent.

## 4. Ledger Commit

Ensure the final verdict is logged to `qdna_soa_ledger.db` (The script handles this automatically).
