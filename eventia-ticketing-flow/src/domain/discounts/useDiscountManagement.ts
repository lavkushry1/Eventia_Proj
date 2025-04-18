/**
 * Discount Management Hook
 * Centralizes all discount management business logic in the domain layer
 */
import { useState, useEffect, useCallback } from 'react';
import { z } from 'zod';
import { toast } from '@/hooks/use-toast';
import { api } from '@/lib/api';

// Type definitions
export interface Discount {
  _id: string;
  discount_code: string;
  discount_type: 'percentage' | 'fixed';
  discount_value: number;
  max_uses: number;
  current_uses: number;
  event_id: string | null;
  active: boolean;
  created_at: string;
  expires_at: string | null;
}

export interface Event {
  _id: string;
  name: string;
}

export interface DiscountFormData {
  discount_code: string;
  discount_type: 'percentage' | 'fixed';
  discount_value: number;
  max_uses: number;
  event_id: string | null;
  active: boolean;
  expires_at: string | null;
}

// Input validation schema
export const discountSchema = z.object({
  discount_code: z.string().min(3, 'Code must be at least 3 characters').max(20, 'Code must be less than 20 characters'),
  discount_type: z.enum(['percentage', 'fixed']),
  discount_value: z.number().min(1, 'Value must be at least 1'),
  max_uses: z.number().min(1, 'Max uses must be at least 1'),
  event_id: z.string().nullable(),
  active: z.boolean(),
  expires_at: z.string().nullable(),
});

/**
 * Custom hook for managing discounts
 * Provides state and operations for discount management
 */
export function useDiscountManagement() {
  // State
  const [discounts, setDiscounts] = useState<Discount[]>([]);
  const [events, setEvents] = useState<Event[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [isDialogOpen, setIsDialogOpen] = useState(false);
  const [currentDiscount, setCurrentDiscount] = useState<Discount | null>(null);
  const [isDeleteDialogOpen, setIsDeleteDialogOpen] = useState(false);
  const [deleteId, setDeleteId] = useState<string | null>(null);

  // Fetch discounts and events
  const fetchData = useCallback(async () => {
    setIsLoading(true);
    try {
      // Parallel data fetching
      const [discountsResponse, eventsResponse] = await Promise.all([
        api.get('/api/admin/discounts'),
        api.get('/api/admin/events')
      ]);

      setDiscounts(discountsResponse.data.discounts);
      setEvents(eventsResponse.data.events);
    } catch (error) {
      console.error('Failed to fetch data:', error);
      toast({
        title: 'Error',
        description: 'Failed to load discount data',
        variant: 'destructive'
      });
    } finally {
      setIsLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchData();
  }, [fetchData]);

  // Create/update a discount
  const saveDiscount = async (data: DiscountFormData) => {
    setIsSubmitting(true);
    try {
      if (currentDiscount) {
        // Update existing discount
        await api.put(`/api/admin/discounts/${currentDiscount._id}`, data);
        toast({
          title: 'Success',
          description: 'Discount updated successfully'
        });
      } else {
        // Create new discount
        await api.post('/api/admin/discounts', data);
        toast({
          title: 'Success',
          description: 'Discount created successfully'
        });
      }
      
      setIsDialogOpen(false);
      setCurrentDiscount(null);
      fetchData();
    } catch (error) {
      console.error('Failed to save discount:', error);
      toast({
        title: 'Error',
        description: 'Failed to save discount',
        variant: 'destructive'
      });
    } finally {
      setIsSubmitting(false);
    }
  };

  // Delete a discount
  const deleteDiscount = async (discountId: string) => {
    try {
      await api.delete(`/api/admin/discounts/${discountId}`);
      toast({
        title: 'Success',
        description: 'Discount deleted successfully'
      });
      fetchData();
    } catch (error) {
      console.error('Failed to delete discount:', error);
      toast({
        title: 'Error',
        description: 'Failed to delete discount',
        variant: 'destructive'
      });
    } finally {
      setIsDeleteDialogOpen(false);
      setDeleteId(null);
    }
  };

  // Toggle discount active state
  const toggleDiscountState = async (discountId: string) => {
    try {
      const discount = discounts.find(d => d.discount_code === discountId);
      if (!discount) return;

      await api.patch(`/api/admin/discounts/${discount._id}/toggle`);
      toast({
        title: 'Success',
        description: `Discount ${discount.active ? 'deactivated' : 'activated'} successfully`
      });
      fetchData();
    } catch (error) {
      console.error('Failed to toggle discount state:', error);
      toast({
        title: 'Error',
        description: 'Failed to update discount state',
        variant: 'destructive'
      });
    }
  };

  // UI state handlers
  const openCreateDialog = () => {
    setCurrentDiscount(null);
    setIsDialogOpen(true);
  };

  const openEditDialog = (discountCode: string) => {
    const discount = discounts.find(d => d.discount_code === discountCode);
    if (discount) {
      setCurrentDiscount(discount);
      setIsDialogOpen(true);
    }
  };

  const openDeleteDialog = (discountCode: string) => {
    setDeleteId(discountCode);
    setIsDeleteDialogOpen(true);
  };

  return {
    // State
    discounts,
    events,
    isLoading,
    isSubmitting,
    isDialogOpen,
    currentDiscount,
    isDeleteDialogOpen,
    deleteId,
    
    // Actions
    fetchData,
    saveDiscount,
    deleteDiscount,
    toggleDiscountState,
    openCreateDialog,
    openEditDialog,
    openDeleteDialog,
    
    // UI state methods
    setIsDialogOpen,
    setIsDeleteDialogOpen
  };
}
