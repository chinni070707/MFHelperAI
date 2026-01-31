"""
Seed database with dummy test data
Run from backend directory: python scripts/seed_database.py
Or from root: python -m backend.scripts.seed_database
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from datetime import datetime, timedelta
import sys
import os

# Add backend directory to path if not already there
backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

# Also add parent of backend (root) to handle running from root
root_dir = os.path.dirname(backend_dir)
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

try:
    from app.models.models import User, UserSettings, Portfolio, Holding, Base
    from app.utils.auth import get_password_hash
    from app.config import settings
except ImportError:
    # Try with backend prefix if running from root
    from backend.app.models.models import User, UserSettings, Portfolio, Holding, Base
    from backend.app.utils.auth import get_password_hash
    from backend.app.config import settings

# Create engine
engine = create_engine(settings.DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def seed_database():
    """Seed database with test data"""
    
    # Create tables
    Base.metadata.create_all(bind=engine)
    print("✅ Database tables created")
    
    db = SessionLocal()
    
    try:
        # Check if users already exist
        existing_users = db.query(User).count()
        if existing_users > 0:
            print(f"⚠️  Database already has {existing_users} users. Skipping seed.")
            response = input("Do you want to clear and reseed? (yes/no): ")
            if response.lower() != 'yes':
                return
            
            # Clear existing data
            db.query(Holding).delete()
            db.query(Portfolio).delete()
            db.query(UserSettings).delete()
            db.query(User).delete()
            db.commit()
            print("🗑️  Cleared existing data")
        
        # Create test users
        users_data = [
            {
                "email": "demo@mfhelper.com",
                "password": "Demo@123",
                "full_name": "Demo User",
                "pan": "ABCDE1234F",
                "phone": "+91 98765 43210"
            },
            {
                "email": "test@example.com",
                "password": "Test@123",
                "full_name": "Test User",
                "pan": "XYZAB5678C",
                "phone": "+91 99999 88888"
            },
            {
                "email": "investor@example.com",
                "password": "Invest@123",
                "full_name": "Smart Investor",
                "pan": "PQRST9012D",
                "phone": "+91 88888 77777"
            }
        ]
        
        users = []
        for user_data in users_data:
            user = User(
                email=user_data["email"],
                hashed_password=get_password_hash(user_data["password"]),
                full_name=user_data["full_name"],
                pan=user_data["pan"],
                phone=user_data["phone"],
                is_active=True,
                is_verified=True
            )
            db.add(user)
            db.flush()
            users.append(user)
            
            # Create settings for each user
            settings = UserSettings(
                user_id=user.id,
                theme="light" if user.id == 1 else "dark" if user.id == 2 else "auto",
                language="en",
                currency="INR",
                email_notifications=True,
                portfolio_alerts=True,
                market_updates=False
            )
            db.add(settings)
            
            print(f"✅ Created user: {user_data['email']} (password: {user_data['password']})")
        
        db.commit()
        
        # Create sample portfolios for demo user
        demo_user = users[0]
        
        # Portfolio 1 (Current - February 2026)
        portfolio1 = Portfolio(
            user_id=demo_user.id,
            name="My Portfolio",
            source="excel",
            total_invested=500000,
            total_current=575000,
            total_gain=75000,
            xirr=12.5,
            snapshot_date=datetime.now()
        )
        db.add(portfolio1)
        db.flush()
        
        # Holdings for portfolio 1
        holdings1 = [
            {
                "fund_name": "HDFC Flexi Cap Fund - Direct Plan - Growth",
                "amc": "HDFC Mutual Fund",
                "category": "Flexi Cap",
                "invested_amount": 150000,
                "current_value": 180000,
                "units": 1234.56,
                "nav": 145.80,
                "gain_loss": 30000,
                "return_pct": 20.0,
                "one_year_return": 18.5,
                "three_year_return": 15.2,
                "alpha": 2.3
            },
            {
                "fund_name": "Parag Parikh Flexi Cap Fund - Direct Plan - Growth",
                "amc": "PPFAS Mutual Fund",
                "category": "Flexi Cap",
                "invested_amount": 100000,
                "current_value": 115000,
                "units": 2345.67,
                "nav": 49.05,
                "gain_loss": 15000,
                "return_pct": 15.0,
                "one_year_return": 16.8,
                "three_year_return": 14.5,
                "alpha": 1.8
            },
            {
                "fund_name": "Axis Midcap Fund - Direct Plan - Growth",
                "amc": "Axis Mutual Fund",
                "category": "Mid Cap",
                "invested_amount": 125000,
                "current_value": 145000,
                "units": 1567.89,
                "nav": 92.47,
                "gain_loss": 20000,
                "return_pct": 16.0,
                "one_year_return": 22.3,
                "three_year_return": 18.7,
                "alpha": 3.2
            },
            {
                "fund_name": "Kotak Small Cap Fund - Direct Plan - Growth",
                "amc": "Kotak Mahindra Mutual Fund",
                "category": "Small Cap",
                "invested_amount": 125000,
                "current_value": 135000,
                "units": 8901.23,
                "nav": 15.17,
                "gain_loss": 10000,
                "return_pct": 8.0,
                "one_year_return": 25.6,
                "three_year_return": 20.1,
                "alpha": 4.5
            }
        ]
        
        for holding_data in holdings1:
            holding = Holding(
                user_id=demo_user.id,
                portfolio_id=portfolio1.id,
                **holding_data
            )
            db.add(holding)
        
        print(f"✅ Created current portfolio for {demo_user.email} with {len(holdings1)} holdings")
        
        # Portfolio 2 (Historical - January 2026)
        portfolio2 = Portfolio(
            user_id=demo_user.id,
            name="My Portfolio",
            source="excel",
            total_invested=480000,
            total_current=520000,
            total_gain=40000,
            xirr=10.2,
            snapshot_date=datetime.now() - timedelta(days=30)
        )
        db.add(portfolio2)
        db.flush()
        
        # Holdings for portfolio 2 (slightly different values)
        holdings2 = [
            {
                "fund_name": "HDFC Flexi Cap Fund - Direct Plan - Growth",
                "amc": "HDFC Mutual Fund",
                "category": "Flexi Cap",
                "invested_amount": 150000,
                "current_value": 168000,
                "units": 1234.56,
                "nav": 136.10,
                "gain_loss": 18000,
                "return_pct": 12.0,
                "one_year_return": 16.5,
                "three_year_return": 14.8
            },
            {
                "fund_name": "Parag Parikh Flexi Cap Fund - Direct Plan - Growth",
                "amc": "PPFAS Mutual Fund",
                "category": "Flexi Cap",
                "invested_amount": 100000,
                "current_value": 108000,
                "units": 2345.67,
                "nav": 46.04,
                "gain_loss": 8000,
                "return_pct": 8.0,
                "one_year_return": 14.2,
                "three_year_return": 13.1
            },
            {
                "fund_name": "Axis Midcap Fund - Direct Plan - Growth",
                "amc": "Axis Mutual Fund",
                "category": "Mid Cap",
                "invested_amount": 125000,
                "current_value": 138000,
                "units": 1567.89,
                "nav": 87.99,
                "gain_loss": 13000,
                "return_pct": 10.4,
                "one_year_return": 20.1,
                "three_year_return": 17.3
            },
            {
                "fund_name": "Kotak Small Cap Fund - Direct Plan - Growth",
                "amc": "Kotak Mahindra Mutual Fund",
                "category": "Small Cap",
                "invested_amount": 105000,
                "current_value": 106000,
                "units": 7234.56,
                "nav": 14.65,
                "gain_loss": 1000,
                "return_pct": 0.95,
                "one_year_return": 23.8,
                "three_year_return": 19.2
            }
        ]
        
        for holding_data in holdings2:
            holding = Holding(
                user_id=demo_user.id,
                portfolio_id=portfolio2.id,
                **holding_data
            )
            db.add(holding)
        
        print(f"✅ Created historical portfolio (Jan 2026) for {demo_user.email}")
        
        # Create portfolio for test user
        test_user = users[1]
        portfolio3 = Portfolio(
            user_id=test_user.id,
            name="Test Portfolio",
            source="cas_pdf",
            total_invested=300000,
            total_current=340000,
            total_gain=40000,
            xirr=11.8,
            snapshot_date=datetime.now()
        )
        db.add(portfolio3)
        db.flush()
        
        holdings3 = [
            {
                "fund_name": "SBI Bluechip Fund - Direct Plan - Growth",
                "amc": "SBI Mutual Fund",
                "category": "Large Cap",
                "invested_amount": 200000,
                "current_value": 230000,
                "units": 3456.78,
                "nav": 66.55,
                "gain_loss": 30000,
                "return_pct": 15.0
            },
            {
                "fund_name": "Nippon India Small Cap Fund - Direct Plan - Growth",
                "amc": "Nippon India Mutual Fund",
                "category": "Small Cap",
                "invested_amount": 100000,
                "current_value": 110000,
                "units": 1234.56,
                "nav": 89.11,
                "gain_loss": 10000,
                "return_pct": 10.0
            }
        ]
        
        for holding_data in holdings3:
            holding = Holding(
                user_id=test_user.id,
                portfolio_id=portfolio3.id,
                **holding_data
            )
            db.add(holding)
        
        print(f"✅ Created portfolio for {test_user.email} with {len(holdings3)} holdings")
        
        db.commit()
        
        print("\n" + "="*60)
        print("🎉 Database seeded successfully!")
        print("="*60)
        print("\n📊 Summary:")
        print(f"   Users: {db.query(User).count()}")
        print(f"   Portfolios: {db.query(Portfolio).count()}")
        print(f"   Holdings: {db.query(Holding).count()}")
        print(f"   Settings: {db.query(UserSettings).count()}")
        
        print("\n🔑 Test Accounts:")
        for user_data in users_data:
            print(f"   Email: {user_data['email']}")
            print(f"   Password: {user_data['password']}")
            print()
        
        print("📍 Database Location:")
        print(f"   {settings.DATABASE_URL}")
        print("\n💡 You can now:")
        print("   1. Start the server: uvicorn app.main:app --reload")
        print("   2. Login with any test account")
        print("   3. View portfolios and test features")
        print()
        
    except Exception as e:
        db.rollback()
        print(f"❌ Error seeding database: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed_database()
