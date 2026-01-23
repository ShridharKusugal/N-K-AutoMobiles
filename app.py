from flask import Flask, render_template, request, redirect, url_for, flash, session
import mysql.connector
from mysql.connector import Error
from functools import wraps
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import os
import db_queries

app = Flask(__name__)
app.secret_key = 'nk_automobiles_secret_key_123'

# ==========================
# FILE UPLOAD CONFIGURATION
# ==========================
UPLOAD_FOLDER = os.path.join(app.static_folder, 'products')
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp', 'mp4', 'webm', 'mov'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['REVIEWS_UPLOAD_FOLDER'] = os.path.join(app.static_folder, 'reviews')
app.config['MAX_CONTENT_LENGTH'] = 64 * 1024 * 1024  # 64MB max file size for videos

# Ensure upload folders exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(app.config['REVIEWS_UPLOAD_FOLDER'], exist_ok=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# ==========================
# DATABASE CONFIGURATION
# ==========================
db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': '2004',     # ✅ YOUR MYSQL PASSWORD
    'database': 'nk_automobiles'
}

def get_db_connection():
    try:
        return mysql.connector.connect(**db_config)
    except Error as e:
        print("Database connection error:", e)
        return None

# ==========================
# DECORATORS
# ==========================
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please login first.', 'warning')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get('role') != 'admin':
            flash('Admin access required.', 'danger')
            return redirect(url_for('home'))
        return f(*args, **kwargs)
    return decorated_function

# ==========================
# ROUTES
# ==========================

# ==========================
# CONTEXT PROCESSORS
# ==========================
@app.context_processor
def inject_cart_count():
    count = 0
    if 'user_id' in session:
        count = db_queries.get_cart_count(session['user_id'])
    return dict(cart_count=count)

# ==========================
# ROUTES
# ==========================

@app.route('/')
def home():
    products = db_queries.get_all_products(limit=6)
    return render_template('home.html', products=products)

@app.route('/products')
def products():
    category_id = request.args.get('category')
    categories = db_queries.get_categories()
    
    if category_id:
        products = db_queries.get_products_by_category(category_id)
    else:
        products = db_queries.get_products_by_category(None)

    return render_template('products.html', products=products, categories=categories)

@app.route('/product/<int:product_id>')
def product_detail(product_id):
    product, reviews, avg_rating, review_count = db_queries.get_product_details(product_id)
    
    related_products = []
    if product:
        related_products = db_queries.get_related_products(product['category_id'], product_id)

    if product:
        return render_template('product_detail.html', product=product, reviews=reviews, avg_rating=avg_rating, review_count=review_count, related_products=related_products)

    return "Product not found", 404

@app.route('/product/<int:product_id>/review', methods=['POST'])
@login_required
def add_review(product_id):
    rating = request.form.get('rating')
    comment = request.form.get('comment')
    files = request.files.getlist('media')
    
    if not rating:
        flash('Please provide a rating.', 'warning')
        return redirect(url_for('product_detail', product_id=product_id))

    conn = get_db_connection()
    if conn:
        cursor = conn.cursor()
        try:
            # Insert Review
            cursor.execute("""
                INSERT INTO reviews (user_id, product_id, rating, comment)
                VALUES (%s, %s, %s, %s)
            """, (session['user_id'], product_id, rating, comment))
            review_id = cursor.lastrowid
            
            # Handle Files
            for file in files:
                if file and allowed_file(file.filename):
                    filename = secure_filename(file.filename)
                    # Add unique prefix
                    import uuid
                    unique_filename = f"{uuid.uuid4().hex}_{filename}"
                    file.save(os.path.join(app.config['REVIEWS_UPLOAD_FOLDER'], unique_filename))
                    
                    # Determine type
                    ext = unique_filename.rsplit('.', 1)[1].lower()
                    media_type = 'video' if ext in ['mp4', 'webm', 'mov'] else 'image'
                    
                    cursor.execute("""
                        INSERT INTO review_media (review_id, media_url, media_type)
                        VALUES (%s, %s, %s)
                    """, (review_id, unique_filename, media_type))
            
            conn.commit()
            flash('Review submitted successfully!', 'success')
        except Error as e:
            print(f"Error submitting review: {e}")
            flash('Error submitting review.', 'danger')
        finally:
            cursor.close()
            conn.close()
            
    return redirect(url_for('product_detail', product_id=product_id))


