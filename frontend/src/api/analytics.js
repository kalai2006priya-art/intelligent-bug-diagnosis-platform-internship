import { request } from './client';

export const analyticsApi = {
  getOverview: async (params = {}) => {
    const query = new URLSearchParams();
    if (params.component) query.append('component', params.component);
    if (params.severity) query.append('severity', params.severity);
    if (params.priority) query.append('priority', params.priority);
    if (params.exception_type) query.append('exception_type', params.exception_type);
    if (params.source) query.append('source', params.source);
    if (params.date_from) query.append('date_from', params.date_from);
    if (params.date_to) query.append('date_to', params.date_to);

    const queryString = query.toString();
    const endpoint = queryString ? `/api/analytics/overview?${queryString}` : '/api/analytics/overview';
    return request(endpoint, { method: 'GET' });
  },

  getComponents: async (source = 'all') => {
    return request(`/api/analytics/components?source=${source}`, { method: 'GET' });
  },

  getExceptions: async (component = '', source = 'all') => {
    const query = new URLSearchParams({ source });
    if (component) query.append('component', component);
    return request(`/api/analytics/exceptions?${query.toString()}`, { method: 'GET' });
  },

  getRootCauses: async (component = '', source = 'all') => {
    const query = new URLSearchParams({ source });
    if (component) query.append('component', component);
    return request(`/api/analytics/root-causes?${query.toString()}`, { method: 'GET' });
  },

  getClusters: async (component = '', source = 'all') => {
    const query = new URLSearchParams({ source });
    if (component) query.append('component', component);
    return request(`/api/analytics/clusters?${query.toString()}`, { method: 'GET' });
  },

  getTrends: async (component = '', source = 'all') => {
    const query = new URLSearchParams({ source });
    if (component) query.append('component', component);
    return request(`/api/analytics/trends?${query.toString()}`, { method: 'GET' });
  },

  getFilters: async () => {
    return request('/api/analytics/filters', { method: 'GET' });
  }
};
