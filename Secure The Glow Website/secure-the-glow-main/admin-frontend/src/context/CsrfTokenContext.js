import React, { createContext, useContext, useState } from 'react';

const CsrfContext = createContext(null);

export const CsrfProvider = ({ children }) => {
    const [csrfToken, setCsrfToken] = useState(null);

    const updateCsrfToken = (token) => {
        setCsrfToken(token);
    };

    return (
        <CsrfContext.Provider value={{ csrfToken, updateCsrfToken }}>
            {children}
        </CsrfContext.Provider>
    );
};

export const useCsrf = () => useContext(CsrfContext);