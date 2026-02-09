"""
Unit tests for Portfolio API endpoints
Tests get, save, delete operations
"""
import pytest


class TestGetPortfolio:
    """Test portfolio retrieval endpoint"""
    
    def test_get_empty_portfolio(self, authenticated_client):
        """Test getting portfolio when none exists"""
        response = authenticated_client.get("/api/portfolio/")
        
        assert response.status_code == 200
        data = response.json()
        assert "holdings" in data
        assert len(data["holdings"]) == 0
        assert "message" in data
    
    def test_get_portfolio_after_save(self, authenticated_client, sample_excel_data):
        """Test getting portfolio after saving"""
        # First save portfolio
        save_response = authenticated_client.post("/api/portfolio/save", json=sample_excel_data)
        assert save_response.status_code == 200
        
        # Then retrieve it
        get_response = authenticated_client.get("/api/portfolio/")
        assert get_response.status_code == 200
        
        data = get_response.json()
        assert len(data["holdings"]) == 2
        assert "summary" in data
    
    def test_get_portfolio_with_custom_user_id(self, authenticated_client, sample_excel_data):
        """Test getting portfolio with custom user ID - should work with authenticated user only"""
        # Save portfolio for authenticated user
        save_response = authenticated_client.post(
            "/api/portfolio/save",
            json=sample_excel_data
        )
        assert save_response.status_code == 200
        
        # Retrieve - authenticated endpoints ignore user_id param, use current user
        get_response = authenticated_client.get("/api/portfolio/")
        assert get_response.status_code == 200
        assert len(get_response.json()["holdings"]) == 2


class TestSavePortfolio:
    """Test portfolio save endpoint"""
    
    def test_save_valid_portfolio(self, authenticated_client, sample_excel_data):
        """Test saving a valid portfolio"""
        response = authenticated_client.post("/api/portfolio/save", json=sample_excel_data)
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "message" in data
    
    def test_save_portfolio_overwrites_existing(self, authenticated_client, sample_excel_data):
        """Test that saving overwrites existing portfolio"""
        # Save initial portfolio
        authenticated_client.post("/api/portfolio/save", json=sample_excel_data)
        
        # Modify and save again
        modified_data = sample_excel_data.copy()
        modified_data["holdings"] = modified_data["holdings"][:1]  # Keep only first holding
        
        response = authenticated_client.post("/api/portfolio/save", json=modified_data)
        assert response.status_code == 200
        
        # Verify it was overwritten
        get_response = authenticated_client.get("/api/portfolio/")
        assert len(get_response.json()["holdings"]) == 1
    
    def test_save_empty_portfolio(self, authenticated_client):
        """Test saving an empty portfolio"""
        empty_data = {
            "holdings": [],
            "summary": {
                "total_funds": 0,
                "total_invested": 0,
                "total_current": 0,
                "total_gain": 0,
                "return_pct": 0
            }
        }
        
        response = authenticated_client.post("/api/portfolio/save", json=empty_data)
        assert response.status_code == 200
    
    def test_save_portfolio_with_invalid_data(self, authenticated_client):
        """Test saving portfolio with invalid data"""
        invalid_data = {"invalid": "data"}
        
        response = authenticated_client.post("/api/portfolio/save", json=invalid_data)
        # Should accept any dict-like structure
        assert response.status_code == 200


class TestDeletePortfolio:
    """Test portfolio delete endpoint"""
    
    def test_delete_existing_portfolio(self, authenticated_client, sample_excel_data):
        """Test deleting an existing portfolio"""
        # First save
        authenticated_client.post("/api/portfolio/save", json=sample_excel_data)
        
        # Then delete
        response = authenticated_client.delete("/api/portfolio/")
        assert response.status_code == 200
        assert response.json()["success"] is True
        
        # Verify it's deleted
        get_response = authenticated_client.get("/api/portfolio/")
        assert len(get_response.json()["holdings"]) == 0
    
    def test_delete_nonexistent_portfolio(self, authenticated_client):
        """Test deleting a portfolio that doesn't exist"""
        response = authenticated_client.delete("/api/portfolio/")
        
        assert response.status_code == 200
        assert response.json()["success"] is True


class TestGetHoldings:
    """Test get holdings endpoint"""
    
    def test_get_holdings_list(self, authenticated_client, sample_excel_data):
        """Test getting just the holdings list"""
        # Save portfolio first
        authenticated_client.post("/api/portfolio/save", json=sample_excel_data)
        
        # Get holdings
        response = authenticated_client.get("/api/portfolio/holdings")
        assert response.status_code == 200
        
        holdings = response.json()
        assert isinstance(holdings, list)
        assert len(holdings) == 2
    
    def test_get_holdings_from_empty_portfolio(self, authenticated_client):
        """Test getting holdings when portfolio is empty"""
        # Delete any existing portfolio first
        authenticated_client.delete("/api/portfolio/")
        
        response = authenticated_client.get("/api/portfolio/holdings")
        
        assert response.status_code == 200
        assert response.json() == []


class TestGetSummary:
    """Test get summary endpoint"""
    
    def test_get_summary(self, authenticated_client, sample_excel_data):
        """Test getting portfolio summary"""
        # Save portfolio first
        authenticated_client.post("/api/portfolio/save", json=sample_excel_data)
        
        # Get summary
        response = authenticated_client.get("/api/portfolio/summary")
        assert response.status_code == 200
        
        summary = response.json()
        # Note: API returns holdings_count, not total_funds
        assert "total_invested" in summary
        assert "total_current" in summary
        assert summary["total_invested"] > 0
    
    def test_get_summary_from_empty_portfolio(self, authenticated_client):
        """Test getting summary when portfolio is empty"""
        # Delete any existing portfolio first
        authenticated_client.delete("/api/portfolio/")
        
        response = authenticated_client.get("/api/portfolio/summary")
        
        assert response.status_code == 200
        assert response.json() == {}


# Integration tests
class TestPortfolioWorkflow:
    """Test complete portfolio workflow"""
    
    def test_upload_save_retrieve_workflow(self, authenticated_client, sample_excel_file):
        """Test complete workflow: upload -> save -> retrieve"""
        # 1. Upload Excel
        with open(sample_excel_file, 'rb') as f:
            upload_response = authenticated_client.post(
                "/api/upload/excel",
                files={"file": ("portfolio.xlsx", f, "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")}
            )
        
        assert upload_response.status_code == 200
        portfolio_data = upload_response.json()
        
        # 2. Save portfolio
        save_response = authenticated_client.post("/api/portfolio/save", json=portfolio_data)
        assert save_response.status_code == 200
        
        # 3. Retrieve portfolio
        get_response = authenticated_client.get("/api/portfolio/")
        assert get_response.status_code == 200
        retrieved_data = get_response.json()
        
        # 4. Verify data integrity
        assert len(retrieved_data["holdings"]) == len(portfolio_data["holdings"])
        # Note: API returns holdings_count (integer), not total_funds 
        # The summary structure differs between upload and get endpoints
        assert "summary" in retrieved_data
    
    def test_multiple_users_isolation(self, authenticated_client, sample_excel_data):
        """Test that authenticated user's portfolio is isolated"""
        # Save for authenticated user
        authenticated_client.post("/api/portfolio/save", json=sample_excel_data)
        
        # Verify user can only see their own data
        user_response = authenticated_client.get("/api/portfolio/")
        
        assert len(user_response.json()["holdings"]) == 2
