"""
Portfolio Routes - Get and manage portfolio data
"""
from fastapi import APIRouter, HTTPException, Depends
from typing import Optional
from datetime import datetime
import logging

# Setup logger
logger = logging.getLogger(__name__)

router = APIRouter()

# In-memory storage (replace with database in production)
portfolio_store = {}


@router.get("/")
async def get_portfolio(user_id: str = "default"):
    """Get user's portfolio"""
    logger.info(f"Fetching portfolio for user: {user_id}")
    
    if user_id not in portfolio_store:
        logger.warning(f"No portfolio found for user: {user_id}")
        return {"holdings": [], "summary": {}, "message": "No portfolio data. Please upload Excel or CAS."}
    
    portfolio = portfolio_store[user_id]
    logger.info(f"Portfolio retrieved for user {user_id}: {len(portfolio.get('holdings', []))} holdings")
    return portfolio


@router.post("/save")
async def save_portfolio(data: dict, user_id: str = "default"):
    """Save portfolio data"""
    logger.info(f"Saving portfolio for user: {user_id}")
    
    portfolio_store[user_id] = {
        **data,
        "saved_at": datetime.now().isoformat()
    }
    
    holdings_count = len(data.get('holdings', []))
    total_value = data.get('summary', {}).get('total_current', 0)
    logger.info(f"Portfolio saved for user {user_id}: {holdings_count} holdings, total value: ₹{total_value:,.0f}")
    
    return {"success": True, "message": "Portfolio saved successfully"}


@router.delete("/")
async def delete_portfolio(user_id: str = "default"):
    """Delete user's portfolio"""
    if user_id in portfolio_store:
        del portfolio_store[user_id]
    return {"success": True, "message": "Portfolio deleted"}


@router.get("/holdings")
async def get_holdings(user_id: str = "default"):
    """Get just the holdings list"""
    if user_id not in portfolio_store:
        return []
    return portfolio_store[user_id].get("holdings", [])


@router.get("/summary")
async def get_summary(user_id: str = "default"):
    """Get portfolio summary"""
    if user_id not in portfolio_store:
        return {}
    return portfolio_store[user_id].get("summary", {})
