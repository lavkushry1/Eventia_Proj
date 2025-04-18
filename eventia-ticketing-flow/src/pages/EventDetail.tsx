import React, { useState, useEffect } from 'react';
import { useParams, useNavigate, Link } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import Navbar from '@/components/layout/Navbar';
import Footer from '@/components/layout/Footer';
import { Calendar, Clock, MapPin, Tag, ArrowLeft, ShoppingCart, Eye, Loader2, AlertTriangle, CreditCard } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { toast } from '@/hooks/use-toast';
import TeamBadge from '@/components/TeamBadge';
import { api } from '@/lib/api';
import { mapApiEventToUIEvent } from '@/lib/adapters';
import { QRCodeSVG } from 'qrcode.react';
import { format } from 'date-fns';
import { CalendarDays, Ticket } from 'lucide-react';
import { Badge } from '@/components/ui/badge';
import { Separator } from '@/components/ui/separator';
import BookingModal from '@/components/booking/BookingModal';
import StadiumBookingModal from '@/components/booking/StadiumBookingModal';
import { Skeleton } from '@/components/ui/skeleton';

interface TicketType {
  category: string;
  price: number;
  available: number;
}

interface Event {
  id: string;
  title: string;
  description: string;
  date: string;
  time: string;
  venue: string;
  category: string;
  image_url: string;
  is_featured: boolean;
  status: string;
  ticket_types: TicketType[];
  team_home?: {
    name: string;
    logo: string;
    primary_color: string;
    secondary_color: string;
  };
  team_away?: {
    name: string;
    logo: string;
    primary_color: string;
    secondary_color: string;
  };
}

