"""
Simple validation of fund holdings - check key metrics
"""
import json
from pathlib import Path

data_file = Path(__file__).parent.parent / 'data' / 'fund_holdings.json'

with open(data_file, encoding='utf-8', errors='replace') as f:
    data = json.load(f)

funds = data['funds']

print(f"\n{'='*80}")
print("FINAL DATA VALIDATION")
print(f"{'='*80}\n")

total_funds = len(funds)
print(f"[TOTAL] {total_funds} funds")

# Check weight distributions
issues = {
    'negative_weights': [],
    'low_total_weight': [],  # <70%
    'high_total_weight': [],  # >110%
    'no_holdings': []
}

weight_ranges = {
    '80-85%': 0,
    '85-90%': 0,
    '90-95%': 0,
    '95-100%': 0,
    '100%+': 0
}

for fund_key, fund_data in funds.items():
    holdings = fund_data['holdings']
    
    if not holdings:
        issues['no_holdings'].append(fund_data['name'])
        continue
    
    # Check for negative weights
    negative = [h for h in holdings if h['weight'] < 0]
    if negative:
        issues['negative_weights'].append({
            'name': fund_data['name'],
            'count': len(negative)
        })
    
    # Calculate total weight
    total_weight = sum(h['weight'] for h in holdings)
    
    if total_weight < 70:
        issues['low_total_weight'].append({
            'name': fund_data['name'],
            'weight': round(total_weight, 1),
            'holdings': len(holdings)
        })
    elif total_weight > 110:
        issues['high_total_weight'].append({
            'name': fund_data['name'],
            'weight': round(total_weight, 1)
        })
    
    # Weight distribution
    if 80 <= total_weight < 85:
        weight_ranges['80-85%'] += 1
    elif 85 <= total_weight < 90:
        weight_ranges['85-90%'] += 1
    elif 90 <= total_weight < 95:
        weight_ranges['90-95%'] += 1
    elif 95 <= total_weight <= 100:
        weight_ranges['95-100%'] += 1
    elif total_weight > 100:
        weight_ranges['100%+'] += 1

print(f"\n[WEIGHT DISTRIBUTION]")
for range_name, count in weight_ranges.items():
    if count > 0:
        print(f"  {range_name}: {count} funds")

print(f"\n[ISSUES FOUND]")
print(f"  Negative weights: {len(issues['negative_weights'])}")
print(f"  Low total weight (<70%): {len(issues['low_total_weight'])}")
print(f"  High total weight (>110%): {len(issues['high_total_weight'])}")
print(f"  No holdings: {len(issues['no_holdings'])}")

if issues['negative_weights']:
    print(f"\n[NEGATIVE WEIGHTS] (first 5):")
    for issue in issues['negative_weights'][:5]:
        print(f"  - {issue['name']}: {issue['count']} negative holdings")

if issues['low_total_weight']:
    print(f"\n[LOW WEIGHT] (first 5):")
    for issue in issues['low_total_weight'][:5]:
        print(f"  - {issue['name']}: {issue['weight']}% ({issue['holdings']} holdings)")

if issues['high_total_weight']:
    print(f"\n[HIGH WEIGHT] (first 5):")
    for issue in issues['high_total_weight'][:5]:
        print(f"  - {issue['name']}: {issue['weight']}%")

# Statistics
holdings_counts = [len(f['holdings']) for f in funds.values()]
avg_holdings = sum(holdings_counts) / len(holdings_counts)
min_holdings = min(holdings_counts)
max_holdings = max(holdings_counts)

print(f"\n[STATISTICS]")
print(f"  Average holdings per fund: {avg_holdings:.1f}")
print(f"  Min holdings: {min_holdings}")
print(f"  Max holdings: {max_holdings}")

# Overall verdict
total_issues = sum(len(v) for v in issues.values())
if total_issues == 0:
    print(f"\n[RESULT] ALL GOOD! No critical issues found.")
    print(f"  {total_funds} funds validated successfully!")
elif total_issues < 10:
    print(f"\n[RESULT] MOSTLY GOOD - {total_issues} minor issues found.")
else:
    print(f"\n[RESULT] NEEDS REVIEW - {total_issues} issues found.")

print(f"\n{'='*80}\n")
