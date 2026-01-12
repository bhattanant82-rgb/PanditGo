# PanditGo Admin Dashboard - Full Control System

## 🚀 Features Implemented

### ✅ Real Gmail Notifications
- **Instant email alerts** for all admin actions
- **Professional HTML emails** with PanditGo branding
- **Event-based notifications**: Bookings, Status Changes, Logins, Errors

### ✅ Complete Admin Dashboard
- **Divine Dark Pro Theme** (#0B0F14 background, #D4AF37 gold)
- **Real-time KPIs** from JSON data
- **Interactive Charts** (Chart.js)
- **Full CRUD Operations** with API calls

### ✅ Backend API System
- **Node.js + Express** server on port 3000
- **RESTful APIs** for all data operations
- **Real JSON file updates** (not just frontend)
- **Error handling & logging**

## 📧 Gmail Setup (MANDATORY)

1. **Enable 2-Step Verification** on your Gmail account
2. **Generate App Password**:
   - Go to Google Account → Security → 2-Step Verification → App passwords
   - Generate password for "Mail"
   - Copy the 16-character password
3. **Credentials are already configured** in `backend/mailer.js`

## 🛠️ Installation & Setup

### 1. Install Node.js Dependencies
```bash
cd backend
npm install
```

### 2. Start Backend Server
```bash
cd backend
npm start
# or for development:
npm run dev
```

Server will start on `http://localhost:3000`

### 3. Start Frontend (XAMPP)
- Open XAMPP Control Panel
- Start Apache
- Open browser: `http://localhost/PanditGo/admin/dashboard.html`

## 📊 Dashboard Sections

### 🏠 Overview
- **KPIs**: Total Pandits, Active Customers, Today's Bookings, Monthly Revenue
- **Charts**: Revenue per Month (Bar), Pandit Availability (Pie)

### 🧑‍💼 Pandits Management
- **View Details**: Click "View" to see pandit info
- **Suspend/Activate**: Updates status + sends Gmail notification
- **Process Payout**: Resets earnings + updates revenue data

### 👥 Customers Management
- **View Details**: Customer information popup
- **Block/Unblock**: Status updates with notifications

### 📅 Bookings Management
- **Real-time booking data** from JSON
- **Status tracking**: Confirmed, Completed, Pending

### 💰 Revenue & Payouts
- **Financial KPIs**: Total revenue, Commission, Pending/Completed payouts
- **Revenue Trend Chart**: Monthly performance

### 📊 Kundli Reports
- **Report Statistics**: Total, Paid, Free reports
- **Report Details Table**: Customer, Type, Date, Amount

### 🚨 Logs & Errors
- **System Events**: Failed bookings, Payment errors, API failures
- **Real-time logging** with timestamps

### ⚙️ Settings
- **Commission Rate**: Platform fee percentage
- **Feature Toggles**: Enable/disable services
- **Max Bookings**: Daily limit

## 📧 Notification Events

The system sends Gmail notifications for:

- ✅ **New Booking Created**
- ✅ **Pandit Status Updated** (Active/Blocked)
- ✅ **Pandit Payout Processed**
- ✅ **Customer Status Updated**
- ✅ **Settings Updated**
- ✅ **Admin Login**
- ✅ **System Errors**

## 🔧 API Endpoints

```
GET  /api/pandits     - Get all pandits
GET  /api/customers   - Get all customers
GET  /api/bookings    - Get all bookings
GET  /api/revenue     - Get revenue data
GET  /api/reports     - Get kundli reports
GET  /api/logs        - Get system logs
GET  /api/settings    - Get admin settings

POST /api/booking     - Create new booking
POST /api/login       - Admin login tracking

PUT  /api/pandits/:id/status   - Update pandit status
PUT  /api/pandits/:id/payout   - Process pandit payout
PUT  /api/customers/:id/status - Update customer status
PUT  /api/settings             - Update admin settings
```

## 🧪 Testing Instructions

### 1. Start Backend
```bash
cd backend
npm start
```

### 2. Open Admin Dashboard
`http://localhost/PanditGo/admin/dashboard.html`

### 3. Login as Admin
- Email: `admin@gmail.com`
- Password: `anything`

### 4. Test Notifications
1. **Go to Pandits tab**
2. **Click "Suspend" on any pandit**
3. **Check Gmail** - You should receive notification instantly

### 5. Test All Features
- Update customer status
- Process pandit payout
- Change settings
- View different sections

## 🔒 Security Features

- **Role-based access** (admin only)
- **Input validation** on all APIs
- **Error logging** with timestamps
- **Gmail authentication** (secure)

## 🚨 Troubleshooting

### Backend Not Starting
```bash
# Check if port 3000 is free
netstat -ano | findstr :3000

# Kill process if needed
taskkill /PID <PID> /F
```

### Gmail Not Working
- Verify App Password is correct
- Check Gmail spam folder
- Ensure 2-Step Verification is enabled

### API Errors
- Check browser console for errors
- Verify backend server is running
- Check JSON file permissions

## 🎯 Next Steps

1. **Add .env file** for secure credentials
2. **Database integration** (MongoDB/PostgreSQL)
3. **Real payment gateway** (Razorpay/Stripe)
4. **SMS notifications** (Twilio)
5. **Mobile app** for admins

---

**Built with ❤️ for PanditGo Admin Control**