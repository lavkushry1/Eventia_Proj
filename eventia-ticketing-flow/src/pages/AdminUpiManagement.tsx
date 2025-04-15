import React, { useState, useEffect } from 'react';
import Navbar from '@/components/layout/Navbar';
import Footer from '@/components/layout/Footer';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Form, FormField, FormItem, FormLabel, FormControl, FormMessage, FormDescription } from '@/components/ui/form';
import { Copy, CreditCard, Shield, CheckCircle2, RefreshCw, Loader2 } from 'lucide-react';
import { toast } from '@/hooks/use-toast';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import * as z from 'zod';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { api, ApiPaymentSettings, ApiUpdatePaymentSettingsRequest } from '@/lib/api';
import { useAdminAuth } from '@/hooks/use-admin-auth';
import { Skeleton } from '@/components/ui/skeleton';
import { QRCodeSVG } from 'qrcode.react';

// Form schema for UPI VPA validation
const upiSchema = z.object({
  merchantName: z.string().min(3, "Merchant name must be at least 3 characters"),
  vpa: z.string()
    .min(5, "UPI VPA must be at least 5 characters")
    .regex(/^[a-zA-Z0-9.\-_]+@[a-zA-Z]+$/, "Invalid UPI VPA format (e.g., example@bank)"),
  description: z.string().optional(),
  paymentMode: z.enum(['vpa', 'qr_image']).default('vpa')
});

type UpiFormValues = z.infer<typeof upiSchema>;

