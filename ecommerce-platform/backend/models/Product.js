const mongoose = require('mongoose');

const productSchema = new mongoose.Schema({
  name: {
    type: String,
    required: true,
    trim: true
  },
  description: {
    type: String,
    required: true
  },
  price: {
    type: Number,
    required: true,
    min: 0
  },
  compareAtPrice: {
    type: Number,
    min: 0
  },
  category: {
    type: String,
    required: true,
    enum: ['electronics', 'clothing', 'home', 'beauty', 'sports', 'books']
  },
  tags: [String],
  sku: {
    type: String,
    required: true,
    unique: true
  },
  inventory: {
    type: Number,
    required: true,
    default: 0,
    min: 0
  },
  images: [String],
  isActive: {
    type: Boolean,
    default: true
  },
  viewCount: {
    type: Number,
    default: 0
  },
  addToCartCount: {
    type: Number,
    default: 0
  },
  purchaseCount: {
    type: Number,
    default: 0
  }
}, { timestamps: true });

productSchema.virtual('conversionRate').get(function () {
  if (this.viewCount === 0) return 0;
  return ((this.purchaseCount / this.viewCount) * 100).toFixed(2);
});

productSchema.virtual('cartRate').get(function () {
  if (this.viewCount === 0) return 0;
  return ((this.addToCartCount / this.viewCount) * 100).toFixed(2);
});

productSchema.set('toJSON', { virtuals: true });

module.exports = mongoose.model('Product', productSchema);
