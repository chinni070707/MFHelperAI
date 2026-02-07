# Start Server Script - Clean startup with process cleanup
# Ensures only ONE server instance is running

param(
    [switch]$Reload
)

$ErrorActionPreference = "Stop"

Write-Host "🚀 Starting MFHelper Server..." -ForegroundColor Cyan
Write-Host ""

# Step 1: Run cleanup
Write-Host "Step 1: Cleaning up existing processes..." -ForegroundColor Yellow
& "$PSScriptRoot\cleanup-servers.ps1"
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Cleanup failed!" -ForegroundColor Red
    exit 1
}
Write-Host ""

# Step 2: Activate virtual environment
Write-Host "Step 2: Activating virtual environment..." -ForegroundColor Yellow
$venvPath = "$PSScriptRoot\.venv\Scripts\Activate.ps1"
if (Test-Path $venvPath) {
    & $venvPath
    Write-Host "✅ Virtual environment activated" -ForegroundColor Green
} else {
    Write-Host "❌ Virtual environment not found at $venvPath" -ForegroundColor Red
    exit 1
}
Write-Host ""

# Step 3: Navigate to backend
Write-Host "Step 3: Navigating to backend directory..." -ForegroundColor Yellow
Set-Location "$PSScriptRoot\backend"
Write-Host "✅ Current directory: $(Get-Location)" -ForegroundColor Green
Write-Host ""

# Step 4: Start server
Write-Host "Step 4: Starting Uvicorn server..." -ForegroundColor Yellow
Write-Host "   Configuration:" -ForegroundColor Cyan
Write-Host "   - Host: 127.0.0.1" -ForegroundColor Cyan
Write-Host "   - Port: 8000" -ForegroundColor Cyan
Write-Host "   - Reload: $Reload" -ForegroundColor Cyan
Write-Host ""
Write-Host "🌐 Server will be available at: http://localhost:8000" -ForegroundColor Green
Write-Host "📊 API docs: http://localhost:8000/docs" -ForegroundColor Green
Write-Host ""
Write-Host "Press Ctrl+C to stop the server" -ForegroundColor Yellow
Write-Host "═══════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host ""

if ($Reload) {
    python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
} else {
    python -m uvicorn app.main:app --host 127.0.0.1 --port 8000
}
