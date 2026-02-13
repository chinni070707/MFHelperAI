"""
Targeted Portfolio Scraper - HDFC, Axis, Parag Parikh Top Funds

Focus on getting real holdings for top funds from these 3 popular AMCs:
1. HDFC Mutual Fund - Top 5 funds
2. Axis Mutual Fund - Top 5 funds  
3. Parag Parikh (PPFAS) - Top 3 funds

These AMCs are popular for their consistent performance and good portfolio disclosure.
"""
import requests
from bs4 import BeautifulSoup
import json
from pathlib import Path
from datetime import datetime
import time

class TargetedAMCScraper:
    """Scrape holdings from HDFC, Axis, and Parag Parikh"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        
        # Top funds to focus on
        self.target_funds = {
            'HDFC': [
                {'name': 'HDFC Flexi Cap Fund', 'url': 'hdfc-flexi-cap-fund'},
                {'name': 'HDFC Top 100 Fund', 'url': 'hdfc-top-100-fund'},
                {'name': 'HDFC Mid Cap Opportunities Fund', 'url': 'hdfc-mid-cap-opportunities-fund'},
                {'name': 'HDFC Small Cap Fund', 'url': 'hdfc-small-cap-fund'},
                {'name': 'HDFC Balanced Advantage Fund', 'url': 'hdfc-balanced-advantage-fund'},
            ],
            'Axis': [
                {'name': 'Axis Bluechip Fund', 'url': 'axis-bluechip-fund'},
                {'name': 'Axis Midcap Fund', 'url': 'axis-midcap-fund'},
                {'name': 'Axis Small Cap Fund', 'url': 'axis-small-cap-fund'},
                {'name': 'Axis Focused 25 Fund', 'url': 'axis-focused-25-fund'},
                {'name': 'Axis Long Term Equity Fund', 'url': 'axis-long-term-equity-fund'},
            ],
            'Parag Parikh': [
                {'name': 'Parag Parikh Flexi Cap Fund', 'url': 'parag-parikh-flexi-cap-fund'},
                {'name': 'Parag Parikh Tax Saver Fund', 'url': 'parag-parikh-tax-saver-fund'},
                {'name': 'Parag Parikh Arbitrage Fund', 'url': 'parag-parikh-arbitrage-fund'},
            ]
        }
    
    def test_hdfc_portfolio_page(self):
        """Test accessing HDFC portfolio page"""
        print("\n" + "="*80)
        print("TESTING HDFC MUTUAL FUND PORTFOLIO ACCESS")
        print("="*80)
        
        # HDFC portfolio disclosure URL
        url = 'https://www.hdfcfund.com/statutory-disclosure/portfolio/fortnightly-portfolio'
        
        print(f"\nFetching: {url}")
        
        try:
            response = self.session.get(url, timeout=30)
            print(f"Status: {response.status_code}")
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Look for Excel/PDF download links
                links = soup.find_all('a', href=True)
                
                portfolio_files = []
                for link in links:
                    href = link.get('href', '')
                    text = link.text.strip()
                    
                    if any(ext in href.lower() for ext in ['.xlsx', '.xls', '.pdf']):
                        portfolio_files.append({
                            'text': text[:80],
                            'url': href if href.startswith('http') else 'https://www.hdfcfund.com' + href
                        })
                
                print(f"\n[OK] Found {len(portfolio_files)} portfolio files")
                
                for i, file in enumerate(portfolio_files[:5], 1):
                    print(f"\n{i}. {file['text']}")
                    print(f"   URL: {file['url'][:100]}...")
                
                return portfolio_files
            else:
                print(f"[ERROR] Could not access page: {response.status_code}")
                return []
                
        except Exception as e:
            print(f"[ERROR] {e}")
            return []
    
    def test_axis_portfolio_page(self):
        """Test accessing Axis portfolio page"""
        print("\n" + "="*80)
        print("TESTING AXIS MUTUAL FUND PORTFOLIO ACCESS")
        print("="*80)
        
        url = 'https://www.axismf.com/statutory-disclosures'
        
        print(f"\nFetching: {url}")
        
        try:
            response = self.session.get(url, timeout=30)
            print(f"Status: {response.status_code}")
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Look for portfolio section
                links = soup.find_all('a', href=True)
                
                portfolio_files = []
                for link in links:
                    href = link.get('href', '')
                    text = link.text.strip()
                    
                    if 'portfolio' in text.lower() or 'portfolio' in href.lower():
                        if any(ext in href.lower() for ext in ['.xlsx', '.xls', '.pdf']):
                            portfolio_files.append({
                                'text': text[:80],
                                'url': href if href.startswith('http') else 'https://www.axismf.com' + href
                            })
                
                print(f"\n[OK] Found {len(portfolio_files)} portfolio files")
                
                for i, file in enumerate(portfolio_files[:5], 1):
                    print(f"\n{i}. {file['text']}")
                    print(f"   URL: {file['url'][:100]}...")
                
                return portfolio_files
            else:
                print(f"[ERROR] Could not access page: {response.status_code}")
                return []
                
        except Exception as e:
            print(f"[ERROR] {e}")
            return []
    
    def test_ppfas_portfolio_page(self):
        """Test accessing Parag Parikh (PPFAS) portfolio page"""
        print("\n" + "="*80)
        print("TESTING PARAG PARIKH (PPFAS) PORTFOLIO ACCESS")
        print("="*80)
        
        url = 'https://amc.ppfas.com/downloads/portfolio-disclosure'
        
        print(f"\nFetching: {url}")
        
        try:
            response = self.session.get(url, timeout=30)
            print(f"Status: {response.status_code}")
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                
                links = soup.find_all('a', href=True)
                
                portfolio_files = []
                for link in links:
                    href = link.get('href', '')
                    text = link.text.strip()
                    
                    if any(ext in href.lower() for ext in ['.xlsx', '.xls', '.pdf']):
                        portfolio_files.append({
                            'text': text[:80],
                            'url': href if href.startswith('http') else 'https://amc.ppfas.com' + href
                        })
                
                print(f"\n[OK] Found {len(portfolio_files)} portfolio files")
                
                for i, file in enumerate(portfolio_files[:5], 1):
                    print(f"\n{i}. {file['text']}")
                    print(f"   URL: {file['url'][:100]}...")
                
                return portfolio_files
            else:
                print(f"[ERROR] Could not access page: {response.status_code}")
                return []
                
        except Exception as e:
            print(f"[ERROR] {e}")
            return []
    
    def test_all_amc_pages(self):
        """Test all 3 AMC portfolio pages"""
        print("\n" + "="*80)
        print("PHASE 2: TESTING AMC PORTFOLIO PAGE ACCESS")
        print("="*80)
        print("\nTesting access to portfolio pages for:")
        print("  1. HDFC Mutual Fund")
        print("  2. Axis Mutual Fund")
        print("  3. Parag Parikh (PPFAS)")
        print("\nThis will help us understand:")
        print("  - How to download portfolio files")
        print("  - What format they're in (Excel/PDF)")
        print("  - How to parse holdings data")
        
        results = {}
        
        # Test HDFC
        hdfc_files = self.test_hdfc_portfolio_page()
        results['HDFC'] = {
            'success': len(hdfc_files) > 0,
            'files_found': len(hdfc_files),
            'files': hdfc_files[:3]
        }
        time.sleep(2)
        
        # Test Axis
        axis_files = self.test_axis_portfolio_page()
        results['Axis'] = {
            'success': len(axis_files) > 0,
            'files_found': len(axis_files),
            'files': axis_files[:3]
        }
        time.sleep(2)
        
        # Test Parag Parikh
        ppfas_files = self.test_ppfas_portfolio_page()
        results['Parag Parikh'] = {
            'success': len(ppfas_files) > 0,
            'files_found': len(ppfas_files),
            'files': ppfas_files[:3]
        }
        
        # Summary
        print("\n" + "="*80)
        print("SUMMARY")
        print("="*80)
        
        for amc, result in results.items():
            status = "[OK]" if result['success'] else "[FAIL]"
            print(f"\n{status} {amc}: {result['files_found']} portfolio files found")
        
        # Save results
        output_file = Path(__file__).parent.parent / 'data' / 'amc_portfolio_test_results.json'
        output_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_file, 'w') as f:
            json.dump({
                'test_date': datetime.now().isoformat(),
                'results': results
            }, f, indent=2)
        
        print(f"\n[OK] Test results saved to: {output_file}")
        
        return results


def main():
    """Run targeted portfolio scraper tests"""
    
    print("\n" + "="*80)
    print("TARGETED PORTFOLIO SCRAPER - PHASE 2")
    print("="*80)
    print("\nFocus: Top funds from 3 popular AMCs")
    print("  - HDFC Mutual Fund (5 top funds)")
    print("  - Axis Mutual Fund (5 top funds)")
    print("  - Parag Parikh PPFAS (3 funds)")
    print("\nTotal: ~13 funds to start with")
    
    scraper = TargetedAMCScraper()
    
    print("\n[STEP 1] Testing AMC portfolio page access...")
    results = scraper.test_all_amc_pages()
    
    print("\n" + "="*80)
    print("NEXT STEPS:")
    print("="*80)
    
    success_count = sum(1 for r in results.values() if r['success'])
    
    if success_count == 3:
        print("\n[OK] All 3 AMC portfolio pages accessible!")
        print("\nNext:")
        print("  1. Download the Excel/PDF files")
        print("  2. Parse holdings data (stock names, weights, sectors)")
        print("  3. Generate fund_holdings.json")
        print("  4. Test with your overlap analysis")
    elif success_count > 0:
        print(f"\n[OK] {success_count}/3 AMC pages accessible")
        print("\nWe can proceed with the accessible ones.")
        print("The others may need:")
        print("  - Different URL structure")
        print("  - JavaScript rendering (Selenium)")
        print("  - Manual factsheet download")
    else:
        print("\n[WARNING] Could not access AMC portfolio pages")
        print("\nAlternative approaches:")
        print("  1. Use Selenium for JavaScript-heavy pages")
        print("  2. Manually download a few factsheets to start")
        print("  3. Focus on Value Research as backup")
    
    print("\n" + "="*80)


if __name__ == "__main__":
    main()
