"""
Quick Database Reset and Setup
"""
import os
import sys

# Change to backend directory
os.chdir(os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy import create_engine, inspect
from app.config import settings
from app.database import Base

# Import all models
from app.models.models import User, Portfolio, UserSettings, Holding, Transaction, FundMaster
from app.models.demo_portfolio import DemoPortfolio
from app.models.user_leads import UserLead

def main():
    print("=" * 60)
    print("DATABASE RESET")
    print("=" * 60)
    
    # Delete existing database
    db_file = settings.DATABASE_URL.replace("sqlite:///", "")
    if os.path.exists(db_file):
        os.remove(db_file)
        print(f"✓ Deleted: {db_file}")
    
    # Create engine and all tables
    engine = create_engine(settings.DATABASE_URL)
    Base.metadata.create_all(bind=engine)
    
    # Verify tables
    inspector = inspect(engine)
    tables = inspector.get_table_names()
    
    print(f"\n✓ Created {len(tables)} tables:")
    for table in tables:
        columns = [col['name'] for col in inspector.get_columns(table)]
        print(f"  - {table} ({len(columns)} columns)")
    
    print("\n" + "=" * 60)
    print("✅ Database ready!")
    print("=" * 60)

if __name__ == "__main__":
    main()
