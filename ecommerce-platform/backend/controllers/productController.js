const Product = require('../models/Product');
const BehaviorEvent = require('../models/BehaviorEvent');

exports.getProducts = async (req, res) => {
  try {
    const { category, search, sort, page = 1, limit = 12 } = req.query;
    const filter = { isActive: true };

    if (category) filter.category = category;
    if (search) filter.name = { $regex: search, $options: 'i' };

    let sortOption = { createdAt: -1 };
    if (sort === 'price_asc') sortOption = { price: 1 };
    if (sort === 'price_desc') sortOption = { price: -1 };
    if (sort === 'popular') sortOption = { viewCount: -1 };

    const skip = (parseInt(page) - 1) * parseInt(limit);

    const [products, total] = await Promise.all([
      Product.find(filter).sort(sortOption).skip(skip).limit(parseInt(limit)),
      Product.countDocuments(filter)
    ]);

    res.json({
      products,
      pagination: {
        page: parseInt(page),
        limit: parseInt(limit),
        total,
        pages: Math.ceil(total / parseInt(limit))
      }
    });
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
};

exports.getProduct = async (req, res) => {
  try {
    const product = await Product.findById(req.params.id);
    if (!product) return res.status(404).json({ error: 'Product not found' });

    // Increment view count
    product.viewCount += 1;
    await product.save();

    res.json({ product });
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
};

exports.createProduct = async (req, res) => {
  try {
    const product = await Product.create(req.body);
    res.status(201).json({ product });
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
};

exports.updateProduct = async (req, res) => {
  try {
    const product = await Product.findByIdAndUpdate(req.params.id, req.body, {
      new: true,
      runValidators: true
    });
    if (!product) return res.status(404).json({ error: 'Product not found' });
    res.json({ product });
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
};

exports.getProductAnalytics = async (req, res) => {
  try {
    const products = await Product.find({ isActive: true })
      .sort({ viewCount: -1 })
      .limit(20)
      .select('name category price viewCount addToCartCount purchaseCount');

    const analytics = products.map(p => ({
      id: p._id,
      name: p.name,
      category: p.category,
      price: p.price,
      views: p.viewCount,
      addToCarts: p.addToCartCount,
      purchases: p.purchaseCount,
      viewToCartRate: p.viewCount > 0 ? ((p.addToCartCount / p.viewCount) * 100).toFixed(2) : 0,
      cartToPurchaseRate: p.addToCartCount > 0 ? ((p.purchaseCount / p.addToCartCount) * 100).toFixed(2) : 0,
      overallConversion: p.viewCount > 0 ? ((p.purchaseCount / p.viewCount) * 100).toFixed(2) : 0
    }));

    res.json({ analytics });
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
};
