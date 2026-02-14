"""
Clean fund holdings data - keep only funds with total weight > 80%
This ensures we keep complete portfolios regardless of holdings count
"""
import json
from pathlib import Path
from datetime import datetime

data_file = Path(__file__).parent.parent / 'data' / 'fund_holdings.json'

print(f"\n{'='*80}")
print("CLEANING FUND DATA BY TOTAL WEIGHT")
print(f"{'='*80}\n")

# Load current data
with open(data_file, encoding='utf-8', errors='replace') as f:
    data = json.load(f)

original_count = len(data['funds'])
print(f"[START] Original funds: {original_count}")

# Filter funds by total weight
good_funds = {}
removed_funds = []

for fund_key, fund_data in data['funds'].items():
    # Calculate total weight
    total_weight = sum(h['weight'] for h in fund_data['holdings'])
    holdings_count = len(fund_data['holdings'])
    
    if total_weight >= 80.0:
        good_funds[fund_key] = fund_data
    else:
        removed_funds.append({
            'key': fund_key,
            'name': fund_data['name'],
            'weight': round(total_weight, 1),
            'holdings': holdings_count
        })

print(f"[FILTER] Kept funds with ≥80% weight: {len(good_funds)}")
print(f"[FILTER] Removed funds with <80% weight: {len(removed_funds)}")

# Show some removed funds
if removed_funds:
    print(f"\n[REMOVED SAMPLES] (first 10):")
    for rf in sorted(removed_funds, key=lambda x: x['weight'])[:10]:
        print(f"  ✗ {rf['name']}")
        print(f"    Weight: {rf['weight']}% | Holdings: {rf['holdings']}")

# Update data
data['funds'] = good_funds
data['last_updated'] = datetime.now().strftime('%Y-%m-%d')
data['source'] = 'MoneyControl (Complete Portfolios ≥80% weight)'
data['version'] = '2026-02'

# Save cleaned data
with open(data_file, 'w', encoding='utf-8') as f:
    json.dump(data, f, indent=2, ensure_ascii=False)

print(f"\n[SAVED] Updated fund_holdings.json")
print(f"  Total funds: {len(good_funds)}")
print(f"  Removed: {len(removed_funds)} incomplete funds")

# Distribution
weight_ranges = {
    '80-85%': sum(1 for f in good_funds.values() if 80 <= sum(h['weight'] for h in f['holdings']) < 85),
    '85-90%': sum(1 for f in good_funds.values() if 85 <= sum(h['weight'] for h in f['holdings']) < 90),
    '90-95%': sum(1 for f in good_funds.values() if 90 <= sum(h['weight'] for h in f['holdings']) < 95),
    '95-100%': sum(1 for f in good_funds.values() if 95 <= sum(h['weight'] for h in f['holdings']) <= 100),
    '100+%': sum(1 for f in good_funds.values() if sum(h['weight'] for h in f['holdings']) > 100),
}

print(f"\n[WEIGHT DISTRIBUTION]")
for range_name, count in weight_ranges.items():
    if count > 0:
        print(f"  {range_name}: {count} funds")

print(f"\n{'='*80}\n")
