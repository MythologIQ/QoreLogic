# qorelogic.ps1
# The Native Controller for QoreLogic Sovereign Gatekeeper
# Usage: .\qorelogic.ps1 attach <workspace_name>

param (
    [Parameter(Mandatory=$true, Position=0)]
    [ValidateSet("attach", "detach", "status", "build")]
    [string]$Command,

    [Parameter(Position=1)]
    [string]$WorkspaceName
)

$ErrorActionPreference = "Stop"
$ImageName = "qorelogic:native"

function Build-Image {
    Write-Host "🏗️  Building QoreLogic Native Image..." -ForegroundColor Cyan
    # Assumes run from repo root
    $DockerFile = "local_fortress/Dockerfile.native"
    if (-not (Test-Path $DockerFile)) {
        Write-Error "Dockerfile.native not found at $DockerFile"
    }
    docker build -f $DockerFile -t $ImageName local_fortress
    Write-Host "✅ Image Built: $ImageName" -ForegroundColor Green
}

function Attach-Workspace {
    if (-not $WorkspaceName) { Write-Error "Workspace Name required for attach." }
    
    $ContainerName = "qorelogic-$WorkspaceName"
    $VolumeName = "qorelogic-ledger-$WorkspaceName"
    
    Write-Host "🔗 Attaching QoreLogic to '$WorkspaceName'..." -ForegroundColor Cyan
    
    # 1. Create Ledger Volume (Persistence)
    docker volume create $VolumeName | Out-Null
    
    # 2. Run Container (Daemon)
    # Mounts current directory to /src
    # Mounts ledger volume to /app/ledger
    $CurrentDir = Get-Location
    
    Write-Host "   - Mount: $CurrentDir -> /src"
    Write-Host "   - Ledger: $VolumeName"
    
    docker run -d --name $ContainerName `
        --restart unless-stopped `
        -v "$($CurrentDir):/src" `
        -v "$($VolumeName):/app/ledger" `
        $ImageName `
        tail -f /dev/null  # Keep alive for exec
        
    # 3. Create Local Alias/Wrapper
    $WrapperContent = @"
@echo off
rem QoreLogic Check Wrapper
docker exec -w /src -i $ContainerName qorelogic-check %*
"@
    Set-Content -Path ".\qorelogic-check.bat" -Value $WrapperContent
    
    Write-Host "✅ Attached!" -ForegroundColor Green
    Write-Host "   - Daemon: Running (Container: $ContainerName)"
    Write-Host "   - Hook: .\qorelogic-check.bat created."
}

# Main Dispatch
switch ($Command) {
    "build" { Build-Image }
    "attach" { Attach-Workspace }
    "status" { docker ps --filter "name=qorelogic-" }
    "detach" { 
        if ($WorkspaceName) { docker rm -f "qorelogic-$WorkspaceName" }
        else { Write-Error "Specify workspace to detach." }
    }
}
