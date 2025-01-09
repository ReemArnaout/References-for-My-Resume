import React, { useState } from 'react';
import { SERVER_URL } from '../App';
import { withAuthorization } from '../components/withAuthorization';
import { useCsrf } from '../context/CsrfTokenContext';
import { Box, Button, TextField, Typography } from '@mui/material';

const StockLevels = ({ roles }) => {
  const [warehouseId, setWarehouseId] = useState('');
  const [productId, setProductId] = useState('');
  const [quantity, setQuantity] = useState('');
  const [response, setResponse] = useState(null);
  const [error, setError] = useState('');
  const { csrfToken } = useCsrf();

  const handleUpdateStock = async () => {
    const payload = {
      warehouse_id: warehouseId,
      product_id: productId,
      quantity: parseInt(quantity, 10),
    };

    try {
      const res = await fetch(`${SERVER_URL}/update_stock_level`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-CSRF-TOKEN': csrfToken,
        },
        credentials: 'include',
        body: JSON.stringify(payload),
      });

      if (!res.ok) {
        const errorMsg = res.status === 403 ? 'Unauthorized' : 'Failed to update stock.';
        throw new Error(errorMsg);
      }

      const data = await res.json();
      setResponse(data);
      setError('');
    } catch (err) {
      console.error('Error updating stock level:', err);
      setError(err.message || 'Failed to update stock.');
    }
  };

  return (
    <Box sx={{ textAlign: 'center', maxWidth: 400, mx: 'auto', mt: 4 }}>
      <Typography variant="h4" gutterBottom>
        Update Stock Levels
      </Typography>
      <TextField
        fullWidth
        variant="outlined"
        label="Warehouse ID"
        value={warehouseId}
        onChange={(e) => setWarehouseId(e.target.value)}
        sx={{ mb: 2 }}
      />
      <TextField
        fullWidth
        variant="outlined"
        label="Product ID"
        value={productId}
        onChange={(e) => setProductId(e.target.value)}
        sx={{ mb: 2 }}
      />
      <TextField
        fullWidth
        variant="outlined"
        label="Quantity (Insert 0 to view current stock levels)" 


        value={quantity}
        onChange={(e) => setQuantity(e.target.value)}
        sx={{ mb: 2 }}
      />
      <Button variant="contained" color="primary" onClick={handleUpdateStock} sx={{ mt: 2 }}>
        Show and Update Stock Levels
      </Button>
      {error && <Typography color="error">{error}</Typography>}
      {response && (
        <Box sx={{ mt: 3, textAlign: 'left' }}>
          <Typography variant="h6">Stock Update Result:</Typography>
          <Typography>Updated Quantity: {response.quantity}</Typography>
          {response.low_stock_alert && <Typography color="error">Low Stock Alert!</Typography>}
        </Box>
      )}
    </Box>
  );
};

// Restrict access to "stocking-employee" role
export default withAuthorization(['stocking-employee'])(StockLevels);
