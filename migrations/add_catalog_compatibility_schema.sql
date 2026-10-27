-- NK Automobiles: Catalog & Compatibility Schema Migration
-- Safe, non-destructive migration script

USE nk_automobiles;

-- 1. Allow NULL for price so products requiring local quotes don't store fake/zero prices
ALTER TABLE products MODIFY COLUMN price DECIMAL(10, 2) NULL DEFAULT NULL;

-- 2. Add catalog and verification tracking columns to products
ALTER TABLE products 
    ADD COLUMN IF NOT EXISTS catalog_id VARCHAR(50) UNIQUE DEFAULT NULL AFTER product_id,
    ADD COLUMN IF NOT EXISTS part_number VARCHAR(100) DEFAULT NULL AFTER brand,
    ADD COLUMN IF NOT EXISTS price_status VARCHAR(60) DEFAULT 'VERIFIED_SELLING_PRICE' AFTER price,
    ADD COLUMN IF NOT EXISTS price_source VARCHAR(255) DEFAULT NULL AFTER price_status,
    ADD COLUMN IF NOT EXISTS source_url VARCHAR(500) DEFAULT NULL AFTER price_source,
    ADD COLUMN IF NOT EXISTS image_status VARCHAR(60) DEFAULT 'VERIFIED_PHOTO' AFTER image_url,
    ADD COLUMN IF NOT EXISTS fitment_status VARCHAR(60) DEFAULT 'VERIFIED' AFTER specifications,
    ADD COLUMN IF NOT EXISTS is_active TINYINT(1) DEFAULT 1 AFTER fitment_status,
    ADD COLUMN IF NOT EXISTS notes TEXT DEFAULT NULL AFTER is_active;

-- 3. Initialize verification statuses for existing products
UPDATE products 
SET price_status = 'VERIFIED_SELLING_PRICE',
    image_status = 'VERIFIED_PHOTO',
    fitment_status = 'VERIFIED',
    is_active = 1
WHERE price_status IS NULL OR price_status = '';

-- 4. Create motorcycle compatibility table
CREATE TABLE IF NOT EXISTS product_compatibility (
    compatibility_id INT AUTO_INCREMENT PRIMARY KEY,
    product_id INT NOT NULL,
    vehicle_model VARCHAR(100) NOT NULL,
    fitment_status VARCHAR(60) DEFAULT 'Requires model-year confirmation',
    notes VARCHAR(255) DEFAULT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (product_id) REFERENCES products(product_id) ON DELETE CASCADE,
    UNIQUE KEY uq_product_vehicle (product_id, vehicle_model)
);

-- 5. Add 'General Spares' category if it doesn't already exist
INSERT INTO categories (name, description)
SELECT 'General Spares', 'Spark plugs, cables, bearings, oils, hardware and general maintenance spares'
WHERE NOT EXISTS (SELECT 1 FROM categories WHERE name = 'General Spares');
