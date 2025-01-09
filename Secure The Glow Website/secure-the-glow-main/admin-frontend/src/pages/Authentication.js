import './Authentication.css'
import React from 'react';
import { useState, useEffect } from "react";
import Button from '@mui/material/Button';
import TextField from '@mui/material/TextField'; 
import {SERVER_URL} from '../App'
import { Link } from 'react-router-dom';
import { useNavigate  } from 'react-router-dom';



const LoginPage = ({ setRoles }) => {
  const navigate = useNavigate ();

  let [email, setEmail] = useState(""); 
  let [password, setPassword] = useState("");
  let [first_name, setFirstName] = useState(""); 
  let [last_name, setLastName] = useState("");
  let [error, setError] = useState("");
  let errorMessage = "Invalid Credentials";
  let [forgotPassword, setForgotPassword] = useState(false);
  let [newPassword, setNewPassword] = useState("");
  let [confirmNewPassword, setConfirmNewPassword] = useState("");
  let [code, setCode] = useState("");
  let [resetPassEmail, setResetPassEmail] = useState("");
  let [codeMessage, setCodeMessage] = useState("");
  let [resetMessage, setResetMessage] = useState("");


  function checkPasswordStrength(pwd){
    const lengthCriteria = pwd.length >= 8;
    const uppercaseCriteria = /[A-Z]/.test(pwd);
    const lowercaseCriteria = /[a-z]/.test(pwd);
    const digitCriteria = /\d/.test(pwd);
    const specialCharCriteria = /[!@#$%^&*(),.?":{}|<>]/.test(pwd);

    const isStrong = lengthCriteria && uppercaseCriteria && lowercaseCriteria && digitCriteria && specialCharCriteria;
    return isStrong
  }

  function resetPassword(){
    if (!checkPasswordStrength(newPassword)){
      setResetMessage("Weak Password");
      return
    }
    if (newPassword != confirmNewPassword){
      setResetMessage("The passwords don't match");
      return
    }
    return fetch(`${SERVER_URL}/reset_password`, { 
      method: "PUT", 
      headers: { 
        "Content-Type": "application/json", 
      }, 
      body: JSON.stringify({ 
        email: email, 
        code: code,
        password: newPassword 
      }), 
    }) 
      .then((response) => {
        if (!response.ok){
            setResetMessage("Please follow the instructions carefully")
            return null
        }
        else{
          setResetMessage("Password reset successfully. Please log in.");            
        }
      });
  }
  function sendCode(){
    return fetch(`${SERVER_URL}/forgot_password`, { 
      method: "POST", 
      headers: { 
        "Content-Type": "application/json", 
      }, 
      body: JSON.stringify({ 
        email: resetPassEmail,  
      }), 
    }) 
      .then((response) => {
          setCodeMessage("Code Sent");    
      }); 
  }
  function login(email, password) { 
    
    return fetch(`${SERVER_URL}/authenticate_employee`, { 
      method: "POST", 
      credentials: 'include',
      headers: { 
        "Content-Type": "application/json", 
      }, 
      body: JSON.stringify({ 
        email: email, 
        password: password, 
      }), 
    }) 
      .then((response) => {
        if (!response.ok){
            setError(errorMessage);
            return null
        }
        else{
            setError("");
            return response.json();
            
        }
      }).then((data) => {
        if (data){
            setRoles(data.roles);
            navigate("/")
        }
      }); 
  }

  return ( <div>{!forgotPassword ? 
    (<div className="login-container">
        <div className='login-form'>      {/* This is displayed ig the user wants to login */}
            <h2 style={{ textAlign: 'center', fontFamily: 'Garamond, serif' }}>Login</h2>
                  <div className="login-form-item"> 
                    <TextField 
                      fullWidth 
                      label="Email" 
                      type="text" 
                      value={email} 
                      onChange={({ target: { value } }) => setEmail(value)} 
                    /> 
                  </div> 
                  <div className="login-form-item"> 
                    <TextField 
                      fullWidth 
                      label="Password" 
                      type="password" 
                      value={password} 
                      onChange={({ target: { value } }) => setPassword(value)} 
                    /> 
                  </div> 
                  
                  <Button 
            className="login-button"
            type="submit"
            color="primary" 
            variant="contained" 
            onClick={() => login(email, password)} 
            
            > 
            Login
            </Button> 
                  <p  style={{color:"red", marginLeft:'0px'}}>{error}</p>
            <Link onClick={() => {setForgotPassword(true); setError("");}} >
                Forgot Password
            </Link>
            <p>Your account gets locked for 15 minutes after 7 wrong attempts</p>
        </div> 
    </div>):
    (<div className="reset-password-page">
      <p>
        <h1 style={{ textAlign: 'center', fontFamily: 'Garamond, serif' }}>
            Instructions
        </h1>
        <ul>
          <li>Enter an email to send the verification code to.</li>
          <li>The verification code expires after 5 minutes. If you get it wrong more than 3 times, you will have to request another code.</li>
          <li>
        Password Strength Criteria:
        <ul>
            <li>Be at least 8 characters long.</li>
            <li>Contain at least one uppercase letter.</li>
            <li>Contain at least one lowercase letter.</li>
            <li>Include at least one digit.</li>
            <li>Have at least one special character.</li>
        </ul>
    </li>

          
        </ul>
      </p>
    <div className="login-container">
      <div className='login-form'>
      <div className="login-form-item"> 
          <TextField 
            fullWidth 
            label="Email" 
            type="text" 
            value={resetPassEmail} 
            onChange={({ target: { value } }) => setResetPassEmail(value)} 
          /> 
        </div>
        <p  style={{color:"red", marginLeft:'0px'}}>{codeMessage}</p>
        <div className="login-form-item"> 
              <Button 
            className="login-button"
            type="submit"
            color="primary" 
            variant="contained" 
            onClick={() => sendCode(email, password)} 
            
            > 
            Send Verification Code
            </Button> 
        </div>
        
      </div>
      <div className='login-form'>
      <h2 style={{ textAlign: 'center', fontFamily: 'Garamond, serif' }}>Reset Password</h2>
        <div className="login-form-item"> 
          <TextField 
            fullWidth 
            label="Email" 
            type="text" 
            value={email} 
            onChange={({ target: { value } }) => setEmail(value)} 
          /> 
        </div> 
        <div className="login-form-item"> 
          <TextField 
            fullWidth 
            label="New Password" 
            type="password" 
            value={newPassword} 
            onChange={({ target: { value } }) => setNewPassword(value)} 
          /> 
        </div> 
        <div className="login-form-item"> 
          <TextField 
            fullWidth 
            label="Confirm New Password" 
            type="password" 
            value={confirmNewPassword} 
            onChange={({ target: { value } }) => setConfirmNewPassword(value)} 
          /> 
        </div> 
        <div className="login-form-item"> 
          <TextField 
            fullWidth 
            label="Verification Code" 
            type="password" 
            value={code} 
            onChange={({ target: { value } }) => setCode(value)} 
          /> 
        </div> 
        <p  style={{color:"red", marginLeft:'0px'}}>{resetMessage}</p>
        <div className="login-form-item"> 
        <Button 
        className="login-button"
        type="submit"
        color="primary" 
        variant="contained" 
        onClick={() => resetPassword(email, password)} 
        > 
        Reset Password
        </Button> 
        
        </div>
        <Link onClick={() => {setForgotPassword(false); setError("");}} >
                Log In Instead
          </Link>

      </div>

    </div>
    </div>)}
      </div> 

    
  );
};

export default LoginPage;