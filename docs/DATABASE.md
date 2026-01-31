# Database Information

## Current Database Setup

**Database Type:** SQLite (Local Development)  
**Location:** `backend/mfhelper.db`  
**Connection String:** `sqlite:///./mfhelper.db`

### Why SQLite for Development?

✅ **Zero Configuration** - No separate database server needed  
✅ **File-based** - Easy to backup, copy, and reset  
✅ **Fast Development** - Instant setup, no installation  
✅ **Portable** - Works on Windows, Mac, Linux  

### Database Schema

#### Tables

1. **users** - User accounts
   - id, email, hashed_password, full_name
   - pan, phone, is_active, is_verified
   - created_at, updated_at

2. **user_settings** - User preferences
   - id, user_id (FK)
   - theme, language, currency, date_format
   - email_notifications, portfolio_alerts, market_updates
   - default_view, show_xirr, group_by

3. **portfolios** - Portfolio snapshots (versioned)
   - id, user_id (FK), name, source
   - snapshot_date (when uploaded)
   - total_invested, total_current, total_gain, xirr
   - allocation percentages

4. **holdings** - Individual fund holdings
   - id, user_id (FK), portfolio_id (FK)
   - fund_name, amc, category, sub_category
   - units, nav, invested_amount, current_value
   - gain_loss, return_pct
   - performance metrics (1Y, 3Y, alpha, beta, etc.)

5. **transactions** - Fund transactions (for XIRR)
   - id, user_id (FK), holding_id (FK)
   - transaction_type, date, amount, units, nav

6. **fund_master** - Master fund data
   - id, scheme_code, isin, scheme_name
   - amc, category, performance data

## 🚀 Quick Start

### 1. Create Database & Tables

Tables are automatically created when you start the server:

```bash
cd backend
uvicorn app.main:app --reload
```

### 2. Seed with Test Data

Run the seeding script to add dummy users and portfolios:

```bash
cd backend
python scripts/seed_database.py
```

This will create:
- **3 test users** with different portfolios
- **2 portfolio snapshots** for demo user (showing history)
- **Sample holdings** with realistic data

### 3. Test Accounts

After seeding, you can login with:

| Email | Password | Description |
|-------|----------|-------------|
| demo@mfhelper.com | Demo@123 | Demo user with 2 portfolio snapshots |
| test@example.com | Test@123 | Test user with 1 portfolio |
| investor@example.com | Invest@123 | Another test user |

## 🔍 Viewing Database

### Option 1: SQLite Browser (GUI)

Download [DB Browser for SQLite](https://sqlitebrowser.org/)

1. Open `backend/mfhelper.db`
2. Browse data, run queries, export data

### Option 2: Command Line

```bash
cd backend
sqlite3 mfhelper.db

# List tables
.tables

# View users
SELECT id, email, full_name, is_active FROM users;

# View portfolios
SELECT id, user_id, name, snapshot_date, total_current FROM portfolios;

# View holdings
SELECT fund_name, category, current_value, return_pct FROM holdings WHERE portfolio_id = 1;

# Exit
.quit
```

### Option 3: Python Script

```python
from sqlalchemy import create_engine
from app.models.models import User, Portfolio, Holding

engine = create_engine("sqlite:///./mfhelper.db")
from sqlalchemy.orm import sessionmaker
Session = sessionmaker(bind=engine)
db = Session()

# Get all users
users = db.query(User).all()
for user in users:
    print(f"{user.email} - {user.full_name}")

# Get portfolios with holdings count
portfolios = db.query(Portfolio).all()
for p in portfolios:
    holdings_count = db.query(Holding).filter(Holding.portfolio_id == p.id).count()
    print(f"Portfolio {p.id}: {p.name} - {holdings_count} holdings")
```

## 🗄️ Database Operations

### Reset Database

To start fresh:

```bash
cd backend
rm mfhelper.db  # Delete database file
python scripts/seed_database.py  # Recreate with test data
```

### Backup Database

```bash
cd backend
cp mfhelper.db mfhelper_backup_$(date +%Y%m%d).db
```

### Export Data

```bash
cd backend
sqlite3 mfhelper.db .dump > backup.sql
```

### Import Data

```bash
cd backend
sqlite3 mfhelper.db < backup.sql
```

## 🔄 Migrations (Future)

For production, we'll use **Alembic** for database migrations:

```bash
# Initialize Alembic
alembic init alembic

# Create migration
alembic revision --autogenerate -m "Add new field"

# Apply migration
alembic upgrade head

# Rollback
alembic downgrade -1
```

## 🚀 Production Database

For production deployment, switch to **PostgreSQL**:

### Update config.py:

```python
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://user:password@localhost/mfhelper"
)
```

### Install PostgreSQL driver:

```bash
pip install psycopg2-binary asyncpg
```

### Migration:

1. Export SQLite data
2. Create PostgreSQL database
3. Import data
4. Update connection string

## 📊 Sample Queries

### Get user's latest portfolio

```sql
SELECT p.*, u.email 
FROM portfolios p 
JOIN users u ON p.user_id = u.id 
WHERE u.email = 'demo@mfhelper.com' 
ORDER BY p.snapshot_date DESC 
LIMIT 1;
```

### Portfolio history for comparison

```sql
SELECT 
    snapshot_date,
    total_invested,
    total_current,
    total_gain,
    ROUND((total_gain * 100.0 / total_invested), 2) as return_pct
FROM portfolios 
WHERE user_id = 1 
ORDER BY snapshot_date DESC;
```

### Holdings by category

```sql
SELECT 
    category,
    COUNT(*) as fund_count,
    SUM(current_value) as total_value,
    SUM(gain_loss) as total_gain
FROM holdings 
WHERE portfolio_id = 1 
GROUP BY category 
ORDER BY total_value DESC;
```

### Best performing funds

```sql
SELECT 
    fund_name,
    category,
    return_pct,
    one_year_return,
    alpha
FROM holdings 
WHERE portfolio_id = 1 
ORDER BY return_pct DESC 
LIMIT 5;
```

## 🔧 Troubleshooting

### Database locked error

SQLite doesn't handle concurrent writes well. For high concurrency:
1. Use PostgreSQL in production
2. Enable WAL mode: `PRAGMA journal_mode=WAL;`

### Database not found

Make sure you're in the `backend` directory when running the app:
```bash
cd backend
uvicorn app.main:app --reload
```

### Permission denied

On Linux/Mac, ensure write permissions:
```bash
chmod 644 mfhelper.db
```

## 📚 Resources

- [SQLite Documentation](https://www.sqlite.org/docs.html)
- [SQLAlchemy ORM](https://docs.sqlalchemy.org/)
- [DB Browser for SQLite](https://sqlitebrowser.org/)
- [Alembic Migrations](https://alembic.sqlalchemy.org/)
