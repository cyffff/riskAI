import React, { useState } from 'react';
import {
  Box,
  Drawer,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  ListItemButton,
  Collapse,
  Typography,
} from '@mui/material';
import {
  Dashboard as DashboardIcon,
  TrendingUp as RiskAnalysisIcon,
  Settings as ModelAdjustmentsIcon,
  List as FeatureIcon,
  Storage as SqlIcon,
  Code as SqlSetIcon,
  SmartToy as AIAssistantIcon,
  ExpandLess,
  ExpandMore,
} from '@mui/icons-material';
import { useNavigate, useLocation } from 'react-router-dom';

const drawerWidth = 240;

const menuItems = [
  { path: '/dashboard', label: 'Dashboard', icon: DashboardIcon },
  { path: '/risk-analysis', label: 'Risk Analysis', icon: RiskAnalysisIcon },
  { path: '/model-adjustments', label: 'Model Adjustments', icon: ModelAdjustmentsIcon },
  {
    label: 'Feature Management',
    icon: FeatureIcon,
    subItems: [
      { path: '/feature-management/features', label: 'Features', icon: FeatureIcon },
      { path: '/feature-management/sql-sets', label: 'SQL Sets', icon: SqlSetIcon },
      { path: '/feature-management/sql-statements', label: 'SQL Statements', icon: SqlIcon },
    ],
  },
  { path: '/ai-assistant', label: 'AI Assistant', icon: AIAssistantIcon },
];

export default function Sidebar() {
  const navigate = useNavigate();
  const location = useLocation();
  const [featureManagementOpen, setFeatureManagementOpen] = useState(true);

  const handleFeatureManagementClick = () => {
    setFeatureManagementOpen(!featureManagementOpen);
    if (!featureManagementOpen) {
      // If we're opening the menu, navigate to the first item by default
      navigate('/feature-management/features');
    }
  };

  const isSelected = (path) => location.pathname === path;
  const isFeatureManagementActive = location.pathname.startsWith('/feature-management');

  return (
    <Drawer
      variant="permanent"
      sx={{
        width: drawerWidth,
        flexShrink: 0,
        '& .MuiDrawer-paper': {
          width: drawerWidth,
          boxSizing: 'border-box',
          backgroundColor: '#f5f5f5',
          borderRight: '1px solid rgba(0, 0, 0, 0.12)',
        },
      }}
    >
      <Box sx={{ overflow: 'auto', height: '100%' }}>
        <Box sx={{ p: 2, borderBottom: '1px solid rgba(0, 0, 0, 0.12)' }}>
          <Typography variant="h6" component="div" sx={{ color: '#1976d2' }}>
            Risk AI Assistant
          </Typography>
        </Box>
        <List>
          {menuItems.map((item) => (
            item.subItems ? (
              <React.Fragment key={item.label}>
                <ListItemButton
                  onClick={handleFeatureManagementClick}
                  selected={isFeatureManagementActive}
                  sx={{
                    '&.Mui-selected': {
                      backgroundColor: 'rgba(25, 118, 210, 0.08)',
                    },
                  }}
                >
                  <ListItemIcon>
                    <item.icon color={isFeatureManagementActive ? 'primary' : 'inherit'} />
                  </ListItemIcon>
                  <ListItemText primary={item.label} />
                  {featureManagementOpen ? <ExpandLess /> : <ExpandMore />}
                </ListItemButton>
                <Collapse in={featureManagementOpen} timeout="auto" unmountOnExit>
                  <List component="div" disablePadding>
                    {item.subItems.map((subItem) => (
                      <ListItemButton
                        key={subItem.path}
                        sx={{ pl: 4 }}
                        selected={isSelected(subItem.path)}
                        onClick={() => navigate(subItem.path)}
                      >
                        <ListItemIcon>
                          <subItem.icon
                            color={isSelected(subItem.path) ? 'primary' : 'inherit'}
                            fontSize="small"
                          />
                        </ListItemIcon>
                        <ListItemText
                          primary={subItem.label}
                          primaryTypographyProps={{ fontSize: '0.9rem' }}
                        />
                      </ListItemButton>
                    ))}
                  </List>
                </Collapse>
              </React.Fragment>
            ) : (
              <ListItemButton
                key={item.path}
                selected={isSelected(item.path)}
                onClick={() => navigate(item.path)}
                sx={{
                  '&.Mui-selected': {
                    backgroundColor: 'rgba(25, 118, 210, 0.08)',
                  },
                }}
              >
                <ListItemIcon>
                  <item.icon color={isSelected(item.path) ? 'primary' : 'inherit'} />
                </ListItemIcon>
                <ListItemText primary={item.label} />
              </ListItemButton>
            )
          ))}
        </List>
      </Box>
    </Drawer>
  );
} 