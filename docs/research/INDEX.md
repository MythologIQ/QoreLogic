# Q-DNA Research Library

**Version:** 1.0
**Created:** December 17, 2025
**Status:** Active Collection
**Purpose:** Authoritative reference library for Q-DNA specification development and evolution

---

## Research Structure Overview

Q-DNA maintains **two complementary research locations**:

| Location                       | Purpose               | Content                                               |
| ------------------------------ | --------------------- | ----------------------------------------------------- |
| `docs/research/` (this folder) | **Reference Library** | Academic literature, standards, benchmarks, citations |
| `research/` (project root)     | **Active Laboratory** | Study protocols, raw data, experimental processes     |

The Reference Library provides the **intellectual foundation**; the Laboratory provides the **operational research process**.

---

## Library Structure

```
Q-DNA/docs/research/
├── INDEX.md                    ← This file (catalog and navigation)
├── METHODOLOGY.md              ← Research standards and citation format
│
├── foundations/                ← Theoretical foundations
│   ├── FORMAL_METHODS.md       ← Formal verification theory
│   ├── TRUST_DYNAMICS.md       ← Reputation and trust systems
│   ├── BEHAVIORAL_ECONOMICS.md ← Deterrence and incentive design
│   └── INFORMATION_THEORY.md   ← Citation depth, decay, provenance
│
├── technologies/               ← Implementation research
│   ├── SENTINEL_TECH.md        ← Sentinel verification (EXISTS)
│   ├── LLM_RELIABILITY.md      ← Hallucination and determinism
│   ├── PRIVACY_ENGINEERING.md  ← Differential privacy, PII handling
│   └── CRYPTOGRAPHIC_STANDARDS.md ← Key management, signing
│
├── compliance/                 ← Legal and regulatory
│   ├── DISCLOSURE_STANDARDS.md ← CERT/CC, vulnerability timing
│   ├── DATA_PROTECTION.md      ← GDPR, CCPA, HIPAA implications
│   └── AI_GOVERNANCE.md        ← NIST AI RMF, EU AI Act
│
├── benchmarks/                 ← Empirical data and metrics
│   ├── HALLUCINATION_RATES.md  ← HaluEval, TruthfulQA baselines
│   ├── SAST_ACCURACY.md        ← False positive rate benchmarks
│   └── SRE_THRESHOLDS.md       ← Resource governance standards
│
├── original_findings/          ← Q-DNA specific research (future)
│   └── .gitkeep                ← Placeholder for original research
│
└── synthesis/                  ← Integration documents
    ├── RESEARCH_VALIDATION.md  ← Design parameter validation (EXISTS)
    └── GAPS_AND_QUESTIONS.md   ← Open research questions
```

---

## Document Categories

### 1. Foundations (Theoretical)

Core academic research that informs Q-DNA design philosophy.

| Document                | Primary Sources                          | Q-DNA Sections     |
| ----------------------- | ---------------------------------------- | ------------------ |
| FORMAL_METHODS.md       | Hoare, Dijkstra, CBMC, ESBMC             | §3 (Sentinel), §13 |
| TRUST_DYNAMICS.md       | Lewicki-Bunker, EigenTrust, Dirks-Ferrin | §5.3 (SCI), §9     |
| BEHAVIORAL_ECONOMICS.md | Nagin, Becker, Kahneman                  | §9 (Penalties)     |
| INFORMATION_THEORY.md   | Shannon, bibliometrics                   | §5.2 (Citations)   |

### 2. Technologies (Implementation)

Practical research on tools, techniques, and systems.

| Document                   | Primary Sources           | Q-DNA Sections |
| -------------------------- | ------------------------- | -------------- |
| SENTINEL_TECH.md           | PyVeritas, ACCA, SPIN     | §3, §13        |
| LLM_RELIABILITY.md         | HaluEval, TruthfulQA, RAG | §4, App A      |
| PRIVACY_ENGINEERING.md     | Dwork, Apple DP, Census   | §10            |
| CRYPTOGRAPHIC_STANDARDS.md | NIST SP 800-57            | §10.2          |

### 3. Compliance (Regulatory)

