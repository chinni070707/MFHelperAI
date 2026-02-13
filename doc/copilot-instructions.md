# GitHub Copilot Instructions - MFHelper Project

## Project Overview

**MFHelper** is a SaaS mutual fund portfolio analytics platform for Indian investors, built as a solo developer project with a focus on simplicity, speed, and cross-platform deployment.

### Mission Statement
Democratize advanced mutual fund analytics by providing retail investors with institutional-grade portfolio insights, typically available only to HNI clients at wealth management firms.

---

## Tech Stack & Architecture

### Core Philosophy: **One Codebase, All Platforms**

```
Single HTML/CSS/JavaScript Codebase
                ↓
    ┌───────────┼───────────┐
    ↓           ↓           ↓
 Web App    Android App   iOS App
 (PWA)     (Capacitor)  (Capacitor)
```

### Technology Choices

**Backend:**
- **FastAPI** (Python) - Modern, fast, async web framework
- **SQLAlchemy** - ORM for database operations
- **SQLite** - Initial database (migrate to PostgreSQL for scale)
- **Pandas** - Data processing and analytics
- **Plotly/Chart.js** - Server-side chart generation (optional)

**Frontend:**
- **Vanilla JavaScript** - No React/Vue/Angular (KISS principle)
- **HTML5 + CSS3** - Modern web standards
- **Plotly.js** - Interactive charts and visualizations
- **PWA** - Progressive Web App for installability
- **Capacitor** - Wrap web app for iOS/Android (when needed)

**Why Vanilla JS instead of React?**
1. Faster development for solo developer
2. No build step complexity
3. Smaller bundle size
4. Easier to debug
5. Direct browser compatibility

---

## Project Goals

### Phase 1: MVP (Month 1-2) ✅
- [x] Excel/CAS portfolio upload
- [x] Dashboard with 5 summary cards
- [x] 6 interactive charts (market cap, AMC, sectors)
- [x] Investment style classification
- [x] Rebalancing calculator
- [x] Portfolio overlap analysis
- [x] PWA setup for mobile
- [x] Error handling & toast notifications

### Phase 2: Differentiation (Month 3-4)
- [ ] XIRR calculator
- [ ] Tax harvesting recommendations
- [ ] Capital gains statement
- [ ] Regular vs Direct comparison
- [ ] Goal-based planning
- [ ] Advanced overlap analysis

### Phase 3: Monetization (Month 5-6)
- [ ] Freemium model (5 uploads/month free)
- [ ] Pro tier (₹499/year)
- [ ] AI-powered recommendations
- [ ] Multi-asset tracking

### Phase 4: B2B (Month 7+)
- [ ] Lead generation for distributors
- [ ] White-label solution
- [ ] API for partners

---

## Key Design Principles

### 1. **Mobile-First**
- 70% of Indian users access from mobile
- Touch-friendly UI (44px minimum touch targets)
- Responsive design auto-applies
- PWA for app-like experience

### 2. **Offline-Capable**
- Service worker caches assets
- Database stored locally (SQLite)
- Fund holdings in database (no runtime API calls)
- Works without internet after initial load

### 3. **Fast & Lightweight**
- No heavy frameworks
- Minimize dependencies
- Lazy load charts
- Database queries over API calls

### 4. **Privacy-First**
- No user data stored on server (initially)
- Everything in localStorage/sessionStorage
- Optional account creation
- GDPR/data privacy compliant

### 5. **Solo Developer Friendly**
- Simple deployment (single command)
- Minimal DevOps complexity
- SQLite → no database server needed
- Free hosting possible (Vercel, Railway)

---

## 📱 Mobile App UI/UX Guidelines (Critical - 2026 Standards)

### **CRITICAL: App vs Website Mindset**

**This is a MOBILE APP, not a mobile-responsive website.**

