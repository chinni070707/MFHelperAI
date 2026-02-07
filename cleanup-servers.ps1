# Cleanup Script - Kill all Python/Uvicorn/Node processes
# Run this before starting the server or tests to ensure clean slate

Write-Host "🧹 Cleaning up all server processes..." -ForegroundColor Cyan

# Kill Python processes
$pythonProcesses = Get-Process | Where-Object {$_.ProcessName -match "python"}
if ($pythonProcesses) {
    Write-Host "  Stopping $($pythonProcesses.Count) Python process(es)..." -ForegroundColor Yellow
    $pythonProcesses | Stop-Process -Force -ErrorAction SilentlyContinue
}

# Kill Uvicorn processes
$uvicornProcesses = Get-Process | Where-Object {$_.ProcessName -match "uvicorn"}
if ($uvicornProcesses) {
    Write-Host "  Stopping $($uvicornProcesses.Count) Uvicorn process(es)..." -ForegroundColor Yellow
    $uvicornProcesses | Stop-Process -Force -ErrorAction SilentlyContinue
}

# Kill Node processes (Playwright tests)
$nodeProcesses = Get-Process | Where-Object {$_.ProcessName -match "node"}
if ($nodeProcesses) {
    Write-Host "  Stopping $($nodeProcesses.Count) Node process(es)..." -ForegroundColor Yellow
    $nodeProcesses | Stop-Process -Force -ErrorAction SilentlyContinue
}

# Wait for processes to terminate
Start-Sleep -Seconds 2

# Check if port 8000 is still in use
$port8000 = netstat -ano | findstr ":8000" | findstr "LISTENING"
if ($port8000) {
    Write-Host "⚠️  Warning: Port 8000 still in use!" -ForegroundColor Red
    Write-Host $port8000
    
    # Extract PIDs and force kill
    $pids = $port8000 | ForEach-Object {
        if ($_ -match '\s+(\d+)\s*$') {
            $matches[1]
        }
    } | Select-Object -Unique
    
    foreach ($pid in $pids) {
        Write-Host "  Force killing PID $pid..." -ForegroundColor Red
        Stop-Process -Id $pid -Force -ErrorAction SilentlyContinue
    }
    
    Start-Sleep -Seconds 1
}

# Final check
$finalCheck = netstat -ano | findstr ":8000" | findstr "LISTENING"
if ($finalCheck) {
    Write-Host "❌ Failed to clean port 8000!" -ForegroundColor Red
    exit 1
} else {
    Write-Host "✅ All processes cleaned successfully!" -ForegroundColor Green
    Write-Host "   Port 8000 is now available." -ForegroundColor Green
}
