# MFHelper - Fund Data Infrastructure

## Overview

This system fetches, stores, and classifies mutual fund data including:
- Stock holdings in each fund
- Market cap classifications (Large/Mid/Small cap)
- Sector allocations
- Historical versioning

## Data Sources

### 1. **Market Cap Data (NSE)**
- **Source**: NSE API / Website
- **Frequency**: Daily (we fetch weekly)
- **Data**: Stock symbols, market caps, sectors
- **Classification**: 
  - Large Cap: ≥ ₹20,000 Cr
  - Mid Cap: ₹5,000 - ₹20,000 Cr
  - Small Cap: < ₹5,000 Cr

### 2. **Fund Holdings**
- **Source**: ValueResearch Online (web scraping)
- **Frequency**: Monthly (fund factsheets)
- **Alternative Sources**:
  - MFCentral API (requires registration)
  - Morningstar India (paid)
  - AMFI website (basic data only)

## Database Schema

### Core Tables

#### `stocks`
Master table for all stocks
```sql
- symbol (NSE symbol)
- company_name
- market_cap (current)
- market_cap_category (Large/Mid/Small)
- sector
```

#### `stock_market_cap_history`
Historical market cap for versioning
```sql
- stock_id
- market_cap
- market_cap_category
- effective_date (weekly snapshot)
```

#### `fund_holding_snapshots`
Versioned fund holdings
```sql
- fund_id
- stock_symbol
- weight (percentage)
- market_cap_category (at that time)
- as_of_date (fund factsheet date)
```

#### `fund_classifications`
Pre-calculated fund classifications
```sql
- fund_id
- large_cap_percentage
- mid_cap_percentage
- small_cap_percentage
- top_sectors
- as_of_date
```

## Usage

### 1. Initial Setup

```bash
# Install dependencies
pip install beautifulsoup4 apscheduler

# Run migrations (create tables)
python -m alembic upgrade head
```

### 2. Manual Data Update

```bash
# Update market caps
curl -X POST http://localhost:8000/api/data/update/market-caps

# Update specific fund holdings
curl -X POST http://localhost:8000/api/data/update/fund-holdings/123?fund_name=HDFC+Flexi+Cap+Fund

# Trigger full weekly update
curl -X POST http://localhost:8000/api/data/update/weekly
```

### 3. Automated Weekly Updates

The scheduler runs automatically every **Sunday at 2:00 AM IST**.

Check scheduler status:
```bash
# View update logs
curl http://localhost:8000/api/data/update/logs
```

### 4. Query Fund Classification

```bash
# Get Large/Mid/Small cap breakdown for a fund
curl http://localhost:8000/api/data/fund/123/classification
```

Response:
```json
{
  "fund_id": 123,
  "as_of_date": "2026-02-01",
  "allocation": {
    "large_cap": 65.5,
    "mid_cap": 25.3,
    "small_cap": 9.2
  },
  "top_sectors": [
    {"sector": "Financial Services", "weight": 28.5},
    {"sector": "Technology", "weight": 18.2},
    {"sector": "Consumer Goods", "weight": 12.1}
  ],
  "number_of_stocks": 42
}
```

## How Classification Works

1. **Fetch Holdings**: Get stock list with weights from fund factsheet
2. **Match Stocks**: Look up each stock in `stocks` table
3. **Get Market Cap**: Get latest market cap from `stock_market_cap_history`
4. **Calculate**: Sum weights by category
   ```python
   large_cap_% = sum(weight for stocks where market_cap >= 20000 Cr)
   mid_cap_% = sum(weight for stocks where 5000 <= market_cap < 20000)
   small_cap_% = sum(weight for stocks where market_cap < 5000)
   ```
5. **Store**: Save in `fund_classifications` table

## Versioning Strategy

- **Market Caps**: Weekly snapshots in `stock_market_cap_history`
- **Fund Holdings**: Monthly snapshots when factsheets are published
- **Classification**: Calculated for each holdings snapshot

This allows:
- Historical analysis: "How did classification change over time?"
- Accurate backtesting: Use classification from specific date
- Audit trail: See when data was updated

## Data Quality

### Handling Missing Data

1. **Stock Not Found**: 
   - Create new stock record
   - Use fund-provided sector
   - Mark market cap as NULL

2. **Market Cap Unavailable**:
   - Use previous week's data
   - Or classify as "Unknown"

3. **Holdings Not Available**:
   - Log warning
   - Keep previous month's data
   - Flag fund for manual review

## Monitoring

### Update Logs
All updates are logged in `data_update_log`:
```sql
SELECT * FROM data_update_log 
ORDER BY started_at DESC 
LIMIT 10;
```

### Data Freshness
```sql
-- Check latest market cap update
SELECT MAX(effective_date) FROM stock_market_cap_history;

-- Check latest fund holdings
SELECT fund_id, MAX(as_of_date) 
FROM fund_holding_snapshots 
GROUP BY fund_id;
```

## Future Enhancements

1. **API Integration**: Replace web scraping with official APIs
   - MFCentral API (requires approval)
   - AMFI API (if available)

2. **Real-time Updates**: Use websockets for live NAV updates

3. **ML Classification**: Auto-detect fund category from holdings

4. **Data Validation**: Cross-check with multiple sources

5. **Cache Layer**: Redis for frequently accessed classifications

## Cost Optimization

- **Storage**: ~100MB for 1000 funds x 12 months x 50 stocks
- **Compute**: Weekly job runs ~30 mins
- **Network**: ~1000 HTTP requests/week (rate-limited)

## Legal Considerations

- **Web Scraping**: ValueResearch TOS - check if allowed
- **Fair Use**: Only for non-commercial / educational use
- **Rate Limiting**: Max 1 request/second
- **Caching**: Cache for 24 hours to reduce load

## Support

For issues or questions, check:
- Update logs: `GET /api/data/update/logs`
- Error logs: `backend/logs/mfhelper_*.log`
- Database: SQLite at `backend/mfhelper.db`
