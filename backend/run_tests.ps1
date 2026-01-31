# Test runner script for MFHelper API tests

# Run all tests
Write-Host "Running all tests..." -ForegroundColor Cyan
pytest

# Run specific test files
# pytest tests/test_upload.py
# pytest tests/test_portfolio.py
# pytest tests/test_analytics.py
# pytest tests/test_rebalance.py

# Run with coverage
# pytest --cov=app --cov-report=html --cov-report=term

# Run only fast tests (excluding slow)
# pytest -m "not slow"

# Run specific test class
# pytest tests/test_upload.py::TestUploadExcel

# Run specific test function
# pytest tests/test_upload.py::TestUploadExcel::test_upload_valid_excel_file

# Run tests in parallel (requires pytest-xdist)
# pytest -n auto

# Run tests with verbose output
# pytest -vv

# Run tests and stop on first failure
# pytest -x

# Generate HTML report
# pytest --html=report.html --self-contained-html
