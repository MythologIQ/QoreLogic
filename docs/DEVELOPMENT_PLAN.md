# Q-DNA Development Roadmap

**Version:** 3.0
**Goal:** Establish the "Sovereign Fortress" with empirically validated governance
**Last Updated:** December 17, 2025
**Specification:** v2.4 (Fully Integrated)
**Repository:** https://github.com/MythologIQ/Q-DNA
**Research Foundation:** See [Research Library](./research/INDEX.md)

---

## Development Philosophy

### Fail Forward

- Failures are data points, not setbacks
- Every failed verification feeds the Shadow Genome
- Bootstrapping through systematic elimination of failure modes

### Research-Driven

- All parameters grounded in empirical research
- No "magic numbers" without citations
- Continuous validation against benchmarks

---

## Phase Summary

| Phase   | Focus                             |    Status     | Compliance |
| :------ | :-------------------------------- | :-----------: | :--------: |
| 1-4     | Foundation                        |  ✅ Complete  |     -      |
| 5       | P0: Critical Security             |  ✅ Complete  |     -      |
| 6       | P1: Citation & Fallback           |  ✅ Complete  |     -      |
| 7       | P2: Advanced Features             |  ✅ Complete  |     -      |
| 8       | Research Integration              |  ✅ Complete  |    98%     |
| **8.5** | **Trust Dynamics & Verification** | 🚧 **Active** |     -      |
| 9       | P3: ML-Dependent                  |   🔬 Future   |     -      |
| 10      | Production Hardening              | ✅ Initiated  |     -      |

---

## Phase 8.5: Trust Dynamics & Verification 🚧 ACTIVE

This phase bridges the gap between research specification (v2.4) and implementation.

### Task Dependency Graph

```
                    ┌─────────────────────────────────────────────────────────┐
                    │                     PHASE 8.5                           │
                    └─────────────────────────────────────────────────────────┘
                                              │
              ┌───────────────────────────────┼───────────────────────────────┐
              │                               │                               │
              ▼                               ▼                               ▼
    ┌─────────────────┐            ┌─────────────────┐            ┌─────────────────┐
    │  TRACK A        │            │  TRACK B        │            │  TRACK C        │
    │  Trust Engine   │            │  Verification   │            │  Infrastructure │
    │  (Sequential)   │            │  (Sequential)   │            │  (Parallel)     │
    └────────┬────────┘            └────────┬────────┘            └────────┬────────┘
             │                              │                              │
    ┌────────▼────────┐            ┌────────▼────────┐            ┌────────▼────────┐
    │ A1: λ-Decay     │            │ B1: Tier 1      │            │ C1: Backpressure│
    │    Engine       │            │    Static       │            │                 │
    └────────┬────────┘            └────────┬────────┘            └────────┬────────┘
             │                              │                              │
    ┌────────▼────────┐            ┌────────▼────────┐            ┌────────▼────────┐
    │ A2: Transitive  │            │ B2: Tier 2      │            │ C2: Mode        │
    │    Trust        │◄───────────│    DbC          │            │    Triggers     │
    └────────┬────────┘            └────────┬────────┘            └─────────────────┘
             │                              │
    ┌────────▼────────┐            ┌────────▼────────┐
    │ A3: L-B Stages  │            │ B3: Tier 3      │
    │                 │            │    FV (Future)  │
    └────────┬────────┘            └─────────────────┘
             │
    ┌────────▼────────┐
    │ A4: Micro-      │
    │    Penalties    │◄───────────────────────────────────────────────────────────┐
    └────────┬────────┘                                                            │
             │                                                                      │
    ┌────────▼────────┐                                                            │
    │ A5: Cooling-Off │                                                            │
    │    Periods      │                                                            │
    └────────┬────────┘                                                            │
             │                                                                      │
    ┌────────▼────────┐                                                            │
    │ A6: Probation   │                                                            │
    │    Logic        │────────────────────────────────────────────────────────────┘
    └─────────────────┘
```

---

### Track A: Trust Dynamics Engine (Sequential)

These tasks must be completed in order as each builds on the previous.