```
❌ WRONG (Website thinking):
   - Long scrolling page with all content
   - Everything visible at once
   - Desktop layout scaled down

✅ CORRECT (App thinking):
   - Tab-based views (one screen at a time)
   - View switching with animations
   - Mobile-native interaction patterns
```

### **Navigation Patterns**

1. **Bottom Navigation Bar** (4-5 tabs max)
   ```
   ┌─────┬─────┬─────┬─────┐
   │ 🏠  │ 💼  │ 📊  │ 👤  │
   │Home │Port │Anal │Prof │
   └─────┴─────┴─────┴─────┘
   ```

2. **View Switching** (NOT scrolling between sections)
   - Each tab shows ONE full-screen view
   - Tapping tab REPLACES current view
   - Animate transitions (fade, slide)

3. **Swipe Gestures**
   - Swipe left/right to navigate tabs
   - Pull-to-refresh from top
   - Swipe-to-delete on list items

### **Essential Mobile Gestures**

| Gesture | Action |
|---------|--------|
| Tap | Primary action |
| Long press | Context menu |
| Swipe left/right | Navigate tabs |
| Pull down | Refresh data |
| Swipe item | Delete/archive |
| Pinch | Zoom charts |
| Double tap | Quick action |

### **Modern UI Must-Haves (2026)**

1. **Loading Skeletons** (NOT spinners)
   ```html
   <!-- Show placeholder shape while loading -->
   <div class="skeleton skeleton-text"></div>
   <div class="skeleton skeleton-circle"></div>
   ```

2. **Haptic Feedback**
   ```javascript
   // Vibrate on important actions
   navigator.vibrate && navigator.vibrate(10);
   ```

3. **Optimistic UI Updates**
   ```javascript
   // Update UI immediately, sync in background
   updateUI(newData);  // Instant
   await saveToServer(newData);  // Background
   ```

4. **Progressive Disclosure**
   - Show summary first
   - Tap to expand details
   - Don't overwhelm with information

5. **Dark Mode Support**
   ```css
   @media (prefers-color-scheme: dark) {
     --bg-primary: #111827;
   }
   ```

### **Mobile UI Research Process**

**ALWAYS follow this checklist when building mobile UI:**

```
□ Navigation pattern defined?
   - Tab-based views (not scrolling page)
   - Bottom nav or side drawer

□ Gestures implemented?
   - Pull-to-refresh
   - Swipe navigation
   - Long-press context menu

□ Loading states?
   - Skeleton loaders (not spinners)
   - Optimistic updates

□ Error handling?
   - Retry buttons
   - Helpful error messages
   - Offline fallback

□ Empty states?
   - Friendly empty message
   - Call-to-action button

□ Success feedback?
   - Toast notifications
   - Animations/celebrations
   - Haptic feedback

□ Accessibility?
   - 44px minimum touch targets
   - Color contrast AA compliant
   - Screen reader labels
```

### **Research Before Building**

When building mobile UI, research these aspects:

1. **Interaction Patterns** (HOW users navigate)
   - Not just visual design (what it looks like)
   - Focus on screen-to-screen flows

2. **Gesture Support** (WHAT actions are available)
   - Swipe, long-press, pull-to-refresh
   - Native mobile expectations

3. **User Flows** (WHERE users go)
   ```
   Launch → Home View → Tap Portfolio → Portfolio View
                    ↓
                 Swipe Left → Analyze View
   ```

4. **Test Real Apps**
   - Install competitor apps (INDmoney, Kuvera, Dezerv)
   - Use them for real tasks
   - Document interaction patterns

### **Common Mobile UI Mistakes to Avoid**

```
❌ Long scrolling page with multiple sections
❌ Showing all content at once
❌ Desktop-style navigation on mobile
❌ Spinners instead of skeletons
❌ No gesture support
❌ Tiny touch targets (<44px)
❌ No loading states
❌ No error recovery options
❌ Ignoring platform conventions
```

### **File Structure for Mobile Components**

