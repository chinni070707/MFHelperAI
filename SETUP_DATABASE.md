# 🚀 Setup Instructions - Database & Overlap Analysis

## Prerequisites

- Python 3.10+
- SQLite (included with Python)
- FastAPI backend running

---

## Step 1: Install Dependencies

```bash
cd backend
pip install -r requirements.txt
```

---

## Step 2: Initialize Database

### Option A: Fresh Setup (First Time)

```bash
cd backend
python scripts/load_holdings_to_db.py
```

This will:
- Create `mfhelper.db` SQLite database
- Load all fund holdings from `data/fund_holdings.json`
- Create necessary tables

**Output:**
```
🚀 Starting fund holdings database migration...
📊 Loading: Parag Parikh Flexi Cap Fund
📊 Loading: HDFC Flexi Cap Fund
...
✅ Successfully loaded 10 funds into database
📈 Total holdings: 100
📊 Total sectors: 60
✅ Migration complete!
```

### Option B: Update Existing Database

```bash
cd backend
python scripts/weekly_update.py
```

Use this for weekly updates after editing `data/fund_holdings.json`.

---

## Step 3: Start the Backend

```bash
cd backend
uvicorn app.main:app --reload
```

Server will start at: `http://localhost:8000`

---

## Step 4: Test the Overlap API

### Test 1: List All Funds

```bash
curl http://localhost:8000/api/holdings/
```

**Response:**
```json
{
  "total": 10,
  "last_updated": "2026-01-29T...",
  "funds": [...]
}
```

### Test 2: Get Fund Details

```bash
curl http://localhost:8000/api/holdings/fund/ppfas-flexi-cap
```

### Test 3: Analyze Overlap

```bash
curl -X POST http://localhost:8000/api/holdings/portfolio-overlap \
  -H "Content-Type: application/json" \
  -d '{"fund_names": ["PPFAS Flexi Cap", "HDFC Flexi Cap"]}'
```

**Response:**
```json
{
  "summary": {
    "overlap_percentage": 62.5,
    "total_stocks": 16,
    "overlapping_stocks_count": 10,
    "alerts_count": 2
  },
  "top_overlaps": [...],
  "alerts": [...]
}
```

---

## Step 5: Open Dashboard

1. Navigate to: `http://localhost:8000/dashboard`
2. Upload your portfolio or use demo data
3. Click "📊 Analyze Overlap" button
4. See overlap analysis with heatmap!

---

## Weekly Update Process

### Manual Update (Every Week/Month)

1. **Update the JSON file** with latest holdings:
   ```bash
   # Edit backend/data/fund_holdings.json
   # Add new funds or update existing ones
   ```

2. **Run update script:**
   ```bash
   cd backend
   python scripts/weekly_update.py
   ```

3. **Verify:**
   ```bash
   curl http://localhost:8000/api/holdings/stats
   ```

### Automated Update (GitHub Actions)

The `.github/workflows/weekly-update.yml` workflow will:
- Run every Sunday at 2 AM UTC
- Update database from JSON
- Commit changes automatically

**To enable:**
1. Push your code to GitHub
2. Workflow runs automatically
3. Check Actions tab for logs

---

## Database Schema

### Tables Created:

1. **fund_master** - Fund information
   - id, fund_key, fund_name, amc, category
   - isin, scheme_code, created_at, updated_at

2. **fund_holdings** - Stock holdings
   - id, fund_id, stock_name, weight, sector
   - as_of_date, created_at

3. **fund_sector_allocation** - Sector allocations
   - id, fund_id, sector, weight
   - as_of_date, created_at

4. **data_update_log** - Update history
   - id, update_type, source, funds_updated
   - status, error_message, started_at, completed_at

---

## File Structure

```
MFHelper/
├── backend/
│   ├── app/
│   │   ├── main.py                    # API entry point
│   │   ├── models/
│   │   │   └── fund_holdings.py       # Database models
│   │   └── routes/
│   │       ├── holdings.py            # Overlap API
│   │       └── errors.py              # Error logging
│   ├── data/
│   │   └── fund_holdings.json         # Holdings data
│   ├── scripts/
│   │   ├── load_holdings_to_db.py     # Initial migration
│   │   └── weekly_update.py           # Weekly updater
│   ├── mfhelper.db                    # SQLite database (created)
│   └── requirements.txt
├── frontend/
│   ├── js/
│   │   ├── overlap.js                 # Overlap analyzer
│   │   ├── toast.js                   # Toast notifications
│   │   ├── errorHandler.js            # Error handling
│   │   └── responsive.js              # Responsive utils
│   └── dashboard.html                 # Main dashboard
└── .github/
    └── workflows/
        └── weekly-update.yml          # Automated updates
```

---

## Troubleshooting

### Error: "No module named 'app.models.fund_holdings'"

**Solution:**
```bash
cd backend
python scripts/load_holdings_to_db.py
```

### Error: "Fund not found"

**Solution:**
Check fund names in database:
```bash
curl http://localhost:8000/api/holdings/
```

Use exact fund names or partial matches work too.

### Database locked error

**Solution:**
Stop all running processes and try again:
```bash
pkill -f uvicorn
python scripts/weekly_update.py
```

### Empty overlap results

**Solution:**
Make sure you have at least 2 funds:
```bash
# Check holdings count
curl http://localhost:8000/api/holdings/stats
```

---

## Adding New Funds

1. **Edit JSON file:**
   ```json
   {
     "funds": {
       "new-fund-key": {
         "name": "New Fund Name",
         "amc": "AMC Name",
         "category": "Flexi Cap",
         "holdings": [
           {"stock": "HDFC Bank", "weight": 8.5, "sector": "Banking"},
           ...
         ],
         "sector_allocation": {
           "Banking": 25,
           ...
         }
       }
     }
   }
   ```

2. **Update database:**
   ```bash
   python scripts/weekly_update.py
   ```

3. **Verify:**
   ```bash
   curl http://localhost:8000/api/holdings/fund/new-fund-key
   ```

---

## Performance Tips

1. **SQLite is fast** - No need for PostgreSQL initially
2. **Database is cached** - Restart backend if you update DB externally
3. **JSON fallback** - If DB fails, can fallback to JSON
4. **Weekly updates sufficient** - Fund holdings change monthly

---

## Next Steps

- [ ] Set up automated weekly updates
- [ ] Add more funds to database (target 50-100)
- [ ] Implement sector overlap visualization
- [ ] Add export overlap report feature
- [ ] Create admin panel for data management

---

**Questions? Check:**
- [DATA_STRATEGY.md](DATA_STRATEGY.md) - Data sources guide
- [FEATURES.md](FEATURES.md) - Feature documentation
- API docs: http://localhost:8000/api/docs

---

*Database-powered overlap analysis is ready! 🎉*
