import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import axios from 'axios';
import { 
  Card, 
  CardContent, 
  CardDescription, 
  CardHeader, 
  CardTitle 
} from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { toast } from '@/hooks/use-toast';
import { api } from '@/lib/api';
import { Tag, PlusCircle, AlertTriangle, Clock, Calendar } from 'lucide-react';
import AdminLayout from '@/components/layout/AdminLayout';
import DiscountForm from '@/components/admin/DiscountForm';
import DiscountList from '@/components/admin/DiscountList';
import DiscountAnalytics from '@/components/admin/DiscountAnalytics';
import BulkDiscountGenerator from '@/components/admin/BulkDiscountGenerator';

// Fetch discounts from API
const fetchDiscounts = async () => {
  const response = await api.get('/discounts');
  return response.data;
};

// Fetch discount analytics from API
const fetchDiscountAnalytics = async () => {
  const response = await api.get('/discounts/analytics');
  return response.data;
};

// Fetch events for dropdown
const fetchEvents = async () => {
  const response = await api.get('/events');
  return response.data;
};

const AdminDiscountManagement = () => {
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const [activeTab, setActiveTab] = useState('discounts');
  const [isCreateModalOpen, setIsCreateModalOpen] = useState(false);
  const [selectedDiscount, setSelectedDiscount] = useState(null);

  // Get discounts
  const { 
    data: discounts, 
    isLoading: isLoadingDiscounts,
    error: discountsError 
  } = useQuery({
    queryKey: ['discounts'],
    queryFn: fetchDiscounts
  });

  // Get discount analytics
  const { 
    data: analytics, 
    isLoading: isLoadingAnalytics 
  } = useQuery({
    queryKey: ['discountAnalytics'],
    queryFn: fetchDiscountAnalytics
  });

  // Get events for dropdown
  const { 
    data: events 
  } = useQuery({
    queryKey: ['events'],
    queryFn: fetchEvents
  });

  // Create discount mutation
  const createDiscountMutation = useMutation({
    mutationFn: (data) => api.post('/discounts', data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['discounts'] });
      queryClient.invalidateQueries({ queryKey: ['discountAnalytics'] });
      toast({ title: "Success", description: "Discount created successfully" });
      setIsCreateModalOpen(false);
    },
    onError: (error) => {
      toast({ 
        title: "Error", 
        description: error.response?.data?.detail || "Failed to create discount", 
        variant: "destructive" 
      });
    }
  });

  // Update discount mutation
  const updateDiscountMutation = useMutation({
    mutationFn: ({ code, data }) => api.put(`/discounts/${code}`, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['discounts'] });
      queryClient.invalidateQueries({ queryKey: ['discountAnalytics'] });
      toast({ title: "Success", description: "Discount updated successfully" });
      setSelectedDiscount(null);
    },
    onError: (error) => {
      toast({ 
        title: "Error", 
        description: error.response?.data?.detail || "Failed to update discount", 
        variant: "destructive" 
      });
    }
  });

  // Delete discount mutation
  const deleteDiscountMutation = useMutation({
    mutationFn: (code) => api.delete(`/discounts/${code}`),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['discounts'] });
      queryClient.invalidateQueries({ queryKey: ['discountAnalytics'] });
      toast({ title: "Success", description: "Discount deleted successfully" });
    },
    onError: (error) => {
      toast({ 
        title: "Error", 
        description: error.response?.data?.detail || "Failed to delete discount", 
        variant: "destructive" 
      });
    }
  });

  // Toggle discount activation mutation
  const toggleDiscountMutation = useMutation({
    mutationFn: (code) => api.post(`/discounts/toggle/${code}`),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['discounts'] });
      queryClient.invalidateQueries({ queryKey: ['discountAnalytics'] });
      toast({ title: "Success", description: "Discount status toggled successfully" });
    },
    onError: (error) => {
      toast({ 
        title: "Error", 
        description: error.response?.data?.detail || "Failed to toggle discount", 
        variant: "destructive" 
      });
    }
  });

  // Create bulk discounts mutation
  const createBulkDiscountsMutation = useMutation({
    mutationFn: (data) => api.post('/discounts/bulk', data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['discounts'] });
      queryClient.invalidateQueries({ queryKey: ['discountAnalytics'] });
      toast({ title: "Success", description: "Bulk discounts created successfully" });
    },
    onError: (error) => {
      toast({ 
        title: "Error", 
        description: error.response?.data?.detail || "Failed to create bulk discounts", 
        variant: "destructive" 
      });
    }
  });

  const handleCreateDiscount = (discountData) => {
    createDiscountMutation.mutate(discountData);
  };

  const handleUpdateDiscount = (discountData) => {
    updateDiscountMutation.mutate({
      code: discountData.discount_code,
      data: discountData
    });
  };

  const handleDeleteDiscount = (code) => {
    if (window.confirm('Are you sure you want to delete this discount?')) {
      deleteDiscountMutation.mutate(code);
    }
  };

  const handleToggleDiscount = (code) => {
    toggleDiscountMutation.mutate(code);
  };

  const handleEditDiscount = (discount) => {
    setSelectedDiscount(discount);
    setIsCreateModalOpen(true);
  };

  const handleCreateBulkDiscounts = (bulkData) => {
    createBulkDiscountsMutation.mutate(bulkData);
  };

  return (
    <AdminLayout>
      <div className="container mx-auto py-8">
        <div className="flex justify-between items-center mb-6">
          <h1 className="text-3xl font-bold">Discount Management</h1>
          <Button onClick={() => {
            setSelectedDiscount(null);
            setIsCreateModalOpen(true);
          }}>
            <PlusCircle className="mr-2 h-4 w-4" />
            Create Discount
          </Button>
        </div>

        <Tabs value={activeTab} onValueChange={setActiveTab}>
          <TabsList className="grid w-full grid-cols-3">
            <TabsTrigger value="discounts">Discounts</TabsTrigger>
            <TabsTrigger value="bulk">Bulk Generation</TabsTrigger>
            <TabsTrigger value="analytics">Analytics</TabsTrigger>
          </TabsList>

          <TabsContent value="discounts" className="space-y-4 mt-6">
            <DiscountList 
              discounts={discounts || []}
              isLoading={isLoadingDiscounts}
              onEdit={handleEditDiscount}
              onDelete={handleDeleteDiscount}
              onToggle={handleToggleDiscount}
            />
          </TabsContent>

          <TabsContent value="bulk" className="space-y-4 mt-6">
            <BulkDiscountGenerator 
              events={events || []}
              onGenerate={handleCreateBulkDiscounts}
              isLoading={createBulkDiscountsMutation.isPending}
            />
          </TabsContent>

          <TabsContent value="analytics" className="space-y-4 mt-6">
            <DiscountAnalytics 
              analytics={analytics}
              isLoading={isLoadingAnalytics}
            />
          </TabsContent>
        </Tabs>

        {isCreateModalOpen && (
          <DiscountForm
            isOpen={isCreateModalOpen}
            onClose={() => {
              setIsCreateModalOpen(false);
              setSelectedDiscount(null);
            }}
            onSubmit={selectedDiscount ? handleUpdateDiscount : handleCreateDiscount}
            discount={selectedDiscount}
            events={events || []}
            isLoading={createDiscountMutation.isPending || updateDiscountMutation.isPending}
          />
        )}
      </div>
    </AdminLayout>
  );
};

export default AdminDiscountManagement; 