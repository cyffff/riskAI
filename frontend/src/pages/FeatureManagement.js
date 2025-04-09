import React, { useState, useEffect } from 'react';
import {
  Box,
  Container,
  Typography,
  Paper,
  Tabs,
  Tab,
  CircularProgress,
  Alert,
} from '@mui/material';
import { FeatureList } from '../components/FeatureList';
import { SQLSetList } from '../components/SQLSetList';
import { SQLStatementList } from '../components/SQLStatementList';
import { useFeatureManagement } from '../hooks/useFeatureManagement';

function TabPanel({ children, value, index }) {
  return (
    <div role="tabpanel" hidden={value !== index}>
      {value === index && <Box sx={{ p: 3 }}>{children}</Box>}
    </div>
  );
}

export default function FeatureManagement() {
  const [tabValue, setTabValue] = useState(0);
  const {
    features,
    sqlSets,
    sqlStatements,
    loading,
    error,
    refreshData,
  } = useFeatureManagement();

  const handleTabChange = (event, newValue) => {
    setTabValue(newValue);
  };

  if (loading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="60vh">
        <CircularProgress />
      </Box>
    );
  }

  if (error) {
    return (
      <Container maxWidth="lg" sx={{ mt: 4 }}>
        <Alert severity="error">{error}</Alert>
      </Container>
    );
  }

  return (
    <Container maxWidth="lg" sx={{ mt: 4 }}>
      <Typography variant="h4" gutterBottom>
        Feature Management
      </Typography>
      <Paper sx={{ width: '100%', mb: 2 }}>
        <Tabs
          value={tabValue}
          onChange={handleTabChange}
          indicatorColor="primary"
          textColor="primary"
        >
          <Tab label="Features" />
          <Tab label="SQL Sets" />
          <Tab label="SQL Statements" />
        </Tabs>

        <TabPanel value={tabValue} index={0}>
          <FeatureList 
            features={features} 
            onUpdate={refreshData}
            sqlSets={sqlSets}
            sqlStatements={sqlStatements}
          />
        </TabPanel>

        <TabPanel value={tabValue} index={1}>
          <SQLSetList 
            sqlSets={sqlSets} 
            onUpdate={refreshData} 
          />
        </TabPanel>

        <TabPanel value={tabValue} index={2}>
          <SQLStatementList 
            sqlStatements={sqlStatements}
            sqlSets={sqlSets}
            onUpdate={refreshData}
          />
        </TabPanel>
      </Paper>
    </Container>
  );
} 