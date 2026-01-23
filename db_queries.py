import mysql.connector
from mysql.connector import Error

db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': '2004',
    'database': 'nk_automobiles'
}

def get_db_connection():
    try:
        return mysql.connector.connect(**db_config)
    except Error as e:
        print("Database connection error:", e)
        return None

# ==========================
# PRODUCT QUERIES
# ==========================
def get_all_products(limit=None):
    conn = get_db_connection()
    if not conn: return []
    cursor = conn.cursor(dictionary=True)
    query = "SELECT * FROM products"
    if limit:
        query += f" LIMIT {limit}"
    cursor.execute(query)
    products = cursor.fetchall()
    cursor.close()
    conn.close()
    return products

def get_products_by_category(category_id=None):
    conn = get_db_connection()
    if not conn: return []
    cursor = conn.cursor(dictionary=True)
    if category_id:
        cursor.execute("SELECT * FROM products WHERE category_id = %s", (category_id,))
    else:
        cursor.execute("SELECT * FROM products")
    products = cursor.fetchall()
    cursor.close()
    conn.close()
    return products

def get_related_products(category_id, current_product_id, limit=10):
    conn = get_db_connection()
    if not conn: return []
    cursor = conn.cursor(dictionary=True)
    
    # 1. Try to get products from same category
    cursor.execute("""
        SELECT * FROM products 
        WHERE category_id = %s AND product_id != %s 
        LIMIT %s
    """, (category_id, current_product_id, limit))
    related = cursor.fetchall()
    
    # 2. If not enough, fill with other random products
    if len(related) < limit:
        needed = limit - len(related)
        exclude_ids = [current_product_id] + [p['product_id'] for p in related]
        format_strings = ','.join(['%s'] * len(exclude_ids))
        
        cursor.execute(f"""
            SELECT * FROM products 
            WHERE product_id NOT IN ({format_strings}) 
            ORDER BY RAND() 
            LIMIT %s
        """, (*exclude_ids, needed))
        
        others = cursor.fetchall()
        related.extend(others)
        
    cursor.close()
    conn.close()
    return related

def get_categories():
    conn = get_db_connection()
    if not conn: return []
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM categories")
    categories = cursor.fetchall()
    cursor.close()
    conn.close()
    return categories

def get_product_details(product_id):
    conn = get_db_connection()
    if not conn: return None, [], 0, 0
    
    cursor = conn.cursor(dictionary=True)
    
    # 1. Product
    cursor.execute("""
        SELECT p.*, c.name AS category_name
        FROM products p
        LEFT JOIN categories c ON p.category_id = c.category_id
        WHERE p.product_id = %s
    """, (product_id,))
    product = cursor.fetchone()
    
    reviews = []
    avg_rating = 0
    review_count = 0
    
    if product:
        # 2. Reviews
        cursor.execute("""
            SELECT r.*, u.username 
            FROM reviews r 
            JOIN users u ON r.user_id = u.user_id 
            WHERE r.product_id = %s 
            ORDER BY r.created_at DESC
        """, (product_id,))
        reviews = cursor.fetchall()
        
        # 3. Stats
        cursor.execute("SELECT AVG(rating) as avg, COUNT(*) as count FROM reviews WHERE product_id = %s", (product_id,))
        stats = cursor.fetchone()
        if stats and stats['avg']:
            avg_rating = round(float(stats['avg']), 1)
            review_count = stats['count']
            
        # 4. Media
        if reviews:
            review_ids = [r['review_id'] for r in reviews]
            format_strings = ','.join(['%s'] * len(review_ids))
            cursor.execute(f"SELECT * FROM review_media WHERE review_id IN ({format_strings})", tuple(review_ids))
            all_media = cursor.fetchall()
            
            media_map = {}
            for m in all_media:
                if m['review_id'] not in media_map:
                    media_map[m['review_id']] = []
                media_map[m['review_id']].append(m)
            
            for r in reviews:
                r['media'] = media_map.get(r['review_id'], [])
                
        # Parse Specs
        specs_dict = {}
        if product.get('specifications'):
            try:
                for line in product['specifications'].split('\n'):
                    if ':' in line:
                        key, value = line.split(':', 1)
                        specs_dict[key.strip()] = value.strip()
            except: pass
        product['specs_parsed'] = specs_dict

    cursor.close()
    conn.close()
    return product, reviews, avg_rating, review_count

