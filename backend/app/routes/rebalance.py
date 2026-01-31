"""
Rebalancing Routes - Portfolio rebalancing calculator
"""
from fastapi import APIRouter
from typing import List, Dict
import logging

# Setup logger
logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/calculate")
async def calculate_rebalance(
    holdings: List[Dict],
    target_large: float = 40,
    target_mid: float = 30,
    target_small: float = 30,
    mode: str = "fresh"  # "fresh" or "rebalance"
):
    """
    Calculate rebalancing requirements
    
    Args:
        holdings: List of fund holdings
        target_large: Target % for large cap (includes flexi, multi, ELSS)
        target_mid: Target % for mid cap
        target_small: Target % for small cap
        mode: "fresh" = add fresh money, "rebalance" = sell and buy
    """
    logger.info(f"Calculating rebalance for {len(holdings)} holdings")
    logger.debug(f"Targets: Large={target_large}%, Mid={target_mid}%, Small={target_small}%, Mode={mode}")
    
    # Categorize holdings into market cap buckets
    large_cap_categories = ['Large Cap', 'Flexi Cap', 'Multi Cap', 'Large & Mid', 'ELSS', 'Focused', 'Contra']
    mid_cap_categories = ['Mid Cap']
    small_cap_categories = ['Small Cap']
    
    current_large = 0
    current_mid = 0
    current_small = 0
    other = 0
    
    large_funds = []
    mid_funds = []
    small_funds = []
    
    for h in holdings:
        cat = h.get('category', 'Equity')
        current = float(h.get('current_value', 0))
        invested = float(h.get('invested', 0))
        gain = current - invested
        
        fund_info = {
            'name': h.get('fund_name', 'Unknown'),
            'current': current,
            'invested': invested,
            'gain': gain,
            'gain_pct': (gain / invested * 100) if invested > 0 else 0
        }
        
        if cat in large_cap_categories:
            current_large += current
            large_funds.append(fund_info)
        elif cat in mid_cap_categories:
            current_mid += current
            mid_funds.append(fund_info)
        elif cat in small_cap_categories:
            current_small += current
            small_funds.append(fund_info)
        else:
            other += current
    
    total_equity = current_large + current_mid + current_small
    
    if total_equity == 0:
        return {"error": "No equity holdings found"}
    
    # Current allocation percentages
    current_large_pct = current_large / total_equity * 100
    current_mid_pct = current_mid / total_equity * 100
    current_small_pct = current_small / total_equity * 100
    
    # Calculate what's needed to reach target
    if mode == "fresh":
        # Fresh money mode - calculate how much to add
        result = calculate_fresh_investment(
            total_equity, current_large, current_mid, current_small,
            target_large, target_mid, target_small
        )
    else:
        # Rebalance mode - calculate what to sell and buy
        result = calculate_rebalance_trades(
            total_equity, current_large, current_mid, current_small,
            target_large, target_mid, target_small,
            large_funds, mid_funds, small_funds
        )
    
    return {
        "current": {
            "large_cap": {"value": current_large, "pct": current_large_pct},
            "mid_cap": {"value": current_mid, "pct": current_mid_pct},
            "small_cap": {"value": current_small, "pct": current_small_pct},
            "other": other,
            "total_equity": total_equity
        },
        "target": {
            "large_cap": target_large,
            "mid_cap": target_mid,
            "small_cap": target_small
        },
        "mode": mode,
        **result
    }


def calculate_fresh_investment(total, curr_large, curr_mid, curr_small, tgt_large, tgt_mid, tgt_small):
    """Calculate fresh investment needed to reach target allocation"""
    
    # Find the category that needs least fresh investment (or none)
    # That becomes our "anchor" category
    
    # If current % > target %, we don't add to that category (it will dilute)
    curr_large_pct = curr_large / total * 100
    curr_mid_pct = curr_mid / total * 100
    curr_small_pct = curr_small / total * 100
    
    # Calculate fresh money needed for each category to reach target
    # Formula: (current + fresh) / (total + total_fresh) = target%
    
    # Start with the most underweight category
    large_gap = tgt_large - curr_large_pct
    mid_gap = tgt_mid - curr_mid_pct
    small_gap = tgt_small - curr_small_pct
    
    # Use the most overweight category as anchor (no fresh money there)
    if large_gap <= mid_gap and large_gap <= small_gap:
        # Large cap is most overweight, calculate based on it
        # Target: curr_large / (total + X) = tgt_large/100
        # X = (curr_large * 100 / tgt_large) - total
        if tgt_large > 0:
            new_total = curr_large * 100 / tgt_large
            total_fresh = new_total - total
        else:
            total_fresh = 0
        fresh_large = 0
    elif mid_gap <= large_gap and mid_gap <= small_gap:
        if tgt_mid > 0:
            new_total = curr_mid * 100 / tgt_mid
            total_fresh = new_total - total
        else:
            total_fresh = 0
        fresh_mid = 0
    else:
        if tgt_small > 0:
            new_total = curr_small * 100 / tgt_small
            total_fresh = new_total - total
        else:
            total_fresh = 0
        fresh_small = 0
    
    total_fresh = max(0, total_fresh)
    new_total = total + total_fresh
    
    # Calculate fresh for each category
    fresh_large = max(0, (tgt_large / 100 * new_total) - curr_large)
    fresh_mid = max(0, (tgt_mid / 100 * new_total) - curr_mid)
    fresh_small = max(0, (tgt_small / 100 * new_total) - curr_small)
    
    return {
        "fresh_investment": {
            "large_cap": fresh_large,
            "mid_cap": fresh_mid,
            "small_cap": fresh_small,
            "total": total_fresh
        },
        "after_investment": {
            "large_cap_pct": (curr_large + fresh_large) / (total + total_fresh) * 100 if total_fresh > 0 else curr_large / total * 100,
            "mid_cap_pct": (curr_mid + fresh_mid) / (total + total_fresh) * 100 if total_fresh > 0 else curr_mid / total * 100,
            "small_cap_pct": (curr_small + fresh_small) / (total + total_fresh) * 100 if total_fresh > 0 else curr_small / total * 100,
            "total": total + total_fresh
        },
        "recommendations": generate_fresh_recommendations(fresh_large, fresh_mid, fresh_small)
    }


