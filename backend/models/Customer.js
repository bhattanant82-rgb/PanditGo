const mongoose = require('mongoose');

const customerSchema = new mongoose.Schema({
  name: String,
  email: String,
  phone: String,
  city: String,
  totalBookings: { type: Number, default: 0 },
  totalSpent: { type: Number, default: 0 },
  lastBooking: Date,
  status: { type: String, enum: ['active', 'inactive'], default: 'active' },
  wallet_balance: { type: Number, default: 0 }
}, { timestamps: true });

module.exports = mongoose.model('Customer', customerSchema);