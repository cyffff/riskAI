import React, { useState, useEffect } from 'react';
import {
  Grid,
  Paper,
  Typography,
  Box,
  CircularProgress,
  Alert
} from '@mui/material';
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer
} from 'recharts';
import {
  BarChart,
  Bar,
} from 'recharts';
import { MockDataAlert } from '../components/MockDataAlert';

// Mock data for when API calls fail
const MOCK_DASHBOARD_DATA = {
  metrics: {
    auc: 0.82,
    approval_rate: 68.5,
    recent_adjustments: 12,
    new_features: 5,
    feature_importance: [
      { name: "Credit Score", importance: 0.85 },
      { name: "Income to Debt Ratio", importance: 0.76 },
      { name: "Previous Defaults", importance: 0.68 },
      { name: "Employment Duration", importance: 0.57 },
      { name: "Address Stability", importance: 0.42 }
    ]
  },
  riskTrends: [
    { date: "2023-01", average_risk_score: 0.42, default_rate: 0.08 },
    { date: "2023-02", average_risk_score: 0.44, default_rate: 0.09 },
    { date: "2023-03", average_risk_score: 0.41, default_rate: 0.08 },
    { date: "2023-04", average_risk_score: 0.39, default_rate: 0.07 },
    { date: "2023-05", average_risk_score: 0.38, default_rate: 0.07 },
    { date: "2023-06", average_risk_score: 0.40, default_rate: 0.08 }
  ],
  userSegments: [
    { segment: "Low Risk", count: 1245 },
    { segment: "Medium Risk", count: 845 },
    { segment: "High Risk", count: 432 },
    { segment: "Very High Risk", count: 178 }
  ]
};

