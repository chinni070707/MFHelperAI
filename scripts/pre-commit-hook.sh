#!/bin/bash
# Pre-commit hook to run tests before committing
# This ensures no broken code reaches the repository

set -e  # Exit on any error

echo "🔍 Running pre-commit checks..."
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Track if any checks failed
FAILED=0

# 1. Test Database Connection
echo "📊 Testing database connection..."
if python backend/test_db_connection.py; then
    echo -e "${GREEN}✓ Database tests passed${NC}"
else
    echo -e "${RED}✗ Database tests failed${NC}"
    FAILED=1
fi
echo ""

# 2. Run Backend Tests
echo "🧪 Running backend tests..."
cd backend
if python -m pytest tests/ -v --tb=short -x --maxfail=3; then
    echo -e "${GREEN}✓ Backend tests passed${NC}"
else
    echo -e "${RED}✗ Backend tests failed${NC}"
    FAILED=1
fi
cd ..
echo ""

# 3. Check Python syntax for staged files
echo "🐍 Checking Python syntax..."
STAGED_PY_FILES=$(git diff --cached --name-only --diff-filter=ACM | grep '\.py$' || true)
if [ -n "$STAGED_PY_FILES" ]; then
    for file in $STAGED_PY_FILES; do
        if ! python -m py_compile "$file" 2>/dev/null; then
            echo -e "${RED}✗ Syntax error in $file${NC}"
            FAILED=1
        fi
    done
    if [ $FAILED -eq 0 ]; then
        echo -e "${GREEN}✓ Python syntax checks passed${NC}"
    fi
else
    echo "No Python files to check"
fi
echo ""

# Final result
if [ $FAILED -eq 1 ]; then
    echo -e "${RED}❌ Pre-commit checks failed. Please fix the issues before committing.${NC}"
    echo ""
    exit 1
else
    echo -e "${GREEN}✅ All pre-commit checks passed!${NC}"
    echo ""
    exit 0
fi
