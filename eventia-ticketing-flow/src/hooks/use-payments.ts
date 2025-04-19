import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { fetchPaymentSettings } from '@/lib/api';
import type { PaymentSettingsResponse } from '@/lib/types';

export function usePaymentSettings() {
  return useQuery({
    queryKey: ['payments', 'settings'],
    queryFn: fetchPaymentSettings,
  });
}

// Note: Additional payment mutations will be added here
// once the backend API endpoints are implemented 