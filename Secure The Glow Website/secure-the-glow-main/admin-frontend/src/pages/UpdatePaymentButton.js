import React, { useState } from 'react';
import {
  Button,
  Dialog,
  DialogActions,
  DialogContent,
  DialogContentText,
  DialogTitle,
  MenuItem,
  Select,
  FormControl,
  InputLabel,
} from '@mui/material';
import { SERVER_URL } from '../App';
import { useCsrf } from '../context/CsrfTokenContext'; // Import CSRF token context

const UpdatePaymentButton = ({ invoiceId, currentStatus, onUpdateSuccess }) => {
  const { csrfToken } = useCsrf(); // Access CSRF token from context
  const [open, setOpen] = useState(false);
  const [newStatus, setNewStatus] = useState(currentStatus);

  const handleClickOpen = () => {
    console.log(`Opening dialog to update payment status for Invoice ID: ${invoiceId}`); // Log dialog open
    setOpen(true);
  };

  const handleClose = () => {
    console.log(`Closing dialog for Invoice ID: ${invoiceId}`); // Log dialog close
    setOpen(false);
  };

  const handleStatusChange = (event) => {
    const status = event.target.value;
    console.log(`Payment status changed to: ${status}`); // Log status change
    setNewStatus(status);
  };

  const handleUpdate = async () => {
    console.log(`Attempting to update payment status for Invoice ID: ${invoiceId} to "${newStatus}"`); // Log update attempt

    try {
      const response = await fetch(`${SERVER_URL}/update_invoice_payment/${invoiceId}`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
          'X-CSRFToken': csrfToken, // Include CSRF token in headers
        },
        credentials: 'include',
        body: JSON.stringify({ payment_status: newStatus }),
      });

      if (response.ok) {
        const updatedInvoice = await response.json();
        console.log(
          `Invoice ${updatedInvoice.invoice.id}: Payment status successfully updated to "${newStatus}".`
        ); // Log successful update
        onUpdateSuccess(updatedInvoice.invoice); // Update parent state
        handleClose();
      } else {
        const errorData = await response.json();
        console.error(
          `Failed to update payment status for Invoice ID: ${invoiceId}. Error: ${errorData.error}`
        ); // Log error details
        alert(errorData.error || 'Failed to update payment status.');
      }
    } catch (err) {
      console.error(`Error updating payment status for Invoice ID: ${invoiceId}:`, err); // Log unexpected errors
      alert('An error occurred while updating the payment status.');
    }
  };

  return (
    <>
      <Button variant="outlined" color="primary" onClick={handleClickOpen}>
        Update Payment
      </Button>
      <Dialog open={open} onClose={handleClose}>
        <DialogTitle>Update Payment Status</DialogTitle>
        <DialogContent>
          <DialogContentText>
            Select the new payment status for this invoice.
          </DialogContentText>
          <FormControl fullWidth margin="normal">
            <InputLabel>Payment Status</InputLabel>
            <Select value={newStatus} onChange={handleStatusChange}>
              <MenuItem value="unpaid">Unpaid</MenuItem>
              <MenuItem value="partial">Partial</MenuItem>
              <MenuItem value="paid">Paid</MenuItem>
            </Select>
          </FormControl>
        </DialogContent>
        <DialogActions>
          <Button onClick={handleClose} color="secondary">
            Cancel
          </Button>
          <Button onClick={handleUpdate} color="primary">
            Save
          </Button>
        </DialogActions>
      </Dialog>
    </>
  );
};

export default UpdatePaymentButton;
