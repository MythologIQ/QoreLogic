
# QoreLogic "One-Click" System Launcher
# Wraps the internal launcher/server.ps1 logic

$ErrorActionPreference = "Stop"

Write-Host "QoreLogic System Startup" -ForegroundColor Cyan
Write-Host "=============================" -ForegroundColor Gray

# 1. Check for Dependencies
if (-not (Get-Command "docker" -ErrorAction SilentlyContinue)) {
    Write-Warning "Docker is not found in PATH. Container capabilities will be limited."
}
if (-not (Get-Command "npm" -ErrorAction SilentlyContinue)) {
    Write-Warning "Node.js (npm) is not found. UI compilation may fail."
}

# 2. Build Frontend (if needed)
$FrontendDir = Join-Path $PSScriptRoot "dashboard\frontend"

if (Test-Path $FrontendDir) {
    $DistPath = Join-Path $FrontendDir "dist"
    if (-not (Test-Path $DistPath)) {
        Write-Host "First-time setup: Building UI assets..." -ForegroundColor Yellow
        Push-Location $FrontendDir
        try {
            # Fast install and build
            npm install --silent
            npm run build
        } catch {
            Write-Error "Failed to build frontend assets."
        } finally {
            Pop-Location
        }
    }
}

# 3. Launch the Control Plane
$LauncherScript = Join-Path $PSScriptRoot "launcher\server.ps1"

if (Test-Path $LauncherScript) {
    Write-Host "Starting Launcher Control Plane..." -ForegroundColor Green
    # Run the launcher script
    & $LauncherScript
} else {
    Write-Error "Critical Missing File: launcher/server.ps1"
}
