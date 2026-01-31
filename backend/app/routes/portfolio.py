"""
Portfolio Routes - Get and manage portfolio data
"""
from fastapi import APIRouter, HTTPException, Depends
from typing import Optional
from datetime import datetime

router = APIRouter()

# In-memory storage (replace with database in production)
portfolio_store = {}


@router.get("/")
async def get_portfolio(user_id: str = "default"):
    """Get user's portfolio"""
    if user_id not in portfolio_store:
        return {"holdings": [], "summary": {}, "message": "No portfolio data. Please upload Excel or CAS."}
    return portfolio_store[user_id]


@router.post("/save")
async def save_portfolio(data: dict, user_id: str = "default"):
    """Save portfolio data"""
    portfolio_store[user_id] = {
        **data,
        "saved_at": datetime.now().isoformat()
    }
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
