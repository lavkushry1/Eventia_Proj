import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { toast } from '@/hooks/use-toast';
import { useAdminAuth } from '@/hooks/use-admin-auth';
import { api, ApiEvent } from '@/lib/api';
import Navbar from '@/components/layout/Navbar';
import Footer from '@/components/layout/Footer';
import AdminProtectedRoute from '@/components/AdminProtectedRoute';
import { 
  Card, 
  CardContent, 
  CardDescription, 
  CardFooter, 
  CardHeader, 
  CardTitle 
} from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Textarea } from '@/components/ui/textarea';
import { Label } from '@/components/ui/label';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import {
  Form,
  FormControl,
  FormDescription,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
} from '@/components/ui/form';
import { Checkbox } from '@/components/ui/checkbox';
import { ArrowLeft, CalendarIcon, Clock, MapPin, Loader2, Trash2, Plus } from 'lucide-react';
import { format } from 'date-fns';
import { Calendar } from '@/components/ui/calendar';
import {
  Popover,
  PopoverContent,
  PopoverTrigger,
} from '@/components/ui/popover';
import { cn } from '@/lib/utils';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import * as z from 'zod';

// Form schema
const eventSchema = z.object({
  title: z.string().min(5, "Title must be at least 5 characters"),
  description: z.string().min(10, "Description must be at least 10 characters"),
  category: z.string().min(1, "Category is required"),
  date: z.date({
    required_error: "Event date is required",
  }),
  time: z.string().regex(/^([0-1]?[0-9]|2[0-3]):[0-5][0-9]$/, "Time must be in HH:MM format"),
  venue: z.string().min(3, "Venue must be at least 3 characters"),
  image_url: z.string().url("Image URL must be a valid URL"),
  ticket_price: z.coerce.number().min(0, "Ticket price must be a positive number"),
  tickets_available: z.coerce.number().min(1, "Tickets available must be at least 1"),
  is_featured: z.boolean().default(false),
  status: z.string(),
  team_home: z.object({
    name: z.string(),
    logo: z.string(),
    primary_color: z.string(),
    secondary_color: z.string(),
  }).optional(),
  team_away: z.object({
    name: z.string(),
    logo: z.string(),
    primary_color: z.string(),
    secondary_color: z.string(),
  }).optional(),
  ticket_types: z.array(
    z.object({
      name: z.string().min(1, "Ticket type name is required"),
      price: z.coerce.number().min(0, "Ticket price must be a positive number"),
      available: z.coerce.number().min(0, "Available tickets must be a positive number"),
      description: z.string().optional(),
    })
  ).optional(),
});

type EventFormValues = z.infer<typeof eventSchema>;

