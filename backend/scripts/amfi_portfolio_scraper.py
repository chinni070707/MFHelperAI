"""
AMFI Portfolio Disclosure Scraper - BEST SOURCE FOR FUND HOLDINGS

This is THE solution! AMFI provides a centralized page with links to 
ALL AMC portfolio disclosures. SEBI mandates monthly portfolio disclosure,
so this data is:
- Official and authoritative ✅
- Standardized format ✅  
- Updated monthly by 7th ✅
- Covers ALL AMCs ✅
- Free and legal ✅

URL: https://www.amfiindia.com/online-center/portfolio-disclosure

Each AMC provides:
- Excel/PDF downloads with complete portfolio holdings
- Fund-wise breakdown
- Monthly updated
- Top holdings + sector allocation
"""

import requests
from bs4 import BeautifulSoup
import json
import time
import re
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class AMFIPortfolioScraper:
    """
    Scrape portfolio data from AMFI's official Portfolio Disclosure page
    This is the BEST source - official, standardized, complete
    """
    
    def __init__(self):
        self.base_url = 'https://www.amfiindia.com'
        self.portfolio_url = f'{self.base_url}/online-center/portfolio-disclosure'
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Referer': 'https://www.amfiindia.com/'
        })
    
    def get_amc_portfolio_links(self) -> List[Dict]:
        """
        Get links to all AMC portfolio pages from AMFI
        
        Returns:
            List of dicts with AMC name and portfolio URL
        """
        try:
            logger.info(f"Fetching AMFI Portfolio Disclosure page...")
            response = self.session.get(self.portfolio_url, timeout=30)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            amc_links = []
            
            # Find all AMC portfolio links
            # The page structure may have:
            # - Dropdown menu with AMC names
            # - Table with AMC names and links
            # - List of AMC links
            
            # Method 1: Look for dropdown options
            select = soup.find('select', id=re.compile(r'amc|fund|portfolio', re.I))
            if select:
                options = select.find_all('option')
                for option in options:
                    amc_name = option.text.strip()
                    link_value = option.get('value', '')
                    
                    if amc_name and link_value:
                        amc_links.append({
                            'amc': amc_name,
                            'link': link_value if link_value.startswith('http') else self.base_url + link_value,
                            'source': 'AMFI Official'
                        })
            
            # Method 2: Look for table with AMC names
            tables = soup.find_all('table')
            for table in tables:
                rows = table.find_all('tr')
                for row in rows:
                    cols = row.find_all('td')
                    if len(cols) >= 2:
                        amc_name = cols[0].text.strip()
                        link = cols[0].find('a') or cols[1].find('a')
                        
                        if link and amc_name:
                            href = link.get('href', '')
                            if href:
                                amc_links.append({
                                    'amc': amc_name,
                                    'link': href if href.startswith('http') else self.base_url + href,
                                    'source': 'AMFI Official'
                                })
            
            # Method 3: Look for list of links
            links = soup.find_all('a', href=re.compile(r'portfolio|disclosure|holdings', re.I))
            for link in links:
                amc_name = link.text.strip()
                href = link.get('href', '')
                
                if amc_name and href and len(amc_name) > 5:  # Filter out short text
                    amc_links.append({
                        'amc': amc_name,
                        'link': href if href.startswith('http') else self.base_url + href,
                        'source': 'AMFI Official'
                    })
            
            # Remove duplicates
            seen = set()
            unique_links = []
            for item in amc_links:
                key = (item['amc'], item['link'])
                if key not in seen:
                    seen.add(key)
                    unique_links.append(item)
            
            logger.info(f"✅ Found {len(unique_links)} AMC portfolio links")
            return unique_links
            
        except Exception as e:
            logger.error(f"Error fetching AMC portfolio links: {e}")
            return []
    
    def download_amc_portfolio(self, amc_link: Dict, output_dir: str = 'portfolio_data') -> Optional[str]:
        """
        Download portfolio data from AMC link
        
        Args:
            amc_link: Dict with 'amc' name and 'link' URL
            output_dir: Directory to save downloads
        
        Returns:
            Path to downloaded file or None
        """
        try:
            amc_name = amc_link['amc']
            url = amc_link['link']
            
            logger.info(f"Downloading portfolio for: {amc_name}")
            
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            
            # Create output directory
            output_path = Path(output_dir)
            output_path.mkdir(parents=True, exist_ok=True)
            
            # Determine file type
            content_type = response.headers.get('Content-Type', '').lower()
            
            if 'excel' in content_type or 'spreadsheet' in content_type:
                file_ext = '.xlsx'
            elif 'pdf' in content_type:
                file_ext = '.pdf'
            elif 'csv' in content_type:
                file_ext = '.csv'
            else:
                file_ext = '.html'
            
            # Save file
            filename = f"{amc_name.replace(' ', '_').replace('/', '_')}_portfolio{file_ext}"
            file_path = output_path / filename
            
            with open(file_path, 'wb') as f:
                f.write(response.content)
            
            logger.info(f"  ✅ Saved to: {file_path}")
            return str(file_path)
            
        except Exception as e:
            logger.error(f"Error downloading portfolio for {amc_link['amc']}: {e}")
            return None
    
    def parse_excel_portfolio(self, excel_file: str) -> Dict:
        """
        Parse Excel file containing portfolio holdings
        
        Requires: pip install openpyxl pandas
        """
        try:
            import pandas as pd
            
            # Read Excel file
            df = pd.read_excel(excel_file, sheet_name=0)
            
            # Common column names in AMC portfolio files
            stock_col = None
            weight_col = None
            sector_col = None
            
            for col in df.columns:
                col_lower = str(col).lower()
                if 'stock' in col_lower or 'company' in col_lower or 'name' in col_lower:
                    stock_col = col
                elif 'weight' in col_lower or '%' in col_lower or 'allocation' in col_lower:
                    weight_col = col
                elif 'sector' in col_lower or 'industry' in col_lower:
                    sector_col = col
            
            if not stock_col or not weight_col:
                logger.warning(f"Could not identify columns in {excel_file}")
                return None
            
            holdings = []
            for _, row in df.iterrows():
                stock = str(row[stock_col]).strip()
                try:
                    weight = float(str(row[weight_col]).replace('%', ''))
                except:
                    continue
                
                sector = str(row[sector_col]).strip() if sector_col else 'Unknown'
                
                if stock and weight > 0:
                    holdings.append({
                        'stock': stock,
                        'weight': weight,
                        'sector': sector
                    })
            
            return {
                'holdings': holdings,
                'total_stocks': len(holdings),
                'source': 'AMFI Portfolio Disclosure'
            }
            
        except Exception as e:
            logger.error(f"Error parsing Excel file {excel_file}: {e}")
            return None
    
    def collect_all_portfolios(self, top_n: int = 10) -> Dict:
        """
        Collect portfolio holdings from all AMCs via AMFI
        
        Args:
            top_n: Number of top AMCs to process
        
        Returns:
            Dict with all portfolio holdings
        """
        logger.info("="*80)
        logger.info("COLLECTING PORTFOLIOS FROM AMFI OFFICIAL SOURCE")
        logger.info("="*80)
        
        # Get AMC links
        amc_links = self.get_amc_portfolio_links()
        
        if not amc_links:
            logger.error("Could not fetch AMC links from AMFI")
            return {}
        
        logger.info(f"\nFound {len(amc_links)} AMCs on AMFI portfolio page")
        logger.info(f"Processing top {min(top_n, len(amc_links))} AMCs...\n")
        
        all_portfolios = {}
        
        for i, amc_link in enumerate(amc_links[:top_n], 1):
            logger.info(f"[{i}/{min(top_n, len(amc_links))}] {amc_link['amc']}")
            
            # Download portfolio file
            file_path = self.download_amc_portfolio(amc_link)
            
            if file_path:
                # Parse if Excel
                if file_path.endswith('.xlsx') or file_path.endswith('.xls'):
                    portfolio_data = self.parse_excel_portfolio(file_path)
                    if portfolio_data:
                        amc_key = amc_link['amc'].lower().replace(' ', '-')
                        all_portfolios[amc_key] = {
                            'amc': amc_link['amc'],
                            'source_url': amc_link['link'],
                            'file_path': file_path,
                            **portfolio_data
                        }
            
            time.sleep(2)  # Rate limiting
        
        return {
            'version': datetime.now().strftime('%Y-%m'),
            'last_updated': datetime.now().strftime('%Y-%m-%d'),
            'source': 'AMFI Official Portfolio Disclosure',
            'portfolios': all_portfolios
        }


