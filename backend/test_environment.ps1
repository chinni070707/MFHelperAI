# Quick Database Test Script for MFHelper
# This script helps you quickly test local and production databases

Write-Host "`n╔══════════════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║       MFHelper - Database Environment Tester                    ║" -ForegroundColor Cyan
Write-Host "╚══════════════════════════════════════════════════════════════════╝`n" -ForegroundColor Cyan

# Function to test local database
function Test-LocalDatabase {
    Write-Host "`n🔧 Testing LOCAL Database (SQLite)..." -ForegroundColor Yellow
    Write-Host "=" * 70
    
    # Check if database file exists
    if (Test-Path ".\mfhelper.db") {
        Write-Host "✓ Database file exists: mfhelper.db" -ForegroundColor Green
        
        # Get file size
        $dbSize = (Get-Item ".\mfhelper.db").Length / 1KB
        Write-Host "✓ Database size: $([math]::Round($dbSize, 2)) KB" -ForegroundColor Green
        
        # Check tables using SQLite
        try {
            $tables = sqlite3 mfhelper.db ".tables" 2>$null
            if ($tables) {
                Write-Host "✓ Tables found: $tables" -ForegroundColor Green
            }
        }
        catch {
            Write-Host "⚠ SQLite3 not found - install from https://sqlite.org/download.html" -ForegroundColor Yellow
        }
    }
    else {
        Write-Host "✗ Database file not found!" -ForegroundColor Red
        Write-Host "  Run: uvicorn app.main:app --reload (creates database)" -ForegroundColor Yellow
    }
    
    # Test Python connection
    Write-Host "`nTesting Python database connection..." -ForegroundColor Cyan
    python test_db_connection.py
}

# Function to test production
function Test-ProductionDatabase {
    Write-Host "`n☁️  Testing PRODUCTION Database (Render.com)..." -ForegroundColor Yellow
    Write-Host "=" * 70
    
    # Test API health endpoint
    try {
        $response = Invoke-RestMethod -Uri "https://mfhelper.onrender.com/health" -TimeoutSec 10
        Write-Host "✓ Production server responding" -ForegroundColor Green
        Write-Host "  Status: $($response.status)" -ForegroundColor Gray
        Write-Host "  Database: $($response.database)" -ForegroundColor Gray
    }
    catch {
        Write-Host "✗ Production server not accessible" -ForegroundColor Red
        Write-Host "  Error: $_" -ForegroundColor Gray
    }
    
    # Show production URL
    Write-Host "`n🌐 Production URLs:" -ForegroundColor Cyan
    Write-Host "  App: https://mfhelper.onrender.com" -ForegroundColor Gray
    Write-Host "  API Docs: https://mfhelper.onrender.com/api/docs" -ForegroundColor Gray
    Write-Host "  Dashboard: https://dashboard.render.com" -ForegroundColor Gray
}

# Function to compare both
function Show-QuickComparison {
    Write-Host "`n📊 QUICK COMPARISON" -ForegroundColor Cyan
    Write-Host "=" * 70
    
    Write-Host "`nLocal (SQLite):" -ForegroundColor White
    Write-Host "  Database: " -NoNewline; Write-Host "mfhelper.db (file-based)" -ForegroundColor Green
    Write-Host "  URL: " -NoNewline; Write-Host "http://localhost:8000" -ForegroundColor Green
    Write-Host "  Start: " -NoNewline; Write-Host "uvicorn app.main:app --reload" -ForegroundColor Yellow
    Write-Host "  Reset: " -NoNewline; Write-Host "Remove-Item mfhelper.db" -ForegroundColor Yellow
    Write-Host "  Test: " -NoNewline; Write-Host "python test_db_connection.py" -ForegroundColor Yellow
    
    Write-Host "`nProduction (PostgreSQL):" -ForegroundColor White
    Write-Host "  Database: " -NoNewline; Write-Host "Render.com hosted" -ForegroundColor Green
    Write-Host "  URL: " -NoNewline; Write-Host "https://mfhelper.onrender.com" -ForegroundColor Green
    Write-Host "  Deploy: " -NoNewline; Write-Host "git push origin main" -ForegroundColor Yellow
    Write-Host "  Logs: " -NoNewline; Write-Host "Render Dashboard → Logs" -ForegroundColor Yellow
    Write-Host "  Monitor: " -NoNewline; Write-Host "https://dashboard.render.com" -ForegroundColor Yellow
}

