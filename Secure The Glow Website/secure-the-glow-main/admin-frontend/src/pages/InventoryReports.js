import React, { useEffect, useState } from 'react';
import { SERVER_URL } from '../App';
import { withAuthorization } from '../components/withAuthorization';
import { Box, Typography, Card, CardContent, Grid } from '@mui/material';

const InventoryReports = () => {
  const [report, setReport] = useState(null);
  const [error, setError] = useState('');

  useEffect(() => {
    const fetchReport = async () => {
      try {
        const res = await fetch(`${SERVER_URL}/inventory_report`, { credentials: 'include' });

        if (!res.ok) {
          const errorMsg = res.status === 403 ? 'Unauthorized' : 'Failed to fetch inventory report.';
          throw new Error(errorMsg);
        }

        const data = await res.json();
        setReport(data);
        setError('');
      } catch (err) {
        console.error('Error fetching inventory report:', err);
        setError(err.message || 'Failed to fetch inventory report.');
      }
    };

    fetchReport();
  }, []);

  const renderReportSection = (title, items, fields, backgroundColor) => (
    <Box sx={{ mt: 3, p: 2, borderRadius: 2, bgcolor: backgroundColor }}>
      <Typography variant="h5" gutterBottom>
        {title}
      </Typography>
      <Grid container spacing={2}>
        {items.map((item, index) => (
          <Grid item xs={12} sm={6} md={4} key={index}>
            <Card>
              <CardContent>
                {fields.map(({ label, key }) => (
                  <Typography key={key} variant="body1">
                    <strong>{label}:</strong> {item[key]}
                  </Typography>
                ))}
              </CardContent>
            </Card>
          </Grid>
        ))}
      </Grid>
    </Box>
  );

  return (
    <Box sx={{ maxWidth: 1200, mx: 'auto', mt: 4 }}>
      <Typography variant="h4" gutterBottom sx={{ textAlign: 'center', mb: 4 }}>
        Inventory Reports
      </Typography>
      {error && (
        <Typography color="error" variant="body1" sx={{ textAlign: 'center', mb: 2 }}>
          {error}
        </Typography>
      )}
      {report && (
        <>
          {renderReportSection(
            'Turnover Report',
            report.turnover_report,
            [
              { label: 'Product ID', key: 'product_id' },
              { label: 'Current Stock', key: 'current_stock' },
              { label: 'Predicted Turnover', key: 'predicted_turnover' },
            ],
            '#e3f2fd' // Light blue
          )}
          {renderReportSection(
            'Popular Products',
            report.popular_products,
            [
              { label: 'Product ID', key: 'product_id' },
              { label: 'Current Stock', key: 'current_stock' },
              { label: 'Popularity Index', key: 'predicted_popularity_index' },
            ],
            '#e3f2fd' 
          )}
          {renderReportSection(
            'Demand Predictions',
            report.demand_predictions,
            [
              { label: 'Product ID', key: 'product_id' },
              { label: 'Predicted Demand', key: 'predicted_demand' },
              { label: 'Current Stock', key: 'current_stock' },
            ],
            '#e3f2fd' 
          )}
        </>
      )}
    </Box>
  );
};

// Restrict access to "marketing-analyst" role
export default withAuthorization(['marketing-analyst'])(InventoryReports);
