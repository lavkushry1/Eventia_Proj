import { useQuery, useMutation, QueryClient } from '@tanstack/react-query';
import { 
  fetchEvents, 
  fetchEvent, 
  fetchPaymentSettings, 
  createBooking, 
  fetchBooking, 
  verifyPayment, 
  getImageUrl 
} from '../lib/api';
import { EventResponse, EventList, BookingCreate, BookingResponse, PaymentSettingsResponse } from '../lib/types';

// Initialize React Query client - typically you would do this in a provider
export const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      refetchOnWindowFocus: false,
      retry: 1,
      staleTime: 5 * 60 * 1000, // 5 minutes
    },
  },
});

/**
 * Hook to fetch a list of events
 */
export function useEvents(category?: string, featured?: boolean) {
  return useQuery({
    queryKey: ['events', { category, featured }],
    queryFn: () => fetchEvents(category, featured),
    select: (data: EventList) => ({
      events: data.events?.map(event => ({
        ...event,
        // Ensure image URLs are absolute and have fallbacks
        image_url: getImageUrl('events', event.image_url),
        teams: event.teams ? {
          home: {
            ...event.teams.home,
            logo: getImageUrl('teams', event.teams.home.logo)
          },
          away: {
            ...event.teams.away,
            logo: getImageUrl('teams', event.teams.away.logo)
          }
        } : undefined
      })) || [],
      total: data.total || 0
    })
  });
}

/**
 * Hook to fetch a single event by ID
 */
export function useEvent(eventId: string) {
  return useQuery({
    queryKey: ['event', eventId],
    queryFn: () => fetchEvent(eventId),
    enabled: !!eventId,
    select: (data: EventResponse) => ({
      ...data,
      // Ensure image URLs are absolute and have fallbacks
      image_url: getImageUrl('events', data.image_url),
      teams: data.teams ? {
        home: {
          ...data.teams.home,
          logo: getImageUrl('teams', data.teams.home.logo)
        },
        away: {
          ...data.teams.away,
          logo: getImageUrl('teams', data.teams.away.logo)
        }
      } : undefined
    })
  });
}

/**
 * Hook to fetch booking details by ID
 */
export function useBooking(bookingId: string) {
  return useQuery({
    queryKey: ['booking', bookingId],
    queryFn: () => fetchBooking(bookingId),
    enabled: !!bookingId,
  });
}

/**
 * Hook to fetch payment settings
 */
export function usePaymentSettings() {
  return useQuery({
    queryKey: ['paymentSettings'],
    queryFn: fetchPaymentSettings,
    select: (data: PaymentSettingsResponse) => ({
      ...data,
      // If there's a QR image URL, make sure it's absolute
      qrImageUrl: data.qrImageUrl ? getImageUrl('payments', data.qrImageUrl) : undefined
    })
  });
}

/**
 * Hook to create a booking
 */
export function useCreateBooking() {
  return useMutation({
    mutationFn: (bookingData: BookingCreate) => createBooking(bookingData),
    onSuccess: () => {
      // Invalidate relevant queries when a new booking is created
      queryClient.invalidateQueries({ queryKey: ['events'] });
    },
  });
}

/**
 * Hook to verify payment (UTR submission)
 */
export function useVerifyPayment() {
  return useMutation({
    mutationFn: verifyPayment,
    onSuccess: (data, variables) => {
      // Invalidate the specific booking query when payment is verified
      queryClient.invalidateQueries({ queryKey: ['booking', variables.booking_id] });
    },
  });
}