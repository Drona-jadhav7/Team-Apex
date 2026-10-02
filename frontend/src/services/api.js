import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000/api';

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 10000,
});

export const fetchBenchmarkSites = async () => {
  const response = await apiClient.get('/sites');
  return response.data;
};

export const fetchSiteById = async (siteId) => {
  const response = await apiClient.get(`/sites/${siteId}`);
  return response.data;
};

export const assessCustomSite = async (sitePayload) => {
  const response = await apiClient.post('/assess', sitePayload);
  return response.data;
};

export const compareSites = async (payload = {}) => {
  const response = await apiClient.post('/compare', payload);
  return response.data;
};

export const checkApiHealth = async () => {
  try {
    const res = await apiClient.get('/health', { baseURL: 'http://127.0.0.1:8000' });
    return res.data;
  } catch (err) {
    return { status: 'offline', error: err.message };
  }
};
