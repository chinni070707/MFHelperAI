"""
Upload Routes - Handle Excel and CAS PDF uploads
"""
from fastapi import APIRouter, UploadFile, File, HTTPException, Depends, Form
from sqlalchemy.orm import Session
import pandas as pd
import io
import re
from typing import Optional
from datetime import datetime
import logging

from app.database import get_db
from app.models.models import Portfolio, Holding, User
from app.utils.auth import get_optional_current_user

# Setup logger
logger = logging.getLogger(__name__)

router = APIRouter()


# ============ Excel Parser ============
def find_header_row(df: pd.DataFrame) -> int:
    """Find the row containing column headers by looking for 'Fund Name' or similar"""
    header_keywords = ['fund name', 'scheme name', 'fund', 'name']
    
    for idx in range(min(10, len(df))):  # Check first 10 rows
        row_values = df.iloc[idx].astype(str).str.lower().str.strip()
        for keyword in header_keywords:
            if any(keyword in str(val) for val in row_values):
                logger.debug(f"Header row found at index {idx}")
                return idx
    logger.warning("No clear header row found, using first row as default")
    return 0  # Default to first row


def parse_excel(file_content: bytes, filename: str) -> dict:
    """Parse Excel file and extract portfolio data"""
    logger.info(f"Starting Excel parsing for file: {filename} (size: {len(file_content)} bytes)")
    
    try:
        # Read Excel file without headers first to detect structure
        if filename.endswith('.csv'):
            df_raw = pd.read_csv(io.BytesIO(file_content), header=None)
            logger.debug(f"CSV file loaded: {df_raw.shape[0]} rows, {df_raw.shape[1]} columns")
        else:
            df_raw = pd.read_excel(io.BytesIO(file_content), header=None)
            logger.debug(f"Excel file loaded: {df_raw.shape[0]} rows, {df_raw.shape[1]} columns")
        
        # Find the header row
        header_row = find_header_row(df_raw)
        
        # Re-read with correct header
        if filename.endswith('.csv'):
            df = pd.read_csv(io.BytesIO(file_content), header=header_row)
        else:
            df = pd.read_excel(io.BytesIO(file_content), header=header_row)
        
        # Remove completely empty rows
        df = df.dropna(how='all')
        
        # Normalize column names - handle unnamed columns
        new_columns = []
        for col in df.columns:
            col_str = str(col).strip().lower()
            if col_str.startswith('unnamed'):
                new_columns.append(col_str)
            else:
                new_columns.append(col_str)
        df.columns = new_columns
        
        # Map common column name variations
        column_mapping = {
            'fund name': 'fund_name',
            'fund': 'fund_name',
            'name': 'fund_name',
            'scheme name': 'fund_name',
            'scheme': 'fund_name',
            'amc': 'amc',
            'fund house': 'amc',
            'asset management company': 'amc',
            'category': 'category',
            'type': 'category',
            'scheme type': 'category',
            'invested': 'invested',
            'invested value': 'invested',
            'amount invested': 'invested',
            'cost': 'invested',
            'purchase value': 'invested',
            'current value': 'current_value',
            'current': 'current_value',
            'market value': 'current_value',
            'nav': 'nav',
            'current nav': 'nav',
            'units': 'units',
            'unit balance': 'units',
            '1y return': 'return_1y',
            '1y': 'return_1y',
            '1yr': 'return_1y',
            '1 year': 'return_1y',
            '3y return': 'return_3y',
            '3y': 'return_3y',
            '3yr': 'return_3y',
            '3 year': 'return_3y',
            '5y': 'return_5y',
            '5yr': 'return_5y',
            '5 year': 'return_5y',
            'alpha': 'alpha',
            'style': 'style',
            'investment style': 'style',
            'folio': 'folio',
            'folio no': 'folio',
            'folio number': 'folio',
            'gains': 'gains',
            'gain': 'gains',
            'weight': 'weight',
            'up capture': 'up_capture',
            'down capture': 'down_capture',
            'rolling return': 'rolling_return',
            'actual large%': 'large_pct',
            'actual mid%': 'mid_pct',
            'actual small%': 'small_pct'
        }
        
        # Rename columns
        df = df.rename(columns={col: column_mapping.get(col, col) for col in df.columns})
        
        # Check if fund_name column exists
        if 'fund_name' not in df.columns:
            # Try to find fund_name in any column
            for col in df.columns:
                sample_vals = df[col].dropna().head(5).astype(str)
                if any('fund' in str(v).lower() or 'cap' in str(v).lower() or 'flexi' in str(v).lower() for v in sample_vals):
                    df = df.rename(columns={col: 'fund_name'})
                    break
        
        if 'fund_name' not in df.columns:
            raise ValueError("Missing required column: Fund Name. Please ensure your Excel has a 'Fund Name' column.")
        
        # Remove rows where fund_name is empty or looks like a header
        df = df[df['fund_name'].notna()]
        df = df[~df['fund_name'].astype(str).str.lower().str.contains('fund name|scheme name|total|summary', na=False)]
        
        # Detect AMC from fund name if AMC column is missing
        if 'amc' not in df.columns or df['amc'].isna().all():
            df['amc'] = df['fund_name'].apply(detect_amc_from_name)
        
        # Detect category from fund name if category is missing or partial
        df['category'] = df.apply(lambda row: detect_category(row.get('fund_name', ''), row.get('category', '')), axis=1)
        
        # Detect investment style
        if 'style' not in df.columns:
            df['style'] = df['fund_name'].apply(detect_style_from_name)
        
        # Ensure numeric columns are numeric
        numeric_cols = ['invested', 'current_value', 'nav', 'units', 'alpha', 'gains', 'weight']
        for col in numeric_cols:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
        
        # Handle return columns (keep as string with %)
        return_cols = ['return_1y', 'return_3y', 'return_5y', 'rolling_return']
        for col in return_cols:
            if col in df.columns:
                df[col] = df[col].apply(lambda x: f"{x}%" if pd.notna(x) and str(x) not in ['-', 'nan', ''] and '%' not in str(x) else str(x) if pd.notna(x) else '-')
        
        # Fill missing values
        df = df.fillna({
            'amc': 'Unknown',
            'category': 'Equity',
            'invested': 0,
            'current_value': 0,
            'style': 'Blend',
            'return_1y': '-',
            'return_3y': '-',
            'alpha': '-'
        })
        
        # Convert to list of dicts
        holdings = df.to_dict('records')
        
        # Clean up holdings
        clean_holdings = []
        for h in holdings:
            if h.get('fund_name') and str(h.get('fund_name')).strip():
                clean_h = {
                    'fund_name': str(h.get('fund_name', '')).strip(),
                    'amc': str(h.get('amc', 'Unknown')).strip(),
                    'category': str(h.get('category', 'Equity')).strip(),
                    'invested': float(h.get('invested', 0) or 0),
                    'current_value': float(h.get('current_value', 0) or 0),
                    'style': str(h.get('style', 'Blend')).strip(),
                    'return_1y': str(h.get('return_1y', '-')),
                    'return_3y': str(h.get('return_3y', '-')),
                    'alpha': h.get('alpha', '-'),
                }
                # Add optional fields
                for field in ['return_5y', 'up_capture', 'down_capture', 'rolling_return', 'large_pct', 'mid_pct', 'small_pct', 'gains', 'weight']:
                    if field in h and pd.notna(h[field]):
                        clean_h[field] = h[field]
                clean_holdings.append(clean_h)
        
        # Calculate totals
        total_invested = sum(float(h.get('invested', 0)) for h in clean_holdings)
        total_current = sum(float(h.get('current_value', 0)) for h in clean_holdings)
        total_gain = total_current - total_invested
        
        logger.info(f"Excel parsing successful: {len(clean_holdings)} holdings, Total: ₹{total_current:,.0f}")
        logger.debug(f"Portfolio summary - Invested: ₹{total_invested:,.0f}, Gain: ₹{total_gain:,.0f}")
        
        return {
            "success": True,
            "source": "excel",
            "filename": filename,
            "holdings": clean_holdings,
            "summary": {
                "total_funds": len(clean_holdings),
                "total_invested": total_invested,
                "total_current": total_current,
                "total_gain": total_gain,
                "return_pct": (total_gain / total_invested * 100) if total_invested > 0 else 0
            },
            "parsed_at": datetime.now().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error parsing Excel file {filename}: {str(e)}", exc_info=True)
        raise HTTPException(status_code=400, detail=f"Error parsing Excel: {str(e)}")


def detect_amc_from_name(fund_name: str) -> str:
    """Detect AMC from fund name"""
    fund_name = str(fund_name).lower()
    amc_patterns = {
        'PPFAS AMC': ['parag parikh', 'ppfas'],
        'HDFC AMC': ['hdfc'],
        'ICICI Prudential': ['icici'],
        'SBI Mutual Fund': ['sbi'],
        'Axis AMC': ['axis'],
        'Kotak AMC': ['kotak'],
        'Nippon India': ['nippon', 'reliance'],
        'Mirae Asset': ['mirae'],
        'Motilal Oswal': ['motilal'],
        'DSP': ['dsp'],
        'Tata AMC': ['tata'],
        'UTI AMC': ['uti'],
        'Aditya Birla': ['aditya', 'birla'],
        'Franklin Templeton': ['franklin', 'templeton'],
        'Invesco': ['invesco'],
        'Edelweiss': ['edelweiss'],
        'Bandhan': ['bandhan'],
        'Quant MF': ['quant'],
        'Navi MF': ['navi'],
        'PGIM': ['pgim'],
        'Canara Robeco': ['canara'],
        'HSBC': ['hsbc'],
        'Sundaram': ['sundaram'],
        'LIC MF': ['lic'],
        'Mahindra Manulife': ['mahindra'],
        'JM Financial': ['jm '],
        'Groww': ['groww'],
    }
    
    for amc, patterns in amc_patterns.items():
        if any(p in fund_name for p in patterns):
            return amc
    return 'Other'


def detect_category(fund_name: str, existing_category: str = '') -> str:
    """Detect category from fund name or use existing"""
    if existing_category and str(existing_category).strip() and str(existing_category).lower() not in ['nan', 'none', '']:
        return str(existing_category).strip()
    
    fund_name = str(fund_name).lower()
    
    if 'liquid' in fund_name:
        return 'Liquid'
    elif 'small cap' in fund_name or 'smallcap' in fund_name:
        return 'Small Cap'
    elif 'mid cap' in fund_name or 'midcap' in fund_name:
        return 'Mid Cap'
    elif 'large cap' in fund_name or 'largecap' in fund_name or 'bluechip' in fund_name:
        return 'Large Cap'
    elif 'flexi' in fund_name or 'flexicap' in fund_name:
        return 'Flexi Cap'
    elif 'multi' in fund_name or 'multicap' in fund_name:
        return 'Multi Cap'
    elif 'elss' in fund_name or 'tax' in fund_name:
        return 'ELSS'
    elif 'focused' in fund_name:
        return 'Focused'
    elif 'contra' in fund_name:
        return 'Contra'
    elif 'value' in fund_name:
        return 'Value'
    elif 'large & mid' in fund_name or 'large and mid' in fund_name:
        return 'Large & Mid'
    elif 'nasdaq' in fund_name or 'us equity' in fund_name or 'international' in fund_name or 'fang' in fund_name or 'global' in fund_name:
        return 'International'
    elif 'digital' in fund_name or 'tech' in fund_name or 'it' in fund_name or 'pharma' in fund_name or 'banking' in fund_name or 'infra' in fund_name:
        return 'Sectoral'
    elif 'hybrid' in fund_name or 'balanced' in fund_name or 'aggressive' in fund_name:
        return 'Hybrid'
    elif 'debt' in fund_name or 'bond' in fund_name or 'gilt' in fund_name:
        return 'Debt'
    else:
        return 'Equity'


def detect_style_from_name(fund_name: str) -> str:
    """Detect investment style from fund name (alias for determine_style)"""
    return determine_style(fund_name)


# ============ CAS PDF Parser ============
def parse_cas_pdf(file_content: bytes, password: Optional[str] = None) -> dict:
    """Parse CAMS/KFintech CAS PDF and extract portfolio data"""
    logger.info(f"Starting CAS PDF parsing (size: {len(file_content)} bytes)")
    
    try:
        import fitz  # PyMuPDF
        
        # Open PDF
        doc = fitz.open(stream=file_content, filetype="pdf")
        logger.debug(f"PDF opened: {doc.page_count} pages, encrypted: {doc.is_encrypted}")
        
        # If password protected, try to decrypt
        if doc.is_encrypted:
            if not password:
                logger.warning("CAS PDF is encrypted but no password provided")
                raise HTTPException(
                    status_code=400, 
                    detail="CAS PDF is password protected. Please provide the PDF password."
                )
            if not doc.authenticate(password):
                logger.error(f"Failed to authenticate PDF with provided password")
                raise HTTPException(status_code=400, detail="Invalid password. Please check your PDF password and try again.")
            logger.info("PDF successfully authenticated")
        
        # Extract text from all pages
        full_text = ""
        for page in doc:
            full_text += page.get_text()
        
        doc.close()
        logger.debug(f"Extracted {len(full_text)} characters from PDF")
        
        # Parse the text to extract holdings
        holdings = extract_holdings_from_cas_text(full_text)
        
        # Calculate totals
        total_invested = sum(h.get('invested', 0) for h in holdings)
        total_current = sum(h.get('current_value', 0) for h in holdings)
        total_gain = total_current - total_invested
        
        return {
            "success": True,
            "source": "cas_pdf",
            "holdings": holdings,
            "summary": {
                "total_funds": len(holdings),
                "total_invested": total_invested,
                "total_current": total_current,
                "total_gain": total_gain,
                "return_pct": (total_gain / total_invested * 100) if total_invested > 0 else 0
            },
            "parsed_at": datetime.now().isoformat()
        }
        
    except ImportError:
        raise HTTPException(
            status_code=500, 
            detail="PDF parsing library not installed. Run: pip install PyMuPDF"
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error parsing CAS PDF: {str(e)}")


def extract_holdings_from_cas_text(text: str) -> list:
    """Extract mutual fund holdings from CAS text"""
    holdings = []
    
    # Common patterns in CAS statements
    # Pattern 1: Fund name followed by folio and details
    fund_pattern = r'([A-Za-z\s\-]+(?:Fund|Scheme|Plan|Growth|Direct|Regular)[A-Za-z\s\-]*)\s*(?:Folio\s*(?:No)?\.?\s*:?\s*)?(\d+[\d\/]*)'
    
    # Pattern 2: NAV and units
    nav_pattern = r'NAV[:\s]+(?:Rs\.?\s*)?([\d,]+\.?\d*)'
    units_pattern = r'(?:Unit\s*Balance|Units)[:\s]+([\d,]+\.?\d*)'
    value_pattern = r'(?:Valuation|Market\s*Value|Current\s*Value)[:\s]+(?:Rs\.?\s*)?([\d,]+\.?\d*)'
    cost_pattern = r'(?:Cost\s*Value|Amount\s*Invested|Purchase\s*Value)[:\s]+(?:Rs\.?\s*)?([\d,]+\.?\d*)'
    
    # Split text by common fund separators
    sections = re.split(r'(?=Registrar\s*:)|(?=ISIN\s*:)|(?=Folio\s*No)', text, flags=re.IGNORECASE)
    
    for section in sections:
        # Try to find fund name
        fund_match = re.search(fund_pattern, section, re.IGNORECASE)
        if fund_match:
            fund_name = fund_match.group(1).strip()
            folio = fund_match.group(2).strip() if fund_match.group(2) else ''
            
            # Extract numeric values
            nav_match = re.search(nav_pattern, section, re.IGNORECASE)
            units_match = re.search(units_pattern, section, re.IGNORECASE)
            value_match = re.search(value_pattern, section, re.IGNORECASE)
            cost_match = re.search(cost_pattern, section, re.IGNORECASE)
            
            nav = float(nav_match.group(1).replace(',', '')) if nav_match else 0
            units = float(units_match.group(1).replace(',', '')) if units_match else 0
            current_value = float(value_match.group(1).replace(',', '')) if value_match else nav * units
            invested = float(cost_match.group(1).replace(',', '')) if cost_match else current_value
            
            if fund_name and (current_value > 0 or units > 0):
                # Determine AMC from fund name
                amc = determine_amc(fund_name)
                category = determine_category(fund_name)
                style = determine_style(fund_name, category)
                
                holdings.append({
                    'fund_name': clean_fund_name(fund_name),
                    'folio': folio,
                    'amc': amc,
                    'category': category,
                    'style': style,
                    'units': units,
                    'nav': nav,
                    'invested': invested,
                    'current_value': current_value,
                    'return_1y': '-',
                    'return_3y': '-',
                    'alpha': '-'
                })
    
    # If no holdings found with patterns, try simpler extraction
    if not holdings:
        holdings = fallback_cas_parser(text)
    
    return holdings


def fallback_cas_parser(text: str) -> list:
    """Fallback parser for CAS when regex patterns don't work"""
    holdings = []
    
    # Look for common fund house names and extract nearby data
    fund_houses = [
        'HDFC', 'ICICI', 'SBI', 'Axis', 'Kotak', 'Nippon', 'Aditya Birla',
        'UTI', 'DSP', 'Tata', 'Mirae', 'Motilal', 'Parag Parikh', 'PPFAS',
        'Quant', 'Invesco', 'Bandhan', 'Edelweiss', 'Franklin', 'HSBC',
        'Canara', 'Baroda', 'LIC', 'Navi', 'Groww'
    ]
    
    lines = text.split('\n')
    
    for i, line in enumerate(lines):
        for fh in fund_houses:
            if fh.lower() in line.lower() and ('fund' in line.lower() or 'scheme' in line.lower()):
                # Found a fund, try to extract details from nearby lines
                context = '\n'.join(lines[max(0, i-2):min(len(lines), i+10)])
                
                # Extract numbers (likely to be value, units, nav)
                numbers = re.findall(r'[\d,]+\.?\d*', context)
                numbers = [float(n.replace(',', '')) for n in numbers if n and float(n.replace(',', '')) > 0]
                
                if numbers:
                    current_value = max(numbers) if numbers else 0
                    holdings.append({
                        'fund_name': line.strip()[:80],
                        'folio': '',
                        'amc': determine_amc(line),
                        'category': determine_category(line),
                        'style': determine_style(line),
                        'units': 0,
                        'nav': 0,
                        'invested': current_value * 0.9,  # Estimate
                        'current_value': current_value,
                        'return_1y': '-',
                        'return_3y': '-',
                        'alpha': '-'
                    })
                break
    
    return holdings


def determine_amc(fund_name: str) -> str:
    """Determine AMC from fund name"""
    amc_patterns = {
        'HDFC': 'HDFC AMC',
        'ICICI': 'ICICI Prudential',
        'SBI': 'SBI Mutual Fund',
        'Axis': 'Axis AMC',
        'Kotak': 'Kotak Mahindra',
        'Nippon': 'Nippon India',
        'Aditya Birla': 'Aditya Birla Sun Life',
        'UTI': 'UTI AMC',
        'DSP': 'DSP Mutual Fund',
        'Tata': 'Tata AMC',
        'Mirae': 'Mirae Asset',
        'Motilal': 'Motilal Oswal',
        'Parag Parikh': 'PPFAS AMC',
        'PPFAS': 'PPFAS AMC',
        'Quant': 'Quant MF',
        'Invesco': 'Invesco India',
        'Bandhan': 'Bandhan MF',
        'Edelweiss': 'Edelweiss AMC',
        'Franklin': 'Franklin Templeton',
        'HSBC': 'HSBC AMC',
        'Navi': 'Navi AMC',
        'Groww': 'Groww MF'
    }
    
    fund_lower = fund_name.lower()
    for pattern, amc in amc_patterns.items():
        if pattern.lower() in fund_lower:
            return amc
    return 'Other'


def determine_category(fund_name: str) -> str:
    """Determine category from fund name"""
    fund_lower = fund_name.lower()
    
    if 'large cap' in fund_lower or 'largecap' in fund_lower:
        return 'Large Cap'
    elif 'mid cap' in fund_lower or 'midcap' in fund_lower:
        return 'Mid Cap'
    elif 'small cap' in fund_lower or 'smallcap' in fund_lower:
        return 'Small Cap'
    elif 'flexi' in fund_lower or 'flexicap' in fund_lower:
        return 'Flexi Cap'
    elif 'multi' in fund_lower:
        return 'Multi Cap'
    elif 'large & mid' in fund_lower or 'large and mid' in fund_lower:
        return 'Large & Mid'
    elif 'elss' in fund_lower or 'tax' in fund_lower:
        return 'ELSS'
    elif 'liquid' in fund_lower or 'money market' in fund_lower:
        return 'Liquid'
    elif 'debt' in fund_lower or 'bond' in fund_lower or 'gilt' in fund_lower:
        return 'Debt'
    elif 'hybrid' in fund_lower or 'balanced' in fund_lower:
        return 'Hybrid'
    elif 'international' in fund_lower or 'global' in fund_lower or 'nasdaq' in fund_lower or 'us ' in fund_lower:
        return 'International'
    elif 'sector' in fund_lower or 'banking' in fund_lower or 'pharma' in fund_lower or 'it ' in fund_lower or 'digital' in fund_lower:
        return 'Sectoral'
    elif 'contra' in fund_lower or 'value' in fund_lower:
        return 'Contra'
    elif 'focused' in fund_lower:
        return 'Focused'
    else:
        return 'Equity'


def determine_style(fund_name: str, category: str = '') -> str:
    """Determine investment style from fund name and category"""
    fund_lower = fund_name.lower()
    cat_lower = (category or '').lower()
    combined = fund_lower + ' ' + cat_lower
    
    # Passive / Index
    if any(kw in combined for kw in ['index', 'nifty', 'sensex', 'nasdaq', 'etf', 's&p', 'bse']):
        return 'Passive'
    # Momentum
    if any(kw in combined for kw in ['quant', 'momentum']):
        return 'Momentum'
    # Value / Contra
    if any(kw in combined for kw in ['contra', 'value', 'dividend yield']):
        return 'Value'
    # Liquid / Debt
    if any(kw in combined for kw in ['liquid', 'money market', 'overnight', 'debt', 'bond',
                                      'gilt', 'corporate bond', 'dynamic bond', 'credit risk',
                                      'floater', 'ultra short', 'low duration']):
        return 'Liquid'
    # Sectoral / Thematic
    if any(kw in combined for kw in ['sector', 'thematic', 'banking', 'pharma', 'digital',
                                      'infra', 'consumption', 'manufacturing', 'energy',
                                      'commodit', 'esg', 'technology', 'healthcare']):
        return 'Sectoral'
    # Quality Growth
    if any(kw in combined for kw in ['quality', 'focused', 'motilal', 'icici pru blue']):
        return 'Quality'
    # GARP (Growth at Reasonable Price)
    if any(kw in combined for kw in ['parag parikh', 'ppfas', 'flexi', 'multi cap',
                                      'hdfc flexi', 'growth']):
        return 'GARP'
    # Hybrid / Balanced — map to Blend
    if any(kw in combined for kw in ['hybrid', 'balanced', 'advantage', 'arbitrage',
                                      'equity saving', 'aggressive hybrid']):
        return 'Blend'
    # ELSS
    if any(kw in combined for kw in ['elss', 'tax sav']):
        return 'GARP'
    
    return 'Blend'


def clean_fund_name(name: str) -> str:
    """Clean and normalize fund name"""
    # Remove extra whitespace
    name = ' '.join(name.split())
    # Remove common suffixes that are redundant
    name = re.sub(r'\s*-?\s*(Direct|Regular)\s*(Plan|Growth|Dividend)?\s*$', '', name, flags=re.IGNORECASE)
    return name.strip()


# ============ API Endpoints ============

@router.post("/excel")
async def upload_excel(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_optional_current_user)
):
    """
    Upload Excel/CSV file containing portfolio data
    
    Expected columns:
    - Fund Name (required)
    - AMC / Fund House
    - Category (Large Cap, Mid Cap, Small Cap, etc.)
    - Invested / Amount Invested
    - Current Value
    - 1Y Return, 3Y Return, Alpha (optional)
    - Style (GARP, Momentum, Quality, etc.)
    - Saves to database if user is authenticated
    """
    if not file.filename or not file.filename.endswith(('.xlsx', '.xls', '.csv')):
        raise HTTPException(status_code=400, detail="Please upload an Excel (.xlsx, .xls) or CSV file")
    
    content = await file.read()
    result = parse_excel(content, file.filename)
    
    # Helper function to safely convert to float
    def safe_float(value, default=None):
        """Convert value to float, handling strings with % and special chars"""
        if value is None:
            return default
        if isinstance(value, (int, float)):
            return float(value)
        if isinstance(value, str):
            value = value.strip()
            if value in ['-', '', 'N/A', 'NA', 'null', 'None']:
                return default
            # Remove % sign if present
            value = value.rstrip('%')
            try:
                return float(value)
            except (ValueError, TypeError):
                return default
        return default
    
    # Save to database if user is authenticated
    if current_user:
        try:
            # Calculate totals
            total_invested = sum(safe_float(h.get('invested'), 0) for h in result['holdings'])
            total_current = sum(safe_float(h.get('current_value'), 0) for h in result['holdings'])
            total_gain = total_current - total_invested
            
            # Create a new portfolio snapshot
            portfolio = Portfolio(
                user_id=current_user.id,
                name="Excel Upload",
                source="excel",
                total_invested=total_invested,
                total_current=total_current,
                total_gain=total_gain
            )
            db.add(portfolio)
            db.flush()  # Get portfolio.id
            
            # Save each holding
            for holding in result['holdings']:
                invested = safe_float(holding.get('invested'), 0)
                current_value = safe_float(holding.get('current_value'), 0)
                gain_loss = current_value - invested
                return_pct = ((current_value - invested) / invested * 100) if invested > 0 else 0
                
                holding_entry = Holding(
                    user_id=current_user.id,
                    portfolio_id=portfolio.id,
                    fund_name=holding.get('fund_name', ''),
                    units=safe_float(holding.get('units'), 0),
                    nav=safe_float(holding.get('nav'), 0),
                    invested_amount=invested,
                    current_value=current_value,
                    gain_loss=gain_loss,
                    return_pct=return_pct,
                    amc=holding.get('amc', ''),
                    category=holding.get('category', ''),
                    one_year_return=safe_float(holding.get('return_1y')),
                    three_year_return=safe_float(holding.get('return_3y')),
                    alpha=safe_float(holding.get('alpha')),
                    investment_style=holding.get('style')
                )
                db.add(holding_entry)
            
            db.commit()
            logger.info(f"✅ Saved portfolio {portfolio.id} with {len(result['holdings'])} holdings from Excel for user {current_user.id}")
            result['saved_to_database'] = True
            result['portfolio_id'] = portfolio.id
            
        except Exception as e:
            db.rollback()
            logger.error(f"Error saving Excel portfolio to database: {str(e)}")
            result['saved_to_database'] = False
            result['save_error'] = str(e)
    else:
        logger.info("No authenticated user, returning parsed Excel data for client-side storage")
        result['saved_to_database'] = False
    
    return result


@router.post("/cas")
async def upload_cas(
    file: UploadFile = File(...),
    password: Optional[str] = Form(None),
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_optional_current_user)
):
    """
    Upload CAMS/KFintech CAS PDF statement
    
    - Most CAS PDFs are password protected
    - Provide PDF password as parameter
    - Password is typically your PAN or date of birth
    - Saves portfolio data to database if user is authenticated
    """
    logger.debug(f"CAS upload endpoint called - File: {file.filename}, User: {current_user.email if current_user else 'None'}")
    
    if not file.filename or not file.filename.endswith('.pdf'):
        raise HTTPException(status_code=400, detail="Please upload a PDF file")
    
    content = await file.read()
    logger.debug(f"PDF content read: {len(content)} bytes")
    
    result = parse_cas_pdf(content, password)
    logger.debug(f"CAS parsed successfully: {len(result['holdings'])} holdings found")
    
    # Save to database if user is authenticated
    if current_user:
        logger.info(f"Authenticated user found: {current_user.email} (ID: {current_user.id})")
        try:
            # Calculate totals
            total_invested = sum(h.get('invested', 0) for h in result['holdings'])
            total_current = sum(h.get('current_value', 0) for h in result['holdings'])
            total_gain = total_current - total_invested
            
            # Create a new portfolio snapshot
            portfolio = Portfolio(
                user_id=current_user.id,
                name="CAS Upload",
                source="cas_pdf",
                total_invested=total_invested,
                total_current=total_current,
                total_gain=total_gain
            )
            db.add(portfolio)
            db.flush()  # Get portfolio.id
            
            logger.debug(f"Created portfolio snapshot ID: {portfolio.id}")
            
            # Save each holding
            for idx, holding in enumerate(result['holdings']):
                logger.debug(f"Saving holding {idx+1}/{len(result['holdings'])}: {holding.get('fund_name', 'Unknown')}")
                holding_entry = Holding(
                    user_id=current_user.id,
                    portfolio_id=portfolio.id,
                    fund_name=holding.get('fund_name', ''),
                    folio_number=holding.get('folio', ''),
                    units=holding.get('units', 0),
                    nav=holding.get('nav', 0),
                    invested_amount=holding.get('invested', 0),
                    current_value=holding.get('current_value', 0),
                    gain_loss=holding.get('current_value', 0) - holding.get('invested', 0),
                    return_pct=((holding.get('current_value', 0) - holding.get('invested', 0)) / holding.get('invested', 1) * 100) if holding.get('invested', 0) > 0 else 0,
                    amc=holding.get('amc', ''),
                    category=holding.get('category', '')
                )
                db.add(holding_entry)
            
            db.commit()
            logger.info(f"✅ Successfully saved portfolio {portfolio.id} with {len(result['holdings'])} holdings for user {current_user.id}")
            result['saved_to_database'] = True
            result['user_email'] = current_user.email
            result['portfolio_id'] = portfolio.id
            
        except Exception as e:
            db.rollback()
            logger.error(f"❌ Error saving portfolio to database: {str(e)}", exc_info=True)
            result['saved_to_database'] = False
            result['save_error'] = str(e)
    else:
        logger.warning("⚠️  No authenticated user found - data will not be saved to database")
        result['saved_to_database'] = False
        result['auth_required'] = True
    
    logger.debug(f"Returning result: saved={result.get('saved_to_database')}")
    return result


