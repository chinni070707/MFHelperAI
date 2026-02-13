# Render.com Environment Variable Setup Script
# This script helps you set environment variables on Render.com

Write-Host "`n🚀 Render.com Environment Setup for MFHelper" -ForegroundColor Cyan
Write-Host "=" -repeat 50 -ForegroundColor Gray

# Check if Render CLI is installed
$renderInstalled = Get-Command render -ErrorAction SilentlyContinue

if (-not $renderInstalled) {
    Write-Host "`n❌ Render CLI not found" -ForegroundColor Red
    Write-Host "`n📦 To install Render CLI:" -ForegroundColor Yellow
    Write-Host "   npm install -g @render-cli/render" -ForegroundColor White
    Write-Host "`n📚 Or use manual setup:" -ForegroundColor Yellow
    Write-Host "   https://dashboard.render.com" -ForegroundColor White
    Write-Host "`n" -ForegroundColor Gray
    exit 1
}

# Read .env file
$envPath = "backend\.env"
if (-not (Test-Path $envPath)) {
    Write-Host "`n❌ .env file not found at: $envPath" -ForegroundColor Red
    exit 1
}

# Parse environment variables
$envVars = @{}
Get-Content $envPath | ForEach-Object {
    if ($_ -match '^([^#][^=]+)=(.*)$') {
        $key = $matches[1].Trim()
        $value = $matches[2].Trim()
        $envVars[$key] = $value
    }
}

# Check required variables
$required = @("RESEND_API_KEY", "RESEND_FROM_EMAIL", "FRONTEND_URL")
$missing = @()

foreach ($var in $required) {
    if (-not $envVars.ContainsKey($var) -or [string]::IsNullOrWhiteSpace($envVars[$var])) {
        $missing += $var
    }
}

if ($missing.Count -gt 0) {
    Write-Host "`n⚠️ Missing required environment variables in .env:" -ForegroundColor Yellow
    $missing | ForEach-Object { Write-Host "   - $_" -ForegroundColor Red }
    exit 1
}

Write-Host "`n✅ Found all required variables" -ForegroundColor Green

# Get Render service info
Write-Host "`n🔍 Render Service Configuration:" -ForegroundColor Cyan
$serviceName = Read-Host "Enter your Render service name (e.g., mfhelper-backend)"

Write-Host "`n📝 Variables to be set:" -ForegroundColor Cyan
foreach ($var in $required) {
    $displayValue = $envVars[$var]
    if ($var -eq "RESEND_API_KEY") {
        $displayValue = $displayValue.Substring(0, [Math]::Min(10, $displayValue.Length)) + "***"
    }
    Write-Host "   $var = $displayValue" -ForegroundColor White
}

$confirm = Read-Host "`n❓ Proceed with setting these variables on Render? (y/n)"

if ($confirm -ne 'y') {
    Write-Host "`n❌ Cancelled" -ForegroundColor Yellow
    exit 0
}

Write-Host "`n🚀 Setting environment variables on Render..." -ForegroundColor Cyan

# Set environment variables using Render CLI
foreach ($var in $required) {
    $value = $envVars[$var]
    Write-Host "   Setting $var..." -ForegroundColor Gray
    
    try {
        $output = render env:set $var=$value --service=$serviceName 2>&1
        if ($LASTEXITCODE -eq 0) {
            Write-Host "   ✅ $var set successfully" -ForegroundColor Green
        } else {
            Write-Host "   ❌ Failed to set $var" -ForegroundColor Red
            Write-Host "   Error: $output" -ForegroundColor Red
        }
    } catch {
        Write-Host "   ❌ Error: $_" -ForegroundColor Red
    }
}

Write-Host "`n✅ Environment variables setup complete!" -ForegroundColor Green
Write-Host "`n📝 Note: Render will automatically redeploy your service" -ForegroundColor Yellow
Write-Host "   This may take 2-3 minutes..." -ForegroundColor Gray

Write-Host "`n🧪 Test your email service after deployment:" -ForegroundColor Cyan
Write-Host "   curl -X POST https://$serviceName.onrender.com/api/email/test-email \" -ForegroundColor White
Write-Host "     -H 'Content-Type: application/json' \" -ForegroundColor White
Write-Host "     -d '{""email"":""your@email.com""}'" -ForegroundColor White
Write-Host "`n" -ForegroundColor Gray
