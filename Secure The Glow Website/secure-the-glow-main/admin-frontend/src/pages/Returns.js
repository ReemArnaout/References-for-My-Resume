import React, { useEffect, useState } from 'react';
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
  Box,
  Button,
  Dialog,
  DialogActions,
  DialogContent,
  DialogContentText,
  DialogTitle,
  TextField,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
} from '@mui/material';
import { SERVER_URL } from '../App';
import { useCsrf } from '../context/CsrfTokenContext'; // Import CSRF token context
import { withAuthorization } from '../components/withAuthorization';

const Returns = () => {
  const { csrfToken } = useCsrf(); // Access CSRF token from context
  const [returns, setReturns] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [openDialog, setOpenDialog] = useState(false);
  const [selectedReturn, setSelectedReturn] = useState(null);
  const [status, setStatus] = useState('');
  const [refundAmount, setRefundAmount] = useState('');

  useEffect(() => {
    const fetchReturns = async () => {
      try {
        const response = await fetch(`${SERVER_URL}/returns`, { credentials: 'include' });
        if (response.ok) {
          const data = await response.json();
          setReturns(data);
        } else {
          const errorData = await response.json();
          setError(errorData.error || 'Failed to fetch returns');
        }
      } catch (err) {
        setError('Error fetching returns');
      } finally {
        setLoading(false);
      }
    };

    fetchReturns();
  }, []);

  const handleDialogOpen = (ret) => {
    setSelectedReturn(ret);
    setStatus(ret.status || '');
    setRefundAmount(ret.refund_amount || '');
    setOpenDialog(true);
  };

  const handleDialogClose = () => {
    setSelectedReturn(null);
    setStatus('');
    setRefundAmount('');
    setOpenDialog(false);
  };

  const handleUpdateStatus = async () => {
    if (!status) {
      alert('Status is required');
      return;
    }

    try {
      const response = await fetch(`${SERVER_URL}/update_return_status/${selectedReturn.id}`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
          'X-CSRFToken': csrfToken, // Include CSRF token in headers
        },
        credentials: 'include',
        body: JSON.stringify({ status, refund_amount: refundAmount }),
      });

      if (response.ok) {
        const updatedReturn = await response.json();
        setReturns((prevReturns) =>
          prevReturns.map((ret) =>
            ret.id === selectedReturn.id ? { ...ret, status, refund_amount: refundAmount } : ret
          )
        );
        handleDialogClose();
        alert('Return status updated successfully');
      } else {
        const error = await response.json();
        alert(error.message || 'Failed to update return status.');
      }
    } catch (err) {
      console.error('Error updating return status:', err);
      alert('An error occurred while updating the return status.');
    }
  };

  if (loading) return <CircularProgress />;
  if (error) return <Typography color="error">{error}</Typography>;

  return (
    <Box>
      <Typography variant="h4" gutterBottom>
        Return Requests
      </Typography>
      <TableContainer component={Paper}>
        <Table>
          <TableHead>
            <TableRow>
              <TableCell>ID</TableCell>
              <TableCell>Order ID</TableCell>
              <TableCell>Product ID</TableCell>
              <TableCell>Customer Email</TableCell>
              <TableCell>Quantity</TableCell>
              <TableCell>Reason</TableCell>
              <TableCell>Status</TableCell>
              <TableCell>Refund Amount</TableCell>
              <TableCell>Actions</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {returns.map((ret) => (
              <TableRow key={ret.id}>
                <TableCell>{ret.id}</TableCell>
                <TableCell>{ret.order_id}</TableCell>
                <TableCell>{ret.product_id}</TableCell>
                <TableCell>{ret.customer_email}</TableCell>
                <TableCell>{ret.quantity_to_be_returned}</TableCell>
                <TableCell>{ret.reason}</TableCell>
                <TableCell>{ret.status}</TableCell>
                <TableCell>{ret.refund_amount || 'N/A'}</TableCell>
                <TableCell>
                  <Button
                    variant="outlined"
                    color="primary"
                    onClick={() => handleDialogOpen(ret)}
                  >
                    Update Status
                  </Button>
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </TableContainer>

      {/* Dialog for Updating Return Status */}
      <Dialog open={openDialog} onClose={handleDialogClose}>
        <DialogTitle>Update Return Status</DialogTitle>
        <DialogContent>
          <DialogContentText>
            Update the status and refund amount (if applicable) for this return request.
          </DialogContentText>
          <FormControl fullWidth margin="normal">
            <InputLabel>Status</InputLabel>
            <Select value={status} onChange={(e) => setStatus(e.target.value)}>
              <MenuItem value="approved">Approved</MenuItem>
              <MenuItem value="denied">Denied</MenuItem>
            </Select>
          </FormControl>
          {status === 'approved' && (
            <TextField
              fullWidth
              margin="normal"
              label="Refund Amount"
              type="number"
              value={refundAmount}
              onChange={(e) => setRefundAmount(e.target.value)}
            />
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={handleDialogClose} color="secondary">
            Cancel
          </Button>
          <Button onClick={handleUpdateStatus} color="primary">
            Save Changes
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default withAuthorization(['customer-service-specialist'])(Returns);
