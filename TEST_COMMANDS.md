# Quick Test Commands for Database & Overlap Analysis

# 1. Initialize Database
cd backend
python scripts/load_holdings_to_db.py

# 2. Test Database Stats
curl http://localhost:8000/api/holdings/stats

# 3. List All Funds
curl http://localhost:8000/api/holdings/

# 4. Get Specific Fund
curl http://localhost:8000/api/holdings/fund/ppfas-flexi-cap

# 5. Test Overlap Analysis
curl -X POST http://localhost:8000/api/holdings/portfolio-overlap \
  -H "Content-Type: application/json" \
  -d "{\"fund_names\": [\"PPFAS Flexi Cap\", \"HDFC Flexi Cap\", \"Axis Bluechip\"]}"

# 6. Weekly Update (after editing JSON)
python scripts/weekly_update.py

# 7. View Update History
python -c "from scripts.weekly_update import get_update_history; get_update_history()"
