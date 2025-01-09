import React, { useEffect, useState } from 'react';
import { useParams, Link, useNavigate } from 'react-router-dom';
import { SERVER_URL } from '../App';
import './ProductDetails.css'; // Import the CSS file
import { useCsrf } from '../context/CsrfTokenContext';

const ProductDetailsPage = ({roles}) => {
  let navigate = useNavigate();
  const { productId } = useParams();
  const [product, setProduct] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [selectedFile, setSelectedFile] = useState(null);
  const [ingredients, setIngredients] = useState([]);
  const [newIngredient, setNewIngredient] = useState('');
  const { csrfToken } = useCsrf();

  function getProductInfo() {
    fetch(`${SERVER_URL}/get_product/${productId}`, { credentials: 'include' })
      .then((response) => response.json())
      .then((data) => {
        setProduct(data);
        setLoading(false);
      })
      .catch((err) => {
        setError(err);
        setLoading(false);
      });
  }
  

  useEffect(getProductInfo, [productId]);

  useEffect(() => {
    fetch(`${SERVER_URL}/get_ingredients/${productId}`, { 
      credentials: 'include',
    })
      .then((response) => response.json())
      .then((data) => {
        setIngredients(data);
      })
      .catch((err) => {
        console.log("error", err)
        setError(err);

      });
  }, [productId]);

  const handleDeleteProduct = async () => {
    const response = await fetch(`${SERVER_URL}/delete_product/${productId}`, {
      headers:{
        'X-CSRFToken': csrfToken,
      },
      method: "DELETE",
      credentials: "include"});
    navigate("/product_list");
  }

  const handleDeleteImage = async (imagePath) => {
    try {
      const response = await fetch(`${SERVER_URL}/delete_image`, {
        method: 'DELETE',
        headers: {
          'Content-Type': 'application/json',
          'X-CSRFToken': csrfToken
        },
        credentials: 'include',
        body: JSON.stringify({
          name: product.name,
          image_name: imagePath,
        }),
      });

      if (response.ok) {
        setProduct((prevProduct) => ({
          ...prevProduct,
          images_base64: prevProduct.images_base64.filter(
            ([path]) => path !== imagePath
          ),
        }));
      } else {
        console.error('Failed to delete image');
      }
    } catch (err) {
      console.error('Error deleting image:', err);
    }
  };

  const handleFileChange = (event) => {
    setSelectedFile(event.target.files[0]);
  };

  const handleUploadImage = async () => {
    if (!selectedFile) return;

    const formData = new FormData();
    formData.append('name', product.name);
    formData.append('file', selectedFile);

    try {
      const response = await fetch(`${SERVER_URL}/upload_image`, {
        headers:{
          'X-CSRFToken': csrfToken,
        },
        method: 'POST',
        credentials: 'include',
        body: formData,
      });

      if (response.ok) {
        getProductInfo();
        setSelectedFile(null);
      } else {
        console.error('Failed to upload image');
      }
    } catch (err) {
      console.error('Error uploading image:', err);
    }
  };



  const handleDeleteIngredient = async (ingredientName) => {
    try {
      const response = await fetch(`${SERVER_URL}/delete_ingredient`, {
        method: 'DELETE',
        headers: {
          'Content-Type': 'application/json',
          'X-CSRFToken': csrfToken,
        },
        credentials: 'include',
        body: JSON.stringify({
          name: product.name,
          ingredient: ingredientName,
        }),
      });

      if (response.ok) {
        setIngredients((prevIngredients) =>
          prevIngredients.filter((ing) => ing.ingredient !== ingredientName)
        );
      } else {
        console.error('Failed to delete ingredient');
      }
    } catch (err) {
      console.error('Error deleting ingredient:', err);
    }
  };

  // Handle adding a new ingredient
  const handleAddIngredient = async () => {
    if (!newIngredient.trim()) return;

    try {
      const response = await fetch(`${SERVER_URL}/add_ingredient`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-CSRFToken': csrfToken,
        },
        credentials: 'include',
        body: JSON.stringify({
          name: product.name,
          ingredient: newIngredient,
        }),
      });

      if (response.ok) {
        setIngredients((prevIngredients) => [
          ...prevIngredients,
          { ingredient: newIngredient, name: product.name },
        ]);
        setNewIngredient('');
      } else {
        console.error('Failed to add ingredient');
      }
    } catch (err) {
      console.error('Error adding ingredient:', err);
    }
  };



  if (loading) return <div>Loading...</div>;
  if (error) return <div>Error fetching product details</div>;
  return (
    <div className="container">
      <h1 className="header">{product.name}</h1>

      <div className="product-info">
        <p><strong>Category:</strong> {product.category}</p>
        <p><strong>Sub-category:</strong> {product.sub_category}</p>
        <p><strong>Description:</strong> {product.description}</p>
        <p><strong>Price:</strong> ${product.regular_price}</p>
        <p><strong>Quantity:</strong> {product.quantity}</p>
        <p><strong>PAO:</strong> {product.pao}</p>
        <p><strong>Discount:</strong> {product.discount} %</p>
        <p><strong>Color:</strong> {product.color}</p>
        <p><strong>Gold Price:</strong> {product.gold_price}</p>
        <p><strong>Premium Price:</strong> {product.premium_price}</p>
        <p><strong>Regular Price:</strong> {product.regular_price}</p>
        <p><strong>Visible to Gold:</strong> {product.gold_visible ? "Yes" : "No"}</p>
        <p><strong>Visible to Premium:</strong> {product.premium_visible ? "Yes" : "No"}</p>
        <p><strong>Visible to All Others:</strong> {product.regular_visible ? "Yes" : "No"}</p>
      </div>
      {roles.includes('business-manager') && (
        <button onClick={() => {navigate(`/product_update/${productId}`)}}> 
            Update Product
        </button >)}
        {roles.includes('business-manager') && (
        <button
          onClick={() => handleDeleteProduct()}
          className="delete-button"
        >
          Delete
        </button>)}
      <h3>Images</h3>
      <div className="image-gallery">
        {product.images_base64 && product.images_base64.length > 0 ? (
          product.images_base64.map(([imagePath, base64Data], index) => (
            <div key={index} className="image-container">
              <img
                src={`data:image/jpeg;base64,${base64Data}`}
                alt={`Product ${index + 1}`}
              />
              {roles.includes('business-manager') && (
              <button
                onClick={() => handleDeleteImage(imagePath)}
                className="delete-button"
              >
                Delete
              </button>)}
            </div>
          ))
        ) : (
          <p>No images available</p>
        )}
      </div>
      {roles.includes('business-manager') && (
      <div className="upload-section">
        <h3>Upload New Image</h3>
        <input type="file" onChange={handleFileChange} />
        <button
          onClick={handleUploadImage}
          disabled={!selectedFile}
          className="upload-button"
        >
          Upload
        </button>
      </div>)}
      <h3>Ingredients</h3>
      <div className="product-info" sx = {{align:"center"}}>
      {ingredients.length > 0 ? (
        ingredients.map((ingredient, index) => (
          <div key={index} style={{ display: 'flex', alignItems: 'center' }}>
            <p>{ingredient.ingredient}</p>
            {roles.includes('business-manager') && (
              <button className = "upload-button" onClick={() => handleDeleteIngredient(ingredient.ingredient)}>Delete</button>)}
          </div>
        ))
      ) : (
        <p>No ingredients available</p>
      )}
      </div>
      {roles.includes('business-manager') && ( 
      <div>
        <h3>Add a New Ingredient</h3>
        <input
          type="text"
          value={newIngredient}
          onChange={(e) => setNewIngredient(e.target.value)}
          placeholder="Enter ingredient name"
        />
        <button onClick={handleAddIngredient} disabled={!newIngredient.trim()}>
          Add Ingredient
        </button> 
      </div>)}
    </div>
  );
};

export default ProductDetailsPage;
