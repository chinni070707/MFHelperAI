"""
Direct test of CAS import to database without API
"""
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from casparser import read_cas_pdf

# Import the service
from app.services.cas_import import import_cas_to_database, import_cas_transactions

# Configuration
CAS_PDF_PATH = r"c:\Users\mahchi01\Downloads\CAS\KFINTECH_97924150102202603102380252686267905.pdf"
PASSWORD = "Mahesh@1234"
TEST_USER_ID = 1  # Use test user ID

print("🧪 Testing Direct CAS Import to Database")
print("=" * 80)

# Create database session
DATABASE_URL = "sqlite:///./test_cas_import.db"
engine = create_engine(DATABASE_URL)

# Import models to create tables
from app.models.models import Base, Portfolio, Holding, Transaction
Base.metadata.create_all(bind=engine)

SessionLocal = sessionmaker(bind=engine)
db = SessionLocal()

print(f"📄 CAS file: {CAS_PDF_PATH}")
print(f"🔐 Password: {PASSWORD}")
print()

try:
    # Parse CAS PDF
    print("🔍 Parsing CAS PDF...")
    cas_data = read_cas_pdf(CAS_PDF_PATH, password=PASSWORD)
    print(f"✅ Successfully parsed CAS")
    print(f"   Investor: {cas_data.investor_info.name if cas_data.investor_info else 'N/A'}")
    print(f"   Folios: {len(cas_data.folios)}")
    print()
    
    # Import to database
    print("💾 Importing to database...")
    portfolio_id = import_cas_to_database(
        cas_data=cas_data,
        user_id=TEST_USER_ID,
        db=db
    )
    print(f"✅ Portfolio created with ID: {portfolio_id}")
    
    # Get portfolio from database
    portfolio = db.query(Portfolio).filter(Portfolio.id == portfolio_id).first()
    if portfolio:
        print()
        print("📊 Portfolio Summary:")
        print(f"   Name: {portfolio.name}")
        print(f"   Total Invested: ₹{portfolio.total_invested:,.2f}")
        print(f"   Current Value: ₹{portfolio.total_current:,.2f}")
        print(f"   Gain/Loss: ₹{portfolio.total_gain_loss:,.2f}")
        print(f"   Return: {portfolio.total_return_pct:.2f}%")
        print(f"   Holdings Count: {len(portfolio.holdings)}")
    
    # Import transactions
    print()
    print("📝 Importing transactions...")
    txn_count = import_cas_transactions(
        cas_data=cas_data,
        portfolio_id=portfolio_id,
        db=db
    )
    print(f"✅ Imported {txn_count} transactions")
    
    # Show sample holdings
    print()
    print("💰 Sample Holdings (first 5):")
    holdings = db.query(Holding).filter(Holding.portfolio_id == portfolio_id).limit(5).all()
    for i, holding in enumerate(holdings, 1):
        print(f"   {i}. {holding.fund_name[:60]}")
        print(f"      Units: {holding.units:,.3f} | NAV: ₹{holding.nav:.4f}")
        print(f"      Invested: ₹{holding.invested_amount:,.2f} | Current: ₹{holding.current_value:,.2f}")
        print(f"      Gain/Loss: ₹{holding.current_value - holding.invested_amount:,.2f}")
        print()
    
    print("=" * 80)
    print("✅ CAS import successful!")
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
finally:
    db.close()
