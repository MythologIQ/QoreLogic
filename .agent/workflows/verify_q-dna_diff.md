---
description: Verification Workflow for QoreLogic Code Diffs
---

# Verify QoreLogic Diff

**Trigger:** Scrivener Agent submits a `Code Diff Artifact`.

## Workflow Steps

1.  **Risk Assessment (Scrivener -> Judge)**

    - Read the `RiskRationale` from the Artifact.
    - If Grade is **L3**, lock the artifact from immediate write.

2.  **Sentinel Challenge (Sentinel Agent)**

    - **Complexity Check:** Verify Cyclomatic Complexity < Threshold.
    - **Citation Check:** Verify Transitive Cap <= 2.
    - **Formal Verification:** Run `cbmc` or `esbmc` on the diff (if configured).
    - **Output:** `PASS` or `FAIL`.

3.  **Consensus (Judge Agent)**

    - **PASS:** Sign artifact with Judge Key. Update SOA Ledger. Status -> `Verified`.
    - **FAIL:** Apply penalty (Manifestation Track). Status -> `Quarantined`.

4.  **Final Write (System)**
    - If `Verified`: Write code to workspace.
    - If `Quarantined`: Reject write, notify Overseer.
