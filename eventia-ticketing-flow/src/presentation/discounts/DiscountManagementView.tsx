/**
 * Discount Management UI Component
 * Pure presentation layer component that uses domain layer logic
 */
import React from 'react';
import { Plus, Loader2 } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import DiscountList from '@/components/admin/DiscountList';
import DiscountForm from '@/components/admin/DiscountForm';
import { useDiscountManagement, DiscountFormData } from '@/domain/discounts/useDiscountManagement';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle
} from '@/components/ui/dialog';
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle
} from '@/components/ui/alert-dialog';

export function DiscountManagementView() {
  const {
    discounts,
    events,
    isLoading,
    isSubmitting,
    isDialogOpen,
    currentDiscount,
    isDeleteDialogOpen,
    deleteId,
    saveDiscount,
    deleteDiscount,
    toggleDiscountState,
    openCreateDialog,
    openEditDialog,
    openDeleteDialog,
    setIsDialogOpen,
    setIsDeleteDialogOpen
  } = useDiscountManagement();

  const handleSaveDiscount = (data: DiscountFormData) => {
    saveDiscount(data);
  };

  const handleDelete = () => {
    if (deleteId) {
      deleteDiscount(deleteId);
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-2xl font-bold tracking-tight">Discount Management</h1>
        <Button onClick={openCreateDialog}>
          <Plus className="mr-2 h-4 w-4" />
          Create Discount
        </Button>
      </div>
      
      <Card>
        <CardHeader>
          <CardTitle>All Discounts</CardTitle>
        </CardHeader>
        <CardContent>
          {isLoading ? (
            <div className="flex justify-center items-center py-10">
              <Loader2 className="h-8 w-8 animate-spin text-muted-foreground" />
            </div>
          ) : (
            <DiscountList
              discounts={discounts}
              isLoading={isLoading}
              onEdit={openEditDialog}
              onDelete={openDeleteDialog}
              onToggle={toggleDiscountState}
            />
          )}
        </CardContent>
      </Card>

      {/* Create/Edit Discount Dialog */}
      <Dialog open={isDialogOpen} onOpenChange={setIsDialogOpen}>
        <DialogContent className="sm:max-w-[600px]">
          <DialogHeader>
            <DialogTitle>
              {currentDiscount ? 'Edit Discount' : 'Create Discount'}
            </DialogTitle>
            <DialogDescription>
              {currentDiscount
                ? 'Edit the discount details below and save your changes.'
                : 'Fill in the discount details and create a new discount code.'}
            </DialogDescription>
          </DialogHeader>
          <DiscountForm
            events={events}
            discount={currentDiscount}
            onSubmit={handleSaveDiscount}
            isSubmitting={isSubmitting}
          />
        </DialogContent>
      </Dialog>

      {/* Delete Confirmation Dialog */}
      <AlertDialog open={isDeleteDialogOpen} onOpenChange={setIsDeleteDialogOpen}>
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle>Are you sure?</AlertDialogTitle>
            <AlertDialogDescription>
              This action cannot be undone. This will permanently delete the discount code.
            </AlertDialogDescription>
          </AlertDialogHeader>
          <AlertDialogFooter>
            <AlertDialogCancel>Cancel</AlertDialogCancel>
            <AlertDialogAction onClick={handleDelete} className="bg-destructive text-destructive-foreground">
              Delete
            </AlertDialogAction>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>
    </div>
  );
}
