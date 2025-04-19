import {
  ApiResponse,
  PaginatedResponse,
  Event,
  Team,
  Stadium,
  StadiumSection,
  Booking,
  Payment,
  AdminUser,
  AdminAuthResponse,
  PaymentSettings
} from '../index';

describe('Type Definitions', () => {
  test('ApiResponse type', () => {
    const response: ApiResponse<string> = {
      data: 'test',
      message: 'success',
      error: undefined
    };
    expect(response).toBeDefined();
  });

  test('PaginatedResponse type', () => {
    const response: PaginatedResponse<Event> = {
      items: [],
      total: 0,
      page: 1,
      limit: 20,
      total_pages: 0
    };
    expect(response).toBeDefined();
  });

  test('Event type', () => {
    const event: Event = {
      id: '1',
      name: 'Test Event',
      description: 'Test Description',
      category: 'Sports',
      start_date: '2024-01-01',
      end_date: '2024-01-02',
      venue_id: '1',
      team_ids: ['1', '2'],
      poster_url: 'test.jpg',
      featured: true,
      status: 'upcoming',
      created_at: '2024-01-01T00:00:00Z',
      updated_at: '2024-01-01T00:00:00Z'
    };
    expect(event).toBeDefined();
  });

  test('Team type', () => {
    const team: Team = {
      id: '1',
      name: 'Test Team',
      code: 'TT',
      logo_url: 'test.jpg',
      created_at: '2024-01-01T00:00:00Z',
      updated_at: '2024-01-01T00:00:00Z'
    };
    expect(team).toBeDefined();
  });

  test('Stadium type', () => {
    const stadium: Stadium = {
      id: '1',
      name: 'Test Stadium',
      location: 'Test Location',
      capacity: 10000,
      image_url: 'test.jpg',
      sections: [],
      created_at: '2024-01-01T00:00:00Z',
      updated_at: '2024-01-01T00:00:00Z'
    };
    expect(stadium).toBeDefined();
  });

  test('StadiumSection type', () => {
    const section: StadiumSection = {
      id: '1',
      name: 'Test Section',
      capacity: 1000,
      price: 100,
      view_image_url: 'test.jpg',
      created_at: '2024-01-01T00:00:00Z',
      updated_at: '2024-01-01T00:00:00Z'
    };
    expect(section).toBeDefined();
  });

  test('Booking type', () => {
    const booking: Booking = {
      id: '1',
      event_id: '1',
      user_id: '1',
      section_id: '1',
      quantity: 2,
      total_amount: 200,
      status: 'pending',
      payment_id: '1',
      created_at: '2024-01-01T00:00:00Z',
      updated_at: '2024-01-01T00:00:00Z'
    };
    expect(booking).toBeDefined();
  });

  test('Payment type', () => {
    const payment: Payment = {
      id: '1',
      booking_id: '1',
      amount: 200,
      status: 'pending',
      payment_method: 'upi',
      utr: '1234567890',
      qr_url: 'test.jpg',
      created_at: '2024-01-01T00:00:00Z',
      updated_at: '2024-01-01T00:00:00Z'
    };
    expect(payment).toBeDefined();
  });

  test('AdminUser type', () => {
    const admin: AdminUser = {
      id: '1',
      username: 'admin',
      role: 'admin',
      created_at: '2024-01-01T00:00:00Z',
      updated_at: '2024-01-01T00:00:00Z'
    };
    expect(admin).toBeDefined();
  });

  test('AdminAuthResponse type', () => {
    const auth: AdminAuthResponse = {
      token: 'test-token',
      user: {
        id: '1',
        username: 'admin',
        role: 'admin',
        created_at: '2024-01-01T00:00:00Z',
        updated_at: '2024-01-01T00:00:00Z'
      }
    };
    expect(auth).toBeDefined();
  });

  test('PaymentSettings type', () => {
    const settings: PaymentSettings = {
      vpa: 'eventia@upi',
      qr_enabled: true,
      upi_enabled: true,
      card_enabled: true,
      netbanking_enabled: true
    };
    expect(settings).toBeDefined();
  });
}); 