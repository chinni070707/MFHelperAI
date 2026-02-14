# Setup Pre-commit Hook (PowerShell)
# This script installs the pre-commit hook to run tests before every commit

Write-Host ""
Write-Host "Setting up pre-commit hook..." -ForegroundColor Cyan
Write-Host ""

$hookPath = ".git\hooks\pre-commit"
$scriptPath = "scripts\pre-commit-hook.ps1"

# Check if .git directory exists
if (-not (Test-Path ".git")) {
    Write-Host "Error: Not a git repository. Please run this from the project root." -ForegroundColor Red
    Write-Host ""
    exit 1
}

# Create hooks directory if it doesn't exist
if (-not (Test-Path ".git\hooks")) {
    New-Item -ItemType Directory -Path ".git\hooks" -Force | Out-Null
}

# Create the pre-commit hook
$hookContent = @'
#!/bin/sh
# Git pre-commit hook - runs PowerShell script on Windows

if command -v powershell.exe >/dev/null 2>&1; then
    powershell.exe -ExecutionPolicy Bypass -File scripts/pre-commit-hook.ps1
elif command -v pwsh >/dev/null 2>&1; then
    pwsh -ExecutionPolicy Bypass -File scripts/pre-commit-hook.ps1
else
    echo "PowerShell not found. Running bash version..."
    bash scripts/pre-commit-hook.sh
fi
'@

# Write the hook file
Set-Content -Path $hookPath -Value $hookContent

Write-Host ""
Write-Host "Pre-commit hook installed successfully!" -ForegroundColor Green
Write-Host ""
Write-Host "The following checks will run before each commit:" -ForegroundColor Yellow
Write-Host "  - Database connection test" -ForegroundColor Gray
Write-Host "  - Backend unit tests" -ForegroundColor Gray
Write-Host "  - Python syntax validation" -ForegroundColor Gray
Write-Host ""
Write-Host "To skip the hook (not recommended), use:" -ForegroundColor Yellow
Write-Host "  git commit --no-verify" -ForegroundColor Gray
Write-Host ""
Write-Host "To test the hook now, run:" -ForegroundColor Yellow
Write-Host "  powershell -ExecutionPolicy Bypass -File $scriptPath" -ForegroundColor Gray
Write-Host ""
