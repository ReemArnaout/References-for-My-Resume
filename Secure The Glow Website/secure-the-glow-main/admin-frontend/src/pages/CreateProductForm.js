import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { TextField, Button, Typography, Box, Select, MenuItem, FormControl, InputLabel } from '@mui/material';
import {withAuthorization} from '../components/withAuthorization';
import { useCsrf } from '../context/CsrfTokenContext';
import { SERVER_URL } from '../App';

const categoryData = {
  "sun care": ["sunscreen", "tanning oil", "after sun"],
  "eyes": ["mascara", "eyeshadow"],
  "cleansers": ["face wash", "micellar water", "cleansing balm"],
  "moisturizers": ["day cream", "night cream", "hydrating gel"],
  "anti-aging": ["retinol cream", "firming serum", "anti-wrinkle lotion"],
  "exfoliators": ["face scrub", "chemical exfoliant", "peel"],
  "lip care": ["lip balm", "lip mask", "lip scrub"],
  "masks": ["clay mask", "sheet mask", "overnight mask"],
  "toners": ["hydrating toner", "exfoliating toner", "pH balancing toner"],
  "serums": ["vitamin C serum", "hyaluronic acid", "niacinamide serum"]
};

const CreateProductForm = ({roles}) => {
  const { csrfToken } = useCsrf();
  const [selectedFile, setSelectedFile] = useState(null);
  const [formData, setFormData] = useState({
    name: '',
    color: '',
    quantity: '',
    description: '',
    gold_price: '',
    premium_price: '',
    regular_price: '',
    category: '',
    sub_category: '',
    pao: '',
    discount: ''
  });

  const [message, setMessage] = useState('');
  const [subCategories, setSubCategories] = useState([]);

  const handleFileChange = (event) => {
    setSelectedFile(event.target.files[0]);
  };

  const handleUploadImage = async () => {
    if (!selectedFile) return;

    const formData = new FormData();
    formData.append('file', selectedFile);

    try {
      const response = await fetch(`${SERVER_URL}/upload_products_csv`, {
        method: 'POST',
        credentials: 'include',
        body: formData,
        headers:{
          'X-CSRFToken': csrfToken,
        }
      });

      if (response.ok) {
        setSelectedFile(null);
        setMessage('Products created successfully!');
      } else {
        setMessage('Failed to upload products');
        console.error('Failed to upload file');
      }
    } catch (err) {
      setMessage('Failed to upload products');
      console.error('Error uploading file:', err);
    }
  };

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData({ ...formData, [name]: value });

    // Update subcategories when the category changes
    if (name === 'category') {
      setSubCategories(categoryData[value] || []);
      setFormData({ ...formData, category: value, sub_category: '' }); // Reset sub_category when category changes
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      const response = await axios.post(`${SERVER_URL}/create_product`, formData, {
        withCredentials: true,
        headers:{
          'X-CSRFToken': csrfToken,
        }
      });
      setMessage('Product created successfully!');
    } catch (error) {
      if (error.response && error.response.status === 400) {
        setMessage('Error: Invalid input or server issue.');
      } else if (error.response && error.response.status === 403) {
        setMessage('Error: Unauthorized. You do not have permission.');
      } else {
        setMessage('Error: Something went wrong.');
      }
    }
  };

  return (
    <div>
      <div className="upload-section">
        <h3>Upload with CSV</h3>
        <p>It should contain the following <strong>exact</strong> fields: name, color, quantity, description, gold_price, premium_price, regular_price, category, sub_category, pao, discount, ingredients</p>
        <p>Ingredients should be separated by <strong>commas</strong></p>
        <p>Upload will not be successful if a product already exists</p>
        <input type="file" onChange={handleFileChange} />
        <button
          onClick={handleUploadImage}
          disabled={!selectedFile}
          className="upload-button"
        >
          Upload
        </button>
      </div>
    <Box component="form" onSubmit={handleSubmit} sx={{ maxWidth: 600, mx: 'auto', mt: 4 }}>
      <Typography variant="h4" gutterBottom>
        Create Product
      </Typography>
      {message && (
        <Typography variant="body1" color="error" gutterBottom>
          {message}
        </Typography>
      )}
      {['name', 'color', 'quantity', 'description', 'gold_price', 'premium_price', 'regular_price', 'pao', 'discount'].map((field) => (
        <TextField
          key={field}
          label={field.replace('_', ' ').toUpperCase()}
          name={field}
          value={formData[field]}
          onChange={handleChange}
          required={field !== 'description'}
          fullWidth
          margin="normal"
        />
      ))}

      <FormControl fullWidth margin="normal">
        <InputLabel id="category-label">CATEGORY</InputLabel>
        <Select
          labelId="category-label"
          id="category"
          name="category"
          value={formData.category}
          onChange={handleChange}
          required
        >
          {Object.keys(categoryData).map((cat) => (
            <MenuItem key={cat} value={cat}>
              {cat}
            </MenuItem>
          ))}
        </Select>
      </FormControl>

      <FormControl fullWidth margin="normal" disabled={!formData.category}>
        <InputLabel id="sub-category-label">SUB CATEGORY</InputLabel>
        <Select
          labelId="sub-category-label"
          id="sub_category"
          name="sub_category"
          value={formData.sub_category}
          onChange={handleChange}
          required
        >
          {subCategories.map((subCat) => (
            <MenuItem key={subCat} value={subCat}>
              {subCat}
            </MenuItem>
          ))}
        </Select>
      </FormControl>

      <Button type="submit" variant="contained" color="primary" fullWidth>
        Create Product
      </Button>
    </Box>
    </div>
  );
};

// Specify the roles that can access the page, e.g., ['business-manager']
export default withAuthorization(['business-manager'])(CreateProductForm);
