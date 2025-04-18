"use client";

import React, { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import axios from 'axios';
import { Plus } from 'lucide-react';
import { toast } from '@/hooks/use-toast';
import { Button } from '@/components/ui/button';
import DiscountList from '@/components/admin/DiscountList';
import DiscountForm from '@/components/admin/DiscountForm';
import { AlertDialog, AlertDialogContent, AlertDialogDescription, AlertDialogFooter, AlertDialogHeader, AlertDialogTitle } from '@/components/ui/alert-dialog';
import DeleteConfirmDialog from '@/components/admin/DeleteConfirmDialog';
import PageHeader from '@/components/admin/PageHeader';
import { z } from 'zod';

interface Event {
  _id: string;
  name: string;
}

interface Discount {
  _id: string;
  discount_code: string;
  discount_type: 'percentage' | 'fixed';
  value: number;
  applicable_events: string[];
  valid_from: string;
  valid_till: string;
  max_uses: number;
  used_count: number;
  active: boolean;
  created_at: string;
  updated_at: string;
}

interface DiscountFormData {
  discount_code: string;
  discount_type: 'percentage' | 'fixed';
  value: number;
  applicable_events: string[];
  valid_from: Date;
  valid_till: Date;
  max_uses: number;
  active: boolean;
}

const AdminDiscountManagement = () => {
  const router = useRouter();
  
  // State variables
  const [discounts, setDiscounts] = useState<Discount[]>([]);
  const [events, setEvents] = useState<Event[]>([]);
  const [selectedDiscount, setSelectedDiscount] = useState<Discount | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [isCreateFormOpen, setIsCreateFormOpen] = useState(false);
  const [isDeleteDialogOpen, setIsDeleteDialogOpen] = useState(false);
  const [discountToDelete, setDiscountToDelete] = useState<string | null>(null);

  // Fetch discounts and events on component mount
  useEffect(() => {
    fetchDiscounts();
    fetchEvents();
  }, []);

  // Fetch all discounts
  const fetchDiscounts = async () => {
    try {
      setIsLoading(true);
      const response = await axios.get('/api/admin/discounts');
      setDiscounts(response.data.discounts);
    } catch (error) {
      console.error('Error fetching discounts:', error);
      toast({
        title: 'Error',
        description: 'Failed to fetch discounts',
        variant: 'destructive',
      });
    } finally {
      setIsLoading(false);
    }
  };

  // Fetch all events for the discount form
  const fetchEvents = async () => {
    try {
      const response = await axios.get('/api/admin/events');
      setEvents(response.data.events);
    } catch (error) {
      console.error('Error fetching events:', error);
      toast({
        title: 'Error',
        description: 'Failed to fetch events',
        variant: 'destructive',
      });
    }
  };

  // Handle create/update discount submission
  const handleDiscountSubmit = async (formData: DiscountFormData) => {
    try {
      setIsLoading(true);
      
      // Format dates for API
      const apiData = {
        ...formData,
        valid_from: formData.valid_from.toISOString(),
        valid_till: formData.valid_till.toISOString(),
      };
      
      if (selectedDiscount) {
        // Update existing discount
        await axios.put(`/api/admin/discounts/${selectedDiscount._id}`, apiData);
        toast({
          title: 'Success',
          description: `Discount code ${formData.discount_code} updated successfully`,
        });
      } else {
        // Create new discount
        await axios.post('/api/admin/discounts', apiData);
        toast({
          title: 'Success',
          description: `Discount code ${formData.discount_code} created successfully`,
        });
      }
      
      // Refresh discounts list and reset form
      fetchDiscounts();
      handleCancelForm();
    } catch (error: any) {
      console.error('Error saving discount:', error);
      toast({
        title: 'Error',
        description: error.response?.data?.message || 'Failed to save discount',
        variant: 'destructive',
      });
    } finally {
      setIsLoading(false);
    }
  };

  // Handle discount deletion
  const handleDeleteDiscount = async () => {
    if (!discountToDelete) return;
    
    try {
      setIsLoading(true);
      await axios.delete(`/api/admin/discounts/${discountToDelete}`);
      
      toast({
        title: 'Success',
        description: 'Discount deleted successfully',
      });
      
      fetchDiscounts();
      setIsDeleteDialogOpen(false);
      setDiscountToDelete(null);
    } catch (error) {
      console.error('Error deleting discount:', error);
      toast({
        title: 'Error',
        description: 'Failed to delete discount',
        variant: 'destructive',
      });
    } finally {
      setIsLoading(false);
    }
  };

  // Handle discount status toggle (active/inactive)
  const handleToggleDiscountStatus = async (discountId: string, currentStatus: boolean) => {
    try {
      setIsLoading(true);
      await axios.patch(`/api/admin/discounts/${discountId}/toggle`, {
        active: !currentStatus
      });
      
      toast({
        title: 'Success',
        description: `Discount ${currentStatus ? 'deactivated' : 'activated'} successfully`,
      });
      
      fetchDiscounts();
    } catch (error) {
      console.error('Error toggling discount status:', error);
      toast({
        title: 'Error',
        description: 'Failed to update discount status',
        variant: 'destructive',
      });
    } finally {
      setIsLoading(false);
    }
  };

  // Open edit form with selected discount
  const handleEditDiscount = (discount: Discount) => {
    setSelectedDiscount(discount);
    setIsCreateFormOpen(true);
  };

  // Open delete confirmation dialog
  const handleDeleteConfirmation = (discountId: string) => {
    setDiscountToDelete(discountId);
    setIsDeleteDialogOpen(true);
  };

  // Cancel form and reset state
  const handleCancelForm = () => {
    setIsCreateFormOpen(false);
    setSelectedDiscount(null);
  };

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

  return (
    <div className="container py-8">
      <PageHeader 
        title="Discount Management"
        description="Create and manage discount codes for events"
      >
        <Button onClick={() => setIsCreateFormOpen(true)} className="gap-2">
          <Plus className="h-4 w-4" />
          Create Discount
        </Button>
      </PageHeader>

      {/* Discount List */}
      <div className="mt-8">
        <DiscountList
          discounts={discounts}
          onEdit={handleEditDiscount}
          onDelete={handleDeleteConfirmation}
          onToggleStatus={handleToggleDiscountStatus}
          isLoading={isLoading}
        />
      </div>

      {/* Discount Form */}
      {isCreateFormOpen && (
        <div className="fixed inset-0 flex items-center justify-center bg-black/50 z-50 p-4">
          <div className="bg-white dark:bg-slate-950 p-6 rounded-lg shadow-lg w-full max-w-4xl max-h-[90vh] overflow-y-auto">
            <DiscountForm
              events={events}
              discount={selectedDiscount || undefined}
              onSubmit={handleDiscountSubmit}
              onCancel={handleCancelForm}
              isLoading={isLoading}
            />
          </div>
        </div>
      )}

      {/* Delete Confirmation Dialog */}
      <DeleteConfirmDialog
        isOpen={isDeleteDialogOpen}
        onClose={() => setIsDeleteDialogOpen(false)}
        onConfirm={handleDeleteDiscount}
        title="Delete Discount"
        description="Are you sure you want to delete this discount code? This action cannot be undone."
        isLoading={isLoading}
      />
    </div>
  );
};

export default AdminDiscountManagement; 