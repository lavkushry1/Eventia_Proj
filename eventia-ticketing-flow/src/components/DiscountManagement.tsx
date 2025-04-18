// DiscountManagement.tsx
import React, { useState, useEffect } from 'react';
import { BarChart, LineChart } from './Charts';
import { DataTable } from './DataTable';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { 
  Dialog, 
  DialogContent, 
  DialogDescription, 
  DialogFooter, 
  DialogHeader, 
  DialogTitle,
  DialogTrigger
} from '@/components/ui/dialog';
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
import { Switch } from '@/components/ui/switch';
import { zodResolver } from '@hookform/resolvers/zod';
import { useForm } from 'react-hook-form';
import * as z from 'zod';
import { toast } from '@/hooks/use-toast';
import { AlertCircle, Plus, RefreshCw, Download, BarChart2, PieChart, ArrowUpRight } from 'lucide-react';
import { cn } from '@/lib/utils';
import axios from 'axios';

// Types
interface Discount {
  id: string;
  code: string;
  type: 'percentage' | 'fixed';
  value: number;
  maxUses: number;
  usedCount: number;
  minOrderAmount?: number;
  startDate: string;
  endDate: string;
  isActive: boolean;
  createdAt: string;
  events: string[];
}

interface DiscountAnalytics {
  totalDiscounts: number;
  activeDiscounts: number;
  totalSaved: number;
  redemptionRate: number;
  usageByDay: {
    labels: string[];
    values: number[];
  };
  discountsByType: {
    labels: string[];
    values: number[];
  };
  topDiscounts: {
    labels: string[];
    values: number[];
  };
}

// Form schema
const discountFormSchema = z.object({
  code: z.string().min(3, { message: "Discount code must be at least 3 characters." }),
  type: z.enum(['percentage', 'fixed']),
  value: z.number().min(0),
  maxUses: z.number().int().min(1),
  minOrderAmount: z.number().min(0).optional(),
  startDate: z.string(),
  endDate: z.string(),
  isActive: z.boolean().default(true),
  events: z.array(z.string()).optional(),
});

