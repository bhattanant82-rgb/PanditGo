const express = require('express');
const router = express.Router();

const Pandit = require('../models/Pandit');
const Booking = require('../models/Booking');
const Payment = require('../models/Payment');
const PricingRule = require('../models/PricingRule');
const CMSContent = require('../models/CMSContent');
const PanchangEvent = require('../models/PanchangEvent');
const AdminLog = require('../models/AdminLog');
const Notification = require('../models/Notification');

// Pandits routes
router.get('/pandits', async (req, res) => {
  try {
    const pandits = await Pandit.find();
    res.json(pandits);
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

router.post('/pandits', async (req, res) => {
  try {
    const pandit = new Pandit(req.body);
    await pandit.save();
    const log = new AdminLog({ action: 'create', entity: 'pandit', admin_id: 'admin', details: { pandit_id: pandit._id } });
    await log.save();
    res.json(pandit);
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

router.put('/pandits/:id', async (req, res) => {
  try {
    const pandit = await Pandit.findByIdAndUpdate(req.params.id, req.body, { new: true });
    const log = new AdminLog({ action: 'update', entity: 'pandit', admin_id: 'admin', details: { pandit_id: pandit._id } });
    await log.save();
    res.json(pandit);
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

router.delete('/pandits/:id', async (req, res) => {
  try {
    await Pandit.findByIdAndDelete(req.params.id);
    const log = new AdminLog({ action: 'delete', entity: 'pandit', admin_id: 'admin', details: { pandit_id: req.params.id } });
    await log.save();
    res.json({ message: 'Deleted' });
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

// Bookings routes
router.get('/bookings', async (req, res) => {
  try {
    const bookings = await Booking.find().populate('pandit_id').populate('customer_id');
    res.json(bookings);
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

router.put('/bookings/:id/cancel', async (req, res) => {
  try {
    const booking = await Booking.findByIdAndUpdate(req.params.id, { booking_status: 'cancelled' }, { new: true });
    const log = new AdminLog({ action: 'cancel', entity: 'booking', admin_id: 'admin', details: { booking_id: booking._id } });
    await log.save();
    res.json(booking);
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

// Payments routes
router.get('/payments', async (req, res) => {
  try {
    const payments = await Payment.find().populate('booking_id');
    res.json(payments);
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

// Pricing Rules
router.get('/pricing-rules', async (req, res) => {
  try {
    const rule = await PricingRule.findOne();
    res.json(rule);
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

router.put('/pricing-rules', async (req, res) => {
  try {
    const rule = await PricingRule.findOneAndUpdate({}, req.body, { new: true, upsert: true });
    const log = new AdminLog({ action: 'update', entity: 'pricing-rule', admin_id: 'admin' });
    await log.save();
    res.json(rule);
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

// CMS Content
router.get('/cms-content', async (req, res) => {
  try {
    const contents = await CMSContent.find();
    res.json(contents);
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

router.put('/cms-content/:id', async (req, res) => {
  try {
    const content = await CMSContent.findByIdAndUpdate(req.params.id, req.body, { new: true });
    const log = new AdminLog({ action: 'update', entity: 'cms-content', admin_id: 'admin', details: { content_id: content._id } });
    await log.save();
    res.json(content);
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

// Panchang Events
router.get('/panchang', async (req, res) => {
  try {
    const events = await PanchangEvent.find();
    res.json(events);
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

// Notifications
router.get('/notifications', async (req, res) => {
  try {
    const notifications = await Notification.find().sort({ createdAt: -1 });
    res.json(notifications);
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

// Admin Logs
router.get('/logs', async (req, res) => {
  try {
    const logs = await AdminLog.find().sort({ createdAt: -1 });
    res.json(logs);
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

module.exports = router;