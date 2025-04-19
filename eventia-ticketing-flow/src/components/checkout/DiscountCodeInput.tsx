import React, { useState } from 'react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { toast } from '@/hooks/use-toast';
import { Loader2, X, CheckCircle } from 'lucide-react';
import { api } from '@/lib/api';

interface DiscountCodeInputProps {
  eventId: string;
  ticketQuantity: number;
  originalAmount: number;
  onDiscountApplied: (code: string, amount: number) => void;
  onDiscountRemoved: () => void;
}

export const DiscountCodeInput: React.FC<DiscountCodeInputProps> = ({
  eventId,
  ticketQuantity,
  originalAmount,
  onDiscountApplied,
  onDiscountRemoved
}) => {
  const [code, setCode] = useState('');
  const [loading, setLoading] = useState(false);
  const [applied, setApplied] = useState(false);
  const [discountAmount, setDiscountAmount] = useState(0);

  const handleApplyDiscount = async () => {
    if (!code.trim()) {
      toast({
        title: "Error",
        description: "Please enter a discount code",
        variant: "destructive"
      });
      return;
    }

    try {
      setLoading(true);
      
      // Call API to validate discount code
      const response = await api.post('/discounts/validate', {
        event_id: eventId,
        discount_code: code,
        amount: originalAmount
      });
      
      if (response.data.valid) {
        setApplied(true);
        setDiscountAmount(response.data.discount_amount);
        onDiscountApplied(code, response.data.discount_amount);
        
        toast({
          title: "Success!",
          description: `Discount code applied: ${response.data.discount_amount} off`,
        });
      } else {
        toast({
          title: "Invalid code",
          description: response.data.message || "This discount code is not valid for this event",
          variant: "destructive"
        });
      }
    } catch (error) {
      console.error('Error validating discount code:', error);
      toast({
        title: "Error",
        description: "Failed to validate discount code. Please try again.",
        variant: "destructive"
      });
    } finally {
      setLoading(false);
    }
  };

  const handleRemoveDiscount = () => {
    setApplied(false);
    setCode('');
    setDiscountAmount(0);
    onDiscountRemoved();
  };

  if (applied) {
    return (
      <div className="flex items-center justify-between p-2 bg-green-50 border border-green-200 rounded-md mb-4">
        <div className="flex items-center">
          <CheckCircle className="h-4 w-4 text-green-500 mr-2" />
          <div>
            <p className="text-sm font-medium">Code applied: {code}</p>
            <p className="text-xs text-green-700">Discount: ₹{discountAmount.toFixed(2)}</p>
          </div>
        </div>
        <Button 
          variant="ghost" 
          size="sm"
          onClick={handleRemoveDiscount}
          className="h-8 text-red-500 hover:text-red-700 hover:bg-red-50"
        >
          <X className="h-4 w-4" />
        </Button>
      </div>
    );
  }

  return (
    <div className="flex items-end gap-2 mb-4">
      <div className="flex-1">
        <p className="text-sm font-medium mb-2">Discount Code</p>
        <Input
          placeholder="Enter discount code"
          value={code}
          onChange={(e) => setCode(e.target.value)}
          className="h-9"
        />
      </div>
      <Button
        onClick={handleApplyDiscount}
        disabled={loading || !code.trim()}
        className="h-9 whitespace-nowrap"
        variant="secondary"
      >
        {loading ? (
          <>
            <Loader2 className="mr-2 h-4 w-4 animate-spin" />
            Validating...
          </>
        ) : (
          'Apply Code'
        )}
      </Button>
    </div>
  );
}; 