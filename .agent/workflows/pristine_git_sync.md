---
description: Protocol for maintaining a valid git state
---

# Pristine Git Sync Protocol

This workflow MUST be triggered at the completion of any significant sub-task.

1.  **Cleanliness Check**

    - Command: `git status`
    - **Condition:** If changes exist (Modified/Untracked).

2.  **Commit Offer**

    - **Action:** Explicitly offer to commit the changes.
    - **Format:** "Task complete. Working tree has changes. Shall I commit with message: '[type]: [desc]'?"

3.  **Sync (Daily/Session Start)**
    - Command: `git fetch origin`
    - **Action:** Ensure local is not behind remote.
