#!/usr/bin/env bash
# Render.com Build Script for MFHelper
# This script runs during the build phase on Render

set -o errexit  # Exit on error
set -o nounset  # Exit on undefined variable

echo "Start: Starting MFHelper build process..."

# Upgrade pip to latest version
echo "[INSTALL] Upgrading pip..."
pip install --upgrade pip

# Install Python dependencies
echo "[INSTALL] Installing Python dependencies from requirements.txt..."
cd backend
pip install -r requirements.txt

# Verify critical packages
echo "[OK] Verifying installation..."
python -c "import fastapi; print(f'FastAPI: {fastapi.__version__}')"
python -c "import sqlalchemy; print(f'SQLAlchemy: {sqlalchemy.__version__}')"
python -c "import psycopg2; print(f'psycopg2: {psycopg2.__version__}')"

# Run database migrations
echo "[MIGRATE] Running database migrations..."
cd ..
PYTHONPATH=backend python -m alembic upgrade head
cd backend

echo "[SUCCESS] Build completed successfully!"
