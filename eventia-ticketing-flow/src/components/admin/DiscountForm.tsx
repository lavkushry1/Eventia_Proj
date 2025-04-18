import React, { useState, useEffect } from 'react';
import { zodResolver } from '@hookform/resolvers/zod';
import { useForm } from 'react-hook-form';
import * as z from 'zod';
import { format } from 'date-fns';
import { Calendar as CalendarIcon } from 'lucide-react';

import { Calendar } from '@/components/ui/calendar';
import {
  Card,
  CardContent,
  CardDescription,
  CardFooter,
  CardHeader,
  CardTitle,
} from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import {
  Form,
  FormControl,
  FormDescription,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
} from '@/components/ui/form';
import { Input } from '@/components/ui/input';
import {
  Popover,
  PopoverContent,
  PopoverTrigger,
} from '@/components/ui/popover';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import {
  Command,
  CommandEmpty,
  CommandGroup,
  CommandInput,
  CommandItem,
} from '@/components/ui/command';
import { Checkbox } from '@/components/ui/checkbox';
import { cn } from '@/lib/utils';
import { Switch } from '@/components/ui/switch';

interface Event {
  _id: string;
  name: string;
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
}

interface DiscountFormProps {
  discount?: Discount;
  events: Event[];
  onSubmit: (discount: Discount) => void;
  onCancel: () => void;
  isProcessing?: boolean;
}

// Schema for form validation
const formSchema = z.object({
  discount_code: z.string().min(2, {
    message: 'Discount code must be at least 2 characters.',
  }).max(50),
  discount_type: z.enum(['percentage', 'fixed']),
  value: z.coerce.number().min(1, { 
    message: 'Discount value must be greater than 0'
  }).refine((val) => val <= 100, {
    message: 'Percentage discount cannot exceed 100%',
    path: ['value'],
  }),
  applicable_events: z.array(z.string()).optional().default([]),
  valid_from: z.date(),
  valid_till: z.date(),
  max_uses: z.coerce.number().int().min(0),
  active: z.boolean().default(true),
}).refine(data => {
  return data.valid_from <= data.valid_till;
}, {
  message: "End date must be after start date",
  path: ["valid_till"],
});

