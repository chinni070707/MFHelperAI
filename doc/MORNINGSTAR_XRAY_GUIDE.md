# Morningstar X-Ray Integration Guide

## What is Morningstar X-Ray?

Morningstar X-Ray is a comprehensive portfolio analysis tool that provides deep insights into your mutual fund portfolio by aggregating holdings across multiple funds and showing:

### Core Features:

1. **Asset Allocation**
   - Equity vs. Debt vs. Cash breakdown
   - Sub-asset class distribution
   - Weighted across entire portfolio

2. **Stock Intersection/Overlap**
   - Common holdings across funds
   - Concentration risk identification
   - Duplicate stock exposure

3. **Sector Exposure**
   - Weighted sector breakdown
   - Over/under-exposure analysis
   - Industry concentration

4. **Market Cap Distribution**
   - Large Cap vs. Mid Cap vs. Small Cap
   - Size-based diversification
   - Market cap drift analysis

5. **Style Box Analysis**
   - Value/Blend/Growth orientation
   - Large/Mid/Small cap focus
   - Morningstar style grid

6. **Geographic Exposure**
   - India vs. International
   - Country-wise breakdown
   - Currency exposure

7. **Risk Metrics**
   - Portfolio Sharpe ratio
   - Standard deviation
   - Maximum drawdown
   - Beta vs. benchmark

---

## Current MFHelper Implementation vs. Morningstar X-Ray

### ✅ Already Implemented

| Feature | MFHelper | Morningstar X-Ray |
|---------|----------|-------------------|
| **Overlap Analysis** | ✅ Complete | ✅ Yes |
| **Sector Allocation** | ✅ Pie charts | ✅ Visual breakdown |
| **Stock Concentration** | ✅ Top stocks | ✅ Concentration metrics |
| **Fund Comparison** | ✅ Side-by-side | ✅ Comparison view |
| **Holdings Count** | ✅ Displayed | ✅ Displayed |

**Location:** `frontend/overlap-analysis.html`

### 🔄 To Add (X-Ray Enhancements)

| Feature | Status | Priority | Complexity |
|---------|--------|----------|------------|
| **Market Cap Distribution Chart** | 🟡 Planned | High | Medium |
| **Style Box Grid** | 🟡 Planned | Medium | Low |
| **Geographic Exposure** | 🟡 Planned | Low | Medium |
| **Risk/Return Scatter** | 🟡 Planned | High | Medium |
| **Herfindahl Index** | 🟡 Planned | Medium | Low |
| **Morningstar Ratings** | 🔴 Not Started | Low | High |

---

## Implementation Plan

### Phase 1: Enhance Existing Overlap Analysis ✅ (Current)

**Already Done:**
- ✅ Stock overlap calculation
- ✅ Sector allocation pie chart
- ✅ Overlap heatmap
- ✅ Diversification score
- ✅ Top overlapping stocks table

**Improvements Needed:**
- [ ] Add market cap breakdown chart
- [ ] Show weighted sector exposure
- [ ] Add concentration metrics (HHI)
- [ ] Improve visual design

### Phase 2: Add X-Ray Style Visualizations

#### 1. Market Cap Distribution Chart
```javascript
// Add to overlap-analysis.html
{
  type: 'pie',
  values: [large_cap_pct, mid_cap_pct, small_cap_pct],
  labels: ['Large Cap', 'Mid Cap', 'Small Cap'],
  marker: {
    colors: ['#2E7D32', '#FFA726', '#EF5350']
  }
}
```

#### 2. Style Box Grid (Morningstar-style)
```html
<div class="style-box-grid">
  <div class="style-cell large-value"></div>
  <div class="style-cell large-blend"></div>
  <div class="style-cell large-growth"></div>
  <!-- ... -->
</div>
```

#### 3. Concentration Metrics
- **Herfindahl-Hirschman Index (HHI)**
  - Formula: Σ(weight²) × 10000
  - 0-1500: Highly diversified
  - 1500-2500: Moderately concentrated
  - 2500+: Highly concentrated

#### 4. Risk/Return Scatter Plot
```javascript
{
  x: returns_data,
  y: risk_data,
  mode: 'markers',
  marker: {
    size: aum_data,
    color: category_data
  },
  text: fund_names
}
```

### Phase 3: Morningstar Data Integration (Optional)

#### Option A: Web Scraping
```python
# See: backend/scripts/morningstar_integration.py
# Class: MorningstarScraper

from morningstar_integration import  MorningstarScraper

scraper = MorningstarScraper()
fund_data = scraper.get_fund_overview('f000000c7q')
portfolio = scraper.get_fund_portfolio('f000000c7q')
xray_data = scraper.get_xray_data('f000000c7q')
```

#### Option B: Manual Data Entry
- Download Morningstar factsheets
- Extract key metrics manually
- Store in database

#### Option C: Morningstar API (If Available)
- Contact Morningstar for API access
- Pricing TBD
- Enterprise-grade data

---

