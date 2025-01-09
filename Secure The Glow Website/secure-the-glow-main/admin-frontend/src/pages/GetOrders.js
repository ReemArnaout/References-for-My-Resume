import React, { useEffect, useState } from 'react';
import { SERVER_URL } from '../App';
import DeleteOrderButton from './DeleteOrderButton';
import EditOrderButton from './EditOrderButton';
import {
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  CircularProgress,
  Typography,
  Collapse,
  IconButton,
  Box,
  Button,
} from '@mui/material';
import KeyboardArrowDownIcon from '@mui/icons-material/KeyboardArrowDown';
import KeyboardArrowUpIcon from '@mui/icons-material/KeyboardArrowUp';
import {withAuthorization} from '../components/withAuthorization';

const GetOrders = () => {
  const [orders, setOrders] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchOrders = async () => {
      try {
        const response = await fetch(`${SERVER_URL}/orders`, { credentials: 'include' });
        if (response.ok) {
          const data = await response.json();
          setOrders(data);
        } else {
          const errorData = await response.json();
          setError(errorData.error || 'Failed to fetch orders');
        }
      } catch (err) {
        setError('Error fetching orders');
      } finally {
        setLoading(false);
      }
    };

    fetchOrders();
  }, []);

  const handleDeleteSuccess = (orderId) => {
    setOrders((prevOrders) => prevOrders.filter((order) => order.id !== orderId));
  };

  const handleEditSuccess = (updatedOrder) => {
    setOrders((prevOrders) =>
      prevOrders.map((order) => (order.id === updatedOrder.id ? updatedOrder : order))
    );
  };

  if (loading) return <CircularProgress />;
  if (error) return <Typography color="error">{error}</Typography>;

  return (
    <Box>
      <Typography variant="h4" gutterBottom>
        Order List
      </Typography>
      <TableContainer component={Paper}>
        <Table>
          <TableHead>
            <TableRow>
              <TableCell />
              <TableCell>Order ID</TableCell>
              <TableCell>Customer Email</TableCell>
              <TableCell>Delivery Address</TableCell>
              <TableCell>Time Slot</TableCell>
              <TableCell>Payment Method</TableCell>
              <TableCell>Status</TableCell>
              <TableCell>Actions</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {orders.map((order) => (
              <OrderRow
                key={order.id}
                order={order}
                onEditSuccess={handleEditSuccess}
                onDeleteSuccess={handleDeleteSuccess}
              />
            ))}
          </TableBody>
        </Table>
      </TableContainer>
    </Box>
  );
};

const OrderRow = ({ order, onEditSuccess, onDeleteSuccess }) => {
  const [open, setOpen] = useState(false);

  return (
    <>
      <TableRow>
        <TableCell>
          <IconButton size="small" onClick={() => setOpen(!open)}>
            {open ? <KeyboardArrowUpIcon /> : <KeyboardArrowDownIcon />}
          </IconButton>
        </TableCell>
        <TableCell>{order.id}</TableCell>
        <TableCell>{order.customer_email}</TableCell>
        <TableCell>{order.delivery_address}</TableCell>
        <TableCell>{order.delivery_time_slot}</TableCell>
        <TableCell>{order.payment_method}</TableCell>
        <TableCell>{order.status}</TableCell>
        <TableCell>
          <EditOrderButton order={order} onEditSuccess={onEditSuccess} />
          <DeleteOrderButton orderId={order.id} onDeleteSuccess={onDeleteSuccess} />
        </TableCell>
      </TableRow>
      <TableRow>
        <TableCell colSpan={8}>
          <Collapse in={open} timeout="auto" unmountOnExit>
            <Box margin={2}>
              <Typography variant="h6" gutterBottom>
                Products
              </Typography>
              <Table size="small">
                <TableHead>
                  <TableRow>
                    <TableCell>Product ID</TableCell>
                    <TableCell>Name</TableCell>
                    <TableCell>Category</TableCell>
                    <TableCell>Quantity</TableCell>
                    <TableCell>Price</TableCell>
                    <TableCell>Total</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {order.products.map((product) => (
                    <TableRow key={product.product_id}>
                      <TableCell>{product.product_id}</TableCell>
                      <TableCell>{product.product_details?.name || 'N/A'}</TableCell>
                      <TableCell>{product.product_details?.category || 'N/A'}</TableCell>
                      <TableCell>{product.quantity}</TableCell>
                      <TableCell>{product.individual_price.toFixed(2)}</TableCell>
                      <TableCell>{product.total_price.toFixed(2)}</TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </Box>
          </Collapse>
        </TableCell>
      </TableRow>
    </>
  );
};

export default withAuthorization(['customer-service-specialist'])(GetOrders);
