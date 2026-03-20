# Qorelogic Skill Registry

## Governance Skills (17) — ALL COMPLIANT

| Skill | Trigger | Persona | Phase | Lines |
|-------|---------|---------|-------|-------|
| ql-bootstrap | /ql-bootstrap | Governor | ALIGN + ENCODE | 155 |
| ql-plan | /ql-plan | Governor | PLAN | 176 |
| ql-audit | /ql-audit | Judge | GATE | 189 |
| ql-implement | /ql-implement | Specialist | IMPLEMENT | 223 |
| ql-refactor | /ql-refactor | Specialist | IMPLEMENT | 184 |
| ql-substantiate | /ql-substantiate | Judge | SUBSTANTIATE | 243 |
| ql-repo-release | /ql-repo-release | Governor | DELIVER | 231 |
| ql-debug | /ql-debug | Fixer | IMPL/SUBST/GATE | 111 |
| ql-course-correct | /ql-course-correct | Navigator | RECOVER | 190 |
| ql-research | /ql-research | Analyst | RESEARCH | 244 |
| ql-document | /ql-document | Tech Writer | DELIVER/IMPL | 235 |
| ql-validate | /ql-validate | Judge | ANY | 106 |
| ql-status | /ql-status | Governor | ANY | 156 |
| ql-help | /ql-help | Governor | ANY | 64 |
| ql-organize | /ql-organize | Governor | ORGANIZE | 137 |
| ql-repo-audit | /ql-repo-audit | Judge | AUDIT | 130 |
| ql-repo-scaffold | /ql-repo-scaffold | Specialist | IMPLEMENT | 121 |

## Agent Personas (6)

| Agent | Lines | Role |
|-------|-------|------|
| ql-governor | 26 | Senior Architect — ALIGN, ENCODE, LEDGER |
| ql-judge | 25 | Security Auditor — GATE, PASS/VETO |
| ql-specialist | 25 | Implementation Expert — ENCODE, VERIFY |
| ql-fixer | 122 | Diagnostic Specialist — 4-layer root-cause |
| ql-technical-writer | 69 | Documentation quality — README, API, changelog |
| ql-ux-evaluator | 93 | UI/UX testing — Playwright, accessibility |

## Third-Party Agents (10 categories)

| Category | Count | Key Agents |
|----------|-------|------------|
| 01-core-development | 12 | backend-dev, frontend-dev, fullstack, api-designer, ui-designer |
| 02-language-specialists | 24 | rust-engineer, typescript-pro, python-pro, golang-pro, java-architect |
| 03-infrastructure | 13 | cloud-architect, devops-engineer, kubernetes, terraform, sre |
| 04-quality-security | 13 | code-reviewer, security-auditor, penetration-tester, qa-expert |
| 05-data-ai | 13 | data-scientist, ml-engineer, llm-architect, prompt-engineer |
| 06-developer-experience | 11 | build-engineer, cli-developer, dx-optimizer, mcp-developer |
| 07-specialized-domains | 12 | blockchain, game-dev, embedded-systems, fintech, iot |
| 08-business-product | 12 | product-manager, business-analyst, scrum-master, ux-researcher |
| 09-meta-orchestration | 9 | agent-organizer, context-manager, workflow-orchestrator |
| 10-research-analysis | 7 | research-analyst, trend-analyst, search-specialist |

## Utility Skills — Triage

### KEEP (Generic / Meta)
| Skill | Lines | Reason |
|-------|-------|--------|
| skill-evaluator | 187 | Meta-skill for measuring skill effectiveness |
| learning-capture | 251 | Meta-skill for converting debug sessions into skills |
| technical-writing-narrative | 88 | Generic writing patterns |
| web-design-guidelines | 48 | Generic design principles |

### ARCHIVE (Project-Specific)
| Skill | Lines | Reason |
|-------|-------|--------|
| build-doctor | 145 | COREFORGE Webpack/PostCSS/Tauri-specific |
| tauri-ipc-wiring | 40 | HearthLink Tauri IPC-specific |
| tauri2-state-management | 38 | Tauri 2.x project-specific |
| tauri2-testing-validation | 32 | Tauri 2.x project-specific |
| tauri-launcher | 210 | Tauri application-specific |

### DISTILL (Extract generic value, discard COREFORGE specifics)
| Skill | Lines | Generic Value |
|-------|-------|---------------|
| code-reviewer | 483 | Review methodology, checklists (not COREFORGE patterns) |
| system-architect | 562 | Architecture patterns, security, performance (not COREFORGE) |
| accessibility-specialist | 566 | WCAG checklist, assistive tech (not COREFORGE components) |
| devops-engineer | 546 | CI/CD patterns, monitoring (not COREFORGE pipeline) |
| documentation-scribe | 773 | Doc standards, API doc patterns (not COREFORGE specifics) |
| project-planner | 602 | Requirements analysis, design (not COREFORGE) |
| agent-architect | 472 | Multi-agent patterns (not COREFORGE agents) |
| ui-correction-specialist | 360 | UI diagnosis methodology (not COREFORGE components) |
| voice-integration-specialist | 611 | Voice UI/UX patterns (broadly applicable) |
| skill-integration-system | 878 | Dynamic skill loading patterns (meta-useful) |

## Overlap Map

| Domain | Utility Skill | Third-Party Agent(s) | Action |
|--------|--------------|----------------------|--------|
| Code Review | code-reviewer | code-reviewer, qa-expert | MERGE: distill utility → enhance agent |
| Accessibility | accessibility-specialist | accessibility-tester | MERGE: utility has richer content |
| Architecture | system-architect | cloud-architect, microservices-architect | KEEP BOTH: different scope |
| DevOps | devops-engineer | devops-engineer, deployment-engineer | KEEP BOTH: project vs platform |
| Documentation | documentation-scribe | documentation-engineer, technical-writer | MERGE: distill utility → enhance agent |
| Planning | project-planner | product-manager, project-manager | KEEP BOTH: technical vs business |
| Agent Design | agent-architect | agent-organizer, multi-agent-coordinator | KEEP BOTH: design vs orchestration |

## Subagent Pairing Opportunities

### Ready Now
| Governance Skill | Existing Subagent | Status |
|-----------------|-------------------|--------|
| ql-debug | ql-fixer | PAIRED |
| ql-document | ql-technical-writer | AVAILABLE (not yet wired) |

### High Value (New Subagents)
| Governance Skill | Proposed Subagent | Benefit |
|-----------------|-------------------|---------|
| ql-audit | parallel-auditor | Run 7 audit passes concurrently |
| ql-implement | test-writer | Write TDD tests in parallel with planning |
| ql-substantiate | verification-auditor | Parallelize 5+ verification passes |

### Not Needed (Sequential by Design)
ql-plan, ql-bootstrap, ql-course-correct, ql-help, ql-repo-release, ql-repo-scaffold
