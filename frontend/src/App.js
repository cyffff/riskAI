import React from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';
import { Box, CssBaseline } from '@mui/material';
import Sidebar from './components/Sidebar/Sidebar';
import Dashboard from './pages/Dashboard';
import RiskAnalysis from './pages/RiskAnalysis';
import ModelAdjustments from './pages/ModelAdjustments';
import Features from './pages/feature-management/Features';
import SQLSets from './pages/feature-management/SQLSets';
import SQLStatements from './pages/feature-management/SQLStatements';
import AIAssistant from './pages/AIAssistant';

function App() {
  return (
    <Box sx={{ display: 'flex' }}>
      <CssBaseline />
      <Sidebar />
      <Box
        component="main"
        sx={{
          flexGrow: 1,
          p: 3,
          backgroundColor: '#fafafa',
          minHeight: '100vh',
        }}
      >
        <Routes>
          <Route path="/" element={<Navigate to="/dashboard" replace />} />
          <Route path="/dashboard" element={<Dashboard />} />
          <Route path="/risk-analysis" element={<RiskAnalysis />} />
          <Route path="/model-adjustments" element={<ModelAdjustments />} />
          <Route path="/feature-management/features" element={<Features />} />
          <Route path="/feature-management/sql-sets" element={<SQLSets />} />
          <Route path="/feature-management/sql-statements" element={<SQLStatements />} />
          <Route path="/ai-assistant" element={<AIAssistant />} />
        </Routes>
      </Box>
    </Box>
  );
}

export default App; 