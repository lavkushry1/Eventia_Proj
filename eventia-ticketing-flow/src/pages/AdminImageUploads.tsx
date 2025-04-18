import React, { useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { uploadImage } from '@/lib/api';

interface UploadResponse {
  message: string;
  image_url: string;
}

const AdminImageUploads: React.FC = () => {
  const { eventId } = useParams<{ eventId?: string }>();
  const navigate = useNavigate();
  const [isUploading, setIsUploading] = useState(false);
  const [uploadedImageUrl, setUploadedImageUrl] = useState<string>('');
  const [message, setMessage] = useState<string>('');
  const [error, setError] = useState<string>('');
  const [activeTab, setActiveTab] = useState<'event' | 'venue' | 'team'>('event');

  const apiBaseUrl = import.meta.env.VITE_API_BASE_URL || '';

  const handleFileUpload = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    setError('');
    setMessage('');
    
    try {
      setIsUploading(true);
      
      const formData = new FormData(e.currentTarget);
      const file = formData.get('file') as File;
      const id = formData.get('id') as string;
      
      if (!file || file.size === 0) {
        throw new Error('Please select a file to upload');
      }
      
      if (!id) {
        throw new Error(`Please provide ${activeTab === 'team' ? 'a team code' : 'an ID'}`);
      }
      
      let endpoint = '';
      
      switch (activeTab) {
        case 'event':
          endpoint = `/api/v1/admin/upload/event-poster?event_id=${id}`;
          break;
        case 'venue':
          endpoint = `/api/v1/admin/upload/venue-image?venue_id=${id}`;
          break;
        case 'team':
          endpoint = `/api/v1/admin/upload/team-logo?team_code=${id}`;
          break;
      }
      
      const uploadData = new FormData();
      uploadData.append('file', file);
      
      const response = await uploadImage(endpoint, uploadData) as UploadResponse;
      
      setUploadedImageUrl(response.image_url);
      setMessage(response.message);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred during upload');
    } finally {
      setIsUploading(false);
    }
  };

  return (
    <div className="container mx-auto p-4 max-w-4xl">
      <h1 className="text-2xl font-bold mb-6">Admin Image Management</h1>
      
      {/* Tab Navigation */}
      <div className="flex border-b mb-6">
        <button 
          className={`px-4 py-2 ${activeTab === 'event' ? 'border-b-2 border-blue-500 text-blue-500' : 'text-gray-500'}`}
          onClick={() => setActiveTab('event')}
        >
          Event Posters
        </button>
        <button 
          className={`px-4 py-2 ${activeTab === 'venue' ? 'border-b-2 border-blue-500 text-blue-500' : 'text-gray-500'}`}
          onClick={() => setActiveTab('venue')}
        >
          Venue Images
        </button>
        <button 
          className={`px-4 py-2 ${activeTab === 'team' ? 'border-b-2 border-blue-500 text-blue-500' : 'text-gray-500'}`}
          onClick={() => setActiveTab('team')}
        >
          Team Logos
        </button>
      </div>
      
      {/* Upload Form */}
      <div className="bg-white rounded-lg shadow-md p-6">
        <h2 className="text-xl font-semibold mb-4">
          Upload {activeTab === 'event' ? 'Event Poster' : activeTab === 'venue' ? 'Venue Image' : 'Team Logo'}
        </h2>
        
        <form onSubmit={handleFileUpload} className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              {activeTab === 'event' ? 'Event ID' : 
               activeTab === 'venue' ? 'Venue ID' : 
               'Team Code (e.g., CSK, MI)'}
            </label>
            <input
              type="text"
              name="id"
              className="w-full p-2 border border-gray-300 rounded-md"
              defaultValue={activeTab === 'event' && eventId ? eventId : ''}
              required
            />
          </div>
          
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Image File (PNG, JPG, JPEG, WEBP)
            </label>
            <input
              type="file"
              name="file"
              accept=".png,.jpg,.jpeg,.webp"
              className="w-full p-2 border border-gray-300 rounded-md"
              required
            />
          </div>
          
          <button
            type="submit"
            className="px-4 py-2 bg-blue-500 text-white rounded-md hover:bg-blue-600 disabled:bg-gray-400"
            disabled={isUploading}
          >
            {isUploading ? 'Uploading...' : 'Upload Image'}
          </button>
        </form>
        
        {/* Success/Error Messages */}
        {message && (
          <div className="mt-4 p-3 bg-green-100 text-green-700 rounded-md">
            {message}
          </div>
        )}
        
        {error && (
          <div className="mt-4 p-3 bg-red-100 text-red-700 rounded-md">
            {error}
          </div>
        )}
        
        {/* Image Preview */}
        {uploadedImageUrl && (
          <div className="mt-6">
            <h3 className="text-lg font-medium mb-2">Preview:</h3>
            <div className="border rounded-md overflow-hidden">
              <img
                src={`${apiBaseUrl}${uploadedImageUrl}`}
                alt="Uploaded preview"
                className="max-w-full h-auto object-contain max-h-80"
                onError={(e) => {
                  (e.target as HTMLImageElement).src = '/placeholder.svg';
                }}
              />
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default AdminImageUploads; 