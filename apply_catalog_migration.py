"""
Apply catalog extension and vehicle compatibility schema updates to MySQL database.
Safe and idempotent.
"""
import os
import mysql.connector
from mysql.connector import Error
from dotenv import load_dotenv

load_dotenv()

def apply_migration():
    conn = None
    try:
        conn = mysql.connector.connect(
            host=os.getenv('DB_HOST', 'localhost'),
            user=os.getenv('DB_USER', 'root'),
            password=os.getenv('DB_PASSWORD', ''),
            database=os.getenv('DB_NAME', 'nk_automobiles')
        )
        cursor = conn.cursor(dictionary=True)
        print("Connected to MySQL database. Applying catalog schema updates...")

        # 1. Modify price to allow NULL
        print("1. Modifying products.price to allow NULL...")
        cursor.execute("ALTER TABLE products MODIFY COLUMN price DECIMAL(10, 2) NULL DEFAULT NULL")
        print("   [OK] products.price modified to allow NULL")

        # 2. Add columns to products if they don't exist
        cursor.execute("SHOW COLUMNS FROM products")
        existing_cols = {col['Field'] for col in cursor.fetchall()}

        new_columns = [
            ("catalog_id", "VARCHAR(50) UNIQUE DEFAULT NULL AFTER product_id"),
            ("part_number", "VARCHAR(100) DEFAULT NULL AFTER brand"),
            ("price_status", "VARCHAR(60) DEFAULT 'VERIFIED_SELLING_PRICE' AFTER price"),
            ("price_source", "VARCHAR(255) DEFAULT NULL AFTER price_status"),
            ("source_url", "VARCHAR(500) DEFAULT NULL AFTER price_source"),
            ("image_status", "VARCHAR(60) DEFAULT 'VERIFIED_PHOTO' AFTER image_url"),
            ("fitment_status", "VARCHAR(60) DEFAULT 'VERIFIED' AFTER specifications"),
            ("is_active", "TINYINT(1) DEFAULT 1 AFTER fitment_status"),
            ("notes", "TEXT DEFAULT NULL AFTER is_active")
        ]

        print("2. Checking / Adding missing columns in products table...")
        for col_name, col_def in new_columns:
            if col_name not in existing_cols:
                try:
                    cursor.execute(f"ALTER TABLE products ADD COLUMN {col_name} {col_def}")
                    print(f"   [OK] Added column '{col_name}'")
                except Error as e:
                    print(f"   [WARN] Could not add '{col_name}': {e}")
            else:
                print(f"   [SKIP] Column '{col_name}' already exists")

        # 3. Initialize verification statuses for existing products
        print("3. Initializing existing products verification status...")
        cursor.execute("""
            UPDATE products 
            SET price_status = 'VERIFIED_SELLING_PRICE',
                image_status = 'VERIFIED_PHOTO',
                fitment_status = 'VERIFIED',
                is_active = 1
            WHERE price_status IS NULL OR price_status = ''
        """)
        conn.commit()
        print(f"   [OK] Initialized existing products")

        # 4. Create product_compatibility table
        print("4. Ensuring product_compatibility table exists...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS product_compatibility (
                compatibility_id INT AUTO_INCREMENT PRIMARY KEY,
                product_id INT NOT NULL,
                vehicle_model VARCHAR(100) NOT NULL,
                fitment_status VARCHAR(60) DEFAULT 'Requires model-year confirmation',
                notes VARCHAR(255) DEFAULT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (product_id) REFERENCES products(product_id) ON DELETE CASCADE,
                UNIQUE KEY uq_product_vehicle (product_id, vehicle_model)
            )
        """)
        print("   [OK] product_compatibility table is ready")

        # 5. Ensure 'General Spares' category exists
        print("5. Checking 'General Spares' category...")
        cursor.execute("SELECT category_id FROM categories WHERE name = 'General Spares'")
        row = cursor.fetchone()
        if not row:
            cursor.execute("""
                INSERT INTO categories (name, description) 
                VALUES ('General Spares', 'Spark plugs, cables, bearings, oils, hardware and general maintenance spares')
            """)
            conn.commit()
            print("   [OK] 'General Spares' category created")
        else:
            print("   [SKIP] 'General Spares' category already exists")

        conn.commit()
        cursor.close()
        print("\nAll database schema updates applied successfully!")
        return True

    except Error as e:
        print(f"Error applying migration: {e}")
        if conn:
            conn.rollback()
        return False
    finally:
        if conn and conn.is_connected():
            conn.close()

if __name__ == '__main__':
    apply_migration()
