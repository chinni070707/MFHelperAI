import sys
sys.path.insert(0, 'backend')

from app.utils.overlap_analyzer import OverlapAnalyzer

# Test the analyzer
analyzer = OverlapAnalyzer()
funds = analyzer.get_fund_list()

print(f"✅ Successfully loaded {len(funds)} funds")

if funds:
    print(f"\nSample fund: {funds[0]['name']}")
    print(f"AMC: {funds[0]['amc']}")
    print(f"Holdings: {funds[0]['holdings_count']}")
    
    # Test pairwise overlap
    if len(funds) >= 2:
        print(f"\n🔬 Testing overlap analysis...")
        result = analyzer.calculate_pairwise_overlap([funds[0]['key'], funds[1]['key']])
        if result:
            overlap = result[0]
            print(f"Overlap between {overlap['fund1']['name']} and {overlap['fund2']['name']}")
            print(f"Overlap percentage: {overlap['overlap_percentage']}%")
            print(f"Common stocks: {overlap['common_stocks_count']}")
            print(f"Risk level: {overlap['risk_level']}")