const DiscountForm: React.FC<DiscountFormProps> = ({
  discount,
  events,
  onSubmit,
  onCancel,
  isProcessing = false
}) => {
  const [openEventsPopover, setOpenEventsPopover] = useState(false);
  const isEditing = !!discount?._id;

  // Initialize form with default values or edit values
  const form = useForm<z.infer<typeof formSchema>>({
    resolver: zodResolver(formSchema),
    defaultValues: discount
      ? {
          ...discount,
          valid_from: new Date(discount.valid_from),
          valid_till: new Date(discount.valid_till),
        }
      : {
          discount_code: '',
          discount_type: 'percentage',
          value: 10,
          applicable_events: [],
          valid_from: new Date(),
          valid_till: new Date(new Date().setMonth(new Date().getMonth() + 1)),
          max_uses: 0,
          active: true,
        },
  });

  // Handle form submission
  const handleSubmit = (values: z.infer<typeof formSchema>) => {
    onSubmit({
      _id: discount?._id,
      discount_code: values.discount_code,
      discount_type: values.discount_type,
      value: values.value,
      applicable_events: values.applicable_events,
      max_uses: values.max_uses,
      active: values.active,
      valid_from: values.valid_from.toISOString(),
      valid_till: values.valid_till.toISOString(),
    });
  };

  // Get selected events data for display
  const selectedEvents = form.watch('applicable_events') || [];
  
  return (
    <Card className="w-full">
      <CardHeader>
        <CardTitle>{isEditing ? 'Edit Discount' : 'Create Discount'}</CardTitle>
        <CardDescription>
          {isEditing 
            ? 'Update the discount details below'
            : 'Fill in the details to create a new discount code'}
        </CardDescription>
      </CardHeader>
      
      <Form {...form}>
        <form onSubmit={form.handleSubmit(handleSubmit)}>
          <CardContent className="space-y-4">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {/* Discount Code */}
              <FormField
                control={form.control}
                name="discount_code"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Discount Code</FormLabel>
                    <FormControl>
                      <Input placeholder="SUMMER2023" {...field} />
                    </FormControl>
                    <FormDescription>
                      Customers will enter this code at checkout
                    </FormDescription>
                    <FormMessage />
                  </FormItem>
                )}
              />

              {/* Max Uses */}
              <FormField
                control={form.control}
                name="max_uses"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Maximum Uses</FormLabel>
                    <FormControl>
                      <Input type="number" min="0" placeholder="0 for unlimited" {...field} />
                    </FormControl>
                    <FormDescription>
                      Set to 0 for unlimited uses
                    </FormDescription>
                    <FormMessage />
                  </FormItem>
                )}
              />
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {/* Discount Type */}
              <FormField
                control={form.control}
                name="discount_type"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Discount Type</FormLabel>
                    <Select 
                      onValueChange={field.onChange} 
                      defaultValue={field.value}
                    >
                      <FormControl>
                        <SelectTrigger>
                          <SelectValue placeholder="Select discount type" />
                        </SelectTrigger>
                      </FormControl>
                      <SelectContent>
                        <SelectItem value="percentage">Percentage (%)</SelectItem>
                        <SelectItem value="fixed">Fixed Amount (₹)</SelectItem>
                      </SelectContent>
                    </Select>
                    <FormDescription>
                      Percentage or fixed amount off
                    </FormDescription>
                    <FormMessage />
                  </FormItem>
                )}
              />

              {/* Discount Value */}
              <FormField
                control={form.control}
                name="value"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Discount Value</FormLabel>
                    <FormControl>
                      <Input 
                        type="number" 
                        min="1" 
                        max={form.watch('discount_type') === 'percentage' ? 100 : undefined}
                        placeholder={form.watch('discount_type') === 'percentage' ? '10' : '100'} 
                        {...field} 
                      />
                    </FormControl>
                    <FormDescription>
                      {form.watch('discount_type') === 'percentage' 
                        ? 'Percentage off the total' 
                        : 'Fixed amount off in rupees'}
                    </FormDescription>
                    <FormMessage />
                  </FormItem>
                )}
              />
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {/* Valid From */}
              <FormField
                control={form.control}
                name="valid_from"
                render={({ field }) => (
                  <FormItem className="flex flex-col">
                    <FormLabel>Valid From</FormLabel>
                    <Popover>
                      <PopoverTrigger asChild>
                        <FormControl>
                          <Button
                            variant={"outline"}
                            className={cn(
                              "w-full pl-3 text-left font-normal",
                              !field.value && "text-muted-foreground"
                            )}
                          >
                            {field.value ? (
                              format(field.value, "PPP")
                            ) : (
                              <span>Pick a date</span>
                            )}
                            <CalendarIcon className="ml-auto h-4 w-4 opacity-50" />
                          </Button>
                        </FormControl>
                      </PopoverTrigger>
                      <PopoverContent className="w-auto p-0" align="start">
                        <Calendar
                          mode="single"
                          selected={field.value}
                          onSelect={field.onChange}
                          disabled={(date) =>
                            date < new Date(new Date().setHours(0, 0, 0, 0))
                          }
                          initialFocus
                        />
                      </PopoverContent>
                    </Popover>
                    <FormDescription>
                      When the discount becomes active
                    </FormDescription>
                    <FormMessage />
                  </FormItem>
                )}
              />

              {/* Valid Till */}
              <FormField
                control={form.control}
                name="valid_till"
                render={({ field }) => (
                  <FormItem className="flex flex-col">
                    <FormLabel>Valid Till</FormLabel>
                    <Popover>
                      <PopoverTrigger asChild>
                        <FormControl>
                          <Button
                            variant={"outline"}
                            className={cn(
                              "w-full pl-3 text-left font-normal",
                              !field.value && "text-muted-foreground"
                            )}
                          >
                            {field.value ? (
                              format(field.value, "PPP")
                            ) : (
                              <span>Pick a date</span>
                            )}
                            <CalendarIcon className="ml-auto h-4 w-4 opacity-50" />
                          </Button>
                        </FormControl>
                      </PopoverTrigger>
                      <PopoverContent className="w-auto p-0" align="start">
                        <Calendar
                          mode="single"
                          selected={field.value}
                          onSelect={field.onChange}
                          disabled={(date) =>
                            date < form.watch('valid_from')
                          }
                          initialFocus
                        />
                      </PopoverContent>
                    </Popover>
                    <FormDescription>
                      When the discount expires
                    </FormDescription>
                    <FormMessage />
                  </FormItem>
                )}
              />
            </div>

            {/* Applicable Events */}
            <FormField
              control={form.control}
              name="applicable_events"
              render={({ field }) => (
                <FormItem className="flex flex-col">
                  <FormLabel>Applicable Events</FormLabel>
                  <Popover open={openEventsPopover} onOpenChange={setOpenEventsPopover}>
                    <PopoverTrigger asChild>
                      <FormControl>
                        <Button
                          variant="outline"
                          role="combobox"
                          className={cn(
                            "w-full justify-between",
                            !field.value?.length && "text-muted-foreground"
                          )}
                        >
                          {field.value?.length
                            ? `${field.value.length} event${field.value.length > 1 ? 's' : ''} selected`
                            : "Select events (leave empty for all)"}
                        </Button>
                      </FormControl>
                    </PopoverTrigger>
                    <PopoverContent className="w-full p-0">
                      <Command>
                        <CommandInput placeholder="Search events..." />
                        <CommandEmpty>No events found.</CommandEmpty>
                        <CommandGroup className="max-h-64 overflow-auto">
                          {events.map((event) => (
                            <CommandItem
                              value={event.name}
                              key={event._id}
                              onSelect={() => {
                                const currentValues = [...(field.value || [])];
                                const index = currentValues.indexOf(event._id);
                                
                                if (index === -1) {
                                  field.onChange([...currentValues, event._id]);
                                } else {
                                  currentValues.splice(index, 1);
                                  field.onChange(currentValues);
                                }
                              }}
                            >
                              <Checkbox
                                checked={field.value?.includes(event._id)}
                                className="mr-2"
                              />
                              {event.name}
                            </CommandItem>
                          ))}
                        </CommandGroup>
                      </Command>
                    </PopoverContent>
                  </Popover>
                  <FormDescription>
                    {selectedEvents.length 
                      ? 'Discount will apply only to selected events' 
                      : 'Leave empty to apply to all events'}
                  </FormDescription>
                  <FormMessage />
                </FormItem>
              )}
            />

            {/* Active Status */}
            <FormField
              control={form.control}
              name="active"
              render={({ field }) => (
                <FormItem className="flex flex-row items-center justify-between rounded-lg border p-4">
                  <div className="space-y-0.5">
                    <FormLabel className="text-base">Active Status</FormLabel>
                    <FormDescription>
                      Activate or deactivate this discount code
                    </FormDescription>
                  </div>
                  <FormControl>
                    <Switch
                      checked={field.value}
                      onCheckedChange={field.onChange}
                    />
                  </FormControl>
                </FormItem>
              )}
            />
          </CardContent>

          <CardFooter className="flex justify-between">
            <Button 
              type="button" 
              variant="outline" 
              onClick={onCancel}
              disabled={isProcessing}
            >
              Cancel
            </Button>
            <Button 
              type="submit"
              disabled={isProcessing}
            >
              {isProcessing ? 'Processing...' : isEditing ? 'Update Discount' : 'Create Discount'}
            </Button>
          </CardFooter>
        </form>
      </Form>
    </Card>
  );
};

export default DiscountForm; 