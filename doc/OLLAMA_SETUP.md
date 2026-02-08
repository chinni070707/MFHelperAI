# 🦙 Ollama + TinyLlama Setup Guide

## Quick Setup (5 minutes)

### **Step 1: Download & Install Ollama**

#### Windows:
```bash
# Option A: Download from website
# Visit: https://ollama.ai/download

# Option B: Use Winget
winget install Ollama.Ollama
```

#### macOS:
```bash
# Download from https://ollama.ai/download
# Or use brew
brew install ollama
```

#### Linux:
```bash
curl https://ollama.ai/install.sh | sh
```

---

### **Step 2: Download TinyLlama Model**

```bash
# Open terminal/command prompt
ollama pull tinyllama

# This downloads 1.1GB model (takes 2-5 minutes depending on internet)
```

---

### **Step 3: Start Ollama Server**

```bash
# Run in terminal
ollama serve

# You'll see:
# Listening on [::]:11434
```

**Keep this terminal running!** Ollama will now be available at `http://localhost:11434`

---

### **Step 4: Test Ollama**

In a new terminal:

```bash
# Test if Ollama is working
curl http://localhost:11434/api/tags

# Or test with a simple prompt
curl http://localhost:11434/api/generate -d '{
  "model": "tinyllama",
  "prompt": "What is mutual fund?"
}'
```

---

## Integration with MFHelper

### **What Happens:**

1. **Rule-Based Queries** (Fast ⚡):
   - "What are my cap ratios?" → Rule-based (instant)
   - "Which funds underperform?" → Rule-based (instant)
   - "Should I rebalance?" → Rule-based (instant)

2. **AI Chat Queries** (TinyLlama):
   - "What is SIP?" → TinyLlama (1-2 seconds)
   - "Difference between index and active?" → TinyLlama (1-2 seconds)
   - "Should I invest in index funds?" → TinyLlama (1-2 seconds)

3. **Fallback**:
   - If Ollama unavailable → Rule-based response
   - If query too complex → Rule-based + suggestion

---

## Configuration

### `.env` for Local AI:

```env
# AI Configuration
AI_ENABLED=true
AI_TYPE=ollama  # Use 'ollama' instead of 'openai'

# Ollama Configuration
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=tinyllama

# Alternative: Use larger model if you want
# OLLAMA_MODEL=mistral (4GB, higher quality)
# OLLAMA_MODEL=llama2:7b (3.8GB, more capable)
```

---

## Models Available

| Model | Size | Speed | Quality | Best For |
|-------|------|-------|---------|----------|
| **tinyllama** | 1.1GB | ⚡⚡⚡ | Good | General Q&A |
| **phi3:mini** | 2.7GB | ⚡⚡ | Better | Portfolio chat |
| **mistral** | 4GB | ⚡ | Excellent | Complex queries |
| **llama2:7b** | 3.8GB | ⚡ | Very Good | Best balanced |

### To Switch Models:

```bash
# Download another model
ollama pull phi3:mini

# Update .env
OLLAMA_MODEL=phi3:mini

# Restart backend
```

---

## Performance Tips

### 1. **Reduce Response Time**
```bash
# Lower max_tokens in prompts
# Default: 500 tokens
# For TinyLlama: 200 tokens (faster)
```

### 2. **Cache Responses**
```python
# Same question asked twice?
# Cache stores response for 1 hour
# Saves 1-2 seconds on second ask
```

### 3. **Use GPU Acceleration** (Optional)
```bash
# If you have NVIDIA GPU
ollama pull tinyllama

# Ollama automatically uses GPU if available
# 3x faster responses!
```

---

## Troubleshooting

### **Ollama won't start**
```bash
# Check if port 11434 is free
netstat -ano | findstr :11434

# If in use, kill the process or use different port
# Or restart computer
```

### **Model download fails**
```bash
# Check internet connection
# Retry with:
ollama pull tinyllama --verbose

# Or try smaller model first:
ollama pull tinyllama  # 1.1GB
```

### **Slow responses**
```bash
# Check if:
1. ollama serve is running
2. Model is fully downloaded (ollama show tinyllama)
3. System has 4GB+ free RAM
4. CPU not maxed out (top or Task Manager)
```

### **Out of memory**
```bash
# Use smaller model:
ollama pull tinyllama  # Instead of larger models

# Or check system RAM:
# Minimum: 4GB
# Recommended: 8GB
# Ideal: 16GB
```

---

## Switching Back to OpenAI (If Needed)

```env
# In .env
AI_TYPE=openai
OPENAI_API_KEY=sk-your-key-here
```

---

## Cost Comparison

| Approach | Monthly Cost | Setup Time | Quality |
|----------|--------------|------------|---------|
| **Local TinyLlama** | $0 | 5 min | Good ⭐⭐⭐ |
| **Local Phi3 Mini** | $0 | 5 min | Better ⭐⭐⭐⭐ |
| **OpenAI GPT-4** | $220+ | 2 min | Best ⭐⭐⭐⭐⭐ |

**Recommendation:** Start with TinyLlama, upgrade to Phi3 if needed, add OpenAI later for premium features.

---

## Next Steps

1. ✅ Install Ollama
2. ✅ Download TinyLlama
3. ✅ Start Ollama server
4. ✅ Test with curl
5. → Backend will auto-detect and use it!

That's it! MFHelper will now use local TinyLlama instead of OpenAI. 🚀

---

## Resources

- Ollama: https://ollama.ai
- TinyLlama: https://github.com/jzhang38/TinyLlama
- Models: https://ollama.ai/library
- Discord: https://discord.gg/ollama
