# Google Analytics Integration Guide

**Status:** ✅ Installed, ⚙️ Configuration Required  
**Last Updated:** February 6, 2026

---

## 📊 What's Included

### Analytics Tracking Utility
- ✅ Auto-initialization on page load
- ✅ Custom event tracking
- ✅ Page view tracking
- ✅ Time on page tracking
- ✅ Error tracking
- ✅ Pre-defined events for common actions

### Integrated Pages
- ✅ [index.html](../frontend/index.html) - Landing page
- ✅ [dashboard.html](../frontend/dashboard.html) - Main dashboard
- ✅ [admin.html](../frontend/admin.html) - Admin panel

---

## 🚀 Quick Setup (5 minutes)

### Step 1: Create Google Analytics Account

1. Go to [Google Analytics](https://analytics.google.com/)
2. Click **Admin** (gear icon)
3. Click **Create Property**
4. Fill in:
   - Property name: **MFHelper**
   - Timezone: **India**
   - Currency: **INR**
5. Click **Next** → **Create** → Accept terms
6. Choose **Web** platform
7. Enter your website URL
8. Copy your **Measurement ID** (looks like `G-XXXXXXXXXX`)

### Step 2: Add Measurement ID to Code

Edit [frontend/js/analytics.js](../frontend/js/analytics.js):

```javascript
// Line 6 - Replace with your actual ID
const GA_MEASUREMENT_ID = 'G-XXXXXXXXXX'; // ← Paste your ID here
```

### Step 3: Deploy & Test

```powershell
# Start backend
cd backend
python -m uvicorn app.main:app --reload

# Open browser
# http://localhost:8000

# Check browser console for:
# "✓ Google Analytics initialized"
```

### Step 4: Verify in Google Analytics

1. Go to Google Analytics
2. Click **Reports** → **Realtime**
3. Open your website
4. You should see yourself in the realtime report! 🎉

---

## 📈 What Gets Tracked Automatically

### Page Views
- Landing page visits
- Dashboard visits
- Admin panel visits
- Time spent on each page

### User Journey
- New vs returning visitors
- Session duration
- Pages per session
- Bounce rate

---

## 🎯 Custom Events You Can Track

### Portfolio Events
```javascript
// Track portfolio upload
trackPortfolioUpload('excel', 15, 5000000);
// Params: source, fund_count, total_value

// Track manual entry
trackPortfolioUpload('manual', 5, 500000);
```

### User Events
```javascript
// Track sign up
trackSignUp('email');

// Track login
trackLogin('email');
```

### Feature Usage
```javascript
// Track overlap analysis
trackAnalysisTool('overlap');

// Track rebalancing
trackAnalysisTool('rebalance');

// Track XIRR calculation
trackAnalysisTool('xirr');
```

### Export Events
```javascript
// Track PDF export
trackExport('pdf');

// Track Excel export
trackExport('excel');
```

### Search Events
```javascript
// Track fund search
trackSearch('HDFC', 'fund_search');

// Track AMC search
trackSearch('ICICI', 'amc_search');
```

### CTA Clicks
```javascript
// Track button clicks
trackCTAClick('upload_portfolio', 'dashboard');
trackCTAClick('manual_entry', 'dashboard');
trackCTAClick('analyze_portfolio', 'results');
```

### Error Tracking
```javascript
// Track errors
trackError('upload_failed', 'Invalid file format');
trackError('api_error', 'Network timeout');
```

---

## 💡 Example Implementations

### Add to Portfolio Upload
In [dashboard.html](../frontend/dashboard.html), find the upload success handler:

```javascript
// After successful upload
async function handleUploadSuccess(data) {
    // Existing code...
    
    // Track the upload
    trackPortfolioUpload(
        uploadSource,           // 'excel' or 'cas_pdf'
        data.funds.length,      // Number of funds
        data.total_value        // Portfolio value
    );
}
```

### Add to Manual Entry
In [dashboard.html](../frontend/dashboard.html), find manual entry submission:

```javascript
// After saving manual entries
async function saveManualEntries(entries) {
    // Existing code...
    
    // Track manual entry
    trackPortfolioUpload('manual', entries.length, totalValue);
}
```

### Add to Sign Up
In [auth.js](../frontend/js/auth-modals.js) or wherever signup happens:

```javascript
// After successful signup
async function handleSignup(userData) {
    // Existing code...
    
    // Track signup
    trackSignUp('email');
}
```

### Add to Analysis Tools
In [overlap.js](../frontend/js/overlap.js):

```javascript
// When overlap analysis runs
function runOverlapAnalysis() {
    trackAnalysisTool('overlap');
    // Rest of the code...
}
```

---

## 📊 Available Reports in Google Analytics

### 1. Realtime Report
- Current active users
- Pages being viewed now
- Traffic sources (where users come from)

### 2. User Report
- Total users
- New vs returning users
- User demographics
- User behavior flow

### 3. Acquisition Report
- How users find your site
- Direct, organic, social, referral traffic
- Campaign tracking

### 4. Engagement Report
- Page views by page
- Average engagement time
- Events (custom tracking)
- Conversions

### 5. Custom Events Report
Go to **Reports** → **Engagement** → **Events** to see:
- `portfolio_upload` - Track upload sources and volumes
- `analysis_tool_used` - Most popular analysis tools
- `export` - Export format preferences
- `feature_used` - Feature adoption
- `error` - Error frequencies

---

## 🎯 Key Metrics to Monitor

### Growth Metrics
- **Daily Active Users (DAU)**
- **Weekly Active Users (WAU)**
- **New user growth rate**
- **Retention rate**

### Engagement Metrics
- **Average session duration**
- **Pages per session**
- **Bounce rate**
- **Time on key pages**

### Conversion Metrics
- **Sign up conversion rate** (visitors → accounts)
- **Portfolio upload rate** (accounts → portfolios)
- **Feature adoption rate** (which tools are used most)
- **Export rate** (engagement indicator)

### Business Metrics
- **Total portfolios uploaded** (volume)
- **Average portfolio value** (AUM indicator)
- **Popular AMCs** (market insights)
- **Peak usage times** (infrastructure planning)

---

## 🔧 Advanced Configuration

### Custom Dimensions

Add user properties in [analytics.js](../frontend/js/analytics.js):

```javascript
// Set user properties
gtag('set', 'user_properties', {
    user_type: 'premium',
    portfolio_count: 5,
    total_aum_bucket: '10L-25L'
});
```

### Enhanced Measurement

In Google Analytics:
1. Go to **Admin** → **Data Streams**
2. Click your web stream
3. Enable **Enhanced measurement**:
   - ✅ Scrolls
   - ✅ Outbound clicks
   - ✅ Site search
   - ✅ Video engagement
   - ✅ File downloads

---

## 📱 Privacy & Compliance

### GDPR Compliance

Add cookie consent banner to [index.html](../frontend/index.html):

```html
<div id="cookie-consent" style="display:none;">
    <p>We use cookies to improve your experience. By using our site, you agree to our use of cookies.</p>
    <button onclick="acceptCookies()">Accept</button>
    <button onclick="declineCookies()">Decline</button>
</div>

<script>
function acceptCookies() {
    localStorage.setItem('cookies-accepted', 'true');
    document.getElementById('cookie-consent').style.display = 'none';
    initGoogleAnalytics(); // Initialize only after consent
}

function declineCookies() {
    localStorage.setItem('cookies-accepted', 'false');
    document.getElementById('cookie-consent').style.display = 'none';
}

// Check consent on load
if (!localStorage.getItem('cookies-accepted')) {
    document.getElementById('cookie-consent').style.display = 'block';
}
</script>
```

### IP Anonymization

Already enabled in GA4 by default. No additional configuration needed.

---

## 🐛 Troubleshooting

### Not Seeing Data in Google Analytics

**1. Check Measurement ID**
```javascript
// In analytics.js, line 6
const GA_MEASUREMENT_ID = 'G-XXXXXXXXXX'; // Must match your GA property
```

**2. Check Browser Console**
Press F12 → Console, look for:
- ✅ "✓ Google Analytics initialized"
- ❌ Any errors about gtag or analytics

**3. Check Ad Blockers**
- Ad blockers prevent GA from loading
- Test in incognito mode
- Test with different browser

**4. Check GA Realtime Report**
- Go to GA → Reports → Realtime
- Open your site in another tab
- Should see 1 active user (yourself)

### Events Not Showing

**1. Wait 24 hours**
- Custom events take time to appear
- Realtime shows events immediately

**2. Check Event Name**
- Event names are case-sensitive
- Use underscore_case, not camelCase

**3. Test Event Tracking**
```javascript
// In browser console
trackEvent('test_event', { test: 'value' });
// Check Realtime → Events
```

---

## 📖 Resources

### Documentation
- [Google Analytics 4 Docs](https://support.google.com/analytics/answer/10089681)
- [GA4 Event Reference](https://developers.google.com/analytics/devguides/collection/ga4/events)
- [gtag.js Reference](https://developers.google.com/analytics/devguides/collection/gtagjs)

### Useful Links
- [Google Analytics Demo Account](https://support.google.com/analytics/answer/6367342)
- [GA4 vs Universal Analytics](https://support.google.com/analytics/answer/10759417)
- [Privacy Policy Generator](https://www.privacypolicygenerator.info/)

---

## ✅ Checklist

### Initial Setup
- [ ] Create Google Analytics account
- [ ] Copy Measurement ID
- [ ] Update analytics.js with your ID
- [ ] Deploy changes
- [ ] Verify in Realtime report

### Add Event Tracking
- [ ] Portfolio upload events
- [ ] Sign up / login events
- [ ] Analysis tool usage
- [ ] Export events
- [ ] Error tracking

### Monitor & Optimize
- [ ] Check dashboard weekly
- [ ] Track key metrics
- [ ] Identify popular features
- [ ] Find pain points (errors, drop-offs)
- [ ] Optimize based on data

---

## 🎉 You're All Set!

Once configured, you'll be able to see in your Google Analytics dashboard:
- 📊 Real-time users on your site
- 📈 User growth over time
- 🎯 Most popular features
- 💼 Portfolio upload trends
- ⚠️ Error frequencies
- 🌍 User locations
- ⏱️ Peak usage times

**Start with:** Just get the Measurement ID and update analytics.js. Everything else will start working automatically!
