"""
Test CAS PDF import with real file
Uses casparser library - a robust CAS parsing solution
"""
import sys
from pathlib import Path

# Test if casparser is installed
try:
    import casparser
    print("✅ casparser is installed")
except ImportError:
    print("❌ casparser not found. Installing...")
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "casparser"])
    import casparser
    print("✅ casparser installed successfully")

def test_cas_import(cas_file_path: str, password: str):
    """Test CAS import using casparser library"""
    print(f"\n{'='*70}")
    print(f"Testing CAS Import: {cas_file_path}")
    print(f"{'='*70}\n")
    
    try:
        # Parse CAS PDF
        print("📄 Parsing CAS PDF...")
        cas_data = casparser.read_cas_pdf(cas_file_path, password)
        
        print(f"✅ CAS parsed successfully!")
        print(f"\n📊 Summary:")
        print(f"   Statement Period: {cas_data['statement_period']['from']} to {cas_data['statement_period']['to']}")
        print(f"   Investor: {cas_data['investor_info'].get('name', 'N/A')}")
        print(f"   Email: {cas_data['investor_info'].get('email', 'N/A')}")
        print(f"   PAN: {cas_data['investor_info'].get('pan', 'N/A')}")
        
        # Count folios and schemes
        total_folios = 0
        total_schemes = 0
        total_valuation = 0
        
        print(f"\n🏦 AMCs and Folios:")
        for folio in cas_data['folios']:
            total_folios += 1
            amc = folio.get('amc', 'Unknown AMC')
            folio_number = folio.get('folio', 'N/A')
            pan = folio.get('PAN', 'N/A')
            
            print(f"\n   AMC: {amc}")
            print(f"   Folio: {folio_number} | PAN: {pan}")
            
            for scheme in folio['schemes']:
                total_schemes += 1
                scheme_name = scheme['scheme']
                advisor = scheme.get('advisor', 'N/A')
                
                # Get current valuation
                valuation = scheme.get('valuation', {})
                current_value = valuation.get('value', 0)
                nav = valuation.get('nav', 0)
                units = valuation.get('units', 0)
                
                total_valuation += current_value if current_value else 0
                
                print(f"      └─ {scheme_name[:60]}")
                print(f"         Units: {units:.4f} | NAV: ₹{nav:.2f} | Value: ₹{current_value:,.2f}")
                
                # Show transactions if any
                if scheme.get('transactions'):
                    print(f"         Transactions: {len(scheme['transactions'])}")
        
        print(f"\n{'='*70}")
        print(f"📈 Total Summary:")
        print(f"   Total AMCs: {len(cas_data['folios'])}")
        print(f"   Total Folios: {total_folios}")
        print(f"   Total Schemes: {total_schemes}")
        print(f"   Total Current Value: ₹{total_valuation:,.2f}")
        print(f"{'='*70}\n")
        
        # Convert to MFHelper format
        holdings = []
        
        for folio in cas_data['folios']:
            amc = folio.get('amc', 'Unknown AMC')
            
            for scheme in folio['schemes']:
                valuation = scheme.get('valuation', {})
                
                # Calculate invested amount from transactions
                invested_amount = 0
                for txn in scheme.get('transactions', []):
                    if txn.get('type') in ['purchase_sip', 'purchase_lumpsum', 'purchase']:
                        invested_amount += txn.get('amount', 0)
                    elif txn.get('type') in ['redemption']:
                        invested_amount -= txn.get('amount', 0)
                
                current_value = valuation.get('value', 0)
                
                if current_value > 0:
                    holding = {
                        'fund_name': scheme['scheme'],
                        'amc': amc,
                        'folio': folio.get('folio', ''),
                        'category': determine_category_from_name(scheme['scheme']),
                        'isin': scheme.get('isin', ''),
                        'units': valuation.get('units', 0),
                        'nav': valuation.get('nav', 0),
                        'invested': invested_amount if invested_amount > 0 else current_value,
                        'current_value': current_value,
                        'gain': current_value - (invested_amount if invested_amount > 0 else current_value),
                        'return_pct': ((current_value - invested_amount) / invested_amount * 100) if invested_amount > 0 else 0
                    }
                    holdings.append(holding)
        
        print(f"✅ Converted to {len(holdings)} holdings for MFHelper format\n")
        
        # Show sample holdings
        print("📋 Sample Holdings (first 3):")
        for i, h in enumerate(holdings[:3], 1):
            print(f"\n   {i}. {h['fund_name'][:60]}")
            print(f"      AMC: {h['amc']}")
            print(f"      Category: {h['category']}")
            print(f"      Invested: ₹{h['invested']:,.2f} | Current: ₹{h['current_value']:,.2f}")
            print(f"      Gain: ₹{h['gain']:,.2f} ({h['return_pct']:.2f}%)")
        
        # Calculate summary
        summary = {
            'total_funds': len(holdings),
            'total_invested': sum(h['invested'] for h in holdings),
            'total_current': sum(h['current_value'] for h in holdings),
            'total_gain': sum(h['gain'] for h in holdings)
        }
        
        print(f"\n📊 Portfolio Summary:")
        print(f"   Total Funds: {summary['total_funds']}")
        print(f"   Total Invested: ₹{summary['total_invested']:,.2f}")
        print(f"   Total Current: ₹{summary['total_current']:,.2f}")
        print(f"   Total Gain: ₹{summary['total_gain']:,.2f}")
        print(f"   Return %: {(summary['total_gain']/summary['total_invested']*100):.2f}%")
        
        return {
            'success': True,
            'cas_data': cas_data,
            'holdings': holdings,
            'summary': summary
        }
        
    except Exception as e:
        print(f"\n❌ Error parsing CAS: {e}")
        import traceback
        traceback.print_exc()
        return {'success': False, 'error': str(e)}


