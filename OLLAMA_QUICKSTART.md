# 🦙 Quick Start - Ollama Setup for MFHelper

## ⚡ TL;DR (3 Steps)

### Step 1: Install Ollama
**Windows:**
```bash
winget install Ollama.Ollama
```
Or download from: https://ollama.ai/download

**macOS:**
```bash
brew install ollama
```

**Linux:**
```bash
curl https://ollama.ai/install.sh | sh
```

### Step 2: Download TinyLlama Model
```bash
ollama pull tinyllama
# Takes 3-10 minutes (downloads 1.1GB)
```

### Step 3: Run Setup Script
```bash
cd backend
python setup_ollama.py
```

**That's it!** 🎉

---

## 🔄 How It Works

### Before Running

**Terminal 1 - Keep Ollama Running:**
```bash
ollama serve
```
Keep this running! You'll see:
```
Listening on [::]:11434
```

### Then Start MFHelper

**Terminal 2 - Run Backend:**
```bash
cd backend
python -m uvicorn app.main:app --reload
```

**Terminal 3 - Open Frontend:**
```
Open: http://localhost:8000
```

---

## 📊 What You Get

### ⚡ Ultra-Fast Portfolio Analysis (Rule-Based)
**Query:** "What are my large/mid/small cap ratios?"
```
Response: Instant ⚡
Large Cap: 60% (₹2,40,000)
Mid Cap: 25% (₹1,00,000)
Small Cap: 15% (₹60,000)
```

### 🤖 Smart Chat (TinyLlama AI)
**Query:** "What is SIP?"
```
Response: 1-2 seconds
TinyLlama: "SIP (Systematic Investment Plan) is investing 
a fixed amount regularly. Great for rupee cost averaging!"
```

### 🎯 Smart Routing
```
Your Query
    ↓
Is it portfolio analysis? → Rule-Based (instant ⚡)
    ↓
General MF question? → TinyLlama (1-2 sec)
    ↓
No AI needed? → Fallback response (instant ⚡)
```

---

## 🔧 Troubleshooting

### Ollama won't install
```bash
# Manual download
https://ollama.ai/download

# Then verify
ollama --version
```

### TinyLlama download fails
```bash
# Check internet, then retry
ollama pull tinyllama --verbose

# Or try smaller model first
ollama pull tinyllama  # 1.1GB
```

### Slow responses
```bash
# Check if Ollama is running
ps aux | grep ollama

# If not running:
ollama serve

# Check RAM usage (need 4GB+ free)
```

### "Ollama not available" error
```bash
# Make sure Ollama is running:
ollama serve

# Wait 2-3 seconds for it to start
# Then try again
```

### Out of memory
```bash
# Your system needs 4GB+ free RAM
# Close other apps and retry

# Or use even smaller model:
ollama pull tinyllama  # 1.1GB (already small!)
```

---

## 📈 Performance

| Operation | Time | Cost |
|-----------|------|------|
| Cap Ratio Analysis | ⚡ 10ms | FREE |
| Fund Performance | ⚡ 50ms | FREE |
| Rebalancing Check | ⚡ 100ms | FREE |
| General Chat | 1-2 sec | FREE |
| Setup (one-time) | 10 min | FREE |

---

## 💾 Storage

- **Ollama:** 150-200MB
- **TinyLlama Model:** 1.1GB
- **Total:** ~1.3GB
- **RAM needed:** 4GB+ (ideal 8GB+)

---

## 🚀 Optional: Upgrade Later

Start with TinyLlama, upgrade anytime:

```bash
# Try Phi-3 Mini (better quality, 2.7GB)
ollama pull phi3:mini
```

Update `.env`:
```env
OLLAMA_MODEL=phi3:mini
```

Restart backend - that's it!

---

## ✅ Verify Setup

Test locally:
```bash
# In terminal, test Ollama directly
curl http://localhost:11434/api/tags

# Should return:
# {"models": [{"name": "tinyllama:latest", ...}]}

# Test with a prompt
curl http://localhost:11434/api/generate -d '{
  "model": "tinyllama",
  "prompt": "What is mutual fund?"
}'
```

---

## 📚 Resources

- **Ollama:** https://ollama.ai
- **TinyLlama:** https://github.com/jzhang38/TinyLlama
- **Models:** https://ollama.ai/library
- **Discord:** https://discord.gg/ollama

---

## 🎯 Next Steps

1. ✅ Run setup script: `python setup_ollama.py`
2. ✅ Start Ollama: `ollama serve`
3. ✅ Start MFHelper: `python -m uvicorn app.main:app`
4. ✅ Open http://localhost:8000
5. ✅ Chat with AI! 🚀

**Your AI is now FREE, LOCAL, and PRIVATE!** 🦙
