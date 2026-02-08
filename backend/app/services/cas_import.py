"""
CAS Import Service - Convert casparser output to database records
"""
from sqlalchemy.orm import Session
from datetime import datetime

from app.models.models import Portfolio, Holding, Transaction


def detect_category(scheme_name: str) -> str:
    """
    Detect fund category from scheme name
    """
    scheme_lower = scheme_name.lower()
    
    # Equity categories
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
    
    # Debt categories
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
    
    # Hybrid
    elif any(word in scheme_lower for word in ['hybrid', 'balanced', 'aggressive', 'conservative']):
        return 'Hybrid'
    
    # Default to equity if no match
    return 'Equity'


def import_cas_to_database(cas_data, user_id: int, db: Session) -> int:
    """
    Import CAS data into database
    
    Creates:
    - One Portfolio record per CAS import
    - Multiple Holding records (one per scheme)
    - Transaction records for each scheme
    
    Returns:
    - portfolio_id of created portfolio
    """
    
    # Create portfolio snapshot
    portfolio = Portfolio(
        user_id=user_id,
        name=f"CAS Import - {datetime.now().strftime('%b %Y')}",
        source="cas_pdf",
        upload_date=datetime.utcnow()
    )
    
    # Calculate portfolio totals
    total_invested = 0
    total_current = 0
    
    holdings_to_create = []
    
    for folio in cas_data.folios:
        for scheme in folio.schemes:
            # Skip schemes with zero units
            if not scheme.close or scheme.close == 0:
                continue
            
            # Extract valuation data
            if scheme.valuation:
                units = float(scheme.close)
                nav = float(scheme.valuation.nav)
                current_value = float(scheme.valuation.value)
                invested_amount = float(scheme.valuation.cost)
                
                total_invested += invested_amount
                total_current += current_value
                
                # Detect category
                category = detect_category(scheme.scheme)
                
                # Create holding
                holding = Holding(
                    fund_name=scheme.scheme,
                    isin=scheme.isin or '',
                    amfi_code=scheme.amfi or '',
                    folio_number=folio.folio,
                    units=units,
                    nav=nav,
                    invested_amount=invested_amount,
                    current_value=current_value,
                    category=category,
                    amc=folio.amc,
                    rta=scheme.rta or '',
                    fund_type=scheme.type or 'EQUITY'
                )
                
                holdings_to_create.append(holding)
    
    # Update portfolio totals
    portfolio.total_invested = round(total_invested, 2)
    portfolio.total_current = round(total_current, 2)
    portfolio.total_gain_loss = round(total_current - total_invested, 2)
    portfolio.total_return_pct = round(((total_current / total_invested - 1) * 100), 2) if total_invested > 0 else 0
    
    # Save to database
    db.add(portfolio)
    db.flush()  # Get portfolio ID
    
    # Associate holdings with portfolio
    for holding in holdings_to_create:
        holding.portfolio_id = portfolio.id
        db.add(holding)
    
    db.commit()
    db.refresh(portfolio)
    
    return portfolio.id


def import_cas_transactions(cas_data, portfolio_id: int, db: Session):
    """
    Import transaction history from CAS
    (Optional - for future XIRR calculations)
    """
    transactions_to_create = []
    
    for folio in cas_data.folios:
        for scheme in folio.schemes:
            for txn in scheme.transactions:
                # Skip non-purchase/redemption transactions
                if not txn.amount or not txn.units:
                    continue
                
                transaction = Transaction(
                    portfolio_id=portfolio_id,
                    fund_name=scheme.scheme,
                    folio_number=folio.folio,
                    transaction_date=txn.date,
                    transaction_type='PURCHASE' if txn.units > 0 else 'REDEMPTION',
                    amount=abs(float(txn.amount)),
                    units=abs(float(txn.units)),
                    nav=float(txn.nav) if txn.nav else 0,
                    description=txn.description
                )
                
                transactions_to_create.append(transaction)
    
    # Bulk insert transactions
    if transactions_to_create:
        db.bulk_save_objects(transactions_to_create)
        db.commit()
    
    return len(transactions_to_create)
