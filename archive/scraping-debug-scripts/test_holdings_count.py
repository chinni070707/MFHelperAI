"""
Test script to check how many holdings are actually available on MoneyControl page
"""
import requests
from bs4 import BeautifulSoup

# Test with a fund that should have many holdings
test_urls = [
    {
        'name': 'Union Flexi Cap Fund',
        'url': 'https://www.moneycontrol.com/mutual-funds/union-flexi-cap-fund-direct-plan-growth/portfolio-holdings/MUK027'
    },
    {
        'name': 'HDFC Flexi Cap Fund (original 98)',
        'url': 'https://www.moneycontrol.com/mutual-funds/hdfc-flexi-cap-fund-direct-plan-growth/portfolio-holdings/MHD1144'
    },
    {
        'name': 'Samco Large Cap Fund',
        'url': 'https://www.moneycontrol.com/mutual-funds/samco-large-cap-fund-direct-plan-growth/portfolio-holdings/MSAA016'
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
        tables = soup.find_all('table')
        holdings_table = None
        
        for table in tables:
            header_row = table.find('tr')
            if header_row:
                headers_list = [th.text.strip() for th in header_row.find_all(['th', 'td'])]
                if 'Stock Invested in' in headers_list:
                    holdings_table = table
                    print(f"\n[FOUND] Portfolio table with headers: {headers_list}")
                    break
        
        if not holdings_table:
            print("[ERROR] No portfolio table found")
            continue
        
        # Count all rows
        all_rows = holdings_table.find_all('tr')
        data_rows = all_rows[1:]  # Skip header
        
        print(f"\n[INFO] Total rows in table: {len(all_rows)} (including header)")
        print(f"[INFO] Data rows: {len(data_rows)}")
        
        # Extract and show first 15 and last 5
        print(f"\n[FIRST 15 STOCKS]:")
        for i, row in enumerate(data_rows[:15], 1):
            cols = row.find_all('td')
            if len(cols) >= 4:
                stock = cols[0].text.strip().replace('#', '').strip()
                sector = cols[1].text.strip()
                weight = cols[3].text.strip()
                print(f"  {i}. {stock}: {weight} ({sector})")
        
        if len(data_rows) > 15:
            print(f"\n... [{len(data_rows) - 20} more rows] ...")
            print(f"\n[LAST 5 STOCKS]:")
            for i, row in enumerate(data_rows[-5:], len(data_rows) - 4):
                cols = row.find_all('td')
                if len(cols) >= 4:
                    stock = cols[0].text.strip().replace('#', '').strip()
                    sector = cols[1].text.strip()
                    weight = cols[3].text.strip()
                    print(f"  {i}. {stock}: {weight} ({sector})")
        
        # Check if there's pagination
        pagination = soup.find_all(['a', 'button'], text=lambda t: t and ('next' in t.lower() or 'more' in t.lower()))
        if pagination:
            print(f"\n[WARNING] Found pagination elements: {[p.text.strip() for p in pagination]}")
        else:
            print(f"\n[INFO] No pagination found - all holdings should be on this page")
        
    except Exception as e:
        print(f"[ERROR] {e}")

print(f"\n{'='*80}")
print("ANALYSIS COMPLETE")
print(f"{'='*80}\n")
