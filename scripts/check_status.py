import os
import mysql.connector
from dotenv import load_dotenv

load_dotenv()

def main():
    conn = mysql.connector.connect(
        host=os.getenv('DB_HOST', 'localhost'),
        user=os.getenv('DB_USER', 'root'),
        password=os.getenv('DB_PASSWORD', 'Shri@2004'),
        database=os.getenv('DB_NAME', 'nk_automobiles')
    )
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT product_id, catalog_id, name, category_id, image_status, image_url
        FROM products
        WHERE image_status != 'VERIFIED_PRODUCT_IMAGE'
        ORDER BY product_id
    """)
    rows = cursor.fetchall()
    print(f"Total unverified products in DB: {len(rows)}")
    for r in rows:
        print(f"[{r['catalog_id']}] (ID: {r['product_id']}, Cat: {r['category_id']}) {r['name']} -> {r['image_url']} (status: {r['image_status']})")
    
    cursor.execute("SELECT COUNT(*) as total FROM products")
    total = cursor.fetchone()['total']
    cursor.execute("SELECT COUNT(*) as verified FROM products WHERE image_status = 'VERIFIED_PRODUCT_IMAGE'")
    verified = cursor.fetchone()['verified']
    print(f"\nProgress: {verified}/{total} verified ({verified/total*100:.1f}%)")
    conn.close()

if __name__ == '__main__':
    main()
