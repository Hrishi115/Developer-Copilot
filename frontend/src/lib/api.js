const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

/**
 * Central fetch wrapper that handles auth headers, errors, and responses
 * @param {string} endpoint - API endpoint (e.g., '/auth/signup')
 * @param {object} options - Fetch options (method, body, headers, etc.)
 * @returns {Promise<any>} - Parsed JSON response
 */

function extractErrorMessage(data, status) {
  if (!data) return `API Error: ${status}`;
  if (Array.isArray(data.detail)) {
    return data.detail.map((e) => e.msg).join(', ');
  }
  if (typeof data.detail === 'string') return data.detail;
  if (typeof data.error === 'string') return data.error;
  return `API Error: ${status}`;
}

export async function apiFetch(endpoint, options = {}) {
  const url = `${API_BASE_URL}${endpoint}`;
  const token = localStorage.getItem('auth_token');

  const headers = {
    'Content-Type': 'application/json',
    ...options.headers,
  };

  if (token) {
    headers['Authorization'] = `Bearer ${token}`;
  }

  const response = await fetch(url, {
    ...options,
    headers,
  });

  const data = await response.json().catch(() => null);

  if (!response.ok) {
    // Handle 401 - token expired
    if (response.status === 401) {
      localStorage.removeItem('auth_token');
      window.location.href = '/';
    }

    const errorMessage = extractErrorMessage(data, response.status);
    const error = new Error(errorMessage);
    error.status = response.status;
    error.data = data;
    throw error;
  }

  return data;
}

/**
 * Authentication endpoints
 */
export async function authSignup(email, password, full_name, username) {
  await apiFetch('/auth/register', {
    method: 'POST',
    body: JSON.stringify({ email, password, full_name, username }),
  });

  const loginResult = authLogin(email, password);

  if (loginResult.access_token) {
    localStorage.setItem('auth_token', loginResult.access_token);
  }
  return loginResult;
}

export async function authLogin(email, password) {
  return apiFetch('/auth/login', {
    method: 'POST',
    body: JSON.stringify({ email, password }),
  });
}

/**
 * Setup endpoint - configures repo and ingest data
 */
export async function setupRepo(config) {
  const {
    // github_token,
    // gemini_api_key,
    owner_repo,
    branch = 'main',
  } = config;

  // Then trigger ingestion of the repository
  const repoUrl = `${owner_repo}`;
  return apiFetch(`/ingest/${encodeURIComponent(repoUrl)}`, {
    method: 'POST',
    body: JSON.stringify({
      // github_token,
      // gemini_api_key,
      branch,
    }),
  });
}

/**
 * Chat/Query endpoint - sends a query about the repo
 */
export async function queryRepo(query, owner_repo) {
  return apiFetch('/retrieval/', {
    method: 'POST',
    body: JSON.stringify({
      query,
      repo: owner_repo,
    }),
  });
}

/**
 * Validate token without making authenticated request
 */
export function hasValidToken() {
  const token = localStorage.getItem('auth_token');
  return Boolean(token);
}
