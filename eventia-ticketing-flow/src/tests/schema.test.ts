import { describe, it, expect } from 'vitest';
import type {
  Event,
  EventResponse,
  UserBase,
  UserResponse,
  BookingResponse,
  Stadium,
  StadiumSection,
  StadiumFacility,
} from '../lib/types';

describe('Schema Validation', () => {
  describe('Event Schema', () => {
    it('should match backend EventBase schema', () => {
      const event: Event = {
        name: 'Test Event',
        date: '2024-04-19',
        time: '19:00',
        venue: 'Test Venue',
        category: 'Sports',
        price: 100.50,
        availability: 1000,
        image_url: null,
        is_featured: false,
        status: 'upcoming',
        ticket_types: null,
        teams: null,
      };

      expect(event).toBeDefined();
      expect(typeof event.price).toBe('number');
      expect(typeof event.availability).toBe('number');
      expect(event.image_url).toBeNull();
      expect(event.ticket_types).toBeNull();
      expect(event.teams).toBeNull();
    });
  });

  describe('User Schema', () => {
    it('should match backend UserBase schema', () => {
      const user: UserBase = {
        email: 'test@example.com',
        full_name: 'Test User',
      };

      expect(user).toBeDefined();
      expect(user.full_name).toBeDefined();
      expect(user.email).toBeDefined();
    });

    it('should match backend UserResponse schema', () => {
      const user: UserResponse = {
        id: '123',
        email: 'test@example.com',
        full_name: 'Test User',
        is_active: true,
        is_admin: false,
        created_at: '2024-04-19T00:00:00Z',
        updated_at: '2024-04-19T00:00:00Z',
      };

      expect(user).toBeDefined();
      expect(user.is_active).toBeDefined();
      expect(user.is_admin).toBeDefined();
    });
  });

  describe('Booking Schema', () => {
    it('should match backend BookingResponse schema', () => {
      const booking: BookingResponse = {
        booking_id: '123',
        event_id: '456',
        customer_info: {
          name: 'Test User',
          email: 'test@example.com',
          phone: '1234567890',
          address: null,
          city: null,
          state: null,
          pincode: null,
        },
        selected_tickets: [],
        status: 'pending',
        total_amount: 100.50,
        ticket_id: null,
        utr: null,
        payment_verified: false,
        payment_verified_at: null,
        created_at: '2024-04-19T00:00:00Z',
        updated_at: '2024-04-19T00:00:00Z',
        message: null,
      };

      expect(booking).toBeDefined();
      expect(booking.customer_info.address).toBeNull();
      expect(booking.ticket_id).toBeNull();
      expect(booking.utr).toBeNull();
      expect(booking.message).toBeNull();
    });
  });

  describe('Stadium Schema', () => {
    it('should match backend Stadium schema', () => {
      const stadium: Stadium = {
        stadium_id: '123',
        name: 'Test Stadium',
        city: 'Test City',
        country: 'Test Country',
        capacity: 10000,
        sections: [],
        facilities: null,
        description: null,
        image_url: null,
        ar_model_url: null,
        is_active: true,
        created_at: null,
        updated_at: null,
      };

      expect(stadium).toBeDefined();
      expect(stadium.facilities).toBeNull();
      expect(stadium.description).toBeNull();
      expect(stadium.image_url).toBeNull();
    });

    it('should match backend StadiumSection schema', () => {
      const section: StadiumSection = {
        section_id: '123',
        name: 'Test Section',
        capacity: 100,
        price: 50.00,
        description: null,
        availability: 100,
        color_code: null,
        is_vip: false,
      };

      expect(section).toBeDefined();
      expect(section.description).toBeNull();
      expect(section.color_code).toBeNull();
    });

    it('should match backend StadiumFacility schema', () => {
      const facility: StadiumFacility = {
        name: 'Test Facility',
        icon: null,
        description: null,
      };

      expect(facility).toBeDefined();
      expect(facility.icon).toBeNull();
      expect(facility.description).toBeNull();
    });
  });
}); 