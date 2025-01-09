import './App.css';
import React, { useState, useEffect } from "react";
import { BrowserRouter as Router, Routes, Route, Navigate } from "react-router-dom";
import LoginPage from './pages/Authentication';
import axios from 'axios';
import HomePage from './pages/Homepage';
import Navigation from './components/NavBar';
import CreateProductForm from './pages/CreateProductForm';
import ProductList from './pages/ProductList';
import ProductDetailsPage from './pages/ProductDetails';
import ProductUpdatePage from './pages/ProductUpdatePage';
import CreateOrder from './pages/CreateOrder';
import GetOrders from './pages/GetOrders';  
import InvoiceList from './pages/InvoiceList';
import Returns from './pages/Returns'; 
import InventoryReports from './pages/InventoryReports'; 
import StockLevels from './pages/StockLevels'; 
import Warehouses from './pages/Warehouses'; 
import EditOrderButton from './pages/EditOrderButton';
import { useCsrf } from './context/CsrfTokenContext';


export const SERVER_URL = "http://localhost:5002";

// Fetch user roles
async function fetchUserInfo() {
  const response = await fetch(`${SERVER_URL}/employee_info`, {
    method: 'GET',
    credentials: 'include',
    withCredentials: true,
  });

  if (response.ok) {
    const data = await response.json();
    return data.roles; // Return the roles or handle as needed
  } else {
    throw new Error('Failed to fetch user info');
  }
}

function App() {
  let [roles, setRoles] = useState([]);
  const { csrfToken, updateCsrfToken } = useCsrf();

  useEffect(() => {
    fetchUserInfo()
      .then((extracted_roles) => {
        setRoles(extracted_roles);
      })
      .catch((error) => {
        console.error(error);
      });
  }, []);

  useEffect(() => {
    axios.get(`${SERVER_URL}/csrf-token`, { withCredentials: true })
      .then(response => {
        updateCsrfToken(response.data.csrf_token);
      })
      .catch(error => console.error('Error fetching CSRF token:', error));
  }, [updateCsrfToken, roles]);

  return (
    <div className="App">
      <Router>
        {roles.length > 0 ? <Navigation roles={roles} setRoles={setRoles} /> : <div></div>}
        <Routes>
          <Route exact path="/" element={roles.length > 0 ? <HomePage /> : <Navigate to="/authentication" replace />} />
          <Route path="/authentication" element={roles.length > 0 ? <Navigate to="/" replace /> : <LoginPage setRoles={setRoles} />} />
          <Route path="/create_product" element={roles.length > 0 ? <CreateProductForm roles={roles} /> : <Navigate to="/authentication" replace />} />
          <Route path="/product_list" element={roles.length > 0 ? <ProductList /> : <Navigate to="/authentication" replace />} />
          <Route path="/product_details/:productId" element={roles.length > 0 ? <ProductDetailsPage roles={roles} /> : <Navigate to="/authentication" replace />} />
          <Route path="/product_update/:productId" element={roles.length > 0 ? <ProductUpdatePage /> : <Navigate to="/authentication" replace />} />

          {/* New Routes for Order Management */}
          <Route path="/create_order" element={roles.length > 0 ? <CreateOrder roles={roles} /> : <Navigate to="/authentication" replace />} />
        
          <Route path="/orders" element={roles.length > 0 ? <GetOrders roles={roles} /> : <Navigate to="/authentication" replace />} />
          <Route path="/edit_order" element={roles.length > 0 ? <EditOrderButton roles={roles} /> : <Navigate to="/authentication" replace />} />
          {/* Invoice Routes */}
          <Route path="/invoices" element={roles.length > 0 ? <InvoiceList roles={roles} /> : <Navigate to="/authentication" replace />} />
          <Route path="/returns" element={roles.length > 0 ? <Returns roles={roles} /> : <Navigate to="/authentication" replace />} />
              {/* New Inventory Routes */}
              <Route path="/inventory/reports"
                element={roles.length > 0 ? <InventoryReports roles={roles}/> : <Navigate to="/authentication" replace />} />
              <Route path="/inventory/stock-levels"
                element={roles.length > 0 ? <StockLevels roles={roles}/> : <Navigate to="/authentication" replace />} />
              <Route path="/inventory/warehouses"
                element={roles.length > 0 ? <Warehouses roles={roles}/> : <Navigate to="/authentication" replace />} />        </Routes>
      </Router>
    </div>
  );
}

export default App;
