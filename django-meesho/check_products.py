import sqlite3
import os

def check_all_products():
    try:
        conn = sqlite3.connect('db.sqlite3')
        cursor = conn.cursor()
        
        # Check if products table exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='core_product'")
        table_exists = cursor.fetchone()
        
        if not table_exists:
            print("Products table does not exist!")
            return
        
        # Get all products
        cursor.execute('SELECT id, name, price, stock, is_available FROM core_product')
        products = cursor.fetchall()
        
        print(f"Total products found: {len(products)}")
        print("\nProducts in database:")
        print("-" * 50)
        for product in products:
            print(f"ID: {product[0]}, Name: {product[1]}, Price: {product[2]}, Stock: {product[3]}, Available: {product[4]}")
        
        # Check if there are any backup files
        backup_files = [f for f in os.listdir('.') if f.endswith('.sqlite3.bak') or f.endswith('.backup')]
        if backup_files:
            print(f"\nBackup files found: {backup_files}")
        else:
            print("\nNo backup files found in current directory")
            
        conn.close()
        
    except Exception as e:
        print(f"Error checking products: {e}")

if __name__ == "__main__":
    check_all_products()
