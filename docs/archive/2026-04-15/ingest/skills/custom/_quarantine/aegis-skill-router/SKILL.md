---
name: aegis-skill-router
description: Route a user request to the most appropriate skill(s) for the Aegis workspace. Use when the user asks which skill to use, requests an agent/skill router, or the task spans multiple domains (governance, UX audit, Tauri IPC, React/Next.js, documentation) and you must select the minimal skill set.
---

# Aegis Skill Router

## Overview

Select the minimal set of skills that best match the user's request and explain the choice. If no skill applies, say so and proceed without a skill.

## Routing Workflow

1. Check if the user explicitly named a skill. If yes, use it (or explain if missing/unavailable).
2. If the task is clearly within a listed skill's domain, select that skill.
3. If multiple skills apply, choose the minimal set that covers the request and state the order.
4. If the request is ambiguous, ask one clarifying question before proceeding.
5. If no skill applies, continue without one and state why.

## Evidence For Selection

- Use `references/skills-map.md` to map tasks to skills.
- Favor the most specific skill over general ones.
- Do not carry skills across turns unless the user re-mentions them.

## Output When Routing

- One sentence stating the chosen skill(s) and why.
- If multiple skills: state the order of use.
- If none: state "No skill applies" and proceed.

## Resources

### references/

- `references/skills-map.md`: Canonical map of available skills and triggers. Keep it updated as the skill list changes.

## Scope Boundary

**In scope**
- Choose the minimal skill set for a user request.
- Resolve overlap by selecting one primary skill and optional secondary skills.

**Out of scope**
- Implement product code changes itself.
- Replace domain skills like UX audit, Tauri IPC wiring, or testing execution.
