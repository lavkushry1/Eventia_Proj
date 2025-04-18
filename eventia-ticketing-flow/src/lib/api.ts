/**
 * @Author: Roni Laukkarinen
 * @Date:   2025-04-18 17:01:14
 * @Last Modified by:   Roni Laukkarinen
 * @Last Modified time: 2025-04-18 18:01:29
 */
import axios, { AxiosRequestConfig, AxiosResponse } from 'axios';
import configManager, { config } from '../config';
import { v4 as uuidv4 } from 'uuid';
import {
  EventResponse,
  EventCreate,
  EventUpdate,
  EventList,
  BookingCreate,
  BookingResponse,
  BookingList,
  BookingDetails,
  LoginRequest,
  Token,
  PaymentSettingsResponse,
  UTRSubmission
} from './types';

// Extend AxiosInstance type for our custom methods
declare module 'axios' {
  interface AxiosInstance {
    getEvent(eventId: string): Promise<EventResponse>;
    getEvents(category?: string): Promise<EventResponse[]>;
    getPaymentSettings(): Promise<ApiPaymentSettings>;
    adminLogin(token: string): Promise<Token>;
    adminLoginWithCredentials(username: string, password: string): Promise<Token>;
    getAnalytics(token: string): Promise<ApiAnalyticsResponse>;
    getPaymentMetrics(token: string): Promise<ApiPaymentMetricsResponse>;
    updatePaymentSettings(token: string, data: ApiUpdatePaymentSettingsRequest): Promise<ApiPaymentSettings>;
    bookTicket(bookingData: ApiBookingRequest): Promise<ApiBookingResponse>;
    submitUTR(data: UTRSubmission): Promise<ApiUTRResponse>;
    cleanupExpiredBookings(token: string): Promise<{
      success: boolean;
      message: string;
      expired_count: number;
      inventory_updated: number;
    }>;
  }
}

// Extend AxiosInstance for admin event updates
declare module 'axios' {
  interface AxiosInstance {
    updateEventVenue(eventId: string, venue: string): Promise<{ venue: string }>;
    uploadEventPoster(eventId: string, file: File): Promise<{ image_url: string }>;
  }
}

// Extend AxiosInstance for admin image uploads
declare module 'axios' {
  interface AxiosInstance {
    uploadEventLogo(eventId: string, file: File): Promise<{ logo_url: string }>;
  }
}

