import requests
from bs4 import BeautifulSoup

url = "https://www.moneycontrol.com/mutual-funds/hdfc-flexi-cap-fund-direct-plan-growth/portfolio-holdings/MHD1144"
response = requests.get(url, headers={"User-Agent": "Mozilla/5.0"})
soup = BeautifulSoup(response.text, "html.parser")

tables = soup.find_all("table")
holdings_table = tables[4]
rows = holdings_table.find_all("tr")

print(f"Scraping HDFC Flexi Cap Fund")
print(f"Found {len(rows)} rows\n")

holdings = []
for row in rows[1:]:
    cols = row.find_all("td")
    if len(cols) < 5:
        continue
    
    stock = cols[0].get_text(strip=True)
    sector = cols[1].get_text(strip=True)
    weight_text = cols[4].get_text(strip=True)
    
    try:
        weight = float(weight_text.replace("%", "").replace(",", ""))
    except:
        continue
    
    if weight > 0.1 and stock:
        holdings.append({"stock": stock, "sector": sector, "weight": weight})

print(f"Extracted {len(holdings)} holdings\n")
print("Top 10:")
for i, h in enumerate(holdings[:10], 1):
    print(f'  {i}. {h["stock"]}: {h["weight"]}% ({h["sector"]})')
