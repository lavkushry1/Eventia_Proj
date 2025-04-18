import React from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { BarChart, LineChart, DoughnutChart, HorizontalBarChart } from '@/components/Charts';
import { Skeleton } from '@/components/ui/skeleton';

// Sample data types for discount analytics
interface DiscountUsageData {
  discountCode: string;
  usageCount: number;
  revenue: number;
  savings: number;
  conversionRate: number;
}

interface DiscountMetrics {
  totalDiscounts: number;
  activeDiscounts: number;
  totalRedemptions: number;
  averageSavings: number;
  totalRevenue: number;
}

interface DiscountAnalyticsProps {
  usageData?: DiscountUsageData[];
  metrics?: DiscountMetrics;
  timeframeData?: {
    labels: string[];
    redemptions: number[];
    revenue: number[];
  };
  loading?: boolean;
}

export const DiscountAnalytics: React.FC<DiscountAnalyticsProps> = ({
  usageData = [],
  metrics,
  timeframeData,
  loading = false,
}) => {
  // Prepare chart data from the provided props
  const usageChartData = {
    labels: usageData.map(item => item.discountCode),
    values: usageData.map(item => item.usageCount),
  };

  const revenueChartData = {
    labels: usageData.map(item => item.discountCode),
    values: usageData.map(item => item.revenue),
  };

  const conversionChartData = {
    labels: usageData.map(item => item.discountCode),
    values: usageData.map(item => item.conversionRate * 100), // Convert to percentage
  };

  const discountDistributionData = metrics ? {
    labels: ['Active', 'Inactive'],
    values: [metrics.activeDiscounts, metrics.totalDiscounts - metrics.activeDiscounts],
  } : { labels: [], values: [] };

  const timeSeriesData = timeframeData ? {
    labels: timeframeData.labels,
    values: timeframeData.redemptions,
  } : { labels: [], values: [] };

  const revenueTimeSeriesData = timeframeData ? {
    labels: timeframeData.labels,
    values: timeframeData.revenue,
  } : { labels: [], values: [] };

  if (loading) {
    return <DiscountAnalyticsSkeleton />;
  }

  return (
    <div className="space-y-6">
      {/* Overview metrics */}
      {metrics && (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          <MetricCard 
            title="Total Discounts" 
            value={metrics.totalDiscounts.toString()} 
            description="Total number of discount codes" 
          />
          <MetricCard 
            title="Active Discounts" 
            value={metrics.activeDiscounts.toString()} 
            description="Currently active discount codes" 
          />
          <MetricCard 
            title="Total Redemptions" 
            value={metrics.totalRedemptions.toString()} 
            description="Times discounts were used" 
          />
          <MetricCard 
            title="Average Savings" 
            value={`₹${metrics.averageSavings.toFixed(2)}`} 
            description="Average amount saved per order" 
          />
        </div>
      )}

      {/* Charts row 1 */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <Card>
          <CardHeader>
            <CardTitle>Discount Usage Over Time</CardTitle>
            <CardDescription>Number of redemptions by time period</CardDescription>
          </CardHeader>
          <CardContent>
            {timeframeData && (
              <LineChart 
                data={timeSeriesData} 
                title="Redemptions" 
                color="rgba(99, 102, 241, 0.8)" 
              />
            )}
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Revenue Generated</CardTitle>
            <CardDescription>Revenue from orders using discounts</CardDescription>
          </CardHeader>
          <CardContent>
            {timeframeData && (
              <LineChart 
                data={revenueTimeSeriesData} 
                title="Revenue" 
                color="rgba(16, 185, 129, 0.8)" 
              />
            )}
          </CardContent>
        </Card>
      </div>

      {/* Charts row 2 */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <Card>
          <CardHeader>
            <CardTitle>Top Discount Codes by Usage</CardTitle>
            <CardDescription>Most frequently used discount codes</CardDescription>
          </CardHeader>
          <CardContent>
            {usageData.length > 0 && (
              <BarChart 
                data={usageChartData} 
                title="Usage Count" 
              />
            )}
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Discount Status Distribution</CardTitle>
            <CardDescription>Active vs. inactive discount codes</CardDescription>
          </CardHeader>
          <CardContent>
            {metrics && (
              <DoughnutChart 
                data={discountDistributionData} 
                title="Discount Status" 
              />
            )}
          </CardContent>
        </Card>
      </div>

      {/* Charts row 3 */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <Card>
          <CardHeader>
            <CardTitle>Conversion Rate by Discount</CardTitle>
            <CardDescription>Percentage of views resulting in redemption</CardDescription>
          </CardHeader>
          <CardContent>
            {usageData.length > 0 && (
              <HorizontalBarChart 
                data={conversionChartData} 
                title="Conversion %" 
                color="rgba(245, 158, 11, 0.8)" 
              />
            )}
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Revenue by Discount Code</CardTitle>
            <CardDescription>Total revenue generated per discount</CardDescription>
          </CardHeader>
          <CardContent>
            {usageData.length > 0 && (
              <BarChart 
                data={revenueChartData} 
                title="Revenue (₹)" 
                color="rgba(20, 184, 166, 0.8)" 
              />
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  );
};

// Helper component for individual metric cards
const MetricCard: React.FC<{ title: string; value: string; description: string }> = ({
  title,
  value,
  description,
}) => {
  return (
    <Card>
      <CardHeader className="pb-2">
        <CardTitle className="text-sm font-medium text-muted-foreground">{title}</CardTitle>
      </CardHeader>
      <CardContent>
        <div className="text-2xl font-bold">{value}</div>
        <p className="text-xs text-muted-foreground mt-1">{description}</p>
      </CardContent>
    </Card>
  );
};

// Loading skeleton for the analytics dashboard
const DiscountAnalyticsSkeleton: React.FC = () => {
  return (
    <div className="space-y-6">
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {[1, 2, 3, 4].map((i) => (
          <Card key={i}>
            <CardHeader className="pb-2">
              <Skeleton className="h-4 w-24" />
            </CardHeader>
            <CardContent>
              <Skeleton className="h-8 w-16 mb-1" />
              <Skeleton className="h-3 w-32" />
            </CardContent>
          </Card>
        ))}
      </div>

      {[1, 2, 3].map((row) => (
        <div key={row} className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {[1, 2].map((col) => (
            <Card key={`${row}-${col}`}>
              <CardHeader>
                <Skeleton className="h-5 w-48 mb-1" />
                <Skeleton className="h-4 w-64" />
              </CardHeader>
              <CardContent>
                <Skeleton className="h-[200px] w-full" />
              </CardContent>
            </Card>
          ))}
        </div>
      ))}
    </div>
  );
};
