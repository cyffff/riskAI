import React from 'react';
import { Alert, Collapse, IconButton } from '@mui/material';
import { Close as CloseIcon } from '@mui/icons-material';

export function MockDataAlert() {
  const [open, setOpen] = React.useState(true);
  
  return (
    <Collapse in={open}>
      <Alert 
        severity="info"
        action={
          <IconButton
            aria-label="close"
            color="inherit"
            size="small"
            onClick={() => setOpen(false)}
          >
            <CloseIcon fontSize="inherit" />
          </IconButton>
        }
        sx={{ mb: 2 }}
      >
        Using mock data - API connection unavailable. This is a development/demo mode.
      </Alert>
    </Collapse>
  );
} 