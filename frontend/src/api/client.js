const BASE_URL = '';

export async function request(endpoint, options = {}) {
  const token = localStorage.getItem('bug_platform_token');
  const headers = {
    ...options.headers,
  };

  // If payload is not FormData, add Content-Type: application/json
  if (!(options.body instanceof FormData)) {
    headers['Content-Type'] = 'application/json';
  }

  if (token) {
    headers['Authorization'] = `Bearer ${token}`;
  }

  const response = await fetch(`${BASE_URL}${endpoint}`, {
    ...options,
    headers,
  });

  if (response.status === 401) {
    // Only redirect if not already on auth/landing pages
    if (!window.location.hash.includes('login') && !window.location.hash.includes('signup') && window.location.hash !== '' && window.location.hash !== '#/') {
      localStorage.removeItem('bug_platform_token');
      localStorage.removeItem('bug_platform_user');
      window.location.hash = '#/login';
    }
  }

  const contentType = response.headers.get('content-type');
  let data = null;
  if (contentType && contentType.includes('application/json')) {
    data = await response.json();
  } else {
    data = await response.text();
  }

  if (!response.ok) {
    const errorMsg = data?.detail || (typeof data === 'string' ? data : 'API Request failed');
    throw new Error(errorMsg);
  }

  return data;
}
