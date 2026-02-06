# MFHelper - Next Actions (Priority Order)

**Last Updated:** February 6, 2026  
**Status:** Phase 1 Complete ✅ → Ready for Testing

---

## 🎯 TODAY (30 minutes)

### 1. Start Redis Locally
```powershell
# Option A: Docker (Recommended)
docker run -d -p 6379:6379 --name mfhelper-redis redis:alpine

# Option B: WSL Ubuntu
wsl
sudo apt-get install redis-server
redis-server --daemonize yes

# Verify Redis is running
docker ps  # OR
redis-cli ping  # Should return "PONG"
```

### 2. Configure Redis URL
```powershell
# Create/update .env file
cd backend
echo "REDIS_URL=redis://localhost:6379/0" > .env

# OR set environment variable
$env:REDIS_URL="redis://localhost:6379/0"
```

### 3. Start Backend and Verify
```powershell
cd backend
python -m uvicorn app.main:app --reload

# Look for these log messages:
# ✓ Redis connected: redis://localhost:6379/0
# ✓ Cache initialized: {'status': 'connected', ...}
# ✓ GZip compression enabled
# Database: ... with connection pool
```

### 4. Test Caching
```powershell
# First request (Cache MISS)
Invoke-WebRequest http://localhost:8000/api/health

# Second request (Cache HIT) - should be faster
Invoke-WebRequest http://localhost:8000/api/health

# Check cache stats
Invoke-WebRequest http://localhost:8000/api/health/cache-stats
```

✅ **Success Criteria:** See "Cache HIT" in logs and faster response times

---

## 🚀 THIS WEEK (4-6 hours)

### Day 1-2: Apply Caching to Top Endpoints (2 hours)

**Highest Impact Endpoints:**

1. **Fund Master List** (`backend/app/routes/funds.py`)
```python
from app.utils.cache import cached

@router.get("/funds")
@cached(key_prefix="fund_list", ttl=86400)  # 24 hours
async def get_funds(amc: str = None, category: str = None):
    # Existing code
```

2. **AMC List** (`backend/app/routes/funds.py`)
```python
@router.get("/funds/amc-list")
@cached(key_prefix="amc_list", ttl=86400)  # 24 hours
async def get_amc_list():
    # Existing code
```

3. **Portfolio Summary** (`backend/app/routes/portfolio.py`)
```python
@router.get("/portfolio/{user_id}")
@cached(key_prefix="portfolio", ttl=300)  # 5 minutes
async def get_portfolio(user_id: int):
    # Existing code
```

4. **NAV Data** (if you have this endpoint)
```python
@cached(key_prefix="nav", ttl=3600)  # 1 hour
```

**Files to modify:**
- `backend/app/routes/funds.py`
- `backend/app/routes/portfolio.py`
- `backend/app/routes/analytics.py`

### Day 3: Load Testing (2 hours)

**Install Apache Bench (included with Apache)**
```powershell
# OR use Python locust
pip install locust
```

**Create load test script** (`backend/test_load.py`):
```python
from locust import HttpUser, task, between

class MFHelperUser(HttpUser):
    wait_time = between(1, 3)
    
    @task(3)
    def view_funds(self):
        self.client.get("/api/funds?amc=HDFC")
    
    @task(2)
    def view_portfolio(self):
        self.client.get("/api/portfolio/1")
    
    @task(1)
    def view_analytics(self):
        self.client.get("/api/analytics/summary")
```

**Run load test:**
```powershell
locust -f backend/test_load.py --host=http://localhost:8000 --users=100 --spawn-rate=10
# Open http://localhost:8089 to view dashboard
```

**Measure:**
- Response times (p50, p95, p99)
- Cache hit rate
- Database queries per second
- Error rate

✅ **Success Criteria:** 
- p95 response time < 200ms
- Cache hit rate > 70%
- Zero errors under 100 concurrent users

### Day 4: Optimize Bottlenecks (2 hours)

Based on load test results:
1. Add caching to slow endpoints
2. Optimize heavy database queries
3. Add pagination where needed
4. Profile slow functions

---

## 📅 NEXT WEEK (Phase 2)

### Priority 1: Background Task Queue (1 day)
**Goal:** Move heavy operations off request thread

