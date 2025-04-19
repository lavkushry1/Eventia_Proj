import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { createBooking, fetchBooking, verifyPayment } from '@/lib/api';
import type { BookingRequest, BookingResponse, PaymentRequest, PaymentResponse } from '@/lib/types';

export function useBooking(bookingId: string) {
  return useQuery({
    queryKey: ['bookings', bookingId],
    queryFn: () => fetchBooking(bookingId),
    enabled: !!bookingId,
  });
}

export function useCreateBooking() {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: createBooking,
    onSuccess: (data) => {
      queryClient.invalidateQueries({ queryKey: ['bookings', data.booking_id] });
    },
  });
}

export function useVerifyPayment() {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: verifyPayment,
    onSuccess: (data, variables) => {
      queryClient.invalidateQueries({ queryKey: ['bookings', variables.booking_id] });
    },
  });
} 