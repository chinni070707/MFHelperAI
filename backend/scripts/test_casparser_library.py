"""
Test CAS parsing using casparser library
"""
import casparser
import json
from pathlib import Path

# Path to the CAS file
cas_file = r"C:\Users\mahchi01\Downloads\CAS_DEC2025_AA01244995_TXN.pdf"
password = "AOLPC2904E"

print("=" * 80)
print("Testing casparser library with real CAS file")
print("=" * 80)

try:
    # Parse the CAS PDF
    print(f"\n📄 Reading CAS file: {cas_file}")
    print(f"🔐 Password: {password}")
    
    data = casparser.read_cas_pdf(cas_file, password)
    
    print(f"\n✅ Successfully parsed CAS file!")
    print(f"📊 File Type: {data.file_type}")
    print(f"📅 Statement Period: {data.statement_period.from_} to {data.statement_period.to}")
    print(f"📋 CAS Type: {data.cas_type}")
    
    # Investor info
    print(f"\n👤 Investor Info:")
    print(f"   Name: {data.investor_info.name}")
    print(f"   Email: {data.investor_info.email}")
    print(f"   Mobile: {data.investor_info.mobile}")
    print(f"   PAN: {data.investor_info.pan if hasattr(data.investor_info, 'pan') else 'N/A'}")
    
    # Portfolio summary
    print(f"\n📈 Portfolio Summary:")
    print(f"   Total Folios: {len(data.folios)}")
    
    total_value = 0
    total_cost = 0
    total_schemes = 0
    
    for folio in data.folios:
        print(f"\n   Folio: {folio.folio}")
        print(f"   AMC: {folio.amc}")
        print(f"   PAN: {folio.PAN}")
        print(f"   Schemes: {len(folio.schemes)}")
        
        total_schemes += len(folio.schemes)
        
        for scheme in folio.schemes:
            print(f"\n      📌 {scheme.scheme}")
            print(f"         ISIN: {scheme.isin}")
            print(f"         Type: {scheme.type}")
            
            if scheme.valuation:
                print(f"         Units: {scheme.close:,.4f}")
                print(f"         NAV: ₹{scheme.valuation.nav:,.4f}")
                print(f"         Value: ₹{scheme.valuation.value:,.2f}")
                print(f"         Cost: ₹{scheme.valuation.cost:,.2f}")
                print(f"         Gain: ₹{scheme.valuation.value - scheme.valuation.cost:,.2f}")
                print(f"         Return: {((scheme.valuation.value / scheme.valuation.cost - 1) * 100):,.2f}%")
                
                total_value += scheme.valuation.value
                total_cost += scheme.valuation.cost
            else:
                print(f"         Units: {scheme.close:,.4f}")
                print(f"         ⚠️ No valuation data available")
            
            print(f"         Transactions: {len(scheme.transactions)}")
            if scheme.transactions:
                print(f"         First Transaction: {scheme.transactions[0].date}")
                print(f"         Last Transaction: {scheme.transactions[-1].date}")
    
    print(f"\n" + "=" * 80)
    print(f"💰 PORTFOLIO TOTALS")
    print(f"=" * 80)
    print(f"Total Schemes: {total_schemes}")
    print(f"Total Invested: ₹{total_cost:,.2f}")
    print(f"Current Value: ₹{total_value:,.2f}")
    print(f"Total Gain: ₹{total_value - total_cost:,.2f}")
    print(f"Overall Return: {((total_value / total_cost - 1) * 100):,.2f}%")
    
    # Save detailed output
    output_file = "cas_parsed_data.json"
    with open(output_file, 'w') as f:
        # Convert to dict and save
        json.dump(data.model_dump(), f, indent=2, default=str)
    
    print(f"\n💾 Detailed data saved to: {output_file}")
    
    # Show sample of first scheme's transactions
    if data.folios and data.folios[0].schemes and data.folios[0].schemes[0].transactions:
        print(f"\n📊 Sample Transactions (first scheme):")
        scheme = data.folios[0].schemes[0]
        print(f"   Scheme: {scheme.scheme}")
        for txn in scheme.transactions[:5]:  # First 5 transactions
            print(f"   {txn.date} | {txn.description:40s} | Units: {txn.units:10.4f} | NAV: ₹{txn.nav:8.2f} | Amount: ₹{txn.amount:12.2f}")
        if len(scheme.transactions) > 5:
            print(f"   ... and {len(scheme.transactions) - 5} more transactions")
    
    print("\n✅ CAS parsing successful!")
    print("✅ casparser library works perfectly with this CAS format!")
    
except Exception as e:
    print(f"\n❌ Error parsing CAS: {e}")
    import traceback
    traceback.print_exc()
    print("\n💡 If you see HeaderParseError, the CAS might be in a different format.")
    print("   casparser supports CAMS, KFintech (Karvy), and NSDL formats.")
