# 📋 MFHelper - Development TODO

> **Last Updated:** January 29, 2026  
> **Status:** MVP Development

---

## 🎯 Current Sprint (Week 1-2)

### 🔥 High Priority - Must Complete

- [x] Basic project structure (FastAPI + Frontend)
- [x] Excel file upload & parsing
- [x] Dashboard with portfolio summary
- [x] Market cap allocation chart
- [x] AMC-wise distribution chart
- [x] Investment style classification
- [x] Rebalancing calculator
- [x] PWA setup (manifest, service worker)
- [ ] **Create app icons** (all sizes from SVG)
- [ ] **Deploy to production** (Vercel/Railway)
- [ ] **Test PWA on mobile devices**
- [ ] Fix any Excel parsing edge cases

### 🟡 Medium Priority - This Week

- [ ] XIRR calculator implementation
- [ ] Capital gains statement generator
- [ ] Regular vs Direct plan comparison
- [ ] Basic goal calculator (retirement, education)
- [ ] Add more sample/demo data

### 🔵 Low Priority - Nice to Have

- [ ] Dark/Light theme toggle
- [ ] Export dashboard as PDF
- [ ] Share portfolio via link (encrypted)

---

## 📱 Mobile App TODO

- [x] PWA manifest.json
- [x] Service Worker (sw.js)
- [x] Offline fallback page
- [x] App icon SVG design
- [ ] Generate PNG icons (all sizes)
- [ ] Test install on Android
- [ ] Test install on iOS
- [ ] Add splash screens for iOS
- [ ] Submit to PWA directories

---

## 🚀 Phase 1: Foundation (Month 1-2)

### Backend
- [x] FastAPI setup
- [x] Excel parser with smart column detection
- [x] CAS PDF parser (basic)
- [ ] API rate limiting
- [x] Error logging (Console-based, expandable to Sentry)
- [x] Database setup (SQLite with migration scripts)
- [ ] User authentication (optional)
- [x] API documentation (Swagger auto-generated)

### Frontend
- [x] Landing page
- [x] File upload component
- [x] Dashboard layout
- [x] Portfolio summary cards
- [x] Chart.js integration
- [x] Plotly.js integration
- [x] Responsive design improvements
- [x] Loading states & skeletons
- [x] Error handling UI
- [x] Toast notifications

### Analytics Features
- [x] Market cap allocation
- [x] AMC distribution
- [x] Fund-wise treemap
- [x] Investment style analysis
- [x] Performance waterfall chart
- [x] Portfolio overlap analysis (with visualization)
- [ ] XIRR calculation
- [ ] Rolling returns
- [ ] Drawdown analysis
- [ ] Benchmark comparison

---

## 💎 Phase 2: Differentiation (Month 3-4)

### Tax Optimization
- [ ] LTCG tax harvesting algorithm
- [ ] STCG vs LTCG calculator
- [ ] Grandfathering benefit calculation
- [ ] Exit load warnings
- [ ] Tax liability estimator
- [ ] Capital gains PDF report

### Portfolio Insights
- [x] Portfolio overlap analysis (with heatmap visualization)
- [x] Stock concentration alerts
- [x] Sector exposure overlap
- [ ] Diversification score
- [ ] Fund manager tracking
- [ ] Manager change alerts

### Smart Features
- [ ] Step-up SIP calculator
- [ ] SIP vs Lumpsum comparison
- [ ] Regular to Direct switch savings
- [ ] Goal-based planning wizard
- [ ] What-if scenario analyzer

---

## 🌟 Phase 3: Premium (Month 5-6)

### AI Features
- [ ] GPT-powered fund recommendations
- [ ] Portfolio health score
- [ ] Natural language queries
- [ ] Automated insights generation
- [ ] Risk profiler questionnaire

### Advanced Analytics
- [ ] Factor analysis (Value, Growth, Quality)
- [ ] Attribution analysis
- [ ] Peer comparison (anonymized)
- [ ] Advanced screeners
- [ ] Custom alerts

### Multi-Asset
- [ ] Stock portfolio tracking
- [ ] FD/PPF tracking
- [ ] Real estate valuation
- [ ] Gold/Silver prices
- [ ] Net worth dashboard

---

## 🏢 Phase 4: B2B Features (Month 7+)

### Lead Generation Platform
- [ ] Lead scoring algorithm
- [ ] Distributor dashboard
- [ ] Lead export API
- [ ] CRM integration (Zoho, Salesforce)
- [ ] White-label solution

