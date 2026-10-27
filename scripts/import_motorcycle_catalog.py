"""
NK Automobiles — 160-Product Motorcycle Spare-Parts Catalog Import Script
Idempotent, safe, and validates data before writing to MySQL database.
"""

import os
import sys
import json
import shutil
import argparse
from decimal import Decimal
import mysql.connector
from mysql.connector import Error
from dotenv import load_dotenv

load_dotenv()

# Category mapping from catalog names to existing DB category names
CATEGORY_MAP = {
    'Products': 'General Spares',
    'General Spares': 'General Spares',
    'Engine-Parts': 'Engine Parts',
    'Engine Parts': 'Engine Parts',
    'Brake-Parts': 'Brake Parts',
    'Brake Parts': 'Brake Parts',
    'Electrical-Parts': 'Electrical Parts',
    'Electrical Parts': 'Electrical Parts',
    'Body-Parts': 'Body Parts',
    'Body Parts': 'Body Parts',
    'Chain-Sprocket': 'Chain & Sprocket',
    'Chain & Sprocket': 'Chain & Sprocket',
    'Filters': 'Filters',
    'Accessories': 'Accessories'
}

TARGET_MODELS = [
    'Hero Splendor Plus',
    'Honda Shine',
    'Bajaj Pulsar 150',
    'TVS Apache RTR 160',
    'Royal Enfield Classic 350',
    'Honda Activa',
    'Bajaj Pulsar NS200',
    'TVS Raider 125'
]

def get_db_connection():
    try:
        conn = mysql.connector.connect(
            host=os.getenv('DB_HOST', 'localhost'),
            user=os.getenv('DB_USER', 'root'),
            password=os.getenv('DB_PASSWORD', ''),
            database=os.getenv('DB_NAME', 'nk_automobiles')
        )
        return conn
    except Error as e:
        print(f"Error connecting to MySQL database: {e}")
        return None

def copy_catalog_images(catalog_dir, dry_run=False):
    """
    Copies SVG placeholder assets from catalog to:
    1) static/products/motorcycle_parts/
    2) static/images/products/motorcycle_parts/
    """
    src_images = os.path.join(catalog_dir, 'images')
    if not os.path.isdir(src_images):
        print(f"[WARN] Images directory not found at {src_images}")
        return 0

    dest_dirs = [
        os.path.join('static', 'products', 'motorcycle_parts'),
        os.path.join('static', 'images', 'products', 'motorcycle_parts')
    ]

    copied_count = 0
    for root, _, files in os.walk(src_images):
        rel_path = os.path.relpath(root, src_images)
        for f in files:
            src_file = os.path.join(root, f)
            for dest_root in dest_dirs:
                target_folder = os.path.join(dest_root, rel_path) if rel_path != '.' else dest_root
                if not dry_run:
                    os.makedirs(target_folder, exist_ok=True)
                    dest_file = os.path.join(target_folder, f)
                    if not os.path.exists(dest_file) or os.path.getsize(dest_file) != os.path.getsize(src_file):
                        shutil.copy2(src_file, dest_file)
            copied_count += 1

    print(f"[{'DRY-RUN' if dry_run else 'OK'}] Verified / copied {copied_count} catalog image assets.")
    return copied_count

def parse_price(val):
    """Safely parse price string to Decimal or None."""
    if val is None:
        return None
    val_str = str(val).strip()
    if not val_str:
        return None
    try:
        cleaned = val_str.replace('₹', '').replace(',', '').strip()
        num = Decimal(cleaned)
        if num > 0:
            return num
        return None
    except Exception:
        return None

def validate_catalog(records):
    """Validates records before performing any database operations."""
    valid_records = []
    errors = []
    category_counts = {}

    for idx, item in enumerate(records, start=1):
        pid = item.get('product_id', '').strip()
        name = item.get('product_name', '').strip()
        cat = item.get('category', '').strip()
        img = item.get('image_path', '').strip()

        if not pid:
            errors.append(f"Row #{idx}: Missing 'product_id'")
            continue
        if not name:
            errors.append(f"Row #{idx} ({pid}): Missing 'product_name'")
            continue
        if not cat:
            errors.append(f"Row #{idx} ({pid}): Missing 'category'")
            continue

        category_counts[cat] = category_counts.get(cat, 0) + 1
        valid_records.append(item)

    return valid_records, errors, category_counts

