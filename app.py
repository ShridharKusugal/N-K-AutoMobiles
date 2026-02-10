from flask import Flask, render_template, request, redirect, url_for, flash, session, make_response, jsonify
from flask_mail import Mail, Message
import mysql.connector
from mysql.connector import Error
from functools import wraps
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import os
import db_queries
from datetime import datetime, timedelta
import uuid
import csv
import io
import json
from email_validator import validate_email, EmailNotValidError
from email_validator.exceptions import EmailUndeliverableError
import random
import string
# import razorpay
import re
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = Flask(__name__)
app.secret_key = 'nk_automobiles_secret_key_123'
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=30)

# Email Configuration
app.config['MAIL_SERVER'] = os.getenv('MAIL_SERVER', 'smtp.gmail.com')
app.config['MAIL_PORT'] = int(os.getenv('MAIL_PORT', 587))
app.config['MAIL_USE_TLS'] = os.getenv('MAIL_USE_TLS', 'True').lower() == 'true'
app.config['MAIL_USERNAME'] = os.getenv('MAIL_USERNAME')
app.config['MAIL_PASSWORD'] = os.getenv('MAIL_PASSWORD')
app.config['MAIL_DEFAULT_SENDER'] = os.getenv('MAIL_DEFAULT_SENDER', app.config['MAIL_USERNAME'])

mail = Mail(app)

# ==========================
# RAZORPAY CONFIGURATION (REMOVED)
# ==========================
RAZORPAY_KEY_ID = os.getenv('RAZORPAY_KEY_ID', 'your_key_id_here')
RAZORPAY_KEY_SECRET = os.getenv('RAZORPAY_KEY_SECRET', 'your_key_secret_here')
# razorpay_client = razorpay.Client(auth=(RAZORPAY_KEY_ID, RAZORPAY_KEY_SECRET))

@app.before_request
def load_guest_data():
    """Load guest orders from cookies if session is empty (e.g. browser restart)"""
    if 'user_id' not in session and 'guest_order_ids' not in session:
        cookie_orders = request.cookies.get('guest_orders')
        if cookie_orders:
            try:
                order_ids = json.loads(cookie_orders)
                if isinstance(order_ids, list):
                    session['guest_order_ids'] = order_ids
            except Exception:
                pass

@app.after_request
def add_header(response):
    """
    Add headers to prevent caching and save guest order IDs to cookies.
    """
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    
    # Save guest orders to cookie for 30 days
    if 'guest_order_ids' in session:
        response.set_cookie('guest_orders', 
                            json.dumps(session['guest_order_ids']),
                            max_age=30*24*60*60)
                            
    return response

# ==========================
# FILE UPLOAD CONFIGURATION
# ==========================
UPLOAD_FOLDER = os.path.join(app.static_folder, 'products')
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp', 'mp4', 'webm', 'mov'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['REVIEWS_UPLOAD_FOLDER'] = os.path.join(app.static_folder, 'reviews')
app.config['PAYMENTS_UPLOAD_FOLDER'] = os.path.join(app.static_folder, 'payments')
app.config['MAX_CONTENT_LENGTH'] = 64 * 1024 * 1024  # 64MB max file size for videos

# Ensure upload folders exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(app.config['REVIEWS_UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['PAYMENTS_UPLOAD_FOLDER'], exist_ok=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# ==========================
# DATABASE CONFIGURATION
# ==========================
db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': 'Shri@2004',
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
        # Allow access if user is logged in OR if it's a guest session
        if 'user_id' not in session and not session.get('is_guest'):
            flash('Please login first.', 'warning')
            return redirect(url_for('login', next=request.url))
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

def send_email(subject, recipient, body, html=None):
    try:
        msg = Message(subject, recipients=[recipient])
        msg.body = body
        if html:
            msg.html = html
        mail.send(msg)
        return True
    except Exception as e:
        print(f"Error sending email: {e}")
        return False

def send_order_confirmation_email(order_id):
    """Fetches order details and sends a detailed HTML confirmation email."""
    try:
        order, items = db_queries.get_order_details(order_id)
        if not order:
            return False
            
        subtotal = sum(float(item['price']) * int(item['quantity']) for item in items)
        
        html_body = render_template('emails/order_confirmation.html', 
                                    order=order, 
                                    items=items, 
                                    subtotal=subtotal)
        
        # Plain text version for non-HTML clients
        text_body = f"Hello {order['full_name']},\n\nYour order #{order_id} has been placed successfully.\nTotal Amount: ₹{order['total_amount']}\n\nYou can track your order here: {url_for('order_confirmation', order_id=order_id, _external=True)}"
        
        return send_email(f'Order Confirmed - NK Automobiles #{order_id}', order['email'], text_body, html=html_body)
    except Exception as e:
        print(f"Error in send_order_confirmation_email: {e}")
        return False

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
    elif 'cart' in session:
        count = sum(item['quantity'] for item in session['cart'].values())
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
    selected_brands = request.args.getlist('brand')
    min_price = request.args.get('min_price')
    max_price = request.args.get('max_price')
    sort_by = request.args.get('sort_by', 'newest')
    
    products = db_queries.get_filtered_products(category_id, selected_brands, min_price, max_price, sort_by)
    
    categories = db_queries.get_categories()
    all_brands = db_queries.get_all_brands()
    global_min, global_max = db_queries.get_price_range()

    return render_template('products.html', 
                          products=products, 
                          categories=categories,
                          all_brands=all_brands,
                          selected_brands=selected_brands,
                          min_price=int(min_price) if min_price else int(global_min),
                          max_price=int(max_price) if max_price else int(global_max),
                          global_min=int(global_min),
                          global_max=int(global_max),
                          current_category=category_id,
                          sort_by=sort_by)

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
            db_queries.add_log('Activity', user_id=session['user_id'], subject='New Review', content=f"User {session['username']} reviewed product #{product_id} with rating {rating}.")
            flash('Review submitted successfully!', 'success')
        except Error as e:
            print(f"Error submitting review: {e}")
            flash('Error submitting review.', 'danger')
        finally:
            cursor.close()
            conn.close()
            
    return redirect(url_for('product_detail', product_id=product_id))


@app.route('/cart')
def cart():
    if session.get('role') == 'admin':
        flash('Admins cannot shop. Please use the dashboard to manage orders.', 'warning')
        return redirect(url_for('admin_dashboard'))
    
    if 'user_id' in session:
        cart_items, grand_total = db_queries.get_cart_items(session['user_id'])
    else:
        # Handle Guest Cart
        guest_cart = session.get('cart', {})
        cart_items = []
        grand_total = 0
        for product_id, item in guest_cart.items():
            product, _, _, _ = db_queries.get_product_details(product_id)
            if product:
                cart_items.append({
                    'product_id': product['product_id'],
                    'name': product['name'],
                    'price': product['price'],
                    'image_url': product['image_url'],
                    'quantity': item['quantity'],
                    'total_price': product['price'] * item['quantity']
                })
                grand_total += product['price'] * item['quantity']
                
    return render_template('cart.html', cart_items=cart_items, grand_total=grand_total)

