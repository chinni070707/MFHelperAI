# AMC Website Scraping Guide - Best Approach for Fund Holdings

## ✅ Why AMC Websites Are Better Than Value Research

### Official AMC Websites (Recommended)

**Advantages:**
- ✅ **Most Accurate** - Primary source, official data
- ✅ **Complete Holdings** - Full portfolio, not just top 10
- ✅ **Latest Data** - Updated monthly as per SEBI regulations
- ✅ **PDF Factsheets** - Downloadable for backup
- ✅ **Legal Compliance** - Regulated disclosures
- ✅ **No Rate Limiting** - More lenient than aggregators
- ✅ **Free** - No subscription needed

**Example:**
```
HDFC Flexi Cap Fund holdings:
Official: https://www.hdfcfund.com/mutual-funds-investment/hdfc-flexi-cap-fund
```

### Value Research (Alternative)

**Advantages:**
- ✅ Consolidated view across AMCs
- ✅ Easier to parse (consistent structure)
- ✅ Additional analytics

**Disadvantages:**
- ❌ Secondary source (may have delays)
- ❌ Often shows only top holdings
- ❌ Requires account for detailed data
- ❌ Stricter anti-scraping measures
- ❌ May be incomplete for some funds

**Example:**
```
Value Research URL:
https://www.valueresearchonline.com/funds/16026/hdfc-flexi-cap-fund-direct-plan/?ln=en#fund-portfolio
```

---

## 📊 Top 10 AMCs by AUM (Focus Area)

These 10 AMCs cover **~80% of industry AUM**:

