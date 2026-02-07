"""
Script to load fund holdings from JSON into database
Run this once to migrate from JSON to DB
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import json
from datetime import datetime
from sqlalchemy.orm import Session
from app.database import SessionLocal, engine
from app.models.fund_holdings import Base, FundMaster, FundHolding, FundSectorAllocation, DataUpdateLog

# Create tables
Base.metadata.create_all(bind=engine)

def load_from_json():
    """Load fund holdings from JSON file into database"""
    
    json_path = os.path.join(os.path.dirname(__file__), "..", "data", "fund_holdings.json")
    
    if not os.path.exists(json_path):
        print(f"[ERROR] JSON file not found: {json_path}")
        return
    
    # Read JSON
    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    db = SessionLocal()
    update_log = None
    
    try:
        # Start update log
        update_log = DataUpdateLog(
            update_type="initial_load",
            source="json_file",
            status="in_progress",
            started_at=datetime.utcnow(),
            update_metadata={"version": data.get("version"), "source_file": json_path}
        )
        db.add(update_log)
        db.commit()
        
        funds = data.get("funds", {})
        funds_count = 0
        
        for fund_key, fund_data in funds.items():
            print(f"[INFO] Loading: {fund_data['name']}")
            
            # Check if fund exists
            existing_fund = db.query(FundMaster).filter(FundMaster.fund_key == fund_key).first()
            
            if existing_fund:
                # Update existing
                fund = existing_fund
                fund.fund_name = fund_data["name"]
                fund.amc = fund_data["amc"]
                fund.category = fund_data["category"]
                fund.updated_at = datetime.utcnow()  # type: ignore
                
                # Delete old holdings and sectors
                db.query(FundHolding).filter(FundHolding.fund_id == fund.id).delete()
                db.query(FundSectorAllocation).filter(FundSectorAllocation.fund_id == fund.id).delete()
            else:
                # Create new fund
                fund = FundMaster(
                    fund_key=fund_key,
                    fund_name=fund_data["name"],
                    amc=fund_data["amc"],
                    category=fund_data["category"]
                )
                db.add(fund)
                db.flush()  # Get the ID
            
            # Add holdings
            for holding in fund_data.get("holdings", []):
                fund_holding = FundHolding(
                    fund_id=fund.id,
                    stock_name=holding["stock"],
                    weight=holding["weight"],
                    sector=holding["sector"],
                    as_of_date=datetime.utcnow()
                )
                db.add(fund_holding)
            
            # Add sector allocations
            for sector, weight in fund_data.get("sector_allocation", {}).items():
                sector_alloc = FundSectorAllocation(
                    fund_id=fund.id,
                    sector=sector,
                    weight=weight,
                    as_of_date=datetime.utcnow()
                )
                db.add(sector_alloc)
            
            funds_count += 1
        
        # Complete update log
        if update_log:
            update_log.funds_updated = funds_count  # type: ignore
            update_log.status = "success"  # type: ignore
            update_log.completed_at = datetime.utcnow()  # type: ignore
        
        db.commit()
        
        print(f"\n[SUCCESS] Successfully loaded {funds_count} funds into database")
        print(f"[INFO] Total holdings: {db.query(FundHolding).count()}")
        print(f"[INFO] Total sectors: {db.query(FundSectorAllocation).count()}")
        
    except Exception as e:
        db.rollback()
        print(f"[ERROR] Error loading data: {e}")
        
        # Log failure
        if update_log:
            update_log.status = "failed"  # type: ignore
            update_log.error_message = str(e)  # type: ignore
            update_log.completed_at = datetime.utcnow()  # type: ignore
            db.commit()
        
    finally:
        db.close()

if __name__ == "__main__":
    print("Start: Starting fund holdings database migration...")
    load_from_json()
    print("[SUCCESS] Migration complete!")