# ==========================
# CART QUERIES
# ==========================
def get_cart_count(user_id):
    conn = get_db_connection()
    if not conn: return 0
    cursor = conn.cursor(dictionary=True)
    count = 0
    try:
        cursor.execute("SELECT SUM(quantity) as count FROM cart WHERE user_id = %s", (user_id,))
        res = cursor.fetchone()
        if res and res['count']: count = int(res['count'])
    except: pass
    cursor.close()
    conn.close()
    return count

def get_cart_items(user_id):
    conn = get_db_connection()
    if not conn: return [], 0
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT c.cart_id, c.quantity, c.product_id, p.name, p.price, p.image_url, (p.price * c.quantity) as total_price
        FROM cart c
        JOIN products p ON c.product_id = p.product_id
        WHERE c.user_id = %s
    """, (user_id,))
    items = cursor.fetchall()
    total = sum(item['total_price'] for item in items)
    cursor.close()
    conn.close()
    return items, total

def add_to_cart_db(user_id, product_id, quantity):
    conn = get_db_connection()
    if not conn: return False, "Database error"
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute("SELECT name, stock_quantity FROM products WHERE product_id = %s", (product_id,))
        product = cursor.fetchone()
        if not product: return False, "Product not found"
        
        if product['stock_quantity'] < quantity:
            return False, f"Only {product['stock_quantity']} units available."
            
        cursor.execute("SELECT * FROM cart WHERE user_id = %s AND product_id = %s", (user_id, product_id))
        existing = cursor.fetchone()
        
        if existing:
            new_qty = existing['quantity'] + quantity
            if new_qty > product['stock_quantity']:
                return False, f"Max limit reached. You have {existing['quantity']} in cart."
            cursor.execute("UPDATE cart SET quantity = %s WHERE cart_id = %s", (new_qty, existing['cart_id']))
        else:
            cursor.execute("INSERT INTO cart (user_id, product_id, quantity) VALUES (%s, %s, %s)", (user_id, product_id, quantity))
            
        conn.commit()
        return True, "Item added to cart"
    except Error as e:
        return False, str(e)
    finally:
        cursor.close()
        conn.close()

def clear_cart(user_id):
    conn = get_db_connection()
    if not conn: return
    cursor = conn.cursor()
    cursor.execute("DELETE FROM cart WHERE user_id = %s", (user_id,))
    conn.commit()
    cursor.close()
    conn.close()

def remove_from_cart(user_id, product_id):
    conn = get_db_connection()
    if not conn: return False, "Connection error"
    cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM cart WHERE user_id = %s AND product_id = %s", (user_id, product_id))
        conn.commit()
        return True, "Item removed from cart"
    except Error as e:
        return False, str(e)
    finally:
        cursor.close()
        conn.close()

def update_cart_quantity(user_id, product_id, quantity):
    conn = get_db_connection()
    if not conn: return False, "Connection error"
    cursor = conn.cursor()
    try:
        if quantity <= 0:
            return remove_from_cart(user_id, product_id)
            
        cursor.execute("SELECT stock_quantity FROM products WHERE product_id = %s", (product_id,))
        res = cursor.fetchone()
        if not res: return False, "Product not found"
        stock = res[0]
        
        if quantity > stock:
            return False, f"Only {stock} units available"
            
        cursor.execute("UPDATE cart SET quantity = %s WHERE user_id = %s AND product_id = %s", (quantity, user_id, product_id))
        conn.commit()
        return True, "Quantity updated"
    except Error as e:
        return False, str(e)
    finally:
        cursor.close()
        conn.close()

# ==========================
# ORDER QUERIES
# ==========================
def create_order(user_id, order_data):
    conn = get_db_connection()
    if not conn: return None, "Connection error"
    cursor = conn.cursor(dictionary=True)
    try:
        # Get Cart
        cursor.execute("""
            SELECT c.product_id, c.quantity, p.price 
            FROM cart c JOIN products p ON c.product_id = p.product_id 
            WHERE c.user_id = %s
        """, (user_id,))
        items = cursor.fetchall()
        if not items: return None, "Cart empty"
        
        total = sum(i['price'] * i['quantity'] for i in items)
        
        cursor.execute("""
            INSERT INTO orders (user_id, full_name, phone_number, address_line1, address_line2, city, state, pincode, total_amount, payment_method, transaction_id, status)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, 'Pending')
        """, (user_id, order_data['full_name'], order_data['phone'], order_data['addr1'], order_data['addr2'], order_data['city'], order_data['state'], order_data['pincode'], total, order_data.get('payment_method', 'COD'), order_data.get('transaction_id', '')))
        order_id = cursor.lastrowid
        
        for item in items:
            cursor.execute("INSERT INTO order_items (order_id, product_id, quantity, price) VALUES (%s, %s, %s, %s)", (order_id, item['product_id'], item['quantity'], item['price']))
            cursor.execute("UPDATE products SET stock_quantity = stock_quantity - %s WHERE product_id = %s", (item['quantity'], item['product_id']))
            
        cursor.execute("DELETE FROM cart WHERE user_id = %s", (user_id,))
        conn.commit()
        return order_id, "Success"
    except Error as e:
        conn.rollback()
        return None, str(e)
    finally:
        cursor.close()
        conn.close()

def get_order_details(order_id, user_id=None):
    conn = get_db_connection()
    if not conn: return None, []
    cursor = conn.cursor(dictionary=True)
    
    query = "SELECT * FROM orders WHERE order_id = %s"
    params = [order_id]
    if user_id:
        query += " AND user_id = %s"
        params.append(user_id)
        
    cursor.execute(query, tuple(params))
    order = cursor.fetchone()
    
    items = []
    if order:
        cursor.execute("""
            SELECT oi.*, p.name, p.image_url 
            FROM order_items oi 
            JOIN products p ON oi.product_id = p.product_id 
            WHERE oi.order_id = %s
        """, (order_id,))
        items = cursor.fetchall()
        
    cursor.close()
    conn.close()
    return order, items

# ==========================
# USER QUERIES
# ==========================
def get_user_by_email(email):
    conn = get_db_connection()
    if not conn: return None
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
    user = cursor.fetchone()
    cursor.close()
    conn.close()
    return user

def create_user(username, email, password_hash):
    conn = get_db_connection()
    if not conn: return False, "Connection error"
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO users (username, email, password_hash, role) VALUES (%s, %s, %s, 'customer')", (username, email, password_hash))
        conn.commit()
        return True, "Success"
    except Error as e:
        return False, str(e)
    finally:
        cursor.close()
        conn.close()

def get_user_by_id(user_id):
    conn = get_db_connection()
    if not conn: return None
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM users WHERE user_id = %s", (user_id,))
    user = cursor.fetchone()
    cursor.close()
    conn.close()
    return user

def get_user_orders(user_id):
    conn = get_db_connection()
    if not conn: return []
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT * FROM orders 
        WHERE user_id = %s 
        ORDER BY created_at DESC
    """, (user_id,))
    orders = cursor.fetchall()
    cursor.close()
    conn.close()
    return orders