**Setup Celery:**
```powershell
pip install celery[redis]
```

**Tasks to move to background:**
- Fund data fetching/scraping
- Portfolio XIRR calculations
- NAV updates
- CAS file parsing

**Expected Impact:** 50% faster API responses

### Priority 2: Monitoring Dashboard (1 day)
**Goal:** Track performance metrics in real-time

**Setup Prometheus + Grafana:**
```powershell
docker-compose up prometheus grafana
```

**Metrics to track:**
- API response times
- Cache hit ratios
- Database query times
- Error rates

### Priority 3: Redis Rate Limiting (2 hours)
**Goal:** Prevent abuse, handle load balancing

**Update rate limiter:**
```python
limiter = Limiter(
    key_func=get_remote_address,
    storage_uri=settings.REDIS_URL  # Instead of memory://
)
```

---

## 📊 Success Metrics Tracking

### Create Dashboard (Google Sheets / Excel)

| Date | p50 (ms) | p95 (ms) | p99 (ms) | Cache Hit % | Errors | Users |
|------|----------|----------|----------|-------------|--------|-------|
| Feb 6 | ? | ? | ? | ? | ? | ? |
| Feb 7 | ? | ? | ? | ? | ? | ? |

**Track daily:**
1. Run load test
2. Record metrics
3. Identify improvements
4. Celebrate wins! 🎉

---

## 🐛 Troubleshooting

### Redis Not Connecting
```powershell
# Check if Redis is running
docker ps | findstr redis

# Check logs
docker logs mfhelper-redis

# Test connection
redis-cli -h localhost -p 6379 ping
```

### Cache Not Working
```powershell
# Check backend logs for:
# "✓ Cache initialized" → Good
# "✗ Cache unavailable" → Redis not configured

# Verify REDIS_URL
$env:REDIS_URL
```

### Slow Queries
```powershell
# Enable SQL query logging
# In backend/app/database.py, set:
# echo=True

# Watch logs for slow queries
# Add indexes for those queries
```

---

## 📖 Quick Reference

### View Documentation
- [PERFORMANCE_IMPROVEMENTS.md](PERFORMANCE_IMPROVEMENTS.md) - What we did
- [SCALING_ROADMAP.md](SCALING_ROADMAP.md) - Long-term plan
- [TESTING_GUIDE.md](../TESTING_GUIDE.md) - Test suite guide

### Common Commands
```powershell
# Start backend
cd backend; python -m uvicorn app.main:app --reload

# Run tests
cd tests; npm test

# Check Redis stats
redis-cli info stats

# View cache keys
redis-cli keys "*"

# Clear all cache
redis-cli FLUSHALL
```

### Quick Cache Test in Python
```python
from app.utils.cache import cache

# Set
cache.set("test_key", {"foo": "bar"}, ttl=60)

# Get
result = cache.get("test_key")
print(result)  # {'foo': 'bar'}

# Stats
print(cache.get_stats())
```

---

## ✅ Completion Checklist

### Phase 1 (Complete)
- [x] Database indexes implemented
- [x] Caching infrastructure created
- [x] Connection pooling configured
- [x] Response compression enabled
- [x] Code committed and pushed

### Phase 1 Validation (This Week)
- [ ] Redis running locally
- [ ] Cache working (see HIT in logs)
- [ ] Caching added to top 5 endpoints
- [ ] Load testing completed
- [ ] Performance metrics collected
- [ ] p95 < 200ms achieved
- [ ] Cache hit rate > 70%

### Phase 2 (Next Week)
- [ ] Celery background tasks
- [ ] Monitoring dashboard
- [ ] Redis rate limiting
- [ ] Load test with 500 users

---

## 🎯 Final Goal

**Production Ready Checklist:**
- [ ] p95 response time < 100ms
- [ ] Cache hit rate > 80%
- [ ] Support 500+ concurrent users
- [ ] Error rate < 0.1%
- [ ] 99.9% uptime
- [ ] Monitoring dashboard live
- [ ] Background tasks operational
- [ ] Rate limiting per user

---

**Start Here:** ⬆️ TODAY section (30 minutes)

**Questions?** Check the documentation or ask!

**Made Progress?** Update this file with ✅ checkmarks!
