import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { MemoryRouter, Routes, Route } from 'react-router-dom';
import { vi } from 'vitest';
import AdminImageUploads from '@/pages/AdminImageUploads';
import * as api from '@/lib/api';

// Mock the API module
vi.mock('@/lib/api', () => ({
  uploadImage: vi.fn(),
}));

// Mock environment variables
vi.mock('import.meta.env', () => ({
  VITE_API_BASE_URL: 'http://localhost:8000',
}));

describe('AdminImageUploads Component', () => {
  beforeEach(() => {
    vi.resetAllMocks();
  });
  
  test('renders all tabs correctly', () => {
    render(
      <MemoryRouter>
        <AdminImageUploads />
      </MemoryRouter>
    );
    
    expect(screen.getByRole('heading', { name: /admin image management/i })).toBeInTheDocument();
    expect(screen.getByText('Event Posters')).toBeInTheDocument();
    expect(screen.getByText('Venue Images')).toBeInTheDocument();
    expect(screen.getByText('Team Logos')).toBeInTheDocument();
  });
  
  test('switches tabs when clicked', () => {
    render(
      <MemoryRouter>
        <AdminImageUploads />
      </MemoryRouter>
    );
    
    // Default tab is Event Posters
    expect(screen.getByText('Upload Event Poster')).toBeInTheDocument();
    
    // Click on Team Logos tab
    fireEvent.click(screen.getByText('Team Logos'));
    expect(screen.getByText('Upload Team Logo')).toBeInTheDocument();
    expect(screen.getByText('Team Code (e.g., CSK, MI)')).toBeInTheDocument();
    
    // Click on Venue Images tab
    fireEvent.click(screen.getByText('Venue Images'));
    expect(screen.getByText('Upload Venue Image')).toBeInTheDocument();
  });
  
  test('pre-fills event ID when provided in URL', () => {
    render(
      <MemoryRouter initialEntries={['/admin/event/123/images']}>
        <Routes>
          <Route path="/admin/event/:eventId/images" element={<AdminImageUploads />} />
        </Routes>
      </MemoryRouter>
    );
    
    const idInput = screen.getByLabelText(/Event ID/i);
    expect(idInput).toHaveValue('123');
  });
  
  test('handles successful image upload', async () => {
    // Mock successful upload response
    vi.mocked(api.uploadImage).mockResolvedValueOnce({
      message: 'Event poster uploaded successfully',
      image_url: '/static/events/123.png'
    });
    
    render(
      <MemoryRouter>
        <AdminImageUploads />
      </MemoryRouter>
    );
    
    // Fill form
    fireEvent.change(screen.getByLabelText(/Event ID/i), {
      target: { value: '123' }
    });
    
    // Create a file
    const file = new File(['dummy content'], 'test.png', { type: 'image/png' });
    const fileInput = screen.getByLabelText(/Image File/i);
    
    // Simulate file selection
    Object.defineProperty(fileInput, 'files', {
      value: [file]
    });
    fireEvent.change(fileInput);
    
    // Submit form
    fireEvent.click(screen.getByRole('button', { name: /Upload Image/i }));
    
    // Check loading state
    expect(screen.getByText('Uploading...')).toBeInTheDocument();
    
    // Wait for success message
    await waitFor(() => {
      expect(screen.getByText('Event poster uploaded successfully')).toBeInTheDocument();
    });
    
    // Check preview section
    expect(screen.getByText('Preview:')).toBeInTheDocument();
    const previewImg = screen.getByAltText('Uploaded preview');
    expect(previewImg).toHaveAttribute('src', 'http://localhost:8000/static/events/123.png');
    
    // Check API was called correctly
    expect(api.uploadImage).toHaveBeenCalledWith(
      '/api/v1/admin/upload/event-poster?event_id=123',
      expect.any(FormData)
    );
  });
  
  test('handles upload error', async () => {
    // Mock error response
    vi.mocked(api.uploadImage).mockRejectedValueOnce(new Error('Invalid file format'));
    
    render(
      <MemoryRouter>
        <AdminImageUploads />
      </MemoryRouter>
    );
    
    // Fill form
    fireEvent.change(screen.getByLabelText(/Event ID/i), {
      target: { value: '123' }
    });
    
    // Create a file
    const file = new File(['dummy content'], 'test.png', { type: 'image/png' });
    const fileInput = screen.getByLabelText(/Image File/i);
    
    // Simulate file selection
    Object.defineProperty(fileInput, 'files', {
      value: [file]
    });
    fireEvent.change(fileInput);
    
    // Submit form
    fireEvent.click(screen.getByRole('button', { name: /Upload Image/i }));
    
    // Wait for error message
    await waitFor(() => {
      expect(screen.getByText('Invalid file format')).toBeInTheDocument();
    });
  });
  
  test('validates required fields', async () => {
    render(
      <MemoryRouter>
        <AdminImageUploads />
      </MemoryRouter>
    );
    
    // Submit empty form
    fireEvent.click(screen.getByRole('button', { name: /Upload Image/i }));
    
    // HTML required validation should prevent form submission
    expect(api.uploadImage).not.toHaveBeenCalled();
  });
}); 