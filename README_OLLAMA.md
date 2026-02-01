# 🦙 MFHelper with Local AI (Ollama + TinyLlama)

## Overview

MFHelper now features a **hybrid AI approach** combining:
- ✅ **Rule-Based System** - Ultra-fast portfolio analysis (instant ⚡)
- ✅ **TinyLlama AI** - Local, free LLM for general questions (1-2 sec)
- ✅ **Zero Cost** - No ChatGPT, no API fees
- ✅ **Complete Privacy** - All processing local, no cloud
- ✅ **Optional OpenAI** - Add GPT-4 later if needed

---

## 🚀 Quick Start (5 Minutes)

### 1. Install Ollama
```bash
# Windows
winget install Ollama.Ollama

# macOS
brew install ollama

# Linux
curl https://ollama.ai/install.sh | sh
```

### 2. Download TinyLlama
```bash
ollama pull tinyllama
# Takes 3-10 minutes (1.1GB download)
```

### 3. Start Ollama Server
```bash
# Keep this running in a terminal
ollama serve
```

### 4. Configure MFHelper
```bash
cd backend

# Copy example env
cp .env.example .env

# Update .env:
# AI_TYPE=ollama
# OLLAMA_MODEL=tinyllama
```

### 5. Start Backend
```bash
python -m uvicorn app.main:app --reload
```

### 6. Open Frontend
```
http://localhost:8000
```

