#!/bin/bash
# Production Cleanup Script
# Removes unnecessary files from production deployment to reduce disk usage

set -e  # Exit on error

echo "====================================="
echo "Starting Production Cleanup..."
echo "====================================="

# Get the deployment directory
DEPLOY_DIR="${DEPLOY_DIR:-/opt/render/project/src}"
cd "$DEPLOY_DIR"

echo ""
echo "Current directory: $(pwd)"
echo "Initial disk usage:"
du -sh . 2>/dev/null || echo "Unable to calculate"

# Files to remove
echo ""
echo "Removing test/demo data files..."
rm -f backend/cas_extracted_text.txt 2>/dev/null && echo "  ✓ Removed cas_extracted_text.txt" || echo "  - cas_extracted_text.txt not found"
rm -f backend/cas_parsed_data.json 2>/dev/null && echo "  ✓ Removed cas_parsed_data.json" || echo "  - cas_parsed_data.json not found"
rm -f backend/cas_parsed_nsdl.json 2>/dev/null && echo "  ✓ Removed cas_parsed_nsdl.json" || echo "  - cas_parsed_nsdl.json not found"
rm -f backend/kfintech_cas_parsed.json 2>/dev/null && echo "  ✓ Removed kfintech_cas_parsed.json" || echo "  - kfintech_cas_parsed.json not found"

# Remove old/backup HTML files
echo ""
echo "Removing backup HTML files..."
rm -f frontend/dashboard-old-backup.html 2>/dev/null && echo "  ✓ Removed dashboard-old-backup.html" || echo "  - dashboard-old-backup.html not found"
rm -f frontend/index-old.html 2>/dev/null && echo "  ✓ Removed index-old.html" || echo "  - index-old.html not found"
rm -f frontend/index-old-backup.html 2>/dev/null && echo "  ✓ Removed index-old-backup.html" || echo "  - index-old-backup.html not found"
rm -f frontend/goal-planning-backup.html 2>/dev/null && echo "  ✓ Removed goal-planning-backup.html" || echo "  - goal-planning-backup.html not found"
rm -f frontend/life_financial_planner_reference.html 2>/dev/null && echo "  ✓ Removed life_financial_planner_reference.html" || echo "  - life_financial_planner_reference.html not found"
rm -f frontend/icon-styles-demo.html 2>/dev/null && echo "  ✓ Removed icon-styles-demo.html" || echo "  - icon-styles-demo.html not found"
rm -f frontend/index-ai.html 2>/dev/null && echo "  ✓ Removed index-ai.html" || echo "  - index-ai.html not found"

# Remove reference files
echo ""
echo "Removing reference files..."
rm -f acorns_site.css 2>/dev/null && echo "  ✓ Removed acorns_site.css" || echo "  - acorns_site.css not found"
rm -f acorns_source.html 2>/dev/null && echo "  ✓ Removed acorns_source.html" || echo "  - acorns_source.html not found"

# Remove unnecessary documentation in production
echo ""
echo "Removing development documentation..."
rm -rf doc/ 2>/dev/null && echo "  ✓ Removed doc/ directory" || echo "  - doc/ directory not found"
rm -rf docs/ 2>/dev/null && echo "  ✓ Removed docs/ directory" || echo "  - docs/ directory not found"

# Remove test scripts
echo ""
echo "Removing test scripts..."
rm -f backend/test_*.py 2>/dev/null && echo "  ✓ Removed backend test files" || echo "  - No backend test files found"
rm -f test_*.py 2>/dev/null && echo "  ✓ Removed root test files" || echo "  - No root test files found"
rm -rf tests/ 2>/dev/null && echo "  ✓ Removed tests/ directory" || echo "  - tests/ directory not found"

# Remove PowerShell scripts (not needed on Linux)
echo ""
echo "Removing Windows-specific files..."
rm -f scripts/*.ps1 2>/dev/null && echo "  ✓ Removed PowerShell scripts" || echo "  - No PowerShell scripts found"
rm -f backend/*.ps1 2>/dev/null && echo "  ✓ Removed backend PowerShell scripts" || echo "  - No backend PowerShell scripts found"

# Remove git files (not needed in production)
echo ""
echo "Removing git-related files..."
rm -rf .git* 2>/dev/null && echo "  ✓ Removed .git directory" || echo "  - .git directory not found"
rm -f .gitignore 2>/dev/null && echo "  ✓ Removed .gitignore" || echo "  - .gitignore not found"

# Remove IDE files
echo ""
echo "Removing IDE configuration files..."
rm -f *.code-workspace 2>/dev/null && echo "  ✓ Removed workspace files" || echo "  - No workspace files found"
rm -rf .vscode/ 2>/dev/null && echo "  ✓ Removed .vscode directory" || echo "  - .vscode directory not found"
rm -rf .idea/ 2>/dev/null && echo "  ✓ Removed .idea directory" || echo "  - .idea directory not found"
rm -rf .claude/ 2>/dev/null && echo "  ✓ Removed .claude directory" || echo "  - .claude directory not found"

# Remove Python cache
echo ""
echo "Removing Python cache files..."
find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null && echo "  ✓ Removed __pycache__ directories" || echo "  - No __pycache__ directories found"
find . -type f -name "*.pyc" -delete 2>/dev/null && echo "  ✓ Removed .pyc files" || echo "  - No .pyc files found"
find . -type f -name "*.pyo" -delete 2>/dev/null && echo "  ✓ Removed .pyo files" || echo "  - No .pyo files found"

# Remove coverage files
echo ""
echo "Removing coverage files..."
rm -rf htmlcov/ 2>/dev/null && echo "  ✓ Removed htmlcov directory" || echo "  - htmlcov directory not found"
rm -f .coverage* 2>/dev/null && echo "  ✓ Removed coverage files" || echo "  - No coverage files found"

# Clean up frontend build artifacts
echo ""
echo "Removing frontend build artifacts..."
rm -rf frontend/www/ 2>/dev/null && echo "  ✓ Removed frontend/www directory" || echo "  - frontend/www directory not found"
rm -rf frontend/node_modules/ 2>/dev/null && echo "  ✓ Removed node_modules" || echo "  - node_modules not found"
rm -f frontend/package-lock.json 2>/dev/null && echo "  ✓ Removed package-lock.json" || echo "  - package-lock.json not found"

echo ""
echo "====================================="
echo "Cleanup Complete!"
echo "====================================="
echo ""
echo "Final disk usage:"
du -sh . 2>/dev/null || echo "Unable to calculate"
echo ""
echo "Space saved by removing unnecessary files."
echo "Production deployment is now optimized."