const Dashboard = () => {
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [metrics, setMetrics] = useState(null);
  const [riskTrends, setRiskTrends] = useState([]);
  const [userSegments, setUserSegments] = useState([]);
  const [usingMockData, setUsingMockData] = useState(false);

  useEffect(() => {
    fetchDashboardData();
  }, []);

  // Safely fetch data with JSON parsing error handling
  const safeFetch = async (url, mockData) => {
    try {
      const response = await fetch(url);
      
      // Check if response is ok (status 200-299)
      if (!response.ok) {
        throw new Error(`Server returned ${response.status} ${response.statusText}`);
      }
      
      // Check content type to ensure it's JSON
      const contentType = response.headers.get('content-type');
      if (!contentType || !contentType.includes('application/json')) {
        console.warn(`Expected JSON but got ${contentType}. Using mock data.`);
        setUsingMockData(true);
        return mockData;
      }
      
      // Try to parse the JSON
      try {
        const data = await response.json();
        return data;
      } catch (jsonError) {
        console.error('Error parsing JSON:', jsonError);
        setUsingMockData(true);
        return mockData;
      }
    } catch (fetchError) {
      console.error('Error fetching data:', fetchError);
      setUsingMockData(true);
      return mockData;
    }
  };

  const fetchDashboardData = async () => {
    try {
      setLoading(true);
      setError(null);
      
      // Check if we should use mock data directly (for development)
      const useMockData = process.env.REACT_APP_USE_MOCK_DATA === 'true' || true;
      
      if (useMockData) {
        setUsingMockData(true);
        setMetrics(MOCK_DASHBOARD_DATA.metrics);
        setRiskTrends(MOCK_DASHBOARD_DATA.riskTrends);
        setUserSegments(MOCK_DASHBOARD_DATA.userSegments);
        return;
      }

      // Use Promise.allSettled for more resilient fetching
      const results = await Promise.allSettled([
        safeFetch('/api/model/metrics', MOCK_DASHBOARD_DATA.metrics),
        safeFetch('/api/risk-analysis/trends', MOCK_DASHBOARD_DATA.riskTrends),
        safeFetch('/api/risk-analysis/segments', MOCK_DASHBOARD_DATA.userSegments)
      ]);

      // Process metrics
      if (results[0].status === 'fulfilled') {
        setMetrics(results[0].value);
      } else {
        console.error('Failed to fetch metrics:', results[0].reason);
        setMetrics(MOCK_DASHBOARD_DATA.metrics);
        setUsingMockData(true);
      }

      // Process risk trends
      if (results[1].status === 'fulfilled') {
        setRiskTrends(results[1].value);
      } else {
        console.error('Failed to fetch risk trends:', results[1].reason);
        setRiskTrends(MOCK_DASHBOARD_DATA.riskTrends);
        setUsingMockData(true);
      }

      // Process user segments
      if (results[2].status === 'fulfilled') {
        setUserSegments(results[2].value);
      } else {
        console.error('Failed to fetch user segments:', results[2].reason);
        setUserSegments(MOCK_DASHBOARD_DATA.userSegments);
        setUsingMockData(true);
      }

    } catch (err) {
      setError(err.message || 'An unexpected error occurred');
      console.error('Error in fetchDashboardData:', err);
      
      // Fall back to mock data on error
      setMetrics(MOCK_DASHBOARD_DATA.metrics);
      setRiskTrends(MOCK_DASHBOARD_DATA.riskTrends);
      setUserSegments(MOCK_DASHBOARD_DATA.userSegments);
      setUsingMockData(true);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="400px">
        <CircularProgress />
      </Box>
    );
  }

  return (
    <Box>
      <Typography variant="h4" component="h1" gutterBottom>
        Dashboard
      </Typography>
      
      {usingMockData && <MockDataAlert />}
      
      {error && (
        <Alert severity="error" sx={{ mt: 2, mb: 2 }}>
          {error}
        </Alert>
      )}

      <Grid container spacing={3}>
        {/* Key Metrics */}
        <Grid item xs={12} md={4}>
          <Paper sx={{ p: 2, display: 'flex', flexDirection: 'column', height: 240 }}>
            <Typography component="h2" variant="h6" color="primary" gutterBottom>
              Model Performance
            </Typography>
            {metrics && (
              <Box>
                <Typography variant="h4" gutterBottom>
                  {metrics.auc.toFixed(3)}
                </Typography>
                <Typography color="text.secondary">AUC Score</Typography>
                <Typography variant="h4" gutterBottom sx={{ mt: 2 }}>
                  {metrics.approval_rate.toFixed(2)}%
                </Typography>
                <Typography color="text.secondary">Approval Rate</Typography>
              </Box>
            )}
          </Paper>
        </Grid>
        <Grid item xs={12} md={4}>
          <Paper sx={{ p: 2, display: 'flex', flexDirection: 'column', height: 240 }}>
            <Typography component="h2" variant="h6" color="primary" gutterBottom>
              Risk Distribution
            </Typography>
            {userSegments.length > 0 && (
              <ResponsiveContainer width="100%" height={180}>
                <BarChart data={userSegments}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="segment" />
                  <YAxis />
                  <Tooltip />
                  <Bar dataKey="count" fill="#8884d8" />
                </BarChart>
              </ResponsiveContainer>
            )}
          </Paper>
        </Grid>
        <Grid item xs={12} md={4}>
          <Paper sx={{ p: 2, display: 'flex', flexDirection: 'column', height: 240 }}>
            <Typography component="h2" variant="h6" color="primary" gutterBottom>
              Recent Activity
            </Typography>
            {metrics && (
              <Box>
                <Typography variant="h4" gutterBottom>
                  {metrics.recent_adjustments}
                </Typography>
                <Typography color="text.secondary">Model Adjustments</Typography>
                <Typography variant="h4" gutterBottom sx={{ mt: 2 }}>
                  {metrics.new_features}
                </Typography>
                <Typography color="text.secondary">New Features</Typography>
              </Box>
            )}
          </Paper>
        </Grid>

        {/* Risk Trends Chart */}
        <Grid item xs={12}>
          <Paper sx={{ p: 2, display: 'flex', flexDirection: 'column', height: 400 }}>
            <Typography component="h2" variant="h6" color="primary" gutterBottom>
              Risk Score Trends
            </Typography>
            {riskTrends.length > 0 && (
              <ResponsiveContainer width="100%" height={300}>
                <LineChart data={riskTrends}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="date" />
                  <YAxis />
                  <Tooltip />
                  <Legend />
                  <Line
                    type="monotone"
                    dataKey="average_risk_score"
                    stroke="#8884d8"
                    name="Average Risk Score"
                  />
                  <Line
                    type="monotone"
                    dataKey="default_rate"
                    stroke="#82ca9d"
                    name="Default Rate"
                  />
                </LineChart>
              </ResponsiveContainer>
            )}
          </Paper>
        </Grid>

        {/* Feature Performance */}
        <Grid item xs={12}>
          <Paper sx={{ p: 2, display: 'flex', flexDirection: 'column', height: 400 }}>
            <Typography component="h2" variant="h6" color="primary" gutterBottom>
              Feature Importance
            </Typography>
            {metrics && metrics.feature_importance && (
              <ResponsiveContainer width="100%" height={300}>
                <BarChart
                  data={metrics.feature_importance}
                  layout="vertical"
                >
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis type="number" />
                  <YAxis type="category" dataKey="name" />
                  <Tooltip />
                  <Bar dataKey="importance" fill="#8884d8" />
                </BarChart>
              </ResponsiveContainer>
            )}
          </Paper>
        </Grid>
      </Grid>
    </Box>
  );
};

export default Dashboard; 