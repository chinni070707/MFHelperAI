#!/usr/bin/env pwsh
# Switch MFHelper to Python 3.11.9 for Render consistency

Write-Host "=== Switching MFHelper to Python 3.11.9 ===" -ForegroundColor Cyan
Write-Host ""

# Check if Python 3.11 is installed
Write-Host "Checking for Python 3.11..." -ForegroundColor Yellow
$python311 = py -3.11 --version 2>$null
if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: Python 3.11 not found!" -ForegroundColor Red
    Write-Host ""
    Write-Host "Please install Python 3.11.9 from:" -ForegroundColor Yellow
    Write-Host "https://www.python.org/ftp/python/3.11.9/python-3.11.9-amd64.exe" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "Installation tips:" -ForegroundColor Yellow
    Write-Host "  1. Check 'Add Python 3.11 to PATH'" -ForegroundColor White
    Write-Host "  2. Choose 'Install for all users' (optional)" -ForegroundColor White
    Write-Host "  3. After installation, restart PowerShell" -ForegroundColor White
    exit 1
}

Write-Host "✓ Found: $python311" -ForegroundColor Green
Write-Host ""

# Backup current venv if exists
if (Test-Path ".venv") {
    Write-Host "Backing up current virtual environment..." -ForegroundColor Yellow
    if (Test-Path ".venv.bak") {
        Remove-Item -Recurse -Force ".venv.bak"
    }
    Rename-Item ".venv" ".venv.bak"
    Write-Host "✓ Backup created: .venv.bak" -ForegroundColor Green
}

# Create new virtual environment with Python 3.11
Write-Host ""
Write-Host "Creating new virtual environment with Python 3.11.9..." -ForegroundColor Yellow
py -3.11 -m venv .venv

if ($LASTEXITCODE -eq 0) {
    Write-Host "✓ Virtual environment created" -ForegroundColor Green
} else {
    Write-Host "ERROR: Failed to create virtual environment" -ForegroundColor Red
    exit 1
}

# Activate virtual environment
Write-Host ""
Write-Host "Activating virtual environment..." -ForegroundColor Yellow
& ".\.venv\Scripts\Activate.ps1"

# Upgrade pip
Write-Host ""
Write-Host "Upgrading pip..." -ForegroundColor Yellow
python -m pip install --upgrade pip

# Install backend requirements
Write-Host ""
Write-Host "Installing backend dependencies..." -ForegroundColor Yellow
pip install -r backend\requirements.txt

# Install test dependencies
Write-Host ""
Write-Host "Installing test dependencies..." -ForegroundColor Yellow
pip install pytest pytest-asyncio pytest-cov httpx

Write-Host ""
Write-Host "=== Setup Complete! ===" -ForegroundColor Green
Write-Host ""
Write-Host "Python version verification:" -ForegroundColor Cyan
python --version
Write-Host ""
Write-Host "Your project is now using Python 3.11.9 (consistent with Render)" -ForegroundColor Green
Write-Host ""
Write-Host "To activate the environment in future sessions:" -ForegroundColor Yellow
Write-Host "  .\.venv\Scripts\Activate.ps1" -ForegroundColor White
Write-Host ""
Write-Host "Old environment backed up at: .venv.bak" -ForegroundColor Gray
Write-Host "(You can delete it once you verify everything works)" -ForegroundColor Gray
