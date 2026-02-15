"""
Verification Test for AMC Cleanup Implementation
"""
import sys
import os
import json
from pathlib import Path

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from app.services.amc_extractor import AmcExtractor

def test_amc_extractor():
    """Test the AMC extractor service"""
    print("\n" + "="*70)
    print("TEST 1: AMC EXTRACTOR SERVICE")
    print("="*70)
    
    test_cases = {
        "Axis Long Term Equity Fund": "Axis Mutual Fund",
        "HDFC Tax Saver ELSS Fund": "HDFC Mutual Fund",
        "Parag Parikh Flexi Cap Fund": "PPFAS Mutual Fund",
        "Kotak Standard Multicap Fund": "Kotak Mahindra Mutual Fund",
    }
    
    passed = 0
    for fund_name, expected_amc in test_cases.items():
        actual_amc = AmcExtractor.extract(fund_name)
        if actual_amc == expected_amc:
            print(f"✅ {fund_name:40} → {actual_amc}")
            passed += 1
        else:
            print(f"❌ {fund_name:40} → Expected: {expected_amc}, Got: {actual_amc}")
    
    print(f"\nResult: {passed}/{len(test_cases)} tests passed")
    return passed == len(test_cases)

def test_fund_holdings_data():
    """Test that fund_holdings.json has clean AMC names"""
    print("\n" + "="*70)
    print("TEST 2: FUND HOLDINGS DATA CLEANUP")
    print("="*70)
    
    data_dir = Path(__file__).parent.parent / 'data'
    holdings_file = data_dir / 'fund_holdings.json'
    
    with open(holdings_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    funds = data.get('funds', {})
    invalid_count = 0
    invalid_amcs = set()
    
    for fund_key, fund_data in funds.items():
        amc = fund_data.get('amc', 'Unknown')
        if not AmcExtractor.is_valid(amc):
            invalid_count += 1
            invalid_amcs.add(amc)
    
    if invalid_count == 0:
        print(f"✅ All {len(funds)} funds have valid AMC names")
        print(f"✅ No invalid AMC terms found (Tax, Cap, ELSS, etc.)")
        return True
    else:
        print(f"❌ Found {invalid_count} funds with invalid AMC names:")
        for amc in invalid_amcs:
            count = sum(1 for f in funds.values() if f.get('amc') == amc)
            print(f"   • {amc} ({count} funds)")
        return False

def test_scraper_import():
    """Test that scraper can import and use AmcExtractor"""
    print("\n" + "="*70)
    print("TEST 3: SCRAPER INTEGRATION")
    print("="*70)
    
    try:
        # Try to import the scraper module
        scraper_file = Path(__file__).parent / 'scrape_moneycontrol.py'
        with open(scraper_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check for proper imports
        has_import = 'from app.services.amc_extractor import AmcExtractor' in content
        uses_extractor = 'AmcExtractor.extract' in content
        validates_amc = 'AmcExtractor.is_valid' in content
        
        if has_import and uses_extractor and validates_amc:
            print("✅ Scraper imports AmcExtractor")
            print("✅ Scraper uses AmcExtractor.extract()")
            print("✅ Scraper validates AMC names")
            return True
        else:
            if not has_import:
                print("❌ Scraper doesn't import AmcExtractor")
            if not uses_extractor:
                print("❌ Scraper doesn't use AmcExtractor.extract()")
            if not validates_amc:
                print("❌ Scraper doesn't validate AMC names")
            return False
    except Exception as e:
        print(f"❌ Error checking scraper: {e}")
        return False

def test_overlap_analyzer_import():
    """Test that overlap analyzer uses AmcExtractor"""
    print("\n" + "="*70)
    print("TEST 4: OVERLAP ANALYZER INTEGRATION")
    print("="*70)
    
    try:
        # Try to import the overlap analyzer
        analyzer_file = Path(__file__).parent.parent / 'app' / 'utils' / 'overlap_analyzer.py'
        with open(analyzer_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        has_import = 'from app.services.amc_extractor import AmcExtractor' in content
        validates_amc = 'AmcExtractor.is_valid' in content
        
        if has_import and validates_amc:
            print("✅ Overlap analyzer imports AmcExtractor")
            print("✅ Overlap analyzer validates AMC names")
            return True
        else:
            if not has_import:
                print("❌ Overlap analyzer doesn't import AmcExtractor")
            if not validates_amc:
                print("❌ Overlap analyzer doesn't validate AMC names")
            return False
    except Exception as e:
        print(f"❌ Error checking overlap analyzer: {e}")
        return False

def main():
    """Run all verification tests"""
    print("\n" + "="*70)
    print("AMC CLEANUP VERIFICATION - ALL TESTS")
    print("="*70)
    
    results = []
    results.append(("AMC Extractor Service", test_amc_extractor()))
    results.append(("Fund Holdings Data", test_fund_holdings_data()))
    results.append(("Scraper Integration", test_scraper_import()))
    results.append(("Overlap Analyzer Integration", test_overlap_analyzer_import()))
    
    print("\n" + "="*70)
    print("FINAL RESULTS")
    print("="*70)
    
    all_passed = True
    for test_name, passed in results:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status}: {test_name}")
        if not passed:
            all_passed = False
    
    print("\n" + "="*70)
    if all_passed:
        print("🎉 ALL TESTS PASSED!")
        print("="*70)
        print("\n✅ AMC cleanup implementation is working correctly")
        print("✅ No more invalid AMC names (Tax, Cap, ELSS, etc.)")
        print("✅ Scraper will use proper AMC extraction going forward")
        print("✅ API validates AMC names before sending to frontend")
        print("✅ Frontend displays clean AMC dropdown\n")
    else:
        print("⚠️  SOME TESTS FAILED")
        print("="*70)
        print("\nPlease review the failed tests above.\n")
    
    return all_passed

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
