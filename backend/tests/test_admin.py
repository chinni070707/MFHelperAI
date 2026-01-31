"""
Unit tests for Admin API endpoints
"""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from datetime import datetime, timedelta

from app.main import app
from app.database import Base, get_db
from app.models.models import User, Portfolio, Holding


# Test database setup
SQLALCHEMY_DATABASE_URL = "sqlite:///./test_admin.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db
client = TestClient(app)


@pytest.fixture(scope="function")
def setup_database():
    """Create test database and tables"""
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def test_data():
    """Create test data"""
    # First ensure database and tables exist
    Base.metadata.create_all(bind=engine)
    
    db = TestingSessionLocal()
    
    try:
        # Create test users
        users = [
            User(
                email=f"user{i}@test.com",
                full_name=f"Test User {i}",
                hashed_password="hashed",
                pan=f"ABCDE{i:04d}F",
                is_active=True,
                is_verified=(i % 2 == 0),
                created_at=datetime.utcnow() - timedelta(days=i)
            )
            for i in range(5)
        ]
        db.add_all(users)
        db.commit()
        
        # Create test portfolios
        portfolios = []
        for user in users:
            portfolio = Portfolio(
                user_id=user.id,
                name=f"Portfolio {user.id}",
                total_current=100000 * user.id,
                total_invested=90000 * user.id,
                total_returns=10000 * user.id,
                percentage_returns=11.11,
                created_at=datetime.utcnow() - timedelta(days=user.id)
            )
            portfolios.append(portfolio)
            db.add(portfolio)
        db.commit()
        
        # Create test holdings
        for portfolio in portfolios:
            holdings = [
                Holding(
                    portfolio_id=portfolio.id,
                    scheme_code=f"SC{i:04d}",
                    fund_name=f"Test Fund {i}",
                    amc="Test AMC" if i < 3 else "Another AMC",
                    category="Equity",
                    current_value=10000 * (i + 1),
                    invested_value=9000 * (i + 1),
                    returns=1000 * (i + 1),
                    return_pct=11.11,
                    units=100.0
                )
                for i in range(3)
            ]
            db.add_all(holdings)
        db.commit()
        
        yield {
            "users_count": len(users),
            "portfolios_count": len(portfolios),
            "holdings_count": len(portfolios) * 3
        }
    finally:
        db.close()
        # Clean up: drop all tables after test
        Base.metadata.drop_all(bind=engine)


class TestAdminStats:
    """Test admin statistics endpoint"""
    
    def test_stats_without_api_key(self, test_data):
        """Test that stats endpoint requires API key"""
        response = client.get("/api/admin/stats")
        assert response.status_code == 401
        assert "Invalid admin credentials" in response.json()["detail"]
    
    def test_stats_with_wrong_api_key(self, test_data):
        """Test that stats endpoint rejects wrong API key"""
        response = client.get("/api/admin/stats?api_key=wrong-key")
        assert response.status_code == 401
    
    def test_stats_with_correct_api_key(self, test_data):
        """Test that stats endpoint works with correct API key"""
        response = client.get("/api/admin/stats?api_key=admin-secret-key-change-in-production")
        assert response.status_code == 200
        
        data = response.json()
        assert "users" in data
        assert "portfolios" in data
        assert "aum" in data
        assert "top_amcs" in data
        assert "top_funds" in data
        assert "recent_activity" in data
    
    def test_stats_user_counts(self, test_data):
        """Test user statistics are correct"""
        response = client.get("/api/admin/stats?api_key=admin-secret-key-change-in-production")
        data = response.json()
        
        assert data["users"]["total"] == test_data["users_count"]
        assert data["users"]["active"] == test_data["users_count"]  # All test users are active
        assert data["users"]["verified"] >= 0  # Some users are verified
    
    def test_stats_portfolio_counts(self, test_data):
        """Test portfolio statistics are correct"""
        response = client.get("/api/admin/stats?api_key=admin-secret-key-change-in-production")
        data = response.json()
        
        assert data["portfolios"]["total_uploads"] == test_data["portfolios_count"]
        assert data["portfolios"]["total_holdings"] == test_data["holdings_count"]
        assert data["portfolios"]["unique_users"] == test_data["users_count"]
    
    def test_stats_aum_calculation(self, test_data):
        """Test AUM calculations are correct"""
        response = client.get("/api/admin/stats?api_key=admin-secret-key-change-in-production")
        data = response.json()
        
        assert data["aum"]["total"] > 0
        assert data["aum"]["total_invested"] > 0
        assert data["aum"]["total_returns"] > 0
        assert data["aum"]["return_percentage"] > 0
    
    def test_stats_top_amcs(self, test_data):
        """Test top AMCs are returned"""
        response = client.get("/api/admin/stats?api_key=admin-secret-key-change-in-production")
        data = response.json()
        
        assert len(data["top_amcs"]) > 0
        assert all("name" in amc for amc in data["top_amcs"])
        assert all("total_value" in amc for amc in data["top_amcs"])
    
    def test_stats_recent_activity(self, test_data):
        """Test recent activity is returned"""
        response = client.get("/api/admin/stats?api_key=admin-secret-key-change-in-production")
        data = response.json()
        
        assert len(data["recent_activity"]) > 0
        assert all("user_id" in activity for activity in data["recent_activity"])
        assert all("total_value" in activity for activity in data["recent_activity"])


