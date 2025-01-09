import React from 'react';

// Higher-Order Component to restrict page based on roles
const withAuthorization = (allowedRoles) => (WrappedComponent) => {
  return (props) => {
    const userRoles = props.roles || []; // Pass roles as a prop or use context

    // Check if the user has any of the allowed roles
    const isAuthorized = allowedRoles.some(role => userRoles.includes(role));

    if (!isAuthorized) {
      return <div>You do not have permission to access this page.</div>;
    }

    return <WrappedComponent {...props} />;
  };
};


export  {withAuthorization};