| ID     | Task                           | Spec       | Dependencies | Effort | Deliverable                |
| :----- | :----------------------------- | :--------- | :----------- | :----: | :------------------------- |
| **A1** | λ-Decay Engine                 | §5.3.3     | None         |   4h   | `trust_engine.py`          |
|        | - Implement EWMA formula       |            |              |        | `calculate_decay()`        |
|        | - Context-based λ (0.94/0.97)  |            |              |        | `get_lambda_for_context()` |
|        | - Integration with SCI updates |            |              |        | `update_trust_score()`     |
| **A2** | Transitive Trust               | §5.3.5     | A1           |   3h   | `transitive_trust.py`      |
|        | - δ damping factor (0.5)       |            |              |        | `propagate_trust()`        |
|        | - Max hop limit (3)            |            |              |        | `get_trust_path()`         |
|        | - Sybil resistance checks      |            |              |        | `check_anchor_distance()`  |
| **A3** | Lewicki-Bunker Stages          | §5.3.6     | A2           |   2h   | Stage mapping              |
|        | - CBT threshold (0.0-0.5)      |            |              |        | `get_trust_stage()`        |
|        | - KBT threshold (0.5-0.8)      |            |              |        | `stage_behavior()`         |
|        | - IBT threshold (>0.8)         |            |              |        | `demote_stage()`           |
| **A4** | Micro-Penalty Layer            | §9.1       | A3           |   4h   | Audit integration          |
|        | - Schema violation (0.5%)      |            |              |        | `apply_micro_penalty()`    |
|        | - API misuse (0.5%)            |            |              |        | `detect_violation_type()`  |
|        | - Stale citation (1%)          |            |              |        | `log_micro_penalty()`      |
|        | - Daily aggregate (2%)         |            |              |        | `aggregate_daily()`        |
| **A5** | Cooling-Off Periods            | §9.2, §9.3 | A4           |   2h   | Recovery gates             |
|        | - 24h gate (honest error)      |            |              |        | `check_cooling_off()`      |
|        | - 48h gate (manipulation)      |            |              |        | `start_cooling_off()`      |
|        | - Block trust repair during    |            |              |        | `can_recover_trust()`      |
| **A6** | Probationary Period            | §5.3.2     | A5           |   2h   | New source protection      |
|        | - 5 verification floor         |            |              |        | `is_in_probation()`        |
|        | - 30 day expiry                |            |              |        | `check_probation_expiry()` |
|        | - Floor protection (>35)       |            |              |        | `apply_probation_floor()`  |

**Track A Total:** ~17 hours

---

### Track B: Verification Pipeline (Sequential)

Multi-tier verification must be built layer by layer.

| ID     | Task                        | Spec   | Dependencies | Effort | Deliverable                  |
| :----- | :-------------------------- | :----- | :----------- | :----: | :--------------------------- |
| **B1** | Tier 1: Static Analysis     | §3.3.1 | None         |   3h   | Pipeline integration         |
|        | - Pylint integration        |        |              |        | `run_tier1_checks()`         |
|        | - Flake8 integration        |        |              |        | `parse_linter_output()`      |
|        | - MyPy integration          |        |              |        | `aggregate_static_results()` |
| **B2** | Tier 2: Design by Contract  | §3.3.2 | B1           |   4h   | `deal` integration           |
|        | - Install `deal` library    |        |              |        | `setup_dbc_environment()`    |
|        | - Pre/post condition hooks  |        |              |        | `verify_contracts()`         |
|        | - Z3 solver connection      |        |              |        | `formal_contract_check()`    |
| **B3** | Tier 3: Formal Verification | §3.3.3 | B2, Phase 9  |  8h+   | External tools               |
|        | - PyVeritas setup           |        |              |        | Future                       |
|        | - CBMC integration          |        |              |        | Future                       |
|        | - CrossHair fallback        |        |              |        | Future                       |

**Track B Total:** ~7 hours (excl. B3)

---

### Track C: Infrastructure (Parallel)

These can be implemented independently alongside Track A and B.

| ID     | Task                        | Spec   | Dependencies | Effort | Deliverable                  |
| :----- | :-------------------------- | :----- | :----------- | :----: | :--------------------------- |
| **C1** | Backpressure Mechanism      | §2.5.1 | None         |   3h   | Server hardening             |
|        | - Queue bound (50 requests) |        |              |        | `check_queue_capacity()`     |
|        | - 80% warning signal        |        |              |        | `emit_backpressure_signal()` |
|        | - Load shedding at 100%     |        |              |        | `shed_load()`                |
|        | - LIFO/FIFO queue types     |        |              |        | `configure_queue_type()`     |
| **C2** | Mode Transition Triggers    | §12    | C1           |   2h   | Auto-mode switching          |
|        | - CPU >70% (5 min) → LEAN   |        |              |        | `monitor_cpu()`              |
|        | - Queue >50 → SURGE         |        |              |        | `monitor_queue_depth()`      |
|        | - Security event → SAFE     |        |              |        | `trigger_safe_mode()`        |

