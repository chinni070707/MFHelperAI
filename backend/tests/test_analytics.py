"""
Unit tests for Analytics API endpoints
Tests allocation, market cap, and performance calculations
"""
import pytest


class TestAllocation:
    """Test allocation calculation endpoint"""
    
    def test_calculate_allocation(self, client, sample_excel_data):
        """Test basic allocation calculation"""
        holdings = sample_excel_data["holdings"]
        
        response = client.post("/api/analytics/allocation", json=holdings)
        
        assert response.status_code == 200
        data = response.json()
        
        assert "by_category" in data
        assert "by_amc" in data
        assert "by_style" in data
        assert "total_value" in data
    
    def test_allocation_percentages(self, client, sample_excel_data):
        """Test that allocation percentages sum to 100%"""
        holdings = sample_excel_data["holdings"]
        
        response = client.post("/api/analytics/allocation", json=holdings)
        data = response.json()
        
        # Check category percentages
        category_total = sum(v["pct"] for v in data["by_category"].values())
        assert category_total == pytest.approx(100.0, rel=1e-2)
        
        # Check AMC percentages
        amc_total = sum(v["pct"] for v in data["by_amc"].values())
        assert amc_total == pytest.approx(100.0, rel=1e-2)
    
    def test_allocation_with_empty_holdings(self, client):
        """Test allocation with empty holdings list"""
        response = client.post("/api/analytics/allocation", json=[])
        
        assert response.status_code == 200
        data = response.json()
        assert data["total_value"] == 0
    
    def test_allocation_by_category(self, client):
        """Test allocation categorization"""
        holdings = [
            {"fund_name": "Fund A", "category": "Large Cap", "current_value": 100000, "amc": "HDFC", "style": "Growth"},
            {"fund_name": "Fund B", "category": "Large Cap", "current_value": 50000, "amc": "ICICI", "style": "Value"},
            {"fund_name": "Fund C", "category": "Mid Cap", "current_value": 50000, "amc": "HDFC", "style": "Growth"}
        ]
        
        response = client.post("/api/analytics/allocation", json=holdings)
        data = response.json()
        
        # Verify Large Cap is 75% (150k out of 200k)
        large_cap_pct = data["by_category"]["Large Cap"]["pct"]
        assert large_cap_pct == pytest.approx(75.0, rel=1e-2)
        
        # Verify Mid Cap is 25%
        mid_cap_pct = data["by_category"]["Mid Cap"]["pct"]
        assert mid_cap_pct == pytest.approx(25.0, rel=1e-2)


class TestMarketCapAllocation:
    """Test market cap allocation endpoint"""
    
    def test_market_cap_calculation(self, client, sample_excel_data):
        """Test market cap allocation calculation"""
        holdings = sample_excel_data["holdings"]
        
        response = client.post("/api/analytics/market-cap", json=holdings)
        
        assert response.status_code == 200
        data = response.json()
        
        assert "allocation" in data
        assert "total" in data
        assert data["total"] > 0
    
    def test_market_cap_mapping(self, client):
        """Test that categories are correctly mapped to market cap"""
        holdings = [
            {"fund_name": "Fund A", "category": "Large Cap", "current_value": 100000},
            {"fund_name": "Fund B", "category": "Mid Cap", "current_value": 50000},
            {"fund_name": "Fund C", "category": "Small Cap", "current_value": 25000},
            {"fund_name": "Fund D", "category": "International", "current_value": 25000}
        ]
        
        response = client.post("/api/analytics/market-cap", json=holdings)
        data = response.json()
        
        allocation = data["allocation"]
        
        # Verify all categories are present
        assert "Large Cap" in allocation
        assert "Mid Cap" in allocation
        assert "Small Cap" in allocation
        assert "International" in allocation
    
    def test_market_cap_with_flexi_cap(self, client):
        """Test that Flexi Cap is mapped to Large Cap"""
        holdings = [
            {"fund_name": "Fund A", "category": "Flexi Cap", "current_value": 100000},
            {"fund_name": "Fund B", "category": "Large Cap", "current_value": 100000}
        ]
        
        response = client.post("/api/analytics/market-cap", json=holdings)
        data = response.json()
        
        # Both should be counted as Large Cap
        large_cap_value = data["allocation"]["Large Cap"]["value"]
        assert large_cap_value == 200000


