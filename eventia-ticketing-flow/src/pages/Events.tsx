import React, { useState, useEffect } from 'react';
import { useQuery } from '@tanstack/react-query';
import Navbar from '@/components/layout/Navbar';
import Footer from '@/components/layout/Footer';
import EventCard from '@/components/events/EventCard';
import { Search, Filter, Loader2 } from 'lucide-react';
import { Input } from '@/components/ui/input';
import { api, fetchEvents } from '@/lib/api';
import { EventResponse } from '@/lib/types';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { mapApiEventToUIEvent } from '@/lib/adapters';

const Events = () => {
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedCategory, setSelectedCategory] = useState<string>('');
  const [categories, setCategories] = useState<string[]>(['All']);

  // Fetch events from API with improved error handling
  const { 
    data, 
    isLoading, 
    error, 
    refetch 
  } = useQuery({
    queryKey: ['events', selectedCategory],
    queryFn: async () => {
      try {
        return await fetchEvents({ category: selectedCategory || undefined });
      } catch (err) {
        console.error('Error fetching events:', err);
        throw err;
      }
    }
  });

  // Debug API response structure
  useEffect(() => {
    if (data) {
      console.debug('API Response Structure:', data);
    }
  }, [data]);

  // Extract and set categories from events data
  useEffect(() => {
    if (data?.events && data.events.length > 0) {
      const uniqueCategories = [...new Set(data.events.map(event => event.category).filter(Boolean))];
      setCategories(['All', ...uniqueCategories]);
    }
  }, [data?.events]);

  // Map API events to UI events using our adapter function
  const events = (data?.events || []).map(event => mapApiEventToUIEvent(event));

  // Filter events based on search term
  const filteredEvents = events.filter(event => {
    if (!searchTerm) return true;
    
    const searchLower = searchTerm.toLowerCase();
    return (
      (event.title?.toLowerCase() || '').includes(searchLower) || 
      (event.description?.toLowerCase() || '').includes(searchLower)
    );
  });

  // Handle error retry
  const handleRetry = () => {
    refetch();
  };

  return (
    <div className="flex flex-col min-h-screen">
      <Navbar />
      
      <main className="flex-grow pt-16">
        {/* Header */}
        <div className="bg-primary text-white py-12">
          <div className="container mx-auto px-4">
            <h1 className="text-3xl md:text-4xl font-bold mb-4">Discover Events</h1>
            <p className="text-lg md:text-xl text-white/80 max-w-2xl">
              Browse and book tickets for the most exciting cricket and cultural events in your city
            </p>
          </div>
        </div>
        
        {/* Search and Filter */}
        <div className="bg-white border-b py-4 sticky top-16 z-10">
          <div className="container mx-auto px-4">
            <div className="flex flex-col md:flex-row gap-4">
              <div className="relative flex-grow">
                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 h-5 w-5" />
                <Input
                  type="text"
                  placeholder="Search for events..."
                  className="pl-10 w-full"
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                />
              </div>
              <div className="flex items-center space-x-2 overflow-x-auto pb-2 md:pb-0">
                <Filter className="text-gray-400 h-5 w-5 flex-shrink-0" />
                {categories.map((category) => (
                  <button
                    key={category}
                    className={`px-4 py-2 rounded-full text-sm font-medium whitespace-nowrap ${
                      selectedCategory === (category === 'All' ? '' : category) 
                        ? 'bg-primary text-white' 
                        : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                    }`}
                    onClick={() => setSelectedCategory(category === 'All' ? '' : category)}
                  >
                    {category}
                  </button>
                ))}
              </div>
            </div>
          </div>
        </div>
        
        {/* Events Grid */}
        <div className="py-12 bg-gray-50">
          <div className="container mx-auto px-4">
            {isLoading ? (
              <div className="flex justify-center items-center py-20">
                <Loader2 className="h-10 w-10 animate-spin text-primary" />
                <span className="ml-2 text-gray-600">Loading events...</span>
              </div>
            ) : error ? (
              <Alert variant="destructive" className="mb-6">
                <AlertDescription>
                  <div className="flex flex-col">
                    <p>{error instanceof Error ? error.message : 'Failed to load events. Please try again.'}</p>
                    <button 
                      onClick={handleRetry}
                      className="mt-2 bg-red-100 text-red-800 px-4 py-2 rounded text-sm font-medium"
                    >
                      Retry
                    </button>
                  </div>
                </AlertDescription>
              </Alert>
            ) : filteredEvents.length > 0 ? (
              <>
                <div className="mb-6 text-gray-600">
                  Showing {filteredEvents.length} {filteredEvents.length === 1 ? 'event' : 'events'}
                </div>
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                  {filteredEvents.map((event) => (
                    <EventCard key={event.id} event={event} />
                  ))}
                </div>
              </>
            ) : (
              <div className="text-center py-12">
                <div className="text-5xl mb-4">🔍</div>
                <h2 className="text-2xl font-semibold text-gray-800 mb-2">No events found</h2>
                <p className="text-gray-600">
                  We couldn't find any events matching your search. Try different keywords or filter criteria.
                </p>
              </div>
            )}
          </div>
        </div>
      </main>
      
      <Footer />
    </div>
  );
};

export default Events;
