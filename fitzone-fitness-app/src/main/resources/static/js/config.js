const API_BASE = '';
const TOKEN_KEY = 'fitzone_token';
const USER_KEY = 'fitzone_user';

function getToken() { return localStorage.getItem(TOKEN_KEY); }
function getUser() { try { return JSON.parse(localStorage.getItem(USER_KEY)); } catch { return null; } }
function setAuth(token, user) { localStorage.setItem(TOKEN_KEY, token); localStorage.setItem(USER_KEY, JSON.stringify(user)); }
function clearAuth() { localStorage.removeItem(TOKEN_KEY); localStorage.removeItem(USER_KEY); }
function isLoggedIn() { return !!getToken(); }

async function apiFetch(path, options = {}) {
    const token = getToken();
    const headers = { 'Content-Type': 'application/json', ...(options.headers || {}) };
    if (token) headers['Authorization'] = 'Bearer ' + token;
    const res = await fetch(API_BASE + path, { ...options, headers });
    if (res.status === 401) { clearAuth(); window.location.href = '/pages/login.html'; return; }
    return res.json();
}

function setupNav() {
    const user = getUser();
    const nameEl = document.getElementById('user-name');
    const authLink = document.getElementById('auth-link');
    if (user && nameEl) {
        nameEl.textContent = user.name;
        if (authLink) { authLink.textContent = 'Logout'; authLink.onclick = (e) => { e.preventDefault(); clearAuth(); window.location.href = '/'; }; }
    }
}

document.addEventListener('DOMContentLoaded', setupNav);
