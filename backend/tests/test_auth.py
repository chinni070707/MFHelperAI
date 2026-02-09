"""
Tests for Authentication endpoints - register, login, profile, settings
"""
import pytest
from unittest.mock import AsyncMock, patch, MagicMock


class TestRegister:
    """Tests for POST /api/auth/register"""

    def test_register_success(self, client):
        """Register a new user with valid data"""
        response = client.post("/api/auth/register", json={
            "email": "newuser@example.com",
            "password": "Secure1234",
            "full_name": "New User",
        })
        assert response.status_code == 201
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
        assert data["user"]["email"] == "newuser@example.com"
        assert data["user"]["full_name"] == "New User"

    def test_register_duplicate_email(self, client, test_user):
        """Registration should fail if email already exists"""
        response = client.post("/api/auth/register", json={
            "email": test_user.email,
            "password": "Secure1234",
            "full_name": "Duplicate User",
        })
        assert response.status_code == 400
        assert "already registered" in response.json()["detail"].lower()

    def test_register_weak_password_no_uppercase(self, client):
        """Password without uppercase should be rejected"""
        response = client.post("/api/auth/register", json={
            "email": "weak@example.com",
            "password": "nodigits1",
            "full_name": "Weak Pass",
        })
        assert response.status_code == 422

    def test_register_weak_password_no_digit(self, client):
        """Password without digit should be rejected"""
        response = client.post("/api/auth/register", json={
            "email": "weak@example.com",
            "password": "NoDigitsHere",
            "full_name": "Weak Pass",
        })
        assert response.status_code == 422

    def test_register_short_password(self, client):
        """Password shorter than 8 chars should be rejected"""
        response = client.post("/api/auth/register", json={
            "email": "short@example.com",
            "password": "Ab1",
            "full_name": "Short Pass",
        })
        assert response.status_code == 422

    def test_register_missing_email(self, client):
        """Registration without email should fail"""
        response = client.post("/api/auth/register", json={
            "password": "Secure1234",
            "full_name": "No Email",
        })
        assert response.status_code == 422

    def test_register_invalid_email(self, client):
        """Registration with invalid email format should fail"""
        response = client.post("/api/auth/register", json={
            "email": "not-an-email",
            "password": "Secure1234",
            "full_name": "Bad Email",
        })
        assert response.status_code == 422

    def test_register_with_optional_fields(self, client):
        """Register with optional pan and phone fields"""
        response = client.post("/api/auth/register", json={
            "email": "full@example.com",
            "password": "Secure1234",
            "full_name": "Full User",
            "pan": "ABCDE1234F",
            "phone": "9876543210",
        })
        assert response.status_code == 201
        data = response.json()
        assert data["user"]["email"] == "full@example.com"


class TestLogin:
    """Tests for POST /api/auth/login"""

    def test_login_success(self, client, test_user):
        """Login with correct credentials"""
        response = client.post("/api/auth/login", json={
            "email": "testuser@example.com",
            "password": "Test1234",
        })
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
        assert data["user"]["email"] == "testuser@example.com"

    def test_login_wrong_password(self, client, test_user):
        """Login with wrong password should return 401"""
        response = client.post("/api/auth/login", json={
            "email": "testuser@example.com",
            "password": "WrongPass1",
        })
        assert response.status_code == 401

    def test_login_nonexistent_user(self, client):
        """Login with non-existent email should return 401"""
        response = client.post("/api/auth/login", json={
            "email": "nobody@example.com",
            "password": "Test1234",
        })
        assert response.status_code == 401

    def test_login_missing_password(self, client):
        """Login without password should fail validation"""
        response = client.post("/api/auth/login", json={
            "email": "testuser@example.com",
        })
        assert response.status_code == 422


class TestMe:
    """Tests for GET /api/auth/me"""

    def test_get_me_authenticated(self, authenticated_client, test_user):
        """Authenticated user can fetch their profile"""
        response = authenticated_client.get("/api/auth/me")
        assert response.status_code == 200
        data = response.json()
        assert data["email"] == test_user.email
        assert data["full_name"] == test_user.full_name

    def test_get_me_unauthenticated(self, client):
        """Unauthenticated request should return 401"""
        response = client.get("/api/auth/me")
        assert response.status_code == 401

    def test_get_me_invalid_token(self, client):
        """Invalid token should return 401"""
        response = client.get(
            "/api/auth/me",
            headers={"Authorization": "Bearer invalid-token-here"},
        )
        assert response.status_code == 401


class TestSettings:
    """Tests for GET/PUT /api/auth/settings"""

    def test_get_default_settings(self, authenticated_client):
        """New user should get default settings"""
        response = authenticated_client.get("/api/auth/settings")
        assert response.status_code == 200
        data = response.json()
        assert data["theme"] == "light"
        assert data["currency"] == "INR"

    def test_update_settings(self, authenticated_client):
        """User can update their settings"""
        response = authenticated_client.put("/api/auth/settings", json={
            "theme": "dark",
            "currency": "USD",
        })
        assert response.status_code == 200
        data = response.json()
        assert data["theme"] == "dark"
        assert data["currency"] == "USD"

    def test_settings_unauthenticated(self, client):
        """Unauthenticated settings access should return 401"""
        response = client.get("/api/auth/settings")
        assert response.status_code == 401


