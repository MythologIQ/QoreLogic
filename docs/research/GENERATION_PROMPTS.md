# QoreLogic Research Document Generation Prompts

Use these prompts with a research-capable LLM to generate the pending documentation.

---

## 1. FORMAL_METHODS.md

```
Generate a research document for the QoreLogic project titled "FORMAL_METHODS.md" that covers formal verification theory for code verification systems.

Required content:
- Historical foundations: Hoare Logic, Dijkstra's weakest precondition calculus
- Bounded Model Checking (BMC): CBMC, ESBMC, their accuracy rates and limitations
- Symbolic execution: theory and practical tools (KLEE, CrossHair)
- Design-by-Contract: principles and the `deal` library for Python
- Integration with Z3 SMT solver
- Practical scope limitations of formal methods (what CAN'T be verified)

Format requirements:
- Use citation format: [FM-001], [FM-002], etc.
- Include a References section with DOIs where available
- Cross-reference to QoreLogic Spec sections: §3 (Sentinel), §13 (Implementation)
- Target length: 800-1200 words

Key claims to substantiate:
- "PyVeritas achieves 80-90% accuracy on formal verification"
- Bounded model checking with 5-10 step bounds catches common errors
```

---

## 2. BEHAVIORAL_ECONOMICS.md

```
Generate a research document for the QoreLogic project titled "BEHAVIORAL_ECONOMICS.md" covering deterrence theory and incentive design for AI governance.

Required content:
- Nagin's HILS (High Inspection/Low Severity) vs LIHS model
- Becker's rational crime model and its limitations
- Kahneman/Tversky on loss aversion (losses hurt 2x gains)
- Asymmetric penalty structures: why failures should hurt more than successes help
- Cooling-off periods: psychological research on reducing retaliation
- "Gambler's Fallacy" in risk-seeking behavior when detection is low

Format requirements:
- Use citation format: [BEHAV-001], [BEHAV-002], etc.
- Include a References section with DOIs where available
- Cross-reference to QoreLogic Spec sections: §9 (Remediation), §5.3.3 (Adjustment Formula)
- Target length: 800-1200 words

Key claims to substantiate:
- HILS creates tighter feedback loops than LIHS
- 100% detection of minor infractions prevents risk-seeking behavior
- Cooling-off periods (24-48h) reduce retaliation cycles
```

---

## 3. INFORMATION_THEORY.md

```
Generate a research document for the QoreLogic project titled "INFORMATION_THEORY.md" covering citation depth, information decay, and provenance tracking.

Required content:
- Shannon's information theory basics relevant to citation chains
- Bibliometric research on citation depth and reliability degradation
- Transitive information loss (why "cited by someone who cited" loses fidelity)
- Quote context requirements (±2 sentences) from journalism standards
- Temporal decay of information value (domain ownership volatility, content drift)
- Provenance chains and their cryptographic verification

Format requirements:
- Use citation format: [INFO-001], [INFO-002], etc.
- Include a References section with DOIs where available
- Cross-reference to QoreLogic Spec sections: §5.2 (Citation Policy), §5.4 (TTL)
- Target length: 600-1000 words

Key claims to substantiate:
- Citation depth ≤2 from primary source maintains reliability
- Quote context (±200 chars) prevents misrepresentation
- 30-day TTL for technical content reflects domain volatility
```

---

## 4. PRIVACY_ENGINEERING.md

```
Generate a research document for the QoreLogic project titled "PRIVACY_ENGINEERING.md" covering differential privacy and PII handling for AI audit systems.

Required content:
- Dwork's differential privacy foundations (ε definition, guarantees)
- Industry benchmarks: Apple (ε=2-16), US Census 2020 (ε≈19.1), Google RAPPOR
- ε budget management: consumption, refresh, and blocking thresholds
- PII detection patterns: SSN, email, credit card, medical identifiers
- Data minimization: hashes vs raw content storage
- Local-first privacy: why sovereignty matters for audit logs

Format requirements:
- Use citation format: [PRIV-001], [PRIV-002], etc.
- Include a References section with DOIs where available
- Cross-reference to QoreLogic Spec sections: §10 (Privacy), §10.3 (ε Budget)
- Target length: 800-1200 words

Key claims to substantiate:
- Starting ε=2.0 per 24h balances privacy with utility
- e²≈7.38 bound provides meaningful protection
- PII redaction must occur BEFORE logging (not after)
```

---

## 5. CRYPTOGRAPHIC_STANDARDS.md

```
Generate a research document for the QoreLogic project titled "CRYPTOGRAPHIC_STANDARDS.md" covering key management and digital signing for audit integrity.

Required content:
- NIST SP 800-57 key management recommendations
- Ed25519 signature algorithm: why chosen over RSA/ECDSA
- Key rotation requirements: 30-day cycles, compromise recovery
- Merkle chain integrity: hash linking for append-only logs
- DID (Decentralized Identifier) format and W3C standards
- Local encrypted keyfile storage best practices

Format requirements:
- Use citation format: [CRYPTO-001], [CRYPTO-002], etc.
- Include a References section with DOIs where available
- Cross-reference to QoreLogic Spec sections: §10.2 (Identity), §11 (SOA Ledger)
- Target length: 600-1000 words

Key claims to substantiate:
- Ed25519 provides 128-bit security with compact signatures
- 30-day key rotation balances security with operational overhead
- Merkle chains provide tamper-evidence for audit logs
```