@app.route('/cart')
@login_required
def cart():
    cart_items, grand_total = db_queries.get_cart_items(session['user_id'])
    return render_template('cart.html', cart_items=cart_items, grand_total=grand_total)

@app.route('/add_to_cart/<int:product_id>', methods=['POST'])
@login_required
def add_to_cart(product_id):
    quantity = int(request.form.get('quantity', 1))
    success, message = db_queries.add_to_cart_db(session['user_id'], product_id, quantity)
    
    if success:
        flash(message, 'success')
    else:
        # Check if message implies stock issue (contains "units" or "limit") to decide category
        category = 'warning' if 'available' in message or 'limit' in message else 'danger'
        flash(message, category)
        return redirect(url_for('product_detail', product_id=product_id))
            
        return redirect(url_for('product_detail', product_id=product_id))
            
    if request.form.get('action') == 'buy_now':
        return redirect(url_for('checkout'))
        
    return redirect(url_for('cart'))


@app.route('/remove_from_cart/<int:product_id>', methods=['POST'])
@login_required
def remove_from_cart(product_id):
    success, message = db_queries.remove_from_cart(session['user_id'], product_id)
    if success:
        flash(message, 'success')
    else:
        flash(message, 'danger')
    return redirect(url_for('cart'))

@app.route('/update_cart/<int:product_id>', methods=['POST'])
@login_required
def update_cart(product_id):
    action = request.form.get('action')
    try:
        current_qty = int(request.form.get('quantity'))
        if action == 'confirm':
             # Manual input
             new_qty = current_qty
        elif action == 'increase':
            new_qty = current_qty + 1
        elif action == 'decrease':
            new_qty = current_qty - 1
        else:
            new_qty = current_qty

        success, message = db_queries.update_cart_quantity(session['user_id'], product_id, new_qty)
        if not success:
            flash(message, 'warning')
            
    except ValueError:
        pass
        
    return redirect(url_for('cart'))

@app.route('/checkout', methods=['GET', 'POST'])
@login_required
def checkout():
    user_id = session['user_id']
    
    # Direct Buy Logic
    direct_product_id = request.args.get('product_id')
    direct_quantity = int(request.args.get('quantity', 1))
    
    if request.method == 'POST':
        # Get address details from form
        order_data = {
            'full_name': request.form['full_name'],
            'phone': request.form['phone_number'],
            'pincode': request.form['pincode'],
            'addr1': request.form['address_line1'],
            'addr2': request.form['address_line2'],
            'landmark': request.form.get('landmark', ''),
            'city': request.form['city'],
            'state': request.form['state'],
            'payment_method': request.form.get('payment_method', 'COD'),
            'transaction_id': request.form.get('transaction_id', '')
        }
        
        if order_data['landmark']:
            order_data['addr2'] += f", Near {order_data['landmark']}"

        # Handle Direct Buy Order or Cart Order
        direct_pid = request.form.get('direct_product_id') # From hidden input
        direct_qty = int(request.form.get('direct_quantity', 1)) # From hidden input

        if direct_pid:
            # Create Temporary "Cart Item" Structure for Order Creation
            # We need a custom order creation logic for this, or modify create_order
            # For simplicity, let's use a specialized logic here since create_order reads from cart
            
            # Fetch product
            product, _, _, _ = db_queries.get_product_details(direct_pid)
            if not product:
                flash("Product not found.", "danger")
                return redirect(url_for('home'))
                
            total_amount = product['price'] * direct_qty
            
            try:
                conn = db_queries.get_db_connection()
                cursor = conn.cursor()
                
                # Insert Order
                cursor.execute("""
                    INSERT INTO orders (user_id, full_name, phone_number, address_line1, address_line2, city, state, pincode, total_amount, payment_method, transaction_id, status)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, 'Pending')
                """, (user_id, order_data['full_name'], order_data['phone'], order_data['addr1'], order_data['addr2'], order_data['city'], order_data['state'], order_data['pincode'], total_amount, order_data['payment_method'], order_data['transaction_id']))
                order_id = cursor.lastrowid
                
                # Insert Order Item
                cursor.execute("INSERT INTO order_items (order_id, product_id, quantity, price) VALUES (%s, %s, %s, %s)", (order_id, direct_pid, direct_qty, product['price']))
                
                # Update Stock
                cursor.execute("UPDATE products SET stock_quantity = stock_quantity - %s WHERE product_id = %s", (direct_qty, direct_pid))
                
                conn.commit()
                cursor.close()
                conn.close()
                
                flash('Order placed successfully!', 'success')
                return redirect(url_for('order_confirmation', order_id=order_id))
                
            except Exception as e:
                flash(f"Error placing direct order: {e}", 'danger')
                return redirect(url_for('checkout', product_id=direct_pid, quantity=direct_qty))

        else:
            # Normal Cart Order
            order_id, message = db_queries.create_order(user_id, order_data)
        
            if order_id:
                flash('Order placed successfully!', 'success')
                return redirect(url_for('order_confirmation', order_id=order_id))
            else:
                flash(f'Error placing order: {message}', 'danger')
                return redirect(url_for('checkout'))

    # GET Request - Show Checkout Form with Summary
    if direct_product_id:
        product, _, _, _ = db_queries.get_product_details(direct_product_id)
        if not product:
            flash("Invalid product.", "danger")
            return redirect(url_for('home'))
            
        # Simulate cart item structure for template
        cart_items = [{
            'product_id': product['product_id'],
            'name': product['name'],
            'image_url': product['image_url'],
            'price': product['price'],
            'quantity': direct_quantity,
            'total_price': product['price'] * direct_quantity
        }]
        grand_total = cart_items[0]['total_price']
    else:
        cart_items, grand_total = db_queries.get_cart_items(user_id)
        if not cart_items:
             flash('Your cart is empty.', 'info')
             return redirect(url_for('cart'))

    return render_template('checkout.html', cart_items=cart_items, grand_total=grand_total, direct_product_id=direct_product_id, direct_quantity=direct_quantity)

