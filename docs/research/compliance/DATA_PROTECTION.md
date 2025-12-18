# Data Protection Research Document

**Version:** 1.0  
**Created:** December 18, 2025  
**Status:** Complete  
**Purpose:** Tripartite Governance (GDPR, CCPA/CPRA, HIPAA) in AI systems  
**Cross-Reference:** Q-DNA Spec §10 (Privacy), §10.2 (Data Sovereignty)

---

## 1. Executive Summary

Q-DNA operates at the intersection of GDPR, CCPA/CPRA, and HIPAA. Compliance requires a "Privacy by Design" re-architecture addressing the "Tripartite Governance Challenge." This document specifies technical requirements for managing Automated Decision-Making (ADM), cross-border transfers (Schrems II), and the inherent re-identification risks of high-dimensional AI models.

**Key Claims Substantiated:**

| Claim                                            | Evidence                                                   |
| ------------------------------------------------ | ---------------------------------------------------------- |
| Vector embeddings qualify as personal data       | GDPR "Singling Out" principle + Mosaic Effect              |
| Inferences are regulated as Personal Information | CCPA/CPRA explicit inclusion of inferred profiles          |
| Safe Harbor is insufficient for high-utility AI  | HIPAA Expert Determination requirement for dates/geography |
| Human-in-the-Loop (HITL) is legally mandatory    | GDPR Art. 22 + CPRA ADMT Opt-Out requirements              |

---

## 2. Redefining Personal Information

### 2.1 GDPR: Vector Identifiability

- **Singling Out:** High-dimensional vectors (embeddings) act as unique fingerprints. If they allow distinguishing an individual, they are Personal Data.
- **Pseudonymization vs. Anonymization:** Pseudonymization is a security measure, not an exemption. Irreversible anonymization is the only path out of scope.

### 2.2 CCPA/CPRA: The Power of Inference

- **Inferred Profiles:** Predicting preferences (intelligence, behavior, etc.) creates Personal Information.
- **Rights:** Triggers "Right to Know" (exporting scores) and "Right to Delete" (requiring Machine Unlearning).
- **Household Data:** Extends to information reasonably linked to a group/household.

### 2.3 HIPAA: Mosaic Effect Re-identification

- **Expert Determination:** Mandatory for AI utility. Requires statistical proof of "very small" re-identification risk.
- **Linkage Attacks:** AI can cross-reference "de-identified" data with public sets to re-identify patients.

---

## 3. Automated Decision-Making (ADM)

### 3.1 Meaningful Human Intervention (MHI)

To bypass the "solely automated" prohibition (GDPR Art. 22), human reviews must be:

- **Substantive:** Authority to overturn the decision.
- **Competent:** Ability to evaluate the reasoning (requires Explainable AI).
- **Active:** Avoiding "automation bias" (rubber-stamping).

### 3.2 System Architectures

- **HITL (Human-in-the-Loop):** Intervention in every decision (Mandatory for high-stakes).
- **HOTL (Human-on-the-Loop):** Monitoring and design oversight.
- **Opt-Out Flux:** CPRA requirement for a bifurcated workflow allowing users to bypass ADMT.

---

## 4. Minimization and Machine Unlearning

### 4.1 The Training Paradox

- **Feature Selection:** Minimize proxies that correlate with protected classes (race, gender).
- **Synthetic Data:** Generating artificial sets to break the link to original purpose constraints.

### 4.2 Machine Unlearning (Right to Erasure)

Deleting a database record is insufficient if gradients are embedded in model weights.

- **SISA Architecture:** Sharded, Isolated, Sliced, Aggregated training to allow localized retraining on deletion requests.

---

## 5. Cross-Border Data Transfers (Schrems II)

### 5.1 Technical Supplemental Measures

- **Encryption:** Keys must be held outside "Third Countries" (e.g., EU-only keys).
- **Confidential Computing:** Processing in TEEs (Trusted Execution Environments) to hide data from cloud providers.

### 5.2 Local-First / Edge AI

- **Data Sovereignty:** Moving models to the data (device-level inference).
- **Federated Learning:** Only gradients transfer; raw data remains local.

---

## 6. Security as Data Protection

### 6.1 Model Inversion as a Breach

If an attacker reconstructs training data via specialized queries, it is a **Loss of Confidentiality**.

- **72-Hour Clock:** Triggered upon detection of an Inversion Attack.
- **Mitigation:** DP-SGD (Differential Privacy Stochastic Gradient Descent) to bound privacy loss.

---

## 7. Audit and Accountability

### 7.1 Glass Box Architecture

- **Lineage Tracking:** Map dataset versions to model binaries.
- **Bias Auditing:** Regular tests for disparate impact against protected classes.
- **Inference Logs:** Log input, model version, score, and human reviewer ID.

---

## References

[DATA-001] GDPR Articles 5, 6, 17, 22, 32, 33.  
[DATA-002] California Privacy Rights Act (CPRA) 2020.  
[DATA-003] HIPAA Privacy Rule & Security Rule (45 CFR).  
[DATA-004] CJEU Case C-311/18 (Schrems II).  
[DATA-005] EDPB Guidelines on Automated Decision-Making and Profiling.  
[DATA-006] NIST AI Risk Management Framework 1.0.  
[DATA-007] OCR Guidance on De-identification of PHI.
