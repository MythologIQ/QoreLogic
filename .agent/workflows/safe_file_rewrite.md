---
description: Protocol for safe large file rewrites to prevent regression
---

# Safe File Rewrite Protocol

This workflow MUST be triggered before rewriting any file > 100 lines.

1.  **Read Current State**

    - Command: `view_file` (Target File)
    - **Action:** Extract list of Key Imports, Exported Functions, and Critical Components.

2.  **Verification (Pre-Computation)**

    - Compare the `New Code Block` against the `Key Components List`.
    - **Stop Condition:** If a Key Component (e.g., `GlobalCommsStream`) is missing in the new code.
    - **Action:** Do NOT write. Regenerate code to include missing component.

3.  **Execution**

    - Command: `write_to_file` / `replace_file_content`
    - write the verified code.

4.  **Blindness Acknowledgement**
    - **Output:** "Applied changes to [File]. I cannot see the rendered UI; please verify [Visual Element] manually."
