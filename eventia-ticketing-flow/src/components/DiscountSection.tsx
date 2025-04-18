// DiscountSection.tsx
import React, { useState } from 'react';
import { Button, Input, Alert, Spinner } from '../ui';
import { useToast } from '../hooks/useToast';
import { api } from '../lib/api';

interface DiscountSectionProps {
  eventId: string;
  tickets: Array<{
    ticketTypeId: string;
    quantity: number;
  }>;
  onDiscountApplied: (discountData: {
    discountCode: string;
    discountAmount: number;
    subtotal: number;
    total: number;
    isValid: boolean;
    message: string;
  }) => void;
}

export function DiscountSection({ eventId, tickets, onDiscountApplied }: DiscountSectionProps) {
  const [discountCode, setDiscountCode] = useState('');
  const [isApplying, setIsApplying] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);
  const { showToast } = useToast();

  const applyDiscount = async () => {
    if (!discountCode.trim()) {
      setError('Please enter a discount code');
      return;
    }

    if (tickets.length === 0 || tickets.every(t => t.quantity === 0)) {
      setError('Please select at least one ticket before applying a discount');
      return;
    }

    setIsApplying(true);
    setError(null);
    setSuccess(null);

    try {
      const response = await api.post('/bookings/calculate', {
        event_id: eventId,
        tickets: tickets.map(t => ({
          ticket_type_id: t.ticketTypeId,
          quantity: t.quantity
        })),
        discount_code: discountCode
      });

      const { data, success } = response.data;

      if (success && data.discount_valid) {
        setSuccess(`Discount applied: ₹${data.discount_amount.toFixed(2)} off`);
        showToast({
          title: 'Discount applied!',
          description: `Saved ₹${data.discount_amount.toFixed(2)}`,
          type: 'success'
        });

        onDiscountApplied({
          discountCode,
          discountAmount: data.discount_amount,
          subtotal: data.subtotal,
          total: data.total,
          isValid: true,
          message: `Discount applied: ₹${data.discount_amount.toFixed(2)} off`
        });
      } else {
        // Even if API returns 200, the discount might be invalid
        setError(data.discount_message || 'Invalid discount code');
        onDiscountApplied({
          discountCode,
          discountAmount: 0,
          subtotal: data.subtotal,
          total: data.subtotal,
          isValid: false,
          message: data.discount_message || 'Invalid discount code'
        });
      }
    } catch (err) {
      console.error('Error applying discount:', err);
      setError('Error applying discount. Please try again.');
      onDiscountApplied({
        discountCode,
        discountAmount: 0,
        subtotal: 0,
        total: 0,
        isValid: false,
        message: 'Error applying discount'
      });
    } finally {
      setIsApplying(false);
    }
  };

  const resetDiscount = () => {
    setDiscountCode('');
    setError(null);
    setSuccess(null);
    onDiscountApplied({
      discountCode: '',
      discountAmount: 0,
      subtotal: 0,
      total: 0,
      isValid: false,
      message: ''
    });
  };

  // Handle pressing Enter key in the input field
  const handleKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === 'Enter' && !isApplying && discountCode.trim() && !success) {
      e.preventDefault();
      applyDiscount();
    }
  };

  return (
    <div className="mt-4 p-4 border border-gray-200 rounded-md">
      <h3 className="text-lg font-medium mb-2">Apply Discount</h3>
      
      <div className="flex gap-2">
        <Input
          type="text"
          placeholder="Enter discount code"
          value={discountCode}
          onChange={(e) => setDiscountCode(e.target.value.toUpperCase())}
          onKeyDown={handleKeyDown}
          className="flex-1"
          disabled={isApplying || !!success}
          aria-label="Discount code"
        />
        
        {!success ? (
          <Button 
            onClick={applyDiscount} 
            disabled={isApplying || !discountCode.trim()}
            className="whitespace-nowrap"
            aria-label="Apply discount code"
          >
            {isApplying ? <Spinner size="sm" className="mr-2" /> : null}
            Apply
          </Button>
        ) : (
          <Button 
            onClick={resetDiscount} 
            variant="outline"
            className="whitespace-nowrap"
            aria-label="Remove discount code"
          >
            Remove
          </Button>
        )}
      </div>
      
      {error && (
        <Alert variant="destructive" className="mt-2">
          {error}
        </Alert>
      )}
      
      {success && (
        <Alert variant="success" className="mt-2">
          {success}
        </Alert>
      )}
      
      <p className="text-xs text-gray-500 mt-2">
        Enter a valid discount code to get special offers on your booking
      </p>
    </div>
  );
}
