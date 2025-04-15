import React from 'react';
import Navbar from '@/components/layout/Navbar';
import Footer from '@/components/layout/Footer';
import { Card, CardContent } from '@/components/ui/card';
import { Mail, Phone, MapPin, Clock, Calendar, Ticket } from 'lucide-react';

const About = () => {
  return (
    <div className="flex flex-col min-h-screen">
      <Navbar />
      
      <main className="flex-grow py-12 bg-gray-50">
        <div className="container mx-auto px-4">
          <div className="max-w-4xl mx-auto">
            <h1 className="text-3xl font-bold mb-6">About Eventia</h1>
            
            <Card className="mb-8">
              <CardContent className="pt-6">
                <h2 className="text-xl font-semibold mb-4">Our Story</h2>
                <p className="mb-4">
                  Eventia is a cutting-edge ticketing platform designed to provide seamless and hassle-free experiences for event attendees.
                  Founded in 2023, we aim to revolutionize the way fans connect with their favorite IPL teams and matches through
                  innovative digital solutions.
                </p>
                <p className="mb-4">
                  Our platform enables cricket enthusiasts to browse upcoming matches, purchase tickets securely, and enjoy a streamlined 
                  experience from booking to attendance. We're passionate about creating memorable moments for cricket fans across India.
                </p>
              </CardContent>
            </Card>
            
            <h2 className="text-2xl font-semibold mb-4">Why Choose Eventia?</h2>
            
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-8">
              <Card>
                <CardContent className="pt-6">
                  <div className="flex items-start gap-3">
                    <Ticket className="h-6 w-6 text-primary mt-1" />
                    <div>
                      <h3 className="font-semibold mb-2">Easy Ticket Booking</h3>
                      <p className="text-sm text-gray-600">
                        Our simple and intuitive booking process lets you secure your tickets in minutes, 
                        with clear information about seating, pricing, and availability.
                      </p>
                    </div>
                  </div>
                </CardContent>
              </Card>
              
              <Card>
                <CardContent className="pt-6">
                  <div className="flex items-start gap-3">
                    <Clock className="h-6 w-6 text-primary mt-1" />
                    <div>
                      <h3 className="font-semibold mb-2">Real-time Updates</h3>
                      <p className="text-sm text-gray-600">
                        Get instant notifications about ticket confirmations, match updates, and any 
                        changes to schedules, ensuring you never miss important information.
                      </p>
                    </div>
                  </div>
                </CardContent>
              </Card>
              
              <Card>
                <CardContent className="pt-6">
                  <div className="flex items-start gap-3">
                    <Calendar className="h-6 w-6 text-primary mt-1" />
                    <div>
                      <h3 className="font-semibold mb-2">Comprehensive Event Calendar</h3>
                      <p className="text-sm text-gray-600">
                        Browse all IPL matches with detailed information about teams, venues, and match timings 
                        in our well-organized event calendar.
                      </p>
                    </div>
                  </div>
                </CardContent>
              </Card>
              
              <Card>
                <CardContent className="pt-6">
                  <div className="flex items-start gap-3">
                    <MapPin className="h-6 w-6 text-primary mt-1" />
                    <div>
                      <h3 className="font-semibold mb-2">Venue Details</h3>
                      <p className="text-sm text-gray-600">
                        Access comprehensive information about match venues, including seating charts, 
                        facilities, and directions to help plan your visit.
                      </p>
                    </div>
                  </div>
                </CardContent>
              </Card>
            </div>
            
            <h2 className="text-2xl font-semibold mb-4">Contact Us</h2>
            
            <Card className="mb-8">
              <CardContent className="pt-6">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <div className="flex items-start gap-3">
                    <Mail className="h-5 w-5 text-primary mt-1" />
                    <div>
                      <h3 className="font-semibold mb-1">Email Us</h3>
                      <p className="text-sm text-gray-600">support@eventia.com</p>
                      <p className="text-sm text-gray-600">For general inquiries and support</p>
                    </div>
                  </div>
                  
                  <div className="flex items-start gap-3">
                    <Phone className="h-5 w-5 text-primary mt-1" />
                    <div>
                      <h3 className="font-semibold mb-1">Call Us</h3>
                      <p className="text-sm text-gray-600">+91 9876543210</p>
                      <p className="text-sm text-gray-600">Mon-Fri, 9:00 AM - 6:00 PM IST</p>
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>
            
            <Card>
              <CardContent className="pt-6">
                <h2 className="text-xl font-semibold mb-4">Legal Information</h2>
                <p className="text-sm text-gray-600 mb-2">
                  Eventia is a registered company operating under the laws of India. All ticketing operations
                  comply with relevant regulatory requirements and consumer protection laws.
                </p>
                <p className="text-sm text-gray-600">
                  © 2023 Eventia. All rights reserved. All IPL team logos and trademarks are property of their respective owners.
                </p>
              </CardContent>
            </Card>
          </div>
        </div>
      </main>
      
      <Footer />
    </div>
  );
};

export default About; 