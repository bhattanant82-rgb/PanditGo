const express = require('express');
const cors = require('cors');
const bodyParser = require('body-parser');
const fs = require('fs');
const path = require('path');
const notify = require('./events');

const app = express();
const PORT = 3000;

// Middleware
app.use(cors());
app.use(bodyParser.json());
app.use(bodyParser.urlencoded({ extended: true }));

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

// Start server
app.listen(PORT, () => {
  console.log(`🚀 PanditGo Backend Server running on port ${PORT}`);
  console.log(`📧 Gmail notifications enabled`);
  console.log(`📊 Data directory: ${dataDir}`);
});