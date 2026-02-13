# MFHelper Setup Script for Windows
# Run this in PowerShell: .\setup.ps1

Write-Host "`n🚀 MFHelper Setup Script" -ForegroundColor Green
Write-Host "========================`n" -ForegroundColor Green

# Check Python
Write-Host "📦 Checking Python..." -ForegroundColor Cyan
try {
    $pythonVersion = python --version 2>&1
    Write-Host "✅ $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ Python not found. Please install Python 3.9+ from https://www.python.org/downloads/" -ForegroundColor Red
    exit 1
}

# Backend Setup
Write-Host "`n🔧 Setting up Backend..." -ForegroundColor Cyan
Set-Location backend

# Create virtual environment
if (!(Test-Path "venv")) {
    Write-Host "Creating virtual environment..." -ForegroundColor Yellow
    python -m venv venv
}

# Activate virtual environment
Write-Host "Activating virtual environment..." -ForegroundColor Yellow
& .\venv\Scripts\Activate.ps1

# Install dependencies
Write-Host "Installing Python packages..." -ForegroundColor Yellow
pip install -r requirements.txt -q

# Initialize database
Write-Host "Initializing database..." -ForegroundColor Yellow
if (!(Test-Path "mfhelper.db")) {
    alembic upgrade head
    Write-Host "✅ Database created" -ForegroundColor Green
} else {
    Write-Host "✅ Database already exists" -ForegroundColor Green
}

Set-Location ..

Write-Host "`n✨ Setup Complete!" -ForegroundColor Green
Write-Host "`nTo start the servers, run:" -ForegroundColor Cyan
Write-Host "  .\start.ps1`n" -ForegroundColor Yellow
