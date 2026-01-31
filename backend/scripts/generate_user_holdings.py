"""
Extract fund names from user's Excel and create sample holdings database
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pandas as pd
import json
from datetime import datetime

# Path to user's Excel file
EXCEL_PATH = r"C:\Users\mahchi01\Downloads\Chinni Mahesh Portfolio review Jan 2026 - Updated.xlsx"
OUTPUT_JSON = os.path.join(os.path.dirname(__file__), "..", "data", "fund_holdings.json")

# Sample stock universe for generating holdings
LARGE_CAP_STOCKS = [
    ("HDFC Bank", "Banking"), ("ICICI Bank", "Banking"), ("State Bank of India", "Banking"),
    ("Kotak Mahindra Bank", "Banking"), ("Axis Bank", "Banking"),
    ("Reliance Industries", "Oil & Gas"), ("TCS", "IT"), ("Infosys", "IT"),
    ("HCL Technologies", "IT"), ("Wipro", "IT"), ("Tech Mahindra", "IT"),
    ("ITC", "FMCG"), ("Hindustan Unilever", "FMCG"), ("Nestle India", "FMCG"),
    ("Bharti Airtel", "Telecom"), ("Larsen & Toubro", "Capital Goods"),
    ("Asian Paints", "Paints"), ("Maruti Suzuki", "Auto"), ("Bajaj Finance", "NBFC"),
    ("UltraTech Cement", "Cement")
]

MID_CAP_STOCKS = [
    ("Tata Motors", "Auto"), ("Max Healthcare", "Healthcare"), ("Persistent Systems", "IT"),
    ("Bajaj Auto", "Auto"), ("Crompton Greaves", "Consumer Durables"),
    ("Dixon Technologies", "Electronics"), ("PI Industries", "Chemicals"),
    ("Escorts Kubota", "Auto"), ("Federal Bank", "Banking"), ("Coforge", "IT"),
    ("Phoenix Mills", "Real Estate"), ("Voltas", "Consumer Durables"),
    ("Godrej Properties", "Real Estate"), ("Mphasis", "IT"), ("ABB India", "Capital Goods")
]

SMALL_CAP_STOCKS = [
    ("Rainbow Children's", "Healthcare"), ("Ratnamani Metals", "Metals"),
    ("KEC International", "Capital Goods"), ("DCM Shriram", "Chemicals"),
    ("Tube Investments", "Auto Components"), ("CEAT", "Auto Components"),
    ("Nazara Technologies", "IT"), ("Alkyl Amines", "Chemicals"),
    ("Polycab India", "Capital Goods"), ("Linde India", "Chemicals"),
    ("KPIT Technologies", "IT"), ("Blue Star", "Capital Goods"),
    ("Solar Industries", "Chemicals"), ("JK Cement", "Cement")
]

def normalize_fund_name(name):
    """Convert fund name to key format"""
    return name.lower()\
        .replace("fund", "")\
        .replace("(", "").replace(")", "")\
        .replace("-", " ")\
        .strip()\
        .replace(" ", "-")

def categorize_fund(fund_name):
    """Categorize fund by name"""
    name_lower = fund_name.lower()
    
    if any(x in name_lower for x in ["small", "smallcap"]):
        return "Small Cap", SMALL_CAP_STOCKS
    elif any(x in name_lower for x in ["mid", "midcap", "emerging"]):
        return "Mid Cap", MID_CAP_STOCKS
    elif any(x in name_lower for x in ["large", "bluechip", "blue chip"]):
        return "Large Cap", LARGE_CAP_STOCKS
    elif any(x in name_lower for x in ["flexi", "multi", "multicap"]):
        return "Flexi Cap", LARGE_CAP_STOCKS + MID_CAP_STOCKS[:5]
    else:
        return "Flexi Cap", LARGE_CAP_STOCKS + MID_CAP_STOCKS[:5]

def extract_amc(fund_name):
    """Extract AMC name from fund name"""
    amc_keywords = [
        "HDFC", "ICICI", "SBI", "Axis", "Kotak", "Parag Parikh", "PPFAS",
        "Mirae", "Nippon", "UTI", "DSP", "Franklin", "Aditya Birla", "Tata",
        "Motilal", "Quant", "Canara", "Bank of India", "L&T", "HSBC"
    ]
    
    for keyword in amc_keywords:
        if keyword.lower() in fund_name.lower():
            return keyword + " Mutual Fund"
    
    # Default to first word
    return fund_name.split()[0] + " Mutual Fund"

def generate_holdings(category, stock_pool, num_holdings=10):
    """Generate realistic holdings for a fund"""
    import random
    
    # Shuffle and pick stocks
    selected = random.sample(stock_pool, min(num_holdings, len(stock_pool)))
    
    # Generate weights that sum to ~60-70% (rest is cash/other)
    if category == "Large Cap":
        # More concentrated
        weights = [random.uniform(4, 10) for _ in range(num_holdings)]
    elif category == "Mid Cap":
        weights = [random.uniform(3, 6) for _ in range(num_holdings)]
    else:  # Small Cap or Flexi
        weights = [random.uniform(2, 5) for _ in range(num_holdings)]
    
    # Normalize to 60-70%
    total = sum(weights)
    target = random.uniform(60, 70)
    weights = [w / total * target for w in weights]
    
    # Sort by weight descending
    holdings_data = [
        {"stock": stock, "weight": round(weight, 2), "sector": sector}
        for (stock, sector), weight in zip(selected, weights)
    ]
    holdings_data.sort(key=lambda x: x["weight"], reverse=True)
    
    return holdings_data

def calculate_sector_allocation(holdings):
    """Calculate sector allocation from holdings"""
    sectors = {}
    for holding in holdings:
        sector = holding["sector"]
        weight = holding["weight"]
        sectors[sector] = sectors.get(sector, 0) + weight
    
    # Add "Others" for remaining
    total = sum(sectors.values())
    if total < 100:
        sectors["Others"] = round(100 - total, 2)
    
    return sectors

def extract_funds_from_excel():
    """Extract unique fund names from Excel"""
    try:
        # Read Excel, skip first 2 rows (title and blank)
        df = pd.read_excel(EXCEL_PATH, header=2)
        
        print(f"📋 Excel shape: {df.shape}")
        print(f"📊 First few rows of each column:")
        for i, col in enumerate(df.columns[:5]):
            vals = df[col].dropna().head(3).tolist()
            print(f"   Column {i} ({col}): {vals}")
        
        # Fund names are typically in column with "Fund Name" or in column 2
        fund_col = None
        
        # Check each column for fund names
        for col in df.columns:
            sample_vals = df[col].dropna().astype(str).head(10).tolist()
            # Check if this column has fund names (contains words like "Growth", "Plan", "Direct")
            if any('growth' in str(v).lower() or 'plan' in str(v).lower() or 'direct' in str(v).lower() 
                   for v in sample_vals):
                fund_col = col
                break
        
        if fund_col is None:
            # Default to column 2 (Unnamed: 2)
            fund_col = df.columns[2] if len(df.columns) > 2 else df.columns[0]
        
        print(f"✅ Using column: '{fund_col}'")
        
        # Extract fund names, remove NaN and empty strings
        funds = df[fund_col].dropna().astype(str).str.strip()
        # Remove header row if it exists
        funds = [f for f in funds if f and f != 'nan' and f != 'Fund Name' and len(f) > 5]
        funds = list(set(funds))  # Remove duplicates
        
        print(f"\n✅ Found {len(funds)} unique funds in Excel:")
        for i, fund in enumerate(funds, 1):
            print(f"   {i}. {fund}")
        
        return funds
        
    except Exception as e:
        print(f"❌ Error reading Excel: {e}")
        import traceback
        traceback.print_exc()
        return []

def create_holdings_database():
    """Create holdings database from user's Excel"""
    print("🚀 Creating holdings database from your portfolio...\n")
    
    # Extract fund names from Excel
    fund_names = extract_funds_from_excel()
    
    if not fund_names:
        print("❌ No funds found in Excel")
        return
    
    # Load existing JSON if exists
    if os.path.exists(OUTPUT_JSON):
        with open(OUTPUT_JSON, 'r', encoding='utf-8') as f:
            data = json.load(f)
    else:
        data = {
            "version": "2026-01",
            "last_updated": datetime.now().strftime("%Y-%m-%d"),
            "source": "Generated from user portfolio",
            "funds": {}
        }
    
    # Generate holdings for each fund
    for fund_name in fund_names:
        fund_key = normalize_fund_name(fund_name)
        
        # Skip if already exists
        if fund_key in data["funds"]:
            print(f"⏭️  Skipping {fund_name} (already exists)")
            continue
        
        print(f"📊 Generating holdings for: {fund_name}")
        
        category, stock_pool = categorize_fund(fund_name)
        amc = extract_amc(fund_name)
        
        # Generate holdings
        holdings = generate_holdings(category, stock_pool)
        sector_allocation = calculate_sector_allocation(holdings)
        
        # Add to database
        data["funds"][fund_key] = {
            "name": fund_name,
            "amc": amc,
            "category": category,
            "holdings": holdings,
            "sector_allocation": sector_allocation
        }
        
        print(f"  ✅ Added {len(holdings)} holdings")
    
    # Update timestamp
    data["last_updated"] = datetime.now().strftime("%Y-%m-%d")
    
    # Save to JSON
    with open(OUTPUT_JSON, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    
    print(f"\n✅ Holdings database created: {OUTPUT_JSON}")
    print(f"📈 Total funds in database: {len(data['funds'])}")
    
    return data

if __name__ == "__main__":
    create_holdings_database()
    
    print("\n" + "="*60)
    print("🎯 Next Steps:")
    print("="*60)
    print("1. Review the generated holdings in:")
    print(f"   {OUTPUT_JSON}")
    print("\n2. Load into database:")
    print("   python scripts/load_holdings_to_db.py")
    print("\n3. Start backend and test:")
    print("   uvicorn app.main:app --reload")
    print("   curl http://localhost:8000/api/holdings/")
    print("="*60)