const AdminEventEditor = () => {
  const { id } = useParams();
  const { adminToken } = useAdminAuth();
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const isEditing = !!id;

  // Placeholder for a fetch function - in a real app, this would be an API call
  const fetchEvent = async (id: string): Promise<ApiEvent> => {
    // Simulated API call for demo purposes
    return {
      id,
      title: 'Mumbai Indians vs Chennai Super Kings',
      description: 'Watch the thrilling IPL match between Mumbai Indians and Chennai Super Kings at the iconic Wankhede Stadium.',
      date: '2023-04-15',
      time: '19:30',
      venue: 'Wankhede Stadium, Mumbai',
      category: 'IPL',
      image_url: 'https://example.com/mi-vs-csk.jpg',
      tickets_available: 5000,
      ticket_price: 2500,
      is_featured: true,
      status: 'available',
      team_home: {
        name: 'Mumbai Indians',
        logo: 'mi',
        primary_color: '#004BA0',
        secondary_color: '#FFFFFF'
      },
      team_away: {
        name: 'Chennai Super Kings',
        logo: 'csk',
        primary_color: '#FFFF00',
        secondary_color: '#0000FF'
      },
      ticket_types: [
        {
          id: '1',
          name: 'General',
          price: 2500,
          available: 2000,
          description: 'Standard seating'
        },
        {
          id: '2',
          name: 'Premium',
          price: 5000,
          available: 1000,
          description: 'Better view and comfortable seating'
        },
        {
          id: '3',
          name: 'VIP',
          price: 10000,
          available: 500,
          description: 'Best seats in the house with complimentary refreshments'
        }
      ]
    };
  };

  // Placeholder for event categories
  const eventCategories = [
    { value: 'IPL', label: 'IPL Match' },
    { value: 'Concert', label: 'Music Concert' },
    { value: 'Comedy', label: 'Comedy Show' },
    { value: 'Conference', label: 'Conference' },
    { value: 'Exhibition', label: 'Exhibition' },
    { value: 'Other', label: 'Other' },
  ];

  // Placeholder for event statuses
  const eventStatuses = [
    { value: 'available', label: 'Available' },
    { value: 'sold_out', label: 'Sold Out' },
    { value: 'cancelled', label: 'Cancelled' },
    { value: 'upcoming', label: 'Upcoming' },
  ];

  // Fetch event data if editing
  const { data: eventData, isLoading: isLoadingEvent, error: eventError } = useQuery({
    queryKey: ['event', id],
    queryFn: () => fetchEvent(id as string),
    enabled: isEditing && !!adminToken,
  });

  // Form setup
  const form = useForm<EventFormValues>({
    resolver: zodResolver(eventSchema),
    defaultValues: {
      title: '',
      description: '',
      category: '',
      date: new Date(),
      time: '19:30',
      venue: '',
      image_url: '',
      ticket_price: 0,
      tickets_available: 100,
      is_featured: false,
      status: 'available',
      ticket_types: [
        { name: 'General', price: 0, available: 0, description: '' }
      ],
    },
  });

  // Update form when event data is loaded
  useEffect(() => {
    if (eventData) {
      form.reset({
        ...eventData,
        date: new Date(eventData.date),
        ticket_types: eventData.ticket_types || [
          { name: 'General', price: eventData.ticket_price, available: eventData.tickets_available, description: '' }
        ],
      });
    }
  }, [eventData, form]);

  // Add ticket type
  const addTicketType = () => {
    const currentTicketTypes = form.getValues('ticket_types') || [];
    form.setValue('ticket_types', [
      ...currentTicketTypes,
      { name: '', price: 0, available: 0, description: '' }
    ]);
  };

  // Remove ticket type
  const removeTicketType = (index: number) => {
    const currentTicketTypes = form.getValues('ticket_types') || [];
    if (currentTicketTypes.length <= 1) {
      toast({
        title: "Cannot remove ticket type",
        description: "You must have at least one ticket type",
        variant: "destructive"
      });
      return;
    }
    
    const newTicketTypes = [...currentTicketTypes];
    newTicketTypes.splice(index, 1);
    form.setValue('ticket_types', newTicketTypes);
  };

  // Handle form submission
  const onSubmit = (data: EventFormValues) => {
    console.log('Form submitted:', data);
    
    // Simulate successful submission
    toast({
      title: isEditing ? "Event updated" : "Event created",
      description: `${data.title} has been ${isEditing ? 'updated' : 'created'} successfully.`,
    });
    
    // Redirect to dashboard
    navigate('/admin-dashboard');
  };

  return (
    <AdminProtectedRoute>
      <div className="flex min-h-screen flex-col">
        <Navbar />
        
        <main className="flex-grow bg-gray-50 py-8">
          <div className="container mx-auto px-4">
            <div className="mb-6 flex justify-between items-center">
              <Button 
                variant="ghost" 
                onClick={() => navigate('/admin-dashboard')}
                className="flex items-center"
              >
                <ArrowLeft className="h-4 w-4 mr-2" />
                Back to Dashboard
              </Button>
              
              <h1 className="text-2xl font-bold">
                {isEditing ? 'Edit Event' : 'Create New Event'}
              </h1>
            </div>
            
            {isEditing && isLoadingEvent ? (
              <div className="flex justify-center items-center h-64">
                <Loader2 className="h-8 w-8 animate-spin text-primary" />
              </div>
            ) : eventError ? (
              <div className="text-center p-8 text-red-500">
                <p>Error loading event data. Please try again.</p>
                <Button 
                  variant="outline" 
                  className="mt-4"
                  onClick={() => navigate('/admin-dashboard')}
                >
                  Back to Dashboard
                </Button>
              </div>
            ) : (
              <Form {...form}>
                <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-8">
                  <Card>
                    <CardHeader>
                      <CardTitle>Basic Information</CardTitle>
                      <CardDescription>
                        Enter the basic details about the event
                      </CardDescription>
                    </CardHeader>
                    <CardContent className="space-y-4">
                      <FormField
                        control={form.control}
                        name="title"
                        render={({ field }) => (
                          <FormItem>
                            <FormLabel>Event Title *</FormLabel>
                            <FormControl>
                              <Input placeholder="Enter event title" {...field} />
                            </FormControl>
                            <FormDescription>
                              This will be displayed as the main title of the event.
                            </FormDescription>
                            <FormMessage />
                          </FormItem>
                        )}
                      />
                      
                      <FormField
                        control={form.control}
                        name="description"
                        render={({ field }) => (
                          <FormItem>
                            <FormLabel>Description *</FormLabel>
                            <FormControl>
                              <Textarea
                                placeholder="Enter event description"
                                className="min-h-[100px]"
                                {...field}
                              />
                            </FormControl>
                            <FormDescription>
                              Provide a detailed description of the event.
                            </FormDescription>
                            <FormMessage />
                          </FormItem>
                        )}
                      />
                      
                      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                        <FormField
                          control={form.control}
                          name="category"
                          render={({ field }) => (
                            <FormItem>
                              <FormLabel>Category *</FormLabel>
                              <Select
                                onValueChange={field.onChange}
                                defaultValue={field.value}
                              >
                                <FormControl>
                                  <SelectTrigger>
                                    <SelectValue placeholder="Select category" />
                                  </SelectTrigger>
                                </FormControl>
                                <SelectContent>
                                  {eventCategories.map((category) => (
                                    <SelectItem key={category.value} value={category.value}>
                                      {category.label}
                                    </SelectItem>
                                  ))}
                                </SelectContent>
                              </Select>
                              <FormDescription>
                                Select the category that best describes this event.
                              </FormDescription>
                              <FormMessage />
                            </FormItem>
                          )}
                        />
                        
                        <FormField
                          control={form.control}
                          name="status"
                          render={({ field }) => (
                            <FormItem>
                              <FormLabel>Status *</FormLabel>
                              <Select
                                onValueChange={field.onChange}
                                defaultValue={field.value}
                              >
                                <FormControl>
                                  <SelectTrigger>
                                    <SelectValue placeholder="Select status" />
                                  </SelectTrigger>
                                </FormControl>
                                <SelectContent>
                                  {eventStatuses.map((status) => (
                                    <SelectItem key={status.value} value={status.value}>
                                      {status.label}
                                    </SelectItem>
                                  ))}
                                </SelectContent>
                              </Select>
                              <FormDescription>
                                Set the current status of this event.
                              </FormDescription>
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
                                This event will be highlighted on the homepage.
                              </FormDescription>
                            </div>
                          </FormItem>
                        )}
                      />
                    </CardContent>
                  </Card>
                  
                  <Card>
                    <CardHeader>
                      <CardTitle>Date & Location</CardTitle>
                      <CardDescription>
                        When and where the event will take place
                      </CardDescription>
                    </CardHeader>
                    <CardContent className="space-y-4">
                      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                        <FormField
                          control={form.control}
                          name="date"
                          render={({ field }) => (
                            <FormItem className="flex flex-col">
                              <FormLabel>Date *</FormLabel>
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
                                The date when the event will take place.
                              </FormDescription>
                              <FormMessage />
                            </FormItem>
                          )}
                        />
                        
                        <FormField
                          control={form.control}
                          name="time"
                          render={({ field }) => (
                            <FormItem>
                              <FormLabel>Time *</FormLabel>
                              <div className="flex items-center">
                                <FormControl>
                                  <Input
                                    placeholder="HH:MM"
                                    {...field}
                                  />
                                </FormControl>
                                <Clock className="ml-2 h-4 w-4 text-muted-foreground" />
                              </div>
                              <FormDescription>
                                The time when the event will start (24-hour format).
                              </FormDescription>
                              <FormMessage />
                            </FormItem>
                          )}
                        />
                      </div>
                      
                      <FormField
                        control={form.control}
                        name="venue"
                        render={({ field }) => (
                          <FormItem>
                            <FormLabel>Venue *</FormLabel>
                            <div className="flex items-center">
                              <FormControl>
                                <Input
                                  placeholder="Enter venue name and location"
                                  {...field}
                                />
                              </FormControl>
                              <MapPin className="ml-2 h-4 w-4 text-muted-foreground" />
                            </div>
                            <FormDescription>
                              The location where the event will be held.
                            </FormDescription>
                            <FormMessage />
                          </FormItem>
                        )}
                      />
                    </CardContent>
                  </Card>
                  
                  <Card>
                    <CardHeader>
                      <CardTitle>Ticketing Information</CardTitle>
                      <CardDescription>
                        Configure ticket prices and availability
                      </CardDescription>
                    </CardHeader>
                    <CardContent className="space-y-4">
                      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                        <FormField
                          control={form.control}
                          name="ticket_price"
                          render={({ field }) => (
                            <FormItem>
                              <FormLabel>Base Ticket Price (₹) *</FormLabel>
                              <FormControl>
                                <Input
                                  type="number"
                                  min="0"
                                  placeholder="0"
                                  {...field}
                                />
                              </FormControl>
                              <FormDescription>
                                The standard price for tickets. You can add different ticket types below.
                              </FormDescription>
                              <FormMessage />
                            </FormItem>
                          )}
                        />
                        
                        <FormField
                          control={form.control}
                          name="tickets_available"
                          render={({ field }) => (
                            <FormItem>
                              <FormLabel>Total Tickets Available *</FormLabel>
                              <FormControl>
                                <Input
                                  type="number"
                                  min="0"
                                  placeholder="100"
                                  {...field}
                                />
                              </FormControl>
                              <FormDescription>
                                The total number of tickets available for this event.
                              </FormDescription>
                              <FormMessage />
                            </FormItem>
                          )}
                        />
                      </div>
                      
                      <div className="space-y-4">
                        <div className="flex items-center justify-between">
                          <h3 className="text-lg font-medium">Ticket Types</h3>
                          <Button
                            type="button"
                            variant="outline"
                            size="sm"
                            onClick={addTicketType}
                          >
                            <Plus className="h-4 w-4 mr-2" />
                            Add Ticket Type
                          </Button>
                        </div>
                        
                        {form.watch('ticket_types')?.map((_, index) => (
                          <div key={index} className="border rounded-lg p-4 space-y-4">
                            <div className="flex justify-between items-center">
                              <h4 className="font-medium">Ticket Type {index + 1}</h4>
                              <Button
                                type="button"
                                variant="ghost"
                                size="sm"
                                onClick={() => removeTicketType(index)}
                              >
                                <Trash2 className="h-4 w-4 text-red-500" />
                              </Button>
                            </div>
                            
                            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                              <FormField
                                control={form.control}
                                name={`ticket_types.${index}.name`}
                                render={({ field }) => (
                                  <FormItem>
                                    <FormLabel>Name *</FormLabel>
                                    <FormControl>
                                      <Input placeholder="e.g., VIP, Standard" {...field} />
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
                                    <FormLabel>Price (₹) *</FormLabel>
                                    <FormControl>
                                      <Input type="number" min="0" {...field} />
                                    </FormControl>
                                    <FormMessage />
                                  </FormItem>
                                )}
                              />
                            </div>
                            
                            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                              <FormField
                                control={form.control}
                                name={`ticket_types.${index}.available`}
                                render={({ field }) => (
                                  <FormItem>
                                    <FormLabel>Available *</FormLabel>
                                    <FormControl>
                                      <Input type="number" min="0" {...field} />
                                    </FormControl>
                                    <FormMessage />
                                  </FormItem>
                                )}
                              />
                              
                              <FormField
                                control={form.control}
                                name={`ticket_types.${index}.description`}
                                render={({ field }) => (
                                  <FormItem>
                                    <FormLabel>Description</FormLabel>
                                    <FormControl>
                                      <Input placeholder="Brief description of this ticket type" {...field} />
                                    </FormControl>
                                    <FormMessage />
                                  </FormItem>
                                )}
                              />
                            </div>
                          </div>
                        ))}
                      </div>
                    </CardContent>
                  </Card>
                  
                  <Card>
                    <CardHeader>
                      <CardTitle>Media & Appearance</CardTitle>
                      <CardDescription>
                        Upload images and set appearance options
                      </CardDescription>
                    </CardHeader>
                    <CardContent className="space-y-4">
                      <FormField
                        control={form.control}
                        name="image_url"
                        render={({ field }) => (
                          <FormItem>
                            <FormLabel>Image URL *</FormLabel>
                            <FormControl>
                              <Input placeholder="https://example.com/image.jpg" {...field} />
                            </FormControl>
                            <FormDescription>
                              Enter a URL for the event image. The image should be at least 800x450 pixels.
                            </FormDescription>
                            <FormMessage />
                          </FormItem>
                        )}
                      />
                      
                      {/* Image preview */}
                      {form.watch('image_url') && (
                        <div className="mt-2">
                          <p className="text-sm font-medium mb-2">Preview:</p>
                          <div className="border rounded-md overflow-hidden">
                            <img
                              src={form.watch('image_url')}
                              alt="Event preview"
                              className="w-full h-auto object-cover"
                              onError={(e) => {
                                (e.target as HTMLImageElement).src = 'https://via.placeholder.com/800x450?text=Image+Not+Found';
                              }}
                            />
                          </div>
                        </div>
                      )}
                    </CardContent>
                  </Card>
                  
                  {/* Teams section for IPL events */}
                  {form.watch('category') === 'IPL' && (
                    <Card>
                      <CardHeader>
                        <CardTitle>Team Information</CardTitle>
                        <CardDescription>
                          Enter details about the competing teams
                        </CardDescription>
                      </CardHeader>
                      <CardContent className="space-y-6">
                        {/* Home Team */}
                        <div>
                          <h3 className="text-lg font-medium mb-4">Home Team</h3>
                          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                            <FormField
                              control={form.control}
                              name="team_home.name"
                              render={({ field }) => (
                                <FormItem>
                                  <FormLabel>Team Name</FormLabel>
                                  <FormControl>
                                    <Input placeholder="e.g., Mumbai Indians" {...field} />
                                  </FormControl>
                                  <FormMessage />
                                </FormItem>
                              )}
                            />
                            
                            <FormField
                              control={form.control}
                              name="team_home.logo"
                              render={({ field }) => (
                                <FormItem>
                                  <FormLabel>Team Code</FormLabel>
                                  <FormControl>
                                    <Input placeholder="e.g., MI" {...field} />
                                  </FormControl>
                                  <FormDescription>
                                    Short code for the team (e.g., MI for Mumbai Indians)
                                  </FormDescription>
                                  <FormMessage />
                                </FormItem>
                              )}
                            />
                            
                            <FormField
                              control={form.control}
                              name="team_home.primary_color"
                              render={({ field }) => (
                                <FormItem>
                                  <FormLabel>Primary Color</FormLabel>
                                  <div className="flex items-center space-x-2">
                                    <FormControl>
                                      <Input placeholder="#004BA0" {...field} />
                                    </FormControl>
                                    <div
                                      className="w-6 h-6 border rounded"
                                      style={{ backgroundColor: field.value }}
                                    />
                                  </div>
                                  <FormDescription>
                                    Hex color code (e.g., #004BA0)
                                  </FormDescription>
                                  <FormMessage />
                                </FormItem>
                              )}
                            />
                            
                            <FormField
                              control={form.control}
                              name="team_home.secondary_color"
                              render={({ field }) => (
                                <FormItem>
                                  <FormLabel>Secondary Color</FormLabel>
                                  <div className="flex items-center space-x-2">
                                    <FormControl>
                                      <Input placeholder="#FFFFFF" {...field} />
                                    </FormControl>
                                    <div
                                      className="w-6 h-6 border rounded"
                                      style={{ backgroundColor: field.value }}
                                    />
                                  </div>
                                  <FormDescription>
                                    Hex color code (e.g., #FFFFFF)
                                  </FormDescription>
                                  <FormMessage />
                                </FormItem>
                              )}
                            />
                          </div>
                        </div>
                        
                        {/* Away Team */}
                        <div>
                          <h3 className="text-lg font-medium mb-4">Away Team</h3>
                          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                            <FormField
                              control={form.control}
                              name="team_away.name"
                              render={({ field }) => (
                                <FormItem>
                                  <FormLabel>Team Name</FormLabel>
                                  <FormControl>
                                    <Input placeholder="e.g., Chennai Super Kings" {...field} />
                                  </FormControl>
                                  <FormMessage />
                                </FormItem>
                              )}
                            />
                            
                            <FormField
                              control={form.control}
                              name="team_away.logo"
                              render={({ field }) => (
                                <FormItem>
                                  <FormLabel>Team Code</FormLabel>
                                  <FormControl>
                                    <Input placeholder="e.g., CSK" {...field} />
                                  </FormControl>
                                  <FormDescription>
                                    Short code for the team (e.g., CSK for Chennai Super Kings)
                                  </FormDescription>
                                  <FormMessage />
                                </FormItem>
                              )}
                            />
                            
                            <FormField
                              control={form.control}
                              name="team_away.primary_color"
                              render={({ field }) => (
                                <FormItem>
                                  <FormLabel>Primary Color</FormLabel>
                                  <div className="flex items-center space-x-2">
                                    <FormControl>
                                      <Input placeholder="#FFFF00" {...field} />
                                    </FormControl>
                                    <div
                                      className="w-6 h-6 border rounded"
                                      style={{ backgroundColor: field.value }}
                                    />
                                  </div>
                                  <FormDescription>
                                    Hex color code (e.g., #FFFF00)
                                  </FormDescription>
                                  <FormMessage />
                                </FormItem>
                              )}
                            />
                            
                            <FormField
                              control={form.control}
                              name="team_away.secondary_color"
                              render={({ field }) => (
                                <FormItem>
                                  <FormLabel>Secondary Color</FormLabel>
                                  <div className="flex items-center space-x-2">
                                    <FormControl>
                                      <Input placeholder="#0000FF" {...field} />
                                    </FormControl>
                                    <div
                                      className="w-6 h-6 border rounded"
                                      style={{ backgroundColor: field.value }}
                                    />
                                  </div>
                                  <FormDescription>
                                    Hex color code (e.g., #0000FF)
                                  </FormDescription>
                                  <FormMessage />
                                </FormItem>
                              )}
                            />
                          </div>
                        </div>
                      </CardContent>
                    </Card>
                  )}
                  
                  <div className="flex justify-end space-x-4">
                    <Button 
                      type="button" 
                      variant="outline"
                      onClick={() => navigate('/admin-dashboard')}
                    >
                      Cancel
                    </Button>
                    <Button type="submit">
                      {isEditing ? 'Update Event' : 'Create Event'}
                    </Button>
                  </div>
                </form>
              </Form>
            )}
          </div>
        </main>
        
        <Footer />
      </div>
    </AdminProtectedRoute>
  );
};

export default AdminEventEditor; 