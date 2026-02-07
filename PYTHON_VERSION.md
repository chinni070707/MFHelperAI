# Python Version Requirements

## Production (Render)
- **Python 3.11.9** (specified in `runtime.txt`)

## Development
- **Recommended: Python 3.11.9** (for consistency with production)
- **Works with: Python 3.11.x - 3.13.x**

## Installation Steps

### Windows
1. Download Python 3.11.9:
   ```
   https://www.python.org/ftp/python/3.11.9/python-3.11.9-amd64.exe
   ```

2. During installation:
   - ✅ Check "Add Python 3.11 to PATH"
   - ✅ Choose "Install for all users" (optional)

3. After installation, restart PowerShell

4. Run the setup script:
   ```powershell
   .\switch-to-python311.ps1
   ```

### Alternative: Manual Setup
```powershell
# Create virtual environment with Python 3.11
py -3.11 -m venv .venv

# Activate
.\.venv\Scripts\Activate.ps1

# Install dependencies
pip install -r backend\requirements.txt
pip install pytest pytest-asyncio pytest-cov httpx
```

### Verify Installation
```powershell
python --version
# Should show: Python 3.11.9
```

## Why Python 3.11.9?

- ✅ Supported by Render (3.13 not yet available)
- ✅ Stable for production
- ✅ Compatible with all dependencies
- ✅ Long-term support until October 2027
- ✅ Ensures local/production consistency
