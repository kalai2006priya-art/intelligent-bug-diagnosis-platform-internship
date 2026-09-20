import { request } from './client';

export const bugsApi = {
  createBug: async (bugData) => {
    return request('/bugs', {
      method: 'POST',
      body: JSON.stringify(bugData),
    });
  },

  uploadLogFile: async (file) => {
    const formData = new FormData();
    formData.append('file', file);
    return request('/bugs/upload', {
      method: 'POST',
      body: formData,
    });
  },

  listBugs: async (skip = 0, limit = 50) => {
    return request(`/bugs?skip=${skip}&limit=${limit}`, {
      method: 'GET',
    });
  },

  getBug: async (bugId) => {
    return request(`/bugs/${bugId}`, {
      method: 'GET',
    });
  },

  analyzeBug: async (bugId) => {
    return request(`/bugs/${bugId}/analyze`, {
      method: 'POST',
    });
  },

  getDiagnosis: async (bugId) => {
    return request(`/bugs/${bugId}/diagnosis`, {
      method: 'GET',
    });
  },

  getBugStats: async () => {
    return request('/bugs/stats/summary', {
      method: 'GET',
    });
  }
};
