"""
Fetch Real Mutual Fund Data from AMFI India
AMFI (Association of Mutual Funds in India) provides official NAV data
"""
import requests
import pandas as pd
from datetime import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import logging

from app.database import engine
from app.config import settings
from app.models.models import FundMaster

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# AMFI NAV data URL
AMFI_NAV_URL = "https://www.amfiindia.com/spages/NAVAll.txt"

def fetch_amfi_data():
    """Fetch mutual fund data from AMFI"""
    try:
        logger.info("Fetching mutual fund data from AMFI India...")
        response = requests.get(AMFI_NAV_URL, timeout=30)
        response.raise_for_status()
        
        # Parse the text file
        lines = response.text.strip().split('\n')
        
        funds = []
        current_amc = None
        
        for line in lines:
            line = line.strip()
            
            # Skip empty lines and header
            if not line or 'Scheme Code' in line:
                continue
            
            # AMC names are lines without semicolons
            if ';' not in line:
                current_amc = line
                continue
            
            # Parse fund data
            try:
                parts = line.split(';')
                if len(parts) >= 5:
                    scheme_code = parts[0].strip()
                    isin = parts[1].strip() if len(parts) > 1 else None
                    isin_reinvest = parts[2].strip() if len(parts) > 2 else None
                    scheme_name = parts[3].strip()
                    nav = parts[4].strip()
                    
                    # Try to parse NAV
                    try:
                        nav_value = float(nav) if nav and nav != 'N.A.' else None
                    except:
                        nav_value = None
                    
                    # Categorize by scheme name keywords
                    scheme_lower = scheme_name.lower()
                    
                    # Determine category
                    if 'equity' in scheme_lower or 'stock' in scheme_lower:
                        if 'large cap' in scheme_lower or 'bluechip' in scheme_lower:
                            category = 'Equity - Large Cap'
                        elif 'mid cap' in scheme_lower:
                            category = 'Equity - Mid Cap'
                        elif 'small cap' in scheme_lower:
                            category = 'Equity - Small Cap'
                        elif 'flexi' in scheme_lower or 'multi cap' in scheme_lower:
                            category = 'Equity - Flexi Cap'
                        else:
                            category = 'Equity - Others'
                    elif 'debt' in scheme_lower or 'bond' in scheme_lower or 'income' in scheme_lower:
                        category = 'Debt'
                    elif 'liquid' in scheme_lower:
                        category = 'Liquid'
                    elif 'hybrid' in scheme_lower or 'balanced' in scheme_lower:
                        category = 'Hybrid'
                    elif 'index' in scheme_lower:
                        category = 'Index'
                    elif 'elss' in scheme_lower or 'tax saver' in scheme_lower:
                        category = 'ELSS'
                    else:
                        category = 'Others'
                    
                    # Determine plan type
                    if 'direct' in scheme_lower:
                        plan_type = 'Direct'
                    else:
                        plan_type = 'Regular'
                    
                    funds.append({
                        'scheme_code': scheme_code,
                        'isin': isin or isin_reinvest,
                        'scheme_name': scheme_name,
                        'amc': current_amc,
                        'category': category,
                        'current_nav': nav_value,
                        'plan_type': plan_type,
                        'is_active': True
                    })
            except Exception as e:
                logger.warning(f"Error parsing line: {line[:50]}... - {e}")
                continue
        
        logger.info(f"Successfully parsed {len(funds)} mutual funds")
        return funds
        
    except Exception as e:
        logger.error(f"Error fetching AMFI data: {e}")
        return None

def load_funds_to_database(funds):
    """Load funds data into database"""
    db = None
    try:
        from app.database import SessionLocal
        db = SessionLocal()
        
        logger.info("Loading funds into database...")
        
        # Clear existing data
        db.query(FundMaster).delete()
        
        # Add new funds
        count = 0
        for fund_data in funds:
            fund = FundMaster(**fund_data)
            db.add(fund)
            count += 1
            
            if count % 1000 == 0:
                db.commit()
                logger.info(f"Loaded {count} funds...")
        
        db.commit()
        db.close()
        
        logger.info(f"✓ Successfully loaded {count} mutual funds into database")
        return count
        
    except Exception as e:
        logger.error(f"Error loading funds to database: {e}")
        if db:
            db.rollback()
            db.close()
        return 0

def get_fund_statistics(funds):
    """Get statistics about loaded funds"""
    df = pd.DataFrame(funds)
    
    print("\n" + "=" * 60)
    print("MUTUAL FUND DATA STATISTICS")
    print("=" * 60)
    print(f"\nTotal Funds: {len(funds)}")
    print(f"\nFunds by Category:")
    print(df['category'].value_counts().to_string())
    print(f"\nFunds by Plan Type:")
    print(df['plan_type'].value_counts().to_string())
    print(f"\nTop 10 AMCs by Fund Count:")
    print(df['amc'].value_counts().head(10).to_string())
    print(f"\nFunds with NAV data: {df['current_nav'].notna().sum()}")
    print("=" * 60)

def main():
    """Main function to fetch and load mutual fund data"""
    print("\n🚀 Fetching Real Mutual Fund Data from AMFI India\n")
    
    # Fetch data
    funds = fetch_amfi_data()
    
    if not funds:
        print("❌ Failed to fetch mutual fund data")
        return
    
    # Show statistics
    get_fund_statistics(funds)
    
    # Load to database
    print("\n📊 Loading data into database...\n")
    count = load_funds_to_database(funds)
    
    if count > 0:
        print(f"\n✅ SUCCESS! Loaded {count} mutual funds into database")
        print("\nYou can now:")
        print("  1. Start the server: python -m uvicorn app.main:app --reload")
        print("  2. Test fund search: http://localhost:8000/api/funds/list")
        print("  3. Search by name: http://localhost:8000/api/funds/list?search=HDFC")
    else:
        print("\n❌ Failed to load funds into database")

if __name__ == "__main__":
    main()