```
frontend/
├── css/
│   ├── design-system.css    # Colors, spacing, typography
│   └── components.css       # Card, button, nav styles
├── js/
│   ├── components.js        # Reusable UI components
│   ├── gestures.js          # Touch gesture handlers
│   └── navigation.js        # View switching logic
└── dashboard-pro.html       # Main app (tab-based views)
```

---

## Code Style Guidelines

### **CRITICAL: No Unicode Characters or Emojis in Code**

**NEVER use unicode characters, emojis, or non-ASCII symbols in actual code files:**

❌ **FORBIDDEN in code:**
```javascript
// ❌ DON'T: Emojis in comments
const portfolioData = fetchData(); // 🚀 Fast API call

// ❌ DON'T: Unicode symbols
const checkmark = '✓';
const arrow = '→';

// ❌ DON'T: Special characters in variable names
const 💰portfolioValue = 1000;
```

✓ **ALLOWED in code:**
```javascript
// ✓ DO: Plain ASCII comments
const portfolioData = fetchData(); // Fast API call

// ✓ DO: ASCII characters only
const checkmark = 'v';
const arrow = '->';

// ✓ DO: Standard variable names
const portfolioValue = 1000;
```

**Where unicode/emojis ARE allowed:**
- Documentation files (.md)
- User-facing strings (UI text, messages)
- Test data representing user input

**Rationale:**
- Ensures cross-platform compatibility
- Prevents encoding issues in terminals/editors
- Maintains code readability across all environments
- Avoids git diff/merge problems

---

### Backend (Python/FastAPI)

```python
# Use type hints always
def calculate_xirr(transactions: List[Transaction]) -> float:
    """
    Calculate XIRR for given transactions
    
    Args:
        transactions: List of Transaction objects
        
    Returns:
        XIRR as decimal (e.g., 0.12 for 12%)
    """
    pass

# Use Pydantic models for validation
class OverlapRequest(BaseModel):
    fund_names: List[str]

# Use dependency injection
@router.get("/holdings")
async def get_holdings(db: Session = Depends(get_db)):
    pass

# Handle errors gracefully
try:
    result = calculate()
except Exception as e:
    raise HTTPException(status_code=500, detail=str(e))
```

### Frontend (JavaScript)

```javascript
// Use async/await for API calls
async function loadPortfolio() {
    const loading = loading.show('Loading...');
    try {
        const response = await fetch('/api/portfolio');
        const data = await response.json();
        displayData(data);
    } catch (error) {
        errorHandler.handleAPIError(error);
    } finally {
        loading.hide(loading);
    }
}

// Use our custom utilities
toast.success('Portfolio loaded!');
errorHandler.log({ type: 'INFO', message: 'User action' });

// Mobile-responsive checks
if (device.isMobile()) {
    // Mobile-specific logic
}
```

### CSS

```css
/* Mobile-first approach */
.container {
    width: 100%;
    padding: 15px;
}

/* Desktop enhancement */
@media (min-width: 768px) {
    .container {
        max-width: 1200px;
        padding: 30px;
    }
}

/* Dark theme (default) */
background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
```

---

## Critical Implementation Details

### 1. **Portfolio Overlap Analysis**

**Data Source:** Database-powered (not runtime API)
```python
# Holdings stored in SQLite
# Updated weekly via GitHub Actions or manual script
# Fast queries, no external dependencies
```

**Update Strategy:**
- Manual: Update JSON → Run script → Commit DB
- Automated: GitHub Actions every Sunday
- No paid APIs needed for MVP

### 2. **File Upload Flow**

```
User uploads Excel/PDF
       ↓
Frontend validates (size, format)
       ↓
Show loading toast
       ↓
POST to /api/upload/excel
       ↓
Backend parses with pandas
       ↓
Returns JSON
       ↓
Store in localStorage
       ↓
Redirect to dashboard
       ↓
Hide loading, show success toast
```

### 3. **PWA Implementation**

