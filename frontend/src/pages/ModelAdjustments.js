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
  Slider,
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

const ModelAdjustments = () => {
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [metrics, setMetrics] = useState(null);
  const [adjustmentHistory, setAdjustmentHistory] = useState([]);
  const [openDialog, setOpenDialog] = useState(false);
  const [newCutoff, setNewCutoff] = useState(0);
  const [rationale, setRationale] = useState('');
  const [adjustmentType, setAdjustmentType] = useState('cutoff');

  useEffect(() => {
    fetchModelData();
  }, []);

  const fetchModelData = async () => {
    try {
      setLoading(true);
      setError(null);

      // Fetch model metrics
      const metricsResponse = await fetch('/api/model/metrics');
      if (!metricsResponse.ok) {
        throw new Error('Failed to fetch model metrics');
      }
      const metricsData = await metricsResponse.json();
      setMetrics(metricsData);

      // Fetch adjustment history
      const historyResponse = await fetch('/api/model/adjustments');
      if (!historyResponse.ok) {
        throw new Error('Failed to fetch adjustment history');
      }
      const historyData = await historyResponse.json();
      setAdjustmentHistory(historyData);

    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleOpenDialog = () => {
    setOpenDialog(true);
  };

  const handleCloseDialog = () => {
    setOpenDialog(false);
    setNewCutoff(0);
    setRationale('');
  };

  const handleSubmitAdjustment = async () => {
    try {
      setLoading(true);
      setError(null);

      const response = await fetch('/api/model/adjustments', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          type: adjustmentType,
          new_value: { cutoff: newCutoff },
          rationale,
          created_by: 'admin', // Replace with actual user
        }),
      });

      if (!response.ok) {
        throw new Error('Failed to submit adjustment');
      }

      handleCloseDialog();
      fetchModelData(); // Refresh data

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

      {/* Model Performance Metrics */}
      <Grid item xs={12} md={6}>
        <Paper sx={{ p: 2, display: 'flex', flexDirection: 'column', height: 400 }}>
          <Typography variant="h6" gutterBottom>
            Model Performance
          </Typography>
          {metrics && (
            <ResponsiveContainer width="100%" height={300}>
              <LineChart data={metrics.metrics}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="evaluation_date" />
                <YAxis />
                <Tooltip />
                <Legend />
                <Line
                  type="monotone"
                  dataKey="value"
                  stroke="#8884d8"
                  name="AUC Score"
                />
              </LineChart>
            </ResponsiveContainer>
          )}
        </Paper>
      </Grid>

      {/* Current Model State */}
      <Grid item xs={12} md={6}>
        <Paper sx={{ p: 2, display: 'flex', flexDirection: 'column', height: 400 }}>
          <Typography variant="h6" gutterBottom>
            Current Model State
          </Typography>
          {metrics && (
            <Box>
              <Typography variant="h4" gutterBottom>
                {metrics.current_cutoff.toFixed(2)}
              </Typography>
              <Typography color="text.secondary">Current Cutoff Threshold</Typography>
              <Button
                variant="contained"
                onClick={handleOpenDialog}
                sx={{ mt: 2 }}
              >
                Adjust Model
              </Button>
            </Box>
          )}
        </Paper>
      </Grid>

      {/* Adjustment History */}
      <Grid item xs={12}>
        <Paper sx={{ p: 2 }}>
          <Typography variant="h6" gutterBottom>
            Adjustment History
          </Typography>
          <TableContainer>
            <Table>
              <TableHead>
                <TableRow>
                  <TableCell>Date</TableCell>
                  <TableCell>Type</TableCell>
                  <TableCell>Previous Value</TableCell>
                  <TableCell>New Value</TableCell>
                  <TableCell>Rationale</TableCell>
                  <TableCell>Status</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {adjustmentHistory.map((adjustment) => (
                  <TableRow key={adjustment.id}>
                    <TableCell>
                      {new Date(adjustment.created_at).toLocaleDateString()}
                    </TableCell>
                    <TableCell>{adjustment.type}</TableCell>
                    <TableCell>
                      {JSON.stringify(adjustment.previous_value)}
                    </TableCell>
                    <TableCell>
                      {JSON.stringify(adjustment.new_value)}
                    </TableCell>
                    <TableCell>{adjustment.rationale}</TableCell>
                    <TableCell>{adjustment.status}</TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </TableContainer>
        </Paper>
      </Grid>

      {/* Adjustment Dialog */}
      <Dialog open={openDialog} onClose={handleCloseDialog}>
        <DialogTitle>Adjust Model Parameters</DialogTitle>
        <DialogContent>
          <FormControl fullWidth sx={{ mt: 2 }}>
            <InputLabel>Adjustment Type</InputLabel>
            <Select
              value={adjustmentType}
              label="Adjustment Type"
              onChange={(e) => setAdjustmentType(e.target.value)}
            >
              <MenuItem value="cutoff">Cutoff Threshold</MenuItem>
              <MenuItem value="weights">Feature Weights</MenuItem>
            </Select>
          </FormControl>
          {adjustmentType === 'cutoff' && (
            <Box sx={{ mt: 2 }}>
              <Typography gutterBottom>New Cutoff Value</Typography>
              <Slider
                value={newCutoff}
                onChange={(e, value) => setNewCutoff(value)}
                min={0}
                max={1}
                step={0.01}
                valueLabelDisplay="auto"
              />
            </Box>
          )}
          <TextField
            fullWidth
            label="Rationale"
            multiline
            rows={4}
            value={rationale}
            onChange={(e) => setRationale(e.target.value)}
            sx={{ mt: 2 }}
          />
        </DialogContent>
        <DialogActions>
          <Button onClick={handleCloseDialog}>Cancel</Button>
          <Button
            onClick={handleSubmitAdjustment}
            variant="contained"
            disabled={loading || !rationale}
          >
            {loading ? <CircularProgress size={24} /> : 'Submit'}
          </Button>
        </DialogActions>
      </Dialog>
    </Grid>
  );
};

export default ModelAdjustments; 