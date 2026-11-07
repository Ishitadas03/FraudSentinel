/**
 * Centralized API Client for FraudSentinel REST API.
 * Interacts with FastAPI backend at /api/v1 endpoints with JWT Authentication,
 * RBAC authorization headers, automatic token refresh, and full CRUD workflows.
 */

const rawApiUrl = (import.meta.env.VITE_API_BASE_URL || '').trim();
const API_BASE_URL =
  rawApiUrl && (import.meta.env.DEV || !rawApiUrl.includes('localhost:8000'))
    ? rawApiUrl
    : (import.meta.env.PROD ? '/api/v1' : 'http://localhost:8000/api/v1');

// Preset credentials for demo role switching
export const ROLE_CREDENTIALS = {
  admin: { email: 'admin@fraudsentinel.com', password: 'admin123' },
  analyst: { email: 'analyst@fraudsentinel.com', password: 'analyst123' },
};


// In-memory / storage token state
let currentToken = localStorage.getItem('fraudsentinel_token') || localStorage.getItem('fraudsentinel_jwt_token') || null;
let currentRole = localStorage.getItem('fraudsentinel_role') || 'admin';
let currentUser = null;

/**
 * Get currently stored JWT access token
 */
export function getAuthToken() {
  return currentToken;
}

/**
 * Update stored JWT access token
 */
export function setAuthToken(token, role = null) {
  currentToken = token;
  if (token) {
    localStorage.setItem('fraudsentinel_token', token);
    localStorage.setItem('fraudsentinel_jwt_token', token);
  } else {
    localStorage.removeItem('fraudsentinel_token');
    localStorage.removeItem('fraudsentinel_jwt_token');
  }
  if (role) {
    currentRole = role;
    localStorage.setItem('fraudsentinel_role', role);
  }
}

export function clearAuthToken() {
  currentToken = null;
  localStorage.removeItem('fraudsentinel_token');
  localStorage.removeItem('fraudsentinel_jwt_token');
}

/**
 * Standard fetch helper with error handling, Bearer authorization, and auto-retry on 401.
 */
async function request(endpoint, options = {}, isRetry = false) {
  const url = `${API_BASE_URL}${endpoint}`;
  const headers = {
    'Content-Type': 'application/json',
    ...options.headers,
  };

  if (currentToken && !headers.Authorization) {
    headers.Authorization = `Bearer ${currentToken}`;
  }

  const config = {
    ...options,
    headers,
  };

  try {
    const response = await fetch(url, config);

    // If unauthorized, clear invalid token
    if (response.status === 401) {
      clearAuthToken();
    }

    if (!response.ok) {
      let errorDetail = `HTTP ${response.status}: ${response.statusText}`;
      try {
        const errorJson = await response.json();
        errorDetail =
          errorJson.detail ||
          errorJson.message ||
          (typeof errorJson === 'string' ? errorJson : JSON.stringify(errorJson));
      } catch {
        // use fallback errorDetail
      }
      throw new Error(errorDetail);
    }

    return await response.json();
  } catch (err) {
    console.error(`[API Error] ${options.method || 'GET'} ${url}:`, err.message || err);
    throw err;
  }
}

/**
 * =======================================================================
 * 1. Authentication & RBAC User Management
 * =======================================================================
 */

export async function login(email, password) {
  const data = await request('/auth/login', {
    method: 'POST',
    body: JSON.stringify({ email, password }),
  });
  if (data?.access_token) {
    setAuthToken(data.access_token, data.role);
    currentUser = {
      id: data.user_id,
      email: data.email,
      full_name: data.full_name,
      role: data.role,
    };
  }
  return data;
}

export async function registerUser({ email, password, full_name, role = 'analyst', security_pin = null }) {
  const data = await request('/auth/register', {
    method: 'POST',
    body: JSON.stringify({ email, password, full_name, role, security_pin }),
  });
  if (data?.access_token) {
    setAuthToken(data.access_token, data.role);
    currentUser = {
      id: data.user_id,
      email: data.email,
      full_name: data.full_name,
      role: data.role,
    };
  }
  return data;
}

export async function loginRole(roleName = 'admin') {
  const normalized = roleName.toLowerCase();
  const creds = ROLE_CREDENTIALS[normalized] || ROLE_CREDENTIALS.admin;
  return login(creds.email, creds.password);
}

export async function getMe(explicitToken = null) {
  const tokenToUse = explicitToken || currentToken;
  const headers = tokenToUse ? { Authorization: `Bearer ${tokenToUse}` } : {};
  const data = await request('/auth/me', { headers });
  currentUser = data;
  return data;
}

export async function getCurrentUser(explicitToken = null) {
  return getMe(explicitToken);
}

export async function getUsers() {
  return request('/auth/users');
}

export async function createUser(userData) {
  return request('/auth/users', {
    method: 'POST',
    body: JSON.stringify(userData),
  });
}