**Required Files:**
- `manifest.json` - App metadata ✅
- `sw.js` - Service worker for caching ✅
- `offline.html` - Offline fallback ✅
- App icons (all sizes) 🔜

**Installation Flow:**
1. User visits site on mobile
2. Browser shows "Add to Home Screen"
3. User installs
4. Opens like native app

### 4. **Error Handling**

**Never use `alert()` or `console.error()` directly!**

```javascript
// ❌ Bad
alert('Error!');

// ✅ Good
toast.error('Something went wrong. Please try again.');
errorHandler.handleAPIError(error);
```

All errors logged to:
1. Browser console
2. localStorage (last 100)
3. Backend endpoint (POST /api/errors)
4. Future: Sentry/monitoring service

---

## Database Strategy

### Current: SQLite (MVP)
```
Pros: 
- Zero setup
- File-based
- Fast for <100k records
- Version controlled (can commit .db file)

Cons:
- Single writer
- Limited concurrency
- Not for high traffic
```

### Future: PostgreSQL (Scale)
```
Migration trigger: >1000 users or need real-time collab
Keep same SQLAlchemy models
Just change connection string
```

### Holdings Data
```
Source: backend/data/fund_holdings.json
Loaded into DB: fund_master, fund_holdings, fund_sector_allocation
Update frequency: Weekly (sufficient, funds change monthly)
Size: ~2-3MB for 1000 funds
Current: 98 funds, 963 unique stocks (as of Feb 2026)
```

### Fund Holdings Data Management

**Data Source:** Holdings are scraped from MoneyControl portfolio pages and stored in `backend/data/fund_holdings.json`.

**Key Scripts:**
- `scripts/refetch_holdings.py` — Main tool to fetch/refresh holdings from MoneyControl
- `scripts/validate_holdings.py` — Validates data quality (sectors, weights, duplicates)

**Refetching Holdings:**
```bash
cd backend

# List any funds with dummy/placeholder data
python scripts/refetch_holdings.py --list-dummy

# Refetch all dummy funds
python scripts/refetch_holdings.py

# Refetch a specific fund
python scripts/refetch_holdings.py --fund hdfc-top-100-fund

# Add a new fund with a MoneyControl URL
python scripts/refetch_holdings.py --add axis-bluechip-fund --url https://www.moneycontrol.com/mutual-funds/axis-bluechip-fund-direct-growth/portfolio-holdings/MXXXX

# Refetch a fund with a custom/corrected URL
python scripts/refetch_holdings.py --fund my-fund --url https://...

# Dry run (show what would be fetched)
python scripts/refetch_holdings.py --dry-run

# Always validate after changes
python scripts/validate_holdings.py
```

**MoneyControl Rate Limiting:**
- MoneyControl aggressively rate-limits (HTTP 503) after ~3-5 requests
- The refetch script has built-in retry logic (3 attempts with 8/16/24s backoff)
- Default delay between funds: 5 seconds
- If blocked, wait 2-5 minutes before retrying
- MoneyControl fund codes (e.g., MHD068) are NOT sequential and don't follow a pattern — you must find them from their website manually

