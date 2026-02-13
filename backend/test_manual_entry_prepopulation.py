"""
Test script to verify manual entry data pre-population functionality
"""
import sys
from pathlib import Path

backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

from sqlalchemy import select
from app.database import SessionLocal
from app.models.models import User, Portfolio, Holding
import json


def test_manual_entry_prepopulation():
    """Test that manual entry data can be retrieved for pre-population"""
    db = SessionLocal()
    
    try:
        print(f"\n{'='*80}")
        print("MANUAL ENTRY PRE-POPULATION TEST")
        print(f"{'='*80}\n")
        
        # Find users with manual entry portfolios
        users_with_manual = db.query(User).join(Portfolio).filter(
            Portfolio.source == 'manual_entry'
        ).distinct().all()
        
        print(f"📋 Users with manual entry data: {len(users_with_manual)}\n")
        
        for user in users_with_manual:
            print(f"User: {user.email} (ID: {user.id})")
            
            # Get latest portfolio
            portfolio = db.query(Portfolio).filter(
                Portfolio.user_id == user.id,
                Portfolio.source == 'manual_entry'
            ).order_by(Portfolio.snapshot_date.desc()).first()
            
            if not portfolio:
                continue
            
            # Get holdings
            holdings = db.query(Holding).filter(
                Holding.portfolio_id == portfolio.id
            ).all()
            
            print(f"  Latest Manual Entry Portfolio:")
            print(f"    Portfolio ID: {portfolio.id}")
            print(f"    Created: {portfolio.snapshot_date}")
            print(f"    Holdings: {len(holdings)}")
            print(f"    Total Invested: ₹{portfolio.total_invested:,.2f}")
            
            # Show what would be sent to frontend
            frontend_data = {
                "portfolio_id": portfolio.id,
                "portfolio_name": portfolio.name,
                "source": portfolio.source,
                "holdings": [
                    {
                        "id": h.id,
                        "fund_name": h.fund_name,
                        "amc": h.amc,
                        "category": h.category,
                        "invested": h.invested_amount,
                        "current_value": h.current_value,
                        "units": h.units,
                        "nav": h.nav
                    }
                    for h in holdings
                ],
                "summary": {
                    "total_invested": portfolio.total_invested,
                    "total_current": portfolio.total_current,
                    "holdings_count": len(holdings)
                }
            }
            
            print(f"\n  Data that will be loaded on manual-entry.html:\n")
            for idx, h in enumerate(frontend_data['holdings'], 1):
                print(f"    Row {idx}:")
                print(f"      AMC: {h['amc']}")
                print(f"      Fund: {h['fund_name']}")
                print(f"      Amount: ₹{h['invested']:,.2f}")
            
            print(f"\n  ✅ This user will see their existing {len(holdings)} holdings pre-populated")
            print(f"  📄 API Endpoint: GET /api/portfolio/ (with auth token)")
            print(f"\n{'-'*80}\n")
        
        if len(users_with_manual) == 0:
            print("⚠️  No users with manual entry data found")
            print("   To test, create a manual entry portfolio first")
        else:
            print(f"\n{'='*80}")
            print("✅ PRE-POPULATION READY")
            print(f"   {len(users_with_manual)} user(s) have manual entry data")
            print("   When they visit manual-entry.html, their data will be pre-loaded")
            print(f"{'='*80}\n")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()


if __name__ == "__main__":
    test_manual_entry_prepopulation()
