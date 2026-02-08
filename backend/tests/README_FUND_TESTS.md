# Fund Data Validation Tests

## Overview
Comprehensive test suite for validating mutual fund master data integrity.

## Test Coverage
Current coverage: **70.27%** for `app/utils/data_validator.py`

## Running Tests

### Run All Fund Data Tests
```bash
cd backend
pytest tests/test_fund_data_sanity.py -v
```

### Run with Coverage
```bash
cd backend
pytest tests/test_fund_data_sanity.py -v --cov=app/utils/data_validator --cov-report=term-missing --cov-report=html
```

### View HTML Coverage Report
After running tests with coverage, open:
```
backend/htmlcov/index.html
```

### Run All Tests
The fund data tests will automatically run when you run the full test suite:
```bash
cd backend
pytest -v
```

Or with coverage for entire app:
```bash
cd backend
pytest -v --cov=app --cov-report=html
```

## Test Suite

### TestFundDataSanity
Tests data integrity and validation:

1. **test_data_exists** - Verifies fund data exists in database
2. **test_amc_data_exists** - Validates AMC (fund house) data
3. **test_each_amc_has_funds** - Ensures each AMC has associated funds
4. **test_fund_has_required_fields** - Checks required fields are present
5. **test_no_duplicate_scheme_codes** - Detects duplicate scheme codes
6. **test_nav_values_valid** - Validates NAV (Net Asset Value) ranges
7. **test_expense_ratio_valid** - Checks expense ratios are reasonable
8. **test_returns_data_valid** - Validates return percentages
9. **test_categories_valid** - Ensures fund categories are valid
10. **test_plan_type_valid** - Validates plan types (Direct/Regular)
11. **test_amc_names_consistent** - Checks AMC naming consistency
12. **test_comprehensive_validation** - Runs all validation checks together

### TestFundDataQueries
Tests fund search and filtering:

13. **test_search_funds_by_name** - Tests fund name search
14. **test_filter_by_amc** - Tests filtering by AMC
15. **test_filter_by_category** - Tests filtering by category

## Continuous Integration

### Automatic Test Execution
Tests are automatically discovered by pytest because:
- Test files follow naming pattern: `test_*.py`
- Test classes start with: `Test*`
- Test methods start with: `test_*`

### Pre-configured in pyproject.toml
```toml
[tool.pytest.ini_options]
testpaths = ["tests"]
python_files = ["test_*.py"]
python_classes = ["Test*"]
python_functions = ["test_*"]
```

## Coverage Configuration

### Current Setup
- Coverage target: `app/` directory
- Reports: HTML + Terminal
- Branch coverage: Enabled
- Minimum coverage: Not enforced (can be added)

### Viewing Coverage in VS Code
1. Install "Coverage Gutters" extension
2. Run tests with coverage
3. Click "Watch" in status bar to see coverage inline

## Test Data

### Sample Data Fixture
Tests use `sample_fund_data` fixture which creates:
- 10 test funds
- 5 unique AMCs (HDFC, ICICI, SBI, Axis, Single Fund AMC)
- Multiple categories (Equity, Liquid, Hybrid, Debt)
- Both Direct and Regular plans
- Active and inactive funds

### Real Data Testing
To test against real production data:
```bash
cd backend
python fetch_fund_data.py  # Load real data
python validate_funds_data.py  # Validate
```

## Markers

### Available Test Markers
```bash
# Run only slow tests
pytest -m slow

# Skip slow tests
pytest -m "not slow"

# Run only unit tests
pytest -m unit

# Run only integration tests
pytest -m integration
```

## Quick Commands

```bash
# Run just fund data tests
pytest tests/test_fund_data_sanity.py

# Run with verbose output
pytest tests/test_fund_data_sanity.py -v

# Run specific test
pytest tests/test_fund_data_sanity.py::TestFundDataSanity::test_data_exists

# Run tests and stop on first failure
pytest tests/test_fund_data_sanity.py -x

# Run tests in parallel (requires pytest-xdist)
pytest tests/test_fund_data_sanity.py -n auto
```

## Coverage Goals

| Module | Current | Target |
|--------|---------|--------|
| data_validator.py | 70.27% | 85% |
| Overall app/ | 27.79% | 80% |

## Contributing

When adding new validation logic:
1. Add validation method to `FundDataValidator`
2. Add corresponding test to `TestFundDataSanity`
3. Update sample data if needed
4. Run tests with coverage to ensure >80% coverage
5. Update this README if adding new tests
