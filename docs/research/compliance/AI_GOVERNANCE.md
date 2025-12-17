# AI Governance and Compliance

**Category:** Compliance
**Version:** 1.0
**Last Updated:** December 17, 2025
**Status:** Complete
**Specification Links:** §1 (Executive Summary), §8 (Disclosure), §11 (SOA Ledger)

---

## Executive Summary

To transition from "Experimental" to "Enterprise," the Q-DNA framework must satisfy rigorous global standards for AI governance. The "Black Box" nature of neural networks is unacceptable in regulated industries. This document maps Q-DNA requirements to GDPR, NIST AI RMF, and ISO 42001.

---

## 1. Regulatory Framework Overview

### 1.1 Key Regulations

| Regulation       | Jurisdiction  | Focus                     | Q-DNA Impact                  |
| ---------------- | ------------- | ------------------------- | ----------------------------- |
| **GDPR Art. 22** | EU            | Automated decision rights | Human-in-the-loop requirement |
| **NIST AI RMF**  | US            | Risk management framework | Documentation standards       |
| **ISO 42001**    | International | AI Management Systems     | Audit trail requirements      |
| **EU AI Act**    | EU            | Risk categorization       | Conformity assessment         |

---

## 2. GDPR Article 22: Automated Decision-Making

### 2.1 The Right

> "The data subject shall have the right not to be subject to a decision based solely on automated processing, including profiling, which produces legal effects concerning him or her."

### 2.2 Q-DNA Implementation

**Detection Requirement:** The system must detect "Legal Effect" decisions:

- Employment decisions
- Credit/loan approvals
- Access to services
- Health recommendations

**Human-in-the-Loop (HITL):** When detected, L3 escalation is mandatory.

**Audit Trail:** Every automated decision must log:

- Input data (hashed for privacy)
- Model version
- Decision rationale (CoT if available)
- Human approver (if escalated)

> [COMP-001] GDPR Article 22. Official Journal of the European Union.

### 2.3 The "Right to Explanation"

