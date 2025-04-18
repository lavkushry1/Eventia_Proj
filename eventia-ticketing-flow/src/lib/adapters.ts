import { ApiEvent, ApiBookingResponse } from '@/lib/api';
import { CustomerInfo, EventResponse, BookingResponse, SelectedTicket } from './types';

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

// Convert backend event model to frontend event model
export const mapApiEventToUIEvent = (apiEvent: LegacyApiEvent): UIEvent => {
  console.log('Mapping API event to UI event:', JSON.stringify(apiEvent, null, 2));
  
  // Check for ticket types from API or create default
  let ticketTypes = [];
  
  // If the API provides ticket_types array, use that
  if (apiEvent.ticket_types && Array.isArray(apiEvent.ticket_types)) {
    console.log('Using ticket_types from API:', apiEvent.ticket_types);
    ticketTypes = apiEvent.ticket_types.map(tt => ({
      category: tt.name || "Standard",
      price: tt.price,
      available: tt.available
    }));
  } else {
    // Otherwise create standard ticket type from ticket_price/tickets_available
    console.log('Creating default ticket types from price/availability');
    const defaultTicketType = {
      category: "Standard",
      price: apiEvent.ticket_price || 0,
      available: apiEvent.tickets_available || 0
    };
    
    ticketTypes = [defaultTicketType];
    
    // Add premium ticket option if regular price exists
    if (apiEvent.ticket_price) {
      ticketTypes.push({
        category: "Premium",
        price: Math.round(apiEvent.ticket_price * 1.5), // 50% more expensive
        available: Math.round(apiEvent.tickets_available * 0.5) // Half the availability
      });
    }
  }

  // Determine if this is an IPL match by checking if category is "IPL"
  const isIplMatch = apiEvent.category === "IPL";
  
  // Initialize teams object
  let teams = undefined;
  
  // If API provides team_home and team_away, use those
  if (apiEvent.team_home && apiEvent.team_away) {
    console.log('Using team data from API');
    teams = {
      team1: {
        name: apiEvent.team_home.name,
        shortName: getTeamShortName(apiEvent.team_home.name),
        logo: apiEvent.team_home.code ? `/assets/teams/${apiEvent.team_home.code.toLowerCase()}.png` : undefined,
        color: apiEvent.team_home.primary_color || apiEvent.team_home.color
      },
      team2: {
        name: apiEvent.team_away.name,
        shortName: getTeamShortName(apiEvent.team_away.name),
        logo: apiEvent.team_away.code ? `/assets/teams/${apiEvent.team_away.code.toLowerCase()}.png` : undefined,
        color: apiEvent.team_away.primary_color || apiEvent.team_away.color
      }
    };
  } 
  // Otherwise, try to parse team information from title if this is an IPL match
  else if (isIplMatch && apiEvent.title && apiEvent.title.includes("vs")) {
    console.log('Parsing team info from title:', apiEvent.title);
    const teamNames = apiEvent.title.split("vs").map((t: string) => t.trim());
    
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
    id: apiEvent.id || `event-${Math.random().toString(36).substring(2, 9)}`,
    title: apiEvent.title || "",
    description: apiEvent.description || "",
    category: apiEvent.category || "Event",
    venue: apiEvent.venue || "TBD",
    date: apiEvent.date || "",
    time: apiEvent.time || "",
    duration: "2-3 hours", // Estimated duration (not provided in backend model)
    ticketTypes: ticketTypes,
    image: apiEvent.image_url || "/placeholder.svg",
    featured: apiEvent.is_featured || false,
    teams: teams
  };
  
  console.log('Mapped to UI event:', JSON.stringify(uiEvent, null, 2));
  return uiEvent;
};

// Convert frontend booking data to backend BookingCreate model
export const mapUIBookingToApiBooking = (
  eventId: string,
  quantity: number,
  customerInfo: CustomerInfo
) => {
  return {
    event_id: eventId,
    customer_info: customerInfo,
    selected_tickets: [{
      ticket_type_id: 'default', // This should be a proper ticket type ID
      quantity: quantity,
      price_per_ticket: 0 // This should be the actual price
    }] as SelectedTicket[]
  };
};

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