@app.route('/order_confirmation/<int:order_id>')
@login_required
def order_confirmation(order_id):
    order, order_items = db_queries.get_order_details(order_id, session['user_id'])

    if not order:
        return "Order not found", 404

    return render_template('order_confirmation.html', order=order, order_items=order_items)

# ==========================
# AUTHENTICATION
# ==========================

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        user = db_queries.get_user_by_email(email)

        if user and check_password_hash(user['password_hash'], password):
            session['user_id'] = user['user_id']
            session['username'] = user['username']
            session['role'] = user['role']
            flash('Login successful!', 'success')

            if user['role'] == 'admin':
                return redirect(url_for('admin_dashboard'))
            return redirect(url_for('home'))
        else:
            flash('Invalid email or password.', 'danger')

    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']

        hashed_password = generate_password_hash(password)

        success, message = db_queries.create_user(username, email, hashed_password)
        
        if success:
            flash('Registration successful! Please login.', 'success')
            return redirect(url_for('login'))
        else:
             flash(f"Error: {message}", 'danger')

    return render_template('register.html')

@app.route('/profile')
@login_required
def profile():
    user = db_queries.get_user_by_id(session['user_id'])
    orders = db_queries.get_user_orders(session['user_id'])
    return render_template('profile.html', user=user, orders=orders)

@app.route('/logout')
def logout():
    session.clear()
    flash('Logged out successfully.', 'info')
    return redirect(url_for('login'))

# ==========================
# ADMIN
# ==========================

@app.route('/admin')
@login_required
@admin_required
def admin_dashboard():
    stats = db_queries.get_dashboard_stats()
    recent_products = db_queries.get_recent_products()
    return render_template('admin.html', stats=stats, recent_products=recent_products)

# ==========================
# ADMIN - USER MANAGEMENT
# ==========================



@app.route('/admin/users/<int:user_id>/edit', methods=['GET', 'POST'])
@login_required
@admin_required
def admin_edit_user(user_id):
    conn = get_db_connection()
    user = None
    if conn:
        cursor = conn.cursor(dictionary=True)
        if request.method == 'POST':
            role = request.form.get('role')
            cursor.execute("UPDATE users SET role = %s WHERE user_id = %s", (role, user_id))
            conn.commit()
            flash('User role updated successfully.', 'success')
            cursor.close()
            conn.close()
            return redirect(url_for('admin_users'))
        
        cursor.execute("SELECT * FROM users WHERE user_id = %s", (user_id,))
        user = cursor.fetchone()
        cursor.close()
        conn.close()
    
    return render_template('admin/user_form.html', user=user)

