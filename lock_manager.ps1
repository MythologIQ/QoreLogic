param (
    [Parameter(Mandatory=$true)]
    [ValidateSet("Acquire", "Release", "Status", "Cleanup")]
    [string]$Action,

    [Parameter(Mandatory=$false)]
    [string]$AgentName = "Gemini",

    [Parameter(Mandatory=$false)]
    [ValidateSet("Personal", "Global", "Federated")]
    [string]$SystemScope = "Global",

    [Parameter(Mandatory=$false)]
    [int]$TimeoutSeconds = 300
)

# Create scoped lock directory: .agent/locks/{SystemScope}/
$LockDir = Join-Path $PSScriptRoot ".agent\locks\$SystemScope"
if (!(Test-Path $LockDir)) { New-Item -ItemType Directory -Path $LockDir -Force | Out-Null }

function Get-LockFile([string]$name) { Join-Path $LockDir "$name.lock" }

switch ($Action) {
    "Acquire" {
        $MyLock = Get-LockFile $AgentName
        $GlobalLock = Get-ChildItem $LockDir -Filter "*.lock" | Where-Object { $_.Name -ne "$AgentName.lock" }

        if ($GlobalLock) {
            Write-Host "CONFLICT: Workspace is locked by $($GlobalLock.BaseName). Waiting..." -ForegroundColor Yellow
            $Elapsed = 0
            while ($GlobalLock -and $Elapsed -lt $TimeoutSeconds) {
                Start-Sleep -Seconds 5
                $Elapsed += 5
                $GlobalLock = Get-ChildItem $LockDir -Filter "*.lock" | Where-Object { $_.Name -ne "$AgentName.lock" }
            }
            if ($GlobalLock) { Throw "TIMEOUT: Could not acquire lock. Agent $($GlobalLock.BaseName) is unresponsive." }
        }

        $LockData = @{ Agent = $AgentName; Timestamp = (Get-Date).ToString("o"); PID = $PID }
        $LockData | ConvertTo-Json | Out-File $MyLock
        Write-Host "SUCCESS: Lock acquired for $AgentName." -ForegroundColor Green
    }

    "Release" {
        $MyLock = Get-LockFile $AgentName
        if (Test-Path $MyLock) { 
            Remove-Item $MyLock -Force
            Write-Host "SUCCESS: Lock released for $AgentName." -ForegroundColor Cyan
        }
    }

    "Cleanup" {
        # Removes locks older than 10 minutes (stale agents)
        Get-ChildItem $LockDir -Filter "*.lock" | Where-Object { (New-TimeSpan -Start $_.LastWriteTime -End (Get-Date)).TotalMinutes -gt 10 } | Remove-Item -Force
        Write-Host "Cleanup complete." -ForegroundColor Gray
    }
}