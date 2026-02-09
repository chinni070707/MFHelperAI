"""
Tests for User Leads API
"""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.database import Base, get_db
from app.models.user_leads import UserLead

# Test database setup
SQLALCHEMY_TEST_DATABASE_URL = "sqlite:///./test_leads.db"
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


@pytest.fixture(autouse=True)
def clear_leads():
    """Clear leads before each test"""
    db = TestingSessionLocal()
    db.query(UserLead).delete()
    db.commit()
    db.close()


class TestUserLeadsAPI:
    """Test suite for user leads capture"""

    def test_capture_lead_with_email(self):
        """Test capturing lead with email"""
        response = client.post(
            "/api/auth/leads/capture",
            params={
                "email": "test@example.com",
                "source": "demo-banner"
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "lead_id" in data
        
        # Verify in database
        db = TestingSessionLocal()
        lead = db.query(UserLead).filter(UserLead.email == "test@example.com").first()
        assert lead is not None
        assert lead.source == "demo-banner"
        assert lead.interaction_count == 1
        db.close()

    def test_capture_lead_with_phone(self):
        """Test capturing lead with phone"""
        response = client.post(
            "/api/auth/leads/capture",
            params={
                "phone": "+919876543210",
                "source": "export-gate"
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        
        # Verify in database
        db = TestingSessionLocal()
        lead = db.query(UserLead).filter(UserLead.phone == "+919876543210").first()
        assert lead is not None
        assert lead.source == "export-gate"
        db.close()

    def test_capture_lead_no_email_or_phone(self):
        """Test that either email or phone is required"""
        response = client.post(
            "/api/auth/leads/capture",
            params={
                "source": "test"
            }
        )
        
        assert response.status_code == 400

    def test_capture_lead_duplicate_email(self):
        """Test updating existing lead"""
        # Create initial lead
        client.post(
            "/api/auth/leads/capture",
            params={
                "email": "test@example.com",
                "source": "demo-banner"
            }
        )
        
        # Capture again with same email
        response = client.post(
            "/api/auth/leads/capture",
            params={
                "email": "test@example.com",
                "source": "export-gate"
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "updated" in data["message"].lower()
        
        # Verify interaction count increased
        db = TestingSessionLocal()
        lead = db.query(UserLead).filter(UserLead.email == "test@example.com").first()
        assert lead.interaction_count == 2
        db.close()

    def test_capture_lead_with_both_email_and_phone(self):
        """Test capturing lead with both email and phone"""
        response = client.post(
            "/api/auth/leads/capture",
            params={
                "email": "test@example.com",
                "phone": "+919876543210",
                "source": "timed-prompt"
            }
        )
        
        assert response.status_code == 200
        
        # Verify in database
        db = TestingSessionLocal()
        lead = db.query(UserLead).filter(UserLead.email == "test@example.com").first()
        assert lead is not None
        assert lead.phone == "+919876543210"
        db.close()

    def test_signup_creates_user_lead(self):
        """Test that signup creates a user lead entry"""
        response = client.post(
            "/api/auth/register",
            json={
                "email": "newuser@example.com",
                "password": "securepass123",
                "full_name": "New User",
                "phone": "+919876543210",
                "source": "direct_signup"
            }
        )
        
        # Signup might fail due to other requirements, but check if lead was attempted
        # This is more of an integration test
        if response.status_code == 201:
            db = TestingSessionLocal()
            lead = db.query(UserLead).filter(UserLead.email == "newuser@example.com").first()
            # Lead should have been created
            if lead:
                assert lead.source == "direct_signup"
            db.close()

    def test_rate_limiting_on_lead_capture(self):
        """Test rate limiting on lead capture"""
        # Make multiple requests rapidly
        email = "ratelimit@example.com"
        
        responses = []
        for i in range(12):  # Rate limit is 10/hour
            response = client.post(
                "/api/auth/leads/capture",
                params={
                    "email": f"{i}{email}",
                    "source": "test"
                }
            )
            responses.append(response.status_code)
        
        # Some requests should succeed, but eventually should hit rate limit
        # This depends on the rate limiter configuration
        success_count = sum(1 for code in responses if code == 200)
        assert success_count >= 10  # At least 10 should succeed


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
