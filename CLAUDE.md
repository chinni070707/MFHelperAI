# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this project is

MFHelper is a mutual fund portfolio analytics web app for Indian investors. Users upload a CAS PDF (Consolidated Account Statement from CAMS/KFintech) or an Excel file to see portfolio analytics, XIRR, fund overlap, rebalancing suggestions, and goal planning.

**Stack:** FastAPI (Python 3.11) · SQLAlchemy 2.0 · SQLite (dev) / PostgreSQL (prod) · Vanilla JS + TypeScript · Vite · Plotly.js · Render.com deployment

---

## Commands

### Backend

```powershell
# Windows — activate venv first
cd backend
.\venv\Scripts\Activate.ps1

# Dev server (auto-reload)
uvicorn app.main:app --reload --port 8000

# Run all tests
pytest tests/ -v

# Run single test file
pytest tests/test_portfolio.py -v

# With coverage
pytest tests/ --cov=app --cov-report=html

# Database migrations
alembic upgrade head          # apply all pending
alembic downgrade -1          # rollback one
alembic revision --autogenerate -m "description"   # new migration
```

API docs (Swagger): `http://localhost:8000/api/docs`

### Frontend

```bash
cd frontend
npm install
npm run dev          # Vite dev server on :3000
npm run build        # TypeScript + Vite build to www/
npm run type-check   # TSC validation only
npm run build:goals  # ESBuild bundle for goal-planning (esbuild.goal-planning.mjs)
```

The frontend is served as static files from FastAPI in production — no separate frontend server. In dev, use Vite on :3000 hitting the backend on :8000.

### E2E Tests (Playwright)

```bash
cd frontend
npm run test                    # all Playwright tests
npm run test:auth               # auth flow only
npm run test:upload             # CAS upload flow
npm run test:report             # open HTML report
npx playwright test --headed    # show browser
```

### One-command startup (Windows)

```powershell
.\startup.ps1                   # start Ollama + backend + open browser
.\startup.ps1 -ForceKill        # kill existing port 8000 first
```

---

## Architecture

### Request flow

```
Browser → FastAPI (main.py)
              ├── /api/auth/*        → routes/auth.py      (JWT login, signup, OAuth, settings)
              ├── /api/upload/cas    → routes/upload.py     (CAS PDF upload — primary user entry)
              ├── /api/upload/excel  → routes/upload.py
              ├── /api/portfolio/*   → routes/portfolio.py  (CRUD, history, snapshots)
              ├── /api/demo/*        → routes/demo.py       (unauthenticated demo data)
              ├── /api/funds/*       → routes/funds.py      (fund search/autocomplete)
              ├── /api/analytics/*   → routes/analytics.py
              ├── /api/overlap/*     → routes/overlap.py
              ├── /api/rebalance/*   → routes/rebalance.py
              ├── /api/xirr/*        → routes/xirr.py
              ├── /api/ai/*          → routes/ai.py         (Ollama / OpenAI chatbot)
              └── /static/*          → frontend HTML/JS/CSS (mounted at root)
```

### CAS PDF parsing (the most important backend path)

`POST /api/upload/cas` → `routes/upload.py` → `parse_cas_pdf()` → **`_parse_cas_with_casparser()`** (primary) → falls back to PyMuPDF + regex if casparser fails.

`casparser` (github.com/codereverser/casparser) is the authoritative parser. It handles KFintech and CAMS PDFs. The PyMuPDF + 4-strategy regex path is a legacy fallback kept for edge cases.

After parsing, holdings are mapped to a flat `{fund_name, invested, current_value, units, nav, amc, category, folio, isin}` list and saved as a new `Portfolio` snapshot row.

### Portfolio display priority

`GET /api/portfolio/` always returns the **latest `cas_pdf` portfolio first**, then latest `excel`, then latest `manual_entry`. This prevents old manually-entered data from overriding a CAS upload. History is never deleted — all snapshots are preserved and accessible via `GET /api/portfolio/history`.

### Database models

| Model | Key fields |
|---|---|
| `User` | email, full_name, phone, pan, is_verified, oauth_provider, last_login_at |
| `UserSettings` | email_notifications, portfolio_alerts, market_updates, theme, default_view |
| `Portfolio` | user_id, source (`cas_pdf`/`excel`/`manual_entry`), snapshot_date, total_invested, total_current |
| `Holding` | portfolio_id, fund_name, isin, folio_number, units, nav, invested_amount, current_value, amc, category |
| `Transaction` | holding_id, tx_type, tx_date, amount, units, nav (used for XIRR) |
| `FundMaster` | scheme_code, isin, scheme_name, amc, category, current_nav |

Migrations live in `alembic/versions/`. Always run `alembic upgrade head` after pulling.

### Frontend structure

All pages are plain `.html` files in `frontend/`. There is no SPA router — each page is a separate file. Pages share:

- `frontend/js/navbar-auth.js` — injects the top-nav user dropdown on every page (reads `localStorage.authToken` and `userInfo`)
- `frontend/js/portfolio-storage.js` — syncs portfolio data between localStorage and the API
- `frontend/js/toast.js` — toast notification helper
- `frontend/css/design-system.css` — global CSS (primary green: `#7FC04C`)

The `goal-planning` feature is compiled separately via ESBuild (`esbuild.goal-planning.mjs`) because it uses React/JSX — all other pages use vanilla JS.

### Auth

JWT tokens (HS256, 7-day expiry) stored in `localStorage` as `authToken`. The backend uses `get_current_user()` (hard requirement) or `get_optional_current_user()` (allows anonymous) as FastAPI dependencies. Unauthenticated uploads still parse the PDF client-side and store in `localStorage`; data is saved to the DB only when a user is authenticated.

### Deployment

Render.com serves the full app (backend + frontend static files) from a single Python process. `render.yaml` defines the service. Build step runs `alembic upgrade head` before starting. Environment variables are set in the Render dashboard — see `backend/.env.example` for the full list. Key ones: `DATABASE_URL`, `SECRET_KEY`, `JWT_SECRET_KEY`, `GOOGLE_CLIENT_ID/SECRET`, `RESEND_API_KEY`.

---

## Code conventions

### No non-ASCII characters in source files

**Never** use emojis, Unicode symbols (✓ → ₹ etc.), or smart quotes in `.py`, `.js`, `.ts`, `.html`, `.css` files. This causes Windows PowerShell encoding failures and git diff issues. Plain ASCII only in code.

Exceptions where Unicode **is** allowed: `.md` files, user-facing UI strings rendered in the browser, JSON API responses.

### Backend patterns

- All authenticated routes use `current_user: User = Depends(get_current_user)`
- Database sessions: `db: Session = Depends(get_db)` — never create sessions manually
- Use `safe_float_convert(value, field_name, default=0.0)` from `app.services.cas_import` instead of bare `float()` — handles empty strings, Decimal, currency symbols
- Raise `HTTPException(status_code=..., detail="...")` for all API errors
- Log with the module-level `logger = logging.getLogger(__name__)`

### Frontend patterns

- Auth headers: `{ 'Authorization': 'Bearer ' + localStorage.getItem('authToken') }`
- After updating user info, write back to `localStorage.setItem('userInfo', JSON.stringify(...))` and call `window.updateNavbarAuth()` to refresh the navbar
- Indian number formatting: values ≥ 1 Cr as `₹X.XXCr`, ≥ 1 L as `₹X.XXL`, else `₹X,XXX`
