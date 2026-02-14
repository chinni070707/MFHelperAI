"""
Quick test to explore AMFI Portfolio Disclosure page structure
"""
import requests
from bs4 import BeautifulSoup
import json

url = 'https://www.amfiindia.com/online-center/portfolio-disclosure'

print("\n" + "="*80)
print("🔍 EXPLORING AMFI PORTFOLIO DISCLOSURE PAGE")
print("="*80)

print(f"\n📍 Fetching: {url}")

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
}

response = requests.get(url, headers=headers, timeout=30)
print(f"✅ Status: {response.status_code}")

soup = BeautifulSoup(response.text, 'html.parser')

# Look for various elements
print("\n" + "="*80)
print("🔍 ANALYZING PAGE STRUCTURE")
print("="*80)

# 1. Check for dropdowns/selects
selects = soup.find_all('select')
print(f"\n1️⃣  Dropdown menus found: {len(selects)}")
for i, select in enumerate(selects):
    print(f"   Select {i+1}: id='{select.get('id')}', name='{select.get('name')}'")
    options = select.find_all('option')
    print(f"   → {len(options)} options")
    if options:
        print(f"   → First few: {[opt.text.strip()[:40] for opt in options[:3]]}")

# 2. Check for tables
tables = soup.find_all('table')
print(f"\n2️⃣  Tables found: {len(tables)}")
for i, table in enumerate(tables):
    rows = table.find_all('tr')
    print(f"   Table {i+1}: {len(rows)} rows")

# 3. Check for links with "portfolio" or "disclosure"
portfolio_links = soup.find_all('a', href=True)
print(f"\n3️⃣  Total links: {len(portfolio_links)}")

relevant_links = []
for link in portfolio_links:
    href = link.get('href', '')
    text = link.text.strip()
    
    if any(keyword in href.lower() or keyword in text.lower() 
           for keyword in ['portfolio', 'disclosure', 'holdings', 'amc', 'fund', '.pdf', '.xlsx', '.xls']):
        relevant_links.append({
            'text': text[:60],
            'href': href[:80]
        })

print(f"   Relevant links found: {len(relevant_links)}")
for i, link in enumerate(relevant_links[:10]):
    print(f"   {i+1}. [{link['text']}]")
    print(f"      → {link['href']}")

# 4. Look for buttons or JavaScript triggers
buttons = soup.find_all('button')
print(f"\n4️⃣  Buttons found: {len(buttons)}")
for i, button in enumerate(buttons[:5]):
    print(f"   Button {i+1}: {button.text.strip()[:40]}")
    print(f"   → onclick: {button.get('onclick', 'None')[:60]}")

# 5. Check for JavaScript/dynamic content indicators
scripts = soup.find_all('script')
print(f"\n5️⃣  Script tags found: {len(scripts)}")

has_react = any('react' in str(script).lower() for script in scripts)
has_vue = any('vue' in str(script).lower() for script in scripts)
has_angular = any('angular' in str(script).lower() for script in scripts)
has_next = any('next' in str(script).lower() for script in scripts)

print(f"   React: {'✅' if has_react else '❌'}")
print(f"   Vue: {'✅' if has_vue else '❌'}")
print(f"   Angular: {'✅' if has_angular else '❌'}")
print(f"   Next.js: {'✅' if has_next else '❌'}")

# 6. Look for API endpoints in scripts
api_endpoints = []
for script in scripts:
    script_text = script.string or ''
    if 'api' in script_text.lower():
        # Look for URLs
        import re
        urls = re.findall(r'https?://[^\s<>"\']+|/api/[^\s<>"\']+', script_text)
        api_endpoints.extend(urls)

if api_endpoints:
    print(f"\n6️⃣  Potential API endpoints found: {len(set(api_endpoints))}")
    for endpoint in list(set(api_endpoints))[:5]:
        print(f"   → {endpoint}")

print("\n" + "="*80)
print("💡 RECOMMENDATIONS:")
print("="*80)

if selects:
    print("\n✅ Page has dropdown menus - data likely loaded dynamically")
    print("   → May need Selenium to interact with dropdowns")
    print("   → Or find the API that populates the dropdown")
elif relevant_links:
    print("\n✅ Found direct links to portfolio files")
    print("   → Can scrape links directly")
else:
    print("\n⚠️  Page structure unclear - may need browser automation")
    print("   → Consider using Selenium")

if has_react or has_next:
    print("\n⚠️  Page uses modern JavaScript framework")
    print("   → Content may be rendered client-side")
    print("   → Check browser Network tab for API calls")

print("\n" + "="*80)
