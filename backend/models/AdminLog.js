const mongoose = require('mongoose');

const adminLogSchema = new mongoose.Schema({
  action: String, // 'create', 'update', 'delete'
  entity: String, // 'pandit', 'booking', etc.
  admin_id: String,
  details: Object // optional details
}, { timestamps: true });

module.exports = mongoose.model('AdminLog', adminLogSchema);