# Vulnerability Disclosure Standards Research Document

**Version:** 1.0  
**Created:** December 18, 2025  
**Status:** Complete  
**Purpose:** Coordinated Vulnerability Disclosure (CVD) policy and SLAs  
**Cross-Reference:** Q-DNA Spec §4 (Security), ISO/IEC 29147, ISO/IEC 30111

---

## 1. Executive Summary

The Q-DNA Project adopts **Coordinated Vulnerability Disclosure (CVD)** to minimize the window of exposure. This document defines the "90+30" model, severity-based SLAs, and specific strategies for AI/ML vulnerabilities where traditional patching (recompilation) is replaced by "Layered Remediation" (guardrails + retraining).

**Key Claims Substantiated:**

| Claim                                              | Evidence                                                     |
| -------------------------------------------------- | ------------------------------------------------------------ |
| 90+30 model protects users from n-day exploits     | Standardizes on Google Project Zero + 30-day adoption window |
| AI models require "Layered Remediation"            | retraining cycles (5-7 weeks) exceed 7-day critical SLAs     |
| Safety-critical issues override standard embargoes | CISA/FDA alignment for imminent public harm                  |

---

## 2. Policy Framework

### 2.1 Standard alignment

- **ISO/IEC 29147:2018:** Vulnerability disclosure communications.
- **ISO/IEC 30111:2019:** Internal vulnerability handling processes.
- **NIST AI RMF:** Manageability and transparency for AI flaws.

### 2.2 The "90+30" Model

- **90 Days:** Hard ceiling for the vendor to release a fix (Remediation).
- **30 Days:** Technical details (PoC, exploit write-up) are withheld for 30 days _after_ the fix is released to allow for user adoption and prevent "patch diffing" n-day attacks.

---

## 3. Operational Lifecycle & SLAs

| Phase           | SLA            | Objective                                        |
| --------------- | -------------- | ------------------------------------------------ |
| **Intake**      | 24 Hours       | Confirm receipt, assign Case ID.                 |
| **Triage**      | 7 Days         | Verify vulnerability, assign CVSS/SSVC priority. |
| **Remediation** | Severity-based | Develop and verify the fix.                      |

### Severity-Based Remedition Targets

| Severity     | CVSS Range | Fix Target | Adoption Window |
| ------------ | ---------- | ---------- | --------------- |
| **Critical** | 9.0 - 10.0 | **7 Days** | 0-3 Days        |
| **High**     | 7.0 - 8.9  | 30 Days    | 30 Days         |
| **Medium**   | 4.0 - 6.9  | 90 Days    | 30 Days         |
| **Low**      | 0.1 - 3.9  | 180 Days   | N/A             |

---

## 4. AI/ML Vulnerability Management

AI/ML vulnerabilities (e.g., membership inference, adversarial evasion) cannot be "patched" in 7 days due to retraining physics (5-7 weeks).

### 4.1 Layered Remediation Strategy

1. **Layer 1: Immediate Mitigation (Guardrails)**

   - **Timeline:** 7-14 Days.
   - **Action:** Input filters, output sanitizers, system-prompt updates.
   - **Goal:** Neutralize the attack vector immediately.

2. **Layer 2: Fundamental Remediation (Retraining)**
   - **Timeline:** 90-120 Days.
   - **Action:** Dataset curation, model retraining, safety evaluation.
   - **Goal:** Eliminate the root cause in model weights.

---

## 5. Imminent Public Harm & Safety

Consisent with CISA/FDA guidelines:

- **Nullification:** Standard 90-day embargo is nullified if a vulnerability poses an immediate threat to physical safety or critical infrastructure.
- **Emergency Disclosure:** Release "Protective Disclosure" (mitigation steps) within hours.
- **Operational Deferral:** Potential 4-hour delay of public release to allow hospital/utility operators to staff manual overrides.

---

## 6. Legal Safe Harbor

Q-DNA considers security research to be **authorized access** under the CFAA provided the researcher:

1. Acts in good faith.
2. Follows the CVD policy.
3. No exfiltration or destruction of user data.

**GDPR Note:** Researchers must NOT access PII. Demonstration of impact must use benign PoCs (e.g., `whoami`).

---

## 7. Coordination & Reporting

- **CISA/CERT/CC:** Multi-party coordination via VINCE for shared protocol flaws.
- **FedRAMP:** 30-day remediation for High-risk vulnerabilities in federal environments.
- **Advisory Format:** CVRF/CSAF for machine-readable advisories.

---

## References

[DISC-001] ISO/IEC 29147:2018 Information technology — Security techniques — Vulnerability disclosure.  
[DISC-002] Google Project Zero. "Policy and Disclosure Philosophy."  
[DISC-003] NIST SP 800-216. "Recommendations for Federal Vulnerability Disclosure Programs."  
[DISC-004] FDA. "Postmarket Management of Cybersecurity in Medical Devices."  
[DISC-005] HackerOne. "Vulnerability Disclosure Policy (VDP) Best Practices."  
[DISC-006] CISA. "Binding Operational Directive 20-01."  
[DISC-007] ISO/IEC 30111:2019 Information technology — Security techniques — Vulnerability handling processes.
