# Information Theory Research Document

**Version:** 1.0  
**Created:** December 18, 2025  
**Status:** Complete  
**Purpose:** Citation depth, information decay, and provenance tracking  
**Cross-Reference:** QoreLogic Spec §5.2 (Citation Policy), §5.4 (TTL)

---

## 1. Executive Summary

Information degrades as it traverses citation chains. This document establishes the theoretical constraints on citation fidelity using Shannon's Data Processing Inequality, quantifies the "Telephone Effect" in academic networks, and defines cryptographic provenance standards for the QoreLogic project.

**Key Claims Substantiated:**

| Claim                                                       | Evidence                                                    |
| ----------------------------------------------------------- | ----------------------------------------------------------- |
| Citation depth ≤2 from primary source maintains reliability | Data Processing Inequality + 0.94 decay coefficient per hop |
| Quote context (±200 chars) prevents misrepresentation       | Fair use heuristics + journalism standards                  |
| 30-day TTL for technical content reflects domain volatility | Industry consensus (API deprecation, financial staling)     |

---

## 2. The Data Processing Inequality

### 2.1 Shannon's Constraint on Transitive Trust

For a Markov chain $U \rightarrow X \rightarrow Y$:

- $U$ = ground truth
- $X$ = primary source
- $Y$ = derived work

**The Data Processing Inequality states:**
$$I(U; Y) \leq I(U; X)$$

No processing at node $Y$ can increase information about $U$ beyond what $X$ transmitted.

**Strong DPI:** The inequality is often strict: $I(U; Y) < I(U; X)$

**Implication:** A secondary citation ($Z$ where $X \rightarrow Y \rightarrow Z$) is mathematically guaranteed to contain **equal or less** information about the original source.

### 2.2 Stochastic Decay in Summarization

In recursive summarization chains:
$$I(X; Y_{i+1}) = I(X; Y_i) - \delta_i$$

Where $\delta_i$ increases with:

- Finite model capacity
- High-temperature sampling ($\tau > 0$)

**Conclusion:** "Creative" summarization is structurally antagonistic to truth preservation. Prioritize low-temperature processing (verbatim extraction, deterministic hashing).

---

## 3. The Telephone Effect

### 3.1 Quantifying Fidelity Decay

| Factor                             | Effect on Fidelity                |
| ---------------------------------- | --------------------------------- |
| Each citation hop                  | **-0.06 normalized coefficient**  |
| Senior first author (high H-index) | Negative correlation              |
| Medium-sized teams                 | Highest fidelity                  |
| Intellectual distance              | Higher distance → faster drift    |
| Temporal distance                  | Older papers → lower fidelity     |
| Verbosity                          | Longer sentences → lower fidelity |

### 3.2 Error Amplification

Errors are **transitive and sticky**:

- Strong positive correlation between intermediary fidelity and subsequent fidelity
- If $Y$ misinterprets $X$, $Z$ reproduces the misinterpretation
- Creates "cascading effect of information distortion"

### 3.3 Morphological Distortion

Claims transform as they propagate:

- Complex conditional claims → stripped of conditions
- Nuanced statements → exaggerated into "received wisdom"
- "Too good to check" myths emerge

---

## 4. Chronobiology of Information

### 4.1 Link Rot Rates

| Domain          | Decay Rate            | Half-Life  |
| --------------- | --------------------- | ---------- |
| Social Media    | ~20% vanish in months | < 3 months |
| News/Media      | 23% broken links      | 2-5 years  |
| Government      | 21% broken links      | 5-10 years |
| Legal Citations | 31% inaccessible      | 5-10 years |
| Academic        | 66.5% rot (1997-2012) | > 20 years |

**Key Finding:** 25% of 2013 webpages inaccessible by 2023.

### 4.2 Content Drift

More insidious than 404:

- URL remains valid (HTTP 200)
- Semantic payload changes
- Citation becomes false yet technically functional

**High-drift domains:**

- Software documentation (monthly release cycles)
- Financial data (millisecond freshness)
- Government policy pages

### 4.3 TTL Policy: The 30-Day Standard

