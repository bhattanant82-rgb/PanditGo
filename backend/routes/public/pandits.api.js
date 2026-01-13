const express = require('express');
const router = express.Router();
const { getActivePandits } = require('../../controllers/pandits.controller');

router.get('/', getActivePandits);

module.exports = router;