const Pandit = require('../models/Pandit');
const Notification = require('../models/Notification');
const AdminLog = require('../models/AdminLog');

// Admin controllers
exports.createPandit = async (req, res) => {
  try {
    const pandit = new Pandit(req.body);
    await pandit.save();
    // Log
    await AdminLog.create({ action: 'create', entity: 'pandit', admin_id: 'admin', details: { pandit_id: pandit._id } });
    res.status(201).json(pandit);
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
};

exports.getAllPandits = async (req, res) => {
  try {
    const pandits = await Pandit.find();
    res.json(pandits);
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
};

exports.updatePandit = async (req, res) => {
  try {
    const pandit = await Pandit.findByIdAndUpdate(req.params.id, req.body, { new: true });
    if (!pandit) return res.status(404).json({ error: 'Pandit not found' });
    // Log
    await AdminLog.create({ action: 'update', entity: 'pandit', admin_id: 'admin', details: { pandit_id: pandit._id } });
    // Notification if availability changed
    if (req.body.availability && req.body.availability !== pandit.availability) {
      await Notification.create({
        type: 'pandit',
        message: `Pandit ${pandit.name} availability changed to ${req.body.availability}`
      });
    }
    res.json(pandit);
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
};

exports.deletePandit = async (req, res) => {
  try {
    const pandit = await Pandit.findByIdAndDelete(req.params.id);
    if (!pandit) return res.status(404).json({ error: 'Pandit not found' });
    await AdminLog.create({ action: 'delete', entity: 'pandit', admin_id: 'admin', details: { pandit_id: req.params.id } });
    res.json({ message: 'Deleted' });
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
};

// Public controllers
exports.getActivePandits = async (req, res) => {
  try {
    const pandits = await Pandit.find({ status: 'active' });
    res.json(pandits);
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
};