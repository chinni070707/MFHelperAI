"""
Analytics Routes - Portfolio analytics and insights
"""
from fastapi import APIRouter
from typing import List, Dict
import logging

# Setup logger
logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/allocation")
async def get_allocation(holdings: List[Dict]):
    """Calculate allocation by category, AMC, and style"""
    logger.info(f"Calculating allocation for {len(holdings)} holdings")
    
    category_totals = {}
    amc_totals = {}
    style_totals = {}
    
    for holding in holdings:
        current = float(holding.get('current_value', 0))
        category = holding.get('category', 'Other')
        amc = holding.get('amc', 'Other')
        style = holding.get('style', 'Blend')
        
        category_totals[category] = category_totals.get(category, 0) + current
        amc_totals[amc] = amc_totals.get(amc, 0) + current
        style_totals[style] = style_totals.get(style, 0) + current
    
    total = sum(category_totals.values())
    
    return {
        "by_category": {k: {"value": v, "pct": v/total*100 if total > 0 else 0} for k, v in category_totals.items()},
        "by_amc": {k: {"value": v, "pct": v/total*100 if total > 0 else 0} for k, v in amc_totals.items()},
        "by_style": {k: {"value": v, "pct": v/total*100 if total > 0 else 0} for k, v in style_totals.items()},
        "total_value": total
    }


@router.post("/market-cap")
async def get_market_cap_allocation(holdings: List[Dict]):
    """Calculate allocation by market cap"""
    
    # Map categories to market cap
    market_cap_map = {
        'Large Cap': 'Large Cap',
        'Large & Mid': 'Large Cap',
        'Flexi Cap': 'Large Cap',
        'Multi Cap': 'Multi Cap',
        'ELSS': 'Large Cap',
        'Focused': 'Large Cap',
        'Mid Cap': 'Mid Cap',
        'Small Cap': 'Small Cap',
        'International': 'International',
        'Sectoral': 'Sectoral',
        'Contra': 'Large Cap',
        'Liquid': 'Debt/Liquid',
        'Debt': 'Debt/Liquid',
        'Hybrid': 'Hybrid'
    }
    
    market_cap_totals = {}
    
    for holding in holdings:
        current = float(holding.get('current_value', 0))
        category = holding.get('category', 'Equity')
        mapped = market_cap_map.get(category, 'Other')
        market_cap_totals[mapped] = market_cap_totals.get(mapped, 0) + current
    
    total = sum(market_cap_totals.values())
    
    return {
        "allocation": {k: {"value": v, "pct": v/total*100 if total > 0 else 0} for k, v in market_cap_totals.items()},
        "total": total
    }


@router.post("/performance")
async def get_performance(holdings: List[Dict]):
    """Calculate performance metrics"""
    
    performance = []
    
    for holding in holdings:
        invested = float(holding.get('invested', 0))
        current = float(holding.get('current_value', 0))
        gain = current - invested
        return_pct = (gain / invested * 100) if invested > 0 else 0
        
        performance.append({
            "fund_name": holding.get('fund_name', 'Unknown'),
            "invested": invested,
            "current": current,
            "gain": gain,
            "return_pct": round(return_pct, 2),
            "return_1y": holding.get('return_1y', '-'),
            "return_3y": holding.get('return_3y', '-'),
            "alpha": holding.get('alpha', '-')
        })
    
    # Sort by returns
    performance.sort(key=lambda x: x['return_pct'], reverse=True)
    
    # Find best and worst performers
    return {
        "holdings": performance,
        "best_performer": performance[0] if performance else None,
        "worst_performer": performance[-1] if performance else None,
        "profitable_count": len([p for p in performance if p['gain'] > 0]),
        "loss_count": len([p for p in performance if p['gain'] < 0])
    }


