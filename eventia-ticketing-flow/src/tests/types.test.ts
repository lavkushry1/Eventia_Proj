import { describe, it, expect } from 'vitest';
import { Event, TeamInfo, BookingResponse, UserResponse } from '../lib/types';

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