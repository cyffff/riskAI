import React, { useState, useEffect } from 'react';
import {
  Box,
  Typography,
  Paper,
  CircularProgress,
  Alert,
} from '@mui/material';
import { SQLStatementList } from '../../components/features/SQLStatementList';
import { MockDataAlert } from '../../components/MockDataAlert';
import { featureApi } from '../../services/api';

export default function SQLStatements() {
  const [sqlStatements, setSqlStatements] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [usingMockData, setUsingMockData] = useState(false);

  const fetchSqlStatements = async () => {
    try {
      setLoading(true);
      setError(null);
      
      // If there's an environment variable for using mock data, this will return true
      const mockDataEnabled = process.env.REACT_APP_USE_MOCK_DATA === 'true' || true;
      setUsingMockData(mockDataEnabled);
      
      const data = await featureApi.getSqlStatements();
      setSqlStatements(data);
    } catch (err) {
      setError(err.message || 'Failed to fetch SQL statements');
      console.error('Error fetching SQL statements:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchSqlStatements();
  }, []);

  return (
    <Box>
      <Typography variant="h4" component="h1" gutterBottom>
        SQL Statements Management
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
          <SQLStatementList sqlStatements={sqlStatements} onUpdate={fetchSqlStatements} />
        )}
      </Paper>
    </Box>
  );
} 