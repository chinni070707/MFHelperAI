# Render MCP Usage Guide

Quick reference for managing Render deployments using the Render MCP (Model Context Protocol) integration.

## 🔧 Prerequisites

- Render API Key configured (see [RENDER_MCP_SETUP.md](../doc/RENDER_MCP_SETUP.md))
- Your service ID: `srv-d63aoqogjchc738uhge0`
- Your service name: `mfhelper`

## 📝 Common Operations

### 1. List All Services

```powershell
$RENDER_API_KEY = "rnd_AsV4jDRzKQCVLcZ4v0vWx5oxAnjm"
$headers = @{ 
    "Authorization" = "Bearer $RENDER_API_KEY"
    "Accept" = "application/json" 
}

$services = Invoke-RestMethod -Uri "https://api.render.com/v1/services" -Headers $headers -Method Get
$services | ForEach-Object { $_.service | Select-Object id, name, type } | Format-Table -AutoSize
```

### 2. Get Service Details

```powershell
$RENDER_API_KEY = "rnd_AsV4jDRzKQCVLcZ4v0vWx5oxAnjm"
$serviceId = "srv-d63aoqogjchc738uhge0"
$headers = @{ "Authorization" = "Bearer $RENDER_API_KEY" }

$service = Invoke-RestMethod -Uri "https://api.render.com/v1/services/$serviceId" -Headers $headers
$service.service | Select-Object name, type, repo, branch, url
```

### 3. View Environment Variables

```powershell
$RENDER_API_KEY = "rnd_AsV4jDRzKQCVLcZ4v0vWx5oxAnjm"
$serviceId = "srv-d63aoqogjchc738uhge0"
$headers = @{ "Authorization" = "Bearer $RENDER_API_KEY" }

$envVars = Invoke-RestMethod -Uri "https://api.render.com/v1/services/$serviceId/env-vars" -Headers $headers
$envVars | ForEach-Object { $_.envVar | Select-Object key, value } | Format-Table -AutoSize
```

### 4. Update Single Environment Variable

```powershell
$RENDER_API_KEY = "rnd_AsV4jDRzKQCVLcZ4v0vWx5oxAnjm"
$serviceId = "srv-d63aoqogjchc738uhge0"
$headers = @{ 
    "Authorization" = "Bearer $RENDER_API_KEY"
    "Accept" = "application/json"
    "Content-Type" = "application/json"
}

# Get all current env vars
$envVarsResponse = Invoke-RestMethod -Uri "https://api.render.com/v1/services/$serviceId/env-vars" -Headers $headers -Method Get

# Update the one you want to change
$envVars = $envVarsResponse | ForEach-Object { 
    @{ 
        key = $_.envVar.key
        value = if ($_.envVar.key -eq "DATABASE_URL") { 
            "sqlite:///./mfhelper.db"  # New value
        } else { 
            $_.envVar.value  # Keep existing
        } 
    } 
}

# Send update
$body = $envVars | ConvertTo-Json -Depth 3
Invoke-RestMethod -Uri "https://api.render.com/v1/services/$serviceId/env-vars" -Headers $headers -Method Put -Body $body
```

### 5. Check Recent Deployments

```powershell
$RENDER_API_KEY = "rnd_AsV4jDRzKQCVLcZ4v0vWx5oxAnjm"
$serviceId = "srv-d63aoqogjchc738uhge0"
$headers = @{ "Authorization" = "Bearer $RENDER_API_KEY" }

$deploys = Invoke-RestMethod -Uri "https://api.render.com/v1/services/$serviceId/deploys?limit=5" -Headers $headers
$deploys | ForEach-Object { 
    $_.deploy | Select-Object @{N='Status';E={$_.status}}, @{N='Created';E={$_.createdAt}}, @{N='Updated';E={$_.updatedAt}} 
} | Format-Table -AutoSize
```

### 6. Trigger Manual Deploy