GDPR implies (though doesn't explicitly mandate) explainability for automated decisions.

**Q-DNA Implementation:**

- Chain-of-Thought reasoning preserved in audit log
- `prompt_hash` enables replay of decision context
- Verification rationale included in schema

---

## 3. NIST AI Risk Management Framework

### 3.1 The Four Core Functions

| Function    | Purpose                      | Q-DNA Mapping                       |
| ----------- | ---------------------------- | ----------------------------------- |
| **GOVERN**  | Culture, accountability      | Agent Accountability Contract       |
| **MAP**     | Context, risk identification | SOA Ledger event taxonomy           |
| **MEASURE** | Assessment, metrics          | Appendix B research metrics         |
| **MANAGE**  | Response, monitoring         | Operational modes, circuit breakers |

> [COMP-002] NIST AI RMF 1.0. (2023). National Institute of Standards and Technology.

### 3.2 Risk Categories

| Category              | Description                         | Q-DNA Risk Grade   |
| --------------------- | ----------------------------------- | ------------------ |
| **Minimal Risk**      | Low impact, reversible              | L1                 |
| **Limited Risk**      | Moderate impact, transparency needs | L2                 |
| **High Risk**         | Significant impact, safety-critical | L3                 |
| **Unacceptable Risk** | Prohibited applications             | N/A (out of scope) |

### 3.3 Documentation Requirements

NIST recommends:

- Model cards
- Data sheets
- Risk assessments
- Continuous monitoring logs

**Q-DNA Implementation:** The SOA Ledger provides continuous monitoring; model cards should be added to agent registration.

---

## 4. ISO 42001: AI Management Systems

### 4.1 Overview

ISO 42001 is the first international standard specifically for AI Management Systems (AIMS).

### 4.2 Requirements

| Requirement                   | Q-DNA Evidence               |
| ----------------------------- | ---------------------------- |
| Risk assessment documentation | SOA Ledger + Risk Grades     |
| Operational controls          | Sentinel verification policy |
| Data quality management       | Citation policy, SCI         |
| Transparency                  | Audit log schema             |
| Accountability                | DID signing, reputation      |

> [COMP-003] ISO/IEC 42001:2023. AI Management Systems.

### 4.3 Audit Evidence

The Q-DNA Audit Log serves as the primary evidence artifact for ISO certification audits. Every agent action is traceable to:

- Actor (DID)
- Model version
- Trust score at time of action
- Verification result
- Human approver (if applicable)

---

## 5. EU AI Act Classification

### 5.1 Risk Categories

| Category         | Examples                                       | Q-DNA Classification         |
| ---------------- | ---------------------------------------------- | ---------------------------- |
| **Unacceptable** | Social scoring, manipulation                   | N/A                          |
| **High-Risk**    | Biometric, employment, critical infrastructure | Possible (context-dependent) |
| **Limited**      | Chatbots, emotion recognition                  | Likely baseline              |
| **Minimal**      | Spam filters, games                            | N/A                          |

### 5.2 Q-DNA as "High-Risk"?

If Q-DNA is used for:

- Code that controls critical infrastructure → High-Risk
- Employment-related decision support → High-Risk
- Financial transaction verification → High-Risk

**Implication:** Conformity assessment required before deployment.

### 5.3 Requirements for High-Risk Systems

| Requirement             | Q-DNA Implementation                |
| ----------------------- | ----------------------------------- |
| Risk management system  | §8 Divergence Protocol + SOA Ledger |
| Data governance         | §5 Citation Policy + SCI            |
| Technical documentation | Research Library + Specification    |
| Record-keeping          | SOA Ledger                          |
| Transparency            | Audit schema + CoT                  |
| Human oversight         | L3 Overseer requirement             |
| Accuracy & robustness   | Verification pipeline               |

---

## 6. The Q-DNA Audit Log Schema

To satisfy all regulatory requirements, Q-DNA mandates a standardized JSON Audit Schema:

```json
{
  "event_id": "UUID-v4",
  "timestamp": "ISO-8601-UTC",
  "actor": {
    "agent_id": "Q-DNA-Worker-05",
    "model_version": "Phi-3-Mini-4k-Instruct",
    "trust_score": 0.88
  },
  "action": {
    "type": "EXECUTE_TOOL",
    "tool_name": "currency_transfer",
    "parameters": { "amount": 100, "currency": "USD" }
  },
  "context": {
    "prompt_hash": "SHA-256",
    "session_id": "sess-998"
  },
  "verification": {
    "required": true,
    "method": "PyVeritas",
    "result": "PASS",
    "verifier_id": "Q-DNA-Verifier-01"
  },
  "governance": {
    "gdpr_art22_trigger": true,
    "human_approver": "User-Admin-01"
  }
}
```

### Schema Field Mapping to Regulations

| Field                         | GDPR         | NIST    | ISO 42001           |
| ----------------------------- | ------------ | ------- | ------------------- |
| event_id                      | Audit trail  | MAP     | Record-keeping      |
| actor.model_version           | Transparency | MAP     | Documentation       |
| actor.trust_score             | N/A          | MEASURE | Risk assessment     |
| verification.result           | Accuracy     | MANAGE  | Operational control |
| governance.gdpr_art22_trigger | Art. 22      | N/A     | Human oversight     |
| governance.human_approver     | Art. 22      | GOVERN  | Accountability      |

---

## 7. Vulnerability Disclosure Policy

### 7.1 Industry Standards

| Policy                  | Deadline | Rationale                         |
| ----------------------- | -------- | --------------------------------- |
| **CERT/CC**             | 45 days  | Faster pressure on vendors        |
| **Google Project Zero** | 90 days  | Complex vulnerabilities need time |

### 7.2 Q-DNA Policy

**Adopted Standard:** Google Project Zero (90 days)

**Rationale:** AI vulnerabilities are complex and may require model retraining or architectural changes. 90 days provides sufficient time for responsible remediation.

**Process:**

1. Report received → Acknowledgment within 24 hours
2. Triage → Within 7 days
3. Fix development → 0-83 days
4. Disclosure → Day 90 (or earlier if patched)

> [COMP-004] Google Project Zero Disclosure Policy. (2023).

---

## 8. Recommended Parameters

| Parameter                | Value            | Confidence | Citation     |
| ------------------------ | ---------------- | ---------- | ------------ |
| GDPR breach notification | 72 hours         | High       | Art. 33      |
| Disclosure deadline      | 90 days          | High       | Project Zero |
| High-risk audit depth    | Full CoT logging | Medium     | EU AI Act    |
| L3 human approval        | Mandatory        | High       | Art. 22      |

---

## 9. Specification Updates

Based on this research, recommend the following updates to Q-DNA_SPECIFICATION.md:

1. **§8 (Disclosure):** Adopt 90-day disclosure policy (vs. 45-day)
2. **§11 (SOA Ledger):** Extend schema with governance fields
3. **New Section:** Add compliance matrix reference
4. **App A:** Add GDPR Art. 22 detection as pass criteria

---

## References

[COMP-001] GDPR Article 22. Official Journal of the European Union.

- Key requirement: Right not to be subject to automated decisions
- Applied In: §4 L3 escalation

[COMP-002] NIST AI RMF 1.0. (2023). National Institute of Standards and Technology.

- Key framework: Govern, Map, Measure, Manage
- Applied In: SOA Ledger design

[COMP-003] ISO/IEC 42001:2023. AI Management Systems.

- Key requirement: Documented risk assessment and controls
- Applied In: Research Library as evidence

[COMP-004] Google Project Zero Disclosure Policy.

- Key policy: 90-day disclosure deadline
- Applied In: §8.2 disclosure windows
