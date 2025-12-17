# Q-DNA Evidence & Citation Policy

This policy enforces the epistemic standards for all claims and code justifications.

## 1. The Transitive Cap

**Rule:** Evidence chains must not exceed **Two Degrees of Separation** from the primary source.

- _Allowed:_ Source A (Primary) -> Agent Claim.
- _Allowed:_ Source A (Primary) -> Source B (Secondary) -> Agent Claim.
- _Forbidden:_ Source A -> Source B -> Source C -> Agent Claim.

**Rationale:** Prevents "Telephone Game" distortion of facts.

## 2. The Quote Context Rule

**Rule:** Direct quotes must include at least **+/- 2 sentences** (or ~200 characters) of surrounding context.

- **Purpose:** To prevent "Quote Mining" (stripping context to change meaning).
- **Enforcement:** Sentinel checks the token window around the quote keyframe.

## 3. Reference Freshness (TTL)

**Rule:** Technical documentation references have a Time-To-Live (TTL) of **6 months**.

- **Expired:** References older than 6 months must be re-verified against the live URL or repo.
