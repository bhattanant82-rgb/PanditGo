const express = require('express');
const cors = require('cors');
const bodyParser = require('body-parser');
const fs = require('fs');
const path = require('path');
const notify = require('./events');
const connectDB = require('./db');

const app = express();
const PORT = 3000;

// Connect to MongoDB
connectDB();

// Middleware
app.use(cors());
app.use(bodyParser.json());
app.use(bodyParser.urlencoded({ extended: true }));

// Serve static files for admin
app.use('/admin-ui', express.static(path.join(__dirname, '..', 'admin-ui')));

// Admin routes
const panditsAdminRoutes = require('./routes/admin/pandits.routes');
app.use('/admin/pandits', panditsAdminRoutes);

// Public routes
const panditsPublicRoutes = require('./routes/public/pandits.api');
app.use('/api/pandits', panditsPublicRoutes);

// Data file paths
const dataDir = path.join(__dirname, '..', 'data');
const panditsFile = path.join(dataDir, 'pandits.json');
const customersFile = path.join(dataDir, 'customers.json');
const bookingsFile = path.join(dataDir, 'bookings.json');
const revenueFile = path.join(dataDir, 'revenue.json');
const reportsFile = path.join(dataDir, 'reports.json');
const logsFile = path.join(dataDir, 'logs.json');
const settingsFile = path.join(dataDir, 'settings.json');

// Helper functions
function readJSON(filePath) {
  try {
    return JSON.parse(fs.readFileSync(filePath, 'utf8'));
  } catch (error) {
    console.log(`Error reading ${filePath}:`, error);
    return [];
  }
}

function writeJSON(filePath, data) {
  try {
    fs.writeFileSync(filePath, JSON.stringify(data, null, 2));
    return true;
  } catch (error) {
    console.log(`Error writing ${filePath}:`, error);
    return false;
  }
}

// API Routes

// Get all data endpoints
app.get('/api/pandits', (req, res) => {
  const data = readJSON(panditsFile);
  res.json(data);
});

app.get('/api/customers', (req, res) => {
  const data = readJSON(customersFile);
  res.json(data);
});

app.get('/api/bookings', (req, res) => {
  const data = readJSON(bookingsFile);
  res.json(data);
});

app.get('/api/revenue', (req, res) => {
  const data = readJSON(revenueFile);
  res.json(data);
});

app.get('/api/reports', (req, res) => {
  const data = readJSON(reportsFile);
  res.json(data);
});

app.get('/api/logs', (req, res) => {
  const data = readJSON(logsFile);
  res.json(data);
});

app.get('/api/settings', (req, res) => {
  const data = readJSON(settingsFile);
  res.json(data);
});

// Booking creation with notification
app.post('/api/booking', (req, res) => {
  const booking = req.body;
  booking.id = `BK${Date.now()}`;
  booking.createdAt = new Date().toISOString();

  const bookings = readJSON(bookingsFile);
  bookings.push(booking);
  writeJSON(bookingsFile, bookings);

  // Send notification
  notify("New Booking Created", booking);

  res.json({ success: true, booking: booking });
});

// Pandit management
app.put('/api/pandits/:id/status', (req, res) => {
  const { id } = req.params;
  const { status } = req.body;

  const pandits = readJSON(panditsFile);
  const pandit = pandits.find(p => p.id == id);

  if (pandit) {
    const oldStatus = pandit.status;
    pandit.status = status;
    writeJSON(panditsFile, pandits);

    // Send notification
    notify("Pandit Status Updated", {
      panditId: id,
      name: pandit.name,
      oldStatus: oldStatus,
      newStatus: status,
      updatedBy: "Admin"
    });

    res.json({ success: true, pandit: pandit });
  } else {
    res.status(404).json({ success: false, error: "Pandit not found" });
  }
});

app.put('/api/pandits/:id/payout', (req, res) => {
  const { id } = req.params;
  const pandits = readJSON(panditsFile);
  const pandit = pandits.find(p => p.id == id);

  if (pandit) {
    const payoutAmount = pandit.earnings;
    pandit.earnings = 0; // Reset earnings after payout
    writeJSON(panditsFile, pandits);

    // Update revenue data
    const revenue = readJSON(revenueFile);
    revenue.pendingPayouts -= payoutAmount;
    revenue.completedPayouts += payoutAmount;
    writeJSON(revenueFile, revenue);

    // Send notification
    notify("Pandit Payout Processed", {
      panditId: id,
      name: pandit.name,
      amount: payoutAmount,
      processedAt: new Date().toISOString()
    });

    res.json({ success: true, amount: payoutAmount });
  } else {
    res.status(404).json({ success: false, error: "Pandit not found" });
  }
});

// Customer management
app.put('/api/customers/:id/status', (req, res) => {
  const { id } = req.params;
  const { status } = req.body;

  const customers = readJSON(customersFile);
  const customer = customers.find(c => c.id == id);

  if (customer) {
    const oldStatus = customer.status;
    customer.status = status;
    writeJSON(customersFile, customers);

    // Send notification
    notify("Customer Status Updated", {
      customerId: id,
      name: customer.name,
      email: customer.email,
      oldStatus: oldStatus,
      newStatus: status
    });

    res.json({ success: true, customer: customer });
  } else {
    res.status(404).json({ success: false, error: "Customer not found" });
  }
});

// Settings update
app.put('/api/settings', (req, res) => {
  const newSettings = req.body;
  writeJSON(settingsFile, newSettings);

  notify("Settings Updated", newSettings);

  res.json({ success: true, settings: newSettings });
});

