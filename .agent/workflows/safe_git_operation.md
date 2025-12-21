---
description: Protocol for safe git interactions to prevent data loss
---

# Safe Git Operation Protocol

This workflow MUST be triggered before any destructive git command (checkout, reset, clean, revert).

1.  **Status Check**

    - Command: `git status`
    - **Stop Condition:** If output shows "Changes not staged for commit" or "Untracked files", you MUST STOP.
    - **Action:** Ask user: "Uncommitted changes detected. Proceeding will destroy them. Confirm?"

2.  **Execution**
    - Only if Status Check passes (Clean Tree) OR User Explicitly Overrides.
    - Run the intended git command.
