"""
Check Funds Database Statistics
Shows what's available for manual portfolio entry
"""
from sqlalchemy import create_engine, func
from sqlalchemy.orm import sessionmaker
from app.config import settings
from app.models.models import FundMaster

def check_funds_database():
    """Check fund database statistics"""
    engine = create_engine(settings.DATABASE_URL)
    SessionLocal = sessionmaker(bind=engine)
    db = SessionLocal()
    
    print("\n" + "=" * 70)
    print("MUTUAL FUNDS DATABASE - MANUAL ENTRY AUTOCOMPLETE")
    print("=" * 70)
    
    # Total funds
    total_funds = db.query(FundMaster).count()
    active_funds = db.query(FundMaster).filter(FundMaster.is_active == True).count()
    
    print(f"\n[INFO] TOTAL FUNDS: {total_funds:,}")
    print(f"[SUCCESS] Active Funds: {active_funds:,}")
    print(f"[ERROR] Inactive Funds: {(total_funds - active_funds):,}")
    
    # By Category
    print("\n[INFO] FUNDS BY CATEGORY:")
    categories = db.query(
        FundMaster.category,
        func.count(FundMaster.id).label('count')
    ).filter(
        FundMaster.is_active == True
    ).group_by(
        FundMaster.category
    ).order_by(
        func.count(FundMaster.id).desc()
    ).all()
    
    for cat, count in categories[:15]:  # Top 15 categories
        print(f"  {cat:.<40} {count:>6,} funds")
    
    # By Plan Type
    print("\n[INFO] FUNDS BY PLAN TYPE:")
    plans = db.query(
        FundMaster.plan_type,
        func.count(FundMaster.id).label('count')
    ).filter(
        FundMaster.is_active == True
    ).group_by(
        FundMaster.plan_type
    ).all()
    
    for plan, count in plans:
        print(f"  {plan:.<40} {count:>6,} funds")
    
    # Top AMCs
    print("\n[INFO] TOP 10 AMCs (Asset Management Companies):")
    amcs = db.query(
        FundMaster.amc,
        func.count(FundMaster.id).label('count')
    ).filter(
        FundMaster.is_active == True
    ).group_by(
        FundMaster.amc
    ).order_by(
        func.count(FundMaster.id).desc()
    ).limit(10).all()
    
    for amc, count in amcs:
        print(f"  {amc:.<50} {count:>5,} funds")
    
    # Sample funds
    print("\n[INFO] SAMPLE FUNDS (First 10 for testing autocomplete):")
    samples = db.query(FundMaster).filter(
        FundMaster.is_active == True,
        FundMaster.scheme_name.ilike('%HDFC%')
    ).limit(10).all()
    
    for fund in samples:
        print(f"  * {fund.scheme_name[:70]}")
        print(f"    AMC: {fund.amc} | Category: {fund.category} | NAV: Rs.{fund.current_nav or 0:.2f}")
    
    # Funds with NAV data
    funds_with_nav = db.query(FundMaster).filter(
        FundMaster.is_active == True,
        FundMaster.current_nav.isnot(None)
    ).count()
    
    print(f"\n[INFO] Funds with NAV Data: {funds_with_nav:,} ({funds_with_nav/active_funds*100:.1f}%)")
    
    print("\n" + "=" * 70)
    print("[SUCCESS] DATABASE READY FOR MANUAL PORTFOLIO ENTRY!")
    print("=" * 70)
    print("\nUsers can search by:")
    print("  * Fund Name (e.g., 'HDFC Top 100')")
    print("  * AMC Name (e.g., 'ICICI', 'SBI')")
    print("  * Category (e.g., 'Large Cap', 'Debt')")
    print("\nAutocomplete API: /api/funds/list?search=XXX&dropdown=true&limit=10")
    print()
    
    db.close()

if __name__ == "__main__":
    check_funds_database()
