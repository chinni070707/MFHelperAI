# Render API Key Setup Script
# This script helps you set up your Render API key for MCP

Write-Host "=====================================" -ForegroundColor Cyan
Write-Host "  Render MCP Server - API Key Setup" -ForegroundColor Cyan
Write-Host "=====================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "Step 1: Get Your Render API Key" -ForegroundColor Yellow
Write-Host "  1. Visit: https://dashboard.render.com/" -ForegroundColor White
Write-Host "  2. Click your profile icon (top right)" -ForegroundColor White
Write-Host "  3. Select 'Account Settings'" -ForegroundColor White
Write-Host "  4. Click 'API Keys' in the left sidebar" -ForegroundColor White
Write-Host "  5. Click 'Create API Key'" -ForegroundColor White
Write-Host "  6. Name it: 'MFHelper MCP'" -ForegroundColor White
Write-Host "  7. Copy the generated key (starts with 'rnd_')" -ForegroundColor White
Write-Host ""

Write-Host "Step 2: Enter Your API Key" -ForegroundColor Yellow
$apiKey = Read-Host "Paste your Render API key here (or press Enter to skip)"

if ($apiKey -and $apiKey.StartsWith("rnd_")) {
    # Set as user environment variable (permanent)
    [System.Environment]::SetEnvironmentVariable('RENDER_API_KEY', $apiKey, 'User')
    
    # Set for current session
    $env:RENDER_API_KEY = $apiKey
    
    Write-Host ""
    Write-Host "✅ API Key saved successfully!" -ForegroundColor Green
    Write-Host ""
    Write-Host "Important: You must RESTART VS Code for the changes to take effect!" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "After restarting VS Code:" -ForegroundColor Cyan
    Write-Host "  1. The Render MCP server should connect automatically" -ForegroundColor White
    Write-Host "  2. You can use @render commands in Copilot Chat" -ForegroundColor White
    Write-Host ""
    Write-Host "Test the connection with: @render" -ForegroundColor White
    Write-Host ""
} elseif ($apiKey) {
    Write-Host ""
    Write-Host "❌ Invalid API key format. Keys should start with 'rnd_'" -ForegroundColor Red
    Write-Host "   Please run this script again with a valid key." -ForegroundColor Yellow
    Write-Host ""
} else {
    Write-Host ""
    Write-Host "Skipped. Run this script again when you have your API key." -ForegroundColor Yellow
    Write-Host ""
}

Write-Host "Press any key to continue..."
$null = $Host.UI.RawUI.ReadKey('NoEcho,IncludeKeyDown')
