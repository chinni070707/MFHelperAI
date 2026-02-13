"""
Parse Parag Parikh Excel files and generate fund_holdings.json

Extract stock names, weights, and sectors from downloaded Excel files.
"""
import pandas as pd
import json
from pathlib import Path
from datetime import datetime

def parse_ppfas_holdings(filepath):
    """Parse PPFAS Excel file and extract holdings"""
    
    try:
        # Read Excel - raw data
        df = pd.read_excel(filepath, sheet_name=0)
        
        # PPFAS structure:
        # Row 2: Headers (Name of Instrument, ISIN, Industry/Rating, Quantity, Market Value, % to Net Assets)
        # Row 5+: Actual stock data
        # Column indices: 0=Code, 1=Stock Name, 2=ISIN, 3=Sector, 4=Quantity, 5=Value, 6=Weight%
        
        holdings = []
        
        # Start from row 5 (0-indexed)
        for idx in range(5, len(df)):
            row = df.iloc[idx]
            
            # Col 1: Stock name
            stock_name = row.iloc[1] if len(row) > 1 else None
            
            # Col 6: Weight percentage
            weight = row.iloc[6] if len(row) > 6 else None
            
            # Col 3: Sector/Industry
            sector = row.iloc[3] if len(row) > 3 else None
            
            # Validate and clean
            if pd.isna(stock_name) or pd.isna(weight):
                continue
            
            stock_name_str = str(stock_name).strip()
            
            # Skip non-stock rows
            if (len(stock_name_str) < 3 or 
                'Total' in stock_name_str or
                'Equity' in stock_name_str or
                'Listed' in stock_name_str or
                'Net Assets' in stock_name_str or
                '(b)' in stock_name_str or
                '(a)' in stock_name_str or
                'Securities' in stock_name_str):
                continue
            
            try:
                weight_float = float(weight) * 100  # Convert decimal to percentage
            except:
                continue
            
            # Only include holdings > 0.1%
            if weight_float < 0.1:
                continue
            
            sector_str = str(sector).strip() if pd.notna(sector) else 'Unknown'
            
            holdings.append({
                'stock': stock_name_str,
                'weight': round(weight_float, 2),
                'sector': sector_str
            })
        
        return holdings
        
    except Exception as e:
        print(f"[ERROR] Parsing {filepath}: {e}")
        import traceback
        traceback.print_exc()
        return None

def generate_fund_holdings_json():
    """Generate fund_holdings.json from Parag Parikh files"""
    
    print("\n" + "="*80)
    print("GENERATING FUND HOLDINGS JSON")
    print("="*80)
    
    download_dir = Path(__file__).parent.parent / 'data' / 'portfolio_downloads'
    
    funds_data = {}
    
    # Parse PPFCF - Parag Parikh Flexi Cap Fund
    print("\n[1/3] Parsing PPFCF - Parag Parikh Flexi Cap Fund...")
    ppfcf_file = download_dir / 'PPFCF_January_2026.xls'
    
    if ppfcf_file.exists():
        holdings = parse_ppfas_holdings(ppfcf_file)
        if holdings:
            print(f"[OK] Found {len(holdings)} holdings")
            
            # Display top 10
            print("\nTop 10 holdings:")
            for i, h in enumerate(holdings[:10], 1):
                print(f"  {i}. {h['stock']}: {h['weight']}% ({h['sector']})")
            
            funds_data['parag-parikh-flexi-cap-fund'] = {
                'name': 'Parag Parikh Flexi Cap Fund',
                'amc': 'Parag Parikh Mutual Fund',
                'category': 'Flexi Cap',
                'holdings': holdings,
                'holdings_count': len(holdings),
                'as_of_date': '2026-01-31',
                'source': 'PPFAS Official Portfolio Disclosure'
            }
    else:
        print(f"[SKIP] File not found: {ppfcf_file}")
    
    # Parse PPFAS Consolidated
    print("\n[2/3] Parsing PPFAS Consolidated...")
    ppfas_file = download_dir / 'PPFAS_Consolidated_January_2026.xls'
    
    if ppfas_file.exists():
        holdings = parse_ppfas_holdings(ppfas_file)
        if holdings:
            print(f"[OK] Found {len(holdings)} holdings")
            
            # Display top 10
            print("\nTop 10 holdings:")
            for i, h in enumerate(holdings[:10], 1):
                print(f"  {i}. {h['stock']}: {h['weight']}% ({h['sector']})")
            
            funds_data['ppfas-consolidated'] = {
                'name': 'Parag Parikh PPFAS Consolidated Fund',
                'amc': 'Parag Parikh Mutual Fund',
                'category': 'Multi Cap',
                'holdings': holdings,
                'holdings_count': len(holdings),
                'as_of_date': '2026-01-31',
                'source': 'PPFAS Official Portfolio Disclosure'
            }
    else:
        print(f"[SKIP] File not found: {ppfas_file}")
    
    # Parse PPLF - Liquid Fund
    print("\n[3/3] Parsing PPLF - Parag Parikh Liquid Fund...")
    pplf_file = download_dir / 'PPLF_January_2026.xls'
    
    if pplf_file.exists():
        holdings = parse_ppfas_holdings(pplf_file)
        if holdings:
            print(f"[OK] Found {len(holdings)} holdings")
            
            # Display top 10
            print("\nTop 10 holdings:")
            for i, h in enumerate(holdings[:10], 1):
                print(f"  {i}. {h['stock']}: {h['weight']}% ({h['sector']})")
            
            funds_data['parag-parikh-liquid-fund'] = {
                'name': 'Parag Parikh Liquid Fund',
                'amc': 'Parag Parikh Mutual Fund',
                'category': 'Liquid',
                'holdings': holdings,
                'holdings_count': len(holdings),
                'as_of_date': '2026-01-31',
                'source': 'PPFAS Official Portfolio Disclosure'
            }
    else:
        print(f"[SKIP] File not found: {pplf_file}")
    
    # Save to fund_holdings.json
    output_file = Path(__file__).parent.parent / 'data' / 'fund_holdings.json'
    
    # Read existing file if it exists
    existing_data = {}
    if output_file.exists():
        with open(output_file, 'r') as f:
            existing_data = json.load(f)
    
    # Merge with existing data
    if 'funds' not in existing_data:
        existing_data['funds'] = {}
    
    existing_data['funds'].update(funds_data)
    existing_data['version'] = '2026-02'
    existing_data['last_updated'] = datetime.now().strftime('%Y-%m-%d')
    
    # Save
    with open(output_file, 'w') as f:
        json.dump(existing_data, f, indent=2, ensure_ascii=False)
    
    print(f"\n[SUCCESS] Updated fund_holdings.json")
    print(f"Location: {output_file}")
    print(f"\nTotal funds in database: {len(existing_data['funds'])}")
    print(f"New funds added: {len(funds_data)}")
    
    print("\n" + "="*80)
    print("SUMMARY")
    print("="*80)
    
    for key, fund in funds_data.items():
        print(f"\n[OK] {fund['name']}")
        print(f"     Holdings: {fund['holdings_count']}")
        print(f"     Category: {fund['category']}")
    
    return funds_data

if __name__ == "__main__":
    generate_fund_holdings_json()
