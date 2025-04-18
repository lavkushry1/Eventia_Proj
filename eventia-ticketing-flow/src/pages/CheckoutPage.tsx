import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Helmet } from 'react-helmet-async';
import { Container } from '@/components/ui/container';
import { toast } from '@/hooks/use-toast';
import PageHeader from '@/components/layout/PageHeader';
import TicketConfirmation from '@/components/checkout/TicketConfirmation';
import { Card, CardContent } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Loader2 } from 'lucide-react';
import { api } from '@/lib/api';

interface BookingData {
  eventId: string;
  eventTitle: string;
  stadiumId: string;
  stadiumName: string;
  tickets: Array<{
    section_id: string;
    name: string;
    quantity: number;
    price: number;
    subtotal: number;
  }>;
  totalAmount: number;
}

const CheckoutPage = () => {
  const navigate = useNavigate();
  const [bookingData, setBookingData] = useState<BookingData | null>(null);
  const [loading, setLoading] = useState(true);
  const [eventDetails, setEventDetails] = useState({
    title: '',
    date: '',
    venue: '',
    image: ''
  });
  const [step, setStep] = useState<'confirmation' | 'payment' | 'success'>('confirmation');
  const [isProcessing, setIsProcessing] = useState(false);

  useEffect(() => {
    // Get booking data from session storage
    const data = sessionStorage.getItem('bookingData');
    if (!data) {
      toast({
        title: 'No booking data found',
        description: 'Please select your seats before proceeding to checkout.',
        variant: 'destructive'
      });
      navigate('/');
      return;
    }

    try {
      const parsed = JSON.parse(data) as BookingData;
      setBookingData(parsed);
      
      // Fetch event details
      const fetchEventDetails = async () => {
        try {
          const response = await api.get(`/events/${parsed.eventId}`);
          const event = response.data;
          setEventDetails({
            title: event.title,
            date: new Date(event.start_time).toLocaleString('en-US', {
              weekday: 'short',
              day: 'numeric',
              month: 'short',
              year: 'numeric',
              hour: 'numeric',
              minute: '2-digit'
            }),
            venue: event.venue,
            image: event.image_url
          });
        } catch (error) {
          console.error('Failed to fetch event details', error);
        } finally {
          setLoading(false);
        }
      };
      
      fetchEventDetails();
    } catch (error) {
      console.error('Error parsing booking data', error);
      toast({
        title: 'Invalid booking data',
        description: 'There was an error processing your booking. Please try again.',
        variant: 'destructive'
      });
      navigate('/');
    }
  }, [navigate]);

  const handleProceedToPayment = () => {
    setStep('payment');
    // Scroll to top
    window.scrollTo(0, 0);
  };

  const handleCancel = () => {
    // Confirm before canceling
    if (window.confirm('Are you sure you want to cancel this booking? Your selections will be lost.')) {
      sessionStorage.removeItem('bookingData');
      navigate('/');
    }
  };

  const handleCompletePayment = async () => {
    if (!bookingData) return;
    
    setIsProcessing(true);
    
    try {
      // Simulate payment processing
      await new Promise(resolve => setTimeout(resolve, 2000));
      
      // Create booking in backend
      const response = await api.bookTicket({
        event_id: bookingData.eventId,
        stadium_id: bookingData.stadiumId,
        sections: bookingData.tickets.map(ticket => ({
          section_id: ticket.section_id,
          quantity: ticket.quantity
        })),
        customer_name: 'John Doe', // In a real app, this would come from a form
        customer_email: 'john@example.com',
        customer_phone: '1234567890'
      });
      
      // Save booking reference for success page
      sessionStorage.setItem('bookingReference', response.booking_id);
      
      // Clear booking data
      sessionStorage.removeItem('bookingData');
      
      // Show success and navigate
      setStep('success');
      toast({
        title: 'Booking Successful!',
        description: `Your booking reference is: ${response.booking_id}`,
      });
    } catch (error) {
      console.error('Payment failed', error);
      toast({
        title: 'Payment Failed',
        description: 'There was an error processing your payment. Please try again.',
        variant: 'destructive'
      });
    } finally {
      setIsProcessing(false);
    }
  };

  if (loading) {
    return (
      <Container className="py-12">
        <div className="flex flex-col items-center justify-center min-h-[300px]">
          <Loader2 className="h-8 w-8 animate-spin text-primary" />
          <p className="mt-4">Loading checkout information...</p>
        </div>
      </Container>
    );
  }

  return (
    <>
      <Helmet>
        <title>Checkout | Eventia</title>
      </Helmet>
      
      <PageHeader
        title={step === 'success' ? 'Booking Successful!' : 'Complete Your Booking'}
        subtitle={step === 'success' ? 'Your tickets have been booked successfully' : 'Review and confirm your selection'}
      />
      
      <Container className="py-12">
        {step === 'confirmation' && bookingData && (
          <TicketConfirmation
            eventTitle={eventDetails.title || bookingData.eventTitle}
            eventDate={eventDetails.date}
            eventVenue={eventDetails.venue}
            stadiumName={bookingData.stadiumName}
            tickets={bookingData.tickets}
            totalAmount={bookingData.totalAmount}
            onProceed={handleProceedToPayment}
            onCancel={handleCancel}
          />
        )}
        
        {step === 'payment' && bookingData && (
          <div className="max-w-3xl mx-auto">
            <Card>
              <CardContent className="pt-6 space-y-6">
                <div className="text-xl font-bold text-center">Payment Details</div>
                
                {/* This would be a full payment form in a real application */}
                <div className="p-4 border rounded-md">
                  <div className="text-lg font-semibold mb-4">Simulated Payment</div>
                  <p className="text-gray-600 mb-6">
                    This is a simulated payment screen. In a real application, this would contain
                    credit card fields, UPI options, and other payment methods.
                  </p>
                  
                  <div className="flex justify-between border-t pt-4 font-bold">
                    <span>Amount:</span>
                    <span>₹{(bookingData.totalAmount + Math.round(bookingData.totalAmount * 0.03)).toLocaleString()}</span>
                  </div>
                </div>
                
                <div className="flex justify-between pt-4">
                  <Button variant="outline" onClick={() => setStep('confirmation')}>
                    Back
                  </Button>
                  <Button onClick={handleCompletePayment} disabled={isProcessing}>
                    {isProcessing ? (
                      <span className="flex items-center">
                        <svg className="animate-spin -ml-1 mr-2 h-4 w-4 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                          <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                          <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                        </svg>
                        Processing Payment...
                      </span>
                    ) : (
                      'Complete Payment'
                    )}
                  </Button>
                </div>
              </CardContent>
            </Card>
          </div>
        )}
        
        {step === 'success' && (
          <div className="max-w-3xl mx-auto text-center space-y-6">
            <div className="w-20 h-20 bg-green-100 rounded-full mx-auto flex items-center justify-center">
              <svg xmlns="http://www.w3.org/2000/svg" className="h-10 w-10 text-green-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
              </svg>
            </div>
            
            <h2 className="text-2xl font-bold">Booking Successful!</h2>
            <p className="text-gray-600">
              Your booking has been confirmed. You will receive an email with your ticket details shortly.
            </p>
            
            <Button className="mt-6" onClick={() => navigate('/')}>
              Back to Home
            </Button>
          </div>
        )}
      </Container>
    </>
  );
};

export default CheckoutPage; 