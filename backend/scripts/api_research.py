"""
Indian Mutual Fund Data APIs - Comprehensive Overview

Research on available APIs from AMCs and official sources
Date: February 2026
"""

# ============================================================================
# OFFICIAL AMC APIs - Reality Check
# ============================================================================

"""
SHORT ANSWER: Most AMCs do NOT provide public APIs ❌

DETAILED BREAKDOWN:

1. HDFC Asset Management
   Public API: ❌ NO
   What they offer: Web portal, PDF factsheets
   
2. ICICI Prudential AMC
   Public API: ❌ NO
   What they offer: Web portal, downloadable reports
   
3. SBI Funds Management
   Public API: ❌ NO
   What they offer: Website, factsheets
   
4. Kotak Mahindra AMC
   Public API: ❌ NO
   What they offer: Website, mobile app (but no public API)
   
5. Axis Asset Management
   Public API: ❌ NO
   What they offer: Website, factsheets

WHY DON'T AMCs PROVIDE APIs?
- Not their core business model
- Focus on distribution through advisors/platforms
- Data aggregators (like Value Research) fill this gap
- Regulatory focus is on disclosure, not tech integration
"""

# ============================================================================
# WHAT IS AVAILABLE - Official & Third-Party APIs
# ============================================================================

AVAILABLE_APIS = {
    
    # 1. AMFI (Official but not REST API)
    "AMFI NAV Data": {
        "provider": "Association of Mutual Funds in India (Official)",
        "type": "Text file endpoint",
        "url": "https://www.amfiindia.com/spages/NAVAll.txt",
        "cost": "FREE",
        "data": "Daily NAV for ALL schemes (~40,000+)",
        "format": "Semicolon-separated text",
        "update_frequency": "Daily",
        "api_type": "❌ Not REST API (just a text file)",
        "reliability": "⭐⭐⭐⭐⭐ (Official source)",
        "holdings": "❌ NO - Only NAV data",
        "example": """
            # Fetch NAV data
            response = requests.get('https://www.amfiindia.com/spages/NAVAll.txt')
            # Parse semicolon-separated format
        """
    },
    
    # 2. MF API (Community Project)
    "MF API (mfapi.in)": {
        "provider": "Community project",
        "type": "REST API",
        "url": "https://api.mfapi.in",
        "cost": "FREE",
        "data": "NAV, historical data, returns",
        "format": "JSON",
        "update_frequency": "Daily",
        "api_type": "✅ REST API",
        "reliability": "⭐⭐⭐⭐ (Good, but community-maintained)",
        "holdings": "❌ NO - Only NAV and returns",
        "documentation": "https://www.mfapi.in/",
        "example": """
            # Get list of all funds
            GET https://api.mfapi.in/mf
            
            # Get specific fund details
            GET https://api.mfapi.in/mf/119551
            
            # Response includes NAV, returns, but NOT holdings
        """
    },
    
    # 3. RapidAPI - Latest Mutual Fund NAV
    "RapidAPI - MF NAV": {
        "provider": "RapidAPI (Third-party)",
        "type": "REST API",
        "url": "https://rapidapi.com/suneetk92/api/latest-mutual-fund-nav",
        "cost": "💰 PAID - $0.001 per request (~$10-50/month)",
        "data": "NAV, basic fund info, returns",
        "format": "JSON",
        "update_frequency": "Daily",
        "api_type": "✅ REST API",
        "reliability": "⭐⭐⭐⭐⭐",
        "holdings": "❌ NO - Limited to NAV and returns",
        "example": """
            headers = {
                'X-RapidAPI-Key': 'your-key',
                'X-RapidAPI-Host': 'latest-mutual-fund-nav.p.rapidapi.com'
            }
            response = requests.get(
                'https://latest-mutual-fund-nav.p.rapidapi.com/master',
                headers=headers
            )
        """
    },
    
    # 4. BSE StAR MF Platform
    "BSE StAR MF API": {
        "provider": "BSE (Bombay Stock Exchange)",
        "type": "API for registered intermediaries",
        "url": "https://bsestarmf.in/",
        "cost": "FREE (but requires registration as intermediary)",
        "data": "NAV, transactions, fund details",
        "format": "API",
        "api_type": "✅ API Available",
        "access": "🔒 Requires BSE registration (ARN/RIA)",
        "reliability": "⭐⭐⭐⭐⭐ (Official exchange platform)",
        "holdings": "❌ NO - Transaction focused",
        "use_case": "For distributors/advisors to place orders",
        "note": "Not accessible without proper credentials"
    },
    
    # 5. NSE Mutual Fund Portal
    "NSE MF Portal": {
        "provider": "NSE (National Stock Exchange)",
        "type": "Portal",
        "url": "https://www.nseindia.com/invest/mutual-funds",
        "cost": "FREE",
        "api_type": "❌ NO Public API",
        "data": "Fund information, NAV",
        "access": "Web scraping only",
        "holdings": "❌ NO"
    },
    
    # 6. Value Research (No Public API)
    "Value Research": {
        "provider": "Value Research (Private)",
        "api_type": "❌ NO Public API",
        "url": "https://www.valueresearchonline.com",
        "cost": "Premium subscription available",
        "data": "Holdings, ratings, analysis",
        "access": "Web scraping or paid data feeds (enterprise)",
        "holdings": "✅ YES - But requires scraping or enterprise deal",
        "note": "They may offer data APIs for enterprise clients (contact sales)"
    },
    
    # 7. Morningstar (No Free API)
    "Morningstar": {
        "provider": "Morningstar",
        "api_type": "✅ API Available (Enterprise)",
        "url": "https://www.morningstar.in",
        "cost": "💰💰💰 EXPENSIVE - Enterprise pricing",
        "data": "Holdings, ratings, analytics, X-Ray",
        "access": "Contact Morningstar for licensing",
        "holdings": "✅ YES",
        "note": "Used by large institutions, very expensive"
    },
    
    # 8. Moneycontrol (No API)
    "Moneycontrol": {
        "provider": "Moneycontrol",
        "api_type": "❌ NO Public API",
        "url": "https://www.moneycontrol.com/mutual-funds",
        "data": "Holdings, NAV, analysis",
        "access": "Web scraping only",
        "holdings": "✅ YES - Via scraping"
    }
}

