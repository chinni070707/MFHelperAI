"""
Enhanced AMFI Portfolio Scraper - Extract AMC URLs from JavaScript

The AMFI page loads content dynamically via Next.js/React.
The AMC portfolio URLs are embedded in the page's JavaScript.
This scraper extracts those URLs directly.
"""
import requests
from bs4 import BeautifulSoup
import json
import re
from typing import Dict, List
from pathlib import Path

def extract_amc_portfolio_urls():
    """Extract ALL AMC portfolio URLs from AMFI page JavaScript"""
    
    url = 'https://www.amfiindia.com/online-center/portfolio-disclosure'
    
    print("\n" + "="*80)
    print("EXTRACTING AMC PORTFOLIO URLS FROM AMFI")
    print("="*80)
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
    }
    
    response = requests.get(url, headers=headers, timeout=30)
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # Extract all scripts
    scripts = soup.find_all('script')
    
    amc_urls = {}
    
    # Pattern to match URLs
    url_pattern = r'https?://[\w\.-]+\.[a-z]{2,}[^\s<>"\'\)]*(?:portfolio|disclosure|holdings|downloads|scheme|factsheet)[^\s<>"\'\)]*'
    
    print(f"\nAnalyzing {len(scripts)} script tags...")
    
    for script in scripts:
        script_text = str(script.string or script.get_text())
        
        # Find all matching URLs
        urls = re.findall(url_pattern, script_text, re.IGNORECASE)
        
        for url in urls:
            # Clean URL
            url = url.rstrip('\\').rstrip(',').rstrip('"').rstrip("'")
            
            # Extract AMC name from URL
            amc_name = None
            
            # Common AMC patterns in URLs
            amc_patterns = {
                'icicipruamc': 'ICICI Prudential Mutual Fund',
                'hdfcfund': 'HDFC Mutual Fund',
                'sbimf': 'SBI Mutual Fund',
                'kotakmf': 'Kotak Mahindra Mutual Fund',
                'axismf': 'Axis Mutual Fund',
                'barodabnpparibasmf': 'Baroda BNP Paribas Mutual Fund',
                'dspim': 'DSP Investment Managers',
                'nipponindiaim': 'Nippon India Mutual Fund',
                'quantmutual': 'Quant Mutual Fund',
                'trustmf': 'Trust Mutual Fund',
                'hsbc.co.in': 'HSBC Mutual Fund',
                'franklintempleton': 'Franklin Templeton Mutual Fund',
                'bnpparibasmf': 'BNP Paribas Mutual Fund',
                'tatamutualfund': 'Tata Mutual Fund',
                'utimf': 'UTI Mutual Fund',
                'birlasunlife': 'Aditya Birla Sun Life Mutual Fund',
                'motilaloswalmf': 'Motilal Oswal Mutual Fund',
                'mahindramanulife': 'Mahindra Manulife Mutual Fund',
                'idfcmf': 'IDFC Mutual Fund',
                'licmf': 'LIC Mutual Fund',
                'edelweissmf': 'Edelweiss Mutual Fund',
                'idbiamcindia': 'IDBI Mutual Fund',
                'ppfas': 'Parag Parikh Mutual Fund',
                'jmfinancialmf': 'JM Financial Mutual Fund',
                'shriramam': 'Shriram Asset Management',
                'unionmf': 'Union Mutual Fund',
                'pgim': 'PGIM India Mutual Fund',
                'invescomutualfund': 'Invesco Mutual Fund',
            }
            
            for pattern, name in amc_patterns.items():
                if pattern in url.lower():
                    amc_name = name
                    break
            
            if amc_name and amc_name not in amc_urls:
                amc_urls[amc_name] = {
                    'amc': amc_name,
                    'portfolio_url': url,
                    'source': 'AMFI Official Page'
                }
    
    print(f"\n[OK] Found portfolio URLs for {len(amc_urls)} AMCs")
    
    # Sort by AMC name
    sorted_amcs = sorted(amc_urls.items())
    
    print("\nAMC PORTFOLIO LINKS:")
    print("="*80)
    for i, (amc_name, data) in enumerate(sorted_amcs, 1):
        print(f"\n{i}. {amc_name}")
        print(f"   URL: {data['portfolio_url'][:100]}...")
    
    # Save to JSON
    output_file = Path(__file__).parent.parent / 'data' / 'amc_portfolio_urls.json'
    output_file.parent.mkdir(parents=True, exist_ok=True)
    
    output_data = {
        'last_updated': '2026-02-12',
        'source': 'AMFI Portfolio Disclosure Page',
        'total_amcs': len(amc_urls),
        'amcs': list(amc_urls.values())
    }
    
    with open(output_file, 'w') as f:
        json.dump(output_data, f, indent=2)
    
    print(f"\nSaved to: {output_file}")
    print("\n" + "="*80)
    print("[OK] EXTRACTION COMPLETE!")
    print("="*80)
    
    return amc_urls

if __name__ == "__main__":
    amc_urls = extract_amc_portfolio_urls()
    
    print(f"\nNEXT STEPS:")
    print("  1. Review the extracted URLs")
    print("  2. Visit each AMC's portfolio page")
    print("  3. Download Excel/PDF files")
    print("  4. Parse holdings data")
    print(f"\nTotal AMCs found: {len(amc_urls)}")
