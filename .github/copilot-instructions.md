# MFHelper - AI Agent Instructions

## Architecture
- **Stack**: FastAPI backend + vanilla HTML/CSS/JS frontend (no React/Vue)
- **Database**: SQLite (local/dev), PostgreSQL (production via Render.com)
- **Migrations**: Alembic - ALWAYS create migrations for schema changes
- **Deployment**: Automatic via Render on `main` push - runs `alembic upgrade head`

## Critical Non-Obvious Patterns

### 1. Light Theme Only (Strict)
- **Never** create dark theme pages - project uses light theme exclusively
- **Always** use CSS variables from `/css/design-system.css` - never hardcode colors
- Primary: `var(--primary-green)` #7FC04C, BG: `var(--bg-primary)`, Text: `var(--text-primary)`

### 2. Standard Navigation (Mandatory)
Every HTML page **must** include exact navbar structure with **this exact order**:
Home → Tools (dropdown) → Goal Planning → Portfolio → Blog → Get Started

Required scripts on every page:
```html
<link rel="stylesheet" href="/css/design-system.css">
<script src="/js/navbar-auth.js" defer></script>
<script src="/js/analytics.js"></script>
<script src="/js/toast.js" defer></script>
```
Copy navbar from `index.html` verbatim - don't modify structure or order.

### 3. Asset Class System (New)
Holdings have `asset_class` field: 'Equity', 'Debt', 'Hybrid', 'Commodity', 'Other'
- Classification logic in `backend/app/services/asset_classifier.py`
- Auto-classified during CAS import via `AssetClassifier.classify(category, fund_name, fund_type)`
- Frontend filters: Equity/Debt/Hybrid/Commodity checkboxes
- **Don't forget** to backfill when adding this to existing portfolios

### 4. Database Migrations (Critical)
```bash
# Create new migration
PYTHONPATH=backend python -m alembic revision -m "description"

# Apply migrations (production auto-runs this)
PYTHONPATH=backend python -m alembic upgrade head

# Verify current version
PYTHONPATH=backend python -m alembic current
```
**All migrations must be idempotent** - check column existence before adding.
Production deployment auto-runs migrations via `build.sh`.

### 5. Data Flows
- **CAS Import**: PDF → casparser → `cas_import.py` → Holdings (with asset_class)
- **Fund Data**: MoneyControl scraper → `fund_holdings.json` (391 funds, 3.5MB)
- **Portfolio Analysis**: Holdings → `portfolio_insights.py` (XIRR, alpha, style detection)
- **Guest Mode**: localStorage only - no server calls, data never saved

## Key Workflows

### Run Backend (Dev)
```bash
cd backend
uvicorn app.main:app --reload --port 8000
```

### Scrape Fund Holdings
```bash
python backend/scripts/scrape_moneycontrol.py --limit 10
```
Selects **largest table** (full portfolio), not top-10 summary.

### Test Classifier
```bash
python backend/test_asset_classifier.py
```

## Common Pitfalls
- ❌ Dark theme - forbidden, use light only
- ❌ Modifying navbar order - must match spec exactly
- ❌ Hardcoded colors - use CSS variables
- ❌ Forgetting `PYTHONPATH=backend` for Alembic
- ❌ Missing asset_class backfill in migrations
- ❌ Non-idempotent migrations (production re-runs on redeploy)

## Reference Files
- Navigation template: `index.html`
- Design system: `css/design-system.css`, `STYLE_GUIDE.md`
- Asset classifier: `backend/app/services/asset_classifier.py`
- Migrations: `alembic/versions/008_add_asset_class_to_holdings.py`
- Deployment: `ASSET_CLASS_DEPLOYMENT.md`, `build.sh`
