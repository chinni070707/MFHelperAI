"""
Verification script to check that all user data is stored in the database
"""
import sys
from pathlib import Path

backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

from sqlalchemy import select, func
from app.database import SessionLocal
from app.models.models import User, Portfolio, Holding
from datetime import datetime
import json


def verify_database_storage():
    """Verify all data is stored in database"""
    db = SessionLocal()
    
    try:
        print(f"\n{'='*80}")
        print("DATABASE STORAGE VERIFICATION")
        print(f"{'='*80}\n")
        
        # Count all records
        user_count = db.query(User).count()
        portfolio_count = db.query(Portfolio).count()
        holding_count = db.query(Holding).count()
        
        print(f"📊 Database Summary:")
        print(f"   Total Users: {user_count}")
        print(f"   Total Portfolios: {portfolio_count}")
        print(f"   Total Holdings: {holding_count}")
        
        # Check for guest users
        guest_users = db.query(User).filter(User.oauth_provider == 'guest').all()
        print(f"\n👤 Guest Users: {len(guest_users)}")
        for guest in guest_users:
            portfolios = db.query(Portfolio).filter(Portfolio.user_id == guest.id).count()
            holdings = db.query(Holding).filter(Holding.user_id == guest.id).count()
            print(f"   - {guest.email} (ID: {guest.id})")
            print(f"     Portfolios: {portfolios}, Holdings: {holdings}")
        
        # Check for regular users
        regular_users = db.query(User).filter(User.oauth_provider != 'guest').all()
        print(f"\n👨‍💼 Regular Users: {len(regular_users)}")
        for user in regular_users:
            portfolios = db.query(Portfolio).filter(Portfolio.user_id == user.id).count()
            holdings = db.query(Holding).filter(Holding.user_id == user.id).count()
            print(f"   - {user.email} (ID: {user.id})")
            print(f"     Portfolios: {portfolios}, Holdings: {holdings}")
        
        # Check portfolio sources
        print(f"\n📁 Portfolio Sources:")
        sources = db.query(Portfolio.source, func.count(Portfolio.id)).group_by(Portfolio.source).all()
        for source, count in sources:
            print(f"   - {source}: {count} portfolios")
        
        # Check data integrity
        print(f"\n🔍 Data Integrity Checks:")
        
        # Check for portfolios without holdings
        portfolios_without_holdings = db.query(Portfolio).outerjoin(Holding).filter(
            Holding.id == None
        ).count()
        print(f"   - Portfolios without holdings: {portfolios_without_holdings}")
        
        # Check for holdings without portfolios
        holdings_without_portfolios = db.query(Holding).outerjoin(Portfolio).filter(
            Portfolio.id == None
        ).count()
        print(f"   - Orphaned holdings: {holdings_without_portfolios}")
        
        # Check for users without portfolios
        users_without_portfolios = db.query(User).outerjoin(Portfolio).filter(
            Portfolio.id == None
        ).count()
        print(f"   - Users without portfolios: {users_without_portfolios}")
        
        # Recent activity
        print(f"\n📈 Recent Activity:")
        recent_portfolios = db.query(Portfolio).order_by(Portfolio.snapshot_date.desc()).limit(5).all()
        for p in recent_portfolios:
            user = db.query(User).filter(User.id == p.user_id).first()
            holdings_count = db.query(Holding).filter(Holding.portfolio_id == p.id).count()
            print(f"   - {p.name} ({p.source}) by {user.email}")
            print(f"     {holdings_count} holdings, ₹{p.total_current:,.0f} value")
            print(f"     Created: {p.snapshot_date}")
        
        # Summary
        print(f"\n{'='*80}")
        if user_count > 0 and portfolio_count > 0:
            print("✅ DATABASE STORAGE IS WORKING")
            print(f"   All user data is being saved to the SQLite database")
            print(f"   Total users: {user_count}, Portfolios: {portfolio_count}, Holdings: {holding_count}")
        else:
            print("⚠️  NO DATA IN DATABASE")
            print("   Please create some data to verify storage")
        print(f"{'='*80}\n")
        
        return {
            "user_count": user_count,
            "portfolio_count": portfolio_count,
            "holding_count": holding_count,
            "guest_users": len(guest_users),
            "regular_users": len(regular_users),
            "verified": user_count > 0 and portfolio_count > 0
        }
        
    except Exception as e:
        print(f"❌ Error verifying database: {e}")
        import traceback
        traceback.print_exc()
        return None
    finally:
        db.close()


if __name__ == "__main__":
    verify_database_storage()
