# Render API CLI - Direct interaction with Render.com
# Usage: .\render-cli.ps1 <command> [options]

param(
    [Parameter(Position=0)]
    [string]$Command = "help",
    
    [Parameter(Position=1)]
    [string]$ServiceId = "",
    
    [Parameter(ValueFromRemainingArguments=$true)]
    [string[]]$RemainingArgs
)

$RENDER_API_KEY = $env:RENDER_API_KEY
$RENDER_API_BASE = "https://api.render.com/v1"

if (-not $RENDER_API_KEY) {
    Write-Host "[!] Error: RENDER_API_KEY environment variable not set" -ForegroundColor Red
    Write-Host "Run: .\setup-render-api-key.ps1" -ForegroundColor Yellow
    exit 1
}

$headers = @{
    "Authorization" = "Bearer $RENDER_API_KEY"
    "Accept" = "application/json"
}

function Invoke-RenderAPI {
    param(
        [string]$Endpoint,
        [string]$Method = "GET",
        [object]$Body = $null
    )
    
    $uri = "$RENDER_API_BASE$Endpoint"
    
    try {
        $params = @{
            Uri = $uri
            Method = $Method
            Headers = $headers
            ContentType = "application/json"
        }
        
        if ($Body) {
            $params.Body = ($Body | ConvertTo-Json -Depth 10)
        }
        
        $response = Invoke-RestMethod @params
        return $response
    }
    catch {
        Write-Host "[!] API Error: $($_.Exception.Message)" -ForegroundColor Red
        if ($_.ErrorDetails.Message) {
            Write-Host $_.ErrorDetails.Message -ForegroundColor Red
        }
        return $null
    }
}

function Show-Services {
    Write-Host "\n[*] Fetching your Render services..." -ForegroundColor Cyan
    $response = Invoke-RenderAPI -Endpoint "/services"
    
    if ($response) {
        $services = $response
        if ($services.Count -eq 0) {
            Write-Host "\n[!] No services found" -ForegroundColor Yellow
            return
        }
        
        Write-Host "`n[*] Your Render Services:" -ForegroundColor Green
        Write-Host ("=" * 80) -ForegroundColor Gray
        
        foreach ($item in $services) {
            $service = $item.service
            $status = if ($service.suspended -eq "suspended") { "[SUSPENDED]" } else { "[ACTIVE]" }
            Write-Host "`nName:       " -NoNewline
            Write-Host $service.name -ForegroundColor Cyan
            Write-Host "ID:         $($service.id)" -ForegroundColor Gray
            Write-Host "Type:       $($service.type)"
            Write-Host "Status:     $status"
            Write-Host "Region:     $($service.serviceDetails.region)"
            Write-Host "URL:        $($service.serviceDetails.url)" -ForegroundColor Blue
            Write-Host "Branch:     $($service.branch)"
            Write-Host "Plan:       $($service.serviceDetails.plan)"
            Write-Host "Created:    $($service.createdAt)"
            Write-Host "Updated:    $($service.updatedAt)"
        }
        Write-Host "`n" + ("=" * 80) -ForegroundColor Gray
    }
}

function Show-Service {
    param([string]$Id)
    
    if (-not $Id) {
        Write-Host "Error: Service ID required" -ForegroundColor Red
        Write-Host "Usage: .\render-cli.ps1 service [service-id]" -ForegroundColor Yellow
        return
    }
    
    Write-Host "\n[*] Fetching service details..." -ForegroundColor Cyan
    $service = Invoke-RenderAPI -Endpoint "/services/$Id"
    
    if ($service) {
        Write-Host "\n[*] Service Details:" -ForegroundColor Green
        Write-Host ("=" * 80) -ForegroundColor Gray
        $service | ConvertTo-Json -Depth 10 | Write-Host
        Write-Host ("=" * 80) -ForegroundColor Gray
    }
}

function Show-Deploys {
    param([string]$Id)
    
    if (-not $Id) {
        Write-Host "Error: Service ID required" -ForegroundColor Red
        Write-Host "Usage: .\render-cli.ps1 deploys [service-id]" -ForegroundColor Yellow
        return
    }
    
    Write-Host "\n[*] Fetching deployments..." -ForegroundColor Cyan
    $response = Invoke-RenderAPI -Endpoint "/services/$Id/deploys"
    
    if ($response) {
        $deploys = $response
        Write-Host "\n[*] Recent Deployments:" -ForegroundColor Green
        Write-Host ("=" * 80) -ForegroundColor Gray
        
        foreach ($item in $deploys | Select-Object -First 10) {
            $deploy = $item.deploy
            $statusIcon = switch ($deploy.status) {
                "live" { "[OK]" }
                "build_failed" { "[FAIL]" }
                "update_failed" { "[FAIL]" }
                "deactivated" { "[PAUSED]" }
                default { "[PENDING]" }
            }
            
            Write-Host "`n$statusIcon Deploy ID: " -NoNewline
            Write-Host $deploy.id -ForegroundColor Cyan
            Write-Host "   Status:     $($deploy.status)"
            Write-Host "   Trigger:    $($deploy.trigger)"
            Write-Host "   Commit:     $($deploy.commit.message.Substring(0, [Math]::Min(80, $deploy.commit.message.Length)))"
            Write-Host "   Created:    $($deploy.createdAt)"
            Write-Host "   Started:    $($deploy.startedAt)"
            Write-Host "   Finished:   $($deploy.finishedAt)"
        }
        Write-Host "`n" + ("=" * 80) -ForegroundColor Gray
    }
}

