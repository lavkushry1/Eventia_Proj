import axios, { AxiosError } from 'axios';
import configManager from './config';
import type {
  EventList, 
  EventResponse, 
  StadiumList, 
  Stadium, 
  SeatViewImageList,
  TeamList,
  BookingRequest,
  BookingResponse,
  PaymentRequest,
  PaymentResponse,
  PaymentSettingsResponse,
  AdminLoginRequest,
  AdminLoginResponse,
  DashboardStats
} from './types';
import { mapApiResponseToFrontendModel } from './adapters';

// Define types for API responses
export interface ApiEvent {
  id: string;
  name: string;
  description?: string;
  start_date?: string;
  end_date?: string;
  venue_id?: string;
  poster_url?: string;
  category?: string;
  featured?: boolean;
  status?: string;
  team_ids?: string[];
  ticket_types?: Array<{
    name: string;
    price: number;
    available: number;
  }>;
}

export interface ApiBookingResponse {
  booking_id: string;
  event_id: string;
  customer_info: any;
  selected_tickets: any[];
  total_amount: number;
  status: string;
  payment_info?: any;
  created_at?: string;
  updated_at?: string;
}

interface EventQueryParams {
  category?: string;
  featured?: boolean;
  page?: number;
  limit?: number;
  search?: string;
  sort?: string;
  order?: 'asc' | 'desc';
}

interface StadiumQueryParams {
  search?: string;
  sort?: string;
  order?: 'asc' | 'desc';
}

interface TeamQueryParams {
  search?: string;
  sort?: string;
  order?: 'asc' | 'desc';
}

// Helper function to get image URL
export const getImageUrl = (imagePath: string): string => {
  const baseUrl = configManager.config().staticUrl || '';
  
  if (!imagePath) return '/placeholder.svg';
  if (imagePath.startsWith('http') || imagePath.startsWith('/assets')) {
    return imagePath;
  }
  
  return `${baseUrl}${imagePath.startsWith('/') ? '' : '/'}${imagePath}`;
};

