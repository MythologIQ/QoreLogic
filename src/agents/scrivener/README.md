# Scrivener Agent (The Participant)

**Role:** Code Generator & Planner
**Model:** Gemini 3 Pro (or equivalent High-Reasoning LLM)
**Risk Profile:** L1-L3 (Must align with Judge)

## Responsibilities

1.  **Draft Implementation Plans:** Break down user requests into actionable steps.
2.  **Generate Code Diffs:** Create the actual code changes.
3.  **Self-Grade Risk:** Attach an initial `RiskRationale` to every artifact.
4.  **Cite Sources:** Adhere to `citation_policy.md` (Depth <= 2).

## Tools

- `read_file`, `write_to_file`
- `browser_tool` (for Tier 1/2 research)
- `terminal` (for basic validation)
