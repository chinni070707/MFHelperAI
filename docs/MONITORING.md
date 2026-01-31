# Monitoring & Logging Setup Guide

## 📊 What's Implemented

### 1. **Health Check Endpoints** ✅
- `/api/health` - Liveness probe (is app running?)
- `/api/health/readiness` - Readiness probe (ready to serve traffic?)
- `/api/health/metrics` - Detailed system metrics
- `/api/health/status` - Comprehensive health status
- `/api/health/ping` - Simple uptime check

### 2. **Sentry Integration** ✅
- Automatic error tracking
- Performance monitoring
- Breadcrumbs for debugging
- User context tracking
- SQL query tracking

### 3. **System Metrics** ✅
- CPU usage
- Memory usage
- Disk usage
- Process metrics
- Database connection status
- Request duration tracking

---

## 🚀 Quick Setup

### Install Dependencies

```bash
cd backend
pip install sentry-sdk prometheus-client psutil
```

Or install from requirements.txt:
```bash
pip install -r requirements.txt
```

---

## 🔧 Configuration

### 1. Sentry Setup (Recommended for Production)

#### Step 1: Create Sentry Account
1. Go to [sentry.io](https://sentry.io)
2. Sign up for free account
3. Create a new project (Python/FastAPI)
4. Copy your DSN (Data Source Name)

#### Step 2: Configure Environment Variables

Add to `.env` file:
```bash
# Sentry Configuration
SENTRY_DSN=https://examplePublicKey@o0.ingest.sentry.io/0
ENVIRONMENT=production  # or staging, development
RELEASE_VERSION=1.0.0
DEBUG=false
```

#### Step 3: Test Sentry

```bash
# Start server
python -m uvicorn app.main:app --reload

# Trigger test error
curl http://localhost:8000/api/test-sentry-error
```

Check Sentry dashboard for the error!

---

### 2. Uptime Monitoring

#### Option A: UptimeRobot (Free, Easy)

1. **Sign up**: [uptimerobot.com](https://uptimerobot.com)
2. **Add Monitor**:
   - Monitor Type: HTTP(s)
   - URL: `https://your-domain.com/api/health/ping`
   - Monitoring Interval: 5 minutes
   - Alert: Email, SMS, Slack
3. **Done!** You'll get alerts if site goes down

#### Option B: Better Uptime

1. **Sign up**: [betteruptime.com](https://betteruptime.com)
2. **Create Monitor**:
   - URL: `https://your-domain.com/api/health/readiness`
   - Check Interval: 1 minute
   - Response Time Alert: > 2000ms
3. **Get status page**: `https://status.your-domain.com`

---

### 3. Metrics Dashboard

#### Access Built-in Metrics

```bash
# Get all metrics
curl http://localhost:8000/api/health/metrics | jq

# Get status summary
curl http://localhost:8000/api/health/status | jq
```

#### Example Response:
```json
{
  "cpu": {
    "percent": 15.3,
    "count": 8
  },
  "memory": {
    "total_mb": 16384,
    "available_mb": 8192,
    "used_mb": 8192,
    "percent": 50.0
  },
  "database": {
    "users_count": 150,
    "portfolios_count": 320,
    "holdings_count": 4500,
    "connected": true
  },
  "uptime_seconds": 86400
}
```

---

## 📈 Production Monitoring Stack

### Recommended Setup:

```
┌─────────────────┐
│   Application   │
│   (FastAPI)     │
└────────┬────────┘
         │
         ├─────────────────┐
         │                 │
    ┌────▼────┐      ┌────▼────┐
    │ Sentry  │      │ Uptime  │
    │ (Errors)│      │ Monitor │
    └─────────┘      └─────────┘
         │
    ┌────▼────────┐
    │   Alerts    │
    │ (Email/SMS) │
    └─────────────┘
```

---

## 🔔 Alert Setup

### Sentry Alerts

Configure in Sentry Dashboard:

1. **Error Rate Alert**
   - Condition: More than 10 errors in 5 minutes
   - Action: Email + Slack notification

2. **Performance Alert**
   - Condition: P95 response time > 2 seconds
   - Action: Email notification

3. **New Issue Alert**
   - Condition: New error never seen before
   - Action: Slack notification

### UptimeRobot Alerts

1. **Downtime Alert**
   - If site down for 5 minutes
   - SMS + Email

2. **Response Time Alert**
   - If response > 2 seconds
   - Email notification

---

## 📊 Monitoring Checklist

### Before Production:

- [ ] Sentry DSN configured
- [ ] ENVIRONMENT set to "production"
- [ ] DEBUG set to False
- [ ] UptimeRobot monitor created
- [ ] Email alerts configured
- [ ] Slack webhook added (optional)
- [ ] Test error tracking works
- [ ] Test uptime monitoring works
- [ ] Set up status page

### After Launch:

- [ ] Monitor Sentry dashboard daily
- [ ] Check health metrics weekly
- [ ] Review error trends
- [ ] Optimize slow endpoints
- [ ] Set up custom dashboards

---

## 🧪 Testing

### Test Health Endpoints

```bash
# Test liveness
curl http://localhost:8000/api/health

# Test readiness
curl http://localhost:8000/api/health/readiness

# Test metrics
curl http://localhost:8000/api/health/metrics

# Test status
curl http://localhost:8000/api/health/status

# Test ping
curl http://localhost:8000/api/health/ping
```

### Test Sentry Error Tracking

Add this test endpoint to `main.py`:
```python
@app.get("/api/test-error")
async def test_error():
    """Test endpoint to trigger Sentry error"""
    raise Exception("This is a test error for Sentry!")
```

Then visit: `http://localhost:8000/api/test-error`

Check Sentry dashboard - error should appear!

---

## 📱 Monitoring from Mobile

### Setup PushOver (Mobile Alerts)

1. Install PushOver app on phone
2. Get API key from pushover.net
3. Add to Sentry/UptimeRobot integrations
4. Get instant push notifications for errors!

---

## 🎯 Key Metrics to Monitor

### Application Metrics:
- ✅ Error rate (errors per minute)
- ✅ Response time (P50, P95, P99)
- ✅ Request rate (requests per second)
- ✅ Database query time
- ✅ User count growth
- ✅ Portfolio upload rate

### System Metrics:
- ✅ CPU usage (< 80%)
- ✅ Memory usage (< 80%)
- ✅ Disk usage (< 85%)
- ✅ Database connections
- ✅ Uptime percentage (> 99.9%)

### Business Metrics:
- ✅ Daily active users
- ✅ Portfolio uploads per day
- ✅ Average portfolio value
- ✅ User retention rate

---

## 🚨 Alert Thresholds

### Critical (Immediate Action):
- Site down for > 2 minutes
- Error rate > 50/minute
- Database connection lost
- Disk usage > 95%
- Memory usage > 95%

### Warning (Check Soon):
- Response time > 2 seconds
- Error rate > 10/minute
- CPU usage > 85%
- Memory usage > 85%

### Info (Monitor):
- New error types
- Slow queries
- Unusual traffic patterns

---

## 💡 Pro Tips

1. **Don't Over-Alert**: Start with critical alerts only, add more as needed
2. **Use Sampling**: In production, sample 20% of transactions to save costs
3. **Tag Everything**: Add user_id, portfolio_id tags to errors for debugging
4. **Monitor Trends**: Look at week-over-week trends, not just instant values
5. **Set Budgets**: Alert if costs exceed $X per month

---

## 📚 Resources

- [Sentry Docs](https://docs.sentry.io/)
- [UptimeRobot Guide](https://uptimerobot.com/blog/monitor-website/)
- [FastAPI Monitoring](https://fastapi.tiangolo.com/advanced/middleware/)
- [Health Check Best Practices](https://cloud.google.com/blog/products/containers-kubernetes/kubernetes-best-practices-setting-up-health-checks-with-readiness-and-liveness-probes)

---

## 🎉 Next Steps

1. **Install dependencies**: `pip install -r requirements.txt`
2. **Set up Sentry**: Get free DSN from sentry.io
3. **Add SENTRY_DSN to .env**
4. **Start server**: `python -m uvicorn app.main:app --reload`
5. **Test health endpoints**: Visit `/api/health/status`
6. **Set up UptimeRobot**: Monitor `/api/health/ping`
7. **Go to production!** 🚀

Your app is now production-ready with comprehensive monitoring! 🎊
