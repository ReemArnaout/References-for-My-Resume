import React, { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { SERVER_URL } from '../App';
import { TextField, Button, Typography, Box, Select, MenuItem, FormControl, InputLabel } from '@mui/material';
import { useCsrf } from '../context/CsrfTokenContext';
import './ProductUpdatePage.css'; 

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


const ProductUpdatePage = () => {
  const { productId } = useParams();
  const navigate = useNavigate();
  const [product, setProduct] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const { csrfToken } = useCsrf();
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
    gold_visible: false,
    premium_visible: false,
    regular_visible: false,
    discount: ''
  });
  const [subCategories, setSubCategories] = useState([]);
  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData({ ...formData, [name]: value });

    // Update subcategories when the category changes
    if (name === 'category') {
      setSubCategories(categoryData[value] || []);
      setFormData({ ...formData, category: value, sub_category: '' }); // Reset sub_category when category changes
    }
  };


  // Fetch product details
  useEffect(() => {
    fetch(`${SERVER_URL}/get_product/${productId}`, { credentials: 'include' })
      .then((response) => response.json())
      .then((data) => {
        setProduct(data);
        setFormData({
          name: data.name,
          color: data.color,
          quantity: data.quantity,
          description: data.description,
          gold_price: data.gold_price,
          premium_price: data.premium_price,
          regular_price: data.regular_price,
          category: data.category,
          sub_category: data.sub_category,
          pao: data.pao,
          gold_visible: data.gold_visible,
          premium_visible: data.premium_visible,
          regular_visible: data.regular_visible,
          discount: data.discount
        });
        setLoading(false);
      })
      .catch((err) => {
        setError(err);
        setLoading(false);
      });
  }, [productId]);

  // Handle form input changes
  const handleInputChange = (e) => {
    const { name, value, type, checked } = e.target;
    setFormData({
      ...formData,
      [name]: type === 'checkbox' ? checked : value,
    });
  };

  // Submit form data
  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      const response = await fetch(`${SERVER_URL}/edit_product/${productId}`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
          'X-CSRFToken': csrfToken
        },
        credentials: 'include',
        body: JSON.stringify(formData),
      });

      if (response.ok) {
        navigate(`/product_details/${productId}`);
      } else {
        const result = await response.json();
        setError(result.error || 'Failed to update product');
      }
    } catch (err) {
        console.log(err);
      setError('Error updating product');
    }
  };

  if (loading) return <div>Loading...</div>;
  if (error) return <div>Error: {error}</div>;

  return (
    <div className="container">
      <h1>Update Product</h1>
      <form onSubmit={handleSubmit}>
        <div className="form-group">
          <label>Name:</label>
          <input
            type="text"
            name="name"
            value={formData.name}
            onChange={handleInputChange}
            required
          />
        </div>
        <div className="form-group">
          <label>Color:</label>
          <input
            type="text"
            name="color"
            value={formData.color}
            onChange={handleInputChange}
          />
        </div>
        <div className="form-group">
          <label>Quantity:</label>
          <input
            type="text"
            name="quantity"
            value={formData.quantity}
            onChange={handleInputChange}
          />
        </div>
        <div className="form-group">
          <label>Description:</label>
          <textarea
            name="description"
            value={formData.description}
            onChange={handleInputChange}
          />
        </div>
        <div className="form-group">
          <label>Gold Price:</label>
          <input
            type="number"
            name="gold_price"
            value={formData.gold_price}
            onChange={handleInputChange}
          />
        </div>
        <div className="form-group">
          <label>Premium Price:</label>
          <input
            type="number"
            name="premium_price"
            value={formData.premium_price}
            onChange={handleInputChange}
          />
        </div>
        <div className="form-group">
          <label>Regular Price:</label>
          <input
            type="number"
            name="regular_price"
            value={formData.regular_price}
            onChange={handleInputChange}
          />
        </div>
        <FormControl fullWidth margin="normal">
        <label>Category</label>
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
      <label>Sub-category</label>
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
        <div className="form-group">
          <label>PAO:</label>
          <input
            type="text"
            name="pao"
            value={formData.pao}
            onChange={handleInputChange}
          />
        </div>
        <div className="form-group">
          <label>Discount:</label>
          <input
            type="text"
            name="discount"
            value={formData.discount}
            onChange={handleInputChange}
          />
        </div>
        <div className="form-group">
          <label>Gold Visible:</label>
          <input
            type="checkbox"
            name="gold_visible"
            checked={formData.gold_visible}
            onChange={handleInputChange}
          />
        </div>
        <div className="form-group">
          <label>Premium Visible:</label>
          <input
            type="checkbox"
            name="premium_visible"
            checked={formData.premium_visible}
            onChange={handleInputChange}
          />
        </div>
        <div className="form-group">
          <label>Regular Visible:</label>
          <input
            type="checkbox"
            name="regular_visible"
            checked={formData.regular_visible}
            onChange={handleInputChange}
          />
        </div>
        <button type="submit">Update Product</button>
      </form>
    </div>
  );
};

export default ProductUpdatePage;
