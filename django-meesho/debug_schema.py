import sqlite3
import sys

def debug_schema():
    try:
        conn = sqlite3.connect('db.sqlite3')
        cursor = conn.cursor()
        
        # Check if the table exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='core_productimage'")
        table_exists = cursor.fetchone()
        
        with open('schema_debug.txt', 'w') as f:
            if not table_exists:
                f.write("Table 'core_productimage' does not exist.\n")
                print("Table 'core_productimage' does not exist.")
                return False
            
            f.write("Table 'core_productimage' exists.\n")
            
            # Get table schema
            cursor.execute('PRAGMA table_info(core_productimage)')
            columns = cursor.fetchall()
            
            f.write("\nColumns in core_productimage table:\n")
            for column in columns:
                f.write(f"  {column[1]} ({column[2]})\n")
            
            # Check if 'name' column exists
            name_column_exists = any(column[1] == 'name' for column in columns)
            f.write(f"\n'name' column exists: {name_column_exists}\n")
            
            # Check all tables to see what's in the database
            f.write("\nAll tables in database:\n")
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = cursor.fetchall()
            for table in tables:
                f.write(f"  {table[0]}\n")
        
        conn.close()
        print("Debug information written to schema_debug.txt")
        return name_column_exists
        
    except Exception as e:
        with open('schema_debug.txt', 'w') as f:
            f.write(f"Error checking schema: {e}\n")
        print(f"Error checking schema: {e}")
        return False

if __name__ == "__main__":
    debug_schema()
