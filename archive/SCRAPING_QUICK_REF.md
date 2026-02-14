# Enhanced Scraping - Quick Reference

## 🚀 Quick Start

```bash
# Test run (5 funds)
python backend/scripts/scrape_moneycontrol.py --test

# Scrape 50 funds
python backend/scripts/scrape_moneycontrol.py --limit 50

# Scrape all remaining
python backend/scripts/scrape_moneycontrol.py

# Force rescrape
python backend/scripts/scrape_moneycontrol.py --force
```

## 📊 Current Status

- **Total Funds Available:** 346
- **Already Scraped:** 98 funds ✅
- **Remaining:** 248 funds
- **Success Rate:** ~60-70% (some funds lack portfolio pages)

## 📝 Track Progress

View live progress: `backend/scripts/scraping_todo.md`

## ✅ Complete Workflow

```bash
# 1. Scrape
python backend/scripts/scrape_moneycontrol.py --limit 50

# 2. Validate
python backend/scripts/validate_holdings.py

# 3. Load to DB
python backend/scripts/load_holdings_to_db.py

# 4. Verify
python backend/validate_funds_data.py
```

## 🎯 Key Features

✅ Smart skip (checks JSON + database)  
✅ Progress tracking (updates every 10 funds)  
✅ Error handling (403/404/500 handled)  
✅ Rate limiting (2 sec delay)  
✅ Retry tracking (failed funds logged)

## ⚠️ Known Issues

- Some funds return 403 (they don't have portfolio pages)
- Solution: Script handles gracefully, continues with others

## 📈 Next Steps

1. Run scraper with `--limit 50`
2. Check `scraping_todo.md` for results
3. Validate and load to database
4. Repeat until all working funds scraped

**Full details:** See `SCRAPING_IMPLEMENTATION_COMPLETE.md`
