import axios from 'axios';

// Default to relative '/api' so all requests pass transparently through the Vite proxy
// on the same origin (preventing "Connection Refused: localhost:8000" on public tunnels)
const API_BASE_URL = import.meta.env.VITE_API_URL || '/api';

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 15000,
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
    // Relative call through Vite proxy
    const res = await apiClient.get('/health', { baseURL: '' });
    return res.data;
  } catch (err) {
    try {
      // Fallback to /api/health
      const res = await apiClient.get('/health');
      return res.data;
    } catch (innerErr) {
      return { status: 'offline', error: innerErr.message };
    }
  }
};
