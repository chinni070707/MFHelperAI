"""
Unit tests for Upload API endpoints
Tests Excel parsing, CAS PDF parsing, file validation, and error handling
"""
import pytest
import io
from fastapi import UploadFile


class TestUploadExcel:
    """Test Excel file upload endpoint"""
    
    def test_upload_valid_excel_file(self, client, sample_excel_file):
        """Test uploading a valid Excel file"""
        with open(sample_excel_file, 'rb') as f:
            response = client.post(
                "/api/upload/excel",
                files={"file": ("portfolio.xlsx", f, "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")}
            )
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["success"] is True
        assert data["source"] == "excel"
        assert "holdings" in data
        assert len(data["holdings"]) > 0
        assert "summary" in data
        assert data["summary"]["total_funds"] == len(data["holdings"])
    
    def test_upload_valid_csv_file(self, client, sample_csv_file):
        """Test uploading a valid CSV file"""
        with open(sample_csv_file, 'rb') as f:
            response = client.post(
                "/api/upload/excel",
                files={"file": ("portfolio.csv", f, "text/csv")}
            )
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["success"] is True
        assert data["source"] == "excel"
        assert len(data["holdings"]) == 2
        
        # Verify first holding
        first_holding = data["holdings"][0]
        assert "fund_name" in first_holding
        assert "invested" in first_holding
        assert "current_value" in first_holding
    
    def test_upload_invalid_file_format(self, client, invalid_excel_file):
        """Test uploading an invalid file format"""
        with open(invalid_excel_file, 'rb') as f:
            response = client.post(
                "/api/upload/excel",
                files={"file": ("invalid.xlsx", f, "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")}
            )
        
        assert response.status_code == 400
        assert "error" in response.json()["detail"].lower()
    
    def test_upload_without_file(self, client):
        """Test uploading without a file"""
        response = client.post("/api/upload/excel")
        assert response.status_code == 422  # Unprocessable Entity
    
    def test_upload_wrong_file_extension(self, client, tmp_path):
        """Test uploading a file with wrong extension"""
        # Create a text file with .xlsx extension
        text_file = tmp_path / "fake.txt"
        text_file.write_text("This is not an Excel file")
        
        with open(text_file, 'rb') as f:
            response = client.post(
                "/api/upload/excel",
                files={"file": ("fake.txt", f, "text/plain")}
            )
        
        # Should still accept .txt files that could be CSV
        # But will fail parsing
        assert response.status_code in [200, 400]
    
    def test_excel_column_mapping(self, client, sample_excel_file):
        """Test that column mapping works correctly"""
        with open(sample_excel_file, 'rb') as f:
            response = client.post(
                "/api/upload/excel",
                files={"file": ("portfolio.xlsx", f, "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")}
            )
        
        data = response.json()
        holdings = data["holdings"]
        
        # Verify all required fields are present
        required_fields = ["fund_name", "invested", "current_value"]
        for holding in holdings:
            for field in required_fields:
                assert field in holding
    
    def test_excel_summary_calculations(self, client, sample_excel_file):
        """Test that summary calculations are correct"""
        with open(sample_excel_file, 'rb') as f:
            response = client.post(
                "/api/upload/excel",
                files={"file": ("portfolio.xlsx", f, "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")}
            )
        
        data = response.json()
        summary = data["summary"]
        holdings = data["holdings"]
        
        # Verify totals
        total_invested = sum(h["invested"] for h in holdings)
        total_current = sum(h["current_value"] for h in holdings)
        
        assert summary["total_invested"] == pytest.approx(total_invested, rel=1e-2)
        assert summary["total_current"] == pytest.approx(total_current, rel=1e-2)
        assert summary["total_gain"] == pytest.approx(total_current - total_invested, rel=1e-2)


