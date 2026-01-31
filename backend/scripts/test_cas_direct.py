"""
Test CAS PDF import with direct text extraction
More robust approach for different CAS formats
"""
import sys
from pathlib import Path
import re
from datetime import datetime

try:
    import fitz  # PyMuPDF
    print("✅ PyMuPDF is installed")
except ImportError:
    print("❌ PyMuPDF not found. Installing...")
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "PyMuPDF"])
    import fitz
    print("✅ PyMuPDF installed successfully")


def extract_text_from_pdf(pdf_path: str, password: str) -> str:
    """Extract all text from PDF"""
    print(f"📄 Opening PDF: {pdf_path}")
    
    doc = fitz.open(pdf_path)
    print(f"   Pages: {doc.page_count}")
    print(f"   Encrypted: {doc.is_encrypted}")
    
    if doc.is_encrypted:
        if doc.authenticate(password):
            print(f"   ✅ Password authenticated")
        else:
            raise ValueError("❌ Invalid password")
    
    # Extract text from all pages
    full_text = ""
    for page_num in range(doc.page_count):
        page = doc[page_num]
        text = page.get_text()
        full_text += text + "\n\n"
        print(f"   Page {page_num + 1}: {len(text)} characters")
    
    doc.close()
    
    print(f"\n   Total text extracted: {len(full_text)} characters")
    return full_text


def parse_cas_statement(text: str) -> dict:
    """Parse CAS statement text to extract portfolio data"""
    print(f"\n📊 Parsing CAS statement...")
    
    # Extract header information
    investor_info = extract_investor_info(text)
    print(f"   Investor: {investor_info.get('name', 'N/A')}")
    print(f"   PAN: {investor_info.get('pan', 'N/A')}")
    print(f"   Email: {investor_info.get('email', 'N/A')}")
    
    # Extract statement period
    period = extract_statement_period(text)
    print(f"   Period: {period.get('from', 'N/A')} to {period.get('to', 'N/A')}")
    
    # Extract holdings from the summary table at the end
    # This is more reliable than parsing individual sections
    holdings = extract_holdings_from_summary_table(text)
    print(f"\n   Found {len(holdings)} holdings from summary table")
    
    # Calculate summary
    total_invested = sum(h['invested'] for h in holdings)
    total_current = sum(h['current_value'] for h in holdings)
    total_gain = total_current - total_invested
    
    return {
        'investor_info': investor_info,
        'period': period,
        'holdings': holdings,
        'summary': {
            'total_funds': len(holdings),
            'total_invested': total_invested,
            'total_current': total_current,
            'total_gain': total_gain,
            'return_pct': (total_gain / total_invested * 100) if total_invested > 0 else 0
        }
    }


def extract_investor_info(text: str) -> dict:
    """Extract investor information from CAS"""
    info = {}
    
    # Name pattern
    name_match = re.search(r'(?:Statement for|Portfolio for|Name\s*:)\s*([A-Z][A-Za-z\s]+?)(?:\n|PAN|Email|Mobile)', text, re.IGNORECASE)
    if name_match:
        info['name'] = name_match.group(1).strip()
    
    # PAN pattern
    pan_match = re.search(r'PAN\s*:?\s*([A-Z]{5}\d{4}[A-Z])', text, re.IGNORECASE)
    if pan_match:
        info['pan'] = pan_match.group(1)
    
    # Email pattern
    email_match = re.search(r'Email\s*:?\s*([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})', text, re.IGNORECASE)
    if email_match:
        info['email'] = email_match.group(1)
    
    # Mobile pattern
    mobile_match = re.search(r'Mobile\s*:?\s*([\d\s+-]+)', text, re.IGNORECASE)
    if mobile_match:
        info['mobile'] = mobile_match.group(1).strip()
    
    return info


