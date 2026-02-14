"""
MoneyControl Portfolio Scraper - Get Real Holdings for 300+ Funds

Scrapes from MoneyControl with smart features:
- Loads 346 funds from moneycontrol_fund_codes.json
- Skips already-scraped funds (checks JSON and database)
- Tracks progress in scraping_todo.md
- Handles errors gracefully with retry list
- Rate limiting: 2 seconds between requests

URL format: https://www.moneycontrol.com/mutual-funds/[fund-name]/portfolio-holdings/[FUND_CODE]
"""
import requests
from bs4 import BeautifulSoup
import pandas as pd
import json
from pathlib import Path
from datetime import datetime
import time
import re
import sys
import os

# Add parent directory to path for database imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models.models import FundMaster

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
        
        # Paths
        self.data_dir = Path(__file__).parent.parent / 'data'
        self.fund_codes_file = self.data_dir / 'moneycontrol_fund_codes.json'
        self.holdings_file = self.data_dir / 'fund_holdings.json'
        self.todo_file = Path(__file__).parent / 'scraping_todo.md'
        
        # Load fund codes from JSON (346 funds)
        self.all_funds = self.load_fund_codes()
        self.existing_in_json = set()
        self.existing_in_db = set()
        self.failed_funds = []
        
    def load_fund_codes(self):
        """Load all 346 fund codes from moneycontrol_fund_codes.json"""
        print("\n" + "="*80)
        print("LOADING FUND CODES")
        print("="*80)
        
        if not self.fund_codes_file.exists():
            print(f"[ERROR] Fund codes file not found: {self.fund_codes_file}")
            return []
        
        with open(self.fund_codes_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        funds_dict = data.get('funds', {})
        funds_list = []
        
        for code, fund_info in funds_dict.items():
            # Build MoneyControl URL from code and slug
            url = f"https://www.moneycontrol.com/mutual-funds/{fund_info['slug']}/portfolio-holdings/{code}"
            
            funds_list.append({
                'code': code,
                'name': fund_info['name'],
                'slug': fund_info['slug'],
                'category': fund_info.get('category', 'Unknown'),
                'url': url
            })
        
        print(f"[OK] Loaded {len(funds_list)} funds from MoneyControl codes")
        return funds_list
    
    def check_existing_data(self):
        """Check what funds already exist in JSON and database"""
        print("\n" + "="*80)
        print("CHECKING EXISTING DATA")
        print("="*80)
        
        # Check JSON file
        if self.holdings_file.exists():
            try:
                with open(self.holdings_file, 'r', encoding='utf-8', errors='replace') as f:
                    existing_data = json.load(f)
                    existing_funds = existing_data.get('funds', {})
                    self.existing_in_json = set(existing_funds.keys())
                    print(f"[OK] Found {len(self.existing_in_json)} funds in fund_holdings.json")
            except Exception as e:
                print(f"[WARNING] Could not load JSON file: {e}")
                print(f"[INFO] Will start with empty dataset")
                self.existing_in_json = set()
        else:
            print("[INFO] No existing fund_holdings.json found")
        
        # Check database
        try:
            db = SessionLocal()
            db_funds = db.query(FundMaster.scheme_name).filter(FundMaster.is_active == True).all()
            # Normalize names to match fund_key format
            for fund in db_funds:
                if fund.scheme_name:
                    normalized = fund.scheme_name.lower().replace(' ', '-').replace('&', 'and')
                    self.existing_in_db.add(normalized)
            print(f"[OK] Found {len(db_funds)} funds in database")
            db.close()
        except Exception as e:
            print(f"[WARNING] Could not check database: {e}")
            print("[INFO] Will only check JSON for existing funds")
        
        # Combined existing
        all_existing = self.existing_in_json | self.existing_in_db
        print(f"\n Total existing (JSON + DB): {len(all_existing)} funds")
        return all_existing
    
    def update_todo_file(self, status_msg, fund_results=None):
        """Update scraping_todo.md with current progress"""
        try:
            now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            
            content = f"""# Mutual Fund Scraping Progress Tracker

**Last Updated:** {now}  
**Status:** {status_msg}

---

## 📊 Overall Progress

- **Total Funds Available:** {len(self.all_funds)}
- **Already Existing:** {len(self.existing_in_json | self.existing_in_db)}
- **To Scrape:** {len(self.all_funds) - len(self.existing_in_json | self.existing_in_db)}
- **Successfully Scraped:** {len([r for r in (fund_results or []) if r.get('success')])}
- **Failed:** {len(self.failed_funds)}

---

## ✅ Recently Completed

"""
            
            if fund_results:
                recent = [r for r in fund_results[-10:] if r.get('success')]
                if recent:
                    for r in recent:
                        content += f"- ✓ {r['name']} ({r['holdings_count']} holdings)\n"
                else:
                    content += "None yet\n"
            else:
                content += "None yet\n"
            
            content += "\n---\n\n## ❌ Failed Funds\n\n"
            
            if self.failed_funds:
                for failed in self.failed_funds[-20:]:
                    content += f"- {failed['name']} ({failed['code']}) - {failed['error']}\n"
            else:
                content += "None\n"
            
            content += """\n---\n\n## 📝 Notes

- **Data Source:** MoneyControl fund codes from `backend/data/moneycontrol_fund_codes.json`
- **Skip Logic:** Skip if fund exists in `fund_holdings.json` OR database `FundMaster` table
- **Rate Limiting:** 2 seconds delay between requests
- **Validation:** Run `python backend/scripts/validate_holdings.py` after scraping

---

**Auto-generated by scrape_moneycontrol.py**
"""
            
            with open(self.todo_file, 'w', encoding='utf-8') as f:
                f.write(content)
                
        except Exception as e:
            print(f"[WARNING] Could not update TODO file: {e}")
    
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
            # IMPORTANT: Pick the table with the MOST rows (full portfolio, not just top 10)
            holdings_table = None
            table_col_layout = "standard"  # or "extended" if has 'Sector Total'
            best_row_count = 0
            
            tables = soup.find_all('table')
            
            for table in tables:
                header_row = table.find('tr')
                if header_row:
                    headers = [th.text.strip() for th in header_row.find_all(['th', 'td'])]
                    if 'Stock Invested in' in headers and '% of Total Holdings' in headers:
                        row_count = len(table.find_all('tr'))
                        # Pick the table with the most rows (full portfolio)
                        if row_count > best_row_count:
                            best_row_count = row_count
                            holdings_table = table
                            # Detect column layout
                            if 'Sector Total' in headers:
                                table_col_layout = "extended"  # Has extra 'Sector Total' column
                            else:
                                table_col_layout = "standard"
            
            if not holdings_table:
                print("[ERROR] No portfolio holdings table found")
                return None
            
            print(f"[OK] Using table with {best_row_count} rows (layout: {table_col_layout})")
            
            holdings = []
            rows = holdings_table.find_all('tr')[1:]  # Skip header row
            
            for row in rows:
                cols = row.find_all('td')
                
                if len(cols) < 4:
                    continue
                
                # MoneyControl has two column layouts:
                # Standard: Stock | Sector | Value(Mn) | % of Total Holdings | 1M Change
                # Extended: Stock | Sector | Sector Total | Value(Mn) | % of Total Holdings
                
                stock_name = cols[0].text.strip().replace('#', '').strip()
                # Remove leading dash (MoneyControl uses - prefix for some stocks)
                stock_name = stock_name.lstrip('-').strip()
                
                sector = cols[1].text.strip() if len(cols) > 1 else 'Unknown'
                
                # Get weight from correct column based on layout
                if table_col_layout == "extended":
                    # Extended layout: % is in column 4
                    weight_text = cols[4].text.strip() if len(cols) > 4 else '0'
                else:
                    # Standard layout: % is in column 3
                    weight_text = cols[3].text.strip() if len(cols) > 3 else '0'
                
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
    
    def scrape_top_funds(self, limit=None, force=False):
        """
        Scrape funds with smart skip logic and progress tracking
        Args:
            limit: Max number of funds to scrape (None = all)
            force: If True, rescrape even if exists (default: False)
        """
        print("\n" + "="*80)
        print("MONEYCONTROL SCRAPER - 300+ FUNDS")
        print("="*80)
        
        # Check existing data
        existing = self.check_existing_data() if not force else set()
        
        # Filter funds to scrape
        funds_to_scrape = []
        for fund in self.all_funds:
            fund_key = fund['name'].lower().replace(' ', '-').replace('&', 'and')
            
            # Skip if exists (unless force=True)
            if not force and (fund_key in existing or fund['code'] in existing):
                continue
            
            funds_to_scrape.append(fund)
        
        if limit:
            funds_to_scrape = funds_to_scrape[:limit]
        
        print(f"\n Total available: {len(self.all_funds)} funds")
        print(f" Already scraped: {len(existing)} funds")
        print(f" To scrape now: {len(funds_to_scrape)} funds")
        print(f"\nStrategy: Skip existing, rate limit 2s, track progress\n")
        
        if not funds_to_scrape:
            print("[INFO] All funds already scraped! Use force=True to rescrape.")
            return {}
        
        # Update TODO: starting
        self.update_todo_file("Scraping in progress...", [])
        
        scraped_data = {}
        fund_results = []
        success = 0
        failed = 0
        
        for idx, fund in enumerate(funds_to_scrape, 1):
            fund_key = fund['name'].lower().replace(' ', '-').replace('&', 'and')
            
            print(f"\n[{idx}/{len(funds_to_scrape)}] ", end="")
            
            try:
                holdings = self.scrape_fund_holdings(fund['url'], fund['name'])
                
                if holdings and len(holdings) > 5:
                    # Extract AMC from fund name (before 'Fund')
                    amc = fund['name'].split(' Fund')[0].split()[-1] if 'Fund' in fund['name'] else 'Unknown'
                    
                    scraped_data[fund_key] = {
                        'name': fund['name'],
                        'amc': amc,
                        'category': fund['category'],
                        'holdings': holdings,
                        'holdings_count': len(holdings),
                        'as_of_date': datetime.now().strftime('%Y-%m-%d'),
                        'source': 'MoneyControl Scraping',
                        'fund_code': fund['code']
                    }
                    fund_results.append({
                        'name': fund['name'],
                        'holdings_count': len(holdings),
                        'success': True
                    })
                    success += 1
                else:
                    print(f"[FAIL] {fund['name']} - No valid holdings found")
                    self.failed_funds.append({
                        'name': fund['name'],
                        'code': fund['code'],
                        'error': 'No valid holdings found'
                    })
                    failed += 1
                    
            except Exception as e:
                print(f"[ERROR] {fund['name']}: {str(e)[:50]}")
                self.failed_funds.append({
                    'name': fund['name'],
                    'code': fund['code'],
                    'error': str(e)[:100]
                })
                failed += 1
            
            # Update TODO every 10 funds
            if idx % 10 == 0 or idx == len(funds_to_scrape):
                self.update_todo_file(f"Scraped {idx}/{len(funds_to_scrape)} funds", fund_results)
            
            time.sleep(2)  # Rate limiting
        
        # Final summary
        print("\n\n" + "="*80)
        print("SCRAPING SUMMARY")
        print("="*80)
        print(f"\n ✓ Successfully scraped: {success} funds")
        print(f" ✗ Failed: {failed} funds")
        if funds_to_scrape:
            print(f" Success rate: {(success / len(funds_to_scrape) * 100):.1f}%")
        
        if scraped_data:
            # Save to fund_holdings.json
            self.update_fund_holdings(scraped_data)
            print(f"\n Updated fund_holdings.json with {len(scraped_data)} new funds")
        
        # Final TODO update
        self.update_todo_file("Scraping completed!", fund_results)
        
        if self.failed_funds:
            print(f"\n⚠️  {len(self.failed_funds)} funds failed. Check scraping_todo.md for details.")
        
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
    """Run scraper with options"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Scrape mutual fund holdings from MoneyControl')
    parser.add_argument('--limit', type=int, default=None, help='Limit number of funds to scrape (default: all)')
    parser.add_argument('--force', action='store_true', help='Rescrape even if fund exists')
    parser.add_argument('--test', action='store_true', help='Test mode: scrape only 5 funds')
    
    args = parser.parse_args()
    
    scraper = MoneyControlScraper()
    
    if args.test:
        print("\n[TEST MODE] Scraping first 5 funds...\n")
        scraper.scrape_top_funds(limit=5, force=args.force)
    else:
        limit = args.limit
        if limit:
            print(f"\n[SCRAPING MODE] Up to {limit} funds\n")
        else:
            print("\n[FULL SCRAPING] All available funds\n")
        scraper.scrape_top_funds(limit=limit, force=args.force)
    
    print("\n" + "="*80)
    print("NEXT STEPS")
    print("="*80)
    print("1. Check progress: backend/scripts/scraping_todo.md")
    print("2. Validate data: python backend/scripts/validate_holdings.py")
    print("3. Load to DB: python backend/scripts/load_holdings_to_db.py")
    print("4. Verify DB: python backend/validate_funds_data.py")
    print("="*80 + "\n")


if __name__ == "__main__":
    main()
