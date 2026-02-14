# Database Sync Strategy - Development to Production

## Current Architecture

### Development (Local)
```
backend/data/fund_holdings.json  ← Source of truth
                ↓
Backend API reads JSON directly
                ↓
Frontend fetches from /api/overlap/funds
```

**Key Point:** The app **doesn't use a database for fund holdings** - it reads directly from the JSON file!

### How Data Flows:

1. **Scraping:**
   ```
   scrape_moneycontrol.py → fund_holdings.json (180 funds)
   ```

2. **API Usage:**
   ```
   backend/app/utils/overlap_analyzer.py → Reads fund_holdings.json directly
   ```

3. **Production Deployment:**
   ```
   Git commit → Push → Render/Production pulls latest code
                                    ↓
                       Includes updated fund_holdings.json
   ```

## Sync Options

### Option A: Git-Based Sync (Current/Recommended)
**How it works:**
1. Commit `backend/data/fund_holdings.json` to repository
2. Push to GitHub
3. Production (Render) auto-deploys with new JSON file
4. No database migration needed!

**Commands:**
```bash
# Add the updated data file
git add backend/data/fund_holdings.json

# Commit
git commit -m "Update fund holdings: 98 funds with complete portfolios"

# Push to production
git push origin main
```

**Pros:**
- ✅ Simple - no database migration
- ✅ Automatic with your existing CI/CD
- ✅ Version controlled
- ✅ Works with current architecture

**Cons:**
- ⚠️ Large JSON file increases repo size
- ⚠️ Requires deployment to update data

---

### Option B: Database Migration (Future Enhancement)
If you want to move to a database:

**Steps:**
1. Create fund holdings tables (already exists: `fund_master`)
2. Load JSON data into database
3. Update overlap_analyzer.py to read from DB instead of JSON
4. Sync development → production database

**Script already exists:** `backend/scripts/load_holdings_to_db.py` (needs fixing for correct models)

**Database sync methods:**
- **Render PostgreSQL:** Use `pg_dump` + `pg_restore`
- **Railway/Heroku:** Use their CLI tools
- **Manual:** Export/import SQL dumps

**Pro Tip:** For now, **stick with Option A (JSON + Git)**. It's simpler and matches your current architecture.

---

## Production Deployment Checklist

### Current Setup (JSON-based):

```bash
# 1. Validate data
python backend/scripts/validate_holdings.py

# 2. Check quality 
python backend/scripts/check_data_quality.py

# 3. Commit to Git
git add backend/data/fund_holdings.json
git commit -m "feat: Add 98 high-quality fund portfolios with complete holdings data"

# 4. Push to production
git push origin main

# 5. Verify deployment
# Check: https://your-app.onrender.com/api/overlap/funds
```

### If Moving to Database:

```bash
# 1. Fix load_holdings_to_db.py script (use correct models)
# 2. Load data locally
python backend/scripts/load_holdings_to_db.py

# 3. Test locally
python backend/scripts/check_funds_db.py

# 4. Sync to production database
render pg:backups:url [your-database]  # Get backup URL
# Or use pg_dump + pg_restore

# 5. Update app to read from DB instead of JSON
# (Requires code changes in overlap_analyzer.py)
```

---

## Recommendation

**For now: Use Option A (JSON + Git sync)**

Reasons:
1. ✅ Your app already reads from JSON - no code changes needed
2. ✅ Simple deployment workflow (just git push)
3. ✅ 180 funds × ~40 holdings = ~7,200 data points = manageable JSON size (~2-3MB)
4. ✅ No database migration complexity
5. ✅ Version controlled and trackable

**Future:** Move to database when:
- JSON file grows too large (>5MB)
- Need real-time updates without deployment
- Add user-generated content (user portfolios, etc.)

---

## Quick Answer to Your Question

**Q: How will funds database sync to production?**

**A:** Currently, it doesn't use a database for fund holdings! The App reads `fund_holdings.json` directly.

**To deploy:**
```bash
git add backend/data/fund_holdings.json
git commit -m "Update fund holdings data"
git push origin main
```

Your production environment (Render) will automatically pull the updated JSON file when you push.

**No database migration needed!** 🎉
