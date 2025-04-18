import React, { useState, useEffect } from 'react';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogFooter } from '@/components/ui/dialog';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { 
  Select, 
  SelectContent, 
  SelectItem, 
  SelectTrigger, 
  SelectValue 
} from '@/components/ui/select';
import { Checkbox } from '@/components/ui/checkbox';
import { RadioGroup, RadioGroupItem } from '@/components/ui/radio-group';
import { Loader2 } from 'lucide-react';
import { toast } from '@/hooks/use-toast';

interface Event {
  _id: string;
  title: string;
  date: string;
}

interface Discount {
  _id?: string;
  discount_code: string;
  discount_type: 'percentage' | 'fixed';
  value: number;
  applicable_events: string[];
  valid_from: string;
  valid_till: string;
  max_uses: number;
  active: boolean;
  used_count?: number;
}

interface DiscountFormProps {
  isOpen: boolean;
  onClose: () => void;
  onSubmit: (discount: any) => void;
  discount?: any | null;
  events: Event[];
  isLoading: boolean;
}

const DiscountForm: React.FC<DiscountFormProps> = ({
  isOpen,
  onClose,
  onSubmit,
  discount = null,
  events = [],
  isLoading
}) => {
  const isEditing = !!discount;
  
  // Format date string to datetime-local input format
  const formatDateForInput = (dateStr: string): string => {
    if (!dateStr) return '';
    try {
      const date = new Date(dateStr);
      return date.toISOString().slice(0, 16);
    } catch (e) {
      return '';
    }
  };

  // Initialize form state
  const [formData, setFormData] = useState<Partial<Discount>>({
    discount_code: '',
    discount_type: 'percentage',
    value: 10,
    applicable_events: [],
    valid_from: formatDateForInput(new Date().toISOString()),
    valid_till: formatDateForInput(new Date(Date.now() + 30 * 24 * 60 * 60 * 1000).toISOString()),
    max_uses: 100,
    active: true
  });

  // Set form data when editing an existing discount
  useEffect(() => {
    if (discount) {
      setFormData({
        ...discount,
        valid_from: formatDateForInput(discount.valid_from),
        valid_till: formatDateForInput(discount.valid_till)
      });
    }
  }, [discount]);

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value, type } = e.target;
    
    if (type === 'number') {
      setFormData({
        ...formData,
        [name]: parseFloat(value)
      });
    } else {
      setFormData({
        ...formData,
        [name]: value
      });
    }
  };

  const handleSelectChange = (name: string, value: string) => {
    setFormData({
      ...formData,
      [name]: value
    });
  };

  const handleCheckboxChange = (name: string, checked: boolean) => {
    setFormData({
      ...formData,
      [name]: checked
    });
  };

  const handleEventSelection = (eventId: string, checked: boolean) => {
    let updatedEvents = [...(formData.applicable_events || [])];
    
    if (checked) {
      updatedEvents.push(eventId);
    } else {
      updatedEvents = updatedEvents.filter(id => id !== eventId);
    }
    
    setFormData({
      ...formData,
      applicable_events: updatedEvents
    });
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    
    // Validation
    if (!formData.discount_code || formData.discount_code.length !== 6) {
      toast({
        title: "Validation Error",
        description: "Discount code must be exactly 6 characters",
        variant: "destructive"
      });
      return;
    }
    
    if (!formData.value || formData.value <= 0) {
      toast({
        title: "Validation Error",
        description: "Discount value must be greater than 0",
        variant: "destructive"
      });
      return;
    }
    
    if (formData.discount_type === 'percentage' && formData.value > 100) {
      toast({
        title: "Validation Error",
        description: "Percentage discount cannot exceed 100%",
        variant: "destructive"
      });
      return;
    }
    
    // Format dates for API
    const formatDateForApi = (dateStr: string): string => {
      try {
        const date = new Date(dateStr);
        return date.toISOString().replace('T', ' ').substring(0, 19);
      } catch (e) {
        return '';
      }
    };
    
    const submissionData = {
      ...formData,
      discount_code: formData.discount_code?.toUpperCase(),
      valid_from: formatDateForApi(formData.valid_from || ''),
      valid_till: formatDateForApi(formData.valid_till || '')
    };
    
    onSubmit(submissionData);
  };

  return (
    <Dialog open={isOpen} onOpenChange={onClose}>
      <DialogContent className="sm:max-w-[600px]">
        <DialogHeader>
          <DialogTitle>{isEditing ? 'Edit Discount' : 'Create New Discount'}</DialogTitle>
        </DialogHeader>
        
        <form onSubmit={handleSubmit} className="space-y-6 py-4">
          <div className="grid grid-cols-2 gap-4">
            <div className="space-y-2">
              <Label htmlFor="discount_code">Discount Code</Label>
              <Input
                id="discount_code"
                name="discount_code"
                value={formData.discount_code || ''}
                onChange={handleChange}
                className="uppercase"
                maxLength={6}
                required
                disabled={isEditing}
                placeholder="e.g. IPL100"
              />
              <p className="text-xs text-gray-500">6 characters, uppercase letters and numbers only</p>
            </div>
            
            <div className="space-y-2">
              <Label>Discount Type</Label>
              <RadioGroup 
                value={formData.discount_type}
                onValueChange={(value) => handleSelectChange('discount_type', value)}
                className="flex space-x-4"
              >
                <div className="flex items-center space-x-2">
                  <RadioGroupItem value="percentage" id="percentage" />
                  <Label htmlFor="percentage">Percentage (%)</Label>
                </div>
                <div className="flex items-center space-x-2">
                  <RadioGroupItem value="fixed" id="fixed" />
                  <Label htmlFor="fixed">Fixed Amount (₹)</Label>
                </div>
              </RadioGroup>
            </div>
          </div>
          
          <div className="grid grid-cols-2 gap-4">
            <div className="space-y-2">
              <Label htmlFor="value">
                {formData.discount_type === 'percentage' ? 'Percentage Value (%)' : 'Fixed Amount (₹)'}
              </Label>
              <Input
                id="value"
                name="value"
                type="number"
                value={formData.value || ''}
                onChange={handleChange}
                min={0}
                max={formData.discount_type === 'percentage' ? 100 : undefined}
                required
              />
            </div>
            
            <div className="space-y-2">
              <Label htmlFor="max_uses">Maximum Uses</Label>
              <Input
                id="max_uses"
                name="max_uses"
                type="number"
                value={formData.max_uses || ''}
                onChange={handleChange}
                min={1}
                required
              />
            </div>
          </div>
          
          <div className="grid grid-cols-2 gap-4">
            <div className="space-y-2">
              <Label htmlFor="valid_from">Valid From</Label>
              <Input
                id="valid_from"
                name="valid_from"
                type="datetime-local"
                value={formData.valid_from || ''}
                onChange={handleChange}
                required
              />
            </div>
            
            <div className="space-y-2">
              <Label htmlFor="valid_till">Valid Till</Label>
              <Input
                id="valid_till"
                name="valid_till"
                type="datetime-local"
                value={formData.valid_till || ''}
                onChange={handleChange}
                required
              />
            </div>
          </div>
          
          <div className="space-y-2">
            <div className="flex items-center justify-between">
              <Label>Applicable Events</Label>
              <div className="flex items-center space-x-2">
                <Checkbox 
                  id="select-all-events"
                  checked={events.length > 0 && formData.applicable_events?.length === events.length}
                  onCheckedChange={(checked) => {
                    if (checked) {
                      setFormData({
                        ...formData,
                        applicable_events: events.map(e => e._id)
                      });
                    } else {
                      setFormData({
                        ...formData,
                        applicable_events: []
                      });
                    }
                  }}
                />
                <Label htmlFor="select-all-events" className="text-sm">Select All</Label>
              </div>
            </div>
            
            <div className="border rounded-md p-3 max-h-[200px] overflow-y-auto">
              {events.length === 0 ? (
                <p className="text-gray-500 text-sm">No events available</p>
              ) : (
                <div className="space-y-2">
                  {events.map(event => (
                    <div key={event._id} className="flex items-center space-x-2">
                      <Checkbox 
                        id={`event-${event._id}`}
                        checked={formData.applicable_events?.includes(event._id)}
                        onCheckedChange={(checked) => 
                          handleEventSelection(event._id, checked === true)
                        }
                      />
                      <Label htmlFor={`event-${event._id}`} className="text-sm">
                        {event.title} ({new Date(event.date).toLocaleDateString()})
                      </Label>
                    </div>
                  ))}
                </div>
              )}
            </div>
            <p className="text-xs text-gray-500">
              Leave empty to apply to all events
            </p>
          </div>
          
          <div className="flex items-center space-x-2">
            <Checkbox 
              id="active"
              checked={formData.active === true}
              onCheckedChange={(checked) => 
                handleCheckboxChange('active', checked === true)
              }
            />
            <Label htmlFor="active">Active</Label>
          </div>
          
          {isEditing && (
            <div className="text-sm text-gray-500">
              <p>Used: {discount.used_count || 0} times</p>
              <p>Created: {new Date(discount.created_at).toLocaleString()}</p>
              {discount.updated_at && (
                <p>Last Updated: {new Date(discount.updated_at).toLocaleString()}</p>
              )}
            </div>
          )}
          
          <DialogFooter>
            <Button type="button" variant="outline" onClick={onClose}>
              Cancel
            </Button>
            <Button type="submit" disabled={isLoading}>
              {isLoading ? (
                <>
                  <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                  {isEditing ? 'Updating...' : 'Creating...'}
                </>
              ) : (
                isEditing ? 'Update Discount' : 'Create Discount'
              )}
            </Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  );
};

export default DiscountForm; 