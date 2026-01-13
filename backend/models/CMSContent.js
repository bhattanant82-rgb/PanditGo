const mongoose = require('mongoose');

const cmsContentSchema = new mongoose.Schema({
  page: String, // 'home', 'pandits', 'pujas'
  section_name: String,
  title: String,
  description: String
}, { timestamps: true });

module.exports = mongoose.model('CMSContent', cmsContentSchema);