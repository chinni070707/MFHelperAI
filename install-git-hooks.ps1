#!/usr/bin/env pwsh
# Git Pre-Push Hook Installer
# Installs a pre-push hook that runs validation before pushing to Git

$ErrorActionPreference = "Stop"

Write-Host ""
Write-Host "Installing Git pre-push hook..." -ForegroundColor Cyan

$projectRoot = $PSScriptRoot
$hookPath = Join-Path $projectRoot ".git\hooks\pre-push"
$hookScript = Join-Path $projectRoot "pre-push-check.ps1"

# Check if pre-push-check.ps1 exists
if (-not (Test-Path $hookScript)) {
    Write-Host "Error: pre-push-check.ps1 not found!" -ForegroundColor Red
    exit 1
}

# Create the pre-push hook
$hookContent = @"
#!/bin/sh
# Git pre-push hook - runs validation before push

echo "Running pre-push validation..."

# Run PowerShell validation script
powershell.exe -ExecutionPolicy Bypass -File "./pre-push-check.ps1"

# If validation fails, prevent push
if [ `$? -ne 0 ]; then
    echo "Pre-push validation failed. Push aborted."
    exit 1
fi

echo "Pre-push validation passed. Continuing with push..."
exit 0
"@

# Write the hook file
Set-Content -Path $hookPath -Value $hookContent -Encoding UTF8 -NoNewline

# Make the hook executable (on Windows, this is automatic for .git/hooks)
Write-Host "Pre-push hook installed at: .git\hooks\pre-push" -ForegroundColor Green

# Test the hook
Write-Host ""
Write-Host "Testing the hook..." -ForegroundColor Yellow
& $hookScript

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "Hook installation successful!" -ForegroundColor Green
    Write-Host ""
    Write-Host "The validation script will now run automatically before every git push." -ForegroundColor Cyan
    Write-Host ""
    Write-Host "To bypass validation (not recommended): git push --no-verify" -ForegroundColor Gray
    Write-Host "To manually run validation anytime: .\pre-push-check.ps1" -ForegroundColor Gray
} else {
    Write-Host ""
    Write-Host "Hook installed but validation failed." -ForegroundColor Yellow
    Write-Host "Fix the issues shown above, then try again." -ForegroundColor Yellow
}