@router.get("/template")
async def download_template():
    """Download Excel template for portfolio upload"""
    template_data = {
        'Fund Name': [
            'Parag Parikh Flexi Cap Fund Direct Growth',
            'HDFC Mid-Cap Opportunities Direct Growth',
            'Quant Small Cap Fund Direct Growth'
        ],
        'AMC': ['PPFAS AMC', 'HDFC AMC', 'Quant MF'],
        'Category': ['Flexi Cap', 'Mid Cap', 'Small Cap'],
        'Invested': [500000, 300000, 200000],
        'Current Value': [650000, 380000, 185000],
        '1Y Return': ['12.5%', '15.3%', '-5.2%'],
        '3Y Return': ['18.2%', '22.1%', '25.8%'],
        'Alpha': [5.2, 7.1, 3.5],
        'Style': ['GARP', 'Quality', 'Momentum']
    }
    
    df = pd.DataFrame(template_data)
    
    # Create Excel in memory
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Portfolio')
    output.seek(0)
    
    from fastapi.responses import StreamingResponse
    return StreamingResponse(
        output,
        media_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        headers={'Content-Disposition': 'attachment; filename=portfolio_template.xlsx'}
    )


@router.get("/cas-info")
async def cas_info():
    """Information about how to get CAS statement"""
    return {
        "title": "How to get your CAS (Consolidated Account Statement)",
        "steps": [
            "Visit CAMS Online (camsonline.com) or KFintech (kfintech.com)",
            "Go to 'Investor Services' > 'Account Statement'",
            "Enter your Email and PAN",
            "Select 'Detailed' statement type",
            "Select date range (suggest: Since inception)",
            "Submit - CAS will be emailed within minutes",
            "CAS PDF password is your PAN number"
        ],
        "links": {
            "cams": "https://www.camsonline.com/Investors/Statements/Consolidated-Account-Statement",
            "kfintech": "https://mfs.kfintech.com/investor/General/ConsolidatedAccountStatement"
        },
        "note": "CAS covers all mutual funds across all AMCs linked to your PAN"
    }
