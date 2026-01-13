const mongoose = require('mongoose');

const bookingSchema = new mongoose.Schema({
  pandit_id: { type: mongoose.Schema.Types.ObjectId, ref: 'Pandit' },
  customer_id: { type: mongoose.Schema.Types.ObjectId, ref: 'Customer' },
  type: { type: String, enum: ['chat', 'call', 'puja'] },
  minutes: Number,
  amount: Number,
  payment_status: { type: String, enum: ['pending', 'paid', 'failed'], default: 'pending' },
  booking_status: { type: String, enum: ['pending', 'confirmed', 'completed', 'cancelled'], default: 'pending' }
}, { timestamps: true });

module.exports = mongoose.model('Booking', bookingSchema);