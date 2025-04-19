import React, { useState, useEffect } from 'react';
import { useForm } from 'react-hook-form';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../components/ui/card';
import { Input } from '../components/ui/input';
import { Button } from '../components/ui/button';
import { Switch } from '../components/ui/switch';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '../components/ui/tabs';
import { Separator } from '../components/ui/separator';
import { Label } from '../components/ui/label';
import { Alert, AlertDescription, AlertTitle } from '../components/ui/alert';
import { CheckCircle, AlertCircle, Upload, RefreshCw } from 'lucide-react';
import { adminUpdatePaymentSettings, fetchAppConfig } from '../lib/api';
import config from '@/config';
import { Toaster } from '@/components/ui/toaster';
import { toast } from '@/hooks/use-toast';
import { useAdminAuth } from '../hooks/useAdminAuth';

interface ConfigSettingsForm {
  payment_enabled: boolean;
  merchant_name: string;
  vpa_address: string;
  qr_image?: FileList;
  frontend_url: string;
  payment_mode: string;
}

const AdminSettings: React.FC = () => {
  const { isAuthenticated, checkingAuth } = useAdminAuth();
  const [isLoading, setIsLoading] = useState(false);
  const [uploadedQrPreview, setUploadedQrPreview] = useState<string | null>(null);
  const [currentQrImageUrl, setCurrentQrImageUrl] = useState<string | null>(null);
  const [activeTab, setActiveTab] = useState('payment');
  
  const { register, handleSubmit, setValue, watch, formState: { errors } } = useForm<ConfigSettingsForm>({
    defaultValues: {
      payment_enabled: config.PAYMENT_ENABLED,
      merchant_name: config.MERCHANT_NAME,
      vpa_address: config.PAYMENT_VPA,
      frontend_url: config.DOMAIN,
      payment_mode: 'vpa',
    }
  });
  
  // Watch the file input to generate preview
  const qrImageFile = watch('qr_image');
  
  useEffect(() => {
    if (qrImageFile?.[0]) {
      const reader = new FileReader();
      reader.onload = (e) => {
        setUploadedQrPreview(e.target?.result as string);
      };
      reader.readAsDataURL(qrImageFile[0]);
    }
  }, [qrImageFile]);

  // Fetch current settings
  useEffect(() => {
    const loadConfig = async () => {
      try {
        setIsLoading(true);
        const data = await fetchAppConfig();
        setValue('payment_enabled', config.PAYMENT_ENABLED);
        setValue('merchant_name', config.MERCHANT_NAME);
        setValue('vpa_address', config.PAYMENT_VPA);
        setValue('frontend_url', config.DOMAIN);
        setCurrentQrImageUrl(config.QR_IMAGE_URL);
        // merge server data...
      } catch (err) {
        toast({ title: 'Failed to load settings', description: String(err) });
      } finally {
        setIsLoading(false);
      }
    };
    loadConfig();
  }, []);
  
  const onSubmit = async (data: ConfigSettingsForm) => {
    setIsLoading(true);
    
    try {
      // Create form data for file upload
      const formData = new FormData();
      formData.append('payment_enabled', data.payment_enabled.toString());
      formData.append('merchant_name', data.merchant_name);
      formData.append('vpa_address', data.vpa_address);
      formData.append('frontend_url', data.frontend_url);
      
      if (data.qr_image?.[0]) {
        formData.append('qr_image', data.qr_image[0]);
      }
      
      // Update settings via API
      await adminUpdatePaymentSettings({
        merchant_name: data.merchant_name,
        vpa: data.vpa_address,
        vpaAddress: data.vpa_address,
        isPaymentEnabled: data.payment_enabled,
        payment_mode: data.qr_image?.[0] ? 'qr_image' : 'vpa'
      });
      
      // Refresh config
      await fetchAppConfig();
      
      toast.success('Settings updated successfully');
    } catch (error) {
      console.error('Error updating settings:', error);
      toast.error('Failed to update settings');
    } finally {
      setIsLoading(false);
    }
  };
  
  const handleRefreshConfig = async () => {
    setIsLoading(true);
    try {
      await fetchAppConfig();
      toast.success('Configuration refreshed successfully');
    } catch (error) {
      console.error('Error refreshing config:', error);
      toast.error('Failed to refresh configuration');
    } finally {
      setIsLoading(false);
    }
  };
  
  if (checkingAuth) {
    return <div className="container mx-auto p-4">Loading...</div>;
  }
  
  if (!isAuthenticated) {
    return (
      <div className="container mx-auto p-4">
        <Alert variant="destructive">
          <AlertCircle className="h-4 w-4" />
          <AlertTitle>Authentication Required</AlertTitle>
          <AlertDescription>
            You need to be logged in as an admin to access this page.
          </AlertDescription>
        </Alert>
      </div>
    );
  }
  
  return (
    <div className="container mx-auto p-4">
      
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-2xl font-bold">Admin Configuration Settings</h1>
        <Button 
          variant="outline" 
          size="sm" 
          onClick={handleRefreshConfig}
          disabled={isLoading}
        >
          <RefreshCw className="h-4 w-4 mr-2" />
          Refresh Config
        </Button>
      </div>
      
      <Tabs defaultValue={activeTab} onValueChange={setActiveTab}>
        <TabsList className="mb-4">
          <TabsTrigger value="payment">Payment Settings</TabsTrigger>
          <TabsTrigger value="system">System Settings</TabsTrigger>
        </TabsList>
        
        <form onSubmit={handleSubmit(onSubmit)}>
          <TabsContent value="payment">
            <Card>
              <CardHeader>
                <CardTitle>Payment Configuration</CardTitle>
                <CardDescription>
                  Configure payment settings for the ticketing platform.
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="grid gap-4 py-4">
                  <div className="flex items-center gap-4">
                    <Label htmlFor="payment_enabled" className="w-40">Enable Payments</Label>
                    <Switch 
                      id="payment_enabled"
                      checked={watch('payment_enabled')}
                      onCheckedChange={(checked) => setValue('payment_enabled', checked)}
                    />
                  </div>
                  
                  <Separator />
                  
                  <div className="flex flex-col gap-4">
                    <div className="grid gap-2">
                      <Label htmlFor="merchant_name">Merchant Name</Label>
                      <Input
                        id="merchant_name"
                        placeholder="Eventia Ticketing"
                        {...register('merchant_name', { required: true })}
                        error={errors.merchant_name ? 'Merchant name is required' : undefined}
                      />
                      {errors.merchant_name && (
                        <p className="text-sm text-red-500">Merchant name is required</p>
                      )}
                    </div>
                    
                    <div className="grid gap-2">
                      <Label htmlFor="vpa_address">UPI VPA Address</Label>
                      <Input
                        id="vpa_address"
                        placeholder="example@bank"
                        {...register('vpa_address', { 
                          required: true,
                          pattern: /^[a-zA-Z0-9.]{3,}@[a-zA-Z]{3,}$/
                        })}
                        error={errors.vpa_address ? 'Valid UPI VPA is required (e.g. name@bank)' : undefined}
                      />
                      {errors.vpa_address && (
                        <p className="text-sm text-red-500">
                          {errors.vpa_address.type === 'required' 
                            ? 'UPI VPA address is required' 
                            : 'Invalid UPI VPA format (e.g. name@bank)'}
                        </p>
                      )}
                    </div>
                    
                    <div className="grid gap-2">
                      <Label htmlFor="qr_image">Payment QR Code (Optional)</Label>
                      <div className="flex gap-4 items-start">
                        <div className="flex-1">
                          <Input
                            id="qr_image"
                            type="file"
                            accept="image/*"
                            {...register('qr_image')}
                          />
                          <p className="text-sm text-gray-500 mt-1">
                            Upload a QR code image if you prefer to display a QR image instead of UPI ID
                          </p>
                        </div>
                        
                        {/* Preview current or uploaded QR */}
                        <div className="flex-shrink-0">
                          {uploadedQrPreview ? (
                            <div className="relative w-24 h-24 border rounded">
                              <img 
                                src={uploadedQrPreview} 
                                alt="QR Preview" 
                                className="w-full h-full object-contain"
                              />
                              <div className="absolute -top-2 -right-2 bg-green-500 text-white rounded-full p-1">
                                <CheckCircle size={16} />
                              </div>
                            </div>
                          ) : currentQrImageUrl && !currentQrImageUrl.includes('placeholder') ? (
                            <div className="w-24 h-24 border rounded">
                              <img 
                                src={currentQrImageUrl} 
                                alt="Current QR" 
                                className="w-full h-full object-contain"
                              />
                            </div>
                          ) : (
                            <div className="w-24 h-24 border rounded flex items-center justify-center bg-gray-100">
                              <Upload size={24} className="text-gray-400" />
                            </div>
                          )}
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>
          </TabsContent>
          
          <TabsContent value="system">
            <Card>
              <CardHeader>
                <CardTitle>System Configuration</CardTitle>
                <CardDescription>
                  Configure system settings for the ticketing platform.
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="grid gap-4 py-4">
                  <div className="grid gap-2">
                    <Label htmlFor="frontend_url">Frontend Base URL</Label>
                    <Input
                      id="frontend_url"
                      placeholder="http://localhost:3000"
                      {...register('frontend_url', { 
                        required: true,
                        pattern: /^(https?:\/\/.+)$/
                      })}
                      error={errors.frontend_url ? 'Valid URL is required (e.g. http://domain.com)' : undefined}
                    />
                    {errors.frontend_url && (
                      <p className="text-sm text-red-500">
                        {errors.frontend_url.type === 'required' 
                          ? 'Frontend URL is required' 
                          : 'Invalid URL format (e.g. http://domain.com)'}
                      </p>
                    )}
                  </div>
                  
                  <Separator />
                  
                  <div className="grid gap-2">
                    <h3 className="font-medium">Environment Information</h3>
                    <div className="flex items-center justify-between">
                      <div className="text-sm">API Base URL:</div>
                      <div className="font-mono">{config.API_BASE_URL}</div>
                    </div>
                    <div className="flex items-center justify-between">
                      <div className="text-sm">Environment:</div>
                      <div className={`px-2 py-1 rounded text-xs ${
                        config.ENV === 'production' 
                          ? 'bg-red-100 text-red-800' 
                          : 'bg-green-100 text-green-800'
                      }`}>
                        {config.ENV}
                      </div>
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>
          </TabsContent>
          
          <div className="mt-6">
            <Button type="submit" className="mr-2" disabled={isLoading}>
              {isLoading ? 'Saving...' : 'Save Settings'}
            </Button>
            <Button 
              type="button" 
              variant="outline" 
              onClick={() => {
                setValue('payment_enabled', config.PAYMENT_ENABLED);
                setValue('merchant_name', config.MERCHANT_NAME);
                setValue('vpa_address', config.PAYMENT_VPA);
                setValue('frontend_url', config.DOMAIN);
                setValue('payment_mode', 'vpa');
                setIsQrMode(false);
                setCurrentQrImageUrl(config.QR_IMAGE_URL);
              }}
              disabled={isLoading}
            >
              Reset
            </Button>
          </div>
        </form>
      </Tabs>
    </div>
  );
};

export default AdminSettings;