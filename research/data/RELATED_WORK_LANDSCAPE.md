# Related Work Landscape

**Status:** Comparative Analysis
**Purpose:** Position Q-DNA against existing state-of-the-art research in AI safety, formal verification, and code generation.

## 1. The "Small Model" Reasoning Revolution

Q-DNA's hypothesis that small, specialized agents (Sentinel) can outperform large monolithic models on specific logic tasks is supported by recent breakthroughs.

| Project           | Architecture                | Size        | Key Finding                                                    | Relevance to Q-DNA                                                        |
| :---------------- | :-------------------------- | :---------- | :------------------------------------------------------------- | :------------------------------------------------------------------------ |
| **Sapient HRM**   | Recurrent (Hierarchical)    | **27M**     | Outperformed GPT-4 (Trillions) on ARC-AGI & Sudoku.            | Validates **Study 003**: Micro-Agents can handle L3 logic checks.         |
| **Microsoft Phi** | Transformer (Textbook Data) | 1.3B - 2.7B | Match performance of 100x larger models via high-quality data. | Supports **Gen 0 Strategy**: Quality of constraints > Quantity of params. |
| **Google Orca**   | Progressive Learning        | 13B         | Learn reasoning traces from GPT-4.                             | Justifies training Sentinel on "Negative Constraints" from larger models. |

## 2. Formal Verification in AI

Q-DNA moves formal verification from "Post-Hoc Analysis" to "Real-Time Gatekeeping".

| Project                        | Focus          | Methodology                            | Gap Filled by Q-DNA                                                   |
| :----------------------------- | :------------- | :------------------------------------- | :-------------------------------------------------------------------- |
| **Astrogator**                 | Code Gen       | Formal Query Language for user intent. | Q-DNA adds **Traceability** (Hash Chains) to the verification.        |
| **Saarthi**                    | Hardware (RTL) | Autonomous Verification Engineer.      | Q-DNA applies this rigour to **General Software**, not just hardware. |
| **Microsoft "Trusted Agents"** | General        | Spec generation & test synthesis.      | Q-DNA adds the **Judge/Enforcement Agent** (Accountability).          |

## 3. Evolutionary Coding & The Shadow Genome

How Q-DNA's "Fail Forward" differs from standard evolutionary algorithms.

| Approach      | Typical Strategy (e.g., AlphaEvolve)   | Q-DNA Strategy                                                        |
| :------------ | :------------------------------------- | :-------------------------------------------------------------------- |
| **Selection** | Select for Success (Fitness Function). | Select for **Failure Modes** (Sentinel Training).                     |
| **Memory**    | Discard failed candidates.             | **Shadow Genome:** Archive `FailureContext` for future compatibility. |
| **Goal**      | Optimization of _Code_.                | Optimization of _The System That Writes Code_ (Autopoiesis).          |

## 4. The Novelty Gap

While individual components (HRM, Verification, Agents) exist in isolation, Q-DNA is unique in combining them into a **Governance Architecture**:

- **Unique Traceality:** No other framework explicitly archives "Negative compatibility" (Shadow Genome).
- **Unique Enforcement:** The AAC provides a "Constitution" that overrides the Agent's objective function.
