# MFHelper Test Setup and Execution Script
# Following webapp-testing skill guidelines

Write-Host "[TEST] MFHelper Playwright Test Setup" -ForegroundColor Cyan
Write-Host "=================================" -ForegroundColor Cyan
Write-Host ""

# Change to tests directory
$testsDir = "$PSScriptRoot"
Set-Location $testsDir

# Check if package.json exists
if (-not (Test-Path "package.json")) {
    Write-Host "[ERROR] package.json not found!" -ForegroundColor Red
    exit 1
}

# Install dependencies
Write-Host "[INSTALL] Installing dependencies..." -ForegroundColor Yellow
npm install

if ($LASTEXITCODE -ne 0) {
    Write-Host "[ERROR] Failed to install dependencies" -ForegroundColor Red
    exit 1
}

# Install Playwright browsers
Write-Host ""
Write-Host "[INSTALL] Installing Playwright browsers..." -ForegroundColor Yellow
npx playwright install

if ($LASTEXITCODE -ne 0) {
    Write-Host "[ERROR] Failed to install browsers" -ForegroundColor Red
    exit 1
}

# Create directories
Write-Host ""
Write-Host "[INFO] Creating test directories..." -ForegroundColor Yellow
New-Item -ItemType Directory -Force -Path "test-results/screenshots" | Out-Null
New-Item -ItemType Directory -Force -Path "test-results/html" | Out-Null

Write-Host ""
Write-Host "[SUCCESS] Setup complete!" -ForegroundColor Green
Write-Host ""
Write-Host "Start: Available commands:" -ForegroundColor Cyan
Write-Host "  npm test           - Run all tests" -ForegroundColor White
Write-Host "  npm run test:headed - Run with visible browser" -ForegroundColor White
Write-Host "  npm run test:ui    - Run with Playwright UI" -ForegroundColor White
Write-Host "  npm run test:debug - Debug tests" -ForegroundColor White
Write-Host "  npm run test:chrome - Run on Chrome only" -ForegroundColor White
Write-Host ""

# Ask user if they want to run tests now
$response = Read-Host "Would you like to run tests now? (y/n)"
if ($response -eq 'y' -or $response -eq 'Y') {
    Write-Host ""
    Write-Host "[TEST] Running tests..." -ForegroundColor Cyan
    npm test
}
