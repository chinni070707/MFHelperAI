"""
Quick database seeding script - run directly without import issues
"""
import sqlite3
from datetime import datetime, timedelta
import hashlib
import os

# Database path
db_path = os.path.join(os.path.dirname(__file__), '..', 'mfhelper.db')

def hash_password(password):
    """Simple password hashing for demo"""
    # In production, this uses bcrypt, but for quick seeding we'll use a simple hash
    return f"$2b$12${hashlib.sha256(password.encode()).hexdigest()[:50]}"

def seed_db():
    print("[CONNECT] Connecting to database...")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    print("[SUCCESS] Connected to:", db_path)
    
    # Check if data exists
    cursor.execute("SELECT COUNT(*) FROM users")
    user_count = cursor.fetchone()[0]
    
    if user_count > 0:
        print(f"[WARNING] Database already has {user_count} users.")
        response = input("Clear and reseed? (yes/no): ")
        if response.lower() != 'yes':
            print("[ERROR] Cancelled")
            return
        
        # Clear data
        cursor.execute("DELETE FROM holdings")
        cursor.execute("DELETE FROM portfolios")
        cursor.execute("DELETE FROM user_settings")
        cursor.execute("DELETE FROM users")
        conn.commit()
        print("[CLEAR] Cleared existing data")
    
    # Insert users
    users = [
        (1, 'demo@mfhelper.com', hash_password('Demo@123'), 'Demo User', 'ABCDE1234F', '+91 98765 43210', 1, 1),
        (2, 'test@example.com', hash_password('Test@123'), 'Test User', 'XYZAB5678C', '+91 99999 88888', 1, 1),
        (3, 'investor@example.com', hash_password('Invest@123'), 'Smart Investor', 'PQRST9012D', '+91 88888 77777', 1, 1)
    ]
    
    cursor.executemany('''
        INSERT INTO users (id, email, hashed_password, full_name, pan, phone, is_active, is_verified)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    ''', users)
    
    print("[SUCCESS] Created 3 users")
    
    # Insert user settings
    settings = [
        (1, 1, 'light', 'en', 'INR', 'DD/MM/YYYY', 1, 1, 0, 'summary', 1, 'category'),
        (2, 2, 'dark', 'en', 'INR', 'DD/MM/YYYY', 1, 1, 0, 'summary', 1, 'category'),
        (3, 3, 'auto', 'en', 'INR', 'DD/MM/YYYY', 1, 1, 0, 'summary', 1, 'category')
    ]
    
    cursor.executemany('''
        INSERT INTO user_settings (id, user_id, theme, language, currency, date_format,
                                   email_notifications, portfolio_alerts, market_updates,
                                   default_view, show_xirr, group_by)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', settings)
    
    print("[SUCCESS] Created settings for all users")
    
    # Insert portfolios
    now = datetime.now().isoformat()
    last_month = (datetime.now() - timedelta(days=30)).isoformat()
    
    portfolios = [
        (1, 1, 'My Portfolio', 'excel', now, 500000, 575000, 75000, 12.5, 0, 0, 0),
        (2, 1, 'My Portfolio', 'excel', last_month, 480000, 520000, 40000, 10.2, 0, 0, 0),
        (3, 2, 'Test Portfolio', 'cas_pdf', now, 300000, 340000, 40000, 11.8, 0, 0, 0)
    ]
    
    cursor.executemany('''
        INSERT INTO portfolios (id, user_id, name, source, snapshot_date,
                              total_invested, total_current, total_gain, xirr,
                              large_cap_pct, mid_cap_pct, small_cap_pct)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', portfolios)
    
    print("[SUCCESS] Created 3 portfolios (including historical snapshot)")
    
    # Insert holdings for portfolio 1 (current)
    holdings1 = [
        (1, 1, 1, 'HDFC Flexi Cap Fund - Direct Plan - Growth', 'HDFC Mutual Fund', 'Flexi Cap', None,
         1234.56, 145.80, 150000, 180000, 30000, 20.0, 18.5, 15.2, 2.3, None, None, None, None),
        (2, 1, 1, 'Parag Parikh Flexi Cap Fund - Direct Plan - Growth', 'PPFAS Mutual Fund', 'Flexi Cap', None,
         2345.67, 49.05, 100000, 115000, 15000, 15.0, 16.8, 14.5, 1.8, None, None, None, None),
        (3, 1, 1, 'Axis Midcap Fund - Direct Plan - Growth', 'Axis Mutual Fund', 'Mid Cap', None,
         1567.89, 92.47, 125000, 145000, 20000, 16.0, 22.3, 18.7, 3.2, None, None, None, None),
        (4, 1, 1, 'Kotak Small Cap Fund - Direct Plan - Growth', 'Kotak Mahindra Mutual Fund', 'Small Cap', None,
         8901.23, 15.17, 125000, 135000, 10000, 8.0, 25.6, 20.1, 4.5, None, None, None, None)
    ]
    
    # Insert holdings for portfolio 2 (historical)
    holdings2 = [
        (5, 1, 2, 'HDFC Flexi Cap Fund - Direct Plan - Growth', 'HDFC Mutual Fund', 'Flexi Cap', None,
         1234.56, 136.10, 150000, 168000, 18000, 12.0, 16.5, 14.8, None, None, None, None, None),
        (6, 1, 2, 'Parag Parikh Flexi Cap Fund - Direct Plan - Growth', 'PPFAS Mutual Fund', 'Flexi Cap', None,
         2345.67, 46.04, 100000, 108000, 8000, 8.0, 14.2, 13.1, None, None, None, None, None),
        (7, 1, 2, 'Axis Midcap Fund - Direct Plan - Growth', 'Axis Mutual Fund', 'Mid Cap', None,
         1567.89, 87.99, 125000, 138000, 13000, 10.4, 20.1, 17.3, None, None, None, None, None),
        (8, 1, 2, 'Kotak Small Cap Fund - Direct Plan - Growth', 'Kotak Mahindra Mutual Fund', 'Small Cap', None,
         7234.56, 14.65, 105000, 106000, 1000, 0.95, 23.8, 19.2, None, None, None, None, None)
    ]
    
    # Holdings for portfolio 3
    holdings3 = [
        (9, 2, 3, 'SBI Bluechip Fund - Direct Plan - Growth', 'SBI Mutual Fund', 'Large Cap', None,
         3456.78, 66.55, 200000, 230000, 30000, 15.0, None, None, None, None, None, None, None),
        (10, 2, 3, 'Nippon India Small Cap Fund - Direct Plan - Growth', 'Nippon India Mutual Fund', 'Small Cap', None,
         1234.56, 89.11, 100000, 110000, 10000, 10.0, None, None, None, None, None, None, None)
    ]
    
    all_holdings = holdings1 + holdings2 + holdings3
    
    cursor.executemany('''
        INSERT INTO holdings (id, user_id, portfolio_id, fund_name, amc, category, sub_category,
                            units, nav, invested_amount, current_value, gain_loss, return_pct,
                            one_year_return, three_year_return, alpha, beta, sharpe_ratio,
                            down_capture, last_transaction_date)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', all_holdings)
    
    print(f"[SUCCESS] Created {len(all_holdings)} holdings")
    
    conn.commit()
    conn.close()
    
    print("\n" + "="*60)
    print("[DONE] Database seeded successfully!")
    print("="*60)
    print("\n[INFO] Summary:")
    print("   Users: 3")
    print("   Portfolios: 3 (including historical)")
    print("   Holdings: 10")
    
    print("\n[KEY] Test Accounts:")
    print("   Email: demo@mfhelper.com / Demo@123")
    print("   Email: test@example.com / Test@123")
    print("   Email: investor@example.com / Invest@123")
    
    print(f"\n[INFO] Database: {db_path}")
    print("\n[INFO] Next steps:")
    print("   1. Start server (if not running): uvicorn app.main:app --reload")
    print("   2. Test login: POST /api/auth/login")
    print("   3. View portfolio: GET /api/portfolio/")
    print()

if __name__ == '__main__':
    seed_db()