def extract_statement_period(text: str) -> dict:
    """Extract statement period"""
    period = {}
    
    # Common patterns
    period_match = re.search(r'(?:From|Period)\s*:?\s*(\d{2}[-/]\w{3}[-/]\d{4})\s*(?:to|To)\s*(\d{2}[-/]\w{3}[-/]\d{4})', text, re.IGNORECASE)
    if period_match:
        period['from'] = period_match.group(1)
        period['to'] = period_match.group(2)
    
    return period


def extract_holdings_from_summary_table(text: str) -> list:
    """
    Extract holdings from the summary table at the end of CAS
    Table has: Scheme Name | ISIN | Folio No. | Closing Bal (Units) | NAV | Cumulative Amount Invested | Valuation
    """
    holdings = []
    
    # Find the summary table section
    summary_start = text.find('MUTUAL FUND UNITS HELD AS ON')
    if summary_start == -1:
        print("   ⚠️  Summary table not found")
        return []
    
    summary_section = text[summary_start:]
    
    # Look for entries with pattern: "CODE - Fund Name" followed by ISIN and numbers
    # Use regex to match each holding entry
    pattern = r'([A-Z0-9]{2,10})\s*-\s*(.+?)\s+(INF[A-Z0-9]{9})\s+([\d\/]+)\s+([\d,.]+)\s+([\d,.]+)\s+([\d,.]+)\s+([\d,.]+)'
    
    matches = re.finditer(pattern, summary_section, re.MULTILINE)
    
    for match in matches:
        try:
            scheme_code = match.group(1).strip()
            fund_name = match.group(2).strip()
            isin = match.group(3).strip()
            folio = match.group(4).strip()
            units = float(match.group(5).replace(',', ''))
            nav = float(match.group(6).replace(',', ''))
            invested = float(match.group(7).replace(',', ''))
            valuation = float(match.group(8).replace(',', ''))
            
            # Determine AMC from fund name
            amc = extract_amc_from_name(fund_name)
            
            holdings.append({
                'fund_name': f"{scheme_code} - {clean_scheme_name(fund_name)}",
                'amc': amc,
                'folio': folio,
                'category': determine_category(fund_name),
                'isin': isin,
                'units': units,
                'nav': nav,
                'invested': invested,
                'current_value': valuation,
                'gain': valuation - invested,
                'return_pct': ((valuation - invested) / invested * 100) if invested > 0 else 0
            })
        except (ValueError, IndexError) as e:
            # Skip entries we can't parse
            continue
    
    return holdings


def extract_amc_from_name(fund_name: str) -> str:
    """Extract AMC name from fund name"""
    amc_keywords = {
        'HDFC': 'HDFC Mutual Fund',
        'ICICI': 'ICICI Prudential Mutual Fund',
        'Axis': 'Axis Mutual Fund',
        'SBI': 'SBI Mutual Fund',
        'Kotak': 'Kotak Mahindra Mutual Fund',
        'Aditya Birla': 'Aditya Birla Sun Life Mutual Fund',
        'Nippon': 'Nippon India Mutual Fund',
        'UTI': 'UTI Mutual Fund',
        'DSP': 'DSP Mutual Fund',
        'Franklin': 'Franklin Templeton Mutual Fund',
        'Mirae': 'Mirae Asset Mutual Fund',
        'Parag Parikh': 'PPFAS Mutual Fund',
        'Motilal': 'Motilal Oswal Mutual Fund',
        'Tata': 'Tata Mutual Fund',
        'Quant': 'Quant Mutual Fund',
        'Canara': 'Canara Robeco Mutual Fund',
        'Invesco': 'Invesco Mutual Fund'
    }
    
    for keyword, amc_name in amc_keywords.items():
        if keyword in fund_name:
            return amc_name
    
    # Try to extract from beginning of name
    first_word = fund_name.split()[0] if fund_name else ''
    return f"{first_word} Mutual Fund" if first_word else 'Unknown AMC'


