"""
Download and Parse Parag Parikh Holdings

Parag Parikh has excellent disclosure - 360 portfolio files available!
Let's download and parse their holdings for the top 3 funds:
1. PPFCF - Parag Parikh Flexi Cap Fund
2. PPTSF - Parag Parikh Tax Saver Fund  
3. PPLF - Parag Parikh Liquid Fund (or other equity fund)
"""
import requests
from pathlib import Path
import json
from datetime import datetime

def download_ppfas_portfolio(url, filename):
    """Download a Parag Parikh portfolio file"""
    try:
        print(f"\nDownloading: {filename}")
        print(f"URL: {url[:80]}...")
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        response = requests.get(url, headers=headers, timeout=30)
        
        if response.status_code == 200:
            # Save file
            output_dir = Path(__file__).parent.parent / 'data' / 'portfolio_downloads'
            output_dir.mkdir(parents=True, exist_ok=True)
            
            filepath = output_dir / filename
            
            with open(filepath, 'wb') as f:
                f.write(response.content)
            
            print(f"[OK] Saved: {filepath}")
            print(f"Size: {len(response.content):,} bytes")
            
            return str(filepath)
        else:
            print(f"[ERROR] Status: {response.status_code}")
            return None
            
    except Exception as e:
        print(f"[ERROR] {e}")
        return None

def parse_ppfas_excel(filepath):
    """Parse Parag Parikh Excel portfolio file"""
    try:
        import pandas as pd
        
        print(f"\nParsing: {filepath}")
        
        # Read Excel file
        df = pd.read_excel(filepath, sheet_name=None)  # Read all sheets
        
        print(f"[OK] Found {len(df)} sheets")
        
        for sheet_name in df.keys():
            print(f"  - {sheet_name}")
        
        # Try the first sheet
        first_sheet_name = list(df.keys())[0]
        data = df[first_sheet_name]
        
        print(f"\nAnalyzing sheet: {first_sheet_name}")
        print(f"Shape: {data.shape[0]} rows x {data.shape[1]} columns")
        print(f"\nColumns: {list(data.columns)}")
        
        # Display first few rows
        print(f"\nFirst 10 rows:")
        print(data.head(10).to_string())
        
        return data
        
    except Exception as e:
        print(f"[ERROR] Parsing failed: {e}")
        return None

def main():
    """Download and parse Parag Parikh

 portfolio files"""
    
    print("\n" + "="*80)
    print("PARAG PARIKH PORTFOLIO DOWNLOADER")
    print("="*80)
    
    # Top 3 Parag Parikh funds - using latest January 2026 data (actual URLs from scrape)
    target_files = [
        {
            'fund': 'PPFCF - Parag Parikh Flexi Cap Fund',
            'url': 'https://amc.ppfas.com/downloads/portfolio-disclosure/2026/PPFCF_PPFAS_Monthly_Portfolio_Report_January_31_2026.xls?31012026_1',
            'filename': 'PPFCF_January_2026.xls'
        },
        {
            'fund': 'PPFAS Consolidated',
            'url': 'https://amc.ppfas.com/downloads/portfolio-disclosure/2026/PPFAS_Monthly_Portfolio_Report_January_31_2026.xls?31012026_1',
            'filename': 'PPFAS_Consolidated_January_2026.xls'
        },
        {
            'fund': 'PPLF - Parag Parikh Liquid Fund',
            'url': 'https://amc.ppfas.com/downloads/portfolio-disclosure/2026/PPLF_PPFAS_Monthly_Portfolio_Report_January_31_2026.xls?31012026',
            'filename': 'PPLF_January_2026.xls'
        }
    ]
    
    downloaded_files = []
    
    for file_info in target_files:
        print(f"\n{'='*80}")
        print(f"Fund: {file_info['fund']}")
        print(f"{'='*80}")
        
        filepath = download_ppfas_portfolio(file_info['url'], file_info['filename'])
        
        if filepath:
            downloaded_files.append({
                'fund': file_info['fund'],
                'filepath': filepath
            })
    
    # Parse the first downloaded file as example
    if downloaded_files:
        print("\n" + "="*80)
        print("PARSING SAMPLE FILE")
        print("="*80)
        
        sample_file = downloaded_files[0]
        print(f"\nAnalyzing: {sample_file['fund']}")
        
        data = parse_ppfas_excel(sample_file['filepath'])
    
    print("\n" + "="*80)
    print("SUMMARY")
    print("="*80)
    print(f"\nDownloaded: {len(downloaded_files)}/3 files")
    
    for file in downloaded_files:
        print(f"  [OK] {file['fund']}")
    
    print("\n[SUCCESS] Parag Parikh portfolio files downloaded!")
    print("\nNext: Parse holdings data from Excel files")
    
    print("\n" + "="*80)


if __name__ == "__main__":
    main()
