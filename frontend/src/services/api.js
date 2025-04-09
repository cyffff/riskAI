import axios from 'axios';
import { mockData } from './mockData';

const API_BASE_URL = process.env.REACT_APP_API_BASE_URL || 'http://localhost:8000/api/v1';

// Flag to determine if we should use mock data (for development/testing)
const USE_MOCK_DATA = process.env.REACT_APP_USE_MOCK_DATA === 'true' || true;

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Utility function to safely make API calls with fallback to mock data
const safeApiCall = async (apiCall, mockDataKey) => {
  if (USE_MOCK_DATA) {
    console.log(`Using mock data for ${mockDataKey}`);
    return mockData[mockDataKey];
  }
  
  try {
    const response = await apiCall();
    return response.data;
  } catch (error) {
    console.error(`API error: ${error.message}. Using mock data instead.`);
    return mockData[mockDataKey];
  }
};

// Feature Management API
export const featureApi = {
  // Features
  getFeatures: async () => {
    return safeApiCall(
      () => api.get('/features'),
      'features'
    );
  },

  createFeature: async (feature) => {
    if (USE_MOCK_DATA) {
      console.log('Mock create feature:', feature);
      return { ...feature, id: Math.floor(Math.random() * 1000) };
    }
    const response = await api.post('/features', feature);
    return response.data;
  },

  updateFeature: async (id, feature) => {
    if (USE_MOCK_DATA) {
      console.log('Mock update feature:', id, feature);
      return { ...feature, id };
    }
    const response = await api.put(`/features/${id}`, feature);
    return response.data;
  },

  deleteFeature: async (id) => {
    if (USE_MOCK_DATA) {
      console.log('Mock delete feature:', id);
      return { success: true };
    }
    const response = await api.delete(`/features/${id}`);
    return response.data;
  },

  // SQL Sets
  getSqlSets: async () => {
    return safeApiCall(
      () => api.get('/sql/sets'),
      'sqlSets'
    );
  },

  createSqlSet: async (sqlSet) => {
    if (USE_MOCK_DATA) {
      console.log('Mock create SQL set:', sqlSet);
      return { ...sqlSet, id: Math.floor(Math.random() * 1000) };
    }
    const response = await api.post('/sql/sets', sqlSet);
    return response.data;
  },

  updateSqlSet: async (id, sqlSet) => {
    if (USE_MOCK_DATA) {
      console.log('Mock update SQL set:', id, sqlSet);
      return { ...sqlSet, id };
    }
    const response = await api.put(`/sql/sets/${id}`, sqlSet);
    return response.data;
  },

  deleteSqlSet: async (id) => {
    if (USE_MOCK_DATA) {
      console.log('Mock delete SQL set:', id);
      return { success: true };
    }
    const response = await api.delete(`/sql/sets/${id}`);
    return response.data;
  },

  // SQL Statements
  getSqlStatements: async () => {
    return safeApiCall(
      () => api.get('/sql/statements'),
      'sqlStatements'
    );
  },

  createSqlStatement: async (sqlStatement) => {
    if (USE_MOCK_DATA) {
      console.log('Mock create SQL statement:', sqlStatement);
      return { ...sqlStatement, id: Math.floor(Math.random() * 1000) };
    }
    const response = await api.post('/sql/statements', sqlStatement);
    return response.data;
  },

  updateSqlStatement: async (id, sqlStatement) => {
    if (USE_MOCK_DATA) {
      console.log('Mock update SQL statement:', id, sqlStatement);
      return { ...sqlStatement, id };
    }
    const response = await api.put(`/sql/statements/${id}`, sqlStatement);
    return response.data;
  },

  deleteSqlStatement: async (id) => {
    if (USE_MOCK_DATA) {
      console.log('Mock delete SQL statement:', id);
      return { success: true };
    }
    const response = await api.delete(`/sql/statements/${id}`);
    return response.data;
  },
};

export default api; 