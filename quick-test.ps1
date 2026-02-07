# Quick Test Runner - Ensures clean test environment
# Checks server and runs Playwright tests

param(
    [string]$TestFile = "ui-revamp.spec.ts",
    [switch]$Headed,
    [switch]$Debug,
    [switch]$All
)

$ErrorActionPreference = "Stop"

Write-Host "🧪 MFHelper Quick Test Runner" -ForegroundColor Cyan
Write-Host "═══════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host ""

# Step 1: Check if server is running
Write-Host "📡 Checking server status..." -ForegroundColor Yellow
$serverRunning = netstat -ano | findstr ":8000" | findstr "LISTENING"
if (-not $serverRunning) {
    Write-Host "❌ Server is not running on port 8000!" -ForegroundColor Red
    Write-Host ""
    Write-Host "   Start the server first:" -ForegroundColor Yellow
    Write-Host "   .\start-server.ps1" -ForegroundColor Cyan
    Write-Host ""
    exit 1
}

# Count server instances
$serverCount = ($serverRunning | Measure-Object).Count
if ($serverCount -gt 2) {
    Write-Host "⚠️  Multiple server instances detected: $serverCount" -ForegroundColor Yellow
    Write-Host "   This may cause test failures!" -ForegroundColor Yellow
    Write-Host "   Run cleanup: .\cleanup-servers.ps1" -ForegroundColor Yellow
    Write-Host ""
    $continue = Read-Host "Continue anyway? (y/N)"
    if ($continue -notmatch '^[Yy]') {
        exit 1
    }
    Write-Host ""
}

Write-Host "✅ Server is running" -ForegroundColor Green
Write-Host ""

# Step 2: Navigate to tests
Set-Location "$PSScriptRoot\tests"

# Step 3: Build command
$cmd = "npx playwright test"

if (-not $All) {
    $cmd += " $TestFile"
    Write-Host "🎯 Test file: $TestFile" -ForegroundColor Cyan
} else {
    Write-Host "🎯 Running all tests" -ForegroundColor Cyan
}

$cmd += " --reporter=list --timeout=10000"

if ($Headed) {
    $cmd += " --headed"
    Write-Host "👁️  Mode: Headed (visible)" -ForegroundColor Cyan
}

if ($Debug) {
    $cmd += " --debug"
    Write-Host "🐛 Debug: Enabled" -ForegroundColor Cyan
}

Write-Host ""
Write-Host "▶️  Starting tests..." -ForegroundColor Yellow
Write-Host "─────────────────────────────────────────────────" -ForegroundColor DarkGray
Write-Host ""

# Run tests
$startTime = Get-Date
Invoke-Expression $cmd
$exitCode = $LASTEXITCODE
$endTime = Get-Date
$duration = $endTime - $startTime

Write-Host ""
Write-Host "─────────────────────────────────────────────────" -ForegroundColor DarkGray

if ($exitCode -eq 0) {
    Write-Host "✅ All tests passed!" -ForegroundColor Green
} else {
    Write-Host "❌ Tests failed!" -ForegroundColor Red
}

Write-Host "⏱️  Duration: $($duration.TotalSeconds.ToString('0.0'))s" -ForegroundColor Cyan
Write-Host ""

exit $exitCode
