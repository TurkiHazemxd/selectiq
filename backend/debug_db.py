import sqlite3
import os
from datetime import datetime

def debug_database():
    db_path = 'app.db'
    
    if not os.path.exists(db_path):
        print("❌ Database file does not exist!")
        return False
    
    print("✅ Database file exists")
    print(f"📁 File size: {os.path.getsize(db_path)} bytes")
    print(f"📅 Last modified: {datetime.fromtimestamp(os.path.getmtime(db_path))}")
    
    # Connect to the database
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        print("✅ Connected to database successfully")
    except Exception as e:
        print(f"❌ Failed to connect to database: {e}")
        return False
    
    # Check all tables and their structure
    print("\n📊 DATABASE STRUCTURE:")
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()
    
    for table in tables:
        table_name = table[0]
        print(f"\n📋 Table: {table_name}")
        
        # Get table schema
        cursor.execute(f"PRAGMA table_info({table_name})")
        columns = cursor.fetchall()
        print("   Columns:")
        for col in columns:
            print(f"     - {col[1]} ({col[2]})")
        
        # Get row count
        cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
        count = cursor.fetchone()[0]
        print(f"   Rows: {count}")
        
        # Show sample data for job_offer and job_application tables
        if table_name in ['job_offer', 'job_application']:
            cursor.execute(f"SELECT * FROM {table_name} LIMIT 5")
            rows = cursor.fetchall()
            if rows:
                print("   Sample data:")
                for row in rows:
                    print(f"     - {row}")
    
    # Check if we can insert data directly
    print("\n🧪 TESTING DIRECT DATABASE INSERT:")
    try:
        cursor.execute("INSERT INTO job_offer (title, company, description, created_at, is_active) VALUES (?, ?, ?, ?, ?)",
                      ('Test Direct Insert', 'Test Company', 'Test description', datetime.now(), 1))
        conn.commit()
        print("✅ Direct insert successful!")
        
        # Verify the insert worked
        cursor.execute("SELECT COUNT(*) FROM job_offer WHERE title = 'Test Direct Insert'")
        count = cursor.fetchone()[0]
        print(f"✅ Verification: Found {count} test records")
        
    except Exception as e:
        print(f"❌ Direct insert failed: {e}")
        conn.rollback()
    
    conn.close()
    return True

if __name__ == "__main__":
    debug_database()