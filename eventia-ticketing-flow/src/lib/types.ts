/**
 * Type definitions for the Eventia application
 * These types should match the backend Pydantic schemas
 */

// Event types
export interface EventBase {
  name: string;
  description?: string;
  date: string;
  time: string;
  venue: string;
  category: string;
  teamOne?: string;
  teamTwo?: string;
  teamOneLogo?: string;
  teamTwoLogo?: string;
  price: number;
  currency: string;
  posterImage?: string;
  isFeatured: boolean;
  venue_id?: string;
  stadium_id?: string;
}

export interface EventResponse extends EventBase {
  id: string;
  status: string;
  totalTickets: number;
  availableTickets: number;
  soldOut: boolean;
  createdAt: string;
  updatedAt: string;
}

export interface EventList {
  events: EventResponse[];
  total: number;
  skip: number;
  limit: number;
}

// Team types
export interface TeamInfo {
  id: string;
  name: string;
  code: string;
  logo: string;
  description?: string;
  country?: string;
  sport?: string;
}

export interface TeamList {
  teams: TeamInfo[];
  total: number;
  skip: number;
  limit: number;
}

// Stadium types
export interface StadiumFacility {
  name: string;
  icon?: string;
  description?: string;
}

export interface SeatViewImage {
  view_id: string;
  description?: string;
  image_url: string;
}

export interface StadiumSection {
  section_id: string;
  name: string;
  description?: string;
  capacity: number;
  price: number;
  availability: number;
  color_code?: string;
  is_vip?: boolean;
  image_url?: string;
  views?: SeatViewImage[];
}

export interface Stadium {
  id: string;
  name: string;
  city: string;
  country: string;
  description?: string;
  image_url?: string;
  capacity: number;
  is_active: boolean;
  address?: string;
  location?: { lat: number; lng: number };
  facilities?: StadiumFacility[];
  sections?: StadiumSection[];
}

export interface StadiumList {
  stadiums: Stadium[];
  total: number;
  skip: number;
  limit: number;
}

export interface SeatViewImageList {
  views: SeatViewImage[];
  total: number;
}

// Booking types
export interface CustomerInfo {
  name: string;
  email: string;
  phone: string;
}

export interface SelectedTicket {
  section_id: string;
  section_name: string;
  price: number;
  quantity: number;
}

export interface BookingRequest {
  event_id: string;
  customer_info: CustomerInfo;
  selected_tickets: SelectedTicket[];
}

export interface BookingResponse {
  booking_id: string;
  event_id: string;
  event_name?: string;
  event_date?: string;
  event_time?: string;
  event_venue?: string;
  customer_info: CustomerInfo;
  selected_tickets: SelectedTicket[];
  total_amount: number;
  payment_status: string;
  booking_status: string;
  created_at: string;
  updated_at: string;
  qr_code?: string;
  utr?: string;
}

export interface BookingList {
  bookings: BookingResponse[];
  total: number;
  skip: number;
  limit: number;
}

// Payment types
export interface PaymentRequest {
  booking_id: string;
  utr: string;
}

export interface PaymentResponse {
  payment_id: string;
  booking_id: string;
  amount: number;
  status: string;
  utr: string;
  verified: boolean;
  verification_time?: string;
  created_at: string;
  updated_at: string;
}

export interface PaymentSettingsResponse {
  id: string;
  merchant_name: string;
  vpa: string;
  vpaAddress: string;
  qr_image: string;
  isPaymentEnabled: boolean;
  payment_mode: string;
  type: string;
}

// Admin types
export interface AdminLoginRequest {
  username: string;
  password: string;
}

export interface AdminLoginResponse {
  token: string;
  user: {
    id: string;
    username: string;
    role: string;
  };
}

export interface DashboardStats {
  total_events: number;
  total_bookings: number;
  total_revenue: number;
  active_events: number;
  pending_payments: number;
  recent_bookings: BookingResponse[];
}

// Error response type
export interface ErrorResponse {
  detail: string;
  code?: string;
  path?: string;
}

/**
 * Event and API response types
 */

// Core API response types
export interface ApiResponse<T> {
  success: boolean;
  message: string;
  data: T;
}

export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  size: number;
  pages: number;
}

// Backend API event types
export interface ApiEvent {
  id: string;
  name: string;
  description: string;
  category: string;
  venue_id: string;
  start_datetime: string;
  end_datetime: string;
  ticket_types: ApiTicketType[];
  image?: string;
  team_ids?: string[];
  status: string;
  totalTickets: number;
  availableTickets: number;
  soldOut: boolean;
  createdAt: string;
  updatedAt: string;
}

export interface ApiTicketType {
  id: string;
  name: string;
  price: number;
  quantity: number;
  remaining?: number;
}

export interface ApiTeam {
  id: string;
  name: string;
  logo?: string;
  description?: string;
}

export interface ApiVenue {
  id: string;
  name: string;
  address: string;
  city: string;
  state: string;
  country: string;
  postalCode: string;
  capacity: number;
  image?: string;
}

// Frontend UI Models
export interface UIEvent {
  id: string;
  title: string;
  description: string;
  category: string;
  venue: string;
  venueId: string;
  date: string;
  time: string;
  duration: string;
  ticketTypes: UITicketType[];
  image: string;
  featured: boolean;
  teams?: string[];
  status?: string;
  isSoldOut?: boolean;
}

export interface UITicketType {
  id: string;
  name: string;
  price: number;
  available: number;
}

// Booking related types
export interface ApiBookingResponse {
  id: string;
  event_id: string;
  user_id: string;
  tickets: ApiBookingTicket[];
  total_amount: number;
  status: string;
  created_at: string;
  updated_at: string;
}

export interface ApiBookingTicket {
  ticket_type_id: string;
  quantity: number;
  price: number;
}

export interface BookingRequest {
  eventId: string;
  tickets: {
    ticketTypeId: string;
    quantity: number;
  }[];
}

export interface UIBooking {
  id: string;
  eventId: string;
  tickets: UIBookingTicket[];
  totalAmount: number;
  status: string;
  createdAt: string;
}

export interface UIBookingTicket {
  ticketTypeId: string;
  ticketTypeName?: string;
  quantity: number;
  price: number;
}

// Legacy interfaces for backward compatibility
export interface LegacyApiEvent {
  id: string;
  title: string; 
  description: string;
  category: string;
  venue: string;
  venue_id?: string;
  start_date: string;
  end_date: string;
  start_time: string;
  end_time: string;
  ticket_types: ApiTicketType[];
  image: string;
  featured: boolean;
  teams: string[];
}

export interface LegacyApiBookingResponse {
  booking_id: string;
  event_id: string;
  user_id: string;
  tickets: {
    type_id: string;
    quantity: number;
    price: number;
  }[];
  total_amount: number;
  status: string;
  created_at: string;
}

// Event response from API
export interface EventResponse {
  id: string;
  name: string;
  description: string;
  category: string;
  venue_id: string;
  start_datetime: string;
  end_datetime: string;
  ticket_types: ApiTicketType[];
  image?: string;
  team_ids?: string[];
  status: string;
  totalTickets: number;
  availableTickets: number;
  soldOut: boolean;
  createdAt: string;
  updatedAt: string;
}

// Used for the events list
export interface EventList {
  events: EventResponse[];
}