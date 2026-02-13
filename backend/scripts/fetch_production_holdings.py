"""
Advanced Fund Holdings Scraper with Real Data Sources

This script provides multiple strategies for getting real fund holdings:
1. ValueResearch API/Scraping (recommended)
2. Moneycontrol Scraping
3. RapidAPI MF Data (paid but reliable)
4. Manual PDF factsheet parsing

For production use, you'll need to:
- Install: pip install beautifulsoup4 lxml selenium pdfplumber
- Get API keys for paid services (optional)
- Handle rate limiting and caching
"""

import requests
from bs4 import BeautifulSoup
import json
import time
from pathlib import Path
from datetime import datetime
import logging
from typing import Dict, List, Optional

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class ValueResearchScraper:
    """
    Scrape fund holdings from ValueResearch
    Note: Requires handling of dynamic content and anti-scraping measures
    """
    
    def __init__(self):
        self.base_url = 'https://www.valueresearchonline.com'
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Referer': 'https://www.valueresearchonline.com/'
        })
    
    def search_fund(self, fund_name: str) -> Optional[str]:
        """Search for fund and get its URL"""
        try:
            search_url = f"{self.base_url}/funds/search"
            params = {'q': fund_name}
            
            response = self.session.get(search_url, params=params, timeout=15)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Find first fund link (this is illustrative - actual structure varies)
            fund_link = soup.find('a', {'class': 'fund-name'})
            
            if fund_link and fund_link.get('href'):
                return fund_link['href']
            
            return None
            
        except Exception as e:
            logger.error(f"Error searching for fund '{fund_name}': {e}")
            return None
    
    def get_fund_holdings(self, fund_url: str) -> Optional[Dict]:
        """Get portfolio holdings from fund page"""
        try:
            portfolio_url = f"{self.base_url}{fund_url}/portfolio"
            
            response = self.session.get(portfolio_url, timeout=15)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Parse holdings table (structure varies by site)
            holdings_table = soup.find('table', {'class': 'portfolio-table'})
            
            if not holdings_table:
                return None
            
            holdings = []
            rows = holdings_table.find_all('tr')[1:]  # Skip header
            
            for row in rows:
                cols = row.find_all('td')
                if len(cols) >= 3:
                    stock_name = cols[0].get_text(strip=True)
                    weight = float(cols[1].get_text(strip=True).replace('%', ''))
                    sector = cols[2].get_text(strip=True)
                    
                    holdings.append({
                        'stock': stock_name,
                        'weight': weight,
                        'sector': sector
                    })
            
            return {
                'holdings': holdings,
                'as_of_date': datetime.now().strftime('%Y-%m-%d')
            }
            
        except Exception as e:
            logger.error(f"Error fetching holdings from {fund_url}: {e}")
            return None

class RapidAPIFetcher:
    """
    Fetch fund data from RapidAPI serviceskip (paid but reliable)
    Example: Latest MF NAV by RapidAPI
    """
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = 'https://latest-mutual-fund-nav.p.rapidapi.com'
        self.headers = {
            'X-RapidAPI-Key': api_key,
            'X-RapidAPI-Host': 'latest-mutual-fund-nav.p.rapidapi.com'
        }
    
    def get_fund_details(self, scheme_code: str) -> Optional[Dict]:
        """Fetch fund details including holdings"""
        try:
            url = f"{self.base_url}/fetchSchemeDetails"
            params = {'Scheme_Code': scheme_code}
            
            response = requests.get(url, headers=self.headers, params=params, timeout=15)
            response.raise_for_status()
            
            return response.json()
            
        except Exception as e:
            logger.error(f"Error fetching from RapidAPI: {e}")
            return None

class MoneycontrolScraper:
    """
    Scrape fund data from Moneycontrol
    Portfolio holdings are available on fund pages
    """
    
    def __init__(self):
        self.base_url = 'https://www.moneycontrol.com/mutual-funds'
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
    
    def search_fund(self, fund_name: str) -> Optional[str]:
        """Search Moneycontrol for fund"""
        # Implementation similar to ValueResearch
        pass
    
    def get_fund_portfolio(self, fund_code: str) -> Optional[Dict]:
        """Get portfolio from Moneycontrol fund page"""
        # Implementation would parse Moneycontrol's portfolio section
        pass

