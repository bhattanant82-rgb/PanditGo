const mongoose = require('mongoose');

const pricingRuleSchema = new mongoose.Schema({
  chat_base_price: Number,
  call_base_price: Number,
  platform_commission_percent: Number
}, { timestamps: true });

module.exports = mongoose.model('PricingRule', pricingRuleSchema);