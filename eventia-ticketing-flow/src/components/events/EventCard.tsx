import React from 'react';
import { Link } from 'react-router-dom';
import { Calendar, MapPin, Clock } from 'lucide-react';
import AnimatedButton from '@/components/ui/AnimatedButton';
import TeamBadge from '@/components/TeamBadge';
import TeamLogo from '@/components/TeamLogo';
import { UIEvent } from '@/lib/adapters';

interface EventCardProps {
  event: UIEvent;
}

const EventCard = ({ event }: EventCardProps) => {
  // Format date if available
  const formattedDate = event.date 
    ? new Date(event.date).toLocaleDateString('en-US', {
        month: 'short',
        day: 'numeric',
        year: 'numeric'
      })
    : 'TBD';

  // Calculate lowest price - safely handle undefined or empty ticketTypes
  const lowestPrice = event.ticketTypes && event.ticketTypes.length > 0 
    ? Math.min(...event.ticketTypes.map(t => t.price || 0))
    : 0;

  // Check if this is an IPL match
  const isIplMatch = event.category === 'IPL' && event.teams;

  return (
    <div className="bg-white rounded-xl shadow-md overflow-hidden hover:shadow-lg transition-shadow duration-300 flex flex-col h-full">
      <div className="relative">
        <img 
          src={event.image || "/placeholder.svg"} 
          alt={event.title} 
          className="w-full h-48 object-cover"
          onError={(e) => {
            e.currentTarget.src = "/placeholder.svg";
          }}
        />
        <div className="absolute top-4 left-4 bg-white rounded-full px-3 py-1 text-xs font-medium text-gray-700">
          {event.category || 'Event'}
        </div>
        
        {/* Team badges for IPL matches */}
        {isIplMatch && (
          <div className="absolute bottom-4 left-0 right-0 flex justify-center items-center space-x-2">
            <div className="flex items-center">
              <TeamLogo 
                teamCode={event.teams?.team1.shortName || ''} 
                size={24}
                className="mr-1" 
              />
              <TeamBadge 
                team={event.teams?.team1.shortName || ''} 
                className="text-xs" 
                color={event.teams?.team1.color} 
              />
            </div>
            <span className="bg-white px-2 py-1 rounded text-xs font-medium">vs</span>
            <div className="flex items-center">
              <TeamLogo 
                teamCode={event.teams?.team2.shortName || ''} 
                size={24}
                className="mr-1" 
              />
              <TeamBadge 
                team={event.teams?.team2.shortName || ''} 
                className="text-xs" 
                color={event.teams?.team2.color} 
              />
            </div>
          </div>
        )}
      </div>
      
      <div className="p-6 flex-grow flex flex-col">
        <h3 className="text-xl font-semibold text-gray-900 mb-2">{event.title || 'Unnamed Event'}</h3>
        
        <div className="text-gray-600 mb-4 line-clamp-2 text-sm">
          {event.description || 'No description available.'}
        </div>
        
        <div className="space-y-2 mb-4">
          <div className="flex items-center text-sm text-gray-600">
            <Calendar className="h-4 w-4 mr-2 text-primary/70" />
            <span>{formattedDate} {event.time && `• ${event.time}`}</span>
          </div>
          <div className="flex items-center text-sm text-gray-600">
            <MapPin className="h-4 w-4 mr-2 text-primary/70" />
            <span>{event.venue || 'Venue TBD'}</span>
          </div>
          <div className="flex items-center text-sm text-gray-600">
            <Clock className="h-4 w-4 mr-2 text-primary/70" />
            <span>{event.duration || 'Duration TBD'}</span>
          </div>
        </div>
        
        <div className="mt-auto flex justify-between items-center pt-4 border-t border-gray-100">
          <div>
            <span className="text-sm text-gray-600">Starting from</span>
            <div className="font-bold text-lg">
              ₹{lowestPrice}
            </div>
          </div>
          <Link to={`/event/${event.id}`}>
            <AnimatedButton size="sm">Book Now</AnimatedButton>
          </Link>
        </div>
      </div>
    </div>
  );
};

export default EventCard;