| Rank | AMC | Website | AUM (₹ Cr) | Implementation |
|------|-----|---------|------------|----------------|
| 1 | HDFC Asset Management | [hdfcfund.com](https://www.hdfcfund.com) | 5,00,000+ | ✅ Started |
| 2 | ICICI Prudential AMC | [icicipruamc.com](https://www.icicipruamc.com) | 4,80,000+ | ✅ Started |
| 3 | SBI Funds Management | [sbimf.com](https://www.sbimf.com) | 4,50,000+ | 🔄 Todo |
| 4 | Aditya Birla Sun Life | [Birla Sunlife](https://www.birlasunlife.com) | 2,80,000+ | 🔄 Todo |
| 5 | Nippon India MF | [nipponindiamf.com](https://mf.nipponindiaim.com) | 2,50,000+ | 🔄 Todo |
| 6 | Kotak Mahindra AMC | [kotakmf.com](https://www.kotakmf.com) | 2,20,000+ | ✅ Started |
| 7 | Axis Asset Management | [axismf.com](https://www.axismf.com) | 2,10,000+ | ✅ Started |
| 8 | UTI Asset Management | [utimf.com](https://www.utimf.com) | 2,00,000+ | 🔄 Todo |
| 9 | DSP Investment Managers | [dspim.com](https://www.dspim.com) | 1,20,000+ | 🔄 Todo |
| 10 | Tata Asset Management | [tatamutualfund.com](https://www.tatamutualfund.com) | 1,00,000+ | 🔄 Todo |

---

## 🏗️ AMC Website Structure Analysis

### HDFC Asset Management
**Website:** https://www.hdfcfund.com/

**Structure:**
```
Fund Categories:
- /mutual-funds-investment/equity-funds
- /mutual-funds-investment/debt-funds
- /mutual-funds-investment/hybrid-funds

Individual Fund:
- /mutual-funds-investment/hdfc-flexi-cap-fund

Data Available:
✅ Portfolio holdings table
✅ PDF factsheet download
✅ NAV history
✅ Performance data
✅ Sector allocation chart
```

**Holdings Location:**
- Tab: "Portfolio" or "Holdings"
- Table with: Stock Name | % of Portfolio | Sector

**Factsheet:**
- PDF link usually at top/bottom
- Monthly updated
- Contains top 30-50 holdings

---

### ICICI Prudential AMC
**Website:** https://www.icicipruamc.com/

**Structure:**
```
Fund List:
- /funds/mutual-funds

Individual Fund:
- /funds/[fund-slug]

Data Available:
✅ Portfolio composition
✅ Downloadable factsheet
✅ Interactive charts
✅ Historical performance
```

---

### SBI Mutual Fund
**Website:** https://www.sbimf.com/

**Structure:**
```
Fund Navigation:
- Category-wise listing
- Direct plan / Regular plan separate

Holdings:
- Portfolio tab on fund page
- Excel/PDF download options
```

---

## 🛠️ Implementation Strategy

### Phase 1: Core AMCs (Week 1-2)
Implement scrapers for:
1. HDFC
2. ICICI Prudential  
3. SBI
4. Kotak
5. Axis

**Target:** 50-60 top funds from these 5 AMCs

---

### Phase 2: Remaining Top 10 (Week 3-4)
Implement:
6. Aditya Birla Sun Life
7. Nippon India
8. UTI
9. DSP
10. Tata

**Target:** Complete top 10 AMC coverage

---

### Phase 3: Automation (Week 5)
- Set up monthly update schedule
- Error handling & notifications
- Data validation
- Backup to database

---

## 📝 Scraping Checklist for Each AMC

For each AMC website, document:

- [ ] Base URL
- [ ] Fund listing page structure
- [ ] Individual fund page URL pattern
- [ ] Holdings table selector
- [ ] Portfolio section location
- [ ] Factsheet PDF link
- [ ] NAV data location
- [ ] Category/scheme type classification
- [ ] Direct vs Regular plan naming
- [ ] Rate limiting requirements
- [ ] Any anti-bot measures
- [ ] Login requirements (if any)

---

## 🔧 Technical Implementation

### 1. Inspect AMC Website

**Chrome DevTools:**
```
1. Open fund page
2. Right-click holdings table → "Inspect"
3. Find table element and classes
4. Note the structure:
   - <table class="portfolio-table">
   - <tr><td>Stock Name</td><td>Weight</td><td>Sector</td></tr>
5. Check if data loads dynamically (Network tab)
```

### 2. Write Scraper

```python
from amc_scrapers import HDFCAMCScraper

scraper = HDFCAMCScraper()

# Get fund list
funds = scraper.get_fund_list()

# Get holdings for specific fund
holdings = scraper.get_fund_holdings(funds[0]['url'])

print(f"Found {len(holdings['holdings'])} stocks")
```

### 3. Handle Edge Cases

**Common Issues:**
- JavaScript-rendered content → Use Selenium
- CAPTCHA → Add delays, rotate User-Agent
- Rate limiting → Implement exponential backoff
- Dynamic URLs → Parse from page source
- Missing data → Fallback to PDF parsing

### 4. Data Validation

```python
def validate_holdings(holdings_data):
    """Validate scraped holdings data"""
    
    # Check required fields
    assert 'name' in holdings_data
    assert 'holdings' in holdings_data
    assert len(holdings_data['holdings']) > 0
    
    # Validate holdings structure
    for holding in holdings_data['holdings']:
        assert 'stock' in holding
        assert 'weight' in holding
        assert 0 <= holding['weight'] <= 100
    
    # Check total weight
    total_weight = sum(h['weight'] for h in holdings_data['holdings'])
    assert 50 <= total_weight <= 150  # Allow some variance
    
    return True
```

---

## 📅 Update Schedule

### Monthly Updates (Required)
- **Frequency:** 1st week of every month
- **Why:** AMCs publish factsheets by 7th of month
- **What:** Update holdings, NAV, performance metrics

### Weekly Updates (Optional)
- **Frequency:** Every Monday
- **What:** NAV only (for tracking)

### Daily Updates (Advanced)
- **What:** NAV from AMFI
- **Source:** https://www.amfiindia.com/spages/NAVAll.txt

---

## 💾 Data Storage

### JSON Structure
```json
{
  "version": "2026-02",
  "last_updated": "2026-02-12",
  "source": "Official AMC Websites",
  "data_quality": "High - Direct from source",
  "funds": {
    "hdfc-flexi-cap-fund-direct-plan": {
      "name": "HDFC Flexi Cap Fund Direct Plan",
      "amc": "HDFC Mutual Fund",
      "scheme_code": "119551",
      "category": "Flexi Cap",
      "holdings": [
        {
          "stock": "HDFC Bank",
          "weight": 8.5,
          "sector": "Banking",
          "isin": "INE040A01034"
        }
      ],
      "total_holdings": 45,
      "as_of_date": "2026-01-31",
      "source_url": "https://www.hdfcfund.com/...",
      "factsheet_url": "https://www.hdfcfund.com/.../factsheet.pdf",
      "scraped_at": "2026-02-12T10:30:00"
    }
  }
}
```

---

## 🚀 Quick Start

### 1. Run AMC Scraper
```bash
cd backend
python scripts/amc_scrapers.py
```

### 2. Collect Holdings
```python
from amc_scrapers import AMCDataCollector

collector = AMCDataCollector()

# Collect from all AMCs (top 10 funds each)
data = collector.collect_all_holdings(top_n_funds_per_amc=10)

# Save to file
collector.save_to_file(data)
```

### 3. Verify Data
```bash
# Check generated file
cat backend/data/fund_holdings.json | jq '.funds | length'
```

---

## ⚠️ Important Notes

### Legal Considerations
- ✅ Public data - freely available
- ✅ No login required
- ✅ Respect robots.txt
- ✅ Add delays between requests
- ❌ Don't overload servers
- ❌ Don't scrape subscriber-only content

### Best Practices
1. **Rate Limiting:** 2-3 seconds between requests
2. **User-Agent:** Use realistic browser UA
3. **Error Handling:** Graceful failures, retry logic
4. **Logging:** Track success/failure for each fund
5. **Backup:** Keep copy of previous month's data
6. **Validation:** Check data quality before replacing old data

---

## 📊 Expected Results

**After Full Implementation:**
