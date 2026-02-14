"""Verify fund_holdings.json is accessible and valid"""
from pathlib import Path
import json

# Find the file
file_path = Path(__file__).parent.parent / 'data' / 'fund_holdings.json'

print("\n" + "="*60)
print("FUND HOLDINGS DATA VERIFICATION")
print("="*60)

# Load and check
try:
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    funds = data.get('funds', {})
    
    print(f"\n✅ File found: {file_path}")
    print(f"✅ Valid JSON format")
    print(f"✅ Contains {len(funds)} funds")
    print(f"✅ Last updated: {data.get('last_updated', 'N/A')}")
    
    # Sample fund
    sample = list(funds.values())[0]
    print(f"\n📊 Sample Fund:")
    print(f"   Name: {sample['name']}")
    print(f"   AMC: {sample['amc']}")
    print(f"   Category: {sample['category']}")
    print(f"   Holdings: {len(sample['holdings'])} stocks")
    print(f"   Top holding: {sample['holdings'][0]['stock']} ({sample['holdings'][0]['weight']}%)")
    
    print(f"\n🎯 STATUS: Ready for use by overlap analyzer!")
    print("="*60 + "\n")
    
except Exception as e:
    print(f"\n❌ ERROR: {e}")
    print("="*60 + "\n")