def determine_category_from_name(scheme_name: str) -> str:
    """Determine fund category from scheme name"""
    name_lower = scheme_name.lower()
    
    if any(word in name_lower for word in ['large cap', 'blue chip', 'top 100', 'nifty 50', 'sensex']):
        return 'Large Cap'
    elif any(word in name_lower for word in ['mid cap', 'midcap', 'mid-cap']):
        return 'Mid Cap'
    elif any(word in name_lower for word in ['small cap', 'smallcap', 'small-cap']):
        return 'Small Cap'
    elif any(word in name_lower for word in ['flexi cap', 'flexicap', 'multi cap', 'multicap']):
        return 'Flexi Cap'
    elif any(word in name_lower for word in ['large & mid', 'large and mid']):
        return 'Large & Mid Cap'
    elif any(word in name_lower for word in ['elss', 'tax saver', 'tax saving']):
        return 'ELSS'
    elif any(word in name_lower for word in ['focused', 'focus']):
        return 'Focused'
    elif any(word in name_lower for word in ['debt', 'bond', 'income', 'credit']):
        return 'Debt'
    elif any(word in name_lower for word in ['liquid', 'money market', 'overnight']):
        return 'Liquid'
    elif any(word in name_lower for word in ['balanced', 'hybrid', 'aggressive']):
        return 'Hybrid'
    elif any(word in name_lower for word in ['index', 'nifty', 'sensex']):
        return 'Index'
    elif any(word in name_lower for word in ['international', 'global', 'foreign']):
        return 'International'
    else:
        return 'Other'


if __name__ == "__main__":
    # Test with the provided CAS file
    cas_file = r"C:\Users\mahchi01\Downloads\CAS_DEC2025_AA01244995_TXN.pdf"
    password = "AOLPC2904E"
    
    if Path(cas_file).exists():
        result = test_cas_import(cas_file, password)
        
        if result['success']:
            print("\n✅ CAS import test completed successfully!")
            print("\n💡 Next steps:")
            print("   1. Integrate casparser into upload.py")
            print("   2. Update /api/upload/cas endpoint")
            print("   3. Add CAS parsing to frontend")
        else:
            print(f"\n❌ Test failed: {result.get('error')}")
    else:
        print(f"❌ File not found: {cas_file}")
