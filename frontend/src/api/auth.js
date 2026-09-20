import { request } from './client';

export const authApi = {
  signup: async (name, email, password) => {
    return request('/api/auth/signup', {
      method: 'POST',
      body: JSON.stringify({ name, email, password }),
    });
  },

  login: async (email, password) => {
    return request('/api/auth/login', {
      method: 'POST',
      body: JSON.stringify({ email, password }),
    });
  },

  getMe: async () => {
    return request('/api/auth/me', {
      method: 'GET',
    });
  }
};
