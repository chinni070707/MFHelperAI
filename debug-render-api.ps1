# Quick debug script to see Render API raw response
$RENDER_API_KEY = $env:RENDER_API_KEY

if (-not $RENDER_API_KEY) {
    Write-Host "[!] Error: RENDER_API_KEY not set" -ForegroundColor Red
    exit 1
}

$headers = @{
    "Authorization" = "Bearer $RENDER_API_KEY"
    "Accept" = "application/json"
}

try {
    Write-Host "[*] Calling Render API..." -ForegroundColor Cyan
    $response = Invoke-RestMethod -Uri "https://api.render.com/v1/services" -Headers $headers
    
    Write-Host "`n[*] Raw Response:" -ForegroundColor Green
    $response | ConvertTo-Json -Depth 5
}
catch {
    Write-Host "[!] Error: $($_.Exception.Message)" -ForegroundColor Red
    if ($_.ErrorDetails.Message) {
        Write-Host $_.ErrorDetails.Message -ForegroundColor Red
    }
}
