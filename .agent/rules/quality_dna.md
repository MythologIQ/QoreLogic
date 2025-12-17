---
description: Quality DNA Definitions (The Genetic Code)
---

# Quality DNA

This file defines the **Base DNA** constraints for all Q-DNA agents. These are the immutable traits that the system seeks to replicate and protect.

## 1. Traceability (The Hash Chain)

- **Trait:** Every logical step in an artifact generation must be hashed.
- **Constraint:** `hash(step_n) == hash(step_n-1 + content_n)`.
- **Enforcement:** Sentinel Agent rejects any chain with broken hashes.

## 2. Privacy (The Identity)

- **Trait:** Zero Raw PII.
- **Constraint:** All PII input must be passed through the `RedactionFilter` before entering Agent Memory.
- **Enforcement:** Judge Agent audits memory for RegEx matches of PII patterns (SSN, Email, etc.).

## 3. Resilience (The Immune System)

- **Trait:** Self-Correction.
- **Constraint:** Any agent error > 0.2 calibration error triggers the **Honest Error Track** (Retraining/Context Clearing).
- **Enforcement:** Judge Agent monitors `CalibrationScore`.

## 4. Complexity (The Efficiency)

- **Trait:** Simplicity.
- **Constraint:** Cyclomatic Complexity per function <= 10.
- **Enforcement:** Sentinel Agent runs `lizard` or `radon` complexity checks.
