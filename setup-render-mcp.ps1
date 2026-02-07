#!/usr/bin/env pwsh
# Setup Render API Key for MCP Server

Write-Host "=== Render MCP Server - API Key Setup ===" -ForegroundColor Cyan
Write-Host ""

# Check if API key is already set
$currentKey = [System.Environment]::GetEnvironmentVariable('RENDER_API_KEY', 'User')

if ($currentKey) {
    Write-Host "✓ Render API Key is already set" -ForegroundColor Green
    Write-Host "Key: $($currentKey.Substring(0, 8))..." -ForegroundColor Gray
    Write-Host ""
    
    $replace = Read-Host "Do you want to replace it? (y/N)"
    if ($replace -ne 'y' -and $replace -ne 'Y') {
        Write-Host "Keeping existing key." -ForegroundColor Yellow
        exit 0
    }
}

Write-Host ""
Write-Host "To get your Render API key:" -ForegroundColor Yellow
Write-Host "  1. Visit: https://dashboard.render.com/" -ForegroundColor White
Write-Host "  2. Click your profile > Account Settings > API Keys" -ForegroundColor White
Write-Host "  3. Create a new API key (name it 'MFHelper MCP')" -ForegroundColor White
Write-Host "  4. Copy the key (starts with 'rnd_')" -ForegroundColor White
Write-Host ""

# Prompt for API key
Write-Host "Paste your Render API key:" -ForegroundColor Cyan
$apiKey = Read-Host -AsSecureString
$apiKeyText = [System.Runtime.InteropServices.Marshal]::PtrToStringAuto(
    [System.Runtime.InteropServices.Marshal]::SecureStringToBSTR($apiKey)
)

# Validate key format
if (-not $apiKeyText.StartsWith('rnd_')) {
    Write-Host ""
    Write-Host "WARNING: Render API keys usually start with 'rnd_'" -ForegroundColor Yellow
    Write-Host "The key you entered: $($apiKeyText.Substring(0, [Math]::Min(10, $apiKeyText.Length)))..." -ForegroundColor Gray
    Write-Host ""
    
    $continue = Read-Host "Continue anyway? (y/N)"
    if ($continue -ne 'y' -and $continue -ne 'Y') {
        Write-Host "Setup cancelled." -ForegroundColor Red
        exit 1
    }
}

# Set environment variable
try {
    [System.Environment]::SetEnvironmentVariable('RENDER_API_KEY', $apiKeyText, 'User')
    Write-Host ""
    Write-Host "✓ API Key saved successfully!" -ForegroundColor Green
    Write-Host ""
    Write-Host "Key stored in: User Environment Variables" -ForegroundColor Gray
    Write-Host "Key preview: $($apiKeyText.Substring(0, 8))..." -ForegroundColor Gray
} catch {
    Write-Host ""
    Write-Host "ERROR: Failed to save API key" -ForegroundColor Red
    Write-Host $_.Exception.Message -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "=== Next Steps ===" -ForegroundColor Cyan
Write-Host ""
Write-Host "1. RESTART VS CODE (important!)" -ForegroundColor Yellow
Write-Host "   - Close and reopen VS Code for the change to take effect" -ForegroundColor White
Write-Host ""
Write-Host "2. Test the connection:" -ForegroundColor Yellow
Write-Host "   - Open Command Palette (Ctrl+Shift+P)" -ForegroundColor White
Write-Host "   - Search: 'MCP: Connect to Server'" -ForegroundColor White
Write-Host "   - Select: 'render'" -ForegroundColor White
Write-Host ""
Write-Host "3. Start using Render MCP:" -ForegroundColor Yellow
Write-Host "   - In Copilot Chat, try: '@render list my services'" -ForegroundColor White
Write-Host ""
Write-Host "Setup complete! 🎉" -ForegroundColor Green
