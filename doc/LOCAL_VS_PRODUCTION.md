# Local vs Production Database - Complete Guide

## 📊 Overview

MFHelper uses **different databases** for development and production to balance ease of local development with production scalability.

| Aspect | **Local (localhost)** | **Production (Render.com)** |
|--------|----------------------|----------------------------|
| **Database** | SQLite (file-based) | PostgreSQL (cloud-hosted) |
| **Location** | `backend/mfhelper.db` | Render.com managed database |
| **Connection** | `sqlite:///./mfhelper.db` | `postgresql://user:pass@host/db` |
| **Pooling** | No pooling (single file) | Connection pool (20 base, 60 max) |
| **DEBUG Mode** | `True` (auto-detected) | `False` (via env var) |
| **Data Persistence** | Local file, easily deleted | Cloud-based, persistent |
| **Backups** | Manual copy of .db file | Render.com automated backups |
| **Performance** | Fast (local disk) | Network latency, but scalable |

---

## 🔧 How They Differ

### 1. **Database Type**

**Local (SQLite):**
```python
# backend/app/config.py
DATABASE_URL: str = "sqlite:///./mfhelper.db"
```
- ✅ Zero setup - just run the app
- ✅ File-based - easy to delete/reset
- ✅ Perfect for development/testing
- ❌ No connection pooling
- ❌ Not suitable for production scale

**Production (PostgreSQL):**
```python
# From Render.com environment
DATABASE_URL = "postgresql://user:password@host.render.com/mfhelper"
```
- ✅ Production-grade database
- ✅ Connection pooling (handles multiple users)
- ✅ Better concurrency and performance
- ✅ Cloud backups and monitoring
- ❌ Requires setup and credentials

### 2. **Connection Handling**

**Local (SQLite):**
```python
# backend/app/database.py
if "sqlite" in settings.DATABASE_URL:
    engine = create_engine(
        settings.DATABASE_URL,
        connect_args={"check_same_thread": False},
        poolclass=None,  # No pooling for SQLite
        echo=settings.DEBUG
    )
```

**Production (PostgreSQL):**
```python
else:
    engine = create_engine(
        settings.DATABASE_URL,
        poolclass=QueuePool,
        pool_size=20,           # 20 base connections
        max_overflow=40,        # + 40 overflow = 60 total
        pool_pre_ping=True,     # Health checks
        pool_recycle=3600,      # Recycle hourly
        echo=settings.DEBUG
    )
```

### 3. **Environment Detection**

The app **automatically detects** which environment it's in:

```python
# backend/app/config.py
if settings.DATABASE_URL.startswith("sqlite"):
    settings.DEBUG = True  # Force debug mode locally
    print("[DEBUG] Local Development Mode")
else:
    # Production - respect DEBUG env var
    print("[DEBUG] Production Mode")
```

---

## 🧪 How to Test Each

### A. Testing Locally (SQLite)

#### 1. **Fresh Start**

```powershell
# Navigate to backend folder
cd backend

# Delete old database (if exists)
Remove-Item mfhelper.db -ErrorAction SilentlyContinue

# Start the server (creates fresh DB)
uvicorn app.main:app --reload
```

#### 2. **Create Test Data**

```powershell
# Seed database with test users and portfolios
python scripts/seed_database.py
```

This creates:
- 3 test users (demo@mfhelper.com, test@example.com, investor@example.com)
- Sample portfolios with holdings
- Transaction history

#### 3. **Test the App**

```powershell
# Open browser
Start-Process http://localhost:8000

# OR test API directly
curl http://localhost:8000/api/health
```

#### 4. **Inspect Database**

```powershell
# View database contents
sqlite3 mfhelper.db

# In SQLite shell:
.tables                    # List all tables
SELECT * FROM users;       # View users
SELECT * FROM portfolios;  # View portfolios
SELECT * FROM holdings;    # View holdings
.exit                      # Exit SQLite
```

