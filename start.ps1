# MFHelper Start Script for Windows
# Run this in PowerShell: .\start.ps1

Write-Host "`n🚀 Starting MFHelper..." -ForegroundColor Green
Write-Host "=====================`n" -ForegroundColor Green

# Start Backend
Write-Host "🔥 Starting Backend Server (Port 8000)..." -ForegroundColor Cyan
$backend = Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd backend; .\venv\Scripts\Activate.ps1; python -m uvicorn app.main:app --reload --port 8000" -PassThru
Start-Sleep -Seconds 3

# Start Frontend
Write-Host "🌐 Starting Frontend Server (Port 3000)..." -ForegroundColor Cyan
$frontend = Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd frontend; python -m http.server 3000" -PassThru
Start-Sleep -Seconds 2

Write-Host "`n✅ Servers Started!" -ForegroundColor Green
Write-Host "`nBackend:  http://localhost:8000" -ForegroundColor Yellow
Write-Host "Frontend: http://localhost:3000" -ForegroundColor Yellow
Write-Host "API Docs: http://localhost:8000/docs" -ForegroundColor Yellow

Write-Host "`n📱 Open your browser and go to:" -ForegroundColor Cyan
Write-Host "   http://localhost:3000`n" -ForegroundColor White

Write-Host "Press Ctrl+C in the server windows to stop.`n" -ForegroundColor Gray