@app.route('/add_to_cart/<int:product_id>', methods=['GET', 'POST'])
def add_to_cart(product_id):
    if session.get('role') == 'admin':
        flash('Admins cannot purchase products.', 'danger')
        return redirect(url_for('admin_dashboard'))

    product, _, _, _ = db_queries.get_product_details(product_id)
    if not product:
        flash('Product not found.', 'danger')
        return redirect(url_for('home'))

    # If GET, it's likely a redirect from guest login or buy now
    if request.method == 'GET':
        quantity = 1
        action = 'add_to_cart'
    else:
        try:
            quantity = int(request.form.get('quantity', 1))
        except ValueError:
            quantity = 1
        action = request.form.get('action', 'add_to_cart')
    
    # Check Stock
    if quantity > product['stock_quantity']:
        flash(f"Only {product['stock_quantity']} units available.", 'warning')
        return redirect(url_for('product_detail', product_id=product_id))

    if 'user_id' in session:
        # Logged in User Logic
        db_queries.add_to_cart_db(session['user_id'], product_id, quantity)
        flash(f"{product['name']} added to cart!", 'success')
    else:
        # Guest User Logic
        if 'cart' not in session:
            session['cart'] = {}
        
        cart = session['cart']
        pid_str = str(product_id)
        if pid_str in cart:
            cart[pid_str]['quantity'] += quantity
        else:
            cart[pid_str] = {'quantity': quantity}
        session['cart'] = cart
        flash(f"{product['name']} added to guest cart!", 'success')
    
    if action == 'buy_now' or request.args.get('action') == 'buy_now':
        return redirect(url_for('checkout'))
    
    return redirect(url_for('cart'))


@app.route('/remove_from_cart/<int:product_id>', methods=['POST'])
def remove_from_cart(product_id):
    if 'user_id' in session:
        success, message = db_queries.remove_from_cart(session['user_id'], product_id)
    else:
        # Guest Cart
        cart = session.get('cart', {})
        pid_str = str(product_id)
        if pid_str in cart:
            del cart[pid_str]
            session['cart'] = cart
            success, message = True, "Item removed from cart"
        else:
            success, message = False, "Item not found in cart"
            
    if success:
        flash(message, 'success')
    else:
        flash(message, 'danger')
    return redirect(url_for('cart'))

@app.route('/update_cart/<int:product_id>', methods=['POST'])
def update_cart(product_id):
    action = request.form.get('action')
    try:
        current_qty = int(request.form.get('quantity'))
        if action == 'confirm':
             new_qty = current_qty
        elif action == 'increase':
            new_qty = current_qty + 1
        elif action == 'decrease':
            new_qty = current_qty - 1
        else:
            new_qty = current_qty

        if 'user_id' in session:
            success, message = db_queries.update_cart_quantity(session['user_id'], product_id, new_qty)
        else:
            # Guest logic
            if new_qty <= 0:
                return remove_from_cart(product_id)
            
            product, _, _, _ = db_queries.get_product_details(product_id)
            if not product:
                success, message = False, "Product not found"
            elif new_qty > product['stock_quantity']:
                success, message = False, f"Only {product['stock_quantity']} units available"
            else:
                cart = session.get('cart', {})
                cart[str(product_id)] = {'quantity': new_qty}
                session['cart'] = cart
                success, message = True, "Quantity updated"

        if not success:
            flash(message, 'warning')
            
    except ValueError:
        pass
        
    return redirect(url_for('cart'))

@app.route('/wishlist')
@login_required
def wishlist():
    if 'user_id' not in session:
        flash("Login to maintain a personal wishlist.", "info")
        return redirect(url_for('login'))
    items = db_queries.get_wishlist_items(session['user_id'])
    return render_template('wishlist.html', items=items)

@app.route('/wishlist/toggle/<int:product_id>', methods=['POST'])
@login_required
def toggle_wishlist(product_id):
    if 'user_id' not in session:
        flash("Please login to use the wishlist.", "info")
        return redirect(url_for('login'))
    success, message = db_queries.toggle_wishlist(session['user_id'], product_id)
    if success:
        flash(message, 'success')
    else:
        flash(message, 'danger')
    return redirect(request.referrer or url_for('products'))

@app.route('/api/validate-coupon', methods=['POST'])
def api_validate_coupon():
    data = request.json
    code = data.get('code')
    total = data.get('total')
    
    if not code:
        return {'success': False, 'message': 'No code provided'}, 400
        
    coupon, message = db_queries.validate_coupon(code, total)
    if coupon:
        return {
            'success': True,
            'message': message,
            'discount_value': float(coupon['discount_value']),
            'discount_type': coupon['discount_type']
        }
    return {'success': False, 'message': message}

