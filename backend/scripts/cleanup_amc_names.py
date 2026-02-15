"""
Clean up AMC names in fund_holdings.json

Fixes polluted AMC names (Tax, Cap, ELSS, etc.) by re-extracting from fund names
using the proper AmcExtractor service.
"""
import json
import sys
import os
from pathlib import Path
from datetime import datetime

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from app.services.amc_extractor import AmcExtractor

def cleanup_amc_names():
    """Clean up AMC names in fund_holdings.json"""
    
    # File paths
    data_dir = Path(__file__).parent.parent / 'data'
    holdings_file = data_dir / 'fund_holdings.json'
    backup_file = data_dir / f'fund_holdings_backup_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
    
    print("\n" + "="*70)
    print("AMC NAME CLEANUP SCRIPT")
    print("="*70)
    
    # Check if file exists
    if not holdings_file.exists():
        print(f"\n❌ Error: {holdings_file} not found!")
        return
    
    # Load existing data
    print(f"\n📂 Loading {holdings_file}")
    with open(holdings_file, 'r', encoding='utf-8') as f:
        full_data = json.load(f)
    
    # Extract funds dictionary
    data = full_data.get('funds', {})
    
    print(f"✅ Loaded {len(data)} funds")
    
    # Create backup
    print(f"\n💾 Creating backup: {backup_file.name}")
    with open(backup_file, 'w', encoding='utf-8') as f:
        json.dump(full_data, f, indent=2)
    print("✅ Backup created")
    
    # Analyze and fix AMC names
    print("\n" + "="*70)
    print("ANALYZING AMC NAMES")
    print("="*70)
    
    changes = []
    invalid_amcs = set()
    valid_amcs = set()
    
    for fund_key, fund_data in data.items():
        old_amc = fund_data.get('amc', 'Unknown')
        fund_name = fund_data.get('name', '')
        
        # Extract proper AMC name
        new_amc = AmcExtractor.extract(fund_name)
        
        # Check if AMC changed
        if old_amc != new_amc:
            changes.append({
                'fund': fund_name,
                'old_amc': old_amc,
                'new_amc': new_amc
            })
            
            # Track invalid AMCs
            if not AmcExtractor.is_valid(old_amc):
                invalid_amcs.add(old_amc)
        
        # Update fund data
        fund_data['amc'] = new_amc
        
        # Track all valid AMCs
        if AmcExtractor.is_valid(new_amc):
            valid_amcs.add(new_amc)
    
    # Report findings
    print(f"\n📊 Summary:")
    print(f"  • Total funds: {len(data)}")
    print(f"  • Changes needed: {len(changes)}")
    print(f"  • Invalid AMCs found: {len(invalid_amcs)}")
    print(f"  • Valid AMCs after cleanup: {len(valid_amcs)}")
    
    if invalid_amcs:
        print(f"\n❌ Invalid AMCs that were found:")
        for amc in sorted(invalid_amcs):
            count = sum(1 for c in changes if c['old_amc'] == amc)
            print(f"  • {amc} ({count} funds)")
    
    if changes:
        print(f"\n🔧 Changes made:")
        print("-" * 70)
        for i, change in enumerate(changes[:20], 1):  # Show first 20
            print(f"{i:2}. {change['fund'][:50]:50} | {change['old_amc']:20} → {change['new_amc']}")
        
        if len(changes) > 20:
            print(f"... and {len(changes) - 20} more changes")
    
    # Save cleaned data
    print(f"\n💾 Saving cleaned data to {holdings_file}")
    full_data['funds'] = data
    with open(holdings_file, 'w', encoding='utf-8') as f:
        json.dump(full_data, f, indent=2)
    
    print("✅ Data saved successfully!")
    
    # Show valid AMCs
    print(f"\n✅ Valid AMCs in dataset ({len(valid_amcs)}):")
    for amc in sorted(valid_amcs):
        count = sum(1 for f in data.values() if f.get('amc') == amc)
        print(f"  • {amc:40} ({count} funds)")
    
    print("\n" + "="*70)
    print("CLEANUP COMPLETE!")
    print("="*70)
    print(f"\n✅ Original file backed up to: {backup_file.name}")
    print(f"✅ Cleaned file saved to: {holdings_file.name}")
    print(f"✅ {len(changes)} AMC names corrected")
    print()

if __name__ == '__main__':
    try:
        cleanup_amc_names()
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