@router.post("/insights")
async def get_insights(holdings: List[Dict]):
    """Generate portfolio insights and recommendations"""
    
    insights = []
    
    # Calculate totals
    total_invested = sum(float(h.get('invested', 0)) for h in holdings)
    total_current = sum(float(h.get('current_value', 0)) for h in holdings)
    total_gain = total_current - total_invested
    
    # Insight 1: Overall performance
    if total_gain > 0:
        insights.append({
            "type": "positive",
            "title": "Portfolio in Profit",
            "message": f"Your portfolio is up ₹{total_gain/100000:.2f}L ({total_gain/total_invested*100:.1f}%)"
        })
    else:
        insights.append({
            "type": "warning",
            "title": "Portfolio in Loss",
            "message": f"Your portfolio is down ₹{abs(total_gain)/100000:.2f}L ({total_gain/total_invested*100:.1f}%)"
        })
    
    # Insight 2: Concentration risk
    for holding in holdings:
        weight = float(holding.get('current_value', 0)) / total_current * 100 if total_current > 0 else 0
        if weight > 25:
            insights.append({
                "type": "warning",
                "title": "Concentration Risk",
                "message": f"{holding.get('fund_name', 'A fund')} is {weight:.1f}% of portfolio. Consider diversifying."
            })
    
    # Insight 3: Check for duplicate categories
    categories = [h.get('category') for h in holdings]
    for cat in set(categories):
        count = categories.count(cat)
        if count > 3:
            insights.append({
                "type": "info",
                "title": "Multiple Funds in Same Category",
                "message": f"You have {count} {cat} funds. Consider consolidating for easier management."
            })
    
    # Insight 4: Check for small allocations
    for holding in holdings:
        current = float(holding.get('current_value', 0))
        if 0 < current < 50000:
            insights.append({
                "type": "info",
                "title": "Small Allocation",
                "message": f"{holding.get('fund_name', 'A fund')} has only ₹{current/1000:.0f}K. Consider increasing or consolidating."
            })
    
    return {
        "insights": insights,
        "summary": {
            "total_invested": total_invested,
            "total_current": total_current,
            "total_gain": total_gain,
            "return_pct": (total_gain / total_invested * 100) if total_invested > 0 else 0,
            "fund_count": len(holdings)
        }
    }


@router.get('/compare_index/{portfolio_id}')
async def compare_index(portfolio_id: int, large_rate: float = 0.12, mid_rate: float = 0.14, small_rate: float = 0.16, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    """Compare portfolio to index returns for large/mid/small cap.

    Returns allocation percentages and hypothetical returns if the same transactions were invested into index funds with given annual rates.
    Rates are expected as decimals (e.g., 0.12 for 12%).
    """
    # Verify portfolio ownership
    portfolio = db.query(Portfolio).filter(Portfolio.id == portfolio_id, Portfolio.user_id == current_user.id).first()
    if not portfolio:
        raise HTTPException(status_code=404, detail="Portfolio not found")

    # Fetch holdings and transactions
    holdings = db.query(Holding).filter(Holding.portfolio_id == portfolio_id).all()
    holding_ids = [h.id for h in holdings]
    transactions = db.query(Transaction).filter(Transaction.holding_id.in_(holding_ids)).order_by(Transaction.transaction_date).all()

    # Map categories to index bucket
    def map_bucket(cat: str):
        if not cat:
            return 'Large'
        c = cat.lower()
        if 'mid' in c:
            return 'Mid'
        if 'small' in c:
            return 'Small'
        return 'Large'

    # Sum actual current values per bucket
    bucket_actual = {'Large': 0.0, 'Mid': 0.0, 'Small': 0.0}
    total_current = 0.0
    for h in holdings:
        b = map_bucket(h.category)
        cur = float(h.current_value or 0)
        bucket_actual[b] += cur
        total_current += cur

    allocation_pct = {k: (v / total_current * 100) if total_current > 0 else 0 for k, v in bucket_actual.items()}

    # Compute hypothetical current value if each transaction was invested into corresponding index
    eval_date = portfolio.snapshot_date or func.now()
    from datetime import datetime
    if isinstance(eval_date, datetime):
        ref_date = eval_date
    else:
        ref_date = datetime.utcnow()

    # rates map
    rates = {'Large': float(large_rate), 'Mid': float(mid_rate), 'Small': float(small_rate)}

    bucket_hypo = {'Large': 0.0, 'Mid': 0.0, 'Small': 0.0}

    for txn in transactions:
        b = None
        # find holding category
        h = next((x for x in holdings if x.id == txn.holding_id), None)
        if h:
            b = map_bucket(h.category)
        else:
            b = 'Large'

        # Determine sign similar to XIRR
        ttype = (txn.transaction_type or '').lower()
        sign = 1.0
        if any(x in ttype for x in ['purchase', 'sip', 'purchase-bse', 'new purchase']):
            sign = -1.0
        elif any(x in ttype for x in ['redemption', 'sell', 'switch']):
            sign = 1.0
        else:
            sign = -1.0 if txn.amount > 0 else 1.0

        amt = sign * float(txn.amount)
        days = (ref_date - txn.transaction_date).days
        years = days / 365.0 if days >= 0 else 0
        r = rates.get(b, 0.12)
        # Future value contribution at eval date: -amt * (1+r)^years (so investments become positive)
        fv = -amt * ((1 + r) ** years)
        bucket_hypo[b] += fv

    total_hypo = sum(bucket_hypo.values())

    return {
        'portfolio_id': portfolio_id,
        'allocation_pct': allocation_pct,
        'actual_by_bucket': bucket_actual,
        'hypothetical_by_bucket': bucket_hypo,
        'hypothetical_total': total_hypo
    }
