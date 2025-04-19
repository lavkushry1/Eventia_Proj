import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import configManager from '@/config';
import type { EventResponse, EventList } from '@/lib/types';
import { apiClient } from '@/lib/api';

// Get the API client and config
const config = configManager.config();

/**
 * Hook to fetch a list of events
 */
export function useEvents(options = {}) {
  const { 
    category, 
    featured = false,
    limit = 10,
    skip = 0,
    enabled = true 
  } = options;
  
  return useQuery({
    queryKey: ['events', { category, featured, limit, skip }],
    queryFn: async () => {
      const params = new URLSearchParams();
      if (category) params.append('category', category);
      if (featured) params.append('featured', 'true');
      params.append('limit', String(limit));
      params.append('skip', String(skip));
      
      const { data } = await apiClient.get(`/api/events?${params.toString()}`);
      
      // Process image URLs
      return {
        ...data,
        events: data.events.map((event: EventResponse) => ({
          ...event,
          image_url: event.image_url ? configManager.getStaticUrl('events', event.image_url) : '',
          teams: event.teams ? {
            home: {
              ...event.teams.home,
              logo: event.teams.home.logo ? configManager.getStaticUrl('teams', event.teams.home.logo) : '',
            },
            away: {
              ...event.teams.away,
              logo: event.teams.away.logo ? configManager.getStaticUrl('teams', event.teams.away.logo) : '',
            }
          } : undefined
        }))
      };
    },
    enabled,
  });
}

/**
 * Hook to fetch a single event
 */
export function useEvent(eventId: string, options = {}) {
  const { enabled = true } = options;
  
  return useQuery({
    queryKey: ['event', eventId],
    queryFn: async () => {
      const { data } = await apiClient.get(`/api/events/${eventId}`);
      
      // Process image URLs
      return {
        ...data,
        image_url: data.image_url ? configManager.getStaticUrl('events', data.image_url) : '',
        teams: data.teams ? {
          home: {
            ...data.teams.home,
            logo: data.teams.home.logo ? configManager.getStaticUrl('teams', data.teams.home.logo) : '',
          },
          away: {
            ...data.teams.away,
            logo: data.teams.away.logo ? configManager.getStaticUrl('teams', data.teams.away.logo) : '',
          }
        } : undefined
      };
    },
    enabled: enabled && !!eventId,
  });
}

/**
 * Hook to create an event (admin)
 */
export function useCreateEvent() {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: async (eventData: any) => {
      const { data } = await apiClient.post('/api/admin/events', eventData);
      return data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['events'] });
    },
  });
}

/**
 * Hook to update an event (admin)
 */
export function useUpdateEvent() {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: async ({ eventId, eventData }: { eventId: string, eventData: any }) => {
      const { data } = await apiClient.put(`/api/admin/events/${eventId}`, eventData);
      return data;
    },
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: ['events'] });
      queryClient.invalidateQueries({ queryKey: ['event', variables.eventId] });
    },
  });
}

/**
 * Hook to delete an event (admin)
 */
export function useDeleteEvent() {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: async (eventId: string) => {
      const { data } = await apiClient.delete(`/api/admin/events/${eventId}`);
      return data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['events'] });
    },
  });
}