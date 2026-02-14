const API_BASE = 'http://localhost:5000/api';

function getToken() {
  return localStorage.getItem('token');
}

function getUser() {
  const user = localStorage.getItem('user');
  return user ? JSON.parse(user) : null;
}

function authHeaders() {
  const headers = { 'Content-Type': 'application/json' };
  const token = getToken();
  if (token) headers['Authorization'] = `Bearer ${token}`;

  // Session tracking
  let sessionId = sessionStorage.getItem('sessionId');
  if (!sessionId) {
    sessionId = 'sess_' + Date.now() + '_' + Math.random().toString(36).slice(2, 9);
    sessionStorage.setItem('sessionId', sessionId);
  }
  headers['x-session-id'] = sessionId;
  headers['x-attribution'] = sessionStorage.getItem('attribution') || 'direct';
  headers['x-device-type'] = /Mobi/i.test(navigator.userAgent) ? 'mobile' : 'desktop';

  return headers;
}

function logout() {
  localStorage.removeItem('token');
  localStorage.removeItem('user');
  window.location.href = '/pages/login.html';
}

// Update auth link across all pages
document.addEventListener('DOMContentLoaded', () => {
  const authLink = document.getElementById('auth-link');
  const user = getUser();
  if (authLink && user) {
    authLink.textContent = `Logout (${user.name})`;
    authLink.href = '#';
    authLink.onclick = (e) => { e.preventDefault(); logout(); };
  }

  // Capture UTM/attribution from URL
  const params = new URLSearchParams(window.location.search);
  const utm = params.get('utm_source') || params.get('channel');
  if (utm) sessionStorage.setItem('attribution', utm);
});
