"""
Quick script to add goal_planning_data column if it doesn't exist
"""
import sqlite3
import os

# Get database path from environment or use default
db_path = os.environ.get('DATABASE_URL', 'sqlite:///./mfhelper.db').replace('sqlite:///', '')

print(f"Connecting to database: {db_path}")

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Check if column exists
cursor.execute("PRAGMA table_info(user_settings)")
columns = [row[1] for row in cursor.fetchall()]

print(f"Current columns in user_settings: {columns}")

if 'goal_planning_data' not in columns:
    print("Adding goal_planning_data column...")
    try:
        cursor.execute("ALTER TABLE user_settings ADD COLUMN goal_planning_data TEXT")
        conn.commit()
        print("✅ Column added successfully!")
    except Exception as e:
        print(f"❌ Error adding column: {e}")
else:
    print("✅ Column already exists!")

conn.close()