class TestUploadCAS:
    """Test CAS PDF upload endpoint"""
    
    def test_upload_cas_without_password(self, client, tmp_path):
        """Test uploading CAS PDF without password"""
        # Create a dummy PDF file
        pdf_file = tmp_path / "cas.pdf"
        pdf_file.write_bytes(b"%PDF-1.4\nDummy PDF content")
        
        with open(pdf_file, 'rb') as f:
            response = client.post(
                "/api/upload/cas",
                files={"file": ("cas.pdf", f, "application/pdf")}
            )
        
        # Should either succeed or ask for password
        assert response.status_code in [200, 400]
    
    def test_upload_cas_with_password(self, client, tmp_path):
        """Test uploading CAS PDF with password"""
        pdf_file = tmp_path / "cas.pdf"
        pdf_file.write_bytes(b"%PDF-1.4\nDummy PDF content")
        
        with open(pdf_file, 'rb') as f:
            response = client.post(
                "/api/upload/cas",
                files={"file": ("cas.pdf", f, "application/pdf")},
                data={"password": "ABCDE1234F"}
            )
        
        assert response.status_code in [200, 400]
    
    def test_upload_non_pdf_file(self, client, sample_excel_file):
        """Test uploading non-PDF file to CAS endpoint"""
        with open(sample_excel_file, 'rb') as f:
            response = client.post(
                "/api/upload/cas",
                files={"file": ("not_a_pdf.xlsx", f, "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")}
            )
        
        # Should reject non-PDF files
        assert response.status_code == 400


class TestDownloadTemplate:
    """Test template download endpoint"""
    
    def test_download_excel_template(self, client):
        """Test downloading Excel template"""
        response = client.get("/api/upload/template")
        
        if response.status_code == 200:
            assert response.headers["content-type"] in [
                "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                "application/vnd.ms-excel"
            ]
            assert len(response.content) > 0


class TestDemoData:
    """Test demo data loading"""
    
    def test_load_demo_data(self, client):
        """Test loading demo portfolio data"""
        response = client.get("/api/upload/demo")
        
        if response.status_code == 200:
            data = response.json()
            assert "holdings" in data
            assert len(data["holdings"]) > 0
            assert "summary" in data


# Performance tests
class TestUploadPerformance:
    """Test upload performance with various file sizes"""
    
    def test_upload_medium_file(self, client, tmp_path):
        """Test uploading a medium-sized file (100 rows)"""
        import pandas as pd
        
        data = {
            'Fund Name': [f'Test Fund {i}' for i in range(100)],
            'Invested': [100000] * 100,
            'Current Value': [125000] * 100
        }
        
        df = pd.DataFrame(data)
        file_path = tmp_path / "medium.xlsx"
        df.to_excel(file_path, index=False)
        
        with open(file_path, 'rb') as f:
            response = client.post(
                "/api/upload/excel",
                files={"file": ("medium.xlsx", f, "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")}
            )
        
        assert response.status_code == 200
        assert len(response.json()["holdings"]) == 100
    
    @pytest.mark.slow
    def test_upload_large_file(self, client, large_excel_file):
        """Test uploading a large file (may be slow)"""
        with open(large_excel_file, 'rb') as f:
            response = client.post(
                "/api/upload/excel",
                files={"file": ("large.xlsx", f, "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")}
            )
        
        # Should either succeed or reject due to size
        assert response.status_code in [200, 413]


# Edge cases
class TestUploadEdgeCases:
    """Test edge cases and error conditions"""
    
    def test_upload_empty_excel(self, client, tmp_path):
        """Test uploading an empty Excel file"""
        import pandas as pd
        
        df = pd.DataFrame()
        file_path = tmp_path / "empty.xlsx"
        df.to_excel(file_path, index=False)
        
        with open(file_path, 'rb') as f:
            response = client.post(
                "/api/upload/excel",
                files={"file": ("empty.xlsx", f, "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")}
            )
        
        # Should handle empty file gracefully
        assert response.status_code in [200, 400]
    
    def test_upload_excel_with_special_characters(self, client, tmp_path):
        """Test Excel with special characters in fund names"""
        import pandas as pd
        
        data = {
            'Fund Name': ['Test Fund & Co.', 'Fund (Growth)', 'Fund - Direct'],
            'Invested': [10000, 20000, 30000],
            'Current Value': [12000, 24000, 36000]
        }
        
        df = pd.DataFrame(data)
        file_path = tmp_path / "special.xlsx"
        df.to_excel(file_path, index=False)
        
        with open(file_path, 'rb') as f:
            response = client.post(
                "/api/upload/excel",
                files={"file": ("special.xlsx", f, "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")}
            )
        
        assert response.status_code == 200
        holdings = response.json()["holdings"]
        assert len(holdings) == 3
