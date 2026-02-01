# 🚀 Manual Ollama + TinyLlama Setup Guide

## Step 1: Download & Install Ollama

### **Windows:**
```bash
# Option A: Automatic (recommended)
winget install Ollama.Ollama

# Option B: Manual download
# Visit: https://ollama.ai/download
# Run the installer
```

### **macOS:**
```bash
brew install ollama
```

### **Linux:**
```bash
curl https://ollama.ai/install.sh | sh
```

---

## Step 2: Verify Installation

```bash
# Check Ollama version
ollama --version

# Should output: ollama version X.X.X
```

---

## Step 3: Download TinyLlama Model

**Open terminal/PowerShell and run:**
```bash
ollama pull tinyllama
```

⏳ **This will take 3-10 minutes** (downloads 1.1GB)

You'll see progress:
```
pulling manifest
pulling 8ee4baf6bcd1
pulling 47e6ce2401ad
... [download progress] ...
verifying sha256 digest
writing manifest
success
```

---

## Step 4: Start Ollama Server

**Keep this terminal open and running:**
```bash
ollama serve
```

You should see:
```
Listening on [::]:11434
```

✅ **Ollama is now running and ready!**

---

## Step 5: Configure MFHelper

Create or update `.env` file in `backend/` directory:

```env
# AI Configuration
AI_TYPE=ollama
AI_ENABLED=true

# Ollama Settings
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=tinyllama
```

---

## Step 6: Test Ollama (Optional)

**Open new terminal and test:**

```bash
# Test Ollama is responding
curl http://localhost:11434/api/tags

# Should return JSON with available models:
# {"models":[{"name":"tinyllama:latest","modified_at":"..."}]}

# Test with a simple prompt
curl http://localhost:11434/api/generate -d '{
  "model": "tinyllama",
  "prompt": "What is a mutual fund?",
  "stream": false
}'
```

---

## Step 7: Start MFHelper Backend

**In a new terminal:**

```bash
cd backend

# Install dependencies (if needed)
pip install -r requirements.txt

# Start backend server
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

---

## Step 8: Open Frontend

**Open in browser:**
```
http://localhost:8000
```

🎉 **Done! Your AI is now live!**

---

## 📋 Checklist

- [ ] Ollama installed (`ollama --version` works)
- [ ] TinyLlama downloaded (`ollama pull tinyllama` completed)
- [ ] Ollama server running (`ollama serve` in terminal)
- [ ] `.env` configured with `AI_TYPE=ollama`
- [ ] Backend started (`python -m uvicorn...`)
- [ ] Frontend accessible (`http://localhost:8000`)

---

## 🧪 How to Test

### Test 1: Chat Test
```
Homepage → Ask "What is SIP?"
Expected: TinyLlama responds with explanation
```

### Test 2: Portfolio Query
```
Homepage → Ask "What are my cap ratios?"
Expected: Rule-based response (instant)
```

### Test 3: Direct API Test
```bash
curl -X POST http://localhost:8000/api/ai/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "What is mutual fund?"}'
```

---

## ⚠️ Troubleshooting

### "Ollama not found"
```bash
# Reinstall Ollama
winget install Ollama.Ollama

# Or download from https://ollama.ai/download
```

### "Connection refused" or "Ollama not available"
```bash
# Make sure Ollama server is running:
ollama serve

# Wait 2-3 seconds for it to start completely
```

### Slow responses
```bash
# Check system resources
# Need: 4GB+ free RAM
# TinyLlama: 1.1GB model

# If very slow, try stopping other apps
# Or use smaller Ollama model
```

### "Model not found"
```bash
# Re-download TinyLlama
ollama rm tinyllama
ollama pull tinyllama

# Verify it downloaded
ollama list  # Should show tinyllama
```

---

## 🔄 Terminal Setup

Recommended: 3 terminal windows running simultaneously

**Terminal 1 - Ollama Server:**
```bash
ollama serve
# Keep this running! 🟢
```

**Terminal 2 - MFHelper Backend:**
```bash
cd backend
python -m uvicorn app.main:app --reload
# Keep this running! 🟢
```

**Terminal 3 - Browser:**
```
Open: http://localhost:8000
```

---

## 💾 File Locations

- **Windows:** 
  - Ollama: `C:\Users\USERNAME\AppData\Local\Ollama`
  - Models: `C:\Users\USERNAME\.ollama\models`

- **macOS:**
  - Ollama: `/Applications/Ollama.app`
  - Models: `~/.ollama/models`

- **Linux:**
  - Ollama: `/usr/bin/ollama`
  - Models: `~/.ollama/models`

---

## 📊 Performance Expectations

| Query Type | Response Time | Model Used |
|------------|---------------|-----------|
| Cap ratios | ⚡ 10-50ms | Rule-based |
| Fund performance | ⚡ 50-100ms | Rule-based |
| "What is SIP?" | 1-2 seconds | TinyLlama |
| "Explain diversification" | 2-3 seconds | TinyLlama |

---

## 🎯 Next Steps

1. ✅ Install Ollama
2. ✅ Download TinyLlama
3. ✅ Start Ollama server
4. ✅ Configure `.env`
5. ✅ Start MFHelper backend
6. ✅ Open http://localhost:8000
7. 🚀 Start chatting with AI!

---

## ❓ Questions?

- **Ollama Not Starting:** Make sure you downloaded the right version for your OS
- **Download Stuck:** Check internet connection, try again
- **Memory Issues:** Close other apps, need 4GB+ free RAM
- **API Errors:** Make sure Ollama is running on port 11434

**Everything working?** You now have a FREE, LOCAL, PRIVATE AI assistant! 🦙🎉
