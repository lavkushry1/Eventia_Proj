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

export interface EventTeam {
  home: TeamInfo;
  away: TeamInfo;
}


export interface TicketType {
  id: string;
  name: string;
  price: number;
  available: number;  
  description?: string;
}

export interface Event {
  name: string; // This was called name on the backend  
  date: string; // Format: YYYY-MM-DD
  time: string; // Format: HH:MM (24-hour)
  venue: string;
  category: string;
  price: number;
  availability: number;
  image_url?: string;
  is_featured?: boolean;  
  status?: string; // "upcoming" | "ongoing" | "completed" | "cancelled"
  ticket_types?: TicketType[];  
  teams?: EventTeam
  created_at?: string; // ISO format
  updated_at?: string; // ISO format
}

export interface EventResponse extends Event {
  id: string;
  
}

export interface EventList {
  events: EventResponse[];
  total: number;
}

// ==================== Booking Models ====================

export interface CustomerInfo {\n  name: string;\n  email: string;\n  phone: string;\n}\n\nexport interface SelectedTicket {\n  ticket_type_id: string;\n  quantity: number;\n  price_per_ticket: number;\n}\n\nexport interface BookingBase {\n  event_id: string;\n  customer_info: CustomerInfo;\n  selected_tickets: SelectedTicket[];\n}\n\n// Using type alias instead of empty interface to avoid linter warning\nexport type BookingCreate = BookingBase;\n\nexport interface UTRSubmission {\n  booking_id: string;\n  utr: string;\n}\n\nexport interface BookingResponse extends BookingBase {\n  booking_id: string;\n  status: string; // \"pending\" | \"payment_pending\" | \"confirmed\" | \"cancelled\"\n  total_amount: number;\n  ticket_id?: string;\n  utr?: string;\n  payment_verified: boolean;\n  payment_verified_at?: string; // ISO date\n  created_at: string; // ISO date\n  updated_at: string; // ISO date\n}\n\nexport interface BookingList {\n  bookings: BookingResponse[];\n  total: number;\n}\n\nexport interface BookingDetails extends BookingResponse {\n  event_details: EventResponse;\n}\n\nexport interface BookingStatusUpdate {\n  status: string; // \"pending\" | \"payment_pending\" | \"confirmed\" | \"cancelled\"\n}\n\n// ==================== User Models ====================\n\nexport interface UserBase {\n  email: string;\n  name: string;\n}\n\nexport interface UserCreate extends UserBase {\n  password: string;\n}\n\nexport interface UserUpdate {\n  email?: string;\n  name?: string;\n  password?: string;\n}\n\nexport interface UserResponse extends UserBase {\n  id: string;\n  role: string;\n  created_at?: string;\n  updated_at?: string;\n}\n\n// token interface updated to match the backend schema\nexport interface Token {\n  access_token: string;\n  token_type?: string;\n  normalUser?: {\n    id: string;\n    role: string;\n    email: string;\n    created_at?: string;\n    updated_at?: string;\n\n  };\n  message?: string;\n  timestamp?: string;\n  admin?: {\n    id: string;\n    is_active: boolean;\n    created_at?: string;\n    updated_at?: string;\n    email: string;\n  };\n}\n\nexport interface LoginRequest {\n  username: string;\n  password: string;\n}\n\n// ==================== Stadium Models ====================\n\nexport interface StadiumSection {\n  section_id: string;\n  name: string;\n  capacity: number;\n  price: number;\n  description?: string;\n  availability: number;\n  color_code?: string;\n  is_vip: boolean;\n}\n\nexport interface StadiumFacility {\n  name: string;\n  icon?: string;\n  description?: string;\n}\n\nexport interface Stadium {\n  stadium_id: string;\n  name: string;\n  city: string;\n  country: string;\n  capacity: number;\n  sections: StadiumSection[];\n  facilities?: StadiumFacility[];\n  description?: string;\n  image_url?: string;\n  ar_model_url?: string;\n  is_active: boolean;\n  created_at?: string;\n  updated_at?: string;\n}\n\nexport interface StadiumList {\n  stadiums: Stadium[];\n  total: number;\n}\n\nexport interface SeatViewImage {\n  view_id: string;\n  stadium_id: string;\n  section_id: string;\n  image_url: string;\n  description: string;\n  created_at?: string;\n  updated_at?: string;\n}\n\nexport interface SeatViewImageList {\n  views: SeatViewImage[];\n  total: number;\n}\n\n// ==================== Settings Models ====================\n\nexport interface PaymentSettingsBase {\n  merchant_name: string;\n  vpa: string;\n  description?: string;\n  isPaymentEnabled: boolean;\n  payment_mode: string; // \"vpa\" | \"qr_image\"\n}\n\nexport interface PaymentSettingsUpdate extends PaymentSettingsBase {\n  qrImageUrl?: string;\n}\n\nexport interface PaymentSettingsResponse extends PaymentSettingsBase {\n  type: string;\n  qrImageUrl?: string;\n  vpaAddress: string;\n  updated_at: string; // ISO date\n}\n\nexport interface AboutPageContent {\n  title: string;\n  content: string;\n  contact_email?: string;\n  contact_phone?: string;\n}\n\nexport interface AboutPageResponse extends AboutPageContent {\n  type: string;\n  updated_at: string; // ISO date\n}\n\nexport interface SeatViewImageCreate {\n  section_id: string;\n  description: string;\n}\n  name: string;\n  email: string;\n  phone: string;\n-  address?: string;\n-  city?: string;\n-  state?: string;\n-  pincode?: string;\n}\n
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
  message?: string;
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
  created_at?: string;
  updated_at?: string;
}

// token interface updated to match the backend schema
export interface Token {
  access_token: string;
  token_type?: string;
  normalUser?: {
    id: string;
    role: string;
    created_at?: string;
    updated_at?: string;

  };
  message?: string;
  timestamp?: string;
  admin?: {
    id: string;
    username?: string;
    hashed_password: string;
    email: string;
    is_active: boolean;
    created_at?: string;
    updated_at?: string;
  };
}

export interface LoginRequest {
  username: string;
  password: string;
}

// ==================== Stadium Models ====================

export interface StadiumSection {
  section_id: string;
  name: string;
  capacity: number;
  price: number;
  description?: string;
  availability: number;
  color_code?: string;
  is_vip: boolean;
}

export interface StadiumFacility {
  name: string;
  icon?: string;
  description?: string;
}

export interface Stadium {
  stadium_id: string;
  name: string;
  city: string;
  country: string;
  capacity: number;
  sections: StadiumSection[];
  facilities?: StadiumFacility[];
  description?: string;
  image_url?: string;
  ar_model_url?: string;
  is_active: boolean;
  created_at?: string;
  updated_at?: string;
}

export interface StadiumList {
  stadiums: Stadium[];
  total: number;
}

export interface SeatViewImage {
  view_id: string;
  stadium_id: string;
  section_id: string;
  image_url: string;
  description: string;
  created_at?: string;
  updated_at?: string;
}

export interface SeatViewImageList {
  views: SeatViewImage[];
  total: number;
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

export interface SeatViewImageCreate {
  section_id: string;
  description: string;
}