#!/usr/bin/env pwsh
# Automated test runner script

Write-Host "🚀 MFHelper Automated Test Suite" -ForegroundColor Cyan
Write-Host "=================================" -ForegroundColor Cyan
Write-Host ""

# Check if backend server is running
Write-Host "📡 Checking backend server..." -ForegroundColor Yellow
$serverRunning = $false
try {
    $response = Invoke-WebRequest -Uri "http://localhost:8000/api/health" -Method Get -TimeoutSec 5 -UseBasicParsing
    if ($response.StatusCode -eq 200) {
        $serverRunning = $true
        Write-Host "✅ Backend server is running" -ForegroundColor Green
    }
} catch {
    Write-Host "❌ Backend server is NOT running" -ForegroundColor Red
    Write-Host "   Starting backend server..." -ForegroundColor Yellow
    
    # Start backend in background
    Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd backend; python -m uvicorn app.main:app --host 0.0.0.0 --port 8000" -WindowStyle Minimized
    
    Write-Host "   Waiting for server to start..." -ForegroundColor Yellow
    Start-Sleep -Seconds 5
    
    # Check again
    try {
        $response = Invoke-WebRequest -Uri "http://localhost:8000/api/health" -Method Get -TimeoutSec 5 -UseBasicParsing
        $serverRunning = $true
        Write-Host "✅ Backend server started successfully" -ForegroundColor Green
    } catch {
        Write-Host "❌ Failed to start backend server" -ForegroundColor Red
        Write-Host "   Please start it manually: cd backend; python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000" -ForegroundColor Yellow
        exit 1
    }
}

Write-Host ""

# Run tests
Write-Host "🧪 Running automated tests..." -ForegroundColor Yellow
Write-Host ""

# Check if node_modules exists
if (-not (Test-Path "tests/node_modules")) {
    Write-Host "📦 Installing test dependencies..." -ForegroundColor Yellow
    Push-Location tests
    npm install
    Pop-Location
    Write-Host "✅ Dependencies installed" -ForegroundColor Green
    Write-Host ""
}

# Run Playwright tests
Write-Host "▶️  Running Playwright E2E tests..." -ForegroundColor Cyan
Push-Location tests
npx playwright test --reporter=list
$testResult = $LASTEXITCODE
Pop-Location

Write-Host ""
if ($testResult -eq 0) {
    Write-Host "✅ ALL TESTS PASSED!" -ForegroundColor Green
} else {
    Write-Host "❌ SOME TESTS FAILED" -ForegroundColor Red
    Write-Host "   Check the output above for details" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "📊 Test Summary:" -ForegroundColor Cyan
Write-Host "   - Manual Entry Tests" -ForegroundColor White
Write-Host "   - File Upload Tests" -ForegroundColor White
Write-Host "   - Dashboard Core Tests" -ForegroundColor White
Write-Host "   - API Integration Tests" -ForegroundColor White
Write-Host "   - JavaScript Validation" -ForegroundColor White
Write-Host ""

exit $testResult
