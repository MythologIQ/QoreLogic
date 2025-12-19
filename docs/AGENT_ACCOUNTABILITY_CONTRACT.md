# Agent Accountability Contract (AAC v2.0)

**Version:** 2.0 (Research Standard - Empirically Validated)
**Status:** Active Research & Proof-of-Concept
**Philosophy:** Recursive Improvement, Tiered Evaluation, Fail Forward
**Research Foundation:** See [Research Library](./research/INDEX.md)

---

## Preamble: The Research Mandate

This document is not merely a software requirement specification; it is a **Governance Standard for Autonomous Systems Research**. Our goal is not to build a Minimum Viable Product (MVP), but to establish a **provably correct system of record** that yields definitive, consistent results.

### The "Fail Forward" Doctrine

- **Failure is Data:** A failed verification is as valuable as a passed one. It defines the boundary of the system's capability.
- **Negative Result Retention:** Failed artifacts train the Sentinel Agent on "what not to do."
- **Bootstrapping:** We begin by identifying failure modes. We optimize by systematically eliminating them.

### The HILS Principle

Per behavioral economics research [BEHAV-001], the system prioritizes **High Inspection / Low Severity (HILS)** over infrequent severe penalties:

- 100% detection of minor infractions (micro-penalties)
- Frequent, small corrections create tighter feedback loops
- Prevents "Gambler's Fallacy" risk-seeking behavior

---

## I. Core Principles (The Constitution)

### 1.1 Truth is Earned

No claim is trusted by default. It must be verified through a cryptographically traceable chain of evidence.

### 1.2 Dual Aims

1. **Protect User Safety:** Prevent harm (Physical, Financial, Reputational).
2. **Protect Objective Truth:** Prevent hallucination and misinformation.

### 1.3 Traceability

Every decision must have a history. We must be able to replay the "thought process" (Chain of Thought) that led to any artifact.

### 1.4 Probabilistic Trust

Trust is not binary. The Source Credibility Index (SCI) provides a 0-100 score with validated thresholds:

- **≥90:** Gold Standard (Auto-accept)
- **60-89:** Verification Required
- **40-59:** Human-in-the-Loop
- **<35:** Hard Rejection

---

## II. Tiered Evaluations (The Risk Matrix)

The system applies **Recursive Quality Checks** relative to the risk level.

| Grade           | Definition                                                   | Verification Depth                                                                  | Resource Allocation         |
| :-------------- | :----------------------------------------------------------- | :---------------------------------------------------------------------------------- | :-------------------------- |
| **L1 (Low)**    | Routine. Typos, minor docs, variable renames.                | **Lean Mode.** 10% sampling. Fast-path check.                                       | Low Priority. Best Effort.  |
| **L2 (Medium)** | Functional. API integration, UI changes, non-critical logic. | **Standard Mode.** Full Citation Audit. 1 Sentinel Pass.                            | Standard Priority. <5 mins. |
| **L3 (High)**   | Critical. Safety, Auth, Finance, Regulatory, Medical.        | **High Assurance.** Formal Verification. Human Overseer. **Recursive Cross-Check.** | **L3 Reserve.** <24 Hours.  |

### Auto-Classification Rules

- **Force L3:** `eval()`, `exec()`, `os.system()`, SQL without parameterization
- **Force L2:** External API calls, file I/O, network operations
- **Default L1:** Formatting, comments, documentation

---

## III. Recursive Verification Lifecycle

This is a loop, not a line. The output of one stage feeds the validation of the next.

```
┌─────────────────────────────────────────────────────────┐
│                    VERIFICATION LOOP                    │
├─────────────────────────────────────────────────────────┤
│  1. PROPOSAL ──→ Scrivener submits spec/code           │
│       │                                                 │
│       ▼                                                 │
│  2. CHALLENGE ──→ Sentinel runs Quality DNA check      │
│       │    ├── FAIL: Log to Shadow Genome              │
│       │    │         Return with "Negative Constraint" │
│       │    └── PASS: Proceed to Consensus              │
│       ▼                                                 │
│  3. CONSENSUS ──→ Judge validates identity & chain     │
│       │                                                 │
│       ▼                                                 │
│  4. INTEGRATION ──→ Pattern added to "Known Good" set  │
│       │                                                 │
│       └────────────→ (Loop repeats)                    │
└─────────────────────────────────────────────────────────┘
```

