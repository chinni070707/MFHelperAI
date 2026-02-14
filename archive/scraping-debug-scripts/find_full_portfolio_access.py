"""
Check if there's a way to get full holdings from MoneyControl
Look for "view all", "show more", different endpoints, etc.
"""
import requests
from bs4 import BeautifulSoup

url = 'https://www.moneycontrol.com/mutual-funds/hdfc-flexi-cap-fund-direct-plan-growth/portfolio-holdings/MHD1144'

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
}

print(f"\n{'='*80}")
print("SEARCHING FOR FULL PORTFOLIO ACCESS")
print(f"{'='*80}\n")

response = requests.get(url, headers=headers)
soup = BeautifulSoup(response.text, 'html.parser')

# Look for "View All", "Show More", "Load More" buttons/links
view_all_patterns = ['view all', 'show all', 'show more', 'load more', 'see all', 'view complete', 'full portfolio']

print("[1] Searching for 'View All' type buttons/links...")
found_links = []
for pattern in view_all_patterns:
    links = soup.find_all(['a', 'button', 'span', 'div'], 
                         string=lambda t: t and pattern in t.lower())
    if links:
        for link in links:
            href = link.get('href', '')
            onclick = link.get('onclick', '')
            print(f"  ✓ Found: '{link.text.strip()}' | href={href} | onclick={onclick}")
            found_links.append({'text': link.text.strip(), 'href': href, 'onclick': onclick})

if not found_links:
    print("  ✗ No 'View All' buttons found")

# Check for AJAX/API endpoints in the page source
print("\n[2] Searching for API endpoints in page source...")
api_patterns = ['/api/', '/ajax/', '/portfolio/', '/holdings/', '/getholdings']
page_source = response.text

for pattern in api_patterns:
    if pattern in page_source.lower():
        # Find the context around the pattern
        idx = page_source.lower().find(pattern)
        context = page_source[max(0, idx-50):min(len(page_source), idx+100)]
        print(f"  ✓ Found '{pattern}' in source:")
        print(f"    ...{context}...")

# Check if there are tabs or sections for different data
print("\n[3] Checking for tabs/sections...")
tabs = soup.find_all(['a', 'button', 'li'], attrs={'class': lambda x: x and any(t in str(x).lower() for t in ['tab', 'nav'])})
if tabs:
    for tab in tabs[:10]:
        print(f"  - Tab: {tab.text.strip()[:50]} | href={tab.get('href', 'N/A')}")
else:
    print("  ✗ No tabs found")

# Check the data source - maybe it's loaded via JavaScript
print("\n[4] Checking for data attributes...")
data_elements = soup.find_all(attrs={'data-url': True})
if data_elements:
    for elem in data_elements:
        print(f"  ✓ data-url: {elem['data-url']}")

# Look for the fund's scheme code or identifier
print("\n[5] Looking for scheme identifiers...")
scheme_codes = soup.find_all(text=lambda t: t and 'scheme' in t.lower())
for code in scheme_codes[:5]:
    print(f"  - {code.strip()[:80]}")

print(f"\n{'='*80}")
print("RECOMMENDATION:")
print(f"{'='*80}")
print("""
If no 'View All' option found, options are:
1. Accept top 10 holdings as 'partial data'
2. Scrape from AMC websites directly (each has their own format)
3. Use AMFI or other data sources
4. Check if MoneyControl has a paid API
5. Use ValueResearch or Morningstar instead
""")
print(f"{'='*80}\n")