def calculate_rebalance_trades(total, curr_large, curr_mid, curr_small, tgt_large, tgt_mid, tgt_small, large_funds, mid_funds, small_funds):
    """Calculate sell and buy trades for rebalancing"""
    
    target_large = total * tgt_large / 100
    target_mid = total * tgt_mid / 100
    target_small = total * tgt_small / 100
    
    sell_large = max(0, curr_large - target_large)
    sell_mid = max(0, curr_mid - target_mid)
    sell_small = max(0, curr_small - target_small)
    
    buy_large = max(0, target_large - curr_large)
    buy_mid = max(0, target_mid - curr_mid)
    buy_small = max(0, target_small - curr_small)
    
    # Calculate tax implications (sell funds with losses first for tax harvesting)
    sell_orders = []
    tax_estimate = 0
    
    if sell_large > 0:
        sell_orders.extend(generate_sell_orders(large_funds, sell_large, 'Large Cap'))
    if sell_mid > 0:
        sell_orders.extend(generate_sell_orders(mid_funds, sell_mid, 'Mid Cap'))
    if sell_small > 0:
        sell_orders.extend(generate_sell_orders(small_funds, sell_small, 'Small Cap'))
    
    # Calculate tax on gains
    for order in sell_orders:
        if order['gain'] > 0:
            # LTCG @ 12.5% on gains above 1.25L (simplified)
            taxable_gain = order['gain']
            tax_estimate += taxable_gain * 0.125
    
    return {
        "sell": {
            "large_cap": sell_large,
            "mid_cap": sell_mid,
            "small_cap": sell_small,
            "total": sell_large + sell_mid + sell_small
        },
        "buy": {
            "large_cap": buy_large,
            "mid_cap": buy_mid,
            "small_cap": buy_small,
            "total": buy_large + buy_mid + buy_small
        },
        "sell_orders": sell_orders,
        "tax_estimate": tax_estimate,
        "note": "Tax calculated at 12.5% LTCG on gains. Actual may vary based on holding period."
    }


def generate_sell_orders(funds, amount_to_sell, category):
    """Generate sell orders, prioritizing funds in loss for tax harvesting"""
    orders = []
    remaining = amount_to_sell
    
    # Sort by gain (sell loss-making funds first)
    funds_sorted = sorted(funds, key=lambda x: x['gain'])
    
    for fund in funds_sorted:
        if remaining <= 0:
            break
        
        sell_amount = min(remaining, fund['current'])
        sell_ratio = sell_amount / fund['current'] if fund['current'] > 0 else 0
        
        orders.append({
            'fund': fund['name'],
            'category': category,
            'sell_amount': sell_amount,
            'gain': fund['gain'] * sell_ratio,
            'gain_pct': fund['gain_pct']
        })
        
        remaining -= sell_amount
    
    return orders


def generate_fresh_recommendations(fresh_large, fresh_mid, fresh_small):
    """Generate fund recommendations for fresh investment"""
    recommendations = []
    
    if fresh_mid > 0:
        recommendations.append({
            'category': 'Mid Cap',
            'amount': fresh_mid,
            'suggestions': [
                'Motilal Oswal Midcap Fund',
                'Kotak Emerging Equity Fund',
                'HDFC Mid-Cap Opportunities'
            ]
        })
    
    if fresh_small > 0:
        recommendations.append({
            'category': 'Small Cap',
            'amount': fresh_small,
            'suggestions': [
                'Nippon India Small Cap',
                'Bandhan Small Cap Fund',
                'Axis Small Cap Fund'
            ]
        })
    
    if fresh_large > 0:
        recommendations.append({
            'category': 'Large Cap',
            'amount': fresh_large,
            'suggestions': [
                'Parag Parikh Flexi Cap',
                'HDFC Flexi Cap Fund',
                'UTI Flexi Cap Fund'
            ]
        })
    
    return recommendations
