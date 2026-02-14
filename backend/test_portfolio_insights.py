"""
Test script for Fund Classifier and Portfolio Insights

Run this to verify the classification logic works correctly.
"""

import sys
sys.path.append('backend')

from app.services.fund_classifier import FundClassifier, PortfolioInsightsGenerator


def test_investment_style():
    """Test investment style inference"""
    print("\n" + "="*60)
    print("TESTING INVESTMENT STYLE INFERENCE")
    print("="*60)
    
    test_cases = [
        ("HDFC Growth Fund", "Large Cap", "Growth"),
        ("SBI Contra Fund", "Large Cap", "Value"),
        ("ICICI Momentum Fund", "Multi Cap", "Momentum"),
        ("Axis Bluechip Fund", "Large Cap", "Value"),
        ("Parag Parikh Flexi Cap Fund", "Flexi Cap", "GARP"),
        ("Mirae Asset Large Cap Fund", "Large Cap", "Diversified"),
        ("Nippon India Banking Fund", "Sectoral", "Sectoral"),
    ]
    
    for fund_name, category, expected in test_cases:
        result = FundClassifier.infer_investment_style(fund_name, category)
        status = "✓" if result == expected else "✗"
        print(f"{status} {fund_name:40s} -> {result:15s} (expected: {expected})")


def test_market_cap_distribution():
    """Test market cap distribution estimation"""
    print("\n" + "="*60)
    print("TESTING MARKET CAP DISTRIBUTION")
    print("="*60)
    
    categories = [
        "Large Cap",
        "Mid Cap", 
        "Small Cap",
        "Flexi Cap",
        "Multi Cap",
        "ELSS",
        "Large & Mid Cap"
    ]
    
    for category in categories:
        dist = FundClassifier.estimate_market_cap_distribution(category)
        print(f"\n{category}:")
        print(f"  Large: {dist['large']*100:.0f}%  |  Mid: {dist['mid']*100:.0f}%  |  Small: {dist['small']*100:.0f}%")


def test_amc_concentration():
    """Test AMC concentration analysis"""
    print("\n" + "="*60)
    print("TESTING AMC CONCENTRATION ANALYSIS")
    print("="*60)
    
    # Sample portfolio with AMC concentration
    holdings = [
        {"amc": "HDFC Mutual Fund", "current_value": 500000, "fund_name": "HDFC Large Cap"},
        {"amc": "HDFC Mutual Fund", "current_value": 300000, "fund_name": "HDFC Mid Cap"},
        {"amc": "HDFC Mutual Fund", "current_value": 200000, "fund_name": "HDFC Flexi Cap"},
        {"amc": "SBI Mutual Fund", "current_value": 150000, "fund_name": "SBI Bluechip"},
        {"amc": "ICICI Prudential Mutual Fund", "current_value": 100000, "fund_name": "ICICI Value"},
    ]
    
    result = PortfolioInsightsGenerator.analyze_amc_concentration(holdings)
    
    print(f"\nTotal AMCs: {result['total_amcs']}")
    print(f"Concentration Risk: {result['concentration_risk'].upper()}")
    print(f"Message: {result['risk_message']}")
    print("\nTop AMCs:")
    for amc in result['top_amcs']:
        print(f"  {amc['name']:30s} {amc['percentage']:5.1f}%  (₹{amc['value']:,.0f})")


def test_investment_style_analysis():
    """Test investment style distribution analysis"""
    print("\n" + "="*60)
    print("TESTING INVESTMENT STYLE ANALYSIS")
    print("="*60)
    
    holdings = [
        {"fund_name": "HDFC Growth Fund", "category": "Large Cap", "current_value": 300000},
        {"fund_name": "SBI Contra Fund", "category": "Large Cap", "current_value": 250000},
        {"fund_name": "ICICI Momentum Fund", "category": "Multi Cap", "current_value": 200000},
        {"fund_name": "Axis Bluechip Fund", "category": "Large Cap", "current_value": 150000},
        {"fund_name": "Parag Parikh Flexi Cap", "category": "Flexi Cap", "current_value": 100000},
    ]
    
    result = PortfolioInsightsGenerator.analyze_investment_style(holdings)
    
    print(f"\nDominant Style: {result['dominant_style']}")
    print(f"Diversification Score: {result['diversification_score']}/100")
    print("\nStyle Distribution:")
    for style, percentage in result['style_distribution'].items():
        print(f"  {style:15s} {percentage:5.1f}%")


def test_market_cap_allocation():
    """Test market cap allocation analysis"""
    print("\n" + "="*60)
    print("TESTING MARKET CAP ALLOCATION")
    print("="*60)
    
    holdings = [
        {"category": "Large Cap", "current_value": 400000},
        {"category": "Mid Cap", "current_value": 300000},
        {"category": "Small Cap", "current_value": 200000},
        {"category": "Flexi Cap", "current_value": 100000},
    ]
    
    result = PortfolioInsightsGenerator.analyze_market_cap_allocation(holdings)
    
    print(f"\nLarge Cap: {result['large_cap_pct']}%")
    print(f"Mid Cap: {result['mid_cap_pct']}%")
    print(f"Small Cap: {result['small_cap_pct']}%")
    print(f"\nRisk Profile: {result['risk_profile']}")
    print(f"Balanced: {'Yes ✓' if result['is_balanced'] else 'No ✗'}")
    print(f"\nRecommendation: {result['recommendation']}")
    print(f"Methodology: {result['methodology']}")


if __name__ == "__main__":
    print("\n" + "="*60)
    print("PORTFOLIO INSIGHTS - CLASSIFICATION TEST SUITE")
    print("="*60)
    
    test_investment_style()
    test_market_cap_distribution()
    test_amc_concentration()
    test_investment_style_analysis()
    test_market_cap_allocation()
    
    print("\n" + "="*60)
    print("ALL TESTS COMPLETED")
    print("="*60)
    print("\nNext steps:")
    print("1. Start the backend server")
    print("2. Navigate to /risk-analyzer.html")
    print("3. Log in or use guest data")
    print("4. Verify the new insights cards display correctly")
    print("="*60 + "\n")
