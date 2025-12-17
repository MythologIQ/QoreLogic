# Trust Dynamics and Reputation Modeling

**Category:** Foundations
**Version:** 1.0
**Last Updated:** December 17, 2025
**Status:** Complete
**Specification Links:** §5.3 (SCI), §9 (Remediation), §11 (SOA Ledger)

---

## Executive Summary

Trust in distributed multi-agent systems cannot be assumed—it must be engineered. This document synthesizes research on dynamic reputation modeling, transitive trust propagation, and trust repair mechanisms to provide validated parameters for the Q-DNA Specification.

The key insight is that **trust is a volatile asset** with temporal decay. Static trust scores are insufficient for long-running autonomous systems. The Q-DNA framework adopts the Exponential Weighted Moving Average (EWMA) model from financial risk management to model the "half-life" of reliability.

---

## 1. The Mathematics of Trust Decay

### 1.1 Exponential Weighted Moving Average (EWMA)

Trust volatility is modeled using the RiskMetrics approach:

```
σ²_t = (1-λ) Σ λ^j × r²_{t-j}
```

Where:

- `r` = interaction outcome (success/failure)
- `λ` = decay factor (0 < λ < 1)
- Higher λ = slower decay (more memory)
- Lower λ = faster decay (more reactive)

### 1.2 Validated Lambda (λ) Parameters

| Context                        | λ Value  | Behavior                           | Use Case                        |
| ------------------------------ | -------- | ---------------------------------- | ------------------------------- |
| **High-Frequency / High-Risk** | **0.94** | Reactive; recent failures dominate | Code execution, financial tasks |
| **Low-Frequency / Long-Term**  | **0.97** | Stable; tolerates minor variance   | Advisory agents, storage nodes  |

> _Source: RiskMetrics Technical Document (JPMorgan). λ=0.94 places ~95% weight on the last 60 observations._

**Applied In:** §5.3.3 (SCI Adjustment Formula) — The α=0.8 memory factor aligns with financial decay models.

---

## 2. Transitive Trust and Damped Propagation

### 2.1 The Cold-Start Problem

How does Agent A trust Agent C when they've never interacted?

**Solution:** Transitive Trust (A trusts B, B trusts C → A can partially trust C)

**Risk:** Trust Spam and Sybil Attacks where malicious collectives artificially boost scores.

### 2.2 EigenTrust Algorithm

The EigenTrust algorithm computes global trust by:

1. Normalizing local trust scores into a matrix
2. Computing the left principal eigenvector
3. Interpreting result as "random walk probability"

> [TRUST-001] Kamvar, S., Schlosser, M., & Garcia-Molina, H. (2003). "The EigenTrust Algorithm for Reputation Management in P2P Networks." WWW '03.

**Limitation:** Assumes static graph; doesn't handle temporal decay.

### 2.3 Damped Propagation

To prevent infinite trust propagation, Q-DNA implements **Damped Propagation**:

```
T_{A→C} = T_{A→B} × T_{B→C} × δ
```

| Parameter          | Value   | Rationale                                                |
| ------------------ | ------- | -------------------------------------------------------- |
| Damping Factor (δ) | **0.5** | Trust halves at each hop                                 |
| Max-Hop Limit      | **3**   | Dunbar Layers research; trust evaporates beyond 3-4 hops |

**Applied In:** §5.3 (SCI) — Transitive citations should decay similarly.

---

## 3. The Lewicki-Bunker Trust Staging Model

Quantitative scores map to qualitative behaviors:

| Stage | Name                             | Trust Score | Q-DNA Behavior                        |
| ----- | -------------------------------- | ----------- | ------------------------------------- |
| **1** | Calculus-Based Trust (CBT)       | 0.0 – 0.5   | Probationary; 100% verification       |
| **2** | Knowledge-Based Trust (KBT)      | 0.5 – 0.8   | Standard; sampling verification       |
| **3** | Identification-Based Trust (IBT) | > 0.8       | Full delegation; can commit resources |

> [TRUST-002] Lewicki, R. J., & Bunker, B. B. (1996). "Developing and Maintaining Trust in Work Relationships." Trust in Organizations, SAGE.

### Trust Stage Transitions

**CBT → KBT:** Requires sustained positive interactions demonstrating predictability.

**KBT → IBT:** Requires alignment of goals and values; rare in agent-to-agent relationships.

**Violation Impact:**

- CBT violation: Standard penalty, recoverable
- KBT violation: Demoted to CBT, requires rebuilding
- IBT violation: Often irreparable; permanent reputation damage

