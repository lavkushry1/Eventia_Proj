import React, { useEffect } from 'react';
import { Navigate, useLocation } from 'react-router-dom';
import { useAdminAuth } from '@/hooks/use-admin-auth';
import { Loader2 } from 'lucide-react';
import { toast } from '@/hooks/use-toast';

interface AdminProtectedRouteProps {
  children: React.ReactNode;
}

const AdminProtectedRoute: React.FC<AdminProtectedRouteProps> = ({ children }) => {
  const { isLoggedIn, adminToken } = useAdminAuth();
  const location = useLocation();

  useEffect(() => {
    if (!isLoggedIn) {
      toast({
        title: "Authentication required",
        description: "Please log in as an admin to access this page",
        variant: "destructive"
      });
    }
  }, [isLoggedIn]);

  // Check if we're still checking authentication
  if (adminToken === null && localStorage.getItem('admin_token')) {
    return (
      <div className="w-full h-screen flex items-center justify-center">
        <div className="text-center">
          <Loader2 className="h-8 w-8 animate-spin mx-auto mb-4 text-primary" />
          <p>Verifying authentication...</p>
        </div>
      </div>
    );
  }

  // If not logged in, redirect to the login page
  if (!isLoggedIn) {
    return <Navigate to="/admin/login" state={{ from: location }} replace />;
  }

  // If authenticated, render the children
  return <>{children}</>;
};

export default AdminProtectedRoute; 