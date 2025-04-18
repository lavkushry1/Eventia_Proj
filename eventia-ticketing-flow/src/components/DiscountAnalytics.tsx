import React from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { BarChart, LineChart, DoughnutChart } from '@/components/Charts';
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

  const discountDistributionData = metrics ? {
    labels: ['Active', 'Inactive'],
    values: [metrics.activeDiscounts, metrics.totalDiscounts - metrics.activeDiscounts],
  } : { labels: [], values: [] };

  const timeSeriesData = timeframeData ? {
    labels: timeframeData.labels,
    values: timeframeData.redemptions,
  } : { labels: [], values: [] };

  if (loading) {
    return <DiscountAnalyticsSkeleton />;
  }

  return (
    <Tabs defaultValue="usage" className="w-full">
      <TabsList className="grid w-full grid-cols-4">
        <TabsTrigger value="usage">Usage</TabsTrigger>
        <TabsTrigger value="revenue">Revenue</TabsTrigger>
        <TabsTrigger value="distribution">Distribution</TabsTrigger>
        <TabsTrigger value="trends">Trends</TabsTrigger>
      </TabsList>
      
      <TabsContent value="usage" className="space-y-4">
        <Card>
          <CardHeader>
            <CardTitle>Discount Usage</CardTitle>
            <CardDescription>Number of times each discount code has been used</CardDescription>
          </CardHeader>
          <CardContent>
            <BarChart labels={usageChartData.labels} values={usageChartData.values} />
          </CardContent>
        </Card>
      </TabsContent>
      
      <TabsContent value="revenue" className="space-y-4">
        <Card>
          <CardHeader>
            <CardTitle>Revenue by Discount</CardTitle>
            <CardDescription>Revenue generated from each discount code</CardDescription>
          </CardHeader>
          <CardContent>
            <BarChart labels={revenueChartData.labels} values={revenueChartData.values} />
          </CardContent>
        </Card>
      </TabsContent>
      
      <TabsContent value="distribution" className="space-y-4">
        <Card>
          <CardHeader>
            <CardTitle>Discount Status Distribution</CardTitle>
            <CardDescription>Active vs Inactive discount codes</CardDescription>
          </CardHeader>
          <CardContent>
            <DoughnutChart labels={discountDistributionData.labels} values={discountDistributionData.values} />
          </CardContent>
        </Card>
      </TabsContent>
      
      <TabsContent value="trends" className="space-y-4">
        <Card>
          <CardHeader>
            <CardTitle>Usage Trends</CardTitle>
            <CardDescription>Discount usage over time</CardDescription>
          </CardHeader>
          <CardContent>
            <LineChart labels={timeSeriesData.labels} values={timeSeriesData.values} />
          </CardContent>
        </Card>
      </TabsContent>
    </Tabs>
  );
};

// Loading skeleton for the analytics dashboard
const DiscountAnalyticsSkeleton: React.FC = () => {
  return (
    <div className="space-y-4">
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        {[1, 2, 3, 4].map((i) => (
          <Card key={i}>
            <CardContent className="pt-4">
              <Skeleton className="h-4 w-24 mb-2" />
              <Skeleton className="h-8 w-16" />
            </CardContent>
          </Card>
        ))}
      </div>
      
      <Card>
        <CardHeader>
          <Skeleton className="h-5 w-48" />
        </CardHeader>
        <CardContent>
          <Skeleton className="h-[200px] w-full" />
        </CardContent>
      </Card>
      
      <Card>
        <CardHeader>
          <Skeleton className="h-5 w-48" />
        </CardHeader>
        <CardContent>
          <Skeleton className="h-[200px] w-full" />
        </CardContent>
      </Card>
    </div>
  );
};
