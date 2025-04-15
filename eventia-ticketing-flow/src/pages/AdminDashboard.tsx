import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import { toast } from '@/hooks/use-toast';
import { useAdminAuth } from '@/hooks/use-admin-auth';
import { api, ApiAnalyticsResponse } from '@/lib/api';
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
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { 
  BarChart, 
  Calendar, 
  Users, 
  CreditCard, 
  DollarSign, 
  TicketCheck, 
  Settings, 
  LogOut,
  Edit,
  Trash2,
  Eye,
  Loader2,
  Search,
  RefreshCw
} from 'lucide-react';
import { 
  Table, 
  TableBody, 
  TableCaption, 
  TableCell, 
  TableHead, 
  TableHeader, 
  TableRow 
} from '@/components/ui/table';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Input } from '@/components/ui/input';
import {
  Pagination,
  PaginationContent,
  PaginationItem,
  PaginationLink,
  PaginationNext,
  PaginationPrevious,
} from '@/components/ui/pagination';

const AdminDashboard = () => {
  const { adminToken, logout } = useAdminAuth();
  const navigate = useNavigate();
  const [activeTab, setActiveTab] = useState('overview');
  const [bookingFilter, setBookingFilter] = useState('all');
  const [searchQuery, setSearchQuery] = useState('');
  
  // Fetch analytics data
  const { 
    data: analyticsData,
    isLoading: isLoadingAnalytics,
    error: analyticsError
  } = useQuery<ApiAnalyticsResponse>({
    queryKey: ['analytics'],
    queryFn: () => api.getAnalytics(adminToken || ''),
    enabled: !!adminToken,
    staleTime: 60000, // 1 minute
  });

  const handleLogout = () => {
    logout();
      toast({
      title: "Logged out",
      description: "You have been logged out successfully.",
    });
  };

  const getStatusBadgeColor = (status: string) => {
    switch (status.toLowerCase()) {
      case 'confirmed':
        return 'bg-green-500';
      case 'pending':
        return 'bg-yellow-500';
      case 'cancelled':
        return 'bg-red-500';
      default:
        return 'bg-gray-500';
    }
  };

  // Placeholder for events data - would be loaded from API in a real implementation
  const eventsData = [
    { 
      id: '1', 
      title: 'Mumbai Indians vs Chennai Super Kings', 
      date: '2023-04-15', 
      venue: 'Wankhede Stadium',
      status: 'available',
      price: 2500,
      tickets_available: 250
    },
    { 
      id: '2', 
      title: 'Royal Challengers Bangalore vs Kolkata Knight Riders', 
      date: '2023-04-18', 
      venue: 'M. Chinnaswamy Stadium',
      status: 'available',
      price: 2000,
      tickets_available: 180
    },
    { 
      id: '3', 
      title: 'Delhi Capitals vs Sunrisers Hyderabad', 
      date: '2023-04-20', 
      venue: 'Arun Jaitley Stadium',
      status: 'sold_out',
      price: 1800,
      tickets_available: 0
    }
  ];
  
  const filteredEvents = eventsData.filter(event => 
    event.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
    event.venue.toLowerCase().includes(searchQuery.toLowerCase())
  );

  return (
    <AdminProtectedRoute>
    <div className="flex min-h-screen flex-col">
      <Navbar />

        <main className="flex-grow bg-gray-50">
          <div className="container mx-auto py-8 px-4">
            <div className="flex justify-between items-center mb-6">
              <h1 className="text-3xl font-bold">Admin Dashboard</h1>
              <Button variant="ghost" onClick={handleLogout}>
                <LogOut className="h-4 w-4 mr-2" />
                Log Out
              </Button>
            </div>
            
            <Tabs defaultValue="overview" value={activeTab} onValueChange={setActiveTab}>
              <TabsList className="mb-8 w-full flex justify-start overflow-x-auto space-x-2">
                <TabsTrigger value="overview" className="flex items-center">
                  <BarChart className="h-4 w-4 mr-2" />
                  Overview
                </TabsTrigger>
                <TabsTrigger value="events" className="flex items-center">
                  <Calendar className="h-4 w-4 mr-2" />
                  Events
                </TabsTrigger>
                <TabsTrigger value="bookings" className="flex items-center">
                  <TicketCheck className="h-4 w-4 mr-2" />
                  Bookings
                </TabsTrigger>
                <TabsTrigger value="payments" className="flex items-center">
                  <DollarSign className="h-4 w-4 mr-2" />
                  Payment Settings
                </TabsTrigger>
                <TabsTrigger value="users" className="flex items-center">
                  <Users className="h-4 w-4 mr-2" />
                  User Management
                </TabsTrigger>
                <TabsTrigger value="settings" className="flex items-center">
                  <Settings className="h-4 w-4 mr-2" />
                  Settings
                </TabsTrigger>
              </TabsList>

              <TabsContent value="overview">
                {isLoadingAnalytics ? (
                  <div className="flex justify-center items-center h-64">
                    <Loader2 className="h-8 w-8 animate-spin text-primary" />
                  </div>
                ) : analyticsError ? (
                  <div className="text-center p-8 text-red-500">
                    <p>Error loading analytics data.</p>
                    <Button 
                      variant="outline" 
                      className="mt-4"
                      onClick={() => navigate(0)}
                    >
                      Retry
                    </Button>
                  </div>
                ) : (
                  <>
                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
                      <Card>
                <CardHeader className="pb-2">
                          <CardTitle className="text-sm font-medium text-muted-foreground">
                            Total Revenue
                  </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="flex items-center">
                            <CreditCard className="h-4 w-4 text-muted-foreground mr-2" />
                            <div className="text-2xl font-bold">
                              ₹{analyticsData?.total_revenue.toLocaleString() || 0}
                  </div>
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="pb-2">
                          <CardTitle className="text-sm font-medium text-muted-foreground">
                            Total Bookings
                          </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="flex items-center">
                            <TicketCheck className="h-4 w-4 text-muted-foreground mr-2" />
                            <div className="text-2xl font-bold">
                              {analyticsData?.total_bookings || 0}
                  </div>
                </div>
                          <div className="text-xs text-muted-foreground mt-1">
                            {analyticsData?.confirmed_bookings || 0} confirmed, {analyticsData?.pending_bookings || 0} pending
                          </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="pb-2">
                          <CardTitle className="text-sm font-medium text-muted-foreground">
                            Total Events
                          </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="flex items-center">
                            <Calendar className="h-4 w-4 text-muted-foreground mr-2" />
                            <div className="text-2xl font-bold">
                              {analyticsData?.total_events || 0}
                  </div>
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="pb-2">
                          <CardTitle className="text-sm font-medium text-muted-foreground">
                            Conversion Rate
                          </CardTitle>
              </CardHeader>
              <CardContent>
                          <div className="text-2xl font-bold">
                            {analyticsData?.total_bookings && analyticsData.confirmed_bookings
                              ? Math.round((analyticsData.confirmed_bookings / analyticsData.total_bookings) * 100)
                              : 0}%
                  </div>
                          <div className="text-xs text-muted-foreground mt-1">
                            Booking to confirmation rate
                </div>
              </CardContent>
            </Card>
          </div>

                    <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                      <Card>
                        <CardHeader>
                          <CardTitle>Popular Events</CardTitle>
                          <CardDescription>Top events by booking count</CardDescription>
                        </CardHeader>
                        <CardContent>
                          <Table>
                            <TableHeader>
                              <TableRow>
                                <TableHead>Event</TableHead>
                                <TableHead className="text-right">Bookings</TableHead>
                              </TableRow>
                            </TableHeader>
                            <TableBody>
                              {analyticsData?.popular_events?.length ? (
                                analyticsData.popular_events.map((event) => (
                                  <TableRow key={event.id}>
                                    <TableCell>{event.title}</TableCell>
                                    <TableCell className="text-right">{event.bookings_count}</TableCell>
                                  </TableRow>
                                ))
                              ) : (
                                <TableRow>
                                  <TableCell colSpan={2} className="text-center">No data available</TableCell>
                                </TableRow>
                              )}
                            </TableBody>
                          </Table>
                        </CardContent>
                      </Card>
                      
              <Card>
                <CardHeader>
                          <CardTitle>Recent Bookings</CardTitle>
                          <CardDescription>Latest 5 bookings</CardDescription>
                        </CardHeader>
                        <CardContent>
                          <Table>
                            <TableHeader>
                              <TableRow>
                                <TableHead>User</TableHead>
                                <TableHead>Status</TableHead>
                                <TableHead className="text-right">Amount</TableHead>
                              </TableRow>
                            </TableHeader>
                            <TableBody>
                              {analyticsData?.recent_bookings?.length ? (
                                analyticsData.recent_bookings.map((booking) => (
                                  <TableRow key={booking.id || booking.booking_id}>
                                    <TableCell>{booking.customer_info?.name || 'Unknown'}</TableCell>
                                    <TableCell>
                                      <Badge 
                                        variant="outline" 
                                        className={`${getStatusBadgeColor(booking.status)} text-white`}
                                      >
                                        {booking.status}
                                      </Badge>
                                    </TableCell>
                                    <TableCell className="text-right">₹{booking.total_amount}</TableCell>
                                  </TableRow>
                                ))
                              ) : (
                                <TableRow>
                                  <TableCell colSpan={3} className="text-center">No recent bookings</TableCell>
                                </TableRow>
                              )}
                            </TableBody>
                          </Table>
                        </CardContent>
                        <CardFooter>
                          <Button 
                            variant="outline" 
                            className="w-full" 
                            onClick={() => setActiveTab('bookings')}
                          >
                            View All Bookings
                          </Button>
                        </CardFooter>
                      </Card>
                    </div>
                  </>
                )}
              </TabsContent>

              <TabsContent value="events">
                <div className="mb-6 flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
                  <div className="flex items-center w-full md:w-auto">
                    <Input
                      placeholder="Search events..."
                      value={searchQuery}
                      onChange={(e) => setSearchQuery(e.target.value)}
                      className="max-w-sm mr-2"
                    />
                    <Button variant="ghost" size="icon">
                      <Search className="h-4 w-4" />
                    </Button>
                  </div>
                  <Button 
                    onClick={() => navigate('/admin-events/new')} 
                    className="w-full md:w-auto"
                  >
                    Add New Event
                  </Button>
                </div>
                
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                  {filteredEvents.length ? (
                    filteredEvents.map((event) => (
                      <Card key={event.id}>
                        <CardHeader>
                          <CardTitle className="text-lg">{event.title}</CardTitle>
                          <CardDescription>
                            {new Date(event.date).toLocaleDateString()} | {event.venue}
                          </CardDescription>
                        </CardHeader>
                        <CardContent>
                          <div className="flex justify-between mb-2">
                            <span className="text-sm text-muted-foreground">Price:</span>
                            <span>₹{event.price}</span>
                          </div>
                          <div className="flex justify-between mb-2">
                            <span className="text-sm text-muted-foreground">Available:</span>
                            <span>{event.tickets_available}</span>
                          </div>
                          <div className="flex justify-between">
                            <span className="text-sm text-muted-foreground">Status:</span>
                            <Badge 
                              variant="outline" 
                              className={
                                event.status === 'available' 
                                  ? 'bg-green-500 text-white' 
                                  : 'bg-red-500 text-white'
                              }
                            >
                              {event.status}
                            </Badge>
                          </div>
                        </CardContent>
                        <CardFooter className="flex justify-between">
                          <Button 
                            variant="outline" 
                      size="sm"
                            onClick={() => navigate(`/events/${event.id}`)}
                          >
                            <Eye className="h-4 w-4 mr-1" />
                            View
                          </Button>
                          <Button 
                            variant="outline" 
                      size="sm"
                            onClick={() => navigate(`/admin/events/edit/${event.id}`)}
                          >
                            <Edit className="h-4 w-4 mr-1" />
                            Edit
                          </Button>
                          <Button 
                            variant="outline" 
                      size="sm"
                            className="text-red-500 hover:text-red-700"
                          >
                            <Trash2 className="h-4 w-4 mr-1" />
                            Delete
                          </Button>
                        </CardFooter>
                      </Card>
                    ))
                  ) : (
                    <div className="col-span-full text-center p-8">
                      <p>No events found. Try a different search or add a new event.</p>
                    </div>
                  )}
                </div>
                
                <Pagination className="mt-8">
                  <PaginationContent>
                    <PaginationItem>
                      <PaginationPrevious href="#" />
                    </PaginationItem>
                    <PaginationItem>
                      <PaginationLink href="#" isActive>1</PaginationLink>
                    </PaginationItem>
                    <PaginationItem>
                      <PaginationLink href="#">2</PaginationLink>
                    </PaginationItem>
                    <PaginationItem>
                      <PaginationLink href="#">3</PaginationLink>
                    </PaginationItem>
                    <PaginationItem>
                      <PaginationNext href="#" />
                    </PaginationItem>
                  </PaginationContent>
                </Pagination>
              </TabsContent>
              
              <TabsContent value="bookings">
                <div className="mb-6 flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
                  <div className="flex items-center w-full md:w-auto">
                    <Select 
                      value={bookingFilter} 
                      onValueChange={setBookingFilter}
                    >
                      <SelectTrigger className="w-[180px]">
                        <SelectValue placeholder="Filter by status" />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="all">All Bookings</SelectItem>
                        <SelectItem value="pending">Pending</SelectItem>
                        <SelectItem value="confirmed">Confirmed</SelectItem>
                        <SelectItem value="cancelled">Cancelled</SelectItem>
                      </SelectContent>
                    </Select>
                    <Input
                      placeholder="Search bookings..."
                      className="max-w-sm ml-2"
                    />
                    <Button variant="ghost" size="icon">
                      <Search className="h-4 w-4" />
                    </Button>
                  </div>
                  <Button 
                    variant="outline" 
                    onClick={() => navigate(0)} 
                    className="w-full md:w-auto"
                  >
                    Refresh
                  </Button>
                </div>
                
                <Card>
                  <CardContent className="p-0">
                    <Table>
                      <TableHeader>
                        <TableRow>
                          <TableHead>Booking ID</TableHead>
                          <TableHead>Customer</TableHead>
                          <TableHead>Event</TableHead>
                          <TableHead>Date</TableHead>
                          <TableHead>Amount</TableHead>
                          <TableHead>Status</TableHead>
                          <TableHead>Actions</TableHead>
                        </TableRow>
                      </TableHeader>
                      <TableBody>
                        {analyticsData?.recent_bookings?.length ? (
                          analyticsData.recent_bookings.map((booking) => (
                            <TableRow key={booking.id || booking.booking_id}>
                              <TableCell className="font-medium">{booking.booking_id}</TableCell>
                              <TableCell>{booking.customer_info?.name}</TableCell>
                              <TableCell>Event #{booking.event_id}</TableCell>
                              <TableCell>{new Date(booking.created_at).toLocaleDateString()}</TableCell>
                              <TableCell>₹{booking.total_amount}</TableCell>
                              <TableCell>
                                <Badge 
                                  variant="outline" 
                                  className={`${getStatusBadgeColor(booking.status)} text-white`}
                                >
                                  {booking.status}
                                </Badge>
                              </TableCell>
                              <TableCell>
                                <div className="flex space-x-2">
                                  <Button size="sm" variant="outline">
                                    Details
                                  </Button>
                                  {booking.status === 'pending' && (
                                    <Button size="sm" variant="outline">
                                      Verify
                                    </Button>
                                  )}
                                </div>
                              </TableCell>
                            </TableRow>
                          ))
                        ) : (
                          <TableRow>
                            <TableCell colSpan={7} className="text-center">No bookings found</TableCell>
                          </TableRow>
                        )}
                      </TableBody>
                    </Table>
                  </CardContent>
                </Card>
                
                <Pagination className="mt-8">
                  <PaginationContent>
                    <PaginationItem>
                      <PaginationPrevious href="#" />
                    </PaginationItem>
                    <PaginationItem>
                      <PaginationLink href="#" isActive>1</PaginationLink>
                    </PaginationItem>
                    <PaginationItem>
                      <PaginationLink href="#">2</PaginationLink>
                    </PaginationItem>
                    <PaginationItem>
                      <PaginationLink href="#">3</PaginationLink>
                    </PaginationItem>
                    <PaginationItem>
                      <PaginationNext href="#" />
                    </PaginationItem>
                  </PaginationContent>
                </Pagination>
              </TabsContent>
              
              <TabsContent value="payments">
                <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                  <div>
                    <Card>
                      <CardHeader>
                        <CardTitle>UPI Payment Settings</CardTitle>
                        <CardDescription>Manage your UPI payment details</CardDescription>
                      </CardHeader>
                      <CardContent>
                        <p className="mb-4">Configure your UPI payment settings to receive payments from customers.</p>
                        <Button onClick={() => navigate('/admin-upi')}>
                          Manage UPI Settings
                        </Button>
                      </CardContent>
                    </Card>

                    <Card className="mt-6">
                      <CardHeader>
                        <CardTitle>Payment Maintenance</CardTitle>
                        <CardDescription>Cleanup expired bookings</CardDescription>
                </CardHeader>
                <CardContent>
                        <p className="mb-4">Run maintenance tasks to clean up expired bookings and release inventory.</p>
                        <Button 
                          variant="outline" 
                          onClick={() => {
                            api.cleanupExpiredBookings(adminToken || '')
                              .then(response => {
                                toast({
                                  title: "Cleanup successful",
                                  description: `Released ${response.expired_count} expired bookings and updated ${response.inventory_updated} event inventories.`
                                });
                              })
                              .catch(error => {
                                toast({
                                  title: "Cleanup failed",
                                  description: error.message,
                                  variant: "destructive"
                                });
                              });
                          }}
                        >
                          Cleanup Expired Bookings
                        </Button>
                      </CardContent>
                    </Card>
                  </div>
                  
                  <div>
                    <Card>
                      <CardHeader>
                        <CardTitle>Payment Metrics</CardTitle>
                        <CardDescription>View payment performance</CardDescription>
                      </CardHeader>
                      <CardContent>
                        <PaymentMetrics adminToken={adminToken} />
                      </CardContent>
                    </Card>
                  </div>
                </div>
              </TabsContent>
              
              <TabsContent value="users">
                <Card>
                  <CardHeader>
                    <CardTitle>User Management</CardTitle>
                    <CardDescription>Manage your users and admins</CardDescription>
                  </CardHeader>
                  <CardContent>
                    <p>This feature is under development. Please check back later.</p>
                </CardContent>
              </Card>
            </TabsContent>

              <TabsContent value="settings">
                <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              <Card>
                <CardHeader>
                      <CardTitle>Admin Settings</CardTitle>
                      <CardDescription>Manage your admin account and preferences</CardDescription>
                </CardHeader>
                <CardContent>
                      <div className="space-y-4">
                        <div>
                          <h3 className="font-medium mb-2">Admin Token</h3>
                          <p className="text-sm text-muted-foreground mb-2">
                            Your admin token is used to authenticate with the API. Keep it secure.
                          </p>
                          <div className="flex">
                            <Input type="password" value="••••••••••••••••" readOnly className="rounded-r-none" />
                            <Button variant="secondary" className="rounded-l-none">
                              Reset
                            </Button>
                          </div>
                        </div>
                  </div>
                </CardContent>
              </Card>

              <Card>
                <CardHeader>
                      <CardTitle>System Settings</CardTitle>
                      <CardDescription>Configure system-wide settings</CardDescription>
                </CardHeader>
                <CardContent>
                      <p>Configure system-wide settings such as email notifications, default currency, etc.</p>
                      <div className="mt-4">
                        <p className="text-sm text-muted-foreground mb-2">This feature is under development.</p>
                  </div>
                </CardContent>
              </Card>
                </div>
            </TabsContent>
          </Tabs>
        </div>
      </main>

      <Footer />
      </div>
    </AdminProtectedRoute>
  );
};

