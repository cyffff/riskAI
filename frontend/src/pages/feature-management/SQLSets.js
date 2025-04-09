import React, { useState, useEffect } from 'react';
import {
  Box,
  Typography,
  Paper,
  CircularProgress,
  Alert,
} from '@mui/material';
import { SQLSetList } from '../../components/features/SQLSetList';
import { MockDataAlert } from '../../components/MockDataAlert';
import { featureApi } from '../../services/api';

export default function SQLSets() {
  const [sqlSets, setSqlSets] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [usingMockData, setUsingMockData] = useState(false);

  const fetchSqlSets = async () => {
    try {
      setLoading(true);
      setError(null);
      
      // If there's an environment variable for using mock data, this will return true
      const mockDataEnabled = process.env.REACT_APP_USE_MOCK_DATA === 'true' || true;
      setUsingMockData(mockDataEnabled);
      
      const data = await featureApi.getSqlSets();
      setSqlSets(data);
    } catch (err) {
      setError(err.message || 'Failed to fetch SQL sets');
      console.error('Error fetching SQL sets:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchSqlSets();
  }, []);

  return (
    <Box>
      <Typography variant="h4" component="h1" gutterBottom>
        SQL Sets Management
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
          <SQLSetList sqlSets={sqlSets} onUpdate={fetchSqlSets} />
        )}
      </Paper>
    </Box>
  );
} 