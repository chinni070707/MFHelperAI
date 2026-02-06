"""
Seed Demo Portfolio
Creates a realistic demo portfolio with popular funds
"""
from sqlalchemy.orm import sessionmaker
from app.database import engine
from app.models.demo_portfolio import DemoPortfolio
from app.models.models import FundMaster
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def seed_demo_portfolio():
    """Create demo portfolio with popular funds"""
    SessionLocal = sessionmaker(bind=engine)
    db = SessionLocal()
    
    try:
        # Clear existing demo data
        db.query(DemoPortfolio).delete()
        
        # Find some popular direct growth funds
        demo_holdings = [
            # HDFC Top 100 Fund - Large Cap
            {"scheme_name": "HDFC", "category": "Equity - Large Cap", "units": 150, "avg_cost": 650},
            # ICICI Prudential Bluechip - Large Cap
            {"scheme_name": "ICICI.*Bluechip", "category": "Equity", "units": 200, "avg_cost": 80},
            # Axis Midcap Fund
            {"scheme_name": "Axis.*Mid Cap", "category": "Equity", "units": 100, "avg_cost": 90},
            # SBI Small Cap Fund
            {"scheme_name": "SBI.*Small Cap", "category": "Equity", "units": 80, "avg_cost": 110},
            # Parag Parikh Flexi Cap
            {"scheme_name": "Parag Parikh", "category": "Equity", "units": 120, "avg_cost": 45},
            # HDFC Hybrid Fund
            {"scheme_name": "HDFC.*Hybrid", "category": "Hybrid", "units": 300, "avg_cost": 70},
            # ICICI Prudential Liquid Fund
            {"scheme_name": "ICICI.*Liquid", "category": "Liquid", "units": 500, "avg_cost": 320},
            # UTI Nifty Index Fund
            {"scheme_name": "UTI.*Nifty.*Index", "category": "Index", "units": 250, "avg_cost": 85},
        ]
        
        added_count = 0
        for holding in demo_holdings:
            # Find matching fund (Direct plan preferred)
            fund = db.query(FundMaster).filter(
                FundMaster.scheme_name.ilike(f"%{holding['scheme_name']}%"),
                FundMaster.scheme_name.ilike("%Direct%"),
                FundMaster.scheme_name.ilike("%Growth%"),
                FundMaster.is_active == True
            ).first()
            
            if fund:
                invested_amount = holding['units'] * holding['avg_cost']
                current_value = holding['units'] * (fund.current_nav or holding['avg_cost'] * 1.15)
                gain_loss = current_value - invested_amount
                gain_loss_percent = (gain_loss / invested_amount * 100) if invested_amount > 0 else 0
                
                demo = DemoPortfolio(
                    scheme_name=fund.scheme_name,
                    scheme_code=fund.scheme_code,
                    units=holding['units'],
                    avg_cost=holding['avg_cost'],
                    current_nav=fund.current_nav or holding['avg_cost'] * 1.15,
                    invested_amount=invested_amount,
                    current_value=current_value,
                    gain_loss=gain_loss,
                    gain_loss_percent=gain_loss_percent,
                    amc=fund.amc,
                    category=fund.category,
                    is_active=True
                )
                db.add(demo)
                added_count += 1
                logger.info(f"Added: {fund.scheme_name[:60]}...")
        
        db.commit()
        logger.info(f"\n✓ Successfully created demo portfolio with {added_count} holdings")
        
        # Calculate totals
        holdings = db.query(DemoPortfolio).filter(DemoPortfolio.is_active == True).all()
        total_invested = sum(h.units * h.avg_cost for h in holdings)
        total_current = sum(h.units * h.current_nav for h in holdings)
        total_gain = total_current - total_invested
        gain_pct = (total_gain / total_invested * 100) if total_invested > 0 else 0
        
        print("\n" + "=" * 60)
        print("DEMO PORTFOLIO SUMMARY")
        print("=" * 60)
        print(f"Total Holdings: {len(holdings)}")
        print(f"Total Invested: ₹{total_invested:,.2f}")
        print(f"Current Value: ₹{total_current:,.2f}")
        print(f"Total Gain: ₹{total_gain:,.2f} ({gain_pct:.2f}%)")
        print("=" * 60)
        
        db.close()
        return added_count
        
    except Exception as e:
        logger.error(f"Error seeding demo portfolio: {e}")
        db.rollback()
        db.close()
        return 0

if __name__ == "__main__":
    print("\n📊 Creating Demo Portfolio...\n")
    count = seed_demo_portfolio()
    
    if count > 0:
        print("\n✅ Demo portfolio created successfully!")
        print("\nNext steps:")
        print("  1. Start server: python -m uvicorn app.main:app --reload")
        print("  2. Test demo: http://localhost:8000/api/demo/portfolio")
    else:
        print("\n❌ Failed to create demo portfolio")
