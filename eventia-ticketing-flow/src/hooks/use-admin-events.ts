import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { adminLogin, adminLogout, fetchDashboardStats } from '@/lib/api';
import type { AdminLoginRequest, AdminLoginResponse, DashboardStats } from '@/lib/types';

export function useAdminLogin() {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: adminLogin,
    onSuccess: (data) => {
      if (data.token) {
        localStorage.setItem('admin_token', data.token);
      }
    },
  });
}

export function useAdminLogout() {
  const queryClient = useQueryClient();
  
  return () => {
    adminLogout();
    queryClient.clear();
  };
}

export function useDashboardStats() {
  return useQuery({
    queryKey: ['admin', 'dashboard', 'stats'],
    queryFn: fetchDashboardStats,
  });
}

// Note: Additional admin event mutations will be added here
// once the backend API endpoints are implemented 