const EventDetail = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const [selectedTicket, setSelectedTicket] = useState<TicketType | null>(null);
  const [quantity, setQuantity] = useState(1);
  const [event, setEvent] = useState<Event | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [isBookingModalOpen, setIsBookingModalOpen] = useState(false);
  const [isStadiumBookingModalOpen, setIsStadiumBookingModalOpen] = useState(false);

  useEffect(() => {
    console.log(`EventDetail mounted with ID: ${id}`);
    return () => {
      console.log('EventDetail unmounted');
    };
  }, [id]);

  // Fetch event details from API
  const { data: eventData, isLoading, error: queryError, isError, refetch } = useQuery({
    queryKey: ['event', id],
    queryFn: async () => {
      console.log(`Fetching event with ID: ${id}`);
      try {
        const apiEvent = await api.getEvent(id);
        console.log(`Received API event data:`, apiEvent);
        
        if (!apiEvent || (Object.keys(apiEvent).length === 0)) {
          console.error('API returned empty event data');
          throw new Error('Event data is empty');
        }
        
        const uiEvent = mapApiEventToUIEvent(apiEvent);
        console.log(`Mapped to UI event:`, uiEvent);
        return uiEvent;
      } catch (error) {
        console.error(`Error fetching event ${id}:`, error);
        throw error;
      }
    },
    retry: 1,
    refetchOnWindowFocus: false
  });
  
  useEffect(() => {
    if (eventData && eventData.ticketTypes && eventData.ticketTypes.length > 0) {
      console.log(`Available ticket types:`, eventData.ticketTypes);
      // Select default ticket type when data loads (if not already selected)
      if (!selectedTicket) {
        const defaultTicket = eventData.ticketTypes[0];
        console.log(`Setting default ticket type:`, defaultTicket);
        setSelectedTicket(defaultTicket);
      }
    }
  }, [eventData, selectedTicket]);

  useEffect(() => {
    if (eventData) {
      // Basic validation of data
      if (eventData.id && eventData.title) {
        setEvent({
          id: eventData.id,
          title: eventData.title,
          description: eventData.description || '',
          date: eventData.date || '',
          time: eventData.time || '',
          venue: eventData.venue || '',
          category: eventData.category || '',
          image_url: eventData.image || '',
          is_featured: !!eventData.featured,
          status: 'upcoming',
          ticket_types: eventData.ticketTypes || [],
          ...(eventData.teams && {
            team_home: {
              name: eventData.teams.team1?.name || '',
              logo: eventData.teams.team1?.shortName?.toLowerCase() || '',
              primary_color: eventData.teams.team1?.color || '#000000',
              secondary_color: '#FFFFFF'
            },
            team_away: {
              name: eventData.teams.team2?.name || '',
              logo: eventData.teams.team2?.shortName?.toLowerCase() || '',
              primary_color: eventData.teams.team2?.color || '#000000',
              secondary_color: '#FFFFFF'
            }
          })
        });
        setLoading(false);
      }
    } else if (isError) {
      setError('Failed to load event details');
      setLoading(false);
    }
  }, [eventData, isError]);

  // Handle adding to cart
  const handleAddToCart = () => {
    if (!event) return;
    
    if (!selectedTicket) {
      toast({
        title: "Please select a ticket type",
        description: "Choose the type of ticket you want to purchase.",
        variant: "destructive"
      });
      return;
    }

    // Basic validation to prevent adding more tickets than available
    if (quantity > selectedTicket.available) {
      toast({
        title: "Not enough tickets available",
        description: `Only ${selectedTicket.available} tickets left for ${selectedTicket.category}.`,
        variant: "destructive"
      });
      return;
    }

    // Store booking data in sessionStorage for checkout
    const bookingData = {
      eventId: event.id,
      eventTitle: event.title,
      eventDate: event.date,
      eventTime: event.time,
      eventVenue: event.venue,
      tickets: [{
        category: selectedTicket.category,
        quantity,
        price: selectedTicket.price,
        subtotal: selectedTicket.price * quantity
      }],
      totalAmount: selectedTicket.price * quantity,
      // Only include teams if this is an IPL match
      ...(event.category === 'IPL' && event.team_home && event.team_away ? { teams: { team1: event.team_home, team2: event.team_away } } : {})
    };
    
    console.log('Saving booking data:', bookingData);
    sessionStorage.setItem('bookingData', JSON.stringify(bookingData));
    
    toast({
      title: "Tickets added to cart",
      description: `${quantity} ${selectedTicket.category} ticket(s) added to your cart.`,
    });

    // Redirect to checkout page
    navigate('/checkout');
  };

  const handleBookingClick = () => {
    // For cricket events, use the stadium booking flow
    if (event?.category?.toLowerCase() === 'cricket' || event?.category?.toLowerCase() === 'ipl') {
      console.log('Opening stadium booking modal for cricket event');
      setIsStadiumBookingModalOpen(true);
    } else {
      console.log('Opening regular booking modal for non-cricket event');
      setIsBookingModalOpen(true);
    }
  };

  // Show loading state
  if (isLoading || loading) {
    return (
      <div className="min-h-screen flex flex-col">
        <Navbar />
        <main className="flex-grow container mx-auto px-4 py-8">
          <div className="flex flex-col items-center justify-center h-[50vh] gap-4">
            <Loader2 className="h-10 w-10 animate-spin text-primary" />
            <p className="text-xl">Loading event details...</p>
          </div>
        </main>
        <Footer />
      </div>
    );
  }

  // Show error state with retry button
  if (error || !event) {
    return (
      <div className="min-h-screen flex flex-col">
        <Navbar />
        <main className="flex-grow container mx-auto px-4 py-8">
          <div className="flex flex-col justify-center items-center h-[50vh] gap-4">
            <p className="text-2xl text-red-500">Error loading event</p>
            <p className="text-gray-600">
              {error}
            </p>
            <div className="flex gap-4 mt-4">
              <Button onClick={() => refetch()}>Retry</Button>
              <Link to="/events">
                <Button variant="outline">Back to Events</Button>
              </Link>
            </div>
          </div>
        </main>
        <Footer />
      </div>
    );
  }

  // Check if this is an IPL match with teams
  const isIplMatch = event.category === 'IPL' && event.team_home && event.team_away;

  // Format date for display if available
  const formattedDate = event.date
    ? format(new Date(event.date), 'MMMM dd, yyyy')
    : 'Date TBD';

  const isCricketMatch = event?.category?.toLowerCase() === 'cricket' || 
                        event?.category?.toLowerCase() === 'ipl';

  return (
    <div className="flex flex-col min-h-screen">
      <Navbar />

      <main className="flex-grow bg-gray-50 pt-16 pb-12">
        <div className="container mx-auto px-4">
          <Button variant="ghost" onClick={() => navigate(-1)} className="mb-4">
            <ArrowLeft className="h-4 w-4 mr-2" />
            Back
          </Button>

          <Card className="overflow-hidden">
            <div className="md:flex">
              <div className="md:w-1/2">
                <img
                  src={event.image_url || "/placeholder.svg"}
                  alt={event.title}
                  className="w-full h-auto object-cover"
                  onError={(e) => {
                    e.currentTarget.src = "/placeholder.svg";
                  }}
                />
              </div>
              <div className="md:w-1/2 p-6">
                <CardHeader className="pb-4">
                  <CardTitle className="text-2xl font-bold">{event.title || 'Unnamed Event'}</CardTitle>
                  {isIplMatch && (
                    <CardDescription className="flex items-center gap-2 mt-2">
                      <TeamBadge 
                        team={event.team_home?.name} 
                        color={event.team_home?.primary_color}
                      />
                      <span className="text-gray-500">vs</span>
                      <TeamBadge 
                        team={event.team_away?.name}
                        color={event.team_away?.primary_color}
                      />
                    </CardDescription>
                  )}
                </CardHeader>
                <CardContent className="text-gray-700">
                  <p className="mb-4">{event.description || 'No description available.'}</p>
                  <div className="flex items-center mb-2">
                    <CalendarDays className="h-4 w-4 mr-2 text-gray-400" />
                    {formattedDate}
                  </div>
                  <div className="flex items-center mb-2">
                    <Clock className="h-4 w-4 mr-2 text-gray-400" />
                    {event.time || 'Time TBD'}
                  </div>
                  <div className="flex items-center mb-2">
                    <MapPin className="h-4 w-4 mr-2 text-gray-400" />
                    {event.venue || 'Venue TBD'}
                  </div>
                  <Separator className="my-4" />

                  <div className="mb-4">
                    <h3 className="text-lg font-semibold mb-2">Tickets</h3>
                    {event.ticket_types && event.ticket_types.length > 0 ? (
                      event.ticket_types.map((ticket, index) => (
                        <div
                          key={index}
                          className={`border rounded-md p-3 mb-2 cursor-pointer ${selectedTicket === ticket ? 'border-primary' : 'border-gray-200'}`}
                          onClick={() => setSelectedTicket(ticket)}
                        >
                          <div className="flex justify-between items-center">
                            <div>
                              <p className="font-medium">{ticket.category}</p>
                              <p className="text-sm text-gray-500">₹{ticket.price}</p>
                            </div>
                            <p className="text-sm text-gray-500">{ticket.available} available</p>
                          </div>
                        </div>
                      ))
                    ) : (
                      <Alert className="mb-4">
                        <AlertDescription>
                          No tickets available for this event at the moment.
                        </AlertDescription>
                      </Alert>
                    )}
                  </div>

                  {event.ticket_types && event.ticket_types.length > 0 && (
                    <>
                      <div className="mb-4">
                        <h3 className="text-lg font-semibold mb-2">Quantity</h3>
                        <div className="flex items-center">
                          <Button
                            variant="outline"
                            size="icon"
                            onClick={() => setQuantity(Math.max(1, quantity - 1))}
                            disabled={quantity <= 1}
                          >
                            -
                          </Button>
                          <span className="mx-4 font-medium">{quantity}</span>
                          <Button
                            variant="outline"
                            size="icon"
                            onClick={() => {
                              const maxAvailable = selectedTicket?.available || 10;
                              setQuantity(Math.min(maxAvailable, quantity + 1));
                            }}
                            disabled={selectedTicket && quantity >= selectedTicket.available}
                          >
                            +
                          </Button>
                        </div>
                      </div>

                      <div className="mt-6">
                        <Button 
                          className="w-full" 
                          size="lg" 
                          onClick={handleBookingClick}
                          disabled={!selectedTicket}
                        >
                          <ShoppingCart className="mr-2 h-5 w-5" />
                          Book Now
                        </Button>
                      </div>
                    </>
                  )}
                </CardContent>
              </div>
            </div>
          </Card>
          
          <div className="mt-6 text-center">
            <Link to={`/venue-preview/${id}`}>
              <Button variant="secondary" size="lg" className="flex items-center">
                <Eye className="h-5 w-5 mr-2" />
                View Venue in AR
              </Button>
            </Link>
          </div>
        </div>
      </main>

      <Footer />

      {/* Regular Booking Modal */}
      {isBookingModalOpen && (
        <BookingModal 
          isOpen={isBookingModalOpen}
          onClose={() => setIsBookingModalOpen(false)}
          eventTitle={event.title}
          ticketTypes={event.ticket_types || []}
        />
      )}
      
      {/* Stadium Booking Modal for Cricket Events */}
      {isStadiumBookingModalOpen && (
        <StadiumBookingModal
          isOpen={isStadiumBookingModalOpen}
          onClose={() => setIsStadiumBookingModalOpen(false)}
          eventId={event.id}
          eventTitle={event.title}
        />
      )}
    </div>
  );
};

export default EventDetail;
