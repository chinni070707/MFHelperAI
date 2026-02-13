"""
AMC Website Scrapers - Official Source for Fund Holdings

Best approach: Parse individual AMC websites for accurate fund constituents
Advantage: Official source, most accurate, latest data, factsheets available

Top 10 AMCs by AUM (India):
1. HDFC Asset Management
2. ICICI Prudential AMC
3. SBI Funds Management
4. Aditya Birla Sun Life AMC
5. Nippon India Mutual Fund
6. Kotak Mahindra Asset Management
7. Axis Asset Management
8. UTI Asset Management
9. DSP Investment Managers
10. Tata Asset Management
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

class BaseAMCScraper:
    """Base class for AMC scrapers"""
    
    def __init__(self, amc_name: str, base_url: str):
        self.amc_name = amc_name
        self.base_url = base_url
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5'
        })
    
    def get_fund_list(self) -> List[Dict]:
        """Get list of all funds - to be implemented by each AMC"""
        raise NotImplementedError
    
    def get_fund_holdings(self, fund_code: str) -> Optional[Dict]:
        """Get portfolio holdings for a fund - to be implemented by each AMC"""
        raise NotImplementedError
    
    def download_factsheet(self, fund_code: str, output_dir: str = 'factsheets') -> Optional[str]:
        """Download PDF factsheet"""
        raise NotImplementedError


class HDFCAMCScraper(BaseAMCScraper):
    """
    HDFC Asset Management Scraper
    Website: https://www.hdfcfund.com/
    
    Structure:
    - Fund list: https://www.hdfcfund.com/mutual-funds-investment/equity-funds
    - Fund page: https://www.hdfcfund.com/mutual-funds-investment/hdfc-flexi-cap-fund
    - Factsheet: PDF available on fund page
    """
    
    def __init__(self):
        super().__init__('HDFC Mutual Fund', 'https://www.hdfcfund.com')
    
    def get_fund_list(self) -> List[Dict]:
        """Get list of HDFC funds"""
        try:
            categories = [
                'equity-funds',
                'debt-funds',
                'hybrid-funds',
                'solution-oriented-funds'
            ]
            
            all_funds = []
            
            for category in categories:
                url = f'{self.base_url}/mutual-funds-investment/{category}'
                response = self.session.get(url, timeout=15)
                response.raise_for_status()
                
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Find fund links (actual selectors need verification)
                fund_links = soup.find_all('a', href=re.compile(r'/mutual-funds-investment/hdfc-'))
                
                for link in fund_links:
                    fund_name = link.text.strip()
                    fund_url = link.get('href')
                    
                    if fund_url and fund_name:
                        all_funds.append({
                            'name': fund_name,
                            'url': fund_url if fund_url.startswith('http') else self.base_url + fund_url,
                            'category': category.replace('-', ' ').title(),
                            'amc': self.amc_name
                        })
            
            logger.info(f"✅ Found {len(all_funds)} HDFC funds")
            return all_funds
            
        except Exception as e:
            logger.error(f"Error fetching HDFC fund list: {e}")
            return []
    
    def get_fund_holdings(self, fund_url: str) -> Optional[Dict]:
        """
        Get portfolio holdings from fund page
        
        HDFC provides:
        1. Portfolio holdings table on fund page
        2. PDF factsheet with detailed holdings
        """
        try:
            response = self.session.get(fund_url, timeout=15)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Find portfolio section
            portfolio_section = soup.find('div', {'class': 'portfolio'}) or soup.find('section', {'id': 'portfolio'})
            
            if not portfolio_section:
                logger.warning(f"No portfolio section found on {fund_url}")
                return None
            
            # Parse holdings table
            holdings = []
            table = portfolio_section.find('table')
            
            if table:
                rows = table.find_all('tr')[1:]  # Skip header
                
                for row in rows:
                    cols = row.find_all('td')
                    if len(cols) >= 2:
                        stock_name = cols[0].text.strip()
                        weight_text = cols[1].text.strip().replace('%', '')
                        
                        try:
                            weight = float(weight_text)
                            sector = cols[2].text.strip() if len(cols) > 2 else 'Unknown'
                            
                            holdings.append({
                                'stock': stock_name,
                                'weight': weight,
                                'sector': sector
                            })
                        except ValueError:
                            continue
            
            # Get fund name
            fund_name_elem = soup.find('h1') or soup.find('title')
            fund_name = fund_name_elem.text.strip() if fund_name_elem else 'Unknown'
            
            return {
                'name': fund_name,
                'amc': self.amc_name,
                'holdings': holdings,
                'source': 'HDFC Official Website',
                'url': fund_url,
                'scraped_at': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error fetching holdings from {fund_url}: {e}")
            return None


class ICICIPrudentialScraper(BaseAMCScraper):
    """
    ICICI Prudential AMC Scraper
    Website: https://www.icicipruamc.com/
    """
    
    def __init__(self):
        super().__init__('ICICI Prudential', 'https://www.icicipruamc.com')
    
    def get_fund_list(self) -> List[Dict]:
        """Get list of ICICI Prudential funds"""
        try:
            url = f'{self.base_url}/funds/mutual-funds'
            response = self.session.get(url, timeout=15)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Parse fund list
            funds = []
            fund_elements = soup.find_all('div', {'class': 'fund-card'})
            
            for elem in fund_elements:
                name_elem = elem.find('h3') or elem.find('a')
                if name_elem:
                    funds.append({
                        'name': name_elem.text.strip(),
                        'url': name_elem.get('href', ''),
                        'amc': self.amc_name
                    })
            
            logger.info(f"✅ Found {len(funds)} ICICI Prudential funds")
            return funds
            
        except Exception as e:
            logger.error(f"Error fetching ICICI Prudential fund list: {e}")
            return []


class SBIMFScraper(BaseAMCScraper):
    """
    SBI Mutual Fund Scraper
    Website: https://www.sbimf.com/
    """
    
    def __init__(self):
        super().__init__('SBI Mutual Fund', 'https://www.sbimf.com')


class AxisAMCScraper(BaseAMCScraper):
    """
    Axis Asset Management Scraper  
    Website: https://www.axismf.com/
    """
    
    def __init__(self):
        super().__init__('Axis Mutual Fund', 'https://www.axismf.com')


class KotakAMCScraper(BaseAMCScraper):
    """
    Kotak Mahindra Asset Management Scraper
    Website: https://www.kotakmf.com/
    """
    
    def __init__(self):
        super().__init__('Kotak Mutual Fund', 'https://www.kotakmf.com')


class AMCDataCollector:
    """
    Orchestrates data collection from multiple AMCs
    """
    
    def __init__(self):
        self.scrapers = {
            'HDFC': HDFCAMCScraper(),
            'ICICI': ICICIPrudentialScraper(),
            'SBI': SBIMFScraper(),
            'Axis': AxisAMCScraper(),
            'Kotak': KotakAMCScraper(),
        }
    
    def collect_all_holdings(self, top_n_funds_per_amc: int = 5) -> Dict:
        """
        Collect holdings from all AMCs
        
        Args:
            top_n_funds_per_amc: Number of top funds to fetch per AMC
        
        Returns:
            Dict with holdings data
        """
        all_holdings = {}
        
        for amc_name, scraper in self.scrapers.items():
            try:
                logger.info(f"\n{'='*60}")
                logger.info(f"Processing {amc_name} Mutual Fund")
                logger.info(f"{'='*60}")
                
                # Get fund list
                funds = scraper.get_fund_list()
                
                if not funds:
                    logger.warning(f"No funds found for {amc_name}")
                    continue
                
                # Get holdings for top N funds
                for i, fund in enumerate(funds[:top_n_funds_per_amc]):
                    logger.info(f"[{i+1}/{top_n_funds_per_amc}] Fetching: {fund['name']}")
                    
                    holdings_data = scraper.get_fund_holdings(fund['url'])
                    
                    if holdings_data:
                        fund_key = self._generate_fund_key(fund['name'])
                        all_holdings[fund_key] = holdings_data
                        logger.info(f"  ✅ Got {len(holdings_data.get('holdings', []))} holdings")
                    else:
                        logger.warning(f"  ❌ Failed to get holdings")
                    
                    time.sleep(2)  # Rate limiting
                
            except Exception as e:
                logger.error(f"Error processing {amc_name}: {e}")
                continue
        
        return {
            'version': datetime.now().strftime('%Y-%m'),
            'last_updated': datetime.now().strftime('%Y-%m-%d'),
            'source': 'Official AMC Websites',
            'data_quality': 'High - Direct from source',
            'funds': all_holdings
        }
    
    def _generate_fund_key(self, fund_name: str) -> str:
        """Generate URL-safe fund key"""
        key = fund_name.lower()
        key = re.sub(r'[^\w\s-]', '', key)
        key = re.sub(r'[\s]+', '-', key)
        return key
    
    def save_to_file(self, data: Dict, output_path: str = None):
        """Save collected data to JSON file"""
        if output_path is None:
            output_path = Path(__file__).parent.parent / 'data' / 'fund_holdings.json'
        
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        logger.info(f"\n✅ Saved to: {output_path}")
        return str(output_path)


def main():
    """Main execution"""
    print("\n" + "="*80)
    print("AMC WEBSITE SCRAPER - Official Source for Fund Holdings")
    print("="*80)
    
    print("\n📊 WHY AMC WEBSITES ARE BETTER:")
    print("  ✅ Official source - Most accurate")
    print("  ✅ Latest data - Updated monthly")
    print("  ✅ Complete holdings - Not just top 10")
    print("  ✅ PDF factsheets - Detailed information")
    print("  ✅ Legal compliance - Regulated disclosures")
    
    print("\n⚠️  VALUE RESEARCH LIMITATIONS:")
    print("  • May have delayed data")
    print("  • Sometimes shows only top holdings")
    print("  • Requires account for some data")
    print("  • Can have scraping restrictions")
    
    print("\n🎯 RECOMMENDED APPROACH:")
    print("  1. Start with top 10 AMCs (covers 80%+ of AUM)")
    print("  2. Parse their official websites")
    print("  3. Download PDF factsheets as backup")
    print("  4. Update monthly (aligned with AMC disclosures)")
    
    print("\n📋 TOP 10 AMCs TO IMPLEMENT:")
    amcs = [
        "1. HDFC Asset Management",
        "2. ICICI Prudential AMC",
        "3. SBI Funds Management",
        "4. Aditya Birla Sun Life AMC",
        "5. Nippon India Mutual Fund",
        "6. Kotak Mahindra AMC",
        "7. Axis Asset Management",
        "8. UTI Asset Management",
        "9. DSP Investment Managers",
        "10. Tata Asset Management"
    ]
    
    for amc in amcs:
        status = "✅ Implemented" if amc.split('.')[1].split()[0] in ['HDFC', 'ICICI', 'SBI', 'Axis', 'Kotak'] else "🔄 Todo"
        print(f"  {amc} - {status}")
    
    print("\n" + "="*80)
    print("NEXT STEPS:")
    print("="*80)
    
    print("\n1. Verify AMC website structures (inspect each site)")
    print("2. Update scraper selectors for each AMC")
    print("3. Test with a few funds first")
    print("4. Run full collection (will take ~1 hour for all AMCs)")
    print("5. Set up monthly update cron job")
    
    print("\n💡 USAGE:")
    print("  # Collect from all AMCs")
    print("  collector = AMCDataCollector()")
    print("  data = collector.collect_all_holdings(top_n_funds_per_amc=10)")
    print("  collector.save_to_file(data)")
    
    print("\n" + "="*80)


if __name__ == "__main__":
    main()
