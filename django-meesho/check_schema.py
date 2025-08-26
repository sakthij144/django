import sqlite3
import sys

def check_productimage_schema():
    try:
        conn = sqlite3.connect('db.sqlite3')
        cursor = conn.cursor()
        
        # Check if the table exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='core_productimage'")
        table_exists = cursor.fetchone()
        
        if not table_exists:
            print("Table 'core_productimage' does not exist.")
            return False
        
        # Get table schema
        cursor.execute('PRAGMA table_info(core_productimage)')
        columns = cursor.fetchall()
        
        print("Columns in core_productimage table:")
        for column in columns:
            print(f"  {column[1]} ({column[2]})")
        
        # Check if 'name' column exists
        name_column_exists = any(column[1] == 'name' for column in columns)
        print(f"\n'name' column exists: {name_column_exists}")
        
        conn.close()
        return name_column_exists
        
    except Exception as e:
        print(f"Error checking schema: {e}")
        return False

if __name__ == "__main__":
    check_productimage_schema()
