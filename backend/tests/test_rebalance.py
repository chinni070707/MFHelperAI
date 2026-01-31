"""
Unit tests for Rebalancing API endpoint
Tests rebalancing calculator with various scenarios
"""
import pytest


class TestRebalanceCalculation:
    """Test rebalancing calculation endpoint"""
    
    def test_fresh_money_rebalancing(self, client, sample_rebalance_request):
        """Test rebalancing with fresh money"""
        # API expects holdings as JSON body and targets/mode as query params
        holdings = sample_rebalance_request["holdings"]
        params = {
            "target_large": sample_rebalance_request["target_large"],
            "target_mid": sample_rebalance_request["target_mid"],
            "target_small": sample_rebalance_request["target_small"],
            "mode": sample_rebalance_request["mode"]
        }
        response = client.post("/api/rebalance/calculate", json=holdings, params=params)
        
        assert response.status_code == 200
        data = response.json()
        
        assert "mode" in data
        assert "current" in data
        assert "target" in data
        assert "recommendations" in data
        
        assert data["mode"] == "fresh"
    
    def test_sell_and_buy_rebalancing(self, client, sample_rebalance_request):
        """Test rebalancing with sell and buy mode"""
        holdings = sample_rebalance_request["holdings"]
        params = {
            "target_large": sample_rebalance_request["target_large"],
            "target_mid": sample_rebalance_request["target_mid"],
            "target_small": sample_rebalance_request["target_small"],
            "mode": "rebalance"  # Changed mode
        }
        
        response = client.post("/api/rebalance/calculate", json=holdings, params=params)
        
        assert response.status_code == 200
        data = response.json()
        assert data["mode"] == "rebalance"
    
    def test_custom_target_allocation(self, client):
        """Test rebalancing with custom target percentages"""
        holdings = [
            {"fund_name": "Large Cap Fund", "category": "Large Cap", "current_value": 100000, "invested": 90000},
            {"fund_name": "Mid Cap Fund", "category": "Mid Cap", "current_value": 50000, "invested": 45000}
        ]
        params = {
            "target_large": 70,
            "target_mid": 30,
            "target_small": 0,
            "mode": "fresh"
        }
        
        response = client.post("/api/rebalance/calculate", json=holdings, params=params)
        
        assert response.status_code == 200
        data = response.json()
        
        # Verify target allocation
        assert data["target"]["large_cap"] == 70
        assert data["target"]["mid_cap"] == 30
        assert data["target"]["small_cap"] == 0
    
    def test_balanced_portfolio_no_rebalancing_needed(self, client):
        """Test when portfolio is already balanced"""
        holdings = [
            {"fund_name": "Large Cap Fund", "category": "Large Cap", "current_value": 60000, "invested": 50000},
            {"fund_name": "Mid Cap Fund", "category": "Mid Cap", "current_value": 30000, "invested": 25000},
            {"fund_name": "Small Cap Fund", "category": "Small Cap", "current_value": 10000, "invested": 8000}
        ]
        params = {
            "target_large": 60,
            "target_mid": 30,
            "target_small": 10,
            "mode": "fresh"
        }
        
        response = client.post("/api/rebalance/calculate", json=holdings, params=params)
        
        assert response.status_code == 200
        data = response.json()
        
        # Current should match target (within tolerance)
        current_large = data["current"]["large_cap"]["pct"]
        assert current_large == pytest.approx(60.0, abs=1.0)


class TestRebalanceRecommendations:
    """Test rebalancing recommendations"""
    
    def test_recommendations_structure(self, client, sample_rebalance_request):
        """Test that recommendations have correct structure"""
        holdings = sample_rebalance_request["holdings"]
        params = {
            "target_large": sample_rebalance_request["target_large"],
            "target_mid": sample_rebalance_request["target_mid"],
            "target_small": sample_rebalance_request["target_small"],
            "mode": sample_rebalance_request["mode"]
        }
        response = client.post("/api/rebalance/calculate", json=holdings, params=params)
        data = response.json()
        
        recommendations = data["recommendations"]
        
        for rec in recommendations:
            assert "category" in rec
            assert "amount" in rec or "suggestions" in rec
    
    def test_fresh_money_recommendations(self, client):
        """Test recommendations for fresh money mode"""
        holdings = [
            {"fund_name": "Large Cap Fund", "category": "Large Cap", "current_value": 100000, "invested": 90000}
        ]
        params = {
            "target_large": 40,
            "target_mid": 30,
            "target_small": 30,
            "mode": "fresh"
        }
        
        response = client.post("/api/rebalance/calculate", json=holdings, params=params)
        data = response.json()
        
        # Should recommend investing in mid and small cap
        recommendations = data["recommendations"]
        categories_to_invest = [rec["category"] for rec in recommendations if rec.get("amount", 0) > 0]
        
        assert "Mid Cap" in categories_to_invest
        assert "Small Cap" in categories_to_invest
    
    def test_rebalance_mode_recommendations(self, client):
        """Test recommendations for sell/buy rebalancing"""
        holdings = [
            {"fund_name": "Large Cap Fund", "category": "Large Cap", "current_value": 150000, "invested": 100000},
            {"fund_name": "Small Cap Fund", "category": "Small Cap", "current_value": 50000, "invested": 40000}
        ]
        params = {
            "target_large": 40,
            "target_mid": 30,
            "target_small": 30,
            "mode": "rebalance"
        }
        
        response = client.post("/api/rebalance/calculate", json=holdings, params=params)
        data = response.json()
        
        # Rebalance mode returns sell/buy orders, not recommendations
        assert "sell" in data or "sell_orders" in data
        assert len(data) > 0


