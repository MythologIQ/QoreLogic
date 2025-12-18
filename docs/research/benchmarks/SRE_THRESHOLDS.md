# SRE Thresholds: Operational Governance

**Version:** 1.0  
**Created:** December 18, 2025  
**Status:** Complete  
**Purpose:** Defining operational boundaries, resource limits, and failure response protocols  
**Cross-Reference:** Q-DNA Spec §3.3 (Operational Modes), §12 (Metrics)

---

## 1. Executive Summary

Q-DNA transitions from ad-hoc monitoring to mathematically derived governance. This document defines "goodput" preservation under saturation using Error Budgets, utilization thresholds (70% CPU rule), and concurrency bulkheads. It balances innovation velocity against system stability using SRE methodologies.

**Key Claims Substantiated:**

| Claim                                        | Evidence                                          |
| -------------------------------------------- | ------------------------------------------------- |
| Error Budgets drive development velocity     | rolling 28-day window ($1 - \text{SLO}$)          |
| CPU saturation "knee" occurs at ~70%         | Queueing theory (M/M/1 wait-time asymptotics)     |
| Latency degradation is functionality failure | AI-specific SLIs for correctness and freshness    |
| LIFO preserves goodput during overload       | Newest-first processing prevents timeout cascades |

---

## 2. Service Level Architecture

### 2.1 The SLI/SLO/SLA Hierarchy

- **SLI (Indicator):** Quantitative measure (e.g., Latency, Correctness).
- **SLO (Objective):** Internal target (e.g., 99.9% availability).
- **SLA (Agreement):** External contract with consequences (e.g., 99.5% availability).

### 2.2 Error Budget Governance

- **Budget = 1 - SLO.**
- **Remaining Budget:** Teams push features at maximum velocity.
- **Exhausted Budget:** Engineering shifts entirely to reliability/technical debt (Launch Freeze).

---

## 3. Quantitative Resource Thresholds

### 3.1 The 70% CPU Rule ("The Knee")

- **Warning State (>70%):** Exponential increase in queue probability. Scale out immediately.
- **Critical State (>80%):** System in "death spiral." Drop requests (Load Shedding).
- **Saturation Failure (100%):** Context switching/thrashing reduces effective throughput.

### 3.2 Memory and Storage

- **Memory Warning (80%):** Buffer for incompressible OOM killer protection.
- **Storage Headroom (25%):** Insurance against log growth and fragmentation (ext4/xfs).
- **N+1 Overcapacity:** Mandatory 25% site/cluster buffer to absorb single-node failure without breach.

---

## 4. Concurrency and Queue Management

### 4.1 Little's Law ($L = \lambda W$)

- **Concurrency Cap:** Set at 50 requests per instance for standard inference (250 RPS @ 200ms latency).
- **Bulkheads:** Hard concurrency limits to prevent thread contention from degrading throughput.

### 4.2 Queue Disciplines

- **FIFO (Normal):** Ensures fairness.
- **LIFO (Saturation):** Switches to newest-first when queue depth >80%. Older requests are shed as they likely timed out on the client side.
- **CoDel:** Adaptive management to decrease "bufferbloat" at ingress layers.

---

## 5. Survival Mechanisms (Backpressure)

- **HTTP 429 (Rate Limit):** Client-specific quota breach.
- **HTTP 503 (Load Shedding):** Global server overload.
- **Retry-After Header:** Mandated with **Jitter** to desynchronize the "thundering herd."
- **Criticality Tiers:** Systematically shed SHEDDABLE (analytics/pre-fetch) before CRITICAL (login/inference) traffic.

---

## 6. AI FinOps (Economic Governance)

- **Cost Per Inference:** Primary KPI connection to COGS (Cost of Goods Sold).
- **Model Serving Efficiency:** ROI of accuracy (cost vs. F1-score).
- **Orphan Sweeps:** Daily termination of idle GPUs (>24h).
- **Spot Instances:** Mandated for non-critical batch training (up to 90% savings).

---

## References

[SRE-001] Google. "Site Reliability Engineering: How Google Runs Production Systems."  
[SRE-002] Little, J.D.C. (1961). "A Proof for the Queuing Formula $L = \lambda W$."  
[SRE-003] FinOps Foundation. "FinOps for AI and Machine Learning."  
[SRE-004] NVIDIA Documentation. "Multi-Instance GPU (MIG) User Guide."  
[SRE-005] RFC 6585. "Additional HTTP Status Codes" (429 Too Many Requests).
