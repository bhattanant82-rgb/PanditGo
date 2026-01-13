const mongoose = require('mongoose');

const paymentSchema = new mongoose.Schema({
  booking_id: { type: mongoose.Schema.Types.ObjectId, ref: 'Booking' },
  razorpay_id: String,
  amount: Number,
  platform_commission: Number,
  pandit_earning: Number,
  status: { type: String, enum: ['pending', 'completed', 'failed'], default: 'pending' }
}, { timestamps: true });

module.exports = mongoose.model('Payment', paymentSchema);