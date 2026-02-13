"""
Quick test script to parse the KFINTECH CAS PDF and identify conversion errors
"""
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

try:
    from casparser import read_cas_pdf
except ImportError:
    print("❌ casparser not installed. Installing...")
    import subprocess
    subprocess.run([sys.executable, "-m", "pip", "install", "casparser"])
    from casparser import read_cas_pdf

# Path to KFINTECH PDF
kfintech_pdf_path = r"c:\Users\mahchi01\Downloads\CAS\KFINTECH_97924150102202603102380252686267905.pdf"

print(f"📄 Testing CAS PDF: {kfintech_pdf_path}")
print("=" * 80)

try:
    # Parse the CAS PDF with provided password
    print("🔍 Parsing CAS PDF...")
    
    password = "Mahesh@1234"
    cas_data = read_cas_pdf(kfintech_pdf_path, password=password)
    password_used = "(password provided)"
    
    print(f"✅ Successfully parsed CAS PDF (password: {password_used})")
    print(f"📊 Investor Email: {cas_data.investor_info.email if cas_data.investor_info else 'N/A'}")
    print(f"📊 Investor Name: {cas_data.investor_info.name if cas_data.investor_info else 'N/A'}")
    print(f"📊 Number of Folios: {len(cas_data.folios)}")
    print()
    
    # Iterate through folios and schemes to find conversion issues
    print("🔍 Checking for potential conversion errors...")
    print("=" * 80)
    
    for folio_idx, folio in enumerate(cas_data.folios, 1):
        print(f"\n📁 Folio {folio_idx}: {folio.folio}")
        print(f"   AMC: {folio.amc}")
        
        for scheme_idx, scheme in enumerate(folio.schemes, 1):
            print(f"\n   💰 Scheme {scheme_idx}: {scheme.scheme[:70]}...")
            print(f"      ISIN: {scheme.isin}")
            print(f"      AMFI: {scheme.amfi}")
            print(f"      Close Units: {scheme.close} (type: {type(scheme.close)})")
            
            # Check valuation
            if scheme.valuation:
                print(f"      Valuation:")
                print(f"         NAV: {scheme.valuation.nav} (type: {type(scheme.valuation.nav)})")
                print(f"         Value: {scheme.valuation.value} (type: {type(scheme.valuation.value)})")
                print(f"         Cost: {scheme.valuation.cost} (type: {type(scheme.valuation.cost)})")
                
                # Try conversions
                try:
                    units = float(scheme.close) if scheme.close else 0
                    print(f"         ✅ Units conversion: {units}")
                except (ValueError, TypeError) as e:
                    print(f"         ❌ Units conversion ERROR: {e}")
                
                try:
                    nav = float(scheme.valuation.nav) if scheme.valuation.nav else 0
                    print(f"         ✅ NAV conversion: {nav}")
                except (ValueError, TypeError) as e:
                    print(f"         ❌ NAV conversion ERROR: {e}")
                
                try:
                    current_value = float(scheme.valuation.value) if scheme.valuation.value else 0
                    print(f"         ✅ Value conversion: {current_value}")
                except (ValueError, TypeError) as e:
                    print(f"         ❌ Value conversion ERROR: {e}")
                
                try:
                    invested_amount = float(scheme.valuation.cost) if scheme.valuation.cost else 0
                    print(f"         ✅ Cost conversion: {invested_amount}")
                except (ValueError, TypeError) as e:
                    print(f"         ❌ Cost conversion ERROR: {e}")
            
            # Check transactions (first 2 only for brevity)
            if scheme.transactions:
                print(f"      📝 Transactions (showing first 2 of {len(scheme.transactions)}):")
                for txn_idx, txn in enumerate(scheme.transactions[:2], 1):
                    print(f"         Txn {txn_idx}: Date={txn.date}, Amount={txn.amount}, Units={txn.units}, NAV={txn.nav}")
                    
                    # Try conversions
                    try:
                        if txn.amount:
                            amount = float(txn.amount)
                            print(f"            ✅ Amount conversion: {amount}")
                    except (ValueError, TypeError) as e:
                        print(f"            ❌ Amount conversion ERROR: {e}")
                    
                    try:
                        if txn.units:
                            units = float(txn.units)
                            print(f"            ✅ Units conversion: {units}")
                    except (ValueError, TypeError) as e:
                        print(f"            ❌ Units conversion ERROR: {e}")

except FileNotFoundError:
    print(f"❌ File not found: {kfintech_pdf_path}")
except Exception as e:
    print(f"❌ Error parsing CAS PDF: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 80)
print("✅ Test complete")
