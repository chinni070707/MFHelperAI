# Render MCP Server Setup Guide

## ✅ What's Configured
- Render MCP server is configured in VS Code (`.vscode/settings.json`)
- Uses `@modelcontextprotocol/server-render` package via npx

## 🔑 Get Your Render API Token

1. **Go to Render Dashboard:**
   - Visit: https://dashboard.render.com/
   - Log in to your account

2. **Navigate to API Keys:**
   - Click your profile icon (top right)
   - Select **"Account Settings"**
   - Click **"API Keys"** in the left sidebar

3. **Create a New API Key:**
   - Click **"Create API Key"**
   - Name it: `MFHelper MCP` (or any name)
   - Copy the generated key (starts with `rnd_...`)
   - ⚠️ **Save it securely** - you won't see it again!

## 🔧 Set Up the API Key (Choose One Method)

### Method 1: User Environment Variable (Recommended for Personal Use)
```powershell
# Set permanently for your user account
[System.Environment]::SetEnvironmentVariable('RENDER_API_KEY', 'rnd_your_api_key_here', 'User')

# Restart VS Code after setting this
```

### Method 2: Project .env File (If using dotenv)
Create `.env` in project root:
```
RENDER_API_KEY=rnd_your_api_key_here
```
⚠️ **Make sure `.env` is in `.gitignore`**

### Method 3: PowerShell Profile (Session-based)
```powershell
# Edit your PowerShell profile
notepad $PROFILE

# Add this line:
$env:RENDER_API_KEY = "rnd_your_api_key_here"

# Restart PowerShell
```

## ✅ Test the Connection

After setting the API key:

1. **Restart VS Code** (very important!)

2. **Open Command Palette** (Ctrl+Shift+P)

3. **Search for:** `MCP: Connect to Server`

4. **Select:** `render`

5. **Verify in Output Panel:**
   - You should see "Connected to Render MCP"
   - No error messages

## 🚀 Using Render MCP

Once connected, you can:
- Check deployment status
- View logs
- Manage services
- Monitor builds
- Trigger deploys

**Example Commands in Copilot Chat:**
```
@render list my services
@render show deployment status for mfhelper
@render get logs for mfhelper
@render check build status
```

## 🔍 Troubleshooting

### "API key not found" error:
1. Verify the key is set: `$env:RENDER_API_KEY` in PowerShell
2. Restart VS Code completely
3. Check the key starts with `rnd_`

### "Cannot connect to Render" error:
1. Check your internet connection
2. Verify your Render account is active
3. Try regenerating the API key

### MCP Server not showing:
1. Reload VS Code window (Ctrl+R)
2. Check `.vscode/settings.json` exists
3. Verify Node.js is installed: `node --version`

## 📚 More Information
- Render MCP Documentation: https://github.com/modelcontextprotocol/servers
- Render API Docs: https://render.com/docs/api
