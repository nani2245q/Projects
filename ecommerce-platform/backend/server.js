require('dotenv').config();
const express = require('express');
const cors = require('cors');
const morgan = require('morgan');
const path = require('path');
const connectDB = require('./config/db');
const Product = require('./models/Product');

const app = express();

// connect to db then auto-seed if empty or data is stale
connectDB().then(async () => {
  try {
    const count = await Product.countDocuments();
    let needsSeed = count === 0;

    // also reseed if all data is older than 90 days (stale dates)
    if (!needsSeed) {
      const Order = require('./models/Order');
      const recent = await Order.findOne({
        createdAt: { $gte: new Date(Date.now() - 90 * 24 * 60 * 60 * 1000) }
      });
      if (!recent) {
        console.log('Data is stale (no recent orders) — re-seeding...');
        needsSeed = true;
      }
    }

    if (needsSeed) {
      console.log('Running auto-seed...');
      const seed = require('./seeds/seed');
      await seed(true);
      console.log('Auto-seed complete!');
    }
  } catch (err) {
    console.error('Auto-seed check failed:', err.message);
  }
});

// middleware
app.use(cors());
app.use(express.json());
app.use(morgan('dev'));

// serve frontend
app.use(express.static(path.join(__dirname, '..', 'frontend')));

// routes
app.use('/api/auth', require('./routes/auth'));
app.use('/api/products', require('./routes/products'));
app.use('/api/cart', require('./routes/cart'));
app.use('/api/orders', require('./routes/orders'));
app.use('/api/track', require('./routes/tracking'));
app.use('/api/analytics', require('./routes/analytics'));

app.get('/api/health', (req, res) => {
  res.json({ status: 'ok', timestamp: new Date().toISOString() });
});

// serve frontend for everything else
app.get('*', (req, res) => {
  res.sendFile(path.join(__dirname, '..', 'frontend', 'index.html'));
});

const PORT = process.env.PORT || 5000;
app.listen(PORT, () => {
  console.log(`Server running on port ${PORT}`);
  console.log(`Analytics dashboard: http://localhost:${PORT}/pages/analytics.html`);
});
