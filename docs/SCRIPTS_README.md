# Server & Test Management Scripts

Scripts to prevent multiple server instances and ensure clean test runs.

## 🧹 cleanup-servers.ps1

**Kills all Python/Uvicorn/Node processes** and frees port 8000.

```powershell
.\cleanup-servers.ps1
```

**When to use:**
- Before starting the server
- When tests are stuck
- When port 8000 is in use
- When you see "Address already in use" errors

**What it does:**
1. ✅ Stops all Python processes
2. ✅ Stops all Uvicorn processes  
3. ✅ Stops all Node processes
4. ✅ Force kills processes using port 8000
5. ✅ Verifies port 8000 is free

---

## 🚀 start-server.ps1

**Starts the server with automatic cleanup.**

```powershell
# Start server (production mode)
.\start-server.ps1

# Start with auto-reload (development mode)
.\start-server.ps1 -Reload
```

**Features:**
- ✅ Auto cleanup before start
- ✅ Activates virtual environment
- ✅ Ensures only ONE server runs
- ✅ Shows server URLs

**Starts at:**
- 🌐 http://localhost:8000
- 📊 http://localhost:8000/docs

---

## 🧪 quick-test.ps1

**Runs Playwright tests with server checks.**

```powershell
# Run UI revamp tests (default)
.\quick-test.ps1

# Run specific test file
.\quick-test.ps1 -TestFile "goal-planning.spec.ts"

# Run all tests
.\quick-test.ps1 -All

# Run with visible browser
.\quick-test.ps1 -Headed

# Debug mode
.\quick-test.ps1 -Debug
```

**Features:**
- ✅ Checks if server is running
- ✅ Warns about multiple servers
- ✅ Sets 10s timeout per test
- ✅ Shows test duration

**Expected timing:**
- Single test: **2-5 seconds**
- UI revamp suite: **45-60 seconds**
- All tests: **2-5 minutes**

---

## 🔄 Typical Workflow

### Development (with auto-reload)
```powershell
# Terminal 1: Start server
.\start-server.ps1 -Reload

# Terminal 2: Run tests
.\quick-test.ps1
```

### Production
```powershell
# Terminal 1: Start server
.\start-server.ps1

# Terminal 2: Run all tests
.\quick-test.ps1 -All
```

### When Things Go Wrong
```powershell
# 1. Clean everything
.\cleanup-servers.ps1

# 2. Start fresh server
.\start-server.ps1

# 3. Wait 5 seconds, then test
Start-Sleep 5
.\quick-test.ps1
```

---

## ⚠️ Common Issues

### "Address already in use"
```powershell
.\cleanup-servers.ps1
.\start-server.ps1
```

### Tests stuck/hanging
```powershell
# Stop tests (Ctrl+C)
# Then cleanup
.\cleanup-servers.ps1
.\start-server.ps1
Start-Sleep 5
.\quick-test.ps1
```

### Multiple servers detected
```powershell
.\cleanup-servers.ps1
# Then restart server
.\start-server.ps1
```

---

## 📊 Port 8000 Management

Check current port usage:
```powershell
netstat -ano | findstr ":8000" | findstr "LISTENING"
```

Should see **1-2 processes** (master + worker).  
If you see **3+ processes**, run cleanup!

---

## 🎯 Quick Reference

| Task | Command |
|------|---------|
| Clean slate | `.\cleanup-servers.ps1` |
| Start server | `.\start-server.ps1` |
| Start with reload | `.\start-server.ps1 -Reload` |
| Run tests | `.\quick-test.ps1` |
| Run all tests | `.\quick-test.ps1 -All` |
| Debug tests | `.\quick-test.ps1 -Debug -Headed` |
| Full reset | `.\cleanup-servers.ps1; .\start-server.ps1` |

---

**Created:** February 7, 2026  
**Purpose:** Prevent multiple server instances that cause test failures
