const express = require('express');
const router = express.Router();
const { createOrder, getOrders, getOrder, getAllOrders } = require('../controllers/orderController');
const { auth, adminAuth } = require('../middleware/auth');

router.post('/', auth, createOrder);
router.get('/', auth, getOrders);
router.get('/all', adminAuth, getAllOrders);
router.get('/:id', auth, getOrder);

module.exports = router;