Legal and regulatory requirements affecting design.

| Document                | Primary Sources        | Q-DNA Sections |
| ----------------------- | ---------------------- | -------------- |
| DISCLOSURE_STANDARDS.md | CERT/CC, Google P0     | §8             |
| DATA_PROTECTION.md      | GDPR, CCPA, HIPAA      | §10            |
| AI_GOVERNANCE.md        | NIST AI RMF, EU AI Act | §1, §8         |

### 4. Benchmarks (Empirical)

Quantitative data informing specific thresholds.

| Document               | Primary Sources       | Q-DNA Sections |
| ---------------------- | --------------------- | -------------- |
| HALLUCINATION_RATES.md | Li et al., Lin et al. | App A          |
| SAST_ACCURACY.md       | OWASP, Veracode       | App A          |
| SRE_THRESHOLDS.md      | Google SRE, FinOps    | §12            |

### 5. Original Findings (Q-DNA Specific)

Research conducted during Q-DNA development.

| Document | Content                  | Status  |
| -------- | ------------------------ | ------- |
| (future) | Pilot deployment metrics | Planned |
| (future) | HRM training results     | Planned |
| (future) | SCI calibration data     | Planned |

### 6. Synthesis (Integration)

Documents that consolidate and apply research.

| Document               | Purpose                 | Status    |
| ---------------------- | ----------------------- | --------- |
| RESEARCH_VALIDATION.md | Parameter justification | Complete  |
| GAPS_AND_QUESTIONS.md  | Open research agenda    | To create |

---

## Citation Standard

All research documents use consistent citation format:

### In-Document Citations

```markdown
The penalty structure aligns with HILS research [BEHAV-001].
```

### Reference Block

```markdown
## References

[BEHAV-001] Nagin, D. (2013). "Deterrence in the Twenty-First Century."
Crime and Justice, 42(1), 199-263.
DOI: 10.1086/670398
Category: Behavioral Economics
Relevance: Penalty calibration, HILS vs LIHS
```

### Cross-Reference to Spec

```markdown
> Applied in: Q-DNA_SPECIFICATION.md §9.1 (Micro-Penalty Layer)
```

---

## Research Status Tracking

| Category     | Documents | Complete | In Progress | Planned |
| ------------ | --------- | -------- | ----------- | ------- |
| Foundations  | 5         | 5        | 0           | 0       |
| Technologies | 4         | 4        | 0           | 0       |
| Compliance   | 3         | 3        | 0           | 0       |
| Benchmarks   | 2         | 2        | 0           | 1       |
| Original     | 0         | 0        | 0           | TBD     |
| Synthesis    | 2         | 2        | 0           | 0       |

**Total:** 16 category documents complete, 4 root-level documents

> **Note:** HALLUCINATION_RATES.md is documented in foundations/ but INDEX structure lists it under benchmarks/. Consider relocating for consistency.

### Completed Documents

**Foundations (5):**

- `foundations/TRUST_DYNAMICS.md` - EigenTrust, Lewicki-Bunker, decay factors
- `foundations/FORMAL_METHODS.md` - Hoare logic, BMC, PyVeritas, Z3
- `foundations/BEHAVIORAL_ECONOMICS.md` - HILS, deterrence, loss aversion
- `foundations/INFORMATION_THEORY.md` - Citation decay, DPI, TTL
- `foundations/HALLUCINATION_RATES.md` - 18-50% spectrum, HaluEval, TruthfulQA

**Technologies (4):**

- `technologies/LLM_RELIABILITY.md` - Hallucination mitigation, verification pipeline
- `technologies/MULTI_AGENT_COORDINATION.md` - JSON-RPC, topologies, edge deployment
- `technologies/PRIVACY_ENGINEERING.md` - Differential privacy, ε budget, PII detection
- `technologies/CRYPTOGRAPHIC_STANDARDS.md` - Ed25519, key rotation, Merkle chains

**Compliance (3):**

- `compliance/AI_GOVERNANCE.md` - GDPR, NIST AI RMF, ISO 42001, EU AI Act
- `compliance/DATA_PROTECTION.md` - GDPR, CCPA, HIPAA, cross-border
- `compliance/DISCLOSURE_STANDARDS.md` - CERT/CC, Project Zero 90-day policy

