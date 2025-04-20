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
  baseURL: configManager.config().apiUrl,
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
    // MOCK DATA: Return mock events instead of calling the API
    console.log("Using mock events data instead of API call");
    
    // Create mock events based on what we saw in the seed scripts
    const mockEvents = [
      {
        id: "mock-event-1",
        name: "IPL 2025: CSK vs MI",
        description: "Chennai Super Kings vs Mumbai Indians",
        start_date: new Date(2025, 3, 15, 19, 30).toISOString(),
        end_date: new Date(2025, 3, 15, 23, 0).toISOString(),
        poster_url: "/static/events/csk-vs-mi.jpg",
        category: "cricket",
        featured: true,
        status: "upcoming",
      },
      {
        id: "mock-event-2",
        name: "IPL 2025: RCB vs KKR",
        description: "Royal Challengers Bangalore vs Kolkata Knight Riders",
        start_date: new Date(2025, 3, 18, 19, 30).toISOString(),
        end_date: new Date(2025, 3, 18, 23, 0).toISOString(),
        poster_url: "/static/events/rcb-vs-kkr.jpg",
        category: "cricket",
        featured: true,
        status: "upcoming",
      },
      {
        id: "mock-event-3",
        name: "IPL 2025: MI vs RCB",
        description: "Mumbai Indians vs Royal Challengers Bangalore",
        start_date: new Date(2025, 3, 22, 15, 30).toISOString(),
        end_date: new Date(2025, 3, 22, 19, 0).toISOString(),
        poster_url: "/static/events/mi-vs-rcb.jpg",
        category: "cricket",
        featured: false,
        status: "upcoming",
      }
    ];
    
    // Map mock events to the expected format
    const standardizedEvents = mockEvents.map(event => mapApiResponseToFrontendModel(event));
    
    return {
      events: standardizedEvents,
      total: mockEvents.length,
      skip: 0,
      limit: mockEvents.length
    };
    
    /* ORIGINAL CODE - COMMENTED OUT
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
    */
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

// Add getEvent function that's being called from EventDetail.tsx
export const getEvent = async (eventId: string): Promise<EventResponse> => {
  try {
    console.log("Using mock data for individual event:", eventId);
    
    // Create more detailed mock events based on what we saw in the adapters
    const mockEvents = [
      {
        id: "mock-event-1",
        name: "IPL 2025: CSK vs MI",
        description: "Chennai Super Kings vs Mumbai Indians - Join us for this exciting IPL 2025 clash between two of the most successful teams in IPL history! The match will be held at the iconic Chidambaram Stadium in Chennai.",
        start_date: new Date(2025, 3, 15, 19, 30).toISOString(),
        end_date: new Date(2025, 3, 15, 23, 0).toISOString(),
        poster_url: "/assets/events/csk-vs-mi.jpg", // Use local assets
        category: "IPL",
        featured: true,
        status: "upcoming",
        venue: "M. A. Chidambaram Stadium, Chennai",
        venue_id: "venue-1",
        stadium_id: "stadium-1",
        team_home: {
          name: "Chennai Super Kings",
          code: "CSK",
          logo: "/assets/teams/csk.png",
          primary_color: "#FFFF00"
        },
        team_away: {
          name: "Mumbai Indians",
          code: "MI",
          logo: "/assets/teams/mi.png",
          primary_color: "#004BA0"
        },
        ticket_types: [
          { name: "VIP", price: 5000, available: 50 },
          { name: "Premium", price: 3000, available: 100 },
          { name: "Standard", price: 1500, available: 200 }
        ]
      },
      {
        id: "mock-event-2",
        name: "IPL 2025: RCB vs KKR",
        description: "Royal Challengers Bangalore vs Kolkata Knight Riders - Watch Virat Kohli lead RCB against KKR in this high-stakes IPL match at M. Chinnaswamy Stadium in Bangalore.",
        start_date: new Date(2025, 3, 18, 19, 30).toISOString(),
        end_date: new Date(2025, 3, 18, 23, 0).toISOString(),
        poster_url: "/assets/events/rcb-vs-kkr.jpg", // Use local assets
        category: "IPL",
        featured: true,
        status: "upcoming",
        venue: "M. Chinnaswamy Stadium, Bangalore",
        venue_id: "venue-2",
        stadium_id: "stadium-2",
        team_home: {
          name: "Royal Challengers Bangalore",
          code: "RCB",
          logo: "/assets/teams/rcb.png",
          primary_color: "#EC1C24"
        },
        team_away: {
          name: "Kolkata Knight Riders",
          code: "KKR",
          logo: "/assets/teams/kkr.png",
          primary_color: "#3A225D"
        },
        ticket_types: [
          { name: "VIP Box", price: 6000, available: 30 },
          { name: "Premium", price: 3500, available: 80 },
          { name: "Standard", price: 1800, available: 150 }
        ]
      },
      {
        id: "mock-event-3",
        name: "IPL 2025: MI vs RCB",
        description: "Mumbai Indians vs Royal Challengers Bangalore - Experience the thrill as Mumbai Indians face off against RCB at the Wankhede Stadium in this exciting evening match.",
        start_date: new Date(2025, 3, 22, 15, 30).toISOString(),
        end_date: new Date(2025, 3, 22, 19, 0).toISOString(),
        poster_url: "/assets/events/mi-vs-rcb.jpg", // Use local assets
        category: "IPL",
        featured: false,
        status: "upcoming",
        venue: "Wankhede Stadium, Mumbai",
        venue_id: "venue-3",
        stadium_id: "stadium-3",
        team_home: {
          name: "Mumbai Indians",
          code: "MI",
          logo: "/assets/teams/mi.png",
          primary_color: "#004BA0"
        },
        team_away: {
          name: "Royal Challengers Bangalore",
          code: "RCB",
          logo: "/assets/teams/rcb.png",
          primary_color: "#EC1C24"
        },
        ticket_types: [
          { name: "VIP", price: 4500, available: 40 },
          { name: "Premium", price: 2500, available: 100 },
          { name: "Standard", price: 1200, available: 200 }
        ]
      }
    ];
    
    // Find the event with the matching ID
    const event = mockEvents.find(event => event.id === eventId);
    
    if (!event) {
      throw new Error(`Event with ID ${eventId} not found`);
    }
    
    // Use the mapper function to convert from API format to frontend format
    return mapApiResponseToFrontendModel(event);
  } catch (error) {
    console.error(`Error fetching event ${eventId}:`, error);
    throw error;
  }
};

// Modify the fetchEvent function to use our new getEvent function
export const fetchEvent = async (eventId: string): Promise<EventResponse> => {
  return getEvent(eventId);
  
  /* ORIGINAL CODE - COMMENTED OUT
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
  */
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

// Extend AxiosInstance type to include our custom methods
declare module 'axios' {
  interface AxiosInstance {
    getEvent(eventId: string): Promise<EventResponse>;
  }
}

// Add getEvent to the api object
api.getEvent = getEvent;

export default api;
