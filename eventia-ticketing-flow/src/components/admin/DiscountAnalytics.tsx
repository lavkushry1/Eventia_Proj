import React from 'react';
import { 
  Card, 
  CardContent, 
  CardDescription, 
  CardHeader, 
  CardTitle 
} from '@/components/ui/card';
import { 
  Table, 
  TableBody, 
  TableCaption, 
  TableCell, 
  TableHead, 
  TableHeader, 
  TableRow 
} from '@/components/ui/table';
import { Badge } from '@/components/ui/badge';
import { Skeleton } from '@/components/ui/skeleton';
import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert';
import { Clock, AlertTriangle, BarChart3, TrendingUp, Users } from 'lucide-react';

interface DiscountSummary {
  total_discounts: number;
  active_discounts: number;
  total_uses: number;
  avg_uses_per_discount: number;
}

interface Discount {
  _id: string;
  discount_code: string;
  discount_type: 'percentage' | 'fixed';
  value: number;
  used_count: number;
  max_uses: number;
  valid_till: string;
  active: boolean;
}

interface DiscountAnalyticsProps {
  analytics: {
    summary: DiscountSummary;
    top_discounts: Discount[];
    expiring_soon: Discount[];
  } | null | undefined;
  isLoading: boolean;
}

const DiscountAnalytics: React.FC<DiscountAnalyticsProps> = ({
  analytics,
  isLoading = false
}) => {
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
  
  // Calculate days until expiry
  const getDaysRemaining = (validTill: string): number => {
    const now = new Date();
    const expiryDate = new Date(validTill);
    const diffTime = expiryDate.getTime() - now.getTime();
    return Math.ceil(diffTime / (1000 * 60 * 60 * 24));
  };

  return (
    <div className="space-y-6">
      {/* Summary Cards */}
      <div className="grid grid-cols-1 gap-4 md:grid-cols-4">
        {isLoading ? (
          <>
            {[...Array(4)].map((_, i) => (
              <Skeleton key={i} className="h-28 w-full" />
            ))}
          </>
        ) : (
          <>
            <Card>
              <CardHeader className="p-4 pb-2">
                <CardTitle className="text-sm font-medium text-muted-foreground">
                  Total Discounts
                </CardTitle>
              </CardHeader>
              <CardContent className="p-4 pt-0">
                <div className="text-2xl font-bold">
                  {analytics?.summary?.total_discounts || 0}
                </div>
                <p className="text-xs text-muted-foreground mt-1">
                  {analytics?.summary?.active_discounts || 0} active discounts
                </p>
              </CardContent>
            </Card>
            
            <Card>
              <CardHeader className="p-4 pb-2">
                <CardTitle className="text-sm font-medium text-muted-foreground">
                  Total Uses
                </CardTitle>
              </CardHeader>
              <CardContent className="p-4 pt-0">
                <div className="text-2xl font-bold">
                  {analytics?.summary?.total_uses || 0}
                </div>
                <p className="text-xs text-muted-foreground mt-1">
                  Total discount code applications
                </p>
              </CardContent>
            </Card>
            
            <Card>
              <CardHeader className="p-4 pb-2">
                <CardTitle className="text-sm font-medium text-muted-foreground">
                  Usage Rate
                </CardTitle>
              </CardHeader>
              <CardContent className="p-4 pt-0">
                <div className="text-2xl font-bold">
                  {analytics?.summary?.avg_uses_per_discount?.toFixed(1) || 0}
                </div>
                <p className="text-xs text-muted-foreground mt-1">
                  Average uses per discount
                </p>
              </CardContent>
            </Card>
            
            <Card>
              <CardHeader className="p-4 pb-2">
                <CardTitle className="text-sm font-medium text-muted-foreground">
                  Utilization
                </CardTitle>
              </CardHeader>
              <CardContent className="p-4 pt-0">
                {analytics?.summary?.total_discounts ? (
                  <div className="text-2xl font-bold">
                    {((analytics?.summary?.active_discounts / analytics?.summary?.total_discounts) * 100).toFixed(0)}%
                  </div>
                ) : (
                  <div className="text-2xl font-bold">0%</div>
                )}
                <p className="text-xs text-muted-foreground mt-1">
                  Active discounts percentage
                </p>
              </CardContent>
            </Card>
          </>
        )}
      </div>
      
      <div className="grid grid-cols-1 gap-6 md:grid-cols-2">
        {/* Top Used Discounts */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center">
              <TrendingUp className="h-5 w-5 mr-2" />
              Most Used Discounts
            </CardTitle>
            <CardDescription>
              Discounts with highest usage
            </CardDescription>
          </CardHeader>
          <CardContent>
            {isLoading ? (
              <div className="space-y-2">
                {[...Array(3)].map((_, i) => (
                  <Skeleton key={i} className="h-12 w-full" />
                ))}
              </div>
            ) : analytics?.top_discounts?.length ? (
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>Code</TableHead>
                    <TableHead>Type</TableHead>
                    <TableHead>Used</TableHead>
                    <TableHead>Status</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {(analytics.top_discounts || []).slice(0, 5).map((discount) => (
                    <TableRow key={discount._id}>
                      <TableCell className="font-mono font-medium">
                        {discount.discount_code}
                      </TableCell>
                      <TableCell>
                        {discount.discount_type === 'percentage' 
                          ? `${discount.value}%` 
                          : `₹${discount.value}`
                        }
                      </TableCell>
                      <TableCell>
                        <div className="flex items-center">
                          <span className="font-medium">{discount.used_count}</span>
                          <span className="text-muted-foreground ml-1">
                            / {discount.max_uses}
                          </span>
                          <div className="w-16 bg-gray-200 rounded-full h-1.5 ml-2">
                            <div 
                              className="bg-primary h-1.5 rounded-full" 
                              style={{ width: `${(discount.used_count / discount.max_uses) * 100}%` }}
                            />
                          </div>
                        </div>
                      </TableCell>
                      <TableCell>
                        {discount.active ? (
                          <Badge variant="outline" className="bg-green-50 text-green-700 border-green-300">
                            Active
                          </Badge>
                        ) : (
                          <Badge variant="outline" className="bg-gray-50 text-gray-700 border-gray-300">
                            Inactive
                          </Badge>
                        )}
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            ) : (
              <div className="text-center py-6 text-muted-foreground">
                No discount usage data available
              </div>
            )}
          </CardContent>
        </Card>

        {/* Soon to Expire Discounts */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center">
              <Clock className="h-5 w-5 mr-2" />
              Expiring Soon
            </CardTitle>
            <CardDescription>
              Active discounts expiring in the next 7 days
            </CardDescription>
          </CardHeader>
          <CardContent>
            {isLoading ? (
              <div className="space-y-2">
                {[...Array(3)].map((_, i) => (
                  <Skeleton key={i} className="h-12 w-full" />
                ))}
              </div>
            ) : analytics?.expiring_soon?.length ? (
              <div className="space-y-3">
                {(analytics.expiring_soon || []).map((discount) => {
                  const daysRemaining = getDaysRemaining(discount.valid_till);
                  return (
                    <Alert key={discount._id} className={
                      daysRemaining <= 1 ? "border-red-200 bg-red-50" :
                      daysRemaining <= 3 ? "border-amber-200 bg-amber-50" :
                      "border-blue-200 bg-blue-50"
                    }>
                      <AlertTriangle className={
                        daysRemaining <= 1 ? "h-4 w-4 text-red-500" :
                        daysRemaining <= 3 ? "h-4 w-4 text-amber-500" :
                        "h-4 w-4 text-blue-500"
                      } />
                      <div className="ml-3">
                        <AlertTitle className="text-sm font-medium flex items-center justify-between">
                          <span className="font-mono">{discount.discount_code}</span>
                          <Badge variant={
                            daysRemaining <= 1 ? "destructive" : "outline"
                          } className={
                            daysRemaining <= 3 && daysRemaining > 1 ? "border-amber-300 bg-amber-100 text-amber-800" :
                            daysRemaining > 3 ? "border-blue-300 bg-blue-100 text-blue-800" : ""
                          }>
                            {daysRemaining <= 0 
                              ? "Expiring today" 
                              : daysRemaining === 1 
                                ? "Expires tomorrow" 
                                : `Expires in ${daysRemaining} days`
                            }
                          </Badge>
                        </AlertTitle>
                        <AlertDescription className="text-xs mt-1">
                          Expires on {formatDate(discount.valid_till)} • {discount.used_count} uses out of {discount.max_uses}
                        </AlertDescription>
                      </div>
                    </Alert>
                  );
                })}
              </div>
            ) : (
              <div className="text-center py-6 text-muted-foreground">
                No discounts expiring soon
              </div>
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  );
};

export default DiscountAnalytics; 