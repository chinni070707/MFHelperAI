# AI Integration - Implementation Guide

## 🤖 Overview

MFHelper now includes comprehensive AI/ML features powered by OpenAI GPT-4, providing users with intelligent portfolio analysis, natural language chat interface, and goal-based planning.

---

## 📋 Features Implemented

### **Phase 1: Portfolio Analysis & Chatbot** ✅

#### 1. **AI Portfolio Health Analyzer**
- **Health Score (0-100):** Comprehensive portfolio evaluation
- **Component Scores:** 
  - Diversification (25%)
  - Allocation (25%)
  - Performance (20%)
  - Risk (15%)
  - Cost (15%)
- **Smart Insights:** Actionable warnings and opportunities
- **AI Recommendations:** GPT-4 powered suggestions

#### 2. **Natural Language Chatbot**
- Context-aware conversation with portfolio data
- Answer questions about holdings, returns, funds
- Explain financial concepts
- Provide personalized advice

### **Phase 2: Goal-Based Planning** ✅

#### 3. **Goal Planner**
- Create financial goals (retirement, house, education, etc.)
- Calculate inflation-adjusted targets
- Determine required monthly SIP
- Generate allocation strategy based on risk
- Track progress with milestones
- AI-powered insights and recommendations

---

## 🚀 Quick Start

### 1. Install Dependencies

```bash
cd backend
pip install -r requirements-ai.txt
```

**Key packages:**
- `openai>=1.12.0` - OpenAI API
- `langchain>=0.1.0` - LLM orchestration
- `chromadb>=0.4.22` - Vector database
- `scikit-learn>=1.4.0` - ML models

### 2. Configure API Key

Add to `.env`:

```env
# AI Configuration
OPENAI_API_KEY=sk-your-api-key-here
AI_ENABLED=true

# Optional
OPENAI_MODEL=gpt-4-turbo-preview
OPENAI_EMBEDDING_MODEL=text-embedding-3-small
```

### 3. Test AI Endpoint

```bash
# Check AI status
curl http://localhost:8000/api/ai/status

# Response:
{
  "ai_available": true,
  "features": {
    "portfolio_analysis": true,
    "chatbot": true,
    "goal_planning": true,
    "recommendations": true
  }
}
```

---

## 📡 API Endpoints

### **Portfolio Analysis**

**GET** `/api/ai/portfolio/analyze`

Analyzes user's portfolio and returns comprehensive insights.

**Headers:**
```
Authorization: Bearer <access_token>
```

**Response:**
```json
{
  "health_score": 78.5,
  "health_grade": "B",
  "scores": {
    "diversification": 82.0,
    "allocation": 75.0,
    "performance": 85.0,
    "risk": 70.0,
    "cost": 75.0
  },
  "insights": [
    {
      "type": "success",
      "category": "diversification",
      "message": "✅ Good diversification across 12 funds"
    },
    {
      "type": "warning",
      "category": "allocation",
      "message": "⚠️ High equity exposure: 85% - Consider rebalancing"
    }
  ],
  "recommendations": [
    "Add debt funds to reduce portfolio volatility",
    "Consider international equity for geographic diversification"
  ],
  "analyzed_at": "2026-02-01T10:30:00",
  "holdings_count": 12,
  "total_value": 245000.0
}
```

---

### **AI Chatbot**

**POST** `/api/ai/chat`

Chat with AI about portfolio.

**Request:**
```json
{
  "message": "Which fund gave me the best returns?"
}
```

**Response:**
```json
{
  "response": "Your best performing fund is Axis Bluechip with 18.5% returns (₹12,340 profit). This fund has consistently outperformed its benchmark and has strong fundamentals.",
  "type": "success",
  "timestamp": "2026-02-01T10:35:00"
}
```

**Example Questions:**
- "Which fund gave me best returns?"
- "Should I invest more in debt funds?"
- "What is expense ratio?"
- "How is my large cap allocation?"
- "Explain diversification"

**DELETE** `/api/ai/chat/history`

Clear conversation history.

---

### **Goal Planning**

**POST** `/api/ai/goals/plan`

Create AI-powered goal-based investment plan.

**Request:**
```json
{
  "goal_name": "Dream House",
  "goal_type": "house",
  "target_amount": 5000000,
  "time_horizon": 5,
  "current_portfolio_value": 500000,
  "monthly_investment": 20000,
  "risk_tolerance": "moderate",
  "user_age": 35
}
```

**Response:**
```json
{
  "goal_name": "Dream House",
  "goal_type": "house",
  "target_amount": 5000000,
  "time_horizon_years": 5,
  "inflation_adjusted_amount": 6691132,
  "current_value": 500000,
  "monthly_investment": 20000,
  "required_monthly_sip": 68500,
  "projected_value": 2845000,
  "gap": 3846132,
  "gap_percentage": 57.5,
  "on_track": false,
  "allocation_strategy": {
    "equity": 60,
    "debt": 30,
    "gold": 10
  },
  "milestones": [
    {
      "percentage": 25,
      "target_value": 1672783,
      "target_date": "Mar 2027",
      "years_from_now": 1.3,
      "status": "pending"
    }
  ],
  "insights": [
    "You need to increase monthly investment by ₹48,500",
    "Current trajectory will only achieve 42.5% of target"
  ],
  "recommendations": [
    "Increase SIP to ₹68,500/month to stay on track",
    "Consider allocating bonuses/increments to close the gap",
    "Review and cut unnecessary expenses to free up ₹48,500/month"
  ],
  "created_at": "2026-02-01T10:40:00"
}
```