| Context           | 30-Day Evidence                  |
| ----------------- | -------------------------------- |
| API Deprecation   | Salesforce, Genesys, GitHub bots |
| Financial Staling | Checks, warrants                 |
| Domain Redemption | 30 days after expiration         |
| Market Volatility | Rolling 30-day window            |

**Recommendation:** Assign 30-day stale date to unversioned Tech/Financial/Social resources.

---

## 5. Quote Context Heuristics

### 5.1 Fair Use Quantitative Standards

| Context             | Limit                      | Source                  |
| ------------------- | -------------------------- | ----------------------- |
| Commercial excerpts | **50 words**               | NYT enforcement         |
| TDM snippets        | **200 characters**         | Elsevier                |
| Academic aggregate  | 300 words total per source | Publishing guidelines   |
| Endorsement quotes  | 1-2 sentences              | University style guides |

### 5.2 "Heart of the Work" Doctrine

Quantitative limits are necessary but not sufficient:

- 10 words of "core revelation" may void fair use
- Prioritize **transformative use** (evidence for claim, not substitute for reading)

### 5.3 Journalism Standards

| Requirement         | Standard                             |
| ------------------- | ------------------------------------ |
| Quote alterations   | Forbidden (even grammar corrections) |
| Contextual brackets | Permitted but discouraged            |
| Context buffer      | ±200 characters to determine intent  |

**QoreLogic Atomic Unit:** Maximum 50 words or 2 sentences, whichever is shorter.

---

## 6. Cryptographic Provenance Standards

### 6.1 Comparative Analysis

| Feature      | W3C PROV           | C2PA            | Signed Citations              |
| ------------ | ------------------ | --------------- | ----------------------------- |
| Primary Goal | Metadata           | Tamper-Evidence | Persistence                   |
| Binding      | None (descriptive) | Hard + Soft     | Hard (hash)                   |
| Text Support | Native (RDF)       | External/PDF    | Native (embedded)             |
| Best For     | Derivation history | Media identity  | Scientific data               |
| Weakness     | No security        | Complex PKI     | Requires hash-aware retrieval |

### 6.2 C2PA Binding Types

- **Hard Binding:** Cryptographic hash of bitstream
- **Soft Binding:** Perceptual hash/watermark for format shifts

### 6.3 Signed Citations

- Content signature (SHA-256) at moment of citation
- Location agnostic (data movable, still verifiable)
- Embedded in content for self-verifying graphs

---

## 7. QoreLogic Protocol Recommendations

### 7.1 Zero-Hop Mandate

| Rule                          | Implementation                             |
| ----------------------------- | ------------------------------------------ |
| Reject intermediary citations | Resolve to canonical source                |
| Fidelity penalty              | **0.94 decay per hop**                     |
| Redundancy priority           | Multiple independent chains to same source |

### 7.2 Provenant Object Structure

```
{
  "payload": "<50 words",
  "context_buffer": "±200 chars (hidden)",
  "hash": "SHA-256",
  "manifest": "C2PA/PROV-O sidecar",
  "stale_date": "calculated by domain"
}
```

### 7.3 Drift Defense Protocol

1. **Re-Hash:** Fetch live URL, generate new hash
2. **Compare:**
   - Match → Extend TTL
   - Mismatch → Flag "DRIFT_DETECTED"
3. **Fallback:** Query Wayback Machine (~90% retrieval rate)

---

## References

[INFO-001] Shannon, C. (1948). "A Mathematical Theory of Communication."  
[INFO-002] Cover, T. & Thomas, J. "Data Processing Inequality."  
[INFO-003] Tishby, N. "Information Bottleneck Method."  
[INFO-004] Pew Research Center (2024). "Web Decay Analysis."  
[INFO-005] Bibliometric Citation Fidelity Studies.  
[INFO-006] AP Stylebook. Quote Handling Standards.  
[INFO-007] U.S. Copyright Law, Title 17, Section 107.  
[INFO-008] W3C PROV Specification.  
[INFO-009] C2PA Technical Specification.  
[INFO-010] Signed Citations for Scientific Data.