class TestPerformance:
    """Test performance calculation endpoint"""
    
    def test_performance_calculation(self, client, sample_excel_data):
        """Test performance metrics calculation"""
        holdings = sample_excel_data["holdings"]
        
        response = client.post("/api/analytics/performance", json=holdings)
        
        assert response.status_code == 200
        data = response.json()
        
        assert "holdings" in data
        assert "best_performer" in data
        assert "worst_performer" in data
        assert isinstance(data["holdings"], list)
        assert len(data["holdings"]) == len(holdings)
        
        # Check first fund
        first_fund = data["holdings"][0]
        assert "fund_name" in first_fund
        assert "invested" in first_fund
        assert "current" in first_fund
        assert "gain" in first_fund
        assert "return_pct" in first_fund
    
    def test_performance_sorting(self, client):
        """Test that performance results are sorted by return percentage"""
        holdings = [
            {"fund_name": "Low Performer", "invested": 100000, "current_value": 105000, "return_1y": "5%", "return_3y": "10%", "alpha": "1.0"},
            {"fund_name": "High Performer", "invested": 100000, "current_value": 150000, "return_1y": "50%", "return_3y": "60%", "alpha": "10.0"},
            {"fund_name": "Mid Performer", "invested": 100000, "current_value": 125000, "return_1y": "25%", "return_3y": "30%", "alpha": "5.0"}
        ]
        
        response = client.post("/api/analytics/performance", json=holdings)
        data = response.json()
        performance_list = data["holdings"]
        
        # Verify sorting (highest return first)
        assert performance_list[0]["fund_name"] == "High Performer"
        assert performance_list[1]["fund_name"] == "Mid Performer"
        assert performance_list[2]["fund_name"] == "Low Performer"
        
        # Verify return percentages are calculated correctly
        assert performance_list[0]["return_pct"] == pytest.approx(50.0, rel=1e-2)
        assert performance_list[1]["return_pct"] == pytest.approx(25.0, rel=1e-2)
        assert performance_list[2]["return_pct"] == pytest.approx(5.0, rel=1e-2)
    
    def test_performance_with_zero_investment(self, client):
        """Test performance calculation with zero investment"""
        holdings = [
            {"fund_name": "Fund A", "invested": 0, "current_value": 10000, "return_1y": "-", "return_3y": "-", "alpha": "-"}
        ]
        
        response = client.post("/api/analytics/performance", json=holdings)
        data = response.json()
        
        # Should handle gracefully
        assert response.status_code == 200
        assert data["holdings"][0]["return_pct"] == 0
    
    def test_performance_with_negative_returns(self, client):
        """Test performance calculation with losses"""
        holdings = [
            {"fund_name": "Loss Fund", "invested": 100000, "current_value": 80000, "return_1y": "-20%", "return_3y": "-15%", "alpha": "-5.0"}
        ]
        
        response = client.post("/api/analytics/performance", json=holdings)
        data = response.json()
        
        assert data["holdings"][0]["return_pct"] == pytest.approx(-20.0, rel=1e-2)
        assert data["holdings"][0]["gain"] == -20000


# Integration tests
class TestAnalyticsWorkflow:
    """Test complete analytics workflow"""
    
    def test_full_analytics_pipeline(self, client, sample_excel_data):
        """Test running all analytics on same data"""
        holdings = sample_excel_data["holdings"]
        
        # 1. Get allocation
        allocation_response = client.post("/api/analytics/allocation", json=holdings)
        assert allocation_response.status_code == 200
        
        # 2. Get market cap
        market_cap_response = client.post("/api/analytics/market-cap", json=holdings)
        assert market_cap_response.status_code == 200
        
        # 3. Get performance
        performance_response = client.post("/api/analytics/performance", json=holdings)
        assert performance_response.status_code == 200
        
        # Verify total values match
        allocation_total = allocation_response.json()["total_value"]
        market_cap_total = market_cap_response.json()["total"]
        
        assert allocation_total == pytest.approx(market_cap_total, rel=1e-2)


# Edge cases
class TestAnalyticsEdgeCases:
    """Test edge cases and boundary conditions"""
    
    def test_single_fund_allocation(self, client):
        """Test allocation with single fund"""
        holdings = [
            {"fund_name": "Only Fund", "category": "Large Cap", "current_value": 100000, "amc": "HDFC", "style": "Growth"}
        ]
        
        response = client.post("/api/analytics/allocation", json=holdings)
        data = response.json()
        
        # Should be 100% in all categories
        assert data["by_category"]["Large Cap"]["pct"] == 100.0
        assert data["by_amc"]["HDFC"]["pct"] == 100.0
        assert data["by_style"]["Growth"]["pct"] == 100.0
    
    def test_very_small_values(self, client):
        """Test analytics with very small portfolio values"""
        holdings = [
            {"fund_name": "Fund A", "category": "Large Cap", "invested": 100, "current_value": 150, "amc": "HDFC", "style": "Growth", "return_1y": "-", "return_3y": "-", "alpha": "-"}
        ]
        
        allocation_response = client.post("/api/analytics/allocation", json=holdings)
        performance_response = client.post("/api/analytics/performance", json=holdings)
        
        assert allocation_response.status_code == 200
        assert performance_response.status_code == 200
    
    def test_missing_optional_fields(self, client):
        """Test analytics when optional fields are missing"""
        holdings = [
            {"fund_name": "Fund A", "category": "Large Cap", "current_value": 100000}
        ]
        
        response = client.post("/api/analytics/allocation", json=holdings)
        assert response.status_code == 200