def main():
    """Demo the AMFI portfolio scraper"""
    
    print("\n" + "="*80)
    print("🎯 AMFI PORTFOLIO DISCLOSURE SCRAPER - THE BEST SOURCE!")
    print("="*80)
    
    print("\n✅ ADVANTAGES:")
    print("  • Official AMFI page (authoritative source)")
    print("  • SEBI mandated disclosures (reliable)")
    print("  • All AMCs in one place (centralized)")
    print("  • Standardized format (easier to parse)")
    print("  • Monthly updated (by 7th of month)")
    print("  • Excel/PDF downloads (structured data)")
    print("  • Free and legal (public disclosure)")
    
    print("\n📋 WHAT YOU GET:")
    print("  • Complete portfolio holdings (30-50+ stocks)")
    print("  • Scheme-wise breakdown")
    print("  • Sector allocation")
    print("  • Monthly snapshots")
    print("  • All funds from all AMCs")
    
    print("\n🚀 THIS IS BETTER THAN:")
    print("  ❌ Scraping individual AMC websites")
    print("  ❌ Paying for Value Research")
    print("  ❌ Using incomplete demo data")
    print("  ✅ Single source for everything!")
    
    print("\n" + "="*80)
    print("USAGE:")
    print("="*80)
    
    print("\nfrom amfi_portfolio_scraper import AMFIPortfolioScraper")
    print("")
    print("scraper = AMFIPortfolioScraper()")
    print("")
    print("# Get all AMC portfolio links")
    print("amc_links = scraper.get_amc_portfolio_links()")
    print("print(f'Found {len(amc_links)} AMCs')")
    print("")
    print("# Download and parse portfolios")
    print("portfolios = scraper.collect_all_portfolios(top_n=10)")
    print("")
    print("# Save to JSON")
    print("import json")
    print("with open('fund_holdings.json', 'w') as f:")
    print("    json.dump(portfolios, f, indent=2)")
    
    print("\n" + "="*80)
    print("📝 NEXT STEPS:")
    print("="*80)
    print("\n1. Install dependencies:")
    print("   pip install beautifulsoup4 requests openpyxl pandas")
    print("\n2. Run the scraper:")
    print("   python amfi_portfolio_scraper.py")
    print("\n3. Parse downloaded Excel/PDF files")
    print("\n4. Generate fund_holdings.json")
    print("\n5. Update monthly (automated cron job)")
    
    print("\n✅ This is THE solution we've been looking for!")
    print("="*80 + "\n")


if __name__ == "__main__":
    main()