@app.route('/admin/users/<int:user_id>/delete', methods=['POST'])
@login_required
@admin_required
def admin_delete_user(user_id):
    if user_id == session['user_id']:
        flash('You cannot delete yourself.', 'danger')
        return redirect(url_for('admin_users'))

    conn = get_db_connection()
    if conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM users WHERE user_id = %s", (user_id,))
        conn.commit()
        cursor.close()
        conn.close()
        flash('User deleted successfully.', 'success')
    return redirect(url_for('admin_users'))

    return redirect(url_for('admin_users'))

# ==========================
# ADMIN - CATEGORY MANAGEMENT
# ==========================

@app.route('/admin/categories')
@login_required
@admin_required
def admin_categories():
    conn = get_db_connection()
    categories = []
    if conn:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM categories")
        categories = cursor.fetchall()
        cursor.close()
        conn.close()
    return render_template('admin/categories.html', categories=categories)

@app.route('/admin/categories/add', methods=['GET', 'POST'])
@login_required
@admin_required
def admin_add_category():
    if request.method == 'POST':
        name = request.form.get('name')
        description = request.form.get('description')
        
        conn = get_db_connection()
        if conn:
            cursor = conn.cursor()
            try:
                cursor.execute("INSERT INTO categories (name, description) VALUES (%s, %s)", (name, description))
                conn.commit()
                flash('Category added successfully!', 'success')
                return redirect(url_for('admin_categories'))
            except Error as e:
                flash(f'Error adding category: {e}', 'danger')
            finally:
                cursor.close()
                conn.close()
    
    return render_template('admin/category_form.html', category=None)

@app.route('/admin/categories/<int:category_id>/edit', methods=['GET', 'POST'])
@login_required
@admin_required
def admin_edit_category(category_id):
    conn = get_db_connection()
    category = None
    if conn:
        cursor = conn.cursor(dictionary=True)
        
        if request.method == 'POST':
            name = request.form.get('name')
            description = request.form.get('description')
            try:
                cursor.execute("UPDATE categories SET name = %s, description = %s WHERE category_id = %s", (name, description, category_id))
                conn.commit()
                flash('Category updated successfully!', 'success')
                return redirect(url_for('admin_categories'))
            except Error as e:
                flash(f'Error updating category: {e}', 'danger')
            finally:
                cursor.close()
                conn.close()
        
        cursor.execute("SELECT * FROM categories WHERE category_id = %s", (category_id,))
        category = cursor.fetchone()
        
        if not category:
            cursor.close()
            conn.close()
            return "Category not found", 404

    return render_template('admin/category_form.html', category=category)

@app.route('/admin/categories/<int:category_id>/delete', methods=['POST'])
@login_required
@admin_required
def admin_delete_category(category_id):
    conn = get_db_connection()
    if conn:
        cursor = conn.cursor()
        try:
            cursor.execute("DELETE FROM categories WHERE category_id = %s", (category_id,))
            conn.commit()
            flash('Category deleted successfully.', 'success')
        except Error as e:
            flash(f'Error deleting category: {e} (Maybe check if products are using it?)', 'danger')
        finally:
            cursor.close()
            conn.close()
    return redirect(url_for('admin_categories'))

# ==========================
# ADMIN - ORDER MANAGEMENT
# ==========================

@app.route('/admin/orders')
@login_required
@admin_required
def admin_orders():
    conn = get_db_connection()
    orders = []
    status_filter = request.args.get('status', '')
    
    if conn:
        cursor = conn.cursor(dictionary=True)
        if status_filter:
            cursor.execute("""
                SELECT o.*, u.username, u.email
                FROM orders o
                JOIN users u ON o.user_id = u.user_id
                WHERE o.status = %s
                ORDER BY o.created_at DESC
            """, (status_filter,))
        else:
            cursor.execute("""
                SELECT o.*, u.username, u.email
                FROM orders o
                JOIN users u ON o.user_id = u.user_id
                ORDER BY o.created_at DESC
            """)
        orders = cursor.fetchall()
        cursor.close()
        conn.close()
    
    return render_template('admin/orders.html', orders=orders, status_filter=status_filter)

