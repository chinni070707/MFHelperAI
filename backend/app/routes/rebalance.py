"""
Rebalancing Routes - Portfolio rebalancing calculator
"""
from fastapi import APIRouter
from typing import List, Dict
import logging

from app.services.fund_classifier import FundClassifier

# Setup logger
logger = logging.getLogger(__name__)

router = APIRouter()

# Generic fund suggestions per category (used when user has no existing fund in bucket)
_GENERIC_SUGGESTIONS = {
    'Large Cap': ['Parag Parikh Flexi Cap', 'HDFC Flexi Cap Fund', 'UTI Flexi Cap Fund'],
    'Mid Cap': ['Motilal Oswal Midcap Fund', 'Kotak Emerging Equity Fund', 'HDFC Mid-Cap Opportunities'],
    'Small Cap': ['Nippon India Small Cap', 'Bandhan Small Cap Fund', 'Axis Small Cap Fund'],
}


def _generic_suggestions(cap: str) -> List[str]:
    return _GENERIC_SUGGESTIONS.get(cap, [])


def _cap_bucket_key(category: str) -> str:
    """Return 'large', 'mid', or 'small' for the given fund category."""
    large_cats = ['Large Cap', 'Flexi Cap', 'Multi Cap', 'Large & Mid', 'ELSS', 'Focused', 'Contra']
    mid_cats = ['Mid Cap']
    small_cats = ['Small Cap']
    if category in large_cats:
        return 'large'
    if category in mid_cats:
        return 'mid'
    if category in small_cats:
        return 'small'
    return 'large'  # default for equity


def _sell_priority_score(fund: dict, cap_bucket: str) -> float:
    """
    Score a fund for sell priority within a cap bucket. Higher = sell first.
    Factors:
      - Cap exposure: sell fund that IS most of the cap we want to reduce
      - Lower gain: minimises tax (tax-loss harvesting)
    """
    dist = FundClassifier.estimate_market_cap_distribution(fund.get('category', ''))
    cap_pct = dist.get(cap_bucket, 0)   # 0-1 scale (e.g. Flexi Cap large = 0.50)
    gain_pct = fund.get('gain_pct', 0)
    # Higher cap exposure + lower gains = higher sell priority
    return (cap_pct * 100) - (gain_pct * 0.5)


def _sell_reason(fund: dict, cap_pct: float, gain_pct: float) -> str:
    """Return a human-readable explanation for why this fund was chosen to sell."""
    cap_label = round(cap_pct * 100)
    if gain_pct < -1:
        return f"{cap_label}% cap exposure | Loss of {abs(gain_pct):.1f}% - tax harvesting opportunity"
    if gain_pct < 5:
        return f"{cap_label}% cap exposure | Low gain ({gain_pct:.1f}%) - minimal tax impact"
    return f"{cap_label}% cap exposure | Highest contributor to overweight in this bucket"


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

    large_cap_categories = ['Large Cap', 'Flexi Cap', 'Multi Cap', 'Large & Mid', 'ELSS', 'Focused', 'Contra']
    mid_cap_categories = ['Mid Cap']
    small_cap_categories = ['Small Cap']

    current_large = 0
    current_mid = 0
    current_small = 0
    other = 0

    large_funds: List[Dict] = []
    mid_funds: List[Dict] = []
    small_funds: List[Dict] = []

    for h in holdings:
        cat = h.get('category', 'Equity')
        current = float(h.get('current_value', 0))
        invested = float(h.get('invested', 0))
        gain = current - invested

        fund_info = {
            'name': h.get('fund_name', 'Unknown'),
            'category': cat,
            'amc': h.get('amc', ''),
            'current': current,
            'invested': invested,
            'nav': float(h.get('nav', 0)),
            'units': float(h.get('units', 0)),
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

    current_large_pct = current_large / total_equity * 100
    current_mid_pct = current_mid / total_equity * 100
    current_small_pct = current_small / total_equity * 100

    if mode == "fresh":
        result = calculate_fresh_investment(
            total_equity, current_large, current_mid, current_small,
            target_large, target_mid, target_small,
            large_funds, mid_funds, small_funds
        )
    else:
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


def calculate_fresh_investment(total, curr_large, curr_mid, curr_small,
                                tgt_large, tgt_mid, tgt_small,
                                large_funds, mid_funds, small_funds):
    """Calculate fresh investment needed to reach target allocation"""

    curr_large_pct = curr_large / total * 100
    curr_mid_pct = curr_mid / total * 100
    curr_small_pct = curr_small / total * 100

    large_gap = tgt_large - curr_large_pct
    mid_gap = tgt_mid - curr_mid_pct
    small_gap = tgt_small - curr_small_pct

    # Use the most overweight category as anchor (no fresh money there)
    if large_gap <= mid_gap and large_gap <= small_gap:
        new_total = (curr_large * 100 / tgt_large) if tgt_large > 0 else total
        total_fresh = max(0, new_total - total)
    elif mid_gap <= large_gap and mid_gap <= small_gap:
        new_total = (curr_mid * 100 / tgt_mid) if tgt_mid > 0 else total
        total_fresh = max(0, new_total - total)
    else:
        new_total = (curr_small * 100 / tgt_small) if tgt_small > 0 else total
        total_fresh = max(0, new_total - total)

    new_total = total + total_fresh
    fresh_large = max(0, (tgt_large / 100 * new_total) - curr_large)
    fresh_mid = max(0, (tgt_mid / 100 * new_total) - curr_mid)
    fresh_small = max(0, (tgt_small / 100 * new_total) - curr_small)

    buy_suggestions = generate_buy_suggestions(
        fresh_large, fresh_mid, fresh_small,
        large_funds, mid_funds, small_funds
    )

    return {
        "fresh_investment": {
            "large_cap": fresh_large,
            "mid_cap": fresh_mid,
            "small_cap": fresh_small,
            "total": total_fresh
        },
        "after_investment": {
            "large_cap_pct": (curr_large + fresh_large) / new_total * 100 if new_total > 0 else 0,
            "mid_cap_pct": (curr_mid + fresh_mid) / new_total * 100 if new_total > 0 else 0,
            "small_cap_pct": (curr_small + fresh_small) / new_total * 100 if new_total > 0 else 0,
            "total": new_total
        },
        "buy_suggestions": buy_suggestions,
        # Keep backward-compat field for any clients reading 'recommendations'
        "recommendations": [
            {"category": s["category"], "amount": s["amount"], "suggestions": s["generic_options"]}
            for s in buy_suggestions
        ]
    }


def calculate_rebalance_trades(total, curr_large, curr_mid, curr_small,
                                tgt_large, tgt_mid, tgt_small,
                                large_funds, mid_funds, small_funds):
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

    sell_orders = []
    tax_estimate = 0

    if sell_large > 0:
        sell_orders.extend(generate_sell_orders(large_funds, sell_large, 'Large Cap', 'large'))
    if sell_mid > 0:
        sell_orders.extend(generate_sell_orders(mid_funds, sell_mid, 'Mid Cap', 'mid'))
    if sell_small > 0:
        sell_orders.extend(generate_sell_orders(small_funds, sell_small, 'Small Cap', 'small'))

    for order in sell_orders:
        if order['gain'] > 0:
            tax_estimate += order['gain'] * 0.125

    # After selling, the proceeds go into underweight buckets
    buy_suggestions = generate_buy_suggestions(
        buy_large, buy_mid, buy_small,
        large_funds, mid_funds, small_funds
    )

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
        "buy_suggestions": buy_suggestions,
        "tax_estimate": tax_estimate,
        "note": "Tax calculated at 12.5% LTCG on gains. Actual may vary based on holding period."
    }


