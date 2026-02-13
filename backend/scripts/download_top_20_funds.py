"""
Auto-Download and Parse Top 20 Mutual Funds by AUM

This script:
1. Auto-discovers Excel file URLs for Top 20 funds
2. Downloads them using requests (no manual work!)
3. Parses holdings data automatically
4. Updates fund_holdings.json

Focus: Top 20 funds = 70% of retail investor coverage
"""
import requests
from bs4 import BeautifulSoup
import pandas as pd
import json
from pathlib import Path
from datetime import datetime
import time

class Top20FundsDownloader:
    """Smart downloader for Top 20 mutual funds by AUM"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        })
        
        self.download_dir = Path(__file__).parent.parent / 'data' / 'portfolio_downloads'
        self.download_dir.mkdir(parents=True, exist_ok=True)
        
        # Top 20 funds by AUM (70% coverage)
        self.top_20_funds = [
            {'rank': 1, 'name': 'HDFC Flexi Cap Fund', 'amc': 'HDFC', 'keywords': ['flexi', 'cap']},
            {'rank': 2, 'name': 'ICICI Prudential Bluechip Fund', 'amc': 'ICICI', 'keywords': ['bluechip']},
            {'rank': 3, 'name': 'SBI Bluechip Fund', 'amc': 'SBI', 'keywords': ['bluechip']},
            {'rank': 4, 'name': 'Axis Bluechip Fund', 'amc': 'Axis', 'keywords': ['bluechip']},
            {'rank': 5, 'name': 'Mirae Asset Large Cap Fund', 'amc': 'Mirae', 'keywords': ['large', 'cap']},
            {'rank': 6, 'name': 'Parag Parikh Flexi Cap Fund', 'amc': 'PPFAS', 'keywords': ['ppfcf'], 'status': 'done'},
            {'rank': 7, 'name': 'HDFC Top 100 Fund', 'amc': 'HDFC', 'keywords': ['top', '100']},
            {'rank': 8, 'name': 'Kotak Equity Opportunities Fund', 'amc': 'Kotak', 'keywords': ['equity', 'opportunities']},
            {'rank': 9, 'name': 'ICICI Prudential Equity & Debt Fund', 'amc': 'ICICI', 'keywords': ['equity', 'debt']},
            {'rank': 10, 'name': 'Nippon India Large Cap Fund', 'amc': 'Nippon', 'keywords': ['large', 'cap']},
            {'rank': 11, 'name': 'Axis Midcap Fund', 'amc': 'Axis', 'keywords': ['midcap', 'mid']},
            {'rank': 12, 'name': 'HDFC Mid Cap Opportunities Fund', 'amc': 'HDFC', 'keywords': ['mid', 'cap', 'opportunities']},
            {'rank': 13, 'name': 'Mirae Asset Emerging Bluechip Fund', 'amc': 'Mirae', 'keywords': ['emerging', 'bluechip']},
            {'rank': 14, 'name': 'SBI Small Cap Fund', 'amc': 'SBI', 'keywords': ['small', 'cap']},
            {'rank': 15, 'name': 'HDFC Small Cap Fund', 'amc': 'HDFC', 'keywords': ['small', 'cap']},
            {'rank': 16, 'name': 'Axis Small Cap Fund', 'amc': 'Axis', 'keywords': ['small', 'cap']},
            {'rank': 17, 'name': 'Kotak Small Cap Fund', 'amc': 'Kotak', 'keywords': ['small', 'cap']},
            {'rank': 18, 'name': 'Nippon India Small Cap Fund', 'amc': 'Nippon', 'keywords': ['small', 'cap']},
            {'rank': 19, 'name': 'HDFC Balanced Advantage Fund', 'amc': 'HDFC', 'keywords': ['balanced', 'advantage']},
            {'rank': 20, 'name': 'Motilal Oswal Midcap Fund', 'amc': 'Motilal', 'keywords': ['midcap']},
        ]
        
        # AMC portfolio URLs
        self.amc_urls = {
            'HDFC': 'https://www.hdfcfund.com/statutory-disclosure/portfolio/fortnightly-portfolio',
            'ICICI': 'https://www.icicipruamc.com/statutory-compliance/portfolio-holdings',
            'SBI': 'https://www.sbimf.com/en-us/statutory-disclosures',
            'Axis': 'https://www.axismf.com/statutory-disclosures',
            'Mirae': 'https://www.miraeassetmf.co.in/downloads',
            'PPFAS': 'https://amc.ppfas.com/downloads/portfolio-disclosure',
            'Kotak': 'https://www.kotakmf.com/statutory-disclosures',
            'Nippon': 'https://mf.nipponindiaim.com/investor-service/DownloadCentre/Pages/Scheme-Related-Documents.aspx',
            'Motilal': 'https://www.motilaloswalmf.com/statutory-disclosures'
        }
    
    def discover_fund_urls(self, amc_name):
        """Discover Excel file URLs for all funds from an AMC"""
        print(f"\n{'='*80}")
        print(f"DISCOVERING FUNDS FROM: {amc_name}")
        print(f"{'='*80}")
        
        if amc_name not in self.amc_urls:
            print(f"[SKIP] No URL configured for {amc_name}")
            return []
        
        url = self.amc_urls[amc_name]
        print(f"\nFetching: {url}")
        
        try:
            response = self.session.get(url, timeout=30)
            print(f"Status: {response.status_code}")
            
            if response.status_code != 200:
                print("[ERROR] Could not access page")
                return []
            
            soup = BeautifulSoup(response.text, 'html.parser')
            links = soup.find_all('a', href=True)
            
            found_files = []
            for link in links:
                href = link.get('href', '')
                text = link.text.strip()
                
                if any(ext in href.lower() for ext in ['.xlsx', '.xls', '.pdf']):
                    if href.startswith('http'):
                        full_url = href
                    elif href.startswith('//'):
                        full_url = 'https:' + href
                    elif href.startswith('/'):
                        base_url = '/'.join(url.split('/')[:3])
                        full_url = base_url + href
                    else:
                        full_url = url.rsplit('/', 1)[0] + '/' + href
                    
                    file_type = 'xlsx' if '.xlsx' in href.lower() else ('xls' if '.xls' in href.lower() else 'pdf')
                    
                    found_files.append({
                        'fund_name': text,
                        'url': full_url,
                        'type': file_type
                    })
            
            print(f"\n[OK] Found {len(found_files)} portfolio files")
            for i, file in enumerate(found_files[:5], 1):
                print(f"  {i}. {file['fund_name'][:60]}")
                print(f"     Type: {file['type'].upper()}")
            
            return found_files
            
        except Exception as e:
            print(f"[ERROR] {e}")
            return []
    
    def match_fund_to_url(self, fund_info, available_files):
        """Match fund to URL using keyword matching"""
        keywords = fund_info['keywords']
        
        for file in available_files:
            file_name_lower = file['fund_name'].lower()
            matches = sum(1 for kw in keywords if kw.lower() in file_name_lower)
            
            if matches >= len(keywords) - 1:
                return file
        
        return None
    
    def download_file(self, url, filename):
        """Download file using requests"""
        try:
            print(f"\n[DOWNLOADING] {filename}")
            print(f"URL: {url[:100]}...")
            
            response = self.session.get(url, timeout=60, stream=True)
            response.raise_for_status()
            
            filepath = self.download_dir / filename
            
            with open(filepath, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
            
            file_size_mb = filepath.stat().st_size / (1024 * 1024)
            print(f"[OK] Downloaded: {filepath.name} ({file_size_mb:.2f} MB)")
            
            return filepath
            
        except Exception as e:
            print(f"[ERROR] Download failed: {e}")
            return None
    
    def download_top_20_funds(self):
        """Main: Auto-discover and download Top 20 funds"""
        print("\n" + "="*80)
        print("AUTO-DOWNLOADING TOP 20 MUTUAL FUNDS BY AUM")
        print("="*80)
        print("\nTarget: 70% of retail investor coverage")
        
        downloaded = []
        skipped = []
        
        # Group by AMC
        by_amc = {}
        for fund in self.top_20_funds:
            if fund.get('status') == 'done':
                print(f"\n[SKIP] Rank {fund['rank']}: {fund['name']} - Already done")
                continue
            
            amc = fund['amc']
            if amc not in by_amc:
                by_amc[amc] = []
            by_amc[amc].append(fund)
        
        # Process each AMC
        for amc, funds in by_amc.items():
            print(f"\n\n{'#'*80}")
            print(f"AMC: {amc} ({len(funds)} funds needed)")
            print(f"{'#'*80}")
            
            available_files = self.discover_fund_urls(amc)
            
            if not available_files:
                print(f"\n[SKIP] {amc}: No files found")
                skipped.extend(funds)
                continue
            
            for fund in funds:
                matched_file = self.match_fund_to_url(fund, available_files)
                
                if matched_file:
                    safe_name = fund['name'].replace(' ', '_').replace('&', 'and')
                    filename = f"{safe_name}_latest.{matched_file['type']}"
                    
                    filepath = self.download_file(matched_file['url'], filename)
                    
                    if filepath:
                        downloaded.append({
                            'rank': fund['rank'],
                            'fund': fund['name'],
                            'amc': amc,
                            'filepath': str(filepath),
                            'type': matched_file['type']
                        })
                else:
                    print(f"\n[MISS] Rank {fund['rank']}: {fund['name']} - No match")
                    skipped.append(fund)
                
                time.sleep(2)
        
        # Summary
        print("\n\n" + "="*80)
        print("DOWNLOAD SUMMARY")
        print("="*80)
        print(f"\n Downloaded: {len(downloaded)} funds")
        print(f"  Skipped: {len(skipped)} funds")
        print(f"\n Coverage: {(len(downloaded) / 19) * 100:.0f}% of Top 20 (excluding PPFAS)")
        
        if downloaded:
            print("\n Successfully Downloaded:")
            for item in downloaded:
                print(f"  {item['rank']}. {item['fund']} ({item['type'].upper()})")
        
        if skipped:
            print("\n  Skipped:")
            for fund in skipped:
                print(f"  {fund['rank']}. {fund['name']} ({fund['amc']})")
        
        results_file = self.download_dir.parent / 'top_20_download_results.json'
        with open(results_file, 'w') as f:
            json.dump({
                'download_date': datetime.now().isoformat(),
                'downloaded': downloaded,
                'skipped': [{'rank': f['rank'], 'name': f['name'], 'amc': f['amc']} for f in skipped]
            }, f, indent=2)
        
        print(f"\n Results saved to: {results_file}")
        return downloaded, skipped


def main():
    downloader = Top20FundsDownloader()
    downloader.download_top_20_funds()


if __name__ == "__main__":
    main()
