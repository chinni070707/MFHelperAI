"""
Data update API endpoints
Admin endpoints for triggering data updates
"""
from fastapi import APIRouter, Depends, BackgroundTasks, HTTPException, Header
from sqlalchemy.orm import Session
from typing import Dict
import logging
import os

from app.database import get_db
from app.services.data_ingestion import FundDataIngestionService
# from app.models.fund_holdings import DataUpdateLog  # Removed

router = APIRouter(prefix="/api/data", tags=["data-updates"])
logger = logging.getLogger(__name__)

ADMIN_API_KEY = os.getenv("ADMIN_API_KEY", "admin-secret-key-change-in-production")


def verify_data_admin(x_admin_key: str = Header(None, alias="X-Admin-Key")):
    """Verify admin API key via header (not query param)"""
    if not x_admin_key or x_admin_key != ADMIN_API_KEY:
        raise HTTPException(status_code=401, detail="Admin authentication required")
    return True


@router.post("/update/market-caps")
async def update_market_caps(
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    _admin: bool = Depends(verify_data_admin)
) -> Dict:
    """
    Trigger market cap data update
    Runs in background
    """
    try:
        service = FundDataIngestionService(db)
        
        # Run in background
        background_tasks.add_task(service.update_stock_market_caps)
        
        return {
            "status": "started",
            "message": "Market cap update started in background"
        }
    except Exception as e:
        logger.error(f"Error starting market cap update: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/update/fund-holdings/{fund_id}")
async def update_fund_holdings(
    fund_id: int,
    fund_name: str,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    _admin: bool = Depends(verify_data_admin)
) -> Dict:
    """
    Trigger holdings update for a specific fund
    """
    try:
        service = FundDataIngestionService(db)
        
        # Run in background
        background_tasks.add_task(
            service.update_fund_holdings,
            fund_id,
            fund_name
        )
        
        return {
            "status": "started",
            "message": f"Holdings update started for fund: {fund_name}"
        }
    except Exception as e:
        logger.error(f"Error starting fund holdings update: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/update/weekly")
async def trigger_weekly_update(
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    _admin: bool = Depends(verify_data_admin)
) -> Dict:
    """
    Trigger full weekly data update
    Updates all market caps and fund holdings
    """
    try:
        service = FundDataIngestionService(db)
        
        # Run in background
        background_tasks.add_task(service.run_weekly_update)
        
        return {
            "status": "started",
            "message": "Weekly data update started in background"
        }
    except Exception as e:
        logger.error(f"Error starting weekly update: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/update/logs")
async def get_update_logs(
    limit: int = 10,
    db: Session = Depends(get_db),
    _admin: bool = Depends(verify_data_admin)
) -> Dict:
    """Get recent update logs"""
    try:
        # DataUpdateLog model not implemented yet
        logs = []
        # logs = db.query(DataUpdateLog).order_by(
        #     DataUpdateLog.started_at.desc()
        # ).limit(limit).all()
        
        return {
            "logs": [
                {
                    "id": log.id,
                    "type": log.update_type,
                    "source": log.source,
                    "status": log.status,
                    "funds_updated": log.funds_updated,
                    "started_at": log.started_at.isoformat(),
                    "completed_at": log.completed_at.isoformat() if log.completed_at else None,
                    "metadata": log.update_metadata
                }
                for log in logs
            ]
        }
    except Exception as e:
        logger.error(f"Error fetching update logs: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/fund/{fund_id}/classification")
async def get_fund_classification(
    fund_id: int,
    db: Session = Depends(get_db)
) -> Dict:
    """
    Get latest classification for a fund
    Returns Large/Mid/Small cap breakdown
    """
    from app.models.market_data import FundClassification
    from sqlalchemy import desc
    
    try:
        classification = db.query(FundClassification).filter(
            FundClassification.fund_id == fund_id
        ).order_by(desc(FundClassification.as_of_date)).first()
        
        if not classification:
            raise HTTPException(
                status_code=404,
                detail="No classification data found for this fund"
            )
        
        return {
            "fund_id": fund_id,
            "as_of_date": classification.as_of_date.isoformat(),
            "allocation": {
                "large_cap": classification.large_cap_percentage,
                "mid_cap": classification.mid_cap_percentage,
                "small_cap": classification.small_cap_percentage
            },
            "top_sectors": [
                {
                    "sector": classification.top_sector_1,
                    "weight": classification.top_sector_1_weight
                },
                {
                    "sector": classification.top_sector_2,
                    "weight": classification.top_sector_2_weight
                },
                {
                    "sector": classification.top_sector_3,
                    "weight": classification.top_sector_3_weight
                }
            ],
            "number_of_stocks": classification.number_of_stocks,
            "calculated_at": classification.calculated_at.isoformat()
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching fund classification: {e}")
        raise HTTPException(status_code=500, detail=str(e))
