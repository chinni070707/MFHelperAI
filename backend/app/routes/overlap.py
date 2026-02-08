"""
Enhanced Overlap Analysis Routes
Provides comprehensive fund overlap analysis with multiple visualization options
"""
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import List, Optional
import logging
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.models import Holding, User
from app.utils.auth import get_current_active_user
from app.utils.overlap_analyzer import OverlapAnalyzer

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/overlap", tags=["Overlap Analysis"])

# Initialize analyzer
analyzer = OverlapAnalyzer()

# Request/Response Models
class OverlapAnalysisRequest(BaseModel):
    fund_keys: List[str]
    analysis_type: Optional[str] = "detailed"  # "simple", "detailed", "portfolio"

class OverlapResponse(BaseModel):
    status: str
    data: dict

@router.get("/funds")
async def get_available_funds():
    """
    Get list of all available funds for overlap analysis
    """
    try:
        funds = analyzer.get_fund_list()
        return {
            "status": "success",
            "total": len(funds),
            "funds": funds
        }
    except Exception as e:
        logger.error(f"Error fetching funds: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/funds/{fund_key}")
async def get_fund_details(fund_key: str):
    """
    Get detailed holdings for a specific fund
    """
    try:
        fund = analyzer.get_fund_holdings(fund_key)
        if not fund:
            raise HTTPException(status_code=404, detail=f"Fund '{fund_key}' not found")
        
        return {
            "status": "success",
            "data": fund
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching fund details: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/analyze")
async def analyze_overlap(request: OverlapAnalysisRequest):
    """
    Analyze overlap between multiple funds
    
    **Analysis Types:**
    - `simple`: Basic overlap percentages
    - `detailed`: Detailed pairwise analysis with stock-level data
    - `portfolio`: Comprehensive portfolio-wide analysis with insights
    
    **Returns:**
    - Overlap percentages
    - Common stocks with weights
    - Sector overlap
    - Risk assessment
    - Actionable recommendations
    """
    try:
        if len(request.fund_keys) < 2:
            raise HTTPException(
                status_code=400,
                detail="At least 2 funds required for overlap analysis"
            )
        
        if len(request.fund_keys) > 10:
            raise HTTPException(
                status_code=400,
                detail="Maximum 10 funds allowed per analysis"
            )
        
        logger.info(f"Analyzing overlap for {len(request.fund_keys)} funds: {request.fund_keys}")
        
        # Validate all funds exist
        for key in request.fund_keys:
            if not analyzer.get_fund_holdings(key):
                raise HTTPException(
                    status_code=404,
                    detail=f"Fund '{key}' not found"
                )
        
        if request.analysis_type == "portfolio":
            # Comprehensive portfolio analysis
            result = analyzer.calculate_portfolio_overlap(request.fund_keys)
        else:
            # Pairwise analysis
            pairwise_overlaps = analyzer.calculate_pairwise_overlap(request.fund_keys)
            
            if request.analysis_type == "simple":
                # Simplified response
                result = {
                    "pairwise_overlaps": [
                        {
                            "funds": [o["fund1"]["name"], o["fund2"]["name"]],
                            "overlap_percentage": o["overlap_percentage"],
                            "risk_level": o["risk_level"]
                        }
                        for o in pairwise_overlaps
                    ]
                }
            else:
                # Detailed response
                result = {
                    "pairwise_overlaps": pairwise_overlaps,
                    "summary": {
                        "total_comparisons": len(pairwise_overlaps),
                        "avg_overlap": round(
                            sum(o["overlap_percentage"] for o in pairwise_overlaps) / len(pairwise_overlaps), 1
                        ) if pairwise_overlaps else 0,
                        "max_overlap": max((o["overlap_percentage"] for o in pairwise_overlaps), default=0),
                        "min_overlap": min((o["overlap_percentage"] for o in pairwise_overlaps), default=0)
                    }
                }
        
        return {
            "status": "success",
            "analysis_type": request.analysis_type,
            "fund_count": len(request.fund_keys),
            "data": result
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in overlap analysis: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/compare-two")
async def compare_two_funds(fund1_key: str, fund2_key: str):
    """
    Quick comparison between two specific funds
    Optimized for simple 2-fund comparisons
    """
    try:
        fund1 = analyzer.get_fund_holdings(fund1_key)
        fund2 = analyzer.get_fund_holdings(fund2_key)
        
        if not fund1 or not fund2:
            raise HTTPException(status_code=404, detail="One or both funds not found")
        
        overlap = analyzer._calculate_single_overlap(fund1_key, fund2_key)
        
        return {
            "status": "success",
            "data": overlap
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error comparing funds: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/portfolio/top-funds")
async def get_user_top_funds(
    limit: int = 5,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get user's top funds by invested amount for overlap analysis
    Returns fund details with investment amounts
    """
    try:
        # Get user's holdings sorted by invested amount
        holdings = db.query(Holding).filter(
            Holding.user_id == current_user.id
        ).order_by(
            Holding.invested_amount.desc()
        ).limit(limit).all()
        
        if not holdings:
            return {
                "status": "success",
                "message": "No holdings found",
                "funds": []
            }
        
        # Get all available funds to match keys
        available_funds = analyzer.get_fund_list()
        fund_name_to_key = {f["name"].lower(): f["key"] for f in available_funds}
        
        # Build response with fund details and amounts
        top_funds = []
        for holding in holdings:
            # Try to match fund name to available fund key
            fund_key = None
            holding_name_lower = holding.fund_name.lower()
            
            # Exact match
            if holding_name_lower in fund_name_to_key:
                fund_key = fund_name_to_key[holding_name_lower]
            else:
                # Partial match
                for name, key in fund_name_to_key.items():
                    if holding_name_lower in name or name in holding_name_lower:
                        fund_key = key
                        break
            
            fund_info = {
                "fund_name": holding.fund_name,
                "invested_amount": float(holding.invested_amount) if holding.invested_amount else 0,
                "current_value": float(holding.current_value) if holding.current_value else 0,
                "amc": holding.amc,
                "category": holding.category,
                "fund_key": fund_key,  # May be None if not found in holdings data
                "has_holdings_data": fund_key is not None
            }
            top_funds.append(fund_info)
        
        return {
            "status": "success",
            "total_funds": len(top_funds),
            "funds": top_funds,
            "total_invested": sum(f["invested_amount"] for f in top_funds)
        }
        
    except Exception as e:
        logger.error(f"Error getting top funds: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/recommendations/{fund_key}")
async def get_diversification_recommendations(fund_key: str, exclude_funds: Optional[List[str]] = None):
    """
    Get fund recommendations to diversify away from the given fund
    Returns funds with low overlap for better diversification
    """
    try:
        target_fund = analyzer.get_fund_holdings(fund_key)
        if not target_fund:
            raise HTTPException(status_code=404, detail=f"Fund '{fund_key}' not found")
        
        all_funds = analyzer.get_fund_list()
        exclude_set = set(exclude_funds or [])
        exclude_set.add(fund_key)  # Don't compare with itself
        
        # Compare with all other funds
        recommendations = []
        for fund in all_funds:
            if fund["key"] in exclude_set:
                continue
            
            overlap = analyzer._calculate_single_overlap(fund_key, fund["key"])
            if overlap:
                recommendations.append({
                    "fund": {
                        "key": fund["key"],
                        "name": fund["name"],
                        "amc": fund["amc"],
                        "category": fund["category"]
                    },
                    "overlap_percentage": overlap["overlap_percentage"],
                    "diversification_benefit": round(100 - overlap["overlap_percentage"], 1),
                    "risk_level": overlap["risk_level"]
                })
        
        # Sort by lowest overlap (best diversification)
        recommendations.sort(key=lambda x: x["overlap_percentage"])
        
        return {
            "status": "success",
            "target_fund": {
                "key": fund_key,
                "name": target_fund["name"]
            },
            "recommendations": recommendations[:20]  # Top 20 recommendations
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting recommendations: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
