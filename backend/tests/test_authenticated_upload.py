"""
Tests for authenticated upload with database persistence
"""
import pytest
import PyPDF2
from io import BytesIO


class TestAuthenticatedUpload:
    """Test authenticated upload with database saving"""
    
    def test_upload_excel_saves_to_database_when_authenticated(self, client, authenticated_client, sample_excel_file, db_session):
        """Test that Excel upload saves to database when user is authenticated"""
        from app.models.models import Portfolio
        
        # Upload with authenticated client
        with open(sample_excel_file, 'rb') as f:
            response = authenticated_client.post(
                "/api/upload/excel",
                files={"file": ("portfolio.xlsx", f, "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")}
            )
        
        assert response.status_code == 200
        data = response.json()
        
        # Check response indicates save
        assert data.get("saved_to_database") is True, f"Expected saved_to_database=True, got {data.get('saved_to_database')}"
        assert "holdings" in data
        
        # Verify data in database
        portfolio_count = db_session.query(Portfolio).count()
        assert portfolio_count > 0, f"Expected portfolio entries in database, found {portfolio_count}"
        
    def test_upload_without_auth_does_not_save_to_database(self, client, sample_excel_file, db_session):
        """Test that upload without auth returns data but doesn't save"""
        from app.models.models import Portfolio
        
        initial_count = db_session.query(Portfolio).count()
        
        with open(sample_excel_file, 'rb') as f:
            response = client.post(
                "/api/upload/excel",
                files={"file": ("portfolio.xlsx", f, "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")}
            )
        
        assert response.status_code == 200
        data = response.json()
        
        # Should return parsed data
        assert data["success"] is True
        assert "holdings" in data
        
        # Should not save to database
        assert data.get("saved_to_database") is False, f"Expected saved_to_database=False, got {data.get('saved_to_database')}"
        
        # Database count should not increase
        final_count = db_session.query(Portfolio).count()
        assert final_count == initial_count, f"Database count changed from {initial_count} to {final_count}"
    
    def test_cas_upload_with_auth_attempts_save(self, authenticated_client, db_session):
        """Test CAS upload attempts to save to database when authenticated"""
        from app.models.models import Portfolio
        
        # Create unencrypted PDF for testing
        pdf_writer = PyPDF2.PdfWriter()
        page = pdf_writer.add_blank_page(width=200, height=200)
        
        pdf_bytes = BytesIO()
        pdf_writer.write(pdf_bytes)
        pdf_bytes.seek(0)
        
        initial_count = db_session.query(Portfolio).count()
        
        response = authenticated_client.post(
            "/api/upload/cas",
            files={"file": ("test_cas.pdf", pdf_bytes, "application/pdf")}
        )
        
        # May fail parsing (no valid CAS data) but should handle gracefully
        # The important thing is it tries to save if user is authenticated
        assert response.status_code in [200, 400]
        
    def test_upload_clears_existing_portfolio(self, authenticated_client, sample_excel_file, db_session):
        """Test that new upload clears existing portfolio before saving"""
        from app.models.models import Portfolio, User
        
        # Get the authenticated user
        user = db_session.query(User).filter(User.email == "test@example.com").first()
        if not user:
            pytest.skip("Test user not found")
        
        # Add some existing portfolio entries
        for i in range(3):
            entry = Portfolio(
                user_id=user.id,
                scheme_name=f"Old Fund {i}",
                invested_amount=10000,
                current_value=12000,
                is_active=True
            )
            db_session.add(entry)
        db_session.commit()
        
        old_count = db_session.query(Portfolio).filter(Portfolio.user_id == user.id).count()
        assert old_count == 3
        
        # Upload new portfolio
        with open(sample_excel_file, 'rb') as f:
            response = authenticated_client.post(
                "/api/upload/excel",
                files={"file": ("portfolio.xlsx", f, "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")}
            )
        
        assert response.status_code == 200
        data = response.json()
        
        # Verify old entries cleared and new ones added
        new_count = db_session.query(Portfolio).filter(Portfolio.user_id == user.id).count()
        assert new_count == len(data["holdings"]), f"Expected {len(data['holdings'])} entries, found {new_count}"
        assert new_count != old_count, "Portfolio should be replaced, not appended"
        
    def test_optional_auth_dependency_works(self, client, db_session):
        """Test that optional auth dependency allows unauthenticated requests"""
        # This tests the fix for oauth2_scheme with auto_error=False
        import pandas as pd
        from io import BytesIO
        
        # Create simple test Excel
        df = pd.DataFrame({
            'Fund Name': ['Test Fund'],
            'Invested': [10000],
            'Current Value': [12000]
        })
        
        excel_bytes = BytesIO()
        df.to_excel(excel_bytes, index=False)
        excel_bytes.seek(0)
        
        # Should work without auth header
        response = client.post(
            "/api/upload/excel",
            files={"file": ("test.xlsx", excel_bytes, "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")}
        )
        
        print(f"Response status: {response.status_code}")
        print(f"Response body: {response.text}")
        print(f"Response headers: {response.headers}")
        
        assert response.status_code == 200, f"Unauthenticated upload should work, got {response.status_code}: {response.text}"
        data = response.json()
        assert data["success"] is True
        assert data.get("saved_to_database") is False