---

## 6. DISCLOSURE_STANDARDS.md

```
Generate a research document for the QoreLogic project titled "DISCLOSURE_STANDARDS.md" covering vulnerability disclosure timing and responsible disclosure practices.

Required content:
- CERT/CC coordinated vulnerability disclosure guidelines
- Google Project Zero 90-day policy and its rationale
- Staged disclosure: acknowledgment (24h), triage (7d), remediation (83d)
- Deferral windows by risk type: safety-critical vs reputational
- AI-specific disclosure challenges (model retraining timelines)
- Regulatory requirements: GDPR Article 33 (72-hour breach notification)

Format requirements:
- Use citation format: [DISC-001], [DISC-002], etc.
- Include a References section with DOIs where available
- Cross-reference to QoreLogic Spec sections: §8.5 (Vulnerability Disclosure), §8.2 (Deferral)
- Target length: 600-1000 words

Key claims to substantiate:
- 90-day timeline accommodates complex AI vulnerabilities
- 24/7/90 staged timeline balances urgency with thoroughness
- Safety-critical issues warrant 4-hour max deferral
```

---

## 7. DATA_PROTECTION.md

```
Generate a research document for the QoreLogic project titled "DATA_PROTECTION.md" covering GDPR, CCPA, and HIPAA implications for AI governance systems.

Required content:
- GDPR Article 22: right to non-automated decisions with legal effect
- GDPR Article 33: 72-hour breach notification requirements
- CCPA consumer rights relevant to AI audit logs
- HIPAA implications if health data enters the pipeline
- Data minimization and purpose limitation principles
- Cross-border data transfer considerations (Schrems II)

Format requirements:
- Use citation format: [DATA-001], [DATA-002], etc.
- Include a References section with DOIs where available
- Cross-reference to QoreLogic Spec sections: §8.6 (Regulatory), §10 (Privacy)
- Target length: 800-1200 words

Key claims to substantiate:
- GDPR Art. 22 mandates human-in-the-loop for legal-effect decisions
- Local-first architecture sidesteps many cross-border issues
- Audit logs themselves may be subject to data protection requirements
```

---

## 8. HALLUCINATION_RATES.md

```
Generate a research document for the QoreLogic project titled "HALLUCINATION_RATES.md" covering LLM hallucination baselines and detection benchmarks.

Required content:
- HaluEval benchmark: methodology and reported rates
- TruthfulQA: baseline accuracy across model families
- Li et al. and Lin et al. hallucination rate studies
- Hallucination rates by task type: factual recall vs reasoning vs code
- The 18-50% range: where it comes from and what it means
- Detection methods: self-consistency, retrieval augmentation, formal verification

Format requirements:
- Use citation format: [HALLU-001], [HALLU-002], etc.
- Include a References section with DOIs where available
- Cross-reference to QoreLogic Spec sections: §1 (Problem Statement), Appendix A
- Target length: 800-1200 words

Key claims to substantiate:
- LLM hallucination rates range 18-50% depending on task
- Code generation hallucinations include non-existent APIs, incorrect logic
- Multi-tier verification reduces effective hallucination rate
```

---

## 9. SAST_ACCURACY.md

```
Generate a research document for the QoreLogic project titled "SAST_ACCURACY.md" covering static analysis false positive rates and LLM-based triage.

Required content:
- OWASP Benchmark: SAST tool accuracy baselines
- Veracode and other commercial tool false positive rates
- Why high FP rates cause "alert fatigue" and tool abandonment
- LLM-based SAST triage: Datadog's 90% FP reduction claim
- Combining static analysis with ML for improved precision
- Multi-tool aggregation strategies (Pylint + Flake8 + MyPy)

Format requirements:
- Use citation format: [SAST-001], [SAST-002], etc.
- Include a References section with DOIs where available
- Cross-reference to QoreLogic Spec sections: §3.2 (Check Matrix), §3.3.1 (Tier 1)
- Target length: 600-1000 words

Key claims to substantiate:
- LLM-based SAST triage reduces false positives by ~90%
- Multi-tool aggregation improves coverage but requires signal harmonization
- <5s latency target for Tier 1 static analysis
```

---

## 10. SRE_THRESHOLDS.md

```
Generate a research document for the QoreLogic project titled "SRE_THRESHOLDS.md" covering resource governance and operational thresholds.

Required content:
- Google SRE: error budgets, SLO/SLI concepts
- FinOps principles for cloud cost governance
- Queue depth thresholds: why 50 requests with 80% warning
- CPU throttling: 70% sustained triggers mode change
- LIFO vs FIFO queue strategies by workload type
- Backpressure signaling and load shedding patterns

Format requirements:
- Use citation format: [SRE-001], [SRE-002], etc.
- Include a References section with DOIs where available
- Cross-reference to QoreLogic Spec sections: §12 (Operational Modes), §2.5.1 (Backpressure)
- Target length: 600-1000 words

Key claims to substantiate:
- 50-request queue bound prevents runaway resource consumption
- 25% compute reserve for L3 ensures safety-critical work isn't starved
- LIFO for interactive, FIFO for batch optimizes user experience
```

---

## Usage Instructions

1. Feed each prompt to a research-capable LLM (Claude, GPT-4, etc.)
2. Save output to the corresponding file in `docs/research/{category}/`
3. Review for accuracy and add any missing citations
4. Update `docs/research/INDEX.md` to mark as complete
