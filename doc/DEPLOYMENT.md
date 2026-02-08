# MFHelper Deployment Guide

## Current Setup

### Python Environment
- **Currently Using:** Global Python 3.13.7
- **Virtual Environment:** NOT using venv
- **Location:** `C:\Users\mahchi01\AppData\Local\Programs\Python\Python313`

### Why No venv Yet?
You're currently developing with global Python, which works fine for local development but **NOT recommended for production**.

---

## 🚨 Should You Use venv?

**YES!** Here's why:

| Without venv (Current) | With venv (Recommended) |
|------------------------|-------------------------|
| Packages installed globally | Isolated project dependencies |
| Risk of version conflicts | Clean, project-specific packages |
| Hard to replicate environment | Easy to deploy |
| Can break other Python projects | No conflicts with other projects |

---

## Setting Up venv (Do This Before Production)

### 1. Create Virtual Environment

```powershell
cd "C:\Users\mahchi01\OneDrive - Cadence Design Systems Inc\Documents\Sourcecode\MFHelper"

# Create venv folder
python -m venv venv

# Activate it
.\venv\Scripts\Activate.ps1

# Verify you're in venv (should show venv path)
python --version
which python
```

### 2. Install Dependencies

```powershell
# Make sure venv is activated
cd backend
pip install -r requirements.txt

# Verify installation
pip list
```

### 3. Update .gitignore

Add to `.gitignore`:
```
# Virtual Environment
venv/
.venv/
```

**NEVER commit venv to Git!** It's huge (~500MB) and platform-specific.

---

## 📦 Deployment Strategy

### What to Upload/Deploy:

#### ✅ INCLUDE:
1. **Source Code**
   - `backend/app/` - All Python code
   - `frontend/www/` - Static files
   - `backend/requirements.txt` - Package list

2. **Configuration**
   - `.env` file (with production secrets)
   - `backend/app/config.py`

3. **Database Schema**
   - Migration files (if using Alembic)
   - Initial schema SQL

#### ❌ EXCLUDE:
1. **venv/** - Recreate on server
2. **node_modules/** - Too large
3. **__pycache__/** - Generated files
4. **logs/** - Server logs
5. **uploads/** - User data (use S3/cloud storage)
6. **.pytest_cache/** - Test artifacts
7. **mfhelper.db** - Local database (use PostgreSQL in production)

---

## 🚀 Production Deployment Steps

### Option 1: Traditional Server (DigitalOcean, AWS EC2, Linode)

```bash
# 1. SSH into server
ssh user@your-server.com

# 2. Clone repository
git clone https://github.com/yourusername/MFHelper.git
cd MFHelper

# 3. Create venv on server
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# OR
.\venv\Scripts\Activate.ps1  # Windows

# 4. Install dependencies
cd backend
pip install -r requirements.txt

# 5. Set environment variables
cp .env.example .env
nano .env  # Edit with production values

# 6. Run migrations
python -m alembic upgrade head

# 7. Start server (with Gunicorn for production)
pip install gunicorn
gunicorn app.main:app --workers 4 --bind 0.0.0.0:8000
```

### Option 2: Docker (Recommended)

Create `Dockerfile`:
```dockerfile
FROM python:3.13-slim

WORKDIR /app

# Install dependencies
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY backend/app ./app

# Run
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

Deploy:
```bash
# Build image
docker build -t mfhelper .

# Run container
docker run -p 8000:8000 -e DATABASE_URL=postgresql://... mfhelper
```

### Option 3: Platform-as-a-Service (Easiest)

**Render.com** (Free tier available):
1. Connect GitHub repo
2. Set build command: `pip install -r backend/requirements.txt`
3. Set start command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
4. Add environment variables
5. Deploy ✅

**Railway.app**, **Fly.io**, **Heroku** work similarly.

---

## 🔐 Environment Variables for Production

Create `.env` file:
```bash
# Database (use PostgreSQL in production)
DATABASE_URL=postgresql://user:pass@localhost:5432/mfhelper

# Security
SECRET_KEY=your-super-secret-key-change-this
JWT_SECRET_KEY=another-secret-key

# APIs
CAMS_API_KEY=your-cams-key
KFINTECH_API_KEY=your-kfintech-key

# Environment
DEBUG=false
```

---

## 📊 Production Checklist

Before deploying to production:

- [ ] Create virtual environment
- [ ] Update `requirements.txt`: `pip freeze > requirements.txt`
- [ ] Add `.env` file with production secrets
- [ ] Switch from SQLite to PostgreSQL
- [ ] Set `DEBUG=false` in config
- [ ] Add proper logging (not just console)
- [ ] Set up HTTPS/SSL certificate
- [ ] Configure CORS properly
- [ ] Add rate limiting
- [ ] Set up backup strategy
- [ ] Configure monitoring (Sentry, LogRocket)
- [ ] Add `.gitignore` for venv, logs, uploads

---

## Quick Commands Reference

```powershell
# Create venv
python -m venv venv

# Activate venv (Windows PowerShell)
.\venv\Scripts\Activate.ps1

# Activate venv (Windows CMD)
venv\Scripts\activate.bat

# Activate venv (Linux/Mac)
source venv/bin/activate

# Deactivate
deactivate

# Install packages
pip install -r requirements.txt

# Save current packages
pip freeze > requirements.txt

# Check if in venv
which python  # Should show venv path
```

---

## Summary

**Current State:**
- ✅ Working locally with global Python
- ❌ Not using venv

**For Production:**
1. Create venv locally
2. Test with venv
3. Deploy code + requirements.txt (NOT venv folder)
4. Server creates its own venv and installs from requirements.txt

**TL;DR:** Never upload venv. Always upload requirements.txt and recreate venv on the server.
