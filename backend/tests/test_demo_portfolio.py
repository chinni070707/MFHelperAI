"""
Tests for Demo Portfolio API
"""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.database import Base, get_db
from app.models.demo_portfolio import DemoPortfolio

# Test database setup
SQLALCHEMY_TEST_DATABASE_URL = "sqlite:///./test_demo.db"
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
def sample_demo_holdings():
    """Sample demo portfolio data"""
    return [
        {
            "scheme_name": "HDFC Equity Fund - Direct Growth",
            "scheme_code": "HDFC001",
            "units": 100.0,
            "avg_cost": 500.0,
            "current_nav": 600.0,
            "amc": "HDFC Mutual Fund",
            "category": "Equity"
        },
        {
            "scheme_name": "ICICI Debt Fund - Direct Growth",
            "scheme_code": "ICICI002",
            "units": 200.0,
            "avg_cost": 100.0,
            "current_nav": 105.0,
            "amc": "ICICI Prudential Mutual Fund",
            "category": "Debt"
        }
    ]


class TestDemoPortfolioAPI:
    """Test suite for demo portfolio endpoints"""

    def test_seed_demo_portfolio(self, sample_demo_holdings):
        """Test seeding demo portfolio data"""
        response = client.post("/api/demo/portfolio/seed", json=sample_demo_holdings)
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["message"].startswith("Demo portfolio seeded with")

    def test_get_demo_portfolio_empty(self):
        """Test getting demo portfolio when none exists"""
        # Clear demo data first
        db = TestingSessionLocal()
        db.query(DemoPortfolio).delete()
        db.commit()
        db.close()
        
        response = client.get("/api/demo/portfolio")
        assert response.status_code == 404
        assert "not configured" in response.json()["detail"].lower()

    def test_get_demo_portfolio_success(self, sample_demo_holdings):
        """Test successfully getting demo portfolio"""
        # Seed first
        client.post("/api/demo/portfolio/seed", json=sample_demo_holdings)
        
        # Get demo portfolio
        response = client.get("/api/demo/portfolio")
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["mode"] == "demo"
        assert len(data["holdings"]) == 2
        assert "metadata" in data
        assert data["metadata"]["fundCount"] == 2
        assert data["metadata"]["isDemo"] is True

    def test_demo_portfolio_calculations(self, sample_demo_holdings):
        """Test that totals are calculated correctly"""
        client.post("/api/demo/portfolio/seed", json=sample_demo_holdings)
        
        response = client.get("/api/demo/portfolio")
        data = response.json()
        
        metadata = data["metadata"]
        
        # HDFC: 100 * 500 = 50000, 100 * 600 = 60000
        # ICICI: 200 * 100 = 20000, 200 * 105 = 21000
        # Total invested: 70000, Current: 81000, Gain: 11000
        
        assert metadata["totalInvested"] == 70000.0
        assert metadata["currentValue"] == 81000.0
        assert metadata["totalGain"] == 11000.0
        assert abs(metadata["totalGainPercent"] - 15.71) < 0.1  # ~15.71%

    def test_demo_portfolio_inactive_holdings(self, sample_demo_holdings):
        """Test that inactive holdings are excluded"""
        # Add holdings
        client.post("/api/demo/portfolio/seed", json=sample_demo_holdings)
        
        # Mark one as inactive
        db = TestingSessionLocal()
        holding = db.query(DemoPortfolio).first()
        holding.is_active = False
        db.commit()
        db.close()
        
        # Get portfolio
        response = client.get("/api/demo/portfolio")
        data = response.json()
        
        # Should only return active holdings
        assert len(data["holdings"]) == 1
        assert data["metadata"]["fundCount"] == 1

    def test_seed_demo_portfolio_invalid_data(self):
        """Test seeding with invalid data"""
        invalid_data = [
            {
                "scheme_name": "Test Fund",
                # Missing required fields
            }
        ]
        
        response = client.post("/api/demo/portfolio/seed", json=invalid_data)
        assert response.status_code in [400, 422, 500]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
