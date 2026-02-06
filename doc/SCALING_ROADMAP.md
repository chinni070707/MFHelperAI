# MFHelper Scaling Implementation Roadmap

**Status:** Planning Phase → Production Ready for 1000+ Users
**Document Created:** February 6, 2026

## Current State Assessment

### ✅ What's Already Good
- FastAPI backend with async support
- SQLAlchemy ORM with basic indexes
- Rate limiting middleware (slowapi) configured
- CORS and security middleware
- Centralized logging
- Sentry error tracking
- Docker support
- Automated tests with Playwright

### ⚠️ Critical Gaps for Scaling
1. **No composite indexes** on frequently queried columns (user_id + date)
2. **No caching layer** - every request hits database
3. **No connection pooling** - SQLite in dev, no pool config for production
4. **No background task queue** - synchronous operations block API
5. **No monitoring** - can't track performance metrics
6. **Rate limiter uses memory** - won't work with multiple servers

---

## Phase 1: Critical Performance (THIS WEEK)
**Goal:** Ready for first 100 users with fast response times

### 1.1 Database Indexes (Priority: CRITICAL)
**Impact:** 10-100x faster queries for user portfolios

**Implementation:**
- [ ] Add composite indexes to models.py
- [ ] Create Alembic migration
- [ ] Test query performance before/after

**Files to modify:**
- `backend/app/models/models.py` - Add `Index()` definitions
- `alembic/versions/` - Create new migration

**Indexes needed:**
```python
# User portfolios lookup
Index('idx_portfolio_user_date', 'user_id', 'created_at')

# Holdings queries
Index('idx_holdings_portfolio', 'portfolio_id', 'user_id')
Index('idx_holdings_user', 'user_id', 'created_at')

# Fund lookups
Index('idx_fund_scheme_isin', 'scheme_code', 'isin')

# Transactions for XIRR
Index('idx_transaction_user_date', 'user_id', 'transaction_date')
Index('idx_transaction_holding', 'holding_id', 'transaction_date')
```

### 1.2 Redis Caching (Priority: CRITICAL)
**Impact:** 50-90% reduction in database queries

**Implementation:**
- [ ] Install Redis locally (WSL or Docker)
- [ ] Create cache utility with decorators
- [ ] Add caching to fund lookups, NAV data, portfolio summaries
- [ ] Update config for Redis URL

**Files to create/modify:**
- `backend/app/utils/cache.py` - NEW FILE
- `backend/app/config.py` - Update REDIS_URL
- `backend/requirements.txt` - Add redis>=5.0.1

**Cache targets:**
- Fund master data (24h TTL)
- NAV prices (1h TTL)
- Portfolio summaries (5min TTL)
- AMC list (24h TTL)

### 1.3 Connection Pooling (Priority: HIGH)
**Impact:** Handle 10x more concurrent users

**Implementation:**
- [ ] Add pool settings to database.py
- [ ] Test with load simulation
- [ ] Monitor pool usage

**Files to modify:**
- `backend/app/database.py`

**Configuration:**
```python
engine = create_engine(
    settings.DATABASE_URL,
    pool_size=20,
    max_overflow=40,
    pool_pre_ping=True,
    pool_recycle=3600
)
```

### 1.4 Response Compression (Priority: MEDIUM)
**Impact:** 70% smaller payloads, faster loading

**Implementation:**
- [ ] Add GZip middleware
- [ ] Test with large portfolio responses

**Files to modify:**
- `backend/app/main.py`

---

## Phase 2: Production Readiness (NEXT WEEK)
**Goal:** Stable, monitored service for 100-500 users

### 2.1 Background Task Queue
**Implementation:** Celery + Redis

**Tasks to move to background:**
- Fund data fetching/scraping
- Portfolio calculations (XIRR, allocations)
- NAV updates
- CAS file parsing

### 2.2 Monitoring & Metrics
**Implementation:** Prometheus + Grafana

**Metrics to track:**
- API response times (p50, p95, p99)
- Database query times
- Cache hit ratio
- Error rates by endpoint
- Active users

### 2.3 Rate Limiter with Redis
**Implementation:** Move from memory to Redis storage

**Why:** Current limiter won't work with load balancer

---

## Phase 3: Scalability (MONTH 1-2)
**Goal:** Ready for 500-1000 users

### 3.1 Database Migration to PostgreSQL
- Move from SQLite to PostgreSQL
- Set up automated backups
- Read replicas for analytics

### 3.2 Horizontal Scaling
- Load balancer (Nginx)
- Multiple FastAPI instances
- Shared Redis cache
- Shared PostgreSQL

### 3.3 CDN for Frontend
- Serve static assets from CDN
- Reduce backend load

---

## Phase 4: Advanced (FUTURE)
**Goal:** 1000+ users with growth capacity

### 4.1 Microservices (if needed)
- Separate fund data service
- Separate calculation engine
- API gateway

### 4.2 Advanced Caching
- Multi-layer cache (Redis + CDN)
- Cache warming strategies
- Intelligent invalidation

### 4.3 Geographic Distribution
- Multi-region deployment
- Data replication
- Edge computing

---

## Implementation Order (Next 7 Days)

### Day 1-2: Database Indexes
1. Add composite indexes to models.py
2. Create and test Alembic migration
3. Measure query performance improvements

### Day 3-4: Redis Caching
1. Install Redis (Docker: `docker run -d -p 6379:6379 redis:alpine`)
2. Create cache utility
3. Add caching to top 5 endpoints
4. Test cache hit rates

### Day 5: Connection Pooling
1. Update database.py with pool settings
2. Load test with Apache Bench
3. Monitor pool metrics

### Day 6: Performance Testing
1. Run load tests (100 concurrent users)
2. Measure improvements
3. Identify remaining bottlenecks

### Day 7: Documentation & Review
1. Update deployment docs
2. Create monitoring dashboard
3. Plan Phase 2

---

## Success Metrics

### Phase 1 Targets (Week 1)
- [ ] API response time < 200ms (p95)
- [ ] Database queries < 50ms (p95)
- [ ] Cache hit ratio > 70%
- [ ] Support 100 concurrent users
- [ ] Zero downtime during deployments

### Phase 2 Targets (Week 2-3)
- [ ] API response time < 100ms (p95)
- [ ] Support 500 concurrent users
- [ ] Error rate < 0.1%
- [ ] Background tasks processing < 1min
- [ ] 99.9% uptime

---

## Quick Wins (Can Do Today)

1. **Add missing indexes** - 2 hours, huge impact
2. **Enable response compression** - 10 minutes
3. **Install Redis locally** - 30 minutes
4. **Add basic caching to fund lookups** - 1 hour

Total: ~4 hours for 10x performance improvement

---

## Resources Needed

### Development
- Redis server (local Docker container)
- Load testing tool (Apache Bench or Locust)
- PostgreSQL for production

### Production (Future)
- Redis Cloud (Free tier → $10/month)
- PostgreSQL hosted (Free tier → $25/month)
- Monitoring service (Free tier)
- Load balancer (Nginx on same server initially)

---

## Questions to Answer

1. **Current user count?** → Determines urgency
2. **Expected growth rate?** → Determines timeline
3. **Budget for infrastructure?** → Determines hosting choices
4. **Critical user flows?** → Determines optimization priorities

---

**Next Action:** Start with Database Indexes (biggest impact, lowest risk)
