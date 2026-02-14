require('dotenv').config({ path: require('path').join(__dirname, '..', '.env') });
const mongoose = require('mongoose');
const bcrypt = require('bcryptjs');
const User = require('../models/User');
const Product = require('../models/Product');
const Order = require('../models/Order');
const Cart = require('../models/Cart');
const BehaviorEvent = require('../models/BehaviorEvent');

const CHANNELS = ['organic', 'paid_search', 'social', 'email', 'referral', 'direct'];
const DEVICES = ['desktop', 'mobile', 'tablet'];

const products = [
  { name: 'Wireless Bluetooth Headphones', description: 'Premium noise-cancelling headphones with 30hr battery', price: 89.99, compareAtPrice: 129.99, category: 'electronics', sku: 'ELEC-001', inventory: 150, tags: ['audio', 'wireless', 'bluetooth'] },
  { name: 'Smart Fitness Watch', description: 'Track heart rate, steps, and sleep with GPS', price: 199.99, category: 'electronics', sku: 'ELEC-002', inventory: 80, tags: ['fitness', 'wearable', 'smart'] },
  { name: 'USB-C Laptop Hub 7-in-1', description: 'HDMI, USB 3.0, SD card reader, ethernet', price: 49.99, compareAtPrice: 69.99, category: 'electronics', sku: 'ELEC-003', inventory: 200, tags: ['accessories', 'usb-c', 'hub'] },
  { name: 'Mechanical Keyboard RGB', description: 'Cherry MX switches, per-key RGB backlighting', price: 129.99, category: 'electronics', sku: 'ELEC-004', inventory: 60, tags: ['keyboard', 'gaming', 'mechanical'] },
  { name: '4K Webcam Pro', description: 'Ultra HD webcam with auto-focus and noise reduction mic', price: 79.99, category: 'electronics', sku: 'ELEC-005', inventory: 100, tags: ['webcam', 'streaming', '4k'] },
  { name: 'Organic Cotton T-Shirt', description: 'Soft, sustainable everyday tee', price: 29.99, category: 'clothing', sku: 'CLTH-001', inventory: 300, tags: ['organic', 'cotton', 'basic'] },
  { name: 'Slim Fit Chinos', description: 'Stretch cotton chinos for everyday wear', price: 59.99, category: 'clothing', sku: 'CLTH-002', inventory: 200, tags: ['pants', 'chinos', 'casual'] },
  { name: 'Merino Wool Sweater', description: 'Lightweight merino wool crew neck', price: 89.99, compareAtPrice: 119.99, category: 'clothing', sku: 'CLTH-003', inventory: 120, tags: ['wool', 'sweater', 'premium'] },
  { name: 'Running Jacket Waterproof', description: 'Breathable, waterproof shell for all weather', price: 149.99, category: 'clothing', sku: 'CLTH-004', inventory: 75, tags: ['running', 'waterproof', 'outerwear'] },
  { name: 'Ceramic Pour-Over Coffee Set', description: 'Handmade ceramic dripper with carafe', price: 44.99, category: 'home', sku: 'HOME-001', inventory: 90, tags: ['coffee', 'ceramic', 'kitchen'] },
  { name: 'Bamboo Desk Organizer', description: 'Multi-compartment organizer for workspace', price: 34.99, category: 'home', sku: 'HOME-002', inventory: 160, tags: ['desk', 'bamboo', 'organizer'] },
  { name: 'Scented Soy Candle Set (3-Pack)', description: 'Lavender, vanilla, and cedarwood', price: 24.99, category: 'home', sku: 'HOME-003', inventory: 250, tags: ['candles', 'soy', 'scented'] },
  { name: 'Vitamin C Brightening Serum', description: '20% vitamin C with hyaluronic acid', price: 38.99, category: 'beauty', sku: 'BEAU-001', inventory: 180, tags: ['skincare', 'serum', 'vitamin-c'] },
  { name: 'Natural Lip Balm Pack (5)', description: 'Beeswax lip balm in assorted flavors', price: 14.99, category: 'beauty', sku: 'BEAU-002', inventory: 400, tags: ['lips', 'natural', 'balm'] },
  { name: 'Yoga Mat Premium 6mm', description: 'Non-slip, eco-friendly TPE material', price: 39.99, category: 'sports', sku: 'SPRT-001', inventory: 140, tags: ['yoga', 'mat', 'fitness'] },
  { name: 'Resistance Bands Set (5)', description: 'Latex-free bands with varying resistance', price: 19.99, category: 'sports', sku: 'SPRT-002', inventory: 220, tags: ['fitness', 'bands', 'resistance'] },
  { name: 'Stainless Steel Water Bottle', description: 'Double-wall insulated, 32oz', price: 27.99, category: 'sports', sku: 'SPRT-003', inventory: 300, tags: ['bottle', 'insulated', 'hydration'] },
  { name: 'Data Science from Scratch', description: 'First principles with Python - Joel Grus', price: 39.99, category: 'books', sku: 'BOOK-001', inventory: 50, tags: ['python', 'data-science', 'programming'] },
  { name: 'Designing Data-Intensive Apps', description: 'Martin Kleppmann — distributed systems', price: 44.99, category: 'books', sku: 'BOOK-002', inventory: 40, tags: ['data', 'systems', 'architecture'] },
  { name: 'The Lean Startup', description: 'Eric Ries — build, measure, learn', price: 16.99, category: 'books', sku: 'BOOK-003', inventory: 100, tags: ['business', 'startup', 'lean'] }
];

