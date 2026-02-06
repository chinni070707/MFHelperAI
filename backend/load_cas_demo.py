"""
Parse KFinTech CAS PDF and Load as Demo Data
Extracts real portfolio data and rounds off decimal values
"""
import PyPDF2
import re
from datetime import datetime
from sqlalchemy.orm import sessionmaker
from app.database import engine
from app.models.demo_portfolio import DemoPortfolio
from app.models.models import FundMaster

PDF_PATH = r"C:\Users\mahchi01\Downloads\PDFs\KFINTECH_97924150102202603102380252686267905.pdf"
PASSWORD = "Mahesh@1234"

def extract_cas_data(pdf_path, password):
    """Extract mutual fund holdings from KFinTech CAS PDF"""
    try:
        with open(pdf_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            
            # Check if PDF is encrypted
            if pdf_reader.is_encrypted:
                pdf_reader.decrypt(password)
            
            # Extract text from all pages
            full_text = ""
            for page in pdf_reader.pages:
                full_text += page.extract_text() + "\n"
            
            print("\n" + "=" * 70)
            print("CAS PDF EXTRACTED SUCCESSFULLY")
            print("=" * 70)
            
            # Save extracted text for debugging
            with open('cas_extracted_text.txt', 'w', encoding='utf-8') as f:
                f.write(full_text)
            print("✓ Extracted text saved to cas_extracted_text.txt")
            
            # Parse holdings
            holdings = parse_holdings(full_text)
            return holdings
            
    except Exception as e:
        print(f"Error reading PDF: {e}")
        return []

def parse_holdings(text):
    """Parse mutual fund holdings from KFinTech CAS text"""
    holdings = []
    
    # Look for the PORTFOLIO SUMMARY section
    if 'PORTFOLIO SUMMARY' in text:
        # Extract the summary table
        summary_start = text.find('PORTFOLIO SUMMARY')
        # Find the next significant section (usually starts with a fund name or "Nominee")
        summary_end = text.find('Nominee 1', summary_start)
        if summary_end == -1:
            summary_end = summary_start + 2000  # fallback
        
        summary_section = text[summary_start:summary_end]
        lines = summary_section.split('\n')
        
        for line in lines[1:]:  # Skip the header line
            line = line.strip()
            if not line or line.startswith('Total'):
                continue
            
            # Parse lines like: "MOTILAL OSWAL MUTUAL FUND 1071564.00 1130971.80"
            # Format: AMC_NAME  COST_VALUE  MARKET_VALUE
            parts = line.split()
            if len(parts) >= 3:
                try:
                    # Last two items should be numbers
                    market_value = float(parts[-1].replace(',', ''))
                    cost_value = float(parts[-2].replace(',', ''))
                    
                    # Everything before the numbers is the fund/AMC name
                    amc_name = ' '.join(parts[:-2])
                    
                    if market_value > 0 and cost_value >= 0:
                        holdings.append({
                            'amc': amc_name,
                            'cost': cost_value,
                            'market_value': market_value
                        })
                except (ValueError, IndexError):
                    continue
    
    # Now look for detailed holdings with scheme names
    detailed_holdings = []
    lines = text.split('\n')
    
    for i, line in enumerate(lines):
        # Look for "Closing Unit Balance:" which indicates fund details
        if 'Closing Unit Balance:' in line:
            # Extract units and market value
            units_match = re.search(r'Closing Unit Balance:\s*([\d,.]+)', line)
            market_match = re.search(r'Market Value[^:]*:\s*INR\s*([\d,.]+)', line)
            cost_match = re.search(r'Total Cost Value[^:]*:\s*INR\s*([\d,.]+)', line)
            
            if units_match and market_match:
                units = float(units_match.group(1).replace(',', ''))
                market_value = float(market_match.group(1).replace(',', ''))
                cost_value = float(cost_match.group(1).replace(',', '')) if cost_match else 0
                
                # Look backwards for the scheme name (usually has ISIN)
                scheme_name = None
                for j in range(max(0, i-10), i):
                    line_text = lines[j]
                    if 'ISIN:' in line_text or ('Folio No' in line_text and '-' in line_text):
                        # Extract scheme name from this line
                        # Format: "Nominee...128TSDGG-Axis ELSS Tax Saver Fund - Direct Growth..."
                        # or "GD340-Bandhan Small Cap Fund-Direct Plan-Growth..."
                        
                        # Find the part after the code and before ISIN/Folio
                        if 'ISIN:' in line_text:
                            parts = line_text.split('ISIN:')[0]
                        else:
                            parts = line_text.split('Folio No')[0]
                        
                        # Extract fund name after the dash following the code
                        # Look for pattern: CODE-FUND NAME
                        match = re.search(r'[A-Z0-9]+-(.*?)(?:\(|$)', parts)
                        if match:
                            scheme_name = match.group(1).strip()
                            # Clean up extra dashes and spaces
                            scheme_name = re.sub(r'\s*-\s*$', '', scheme_name)
                            break
                        
                        # Alternative: Just take everything after "Nominee...CODE-"
                        nominee_match = re.search(r'Nominee.*?[A-Z0-9]+-(.+)', parts)
                        if nominee_match:
                            scheme_name = nominee_match.group(1).strip()
                            break
                
                if scheme_name and units > 0 and market_value > 0:
                    detailed_holdings.append({
                        'scheme_name': scheme_name,
                        'units': units,
                        'cost': cost_value,
                        'market_value': market_value
                    })
    
    # Prefer detailed holdings if available
    if detailed_holdings:
        return detailed_holdings
    
    # Fallback to summary holdings
    return holdings

def round_off_data(holdings):
    """Round off all numerical values"""
    for holding in holdings:
        if 'units' in holding:
            holding['units'] = round(holding['units'])
        if 'cost' in holding:
            holding['amount'] = round(holding['cost'])
        if 'market_value' in holding:
            holding['market_value'] = round(holding['market_value'])
        if 'units' in holding and 'amount' in holding and holding['units'] > 0:
            holding['avg_cost'] = round(holding['amount'] / holding['units'])
        else:
            holding['avg_cost'] = 0
    return holdings

def match_funds_with_database(holdings, db):
    """Match CAS fund names with database funds"""
    matched_holdings = []
    
    print("\n📊 MATCHING FUNDS WITH DATABASE:")
    print("-" * 70)
    
    for holding in holdings:
        cas_fund_name = holding['scheme_name']
        
        # Try to find matching fund in database
        # First try exact match
        fund = db.query(FundMaster).filter(
            FundMaster.scheme_name.ilike(f"%{cas_fund_name}%"),
            FundMaster.is_active == True
        ).first()
        
        if not fund:
            # Try matching key words
            words = cas_fund_name.split()[:3]  # First 3 words
            search_pattern = '%'.join(words)
            fund = db.query(FundMaster).filter(
                FundMaster.scheme_name.ilike(f"%{search_pattern}%"),
                FundMaster.is_active == True
            ).first()
        
        if fund:
            matched_holdings.append({
                'scheme_name': fund.scheme_name,
                'scheme_code': fund.scheme_code,
                'amc': fund.amc,
                'category': fund.category,
                'units': holding['units'],
                'amount': holding['amount'],
                'avg_cost': holding['avg_cost'],
                'current_nav': fund.current_nav or holding['avg_cost']
            })
            print(f"✓ Matched: {cas_fund_name[:50]}")
            print(f"  → {fund.scheme_name[:60]}")
        else:
            print(f"✗ Not found: {cas_fund_name[:50]}")
    
    print("-" * 70)
    print(f"Matched: {len(matched_holdings)} / {len(holdings)} funds")
    
    return matched_holdings

def load_to_demo_portfolio(holdings):
    """Load holdings to demo_portfolio table"""
    SessionLocal = sessionmaker(bind=engine)
    db = SessionLocal()
    
    try:
        # Clear existing demo data
        db.query(DemoPortfolio).delete()
        
        # Match with database
        matched_holdings = match_funds_with_database(holdings, db)
        
        if not matched_holdings:
            print("\n❌ No funds matched with database!")
            return False
        
        print("\n📝 LOADING TO DEMO PORTFOLIO:")
        print("-" * 70)
        
        # Add matched holdings
        for holding in matched_holdings:
            invested_amount = holding['amount']
            current_value = holding['units'] * holding['current_nav']
            gain_loss = current_value - invested_amount
            gain_loss_percent = (gain_loss / invested_amount * 100) if invested_amount > 0 else 0
            
            demo = DemoPortfolio(
                scheme_name=holding['scheme_name'],
                scheme_code=holding['scheme_code'],
                units=holding['units'],
                avg_cost=holding['avg_cost'],
                current_nav=holding['current_nav'],
                invested_amount=invested_amount,
                current_value=current_value,
                gain_loss=gain_loss,
                gain_loss_percent=gain_loss_percent,
                amc=holding['amc'],
                category=holding['category'],
                is_active=True
            )
            db.add(demo)
            
            print(f"  • {holding['scheme_name'][:60]}")
            print(f"    Units: {holding['units']:>10,.0f} | Amount: ₹{invested_amount:>12,.0f}")
        
        db.commit()
        
        # Calculate totals
        total_invested = sum(h['amount'] for h in matched_holdings)
        total_current = sum(h['units'] * h['current_nav'] for h in matched_holdings)
        total_gain = total_current - total_invested
        gain_pct = (total_gain / total_invested * 100) if total_invested > 0 else 0
        
        print("-" * 70)
        print("\n" + "=" * 70)
        print("DEMO PORTFOLIO SUMMARY")
        print("=" * 70)
        print(f"Total Holdings: {len(matched_holdings)}")
        print(f"Total Invested: ₹{total_invested:>15,.0f}")
        print(f"Current Value:  ₹{total_current:>15,.0f}")
        print(f"Total Gain:     ₹{total_gain:>15,.0f} ({gain_pct:+.2f}%)")
        print("=" * 70)
        
        db.close()
        return True
        
    except Exception as e:
        print(f"\n❌ Error loading demo data: {e}")
        db.rollback()
        db.close()
        return False

def main():
    print("\n🚀 LOADING REAL CAS DATA AS DEMO PORTFOLIO")
    print("=" * 70)
    print(f"PDF File: {PDF_PATH}")
    print(f"Password: {'*' * len(PASSWORD)}")
    print("=" * 70)
    
    # Extract data from CAS
    holdings = extract_cas_data(PDF_PATH, PASSWORD)
    
    if not holdings:
        print("\n❌ No holdings found in CAS!")
        print("\nTrying alternative parsing...")
        return
    
    print(f"\n✓ Extracted {len(holdings)} holdings from CAS")
    
    # Round off numbers
    holdings = round_off_data(holdings)
    
    print("\n📋 EXTRACTED HOLDINGS (ROUNDED):")
    print("-" * 70)
    for i, h in enumerate(holdings, 1):
        print(f"{i}. {h['scheme_name'][:50]}")
        print(f"   Units: {h['units']:>10,.0f} | Amount: ₹{h['amount']:>12,.0f} | Avg: ₹{h['avg_cost']:>8,.0f}")
    print("-" * 70)
    
    # Load to database
    if load_to_demo_portfolio(holdings):
        print("\n✅ SUCCESS! Demo portfolio updated with real CAS data")
        print("\nNext steps:")
        print("  1. Restart server (if running)")
        print("  2. Test: http://localhost:8000/api/demo/portfolio")
        print("  3. Visit: http://localhost:8000/dashboard?mode=demo")
    else:
        print("\n❌ Failed to load demo portfolio")

if __name__ == "__main__":
    main()
