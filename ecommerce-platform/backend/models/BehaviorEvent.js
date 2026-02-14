const mongoose = require('mongoose');

const behaviorEventSchema = new mongoose.Schema({
  user: {
    type: mongoose.Schema.Types.ObjectId,
    ref: 'User'
  },
  sessionId: {
    type: String,
    required: true,
    index: true
  },
  eventType: {
    type: String,
    required: true,
    enum: [
      'page_view',
      'product_view',
      'product_search',
      'add_to_cart',
      'remove_from_cart',
      'cart_view',
      'checkout_start',
      'checkout_shipping',
      'checkout_payment',
      'checkout_complete',
      'checkout_abandon'
    ],
    index: true
  },
  product: {
    type: mongoose.Schema.Types.ObjectId,
    ref: 'Product'
  },
  metadata: {
    page: String,
    referrer: String,
    searchQuery: String,
    category: String,
    quantity: Number,
    cartValue: Number,
    orderTotal: Number,
    orderId: mongoose.Schema.Types.ObjectId,
    timeOnPage: Number,
    scrollDepth: Number
  },
  attributionChannel: {
    type: String,
    enum: ['organic', 'paid_search', 'social', 'email', 'referral', 'direct'],
    default: 'direct'
  },
  deviceType: {
    type: String,
    enum: ['desktop', 'mobile', 'tablet'],
    default: 'desktop'
  },
  timestamp: {
    type: Date,
    default: Date.now,
    index: true
  }
}, { timestamps: true });

behaviorEventSchema.index({ eventType: 1, timestamp: -1 });
behaviorEventSchema.index({ sessionId: 1, timestamp: 1 });
behaviorEventSchema.index({ user: 1, eventType: 1 });

module.exports = mongoose.model('BehaviorEvent', behaviorEventSchema);
