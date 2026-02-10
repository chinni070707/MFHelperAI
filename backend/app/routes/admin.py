"""
Admin API endpoints
Dashboard statistics and analytics for administrators
"""
from fastapi import APIRouter, Depends, HTTPException, status, Header
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from typing import Dict
from datetime import datetime, timedelta
import logging
import os

from app.database import get_db
from app.models.models import User, Portfolio, Holding

router = APIRouter(prefix="/api/admin", tags=["admin"])
logger = logging.getLogger(__name__)


# Load admin key from environment variable instead of hardcoding
ADMIN_API_KEY = os.getenv("ADMIN_API_KEY", "admin-secret-key-change-in-production")


def verify_admin(x_admin_key: str = Header(None, alias="X-Admin-Key"), api_key: str = None):
    """Verify admin API key via header (preferred) or query param (deprecated)"""
    key = x_admin_key or api_key  # Header takes priority, fall back to query param
    if not key or key != ADMIN_API_KEY:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid admin credentials"
        )
    return True


@router.get("/stats")
async def get_admin_stats(
    api_key: str = None,
    db: Session = Depends(get_db)
) -> Dict:
    """
    Get comprehensive admin statistics
    
    Query params:
        api_key: Admin API key for authentication
    
    Returns:
        Dictionary with user stats, portfolio stats, and AUM data
    """
    verify_admin(api_key)
    
    try:
        # User Statistics
        total_users = db.query(func.count(User.id)).scalar() or 0
        active_users = db.query(func.count(User.id)).filter(User.is_active == True).scalar() or 0
        verified_users = db.query(func.count(User.id)).filter(User.is_verified == True).scalar() or 0
        
        # Users registered in last 7 days
        week_ago = datetime.utcnow() - timedelta(days=7)
        new_users_week = db.query(func.count(User.id)).filter(
            User.created_at >= week_ago
        ).scalar() or 0
        
        # Users registered today
        today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
        new_users_today = db.query(func.count(User.id)).filter(
            User.created_at >= today_start
        ).scalar() or 0
        
        # Portfolio Statistics
        total_portfolios = db.query(func.count(Portfolio.id)).scalar() or 0
        
        # Total portfolio uploads/refreshes (each portfolio record = 1 upload)
        total_uploads = total_portfolios
        
        # Unique users with portfolios
        users_with_portfolios = db.query(func.count(func.distinct(Portfolio.user_id))).scalar() or 0
        
        # Average portfolios per user
        avg_portfolios_per_user = total_portfolios / total_users if total_users > 0 else 0
        
        # AUM Statistics (Assets Under Management)
        aum_data = db.query(
            func.sum(Portfolio.total_current).label('total_aum'),
            func.sum(Portfolio.total_invested).label('total_invested'),
            func.avg(Portfolio.total_current).label('avg_portfolio_value')
        ).first()
        
        total_aum = float(aum_data.total_aum or 0)
        total_invested = float(aum_data.total_invested or 0)
        avg_portfolio_value = float(aum_data.avg_portfolio_value or 0)
        total_returns = total_aum - total_invested
        
        # Holdings Statistics
        total_holdings = db.query(func.count(Holding.id)).scalar() or 0
        unique_funds = db.query(func.count(func.distinct(Holding.scheme_code))).scalar() or 0
        
        # Top AMCs by AUM
        top_amcs = db.query(
            Holding.amc,
            func.sum(Holding.current_value).label('total_value')
        ).group_by(Holding.amc).order_by(desc('total_value')).limit(5).all()
        
        # Top performing funds
        top_funds = db.query(
            Holding.fund_name,
            Holding.return_pct,
            func.sum(Holding.current_value).label('total_value')
        ).group_by(Holding.fund_name, Holding.return_pct).order_by(
            desc(Holding.return_pct)
        ).limit(5).all()
        
        # Recent activity (fixed N+1 query #16 — use subquery instead of per-portfolio count)
        holdings_count_subq = db.query(
            Holding.portfolio_id,
            func.count(Holding.id).label('funds_count')
        ).group_by(Holding.portfolio_id).subquery()
        
        recent_query = db.query(
            Portfolio.user_id,
            Portfolio.name,
            Portfolio.total_current,
            Portfolio.created_at,
            func.coalesce(holdings_count_subq.c.funds_count, 0).label('funds_count')
        ).outerjoin(
            holdings_count_subq,
            Portfolio.id == holdings_count_subq.c.portfolio_id
        ).order_by(desc(Portfolio.created_at)).limit(10).all()
        
        recent_activity = [
            {
                "user_id": r.user_id,
                "portfolio_name": r.name,
                "total_value": r.total_current,
                "funds_count": r.funds_count,
                "created_at": r.created_at.isoformat()
            }
            for r in recent_query
        ]
        
        # Growth metrics (compared to last week)
        last_week = datetime.utcnow() - timedelta(days=7)
        last_week_users = db.query(func.count(User.id)).filter(
            User.created_at < last_week
        ).scalar() or 0
        
        user_growth_rate = ((total_users - last_week_users) / last_week_users * 100) if last_week_users > 0 else 0
        
        return {
            "timestamp": datetime.utcnow().isoformat(),
            "users": {
                "total": total_users,
                "active": active_users,
                "verified": verified_users,
                "new_today": new_users_today,
                "new_this_week": new_users_week,
                "growth_rate_weekly": round(user_growth_rate, 2),
                "with_portfolios": users_with_portfolios,
                "conversion_rate": round((users_with_portfolios / total_users * 100), 2) if total_users > 0 else 0
            },
            "portfolios": {
                "total_uploads": total_uploads,
                "unique_users": users_with_portfolios,
                "avg_per_user": round(avg_portfolios_per_user, 2),
                "total_holdings": total_holdings,
                "unique_funds": unique_funds,
                "avg_holdings_per_portfolio": round(total_holdings / total_portfolios, 2) if total_portfolios > 0 else 0
            },
            "aum": {
                "total": round(total_aum, 2),
                "total_invested": round(total_invested, 2),
                "total_returns": round(total_returns, 2),
                "avg_portfolio_value": round(avg_portfolio_value, 2),
                "return_percentage": round((total_returns / total_invested * 100), 2) if total_invested > 0 else 0,
                "total_lakhs": round(total_aum / 100000, 2),
                "total_crores": round(total_aum / 10000000, 2)
            },
            "top_amcs": [
                {
                    "name": amc[0] or "Unknown",
                    "total_value": round(float(amc[1]), 2),
                    "value_lakhs": round(float(amc[1]) / 100000, 2)
                }
                for amc in top_amcs if amc[0]
            ],
            "top_funds": [
                {
                    "name": fund[0],
                    "return_pct": round(float(fund[1] or 0), 2),
                    "total_value": round(float(fund[2]), 2)
                }
                for fund in top_funds
            ],
            "recent_activity": recent_activity
        }
        
    except Exception as e:
        logger.error(f"Error fetching admin stats: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch admin statistics: {str(e)}"
        )


