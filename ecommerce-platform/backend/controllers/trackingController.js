const BehaviorEvent = require('../models/BehaviorEvent');
const Product = require('../models/Product');

// track a single user event
exports.trackEvent = async (req, res) => {
  try {
    const { eventType, productId, metadata, sessionId } = req.body;

    const event = await BehaviorEvent.create({
      user: req.user?._id,
      sessionId: sessionId || req.headers['x-session-id'] || 'unknown',
      eventType,
      product: productId || undefined,
      metadata: metadata || {},
      attributionChannel: req.headers['x-attribution'] || 'direct',
      deviceType: req.headers['x-device-type'] || 'desktop',
      timestamp: new Date()
    });

    // bump view count if its a product view
    if (eventType === 'product_view' && productId) {
      await Product.findByIdAndUpdate(productId, { $inc: { viewCount: 1 } });
    }

    res.status(201).json({ event: { id: event._id, eventType: event.eventType } });
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
};

// batch track multiple events at once
exports.trackBatch = async (req, res) => {
  try {
    const { events } = req.body;

    const enriched = events.map(e => ({
      ...e,
      user: req.user?._id,
      sessionId: e.sessionId || req.headers['x-session-id'] || 'unknown',
      attributionChannel: req.headers['x-attribution'] || 'direct',
      deviceType: req.headers['x-device-type'] || 'desktop',
      timestamp: e.timestamp || new Date()
    }));

    const created = await BehaviorEvent.insertMany(enriched);
    res.status(201).json({ count: created.length });
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
};
