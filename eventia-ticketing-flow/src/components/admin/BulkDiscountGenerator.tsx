import React, { useState } from 'react';
import { 
  Card, 
  CardContent, 
  CardDescription, 
  CardHeader, 
  CardTitle,
  CardFooter 
} from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { RadioGroup, RadioGroupItem } from '@/components/ui/radio-group';
import { Slider } from '@/components/ui/slider';
import { 
  Select, 
  SelectContent, 
  SelectItem, 
  SelectTrigger, 
  SelectValue 
} from '@/components/ui/select';
import { Checkbox } from '@/components/ui/checkbox';
import { toast } from '@/hooks/use-toast';
import { Loader2, Tag, RefreshCw, Copy } from 'lucide-react';

interface Event {
  _id: string;
  title: string;
  date: string;
}

interface BulkDiscountGeneratorProps {
  events: Event[];
  onGenerate: (data: any) => void;
  isLoading: boolean;
}

const BulkDiscountGenerator: React.FC<BulkDiscountGeneratorProps> = ({
  events = [],
  onGenerate,
  isLoading = false
}) => {
  const [formData, setFormData] = useState({
    count: 10,
    prefix: '',
    discount_type: 'percentage',
    value: 10,
    applicable_events: [] as string[],
    valid_from: new Date().toISOString().slice(0, 16),
    valid_till: new Date(Date.now() + 30 * 24 * 60 * 60 * 1000).toISOString().slice(0, 16),
    max_uses: 1,
    active: true
  });
  
  const [previewCode, setPreviewCode] = useState('');
  
  // Generate a preview code based on the prefix
  const generatePreview = () => {
    const prefix = formData.prefix.toUpperCase();
    if (prefix.length >= 6) {
      return prefix.substring(0, 6);
    }
    
    const chars = 'ABCDEFGHJKLMNPQRSTUVWXYZ23456789'; // Removed confusing chars like I,O,0,1
    let result = prefix;
    for (let i = 0; i < 6 - prefix.length; i++) {
      result += chars.charAt(Math.floor(Math.random() * chars.length));
    }
    return result;
  };
  
  // Update preview code when prefix changes
  React.useEffect(() => {
    setPreviewCode(generatePreview());
  }, [formData.prefix]);
  
  // Handle form field changes
  const handleChange = (field: string, value: any) => {
    setFormData(prev => ({
      ...prev,
      [field]: value
    }));
  };
  
  // Handle checkbox selection for applicable events
  const handleEventSelection = (eventId: string, checked: boolean) => {
    let updatedEvents = [...formData.applicable_events];
    
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
  
  // Form submission
  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    
    // Validation
    if (formData.prefix && !/^[A-Za-z0-9]+$/.test(formData.prefix)) {
      toast({
        title: "Invalid prefix",
        description: "Prefix can only contain letters and numbers",
        variant: "destructive"
      });
      return;
    }
    
    if (formData.prefix.length >= 6) {
      toast({
        title: "Prefix too long",
        description: "Prefix must be shorter than 6 characters",
        variant: "destructive"
      });
      return;
    }
    
    if (formData.count <= 0 || formData.count > 100) {
      toast({
        title: "Invalid count",
        description: "Count must be between 1 and 100",
        variant: "destructive"
      });
      return;
    }
    
    if (formData.value <= 0 || (formData.discount_type === 'percentage' && formData.value > 100)) {
      toast({
        title: "Invalid discount value",
        description: formData.discount_type === 'percentage' 
          ? "Percentage must be between 1 and 100" 
          : "Amount must be greater than 0",
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
      prefix: formData.prefix.toUpperCase(),
      valid_from: formatDateForApi(formData.valid_from),
      valid_till: formatDateForApi(formData.valid_till)
    };
    
    onGenerate(submissionData);
  };
  
  // Regenerate preview code
  const refreshPreviewCode = () => {
    setPreviewCode(generatePreview());
  };
  
  // Copy preview code to clipboard
  const copyPreviewCode = () => {
    navigator.clipboard.writeText(previewCode)
      .then(() => {
        toast({
          title: "Copied!",
          description: "Sample code copied to clipboard"
        });
      })
      .catch(() => {
        toast({
          title: "Failed to copy",
          description: "Please copy the code manually",
          variant: "destructive"
        });
      });
  };

  return (
    <Card>
      <CardHeader>
        <CardTitle>Bulk Discount Generator</CardTitle>
        <CardDescription>
          Generate multiple discount codes at once
        </CardDescription>
      </CardHeader>
      <CardContent>
        <form onSubmit={handleSubmit} className="space-y-6">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div className="space-y-4">
              <div>
                <Label>Discount Count</Label>
                <div className="flex items-center space-x-2 mt-1">
                  <Slider
                    defaultValue={[10]}
                    max={100}
                    min={1}
                    step={1}
                    value={[formData.count]}
                    onValueChange={(value) => handleChange('count', value[0])}
                  />
                  <Input
                    type="number"
                    min={1}
                    max={100}
                    value={formData.count}
                    onChange={(e) => handleChange('count', parseInt(e.target.value) || 1)}
                    className="w-20"
                  />
                </div>
                <p className="text-xs text-muted-foreground mt-1">
                  Number of unique codes to generate (max 100)
                </p>
              </div>
              
              <div>
                <Label htmlFor="prefix">Code Prefix</Label>
                <div className="flex space-x-2 mt-1">
                  <Input
                    id="prefix"
                    placeholder="e.g. IPL"
                    value={formData.prefix}
                    onChange={(e) => handleChange('prefix', e.target.value.toUpperCase())}
                    className="uppercase"
                    maxLength={5}
                  />
                  <Button
                    type="button"
                    variant="outline"
                    size="icon"
                    onClick={refreshPreviewCode}
                  >
                    <RefreshCw className="h-4 w-4" />
                  </Button>
                </div>
                <p className="text-xs text-muted-foreground mt-1">
                  Optional: Set a common prefix for all codes (max 5 chars)
                </p>
              </div>
              
              <div className="p-3 border rounded-md bg-gray-50 flex items-center justify-between">
                <div className="flex items-center">
                  <Tag className="h-4 w-4 mr-2 text-muted-foreground" />
                  <div>
                    <div className="text-sm font-medium">Sample Code</div>
                    <div className="font-mono text-lg">{previewCode}</div>
                  </div>
                </div>
                <Button
                  type="button"
                  variant="ghost"
                  size="sm"
                  onClick={copyPreviewCode}
                >
                  <Copy className="h-4 w-4" />
                </Button>
              </div>
              
              <div>
                <Label>Discount Type</Label>
                <RadioGroup 
                  value={formData.discount_type}
                  onValueChange={(value) => handleChange('discount_type', value)}
                  className="flex space-x-4 mt-1"
                >
                  <div className="flex items-center space-x-2">
                    <RadioGroupItem value="percentage" id="bulk-percentage" />
                    <Label htmlFor="bulk-percentage">Percentage (%)</Label>
                  </div>
                  <div className="flex items-center space-x-2">
                    <RadioGroupItem value="fixed" id="bulk-fixed" />
                    <Label htmlFor="bulk-fixed">Fixed Amount (₹)</Label>
                  </div>
                </RadioGroup>
              </div>
              
              <div>
                <Label htmlFor="value">
                  {formData.discount_type === 'percentage' ? 'Percentage Value (%)' : 'Fixed Amount (₹)'}
                </Label>
                <Input
                  id="value"
                  type="number"
                  value={formData.value}
                  onChange={(e) => handleChange('value', parseFloat(e.target.value) || 0)}
                  min={0}
                  max={formData.discount_type === 'percentage' ? 100 : undefined}
                  className="mt-1"
                />
              </div>
            </div>
            
            <div className="space-y-4">
              <div>
                <div className="flex items-center justify-between">
                  <Label>Applicable Events</Label>
                  <div className="flex items-center space-x-2">
                    <Checkbox 
                      id="select-all-events-bulk"
                      checked={events.length > 0 && formData.applicable_events.length === events.length}
                      onCheckedChange={(checked) => {
                        if (checked) {
                          handleChange('applicable_events', events.map(e => e._id));
                        } else {
                          handleChange('applicable_events', []);
                        }
                      }}
                    />
                    <Label htmlFor="select-all-events-bulk" className="text-sm">Select All</Label>
                  </div>
                </div>
                
                <div className="border rounded-md p-3 h-[200px] overflow-y-auto mt-1">
                  {events.length === 0 ? (
                    <p className="text-gray-500 text-sm">No events available</p>
                  ) : (
                    <div className="space-y-2">
                      {events.map(event => (
                        <div key={event._id} className="flex items-center space-x-2">
                          <Checkbox 
                            id={`bulk-event-${event._id}`}
                            checked={formData.applicable_events.includes(event._id)}
                            onCheckedChange={(checked) => 
                              handleEventSelection(event._id, checked === true)
                            }
                          />
                          <Label htmlFor={`bulk-event-${event._id}`} className="text-sm">
                            {event.title} ({new Date(event.date).toLocaleDateString()})
                          </Label>
                        </div>
                      ))}
                    </div>
                  )}
                </div>
                <p className="text-xs text-muted-foreground mt-1">
                  Leave empty to apply to all events
                </p>
              </div>
              
              <div className="grid grid-cols-2 gap-3">
                <div>
                  <Label htmlFor="valid_from">Valid From</Label>
                  <Input
                    id="valid_from"
                    type="datetime-local"
                    value={formData.valid_from}
                    onChange={(e) => handleChange('valid_from', e.target.value)}
                    className="mt-1"
                  />
                </div>
                
                <div>
                  <Label htmlFor="valid_till">Valid Till</Label>
                  <Input
                    id="valid_till"
                    type="datetime-local"
                    value={formData.valid_till}
                    onChange={(e) => handleChange('valid_till', e.target.value)}
                    className="mt-1"
                  />
                </div>
              </div>
              
              <div>
                <Label htmlFor="max_uses">Maximum Uses Per Code</Label>
                <Input
                  id="max_uses"
                  type="number"
                  value={formData.max_uses}
                  onChange={(e) => handleChange('max_uses', parseInt(e.target.value) || 1)}
                  min={1}
                  className="mt-1"
                />
                <p className="text-xs text-muted-foreground mt-1">
                  How many times each code can be used
                </p>
              </div>
              
              <div className="flex items-center space-x-2">
                <Checkbox 
                  id="active-bulk"
                  checked={formData.active}
                  onCheckedChange={(checked) => 
                    handleChange('active', checked === true)
                  }
                />
                <Label htmlFor="active-bulk">Make codes active immediately</Label>
              </div>
            </div>
          </div>
          
          <CardFooter className="px-0 pt-6">
            <Button 
              type="submit" 
              disabled={isLoading}
              className="w-full"
            >
              {isLoading ? (
                <>
                  <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                  Generating...
                </>
              ) : (
                `Generate ${formData.count} Discount Codes`
              )}
            </Button>
          </CardFooter>
        </form>
      </CardContent>
    </Card>
  );
};

export default BulkDiscountGenerator; 