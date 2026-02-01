"""
Test KFintech CAS parsing with casparser library
"""
import casparser
import json
from pathlib import Path

# KFintech CAS file
cas_file = r"C:\Users\mahchi01\Downloads\KFINTECH_97924150102202603102380252686267905.pdf"
password = "YOUR_CAS_PDF_PASSWORD"  # Replace with your actual CAS password

print("=" * 80)
print("Testing casparser with KFintech CAS file")
print("=" * 80)

try:
    # Check if file exists
    if not Path(cas_file).exists():
        print(f"\n❌ File not found: {cas_file}")
        exit(1)
    
    # Parse the CAS PDF
    print(f"\n📄 Reading KFintech CAS file...")
    print(f"🔐 Using password: {password}")
    
    data = casparser.read_cas_pdf(cas_file, password)
    
    print(f"\n✅ Successfully parsed KFintech CAS!")
    print(f"\n📊 File Information:")
    print(f"   File Type: {data.file_type}")
    print(f"   CAS Type: {data.cas_type}")
    print(f"   Statement Period: {data.statement_period.from_} to {data.statement_period.to}")
    
    # Investor info
    print(f"\n👤 Investor Information:")
    print(f"   Name: {data.investor_info.name}")
    print(f"   Email: {data.investor_info.email}")
    print(f"   Mobile: {data.investor_info.mobile}")
    
    # Portfolio summary
    print(f"\n📈 Portfolio Summary:")
    print(f"   Total Folios: {len(data.folios)}")
    
    total_value = 0
    total_cost = 0
    total_schemes = 0
    
    for folio_idx, folio in enumerate(data.folios, 1):
        print(f"\n{'='*80}")
        print(f"📁 Folio {folio_idx}: {folio.folio}")
        print(f"{'='*80}")
        print(f"   AMC: {folio.amc}")
        print(f"   PAN: {folio.PAN}")
        print(f"   KYC: {folio.KYC}")
        print(f"   Total Schemes: {len(folio.schemes)}")
        
        total_schemes += len(folio.schemes)
        
        for scheme_idx, scheme in enumerate(folio.schemes, 1):
            print(f"\n   {'─'*70}")
            print(f"   📌 Scheme {scheme_idx}: {scheme.scheme}")
            print(f"   {'─'*70}")
            print(f"      ISIN: {scheme.isin}")
            print(f"      AMFI Code: {scheme.amfi}")
            print(f"      Type: {scheme.type}")
            print(f"      RTA: {scheme.rta}")
            
            if scheme.valuation:
                print(f"\n      💰 Valuation (as of {scheme.valuation.date}):")
                print(f"         Units (Opening): {scheme.open:,.4f}")
                print(f"         Units (Closing): {scheme.close:,.4f}")
                print(f"         NAV: ₹{scheme.valuation.nav:,.4f}")
                print(f"         Current Value: ₹{scheme.valuation.value:,.2f}")
                print(f"         Cost: ₹{scheme.valuation.cost:,.2f}")
                print(f"         Gain/Loss: ₹{scheme.valuation.value - scheme.valuation.cost:,.2f}")
                gain_pct = ((scheme.valuation.value / scheme.valuation.cost - 1) * 100) if scheme.valuation.cost > 0 else 0
                print(f"         Return: {gain_pct:,.2f}%")
                
                total_value += scheme.valuation.value
                total_cost += scheme.valuation.cost
            else:
                print(f"\n      ⚠️  No valuation data available")
                print(f"         Units (Closing): {scheme.close:,.4f}")
            
            print(f"\n      📊 Transactions: {len(scheme.transactions)}")
            if scheme.transactions:
                print(f"         First: {scheme.transactions[0].date} - {scheme.transactions[0].description}")
                print(f"         Last: {scheme.transactions[-1].date} - {scheme.transactions[-1].description}")
                
                # Show last 3 transactions
                print(f"\n         Recent Transactions:")
                for txn in scheme.transactions[-3:]:
                    txn_type = "📥" if txn.amount and txn.amount >= 0 else "📤"
                    amount_str = f"₹{txn.amount:12,.2f}" if txn.amount is not None else "N/A".rjust(13)
                    units_str = f"{txn.units:10,.4f}" if txn.units is not None else "N/A".rjust(10)
                    nav_str = f"₹{txn.nav:8,.2f}" if txn.nav is not None else "N/A".rjust(9)
                    balance_str = f"{txn.balance:10,.4f}" if txn.balance is not None else "N/A".rjust(10)
                    print(f"         {txn_type} {txn.date} | {txn.description[:50]:50s}")
                    print(f"            Amount: {amount_str} | Units: {units_str} | NAV: {nav_str} | Balance: {balance_str}")
    
    # Overall summary
    print(f"\n{'='*80}")
    print(f"💰 OVERALL PORTFOLIO SUMMARY")
    print(f"{'='*80}")
    print(f"Total Folios: {len(data.folios)}")
    print(f"Total Schemes: {total_schemes}")
    print(f"Total Invested (Cost): ₹{total_cost:,.2f}")
    print(f"Current Value: ₹{total_value:,.2f}")
    print(f"Total Gain/Loss: ₹{total_value - total_cost:,.2f}")
    if total_cost > 0:
        overall_return = ((total_value / total_cost - 1) * 100)
        print(f"Overall Return: {overall_return:,.2f}%")
    
    # Save detailed output
    output_file = "kfintech_cas_parsed.json"
    with open(output_file, 'w') as f:
        json.dump(data.model_dump(), f, indent=2, default=str)
    
    print(f"\n💾 Detailed data saved to: {output_file}")
    
    # Category-wise breakdown
    category_summary = {}
    for folio in data.folios:
        for scheme in folio.schemes:
            # Try to guess category from scheme name
            scheme_name_lower = scheme.scheme.lower()
            if 'large' in scheme_name_lower or 'blue' in scheme_name_lower:
                category = 'Large Cap'
            elif 'mid' in scheme_name_lower:
                category = 'Mid Cap'
            elif 'small' in scheme_name_lower:
                category = 'Small Cap'
            elif 'flexi' in scheme_name_lower or 'multi' in scheme_name_lower:
                category = 'Flexi Cap'
            elif 'debt' in scheme_name_lower or 'bond' in scheme_name_lower or 'income' in scheme_name_lower:
                category = 'Debt'
            elif 'liquid' in scheme_name_lower:
                category = 'Liquid'
            elif 'hybrid' in scheme_name_lower or 'balanced' in scheme_name_lower:
                category = 'Hybrid'
            else:
                category = 'Other'
            
            if category not in category_summary:
                category_summary[category] = {'count': 0, 'value': 0, 'cost': 0}
            
            category_summary[category]['count'] += 1
            if scheme.valuation:
                category_summary[category]['value'] += scheme.valuation.value
                category_summary[category]['cost'] += scheme.valuation.cost
    
    if category_summary:
        print(f"\n{'='*80}")
        print(f"📊 CATEGORY-WISE BREAKDOWN")
        print(f"{'='*80}")
        for category, data in sorted(category_summary.items(), key=lambda x: x[1]['value'], reverse=True):
            allocation_pct = (data['value'] / total_value * 100) if total_value > 0 else 0
            gain = data['value'] - data['cost']
            gain_pct = ((data['value'] / data['cost'] - 1) * 100) if data['cost'] > 0 else 0
            print(f"\n{category}:")
            print(f"   Schemes: {data['count']}")
            print(f"   Value: ₹{data['value']:,.2f} ({allocation_pct:.1f}%)")
            print(f"   Cost: ₹{data['cost']:,.2f}")
            print(f"   Gain: ₹{gain:,.2f} ({gain_pct:+.2f}%)")
    
    print("\n" + "="*80)
    print("✅ KFintech CAS parsing SUCCESSFUL!")
    print("✅ casparser works perfectly with KFintech format!")
    print("="*80)
    
    print("\n💡 Next Steps:")
    print("   1. This data can now be imported into the database")
    print("   2. Each folio → Portfolio record")
    print("   3. Each scheme → Holding record")
    print("   4. Each transaction → Transaction record")
    print("   5. Use this for XIRR calculation")
    
except Exception as e:
    print(f"\n❌ Error parsing KFintech CAS: {e}")
    import traceback
    traceback.print_exc()
    print("\n💡 Troubleshooting:")
    print("   - Check if the file path is correct")
    print("   - Verify the password is correct")
    print("   - Ensure casparser is installed: pip install casparser[fast]")
