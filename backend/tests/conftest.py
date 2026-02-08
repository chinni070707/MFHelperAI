"""
Test configuration and fixtures for MFHelper API tests
"""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
import os
import tempfile

from app.main import app
from app.database import Base, get_db
from app.models.models import User
from app.utils.auth import get_password_hash, create_access_token


# Test database setup — in-memory SQLite for clean isolation
SQLALCHEMY_TEST_DATABASE_URL = "sqlite://"

engine = create_engine(
    SQLALCHEMY_TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="function")
def test_db():
    """Create a fresh database for each test"""
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def db_session(test_db):
    """Get a database session for testing"""
    session = TestingSessionLocal()
    yield session
    session.rollback()
    session.close()


@pytest.fixture(scope="function")
def db(db_session):
    """Alias for db_session to match common test parameter naming"""
    return db_session


@pytest.fixture(scope="function")
def client(db_session):
    """Create a test client with database override"""
    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()


@pytest.fixture
def test_user(db_session):
    """Create a test user in the database"""
    user = User(
        email="testuser@example.com",
        hashed_password=get_password_hash("Test1234"),
        full_name="Test User",
        is_active=True,
        is_verified=False,
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def auth_token(test_user):
    """Create a valid JWT token for the test user"""
    return create_access_token(data={"sub": test_user.id})


@pytest.fixture
def authenticated_client(db_session, test_user, auth_token):
    """Test client with authentication headers"""
    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app, headers={"Authorization": f"Bearer {auth_token}"}) as test_client:
        yield test_client

    app.dependency_overrides.clear()


@pytest.fixture
def sample_excel_data():
    """Sample portfolio data for testing"""
    return {
        "holdings": [
            {
                "fund_name": "Parag Parikh Flexi Cap Fund",
                "amc": "PPFAS AMC",
                "category": "Flexi Cap",
                "invested": 100000,
                "current_value": 125000,
                "units": 1234.56,
                "nav": 101.25,
                "return_1y": "18.5%",
                "return_3y": "22.3%",
                "alpha": "5.2",
                "style": "GARP"
            },
            {
                "fund_name": "ICICI Prudential Bluechip Fund",
                "amc": "ICICI Prudential",
                "category": "Large Cap",
                "invested": 50000,
                "current_value": 58000,
                "units": 567.89,
                "nav": 102.10,
                "return_1y": "15.2%",
                "return_3y": "19.8%",
                "alpha": "3.5",
                "style": "Quality"
            }
        ],
        "summary": {
            "total_funds": 2,
            "total_invested": 150000,
            "total_current": 183000,
            "total_gain": 33000,
            "return_pct": 22.0
        }
    }


@pytest.fixture
def sample_excel_file(tmp_path):
    """Create a sample Excel file for testing"""
    import pandas as pd
    
    data = {
        'Fund Name': ['Parag Parikh Flexi Cap Fund', 'ICICI Prudential Bluechip Fund'],
        'AMC': ['PPFAS AMC', 'ICICI Prudential'],
        'Category': ['Flexi Cap', 'Large Cap'],
        'Invested': [100000, 50000],
        'Current Value': [125000, 58000],
        'Units': [1234.56, 567.89],
        'NAV': [101.25, 102.10]
    }
    
    df = pd.DataFrame(data)
    file_path = tmp_path / "test_portfolio.xlsx"
    df.to_excel(file_path, index=False)
    
    return file_path


@pytest.fixture
def sample_csv_file(tmp_path):
    """Create a sample CSV file for testing"""
    import pandas as pd
    
    data = {
        'Fund Name': ['Quant Active Fund', 'Motilal Oswal Midcap Fund'],
        'AMC': ['Quant MF', 'Motilal Oswal'],
        'Category': ['Multi Cap', 'Mid Cap'],
        'Invested': [75000, 60000],
        'Current Value': [95000, 72000],
        'Units': [890.12, 456.78],
        'NAV': [106.75, 157.60]
    }
    
    df = pd.DataFrame(data)
    file_path = tmp_path / "test_portfolio.csv"
    df.to_csv(file_path, index=False)
    
    return file_path


@pytest.fixture
def invalid_excel_file(tmp_path):
    """Create an invalid Excel file for error testing"""
    file_path = tmp_path / "invalid.xlsx"
    with open(file_path, 'wb') as f:
        f.write(b"This is not a valid Excel file")
    return file_path


@pytest.fixture
def large_excel_file(tmp_path):
    """Create a large Excel file for size limit testing"""
    import pandas as pd
    
    # Create a DataFrame with 10000 rows
    data = {
        'Fund Name': [f'Test Fund {i}' for i in range(10000)],
        'Invested': [100000] * 10000,
        'Current Value': [125000] * 10000
    }
    
    df = pd.DataFrame(data)
    file_path = tmp_path / "large_portfolio.xlsx"
    df.to_excel(file_path, index=False)
    
    return file_path


@pytest.fixture
def mock_fund_holdings():
    """Mock fund holdings data for overlap testing"""
    return [
        {
            "fund_name": "Parag Parikh Flexi Cap Fund",
            "amc": "PPFAS AMC",
            "category": "Flexi Cap",
            "current_value": 125000
        },
        {
            "fund_name": "ICICI Prudential Bluechip Fund",
            "amc": "ICICI Prudential",
            "category": "Large Cap",
            "current_value": 58000
        }
    ]


@pytest.fixture
def sample_rebalance_request():
    """Sample rebalancing request data"""
    return {
        "holdings": [
            {
                "fund_name": "HDFC Flexi Cap Fund",
                "category": "Flexi Cap",
                "current_value": 200000,
                "invested": 180000
            },
            {
                "fund_name": "Kotak Small Cap Fund",
                "category": "Small Cap",
                "current_value": 50000,
                "invested": 45000
            }
        ],
        "target_large": 60,
        "target_mid": 20,
        "target_small": 20,
        "mode": "fresh"
    }


# Helper functions for tests
def assert_valid_response(response, status_code=200):
    """Assert response is valid"""
    assert response.status_code == status_code
    if status_code == 200:
        assert response.json() is not None


def assert_error_response(response, status_code, error_message=None):
    """Assert error response"""
    assert response.status_code == status_code
    if error_message:
        assert error_message in response.json().get("detail", "")
