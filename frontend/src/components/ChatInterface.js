import React, { useState, useEffect, useRef } from 'react';
import {
  Box,
  Paper,
  TextField,
  IconButton,
  Typography,
  List,
  ListItem,
  ListItemText,
  CircularProgress,
  Divider,
} from '@mui/material';
import SendIcon from '@mui/icons-material/Send';
import ChatBubbleOutlineIcon from '@mui/icons-material/ChatBubbleOutline';
import PersonIcon from '@mui/icons-material/Person';
import axios from 'axios';

const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000/api';

const ChatInterface = () => {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [sessionId, setSessionId] = useState(null);
  const messageEndRef = useRef(null);

  useEffect(() => {
    // Generate a random session ID on component mount
    const newSessionId = `user-${Math.random().toString(36).substring(2, 10)}`;
    setSessionId(newSessionId);

    // Add initial bot greeting
    setMessages([
      {
        text: "Hello! I'm your Credit Risk AI Assistant. How can I help you today?",
        sender: 'bot',
        timestamp: new Date().toISOString(),
      },
    ]);
  }, []);

  useEffect(() => {
    // Scroll to the bottom when messages change
    messageEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const sendMessage = async () => {
    if (!input.trim()) return;

    const userMessage = {
      text: input,
      sender: 'user',
      timestamp: new Date().toISOString(),
    };

    setMessages((prev) => [...prev, userMessage]);
    setInput('');
    setLoading(true);
    setError(null);

    try {
      const response = await axios.post(`${API_URL}/chat/message`, {
        message: input,
        sender_id: sessionId,
      }, {
        timeout: 10000, // 10 second timeout
        retries: 3, // Allow 3 retries
      });

      // Handle the bot responses
      const botResponses = response.data.responses || [];
      
      if (botResponses.length === 0) {
        // Add default response if none returned
        setMessages((prev) => [
          ...prev,
          {
            text: "I'm not sure how to respond to that. Could you try phrasing your question differently?",
            sender: 'bot',
            timestamp: new Date().toISOString(),
          },
        ]);
      } else {
        // Add each bot response as a separate message
        botResponses.forEach((resp) => {
          setMessages((prev) => [
            ...prev,
            {
              text: resp.text,
              sender: 'bot',
              timestamp: new Date().toISOString(),
              buttons: resp.buttons,
              image: resp.image,
            },
          ]);
        });
      }
    } catch (err) {
      console.error('Error sending message:', err);
      let errorMessage = 'Sorry, I encountered an error. Please try again or check your connection.';
      
      if (err.response) {
        // Server responded with error
        if (err.response.status === 404) {
          errorMessage = 'The chat service is currently unavailable. Please try again later.';
        } else if (err.response.status === 400) {
          errorMessage = 'Invalid request. Please try again with a different question.';
        } else if (err.response.status >= 500) {
          errorMessage = 'The server encountered an error. Please try again later.';
        }
      } else if (err.code === 'ECONNABORTED') {
        errorMessage = 'The request timed out. Please try again.';
      } else if (!navigator.onLine) {
        errorMessage = 'You appear to be offline. Please check your internet connection.';
      }
      
      setError(errorMessage);
      setMessages((prev) => [
        ...prev,
        {
          text: errorMessage,
          sender: 'bot',
          timestamp: new Date().toISOString(),
          isError: true,
        },
      ]);
    } finally {
      setLoading(false);
    }
  };

  const handleKeyPress = (event) => {
    if (event.key === 'Enter') {
      sendMessage();
    }
  };

  const handleButtonClick = (buttonText) => {
    setInput(buttonText);
    setTimeout(() => {
      sendMessage();
    }, 100);
  };

  return (
    <Paper
      elevation={3}
      sx={{
        height: '100%',
        display: 'flex',
        flexDirection: 'column',
        overflow: 'hidden',
      }}
    >
      <Box
        sx={{
          p: 2,
          backgroundColor: '#1976d2',
          color: 'white',
          display: 'flex',
          alignItems: 'center',
        }}
      >
        <ChatBubbleOutlineIcon sx={{ mr: 1 }} />
        <Typography variant="h6">Credit Risk Assistant</Typography>
      </Box>
      <Divider />
      <List
        sx={{
          flex: 1,
          overflow: 'auto',
          p: 2,
          backgroundColor: '#f5f5f5',
        }}
      >
        {messages.map((message, index) => (
          <ListItem
            key={index}
            sx={{
              display: 'flex',
              justifyContent: message.sender === 'user' ? 'flex-end' : 'flex-start',
              mb: 1,
            }}
          >
            <Paper
              elevation={1}
              sx={{
                p: 2,
                maxWidth: '70%',
                backgroundColor: message.sender === 'user' ? '#e3f2fd' : 'white',
                borderRadius: 2,
                position: 'relative',
              }}
            >
              <Box
                sx={{
                  display: 'flex',
                  alignItems: 'flex-start',
                  mb: 1,
                }}
              >
                {message.sender === 'user' ? (
                  <PersonIcon fontSize="small" sx={{ mr: 1, color: '#1976d2' }} />
                ) : (
                  <ChatBubbleOutlineIcon fontSize="small" sx={{ mr: 1, color: '#1976d2' }} />
                )}
                <Typography
                  variant="body1"
                  sx={{
                    color: message.isError ? 'error.main' : 'text.primary',
                    whiteSpace: 'pre-line',
                  }}
                >
                  {message.text}
                </Typography>
              </Box>

              {message.image && (
                <Box sx={{ mt: 1 }}>
                  <img
                    src={message.image}
                    alt="Bot message attachment"
                    style={{ maxWidth: '100%', borderRadius: 4 }}
                  />
                </Box>
              )}

              {message.buttons && message.buttons.length > 0 && (
                <Box sx={{ mt: 1, display: 'flex', flexWrap: 'wrap', gap: 1 }}>
                  {message.buttons.map((button, buttonIndex) => (
                    <Box
                      key={buttonIndex}
                      sx={{
                        p: 1,
                        borderRadius: 1,
                        backgroundColor: '#e0e0e0',
                        cursor: 'pointer',
                        '&:hover': {
                          backgroundColor: '#d0d0d0',
                        },
                      }}
                      onClick={() => handleButtonClick(button.payload || button.title)}
                    >
                      <Typography variant="body2">{button.title}</Typography>
                    </Box>
                  ))}
                </Box>
              )}

              <Typography
                variant="caption"
                sx={{ position: 'absolute', right: 8, bottom: 4, color: 'text.secondary' }}
              >
                {new Date(message.timestamp).toLocaleTimeString([], {
                  hour: '2-digit',
                  minute: '2-digit',
                })}
              </Typography>
            </Paper>
          </ListItem>
        ))}
        {loading && (
          <ListItem
            sx={{
              display: 'flex',
              justifyContent: 'flex-start',
              mb: 1,
            }}
          >
            <Paper
              elevation={1}
              sx={{
                p: 2,
                backgroundColor: 'white',
                borderRadius: 2,
              }}
            >
              <Box sx={{ display: 'flex', alignItems: 'center' }}>
                <CircularProgress size={20} sx={{ mr: 1 }} />
                <Typography variant="body2">Assistant is typing...</Typography>
              </Box>
            </Paper>
          </ListItem>
        )}
        <div ref={messageEndRef} />
      </List>
      <Divider />
      <Box
        sx={{
          p: 2,
          backgroundColor: 'white',
          display: 'flex',
          alignItems: 'center',
        }}
      >
        <TextField
          fullWidth
          placeholder="Type your message..."
          variant="outlined"
          size="small"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyPress={handleKeyPress}
          disabled={loading}
          sx={{ mr: 1 }}
        />
        <IconButton
          color="primary"
          onClick={sendMessage}
          disabled={loading || !input.trim()}
          aria-label="send message"
        >
          <SendIcon />
        </IconButton>
      </Box>
    </Paper>
  );
};

export default ChatInterface; 