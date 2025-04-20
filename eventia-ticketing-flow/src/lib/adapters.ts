import { ApiEvent, ApiBookingResponse } from '@/lib/api';
import { CustomerInfo, EventResponse, BookingResponse, SelectedTicket } from './types';
import configManager from './config';

// Helper function to extract time from ISO datetime
function extractTimeFromDateTime(dateTimeStr?: string): string {
  if (!dateTimeStr) return '';
  try {
    const date = new Date(dateTimeStr);
    return date.toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' });
  } catch (e) {
    console.error('Error parsing datetime:', e);
    return '';
  }
}

// Helper function to format image URLs
function formatImageUrl(imageUrl?: string, type: string = 'events'): string {
  if (!imageUrl) return '/placeholder.svg';
  if (imageUrl.startsWith('http') || imageUrl.startsWith('/assets')) {
    return imageUrl;
  }
  return `${configManager.getStaticUrl(type, imageUrl)}`;
}

// Frontend event model (UI-specific)
export interface UIEvent {
  id: string;
  title: string;
  description: string;
  category: string;
  venue: string;
  date: string;
  time: string;
  duration: string;
  ticketTypes: {
    category: string;
    price: number;
    available: number;
  }[];
  image: string;
  featured: boolean;
  teams?: {
    team1: {
      name: string;
      shortName: string;
      logo: string;
      color?: string;
    };
    team2: {
      name: string;
      shortName: string;
      logo: string;
      color?: string;
    };
  };
}

// For backward compatibility with legacy API format
interface LegacyApiEvent extends ApiEvent {
  ticket_price?: number;
  tickets_available?: number;
  team_home?: {
    name: string;
    code: string;
    logo?: string;
    primary_color?: string;
    color?: string;
  };
  team_away?: {
    name: string;
    code: string;
    logo?: string;
    primary_color?: string;
    color?: string;
  };
}

// For backward compatibility with legacy API booking response
interface LegacyApiBookingResponse extends ApiBookingResponse {
  payment_info?: Record<string, unknown>;
}

// Helper to extract short team name
const getTeamShortName = (fullName: string): string => {
  const teamShortCodes: Record<string, string> = {
    "Mumbai Indians": "MI",
    "Chennai Super Kings": "CSK",
    "Royal Challengers Bangalore": "RCB", 
    "Kolkata Knight Riders": "KKR",
    "Delhi Capitals": "DC",
    "Rajasthan Royals": "RR",
    "Punjab Kings": "PBKS",
    "Sunrisers Hyderabad": "SRH",
    "Gujarat Titans": "GT",
    "Lucknow Super Giants": "LSG"
  };
  
  return teamShortCodes[fullName] || fullName.substring(0, 3).toUpperCase();
};

/**
 * Consistent adapter function to map any backend event data format to 
 * the frontend EventResponse type
 */
export function mapApiResponseToFrontendModel(apiEvent: any): EventResponse {
  console.debug('Mapping API event:', apiEvent);
  
  return {
    id: apiEvent.id || apiEvent._id || '',
    name: apiEvent.name || '',
    description: apiEvent.description || '',
    date: apiEvent.date || (apiEvent.start_date ? new Date(apiEvent.start_date).toISOString().split('T')[0] : ''),
    time: apiEvent.time || (apiEvent.start_date ? extractTimeFromDateTime(apiEvent.start_date) : ''),
    venue: apiEvent.venue || 'TBD',
    venue_id: apiEvent.venue_id || '',
    stadium_id: apiEvent.stadium_id || '',
    category: apiEvent.category || 'Event',
    price: apiEvent.price || 0,
    currency: apiEvent.currency || 'INR',
    totalTickets: apiEvent.totalTickets || 0,
    availableTickets: apiEvent.availableTickets || 0,
    soldOut: apiEvent.soldOut || false,
    isFeatured: apiEvent.featured || apiEvent.isFeatured || false,
    status: apiEvent.status || 'upcoming',
    posterImage: formatImageUrl(apiEvent.poster_url || apiEvent.posterImage, 'events'),
    teamOne: apiEvent.teamOne || (apiEvent.team_home ? apiEvent.team_home.name : ''),
    teamTwo: apiEvent.teamTwo || (apiEvent.team_away ? apiEvent.team_away.name : ''),
    teamOneLogo: formatImageUrl(apiEvent.teamOneLogo || (apiEvent.team_home ? apiEvent.team_home.logo : ''), 'teams'),
    teamTwoLogo: formatImageUrl(apiEvent.teamTwoLogo || (apiEvent.team_away ? apiEvent.team_away.logo : ''), 'teams'),
    createdAt: apiEvent.createdAt || apiEvent.created_at || '',
    updatedAt: apiEvent.updatedAt || apiEvent.updated_at || ''
  };
}

