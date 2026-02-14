"""
Check if MoneyControl loads additional holdings via JavaScript/AJAX
Look for dynamic content loading
"""
import requests
from bs4 import BeautifulSoup
import re

url = 'https://www.moneycontrol.com/mutual-funds/hdfc-flexi-cap-fund-direct-plan-growth/portfolio-holdings/MHD1144'

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
}

response = requests.get(url, headers=headers)
page_source = response.text

print(f"\n{'='*80}")
print("ANALYZING PAGE FOR DYNAMIC LOADING")
print(f"{'='*80}\n")

# 1. Check for "Show More" / "Load More" buttons
print("[1] Looking for 'Show More' / 'Load More' elements...")
soup = BeautifulSoup(page_source, 'html.parser')
load_more = soup.find_all(['a', 'button', 'div'], string=re.compile(r'(show|load|view).*(more|all)', re.I))
if load_more:
    for elem in load_more:
        print(f"  [FOUND] {elem.name} - '{elem.text.strip()[:50]}'")
        print(f"    onclick: {elem.get('onclick', 'N/A')}")
        print(f"    data-url: {elem.get('data-url', 'N/A')}")
else:
    print("  [NOT FOUND] No 'Load More' elements")

# 2. Look for AJAX endpoints in JavaScript
print("\n[2] Searching for AJAX/API calls in JavaScript...")
ajax_patterns = [
    r'\.ajax\([^)]+\)',
    r'fetch\(["\']([^"\']+)',
    r'XMLHttpRequest.*open\(["\']GET["\'],\s*["\']([^"\']+)',
    r'/api/[^"\'\s]+',
    r'getPortfolio',
    r'loadHoldings'
]

for pattern in ajax_patterns:
    matches = re.findall(pattern, page_source, re.IGNORECASE)
    if matches:
        print(f"  ✓ Pattern '{pattern}' found {len(matches)} times:")
        for match in matches[:3]:
            print(f"    - {match[:80]}")

# 3. Check if table rows have data-* attributes that might trigger loading
print("\n[3] Checking table for dynamic loading attributes...")
table = soup.find('table')
if table:
    rows = table.find_all('tr')
    has_data_attrs = False
    for row in rows[:5]:
        attrs = {k:v for k,v in row.attrs.items() if k.startswith('data-')}
        if attrs:
            has_data_attrs = True
            print(f"  ✓ Found data attributes: {attrs}")
    
    if not has_data_attrs:
        print("  [NOT FOUND] No data-* attributes in table rows")
    
    # Check if last row has "load more" indicator
    last_row = rows[-1] if rows else None
    if last_row:
        last_text = last_row.get_text().lower()
        if 'more' in last_text or 'load' in last_text:
            print(f"  [FOUND] Last row indicates more data: '{last_text[:50]}'")
else:
    print("  [NOT FOUND] No table found")

# 4. Check for fund scheme code that might be used in API calls
print("\n[4] Looking for scheme code in page...")
scheme_patterns = [
    r'scheme[_-]?code["\']?\s*[:=]\s*["\']?([A-Z0-9]+)',
    r'schemeCode:\s*["\']([^"\']+)',
    r'MHD\d+',  # MoneyControl code pattern
]

for pattern in scheme_patterns:
    matches = re.findall(pattern, page_source)
    if matches:
        print(f"  ✓ Found scheme codes: {matches[:5]}")

# 5. Check if there's pagination
print("\n[5] Checking for pagination...")
pagination = soup.find_all(['nav', 'div'], attrs={'class': re.compile(r'paginat', re.I)})
pagination += soup.find_all(['a'], string=re.compile(r'(next|previous|page \d+)', re.I))
if pagination:
    for elem in pagination:
        print(f"  [FOUND] {elem.name} - class={elem.get('class')} - text={elem.text[:30]}")
else:
    print("  [NOT FOUND] No pagination found")

print(f"\n{'='*80}")
print("CONCLUSION")
print(f"{'='*80}")
print("""
If no dynamic loading mechanisms are found, then MoneyControl genuinely
only displays 10 holdings on this page now, and full holdings data must
come from:
1. A different MoneyControl page/URL
2. MoneyControl API (requires auth/subscription)
3. AMC official disclosures (scrape each AMC's website)
4. Third-party data providers (ValueResearch, Morningstar, etc.)
""")
print(f"{'='*80}\n")