@router.get("/users")
async def get_users_list(
    api_key: str = None,
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db)
) -> Dict:
    """
    Get list of users with pagination
    
    Query params:
        api_key: Admin API key
        skip: Number of records to skip
        limit: Maximum records to return
    """
    verify_admin(api_key)
    
    try:
        # Fixed N+1 query (#17) — use subquery to batch portfolio counts + AUM
        user_portfolio_subq = db.query(
            Portfolio.user_id,
            func.count(Portfolio.id).label('portfolio_count'),
            func.coalesce(func.sum(Portfolio.total_current), 0).label('total_aum')
        ).group_by(Portfolio.user_id).subquery()
        
        users_with_stats = db.query(
            User,
            func.coalesce(user_portfolio_subq.c.portfolio_count, 0).label('portfolio_count'),
            func.coalesce(user_portfolio_subq.c.total_aum, 0).label('total_aum')
        ).outerjoin(
            user_portfolio_subq,
            User.id == user_portfolio_subq.c.user_id
        ).order_by(desc(User.created_at)).offset(skip).limit(limit).all()
        
        total = db.query(func.count(User.id)).scalar()
        
        users_data = []
        for user, portfolio_count, total_aum in users_with_stats:
            users_data.append({
                "id": user.id,
                "email": user.email,
                "full_name": user.full_name,
                "pan": ("****" + user.pan[-4:]) if user.pan and len(user.pan) >= 4 else ("****" if user.pan else None),
                "phone": None,  # Redacted from list view for privacy
                "is_active": user.is_active,
                "is_verified": user.is_verified,
                "created_at": user.created_at.isoformat(),
                "portfolio_count": portfolio_count,
                "total_aum": round(float(total_aum), 2)
            })
        
        return {
            "total": total,
            "skip": skip,
            "limit": limit,
            "users": users_data
        }
        
    except Exception as e:
        logger.error(f"Error fetching users list: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch users: {str(e)}"
        )


@router.get("/analytics/timeline")
async def get_timeline_analytics(
    api_key: str = None,
    days: int = 30,
    db: Session = Depends(get_db)
) -> Dict:
    """
    Get timeline analytics (daily user registrations and uploads)
    
    Query params:
        api_key: Admin API key
        days: Number of days to look back (default 30)
    """
    verify_admin(api_key)
    
    try:
        start_date = datetime.utcnow() - timedelta(days=days)
        
        # Daily user registrations
        daily_users = db.query(
            func.date(User.created_at).label('date'),
            func.count(User.id).label('count')
        ).filter(
            User.created_at >= start_date
        ).group_by(func.date(User.created_at)).order_by('date').all()
        
        # Daily portfolio uploads
        daily_uploads = db.query(
            func.date(Portfolio.created_at).label('date'),
            func.count(Portfolio.id).label('count')
        ).filter(
            Portfolio.created_at >= start_date
        ).group_by(func.date(Portfolio.created_at)).order_by('date').all()
        
        return {
            "period_days": days,
            "start_date": start_date.date().isoformat(),
            "end_date": datetime.utcnow().date().isoformat(),
            "daily_registrations": [
                {"date": str(row.date), "count": row.count}
                for row in daily_users
            ],
            "daily_uploads": [
                {"date": str(row.date), "count": row.count}
                for row in daily_uploads
            ]
        }
        
    except Exception as e:
        logger.error(f"Error fetching timeline analytics: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch timeline analytics: {str(e)}"
        )
