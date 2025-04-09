import React from 'react';
import { Grid, Paper, Typography, Box } from '@mui/material';
import ChatInterface from '../components/ChatInterface';

const ChatBot = () => {
  return (
    <Grid container spacing={3}>
      <Grid item xs={12}>
        <Paper sx={{ p: 2, mb: 3 }}>
          <Typography variant="h5" gutterBottom>
            Credit Risk AI Assistant Chat
          </Typography>
          <Typography variant="body1" color="text.secondary">
            Ask questions about risk metrics, model performance, or request user risk analysis.
          </Typography>
        </Paper>
      </Grid>
      
      <Grid item xs={12} md={8}>
        <Box sx={{ height: 'calc(100vh - 240px)', minHeight: '500px' }}>
          <ChatInterface />
        </Box>
      </Grid>
      
      <Grid item xs={12} md={4}>
        <Paper sx={{ p: 2, height: 'calc(100vh - 240px)', minHeight: '500px', overflow: 'auto' }}>
          <Typography variant="h6" gutterBottom>
            Example Questions
          </Typography>
          <Box component="ul" sx={{ pl: 2 }}>
            <Box component="li" sx={{ mb: 1 }}>
              <Typography variant="body2">
                "What's our current model performance?"
              </Typography>
            </Box>
            <Box component="li" sx={{ mb: 1 }}>
              <Typography variant="body2">
                "Analyze risk for user 12345"
              </Typography>
            </Box>
            <Box component="li" sx={{ mb: 1 }}>
              <Typography variant="body2">
                "What's our approval rate for medium risk customers?"
              </Typography>
            </Box>
            <Box component="li" sx={{ mb: 1 }}>
              <Typography variant="body2">
                "Explain how risk scores are calculated"
              </Typography>
            </Box>
            <Box component="li" sx={{ mb: 1 }}>
              <Typography variant="body2">
                "Which features are most important for risk assessment?"
              </Typography>
            </Box>
            <Box component="li" sx={{ mb: 1 }}>
              <Typography variant="body2">
                "Why was user 67890 rejected?"
              </Typography>
            </Box>
            <Box component="li" sx={{ mb: 1 }}>
              <Typography variant="body2">
                "Set cutoff threshold to 0.75"
              </Typography>
            </Box>
          </Box>
          
          <Typography variant="h6" gutterBottom sx={{ mt: 4 }}>
            Capabilities
          </Typography>
          <Box component="ul" sx={{ pl: 2 }}>
            <Box component="li" sx={{ mb: 1 }}>
              <Typography variant="body2">
                Risk analysis for specific users
              </Typography>
            </Box>
            <Box component="li" sx={{ mb: 1 }}>
              <Typography variant="body2">
                Model performance metrics and trends
              </Typography>
            </Box>
            <Box component="li" sx={{ mb: 1 }}>
              <Typography variant="body2">
                Explanation of risk factors and scoring
              </Typography>
            </Box>
            <Box component="li" sx={{ mb: 1 }}>
              <Typography variant="body2">
                Feature importance information
              </Typography>
            </Box>
            <Box component="li" sx={{ mb: 1 }}>
              <Typography variant="body2">
                Model parameter adjustments
              </Typography>
            </Box>
            <Box component="li" sx={{ mb: 1 }}>
              <Typography variant="body2">
                Approval rate statistics by risk level
              </Typography>
            </Box>
          </Box>
        </Paper>
      </Grid>
    </Grid>
  );
};

export default ChatBot; 