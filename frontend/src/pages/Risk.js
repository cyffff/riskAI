import React, { useState, useEffect } from 'react';
import {
  Grid,
  Paper,
  Typography,
  Box,
  TextField,
  Button,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  CircularProgress,
  Alert,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Card,
  CardContent,
  LinearProgress,
} from '@mui/material';
import {
  LineChart,
  Line,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell,
} from 'recharts';

const COLORS = ['#0088FE', '#00C49F', '#FFBB28', '#FF8042'];

const Risk = () => {
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [riskMetrics, setRiskMetrics] = useState(null);
  const [riskTrends, setRiskTrends] = useState([]);
  const [userSegments, setUserSegments] = useState([]);
  const [openAnalysisDialog, setOpenAnalysisDialog] = useState(false);
  const [selectedUserId, setSelectedUserId] = useState('');
  const [analysisPeriod, setAnalysisPeriod] = useState('30d');

  useEffect(() => {
    fetchRiskData();
  }, []);

  const fetchRiskData = async () => {
    try {
      setLoading(true);
      setError(null);

      // Fetch risk metrics
      const metricsResponse = await fetch('/api/risk/metrics');
      if (!metricsResponse.ok) {
        throw new Error('Failed to fetch risk metrics');
      }
      const metricsData = await metricsResponse.json();
      setRiskMetrics(metricsData);

      // Fetch risk trends
      const trendsResponse = await fetch('/api/risk/trends');
      if (!trendsResponse.ok) {
        throw new Error('Failed to fetch risk trends');
      }
      const trendsData = await trendsResponse.json();
      setRiskTrends(trendsData);

      // Fetch user segments
      const segmentsResponse = await fetch('/api/risk/segments');
      if (!segmentsResponse.ok) {
        throw new Error('Failed to fetch user segments');
      }
      const segmentsData = await segmentsResponse.json();
      setUserSegments(segmentsData);

    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleOpenAnalysisDialog = () => {
    setOpenAnalysisDialog(true);
  };

  const handleCloseAnalysisDialog = () => {
    setOpenAnalysisDialog(false);
    setSelectedUserId('');
  };

  const handleAnalyzeUser = async () => {
    try {
      setLoading(true);
      setError(null);

      const response = await fetch(`/api/risk/analyze/${selectedUserId}?period=${analysisPeriod}`);
      if (!response.ok) {
        throw new Error('Failed to analyze user risk');
      }

      handleCloseAnalysisDialog();
      fetchRiskData(); // Refresh data

    } catch (err) {
      setError(err.message);
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
    <Grid container spacing={3}>
      {error && (
        <Grid item xs={12}>
          <Alert severity="error">{error}</Alert>
        </Grid>
      )}

      {/* Key Risk Metrics */}
      <Grid item xs={12} md={3}>
        <Card>
          <CardContent>
            <Typography color="textSecondary" gutterBottom>
              Overall Risk Score
            </Typography>
            <Typography variant="h4" component="div">
              {riskMetrics?.overall_risk_score.toFixed(1)}
            </Typography>
            <LinearProgress
              variant="determinate"
              value={riskMetrics?.overall_risk_score * 100}
              sx={{ mt: 1 }}
            />
          </CardContent>
        </Card>
      </Grid>

      <Grid item xs={12} md={3}>
        <Card>
          <CardContent>
            <Typography color="textSecondary" gutterBottom>
              Default Rate
            </Typography>
            <Typography variant="h4" component="div">
              {(riskMetrics?.default_rate * 100).toFixed(1)}%
            </Typography>
            <LinearProgress
              variant="determinate"
              value={riskMetrics?.default_rate * 100}
              color="error"
              sx={{ mt: 1 }}
            />
          </CardContent>
        </Card>
      </Grid>

      <Grid item xs={12} md={3}>
        <Card>
          <CardContent>
            <Typography color="textSecondary" gutterBottom>
              Approval Rate
            </Typography>
            <Typography variant="h4" component="div">
              {(riskMetrics?.approval_rate * 100).toFixed(1)}%
            </Typography>
            <LinearProgress
              variant="determinate"
              value={riskMetrics?.approval_rate * 100}
              color="success"
              sx={{ mt: 1 }}
            />
          </CardContent>
        </Card>
      </Grid>

      <Grid item xs={12} md={3}>
        <Card>
          <CardContent>
            <Typography color="textSecondary" gutterBottom>
              Average Risk Score
            </Typography>
            <Typography variant="h4" component="div">
              {riskMetrics?.average_risk_score.toFixed(1)}
            </Typography>
            <LinearProgress
              variant="determinate"
              value={riskMetrics?.average_risk_score * 100}
              sx={{ mt: 1 }}
            />
          </CardContent>
        </Card>
      </Grid>

      {/* Risk Trends */}
      <Grid item xs={12} md={8}>
        <Paper sx={{ p: 2, display: 'flex', flexDirection: 'column', height: 400 }}>
          <Typography variant="h6" gutterBottom>
            Risk Score Trends
          </Typography>
          <ResponsiveContainer width="100%" height={300}>
            <LineChart data={riskTrends}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="date" />
              <YAxis />
              <Tooltip />
              <Legend />
              <Line
                type="monotone"
                dataKey="risk_score"
                stroke="#8884d8"
                name="Risk Score"
              />
              <Line
                type="monotone"
                dataKey="default_rate"
                stroke="#ff7300"
                name="Default Rate"
              />
            </LineChart>
          </ResponsiveContainer>
        </Paper>
      </Grid>

      {/* User Segments */}
      <Grid item xs={12} md={4}>
        <Paper sx={{ p: 2, display: 'flex', flexDirection: 'column', height: 400 }}>
          <Typography variant="h6" gutterBottom>
            User Segments
          </Typography>
          <ResponsiveContainer width="100%" height={300}>
            <PieChart>
              <Pie
                data={userSegments}
                dataKey="value"
                nameKey="name"
                cx="50%"
                cy="50%"
                outerRadius={100}
                label
              >
                {userSegments.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                ))}
              </Pie>
              <Tooltip />
              <Legend />
            </PieChart>
          </ResponsiveContainer>
        </Paper>
      </Grid>

      {/* Risk Analysis Actions */}
      <Grid item xs={12}>
        <Paper sx={{ p: 2 }}>
          <Box display="flex" justifyContent="space-between" alignItems="center">
            <Typography variant="h6">Risk Analysis</Typography>
            <Button
              variant="contained"
              onClick={handleOpenAnalysisDialog}
            >
              Analyze User Risk
            </Button>
          </Box>
        </Paper>
      </Grid>

      {/* User Analysis Dialog */}
      <Dialog open={openAnalysisDialog} onClose={handleCloseAnalysisDialog}>
        <DialogTitle>Analyze User Risk</DialogTitle>
        <DialogContent>
          <TextField
            fullWidth
            label="User ID"
            value={selectedUserId}
            onChange={(e) => setSelectedUserId(e.target.value)}
            sx={{ mt: 2 }}
          />
          <FormControl fullWidth sx={{ mt: 2 }}>
            <InputLabel>Analysis Period</InputLabel>
            <Select
              value={analysisPeriod}
              label="Analysis Period"
              onChange={(e) => setAnalysisPeriod(e.target.value)}
            >
              <MenuItem value="30d">Last 30 Days</MenuItem>
              <MenuItem value="90d">Last 90 Days</MenuItem>
              <MenuItem value="180d">Last 180 Days</MenuItem>
              <MenuItem value="1y">Last Year</MenuItem>
            </Select>
          </FormControl>
        </DialogContent>
        <DialogActions>
          <Button onClick={handleCloseAnalysisDialog}>Cancel</Button>
          <Button
            onClick={handleAnalyzeUser}
            variant="contained"
            disabled={loading || !selectedUserId}
          >
            {loading ? <CircularProgress size={24} /> : 'Analyze'}
          </Button>
        </DialogActions>
      </Dialog>
    </Grid>
  );
};

export default Risk; 