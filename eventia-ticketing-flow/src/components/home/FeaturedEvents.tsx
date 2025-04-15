
import React from 'react';
import { ArrowRight } from 'lucide-react';
import { Link } from 'react-router-dom';
import { events } from '@/data/eventsData';
import { iplMatches } from '@/data/iplData';
import EventCard from '@/components/events/EventCard';
import AnimatedButton from '@/components/ui/AnimatedButton';

const FeaturedEvents = () => {
  // Get featured events
  const featuredEvents = events.filter(event => event.featured).slice(0, 3);
  
  // Get first 2 IPL matches
  const featuredMatches = iplMatches.slice(0, 2);

  return (
    <div className="py-16 bg-gray-50">
      <div className="container mx-auto px-4">
        {/* Featured Events Section */}
        <div className="mb-16">
          <div className="flex justify-between items-center mb-8">
            <div>
              <h2 className="text-3xl font-bold text-gray-900">Featured Events</h2>
              <p className="text-gray-600 mt-2">Discover the most popular upcoming events</p>
            </div>
            <Link to="/events">
              <AnimatedButton variant="outline" className="hidden sm:flex">
                View All Events <ArrowRight className="ml-2 h-4 w-4" />
              </AnimatedButton>
            </Link>
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {featuredEvents.map((event) => (
              <EventCard key={event.id} event={event} />
            ))}
          </div>
          
          <div className="mt-8 flex justify-center sm:hidden">
            <Link to="/events">
              <AnimatedButton variant="outline">
                View All Events <ArrowRight className="ml-2 h-4 w-4" />
              </AnimatedButton>
            </Link>
          </div>
        </div>
        
        {/* Featured IPL Matches Section */}
        <div>
          <div className="flex justify-between items-center mb-8">
            <div>
              <h2 className="text-3xl font-bold text-gray-900">Upcoming IPL Matches</h2>
              <p className="text-gray-600 mt-2">Book your tickets for the hottest cricket matches</p>
            </div>
            <Link to="/ipl-tickets">
              <AnimatedButton variant="outline" className="hidden sm:flex">
                View All Matches <ArrowRight className="ml-2 h-4 w-4" />
              </AnimatedButton>
            </Link>
          </div>
          
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {featuredMatches.map((match) => (
              <div 
                key={match.id} 
                className="bg-white rounded-xl shadow-md overflow-hidden hover:shadow-lg transition-shadow duration-300"
              >
                <div className="p-6">
                  <div className="flex justify-between items-center mb-4">
                    <h3 className="text-lg font-semibold text-gray-900">{match.title}</h3>
                    <span className="text-sm font-medium bg-blue-100 text-blue-800 py-1 px-2 rounded">
                      {new Date(match.date).toLocaleDateString('en-US', { month: 'short', day: 'numeric' })}
                    </span>
                  </div>
                  
                  <div className="flex items-center justify-between mb-4">
                    <div className="flex items-center space-x-4">
                      <div className="w-12 h-12 bg-gray-200 rounded-full flex items-center justify-center">
                        <span className="font-bold text-sm">{match.teams.team1.shortName}</span>
                      </div>
                      <span className="font-bold text-xl text-gray-500">VS</span>
                      <div className="w-12 h-12 bg-gray-200 rounded-full flex items-center justify-center">
                        <span className="font-bold text-sm">{match.teams.team2.shortName}</span>
                      </div>
                    </div>
                    <div className="text-right">
                      <div className="text-sm text-gray-600">{match.venue}</div>
                      <div className="font-semibold">{match.time} IST</div>
                    </div>
                  </div>
                  
                  <div className="flex justify-between items-center">
                    <div className="text-gray-600 text-sm">
                      Tickets from ₹{Math.min(...match.ticketTypes.map(t => t.price))}
                    </div>
                    <Link to={`/event/${match.id}`}>
                      <AnimatedButton size="sm" className="bg-primary hover:bg-primary/90">
                        Book Now
                      </AnimatedButton>
                    </Link>
                  </div>
                </div>
              </div>
            ))}
          </div>
          
          <div className="mt-8 flex justify-center sm:hidden">
            <Link to="/ipl-tickets">
              <AnimatedButton variant="outline">
                View All Matches <ArrowRight className="ml-2 h-4 w-4" />
              </AnimatedButton>
            </Link>
          </div>
        </div>
      </div>
    </div>
  );
};

export default FeaturedEvents;