@app.route('/checkout', methods=['GET', 'POST'])
def checkout():
    if session.get('role') == 'admin':
        flash('Admins cannot perform checkout.', 'danger')
        return redirect(url_for('admin_dashboard'))
    
    user_id = session.get('user_id')
    user = db_queries.get_user_by_id(user_id) if user_id else None
    
    # Direct Buy Logic
    direct_product_id = request.args.get('product_id')
    direct_quantity = int(request.args.get('quantity', 1))
    
    if request.method == 'POST':
        # Get address details from form
        order_data = {
            'full_name': request.form['full_name'],
            'email': request.form['email'],
            'phone': request.form['phone_number'],
            'pincode': request.form['pincode'],
            'addr1': request.form['address_line1'],
            'addr2': request.form['address_line2'],
            'landmark': request.form.get('landmark', ''),
            'city': request.form['city'],
            'state': request.form['state'],
            'payment_method': request.form.get('payment_method', 'COD'),
            'transaction_id': request.form.get('transaction_id', ''),
            'applied_coupon': request.form.get('applied_coupon', '').strip().upper()
        }
        
        if order_data['landmark']:
            order_data['addr2'] += f", Near {order_data['landmark']}"

        # VALIDATION: Check Payment Method
        if order_data['payment_method'] == 'Card':
             flash("Card payments are currently disabled. Please use UPI or COD.", "warning")
             if direct_product_id:
                 return redirect(url_for('checkout', product_id=direct_product_id, quantity=direct_quantity))
             return redirect(url_for('checkout'))

        # VALIDATION: Require Transaction ID & Screenshot for UPI_QR
        if order_data['payment_method'] == 'UPI_QR':
             tid = order_data['transaction_id'].strip()
             
             # 1. Check for empty UTR
             if not tid:
                flash("Please enter the 12-digit Payment Transaction ID / UTR Number.", "danger")
                if direct_product_id:
                    return redirect(url_for('checkout', product_id=direct_product_id, quantity=direct_quantity))
                return redirect(url_for('checkout'))
             
             # 2. Check for exact 12-digit numeric format (Standard UPI UTR)
             if not re.match(r'^[0-9]{12}$', tid):
                 flash("Invalid Transaction ID. A valid UPI UTR must be exactly 12 numeric digits.", "danger")
                 if direct_product_id:
                     return redirect(url_for('checkout', product_id=direct_product_id, quantity=direct_quantity))
                 return redirect(url_for('checkout'))
             
             # 3. Check for duplicate transaction ID
             if db_queries.is_transaction_id_used(tid):
                 flash(f"Transaction ID '{tid}' has already been used. Please enter a valid, new Transaction ID.", "danger")
                 if direct_product_id:
                    return redirect(url_for('checkout', product_id=direct_product_id, quantity=direct_quantity))
                 return redirect(url_for('checkout'))
                 
             # 4. Handle Screenshot Requirement
             screenshot = request.files.get('payment_screenshot')
             if not screenshot or screenshot.filename == '':
                 flash("Please upload a screenshot of your payment for verification.", "danger")
                 if direct_product_id:
                     return redirect(url_for('checkout', product_id=direct_product_id, quantity=direct_quantity))
                 return redirect(url_for('checkout'))
                 
             if screenshot and allowed_file(screenshot.filename):
                 filename = secure_filename(screenshot.filename)
                 unique_filename = f"PAY_{uuid.uuid4().hex[:8]}_{filename}"
                 screenshot.save(os.path.join(app.config['PAYMENTS_UPLOAD_FOLDER'], unique_filename))
                 order_data['payment_screenshot'] = unique_filename
             else:
                 flash("Invalid file format for screenshot. Please upload an image (JPG, PNG).", "danger")
                 if direct_product_id:
                     return redirect(url_for('checkout', product_id=direct_product_id, quantity=direct_quantity))
                 return redirect(url_for('checkout'))


        # Handle Direct Buy Order or Cart Order
        direct_pid = request.form.get('direct_product_id')
        direct_qty = int(request.form.get('direct_quantity', 1))

        # If user is logged in and NOT doing direct buy, use the existing db_queries.create_order
        if 'user_id' in session and not direct_pid:
            order_id, message = db_queries.create_order(user_id, order_data)
        
            if order_id:
                flash('Order placed successfully!', 'success')
                db_queries.add_log('Activity', user_id=user_id, subject='Order Placed (Cart)', content=f"Order #{order_id} placed.")
                
                # Send Actual Confirmation Email
                email_content = f"Hello,\n\nYour order #{order_id} has been placed successfully at NK Automobiles.\n\nThank you for shopping with us!"
                email_sent = send_email(f'Order Confirmed - NK Automobiles #{order_id}', order_data['email'], email_content)
                
                db_queries.add_log('Email', recipient=order_data['email'], subject=f'Order Confirmed #{order_id}', content=f"Your cart order confirmation email {'sent' if email_sent else 'failed to send'}.")
                return redirect(url_for('order_confirmation', order_id=order_id))
            else:
                flash(f'Error placing order: {message}', 'danger')
                return redirect(url_for('checkout'))
        
        # Manual Order Creation for Guest Cart or Direct Buy
        items_to_order = []
        if direct_pid:
            product, _, _, _ = db_queries.get_product_details(direct_pid)
            if product:
                items_to_order.append({'product_id': product['product_id'], 'quantity': direct_qty, 'price': product['price'], 'name': product['name']})
        else:
            # Guest Cart
            guest_cart = session.get('cart', {})
            for pid, item in guest_cart.items():
                product, _, _, _ = db_queries.get_product_details(pid)
                if product:
                    items_to_order.append({'product_id': product['product_id'], 'quantity': item['quantity'], 'price': product['price'], 'name': product['name']})

        if not items_to_order:
            flash("No items found to order.", "danger")
            return redirect(url_for('cart'))

        cart_total = sum(i['price'] * i['quantity'] for i in items_to_order)
        final_total = cart_total
        discount_amount = 0.0
        applied_coupon_id = None
        
        try:
            conn = db_queries.get_db_connection()
            cursor = conn.cursor(dictionary=True)
            
            # Validate Coupon AGAIN server-side
            coupon_code = order_data.get('applied_coupon')
            if coupon_code:
                cursor.execute("""
                    SELECT * FROM coupons 
                    WHERE code = %s 
                    AND (valid_from IS NULL OR valid_from <= NOW())
                    AND (valid_until IS NULL OR valid_until >= NOW())
                    AND (usage_limit IS NULL OR used_count < usage_limit)
                    AND min_purchase <= %s
                """, (coupon_code, cart_total))
                coupon = cursor.fetchone()
                if coupon:
                    applied_coupon_id = coupon['coupon_id']
                    if coupon['discount_type'] == 'percentage':
                        discount_amount = (cart_total * float(coupon['discount_value'])) / 100
                    else:
                        discount_amount = float(coupon['discount_value'])
                    final_total = cart_total - discount_amount

            # Determine order status based on payment method
            order_status = 'Payment Pending' if order_data['payment_method'] in ['UPI', 'UPI_QR'] else 'Pending'
            
            # Insert Order
            cursor.execute("""
                INSERT INTO orders (user_id, email, full_name, phone_number, address_line1, address_line2, city, state, pincode, total_amount, payment_method, transaction_id, payment_screenshot, status, discount_amount, coupon_id)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (user_id, order_data['email'], order_data['full_name'], order_data['phone'], order_data['addr1'], order_data['addr2'], order_data['city'], order_data['state'], order_data['pincode'], final_total, order_data['payment_method'], order_data['transaction_id'], order_data.get('payment_screenshot'), order_status, discount_amount, applied_coupon_id))
            order_id = cursor.lastrowid
            session['last_order_id'] = order_id
            if 'user_id' not in session:
                if 'guest_order_ids' not in session:
                    session['guest_order_ids'] = []
                if order_id not in session['guest_order_ids']:
                    session['guest_order_ids'].append(order_id)
                session.modified = True
            
            # Track Coupon Usage
            if applied_coupon_id:
                cursor.execute("UPDATE coupons SET used_count = used_count + 1 WHERE coupon_id = %s", (applied_coupon_id,))

            # Insert Order Items
            for item in items_to_order:
                cursor.execute("INSERT INTO order_items (order_id, product_id, quantity, price) VALUES (%s, %s, %s, %s)", (order_id, item['product_id'], item['quantity'], item['price']))
                # Update Stock
                cursor.execute("UPDATE products SET stock_quantity = stock_quantity - %s WHERE product_id = %s", (item['quantity'], item['product_id']))
            
            # Award Loyalty Points (1 point per ₹100) if user is logged in
            if user_id:
                loyalty_points = int(final_total / 100)
                if loyalty_points > 0:
                    cursor.execute("UPDATE users SET loyalty_points = loyalty_points + %s WHERE user_id = %s", (loyalty_points, user_id))
            
            conn.commit()
            cursor.close()
            conn.close()
            
            # Clear guest cart if applicable
            if not direct_pid and 'user_id' not in session:
                session.pop('cart', None)

            flash('Order placed successfully!', 'success')
            
            # Log Order Placement
            log_user_id = user_id if user_id else None
            db_queries.add_log('Activity', user_id=log_user_id, subject='Order Placed', content=f"Order #{order_id} placed for ₹{final_total}.")
            
            # Send Detailed Confirmation Email
            email_sent = send_order_confirmation_email(order_id)
            
            db_queries.add_log('Email', recipient=order_data['email'], subject=f'Order Confirmed #{order_id}', content=f"Your order confirmation email {'sent' if email_sent else 'failed to send'}.")

            return redirect(url_for('order_confirmation', order_id=order_id))
            
        except Exception as e:
            flash(f"Error placing order: {e}", 'danger')
            if direct_pid:
                return redirect(url_for('checkout', product_id=direct_pid, quantity=direct_qty))
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
        if 'user_id' in session:
            cart_items, grand_total = db_queries.get_cart_items(user_id)
        else:
            # Guest Cart items for display
            guest_cart = session.get('cart', {})
            cart_items = []
            grand_total = 0
            for pid, item in guest_cart.items():
                product, _, _, _ = db_queries.get_product_details(pid)
                if product:
                    cart_items.append({
                        'product_id': product['product_id'],
                        'name': product['name'],
                        'price': product['price'],
                        'image_url': product['image_url'],
                        'quantity': item['quantity'],
                        'total_price': product['price'] * item['quantity']
                    })
                    grand_total += product['price'] * item['quantity']

        if not cart_items:
             flash('Your cart is empty.', 'info')
             return redirect(url_for('cart'))

    return render_template('checkout.html', cart_items=cart_items, grand_total=grand_total, direct_product_id=direct_product_id, direct_quantity=direct_quantity, user=user, razorpay_key_id=RAZORPAY_KEY_ID)

# ==========================
# RAZORPAY PAYMENT ROUTES
# ==========================

# @app.route('/create-razorpay-order', methods=['POST'])
# @login_required
# def create_razorpay_order():
#     """Create a Razorpay order for payment - REMOVED"""
#     return jsonify({'success': False, 'message': 'Razorpay integration removed'}), 400

@app.route('/verify-razorpay-payment', methods=['POST'])
def verify_razorpay_payment():
    """Verify Razorpay payment signature and create order"""
    try:
        data = request.json
        razorpay_order_id = data.get('razorpay_order_id')
        razorpay_payment_id = data.get('razorpay_payment_id')
        razorpay_signature = data.get('razorpay_signature')
        order_details = data.get('order_details')
        
        # Verify payment signature
        # Check for DEMO payment
        if razorpay_payment_id.startswith('pay_demo_'):
            # This is a demo payment, skip signature verification
            pass
        else:
            params_dict = {
                'razorpay_order_id': razorpay_order_id,
                'razorpay_payment_id': razorpay_payment_id,
                'razorpay_signature': razorpay_signature
            }
            
            try:
                razorpay_client.utility.verify_payment_signature(params_dict)
            except razorpay.errors.SignatureVerificationError:
                return jsonify({'success': False, 'message': 'Payment verification failed'}), 400
        
        # Payment verified successfully, create order in database
        user_id = session.get('user_id')
        
        # Prepare order data
        order_data = {
            'full_name': order_details['full_name'],
            'phone': order_details['phone_number'],
            'pincode': order_details['pincode'],
            'addr1': order_details['address_line1'],
            'addr2': order_details['address_line2'],
            'landmark': order_details.get('landmark', ''),
            'city': order_details['city'],
            'state': order_details['state'],
            'payment_method': 'Razorpay',
            'transaction_id': razorpay_payment_id,
            'applied_coupon': order_details.get('applied_coupon', '').strip().upper()
        }
        
        if order_data['landmark']:
            order_data['addr2'] += f", Near {order_data['landmark']}"
        
        # Handle Direct Buy or Cart Order
        direct_pid = order_details.get('direct_product_id')
        direct_qty = int(order_details.get('direct_quantity', 1))
        
        if direct_pid:
            # Direct Buy Order
            product, _, _, _ = db_queries.get_product_details(direct_pid)
            if not product:
                return jsonify({'success': False, 'message': 'Product not found'}), 404
            
            cart_total = product['price'] * direct_qty
            final_total = cart_total
            discount_amount = 0.0
            applied_coupon_id = None
            
            try:
                conn = db_queries.get_db_connection()
                cursor = conn.cursor(dictionary=True)
                
                # Validate Coupon
                coupon_code = order_data.get('applied_coupon')
                if coupon_code:
                    cursor.execute("""
                        SELECT * FROM coupons 
                        WHERE code = %s 
                        AND (valid_from IS NULL OR valid_from <= NOW())
                        AND (valid_until IS NULL OR valid_until >= NOW())
                        AND (usage_limit IS NULL OR used_count < usage_limit)
                        AND min_purchase <= %s
                    """, (coupon_code, cart_total))
                    coupon = cursor.fetchone()
                    if coupon:
                        applied_coupon_id = coupon['coupon_id']
                        if coupon['discount_type'] == 'percentage':
                            discount_amount = (cart_total * float(coupon['discount_value'])) / 100
                        else:
                            discount_amount = float(coupon['discount_value'])
                        final_total = cart_total - discount_amount
                
                # Verify Payment Amount (Security Check)
                if not razorpay_payment_id.startswith('pay_demo_'):
                    payment_info = razorpay_client.payment.fetch(razorpay_payment_id)
                    if abs(payment_info['amount'] - int(final_total * 100)) > 100:
                        return jsonify({'success': False, 'message': 'Payment amount mismatch. Verification failed.'}), 400

                # Insert Order with 'Confirmed' status (payment already verified)
                cursor.execute("""
                    INSERT INTO orders (user_id, email, full_name, phone_number, address_line1, address_line2, city, state, pincode, total_amount, payment_method, transaction_id, status, discount_amount, coupon_id)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """, (user_id, order_data['email'], order_data['full_name'], order_data['phone'], order_data['addr1'], order_data['addr2'], order_data['city'], order_data['state'], order_data['pincode'], final_total, order_data['payment_method'], order_data['transaction_id'], 'Confirmed', discount_amount, applied_coupon_id))
                order_id = cursor.lastrowid
                session['last_order_id'] = order_id
                if 'user_id' not in session:
                    if 'guest_order_ids' not in session:
                        session['guest_order_ids'] = []
                    if order_id not in session['guest_order_ids']:
                        session['guest_order_ids'].append(order_id)
                    session.modified = True
                
                # Track Coupon Usage
                if applied_coupon_id:
                    cursor.execute("UPDATE coupons SET used_count = used_count + 1 WHERE coupon_id = %s", (applied_coupon_id,))
                
                # Insert Order Item
                cursor.execute("INSERT INTO order_items (order_id, product_id, quantity, price) VALUES (%s, %s, %s, %s)", (order_id, direct_pid, direct_qty, product['price']))
                
                # Update Stock
                cursor.execute("UPDATE products SET stock_quantity = stock_quantity - %s WHERE product_id = %s", (direct_qty, direct_pid))
                
                # Award Loyalty Points (1 point per ₹100)
                loyalty_points = int(final_total / 100)
                if loyalty_points > 0:
                    cursor.execute("UPDATE users SET loyalty_points = loyalty_points + %s WHERE user_id = %s", (loyalty_points, user_id))
                
                conn.commit()
                cursor.close()
                conn.close()
                
                # Log Order Placement
                db_queries.add_log('Activity', user_id=user_id, subject='Order Placed (Razorpay Direct)', content=f"Order #{order_id} placed for ₹{final_total} via Razorpay.")
                
                # Send Detailed Confirmation Email
                send_order_confirmation_email(order_id)
                db_queries.add_log('Email', recipient=order_data.get('email', order_data.get('phone')), subject=f'Order Confirmed #{order_id}', content=f"Detailed order confirmation email sent for direct Razorpay order.")
                
                return jsonify({'success': True, 'order_id': order_id})
                
            except Exception as e:
                return jsonify({'success': False, 'message': f'Error creating order: {str(e)}'}), 500
        else:
            # Cart Order
            order_id, message = db_queries.create_order(user_id, order_data)
            session['last_order_id'] = order_id
            if 'user_id' not in session:
                if 'guest_order_ids' not in session:
                    session['guest_order_ids'] = []
                if order_id not in session['guest_order_ids']:
                    session['guest_order_ids'].append(order_id)
                session.modified = True
            
            if order_id:
                # Security Check: Verify Amount
                try:
                    if not razorpay_payment_id.startswith('pay_demo_'):
                        order_info, _ = db_queries.get_order_details(order_id, user_id)
                        payment_info = razorpay_client.payment.fetch(razorpay_payment_id)
                        
                        if abs(payment_info['amount'] - int(order_info['total_amount'] * 100)) > 100:
                            db_queries.update_order_status(order_id, 'Cancelled')
                            return jsonify({'success': False, 'message': 'Payment amount mismatch. Order cancelled.'}), 400
                except Exception as e:
                    # Log verification failure but proceed if critical? No, fail safe.
                    return jsonify({'success': False, 'message': f'Payment verification error: {str(e)}'}), 500

                # Update order status to Confirmed (payment verified)
                db_queries.update_order_status(order_id, 'Confirmed')
                
                # Award Loyalty Points (1 point per ₹100)
                try:
                    order_info, _ = db_queries.get_order_details(order_id, user_id)
                    loyalty_points = int(order_info['total_amount'] / 100)
                    if loyalty_points > 0:
                        conn = db_queries.get_db_connection()
                        cursor = conn.cursor()
                        cursor.execute("UPDATE users SET loyalty_points = loyalty_points + %s WHERE user_id = %s", (loyalty_points, user_id))
                        conn.commit()
                        cursor.close()
                        conn.close()
                except Exception as e:
                    # Don't fail the order just for loyalty points failure, log it
                    print(f"Error awarding loyalty points: {e}")

                # Log Order Placement
                db_queries.add_log('Activity', user_id=user_id, subject='Order Placed (Razorpay Cart)', content=f"Order #{order_id} placed via Razorpay.")
                
                # Send Detailed Confirmation Email
                send_order_confirmation_email(order_id)
                db_queries.add_log('Email', recipient=order_data.get('email', order_data.get('phone')), subject=f'Order Confirmed #{order_id}', content=f"Detailed order confirmation email sent for cart Razorpay order.")
                
                return jsonify({'success': True, 'order_id': order_id})
            else:
                return jsonify({'success': False, 'message': message}), 500
                
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/razorpay-webhook', methods=['POST'])
def razorpay_webhook():
    """Handle Razorpay webhook for payment events"""
    try:
        # Verify webhook signature
        webhook_signature = request.headers.get('X-Razorpay-Signature')
        webhook_secret = os.getenv('RAZORPAY_WEBHOOK_SECRET', '')
        
        if webhook_secret:
            try:
                razorpay_client.utility.verify_webhook_signature(
                    request.get_data().decode('utf-8'),
                    webhook_signature,
                    webhook_secret
                )
            except razorpay.errors.SignatureVerificationError:
                return jsonify({'status': 'error', 'message': 'Invalid signature'}), 400
        
        # Process webhook event
        event = request.json
        event_type = event.get('event')
        
        if event_type == 'payment.captured':
            # Payment was successfully captured
            payment_entity = event.get('payload', {}).get('payment', {}).get('entity', {})
            payment_id = payment_entity.get('id')
            order_id = payment_entity.get('order_id')
            
            # You can add additional processing here if needed
            # For example, send confirmation emails, update inventory, etc.
            
        return jsonify({'status': 'ok'}), 200
        
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500


@app.route('/order_confirmation/<int:order_id>')
def order_confirmation(order_id):
    user_id = session.get('user_id')
    # Allow if logged in user owns the order OR if it's the last order placed in this session
    order, order_items = db_queries.get_order_details(order_id, user_id)

    if not order and session.get('last_order_id') == order_id:
        order, order_items = db_queries.get_order_details(order_id)

    if not order:
        # Check if they tracked it recently? Let's allow access if tracked in this session too if we want to be generous
        # For now, let's just use the basic checks.
        flash("Order not found or you don't have permission to view it.", "danger")
        return redirect(url_for('home'))

    estimated_date = order['created_at'] + timedelta(days=4)
    return render_template('order_confirmation.html', order=order, order_items=order_items, estimated_date=estimated_date)

@app.route('/order/<int:order_id>/invoice')
def order_invoice(order_id):
    """Guest-accessible invoice (mirrors confirmation logic)"""
    user_id = session.get('user_id')
    order, items = db_queries.get_order_details(order_id, user_id)
    
    # Allow guest access if it's their last order or they follow the link from confirmation
    if not order:
        if session.get('last_order_id') == order_id:
             order, items = db_queries.get_order_details(order_id)
        else:
            # Fallback for tracking: verify with email/phone if they just tracked it?
            # For simplicity, if they have the ID and tracked it previously, it might be in session.
            # But here let's just flash an error if they don't have access.
            flash("You don't have permission to view this invoice.", "danger")
            return redirect(url_for('home'))

    subtotal = sum(float(item['price']) * int(item['quantity']) for item in items)
    return render_template('admin/invoice.html', order=order, items=items, subtotal=subtotal, is_guest=True)


@app.route('/my-orders')
def my_orders():
    """Show order history for logged in users OR guests with session orders"""
    if 'user_id' in session:
        return redirect(url_for('profile'))
        
    guest_order_ids = session.get('guest_order_ids', [])
    orders = []
    
    if guest_order_ids:
        for oid in reversed(guest_order_ids):
            order, items = db_queries.get_order_details(oid)
            if order:
                order['order_items'] = items
                orders.append(order)
                
    return render_template('guest_orders.html', orders=orders)

# ==========================
# AUTHENTICATION
# ==========================

@app.route('/guest_login')
def guest_login():
    next_url = request.args.get('next')
    # Save cart before clearing
    cart = session.get('cart')
    session.clear()
    if cart:
        session['cart'] = cart
    session['is_guest'] = True
    flash('You are now in Guest Mode. You can browse and buy products.', 'success')
    if next_url:
        return redirect(next_url)
    return redirect(url_for('home'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    # Redirect if already logged in
    if 'user_id' in session:
        if session.get('role') == 'admin':
            return redirect(url_for('admin_dashboard'))
        return redirect(url_for('home'))
        
    if request.method == 'POST':
        email = request.form['email'].lower().strip()
        password = request.form['password']

        # Search for user in database
        user = db_queries.get_user_by_email(email)

        if user:
            if check_password_hash(user['password_hash'], password):
                # Complete login directly
                session['user_id'] = user['user_id']
                session['username'] = user['username']
                session['role'] = user['role']
                session.permanent = True

                # Merge Guest Cart if exists
                guest_cart = session.get('cart', {})
                if guest_cart:
                    for product_id, item in guest_cart.items():
                        # Using add_to_cart_db which is the correct name in db_queries.py
                        db_queries.add_to_cart_db(user['user_id'], int(product_id), item['quantity'])
                    session.pop('cart', None) # Clear guest cart after merging
                
                # Link any previous guest orders from this email
                db_queries.link_guest_orders_to_user(user['email'], user['user_id'])
                
                session.pop('is_guest', None) # No longer a guest

                db_queries.add_log('Activity', user_id=user['user_id'], subject='User Login', content=f"User {user['username']} logged in successfully.")
                flash('Login successful!', 'success')

                if user['role'] == 'admin':
                    return redirect(url_for('admin_dashboard'))
                
                return redirect(url_for('home'))
            else:
                flash('Invalid password.', 'danger')
        else:
            flash('Email not found.', 'danger')

    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username'].strip()
        email = request.form['email'].lower().strip()
        password = request.form['password']
        confirm_password = request.form['confirm_password']

        # Password confirmation check
        if password != confirm_password:
            flash("Passwords do not match.", "danger")
            return render_template('register.html')

        # Accurate Email Check: Verify email existence/deliverability
        try:
            # Check syntax only (skip DNS check to allow placeholder domains like nkautomobiles.com)
            email_info = validate_email(email, check_deliverability=False)
            email = email_info.normalized
        except (EmailNotValidError, EmailUndeliverableError) as e:
            flash(f"Email verification failed: {str(e)}. Please provide a real and existing email address.", 'danger')
            return render_template('register.html')

        # Check if email already exists
        if db_queries.get_user_by_email(email):
            flash("Email already registered. Please login.", "warning")
            return redirect(url_for('login'))

        hashed_password = generate_password_hash(password)

        # Generate OTP for registration
        otp = ''.join(random.choices(string.digits, k=6))
        
        # Store in session
        session['pending_user'] = {
            'username': username,
            'email': email,
            'password_hash': hashed_password
        }
        session['registration_otp'] = otp
        
        # Send Actual Email with OTP
        email_content = f"Hello {username},\n\nYour OTP for registration at NK Automobiles is: {otp}\n\nThis OTP is valid for a limited time. Please do not share it with anyone."
        email_sent = send_email('NK Automobiles - Registration OTP', email, email_content)
        
        db_queries.add_log('Email', recipient=email, subject='Registration OTP', content=f"OTP {otp} {'sent successfully' if email_sent else 'failed to send but was generated'}")
        
        flash('An OTP has been sent to your email. Please enter it to complete registration.', 'info')
        return redirect(url_for('verify_otp'))

    return render_template('register.html')

@app.route('/verify-otp', methods=['GET', 'POST'])
def verify_otp():
    if 'pending_user' not in session or 'registration_otp' not in session:
        flash("No active registration found. Please register again.", "warning")
        return redirect(url_for('register'))
        
    if request.method == 'POST':
        user_otp = request.form.get('otp')
        
        if user_otp == session.get('registration_otp'):
            # OTP verified, create user
            user_data = session['pending_user']
            success, message = db_queries.create_user(
                user_data['username'], 
                user_data['email'], 
                user_data['password_hash']
            )
            
            if success:
                # Log success
                user = db_queries.get_user_by_email(user_data['email'])
                if user:
                    db_queries.link_guest_orders_to_user(user['email'], user['user_id'])
                
                db_queries.add_log('Email', recipient=user_data['email'], subject='Welcome to NK Automobiles!', content=f"Hello {user_data['username']}, your account has been created.")
                
                # Clear session
                session.pop('pending_user', None)
                session.pop('registration_otp', None)
                
                flash('Email verified! Registration successful. Please login.', 'success')
                return redirect(url_for('login'))
            else:
                flash(f"Error creating account: {message}", 'danger')
        else:
            flash('Invalid OTP. Please check your email and try again.', 'danger')
            
    return render_template('verify_otp.html', email=session['pending_user']['email'])


@app.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    if 'user_id' not in session:
        flash("Please login to view your profile.", "info")
        return redirect(url_for('login'))
        
    if request.method == 'POST':
        data = {
            'full_name': request.form.get('full_name'),
            'phone': request.form.get('phone'),
            'address_line1': request.form.get('address_line1'),
            'address_line2': request.form.get('address_line2'),
            'city': request.form.get('city'),
            'state': request.form.get('state'),
            'pincode': request.form.get('pincode')
        }
        success, message = db_queries.update_user_profile(session['user_id'], data)
        if success:
            flash('Profile updated successfully!', 'success')
        else:
            flash(f'Error updating profile: {message}', 'danger')
        return redirect(url_for('profile'))

    user = db_queries.get_user_by_id(session['user_id'])
    orders = db_queries.get_user_orders(session['user_id'])
    return render_template('profile.html', user=user, orders=orders)

@app.route('/order/<int:order_id>/cancel', methods=['POST'])
def cancel_order(order_id):
    user_id = session.get('user_id')
    is_guest = session.get('is_guest')
    guest_order_ids = session.get('guest_order_ids', [])
    
    # Verify order belongs to user or is in guest session
    order, items = db_queries.get_order_details(order_id)
    if not order:
        flash("Order not found.", "danger")
        return redirect(url_for('home'))

    # Permission check
    has_permission = False
    if user_id and order['user_id'] == user_id:
        has_permission = True
    elif order_id in guest_order_ids:
        has_permission = True
    elif session.get('last_order_id') == order_id:
        has_permission = True

    if not has_permission:
        flash("Unauthorized action.", "danger")
        return redirect(url_for('home'))
        
    if order['status'] not in ['Pending', 'Payment Pending']:
        flash("This order cannot be cancelled in its current state.", "warning")
        return redirect(url_for('my_orders' if not user_id else 'profile'))
        
    # Update status and log
    success, message = db_queries.update_order_status(order_id, 'Cancelled')
    if success:
        # Restore Stock
        try:
            conn = db_queries.get_db_connection()
            cursor = conn.cursor()
            for item in items:
                cursor.execute("UPDATE products SET stock_quantity = stock_quantity + %s WHERE product_id = %s", (item['quantity'], item['product_id']))
            conn.commit()
            cursor.close()
            conn.close()
            
            db_queries.add_log('Activity', user_id=user_id, subject='Order Cancelled', content=f"User cancelled order #{order_id}")
            flash("Order cancelled successfully.", "info")
        except Exception as e:
            flash(f"Error restoring stock: {e}", "danger")
    else:
        flash(f"Error: {message}", "danger")
        
    return redirect(url_for('profile'))

@app.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        email = request.form['email'].lower().strip()
        user = db_queries.get_user_by_email(email)
        
        if user:
            # Generate 6-digit OTP
            otp = ''.join(random.choices(string.digits, k=6))
            expiry = datetime.now() + timedelta(minutes=15) # 15 minutes validity
            
            if db_queries.set_reset_token(email, otp, expiry):
                # Send Password Reset OTP Email
                email_content = f"Hello {user['username']},\n\nYour OTP for resetting your NK Automobiles password is: {otp}\n\nThis OTP is valid for 15 minutes. Please do not share it with anyone."
                email_sent = send_email('NK Automobiles - Password Reset OTP', email, email_content)
                
                db_queries.add_log('Email', recipient=email, subject='Password Reset OTP', content=f"Reset OTP {otp} {'sent' if email_sent else 'failed to send'} to {email}")
                print(f"\n[RESET OTP] {otp} for {email}: {'Sent' if email_sent else 'Failed'}\n")
                
                session['reset_email'] = email
                flash(f"A 6-digit OTP has been sent to {email}. Please enter it to verify.", "info")
                return redirect(url_for('verify_reset_otp'))
            else:
                 flash("Error generating reset OTP.", "danger")
        else:
            flash("If that email is registered, an OTP has been sent.", "info")
            
        return redirect(url_for('login'))
        
    return render_template('forgot_password.html')

@app.route('/verify-reset-otp', methods=['GET', 'POST'])
def verify_reset_otp():
    if 'reset_email' not in session:
        flash("Please request a password reset first.", "warning")
        return redirect(url_for('forgot_password'))
        
    if request.method == 'POST':
        otp = request.form.get('otp')
        email = session['reset_email']
        
        user = db_queries.get_user_by_email(email)
        if user and user.get('reset_token') == otp:
            # Check expiry
            if user['reset_token_expiry'] and user['reset_token_expiry'] > datetime.now():
                session['otp_verified'] = True
                flash("OTP verified. Please set your new password.", "success")
                return redirect(url_for('reset_password'))
            else:
                flash("OTP has expired. Please request a new one.", "danger")
                return redirect(url_for('forgot_password'))
        else:
            flash("Invalid OTP. Please try again.", "danger")
            
    return render_template('verify_reset_otp.html')

@app.route('/reset-password', methods=['GET', 'POST'])
def reset_password():
    if 'reset_email' not in session or not session.get('otp_verified'):
        flash("Please verify your OTP first.", "warning")
        return redirect(url_for('forgot_password'))
        
    email = session['reset_email']
    user = db_queries.get_user_by_email(email)
    
    if not user:
        flash("User not found.", "danger")
        return redirect(url_for('login'))
        
    if request.method == 'POST':
        password = request.form['password']
        confirm_password = request.form['confirm_password']
        
        if password != confirm_password:
            flash("Passwords do not match.", "danger")
        else:
            hashed_password = generate_password_hash(password)
            if db_queries.update_password(user['user_id'], hashed_password):
                # Clear reset data
                db_queries.set_reset_token(email, None, None)
                session.pop('reset_email', None)
                session.pop('otp_verified', None)
                flash("Your password has been reset successfully. Please login.", "success")
                return redirect(url_for('login'))
            else:
                flash("Error updating password.", "danger")
                
    return render_template('reset_password.html')

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

# ==========================
# ADMIN - ORDER MANAGEMENT
# ==========================

@app.route('/admin/orders')
@login_required
@admin_required
def admin_orders():
    status_filter = request.args.get('status', '')
    search_query = request.args.get('q', '').strip()
    
    conn = get_db_connection()
    orders = []
    if conn:
        cursor = conn.cursor(dictionary=True)
        query = """
            SELECT o.*, 
                   COALESCE(u.username, o.full_name) as display_name,
                   COALESCE(o.email, u.email) as customer_email
            FROM orders o 
            LEFT JOIN users u ON o.user_id = u.user_id 
            WHERE 1=1
        """
        params = []
        
        if status_filter:
            query += " AND o.status = %s"
            params.append(status_filter)
        if search_query:
            query += " AND (o.order_id LIKE %s OR u.username LIKE %s OR u.email LIKE %s OR o.full_name LIKE %s OR o.email LIKE %s)"
            search_term = f"%{search_query}%"
            params.extend([search_term, search_term, search_term, search_term, search_term])
            
        query += " ORDER BY o.created_at DESC"
        cursor.execute(query, tuple(params))
        orders = cursor.fetchall()
        cursor.close()
        conn.close()
    
    return render_template('admin/orders.html', orders=orders, status_filter=status_filter, search_query=search_query)

@app.route('/admin/orders/export')
@login_required
@admin_required
def admin_export_orders():
    orders = db_queries.get_all_orders()
    
    output = io.StringIO()
    writer = csv.writer(output)
    
    # Header
    writer.writerow(['Order ID', 'Customer Name', 'Email', 'Total Amount', 'Status', 'Date'])
    
    for o in orders:
        writer.writerow([
            o['order_id'], 
            o['display_name'], 
            o['customer_email'], 
            o['total_amount'], 
            o['status'], 
            o['created_at'].strftime('%Y-%m-%d %H:%M:%S') if o['created_at'] else ''
        ])
    
    response = make_response(output.getvalue())
    response.headers['Content-Disposition'] = f"attachment; filename=orders_{datetime.now().strftime('%Y%m%d')}.csv"
    response.headers['Content-Type'] = 'text/csv'
    return response

@app.route('/admin/orders/<int:order_id>/invoice')
@login_required
@admin_required
def admin_order_invoice(order_id):
    order, items = db_queries.get_order_details(order_id)
    if not order:
        flash("Order not found.", "danger")
        return redirect(url_for('admin_orders'))
    
    # Calculate subtotal before discount
    subtotal = sum(float(item['price']) * int(item['quantity']) for item in items)
    
    return render_template('admin/invoice.html', order=order, items=items, subtotal=subtotal)

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
            SELECT o.*, u.username, u.email as user_email
            FROM orders o
            LEFT JOIN users u ON o.user_id = u.user_id
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
    tracking_number = request.form.get('tracking_number')
    courier_name = request.form.get('courier_name')
    
    valid_statuses = ['Pending', 'Confirmed', 'Shipped', 'Delivered', 'Cancelled']
    
    if new_status not in valid_statuses:
        flash('Invalid status.', 'danger')
        return redirect(url_for('admin_orders'))
    
    # Use the new function that handles tracking info too
    success, message = db_queries.update_order_tracking(order_id, new_status, tracking_number, courier_name)
    
    if success:
        # Get order to send email
        order, _ = db_queries.get_order_details(order_id)
        if order:
            # Use the email from order if available, otherwise phone_number (though add_log expecting email for 'Email' type)
            recipient_email = order.get('email')
            if not recipient_email:
                # Fallback to fetching user email if it's a member order
                if order.get('user_id'):
                    user = db_queries.get_user_by_id(order['user_id'])
                    if user: recipient_email = user['email']
            
            # If still no email, use phone (less ideal for 'Email' type log but best effort)
            final_recipient = recipient_email if recipient_email else order['phone_number']
            
            db_queries.add_log('Activity', user_id=session['user_id'], subject='Order Status Update', content=f"Order #{order_id} changed to {new_status}.")
            db_queries.add_log('Email', recipient=final_recipient, subject=f"Order Update #{order_id}", content=f"Your order status has been updated to: {new_status}. {f'Courier: {courier_name}, Tracking: {tracking_number}' if tracking_number else ''}")
        
        flash(f'Order #{order_id} updated.', 'success')
    else:
        flash(f"Error: {message}", 'danger')
    
    return redirect(url_for('admin_order_detail', order_id=order_id))

# ==========================
# PUBLIC TRACKING
# ==========================
@app.route('/track-order', methods=['GET', 'POST'])
def track_order():
    order = None
    items = []
    error = None
    
    if request.method == 'POST':
        order_id_str = request.form.get('order_id', '').strip()
        email_or_phone = request.form.get('email_or_phone', '').strip()
        
        if not order_id_str or not email_or_phone:
            flash("Please provide both Order ID and Email/Phone.", "warning")
        else:
            if order_id_str.isdigit():
                order, items = db_queries.get_order_for_tracking(int(order_id_str), email_or_phone)
                if not order:
                    flash("Order not found or details incorrect.", "danger")
            else:
                 flash("Order ID must be a number.", "warning")
    
    return render_template('track_order.html', order=order, items=items)

# ==========================
# ADMIN - PRODUCT MANAGEMENT
# ==========================

@app.route('/admin/products')
@login_required
@admin_required
def admin_products():
    filter_type = request.args.get('filter')
    search_query = request.args.get('q', '').strip()
    
    if search_query:
        products = db_queries.search_admin_products(search_query)
    elif filter_type == 'low_stock':
        products = db_queries.get_low_stock_products()
    else:
        products = db_queries.get_admin_products()
        
    return render_template('admin/products.html', products=products, filter_type=filter_type, search_query=search_query)

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
            db_queries.add_log('Activity', user_id=session['user_id'], subject='Product Added', content=f"Admin added new product: {data['name']}")
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
            db_queries.add_log('Activity', user_id=session['user_id'], subject='Product Updated', content=f"Admin updated product #{product_id}: {data['name']}")
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
        db_queries.add_log('Activity', user_id=session['user_id'], subject='Product Deleted', content=f"Admin deleted product #{product_id}")
        flash(message, 'success')
    else:
        flash(f"Error: {message}", 'danger')
    return redirect(url_for('admin_products'))

# ==========================
# ADMIN - CATEGORY MANAGEMENT
# ==========================

@app.route('/admin/categories')
@login_required
@admin_required
def admin_categories():
    categories = db_queries.get_categories_with_stats()
    return render_template('admin/categories.html', categories=categories)

@app.route('/admin/categories/add', methods=['GET', 'POST'])
@login_required
@admin_required
def admin_add_category():
    if request.method == 'POST':
        name = request.form.get('name')
        description = request.form.get('description')
        success, message = db_queries.add_category(name, description)
        if success:
            flash(message, 'success')
            return redirect(url_for('admin_categories'))
        flash(message, 'danger')
    return render_template('admin/category_form.html', category=None)

@app.route('/admin/categories/<int:category_id>/edit', methods=['GET', 'POST'])
@login_required
@admin_required
def admin_edit_category(category_id):
    # Find category details
    categories = db_queries.get_categories()
    category = next((c for c in categories if c['category_id'] == category_id), None)
    
    if request.method == 'POST':
        name = request.form.get('name')
        description = request.form.get('description')
        success, message = db_queries.update_category(category_id, name, description)
        if success:
            flash(message, 'success')
            return redirect(url_for('admin_categories'))
        flash(message, 'danger')
    return render_template('admin/category_form.html', category=category)

@app.route('/admin/categories/<int:category_id>/delete', methods=['POST'])
@login_required
@admin_required
def admin_delete_category(category_id):
    success, message = db_queries.delete_category(category_id)
    if success:
        flash(message, 'success')
    else:
        flash(message, 'danger')
    return redirect(url_for('admin_categories'))

# ==========================
# ADMIN - REVIEW MANAGEMENT
# ==========================

@app.route('/admin/reviews')
@login_required
@admin_required
def admin_reviews():
    reviews = db_queries.get_all_reviews_admin()
    return render_template('admin/reviews.html', reviews=reviews)

@app.route('/admin/reviews/<int:review_id>/delete', methods=['POST'])
@login_required
@admin_required
def admin_delete_review(review_id):
    success, message = db_queries.delete_review(review_id)
    if success:
        flash(message, 'success')
    else:
        flash(message, 'danger')
    return redirect(url_for('admin_reviews'))

# ==========================
# ADMIN - COUPON MANAGEMENT
# ==========================

@app.route('/admin/coupons')
@login_required
@admin_required
def admin_coupons():
    coupons = db_queries.get_all_coupons()
    return render_template('admin/coupons.html', coupons=coupons)

@app.route('/admin/coupons/add', methods=['GET', 'POST'])
@login_required
@admin_required
def admin_add_coupon():
    if request.method == 'POST':
        data = {
            'code': request.form.get('code').upper(),
            'discount_value': request.form.get('discount_value'),
            'discount_type': request.form.get('discount_type'),
            'min_purchase': request.form.get('min_purchase') or 0,
            'valid_from': request.form.get('valid_from') or None,
            'valid_until': request.form.get('valid_until') or None,
            'usage_limit': request.form.get('usage_limit') or None
        }
        success, message = db_queries.add_coupon(data)
        if success:
            flash(message, 'success')
            return redirect(url_for('admin_coupons'))
        flash(message, 'danger')
    return render_template('admin/coupon_form.html')

@app.route('/admin/coupons/<int:coupon_id>/delete', methods=['POST'])
@login_required
@admin_required
def admin_delete_coupon(coupon_id):
    success, message = db_queries.delete_coupon(coupon_id)
    if success:
        flash(message, 'success')
    else:
        flash(message, 'danger')
    return redirect(url_for('admin_coupons'))

# ==========================
# ADMIN - USER MANAGEMENT
# ==========================

@app.route('/admin/users')
@login_required
@admin_required
def admin_users():
    users = db_queries.get_all_users()
    return render_template('admin/users.html', users=users)

@app.route('/admin/logs')
@login_required
@admin_required
def admin_logs():
    log_type = request.args.get('type')
    logs = db_queries.get_system_logs(log_type=log_type)
    return render_template('admin/logs.html', logs=logs, type=log_type)

# ==========================
# ADMIN - CONTACT MESSAGES
# ==========================

# ==========================
# STATIC PAGES
# ==========================

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/contact', methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        subject = request.form.get('subject')
        message = request.form.get('message')
        
        data = {
            'name': name,
            'email': email,
            'subject': subject,
            'message': message
        }
        
        success, msg = db_queries.add_contact_message(data)
        
        if success:
            db_queries.add_log('Activity', subject='New Contact Message', content=f"From: {name} ({email}) - {subject}")
            flash("Thank you for reaching out! We will get back to you soon.", "success")
        else:
            flash(f"Error sending message: {msg}", "danger")
            
        return redirect(url_for('contact'))

    return render_template('contact.html')

# ==========================
# ADMIN - CONTACT MESSAGES
# ==========================

@app.route('/admin/contact-messages')
@login_required
@admin_required
def admin_contact_messages():
    messages = db_queries.get_contact_messages(limit=100)
    return render_template('admin/contact_messages.html', messages=messages)

@app.route('/admin/contact-messages/<int:message_id>/status', methods=['POST'])
@login_required
@admin_required
def admin_update_message_status(message_id):
    status = request.form.get('status')
    success, msg = db_queries.update_contact_status(message_id, status)
    if success:
        flash("Status updated.", "success")
    else:
        flash(f"Error: {msg}", "danger")
    return redirect(url_for('admin_contact_messages'))

@app.route('/admin/contact-messages/<int:message_id>/delete', methods=['POST'])
@login_required
@admin_required
def admin_delete_message(message_id):
    success, msg = db_queries.delete_contact_message(message_id)
    if success:
        flash("Message deleted.", "success")
    else:
        flash(f"Error: {msg}", "danger")
    return redirect(url_for('admin_contact_messages'))


# ==========================
# RUN SERVER
# ==========================

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