def clean_scheme_name(name: str) -> str:
    """Clean up scheme name"""
    # Remove extra spaces
    name = re.sub(r'\s+', ' ', name)
    # Remove trailing dashes/underscores
    name = name.strip(' -_')
    return name


def determine_category(scheme_name: str) -> str:
    """Determine fund category from scheme name"""
    name_lower = scheme_name.lower()
    
    categories = [
        (['large cap', 'blue chip', 'top 100', 'nifty 50', 'sensex'], 'Large Cap'),
        (['mid cap', 'midcap', 'mid-cap'], 'Mid Cap'),
        (['small cap', 'smallcap', 'small-cap'], 'Small Cap'),
        (['flexi cap', 'flexicap', 'multi cap', 'multicap'], 'Flexi Cap'),
        (['large & mid', 'large and mid'], 'Large & Mid Cap'),
        (['elss', 'tax saver', 'tax saving'], 'ELSS'),
        (['focused', 'focus'], 'Focused'),
        (['debt', 'bond', 'income', 'credit', 'gilt'], 'Debt'),
        (['liquid', 'money market', 'overnight'], 'Liquid'),
        (['balanced', 'hybrid', 'aggressive'], 'Hybrid'),
        (['index', 'nifty', 'sensex'], 'Index'),
        (['international', 'global', 'foreign'], 'International')
    ]
    
    for keywords, category in categories:
        if any(keyword in name_lower for keyword in keywords):
            return category
    
    return 'Other'


def save_to_file(data: dict, output_file: str):
    """Save parsed data to JSON file"""
    import json
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, default=str)
    print(f"\n💾 Data saved to: {output_file}")


if __name__ == "__main__":
    cas_file = r"C:\Users\mahchi01\Downloads\CAS_DEC2025_AA01244995_TXN.pdf"
    password = "YOUR_CAS_PASSWORD"
    
    if not Path(cas_file).exists():
        print(f"❌ File not found: {cas_file}")
        sys.exit(1)
    
    try:
        print(f"\n{'='*70}")
        print(f"CAS PDF Import Test")
        print(f"{'='*70}\n")
        
        # Step 1: Extract text
        text = extract_text_from_pdf(cas_file, password)
        
        # Save extracted text for debugging
        text_file = "cas_extracted_text.txt"
        with open(text_file, 'w', encoding='utf-8') as f:
            f.write(text)
        print(f"\n💾 Extracted text saved to: {text_file}")
        
        # Step 2: Parse the text
        cas_data = parse_cas_statement(text)
        
        # Step 3: Display results
        print(f"\n{'='*70}")
        print(f"✅ CAS Parsed Successfully!")
        print(f"{'='*70}\n")
        
        print(f"📊 Summary:")

        print(f"   Total Schemes: {cas_data['summary']['total_funds']}")
        print(f"   Total Invested: ₹{cas_data['summary']['total_invested']:,.2f}")
        print(f"   Total Current: ₹{cas_data['summary']['total_current']:,.2f}")
        print(f"   Total Gain: ₹{cas_data['summary']['total_gain']:,.2f}")
        print(f"   Return %: {cas_data['summary']['return_pct']:.2f}%")
        
        print(f"\n📋 Holdings (first 5):")
        for i, h in enumerate(cas_data['holdings'][:5], 1):
            print(f"\n   {i}. {h['fund_name'][:60]}")
            print(f"      AMC: {h['amc']}")
            print(f"      Category: {h['category']}")
            print(f"      Units: {h['units']:.4f} | NAV: ₹{h['nav']:.2f}")
            print(f"      Invested: ₹{h['invested']:,.2f} | Current: ₹{h['current_value']:,.2f}")
            print(f"      Gain: ₹{h['gain']:,.2f} ({h['return_pct']:.2f}%)")
        
        # Save parsed data
        output_file = "cas_parsed_data.json"
        save_to_file(cas_data, output_file)
        
        print(f"\n{'='*70}")
        print(f"✅ Test completed successfully!")
        print(f"{'='*70}")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
