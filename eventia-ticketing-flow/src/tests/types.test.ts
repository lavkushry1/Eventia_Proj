import { describe, it, expect } from 'vitest';
import {
  Event,
  EventResponse,
  TeamInfo,
  BookingResponse,
  PaymentSettingsResponse,
  UserResponse
} from '../lib/types';

// Mock data for testing
const mockEvent: EventResponse = {
  id: 'event-123',
  name: 'IPL Finals',
  date: '2025-05-30',
  time: '19:00',
  venue: 'Narendra Modi Stadium',
  category: 'cricket',
  price: 1200,
  availability: 5000,
  image_url: '/static/events/ipl-finals.png',
  is_featured: true,
  status: 'upcoming',
  created_at: '2025-04-01T12:00:00Z',
  updated_at: '2025-04-10T15:30:00Z',
  teams: {
    home: {
      name: 'Mumbai Indians',
      code: 'MI',
      logo: '/static/teams/mi.png',
      color: '#004BA0',
      secondary_color: '#D1AB3E',
    },
    away: {
      name: 'Chennai Super Kings',
      code: 'CSK',
      logo: '/static/teams/csk.png',
      color: '#FFFF3C',
      secondary_color: '#0081E9',
    }
  }
};

const mockBooking: BookingResponse = {
  booking_id: 'BKG-12345',
  event_id: 'event-123',
  customer_info: {
    name: 'Rahul Sharma',
    email: 'rahul@example.com',
    phone: '9876543210'
  },
  selected_tickets: [
    {
      ticket_type_id: 'premium',
      quantity: 2,
      price_per_ticket: 1500
    }
  ],
  status: 'confirmed',
  total_amount: 3000,
  payment_verified: true,
  created_at: '2025-04-20T10:15:00Z',
  updated_at: '2025-04-20T10:20:00Z'
};

const mockPaymentSettings: PaymentSettingsResponse = {
  merchant_name: 'Eventia Payments',
  vpa: 'eventia@upi',
  vpaAddress: 'eventia@upi',
  isPaymentEnabled: true,
  payment_mode: 'vpa',
  description: 'UPI payments are enabled',
  type: 'payment_settings',
  updated_at: '2025-04-15T12:00:00Z'
};