**Goal Types:**
- `retirement` - Retirement corpus
- `house` - House purchase
- `education` - Child's education
- `car` - Vehicle purchase
- `vacation` - Dream vacation
- `emergency_fund` - Emergency savings
- `wedding` - Wedding expenses
- `custom` - Custom goal

**Risk Tolerance:**
- `low` - 30% equity, 60% debt, 10% gold
- `moderate` - 60% equity, 30% debt, 10% gold
- `high` - 80% equity, 15% debt, 5% gold

---

## 🏗️ Architecture

### **Backend Services**

```
backend/app/
├── services/
│   ├── ai_service.py          # Core OpenAI integration
│   ├── portfolio_analyzer.py  # Health score calculation
│   ├── chatbot.py             # NL conversation handler
│   └── goal_planner.py        # Goal-based planning
├── routes/
│   └── ai.py                  # API endpoints
└── config_ai.py               # AI configuration
```

### **Flow Diagram**

```
User Request
    ↓
FastAPI Endpoint (/api/ai/*)
    ↓
Service Layer (analyzer/chatbot/planner)
    ↓
OpenAI API (GPT-4)
    ↓
Response Processing
    ↓
Return to User
```

---

## 💰 Cost Estimation

### **OpenAI Pricing (GPT-4 Turbo)**

| Feature | Tokens | Cost/Request | Requests/Day | Daily Cost |
|---------|--------|--------------|--------------|------------|
| Portfolio Analysis | ~1500 | $0.03 | 100 | $3.00 |
| Chatbot (avg) | ~800 | $0.016 | 200 | $3.20 |
| Goal Planning | ~1200 | $0.024 | 50 | $1.20 |
| **Total** | | | **350** | **$7.40/day** |

**Monthly Cost:** ~$220 for 350 requests/day  
**Cost per User:** ~$0.022/request

### **Optimization Strategies:**

1. **Caching:** Cache similar analyses (reduce 40% costs)
2. **Rate Limiting:** 50 requests/hour/user
3. **Batch Processing:** Group similar requests
4. **Fallback to Rules:** Use rule-based for simple queries
5. **Cost Alerts:** Track daily spending

---

## 🎨 Frontend Integration

### **1. Add AI Features to Dashboard**

```javascript
// Analyze Portfolio
async function analyzePortfolio() {
    const response = await fetch('/api/ai/portfolio/analyze', {
        headers: {
            'Authorization': `Bearer ${token}`
        }
    });
    const analysis = await response.json();
    
    // Display health score
    document.getElementById('healthScore').textContent = analysis.health_score;
    document.getElementById('healthGrade').textContent = analysis.health_grade;
    
    // Show insights
    analysis.insights.forEach(insight => {
        displayInsight(insight);
    });
}

// Chat with AI
async function chatWithAI(message) {
    const response = await fetch('/api/ai/chat', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({ message })
    });
    const chat = await response.json();
    displayChatMessage(chat.response);
}

// Create Goal Plan
async function createGoal(goalData) {
    const response = await fetch('/api/ai/goals/plan', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify(goalData)
    });
    const plan = await response.json();
    displayGoalPlan(plan);
}
```

### **2. UI Components**

**Health Score Card:**
```html
<div class="health-score-card">
    <div class="score-circle">
        <span class="score">78.5</span>
        <span class="grade">B</span>
    </div>
    <div class="score-breakdown">
        <div class="score-item">
            <span>Diversification</span>
            <span>82/100</span>
        </div>
        <!-- More scores -->
    </div>
</div>
```

**Chat Interface:**
```html
<div class="ai-chat">
    <div class="chat-messages">
        <!-- Messages here -->
    </div>
    <input type="text" placeholder="Ask about your portfolio..." />
    <button onclick="sendMessage()">Send</button>
</div>
```

**Goal Planning Wizard:**
```html
<div class="goal-wizard">
    <h3>Create Financial Goal</h3>
    <input name="goal_name" placeholder="e.g., Dream House" />
    <input name="target_amount" type="number" placeholder="Target Amount" />
    <input name="time_horizon" type="number" placeholder="Years" />
    <select name="risk_tolerance">
        <option value="low">Low Risk</option>
        <option value="moderate">Moderate Risk</option>
        <option value="high">High Risk</option>
    </select>
    <button onclick="createGoal()">Create Plan</button>
</div>
```

---

## 🧪 Testing

### **1. Unit Tests**

