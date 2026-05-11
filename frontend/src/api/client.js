const API_BASE = import.meta.env.VITE_API_BASE || '';

const TOKEN_KEY = 'safeflow.access_token';
const REFRESH_KEY = 'safeflow.refresh_token';
const USER_KEY = 'safeflow.user';

export const tokenStore = {
  getAccess: () => localStorage.getItem(TOKEN_KEY),
  getRefresh: () => localStorage.getItem(REFRESH_KEY),
  getUser: () => {
    const raw = localStorage.getItem(USER_KEY);
    return raw ? JSON.parse(raw) : null;
  },
  set: ({ access_token, refresh_token, user }) => {
    if (access_token) localStorage.setItem(TOKEN_KEY, access_token);
    if (refresh_token) localStorage.setItem(REFRESH_KEY, refresh_token);
    if (user) localStorage.setItem(USER_KEY, JSON.stringify(user));
  },
  clear: () => {
    localStorage.removeItem(TOKEN_KEY);
    localStorage.removeItem(REFRESH_KEY);
    localStorage.removeItem(USER_KEY);
  },
};

async function request(path, { method = 'GET', body, auth = true, headers = {} } = {}) {
  const finalHeaders = { 'Content-Type': 'application/json', ...headers };
  if (auth) {
    const token = tokenStore.getAccess();
    if (token) finalHeaders.Authorization = `Bearer ${token}`;
  }
  const res = await fetch(`${API_BASE}${path}`, {
    method,
    headers: finalHeaders,
    body: body ? JSON.stringify(body) : undefined,
  });

  let data = null;
  const text = await res.text();
  if (text) {
    try {
      data = JSON.parse(text);
    } catch {
      data = text;
    }
  }

  if (!res.ok) {
    const detail =
      (data && (data.detail || data.message)) ||
      (typeof data === 'string' ? data : `Request failed (${res.status})`);
    const error = new Error(typeof detail === 'string' ? detail : JSON.stringify(detail));
    error.status = res.status;
    error.data = data;
    throw error;
  }

  return data;
}

export const api = {
  // Auth
  register: (payload) =>
    request('/auth/register', { method: 'POST', body: payload, auth: false }),
  login: (payload) =>
    request('/auth/login', { method: 'POST', body: payload, auth: false }),
  logout: () => request('/auth/logout', { method: 'POST' }),

  // Account
  myAccount: () => request('/api/accounts/me'),

  // Transactions
  myTransactions: () => request('/api/transactions/me'),
  transaction: (id) => request(`/api/transactions/${id}`),

  // Payments
  createPayment: (payload) =>
    request('/api/payments', { method: 'POST', body: payload }),
  confirmPayment: (id, payload = {}) =>
    request(`/api/payments/${id}/confirm`, { method: 'POST', body: payload }),
  cancelPayment: (id, payload = {}) =>
    request(`/api/payments/${id}/cancel`, { method: 'POST', body: payload }),
};