**Benchmarks (2):**

- `benchmarks/SAST_ACCURACY.md` - OWASP, Veracode, LLM triage
- `benchmarks/SRE_THRESHOLDS.md` - Queue depth, CPU saturation, backpressure

**Synthesis (2):**

- `synthesis/RESEARCH_VALIDATION.md` - Design parameter validation
- `synthesis/GAPS_AND_QUESTIONS.md` - Open research agenda

**Root Level (4):**

- `INDEX.md` - This catalog
- `METHODOLOGY.md` - Citation standards
- `GENERATION_PROMPTS.md` - Research prompt templates
- `SENTINEL_TECH.md` - Sentinel verification overview

---

## Integration with Specification

The research library serves the specification through:

1. **Justification:** Every design parameter traces to a research document
2. **Evolution:** Research gaps inform specification updates
3. **Validation:** Benchmarks provide acceptance criteria baselines
4. **Compliance:** Regulatory research ensures legal defensibility

### Traceability Matrix

| Spec Section     | Research Documents                         |
| ---------------- | ------------------------------------------ |
| §3 (Sentinel)    | SENTINEL_TECH, FORMAL_METHODS              |
| §5 (Evidence)    | TRUST_DYNAMICS, INFORMATION_THEORY         |
| §8 (Disclosure)  | DISCLOSURE_STANDARDS, BEHAVIORAL_ECONOMICS |
| §9 (Remediation) | BEHAVIORAL_ECONOMICS, TRUST_DYNAMICS       |
| §10 (Privacy)    | PRIVACY_ENGINEERING, DATA_PROTECTION       |
| §12 (Operations) | SRE_THRESHOLDS                             |
| App A (Criteria) | HALLUCINATION_RATES, SAST_ACCURACY         |

---

## Maintenance Protocol

### Adding New Research

1. Create document in appropriate category folder
2. Use standard citation format
3. Update this INDEX.md with new entry
4. Cross-reference to specification sections
5. Update GAPS_AND_QUESTIONS.md if research answers open questions

### Deprecating Seed Documents

When research library is complete, the following can be archived:

- `Q-DNA-discussion.md` → Replaced by structured research docs
- Any ad-hoc notes → Consolidated into category documents

### Original Research Protocol

When Q-DNA produces original findings:

1. Document methodology in finding document
2. Include raw data or links to data
3. Note confidence intervals and limitations
4. Cross-reference to external validation (if any)

---

## Next Steps

**Completed:**

- [x] Create INDEX.md (this file)
- [x] Create METHODOLOGY.md (citation standards)
- [x] Create GAPS_AND_QUESTIONS.md (open research agenda)
- [x] Move RESEARCH_VALIDATION.md to synthesis/
- [x] Create foundations/FORMAL_METHODS.md
- [x] Create foundations/TRUST_DYNAMICS.md
- [x] Create foundations/BEHAVIORAL_ECONOMICS.md
- [x] Create foundations/INFORMATION_THEORY.md
- [x] Create foundations/HALLUCINATION_RATES.md
- [x] Create technologies/LLM_RELIABILITY.md
- [x] Create technologies/PRIVACY_ENGINEERING.md
- [x] Create technologies/CRYPTOGRAPHIC_STANDARDS.md
- [x] Create technologies/MULTI_AGENT_COORDINATION.md
- [x] Create compliance/DISCLOSURE_STANDARDS.md
- [x] Create compliance/DATA_PROTECTION.md
- [x] Create compliance/AI_GOVERNANCE.md
- [x] Create benchmarks/SAST_ACCURACY.md
- [x] Create benchmarks/SRE_THRESHOLDS.md

**Remaining:**

- [ ] Expand SENTINEL_TECH.md (add formal citations per METHODOLOGY.md)
- [ ] Create benchmarks/HALLUCINATION_RATES.md (or relocate from foundations/)
- [ ] Create CITATION_REGISTRY.md (central citation index)
- [ ] Begin original_findings/ population after pilot deployment
