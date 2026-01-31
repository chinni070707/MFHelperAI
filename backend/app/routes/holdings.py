"""
Fund Holdings and Portfolio Overlap Analysis
Uses Database instead of JSON for better performance and scalability
"""
from fastapi import APIRouter, HTTPException, Body, Depends
from pydantic import BaseModel
from typing import List, Dict, Optional
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.fund_holdings import FundMaster, FundHolding, FundSectorAllocation
import logging

# Setup logger
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/holdings", tags=["Holdings"])

class OverlapRequest(BaseModel):
    fund_names: List[str]

class OverlapResponse(BaseModel):
    overlapping_stocks: Dict
    overlap_percentage: float
    total_unique_stocks: int
    sector_overlap: Dict
    concentration_alerts: List[str]

def normalize_fund_name(name: str) -> str:
    """Normalize fund name to match keys in database"""
    return name.lower().replace(" ", "-").replace("fund", "").strip("-")

@router.get("/")
async def list_funds(db: Session = Depends(get_db)):
    """Get list of all available funds from database"""
    logger.info("Fetching list of all available funds from database")
    
    funds = db.query(FundMaster).all()
    logger.debug(f"Found {len(funds)} funds in database")
    
    fund_list = []
    for fund in funds:
        holdings_count = db.query(FundHolding).filter(FundHolding.fund_id == fund.id).count()
        fund_list.append({
            "key": fund.fund_key,
            "name": fund.fund_name,
            "amc": fund.amc,
            "category": fund.category,
            "holdings_count": holdings_count
        })
    
    logger.info(f"Returning {len(fund_list)} funds with holdings data")
    
    return {
        "total": len(fund_list),
        "last_updated": funds[0].updated_at.isoformat() if funds else None,
        "funds": fund_list
    }

@router.get("/fund/{fund_key}")
async def get_fund_holdings(fund_key: str, db: Session = Depends(get_db)):
    """Get detailed holdings for a specific fund from database"""
    fund = db.query(FundMaster).filter(FundMaster.fund_key == fund_key).first()
    
    if not fund:
        raise HTTPException(status_code=404, detail=f"Fund '{fund_key}' not found")
    
    # Get holdings
    holdings = db.query(FundHolding).filter(FundHolding.fund_id == fund.id).all()
    
    # Get sector allocations
    sectors = db.query(FundSectorAllocation).filter(FundSectorAllocation.fund_id == fund.id).all()
    
    return {
        "name": fund.fund_name,
        "amc": fund.amc,
        "category": fund.category,
        "holdings": [
            {
                "stock": h.stock_name,
                "weight": h.weight,
                "sector": h.sector
            }
            for h in holdings
        ],
        "sector_allocation": {
            s.sector: s.weight
            for s in sectors
        },
        "updated_at": fund.updated_at.isoformat()
    }

