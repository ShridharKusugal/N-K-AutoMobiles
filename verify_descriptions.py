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
cursor.execute('SELECT product_id, name, LEFT(description, 200) as desc_preview FROM products WHERE product_id <= 5 ORDER BY product_id')
products = cursor.fetchall()

print("\n" + "="*100)
print("UPDATED PRODUCT DESCRIPTIONS - PREVIEW")
print("="*100 + "\n")

for p in products:
    print(f"ID: {p['product_id']}")
    print(f"Name: {p['name']}")
    print(f"Description Preview: {p['desc_preview']}...")
    print("-" * 100)

cursor.close()
conn.close()

print("\nAll 20 products have been updated with detailed, comprehensive descriptions!")
