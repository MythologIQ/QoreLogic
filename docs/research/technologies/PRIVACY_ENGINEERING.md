# Privacy Engineering Research Document

**Version:** 1.0  
**Created:** December 18, 2025  
**Status:** Complete  
**Purpose:** Differential privacy and PII handling for Q-DNA audit systems  
**Cross-Reference:** Q-DNA Spec §10 (Privacy), §10.3 (ε Budget)

---

## 1. Executive Summary

Q-DNA adopts **Differential Privacy (DP)** as its sole metric for privacy preservation. Traditional anonymization (k-anonymity, l-diversity, masking) has been systematically defeated by reconstruction and membership inference attacks. This document specifies:

- DP implementation with ε budget management
- PII detection and redaction architectures
- Local-first sovereignty principles

**Key Claims Substantiated:**

| Claim                                                | Evidence                                       |
| ---------------------------------------------------- | ---------------------------------------------- |
| Starting ε=2.0 per 24h balances privacy with utility | Apple Health: ε=2 (strictest), Census: ε≈19.61 |
| e²≈7.38 bound provides meaningful protection         | Privacy loss guarantee mathematics             |
| PII redaction must occur BEFORE logging              | "Redact-at-Edge" eliminates attack surface     |

---

## 2. Differential Privacy Foundations

### 2.1 The Definition

A randomized mechanism $\mathcal{M}$ satisfies $(\epsilon, \delta)$-differential privacy if for all neighboring datasets $D_1$, $D_2$:

$$\Pr[\mathcal{M}(D_1) \in S] \le e^{\epsilon} \cdot \Pr[\mathcal{M}(D_2) \in S] + \delta$$

### 2.2 Parameters

| Parameter       | Meaning                               | Q-DNA Constraint            |
| --------------- | ------------------------------------- | --------------------------- |
| **ε (epsilon)** | Privacy budget / maximum privacy loss | Lower = stronger protection |
| **δ (delta)**   | Probability of complete failure       | Must be < 10⁻⁶ for PII      |

### 2.3 Privacy Mechanisms

| Mechanism       | Use Case                   | Formula                                            |
| --------------- | -------------------------- | -------------------------------------------------- |
| **Laplace**     | Numeric queries, Pure ε-DP | $f(D) + \text{Lap}(\Delta f/\epsilon)$             |
| **Gaussian**    | Vector queries, (ε,δ)-DP   | $f(D) + \mathcal{N}(0, \sigma^2)$                  |
| **Exponential** | Selection from set         | $\Pr[r] \propto \exp(\epsilon u(D,r) / 2\Delta u)$ |

### 2.4 Key Properties

- **Post-Processing Invariance:** DP output can be processed without increasing privacy loss
- **Sequential Composition:** $k$ mechanisms with budgets $\epsilon_1...\epsilon_k$ → total loss $\sum \epsilon_i$

---

## 3. Industry Benchmarks

### 3.1 Apple Local Differential Privacy

| Feature           | ε Value   | Contribution Limit |
| ----------------- | --------- | ------------------ |
| Health Type Usage | **ε = 2** | 1/day              |
| Emoji Suggestions | ε = 4     | -                  |
| Lookup Hints      | ε = 4     | 2/day              |
| Safari Energy     | ε = 4     | -                  |
| Safari Autoplay   | ε = 8     | -                  |
| QuickType         | ε = 8-16  | -                  |

**Key Insight:** Budget resets **daily** ("User-Day" privacy unit).

### 3.2 US Census 2020

| Category         | ε Allocation  |
| ---------------- | ------------- |
| Person File      | **ε = 17.14** |
| Housing Unit     | ε = 2.47      |
| **Total Global** | **ε = 19.61** |

**Reconstruction Attack:** 2010 Census data reconstructed 46% of US population using only public tables. Proved anonymization is dead.

### 3.3 Google Evolution

| System  | Status     | Mechanism                                   |
| ------- | ---------- | ------------------------------------------- |
| RAPPOR  | Deprecated | Bloom Filters + Randomized Response         |
| Prochlo | Current    | Shuffle Model (ESA: Encode-Shuffle-Analyze) |
| Cobalt  | Current    | Updated aggregation protocols               |

**Amplification by Shuffling:** LDP ε=5 → Central ε=0.5 after shuffling millions of reports.

---

## 4. Privacy Budget Management

### 4.1 Blocking Thresholds

```
IF Current_Budget + Query_Cost > Max_Budget:
    RETURN "NOISE_BUDGET_EXHAUSTED"
    BLOCK query execution
```

### 4.2 Sliding Window Accounting

- **Window (W):** Privacy guarantees maintained for events within window (e.g., 30 days)
- **Reclamation:** Data older than W expires from active budget calculation
- Enables perpetual monitoring without lifetime budget exhaustion

### 4.3 Floating Point Vulnerabilities

**The Attack:** IEEE 754 floating-point discretization can leak information about impossible values.

**Mandated Mitigation:**

