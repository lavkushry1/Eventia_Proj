import React, { useState } from 'react';
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
  Card, 
  CardContent, 
  CardDescription, 
  CardHeader, 
  CardTitle 
} from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Switch } from '@/components/ui/switch';
import { Input } from '@/components/ui/input';
import { 
  DropdownMenu, 
  DropdownMenuContent, 
  DropdownMenuItem, 
  DropdownMenuLabel, 
  DropdownMenuSeparator, 
  DropdownMenuTrigger 
} from '@/components/ui/dropdown-menu';
import { 
  Edit, 
  Trash2, 
  MoreVertical, 
  Search, 
  Calendar, 
  Tag, 
  Percent, 
  DollarSign, 
  Clock, 
  Info, 
  Filter,
  ToggleLeft,
  ToggleRight
} from 'lucide-react';
import { Skeleton } from '@/components/ui/skeleton';
import { format } from 'date-fns';

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
  updated_at?: string;
}

interface DiscountListProps {
  discounts: Discount[];
  isLoading: boolean;
  onEdit: (discount: Discount) => void;
  onDelete: (code: string) => void;
  onToggle: (code: string) => void;
}

const DiscountList: React.FC<DiscountListProps> = ({
  discounts = [],
  isLoading = false,
  onEdit,
  onDelete,
  onToggle
}) => {
  const [searchTerm, setSearchTerm] = useState('');
  const [filterActive, setFilterActive] = useState<boolean | null>(null);

  // Filter discounts based on search term and active filter
  const filteredDiscounts = discounts.filter(discount => {
    const matchesSearch = 
      discount.discount_code.toLowerCase().includes(searchTerm.toLowerCase());
    
    const matchesActiveFilter = 
      filterActive === null || discount.active === filterActive;
    
    return matchesSearch && matchesActiveFilter;
  });

  // Helper function to format dates
  const formatDate = (dateString: string) => {
    return format(new Date(dateString), 'MMM dd, yyyy');
  };

  // Calculate usage percentage
  const calculateUsage = (used: number, max: number) => {
    if (max === 0) return "∞"; // If unlimited uses
    return `${used}/${max} (${Math.round((used / max) * 100)}%)`;
  };

  // Get discount badge variant based on status
  const getStatusBadge = (discount: Discount) => {
    const now = new Date();
    const validFrom = new Date(discount.valid_from);
    const validTill = new Date(discount.valid_till);
    
    if (!discount.active) {
      return <Badge variant="outline" className="bg-gray-100">Inactive</Badge>;
    } else if (now < validFrom) {
      return <Badge variant="outline" className="bg-blue-100">Scheduled</Badge>;
    } else if (now > validTill) {
      return <Badge variant="outline" className="bg-red-100">Expired</Badge>;
    } else if (discount.max_uses > 0 && discount.used_count >= discount.max_uses) {
      return <Badge variant="outline" className="bg-amber-100">Exhausted</Badge>;
    } else {
      return <Badge variant="outline" className="bg-green-100">Active</Badge>;
    }
  };

  if (isLoading) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>Discount Codes</CardTitle>
          <CardDescription>Manage your discount codes</CardDescription>
        </CardHeader>
        <CardContent>
          <Skeleton className="h-[300px] w-full" />
        </CardContent>
      </Card>
    );
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle>Discount Codes</CardTitle>
        <CardDescription>
          Manage your discount codes for events
        </CardDescription>
      </CardHeader>
      <CardContent>
        <div className="mb-4 flex flex-col space-y-2 sm:flex-row sm:space-y-0 sm:space-x-2">
          <div className="relative flex-1">
            <Search className="absolute left-2 top-2.5 h-4 w-4 text-muted-foreground" />
            <Input
              placeholder="Search by code..."
              className="pl-8"
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
            />
          </div>
          <DropdownMenu>
            <DropdownMenuTrigger asChild>
              <Button variant="outline" className="w-full sm:w-auto">
                <Filter className="mr-2 h-4 w-4" />
                Filter
              </Button>
            </DropdownMenuTrigger>
            <DropdownMenuContent>
              <DropdownMenuLabel>Status Filter</DropdownMenuLabel>
              <DropdownMenuSeparator />
              <DropdownMenuItem onClick={() => setFilterActive(null)}>
                All
              </DropdownMenuItem>
              <DropdownMenuItem onClick={() => setFilterActive(true)}>
                Active Only
              </DropdownMenuItem>
              <DropdownMenuItem onClick={() => setFilterActive(false)}>
                Inactive Only
              </DropdownMenuItem>
            </DropdownMenuContent>
          </DropdownMenu>
        </div>

        <Table>
          <TableHeader>
            <TableRow>
              <TableHead>Code</TableHead>
              <TableHead>Type</TableHead>
              <TableHead>Value</TableHead>
              <TableHead>Valid Period</TableHead>
              <TableHead>Usage</TableHead>
              <TableHead>Status</TableHead>
              <TableHead className="text-right">Actions</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {discounts.length === 0 ? (
              <TableRow>
                <TableCell colSpan={7} className="text-center py-6">
                  No discount codes found. Create your first discount code!
                </TableCell>
              </TableRow>
            ) : (
              filteredDiscounts.map((discount) => (
                <TableRow key={discount._id}>
                  <TableCell className="font-medium">{discount.discount_code}</TableCell>
                  <TableCell>
                    <div className="flex items-center">
                      {discount.discount_type === 'percentage' ? (
                        <Percent className="h-4 w-4 mr-1" />
                      ) : (
                        <DollarSign className="h-4 w-4 mr-1" />
                      )}
                      {discount.discount_type === 'percentage' ? 'Percentage' : 'Fixed'}
                    </div>
                  </TableCell>
                  <TableCell>
                    {discount.discount_type === 'percentage' ? `${discount.value}%` : `₹${discount.value}`}
                  </TableCell>
                  <TableCell>
                    {formatDate(discount.valid_from)} to {formatDate(discount.valid_till)}
                  </TableCell>
                  <TableCell>
                    {calculateUsage(discount.used_count, discount.max_uses)}
                  </TableCell>
                  <TableCell>
                    {getStatusBadge(discount)}
                  </TableCell>
                  <TableCell className="text-right">
                    <div className="flex justify-end gap-2">
                      <Button variant="outline" size="sm" onClick={() => onEdit(discount)}>
                        <Edit className="h-4 w-4" />
                        <span className="sr-only">Edit</span>
                      </Button>
                      <Button variant="outline" size="sm" onClick={() => onDelete(discount.discount_code)}>
                        <Trash2 className="h-4 w-4" />
                        <span className="sr-only">Delete</span>
                      </Button>
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={() => onToggle(discount.discount_code)}
                      >
                        {discount.active ? (
                          <ToggleRight className="h-4 w-4" />
                        ) : (
                          <ToggleLeft className="h-4 w-4" />
                        )}
                        <span className="sr-only">
                          {discount.active ? 'Deactivate' : 'Activate'}
                        </span>
                      </Button>
                    </div>
                  </TableCell>
                </TableRow>
              ))
            )}
          </TableBody>
        </Table>
      </CardContent>
    </Card>
  );
};

export default DiscountList; 