def run_import(catalog_dir=None, dry_run=False):
    # Locate catalog folder
    if not catalog_dir:
        candidates = [
            'NK_Automobiles_Product_Catalog',
            'nk_automobiles_catalog',
            os.path.join(os.path.dirname(__file__), '..', 'NK_Automobiles_Product_Catalog'),
            os.path.join(os.path.dirname(__file__), '..', 'nk_automobiles_catalog')
        ]
        for c in candidates:
            if os.path.isdir(c):
                catalog_dir = c
                break

    if not catalog_dir or not os.path.isdir(catalog_dir):
        print(f"Error: Catalog directory could not be found.")
        return False

    json_path = os.path.join(catalog_dir, 'products.json')
    if not os.path.exists(json_path):
        print(f"Error: Canonical products.json not found in {catalog_dir}")
        return False

    print(f"\n========================================================")
    print(f"NK AUTOMOBILES — MOTORCYCLE CATALOG IMPORT")
    print(f"========================================================")
    print(f"Catalog Directory : {catalog_dir}")
    print(f"Mode              : {'DRY RUN (No changes will be written)' if dry_run else 'LIVE IMPORT'}")

    with open(json_path, 'r', encoding='utf-8') as f:
        records = json.load(f)

    total_records = len(records)
    print(f"Total Records     : {total_records}")

    valid_records, validation_errors, cat_counts = validate_catalog(records)

    print("\n--- Category Distribution in Source File ---")
    for cat, count in cat_counts.items():
        mapped = CATEGORY_MAP.get(cat, 'UNKNOWN')
        print(f"  • {cat:<18} -> Maps to '{mapped}': {count} records")

    if validation_errors:
        print(f"\n[WARN] Validation encountered {len(validation_errors)} errors:")
        for err in validation_errors[:10]:
            print(f"  - {err}")
        if len(validation_errors) > 10:
            print(f"  ... and {len(validation_errors) - 10} more.")

    # Copy / Verify image assets
    copy_catalog_images(catalog_dir, dry_run=dry_run)

    # Database Operations
    conn = get_db_connection()
    if not conn:
        print("Error: Could not connect to database. Aborting import.")
        return False

    cursor = conn.cursor(dictionary=True)

    # 1. Fetch category map from database
    cursor.execute("SELECT category_id, name FROM categories")
    db_categories = {row['name'].lower(): row['category_id'] for row in cursor.fetchall()}

    # 2. Fetch existing products by catalog_id
    cursor.execute("SELECT product_id, catalog_id, name, price, stock_quantity, image_url FROM products WHERE catalog_id IS NOT NULL")
    existing_catalog_prods = {row['catalog_id']: row for row in cursor.fetchall()}

    inserted_count = 0
    updated_count = 0
    skipped_count = 0
    compat_inserted = 0

    try:
        for item in valid_records:
            cat_id_code = item['product_id']
            cat_name_src = item['category'].strip()
            target_cat_name = CATEGORY_MAP.get(cat_name_src, cat_name_src)
            category_id = db_categories.get(target_cat_name.lower())

            if not category_id:
                # Fallback to General Spares if not found
                category_id = db_categories.get('general spares', 1)

            product_name = item['product_name'].strip()
            description = item.get('description', '').strip()
            raw_brand = item.get('brand', '').strip()
            brand = raw_brand if raw_brand and raw_brand.lower() != 'not verified' else None
            raw_part = item.get('part_number', '').strip()
            part_number = raw_part if raw_part and raw_part.lower() != 'not verified' else None

            price = parse_price(item.get('price_inr'))
            price_status = item.get('price_status', 'HUBBALLI_QUOTE_REQUIRED')
            price_source = item.get('price_source', '') or None
            source_url = item.get('source_url', '') or None

            # Relative image path: e.g. motorcycle_parts/Products/NK-001-spark-plug.svg
            # Catalog gives: images/Products/NK-001-spark-plug.svg
            raw_img = item.get('image_path', '')
            if raw_img.startswith('images/'):
                clean_img = 'motorcycle_parts/' + raw_img[len('images/'):]
            else:
                clean_img = 'motorcycle_parts/' + raw_img

            image_status = item.get('image_status', 'PLACEHOLDER_NOT_A_REAL_PRODUCT_PHOTO')
            notes = item.get('notes', '') or None

            # Compatibility models
            compat_str = item.get('compatible_models', '')
            model_list = [m.strip() for m in compat_str.split(';') if m.strip()]

            if cat_id_code in existing_catalog_prods:
                # Product already exists: Idempotent update
                existing = existing_catalog_prods[cat_id_code]
                prod_db_id = existing['product_id']

                if not dry_run:
                    # Update fields without overwriting user-modified price or custom photo
                    cursor.execute("""
                        UPDATE products SET
                            name = COALESCE(%s, name),
                            category_id = COALESCE(%s, category_id),
                            brand = COALESCE(brand, %s),
                            part_number = COALESCE(part_number, %s),
                            price_status = COALESCE(price_status, %s),
                            price_source = COALESCE(price_source, %s),
                            source_url = COALESCE(source_url, %s),
                            image_status = COALESCE(image_status, %s),
                            notes = COALESCE(notes, %s)
                        WHERE product_id = %s
                    """, (
                        product_name, category_id, brand, part_number,
                        price_status, price_source, source_url, image_status,
                        notes, prod_db_id
                    ))
                updated_count += 1
            else:
                # Insert new product
                prod_db_id = None
                if not dry_run:
                    cursor.execute("""
                        INSERT INTO products (
                            catalog_id, name, description, category_id, brand, part_number,
                            price, price_status, price_source, source_url,
                            image_url, image_status, fitment_status, stock_quantity, is_active, notes
                        ) VALUES (
                            %s, %s, %s, %s, %s, %s,
                            %s, %s, %s, %s,
                            %s, %s, %s, %s, %s, %s
                        )
                    """, (
                        cat_id_code, product_name, description, category_id, brand, part_number,
                        price, price_status, price_source, source_url,
                        clean_img, image_status, 'Requires confirmation', 0, 1, notes
                    ))
                    prod_db_id = cursor.lastrowid
                inserted_count += 1

            # Insert Compatibility records
            if not dry_run and prod_db_id and model_list:
                for model_entry in model_list:
                    # Determine fitment status
                    if any(tm.lower() in model_entry.lower() for tm in TARGET_MODELS):
                        fit_status = 'Requires model-year confirmation'
                    else:
                        fit_status = 'Requires confirmation'

                    cursor.execute("""
                        INSERT INTO product_compatibility (product_id, vehicle_model, fitment_status, notes)
                        VALUES (%s, %s, %s, %s)
                        ON DUPLICATE KEY UPDATE 
                            fitment_status = VALUES(fitment_status),
                            notes = VALUES(notes)
                    """, (prod_db_id, model_entry, fit_status, 'Imported from catalog target range'))
                    compat_inserted += 1

        if not dry_run:
            conn.commit()
            print("\n[SUCCESS] Transaction committed successfully.")
        else:
            print("\n[DRY RUN] No database writes were committed.")

    except Exception as e:
        if not dry_run:
            conn.rollback()
            print(f"\n[ERROR] Exception encountered during import: {e}. Transaction rolled back.")
        return False
    finally:
        cursor.close()
        conn.close()

    print(f"\n========================================================")
    print(f"IMPORT SUMMARY")
    print(f"========================================================")
    print(f"Total Source Records : {total_records}")
    print(f"Validated Records    : {len(valid_records)}")
    print(f"New Records Inserted : {inserted_count}")
    print(f"Existing Updated     : {updated_count}")
    print(f"Skipped / Failed     : {skipped_count}")
    print(f"Compatibility Rows   : {compat_inserted}")
    print(f"Status               : {'Dry Run Completed' if dry_run else 'Live Import Completed'}")
    print(f"========================================================\n")
    return True

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Import NK Automobiles Motorcycle Catalog")
    parser.add_argument('--catalog-dir', type=str, default=None, help="Path to catalog folder")
    parser.add_argument('--dry-run', action='store_true', help="Run validation without database commit")
    args = parser.parse_args()

    run_import(catalog_dir=args.catalog_dir, dry_run=args.dry_run)