# ==========================
# ADMIN QUERIES (Partial)
# ==========================
def get_dashboard_stats():
    conn = get_db_connection()
    if not conn: return {}
    cursor = conn.cursor(dictionary=True)
    stats = {}
    
    cursor.execute("SELECT COUNT(*) as c FROM products")
    stats['products'] = cursor.fetchone()['c']
    cursor.execute("SELECT COUNT(*) as c FROM users")
    stats['users'] = cursor.fetchone()['c']
    cursor.execute("SELECT COUNT(*) as c FROM orders")
    stats['orders'] = cursor.fetchone()['c']
    cursor.execute("SELECT COUNT(*) as c FROM products WHERE stock_quantity < 10")
    stats['low_stock'] = cursor.fetchone()['c']
    
    cursor.close()
    conn.close()
    return stats

def get_recent_products(limit=5):
    conn = get_db_connection()
    if not conn: return []
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT p.*, c.name as category_name
        FROM products p
        LEFT JOIN categories c ON p.category_id = c.category_id
        ORDER BY p.product_id DESC LIMIT %s
    """, (limit,))
    res = cursor.fetchall()
    cursor.close()
    conn.close()
    return res

# ==========================
# ADMIN CRUD QUERIES
# ==========================

def get_admin_products():
    conn = get_db_connection()
    if not conn: return []
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT p.*, c.name as category_name
        FROM products p
        LEFT JOIN categories c ON p.category_id = c.category_id
        ORDER BY p.product_id DESC
    """)
    products = cursor.fetchall()
    cursor.close()
    conn.close()
    return products