### API & Integrations
- [ ] Public API for partners
- [ ] Zerodha integration
- [ ] Groww integration
- [ ] Account Aggregator framework
- [ ] WhatsApp bot

### Family Office
- [ ] Multi-PAN support
- [ ] Family portfolio view
- [ ] Succession planning
- [ ] HUF support
- [ ] NRI portfolio

---

## 🐛 Known Bugs

| Bug | Priority | Status |
|-----|----------|--------|
| Excel parsing fails for merged cells | High | Open |
| Chart not responsive on small screens | Medium | Open |
| Service worker cache issues on update | Low | Open |

---

## 💡 Feature Requests (Backlog)

- [ ] Email reports (weekly/monthly digest)
- [ ] Telegram/WhatsApp notifications
- [ ] Voice commands (Hey Siri integration)
- [ ] Apple Watch complication
- [ ] Browser extension for NAV tracking
- [ ] Slack integration for teams
- [ ] Google Sheets integration
- [ ] Mutual fund news feed
- [ ] Fund house AMAs calendar
- [ ] Investment community/forum

---

## 📊 Metrics to Track

### Product Metrics
- [ ] Setup analytics (Google Analytics / Plausible)
- [ ] Track page views
- [ ] Track feature usage
- [ ] Track file upload success rate
- [ ] Track time on dashboard

### Business Metrics
- [ ] User signups
- [ ] Portfolio size distribution
- [ ] Feature adoption rates
- [ ] Conversion to premium
- [ ] Referral tracking

---

## 🔧 Technical Debt

- [ ] Add unit tests for Excel parser
- [ ] Add integration tests for API
- [ ] Refactor dashboard.html (too large)
- [ ] Split JavaScript into modules
- [ ] Add TypeScript for frontend
- [ ] Setup CI/CD pipeline
- [ ] Add code linting (ESLint, Black)
- [ ] Documentation for API
- [ ] Performance optimization
- [ ] Accessibility audit (WCAG)

---

## 📅 Milestones

| Milestone | Target Date | Status |
|-----------|-------------|--------|
| MVP Launch | Feb 15, 2026 | 🟡 In Progress |
| 100 Users | Mar 1, 2026 | ⬜ Not Started |
| Pro Tier Launch | Apr 1, 2026 | ⬜ Not Started |
| 1,000 Users | May 1, 2026 | ⬜ Not Started |
| Play Store Launch | Jun 1, 2026 | ⬜ Not Started |
| Premium Tier | Jul 1, 2026 | ⬜ Not Started |
| 10,000 Users | Sep 1, 2026 | ⬜ Not Started |
| B2B Launch | Oct 1, 2026 | ⬜ Not Started |

---

## 📝 Notes

### Design Decisions
- Using vanilla JS instead of React (simpler, faster for solo dev)
- SQLite for initial launch, migrate to PostgreSQL later
- PWA first approach (no native app initially)
- Direct API calls, no GraphQL (KISS principle)

### Competitors to Watch
- Dezerv Wealth Monitor (HNI focus)
- Kuvera (tax harvesting)
- ET Money Genius (AI recommendations)
- INDMoney (multi-asset)
- Tickertape (screeners)

### Key Learnings
- Excel formats vary wildly - need robust parser
- Users want actionable insights, not just data
- Tax savings is the #1 requested feature
- Mobile-first is essential for Indian users

---

## 🆘 Help Needed

- [ ] UI/UX review from designer
- [ ] Legal review for data privacy
- [ ] Tax consultant for accuracy
- [ ] Beta testers (10-20 users)
- [ ] Content writer for blog/SEO

---

## ✅ Completed (Archive)

### January 2026
- [x] Project setup and structure
- [x] Basic Excel parsing
- [x] Dashboard with 5 summary cards
- [x] 6 interactive charts
- [x] Investment style guide
- [x] Rebalancing calculator
- [x] PWA configuration
- [x] Marketing plan document
- [x] Mobile app guide
- [x] Toast notification system
- [x] Error handling & logging
- [x] Responsive design improvements
- [x] Loading states
- [x] Database setup (SQLite)
- [x] Fund holdings database (30 funds from user's portfolio)
- [x] Portfolio overlap analysis
- [x] Overlap visualization with heatmap
- [x] Weekly auto-update workflow
- [x] **PROFESSIONAL UI REDESIGN**
- [x] **Design system (Dezerv-inspired)**
- [x] **Card-based components**
- [x] **Mobile-first layout**
- [x] **Bottom navigation**
- [x] **Professional color palette**

---

*Update this file regularly to track progress!*
