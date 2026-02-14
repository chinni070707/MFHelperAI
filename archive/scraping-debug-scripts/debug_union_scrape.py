"""
Test scraper on Union Flexi Cap to debug why only 4 holdings extracted
URL: https://www.moneycontrol.com/mutual-funds/union-flexi-cap-fund-direct-plan-growth/portfolio-holdings/MUK027
"""
import requests
from bs4 import BeautifulSoup

url = "https://www.moneycontrol.com/mutual-funds/union-flexi-cap-fund-direct-plan-growth/portfolio-holdings/MUK027"

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
}

print("Fetching URL...")
response = requests.get(url, headers=headers, timeout=30)
print(f"Status: {response.status_code}\n")

soup = BeautifulSoup(response.text, 'html.parser')

# Find all tables
tables = soup.find_all('table')
print(f"Found {len(tables)} tables on the page\n")

# Find the correct table
holdings_table = None
for i, table in enumerate(tables):
    header_row = table.find('tr')
    if header_row:
        headers = [th.text.strip() for th in header_row.find_all(['th', 'td'])]
        print(f"Table {i+1} headers: {headers[:5]}")  # Print first 5 headers
        if 'Stock Invested in' in headers:
            holdings_table = table
            print(f"✓ Found holdings table (Table {i+1})")
            break

if not holdings_table:
    print("\n❌ No holdings table found!")
    exit(1)

print(f"\nExtracting holdings...\n")
print("="*80)

rows = holdings_table.find_all('tr')[1:]  # Skip header
print(f"Total data rows: {len(rows)}\n")

holdings = []
for idx, row in enumerate(rows, 1):
    cols = row.find_all('td')
    
    print(f"Row {idx}: {len(cols)} columns")
    
    if len(cols) < 5:
        print(f"  → Skipped (< 5 columns)")
        continue
    
    # Extract data
    stock_name = cols[0].text.strip().replace('#', '').strip()
    sector = cols[1].text.strip() if len(cols) > 1 else 'Unknown'
    weight_text = cols[3].text.strip() if len(cols) > 3 else '0'  # Fixed: Col 3, not Col 4!
    
    # Show what we're seeing
    print(f"  Stock: {stock_name[:50]}")
    print(f"  Sector: {sector[:30]}")
    print(f"  Weight: {weight_text}")
    
    # Check filters
    skip_keywords = ['total', 'equity', 'debt', 'cash', 'net', 'treps']
    if any(skip in stock_name.lower() for skip in skip_keywords):
        print(f"  → Skipped (summary row)")
        continue
    
    if not stock_name or len(stock_name) < 3:
        print(f"  → Skipped (name too short)")
        continue
    
    try:
        weight = float(weight_text.replace('%', '').strip())
    except:
        print(f"  → Skipped (invalid weight)")
        continue
    
    if weight <= 0.1:
        print(f"  → Skipped (weight <= 0.1%)")
        continue
    
    holdings.append({
        'stock': stock_name,
        'weight': weight,
        'sector': sector
    })
    print(f"  ✓ Added to holdings")

print("\n" + "="*80)
print(f"\n✓ Successfully extracted {len(holdings)} holdings\n")

if holdings:
    print("First 10 holdings:")
    for i, h in enumerate(holdings[:10], 1):
        print(f"  {i}. {h['stock']}: {h['weight']}% ({h['sector']})")

print(f"\n📊 Total: {len(holdings)} holdings")
print(f"✓ Would {'PASS' if len(holdings) > 5 else 'FAIL'} the >5 threshold check")
