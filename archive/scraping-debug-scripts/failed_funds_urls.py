"""
Sample URLs of funds that failed - for manual inspection
"""

# Funds that had only 3-5 holdings (filtered out as incomplete)
INCOMPLETE_FUNDS = [
    {
        'name': 'DSP Flexi Cap Fund - Direct Plan - Growth',
        'url': 'https://www.moneycontrol.com/mutual-funds/dsp-flexi-cap-fund-direct-plan-growth/portfolio-holdings/MDS1023',
        'reason': 'Only 5 holdings found - likely top holdings summary, not full portfolio'
    },
    {
        'name': 'Union Flexi Cap Fund - Direct Plan - Growth',
        'url': 'https://www.moneycontrol.com/mutual-funds/union-flexi-cap-fund-direct-plan-growth/portfolio-holdings/MUK027',
        'reason': 'Only 4 holdings found'
    },
    {
        'name': 'NJ Flexi Cap Fund - Direct Plan - Growth',
        'url': 'https://www.moneycontrol.com/mutual-funds/nj-flexi-cap-fund-direct-plan-growth/portfolio-holdings/MNJA007',
        'reason': 'Only 5 holdings found'
    },
    {
        'name': 'PGIM India Flexi Cap Fund - Direct Plan - Growth',
        'url': 'https://www.moneycontrol.com/mutual-funds/pgim-india-flexi-cap-fund-direct-plan-growth/portfolio-holdings/MPA159',
        'reason': 'Only 3 holdings found'
    }
]

# Funds with no portfolio table at all
NO_PORTFOLIO_FUNDS = [
    {
        'name': 'HDFC Equity Opportunities Fund - Series II - 1126D May',
        'url': 'https://www.moneycontrol.com/mutual-funds/hdfc-equity-opportunities-fund-series-ii-1126d-may-direct-plan-growth/portfolio-holdings/MHD3073',
        'reason': 'No portfolio holdings table found - likely closed-end fund or series'
    },
    {
        'name': 'Kotak India Growth Fund - Series IV',
        'url': 'https://www.moneycontrol.com/mutual-funds/kotak-india-growth-fund-series-iv-direct-plan-growth/portfolio-holdings/MKM1087',
        'reason': 'No portfolio holdings table found'
    }
]

# Successful funds for comparison (6+ holdings)
SUCCESSFUL_FUNDS = [
    {
        'name': 'Abakkus Flexi Cap Fund - Direct Plan - Growth',
        'url': 'https://www.moneycontrol.com/mutual-funds/abakkus-flexi-cap-fund-direct-plan-growth/portfolio-holdings/MAMA005',
        'holdings': 10,
        'reason': 'Full portfolio with 10 holdings'
    },
    {
        'name': 'Motilal Oswal Focused Fund - Direct Plan - Growth',
        'url': 'https://www.moneycontrol.com/mutual-funds/motilal-oswal-focused-fund-direct-plan-growth/portfolio-holdings/MMO021',
        'holdings': 9,
        'reason': 'Full portfolio with 9 holdings'
    },
    {
        'name': 'HDFC Focused Fund - Direct Plan - Growth',
        'url': 'https://www.moneycontrol.com/mutual-funds/hdfc-focused-fund-direct-plan-growth/portfolio-holdings/MHD1188',
        'holdings': 8,
        'reason': 'Full portfolio with 8 holdings'
    }
]

print("\n" + "="*80)
print("FUND SCRAPING - SAMPLE URLS FOR MANUAL INSPECTION")
print("="*80)

print("\n📋 INCOMPLETE FUNDS (3-5 holdings - top holdings only):")
print("-" * 80)
for fund in INCOMPLETE_FUNDS:
    print(f"\n✗ {fund['name']}")
    print(f"  URL: {fund['url']}")
    print(f"  Issue: {fund['reason']}")

print("\n\n❌ NO PORTFOLIO FUNDS (no table found):")
print("-" * 80)
for fund in NO_PORTFOLIO_FUNDS:
    print(f"\n✗ {fund['name']}")
    print(f"  URL: {fund['url']}")
    print(f"  Issue: {fund['reason']}")

print("\n\n✅ SUCCESSFUL FUNDS (6+ holdings - full portfolios):")
print("-" * 80)
for fund in SUCCESSFUL_FUNDS:
    print(f"\n✓ {fund['name']}")
    print(f"  URL: {fund['url']}")
    print(f"  Holdings: {fund['holdings']} stocks")
    print(f"  Status: {fund['reason']}")

print("\n" + "="*80)
print("\n💡 KEY OBSERVATIONS:")
print("   - Funds with 3-5 holdings show only TOP holdings, not full portfolios")
print("   - These are summary pages, not detailed portfolio disclosures")
print("   - Only funds with 6+ holdings have complete portfolio data")
print("   - Series funds (closed-end) often don't have portfolio pages")
print("\n" + "="*80 + "\n")