# ============================================================================
# SUMMARY: What Data Requires What Approach
# ============================================================================

DATA_ACCESS_MATRIX = """
┌────────────────────────┬──────────────────┬─────────────────┬──────────────┐
│ Data Type              │ Available Via    │ Cost            │ Reliability  │
├────────────────────────┼──────────────────┼─────────────────┼──────────────┤
│ Daily NAV              │ AMFI (text file) │ FREE ✅         │ ⭐⭐⭐⭐⭐    │
│                        │ MF API (REST)    │ FREE ✅         │ ⭐⭐⭐⭐      │
│                        │ RapidAPI         │ ~$10-50/mo 💰   │ ⭐⭐⭐⭐⭐    │
├────────────────────────┼──────────────────┼─────────────────┼──────────────┤
│ Fund Returns           │ MF API           │ FREE ✅         │ ⭐⭐⭐⭐      │
│                        │ Calculated       │ FREE ✅         │ ⭐⭐⭐⭐⭐    │
├────────────────────────┼──────────────────┼─────────────────┼──────────────┤
│ Portfolio Holdings     │ AMC Websites     │ FREE ✅         │ ⭐⭐⭐⭐⭐    │
│ (30-50 stocks)         │ PDF Factsheets   │ FREE ✅         │ ⭐⭐⭐⭐⭐    │
│                        │ Value Research   │ Scraping 🔧     │ ⭐⭐⭐⭐      │
│                        │ Moneycontrol     │ Scraping 🔧     │ ⭐⭐⭐⭐      │
│                        │ Morningstar      │ $$$$ 💰💰💰    │ ⭐⭐⭐⭐⭐    │
├────────────────────────┼──────────────────┼─────────────────┼──────────────┤
│ Fund Master Data       │ AMFI             │ FREE ✅         │ ⭐⭐⭐⭐⭐    │
│ (scheme codes, ISINs)  │ BSE StAR         │ Registration 🔒 │ ⭐⭐⭐⭐⭐    │
├────────────────────────┼──────────────────┼─────────────────┼──────────────┤
│ Ratings, Analytics     │ Value Research   │ Scraping 🔧     │ ⭐⭐⭐⭐      │
│                        │ Morningstar      │ $$$$ 💰💰💰    │ ⭐⭐⭐⭐⭐    │
├────────────────────────┼──────────────────┼─────────────────┼──────────────┤
│ Transactions           │ BSE StAR MF      │ Registration 🔒 │ ⭐⭐⭐⭐⭐    │
│ (buying/selling)       │ AMC Platforms    │ Direct 🔒       │ ⭐⭐⭐⭐⭐    │
└────────────────────────┴──────────────────┴─────────────────┴──────────────┘

Legend:
✅ = Free
💰 = Paid
🔧 = Requires scraping
🔒 = Requires credentials/registration
"""

