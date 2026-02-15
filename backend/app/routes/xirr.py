"""
XIRR Routes - calculate portfolio and holding XIRR
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.utils.auth import get_current_user
from app.models.models import Portfolio, Holding, Transaction
from app.services.xirr import compute_xirr_from_transactions

router = APIRouter(prefix="/api/analytics", tags=["Analytics"])


@router.get("/xirr/{portfolio_id}")
async def get_portfolio_xirr(portfolio_id: int, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    """Compute XIRR for a portfolio and its holdings"""
    # Verify portfolio ownership
    portfolio = db.query(Portfolio).filter(Portfolio.id == portfolio_id, Portfolio.user_id == current_user.id).first()
    if not portfolio:
        raise HTTPException(status_code=404, detail="Portfolio not found")

    # Fetch holdings — always filter by user_id as defense-in-depth
    holdings = db.query(Holding).filter(
        Holding.portfolio_id == portfolio_id,
        Holding.user_id == current_user.id
    ).all()
    holding_ids = [h.id for h in holdings]

    # Fetch transactions for these holdings
    transactions = db.query(Transaction).filter(Transaction.holding_id.in_(holding_ids)).order_by(Transaction.transaction_date).all()

    # Build cashflows for portfolio
    portfolio_cashflows = []
    holding_cashflows_map = {h.id: [] for h in holdings}

    for txn in transactions:
        # Determine sign: purchases/SIP are negative (cash out), redemptions positive
        ttype = (txn.transaction_type or '').lower()
        sign = 1.0
        if any(x in ttype for x in ['purchase', 'sip', 'purchase-bse', 'new purchase']):
            sign = -1.0
        elif any(x in ttype for x in ['redemption', 'sell', 'switch']):
            sign = 1.0
        else:
            # default: if amount is negative in DB keep sign, else treat purchases as negative
            sign = -1.0 if txn.amount > 0 else 1.0

        amt = sign * float(txn.amount)
        date = txn.transaction_date
        portfolio_cashflows.append((date, amt))
        if txn.holding_id in holding_cashflows_map:
            holding_cashflows_map[txn.holding_id].append((date, amt))

    # Compute portfolio XIRR
    portfolio_xirr = compute_xirr_from_transactions(portfolio_cashflows) if portfolio_cashflows else None

    # Compute per-holding XIRR
    holding_results = []
    for h in holdings:
        cf = holding_cashflows_map.get(h.id, [])
        hx = compute_xirr_from_transactions(cf) if cf else None
        holding_results.append({
            "holding_id": h.id,
            "fund_name": h.fund_name,
            "xirr_pct": hx
        })

    return {
        "portfolio_id": portfolio_id,
        "portfolio_xirr_pct": portfolio_xirr,
        "holdings": holding_results
    }
