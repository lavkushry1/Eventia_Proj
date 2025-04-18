/**
 * @Author: Roni Laukkarinen
 * @Date:   2025-04-18 17:01:14
 * @Last Modified by:   Roni Laukkarinen
 * @Last Modified time: 2025-04-19 00:11:11
 */
import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';

interface AdminAuthState {
  adminToken: string | null;
  isLoggedIn: boolean;
  checkingAuth: boolean;
  error: string | null;
}

/**
 * Unified admin authentication hook
 * Provides authentication state and methods for admin users
 * @returns Authentication state and methods
 */
export const useAdminAuth = () => {
  const [authState, setAuthState] = useState<AdminAuthState>({
    adminToken: null,
    isLoggedIn: false,
    checkingAuth: true,
    error: null
  });
  const navigate = useNavigate();

  useEffect(() => {
    // Check if token exists in localStorage
    const storedToken = localStorage.getItem('admin_token');
    if (storedToken) {
      setAuthState({
        adminToken: storedToken,
        isLoggedIn: true,
        checkingAuth: false,
        error: null
      });
    } else {
      setAuthState(prev => ({
        ...prev,
        checkingAuth: false
      }));
    }
  }, []);

  const login = (token: string) => {
    localStorage.setItem('admin_token', token);
    setAuthState({
      adminToken: token,
      isLoggedIn: true,
      checkingAuth: false,
      error: null
    });
  };

  const logout = () => {
    localStorage.removeItem('admin_token');
    setAuthState({
      adminToken: null,
      isLoggedIn: false,
      checkingAuth: false,
      error: null
    });
    navigate('/admin/login');
  };

  const requireAuth = () => {
    if (!authState.isLoggedIn && !authState.checkingAuth) {
      navigate('/admin/login');
      return false;
    }
    return true;
  };

  return {
    adminToken: authState.adminToken,
    isLoggedIn: authState.isLoggedIn,
    checkingAuth: authState.checkingAuth,
    error: authState.error,
    login,
    logout,
    requireAuth
  };
}; 