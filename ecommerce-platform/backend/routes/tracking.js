const express = require('express');
const router = express.Router();
const { trackEvent, trackBatch } = require('../controllers/trackingController');
const { auth } = require('../middleware/auth');

// Auth is optional for tracking — allows anonymous tracking
router.post('/event', (req, res, next) => {
  const token = req.header('Authorization');
  if (token) return auth(req, res, next);
  next();
}, trackEvent);

router.post('/batch', (req, res, next) => {
  const token = req.header('Authorization');
  if (token) return auth(req, res, next);
  next();
}, trackBatch);

module.exports = router;
