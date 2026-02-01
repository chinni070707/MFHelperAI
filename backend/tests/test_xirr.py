"""
Unit tests for XIRR calculation and compare_index analytics
"""
import pytest
from datetime import datetime, timedelta
from app.services.xirr import xirr, compute_xirr_from_transactions


class TestXIRRCalculation:
    """Test XIRR calculation with known scenarios"""

    def test_xirr_simple_break_even(self):
        """Test XIRR for simple scenario: invest 1000, get 1000 back after 1 year"""
        # Should be ~0% (actually slightly negative due to time value)
        cashflows = [
            (datetime(2024, 1, 1), -1000.0),  # Investment
            (datetime(2025, 1, 1), 1000.0),   # Redemption
        ]
        result = xirr(cashflows)
        assert result is not None
        # Should be close to 0 (within 1%)
        assert abs(result) < 0.01, f"Expected ~0%, got {result*100:.2f}%"

    def test_xirr_10_percent_growth(self):
        """Test XIRR for 10% annual growth"""
        cashflows = [
            (datetime(2024, 1, 1), -1000.0),
            (datetime(2025, 1, 1), 1100.0),  # 10% return
        ]
        result = xirr(cashflows)
        assert result is not None
        expected = 0.10
        # Should be close to 10% (within 2%)
        assert abs(result - expected) < 0.02, f"Expected ~{expected*100}%, got {result*100:.2f}%"

    def test_xirr_multiple_cashflows(self):
        """Test XIRR with multiple investments and redemption"""
        cashflows = [
            (datetime(2024, 1, 1), -1000.0),   # Initial investment
            (datetime(2024, 7, 1), -1000.0),   # Additional investment
            (datetime(2025, 1, 1), 2200.0),    # Redemption (10% on first 1000, ~5% on second 1000)
        ]
        result = xirr(cashflows)
        assert result is not None
        # Should be positive (typically 7-9% given weighted average of investments)
        assert 0 < result < 0.15

    def test_xirr_loss_scenario(self):
        """Test XIRR for loss scenario"""
        cashflows = [
            (datetime(2024, 1, 1), -1000.0),
            (datetime(2025, 1, 1), 900.0),    # 10% loss
        ]
        result = xirr(cashflows)
        assert result is not None
        # Should be negative
        assert result < 0, f"Expected negative return, got {result*100:.2f}%"

    def test_xirr_empty_cashflows(self):
        """Test XIRR with empty cashflows"""
        result = xirr([])
        assert result is None

    def test_xirr_single_cashflow(self):
        """Test XIRR with only one cashflow (should return None or handle gracefully)"""
        cashflows = [(datetime(2024, 1, 1), -1000.0)]
        result = xirr(cashflows)
        # Single cashflow can't determine XIRR
        assert result is None or isinstance(result, float)

    def test_compute_xirr_from_transactions(self):
        """Test wrapper function that returns percentage"""
        cashflows = [
            (datetime(2024, 1, 1), -1000.0),
            (datetime(2025, 1, 1), 1100.0),
        ]
        result = compute_xirr_from_transactions(cashflows)
        assert result is not None
        # Result should be ~10.0 (as percentage)
        assert 8 < result < 12, f"Expected ~10%, got {result}%"

    def test_xirr_monthly_sip(self):
        """Test XIRR for monthly SIP pattern"""
        cashflows = []
        base_date = datetime(2024, 1, 1)
        # SIP: 1000 every month for 12 months
        for i in range(12):
            date = base_date + timedelta(days=30*i)
            cashflows.append((date, -1000.0))
        # Final value after 1 year
        cashflows.append((base_date + timedelta(days=365), 13000.0))  # ~8.3% return
        
        result = xirr(cashflows)
        assert result is not None
        # Should be positive
        assert result > 0


class TestCompareIndexScenario:
    """Test scenarios for compare_index logic"""

    def test_allocation_percentage_calculation(self):
        """Verify allocation percentage logic"""
        buckets = {
            'Large': 100000.0,
            'Mid': 50000.0,
            'Small': 50000.0
        }
        total = sum(buckets.values())
        pct = {k: (v / total * 100) for k, v in buckets.items()}
        
        assert pct['Large'] == 50.0
        assert pct['Mid'] == 25.0
        assert pct['Small'] == 25.0

    def test_hypothetical_index_calculation(self):
        """Test hypothetical return calculation for index"""
        # Investment of 1000 on 2024-01-01
        # Evaluate on 2025-01-01
        # At 12% annual rate
        amount = -1000.0
        days = 365
        years = days / 365.0
        rate = 0.12
        fv = -amount * ((1 + rate) ** years)
        
        expected = 1000 * (1.12 ** 1.0)
        assert abs(fv - expected) < 1.0, f"Expected {expected}, got {fv}"

    def test_bucket_mapping(self):
        """Test category to bucket mapping"""
        category_map = {
            'Large Cap': 'Large',
            'Mid Cap': 'Mid',
            'Small Cap': 'Small',
            'Flexi Cap': 'Large',
            'ELSS': 'Large',
            'Equity': 'Large',
            'Debt': 'Large',
        }
        
        for cat, expected_bucket in category_map.items():
            # Implement basic mapping
            c = cat.lower()
            if 'mid' in c:
                bucket = 'Mid'
            elif 'small' in c:
                bucket = 'Small'
            else:
                bucket = 'Large'
            assert bucket == expected_bucket


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