**Track C Total:** ~5 hours

---

### Execution Plan

#### Sprint 1: Foundation (Can run in parallel)

| Day | Track A                  | Track B                 | Track C               |
| :-: | :----------------------- | :---------------------- | :-------------------- |
|  1  | **A1:** λ-Decay Engine   | **B1:** Static Analysis | **C1:** Backpressure  |
|  2  | A1 (cont.)               | B1 (cont.)              | **C2:** Mode Triggers |
|  3  | **A2:** Transitive Trust | **B2:** DbC Setup       | C2 (cont.)            |

#### Sprint 2: Integration (Sequential dependencies)

| Day | Track A                 | Track B              | Track C     |
| :-: | :---------------------- | :------------------- | :---------- |
|  4  | A2 (cont.)              | B2 (cont.)           | ✅ Complete |
|  5  | **A3:** L-B Stages      | B2 (cont.)           | -           |
|  6  | **A4:** Micro-Penalties | ✅ Tier 1-2 Complete | -           |

#### Sprint 3: Completion

| Day | Track A             | Notes               |
| :-: | :------------------ | :------------------ |
|  7  | A4 (cont.)          | Integration testing |
|  8  | **A5:** Cooling-Off | End-to-end flow     |
|  9  | **A6:** Probation   | Final validation    |

**Total Phase 8.5 Duration:** ~9 working days (~29 hours)

---

## Phase 9: P3 ML-Dependent 🔬 FUTURE

Requires machine learning capabilities beyond current bootstrapping scope.

| Item                     | Status | Blocker                | Priority | Est. Effort |
| :----------------------- | :----: | :--------------------- | :------- | :---------- |
| Semantic Drift Monitor   |   ❌   | Embedding model        | High     | 16h         |
| Diversity Quorum (L3)    |   ❌   | Multi-model inference  | High     | 12h         |
| Real CBMC Integration    |   ❌   | External tool setup    | Medium   | 8h          |
| Adversarial Review       |   ❌   | Devil's advocate model | Medium   | 8h          |
| Echo/Paraphrase Detector |   ❌   | N-gram/embedding       | Low      | 6h          |

---

## Phase 10: Production Hardening ✅ INITIATED

| Item                    |   Status    | Description                         | Est. Effort |
| :---------------------- | :---------: | :---------------------------------- | :---------- |
| Repository Creation     | ✅ **Done** | https://github.com/MythologIQ/Q-DNA | -           |
| README + LICENSE        | ✅ **Done** | Apache 2.0                          | -           |
| CI/CD Pipeline          |     📋      | GitHub Actions                      | 4h          |
| Docker Containerization |     📋      | Multi-stage build                   | 4h          |
| Documentation Site      |     📋      | MkDocs/Docusaurus                   | 6h          |
| Pilot Deployment        |     📋      | Internal dogfooding                 | 8h          |
| Benchmark Validation    |     📋      | Trap dataset execution              | 8h          |

---

## System Statistics

### MCP Tools: 36

| Category         | Count | Purpose                  |
| :--------------- | :---: | :----------------------- |
| Sentinel         |   2   | Code/claim auditing      |
| Judge            |   2   | Event logging, penalties |
| Overseer         |   3   | L3 approval workflow     |
| Shadow Genome    |   1   | Failure archival         |
| Volatility       |   3   | TTL tracking             |
| SLA              |   1   | SLA status               |
| Identity         |   1   | Signature verification   |
| System           |   3   | Mode, status, health     |
| Credibility      |   4   | SCI management           |
| Quarantine       |   4   | Time-based quarantine    |
| Fallback         |   1   | Sentinel unavailable     |
| Deferral         |   4   | Disclosure windows       |
| Mode Enforcement |   2   | Operational modes        |
| Calibration      |   3   | Brier score tracking     |
| Reputation       |   2   | Auto-recovery            |