class TestGoogleSignIn:
    """Tests for POST /api/auth/google/verify"""

    @patch('app.routes.auth.httpx.AsyncClient')
    def test_google_signin_new_user(self, mock_client_class, client, db_session):
        """Google Sign-In with new user creates account"""
        # Mock Google's tokeninfo response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'aud': '106393763654-95tm312afpu5blldr7eitmgd5j2khnjv.apps.googleusercontent.com',
            'email': 'newgoogle@example.com',
            'sub': 'google-id-12345',
            'name': 'Google User',
            'picture': 'https://example.com/photo.jpg',
            'email_verified': 'true'
        }
        
        # Setup the async client mock
        mock_client = AsyncMock()
        mock_client.get.return_value = mock_response
        mock_client_class.return_value.__aenter__.return_value = mock_client
        
        response = client.post("/api/auth/google/verify", json={
            "token": "fake-google-token-12345"
        })
        
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
        assert data["user"]["email"] == "newgoogle@example.com"
        assert data["user"]["full_name"] == "Google User"
        assert data["user"]["profile_picture_url"] == "https://example.com/photo.jpg"

    @patch('app.routes.auth.httpx.AsyncClient')
    def test_google_signin_existing_user(self, mock_client_class, client, test_user, db_session):
        """Google Sign-In with existing user updates profile"""
        # Mock Google's tokeninfo response with test_user's email
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'aud': '106393763654-95tm312afpu5blldr7eitmgd5j2khnjv.apps.googleusercontent.com',
            'email': test_user.email,
            'sub': 'google-id-existing',
            'name': test_user.full_name,
            'picture': 'https://example.com/updated-photo.jpg',
            'email_verified': 'true'
        }
        
        # Setup the async client mock
        mock_client = AsyncMock()
        mock_client.get.return_value = mock_response
        mock_client_class.return_value.__aenter__.return_value = mock_client
        
        response = client.post("/api/auth/google/verify", json={
            "token": "fake-google-token-existing"
        })
        
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["user"]["email"] == test_user.email

    @patch('app.routes.auth.httpx.AsyncClient')
    def test_google_signin_invalid_token(self, mock_client_class, client):
        """Google Sign-In with invalid token returns 401"""
        # Mock Google's tokeninfo response for invalid token
        mock_response = MagicMock()
        mock_response.status_code = 400
        
        # Setup the async client mock
        mock_client = AsyncMock()
        mock_client.get.return_value = mock_response
        mock_client_class.return_value.__aenter__.return_value = mock_client
        
        response = client.post("/api/auth/google/verify", json={
            "token": "invalid-token"
        })
        
        assert response.status_code == 401
        assert "Invalid Google token" in response.json()["detail"]

    @patch('app.routes.auth.httpx.AsyncClient')
    def test_google_signin_wrong_audience(self, mock_client_class, client):
        """Google Sign-In with wrong client ID returns 401"""
        # Mock Google's tokeninfo response with wrong audience
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'aud': 'wrong-client-id',
            'email': 'user@example.com',
            'sub': 'google-id',
            'name': 'User',
            'email_verified': 'true'
        }
        
        # Setup the async client mock
        mock_client = AsyncMock()
        mock_client.get.return_value = mock_response
        mock_client_class.return_value.__aenter__.return_value = mock_client
        
        response = client.post("/api/auth/google/verify", json={
            "token": "fake-token-wrong-audience"
        })
        
        assert response.status_code == 401
        assert "Invalid token audience" in response.json()["detail"]

    def test_google_signin_missing_token(self, client):
        """Google Sign-In without token returns 400"""
        response = client.post("/api/auth/google/verify", json={})
        
        assert response.status_code == 400
        assert "Token is required" in response.json()["detail"]

    @patch('app.routes.auth.httpx.AsyncClient')
    def test_google_signin_no_email(self, mock_client_class, client):
        """Google Sign-In without email in response returns 400"""
        # Mock Google's tokeninfo response without email
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'aud': '106393763654-95tm312afpu5blldr7eitmgd5j2khnjv.apps.googleusercontent.com',
            'sub': 'google-id-12345',
            'name': 'User',
            'email_verified': 'true'
        }
        
        # Setup the async client mock
        mock_client = AsyncMock()
        mock_client.get.return_value = mock_response
        mock_client_class.return_value.__aenter__.return_value = mock_client
        
        response = client.post("/api/auth/google/verify", json={
            "token": "fake-token-no-email"
        })
        
        assert response.status_code == 400
        assert "Email not provided" in response.json()["detail"]
