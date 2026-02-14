import sys
import sqlite3
from pathlib import Path

def count_blog_posts(db_path):
    """Count blog posts in a database"""
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM blog_posts")
        count = cursor.fetchone()[0]
        conn.close()
        return count
    except Exception as e:
        return f"Error: {e}"

# Check both databases
root_db = "mfhelper.db"
backend_db = "backend/mfhelper.db"

print(f"\n📊 Database Comparison:\n")
print(f"Root DB ({root_db}):")
print(f"  Blog posts: {count_blog_posts(root_db)}")

print(f"\nBackend DB ({backend_db}):")
print(f"  Blog posts: {count_blog_posts(backend_db)}")
