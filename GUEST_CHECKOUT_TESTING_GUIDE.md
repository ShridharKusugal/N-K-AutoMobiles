# Guest Checkout & Order Management - Testing Guide

## 🎯 Overview
This guide will help you test all the guest checkout features we've implemented for NK Automobiles.

---

## ✨ Features Implemented

### 1. **Guest Checkout System**
- ✅ Customers can purchase without creating an account
- ✅ Guest session management with cookies (30-day persistence)
- ✅ Email-based order tracking for guests

### 2. **Order ID Awareness & Retention**
- ✅ Automatic popup modal reminding guests to save their Order ID
- ✅ One-click "Copy Order ID" button
- ✅ Pre-checkout notification about Order ID generation

### 3. **Guest Order History**
- ✅ "My Orders" page accessible to guests
- ✅ Order history persists across browser sessions (via cookies)
- ✅ Beautiful order cards with status indicators

### 4. **Account Linking**
- ✅ Automatic linking of guest orders when registering with same email
- ✅ Automatic linking when logging in with same email
- ✅ Seamless transition from guest to registered user

### 5. **Guest Self-Service**
- ✅ Cancel pending orders directly
- ✅ View order invoices
- ✅ Track order status
- ✅ Access order confirmation emails

### 6. **Admin Features**
- ✅ "GUEST" badge on orders placed by non-registered users
- ✅ Clear visibility of guest vs. registered customer orders

---

## 🧪 Testing Steps

### **Test 1: Basic Guest Checkout**

1. **Start Fresh**
   - Open browser in incognito/private mode
   - Navigate to: `http://127.0.0.1:5000`

2. **Browse & Add to Cart**
   - Click "Products" in navigation
   - Select any product
   - Click "Add to Cart" or "Buy Now"

3. **Checkout as Guest**
   - Click cart icon → "Proceed to Checkout"
   - Fill in shipping details:
     ```
     Full Name: John Guest
     Email: johnguest@example.com
     Phone: 9876543210
     Pincode: 580024
     Address Line 1: 123 Test Street
     Address Line 2: Near Test Park
     City: Hubli
     State: Karnataka
     ```
   - Select "Cash on Delivery"
   - Click "Place Order"

