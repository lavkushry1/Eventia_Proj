import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';

interface AdminAuthState {
  isAuthenticated: boolean;
  checkingAuth: boolean;
  error: string | null;
}

export function useAdminAuth() {
  const [authState, setAuthState] = useState<AdminAuthState>({
    isAuthenticated: false,
    checkingAuth: true,
    error: null,
  });
  const navigate = useNavigate();

  useEffect(() => {
    const checkAuth = () => {
      try {
        // Get token from localStorage
        const token = localStorage.getItem('token');
        
        if (!token) {
          setAuthState({
            isAuthenticated: false,
            checkingAuth: false,
            error: 'No authentication token found',
          });
          return;
        }
        
        // Check if token is expired by trying to parse it
        // This is a simple check, for a real app you should validate the token properly
        try {
          // JWT tokens are base64 encoded and have 3 parts separated by dots
          const tokenParts = token.split('.');
          if (tokenParts.length !== 3) {
            throw new Error('Invalid token format');
          }
          
          // Parse the payload (second part)
          const payload = JSON.parse(atob(tokenParts[1]));
          
          // Check if token has expired
          if (payload.exp && payload.exp * 1000 < Date.now()) {
            throw new Error('Token has expired');
          }
          
          // Token is valid
          setAuthState({
            isAuthenticated: true,
            checkingAuth: false,
            error: null,
          });
        } catch (error) {
          // Token is invalid or expired
          localStorage.removeItem('token');
          setAuthState({
            isAuthenticated: false,
            checkingAuth: false,
            error: 'Authentication token is invalid or expired',
          });
        }
      } catch (error) {
        console.error('Error checking authentication:', error);
        setAuthState({
          isAuthenticated: false,
          checkingAuth: false,
          error: 'Error checking authentication',
        });
      }
    };
    
    checkAuth();
  }, []);
  
  const login = (token: string) => {
    localStorage.setItem('token', token);
    setAuthState({
      isAuthenticated: true,
      checkingAuth: false,
      error: null,
    });
  };
  
  const logout = () => {
    localStorage.removeItem('token');
    setAuthState({
      isAuthenticated: false,
      checkingAuth: false,
      error: null,
    });
    navigate('/admin/login');
  };
  
  return {
    ...authState,
    login,
    logout,
  };
} 