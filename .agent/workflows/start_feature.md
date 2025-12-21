---
description: Protocol for initializing a new feature or task
---

# Feature Initialization Protocol

This workflow MUST be triggered when starting a new task defined in `task.md` or a user request implying a new feature.

1.  **Sync**

    - Command: `git fetch origin`
    - Command: `git status`
    - **Action:** If behind, ask to pull.

2.  **Branching**

    - **Rule:** NEVER commit to `main` for new features.
    - Command: `git checkout -b feature/[name]` or `fix/[issue]`.

3.  **Documentation (Optional)**
    - If this is a tracked bug/feature:
      - Command: `gh issue create`
      - Note the Issue ID.