- Use OpenDP or Google DP Library
- Secure noise generation algorithms
- Discrete Gaussian distributions

---

## 5. PII Detection Architecture

### 5.1 Microsoft Presidio Coverage

| Category             | Entities                              |
| -------------------- | ------------------------------------- |
| **Global Financial** | Credit Cards, Crypto Wallets, IBAN    |
| **Digital Identity** | Email, IP Address, URL                |
| **US Specific**      | SSN, Driver's License, ITIN, Passport |
| **UK Specific**      | NHS Number, NINO                      |
| **EU Specific**      | Driver's Licenses, Tax IDs            |

**Context-Aware Recognition:** Boost confidence only when context words ("Social Security", "SSN") appear in proximity.

### 5.2 Algorithmic Validation

| Check           | Algorithm                 | Purpose                                    |
| --------------- | ------------------------- | ------------------------------------------ |
| **Credit Card** | Luhn checksum             | Distinguish from timestamps/UUIDs          |
| **NPI**         | Luhn with "80840" prefix  | Distinguish from phone numbers             |
| **Email**       | RFC 5322 + TLD validation | Avoid triggering on code (`object.method`) |

#### Luhn Algorithm

```python
def luhn_check(number: str) -> bool:
    digits = [int(d) for d in number]
    for i in range(len(digits)-2, -1, -2):
        digits[i] *= 2
        if digits[i] > 9:
            digits[i] -= 9
    return sum(digits) % 10 == 0
```

### 5.3 High-Latency InfoTypes

| InfoType    | Latency | Handling             |
| ----------- | ------- | -------------------- |
| PERSON_NAME | High    | Async post-ingestion |
| LOCATION    | High    | Async post-ingestion |
| CREDIT_CARD | Low     | Real-time blocking   |

---

## 6. Data Minimization Strategies

### 6.1 Redact-at-Edge (Mandatory)

| Approach                   | Risk                      | Status      |
| -------------------------- | ------------------------- | ----------- |
| Store raw → nightly scrub  | High (privacy gap window) | ❌ REJECTED |
| Redact at ingestion stream | Minimal surface area      | ✅ MANDATED |

### 6.2 Transformation Techniques

| Technique          | Implementation        | Use Case           | Risk                           |
| ------------------ | --------------------- | ------------------ | ------------------------------ |
| **Hashing**        | SHA-256(PII + Salt)   | Unique user counts | Dictionary attacks if unsalted |
| **Masking**        | `****-****-****-1234` | Debug logs         | Partial leakage                |
| **Tokenization**   | UUID + Vault          | Legal retention    | Central point of failure       |
| **Generalization** | Age 20-30             | ML training        | Reduced precision              |
| **Suppression**    | `<REDACTED>`          | Audit logs         | Zero utility                   |

### 6.3 Audit Log Sanitization

- **Exception Sanitization:** Remove variable values from stack traces
- **Structured Logging:** Separate "Message" from "Context"
- **Sovereign Logging:** Encrypt with public key; system cannot read own logs

---

## 7. Local-First Architecture

### 7.1 Local Inference (Ollama/Llama.cpp)

- **Privacy Air Gap:** Data never leaves user infrastructure
- **Privacy Firewall:** Block outbound traffic from inference container
- **Thinking Mode Logs:** Store Chain of Thought locally, encrypted

### 7.2 Federated Learning + LDP

1. Client downloads global model
2. Trains on local data
3. Clips gradients, adds Gaussian noise (LDP)
4. Sends only noisy gradients to server
5. Server aggregates thousands of noisy updates

**Trust Model:** Server never sees training examples.

---

## 8. Q-DNA Mandates

| Category         | Mandate                                                  |
| ---------------- | -------------------------------------------------------- |
| **Budgeting**    | Track ε per query; cap < 20 aggregate, < 5 user-specific |
| **Accounting**   | Use OpenDP; enforce sliding window                       |
| **Detection**    | Presidio + Luhn/NPI validation + context-aware           |
| **Architecture** | Local-first default; redact at edge; sovereign keys      |
| **δ Constraint** | Must be < 10⁻⁶ for any PII mechanism                     |

---

## References

[PRIV-001] Dwork, C. & Roth, A. "The Algorithmic Foundations of Differential Privacy."  
[PRIV-002] Apple. "Differential Privacy Technical Overview."  
[PRIV-003] US Census Bureau. "2020 Disclosure Avoidance System."  
[PRIV-004] Google. "RAPPOR: Randomized Aggregatable Privacy-Preserving Ordinal Response."  
[PRIV-005] Google. "Prochlo: Strong Privacy for Analytics in the Crowd."  
[PRIV-006] Microsoft. "Presidio: Data Protection and Anonymization SDK."  
[PRIV-007] OpenDP. "The OpenDP Programming Framework."  
[PRIV-008] NIST SP 800-188. "De-Identification of Personal Information."  
[PRIV-009] Narayanan, A. & Shmatikov, V. "Robust De-anonymization of Large Sparse Datasets."
