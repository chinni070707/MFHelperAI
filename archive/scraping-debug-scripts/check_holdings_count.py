"""Check holdings count in original data"""
import json

with open('backend/data/fund_holdings.json', encoding='utf-8') as f:
    data = json.load(f)

# Check a few original funds
original_funds = [
    'hdfc-flexi-cap-fund',
    'hdfc-mid-cap-opportunities-fund',
    'axis-midcap-fund'
]

print("\n" + "="*60)
print("ORIGINAL 98 FUNDS - HOLDINGS COUNT")
print("="*60 + "\n")

for fund_key in original_funds:
    if fund_key in data['funds']:
        fund = data['funds'][fund_key]
        holdings_count = len(fund['holdings'])
        total_weight = sum(h['weight'] for h in fund['holdings'])
        
        print(f"{fund['name']}")
        print(f"  Holdings: {holdings_count}")
        print(f"  Total Weight: {total_weight:.1f}%")
        print(f"  Top 3:")
        for h in fund['holdings'][:3]:
            print(f"    - {h['stock']}: {h['weight']}%")
        print()

# Now check the new funds we just scraped
new_funds_sample = []
for key, value in data['funds'].items():
    if value.get('source') == 'MoneyControl Scraping':
        new_funds_sample.append(key)
        if len(new_funds_sample) >= 3:
            break

if new_funds_sample:
    print("="*60)
    print("NEW SCRAPED FUNDS - HOLDINGS COUNT")
    print("="*60 + "\n")
    
    for fund_key in new_funds_sample:
        fund = data['funds'][fund_key]
        holdings_count = len(fund['holdings'])
        total_weight = sum(h['weight'] for h in fund['holdings'])
        
        print(f"{fund['name']}")
        print(f"  Holdings: {holdings_count}")
        print(f"  Total Weight: {total_weight:.1f}%")
        print(f"  Top 3:")
        for h in fund['holdings'][:3]:
            print(f"    - {h['stock']}: {h['weight']}%")
        print()

print("="*60)