### The Zero-Trust Verification Pipeline

Per LLM reliability research [LLM-001], code verification uses three tiers:

| Tier  | Method              | Coverage | Tools                                |
| :---- | :------------------ | :------- | :----------------------------------- |
| **1** | Static Analysis     | All code | Pylint, Flake8, MyPy                 |
| **2** | Design by Contract  | All code | `deal` library (pre/post conditions) |
| **3** | Formal Verification | L3 code  | PyVeritas + CBMC, CrossHair          |

---

## IV. Operational Modes (Resilience)

The system adapts its rigor based on environmental stress, but **never compromises L3 safety**.

| Mode       | Trigger          | L1         | L2        | L3         |
| :--------- | :--------------- | :--------- | :-------- | :--------- |
| **NORMAL** | Default          | 100%       | 100%      | 100%       |
| **LEAN**   | CPU >70% (5 min) | 10% sample | 100%      | 100%       |
| **SURGE**  | Queue >50 tasks  | Deferred   | 100%      | 100%       |
| **SAFE**   | Threat detected  | Suspended  | Suspended | Human only |

> Per SRE research [SRE-001], backpressure and load shedding are mandatory at queue capacity.

---

## V. Trust Dynamics (Reputation Engineering)

### 5.1 Dynamic Trust Decay

Trust is volatile. Per RiskMetrics research [TRUST-004]:

```
Trust_new = λ × Trust_old + (1-λ) × Verification_result
```

| Context         | λ (Decay Factor) | Behavior                           |
| :-------------- | :--------------- | :--------------------------------- |
| High-risk tasks | **0.94**         | Reactive; recent failures dominate |
| Advisory roles  | **0.97**         | Stable; tolerates minor variance   |

### 5.2 Transitive Trust

When Agent A hasn't met Agent C, trust propagates through Agent B with:

- **Damping Factor (δ):** 0.5 (trust halves at each hop)
- **Max Hops:** 3 (per Dunbar research)

```
Trust_{A→C} = Trust_{A→B} × Trust_{B→C} × 0.5
```

### 5.3 Lewicki-Bunker Trust Stages

| Stage | Name                             | Trust Score | QoreLogic Behavior                  |
| :---- | :------------------------------- | :---------- | :------------------------------ |
| 1     | Calculus-Based Trust (CBT)       | 0.0 – 0.5   | Probationary; 100% verification |
| 2     | Knowledge-Based Trust (KBT)      | 0.5 – 0.8   | Standard; sampling verification |
| 3     | Identification-Based Trust (IBT) | >0.8        | Full delegation                 |

---

## VI. Enforcement Tracks (Correction)

Agents are not deleted; they are corrected or quarantined.

### 6.1 Micro-Penalty Layer (Automated)

| Infraction              | Detection  | Penalty     |
| :---------------------- | :--------- | :---------- |
| Schema violation        | 100%       | 0.5% weight |
| API misuse              | 100%       | 0.5% weight |
| Stale citation          | 100%       | 1% weight   |
| Minor calibration drift | Continuous | 2% weight   |

### 6.2 Honest Error Track

- **Trigger:** Calibration error >0.2 (Overconfidence), repeated micro-penalties
- **Penalty:** 5% influence weight reduction
- **Action:** Context Flush. Retraining on failure examples.
- **Cooling-Off:** 24 hours

### 6.3 Manipulation Track

- **Trigger:** Hash chain tampering, citation fabrication, gaming
- **Penalty:** 25% influence weight reduction
- **Action:** 48-hour quarantine. Full re-audit.
- **Cooling-Off:** 24 hours before trust repair begins

