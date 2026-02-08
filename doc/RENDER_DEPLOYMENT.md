# Render.com Deployment Guide for MFHelper

Complete step-by-step instructions to deploy MFHelper to Render.com.

## 📋 Prerequisites

- GitHub account with MFHelper repository
- Render.com account (sign up at https://render.com - free tier available)
- Git installed locally

---

## 🚀 Quick Start Deployment

### Step 1: Prepare Your Repository

All configuration files are already created in your repository:
- ✅ `render.yaml` - Infrastructure as Code configuration
- ✅ `build.sh` - Build script for Render
- ✅ `backend/requirements.txt` - Updated with PostgreSQL driver
- ✅ `backend/app/config.py` - Auto-detects production environment

**Push to GitHub:**
```powershell
cd "C:\Users\mahchi01\OneDrive - Cadence Design Systems Inc\Documents\Sourcecode\MFHelper"

# Check git status
git status

# Add new deployment files
git add render.yaml build.sh backend/requirements.txt backend/app/config.py

# Commit changes
git commit -m "Add Render.com deployment configuration"

# Push to GitHub
git push origin main
```

---

### Step 2: Deploy to Render

#### Option A: Using Blueprint (Recommended - Automated)

1. **Go to Render Dashboard:**
   - Visit: https://dashboard.render.com
   - Sign in with GitHub

2. **Create New Blueprint:**
   - Click **"New +"** button (top right)
   - Select **"Blueprint"**
   - Click **"Connect GitHub"** and authorize Render
   - Select your **MFHelper** repository
   - Click **"Connect"**

3. **Review Configuration:**
   - Render will detect `render.yaml` automatically
   - Preview shows:
     - ✅ Web Service: `mfhelper`
     - ✅ PostgreSQL Database: `mfhelper-db`
     - ✅ Redis Cache: `mfhelper-redis`
   - Click **"Apply"**

4. **Wait for Deployment:**
   - Render will:
     - Create PostgreSQL database
     - Create Redis instance
     - Build your application (install dependencies)
     - Deploy web service
   - First build takes 3-5 minutes

5. **Your App is Live! 🎉**
   - Access at: `https://mfhelper-xxxxx.onrender.com`
   - Find URL in service dashboard

---

#### Option B: Manual Setup (Step-by-Step)

If you prefer manual control or want to customize:

##### 2.1 Create PostgreSQL Database

1. **Dashboard → "New +"  → "PostgreSQL"**
2. **Configure:**
   - Name: `mfhelper-db`
   - Database: `mfhelper`
   - User: `mfhelper`
   - Region: `Singapore` (or closest to you)
   - Plan: **Free** (90 days free, then $7/mo)
3. **Click "Create Database"**
4. **Copy Internal Database URL** (you'll need it for web service)

##### 2.2 Create Redis Instance (Optional but Recommended)

1. **Dashboard → "New +" → "Redis"**
2. **Configure:**
   - Name: `mfhelper-redis`
   - Region: `Singapore` (same as database)
   - Plan: **Free** (30 days free)
   - Max Memory Policy: `allkeys-lru`
3. **Click "Create Redis"**
4. **Copy Internal Redis URL**

##### 2.3 Create Web Service

1. **Dashboard → "New +" → "Web Service"**
2. **Connect Repository:**
   - Click "Connect GitHub"
   - Select **MFHelper** repository
   - Click "Connect"

3. **Configure Service:**
   ```
   Name: mfhelper
   Region: Singapore (same as database)
   Branch: main
   Root Directory: (leave empty)
   Environment: Python 3
   Build Command: pip install -r backend/requirements.txt
   Start Command: cd backend && uvicorn app.main:app --host 0.0.0.0 --port $PORT
   ```

4. **Select Plan:**
   - **Free**: Spins down after 15 min inactivity (starts in ~30 sec)
   - **Starter ($7/mo)**: Always-on, faster startup
   - Choose **Free** for testing

5. **Click "Create Web Service"** (don't deploy yet)

##### 2.4 Configure Environment Variables

1. **In your web service, go to "Environment" tab**
2. **Add these variables:**

```bash
# Required
DATABASE_URL=<paste Internal Database URL from step 2.1>
DEBUG=false
SECRET_KEY=<generate using command below>
JWT_SECRET_KEY=<generate using command below>

# Optional but recommended
REDIS_URL=<paste Internal Redis URL from step 2.2>

# Optional API keys (add when you have them)
CAMS_API_KEY=
KFINTECH_API_KEY=
SENTRY_DSN=
```

**Generate Secure Keys:**
```powershell
# Run this locally to generate random secure keys
python -c "import secrets; print('SECRET_KEY=' + secrets.token_urlsafe(32))"
python -c "import secrets; print('JWT_SECRET_KEY=' + secrets.token_urlsafe(32))"
```

3. **Click "Save Changes"**

##### 2.5 Deploy

1. **Go to "Manual Deploy" tab**
2. **Click "Deploy latest commit"**
3. **Monitor build logs** (3-5 minutes for first build)
4. **Wait for "Live" status** ✅

---

### Step 3: Initialize Database

**After first successful deployment:**

1. **Open Shell in Web Service:**
   - Go to your web service
   - Click **"Shell"** tab (left sidebar)
   - Wait for shell to connect

2. **Run Database Migrations:**
   ```bash
   cd backend
   alembic upgrade head
   ```

3. **Verify Tables Created:**
   ```bash
   python -c "from app.database import engine; from sqlalchemy import inspect; print(inspect(engine).get_table_names())"
   ```

You should see output like:
```
['users', 'portfolios', 'transactions', 'holdings', ...]
```

---

### Step 4: Test Your Deployment

1. **Visit Your App:**
   - URL: `https://mfhelper-xxxxx.onrender.com`
   - Should load the landing page

2. **Test API Health:**
   - Visit: `https://mfhelper-xxxxx.onrender.com/health`
   - Should return: `{"status": "healthy", ...}`

3. **Test API Docs:**
   - Visit: `https://mfhelper-xxxxx.onrender.com/api/docs`
   - Should see FastAPI Swagger UI

4. **Test Login/Signup:**
   - Visit: `https://mfhelper-xxxxx.onrender.com/signup.html`
   - Create a test account
   - Login and access dashboard

---

## 🔧 Configuration & Customization

### Update CORS Origins (Important!)

After deployment, update CORS to allow only your domain:

1. **Edit `backend/app/main.py`:**
   ```python
   origins = [
       "https://mfhelper-xxxxx.onrender.com",  # Your Render URL
       "https://mfhelper.com",  # Your custom domain (if any)
   ]
   ```

2. **Commit and push:**
   ```powershell
   git add backend/app/main.py
   git commit -m "Update CORS for production domain"
   git push origin main
   ```

3. **Render auto-deploys** (if enabled in render.yaml)

---

### Add Custom Domain (Optional)

1. **In Render Service Settings:**
   - Go to **"Settings"** → **"Custom Domain"**
   - Click **"Add Custom Domain"**
   - Enter: `app.mfhelper.com` or `mfhelper.com`

2. **In Your Domain Registrar (GoDaddy, Namecheap, etc.):**
   - Add CNAME record:
     ```
     Type: CNAME
     Name: app (or @ for root domain)
     Value: mfhelper-xxxxx.onrender.com
     TTL: 3600
     ```

3. **Wait for DNS Propagation** (5-30 minutes)

4. **Render automatically provisions SSL certificate** 🔒

---

### Disable AI Features (Recommended on Render)

Ollama AI requires local installation and won't work on Render free tier.

**Option 1: Already Disabled (Default)**
- `render.yaml` sets `AI_ENABLED=false`
- No changes needed

**Option 2: Use OpenAI Instead**
- Add to environment variables:
  ```
  AI_ENABLED=true
  AI_TYPE=openai
  OPENAI_API_KEY=sk-your-key-here
  ```

---

## 📊 Monitoring & Logs

### View Logs

1. **Real-time Logs:**
   - Service Dashboard → **"Logs"** tab
   - Shows all application output

2. **Search Logs:**
   - Use search box to filter by keyword
   - Filter by timestamp

### Health Monitoring

Render automatically monitors `/health` endpoint:
- Check frequency: Every 30 seconds
- If fails 3 times, service is restarted
- View uptime in "Metrics" tab

---

## 💰 Cost Breakdown

### Free Tier (Recommended for Testing)
- **Web Service**: Free, spins down after 15 min inactivity
- **PostgreSQL**: Free for 90 days, then $7/mo
- **Redis**: Free for 30 days, then $10/mo
- **Bandwidth**: 100 GB/month free
- **Total**: $0 initially, ~$17/mo after free periods

### Production Tier (Always-On)
- **Web Service**: Starter - $7/mo
- **PostgreSQL**: Standard - $7/mo
- **Redis**: Standard - $10/mo
- **Total**: ~$24/mo

### Free Tier Limitations
- **Spin Down**: Service sleeps after 15 min inactivity
- **Cold Start**: Takes ~30 sec to wake up
- **Monthly Hours**: 750 hours/month (about 1 month if always-on)

**Workaround for Free Tier:**
Use UptimeRobot to ping your app every 14 minutes to keep it awake.

---

## 🔒 Security Checklist

Before going to production:

- [ ] Set `DEBUG=false` in environment variables
- [ ] Generate strong `SECRET_KEY` and `JWT_SECRET_KEY`
- [ ] Update CORS origins to production domains only
- [ ] Enable HTTPS redirect (already configured in code)
- [ ] Review TrustedHost middleware settings
- [ ] Set up Sentry for error tracking (add `SENTRY_DSN`)
- [ ] Enable database backups (Render does this automatically)
- [ ] Review and limit API rate limits
- [ ] Set up monitoring alerts in Render

---

## 🐛 Troubleshooting

### Build Fails

**Error: "Could not find a version that satisfies the requirement..."**
- **Fix**: Check Python version compatibility
- Add to environment variables: `PYTHON_VERSION=3.13`

**Error: "No module named 'psycopg2'"**
- **Fix**: Ensure `psycopg2-binary` is in `requirements.txt`
- Already added ✅

### Database Connection Fails

**Error: "could not connect to server"**
- **Fix**: Verify `DATABASE_URL` is set correctly
- Use **Internal Connection String** (faster, free egress)
- Check database and web service are in same region

### App Not Loading

**Error: 404 or blank page**
- **Fix**: Check static files path in `app/main.py`
- Verify frontend files are in repository
- Check logs for path errors

### Free Tier Sleeping

**App is slow / times out**
- **Expected**: Free tier spins down after 15 min
- **Fix 1**: Upgrade to Starter plan ($7/mo)
- **Fix 2**: Use uptime monitor (UptimeRobot) to ping every 14 min

---

## 🚀 Continuous Deployment

### Auto-Deploy on Push (Already Enabled)

In `render.yaml`:
```yaml
autoDeploy: true
```

Every push to `main` branch triggers automatic deployment.

### Manual Deploy

1. Go to service dashboard
2. Click "Manual Deploy" → "Deploy latest commit"
3. Or deploy specific commit/branch

### Rollback

1. Go to "Events" tab
2. Find previous successful deploy
3. Click "Rollback to this version"

---

## 📈 Scaling & Performance

### Monitor Performance

**Metrics Tab shows:**
- CPU usage
- Memory usage
- Request rate
- Response time

### Upgrade Plan When:
- CPU consistently > 70%
- Memory consistently > 80%
- Response time > 2 seconds
- Monthly hours exceed 750 (free tier limit)

### Performance Optimizations Already Included:
- ✅ GZip compression (70% size reduction)
- ✅ Redis caching
- ✅ Rate limiting
- ✅ Connection pooling
- ✅ Static file serving

---

## 📞 Support

### Render Support
- **Community**: https://community.render.com
- **Docs**: https://render.com/docs
- **Status**: https://status.render.com

### MFHelper Issues
- Check application logs first
- Review error tracking in Sentry (if configured)
- Check database connectivity

---

## 🎯 Next Steps

After successful deployment:

1. **Test all features** - Signup, login, portfolio upload, analytics
2. **Set up monitoring** - Add Sentry DSN for error tracking
3. **Configure custom domain** - Make it professional
4. **Enable backups** - Render does daily backups automatically
5. **Optimize performance** - Monitor metrics and upgrade if needed
6. **Set up staging environment** - Create separate Render service for testing

---

## 📝 Quick Command Reference

```powershell
# Deploy changes
git add .
git commit -m "Update feature"
git push origin main  # Auto-deploys to Render

# Generate secret keys
python -c "import secrets; print(secrets.token_urlsafe(32))"

# Check local database URL
python -c "from backend.app.config import settings; print(settings.DATABASE_URL)"

# Test API locally before deploying
cd backend
..\\.venv\\Scripts\\Activate.ps1
uvicorn app.main:app --reload

# View Render logs (from dashboard)
# Or use Render CLI:
render logs -s mfhelper
```

---

## ✅ Post-Deployment Checklist

- [ ] App is accessible at Render URL
- [ ] `/health` endpoint returns healthy status
- [ ] API docs at `/api/docs` are working
- [ ] Signup/login functionality works
- [ ] Database is connected (TEST by creating user)
- [ ] Static files (CSS, JS) load correctly
- [ ] CORS is configured for production domain
- [ ] Environment variables are set correctly
- [ ] Monitoring and logging are active
- [ ] Custom domain configured (optional)
- [ ] SSL certificate is active (automatic)

---

## 🎉 You're Live!

Your MFHelper app is now running on Render.com!

**Share your app:**
- Public URL: `https://mfhelper-xxxxx.onrender.com`
- Custom domain: `https://mfhelper.com` (if configured)

**Monitor your app:**
- Render Dashboard: https://dashboard.render.com
- View logs, metrics, and manage services

**Keep improving:**
- Push updates to GitHub → Auto-deploys to Render
- Monitor performance and scale as needed
- Add features and iterate

---

**Need Help?**
- Check Render docs: https://render.com/docs/deploy-fastapi
- MFHelper issues: Review application logs in Render dashboard
- Community support: https://community.render.com
