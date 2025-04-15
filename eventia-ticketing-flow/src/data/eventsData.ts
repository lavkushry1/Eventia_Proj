
export interface Event {
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
}

export const events: Event[] = [
  {
    id: "event-2025-01",
    title: "Cricket Legends Meet & Greet",
    description: "Meet your favorite cricket legends in person! Get autographs, take photos, and listen to their stories from the field.",
    category: "Meet & Greet",
    venue: "The Cricket Club, Mumbai",
    date: "2025-04-05",
    time: "14:00",
    duration: "4 hours",
    ticketTypes: [
      {
        category: "Standard Entry",
        price: 2000,
        available: 200
      },
      {
        category: "VIP Experience",
        price: 5000,
        available: 50
      }
    ],
    image: "/placeholder.svg",
    featured: true
  },
  {
    id: "event-2025-02",
    title: "IPL Fan Festival",
    description: "The ultimate celebration for IPL fans with music, food, games, merchandise, and surprise appearances by cricket stars.",
    category: "Festival",
    venue: "Marine Drive, Mumbai",
    date: "2025-04-10",
    time: "12:00",
    duration: "8 hours",
    ticketTypes: [
      {
        category: "Day Pass",
        price: 500,
        available: 2000
      },
      {
        category: "Premium Pass",
        price: 1200,
        available: 500
      }
    ],
    image: "/placeholder.svg",
    featured: true
  },
  {
    id: "event-2025-03",
    title: "Cricket Masterclass with Rahul Dravid",
    description: "Learn the techniques and mindset of cricket from one of the greatest batsmen of all time.",
    category: "Workshop",
    venue: "National Cricket Academy, Bangalore",
    date: "2025-04-15",
    time: "09:00",
    duration: "6 hours",
    ticketTypes: [
      {
        category: "Participant",
        price: 4000,
        available: 100
      },
      {
        category: "Observer",
        price: 1500,
        available: 200
      }
    ],
    image: "/placeholder.svg",
    featured: false
  },
  {
    id: "event-2025-04",
    title: "IPL Awards Night",
    description: "A glamorous evening celebrating the best performers and moments from the IPL 2025 season.",
    category: "Gala",
    venue: "Grand Hyatt, Mumbai",
    date: "2025-05-28",
    time: "20:00",
    duration: "4 hours",
    ticketTypes: [
      {
        category: "Standard Seat",
        price: 7500,
        available: 300
      },
      {
        category: "Premium Table",
        price: 15000,
        available: 20
      }
    ],
    image: "/placeholder.svg",
    featured: true
  },
  {
    id: "event-2025-05",
    title: "T20 Cricket Clinic for Kids",
    description: "A fun and educational cricket clinic for children aged 8-15, taught by professional coaches.",
    category: "Kids",
    venue: "DY Patil Sports Stadium, Navi Mumbai",
    date: "2025-04-25",
    time: "08:00",
    duration: "5 hours",
    ticketTypes: [
      {
        category: "Child Entry",
        price: 1500,
        available: 150
      }
    ],
    image: "/placeholder.svg",
    featured: false
  },
  {
    id: "event-2025-06",
    title: "Cricket Analytics Conference",
    description: "Explore how data and analytics are transforming cricket strategy, training, and player development.",
    category: "Conference",
    venue: "ITC Gardenia, Bangalore",
    date: "2025-05-10",
    time: "09:30",
    duration: "2 days",
    ticketTypes: [
      {
        category: "Professional Pass",
        price: 6000,
        available: 200
      },
      {
        category: "Student Pass",
        price: 2500,
        available: 100
      }
    ],
    image: "/placeholder.svg",
    featured: false
  }
];
