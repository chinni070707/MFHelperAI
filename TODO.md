# MFHelper - TODO List

## 🔴 High Priority - Auth & User Management

### Testing & Validation
- [ ] **Write unit tests for auth routes**
  - Test user registration (valid/invalid data)
  - Test login (correct/incorrect credentials)
  - Test protected routes (with/without token)
  - Test user settings CRUD operations
  
- [ ] **Compile TypeScript without errors**
  - Fix import paths in auth-ui.ts (toast.js reference)
  - Ensure all types are properly defined
  - Generate JavaScript output files

- [ ] **Test auth UI in browser**
  - Test registration modal
  - Test login modal
  - Test settings modal with all tabs
  - Test theme switching (light/dark/auto)
  - Test form validation

### Frontend Integration
- [ ] **Add auth buttons to main pages**
  - Add Login/Register buttons to index.html
  - Add Settings button to dashboard
  - Add Logout functionality
  - Show user info in header when logged in

- [ ] **Update existing pages for auth**
  - Add auth checks to dashboard.html
  - Add auth checks to upload functionality
  - Redirect to login if not authenticated
  - Handle 401 responses gracefully

- [ ] **Build TypeScript properly**
  - Set up proper build script in package.json
  - Configure module resolution
  - Add source maps for debugging

### Backend Enhancements
- [ ] **Email Verification**
  - Send verification email on registration
  - Create email verification endpoint
  - Add email templates
  - Configure SMTP settings

- [ ] **Password Reset Flow**
  - Forgot password endpoint
  - Generate reset tokens
  - Send reset email
  - Reset password endpoint

- [ ] **Social Authentication**
  - Google OAuth integration
  - GitHub OAuth integration
  - Link social accounts to existing users

### Database & Data Management
- [ ] **Create database migration system**
  - Use Alembic for migrations
  - Create initial migration
  - Add migration for UserSettings table

- [ ] **Seed database with test data**
  - Create script to add dummy users
  - Create script to add sample portfolios
  - Add sample fund master data

- [ ] **Portfolio history analytics**
  - Create comparison views (month-over-month)
  - Show portfolio growth charts
  - Track category allocation changes over time

## 🟡 Medium Priority - Features

### Portfolio Management
- [ ] **Import from CAS PDF**
  - Parse CAMS CAS files
  - Parse KFintech CAS files
  - Handle merged RTAs format

- [ ] **Automatic data refresh**
  - Implement CAMS API integration
  - Implement KFintech API integration
  - Schedule weekly updates
  - Notify users of portfolio changes

- [ ] **Transaction history**
  - Parse transaction data from CAS
  - Calculate XIRR properly
  - Show transaction timeline

### Analytics & Insights
- [ ] **Overlap analysis**
  - Compare holdings across funds
  - Show stock-level overlaps
  - Calculate overlap percentage

- [ ] **Performance attribution**
  - Show which funds contributed most
  - Compare against benchmarks
  - Show sector-wise performance

- [ ] **Risk metrics**
  - Calculate portfolio beta
  - Calculate Sharpe ratio
  - Show down-capture ratio

### UI/UX Improvements
- [ ] **Responsive design polish**
  - Test on mobile devices
  - Improve touch interactions
  - Optimize for tablets

- [ ] **Accessibility (a11y)**
  - Add ARIA labels
  - Keyboard navigation
  - Screen reader support

- [ ] **Progressive Web App (PWA)**
  - Add service worker
  - Enable offline mode
  - Add app manifest
  - Make installable

## 🟢 Low Priority - Nice to Have

### Advanced Features
- [ ] **Goal-based investing**
  - Set financial goals
  - Track goal progress
  - Suggest allocation changes

- [ ] **Tax planning**
  - LTCG/STCG calculations
  - Tax loss harvesting suggestions
  - Generate tax reports

- [ ] **Alerts & Notifications**
  - Price alerts
  - Allocation drift alerts
  - Rebalancing reminders
  - NAV update notifications

### Admin Features
- [ ] **Admin dashboard**
  - View all users
  - Monitor system health
  - View API usage stats

- [ ] **Fund data management**
  - Bulk import fund data
  - Update NAVs automatically
  - Scrape fund holdings data

### Documentation
- [ ] **API documentation**
  - Complete OpenAPI/Swagger docs
  - Add request/response examples
  - Document authentication flow

- [ ] **User guide**
  - Getting started guide
  - Feature walkthroughs
  - FAQ section
  - Video tutorials

## 🔧 Technical Debt

- [ ] **Code quality**
  - Add linting (ESLint, Pylint)
  - Add code formatting (Prettier, Black)
  - Add pre-commit hooks

- [ ] **Error handling**
  - Standardize error responses
  - Add proper logging
  - Add error tracking (Sentry)

- [ ] **Performance optimization**
  - Add database indexes
  - Implement caching (Redis)
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
✅ User settings & preferences
✅ Database-backed portfolio storage
✅ Portfolio history tracking
✅ Theme support (light/dark/auto)
✅ TypeScript frontend components
✅ 61/61 backend tests passing
✅ Rebalancing calculator
✅ Analytics endpoints

**In Progress:**
🔄 TypeScript compilation fixes
🔄 Frontend integration

**Blocked:**
❌ None currently

---

**Last Updated:** February 1, 2026
