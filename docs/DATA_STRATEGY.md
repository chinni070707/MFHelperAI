# 📊 Mutual Fund Data Strategy - Portfolio Overlap Analysis

## Problem Statement

To calculate portfolio overlap, we need:
1. **Top holdings** of each fund (stock-level data)
2. **Sector allocation** of each fund
3. **Updated monthly** (as per SEBI regulations)

---

## 🏆 Best Data Sources (India)

### 1. **AMFI (Association of Mutual Funds in India)** ⭐ RECOMMENDED
- **URL**: https://www.amfiindia.com/
- **Data**: Monthly portfolio disclosures
- **Format**: Excel files
- **Update**: Every month (within 10 days of month-end)
- **Cost**: FREE
- **Coverage**: All SEBI-registered funds

**What They Publish:**
- Top 10 holdings
- Sector allocation
- Asset allocation
- Fund manager details

### 2. **MFApi.in** ⭐ BEST FOR DEVELOPERS
- **URL**: https://mfapi.in/
- **Type**: REST API
- **Cost**: FREE
- **Data**: NAV, scheme details, returns
- **Rate Limit**: Generous
- **Update**: Daily

**Sample Endpoints:**
```
GET https://api.mfapi.in/mf
GET https://api.mfapi.in/mf/{scheme_code}
GET https://api.mfapi.in/mf/search?q=axis
```

**Limitation**: Doesn't have portfolio holdings (only NAV/returns)

### 3. **Value Research API** 💰
- **Type**: Commercial API
- **Cost**: Paid subscription
- **Data**: Holdings, ratings, analytics
- **Best For**: Production apps with budget

### 4. **Morningstar India** 💰
- Similar to Value Research
- Premium data

### 5. **Fund House Websites (Web Scraping)**
- Each fund publishes monthly factsheets
- **Pros**: Official, accurate
- **Cons**: Different formats, scraping needed

---

## 💡 Recommended Approach for MFHelper

### Phase 1: Manual Dataset (MVP) ✅ START HERE

**What to do:**
1. Download monthly portfolio files from AMFI
2. Create a JSON database
3. Ship with the app
4. Update monthly (manual for now)

**Implementation:**

```json
// data/fund_holdings.json
{
  "funds": {
    "parag-parikh-flexi-cap": {
      "fund_name": "Parag Parikh Flexi Cap Fund",
      "isin": "INF769K01FH4",
      "updated": "2026-01-31",
      "holdings": [
        {"stock": "HDFC Bank", "allocation": 8.5, "sector": "Banking"},
        {"stock": "Reliance Industries", "allocation": 7.2, "sector": "Oil & Gas"},
        {"stock": "Infosys", "allocation": 5.8, "sector": "IT"},
        ...
      ],
      "sector_allocation": {
        "Banking": 28,
        "IT": 18,
        "Oil & Gas": 12,
        ...
      }
    }
  }
}
```

**Pros:**
- ✅ Fast (no API calls)
- ✅ No rate limits
- ✅ Works offline
- ✅ Free

**Cons:**
- ❌ Manual updates needed
- ❌ File size grows

**File Size Estimate:**
- 1000 funds × 50 holdings = ~2-3 MB JSON (acceptable!)

---

### Phase 2: Hybrid (API + Cache) 🚀 PRODUCTION

**What to do:**
1. Use MFApi for NAV/returns
2. Build backend service to scrape/collect holdings monthly
3. Cache in database
4. Expose via your API

**Architecture:**

```
┌─────────────────┐
│  Frontend       │
│  (Dashboard)    │
└────────┬────────┘
         │
         ↓
┌─────────────────┐      ┌──────────────┐
│  Your Backend   │──────│  PostgreSQL  │
│  FastAPI        │      │  (Holdings)  │
└────────┬────────┘      └──────────────┘
         │
    ┌────┴────┐
    ↓         ↓
┌────────┐ ┌────────┐
│ MFApi  │ │ AMFI   │
│ (NAV)  │ │(Hold.) │
└────────┘ └────────┘
```

---

### Phase 3: Real-time API (Advanced) 💎

Partner with data providers or build comprehensive scraper.

---

## 🛠️ Implementation Plan

### Step 1: Create Data Downloader Script

```python
# scripts/download_fund_data.py
import requests
import json
from bs4 import BeautifulSoup
import pandas as pd

def download_amfi_data():
    """Download latest portfolio data from AMFI"""
    url = "https://www.amfiindia.com/research-information/other-data/monthly-portfolio-holdings"
    # Parse and extract data
    pass

def create_fund_database():
    """Create JSON database from downloaded files"""
    funds_data = {}
    
    # Top 50 most popular funds (start small)
    popular_funds = [
        "Parag Parikh Flexi Cap",
        "HDFC Flexi Cap",
        "Axis Bluechip",
        "SBI Bluechip",
        "Mirae Asset Large Cap",
        # ... add 45 more
    ]
    
    for fund in popular_funds:
        holdings = extract_holdings(fund)  # Your extraction logic
        funds_data[fund] = holdings
    
    # Save to JSON
    with open('data/fund_holdings.json', 'w') as f:
        json.dump(funds_data, f, indent=2)

if __name__ == "__main__":
    download_amfi_data()
    create_fund_database()
```

---

### Step 2: Create Holdings API Endpoint

