/**
 * This file defines Zod schemas that match the backend Pydantic validation rules.
 * Use these schemas to validate form inputs before submitting to the API.
 */
import { z } from 'zod';

// ==================== Event Validations ====================

export const teamInfoSchema = z.object({
  name: z.string().min(1, "Team name is required"),
  code: z.string().min(1, "Team code is required"),
  color: z.string().optional(),
  secondary_color: z.string().optional(),
  home_ground: z.string().optional(),
  logo: z.string().optional()
});

export const ticketTypeSchema = z.object({
  id: z.string().optional(), // Auto-generated on the backend
  name: z.string().min(1, "Ticket name is required"),
  price: z.number().min(0, "Price must be positive"),
  available: z.number().int().min(0, "Available tickets must be a positive number"),
  description: z.string().optional()
});

// Date format validation (YYYY-MM-DD)
const dateRegex = /^\d{4}-\d{2}-\d{2}$/;
// Time format validation (HH:MM)
const timeRegex = /^([01]\d|2[0-3]):([0-5]\d)$/;

export const eventBaseSchema = z.object({
  title: z.string().min(3, "Title must be at least 3 characters"),
  description: z.string().min(10, "Description must be at least 10 characters"),
  date: z.string().regex(dateRegex, "Date must be in YYYY-MM-DD format"),
  time: z.string().regex(timeRegex, "Time must be in HH:MM format (24-hour)"),
  venue: z.string().min(3, "Venue must be at least 3 characters"),
  category: z.string().min(1, "Category is required")
});

export const eventCreateSchema = eventBaseSchema.extend({
  image_url: z.string().optional().default("/placeholder.jpg"),
  is_featured: z.boolean().optional().default(false),
  status: z.string().optional().default("upcoming"),
  ticket_types: z.array(ticketTypeSchema).min(1, "At least one ticket type is required"),
  team_home: teamInfoSchema.optional(),
  team_away: teamInfoSchema.optional()
});

export const eventUpdateSchema = z.object({
  title: z.string().min(3, "Title must be at least 3 characters").optional(),
  description: z.string().min(10, "Description must be at least 10 characters").optional(),
  date: z.string().regex(dateRegex, "Date must be in YYYY-MM-DD format").optional(),
  time: z.string().regex(timeRegex, "Time must be in HH:MM format (24-hour)").optional(),
  venue: z.string().min(3, "Venue must be at least 3 characters").optional(),
  category: z.string().min(1, "Category is required").optional(),
  image_url: z.string().optional(),
  is_featured: z.boolean().optional(),
  status: z.string().optional(),
  ticket_types: z.array(ticketTypeSchema).min(1, "At least one ticket type is required").optional(),
  team_home: teamInfoSchema.optional(),
  team_away: teamInfoSchema.optional()
});

// ==================== Booking Validations ====================

export const customerInfoSchema = z.object({
  name: z.string().min(2, "Name must be at least 2 characters"),
  email: z.string().email("Invalid email address"),
  phone: z.string().min(10, "Phone number must be at least 10 digits"),
  address: z.string().optional(),
  city: z.string().optional(),
  state: z.string().optional(),
  pincode: z.string().optional()
});

export const selectedTicketSchema = z.object({
  ticket_type_id: z.string().min(1, "Ticket type ID is required"),
  quantity: z.number().int().min(1, "Quantity must be at least 1"),
  price_per_ticket: z.number().min(0, "Price must be positive")
});

export const bookingCreateSchema = z.object({
  event_id: z.string().min(1, "Event ID is required"),
  customer_info: customerInfoSchema,
  selected_tickets: z.array(selectedTicketSchema).min(1, "At least one ticket is required")
});

export const utrSubmissionSchema = z.object({
  booking_id: z.string().min(1, "Booking ID is required"),
  utr: z.string().min(8, "UTR number must be at least 8 characters")
});

export const bookingStatusUpdateSchema = z.object({
  status: z.enum(["pending", "payment_pending", "confirmed", "cancelled"], {
    errorMap: () => ({ message: "Status must be one of: pending, payment_pending, confirmed, cancelled" })
  })
});

// ==================== User Validations ====================

export const userCreateSchema = z.object({
  email: z.string().email("Invalid email address"),
  name: z.string().min(2, "Name must be at least 2 characters"),
  password: z.string().min(8, "Password must be at least 8 characters long")
});

export const userUpdateSchema = z.object({
  email: z.string().email("Invalid email address").optional(),
  name: z.string().min(2, "Name must be at least 2 characters").optional(),
  password: z.string().min(8, "Password must be at least 8 characters long").optional()
});

export const loginRequestSchema = z.object({
  username: z.string().email("Invalid email address"),
  password: z.string().min(1, "Password is required")
});

// ==================== Settings Validations ====================

export const paymentSettingsUpdateSchema = z.object({
  merchant_name: z.string().min(1, "Merchant name is required"),
  vpa: z.string().min(1, "VPA address is required"),
  description: z.string().optional(),
  isPaymentEnabled: z.boolean().optional().default(true),
  payment_mode: z.enum(["vpa", "qr_image"], {
    errorMap: () => ({ message: "Payment mode must be one of: vpa, qr_image" })
  }),
  qrImageUrl: z.string().optional()
});

export const aboutPageContentSchema = z.object({
  title: z.string().min(1, "Title is required"),
  content: z.string().min(10, "Content must be at least 10 characters"),
  contact_email: z.string().email("Invalid email address").optional(),
  contact_phone: z.string().optional()
}); 