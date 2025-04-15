/**
 * This file contains TypeScript interfaces that directly match the backend Pydantic models.
 * 
 * IMPORTANT: When the backend schema changes, update these interfaces to match.
 */

// ==================== Event Models ====================

export interface TeamInfo {
  name: string;
  code: string;
  color?: string;
  secondary_color?: string;
  home_ground?: string;
  logo?: string;
}

export interface TicketType {
  id: string;
  name: string;
  price: number;
  available: number;
  description?: string;
}

export interface EventBase {
  title: string;
  description: string;
  date: string; // Format: YYYY-MM-DD
  time: string; // Format: HH:MM (24-hour)
  venue: string;
  category: string;
}

export interface EventCreate extends EventBase {
  image_url?: string;
  is_featured?: boolean;
  status?: string; // "upcoming" | "ongoing" | "completed" | "cancelled"
  ticket_types: TicketType[];
  team_home?: TeamInfo;
  team_away?: TeamInfo;
}

export interface EventUpdate {
  title?: string;
  description?: string;
  date?: string; // Format: YYYY-MM-DD
  time?: string; // Format: HH:MM (24-hour)
  venue?: string;
  category?: string;
  image_url?: string;
  is_featured?: boolean;
  status?: string; // "upcoming" | "ongoing" | "completed" | "cancelled"
  ticket_types?: TicketType[];
  team_home?: TeamInfo;
  team_away?: TeamInfo;
}

export interface EventResponse extends EventBase {
  id: string;
  image_url: string;
  is_featured: boolean;
  status: string;
  ticket_types: TicketType[];
  team_home?: TeamInfo;
  team_away?: TeamInfo;
  created_at: string; // ISO format
  updated_at: string; // ISO format
}

export interface EventList {
  events: EventResponse[];
  total: number;
}

// ==================== Booking Models ====================

export interface CustomerInfo {
  name: string;
  email: string;
  phone: string;
  address?: string;
  city?: string;
  state?: string;
  pincode?: string;
}

export interface SelectedTicket {
  ticket_type_id: string;
  quantity: number;
  price_per_ticket: number;
}

export interface BookingBase {
  event_id: string;
  customer_info: CustomerInfo;
  selected_tickets: SelectedTicket[];
}

// Using type alias instead of empty interface to avoid linter warning
export type BookingCreate = BookingBase;

export interface UTRSubmission {
  booking_id: string;
  utr: string;
}

export interface BookingResponse extends BookingBase {
  booking_id: string;
  status: string; // "pending" | "payment_pending" | "confirmed" | "cancelled"
  total_amount: number;
  ticket_id?: string;
  utr?: string;
  payment_verified: boolean;
  payment_verified_at?: string; // ISO date
  created_at: string; // ISO date
  updated_at: string; // ISO date
}

export interface BookingList {
  bookings: BookingResponse[];
  total: number;
}

export interface BookingDetails extends BookingResponse {
  event_details: EventResponse;
}

export interface BookingStatusUpdate {
  status: string; // "pending" | "payment_pending" | "confirmed" | "cancelled"
}

// ==================== User Models ====================

export interface UserBase {
  email: string;
  name: string;
}

export interface UserCreate extends UserBase {
  password: string;
}

export interface UserUpdate {
  email?: string;
  name?: string;
  password?: string;
}

export interface UserResponse extends UserBase {
  id: string;
  role: string;
}

export interface Token {
  access_token: string;
  token_type?: string;
  user?: UserResponse;
  message?: string;
  timestamp?: string;
  admin?: {
    id: string;
    username: string;
    email: string;
  };
}

export interface LoginRequest {
  username: string;
  password: string;
}

// ==================== Settings Models ====================

export interface PaymentSettingsBase {
  merchant_name: string;
  vpa: string;
  description?: string;
  isPaymentEnabled: boolean;
  payment_mode: string; // "vpa" | "qr_image"
}

export interface PaymentSettingsUpdate extends PaymentSettingsBase {
  qrImageUrl?: string;
}

export interface PaymentSettingsResponse extends PaymentSettingsBase {
  type: string;
  qrImageUrl?: string;
  vpaAddress: string;
  updated_at: string; // ISO date
}

export interface AboutPageContent {
  title: string;
  content: string;
  contact_email?: string;
  contact_phone?: string;
}

export interface AboutPageResponse extends AboutPageContent {
  type: string;
  updated_at: string; // ISO date
} 