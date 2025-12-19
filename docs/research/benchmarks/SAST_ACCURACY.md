# Static Application Security Testing (SAST) Accuracy

**Version:** 1.0  
**Created:** December 18, 2025  
**Status:** Complete  
**Purpose:** Evaluation of SAST error rates and AI-driven precision improvements  
**Cross-Reference:** QoreLogic Spec §4 (Security), §9 (ML-Dependent Verification)

---

## 1. Executive Summary

Static Application Security Testing (SAST) faces a "False Positive Paradox": the necessity of over-approximation to ensure safety generates a deluge of non-actionable alerts. In 2024–2025, enterprise SAST solutions frequently exhibit **false positive rates (FPR) of 36% to 80%**, leading to "alert fatigue" and tool abandonment.

This document analyzes the shift toward a **"Filter-and-Verify" architecture**, where traditional deterministic engines act as "candidate generators" and LLM-based verifiers reduce false alarms by over 90%.

**Key Claims Substantiated:**

| Claim                                                        | Evidence                                                      |
| ------------------------------------------------------------ | ------------------------------------------------------------- |
| Enterprise Java apps reach peak FPR of 78%                   | NIST studies 2024                                             |
| AI-native detection significantly outperforms legacy SAST    | Wild-vulnerability benchmarking (DryRun Security vs. Semgrep) |
| "Filter-and-Verify" reduces triage burden by >90%            | ZeroFalse framework (F1-score 0.955)                          |
| 5-second latency is the threshold for pre-commit abandonment | Developer productivity research                               |

---

## 2. The Theoretical Crisis: Over-Approximation

### 2.1 The Deterministic Dilemma

SAST engines must battle the Halting Problem. Lacking runtime state, they must choose:

- **Under-approximate:** Risk False Negatives (unacceptable).
- **Over-approximate:** Create False Positives (noise).

### 2.2 Operational Impact of Noise

| Metric            | Value      | Impact                                         |
| ----------------- | ---------- | ---------------------------------------------- |
| **Peak Java FPR** | 78%        | 4 out of 5 alerts are invalid                  |
| **Triage Time**   | 15–30 mins | Human investigation cost per finding           |
| **Adoption Gap**  | 41%        | First-party flaws unremediated after 12 months |

**Psychology:** 62% of security leads prefer reducing false positives over finding more "true" positives. Precision is now more valuable than sensitivity.

---

## 3. Landscape of Accuracy (2024-2025)

### 3.1 OWASP Benchmark Results

A synthetic 2,740-case test application (50/50 TP/FP split).

- **Fluid Attacks:** Perfect score (potentially overfit).
- **SonarQube:** ~1% FPR (prefers silence over error).

### 3.2 Real-World ("Wild") Performance

| Tool                     | Detection Rate | Logic Flaw Detection |
| ------------------------ | -------------- | -------------------- |
| **AI-Native (DryRun)**   | **88%**        | High (Context-aware) |
| **Rule-Based (Semgrep)** | 46%            | Low (Pattern-based)  |
| **Legacy SAST**          | < 50%          | Very Low             |

---

## 4. Pathology of False Positives

1. **Sanitization Blindness:** Tools fail to recognize "custom" cleansers outside standard libraries.
2. **Contextual Reachability:** Flagging "vulnerabilities" in dead code or development-only blocks.
3. **Configuration Mismatch:** In Python, the "civil war" between Pylint (opinionated) and Mypy (type-strict) creates conflicting "error" signals.

**Solution:** Ecosystem unification via `pyproject.toml` and Rust-based tools like **Ruff** for consistent enforcement.

---

## 5. The "Filter-and-Verify" Architecture

### 5.1 Mechanics

1. **Candidate Generation:** SAST engine runs in high-sensitivity mode.
2. **Contextualization:** System extracts data flow + intermediate function code.
3. **LLM Verification:** A reasoning-oriented model (GPT-5 class) adjudicates the path.

### 5.2 Academic Validation (ZeroFalse & IRIS)

- **F1-Score 0.955:** Achieved via **CWE-Specialized Prompting** (evaluating specific criteria like integer casting or parameterization).
- **Path Filtering:** 5 out of 8 false positives correctly removed from CodeQL traces using LLM filters.

---

## 6. Operationalizing Accuracy: Latency

Accuracy matters only if it fits the developer's window.

| Stage          | Trigger    | Latency Target  | Tool Strategy          |
| -------------- | ---------- | --------------- | ---------------------- |
| **IDE**        | Save       | < 200 ms        | Linters (Ruff/LSP)     |
| **Pre-Commit** | git commit | **< 5 seconds** | Fast SAST (No LLM)     |
| **CI / PR**    | Push       | < 15 minutes    | Deep SAST + LLM Verify |

---

## 7. Future Directions

- **Agentic Remediation:** AI agents generating Pull Requests to fix identified (verified) true positives.
- **Hybrid Intelligence:** Combining the mathematical coverage of CodeQL-style rules with the semantic reasoning of LLMs.
- **Risk:** LLM hallucinations (misunderstanding a library function) necessitate that humans remain the final approvers.

---

## References

[SAST-001] NIST ITL Bulletin (2024). "Source Code Analysis Tools."  
[SAST-002] OWASP Benchmark Project v1.2.  
[SAST-003] Finite State (2024). "The State of AppSec Noise."  
[SAST-004] ZeroFalse Framework (2025). "Reducing SAST FPR via Specialized LLM Prompting."  
[SAST-005] Datadog Bits AI Case Study. "Contextual Security Evaluation."  
[SAST-006] Ruff/PEP 518 Documentation. Python Ecosystem Consolidation.  
[SAST-007] Meta Engineering (2023). "Nullsafe: Scaling Static Analysis at Meta."
