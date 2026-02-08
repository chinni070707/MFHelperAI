# Test Suite for New Features

## Overview
Comprehensive test suite for demo portfolio, funds list, user leads, and frontend components.

## Backend Tests

### Test Files
- `test_demo_portfolio.py` - Demo portfolio API tests
- `test_funds_api.py` - Funds list and search API tests
- `test_user_leads.py` - User leads capture tests

### Running Backend Tests
```bash
cd backend
pytest tests/test_demo_portfolio.py -v
pytest tests/test_funds_api.py -v
pytest tests/test_user_leads.py -v

# Run all backend tests
pytest tests/ -v
```

## Frontend Tests

### Test Files
- `portfolio-storage.test.js` - PortfolioStorage class tests

### Running Frontend Tests
```bash
cd frontend
npm test

# Or with Jest
npx jest tests/portfolio-storage.test.js
```

## Integration Tests

### Test File
- `test_integration.py` - Selenium-based end-to-end tests

### Prerequisites
```bash
pip install selenium pytest
# Download ChromeDriver for your Chrome version
```

### Running Integration Tests
```bash
# Start backend server first
cd backend
python -m uvicorn app.main:app --reload &

# Run integration tests
cd ../tests
pytest test_integration.py -v -s
```

## Test Coverage

### Backend API Tests
- ✅ Demo portfolio seeding and retrieval
- ✅ Portfolio totals calculation
- ✅ Inactive holdings filtering
- ✅ Funds list with pagination
- ✅ Fund search and filtering
- ✅ Category and AMC filtering
- ✅ Dropdown format response
- ✅ User leads capture
- ✅ Duplicate lead handling
- ✅ Rate limiting

### Frontend Tests
- ✅ Portfolio mode management
- ✅ Demo data save/load
- ✅ Guest data save/load
- ✅ Expiry detection
- ✅ Data migration
- ✅ localStorage persistence

### Integration Tests
- ✅ Homepage load
- ✅ Demo portfolio flow
- ✅ Portfolio source modal
- ✅ Manual entry form
- ✅ Fund search autocomplete
- ✅ Export email gate
- ✅ Signup modal
- ✅ Conversion prompts
- ✅ Guest mode banner
- ✅ Complete user flow
- ✅ localStorage persistence

## Manual Testing Checklist

### 1. Homepage Flow
- [ ] Load homepage
- [ ] Click "Try Demo" button
- [ ] Verify redirect to dashboard
- [ ] Check demo banner appears
- [ ] Click "Add Your Portfolio"
- [ ] Verify upload/manual entry options

### 2. Demo Portfolio
- [ ] Demo data loads automatically
- [ ] Demo banner shows with "Sign Up" button
- [ ] Click "Sign Up" from banner
- [ ] Verify signup modal opens
- [ ] Dismiss banner and check session persistence

### 3. Manual Entry
- [ ] Open manual entry modal
- [ ] Type fund name
- [ ] Verify autocomplete dropdown appears
- [ ] Select a fund from dropdown
- [ ] Enter amount
- [ ] Add another fund
- [ ] Save portfolio
- [ ] Verify guest mode banner appears

### 4. Guest Mode
- [ ] Save portfolio without auth
- [ ] Verify guest banner shows expiry days
- [ ] Refresh page
- [ ] Check data persists
- [ ] Click "Sign Up to Save"
- [ ] Verify signup modal opens

### 5. Conversion Prompts
- [ ] Wait 2 minutes in demo mode
- [ ] Check progress prompt appears
- [ ] Dismiss prompt
- [ ] Click 3 different features
- [ ] Check feature prompt appears
- [ ] Wait 5 minutes
- [ ] Check timed prompt appears

### 6. Export Email Gate
- [ ] Clear auth token
- [ ] Click export button
- [ ] Verify email modal appears
- [ ] Enter email
- [ ] Check lead captured in backend
- [ ] Try export again
- [ ] Verify email not requested again

### 7. Authentication
- [ ] Click signup
- [ ] Fill form with valid data
- [ ] Submit
- [ ] Verify token saved
- [ ] Check user lead created
- [ ] Logout
- [ ] Try login
- [ ] Verify successful login

### 8. Fund Search
- [ ] Open manual entry
- [ ] Type "HDFC" in fund search
- [ ] Verify results appear
- [ ] Select a fund
- [ ] Verify name populated
- [ ] Clear and search "Debt"
- [ ] Verify category filtering works

## Test Data

### Sample Demo Portfolio
```json
[
  {
    "scheme_name": "HDFC Equity Fund - Direct Growth",
    "scheme_code": "HDFC001",
    "units": 100,
    "avg_cost": 500,
    "current_nav": 600,
    "amc": "HDFC Mutual Fund",
    "category": "Equity"
  }
]
```

### Sample Fund Data
```json
{
  "scheme_name": "ICICI Prudential Balanced Advantage Fund",
  "scheme_code": "ICICI-BAF-D",
  "amc": "ICICI Prudential Mutual Fund",
  "category": "Hybrid",
  "current_nav": 45.67,
  "plan_type": "Direct"
}
```

## Known Issues / Notes
- Rate limiting tests may be flaky depending on system clock
- Integration tests require Chrome/ChromeDriver installed
- Selenium tests run in headless mode by default
- Some timers (5 min prompts) are tested by triggering manually

## Continuous Integration
Add to CI/CD pipeline:
```yaml
- name: Run Backend Tests
  run: |
    cd backend
    pytest tests/ -v --cov=app --cov-report=html
    
- name: Run Frontend Tests
  run: |
    cd frontend
    npm test -- --coverage
```
