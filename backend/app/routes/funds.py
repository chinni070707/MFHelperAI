"""
Funds List Routes
Provides searchable mutual fund master list for manual entry
"""
from fastapi import APIRouter, Depends, HTTPException, Query, Body
from sqlalchemy.orm import Session
from sqlalchemy import or_
from typing import List, Optional
import json
import logging
from pathlib import Path

from app.database import get_db
from app.models.models import FundMaster

router = APIRouter(prefix="/funds", tags=["Funds"])
logger = logging.getLogger(__name__)

# Lazy-loaded fund metrics cache
_fund_metrics_cache = None
_fund_metrics_mtime = 0


def _load_fund_metrics():
    """Load fund_metrics.json with file-mtime caching."""
    global _fund_metrics_cache, _fund_metrics_mtime
    metrics_file = Path(__file__).parent.parent.parent / "data" / "fund_metrics.json"
    if not metrics_file.exists():
        return {}
    mtime = metrics_file.stat().st_mtime
    if _fund_metrics_cache is None or mtime != _fund_metrics_mtime:
        with open(metrics_file, "r", encoding="utf-8") as f:
            data = json.load(f)
        _fund_metrics_cache = data.get("funds", {})
        _fund_metrics_mtime = mtime
        logger.info(f"Loaded fund metrics: {len(_fund_metrics_cache)} funds")
    return _fund_metrics_cache


@router.get("/list")
async def get_funds_list(
    search: Optional[str] = Query(None, description="Search by scheme name or AMC"),
    category: Optional[str] = Query(None, description="Filter by category"),
    amc: Optional[str] = Query(None, description="Filter by AMC"),
    plan_type: Optional[str] = Query(None, description="Filter by plan type (Direct/Regular)"),
    active_only: bool = Query(True, description="Show only active funds"),
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(50, ge=1, le=200, description="Results per page"),
    dropdown: bool = Query(False, description="Return dropdown format"),
    db: Session = Depends(get_db)
):
    """
    Get searchable list of mutual funds
    
    Supports:
    - Text search on scheme name and AMC
    - Filters by category, AMC, plan type
    - Pagination
    - Dropdown-optimized format
    """
    try:
        # Build query
        query = db.query(FundMaster)
        
        # Filter active funds
        if active_only:
            query = query.filter(FundMaster.is_active == True)
        
        # Text search
        if search:
            search_term = f"%{search}%"
            query = query.filter(
                or_(
                    FundMaster.scheme_name.ilike(search_term),
                    FundMaster.amc.ilike(search_term),
                    FundMaster.scheme_code.ilike(search_term)
                )
            )
        
        # Category filter
        if category:
            query = query.filter(FundMaster.category == category)
        
        # AMC filter
        if amc:
            query = query.filter(FundMaster.amc == amc)
        
        # Plan type filter
        if plan_type:
            query = query.filter(FundMaster.plan_type == plan_type)
        
        # Get total count
        total = query.count()
        
        # Apply pagination
        offset = (page - 1) * limit
        funds = query.order_by(FundMaster.scheme_name).offset(offset).limit(limit).all()
        
        # Format response
        if dropdown:
            results = [fund.to_dropdown_option() for fund in funds]
        else:
            results = [fund.to_dict() for fund in funds]
        
        return {
            "success": True,
            "funds": results,
            "pagination": {
                "page": page,
                "limit": limit,
                "total": total,
                "totalPages": (total + limit - 1) // limit
            }
        }
        
    except Exception as e:
        logger.error(f"Error fetching funds list: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch funds list: {str(e)}"
        )


@router.get("/categories")
async def get_categories(db: Session = Depends(get_db)):
    """Get list of all fund categories"""
    try:
        categories = db.query(FundMaster.category).filter(
            FundMaster.is_active == True
        ).distinct().order_by(FundMaster.category).all()
        
        return {
            "success": True,
            "categories": [cat[0] for cat in categories if cat[0]]
        }
    except Exception as e:
        logger.error(f"Error fetching categories: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/amcs")
async def get_amcs(db: Session = Depends(get_db)):
    """Get list of all AMCs (Asset Management Companies)"""
    try:
        amcs = db.query(FundMaster.amc).filter(
            FundMaster.is_active == True
        ).distinct().order_by(FundMaster.amc).all()
        
        return {
            "success": True,
            "amcs": [amc[0] for amc in amcs if amc[0]]
        }
    except Exception as e:
        logger.error(f"Error fetching AMCs: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/amc-list")
