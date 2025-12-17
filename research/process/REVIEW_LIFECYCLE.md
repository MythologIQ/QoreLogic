# Q-DNA Review Process

This diagram defines the **Recursive Verification Lifecycle** used by Q-DNA agents.

## Flow

1.  **Drafting (Scrivener):** Agent generates `Solution X`.
2.  **Risk Tagging (Scrivener):** Agent tags Risk (L1/L2/L3).
3.  **The Filter (Sentinel):**
    - _Input:_ `Solution X` + `Risk Grade`.
    - _Check:_ Runs `verify_q-dna_diff` workflow.
    - _Output:_ `PASS` or `FAIL` + `FailureContext`.
4.  **Consensus (Judge):**
    - _Input:_ `Sentinel Result` + `Agent Identity`.
    - _Action:_ Sign Ledger.
    - _Output:_ `Verified Artifact` or `Quarantine Order`.

## Failure Loop (Fail Forward)

If **FAIL**:

- The `FailureContext` is archived in the **Shadow Genome**.
- The Scrivener receives the `FailureContext` as a constraint for the next attempt.
- **Result:** Generation `X+1` is inherently smarter than `X`.
