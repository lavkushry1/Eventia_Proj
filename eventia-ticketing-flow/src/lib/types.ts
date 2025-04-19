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