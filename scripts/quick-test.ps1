# Quick Test Runner - Ensures clean test environment
# Checks server and runs Playwright tests

param(
    [string]$TestFile = "ui-revamp.spec.ts",
    [switch]$Headed,
    [switch]$Debug,
    [switch]$All
)

$ErrorActionPreference = "Stop"

Write-Host "[TEST] MFHelper Quick Test Runner" -ForegroundColor Cyan
Write-Host "===================================================" -ForegroundColor Cyan
Write-Host ""

# Step 1: Check if server is running
Write-Host "[CHECK] Checking server status..." -ForegroundColor Yellow
$serverRunning = netstat -ano | findstr ":8000" | findstr "LISTENING"
if (-not $serverRunning) {
    Write-Host "[ERROR] Server is not running on port 8000!" -ForegroundColor Red
    Write-Host ""
    Write-Host "   Start the server first:" -ForegroundColor Yellow
    Write-Host "   .\start-server.ps1" -ForegroundColor Cyan
    Write-Host ""
    exit 1
}

# Count server instances
$serverCount = ($serverRunning | Measure-Object).Count
if ($serverCount -gt 2) {
    Write-Host "[WARNING] Multiple server instances detected: $serverCount" -ForegroundColor Yellow
    Write-Host "   This may cause test failures!" -ForegroundColor Yellow
    Write-Host "   Run cleanup: .\cleanup-servers.ps1" -ForegroundColor Yellow
    Write-Host ""
    $continue = Read-Host "Continue anyway? (y/N)"
    if ($continue -notmatch '^[Yy]') {
        exit 1
    }
    Write-Host ""
}

Write-Host "[OK] Server is running" -ForegroundColor Green
Write-Host ""

# Step 2: Navigate to tests
Set-Location "$PSScriptRoot\tests"

# Step 3: Build command
$cmd = "npx playwright test"

if (-not $All) {
    $cmd += " $TestFile"
    Write-Host "[INFO] Test file: $TestFile" -ForegroundColor Cyan
} else {
    Write-Host "[INFO] Running all tests" -ForegroundColor Cyan
}

$cmd += " --reporter=list --timeout=10000"

if ($Headed) {
    $cmd += " --headed"
    Write-Host "[INFO] Mode: Headed (visible)" -ForegroundColor Cyan
}

if ($Debug) {
    $cmd += " --debug"
    Write-Host "[INFO] Debug: Enabled" -ForegroundColor Cyan
}

Write-Host ""
Write-Host "[RUN] Starting tests..." -ForegroundColor Yellow
Write-Host "-------------------------------------------------" -ForegroundColor DarkGray
Write-Host ""

# Run tests
$startTime = Get-Date
Invoke-Expression $cmd
$exitCode = $LASTEXITCODE
$endTime = Get-Date
$duration = $endTime - $startTime

Write-Host ""
Write-Host "-------------------------------------------------" -ForegroundColor DarkGray

if ($exitCode -eq 0) {
    Write-Host "[SUCCESS] All tests passed!" -ForegroundColor Green
} else {
    Write-Host "[ERROR] Tests failed!" -ForegroundColor Red
}

Write-Host "[INFO] Duration: $($duration.TotalSeconds.ToString('0.0'))s" -ForegroundColor Cyan
Write-Host ""

exit $exitCode
