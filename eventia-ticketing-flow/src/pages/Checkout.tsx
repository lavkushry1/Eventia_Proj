import React, { useState, useEffect } from 'react';
import { useNavigate, useLocation, useParams } from 'react-router-dom';
import Navbar from '@/components/layout/Navbar';
import Footer from '@/components/layout/Footer';
import { ArrowLeft, ArrowRight, Loader2, Calendar, MapPin, Clock, CreditCard, AlertTriangle } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Separator } from '@/components/ui/separator';
import { toast } from '@/hooks/use-toast';
import { useMutation, useQuery } from '@tanstack/react-query';
import { api, createBooking, verifyPayment, fetchPaymentSettings, ApiBookingResponse, ApiUTRResponse, ApiPaymentSettings } from '@/lib/api';
import { mapUIBookingToApiBooking } from '@/lib/adapters';
import { QRCodeSVG } from 'qrcode.react';
import TeamBadge from '@/components/TeamBadge';
import { FormField, FormItem, FormLabel, FormControl } from '@/components/ui/form';
import { z } from 'zod';
import { Select, SelectItem } from '@/components/ui/select';
import { config } from '../config';

// Define CustomerInfo interface locally if not exported from adapters
interface CustomerInfo {
  name: string;
  email: string;
  phone: string;
  address?: string;
  city?: string;
  state?: string;
  pincode?: string;
}

// API Base URL for image paths
const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:3002';

interface TicketInfo {
  category: string;
  quantity: number;
  price: number;
  subtotal: number;
}

interface BookingData {
  eventId: string;
  eventTitle: string;
  tickets: TicketInfo[];
  totalAmount: number;
  eventDate?: string;
  eventTime?: string;
  eventVenue?: string;
  teams?: {
    team1: {
      name: string;
      shortName: string;
      logo?: string;
      color?: string;
    };
    team2: {
      name: string;
      shortName: string;
      logo?: string;
      color?: string;
    };
  };
}

// Payment expiration countdown component
const PaymentCountdown = ({ startTime }: { startTime: Date }) => {
  const [timeLeft, setTimeLeft] = useState<number>(0);
  
  useEffect(() => {
    // Calculate time left in seconds (30 minute limit)
    const calculateTimeLeft = () => {
      const now = new Date();
      const elapsed = Math.floor((now.getTime() - startTime.getTime()) / 1000);
      const totalSeconds = 30 * 60; // 30 minutes in seconds
      const remaining = Math.max(0, totalSeconds - elapsed);
      setTimeLeft(remaining);
    };
    
    // Initial calculation
    calculateTimeLeft();
    
    // Update every second
    const timer = setInterval(calculateTimeLeft, 1000);
    
    // Clean up on unmount
    return () => clearInterval(timer);
  }, [startTime]);
  
  // Format time as mm:ss
  const minutes = Math.floor(timeLeft / 60);
  const seconds = timeLeft % 60;
  const formattedTime = `${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`;
  
  // Calculate progress percentage
  const progress = (timeLeft / (30 * 60)) * 100;
  
  // Show warning when less than 5 minutes remain
  const isWarning = timeLeft < 5 * 60;
  
  if (timeLeft <= 0) {
    return (
      <div className="bg-red-50 p-3 rounded-md border border-red-200 flex items-center mt-2 mb-4">
        <AlertTriangle className="h-5 w-5 text-red-500 mr-2" />
        <div>
          <p className="text-sm font-medium text-red-700">Payment window expired</p>
          <p className="text-xs text-red-600">
            Your booking has expired. Please start a new booking.
          </p>
        </div>
      </div>
    );
  }
  
  return (
    <div className={`p-3 rounded-md border flex items-center mt-2 mb-4 ${isWarning ? 'bg-yellow-50 border-yellow-200' : 'bg-blue-50 border-blue-200'}`}>
      <Clock className={`h-5 w-5 mr-2 ${isWarning ? 'text-yellow-500' : 'text-blue-500'}`} />
      <div className="flex-1">
        <div className="flex justify-between items-center mb-1">
          <p className={`text-sm font-medium ${isWarning ? 'text-yellow-700' : 'text-blue-700'}`}>
            {isWarning ? 'Payment window closing soon' : 'Payment window'}
          </p>
          <p className={`text-sm font-medium ${isWarning ? 'text-yellow-700' : 'text-blue-700'}`}>{formattedTime}</p>
        </div>
        <div className="w-full bg-gray-200 rounded-full h-1.5">
          <div 
            className={`h-1.5 rounded-full ${isWarning ? 'bg-yellow-500' : 'bg-blue-500'}`} 
            style={{ width: `${progress}%` }}
          />
        </div>
        <p className="text-xs mt-1 text-gray-600">
          Please complete payment within the time limit to secure your tickets
        </p>
      </div>
    </div>
  );
};