// Convert backend event model to frontend event model
export const mapApiEventToUIEvent = (apiEvent: LegacyApiEvent | EventResponse): UIEvent => {
  console.debug('Mapping to UI event model:', apiEvent);
  
  // Standardize the event object first if it's not already in the expected format
  const standardEvent = 'id' in apiEvent && 'name' in apiEvent ? 
    apiEvent as EventResponse : 
    mapApiResponseToFrontendModel(apiEvent);
  
  // Check for ticket types from API or create default
  let ticketTypes = [];
  
  // If the API provides ticket_types array, use that
  if ('ticket_types' in apiEvent && Array.isArray(apiEvent.ticket_types)) {
    console.debug('Using ticket_types from API:', apiEvent.ticket_types);
    ticketTypes = apiEvent.ticket_types.map(tt => ({
      category: tt.name || "Standard",
      price: tt.price,
      available: tt.available
    }));
  } else {
    // Otherwise create standard ticket type from available properties
    const price = standardEvent.price || 0;
    const available = standardEvent.availableTickets || 0;
    
    ticketTypes = [{
      category: "Standard",
      price,
      available
    }];
    
    // Add premium ticket option if regular price exists
    if (price > 0) {
      ticketTypes.push({
        category: "Premium",
        price: Math.round(price * 1.5), // 50% more expensive
        available: Math.round(available * 0.5) // Half the availability
      });
    }
  }

  // Determine if this is an IPL match by checking if category is "IPL"
  const isIplMatch = standardEvent.category === "IPL";
  
  // Initialize teams object
  let teams = undefined;
  
  // If we have team information (either from standardEvent or original apiEvent)
  if (standardEvent.teamOne && standardEvent.teamTwo) {
    teams = {
      team1: {
        name: standardEvent.teamOne,
        shortName: getTeamShortName(standardEvent.teamOne),
        logo: standardEvent.teamOneLogo || '',
        color: "#004BA0" // Default blue
      },
      team2: {
        name: standardEvent.teamTwo,
        shortName: getTeamShortName(standardEvent.teamTwo),
        logo: standardEvent.teamTwoLogo || '',
        color: "#FFFF00" // Default yellow
      }
    };
  }
  // Otherwise, try to parse team information from title if this is an IPL match
  else if (isIplMatch && standardEvent.name && standardEvent.name.includes("vs")) {
    const teamNames = standardEvent.name.split("vs").map((t: string) => t.trim());
    
    if (teamNames.length === 2) {
      const team1Code = getTeamShortName(teamNames[0]).toLowerCase();
      const team2Code = getTeamShortName(teamNames[1]).toLowerCase();
      
      teams = {
        team1: {
          name: teamNames[0],
          shortName: getTeamShortName(teamNames[0]),
          logo: `/assets/teams/${team1Code}.png`,
          color: "#004BA0" // Default blue
        },
        team2: {
          name: teamNames[1],
          shortName: getTeamShortName(teamNames[1]),
          logo: `/assets/teams/${team2Code}.png`,
          color: "#FFFF00" // Default yellow
        }
      };
    }
  }

  const uiEvent = {
    id: standardEvent.id,
    title: standardEvent.name,
    description: standardEvent.description || '',
    category: standardEvent.category,
    venue: standardEvent.venue || '',
    date: standardEvent.date,
    time: standardEvent.time,
    duration: "2-3 hours", // Default duration
    ticketTypes: ticketTypes,
    image: standardEvent.posterImage || "/placeholder.svg",
    featured: standardEvent.isFeatured,
    teams: teams
  };
  
  console.debug('Mapped to UI event:', uiEvent);
  return uiEvent;
};

// Convert frontend booking data to backend BookingCreate model
export function mapUIBookingToApiBooking(
  eventId: string,
  quantity: number,
  customerInfo: {
    name: string;
    email: string;
    phone: string;
    address?: string;
    city?: string;
    state?: string;
    pincode?: string;
  },
  discountCode?: string,
  ticketTypeId?: string
) {
  // Create a selected_tickets array with a single item when no specific ticket types
  // are provided (backward compatibility)
  const selected_tickets = ticketTypeId 
    ? [{ 
        ticket_type_id: ticketTypeId,
        quantity: quantity,
        price_per_ticket: 0 // Price will be determined on the server side
      }] 
    : [{ 
        ticket_type_id: "default", // Use default when no specific ticket type is provided
        quantity: quantity,
        price_per_ticket: 0 // Price will be determined on the server side
      }];

  return {
    event_id: eventId,
    customer_info: {
      name: customerInfo.name,
      email: customerInfo.email,
      phone: customerInfo.phone,
      address: customerInfo.address || "",
      city: customerInfo.city || "",
      state: customerInfo.state || "",
      pincode: customerInfo.pincode || ""
    },
    selected_tickets,
    discount_code: discountCode || undefined
  };
}

export interface UIBooking {
  bookingId: string;
  eventTitle: string;
  totalAmount: number;
  paymentInfo?: Record<string, unknown>;
  status: string;
}

// Map backend booking response to frontend booking data
export const mapApiBookingToUIBooking = (apiBooking: LegacyApiBookingResponse, eventName: string): UIBooking => {
  return {
    bookingId: apiBooking.booking_id,
    eventTitle: eventName,
    totalAmount: apiBooking.total_amount,
    paymentInfo: apiBooking.payment_info,
    status: apiBooking.status || "pending"
  };
}; 