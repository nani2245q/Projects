const express = require('express');
const router = express.Router();
const {
  getConversionFunnel,
  getRevenueMetrics,
  getAttributionReport,
  getCustomerCohorts,
  getCategoryPerformance,
  getDashboardKPIs
} = require('../controllers/analyticsController');
const { adminAuth } = require('../middleware/auth');

router.get('/dashboard', adminAuth, getDashboardKPIs);
router.get('/funnel', adminAuth, getConversionFunnel);
router.get('/revenue', adminAuth, getRevenueMetrics);
router.get('/attribution', adminAuth, getAttributionReport);
router.get('/cohorts', adminAuth, getCustomerCohorts);
router.get('/categories', adminAuth, getCategoryPerformance);

module.exports = router;
