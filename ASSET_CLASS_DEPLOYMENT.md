# Asset Class Feature - Production Deployment Guide

## ✅ Automatic Deployment (Recommended)

The asset class feature will **automatically deploy to production** when you push code to `main` branch. Here's how it works:

### **What Happens Automatically:**

1. **Render.com Build Process:**
   ```bash
   # From render.yaml buildCommand:
   cd .. && PYTHONPATH=backend python -m alembic upgrade head
   ```
   - Runs ALL pending Alembic migrations
   - Includes the new migration `008_add_asset_class_to_holdings.py`
   - Creates `asset_class` column
   - Backfills existing holdings
   - Creates index for fast filtering

2. **Idempotent Migration:**
   - Safe to run multiple times
   - Checks if column exists before adding
   - Skips if already applied
   - No errors if run again

3. **Application Startup:**
   - Backend starts with updated models
   - Frontend loads with new filters
   - All features work immediately

---

## 📋 Deployment Checklist

### **Before Push:**
- [x] Alembic migration created: `008_add_asset_class_to_holdings.py`
- [x] Migration is idempotent (safe to re-run)
- [x] Frontend updated with asset class filters
- [x] AssetClassifier service created
- [x] CAS import integrated with classifier
- [x] Local testing completed

### **To Deploy:**
```bash
# 1. Commit all changes
git add .
git commit -m "feat: Add asset class classification (Equity/Debt/Hybrid/Commodity)"

# 2. Push to main
git push origin main

# 3. Render automatically:
#    - Runs build.sh
#    - Executes: python -m alembic upgrade head
#    - Starts backend with new code
#    - Migration runs successfully
```

### **Verify Deployment:**
1. Check Render logs for:
   ```
   [MIGRATE] Running database migrations...
   INFO Running upgrade 007_add_broker -> 008_asset_class
   ✓ Added asset_class column
   ✓ Created index on asset_class
   ✓ Backfilled X holdings
   ```

2. Open production dashboard
3. Import a CAS file (or use existing portfolio)
4. Check for:
   - 🎯 Asset Class Allocation chart visible
   - Asset class filters working (Equity/Debt/Hybrid/Commodity)
   - Holdings properly classified

---

## 🔧 Manual Deployment (If Needed)

### **If Automatic Migration Fails:**

```bash
# SSH into Render server or run locally for production DB
PYTHONPATH=backend python -m alembic upgrade head
```

### **Check Migration Status:**
```bash
# See current version
PYTHONPATH=backend python -m alembic current

# See pending migrations
PYTHONPATH=backend python -m alembic history

# Expected output:
# 007_add_broker (head)  -> 008_asset_class
```

### **Rollback (Emergency Only):**
```bash
# Rollback one version
PYTHONPATH=backend python -m alembic downgrade -1

# Rollback to specific version
PYTHONPATH=backend python -m alembic downgrade 007_add_broker
```

---

## 🎯 What Gets Deployed

### **Backend Changes:**
1. **Database Schema:**
   - `holdings.asset_class` column (VARCHAR(20), default='Equity')
   - `idx_holding_asset_class` index on (asset_class, user_id)

2. **New Service:**
   - `backend/app/services/asset_classifier.py`
   - AssetClassifier with smart classification logic

3. **CAS Import Enhancement:**
   - Auto-classifies funds during import
   - Stores asset_class with each holding

4. **Migration Script:**
   - `alembic/versions/008_add_asset_class_to_holdings.py`
   - Runs automatically on deploy

### **Frontend Changes:**
1. **Asset Allocation Chart:**
   - Donut chart showing Equity/Debt/Hybrid/Commodity split
   - Summary cards with percentages

2. **Enhanced Filters:**
   - Fund Type: Direct | Regular
   - Asset Class: 📈 Equity | 🏦 Debt | ⚖️ Hybrid | 🥇 Commodity
   - Real-time filtering

3. **Dashboard Updates:**
   - `renderAssetClassChart()` function
   - Updated `filterHoldings()` logic
   - New filter UI components

---

## 📊 How Classification Works