```powershell
$RENDER_API_KEY = "rnd_AsV4jDRzKQCVLcZ4v0vWx5oxAnjm"
$serviceId = "srv-d63aoqogjchc738uhge0"
$headers = @{ 
    "Authorization" = "Bearer $RENDER_API_KEY"
    "Content-Type" = "application/json"
}

$body = '{"clearCache":"do_not_clear"}'
$deploy = Invoke-RestMethod -Uri "https://api.render.com/v1/services/$serviceId/deploys" -Headers $headers -Method Post -Body $body

Write-Host "Deploy triggered!" -ForegroundColor Green
$deploy.deploy | Select-Object id, status, createdAt | Format-List
```

### 7. Check Deploy Status

```powershell
$RENDER_API_KEY = "rnd_AsV4jDRzKQCVLcZ4v0vWx5oxAnjm"
$serviceId = "srv-d63aoqogjchc738uhge0"
$headers = @{ "Authorization" = "Bearer $RENDER_API_KEY" }

$deploys = Invoke-RestMethod -Uri "https://api.render.com/v1/services/$serviceId/deploys?limit=1" -Headers $headers
$deploys[0].deploy | Select-Object @{N='ID';E={$_.id}}, @{N='Status';E={$_.status}}, @{N='Started';E={$_.createdAt}} | Format-Table -AutoSize
```

### 8. Get Service Logs (Recent)

```powershell
$RENDER_API_KEY = "rnd_AsV4jDRzKQCVLcZ4v0vWx5oxAnjm"
$serviceId = "srv-d63aoqogjchc738uhge0"
$headers = @{ "Authorization" = "Bearer $RENDER_API_KEY" }

# Get logs from the last hour
$logs = Invoke-RestMethod -Uri "https://api.render.com/v1/services/$serviceId/logs" -Headers $headers
$logs
```

## 🎯 Quick Reference Commands

### Check if service is live:
```powershell
$RENDER_API_KEY = "rnd_AsV4jDRzKQCVLcZ4v0vWx5oxAnjm"; $serviceId = "srv-d63aoqogjchc738uhge0"; $headers = @{ "Authorization" = "Bearer $RENDER_API_KEY" }; $service = Invoke-RestMethod -Uri "https://api.render.com/v1/services/$serviceId" -Headers $headers; Write-Host "$($service.service.name): $($service.service.serviceDetails.url)" -ForegroundColor Cyan
```

### Get specific env var:
```powershell
$RENDER_API_KEY = "rnd_AsV4jDRzKQCVLcZ4v0vWx5oxAnjm"; $serviceId = "srv-d63aoqogjchc738uhge0"; $headers = @{ "Authorization" = "Bearer $RENDER_API_KEY" }; $envVars = Invoke-RestMethod -Uri "https://api.render.com/v1/services/$serviceId/env-vars" -Headers $headers; $envVars | Where-Object { $_.envVar.key -eq "DATABASE_URL" } | Select-Object -ExpandProperty envVar
```

### Latest deploy status:
```powershell
$RENDER_API_KEY = "rnd_AsV4jDRzKQCVLcZ4v0vWx5oxAnjm"; $serviceId = "srv-d63aoqogjchc738uhge0"; $headers = @{ "Authorization" = "Bearer $RENDER_API_KEY" }; $deploys = Invoke-RestMethod -Uri "https://api.render.com/v1/services/$serviceId/deploys?limit=1" -Headers $headers; $deploys[0].deploy.status
```

## 📊 Deploy Status Values

- `build_in_progress` - Currently building
- `update_in_progress` - Currently deploying
- `live` - Successfully deployed and running
- `deactivated` - Service stopped
- `build_failed` - Build failed
- `update_failed` - Deploy failed
- `canceled` - Deploy was canceled

## 🔐 Security Notes

- **Never commit the API key** to version control
- Store it in environment variables or secure vaults
- Rotate keys periodically from Render Dashboard
- Use separate keys for different environments (dev/prod)

## 🔗 Useful Links

- Render Dashboard: https://dashboard.render.com
- Render API Docs: https://render.com/docs/api
- Your Service: https://dashboard.render.com/web/srv-d63aoqogjchc738uhge0

## 📚 Related Documentation

- [RENDER_MCP_SETUP.md](../doc/RENDER_MCP_SETUP.md) - Initial setup guide
- [RENDER_DEPLOYMENT.md](./RENDER_DEPLOYMENT.md) - Full deployment guide
- [DEPLOYMENT.md](./DEPLOYMENT.md) - General deployment documentation
