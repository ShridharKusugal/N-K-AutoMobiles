# 🚀 Quick Start Guide - Guest Checkout System

## Server Status
✅ **Flask Server Running**
- Local: http://127.0.0.1:5000
- Network: http://192.168.0.118:5000
- Debug Mode: ON
- Debugger PIN: 480-770-857

---

## 🎯 Quick Test (5 Minutes)

### 1. **Open Browser**
```
Navigate to: http://127.0.0.1:5000
```

### 2. **Guest Checkout**
```
Products → Select Item → Add to Cart → Checkout
Fill Form → Select COD → Place Order
```

### 3. **Verify Features**
- [ ] Modal popup appears with "Save Your Order ID!"
- [ ] Order ID is displayed with Copy button
- [ ] "My Orders" link appears in navigation
- [ ] Guest badge shows in navbar

### 4. **Check Order History**
```
Click "My Orders" → See your order → Click "VIEW DETAILS"
```

### 5. **Test Invoice**
```
Click "View Invoice" → Verify invoice loads → Try Print button
```

---

## 📁 Documentation Files Created

1. **GUEST_CHECKOUT_TESTING_GUIDE.md**
   - Complete testing procedures
   - 10 comprehensive test scenarios
   - UI/UX verification checklist

2. **IMPLEMENTATION_SUMMARY.md**
   - Full technical documentation
   - All features explained
   - Code examples and diagrams

3. **This file (QUICK_START.md)**
   - Rapid testing guide
   - Essential commands

---

## 🔑 Key Features to Test

### ✅ Guest Checkout
- No login required
- Email-based tracking
- Session management

### ✅ Order ID System
- Automatic popup reminder
- Copy-to-clipboard button
- Pre-checkout notification

### ✅ Order History
- "My Orders" page
- Cookie persistence (30 days)
- Beautiful order cards

### ✅ Account Linking
- Register with same email
- Orders automatically linked
- Seamless transition

### ✅ Self-Service
- Cancel pending orders
- View invoices
- Track status

### ✅ Email Notifications
- HTML email template
- Product details
- Action buttons

### ✅ Admin Features
- "GUEST" badge
- Clear visibility
- Guest order management

---

## 🎨 What You'll See

### Order Confirmation Page
```
✓ Success Animation
✓ Modal Popup: "SAVE YOUR ORDER ID"
✓ Order ID: #1025 [Copy Button]
✓ Estimated Delivery Date
✓ Action Buttons (Track, Invoice, Cancel)
```

### My Orders Page
```
✓ Guest Mode Badge
✓ Order Cards with Status
✓ Product Thumbnails
✓ Cancel Buttons (for pending)
✓ View Details Links
```

### Email (Check Inbox)
```
✓ Professional Header
✓ Product Table
✓ Shipping Address
✓ Track Order Button
✓ View Invoice Button
```

---

## 🐛 Troubleshooting

### Modal Doesn't Appear?
- Check browser console (F12)
- Verify Bootstrap is loaded
- Clear browser cache

### Can't See My Orders?
- Check if cookies are enabled
- Verify you're not in incognito mode
- Look for "Guest Mode" badge

### Email Not Received?
- Check spam folder
- Verify SMTP settings in `.env`
- Check Flask terminal for errors

### Orders Not Linking?
- Ensure exact email match
- Check database logs
- Verify user was created successfully

---

## 📧 Email Configuration

Create/edit `.env` file:
```env
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-app-password
MAIL_DEFAULT_SENDER=your-email@gmail.com
```

**Note:** For Gmail, use App Password, not regular password!

---

## 🎯 Success Indicators

You'll know it's working when:
1. ✅ Modal appears after placing order
2. ✅ "My Orders" link visible in navbar
3. ✅ Orders persist after browser restart
4. ✅ Email arrives in inbox
5. ✅ Invoice opens correctly
6. ✅ Admin sees "GUEST" badge

---

## 📱 Test on Mobile

Open on your phone:
```
http://192.168.0.118:5000
```

Verify:
- [ ] Responsive design
- [ ] Modal works on mobile
- [ ] Navigation is accessible
- [ ] Forms are easy to fill

---

## 🔄 Reset Testing

To start fresh:
1. Clear browser cookies
2. Use incognito/private mode
3. Or use different email each time

---

## 📞 Need Help?

Check these files:
1. `GUEST_CHECKOUT_TESTING_GUIDE.md` - Detailed tests
2. `IMPLEMENTATION_SUMMARY.md` - Technical details
3. Flask terminal - Error messages
4. Browser console (F12) - JavaScript errors

---

## 🎉 You're All Set!

The server is running and ready for testing. Start with the Quick Test above, then explore all features using the comprehensive testing guide.

**Happy Testing! 🚀**

---

**Last Updated:** February 10, 2026  
**Server Status:** ✅ Running  
**Port:** 5000
