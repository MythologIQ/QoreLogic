---

name: ql-help
description: Quick reference that summarizes the purpose and usage of all QoreLogic commands. Use when: (1) Need to understand available commands, (2) Unsure which command to use, or (3) Looking for command overview.

# /ql-help - Command Summary

<skill>
  <trigger>/ql-help</trigger>
  <phase>ANY</phase>
  <persona>Governor</persona>
  <output>Concise summary of available QoreLogic commands</output>
</skill>

## Summary

| Command            | Purpose                                                                      | Typical When                                    |
| ------------------ | ---------------------------------------------------------------------------- | ----------------------------------------------- |
| `/ql-bootstrap`    | Initialize QoreLogic DNA and create baseline docs and `.agent/` scaffolding. | New project or first-time setup.                |
| `/ql-status`       | Diagnose lifecycle stage and next required action.                           | Any time you need current state.                |
| `/ql-audit`        | Judge review for L2/L3 risk work; produces PASS/VETO.                        | Before any high-risk change.                    |
| `/ql-implement`    | Execute work under KISS constraints after a PASS verdict.                    | After `/ql-audit` PASS.                         |
| `/ql-refactor`     | Apply scoped refactors with guardrails.                                      | After initial implementation or when requested. |
| `/ql-validate`     | Verify Merkle chain integrity and artifacts.                                 | Before delivery or handoff.                     |
| `/ql-substantiate` | Seal the session and record evidence.                                        | End of a completed work session.                |

## Notes

Use `/ql-status` first if you are unsure. Each command has full instructions in its corresponding `skills/*.md` file.
