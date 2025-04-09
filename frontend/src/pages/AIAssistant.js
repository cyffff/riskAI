import React, { useState, useRef, useEffect } from 'react';
import { 
  Box, 
  Typography, 
  Paper, 
  TextField, 
  Button, 
  List, 
  ListItem, 
  ListItemText, 
  Chip,
  Avatar,
  CircularProgress,
  Divider,
  Alert
} from '@mui/material';
import { 
  Send as SendIcon,
  SmartToy as AIIcon,
  Person as UserIcon
} from '@mui/icons-material';
import { featureApi } from '../services/api';
import { MockDataAlert } from '../components/MockDataAlert';

// Sample suggestions for the user
const SUGGESTIONS = [
  "What are the top 3 features by importance score?",
  "How do I interpret the Credit Utilization SQL query?",
  "Show me all features related to credit risk",
  "What parameters does the Suspicious Transactions query take?",
  "Explain the Income to Debt Ratio feature"
];

export default function AIAssistant() {
  const [messages, setMessages] = useState([
    { 
      role: 'assistant', 
      content: 'Hello! I\'m your Credit Risk AI Assistant. How can I help you today?' 
    }
  ]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [features, setFeatures] = useState([]);
  const [sqlStatements, setSqlStatements] = useState([]);
  const [dataLoaded, setDataLoaded] = useState(false);
  const [dataError, setDataError] = useState(null);
  const [usingMockData, setUsingMockData] = useState(false);
  
  const messagesEndRef = useRef(null);

  // Safely parse JSON string to object with error handling
  const safeJsonParse = (str) => {
    try {
      return typeof str === 'string' ? JSON.parse(str) : str;
    } catch (e) {
      console.error('Error parsing JSON:', e);
      return null;
    }
  };

  // Safely stringify object to JSON with error handling
  const safeJsonStringify = (obj) => {
    try {
      return JSON.stringify(obj, null, 2);
    } catch (e) {
      console.error('Error stringifying JSON:', e);
      return '{}';
    }
  };

  // Load data when component mounts
  useEffect(() => {
    const loadData = async () => {
      try {
        setLoading(true);
        setDataError(null);
        
        // If there's an environment variable for using mock data, this will return true
        const mockDataEnabled = process.env.REACT_APP_USE_MOCK_DATA === 'true' || true;
        setUsingMockData(mockDataEnabled);
        
        // Use Promise.allSettled for more resilient fetching
        const results = await Promise.allSettled([
          featureApi.getFeatures(),
          featureApi.getSqlStatements()
        ]);
        
        if (results[0].status === 'fulfilled') {
          // Check if data is not null and is iterable
          if (results[0].value && Array.isArray(results[0].value)) {
            setFeatures(results[0].value);
          } else {
            setFeatures([]);
            console.error("Features data is not in expected format:", results[0].value);
          }
        } else {
          console.error("Error fetching features:", results[0].reason);
          setFeatures([]);
        }
        
        if (results[1].status === 'fulfilled') {
          // Check if data is not null and is iterable
          if (results[1].value && Array.isArray(results[1].value)) {
            // Process SQL statements to ensure all required fields exist
            const processedStatements = results[1].value.map(stmt => {
              // Ensure statement has metadata property
              if (!stmt.metadata) stmt.metadata = {};
              
              // Ensure parameters exist
              if (!stmt.metadata.parameters) stmt.metadata.parameters = [];
              
              // Ensure statement property exists
              if (!stmt.statement) stmt.statement = "";
              
              return stmt;
            });
            setSqlStatements(processedStatements);
          } else {
            setSqlStatements([]);
            console.error("SQL statements data is not in expected format:", results[1].value);
          }
        } else {
          console.error("Error fetching SQL statements:", results[1].reason);
          setSqlStatements([]);
        }
        
        setDataLoaded(true);
      } catch (error) {
        console.error("Error loading data for AI Assistant:", error);
        setDataError("Failed to load necessary data. Using fallback options.");
        // Still mark as loaded so the interface is usable
        setDataLoaded(true);
      } finally {
        setLoading(false);
      }
    };
    
    loadData();
  }, []);

  // Scroll to bottom whenever messages change
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const handleInputChange = (e) => {
    setInput(e.target.value);
  };

  const handleSuggestionClick = (suggestion) => {
    setInput(suggestion);
  };

  const handleSubmit = async () => {
    if (!input.trim()) return;
    
    // Add user message
    const userMessage = { role: 'user', content: input };
    setMessages([...messages, userMessage]);
    setInput('');
    setLoading(true);
    
    // Simulate AI thinking
    await new Promise(resolve => setTimeout(resolve, 1000));
    
    // Generate response based on the query
    const response = generateResponse(input.trim());
    setMessages(prev => [...prev, { role: 'assistant', content: response }]);
    setLoading(false);
  };

  // Function to generate responses based on user input
  const generateResponse = (query) => {
    const queryLower = query.toLowerCase();
    
    try {
      // Top features
      if (queryLower.includes('top') && queryLower.includes('feature')) {
        if (!features || features.length === 0) {
          return "I don't have any feature data available at the moment.";
        }
        
        const sortedFeatures = [...features]
          .filter(f => typeof f.importance_score === 'number')
          .sort((a, b) => b.importance_score - a.importance_score);
          
        const topN = queryLower.includes('3') ? 3 : (queryLower.includes('5') ? 5 : 3);
        const topFeatures = sortedFeatures.slice(0, topN);
        
        if (topFeatures.length === 0) {
          return "I couldn't find features with valid importance scores.";
        }
        
        return `The top ${topN} features by importance score are:
${topFeatures.map((f, i) => `${i + 1}. ${f.name} (${f.importance_score})`).join('\n')}`;
      }
      
      // Credit Utilization SQL
      if (queryLower.includes('credit utilization') && queryLower.includes('sql')) {
        const creditUtilizationQuery = sqlStatements.find(s => s.name === 'Credit Utilization');
        if (creditUtilizationQuery && creditUtilizationQuery.statement) {
          const statement = typeof creditUtilizationQuery.statement === 'object' 
            ? safeJsonStringify(creditUtilizationQuery.statement)
            : creditUtilizationQuery.statement;
            
          return `The Credit Utilization SQL query calculates what portion of available credit a customer is using. 

It works by dividing the sum of balances by the sum of credit limits for all active accounts.

Here's the query:
\`\`\`sql
${statement}
\`\`\`

This query returns customers whose utilization ratio exceeds the threshold parameter (default is 0.7 or 70%).
Higher utilization ratios generally indicate higher credit risk.`;
        } else {
          return "I couldn't find the Credit Utilization SQL query in my data.";
        }
      }
      
      // Features related to credit risk
      if (queryLower.includes('feature') && queryLower.includes('credit risk')) {
        if (!features || features.length === 0) {
          return "I don't have any feature data available at the moment.";
        }
        
        const creditRiskFeatures = features.filter(f => {
          try {
            return (f.category === 'Credit Risk' || 
              (Array.isArray(f.tags) && f.tags.some(t => 
                t && t.name && t.name.toLowerCase().includes('credit')
              ))
            );
          } catch (e) {
            return false;
          }
        });
        
        if (creditRiskFeatures.length > 0) {
          return `I found ${creditRiskFeatures.length} features related to credit risk:
${creditRiskFeatures.map(f => `- ${f.name}: ${f.description || 'No description available'}`).join('\n')}`;
        } else {
          return "I couldn't find any features specifically categorized as Credit Risk.";
        }
      }
      
      // Suspicious Transactions parameters
      if (queryLower.includes('suspicious transactions') && (queryLower.includes('parameter') || queryLower.includes('param'))) {
        const suspiciousQuery = sqlStatements.find(s => s.name === 'Suspicious Transactions');
        
        if (!suspiciousQuery) {
          return "I couldn't find the Suspicious Transactions query in my data.";
        }
        
        const metadata = suspiciousQuery.metadata || {};
        const params = metadata.parameters || [];
        
        if (params.length > 0) {
          return `The Suspicious Transactions query takes ${params.length} parameters:
${params.map(p => `- ${p.name} (${p.type}): ${p.default_value || 'N/A'}${p.required ? ' (required)' : ''}`).join('\n')}

This query identifies transactions that are much larger than a customer's average transaction amount, which could indicate fraudulent activity.`;
        } else {
          return "The Suspicious Transactions query doesn't have any parameters defined.";
        }
      }
      
      // Explain Income to Debt Ratio
      if (queryLower.includes('income to debt ratio') || (queryLower.includes('debt') && queryLower.includes('ratio'))) {
        const feature = features.find(f => f.name === 'Income to Debt Ratio');
        if (feature) {
          return `The Income to Debt Ratio feature (importance score: ${feature.importance_score}) measures a customer's ability to manage debt.

Description: ${feature.description || 'No description available'}
Computation: ${feature.computation_logic || 'No computation logic available'}

This ratio is critical for assessing affordability. Lower ratios indicate higher risk as more of the customer's income is going toward debt payments.`;
        } else {
          return "I couldn't find the Income to Debt Ratio feature in my data.";
        }
      }
      
      // Default response if no specific match
      return `Thank you for your question about "${query}". I'm currently running in demo mode with limited functionality. I can help with questions about features, SQL queries, and risk metrics. Try asking about top features, credit utilization, or specific SQL parameters.`;
    } catch (error) {
      console.error("Error generating response:", error);
      return `I apologize, but I encountered an error while processing your question about "${query}". This could be due to data format issues. Please try a different question or one of the suggested topics.`;
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit();
    }
  };

  return (
    <Box>
      <Typography variant="h4" component="h1" gutterBottom>
        AI Assistant
      </Typography>
      
      {usingMockData && <MockDataAlert />}
      
      {dataError && (
        <Alert severity="warning" sx={{ mb: 2 }}>
          {dataError}
        </Alert>
      )}
      
      <Paper sx={{ p: 2, mb: 2, height: '60vh', display: 'flex', flexDirection: 'column' }}>
        {/* Message history */}
        <Box 
          sx={{ 
            flex: 1, 
            mb: 2, 
            overflowY: 'auto',
            bgcolor: '#f9f9f9',
            p: 2,
            borderRadius: 1
          }}
        >
          {messages.map((message, index) => (
            <Box 
              key={index} 
              sx={{ 
                display: 'flex', 
                mb: 2,
                justifyContent: message.role === 'user' ? 'flex-end' : 'flex-start'
              }}
            >
              {message.role === 'assistant' && (
                <Avatar sx={{ mr: 1, bgcolor: 'primary.main' }}>
                  <AIIcon />
                </Avatar>
              )}
              <Paper 
                elevation={1} 
                sx={{ 
                  p: 2, 
                  maxWidth: '70%',
                  bgcolor: message.role === 'user' ? 'primary.light' : 'white',
                  color: message.role === 'user' ? 'white' : 'text.primary'
                }}
              >
                <Typography 
                  variant="body1" 
                  sx={{ 
                    whiteSpace: 'pre-wrap' 
                  }}
                >
                  {message.content}
                </Typography>
              </Paper>
              {message.role === 'user' && (
                <Avatar sx={{ ml: 1, bgcolor: 'secondary.main' }}>
                  <UserIcon />
                </Avatar>
              )}
            </Box>
          ))}
          {loading && (
            <Box 
              sx={{ 
                display: 'flex', 
                mb: 2,
                justifyContent: 'flex-start'
              }}
            >
              <Avatar sx={{ mr: 1, bgcolor: 'primary.main' }}>
                <AIIcon />
              </Avatar>
              <Paper 
                elevation={1} 
                sx={{ 
                  p: 2, 
                  bgcolor: 'white',
                }}
              >
                <CircularProgress size={20} />
              </Paper>
            </Box>
          )}
          <div ref={messagesEndRef} />
        </Box>
        
        {/* Suggested questions */}
        <Box sx={{ mb: 2 }}>
          <Typography variant="subtitle2" gutterBottom>
            Suggested questions:
          </Typography>
          <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1 }}>
            {SUGGESTIONS.map((suggestion, index) => (
              <Chip 
                key={index} 
                label={suggestion} 
                onClick={() => handleSuggestionClick(suggestion)}
                variant="outlined"
                clickable
              />
            ))}
          </Box>
        </Box>
        
        <Divider sx={{ my: 2 }} />
        
        {/* Input area */}
        <Box sx={{ display: 'flex', alignItems: 'center' }}>
          <TextField
            fullWidth
            variant="outlined"
            placeholder="Ask me anything about credit risk..."
            value={input}
            onChange={handleInputChange}
            onKeyPress={handleKeyPress}
            disabled={loading || !dataLoaded}
            multiline
            maxRows={3}
            sx={{ mr: 1 }}
          />
          <Button 
            variant="contained" 
            color="primary" 
            endIcon={<SendIcon />}
            onClick={handleSubmit}
            disabled={loading || !input.trim() || !dataLoaded}
          >
            Send
          </Button>
        </Box>
      </Paper>
    </Box>
  );
} 