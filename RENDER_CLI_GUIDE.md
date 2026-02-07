# Render CLI - Quick Reference Guide

## ✅ Setup Complete!

Your Render API is now configured and working. You can interact with your Render services directly from PowerShell.

## 🔑 API Key Status
- ✅ API key is set in environment variable `RENDER_API_KEY`
- ✅ Key is saved permanently in user environment

## 📦 Your Services

1. **mfhelper** (srv-d63aoqogjchc738uhge0)
   - URL: https://mfhelper.onrender.com
   - Region: Singapore
   - Status: Active (but deployments failing)
   
2. **PeopleRate** (srv-d4l6cq7pm1nc738kq0o0)
   - URL: https://peoplerate.onrender.com
   - Region: Oregon
   - Status: Active

## 🚀 Available Commands

```powershell
# List all services
.\render-cli.ps1 services

# Get detailed info for a specific service
.\render-cli.ps1 service srv-d63aoqogjchc738uhge0

# View deployment history
.\render-cli.ps1 deploys srv-d63aoqogjchc738uhge0

# View service logs
.\render-cli.ps1 logs srv-d63aoqogjchc738uhge0

# Show help
.\render-cli.ps1 help
```

## ⚠️ MFHelper Deployment Issues

All recent deployments for mfhelper have failed:
- 6 failed deployments in the last few hours
- Issues appear to be:
  - Python version compatibility
  - Build configuration problems
  - Update failures

### To Fix:
1. Check the deployment logs in Render dashboard
2. Verify `backend/requirements.txt` compatibility
3. Check `render.yaml` configuration
4. Review `build.sh` script

## 📝 Note About MCP Server

The `@modelcontextprotocol/server-render` package doesn't exist on npm yet. That's why we created this PowerShell CLI as an alternative. This CLI provides direct API access to Render with the same functionality.

## 🔧 Scripts Available

- `setup-render-api-key.ps1` - Configure your API key
- `render-cli.ps1` - Main CLI tool
- `debug-render-api.ps1` - Debug API responses

## 📚 Next Steps

1. **Fix MFHelper Deployment**: Investigate why deployments are failing
2. **Check Logs**: Use `.\render-cli.ps1 logs srv-d63aoqogjchc738uhge0`
3. **Review Configuration**: Check render.yaml and build scripts
4. **Test Locally**: Ensure the app works locally before deploying

## 🌐 Render Dashboard

For full management features, visit: https://dashboard.render.com