const Checkout = () => {
  const { eventId, ticketTypeId } = useParams();
  const navigate = useNavigate();
  const location = useLocation();
  const queryParams = new URLSearchParams(location.search);
  const [bookingData, setBookingData] = useState<BookingData | null>(null);
  const [step, setStep] = useState(1);
  const [paymentCompleted, setPaymentCompleted] = useState(false);
  const [utr, setUtr] = useState('');
  const [customerInfo, setCustomerInfo] = useState<CustomerInfo>({
    name: '',
    email: '',
    phone: '',
    address: '',
    city: '',
    state: '',
    pincode: ''
  });
  const [bookingId, setBookingId] = useState<string | null>(null);
  const [ticketQRData, setTicketQRData] = useState<string | null>(null);
  const [bookingCreatedTime, setBookingCreatedTime] = useState<Date | null>(null);
  const [paymentMode, setPaymentMode] = useState<'vpa' | 'qr_image'>('vpa');
  const [qrImage, setQrImage] = useState<string | null>(null);

  // Payment settings
  const [paymentSettings, setPaymentSettings] = useState({
    merchantName: config().MERCHANT_NAME,
    vpaAddress: config().VPA_ADDRESS,
    isPaymentEnabled: config().PAYMENT_ENABLED,
    qrImageUrl: config().QR_IMAGE_URL,
    paymentMode: 'vpa',  // Default to vpa mode
  });

  // Fetch current payment settings from backend
  const { data: paymentSettingsData, isLoading: isLoadingPaymentSettings, error: paymentSettingsError } = useQuery({
    queryKey: ['paymentSettings'],
    queryFn: fetchPaymentSettings
  });
  
  // Handle successful payment settings fetch
  useEffect(() => {
    if (paymentSettingsData) {
      setPaymentSettings({
        merchantName: paymentSettingsData.merchant_name || config().MERCHANT_NAME,
        vpaAddress: paymentSettingsData.vpaAddress || config().VPA_ADDRESS,
        isPaymentEnabled: paymentSettingsData.isPaymentEnabled !== undefined ? paymentSettingsData.isPaymentEnabled : config().PAYMENT_ENABLED,
        qrImageUrl: paymentSettingsData.qrImageUrl || config().QR_IMAGE_URL,
        paymentMode: paymentSettingsData.payment_mode || 'vpa',  // Use the payment_mode from server
      });
    }
  }, [paymentSettingsData]);
  
  // Handle payment settings fetch error
  useEffect(() => {
    if (paymentSettingsError) {
      console.error('Error fetching payment settings:', paymentSettingsError);
      toast({
        title: "Error",
        description: "Could not load payment settings. Using default settings.",
        variant: "destructive"
      });
    }
  }, [paymentSettingsError]);

  // Format date if available
  const formattedDate = bookingData?.eventDate
    ? new Date(bookingData.eventDate).toLocaleDateString('en-US', {
        weekday: 'long',
        year: 'numeric',
        month: 'long',
        day: 'numeric'
      })
    : null;

  // Booking mutation
  const bookTicketMutation = useMutation({
    mutationFn: (data: {
      eventId: string;
      quantity: number;
      customerInfo: CustomerInfo;
    }) => {
      return createBooking(mapUIBookingToApiBooking(
        data.eventId,
        data.quantity,
        data.customerInfo
      ));
    },
    onSuccess: (response: ApiBookingResponse) => {
      setBookingId(response.booking_id);
      setBookingCreatedTime(new Date());
      setStep(2);
      toast({
        title: "Booking created successfully",
        description: "Please complete the payment to confirm your booking.",
      });
    },
    onError: (error: Error) => {
      toast({
        title: "Booking failed",
        description: error?.message || "Failed to create booking. Please try again.",
        variant: "destructive"
      });
    }
  });

  // UTR submission mutation
  const submitUTRMutation = useMutation({
    mutationFn: (data: { bookingId: string; utr: string }) => {
      return verifyPayment({
        booking_id: data.bookingId,
        utr: data.utr
      });
    },
    onSuccess: (response: ApiUTRResponse) => {
      setTicketQRData(JSON.stringify({
        bookingId: bookingId,
        eventTitle: bookingData?.eventTitle,
        customerName: customerInfo.name,
        tickets: bookingData?.tickets,
        eventDate: bookingData?.eventDate,
        eventTime: bookingData?.eventTime,
        eventVenue: bookingData?.eventVenue,
        teams: bookingData?.teams,
        timestamp: new Date().toISOString()
      }));
      setStep(3);
      toast({
        title: "Payment verified",
        description: "Your ticket has been generated successfully.",
      });
    },
    onError: (error: Error) => {
      toast({
        title: "Payment verification failed",
        description: error?.message || "Failed to verify payment. Please check your UTR number and try again.",
        variant: "destructive"
      });
    }
  });
  
  useEffect(() => {
    // Retrieve booking data from session storage
    const data = sessionStorage.getItem('bookingData');
    if (data) {
      try {
        const parsedData = JSON.parse(data);
        setBookingData(parsedData);
        console.log('Loaded booking data:', parsedData);
      } catch (error) {
        console.error('Error parsing booking data:', error);
        toast({
          title: "Error loading booking data",
          description: "Please try again or return to the event page.",
          variant: "destructive"
        });
        navigate('/events');
      }
    } else {
      // No booking data, redirect to events page
      navigate('/events');
    }
  }, [navigate]);

  const handleSubmitCustomerInfo = (e: React.FormEvent) => {
    e.preventDefault();
    
    // Validate customer info
    if (!customerInfo.name || !customerInfo.email || !customerInfo.phone) {
      toast({
        title: "Missing information",
        description: "Please fill in all required fields.",
        variant: "destructive"
      });
      return;
    }

    if (!bookingData) return;
    
    // Submit booking to API
    bookTicketMutation.mutate({
      eventId: bookingData.eventId,
      quantity: bookingData.tickets[0].quantity,
      customerInfo
    });
  };

  const handleSubmitUTR = (e: React.FormEvent) => {
    e.preventDefault();
    
    // Validate UTR format - should be 10-23 alphanumeric characters
    if (!utr) {
      toast({
        title: "UTR Required",
        description: "Please enter the UTR number from your payment.",
        variant: "destructive"
      });
      return;
    }
    
    // Validate UTR format with regex
    const utrRegex = /^[A-Za-z0-9]{10,23}$/;
    if (!utrRegex.test(utr)) {
      toast({
        title: "Invalid UTR Format",
        description: "UTR should be 10-23 alphanumeric characters. Please check and try again.",
        variant: "destructive"
      });
      return;
    }
    
    if (!bookingId) return;

    // Submit UTR to API
    submitUTRMutation.mutate({
      bookingId,
      utr
    });
  };

  const handlePaymentClick = () => {
    setPaymentCompleted(true);
  };

  const handleBackToPaymentOptions = () => {
    setPaymentCompleted(false);
  };
  
  if (!bookingData) {
    return (
      <div className="flex flex-col min-h-screen">
        <Navbar />
        <main className="flex-grow flex items-center justify-center">
          <div className="text-center">
            <Loader2 className="h-12 w-12 animate-spin text-primary mx-auto mb-4" />
            <p className="text-lg text-gray-600">Loading booking details...</p>
          </div>
        </main>
        <Footer />
      </div>
    );
  }

  // Loading state for payment settings
  const isLoadingPaymentDetails = isLoadingPaymentSettings;

  // Payment section with QR or VPA based on config
  const renderPaymentSection = () => {
    // Generate UPI QR code data for the VPA payment mode
    const generateUpiQrData = () => {
      // Format according to UPI deep link specification
      const upiData = new URLSearchParams({
        pa: paymentSettings.vpaAddress,
        pn: encodeURIComponent(paymentSettings.merchantName),
        am: String(bookingData?.totalAmount),
        tn: encodeURIComponent(`Tickets for ${bookingData?.eventTitle}`),
        cu: "INR"
      });
      
      return `upi://pay?${upiData.toString()}`;
    };

    const paymentAmount = bookingData?.totalAmount || 0;
    
    return (
      <div className="mt-6 p-6 bg-white rounded-lg border">
        <h2 className="text-xl font-semibold mb-4">Complete Payment</h2>
        
        <div className="flex flex-col md:flex-row md:space-x-6">
          {/* QR Code Section */}
          <div className="flex-1 flex flex-col items-center justify-center p-4 border rounded-lg bg-gray-50">
            <p className="text-center mb-4 font-medium">Scan to pay ₹{paymentAmount.toFixed(2)}</p>
            
            {paymentSettings.paymentMode === 'qr_image' && paymentSettings.qrImageUrl && !paymentSettings.qrImageUrl.includes('placeholder') ? (
              // Show the custom QR image uploaded by admin
              <div className="w-40 sm:w-56 md:w-64 relative mb-4">
                <img 
                  src={paymentSettings.qrImageUrl.startsWith('http') 
                    ? paymentSettings.qrImageUrl 
                    : `${config().API_BASE_URL.replace('/api', '')}${paymentSettings.qrImageUrl}`} 
                  alt="Payment QR Code" 
                  className="w-full h-auto object-contain"
                />
              </div>
            ) : (
              // Generate dynamic QR code for the VPA
              <div className="w-40 sm:w-56 md:w-64 mb-4">
                <QRCodeSVG 
                  value={generateUpiQrData()}
                  size={200}
                  level="H"
                  className="w-full h-auto"
                />
              </div>
            )}
            
            <div className="text-center mt-2">
              <p className="text-sm font-medium">Use your UPI app to scan this QR code</p>
              <p className="text-xs text-gray-500">
                You can also take a screenshot of this QR code and upload it in your UPI app to complete payment.
              </p>
            </div>
          </div>
          
          {/* Payment Instructions */}
          <div className="flex-1 mt-6 md:mt-0">
            <h3 className="font-medium mb-3">Payment Instructions:</h3>
            <ol className="list-decimal pl-5 space-y-2 text-sm">
              <li>Open any UPI app on your phone (PhonePe, Google Pay, Paytm, etc.)</li>
              <li>Scan the QR code or use the UPI ID to make payment</li>
              <li>Amount to pay: <span className="font-medium">₹{paymentAmount.toFixed(2)}</span></li>
              <li>After payment is complete, enter the UTR/Reference number below</li>
            </ol>
            
            <form onSubmit={handleSubmitUTR} className="mt-6">
              <div className="mb-4">
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  UTR/Reference Number <span className="text-red-500">*</span>
                </label>
                <Input
                  type="text"
                  value={utr}
                  onChange={(e) => setUtr(e.target.value)}
                  placeholder="Enter UTR from your payment app"
                  required
                />
                <p className="text-xs text-gray-500 mt-1">
                  You can find this number in the transaction details of your payment app
                </p>
              </div>
              
              <Button type="submit" className="w-full" disabled={submitUTRMutation.isPending}>
                {submitUTRMutation.isPending ? (
                  <><Loader2 className="h-4 w-4 animate-spin mr-2" /> Verifying...</>
                ) : (
                  'Verify Payment'
                )}
              </Button>
            </form>
          </div>
        </div>
      </div>
    );
  };
  
  return (
    <div className="flex flex-col min-h-screen">
      <Navbar />
      <main className="flex-grow bg-gray-50 pt-16 pb-12">
        <div className="container mx-auto px-4 max-w-3xl">
          <Button variant="ghost" onClick={() => navigate(-1)} className="mb-4">
            <ArrowLeft className="h-4 w-4 mr-2" />
            Back
          </Button>
          
          <Card>
            <CardHeader>
              <CardTitle>Checkout</CardTitle>
              {step === 1 && <CardDescription>Step 1: Your Details</CardDescription>}
              {step === 2 && <CardDescription>Step 2: Payment</CardDescription>}
              {step === 3 && <CardDescription>Your Ticket</CardDescription>}
            </CardHeader>
            <CardContent>
              <div className="mb-6">
                <h3 className="text-lg font-semibold mb-2">Order Summary</h3>
                <div className="bg-gray-50 p-4 rounded-md">
                  <div className="font-medium text-lg mb-2">{bookingData.eventTitle}</div>
                  
                  {/* Show team badges if it's a match */}
                  {bookingData.teams && (
                    <div className="flex items-center gap-2 mb-3">
                      <TeamBadge 
                        team={bookingData.teams.team1.shortName} 
                        color={bookingData.teams.team1.color}
                      />
                      <span className="text-gray-500">vs</span>
                      <TeamBadge 
                        team={bookingData.teams.team2.shortName}
                        color={bookingData.teams.team2.color}
                      />
                    </div>
                  )}
                  
                  {/* Event details */}
                  {(formattedDate || bookingData.eventTime || bookingData.eventVenue) && (
                    <div className="mb-3 text-sm space-y-1">
                      {formattedDate && (
                        <div className="flex items-center text-gray-600">
                          <Calendar className="h-3 w-3 mr-2" />
                          {formattedDate}
                        </div>
                      )}
                      {bookingData.eventTime && (
                        <div className="flex items-center text-gray-600">
                          <Clock className="h-3 w-3 mr-2" />
                          {bookingData.eventTime}
                        </div>
                      )}
                      {bookingData.eventVenue && (
                        <div className="flex items-center text-gray-600">
                          <MapPin className="h-3 w-3 mr-2" />
                          {bookingData.eventVenue}
                        </div>
                      )}
                </div>
                  )}
                  
                  {/* Ticket summary */}
                  <div className="border-t border-gray-200 pt-3 mt-3">
                    <div className="text-sm font-medium mb-2">Tickets:</div>
                    {bookingData.tickets.map((ticket: TicketInfo, index: number) => (
                      <div key={index} className="flex justify-between my-2">
                        <span>{ticket.quantity} x {ticket.category}</span>
                        <span>₹{ticket.subtotal}</span>
                      </div>
                    ))}
                    <Separator className="my-2" />
                    <div className="flex justify-between font-medium">
                      <span>Total</span>
                      <span>₹{bookingData.totalAmount}</span>
                    </div>
                  </div>
                </div>
              </div>
              
              {step === 1 && (
                <form onSubmit={handleSubmitCustomerInfo}>
                  <div className="space-y-4">
                    <h3 className="text-lg font-semibold">Your Information</h3>
                    
                  <div>
                      <Label htmlFor="name">Full Name *</Label>
                    <Input 
                      id="name" 
                      placeholder="Enter your full name"
                        value={customerInfo.name}
                        onChange={(e) => setCustomerInfo({...customerInfo, name: e.target.value})}
                        required
                    />
                  </div>
                  
                  <div>
                      <Label htmlFor="email">Email *</Label>
                    <Input 
                      id="email" 
                      type="email" 
                      placeholder="Enter your email"
                        value={customerInfo.email}
                        onChange={(e) => setCustomerInfo({...customerInfo, email: e.target.value})}
                        required
                    />
                  </div>
                  
                  <div>
                      <Label htmlFor="phone">Phone Number *</Label>
                    <Input 
                      id="phone" 
                      placeholder="Enter your phone number"
                        value={customerInfo.phone}
                        onChange={(e) => setCustomerInfo({...customerInfo, phone: e.target.value})}
                        required
                    />
                  </div>
                  
                  <div>
                      <Label htmlFor="address">Address *</Label>
                    <Input 
                      id="address" 
                        placeholder="Enter your address"
                        value={customerInfo.address}
                        onChange={(e) => setCustomerInfo({...customerInfo, address: e.target.value})}
                        required
                      />
                    </div>
                    
                    <div>
                      <Label htmlFor="city">City *</Label>
                      <Input 
                        id="city"
                        placeholder="Enter your city"
                        value={customerInfo.city}
                        onChange={(e) => setCustomerInfo({...customerInfo, city: e.target.value})}
                        required
                      />
                    </div>
                    
                    <div>
                      <Label htmlFor="state">State *</Label>
                      <Input
                        id="state"
                        placeholder="Enter your state"
                        value={customerInfo.state}
                        onChange={(e) => setCustomerInfo({...customerInfo, state: e.target.value})}
                        required
                      />
                    </div>
                    
                    <div>
                      <Label htmlFor="pincode">Pincode *</Label>
                      <Input
                        id="pincode"
                        placeholder="Enter your pincode"
                        value={customerInfo.pincode}
                        onChange={(e) => setCustomerInfo({...customerInfo, pincode: e.target.value})}
                        required
                      />
                    </div>
                  </div>

                  <Button
                    type="submit"
                    className="mt-6 w-full"
                    disabled={bookTicketMutation.isPending}
                  >
                    {bookTicketMutation.isPending ? (
                      <>
                        <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                        Processing...
                      </>
                    ) : (
                      <>
                        Continue to Payment
                        <ArrowRight className="ml-2 h-4 w-4" />
                      </>
                    )}
                  </Button>
                </form>
              )}

              {step === 2 && (
                <div>
                  <h3 className="text-lg font-semibold mb-4">Payment</h3>
                  
                  {/* Display countdown timer when booking is created */}
                  {bookingCreatedTime && (
                    <PaymentCountdown startTime={bookingCreatedTime} />
                  )}
                  
                  {!paymentCompleted ? (
                    renderPaymentSection()
                  ) :
                    <form onSubmit={handleSubmitUTR}>
                      <div className="space-y-4">
                        <p>Please enter the UTR (Unique Transaction Reference) number from your payment:</p>
                        <div>
                          <Label htmlFor="utr">UTR Number</Label>
                          <Input
                            id="utr"
                            placeholder="Enter UTR number"
                            value={utr}
                            onChange={(e) => setUtr(e.target.value)}
                            pattern="^[A-Za-z0-9]{10,23}$"
                            title="UTR should be 10-23 alphanumeric characters"
                            required
                          />
                          <p className="text-xs text-gray-500 mt-1">
                            You can find the UTR number in your payment app's transaction history or SMS confirmation
                          </p>
                        </div>
                        <div className="flex gap-2">
                      <Button 
                            type="button"
                        variant="outline" 
                            onClick={handleBackToPaymentOptions}
                      >
                        Back to Payment Options
                      </Button>
                          <Button
                            type="submit"
                            className="flex-1"
                            disabled={submitUTRMutation.isPending}
                          >
                            {submitUTRMutation.isPending ? (
                              <>
                                <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                                Verifying...
                              </>
                            ) : (
                              "Complete Order"
                            )}
                          </Button>
                        </div>
                      </div>
                    </form>
                  }
                    </div>
              )}

              {step === 3 && ticketQRData && (
                <div className="text-center">
                  <h3 className="text-lg font-semibold mb-4">Your Ticket</h3>
                  <div className="bg-white p-4 rounded-md shadow-md inline-block mx-auto">
                    <QRCodeSVG value={ticketQRData} size={200} />
                  </div>
                  <div className="mt-4">
                    <p className="font-medium">Booking ID: {bookingId}</p>
                    <p className="text-gray-600">Show this QR code at the venue entrance</p>
              </div>
                  <Button className="mt-6" onClick={() => window.print()}>
                    Print Ticket
                  </Button>
            </div>
              )}
            </CardContent>
          </Card>
        </div>
      </main>
      <Footer />
    </div>
  );
};

export default Checkout;
