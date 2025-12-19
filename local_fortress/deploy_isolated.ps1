# deploy_isolated.ps1
# Builds QoreLogic Gatekeeper in a sterile Docker container.
# Prevents local pollution (No 'pip install' on host).

$ErrorActionPreference = "Stop"

Write-Host "🛡️  Initializing QoreLogic Sterile Build..." -ForegroundColor Cyan

# 1. Check for Docker
if (-not (Get-Command "docker" -ErrorAction SilentlyContinue)) {
    Write-Error "Docker is required for isolated deployment."
}

# 2. Setup Build Context
$ScriptDir = $PSScriptRoot
# Assuming script is run from local_fortress root
$DistDir = "$ScriptDir/dist"
$WhlFile = Get-ChildItem -Path $DistDir -Filter "qorelogic_gatekeeper-*.whl" | Select-Object -First 1

if (-not $WhlFile) {
    Write-Error "No .whl package found in $DistDir. Run 'python setup.py bdist_wheel' first?"
}

Write-Host "   - Artifact: $($WhlFile.Name)"

# Copy Dockerfile.dist to current scope for build
Copy-Item -Path "$ScriptDir/Dockerfile.dist" -Destination "$DistDir/Dockerfile" -Force

# 3. Build Container
Write-Host "📦 Building Sterile Container (qorelogic:latest)..." -ForegroundColor Yellow
# Build context is the dist/ folder where the wheel is
docker build -t qorelogic:latest "$DistDir"

# 4. Create Wrapper Scripts
Write-Host "🔗 Creating Wrapper Scripts..." -ForegroundColor Yellow

$WrapperContent = @"
@echo off
rem Wrapper for QoreLogic Check running inside Docker
docker run --rm -v "%CD%:/src" -w /src qorelogic:latest qorelogic-check %*
"@

$WrapperPath = Join-Path $ScriptDir "qorelogic-check.bat"
Set-Content -Path $WrapperPath -Value $WrapperContent

Write-Host "`n✅ Build Complete." -ForegroundColor Green
Write-Host "   - Container: qorelogic:latest"
Write-Host "   - Wrapper: $WrapperPath"
Write-Host "`nTo usage:"
Write-Host "   Local: .\qorelogic-check.bat --monitor your_file.py"
Write-Host "   (Add $ScriptDir to your PATH for global usage)"