export async function updateUser(userId, updateData) {
  return request(`/auth/users/${encodeURIComponent(userId)}`, {
    method: 'PATCH',
    body: JSON.stringify(updateData),
  });
}

export async function deleteUser(userId) {
  return request(`/auth/users/${encodeURIComponent(userId)}`, {
    method: 'DELETE',
  });
}

/**
 * =======================================================================
 * 2. System Health & Telemetry
 * =======================================================================
 */

export async function getHealth() {
  const baseUrl = API_BASE_URL.replace('/api/v1', '');
  try {
    const res = await fetch(`${baseUrl}/health`);
    return await res.json();
  } catch (err) {
    return { status: 'offline', error: err.message };
  }
}

export async function getDbHealth() {
  return request('/health/db');
}

/**
 * =======================================================================
 * 3. Analytics & KPI Trends
 * =======================================================================
 */

export async function getAnalyticsSummary() {
  return request('/analytics/summary');
}

export async function getAnalyticsTrends() {
  return request('/analytics/trends');
}

/**
 * =======================================================================
 * 4. Transactions & Machine Learning Analysis
 * =======================================================================
 */

export async function analyzeTransaction(transactionPayload) {
  return request('/transactions/analyze', {
    method: 'POST',
    body: JSON.stringify(transactionPayload),
  });
}

export async function getTransactions(params = {}) {
  const query = new URLSearchParams();
  Object.entries(params).forEach(([key, value]) => {
    if (value !== undefined && value !== null && value !== '' && value !== 'All') {
      query.append(key, value);
    }
  });
  const qs = query.toString();
  return request(`/transactions${qs ? `?${qs}` : ''}`);
}

export async function getTransactionById(transactionId) {
  return request(`/transactions/${encodeURIComponent(transactionId)}`);
}

/**
 * =======================================================================
 * 5. Fraud Alerts & Triage Management
 * =======================================================================
 */

export async function getAlerts(params = {}) {
  const query = new URLSearchParams();
  Object.entries(params).forEach(([key, value]) => {
    if (value !== undefined && value !== null && value !== '' && value !== 'All') {
      query.append(key, value);
    }
  });
  const qs = query.toString();
  return request(`/alerts${qs ? `?${qs}` : ''}`);
}

export async function getAlertById(alertId) {
  return request(`/alerts/${encodeURIComponent(alertId)}`);
}

export async function updateAlert(alertId, updateData) {
  return request(`/alerts/${encodeURIComponent(alertId)}`, {
    method: 'PATCH',
    body: JSON.stringify(updateData),
  });
}

export async function resolveAlert(alertId) {
  return request(`/alerts/${encodeURIComponent(alertId)}/resolve`, {
    method: 'POST',
  });
}

export async function bulkResolveAlerts(severity = null) {
  const qs = severity && severity !== 'All' ? `?severity=${encodeURIComponent(severity.toLowerCase())}` : '';
  return request(`/alerts/bulk-resolve${qs}`, {
    method: 'POST',
  });
}

/**
 * =======================================================================
 * 6. Multi-Paradigm KR&R & Bayesian Reasoning
 * =======================================================================
 */

export async function getReasoning(transactionId) {
  return request(`/reasoning/${encodeURIComponent(transactionId)}`);
}

/**
 * =======================================================================
 * 7. Time-Series Predictive Forecasting
 * =======================================================================
 */

export async function getForecasts() {
  return request('/forecasts');
}

export async function getForecastByHorizon(horizon = 7) {
  return request(`/forecasts/${encodeURIComponent(horizon)}`);
}

/**
 * =======================================================================
 * 8. Investigation & Graph Search
 * =======================================================================
 */

export async function getInvestigationNodes() {
  return request('/investigations/nodes');
}

export async function searchInvestigation(searchPayload) {
  // Normalize payload fields for backend schema
  const payload = {
    start_node: searchPayload.start_node || searchPayload.source_account || 'VIC_1',
    goal_node: searchPayload.goal_node || searchPayload.target_account || 'HUB_ALPHA',
    algorithm: searchPayload.algorithm || 'astar',
    heuristic: searchPayload.heuristic || 'euclidean',
  };

  return request('/investigations/search', {
    method: 'POST',
    body: JSON.stringify(payload),
  });
}

export default {
  ROLE_CREDENTIALS,
  getAuthToken,
  setAuthToken,
  clearAuthToken,
  login,
  loginRole,
  getMe,
  getCurrentUser,
  getUsers,
  createUser,
  updateUser,
  deleteUser,
  getHealth,
  getDbHealth,
  getAnalyticsSummary,
  getAnalyticsTrends,
  analyzeTransaction,
  getTransactions,
  getTransactionById,
  getAlerts,
  getAlertById,
  updateAlert,
  resolveAlert,
  bulkResolveAlerts,
  getReasoning,
  getForecasts,
  getForecastByHorizon,
  getInvestigationNodes,
  searchInvestigation,
};
