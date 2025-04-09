import React, { useState } from 'react';
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
} from '@mui/material';
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from 'recharts';

const RiskAnalysis = () => {
  const [userId, setUserId] = useState('');
  const [period, setPeriod] = useState('30d');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [analysis, setAnalysis] = useState(null);
  const [transactionHistory, setTransactionHistory] = useState([]);

  const handleAnalyze = async () => {
    if (!userId) {
      setError('Please enter a user ID');
      return;
    }

    try {
      setLoading(true);
      setError(null);

      // Fetch risk analysis
      const analysisResponse = await fetch(`/api/risk-analysis/${userId}?period=${period}`);
      if (!analysisResponse.ok) {
        throw new Error('Failed to fetch risk analysis');
      }
      const analysisData = await analysisResponse.json();
      setAnalysis(analysisData);

      // Fetch transaction history
      const transactionsResponse = await fetch(`/api/risk-analysis/${userId}/transactions?period=${period}`);
      if (!transactionsResponse.ok) {
        throw new Error('Failed to fetch transaction history');
      }
      const transactionsData = await transactionsResponse.json();
      setTransactionHistory(transactionsData);

    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <Grid container spacing={3}>
      {/* Input Section */}
      <Grid item xs={12}>
        <Paper sx={{ p: 2 }}>
          <Typography variant="h6" gutterBottom>
            Risk Analysis
          </Typography>
          <Grid container spacing={2} alignItems="center">
            <Grid item xs={12} md={4}>
              <TextField
                fullWidth
                label="User ID"
                value={userId}
                onChange={(e) => setUserId(e.target.value)}
                error={!!error && !userId}
                helperText={error && !userId ? error : ''}
              />
            </Grid>
            <Grid item xs={12} md={4}>
              <FormControl fullWidth>
                <InputLabel>Analysis Period</InputLabel>
                <Select
                  value={period}
                  label="Analysis Period"
                  onChange={(e) => setPeriod(e.target.value)}
                >
                  <MenuItem value="30d">Last 30 Days</MenuItem>
                  <MenuItem value="90d">Last 90 Days</MenuItem>
                  <MenuItem value="180d">Last 180 Days</MenuItem>
                  <MenuItem value="1y">Last Year</MenuItem>
                </Select>
              </FormControl>
            </Grid>
            <Grid item xs={12} md={4}>
              <Button
                fullWidth
                variant="contained"
                onClick={handleAnalyze}
                disabled={loading}
              >
                {loading ? <CircularProgress size={24} /> : 'Analyze Risk'}
              </Button>
            </Grid>
          </Grid>
        </Paper>
      </Grid>

      {error && (
        <Grid item xs={12}>
          <Alert severity="error">{error}</Alert>
        </Grid>
      )}

      {analysis && (
        <>
          {/* Risk Summary */}
          <Grid item xs={12} md={4}>
            <Paper sx={{ p: 2, display: 'flex', flexDirection: 'column', height: 240 }}>
              <Typography variant="h6" gutterBottom>
                Risk Summary
              </Typography>
              <Box>
                <Typography variant="h4" gutterBottom>
                  {analysis.risk_score.toFixed(1)}
                </Typography>
                <Typography color="text.secondary">Risk Score</Typography>
                <Typography
                  variant="h5"
                  gutterBottom
                  sx={{ mt: 2 }}
                  color={
                    analysis.risk_level === 'low'
                      ? 'success.main'
                      : analysis.risk_level === 'medium'
                      ? 'warning.main'
                      : 'error.main'
                  }
                >
                  {analysis.risk_level.toUpperCase()} Risk
                </Typography>
              </Box>
            </Paper>
          </Grid>

          {/* Transaction Metrics */}
          <Grid item xs={12} md={4}>
            <Paper sx={{ p: 2, display: 'flex', flexDirection: 'column', height: 240 }}>
              <Typography variant="h6" gutterBottom>
                Transaction Metrics
              </Typography>
              <Box>
                <Typography variant="h4" gutterBottom>
                  {analysis.transactions_summary.total_amount.toLocaleString()}
                </Typography>
                <Typography color="text.secondary">Total Transaction Amount</Typography>
                <Typography variant="h4" gutterBottom sx={{ mt: 2 }}>
                  {analysis.transactions_summary.count}
                </Typography>
                <Typography color="text.secondary">Total Transactions</Typography>
              </Box>
            </Paper>
          </Grid>

          {/* Credit Metrics */}
          <Grid item xs={12} md={4}>
            <Paper sx={{ p: 2, display: 'flex', flexDirection: 'column', height: 240 }}>
              <Typography variant="h6" gutterBottom>
                Credit Metrics
              </Typography>
              <Box>
                <Typography variant="h4" gutterBottom>
                  {analysis.credit_inquiries_summary.count}
                </Typography>
                <Typography color="text.secondary">Credit Inquiries</Typography>
                <Typography variant="h4" gutterBottom sx={{ mt: 2 }}>
                  {(
                    (analysis.credit_inquiries_summary.by_status.approved /
                      analysis.credit_inquiries_summary.count) *
                    100
                  ).toFixed(1)}%
                </Typography>
                <Typography color="text.secondary">Approval Rate</Typography>
              </Box>
            </Paper>
          </Grid>

          {/* Risk Score Trend */}
          <Grid item xs={12}>
            <Paper sx={{ p: 2, display: 'flex', flexDirection: 'column', height: 400 }}>
              <Typography variant="h6" gutterBottom>
                Risk Score Trend
              </Typography>
              <ResponsiveContainer width="100%" height={300}>
                <LineChart data={transactionHistory}>
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
                    dataKey="transaction_amount"
                    stroke="#82ca9d"
                    name="Transaction Amount"
                  />
                </LineChart>
              </ResponsiveContainer>
            </Paper>
          </Grid>

          {/* Transaction History */}
          <Grid item xs={12}>
            <Paper sx={{ p: 2 }}>
              <Typography variant="h6" gutterBottom>
                Transaction History
              </Typography>
              <TableContainer>
                <Table>
                  <TableHead>
                    <TableRow>
                      <TableCell>Date</TableCell>
                      <TableCell>Type</TableCell>
                      <TableCell>Amount</TableCell>
                      <TableCell>Status</TableCell>
                    </TableRow>
                  </TableHead>
                  <TableBody>
                    {transactionHistory.map((transaction, index) => (
                      <TableRow key={index}>
                        <TableCell>
                          {new Date(transaction.date).toLocaleDateString()}
                        </TableCell>
                        <TableCell>{transaction.type}</TableCell>
                        <TableCell>
                          {transaction.amount.toLocaleString()}
                        </TableCell>
                        <TableCell>{transaction.status}</TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </TableContainer>
            </Paper>
          </Grid>
        </>
      )}
    </Grid>
  );
};

export default RiskAnalysis; 