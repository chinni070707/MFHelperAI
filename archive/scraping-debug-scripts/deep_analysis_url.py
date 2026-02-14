"""
Deep dive into the user's URL to find where 30+ holdings are shown
"""
import requests
from bs4 import BeautifulSoup

url = 'https://www.moneycontrol.com/mutual-funds/hdfc-flexi-cap-fund/portfolio-holdings/MHD001'

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
}

response = requests.get(url, headers=headers, timeout=10)
soup = BeautifulSoup(response.text, 'html.parser')

print(f"\n{'='*80}")
print("DEEP ANALYSIS OF USER'S URL")
print(f"{'='*80}\n")

# 1. Find ALL tables on the page
print("[1] All tables on the page:")
all_tables = soup.find_all('table')
print(f"Found {len(all_tables)} tables\n")

for i, table in enumerate(all_tables, 1):
    header_row = table.find('tr')
    if header_row:
        headers = [th.text.strip() for th in header_row.find_all(['th', 'td'])]
        row_count = len(table.find_all('tr')) - 1
        print(f"Table {i}: {row_count} rows")
        print(f"  Headers: {headers[:5]}")  # First 5 headers
        print()

# 2. Look for tabs or sections
print("\n[2] Looking for tabs/sections:")
tabs = soup.find_all(['a', 'button', 'li', 'div'], attrs={'class': lambda x: x and ('tab' in str(x).lower() or 'nav' in str(x).lower())})
relevant_tabs = []
for tab in tabs:
    text = tab.text.strip()
    if text and len(text) < 50 and any(word in text.lower() for word in ['portfolio', 'holding', 'equity', 'stock', 'detail', 'complete', 'full']):
        href = tab.get('href', '')
        onclick = tab.get('onclick', '')
        relevant_tabs.append({
            'text': text,
            'href': href,
            'onclick': onclick
        })

if relevant_tabs:
    print("Found relevant tabs/links:")
    for tab in relevant_tabs[:10]:
        print(f"  - '{tab['text']}'")
        if tab['href']:
            print(f"    href: {tab['href']}")
        if tab['onclick']:
            print(f"    onclick: {tab['onclick']}")
else:
    print("No relevant tabs found")

# 3. Look for expandable sections or accordions
print("\n[3] Looking for expandable sections:")
expand_elements = soup.find_all(['div', 'section'], attrs={'class': lambda x: x and any(cls in str(x).lower() for cls in ['collapse', 'expand', 'accordion', 'toggle'])})
if expand_elements:
    print(f"Found {len(expand_elements)} expandable elements")
    for elem in expand_elements[:5]:
        print(f"  - class: {elem.get('class')}")
        print(f"    id: {elem.get('id')}")
else:
    print("No expandable sections found")

# 4. Check for pagination or "Show More" in the specific table area
print("\n[4] Looking for pagination near portfolio table:")
for table in all_tables:
    header_row = table.find('tr')
    if header_row:
        headers = [th.text.strip() for th in header_row.find_all(['th', 'td'])]
        if 'Stock Invested in' in headers:
            # Look for pagination around this table
            parent = table.parent
            if parent:
                pagination = parent.find_all(['a', 'button', 'div'], string=lambda t: t and any(word in t.lower() for word in ['more', 'all', 'next', 'page']))
                if pagination:
                    print("Found pagination/show more:")
                    for elem in pagination:
                        print(f"  - {elem.name}: '{elem.text.strip()[:40]}'")
                        print(f"    href: {elem.get('href', 'N/A')}")
                        print(f"    onclick: {elem.get('onclick', 'N/A')}")
                else:
                    print("No pagination found near portfolio table")

# 5. Save a snippet of the page source around the table
print("\n[5] Checking page source around 'portfolio' keyword:")
page_source = response.text
portfolio_idx = page_source.lower().find('portfolio')
if portfolio_idx != -1:
    snippet = page_source[portfolio_idx:portfolio_idx+500]
    # Look for any URLs or endpoints
    if '/portfolio' in snippet or 'getportfolio' in snippet.lower() or 'loadholdings' in snippet.lower():
        print("Found portfolio-related code:")
        print(snippet[:300])

print(f"\n{'='*80}")
print("RECOMMENDATION")
print(f"{'='*80}")
print("""
If you saw 30+ holdings manually, please check:
1. Were you logged in to MoneyControl?
2. Did you scroll down or click a 'Show More' button?
3. Was it a different page/tab?
4. Can you take a screenshot showing where you saw 30+ holdings?
""")
print(f"{'='*80}\n")