**Data Quality Rules:**
- Every fund must have: name, amc (non-empty), category, holdings (>=3 stocks)
- Weights should sum to 80-105% (some funds don't list all holdings)
- Sector names vary across MoneyControl pages (e.g., "Banks" vs "Private sector bank") — this is expected
- Run `validate_holdings.py` after any data changes; 0 errors required, warnings are acceptable

**Known Issues (as of Feb 2026):**
- 6 popular funds are missing due to incorrect MoneyControl codes: axis-bluechip-fund, sbi-bluechip-fund, icici-prudential-bluechip-fund, mirae-asset-emerging-bluechip-fund, quantum-elss-tax-saver-fund, quantum-value-fund
- hdfc-top-100-fund and hdfc-mid-cap-fund share identical data (wrong MC URL for mid-cap)
- MoneyControl has 2 table formats: basic (9 cols) and extended (12 cols with "Sector Total", "M-Cap") — the scraper picks the table with the most rows

---

## Deployment Strategy

### Phase 1: Free Hosting
- **Backend:** Railway.app or Render.com (free tier)
- **Frontend:** Vercel or Netlify (free)
- **Database:** SQLite file (committed to repo)
- **Domain:** free subdomain or ₹500/year .in domain

### Phase 2: Paid Hosting
- **Backend:** Railway Pro (₹1000/month)
- **Database:** Railway PostgreSQL or Supabase
- **CDN:** Cloudflare (free)
- **Monitoring:** Sentry (free tier)

---

## User Personas

### 1. **DIY Investor (Primary)**
- Age: 25-40
- Tech-savvy
- Has 5-15 mutual funds
- Uses Zerodha/Groww
- Wants: Overlap analysis, tax planning
- Willing to pay: ₹500-1000/year

### 2. **New Investor (Secondary)**
- Age: 22-30
- Learning about mutual funds
- Has 2-5 funds
- Wants: Simple analytics, education
- Willing to pay: ₹0 (free tier)

### 3. **Distributor/Advisor (B2B)**
- Manages 50-500 clients
- Needs: Lead gen, white-label
- Willing to pay: ₹5000-50,000/year

---

## Competitive Advantage

| Feature | MFHelper | Kuvera | Paytm Money | INDMoney |
|---------|----------|---------|-------------|----------|
| **Overlap Analysis** | ✅ Free | ❌ | ❌ | ✅ Paid |
| **Tax Harvesting** | 🔜 | ✅ | ❌ | ✅ |
| **Goal Planning** | 🔜 | ✅ | ✅ | ✅ |
| **No Account Needed** | ✅ | ❌ | ❌ | ❌ |
| **Works Offline** | ✅ | ❌ | ❌ | ❌ |
| **Privacy-First** | ✅ | ❌ | ❌ | ❌ |

**Our USP:** Analytics-first, no investment platform lock-in, privacy-focused.

---

## File Structure Convention

```
MFHelper/
├── backend/
│   ├── app/
│   │   ├── main.py              # FastAPI app
│   │   ├── models/              # SQLAlchemy models
│   │   ├── routes/              # API endpoints
│   │   ├── services/            # Business logic
│   │   └── utils/               # Helper functions
│   ├── data/                    # Static data (JSON)
│   ├── scripts/                 # Migration/update scripts
│   └── tests/                   # Unit tests
├── frontend/
│   ├── index.html               # Landing page
│   ├── dashboard.html           # Main dashboard
│   ├── js/
│   │   ├── toast.js            # Toast notifications
│   │   ├── errorHandler.js     # Error handling
│   │   ├── responsive.js       # Mobile utilities
│   │   └── overlap.js          # Overlap analyzer
│   ├── icons/                   # PWA icons
│   ├── manifest.json           # PWA manifest
│   └── sw.js                   # Service worker
├── .github/workflows/           # CI/CD
├── docs/                        # Documentation
└── README.md
```

---

## Common Patterns & Helpers

### 1. **API Call Pattern**

```javascript
async function apiCall(endpoint, options = {}) {
    const loadingId = loading.show('Loading...');
    try {
        const response = await fetch(endpoint, {
            ...options,
            headers: {
                'Content-Type': 'application/json',
                ...options.headers
            }
        });
        
        if (!response.ok) {
            throw new Error(`HTTP ${response.status}`);
        }
        
        const data = await response.json();
        loading.hide(loadingId);
        return data;
    } catch (error) {
        loading.hide(loadingId);
        errorHandler.handleAPIError(error, { endpoint });
        throw error;
    }
}
```

### 2. **Chart Creation Pattern**

```javascript
function createChart(containerId, data, config) {
    const defaultConfig = {
        responsive: true,
        displayModeBar: false,
        paper_bgcolor: 'transparent',
        plot_bgcolor: 'transparent',
        font: { color: '#fff', family: 'Inter' }
    };
    
    Plotly.newPlot(
        containerId,
        data,
        { ...defaultConfig, ...config }
    );
}
```

### 3. **Database Query Pattern**

```python
def get_fund_with_holdings(db: Session, fund_key: str):
    """Get fund with all holdings in one query"""
    return db.query(FundMaster)\
        .options(joinedload(FundMaster.holdings))\
        .filter(FundMaster.fund_key == fund_key)\
        .first()
```

---

## Important URLs & Resources

### External Resources
- **MFApi:** https://mfapi.in/ (Free NAV data)
- **AMFI:** https://www.amfiindia.com/ (Official holdings data)
- **Capacitor Docs:** https://capacitorjs.com/ (For mobile apps)
- **PWA Guide:** https://web.dev/progressive-web-apps/
- **Plotly Examples:** https://plotly.com/javascript/

### Project Documentation
- **[Render MCP Usage Guide](../docs/RENDER_MCP_USAGE.md)** - Quick reference for managing Render deployments via API
- **[Render MCP Setup](RENDER_MCP_SETUP.md)** - Initial Render MCP configuration
- **[Render Deployment Guide](RENDER_DEPLOYMENT.md)** - Full deployment setup instructions
- **[Testing Guide](TESTING_GUIDE.md)** - How to run tests

---

## DO's and DON'Ts

### ✅ DO

- Use async/await for all API calls
- Show loading states for every operation
- Handle all errors with toast notifications
- Test on mobile after every major change
- Keep functions small and focused
- Add comments for complex logic
- Use type hints in Python
- Cache expensive calculations
- Update TODO.md after completing tasks

### ❌ DON'T

- Use `alert()` or `confirm()` - Use toast instead
- Use `console.log()` for errors - Use errorHandler
- Add dependencies without strong reason
- Make breaking changes without backward compatibility
- Store sensitive data in localStorage
- Use synchronous operations for I/O
- Hardcode configuration values
- Skip error handling
- Forget mobile responsiveness

---

## Testing Checklist

Before considering any feature complete:

- [ ] Works on Chrome/Firefox/Safari
- [ ] Works on mobile (iOS + Android)
- [ ] Works offline (PWA)
- [ ] Error handling in place
- [ ] Loading states shown
- [ ] Toast notifications for user feedback
- [ ] Responsive design applied
- [ ] No console errors
- [ ] API documented (Swagger)
- [ ] TODO.md updated

---

## Future Vision (12 Months)

**User Acquisition:**
- 10,000 users
- 1,000 paying customers
- ₹5L ARR

**Features:**
- Full tax optimization suite
- Multi-asset tracking (stocks, FD, PPF)
- AI-powered recommendations
- WhatsApp/Telegram bot
- B2B white-label solution

**Technical:**
- Migrate to PostgreSQL
- Mobile apps on Play Store / App Store
- Real-time collaboration
- Advanced analytics with ML

---

## Support & Community

- **GitHub Issues:** Bug reports and feature requests
- **Discussions:** General questions
- **Email:** support@mfhelper.com (future)
- **Twitter:** @mfhelper (future)

---

## Quick Reference

**Start Backend:**
```bash
cd backend
uvicorn app.main:app --reload
```

**Initialize Database:**
```bash
python scripts/load_holdings_to_db.py
```

**Update Holdings:**
```bash
python scripts/weekly_update.py
```

**Refetch/Validate Holdings Data:**
```bash
python scripts/refetch_holdings.py --list-dummy
python scripts/refetch_holdings.py --fund <fund-key>
python scripts/validate_holdings.py
```

**Test API:**
```bash
curl http://localhost:8000/api/holdings/stats
```

---

**Last Updated:** February 13, 2026  
**Version:** 1.0.0-MVP  
**Status:** Active Development

---

*This file helps GitHub Copilot understand the MFHelper project context and provide better code suggestions. Keep it updated as the project evolves!*