describe('Type validation tests', () => {
  describe('Event type validation', () => {
    it('should have all required fields for Event', () => {
      // Check essential fields
      expect(mockEvent).toHaveProperty('id');
      expect(mockEvent).toHaveProperty('name');
      expect(mockEvent).toHaveProperty('date');
      expect(mockEvent).toHaveProperty('time');
      expect(mockEvent).toHaveProperty('venue');
      expect(mockEvent).toHaveProperty('price');
      expect(mockEvent).toHaveProperty('availability');
    });

    it('should handle teams data correctly', () => {
      expect(mockEvent.teams).toBeDefined();
      expect(mockEvent.teams?.home).toHaveProperty('name');
      expect(mockEvent.teams?.home).toHaveProperty('code');
      expect(mockEvent.teams?.away).toHaveProperty('name');
      expect(mockEvent.teams?.away).toHaveProperty('code');
    });

    it('should handle image URLs correctly', () => {
      expect(mockEvent.image_url).toMatch(/^(\/static\/events\/|http)/);
      expect(mockEvent.teams?.home.logo).toMatch(/^(\/static\/teams\/|http)/);
      expect(mockEvent.teams?.away.logo).toMatch(/^(\/static\/teams\/|http)/);
    });
  });

  describe('Booking type validation', () => {
    it('should have all required fields for Booking', () => {
      expect(mockBooking).toHaveProperty('booking_id');
      expect(mockBooking).toHaveProperty('event_id');
      expect(mockBooking).toHaveProperty('customer_info');
      expect(mockBooking).toHaveProperty('selected_tickets');
      expect(mockBooking).toHaveProperty('status');
      expect(mockBooking).toHaveProperty('total_amount');
    });

    it('should have valid customer info', () => {
      expect(mockBooking.customer_info).toHaveProperty('name');
      expect(mockBooking.customer_info).toHaveProperty('email');
      expect(mockBooking.customer_info).toHaveProperty('phone');
    });

    it('should have valid selected tickets', () => {
      expect(mockBooking.selected_tickets.length).toBeGreaterThan(0);
      expect(mockBooking.selected_tickets[0]).toHaveProperty('ticket_type_id');
      expect(mockBooking.selected_tickets[0]).toHaveProperty('quantity');
      expect(mockBooking.selected_tickets[0]).toHaveProperty('price_per_ticket');
    });
  });

  describe('Payment Settings type validation', () => {
    it('should have all required fields for PaymentSettings', () => {
      expect(mockPaymentSettings).toHaveProperty('merchant_name');
      expect(mockPaymentSettings).toHaveProperty('vpa');
      expect(mockPaymentSettings).toHaveProperty('vpaAddress');
      expect(mockPaymentSettings).toHaveProperty('isPaymentEnabled');
      expect(mockPaymentSettings).toHaveProperty('payment_mode');
      expect(mockPaymentSettings).toHaveProperty('type');
    });

    it('should have consistent VPA fields', () => {
      // vpaAddress should match vpa for consistent frontend rendering
      expect(mockPaymentSettings.vpaAddress).toBe(mockPaymentSettings.vpa);
    });
  });

  describe('TypeScript Interfaces', () => {
    it('should validate Event interface', () => {
      const event: Event = {
        title: 'Test Event',
        price: 100,
        description: 'This is a test event',
        date: '2024-12-31',
        time: '20:00',
        venue: 'Test Venue',
        category: 'Test Category',
        image_url: '/test.jpg',
        is_featured: true,
        status: 'upcoming',
        ticket_types: [
          {
            id: 'tkt-1',
            name: 'VIP',
            price: 500,
            available: 100,
            description: 'VIP access',
          },
        ],
        teams: {
          home: {
            name: 'Home Team',
            code: 'HT',
            color: '#FF0000',
            secondary_color: '#FFFFFF',
            home_ground: 'Home ground',
            logo: '/home.png',
          },
          away: {
            name: 'Away Team',
            code: 'AT',
            color: '#0000FF',
            secondary_color: '#FFFFFF',
            home_ground: 'Away ground',
            logo: '/away.png',
          },
        },
        created_at: '2024-01-01T00:00:00Z',
        updated_at: '2024-01-01T00:00:00Z',
      };

      expect(event.title).toBeDefined();
      expect(event.price).toBeDefined();
      expect(event.description).toBeDefined();
      expect(event.date).toBeDefined();
      expect(event.time).toBeDefined();
      expect(event.venue).toBeDefined();
      expect(event.category).toBeDefined();
      expect(event.image_url).toBeDefined();
      expect(event.is_featured).toBeDefined();
      expect(event.status).toBeDefined();
      expect(event.ticket_types).toBeDefined();
      expect(event.teams).toBeDefined();
      expect(event.created_at).toBeDefined();
      expect(event.updated_at).toBeDefined();
    });

    it('should validate TeamInfo interface', () => {
      const teamInfo: TeamInfo = {
        name: 'Test Team',
        code: 'TT',
        color: '#000000',
        secondary_color: '#FFFFFF',
        home_ground: 'Test Ground',
        logo: '/test.png',
      };

      expect(teamInfo.name).toBeDefined();
      expect(teamInfo.code).toBeDefined();
      expect(teamInfo.color).toBeDefined();
      expect(teamInfo.secondary_color).toBeDefined();
      expect(teamInfo.home_ground).toBeDefined();
      expect(teamInfo.logo).toBeDefined();
    });

    it('should validate BookingResponse interface', () => {
      const bookingResponse: BookingResponse = {
        booking_id: 'BKG-123',
        event_id: 'EVT-456',
        customer_info: {
          name: 'John Doe',
          email: 'john.doe@example.com',
          phone: '+15551234567',
        },
        selected_tickets: [
          {
            ticket_type_id: 'tkt-1',
            quantity: 2,
            price_per_ticket: 500,
          },
        ],
        status: 'confirmed',
        total_amount: 1000,
        ticket_id: 'TKT-789',
        utr: 'UTR123456',
        payment_verified: true,
        payment_verified_at: '2024-01-01T12:00:00Z',
        created_at: '2024-01-01T10:00:00Z',
        updated_at: '2024-01-01T12:00:00Z',
        message: "Payment successfull"
      };

      expect(bookingResponse.booking_id).toBeDefined();
      expect(bookingResponse.event_id).toBeDefined();
      expect(bookingResponse.customer_info).toBeDefined();
      expect(bookingResponse.selected_tickets).toBeDefined();
      expect(bookingResponse.status).toBeDefined();
      expect(bookingResponse.total_amount).toBeDefined();
      expect(bookingResponse.ticket_id).toBeDefined();
      expect(bookingResponse.utr).toBeDefined();
      expect(bookingResponse.payment_verified).toBeDefined();
      expect(bookingResponse.payment_verified_at).toBeDefined();
      expect(bookingResponse.created_at).toBeDefined();
      expect(bookingResponse.updated_at).toBeDefined();
      expect(bookingResponse.message).toBeDefined();
    });

    it('should validate UserResponse interface', () => {
      const userResponse: UserResponse = {
        id: 'USR-123',
        email: 'john.doe@example.com',
        name: 'John Doe',
        role: 'user',
        created_at: '2024-01-01T00:00:00Z',
        updated_at: '2024-01-01T00:00:00Z',
      };

      expect(userResponse.id).toBeDefined();
      expect(userResponse.email).toBeDefined();
      expect(userResponse.name).toBeDefined();
      expect(userResponse.role).toBeDefined();
      expect(userResponse.created_at).toBeDefined();
      expect(userResponse.updated_at).toBeDefined();
    });
  });
});