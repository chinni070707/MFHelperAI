<#
PowerShell startup script for MFHelper

Features:
- Ensures Ollama server is running (starts it if needed)
- Ensures the TinyLlama model is downloaded (pulls if missing)
- Starts the backend in a new PowerShell window
- Opens the frontend URL in the default browser

Usage:
  .\startup.ps1            # starts ollama, backend, opens UI
  .\startup.ps1 -NoBrowser # start services without opening browser

Notes:
- Requires PowerShell running with permission to start processes.
- Adjust the paths if Ollama is installed in a non-standard location.
#>

param(
    [switch]$NoBrowser
)

function Test-OllamaRunning {
    try {
        $resp = Invoke-RestMethod -Uri 'http://localhost:11434/api/tags' -Method Get -UseBasicParsing -TimeoutSec 2
        return $true
    } catch {
        return $false
    }
}

function Ensure-OllamaStarted {
    if (Test-OllamaRunning) {
        Write-Host "Ollama already running at http://localhost:11434"
        return $true
    }

    # Attempt to locate Ollama executable
    $ollamaExe = "$env:LOCALAPPDATA\Programs\Ollama\ollama.exe"
    if (-not (Test-Path $ollamaExe)) {
        Write-Warning "Could not find ollama.exe at $ollamaExe. Please ensure Ollama is installed and in PATH."
        return $false
    }

    Write-Host "Starting Ollama server... (new window)"
    Start-Process powershell -ArgumentList "-NoExit","-Command","& '$ollamaExe' serve" -WindowStyle Normal

    # Wait for Ollama to start
    $tries = 0
    while ($tries -lt 30) {
        Start-Sleep -Seconds 1
        if (Test-OllamaRunning) {
            Write-Host "Ollama is now running."
            return $true
        }
        $tries++
    }

    Write-Warning "Ollama did not start within expected time. Check 'ollama serve' output."
    return $false
}

function Ensure-TinyLlamaModel {
    try {
        $tags = Invoke-RestMethod -Uri 'http://localhost:11434/api/tags' -Method Get -UseBasicParsing
        $models = $tags.models | ForEach-Object { $_.name }
        if ($models -match 'tinyllama') {
            Write-Host "TinyLlama model present"
            return $true
        }
    } catch {
        Write-Verbose "Could not query Ollama tags: $_"
    }

    # Pull tinyllama if Ollama available
    $ollamaExe = "$env:LOCALAPPDATA\Programs\Ollama\ollama.exe"
    if (-not (Test-Path $ollamaExe)) {
        Write-Warning "Cannot pull model: ollama.exe not found."
        return $false
    }

    Write-Host "Pulling TinyLlama model (this may take a few minutes)..."
    $pull = Start-Process -FilePath $ollamaExe -ArgumentList "pull","tinyllama" -NoNewWindow -Wait -PassThru
    if ($pull.ExitCode -eq 0) {
        Write-Host "TinyLlama downloaded successfully."
        return $true
    }

    Write-Warning "TinyLlama pull failed (exit code $($pull.ExitCode))."
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

# Step 1: Ensure Ollama is running
$ollamaOk = Ensure-OllamaStarted
if ($ollamaOk) {
    # Step 2: Ensure model is present
    Ensure-TinyLlamaModel | Out-Null
} else {
    Write-Warning "Ollama not started. You may need to start it manually and run model pull."
}

# Step 3: Start backend
Start-Backend | Out-Null

# Step 4: Open GUI
if (-not $NoBrowser) {
    Start-Sleep -Seconds 2
    Write-Host "Opening frontend at http://localhost:8000"
    Start-Process "http://localhost:8000"
}

Write-Host "Startup script finished. Check the new PowerShell windows for Ollama and backend logs."
