import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { fetchEvents, fetchEvent } from '@/lib/api';
import type { EventList, EventResponse } from '@/lib/types';

interface EventQueryParams {
  category?: string;
  featured?: boolean;
  page?: number;
  limit?: number;
  search?: string;
  sort?: string;
  order?: 'asc' | 'desc';
}

export function useEvents(params: EventQueryParams = {}) {
  return useQuery({
    queryKey: ['events', params],
    queryFn: () => fetchEvents(params),
  });
}

export function useEvent(eventId: string) {
  return useQuery({
    queryKey: ['events', eventId],
    queryFn: () => fetchEvent(eventId),
    enabled: !!eventId,
  });
}

// Note: Admin event mutations will be implemented in a separate admin hooks file
// since they require admin authentication and have different endpoints 