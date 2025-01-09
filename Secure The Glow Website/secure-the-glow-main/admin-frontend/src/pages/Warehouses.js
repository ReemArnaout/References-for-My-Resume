import React, { useState } from 'react';
import { SERVER_URL } from '../App';
import { withAuthorization } from '../components/withAuthorization';
import { Box, Button, TextField, Typography } from '@mui/material';

const Warehouses = ({ roles }) => {
  const [warehouses, setWarehouses] = useState([]);
  const [warehouseId, setWarehouseId] = useState('');
  const [error, setError] = useState('');

  const fetchWarehouses = async () => {
    const endpoint = warehouseId
      ? `${SERVER_URL}/warehouse/${warehouseId}`
      : `${SERVER_URL}/warehouses`;

    try {
      const res = await fetch(endpoint, { credentials: 'include' });

      if (!res.ok) {
        const errorMsg = res.status === 403 ? 'Unauthorized' : 'Failed to fetch warehouses.';
        throw new Error(errorMsg);
      }

      const data = await res.json();
      setWarehouses(Array.isArray(data) ? data : [data]);
      setError('');
    } catch (err) {
      console.error('Error fetching warehouses:', err);
      setError(err.message || 'Failed to fetch warehouses.');
    }
  };

  return (
    <Box sx={{ textAlign: 'center', maxWidth: 600, mx: 'auto', mt: 4 }}>
      <Typography variant="h4" gutterBottom>
        Warehouses
      </Typography>
      <TextField
        fullWidth
        variant="outlined"
        label="Warehouse ID (optional)"
        value={warehouseId}
        onChange={(e) => setWarehouseId(e.target.value)}
        sx={{ mb: 2 }}
      />
      <Button variant="contained" color="primary" onClick={fetchWarehouses} sx={{ mt: 2 }}>
        Fetch Warehouses
      </Button>
      {error && <Typography color="error" sx={{ mt: 2 }}>{error}</Typography>}
      {warehouses.length > 0 && (
        <Box sx={{ mt: 4, textAlign: 'left' }}>
          {warehouses.map((warehouse, index) => (
            <Box key={index} sx={{ mb: 2 }}>
              <Typography variant="h6">
                {warehouse.warehouse_name} (ID: {warehouse.warehouse_id})
              </Typography>
              <Typography>Location: {warehouse.location}</Typography>
              {warehouse.products && (
                <Box sx={{ mt: 1 }}>
                  {warehouse.products.map((product) => (
                    <Typography key={product.product_id}>
                      Product ID: {product.product_id}, Quantity: {product.quantity}
                    </Typography>
                  ))}
                </Box>
              )}
            </Box>
          ))}
        </Box>
      )}
    </Box>
  );
};

// Restrict access to "stocking-employee" role
export default withAuthorization(['stocking-employee'])(Warehouses);
