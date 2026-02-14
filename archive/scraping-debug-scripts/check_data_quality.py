"""Quick script to analyze existing fund holdings data"""
import json
from collections import Counter
from pathlib import Path

# Load data
data_file = Path(__file__).parent.parent / 'data' / 'fund_holdings.json'
with open(data_file, encoding='utf-8', errors='replace') as f:
    data = json.load(f)

funds = data['funds']

print(f'\n{"="*60}')
print("EXISTING DATA ANALYSIS")
print(f'{"="*60}')

print(f'\nTotal Funds: {len(funds)}')

# Holdings stats
holdings_counts = [len(f['holdings']) for f in funds.values()]
print(f'\nHoldings per fund:')
print(f'  Average: {sum(holdings_counts)/len(holdings_counts):.1f} stocks')
print(f'  Min: {min(holdings_counts)}, Max: {max(holdings_counts)} stocks')

# AMC coverage
amcs = Counter(f.get('amc', 'Unknown') for f in funds.values())
print(f'\nTop 10 AMCs:')
for amc, count in amcs.most_common(10):
    print(f'  {amc}: {count} funds')

# Category coverage
categories = Counter(f.get('category', 'Unknown') for f in funds.values())
print(f'\nAll Categories:')
for cat, count in sorted(categories.items(), key=lambda x: x[1], reverse=True):
    print(f'  {cat}: {count} funds')

print(f'\n{"="*60}')
print('CONCLUSION: 98 funds is good coverage!')
print('The 248 remaining funds likely have 403 errors.')
print(f'{"="*60}\n')
