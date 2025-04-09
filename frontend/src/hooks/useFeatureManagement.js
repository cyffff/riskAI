import { useState, useEffect } from 'react';
import { featureApi } from '../services/api';

export function useFeatureManagement() {
  const [features, setFeatures] = useState([]);
  const [sqlSets, setSqlSets] = useState([]);
  const [sqlStatements, setSqlStatements] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const fetchData = async () => {
    try {
      setLoading(true);
      setError(null);
      
      // Use Promise.allSettled to ensure all promises complete regardless of success/failure
      const results = await Promise.allSettled([
        featureApi.getFeatures(),
        featureApi.getSqlSets(),
        featureApi.getSqlStatements()
      ]);
      
      // Process results - we should have data even if API fails due to our mock data fallback
      const [featuresResult, sqlSetsResult, sqlStatementsResult] = results;
      
      if (featuresResult.status === 'fulfilled') {
        setFeatures(featuresResult.value || []);
      } else {
        console.error('Failed to fetch features:', featuresResult.reason);
        setFeatures([]);
      }
      
      if (sqlSetsResult.status === 'fulfilled') {
        setSqlSets(sqlSetsResult.value || []);
      } else {
        console.error('Failed to fetch SQL sets:', sqlSetsResult.reason);
        setSqlSets([]);
      }
      
      if (sqlStatementsResult.status === 'fulfilled') {
        setSqlStatements(sqlStatementsResult.value || []);
      } else {
        console.error('Failed to fetch SQL statements:', sqlStatementsResult.reason);
        setSqlStatements([]);
      }
    } catch (err) {
      setError(err.message || 'Failed to fetch data');
      console.error('Error fetching data:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, []);

  const refreshData = () => {
    fetchData();
  };

  return {
    features,
    sqlSets,
    sqlStatements,
    loading,
    error,
    refreshData
  };
} 