"""
MoneyControl Portfolio Scraper - Get Real Holdings for Top 100 Funds

MoneyControl has consistent HTML structure for all funds:
URL format: https://www.moneycontrol.com/mutual-funds/[fund-name]/portfolio-holdings/[FUND_CODE]

Advantages:
- Single consistent HTML structure
- All AMCs in one place
- Already formatted tables
- Free to access
"""
import requests
from bs4 import BeautifulSoup
import pandas as pd
import json
from pathlib import Path
from datetime import datetime
import time
import re

class MoneyControlScraper:
    """
    Scrape portfolio holdings from MoneyControl
    Works for ALL mutual funds - one consistent format!
    """
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9',
            'Referer': 'https://www.moneycontrol.com/'
        })
        
        # Top 20 funds with MoneyControl URLs (will expand to 100)
        self.top_funds = [
            {'rank': 1, 'name': 'HDFC Flexi Cap Fund', 'amc': 'HDFC', 'category': 'Flexi Cap', 
             'url': 'https://www.moneycontrol.com/mutual-funds/hdfc-flexi-cap-fund-direct-plan-growth/portfolio-holdings/MHD1144'},
            
            {'rank': 2, 'name': 'ICICI Prudential Bluechip Fund', 'amc': 'ICICI Prudential', 'category': 'Large Cap',
             'url': 'https://www.moneycontrol.com/mutual-funds/icici-prudential-bluechip-fund-direct-plan-growth/portfolio-holdings/MPI008'},
            
            {'rank': 3, 'name': 'SBI Bluechip Fund', 'amc': 'SBI', 'category': 'Large Cap',
             'url': 'https://www.moneycontrol.com/mutual-funds/sbi-bluechip-fund-direct-growth/portfolio-holdings/MSB1069'},
            
            {'rank': 4, 'name': 'Axis Bluechip Fund', 'amc': 'Axis', 'category': 'Large Cap',
             'url': 'https://www.moneycontrol.com/mutual-funds/axis-bluechip-fund-direct-growth/portfolio-holdings/MAX117'},
            
            {'rank': 5, 'name': 'Mirae Asset Large Cap Fund', 'amc': 'Mirae Asset', 'category': 'Large Cap',
             'url': 'https://www.moneycontrol.com/mutual-funds/mirae-asset-large-cap-fund-direct-growth/portfolio-holdings/MMI002'},
            
            {'rank': 7, 'name': 'HDFC Top 100 Fund', 'amc': 'HDFC', 'category': 'Large Cap',
             'url': 'https://www.moneycontrol.com/mutual-funds/hdfc-top-100-fund-direct-plan-growth/portfolio-holdings/MHD068'},
            
            {'rank': 8, 'name': 'Kotak Equity Opportunities Fund', 'amc': 'Kotak', 'category': 'Large & Mid Cap',
             'url': 'https://www.moneycontrol.com/mutual-funds/kotak-equity-opportunities-fund-direct-growth/portfolio-holdings/MKO033'},
            
            {'rank': 11, 'name': 'Axis Midcap Fund', 'amc': 'Axis', 'category': 'Mid Cap',
             'url': 'https://www.moneycontrol.com/mutual-funds/axis-midcap-fund-direct-growth/portfolio-holdings/MAX129'},
            
            {'rank': 12, 'name': 'HDFC Mid Cap Opportunities Fund', 'amc': 'HDFC', 'category': 'Mid Cap',
             'url': 'https://www.moneycontrol.com/mutual-funds/hdfc-mid-cap-opportunities-fund-direct-plan-growth/portfolio-holdings/MHD003'},
            
            {'rank': 13, 'name': 'Mirae Asset Emerging Bluechip Fund', 'amc': 'Mirae Asset', 'category': 'Large & Mid Cap',
             'url': 'https://www.moneycontrol.com/mutual-funds/mirae-asset-emerging-bluechip-fund-direct-growth/portfolio-holdings/MMI001'},
        ]
    
    def scrape_fund_holdings(self, fund_url, fund_name):
        """
        Scrape holdings from a single fund's MoneyControl page
        Returns: list of {'stock': 'xxx', 'weight': 5.2, 'sector': 'Banking'}
        """
        print(f"\n{'='*80}")
        print(f"Scraping: {fund_name}")
        print(f"{'='*80}")
        print(f"URL: {fund_url}")
        
        try:
            response = self.session.get(fund_url, timeout=30)
            
            if response.status_code != 200:
                print(f"[ERROR] Status {response.status_code}")
                return None
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Find the correct table - look for "Stock Invested in" header
            holdings_table = None
            tables = soup.find_all('table')
            
            for table in tables:
                header_row = table.find('tr')
                if header_row:
                    headers = [th.text.strip() for th in header_row.find_all(['th', 'td'])]
                    if 'Stock Invested in' in headers:
                        holdings_table = table
                        break
            
            if not holdings_table:
                print("[ERROR] No portfolio holdings table found")
                return None
            
            holdings = []
            rows = holdings_table.find_all('tr')[1:]  # Skip header row
            
            for row in rows:
                cols = row.find_all('td')
                
                if len(cols) < 5:
                    continue
                
                # Col 0: Stock name (may have # prefix)
                # Col 1: Sector
                # Col 4: % of Total Holdings
                
                stock_name = cols[0].text.strip().replace('#', '').strip()
                sector = cols[1].text.strip() if len(cols) > 1 else 'Unknown'
                weight_text = cols[4].text.strip() if len(cols) > 4 else '0'
                
                # Skip summary rows
                if any(skip in stock_name.lower() for skip in ['total', 'equity', 'debt', 'cash', 'net', 'treps']):
                    continue
                
                if not stock_name or len(stock_name) < 3:
                    continue
                
                try:
                    weight = float(weight_text.replace('%', '').strip())
                except:
                    continue
                
                if weight > 0.1:  # Only include holdings > 0.1%
                    holdings.append({
                        'stock': stock_name,
                        'weight': round(weight, 2),
                        'sector': sector
                    })
            
            print(f"[OK] Found {len(holdings)} holdings")
            
            if holdings:
                print("\nTop 5 holdings:")
                for i, h in enumerate(holdings[:5], 1):
                    print(f"  {i}. {h['stock']}: {h['weight']}% ({h['sector']})")
            
            return holdings
            
        except Exception as e:
            print(f"[ERROR] Scraping failed: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def scrape_top_funds(self, limit=None):
        """
        Scrape all top funds (or limited number for testing)
        """
        print("\n" + "="*80)
        print("MONEYCONTROL SCRAPER - TOP FUNDS")
        print("="*80)
        print(f"\nTarget: {len(self.top_funds) if not limit else limit} funds")
        print("Strategy: Scrape consistent HTML from MoneyControl")
        
        funds_to_scrape = self.top_funds[:limit] if limit else self.top_funds
        
        scraped_data = {}
        success = 0
        failed = 0
        
        for fund in funds_to_scrape:
            fund_key = fund['name'].lower().replace(' ', '-').replace('&', 'and')
            
            holdings = self.scrape_fund_holdings(fund['url'], fund['name'])
            
            if holdings and len(holdings) > 5:
                scraped_data[fund_key] = {
                    'name': fund['name'],
                    'amc': fund['amc'],
                    'category': fund['category'],
                    'holdings': holdings,
                    'holdings_count': len(holdings),
                    'as_of_date': datetime.now().strftime('%Y-%m-%d'),
                    'source': 'MoneyControl Scraping'
                }
                success += 1
            else:
                print(f"[FAIL] {fund['name']} - No valid holdings found")
                failed += 1
            
            time.sleep(2)  # Be nice to MoneyControl servers
        
        # Summary
        print("\n\n" + "="*80)
        print("SCRAPING SUMMARY")
        print("="*80)
        print(f"\n Successfully scraped: {success} funds")
        print(f" Failed: {failed} funds")
        print(f"\n Success rate: {(success / len(funds_to_scrape) * 100):.0f}%")
        
        if scraped_data:
            # Save to fund_holdings.json
            self.update_fund_holdings(scraped_data)
        
        return scraped_data
    
    def update_fund_holdings(self, new_data):
        """
        Update fund_holdings.json with newly scraped data
        """
        output_file = Path(__file__).parent.parent / 'data' / 'fund_holdings.json'
        
        # Read existing
        existing_data = {}
        if output_file.exists():
            with open(output_file, 'r') as f:
                existing_data = json.load(f)
        
        # Merge
        if 'funds' not in existing_data:
            existing_data['funds'] = {}
        
        existing_data['funds'].update(new_data)
        existing_data['version'] = '2026-02'
        existing_data['last_updated'] = datetime.now().strftime('%Y-%m-%d')
        
        # Save
        with open(output_file, 'w') as f:
            json.dump(existing_data, f, indent=2, ensure_ascii=False)
        
        print(f"\n Updated fund_holdings.json")
        print(f"Location: {output_file}")
        print(f"Total funds in database: {len(existing_data['funds'])}")


def main():
    """Run scraper"""
    scraper = MoneyControlScraper()
    
    # Test with first 3 funds
    print("\n TEST MODE: Scraping first 3 funds...")
    scraper.scrape_top_funds(limit=3)
    
    # Uncomment to scrape all:
    # scraper.scrape_top_funds()


if __name__ == "__main__":
    main()