function Show-Logs {
    param([string]$Id)
    
    if (-not $Id) {
        Write-Host "Error: Service ID required" -ForegroundColor Red
        Write-Host "Usage: .\render-cli.ps1 logs [service-id]" -ForegroundColor Yellow
        return
    }
    
    Write-Host "\n[*] Fetching recent logs..." -ForegroundColor Cyan
    $response = Invoke-RenderAPI -Endpoint "/services/$Id/logs"
    
    if ($response) {
        Write-Host "\n[*] Service Logs:" -ForegroundColor Green
        Write-Host ("=" * 80) -ForegroundColor Gray
        $response | Write-Host
        Write-Host ("=" * 80) -ForegroundColor Gray
    }
}

function Trigger-Deploy {
    param(
        [string]$Id,
        [switch]$ClearCache
    )
    
    if (-not $Id) {
        Write-Host "Error: Service ID required" -ForegroundColor Red
        Write-Host "Usage: .\render-cli.ps1 deploy [service-id] [-ClearCache]" -ForegroundColor Yellow
        return
    }
    
    Write-Host "\n[*] Triggering new deployment..." -ForegroundColor Cyan
    
    $clearCacheValue = if ($ClearCache.IsPresent) { "clear" } else { "do_not_clear" }
    $body = @{
        clearCache = $clearCacheValue
    }
    
    $response = Invoke-RenderAPI -Endpoint "/services/$Id/deploys" -Method "POST" -Body $body
    
    if ($response) {
        $deploy = $response.deploy
        Write-Host "\n[SUCCESS] Deployment triggered!" -ForegroundColor Green
        Write-Host ("=" * 80) -ForegroundColor Gray
        Write-Host "Deploy ID:  " -NoNewline
        Write-Host $deploy.id -ForegroundColor Cyan
        Write-Host "Status:     $($deploy.status)"
        Write-Host "Trigger:    $($deploy.trigger)"
        Write-Host "Created:    $($deploy.createdAt)"
        Write-Host ""
        Write-Host "Monitor progress at:" -ForegroundColor Yellow
        Write-Host "  Dashboard: https://dashboard.render.com/web/$Id" -ForegroundColor Blue
        Write-Host "  Or run: .\render-cli.ps1 deploys $Id" -ForegroundColor White
        Write-Host ("=" * 80) -ForegroundColor Gray
    }
}

function Show-Help {
    Write-Host ""
    Write-Host "Render CLI - Command Line Interface for Render.com" -ForegroundColor Cyan
    Write-Host ("=" * 60) -ForegroundColor Gray
    Write-Host ""
    Write-Host "Usage: .\render-cli.ps1 [command] [options]" -ForegroundColor White
    Write-Host ""
    Write-Host "Commands:" -ForegroundColor Yellow
    Write-Host "  services              List all your services"
    Write-Host "  service [id]          Show detailed info for a service"
    Write-Host "  deploys [id]          Show deployment history for a service"
    Write-Host "  deploy [id]           Trigger a new deployment"
    Write-Host "  logs [id]             Show recent logs for a service"
    Write-Host "  help                  Show this help message"
    Write-Host ""
    Write-Host "Examples:" -ForegroundColor Yellow
    Write-Host "  .\render-cli.ps1 services"
    Write-Host "  .\render-cli.ps1 service srv-abc123"
    Write-Host "  .\render-cli.ps1 deploys srv-abc123"
    Write-Host "  .\render-cli.ps1 deploy srv-abc123"
    Write-Host "  .\render-cli.ps1 deploy srv-abc123 -ClearCache"
    Write-Host "  .\render-cli.ps1 logs srv-abc123"
    Write-Host ""
    Write-Host "Environment:" -ForegroundColor Yellow
    Write-Host "  RENDER_API_KEY must be set (use .\setup-render-api-key.ps1)"
    Write-Host ""
}

# Main command router
switch ($Command.ToLower()) {
    "services" { Show-Services }
    "list" { Show-Services }
    "service" { Show-Service -Id $ServiceId }
    "get" { Show-Service -Id $ServiceId }
    "deploys" { Show-Deploys -Id $ServiceId }
    "deployments" { Show-Deploys -Id $ServiceId }
    "deploy" { Trigger-Deploy -Id $ServiceId -ClearCache:($RemainingArgs -contains "-ClearCache") }
    "trigger" { Trigger-Deploy -Id $ServiceId -ClearCache:($RemainingArgs -contains "-ClearCache") }
    "logs" { Show-Logs -Id $ServiceId }
    "help" { Show-Help }
    default { Show-Help }
}
