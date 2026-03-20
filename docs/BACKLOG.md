# Project Backlog

## Blockers (Must Fix Before Progress)

### Development Blockers
- [x] [D1] Import existing QL skills from FailSafe extension into ingest/internal/ (Complete)
- [x] [D2] Create processing script that normalizes skills to S.H.I.E.L.D. format (Complete — scripts/process-skills.py)
- [x] [D3] Create ql-document skill (Complete — ingest/internal/governance/ql-document.md)

## Backlog (Planned Work)
- [x] [B1] Import all existing ql-* skills from G:/MythologIQ/FailSafe/.claude/commands/ (Complete)
- [ ] [B2] Create compilation script for Claude Code format (.claude/skills/)
- [ ] [B3] Create compilation script for Agent workflow format (.agent/workflows/)
- [ ] [B4] Process brainstorming/collaborative design principles into ql-plan and ql-bootstrap
- [x] [B5] Create ql-course-correct skill (Complete — Navigator persona, 190 lines)
- [x] [B6] Identify and fill skill gaps for e2e autonomous building (Complete — all gaps filled)
- [ ] [B7] Create skill quality audit checklist
- [x] [B8] Create ql-fixer subagent definition (Complete — 4-layer methodology, 122 lines)
- [ ] [B9] Implement tools/reliability/ scripts (Intent Lock, Skill Admission, Gate-to-Skill Matrix)
- [x] [B10] Create SKILL_REGISTRY.md — comprehensive index of all content (Complete)
- [x] [B11] Consolidate utility skills — archive, merge, distill (Complete)
- [x] [B12] Wire ql-document → ql-technical-writer subagent dispatch (Complete)

## Lifecycle Coverage

```
ALIGN → ENCODE → PLAN → GATE → IMPLEMENT → SUBSTANTIATE → DELIVER
  ✓        ✓       ✓      ✓       ✓            ✓           ✓
```
Cross-cutting: RESEARCH ✓, DEBUG ✓, STATUS ✓, VALIDATE ✓, ORGANIZE ✓, RECOVER ✓

**All persona gaps filled. All lifecycle phases covered.**

## Subagent Pairings

| Governance Skill | Subagent | Status |
|-----------------|----------|--------|
| ql-debug | ql-fixer | PAIRED |
| ql-document | ql-technical-writer | PAIRED |
| ql-audit | (parallel-auditor) | PROPOSED |
| ql-implement | (test-writer) | PROPOSED |
| ql-substantiate | (verification-auditor) | PROPOSED |

## Final Inventory

| Category | Count | Location |
|----------|-------|----------|
| Governance skills | 17 | ingest/internal/governance/ — ALL COMPLIANT |
| Agent personas | 6 | ingest/internal/agents/ |
| Reference docs | 14 | ingest/internal/references/ (7 ql-templates + 7 patterns) |
| Utility skills | 4 | ingest/internal/utilities/ (meta-skills + generic) |
| Third-party agents | 229 | ingest/third-party/agents/ (3 enhanced) |
| Archived | 5 | ingest/experimental/ |
| Scripts/rules | 402 | ingest/scripts/ |

## Remaining Work
- [ ] [B2] Compilation script for Claude Code format
- [ ] [B3] Compilation script for Agent workflow format
- [ ] [B4] Collaborative design principles in ql-plan/ql-bootstrap
- [ ] [B7] Skill quality audit checklist
- [ ] [B9] Reliability scripts

---

_Updated by /ql-* commands automatically_