async def get_amc_list(
    db: Session = Depends(get_db)
):
    """
    Get list of all AMCs (Asset Management Companies)
    
    Returns unique list of AMC names for dropdown
    """
    try:
        # Get unique AMCs from fund master
        amcs = db.query(FundMaster.amc).filter(
            FundMaster.amc.isnot(None),
            FundMaster.amc != '',
            FundMaster.is_active == True
        ).distinct().order_by(FundMaster.amc).all()
        
        amc_list = [amc[0] for amc in amcs if amc[0]]
        
        return {
            "success": True,
            "amcs": amc_list,
            "count": len(amc_list)
        }
        
    except Exception as e:
        logger.error(f"Error fetching AMC list: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# -------------------------------------------------------------------
# Fund Metrics Endpoints (computed from NAV history)
# Must be BEFORE /{fund_id} to avoid path-parameter conflict
# -------------------------------------------------------------------

@router.get("/metrics")
async def get_fund_metrics(
    name: Optional[str] = Query(None, description="Search by fund name (substring match)"),
    mc_code: Optional[str] = Query(None, description="MoneyControl fund code"),
    scheme_code: Optional[str] = Query(None, description="AMFI scheme code"),
):
    """
    Get computed risk/return metrics for a fund from fund_metrics.json.
    
    Returns: Sharpe, Sortino, Beta, Alpha, StdDev, Max Drawdown, 
    Returns (1M-10Y), Benchmark metrics (R-squared, Treynor, Info Ratio,
    Up/Down Capture), and Portfolio stats.
    """
    metrics = _load_fund_metrics()
    
    if not metrics:
        raise HTTPException(status_code=404, detail="Fund metrics data not available. Run scrape_fund_metrics.py first.")
    
    # Search by MoneyControl code
    if mc_code:
        fund = metrics.get(mc_code)
        if fund:
            return {"success": True, "fund": fund}
        raise HTTPException(status_code=404, detail=f"No metrics found for MC code: {mc_code}")
    
    # Search by AMFI scheme code
    if scheme_code:
        for code, fund in metrics.items():
            if str(fund.get("scheme_code")) == str(scheme_code):
                return {"success": True, "fund": fund}
        raise HTTPException(status_code=404, detail=f"No metrics found for scheme code: {scheme_code}")
    
    # Search by name (substring)
    if name:
        name_lower = name.lower()
        results = []
        for code, fund in metrics.items():
            fund_name = fund.get("name", "").lower()
            if name_lower in fund_name:
                results.append({**fund, "_mc_code": code})
        
        if results:
            return {"success": True, "count": len(results), "funds": results[:20]}
        raise HTTPException(status_code=404, detail=f"No funds matching: {name}")
    
    # No filter - return summary
    return {
        "success": True,
        "total_funds": len(metrics),
        "funds_available": list(metrics.keys())[:50],
    }


@router.post("/metrics/batch")
async def get_fund_metrics_batch(
    fund_names: List[str] = Body(..., description="List of fund names to look up"),
):
    """
    Get metrics for multiple funds at once (used by risk analyzer page).
    
    Accepts a list of fund names and returns the best matching metrics
    for each. Uses fuzzy substring matching.
    """
    metrics = _load_fund_metrics()
    
    if not metrics:
        return {"success": False, "error": "Fund metrics not available", "results": {}}
    
    results = {}
    
    for query_name in fund_names:
        if not query_name:
            continue
        
        query_lower = query_name.lower()
        # Remove common suffixes for better matching
        query_clean = query_lower
        for suffix in [" - direct plan - growth", " - direct - growth",
                       " - growth option", " - direct plan", " direct growth",
                       " growth", " direct"]:
            query_clean = query_clean.replace(suffix, "")
        query_clean = query_clean.strip()
        
        best_match = None
        best_score = 0
        
        for code, fund in metrics.items():
            fund_name_lower = fund.get("name", "").lower()
            
            # Exact match
            if query_lower == fund_name_lower:
                best_match = fund
                best_match["_mc_code"] = code
                best_score = 100
                break
            
            # Clean name match
            fund_clean = fund_name_lower
            for suffix in [" - direct plan - growth option", " - growth option",
                           " - direct plan", " direct growth", " growth", " direct"]:
                fund_clean = fund_clean.replace(suffix, "")
            fund_clean = fund_clean.strip()
            
            if query_clean == fund_clean:
                best_match = {**fund, "_mc_code": code}
                best_score = 90
                continue
            
            # Substring match
            if query_clean in fund_clean or fund_clean in query_clean:
                score = len(query_clean) / max(len(fund_clean), 1) * 80
                if score > best_score:
                    best_match = {**fund, "_mc_code": code}
                    best_score = score
        
        if best_match:
            results[query_name] = best_match
    
    return {
        "success": True,
        "matched": len(results),
        "total_requested": len(fund_names),
        "results": results,
    }


@router.get("/metrics/summary")
async def get_fund_metrics_summary():
    """
    Get a summary of available fund metrics data.
    Useful for checking data freshness and coverage.
    """
    metrics = _load_fund_metrics()
    metrics_file = Path(__file__).parent.parent.parent / "data" / "fund_metrics.json"
    
    if not metrics:
        return {"available": False, "message": "No fund metrics data available"}
    
    # Read file header
    with open(metrics_file, "r", encoding="utf-8") as f:
        full_data = json.load(f)
    
    # Compute coverage stats
    has_risk = sum(1 for f in metrics.values() if f.get("risk", {}).get("1y"))
    has_benchmark = sum(1 for f in metrics.values() if f.get("benchmark", {}).get("available"))
    has_portfolio = sum(1 for f in metrics.values() if f.get("portfolio", {}).get("num_stocks"))
    
    categories = {}
    for fund in metrics.values():
        cat = fund.get("mc_category", fund.get("category", "Unknown"))
        categories[cat] = categories.get(cat, 0) + 1
    
    return {
        "available": True,
        "total_funds": len(metrics),
        "last_updated": full_data.get("last_updated"),
        "source": full_data.get("source"),
        "risk_free_rate": full_data.get("risk_free_rate"),
        "benchmark": full_data.get("benchmark"),
        "coverage": {
            "risk_metrics": has_risk,
            "benchmark_metrics": has_benchmark,
            "portfolio_stats": has_portfolio,
        },
        "categories": categories,
    }


# -------------------------------------------------------------------
# Individual Fund Details (catch-all route - MUST be last)
# -------------------------------------------------------------------

@router.get("/{fund_id}")
async def get_fund_details(fund_id: int, db: Session = Depends(get_db)):
    """Get detailed information about a specific fund"""
    try:
        fund = db.query(FundMaster).filter(FundMaster.id == fund_id).first()
        
        if not fund:
            raise HTTPException(status_code=404, detail="Fund not found")
        
        return {
            "success": True,
            "fund": fund.to_dict()
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching fund details: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/seed")
async def seed_funds_master(
    funds_data: List[dict],
    db: Session = Depends(get_db)
):
    """
    Admin endpoint to seed funds master data
    Accepts list of fund dictionaries
    """
    try:
        added = 0
        updated = 0
        
        for fund_data in funds_data:
            # Check if fund exists by scheme_code
            existing = None
            if fund_data.get("scheme_code"):
                existing = db.query(FundMaster).filter(
                    FundMaster.scheme_code == fund_data["scheme_code"]
                ).first()
            
            if existing:
                # Update existing fund
                for key, value in fund_data.items():
                    setattr(existing, key, value)
                updated += 1
            else:
                # Add new fund
                fund = FundMaster(**fund_data)
                db.add(fund)
                added += 1
        
        db.commit()
        
        logger.info(f"Funds master seeded: {added} added, {updated} updated")
        
        return {
            "success": True,
            "added": added,
            "updated": updated,
            "total": added + updated
        }
        
    except Exception as e:
        db.rollback()
        logger.error(f"Error seeding funds master: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/validate")
async def validate_fund_data(
    db: Session = Depends(get_db)
):
    """
    Validate fund master data integrity
    
    Runs comprehensive sanity checks:
    - Data existence
    - AMC data validity
    - Fund completeness
    - Duplicate detection
    - Invalid data values
    - Data freshness
    
    Returns validation results with passed/failed checks
    """
    try:
        from app.utils.data_validator import validate_fund_data as run_validation
        
        logger.info("Running fund data validation...")
        results = run_validation(db)
        
        return {
            "success": True,
            "validation": results
        }
        
    except Exception as e:
        logger.error(f"Error validating fund data: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
