"""
Test Script - Verify Local vs Production Database Setup

This script helps you test and verify that your database is working correctly
in both local and production environments.

Usage:
    python test_db_connection.py
"""

import sys
import os
from sqlalchemy import create_engine, text
from sqlalchemy.exc import OperationalError
import requests

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.config import settings
from app.database import engine, SessionLocal
from app.models.models import User, Portfolio, Holding


def print_header(title):
    """Print a formatted header"""
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70)


def test_database_connection():
    """Test basic database connectivity"""
    print_header("1. DATABASE CONNECTION TEST")
    
    try:
        # Get database type
        db_type = "SQLite" if "sqlite" in settings.DATABASE_URL else "PostgreSQL"
        db_url_display = settings.DATABASE_URL.split('@')[0] if '@' in settings.DATABASE_URL else settings.DATABASE_URL[:50]
        
        print(f"✓ Database Type: {db_type}")
        print(f"✓ Connection String: {db_url_display}...")
        print(f"✓ DEBUG Mode: {settings.DEBUG}")
        
        # Try to connect
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1"))
            result.fetchone()
        
        print("✓ Connection: SUCCESS")
        
        return True
        
    except Exception as e:
        print(f"✗ Connection: FAILED - {str(e)}")
        return False


def test_pool_info():
    """Display connection pool information"""
    print_header("2. CONNECTION POOL INFO")
    
    try:
        pool = engine.pool
        print(f"✓ Pool Class: {pool.__class__.__name__}")
        
        if hasattr(pool, 'size'):
            print(f"✓ Pool Size: {pool.size()}")
            print(f"✓ Checked Out: {pool.checkedout()}")
            print(f"✓ Overflow: {pool.overflow()}")
        else:
            print("ℹ No pooling (SQLite/NullPool)")
        
        return True
        
    except Exception as e:
        print(f"✗ Pool Info: {str(e)}")
        return False


def test_tables_exist():
    """Check if all required tables exist"""
    print_header("3. DATABASE SCHEMA TEST")
    
    required_tables = ['users', 'user_settings', 'portfolios', 'holdings', 'transactions']
    
    try:
        from sqlalchemy import inspect
        inspector = inspect(engine)
        existing_tables = inspector.get_table_names()
        
        print(f"✓ Found {len(existing_tables)} tables: {', '.join(existing_tables)}")
        
        all_exist = True
        for table in required_tables:
            if table in existing_tables:
                print(f"  ✓ {table} - EXISTS")
            else:
                print(f"  ✗ {table} - MISSING")
                all_exist = False
        
        if all_exist:
            print("✓ All required tables exist")
        else:
            print("⚠ Some tables are missing - run the app once to create them")
        
        return all_exist
        
    except Exception as e:
        print(f"✗ Schema Check: {str(e)}")
        return False


def test_basic_queries():
    """Test basic database operations"""
    print_header("4. DATABASE OPERATIONS TEST")
    
    try:
        db = SessionLocal()
        
        # Count records
        user_count = db.query(User).count()
        portfolio_count = db.query(Portfolio).count()
        holding_count = db.query(Holding).count()
        
        print(f"✓ Users: {user_count}")
        print(f"✓ Portfolios: {portfolio_count}")
        print(f"✓ Holdings: {holding_count}")
        
        if user_count == 0:
            print("\nℹ No users found. Run seed script:")
            print("  python scripts/seed_database.py")
        
        # Test a sample user
        if user_count > 0:
            sample_user = db.query(User).first()
            print(f"\n✓ Sample user: {sample_user.email}")
            
            # Get their portfolios
            user_portfolios = db.query(Portfolio).filter(
                Portfolio.user_id == sample_user.id
            ).count()
            print(f"  - Portfolios: {user_portfolios}")
        
        db.close()
        print("\n✓ Database operations: SUCCESS")
        return True
        
    except Exception as e:
        print(f"✗ Database operations: {str(e)}")
        return False


def test_api_health():
    """Test if API server is running"""
    print_header("5. API SERVER TEST")
    
    # Determine base URL
    if "sqlite" in settings.DATABASE_URL:
        base_url = "http://localhost:8000"
        print(f"Testing local server: {base_url}")
    else:
        base_url = "https://mfhelper.onrender.com"
        print(f"Testing production server: {base_url}")
    
    try:
        response = requests.get(f"{base_url}/health", timeout=10)
        
        if response.status_code == 200:
            print(f"✓ API Health Check: SUCCESS (status {response.status_code})")
            data = response.json()
            print(f"  - Status: {data.get('status')}")
            print(f"  - Database: {data.get('database')}")
            return True
        else:
            print(f"✗ API Health Check: FAILED (status {response.status_code})")
            return False
            
    except requests.exceptions.ConnectionError:
        print(f"✗ API Server: Not running or not accessible")
        print(f"  Start server with: uvicorn app.main:app --reload")
        return False
    except Exception as e:
        print(f"✗ API Health Check: {str(e)}")
        return False


def test_upload_endpoint():
    """Test if upload endpoints are accessible"""
    print_header("6. UPLOAD ENDPOINTS TEST")
    
    base_url = "http://localhost:8000" if "sqlite" in settings.DATABASE_URL else "https://mfhelper.onrender.com"
    
    endpoints = [
        "/api/upload/cas",
        "/api/upload/excel",
        "/api/portfolio/",
    ]
    
    for endpoint in endpoints:
        try:
            # Note: These will return 401/422 without auth, but that means they exist
            response = requests.get(f"{base_url}{endpoint}", timeout=5)
            
            if response.status_code in [200, 401, 422, 405]:  # 405 = Method Not Allowed (GET instead of POST)
                print(f"✓ {endpoint} - Accessible")
            else:
                print(f"⚠ {endpoint} - Unexpected status {response.status_code}")
                
        except requests.exceptions.ConnectionError:
            print(f"✗ {endpoint} - Server not running")
            return False
        except Exception as e:
            print(f"✗ {endpoint} - {str(e)}")
            return False
    
    return True


def run_all_tests():
    """Run all tests and display summary"""
    print("\n")
    print("╔══════════════════════════════════════════════════════════════════╗")
    print("║       MFHelper Database & API Test Suite                        ║")
    print("╚══════════════════════════════════════════════════════════════════╝")
    
    results = {
        "Database Connection": test_database_connection(),
        "Connection Pool": test_pool_info(),
        "Database Schema": test_tables_exist(),
        "Database Operations": test_basic_queries(),
        "API Server": test_api_health(),
        "Upload Endpoints": test_upload_endpoint(),
    }
    
    # Summary
    print_header("📊 TEST SUMMARY")
    
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    for test_name, result in results.items():
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{status:8} {test_name}")
    
    print(f"\n{'='*70}")
    print(f"  Results: {passed}/{total} tests passed")
    
    if passed == total:
        print(f"  Status: ✓ ALL TESTS PASSED")
        print(f"{'='*70}\n")
        return 0
    else:
        print(f"  Status: ✗ SOME TESTS FAILED")
        print(f"{'='*70}\n")
        return 1


if __name__ == "__main__":
    try:
        exit_code = run_all_tests()
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n\nTest interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n✗ Fatal error: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
