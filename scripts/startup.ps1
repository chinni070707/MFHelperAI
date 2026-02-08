<#
PowerShell startup script for MFHelper

Features:
- Starts the backend in a new PowerShell window
- Opens the frontend URL in the default browser

Usage:
  .\startup.ps1            # starts backend, opens UI
  .\startup.ps1 -NoBrowser # start backend without opening browser
#>

param(
    [switch]$NoBrowser,
    [switch]$ForceKill
)

function Get-PidByPort {
    param([int]$Port)
    try {
        $conn = Get-NetTCPConnection -LocalPort $Port -ErrorAction SilentlyContinue
        if ($conn) { return $conn.OwningProcess }
    } catch {
        return $null
    }
}

function Kill-ProcessIfExists {
    param([int]$Port, [string]$Name)
    $procPid = Get-PidByPort -Port $Port
    if ($procPid) {
        Write-Host "Found process listening on port $Port (PID: $procPid)"
        if ($ForceKill) {
            Write-Host "Force killing PID $procPid..."
            try { Stop-Process -Id $procPid -Force -ErrorAction Stop; Write-Host "Killed PID $procPid" } catch { Write-Warning "Failed to kill PID $procPid - $_" }
            return $true
        } else {
            $proc = Get-Process -Id $procPid -ErrorAction SilentlyContinue
            $procName = if ($proc) { $proc.ProcessName } else { $Name }
            $answer = Read-Host "Process $procName (PID $procPid) is using port $Port. Kill it? (y/N)"
            if ($answer -match '^[Yy]') {
                try { Stop-Process -Id $procPid -Force -ErrorAction Stop; Write-Host "Killed PID $procPid" } catch { Write-Warning "Failed to kill PID $procPid - $_" }
                return $true
            } else {
                Write-Warning "Leaving existing process running. This may conflict."
                return $false
            }
        }
    }
    return $false
}

function Start-Backend {
    $backendDir = Join-Path -Path (Get-Location) -ChildPath 'backend'
    if (-not (Test-Path $backendDir)) {
        Write-Warning "Backend directory not found at $backendDir"
        return $false
    }

    $cmd = "cd `"$backendDir`"; python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000"
    Write-Host "Starting backend in new PowerShell window..."
    Start-Process powershell -ArgumentList "-NoExit","-Command",$cmd -WindowStyle Normal
    return $true
}

Write-Host "=== MFHelper Startup Script ==="

# Kill existing backend on port 8000 if needed
if (Get-PidByPort -Port 8000) {
    Kill-ProcessIfExists -Port 8000 -Name 'uvicorn' | Out-Null
}

# Start backend
Start-Backend | Out-Null

# Open GUI
if (-not $NoBrowser) {
    Start-Sleep -Seconds 2
    Write-Host "Opening frontend at http://localhost:8000"
    Start-Process "http://localhost:8000"
}

Write-Host "Startup script finished. Check the backend PowerShell window for logs."
