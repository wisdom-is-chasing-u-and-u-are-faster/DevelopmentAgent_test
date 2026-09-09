/**
 * CosmeticsAPI - Enterprise D2C Online Cosmetic Store API Client
 */
const CosmeticsAPI = {
  baseUrl: '/api/v1',

  async request(endpoint, options = {}) {
    const url = `${this.baseUrl}${endpoint}`;
    const defaultHeaders = {
      'Content-Type': 'application/json',
      'Accept': 'application/json'
    };

    const config = {
      ...options,
      headers: {
        ...defaultHeaders,
        ...options.headers
      }
    };

    try {
      const response = await fetch(url, config);
      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.detail || `HTTP Error ${response.status}`);
      }
      return await response.json();
    } catch (error) {
      console.error(`API Error on [${options.method || 'GET'}] ${url}:`, error);
      throw error;
    }
  },

  // Products
  async getProducts(params = {}) {
    const searchParams = new URLSearchParams();
    if (params.category) searchParams.append('category', params.category);
    if (params.undertone) searchParams.append('undertone', params.undertone);
    if (params.finish) searchParams.append('finish', params.finish);
    if (params.depth) searchParams.append('depth', params.depth);
    if (params.search) searchParams.append('search', params.search);

    const qs = searchParams.toString();
    return this.request(`/products${qs ? '?' + qs : ''}`);
  },

  async getProduct(productId) {
    return this.request(`/products/${productId}`);
  },

  // Shade Finder Quiz
  async matchShade(data) {
    return this.request('/shade-finder/match', {
      method: 'POST',
      body: JSON.stringify(data)
    });
  },

  // Cart Management
  async getCart() {
    return this.request('/cart');
  },

  async addToCart(data) {
    return this.request('/cart', {
      method: 'POST',
      body: JSON.stringify(data)
    });
  },

  async removeFromCart(itemId) {
    return this.request(`/cart/${itemId}`, {
      method: 'DELETE'
    });
  },

  // Checkout
  async processCheckout(data) {
    return this.request('/checkout', {
      method: 'POST',
      body: JSON.stringify(data)
    });
  },

  // Account & Loyalty
  async getDashboard() {
    return this.request('/account/dashboard');
  },

  // Subscriptions
  async getSubscriptions() {
    return this.request('/subscriptions');
  },

  async skipSubscription(subId) {
    return this.request(`/subscriptions/${subId}/skip`, {
      method: 'POST'
    });
  },

  async swapSubscription(subId, newShadeId) {
    return this.request(`/subscriptions/${subId}/swap`, {
      method: 'POST',
      body: JSON.stringify({ new_shade_id: newShadeId })
    });
  }
};

window.CosmeticsAPI = CosmeticsAPI;
