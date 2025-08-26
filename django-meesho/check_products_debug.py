import sqlite3
import os

def check_all_products():
    try:
        conn = sqlite3.connect('db.sqlite3')
        cursor = conn.cursor()
        
        # Check if products table exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='core_product'")
        table_exists = cursor.fetchone()
        
        with open('products_debug.txt', 'w') as f:
            if not table_exists:
                f.write("Products table does not exist!\n")
                print("Products table does not exist!")
                return
            
            # Get all products
            cursor.execute('SELECT id, name, price, stock, is_available FROM core_product')
            products = cursor.fetchall()
            
            f.write(f"Total products found: {len(products)}\n")
            f.write("\nProducts in database:\n")
            f.write("-" * 50 + "\n")
            for product in products:
                f.write(f"ID: {product[0]}, Name: {product[1]}, Price: {product[2]}, Stock: {product[3]}, Available: {product[4]}\n")
            
            # Check if there are any backup files
            backup_files = [f for f in os.listdir('.') if f.endswith('.sqlite3.bak') or f.endswith('.backup')]
            if backup_files:
                f.write(f"\nBackup files found: {backup_files}\n")
            else:
                f.write("\nNo backup files found in current directory\n")
                
            conn.close()
            
            print("Debug information written to products_debug.txt")
            
    except Exception as e:
        with open('products_debug.txt', 'w') as f:
            f.write(f"Error checking products: {e}\n")
        print(f"Error checking products: {e}")

if __name__ == "__main__":
    check_all_products()