export const DiscountManagement: React.FC = () => {
  const [loading, setLoading] = useState(true);
  const [discounts, setDiscounts] = useState<Discount[]>([]);
  const [analytics, setAnalytics] = useState<DiscountAnalytics>({
    totalDiscounts: 0,
    activeDiscounts: 0,
    totalSaved: 0,
    redemptionRate: 0,
    usageByDay: { labels: [], values: [] },
    discountsByType: { labels: [], values: [] },
    topDiscounts: { labels: [], values: [] },
  });
  const [events, setEvents] = useState<{ id: string; name: string }[]>([]);
  const [bulkAmount, setBulkAmount] = useState('10');
  const [showAddDialog, setShowAddDialog] = useState(false);
  const [showBulkDialog, setShowBulkDialog] = useState(false);
  
  const form = useForm<z.infer<typeof discountFormSchema>>({
    resolver: zodResolver(discountFormSchema),
    defaultValues: {
      code: '',
      type: 'percentage',
      value: 10,
      maxUses: 100,
      minOrderAmount: 0,
      startDate: new Date().toISOString().split('T')[0],
      endDate: new Date(Date.now() + 30 * 24 * 60 * 60 * 1000).toISOString().split('T')[0],
      isActive: true,
      events: [],
    },
  });

  // Load discounts and analytics
  useEffect(() => {
    const fetchData = async () => {
      setLoading(true);
      try {
        // In a real app, these would be actual API calls
        const [discountsRes, analyticsRes, eventsRes] = await Promise.all([
          axios.get('/api/admin/discounts'),
          axios.get('/api/admin/discounts/analytics'),
          axios.get('/api/admin/events/list')
        ]);
        
        setDiscounts(discountsRes.data);
        setAnalytics(analyticsRes.data);
        setEvents(eventsRes.data);
      } catch (error) {
        console.error('Error loading discount data:', error);
        toast({
          title: "Error loading data",
          description: "Could not load discount data. Please try again.",
          variant: "destructive",
        });
        
        // Fallback demo data
        setDiscounts([
          {
            id: '1',
            code: 'SUMMER2025',
            type: 'percentage',
            value: 20,
            maxUses: 100,
            usedCount: 45,
            startDate: '2025-05-01',
            endDate: '2025-08-31',
            isActive: true,
            createdAt: '2025-04-15',
            events: []
          },
          {
            id: '2',
            code: 'WELCOME10',
            type: 'percentage',
            value: 10,
            maxUses: 500,
            usedCount: 213,
            startDate: '2025-01-01',
            endDate: '2025-12-31',
            isActive: true,
            createdAt: '2025-01-01',
            events: []
          },
          {
            id: '3',
            code: 'FLASH25',
            type: 'percentage',
            value: 25,
            maxUses: 200,
            usedCount: 198,
            startDate: '2025-03-15',
            endDate: '2025-03-20',
            isActive: false,
            createdAt: '2025-03-10',
            events: ['1']
          },
          {
            id: '4',
            code: 'FIXED50',
            type: 'fixed',
            value: 50,
            maxUses: 300,
            usedCount: 87,
            minOrderAmount: 200,
            startDate: '2025-02-01',
            endDate: '2025-06-30',
            isActive: true,
            createdAt: '2025-01-25',
            events: []
          }
        ]);
        
        setAnalytics({
          totalDiscounts: 4,
          activeDiscounts: 3,
          totalSaved: 7834.50,
          redemptionRate: 35.8,
          usageByDay: {
            labels: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'],
            values: [23, 41, 30, 27, 45, 53, 38]
          },
          discountsByType: {
            labels: ['Percentage', 'Fixed Amount'],
            values: [3, 1]
          },
          topDiscounts: {
            labels: ['WELCOME10', 'SUMMER2025', 'FIXED50', 'FLASH25'],
            values: [213, 45, 87, 198]
          }
        });
        
        setEvents([
          { id: '1', name: 'Summer Music Festival' },
          { id: '2', name: 'Tech Conference 2025' },
          { id: '3', name: 'Charity Gala Dinner' }
        ]);
      } finally {
        setLoading(false);
      }
    };
    
    fetchData();
  }, []);

  // Submit handler for discount form
  const onSubmit = async (data: z.infer<typeof discountFormSchema>) => {
    try {
      // In a real app, this would be an actual API call
      // const response = await axios.post('/api/admin/discounts', data);
      
      // Mock successful response
      const newDiscount: Discount = {
        id: Math.random().toString(36).substring(2, 9),
        ...data,
        usedCount: 0,
        createdAt: new Date().toISOString(),
        events: data.events || []
      };
      
      setDiscounts([newDiscount, ...discounts]);
      setAnalytics({
        ...analytics,
        totalDiscounts: analytics.totalDiscounts + 1,
        activeDiscounts: data.isActive ? analytics.activeDiscounts + 1 : analytics.activeDiscounts
      });
      
      toast({
        title: "Discount created",
        description: `Discount code '${data.code}' has been created successfully.`,
      });
      
      setShowAddDialog(false);
      form.reset();
    } catch (error) {
      console.error('Error creating discount:', error);
      toast({
        title: "Error creating discount",
        description: "Could not create discount. Please try again.",
        variant: "destructive",
      });
    }
  };

  // Generate bulk discount codes
  const handleBulkGenerate = async () => {
    try {
      const amount = parseInt(bulkAmount, 10);
      
      // In a real app, this would be an actual API call
      // const response = await axios.post('/api/admin/discounts/bulk', {
      //   amount,
      //   ...form.getValues()
      // });
      
      // Mock successful response
      const bulkDiscounts: Discount[] = Array.from({ length: amount }, (_, i) => ({
        id: Math.random().toString(36).substring(2, 9),
        ...form.getValues(),
        code: `${form.getValues().code}${i + 1}`,
        usedCount: 0,
        createdAt: new Date().toISOString(),
        events: form.getValues().events || []
      }));
      
      setDiscounts([...bulkDiscounts, ...discounts]);
      setAnalytics({
        ...analytics,
        totalDiscounts: analytics.totalDiscounts + amount,
        activeDiscounts: form.getValues().isActive ? analytics.activeDiscounts + amount : analytics.activeDiscounts
      });
      
      toast({
        title: "Bulk discounts created",
        description: `${amount} discount codes have been generated successfully.`,
      });
      
      setShowBulkDialog(false);
    } catch (error) {
      console.error('Error generating bulk discounts:', error);
      toast({
        title: "Error generating discounts",
        description: "Could not generate bulk discount codes. Please try again.",
        variant: "destructive",
      });
    }
  };

  // Toggle discount active status
  const handleToggleActive = async (id: string, currentStatus: boolean) => {
    try {
      // In a real app, this would be an actual API call
      // await axios.patch(`/api/admin/discounts/${id}`, { isActive: !currentStatus });
      
      // Update local state
      const updatedDiscounts = discounts.map(discount => 
        discount.id === id ? { ...discount, isActive: !currentStatus } : discount
      );
      
      setDiscounts(updatedDiscounts);
      setAnalytics({
        ...analytics,
        activeDiscounts: currentStatus 
          ? analytics.activeDiscounts - 1 
          : analytics.activeDiscounts + 1
      });
      
      toast({
        title: `Discount ${currentStatus ? 'deactivated' : 'activated'}`,
        description: `The discount has been ${currentStatus ? 'deactivated' : 'activated'} successfully.`,
      });
    } catch (error) {
      console.error('Error toggling discount status:', error);
      toast({
        title: "Error updating discount",
        description: "Could not update discount status. Please try again.",
        variant: "destructive",
      });
    }
  };

  // Delete discount
  const handleDelete = async (id: string) => {
    if (!confirm('Are you sure you want to delete this discount code?')) return;
    
    try {
      // In a real app, this would be an actual API call
      // await axios.delete(`/api/admin/discounts/${id}`);
      
      const discountToDelete = discounts.find(d => d.id === id);
      const updatedDiscounts = discounts.filter(discount => discount.id !== id);
      
      setDiscounts(updatedDiscounts);
      if (discountToDelete?.isActive) {
        setAnalytics({
          ...analytics,
          totalDiscounts: analytics.totalDiscounts - 1,
          activeDiscounts: analytics.activeDiscounts - 1
        });
      } else {
        setAnalytics({
          ...analytics,
          totalDiscounts: analytics.totalDiscounts - 1
        });
      }
      
      toast({
        title: "Discount deleted",
        description: "The discount code has been deleted successfully.",
      });
    } catch (error) {
      console.error('Error deleting discount:', error);
      toast({
        title: "Error deleting discount",
        description: "Could not delete the discount code. Please try again.",
        variant: "destructive",
      });
    }
  };

  // Export discounts to CSV
  const handleExport = () => {
    const headers = ['Code', 'Type', 'Value', 'Max Uses', 'Used Count', 'Min Order', 'Start Date', 'End Date', 'Active'];
    const rows = discounts.map(d => [
      d.code,
      d.type,
      d.value.toString(),
      d.maxUses.toString(),
      d.usedCount.toString(),
      d.minOrderAmount?.toString() || '0',
      d.startDate,
      d.endDate,
      d.isActive ? 'Yes' : 'No'
    ]);
    
    const csvContent = [
      headers.join(','),
      ...rows.map(row => row.join(','))
    ].join('\n');
    
    const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.setAttribute('href', url);
    link.setAttribute('download', `eventia_discounts_${new Date().toISOString().split('T')[0]}.csv`);
    link.click();
  };

  // Format currency
  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat('en-IN', {
      style: 'currency',
      currency: 'INR'
    }).format(amount);
  };

  // Table columns definition
  const columns = [
    {
      accessorKey: 'code',
      header: 'Discount Code',
      cell: ({ row }) => <div className="font-medium">{row.getValue('code')}</div>,
    },
    {
      accessorKey: 'type',
      header: 'Type',
      cell: ({ row }) => (
        <div className="capitalize">
          {row.getValue('type') === 'percentage' ? 'Percentage' : 'Fixed Amount'}
        </div>
      ),
    },
    {
      accessorKey: 'value',
      header: 'Value',
      cell: ({ row }) => {
        const value = row.getValue('value') as number;
        const type = row.getValue('type') as string;
        return (
          <div>
            {type === 'percentage' ? `${value}%` : formatCurrency(value)}
          </div>
        );
      },
    },
    {
      accessorKey: 'usageRate',
      header: 'Usage',
      cell: ({ row }) => {
        const usedCount = row.original.usedCount as number;
        const maxUses = row.original.maxUses as number;
        const percentage = (usedCount / maxUses) * 100;
        
        return (
          <div className="flex items-center gap-2">
            <div className="w-24 h-2 bg-gray-200 rounded-full overflow-hidden">
              <div 
                className={cn(
                  "h-full rounded-full",
                  percentage > 90 ? "bg-red-500" : 
                  percentage > 60 ? "bg-amber-500" : "bg-green-500"
                )}
                style={{ width: `${percentage}%` }}
              />
            </div>
            <span className="text-xs text-gray-500">
              {usedCount}/{maxUses}
            </span>
          </div>
        );
      },
    },
    {
      accessorKey: 'startDate',
      header: 'Start Date',
      cell: ({ row }) => new Date(row.getValue('startDate')).toLocaleDateString(),
    },
    {
      accessorKey: 'endDate',
      header: 'End Date',
      cell: ({ row }) => new Date(row.getValue('endDate')).toLocaleDateString(),
    },
    {
      accessorKey: 'isActive',
      header: 'Status',
      cell: ({ row }) => {
        const isActive = row.getValue('isActive') as boolean;
        return (
          <div className="flex items-center">
            <div 
              className={cn(
                "h-2 w-2 rounded-full mr-2",
                isActive ? "bg-green-500" : "bg-gray-300"
              )}
            />
            <span>{isActive ? 'Active' : 'Inactive'}</span>
          </div>
        );
      },
    },
    {
      id: 'actions',
      header: 'Actions',
      cell: ({ row }) => {
        const discount = row.original;
        const isActive = discount.isActive as boolean;
        
        return (
          <div className="flex items-center gap-2">
            <Button
              variant="outline"
              size="sm"
              onClick={() => handleToggleActive(discount.id, isActive)}
            >
              {isActive ? 'Deactivate' : 'Activate'}
            </Button>
            <Button
              variant="destructive"
              size="sm"
              onClick={() => handleDelete(discount.id)}
            >
              Delete
            </Button>
          </div>
        );
      },
    },
  ];

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Discount Management</h1>
          <p className="text-muted-foreground">
            Create and manage discount codes for your events
          </p>
        </div>
        <div className="flex items-center gap-3">
          <Button
            onClick={handleExport}
            variant="outline"
            className="flex items-center gap-2"
          >
            <Download className="h-4 w-4" />
            Export
          </Button>
          <Dialog open={showAddDialog} onOpenChange={setShowAddDialog}>
            <DialogTrigger asChild>
              <Button className="flex items-center gap-2">
                <Plus className="h-4 w-4" />
                Add Discount
              </Button>
            </DialogTrigger>
            <DialogContent className="sm:max-w-[500px]">
              <DialogHeader>
                <DialogTitle>Create New Discount</DialogTitle>
                <DialogDescription>
                  Add a new discount code that customers can use during checkout.
                </DialogDescription>
              </DialogHeader>
              <Form {...form}>
                <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-4">
                  <FormField
                    control={form.control}
                    name="code"
                    render={({ field }) => (
                      <FormItem>
                        <FormLabel>Discount Code</FormLabel>
                        <FormControl>
                          <Input placeholder="SUMMER2025" {...field} />
                        </FormControl>
                        <FormDescription>
                          Code that customers will enter to apply the discount.
                        </FormDescription>
                        <FormMessage />
                      </FormItem>
                    )}
                  />
                  <div className="grid grid-cols-2 gap-4">
                    <FormField
                      control={form.control}
                      name="type"
                      render={({ field }) => (
                        <FormItem>
                          <FormLabel>Type</FormLabel>
                          <Select
                            onValueChange={field.onChange}
                            defaultValue={field.value}
                          >
                            <FormControl>
                              <SelectTrigger>
                                <SelectValue placeholder="Select type" />
                              </SelectTrigger>
                            </FormControl>
                            <SelectContent>
                              <SelectItem value="percentage">Percentage</SelectItem>
                              <SelectItem value="fixed">Fixed Amount</SelectItem>
                            </SelectContent>
                          </Select>
                          <FormMessage />
                        </FormItem>
                      )}
                    />
                    <FormField
                      control={form.control}
                      name="value"
                      render={({ field }) => (
                        <FormItem>
                          <FormLabel>Value</FormLabel>
                          <FormControl>
                            <Input 
                              type="number" 
                              {...field}
                              onChange={e => field.onChange(Number(e.target.value))}
                            />
                          </FormControl>
                          <FormMessage />
                        </FormItem>
                      )}
                    />
                  </div>
                  <div className="grid grid-cols-2 gap-4">
                    <FormField
                      control={form.control}
                      name="maxUses"
                      render={({ field }) => (
                        <FormItem>
                          <FormLabel>Maximum Uses</FormLabel>
                          <FormControl>
                            <Input 
                              type="number" 
                              {...field}
                              onChange={e => field.onChange(Number(e.target.value))}
                            />
                          </FormControl>
                          <FormMessage />
                        </FormItem>
                      )}
                    />
                    <FormField
                      control={form.control}
                      name="minOrderAmount"
                      render={({ field }) => (
                        <FormItem>
                          <FormLabel>Minimum Order Amount</FormLabel>
                          <FormControl>
                            <Input 
                              type="number" 
                              {...field}
                              onChange={e => field.onChange(Number(e.target.value))}
                            />
                          </FormControl>
                          <FormMessage />
                        </FormItem>
                      )}
                    />
                  </div>
                  <div className="grid grid-cols-2 gap-4">
                    <FormField
                      control={form.control}
                      name="startDate"
                      render={({ field }) => (
                        <FormItem>
                          <FormLabel>Start Date</FormLabel>
                          <FormControl>
                            <Input type="date" {...field} />
                          </FormControl>
                          <FormMessage />
                        </FormItem>
                      )}
                    />
                    <FormField
                      control={form.control}
                      name="endDate"
                      render={({ field }) => (
                        <FormItem>
                          <FormLabel>End Date</FormLabel>
                          <FormControl>
                            <Input type="date" {...field} />
                          </FormControl>
                          <FormMessage />
                        </FormItem>
                      )}
                    />
                  </div>
                  <FormField
                    control={form.control}
                    name="events"
                    render={({ field }) => (
                      <FormItem>
                        <FormLabel>Limit to Events (Optional)</FormLabel>
                        <Select
                          onValueChange={(value) => field.onChange([value])}
                        >
                          <FormControl>
                            <SelectTrigger>
                              <SelectValue placeholder="All events" />
                            </SelectTrigger>
                          </FormControl>
                          <SelectContent>
                            {events.map(event => (
                              <SelectItem key={event.id} value={event.id}>
                                {event.name}
                              </SelectItem>
                            ))}
                          </SelectContent>
                        </Select>
                        <FormDescription>
                          Leave empty to apply to all events
                        </FormDescription>
                        <FormMessage />
                      </FormItem>
                    )}
                  />
                  <FormField
                    control={form.control}
                    name="isActive"
                    render={({ field }) => (
                      <FormItem className="flex flex-row items-center justify-between rounded-lg border p-4">
                        <div className="space-y-0.5">
                          <FormLabel className="text-base">
                            Active
                          </FormLabel>
                          <FormDescription>
                            Enable this discount immediately
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
                  <DialogFooter className="mt-6">
                    <Button
                      type="button"
                      variant="outline"
                      onClick={() => {
                        setShowAddDialog(false);
                        setShowBulkDialog(true);
                      }}
                    >
                      Bulk Generate
                    </Button>
                    <Button type="submit">Create Discount</Button>
                  </DialogFooter>
                </form>
              </Form>
            </DialogContent>
          </Dialog>
          
          <Dialog open={showBulkDialog} onOpenChange={setShowBulkDialog}>
            <DialogContent className="sm:max-w-[500px]">
              <DialogHeader>
                <DialogTitle>Bulk Generate Discount Codes</DialogTitle>
                <DialogDescription>
                  Generate multiple discount codes with the same settings.
                </DialogDescription>
              </DialogHeader>
              <div className="space-y-4 py-4">
                <div className="space-y-2">
                  <Label htmlFor="bulk-amount">Number of Codes</Label>
                  <Input
                    id="bulk-amount"
                    type="number"
                    value={bulkAmount}
                    onChange={(e) => setBulkAmount(e.target.value)}
                    min="1"
                    max="100"
                  />
                  <p className="text-sm text-muted-foreground">
                    Each code will have a unique number appended to it.
                  </p>
                </div>
                <div className="bg-amber-50 border border-amber-200 rounded-md p-3 flex items-start">
                  <AlertCircle className="h-5 w-5 text-amber-500 mt-0.5 mr-2" />
                  <div>
                    <h4 className="text-sm font-medium text-amber-800">Important Note</h4>
                    <p className="text-xs text-amber-700 mt-1">
                      Using the pattern "{form.watch('code')}1", "{form.watch('code')}2", etc.
                      All settings from the discount form will be applied to these codes.
                    </p>
                  </div>
                </div>
              </div>
              <DialogFooter>
                <Button
                  type="button"
                  variant="outline" 
                  onClick={() => {
                    setShowBulkDialog(false);
                    setShowAddDialog(true);
                  }}
                >
                  Back
                </Button>
                <Button onClick={handleBulkGenerate}>Generate Codes</Button>
              </DialogFooter>
            </DialogContent>
          </Dialog>
        </div>
      </div>

      <div className="grid gap-4 grid-cols-1 md:grid-cols-2 lg:grid-cols-4">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Total Discounts</CardTitle>
            <BarChart2 className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{analytics.totalDiscounts}</div>
            <p className="text-xs text-muted-foreground">
              {analytics.activeDiscounts} active
            </p>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Total Savings</CardTitle>
            <ArrowUpRight className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{formatCurrency(analytics.totalSaved)}</div>
            <p className="text-xs text-muted-foreground">
              Across all discounts
            </p>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Redemption Rate</CardTitle>
            <RefreshCw className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{analytics.redemptionRate}%</div>
            <p className="text-xs text-muted-foreground">
              Of available discounts used
            </p>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Discount Types</CardTitle>
            <PieChart className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{analytics.discountsByType.values[0] || 0}</div>
            <p className="text-xs text-muted-foreground">
              Percentage discounts ({analytics.discountsByType.values[1] || 0} fixed)
            </p>
          </CardContent>
        </Card>
      </div>

      <Tabs defaultValue="all">
        <div className="flex justify-between items-center mb-4">
          <TabsList>
            <TabsTrigger value="all">All Discounts</TabsTrigger>
            <TabsTrigger value="analytics">Analytics</TabsTrigger>
          </TabsList>
        </div>
        
        <TabsContent value="all" className="space-y-4">
          <DataTable
            columns={columns}
            data={discounts}
            loading={loading}
            searchPlaceholder="Search discounts..."
            searchField="code"
          />
        </TabsContent>
        
        <TabsContent value="analytics" className="space-y-6">
          <div className="grid gap-6 grid-cols-1 lg:grid-cols-2">
            <Card>
              <CardHeader>
                <CardTitle>Usage By Day of Week</CardTitle>
                <CardDescription>
                  Number of discount redemptions by day
                </CardDescription>
              </CardHeader>
              <CardContent>
                <BarChart 
                  data={analytics.usageByDay}
                  height={300}
                  title="Redemptions"
                  color="rgba(99, 102, 241, 0.8)"
                />
              </CardContent>
            </Card>
            
            <Card>
              <CardHeader>
                <CardTitle>Top Performing Discounts</CardTitle>
                <CardDescription>
                  Most frequently used discount codes
                </CardDescription>
              </CardHeader>
              <CardContent>
                <BarChart 
                  data={analytics.topDiscounts}
                  height={300}
                  title="Uses"
                  color="rgba(16, 185, 129, 0.8)"
                />
              </CardContent>
            </Card>

            <Card className="lg:col-span-2">
              <CardHeader>
                <CardTitle>Monthly Discount Performance</CardTitle>
                <CardDescription>
                  Discount usage and savings over time
                </CardDescription>
              </CardHeader>
              <CardContent>
                <LineChart 
                  data={{
                    labels: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'],
                    values: [23, 45, 67, 78, 45, 90, 112, 134, 156, 143, 132, 167]
                  }}
                  height={300}
                  title="Monthly Redemptions"
                  color="rgba(245, 158, 11, 0.8)"
                />
              </CardContent>
            </Card>
          </div>
        </TabsContent>
      </Tabs>
    </div>
  );
}
