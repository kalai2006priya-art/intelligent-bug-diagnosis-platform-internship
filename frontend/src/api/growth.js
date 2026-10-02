import { request } from './client';

export const growthApi = {
  validateQualityGate: async (bugId) => {
    return request(`/api/knowledge-base/growth/validate/${bugId}`, {
      method: 'GET'
    });
  },

  resolveBug: async (bugId, payload) => {
    return request(`/api/knowledge-base/growth/resolve/${bugId}`, {
      method: 'POST',
      body: JSON.stringify(payload)
    });
  },

  promoteToKnowledgeBase: async (bugId, payload = null) => {
    return request(`/api/knowledge-base/growth/promote/${bugId}`, {
      method: 'POST',
      body: payload ? JSON.stringify(payload) : undefined
    });
  },

  getCandidates: async () => {
    return request('/api/knowledge-base/growth/candidates', {
      method: 'GET'
    });
  },

  getStats: async () => {
    return request('/api/knowledge-base/growth/stats', {
      method: 'GET'
    });
  }
};
