const BehaviorEvent = require('../models/BehaviorEvent');
const Order = require('../models/Order');
const User = require('../models/User');
const Product = require('../models/Product');

// get funnel data
exports.getConversionFunnel = async (req, res) => {
  try {
    const { startDate, endDate, channel } = req.query;
    const dateFilter = buildDateFilter(startDate, endDate);
    const matchStage = { timestamp: dateFilter };
    if (channel) matchStage.attributionChannel = channel;

    const funnelStages = [
      'page_view',
      'product_view',
      'add_to_cart',
      'checkout_start',
      'checkout_complete'
    ];

    const pipeline = [
      { $match: matchStage },
      {
        $group: {
          _id: '$eventType',
          uniqueUsers: { $addToSet: '$user' },
          uniqueSessions: { $addToSet: '$sessionId' },
          totalEvents: { $sum: 1 }
        }
      }
    ];

    const results = await BehaviorEvent.aggregate(pipeline);

    const funnel = funnelStages.map((stage, i) => {
      const data = results.find(r => r._id === stage) || {
        uniqueUsers: [],
        uniqueSessions: [],
        totalEvents: 0
      };
      const users = data.uniqueUsers.length;
      const prevUsers = i > 0
        ? (results.find(r => r._id === funnelStages[i - 1])?.uniqueUsers.length || 0)
        : users;

      return {
        stage,
        label: formatStageName(stage),
        uniqueUsers: users,
        uniqueSessions: data.uniqueSessions.length,
        totalEvents: data.totalEvents,
        dropOffRate: prevUsers > 0 ? (((prevUsers - users) / prevUsers) * 100).toFixed(2) : 0,
        conversionFromPrev: prevUsers > 0 ? ((users / prevUsers) * 100).toFixed(2) : 100
      };
    });

    const overallConversion = funnel[0].uniqueUsers > 0
      ? ((funnel[funnel.length - 1].uniqueUsers / funnel[0].uniqueUsers) * 100).toFixed(2)
      : 0;

    res.json({ funnel, overallConversionRate: overallConversion });
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
};

// revenue over time
exports.getRevenueMetrics = async (req, res) => {
  try {
    const { startDate, endDate, granularity = 'day' } = req.query;
    const dateFilter = buildDateFilter(startDate, endDate);

    const groupFormat = {
      day: { $dateToString: { format: '%Y-%m-%d', date: '$createdAt' } },
      week: { $dateToString: { format: '%Y-W%V', date: '$createdAt' } },
      month: { $dateToString: { format: '%Y-%m', date: '$createdAt' } }
    };

    const pipeline = [
      { $match: { createdAt: dateFilter, status: { $nin: ['cancelled', 'refunded'] } } },
      {
        $group: {
          _id: groupFormat[granularity] || groupFormat.day,
          revenue: { $sum: '$total' },
          orderCount: { $sum: 1 },
          avgOrderValue: { $avg: '$total' },
          uniqueCustomers: { $addToSet: '$user' }
        }
      },
      { $sort: { _id: 1 } },
      {
        $project: {
          period: '$_id',
          revenue: { $round: ['$revenue', 2] },
          orderCount: 1,
          avgOrderValue: { $round: ['$avgOrderValue', 2] },
          uniqueCustomers: { $size: '$uniqueCustomers' }
        }
      }
    ];

    const timeSeries = await Order.aggregate(pipeline);

    // also get overall summary
    const summaryPipeline = [
      { $match: { createdAt: dateFilter, status: { $nin: ['cancelled', 'refunded'] } } },
      {
        $group: {
          _id: null,
          totalRevenue: { $sum: '$total' },
          totalOrders: { $sum: 1 },
          avgOrderValue: { $avg: '$total' },
          uniqueCustomers: { $addToSet: '$user' }
        }
      }
    ];

    const [summary] = await Order.aggregate(summaryPipeline);

    res.json({
      summary: summary ? {
        totalRevenue: Math.round(summary.totalRevenue * 100) / 100,
        totalOrders: summary.totalOrders,
        avgOrderValue: Math.round(summary.avgOrderValue * 100) / 100,
        uniqueCustomers: summary.uniqueCustomers.length
      } : { totalRevenue: 0, totalOrders: 0, avgOrderValue: 0, uniqueCustomers: 0 },
      timeSeries
    });
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
};

// marketing attribution - which channels bring in money
exports.getAttributionReport = async (req, res) => {
  try {
    const { startDate, endDate } = req.query;
    const dateFilter = buildDateFilter(startDate, endDate);

    // revenue by channel
    const revenuePipeline = [
      { $match: { createdAt: dateFilter, status: { $nin: ['cancelled', 'refunded'] } } },
      {
        $group: {
          _id: '$attributionChannel',
          revenue: { $sum: '$total' },
          orders: { $sum: 1 },
          avgOrderValue: { $avg: '$total' },
          customers: { $addToSet: '$user' }
        }
      },
      {
        $project: {
          channel: '$_id',
          revenue: { $round: ['$revenue', 2] },
          orders: 1,
          avgOrderValue: { $round: ['$avgOrderValue', 2] },
          uniqueCustomers: { $size: '$customers' }
        }
      },
      { $sort: { revenue: -1 } }
    ];

    // traffic by channel
    const trafficPipeline = [
      { $match: { timestamp: dateFilter, eventType: 'page_view' } },
      {
        $group: {
          _id: '$attributionChannel',
          sessions: { $addToSet: '$sessionId' },
          pageViews: { $sum: 1 }
        }
      },
      {
        $project: {
          channel: '$_id',
          sessions: { $size: '$sessions' },
          pageViews: 1
        }
      }
    ];

    const [revenueByChannel, trafficByChannel] = await Promise.all([
      Order.aggregate(revenuePipeline),
      BehaviorEvent.aggregate(trafficPipeline)
    ]);

    // merge traffic + revenue
    const channels = ['organic', 'paid_search', 'social', 'email', 'referral', 'direct'];
    const attribution = channels.map(ch => {
      const rev = revenueByChannel.find(r => r.channel === ch) || { revenue: 0, orders: 0, avgOrderValue: 0, uniqueCustomers: 0 };
      const traffic = trafficByChannel.find(t => t.channel === ch) || { sessions: 0, pageViews: 0 };
      return {
        channel: ch,
        sessions: traffic.sessions,
        pageViews: traffic.pageViews,
        orders: rev.orders,
        revenue: rev.revenue,
        avgOrderValue: rev.avgOrderValue,
        conversionRate: traffic.sessions > 0 ? ((rev.orders / traffic.sessions) * 100).toFixed(2) : 0,
        revenuePerSession: traffic.sessions > 0 ? (rev.revenue / traffic.sessions).toFixed(2) : 0
      };
    });

    res.json({ attribution });
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
};

// cohort analysis stuff
exports.getCustomerCohorts = async (req, res) => {
  try {
    const { startDate, endDate } = req.query;
    const dateFilter = buildDateFilter(startDate, endDate);

    // group users by when they signed up
    const cohortPipeline = [
      {
        $group: {
          _id: { $dateToString: { format: '%Y-%m', date: '$firstSeenAt' } },
          users: { $push: '$_id' },
          count: { $sum: 1 }
        }
      },
      { $sort: { _id: 1 } }
    ];

    const cohorts = await User.aggregate(cohortPipeline);

    // for each cohort check their order activity
    const cohortData = await Promise.all(
      cohorts.map(async (cohort) => {
        const orderPipeline = [
          { $match: { user: { $in: cohort.users } } },
          {
            $group: {
              _id: { $dateToString: { format: '%Y-%m', date: '$createdAt' } },
              revenue: { $sum: '$total' },
              orders: { $sum: 1 },
              activeUsers: { $addToSet: '$user' }
            }
          },
          { $sort: { _id: 1 } }
        ];
        const activity = await Order.aggregate(orderPipeline);

        return {
          cohortMonth: cohort._id,
          totalUsers: cohort.count,
          activity: activity.map(a => ({
            month: a._id,
            revenue: Math.round(a.revenue * 100) / 100,
            orders: a.orders,
            activeUsers: a.activeUsers.length,
            retentionRate: ((a.activeUsers.length / cohort.count) * 100).toFixed(2)
          }))
        };
      })
    );

    res.json({ cohorts: cohortData });
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
};

// category performance breakdown
exports.getCategoryPerformance = async (req, res) => {
  try {
    const pipeline = [
      { $match: { isActive: true } },
      {
        $group: {
          _id: '$category',
          productCount: { $sum: 1 },
          totalViews: { $sum: '$viewCount' },
          totalAddToCarts: { $sum: '$addToCartCount' },
          totalPurchases: { $sum: '$purchaseCount' },
          avgPrice: { $avg: '$price' },
          totalRevenue: {
            $sum: { $multiply: ['$price', '$purchaseCount'] }
          }
        }
      },
      {
        $project: {
          category: '$_id',
          productCount: 1,
          totalViews: 1,
          totalAddToCarts: 1,
          totalPurchases: 1,
          avgPrice: { $round: ['$avgPrice', 2] },
          totalRevenue: { $round: ['$totalRevenue', 2] },
          viewToCartRate: {
            $cond: [
              { $gt: ['$totalViews', 0] },
              { $round: [{ $multiply: [{ $divide: ['$totalAddToCarts', '$totalViews'] }, 100] }, 2] },
              0
            ]
          },
          cartToPurchaseRate: {
            $cond: [
              { $gt: ['$totalAddToCarts', 0] },
              { $round: [{ $multiply: [{ $divide: ['$totalPurchases', '$totalAddToCarts'] }, 100] }, 2] },
              0
            ]
          }
        }
      },
      { $sort: { totalRevenue: -1 } }
    ];

    const categories = await Product.aggregate(pipeline);
    res.json({ categories });
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
};

// dashboard KPIs - main overview numbers
exports.getDashboardKPIs = async (req, res) => {
  try {
    const now = new Date();
    const today = new Date(now.getFullYear(), now.getMonth(), now.getDate());
    const last30 = new Date(now - 30 * 24 * 60 * 60 * 1000);
    const prev30 = new Date(now - 60 * 24 * 60 * 60 * 1000);

    const [
      todayOrders,
      last30Revenue,
      prev30Revenue,
      totalCustomers,
      last30Events,
      topProducts
    ] = await Promise.all([
      Order.countDocuments({ createdAt: { $gte: today } }),
      Order.aggregate([
        { $match: { createdAt: { $gte: last30 }, status: { $nin: ['cancelled', 'refunded'] } } },
        { $group: { _id: null, total: { $sum: '$total' }, count: { $sum: 1 }, avg: { $avg: '$total' } } }
      ]),
      Order.aggregate([
        { $match: { createdAt: { $gte: prev30, $lt: last30 }, status: { $nin: ['cancelled', 'refunded'] } } },
        { $group: { _id: null, total: { $sum: '$total' }, count: { $sum: 1 } } }
      ]),
      User.countDocuments({ role: 'customer' }),
      BehaviorEvent.countDocuments({ timestamp: { $gte: last30 } }),
      Product.find({ isActive: true }).sort({ purchaseCount: -1 }).limit(5).select('name category price purchaseCount viewCount')
    ]);

    const current = last30Revenue[0] || { total: 0, count: 0, avg: 0 };
    const previous = prev30Revenue[0] || { total: 0, count: 0 };

    const revenueGrowth = previous.total > 0
      ? (((current.total - previous.total) / previous.total) * 100).toFixed(2)
      : 0;

    res.json({
      kpis: {
        todayOrders,
        last30DaysRevenue: Math.round(current.total * 100) / 100,
        last30DaysOrders: current.count,
        avgOrderValue: Math.round(current.avg * 100) / 100 || 0,
        revenueGrowth: parseFloat(revenueGrowth),
        totalCustomers,
        last30DaysEvents: last30Events
      },
      topProducts
    });
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
};

// helper to build date range filter
function buildDateFilter(startDate, endDate) {
  const filter = {};
  if (startDate) filter.$gte = new Date(startDate);
  else filter.$gte = new Date(Date.now() - 90 * 24 * 60 * 60 * 1000); // default 90 days
  if (endDate) filter.$lte = new Date(endDate);
  else filter.$lte = new Date();
  return filter;
}

function formatStageName(stage) {
  const names = {
    page_view: 'Page View',
    product_view: 'Product View',
    add_to_cart: 'Add to Cart',
    checkout_start: 'Checkout Started',
    checkout_complete: 'Purchase Complete'
  };
  return names[stage] || stage;
}
