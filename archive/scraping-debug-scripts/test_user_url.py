"""
Test the URL provided by user - different format!
"""
import requests
from bs4 import BeautifulSoup

# User's URL - regular plan, not direct plan
test_urls = [
    {
        'name': 'HDFC Flexi Cap (Regular Plan - User URL)',
        'url': 'https://www.moneycontrol.com/mutual-funds/hdfc-flexi-cap-fund/portfolio-holdings/MHD001'
    },
    {
        'name': 'HDFC Flexi Cap (Direct Plan - Our URL)',
        'url': 'https://www.moneycontrol.com/mutual-funds/hdfc-flexi-cap-fund-direct-plan-growth/portfolio-holdings/MHD1144'
    }
]

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
}

for test in test_urls:
    print(f"\n{'='*80}")
    print(f"Testing: {test['name']}")
    print(f"URL: {test['url']}")
    print(f"{'='*80}")
    
    try:
        response = requests.get(test['url'], headers=headers, timeout=10)
        
        if response.status_code != 200:
            print(f"[ERROR] Status {response.status_code}")
            continue
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Find portfolio table
        holdings_table = None
        for table in soup.find_all('table'):
            header_row = table.find('tr')
            if header_row:
                headers_list = [th.text.strip() for th in header_row.find_all(['th', 'td'])]
                if 'Stock Invested in' in headers_list:
                    holdings_table = table
                    print(f"\n[FOUND] Portfolio table")
                    print(f"Headers: {headers_list}")
                    break
        
        if not holdings_table:
            print("[ERROR] No portfolio table found")
            continue
        
        # Count all data rows
        all_rows = holdings_table.find_all('tr')
        data_rows = all_rows[1:]  # Skip header
        
        print(f"\n[INFO] Total data rows in table: {len(data_rows)}")
        
        # Extract holdings
        holdings = []
        for i, row in enumerate(data_rows, 1):
            cols = row.find_all('td')
            if len(cols) >= 4:
                stock = cols[0].text.strip().replace('#', '').strip()
                sector = cols[1].text.strip()
                weight = cols[3].text.strip()
                
                # Skip totals/summary rows
                if any(skip in stock.lower() for skip in ['total', 'equity', 'debt', 'cash', 'net', 'treps']):
                    continue
                
                holdings.append({
                    'stock': stock,
                    'sector': sector,
                    'weight': weight
                })
                
                # Show first 10 and last 5
                if i <= 10:
                    print(f"  {i}. {stock}: {weight} ({sector})")
        
        if len(holdings) > 15:
            print(f"\n  ... [{len(holdings) - 15} more holdings] ...")
            print(f"\n[LAST 5 HOLDINGS]:")
            for holding in holdings[-5:]:
                print(f"  {len(holdings) - 4 + holdings[-5:].index(holding)}. {holding['stock']}: {holding['weight']} ({holding['sector']})")
        
        print(f"\n[RESULT] Extracted {len(holdings)} valid holdings!")
        
        # Check total weight
        try:
            weights = [float(h['weight'].replace('%', '').strip()) for h in holdings]
            total_weight = sum(weights)
            print(f"[TOTAL WEIGHT] {total_weight:.1f}%")
        except:
            pass
        
    except Exception as e:
        print(f"[ERROR] {e}")

print(f"\n{'='*80}")
print("CONCLUSION")
print(f"{'='*80}")
print("Check if Regular Plan URLs have more holdings than Direct Plan URLs")
print(f"{'='*80}\n")
