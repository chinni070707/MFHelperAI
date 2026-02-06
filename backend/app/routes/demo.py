"""
Demo Portfolio Routes
Provides demo portfolio data for unauthenticated users
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Dict, Any
import logging

from app.database import get_db
from app.models.demo_portfolio import DemoPortfolio

router = APIRouter(prefix="/demo", tags=["Demo Portfolio"])
logger = logging.getLogger(__name__)


@router.get("/portfolio")
async def get_demo_portfolio(db: Session = Depends(get_db)):
    """
    Get demo portfolio data for demo mode
    
    Returns:
        Portfolio data with holdings and metadata
    """
    try:
        # Get all active demo holdings
        holdings = db.query(DemoPortfolio).filter(DemoPortfolio.is_active == True).all()
        
        if not holdings:
            raise HTTPException(
                status_code=404,
                detail="Demo portfolio not configured. Please contact administrator."
            )
        
        # Calculate totals
        total_invested = sum(h.invested_amount for h in holdings)
        total_current = sum(h.current_value for h in holdings)
        total_gain = total_current - total_invested
        total_gain_percent = (total_gain / total_invested * 100) if total_invested > 0 else 0
        
        # Build response
        response = {
            "success": True,
            "mode": "demo",
            "holdings": [h.to_dict() for h in holdings],
            "metadata": {
                "totalInvested": round(total_invested, 2),
                "currentValue": round(total_current, 2),
                "totalGain": round(total_gain, 2),
                "totalGainPercent": round(total_gain_percent, 2),
                "fundCount": len(holdings),
                "isDemo": True
            }
        }
        
        logger.info(f"Demo portfolio loaded: {len(holdings)} holdings")
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error loading demo portfolio: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to load demo portfolio: {str(e)}"
        )


@router.post("/portfolio/seed")
async def seed_demo_portfolio(
    holdings_data: List[Dict[str, Any]],
    db: Session = Depends(get_db)
):
    """
    Admin endpoint to seed demo portfolio data
    
    Request body: List of holdings with scheme details
    """
    try:
        # Clear existing demo data
        db.query(DemoPortfolio).delete()
        
        # Insert new demo holdings
        for holding_data in holdings_data:
            demo_holding = DemoPortfolio(
                scheme_name=holding_data["scheme_name"],
                scheme_code=holding_data.get("scheme_code"),
                units=holding_data["units"],
                avg_cost=holding_data["avg_cost"],
                current_nav=holding_data["current_nav"],
                invested_amount=holding_data["units"] * holding_data["avg_cost"],
                current_value=holding_data["units"] * holding_data["current_nav"],
                gain_loss=(holding_data["units"] * holding_data["current_nav"]) - (holding_data["units"] * holding_data["avg_cost"]),
                gain_loss_percent=((holding_data["current_nav"] - holding_data["avg_cost"]) / holding_data["avg_cost"] * 100) if holding_data["avg_cost"] > 0 else 0,
                amc=holding_data.get("amc"),
                category=holding_data.get("category"),
                sub_category=holding_data.get("sub_category"),
                is_active=True
            )
            db.add(demo_holding)
        
        db.commit()
        
        count = len(holdings_data)
        logger.info(f"Demo portfolio seeded with {count} holdings")
        
        return {
            "success": True,
            "message": f"Demo portfolio seeded with {count} holdings"
        }
        
    except Exception as e:
        db.rollback()
        logger.error(f"Error seeding demo portfolio: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to seed demo portfolio: {str(e)}"
        )