**OR use GUI tool:**
- Download [DB Browser for SQLite](https://sqlitebrowser.org/)
- Open `backend/mfhelper.db`
- Browse tables, run queries, export data

#### 5. **Test Upload Flow**

```powershell
# 1. Start server
uvicorn app.main:app --reload

# 2. Login as test user
# Browser: http://localhost:8000/login.html
# Email: demo@mfhelper.com
# Password: Demo@123

# 3. Upload CAS file with password
# 4. Check database was updated:
sqlite3 mfhelper.db "SELECT COUNT(*) FROM holdings;"
```

#### 6. **Reset Everything**

```powershell
# Delete database and start fresh
Remove-Item mfhelper.db
uvicorn app.main:app --reload
```

---

### B. Testing Production (Render.com)

#### 1. **Check Production Status**

```powershell
# Visit Render.com dashboard
Start-Process https://dashboard.render.com

# Or test API endpoint directly
curl https://mfhelper.onrender.com/api/health
```

#### 2. **View Logs**

```powershell
# In Render.com dashboard:
# 1. Go to your service
# 2. Click "Logs" tab
# 3. Watch real-time logs

# Look for database connection logs:
# [DEBUG] Production Mode: DEBUG=False
# [DEBUG] Database: postgresql...
```

#### 3. **Check Database Connection**

Production uses environment variables from Render:

```bash
# Render.com sets these automatically:
DATABASE_URL=postgresql://user:pass@host.render.com:5432/mfhelper_db
DEBUG=false
SECRET_KEY=<auto-generated>
JWT_SECRET_KEY=<auto-generated>
```

#### 4. **Test Production Upload**

```powershell
# 1. Go to production URL
Start-Process https://mfhelper.onrender.com

# 2. Sign up / Login
# 3. Upload CAS file
# 4. Check logs in Render dashboard for:
#    "✅ Successfully saved portfolio..."
```

#### 5. **Access Production Database**

```powershell
# If you setup PostgreSQL on Render:

# Get connection string from Render dashboard
# Services → mfhelper-db → Connect → External Connection

# Connect using psql:
psql "postgresql://user:pass@host.render.com:5432/mfhelper_db"

# In psql:
\dt                                    # List tables
SELECT * FROM users;                   # View users
SELECT COUNT(*) FROM portfolios;       # Count portfolios
\q                                     # Exit
```

#### 6. **Monitor Production**

```powershell
# Check metrics in Render dashboard:
# - CPU usage
# - Memory usage
# - Request count
# - Response times
# - Error rates
```

---

## 🔄 Migrating from SQLite to PostgreSQL

When you're ready to use PostgreSQL in production:

### 1. **Update render.yaml**

```yaml
# Uncomment PostgreSQL database section
databases:
  - name: mfhelper-db
    databaseName: mfhelper
    user: mfhelper
    plan: free  # or starter ($7/mo)
```

### 2. **Update Environment Variable**

```yaml
envVars:
  - key: DATABASE_URL
    fromDatabase:
      name: mfhelper-db
      property: connectionString
```

### 3. **Deploy**

```powershell
git add render.yaml
git commit -m "Add PostgreSQL database"
git push origin main
```

Render will:
1. Create PostgreSQL database
2. Set DATABASE_URL automatically
3. Restart your service
4. Run migrations (tables auto-created via SQLAlchemy)

### 4. **Verify**

```powershell
# Check logs in Render dashboard for:
# "Database: Production mode with connection pool (size: 20, max: 60)"
```

---

## 🐛 Troubleshooting

### Issue: "No portfolio data in dashboard after upload"

**Local:**
```powershell
# Check if data was saved
sqlite3 mfhelper.db "SELECT COUNT(*) FROM portfolios;"
sqlite3 mfhelper.db "SELECT COUNT(*) FROM holdings;"

# Check logs
# Look for: "✅ Successfully saved portfolio..."
```

**Production:**
```powershell
# Check Render logs for errors
# Look for: "❌ Error saving portfolio to database"

# Verify DATABASE_URL is set correctly
# In Render dashboard → Environment → DATABASE_URL
```

### Issue: "Connection pool timeout"

**Production only:**
```python
# Increase pool settings in backend/app/database.py
POOL_SETTINGS = {
    "pool_size": 30,        # Increase from 20
    "max_overflow": 50,     # Increase from 40
    "pool_timeout": 60,     # Increase from 30
}
```

### Issue: "Database locked" (SQLite only)

**Local:**
```powershell
# Close all connections
# Restart server
uvicorn app.main:app --reload

# Or delete and recreate
Remove-Item mfhelper.db
uvicorn app.main:app --reload
python scripts/seed_database.py
```

---

## 📝 Quick Reference Commands

### Local Testing
```powershell
# Start fresh
Remove-Item mfhelper.db; uvicorn app.main:app --reload

# Add test data
python scripts/seed_database.py

# View database
sqlite3 mfhelper.db

# Run tests
pytest tests/

# Check specific user's data
sqlite3 mfhelper.db "SELECT * FROM users WHERE email='demo@mfhelper.com';"
```

### Production Testing
```powershell
# View logs
# Go to Render dashboard → Logs

# Test health endpoint
curl https://mfhelper.onrender.com/api/health

# Test authentication
curl -X POST https://mfhelper.onrender.com/api/auth/login `
  -H "Content-Type: application/json" `
  -d '{\"email\":\"test@example.com\",\"password\":\"Test@123\"}'

# Check app version
curl https://mfhelper.onrender.com/api/version
```

---

## 🎯 Best Practices

### Development (Local)
1. ✅ Use SQLite for speed and simplicity
2. ✅ Add `.db` files to `.gitignore` (already done)
3. ✅ Reset database frequently to test fresh installs
4. ✅ Use seed script for consistent test data
5. ✅ Keep DEBUG=True for detailed error messages

### Production (Render)
1. ✅ Use PostgreSQL for scalability
2. ✅ Set DEBUG=False to hide sensitive errors
3. ✅ Use environment variables for secrets
4. ✅ Enable automated backups
5. ✅ Monitor logs and performance metrics
6. ✅ Test uploads with real CAS files
7. ✅ Set up error tracking (Sentry)

---

## 🚀 Summary

| Action | Local | Production |
|--------|-------|------------|
| **Database** | SQLite file | PostgreSQL cloud |
| **Start Server** | `uvicorn app.main:app --reload` | Auto-deploys via git push |
| **Add Test Data** | `python scripts/seed_database.py` | Manual signup/upload |
| **View Data** | `sqlite3 mfhelper.db` | `psql <connection_string>` or Render UI |
| **Reset Database** | `Remove-Item mfhelper.db` | Render Dashboard → Reset |
| **Check Logs** | Terminal output | Render Dashboard → Logs |
| **Debug** | DEBUG=True (auto) | DEBUG=False (env var) |

---

## 💡 Tips

1. **Always test locally first** before deploying to production
2. **Use `.env.example`** as a template for your local `.env` file
3. **Never commit** `.env` or `mfhelper.db` to git (already in `.gitignore`)
4. **Monitor production logs** after deployments to catch errors early
5. **Keep local and production schemas in sync** by using SQLAlchemy migrations

---

**Need Help?**
- Check logs: Local terminal or Render dashboard
- Review [DATABASE.md](./DATABASE.md) for schema details
- Review [DEPLOYMENT.md](./DEPLOYMENT.md) for deployment info
