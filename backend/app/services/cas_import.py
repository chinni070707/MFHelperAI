"""
CAS Import Service - Convert casparser output to database records  
"""
from sqlalchemy.orm import Session
from datetime import datetime
import re
from decimal import Decimal

from app.models.models import Portfolio, Holding, Transaction


def safe_float_convert(value, field_name="value", default=0.0) -> float:
    """Safely convert various types to float with multiple fallback strategies"""
    if value is None or value == '':
        return default
    
    original_value = value  # Keep original for logging
    original_type = type(value).__name__
    
    if isinstance(value, (int, float)):
        return float(value)
    if isinstance(value, Decimal):
        return float(value)
    if isinstance(value, str):
        try:
            return float(value)
        except ValueError:
            try:
                cleaned = re.sub(r'[₹$,\s]', '', value)
                cleaned = re.sub(r'^Rs\.?', '', cleaned, flags=re.IGNORECASE)
                cleaned = cleaned.strip()
                if cleaned:
                    return float(cleaned)
                else:
                    return default
            except ValueError:
                match = re.search(r'-?\d+\.?\d*', value)
                if match:
                    try:
                        return float(match.group())
                    except ValueError:
                        pass
    
    # Log detailed conversion failure for debugging
    import logging
    logger = logging.getLogger(__name__)
    logger.error(
        f"❌ CONVERSION FAILED | "
        f"Field: {field_name} | "
        f"Value: '{original_value}' | "
        f"Type: {original_type} | "
        f"Length: {len(str(original_value))} | "
        f"Using default: {default}"
    )
    return default


def detect_category(scheme_name: str) -> str:
    """Detect fund category from scheme name"""
    scheme_lower = scheme_name.lower()
    if any(word in scheme_lower for word in ['large cap', 'large & mid', 'bluechip']):
        return 'Large Cap'
    elif 'mid cap' in scheme_lower or 'midcap' in scheme_lower:
        return 'Mid Cap'
    elif 'small cap' in scheme_lower or 'smallcap' in scheme_lower:
        return 'Small Cap'
    elif any(word in scheme_lower for word in ['flexi cap', 'flexicap', 'multi cap', 'multicap']):
        return 'Flexi Cap'
    elif any(word in scheme_lower for word in ['focused', 'focus']):
        return 'Focused'
    elif any(word in scheme_lower for word in ['elss', 'tax saver', 'tax saving']):
        return 'ELSS'
    elif any(word in scheme_lower for word in ['value', 'contra']):
        return 'Value'
    elif any(word in scheme_lower for word in ['sectoral', 'thematic', 'pharma', 'healthcare', 'banking', 'technology', 'digital', 'infrastructure']):
        return 'Sectoral/Thematic'
    elif any(word in scheme_lower for word in ['international', 'overseas', 'us ', 'nasdaq', 'fang', 'global']):
        return 'International'
    elif any(word in scheme_lower for word in ['liquid', 'overnight']):
        return 'Liquid'
    elif any(word in scheme_lower for word in ['ultra short', 'ultrashort']):
        return 'Ultra Short Duration'
    elif any(word in scheme_lower for word in ['short duration', 'short term']):
        return 'Short Duration'
    elif any(word in scheme_lower for word in ['corporate bond', 'corporate debt']):
        return 'Corporate Bond'
    elif any(word in scheme_lower for word in ['banking & psu', 'banking and psu']):
        return 'Banking & PSU'
    elif any(word in scheme_lower for word in ['gilt', 'government']):
       return 'Gilt'
    elif any(word in scheme_lower for word in ['dynamic bond', 'income']):
        return 'Dynamic Bond'
    elif any(word in scheme_lower for word in ['credit risk']):
        return 'Credit Risk'
    elif any(word in scheme_lower for word in ['debt', 'bond', 'fixed income']):
        return 'Debt'
    elif any(word in scheme_lower for word in ['hybrid', 'balanced', 'aggressive', 'conservative']):
        return 'Hybrid'
    return 'Equity'