// Login tracking
app.post('/api/login', (req, res) => {
  const { email, role } = req.body;

  notify("Admin Login", {
    email: email,
    role: role,
    timestamp: new Date().toISOString(),
    ip: req.ip
  });

  res.json({ success: true });
});

// Error logging
app.post('/api/log-error', (req, res) => {
  const error = req.body;
  error.timestamp = new Date().toISOString();

  const logs = readJSON(logsFile);
  logs.push(error);
  writeJSON(logsFile, logs);

  notify("System Error Logged", error);

  res.json({ success: true });
});

// ===== NEW CALL/CHAT APIs =====

// Start Call/Chat Session
app.post('/api/start-session', (req, res) => {
  const { pandit_id, user_id, type } = req.body;
  
  const session = {
    session_id: `S${Date.now()}`,
    pandit_id,
    user_id,
    type,
    status: 'active',
    start_time: new Date().toISOString(),
    end_time: null,
    minutes: 0,
    amount: 0
  };

  const bookings = readJSON(bookingsFile);
  bookings.push(session);
  writeJSON(bookingsFile, bookings);

  notify("Session Started", session);

  res.json({ success: true, session });
});

// Update Session (per minute billing)
app.post('/api/update-session', (req, res) => {
  const { session_id, minutes } = req.body;
  
  const bookings = readJSON(bookingsFile);
  const sessionIndex = bookings.findIndex(b => b.booking_id == session_id);
  
  if (sessionIndex === -1) {
    return res.status(404).json({ error: 'Session not found' });
  }

  const session = bookings[sessionIndex];
  const pandits = readJSON(panditsFile);
  const pandit = pandits.find(p => p.id == session.pandit_id);
  
  if (!pandit) {
    return res.status(404).json({ error: 'Pandit not found' });
  }

  // Calculate price per minute
  const pricePerMin = session.type === 'call' ? pandit.call_price_per_min : pandit.chat_price_per_min;
  const newAmount = minutes * pricePerMin;
  
  session.minutes = minutes;
  session.amount = newAmount;
  
  writeJSON(bookingsFile, bookings);

  res.json({ success: true, session });
});

// End Session
app.post('/api/end-session', (req, res) => {
  const { session_id } = req.body;
  
  const bookings = readJSON(bookingsFile);
  const sessionIndex = bookings.findIndex(b => b.booking_id == session_id);
  
  if (sessionIndex === -1) {
    return res.status(404).json({ error: 'Session not found' });
  }

  const session = bookings[sessionIndex];
  session.status = 'completed';
  session.end_time = new Date().toISOString();
  
  // Update pandit wallet
  const pandits = readJSON(panditsFile);
  const panditIndex = pandits.findIndex(p => p.id == session.pandit_id);
  if (panditIndex !== -1) {
    pandits[panditIndex].wallet_balance += session.amount * 0.8; // 80% to pandit
    writeJSON(panditsFile, pandits);
  }

  writeJSON(bookingsFile, bookings);

  notify("Session Completed", session);

  res.json({ success: true, session });
});

// Wallet Top-up (Razorpay integration placeholder)
app.post('/api/wallet-topup', (req, res) => {
  const { user_id, amount, razorpay_payment_id } = req.body;
  
  // Here you would verify Razorpay payment
  // For now, assume success
  
  // Update user wallet (assuming customers.json has wallet_balance)
  const customers = readJSON(customersFile);
  const customerIndex = customers.findIndex(c => c.id == user_id);
  if (customerIndex !== -1) {
    customers[customerIndex].wallet_balance = (customers[customerIndex].wallet_balance || 0) + amount;
    writeJSON(customersFile, customers);
  }

  notify("Wallet Top-up", { user_id, amount, razorpay_payment_id });

  res.json({ success: true, new_balance: customers[customerIndex].wallet_balance });
});

// Get User Wallet Balance
app.get('/api/wallet/:user_id', (req, res) => {
  const { user_id } = req.params;
  const customers = readJSON(customersFile);
  const customer = customers.find(c => c.id == user_id);
  
  res.json({ balance: customer ? customer.wallet_balance || 0 : 0 });
});

// Admin Revenue Dashboard
app.get('/api/admin/revenue', (req, res) => {
  const bookings = readJSON(bookingsFile);
  const pandits = readJSON(panditsFile);
  
  const totalRevenue = bookings.reduce((sum, b) => sum + (b.amount || 0), 0);
  const platformCommission = totalRevenue * 0.2; // 20% commission
  const panditEarnings = totalRevenue * 0.8;
  
  const callMinutes = bookings.filter(b => b.type === 'call').reduce((sum, b) => sum + (b.minutes || 0), 0);
  const chatMinutes = bookings.filter(b => b.type === 'chat').reduce((sum, b) => sum + (b.minutes || 0), 0);
  
  const pendingPayouts = pandits.reduce((sum, p) => sum + (p.wallet_balance || 0), 0);

  res.json({
    total_revenue: totalRevenue,
    platform_commission: platformCommission,
    pandit_earnings: panditEarnings,
    call_minutes_sold: callMinutes,
    chat_minutes_sold: chatMinutes,
    pending_payouts: pendingPayouts
  });
});

// Start server
app.listen(PORT, () => {
  console.log(`🚀 PanditGo Backend Server running on port ${PORT}`);
  console.log(`📧 Gmail notifications enabled`);
  console.log(`📊 Data directory: ${dataDir}`);
});