class TestAdminUsers:
    """Test admin users list endpoint"""
    
    def test_users_list_without_api_key(self, test_data):
        """Test that users endpoint requires API key"""
        response = client.get("/api/admin/users")
        assert response.status_code == 401
    
    def test_users_list_with_correct_api_key(self, test_data):
        """Test users list endpoint"""
        response = client.get("/api/admin/users?api_key=admin-secret-key-change-in-production")
        assert response.status_code == 200
        
        data = response.json()
        assert "total" in data
        assert "users" in data
        assert data["total"] == test_data["users_count"]
        assert len(data["users"]) == test_data["users_count"]
    
    def test_users_list_pagination(self, test_data):
        """Test users list pagination"""
        response = client.get("/api/admin/users?api_key=admin-secret-key-change-in-production&skip=0&limit=2")
        assert response.status_code == 200
        
        data = response.json()
        assert data["total"] == test_data["users_count"]
        assert len(data["users"]) == 2  # Limited to 2
        assert data["skip"] == 0
        assert data["limit"] == 2
    
    def test_users_list_user_details(self, test_data):
        """Test user details in list"""
        response = client.get("/api/admin/users?api_key=admin-secret-key-change-in-production")
        data = response.json()
        
        user = data["users"][0]
        assert "id" in user
        assert "email" in user
        assert "full_name" in user
        assert "portfolio_count" in user
        assert "total_aum" in user
        assert "created_at" in user


class TestAdminTimeline:
    """Test admin timeline analytics endpoint"""
    
    def test_timeline_without_api_key(self, test_data):
        """Test that timeline endpoint requires API key"""
        response = client.get("/api/admin/analytics/timeline")
        assert response.status_code == 401
    
    def test_timeline_with_correct_api_key(self, test_data):
        """Test timeline analytics endpoint"""
        response = client.get("/api/admin/analytics/timeline?api_key=admin-secret-key-change-in-production")
        assert response.status_code == 200
        
        data = response.json()
        assert "period_days" in data
        assert "daily_registrations" in data
        assert "daily_uploads" in data
    
    def test_timeline_custom_days(self, test_data):
        """Test timeline with custom days parameter"""
        response = client.get("/api/admin/analytics/timeline?api_key=admin-secret-key-change-in-production&days=7")
        assert response.status_code == 200
        
        data = response.json()
        assert data["period_days"] == 7
    
    def test_timeline_data_structure(self, test_data):
        """Test timeline data structure"""
        response = client.get("/api/admin/analytics/timeline?api_key=admin-secret-key-change-in-production")
        data = response.json()
        
        # Check daily registrations structure
        if len(data["daily_registrations"]) > 0:
            reg = data["daily_registrations"][0]
            assert "date" in reg
            assert "count" in reg
        
        # Check daily uploads structure
        if len(data["daily_uploads"]) > 0:
            upload = data["daily_uploads"][0]
            assert "date" in upload
            assert "count" in upload


class TestAdminSecurity:
    """Test admin security features"""
    
    def test_multiple_wrong_api_keys(self, test_data):
        """Test that multiple wrong API keys are rejected"""
        wrong_keys = ["wrong1", "wrong2", "wrong3", ""]
        
        for key in wrong_keys:
            response = client.get(f"/api/admin/stats?api_key={key}")
            assert response.status_code == 401
    
    def test_api_key_case_sensitivity(self, test_data):
        """Test that API key is case sensitive"""
        wrong_case_key = "ADMIN-SECRET-KEY-CHANGE-IN-PRODUCTION"
        response = client.get(f"/api/admin/stats?api_key={wrong_case_key}")
        assert response.status_code == 401
    
    def test_no_sensitive_data_in_error(self, test_data):
        """Test that error messages don't leak sensitive data"""
        response = client.get("/api/admin/stats?api_key=wrong")
        error_message = response.json()["detail"].lower()
        
        # Should not contain actual API key or database details
        assert "admin-secret-key" not in error_message
        assert "password" not in error_message
        assert "database" not in error_message
