import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';

export const useAdminAuth = () => {
  const [adminToken, setAdminToken] = useState<string | null>(null);
  const [isLoggedIn, setIsLoggedIn] = useState(false);
  const navigate = useNavigate();

  useEffect(() => {
    // Check if token exists in localStorage
    const storedToken = localStorage.getItem('admin_token');
    if (storedToken) {
      setAdminToken(storedToken);
      setIsLoggedIn(true);
    }
  }, []);

  const login = (token: string) => {
    localStorage.setItem('admin_token', token);
    setAdminToken(token);
    setIsLoggedIn(true);
  };

  const logout = () => {
    localStorage.removeItem('admin_token');
    setAdminToken(null);
    setIsLoggedIn(false);
    navigate('/admin/login');
  };

  const requireAuth = () => {
    if (!isLoggedIn) {
      navigate('/admin/login');
      return false;
    }
    return true;
  };

  return {
    adminToken,
    isLoggedIn,
    login,
    logout,
    requireAuth
  };
}; 