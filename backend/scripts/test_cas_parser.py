"""
Test CAS PDF parsing using casparser library
"""
import sys
import os
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

import casparser
from datetime import datetime


def parse_cas_with_casparser(pdf_path, password=None):
    """Parse CAS PDF using the casparser library"""
    
    print(f"📄 Opening CAS PDF: {pdf_path}")
    
    try:
        # Parse CAS file
        cas_data = casparser.read_cas_pdf(
            pdf_path, 
            password=password,
            output="dict"  # Get dictionary output instead of JSON
        )
        
        print("✅ CAS PDF parsed successfully!")
        print()
        
        # Extract basic info
        print("="*70)
        print("📋 CAS STATEMENT DETAILS")
        print("="*70)
        print(f"Statement Period: {cas_data.get('statement_period', {}).get('from')} to {cas_data.get('statement_period', {}).get('to')}")
        print(f"File Type: {cas_data.get('file_type', 'N/A')}")
        print(f"CAS Type: {cas_data.get('cas_type', 'N/A')}")
        
        # Investor info
        investor_info = cas_data.get('investor_info', {})
        print(f"\nInvestor: {investor_info.get('name', 'N/A')}")
        print(f"Email: {investor_info.get('email', 'N/A')}")
        print(f"Mobile: {investor_info.get('mobile', 'N/A')}")
        
        # Parse folios and schemes
        folios = cas_data.get('folios', [])
        print(f"\n📁 Total Folios: {len(folios)}")
        
        all_holdings = []
        total_current_value = 0
        total_invested = 0
        
        for folio in folios:
            amc = folio.get('amc', 'Unknown AMC')
            folio_number = folio.get('folio', 'N/A')
            pan = folio.get('PAN', 'N/A')
            
            print(f"\n  Folio: {folio_number} | AMC: {amc} | PAN: {pan}")
            
            schemes = folio.get('schemes', [])
            
            for scheme in schemes:
                scheme_name = scheme.get('scheme', 'Unknown Scheme')
                advisor = scheme.get('advisor', '')
                isin = scheme.get('isin', '')
                
                # Get closing balance
                close_data = scheme.get('close', 0)
                if isinstance(close_data, dict):
                    close_units = close_data.get('units', 0)
                    close_value = close_data.get('value', 0)
                    close_nav = close_data.get('nav', 0)
                else:
                    close_units = close_data
                    close_value = 0
                    close_nav = 0
                
                # Calculate invested amount from transactions
                transactions = scheme.get('transactions', [])
                invested = 0
                for txn in transactions:
                    txn_type = txn.get('type', '').upper()
                    amount = txn.get('amount', 0)
                    
                    if 'PURCHASE' in txn_type or 'SWITCH' in txn_type and amount > 0:
                        invested += amount
                    elif 'REDEMPTION' in txn_type or 'SWITCH' in txn_type and amount < 0:
                        invested += amount  # Negative for redemptions
                
                if close_units > 0:  # Only include schemes with holdings
                    holding = {
                        "fund_name": scheme_name,
                        "amc": amc,
                        "folio": folio_number,
                        "advisor": advisor,
                        "isin": isin,
                        "units": close_units,
                        "nav": close_nav,
                        "current_value": close_value,
                        "invested": abs(invested),
                        "gain": close_value - abs(invested),
                        "return_pct": ((close_value - abs(invested)) / abs(invested) * 100) if invested != 0 else 0
                    }
                    
                    all_holdings.append(holding)
                    total_current_value += close_value
                    total_invested += abs(invested)
                    
                    print(f"    ✓ {scheme_name[:50]}")
                    print(f"      Units: {close_units:,.2f} | NAV: ₹{close_nav:.2f} | Value: ₹{close_value:,.2f}")
                    if invested:
                        print(f"      Invested: ₹{abs(invested):,.2f} | Gain: ₹{holding['gain']:,.2f} ({holding['return_pct']:.2f}%)")
        
        return {
            "investor_info": investor_info,
            "statement_period": cas_data.get('statement_period', {}),
            "holdings": all_holdings,
            "summary": {
                "total_folios": len(folios),
                "total_schemes": len(all_holdings),
                "total_invested": total_invested,
                "total_current": total_current_value,
                "total_gain": total_current_value - total_invested,
                "return_pct": ((total_current_value - total_invested) / total_invested * 100) if total_invested > 0 else 0
            }
        }
        
    except Exception as e:
        print(f"❌ Error parsing CAS PDF: {e}")
        import traceback
        traceback.print_exc()
        return None


def main():
    # Test with real CAS PDF
    pdf_path = r"C:\Users\mahchi01\Downloads\CAS_DEC2025_AA01244995_TXN.pdf"
    password = "YOUR_CAS_PASSWORD"
    
    print("="*70)
    print("🔍 Testing CAS PDF Parser (using casparser library)")
    print("="*70)
    print()
    
    result = parse_cas_with_casparser(pdf_path, password)
    
    if result:
        print("\n" + "="*70)
        print("📊 PORTFOLIO SUMMARY")
        print("="*70)
        summary = result['summary']
        print(f"Total Folios: {summary['total_folios']}")
        print(f"Total Schemes: {summary['total_schemes']}")
        print(f"Total Invested: ₹{summary['total_invested']:,.2f}")
        print(f"Current Value: ₹{summary['total_current']:,.2f}")
        print(f"Total Gain: ₹{summary['total_gain']:,.2f}")
        print(f"Return %: {summary['return_pct']:.2f}%")
        
        print("\n" + "="*70)
        print("🎯 TOP 5 HOLDINGS BY VALUE")
        print("="*70)
        
        # Sort by current value
        top_holdings = sorted(result['holdings'], key=lambda x: x['current_value'], reverse=True)[:5]
        
        for i, holding in enumerate(top_holdings, 1):
            print(f"\n{i}. {holding['fund_name']}")
            print(f"   AMC: {holding['amc']}")
            print(f"   Folio: {holding['folio']}")
            print(f"   Units: {holding['units']:,.2f} @ ₹{holding['nav']:.2f}")
            print(f"   Value: ₹{holding['current_value']:,.2f}")
            print(f"   Invested: ₹{holding['invested']:,.2f}")
            print(f"   Gain: ₹{holding['gain']:,.2f} ({holding['return_pct']:.2f}%)")
        
        print("\n" + "="*70)
        print("✅ CAS PARSING SUCCESSFUL!")
        print("="*70)
        print("\n💡 This data can now be saved to the database")
        print("   Use: POST /api/upload/cas with this CAS file")
        
    else:
        print("\n❌ Failed to parse CAS PDF")


if __name__ == "__main__":
    main()
