# Multi-Agent Coordination Architecture

**Category:** Technologies
**Version:** 1.0
**Last Updated:** December 17, 2025
**Status:** Complete
**Specification Links:** §2 (Architecture), §3 (Sentinel), §12 (Operations)

---

## Executive Summary

This document addresses a previously unspecified gap in the QoreLogic Specification: **Multi-Agent Coordination (MAC)**. The transition from single-agent to Multi-Agent System (MAS) architecture requires rigorous standards for communication protocols, topological patterns, and resource management.

Key finding: FIPA-ACL's semantic richness comes with unacceptable overhead for edge deployment. QoreLogic adopts **JSON-RPC 2.0** (MCP-compatible) with strict Pydantic schemas to retain semantic integrity at minimal cost.

---

## 1. Communication Protocol Selection

### 1.1 FIPA-ACL: The Legacy Standard

The Foundation for Intelligent Physical Agents - Agent Communication Language (FIPA-ACL) uses **Speech Act Theory** with explicit performatives:

| Performative | Intent              |
| ------------ | ------------------- |
| `inform`     | Convey belief       |
| `request`    | Ask for action      |
| `query-ref`  | Ask for information |
| `agree`      | Commit to action    |
| `refuse`     | Decline action      |

**Limitations:**

- Verbose syntax (S-expressions, XML)
- Heavy middleware dependency (JADE)
- High parsing overhead
- Monolithic architecture

### 1.2 JSON-RPC 2.0: The Modern Standard

JSON-RPC 2.0 is the de facto standard for LLM tool interoperability, exemplified by the **Model Context Protocol (MCP)**.

| Feature        | FIPA-ACL             | JSON-RPC (MCP)     |
| -------------- | -------------------- | ------------------ |
| Semantic Basis | Speech Act Theory    | Procedure Call     |
| Payload Weight | High (verbose)       | Low (minimal JSON) |
| Transport      | Middleware-dependent | Transport agnostic |
| Discovery      | Centralized          | Dynamic/Ad-hoc     |
| State          | Often stateful       | Stateless          |

### 1.3 QoreLogic Protocol Adoption

**Decision:** JSON-RPC 2.0 as transport layer with **Semantic Schema Layer** for performative reconstruction.

**Implementation:**

- `method` field serves as performative proxy (e.g., `agent.inform`, `agent.request`)
- `params` object adheres to Pydantic models for type safety
- All agents implement `handle_request` accepting JSON-RPC payloads

```python
# Example: QoreLogic Agent Request Handler
from pydantic import BaseModel

class AgentRequest(BaseModel):
    method: str  # e.g., "agent.request"
    params: dict
    id: str

async def handle_request(request: AgentRequest) -> dict:
    if request.method == "agent.request":
        return await process_request(request.params)
    elif request.method == "agent.inform":
        return await process_inform(request.params)
    ...
```

---

## 2. Topological Patterns

### 2.1 Blackboard Architecture

**Use Case:** Collaborative problem-solving where no single agent has full context.

**Mechanism:**

- Shared memory space ("Blackboard")
- Agents ("Knowledge Sources") read/write partial solutions
- Agents don't communicate directly—monitor board for triggers

**Example:** Syntax Checker triggers when Code Generator posts draft function.

**Scalability Solution:** Hierarchical Blackboard

- Local blackboards for sub-teams (e.g., "Dev Team")
- Summarize to global blackboard

**QoreLogic Application:** The "World Model" implements Hierarchical Blackboard for global context without network saturation.

### 2.2 Contract Net Protocol (CNP)

**Use Case:** Resource allocation and task distribution.

**Workflow:**

1. **Manager:** Broadcasts Task Announcement
2. **Bidders:** Submit bids based on local resources
3. **Award:** Manager evaluates and awards contract
4. **Execution:** Winner executes and returns result

**QoreLogic Application:** Dynamic task routing away from overloaded nodes (backpressure implementation).

### 2.3 Hierarchical Swarms

**Use Case:** Complex task decomposition.

**Pattern:**

- Orchestrator (Planner) decomposes user prompt into sub-tasks
- Delegates to specialized Worker agents
- Event-driven: Agents subscribe to topics (e.g., `code.generated`, `test.failed`)

**QoreLogic Application:** Asynchronous coupling enables robust error handling without explicit invocation chains.

---

## 3. Backpressure and Load Shedding

