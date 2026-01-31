"""
Analytics Routes - Portfolio analytics and insights
"""
from fastapi import APIRouter
from typing import List, Dict

router = APIRouter()


@router.post("/allocation")
async def get_allocation(holdings: List[Dict]):
    """Calculate allocation by category, AMC, and style"""
    
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
