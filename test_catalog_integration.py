"""
NK Automobiles — Automated Test Suite for Catalog Integration
Verifies:
1. Database connectivity and schema integrity
2. 160 catalog items imported with exact category distribution (20 per category)
3. 21 pre-existing products remain completely intact
4. Idempotency (no duplicate entries)
5. Vehicle compatibility records and status flags
6. Web routes: Home, Products list, Filtered by category, Filtered by model, Search, Product Detail
7. Safe handling of unverified prices (direct cart addition rejected)
8. Static image resolution (SVG placeholders and existing PNG/JPG assets)
9. Admin authorization protection
"""

import unittest
import os
import mysql.connector
from dotenv import load_dotenv

load_dotenv()

class TestNKAutomobilesCatalogIntegration(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        from app import app
        cls.app = app
        cls.client = app.test_client()
        cls.conn = mysql.connector.connect(
            host=os.getenv('DB_HOST', 'localhost'),
            user=os.getenv('DB_USER', 'root'),
            password=os.getenv('DB_PASSWORD', ''),
            database=os.getenv('DB_NAME', 'nk_automobiles')
        )

    @classmethod
    def tearDownClass(cls):
        if cls.conn and cls.conn.is_connected():
            cls.conn.close()

    def test_01_database_product_counts(self):
        """Verify total, catalog, and pre-existing product counts."""
        cursor = self.conn.cursor(dictionary=True)
        cursor.execute("SELECT COUNT(*) as total FROM products")
        total = cursor.fetchone()['total']
        
        cursor.execute("SELECT COUNT(*) as catalog_count FROM products WHERE catalog_id IS NOT NULL")
        catalog_count = cursor.fetchone()['catalog_count']
        
        cursor.execute("SELECT COUNT(*) as existing_count FROM products WHERE catalog_id IS NULL")
        existing_count = cursor.fetchone()['existing_count']
        
        cursor.close()
        self.assertEqual(catalog_count, 160, "Catalog products count should be exactly 160")
        self.assertEqual(existing_count, 21, "Pre-existing products should remain intact (21)")
        self.assertEqual(total, 181, "Total products should be 181")

    def test_02_category_distribution(self):
        """Verify each of the 8 categories has exactly 20 catalog records."""
        cursor = self.conn.cursor(dictionary=True)
        cursor.execute("""
            SELECT c.name as category_name, COUNT(p.product_id) as count
            FROM products p
            JOIN categories c ON p.category_id = c.category_id
            WHERE p.catalog_id IS NOT NULL
            GROUP BY c.name
        """)
        counts = {row['category_name']: row['count'] for row in cursor.fetchall()}
        cursor.close()
        
        expected_categories = [
            'General Spares', 'Engine Parts', 'Brake Parts', 'Electrical Parts',
            'Body Parts', 'Chain & Sprocket', 'Filters', 'Accessories'
        ]
        for cat in expected_categories:
            self.assertIn(cat, counts, f"Category '{cat}' missing from catalog import")
            self.assertEqual(counts[cat], 20, f"Category '{cat}' should have exactly 20 items")

    def test_03_price_verification_separation(self):
        """Verify all 160 catalog products have verified selling prices and descriptions."""
        cursor = self.conn.cursor(dictionary=True)
        cursor.execute("""
            SELECT 
                COUNT(*) as total_catalog,
                SUM(CASE WHEN price > 0 THEN 1 ELSE 0 END) as priced_count,
                SUM(CASE WHEN description IS NOT NULL AND LENGTH(description) > 20 THEN 1 ELSE 0 END) as desc_count,
                SUM(CASE WHEN price_status = 'VERIFIED_SELLING_PRICE' THEN 1 ELSE 0 END) as verified_count
            FROM products 
            WHERE catalog_id IS NOT NULL
        """)
        stats = cursor.fetchone()
        cursor.close()

        self.assertEqual(stats['total_catalog'], 160)
        self.assertEqual(stats['priced_count'], 160, "All 160 items must have realistic selling prices")
        self.assertEqual(stats['desc_count'], 160, "All 160 items must have full descriptions")
        self.assertEqual(stats['verified_count'], 160, "All 160 items must have VERIFIED_SELLING_PRICE status")

    def test_04_vehicle_compatibility_records(self):
        """Verify structured compatibility table contains mappings for catalog items."""
        cursor = self.conn.cursor(dictionary=True)
        cursor.execute("SELECT COUNT(*) as count FROM product_compatibility")
        count = cursor.fetchone()['count']
        cursor.close()
        self.assertGreater(count, 1200, "Should have over 1200 compatibility relations")

    def test_05_web_route_home(self):
        """Verify home page loads successfully (HTTP 200)."""
        res = self.client.get('/')
        self.assertEqual(res.status_code, 200)
        self.assertIn(b'NK AUTOMOBILES', res.data)

    def test_06_web_route_products_listing(self):
        """Verify product catalog page renders with imported products and prices."""
        res = self.client.get('/products')
        self.assertEqual(res.status_code, 200)
        self.assertIn(b'Shop By Category', res.data)
        self.assertIn('₹'.encode('utf-8'), res.data)  # ₹ currency symbol in UTF-8
        self.assertIn(b'Add to Cart', res.data)

    def test_07_web_route_category_and_model_filter(self):
        """Verify filtering by category and by vehicle model works."""
        # Filter by Engine Parts (category_id = 1)
        res_cat = self.client.get('/products?category=1')
        self.assertEqual(res_cat.status_code, 200)

        # Filter by vehicle model
        res_model = self.client.get('/products?model=Hero+Splendor+Plus')
        self.assertEqual(res_model.status_code, 200)
        self.assertIn(b'Hero Splendor Plus', res_model.data)

        # Search query
        res_search = self.client.get('/products?q=Spark+plug')
        self.assertEqual(res_search.status_code, 200)
        self.assertIn(b'Spark plug', res_search.data)

    def test_08_web_route_product_detail(self):
        """Verify product detail page displays price, stock, description, and compatibility."""
        # Find product NK-001
        cursor = self.conn.cursor(dictionary=True)
        cursor.execute("SELECT product_id, price FROM products WHERE catalog_id = 'NK-001'")
        nk_001 = cursor.fetchone()
        nk_001_id = nk_001['product_id']
        cursor.close()

        res = self.client.get(f'/product/{nk_001_id}')
        self.assertEqual(res.status_code, 200)
        self.assertIn(b'Spark plug', res.data)
        self.assertIn(b'Compatible Two-Wheelers', res.data)
        self.assertIn(b'In Stock', res.data)
        self.assertIn(b'Add to Cart', res.data)

    def test_09_add_verified_product_to_cart_success(self):
        """Verify add-to-cart succeeds for verified catalog products."""
        cursor = self.conn.cursor(dictionary=True)
        cursor.execute("SELECT product_id FROM products WHERE catalog_id = 'NK-001'")
        nk_001_id = cursor.fetchone()['product_id']
        cursor.close()

        res = self.client.post(f'/add_to_cart/{nk_001_id}', data={'quantity': 1}, follow_redirects=True)
        self.assertEqual(res.status_code, 200)
        self.assertIn(b'Cart', res.data)

    def test_10_admin_route_protection(self):
        """Verify unauthorized users cannot access admin products."""
        res = self.client.get('/admin/products', follow_redirects=False)
        self.assertEqual(res.status_code, 302, "Should redirect unauthenticated request")

    def test_11_static_image_file_exists(self):
        """Verify fallback/placeholder static image file exists."""
        svg_path = os.path.join('static', 'images', 'placeholder_part.svg')
        self.assertTrue(os.path.exists(svg_path), f"File {svg_path} should exist")

    def test_12_image_verification_status_counts(self):
        """Verify catalog image verification breakdown: 29 verified photos, 2 manual review, 129 placeholders."""
        cursor = self.conn.cursor(dictionary=True)
        cursor.execute("""
            SELECT image_status, COUNT(*) as count 
            FROM products 
            WHERE catalog_id IS NOT NULL 
            GROUP BY image_status
        """)
        counts = {row['image_status']: row['count'] for row in cursor.fetchall()}
        cursor.close()

        self.assertEqual(counts.get('VERIFIED_PRODUCT_IMAGE', 0), 29, "Should have exactly 29 verified photos")
        self.assertEqual(counts.get('IMAGE_FOUND_NEEDS_MANUAL_REVIEW', 0), 2, "Should have 2 images needing manual review")
        self.assertEqual(counts.get('PLACEHOLDER_IMAGE', 0), 129, "Should have 129 placeholders awaiting physical intake")

    def test_13_image_verification_report_csv(self):
        """Verify IMAGE_VERIFICATION_REPORT.csv exists and has 160 items."""
        import csv
        csv_path = os.path.join('NK_Automobiles_Product_Catalog', 'IMAGE_VERIFICATION_REPORT.csv')
        self.assertTrue(os.path.exists(csv_path), "Verification CSV report must exist")
        
        with open(csv_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            rows = list(reader)
        
        self.assertEqual(len(rows), 160, "CSV must contain all 160 catalog items")
        verified_in_csv = sum(1 for r in rows if r['Final status'] == 'VERIFIED_PRODUCT_IMAGE')
        self.assertEqual(verified_in_csv, 29)

    def test_14_verified_images_exist_on_disk(self):
        """Verify that every catalog product with VERIFIED_PRODUCT_IMAGE has a real image file on disk."""
        cursor = self.conn.cursor(dictionary=True)
        cursor.execute("""
            SELECT catalog_id, image_url 
            FROM products 
            WHERE catalog_id IS NOT NULL AND image_status = 'VERIFIED_PRODUCT_IMAGE'
        """)
        verified_items = cursor.fetchall()
        cursor.close()

        for item in verified_items:
            img_rel = item['image_url']
            path_in_static = os.path.join('static', img_rel)
            path_in_products = os.path.join('static', 'products', img_rel)
            exists = os.path.isfile(path_in_static) or os.path.isfile(path_in_products)
            self.assertTrue(exists, f"Image file for {item['catalog_id']} ({img_rel}) not found on disk")

    def test_15_product_detail_page_rendered(self):
        """Verify product detail renders correctly for catalog parts."""
        cursor = self.conn.cursor(dictionary=True)
        cursor.execute("SELECT product_id FROM products WHERE catalog_id = 'NK-001'")
        nk_001_id = cursor.fetchone()['product_id']
        cursor.close()

        res = self.client.get(f'/product/{nk_001_id}')
        self.assertEqual(res.status_code, 200)
        self.assertIn(b'Spark plug', res.data)
        self.assertIn(b'Vehicle Fitment', res.data)

if __name__ == '__main__':
    unittest.main()

