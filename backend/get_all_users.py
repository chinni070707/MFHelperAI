"""
Script to retrieve all users from the database
"""
import sys
from pathlib import Path

# Add backend directory to path
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

from sqlalchemy import select
from app.database import SessionLocal, engine
from app.models.models import User, Portfolio, Holding
from datetime import datetime
import json


def get_all_users():
    """Retrieve all users with their portfolio data"""
    db = SessionLocal()
    
    try:
        # Query all users
        users = db.query(User).all()
        
        print(f"\n{'='*80}")
        print(f"DATABASE USERS - Total: {len(users)}")
        print(f"{'='*80}\n")
        
        user_data_list = []
        
        for user in users:
            # Get portfolio count
            portfolio_count = db.query(Portfolio).filter(
                Portfolio.user_id == user.id
            ).count()
            
            # Get holdings count
            holdings_count = db.query(Holding).filter(
                Holding.user_id == user.id
            ).count()
            
            # Get latest portfolio
            latest_portfolio = db.query(Portfolio).filter(
                Portfolio.user_id == user.id
            ).order_by(Portfolio.snapshot_date.desc()).first()
            
            user_data = {
                "id": user.id,
                "email": user.email,
                "full_name": user.full_name,
                "pan": user.pan,
                "phone": user.phone,
                "is_active": user.is_active,
                "is_verified": user.is_verified,
                "oauth_provider": user.oauth_provider,
                "oauth_id": user.oauth_id,
                "last_login_at": user.last_login_at.isoformat() if user.last_login_at else None,
                "created_at": user.created_at.isoformat() if user.created_at else None,
                "portfolio_count": portfolio_count,
                "holdings_count": holdings_count,
                "latest_portfolio": {
                    "id": latest_portfolio.id,
                    "name": latest_portfolio.name,
                    "source": latest_portfolio.source,
                    "total_invested": latest_portfolio.total_invested,
                    "total_current": latest_portfolio.total_current,
                    "total_gain": latest_portfolio.total_gain,
                    "xirr": latest_portfolio.xirr,
                    "snapshot_date": latest_portfolio.snapshot_date.isoformat()
                } if latest_portfolio else None
            }
            
            user_data_list.append(user_data)
            
            # Print user details
            print(f"User ID: {user.id}")
            print(f"  Email: {user.email}")
            print(f"  Name: {user.full_name or 'N/A'}")
            print(f"  PAN: {user.pan or 'N/A'}")
            print(f"  Phone: {user.phone or 'N/A'}")
            print(f"  Active: {user.is_active}")
            print(f"  Verified: {user.is_verified}")
            print(f"  OAuth Provider: {user.oauth_provider or 'Email/Password'}")
            print(f"  Last Login: {user.last_login_at or 'Never'}")
            print(f"  Created: {user.created_at}")
            print(f"  Portfolios: {portfolio_count}")
            print(f"  Holdings: {holdings_count}")
            
            if latest_portfolio:
                print(f"  Latest Portfolio:")
                print(f"    - Name: {latest_portfolio.name}")
                print(f"    - Source: {latest_portfolio.source}")
                print(f"    - Total Invested: ₹{latest_portfolio.total_invested:,.2f}")
                print(f"    - Total Current: ₹{latest_portfolio.total_current:,.2f}")
                print(f"    - Total Gain: ₹{latest_portfolio.total_gain:,.2f}")
                print(f"    - XIRR: {latest_portfolio.xirr:.2f}%" if latest_portfolio.xirr else "    - XIRR: N/A")
                print(f"    - Snapshot Date: {latest_portfolio.snapshot_date}")
            
            print(f"\n{'-'*80}\n")
        
        # Save to JSON file
        output_file = backend_dir / "all_users_data.json"
        with open(output_file, 'w') as f:
            json.dump(user_data_list, f, indent=2, default=str)
        
        print(f"\n✅ User data exported to: {output_file}")
        print(f"\nSummary:")
        print(f"  Total Users: {len(users)}")
        print(f"  Active Users: {sum(1 for u in users if u.is_active)}")
        print(f"  Verified Users: {sum(1 for u in users if u.is_verified)}")
        print(f"  Users with OAuth: {sum(1 for u in users if u.oauth_provider)}")
        
        return user_data_list
        
    except Exception as e:
        print(f"❌ Error retrieving users: {e}")
        import traceback
        traceback.print_exc()
        return []
    finally:
        db.close()


if __name__ == "__main__":
    get_all_users()
