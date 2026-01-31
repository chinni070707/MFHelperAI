"""
Unit tests for Portfolio API endpoints
Tests get, save, delete operations
"""
import pytest


class TestGetPortfolio:
    """Test portfolio retrieval endpoint"""
    
    def test_get_empty_portfolio(self, client):
        """Test getting portfolio when none exists"""
        response = client.get("/api/portfolio/")
        
        assert response.status_code == 200
        data = response.json()
        assert "holdings" in data
        assert len(data["holdings"]) == 0
        assert "message" in data
    
    def test_get_portfolio_after_save(self, client, sample_excel_data):
        """Test getting portfolio after saving"""
        # First save portfolio
        save_response = client.post("/api/portfolio/save", json=sample_excel_data)
        assert save_response.status_code == 200
        
        # Then retrieve it
        get_response = client.get("/api/portfolio/")
        assert get_response.status_code == 200
        
        data = get_response.json()
        assert len(data["holdings"]) == 2
        assert "summary" in data
    
    def test_get_portfolio_with_custom_user_id(self, client, sample_excel_data):
        """Test getting portfolio with custom user ID"""
        user_id = "test_user_123"
        
        # Save with custom user ID
        save_response = client.post(
            f"/api/portfolio/save?user_id={user_id}",
            json=sample_excel_data
        )
        assert save_response.status_code == 200
        
        # Retrieve with same user ID
        get_response = client.get(f"/api/portfolio/?user_id={user_id}")
        assert get_response.status_code == 200
        assert len(get_response.json()["holdings"]) == 2


class TestSavePortfolio:
    """Test portfolio save endpoint"""
    
    def test_save_valid_portfolio(self, client, sample_excel_data):
        """Test saving a valid portfolio"""
        response = client.post("/api/portfolio/save", json=sample_excel_data)
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "message" in data
    
    def test_save_portfolio_overwrites_existing(self, client, sample_excel_data):
        """Test that saving overwrites existing portfolio"""
        # Save initial portfolio
        client.post("/api/portfolio/save", json=sample_excel_data)
        
        # Modify and save again
        modified_data = sample_excel_data.copy()
        modified_data["holdings"] = modified_data["holdings"][:1]  # Keep only first holding
        
        response = client.post("/api/portfolio/save", json=modified_data)
        assert response.status_code == 200
        
        # Verify it was overwritten
        get_response = client.get("/api/portfolio/")
        assert len(get_response.json()["holdings"]) == 1
    
    def test_save_empty_portfolio(self, client):
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
        
        response = client.post("/api/portfolio/save", json=empty_data)
        assert response.status_code == 200
    
    def test_save_portfolio_with_invalid_data(self, client):
        """Test saving portfolio with invalid data"""
        invalid_data = {"invalid": "data"}
        
        response = client.post("/api/portfolio/save", json=invalid_data)
        # Should accept any dict-like structure
        assert response.status_code == 200


class TestDeletePortfolio:
    """Test portfolio delete endpoint"""
    
    def test_delete_existing_portfolio(self, client, sample_excel_data):
        """Test deleting an existing portfolio"""
        # First save
        client.post("/api/portfolio/save", json=sample_excel_data)
        
        # Then delete
        response = client.delete("/api/portfolio/")
        assert response.status_code == 200
        assert response.json()["success"] is True
        
        # Verify it's deleted
        get_response = client.get("/api/portfolio/")
        assert len(get_response.json()["holdings"]) == 0
    
    def test_delete_nonexistent_portfolio(self, client):
        """Test deleting a portfolio that doesn't exist"""
        response = client.delete("/api/portfolio/")
        
        assert response.status_code == 200
        assert response.json()["success"] is True


class TestGetHoldings:
    """Test get holdings endpoint"""
    
    def test_get_holdings_list(self, client, sample_excel_data):
        """Test getting just the holdings list"""
        # Save portfolio first
        client.post("/api/portfolio/save", json=sample_excel_data)
        
        # Get holdings
        response = client.get("/api/portfolio/holdings")
        assert response.status_code == 200
        
        holdings = response.json()
        assert isinstance(holdings, list)
        assert len(holdings) == 2
    
    def test_get_holdings_from_empty_portfolio(self, client):
        """Test getting holdings when portfolio is empty"""
        # Delete any existing portfolio first
        client.delete("/api/portfolio/")
        
        response = client.get("/api/portfolio/holdings")
        
        assert response.status_code == 200
        assert response.json() == []


class TestGetSummary:
    """Test get summary endpoint"""
    
    def test_get_summary(self, client, sample_excel_data):
        """Test getting portfolio summary"""
        # Save portfolio first
        client.post("/api/portfolio/save", json=sample_excel_data)
        
        # Get summary
        response = client.get("/api/portfolio/summary")
        assert response.status_code == 200
        
        summary = response.json()
        assert "total_funds" in summary
        assert "total_invested" in summary
        assert "total_current" in summary
        assert summary["total_funds"] == 2
    
    def test_get_summary_from_empty_portfolio(self, client):
        """Test getting summary when portfolio is empty"""
        # Delete any existing portfolio first
        client.delete("/api/portfolio/")
        
        response = client.get("/api/portfolio/summary")
        
        assert response.status_code == 200
        assert response.json() == {}


# Integration tests
class TestPortfolioWorkflow:
    """Test complete portfolio workflow"""
    
    def test_upload_save_retrieve_workflow(self, client, sample_excel_file):
        """Test complete workflow: upload -> save -> retrieve"""
        # 1. Upload Excel
        with open(sample_excel_file, 'rb') as f:
            upload_response = client.post(
                "/api/upload/excel",
                files={"file": ("portfolio.xlsx", f, "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")}
            )
        
        assert upload_response.status_code == 200
        portfolio_data = upload_response.json()
        
        # 2. Save portfolio
        save_response = client.post("/api/portfolio/save", json=portfolio_data)
        assert save_response.status_code == 200
        
        # 3. Retrieve portfolio
        get_response = client.get("/api/portfolio/")
        assert get_response.status_code == 200
        retrieved_data = get_response.json()
        
        # 4. Verify data integrity
        assert len(retrieved_data["holdings"]) == len(portfolio_data["holdings"])
        assert retrieved_data["summary"]["total_funds"] == portfolio_data["summary"]["total_funds"]
    
    def test_multiple_users_isolation(self, client, sample_excel_data):
        """Test that different users have isolated portfolios"""
        user1_data = sample_excel_data.copy()
        user2_data = sample_excel_data.copy()
        user2_data["holdings"] = user2_data["holdings"][:1]
        
        # Save for user 1
        client.post("/api/portfolio/save?user_id=user1", json=user1_data)
        
        # Save for user 2
        client.post("/api/portfolio/save?user_id=user2", json=user2_data)
        
        # Verify isolation
        user1_response = client.get("/api/portfolio/?user_id=user1")
        user2_response = client.get("/api/portfolio/?user_id=user2")
        
        assert len(user1_response.json()["holdings"]) == 2
        assert len(user2_response.json()["holdings"]) == 1