@app.route('/admin/orders/<int:order_id>')
@login_required
@admin_required
def admin_order_detail(order_id):
    conn = get_db_connection()
    order = None
    items = []
    
    if conn:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("""
            SELECT o.*, u.username, u.email
            FROM orders o
            JOIN users u ON o.user_id = u.user_id
            WHERE o.order_id = %s
        """, (order_id,))
        order = cursor.fetchone()
        
        cursor.execute("""
            SELECT oi.*, p.name, p.image_url
            FROM order_items oi
            JOIN products p ON oi.product_id = p.product_id
            WHERE oi.order_id = %s
        """, (order_id,))
        items = cursor.fetchall()
        cursor.close()
        conn.close()
    
    return render_template('admin/order_detail.html', order=order, items=items)

@app.route('/admin/orders/<int:order_id>/status', methods=['POST'])
@login_required
@admin_required
def admin_update_order_status(order_id):
    new_status = request.form.get('status')
    valid_statuses = ['Pending', 'Confirmed', 'Shipped', 'Delivered', 'Cancelled']
    
    if new_status not in valid_statuses:
        flash('Invalid status.', 'danger')
        return redirect(url_for('admin_orders'))
    
    success, message = db_queries.update_order_status(order_id, new_status)
    if success:
        flash(f'Order #{order_id} status updated to {new_status}.', 'success')
    else:
        flash(f"Error: {message}", 'danger')
    
    return redirect(url_for('admin_orders'))

# ==========================
# ADMIN - PRODUCT MANAGEMENT
# ==========================

@app.route('/admin/products')
@login_required
@admin_required
def admin_products():
    products = db_queries.get_admin_products()
    return render_template('admin/products.html', products=products)

@app.route('/admin/products/add', methods=['GET', 'POST'])
@login_required
@admin_required
def admin_add_product():
    categories = db_queries.get_categories()
        
    if request.method == 'POST':
        data = {
            'name': request.form.get('name'),
            'brand': request.form.get('brand'),
            'category_id': request.form.get('category_id'),
            'price': request.form.get('price'),
            'stock_quantity': request.form.get('stock_quantity'),
            'description': request.form.get('description'),
            'specifications': request.form.get('specifications'),
            'image_url': request.form.get('image_url', 'default.jpg')
        }
        
        success, message = db_queries.add_product(data)
        
        if success:
            flash(message, 'success')
            return redirect(url_for('admin_products'))
        else:
            flash(f"Error: {message}", 'danger')
    
    return render_template('admin/product_form.html', product=None, categories=categories)

@app.route('/admin/products/<int:product_id>/edit', methods=['GET', 'POST'])
@login_required
@admin_required
def admin_edit_product(product_id):
    product, _, _, _ = db_queries.get_product_details(product_id)
    categories = db_queries.get_categories()

    if request.method == 'POST':
        data = {
            'name': request.form.get('name'),
            'brand': request.form.get('brand'),
            'category_id': request.form.get('category_id'),
            'price': request.form.get('price'),
            'stock_quantity': request.form.get('stock_quantity'),
            'description': request.form.get('description'),
            'specifications': request.form.get('specifications'),
            'image_url': request.form.get('image_url')
        }
        
        success, message = db_queries.update_product(product_id, data)
        if success:
            flash(message, 'success')
            return redirect(url_for('admin_products'))
        else:
            flash(f"Error: {message}", 'danger')
    
    return render_template('admin/product_form.html', product=product, categories=categories)

@app.route('/admin/products/<int:product_id>/delete', methods=['POST'])
@login_required
@admin_required
def admin_delete_product(product_id):
    success, message = db_queries.delete_product(product_id)
    if success:
        flash(message, 'success')
    else:
        flash(f"Error: {message}", 'danger')
    return redirect(url_for('admin_products'))

# ==========================
# ADMIN - USER MANAGEMENT
# ==========================

@app.route('/admin/users')
@login_required
@admin_required
def admin_users():
    users = db_queries.get_all_users()
    return render_template('admin/users.html', users=users)

# ==========================
# STATIC PAGES
# ==========================

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/contact')
def contact():
    return render_template('contact.html')

# ==========================
# RUN SERVER
# ==========================

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
