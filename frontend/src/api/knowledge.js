import { request } from './client';

export const knowledgeApi = {
  listDefects: async (filters = {}) => {
    const params = new URLSearchParams();
    if (filters.source) params.append('source', filters.source);
    if (filters.project) params.append('project', filters.project);
    if (filters.component) params.append('component', filters.component);
    if (filters.limit) params.append('limit', filters.limit);
    return request(`/api/knowledge-base/defects?${params.toString()}`, {
      method: 'GET',
    });
  },

  searchSemantic: async (query, top_k = 5, source = null) => {
    return request('/api/knowledge-base/search', {
      method: 'POST',
      body: JSON.stringify({ query, top_k, source }),
    });
  },

  getStats: async () => {
    return request('/api/knowledge-base/stats', {
      method: 'GET',
    });
  }
};
