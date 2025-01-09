import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom'; // For navigation to product details page
import { SERVER_URL } from '../App';
import './ProductList.css'; // Assuming your CSS is in this file

const ProductList = () => {
  const [products, setProducts] = useState([]);

  useEffect(() => {
    // Fetch the list of products from your backend route
    fetch(`${SERVER_URL}/all_products`, { credentials: 'include' })
      .then((response) => response.json())
      .then((data) => setProducts(data))
      .catch((error) => console.error('Error fetching products:', error));
  }, []);

  return (
    <div>
      <h1>Product List</h1>
      <div className="product-list">
        {products.map((product) => (
          <div key={product.id} className="product-card">
            <img
              src={`data:image/jpeg;base64,${product.image_base64}`} 
              alt={product.name}
              style={{ width: '100px', height: '100px' }} // Adjust image size
            />
            <h3>{product.name}</h3>
            <p>{product.description}</p>
            <p>Price: ${product.regular_price}</p>
            {/* Link to the product details page */}
            <Link to={`/product_details/${product.id}`}>View Details</Link>
          </div>
        ))}
      </div>
    </div>
  );
};

export default ProductList;
