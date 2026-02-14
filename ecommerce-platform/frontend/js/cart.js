async function loadCart() {
  const token = getToken();
  if (!token) {
    window.location.href = '/pages/login.html';
    return;
  }

  try {
    const res = await fetch(`${API_BASE}/cart`, { headers: authHeaders() });
    const data = await res.json();
    renderCart(data.cart);

    Tracker.track('cart_view', {
      metadata: { cartValue: data.cart.items.length }
    });
  } catch (err) {
    console.error('Failed to load cart:', err);
  }
}

function renderCart(cart) {
  const itemsContainer = document.getElementById('cart-items');
  const emptyMsg = document.getElementById('cart-empty');
  const summary = document.getElementById('cart-summary');

  if (!cart.items || cart.items.length === 0) {
    emptyMsg.classList.remove('hidden');
    summary.classList.add('hidden');
    itemsContainer.innerHTML = '';
    updateCartBadge(0);
    return;
  }

  emptyMsg.classList.add('hidden');
  summary.classList.remove('hidden');
  updateCartBadge(cart.items.length);

  itemsContainer.innerHTML = cart.items.map(item => `
    <div class="cart-item">
      <div class="item-details">
        <div class="item-name">${item.product.name}</div>
        <div style="color: var(--gray-500); font-size: 0.85rem;">${item.product.category}</div>
        <div class="item-price">$${item.product.price.toFixed(2)} x ${item.quantity}</div>
      </div>
      <button class="btn btn-danger btn-sm" onclick="removeFromCart('${item.product._id}')">Remove</button>
    </div>
  `).join('');

  const subtotal = cart.items.reduce((s, i) => s + i.product.price * i.quantity, 0);
  const tax = Math.round(subtotal * 0.08 * 100) / 100;
  const shipping = subtotal > 50 ? 0 : 9.99;
  const total = Math.round((subtotal + tax + shipping) * 100) / 100;

  document.getElementById('subtotal').textContent = `$${subtotal.toFixed(2)}`;
  document.getElementById('tax').textContent = `$${tax.toFixed(2)}`;
  document.getElementById('shipping').textContent = shipping === 0 ? 'Free' : `$${shipping.toFixed(2)}`;
  document.getElementById('total').textContent = `$${total.toFixed(2)}`;
}

async function removeFromCart(productId) {
  try {
    const res = await fetch(`${API_BASE}/cart/item/${productId}`, {
      method: 'DELETE',
      headers: authHeaders()
    });
    if (res.ok) {
      const data = await res.json();
      renderCart(data.cart);
      Tracker.trackRemoveFromCart(productId);
    }
  } catch (err) {
    console.error('Remove failed:', err);
  }
}

async function checkout() {
  const subtotalText = document.getElementById('subtotal').textContent;
  const cartValue = parseFloat(subtotalText.replace('$', ''));
  Tracker.trackCheckoutStart(cartValue);

  try {
    const res = await fetch(`${API_BASE}/orders`, {
      method: 'POST',
      headers: authHeaders(),
      body: JSON.stringify({
        shippingAddress: {
          street: '123 Main St',
          city: 'Austin',
          state: 'TX',
          zip: '73301',
          country: 'US'
        },
        paymentMethod: 'credit_card'
      })
    });

    if (res.ok) {
      const data = await res.json();
      Tracker.trackCheckoutComplete(data.order.total, data.order._id);

      document.getElementById('cart-items').innerHTML = `
        <div class="alert alert-success">
          Order placed successfully! Order total: $${data.order.total.toFixed(2)}
        </div>
      `;
      document.getElementById('cart-summary').classList.add('hidden');
      updateCartBadge(0);
    } else {
      const err = await res.json();
      alert(err.error || 'Checkout failed');
    }
  } catch (err) {
    console.error('Checkout error:', err);
  }
}

function updateCartBadge(count) {
  const badge = document.getElementById('cart-count');
  if (badge) badge.textContent = count;
}

document.addEventListener('DOMContentLoaded', loadCart);
