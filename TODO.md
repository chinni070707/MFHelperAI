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

**Last Updated:** February 1, 2026 (after CAS parsing investigation)
