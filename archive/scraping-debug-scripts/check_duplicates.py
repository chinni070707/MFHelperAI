"""
Check for duplicate funds and data quality issues
"""
import json
from pathlib import Path
from collections import Counter

data_file = Path(__file__).parent.parent / 'data' / 'fund_holdings.json'

with open(data_file, encoding='utf-8', errors='replace') as f:
    data = json.load(f)

funds = data['funds']

print(f"\n{'='*80}")
print("DUPLICATE & QUALITY CHECK")
print(f"{'='*80}\n")

# Check for duplicates by fund name
fund_names = [f['name'] for f in funds.values()]
name_counts = Counter(fund_names)
duplicates = {name: count for name, count in name_counts.items() if count > 1}

if duplicates:
    print(f"[DUPLICATES] Found {len(duplicates)} duplicate fund names:\n")
    for name, count in sorted(duplicates.items(), key=lambda x: -x[1])[:20]:
        print(f"  {count}x: {name}")
        # Find the fund keys
        keys = [k for k, v in funds.items() if v['name'] == name]
        print(f"      Keys: {', '.join(keys[:5])}")
        # Check holdings count for each
        holdings_counts = [len(v['holdings']) for k, v in funds.items() if v['name'] == name]
        print(f"      Holdings: {holdings_counts}")
        print()
else:
    print("[OK] No duplicate fund names found")

# Check holdings distribution
print(f"\n[HOLDINGS DISTRIBUTION]")
holdings_counts = [len(f['holdings']) for f in funds.values()]
holdings_dist = Counter(holdings_counts)

print(f"Funds with < 15 holdings (likely incomplete): {sum(count for h, count in holdings_dist.items() if h < 15)}")
print(f"Funds with 15-40 holdings (good): {sum(count for h, count in holdings_dist.items() if 15 <= h < 40)}")
print(f"Funds with 40+ holdings (excellent): {sum(count for h, count in holdings_dist.items() if h >= 40)}")

print(f"\n[RECOMMENDATION]")
print(f"- Total funds: {len(funds)}")
print(f"- Should check for duplicates and remove lower quality versions")
print(f"- Expected: ~200-300 unique funds with complete portfolios")

print(f"\n{'='*80}\n")
