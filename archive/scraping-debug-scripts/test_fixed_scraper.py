"""
Quick test of the fixed scraper logic
"""
import requests
from bs4 import BeautifulSoup

url = 'https://www.moneycontrol.com/mutual-funds/hdfc-flexi-cap-fund/portfolio-holdings/MHD001'

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
}

print(f"\nTesting fixed scraper logic on: {url}\n")

response = requests.get(url, headers=headers, timeout=10)
soup = BeautifulSoup(response.text, 'html.parser')

# New logic: Find table with MOST rows
holdings_table = None
table_col_layout = "standard"
best_row_count = 0

tables = soup.find_all('table')

for table in tables:
    header_row = table.find('tr')
    if header_row:
        headers = [th.text.strip() for th in header_row.find_all(['th', 'td'])]
        if 'Stock Invested in' in headers and '% of Total Holdings' in headers:
            row_count = len(table.find_all('tr'))
            print(f"Found portfolio table with {row_count} rows")
            print(f"  Headers: {headers}")
            
            if row_count > best_row_count:
                best_row_count = row_count
                holdings_table = table
                if 'Sector Total' in headers:
                    table_col_layout = "extended"
                else:
                    table_col_layout = "standard"

print(f"\n[SELECTED] Table with {best_row_count} rows (layout: {table_col_layout})")

# Extract holdings using correct column
holdings = []
rows = holdings_table.find_all('tr')[1:]  # Skip header

for row in rows:
    cols = row.find_all('td')
    
    if len(cols) < 4:
        continue
    
    stock_name = cols[0].text.strip().replace('#', '').strip().lstrip('-').strip()
    sector = cols[1].text.strip() if len(cols) > 1 else 'Unknown'
    
    # Use correct column based on layout
    if table_col_layout == "extended":
        weight_text = cols[4].text.strip() if len(cols) > 4 else '0'
    else:
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

print(f"\n[SUCCESS] Extracted {len(holdings)} holdings!")
print(f"\nFirst 10 holdings:")
for i, h in enumerate(holdings[:10], 1):
    print(f"  {i}. {h['stock']}: {h['weight']}% ({h['sector']})")

if len(holdings) > 20:
    print(f"\n... [{len(holdings) - 20} more holdings] ...")
    print(f"\nLast 10 holdings:")
    for i, h in enumerate(holdings[-10:], len(holdings) - 9):
        print(f"  {i}. {h['stock']}: {h['weight']}% ({h['sector']})")

# Check total weight
total_weight = sum(h['weight'] for h in holdings)
print(f"\n[TOTAL WEIGHT] {total_weight:.1f}%")
print(f"[RESULT] {'COMPLETE PORTFOLIO' if total_weight > 80 else 'PARTIAL PORTFOLIO'}")
