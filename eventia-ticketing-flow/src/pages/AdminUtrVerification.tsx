
import React, { useState } from 'react';
import Navbar from '@/components/layout/Navbar';
import Footer from '@/components/layout/Footer';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table';
import { Badge } from '@/components/ui/badge';
import { Search, CheckCircle, XCircle, Truck, AlertCircle, ArrowDownAZ, ArrowUpAZ, FileText } from 'lucide-react';
import { toast } from '@/hooks/use-toast';

// Mock data for UTR verifications
const utrData = [
  {
    id: 'UTR123456',
    customerName: 'Amit Sharma',
    email: 'amit.sharma@example.com',
    phone: '9876543210',
    address: '123 Main Street, Mumbai, Maharashtra 400001',
    amount: 4500,
    status: 'pending',
    date: '2023-05-15T10:30:00Z',
    eventName: 'IPL: MI vs CSK',
    ticketCategory: 'Premium',
    quantity: 2
  },
  {
    id: 'UTR123457',
    customerName: 'Priya Patel',
    email: 'priya.patel@example.com',
    phone: '9876543211',
    address: '456 Park Avenue, Delhi, Delhi 110001',
    amount: 3000,
    status: 'verified',
    date: '2023-05-14T14:45:00Z',
    eventName: 'IPL: RCB vs KKR',
    ticketCategory: 'General',
    quantity: 3
  },
  {
    id: 'UTR123458',
    customerName: 'Rahul Verma',
    email: 'rahul.verma@example.com',
    phone: '9876543212',
    address: '789 Lake View, Bangalore, Karnataka 560001',
    amount: 6000,
    status: 'dispatched',
    date: '2023-05-13T09:15:00Z',
    eventName: 'Music Festival',
    ticketCategory: 'VIP',
    quantity: 2
  },
  {
    id: 'UTR123459',
    customerName: 'Sneha Desai',
    email: 'sneha.desai@example.com',
    phone: '9876543213',
    address: '101 River Road, Chennai, Tamil Nadu 600001',
    amount: 2500,
    status: 'pending',
    date: '2023-05-16T11:20:00Z',
    eventName: 'Comedy Night',
    ticketCategory: 'Standard',
    quantity: 5
  },
  {
    id: 'UTR123460',
    customerName: 'Vikram Singh',
    email: 'vikram.singh@example.com',
    phone: '9876543214',
    address: '202 Hill View, Hyderabad, Telangana 500001',
    amount: 8000,
    status: 'rejected',
    date: '2023-05-12T16:10:00Z',
    eventName: 'IPL: DC vs PBKS',
    ticketCategory: 'Premium',
    quantity: 4
  }
];

