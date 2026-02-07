"""
Fresh Database Setup
Drops and recreates all tables from scratch
"""
from sqlalchemy import create_engine
from app.database import Base
from app.config import settings

# Import ALL models to register them with Base
from app.models.models import (
    User, Portfolio, UserSettings, Holding, Transaction, FundMaster
)
from app.models.demo_portfolio import DemoPortfolio
from app.models.user_leads import UserLead
import os

def reset_database():
    """Drop and recreate all tables"""
    
    # Close any existing connections
    print("Resetting database...")
    
    # Delete database file if it exists
    db_file = settings.DATABASE_URL.replace("sqlite:///", "")
    if os.path.exists(db_file):
        try:
            os.remove(db_file)
            print(f"[OK] Deleted existing database: {db_file}")
        except Exception as e:
            print(f"[X] Could not delete database (might be in use): {e}")
            print("  Please stop the server first!")
            return False
    
    # Create fresh database with all tables
    engine = create_engine(settings.DATABASE_URL)
    Base.metadata.create_all(bind=engine)
    
    print("\n[OK] Database recreated successfully!")
    print("\nTables created:")
    for table in Base.metadata.sorted_tables:
        print(f"  - {table.name}")
    
    return True

if __name__ == "__main__":
    reset_database()
