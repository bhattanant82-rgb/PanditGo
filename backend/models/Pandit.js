const mongoose = require('mongoose');

const panditSchema = new mongoose.Schema({
  name: String,
  photo: String,
  city: String,
  languages: [String],
  expertise: [String],
  experience: Number,
  specialization: String,
  chat_price_per_min: Number,
  call_price_per_min: Number,
  availability: { type: String, enum: ['online', 'offline'], default: 'offline' },
  phone: String,
  rating: { type: Number, default: 0 },
  status: { type: String, enum: ['active', 'blocked'], default: 'active' },
  wallet_balance: { type: Number, default: 0 },
  totalBookings: { type: Number, default: 0 },
  lastActive: Date
}, { timestamps: true });

module.exports = mongoose.model('Pandit', panditSchema);