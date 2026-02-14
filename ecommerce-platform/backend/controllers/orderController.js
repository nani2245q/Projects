const Order = require('../models/Order');
const Cart = require('../models/Cart');
const Product = require('../models/Product');
const BehaviorEvent = require('../models/BehaviorEvent');

exports.createOrder = async (req, res) => {
  try {
    const { shippingAddress, paymentMethod } = req.body;
    const sessionId = req.headers['x-session-id'] || 'unknown';
    const attribution = req.headers['x-attribution'] || 'direct';

    const cart = await Cart.findOne({ user: req.user._id }).populate('items.product');
    if (!cart || cart.items.length === 0) {
      return res.status(400).json({ error: 'Cart is empty' });
    }

    // log checkout start event
    await BehaviorEvent.create({
      user: req.user._id,
      sessionId,
      eventType: 'checkout_start',
      metadata: { cartValue: cart.items.reduce((sum, i) => sum + i.product.price * i.quantity, 0) },
      attributionChannel: attribution
    });

    const items = cart.items.map(item => ({
      product: item.product._id,
      name: item.product.name,
      price: item.product.price,
      quantity: item.quantity
    }));

    const subtotal = items.reduce((sum, item) => sum + item.price * item.quantity, 0);
    const tax = Math.round(subtotal * 0.08 * 100) / 100;
    const shipping = subtotal > 50 ? 0 : 9.99; // free shipping over $50
    const total = Math.round((subtotal + tax + shipping) * 100) / 100;

    const order = await Order.create({
      user: req.user._id,
      items,
      subtotal,
      tax,
      shipping,
      total,
      shippingAddress,
      paymentMethod,
      attributionChannel: attribution,
      sessionId,
      completedAt: new Date()
    });

    // update purchase counts
    for (const item of cart.items) {
      await Product.findByIdAndUpdate(item.product._id, {
        $inc: { purchaseCount: item.quantity }
      });
    }

    // log checkout complete
    await BehaviorEvent.create({
      user: req.user._id,
      sessionId,
      eventType: 'checkout_complete',
      metadata: { orderTotal: total, orderId: order._id },
      attributionChannel: attribution
    });

    // empty the cart
    cart.items = [];
    await cart.save();

    res.status(201).json({ order });
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
};

// get orders for current user
exports.getOrders = async (req, res) => {
  try {
    const orders = await Order.find({ user: req.user._id })
      .sort({ createdAt: -1 })
      .populate('items.product', 'name images');
    res.json({ orders });
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
};

exports.getOrder = async (req, res) => {
  try {
    const order = await Order.findOne({
      _id: req.params.id,
      user: req.user._id
    }).populate('items.product', 'name images');
    if (!order) return res.status(404).json({ error: 'Order not found' });
    res.json({ order });
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
};

// admin - get all orders with pagination
exports.getAllOrders = async (req, res) => {
  try {
    const { page = 1, limit = 20, status } = req.query;
    const filter = {};
    if (status) filter.status = status;

    const [orders, total] = await Promise.all([
      Order.find(filter)
        .sort({ createdAt: -1 })
        .skip((page - 1) * limit)
        .limit(parseInt(limit))
        .populate('user', 'name email'),
      Order.countDocuments(filter)
    ]);

    res.json({ orders, pagination: { page: parseInt(page), total, pages: Math.ceil(total / limit) } });
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
};
