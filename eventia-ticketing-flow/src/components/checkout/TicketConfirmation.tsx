import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Separator } from '@/components/ui/separator';
import { Clock, CreditCard, Ticket, User, AlertCircle } from 'lucide-react';
import { toast } from '@/hooks/use-toast';

interface TicketItem {
  section_id: string;
  name: string;
  quantity: number;
  price: number;
  subtotal: number;
}

interface TicketConfirmationProps {
  eventTitle: string;
  eventDate: string;
  eventVenue: string;
  stadiumName: string;
  tickets: TicketItem[];
  totalAmount: number;
  onProceed: () => void;
  onCancel: () => void;
}

const TicketConfirmation: React.FC<TicketConfirmationProps> = ({
  eventTitle,
  eventDate,
  eventVenue,
  stadiumName,
  tickets,
  totalAmount,
  onProceed,
  onCancel
}) => {
  const [isLoading, setIsLoading] = useState(false);
  const navigate = useNavigate();
  
  // BookMyShow-style countdown timer for checkout
  const [timeRemaining, setTimeRemaining] = useState<number>(600); // 10 minutes
  
  // Format time as MM:SS
  const formatTime = (seconds: number) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}:${secs < 10 ? '0' : ''}${secs}`;
  };
  
  // Calculate total tickets
  const totalTickets = tickets.reduce((sum, ticket) => sum + ticket.quantity, 0);
  
  // Handle payment
  const handleProceedToPayment = () => {
    setIsLoading(true);
    setTimeout(() => {
      setIsLoading(false);
      onProceed();
    }, 1500);
  };
  
  return (
    <div className="max-w-3xl mx-auto space-y-6">
      {/* Timer bar */}
      <div className="bg-red-600 text-white p-3 rounded-md flex items-center justify-between">
        <div className="flex items-center">
          <Clock className="mr-2 h-5 w-5" />
          <span>Time left to complete your booking:</span>
        </div>
        <div className="font-bold text-xl">{formatTime(timeRemaining)}</div>
      </div>
      
      {/* Event info */}
      <Card>
        <CardHeader>
          <CardTitle className="text-xl">{eventTitle}</CardTitle>
          <CardDescription className="flex flex-col gap-1">
            <span>{eventDate}</span>
            <span>{eventVenue}</span>
            <span>{stadiumName}</span>
          </CardDescription>
        </CardHeader>
      </Card>
      
      {/* Ticket summary */}
      <Card>
        <CardHeader>
          <CardTitle className="text-lg flex items-center">
            <Ticket className="mr-2 h-5 w-5" />
            Ticket Summary
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          {tickets.map((ticket, index) => (
            <div key={index} className="flex justify-between items-center">
              <div>
                <div className="font-medium">{ticket.name}</div>
                <div className="text-sm text-gray-500">₹{ticket.price.toLocaleString()} x {ticket.quantity}</div>
              </div>
              <div className="font-bold">₹{ticket.subtotal.toLocaleString()}</div>
            </div>
          ))}
          
          <Separator />
          
          <div className="flex justify-between items-center font-medium">
            <span>Convenience Fee:</span>
            <span>₹{Math.round(totalAmount * 0.03).toLocaleString()}</span>
          </div>
          
          <div className="flex justify-between items-center text-lg font-bold">
            <span>Amount Payable:</span>
            <span>₹{(totalAmount + Math.round(totalAmount * 0.03)).toLocaleString()}</span>
          </div>
        </CardContent>
      </Card>
      
      {/* Important notes */}
      <Card className="bg-yellow-50 border-yellow-200">
        <CardContent className="pt-4">
          <div className="flex">
            <AlertCircle className="h-5 w-5 text-yellow-600 mr-2 flex-shrink-0 mt-0.5" />
            <div className="space-y-2">
              <h3 className="font-medium text-yellow-800">Important Information</h3>
              <ul className="text-sm text-yellow-700 space-y-1 list-disc pl-5">
                <li>Tickets once booked cannot be exchanged or refunded</li>
                <li>To be admitted, carry a valid ID proof along with your ticket</li>
                <li>Entry for children above the age of 3 requires a separate ticket</li>
                <li>Venue rules prohibit carrying outside food and beverages</li>
              </ul>
            </div>
          </div>
        </CardContent>
      </Card>
      
      {/* Action buttons */}
      <div className="flex flex-col md:flex-row gap-4 justify-between items-center bg-white p-4 rounded-lg shadow-md">
        <div>
          <div className="text-sm text-gray-500">Total: {totalTickets} Tickets</div>
          <div className="text-xl font-bold">₹{(totalAmount + Math.round(totalAmount * 0.03)).toLocaleString()}</div>
        </div>
        
        <div className="flex gap-3">
          <Button variant="outline" onClick={onCancel}>
            Cancel
          </Button>
          <Button onClick={handleProceedToPayment} disabled={isLoading}>
            {isLoading ? (
              <span className="flex items-center">
                <svg className="animate-spin -ml-1 mr-2 h-4 w-4 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                  <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                  <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                </svg>
                Processing...
              </span>
            ) : (
              <span className="flex items-center">
                <CreditCard className="mr-2 h-4 w-4" />
                Proceed to Payment
              </span>
            )}
          </Button>
        </div>
      </div>
    </div>
  );
};

export default TicketConfirmation; 