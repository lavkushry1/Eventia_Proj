import React from 'react';
import { useForm, Controller } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Textarea } from '@/components/ui/textarea';
import { Checkbox } from '@/components/ui/checkbox';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from '@/components/ui/card';
import { Label } from '@/components/ui/label';
import { FormField, FormItem, FormLabel, FormControl, FormDescription, FormMessage, Form } from '@/components/ui/form';
import { EventCreate, TicketType, TeamInfo } from '@/lib/types';
import { eventCreateSchema } from '@/lib/validation';
import { adminCreateEvent } from '@/lib/api';
import { toast } from '@/hooks/use-toast';

interface EventFormProps {
  onSuccess?: (eventId: string) => void;
  onCancel?: () => void;
  defaultValues?: Partial<EventCreate>;
}

const EventForm: React.FC<EventFormProps> = ({ onSuccess, onCancel, defaultValues }) => {
  const form = useForm<EventCreate>({
    resolver: zodResolver(eventCreateSchema),
    defaultValues: {
      title: '',
      description: '',
      date: new Date().toISOString().split('T')[0],
      time: '19:30',
      venue: '',
      category: 'IPL',
      is_featured: false,
      status: 'upcoming',
      ticket_types: [
        {
          id: '',
          name: 'Standard',
          price: 1000,
          available: 1000,
          description: 'Standard ticket'
        }
      ],
      ...defaultValues
    }
  });

  const [isSubmitting, setIsSubmitting] = React.useState(false);
  const [ticketTypes, setTicketTypes] = React.useState<TicketType[]>(
    form.getValues().ticket_types || []
  );

  const onSubmit = async (data: EventCreate) => {
    try {
      setIsSubmitting(true);

      console.log('Submitting event data:', data);
      
      // Submit to API
      const response = await adminCreateEvent(data);
      
      toast({
        title: 'Event created successfully',
        description: `Event "${data.title}" has been created.`,
      });
      
      if (onSuccess) {
        onSuccess(response.id);
      }
    } catch (error) {
      console.error('Error creating event:', error);
      toast({
        title: 'Error creating event',
        description: 'There was an error creating the event. Please try again.',
        variant: 'destructive',
      });
    } finally {
      setIsSubmitting(false);
    }
  };

  const addTicketType = () => {
    const newTicketType: TicketType = {
      id: '',
      name: `Ticket Type ${ticketTypes.length + 1}`,
      price: 0,
      available: 0,
      description: ''
    };
    
    const updatedTicketTypes = [...ticketTypes, newTicketType];
    setTicketTypes(updatedTicketTypes);
    form.setValue('ticket_types', updatedTicketTypes, { shouldValidate: true });
  };

  const removeTicketType = (index: number) => {
    const updatedTicketTypes = [...ticketTypes];
    updatedTicketTypes.splice(index, 1);
    setTicketTypes(updatedTicketTypes);
    form.setValue('ticket_types', updatedTicketTypes, { shouldValidate: true });
  };

  return (
    <Card className="w-full">
      <CardHeader>
        <CardTitle>Create New Event</CardTitle>
        <CardDescription>
          Fill in the details to create a new event.
        </CardDescription>
      </CardHeader>
      <CardContent>
        <Form {...form}>
          <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-6">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <FormField
                control={form.control}
                name="title"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Event Title</FormLabel>
                    <FormControl>
                      <Input placeholder="Enter event title" {...field} />
                    </FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />

              <FormField
                control={form.control}
                name="category"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Category</FormLabel>
                    <FormControl>
                      <Select 
                        onValueChange={field.onChange} 
                        defaultValue={field.value}
                      >
                        <SelectTrigger>
                          <SelectValue placeholder="Select category" />
                        </SelectTrigger>
                        <SelectContent>
                          <SelectItem value="IPL">IPL</SelectItem>
                          <SelectItem value="Concert">Concert</SelectItem>
                          <SelectItem value="Exhibition">Exhibition</SelectItem>
                          <SelectItem value="Food">Food</SelectItem>
                          <SelectItem value="Festival">Festival</SelectItem>
                        </SelectContent>
                      </Select>
                    </FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />

              <FormField
                control={form.control}
                name="date"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Date</FormLabel>
                    <FormControl>
                      <Input type="date" {...field} />
                    </FormControl>
                    <FormDescription>Format: YYYY-MM-DD</FormDescription>
                    <FormMessage />
                  </FormItem>
                )}
              />

              <FormField
                control={form.control}
                name="time"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Time</FormLabel>
                    <FormControl>
                      <Input type="time" {...field} />
                    </FormControl>
                    <FormDescription>24-hour format</FormDescription>
                    <FormMessage />
                  </FormItem>
                )}
              />

              <FormField
                control={form.control}
                name="venue"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Venue</FormLabel>
                    <FormControl>
                      <Input placeholder="Event venue" {...field} />
                    </FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />

              <FormField
                control={form.control}
                name="image_url"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Image URL</FormLabel>
                    <FormControl>
                      <Input placeholder="https://example.com/image.jpg" {...field} />
                    </FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />

              <div className="col-span-1 md:col-span-2">
                <FormField
                  control={form.control}
                  name="description"
                  render={({ field }) => (
                    <FormItem>
                      <FormLabel>Description</FormLabel>
                      <FormControl>
                        <Textarea 
                          placeholder="Event description" 
                          className="min-h-32" 
                          {...field} 
                        />
                      </FormControl>
                      <FormMessage />
                    </FormItem>
                  )}
                />
              </div>

              <FormField
                control={form.control}
                name="is_featured"
                render={({ field }) => (
                  <FormItem className="flex flex-row items-start space-x-3 space-y-0 rounded-md border p-4">
                    <FormControl>
                      <Checkbox
                        checked={field.value}
                        onCheckedChange={field.onChange}
                      />
                    </FormControl>
                    <div className="space-y-1 leading-none">
                      <FormLabel>Featured Event</FormLabel>
                      <FormDescription>
                        Featured events appear on the homepage
                      </FormDescription>
                    </div>
                  </FormItem>
                )}
              />

              <FormField
                control={form.control}
                name="status"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Status</FormLabel>
                    <FormControl>
                      <Select 
                        onValueChange={field.onChange} 
                        defaultValue={field.value}
                      >
                        <SelectTrigger>
                          <SelectValue placeholder="Select status" />
                        </SelectTrigger>
                        <SelectContent>
                          <SelectItem value="upcoming">Upcoming</SelectItem>
                          <SelectItem value="ongoing">Ongoing</SelectItem>
                          <SelectItem value="completed">Completed</SelectItem>
                          <SelectItem value="cancelled">Cancelled</SelectItem>
                        </SelectContent>
                      </Select>
                    </FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />
            </div>

            <div className="border-t pt-4">
              <div className="flex justify-between items-center mb-4">
                <h3 className="text-lg font-medium">Ticket Types</h3>
                <Button type="button" onClick={addTicketType} variant="outline" size="sm">
                  Add Ticket Type
                </Button>
              </div>

              {ticketTypes.map((ticket, index) => (
                <div key={index} className="grid grid-cols-1 md:grid-cols-4 gap-4 p-4 border rounded-md mb-4">
                  <FormField
                    control={form.control}
                    name={`ticket_types.${index}.name`}
                    render={({ field }) => (
                      <FormItem>
                        <FormLabel>Name</FormLabel>
                        <FormControl>
                          <Input placeholder="Ticket name" {...field} />
                        </FormControl>
                        <FormMessage />
                      </FormItem>
                    )}
                  />

                  <FormField
                    control={form.control}
                    name={`ticket_types.${index}.price`}
                    render={({ field }) => (
                      <FormItem>
                        <FormLabel>Price</FormLabel>
                        <FormControl>
                          <Input 
                            type="number" 
                            placeholder="0" 
                            {...field}
                            onChange={(e) => field.onChange(parseFloat(e.target.value))}
                          />
                        </FormControl>
                        <FormMessage />
                      </FormItem>
                    )}
                  />

                  <FormField
                    control={form.control}
                    name={`ticket_types.${index}.available`}
                    render={({ field }) => (
                      <FormItem>
                        <FormLabel>Available</FormLabel>
                        <FormControl>
                          <Input 
                            type="number" 
                            placeholder="0" 
                            {...field}
                            onChange={(e) => field.onChange(parseInt(e.target.value))}
                          />
                        </FormControl>
                        <FormMessage />
                      </FormItem>
                    )}
                  />

                  <div className="flex items-end">
                    <Button 
                      type="button" 
                      onClick={() => removeTicketType(index)} 
                      variant="destructive"
                      size="sm"
                      className="mb-2"
                      disabled={ticketTypes.length <= 1}
                    >
                      Remove
                    </Button>
                  </div>
                </div>
              ))}
            </div>

            <div className="flex justify-end space-x-2">
              {onCancel && (
                <Button type="button" variant="outline" onClick={onCancel}>
                  Cancel
                </Button>
              )}
              <Button type="submit" disabled={isSubmitting}>
                {isSubmitting ? 'Creating...' : 'Create Event'}
              </Button>
            </div>
          </form>
        </Form>
      </CardContent>
    </Card>
  );
};

export default EventForm; 