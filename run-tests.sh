#!/bin/bash
# Automated test runner for Unix/Linux/Mac

echo "Start: MFHelper Automated Test Suite"
echo "================================="
echo ""

# Check if backend server is running
echo "[CHECK] Checking backend server..."
if curl -s http://localhost:8000/api/health > /dev/null; then
    echo "[OK] Backend server is running"
else
    echo "[ERROR] Backend server is NOT running"
    echo "   Please start it manually: cd backend && python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000"
    exit 1
fi

echo ""

# Check if node_modules exists
if [ ! -d "tests/node_modules" ]; then
    echo "[INSTALL] Installing test dependencies..."
    cd tests && npm install && cd ..
    echo "[OK] Dependencies installed"
    echo ""
fi

# Run Playwright tests
echo "[RUN] Running Playwright E2E tests..."
cd tests
npx playwright test --reporter=list
TEST_RESULT=$?
cd ..

echo ""
if [ $TEST_RESULT -eq 0 ]; then
    echo "[SUCCESS] ALL TESTS PASSED!"
else
    echo "[ERROR] SOME TESTS FAILED"
    echo "   Check the output above for details"
fi

echo ""
echo "[INFO] Test Summary:"
echo "   - Manual Entry Tests"
echo "   - File Upload Tests"
echo "   - Dashboard Core Tests"
echo "   - API Integration Tests"
echo "   - JavaScript Validation"
echo ""

exit $TEST_RESULT
