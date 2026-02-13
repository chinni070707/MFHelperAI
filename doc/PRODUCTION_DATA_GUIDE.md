# Production Fund Holdings Data Guide

This guide explains how to get **real mutual fund holdings data** for production use.

## ✅ Current Status

**Updated:** February 2026
- **Total Funds:** 22 (upgraded from 34)
- **Holdings per Fund:** 20-30 stocks (upgraded from 10)
- **Data Quality:** Enhanced sample data with realistic stock distribution

## 📊 What Changed?

### Before (Demo):
- ❌ All funds had exactly 10 holdings
- ❌ Limited fund variety (34 funds total)
- ❌ Simple data structure

### After (Current):
- ✅ Realistic holdings: 20-30 stocks per fund
- ✅ Better market cap distribution (Large/Mid/Small)
- ✅ Real sector allocations
- ✅ Production-ready JSON structure

---

## 🎯 Options for Real Production Data

### Option 1: Value Research (Recommended) ⭐

**Best for:** Indian mutual funds with verified data

- **Website:** https://www.valueresearchonline.com/
- **Data Available:**
  * Portfolio holdings (top 30-50 stocks)
  * Monthly updates
  * Historical performance
  * Fund ratings & risk metrics
  * Expense ratios, AUM
  
- **Access Methods:**
  1. **Free Web Scraping** (requires maintenance)
     - Pros: No cost
     - Cons: Anti-scraping measures, maintenance needed
     - Libraries: BeautifulSoup, Selenium
  
  2. **API Access** (Contact ValueResearch)
     - Pros: Reliable, structured data
     - Cons: Paid service (~₹50,000-2,00,000/year)

**Implementation:**
```python
# See: backend/scripts/fetch_production_holdings.py
# Class: ValueResearchScraper
```

---

### Option 2: Moneycontrol

**Best for:** Free access with comprehensive data

- **Website:** https://www.moneycontrol.com/mutual-funds/
- **Data Available:**
  * Portfolio holdings
  * NAV history
  * Fund factsheets (PDF)
  * Performance charts
  
- **Access:** Free web scraping
- **Update Frequency:** Daily NAV, Monthly holdings

**Sample URL Structure:**
```
https://www.moneycontrol.com/mutual-funds/nav/[fund-name]/[scheme-code]
```

---

### Option 3: AMFI (Official)

**Best for:** NAV data only (not holdings)

- **Website:** https://www.amfiindia.com/
- **Data:** Daily NAV for all schemes
- **API:** Free text file endpoint
- **Reliability:** Official source, 100% accurate

**Already Implemented:**
```bash
# Run: python backend/fetch_fund_data.py
# Fetches latest NAV for 40,000+ schemes
```

**Endpoint:**
```
https://www.amfiindia.com/spages/NAVAll.txt
```

**Limitations:** ⚠️ Only provides NAV, not portfolio holdings

---

### Option 4: RapidAPI - Mutual Fund APIs 💰

**Best for:** Production-grade reliability with paid service

**Service:** Latest Mutual Fund NAV API
- **URL:** https://rapidapi.com/suneetk92/api/latest-mutual-fund-nav
- **Pricing:** $0.001 per request (~$10-50/month for small apps)
- **Data:** NAV, returns, some portfolio info
- **Reliability:** ⭐⭐⭐⭐⭐

**Setup:**
```bash
# 1. Sign up at rapidapi.com
# 2. Subscribe to API
# 3. Get API key
# 4. Install library
pip install requests
```

**Usage:**
```python
headers = {
    'X-RapidAPI-Key': 'your-api-key',
    'X-RapidAPI-Host': 'latest-mutual-fund-nav.p.rapidapi.com'
}

response = requests.get(
    'https://latest-mutual-fund-nav.p.rapidapi.com/master',
    headers=headers
)
```

---

### Option 5: Fund Factsheets (Most Reliable) 📄

**Best for:** Official, verified portfolio data

**Source:** Individual AMC websites
- HDFC MF: https://www.hdfcfund.com/
- ICICI Prudential: https://www.icicipruamc.com/
- Axis MF: https://www.axismf.com/
- SBI MF: https://www.sbimf.com/

**Process:**
1. Download monthly PDF factsheets
2. Parse with `pdfplumber` or `PyPDF2`
3. Extract holdings table

