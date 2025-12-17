# Sentinel Agent (The Audit)

**Role:** Quality Gate & Formal Verifier
**Model:** HRM Micro-Model (e.g., 27M Parameter Recurrent Network)
**Latency Target:** < 500ms for L2 checks.

## Responsibilities

1.  **Formal Verification:** specific safety checks on Code Diffs.
2.  **Citation Auditing:** Verify Transitive Cap and Quote Context.
3.  **Complexity Analysis:** Enforce `quality_dna.md` complexity limits.

## Tools

- `cbmc` (C Bounded Model Checker)
- `esbmc` (Python/C++ Verifier)
- `hash_validator` (Internal script)
