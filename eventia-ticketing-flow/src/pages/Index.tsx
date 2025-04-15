
import React from 'react';
import { Link } from 'react-router-dom';
import Navbar from '@/components/layout/Navbar';
import Footer from '@/components/layout/Footer';
import Hero from '@/components/home/Hero';
import FeaturedEvents from '@/components/home/FeaturedEvents';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from '@/components/ui/card';
import { CreditCard, MapPin, QrCode, Truck, View, Timer } from 'lucide-react';

const Index = () => {
  const features = [
    {
      icon: <QrCode className="h-10 w-10 text-primary" />,
      title: "QR-Based Payments",
      description: "Scan QR code with any UPI app, enter UTR ID, and you're done. No accounts needed."
    },
    {
      icon: <Truck className="h-10 w-10 text-primary" />,
      title: "Home Delivery",
      description: "Physical tickets delivered to your doorstep within 2 days of confirmed payment."
    },
    {
      icon: <View className="h-10 w-10 text-primary" />,
      title: "AR Venue Preview",
      description: "Check your seat view in augmented reality before booking for the perfect match experience."
    },
    {
      icon: <Timer className="h-10 w-10 text-primary" />,
      title: "Quick Booking",
      description: "Book tickets in under 2 minutes without creating an account or OTP verification."
    }
  ];

  return (
    <div className="flex flex-col min-h-screen">
      <Navbar />
      
      <main className="flex-grow">
        <Hero />
        
        <section className="py-16 bg-gray-50">
          <div className="container mx-auto px-4">
            <div className="text-center mb-12">
              <h2 className="text-3xl font-bold mb-4">The Future of Event Ticketing</h2>
              <p className="text-xl text-gray-600 max-w-2xl mx-auto">
                Book IPL match tickets and events without the hassle of creating accounts or verifying OTPs.
              </p>
            </div>
            
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
              {features.map((feature, index) => (
                <Card key={index} className="hover:shadow-md transition-shadow">
                  <CardHeader className="pb-4">
                    <div className="mb-4">{feature.icon}</div>
                    <CardTitle>{feature.title}</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <CardDescription className="text-gray-600">
                      {feature.description}
                    </CardDescription>
                  </CardContent>
                </Card>
              ))}
            </div>
            
            <div className="mt-12 text-center">
              <Link to="/events">
                <Button size="lg" className="px-8">
                  Browse Events
                </Button>
              </Link>
            </div>
          </div>
        </section>
        
        <FeaturedEvents />
        
        <section className="py-16 bg-primary/5">
          <div className="container mx-auto px-4">
            <div className="grid md:grid-cols-2 gap-12 items-center">
              <div>
                <h2 className="text-3xl font-bold mb-6">Experience Venues in AR Before Booking</h2>
                <p className="text-lg text-gray-700 mb-6">
                  Not sure if your seat has a good view? Use our AR venue preview to experience the stadium from your chosen seat before you book.
                </p>
                <ul className="space-y-4 mb-8">
                  <li className="flex items-start">
                    <div className="flex-shrink-0 h-6 w-6 bg-primary/10 rounded-full flex items-center justify-center text-primary mr-3">
                      ✓
                    </div>
                    <span>Interactive 3D stadium models</span>
                  </li>
                  <li className="flex items-start">
                    <div className="flex-shrink-0 h-6 w-6 bg-primary/10 rounded-full flex items-center justify-center text-primary mr-3">
                      ✓
                    </div>
                    <span>Realistic seat perspective views</span>
                  </li>
                  <li className="flex items-start">
                    <div className="flex-shrink-0 h-6 w-6 bg-primary/10 rounded-full flex items-center justify-center text-primary mr-3">
                      ✓
                    </div>
                    <span>Mobile-friendly AR experience</span>
                  </li>
                </ul>
                <Link to="/venue-preview/123">
                  <Button variant="outline" size="lg">
                    <MapPin className="mr-2 h-4 w-4" />
                    Try AR Preview
                  </Button>
                </Link>
              </div>
              <div className="bg-white p-8 rounded-xl shadow-sm">
                <div className="aspect-video bg-gray-100 rounded-lg flex items-center justify-center mb-4">
                  <div className="text-center p-6">
                    <View className="h-16 w-16 text-primary/40 mx-auto mb-4" />
                    <p className="text-gray-500">AR Venue Preview Demo</p>
                  </div>
                </div>
                <div className="text-center">
                  <p className="text-sm text-gray-500">Experience stadium views in augmented reality</p>
                </div>
              </div>
            </div>
          </div>
        </section>
        
        <section className="py-16 bg-gradient-to-r from-primary/90 to-primary/70 text-white">
          <div className="container mx-auto px-4 text-center">
            <h2 className="text-3xl font-bold mb-6">Ready to Book Your Next Event?</h2>
            <p className="text-xl mb-8 max-w-2xl mx-auto">
              Browse upcoming IPL matches and events, and secure your tickets in minutes.
            </p>
            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              <Link to="/events">
                <Button size="lg" variant="secondary">
                  Explore Events
                </Button>
              </Link>
              <Link to="/admin-login">
                <Button size="lg" variant="outline" className="bg-white/10 hover:bg-white/20 text-white border-white/20">
                  Admin Login
                </Button>
              </Link>
            </div>
          </div>
        </section>
      </main>
      
      <Footer />
    </div>
  );
};

export default Index;
