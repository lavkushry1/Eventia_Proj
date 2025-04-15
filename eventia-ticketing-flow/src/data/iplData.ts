
export interface IPLMatch {
  id: string;
  title: string;
  teams: {
    team1: {
      name: string;
      shortName: string;
      logo: string;
    };
    team2: {
      name: string;
      shortName: string;
      logo: string;
    };
  };
  venue: string;
  date: string;
  time: string;
  ticketTypes: {
    category: string;
    price: number;
    available: number;
  }[];
  image: string;
}

export const iplMatches: IPLMatch[] = [
  {
    id: "ipl-2025-01",
    title: "IPL 2025: Opening Match",
    teams: {
      team1: {
        name: "Mumbai Indians",
        shortName: "MI",
        logo: "/placeholder.svg"
      },
      team2: {
        name: "Chennai Super Kings",
        shortName: "CSK",
        logo: "/placeholder.svg"
      }
    },
    venue: "Wankhede Stadium, Mumbai",
    date: "2025-03-28",
    time: "19:30",
    ticketTypes: [
      {
        category: "General Stand",
        price: 1000,
        available: 1000
      },
      {
        category: "Premium Stand",
        price: 3000,
        available: 500
      },
      {
        category: "VIP Box",
        price: 8000,
        available: 100
      }
    ],
    image: "/placeholder.svg"
  },
  {
    id: "ipl-2025-02",
    title: "IPL 2025: Match 2",
    teams: {
      team1: {
        name: "Royal Challengers Bangalore",
        shortName: "RCB",
        logo: "/placeholder.svg"
      },
      team2: {
        name: "Delhi Capitals",
        shortName: "DC",
        logo: "/placeholder.svg"
      }
    },
    venue: "M. Chinnaswamy Stadium, Bangalore",
    date: "2025-03-29",
    time: "15:30",
    ticketTypes: [
      {
        category: "General Stand",
        price: 1200,
        available: 1200
      },
      {
        category: "Premium Stand",
        price: 3500,
        available: 600
      },
      {
        category: "VIP Box",
        price: 7500,
        available: 80
      }
    ],
    image: "/placeholder.svg"
  },
  {
    id: "ipl-2025-03",
    title: "IPL 2025: Match 3",
    teams: {
      team1: {
        name: "Kolkata Knight Riders",
        shortName: "KKR",
        logo: "/placeholder.svg"
      },
      team2: {
        name: "Rajasthan Royals",
        shortName: "RR",
        logo: "/placeholder.svg"
      }
    },
    venue: "Eden Gardens, Kolkata",
    date: "2025-03-30",
    time: "19:30",
    ticketTypes: [
      {
        category: "General Stand",
        price: 900,
        available: 1500
      },
      {
        category: "Premium Stand",
        price: 2800,
        available: 700
      },
      {
        category: "VIP Box",
        price: 6500,
        available: 120
      }
    ],
    image: "/placeholder.svg"
  },
  {
    id: "ipl-2025-04",
    title: "IPL 2025: Match 4",
    teams: {
      team1: {
        name: "Punjab Kings",
        shortName: "PBKS",
        logo: "/placeholder.svg"
      },
      team2: {
        name: "Sunrisers Hyderabad",
        shortName: "SRH",
        logo: "/placeholder.svg"
      }
    },
    venue: "Punjab Cricket Association Stadium, Mohali",
    date: "2025-03-31",
    time: "15:30",
    ticketTypes: [
      {
        category: "General Stand",
        price: 800,
        available: 1300
      },
      {
        category: "Premium Stand",
        price: 2500,
        available: 600
      },
      {
        category: "VIP Box",
        price: 6000,
        available: 90
      }
    ],
    image: "/placeholder.svg"
  }
];
