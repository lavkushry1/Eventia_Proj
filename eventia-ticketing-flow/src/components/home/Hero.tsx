
import React from 'react';
import { Link } from 'react-router-dom';
import { CalendarDays, Ticket, ArrowRight } from 'lucide-react';
import AnimatedButton from '@/components/ui/AnimatedButton';

const Hero = () => {
  return (
    <div className="relative h-[90vh] flex items-center overflow-hidden bg-gradient-to-b from-blue-900 to-blue-700">
      {/* Background pattern */}
      <div className="absolute inset-0 opacity-10">
        <div className="absolute inset-0 bg-[url('data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iNjAiIGhlaWdodD0iNjAiIHZpZXdCb3g9IjAgMCA2MCA2MCIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj48ZyBmaWxsPSJ3aGl0ZSIgZmlsbC1ydWxlPSJldmVub2RkIj48Y2lyY2xlIGN4PSIyIiBjeT0iMiIgcj0iMiIvPjwvZz48L3N2Zz4=')]"></div>
      </div>

      <div className="container mx-auto px-4 z-10">
        <div className="md:max-w-3xl">
          <div className="flex items-center space-x-2 mb-6">
            <div className="bg-secondary/20 text-secondary rounded-full px-4 py-1 flex items-center">
              <CalendarDays className="h-4 w-4 mr-2" />
              <span className="text-sm font-medium">IPL 2025 Season Tickets Now Available</span>
            </div>
          </div>

          <h1 className="text-4xl md:text-6xl font-bold text-white leading-tight mb-6">
            Book Your <span className="text-secondary">Cricket Experience</span> With Zero Hassle
          </h1>
          
          <p className="text-lg md:text-xl text-white/80 mb-8 md:pr-12">
            No login. No OTP. Just pick your event, pay via QR code, and get tickets delivered directly to your doorstep.
          </p>
          
          <div className="flex flex-col sm:flex-row gap-4">
            <Link to="/ipl-tickets">
              <AnimatedButton size="lg" className="bg-secondary hover:bg-secondary/90 text-white" animation="pulse">
                <Ticket className="mr-2 h-5 w-5" />
                Book IPL Tickets
              </AnimatedButton>
            </Link>
            <Link to="/events">
              <AnimatedButton size="lg" variant="outline" className="bg-white/10 text-white border-white/20 hover:bg-white/20">
                Browse All Events
                <ArrowRight className="ml-2 h-5 w-5" />
              </AnimatedButton>
            </Link>
          </div>
          
          <div className="mt-12 flex items-center space-x-4">
            <div className="flex -space-x-2">
              {[1, 2, 3, 4].map((i) => (
                <div key={i} className="w-10 h-10 rounded-full bg-gray-300 border-2 border-white flex items-center justify-center overflow-hidden">
                  <span className="text-xs font-medium text-gray-600">User</span>
                </div>
              ))}
            </div>
            <div className="text-white/80 text-sm">
              <span className="font-bold text-white">10,000+</span> tickets booked this month
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Hero;