### 6.4 Reputation Recovery

| State               | Recovery Rate | Conditions                 |
| :------------------ | :------------ | :------------------------- |
| After Micro-Penalty | +0.5%/audit   | Automatic                  |
| After Honest Error  | +1%/audit     | After 24h cooling-off      |
| After Manipulation  | +0.5%/audit   | After 48h + 3 clean audits |

- **Starting Weight:** 1.0
- **Max Weight:** 2.0
- **Min Weight:** 0.1 (allows recovery path)

---

## VII. The Divergence Doctrine

When a conflict exists between **Truth Disclosure** and **Imminent Harm**:

### 7.1 L3 Triage

The item is automatically locked as L3.

### 7.2 Deferral Windows (Per GDPR/CERT Research)

| Category                | Max Deferral  | Rationale                  |
| :---------------------- | :------------ | :------------------------- |
| Safety-Critical         | 4 hours       | Immediate risk             |
| Medical/Legal/Financial | 24 hours      | Regulatory alignment       |
| Reputational            | 72 hours      | Stakeholder notification   |
| Low Risk                | 0 (immediate) | No justification for delay |

### 7.3 Comfort Layer

Supportive framing is permitted **only after** verified facts are recorded in the SOA Ledger.

---

## VIII. Governance & Compliance

### 8.1 Regulatory Alignment

| Regulation   | Requirement                      | QoreLogic Implementation |
| :----------- | :------------------------------- | :------------------- |
| GDPR Art. 22 | Right to non-automated decisions | L3 Human-in-the-Loop |
| NIST AI RMF  | Govern, Map, Measure, Manage     | SOA Ledger + Metrics |
| ISO 42001    | AI Management Systems            | Audit log schema     |

### 8.2 Vulnerability Disclosure

**Adopted Standard:** Google Project Zero (90 days)

- Acknowledgment: 24 hours
- Triage: 7 days
- Disclosure: Day 90 (or earlier if patched)

### 8.3 Audit Log Schema

Every decision is logged with:

- `event_id`, `timestamp`, `actor` (DID, model version, trust score)
- `action` (type, parameters)
- `verification` (method, result, verifier)
- `governance` (GDPR trigger, human approver)

---

## IX. Acceptance Criteria (The "Definitive Result")

| Metric                   | Target     | Required Components           |
| :----------------------- | :--------- | :---------------------------- |
| Hallucination Rate       | ≤1%†       | RAG + CoT + Span Verification |
| Hallucination Catch Rate | ≥95%       | Sentinel + verification loop  |
| False Positive Rate      | ≤5%†       | Enterprise-grade SAST         |
| L3 Verification SLA      | 100% <24h  | Queue management              |
| L3 First Response        | <2 min     | Immediate acknowledgment      |
| PII Leakage              | 0%         | Mandatory redaction           |
| Merkle Chain Integrity   | 100%       | Hash verification             |
| Determinism              | Semantic\* | Seed logging + drift tracking |

> † "Forcing functions" requiring specific architecture
>
> - Bitwise determinism infeasible; semantic equivalence measured

---

## X. Research References

This contract is grounded in empirical research documented in the [Research Library](./research/INDEX.md):

- **[TRUST-001]** Kamvar et al. - EigenTrust Algorithm
- **[TRUST-002]** Lewicki & Bunker - Trust Stages
- **[TRUST-004]** RiskMetrics - Decay Factors
- **[BEHAV-001]** Nagin - HILS Deterrence
- **[LLM-001]** HaluEval - Hallucination Benchmarks
- **[COMP-001]** GDPR Article 22
- **[COMP-002]** NIST AI RMF
- **[SRE-001]** Google SRE Handbook

---

## Changelog

| Version | Date           | Changes                                                 |
| :------ | :------------- | :------------------------------------------------------ |
| 1.0     | 2025-12        | Initial draft                                           |
| 1.2     | 2025-12        | Research Standard formatting                            |
| **2.0** | **2025-12-17** | **Empirically validated; integrated research findings** |