@router.post("/overlap", response_model=OverlapResponse)
async def calculate_overlap(request: OverlapRequest, db: Session = Depends(get_db)):
    """
    Calculate portfolio overlap between multiple funds using database
    
    Returns:
    - Overlapping stocks (appearing in 2+ funds)
    - Overlap percentage
    - Sector overlap
    - Concentration alerts
    """
    fund_names = request.fund_names
    
    # Find funds in database
    funds_data = []
    for fund_name in fund_names:
        # Try exact key match first
        fund_key = normalize_fund_name(fund_name)
        fund = db.query(FundMaster).filter(FundMaster.fund_key == fund_key).first()
        
        # If not found, try partial name match
        if not fund:
            fund = db.query(FundMaster).filter(
                FundMaster.fund_name.ilike(f"%{fund_name}%")
            ).first()
        
        if fund:
            # Get holdings
            holdings = db.query(FundHolding).filter(FundHolding.fund_id == fund.id).all()
            
            # Get sector allocations
            sectors = db.query(FundSectorAllocation).filter(
                FundSectorAllocation.fund_id == fund.id
            ).all()
            
            funds_data.append({
                "name": fund.fund_name,
                "holdings": [
                    {"stock": h.stock_name, "weight": h.weight, "sector": h.sector}
                    for h in holdings
                ],
                "sectors": {s.sector: s.weight for s in sectors}
            })
        else:
            print(f"⚠️ Fund not found: {fund_name}")
    
    if len(funds_data) < 2:
        raise HTTPException(
            status_code=400, 
            detail=f"Need at least 2 funds for overlap analysis. Found {len(funds_data)} matching funds."
        )
    
    # Calculate stock overlap
    all_stocks = {}
    all_sectors = {}
    
    for fund in funds_data:
        fund_name = fund["name"]
        
        # Track stocks
        for holding in fund["holdings"]:
            stock = holding["stock"]
            if stock not in all_stocks:
                all_stocks[stock] = []
            all_stocks[stock].append({
                "fund": fund_name,
                "weight": holding["weight"],
                "sector": holding["sector"]
            })
        
        # Track sectors
        for sector, weight in fund["sectors"].items():
            if sector not in all_sectors:
                all_sectors[sector] = []
            all_sectors[sector].append({
                "fund": fund_name,
                "weight": weight
            })
    
    # Find overlapping stocks (appearing in 2+ funds)
    overlapping_stocks = {
        stock: funds_list 
        for stock, funds_list in all_stocks.items() 
        if len(funds_list) > 1
    }
    
    # Find overlapping sectors
    overlapping_sectors = {
        sector: funds_list 
        for sector, funds_list in all_sectors.items() 
        if len(funds_list) > 1
    }
    
    # Calculate overlap percentage
    total_unique_stocks = len(all_stocks)
    overlap_count = len(overlapping_stocks)
    overlap_percentage = (overlap_count / total_unique_stocks * 100) if total_unique_stocks > 0 else 0
    
    # Generate concentration alerts
    concentration_alerts = []
    
    # Alert if any stock appears in all funds
    for stock, funds_list in overlapping_stocks.items():
        if len(funds_list) == len(funds_data):
            total_weight = sum(f["weight"] for f in funds_list)
            concentration_alerts.append(
                f"⚠️ {stock} appears in ALL {len(funds_data)} funds (combined {total_weight:.1f}%)"
            )
    
    # Alert if any stock has >15% combined exposure
    for stock, funds_list in overlapping_stocks.items():
        total_weight = sum(f["weight"] for f in funds_list)
        if total_weight > 15:
            concentration_alerts.append(
                f"⚠️ High exposure to {stock}: {total_weight:.1f}% across {len(funds_list)} funds"
            )
    
    # Alert on sector over-concentration
    for sector, funds_list in overlapping_sectors.items():
        if sector == "Others":
            continue
        total_weight = sum(f["weight"] for f in funds_list)
        avg_weight = total_weight / len(funds_list)
        if avg_weight > 25:
            concentration_alerts.append(
                f"⚠️ Sector {sector} is overweighted: avg {avg_weight:.1f}% across funds"
            )
    
    return {
        "overlapping_stocks": overlapping_stocks,
        "overlap_percentage": round(overlap_percentage, 2),
        "total_unique_stocks": total_unique_stocks,
        "sector_overlap": overlapping_sectors,
        "concentration_alerts": concentration_alerts
    }

@router.post("/portfolio-overlap")
async def analyze_user_portfolio(
    fund_names: List[str] = Body(..., embed=True),
    db: Session = Depends(get_db)
):
    """
    Analyze overlap in user's actual portfolio
    Simplified version that returns visualization-friendly data
    """
    result = await calculate_overlap(OverlapRequest(fund_names=fund_names), db)
    
    # Format for easy visualization
    top_overlaps = sorted(
        result["overlapping_stocks"].items(),
        key=lambda x: len(x[1]),
        reverse=True
    )[:10]  # Top 10 most overlapping stocks
    
    return {
        "summary": {
            "overlap_percentage": result["overlap_percentage"],
            "total_stocks": result["total_unique_stocks"],
            "overlapping_stocks_count": len(result["overlapping_stocks"]),
            "alerts_count": len(result["concentration_alerts"])
        },
        "top_overlaps": [
            {
                "stock": stock,
                "appears_in": len(funds),
                "funds": [{"name": f["fund"], "weight": f["weight"]} for f in funds],
                "total_exposure": sum(f["weight"] for f in funds)
            }
            for stock, funds in top_overlaps
        ],
        "alerts": result["concentration_alerts"]
    }

@router.get("/stats")
async def get_database_stats(db: Session = Depends(get_db)):
    """Get statistics about holdings database"""
    total_funds = db.query(FundMaster).count()
    total_holdings = db.query(FundHolding).count()
    total_sectors = db.query(FundSectorAllocation).count()
    
    # Get unique stocks
    unique_stocks = db.query(FundHolding.stock_name).distinct().count()
    
    # Get latest update
    latest_fund = db.query(FundMaster).order_by(FundMaster.updated_at.desc()).first()
    
    return {
        "total_funds": total_funds,
        "total_holdings": total_holdings,
        "total_sectors": total_sectors,
        "unique_stocks": unique_stocks,
        "last_updated": latest_fund.updated_at.isoformat() if latest_fund else None
    }
