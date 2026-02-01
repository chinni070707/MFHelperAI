"""
XIRR calculation utilities
"""
from datetime import datetime
from typing import List, Tuple, Optional


def _xnpv(rate: float, cashflows: List[Tuple[datetime, float]]) -> float:
    """Calculate the net present value for a series of cashflows at given rate."""
    if rate <= -1.0:
        return float('inf')
    t0 = cashflows[0][0]
    total = 0.0
    for date, amount in cashflows:
        days = (date - t0).days
        total += amount / ((1 + rate) ** (days / 365.0))
    return total


def xirr(cashflows: List[Tuple[datetime, float]], guess: float = 0.1, tol: float = 1e-6, maxiter: int = 100) -> Optional[float]:
    """
    Compute XIRR (annualized) for given cashflows.
    `cashflows` should be a list of (date, amount) where amounts are signed (investments negative, returns positive).
    Returns annualized rate (e.g., 0.123 -> 12.3%) or None on failure.
    """
    if not cashflows:
        return None
    # Ensure sorted by date
    cashflows = sorted(cashflows, key=lambda x: x[0])

    # Bracket solution using secant / Newton-like method
    rate = guess
    for i in range(maxiter):
        # Compute function value and derivative approximation
        f = _xnpv(rate, cashflows)
        # Numerical derivative
        h = 1e-6 if abs(rate) < 1 else 1e-6 * abs(rate)
        f1 = _xnpv(rate + h, cashflows)
        deriv = (f1 - f) / h if h != 0 else 0

        if abs(f) < tol:
            return rate

        # If derivative is zero, use small step
        if deriv == 0:
            rate += 0.1
        else:
            rate -= f / deriv

        # Keep rate in reasonable bounds
        if rate < -0.999999:
            rate = -0.999999
    return None


def compute_xirr_from_transactions(transactions: List[Tuple[datetime, float]]) -> Optional[float]:
    """
    Helper: transactions is list of (date, signed_amount)
    Returns XIRR as percentage (float) or None
    """
    try:
        r = xirr(transactions)
        if r is None:
            return None
        return round(r * 100, 4)
    except Exception:
        return None
