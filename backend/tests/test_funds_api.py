"""
Tests for Funds List API
"""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.database import Base, get_db
from app.models.funds_master import FundMaster

# Test database setup
SQLALCHEMY_TEST_DATABASE_URL = "sqlite:///./test_funds.db"
engine = create_engine(SQLALCHEMY_TEST_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db
client = TestClient(app)


@pytest.fixture(scope="module", autouse=True)
def setup_database():
    """Create test database and tables"""
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def sample_funds():
    """Sample fund data"""
    return [
        {
            "scheme_name": "HDFC Equity Fund - Direct Growth",
            "scheme_code": "HDFC001",
            "amc": "HDFC Mutual Fund",
            "category": "Equity",
            "current_nav": 600.0,
            "plan_type": "Direct",
            "is_active": True
        },
        {
            "scheme_name": "ICICI Debt Fund - Direct Growth",
            "scheme_code": "ICICI002",
            "amc": "ICICI Prudential Mutual Fund",
            "category": "Debt",
            "current_nav": 105.0,
            "plan_type": "Direct",
            "is_active": True
        },
        {
            "scheme_name": "SBI Hybrid Fund - Regular Growth",
            "scheme_code": "SBI003",
            "amc": "SBI Mutual Fund",
            "category": "Hybrid",
            "current_nav": 200.0,
            "plan_type": "Regular",
            "is_active": True
        },
        {
            "scheme_name": "Axis Liquid Fund - Direct Growth",
            "scheme_code": "AXIS004",
            "amc": "Axis Mutual Fund",
            "category": "Liquid",
            "current_nav": 1000.0,
            "plan_type": "Direct",
            "is_active": False  # Inactive fund
        }
    ]


class TestFundsListAPI:
    """Test suite for funds list endpoints"""

    def test_seed_funds_master(self, sample_funds):
        """Test seeding funds master data"""
        response = client.post("/api/funds/seed", json=sample_funds)
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["added"] == 4
        assert data["total"] == 4

    def test_get_funds_list_all(self, sample_funds):
        """Test getting all funds"""
        client.post("/api/funds/seed", json=sample_funds)
        
        response = client.get("/api/funds/list")
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        # Should only return active funds
        assert len(data["funds"]) == 3
        assert data["pagination"]["total"] == 3

    def test_get_funds_list_search(self, sample_funds):
        """Test searching funds by name"""
        client.post("/api/funds/seed", json=sample_funds)
        
        response = client.get("/api/funds/list?search=HDFC")
        
        assert response.status_code == 200
        data = response.json()
        assert len(data["funds"]) == 1
        assert "HDFC" in data["funds"][0]["scheme_name"]

    def test_get_funds_list_filter_category(self, sample_funds):
        """Test filtering by category"""
        client.post("/api/funds/seed", json=sample_funds)
        
        response = client.get("/api/funds/list?category=Equity")
        
        assert response.status_code == 200
        data = response.json()
        assert len(data["funds"]) == 1
        assert data["funds"][0]["category"] == "Equity"

    def test_get_funds_list_filter_amc(self, sample_funds):
        """Test filtering by AMC"""
        client.post("/api/funds/seed", json=sample_funds)
        
        response = client.get("/api/funds/list?amc=ICICI Prudential Mutual Fund")
        
        assert response.status_code == 200
        data = response.json()
        assert len(data["funds"]) == 1
        assert data["funds"][0]["amc"] == "ICICI Prudential Mutual Fund"

    def test_get_funds_list_filter_plan_type(self, sample_funds):
        """Test filtering by plan type"""
        client.post("/api/funds/seed", json=sample_funds)
        
        response = client.get("/api/funds/list?plan_type=Direct")
        
        assert response.status_code == 200
        data = response.json()
        assert len(data["funds"]) == 2
        for fund in data["funds"]:
            assert fund["plan_type"] == "Direct"

    def test_get_funds_list_pagination(self, sample_funds):
        """Test pagination"""
        client.post("/api/funds/seed", json=sample_funds)
        
        # Page 1 with limit 2
        response = client.get("/api/funds/list?page=1&limit=2")
        
        assert response.status_code == 200
        data = response.json()
        assert len(data["funds"]) == 2
        assert data["pagination"]["page"] == 1
        assert data["pagination"]["limit"] == 2
        assert data["pagination"]["total"] == 3

    def test_get_funds_list_dropdown_format(self, sample_funds):
        """Test dropdown format response"""
        client.post("/api/funds/seed", json=sample_funds)
        
        response = client.get("/api/funds/list?dropdown=true&limit=10")
        
        assert response.status_code == 200
        data = response.json()
        
        # Check dropdown format
        fund = data["funds"][0]
        assert "value" in fund
        assert "label" in fund
        assert "scheme_name" in fund
        assert "amc" in fund

    def test_get_funds_list_include_inactive(self, sample_funds):
        """Test including inactive funds"""
        client.post("/api/funds/seed", json=sample_funds)
        
        response = client.get("/api/funds/list?active_only=false")
        
        assert response.status_code == 200
        data = response.json()
        # Should include all 4 funds (including inactive)
        assert data["pagination"]["total"] == 4

    def test_get_categories(self, sample_funds):
        """Test getting list of categories"""
        client.post("/api/funds/seed", json=sample_funds)
        
        response = client.get("/api/funds/categories")
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "Equity" in data["categories"]
        assert "Debt" in data["categories"]
        assert "Hybrid" in data["categories"]
        # Liquid is inactive, so shouldn't appear
        assert len(data["categories"]) == 3

    def test_get_amcs(self, sample_funds):
        """Test getting list of AMCs"""
        client.post("/api/funds/seed", json=sample_funds)
        
        response = client.get("/api/funds/amcs")
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "HDFC Mutual Fund" in data["amcs"]
        assert "ICICI Prudential Mutual Fund" in data["amcs"]
        assert len(data["amcs"]) == 3

    def test_get_fund_details(self, sample_funds):
        """Test getting specific fund details"""
        client.post("/api/funds/seed", json=sample_funds)
        
        # Get fund ID
        list_response = client.get("/api/funds/list?limit=1")
        fund_id = list_response.json()["funds"][0]["id"]
        
        # Get details
        response = client.get(f"/api/funds/{fund_id}")
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "fund" in data
        assert data["fund"]["id"] == fund_id

    def test_get_fund_details_not_found(self):
        """Test getting non-existent fund"""
        response = client.get("/api/funds/99999")
        
        assert response.status_code == 404

    def test_seed_funds_update_existing(self, sample_funds):
        """Test updating existing funds"""
        # Seed initial data
        client.post("/api/funds/seed", json=sample_funds)
        
        # Update with modified data
        updated_fund = sample_funds[0].copy()
        updated_fund["current_nav"] = 650.0
        
        response = client.post("/api/funds/seed", json=[updated_fund])
        
        assert response.status_code == 200
        data = response.json()
        assert data["updated"] == 1
        assert data["added"] == 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
