import React, { useState, useEffect } from 'react';
import {
  Box,
  Typography,
  Paper,
  CircularProgress,
  Alert,
} from '@mui/material';
import { FeatureList } from '../../components/features/FeatureList';
import { MockDataAlert } from '../../components/MockDataAlert';
import { featureApi } from '../../services/api';

export default function Features() {
  const [features, setFeatures] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [usingMockData, setUsingMockData] = useState(false);

  const fetchFeatures = async () => {
    try {
      setLoading(true);
      setError(null);
      
      // If there's an environment variable for using mock data, this will return true
      const mockDataEnabled = process.env.REACT_APP_USE_MOCK_DATA === 'true' || true;
      setUsingMockData(mockDataEnabled);
      
      const data = await featureApi.getFeatures();
      setFeatures(data);
    } catch (err) {
      setError(err.message || 'Failed to fetch features');
      console.error('Error fetching features:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchFeatures();
  }, []);

  return (
    <Box>
      <Typography variant="h4" component="h1" gutterBottom>
        Feature Management
      </Typography>
      
      {usingMockData && <MockDataAlert />}
      
      <Paper sx={{ p: 2, mb: 2 }}>
        {loading ? (
          <Box display="flex" justifyContent="center" p={3}>
            <CircularProgress />
          </Box>
        ) : error ? (
          <Alert severity="error">{error}</Alert>
        ) : (
          <FeatureList features={features} onUpdate={fetchFeatures} />
        )}
      </Paper>
    </Box>
  );
} 