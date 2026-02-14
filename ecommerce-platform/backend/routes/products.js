const express = require('express');
const router = express.Router();
const { getProducts, getProduct, createProduct, updateProduct, getProductAnalytics } = require('../controllers/productController');
const { auth, adminAuth } = require('../middleware/auth');

router.get('/', getProducts);
router.get('/analytics', adminAuth, getProductAnalytics);
router.get('/:id', getProduct);
router.post('/', adminAuth, createProduct);
router.put('/:id', adminAuth, updateProduct);

module.exports = router;