### 3.1 The Problem

In high-throughput systems, queues grow unbounded if arrival rate exceeds processing rate.

### 3.2 Google SRE Solution

| Mechanism          | Description                                       |
| ------------------ | ------------------------------------------------- |
| **Bounded Queues** | Reject when full                                  |
| **Load Shedding**  | Drop requests under overload                      |
| **Backpressure**   | Signal sender to slow down                        |
| **LIFO Queues**    | Process most recent first (for interactive tasks) |

### 3.3 QoreLogic Implementation

**Mandatory:** All agents implement bounded queues for JSON-RPC requests.

**Behavior:**

- LIFO with timeout for interactive (user-facing) tasks
- FIFO for batch processing
- Explicit `busy` signal when queue >80% full
- Load shedding at 100% queue capacity

**Applied In:** §12 (Operational Modes) — SURGE mode triggers when queue >50 tasks.

---

## 4. Edge Deployment Constraints

### 4.1 The Memory Wall

Target: Raspberry Pi 4 (4GB RAM)

| Component             | Memory |
| --------------------- | ------ |
| Linux OS              | ~500MB |
| Agent Runtime         | ~200MB |
| Model Weights (7B q4) | ~3.5GB |
| **Remaining**         | ~0     |

**Conclusion:** 7B models are infeasible on 4GB edge devices.

### 4.2 Framework Selection

#### uAgents (Fetch.ai)

**For:** Lightweight, autonomous local loops

- Minimal memory footprint
- Decentralized agent registration (Almanac)
- Designed for edge deployment

#### AutoGen v0.4 (Microsoft)

**For:** Orchestration and complex workflows

- Event-driven (agents can "sleep")
- Distributed patterns
- RPi as Worker, cloud as Orchestrator

### 4.3 QoreLogic Edge Stack

| Component       | Selection                                | Rationale         |
| --------------- | ---------------------------------------- | ----------------- |
| Hardware        | RPi 4 (4GB)                              | Target constraint |
| Inference       | Ollama + Phi-3 Mini or Gemma 2B (q4_k_m) | <2GB RAM          |
| Agent Framework | uAgents                                  | Minimal overhead  |
| Vector Store    | Qdrant (local) or Chroma                 | Lightweight       |
| Networking      | JSON-RPC over WebSocket                  | Low latency mesh  |

---

## 5. Recommended Parameters

| Parameter                        | Value                       | Confidence | Citation            |
| -------------------------------- | --------------------------- | ---------- | ------------------- |
| Protocol overhead reduction      | >40% (JSON-RPC vs FIPA-ACL) | High       | Comparative studies |
| Queue bound (interactive)        | 50 requests                 | Medium     | SRE practices       |
| LIFO timeout                     | 5 seconds                   | Medium     | UX research         |
| Backpressure threshold           | 80% queue                   | High       | SRE practices       |
| Max edge model size              | <2GB (quantized)            | High       | Memory constraints  |
| Lambda for high-risk trust decay | 0.94                        | High       | RiskMetrics         |

---

## 6. Specification Updates

Based on this research, recommend the following additions to QoreLogic_SPECIFICATION.md:

1. **New Section §2.5:** Communication Protocol (JSON-RPC 2.0 + Pydantic)
2. **§12 (Operations):** Add backpressure and load shedding requirements
3. **§13 (Implementation):** Add uAgents, AutoGen v0.4 to framework options
4. **§12.2 (Resource Governance):** Add queue depth thresholds

---

## References

[MAC-001] FIPA Agent Communication Language Specifications. fipa.org

- Key finding: Performatives provide semantic richness
- Applied In: §2.5 method naming convention

[MAC-002] Model Context Protocol Documentation. github.com/anthropics/mcp

- Key finding: JSON-RPC 2.0 transport standard
- Applied In: §2.5 transport protocol

[MAC-003] Beyer, B., et al. (2016). "Site Reliability Engineering." O'Reilly.

- Key finding: Backpressure and load shedding essential
- Applied In: §12 operational modes

[MAC-004] Fetch.ai uAgents Documentation. docs.fetch.ai

- Key finding: Lightweight agent framework for edge
- Applied In: §13 framework selection

[MAC-005] Microsoft AutoGen v0.4 Documentation. microsoft.github.io/autogen

- Key finding: Event-driven, distributed patterns
- Applied In: §13 orchestration options
