"""
CAS Upload Route - Parse and import Consolidated Account Statement PDFs
Supports CAMS, KFintech, and NSDL/CDSL formats
"""
from fastapi import APIRouter, UploadFile, File, Form, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Optional
import tempfile
import os

from app.database import get_db
from app.models.models import User
from app.utils.auth import get_current_user

router = APIRouter(prefix="/api/cas", tags=["CAS Import"])


@router.post("/cas", response_model=dict)
async def upload_cas(
    file: UploadFile = File(...),
    password: Optional[str] = Form(None),
    save_to_db: bool = Form(True),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Upload and parse CAS PDF file
    
    - **file**: CAS PDF file (CAMS/KFintech/NSDL/CDSL)
    - **password**: PDF password (usually PAN number)
    - **save_to_db**: Whether to save parsed data to database (default: True)
    
    Returns:
    - Parsed portfolio summary
    - List of folios with schemes
    - Investment summary (cost, value, gains)
    """
    
    # Validate file type
    if not file.filename.endswith('.pdf'):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only PDF files are supported"
        )
    
    # Read file content
    content = await file.read()
    
    # Security: Validate file size (10MB max)
    MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
    if len(content) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"File size exceeds maximum allowed size of {MAX_FILE_SIZE / (1024*1024):.0f}MB"
        )
    
    # Security: Validate file is actually a PDF
    if not content.startswith(b'%PDF'):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File does not appear to be a valid PDF"
        )
    
    # Create temporary file to store upload
    temp_file = None
    try:
        # Save uploaded file to temp location
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as temp_file:
            temp_file.write(content)
            temp_file_path = temp_file.name
        
        # Parse CAS using casparser (lazy import — needs libpoppler on Linux)
        try:
            import casparser
            cas_data = casparser.read_cas_pdf(temp_file_path, password or "")
        except Exception as parse_error:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Failed to parse CAS PDF: {str(parse_error)}. "
                       f"Please check the password and ensure the file is a valid CAS PDF."
            )
        
        # Extract summary information
        total_value = 0
        total_cost = 0
        total_schemes = 0
        folios_summary = []
        
        for folio in cas_data.folios:
            folio_value = 0
            folio_cost = 0
            schemes_list = []
            
            for scheme in folio.schemes:
                total_schemes += 1
                
                # Import the safe converter
                from app.services.cas_import import safe_float_convert
                
                # Use smart conversion
                units = safe_float_convert(scheme.close, "units", 0)
                
                # Extract broker/advisor information if available
                broker = None
                if hasattr(scheme, 'advisor') and scheme.advisor:
                    broker = str(scheme.advisor).strip()
                
                scheme_info = {
                    "scheme_name": scheme.scheme,
                    "isin": scheme.isin,
                    "amfi_code": scheme.amfi,
                    "type": scheme.type,
                    "units": units,
                    "broker": broker,
                }
                
                if scheme.valuation:
                    # Use robust conversion with fallbacks
                    scheme_value = safe_float_convert(scheme.valuation.value, "value", 0)
                    scheme_cost = safe_float_convert(scheme.valuation.cost, "cost", 0)
                    nav_value = safe_float_convert(scheme.valuation.nav, "NAV", 0)
                    
                    scheme_info.update({
                        "nav": nav_value,
                        "current_value": scheme_value,
                        "invested_amount": scheme_cost,
                        "gain_loss": scheme_value - scheme_cost,
                        "return_pct": ((scheme_value / scheme_cost - 1) * 100) if scheme_cost > 0 else 0,
                        "valuation_date": str(scheme.valuation.date) if scheme.valuation.date else ""
                    })
                    
                    folio_value += scheme_value
                    folio_cost += scheme_cost
                    total_value += scheme_value
                    total_cost += scheme_cost
                
                scheme_info["transactions_count"] = len(scheme.transactions)
                schemes_list.append(scheme_info)
            
            folios_summary.append({
                "folio_number": folio.folio,
                "amc": folio.amc,
                "pan": folio.PAN,
                "kyc_status": folio.KYC,
                "schemes_count": len(folio.schemes),
                "total_value": folio_value,
                "total_cost": folio_cost,
                "gain_loss": folio_value - folio_cost,
                "schemes": schemes_list
            })
        
        response_data = {
            "success": True,
            "message": "CAS parsed successfully",
            "file_info": {
                "file_type": cas_data.file_type.value if hasattr(cas_data.file_type, 'value') else str(cas_data.file_type),
                "cas_type": cas_data.cas_type.value if hasattr(cas_data.cas_type, 'value') else str(cas_data.cas_type),
                "statement_period": {
                    "from": str(cas_data.statement_period.from_),
                    "to": str(cas_data.statement_period.to)
                }
            },
            "investor_info": {
                "name": cas_data.investor_info.name if cas_data.investor_info else None,
                "email": cas_data.investor_info.email if cas_data.investor_info else None,
                "mobile": cas_data.investor_info.mobile if cas_data.investor_info else None,
            },
            "summary": {
                "total_folios": len(cas_data.folios),
                "total_schemes": total_schemes,
                "total_invested": round(total_cost, 2),
                "current_value": round(total_value, 2),
                "total_gain_loss": round(total_value - total_cost, 2),
                "overall_return_pct": round(((total_value / total_cost - 1) * 100), 2) if total_cost > 0 else 0
            },
            "folios": folios_summary
        }
        
        # Save to database if requested
        if save_to_db:
            import_result = await save_cas_to_database(
                cas_data=cas_data,
                user_id=current_user.id,
                db=db
            )
            response_data["portfolio_id"] = import_result["portfolio_id"]
            response_data["import_stats"] = {
                "total_imported": import_result["total_imported"],
                "total_skipped": import_result["total_skipped"],
                "skipped_schemes": import_result["skipped_schemes"]
            }
            
            # Add warning message if schemes were skipped
            if import_result["total_skipped"] > 0:
                response_data["message"] = f"CAS saved - {import_result['total_imported']} holdings imported. ⚠️ {import_result['total_skipped']} schemes had data issues and were skipped."
                response_data["warnings"] = [
                    f"Some schemes could not be imported due to invalid data.",
                    f"{import_result['total_skipped']} schemes were skipped - see details below.",
                    "This has been logged for admin review."
                ]
            else:
                response_data["message"] = "CAS parsed and saved to database successfully"
        
        return response_data
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing CAS file: {str(e)}"
        )
    finally:
        # Clean up temporary file
        if temp_file and os.path.exists(temp_file_path):
            try:
                os.unlink(temp_file_path)
            except:
                pass


async def save_cas_to_database(cas_data, user_id: int, db: Session) -> dict:
    """
    Save parsed CAS data to database
    Creates Portfolio and Holding records, then imports transactions
    Returns dict with portfolio_id and import statistics
    """
    from app.services.cas_import import import_cas_to_database, import_cas_transactions
    
    import_result = import_cas_to_database(
        cas_data=cas_data,
        user_id=user_id,
        db=db
    )
    
    portfolio_id = import_result["portfolio_id"]
    
    # Import transactions for XIRR and analytics
    try:
        import_cas_transactions(
            cas_data=cas_data,
            portfolio_id=portfolio_id,
            db=db
        )
    except Exception as e:
        # Log but don't fail — transactions are optional for XIRR
        import logging
        logger = logging.getLogger(__name__)
        logger.warning(f"Failed to import CAS transactions: {str(e)}")
    
    return import_result