// Payment metrics component
const PaymentMetrics = ({ adminToken }: { adminToken: string | null }) => {
  const { data, isLoading, error, refetch } = useQuery({
    queryKey: ['paymentMetrics'],
    queryFn: () => api.getPaymentMetrics(adminToken || ''),
    enabled: !!adminToken,
    refetchInterval: 60000 // Refresh every minute
  });

  if (isLoading) {
    return (
      <div className="py-4 flex justify-center">
        <Loader2 className="h-8 w-8 animate-spin text-primary" />
      </div>
    );
  }

  if (error) {
    return (
      <div className="py-4 text-center">
        <p className="text-red-500 mb-2">Error loading payment metrics</p>
        <Button variant="outline" size="sm" onClick={() => refetch()}>
          Retry
        </Button>
      </div>
    );
  }

  if (!data) {
    return (
      <div className="py-4 text-center">
        <p className="text-gray-500">No payment data available</p>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="grid grid-cols-2 gap-4">
        <div className="bg-gray-50 p-4 rounded-md">
          <p className="text-sm text-gray-500 mb-1">Conversion Rate</p>
          <p className="text-2xl font-bold">{data.conversion_rate}%</p>
          <p className="text-xs text-gray-400">Of total bookings</p>
        </div>
        <div className="bg-gray-50 p-4 rounded-md">
          <p className="text-sm text-gray-500 mb-1">Avg. Payment Time</p>
          <p className="text-2xl font-bold">{data.avg_payment_time_minutes} min</p>
          <p className="text-xs text-gray-400">From booking to payment</p>
        </div>
      </div>

      <div className="grid grid-cols-3 gap-3">
        <div className="bg-blue-50 p-3 rounded-md text-center">
          <p className="text-xs text-gray-500">Confirmed</p>
          <p className="text-xl font-bold text-blue-600">{data.confirmed_payments}</p>
        </div>
        <div className="bg-yellow-50 p-3 rounded-md text-center">
          <p className="text-xs text-gray-500">Pending</p>
          <p className="text-xl font-bold text-yellow-600">{data.pending_payments}</p>
        </div>
        <div className="bg-red-50 p-3 rounded-md text-center">
          <p className="text-xs text-gray-500">Expired</p>
          <p className="text-xl font-bold text-red-600">{data.expired_payments}</p>
        </div>
      </div>

      <div>
        <h4 className="text-sm font-medium mb-2">Recent Payments</h4>
        <div className="border rounded-md overflow-hidden">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-3 py-2 text-left text-xs font-medium text-gray-500">Booking</th>
                <th className="px-3 py-2 text-left text-xs font-medium text-gray-500">Amount</th>
                <th className="px-3 py-2 text-left text-xs font-medium text-gray-500">Time</th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {data.recent_payments.map(payment => (
                <tr key={payment.id}>
                  <td className="px-3 py-2 text-xs">{payment.booking_id.slice(-6)}</td>
                  <td className="px-3 py-2 text-xs">₹{payment.total_amount}</td>
                  <td className="px-3 py-2 text-xs">
                    {payment.payment_verified_at ? 
                      new Date(payment.payment_verified_at).toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'}) 
                      : '-'}
                  </td>
                </tr>
              ))}
              {data.recent_payments.length === 0 && (
                <tr>
                  <td colSpan={3} className="px-3 py-4 text-sm text-center text-gray-500">
                    No recent payments
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>

      <div className="flex justify-end">
        <Button variant="ghost" size="sm" onClick={() => refetch()}>
          <RefreshCw className="h-3 w-3 mr-2" />
          Refresh
        </Button>
      </div>
    </div>
  );
};

export default AdminDashboard;
