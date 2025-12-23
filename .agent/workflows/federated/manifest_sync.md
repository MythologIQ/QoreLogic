---
name: Federated Manifest Synchronization
trigger: "Session start, before/after Parallel Tribunal execution"
scope: Personal
description: Maintains context state in .agent/staging/ for Governor-Judge coordination
---

# FEDERATED MANIFEST SYNCHRONIZATION

## PURPOSE

Maintains a lightweight context manifest for Governor-Judge coordination. Since Executor (Kilo) and Scrivener (Codex) are not automatable, this workflow focuses on staging area management.

---

## 1. INITIALIZATION

Check and create manifest if missing:

```powershell
$manifest = ".agent/staging/GOAL_MANIFEST.json"
if (!(Test-Path $manifest)) {
    @{
        version = "1.0"
        lastSync = (Get-Date).ToString("o")
        agents = @{
            governor = @{ status = "active"; model = "gemini" }
            judge = @{ status = "ready"; model = "claude" }
        }
        currentTask = $null
        auditHistory = @()
    } | ConvertTo-Json -Depth 3 | Out-File -Encoding utf8 $manifest
}
```

---

## 2. PRE-TRIBUNAL SYNC

Before starting a `/parallel_tribunal` workflow:

```powershell
# Clear previous audit artifacts
Remove-Item .agent/staging/judge_audit.md -ErrorAction SilentlyContinue

# Update manifest with current task
$manifest = Get-Content .agent/staging/GOAL_MANIFEST.json | ConvertFrom-Json
$manifest.lastSync = (Get-Date).ToString("o")
$manifest.currentTask = "[TASK_DESCRIPTION]"
$manifest | ConvertTo-Json -Depth 3 | Out-File -Encoding utf8 .agent/staging/GOAL_MANIFEST.json
```

---

## 3. POST-TRIBUNAL SYNC

After tribunal completion:

```powershell
# Archive audit result
$timestamp = (Get-Date).ToString("yyyyMMdd_HHmmss")
if (Test-Path .agent/staging/judge_audit.md) {
    if (!(Test-Path .agent/staging/archive)) {
        New-Item -ItemType Directory -Path .agent/staging/archive | Out-Null
    }
    Copy-Item .agent/staging/judge_audit.md ".agent/staging/archive/audit_$timestamp.md"
}

# Update manifest
$manifest = Get-Content .agent/staging/GOAL_MANIFEST.json | ConvertFrom-Json
$manifest.lastSync = (Get-Date).ToString("o")
$manifest.currentTask = $null
$manifest.auditHistory += @{ timestamp = $timestamp; result = "completed" }
$manifest | ConvertTo-Json -Depth 3 | Out-File -Encoding utf8 .agent/staging/GOAL_MANIFEST.json
```

---

## STAGING DIRECTORY STRUCTURE

```
.agent/
├── staging/
│   ├── GOAL_MANIFEST.json      # Context state
│   ├── judge_audit.md          # Current audit output
│   └── archive/                # Historical audits
├── locks/
│   └── Personal/               # Personal scope locks
└── workflows/
    └── federated/
        ├── parallel_tribunal.md
        └── manifest_sync.md
```

---

## INTEGRATION

This workflow is automatically invoked by `/parallel_tribunal`. Manual invocation is only needed for:

- Session recovery after crash
- Clearing stale state
- Viewing audit history
