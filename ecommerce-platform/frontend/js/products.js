const CATEGORY_ICONS = {
  electronics: '💻',
  clothing: '👕',
  home: '🏠',
  beauty: '✨',
  sports: '🏃',
  books: '📚'
};

let currentProducts = [];

async function loadProducts() {
  const category = document.getElementById('category-filter').value;
  const sort = document.getElementById('sort-filter').value;
  const search = document.getElementById('search-input').value;

  const params = new URLSearchParams();
  if (category) params.set('category', category);
  if (sort) params.set('sort', sort);
  if (search) params.set('search', search);

  try {
    const res = await fetch(`${API_BASE}/products?${params}`);
    const data = await res.json();
    currentProducts = data.products;
    renderProducts(data.products);

    if (search) {
      Tracker.track('product_search', { metadata: { searchQuery: search } });
    }
  } catch (err) {
    console.error('Failed to load products:', err);
  }
}

function renderProducts(products) {
  const grid = document.getElementById('product-grid');
  grid.innerHTML = products.map(p => `
    <div class="product-card" onclick="viewProduct('${p._id}', '${p.category}')">
      <div class="product-img">${CATEGORY_ICONS[p.category] || '📦'}</div>
      <div class="product-info">
        <div class="product-category">${p.category}</div>
        <div class="product-name">${p.name}</div>
        <div class="product-price">
          $${p.price.toFixed(2)}
          ${p.compareAtPrice ? `<span class="compare-price">$${p.compareAtPrice.toFixed(2)}</span>` : ''}
        </div>
        <button class="btn btn-primary btn-sm btn-block" onclick="event.stopPropagation(); addToCart('${p._id}')">
          Add to Cart
        </button>
      </div>
    </div>
  `).join('');
}

function viewProduct(productId, category) {
  Tracker.trackProductView(productId, category);
  // In a full app, this would navigate to a product detail page
}

async function addToCart(productId) {
  const token = getToken();
  if (!token) {
    window.location.href = '/pages/login.html';
    return;
  }

  try {
    const res = await fetch(`${API_BASE}/cart/add`, {
      method: 'POST',
      headers: authHeaders(),
      body: JSON.stringify({ productId, quantity: 1 })
    });

    if (res.ok) {
      const data = await res.json();
      updateCartBadge(data.cart.items.length);
      Tracker.trackAddToCart(productId, 1);
    }
  } catch (err) {
    console.error('Add to cart failed:', err);
  }
}

function updateCartBadge(count) {
  const badge = document.getElementById('cart-count');
  if (badge) badge.textContent = count;
}

async function loadCartCount() {
  const token = getToken();
  if (!token) return;

  try {
    const res = await fetch(`${API_BASE}/cart`, { headers: authHeaders() });
    if (res.ok) {
      const data = await res.json();
      updateCartBadge(data.cart.items.length);
    }
  } catch (err) {
    // ignore
  }
}

// Debounce search
let searchTimeout;
document.getElementById('search-input')?.addEventListener('input', () => {
  clearTimeout(searchTimeout);
  searchTimeout = setTimeout(loadProducts, 300);
});

document.getElementById('category-filter')?.addEventListener('change', loadProducts);
document.getElementById('sort-filter')?.addEventListener('change', loadProducts);

document.addEventListener('DOMContentLoaded', () => {
  loadProducts();
  loadCartCount();
});
