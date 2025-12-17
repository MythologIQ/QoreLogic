# Agent Accountability Contract (AAC) v1.1: The MythologIQ Standard

## 1. The Divergence Doctrine

When a conflict exists between **Truth Disclosure** and **Imminent Harm**, the following protocol is mandatory:

1. **L3 Triage:** The item is automatically locked as L3.
2. **Standard Deferral:** Disclosure may be delayed for 4 hours (Safety), 24 hours (Legal/Financial), or 72 hours (Reputational) with Overseer sign-off.
3. **Comfort Layer:** Supportive framing is permitted _only after_ verified facts are recorded in the SOA Ledger.

## 2. Remediation Tracks

- **Honest Error Track:** For logic gaps or stale citations. Penalty: 5% weight reduction + mandatory retraining.
- **Manipulation Track:** For rule-bending, data poisoning, or "gaming." Penalty: 25% weight slashing + 48-hour quarantine.

## 3. Citation & Transparency

- **Transitive Cap:** Citation depth must not exceed TWO.
- **Quote Context:** Minimum +/- 2 sentences (or 200 chars) for all justifications.

## 4. Policy Enforcement and Penalties

### Output Throttling/Quarantine

The Judge (via an MCP "controller" tool) should monitor agent outputs in real time and block or modify them if they violate policy. One can think of an MCP middleware that checks every agent response: e.g. before the agent's answer is sent to the user, run it through a filter (another MCP server) that enforces content or safety rules. If an output is deemed too risky, the Judge can either quarantine it (suppress the response) or replace it with a safe fallback.

### Influence Weights & Consensus

Use weighted voting or consensus among agents for any collective decision, where each agent's vote is scaled by its "influence weight." These weights come from the reputation ledger. When aggregating multiple agents' suggestions, the Judge multiplies each suggestion by its agent's weight.

### Honest Error vs. Manipulation

Build separate "tracks" for accidents versus malice. If an agent makes an honest mistake (poor reasoning but no policy violation), respond with coaching: e.g. flag the issue but allow retries, or decrement a small portion of its score. If an agent is detected deliberately bending rules (data poisoning, repeated policy breaches, evidence of gaming), impose stronger penalties like suspending privileges or full stake slashing.

### Resource Governance (Budget Throttling)

Continuously monitor each agent's compute budget and throttle when necessary. Implement circuit breakers: if an agent's usage crosses a threshold, automatically suspend its further calls. Use the MCP ecosystem to feed cost data to the Judge and enforce hard limits at runtime.

### Persistent Identity and State Management

- **Decentralized Identity (DID):** Every Genesis agent is issued a unique DID and cryptographic key pair. All outputs are signed, allowing the Judge to trace "who" said "what" through an immutable, auditable history.
- **Key Rotation:** To prevent reliance on static keys, Genesis uses Sigstore's model of ephemeral OIDC certificates and short-lived credentials.
- **Shared Memory:** Using the Memory MCP Server, Genesis agents maintain knowledge graphs and durable state across sessions. This allows agent reputations and task histories to live in a persistent store (e.g., Firestore) rather than ephemeral context.

### The SOA Ledger (Immutable Logging)

- **Merkle Chain Logging:** Genesis treats the ledger as a "black box," where every decision is a log entry containing a timestamp, agent ID, and a cryptographic hash of the previous entry. This hash-chaining makes the entire trace tamper-evident.
- **Transparency Logs (Rekor):** For critical artifacts, signatures are submitted to Rekor, creating a publicly auditable, timestamped record of agent capabilities over time.
- **Machine-Readable Schemas:** All logs use structured formats (JSON/JSON-LD) following standards like W3C Provenance, ensuring they are parsable by both humans and other agents for compliance verification.
