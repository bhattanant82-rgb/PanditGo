const express = require('express');
const router = express.Router();
const {
  createPandit,
  getAllPandits,
  updatePandit,
  deletePandit
} = require('../../controllers/pandits.controller');

router.get('/', getAllPandits);
router.post('/', createPandit);
router.put('/:id', updatePandit);
router.delete('/:id', deletePandit);

module.exports = router;