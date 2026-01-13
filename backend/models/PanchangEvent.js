const mongoose = require('mongoose');

const panchangEventSchema = new mongoose.Schema({
  date: Date,
  tithi: String,
  festival: String,
  is_auspicious: Boolean
}, { timestamps: true });

module.exports = mongoose.model('PanchangEvent', panchangEventSchema);