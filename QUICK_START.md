# MFHelper - Quick Start Guide

## Prerequisites

Before starting, make sure you have:
- **Python 3.9+** installed ([Download](https://www.python.org/downloads/))
  - Mac: `brew install python` (if using [Homebrew](https://brew.sh/))
- **Node.js 16+** (optional, only for frontend build tools) ([Download](https://nodejs.org/))
- **Git** (already have the code)

---

## 🚀 Quick Start (5 minutes)

### Step 1: Backend Setup

**For Windows (PowerShell):**
```powershell
# Navigate to backend directory
cd backend

# Create virtual environment (recommended)
python -m venv venv

# Activate virtual environment
.\venv\Scripts\Activate.ps1
# If you get execution policy error, run: Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

# Install dependencies
pip install -r requirements.txt

# Initialize database (creates SQLite database)
alembic upgrade head

# Start backend server
python -m uvicorn app.main:app --reload --port 8000
```

**For Mac/Linux (Terminal):**
```bash
# Navigate to backend directory
cd backend

# Create virtual environment (recommended)
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Initialize database (creates SQLite database)
alembic upgrade head

# Start backend server
python -m uvicorn app.main:app --reload --port 8000
```

**Backend will run on:** `http://localhost:8000`

---

### Step 2: Frontend Setup

Open a **new terminal** (keep backend running):

**For Windows:**
```powershell
# Navigate to frontend directory
cd frontend

# Start frontend server (using Python's built-in server)
python -m http.server 3000
```

**For Mac/Linux:**
```bash
# Navigate to frontend directory
cd frontend

# Start frontend server (using Python's built-in server)
python3 -m http.server 3000
```

**Frontend will run on:** `http://localhost:3000`

---

### Step 3: Access Application

Open your browser and go to:
**Windows:**
```powershell
cd backend

# Start server
python -m uvicorn app.main:app --reload --port 8000

# Run tests
pytest

# Check database users
python get_all_users.py

# Reset database (WARNING: Deletes all data)
python reset_database.py
```

**Mac/Linux:**
```bash
cd backend

# Start server
python3 -m uvicorn app.main:app --reload --port 8000

# Run tests
pytest

# Check database users
python3 get_all_users.py

# Reset database (WARNING: Deletes all data)
python3 reset_database.py
```

### Frontend

**Windows:**
```powershell
cd frontend

# Start server (Python)
python -m http.server 3000

# Or use Node.js (if installed)
npx http-server -p 3000
```

**Mac/Linux:**
```bash
cd frontend

# Start server (Python)
python3
└── doc/                # Documentation
```

---

## 🛠️ Common Commands

### Backend

```powershell
cd backend


**Windows:**
```powershell
curl http://localhost:8000/health
# Should return: {"status":"healthy"}
```

**Mac/Linux:**
```bashr
python -m uvicorn app.main:app --reload --port 8000

# Run tests
pytest

# Check database users
python get_all_users.py

# Reset database (WARNING: Deletes all data)
python reset_database.py
```

### Frontend

```powershell
cd frontend

# Start server (Python)
python -m http.server 3000

# Or use Node.js (if installed)
npx http-server -p 3000
```

---

## 🔍 Verify Installation

### Check Backend is Running:
```powershell
curl http://localhost:8000/health
# Should return: {"status":"healthy"}
```

### Check Frontend is Running:
Open browser: `http://localhost:3000`
- You should see the MFHelper landing page

---

## 🌐 Environment Variables (Optional)

**Windows:**
```powershell
# Backend (8000)
netstat -ano | findstr :8000
taskkill /PID <PID> /F

# Frontend (3000)
netstat -ano | findstr :3000
taskkill /PID <PID> /F
```

**Mac/Linux:**
```bash
# Find process using port
lsof -ti:8000  # Backend
lsof -ti:3000  # Frontend

# Kill process
kill -9 $(lsof -ti:8000)  # Backend
kill -9 $(lsof -ti:3000)  # Frontend
```

### Virtual Environment Issues

**Windows:**
```powershell
# If activation fails
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

# Deactivate and recreate
deactivate
Remove-Item -Recurse -Force venv
python -m venv venv
```

**Mac/Linux:**
```bash
# Deactivate and recreate
deactivate
rm -rf venv
python3 -m venv venv
source venv/bin/activate
```

### Database Errors

**Windows:**
```powershell
cd backend

# Delete and recreate database
Remove-Item mfhelper.db
alembic upgrade head
```

**Mac/Linux:**
```bash
cd backend

# Delete and recreate database
rm mfhelper.db
alembic upgrade head
```

### Module Import Errors

**Both platforms:**
```bash
# Reinstall dependencies
pip install --upgrade -r requirements.txt

**Windows:**
```powershell
ipconfig
# Look for "IPv4 Address" (e.g., 192.168.1.100)
```

**Mac:**
```bash
ifconfig | grep "inet " | grep -v 127.0.0.1
# Look for your local IP (e.g., 192.168.1.100)

# Or simpler:
ipconfig getifaddr en0  # WiFi
ipconfig getifaddr en1  # Ethernet
```

**Linux:**
```bash
hostname -I
# Or
ip addr show | grep "inet " | grep -v 127.0.0.1
```bash
# If you get SSL certificate errors with pip
/Applications/Python\ 3.x/Install\ Certificates.command
# Or install certificates package
pip install --upgrade certifi
```

### Mac-Specific: Permission Issues
```bash
# If you get permission errors
sudo chown -R $USER:staff backend/
chmod -R 755 backend/

## 🐛 Troubleshooting

### Port Already in Use
```powershell
# Backend (8000)
netstat -ano | findstr :8000
taskkill /PID <PID> /F

# Frontend (3000)
netstat -ano | findstr :3000
taskkill /PID <PID> /F
```

### Virtual Environment Issues
```powershell
# If activation fails
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

# Deactivate and recreate (Cmd+Option+J on Mac)
3. **Database Check**: 
   - Windows: `python backend/get_all_users.py`
   - Mac/Linux: `python3 backend/get_all_users.py`
4. **API Status**: `curl http://localhost:8000/health`

### Platform-Specific Notes

**Mac Users:**
- Use `python3` instead of `python` in all commands
- Use `pip3` if `pip` doesn't work
- Virtual environment activation: `source venv/bin/activate`
- May need to allow Python through Firewall (System Preferences → Security)

**Windows Users:**
- Use PowerShell (not CMD) for best experience
- May need to set execution policy for scripts
- Virtual environment activation: `.\venv\Scripts\Activate.ps1
python -m venv venv
```

### Database Errors
```powershell
cd backend

# Delete and recreate database
Remove-Item mfhelper.db
alembic upgrade head
```

### Module Import Errors
```powershell
# Reinstall dependencies
pip install --upgrade -r requirements.txt
```

---

## 📱 Access from Other Devices (Same Network)

### Find Your IP Address:
```powershell
ipconfig
# Look for "IPv4 Address" (e.g., 192.168.1.100)
```

### Update Backend CORS:
Edit `backend/app/main.py`:
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://192.168.1.100:3000"  # Add your IP
    ],
    ...
)
```

### Access from Other Device:
```
http://192.168.1.100:3000
```

---

## 🎯 What's Working

✅ User authentication (email/password)
✅ Guest user auto-creation
✅ Manual portfolio entry
✅ CAS PDF upload
✅ Excel/CSV upload
✅ Portfolio dashboard
✅ Overlap analysis
✅ Fund comparison tools
✅ Rebalancing calculator
✅ Goal planning
✅ Risk analysis

---

## 📚 Additional Resources

- **API Documentation**: `http://localhost:8000/docs` (Swagger UI)
- **Alternative API Docs**: `http://localhost:8000/redoc` (ReDoc)
- **Database Schema**: `backend/app/models/models.py`
- **Frontend Routes**: Check HTML files in `frontend/` folder

---

## 🆘 Need Help?

1. **Check Logs**: Terminal output from backend/frontend
2. **Browser Console**: F12 → Console tab (for frontend errors)
3. **Database Check**: `python backend/get_all_users.py`
4. **API Status**: `curl http://localhost:8000/health`

---

## 🚀 Production Deployment

For deployment to Render/Heroku/other platforms, see:
- `render.yaml` - Render configuration
- `requirements.txt` - Python dependencies
- `runtime.txt` - Python version
- `startup.sh` - Production startup script

---

**Happy Coding! 🎉**
