"""
Test Asset Class Classifier

Run this to verify asset classification logic works correctly.
"""

import sys
sys.path.append('backend')

from app.services.asset_classifier import AssetClassifier


def test_asset_classifier():
    """Test asset class classification"""
    
    print("\n" + "="*70)
    print("TESTING ASSET CLASS CLASSIFIER")
    print("="*70)
    
    # Test cases: (category, fund_name, expected_class)
    test_cases = [
        # Equity
        ("Large Cap", "HDFC Top 100 Fund", "Equity"),
        ("Mid Cap", "Axis Midcap Fund", "Equity"),
        ("Small Cap", "Nippon India Small Cap Fund", "Equity"),
        ("Flexi Cap", "Parag Parikh Flexi Cap Fund", "Equity"),
        ("ELSS", "Axis Long Term Equity Fund", "Equity"),
        ("Sectoral", "ICICI Prudential Banking Fund", "Equity"),
        
        # Debt
        ("Liquid", "HDFC Liquid Fund", "Debt"),
        ("Ultra Short Duration", "ICICI Prudential Ultra Short Term Fund", "Debt"),
        ("Corporate Bond", "Axis Corporate Debt Fund", "Debt"),
        ("Gilt", "HDFC Gilt Fund", "Debt"),
        ("Dynamic Bond", "ICICI Prudential Dynamic Bond Fund", "Debt"),
        ("Short Duration", "SBI Short Term Debt Fund", "Debt"),
        
        # Hybrid
        ("Hybrid", "HDFC Balanced Advantage Fund", "Hybrid"),
        ("Aggressive Hybrid", "ICICI Prudential Equity & Debt Fund", "Hybrid"),
        ("Conservative Hybrid", "HDFC Hybrid Debt Fund", "Hybrid"),
        ("Arbitrage", "Kotak Equity Arbitrage Fund", "Hybrid"),
        
        # Commodity
        ("ETF", "HDFC Gold ETF", "Commodity"),
        ("ETF", "SBI ETF Gold", "Commodity"),
        ("ETF", "ICICI Prudential Silver ETF", "Commodity"),
        ("International", "ABCD Gold Fund", "Commodity"),
        
        # Edge cases
        (None, "Some Unknown Fund", "Equity"),  # Default
        ("", "Another Fund", "Equity"),  # Default
    ]
    
    print("\n📊 Test Results:\n")
    
    passed = 0
    failed = 0
    
    for category, fund_name, expected in test_cases:
        result = AssetClassifier.classify(category, fund_name)
        status = "✓" if result == expected else "✗"
        
        if result == expected:
            passed += 1
        else:
            failed += 1
            
        print(f"{status} {fund_name[:45]:45s} | Cat: {str(category)[:20]:20s} | "
              f"Expected: {expected:10s} | Got: {result:10s}")
    
    print("\n" + "="*70)
    print(f"RESULTS: {passed} passed, {failed} failed out of {len(test_cases)} tests")
    print("="*70)
    
    # Test helper functions
    print("\n🎨 Color & Icon Mapping:\n")
    for asset_class in ['Equity', 'Debt', 'Hybrid', 'Commodity', 'Other']:
        color = AssetClassifier.get_asset_class_color(asset_class)
        icon = AssetClassifier.get_asset_class_icon(asset_class)
        risk = AssetClassifier.get_risk_profile(asset_class)
        print(f"{icon} {asset_class:12s} | Color: {color:10s} | Risk: {risk}")
    
    return passed, failed


if __name__ == "__main__":
    passed, failed = test_asset_classifier()
    
    print("\n" + "="*70)
    if failed == 0:
        print("✅ ALL TESTS PASSED!")
    else:
        print(f"⚠️  {failed} TEST(S) FAILED - Review classification logic")
    print("="*70)
    
    print("\nNext steps:")
    print("1. Run migration: python backend/scripts/migrate_add_asset_class.py")
    print("2. Test CAS import with real data")
    print("3. Verify frontend filters work correctly")
    print("="*70 + "\n")
