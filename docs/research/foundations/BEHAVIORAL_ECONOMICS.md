# Behavioral Economics Research Document

**Version:** 1.0  
**Created:** December 18, 2025  
**Status:** Complete  
**Purpose:** Deterrence theory and incentive design for QoreLogic governance  
**Cross-Reference:** QoreLogic Spec §9 (Remediation), §5.3.3 (Adjustment Formula)

---

## 1. Executive Summary

Traditional AI governance relies on rigid determinism. QoreLogic requires a paradigm shift to **probabilistic and incentive-based governance** rooted in Behavioral Economics. This report synthesizes:

- **Gary Becker's** economic model of crime (rational choice)
- **Daniel Nagin's** empirical findings on detection certainty vs punishment severity
- **Kahneman/Tversky's** Prospect Theory and loss aversion
- **Cooling-off periods** as temporal circuit breakers

**Key Finding:** A governance system should prioritize **omnipresent monitoring (high p)** over **draconian kill-switches (high f)**.

---

## 2. The Economic Foundations of Compliance

### 2.1 The Classical Rational Choice Model

Gary Becker's 1968 "Crime and Punishment: An Economic Approach" posits that criminal behavior is a **rational economic choice**, not a moral failing.

**Expected Utility of Violation:**
$$EU = pU(Y - f) + (1-p)U(Y)$$

Where:

- $p$ = probability of detection (Certainty)
- $f$ = severity of punishment
- $Y$ = gain from offense

**Implication for QoreLogic:** If agents deviate from safety protocols, it's because Expected Utility of Violation > Expected Utility of Compliance. The deviation is a **rational response to flawed incentives**.

### 2.2 Bounded Rationality

Agents operate under:

- **Information Asymmetry:** Cannot observe true detection probability
- **Perceived Detection Risk (PDR):** Updates based on experience
- Agents who commit violations without being caught **lower their PDR**, reinforcing behavior

---

## 3. Certainty vs. Severity: The Nagin Consensus

### 3.1 Key Finding

> "The certainty of apprehension is a far more effective deterrent than the severity of the ensuing consequence." — Daniel Nagin

**Severity fails due to:**

- **Temporal Discounting:** Severe but distant/unlikely punishment is discounted
- **Signal Loss:** Agents "know little about sanctions for specific crimes"

### 3.2 HILS vs. LIHS Experiments

| Feature                   | HILS                | LIHS                    |
| ------------------------- | ------------------- | ----------------------- |
| Detection Probability (p) | High (0.9 - 1.0)    | Low (< 0.1)             |
| Penalty Magnitude (f)     | Low (Corrective)    | High (Catastrophic)     |
| Behavioral Outcome        | **High Compliance** | Risk-Seeking / Gambling |
| Mechanism                 | Immediate Feedback  | Temporal Discounting    |
| System Stability          | **High**            | Low (Variance & Shocks) |
| **QoreLogic Recommendation**  | **ADOPT**           | REJECT                  |

**Result:** HILS ($p=0.9$) significantly more effective than LIHS.

### 3.3 The 100% Detection Horizon

- Human sentinels suffer **vigilance decrement**
- AI monitors can maintain $p = 1.0$ indefinitely
- QoreLogic should invest in **Continuous Automated Auditing** (HILS)

---

## 4. Prospect Theory: Loss Aversion

### 4.1 The Magic Number: λ ≈ 2.25

Losses hurt **2.25× more** than equivalent gains feel good.

**Value Function:**
$$v(x) = \begin{cases} x^\alpha & \text{if } x \ge 0 \\ -\lambda(-x)^\beta & \text{if } x < 0 \end{cases}$$

**For QoreLogic:** Penalty must be at least **2.25× the perceived gain** to be psychologically neutral.

### 4.2 Asymmetric Penalty Design

| Feature             | Symmetric Model        | Asymmetric (Convex) Model |
| ------------------- | ---------------------- | ------------------------- |
| Structure           | Reward +x / Penalty -x | Reward +x / Penalty -x²   |
| Loss Aversion       | Ignores λ              | **Leverages λ**           |
| Effect on Collusion | Promotes Silence       | Promotes Reporting        |
| Compliance Outcome  | Moderate               | **High**                  |

**Convex Penalty Function:**
$$P(x) \propto x^n \quad \text{where } n > 1$$

Prevents aggregating small violations or justifying large violations with linear trade-offs.

### 4.3 Framing Effects

Frame compliance as **"avoiding a loss"** rather than "gaining a bonus":