### Database Tables: 11

| Table                 | Purpose           | Integrity     |
| :-------------------- | :---------------- | :------------ |
| `soa_ledger`          | Event log         | Merkle chain  |
| `agent_registry`      | Agent DIDs        | Ed25519       |
| `reputation_log`      | Penalties/rewards | Event-linked  |
| `shadow_genome`       | Failure archive   | Training data |
| `l3_approval_queue`   | Approvals         | Timeout       |
| `system_state`        | Mode              | Single row    |
| `claim_volatility`    | TTLs              | Auto-expiry   |
| `source_credibility`  | SCI               | Tier-based    |
| `agent_quarantine`    | Quarantine        | 48h default   |
| `disclosure_deferral` | Deferrals         | Time-boxed    |
| `calibration_log`     | Brier scores      | Rolling 100   |

### Implementation Files

| File                     | Purpose        | Lines |
| :----------------------- | :------------- | :---: |
| `server.py`              | MCP Server     | ~1100 |
| `sentinel_engine.py`     | Verification   | ~600  |
| `identity_manager.py`    | Ed25519        | ~280  |
| `volatility_manager.py`  | TTL/SLA        | ~300  |
| `credibility_manager.py` | SCI/Quarantine | ~400  |
| `advanced_features.py`   | P2 Features    | ~500  |
| `bootstrapper.py`        | Evolution      | ~350  |

**Total Implementation:** ~3,500 lines

### Research Library: 9 Documents

| Category     | Complete | Planned |
| :----------- | :------: | :-----: |
| Foundations  |    1     |    3    |
| Technologies |    3     |    2    |
| Compliance   |    1     |    2    |
| Benchmarks   |    0     |    3    |
| Synthesis    |    2     |    0    |
| Methodology  |    2     |    0    |
| **Total**    |  **9**   | **10**  |

---

## Quality Metrics

| Metric            | Target |  Current  |
| :---------------- | :----: | :-------: |
| Spec Compliance   |  100%  |  **98%**  |
| Test Pass Rate    |  100%  | **100%**  |
| Research Coverage |  100%  |  **80%**  |
| P0 Complete       |  6/6   |    ✅     |
| P1 Complete       |  4/4   |    ✅     |
| P2 Complete       |  4/4   |    ✅     |
| P3 Complete       |  0/5   | 🔬 Future |

---

## Implementation Gaps Status

### ✅ FIXED (December 17, 2025)

| Gap                    | Location                 | Fix Applied                         |
| :--------------------- | :----------------------- | :---------------------------------- |
| SCI_REJECT threshold   | `credibility_manager.py` | 30 → **35** per spec §5.3.1         |
| T4 initial credibility | `credibility_manager.py` | 40 → **45** per spec §5.3.2         |
| SCI_ESCALATE_L2        | `credibility_manager.py` | 50 → **60** per spec §5.3.1         |
| SCI_ESCALATE_L3        | `credibility_manager.py` | 50 → **40** per spec §5.3.1         |
| Missing SOA columns    | `schema.sql`             | Added 6 governance columns          |
| Missing event types    | `schema.sql`             | Added 8 new event types             |
| Schema version         | `schema.sql`             | v2.0 → **v2.4**                     |
| GitHub repository      | -                        | https://github.com/MythologIQ/Q-DNA |

### 🚧 IN PROGRESS (Phase 8.5)

See detailed task breakdown in Track A, B, C above.

### 📋 PLANNED (Phase 9+)

| Gap                         | Spec Section | Blocker              |
| :-------------------------- | :----------- | :------------------- |
| Tier 3 formal verification  | App A        | PyVeritas/CBMC setup |
| GDPR Art. 22 auto-detection | §8.6         | Pattern matching     |
| Edge deployment profile     | §2.6         | RPi 4 hardware       |

---

## Changelog

| Version | Date           | Changes                                                                                               |
| :------ | :------------- | :---------------------------------------------------------------------------------------------------- |
| 1.0     | 2025-12        | Initial phases                                                                                        |
| 2.0     | 2025-12-17     | Research integration, gap analysis                                                                    |
| 2.1     | 2025-12-17     | Fixed thresholds, schema updates                                                                      |
| **3.0** | **2025-12-17** | **Complete task breakdown with dependency graph, parallel tracks, effort estimates, and sprint plan** |
