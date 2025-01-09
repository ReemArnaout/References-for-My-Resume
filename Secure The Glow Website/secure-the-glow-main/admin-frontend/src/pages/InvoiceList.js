import React, { useEffect, useState } from 'react';
import { SERVER_URL } from '../App';
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
} from '@mui/material';
import KeyboardArrowDownIcon from '@mui/icons-material/KeyboardArrowDown';
import KeyboardArrowUpIcon from '@mui/icons-material/KeyboardArrowUp';
import UpdatePaymentButton from './UpdatePaymentButton';
import {withAuthorization} from '../components/withAuthorization';
const InvoiceList = () => {
  const [invoices, setInvoices] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // Fetch invoices on component mount
  useEffect(() => {
    const fetchInvoices = async () => {
      try {
        const response = await fetch(`${SERVER_URL}/invoices`, {
          method: 'GET',
          credentials: 'include', // Ensure cookies are sent if required for auth
        });

        if (response.ok) {
          const data = await response.json();
          setInvoices(data);
        } else {
          const errorData = await response.json();
          setError(errorData.error || 'Failed to fetch invoices');
        }
      } catch (err) {
        setError('Error fetching invoices');
      } finally {
        setLoading(false);
      }
    };

    fetchInvoices();
  }, []);

  if (loading) return <CircularProgress />;
  if (error) return <Typography color="error">{error}</Typography>;

  const handleUpdateSuccess = (updatedInvoice) => {
    setInvoices((prevInvoices) =>
      prevInvoices.map((invoice) =>
        invoice.id === updatedInvoice.id ? updatedInvoice : invoice
      )
    );
  };

  return (
    <Box>
      <Typography variant="h4" gutterBottom>
        Invoice List
      </Typography>
      <TableContainer component={Paper}>
        <Table>
          <TableHead>
            <TableRow>
              <TableCell />
              <TableCell>Invoice ID</TableCell>
              <TableCell>Order ID</TableCell>
              <TableCell>Date</TableCell>
              <TableCell>Total Amount</TableCell>
              <TableCell>Tax</TableCell>
              <TableCell>Payment Status</TableCell>
              <TableCell>Actions</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {invoices.map((invoice) => (
              <InvoiceRow
                key={invoice.id}
                invoice={invoice}
                onUpdateSuccess={handleUpdateSuccess}
              />
            ))}
          </TableBody>
        </Table>
      </TableContainer>
    </Box>
  );
};
const InvoiceRow = ({ invoice, onUpdateSuccess }) => {
  const [open, setOpen] = useState(false);
  const [currentStatus, setCurrentStatus] = useState(invoice.payment_status);

  const handleUpdateSuccess = (updatedInvoice) => {
    setCurrentStatus(updatedInvoice.payment_status);
    onUpdateSuccess(updatedInvoice); // Notify parent about the update
  };

  return (
    <>
      <TableRow>
        <TableCell>
          <IconButton size="small" onClick={() => setOpen(!open)}>
            {open ? <KeyboardArrowUpIcon /> : <KeyboardArrowDownIcon />}
          </IconButton>
        </TableCell>
        <TableCell>{invoice.id}</TableCell>
        <TableCell>{invoice.order_id}</TableCell>
        <TableCell>
          {invoice.invoice_date
            ? new Date(invoice.invoice_date).toLocaleDateString()
            : 'N/A'}
        </TableCell>
        <TableCell>
          {typeof invoice.total_amount === 'number'
            ? invoice.total_amount.toFixed(2)
            : 'N/A'}
        </TableCell>
        <TableCell>
          {typeof invoice.tax === 'number' ? invoice.tax.toFixed(2) : 'N/A'}
        </TableCell>
        <TableCell>{currentStatus}</TableCell>
        <TableCell>
          <UpdatePaymentButton
            invoiceId={invoice.id}
            currentStatus={currentStatus}
            onUpdateSuccess={handleUpdateSuccess}
          />
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
                  {(invoice.products || []).map((product) => (
                    <TableRow key={product.product_id}>
                      <TableCell>{product.product_id}</TableCell>
                      <TableCell>
                        {product.product_details?.name || 'N/A'}
                      </TableCell>
                      <TableCell>
                        {product.product_details?.category || 'N/A'}
                      </TableCell>
                      <TableCell>
                        {typeof product.quantity === 'number'
                          ? product.quantity
                          : 'N/A'}
                      </TableCell>
                      <TableCell>
                        {typeof product.price_at_time_of_purchase === 'number'
                          ? product.price_at_time_of_purchase.toFixed(2)
                          : 'N/A'}
                      </TableCell>
                      <TableCell>
                        {typeof product.total_price === 'number'
                          ? product.total_price.toFixed(2)
                          : 'N/A'}
                      </TableCell>
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

export default withAuthorization(['customer-service-specialist'])(InvoiceList);