class TestRebalanceEdgeCases:
    """Test edge cases for rebalancing"""
    
    def test_single_fund_portfolio(self, client):
        """Test rebalancing with single fund"""
        holdings = [
            {"fund_name": "Only Fund", "category": "Large Cap", "current_value": 100000, "invested": 90000}
        ]
        params = {
            "target_large": 40,
            "target_mid": 30,
            "target_small": 30,
            "mode": "fresh"
        }
        
        response = client.post("/api/rebalance/calculate", json=holdings, params=params)
        
        assert response.status_code == 200
        data = response.json()
        
        # Should show that portfolio is 100% large cap currently
        assert data["current"]["large_cap"]["pct"] == 100.0
    
    def test_empty_portfolio(self, client):
        """Test rebalancing with empty portfolio"""
        holdings = []
        params = {
            "target_large": 40,
            "target_mid": 30,
            "target_small": 30,
            "mode": "fresh"
        }
        
        response = client.post("/api/rebalance/calculate", json=holdings, params=params)
        
        # Should handle gracefully
        assert response.status_code == 200
    
    def test_invalid_target_percentages(self, client):
        """Test with invalid target percentages (not summing to 100)"""
        holdings = [
            {"fund_name": "Fund A", "category": "Large Cap", "current_value": 100000, "invested": 90000}
        ]
        params = {
            "target_large": 50,
            "target_mid": 50,
            "target_small": 50,  # Total = 150%
            "mode": "fresh"
        }
        
        response = client.post("/api/rebalance/calculate", json=holdings, params=params)
        
        # Should still process (might normalize or show warning)
        assert response.status_code in [200, 400]
    
    def test_zero_current_value(self, client):
        """Test with fund having zero current value"""
        holdings = [
            {"fund_name": "Fund A", "category": "Large Cap", "current_value": 0, "invested": 10000}
        ]
        params = {
            "target_large": 100,
            "target_mid": 0,
            "target_small": 0,
            "mode": "fresh"
        }
        
        response = client.post("/api/rebalance/calculate", json=holdings, params=params)
        assert response.status_code == 200
    
    def test_negative_target_percentages(self, client):
        """Test with negative target percentages"""
        holdings = [
            {"fund_name": "Fund A", "category": "Large Cap", "current_value": 100000, "invested": 90000}
        ]
        params = {
            "target_large": -10,
            "target_mid": 60,
            "target_small": 50,
            "mode": "fresh"
        }
        
        response = client.post("/api/rebalance/calculate", json=holdings, params=params)
        
        # Should reject or handle gracefully
        assert response.status_code in [200, 400]


class TestRebalanceCalculations:
    """Test mathematical accuracy of rebalancing calculations"""
    
    def test_allocation_percentage_accuracy(self, client):
        """Test that allocation percentages are calculated accurately"""
        holdings = [
            {"fund_name": "Fund A", "category": "Large Cap", "current_value": 100000, "invested": 90000},
            {"fund_name": "Fund B", "category": "Mid Cap", "current_value": 50000, "invested": 45000},
            {"fund_name": "Fund C", "category": "Small Cap", "current_value": 25000, "invested": 20000}
        ]
        params = {
            "target_large": 40,
            "target_mid": 30,
            "target_small": 30,
            "mode": "fresh"
        }
        
        response = client.post("/api/rebalance/calculate", json=holdings, params=params)
        data = response.json()
        
        current = data["current"]
        
        # Total is 175000
        # Large Cap: 100000 / 175000 = 57.14%
        # Mid Cap: 50000 / 175000 = 28.57%
        # Small Cap: 25000 / 175000 = 14.29%
        
        assert current["large_cap"]["pct"] == pytest.approx(57.14, abs=0.1)
        assert current["mid_cap"]["pct"] == pytest.approx(28.57, abs=0.1)
        assert current["small_cap"]["pct"] == pytest.approx(14.29, abs=0.1)
    
    def test_total_value_consistency(self, client):
        """Test that total values are consistent across calculations"""
        holdings = [
            {"fund_name": "Fund A", "category": "Large Cap", "current_value": 100000, "invested": 90000},
            {"fund_name": "Fund B", "category": "Mid Cap", "current_value": 50000, "invested": 45000}
        ]
        params = {
            "target_large": 50,
            "target_mid": 50,
            "target_small": 0,
            "mode": "fresh"
        }
        
        response = client.post("/api/rebalance/calculate", json=holdings, params=params)
        data = response.json()
        
        # Verify total value
        current_total = sum(cat["value"] for key, cat in data["current"].items() if isinstance(cat, dict) and "value" in cat)
        expected_total = 150000
        
        assert current_total == pytest.approx(expected_total, rel=1e-2)


# Integration tests
class TestRebalanceWorkflow:
    """Test complete rebalancing workflow"""
    
    def test_analyze_and_rebalance_workflow(self, client, sample_excel_data):
        """Test workflow: get portfolio -> calculate rebalancing"""
        # 1. Save portfolio
        client.post("/api/portfolio/save", json=sample_excel_data)
        
        # 2. Get holdings
        get_response = client.get("/api/portfolio/holdings")
        holdings = get_response.json()
        
        # 3. Calculate rebalancing
        params = {
            "target_large": 50,
            "target_mid": 30,
            "target_small": 20,
            "mode": "fresh"
        }
        
        rebalance_response = client.post("/api/rebalance/calculate", json=holdings, params=params)
        
        assert rebalance_response.status_code == 200
        assert "recommendations" in rebalance_response.json()