**Applied In:** §9.4 (Reputation Recovery) — Recovery rates should vary by trust stage.

---

## 4. Trust Repair and Conflict Resolution

### 4.1 The Dirks-Ferrin Meta-Analysis

Research on trust repair shows:

| Violation Type              | Repair Difficulty | Required Actions                              |
| --------------------------- | ----------------- | --------------------------------------------- |
| Competence (honest mistake) | Moderate          | Acknowledgment + demonstration of improvement |
| Integrity (deception)       | High              | Apology + structural changes + time           |

> [TRUST-003] Dirks, K. T., & Ferrin, D. L. (2002). "Trust in Leadership: Meta-Analytic Findings." Journal of Applied Psychology.

### 4.2 Cooling-Off Periods

Research on platform governance (eBay, gaming) shows:

- **Permanent bans** lead to "Ban Evasion" (creating new identities)
- **Temporary suspensions** are more effective for behavior correction

**Q-DNA Policy:**

- First-time offenders: Cooling-off state (cannot bid on Contract Nets)
- Duration: Calculated by trust decay function—time to re-enter CBT threshold

**Applied In:** §9.3 (Manipulation Track) — 48-hour quarantine aligns with cooling-off research.

---

## 5. Sybil Resistance

### 5.1 The Sybil Attack

A malicious actor creates multiple fake identities to:

- Artificially boost reputation
- Overwhelm voting mechanisms
- Dilute legitimate trust signals

### 5.2 Countermeasures

| Mechanism         | Description                      | Q-DNA Application                             |
| ----------------- | -------------------------------- | --------------------------------------------- |
| **Identity Cost** | Make identity creation expensive | DID registration requires cryptographic work  |
| **Trust Anchors** | Pre-trusted seeds in EigenTrust  | Overseer (Human) is the ultimate trust anchor |
| **Damping**       | Transitive trust decays          | δ=0.5 prevents reputation inflation           |
| **Hop Limits**    | Cap trust chain length           | Max 3 hops                                    |

**Applied In:** §10.2 (Identity Requirements) — Ed25519 signing provides identity cost.

---

## 6. Recommended Parameters

| Parameter                 | Value                     | Confidence | Citation            |
| ------------------------- | ------------------------- | ---------- | ------------------- |
| High-risk trust decay (λ) | 0.94                      | High       | RiskMetrics         |
| Low-risk trust decay (λ)  | 0.97                      | High       | RiskMetrics         |
| Transitive damping (δ)    | 0.5                       | Medium     | Network theory      |
| Max trust hops            | 3                         | Medium     | Dunbar research     |
| CBT threshold             | 0.0 – 0.5                 | High       | Lewicki-Bunker      |
| KBT threshold             | 0.5 – 0.8                 | High       | Lewicki-Bunker      |
| IBT threshold             | > 0.8                     | High       | Lewicki-Bunker      |
| Cooling-off effectiveness | Higher than permanent ban | High       | Platform governance |

---

## 7. Specification Updates

Based on this research, recommend the following updates to Q-DNA_SPECIFICATION.md:

1. **§5.3.3:** Add λ decay factor to SCI adjustment formula
2. **§5.3:** Add transitive trust damping factor (δ=0.5) and hop limit (3)
3. **§9.4:** Map reputation thresholds to Lewicki-Bunker stages
4. **§9.3:** Formalize cooling-off period calculation

---

## References

[TRUST-001] Kamvar, S., Schlosser, M., & Garcia-Molina, H. (2003). "The EigenTrust Algorithm for Reputation Management in P2P Networks." WWW '03.

- Key finding: Principal eigenvector provides Sybil-resistant global trust
- Applied In: §5.3 transitive trust model

[TRUST-002] Lewicki, R. J., & Bunker, B. B. (1996). "Developing and Maintaining Trust in Work Relationships." Trust in Organizations, SAGE.

- Key finding: CBT → KBT → IBT progression model
- Applied In: §9.4 reputation recovery stages

[TRUST-003] Dirks, K. T., & Ferrin, D. L. (2002). "Trust in Leadership: Meta-Analytic Findings." Journal of Applied Psychology.

- Key finding: Integrity violations harder to repair than competence violations
- Applied In: §9.2 vs §9.3 penalty differentiation

[TRUST-004] RiskMetrics Technical Document. (1996). JPMorgan.

- Key finding: λ=0.94 optimal for high-frequency decay
- Applied In: §5.3.3 adjustment formula calibration