def generate_sell_orders(funds: List[Dict], amount_to_sell: float,
                         category: str, cap_bucket: str) -> List[Dict]:
    """
    Generate prioritised sell orders for a cap bucket.

    Sorting: highest cap exposure first, then lowest gain (tax-efficient).
    For each fund we also return:
      - sell_units: how many units to redeem
      - cap_exposure_pct: % of this fund that belongs to the target cap bucket
      - reason: plain-English explanation of the choice
      - is_full_exit: True when we suggest selling the entire holding
    """
    orders = []
    remaining = amount_to_sell

    # Sort by descending sell-priority score (most overweight + least taxed first)
    funds_sorted = sorted(funds, key=lambda f: -_sell_priority_score(f, cap_bucket))

    for fund in funds_sorted:
        if remaining <= 0:
            break

        sell_amount = min(remaining, fund['current'])
        sell_ratio = sell_amount / fund['current'] if fund['current'] > 0 else 0
        is_full_exit = (sell_amount >= fund['current'] * 0.99)  # within 1% = full exit

        # Units to sell (useful for broker entry)
        nav = fund.get('nav', 0)
        sell_units = round(sell_amount / nav, 3) if nav > 0 else None

        dist = FundClassifier.estimate_market_cap_distribution(fund.get('category', ''))
        cap_pct = dist.get(cap_bucket, 0)

        orders.append({
            'fund': fund['name'],
            'amc': fund.get('amc', ''),
            'category': category,
            'sell_amount': round(sell_amount, 2),
            'sell_units': sell_units,
            'gain': round(fund['gain'] * sell_ratio, 2),
            'gain_pct': round(fund['gain_pct'], 2),
            'cap_exposure_pct': round(cap_pct * 100),
            'is_full_exit': is_full_exit,
            'reason': _sell_reason(fund, cap_pct, fund['gain_pct'])
        })

        remaining -= sell_amount

    return orders


def generate_buy_suggestions(buy_large: float, buy_mid: float, buy_small: float,
                              large_funds: List[Dict], mid_funds: List[Dict],
                              small_funds: List[Dict]) -> List[Dict]:
    """
    Generate smart buy suggestions per cap bucket.

    Priority:
      1. Top up the existing fund the user ALREADY holds that is SMALLEST in that
         bucket (most underweight within the category).
      2. If user has no fund in that category, show generic options.

    Each suggestion also lists all existing funds in the bucket + generic options
    so the user can choose an alternative.
    """
    suggestions = []

    pairs = [
        ('Large Cap', buy_large, large_funds),
        ('Mid Cap', buy_mid, mid_funds),
        ('Small Cap', buy_small, small_funds),
    ]

    for cap_label, amount, existing_funds in pairs:
        if amount <= 0:
            continue

        if existing_funds:
            # Recommend topping up the smallest existing fund in this bucket
            sorted_funds = sorted(existing_funds, key=lambda f: f['current'])
            primary = sorted_funds[0]
            suggestions.append({
                'category': cap_label,
                'amount': round(amount, 2),
                'action': 'top_up',
                'fund': primary['name'],
                'amc': primary.get('amc', ''),
                'reason': f"Already in your portfolio - top up to increase {cap_label} exposure",
                'existing_options': [
                    {'name': f['name'], 'amc': f.get('amc', ''), 'current_value': round(f['current'], 2)}
                    for f in sorted_funds
                ],
                'generic_options': _generic_suggestions(cap_label)
            })
        else:
            suggestions.append({
                'category': cap_label,
                'amount': round(amount, 2),
                'action': 'new_fund',
                'fund': None,
                'amc': None,
                'reason': f"No existing {cap_label} fund in your portfolio - consider adding one",
                'existing_options': [],
                'generic_options': _generic_suggestions(cap_label)
            })

    return suggestions
