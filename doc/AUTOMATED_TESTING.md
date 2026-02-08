# Automated Testing Setup Guide

## Current State

### ✅ What's Automated
1. **GitHub Actions** - Runs E2E tests on push/PR
2. **Render Health Check** - Verifies server starts (`/health` endpoint)

### ❌ What's NOT Automated
1. Database connection tests
2. Database schema validation
3. Integration tests
4. Load/stress tests

---

## Options to Add Automated Database Testing

### Option 1: Add to Render Deployment (Recommended)

Add a post-build test command to verify database after deployment:

```yaml
# render.yaml
services:
  - type: web
    name: mfhelper
    buildCommand: |
      pip install -r requirements.txt
      python test_db_connection.py || echo "Warning: DB test failed"
    startCommand: "uvicorn app.main:app --host 0.0.0.0 --port $PORT"
```

**Pros:**
- ✅ Runs after every deployment
- ✅ Catches database issues immediately
- ✅ Non-blocking (warning only)

**Cons:**
- ⚠️ Adds ~10-30 seconds to deployment
- ⚠️ If test fails, deployment still proceeds

### Option 2: Strict Pre-Deploy CI/CD with GitHub Actions

Create a full pre-deployment test suite:

```yaml
# .github/workflows/pre-deploy.yml
name: Pre-Deploy Tests

on:
  push:
    branches: [ main ]

jobs:
  database-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Setup Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      
      - name: Install dependencies
        run: |
          cd backend
          pip install -r requirements.txt
      
      - name: Run database tests
        run: |
          cd backend
          python test_db_connection.py
      
      - name: Run integration tests
        run: |
          cd backend
          pytest tests/ -v
```

**Pros:**
- ✅ Blocks bad code from deploying
- ✅ Catches issues before production
- ✅ Full test suite

**Cons:**
- ⚠️ Slower deployments
- ⚠️ Requires test database setup

### Option 3: Git Pre-Push Hook

Run tests locally before pushing:

```bash
# .git/hooks/pre-push
#!/bin/bash
cd backend
python test_db_connection.py
if [ $? -ne 0 ]; then
  echo "Database tests failed! Push aborted."
  exit 1
fi
```

**Pros:**
- ✅ Catches issues before pushing
- ✅ Fast feedback loop
- ✅ No CI/CD cost

**Cons:**
- ⚠️ Developers can bypass with --no-verify
- ⚠️ Only tests local environment

### Option 4: Render Deploy Hooks (Beta)

Use Render's deploy hooks API:

```yaml
# In Render Dashboard:
# Services → mfhelper → Settings → Deploy Hooks
# Add: POST deploy hook that runs tests
```

**Pros:**
- ✅ Runs after successful deploy
- ✅ Can rollback on failure

**Cons:**
- ⚠️ Requires Render API setup
- ⚠️ Beta feature

---

## Recommended Setup (Hybrid Approach)

**1. Local Pre-Push Hook** (Fast Feedback)
```powershell
# Install pre-push hook
./scripts/install-git-hooks.ps1
```

**2. GitHub Actions** (CI/CD Gate)
```yaml
# Runs on every push to main
# Blocks deployment if tests fail
```

**3. Render Health Check** (Basic Verification)
```yaml
# Already configured
healthCheckPath: /health
```

**4. Post-Deploy Smoke Test** (Optional)
```yaml
# Add to render.yaml buildCommand
python test_db_connection.py || echo "Warning"
```

---

## Implementation Steps

### Step 1: Add Database Tests to CI/CD

Create `.github/workflows/database-tests.yml`:
```yaml
name: Database Tests

on:
  push:
    branches: [ main ]
  pull_request:
    branches: [ main ]

jobs:
  test-database:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Setup Python 3.11
      uses: actions/setup-python@v4
      with:
        python-version: '3.11'
    
    - name: Install dependencies
      run: |
        cd backend
        pip install -r requirements.txt
    
    - name: Run database connection test
      run: |
        cd backend
        python test_db_connection.py
    
    - name: Run pytest suite
      run: |
        cd backend
        pytest tests/ -v --cov=app
```

### Step 2: Add to Render Deployment

Update `render.yaml`:
```yaml
services:
  - type: web
    buildCommand: |
      pip install -r requirements.txt
      echo "Running database tests..."
      python test_db_connection.py || true
```

### Step 3: Install Git Hooks

Create `scripts/install-git-hooks.ps1`:
```powershell
# Copy pre-push hook
Copy-Item .git-hooks/pre-push .git/hooks/pre-push
icacls .git/hooks/pre-push /grant Everyone:RX
Write-Host "Git hooks installed!"
```

Create `.git-hooks/pre-push`:
```bash
#!/bin/bash
cd backend
python test_db_connection.py
exit $?
```

---

## Testing Your Setup

### Test GitHub Actions
```powershell
# Push to main to trigger workflow
git add .
git commit -m "test: verify automated testing"
git push origin main

# Check workflow status
# Go to: https://github.com/YOUR_REPO/actions
```

### Test Render Deployment
```powershell
# Deploy triggers on push to main
git push origin main

# Check Render logs:
# https://dashboard.render.com → mfhelper → Logs
# Look for: "Running database tests..."
```

### Test Git Hook
```powershell
# Install hook
./scripts/install-git-hooks.ps1

# Try to push
git push origin main
# Should run test_db_connection.py first
```

---

## Monitoring & Alerts

### Option 1: GitHub Notifications
- Enable in: Settings → Notifications → Actions
- Get email/Slack alerts on test failures

### Option 2: Render Alerts
- Enable in: Render Dashboard → Services → Alerts
- Get notified on deployment failures

### Option 3: Sentry Integration
- Add SENTRY_DSN to environment
- Automatic error tracking and alerts

---

## Cost Considerations

| Option | Cost | Speed | Reliability |
|--------|------|-------|-------------|
| **Local Git Hook** | Free | Fast (1-5s) | Medium |
| **GitHub Actions** | Free (2000 min/mo) | Medium (30-60s) | High |
| **Render Build Tests** | Free | Medium (10-30s) | High |
| **Post-Deploy Hook** | Free | Slow (after deploy) | High |

**Recommended:** Use all 4 in layers for defense in depth!

---

## Troubleshooting

### Issue: GitHub Actions Failing

**Check:**
```powershell
# View workflow logs
# GitHub → Actions → Failed workflow → View logs
```

**Fix:**
```powershell
# Test locally first
cd backend
python test_db_connection.py
pytest tests/ -v
```

### Issue: Render Deployment Failing

**Check:**
```powershell
# Render Dashboard → Logs
# Look for build errors
```

**Fix:**
```yaml
# Make tests non-blocking temporarily
buildCommand: |
  pip install -r requirements.txt
  python test_db_connection.py || echo "Test warning"
```

### Issue: Git Hook Not Running

**Check:**
```powershell
# Verify hook is executable
icacls .git/hooks/pre-push
```

**Fix:**
```powershell
# Reinstall hook
./scripts/install-git-hooks.ps1
```

---

## Summary

**Current State:**
- ✅ E2E tests on GitHub Actions
- ✅ Health check on Render
- ❌ No database tests during deployment

**Recommended Next Steps:**
1. Add GitHub Actions database tests (5 min)
2. Update render.yaml with test command (2 min)
3. Install git pre-push hook (1 min)
4. Test all layers (10 min)

**Total Setup Time:** ~20 minutes
**Ongoing Maintenance:** Minimal

---

Want me to implement any of these options? Let me know which approach you prefer!