# ============================================================================
# RECOMMENDATIONS
# ============================================================================

RECOMMENDATIONS = """
FOR YOUR USE CASE (Portfolio Holdings):

🥇 BEST APPROACH - Hybrid Strategy:
   1. NAV Data: Use AMFI text file or MF API (FREE, daily updates)
   2. Holdings: Scrape AMC websites monthly (FREE, most accurate)
   3. Backup: Parse PDF factsheets
   4. Optional: Subscribe to RapidAPI for NAV (~$20/month)

🥈 ALTERNATIVE - If Budget Allows:
   1. Morningstar Enterprise API ($$$$, complete data)
   2. Value Research Enterprise ($$, good for India)

🥉 QUICK START (Current State):
   1. Use MF API for basic fund info ✅
   2. Manually curated holdings (what you have now) ✅
   3. Gradually add AMC scrapers ✅

❌ NOT RECOMMENDED:
   - Waiting for AMCs to launch public APIs (won't happen soon)
   - Paying for BSE StAR without being a registered intermediary
   - Relying solely on Value Research scraping (fragile)
"""

# ============================================================================
# CODE EXAMPLES
# ============================================================================

def demo_available_apis():
    """Demonstrate actually working APIs"""
    
    print("="*80)
    print("WORKING APIs FOR INDIAN MUTUAL FUNDS")
    print("="*80)
    
    # 1. AMFI NAV Data
    print("\n1️⃣  AMFI NAV Data (Official)")
    print("   URL: https://www.amfiindia.com/spages/NAVAll.txt")
    print("   Data: All scheme NAVs (~40,000 schemes)")
    print("   Cost: FREE")
    print("   Example:")
    print("""
    import requests
    
    response = requests.get('https://www.amfiindia.com/spages/NAVAll.txt')
    lines = response.text.split('\\n')
    
    # Parse format: SchemeCode;ISINDiv;ISINGrowth;SchemeName;NAV;Date
    for line in lines:
        if ';' in line:
            parts = line.split(';')
            if len(parts) >= 5:
                scheme_code, scheme_name, nav = parts[0], parts[3], parts[4]
                print(f"{scheme_name}: ₹{nav}")
    """)
    
    # 2. MF API
    print("\n2️⃣  MF API (Community)")
    print("   URL: https://api.mfapi.in")
    print("   Data: NAV, returns, historical data")
    print("   Cost: FREE")
    print("   Example:")
    print("""
    import requests
    
    # Get all funds
    response = requests.get('https://api.mfapi.in/mf')
    funds = response.json()
    
    # Get specific fund (HDFC Flexi Cap - 119551)
    response = requests.get('https://api.mfapi.in/mf/119551')
    fund_data = response.json()
    print(fund_data['meta']['scheme_name'])
    print(f"NAV: {fund_data['data'][0]['nav']}")
    """)
    
    # 3. RapidAPI
    print("\n3️⃣  RapidAPI - Latest MF NAV (Paid)")
    print("   URL: https://rapidapi.com/suneetk92/api/latest-mutual-fund-nav")
    print("   Data: NAV, returns")
    print("   Cost: ~$10-50/month")
    print("   Example:")
    print("""
    import requests
    
    headers = {
        'X-RapidAPI-Key': 'your-api-key',
        'X-RapidAPI-Host': 'latest-mutual-fund-nav.p.rapidapi.com'
    }
    
    response = requests.get(
        'https://latest-mutual-fund-nav.p.rapidapi.com/master',
        headers=headers
    )
    data = response.json()
    """)
    
    print("\n" + "="*80)
    print("⚠️  IMPORTANT: None of these APIs provide portfolio holdings!")
    print("    For holdings, you MUST scrape AMC websites or parse PDFs")
    print("="*80)

if __name__ == "__main__":
    demo_available_apis()
