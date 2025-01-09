import React from 'react';
import { Button, Dialog, DialogActions, DialogContent, DialogContentText, DialogTitle } from '@mui/material';
import { SERVER_URL } from '../App';
import { useCsrf } from '../context/CsrfTokenContext'; // Import CSRF token context

const DeleteOrderButton = ({ orderId, onDeleteSuccess }) => {
  const { csrfToken } = useCsrf(); // Access CSRF token from context
  const [open, setOpen] = React.useState(false);

  const handleClickOpen = () => {
    console.log(`Open confirmation dialog for deleting order ID: ${orderId}`); // Log when the dialog opens
    setOpen(true);
  };

  const handleClose = () => {
    console.log(`Close confirmation dialog for order ID: ${orderId}`); // Log when the dialog closes
    setOpen(false);
  };

  const handleDelete = async () => {
    console.log(`Attempting to delete order ID: ${orderId}`); // Log the delete attempt
    try {
      const response = await fetch(`${SERVER_URL}/delete_order/${orderId}`, {
        method: 'DELETE',
        headers: {
          'Content-Type': 'application/json',
          'X-CSRFToken': csrfToken, // Include CSRF token in headers
        },
        credentials: 'include', // Include cookies for authentication if needed
      });

      if (response.ok) {
        console.log(`Order ID: ${orderId} deleted successfully.`); // Log success
        onDeleteSuccess(orderId); // Notify parent component about successful deletion
        alert('Order deleted successfully');
        handleClose();
      } else {
        const result = await response.json();
        console.error(`Failed to delete order ID: ${orderId}. Error: ${result.error}`); // Log error details
        alert(result.error || 'Failed to delete the order');
      }
    } catch (err) {
      console.error(`Error deleting order ID: ${orderId}:`, err); // Log unexpected errors
      alert('An error occurred while deleting the order.');
    }
  };

  return (
    <>
      <Button variant="outlined" color="error" onClick={handleClickOpen}>
        Delete Order
      </Button>
      <Dialog
        open={open}
        onClose={handleClose}
        aria-labelledby="alert-dialog-title"
        aria-describedby="alert-dialog-description"
      >
        <DialogTitle id="alert-dialog-title">{"Delete Order"}</DialogTitle>
        <DialogContent>
          <DialogContentText id="alert-dialog-description">
            Are you sure you want to delete this order? This action cannot be undone.
          </DialogContentText>
        </DialogContent>
        <DialogActions>
          <Button onClick={handleClose} color="primary">
            Cancel
          </Button>
          <Button onClick={handleDelete} color="error" autoFocus>
            Delete
          </Button>
        </DialogActions>
      </Dialog>
    </>
  );
};

export default DeleteOrderButton;
