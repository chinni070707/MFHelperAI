"""
Database Migration Script: Add OAuth Support to Users Table

This script adds Google OAuth columns to the users table.

Run this with: python add_oauth_support.py
"""
import sys
import os

# Add parent directory to path to import app modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import create_engine, text
from app.config import settings

def run_migration():
    """Add OAuth columns to users table"""
    print("🔧 Starting database migration: Add OAuth support")
    print(f"📁 Database: {settings.DATABASE_URL.split('@')[0] if '@' in settings.DATABASE_URL else 'SQLite'}")
    
    engine = create_engine(settings.DATABASE_URL)
    
    with engine.connect() as conn:
        try:
            # Check if columns already exist
            result = conn.execute(text("PRAGMA table_info(users)"))
            columns = [row[1] for row in result]
            
            migrations_needed = []
            
            if 'oauth_provider' not in columns:
                migrations_needed.append("oauth_provider")
            if 'oauth_id' not in columns:
                migrations_needed.append("oauth_id")
            if 'profile_picture_url' not in columns:
                migrations_needed.append("profile_picture_url")
            
            if not migrations_needed:
                print("✅ Database already has OAuth support. No migration needed.")
                return
            
            print(f"📝 Adding columns: {', '.join(migrations_needed)}")
            
            # Add columns one by one (SQLite doesn't support adding multiple columns at once)
            if 'oauth_provider' in migrations_needed:
                conn.execute(text("ALTER TABLE users ADD COLUMN oauth_provider VARCHAR(50)"))
                print("  ✓ Added oauth_provider column")
            
            if 'oauth_id' in migrations_needed:
                conn.execute(text("ALTER TABLE users ADD COLUMN oauth_id VARCHAR(255)"))
                print("  ✓ Added oauth_id column")
            
            if 'profile_picture_url' in migrations_needed:
                conn.execute(text("ALTER TABLE users ADD COLUMN profile_picture_url VARCHAR(500)"))
                print("  ✓ Added profile_picture_url column")
            
            # Check if hashed_password allows NULL (can't modify in SQLite easily)
            print("  ℹ️  Note: hashed_password column should allow NULL for OAuth users")
            print("     This is already handled in the model definition")
            
            conn.commit()
            
            print("\n✅ Migration completed successfully!")
            print("📚 Next steps:")
            print("   1. Set up Google OAuth credentials (see docs/GOOGLE_OAUTH_SETUP.md)")
            print("   2. Add GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET to .env")
            print("   3. Update frontend/login.html with your Google Client ID")
            print("   4. Restart the backend server")
            
        except Exception as e:
            print(f"\n❌ Migration failed: {str(e)}")
            conn.rollback()
            raise

if __name__ == "__main__":
    try:
        run_migration()
    except KeyboardInterrupt:
        print("\n\n⚠️  Migration cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        sys.exit(1)
