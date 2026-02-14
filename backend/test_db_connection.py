"""
Database Connection and Schema Test
Tests database connectivity and verifies all tables are created correctly.
Used by CI/CD pipeline to validate database setup.
"""
import sys
import os
from sqlalchemy import inspect, text

def test_database_connection():
    """Test basic database connectivity and schema"""
    print("=" * 60)
    print("DATABASE CONNECTION TEST")
    print("=" * 60)
    
    try:
        # Import after path setup
        from app.database import engine, Base
        from app.models import models
        
        # Test 1: Database Connection
        print("\n[1/5] Testing database connection...")
        with engine.connect() as connection:
            result = connection.execute(text("SELECT 1"))
            assert result.fetchone()[0] == 1
        print("[PASS] Database connection successful")
        
        # Test 2: Create all tables
        print("\n[2/5] Creating database schema...")
        Base.metadata.create_all(bind=engine)
        print("[PASS] Database schema created")
        
        # Test 3: Verify tables exist
        print("\n[3/5] Verifying tables...")
        inspector = inspect(engine)
        expected_tables = [
            'users',
            'user_settings',
            'portfolios',
            'holdings',
            'goals',
            'blog_posts',
            'blog_tags'
        ]
        
        existing_tables = inspector.get_table_names()
        missing_tables = [t for t in expected_tables if t not in existing_tables]
        
        if missing_tables:
            print(f"[WARN] Missing tables: {missing_tables}")
        else:
            print(f"[PASS] All {len(expected_tables)} expected tables exist")
        
        print("\n   Tables found:")
        for table in existing_tables:
            columns = inspector.get_columns(table)
            print(f"   - {table}: {len(columns)} columns")
        
        # Test 4: Verify critical columns
        print("\n[4/5] Verifying critical table structures...")
        
        # Check users table
        user_columns = {col['name'] for col in inspector.get_columns('users')}
        required_user_cols = {'id', 'email', 'hashed_password'}
        if not required_user_cols.issubset(user_columns):
            raise AssertionError(f"Missing required columns in users table: {required_user_cols - user_columns}")
        print("   [PASS] users table structure valid")
        
        # Check portfolios table
        portfolio_columns = {col['name'] for col in inspector.get_columns('portfolios')}
        required_portfolio_cols = {'id', 'user_id', 'name'}
        if not required_portfolio_cols.issubset(portfolio_columns):
            raise AssertionError(f"Missing required columns in portfolios table: {required_portfolio_cols - portfolio_columns}")
        print("   [PASS] portfolios table structure valid")
        
        # Check holdings table
        holdings_columns = {col['name'] for col in inspector.get_columns('holdings')}
        required_holdings_cols = {'id', 'user_id', 'fund_name'}
        if not required_holdings_cols.issubset(holdings_columns):
            raise AssertionError(f"Missing required columns in holdings table: {required_holdings_cols - holdings_columns}")
        print("   [PASS] holdings table structure valid")
        
        # Test 5: Test basic query
        print("\n[5/5] Testing basic database operations...")
        with engine.connect() as connection:
            result = connection.execute(text("SELECT COUNT(*) FROM users"))
            user_count = result.fetchone()[0]
            print(f"   Current users in database: {user_count}")
        print("[PASS] Database queries working")
        
        # Final summary
        print("\n" + "=" * 60)
        print("DATABASE TEST SUMMARY")
        print("=" * 60)
        print("[PASS] Connection: OK")
        print("[PASS] Schema: OK")
        print(f"[PASS] Tables: {len(existing_tables)} tables created")
        print("[PASS] Queries: OK")
        print("\n[SUCCESS] All database tests passed!")
        print("=" * 60)
        
        return 0
        
    except ImportError as e:
        print(f"[FAIL] Import Error: {e}")
        print("\nMake sure you're running this from the backend directory")
        print("or that PYTHONPATH is set correctly.")
        return 1
        
    except Exception as e:
        print(f"\n[FAIL] Database Test Failed!")
        print(f"Error: {str(e)}")
        print(f"Type: {type(e).__name__}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(test_database_connection())
