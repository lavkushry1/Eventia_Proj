import { useQuery, useMutation } from '@tanstack/react-query';
import { queryClient } from './use-queries';
import { 
  adminLogin, 
  adminLoginWithCredentials, 
  adminFetchEvents, 
  adminCreateEvent, 
  adminUpdateEvent, 
  adminDeleteEvent, 
  adminFetchBookings,
  adminUpdatePaymentSettings,
  getImageUrl
} from '../lib/api';

/**
 * Hook for admin login with token
 */
export function useAdminLogin() {
  return useMutation({
    mutationFn: (token: string) => adminLogin(token),
    onSuccess: () => {
      // Clear and refetch admin data on successful login
      queryClient.invalidateQueries({ queryKey: ['admin'] });
    }
  });
}

/**
 * Hook for admin login with credentials
 */
export function useAdminLoginWithCredentials() {
  return useMutation({
    mutationFn: ({ username, password }: { username: string; password: string }) => 
      adminLoginWithCredentials(username, password),
    onSuccess: () => {
      // Clear and refetch admin data on successful login
      queryClient.invalidateQueries({ queryKey: ['admin'] });
    }
  });
}

/**
 * Hook to fetch events for admin
 */
export function useAdminEvents(page = 1, limit = 20) {
  return useQuery({
    queryKey: ['admin', 'events', page, limit],
    queryFn: () => adminFetchEvents(page, limit),
    select: (data) => ({
      ...data,
      events: data.events?.map(event => ({
        ...event,
        // Ensure image URLs are absolute
        image_url: getImageUrl('events', event.image_url),
        teams: event.teams ? {
          home: {
            ...event.teams.home,
            logo: getImageUrl('teams', event.teams.home?.logo)
          },
          away: {
            ...event.teams.away,
            logo: getImageUrl('teams', event.teams.away?.logo)
          }
        } : undefined
      })) || []
    })
  });
}

/**
 * Hook to create an event (admin)
 */
export function useCreateEvent() {
  return useMutation({
    mutationFn: adminCreateEvent,
    onSuccess: () => {
      // Invalidate relevant queries on success
      queryClient.invalidateQueries({ queryKey: ['admin', 'events'] });
      queryClient.invalidateQueries({ queryKey: ['events'] });
    }
  });
}

/**
 * Hook to update an event (admin)
 */
export function useUpdateEvent() {
  return useMutation({
    mutationFn: ({ eventId, eventData }: { eventId: string; eventData: any }) => 
      adminUpdateEvent(eventId, eventData),
    onSuccess: (_, variables) => {
      // Invalidate relevant queries on success
      queryClient.invalidateQueries({ queryKey: ['admin', 'events'] });
      queryClient.invalidateQueries({ queryKey: ['events'] });
      queryClient.invalidateQueries({ queryKey: ['event', variables.eventId] });
    }
  });
}

/**
 * Hook to delete an event (admin)
 */
export function useDeleteEvent() {
  return useMutation({
    mutationFn: (eventId: string) => adminDeleteEvent(eventId),
    onSuccess: () => {
      // Invalidate relevant queries on success
      queryClient.invalidateQueries({ queryKey: ['admin', 'events'] });
      queryClient.invalidateQueries({ queryKey: ['events'] });
    }
  });
}

/**
 * Hook to fetch bookings for admin
 */
export function useAdminBookings(page = 1, limit = 20) {
  return useQuery({
    queryKey: ['admin', 'bookings', page, limit],
    queryFn: () => adminFetchBookings(page, limit)
  });
}

/**
 * Hook to update payment settings (admin)
 */
export function useUpdatePaymentSettings() {
  return useMutation({
    mutationFn: (settings: any) => adminUpdatePaymentSettings(settings),
    onSuccess: () => {
      // Invalidate payment settings query
      queryClient.invalidateQueries({ queryKey: ['paymentSettings'] });
    }
  });
}