# MFHelper — Short TODO

## Portfolio Data Scraping (In Progress)

Recent progress:
- [x] Discovered AMFI Portfolio Disclosure page (official source)
- [x] Extracted 24 AMC portfolio URLs from AMFI
- [x] Downloaded and parsed Parag Parikh Flexi Cap Fund (110 real holdings)
- [x] Created scraper framework for AMC websites
- [x] Generated comprehensive AMC scraping documentation

Pending (to be done from laptop with Chrome extensions):
- [ ] **HDFC Mutual Fund** - Top 5 funds holdings extraction
  - HDFC Flexi Cap Fund
  - HDFC Top 100 Fund
  - HDFC Mid Cap Opportunities Fund
  - HDFC Small Cap Fund
  - HDFC Balanced Advantage Fund
  - Source: https://www.hdfcfund.com/statutory-disclosure/portfolio/fortnightly-portfolio

- [ ] **Axis Mutual Fund** - Top 5 funds holdings extraction
  - Axis Bluechip Fund
  - Axis Midcap Fund
  - Axis Small Cap Fund
  - Axis Focused 25 Fund
  - Axis Long Term Equity Fund
  - Source: https://www.axismf.com/statutory-disclosures

- [ ] Add more Parag Parikh funds (files already downloaded)
  - PPFAS Consolidated
  - PPLF Liquid Fund

Scripts created:
- `backend/scripts/amfi_portfolio_scraper.py` - Main scraper framework
- `backend/scripts/targeted_scraper.py` - AMC page tester
- `backend/scripts/download_ppfas.py` - PPFAS downloader
- `backend/scripts/parse_ppfas_holdings.py` - Holdings parser
- `backend/scripts/extract_amc_urls.py` - URL extractor from AMFI

---

## Authentication & Email

Recent changes (implemented):

- [x] Email Verification System (Gmail SMTP)
  - Email verification on registration (optional - works without SMTP configured)
  - Gmail SMTP integration ready to use
  - Beautiful HTML email templates (verification, welcome, password reset)
  - Dashboard shows yellow banner for unverified users
  - **SETUP REQUIRED** (see below)

- [x] Authentication Security Improvements
  - Failed login attempt tracking (lockout after 5 attempts for 15 mins)
  - Email normalization (case-insensitive)
  - Password confirmation on signup
  - Last login tracking
  - Password change endpoint: `POST /api/auth/change-password`
  - Account deletion endpoint: `DELETE /api/auth/me`
  - Backend logout endpoint: `POST /api/auth/logout`

- [x] Startup scripts
  - `startup.ps1` (Windows): starts Ollama, pulls `tinyllama`, starts backend, opens UI. Supports `-ForceKill` and `-NoBrowser`.
  - `startup.sh` (Linux): background `ollama serve`, pull model, start `uvicorn`.

- [x] Graceful restart behavior
  - `startup.ps1` now detects processes on ports `11434` (Ollama) and `8000` (backend) and can kill them (prompt or `-ForceKill`).

- [x] AI health endpoint
  - `GET /api/ai/health` implemented in `backend/app/routes/ai.py` — returns `{ available, provider, model, message }`.

- [x] Frontend AI status UI
  - `frontend/dashboard.html` shows a dismissible AI banner and sets `window.AI_AVAILABLE` based on `/api/ai/health`.

- [x] Chat UI fallback
  - `frontend/ai-demo.html` respects `window.AI_AVAILABLE` and shows a friendly fallback message suggesting dashboard search when AI is offline.

Next / Nice-to-have (suggested):

- [ ] Polling + auto-reconnect: poll `/api/ai/health` every 30–60s to auto-update UI and restore AI when available.
- [ ] systemd unit files for Ollama & backend on Linux (production-ready management).
- [ ] Telemetry: record AI-down and fallback usage (analytics & Sentry breadcrumbs).
- [ ] Chat fallback to a real dashboard search API (instead of only showing a message).
- [ ] Add `Makefile` or npm scripts to wrap `startup` commands and common dev tasks.

Files to review:

- `startup.ps1` (repo root)
- `startup.sh` (repo root)
- `backend/app/routes/ai.py` (health endpoint)
- `frontend/dashboard.html` (AI banner + health check)
- `frontend/ai-demo.html` (chat fallback)