// Create axios instance with default configuration
export const api = axios.create({
  baseURL: 'http://localhost:3000/api/v1',
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add response interceptor for logging and debugging
api.interceptors.response.use(
  (response) => {
    console.debug(`API Response [${response.config.method?.toUpperCase()}] ${response.config.url}:`, response.data);
    return response;
  },
  (error: AxiosError) => {
    console.error(`API Error [${error.config?.method?.toUpperCase()}] ${error.config?.url}:`, {
      status: error.response?.status,
      data: error.response?.data,
      message: error.message
    });
    return Promise.reject(error);
  }
);

// Add request interceptor for logging
api.interceptors.request.use(
  (config) => {
    console.debug(`API Request [${config.method?.toUpperCase()}] ${config.url}:`, {
      params: config.params,
      data: config.data
    });
    return config;
  },
  (error) => {
    console.error('API Request Error:', error);
    return Promise.reject(error);
  }
);

// Event API calls
export const fetchEvents = async (params: EventQueryParams = {}): Promise<EventList> => {
  try {
    const { data } = await api.get('/events', { params });

    // Handle different response formats
    // If backend returns items property (paginated response)
    const events = data.items || data.events || [];
    
    // Map each event to the standard format
    const standardizedEvents = events.map((event: any) => mapApiResponseToFrontendModel(event));
    
    return {
      events: standardizedEvents,
      total: data.total || events.length,
      skip: data.skip || 0,
      limit: data.limit || events.length
    };
  } catch (error) {
    console.error('Error fetching events:', error);
    // Return empty result on error
    return {
      events: [],
      total: 0,
      skip: 0,
      limit: 10
    };
  }
};

export const fetchEvent = async (eventId: string): Promise<EventResponse> => {
  try {
    const { data } = await api.get(`/events/${eventId}`);
    
    // Handle different response formats
    // If data is nested under 'data' property (common pattern)
    const eventData = data.data || data;
    
    // Return standardized event
    return mapApiResponseToFrontendModel(eventData);
  } catch (error) {
    console.error(`Error fetching event ${eventId}:`, error);
    throw error;
  }
};

// Stadium API calls
export const fetchStadiums = async (): Promise<StadiumList> => {
  try {
    const { data } = await api.get('/stadiums');
    
    // Process image URLs
    const stadiums = (data.items || data.stadiums || []).map((stadium: Stadium) => ({
      ...stadium,
      image_url: stadium.image_url ? getImageUrl(stadium.image_url) : undefined,
    }));
    
    return {
      stadiums,
      total: data.total || stadiums.length,
      skip: data.skip || 0,
      limit: data.limit || stadiums.length
    };
  } catch (error) {
    console.error('Error fetching stadiums:', error);
    return {
      stadiums: [],
      total: 0,
      skip: 0,
      limit: 10
    };
  }
};

export const fetchStadium = async (stadiumId: string): Promise<Stadium> => {
  try {
    const { data } = await api.get(`/stadiums/${stadiumId}`);
    
    // Handle nested data
    const stadium = data.data || data;
    
    // Process image URLs
    return {
      ...stadium,
      image_url: stadium.image_url ? getImageUrl(stadium.image_url) : undefined,
      sections: (stadium.sections || []).map((section: any) => ({
        ...section,
        image_url: section.image_url ? getImageUrl(section.image_url) : undefined,
      })),
    };
  } catch (error) {
    console.error(`Error fetching stadium ${stadiumId}:`, error);
    throw error;
  }
};

export const fetchSeatViewImages = async (stadiumId: string, sectionId: string): Promise<SeatViewImageList> => {
  const { data } = await api.get(`/api/stadiums/${stadiumId}/sections/${sectionId}/views`);

  // Process image URLs
  data.views = data.views.map(view => ({
    ...view,
    image_url: getImageUrl(view.image_url),
  }));

  return data;
};

// Team API calls
export const fetchTeams = async (params: TeamQueryParams = {}): Promise<TeamList> => {
  const { data } = await api.get('/api/teams', { params });

  // Process logo URLs
  data.teams = data.teams.map(team => ({
    ...team,
    logo: getImageUrl(team.logo),
  }));

  return data;
};

// Booking API calls
export const createBooking = async (bookingData: BookingRequest): Promise<BookingResponse> => {
  const { data } = await api.post('/api/bookings', bookingData);
  return data;
};

export const fetchBooking = async (bookingId: string): Promise<BookingResponse> => {
  const { data } = await api.get(`/api/bookings/${bookingId}`);

  // Process QR code URL if present
  if (data.qr_code) {
    data.qr_code = getImageUrl(data.qr_code);
  }

  return data;
};

// Payment API calls
export const verifyPayment = async (paymentData: PaymentRequest): Promise<PaymentResponse> => {
  const { data } = await api.post('/api/payments/verify', paymentData);
  return data;
};

export const fetchPaymentSettings = async (): Promise<PaymentSettingsResponse> => {
  const { data } = await api.get('/api/payments/settings');

  // Process QR image URL
  data.qr_image = getImageUrl(data.qr_image);

  return data;
};

// Admin API calls
export const adminLogin = async (credentials: AdminLoginRequest): Promise<AdminLoginResponse> => {
  const { data } = await api.post('/api/admin/login', credentials);

  // Store token in localStorage
  if (data.token) {
    localStorage.setItem('admin_token', data.token);
  }

  return data;
};

export const fetchDashboardStats = async (): Promise<DashboardStats> => {
  const { data } = await api.get('/api/admin/dashboard/stats');
  return data;
};

export const adminLogout = (): void => {
  localStorage.removeItem('admin_token');
  window.location.href = '/admin/login';
};

export const adminUploadQRImage = async (file: File): Promise<{ filename: string }> => {
    const formData = new FormData();
  formData.append('file', file);
  const { data } = await api.post('/api/admin/upload/qr', formData, {
      headers: {
      'Content-Type': 'multipart/form-data',
    },
  });
  return data;
};

export default api;