const AdminUpiManagement = () => {
  const [isCopied, setIsCopied] = useState(false);
  const { adminToken } = useAdminAuth();
  const queryClient = useQueryClient();
  const [qrImageFile, setQrImageFile] = useState<File | null>(null);
  const [qrImagePreview, setQrImagePreview] = useState<string | null>(null);
  
  // Query to fetch payment settings
  const { 
    data: paymentSettings, 
    isLoading, 
    error 
  } = useQuery({
    queryKey: ['paymentSettings'],
    queryFn: api.getPaymentSettings,
    staleTime: 1000 * 60 * 5, // 5 minutes
  });
  
  // Mutation to update payment settings
  const updateSettingsMutation = useMutation({
    mutationFn: (data: ApiUpdatePaymentSettingsRequest) => 
      api.updatePaymentSettings(adminToken || '', data),
    onSuccess: () => {
      toast({
        title: "UPI details updated",
        description: "Your UPI VPA has been successfully updated.",
      });
      queryClient.invalidateQueries({ queryKey: ['paymentSettings'] });
    },
    onError: (err: Error) => {
      toast({
        title: "Failed to update UPI details",
        description: err.message || "An error occurred while updating UPI details.",
        variant: "destructive"
      });
    }
  });
  
  const form = useForm<UpiFormValues>({
    resolver: zodResolver(upiSchema),
    defaultValues: {
      merchantName: '',
      vpa: '',
      description: '',
    }
  });
  
  // Update form with data from API
  useEffect(() => {
    if (paymentSettings) {
      form.reset({
        merchantName: paymentSettings.merchant_name,
        vpa: paymentSettings.vpa,
        description: paymentSettings.description,
        paymentMode: paymentSettings.payment_mode || 'vpa'
      });
      
      // Set QR image preview if available
      if (paymentSettings.qrImageUrl) {
        setQrImagePreview(paymentSettings.qrImageUrl);
      }
    }
  }, [paymentSettings, form]);

  const onSubmit = (data: UpiFormValues) => {
    if (!adminToken) {
      toast({
        title: "Authentication required",
        description: "Please log in as an admin to update UPI details.",
        variant: "destructive"
      });
      return;
    }
    
    // Format data for API
    const apiRequest: ApiUpdatePaymentSettingsRequest = {
      merchant_name: data.merchantName,
      vpa: data.vpa,
      description: data.description,
      payment_mode: data.paymentMode
    };
    
    // Add QR image if available
    if (qrImageFile && data.paymentMode === 'qr_image') {
      apiRequest.qr_image = qrImageFile;
    }
    
    // Submit to API
    updateSettingsMutation.mutate(apiRequest);
  };

  const copyToClipboard = () => {
    const vpa = form.getValues('vpa');
    navigator.clipboard.writeText(vpa);
    setIsCopied(true);
    toast({
      title: "UPI VPA copied",
      description: "UPI VPA has been copied to clipboard.",
    });
    
    setTimeout(() => {
      setIsCopied(false);
    }, 3000);
  };

  // Generate UPI QR code data
  const generateUpiQrData = () => {
    if (!paymentSettings) return '';
    
    // Format according to UPI deep link specification
    // pa: payee address (VPA)
    // pn: payee name
    // tn: transaction note
    const upiData = new URLSearchParams({
      pa: paymentSettings.vpa,
      pn: encodeURIComponent(paymentSettings.merchant_name),
      tn: encodeURIComponent(paymentSettings.description || "Ticket payment"),
    });
    
    return `upi://pay?${upiData.toString()}`;
  };

  const refreshQR = () => {
    queryClient.invalidateQueries({ queryKey: ['paymentSettings'] });
    toast({
      title: "QR Code refreshed",
      description: "The QR code has been regenerated with the current UPI VPA.",
    });
  };

  const handleQrImageUpload = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (file) {
      // Validate file type
      const validTypes = ['image/jpeg', 'image/png', 'image/jpg'];
      if (!validTypes.includes(file.type)) {
        toast({
          title: "Invalid file type",
          description: "Please upload a JPEG or PNG image file.",
          variant: "destructive"
        });
        return;
      }
      
      // Set file for form submission
      setQrImageFile(file);
      
      // Create preview
      const reader = new FileReader();
      reader.onloadend = () => {
        setQrImagePreview(reader.result as string);
      };
      reader.readAsDataURL(file);
    }
  };

  // Error state
  if (error) {
    return (
      <div className="flex min-h-screen flex-col">
        <Navbar />
        <main className="flex-grow bg-gray-50 pt-16 pb-12">
          <div className="container mx-auto px-4">
            <div className="mb-6">
              <h1 className="text-3xl font-bold text-gray-900">UPI Payment Settings</h1>
            </div>
            <Card>
              <CardContent className="flex flex-col items-center justify-center py-10">
                <p className="text-red-500 mb-4">Failed to load UPI settings</p>
                <Button onClick={() => queryClient.invalidateQueries({ queryKey: ['paymentSettings'] })}>
                  Retry
                </Button>
              </CardContent>
            </Card>
          </div>
        </main>
        <Footer />
      </div>
    );
  }

  return (
    <div className="flex min-h-screen flex-col">
      <Navbar />

      <main className="flex-grow bg-gray-50 pt-16 pb-12">
        <div className="container mx-auto px-4">
          <div className="mb-6">
            <h1 className="text-3xl font-bold text-gray-900">UPI Payment Settings</h1>
            <p className="text-gray-600 mt-1">Manage your UPI Virtual Payment Address (VPA) for ticket transactions</p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div className="md:col-span-2">
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center">
                    <CreditCard className="h-5 w-5 mr-2 text-primary" />
                    UPI VPA Configuration
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  {isLoading ? (
                    <div className="space-y-4">
                      <Skeleton className="h-4 w-full" />
                      <Skeleton className="h-10 w-full" />
                      <Skeleton className="h-4 w-full" />
                      <Skeleton className="h-10 w-full" />
                      <Skeleton className="h-4 w-full" />
                      <Skeleton className="h-10 w-full" />
                      <div className="flex justify-end pt-2">
                        <Skeleton className="h-10 w-24" />
                      </div>
                    </div>
                  ) : (
                    <Form {...form}>
                      <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-4">
                        <FormField
                          control={form.control}
                          name="merchantName"
                          render={({ field }) => (
                            <FormItem>
                              <FormLabel>Merchant Name</FormLabel>
                              <FormControl>
                                <Input placeholder="e.g., Eventia Tickets" {...field} />
                              </FormControl>
                              <FormDescription>
                                This name will appear in users' UPI payment apps
                              </FormDescription>
                              <FormMessage />
                            </FormItem>
                          )}
                        />
                        
                        <FormField
                          control={form.control}
                          name="vpa"
                          render={({ field }) => (
                            <FormItem>
                              <FormLabel>UPI VPA</FormLabel>
                              <div className="flex">
                                <FormControl>
                                  <Input placeholder="e.g., business@bank" {...field} className="rounded-r-none" />
                                </FormControl>
                                <Button
                                  type="button"
                                  variant="secondary"
                                  size="icon"
                                  className="rounded-l-none"
                                  onClick={copyToClipboard}
                                >
                                  {isCopied ? <CheckCircle2 className="h-4 w-4 text-green-500" /> : <Copy className="h-4 w-4" />}
                                </Button>
                              </div>
                              <FormDescription>
                                The Virtual Payment Address that will receive payments (e.g., name@bank)
                              </FormDescription>
                              <FormMessage />
                            </FormItem>
                          )}
                        />
                        
                        <FormField
                          control={form.control}
                          name="description"
                          render={({ field }) => (
                            <FormItem>
                              <FormLabel>Description (Optional)</FormLabel>
                              <FormControl>
                                <Input placeholder="e.g., Official payment account for tickets" {...field} />
                              </FormControl>
                              <FormDescription>
                                Additional information about this payment address
                              </FormDescription>
                              <FormMessage />
                            </FormItem>
                          )}
                        />
                        
                        <FormField
                          control={form.control}
                          name="paymentMode"
                          render={({ field }) => (
                            <FormItem>
                              <FormLabel>Payment Mode</FormLabel>
                              <div className="space-y-2">
                                <div className="flex items-center space-x-2">
                                  <input
                                    type="radio"
                                    id="vpa-mode"
                                    value="vpa"
                                    checked={field.value === 'vpa'}
                                    onChange={() => field.onChange('vpa')}
                                    className="h-4 w-4 border-gray-300 text-primary focus:ring-primary"
                                  />
                                  <label htmlFor="vpa-mode" className="text-sm">VPA Only (Generate QR from UPI ID)</label>
                                </div>
                                
                                <div className="flex items-center space-x-2">
                                  <input
                                    type="radio"
                                    id="qr-mode"
                                    value="qr_image"
                                    checked={field.value === 'qr_image'}
                                    onChange={() => field.onChange('qr_image')}
                                    className="h-4 w-4 border-gray-300 text-primary focus:ring-primary"
                                  />
                                  <label htmlFor="qr-mode" className="text-sm">Custom QR Image Upload</label>
                                </div>
                              </div>
                              <FormDescription>
                                Choose how the payment QR will be displayed to users
                              </FormDescription>
                              <FormMessage />
                            </FormItem>
                          )}
                        />
                        
                        {form.watch('paymentMode') === 'qr_image' && (
                          <div className="border rounded-md p-4 bg-gray-50">
                            <FormLabel className="block mb-2">Upload QR Image</FormLabel>
                            <div className="flex flex-col items-center space-y-4">
                              {qrImagePreview ? (
                                <div className="relative">
                                  <img 
                                    src={qrImagePreview} 
                                    alt="QR Preview" 
                                    className="w-32 h-32 object-contain border rounded-md"
                                  />
                                  <Button
                                    variant="ghost"
                                    size="sm"
                                    className="absolute -top-2 -right-2 h-6 w-6 rounded-full p-0 text-red-500"
                                    onClick={() => {
                                      setQrImageFile(null);
                                      setQrImagePreview(null);
                                    }}
                                  >
                                    ×
                                  </Button>
                                </div>
                              ) : (
                                <div className="w-32 h-32 border-2 border-dashed border-gray-300 rounded-md flex items-center justify-center bg-white">
                                  <span className="text-xs text-gray-500 text-center">No image uploaded</span>
                                </div>
                              )}
                              
                              <Input
                                type="file"
                                accept=".jpg,.jpeg,.png"
                                onChange={handleQrImageUpload}
                                className="max-w-xs"
                              />
                              <FormDescription className="text-xs text-center">
                                Upload a JPG or PNG image of your payment QR code. <br />
                                Recommended size: 300x300px
                              </FormDescription>
                            </div>
                          </div>
                        )}
                        
                        <div className="flex justify-end pt-2">
                          <Button type="submit" disabled={updateSettingsMutation.isPending}>
                            {updateSettingsMutation.isPending ? (
                              <>
                                <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                                Saving...
                              </>
                            ) : "Save Changes"}
                          </Button>
                        </div>
                      </form>
                    </Form>
                  )}
                </CardContent>
              </Card>
            </div>
            
            <div>
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center">
                    <Shield className="h-5 w-5 mr-2 text-primary" />
                    UPI QR Code
                  </CardTitle>
                </CardHeader>
                <CardContent className="flex flex-col items-center">
                  {isLoading ? (
                    <Skeleton className="h-48 w-48 rounded-md mb-4" />
                  ) : (
                    <div className="bg-white p-4 rounded-md shadow-sm border w-48 h-48 flex items-center justify-center mb-4">
                      {paymentSettings?.payment_mode === 'qr_image' && paymentSettings.qrImageUrl ? (
                        <div className="relative overflow-hidden w-full h-full flex items-center justify-center">
                          <img 
                            src={paymentSettings.qrImageUrl} 
                            alt="Custom QR Code" 
                            className="max-w-full max-h-full object-contain"
                          />
                          <div className="absolute inset-0 bg-black/5 opacity-0 hover:opacity-100 transition-opacity flex items-center justify-center">
                            <p className="text-xs text-center text-gray-600 bg-white/80 px-2 py-1 rounded">
                              Custom QR Image
                            </p>
                          </div>
                        </div>
                      ) : paymentSettings && (
                        <>
                          <QRCodeSVG 
                            value={generateUpiQrData()} 
                            size={170}
                            level="H"
                            includeMargin={true}
                            imageSettings={{
                              src: "/upi-logo.png",
                              height: 24,
                              width: 24,
                              excavate: true,
                            }}
                          />
                          <p className="text-xs text-gray-500 mt-2 text-center absolute bottom-2">
                            {paymentSettings.vpa}
                          </p>
                        </>
                      )}
                    </div>
                  )}
                  
                  <Button 
                    variant="outline" 
                    size="sm"
                    className="w-full mb-2"
                    onClick={refreshQR}
                    disabled={isLoading}
                  >
                    <RefreshCw className="h-3 w-3 mr-2" />
                    Refresh QR Code
                  </Button>
                  
                  <div className="mt-2 text-xs text-gray-500 text-center w-full">
                    <p>Scan with any UPI app to test</p>
                    {paymentSettings && (
                      <>
                        <p className="mt-1">
                          Last updated: {new Date(paymentSettings.updated_at).toLocaleString()}
                        </p>
                        <p className="mt-1 text-xs">
                          Mode: {paymentSettings.payment_mode === 'qr_image' ? 'Custom QR Image' : 'Dynamic UPI QR'}
                        </p>
                      </>
                    )}
                  </div>
                </CardContent>
              </Card>
            </div>
          </div>
        </div>
      </main>

      <Footer />
    </div>
  );
};

export default AdminUpiManagement;
