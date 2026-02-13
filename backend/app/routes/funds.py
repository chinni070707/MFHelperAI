"""
Funds List Routes
Provides searchable mutual fund master list for manual entry
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import or_
from typing import List, Optional
import logging

from app.database import get_db
from app.models.models import FundMaster

router = APIRouter(prefix="/funds", tags=["Funds"])
logger = logging.getLogger(__name__)


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