If you want, I can implement polling, telemetry, systemd units, or wire the fallback to the dashboard search API next.

---

## 📧 Setup: Email Verification (Gmail SMTP)

Email verification is **optional**. Without SMTP configured, registration/login works normally, users just won't receive verification emails.

### To Enable Email Verification:

**Step 1: Create Gmail App Password**
```
1. Go to: Google Account → Security → 2-Step Verification (enable if not already)
2. Go to: Google Account → Security → App Passwords
3. Select "Mail" and your device → Generate
4. Copy the 16-character password (e.g., "abcd efgh ijkl mnop")
```

**Step 2: Set Environment Variables**
```bash
# Add to .env or Render environment
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=abcd efgh ijkl mnop   # The 16-char app password (no spaces)
SMTP_FROM_EMAIL=your-email@gmail.com  # Optional, defaults to SMTP_USER
FRONTEND_URL=https://mfhelper.onrender.com  # For email links
```

**Step 3: Run Migration**
```bash
cd backend
alembic upgrade head
```

### Endpoints Added:
- `GET /api/auth/verify-email?token=xxx` - Verify email from link
- `POST /api/auth/resend-verification` - Resend (logged-in users)
- `POST /api/auth/resend-verification-by-email` - Resend (by email)
- `GET /api/auth/verification-status` - Check verification status

### Files:
- `backend/app/utils/email_service.py` - SMTP service & templates
- `frontend/verify-email.html` - Verification landing page
- Migration: `alembic/versions/003_add_email_verification.py`

---

# MFHelper - TODO List

> **Goal:** 1000 users in 1 month
> **Strategy:** Fix blockers → Add viral features → Deploy to production → Scale

---

## 🔥 Critical Path (Week 1) - Blocking User Growth

### 1. 🐛 Fix Android Load Demo Button
- [ ] Test Load Demo button on actual Android device
- [ ] Debug why button doesn't work (check console logs)
- [ ] Fix button click handler or data loading issue
- [ ] Verify demo data loads correctly on Android
- [ ] Test on multiple Android versions (10, 11, 12, 13)

**Why Critical:** Users can't try the app without this. Zero conversion if demo doesn't work.

---

### 2. 📸 Complete Portfolio Report Card Generator
- [ ] Find/create PortfolioSummary component for timestamp display
- [ ] Test report card image generation (html2canvas)
- [ ] Verify downloaded PNG quality (1080x1350px)
- [ ] Test social sharing on WhatsApp/Twitter/Instagram
- [ ] Add "Share to unlock premium" incentive
- [ ] Track report card generation & shares in analytics

**Why Critical:** Main viral feature. Each share = 10-50 potential users.

---

### 3. 🔗 Add Referral System
- [ ] Generate unique referral codes per user
- [ ] Create referral link: `mfhelper.app?ref=USER123`
- [ ] Track referral clicks and signups
- [ ] Show referral dashboard (invited, signed up, active)
- [ ] Unlock features: 3 referrals = Premium Analytics
- [ ] Add social share buttons for referral links

**Why Critical:** 1 user → 3 users = 3x growth multiplier. Essential for scaling.

---

### 4. 🚀 Landing Page Optimization
- [ ] Add hero section with clear value prop
- [ ] Add "Try Demo" CTA above the fold
- [ ] Show demo portfolio preview (screenshot/embed)
- [ ] Add social proof: "Used by 500+ investors"
- [ ] Add 3 key features with icons
- [ ] Add testimonials section
- [ ] Optimize for mobile (80% traffic is mobile)
- [ ] Add schema markup for SEO

**Why Critical:** First impression. 50% of users decide in 3 seconds. Current page is too basic.

---