4. **Verify Order Confirmation**
   - ✅ Check if "Save Your Order ID" modal appears automatically
   - ✅ Note the Order ID (e.g., #1025)
   - ✅ Click "Copy" button and verify clipboard
   - ✅ Click "I'VE MARKED THE ID" to close modal
   - ✅ Verify order details are displayed correctly

5. **Check Navigation**
   - ✅ Look for "Guest Mode" badge in navbar
   - ✅ Look for "My Orders" link in navbar

---

### **Test 2: Guest Order History**

1. **Access My Orders**
   - Click "My Orders" in navigation
   - ✅ Verify your recent order appears
   - ✅ Check order status badge (Pending/Confirmed/etc.)
   - ✅ Verify order total is correct

2. **View Order Details**
   - Click "VIEW DETAILS" button
   - ✅ Confirm you're redirected to order confirmation page
   - ✅ Verify all order information is accurate

3. **Access Invoice**
   - Click "View Invoice" button
   - ✅ Check invoice displays correctly
   - ✅ Verify "Back to Details" button appears (not "Back to Admin")
   - ✅ Try printing the invoice

---

### **Test 3: Order Tracking**

1. **Track by ID**
   - Click "Track Order" in navigation
   - Enter your Order ID and email
   - Click "TRACK SHIPMENT"
   - ✅ Verify order status timeline appears
   - ✅ Check shipping address is correct
   - ✅ Verify order items are listed

2. **View Invoice from Tracking**
   - Click "VIEW FULL INVOICE" button
   - ✅ Confirm invoice opens correctly

---

### **Test 4: Guest Order Cancellation**

1. **Cancel from My Orders**
   - Go to "My Orders"
   - Find a "Pending" order
   - Click "CANCEL" button
   - ✅ Confirm cancellation prompt appears
   - Confirm cancellation
   - ✅ Verify order status changes to "Cancelled"

2. **Cancel from Order Confirmation**
   - Navigate to order confirmation page
   - Scroll to bottom
   - Click "Cancel Order" link (if order is Pending)
   - ✅ Confirm cancellation works

---

### **Test 5: Cookie Persistence**

1. **Close Browser**
   - Note your Order ID
   - Close the browser completely

2. **Reopen Browser**
   - Open browser again (same profile, not incognito)
   - Navigate to: `http://127.0.0.1:5000`
   - ✅ Check if "My Orders" link still appears
   - Click "My Orders"
   - ✅ Verify your previous orders are still visible

---

### **Test 6: Account Linking**

1. **Register with Same Email**
   - Click "Register" in navigation
   - Use the SAME email as your guest order (e.g., johnguest@example.com)
   - Complete registration with OTP
   - ✅ Login after registration

2. **Check Order History**
   - Click "My Profile"
   - Scroll to "Order History"
   - ✅ Verify your guest orders now appear in your account
   - ✅ Confirm orders are linked to your user account

---

### **Test 7: Email Confirmation**

1. **Check Email Inbox**
   - Open the email account used during checkout
   - ✅ Look for "Order Confirmed - NK Automobiles #[ORDER_ID]" email
   - ✅ Verify email contains:
     - Product details with images
     - Order summary
     - Shipping address
     - "Track Your Order" button
     - "View Invoice" button

2. **Click Email Links**
   - Click "Track Your Order" in email
   - ✅ Verify it opens the order confirmation page
   - Click "View Invoice" in email
   - ✅ Verify invoice opens correctly

---

### **Test 8: Admin View**

1. **Login as Admin**
   - Logout from guest session
   - Login with admin credentials

2. **View Orders**
   - Navigate to Admin Dashboard
   - Click "Manage Orders"
   - ✅ Look for orders with "GUEST" badge
   - ✅ Verify guest orders show customer name from order (not username)
   - ✅ Check that email is displayed correctly

---

### **Test 9: UPI Payment Flow**

1. **Checkout with UPI**
   - Add product to cart
   - Proceed to checkout
   - Select "Pay via UPI / QR Code"
   - ✅ Verify QR code appears
   - ✅ Check for "Order ID will be generated" tip message
   - Enter dummy Transaction ID: TEST123456
   - Check confirmation checkbox
   - Place order

2. **Verify Payment Pending Status**
   - ✅ Check order status shows "Payment Pending"
   - ✅ Verify warning message appears on confirmation page

---

### **Test 10: Multiple Guest Orders**

1. **Place Multiple Orders**
   - Place 2-3 orders as guest (same session)
   - ✅ Verify each order gets unique Order ID

2. **Check My Orders Page**
   - Navigate to "My Orders"
   - ✅ Verify all orders appear in reverse chronological order
   - ✅ Check each order card displays correctly

---

## 🎨 UI/UX Verification Checklist

### Order Confirmation Page
- [ ] Success checkmark animation appears
- [ ] "Save Your Order ID" modal pops up automatically
- [ ] Order ID is prominently displayed with copy button
- [ ] Estimated delivery date shown (if not Payment Pending)
- [ ] All action buttons are visible and styled correctly
- [ ] Cancel order option appears for pending orders

### My Orders Page
- [ ] Page title and description are clear
- [ ] Order cards have glassmorphism effect
- [ ] Status badges are color-coded correctly
- [ ] Product thumbnails display
- [ ] "GUEST" indicator or tip message appears
- [ ] Cancel buttons appear only for pending orders

### Email Template
- [ ] Professional header with NK Automobiles branding
- [ ] Product table is formatted correctly
- [ ] Buttons are styled and clickable
- [ ] Footer contains contact information

### Invoice Page
- [ ] Clean, print-friendly design
- [ ] "Back to Details" button for guests (not "Back to Admin")
- [ ] All order information is accurate
- [ ] Print button works correctly

---

## 🐛 Known Limitations

1. **Guest Session Limits**
   - Guest orders persist for 30 days in cookies
   - Clearing browser data will remove guest order history
   - Recommend guests to register for permanent history

2. **Email Delivery**
   - Requires proper SMTP configuration in `.env`
   - Test emails may go to spam folder

3. **Order Cancellation**
   - Only available for "Pending" and "Payment Pending" orders
   - Cannot cancel "Confirmed", "Shipped", or "Delivered" orders

---

## 📧 Email Configuration

Ensure your `.env` file contains:
```env
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-app-password
MAIL_DEFAULT_SENDER=your-email@gmail.com
```

---

## 🎯 Success Criteria

All tests should pass with:
- ✅ No errors in browser console
- ✅ No errors in Flask terminal
- ✅ Smooth user experience
- ✅ All features working as described
- ✅ Professional UI/UX throughout

---

## 📝 Notes

- The server is running at: `http://127.0.0.1:5000`
- Admin credentials should be set up in your database
- Test in both desktop and mobile views
- Check browser compatibility (Chrome, Firefox, Safari)

---

**Happy Testing! 🚀**
