import mysql.connector
from dotenv import load_dotenv
import os

load_dotenv()

conn = mysql.connector.connect(
    host=os.getenv('DB_HOST'),
    user=os.getenv('DB_USER'),
    password=os.getenv('DB_PASSWORD'),
    database=os.getenv('DB_NAME')
)

cursor = conn.cursor(dictionary=True)
cursor.execute('SELECT product_id, name, description, brand, category_id FROM products ORDER BY product_id LIMIT 20')
products = cursor.fetchall()

print("\n=== CURRENT PRODUCTS ===\n")
for p in products:
    print(f"ID: {p['product_id']}")
    print(f"Name: {p['name']}")
    print(f"Brand: {p['brand']}")
    print(f"Category: {p['category_id']}")
    print(f"Description: {p['description'][:100] if p['description'] else 'None'}...")
    print("-" * 80)

cursor.close()
conn.close()
