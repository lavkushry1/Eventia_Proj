import axios from 'axios';
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

// Create axios instance with default configuration
export const api = axios.create({
  baseURL: configManager.getApiUrl(''),
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add request interceptor for authentication
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('admin_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
});

// Add response interceptor for error handling
api.interceptors.response.use(
  (response) => response,
  (error) => {
    // Handle session expiry
    if (error.response && error.response.status === 401) {
      // Check if the error is on an admin route
      if (error.config.url.includes('/admin')) {
        localStorage.removeItem('admin_token');
        window.location.href = '/admin/login';
      }
    }
    return Promise.reject(error);
  }
);

// Handle image URLs to ensure they have proper base URL
export const getImageUrl = (path: string | undefined | null): string => {
  if (!path) return '';

  // Return as is if it's already an absolute URL
  if (path.startsWith('http://') || path.startsWith('https://')) {
    return path;
  }

  // Add API_BASE_URL if it's a relative path
  if (path.startsWith('/')) {
    return configManager.getApiUrl(path);
  }

  // Add static path for other cases
  return `${configManager.getConfig().STATIC_URL}/${path}`;
};

// Event API calls
export const fetchEvents = async (params: EventQueryParams = {}): Promise<EventList> => {
  const { data } = await api.get('/api/events', { params });

  // Process image URLs in the response
  data.events = data.events.map((event: EventResponse) => ({
    ...event,
    posterImage: event.posterImage ? getImageUrl(event.posterImage) : '',
    teamOneLogo: event.teamOneLogo ? getImageUrl(event.teamOneLogo) : '',
    teamTwoLogo: event.teamTwoLogo ? getImageUrl(event.teamTwoLogo) : '',
  }));

  return data;
};

export const fetchEvent = async (eventId: string): Promise<EventResponse> => {
  const { data } = await api.get(`/api/events/${eventId}`);

  // Process image URLs
  return {
    ...data,
    posterImage: data.posterImage ? getImageUrl(data.posterImage) : '',
    teamOneLogo: data.teamOneLogo ? getImageUrl(data.teamOneLogo) : '',
    teamTwoLogo: data.teamTwoLogo ? getImageUrl(data.teamTwoLogo) : '',
  };
};

// Stadium API calls
export const fetchStadiums = async (params: StadiumQueryParams = {}): Promise<StadiumList> => {
  const { data } = await api.get('/api/stadiums', { params });

  // Process image URLs
  data.stadiums = data.stadiums.map((stadium: Stadium) => ({
    ...stadium,
    image_url: stadium.image_url ? getImageUrl(stadium.image_url) : '',
    sections: stadium.sections?.map(section => ({
      ...section,
      image_url: section.image_url ? getImageUrl(section.image_url) : '',
      views: section.views?.map(view => ({
        ...view,
        image_url: getImageUrl(view.image_url),
      })),
    })),
  }));

  return data;
};

export const fetchStadium = async (stadiumId: string): Promise<Stadium> => {
  const { data } = await api.get(`/api/stadiums/${stadiumId}`);

  // Process image URLs
  return {
    ...data,
    image_url: data.image_url ? getImageUrl(data.image_url) : '',
    sections: data.sections?.map(section => ({
      ...section,
      image_url: section.image_url ? getImageUrl(section.image_url) : '',
      views: section.views?.map(view => ({
        ...view,
        image_url: getImageUrl(view.image_url),
      })),
    })),
  };
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
