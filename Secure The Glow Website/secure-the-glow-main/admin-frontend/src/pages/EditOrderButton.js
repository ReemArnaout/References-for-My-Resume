import React, { useState } from 'react';
import {
  Button,
  Dialog,
  DialogActions,
  DialogContent,
  DialogContentText,
  DialogTitle,
  TextField,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
} from '@mui/material';
import { SERVER_URL } from '../App';
import { useCsrf } from '../context/CsrfTokenContext'; // Import CSRF token context

const EditOrderButton = ({ order, onEditSuccess }) => {
  const { csrfToken } = useCsrf(); // Access CSRF token from context
  const [open, setOpen] = useState(false);
  const [formData, setFormData] = useState({
    delivery_time_slot: order.delivery_time_slot || '',
    delivery_address: order.delivery_address || '',
    status: order.status || '',
    products: order.products || [],
  });

  const handleClickOpen = () => setOpen(true);

  const handleClose = () => setOpen(false);

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData({ ...formData, [name]: value });
  };

  const handleProductChange = (index, e) => {
    const { name, value } = e.target;
    const updatedProducts = [...formData.products];
    updatedProducts[index][name] = value;
    setFormData({ ...formData, products: updatedProducts });
  };

  const handleAddProduct = () => {
    setFormData({
      ...formData,
      products: [...formData.products, { product_id: '', quantity: 1 }],
    });
  };

  const handleSubmit = async () => {
    try {
      const response = await fetch(`${SERVER_URL}/edit_order/${order.id}`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
          'X-CSRFToken': csrfToken, // Include CSRF token in headers
        },
        credentials: 'include', // Include cookies for authentication
        body: JSON.stringify(formData),
      });

      if (response.ok) {
        const updatedOrder = await response.json();
        console.log('Order updated successfully:', updatedOrder);
        onEditSuccess(updatedOrder); // Notify parent of the updated order
        alert('Order updated successfully!');
        handleClose();
      } else {
        const error = await response.json();
        console.error('Failed to update order:', error);
        alert(error.message || 'Failed to update order.');
      }
    } catch (err) {
      console.error('Error updating order:', err);
      alert('An error occurred while updating the order.');
    }
  };

  return (
    <>
      <Button variant="outlined" color="primary" onClick={handleClickOpen}>
        Edit Order
      </Button>
      <Dialog open={open} onClose={handleClose}>
        <DialogTitle>Edit Order</DialogTitle>
        <DialogContent>
          <DialogContentText>
            Modify the details of this order. Ensure all fields are correctly filled.
          </DialogContentText>
          <FormControl fullWidth margin="normal">
            <InputLabel>Delivery Time Slot</InputLabel>
            <Select
              name="delivery_time_slot"
              value={formData.delivery_time_slot}
              onChange={handleInputChange}
            >
              <MenuItem value="Morning">Morning</MenuItem>
              <MenuItem value="Afternoon">Afternoon</MenuItem>
              <MenuItem value="Evening">Evening</MenuItem>
            </Select>
          </FormControl>
          <TextField
            fullWidth
            margin="normal"
            label="Delivery Address"
            name="delivery_address"
            value={formData.delivery_address}
            onChange={handleInputChange}
          />
          <FormControl fullWidth margin="normal">
            <InputLabel>Status</InputLabel>
            <Select name="status" value={formData.status} onChange={handleInputChange}>
              <MenuItem value="pending">Pending</MenuItem>
              <MenuItem value="processing">Processing</MenuItem>
              <MenuItem value="shipped">Shipped</MenuItem>
              <MenuItem value="delivered">Delivered</MenuItem>
            </Select>
          </FormControl>
          <h4>Products</h4>
          {formData.products.map((product, index) => (
            <div key={index}>
              <TextField
                fullWidth
                margin="normal"
                label="Product ID"
                name="product_id"
                value={product.product_id}
                onChange={(e) => handleProductChange(index, e)}
              />
              <TextField
                fullWidth
                margin="normal"
                label="Quantity"
                name="quantity"
                type="number"
                value={product.quantity}
                onChange={(e) => handleProductChange(index, e)}
              />
            </div>
          ))}
          <Button
            variant="outlined"
            color="primary"
            onClick={handleAddProduct}
            style={{ marginTop: '10px' }}
          >
            Add Product
          </Button>
        </DialogContent>
        <DialogActions>
          <Button onClick={handleClose} color="secondary">
            Cancel
          </Button>
          <Button onClick={handleSubmit} color="primary">
            Save Changes
          </Button>
        </DialogActions>
      </Dialog>
    </>
  );
};

export default EditOrderButton;
