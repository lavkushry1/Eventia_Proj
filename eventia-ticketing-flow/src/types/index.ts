// Common types
export interface ApiResponse<T> {
  data: T;
  message?: string;
  error?: string;
}

export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  limit: number;
  total_pages: number;
}

// Event types
export interface Event {
  id: string;
  name: string;
  description: string;
  category: string;
  start_date: string;
  end_date: string;
  venue_id: string;
  team_ids: string[];
  poster_url?: string;
  featured: boolean;
  status: 'upcoming' | 'ongoing' | 'completed' | 'cancelled';
  created_at: string;
  updated_at: string;
}

// Team types
export interface Team {
  id: string;
  name: string;
  code: string;
  logo_url?: string;
  created_at: string;
  updated_at: string;
}

// Stadium types
export interface Stadium {
  id: string;
  name: string;
  location: string;
  capacity: number;
  image_url?: string;
  sections: StadiumSection[];
  created_at: string;
  updated_at: string;
}

export interface StadiumSection {
  id: string;
  name: string;
  capacity: number;
  price: number;
  view_image_url?: string;
  created_at: string;
  updated_at: string;
}

// Booking types
export interface Booking {
  id: string;
  event_id: string;
  user_id: string;
  section_id: string;
  quantity: number;
  total_amount: number;
  status: 'pending' | 'confirmed' | 'cancelled';
  payment_id?: string;
  created_at: string;
  updated_at: string;
}

// Payment types
export interface Payment {
  id: string;
  booking_id: string;
  amount: number;
  status: 'pending' | 'completed' | 'failed';
  payment_method: 'upi' | 'card' | 'netbanking';
  utr?: string;
  qr_url?: string;
  created_at: string;
  updated_at: string;
}

// Admin types
export interface AdminUser {
  id: string;
  username: string;
  role: 'admin' | 'superadmin';
  created_at: string;
  updated_at: string;
}

export interface AdminAuthResponse {
  token: string;
  user: AdminUser;
}

// Settings types
export interface PaymentSettings {
  vpa: string;
  qr_enabled: boolean;
  upi_enabled: boolean;
  card_enabled: boolean;
  netbanking_enabled: boolean;
} 