```python
# backend/app/routes/holdings.py
from fastapi import APIRouter, HTTPException
import json
import os

router = APIRouter(prefix="/api/holdings", tags=["Holdings"])

# Load holdings data on startup
HOLDINGS_FILE = "data/fund_holdings.json"
holdings_cache = {}

@router.on_event("startup")
async def load_holdings():
    global holdings_cache
    if os.path.exists(HOLDINGS_FILE):
        with open(HOLDINGS_FILE, 'r') as f:
            holdings_cache = json.load(f)

@router.get("/fund/{fund_name}")
async def get_fund_holdings(fund_name: str):
    """Get holdings for a specific fund"""
    fund_key = fund_name.lower().replace(" ", "-")
    
    if fund_key not in holdings_cache.get("funds", {}):
        raise HTTPException(status_code=404, detail="Fund not found")
    
    return holdings_cache["funds"][fund_key]

@router.post("/overlap")
async def calculate_overlap(fund_names: list[str]):
    """Calculate overlap between multiple funds"""
    funds_data = []
    
    for fund_name in fund_names:
        fund_key = fund_name.lower().replace(" ", "-")
        if fund_key in holdings_cache.get("funds", {}):
            funds_data.append(holdings_cache["funds"][fund_key])
    
    # Calculate overlap
    overlap = calculate_portfolio_overlap(funds_data)
    return overlap

def calculate_portfolio_overlap(funds_data):
    """Calculate stock and sector overlap"""
    all_stocks = {}
    
    for fund in funds_data:
        for holding in fund["holdings"]:
            stock = holding["stock"]
            if stock not in all_stocks:
                all_stocks[stock] = []
            all_stocks[stock].append({
                "fund": fund["fund_name"],
                "allocation": holding["allocation"]
            })
    
    # Find overlapping stocks
    overlapping_stocks = {
        stock: funds 
        for stock, funds in all_stocks.items() 
        if len(funds) > 1
    }
    
    return {
        "overlapping_stocks": overlapping_stocks,
        "overlap_percentage": len(overlapping_stocks) / len(all_stocks) * 100 if all_stocks else 0
    }
```

---

### Step 3: Frontend Integration

```javascript
// frontend/js/overlap.js
async function analyzeOverlap(fundNames) {
    const loadingId = loading.show('Analyzing portfolio overlap...');
    
    try {
        const response = await fetch('/api/holdings/overlap', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(fundNames)
        });
        
        if (!response.ok) throw new Error('Failed to analyze overlap');
        
        const data = await response.json();
        
        loading.hide(loadingId);
        displayOverlapResults(data);
        
    } catch (error) {
        loading.hide(loadingId);
        errorHandler.handleAPIError(error);
    }
}

function displayOverlapResults(data) {
    // Show overlap visualization
    const overlappingStocks = data.overlapping_stocks;
    
    let html = '<h2>Portfolio Overlap Analysis</h2>';
    html += `<p>Overlap: ${data.overlap_percentage.toFixed(1)}%</p>`;
    
    html += '<h3>Common Holdings:</h3><ul>';
    for (const [stock, funds] of Object.entries(overlappingStocks)) {
        html += `<li><strong>${stock}</strong>: `;
        html += funds.map(f => `${f.fund} (${f.allocation}%)`).join(', ');
        html += '</li>';
    }
    html += '</ul>';
    
    document.getElementById('overlap-results').innerHTML = html;
}
```

---

## 📅 Data Update Strategy

### Option 1: Manual Monthly Updates
```bash
# Run every month
python scripts/download_fund_data.py
git add data/fund_holdings.json
git commit -m "Update fund holdings for Jan 2026"
git push
# Redeploy app
```

### Option 2: Automated (GitHub Actions)
```yaml
# .github/workflows/update-data.yml
name: Update Fund Holdings
on:
  schedule:
    - cron: '0 0 5 * *'  # 5th of every month
jobs:
  update:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Download latest data
        run: python scripts/download_fund_data.py
      - name: Commit changes
        run: |
          git config --global user.email "bot@mfhelper.com"
          git config --global user.name "MFHelper Bot"
          git add data/fund_holdings.json
          git commit -m "Auto-update holdings"
          git push
```

---

## 🎯 Quick Start Implementation

### Today (2 hours):
1. **Create sample holdings data** for top 10 funds manually
2. **Implement basic overlap API**
3. **Show proof-of-concept** on dashboard

### This Week:
1. Download AMFI data for top 50 funds
2. Build extractor script
3. Complete overlap feature

### Next Month:
1. Automate data updates
2. Add all 1000+ funds
3. Add sector overlap analysis

---

## 💰 Cost Analysis

| Approach | Setup Time | Monthly Cost | Maintenance | Best For |
|----------|-----------|--------------|-------------|----------|
| **Manual JSON** | 2 hours | ₹0 | 2 hrs/month | MVP |
| **Web Scraping** | 1 week | ₹0 | Auto | Growth |
| **Paid API** | 1 day | ₹5,000-50,000 | Minimal | Enterprise |

---

**My Recommendation for MFHelper:**

Start with **Manual JSON** (Phase 1) → Launch MVP → Get users → Then invest in automation!

---

## 📦 Data Sources Links

### Free APIs:
- **MFApi**: https://mfapi.in/
- **RapidAPI MF India**: https://rapidapi.com/hub
- **MoneyControl Scraper**: DIY

### Official Sources:
- **AMFI**: https://www.amfiindia.com/
- **NSE**: https://www.nseindia.com/
- **BSE**: https://www.bseindia.com/

### Datasets:
- **Kaggle**: Search "Indian Mutual Funds"
- **GitHub**: Many scrapers available

---

*Let me know if you want me to create the starter dataset with top 50 funds now!* 🚀
