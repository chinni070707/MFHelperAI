"""
Robust CAS PDF Parser using PyMuPDF
Handles various CAS formats from CAMS and KFintech
"""
import sys
import os
from pathlib import Path
import re
from datetime import datetime
from typing import List, Dict, Optional

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

import fitz  # PyMuPDF


class CASParser:
    """Parse CAS PDF and extract portfolio data"""
    
    def __init__(self, pdf_path: str, password: Optional[str] = None):
        self.pdf_path = pdf_path
        self.password = password
        self.doc = None
        self.full_text = ""
        
    def open_pdf(self) -> bool:
        """Open and unlock PDF"""
        try:
            self.doc = fitz.open(self.pdf_path)
            
            if self.doc.is_encrypted and self.password:
                if not self.doc.authenticate(self.password):
                    print("❌ Failed to unlock PDF with provided password")
                    return False
                print("✅ PDF unlocked successfully")
            
            print(f"📄 PDF has {len(self.doc)} pages")
            return True
            
        except Exception as e:
            print(f"❌ Error opening PDF: {e}")
            return False
    
    def extract_text(self):
        """Extract text from all pages"""
        self.full_text = ""
        for page_num in range(len(self.doc)):
            page = self.doc[page_num]
            self.full_text += page.get_text() + "\n"
        
        print(f"📝 Extracted {len(self.full_text)} characters")
    
    def parse_investor_info(self) -> Dict:
        """Extract investor information"""
        info = {}
        
        # Extract PAN
        pan_match = re.search(r'PAN\s*:?\s*([A-Z]{5}\d{4}[A-Z])', self.full_text, re.IGNORECASE)
        if pan_match:
            info['pan'] = pan_match.group(1)
        
        # Extract name (usually after "Name:" or before PAN)
        name_match = re.search(r'(?:Name|Investor)\s*:?\s*([A-Z\s]+?)(?:\s*PAN|\s*\n)', self.full_text, re.IGNORECASE)
        if name_match:
            info['name'] = name_match.group(1).strip()
        
        # Extract email
        email_match = re.search(r'([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})', self.full_text)
        if email_match:
            info['email'] = email_match.group(1)
        
        # Extract mobile
        mobile_match = re.search(r'(?:Mobile|Phone)\s*:?\s*(\+?\d[\d\s-]{8,})', self.full_text, re.IGNORECASE)
        if mobile_match:
            info['mobile'] = mobile_match.group(1).strip()
        
        return info
    
    def parse_statement_period(self) -> Dict:
        """Extract statement period"""
        period = {}
        
        # Look for date ranges
        date_pattern = r'(\d{1,2}[-/]\w{3}[-/]\d{2,4})'
        dates = re.findall(date_pattern, self.full_text)
        
        if len(dates) >= 2:
            period['from'] = dates[0]
            period['to'] = dates[-1]
        
        return period
    
    def parse_holdings_from_table(self) -> List[Dict]:
        """Parse holdings from the closing balance table"""
        holdings = []
        lines = self.full_text.split('\n')
        
        in_mf_section = False
        current_amc = None
        current_scheme = None
        current_folio = None
        
        i = 0
        while i < len(lines):
            line = lines[i].strip()
            
            # Detect mutual fund section
            if 'mutual fund' in line.lower() and 'folio' in line.lower():
                in_mf_section = True
                i += 1
                continue
            
            # Stop at broking/equity section
            if any(keyword in line.lower() for keyword in ['broking', 'equity statement', 'demat']):
                in_mf_section = False
                i += 1
                continue
            
            if not in_mf_section:
                i += 1
                continue
            
            # Look for AMC Name
            if line.startswith('AMC Name'):
                amc_match = re.search(r'AMC Name\s*:\s*(.+)', line, re.IGNORECASE)
                if amc_match:
                    current_amc = amc_match.group(1).strip()
                i += 1
                continue
            
            # Look for Scheme Name
            if line.startswith('Scheme Name'):
                scheme_match = re.search(r'Scheme Name\s*:\s*(.+)', line, re.IGNORECASE)
                if scheme_match:
                    current_scheme = scheme_match.group(1).strip()
                    
                    # Scheme name might continue on next line
                    if i + 1 < len(lines):
                        next_line = lines[i + 1].strip()
                        if next_line and not next_line.startswith(('AMC', 'Scheme', 'Folio', 'Registrar', 'Advisor')) and len(next_line) < 50:
                            current_scheme += " " + next_line
                            i += 1
                
                i += 1
                continue
            
            # Look for Folio
            if line.startswith('Folio'):
                folio_match = re.search(r'Folio\s*(?:No|Number)?\s*:\s*(\d+)', line, re.IGNORECASE)
                if folio_match:
                    current_folio = folio_match.group(1)
                i += 1
                continue
            
            # Look for closing balance section with valuation
            if current_scheme and 'Closing Balance : Valuation as on' in line:
                # Next few lines should have the units, NAV, value
                units = None
                nav = None
                value = None
                
                # Look ahead for the data
                for j in range(i+1, min(i+10, len(lines))):
                    data_line = lines[j].strip()
                    
                    # Extract all numbers from this line
                    numbers = re.findall(r'[\d,]+\.?\d+', data_line)
                    if len(numbers) >= 3:
                        # Should be: units, NAV, value
                        try:
                            units = float(numbers[0].replace(',', ''))
                            nav = float(numbers[1].replace(',', ''))
                            value = float(numbers[2].replace(',', ''))
                            break
                        except (ValueError, IndexError):
                            continue
                
                if units and value:
                    holding = {
                        "fund_name": current_scheme,
                        "amc": current_amc,
                        "folio": current_folio,
                        "units": units,
                        "nav": nav or (value / units if units > 0 else 0),
                        "current_value": value,
                        "invested": 0,
                        "gain": 0,
                        "return_pct": 0
                    }
                    holdings.append(holding)
                    
                # Reset for next scheme
                current_scheme = None
                current_folio = None
            
            i += 1
        
        return holdings
    
    def _process_holding_buffer(self, buffer: List[str], amc: Optional[str] = None) -> Optional[Dict]:
        """Process buffered lines to extract a single holding"""
        if not buffer:
            return None
        
        # First line is typically the fund name
        fund_name = buffer[0].strip()
        
        # Ignore if it looks like a broker/equity holding
        if any(keyword in fund_name.lower() for keyword in ['broking', 'securities', 'zerodha', 'upstox', 'ltd', 'limited', 'private']):
            return None
        
        # Look for numbers in remaining lines
        all_numbers = []
        folio = None
        advisor = None
        
        for line in buffer[1:]:
            # Check for folio number pattern
            folio_match = re.search(r'(\d{8,})', line)
            if folio_match and not folio:
                folio = folio_match.group(1)
            
            # Check for advisor
            if 'advisor' in line.lower():
                advisor_match = re.search(r'Advisor\s*:?\s*(.+)', line, re.IGNORECASE)
                if advisor_match:
                    advisor = advisor_match.group(1).strip()
            
            # Extract all numbers
            numbers = re.findall(r'[\d,]+\.?\d*', line)
            all_numbers.extend(numbers)
        
        # Try to parse numbers (expecting: units, NAV, value)
        if len(all_numbers) >= 2:
            try:
                # Clean and convert
                cleaned_numbers = [float(n.replace(',', '')) for n in all_numbers]
                
                # Last two numbers are typically units and value
                # Or could be NAV, units, value
                if len(cleaned_numbers) >= 3:
                    nav = cleaned_numbers[-3]
                    units = cleaned_numbers[-2]
                    value = cleaned_numbers[-1]
                else:
                    nav = None
                    units = cleaned_numbers[-2]
                    value = cleaned_numbers[-1]
                
                # Validate: value should be close to units * nav
                if nav and abs(value - (units * nav)) / value > 0.05:  # More than 5% difference
                    # Might be wrong parsing, try different combination
                    if len(cleaned_numbers) >= 2:
                        units = cleaned_numbers[-2]
                        value = cleaned_numbers[-1]
                        nav = value / units if units > 0 else 0
                
                if units > 0 and value > 100:  # Only include if value > 100
                    return {
                        "fund_name": fund_name,
                        "amc": amc,
                        "folio": folio,
                        "advisor": advisor,
                        "units": units,
                        "nav": nav or (value / units if units > 0 else 0),
                        "current_value": value,
                        "invested": 0,  # Will be calculated from transactions if available
                        "gain": 0,
                        "return_pct": 0
                    }
            
            except (ValueError, ZeroDivisionError) as e:
                pass
        
        return None
    
    def parse(self) -> Dict:
        """Main parsing method"""
        if not self.open_pdf():
            return None
        
        self.extract_text()
        
        # Extract data
        investor_info = self.parse_investor_info()
        statement_period = self.parse_statement_period()
        holdings = self.parse_holdings_from_table()
        
        # Calculate summary
        total_current = sum(h['current_value'] for h in holdings)
        total_invested = sum(h.get('invested', 0) for h in holdings)
        
        result = {
            "investor_info": investor_info,
            "statement_period": statement_period,
            "holdings": holdings,
            "summary": {
                "total_schemes": len(holdings),
                "total_invested": total_invested,
                "total_current": total_current,
                "total_gain": total_current - total_invested,
                "return_pct": ((total_current - total_invested) / total_invested * 100) if total_invested > 0 else 0
            }
        }
        
        self.doc.close()
        return result