def create_production_holdings_template():
    """
    Create a template structure for production fund holdings
    Shows the expected format for real data integration
    """
    
    template = {
        "version": "2026-02",
        "last_updated": datetime.now().strftime('%Y-%m-%d'),
        "source": "Production - Multiple sources aggregated",
        "data_sources": {
            "nav_data": "AMFI",
            "holdings": "ValueResearch / Moneycontrol / Fund Factsheets",
            "market_cap_data": "NSE / BSE",
            "sector_classification": "NSE / AMFI"
        },
        "funds": {
            "example-fund-key": {
                "name": "Example Mutual Fund",
                "amc": "Example AMC",
                "category": "Equity - Large Cap",
                "scheme_code": "123456",
                "isin": "INF123456789",
                "aum": 50000,  # in Crores
                "expense_ratio": 0.85,
                "exit_load": "1% if redeemed within 1 year",
                "min_investment": 5000,
                "launch_date": "2020-01-01",
                "fund_manager": "Manager Name",
                "benchmark": "NIFTY 50",
                "returns": {
                    "1m": 2.5,
                    "3m": 7.8,
                    "6m": 12.5,
                    "1y": 18.5,
                    "3y": 15.2,
                    "5y": 14.8
                },
                "risk_metrics": {
                    "sharpe_ratio": 1.25,
                    "alpha": 2.5,
                    "beta": 0.98,
                    "std_deviation": 12.5
                },
                "holdings": [
                    {
                        "stock": "HDFC Bank",
                        "weight": 8.5,
                        "sector": "Banking",
                        "isin": "INE040A01034",
                        "market_cap": "Large Cap"
                    },
                    # ... more holdings
                ],
                "sector_allocation": {
                    "Banking": 22.5,
                    "IT": 18.3,
                    "Oil & Gas": 8.5,
                    "Auto": 6.2,
                    "Pharma": 5.8,
                    "FMCG": 7.5,
                    "Others": 31.2
                },
                "market_cap_allocation": {
                    "Large Cap": 75.5,
                    "Mid Cap": 18.3,
                    "Small Cap": 6.2
                },
                "as_of_date": "2026-01-31",
                "last_updated": datetime.now().isoformat()
            }
        }
    }
    
    # Save template
    output_path = Path(__file__).parent.parent / 'data' / 'fund_holdings_template.json'
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(template, f, indent=2, ensure_ascii=False)
    
    logger.info(f"✅ Template saved to: {output_path}")
    return template

def main():
    """Main function with production recommendations"""
    
    print("\n" + "=" * 80)
    print("PRODUCTION FUND HOLDINGS DATA GUIDE")
    print("=" * 80)
    
    print("\n📋 OPTIONS FOR GETTING REAL FUND HOLDINGS:\n")
    
    print("1️⃣  VALUE RESEARCH (Recommended for India)")
    print("   • URL: https://www.valueresearchonline.com/")
    print("   • Data: Portfolio holdings, NAV, returns, ratings")
    print("   • Access: Free web scraping or paid API")
    print("   • Update Frequency: Monthly")
    
    print("\n2️⃣  MONEYCONTROL")
    print("   • URL: https://www.moneycontrol.com/mutual-funds/")
    print("   • Data: Portfolio, NAV, factsheets")
    print("   • Access: Free web scraping")
    print("   • Update Frequency: Daily/Monthly")
    
    print("\n3️⃣  RAPIDAPI - INDIAN MUTUAL FUND API")
    print("   • URL: https://rapidapi.com/suneetk92/api/latest-mutual-fund-nav")
    print("   • Data: NAV, returns, some portfolio data")
    print("   • Access: Paid API ($0.001 per request)")
    print("   • Update Frequency: Daily")
    
    print("\n4️⃣  AMFI (Official)")
    print("   • URL: https://www.amfiindia.com/")
    print("   • Data: NAV only (not holdings)")
    print("   • Access: Free")
    print("   • Update Frequency: Daily")
    
    print("\n5️⃣  FUND FACTSHEETS (Most Reliable)")
    print("   • Source: Individual AMC websites")
    print("   • Data: Complete portfolio, top 10-30 holdings")
    print("   • Access: Free PDF download")
    print("   • Update Frequency: Monthly")
    print("   • Format: PDF - requires parsing (pdfplumber/PyPDF2)")
    
    print("\n" + "=" * 80)
    print("RECOMMENDED APPROACH FOR PRODUCTION:")
    print("=" * 80)
    
    print("\n✅ Phase 1: Quick Start (Current)")
    print("   • Use curated sample data with realistic stocks")
    print("   • 30-40 holdings per fund")
    print("   • Focus on popular large-cap funds")
    
    print("\n✅ Phase 2: Semi-Automated (Next)")
    print("   • Scrape ValueResearch/Moneycontrol monthly")
    print("   • Store in database with version history")
    print("   • Cache API responses")
    
    print("\n✅ Phase 3: Fully Automated (Production)")
    print("   • Subscribe to RapidAPI or paid data service")
    print("   • Parse AMC factsheets automatically (PDF)")
    print("   • Daily NAV updates from AMFI")
    print("   • Monthly holdings refresh")
    print("   • Store historical data for backtesting")
    
    print("\n" + "=" * 80)
    print("NEXT STEPS:")
    print("=" * 80)
    
    print("\n1. Run the basic script to generate enhanced sample data:")
    print("   python backend/scripts/fetch_real_holdings.py")
    
    print("\n2. For real production data, install dependencies:")
    print("   pip install beautifulsoup4 lxml requests selenium pdfplumber")
    
    print("\n3. Choose your data source:")
    print("   • Free: Manual scraping (requires maintenance)")
    print("   • Paid: RapidAPI ($10-50/month for small scale)")
    print("   • Hybrid: AMFI for NAV + Manual holdings updates")
    
    # Generate template
    print("\n\n📝 Generating production-ready template...")
    create_production_holdings_template()
    
    print("\n✅ Setup complete!")

if __name__ == "__main__":
    main()
