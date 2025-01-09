import React, { useState } from 'react';
import axios from 'axios';
import { useCsrf } from '../context/CsrfTokenContext';  // Import CSRF token context
import {
  TextField,
  Button,
  Typography,
  Box,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  RadioGroup,
  FormControlLabel,
  Radio,
} from '@mui/material';
import { withAuthorization } from '../components/withAuthorization';

const CreateOrder = () => {
  const { csrfToken } = useCsrf();  // Access CSRF token from context
  const [customerEmail, setCustomerEmail] = useState('');
  const [deliveryTimeSlot, setDeliveryTimeSlot] = useState('');
  const [paymentMethod, setPaymentMethod] = useState('');
  const [products, setProducts] = useState([{ product_id: '', quantity: 0 }]);
  const [orderType, setOrderType] = useState('delivery');  // New state for order type (delivery or in-store)
  const [instorePickup, setInstorePickup] = useState('');
  const [deliveryAddress, setDeliveryAddress] = useState('');

  const handleProductChange = (index, event) => {
    const values = [...products];
    values[index][event.target.name] = event.target.value;
    setProducts(values);
  };

  const addProduct = () => {
    setProducts([...products, { product_id: '', quantity: 0 }]);
  };

  const deleteProduct = (index) => {
    if (products.length > 1) {
      const values = [...products];
      values.splice(index, 1);
      setProducts(values);
    } else {
      alert('You must have at least one product in the order.');
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();

    const orderData = {
      customer_email: customerEmail,
      delivery_time_slot: deliveryTimeSlot,
      payment_method: paymentMethod,
      products,
      instore_pickup: orderType === 'instore' ? instorePickup : '',  // Store name if in-store selected
      delivery_address: orderType === 'delivery' ? deliveryAddress : '',  // Delivery address if delivery selected
    };

    try {
      const response = await axios.post('http://localhost:5002/create_order', orderData, {
        withCredentials: true,
        headers: {
          'X-CSRFToken': csrfToken,
        },
      });

      if (response.status === 201) {
        alert("Order created successfully!");
      }
    } catch (error) {
      alert("Failed to create order");
      console.error(error);
    }
  };

  return (
    <Box component="form" onSubmit={handleSubmit} sx={{ maxWidth: 600, mx: 'auto', mt: 4 }}>
      <Typography variant="h4" gutterBottom>
        Create Order
      </Typography>

      <TextField
        label="Customer Email"
        type="email"
        value={customerEmail}
        onChange={(e) => setCustomerEmail(e.target.value)}
        required
        fullWidth
        margin="normal"
      />

      <FormControl fullWidth margin="normal" sx={{ mt: 2 }}>
        <InputLabel>Delivery Time Slot</InputLabel>
        <Select
          value={deliveryTimeSlot}
          onChange={(e) => setDeliveryTimeSlot(e.target.value)}
          label="Delivery Time Slot"
          required
        >
          <MenuItem value="Morning">Morning</MenuItem>
          <MenuItem value="Noon">Noon</MenuItem>
          <MenuItem value="Evening">Evening</MenuItem>
        </Select>
      </FormControl>

      <FormControl fullWidth margin="normal" sx={{ mt: 2 }}>
        <InputLabel>Payment Method</InputLabel>
        <Select
          value={paymentMethod}
          onChange={(e) => setPaymentMethod(e.target.value)}
          label="Payment Method"
          required
        >
          <MenuItem value="Credit Card">Credit Card</MenuItem>
          <MenuItem value="Cash on Delivery">Cash on Delivery</MenuItem>
        </Select>
      </FormControl>

      {products.map((product, index) => (
        <Box key={index} sx={{ mt: 2, display: 'flex', gap: 2, alignItems: 'center' }}>
          <TextField
            label="Product ID"
            name="product_id"
            value={product.product_id}
            onChange={(e) => handleProductChange(index, e)}
            required
            fullWidth
            margin="normal"
          />
          <TextField
            label="Quantity"
            name="quantity"
            type="number"
            value={product.quantity}
            onChange={(e) => handleProductChange(index, e)}
            required
            fullWidth
            margin="normal"
          />
          <Button
            variant="outlined"
            color="error"
            onClick={() => deleteProduct(index)}
          >
            Delete
          </Button>
        </Box>
      ))}

      <Button variant="outlined" color="primary" onClick={addProduct} sx={{ mt: 2 }}>
        Add Another Product
      </Button>

      {/* Order Type (Delivery or In-store) */}
      <Typography variant="h6" sx={{ mt: 2 }}>
        Choose Order Type
      </Typography>
      <RadioGroup
        value={orderType}
        onChange={(e) => setOrderType(e.target.value)}
        row
      >
        <FormControlLabel value="delivery" control={<Radio />} label="Delivery" />
        <FormControlLabel value="instore" control={<Radio />} label="In-store Pickup" />
      </RadioGroup>

      {/* Conditionally render either the delivery address or store selection */}
      {orderType === 'delivery' ? (
          <TextField
            label="Delivery Address"
            type="text"
            value={deliveryAddress}
            onChange={(e) => setDeliveryAddress(e.target.value)}
            required
            fullWidth
            margin="normal"
            placeholder="City-Street-Building-Floor (e.g., New York-5th Avenue-Building 101-2)"
            helperText="Please enter the address in the format: City-Street-Building-Floor. Floor must be numeric."
          />
        ) : (
          <FormControl fullWidth margin="normal" sx={{ mt: 2 }}>
            <InputLabel>Select Store for In-store Pickup</InputLabel>
            <Select
              value={instorePickup}
              onChange={(e) => setInstorePickup(e.target.value)}
              label="Select Store"
              required
            >
              <MenuItem value="ABC Verdun">ABC Verdun</MenuItem>
              <MenuItem value="ABC Ashrafieh">ABC Ashrafieh</MenuItem>
              <MenuItem value="ABC Dbayeh">ABC Dbayeh</MenuItem>
            </Select>
          </FormControl>
        )}


      <Button type="submit" variant="contained" color="primary" fullWidth sx={{ mt: 2 }}>
        Create Order
      </Button>
    </Box>
  );
};

export default withAuthorization(['customer-service-specialist'])(CreateOrder);
