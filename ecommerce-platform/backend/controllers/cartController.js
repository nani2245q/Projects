const Cart = require('../models/Cart');
const Product = require('../models/Product');
const BehaviorEvent = require('../models/BehaviorEvent');

exports.getCart = async (req, res) => {
  try {
    let cart = await Cart.findOne({ user: req.user._id }).populate('items.product');
    if (!cart) {
      cart = await Cart.create({ user: req.user._id, items: [] });
    }
    res.json({ cart });
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
};

exports.addToCart = async (req, res) => {
  try {
    const { productId, quantity = 1 } = req.body;

    const product = await Product.findById(productId);
    if (!product) return res.status(404).json({ error: 'Product not found' });

    let cart = await Cart.findOne({ user: req.user._id });
    if (!cart) {
      cart = new Cart({ user: req.user._id, items: [] });
    }

    // check if item already in cart
    const existing = cart.items.find(
      item => item.product.toString() === productId
    );

    if (existing) {
      existing.quantity += quantity;
    } else {
      cart.items.push({ product: productId, quantity });
    }

    await cart.save();

    // bump analytics counter
    product.addToCartCount += 1;
    await product.save();

    // track event
    await BehaviorEvent.create({
      user: req.user._id,
      sessionId: req.headers['x-session-id'] || 'unknown',
      eventType: 'add_to_cart',
      product: productId,
      metadata: {
        quantity,
        cartValue: cart.items.length
      },
      attributionChannel: req.headers['x-attribution'] || 'direct',
      deviceType: req.headers['x-device-type'] || 'desktop'
    });

    cart = await cart.populate('items.product');
    res.json({ cart });
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
};

exports.removeFromCart = async (req, res) => {
  try {
    const { productId } = req.params;
    const cart = await Cart.findOne({ user: req.user._id });

    if (!cart) return res.status(404).json({ error: 'Cart not found' });

    cart.items = cart.items.filter(
      item => item.product.toString() !== productId
    );
    await cart.save();

    await BehaviorEvent.create({
      user: req.user._id,
      sessionId: req.headers['x-session-id'] || 'unknown',
      eventType: 'remove_from_cart',
      product: productId,
      attributionChannel: req.headers['x-attribution'] || 'direct'
    });

    await cart.populate('items.product');
    res.json({ cart });
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
};

exports.clearCart = async (req, res) => {
  try {
    const cart = await Cart.findOne({ user: req.user._id });
    if (cart) {
      cart.items = [];
      await cart.save();
    }
    res.json({ message: 'Cart cleared' });
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
};