async function seed(alreadyConnected = false) {
  try {
    if (!alreadyConnected) {
      await mongoose.connect(process.env.MONGODB_URI);
      console.log('Connected to MongoDB');
    }

    // wipe everything first
    await Promise.all([
      User.deleteMany({}),
      Product.deleteMany({}),
      Order.deleteMany({}),
      Cart.deleteMany({}),
      BehaviorEvent.deleteMany({})
    ]);
    console.log('Cleared existing data');

    // admin account
    const admin = await User.create({
      email: 'admin@ecommerce.com',
      password: 'admin123',
      name: 'Admin User',
      role: 'admin',
      acquisitionChannel: 'direct',
      firstSeenAt: new Date('2024-01-01')
    });
    console.log('Admin created: admin@ecommerce.com / admin123');

    // make a bunch of fake customers
    const customerData = [];
    for (let i = 1; i <= 50; i++) {
      const monthOffset = Math.floor(Math.random() * 6);
      const dayOffset = Math.floor(Math.random() * 28);
      const firstSeen = new Date(2024, monthOffset, dayOffset + 1);

      customerData.push({
        email: `customer${i}@test.com`,
        password: 'password123',
        name: `Customer ${i}`,
        role: 'customer',
        acquisitionChannel: CHANNELS[Math.floor(Math.random() * CHANNELS.length)],
        firstSeenAt: firstSeen,
        lastActiveAt: new Date(firstSeen.getTime() + Math.random() * 180 * 24 * 60 * 60 * 1000)
      });
    }
    const customers = await User.create(customerData);
    console.log(`Created ${customers.length} customers`);

    const createdProducts = await Product.create(products);
    console.log(`Created ${createdProducts.length} products`);

    // generate fake behavior events + orders
    const events = [];
    const orders = [];
    const now = new Date();

    for (const customer of customers) {
      const sessionCount = 2 + Math.floor(Math.random() * 8);

      for (let s = 0; s < sessionCount; s++) {
        const sessionDate = new Date(
          customer.firstSeenAt.getTime() +
          Math.random() * (now - customer.firstSeenAt)
        );
        const sessionId = `sess_${customer._id}_${s}`;
        const channel = Math.random() < 0.6 ? customer.acquisitionChannel : CHANNELS[Math.floor(Math.random() * CHANNELS.length)];
        const device = DEVICES[Math.floor(Math.random() * DEVICES.length)];

        // page view
        events.push({
          user: customer._id,
          sessionId,
          eventType: 'page_view',
          metadata: { page: '/' },
          attributionChannel: channel,
          deviceType: device,
          timestamp: sessionDate
        });

        // browse some products
        const browseCount = 2 + Math.floor(Math.random() * 5);
        const viewedProducts = [];
        for (let v = 0; v < browseCount; v++) {
          const prod = createdProducts[Math.floor(Math.random() * createdProducts.length)];
          viewedProducts.push(prod);

          events.push({
            user: customer._id,
            sessionId,
            eventType: 'product_view',
            product: prod._id,
            metadata: {
              page: `/product/${prod._id}`,
              category: prod.category,
              timeOnPage: 5 + Math.floor(Math.random() * 120)
            },
            attributionChannel: channel,
            deviceType: device,
            timestamp: new Date(sessionDate.getTime() + v * 30000)
          });
        }

        // maybe add some to cart (40% chance each)
        const cartProducts = viewedProducts.filter(() => Math.random() < 0.4);
        for (const prod of cartProducts) {
          events.push({
            user: customer._id,
            sessionId,
            eventType: 'add_to_cart',
            product: prod._id,
            metadata: { quantity: 1 + Math.floor(Math.random() * 3) },
            attributionChannel: channel,
            deviceType: device,
            timestamp: new Date(sessionDate.getTime() + 300000)
          });
        }

        // checkout (60% of sessions with cart items)
        if (cartProducts.length > 0 && Math.random() < 0.6) {
          events.push({
            user: customer._id,
            sessionId,
            eventType: 'checkout_start',
            metadata: { cartValue: cartProducts.reduce((s, p) => s + p.price, 0) },
            attributionChannel: channel,
            deviceType: device,
            timestamp: new Date(sessionDate.getTime() + 600000)
          });

          // 30% abandon
          if (Math.random() < 0.3) {
            events.push({
              user: customer._id,
              sessionId,
              eventType: 'checkout_abandon',
              attributionChannel: channel,
              deviceType: device,
              timestamp: new Date(sessionDate.getTime() + 900000)
            });
          } else {
            // complete the order
            const items = cartProducts.map(p => ({
              product: p._id,
              name: p.name,
              price: p.price,
              quantity: 1 + Math.floor(Math.random() * 2)
            }));

            const subtotal = items.reduce((s, i) => s + i.price * i.quantity, 0);
            const tax = Math.round(subtotal * 0.08 * 100) / 100;
            const shipping = subtotal > 50 ? 0 : 9.99;
            const total = Math.round((subtotal + tax + shipping) * 100) / 100;

            events.push({
              user: customer._id,
              sessionId,
              eventType: 'checkout_complete',
              metadata: { orderTotal: total },
              attributionChannel: channel,
              deviceType: device,
              timestamp: new Date(sessionDate.getTime() + 1200000)
            });

            orders.push({
              user: customer._id,
              items,
              subtotal: Math.round(subtotal * 100) / 100,
              tax,
              shipping,
              total,
              status: ['pending', 'processing', 'shipped', 'delivered'][Math.floor(Math.random() * 4)],
              shippingAddress: {
                street: `${100 + Math.floor(Math.random() * 9900)} Main St`,
                city: ['Austin', 'Portland', 'Denver', 'Chicago', 'Seattle'][Math.floor(Math.random() * 5)],
                state: ['TX', 'OR', 'CO', 'IL', 'WA'][Math.floor(Math.random() * 5)],
                zip: `${10000 + Math.floor(Math.random() * 89999)}`,
                country: 'US'
              },
              paymentMethod: ['credit_card', 'debit_card', 'paypal'][Math.floor(Math.random() * 3)],
              attributionChannel: channel,
              sessionId,
              completedAt: new Date(sessionDate.getTime() + 1200000),
              createdAt: new Date(sessionDate.getTime() + 1200000)
            });
          }
        }
      }
    }

    // insert events in batches
    const BATCH_SIZE = 500;
    for (let i = 0; i < events.length; i += BATCH_SIZE) {
      await BehaviorEvent.insertMany(events.slice(i, i + BATCH_SIZE));
    }
    console.log(`Created ${events.length} behavior events`);

    if (orders.length > 0) {
      await Order.insertMany(orders);
    }
    console.log(`Created ${orders.length} orders`);

    // update product view/cart/purchase counters
    for (const product of createdProducts) {
      const views = events.filter(e => e.eventType === 'product_view' && e.product?.toString() === product._id.toString()).length;
      const carts = events.filter(e => e.eventType === 'add_to_cart' && e.product?.toString() === product._id.toString()).length;
      const purchases = orders.reduce((sum, o) => {
        const item = o.items.find(i => i.product.toString() === product._id.toString());
        return sum + (item ? item.quantity : 0);
      }, 0);

      await Product.findByIdAndUpdate(product._id, {
        viewCount: views,
        addToCartCount: carts,
        purchaseCount: purchases
      });
    }
    console.log('Updated product analytics counters');

    console.log('\nSeed done!');
    console.log(`Users: ${customers.length + 1}`);
    console.log(`Products: ${createdProducts.length}`);
    console.log(`Events: ${events.length}`);
    console.log(`Orders: ${orders.length}`);

    if (!alreadyConnected) {
      await mongoose.connection.close();
      process.exit(0);
    }
  } catch (err) {
    console.error('Seed error:', err);
    if (!alreadyConnected) process.exit(1);
  }
}

module.exports = seed;

// run directly: node seed.js
if (require.main === module) {
  seed(false);
}