def import_cas_to_database(cas_data, user_id: int, db

: Session) -> dict:
    """Import CAS data into database - returns dict with portfolio_id and stats"""
    portfolio = Portfolio(
        user_id=user_id,
        name=f"CAS Import - {datetime.now().strftime('%b %Y')}",
        source="cas_pdf",
        upload_date=datetime.utcnow()
    )
    total_invested = 0
    total_current = 0
    holdings_to_create = []
    skipped_schemes = []
    
    for folio in cas_data.folios:
        for scheme in folio.schemes:
            if not scheme.close or scheme.close == 0:
                continue
            if scheme.valuation:
                units = safe_float_convert(scheme.close, "units", 0)
                nav = safe_float_convert(scheme.valuation.nav, "NAV", 0)
                current_value = safe_float_convert(scheme.valuation.value, "current_value", 0)
                invested_amount = safe_float_convert(scheme.valuation.cost, "cost", 0)
                if units == 0 and current_value == 0 and invested_amount == 0:
                    # Log detailed info about skipped scheme
                    skipped_info = {
                        "scheme": scheme.scheme,
                        "folio": folio.folio,
                        "amc": folio.amc,
                        "reason": "All numeric fields are zero or invalid",
                        "raw_values": {
                            "close": str(scheme.close),
                            "nav": str(scheme.valuation.nav) if scheme.valuation else "N/A",
                            "value": str(scheme.valuation.value) if scheme.valuation else "N/A",
                            "cost": str(scheme.valuation.cost) if scheme.valuation else "N/A"
                        }
                    }
                    skipped_schemes.append(skipped_info)
                    continue
                total_invested += invested_amount
                total_current += current_value
                category = detect_category(scheme.scheme)
                holding = Holding(
                    fund_name=scheme.scheme, isin=scheme.isin or '', amfi_code=scheme.amfi or '',
                    folio_number=folio.folio, units=units, nav=nav,
                    invested_amount=invested_amount, current_value=current_value,
                    category=category, amc=folio.amc, rta=scheme.rta or '', fund_type=scheme.type or 'EQUITY'
                )
                holdings_to_create.append(holding)
    
    if skipped_schemes:
        import logging
        logger = logging.getLogger(__name__)
        logger.error("=" * 80)
        logger.error(f"⚠️  CAS IMPORT DATA QUALITY WARNING")
        logger.error(f"User ID: {user_id}")
        logger.error(f"Total Schemes Skipped: {len(skipped_schemes)}")
        logger.error(f"Total Holdings Imported: {len(holdings_to_create)}")
        logger.error("=" * 80)
        
        # Log each skipped scheme with full details
        for idx, skipped in enumerate(skipped_schemes, 1):
            logger.error(f"SKIPPED #{idx}:")
            logger.error(f"  Scheme: {skipped['scheme']}")
            logger.error(f"  Folio: {skipped['folio']}")
            logger.error(f"  AMC: {skipped.get('amc', 'N/A')}")
            logger.error(f"  Reason: {skipped['reason']}")
            if 'raw_values' in skipped:
                logger.error(f"  Raw Values from CAS:")
                for field, value in skipped['raw_values'].items():
                    logger.error(f"    {field}: '{value}' (type: {type(value).__name__})")
        
        logger.error("=" * 80)
        logger.error("💡 ACTION REQUIRED: Review these parsing failures to improve code")
        logger.error("=" * 80)
    
    portfolio.total_invested = round(total_invested, 2)
    portfolio.total_current = round(total_current, 2)
    portfolio.total_gain_loss = round(total_current - total_invested, 2)
    portfolio.total_return_pct = round(((total_current / total_invested - 1) * 100), 2) if total_invested > 0 else 0
    db.add(portfolio)
    db.flush()
    for holding in holdings_to_create:
        holding.portfolio_id = portfolio.id
        db.add(holding)
    db.commit()
    db.refresh(portfolio)
    return {"portfolio_id": portfolio.id, "skipped_schemes": skipped_schemes, "total_imported": len(holdings_to_create), "total_skipped": len(skipped_schemes)}


def import_cas_transactions(cas_data, portfolio_id: int, db: Session):
    """Import transaction history from CAS"""
    transactions_to_create = []
    for folio in cas_data.folios:
        for scheme in folio.schemes:
            for txn in scheme.transactions:
                amount_val = safe_float_convert(txn.amount, "amount", 0)
                units_val = safe_float_convert(txn.units, "units", 0)
                nav_val = safe_float_convert(txn.nav, "NAV", 0)
                if amount_val == 0 and units_val == 0:
                    continue
                try:
                    transaction = Transaction(
                        portfolio_id=portfolio_id, fund_name=scheme.scheme, folio_number=folio.folio,
                        transaction_date=txn.date, transaction_type='PURCHASE' if units_val > 0 else 'REDEMPTION',
                        amount=abs(amount_val), units=abs(units_val), nav=nav_val,
                        description=txn.description if txn.description else ''
                    )
                    transactions_to_create.append(transaction)
                except (ValueError, TypeError, AttributeError):
                    continue
    if transactions_to_create:
        db.bulk_save_objects(transactions_to_create)
        db.commit()
    return len(transactions_to_create)