### 5. 📱 Android Build & Test
- [ ] Build APK with latest updates (timestamp, report card)
- [ ] Test on 3+ physical devices (different manufacturers)
- [ ] Fix Load Demo button (see #1)
- [ ] Test PWA install prompt
- [ ] Optimize APK size (<10MB)
- [ ] Prepare for Play Store submission
- [ ] Create app screenshots for listing

**Why Critical:** Android = 70% of Indian smartphone market. Can't ignore this segment.

---

## ⚡ High Priority (Week 2) - Growth Enablers

### 6. ✨ Add PWA Install Prompt
- [ ] Detect if app is installable
- [ ] Show custom install banner (better than browser default)
- [ ] Add "Install App" button in settings
- [ ] Track install rate
- [ ] A/B test prompt timing (immediate vs after 30s)

**Impact:** Installed PWA = 3x better retention than web.

---

### 7. 📊 Add Analytics Tracking
- [ ] Set up Google Analytics 4
- [ ] Track key events:
  - Page views (home, dashboard, upload)
  - Portfolio uploads (Excel, demo)
  - Report card generations
  - Report card shares
  - Referral link clicks
- [ ] Set up conversion funnels
- [ ] Create dashboard for metrics

**Impact:** Can't improve what you don't measure. Essential for optimization.

---

### 8. 🎯 SEO & Content Marketing
- [ ] Create 3 blog posts:
  - "How to Track Your Mutual Fund Portfolio in 2026"
  - "Complete Guide to Portfolio Rebalancing"
  - "Understanding Large Cap vs Mid Cap vs Small Cap"
- [ ] Optimize meta tags (title, description, OG tags)
- [ ] Add schema markup (Article, WebApplication)
- [ ] Submit to Google Search Console
- [ ] Target keywords: "mutual fund tracker", "portfolio analyzer"
- [ ] Create sitemap.xml

**Impact:** Organic search = Free traffic. 20-30% of visitors can come from SEO.

---

### 9. 📢 Social Media Presence
- [ ] Create Twitter account @MFHelperApp
- [ ] Create LinkedIn page
- [ ] Post daily:
  - Portfolio tips
  - Screenshots of features
  - User success stories
- [ ] Engage in:
  - r/IndiaInvestments
  - r/IndianStockMarket
  - Twitter #MutualFunds #PortfolioManagement
- [ ] Partner with finance influencers

**Impact:** Direct channel to target audience. Low cost, high reach.

---

## 🔧 Production Ready (Week 3) - Before Scaling

### 10. 💾 Production Database Setup
- [ ] Set up PostgreSQL on cloud (Render/Railway/Supabase)
- [ ] Create production database
- [ ] Run Alembic migrations
- [ ] Set up automated backups
- [ ] Configure connection pooling
- [ ] Test database performance under load

**Impact:** SQLite won't scale. Need proper DB before hitting 1000 users.

---

### 11. 🔐 Environment Variables & Security
- [ ] Create production .env file
- [ ] Set up secrets on hosting platform
- [ ] Rotate all API keys
- [ ] Configure CORS properly
- [ ] Add rate limiting
- [ ] Enable HTTPS/SSL
- [ ] Set DEBUG=False

**Impact:** Security breach = Game over. Must be done right.

---

### 12. 🌐 Deploy to Production
- [ ] Deploy backend to Render/Railway
- [ ] Deploy frontend to Vercel/Netlify
- [ ] Set up custom domain (mfhelper.app)
- [ ] Configure DNS
- [ ] Test production deployment
- [ ] Set up CI/CD pipeline
- [ ] Create deployment checklist

**Impact:** Can't get users without being live!

---

### 13. 📊 Data Infrastructure Implementation
- [ ] Follow docs/DATA_INFRASTRUCTURE.md
- [ ] Set up NSE data fetcher
- [ ] Set up fund holdings scraper
- [ ] Configure weekly scheduler (Sundays 2 AM)
- [ ] Test market cap classification
- [ ] Verify data accuracy

**Impact:** Accurate Large/Mid/Small cap data = Trust = User retention.

---

### 14. 🧪 Testing & QA
- [ ] Run pytest test suite
- [ ] Test on Chrome, Firefox, Safari
- [ ] Test on Android (3+ devices)
- [ ] Test on iOS (if possible)
- [ ] Load testing (100 concurrent users)
- [ ] Fix all critical bugs
- [ ] Document known issues

**Impact:** Bugs = Bad reviews = No growth.

---

### 15. 📈 Monitoring & Logging
- [ ] Set up Sentry for error tracking
- [ ] Set up UptimeRobot for uptime monitoring
- [ ] Configure alerts (email, Slack, SMS)
- [ ] Set up log aggregation
- [ ] Create monitoring dashboard
- [ ] Document incident response

**Impact:** Can't fix what you can't see. Essential for maintaining uptime.

---

## 📚 Moved to Backlog (Post-1000 Users)

### Auth & User Management
- [ ] Email verification system
- [ ] Password reset flow
- [ ] Social authentication (Google, GitHub)
- [ ] User settings CRUD
- [ ] Profile management

### Advanced Analytics
- [ ] Portfolio overlap analysis
- [ ] Performance attribution
- [ ] Risk metrics (beta, Sharpe ratio)
- [ ] Sector-wise performance
- [ ] Goal-based investing

### Data Management
- [ ] **CAS PDF import (CAMS/KFintech)** ⭐ MOVE TO HIGH PRIORITY
  - Implement `/api/upload/cas` endpoint using casparser
  - Get CAMS or KFintech CAS sample for testing
  - Parse folios, schemes, transactions, valuations
  - Calculate portfolio metrics (invested, current, gains, XIRR)
  - Save to database with historical snapshots
  - Add CAS upload UI to dashboard
  - Handle password-protected PDFs
  - See: `docs/CAS_PARSING_INVESTIGATION.md` for details
  
- [ ] **CDSL CAS Support (Low Priority)**
  - casparser partially supports CDSL (accounts but not holdings)
  - Option 1: Contribute holdings extraction to casparser
  - Option 2: Build custom CDSL parser
  - Option 3: Ask users for CAMS/KFin CAS instead
  - Decision: Defer until CAMS/KFin implementation complete
  
- [ ] Automatic data refresh via APIs
- [ ] Transaction history parsing
- [ ] XIRR calculations
- [ ] Tax planning (LTCG/STCG)

### Auth & User Management (Partially Complete)
- [x] ~~JWT authentication system~~ ✅
- [x] ~~User registration/login~~ ✅
- [x] ~~User settings with theme support~~ ✅
- [x] ~~Database-backed storage~~ ✅
- [ ] **Fix TypeScript compilation errors**
  - Fix toast.js import in auth-ui.ts
  - Compile TypeScript to JavaScript
  - Test compiled output in browser
- [ ] **Test auth UI in browser**
  - Login/Register modals
  - Settings modal (Profile/Preferences/Notifications tabs)
  - Theme switching
  - Form validation
- [ ] **Write auth route tests**
  - Registration tests (valid/invalid)
  - Login tests (success/failure)
  - Protected route tests
  - Settings CRUD tests
- [ ] Email verification system
- [ ] Password reset flow
- [ ] Social authentication (Google, GitHub)

### Database Management
- [x] ~~Seed database script created~~ ✅ `scripts/seed_database.py`
- [ ] **Run seed script to populate test data**
  - 3 test users (demo@mfhelper.com, test@example.com, investor@example.com)
  - 2 portfolio snapshots for demo user (Feb + Jan 2026)
  - Realistic holdings with NAV, returns, performance data
  - Run: `python scripts/seed_database.py`
- [ ] **Create Alembic migration system**
  - Initialize Alembic
  - Create initial migration from models
  - Add UserSettings migration
  - Document migration workflow
- [ ] Accessibility (a11y)
- [ ] Keyboard navigation
- [ ] Dark mode improvements
- [ ] Responsive design polish

### Admin Features
- [ ] Admin dashboard
- [ ] User management
- [ ] System health monitoring
- [ ] Fund data management

---

## 🎯 Success Metrics

**Week 1:** 
- Android demo working ✅
- Report card live + 50 shares
- Referral system live
- Landing page redesigned

**Week 2:**
- Analytics tracking live
- 100 daily active users
- 20% referral conversion
- 10% install rate (PWA)

**Week 3:**
- Production deployed
- 500 total users
- 99.9% uptime
- <500ms response time

**Week 4:**
- 1000 total users 🎉
- 300 daily active users
- 50 report card shares/day
- 4.5+ rating

---

## 💡 Quick Wins (Can Do Anytime)

- [ ] Add loading states to all buttons
- [ ] Improve error messages
- [ ] Add tooltips for complex features
- [ ] Compress images for faster loading
- [ ] Add keyboard shortcuts
- [ ] Create demo video (30 seconds)
- [ ] Write press release
- [ ] Create social media templates

---

**Next Action:** Start with #1 - Fix Android Load Demo Button!
  - Optimize queries
  - Add pagination

- [ ] **Security hardening**
  - Add rate limiting
  - Add CSRF protection
  - Add input sanitization
  - Security audit

## 📊 Current Status

**Completed:**
✅ User authentication system (JWT)
✅ User settings & preferences (theme, notifications, display)
✅ Database-backed portfolio storage with history tracking
✅ Portfolio history snapshots (never deletes old data)
✅ Theme support (light/dark/auto)
✅ TypeScript frontend components (auth-ui, auth service)
✅ 61/61 backend tests passing (portfolio, upload, analytics, rebalance)
✅ Rebalancing calculator with recommendations
✅ Analytics endpoints (allocation, performance, risk)
✅ Database seed script with test data
✅ CAS parsing investigation completed
✅ casparser library tested with CDSL format
✅ Comprehensive CAS parsing documentation

**In Progress:**
🔄 TypeScript compilation fixes (toast.js import issue)
🔄 Frontend auth integration (add buttons, test modals)
🔄 CAS import implementation (waiting for CAMS/KFin sample)

**Next Up:**
⏭️ Run database seed script
⏭️ Fix TypeScript compilation
⏭️ Get CAMS or KFintech CAS sample
⏭️ Implement CAS upload endpoint
⏭️ Test auth UI in browser
⏭️ Write auth route tests

**Blocked:**
❌ CAS import - need CAMS/KFintech sample (CDSL partially works but missing holdings)

---

**Last Updated:** February 10, 2026 (after E2E audit)

---

# Non-Critical Issues (E2E Audit — 2026-02-10)

> Critical bugs fixed separately: appendChild null, style redeclaration, portfolioStorage.load, marketCap misclassification, style misclassification, route conflict

## Fix First (Medium Severity, High Impact)

### SECURITY

- [ ] **#1** `SECRET_KEY` / `JWT_SECRET_KEY` fall back to weak hardcoded defaults → Raise startup error if not set in non-DEBUG mode  
  **File:** `backend/app/config.py`

- [x] **#2** `ADMIN_API_KEY` hardcoded, passed as query param → Moved to `os.getenv()`, added `X-Admin-Key` header support  
  **File:** `backend/app/routes/admin.py`

- [x] **#3** All 5 data update endpoints (`/api/data/update/*`) had zero authentication → Added `Depends(verify_data_admin)` with `X-Admin-Key` header  
  **File:** `backend/app/routes/data_updates.py`

- [ ] **#4** Google OAuth client ID hardcoded in HTML → Inject via API or env  
  **File:** `frontend/auth.html`

- [x] **#5** `/api/auth/check-email` enabled email enumeration → Now returns generic `"Email checked"` message  
  **File:** `backend/app/routes/auth.py`

- [x] **#6** `/api/admin/users` exposed full PAN and phone → PAN redacted to `****XXXX`, phone removed from list  
  **File:** `backend/app/routes/admin.py`

### CODE QUALITY / XSS

- [x] **#21** `innerHTML` XSS vector → Added `escapeHtml()` helper, all user data (fund names, AMC, category, style) now escaped  
  **File:** `frontend/js/dashboard.js`

- [x] **#22** `toast.innerHTML` XSS → Added `escapeHtml()` to ToastManager, message now sanitized  
  **File:** `frontend/js/toast.js`

### FUNCTIONAL BUG

- [x] **#10** Token key mismatch → Now checks `authToken` first, falls back to `access_token`  
  **File:** `frontend/js/dashboard.js`

### PERFORMANCE

- [x] **#15** 12 render-blocking scripts → Added `defer` to all 14 `<script>` tags in dashboard head  
  **File:** `frontend/dashboard.html`

### DEPRECATION

- [x] **#12** Plotly CDN frozen at v1.58.5 → Updated to `plotly-2.35.2.min.js`  
  **Files:** `frontend/dashboard.html`, `frontend/dashboard-pro.html`

### UX

- [x] **#30** Auth modal missing confirm password → Added confirm password field + regex strength validation  
  **File:** `frontend/js/auth-modals.js`

### ACCESSIBILITY

- [x] **#33** Auth page missing ARIA → Added `role="tablist"`, `role="tab"`, `aria-selected`, `aria-controls`, `role="tabpanel"`  
  **File:** `frontend/auth.html`

### BACKEND

- [x] **#23** 4 bare `print()` at import time → Replaced with `logger.info()`  
  **File:** `backend/app/config.py`

---

## Fix Later (Low Severity)

### SECURITY

- [x] **#7** No `Content-Security-Policy` header → Added CSP, X-Frame-Options, X-Content-Type-Options, HSTS, Referrer-Policy via middleware  
  **File:** `backend/app/main.py`

- [ ] **#8** `POST /api/auth/logout` is a no-op — JWT remains valid for 7 days, no token blacklist  
  **File:** `backend/app/routes/auth.py`

- [ ] **#9** JWT expiry is 7 days with no revocation mechanism  
  **File:** `backend/app/utils/auth.py`

- [ ] **#11** Guest uploads saved to `./uploads` with no cleanup/TTL mechanism  
  **File:** `backend/app/routes/upload.py`

### DEPRECATION

- [x] **#13** Deprecated `declarative_base` import → Updated to `sqlalchemy.orm.declarative_base`  
  **File:** `backend/app/database.py`

- [x] **#14** GA placeholder `G-XXXXXXXXXX` → Disabled until configured via `window.GA_MEASUREMENT_ID`  
  **File:** `frontend/js/analytics.js`

### PERFORMANCE

- [x] **#16** N+1 query in `/api/admin/stats` → Replaced with subquery join for holdings count  
  **File:** `backend/app/routes/admin.py`

- [x] **#17** N+1 query in `/api/admin/users` → Replaced with aggregated subquery for portfolio count + AUM  
  **File:** `backend/app/routes/admin.py`

- [x] **#18** `user-scalable=no` disabled pinch-to-zoom → Removed from viewport meta  
  **Files:** `frontend/dashboard.html`, `frontend/how-it-works.html`

- [x] **#19** `echo=settings.DEBUG` logged every SQL query → Set `echo=False`, removed DEBUG force-set  
  **File:** `backend/app/database.py`

- [ ] **#20** ~170 lines of inline `<script>` in index.html duplicating logic from index.js  
  **File:** `frontend/index.html`

### CODE QUALITY

- [x] **#24** ~60+ `console.log` / `console.warn` in production JS → Removed informational logs, kept `console.error`  
  **Files:** Multiple frontend JS files

- [ ] **#25** Component stubs show "coming soon" toasts — placeholder code  
  **File:** `frontend/js/components.js`

- [x] **#26** `print()` in holdings.py → Replaced with `logger.warning()`  
  **File:** `backend/app/routes/holdings.py`

- [x] **#27** `print()` in error handlers → Replaced with `logger.warning()` / `logger.error()`  
  **File:** `backend/app/routes/errors.py`

- [x] **#28** ~270 lines of repetitive static routes → Replaced with generic catch-all handler  
  **File:** `backend/app/main.py`

- [x] **#29** `sendDashboardChat()` hardcoded `Bearer demo-token` → Now uses real `authToken` from localStorage  
  **File:** `frontend/js/dashboard.js`

### UX

- [x] **#31** "Forgot password?" dead link → Shows alert with support email (full reset flow deferred)  
  **File:** `frontend/auth.html`

- [x] **#32** "Settings" link opened admin panel → Now points to `/dashboard.html`  
  **File:** `frontend/js/navbar-auth.js`

### ACCESSIBILITY

- [x] **#34** `user-scalable=no` blocked zoom → Removed (same fix as #18)  
  **Files:** `frontend/dashboard.html`, `frontend/how-it-works.html`

- [x] **#35** Charts had no text alternatives → Added `role="img"` + `aria-label` to all 6 chart containers  
  **File:** `frontend/js/dashboard.js`

- [x] **#36** Modals lacked focus trap + Escape → Added `_trapFocus()`/`_releaseFocus()` + Escape key handler  
  **File:** `frontend/js/auth-modals.js`

### BACKEND

- [ ] **#39** Upload has no file content validation beyond extension  
  **File:** `backend/app/routes/upload.py`

- [x] **#40** `DEBUG` force-set to `True` for SQLite → Removed silent override, respects env var  
  **File:** `backend/app/config.py`
