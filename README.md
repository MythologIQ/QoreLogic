# Q-DNA: The Code DNA Engine

**Version:** 2.4 (Fully Integrated)  
**Status:** Active Research / Bootstrapping Phase

---

## Overview

Q-DNA (Quality DNA Engine) is a **local-first governance layer** for high-assurance AI-assisted code development. It addresses the fundamental unreliability of Large Language Models by implementing a multi-tier verification pipeline grounded in formal methods and probabilistic trust engineering.

### Core Value Proposition

| Problem                    | Q-DNA Solution                   |
| :------------------------- | :------------------------------- |
| LLM hallucination (18-50%) | Multi-tier verification pipeline |
| Cloud dependency           | Sovereign local execution        |
| Static trust assumptions   | Dynamic reputation with decay    |
| Binary security            | Probabilistic risk grading       |
| Audit opacity              | Merkle-chained transparency      |

---

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        THE SOVEREIGN FORTRESS                    │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│   Cloud (Scrivener)  ──────▶  MCP Gateway (Port 8001)           │
│                                      │                           │
│                                      ▼                           │
│                         ┌─────────────────────┐                  │
│                         │   VERIFICATION      │                  │
│                         │   ├── Tier 1: Static│                  │
│                         │   ├── Tier 2: DbC   │                  │
│                         │   └── Tier 3: FV    │                  │
│                         └─────────────────────┘                  │
│                                      │                           │
│                                      ▼                           │
│   ┌──────────┐    ┌──────────┐    ┌──────────┐                  │
│   │ Sentinel │───▶│  Judge   │───▶│  Ledger  │                  │
│   └──────────┘    └──────────┘    └──────────┘                  │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## Key Features

### 🛡️ Verification Pipeline

- **Tier 1:** Static Analysis (Pylint, Flake8, MyPy)
- **Tier 2:** Design by Contract (`deal` library)
- **Tier 3:** Formal Verification (PyVeritas, CBMC)

### 📊 Trust Dynamics

- Source Credibility Index (SCI) with dynamic decay
- Transitive trust with damping (δ=0.5)
- Lewicki-Bunker trust stages (CBT/KBT/IBT)

### ⚖️ Compliance

- GDPR Article 22 alignment
- NIST AI RMF integration
- 90-day vulnerability disclosure policy

### 🔒 Security

- Ed25519 cryptographic signing
- Merkle-chained audit ledger
- HILS penalty model (High Inspection/Low Severity)

---

## Documentation

| Document                                              | Description                       |
| :---------------------------------------------------- | :-------------------------------- |
| [Q-DNA_SPECIFICATION.md](docs/Q-DNA_SPECIFICATION.md) | Complete specification (v2.4)     |
| [PRD.md](docs/PRD.md)                                 | Product requirements              |
| [ARCHITECTURE.md](docs/ARCHITECTURE.md)               | Technical architecture            |
| [DEVELOPMENT_PLAN.md](docs/DEVELOPMENT_PLAN.md)       | Roadmap and implementation status |
| [Research Library](docs/research/INDEX.md)            | Empirical research foundation     |

---

## Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Run the MCP server
python -m local_fortress.mcp_server.server

# Run tests
python -m pytest tests/
```

---

## Implementation Status

| Phase | Status | Description                               |
| :---- | :----: | :---------------------------------------- |
| P0    |   ✅   | Critical Security (Ed25519, key rotation) |
| P1    |   ✅   | Citation & Fallback (SCI, tiers)          |
| P2    |   ✅   | Advanced Features (modes, calibration)    |
| P3    |   🔬   | ML-Dependent (drift detection, quorum)    |

---

## Research Foundation

Q-DNA is grounded in empirical research:

- **Trust:** EigenTrust, Lewicki-Bunker, RiskMetrics
- **Verification:** HaluEval, PyVeritas, OWASP Benchmark
- **Compliance:** GDPR, NIST AI RMF, ISO 42001
- **Deterrence:** Nagin HILS model

See the [Research Library](docs/research/INDEX.md) for full citations.

---

## License

This project is licensed under the Apache License 2.0 - see the [LICENSE](LICENSE) file for details.

---

## Contributing

Q-DNA is currently in active research phase. Contributions welcome after v1.0 release.

---

**MythologIQ Studio** | _Building trustworthy AI systems_