**Done!** 🎉

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────┐
│         MFHelper Frontend               │
│  (Chat Interface - http://localhost)    │
└──────────────────┬──────────────────────┘
                   │
                   ↓
┌─────────────────────────────────────────┐
│      MFHelper Backend API                │
│  (FastAPI - http://localhost:8000)      │
└──────────────────┬──────────────────────┘
                   │
        ┌──────────┴──────────┐
        ↓                     ↓
   ┌─────────────┐       ┌─────────────┐
   │ Rule-Based  │       │  Hybrid AI  │
   │   System    │       │   Router    │
   │             │       │             │
   │ Portfolio   │       │ • Detects   │
   │ Analysis    │       │   query     │
   │ (INSTANT ⚡)│       │ • Routes to │
   │             │       │   engine    │
   │ • Cap ratio │       │ • Falls back│
   │ • Perf rank │       │             │
   │ • Rebalance │       └──────┬──────┘
   │ • Diversity │              │
   └─────────────┘         ┌────┴────┐
                           ↓         ↓
                   ┌────────────┐  ┌────────────┐
                   │  TinyLlama │  │  Fallback  │
                   │  (Ollama)  │  │  Responses │
                   │            │  │            │
                   │ • General  │  │ • Pre-made │
                   │   questions│  │   MF facts │
                   │ • Chat     │  │            │
                   │ • 1-2 sec  │  │ INSTANT ⚡ │
                   └────────────┘  └────────────┘
```

---

## 💡 How Queries Are Handled

### Example 1: Portfolio Analysis (Rule-Based)
```
User: "What are my large/mid/small cap ratios?"
         ↓
Hybrid Router detects "cap ratio" keyword
         ↓
Route to Rule-Based System
         ↓
INSTANT ⚡ Response:
"Large Cap: 60% (₹2,40,000)
 Mid Cap: 25% (₹1,00,000)
 Small Cap: 15% (₹60,000)"
```

### Example 2: General Question (TinyLlama)
```
User: "What is SIP?"
         ↓
Hybrid Router doesn't detect portfolio query
         ↓
Route to TinyLlama AI (via Ollama)
         ↓
1-2 seconds
         ↓
Response from TinyLlama:
"SIP (Systematic Investment Plan) is investing
a fixed amount regularly. Great for rupee 
cost averaging and long-term wealth!"
```

### Example 3: Fallback
```
User: "Random question"
         ↓
Not portfolio query
         ↓
Ollama unavailable? 
         ↓
Use pre-made fallback
         ↓
INSTANT ⚡ Response:
"I can help with mutual funds! Ask about
SIP, diversification, or upload your portfolio."
```

---

## 📊 Query Classification

### Rule-Based Queries (Portfolio Analysis) ⚡
Instantly returned using data + rules:
- "What are my cap ratios?"
- "Which funds are underperforming?"
- "Should I rebalance?"
- "How diversified is my portfolio?"
- "What's my expense ratio?"
- "Which categories are in my portfolio?"

### AI Queries (TinyLlama) 🤖
Handled by local LLM (1-2 sec):
- "What is SIP?"
- "Difference between index and active funds?"
- "Should I invest in small caps?"
- "Explain diversification"
- "What is expense ratio?"
- "How to choose funds?"

---

## ⚙️ Configuration

### `.env` Setup

```env
# Use Ollama (Local AI - Recommended)
AI_TYPE=ollama
AI_ENABLED=true
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=tinyllama

# Optional: Use OpenAI (Paid) instead
# AI_TYPE=openai
# OPENAI_API_KEY=sk-...
```

### Model Options

| Model | Size | Speed | Quality | Cost |
|-------|------|-------|---------|------|
| **tinyllama** | 1.1GB | ⚡⚡⚡ | Good | FREE |
| phi3:mini | 2.7GB | ⚡⚡ | Better | FREE |
| mistral | 4GB | ⚡ | Excellent | FREE |
| llama2:7b | 3.8GB | ⚡ | Very Good | FREE |

To upgrade:
```bash
ollama pull phi3:mini
# Update .env: OLLAMA_MODEL=phi3:mini
```

---

## 🔧 Troubleshooting

### Ollama Connection Error
```bash
# Make sure Ollama is running
ollama serve

# Check connectivity
curl http://localhost:11434/api/tags

# Should return model list
```

### TinyLlama Download Failed
```bash
# Retry download
ollama pull tinyllama --verbose

# Or use smaller model
ollama pull tinyllama
```

### Slow Responses
```bash
# Check system resources (need 4GB+ free RAM)
# Check CPU usage
# Consider smaller model (TinyLlama is already small)
```

### "Model not found" Error
```bash
# List available models
ollama list

# Re-download if missing
ollama pull tinyllama
```

---

## 📈 Performance

| Operation | Speed | Engine |
|-----------|-------|--------|
| Cap ratios | ⚡ 10ms | Rule-based |
| Fund ranking | ⚡ 50ms | Rule-based |
| Rebalance check | ⚡ 100ms | Rule-based |
| Chat response | 1-2 sec | TinyLlama |
| Setup (one-time) | 10 min | Download |

---

## 💾 Storage Requirements

- **Ollama Binary:** 150-200MB
- **TinyLlama Model:** 1.1GB
- **MFHelper App:** 200MB
- **Total:** ~1.5GB

### RAM Requirements
- **Minimum:** 4GB free RAM
- **Recommended:** 8GB free RAM
- **Ideal:** 16GB+ total RAM

---

## 🎯 Files Modified/Created

```
backend/
├── app/
│   ├── services/
│   │   ├── hybrid_ai_service.py      ✨ NEW: Hybrid router
│   │   ├── ai_service.py             ✏️ UPDATED: Ollama support
│   │   ├── portfolio_analyzer.py     ✓ Rule-based portfolio analysis
│   │   ├── chatbot.py                ✓ Chat interface
│   │   └── goal_planner.py           ✓ Goal planning
│   ├── config_ai.py                  ✏️ UPDATED: Ollama config
│   └── main.py                       ✓ Already integrated
├── requirements.txt                  ✏️ UPDATED: Added requests
├── .env.example                      ✏️ UPDATED: Ollama config
├── setup_ollama.py                   ✨ NEW: Auto setup script
└── [other files unchanged]

docs/
├── OLLAMA_SETUP.md                   ✨ NEW: Detailed setup
├── OLLAMA_QUICKSTART.md              ✨ NEW: Quick reference
├── OLLAMA_MANUAL_SETUP.md            ✨ NEW: Step-by-step guide
└── [other docs unchanged]
```

---

## 🚀 Deployment Options

### Option 1: Local Development
```bash
# All-in-one on your machine
ollama serve          # Terminal 1
python -m uvicorn... # Terminal 2
# Open http://localhost:8000
```

### Option 2: Production (Same Machine)
```bash
# Ollama as service
# Backend as service (systemd/Docker)
# Frontend on CDN
# Database on cloud

# Still using local TinyLlama for AI
```

### Option 3: Add OpenAI Later
```env
# Switch to cloud AI when scaling
AI_TYPE=openai
OPENAI_API_KEY=sk-...
```

---

## 🎓 Learning Resources

- **Ollama:** https://ollama.ai
- **TinyLlama:** https://github.com/jzhang38/TinyLlama
- **Models Library:** https://ollama.ai/library
- **Discord Community:** https://discord.gg/ollama

---

## ✅ Verification Checklist

- [ ] Ollama installed (`ollama --version`)
- [ ] TinyLlama downloaded (`ollama list` shows tinyllama)
- [ ] Ollama server running (`ollama serve` in terminal)
- [ ] .env configured with `AI_TYPE=ollama`
- [ ] Backend starts successfully
- [ ] Frontend accessible (`http://localhost:8000`)
- [ ] AI chat responds (try "What is SIP?")
- [ ] Portfolio queries work (try "What are my cap ratios?")

---

## 🎉 You're All Set!

Your MFHelper now has:
- ✅ **FREE Local AI** - TinyLlama (no costs!)
- ✅ **Ultra-Fast Portfolio Analysis** - Rule-based (instant!)
- ✅ **Complete Privacy** - All processing local
- ✅ **Zero Dependencies** - No external APIs needed
- ✅ **Easy to Upgrade** - Can switch to OpenAI anytime

**Start analyzing mutual funds with AI!** 🚀

---

## 📞 Support

- Check: `OLLAMA_MANUAL_SETUP.md` for detailed steps
- Check: `OLLAMA_QUICKSTART.md` for quick reference
- Review: `docs/OLLAMA_SETUP.md` for advanced config
- Run: `python setup_ollama.py` for auto setup

Happy analyzing! 📊🤖
