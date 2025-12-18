# Hallucination Rates in Large Language Models

**Version:** 1.0  
**Created:** December 18, 2025  
**Status:** Complete  
**Purpose:** Establishing error baselines for Generative AI in critical decision-making  
**Cross-Reference:** Q-DNA Spec §9 (ML-Dependent Verification), §9.2 (Diversity Quorum)

---

## 1. Executive Summary

Generative AI faces an epistemological crisis: "hallucination." This document establishes a **18-50% hallucination rate spectrum** based on SOTA benchmarks (HaluEval, TruthfulQA). While scaling improves fluency, it does not eliminate the "reliability floor" of ~18% for complex tasks, necessitating hybrid architectures (RAG + Formal Verification) and human-in-the-loop oversight.

**Key Claims Substantiated:**

| Claim                                            | Evidence                                         |
| ------------------------------------------------ | ------------------------------------------------ |
| SOTA models exhibit a ~18% hallucination floor   | HaluEval-Wild (GPT-4): 18.64%                    |
| Reasoning complexity acts as an error multiplier | HotpotQA (Multi-hop): GPT-4=28%, Llama-3=~55%    |
| Medical citation fabrication rate is ~20%        | Domain study on GPT-4o mental health lit reviews |
| Larger models can be "better liars"              | TruthfulQA inverse scaling law (GPT-3 era)       |

---

## 2. Taxonomy of Hallucination

### 2.1 Error Classification

| Type                              | Origin               | Definition                                                                    |
| --------------------------------- | -------------------- | ----------------------------------------------------------------------------- |
| **Fact-Conflicting (Intrinsic)**  | Parametric Memory    | Contradicts established world knowledge. Driven by training data compression. |
| **Input-Conflicting (Extrinsic)** | Contextual Grounding | Contradicts provided prompt/context (e.g., RAG failure or summary error).     |

### 2.2 The "Siren's Song" Etiology (Li et al.)

- **Data Stage:** Training on misinformation/satire ("Garbage in, garbage out").
- **Training Stage:** Optimizing for _imitation_ of human text rather than truth.
- **Inference Stage:** Stochastic decoding (high temperature) prioritizes creativity over factuality.
- **Alignment Stage:** RLHF induces "sycophancy"—agreeing with false user premises to maximize rewards.

---

## 3. Benchmarking Frameworks

### 3.1 HaluEval (Hallucination Evaluation)

Industrialized detection using 35,000 samples.

- **Methodology:** "Sampling-then-Filtering" using LLMs to generate plausible, subtle fabrications.
- **The "Detection Gap":** Models are poor judges of their own hallucinations without external context.

### 3.2 TruthfulQA (Imitative Falsehoods)

Measures if models mimic popular human misconceptions (e.g., "sugar causes hyperactivity").

- **Inverse Scaling:** Larger models historically scored _lower_ on truthfulness because they were better at learning the distribution of common internet myths.
- **Status (2025):** SOTA models (Claude 3.5) are finally breaking this law, but open-source models still lag.

---

## 4. The 18-50% Reliability Spectrum

Synthesis of 2024-2025 data across unconstrained "in-the-wild" queries:

| Model             | Hallucination Rate | Tier                 |
| ----------------- | ------------------ | -------------------- |
| **GPT-4 Turbo**   | **18.64%**         | SOTA (The 18% Floor) |
| **GPT-3.5 Turbo** | 35.47%             | Commercial Legacy    |
| **Mixtral 8x7B**  | 51.51%             | High-end Open Weight |
| **Mistral 7B**    | 57.43%             | Standard Open Weight |

---

## 5. Domain Failure Modes

| Domain            | Failure Mode         | Impact                                                                    |
| ----------------- | -------------------- | ------------------------------------------------------------------------- |
| **Medical**       | Citation Fabrication | **19.9% fabrication rate**; 45.4% bibliographic errors.                   |
| **Legal**         | Case Law Mirage      | Inventing plausible-sounding but fictitious cases.                        |
| **Code**          | Non-Existent APIs    | **19.7% package hallucinations**; creates "typosquatting" security risks. |
| **Summarization** | Topic Inconsistency  | 44% - 79% hallucination rate in high-entropy settings.                    |

---

## 6. Detection and Mitigation

### 6.1 Probabilistic: Self-Consistency

Sample $k$ diverse outputs and use majority voting.

- **Assumption:** There are many ways to be wrong, but usually one way to be right.
- **Failure Mode:** "Consistent hallucinations" where a model is certain about a falsehood.

### 6.2 Deterministic: Formal Verification (PyVeritas)

Transpiling Python to C to use **CBMC (C Bounded Model Checker)**.

- **Result:** Proof of correctness rather than probabilistic confidence.
- **Success:** LLM-based transpilation achieves 80-90% semantic faithfulness for verification.

### 6.3 Architectural: RAG

Retrieval Augmented Generation converts "open-book" memory tasks into "reading comprehension."

- **Current Issue:** "Faithfulness" failures—ignoring or misinterpreting the source.

---

## 7. Q-DNA Strategic Mandate

No LLM can be deployed as a standalone source of truth. Q-DNA architecture must be hybrid:

1. **RAG** for knowledge grounding.
2. **Diversity Quorum** (Multiple Models) for consensus validation.
3. **Formal Verification** (PyVeritas) for critical code/logic.
4. **Human-in-the-Loop** an irreducible requirement for high-stakes decisions.

---

## References

[HALU-001] Li et al. (2023). "Siren’s Song in the AI Ocean: A Survey on Hallucination in Large Language Models."  
[HALU-002] Li et al. (2023). "HaluEval: A Large-Scale Hallucination Evaluation Benchmark."  
[HALU-003] Lin et al. (2022). "TruthfulQA: Measuring How Models Mimic Human Falsehoods."  
[HALU-004] Domain study (2024). "Fabricated Citations in Mental Health Research via GPT-4o."  
[HALU-005] Wang et al. (2023). "Self-Consistency Improves Chain of Thought Reasoning."  
[HALU-006] PyVeritas (2024). "Formal Verification of Python Code via LLM Transpilation."  
[HALU-007] HaluEval-Wild Benchmark Data (2024-2025).