### **During CAS Import:**
```
1. User uploads CAS PDF
2. Parser extracts fund details
3. AssetClassifier.classify() determines asset class based on:
   - Commodity keywords (gold, silver) → Commodity
   - Category (Liquid, Debt, Gilt) → Debt
   - Category (Hybrid, Balanced) → Hybrid
   - Everything else → Equity
4. Stored in holdings.asset_class
```

### **Classification Examples:**
| Fund Name | Category | Asset Class |
|-----------|----------|-------------|
| HDFC Top 100 Fund | Large Cap | **Equity** |
| ICICI Liquid Fund | Liquid | **Debt** |
| HDFC Balanced Advantage | Hybrid | **Hybrid** |
| SBI Gold ETF | ETF | **Commodity** |

---

## 🧪 Testing in Production

### **After Deployment:**

1. **Test New CAS Import:**
   ```
   1. Upload CAS PDF
   2. Check asset_class is populated for each holding
   3. Verify filters work correctly
   4. Confirm chart displays properly
   ```

2. **Test Existing Data:**
   ```
   1. Open existing portfolio
   2. Holdings should be backfilled with asset_class
   3. Filters should work immediately
   4. Chart should show distribution
   ```

3. **Test Edge Cases:**
   ```
   - Gold/Silver ETFs → Commodity
   - Debt funds → Debt
   - Hybrid funds → Hybrid
   - Unknown funds → Equity (default)
   ```

---

## 🔍 Monitoring & Debugging

### **Check Migration Applied:**
```sql
-- In production database
PRAGMA table_info(holdings);
-- Should show 'asset_class' column

SELECT DISTINCT asset_class, COUNT(*) 
FROM holdings 
GROUP BY asset_class;
-- Should show distribution
```

### **Check Logs:**
```bash
# Render logs
Render Dashboard → Service → Logs

# Look for:
[MIGRATE] Running database migrations...
INFO Running upgrade 007_add_broker -> 008_asset_class
✓ Added asset_class column
✓ Backfilled X holdings
```

### **Common Issues:**

**1. Migration doesn't run:**
- Check render.yaml has alembic command
- Verify PYTHONPATH=backend is set
- Check build logs for errors

**2. Column exists error:**
- Migration is now idempotent
- Will skip if column exists
- No action needed

**3. Classification seems wrong:**
- Check AssetClassifier logic
- Fund names/categories may need adjustment
- Can backfill manually if needed

---

## 📈 Future Enhancements

### **Planned Features:**
1. **Asset-wise XIRR:**
   - Calculate returns per asset class
   - Show "Equity returned 15%, Debt returned 7%"

2. **Asset Allocation Rebalancing:**
   - Set target: "60% Equity, 30% Debt, 10% Hybrid"
   - Get recommendations to rebalance

3. **Debt Fund Analysis:**
   - Duration metrics
   - Credit risk analysis
   - Maturity profiles

### **To Implement:**
```bash
# Create new migration
python -m alembic revision -m "Add duration to debt funds"

# Edit:
alembic/versions/009_add_debt_metrics.py

# Deploy automatically on next push
```

---

## 🚀 Quick Reference

### **Deploy Commands:**
```bash
# Full deployment
git add . && git commit -m "feat: Asset class" && git push origin main

# Check migration status
PYTHONPATH=backend python -m alembic current

# Run migrations manually
PYTHONPATH=backend python -m alembic upgrade head

# Test classifier
python backend/test_asset_classifier.py
```

### **Key Files:**
- Migration: `alembic/versions/008_add_asset_class_to_holdings.py`
- Classifier: `backend/app/services/asset_classifier.py`
- Model: `backend/app/models/models.py` (Holding.asset_class)
- Frontend: `frontend/dashboard.html` (filters + chart)

---

## ✅ Success Criteria

**Deployment is successful when:**
- [x] Migration runs without errors
- [x] asset_class column exists in holdings table
- [x] Existing holdings backfilled with classifications
- [x] Asset allocation chart displays on dashboard
- [x] Filters work (Equity/Debt/Hybrid/Commodity)
- [x] New CAS imports classify funds automatically
- [x] No errors in Render logs

---

**Version:** 1.0  
**Last Updated:** February 14, 2026  
**Migration Version:** 008_asset_class