# Function to show useful commands
function Show-UsefulCommands {
    Write-Host "`n💡 USEFUL COMMANDS" -ForegroundColor Cyan
    Write-Host "=" * 70
    
    Write-Host "`nLocal Development:" -ForegroundColor White
    Write-Host "  # Start server" -ForegroundColor Gray
    Write-Host "  uvicorn app.main:app --reload" -ForegroundColor Yellow
    
    Write-Host "`n  # Reset database" -ForegroundColor Gray
    Write-Host "  Remove-Item mfhelper.db" -ForegroundColor Yellow
    
    Write-Host "`n  # Add test data" -ForegroundColor Gray
    Write-Host "  python scripts/seed_database.py" -ForegroundColor Yellow
    
    Write-Host "`n  # View database" -ForegroundColor Gray
    Write-Host "  sqlite3 mfhelper.db" -ForegroundColor Yellow
    
    Write-Host "`n  # Count records" -ForegroundColor Gray
    Write-Host '  sqlite3 mfhelper.db "SELECT COUNT(*) FROM users;"' -ForegroundColor Yellow
    
    Write-Host "`nProduction:" -ForegroundColor White
    Write-Host "  # Deploy changes" -ForegroundColor Gray
    Write-Host "  git push origin main" -ForegroundColor Yellow
    
    Write-Host "`n  # View logs" -ForegroundColor Gray
    Write-Host "  # Go to: https://dashboard.render.com → Logs" -ForegroundColor Yellow
    
    Write-Host "`n  # Test health" -ForegroundColor Gray
    Write-Host "  curl https://mfhelper.onrender.com/health" -ForegroundColor Yellow
}

# Main menu
function Show-Menu {
    Write-Host "`nWhat would you like to test?" -ForegroundColor Cyan
    Write-Host "  1) Test Local Database (SQLite)" -ForegroundColor White
    Write-Host "  2) Test Production (Render.com)" -ForegroundColor White
    Write-Host "  3) Test Both" -ForegroundColor White
    Write-Host "  4) Show Comparison" -ForegroundColor White
    Write-Host "  5) Show Commands" -ForegroundColor White
    Write-Host "  6) Exit" -ForegroundColor White
    Write-Host ""
    
    $choice = Read-Host "Enter choice (1-6)"
    
    switch ($choice) {
        "1" { Test-LocalDatabase }
        "2" { Test-ProductionDatabase }
        "3" { 
            Test-LocalDatabase
            Test-ProductionDatabase
        }
        "4" { Show-QuickComparison }
        "5" { Show-UsefulCommands }
        "6" { 
            Write-Host "`nGoodbye! 👋`n" -ForegroundColor Green
            exit 
        }
        default {
            Write-Host "`n✗ Invalid choice. Please enter 1-6." -ForegroundColor Red
        }
    }
}

# Navigate to backend directory if not already there
if (-not (Test-Path ".\app\main.py")) {
    if (Test-Path ".\backend\app\main.py") {
        Set-Location backend
        Write-Host "📁 Changed to backend directory" -ForegroundColor Gray
    }
    else {
        Write-Host "✗ Error: Cannot find backend directory!" -ForegroundColor Red
        Write-Host "  Please run this script from the root or backend folder" -ForegroundColor Yellow
        exit 1
    }
}

# Main loop
do {
    Show-Menu
    Write-Host "`nPress any key to continue..." -ForegroundColor Gray
    $null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
    Clear-Host
    Write-Host "`n╔══════════════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
    Write-Host "║       MFHelper - Database Environment Tester                    ║" -ForegroundColor Cyan
    Write-Host "╚══════════════════════════════════════════════════════════════════╝`n" -ForegroundColor Cyan
} while ($true)
