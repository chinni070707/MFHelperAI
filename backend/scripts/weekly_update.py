"""
Weekly automated update script for fund holdings
Can be run as a cron job or GitHub Action
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import json
from datetime import datetime
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models.fund_holdings import FundMaster, FundHolding, FundSectorAllocation, DataUpdateLog

def update_from_json():
    """
    Update database from JSON file
    Run this weekly after updating the JSON with latest data
    """
    json_path = os.path.join(os.path.dirname(__file__), "..", "data", "fund_holdings.json")
    
    if not os.path.exists(json_path):
        print(f"❌ JSON file not found: {json_path}")
        return False
    
    # Read JSON
    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    db = SessionLocal()
    update_log = None
    
    try:
        # Create update log
        update_log = DataUpdateLog(
            update_type="weekly_update",
            source="json_file",
            status="in_progress",
            started_at=datetime.utcnow(),
            update_metadata={"version": data.get("version"), "date": datetime.utcnow().isoformat()}
        )
        db.add(update_log)
        db.commit()
        
        funds = data.get("funds", {})
        funds_updated = 0
        
        for fund_key, fund_data in funds.items():
            print(f"🔄 Updating: {fund_data['name']}")
            
            # Get or create fund
            fund = db.query(FundMaster).filter(FundMaster.fund_key == fund_key).first()
            
            if not fund:
                fund = FundMaster(
                    fund_key=fund_key,
                    fund_name=fund_data["name"],
                    amc=fund_data["amc"],
                    category=fund_data["category"]
                )
                db.add(fund)
                db.flush()
                print(f"  ✅ Created new fund: {fund_data['name']}")
            else:
                fund.fund_name = fund_data["name"]
                fund.amc = fund_data["amc"]
                fund.category = fund_data["category"]
                fund.updated_at = datetime.utcnow()  # type: ignore
                print(f"  🔄 Updated existing fund: {fund_data['name']}")
            
            # Delete old holdings and sectors
            db.query(FundHolding).filter(FundHolding.fund_id == fund.id).delete()
            db.query(FundSectorAllocation).filter(FundSectorAllocation.fund_id == fund.id).delete()
            
            # Add new holdings
            for holding in fund_data.get("holdings", []):
                fund_holding = FundHolding(
                    fund_id=fund.id,
                    stock_name=holding["stock"],
                    weight=holding["weight"],
                    sector=holding["sector"],
                    as_of_date=datetime.utcnow()
                )
                db.add(fund_holding)
            
            # Add new sector allocations
            for sector, weight in fund_data.get("sector_allocation", {}).items():
                sector_alloc = FundSectorAllocation(
                    fund_id=fund.id,
                    sector=sector,
                    weight=weight,
                    as_of_date=datetime.utcnow()
                )
                db.add(sector_alloc)
            
            funds_updated += 1
        
        # Complete update log
        if update_log:
            update_log.funds_updated = funds_updated  # type: ignore
            update_log.status = "success"  # type: ignore
            update_log.completed_at = datetime.utcnow()  # type: ignore
        
        db.commit()
        
        print(f"\n✅ Successfully updated {funds_updated} funds")
        print(f"📈 Total holdings in DB: {db.query(FundHolding).count()}")
        print(f"📊 Total sectors in DB: {db.query(FundSectorAllocation).count()}")
        
        return True
        
    except Exception as e:
        db.rollback()
        print(f"❌ Error updating data: {e}")
        
        # Log failure
        if update_log:
            update_log.status = "failed"  # type: ignore
            update_log.error_message = str(e)  # type: ignore
            update_log.completed_at = datetime.utcnow()  # type: ignore
            db.commit()
        
        return False
        
    finally:
        db.close()

def get_update_history():
    """Get history of past updates"""
    db = SessionLocal()
    try:
        logs = db.query(DataUpdateLog).order_by(DataUpdateLog.started_at.desc()).limit(10).all()
        
        print("\n📜 Recent Update History:")
        print("-" * 80)
        for log in logs:
            status_emoji = "✅" if log.status == "success" else "❌"
            print(f"{status_emoji} {log.update_type} | {log.started_at.strftime('%Y-%m-%d %H:%M')} | "
                  f"Funds: {log.funds_updated} | Status: {log.status}")
        print("-" * 80)
        
    finally:
        db.close()

if __name__ == "__main__":
    print("🚀 Starting weekly fund holdings update...")
    print(f"⏰ Timestamp: {datetime.utcnow().isoformat()}\n")
    
    success = update_from_json()
    
    if success:
        print("\n✅ Weekly update completed successfully!")
        get_update_history()
    else:
        print("\n❌ Weekly update failed!")
        sys.exit(1)