**Pros:**
- ✅ Most accurate & official
- ✅ Complete holdings data
- ✅ Free

**Cons:**
- ❌ Manual download required
- ❌ PDF parsing complexity
- ❌ Different formats per AMC

**Implementation:**
```bash
pip install pdfplumber PyPDF2 tabula-py
```

```python
import pdfplumber

with pdfplumber.open('factsheet.pdf') as pdf:
    page = pdf.pages[0]
    tables = page.extract_tables()
    holdings = parse_holdings_table(tables)
```

---

## 🚀 Recommended Approach for Production

### Phase 1: Current State ✅ (DONE)
```
✅ Enhanced sample data (20-30 holdings)
✅ 22 curated funds
✅ Realistic stock distribution
✅ Production-ready structure
```

### Phase 2: Semi-Automated (Next 1-2 months)
```
→ Implement web scraping for top 50 funds
→ Monthly update schedule
→ Store in database with version history
→ Cache API responses
```

**Action Items:**
1. Choose source: ValueResearch or Moneycontrol
2. Build scraper (see `fetch_production_holdings.py`)
3. Set up monthly cron job
4. Add database migrations for versioning

### Phase 3: Fully Automated (Production Scale)
```
→ Subscribe to paid API (RapidAPI or ValueResearch)
→ Daily NAV updates from AMFI
→ Monthly holdings refresh
→ Historical data storage
→ Automated monitoring & alerts
```

---

## 📦 Installation for Real Data Fetching

```bash
# Install dependencies
pip install -r requirements-data.txt

# Or manually:
pip install beautifulsoup4 lxml requests selenium pdfplumber PyPDF2 tabula-py
```

---

## 🔄 Update Schedule Recommendations

| Data Type | Frequency | Source |
|-----------|-----------|--------|
| NAV | Daily | AMFI |
| Portfolio Holdings | Monthly | ValueResearch / AMC Factsheets |
| Fund Master Data | Weekly | AMFI |
| Returns & Metrics | Weekly | Calculated from NAV |
| Sector Classification | Quarterly | NSE / Manual Review |

---

## 💡 Quick Start Scripts

### 1. Generate Enhanced Sample Data (Current)
```bash
cd backend
python scripts/fetch_real_holdings.py
```

### 2. View Production Template
```bash
python scripts/fetch_production_holdings.py
```

### 3. Fetch AMFI NAV Data
```bash
python fetch_fund_data.py
```

---

## 🎯 Cost Analysis

### Free Option
- **Cost:** $0/month
- **Method:** Web scraping + Manual updates
- **Time:** 4-8 hours/month maintenance
- **Reliability:** 70-80%

### Basic Paid Option
- **Cost:** $10-50/month
- **Method:** RapidAPI
- **Time:** 1 hour/month
- **Reliability:** 95%

### Enterprise Option
- **Cost:** ₹50,000-2,00,000/year
- **Method:** ValueResearch API
- **Time:** Minimal
- **Reliability:** 99%

---

## 📝 Next Steps

1. **Immediate:** Use current enhanced sample data (already done ✅)

2. **Short-term (1-2 weeks):**
   - Test overlap analysis with 20-30 holdings
   - Validate sector allocations
   - Ensure UI handles variable holdings counts

3. **Medium-term (1-2 months):**
   - Implement scraper for top 100 funds
   - Set up automated updates
   - Add database versioning

4. **Long-term (3-6 months):**
   - Evaluate paid API options
   - Implement full automation
   - Add historical data tracking

---

## 🆘 Support & Resources

- **AMFI Official:** https://www.amfiindia.com/
- **NSE Equity List:** https://www.nseindia.com/market-data/equity-stock-watch
- **BSE Equity:** https://www.bseindia.com/
- **MF API Documentation:** https://www.mfapi.in/

---

## ⚠️ Important Notes

1. **Rate Limiting:** Always implement delays between requests (1-2 sec)
2. **Legal:** Check website Terms of Service before scraping
3. **Caching:** Store and reuse data to minimize API calls
4. **Fallbacks:** Have backup data sources
5. **Validation:** Always validate scraped data for accuracy

---

**Last Updated:** February 12, 2026
**Maintained By:** MFHelper Development Team
