import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import {
  Drawer,
  List,
  ListItem,
  ListItemText,
  IconButton,
  Toolbar,
  AppBar,
  Typography,
  Button,
  Box,
} from '@mui/material';
import MenuIcon from '@mui/icons-material/Menu';
import { SERVER_URL } from '../App';

const Navigation = ({ roles, setRoles }) => {
  const navigate = useNavigate();
  const [isDrawerOpen, setIsDrawerOpen] = useState(false);

  function handleLogout() {
    return fetch(`${SERVER_URL}/logout`, {
      method: 'POST',
      credentials: 'include',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({}),
    }).then(() => {
      setRoles([]);
      navigate('/authentication');
    });
  }

  const toggleDrawer = (open) => (event) => {
    if (event.type === 'keydown' && (event.key === 'Tab' || event.key === 'Shift')) {
      return;
    }
    setIsDrawerOpen(open);
  };

  return (
    <div>
      <AppBar position="static" color="primary">
        <Toolbar>
          <IconButton edge="start" color="inherit" aria-label="menu" onClick={toggleDrawer(true)}>
            <MenuIcon />
          </IconButton>
          <Typography variant="h6" sx={{ flexGrow: 1 }}>
            Secure The Glow Admin
          </Typography>
        </Toolbar>
      </AppBar>
      <Drawer anchor="left" open={isDrawerOpen} onClose={toggleDrawer(false)}>
        <Box
          sx={{ width: 250 }}
          role="presentation"
          onClick={toggleDrawer(false)}
          onKeyDown={toggleDrawer(false)}
        >
          <List>
            {/* Business Manager Role */}
            {roles.includes('business-manager') && (
              <ListItem button component={Link} to="/create_product">
                <ListItemText primary="Create Product" />
              </ListItem>
            )}

            {/* Customer Service Specialist Role */}
            {roles.includes('customer-service-specialist') && (
              <>
                <ListItem button component={Link} to="/create_order">
                  <ListItemText primary="Create Order" />
                </ListItem>
                <ListItem button component={Link} to="/orders">
                  <ListItemText primary="View Orders" />
                </ListItem>
                <ListItem button component={Link} to="/invoices">
                  <ListItemText primary="Invoices" />
                </ListItem>
                <ListItem button component={Link} to="/returns">
                  <ListItemText primary="Returns" />
                </ListItem>
              </>
            )}

            {/* Common for All Roles */}
            <ListItem button component={Link} to="/product_list">
              <ListItemText primary="Products List" />
            </ListItem>
          {roles.includes('marketing-analyst') && (
              <ListItem button component={Link} to="/inventory/reports">
                <ListItemText primary="Inventory Reports" />
              </ListItem>
            )}
            {roles.includes('stocking-employee') && (
              <>
                <ListItem button component={Link} to="/inventory/stock-levels">
                  <ListItemText primary="Stock Levels" />
                </ListItem>
                <ListItem button component={Link} to="/inventory/warehouses">
                  <ListItemText primary="Warehouses" />
                </ListItem>
              </>
            )}
            <ListItem>
              <Button
                className="logout-button"
                type="submit"
                color="primary"
                variant="contained"
                fullWidth
                onClick={handleLogout}
              >
                Logout
              </Button>
            </ListItem>
          </List>
        </Box>
      </Drawer>
    </div>
  );
};

export default Navigation;
