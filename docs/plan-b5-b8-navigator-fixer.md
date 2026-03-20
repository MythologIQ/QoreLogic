# Plan: ql-course-correct (B5) + ql-fixer subagent (B8)

## Open Questions

- Should ql-course-correct have the authority to amend CONCEPT.md or ARCHITECTURE_PLAN.md directly, or should it always route through /ql-bootstrap or /ql-plan for those changes?
- Should ql-fixer be a full subagent definition or a skill file? ql-debug references it as `subagent_type: "ql-fixer"` which suggests Claude Code subagent config.

## Phase 1: ql-fixer Subagent Definition (B8)

### Affected Files

- `ingest/internal/agents/ql-fixer.md` — NEW: Fixer subagent definition
- `docs/BACKLOG.md` — Mark B8 complete

### Changes

Create `ql-fixer.md` as a subagent definition (matching existing agent format in `ingest/internal/agents/`).

The fixer implements a 4-layer diagnostic methodology referenced by ql-debug:

**Layer 1 — Dijkstra (Static Structure)**:
Read the code. Trace data flow. Identify structural issues (missing imports, wrong types, broken references) without running anything.

**Layer 2 — Hamming/Shannon (Error Signal Analysis)**:
Analyze the error message/output. Decode what the error is actually saying vs what it appears to say. Check for misleading symptoms.

**Layer 3 — Turing/Hopper (Execution Trace)**:
Trace the actual execution path. Run tests, check logs, verify what code actually executes vs what was intended.

**Layer 4 — Zeller (Regression Archaeology)**:
Check git history. When did this break? What changed? Is this a regression from a known-good state?

The subagent must:
- Accept a problem description (symptom, context, reproduction)
- Run all 4 layers before proposing any fix
- Output: root cause with evidence, cause-effect chain, proposed fix, regression risk
- Support both "rapid root-cause" and "residual sweep" modes

## Phase 2: ql-course-correct Skill (B5)

### Affected Files

- `ingest/internal/governance/ql-course-correct.md` — NEW: Navigator skill
- `docs/ARCHITECTURE_PLAN.md` — Confirm Navigator persona mapping
- `docs/BACKLOG.md` — Mark B5 complete

### Changes

Create `ql-course-correct.md` as a S.H.I.E.L.D. compliant governance skill for the Navigator persona.

**Trigger conditions** (when to invoke):
- Multiple consecutive VETOs from /ql-audit
- Recurring Shadow Genome patterns (same failure mode appearing >2 times)
- User feels "stuck" or direction has gone wrong
- Scope creep detected (implementation diverging from CONCEPT.md)
- Significant time elapsed with no /ql-substantiate seal

**Core approach** — collaborative dialogue (per feedback memory):
1. Read current state: META_LEDGER (recent entries), SHADOW_GENOME (failure patterns), CONCEPT.md, ARCHITECTURE_PLAN.md, BACKLOG.md
2. Diagnose the drift through structured questions (one at a time, multiple choice)
3. Classify drift type: SCOPE_CREEP, DESIGN_MISMATCH, COMPLEXITY_SPIRAL, BLOCKED_DEPENDENCY, LOST_DIRECTION
4. Propose 2-3 recovery paths with trade-offs
5. User selects path
6. Execute recovery: amend governance docs, reset blocked items, simplify architecture, or rescope

**Skill structure** (must pass process-skills.py):
- `<skill>` block with phase=RECOVER, persona=Navigator
- Execution protocol with numbered steps
- Constraints (NEVER/ALWAYS)
- Success criteria (checkboxes)
- Integration section

**Key design principle**: ql-course-correct is NOT ql-debug. It doesn't fix code bugs. It fixes direction — the gap between where you ARE and where CONCEPT.md says you should BE.

### Unit Tests

No code tests (these are markdown skill files). Validation is via `scripts/process-skills.py` — both files must be COMPLIANT.

## Phase 3: Integration Verification

### Affected Files

- `docs/BACKLOG.md` — Update processing status, mark B5+B8 complete
- `docs/META_LEDGER.md` — Record implementation entry

### Changes

1. Run `python scripts/process-skills.py` — verify both new files are COMPLIANT
2. Verify ql-course-correct appears in `processed/ql-course-correct.md`
3. Verify ql-fixer appears in agent personas list
4. Update ARCHITECTURE_PLAN.md persona table if needed (Navigator should already map to ql-course-correct)
5. Update BACKLOG: mark B5 and B8 complete, update gap analysis (all personas now have skills)
6. Record META_LEDGER entry with content hash
