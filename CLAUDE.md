# MFHelper - Mutual Fund Portfolio Analytics Platform

A full-stack fintech web app for Indian mutual fund investors to upload, analyze, and optimize their portfolios with AI-powered insights.

## Tech Stack

- **Backend:** FastAPI (Python 3.13.7), SQLAlchemy 2.0, Pydantic
- **Frontend:** Vite + TypeScript/JavaScript, Chart.js, Plotly.js
- **Database:** SQLite (dev) | PostgreSQL 15 (prod)
- **Auth:** JWT tokens (python-jose), bcrypt password hashing
- **AI:** Ollama (local) / OpenAI API (fallback)
- **Caching:** Redis (optional)
- **Testing:** Pytest (backend), Playwright (E2E)
- **Deployment:** Render.com, Docker

## Project Structure

```
MFHelper/
  backend/app/           # FastAPI backend
    main.py              # App entry point
    config.py            # Environment config
    database.py          # SQLAlchemy setup
    models/              # ORM models (User, Portfolio, Holding)
    routes/              # API endpoints (auth, portfolio, upload, funds, analysis, ai)
    services/            # Business logic (analyzer, cas_import, xirr, chatbot)
    middleware/           # Rate limiting
    utils/               # Auth, cache, logger, sentry
  backend/tests/         # Pytest test suite
  frontend/src/          # TypeScript source (components, services, types, utils)
  frontend/js/           # JavaScript modules (modals, analytics, storage)
  frontend/css/          # Design system (Acorns-inspired green palette)
  frontend/*.html        # Pages (index, dashboard, dashboard-pro, goal-planning, demo)
  tests/e2e/             # Playwright E2E tests
  docs/                  # Project documentation
  alembic/               # Database migrations
```

## Common Commands

### Start Development Server (Windows)
```powershell
.\startup.ps1                    # Starts Ollama + backend + opens browser
.\startup.ps1 -ForceKill        # Kill existing processes first
.\startup.ps1 -NoBrowser        # Skip browser auto-open
```

### Start Backend Manually
```bash
cd backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Start Frontend Dev Server
```bash
cd frontend
npm run dev                      # Dev server on localhost:3000
npm run build                    # Build to www/
npm run type-check               # TypeScript validation
```

### Run Tests
```bash
# Backend (Pytest)
cd backend
pytest tests/ -v                              # All tests
pytest tests/ -m "unit" -v                    # Unit tests only
pytest tests/ --cov=app --cov-report=html     # With coverage

# Frontend E2E (Playwright)
cd tests
npx playwright test                           # All E2E tests
npx playwright test --headed                  # Show browser
npx playwright test --debug                   # Debug mode

# Quick test helper (Windows)
.\quick-test.ps1                # Run UI tests
.\quick-test.ps1 -All           # Run all tests

# Full test suite
.\run-tests.ps1                 # Windows
./run-tests.sh                  # Linux/Mac
```

### Database
```bash
alembic upgrade head             # Apply migrations
alembic downgrade -1             # Rollback last migration
```

### Server Management (Windows)
```powershell
.\cleanup-servers.ps1            # Kill processes on port 8000
.\start-server.ps1 -Reload       # Start with auto-reload
.\pre-push-check.ps1             # Manual pre-push validation
```

## Code Conventions

### Backend (Python/FastAPI)
- Modular routes with FastAPI dependency injection
- Use `get_current_user()` dependency for authenticated endpoints
- Use `get_db()` dependency for database sessions
- Centralized logging via `app.utils.logger`
- HTTPException for errors with proper status codes
- Pydantic schemas for request/response validation
- Rate limiting via slowapi decorators
- API docs auto-generated at `/api/docs`

### Frontend (TypeScript/JavaScript)
- ES modules with imports/exports
- Fetch API for HTTP requests with Bearer token auth
- localStorage for guest mode, IndexedDB for PWA
- CSS variables for theming (primary green #7FC04C)
- Custom toast notification system
- Mobile-first responsive design

### Testing
- Backend: Pytest fixtures in conftest.py, markers: slow, integration, unit, api
- Frontend: Playwright with beforeEach setup patterns
- Pre-push git hooks validate code before pushing

## Key API Endpoints

```
GET    /health                     # Health check
POST   /api/auth/register          # User registration
POST   /api/auth/login             # Login (returns JWT)
GET    /api/portfolio              # Get user portfolio
POST   /api/portfolio/upload       # Upload CAS PDF/Excel
GET    /api/funds/search?q=...     # Search mutual funds
POST   /api/analysis/rebalance     # Rebalancing advice
POST   /api/analysis/overlap       # Fund overlap analysis
GET    /api/demo/portfolio         # Demo data
GET    /api/ai/health              # AI service status
POST   /api/ai/chat                # AI chatbot
GET    /api/docs                   # Swagger API docs
```

## Environment Setup

Copy `.env.example` to `.env` and configure:
- `SECRET_KEY` / `JWT_SECRET_KEY` - Auth secrets
- `DATABASE_URL` - PostgreSQL connection (SQLite default for dev)
- `OLLAMA_BASE_URL` / `OLLAMA_MODEL` - Local AI setup
- `REDIS_URL` - Optional caching
- `SENTRY_DSN` - Optional error tracking

## Important Notes

- File upload limit: 10MB (CAS PDF, Excel, CSV)
- Debug mode auto-detected: SQLite = dev, PostgreSQL = prod
- Connection pooling: 20 base + 40 overflow (production)
- Rate limits on auth endpoints: 5/minute
- Pre-push hooks installed via `.\install-git-hooks.ps1`