def main():
    pdf_path = r"C:\Users\mahchi01\Downloads\CAS_DEC2025_AA01244995_TXN.pdf"
    password = "YOUR_CAS_PASSWORD"
    
    print("="*70)
    print("🔍 CAS PDF Parser (Robust PyMuPDF-based)")
    print("="*70)
    print()
    
    parser = CASParser(pdf_path, password)
    result = parser.parse()
    
    if result and result['holdings']:
        print("\n" + "="*70)
        print("📋 INVESTOR INFO")
        print("="*70)
        info = result['investor_info']
        for key, value in info.items():
            print(f"{key.upper()}: {value}")
        
        print("\n" + "="*70)
        print("📊 PORTFOLIO SUMMARY")
        print("="*70)
        summary = result['summary']
        print(f"Total Schemes: {summary['total_schemes']}")
        print(f"Current Value: ₹{summary['total_current']:,.2f}")
        
        print("\n" + "="*70)
        print("💼 HOLDINGS")
        print("="*70)
        
        for i, holding in enumerate(result['holdings'], 1):
            print(f"\n{i}. {holding['fund_name']}")
            if holding.get('folio'):
                print(f"   Folio: {holding['folio']}")
            if holding.get('advisor'):
                print(f"   Advisor: {holding['advisor']}")
            print(f"   Units: {holding['units']:,.2f} @ ₹{holding['nav']:.2f}")
            print(f"   Value: ₹{holding['current_value']:,.2f}")
        
        print("\n" + "="*70)
        print("✅ CAS PARSING SUCCESSFUL!")
        print("="*70)
        
    else:
        print("\n❌ Failed to parse CAS PDF or no holdings found")


if __name__ == "__main__":
    main()
