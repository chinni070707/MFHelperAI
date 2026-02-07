# Monitor Render Deployment
# This script monitors a specific deployment until it completes

param(
    [string]$ServiceId = "srv-d63aoqogjchc738uhge0",
    [string]$DeployId = "dep-d63elpa4d50c73dl93ig",
    [int]$IntervalSeconds = 15,
    [int]$MaxChecks = 20
)

$RENDER_API_KEY = $env:RENDER_API_KEY

if (-not $RENDER_API_KEY) {
    Write-Host "[!] Error: RENDER_API_KEY not set" -ForegroundColor Red
    exit 1
}

$headers = @{
    "Authorization" = "Bearer $RENDER_API_KEY"
    "Accept" = "application/json"
}

Write-Host ""
Write-Host ("=" * 80) -ForegroundColor Cyan
Write-Host "  Monitoring Render Deployment" -ForegroundColor Cyan
Write-Host ("=" * 80) -ForegroundColor Cyan
Write-Host "Service ID:    $ServiceId" -ForegroundColor White
Write-Host "Deploy ID:     $DeployId" -ForegroundColor White
Write-Host "Check Interval: $IntervalSeconds seconds" -ForegroundColor White
Write-Host ("=" * 80) -ForegroundColor Cyan
Write-Host ""

$check = 0
$lastStatus = ""

while ($check -lt $MaxChecks) {
    $check++
    
    try {
        # Get latest deployment info
        $response = Invoke-RestMethod -Uri "https://api.render.com/v1/services/$ServiceId/deploys?limit=1" -Headers $headers
        $deploy = $response[0].deploy
        
        # Only show update if status changed
        if ($deploy.status -ne $lastStatus) {
            $timestamp = Get-Date -Format "HH:mm:ss"
            
            $statusIcon = switch ($deploy.status) {
                "live" { "[SUCCESS]" }
                "build_in_progress" { "[BUILDING]" }
                "update_failed" { "[FAILED]" }
                "build_failed" { "[FAILED]" }
                default { "[PENDING]" }
            }
            
            Write-Host "[$timestamp] Check $check/$MaxChecks - Status: " -NoNewline
            
            if ($deploy.status -eq "live") {
                Write-Host "$statusIcon $($deploy.status)" -ForegroundColor Green
            } elseif ($deploy.status -like "*failed*") {
                Write-Host "$statusIcon $($deploy.status)" -ForegroundColor Red
            } else {
                Write-Host "$statusIcon $($deploy.status)" -ForegroundColor Yellow
            }
            
            $lastStatus = $deploy.status
        }
        
        # Check if deployment is complete
        if ($deploy.status -eq "live") {
            Write-Host ""
            Write-Host ("=" * 80) -ForegroundColor Green
            Write-Host "  DEPLOYMENT SUCCESSFUL!" -ForegroundColor Green
            Write-Host ("=" * 80) -ForegroundColor Green
            Write-Host "URL: https://mfhelper.onrender.com" -ForegroundColor Cyan
            Write-Host "Finished at: $($deploy.finishedAt)" -ForegroundColor White
            Write-Host ""
            exit 0
        }
        
        if ($deploy.status -like "*failed*") {
            Write-Host ""
            Write-Host ("=" * 80) -ForegroundColor Red
            Write-Host "  DEPLOYMENT FAILED" -ForegroundColor Red
            Write-Host ("=" * 80) -ForegroundColor Red
            Write-Host "Check logs in dashboard for details" -ForegroundColor Yellow
            Write-Host "Dashboard: https://dashboard.render.com/web/$ServiceId" -ForegroundColor Blue
            Write-Host ""
            exit 1
        }
        
        # Wait before next check
        if ($check -lt $MaxChecks) {
            Start-Sleep -Seconds $IntervalSeconds
        }
    }
    catch {
        Write-Host "[!] Error checking deployment: $($_.Exception.Message)" -ForegroundColor Red
        Start-Sleep -Seconds $IntervalSeconds
    }
}

Write-Host ""
Write-Host "[!] Maximum checks reached. Deployment still in progress." -ForegroundColor Yellow
Write-Host "Continue monitoring at: https://dashboard.render.com/web/$ServiceId" -ForegroundColor Blue
Write-Host ""