// Create axios instance with default config
const api = axios.create({
  baseURL: config().API_BASE_URL,
  timeout: 15000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add compatibility methods to api object
api.getEvent = (eventId: string) => fetchEvent(eventId);
api.getEvents = (category?: string) => fetchEvents(category);
api.getPaymentSettings = () => fetchPaymentSettings();
api.adminLogin = (token: string) => adminLogin(token);
api.adminLoginWithCredentials = (username: string, password: string) => adminLoginWithCredentials(username, password);
api.getAnalytics = (token: string) => {
  return api.get('/admin/analytics', {
    headers: { Authorization: `Bearer ${token}` }
  }).then(resp => resp.data);
};
api.getPaymentMetrics = (token: string) => {
  return api.get('/admin/payment-metrics', {
    headers: { Authorization: `Bearer ${token}` }
  }).then(resp => resp.data);
};
api.updatePaymentSettings = (token: string, data: Partial<ApiPaymentSettings>) => {
  return adminUpdatePaymentSettings(data);
};
api.bookTicket = (bookingData: ApiBookingRequest) => createBooking(bookingData);
api.submitUTR = (data: UTRSubmission) => verifyPayment(data);
api.cleanupExpiredBookings = (token: string) => {
  return api.post('/admin/bookings/cleanup', {}, {
    headers: { Authorization: `Bearer ${token}` }
  }).then(resp => resp.data);
};

// Admin-specific event updates
api.updateEventVenue = (eventId: string, venue: string) => {
  return api.put(`/api/events/${eventId}`, { venue }).then(resp => resp.data);
};

api.uploadEventPoster = (eventId: string, file: File) => {
  const formData = new FormData();
  formData.append('poster', file);
  return api.post(`/api/events/${eventId}/poster`, formData, {
    headers: { 'Content-Type': 'multipart/form-data' }
  }).then(resp => resp.data);
};

api.uploadEventLogo = (eventId: string, file: File) => {
  const formData = new FormData();
  formData.append('logo', file);
  return api.post(`/api/events/${eventId}/logo`, formData, {
    headers: { 'Content-Type': 'multipart/form-data' }
  }).then(resp => resp.data);
};

// Initialize the API with token from localStorage if available
const token = localStorage.getItem('token');
if (token) {
  api.defaults.headers.common['Authorization'] = `Bearer ${token}`;
}

export { api };
export default api;

// Utility marker for performance tracking
export function perfMark(name: string): void {
  if (typeof performance !== 'undefined' && performance.mark) {
    performance.mark(name);
  }
}

// Add request interceptor for logging and performance tracking
api.interceptors.request.use(
  (config) => {
    // Generate a correlation ID for request tracing
    const correlationId = `req-${Date.now()}-${Math.random().toString(36).substring(2, 9)}`;
    config.headers['X-Correlation-ID'] = correlationId;
    
    // Mark request start for performance tracking
    perfMark(`req-start-${config.url}`);
    
    // Log the request in development
    if (configManager.isDevelopment()) {
      console.log(`API Request: ${config.method?.toUpperCase()} ${config.url}`, {
        headers: config.headers,
        data: config.data,
        correlationId,
      });
    }
    
    return config;
  },
  (error) => {
    console.error('API Request Error:', error);
    return Promise.reject(error);
  }
);

// Add response interceptor for logging and performance tracking
api.interceptors.response.use(
  (response) => {
    // Mark request end for performance tracking
    perfMark(`req-end-${response.config.url}`);
    
    // Calculate duration
    const startMark = `req-start-${response.config.url}`;
    const endMark = `req-end-${response.config.url}`;
    
    try {
      if (typeof performance !== 'undefined' && performance.measure) {
        performance.measure(`req-${response.config.url}`, startMark, endMark);
        const measure = performance.getEntriesByName(`req-${response.config.url}`, 'measure')[0];
        const duration = measure ? measure.duration : 0;
        
        // Log in development
        if (configManager.isDevelopment()) {
          console.log(`API Response: ${response.config.method?.toUpperCase()} ${response.config.url} - ${response.status} (${duration.toFixed(2)}ms)`, {
            data: response.data,
            correlationId: response.config.headers['X-Correlation-ID'],
          });
        }
      }
    } catch (e) {
      // Ignore performance API errors
    }
    
    return response;
  },
  (error) => {
    // Log error
    if (error.response) {
      console.error('API Response Error:', {
        status: error.response.status,
        data: error.response.data,
        correlationId: error.config?.headers?.['X-Correlation-ID'],
      });
    } else if (error.request) {
      console.error('API Request Error: No response received', {
        request: error.request,
        correlationId: error.config?.headers?.['X-Correlation-ID'],
      });
    } else {
      console.error('API Error:', error.message);
    }
    
    return Promise.reject(error);
  }
);

// API Types - Using type aliases instead of empty interfaces
export type ApiEvent = EventResponse;
export type ApiBookingRequest = BookingCreate;
export type ApiPaymentSettings = PaymentSettingsResponse;

// Analytics response interfaces
export interface ApiAnalyticsResponse {
  total_bookings: number;
  total_revenue: number;
  recent_bookings: Array<{
    booking_id: string;
    event_id: string;
    event_title: string;
    customer_name: string;
    amount: number;
    date: string;
  }>;
  event_popularity: Record<string, number>;
}

export interface ApiPaymentMetricsResponse {
  total_transactions: number;
  successful_payments: number;
  payment_success_rate: number;
  average_ticket_price: number;
  revenue_by_category: Record<string, number>;
  conversion_rate: number;
  avg_payment_time_minutes: number;
  confirmed_payments: number;
  pending_payments: number;
  expired_payments: number;
  recent_payments: Array<{
    id: string;
    booking_id: string;
    total_amount: number;
    payment_verified_at: string | null;
  }>;
}

export interface ApiUpdatePaymentSettingsRequest {
  merchant_name: string;
  vpa: string;
  description?: string;
  payment_mode?: 'vpa' | 'qr_image';
  qr_image?: File;
}

// API Response interfaces
export interface ApiBookingResponse {
  booking_id: string;
  total_amount: number;
  status: string;
  message?: string;
}

export interface ApiUTRResponse {
  booking_id: string;
  ticket_id: string;
  status: string;
  message: string;
}

// Interface for the admin login response from the backend
interface AdminLoginResponse {
  status: string;
  message: string;
  token?: string;
  admin?: {
    id: string;
    username: string;
    email: string;
  };
  timestamp: string;
  error?: string;
}

// API Functions
export async function fetchEvents(category?: string, featured?: boolean) {
  perfMark('fetchEvents-start');
  
  try {
    const params: Record<string, string | boolean> = {};
    if (category) params.category = category;
    if (featured !== undefined) params.is_featured = featured;
    
    const response = await api.get('/events', { params });
    
    perfMark('fetchEvents-end');
    return response.data;
  } catch (error) {
    console.error('Error fetching events:', error);
    throw error;
  }
}

export async function fetchEvent(eventId: string) {
  perfMark(`fetchEvent-${eventId}-start`);
  
  try {
    const response = await api.get(`/events/${eventId}`);
    
    perfMark(`fetchEvent-${eventId}-end`);
    return response.data;
  } catch (error) {
    console.error(`Error fetching event ${eventId}:`, error);
    throw error;
  }
}

export async function createBooking(bookingData: ApiBookingRequest): Promise<ApiBookingResponse> {
  perfMark('createBooking-start');
  
  try {
    const response = await api.post('/bookings', bookingData);
    
    perfMark('createBooking-end');
    return response.data;
  } catch (error) {
    console.error('Error creating booking:', error);
    throw error;
  }
}

export async function verifyPayment(data: UTRSubmission): Promise<ApiUTRResponse> {
  perfMark(`verifyPayment-${data.booking_id}-start`);
  
  try {
    const response = await api.post('/bookings/verify-payment', data);
    
    perfMark(`verifyPayment-${data.booking_id}-end`);
    return response.data;
  } catch (error) {
    console.error(`Error verifying payment for booking ${data.booking_id}:`, error);
    throw error;
  }
}

export async function fetchBooking(bookingId: string) {
  perfMark(`fetchBooking-${bookingId}-start`);
  
  try {
    const response = await api.get(`/bookings/${bookingId}`);
    
    perfMark(`fetchBooking-${bookingId}-end`);
    return response.data;
  } catch (error) {
    console.error(`Error fetching booking ${bookingId}:`, error);
    throw error;
  }
}

export async function fetchPaymentSettings(): Promise<ApiPaymentSettings> {
  perfMark('fetchPaymentSettings-start');
  
  try {
    // Use the correct endpoint path with the /api prefix if needed
    const endpoint = api.defaults.baseURL?.includes('/api') ? '/payment-settings' : '/api/payment-settings';
    console.log(`Fetching payment settings from: ${endpoint}`);
    
    const response = await api.get<ApiPaymentSettings>(endpoint);
    
    perfMark('fetchPaymentSettings-end');
    return response.data;
  } catch (error) {
    console.error('Error fetching payment settings:', error);
    // Return default settings if the API fails
    return {
      merchant_name: config().MERCHANT_NAME,
      vpa: config().VPA_ADDRESS,
      vpaAddress: config().VPA_ADDRESS,
      isPaymentEnabled: config().PAYMENT_ENABLED,
      qrImageUrl: config().QR_IMAGE_URL,
      payment_mode: 'vpa',
      description: 'Default payment settings',
      updated_at: new Date().toISOString(),
      type: 'payment_settings' // Required type field
    };
  }
}

// Admin API Functions
export async function adminLogin(token: string): Promise<Token> {
  perfMark('adminLogin-start');
  
  try {
    // Send the token in the format expected by the backend
    const response = await api.post<AdminLoginResponse>('/admin/login', { token });
    
    // The backend returns a success message but not an actual token
    // Use the provided token as the access token
    if (response.data && response.data.status === 'success') {
      // Store the admin token in localStorage
      localStorage.setItem('token', token);
      api.defaults.headers.common['Authorization'] = `Bearer ${token}`;
      
      // Return a token object that matches the expected interface
      const tokenResponse: Token = {
        access_token: token,
        message: response.data.message || 'Admin login successful',
        timestamp: response.data.timestamp
      };
      
      perfMark('adminLogin-end');
      return tokenResponse;
    } else {
      throw new Error(response.data?.error || 'Invalid admin token');
    }
  } catch (error) {
    console.error('Error logging in:', error);
    throw error;
  }
}

export async function adminLoginWithCredentials(username: string, password: string): Promise<Token> {
  perfMark('adminLoginWithCredentials-start');
  
  try {
    // Send username and password to the backend
    const response = await api.post<AdminLoginResponse>('/admin/login', { username, password });
    
    if (response.data && response.data.status === 'success') {
      // The backend should return a session token for username/password login
      const sessionToken = response.data.token || '';
      
      // Store the token in localStorage
      localStorage.setItem('token', sessionToken);
      api.defaults.headers.common['Authorization'] = `Bearer ${sessionToken}`;
      
      // Return a token object that matches the expected interface
      const tokenResponse: Token = {
        access_token: sessionToken,
        message: response.data.message || 'Admin login successful',
        timestamp: response.data.timestamp,
        admin: response.data.admin
      };
      
      perfMark('adminLoginWithCredentials-end');
      return tokenResponse;
    } else {
      throw new Error(response.data?.error || 'Invalid credentials');
    }
  } catch (error) {
    console.error('Error logging in with credentials:', error);
    throw error;
  }
}

export async function adminLogout() {
  // Remove token from localStorage
  localStorage.removeItem('token');
  delete api.defaults.headers.common['Authorization'];
  
  return { success: true };
}

export async function adminFetchEvents(page = 1, limit = 20) {
  try {
    const response = await api.get('/events', { 
      params: { skip: (page - 1) * limit, limit },
      headers: { Authorization: `Bearer ${localStorage.getItem('token')}` } 
    });
    
    return response.data;
  } catch (error) {
    if (axios.isAxiosError(error) && error.response?.status === 401) {
      // Handle unauthorized error
      adminLogout();
    }
    throw error;
  }
}

export async function adminCreateEvent(eventData: EventCreate) {
  try {
    const response = await api.post<EventResponse>('/events', eventData, {
      headers: { Authorization: `Bearer ${localStorage.getItem('token')}` }
    });
    
    return response.data;
  } catch (error) {
    if (axios.isAxiosError(error) && error.response?.status === 401) {
      adminLogout();
    }
    throw error;
  }
}

export async function adminUpdateEvent(eventId: string, eventData: EventUpdate) {
  try {
    const response = await api.put<EventResponse>(`/events/${eventId}`, eventData, {
      headers: { Authorization: `Bearer ${localStorage.getItem('token')}` }
    });
    
    return response.data;
  } catch (error) {
    if (axios.isAxiosError(error) && error.response?.status === 401) {
      adminLogout();
    }
    throw error;
  }
}

export async function adminDeleteEvent(eventId: string) {
  try {
    const response = await api.delete(`/events/${eventId}`, {
      headers: { Authorization: `Bearer ${localStorage.getItem('token')}` }
    });
    
    return response.status === 204;
  } catch (error) {
    if (axios.isAxiosError(error) && error.response?.status === 401) {
      adminLogout();
    }
    throw error;
  }
}

export async function adminFetchBookings(page = 1, limit = 20) {
  try {
    const response = await api.get('/bookings', { 
      params: { skip: (page - 1) * limit, limit },
      headers: { Authorization: `Bearer ${localStorage.getItem('token')}` } 
    });
    
    return response.data;
  } catch (error) {
    if (axios.isAxiosError(error) && error.response?.status === 401) {
      adminLogout();
    }
    throw error;
  }
}

export async function adminUpdatePaymentSettings(settings: Partial<ApiPaymentSettings>) {
  try {
    // Use the correct endpoint path with the /api prefix if needed
    const endpoint = api.defaults.baseURL?.includes('/api') ? '/payment-settings' : '/api/payment-settings';
    console.log(`Updating payment settings at: ${endpoint}`);
    
    const response = await api.put(endpoint, settings, {
      headers: { Authorization: `Bearer ${localStorage.getItem('token')}` }
    });
    
    return response.data;
  } catch (error) {
    if (axios.isAxiosError(error) && error.response?.status === 401) {
      adminLogout();
    }
    throw error;
  }
}

// Function to update config
export async function fetchAppConfig() {
  try {
    // Initialize the configuration
    await configManager.init();
    const appConfig = config();
    
    // Update API baseURL with the latest config
    api.defaults.baseURL = appConfig.API_BASE_URL;
    
    console.log('App config loaded:', appConfig);
    
    return appConfig;
  } catch (error) {
    console.error('Error fetching app config:', error);
    throw error;
  }
}

/**
 * Upload an image to the server
 * @param endpoint The API endpoint path 
 * @param formData FormData containing the file and other parameters
 * @returns API response with image URL
 */
export const uploadImage = async (endpoint: string, formData: FormData) => {
  const apiBaseUrl = import.meta.env.VITE_API_BASE_URL || '';
  
  const response = await fetch(`${apiBaseUrl}${endpoint}`, {
    method: 'POST',
    credentials: 'include',  // Include cookies for authentication
    body: formData,
    // Don't set Content-Type header - browser will set it with boundary for FormData
  });
  
  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || 'Failed to upload image');
  }
  
  return response.json();
};