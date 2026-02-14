// ─── Client-Side Behavior Tracking ──────────────────────────────────
// Tracks user interactions and sends them to the analytics backend

const Tracker = {
  queue: [],
  flushInterval: null,

  init() {
    // Flush event queue every 5 seconds
    this.flushInterval = setInterval(() => this.flush(), 5000);

    // Flush on page unload
    window.addEventListener('beforeunload', () => this.flush());

    // Track initial page view
    this.trackPageView();
  },

  track(eventType, data = {}) {
    this.queue.push({
      eventType,
      productId: data.productId || undefined,
      sessionId: sessionStorage.getItem('sessionId'),
      metadata: data.metadata || {},
      timestamp: new Date().toISOString()
    });

    // Flush immediately for important events
    if (['checkout_start', 'checkout_complete', 'add_to_cart'].includes(eventType)) {
      this.flush();
    }
  },

  trackPageView() {
    this.track('page_view', {
      metadata: {
        page: window.location.pathname,
        referrer: document.referrer
      }
    });
  },

  trackProductView(productId, category) {
    this.track('product_view', {
      productId,
      metadata: { category, page: window.location.pathname }
    });
  },

  trackAddToCart(productId, quantity) {
    this.track('add_to_cart', {
      productId,
      metadata: { quantity }
    });
  },

  trackRemoveFromCart(productId) {
    this.track('remove_from_cart', { productId });
  },

  trackCheckoutStart(cartValue) {
    this.track('checkout_start', {
      metadata: { cartValue }
    });
  },

  trackCheckoutComplete(orderTotal, orderId) {
    this.track('checkout_complete', {
      metadata: { orderTotal, orderId }
    });
  },

  async flush() {
    if (this.queue.length === 0) return;

    const events = [...this.queue];
    this.queue = [];

    try {
      await fetch(`${API_BASE}/track/batch`, {
        method: 'POST',
        headers: authHeaders(),
        body: JSON.stringify({ events })
      });
    } catch (err) {
      // Re-queue failed events
      this.queue.unshift(...events);
    }
  }
};

// Auto-initialize tracker
document.addEventListener('DOMContentLoaded', () => Tracker.init());