const AdminUtrVerification = () => {
  const [filter, setFilter] = useState('all');
  const [searchTerm, setSearchTerm] = useState('');
  const [sortDirection, setSortDirection] = useState<'asc' | 'desc'>('desc');
  const [selectedUtr, setSelectedUtr] = useState<any>(null);
  
  // Filter and sort UTRs
  const filteredUTRs = utrData
    .filter(utr => {
      if (filter !== 'all' && utr.status !== filter) return false;
      
      const searchLower = searchTerm.toLowerCase();
      return (
        utr.id.toLowerCase().includes(searchLower) ||
        utr.customerName.toLowerCase().includes(searchLower) ||
        utr.email.toLowerCase().includes(searchLower) ||
        utr.eventName.toLowerCase().includes(searchLower)
      );
    })
    .sort((a, b) => {
      const dateA = new Date(a.date).getTime();
      const dateB = new Date(b.date).getTime();
      return sortDirection === 'desc' ? dateB - dateA : dateA - dateB;
    });
  
  const handleVerifyUtr = () => {
    if (!selectedUtr) return;
    
    // In a real app, this would call an API to update the UTR status
    toast({
      title: "UTR Verified",
      description: `UTR ${selectedUtr.id} has been verified successfully.`,
    });
    
    // Update the selected UTR's status (in a real app, this would be handled by reloading data from API)
    setSelectedUtr({
      ...selectedUtr,
      status: 'verified'
    });
  };
  
  const handleRejectUtr = () => {
    if (!selectedUtr) return;
    
    toast({
      title: "UTR Rejected",
      description: `UTR ${selectedUtr.id} has been marked as rejected.`,
      variant: "destructive"
    });
    
    setSelectedUtr({
      ...selectedUtr,
      status: 'rejected'
    });
  };
  
  const handleDispatchTicket = () => {
    if (!selectedUtr) return;
    
    toast({
      title: "Ticket Dispatched",
      description: `Tickets for UTR ${selectedUtr.id} have been dispatched.`,
    });
    
    setSelectedUtr({
      ...selectedUtr,
      status: 'dispatched'
    });
  };
  
  const getStatusBadge = (status: string) => {
    switch (status) {
      case 'pending':
        return <Badge variant="outline" className="bg-yellow-100 text-yellow-800">Pending</Badge>;
      case 'verified':
        return <Badge variant="outline" className="bg-blue-100 text-blue-800">Verified</Badge>;
      case 'dispatched':
        return <Badge variant="outline" className="bg-green-100 text-green-800">Dispatched</Badge>;
      case 'rejected':
        return <Badge variant="outline" className="bg-red-100 text-red-800">Rejected</Badge>;
      default:
        return <Badge variant="outline">Unknown</Badge>;
    }
  };
  
  return (
    <div className="flex min-h-screen flex-col">
      <Navbar />

      <main className="flex-grow bg-gray-50 pt-16 pb-12">
        <div className="container mx-auto px-4">
          <div className="mb-6">
            <h1 className="text-3xl font-bold text-gray-900">UTR Verification & Ticket Dispatch</h1>
            <p className="text-gray-600 mt-1">Verify payments and dispatch tickets to customers</p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div className="md:col-span-2">
              <Card>
                <CardHeader className="pb-2">
                  <div className="flex items-center justify-between">
                    <CardTitle>UTR Submissions</CardTitle>
                    <div className="flex items-center space-x-2">
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={() => setSortDirection(sortDirection === 'desc' ? 'asc' : 'desc')}
                        className="text-gray-500"
                      >
                        {sortDirection === 'desc' ? (
                          <ArrowDownAZ className="h-4 w-4" />
                        ) : (
                          <ArrowUpAZ className="h-4 w-4" />
                        )}
                      </Button>
                    </div>
                  </div>
                  <CardDescription>Manage customer payments and ticket delivery</CardDescription>
                  
                  <div className="mt-4 flex flex-col sm:flex-row gap-4">
                    <div className="relative flex-grow">
                      <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 h-4 w-4" />
                      <Input
                        placeholder="Search by UTR, name, email..."
                        className="pl-10"
                        value={searchTerm}
                        onChange={(e) => setSearchTerm(e.target.value)}
                      />
                    </div>
                    
                    <Tabs defaultValue="all" className="w-auto" onValueChange={setFilter}>
                      <TabsList>
                        <TabsTrigger value="all">All</TabsTrigger>
                        <TabsTrigger value="pending">Pending</TabsTrigger>
                        <TabsTrigger value="verified">Verified</TabsTrigger>
                        <TabsTrigger value="dispatched">Dispatched</TabsTrigger>
                        <TabsTrigger value="rejected">Rejected</TabsTrigger>
                      </TabsList>
                    </Tabs>
                  </div>
                </CardHeader>
                <CardContent>
                  <Table>
                    <TableHeader>
                      <TableRow>
                        <TableHead>UTR ID</TableHead>
                        <TableHead>Customer</TableHead>
                        <TableHead>Event</TableHead>
                        <TableHead>Amount</TableHead>
                        <TableHead>Status</TableHead>
                      </TableRow>
                    </TableHeader>
                    <TableBody>
                      {filteredUTRs.length > 0 ? (
                        filteredUTRs.map((utr) => (
                          <TableRow 
                            key={utr.id}
                            className={`cursor-pointer hover:bg-gray-50 ${selectedUtr?.id === utr.id ? 'bg-blue-50' : ''}`}
                            onClick={() => setSelectedUtr(utr)}
                          >
                            <TableCell className="font-medium">{utr.id}</TableCell>
                            <TableCell>{utr.customerName}</TableCell>
                            <TableCell>{utr.eventName}</TableCell>
                            <TableCell>₹{utr.amount}</TableCell>
                            <TableCell>{getStatusBadge(utr.status)}</TableCell>
                          </TableRow>
                        ))
                      ) : (
                        <TableRow>
                          <TableCell colSpan={5} className="text-center py-4 text-gray-500">
                            No UTR submissions found
                          </TableCell>
                        </TableRow>
                      )}
                    </TableBody>
                  </Table>
                </CardContent>
              </Card>
            </div>
            
            <div>
              {selectedUtr ? (
                <Card>
                  <CardHeader>
                    <CardTitle>UTR Details</CardTitle>
                    <CardDescription>UTR ID: {selectedUtr.id}</CardDescription>
                  </CardHeader>
                  <CardContent className="space-y-4">
                    <div>
                      <h3 className="text-sm font-medium text-gray-500">Customer Information</h3>
                      <div className="mt-2 space-y-1">
                        <p className="text-sm">{selectedUtr.customerName}</p>
                        <p className="text-sm text-gray-500">{selectedUtr.email}</p>
                        <p className="text-sm text-gray-500">{selectedUtr.phone}</p>
                      </div>
                    </div>
                    
                    <div>
                      <h3 className="text-sm font-medium text-gray-500">Delivery Address</h3>
                      <p className="text-sm mt-2">{selectedUtr.address}</p>
                    </div>
                    
                    <div>
                      <h3 className="text-sm font-medium text-gray-500">Ticket Details</h3>
                      <div className="mt-2 space-y-1">
                        <p className="text-sm"><span className="font-medium">Event:</span> {selectedUtr.eventName}</p>
                        <p className="text-sm"><span className="font-medium">Category:</span> {selectedUtr.ticketCategory}</p>
                        <p className="text-sm"><span className="font-medium">Quantity:</span> {selectedUtr.quantity}</p>
                        <p className="text-sm"><span className="font-medium">Amount:</span> ₹{selectedUtr.amount}</p>
                      </div>
                    </div>
                    
                    <div>
                      <h3 className="text-sm font-medium text-gray-500">Status</h3>
                      <div className="mt-2">
                        {getStatusBadge(selectedUtr.status)}
                      </div>
                    </div>
                    
                    <div className="pt-4 space-y-2">
                      {selectedUtr.status === 'pending' && (
                        <>
                          <Button onClick={handleVerifyUtr} className="w-full">
                            <CheckCircle className="mr-2 h-4 w-4" />
                            Verify Payment
                          </Button>
                          <Button onClick={handleRejectUtr} variant="destructive" className="w-full">
                            <XCircle className="mr-2 h-4 w-4" />
                            Reject Payment
                          </Button>
                        </>
                      )}
                      
                      {selectedUtr.status === 'verified' && (
                        <Button onClick={handleDispatchTicket} className="w-full">
                          <Truck className="mr-2 h-4 w-4" />
                          Dispatch Tickets
                        </Button>
                      )}
                      
                      {selectedUtr.status === 'rejected' && (
                        <div className="bg-red-50 p-3 rounded-md text-sm text-red-800 flex items-start">
                          <AlertCircle className="h-5 w-5 mr-2 flex-shrink-0 text-red-600" />
                          <p>This payment has been rejected. No further action is required.</p>
                        </div>
                      )}
                      
                      {selectedUtr.status === 'dispatched' && (
                        <div className="bg-green-50 p-3 rounded-md text-sm text-green-800 flex items-start">
                          <CheckCircle className="h-5 w-5 mr-2 flex-shrink-0 text-green-600" />
                          <p>Tickets have been dispatched to the customer. Delivery expected within 2 days.</p>
                        </div>
                      )}
                    </div>
                    
                    <Button variant="outline" className="w-full">
                      <FileText className="mr-2 h-4 w-4" />
                      Generate Invoice
                    </Button>
                  </CardContent>
                </Card>
              ) : (
                <Card>
                  <CardContent className="py-8 text-center text-gray-500">
                    <p>Select a UTR submission to view details</p>
                  </CardContent>
                </Card>
              )}
            </div>
          </div>
        </div>
      </main>

      <Footer />
    </div>
  );
};

export default AdminUtrVerification;
