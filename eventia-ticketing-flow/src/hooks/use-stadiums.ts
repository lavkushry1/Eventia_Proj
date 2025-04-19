import { useQuery } from '@tanstack/react-query';
import { fetchStadiums, fetchStadium, fetchSeatViewImages } from '@/lib/api';
import type { StadiumList, Stadium, SeatViewImageList } from '@/lib/types';

interface StadiumQueryParams {
  search?: string;
  sort?: string;
  order?: 'asc' | 'desc';
}

/**
 * Hook to fetch all stadiums
 */
export function useStadiums(params: StadiumQueryParams = {}) {
  return useQuery({
    queryKey: ['stadiums', params],
    queryFn: () => fetchStadiums(params),
  });
}

/**
 * Hook to fetch a single stadium
 */
export function useStadium(stadiumId: string) {
  return useQuery({
    queryKey: ['stadiums', stadiumId],
    queryFn: () => fetchStadium(stadiumId),
    enabled: !!stadiumId,
  });
}

/**
 * Hook to fetch seat view images for a stadium section
 */
export function useSeatViewImages(stadiumId: string, sectionId: string) {
  return useQuery({
    queryKey: ['stadiums', stadiumId, 'sections', sectionId, 'views'],
    queryFn: () => fetchSeatViewImages(stadiumId, sectionId),
    enabled: !!stadiumId && !!sectionId,
  });
}