import { render, screen } from '@testing-library/react';
import { describe, it, expect, vi } from 'vitest';
import { BrowserRouter } from 'react-router-dom';
import EventCard from './EventCard';

describe('EventCard', () => {
  const mockEvent = {
    id: 'evt_1',
    title: 'Mumbai Indians vs Chennai Super Kings',
    date: '2025-05-01',
    time: '19:30',
    venue: 'Wankhede Stadium, Mumbai',
    image: 'https://picsum.photos/800/450?random=1',
    price: 2500,
    teams: {
      team1: {
        name: 'Mumbai Indians',
        shortName: 'MI',
        logo: 'mi',
        primaryColor: '#004BA0',
        secondaryColor: '#FFFFFF'
      },
      team2: {
        name: 'Chennai Super Kings',
        shortName: 'CSK',
        logo: 'csk',
        primaryColor: '#FFFF00',
        secondaryColor: '#0081E9'
      }
    }
  };

  it('renders event information correctly', () => {
    render(
      <BrowserRouter>
        <EventCard event={mockEvent} />
      </BrowserRouter>
    );

    // Check that the title is displayed
    expect(screen.getByText(mockEvent.title)).toBeInTheDocument();
    
    // Check that venue is displayed
    expect(screen.getByText(mockEvent.venue)).toBeInTheDocument();
    
    // Check that formatted date is displayed (depends on your format implementation)
    // This is just a placeholder, adjust according to your actual formatting
    expect(screen.getByText(/May 1, 2025/)).toBeInTheDocument();
    
    // Check that price is displayed correctly
    expect(screen.getByText(/₹2,500/)).toBeInTheDocument();
    
    // Check that team badges are displayed
    expect(screen.getByText('MI')).toBeInTheDocument();
    expect(screen.getByText('CSK')).toBeInTheDocument();
    
    // Check that the image is rendered with correct src
    const image = screen.getByRole('img');
    expect(image).toHaveAttribute('src', mockEvent.image);
    expect(image).toHaveAttribute('alt', mockEvent.title);
  });

  it('renders "Sold Out" badge when no tickets are available', () => {
    render(
      <BrowserRouter>
        <EventCard event={{ ...mockEvent, soldOut: true }} />
      </BrowserRouter>
    );

    expect(screen.getByText('Sold Out')).toBeInTheDocument();
  });

  it('links to the event detail page', () => {
    render(
      <BrowserRouter>
        <EventCard event={mockEvent} />
      </BrowserRouter>
    );

    // Find the link and check that it points to the event detail page
    const link = screen.getByRole('link');
    expect(link).toHaveAttribute('href', `/events/${mockEvent.id}`);
  });
}); 