```python
# tests/test_ai_services.py
import pytest
from app.services.portfolio_analyzer import portfolio_analyzer

@pytest.mark.asyncio
async def test_portfolio_analysis():
    portfolio_data = {
        "holdings": [
            {
                "fund_name": "Test Fund",
                "amc": "Test AMC",
                "category": "Equity",
                "current_value": 10000,
                "invested_value": 9000,
                "returns": 1000
            }
        ]
    }
    
    analysis = await portfolio_analyzer.analyze_portfolio(portfolio_data)
    
    assert "health_score" in analysis
    assert analysis["health_score"] >= 0
    assert analysis["health_score"] <= 100
```

### **2. Integration Tests**

```python
def test_ai_portfolio_analyze_endpoint(client, auth_headers):
    response = client.get("/api/ai/portfolio/analyze", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert "health_score" in data
    assert "insights" in data
```

### **3. Manual Testing**

```bash
# Test with curl
curl -X GET http://localhost:8000/api/ai/portfolio/analyze \
  -H "Authorization: Bearer your-token-here"

curl -X POST http://localhost:8000/api/ai/chat \
  -H "Authorization: Bearer your-token-here" \
  -H "Content-Type: application/json" \
  -d '{"message": "What is my portfolio value?"}'
```

---

## 🔒 Security & Best Practices

1. **API Key Security:**
   - Store in environment variables
   - Never commit to git
   - Rotate keys monthly

2. **Rate Limiting:**
   - 50 requests/hour per user
   - Implement exponential backoff
   - Track usage per user

3. **Cost Control:**
   - Set daily spending limits ($50/day default)
   - Alert when approaching limit
   - Fallback to rule-based system

4. **Data Privacy:**
   - Don't send PII to OpenAI
   - Anonymize portfolio data
   - Log only metadata

5. **Error Handling:**
   - Graceful degradation
   - Clear error messages
   - Fallback responses

---

## 📊 Monitoring & Analytics

### **Track Metrics:**

```python
# Log AI usage
logger.info(f"AI Analysis - User: {user_id}, Cost: ${cost:.4f}, Tokens: {tokens}")

# Metrics to track:
- AI requests per user
- Average response time
- Daily/monthly costs
- Error rates
- Feature usage (analysis vs chat vs goals)
- User satisfaction (implicit: repeat usage)
```

### **Cost Dashboard:**

Create admin endpoint to track:
- Total AI spend today/month
- Cost per feature
- Most active users
- Token usage trends

---

## 🚀 Deployment

### **1. Environment Variables**

```env
# Production .env
OPENAI_API_KEY=sk-prod-key-here
AI_ENABLED=true
OPENAI_MODEL=gpt-4-turbo-preview
AI_RATE_LIMIT_PER_USER=50
DAILY_COST_LIMIT=50.0
CACHE_AI_RESPONSES=true
```

### **2. Docker Configuration**

```dockerfile
# Add to Dockerfile
RUN pip install -r requirements-ai.txt

ENV OPENAI_API_KEY=${OPENAI_API_KEY}
ENV AI_ENABLED=true
```

### **3. Health Checks**

```python
# Add to health check
@router.get("/health/ai")
async def ai_health():
    from app.services.ai_service import ai_service
    return {
        "status": "healthy" if ai_service.is_available() else "degraded",
        "features_available": ai_service.is_available()
    }
```

---

## 📈 Future Enhancements

### **Phase 3: Advanced Features**

1. **Fund Recommendations:**
   - ML model to suggest funds
   - Based on risk profile, goals, current portfolio
   - Compare with similar portfolios

2. **Predictive Alerts:**
   - Detect fund manager changes
   - Market volatility warnings
   - Tax loss harvesting opportunities

3. **Market Sentiment:**
   - Analyze news for user's funds
   - Social media sentiment tracking
   - Peer comparison insights

4. **Voice Assistant:**
   - "Alexa, what's my portfolio value?"
   - Voice-based portfolio queries
   - Natural voice responses

---

## 🐛 Troubleshooting

### **AI Not Available**

```python
# Check status
GET /api/ai/status

# If false, check:
1. OPENAI_API_KEY set in .env
2. pip install -r requirements-ai.txt
3. Logs: tail -f logs/mfhelper_*.log
```

### **High Costs**

```python
# Reduce costs:
1. Enable caching: CACHE_AI_RESPONSES=true
2. Lower rate limit: AI_RATE_LIMIT_PER_USER=20
3. Use cheaper model: OPENAI_MODEL=gpt-3.5-turbo
4. Implement fallback to rules
```

### **Slow Responses**

```python
# Optimize:
1. Reduce MAX_TOKENS (default 2000 → 1000)
2. Cache similar queries
3. Use async properly
4. Consider local embeddings
```

---

## ✅ Summary

**Implemented:**
- ✅ Portfolio Health Analyzer with AI recommendations
- ✅ Natural Language Chatbot with context
- ✅ Goal-Based Planning with calculations
- ✅ Comprehensive API endpoints
- ✅ Error handling and fallbacks

**Ready for:**
- Frontend integration
- Production deployment
- User testing
- Feature expansion

**Cost:** ~$220/month for 350 requests/day

**Next Steps:**
1. Add frontend UI components
2. Test with real users
3. Monitor costs and usage
4. Iterate based on feedback

🎉 **AI features are production-ready!**