| Bad Frame                      | Good Frame                         |
| ------------------------------ | ---------------------------------- |
| Base 100 + 20 bonus for safety | Base 120 - 20 penalty for unsafety |

Same economic value, **stronger behavioral impact**.

---

## 5. Cognitive Biases: Gambler's Fallacy

### 5.1 The Resetting Effect

**Danger:** Offenders believe being caught twice in a row is "extremely unlikely."

> "Punished offenders reset their sanction certainty estimate, believing they would have to be exceedingly unlucky to be apprehended again."

**Counter-Strategy:** Implement **Probationary Probability Shift**:

- If detected → enter "Probation Mode" where $p = 1.0$ for set duration
- Agent learns detection is **positively autocorrelated**

### 5.2 Low Detection Feedback Loop

1. Agent attempts minor violation
2. System fails to detect (Low p)
3. Agent updates perceived p downward
4. Agent attempts **major** violation

**Solution:** Even "minor" infractions must be detected (HILS) to maintain PDR.

---

## 6. Cooling-Off Periods

### 6.1 The "Hot State" Problem

Agents in high-pressure states make poor decisions. Temporal governance restores "cold state" rationality.

### 6.2 Duration Benchmarks

| Context             | Duration    | Rationale                          |
| ------------------- | ----------- | ---------------------------------- |
| Police Misconduct   | 48 hours    | Allow trauma/adrenaline to subside |
| Consumer Protection | 48 hours    | Reverse "hot state" decisions      |
| Domestic Violence   | 48-72 hours | Prevent retaliation                |
| Labor Strikes       | 10-20 days  | Allow negotiation                  |

### 6.3 QoreLogic Implementation

| Trigger Event         | Duration   | Mechanism                         |
| --------------------- | ---------- | --------------------------------- |
| Violation Detection   | 48 Cycles  | Agent locked in Read-Only mode    |
| Adversarial Contact   | 72 Cycles  | Agents "walled" from interaction  |
| Codebase Modification | 48 Hours   | Changes staged until human review |
| Resource Deadlock     | 10-20 Days | Arbitration protocol              |

---

## 7. The QoreLogic Governance Architecture

### 7.1 HILS-Convex Model

| Component                  | Implementation                              |
| -------------------------- | ------------------------------------------- |
| **Inspection (Certainty)** | AI Sentinels achieve $p \to 1$              |
| **Penalty (Asymmetry)**    | $P(x) = x^2$; baseline > 2.25× gain         |
| **Whistleblowing**         | Reporting agent rewarded; violator punished |

### 7.2 Countering Gambler's Fallacy

**Bayesian Inspection Updates:**

- Standard: If detected → punish
- QoreLogic: If detected → punish **AND** increase sampling rate for next N periods

### 7.3 Explicit Signaling

- Threat of punishment **explicitly communicated** via API
- Sentinel daemon **visible** to monitored agent
- "Showing the police officer" increases compliance more than hidden monitoring

### 7.4 Temporal Circuit Breakers

- Any agent triggering "Hot State" alert → automatic 48-cycle Cooling-Off
- Hard-stop prevents cascading failures

---

## 8. Conclusion

The optimal QoreLogic configuration:

- **High-Inspection (HILS)** environment
- **Asymmetric, convex penalties** (λ ≈ 2.25×)
- **Temporal circuit breakers** (24-48h cooling-off)
- **Probationary probability shift** after violations

> "Severity is a weak lever compared to certainty. Losses loom larger than gains. Cooling off is sometimes more powerful than acting immediately."

---

## References

[BEHAV-001] Becker, G. (1968). "Crime and Punishment: An Economic Approach." Journal of Political Economy.  
[BEHAV-002] Nagin, D. (2013). "Deterrence in the Twenty-First Century." Crime and Justice.  
[BEHAV-003] Kahneman, D. & Tversky, A. (1979). "Prospect Theory." Econometrica.  
[BEHAV-004] Tversky, A. & Kahneman, D. (1992). "Advances in Prospect Theory." Journal of Risk and Uncertainty.  
[BEHAV-005] Simon, H. (1955). "A Behavioral Model of Rational Choice." Quarterly Journal of Economics.  
[BEHAV-006] Nagin, D. et al. "High Inspection, Low Severity Experiments."  
[BEHAV-007] CrowdStrike. "100% Detection Capabilities."  
[BEHAV-008] Asylum Judge Decision Patterns Study.  
[BEHAV-009] Resetting Effect in Recidivism Research.  
[BEHAV-010] Hot-Cold Empathy Gap Literature.  
[BEHAV-011] Cooling-Off Periods in Labor Relations.
