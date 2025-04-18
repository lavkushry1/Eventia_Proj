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
  Filter
} from 'lucide-react';
import { Skeleton } from '@/components/ui/skeleton';

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

  // Check if a discount is expired
  const isExpired = (validTill: string): boolean => {
    return new Date(validTill) < new Date();
  };

  // Format date for display
  const formatDate = (dateStr: string): string => {
    return new Date(dateStr).toLocaleString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

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

        {isLoading ? (
          <div className="space-y-2">
            {[...Array(5)].map((_, i) => (
              <Skeleton key={i} className="h-12 w-full" />
            ))}
          </div>
        ) : (
          <div className="overflow-x-auto">
            <Table>
              <TableCaption>List of discount codes</TableCaption>
              <TableHeader>
                <TableRow>
                  <TableHead>Code</TableHead>
                  <TableHead>Type</TableHead>
                  <TableHead>Value</TableHead>
                  <TableHead>Usage</TableHead>
                  <TableHead>Valid Period</TableHead>
                  <TableHead>Status</TableHead>
                  <TableHead className="text-right">Actions</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {filteredDiscounts.length === 0 ? (
                  <TableRow>
                    <TableCell colSpan={7} className="text-center py-6 text-muted-foreground">
                      No discount codes found
                    </TableCell>
                  </TableRow>
                ) : (
                  filteredDiscounts.map((discount) => {
                    const expired = isExpired(discount.valid_till);
                    
                    return (
                      <TableRow key={discount._id}>
                        <TableCell className="font-mono font-medium">
                          {discount.discount_code}
                        </TableCell>
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
                          {discount.discount_type === 'percentage'
                            ? `${discount.value}%`
                            : `₹${discount.value}`
                          }
                        </TableCell>
                        <TableCell>
                          <div className="text-sm">
                            <span className="font-medium">{discount.used_count}</span>
                            <span className="text-muted-foreground"> / {discount.max_uses}</span>
                          </div>
                          {discount.used_count > 0 && (
                            <div className="w-full bg-gray-200 rounded-full h-1.5 mt-1">
                              <div 
                                className="bg-primary h-1.5 rounded-full" 
                                style={{ width: `${(discount.used_count / discount.max_uses) * 100}%` }}
                              />
                            </div>
                          )}
                        </TableCell>
                        <TableCell className="text-sm">
                          <div className="flex flex-col">
                            <span>
                              <Calendar className="inline-block h-3 w-3 mr-1" />
                              {formatDate(discount.valid_from)}
                            </span>
                            <span>
                              <Clock className="inline-block h-3 w-3 mr-1" />
                              {formatDate(discount.valid_till)}
                            </span>
                          </div>
                        </TableCell>
                        <TableCell>
                          <div className="flex flex-col space-y-1">
                            <Switch
                              checked={discount.active}
                              onCheckedChange={() => onToggle(discount.discount_code)}
                              className="data-[state=checked]:bg-green-500"
                            />
                            <div className="flex space-x-1">
                              {expired && (
                                <Badge variant="destructive" className="text-xs">Expired</Badge>
                              )}
                              {discount.active ? (
                                <Badge variant="outline" className="bg-green-50 text-green-700 border-green-300 text-xs">
                                  Active
                                </Badge>
                              ) : (
                                <Badge variant="outline" className="bg-gray-50 text-gray-700 border-gray-300 text-xs">
                                  Inactive
                                </Badge>
                              )}
                            </div>
                          </div>
                        </TableCell>
                        <TableCell className="text-right">
                          <DropdownMenu>
                            <DropdownMenuTrigger asChild>
                              <Button variant="ghost" className="h-8 w-8 p-0">
                                <span className="sr-only">Open menu</span>
                                <MoreVertical className="h-4 w-4" />
                              </Button>
                            </DropdownMenuTrigger>
                            <DropdownMenuContent align="end">
                              <DropdownMenuLabel>Actions</DropdownMenuLabel>
                              <DropdownMenuSeparator />
                              <DropdownMenuItem onClick={() => onEdit(discount)}>
                                <Edit className="mr-2 h-4 w-4" />
                                Edit
                              </DropdownMenuItem>
                              <DropdownMenuItem 
                                onClick={() => onToggle(discount.discount_code)}
                                className="flex items-center"
                              >
                                <Switch 
                                  checked={discount.active}
                                  className="mr-2 h-4 data-[state=checked]:bg-green-500"
                                />
                                {discount.active ? 'Deactivate' : 'Activate'}
                              </DropdownMenuItem>
                              <DropdownMenuSeparator />
                              <DropdownMenuItem 
                                onClick={() => onDelete(discount.discount_code)}
                                className="text-red-600 focus:text-red-600"
                              >
                                <Trash2 className="mr-2 h-4 w-4" />
                                Delete
                              </DropdownMenuItem>
                            </DropdownMenuContent>
                          </DropdownMenu>
                        </TableCell>
                      </TableRow>
                    );
                  })
                )}
              </TableBody>
            </Table>
          </div>
        )}
      </CardContent>
    </Card>
  );
};

export default DiscountList; 