## Quick Wins: Features to Add Now

### 1. Market Cap Distribution (20 mins)

**Backend:** Already have data in `fund_holdings.json`

**Frontend Addition:**
```javascript
// Add to overlap-analysis.html
function displayMarketCapAllocation(data) {
  const marketCapData = {
    'Large Cap': 0,
    'Mid Cap': 0,
    'Small Cap': 0
  };
  
  // Calculate from holdings
  data.stocks.forEach(stock => {
    if (stock.market_cap) {
      marketCapData[stock.market_cap] += stock.weight;
    }
  });
  
  // Create Plotly chart
  Plotly.newPlot('marketCapChart', [{
    type: 'pie',
    values: Object.values(marketCapData),
    labels: Object.keys(marketCapData),
    hole: 0.4
  }]);
}
```

### 2. Concentration Score (15 mins)

**Add HHI calculation:**
```javascript
function calculateHerfindahlIndex(holdings) {
  const totalWeight = holdings.reduce((sum, h) => sum + h.weight, 0);
  const hhi = holdings.reduce((sum, h) => {
    const share = h.weight / totalWeight;
    return sum + (share * share);
  }, 0);
  
  return Math.round(hhi * 10000);
}
```

### 3. Enhanced Metrics Display (10 mins)

Add to results section:
- **Portfolio Concentration:** HHI score
- **Unique Stocks:** Count across all funds
- **Average Holding Size:** Mean weight per stock
- **Top Stock Exposure:** Largest single position

---

## Sample Morningstar URL Structure

### Fund URLs:
```
Overview:
https://www.morningstar.in/mutualfunds/{fund_code}/overview.aspx

Portfolio:
https://www.morningstar.in/mutualfunds/{fund_code}/portfolio.aspx

Performance:
https://www.morningstar.in/mutualfunds/{fund_code}/performance.aspx

Risk:
https://www.morningstar.in/mutualfunds/{fund_code}/risk.aspx
```

### Example Fund Codes:
- Bandhan Large Cap: `f000000c7q`
- HDFC Top 100: `f00000owj6`
- ICICI Pru Bluechip: `f00000oms3`

---

## API Endpoints to Create

### 1. X-Ray Analysis Endpoint
```python
@router.post("/api/xray/analyze")
async def analyze_xray(request: XRayRequest):
    """
    Full X-Ray analysis for portfolio
    
    Returns:
    - Asset allocation
    - Sector exposure
    - Market cap distribution
    - Concentration metrics
    - Risk metrics
    """
    pass
```

### 2. Market Cap Distribution Endpoint
```python
@router.get("/api/xray/market-cap/{fund_keys}")
async def get_market_cap_distribution(fund_keys: List[str]):
    """Return aggregated market cap breakdown"""
    pass
```

---

## Resources

### Morningstar Links:
- **Main Site:** https://www.morningstar.in/
- **Fund Search:** https://www.morningstar.in/mutualfunds/fundSelector.aspx
- **Research:** https://www.morningstar.in/research/default.aspx

### Similar Tools:
- **ValueResearch Portfolio X-Ray:** https://www.valueresearchonline.com/portfolio/
- **ET Money Portfolio Analyzer:** https://www.etmoney.com/
- **Groww Portfolio:** https://groww.in/portfolio

### Implementation Help:
- **Plotly Charts:** https://plotly.com/javascript/
- **BeautifulSoup:** https://www.crummy.com/software/BeautifulSoup/
- **Selenium:** https://selenium-python.readthedocs.io/

---

## Comparison: MFHelper vs. Morningstar X-Ray

| Feature | MFHelper | Morningstar X-Ray | Action |
|---------|----------|-------------------|--------|
| Overlap Analysis | ✅ Good | ✅ Excellent | Add HHI |
| Sector Breakdown | ✅ Charts | ✅ Interactive | Enhance UI |
| Market Cap | ❌ Missing | ✅ Visual | **Add Now** |
| Style Box | ❌ Missing | ✅ Grid View | Add simple version |
| Risk Metrics | ❌ Missing | ✅ Comprehensive | Phase 2 |
| Geographic | ❌ Missing | ✅ Detailed | Phase 3 |
| Ratings | ❌ Missing | ✅ Star Rating | Optional |

---

## Next Steps

### Immediate (This Week):
1. ✅ Create morningstar_integration.py (Done)
2. ✅ Document X-Ray features (Done)
3. 🔄 Add market cap chart to overlap-analysis.html
4. 🔄 Add HHI concentration metric
5. 🔄 Enhance visual design

### Short-term (Next 2 Weeks):
1. Create dedicated X-Ray analysis page
2. Add style box visualization
3. Implement risk/return scatter plot
4. Add more concentration metrics

### Long-term (Next Month):
1. Scrape Morningstar for additional data
2. Add historical trend analysis
3. Implement portfolio rebalancing suggestions
4. Add benchmark comparison

---

**Last Updated:** February 12, 2026
**Status:** Documentation Complete, Implementation Planned
