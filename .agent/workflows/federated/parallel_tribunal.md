---
name: Federated Parallel Tribunal
trigger: "/parallel_tribunal [task]"
scope: Personal
description: Parallel multi-agent workflow orchestrating Governor (Gemini) and Judge (Claude CLI)
---

# FEDERATED PARALLEL TRIBUNAL WORKFLOW

> ⚠️ **MANDATORY EXECUTION**: When this workflow is triggered via `/parallel_tribunal`, the Governor (Gemini) **MUST** execute each numbered step. Do NOT skip steps. Do NOT just describe what should happen — actually run the commands.

---

## AGENTS

| Agent             | Model         | Role                           | Invocation                 |
| ----------------- | ------------- | ------------------------------ | -------------------------- |
| **Governor**      | Gemini        | Orchestration + Implementation | Native (this agent)        |
| **Judge (Quick)** | Claude Haiku  | Fast audits                    | `claude -p --model haiku`  |
| **Judge (Deep)**  | Claude Sonnet | Architectural review           | `claude -p --model sonnet` |

---

## EXECUTION STEPS

### STEP 1: ACQUIRE LOCK

**ACTION:** Run this command immediately.

```powershell
powershell -ExecutionPolicy Bypass -File .\lock_manager.ps1 -Action Acquire -AgentName Federated_Tribunal -SystemScope Personal
```

**STOP CONDITION:** If lock acquisition fails, STOP and notify user.

---

### STEP 2: IDENTIFY TARGET FILES

**ACTION:** Based on the user's task, identify the file(s) to audit.

- Use `find_by_name`, `grep_search`, or `view_file` to locate relevant files.
- Store the file path(s) for use in Step 3.

---

### STEP 3: SPAWN JUDGE (Claude)

**ACTION:** Run Claude CLI to audit the identified file(s).

**For accessibility/quick checks (use Haiku):**

```powershell
claude -p --model haiku --output-format text "Read [FILE_PATH] and [AUDIT_INSTRUCTION]. Be brief." | Out-File -Encoding utf8 .agent/staging/judge_audit.md
```

**For deep analysis (use Sonnet):**

```powershell
claude -p --model sonnet --output-format text "Analyze [FILE_PATH] for [DEEP_ISSUE]." | Out-File -Encoding utf8 .agent/staging/judge_audit.md
```

**WAIT:** This command runs in background. Use `command_status` to wait for completion.

---

### STEP 4: HARVEST JUDGE OUTPUT

**ACTION:** Read the audit results.

```powershell
Get-Content .agent/staging/judge_audit.md -Encoding utf8
```

**DECISION:**

- If **no issues** → Proceed to Step 5 (implementation)
- If **minor issues** → Note them, proceed to Step 5
- If **critical issues** → Report to user, await guidance
- If **architectural veto** → STOP. Do not implement.

---

### STEP 5: GOVERNOR IMPLEMENTS

**ACTION:** Based on the user's task AND the Judge's findings:

- Use `view_file` to read current code
- Use `replace_file_content` or `write_to_file` to apply changes
- If file > 100 lines, follow `/safe_file_rewrite` protocol

---

### STEP 6: VERIFY (Optional)

**ACTION:** Re-run Judge on modified file to confirm fixes.

```powershell
claude -p --model haiku --output-format text "Verify that [FILE_PATH] now addresses: [ORIGINAL_ISSUES]. Confirm fixed or list remaining issues." | Out-File -Encoding utf8 .agent/staging/judge_verify.md
```

---

### STEP 7: RELEASE LOCK

**ACTION:** Run this command to release the workspace lock.

```powershell
powershell -ExecutionPolicy Bypass -File .\lock_manager.ps1 -Action Release -AgentName Federated_Tribunal -SystemScope Personal
```

---

### STEP 8: REPORT

**ACTION:** Summarize to the user:

- What the Judge found
- What was implemented
- Any remaining concerns

---

## QUICK REFERENCE: AUDIT PROMPTS

| Audit Type    | Model  | Prompt Template                                                |
| ------------- | ------ | -------------------------------------------------------------- |
| Accessibility | haiku  | "List missing ARIA attributes in [FILE]. Be brief."            |
| Security      | sonnet | "Analyze [FILE] for XSS, injection, and auth vulnerabilities." |
| Code Quality  | haiku  | "Review [FILE] for code smells and complexity."                |
| Architecture  | sonnet | "Evaluate if [FILE] follows SOLID principles."                 |
| Performance   | haiku  | "Identify performance bottlenecks in [FILE]."                  |

---

## ENFORCEMENT

When Governor sees `/parallel_tribunal [task]`:

1. **DO NOT** just explain the workflow
2. **DO** execute Steps 1-8 in order
3. **DO** run actual commands via `run_command`
4. **DO** read actual outputs via `view_file` or `command_status`
5. **DO** implement actual fixes via code editing tools