def add_product(data):
    conn = get_db_connection()
    if not conn: return False, "Connection error"
    cursor = conn.cursor()
    try:
        cursor.execute("""
            INSERT INTO products (name, brand, category_id, price, stock_quantity, description, specifications, image_url)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """, (data['name'], data['brand'], data['category_id'], data['price'], data['stock_quantity'], data['description'], data['specifications'], data['image_url']))
        conn.commit()
        return True, "Product added successfully"
    except Error as e:
        return False, str(e)
    finally:
        cursor.close()
        conn.close()

def update_product(product_id, data):
    conn = get_db_connection()
    if not conn: return False, "Connection error"
    cursor = conn.cursor()
    try:
        cursor.execute("""
            UPDATE products SET name=%s, brand=%s, category_id=%s, price=%s, 
            stock_quantity=%s, description=%s, specifications=%s, image_url=%s WHERE product_id=%s
        """, (data['name'], data['brand'], data['category_id'], data['price'], data['stock_quantity'], data['description'], data['specifications'], data['image_url'], product_id))
        conn.commit()
        return True, "Product updated successfully"
    except Error as e:
        return False, str(e)
    finally:
        cursor.close()
        conn.close()

def delete_product(product_id):
    conn = get_db_connection()
    if not conn: return False, "Connection error"
    cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM products WHERE product_id = %s", (product_id,))
        conn.commit()
        return True, "Product deleted successfully"
    except Error as e:
        return False, str(e)
    return True, "Product deleted successfully"

def get_all_orders():
    conn = get_db_connection()
    if not conn: return []
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT o.*, u.username, u.email 
        FROM orders o 
        JOIN users u ON o.user_id = u.user_id 
        ORDER BY o.created_at DESC
    """)
    orders = cursor.fetchall()
    cursor.close()
    conn.close()
    return orders

def update_order_status(order_id, status):
    conn = get_db_connection()
    if not conn: return False, "Connection error"
    cursor = conn.cursor()
    try:
        cursor.execute("UPDATE orders SET status = %s WHERE order_id = %s", (status, order_id))
        conn.commit()
        return True, "Status updated"
    except Error as e:
        return False, str(e)
    finally:
        cursor.close()
        conn.close()

def get_all_users():
    conn = get_db_connection()
    if not conn: return []
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM users ORDER BY created_at DESC")
    users = cursor.fetchall()
    cursor.close()
    conn.close()
    return users

