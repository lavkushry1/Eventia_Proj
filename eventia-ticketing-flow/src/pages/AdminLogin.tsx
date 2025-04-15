import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import Navbar from '@/components/layout/Navbar';
import Footer from '@/components/layout/Footer';
import { Input } from '@/components/ui/input';
import { Button } from '@/components/ui/button';
import { toast } from '@/hooks/use-toast';
import { Shield, Lock, User, Mail, Loader2 } from 'lucide-react';
import { useAdminAuth } from '@/hooks/use-admin-auth';
import { api } from '@/lib/api';
import { useMutation } from '@tanstack/react-query';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';

const AdminLogin = () => {
  const [token, setToken] = useState('');
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [authMethod, setAuthMethod] = useState<'token' | 'credentials'>('credentials');
  const { login, isLoggedIn } = useAdminAuth();
  const navigate = useNavigate();

  // Redirect if already logged in
  useEffect(() => {
    if (isLoggedIn) {
      navigate('/admin-dashboard');
    }
  }, [isLoggedIn, navigate]);

  // Login mutation
  const loginMutation = useMutation({
    mutationFn: (loginData: { token?: string; username?: string; password?: string }) => {
      if (loginData.token) {
        return api.adminLogin(loginData.token);
      } else if (loginData.username && loginData.password) {
        return api.adminLoginWithCredentials(loginData.username, loginData.password);
      }
      throw new Error('Invalid login data');
    },
    onSuccess: (data) => {
      // Use the token from the response or the input token
      const authToken = data.access_token;
      login(authToken);
      toast({
        title: "Login successful",
        description: "Welcome to the admin dashboard",
      });
      navigate('/admin-dashboard');
    },
    onError: (error: Error) => {
      toast({
        title: "Login failed",
        description: error.message || "Please check your credentials and try again",
        variant: "destructive"
      });
    }
  });

  const handleLogin = (e: React.FormEvent) => {
    e.preventDefault();
    
    if (authMethod === 'token') {
      if (!token) {
        toast({
          title: "Admin token is required",
          variant: "destructive"
        });
        return;
      }
      
      // Attempt to login with token
      loginMutation.mutate({ token });
    } else {
      if (!username || !password) {
        toast({
          title: "Username and password are required",
          variant: "destructive"
        });
        return;
      }
      
      // Attempt to login with username and password
      loginMutation.mutate({ username, password });
    }
  };

  return (
    <div className="flex flex-col min-h-screen">
      <Navbar />
      
      <main className="flex-grow pt-16 bg-gray-50 flex items-center justify-center">
        <div className="w-full max-w-md p-8 bg-white rounded-xl shadow-sm">
          <div className="text-center mb-6">
            <div className="w-16 h-16 bg-primary/10 rounded-full flex items-center justify-center mx-auto mb-4">
              <Shield className="h-8 w-8 text-primary" />
            </div>
            <h1 className="text-2xl font-bold text-gray-900">Admin Login</h1>
            <p className="text-gray-600 mt-2">Access the admin dashboard</p>
          </div>
          
          <Tabs value={authMethod} onValueChange={(v) => setAuthMethod(v as 'token' | 'credentials')}>
            <TabsList className="grid w-full grid-cols-2 mb-6">
              <TabsTrigger value="credentials">Username & Password</TabsTrigger>
              <TabsTrigger value="token">Token</TabsTrigger>
            </TabsList>
            
            <TabsContent value="credentials">
              <form onSubmit={handleLogin}>
                <div className="space-y-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Username
                    </label>
                    <div className="relative">
                      <Input
                        type="text"
                        value={username}
                        onChange={(e) => setUsername(e.target.value)}
                        placeholder="Enter your username"
                        className="pl-10"
                      />
                      <User className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
                    </div>
                  </div>
                  
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Password
                    </label>
                    <div className="relative">
                      <Input
                        type="password"
                        value={password}
                        onChange={(e) => setPassword(e.target.value)}
                        placeholder="Enter your password"
                        className="pl-10"
                      />
                      <Lock className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
                    </div>
                  </div>
                  
                  <Button type="submit" className="w-full" disabled={loginMutation.isPending}>
                    {loginMutation.isPending ? (
                      <>
                        <Loader2 className="h-4 w-4 animate-spin mr-2" />
                        Logging in...
                      </>
                    ) : (
                      "Login"
                    )}
                  </Button>
                </div>
              </form>
            </TabsContent>
            
            <TabsContent value="token">
              <form onSubmit={handleLogin}>
                <div className="mb-6">
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Admin Token
                  </label>
                  <div className="relative">
                    <Input
                      type="password"
                      value={token}
                      onChange={(e) => setToken(e.target.value)}
                      placeholder="Enter your admin token"
                      className="pl-10"
                    />
                    <Lock className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
                  </div>
                  <p className="text-xs text-gray-500 mt-2">
                    Use the token provided in your .env file.
                  </p>
                </div>
                
                <Button type="submit" className="w-full" disabled={loginMutation.isPending}>
                  {loginMutation.isPending ? (
                    <>
                      <Loader2 className="h-4 w-4 animate-spin mr-2" />
                      Logging in...
                    </>
                  ) : (
                    "Login with Token"
                  )}
                </Button>
              </form>
            </TabsContent>
          </Tabs>
          
          <div className="mt-6 text-center text-sm text-gray-600">
            <p>For the best security, use username and password login</p>
          </div>
        </div>
      </main>
      
      <Footer />
    </div>
  );
};

export default AdminLogin;
