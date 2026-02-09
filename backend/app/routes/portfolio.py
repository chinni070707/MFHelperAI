"""
Portfolio Routes - Get and manage portfolio data with database persistence
"""
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from typing import Optional
from datetime import datetime
import logging

from app.database import get_db
from app.models.models import User, Portfolio, Holding
from app.utils.auth import get_current_user

# Setup logger
logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/")
async def get_portfolio(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get user's latest portfolio"""
    logger.info(f"Fetching portfolio for user: {current_user.email}")
    
    # Get latest portfolio
    portfolio = db.query(Portfolio).filter(
        Portfolio.user_id == current_user.id
    ).order_by(Portfolio.snapshot_date.desc()).first()
    
    if not portfolio:
        logger.warning(f"No portfolio found for user: {current_user.email}")
        return {
            "holdings": [],
            "summary": {},
            "message": "No portfolio data. Please upload Excel or CAS."
        }
    
    # Get holdings for this portfolio
    holdings = db.query(Holding).filter(
        Holding.portfolio_id == portfolio.id
    ).all()
    
    # Format response
    summary = {
        "total_invested": portfolio.total_invested,
        "total_current": portfolio.total_current,
        "total_gain": portfolio.total_gain,
        "return_pct": (portfolio.total_gain / portfolio.total_invested * 100) if portfolio.total_invested > 0 else 0,
        "xirr": portfolio.xirr,
        "holdings_count": len(holdings),
        "last_updated": portfolio.snapshot_date.isoformat()
    }
    
    holdings_list = [
        {
            "id": h.id,
            "fund_name": h.fund_name,
            "amc": h.amc,
            "category": h.category,
            "invested": h.invested_amount,
            "current_value": h.current_value,
            "units": h.units,
            "nav": h.nav,
            "gain": h.gain_loss,
            "return_pct": h.return_pct,
            "return_1y": h.one_year_return,
            "return_3y": h.three_year_return,
            "alpha": h.alpha
        }
        for h in holdings
    ]
    
    logger.info(f"Portfolio retrieved for user {current_user.email}: {len(holdings)} holdings")
    
    return {
        "portfolio_id": portfolio.id,
        "portfolio_name": portfolio.name,
        "source": portfolio.source,
        "holdings": holdings_list,
        "summary": summary
    }


@router.post("/save")
async def save_portfolio(
    data: dict,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Save portfolio data - creates a new snapshot preserving history"""
    logger.info(f"Saving portfolio for user: {current_user.email}")
    
    # Helper function to safely convert to float
    def safe_float(value, default=None):
        """Convert value to float, handling strings with % and special chars"""
        if value is None:
            return default
        if isinstance(value, (int, float)):
            return float(value)
        if isinstance(value, str):
            value = value.strip()
            if value in ['-', '', 'N/A', 'NA', 'null', 'None']:
                return default
            # Remove % sign if present
            value = value.rstrip('%')
            try:
                return float(value)
            except (ValueError, TypeError):
                return default
        return default
    
    summary = data.get('summary', {})
    holdings_data = data.get('holdings', [])
    
    # Create new portfolio snapshot
    new_portfolio = Portfolio(
        user_id=current_user.id,
        name=data.get('name', 'My Portfolio'),
        source=data.get('source', 'upload'),
        total_invested=summary.get('total_invested', 0),
        total_current=summary.get('total_current', 0),
        total_gain=summary.get('total_gain', 0),
        xirr=summary.get('xirr'),
        snapshot_date=datetime.now()
    )
    
    db.add(new_portfolio)
    db.flush()  # Get portfolio ID without committing
    
    # Add holdings
    for holding_data in holdings_data:
        holding = Holding(
            user_id=current_user.id,
            portfolio_id=new_portfolio.id,
            fund_name=holding_data.get('fund_name'),
            amc=holding_data.get('amc'),
            category=holding_data.get('category'),
            sub_category=holding_data.get('sub_category'),
            units=safe_float(holding_data.get('units'), 0),
            nav=safe_float(holding_data.get('nav')),
            invested_amount=safe_float(holding_data.get('invested'), 0),
            current_value=safe_float(holding_data.get('current_value'), 0),
            gain_loss=safe_float(holding_data.get('gain'), 0),
            return_pct=safe_float(holding_data.get('return_pct'), 0),
            one_year_return=safe_float(holding_data.get('return_1y')),
            three_year_return=safe_float(holding_data.get('return_3y')),
            alpha=safe_float(holding_data.get('alpha'))
        )
        db.add(holding)
    
    db.commit()
    
    logger.info(f"Portfolio saved for user {current_user.email}: Portfolio ID {new_portfolio.id}, {len(holdings_data)} holdings")
    
    return {
        "success": True,
        "message": "Portfolio saved successfully",
        "portfolio_id": new_portfolio.id,
        "holdings_count": len(holdings_data)
    }


@router.post("/manual")
async def save_manual_portfolio(
    data: dict,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Save manually entered portfolio data"""
    logger.info(f"Saving manual portfolio for user: {current_user.email}")
    
    holdings_data = data.get('holdings', [])
    
    if not holdings_data:
        raise HTTPException(status_code=400, detail="No holdings provided")
    
    # Calculate totals
    total_invested = sum(h.get('invested_amount', 0) for h in holdings_data)
    
    # Create new portfolio snapshot
    new_portfolio = Portfolio(
        user_id=current_user.id,
        name="Manual Entry",
        source="manual_entry",
        total_invested=total_invested,
        total_current=total_invested,  # For manual entry, current = invested initially
        total_gain=0,
        snapshot_date=datetime.now()
    )
    
    db.add(new_portfolio)
    db.flush()  # Get portfolio ID
    
    # Add holdings
    for holding_data in holdings_data:
        holding = Holding(
            user_id=current_user.id,
            portfolio_id=new_portfolio.id,
            fund_name=holding_data.get('scheme_name', ''),
            amc=holding_data.get('amc', ''),
            invested_amount=holding_data.get('invested_amount', 0),
            current_value=holding_data.get('invested_amount', 0),  # Initially same as invested
            gain_loss=0,
            return_pct=0
        )
        db.add(holding)
    
    db.commit()
    
    logger.info(f"✅ Manual portfolio saved for user {current_user.email}: Portfolio ID {new_portfolio.id}, {len(holdings_data)} holdings")
    
    return {
        "success": True,
        "message": "Portfolio saved successfully",
        "portfolio_id": new_portfolio.id,
        "holdings_count": len(holdings_data)
    }


@router.delete("/")
async def delete_portfolio(
    portfolio_id: Optional[int] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete a specific portfolio or all portfolios"""
    if portfolio_id:
        # Delete specific portfolio
        portfolio = db.query(Portfolio).filter(
            Portfolio.id == portfolio_id,
            Portfolio.user_id == current_user.id
        ).first()
        
        if not portfolio:
            raise HTTPException(status_code=404, detail="Portfolio not found")
        
        db.delete(portfolio)
        logger.info(f"Deleted portfolio {portfolio_id} for user {current_user.email}")
    else:
        # Delete all portfolios for user
        db.query(Portfolio).filter(Portfolio.user_id == current_user.id).delete()
        logger.info(f"Deleted all portfolios for user {current_user.email}")
    
    db.commit()
    return {"success": True, "message": "Portfolio deleted"}


@router.get("/holdings")
async def get_holdings(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get just the holdings list from latest portfolio"""
    portfolio = db.query(Portfolio).filter(
        Portfolio.user_id == current_user.id
    ).order_by(Portfolio.snapshot_date.desc()).first()
    
    if not portfolio:
        return []
    
    holdings = db.query(Holding).filter(Holding.portfolio_id == portfolio.id).all()
    
    return [
        {
            "fund_name": h.fund_name,
            "amc": h.amc,
            "category": h.category,
            "invested": h.invested_amount,
            "current_value": h.current_value,
            "gain": h.gain_loss,
            "return_pct": h.return_pct
        }
        for h in holdings
    ]


@router.get("/summary")
async def get_summary(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get portfolio summary"""
    portfolio = db.query(Portfolio).filter(
        Portfolio.user_id == current_user.id
    ).order_by(Portfolio.snapshot_date.desc()).first()
    
    if not portfolio:
        return {}
    
    return {
        "total_invested": portfolio.total_invested,
        "total_current": portfolio.total_current,
        "total_gain": portfolio.total_gain,
        "return_pct": (portfolio.total_gain / portfolio.total_invested * 100) if portfolio.total_invested > 0 else 0,
        "xirr": portfolio.xirr
    }


@router.get("/history")
async def get_portfolio_history(
    limit: int = 10,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get historical portfolio snapshots for trend analysis"""
    portfolios = db.query(Portfolio).filter(
        Portfolio.user_id == current_user.id
    ).order_by(Portfolio.snapshot_date.desc()).limit(limit).all()
    
    return [
        {
            "id": p.id,
            "name": p.name,
            "snapshot_date": p.snapshot_date.isoformat(),
            "total_invested": p.total_invested,
            "total_current": p.total_current,
            "total_gain": p.total_gain,
            "return_pct": (p.total_gain / p.total_invested * 100) if p.total_invested > 0 else 0
        }
        for p in portfolios
    ]


@router.get("/latest-id")
async def get_latest_portfolio_id(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get user's most recent portfolio ID"""
    portfolio = db.query(Portfolio).filter(
        Portfolio.user_id == current_user.id
    ).order_by(Portfolio.created_at.desc()).first()
    
    if not portfolio:
        raise HTTPException(status_code=404, detail="No portfolios found")
    
    return {
        "id": portfolio.id,
        "name": portfolio.name,
        "source": portfolio.source,
        "total_invested": portfolio.total_invested,
        "total_current": portfolio.total_current,
        "created_at": str(portfolio.created_at)
    }
